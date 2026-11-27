#!/usr/bin/env python3
"""brdcheck: deterministic checks of SVG logo files (see SPEC.md). Standard library only.

Never executes SVG content, never fetches anything, never parses a file with DOCTYPE or ENTITY (SEC-01 fail).
Directory arguments are searched recursively. Exit codes: 0 no unwaived MUST failure, 1 MUST failure (including a DOCTYPE or ENTITY file, SEC-01), 2 usage or input error.
"""
import argparse, json, math, os, re, struct, sys, datetime, zipfile, zlib
import xml.etree.ElementTree as ET

VERSION = "0.1.0"
HERE = os.path.dirname(os.path.abspath(__file__))
THRESHOLDS = os.path.join(HERE, "..", "references", "thresholds.md")
SVG_NS = "http://www.w3.org/2000/svg"
SEV = {"TYP-01": "MUST", "CTR-01": "MUST", "CTR-02": "MUST", "CTR-03": "SHOULD", "CTR-04": "MUST", "CTR-05": "SHOULD", "CTR-06": "MUST",
       "CAP-01": "SHOULD", "CAP-03": "SHOULD", "CRF-03": "SHOULD", "CRF-04": "SHOULD",
       "SET-01": "MUST", "SET-02": "SHOULD", "SET-03": "SHOULD", "SEC-01": "MUST", "EVD-02": "SHOULD", "PAL-08": "SHOULD", "POS-05": "SHOULD", "TYP-05": "SHOULD", "TYP-06": "SHOULD"}
FIX = {"TYP-01": "outline the lettering from an OFL font and record the font", "CTR-01": "repair; regenerate if truncated", "CTR-02": "remove the feature", "CTR-03": "add title and meaningful ids",
       "CTR-04": "outline text; remove raster, filter or external reference", "CTR-05": "ship a flat mark.svg beside it",
       "CAP-01": "reduce or justify", "CAP-03": "simplify or round coordinates", "CRF-03": "snap angles and coordinates",
       "CRF-04": "re-centre and balance padding", "SET-01": "normalise the set", "SET-02": "add or complete style-spec.json",
       "SET-03": "use currentColor", "SEC-01": "strip it", "EVD-02": "adjust the palette", "CTR-06": "run brdrender.py --export for every master, variant and lockup, then bundle the folder", "TYP-05": "drop or replace a family, or state the third family's role", "TYP-06": "use a larger size or a heavier weight", "POS-05": "draft or trim the ## Story section and set story-status", "PAL-08": "recolour the file to the role values of its own column (light, or dark for reversed files) and keep the brand or text value as the ink, or add the colour to the roles table"}
CHECKED = ["CTR-01", "CTR-02", "CTR-03", "CTR-04", "CTR-05", "CAP-01", "CAP-03", "CRF-03", "CRF-04", "TYP-01", "SEC-01"]  # run on every file; only findings are printed
# CTR-02 lists SVG 2-only and animation elements; script belongs to SEC-01 alone.
BAN_FEATURES = {"animate", "animatemotion", "animatetransform", "animatecolor", "set", "mesh", "meshgradient",
                "meshrow", "meshpatch", "hatch", "hatchpath", "solidcolor", "discard"}
BAN_CONTENT = {"image", "filter"}
LIVE_TEXT = {"text", "tspan", "textpath"}
NAMED = {"black": "#000000", "white": "#ffffff", "red": "#ff0000", "green": "#008000", "blue": "#0000ff",
         "yellow": "#ffff00", "gray": "#808080", "grey": "#808080", "orange": "#ffa500", "purple": "#800080"}
GEN_ID = re.compile(r"^(g|path|rect|circle|ellipse|line|polygon|polyline|layer_?|group)\d+$", re.I)
NUM = re.compile(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")


class InputError(Exception):
    pass


def load_thresholds():
    text = open(THRESHOLDS, encoding="utf-8").read()
    block = re.search(r"```yaml\n(.*?)```", text, re.S)
    if not block:
        raise InputError("no yaml block in thresholds.md")
    out = {}
    for line in block.group(1).splitlines():
        m = re.match(r"(\w+):\s*([^#]+?)\s*(#.*)?$", line)
        if m:
            v = m.group(2)
            out[m.group(1)] = json.loads(v) if v.startswith("[") else float(v) if "." in v else int(v)
    return out


def css_unescape(t):
    """Decode CSS escapes (u\\72l is url) so a scan for url( and @import cannot be dodged."""
    t = re.sub(r"\\([0-9a-fA-F]{1,6})\s?", lambda m: chr(min(int(m.group(1), 16), 0x10FFFF)) if int(m.group(1), 16) else "", t)
    return re.sub(r"\\(.)", r"\1", t)


def local(tag):
    return tag.rsplit("}", 1)[-1].lower()


def norm_colour(v):
    v = v.strip().lower()
    if v in ("", "none", "currentcolor", "inherit", "transparent") or v.startswith("url("):
        return None
    if v in NAMED:
        return NAMED[v]
    m = re.fullmatch(r"#([0-9a-f]{3})", v)
    if m:
        return "#" + "".join(c * 2 for c in m.group(1))
    m = re.fullmatch(r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", v)
    if m:
        return "#%02x%02x%02x" % tuple(min(255, int(x)) for x in m.groups())
    return v


def style_of(el):
    out = {}
    for p in el.get("style", "").split(";"):
        if ":" in p:
            k, v = p.split(":", 1)
            out[k.strip().lower()] = re.sub(r"\s*!important\s*$", "", v.strip(), flags=re.I)
    return out


def colours_of(el):
    out = []
    st = style_of(el)
    for prop in ("fill", "stroke", "stop-color", "flood-color", "color"):
        v = st.get(prop, el.get(prop))
        c = norm_colour(v) if v else None
        if c:
            out.append(c.strip())
    return out


# ---- geometry -------------------------------------------------------------
def mat_mul(a, b):
    return (a[0]*b[0]+a[2]*b[1], a[1]*b[0]+a[3]*b[1], a[0]*b[2]+a[2]*b[3], a[1]*b[2]+a[3]*b[3],
            a[0]*b[4]+a[2]*b[5]+a[4], a[1]*b[4]+a[3]*b[5]+a[5])


def parse_transform(s):
    m = (1, 0, 0, 1, 0, 0)
    for name, args in re.findall(r"(\w+)\s*\(([^)]*)\)", s or ""):
        a = [float(x) for x in NUM.findall(args)]
        if name == "translate":
            t = (1, 0, 0, 1, a[0], a[1] if len(a) > 1 else 0)
        elif name == "scale":
            t = (a[0], 0, 0, a[1] if len(a) > 1 else a[0], 0, 0)
        elif name == "rotate":
            r = math.radians(a[0]); c, s_ = math.cos(r), math.sin(r)
            t = (c, s_, -s_, c, 0, 0)
            if len(a) == 3:
                t = mat_mul(mat_mul((1, 0, 0, 1, a[1], a[2]), t), (1, 0, 0, 1, -a[1], -a[2]))
        elif name == "matrix" and len(a) == 6:
            t = tuple(a)
        else:
            continue
        m = mat_mul(m, t)
    return m


def apply(m, p):
    return (m[0]*p[0]+m[2]*p[1]+m[4], m[1]*p[0]+m[3]*p[1]+m[5])


def arc_points(p0, rx, ry, phi_deg, fa, fs, p1):
    """End point plus the x and y extrema of an SVG elliptical arc (endpoint to centre conversion, SVG 1.1 F.6.5)."""
    rx, ry = abs(rx), abs(ry)
    if rx == 0 or ry == 0 or p0 == p1:
        return [p1]
    phi = math.radians(phi_deg); c, s = math.cos(phi), math.sin(phi)
    dx, dy = (p0[0]-p1[0])/2, (p0[1]-p1[1])/2
    x1p, y1p = c*dx + s*dy, -s*dx + c*dy
    lam = x1p**2/rx**2 + y1p**2/ry**2
    if lam > 1:
        rx, ry = rx*math.sqrt(lam), ry*math.sqrt(lam)
    den = rx**2*y1p**2 + ry**2*x1p**2
    co = math.sqrt(max(0.0, (rx**2*ry**2 - rx**2*y1p**2 - ry**2*x1p**2)/den)) * (-1 if fa == fs else 1)
    cxp, cyp = co*rx*y1p/ry, -co*ry*x1p/rx
    cx, cy = c*cxp - s*cyp + (p0[0]+p1[0])/2, s*cxp + c*cyp + (p0[1]+p1[1])/2
    ang = lambda ux, uy, vx, vy: math.atan2(ux*vy - uy*vx, ux*vx + uy*vy)
    ux, uy = (x1p-cxp)/rx, (y1p-cyp)/ry
    th1, dth = ang(1, 0, ux, uy), ang(ux, uy, (-x1p-cxp)/rx, (-y1p-cyp)/ry)
    if not fs and dth > 0:
        dth -= 2*math.pi
    if fs and dth < 0:
        dth += 2*math.pi
    out = [p1]
    for t0 in (math.atan2(-ry*s, rx*c), math.atan2(ry*c, rx*s)):
        for t in (t0, t0 + math.pi):
            if ((t - th1) * (1 if dth >= 0 else -1)) % (2*math.pi) <= abs(dth):
                out.append((cx + rx*math.cos(t)*c - ry*math.sin(t)*s, cy + rx*math.cos(t)*s + ry*math.sin(t)*c))
    return out


def path_geometry(d):
    """Return (points, straight_segments, anchors). Arcs and curves: control and end points only (bounds approximate)."""
    toks = re.findall(r"[MmLlHhVvCcSsQqTtAaZz]|" + NUM.pattern, d)
    pts, segs, anchors = [], [], 0
    i, cur, start, cmd = 0, (0.0, 0.0), (0.0, 0.0), None
    argc = {"M": 2, "L": 2, "H": 1, "V": 1, "C": 6, "S": 4, "Q": 4, "T": 2, "A": 7, "Z": 0}

    def nums(n):
        nonlocal i
        v = [float(x) for x in toks[i:i+n]]
        i += n
        return v
    while i < len(toks):
        if re.fullmatch(r"[A-Za-z]", toks[i]):
            cmd = toks[i]; i += 1
            if cmd in "Zz":
                if cur != start:
                    segs.append((cur, start))
                cur = start; anchors += 1
                continue
        if cmd is None or i + argc[cmd.upper()] > len(toks):
            break
        rel, c = cmd.islower(), cmd.upper()
        v = nums(argc[c])
        ox, oy = cur if rel else (0, 0)
        if c in "ML":
            n = (v[0]+ox, v[1]+oy)
            if c == "L":
                segs.append((cur, n))
            else:
                start = n; cmd = "l" if rel else "L"
            cur = n; pts.append(n)
        elif c == "H":
            n = (v[0]+ox, cur[1]); segs.append((cur, n)); cur = n; pts.append(n)
        elif c == "V":
            n = (cur[0], v[0]+oy); segs.append((cur, n)); cur = n; pts.append(n)
        elif c == "A":
            end = (v[5]+ox, v[6]+oy)
            pts.extend(arc_points(cur, v[0], v[1], v[2], int(v[3]), int(v[4]), end))
            cur = end
        else:
            for k in range(0, len(v), 2):
                pts.append((v[k]+ox, v[k+1]+oy))
            cur = pts[-1]
        anchors += 1
    return pts, segs, anchors


def element_points(el, tag, vb=None):
    def f(k, d=0.0):
        raw = el.get(k, str(d))
        n = NUM.findall(raw)
        if not n:
            return d
        v = float(n[0])
        if raw.strip().endswith("%"):  # a percentage is of the viewBox; without one it is unknown, so 0
            if not vb:
                return 0.0
            base = vb[2] if k in ("x", "width", "cx", "rx", "x1", "x2") else vb[3] if k in ("y", "height", "cy", "ry", "y1", "y2") else (vb[2] + vb[3]) / 2
            return v * base / 100
        return v
    if tag == "rect":
        x, y, w, h = f("x"), f("y"), f("width"), f("height")
        return [(x, y), (x+w, y), (x+w, y+h), (x, y+h)], []
    if tag in ("circle", "ellipse"):
        cx, cy = f("cx"), f("cy")
        rx = f("r") if tag == "circle" else f("rx")
        ry = f("r") if tag == "circle" else f("ry")
        return [(cx-rx, cy-ry), (cx+rx, cy-ry), (cx+rx, cy+ry), (cx-rx, cy+ry)], []
    if tag == "line":
        a, b = (f("x1"), f("y1")), (f("x2"), f("y2"))
        return [a, b], [(a, b)]
    if tag in ("polyline", "polygon"):
        n = [float(x) for x in NUM.findall(el.get("points", ""))]
        p = list(zip(n[0::2], n[1::2]))
        s = list(zip(p, p[1:])) + ([(p[-1], p[0])] if tag == "polygon" and len(p) > 2 else [])
        return p, s
    if tag == "path":
        p, s, _ = path_geometry(el.get("d", ""))
        return p, s
    return [], []


def stroke_half(el, inh):
    """Half the stroke width an element paints with (own or inherited), 0 when it has no stroke."""
    st = style_of(el)
    stroke = st.get("stroke", el.get("stroke", inh.get("stroke")))
    width = st.get("stroke-width", el.get("stroke-width", inh.get("stroke-width", "1")))
    if not stroke or stroke.strip().lower() == "none":
        return 0.0
    n = NUM.findall(width)
    return float(n[0]) / 2 if n else 0.0


def collect(root, vb=None, lettering_ok=False):
    """Walk the tree applying transforms.

    Returns bounds points (stroke width included), segments, per-path anchors, grid points and ink points.
    Outlined lettering (a group or path whose id starts with 'wordmark' or 'glyph', only when lettering_ok,
    i.e. in a file named wordmark* or lockup*) is font geometry: it
    counts for bounds but not for the segment, anchor or grid checks. Inside a scaled group the grid check is skipped
    too (the mark keeps the grid of its own coordinates). A rect that fills the whole viewBox
    is a background: it counts for bounds but not for the centring and padding numbers (ink points).
    """
    pts, segs, anchors, gpts, ipts = [], [], [], [], []

    def walk(el, m, inh, lettering):
        tag = local(el.tag)
        m = mat_mul(m, parse_transform(el.get("transform")))
        if tag in ("defs", "symbol", "clippath", "mask", "pattern", "marker"):
            return
        ident = el.get("id") or ""
        lettering = lettering or (lettering_ok and ident.startswith(("wordmark", "glyph")))
        p, s = element_points(el, tag, vb)
        hw = stroke_half(el, inh) * math.sqrt(abs(m[0]*m[3] - m[1]*m[2]))
        q = [apply(m, x) for x in p]
        grown = [(x + dx, y + dy) for x, y in q for dx, dy in ((-hw, -hw), (hw, hw))] if hw else q
        pts.extend(grown)
        ground = (tag == "rect" and vb and q and
                  min(a[0] for a in q) <= vb[0] and min(a[1] for a in q) <= vb[1] and
                  max(a[0] for a in q) >= vb[0] + vb[2] and max(a[1] for a in q) >= vb[1] + vb[3])
        if not ground:
            ipts.extend(grown)
        scaled = abs(math.hypot(m[0], m[1]) - 1) > 1e-6 or abs(math.hypot(m[2], m[3]) - 1) > 1e-6  # a scaled group keeps its own grid
        if not lettering:
            if not scaled:
                gpts.extend(q)
            segs.extend((apply(m, a), apply(m, b)) for a, b in s)
            if tag == "path":
                anchors.append((ident or "path", path_geometry(el.get("d", ""))[2]))
        inh = dict(inh)
        for k in ("stroke", "stroke-width"):
            v = style_of(el).get(k, el.get(k))
            if v is not None:
                inh[k] = v
        for ch in el:
            walk(ch, m, inh, lettering)
    walk(root, (1, 0, 0, 1, 0, 0), {}, False)
    return pts, segs, anchors, gpts, ipts


# ---- brief and waivers ----------------------------------------------------
def read_brief(path):
    if not path:
        return {"palette": [], "grid": None, "waivers": [], "wordmark_font": "", "roles": [], "keys": {}, "rationale": [], "has_rationale": False, "story": [], "story_status": ""}
    try:
        text = open(path, encoding="utf-8").read()
    except OSError as e:
        raise InputError("cannot read brief: %s" % e)
    pal = []
    m = re.search(r"^palette:\s*(.+)$", text, re.M)
    if m:
        for entry in m.group(1).split(";"):
            mm = re.search(r"(#[0-9a-fA-F]{3,6})\s+(background|text|ui|mark)", entry)
            if mm:
                pal.append((norm_colour(mm.group(1)), mm.group(2)))
    g = re.search(r"^grid-unit:\s*([0-9.]+)", text, re.M)
    wf = re.search(r"^wordmark-font:[ \t]*(.*)$", text, re.M)
    waivers = [(m.group(1), m.group(2).strip(), m.group(3)) for m in
               re.finditer(r"Waives brd:([A-Z]+-\d+) for ([^:]+):.*?Review by:\s*(\d{4}-\d{2}-\d{2})", text)]
    roles = []
    sec = re.search(r"^#{1,6}[ \t]+Palette roles[ \t]*:?[ \t]*$(.*?)(?=^#{1,6}[ \t]|\Z)", text, re.M | re.S | re.I)
    if sec:
        for row in sec.group(1).splitlines():
            cells = [c.strip() for c in row.strip().strip("|").split("|")]
            if len(cells) >= 3 and cells[0].lower() not in ("role", "") and not set(cells[0]) <= set("-: "):
                lt, dk = (re.fullmatch(r"#[0-9a-fA-F]{6}", c) and norm_colour(c) for c in cells[1:3])
                rm = re.fullmatch(r"(\S+)\s+(\d+)\s*/\s*(\d+)", cells[3]) if len(cells) > 3 else None
                roles.append({"role": cells[0].lower(), "light": lt or None, "dark": dk or None,
                              "ramp": rm.group(1) if rm else None, "lstep": int(rm.group(2)) if rm else None,
                              "dstep": int(rm.group(3)) if rm else None})
    keys = {k: (re.search(r"^%s:[ \t]*(.*)$" % k, text, re.M) or [None, ""])[1].strip()
            for k in ("positioning", "own-word", "assets", "category-colours", "tone", "story-status", "pair-cue")}
    rsec = re.search(r"^#{1,6}[ \t]+Rationale[ \t]*:?[ \t]*$(.*?)(?=^#{1,6}[ \t]|\Z)", text, re.M | re.S | re.I)
    rationale = [l.strip("-* \t") for l in rsec.group(1).splitlines() if l.strip("-* \t")] if rsec else []
    ssec = re.search(r"^#{1,6}[ \t]+Story[ \t]*:?[ \t]*$(.*?)(?=^#{1,6}[ \t]|\Z)", text, re.M | re.S | re.I)
    story = []
    if ssec:
        body = re.sub(r"<!--.*?-->", "", ssec.group(1), flags=re.S)
        story = [" ".join(p.split()) for p in re.split(r"\n\s*\n", body) if p.strip() and not re.fullmatch(r"<[^<>]*>", p.strip())]
    return {"palette": pal, "grid": float(g.group(1)) if g else None, "waivers": waivers, "story": story, "story_status": keys["story-status"].lower(),
            "wordmark_font": (wf.group(1).strip() if wf else ""), "roles": roles, "keys": keys,
            "rationale": rationale, "has_rationale": bool(rsec)}


def waived(rule, file, waivers, today):
    for r, f, date in waivers:
        if r == rule and (file == f or os.path.basename(file) == f or file.endswith("/" + f)) and date >= today:
            return True
    return False


# ---- contrast -------------------------------------------------------------
def lum(hexc):
    h = hexc.lstrip("#")
    if len(h) != 6:
        return None
    c = [int(h[i:i+2], 16)/255 for i in (0, 2, 4)]
    c = [x/12.92 if x <= 0.03928 else ((x+0.055)/1.055) ** 2.4 for x in c]
    return 0.2126*c[0] + 0.7152*c[1] + 0.0722*c[2]


def contrast(a, b):
    la, lb = lum(a), lum(b)
    if la is None or lb is None:
        return None
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


# ---- per-file checks ------------------------------------------------------
def check_svg(path, th, brief, grid, out):
    def add(rule, status, msg):
        out.append({"id": "brd:" + rule, "severity": SEV[rule], "status": status, "file": path,
                    "finding": msg, "fix": FIX[rule], "evidence": "script"})
    raw = open(path, encoding="utf-8", errors="replace").read()
    if re.search(r"<!DOCTYPE|<!ENTITY", raw, re.I):
        add("SEC-01", "fail", "DOCTYPE or ENTITY declaration; file not parsed (entity-expansion risk)")
        return
    if re.search(r"<\?(?!xml\s)", raw):
        add("SEC-01", "fail", "processing instruction (for example xml-stylesheet) that a viewer may act on; file not parsed")
        return
    head = re.sub(r"<\?xml\s.*?\?>|<!--.*?-->", "", raw[:raw.lower().find("<svg")] if "<svg" in raw.lower() else raw, flags=re.S)
    tail_i = raw.lower().rfind("</svg>")
    tail = re.sub(r"<!--.*?-->", "", raw[tail_i+6:], flags=re.S) if tail_i >= 0 else ""
    if head.strip() or tail.strip():
        add("CTR-01", "fail", "text outside the svg element (prose or code fence)")
    if re.search(r"\b(NaN|Infinity)\b", raw):
        add("CTR-01", "fail", "NaN or Infinity in the file")
    try:
        root = ET.fromstring(raw[raw.lower().find("<svg"):tail_i+6] if "<svg" in raw.lower() and tail_i >= 0 else raw)
    except ET.ParseError as e:
        add("CTR-01", "fail", "does not parse: %s" % e)
        return
    if root.tag != "{%s}svg" % SVG_NS:
        add("CTR-01", "fail", "root is not svg in the SVG namespace")
        return
    vb = [float(x) for x in NUM.findall(root.get("viewBox", ""))]
    if len(vb) != 4 or vb[2] <= 0 or vb[3] <= 0:
        add("CTR-01", "fail", "missing or invalid viewBox")
        vb = None

    lok = os.path.basename(path).lower().startswith(("wordmark", "lockup"))
    try:
        pts, segs, anchors, gpts, ipts = collect(root, vb, lok)
    except RecursionError:
        add("CTR-01", "fail", "elements are nested too deeply to check")
        return
    if vb and pts:
        x0, y0, x1, y1 = min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts)
        e = 1e-6
        if x0 < vb[0]-e or y0 < vb[1]-e or x1 > vb[0]+vb[2]+e or y1 > vb[1]+vb[3]+e:
            add("CTR-01", "fail", "content extends outside the viewBox (%.2f..%.2f, %.2f..%.2f)" % (x0, x1, y0, y1))
    if vb and ipts:
        x0, y0, x1, y1 = min(p[0] for p in ipts), min(p[1] for p in ipts), max(p[0] for p in ipts), max(p[1] for p in ipts)
        cx, cy = (x0+x1)/2 - (vb[0]+vb[2]/2), (y0+y1)/2 - (vb[1]+vb[3]/2)
        tol = th["centre_tolerance_pct"] / 100
        if abs(cx) > tol * vb[2] or abs(cy) > tol * vb[3]:  # silent inside the tolerance: a centred mark has nothing to report
            add("CRF-04", "review", "centre offset dx=%.2f dy=%.2f (tolerance %.1f%% of the viewBox); padding left=%.2f top=%.2f right=%.2f bottom=%.2f" %
                (cx, cy, th["centre_tolerance_pct"], x0-vb[0], y0-vb[1], vb[0]+vb[2]-x1, vb[1]+vb[3]-y1))

    els = list(root.iter())
    tags = [local(e.tag) for e in els]
    feats = sorted({t for t in tags if t in BAN_FEATURES})
    if feats:
        add("CTR-02", "fail", "unsupported elements: " + ", ".join(feats))
    if "title" not in tags:
        add("CTR-03", "fail", "no <title>")
    gen = sorted({e.get("id") for e in els if e.get("id") and GEN_ID.match(e.get("id"))})
    if gen:
        add("CTR-03", "review", "generated-looking ids: " + ", ".join(gen[:6]))
    bad = sorted({t for t in tags if t in BAN_CONTENT or t.startswith("fe")})
    ext = []
    for e in els:
        for k, v in e.attrib.items():
            if k.rsplit("}", 1)[-1] == "href" and not v.startswith("#"):
                ext.append(v[:30])
            if re.search(r"url\(\s*(?!['\"]?#)", v):
                ext.append(v[:30])
    for e in els:
        if local(e.tag) == "style" and e.text and re.search(r"@import|url\(\s*(?![\s'\"]*#)", css_unescape(e.text)):
            ext.append("<style> import or url()")
    live = sorted({t for t in tags if t in LIVE_TEXT})
    if live:
        msg = "live text (%s) in a master" % ", ".join(live)
        add("CTR-04", "fail", msg)
        add("TYP-01", "fail", msg)
    base = os.path.basename(path).lower()
    if base.startswith(("wordmark", "lockup")):
        grp = [e for e in els if (e.get("id") or "").startswith("wordmark")]
        if not any(local(x.tag) == "path" for g in grp for x in g.iter()):
            add("TYP-01", "fail", "no path in a group with id 'wordmark'; lettering is not outlines")
    if bad or ext:
        add("CTR-04", "fail", "; ".join(filter(None, ["forbidden in a master: " + ", ".join(bad) if bad else "",
                                                    "external reference: " + ", ".join(sorted(set(ext))[:3]) if ext else ""])))
    if "lineargradient" in tags or "radialgradient" in tags:
        flat = os.path.join(os.path.dirname(path), "mark.svg")
        if os.path.basename(path) == "mark.svg" or not os.path.exists(flat) or re.search(r"[lr][a-z]*Gradient", open(flat, errors="replace").read()):
            add("CTR-05", "fail", "gradient without a gradient-free mark.svg beside it")

    css = [norm_colour(m.group(2)) for e in els if local(e.tag) == "style" and e.text
           for m in re.finditer(r"(?<![\w-])(fill|stroke|stop-color|flood-color|color)\s*:\s*([^;}!]+)", css_unescape(e.text), re.I)]
    matte = {id(x) for e in els if local(e.tag) in ("mask", "clippath") for x in e.iter()}  # a matte is luminance, not painted colour
    cols = sorted({c for e in els if id(e) not in matte for c in colours_of(e)} | {c for c in css if c})
    if len(cols) > th["max_master_colours"]:
        add("CAP-01", "fail", "%d flat colours (%s), budget %d" % (len(cols), ", ".join(cols), th["max_master_colours"]))
    roles = brief.get("roles") or []
    if roles and not re.search(r"(^|[-_.])(mono|gradient)([-_.]|$)", base):  # PAL-08: every colour in a file is a declared role value
        dark = is_dark(base)  # variant name picks the column: reversed or dark files sit on dark surfaces
        col, other = ("dark", "light") if dark else ("light", "dark")
        mine = {r[col] for r in roles if r.get(col)} | (set() if dark else {c for c, _ in brief["palette"]})
        theirs = {r[other] for r in roles if r.get(other)} - mine
        wrong = [c for c in cols if c in theirs]
        stray = [c for c in cols if c not in mine and c not in theirs and c not in {c2 for c2, _ in brief["palette"]}]
        if stray:
            add("PAL-08", "fail", "colour%s %s not in the brief's palette roles (light or dark) or palette line" % ("s" if len(stray) > 1 else "", ", ".join(stray)))
        if wrong:
            add("PAL-08", "fail", "%s file uses %s-column value%s %s; use the %s values of the roles table" % (col, other, "s" if len(wrong) > 1 else "", ", ".join(wrong), col))
        ink = {r[col] for r in roles if r.get("role") in ("brand", "text") and r.get(col)}
        if ink and cols and not stray and not wrong and not (set(cols) & ink):
            add("PAL-08", "fail", "no %s-column brand or text value in the file (%s); the logo ink must be the brand role" % (col, ", ".join(sorted(ink))))

    maxd = th["max_decimals"]
    long_n = 0
    for e in els:
        for k in ("d", "points", "x", "y", "width", "height", "cx", "cy", "r", "rx", "ry", "x1", "y1", "x2", "y2", "viewBox", "transform"):
            for n in NUM.findall(e.get(k, "")):
                if "e" not in n.lower() and "." in n and len(n.split(".")[1]) > maxd:
                    long_n += 1
    if long_n:
        add("CAP-03", "fail", "%d numbers with more than %d decimals" % (long_n, maxd))
    many = [(i, n) for i, n in anchors if n > th["anchor_review"]]
    if many:
        add("CAP-03", "review", "paths with many anchors: " + ", ".join("%s=%d" % x for x in many[:4]))

    exact = set(th["exact_angles_deg"]) | {0, 90}
    near = 0
    for a, b in segs:
        dx, dy = b[0]-a[0], b[1]-a[1]
        if math.hypot(dx, dy) < 1e-9:
            continue
        ang = abs(math.degrees(math.atan2(dy, dx))) % 180
        for t in exact | {180 - x for x in exact} | {180}:
            if th["angle_tolerance_deg"] < abs(ang - t) <= th["near_angle_window_deg"]:  # rounded endpoints sit a hair off an exact angle
                near += 1
                break
    off = 0
    if grid:
        off = sum(1 for p in gpts for v in p if abs(v/grid - round(v/grid)) > 1e-6)
    if near or off:
        add("CRF-03", "review", "%d segments within the near-angle window of an exact angle but not on it; %d coordinates off the grid unit %s" %
            (near, off, grid))

    why = []
    for e in els:
        t = local(e.tag)
        names = [k.rsplit("}", 1)[-1].lower() for k in e.attrib]
        hrefs = [v for k, v in e.attrib.items() if k.rsplit("}", 1)[-1] == "href"]
        if t in ("script", "foreignobject"):
            why.append("<%s>" % t)
        if any(n.startswith("on") for n in names):
            why.append("event handler")
        if any("javascript:" in v.lower() for v in e.attrib.values()):
            why.append("javascript: URL")
        for v in hrefs:
            m = re.match(r"data:([^;,]*)", v.strip(), re.I)
            if m and m.group(1).lower() not in ("image/png", "image/jpeg", "image/gif", "image/webp"):
                why.append("executable data: URL")
    if why:
        add("SEC-01", "fail", ", ".join(sorted(set(why))))
    return {"colours": cols}


# ---- colour: Oklab, colour-blind simulation, role checks -------------------
# Machado, Oliveira and Fernandes 2009, severity 1.0 (Table 1 on the authors' page, read 2026-11-19); apply in linear RGB.
CVD = {"deuteranopia": ((0.367322, 0.860646, -0.227968), (0.280085, 0.672501, 0.047413), (-0.011820, 0.042940, 0.968881)),
       "protanopia": ((0.152286, 1.052583, -0.204868), (0.114503, 0.786281, 0.099216), (-0.003882, -0.048116, 1.051998)),
       "tritanopia": ((1.255528, -0.076749, -0.178779), (-0.078411, 0.930809, 0.147602), (0.004733, 0.691367, 0.303900))}
NEUTRAL_ROLES = ("neutral", "background", "text", "status")


def to_linear(hexc):
    h = hexc.lstrip("#")
    c = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    return [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]


def oklab_lin(c):
    """Linear sRGB to Oklab (Ottosson, 2020)."""
    r, g, b = c
    l = (0.4122214708*r + 0.5363325363*g + 0.0514459929*b) ** (1/3)
    m = (0.2119034982*r + 0.6806995451*g + 0.1073969566*b) ** (1/3)
    s = (0.0883024619*r + 0.2817188376*g + 0.6299787005*b) ** (1/3)
    return (0.2104542553*l + 0.7936177850*m - 0.0040720468*s,
            1.9779984951*l - 2.4285922050*m + 0.4505937099*s,
            0.0259040371*l + 0.7827717662*m - 0.8086757660*s)


def oklab(hexc):
    return oklab_lin(to_linear(hexc))


def cvd_oklab(hexc, kind):
    lin = to_linear(hexc)
    sim = [min(1.0, max(0.0, sum(row[j] * lin[j] for j in range(3)))) for row in CVD[kind]]
    return oklab_lin(sim)


def ok_dist(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def hue_chroma(hexc):
    _, a, b = oklab(hexc)
    return math.degrees(math.atan2(b, a)) % 360, math.hypot(a, b)


def hue_gap(h1, h2):
    d = abs(h1 - h2) % 360
    return min(d, 360 - d)


def valid_hex(c):
    return bool(c) and bool(re.fullmatch(r"#[0-9a-f]{6}", c))


def check_roles(path, th, brief, out):
    """PAL-01 to PAL-03, PAL-07 (break distance), EVD-02 widened, EVD-03, EVD-04 from the brief's '## Palette roles' table."""
    def add(rid, sev, status, msg, fix):
        out.append({"id": "brd:" + rid, "severity": sev, "status": status, "file": path,
                    "finding": msg, "fix": fix, "evidence": "script"})
    rows = brief["roles"]
    by = {}
    for r in rows:
        by.setdefault(r["role"], []).append(r)
    known = ("brand", "brand-2", "neutral", "background", "text", "status")
    ok = lambda r: valid_hex(r["light"]) and valid_hex(r["dark"])
    required = ("brand", "neutral", "background", "text")
    problems = [n for n in required if not any(ok(r) for r in by.get(n, []))]
    problems += ["%s row with an invalid hex (use #RRGGBB)" % r["role"] for r in rows if r["role"] in known and not ok(r) and r["role"] not in problems]
    problems += ["%s (no valid ramp entry)" % r["role"] for r in rows if r["role"] in known and ok(r) and not r["ramp"]]
    if problems:
        add("PAL-01", "SHOULD", "fail", "palette roles missing, without two valid #RRGGBB values, or without a ramp entry: %s" % ", ".join(problems),
            "add the rows; derive missing values from the role's ramp; write the ramp as '<name> <light step>/<dark step>'")
    for n in known:
        if n != "status" and len(by.get(n, [])) > 1:
            add("PAL-01", "SHOULD", "review", "more than one row for role '%s'; only the first row is checked" % n, "keep one row per role (status may repeat)")
    for r in rows:
        if r["role"] not in known:
            add("PAL-01", "SHOULD", "review", "unknown role '%s' counted as a brand hue" % r["role"],
                "use one of brand, brand-2, neutral, background, text, status")
    if any(n not in by or not ok(by[n][0]) for n in required):
        for rid, why in (("PAL-02", "brand hues"), ("PAL-03", "ramp order"), ("EVD-02", "role contrast"), ("EVD-03", "pairs to tell apart"), ("EVD-04", "colour-blind distance"), ("PAL-07", "category colours")):
            add(rid, "SHOULD", "not run", "the roles table is incomplete (see brd:PAL-01), so the %s check was not run" % why, "complete the roles table")
        return
    brands = [r for r in rows if r["role"] not in ("neutral", "background", "text", "status") and ok(r)]
    statuses = [r for r in rows if r["role"] == "status" and ok(r)]
    # PAL-02: hues within same_hue_window_deg count as one
    hues = [(r["role"], hue_chroma(r["light"])[0]) for r in brands]
    clusters = []
    for name, h in hues:
        for cl in clusters:
            if any(hue_gap(h, h2) <= th["same_hue_window_deg"] for _, h2 in cl):
                cl.append((name, h))
                break
        else:
            clusters.append([(name, h)])
    if len(clusters) > th["max_brand_hues"]:
        add("PAL-02", "SHOULD", "fail", "%d brand hues (%s), budget %d (hues within %d degrees count as one)" %
            (len(clusters), ", ".join(n for n, _ in hues), th["max_brand_hues"], th["same_hue_window_deg"]),
            "merge or drop a hue, or state why in the palette rationale line")
    for cl in clusters:
        if len(cl) > 1:
            add("PAL-02", "SHOULD", "review", "%s are within %d degrees of hue and count as one hue" %
                (" and ".join(n for n, _ in cl), th["same_hue_window_deg"]), "merge them, or give the second a reason")
    # PAL-03: within one ramp, lightness falls as the step number rises
    ramps = {}
    for r in rows:
        if r["ramp"] and ok(r):
            ramps.setdefault(r["ramp"], []).append(r)
    for name, rs in ramps.items():
        for v, step in (("light", "lstep"), ("dark", "dstep")):
            seq = sorted(((r[step], oklab(r[v])[0], r["role"]) for r in rs), key=lambda t: t[0])
            for (s1, l1, r1), (s2, l2, r2) in zip(seq, seq[1:]):
                if s2 > s1 and l2 >= l1 - 1e-9:
                    add("PAL-03", "SHOULD", "fail", "ramp %s (%s values): step %d (%s) is not darker than step %d (%s)" % (name, v, s2, r2, s1, r1),
                        "rebuild the ramp: lightness must fall as the step number rises")
    # EVD-02 widened: floors per role, light on light and dark on dark
    for v in ("light", "dark"):
        bg = by["background"][0][v]
        for r in rows:
            if r["role"] in ("background",) or not ok(r):
                continue
            floor = th["contrast_text"] if r["role"] in ("text", "neutral") else th["contrast_large_or_nontext"]
            c = contrast(r[v], bg)
            if c is not None and c < floor:
                add("EVD-02", "SHOULD", "fail", "%s %s %s on background %s is %.4f:1, need %.1f" % (v, r["role"], r[v], bg, c, floor), FIX["EVD-02"])
    # EVD-03 and EVD-04: brand against brand-2, and every two status colours
    pairs = []
    b1, b2 = (by.get("brand") or [None])[0], (by.get("brand-2") or [None])[0]
    if b1 and b2 and ok(b1) and ok(b2):
        pairs.append(("brand", "brand-2", b1, b2))
    for i, a in enumerate(statuses):
        for b in statuses[i + 1:]:
            pairs.append(("status %s" % (a["ramp"] or i), "status %s" % (b["ramp"] or "other"), a, b))
    cue = brief["keys"].get("pair-cue", "")
    cue = "" if PLACEHOLDER.fullmatch(cue.strip()) else cue
    for n1, n2, a, b in pairs:
        for v in ("light", "dark"):
            c = contrast(a[v], b[v])
            if c is not None and c < th["contrast_large_or_nontext"]:
                if cue:
                    add("EVD-03", "SHOULD", "pass", "%s %s and %s %s differ by only %.2f:1 (%s); told apart by the declared cue: %s" % (n1, a[v], n2, b[v], c, v, cue), "none")
                    continue
                add("EVD-03", "SHOULD", "review", "%s %s and %s %s differ by only %.2f:1 (%s)" % (n1, a[v], n2, b[v], c, v),
                    "name a non-colour cue (shape, text, pattern) in the palette rationale, or move one lightness")
            for kind in CVD:
                d = ok_dist(cvd_oklab(a[v], kind), cvd_oklab(b[v], kind))
                if d < th["cvd_min_oklab_distance"]:
                    add("EVD-04", "SHOULD", "review" if kind == "tritanopia" else "fail",
                        "%s and %s (%s) look alike under %s simulation: Oklab distance %.3f, need %.2f" % (n1, n2, v, kind, d, th["cvd_min_oklab_distance"]),
                        "change lightness first, then hue")
    # PAL-08 for the brand sheet: hex values it shows must be role values, palette-line values or category colours
    sheet = os.path.join(os.path.dirname(os.path.abspath(path)), "brand-sheet.md")
    if os.path.isfile(sheet):
        known = {r[v] for r in rows for v in ("light", "dark") if r.get(v)} | {c for c, _ in brief["palette"]}
        known |= {norm_colour(h) for h in re.findall(r"#[0-9a-fA-F]{6}", brief["keys"].get("category-colours", ""))}
        known |= {"#000000", "#ffffff"}
        stale = sorted({norm_colour(h) for h in re.findall(r"#[0-9a-fA-F]{6}\b", open(sheet, encoding="utf-8", errors="replace").read())} - known)
        if stale:
            add("PAL-08", "SHOULD", "review", "brand-sheet.md shows colours that are not in the roles table, palette line or category colours: %s" % ", ".join(stale),
                "regenerate the sheet from the brief")
    # PAL-07 (script part): a 'break' colour must sit outside the hue window of every brand hue
    for m in re.finditer(r"([^;#]*?)\s*(#[0-9a-fA-F]{6})\s+break\b", brief["keys"].get("category-colours", "")):
        h, c = hue_chroma(norm_colour(m.group(2)))
        near = [n for n, bh in hues if c > th["achromatic_chroma"] and hue_gap(h, bh) <= th["same_hue_window_deg"]]
        if near:
            add("PAL-07", "SHOULD", "fail", "category colour %s %s is marked 'break' but lies within %d degrees of the brand hue (%s)" %
                (m.group(1).strip() or "(unnamed)", m.group(2), th["same_hue_window_deg"], ", ".join(near)),
                "pick a hue further away, or mark it 'follow' with a distinct shade")


PLACEHOLDER = re.compile(r"(<.*>|tbd|tbc|todo|n/?a|none|assumed|\?+|-+|\.+|\u2026)(\s*\(.*\))?", re.I)


def check_positioning(path, th, brief, out, concept=False):
    """POS-01, POS-02 presence checks, TYP-05 and TYP-06 from the 'type:' rationale line; content is read by the reviewer."""
    def add(rid, status, msg, fix):
        out.append({"id": "brd:" + rid, "severity": "SHOULD", "status": status, "file": path, "finding": msg, "fix": fix, "evidence": "script"})
    k = brief["keys"]
    present = any(k.get(x) for x in ("positioning", "own-word", "assets", "category-colours")) or brief["has_rationale"]
    if not present:
        add("POS-01", "n/a", "no positioning fields or rationale section in the brief (a 0.1.x brief); POS-01 and POS-02 not run",
            "add positioning, own-word and a '## Rationale' section")
        return
    bad = [x for x in ("positioning", "own-word") if not k.get(x) or PLACEHOLDER.fullmatch(k[x].strip())]
    if k.get("positioning") and "positioning" not in bad and len(k["positioning"].split()) < 6:
        bad.append("positioning (too short to name audience, category, benefit and alternative)")
    if bad:
        add("POS-01", "fail", "brief field missing, empty or a placeholder: %s" % ", ".join(bad),
            "draft both from the narrative, mark them assumed, confirm with the user")
    words = [w.strip().lower() for w in re.split(r"[,;]", k.get("tone", "")) if w.strip()]
    heads = {l.split(":", 1)[0].strip().lower() for l in brief["rationale"] if ":" in l}
    gone = [w for w in words + ["palette", "type"] if w not in heads]
    if gone and concept:
        add("POS-02", "n/a", "concept stage: the '## Rationale' lines are written at kit steps 2 and 3, not yet checked", "none")
    elif gone:
        add("POS-02", "fail", "'## Rationale' has no line for: %s" % ", ".join(gone),
            "add one '- <word>: ...' line per tone word, plus '- palette: ...' and '- type: ...'")
    n = len(brief["story"])
    if n == 0 and concept:
        add("POS-05", "n/a", "concept stage: the '## Story' is written at kit step 7, not yet checked", "none")
    elif n == 0:
        add("POS-05", "fail", "no '## Story' section with at least one paragraph; the applications page falls back to labelled brief fields",
            "draft two to four short paragraphs from the finished brief, set story-status: assumed, and confirm with the user")
    elif n > th["max_story_paragraphs"]:
        add("POS-05", "fail", "'## Story' has %d paragraphs, budget %d" % (n, th["max_story_paragraphs"]), "cut it to the beats that point at a choice in the kit")
    elif brief["story_status"] != "confirmed":
        add("POS-05", "review", "the story is a draft (story-status is '%s'); confirm it with the user, then set story-status: confirmed" % (brief["story_status"] or "not set"),
            "show the story at the final report and ask for edits")
    typ = [l for l in brief["rationale"] if l.lower().startswith("type:")]
    if typ:
        body = typ[0].split(":", 1)[1].strip()
        fams = [f for f in re.split(r"\s*\+\s*", re.split(r"\.(?:\s|$)", body, maxsplit=1)[0]) if f.strip()]
        if len(fams) > th["max_type_families"] + 1:
            add("TYP-05", "fail", "%d type families (%s), budget %d" % (len(fams), ", ".join(fams), th["max_type_families"]), FIX["TYP-05"])
        elif len(fams) > th["max_type_families"]:
            add("TYP-05", "review", "%d type families; the extra one needs a stated role in the type line" % len(fams), FIX["TYP-05"])
        for m in re.finditer(r"(?:smallest|minimum|min)\s*(?:text\s*)?(?:size\s*)?(?:of\s*)?(\d+(?:\.\d+)?)\s*px", body, re.I):
            if float(m.group(1)) < th["min_text_px"]:
                add("TYP-06", "fail", "stated smallest text size %s px is below %s px" % (m.group(1), th["min_text_px"]), FIX["TYP-06"])


WALK_SKIP = {"concepts", "exports", "renders", "checks", "icons"}  # a folder argument skips these: drafts, copies, outputs and the icon set (--icons)


def walk_svgs(root):
    found = []
    for r, ds, fs in os.walk(root):
        ds[:] = sorted(x for x in ds if x not in WALK_SKIP)
        found += [os.path.join(r, f) for f in sorted(fs) if f.lower().endswith(".svg")]
    return found


def is_dark(stem):
    """A stem with a reversed or dark word is made for a dark surface. A naming convention, like tile names."""
    return bool(re.search(r"(^|[-_.])(reversed|dark)([-_.]|$)", stem.lower()))


def is_tile(stem):
    """Tiles, app icons, social images and favicons carry a background on purpose. A naming convention, not a measurement."""
    s = stem.lower()
    return s.startswith(("app-icon", "social", "favicon")) or "-tile" in s


def read_png_rgba(path):
    """8-bit non-interlaced PNG (grey, grey+alpha, RGB or RGBA) to (width, height, rows, alpha offset or None). Raises ValueError for anything else.
    A renderer drops the alpha channel when the whole image is opaque, so the no-alpha types must be readable."""
    data = open(path, "rb").read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG: " + path)
    pos, idat, hdr = 8, b"", None
    while pos + 8 <= len(data):
        n, typ = struct.unpack(">I4s", data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + n]
        pos += 12 + n
        if typ == b"IHDR":
            hdr = struct.unpack(">IIBBBBB", body)
        elif typ == b"IDAT":
            idat += body
    if hdr is None:
        raise ValueError("no IHDR")
    w, h, depth, ctype, _, _, interlace = hdr
    bpp = {0: 1, 2: 3, 4: 2, 6: 4}.get(ctype)
    if depth != 8 or bpp is None or interlace != 0:
        raise ValueError("unsupported PNG (bit depth %d, colour type %d, interlace %d); need 8-bit grey, RGB or RGBA, non-interlaced" % (depth, ctype, interlace))
    raw = zlib.decompress(idat)
    stride = w * bpp
    rows, prev = [], bytearray(stride)
    for y in range(h):
        f = raw[y * (stride + 1)]
        line = bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        for i in range(stride):
            a = line[i - bpp] if i >= bpp else 0
            b = prev[i]
            c = prev[i - bpp] if i >= bpp else 0
            if f == 1: line[i] = (line[i] + a) & 255
            elif f == 2: line[i] = (line[i] + b) & 255
            elif f == 3: line[i] = (line[i] + (a + b) // 2) & 255
            elif f == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[i] = (line[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        rows.append(line)
        prev = line
    return w, h, rows, ({4: 1, 6: 3}.get(ctype))


def png_width(path):
    head = open(path, "rb").read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n" or head[12:16] != b"IHDR":
        raise ValueError("not a PNG: " + path)
    return struct.unpack(">I", head[16:20])[0]


def opaque_ratio(path):
    """Share of pixels with any opacity. A background covers nearly all of the image; a mark or wordmark does not."""
    w, h, rows, a = read_png_rgba(path)
    if a is None:
        return 1.0  # no alpha channel: every pixel is opaque
    step = 2 if a == 1 else 4
    return sum(1 for r in rows for x in range(w) if r[step * x + a] > 0) / float(w * h)


def check_exports(d, th, out):
    """CTR-06: the downloadable set exists, matches the masters, is transparent and bundled. Reads the files, not the manifest's claims."""
    def fail(msg):
        out.append({"id": "brd:CTR-06", "severity": "MUST", "status": "fail", "file": d, "finding": msg, "fix": FIX["CTR-06"], "evidence": "script"})
    if not os.path.isdir(d):
        return fail("no exports folder; a delivered kit needs downloadable SVG and transparent PNG assets")
    try:
        man = json.load(open(os.path.join(d, "manifest.json")))
    except (OSError, ValueError):
        return fail("no readable manifest.json; exports were not made with brdrender.py --export")
    if not isinstance(man, dict) or not isinstance(man.get("files"), dict) or not man["files"]:
        return fail("manifest.json is malformed or lists no files")
    root = os.path.realpath(d)
    top = os.path.dirname(os.path.abspath(d))
    sizes = [int(x) for x in th["export_sizes_px"]]
    probe = min(sizes, key=lambda x: abs(x - 64))
    safe = []
    for stem in sorted(man["files"]):
        if not re.fullmatch(r"[^/\\\x00:]+", stem) or stem.startswith("."):
            fail("unsafe file name in the manifest: %r" % stem[:40])
            continue
        want = {"svg": os.path.join(d, "svg", stem + ".svg")}
        want.update({s: os.path.join(d, "png", "%s-%d.png" % (stem, s)) for s in sizes})
        gone = [k for k, p in want.items() if not os.path.isfile(p) or not os.path.realpath(p).startswith(root + os.sep)]
        if gone:
            fail("%s: missing export file(s): %s" % (stem, ", ".join(os.path.relpath(want[k], d) for k in gone[:4])))
            continue
        safe.append(stem)
        master = os.path.join(top, stem + ".svg")
        if os.path.isfile(master) and open(master, "rb").read() != open(want["svg"], "rb").read():
            fail("%s: the exported SVG differs from brand/%s.svg; export again" % (stem, stem))
        try:
            wrong = [s for s in sizes if png_width(want[s]) != s]
        except (OSError, ValueError, struct.error):
            fail("%s: a PNG in the set is not a valid PNG" % stem)
            continue
        if wrong:
            fail("%s: PNG width does not match its size in the name: %s" % (stem, ", ".join(str(x) for x in wrong[:4])))
            continue
        if not is_tile(stem):
            try:
                ratio = opaque_ratio(want[probe])
            except (OSError, ValueError, zlib.error, struct.error) as e:
                fail("%s: the %d px PNG cannot be read (%s)" % (stem, probe, str(e)[:80]))
                continue
            if ratio >= th["export_background_coverage"]:
                fail("%s: the PNG has a background (%.0f%% of its pixels are opaque); exports must be transparent unless named as a tile, app icon, social image or favicon" % (stem, ratio * 100))
    on_disk = {os.path.splitext(f)[0] for f in os.listdir(top) if f.lower().endswith(".svg")}
    absent = sorted(on_disk - set(man["files"]))
    if absent:
        fail("not exported: %s" % ", ".join(absent[:6]))
    zips = [f for f in os.listdir(d) if f.lower().endswith(".zip")]
    if not zips:
        return fail("no zip bundle of the exports")
    need = {"svg/%s.svg" % st for st in safe} | {"png/%s-%d.png" % (st, sz) for st in safe for sz in sizes}
    for z in zips:
        zp = os.path.join(d, z)
        try:
            ok_zip = zipfile.is_zipfile(zp)
            with zipfile.ZipFile(zp) as zf:
                names = set(zf.namelist())
                bad_member = zf.testzip() if ok_zip else None
        except (OSError, zipfile.BadZipFile):
            ok_zip, names, bad_member = False, set(), None
        if not ok_zip:
            fail("%s is not a valid zip file" % z)
        elif bad_member:
            fail("%s: member %s is damaged" % (z, bad_member))
        elif need - names:
            fail("%s does not hold every exported file (missing %d, for example %s)" % (z, len(need - names), sorted(need - names)[0]))


def check_brief_palette(path, th, brief, out):
    if brief["roles"]:
        check_roles(path, th, brief, out)
        return
    pal = brief["palette"]
    if not pal:
        out.append({"id": "brd:EVD-02", "severity": "SHOULD", "status": "n/a", "file": path,
                    "finding": "no usable palette line in the brief; nothing to check yet",
                    "fix": "add a palette line to the brief", "evidence": "script"})
    bgs = [c for c, r in pal if r == "background"]
    if pal and not bgs:
        out.append({"id": "brd:EVD-02", "severity": "SHOULD", "status": "review", "file": path,
                    "finding": "the palette has no background colour, so contrast was not checked",
                    "fix": "add a background entry to the palette line", "evidence": "script"})
    for c, role in pal:
        if role not in ("text", "ui", "mark"):
            continue
        for bg in bgs:
            r = contrast(c, bg)
            if r is None:
                continue
            need = th["contrast_text"] if role == "text" else th["contrast_large_or_nontext"]
            if role == "mark":
                out.append({"id": "brd:EVD-02", "severity": "SHOULD", "status": "review", "file": path,
                            "finding": "mark %s on %s is %.2f:1 (a brand logo may be exempt, only if the low contrast is brand-mandated and it is not a control; flagged)" % (c, bg, r),
                            "fix": "report only; make sure the logo is not used as a link or control", "evidence": "script"})
            elif r < need:
                out.append({"id": "brd:EVD-02", "severity": "SHOULD", "status": "fail", "file": path,
                            "finding": "%s %s on %s is %.2f:1, need %.1f" % (role, c, bg, r, need),
                            "fix": FIX["EVD-02"], "evidence": "script"})


def check_icons(d, th, out):
    def add(rule, status, msg, f):
        out.append({"id": "brd:" + rule, "severity": SEV[rule], "status": status, "file": f,
                    "finding": msg, "fix": FIX[rule], "evidence": "script"})
    spec_path = os.path.join(d, "style-spec.json")
    spec = None
    if not os.path.exists(spec_path):
        add("SET-02", "fail", "style-spec.json missing", spec_path)
    else:
        try:
            spec = json.load(open(spec_path, encoding="utf-8"))
            miss = [k for k in ("grid", "strokeWidth", "strokeLinecap", "strokeLinejoin", "cornerRadius", "padding") if k not in spec]
            if miss:
                add("SET-02", "fail", "missing keys: " + ", ".join(miss), spec_path)
        except ValueError:
            add("SET-02", "fail", "invalid JSON", spec_path)
    seen = {}
    for f in sorted(os.listdir(d)):
        if not f.lower().endswith(".svg"):
            continue
        p = os.path.join(d, f)
        raw = open(p, encoding="utf-8", errors="replace").read()
        if re.search(r"<!DOCTYPE|<!ENTITY", raw, re.I):
            add("SEC-01", "fail", "DOCTYPE or ENTITY declaration; file not parsed", p)
            continue
        try:
            root = ET.fromstring(raw)
        except ET.ParseError:
            add("SET-01", "fail", "does not parse", p)
            continue
        tmp = []
        check_svg(p, th, {"palette": [], "grid": None, "waivers": []}, None, tmp)
        out.extend(f for f in tmp if f["id"] in ("brd:SEC-01", "brd:CTR-04", "brd:TYP-01", "brd:CTR-01"))
        key = (root.get("viewBox"), root.get("stroke-width"), root.get("stroke-linecap"), root.get("stroke-linejoin"), root.get("fill"))
        seen[p] = key
        if spec and "strokeWidth" in spec and root.get("stroke-width") and float(root.get("stroke-width")) != float(spec["strokeWidth"]):
            add("SET-01", "fail", "stroke-width %s disagrees with style-spec %s" % (root.get("stroke-width"), spec["strokeWidth"]), p)
        bad = {c for e in root.iter() for c in colours_of(e)}
        if bad:
            add("SET-03", "fail", "fixed colours %s; use currentColor" % ", ".join(sorted(bad)), p)
    if len(set(seen.values())) > 1:
        add("SET-01", "fail", "icons differ in viewBox or root stroke/fill attributes", d)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Deterministic checks of SVG logo files.")
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--brief")
    ap.add_argument("--grid-unit", type=float)
    ap.add_argument("--icons")
    ap.add_argument("--exports", help="the exports folder to check (brd:CTR-06)")
    ap.add_argument("--stage", choices=["auto", "concept", "kit"], default="auto", help="concept: brief-level rules that need kit sections print n/a; auto picks concept when the Palette roles table has no rows")
    ap.add_argument("--root", help="chdir here first; brand/ is resolved against it")
    ap.add_argument("--out", default="brand/checks/check.json")
    a = ap.parse_args(argv)
    if a.root:
        if not os.path.isdir(a.root):
            print("brdcheck: --root is not a directory: %s" % a.root, file=sys.stderr)
            return 2
        os.chdir(a.root)
    try:
        th = load_thresholds()
        brief = read_brief(a.brief)
        files = []
        for p in a.paths:
            if os.path.isdir(p):
                files += walk_svgs(p)
            elif os.path.isfile(p):
                files.append(p)
            else:
                raise InputError("no such file: " + p)
        if not files and not a.icons and not a.brief and not a.exports:
            raise InputError("nothing to check")
        out_abs = os.path.realpath(a.out)
        base = os.path.realpath("brand")
        if not (out_abs == base or out_abs.startswith(base + os.sep)):
            raise InputError("--out must be inside the brand folder (brand/)")
        if os.path.isdir(out_abs):
            raise InputError("--out must be a file path, not a folder")
        findings = []
        for f in files:
            check_svg(f, th, brief, a.grid_unit or brief["grid"], findings)
        if a.icons:
            check_icons(a.icons, th, findings)
        if a.exports:
            check_exports(a.exports, th, findings)
        if a.brief:
            check_brief_palette(a.brief, th, brief, findings)
            concept = a.stage == "concept" or (a.stage == "auto" and not brief["roles"])
            check_positioning(a.brief, th, brief, findings, concept)
            if not brief["wordmark_font"] and any(os.path.basename(f).lower().startswith(("wordmark", "lockup")) for f in files):
                findings.append({"id": "brd:TYP-01", "severity": "MUST", "status": "n/a" if concept else "fail", "file": a.brief,
                                 "finding": ("concept stage: the brief's wordmark-font is filled once a font is picked, not yet checked" if concept else
                                             "a wordmark file exists but the brief's wordmark-font is empty"),
                                 "fix": FIX["TYP-01"], "evidence": "script"})
    except InputError as e:
        print("brdcheck: %s" % e, file=sys.stderr)
        return 2
    today = datetime.date.today().isoformat()
    for f in findings:
        if f["status"] == "fail" and waived(f["id"].split(":")[1], f["file"], brief["waivers"], today):
            f["status"] = "waived"
    summary = {"fail_must": sum(f["severity"] == "MUST" and f["status"] == "fail" for f in findings),
               "fail_should": sum(f["severity"] != "MUST" and f["status"] == "fail" for f in findings),
               "review": sum(f["status"] == "review" for f in findings),
               "waived": sum(f["status"] == "waived" for f in findings)}
    brief_rules = []
    if a.brief:
        brief_rules = ["EVD-02", "POS-01", "POS-02", "POS-05"] + (["PAL-01", "PAL-02", "PAL-03", "PAL-07", "EVD-03", "EVD-04"] if brief["roles"] else [])
    os.makedirs(os.path.dirname(out_abs), exist_ok=True)
    json.dump({"script": "brdcheck", "version": VERSION, "thresholds": "references/thresholds.md", "tools": {},
               "files": files, "rules_checked": CHECKED + (["PAL-08"] if brief["roles"] else []), "brief_rules_checked": brief_rules,
               "exports_rules_checked": ["CTR-06"] if a.exports else [], "findings": findings, "summary": summary}, open(out_abs, "w"), indent=2)
    print("brdcheck %s: %d files, no optional tools used; rules checked per file: %s%s%s" % (
        VERSION, len(files), " ".join(CHECKED + (["PAL-08"] if brief["roles"] else [])),
        "; brief: " + " ".join(brief_rules) if brief_rules else "", "; exports: CTR-06" if a.exports else ""))
    lines = {}
    for f in findings:  # one line per defect: rules that report the same finding share a line
        ids, fixes = lines.setdefault((f["status"], f["file"], f["finding"]), ([], []))
        ids.append(f["id"])
        if f["fix"] not in fixes:
            fixes.append(f["fix"])
    shown = ["%s %s %s: %s -> %s [evidence: script]" % (st, ", ".join(ids), fl, fd, "; ".join(fx))
             for (st, fl, fd), (ids, fx) in lines.items()]
    print("\n".join(shown[:36]))
    if len(shown) > 36:
        print("... %d more in %s" % (len(shown) - 36, a.out))
    print("summary: %s" % json.dumps(summary))
    return 1 if summary["fail_must"] else 0


if __name__ == "__main__":
    sys.exit(main())
