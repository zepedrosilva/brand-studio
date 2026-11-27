#!/usr/bin/env python3
"""brdtext: turn a brand name into outlined, kerned glyph paths from a font file (see SPEC.md).

Needs fontTools (optional). Uses uharfbuzz for shaping when installed. Never downloads a font.
Exit codes: 0 written, 2 usage or input error, 3 a needed optional dependency is missing.
"""
import argparse, importlib.util, json, math, os, re, sys, tempfile
from xml.sax.saxutils import escape

VERSION = "0.1.0"
HERE = os.path.dirname(os.path.abspath(__file__))


def thresholds_decimals():
    text = open(os.path.join(HERE, "..", "references", "thresholds.md"), encoding="utf-8").read()
    m = re.search(r"^max_decimals:\s*(\d+)", text, re.M)
    return int(m.group(1)) if m else 2


def die(code, msg):
    print("brdtext: " + msg, file=sys.stderr)
    sys.exit(code)


def clamp_axis(value, lo, hi):
    """Clamp value into [lo, hi]; returns (value, note or None)."""
    v = min(max(value, lo), hi)
    return v, (None if v == value else "--opsz %g is outside the font's optical-size range %g to %g; clamped to %g" % (value, lo, hi, v))


def pair_kern(tt, g1, g2):
    """Pair kerning in font units from GPOS pair adjustment or the kern table.
    shortcut: GPOS features are not filtered to 'kern'; first non-zero XAdvance wins."""
    if "GPOS" in tt:
        for lk in tt["GPOS"].table.LookupList.Lookup:
            for st in lk.SubTable:
                typ = lk.LookupType
                if typ == 9:
                    typ, st = st.ExtensionLookupType, st.ExtSubTable
                if typ != 2:
                    continue
                cov = st.Coverage.glyphs
                if g1 not in cov:
                    continue
                if st.Format == 1:
                    for r in st.PairSet[cov.index(g1)].PairValueRecord:
                        if r.SecondGlyph == g2:
                            v = getattr(r.Value1, "XAdvance", 0) if r.Value1 else 0
                            if v:
                                return v
                elif st.Format == 2:
                    c1 = st.ClassDef1.classDefs.get(g1, 0)
                    c2 = st.ClassDef2.classDefs.get(g2, 0)
                    v = st.Class1Record[c1].Class2Record[c2].Value1
                    v = getattr(v, "XAdvance", 0) if v else 0
                    if v:
                        return v
    if "kern" in tt:
        for t in tt["kern"].kernTables:
            v = t.kernTable.get((g1, g2), 0)
            if v:
                return v
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Outline a wordmark from a font file.")
    ap.add_argument("--font", required=True)
    ap.add_argument("--text", required=True)
    ap.add_argument("--size", type=float, default=96)
    ap.add_argument("--tracking", type=float, default=0, help="extra space between glyphs, in font units")
    ap.add_argument("--weight", type=float, help="weight for a variable font (wght axis); without it the default instance is used")
    ap.add_argument("--opsz", type=float, help="optical size for a variable font with an opsz axis; a value outside the axis range is clamped and reported")
    ap.add_argument("--root", help="chdir here first; brand/ is resolved against it")
    ap.add_argument("--out", default="brand/wordmark.svg")
    ap.add_argument("--no-harfbuzz", action="store_true", help="skip uharfbuzz even when installed (Latin-1 only)")
    a = ap.parse_args(argv)
    if a.root:
        if not os.path.isdir(a.root):
            die(2, "--root is not a directory: " + a.root)
        os.chdir(a.root)

    out_abs, base = os.path.realpath(a.out), os.path.realpath("brand")
    if not (out_abs == base or out_abs.startswith(base + os.sep)):
        die(2, "--out must be inside the brand folder (brand/)")
    if not os.path.isfile(a.font):
        die(2, "no such font file: " + a.font)
    if not a.text.strip():
        die(2, "--text is empty")
    if importlib.util.find_spec("fontTools") is None:
        die(3, "pip install fonttools uharfbuzz (fontTools is needed; uharfbuzz is optional, for kerning and non-Latin text)")
    from fontTools.ttLib import TTFont
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    from fontTools.pens.boundsPen import BoundsPen

    has_hb = importlib.util.find_spec("uharfbuzz") is not None and not a.no_harfbuzz
    if not has_hb and any(not (0x20 <= ord(c) <= 0xFF) for c in a.text):
        die(3, "install uharfbuzz for this script (text beyond Latin-1 needs shaping)")
    try:
        tt = TTFont(a.font, fontNumber=0)
    except Exception as e:
        die(2, "cannot read font: %s" % e)
    fpath = a.font
    loc, notes = {}, []
    axes = {x.axisTag: x for x in tt["fvar"].axes} if "fvar" in tt else {}
    if a.weight is not None:  # a variable font is read at its default weight unless asked
        if "wght" not in axes:
            die(2, "--weight needs a variable font with a wght axis")
        if not axes["wght"].minValue <= a.weight <= axes["wght"].maxValue:
            die(2, "--weight %g is outside the font's range %g to %g" % (a.weight, axes["wght"].minValue, axes["wght"].maxValue))
        loc["wght"] = a.weight
    if a.opsz is not None:
        if "opsz" in axes:
            loc["opsz"], note = clamp_axis(a.opsz, axes["opsz"].minValue, axes["opsz"].maxValue)
            notes.append(note or "--opsz set to %g" % loc["opsz"])
        else:
            notes.append("--opsz %g ignored: the font has no optical-size axis" % a.opsz)
    if loc:
        from fontTools.varLib.instancer import instantiateVariableFont
        tmpdir = tempfile.TemporaryDirectory()
        fpath = os.path.join(tmpdir.name, "instance.ttf")
        instantiateVariableFont(tt, loc).save(fpath)
        tt = TTFont(fpath)

    have = tt.getBestCmap()
    missing = sorted({ch for ch in a.text if not ch.isspace() and ord(ch) not in have})
    if missing:  # brd:TYP-07: with harfbuzz a missing character would silently become .notdef
        die(2, "brd:TYP-07: font has no glyph for %s" % ", ".join(repr(c) for c in missing))
    gs, upm = tt.getGlyphSet(), tt["head"].unitsPerEm
    s = a.size / upm
    glyphs = []  # (glyph name, x in font units, char)
    if has_hb:
        import uharfbuzz as hb
        blob = hb.Blob.from_file_path(fpath)
        font = hb.Font(hb.Face(blob))
        buf = hb.Buffer()
        buf.add_str(a.text)
        buf.guess_segment_properties()
        hb.shape(font, buf, {"kern": True, "liga": True})
        x = 0
        for i, (info, pos) in enumerate(zip(buf.glyph_infos, buf.glyph_positions)):
            name = tt.getGlyphName(info.codepoint)
            glyphs.append((name, x + pos.x_offset, a.text[min(info.cluster, len(a.text) - 1)]))
            x += pos.x_advance + a.tracking
        shaping = "uharfbuzz"
    else:
        cmap, hmtx, x, prev = tt.getBestCmap(), tt["hmtx"], 0, None
        for ch in a.text:
            name = cmap.get(ord(ch))
            if name is None:
                die(2, "font has no glyph for %r" % ch)
            if prev:
                x += pair_kern(tt, prev, name)
            glyphs.append((name, x, ch))
            x += hmtx[name][0] + a.tracking
            prev = name
        shaping = "none"

    dec = thresholds_decimals()
    ntos = lambda v: ("%.*f" % (dec, v)).rstrip("0").rstrip(".") or "0"
    paths, bp = [], BoundsPen(gs)
    for n, (name, gx, ch) in enumerate(glyphs):
        t = (s, 0, 0, -s, gx * s, 0)
        sp = SVGPathPen(gs, ntos=ntos)
        gs[name].draw(TransformPen(sp, t))
        gs[name].draw(TransformPen(bp, t))
        d = sp.getCommands()
        if d:  # spaces have no outline
            paths.append('    <path id="glyph-%d-%s" d="%s"/>' % (n, re.sub(r"\W", "_", ch), d))
    if not paths or bp.bounds is None:
        die(2, "no outlines produced")
    x0, y0, x1, y1 = bp.bounds
    x0, y0 = math.floor(x0 * 10**dec) / 10**dec, math.floor(y0 * 10**dec) / 10**dec
    x1, y1 = math.ceil(x1 * 10**dec) / 10**dec, math.ceil(y1 * 10**dec) / 10**dec

    name_of = lambda i: next((r.toUnicode() for r in tt["name"].names if r.nameID == i), "")
    rec = {"family": name_of(1), "version": name_of(5), "licence": name_of(13), "licence_url": name_of(14),
           "shaping": shaping, "tracking": a.tracking, "size": a.size, "weight": a.weight, "opsz": loc.get("opsz"), "text": a.text}
    comment = " ".join("%s=%s" % (k, str(v).replace("--", "-")) for k, v in rec.items() if k != "text")
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="%s %s %s %s">\n  <title>%s wordmark</title>\n  <!-- brdtext %s: %s -->\n'
           '  <g id="wordmark">\n%s\n  </g>\n</svg>\n') % (ntos(x0), ntos(y0), ntos(x1 - x0), ntos(y1 - y0),
                                                          escape(a.text), VERSION, escape(comment), "\n".join(paths))
    os.makedirs(os.path.dirname(out_abs), exist_ok=True)
    open(out_abs, "w", encoding="utf-8").write(svg)
    findings = [
        {"id": "brd:TYP-01", "status": "pass", "evidence": "script", "finding": "outlines written; font recorded"},
        {"id": "brd:TYP-02", "status": "review", "evidence": "script",
         "finding": "licence field says: %s %s (a hint, not proof; full text in the JSON record)" % (
             (rec["licence"][:80] + "..." if len(rec["licence"]) > 80 else rec["licence"]) or "none", rec["licence_url"])},
        {"id": "brd:TYP-03", "status": "review", "evidence": "script", "finding": "inspect pairs on the display render"},
        {"id": "brd:TYP-07", "status": "pass", "evidence": "script", "finding": "the font has a glyph for every character of the name"}]
    if shaping == "none":
        findings.append({"id": "brd:TYP-03", "status": "review", "evidence": "script",
                         "finding": "kerning from uharfbuzz was not applied (shaping none, only pair kerning read from the font); install uharfbuzz (pip install uharfbuzz) for full shaping"})
    findings += [{"id": "brd:TYP-03", "status": "review", "evidence": "script", "finding": n} for n in notes]
    json.dump({"script": "brdtext", "version": VERSION, "tools": {"fontTools": True, "uharfbuzz": has_hb},
               "font": rec, "output": a.out, "findings": findings}, open(os.path.splitext(out_abs)[0] + ".json", "w"), indent=2)
    print("brdtext %s: %d glyphs, shaping %s, font %s %s" % (VERSION, len(paths), shaping, rec["family"], rec["version"]))
    for f in findings:
        print("%s %s: %s" % (f["id"], f["status"], f["finding"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
