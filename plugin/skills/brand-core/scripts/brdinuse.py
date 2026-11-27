#!/usr/bin/env python3
"""brdinuse: write brand/applications.html, the kit placed in everyday applications with every colour pair measured (see SPEC.md).

Reads the brief's palette roles and the kit's own SVG and PNG files. Standalone HTML: no external fonts, scripts or links.
Exit codes: 0 page written (pairs below their floor are printed as `fail brd:PAL-09` lines, a SHOULD), 2 usage or input error.
"""
import argparse, base64, html, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import brdcheck  # noqa: E402  (same folder; -I removes the script dir from sys.path)

VERSION = "0.1.0"
MAX_EMBED = 2 * 1024 * 1024  # a file larger than this is not embedded
TEXT = LARGE = UI = None  # set from thresholds.md in page_for: contrast_text and contrast_large_or_nontext, the numbers brd:EVD-02 uses
TAB_LIGHT, TAB_DARK = "#FFFFFF", "#14232F"  # assumed browser tab colours, not brand colours
e = html.escape
WORDS = {5: "five", 6: "six", 7: "seven"}  # the intro count word, computed from the number of mocks


class Fail(Exception):
    pass


def roles_by_variant(roles):
    out = {"light": {}, "dark": {}, "extra": {}}
    for r in roles:
        for v in ("light", "dark"):
            if not r.get(v):
                continue
            hx = r[v].upper()
            if r["role"] == "status":
                out[v].setdefault("status", []).append((r.get("ramp") or "status", hx))
            else:
                out[v].setdefault(r["role"], hx)
    return out


def data_uri(path, mime):
    try:
        if os.path.getsize(path) > MAX_EMBED:
            return None
        return "data:%s;base64,%s" % (mime, base64.b64encode(open(path, "rb").read()).decode())
    except OSError:
        return None


def first_sentence(text, limit=140):
    s = re.split(r"(?<=[.!?])\s", text.strip(), maxsplit=1)[0]
    if len(s) <= limit:
        return s
    return s[:limit].rsplit(" ", 1)[0].rstrip(",;:") + "…"


def field(text, key):
    m = re.search(r"^%s:[ \t]*(.*)$" % key, text, re.M)
    return m.group(1).strip() if m else ""


def story_html(brief, text):
    """The story at the top: the brief's ## Story paragraphs, or labelled facts quoted from the brief when there are none. Returns (html, note or None)."""
    paras = brief["story"]
    if paras:
        cap = int(brdcheck.load_thresholds()["max_story_paragraphs"])
        note = ("the story has %d paragraphs; showing the first %d" % (len(paras), cap)) if len(paras) > cap else None
        body = "".join("<p>%s</p>" % e(p) for p in paras[:cap])
        draft = "" if brief["story_status"] == "confirmed" else '<p class="draft">Draft story, not yet confirmed by the brand owner.</p>'
        return '<div class="story">%s%s</div>' % (body, draft), note
    tension = re.search(r"^- Tension:[ \t]*(.*)$", text, re.M)
    palette = field(text, "assets").split(";")
    rat = {l.split(":", 1)[0].lower(): l.split(":", 1)[1].strip() for l in brief["rationale"] if ":" in l}
    rows = [("Who it is for", field(text, "audience")), ("The tension", tension.group(1).strip() if tension else ""),
            ("The idea", field(text, "concept")), ("The word to own", field(text, "own-word")),
            ("The mark", field(text, "metaphor").split(" (")[0]), ("The palette", palette[-1].strip() if palette[-1].strip() else ""),
            ("The type", rat.get("type", "")), ("Tone", field(text, "tone"))]
    rows = [(k, v) for k, v in rows if v]
    if not rows:
        return "", None
    return '<dl class="facts">%s</dl>' % "".join("<div><dt>%s</dt><dd>%s</dd></div>" % (e(k), e(v[:1].upper() + v[1:])) for k, v in rows), None


def font_stack(rationale):
    line = next((l for l in rationale if l.lower().startswith("type:")), "")
    fam = re.split(r"\s*\+\s*|\.(?:\s|$)", line.split(":", 1)[1].strip(), maxsplit=1)[0].strip() if line else ""
    base = 'system-ui,-apple-system,"Segoe UI",Roboto,sans-serif'
    return ('"%s",%s' % (fam, base)) if re.fullmatch(r"[A-Za-z0-9 \-]{1,40}", fam) else base


class Kit:
    def __init__(self, brand):
        self.brand = brand

    def svg(self, *names):
        for n in names:
            p = os.path.join(self.brand, n + ".svg")
            if os.path.isfile(p):
                return n, data_uri(p, "image/svg+xml")
        return None, None

    def png(self, stem, size):
        return data_uri(os.path.join(self.brand, "exports", "png", "%s-%d.png" % (stem, size)), "image/png")


def img(uri, height, label, cls=""):
    if not uri:
        return ""
    return '<img src="%s" height="%d" alt="%s"%s>' % (uri, height, e(label), (' class="%s"' % cls) if cls else "")


def lockup(kit, names, height, label, name, ink):
    stem, uri = kit.svg(*names)
    if uri:
        return img(uri, height, label)
    _, m = kit.svg("mark")
    return '<span class="fallback">%s<b style="color:%s">%s</b></span>' % (img(m, height, ""), ink, e(name))


def page_for(brief_path, brand):
    global TEXT, LARGE, UI
    th = brdcheck.load_thresholds()
    TEXT, LARGE = float(th["contrast_text"]), float(th["contrast_large_or_nontext"])
    UI = LARGE
    brief = brdcheck.read_brief(brief_path)
    text = open(brief_path, encoding="utf-8").read()
    rv = roles_by_variant(brief["roles"])
    need = ("brand", "neutral", "background", "text")
    missing = ["%s (%s)" % (k, v) for v in ("light", "dark") for k in need if k not in rv[v]]
    if missing:
        raise Fail("the brief's ## Palette roles table lacks a valid #RRGGBB value for: " + ", ".join(missing))
    if not os.path.isfile(os.path.join(brand, "mark.svg")):
        raise Fail("no %s: draw the mark first" % os.path.join(brand, "mark.svg"))
    L, D = rv["light"], rv["dark"]
    name = field(text, "name") or "Brand"
    concept = first_sentence(field(text, "concept")) or name
    own = field(text, "own-word")
    kit = Kit(brand)
    notes = []
    if not kit.svg("mark-reversed")[1]:
        notes.append("no mark-reversed.svg: the dark mocks use mark.svg and may be unreadable")
    if not os.path.isdir(os.path.join(brand, "exports", "png")):
        notes.append("no exports folder: favicon and app icon are drawn from the SVG, not the exported PNGs")

    pairs = []  # (group, what, fg, bg, floor, kind)

    def P(group, what, fg, bg, floor, kind):
        pairs.append((group, what, fg, bg, floor, kind))

    # status icons: one per status row, tick for ok-like ramp names, cross otherwise
    def stat(v):
        return rv[v].get("status", [])[:2]

    def statuses(v):
        """(svg, label, hx, ramp) per status row: tick for ok-like ramps, then a cross, then a dash, so shape and text both differ."""
        out, other = [], 0
        for ramp, hx in stat(v):
            short = re.sub(r"\s+\d.*$", "", ramp)
            if re.search(r"ok|success|pass|green", ramp, re.I):
                d, lab = "M3 8.5l3.2 3.2L13 4.8", "Passed (%s)" % short
            else:
                d, lab = ("M4 4l8 8M12 4l-8 8" if other == 0 else "M3.5 8h9"), "Needs attention (%s)" % short
                other += 1
            out.append(('<svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true"><path d="%s" fill="none" stroke="%s" stroke-width="2.4"/></svg>' % (d, hx), lab, hx, ramp))
        return out

    # ---- 0 phone app (light roles)
    st = statuses("light")
    best = lambda bg: max((L["text"], L["background"]), key=lambda c: brdcheck.contrast(c, bg))
    chips = [(lab, hx) for _, lab, hx, _ in st] if len(st) >= 2 else [("Active", L["brand"])]
    rowhtml = ""
    for i, t in enumerate(("Item one", "Item two", "Item three")):
        lab, fill = chips[i % len(chips)]
        rowhtml += '<li><span>%s</span><b class="pill" style="background:%s;color:%s">%s</b></li>' % (t, fill, best(fill), e(lab))
    for lab, fill in chips:
        P("app", "Chip text (%s)" % lab, best(fill), fill, TEXT, "text")
    phone = ('<div class="mock phone" style="background:{bg};color:{tx}"><div class="appbar" style="border-bottom:1px solid {ne}">{mk}<strong>{n}</strong></div>'
             '<ul class="rows">{rows}</ul><button class="wide" style="background:{br};color:{bg};border:2px solid {br}">Primary action</button></div>').format(
        bg=L["background"], tx=L["text"], ne=L["neutral"], br=L["brand"], n=e(name), rows=rowhtml, mk=img(kit.svg("mark")[1], 28, name + " mark"))
    P("app", "App bar name and row text", L["text"], L["background"], TEXT, "text")
    P("app", "Primary button label", L["background"], L["brand"], TEXT, "text")

    # ---- 1 tab and home screen
    f16, f32 = kit.png("mark", 16), kit.png("mark", 32)
    r16 = kit.png("mark-reversed", 16)
    _, msvg = kit.svg("mark")
    _, rsvg = kit.svg("mark-reversed", "mark")
    fav_l = img(f16 or msvg, 16, name + " favicon", "fav")
    fav_d = img(r16 or rsvg, 16, name + " reversed favicon", "fav")
    zoom = ""
    for uri, px, mult in ((f16, 16, 6), (f32, 32, 3)):
        if uri:
            zoom += '<figure><img class="px" src="%s" width="%d" height="%d" alt="%d px favicon enlarged"><figcaption>%d px, shown %d×</figcaption></figure>' % (uri, px * mult, px * mult, px, px, mult)
    tile_png = kit.png("mark-reversed-tile", 128)
    tile_inner = (lambda s: img(tile_png, s, name + " app icon")) if tile_png else \
        (lambda s: '<span class="tilefill" style="background:%s;width:%dpx;height:%dpx">%s</span>' % (D["background"], s, s, img(rsvg, int(s * .7), "")))
    for s in (60, 40, 29):
        zoom += '<figure><div class="tile" style="width:%dpx;height:%dpx">%s</div><figcaption>App icon, %d px</figcaption></figure>' % (s, s, tile_inner(s), s)
    tab = ('<div class="frames"><div class="tabstrip" style="background:#E4E9ED;border-color:#D3DCE3"><div class="tab" style="background:%s;color:%s">%s<span>%s</span></div>'
           '<div class="tab ghost" style="color:%s"><span>Other tab</span></div></div>'
           '<div class="tabstrip" style="background:#0A131A;border-color:#2A3B49"><div class="tab" style="background:%s;color:%s">%s<span>%s</span></div>'
           '<div class="tab ghost" style="color:%s"><span>Other tab</span></div></div></div><div class="zoom">%s</div>') % (
        TAB_LIGHT, L["text"], fav_l, e(name), L["neutral"], TAB_DARK, D["text"], fav_d, e(name), D["neutral"], zoom)
    P("tab", "Mark ink on a light tab", L["brand"], TAB_LIGHT, UI, "graphic")
    P("tab", "Mark ink on a dark tab", D["text"], TAB_DARK, UI, "graphic")
    if "brand-2" in L and "brand-2" in D:
        P("tab", "Second colour of the mark on a light tab", L["brand-2"], TAB_LIGHT, UI, "graphic")
        P("tab", "Second colour of the mark on a dark tab", D["brand-2"], TAB_DARK, UI, "graphic")
    P("tab", "Tab title, light", L["text"], TAB_LIGHT, TEXT, "text")
    P("tab", "Tab title, dark", D["text"], TAB_DARK, TEXT, "text")

    # ---- 2 web page (light)
    lines = ""
    for ic, lab, hx, ramp in statuses("light"):
        lines += "<li>%s<span>%s</span></li>" % (ic, lab)
        P("web", "Status icon (%s)" % ramp, hx, L["background"], UI, "graphic")
    web = ('<div class="mock web" style="background:{bg};color:{tx}"><header style="border-bottom:1px solid #D3DCE3">{lock}<nav><a style="color:{tx}">One</a><a style="color:{tx}">Two</a><a style="color:{tx}">Three</a></nav></header>'
           '<main><h3>{h}</h3><p class="lead" style="color:{ne}">{lead} <a style="color:{br}">A text link</a></p>'
           '<div class="btns"><button style="background:{br};color:{bg};border:2px solid {br}">Primary action</button>'
           '<button style="background:transparent;color:{br};border:2px solid {br}">Secondary action</button></div><ul class="status">{lines}</ul></main></div>').format(
        bg=L["background"], tx=L["text"], ne=L["neutral"], br=L["brand"], h=e(name), lead=e(concept),
        lock=lockup(kit, ("lockup-horizontal",), 34, name, name, L["text"]), lines=lines)
    P("web", "Body, heading and nav", L["text"], L["background"], TEXT, "text")
    P("web", "Secondary line", L["neutral"], L["background"], TEXT, "text")
    P("web", "Link", L["brand"], L["background"], TEXT, "text")
    P("web", "Primary button label", L["background"], L["brand"], TEXT, "text")
    P("web", "Secondary button border", L["brand"], L["background"], UI, "UI component")

    # ---- 3 dark card
    rows = ""
    for ic, lab, hx, ramp in statuses("dark"):
        rows += '<div class="row">%s<span>%s</span></div>' % (ic, lab)
        P("card", "Status icon (%s)" % ramp, hx, D["background"], UI, "graphic")
    card = ('<div class="mock card" style="background:{bg};color:{tx}"><div class="cardhead">{mk}<div><strong>{n}</strong><span style="color:{ne}">Sample card</span></div></div>{rows}'
            '<div class="btns"><button style="background:{br};color:{bg};border:2px solid {br}">Confirm</button><a style="color:{br}">Details</a></div></div>').format(
        bg=D["background"], tx=D["text"], ne=D["neutral"], br=D["brand"], n=e(name), rows=rows, mk=img(rsvg, 40, name + " mark"))
    P("card", "Body text", D["text"], D["background"], TEXT, "text")
    P("card", "Secondary line", D["neutral"], D["background"], TEXT, "text")
    P("card", "Link", D["brand"], D["background"], TEXT, "text")
    P("card", "Button label", D["background"], D["brand"], TEXT, "text")

    # ---- 4 slide
    slide = ('<div class="mock slide" style="background:{bg};color:{tx}"><p class="eyebrow" style="color:{ne}">Sample slide</p><h3>{n}</h3><p class="sub" style="color:{ne}">{c}</p>'
             '<div class="slidefoot">{lock}<span style="color:{ne}">{o}</span></div></div>').format(
        bg=D["background"], tx=D["text"], ne=D["neutral"], n=e(name), c=e(concept), o=e(own),
        lock=lockup(kit, ("lockup-horizontal-reversed", "lockup-horizontal"), 34, name, name, D["text"]))
    P("slide", "Slide title (large)", D["text"], D["background"], LARGE, "large text")
    P("slide", "Subtitle", D["neutral"], D["background"], TEXT, "text")
    P("slide", "Footer note", D["neutral"], D["background"], TEXT, "text")

    # ---- 5 flyer
    flyer = ('<div class="mock flyer" style="background:{bg};color:{tx}"><div>{mk}</div><h3>{c}</h3><p>Sample text at body size, set in the declared type family.</p>'
             '<p class="small" style="color:{ne}">Small print at 12 px</p><div class="flyerfoot" style="border-top:1px solid #D3DCE3">{lock}</div></div>').format(
        bg=L["background"], tx=L["text"], ne=L["neutral"], c=e(concept), mk=img(msvg, 96, name + " mark"),
        lock=lockup(kit, ("lockup-stacked", "lockup-horizontal"), 64, name, name, L["text"]))
    P("flyer", "Headline and body", L["text"], L["background"], TEXT, "text")
    P("flyer", "Small print (12 px)", L["neutral"], L["background"], TEXT, "text")

    # ---- not offered as text
    no = []
    for v, c in (("light", L), ("dark", D)):
        if "brand-2" in c:
            no.append(("Second colour as text, %s" % v, c["brand-2"], c["background"], TEXT, "text"))
        for ramp, hx in rv[v].get("status", [])[:2]:
            no.append(("Status %s as text, %s" % (ramp, v), hx, c["background"], TEXT, "text"))

    story, story_note = story_html(brief, text)
    if story_note:
        notes.append(story_note)
    th_note = "Floors: %.1f:1 for text, %.1f:1 for large text, icons and UI components." % (TEXT, UI)
    return dict(story=story, pairs=pairs, no=no, name=name, font=font_stack(brief["rationale"]), notes=notes, th_note=th_note,
                parts=[("Phone app", "light roles", phone, "app", "For a brand that ships a mobile app. Chip text names the status ramp, so statuses differ by text as well as colour."),
                       ("Browser tab and home screen", "small-size legibility · brd:CTR-06", tab, "tab", "Favicon and app icon come from the exported PNGs when they exist."),
                       ("Web page", "light roles", web, "web", ""), ("Dark card", "dark roles", card, "card", ""),
                       ("Slide, 16:9", "dark roles", slide, "slide", ""), ("Flyer, A5", "light roles", flyer, "flyer", "")],
            light=L, dark=D)


def table(rows):
    out = []
    for what, fg, bg, floor, kind in rows:
        c = brdcheck.contrast(fg, bg)
        ok = c >= floor
        out.append('<tr><th scope="row" data-label="Pair">%s</th><td data-label="Colours"><span class="chip" style="background:%s;color:%s">Aa</span> <span class="mono">%s on %s</span></td><td class="num" data-label="Measured">%.2f:1</td><td class="num" data-label="Floor">%.1f:1 <span class="muted">%s</span></td><td data-label="Result"><span class="res %s">%s</span></td></tr>'
                   % (e(what), bg, fg, fg, bg, c, floor, e(kind), "ok" if ok else "bad", "pass" if ok else "below floor"))
    return '<div class="scroll"><table><thead><tr><th>Pair</th><th>Colours</th><th>Measured</th><th>Floor</th><th>Result</th></tr></thead><tbody>%s</tbody></table></div>' % "".join(out)


CSS = """
:root{--bg:#FFFFFF;--surface:#FFFFFF;--ink:#1A1A1A;--muted:#5F6368;--line:#E5E7EB;--ok:#02470A;--ok-bg:#E3F0E4;--bad:#9B2C26;--bad-bg:#FBE9E7;--sans:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;--bf:%(font)s;--mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:400 15px/1.55 var(--sans);padding-block:32px 64px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
main.page{max-width:880px;margin:0 auto;display:grid;gap:40px}
h1{font:700 30px/1.15 var(--sans);margin:0 0 8px}h2{font:600 19px/1.25 var(--sans);margin:0}p{margin:0}
.muted{color:var(--muted)}.mono{font-family:var(--mono);font-size:12.5px}
.intro{display:grid;gap:12px;max-width:68ch}
.verdict{display:flex;flex-wrap:wrap;gap:8px 20px;align-items:baseline;padding:14px 16px;background:var(--surface);border:1px solid var(--line);border-radius:8px}.verdict strong{font-size:22px}
section{display:grid;gap:14px}
.stephead{display:flex;flex-wrap:wrap;gap:4px 14px;align-items:baseline;justify-content:space-between;border-bottom:1px solid var(--line);padding-bottom:8px}
.rules{font:500 12px var(--mono);color:var(--muted)}
.scroll{overflow-x:auto}table{border-collapse:collapse;width:100%%;font-size:13.5px}
th,td{text-align:left;padding:7px 10px;border-bottom:1px solid var(--line);vertical-align:middle}
thead th{font:600 11.5px var(--sans);letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}tbody th{font-weight:500}
td.num{font-variant-numeric:tabular-nums;white-space:nowrap}
.chip{display:inline-grid;place-items:center;width:34px;height:24px;border-radius:4px;font:600 12px var(--bf);border:1px solid var(--line)}
.res{display:inline-block;padding:2px 9px;border-radius:99px;font-size:12px;font-weight:600}.res.ok{background:var(--ok-bg);color:var(--ok)}.res.bad{background:var(--bad-bg);color:var(--bad)}
.note{padding:12px 14px;background:var(--surface);border:1px solid var(--line);border-radius:8px;max-width:72ch}
.frames{display:grid;gap:10px}.tabstrip{display:flex;gap:4px;padding:8px 8px 0;border:1px solid;border-radius:8px 8px 0 0;height:44px;align-items:flex-end}
.tab{display:flex;align-items:center;gap:8px;padding:0 14px;height:34px;border-radius:8px 8px 0 0;font:500 13px var(--bf);white-space:nowrap}.tab.ghost{background:transparent}
.zoom{display:flex;flex-wrap:wrap;gap:20px;align-items:flex-end}.zoom figure{margin:0;display:grid;gap:6px;justify-items:start}.zoom figcaption{font-size:12px;color:var(--muted)}
.px{image-rendering:pixelated;background:repeating-conic-gradient(#E4E9ED 0 25%%,#FFFFFF 0 50%%) 0 0/12px 12px;border:1px solid var(--line)}
.tile{overflow:hidden;border-radius:22%%}.tile img,.tilefill{display:block}.tilefill{display:grid;place-items:center}
.mock{border:1px solid var(--line);border-radius:10px;overflow:hidden}.mock{font-family:var(--bf)}.mock h3{font:700 24px/1.2 var(--bf);margin:0 0 8px}
.mock button{font:600 14px var(--bf);padding:9px 16px;border-radius:6px}.mock .btns{display:flex;flex-wrap:wrap;gap:10px;align-items:center}.mock a{font-weight:500;text-decoration:underline;text-underline-offset:3px}
.web header{display:flex;flex-wrap:wrap;gap:10px 28px;align-items:center;padding:16px 24px}.web nav{display:flex;gap:20px;font-size:14px}.web main{padding:28px 24px 32px;display:grid;gap:14px}.web .lead{max-width:60ch}
.status{list-style:none;margin:4px 0 0;padding:0;display:grid;gap:8px;font-size:14px}.status li,.card .row{display:flex;gap:10px;align-items:center}
.card{max-width:420px;padding:20px;display:grid;gap:14px}.cardhead{display:flex;gap:12px;align-items:center}.cardhead div{display:grid;font-size:14px}.card .row{font-size:14px}
.slide{min-height:240px;padding:24px 22px;display:flex;flex-direction:column;gap:10px}.slide h3{font-size:clamp(24px,5vw,44px)}.slide .sub{font-size:clamp(14px,2vw,18px);max-width:34ch}
.slide .eyebrow{font:600 12px var(--bf);letter-spacing:.1em;text-transform:uppercase}
.slidefoot{margin-top:auto;padding-top:16px;display:flex;flex-wrap:wrap;gap:8px 16px;justify-content:space-between;align-items:center;font-size:12px}
@media (min-width:640px){.slide{aspect-ratio:16/9;min-height:0;padding:6%% 7%%;justify-content:center}.slidefoot{position:absolute;left:7%%;right:7%%;bottom:6%%;padding-top:0}.slide{position:relative}}
.phone{max-width:300px;border:6px solid var(--ink);border-radius:30px;padding:0 0 18px;display:grid;gap:14px;align-content:start}
.appbar{display:flex;gap:10px;align-items:center;padding:14px 16px;font-size:15px}.rows{list-style:none;margin:0;padding:0 16px;display:grid;gap:10px;font-size:14px}
.rows li{display:flex;gap:8px;justify-content:space-between;align-items:center}.pill{font:600 11.5px var(--bf);padding:3px 9px;border-radius:99px;text-align:right}
.phone .wide{margin:0 16px}
.flyer{max-width:340px;aspect-ratio:148/210;padding:28px 26px;display:grid;align-content:start;gap:12px;grid-template-rows:auto auto auto auto 1fr}.flyer h3{font-size:22px}.flyer p{font-size:14px}.flyer p.small{font-size:12px}.flyerfoot{padding-top:14px;align-self:end}
.fallback{display:inline-flex;gap:10px;align-items:center}
.story{display:grid;gap:10px;max-width:62ch}.story .draft{font-size:12.5px;color:var(--muted);border-left:3px solid var(--muted);padding-left:10px}
.facts{margin:0;display:grid;gap:8px;max-width:72ch}.facts>div{display:grid;grid-template-columns:minmax(0,9.5em) 1fr;gap:4px 14px;align-items:baseline}
.facts dt{font:600 12px var(--sans);letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}.facts dd{margin:0}
@media (max-width:520px){.facts>div{grid-template-columns:1fr}}
@media (min-width:601px){table{min-width:560px}}
@media (max-width:600px){table,tbody,tr,th,td{display:block}thead{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
tr{padding:8px 0;border-bottom:1px solid var(--line)}th,td{border:0;padding:3px 10px;display:flex;gap:12px;justify-content:space-between;align-items:center;text-align:right}
th[data-label],td[data-label]{}th::before,td::before{content:attr(data-label);font:600 11.5px var(--sans);letter-spacing:.06em;text-transform:uppercase;color:var(--muted);text-align:left;flex:none}}
.embed .intro{display:none}
"""


def render(d):
    L, D = d["light"], d["dark"]
    bad = [p for p in d["pairs"] if brdcheck.contrast(p[2], p[3]) < p[4]]
    css = CSS % dict(font=d["font"])
    secs = "".join('<section><div class="stephead"><h2>%s</h2><span class="rules">%s</span></div>%s%s%s</section>' % (
        e(t), e(r), mock, table([p[1:] for p in d["pairs"] if p[0] == g]), ('<p class="note">%s</p>' % e(n)) if n else "")
        for t, r, mock, g, n in d["parts"])
    no = ""
    if d["no"]:
        nb = sum(1 for p in d["no"] if brdcheck.contrast(p[1], p[2]) < p[3])
        no = ('<section><div class="stephead"><h2>Not offered as text</h2><span class="rules">brd:PAL-05 · brd:EVD-02</span></div>%s'
              '<p class="note">%d of %d fail. These are colours the roles table does not offer as text. A row that fails shows why; a row that passes is a brand choice, not a limit.</p></section>') % (table(d["no"]), nb, len(d["no"]))
    notes = "".join("<p class=\"note\">%s</p>" % e(n) for n in d["notes"])
    n, ok = len(d["pairs"]), len(d["pairs"]) - len(bad)
    return ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
            '<title>%s applications</title><style>%s</style><script>if(/[?&]embed\\b/.test(location.search))document.documentElement.className+=\' embed\'</script></head><body><main class="page"><div class="intro"><h1>Applications</h1>%s'
            '<p>The kit placed in %s everyday applications, using only the colours in its roles table. Every colour pair is measured. The copy is placeholder text, set in the declared type family where it is installed and in a system font otherwise.</p>'
            '<div class="verdict"><strong>%d of %d pairs clear their floor</strong><span class="muted">%s</span></div>%s</div>%s%s</main></body></html>\n') % (
        e(d["name"]), css, d["story"], WORDS[len(d["parts"])], ok, n, e(d["th_note"]), notes, secs, no), bad


def main(argv=None):
    ap = argparse.ArgumentParser(prog="brdinuse", description=__doc__.splitlines()[0])
    ap.add_argument("--brief", default="brand/brief.md")
    ap.add_argument("--brand", default="brand", help="folder with mark.svg and the other kit files")
    ap.add_argument("--root", default=None, help="project folder to work in; the other paths are relative to it")
    ap.add_argument("--out", default=None, help="default <brand>/applications.html; must be inside the brand folder")
    a = ap.parse_args(argv)
    if a.root is not None:
        if not os.path.isdir(a.root):
            print("brdinuse: --root is not a directory: %s" % a.root, file=sys.stderr)
            return 2
        os.chdir(a.root)
    try:
        brand = os.path.realpath(a.brand)
        out = os.path.realpath(a.out or os.path.join(a.brand, "applications.html"))
        if not (out.startswith(brand + os.sep)) or os.path.isdir(out) or not out.lower().endswith(".html"):
            raise Fail("--out must be an .html file path inside the brand folder")
        if not os.path.isfile(a.brief):
            raise Fail("cannot read brief: %s" % a.brief)
        d = page_for(a.brief, brand)
        doc, bad = render(d)
    except (Fail, brdcheck.InputError) as ex:
        print("brdinuse: %s" % ex, file=sys.stderr)
        return 2
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(doc)
    n = len(d["pairs"])
    print("brdinuse %s: wrote %s; %d of %d pairs clear their floor" % (VERSION, os.path.relpath(out), n - len(bad), n))
    for note in d["notes"]:
        print("note: " + note)
    for g, what, fg, bg, floor, kind in bad[:30]:
        print("fail brd:PAL-09 %s: %s %s on %s is %.2f:1, floor %.1f:1 -> change the role value or the use, then run again [evidence: script]" % (
            g, what, fg, bg, brdcheck.contrast(fg, bg), floor))
    return 0


if __name__ == "__main__":
    sys.exit(main())
