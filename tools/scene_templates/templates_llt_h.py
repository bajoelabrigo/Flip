"""Orange caret lower thirds, eighth set (2026-11-07): the fifteen of 1246018.mp4 (1280×720 at 30 fps, measured
scaled to 1080p). One family: an orange caret runs over the name from its end to its start uncovering it while the
name drifts a little to the right, a smaller caret runs over the role, and orange bars, brackets and lines grow
with them. The caret curve is the one measured on «Brandon Blake» (frames from the piece's first one); each piece
has its own measured layout and leaves with its entrance played backwards. Bebas Neue (names) and Oswald Light
(roles), orange #FD8900. Laid out where the reference has them, no background. Order 8620-8634.
"""

from __future__ import annotations

import templates_llt_f as f6
from kit import wide
from templates_llt_f import Piece, table

f6._FILES[("Bebas Neue", 400)] = "fonts.basic/fonts/bebasneue/BebasNeue-Regular.ttf"
f6._FILES[("Oswald", 300)] = "fonts.basic/fonts/oswald/Oswald-Light.ttf"
NAME_FONT, ROLE_FONT = "Bebas Neue", "Oswald"
ORANGE = "#FD8900"
WHITE = "#FFFFFF"
FPS = 30.0

# Measured on Brandon Blake: how far the caret has gone (0 at its start, 1 at its end) and how far the name still
# has to drift (1 = all of it, 0.216 of the name's width).
CARET = table({-3: 0.0, 0: 0.06, 1: 0.14, 2: 0.2, 3: 0.27, 4: 0.33, 6: 0.42, 7: 0.47, 8: 0.52, 9: 0.57, 10: 0.61,
               11: 0.64, 12: 0.68, 13: 0.71, 14: 0.74, 15: 0.77, 16: 0.8, 17: 0.82, 18: 0.84, 19: 0.86, 20: 0.88,
               21: 0.9, 22: 0.91, 23: 0.93, 24: 0.94, 25: 0.95, 26: 0.96, 27: 0.97, 28: 0.98, 29: 0.99, 31: 0.995,
               33: 1.0})
DRIFT = table({-3: 1.0, 0: 1.0, 2: 0.845, 4: 0.713, 6: 0.597, 8: 0.496, 10: 0.411, 12: 0.341, 14: 0.279, 16: 0.217,
               18: 0.171, 20: 0.132, 22: 0.101, 24: 0.07, 26: 0.047, 28: 0.031, 30: 0.016, 32: 0.008, 38: 0.0})


class CaretPiece(Piece):
    def __init__(self, t, dur):
        super().__init__(t, dur, 0)

    def frame(self, u):
        return min(u, self.dur - u) * FPS - 3


def _kit(id, es, en, dur, order, tags, **kw):
    return wide(f"llt8-{id}", es, en, "ytkit", dur, order=order, tags=["kit:lowerthirds", "tercio", "naranja"] + tags,
                **kw)


def build(id, es, en, order, D, name, roles=(), bars=(), caret_stays=None, tags=(), from_right=False):
    """name = (content, x0, y0, x1, y1): the name's ink box; roles = [(content, x0, y0, x1, y1, way, delay)], way
    "ltr" (uncovered from its start, caret at its end) or "rtl"; bars = [(x0, y0, x1, y1, grows, delay)], grows
    "ltr", "rtl", "ttb", "btt", "out" (from the middle) or "pop"; caret_stays = the caret's last x when it stays as a
    bar left of the name (its width 11), else it fades out at the end of its run."""
    t = _kit(id, es, en, D, order, list(tags), thumb_at=round(D / 2, 1))
    p = CaretPiece(t, D)
    content, nx0, ny0, nx1, ny1 = name
    width = nx1 - nx0
    drift_px = 0.216 * width
    start_x = nx1 + (drift_px if from_right else -drift_px)
    end_x = caret_stays if caret_stays is not None else nx0 - 14
    caret_x = lambda fr: start_x + (end_x - start_x) * CARET(fr)  # noqa: E731
    # The name drifts into place from the left while the caret uncovers it (from the right for Richard Madden).
    shift = lambda fr: (drift_px if from_right else -drift_px) * DRIFT(fr)  # noqa: E731
    p.text(content, nx0, ny0, ny1, width, NAME_FONT, 400, WHITE, "Nombre", spacing_em=0.01, shift=shift,
           reveal=lambda fr: (caret_x(fr) + 11, ny0 - 10, 1920, ny1 + 10) if fr > -3 else (0, 0, 0, 0))
    ch = (ny1 - ny0) + 10

    def caret(fr):
        if fr <= -3:
            return (start_x, ny0 - 5, start_x, ny1 + 5)
        if caret_stays is None and fr > 30:
            k = max(0.0, 1 - (fr - 30) / 6)
            return (caret_x(fr), (ny0 + ny1) / 2 - ch / 2 * k, caret_x(fr) + 11, (ny0 + ny1) / 2 + ch / 2 * k)
        return (caret_x(fr), ny0 - 5, caret_x(fr) + 11, ny1 + 5)
    p.shape("Cursor", ORANGE, (end_x, ny0 - 5, end_x + 11, ny1 + 5), caret)
    for i, (rc, x0, y0, x1, y1, way, delay) in enumerate(roles):
        k = lambda fr, d=delay: CARET(fr - d)  # noqa: E731
        label = "Cargo" if i == 0 else f"Cargo {i + 1}"
        if way == "ltr":
            reveal = lambda fr, x0=x0, x1=x1, y0=y0, y1=y1, k=k: (x0 - 4, y0 - 6, x0 + (x1 + 4 - x0) * k(fr), y1 + 6)
        else:
            reveal = lambda fr, x0=x0, x1=x1, y0=y0, y1=y1, k=k: (x1 + 4 - (x1 + 4 - x0) * k(fr), y0 - 6, 1920, y1 + 6)
        p.text(rc, x0, y0, y1, x1 - x0, ROLE_FONT, 300, WHITE, label, spacing_em=0.06, reveal=reveal)
    for j, (x0, y0, x1, y1, grows, delay) in enumerate(bars):
        k = lambda fr, d=delay: CARET(fr - d)  # noqa: E731

        def rect(fr, x0=x0, y0=y0, x1=x1, y1=y1, grows=grows, k=k):
            v = k(fr)
            if grows == "ltr":
                return (x0, y0, x0 + (x1 - x0) * v, y1)
            if grows == "rtl":
                return (x1 - (x1 - x0) * v, y0, x1, y1)
            if grows == "ttb":
                return (x0, y0, x1, y0 + (y1 - y0) * v)
            if grows == "btt":
                return (x0, y1 - (y1 - y0) * v, x1, y1)
            if grows == "out":
                cx = (x0 + x1) / 2
                return (cx - (cx - x0) * v, y0, cx + (x1 - cx) * v, y1)
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            return (cx - (cx - x0) * v, cy - (cy - y0) * v, cx + (x1 - cx) * v, cy + (y1 - cy) * v)
        p.shape(f"Adorno {j + 1}", ORANGE, (x0, y0, x1, y1), rect)
    return t


def cameron():
    return build("cameron", "Tercio naranja: cargo arriba con marcas", "Orange lower third: role above, marks", 8620,
                 6.3, ("Cameron Banks", 353, 860, 915, 932), caret_stays=313,
                 roles=[("Production designer", 500, 813, 848, 840, "ltr", 6)],
                 bars=[(862, 807, 872, 843, "pop", 12), (313, 891, 326, 900, "pop", 4), (313, 918, 326, 927, "pop", 6),
                       (862, 949, 872, 960, "pop", 8)])


def brandon():
    return build("brandon", "Tercio naranja: barra y nombre", "Orange lower third: bar and name", 8621, 7.0,
                 ("Brandon Blake", 419, 818, 1014, 891), caret_stays=388,
                 roles=[("Motion designer", 333, 915, 621, 945, "ltr", 4)],
                 bars=[(635, 912, 646, 946, "pop", 20), (388, 959, 399, 972, "pop", 14)])


def ryan():
    return build("ryan", "Tercio naranja: línea y cargo arriba", "Orange lower third: line and role above", 8622, 7.1,
                 ("Ryan Gallagher", 352, 857, 997, 931),
                 roles=[("Creative director", 563, 804, 873, 832, "ltr", 12)],
                 bars=[(410, 822, 546, 839, "ltr", 8), (408, 952, 424, 968, "pop", 16)])


def richard_madden():
    return build("madden", "Tercio naranja: líneas a los lados del cargo", "Orange lower third: lines beside the role",
                 8623, 8.0, ("Richard Madden", 382, 838, 1011, 911), from_right=True,
                 roles=[("Any length of text", 528, 931, 862, 959, "rtl", 4)],
                 bars=[(372, 941, 511, 950, "rtl", 0), (878, 941, 1011, 950, "ltr", 0)])


def rason():
    return build("rason", "Tercio naranja: barra y cargo arriba", "Orange lower third: bar, role above", 8624, 6.5,
                 ("Rason Hickman", 393, 876, 976, 950), caret_stays=360,
                 roles=[("Creative director", 629, 824, 939, 852, "rtl", 8)])


def john():
    return build("john", "Tercio naranja: corchete", "Orange lower third: bracket", 8625, 6.6,
                 ("John Bishop", 421, 811, 859, 884),
                 roles=[("Casting director", 455, 905, 757, 935, "rtl", 6)],
                 bars=[(393, 759, 510, 769, "rtl", 0), (393, 759, 403, 972, "ttb", 6), (393, 962, 450, 972, "ltr", 14),
                       (500, 781, 508, 790, "pop", 16)])


def castro():
    return build("castro", "Tercio naranja: cargo en dos líneas", "Orange lower third: two-line role", 8626, 6.2,
                 ("Michael Castro", 343, 812, 925, 884),
                 roles=[("Designer", 472, 909, 616, 937, "ltr", 6), ("Any length of text", 472, 954, 806, 982, "ltr", 10)],
                 bars=[(444, 786, 454, 800, "pop", 16), (444, 900, 454, 989, "ttb", 4), (631, 902, 639, 942, "pop", 18)])


def jake():
    return build("jake", "Tercio naranja: líneas largas a los lados", "Orange lower third: long lines either side",
                 8627, 7.8, ("Jake Griffith", 419, 871, 900, 943),
                 roles=[("Any length of text", 638, 821, 985, 850, "ltr", 10)],
                 bars=[(0, 925, 402, 934, "rtl", 0), (934, 925, 1915, 934, "ltr", 0), (616, 819, 622, 852, "pop", 14)])


def hayden():
    return build("hayden", "Tercio naranja: barra alta y cargo", "Orange lower third: tall bar and role", 8628, 6.8,
                 ("Hayden Dawson", 416, 842, 1000, 917), caret_stays=390,
                 roles=[("Casting director", 442, 944, 744, 973, "ltr", 6)],
                 bars=[(390, 804, 402, 976, "ttb", 0), (418, 806, 426, 821, "pop", 14), (418, 942, 426, 975, "pop", 10)])


def daniel():
    return build("daniel", "Tercio naranja: bloque junto al cargo", "Orange lower third: block beside the role", 8629,
                 6.6, ("Daniel Greene", 398, 814, 921, 886), caret_stays=365,
                 roles=[("Costume designer", 364, 906, 665, 934, "ltr", 8)],
                 bars=[(683, 901, 923, 940, "rtl", 2), (365, 946, 376, 957, "pop", 14)])


def charley():
    return build("charley", "Tercio naranja: barra que baja", "Orange lower third: bar running down", 8630, 6.8,
                 ("Charley Carney", 431, 817, 1031, 890), caret_stays=396,
                 roles=[("Photographer", 389, 915, 640, 944, "ltr", 8)],
                 bars=[(396, 960, 408, 1080, "ttb", 6)])


def michael_barrett():
    return build("barrett", "Tercio naranja: subrayado largo", "Orange lower third: long underline", 8631, 6.5,
                 ("Michael Barrett", 382, 862, 993, 934),
                 roles=[("Creative producer", 382, 814, 703, 842, "ltr", 10)],
                 bars=[(379, 951, 1010, 959, "ltr", 0)])


def james():
    return build("james", "Tercio naranja: bloque antes del cargo", "Orange lower third: block before the role", 8632,
                 8.0, ("James Friedman", 387, 819, 978, 892),
                 roles=[("Producer, casting director", 543, 910, 1005, 938, "ltr", 8)],
                 bars=[(382, 906, 526, 941, "ltr", 0)])


def mason():
    return build("mason", "Tercio naranja: línea larga y cargo a la derecha",
                 "Orange lower third: long line, role on the right", 8633, 7.9, ("Mason Williams", 336, 809, 987, 883),
                 roles=[("Production designer", 1181, 924, 1529, 952, "ltr", 10)],
                 bars=[(330, 899, 1528, 909, "ltr", 0)])


def richard_dodson():
    return build("dodson", "Tercio naranja: línea y cargo a la derecha", "Orange lower third: line, role on the right",
                 8634, 7.6, ("Richard Dodson", 405, 841, 1016, 915),
                 roles=[("Casting director", 718, 932, 1014, 961, "rtl", 6)],
                 bars=[(404, 944, 685, 953, "ltr", 2)])


TEMPLATES = [cameron, brandon, ryan, richard_madden, rason, john, castro, jake, hayden, daniel, charley,
             michael_barrett, james, mason, richard_dodson]
