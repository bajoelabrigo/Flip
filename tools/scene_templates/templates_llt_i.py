"""Gold lower thirds, ninth set (2026-11-07): the nine of 49618170.mp4 (1920×1080 at 30 fps), Kanit (italic and
upright, heavy names, light roles) with gold accents (#FF9E00, gold squares fading from dark). One family: the name
types in letter by letter (forwards, or from its end), the role the same a little later, and gold squares, tags,
boxes and lines grow with them; each leaves with its entrance played backwards. Laid out where the reference has
them over video, with no background. Order 8640-8648.
"""

from __future__ import annotations

import templates_llt_f as f6
from kit import wide
from scene import fill, gradient, no_stroke, tanim
from templates_llt_f import Piece, table

for w, file in ((400, "Kanit-Regular"), (500, "Kanit-Medium"), (600, "Kanit-SemiBold"), (700, "Kanit-Bold"),
                (800, "Kanit-ExtraBold"), (900, "Kanit-Black")):
    f6._FILES[("Kanit", w)] = f"fonts.extra/fonts/kanit/{file}.ttf"
FONT = "Kanit"
GOLD = "#FF9E00"
WHITE = "#FFFFFF"
INK = "#111111"
FPS = 30.0
FADE_GOLD = [gradient([(0.0, "#2E2000"), (1.0, "#FFA400")], angle=0), no_stroke()]
GROW = table({0: 0.0, 2: 0.18, 4: 0.42, 6: 0.63, 8: 0.79, 10: 0.89, 12: 0.95, 14: 0.98, 16: 1.0})


class GoldPiece(Piece):
    def __init__(self, t, dur):
        super().__init__(t, dur, 0)

    def frame(self, u):
        return min(u, self.dur - u) * FPS


def _kit(id, es, en, dur, order, tags, **kw):
    return wide(f"llt9-{id}", es, en, "ytkit", dur, order=order, tags=["kit:lowerthirds", "tercio", "dorado"] + tags,
                **kw)


def typed(p, content, edge, caps, width, weight, italic, colour, name, start, backward=False, stagger=0.08,
          align="left"):
    """A line whose letters pop in one by one from frame `start` (from its end with backward)."""
    clip = p.text(content, edge, caps[0], caps[1], width, FONT, weight, colour, name, align=align, case="none")
    if italic:
        clip["textStyle"]["italic"] = True
    wait = round(start / FPS, 2)
    order = "backward" if backward else "forward"
    out_order = "forward" if backward else "backward"
    clip["textStyle"]["animation"] = {
        "in": tanim("pop", duration=0.27, unit="character", stagger=stagger, ease="back", delay=wait, order=order,
                    **{"from": 0}),
        "out": tanim("pop", duration=0.27, unit="character", stagger=stagger, ease="easeIn", delay=wait,
                     order=out_order, **{"from": 0})}
    return clip


def shape(p, name, rect, grows, start, layers=None, colour=GOLD, kind="rectangle", radius=0, hdelay=8):
    """A shape on `rect` growing from frame `start`: ltr, rtl, ttb, btt, out (from its middle), pop, or vline (a
    thin upright line first, then out to the right)."""
    x0, y0, x1, y1 = rect

    def r(fr):
        k = GROW(fr - start)
        if grows == "ltr":
            return (x0, y0, x0 + (x1 - x0) * k, y1)
        if grows == "rtl":
            return (x1 - (x1 - x0) * k, y0, x1, y1)
        if grows == "ttb":
            return (x0, y0, x1, y0 + (y1 - y0) * k)
        if grows == "btt":
            return (x0, y1 - (y1 - y0) * k, x1, y1)
        if grows == "out":
            cx = (x0 + x1) / 2
            return (cx - (cx - x0) * k, y0, cx + (x1 - cx) * k, y1)
        if grows == "vline":
            kv, kh = GROW(fr - start), GROW(fr - start - hdelay)
            cy = (y0 + y1) / 2
            return (x0, cy - (cy - y0) * kv, x0 + 6 + (x1 - x0 - 6) * kh, cy + (y1 - cy) * kv)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        return (cx - (cx - x0) * k, cy - (cy - y0) * k, cx + (x1 - cx) * k, cy + (y1 - cy) * k)
    clip = p.shape(name, colour, rect, r)
    if layers:
        clip["shapeStyle"]["layers"] = layers
    if kind != "rectangle" or radius:
        clip["shapeStyle"]["kind"] = kind
        clip["shapeStyle"]["cornerRadius"] = radius
    return clip


def piece(id, es, en, order, D, tags=()):
    t = _kit(id, es, en, D, order, list(tags), thumb_at=round(D / 2, 1))
    return t, GoldPiece(t, D)


def vanja_light():
    t, p = piece("vanja", "Tercio dorado: cursiva fina con cuadros", "Gold lower third: light italic, squares", 8640,
                 6.2, ["cursiva"])
    shape(p, "Cuadro", (196, 864, 274, 942), "pop", 24, layers=FADE_GOLD)
    shape(p, "Cuadro 2", (1088, 774, 1162, 850), "pop", 13, layers=FADE_GOLD)
    typed(p, "Vanja Aleksov", 300, (862, 946), 784, 400, True, WHITE, "Nombre", 1)
    typed(p, "Motion Designer", 530, (821, 847), 286, 600, True, WHITE, "Cargo", 20)
    return t


def vanja_bold():
    t, p = piece("vanja-negrita", "Tercio dorado: cursiva gruesa con cuadros", "Gold lower third: heavy italic, squares",
                 8641, 5.9, ["cursiva"])
    shape(p, "Cuadro", (205, 832, 270, 900), "pop", 0, layers=FADE_GOLD)
    shape(p, "Cuadro 2", (222, 868, 290, 942), "pop", 3, layers=FADE_GOLD)
    typed(p, "Vanja Aleksov", 325, (864, 946), 851, 800, True, WHITE, "Nombre", 1)
    typed(p, "IT specialist", 325, (826, 848), 184, 400, True, WHITE, "Cargo", 13)
    return t


def victoria():
    t, p = piece("victoria", "Tercio dorado: barra y cursiva gruesa", "Gold lower third: bar, heavy italic", 8642, 5.9,
                 ["cursiva"])
    shape(p, "Barra", (197, 880, 232, 957), "btt", 0, layers=FADE_GOLD)
    typed(p, "Victoria Sydorenko", 231, (884, 955), 936, 800, True, WHITE, "Nombre", 1, stagger=0.07)
    typed(p, "Architect", 256, (846, 866), 134, 400, True, WHITE, "Cargo", 21)
    return t


def natalie():
    t, p = piece("natalie", "Tercio dorado: línea con punto", "Gold lower third: line with a dot", 8643, 7.2)
    shape(p, "Línea", (171, 840, 176, 962), "btt", 0)
    shape(p, "Punto", (166, 958, 181, 973), "pop", 10, colour=WHITE, kind="ellipse")
    typed(p, "Natalie Johnson", 207, (836, 912), 946, 900, False, WHITE, "Nombre", 22, stagger=0.06)
    typed(p, "Math Teacher", 207, (943, 961), 214, 500, False, WHITE, "Cargo", 26)
    return t


def yaroslava():
    t, p = piece("yaroslava", "Tercio dorado: cuadro con cargo a la derecha", "Gold lower third: box with role, right",
                 8644, 5.6, ["cursiva", "derecha"])
    shape(p, "Cuadro", (1491, 801, 1725, 966), "rtl", 0, layers=FADE_GOLD)
    typed(p, "Yaroslava Sokolova", 1709, (870, 934), 892, 800, True, WHITE, "Nombre", 1, backward=True, stagger=0.07,
          align="right")
    typed(p, "Interior Designer", 1708, (843, 864), 245, 700, True, WHITE, "Cargo", 17, backward=True, align="right")
    return t


def max_jacobs():
    t, p = piece("max", "Tercio dorado: nombre en caja y cargo en ficha", "Gold lower third: name in a box, role tag",
                 8645, 6.6, ["cursiva", "caja"])
    shape(p, "Caja", (194, 784, 920, 890), "vline", 0, layers=FADE_GOLD)
    shape(p, "Ficha", (194, 900, 920, 946), "vline", 4, colour=WHITE, radius=4)
    typed(p, "Max Jacobs", 210, (810, 876), 700, 900, True, WHITE, "Nombre", 13)
    typed(p, "Graphic Designer", 366, (906, 940), 384, 500, True, INK, "Cargo", 17)
    return t


def emily():
    t, p = piece("emily", "Tercio dorado: nombre en caja blanca y etiqueta", "Gold lower third: name in a white box, tag",
                 8646, 6.9, ["caja"])
    shape(p, "Caja", (230, 844, 974, 966), "vline", 0, colour=WHITE, hdelay=17)
    shape(p, "Etiqueta", (200, 824, 510, 860), "ltr", 10)
    typed(p, "Emily Johnson", 256, (870, 944), 694, 900, False, INK, "Nombre", 17)
    typed(p, "Marketing Manager", 236, (834, 851), 238, 700, True, WHITE, "Cargo", 14)
    return t


def katherine():
    t, p = piece("katherine", "Tercio dorado: etiqueta y punto a la derecha", "Gold lower third: tag and dot, right",
                 8647, 6.4, ["cursiva", "derecha"])
    typed(p, "Katherine Roberts", 1649, (822, 890), 1100, 800, True, WHITE, "Nombre", 1, backward=True, stagger=0.07,
          align="right")
    shape(p, "Etiqueta", (1234, 918, 1662, 965), "rtl", 22)
    shape(p, "Punto", (1674, 927, 1712, 965), "pop", 26, kind="ellipse")
    typed(p, "GRAPHIC DESIGNER", 1645, (928, 955), 400, 700, True, WHITE, "Cargo", 26, backward=True, align="right")
    return t


def benjamin():
    t, p = piece("benjamin", "Tercio dorado: etiqueta arriba y línea", "Gold lower third: tag above, line", 8648, 6.5)
    shape(p, "Línea", (92, 920, 1241, 924), "out", 26)
    shape(p, "Etiqueta", (472, 832, 836, 878), "vline", 7)
    typed(p, "Aerospace Engineer", 1124, (880, 944), 934, 900, False, WHITE, "Cargo", 17, backward=True, stagger=0.06,
          align="right")
    typed(p, "Benjamin Harris", 480, (842, 868), 346, 700, False, WHITE, "Nombre", 20)
    return t


TEMPLATES = [vanja_light, vanja_bold, victoria, natalie, yaroslava, max_jacobs, emily, katherine, benjamin]
