"""INSTAGRAM folder video 59320997.mp4 as Stock templates (ig10-*). See docs/plan-instagram.md.

59320997.mp4 (960×540 at 25 fps, 27 s): five «models» stories on a pale pink page, shown side by side and then one
by one (the story is 223×396 px there, x 264 y 72; laid out ×4.84 on 1080×1920). Photos in shapes: a U that falls
from the top, ovals that rise or open from a line, a veiled photo with a clear arch window, an arch that rises; thin
white outlines that draw themselves, serif titles with small caps, a round camera icon. Moves copied from 10 fps
sheets (frames at 29.97 fps from each story's start). The brand word of the title («Instagram») is the neutral
«Fashion», the address «www.yoursite.com»; the round camera icon stays as a small social icon. Photos are slots
(our samples). Kit de Instagram; ids `ig10-*`, order 16300-. Notes in tienda/plantillas/estudio-59320997/NOTAS.md.

Each story plays its entrance, holds, and leaves with its entrance backwards at 2.5× speed (S.frame).
"""

from __future__ import annotations

import math

import templates_llt_f as f6
from kit import tall
from scene import keys
from templates_ig9 import Story, dur_for, finish, ko, table
from templates_tit_c import k
from templates_tit_e import solid
from templates_tit_h import poly, ring, rot_pt
from templates_yp4 import art_except

W, H = 1080, 1920
WHITE, PINK, CAM, GREYTX = "#FFFFFF", "#EEE3E1", "#2A2626", "#4D4747"
SERIF = "Crimson Text"
for _w, _f in ((400, "Regular"), (600, "SemiBold"), (700, "Bold")):
    f6._FILES[(SERIF, _w)] = f"fonts.extra/fonts/crimsontext/CrimsonText-{_f}.ttf"
URB = "Urbanist"
WEB = "www.yoursite.com"
TITLE = "Fashion"


def _p(id, es, en, order, dur, tags=(), thumb=None):
    return tall(f"ig10-{id}", es, en, "instagram", dur, order=order,
                tags=["instagram", "historia", "reels", "moda", "modelos"] + list(tags),
                thumb_at=thumb if thumb is not None else round(dur * 0.55, 1))


def small_caps(clip, word="MODELS", scale=0.8):
    """MODELS with its inner letters a size smaller (the reference's small capitals)."""
    clip["textStyle"]["runs"] = [{"start": 1, "end": len(word) - 1, "sizeEnabled": True, "sizeScale": scale}]
    return clip


def stadium(s, name, layers, rect, base=None):
    """A pill (round ends on the short side) covering rect(fr) = (cx, cy, w, h, rot, op); its corner radius is set
    at its full size, so it turns into an ellipse when squashed."""
    bw, bh = base
    return s.obj(name, layers, rect, kind="rounded-rectangle", radius=min(bw, bh) / 2, base=base)


def trim(clip, s, fn, offset=0.0):
    """Draw a shape's outline: fn(fr) = percent of it shown (from trimOffset degrees round)."""
    st = clip["shapeStyle"]
    st["trimStart"], st["trimEnd"], st["trimOffset"] = 0.0, 100.0, offset
    st.setdefault("keyframes", {})["trimEnd"] = keys([(u, round(max(0.0, min(100.0, fn(fr))), 3), "linear")
                                                      for u, fr in s.each()])
    return clip


def camera(s, name, geom, disc, ink):
    """The round camera icon: a disc with a rounded square, a lens ring and a dot. geom(fr) = (cx, cy, d, rot, op)."""
    s.obj(f"{name} (disco)", solid(disc), lambda fr, u: geom(fr)[:2] + (geom(fr)[2], geom(fr)[2]) + geom(fr)[3:],
          kind="ellipse", base=(300, 300))
    D = 270.0

    def part(rel, dx=0.0, dy=0.0):
        def g(fr, u):
            cx, cy, d, r, op = geom(fr)
            sc = d / D
            x, y = rot_pt(cx + dx * sc, cy + dy * sc, r, cx, cy)
            return x, y, rel * sc, rel * sc, r, op
        return g
    s.obj(f"{name} (marco)", ring(ink, 15), part(140), kind="rounded-rectangle", radius=40, base=(140, 140))
    s.obj(f"{name} (lente)", ring(ink, 15), part(64), kind="ellipse", base=(64, 64))
    s.obj(f"{name} (punto)", solid(ink), part(16, 37, -37), kind="ellipse", base=(16, 16))


def grow(at, n, d, spin=-140.0):
    """A disc that grows from nothing while turning."""
    return lambda fr: (d * ko(fr, at, n), spin * (1 - ko(fr, at, n + 4)), 1.0 if fr > at else 0.0)


def U_path(w, h):
    """A box w × h whose bottom is a half circle (flat top, round bottom), on the 100 box."""
    r = w / 2
    pts = [(0, 0), (100, 0), (100, 100 * (h - r) / h)]
    for i in range(1, 24):
        a = math.pi * i / 24
        pts.append((50 + 50 * math.cos(a), 100 * (h - r + r * math.sin(a)) / h))
    pts.append((0, 100 * (h - r) / h))
    return poly(pts)


def U_line(w, h, top, bottom_r):
    """An open U outline (sides from `top`, round bottom), on the 100 box of w × h."""
    r = bottom_r
    pts = [(100, 100 * top / h), (100, 100 * (h - r) / h)]
    for i in range(1, 24):
        a = math.pi * i / 24
        pts.append((50 + 50 * math.cos(a), 100 * (h - r + r * math.sin(a)) / h))
    pts.append((0, 100 * (h - r) / h))
    pts.append((0, 100 * top / h))
    return "M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y in pts)


def outline(colour, w):
    lay = ring(colour, w)
    return lay


# ==================================================================================================================
# 1. A photo with a round bottom falls from the top, the camera icon grows below it turning, the title rises, a frame
#    draws round it and a white U line draws inside the photo
def u_photo():
    D = dur_for(64)
    t = _p("u-foto", "Historia: foto con fondo redondo y título en marco", "Story: round-bottom photo and framed title",
           16300, D, ["foto", "marco"])
    s = Story(t, D)
    s.bg(PINK)
    drop = lambda fr: -1470 * (1 - ko(fr, 2, 22, 2.0))  # noqa: E731
    m = s.obj("Foto (forma)", solid(WHITE), lambda fr, u: (540, 735 + drop(fr), 1080, 1470, 0, 1.0),
              path=U_path(1080, 1470))
    s.pic("Foto", "ig3-sunglasses-03", (0, 0, W, 1480), geom=lambda fr, u: (0, 0, 1.15 - 0.15 * ko(fr, 0, 60)),
          matte_clip=m, label="Foto")
    line = s.obj("Línea", ring(WHITE, 6), lambda fr, u: (540, 1028, 1062, 710, 0, 1.0), path=U_line(1062, 710, 0, 531))
    trim(line, s, lambda fr: 100 * ko(fr, 37, 18, 1.6))
    s.line(TITLE, (250, 760, 830, 876), SERIF, 400, WHITE, "Título", reveal=lambda fr: (0, 0, W, 890),
           shift=lambda fr: (0.0, 130 * (1 - ko(fr, 24, 10))))
    small_caps(s.line("MODELS", (321, 925, 765, 1015), SERIF, 400, WHITE, "Título 2",
                      reveal=lambda fr: (0, 890, W, 1035), shift=lambda fr: (0.0, 130 * (1 - ko(fr, 28, 10)))))
    s.frame_lines("Marco", WHITE, lambda fr: (186, 711, 909, 1065), 6,
                  table([(33, 0), (44, 600), (52, 1776), (58, 2000), (64, 2154)]), start="tr")
    s.line(WEB, (300, 1112, 800, 1156), URB, 700, WHITE, "Web", op=lambda fr, u: k(fr, 48, 8))
    g = grow(8, 18, 273)
    camera(s, "Icono", lambda fr: (540, 1689) + g(fr), CAM, WHITE)
    return finish(t)


# 2. An oval photo rises from below with the title on it, the icon grows, the MODELS label opens and two thin
#    outlines draw round the oval
def oval_rise():
    D = dur_for(66)
    t = _p("ovalo-sube", "Historia: foto ovalada que sube con dos contornos",
           "Story: rising oval photo with two outlines", 16301, D, ["foto", "óvalo"])
    s = Story(t, D)
    s.bg(PINK)
    rise = table([(-3, 1900), (-1.5, 1764), (4.5, 1599), (10.5, 873), (16.5, 294), (22.5, 129), (34.5, 15), (43, 0)])
    m = stadium(s, "Foto (forma)", solid(WHITE), lambda fr, u: (540, 933 + rise(fr), 1068, 1704, 0, 1.0),
                base=(1068, 1704))
    s.pic("Foto", "portrait-02", (0, 0, W, H), geom=lambda fr, u: (0, rise(fr), 1.3 - 0.3 * ko(fr, 8, 55)),
          matte_clip=m, label="Foto")
    rings = [((24, 100, 1056, 1740), 31, 30), ((60, 136, 1020, 1704), 36, 30)]
    for i, ((x0, y0, x1, y1), at, n) in enumerate(rings):
        c = stadium(s, f"Contorno {i + 1}", ring(WHITE, 6),
                    lambda fr, u, x0=x0, y0=y0, x1=x1, y1=y1: ((x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, 0,
                                                               1.0), base=(x1 - x0, y1 - y0))
        trim(c, s, lambda fr, at=at, n=n: 100 * ko(fr, at, n, 1.5), offset=60.0)
    s.line(TITLE, (150, 1180, 930, 1290), SERIF, 400, WHITE, "Título", geom=lambda fr, u: (0, rise(fr), 1, 0, 1.0))
    s.line(WEB, (284, 1362, 799, 1410), URB, 700, WHITE, "Web", geom=lambda fr, u: (0, rise(fr), 1, 0, 1.0))
    # The MODELS label opens from its middle.
    half = lambda fr: 165 * ko(fr, 31, 13)  # noqa: E731
    s.bar("Etiqueta", WHITE, lambda fr, u: (549 - half(fr), 663, 549 + half(fr), 774),
          op=lambda fr, u: 1.0 if fr > 31 else 0.0)
    small_caps(s.line("MODELS", (402, 692, 696, 748), SERIF, 600, CAM, "Etiqueta (texto)",
                      reveal=lambda fr: (549 - half(fr), 663, 549 + half(fr), 774)))
    g = grow(19, 21, 225)
    camera(s, "Icono", lambda fr: (549, 960) + g(fr), WHITE, CAM)
    return finish(t)


# 3. A line opens into an oval photo, the icon pops at its foot and rises inside a thin pill that draws itself,
#    the title rises at the top, the address below
def oval_open():
    D = dur_for(80)
    t = _p("ovalo-abre", "Historia: foto ovalada que se abre desde una línea",
           "Story: oval photo opening from a line", 16302, D, ["foto", "óvalo"])
    s = Story(t, D)
    s.bg(PINK)
    hh = table([(0, 3), (10.5, 48), (19.5, 180), (28.5, 1215), (34.5, 1485), (40.5, 1632), (50, 1695)])
    ww = table([(0, 1080), (19.5, 1080), (28.5, 1041), (50, 1008)])
    m = stadium(s, "Foto (forma)", solid(WHITE), lambda fr, u: (540, 928, ww(fr), hh(fr), 0, 1.0),
                base=(1008, 1695))
    s.pic("Foto", "fx-woman-07", (0, 0, W, H), geom=lambda fr, u: (0, 0, 1.08 - 0.08 * ko(fr, 0, 80)), matte_clip=m,
          label="Foto")
    gy = table([(50, 1566), (52, 1530), (58, 1449), (64, 1176), (70, 1074), (79, 1029)])
    c = stadium(s, "Contorno", ring(WHITE, 5), lambda fr, u: (545, gy(fr) - 120, 429, 720, 0, 1.0 if fr > 44 else 0.0),
                base=(429, 720))
    trim(c, s, lambda fr: 100 * ko(fr, 44, 32, 1.5), offset=90.0)
    s.line(TITLE, (225, 372, 885, 478), SERIF, 400, WHITE, "Título", reveal=lambda fr: (0, 0, W, 492),
           shift=lambda fr: (0.0, 120 * (1 - ko(fr, 58, 10))))
    s.line(WEB, (330, 1290, 750, 1334), URB, 700, WHITE, "Web", op=lambda fr, u: k(fr, 72, 8))
    camera(s, "Icono", lambda fr: (545, gy(fr), 270 * ko(fr, 26, 8), 0.0, 1.0 if fr > 26 else 0.0), WHITE, CAM)
    return finish(t)


# 4. The photo under a pale veil, a clear arch window falls into place with its outline, the title lines scroll up
#    one after another and settle, the icon pops
def veil_window():
    D = dur_for(62)
    t = _p("ventana-arco", "Historia: foto velada con ventana de arco", "Story: veiled photo with an arch window",
           16303, D, ["foto", "arco", "velo"])
    s = Story(t, D)
    s.bg(PINK)
    first = s.pic("Foto de fondo", "shopping-03", op=lambda fr, u: k(fr, 0, 6), label="Foto")
    s.bar("Velo", PINK, lambda fr, u: (-10, -10, W + 10, H + 10), alpha=0.62, op=lambda fr, u: k(fr, 0, 6))
    cy = table([(8, -760), (10.5, -695), (16.5, -384), (22.5, 921), (28.5, 1488), (34.5, 1644), (40.5, 1660)])
    win = lambda fr, u: (540, cy(fr), 930, 1400, 0, 1.0 if fr > 8 else 0.0)  # noqa: E731
    m = stadium(s, "Ventana (forma)", solid(WHITE), win, base=(930, 1400))
    s.pic("Ventana", first["_sample"], matte_clip=m, reuse=first["placeholderId"])
    stadium(s, "Ventana (contorno)", ring(WHITE, 6), win, base=(930, 1400))
    lines = [(TITLE, (255, 262, 870, 342), [(18, 1700), (22.5, 1596), (28.5, 1110), (34.5, 210), (40.5, 45), (46.5, 0)],
              "Título"),
             ("MODELS", (255, 405, 900, 507), [(24, 1600), (28.5, 1419), (34.5, 429), (40.5, 144), (46.5, 39),
                                               (52.5, 9), (61.5, 0)], "Título 2"),
             (WEB, (395, 559, 757, 599), [(30, 1200), (34.5, 996), (40.5, 282), (46.5, 105), (52.5, 30), (61.5, 0)],
              "Web")]
    for text, ink, pts, name in lines:
        dy = table(pts)
        c = s.line(text, ink, URB if text == WEB else SERIF, 700 if text == WEB else 400, GREYTX, name,
                   geom=lambda fr, u, dy=dy, f0=pts[0][0]: (0, dy(fr), 1, 0, 1.0 if fr > f0 else 0.0))
        if text == "MODELS":
            small_caps(c)
    g = grow(22, 12, 270)
    camera(s, "Icono", lambda fr: (585, 1683) + g(fr), WHITE, CAM)
    return art_except(t, keep=("Fondo", "Foto de fondo", "Velo"))


# 5. An arch photo rises with a grey and a white outline, MODELS and the address scroll up and settle, two lines,
#    the icon grows
def arch_rise():
    D = dur_for(90)
    t = _p("arco-sube", "Historia: foto en arco que sube con MODELS", "Story: rising arch photo with MODELS", 16304,
           D, ["foto", "arco"])
    s = Story(t, D)
    s.bg(PINK)
    top = table([(0, 1990), (1.5, 1905), (7.5, 1854), (13.5, 1716), (19.5, 1095), (25.5, 600), (31.5, 465),
                 (37.5, 399), (43.5, 369), (49.5, 360)])
    ah = 3200
    m = stadium(s, "Foto (forma)", solid(WHITE), lambda fr, u: (540, top(fr) + ah / 2, 1080, ah, 0, 1.0),
                base=(1080, ah))
    s.pic("Foto", "portrait-01", (0, 0, W, H), geom=lambda fr, u: (0, 0, 1.12 - 0.12 * ko(fr, 10, 60)), matte_clip=m,
          label="Foto")
    stadium(s, "Contorno", ring("#9E9897", 5), lambda fr, u: (540, top(fr) - 54 + (ah + 108) / 2, 1110, ah + 108, 0,
                                                             1.0), base=(1110, ah + 108))
    stadium(s, "Contorno 2", ring(WHITE, 5), lambda fr, u: (545, top(fr) + 90 + (ah - 180) / 2, 981, ah - 180, 0,
                                                           1.0), base=(981, ah - 180))
    md = table([(19.5, 950), (25.5, 884), (31.5, 803), (37.5, 422), (43.5, 167), (49.5, 68), (58.5, 23), (70.5, 8),
                (85, 0)])
    small_caps(s.line("MODELS", (201, 948, 915, 1077), SERIF, 400, WHITE, "Título",
                      geom=lambda fr, u: (0, md(fr), 1, 0, 1.0)))
    wd = table([(30, 1000), (37.5, 771), (43.5, 471), (49.5, 210), (58.5, 81), (70.5, 15), (85, 0)])
    s.line(WEB, (306, 1128, 780, 1170), URB, 700, WHITE, "Web", geom=lambda fr, u: (0, wd(fr), 1, 0, 1.0))
    s.bar("Línea", WHITE, lambda fr, u: (410, 1245 + wd(fr), 710, 1251 + wd(fr)))
    s.bar("Línea 2", WHITE, lambda fr, u: (485, 1293 + wd(fr), 635, 1299 + wd(fr)))
    g = grow(43, 17, 270)
    camera(s, "Icono", lambda fr: (549, 1695) + g(fr), WHITE, CAM)
    return finish(t)


TEMPLATES = [u_photo, oval_rise, oval_open, veil_window, arch_rise]
