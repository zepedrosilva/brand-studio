#!/usr/bin/env python3
"""brdrender: render the PNGs the brd render rules need (see SPEC.md).

Wraps resvg or rsvg-convert for rasterising; PNG post-processing uses zlib and struct only.
Exit codes: 0 rendered, 1 pre-check failed (checked first, so a hostile file gives 1 even with no renderer), 2 usage or input error, 3 no renderer.
"""
import argparse, json, os, re, shutil, struct, subprocess, sys, tempfile, zlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import brdcheck  # noqa: E402  (same folder; -I removes the script dir from sys.path)

VERSION = "0.1.0"
# shortcut: 0.5 luminance cut is an assumption; move to thresholds.md if kept.
LUM_CUT = 0.5
MONO_PX = 256
DISPLAY_PX = 512
DARK_BG = "#1a1a1a"  # neutral dark ground for reversed or dark sources, so light ink is visible; exports stay transparent


class Fail(Exception):
    def __init__(self, code, msg):
        super().__init__(msg)
        self.code, self.msg = code, msg


def find_renderer(force):
    order = [force] if force else ["resvg", "rsvg-convert"]
    for name in order:
        path = shutil.which(name)
        if path:
            try:
                v = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=10).stdout.strip()
            except Exception:
                v = "unknown"
            return name, path, v
    raise Fail(3, "install resvg or rsvg-convert (no renderer found)")


def render(renderer, src, dst, width, bg=None):
    name, path, _ = renderer
    flag = ["--background", bg] if bg and name == "resvg" else ["-b", bg] if bg else []
    cmd = [path, "-w", str(width)] + flag + ([src, dst] if name == "resvg" else ["-o", dst, src])
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if r.returncode != 0 or not os.path.exists(dst):
        raise Fail(2, "renderer failed on %s: %s" % (src, r.stderr.strip()[:200]))


def read_png(path):
    data = open(path, "rb").read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise Fail(2, "not a PNG: " + path)
    pos, idat, hdr = 8, b"", None
    while pos < len(data):
        n, typ = struct.unpack(">I4s", data[pos:pos+8])
        body = data[pos+8:pos+8+n]
        pos += 12 + n
        if typ == b"IHDR":
            hdr = struct.unpack(">IIBBBBB", body)
        elif typ == b"IDAT":
            idat += body
    w, h, depth, ctype, _, _, interlace = hdr
    if depth != 8 or ctype != 6 or interlace != 0:
        raise Fail(2, "unsupported PNG (bit depth %d, colour type %d, interlace %d); need 8-bit RGBA, non-interlaced" % (depth, ctype, interlace))
    raw = zlib.decompress(idat)
    bpp, stride = 4, w * 4
    rows, prev = [], bytearray(stride)
    for y in range(h):
        f = raw[y*(stride+1)]
        line = bytearray(raw[y*(stride+1)+1:(y+1)*(stride+1)])
        for i in range(stride):
            a = line[i-bpp] if i >= bpp else 0
            b = prev[i]
            c = prev[i-bpp] if i >= bpp else 0
            if f == 1: line[i] = (line[i] + a) & 255
            elif f == 2: line[i] = (line[i] + b) & 255
            elif f == 3: line[i] = (line[i] + (a + b) // 2) & 255
            elif f == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[i] = (line[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        rows.append(line)
        prev = line
    return w, h, rows


def write_gray_png(path, w, h, rows):
    def chunk(t, b):
        return struct.pack(">I", len(b)) + t + b + struct.pack(">I", zlib.crc32(t + b) & 0xffffffff)
    raw = b"".join(b"\x00" + bytes(r) for r in rows)
    open(path, "wb").write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 0, 0, 0, 0)) +
                           chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


def lin(v):
    v /= 255
    return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4


def mono_rows(w, h, rows):
    """Composite on white, WCAG luminance, threshold. Returns black/white grey rows."""
    table = [lin(i) for i in range(256)]
    out = []
    for r in rows:
        line = bytearray(w)
        for x in range(w):
            R, G, B, A = r[4*x:4*x+4]
            a = A / 255
            cr, cg, cb = (R*a + 255*(1-a)), (G*a + 255*(1-a)), (B*a + 255*(1-a))
            L = 0.2126*table[int(round(cr))] + 0.7152*table[int(round(cg))] + 0.0722*table[int(round(cb))]
            line[x] = 255 if L >= LUM_CUT else 0
        out.append(line)
    return out


def variant_svg(raw, kind):
    m = re.search(r"<svg\b[^>]*>", raw)
    vb = re.search(r'viewBox\s*=\s*["\']([^"\']+)["\']', m.group(0))
    x, y, w, h = [float(n) for n in vb.group(1).replace(",", " ").split()]
    cx, cy = x + w/2, y + h/2
    # shortcut: rot90 assumes a roughly square viewBox; non-square marks clip.
    t = {"mirror": "translate(%g 0) scale(-1 1)" % (2*x + w),
         "rot90": "rotate(90 %g %g)" % (cx, cy), "rot180": "rotate(180 %g %g)" % (cx, cy)}[kind]
    end = raw.rfind("</svg>")
    return raw[:m.end()] + '<g transform="%s">' % t + raw[m.end():end] + "</g>" + raw[end:]


def export(renderer, svg, stem, sizes, out_abs, out_rel):
    svg_dir, png_dir = os.path.join(out_abs, "svg"), os.path.join(out_abs, "png")
    os.makedirs(svg_dir, exist_ok=True)
    os.makedirs(png_dir, exist_ok=True)
    shutil.copyfile(svg, os.path.join(svg_dir, stem + ".svg"))
    pngs = {}
    for s in sizes:
        dst = os.path.join(png_dir, "%s-%d.png" % (stem, s))
        render(renderer, svg, dst, s)
        pngs[str(s)] = "png/%s-%d.png" % (stem, s)
    with tempfile.TemporaryDirectory() as tmp:
        probe = os.path.join(tmp, "probe.png")
        render(renderer, svg, probe, 64)
        ratio = brdcheck.opaque_ratio(probe)
    # a background covers nearly every pixel; ink on a tight viewBox does not (same test as brdcheck --exports)
    transparent = ratio < brdcheck.load_thresholds()["export_background_coverage"]
    tile = brdcheck.is_tile(stem)
    mpath = os.path.join(out_abs, "manifest.json")
    try:
        man = json.load(open(mpath))
    except (OSError, ValueError):
        man = {"script": "brdrender", "version": VERSION, "files": {}}
    man["version"], man["sizes"] = VERSION, sizes
    man["files"][stem] = {"svg": "svg/%s.svg" % stem, "png": pngs, "transparent": transparent, "tile": tile}
    json.dump(man, open(mpath, "w"), indent=2)
    print("brdrender %s: %s %s, exported %s as SVG and %d PNGs in %s (transparent: %s)" %
          (VERSION, renderer[0], renderer[2], stem, len(sizes), out_rel, "yes" if transparent else "no"))
    if not transparent and not tile:
        print("fail brd:CTR-06 %s: the export has a background; make it transparent, or name it *-tile if the background is intended [evidence: render]" % svg)
        return 1
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Render PNGs for the brd render rules.")
    ap.add_argument("svg")
    ap.add_argument("--sizes", default=None, help="comma-separated; default test_sizes_px from thresholds.md")
    ap.add_argument("--out", default=None, help="default brand/renders, or brand/exports with --export")
    ap.add_argument("--export", action="store_true", help="write the downloadable set: SVG copy and transparent PNGs at export_sizes_px, plus a manifest (brd:CTR-06)")
    ap.add_argument("--renderer", choices=["resvg", "rsvg-convert"])
    ap.add_argument("--root", help="chdir here first; brand/ is resolved against it")
    a = ap.parse_args(argv)
    try:
        if a.root:
            if not os.path.isdir(a.root):
                raise Fail(2, "--root is not a directory: " + a.root)
            os.chdir(a.root)
        if not os.path.isfile(a.svg):
            raise Fail(2, "no such file: " + a.svg)
        a.out = a.out or ("brand/exports" if a.export else "brand/renders")
        out_abs, base = os.path.realpath(a.out), os.path.realpath("brand")
        if not (out_abs == base or out_abs.startswith(base + os.sep)):
            raise Fail(2, "--out must be inside the brand folder (brand/)")
        try:
            default = "export_sizes_px" if a.export else "test_sizes_px"
            sizes = [int(s) for s in a.sizes.split(",")] if a.sizes else list(brdcheck.load_thresholds()[default])
        except ValueError:
            raise Fail(2, "--sizes must be comma-separated integers")
        if a.export:
            lack = [x for x in brdcheck.load_thresholds()["export_sizes_px"] if x not in sizes]
            if lack:
                raise Fail(2, "--sizes for --export must include every export_sizes_px value (missing %s); the check reads the full set" % ", ".join(str(x) for x in lack))
        pre = []
        th = brdcheck.load_thresholds()
        brdcheck.check_svg(a.svg, th, {"palette": [], "grid": None, "waivers": []}, None, pre)
        block = [f for f in pre if f["status"] == "fail" and f["id"] in ("brd:SEC-01", "brd:CTR-04", "brd:CTR-01")]
        if block:
            for f in block:
                print("%s %s: %s" % (f["id"], f["file"], f["finding"]))
            print("brdrender: pre-check failed; nothing rendered")
            return 1
        renderer = find_renderer(a.renderer)  # after the pre-check: a hostile file is refused even with no renderer
        os.makedirs(out_abs, exist_ok=True)
        stem = os.path.splitext(os.path.basename(a.svg))[0]
        if a.export:
            return export(renderer, a.svg, stem, sizes, out_abs, a.out)
        raw = open(a.svg, encoding="utf-8").read()
        bg = DARK_BG if brdcheck.is_dark(stem) else None
        shown = lambda name: os.path.join(a.out, name)  # as given, not the resolved symlink target
        written, tmpdir = [], tempfile.TemporaryDirectory()
        tmp = tmpdir.name
        for s in sizes:
            dst = os.path.join(out_abs, "%s-%d.png" % (stem, s))
            render(renderer, a.svg, dst, s, bg)
            written.append((shown("%s-%d.png" % (stem, s)), "brd:CRF-02 brd:CAP-02 brd:EVD-01"))
        probe = os.path.join(tmp, "probe.png")
        render(renderer, a.svg, probe, MONO_PX)
        w, h, rows = read_png(probe)
        g = mono_rows(w, h, rows)
        mono = os.path.join(out_abs, stem + "-mono.png")
        write_gray_png(mono, w, h, g)
        written.append((shown(stem + "-mono.png"), "brd:CRF-01"))
        inv = os.path.join(out_abs, stem + "-mono-inverted.png")  # not -reversed: that name belongs to a real X-reversed.svg
        write_gray_png(inv, w, h, [bytearray(255 - v for v in r) for r in g])
        written.append((shown(stem + "-mono-inverted.png"), "brd:CRF-01"))
        for kind in ("mirror", "rot90", "rot180"):
            vsrc = os.path.join(tmp, kind + ".svg")
            open(vsrc, "w", encoding="utf-8").write(variant_svg(raw, kind))
            dst = os.path.join(out_abs, "%s-%s.png" % (stem, kind))
            render(renderer, vsrc, dst, MONO_PX)
            written.append((shown("%s-%s.png" % (stem, kind)), "brd:CRF-05"))
        disp = os.path.join(out_abs, stem + "-display.png")
        render(renderer, a.svg, disp, DISPLAY_PX, bg)
        written.append((shown(stem + "-display.png"), "brd:TYP-03 brd:CRF-06"))
        findings = [{"id": r, "status": "review", "file": p, "evidence": "render",
                     "finding": "render written; a reviewer must look at it"} for p, r in written]
        json.dump({"script": "brdrender", "version": VERSION, "tools": {renderer[0]: renderer[2]}, "files": [a.svg],
                   "luminance_cut": LUM_CUT, "findings": findings, "summary": {"fail_must": 0, "fail_should": 0, "review": len(findings), "waived": 0}}, open(os.path.join(out_abs, stem + "-render.json"), "w"), indent=2)
        print("brdrender %s: %s %s, %d images in %s" % (VERSION, renderer[0], renderer[2], len(written), a.out))
        for p, r in written:
            print("review %s %s: render written; look at it [evidence: render]" % (r, p))
        tmpdir.cleanup()
        return 0
    except Fail as e:
        print("brdrender: %s" % e.msg, file=sys.stderr)
        return e.code
    except Exception as e:  # never a stack trace
        print("brdrender: unexpected %s: %s" % (type(e).__name__, e), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
