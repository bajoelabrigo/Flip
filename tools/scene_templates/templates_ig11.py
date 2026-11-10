"""INSTAGRAM folder video 59444568.mp4 as Stock templates (ig11-*). See docs/plan-instagram.md.

Instagram-style call-to-action widgets that pop up over footage (1920×1080, 60 fps, 73 s): a profile card with
counters and Follow / Message buttons, a post card that opens from a line, name pills that grow out of a round
picture, a picture with a story ring and Follow, «Comment below if you agree», a comment card with Reply, «Tag
Someone» with an @ that draws itself, «Add Your Story», «Click Our Bio Link», «Watch Our Latest Reels», «Tap to See
Story», «Give Double Tap!», «Find Your Inspiration» and «Share Post to More». Each one studied on 10 fps sheets and
laid out where it sits in the reference; most pop up as a dot in the centre, hold, then slide aside while a panel
grows out from behind them and the words type in; all fade out together. Overlays: no background of their own (the
footage is not copied); pictures are round photo slots, names are ordinary editable text, the Instagram glyphs are
our own small line icons. Times are the reference's seconds (each piece starts at its own `o`). Kit de Instagram;
order 16400-. Study notes in tienda/plantillas/estudio-59444568/NOTAS.md.
"""

from __future__ import annotations

import math

import templates_llt_f as f6
from kit import Box, wide
from llt_motion import frames_of
from scene import gradient, keys, no_stroke, tanim, us
from templates_lg0 import sh
from templates_tit_e import solid
from templates_yp0 import E, L, W

P_ = "Poppins"
for _w, _f in ((400, "Regular"), (500, "Medium"), (600, "SemiBold"), (700, "Bold")):
    f6._FILES[(P_, _w)] = f"fonts.basic/fonts/poppins/Poppins-{_f}.ttf"

WHITE = "#FFFFFF"
INK = "#151515"
LILAC = "#C18FFB"
RED = "#EB271A"
DARK = "#131112"
GREY = "#A3A3A3"
RING = [gradient([(0.0, "#E83A3C"), (1.0, "#CF72C4")], angle=90), no_stroke()]
HOLLOW = {"id": "fill", "kind": "fill", "enabled": False, "paint": {"kind": "solid", "color": "#00000000"}}


def line(colour, width):
    return {"id": "stroke", "kind": "stroke", "enabled": True, "width": width, "strokeAlign": "center",
            "opacity": 1.0, "cap": "round", "join": "round",
            "paint": {"kind": "solid", "color": "#ff" + colour.lstrip("#").lower()}}


def outline(colour, width):
    return [HOLLOW, line(colour, width)]


# --- small helpers ---------------------------------------------------------------------------------------------
def eo(v, a, d, p=3.0):
    """Ease-out 0 → 1 from second a over d."""
    return 1 - (1 - L(v, a, d)) ** p


def tab(points):
    """[(second, value), …] → f(v), linear between the measured samples, held outside."""
    def f(v):
        if v <= points[0][0]:
            return points[0][1]
        for (a, va), (b, vb) in zip(points, points[1:]):
            if v <= b:
                return va + (vb - va) * (v - a) / (b - a)
        return points[-1][1]
    return f


def circ(cx, cy, r):
    c = 0.5523 * r
    return (f"M {cx + r:.2f} {cy:.2f} C {cx + r:.2f} {cy + c:.2f} {cx + c:.2f} {cy + r:.2f} {cx:.2f} {cy + r:.2f} "
            f"C {cx - c:.2f} {cy + r:.2f} {cx - r:.2f} {cy + c:.2f} {cx - r:.2f} {cy:.2f} "
            f"C {cx - r:.2f} {cy - c:.2f} {cx - c:.2f} {cy - r:.2f} {cx:.2f} {cy - r:.2f} "
            f"C {cx + c:.2f} {cy - r:.2f} {cx + r:.2f} {cy - c:.2f} {cx + r:.2f} {cy:.2f} Z")


def rrect(x0, y0, x1, y1, r):
    c = 0.4477 * r
    return (f"M {x0 + r} {y0} L {x1 - r} {y0} C {x1 - c} {y0} {x1} {y0 + c} {x1} {y0 + r} L {x1} {y1 - r} "
            f"C {x1} {y1 - c} {x1 - c} {y1} {x1 - r} {y1} L {x0 + r} {y1} C {x0 + c} {y1} {x0} {y1 - c} {x0} {y1 - r} "
            f"L {x0} {y0 + r} C {x0} {y0 + c} {x0 + c} {y0} {x0 + r} {y0} Z")


def _pts(points, close=False):
    s = "M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y in points)
    return s + (" Z" if close else "")


def _arc_pts(cx, cy, r, a0, a1, n=24):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def _capsule(cx, cy, ln, wd, ang):
    r = wd / 2
    half = ln / 2 - r
    pts = _arc_pts(half, 0, r, -90, 90, 10) + _arc_pts(-half, 0, r, 90, 270, 10)
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    return [(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in pts]


# Glyphs on a 0..100 box (our own line drawings of the usual social icons).
IG = rrect(5, 5, 95, 95, 27) + " " + circ(50, 50, 21) + " " + circ(74.5, 25.5, 2.5)
REELS = (rrect(5, 5, 95, 95, 24) + " M 5 31 L 95 31 M 33 6 L 45 30 M 58 6 L 70 30 "
         + _pts([(40, 47), (40, 79), (68, 63)], close=True))
SEARCH = circ(42, 42, 31) + " M 65 65 L 94 94"
HEART = ("M 50 92 C 22 72 3 54 3 31 C 3 15 15 4 29 4 C 38 4 45 9 50 17 C 55 9 62 4 71 4 C 85 4 97 15 97 31 "
         "C 97 54 78 72 50 92 Z")
BUBBLE = ("M 50 8 C 75 8 95 25 95 46 C 95 67 75 84 50 84 C 43 84 36 83 30 80 L 7 90 L 14 69 "
          "C 8 62 5 54 5 46 C 5 25 25 8 50 8 Z")
PLANE = "M 95 6 L 5 39 L 41 55 L 60 94 Z M 95 6 L 41 55"
BOOKMARK = "M 14 4 L 86 4 L 86 96 L 50 70 L 14 96 Z"
CHEV_R = "M 22 4 L 76 50 L 22 96"
CHEV_D = "M 4 22 L 50 76 L 96 22"
ADD_PERSON = (circ(36, 29, 18) + " M 4 94 C 4 70 18 57 36 57 C 54 57 68 70 68 94 M 85 26 L 85 56 M 70 41 L 100 41")
PEOPLE = (circ(30, 28, 17) + " M 3 94 C 3 72 14 60 30 60 C 46 60 57 72 57 94 " + circ(72, 30, 14)
          + " M 68 60 C 86 60 97 72 97 94")
LINK = _pts(_capsule(35, 65, 58, 28, -45), close=True) + " " + _pts(_capsule(65, 35, 58, 28, -45), close=True)
PLUS = "M 50 18 L 50 82 M 18 50 L 82 50"
CHECK = "M 27 52 L 43 68 L 74 35"
SCALLOP = _pts([(50 + (50 if i % 2 == 0 else 43) * math.cos(math.radians(i * 15 - 90)),
                 50 + (50 if i % 2 == 0 else 43) * math.sin(math.radians(i * 15 - 90))) for i in range(24)], True)
# The @ drawn the way the reference strokes it: from the bottom of the outer ring round clockwise, down the hook,
# round the inner ring and up the stem.
AT = _pts(_arc_pts(50, 50, 42, 60, 360, 60) + _arc_pts(80.5, 52, 11.5, 0, 180, 10)[1:]
          + _arc_pts(50, 50, 19, 0, 360, 36) + [(69, 30)])


class P(W):
    """A widget over footage: every geometry a function of the reference's second v; all of it fades out together
    from `out_at`."""

    def __init__(self, t, dur, o, out_at, out_d=0.25):
        super().__init__(t, dur, o)
        self.out_at, self.out_d = out_at, out_d

    def fo(self, v):
        return 1 - E(v, self.out_at, self.out_d)

    def shp(self, name, layers, g, **kw):
        return W.shp(self, name, layers, lambda v: (lambda r: tuple(r[:5]) + (r[5] * self.fo(v),))(g(v)), **kw)

    def tx(self, content, ink, weight, colour, name, g=None, align="left", editable=True, family=P_):
        gg = g or (lambda v: (0, 0, 1, 0, 1))
        return W.txt(self, content, ink, family, weight, colour, name, align=align, editable=editable,
                     g=lambda v: (lambda r: tuple(r[:4]) + (r[4] * self.fo(v),))(gg(v)))

    def type_in(self, clip, at, per, dur=0.1):
        """Letters fade in one after another from second `at`, `per` seconds apart."""
        clip["textStyle"]["animation"] = {"in": tanim("fade", duration=dur, unit="character", stagger=per,
                                                      ease="easeOut", delay=round(max(0.0, at - self.o), 3))}
        return clip

    def typed(self, content, ink, weight, colour, name, at, per, centre=False, g=None, align="left"):
        """Typed text; with centre=True the letters typed so far stay centred on the line's centre (the reference
        types from the middle out), done by sliding the line while it types."""
        gg = g or (lambda v: (0, 0, 1, 0, 1))
        if centre:
            f = f6._font(P_, weight)
            full = f.getlength(content)
            x0, y0, x1, y1 = ink
            bb, cap = f.getbbox(content), f.getbbox("H")
            wf = min(x1 - x0, (y1 - y0) * (bb[2] - bb[0]) / max(1, cap[3] - cap[1]))
            n = len(content)

            def frac(v):
                k = max(0.0, min(float(n), (v - at) / per + 1))
                i = int(k)
                a = f.getlength(content[:i])
                b = f.getlength(content[:min(n, i + 1)])
                return (a + (b - a) * (k - i)) / full
            g0 = gg
            gg = lambda v: (lambda r: (r[0] + wf * (1 - frac(v)) / 2,) + tuple(r[1:]))(g0(v))  # noqa: E731
        c = self.tx(content, ink, weight, colour, name, g=gg, align=align)
        return self.type_in(c, at, per)

    def counter(self, content, ink, weight, colour, name, start, secs, g=None, align="left", linear=False):
        """A number that counts up from 0, starting at second `start` and landing `secs` later."""
        a = max(0.0, start - self.o)
        sub = P(self.t, self.dur - a, self.o + a, self.out_at, self.out_d)
        c = sub.tx(content, ink, weight, colour, name, g=g, align=align)
        c["timelineStartUs"] = us(a)
        c["textStyle"].update(counter=True, counterFrom=0, counterSeconds=secs,
                              counterCurve="linear" if linear else "easeOut")
        return c

    def icon(self, name, path, colour, width, g, base, fill=False):
        """A glyph: g(v) = (cx, cy, scale, op); its stroke follows the scale."""
        layers = solid(colour) if fill else outline(colour, width)
        return sh(self, name, layers, lambda v: (lambda r: (r[0], r[1], base[0] * r[2], base[1] * r[2], 0, r[3]))(
            g(v)), base, stroke=0 if fill else width, path=path)

    def box(self, name, layers, r, radius=0.0, op=None):
        """A rounded box on r(v) = (x0, y0, x1, y1); the corner radius never passes half its short side."""
        def g(v):
            x0, y0, x1, y1 = r(v)
            return (x0 + x1) / 2, (y0 + y1) / 2, max(1e-3, x1 - x0), max(1e-3, y1 - y0), 0, op(v) if op else 1.0
        clip = self.shp(name, layers, g)
        if radius:
            rad = radius if callable(radius) else (lambda v: radius)
            clip["shapeStyle"]["keyframes"] = {"cornerRadius": keys([(u, round(min(rad(u + self.o), g(u + self.o)[2] / 2,
                                                                                      g(u + self.o)[3] / 2), 3),
                                                                       "linear") for u in frames_of(self.dur)])}
        return clip

    def avatar(self, sample, geo, r_out, ring, ring_w, gap=0.0, name="Foto"):
        """A round picture in a ring: geo(v) = (cx, cy, ring scale, photo scale, op). The ring is a disc of `ring`
        layers r_out wide, a white disc `gap` px inside it, the photo inside that."""
        def disc(r, scale_i):
            return lambda v: (lambda o: (o[0], o[1], 2 * r * o[scale_i], 2 * r * o[scale_i], 0, o[4]))(geo(v))
        self.shp(f"{name} (aro)", ring, disc(r_out, 2), kind="ellipse", base=(2 * r_out, 2 * r_out))
        rp = r_out - ring_w
        if gap:
            self.shp(f"{name} (borde)", solid(WHITE), disc(rp, 3), kind="ellipse", base=(2 * rp, 2 * rp))
            rp -= gap
        cx0, cy0 = geo(self.o + self.dur)[:2]
        track = self.t.track("video", name)
        mo, op = [], []
        for u in frames_of(self.dur):
            o = geo(u + self.o)
            mo.append((u, {"s": max(1e-3, o[3]), "dx": o[0] - cx0, "dy": o[1] - cy0}, "linear"))
            op.append((u, round(max(0.0, min(1.0, o[4] * self.fo(u + self.o) if o[3] > 0.02 else 0.0)), 4),
                       "linear"))
        clip = self.t.photo(track, sample, 0.0, self.dur, Box(cx0 - rp, cy0 - rp, 2 * rp, 2 * rp), mo,
                            label="Tu foto")
        clip["opacity"] = keys(op)
        self.t.mask(track, clip, "ellipse")
        return clip


def pop(v, a, d=0.33):
    return E(v, a, d)


def _p(id, es, en, order, dur, thumb, tags=()):
    return wide(f"ig11-{id}", es, en, "instagram", dur, order=order,
                tags=["instagram", "elementos", "llamada a la acción", "redes"] + list(tags), thumb_at=thumb)


# --- 1. Profile card: picture, @name, posts / followers / following counting up, Following / Message (6.3–10.5 s) ---
def profile():
    O, D = 6.25, 4.3
    t = _p("perfil", "Tarjeta de perfil", "Profile card", 16400, D, 3.2, ["perfil", "seguir", "seguidores"])
    s = P(t, D, O, 10.13, 0.3)
    m = lambda v: eo(v, 7.62, 0.65)  # noqa: E731  (the square opens into the card)
    sq = lambda v: 120 * E(v, 6.3, 0.45)  # noqa: E731

    def card(v):
        q, h = m(v), sq(v)
        return (960 - h + (520 - 840) * q, 540 - h + (330 - 420) * q, 960 + h + (1400 - 1080) * q,
                540 + h + (750 - 660) * q)
    s.box("Tarjeta", solid(WHITE), card, radius=48)
    ax = lambda v: 960 + (670 - 960) * m(v)  # noqa: E731
    ay = lambda v: 540 + (480 - 540) * m(v)  # noqa: E731
    s.avatar("fx-woman-05", lambda v: (ax(v), ay(v), E(v, 6.5, 0.3), E(v, 6.64, 0.3), 1.0), 103, RING, 7, 5)
    name = s.tx("@yourname", (860, 406, 1250, 436), 400, INK, "Usuario")
    s.type_in(name, 7.8, 0.055)
    for x, num, lab in ((890, "18", "Posts"), (1081, "144k", "Followers"), (1290, "100", "Following")):
        s.counter(num, (x - 80, 481, x + 80, 504), 400, "#1E1E1E", f"{lab} (número)", 8.0, 1.1, align="center",
                  g=lambda v: (0, 0, 1, 0, E(v, 8.0, 0.15)), linear=True)
        s.tx(lab, (x - 90, 530, x + 90, 553), 400, GREY, lab, align="center", g=lambda v: (0, 0, 1, 0, E(v, 8.0, 0.3)))
    # Buttons grow sideways out of their centres.
    for i, (x0, x1, a) in enumerate(((568, 888, 8.03), (919, 1240, 8.13), (1271, 1353, 8.15))):
        c, hw = (x0 + x1) / 2, (x1 - x0) / 2

        def br(v, c=c, hw=hw, a=a):
            q = eo(v, a, 0.45)
            w = max(4.0, hw * q) if v >= a else 0.0
            h = 30 * min(1.0, 0.35 + 0.65 * eo(v, a, 0.25)) if v >= a else 0.0
            return c - w, 672 - h, c + w, 672 + h
        if i == 0:
            s.box("Siguiendo (botón)", solid(LILAC), br, radius=30)
        else:
            s.box("Mensaje (botón)" if i == 1 else "Añadir (botón)", [fill_layer(WHITE), line("#A8A8A8", 2)], br,
                  radius=30)
    s.typed("Following", (612, 660, 780, 683), 400, INK, "Siguiendo", 8.22, 0.033, centre=True, align="center")
    s.icon("Siguiendo (flecha)", CHEV_D, INK, 2.5, lambda v: (788, 673, 1.0, E(v, 8.48, 0.08)), (20, 11))
    s.typed("Message", (980, 660, 1180, 683), 400, INK, "Mensaje", 8.3, 0.035, centre=True, align="center")
    s.icon("Añadir persona", ADD_PERSON, RED, 2.6, lambda v: (1313, 672, E(v, 8.25, 0.25), 1.0), (34, 30))
    return t


def fill_layer(colour):
    return solid(colour)[0]


# --- 2. Post card: a line opens into a photo, a red bar and the like / comment / share / save row (10.73–13.65 s) ---
def post():
    O, D = 10.73, 2.95
    t = _p("publicacion", "Tarjeta de publicación", "Post card", 16401, D, 2.0, ["publicación", "me gusta"])
    s = P(t, D, O, 13.26, 0.3)
    hw = tab([(10.73, 1), (10.83, 4), (10.93, 15), (11.03, 86), (11.13, 258), (11.23, 344), (11.33, 385),
              (11.43, 409), (11.53, 423), (11.73, 438), (11.9, 440)])
    card = lambda v: (960 - hw(v), 330, 960 + hw(v), 750)  # noqa: E731
    track = t.track("video", "Foto")
    photo = t.photo(track, "fx-skater-03", 0.0, D, Box(520, 330, 880, 420), None, label="Tu foto")
    photo["opacity"] = keys([(u, round(s.fo(u + O), 4), "linear") for u in frames_of(D)])
    photo["matte"] = {"clip": s.box("Forma de la tarjeta", solid(WHITE), card, radius=48)["id"], "mode": "alpha"}
    rt = tab([(11.38, 752), (11.43, 721), (11.53, 622), (11.63, 587), (11.73, 563), (11.83, 553), (11.93, 547),
              (12.1, 541)])
    wt = tab([(11.7, 752), (11.81, 690), (11.91, 663), (12.01, 645), (12.11, 633), (12.28, 627)])
    for nm, col, top in (("Barra roja", RED, rt), ("Barra blanca", WHITE, wt)):
        c = s.box(nm, solid(col), lambda v, top=top: (520, top(v), 1400, 750), op=lambda v, top=top: 1.0 if top(v) < 751
                  else 0.0)
        c["matte"] = {"clip": s.box(f"{nm} (forma)", solid(WHITE), card, radius=48)["id"], "mode": "alpha"}
    s.tx("More Info Below", (570, 572, 1000, 597), 400, INK, "Texto", g=lambda v: (0, 0, 1, 0, E(v, 11.8, 0.2)))
    s.icon("Flecha", CHEV_R, INK, 2.6, lambda v: (1343, 584, 1.0, E(v, 11.85, 0.15)), (16, 32))
    for i, (nm, path, cx, w, h) in enumerate((("Me gusta", HEART, 576, 46, 41), ("Comentar", BUBBLE, 678, 44, 38),
                                              ("Compartir", PLANE, 779, 40, 37), ("Guardar", BOOKMARK, 1353, 25, 34))):
        a = 11.9 + 0.06 * i
        s.icon(nm, path, INK, 3.0, lambda v, a=a, cx=cx: (cx, 686, E(v, a, 0.22), 1.0), (w, h))
    return t


# --- the shared rig of the pills: a round thing pops up in the middle, then slides left while a pill grows out ----
def _pill_rig(s, pop_at, move_at, cx_end, pill, colour, move_d=0.75, radius=90):
    """Returns cx(v) (the round thing's centre); draws the pill (x0 offset from cx, x1, y0, y1)."""
    x_off, x1_end, y0, y1 = pill
    q = lambda v: eo(v, move_at, move_d)  # noqa: E731
    cx = lambda v: 960 + (cx_end - 960) * q(v)  # noqa: E731
    s.box("Pastilla", solid(colour), lambda v: (cx(v) - x_off * (1 if v > move_at else 0), y0,
                                               max(cx(v) + 1, 960 + (x1_end - 960) * q(v)), y1),
          radius=radius, op=lambda v: 1.0 if v > move_at else 0.0)
    return cx


# --- 3. Name pill with FOLLOW (14.05–18.25 s) --------------------------------------------------------------------
def follow_pill():
    O, D = 14.05, 4.2
    t = _p("pastilla-seguir", "Nombre con botón seguir", "Name pill with follow", 16402, D, 2.6, ["seguir", "nombre"])
    s = P(t, D, O, 17.88)
    cx = _pill_rig(s, 14.1, 15.22, 680, (80, 1330, 450, 630), LILAC)
    s.avatar("fx-woman-02", lambda v: (cx(v), 540, pop(v, 14.08), pop(v, 14.16), 1.0), 90, solid(RED), 10, 5)
    dx = lambda v: cx(v) - 680  # noqa: E731
    s.tx("Your Name", (795, 497, 1090, 530), 600, WHITE, "Nombre", g=lambda v: (dx(v), 0, 1, 0, E(v, 15.6, 0.25)))
    s.tx("@yourname", (795, 563, 1090, 586), 400, "#F4ECFF", "Usuario", g=lambda v: (dx(v), 0, 1, 0, E(v, 15.8, 0.2)))
    bw = tab([(15.78, 0), (15.85, 5), (15.95, 25), (16.05, 56), (16.15, 80), (16.25, 92)])
    bh = tab([(15.78, 0), (15.85, 5), (15.95, 18), (16.05, 30), (16.15, 36), (16.25, 37)])
    s.box("Seguir (botón)", solid(RED), lambda v: (1196 - bw(v), 541 - bh(v), 1196 + bw(v), 541 + bh(v)),
          radius=37, op=lambda v: 1.0 if v > 15.79 else 0.0)
    s.typed("FOLLOW", (1130, 529, 1262, 553), 500, INK, "Seguir", 16.0, 0.05, centre=True, align="center")
    return t


# --- 4. Red user pill: picture, @name, followers counting up, Instagram ring (18.63–22.83 s) ----------------------
def user_pill():
    O, D = 18.63, 4.2
    t = _p("pastilla-usuario", "Usuario con seguidores", "User pill with followers", 16403, D, 3.2,
           ["usuario", "seguidores", "contador"])
    s = P(t, D, O, 22.46)
    cx = _pill_rig(s, 18.68, 19.8, 680, (90, 1330, 450, 630), RED)
    s.avatar("fx-man-05", lambda v: (cx(v), 540, pop(v, 18.66), pop(v, 18.74), 1.0), 60, solid("#161616"), 7)
    dx = lambda v: cx(v) - 680  # noqa: E731
    s.tx("@yourname", (790, 497, 1150, 530), 600, INK, "Usuario", g=lambda v: (dx(v), 0, 1, 0, E(v, 20.18, 0.25)))
    s.icon("Seguidores (icono)", PEOPLE, WHITE, 2.2, lambda v: (806 + dx(v), 573, 1.0, E(v, 20.38, 0.2)), (32, 25))
    s.counter("144,870", (838, 565, 1000, 583), 400, WHITE, "Seguidores", 20.62, 1.0,
              g=lambda v: (dx(v), 0, 1, 0, E(v, 20.38, 0.2)))
    g = lambda v: (1233, 540, E(v, 20.38, 0.4), 1.0)  # noqa: E731
    s.icon("Instagram (aro)", circ(50, 50, 48), "#D77BE8", 4.5, g, (118, 118))
    s.icon("Instagram", IG, "#D77BE8", 4.5, lambda v: (1233, 540, E(v, 20.45, 0.35), 1.0), (58, 58))
    return t


# --- 5. Picture with a story ring, @name and Follow (23.12–27.45 s) -----------------------------------------------
def story_follow():
    O, D = 23.12, 4.33
    t = _p("avatar-seguir", "Foto de perfil con seguir", "Profile picture with follow", 16404, D, 3.0,
           ["seguir", "historia", "perfil"])
    s = P(t, D, O, 27.08)
    ay = lambda v: 540 + (420 - 540) * eo(v, 24.42, 0.35)  # noqa: E731
    s.avatar("fx-woman-08", lambda v: (960, ay(v), pop(v, 23.2, 0.45), pop(v, 23.3, 0.42), 1.0), 120, RING, 8, 6)
    s.shp("Verificado", solid("#F2E4EE"), lambda v: (1043, ay(v) + 85, 38 * E(v, 25.1, 0.2), 38 * E(v, 25.1, 0.2), 0,
                                                     1.0), path=SCALLOP, base=(38, 38))
    s.icon("Verificado (visto)", CHECK, "#D06EBB", 3.0, lambda v: (1043, ay(v) + 85, E(v, 25.15, 0.2), 1.0),
           (22, 22))
    s.tx("@yourname", (760, 594, 1160, 628), 500, WHITE, "Usuario", align="center",
         g=lambda v: (0, 26 * (1 - eo(v, 24.55, 0.35)), 1, 0, E(v, 24.55, 0.3)))
    hw = tab([(24.55, 1), (24.65, 3), (24.75, 8), (24.85, 54), (24.95, 100), (25.05, 118), (25.15, 131), (25.25, 140)])
    s.box("Seguir (botón)", solid(RED), lambda v: (960 - hw(v), 705, 960 + hw(v), 780), radius=18,
          op=lambda v: 1.0 if v > 24.55 else 0.0)
    s.tx("Follow", (860, 731, 1060, 756), 400, WHITE, "Seguir", align="center",
         g=lambda v: (0, 14 * (1 - eo(v, 24.98, 0.25)), 1, 0, E(v, 24.98, 0.2)))
    return t


# --- 6. «Comment below if you agree» with a comments counter (27.9–32.05 s) ---------------------------------------
def comment():
    O, D = 27.9, 4.15
    t = _p("comenta", "Comenta abajo", "Comment below", 16405, D, 2.9, ["comentarios", "contador"])
    s = P(t, D, O, 31.68)
    hw = tab([(28.98, 0), (29.05, 10), (29.15, 166), (29.25, 239), (29.35, 270), (29.45, 290), (29.55, 301),
              (29.65, 309), (29.85, 314)])
    hh = tab([(28.98, 0), (29.05, 8), (29.15, 56), (29.25, 82), (29.35, 94), (29.45, 100), (29.6, 105), (29.85, 107.5)])
    s.box("Panel", solid(LILAC), lambda v: (960 - hw(v), 563.5 - hh(v), 960 + hw(v), 563.5 + hh(v)), radius=40,
          op=lambda v: 1.0 if v > 28.98 else 0.0)
    iy = tab([(28.95, 540), (29.05, 525), (29.15, 497), (29.25, 474), (29.35, 466), (29.5, 458), (29.7, 455)])
    s.shp("Icono (disco)", solid(DARK), lambda v: (960, iy(v), 92 * pop(v, 27.93, 0.3), 92 * pop(v, 27.93, 0.3), 0,
                                                   1.0), kind="ellipse", base=(92, 92))
    s.icon("Instagram", IG, RED, 4.0, lambda v: (960, iy(v), pop(v, 28.05, 0.25), 1.0), (44, 44))
    s.counter("15,760 Comments", (686, 538, 1000, 561), 400, INK, "Comentarios", 29.72, 1.1,
              g=lambda v: (0, 0, 1, 0, E(v, 29.7, 0.15)))
    s.typed("Comment below if you agree", (688, 588, 1240, 620), 500, INK, "Texto", 29.15, 0.025, centre=True)
    return t


# --- 7. Comment card: picture, @name, «Write any topic…», Reply (32.28–36.6 s) -------------------------------------
def reply():
    O, D = 32.28, 4.32
    t = _p("responder", "Comentario con responder", "Comment card with reply", 16406, D, 2.8,
           ["comentario", "responder"])
    s = P(t, D, O, 36.26)
    hw = tab([(32.3, 1), (32.43, 8), (32.53, 20), (32.63, 147), (32.73, 195), (32.83, 219), (32.93, 233), (33.1, 245),
              (33.3, 250)])
    hh = tab([(32.3, 1), (32.43, 4), (32.53, 11), (32.63, 84), (32.73, 113), (32.83, 125), (32.93, 133), (33.1, 138)])
    top = tab([(33.75, 402), (33.85, 390), (33.95, 375), (34.05, 357), (34.15, 352), (34.35, 343)])
    lb = tab([(33.8, 677), (33.95, 688), (34.05, 680), (34.15, 655), (34.3, 638), (34.45, 632)])
    bb = tab([(33.95, 677), (34.05, 705), (34.15, 722), (34.3, 733), (34.45, 737)])
    late = lambda v: v >= 33.75  # noqa: E731

    def lilac(v):
        if not late(v):
            return 960 - hw(v), 540 - hh(v), 960 + hw(v), 540 + hh(v)
        return 710, top(v), 1210, lb(v)
    s.box("Respuesta (barra)", solid(DARK), lambda v: (710, lb(v) - 48, 1210, bb(v)), radius=48,
          op=lambda v: 1.0 if late(v) and bb(v) > lb(v) + 1 else 0.0)
    s.box("Panel", solid(LILAC), lilac, radius=48)
    s.box("Panel (base)", solid(LILAC), lambda v: (710, lb(v) - 48, 1210, lb(v)),
          op=lambda v: 1.0 if late(v) and bb(v) > lb(v) + 1 else 0.0)
    dx = lambda v: lilac(v)[0] - 710  # noqa: E731
    dy = lambda v: lilac(v)[1] - 343  # noqa: E731
    s.avatar("h-portrait-01", lambda v: (810 + dx(v), 443 + dy(v), 1.0, 1.0, E(v, 32.8, 0.15)), 60, RING, 6, 4)
    s.tx("@yourname", (908, 430, 1180, 459), 600, INK, "Usuario", g=lambda v: (dx(v), dy(v), 1, 0, E(v, 32.83, 0.15)))
    c = s.tx("Write Any Topic...", (751, 556, 1180, 584), 400, INK, "Comentario", g=lambda v: (dx(v), dy(v), 1, 0, 1))
    s.type_in(c, 32.85, 0.05)
    s.tx("Reply", (754, 668, 1000, 697), 400, WHITE, "Responder",
         g=lambda v: (0, bb(v) - 737, 1, 0, E(v, 34.1, 0.2)))
    s.icon("Responder (flecha)", CHEV_R, WHITE, 2.6, lambda v: (1160, 684 + bb(v) - 737, 1.0, E(v, 34.1, 0.2)),
           (16, 32))
    return t


# --- 8. «Tag Someone»: an @ draws itself, the box opens, three pictures pop (36.87–41.3 s) ------------------------
def tag():
    O, D = 36.87, 4.43
    t = _p("etiqueta", "Etiqueta a alguien", "Tag someone", 16407, D, 3.0, ["etiqueta", "arroba", "amigos"])
    s = P(t, D, O, 40.85, 0.3)
    h0 = tab([(37.0, 1), (37.12, 30), (37.22, 70), (37.32, 115), (37.42, 140), (37.52, 148), (37.7, 146)])
    x0 = tab([(38.3, 814), (38.42, 791), (38.52, 755), (38.62, 690), (38.72, 662), (38.82, 648), (38.95, 636),
              (39.1, 630)])
    x1 = tab([(38.3, 1106), (38.42, 1123), (38.52, 1162), (38.62, 1230), (38.72, 1258), (38.82, 1269), (38.95, 1282),
              (39.1, 1290)])
    wide_ = lambda v: v >= 38.3  # noqa: E731

    def red(v):
        if not wide_(v):
            return 960 - h0(v), 540 - h0(v), 960 + h0(v), 540 + h0(v)
        q = L(v, 38.3, 0.8)
        return x0(v), 394 - 5 * q, x1(v), 686 + 4 * q
    s.box("Caja", solid(RED), red, radius=lambda v: 68 if wide_(v) else 0.466 * h0(v))
    cx = tab([(38.3, 960), (38.42, 940), (38.52, 904), (38.62, 828), (38.72, 800), (38.82, 786), (38.95, 775),
              (39.1, 769)])
    rr = tab([(37.15, 0), (37.22, 10), (37.32, 62), (37.42, 95), (37.52, 112), (38.42, 112), (38.52, 100), (38.62, 87),
              (38.82, 82), (39.1, 79)])
    s.shp("Disco", solid(DARK), lambda v: (cx(v), 540, 2 * rr(v), 2 * rr(v), 0, 1.0 if rr(v) > 0.5 else 0.0),
          kind="ellipse", base=(224, 224))
    at = s.icon("Arroba", AT, WHITE, 11.5, lambda v: (cx(v), 540, rr(v) / 79, 1.0 if v > 37.5 else 0.0), (104, 104))
    trim = lambda v: E(v, 37.52, 0.55)  # noqa: E731
    at["shapeStyle"].setdefault("keyframes", {}).update(
        trimStart=keys([(0.0, 0.0, "hold")]),
        trimEnd=keys([(u, round(100 * trim(u + O), 3), "linear") for u in frames_of(D)]))
    for i, (sample, x) in enumerate((("h-portrait-06", 1004), ("h-man-03", 959), ("h-portrait-04", 913))):
        a = 38.82 + 0.1 * (2 - i)
        s.avatar(sample, lambda v, a=a, x=x: (x, 495, E(v, a, 0.18), E(v, a + 0.03, 0.18), 1.0), 33, solid(WHITE),
                 4, name=f"Amigo {3 - i}")
    c = s.tx("Tag Someone", (877, 568, 1250, 605), 400, WHITE, "Texto")
    s.type_in(c, 38.82, 0.065, 0.12)
    return t


# --- 9. «Add Your Story / Share with 14,000 Viewers» (41.55–45.8 s) ------------------------------------------------
def add_story():
    O, D = 41.55, 4.25
    t = _p("tu-historia", "Añade tu historia", "Add your story", 16408, D, 3.0, ["historia", "compartir"])
    s = P(t, D, O, 45.43)
    cx = tab([(42.9, 960), (43.0, 919), (43.1, 782), (43.2, 741), (43.3, 710), (43.4, 701), (43.5, 694), (43.7, 690)])
    x1 = tab([(42.9, 960), (43.0, 1047), (43.1, 1194), (43.2, 1257), (43.3, 1288), (43.4, 1307), (43.5, 1320),
              (43.7, 1333)])
    s.box("Pastilla", solid(LILAC), lambda v: (cx(v), 477, max(cx(v) + 1, x1(v)), 642), radius=42,
          op=lambda v: 1.0 if v > 42.95 else 0.0)
    ay = lambda v: 548 + 7 * L(v, 42.9, 0.6)  # noqa: E731
    s.avatar("h-man-01", lambda v: (cx(v), ay(v), pop(v, 41.6), pop(v, 41.68), 1.0), 103, solid(RED), 10, 6)
    bg = lambda v: (cx(v) + 65, ay(v) + 79, E(v, 42.25, 0.15), 1.0)  # noqa: E731
    s.shp("Más (disco)", [fill_layer(DARK), line(WHITE, 2)], lambda v: (lambda b: (b[0], b[1], 46 * b[2], 46 * b[2],
                                                                                    0, 1.0))(bg(v)),
          kind="ellipse", base=(46, 46))
    s.icon("Más", PLUS, WHITE, 2.5, bg, (22, 22))
    s.typed("Share with 14,000 Viewers", (822, 568, 1300, 598), 400, INK, "Texto", 43.0, 0.022, centre=True)
    hw = tab([(43.85, 0), (43.92, 8), (44.0, 53), (44.1, 132), (44.2, 164), (44.3, 180), (44.45, 197)])
    bt = tab([(43.92, 425), (44.0, 444), (44.1, 488), (44.2, 503), (44.3, 515), (44.45, 522)])
    s.box("Etiqueta roja", solid(RED), lambda v: (1038 - hw(v), 418, 1038 + hw(v), bt(v)), radius=22,
          op=lambda v: 1.0 if v > 43.86 else 0.0)
    s.tx("Add Your Story", (880, 457, 1196, 487), 500, "#2A0A07", "Título", align="center",
         g=lambda v: (0, 0, 1, 0, E(v, 44.25, 0.2)))
    return t


# --- 10. «Click Our Bio Link» (46.13–50.35 s) ---------------------------------------------------------------------
def bio_link():
    O, D = 46.13, 4.22
    t = _p("enlace-bio", "Enlace en la biografía", "Click our bio link", 16409, D, 3.0, ["enlace", "biografía"])
    s = P(t, D, O, 49.98)
    cx = tab([(47.25, 960), (47.38, 907), (47.48, 797), (47.58, 732), (47.68, 700), (47.78, 682), (47.88, 669),
              (47.98, 663), (48.15, 658)])
    off = tab([(47.3, 0), (47.48, 63), (47.58, 81), (47.68, 94), (47.78, 102), (47.98, 108), (48.15, 110)])
    x1 = tab([(47.25, 960), (47.38, 1012), (47.48, 1154), (47.58, 1241), (47.68, 1279), (47.78, 1298), (47.88, 1313),
              (47.98, 1322), (48.15, 1332)])
    s.box("Pastilla", solid(RED), lambda v: (cx(v) + off(v), 470, max(cx(v) + off(v) + 1, x1(v)), 610), radius=70,
          op=lambda v: 1.0 if v > 47.27 else 0.0)
    s.shp("Disco", solid(LILAC), lambda v: (cx(v), 540, 140 * pop(v, 46.2, 0.3), 140 * pop(v, 46.2, 0.3), 0, 1.0),
          kind="ellipse", base=(140, 140))
    s.icon("Instagram", IG, INK, 5.0, lambda v: (cx(v), 540, pop(v, 46.33, 0.25), 1.0), (62, 62))
    s.typed("Click Our Bio Link", (812, 522, 1240, 557), 400, INK, "Texto", 47.45, 0.033, centre=True)
    s.icon("Enlace", LINK, INK, 3.0, lambda v: (1266, 540, 1.0, E(v, 48.0, 0.15)), (36, 36))
    return t


# --- 11. «Watch Our Latest Reels» with a views counter (50.72–54.95 s) ---------------------------------------------
def reels():
    O, D = 50.72, 4.23
    t = _p("reels", "Mira nuestros reels", "Watch our latest reels", 16410, D, 3.2, ["reels", "vistas", "contador"])
    s = P(t, D, O, 54.60)
    cx = tab([(51.97, 960), (52.07, 872), (52.17, 766), (52.27, 726), (52.37, 704), (52.47, 694), (52.57, 685),
              (52.8, 678)])
    x0 = tab([(51.97, 960), (52.07, 780), (52.17, 685), (52.27, 632), (52.37, 600), (52.47, 585), (52.57, 569),
              (52.8, 558)])
    x1 = tab([(51.97, 960), (52.07, 1079), (52.17, 1229), (52.27, 1288), (52.37, 1319), (52.47, 1335), (52.57, 1345),
              (52.8, 1362)])
    s.box("Caja", solid(RED), lambda v: (x0(v), 437, max(x0(v) + 1, x1(v)), 642), radius=50,
          op=lambda v: 1.0 if v > 51.99 else 0.0)
    s.shp("Aro", solid(LILAC), lambda v: (cx(v), 540, 160 * pop(v, 50.78, 0.4), 160 * pop(v, 50.78, 0.4), 0, 1.0),
          kind="ellipse", base=(160, 160))
    s.shp("Disco", solid(DARK), lambda v: (cx(v), 540, 132 * pop(v, 50.86, 0.4), 132 * pop(v, 50.86, 0.4), 0, 1.0),
          kind="ellipse", base=(132, 132))
    s.icon("Reels", REELS, WHITE, 4.0, lambda v: (cx(v), 540, pop(v, 50.98, 0.28), 1.0), (68, 68))
    s.counter("15,760 Views", (802, 481, 1100, 507), 400, INK, "Vistas", 52.55, 1.05,
              g=lambda v: (0, 0, 1, 0, E(v, 52.45, 0.15)))
    s.typed("Watch Our Latest Reels", (803, 567, 1340, 601), 600, INK, "Texto", 52.07, 0.032, centre=True)
    return t


# --- 12. «Tap to See Story» over a picture with «15 Stories» (55.25–59.2 s) -----------------------------------------
def tap_story():
    O, D = 55.25, 3.95
    t = _p("ver-historia", "Toca para ver la historia", "Tap to see story", 16411, D, 2.6, ["historia", "toca"])
    s = P(t, D, O, 58.83)
    hw = tab([(56.58, 0), (56.7, 175), (56.8, 212), (56.9, 232), (57.0, 245), (57.1, 254), (57.25, 260)])
    top = tab([(56.58, 560), (56.7, 445), (56.8, 420), (56.9, 405), (57.0, 395), (57.1, 388), (57.25, 384)])
    s.box("Panel", solid(LILAC), lambda v: (960 - hw(v), top(v), 960 + hw(v), 580), radius=55,
          op=lambda v: 1.0 if v > 56.6 else 0.0)
    s.tx("Tap to See Story", (751, 437, 1110, 474), 500, INK, "Texto", g=lambda v: (0, 0, 1, 0, E(v, 57.0, 0.2)))
    s.icon("Flecha", CHEV_R, INK, 3.0, lambda v: (1162, 457, 1.0, E(v, 57.05, 0.2)), (16, 32))
    ay = tab([(56.5, 540), (56.6, 545), (56.7, 562), (56.8, 570), (56.9, 574), (57.05, 576)])
    s.avatar("fx-man-02", lambda v: (960, ay(v), pop(v, 55.3, 0.4), pop(v, 55.38, 0.38), 1.0), 56, solid(RED), 6, 3)
    s.tx("15 Stories", (860, 641, 1060, 667), 400, WHITE, "Historias", align="center",
         g=lambda v: (0, 0, 1, 0, E(v, 55.72, 0.2)))
    return t


# --- 13. «Give Double Tap!» with a heart and a likes counter (59.68–63.85 s) ---------------------------------------
def double_tap():
    O, D = 59.68, 4.17
    t = _p("doble-toque", "Dale doble toque", "Give double tap", 16412, D, 3.0, ["me gusta", "corazón", "contador"])
    s = P(t, D, O, 63.46)
    cx = tab([(61.1, 960), (61.23, 944), (61.33, 922), (61.43, 838), (61.53, 785), (61.63, 760), (61.73, 747),
              (61.83, 741), (62.1, 733)])
    s.shp("Disco", solid(LILAC), lambda v: (cx(v), 540, 180 * pop(v, 59.72, 0.3), 180 * pop(v, 59.72, 0.3), 0, 1.0),
          kind="ellipse", base=(180, 180))
    s.icon("Corazón", HEART, RED, 0, lambda v: (cx(v), 543, pop(v, 59.82, 0.3), 1.0), (100, 88), fill=True)
    dx = lambda v: cx(v) - 733  # noqa: E731
    s.typed("Give Double Tap!", (864, 492, 1300, 527), 600, WHITE, "Texto", 61.18, 0.04,
            g=lambda v: (dx(v), 0, 1, 0, 1))
    s.counter("Became after 3,870 Likes", (864, 571, 1250, 595), 400, WHITE, "Me gusta", 61.75, 1.0,
              g=lambda v: (dx(v), 0, 1, 0, E(v, 61.83, 0.12)))
    return t


# --- 14. «Find Your Inspiration» search bar (64.17–68.4 s) ----------------------------------------------------------
def find():
    O, D = 64.17, 4.23
    t = _p("inspiracion", "Encuentra tu inspiración", "Find your inspiration", 16413, D, 3.0, ["buscar", "búsqueda"])
    s = P(t, D, O, 68.05)
    cx = tab([(65.2, 960), (65.32, 944), (65.42, 916), (65.52, 826), (65.62, 763), (65.72, 735), (65.82, 716),
              (65.92, 710), (66.1, 700)])
    x1 = tab([(65.2, 960), (65.32, 1001), (65.42, 1035), (65.52, 1141), (65.62, 1207), (65.72, 1240), (65.85, 1262),
              (66.1, 1275)])
    s.box("Pastilla", solid(LILAC), lambda v: (cx(v) + 15, 477, max(cx(v) + 16, x1(v)), 603), radius=63,
          op=lambda v: 1.0 if v > 65.22 else 0.0)
    s.shp("Disco", solid(DARK), lambda v: (cx(v), 540, 112 * pop(v, 64.22, 0.3), 112 * pop(v, 64.22, 0.3), 0, 1.0),
          kind="ellipse", base=(112, 112))
    s.icon("Buscar", SEARCH, RED, 4.0, lambda v: (cx(v), 540, pop(v, 64.33, 0.25), 1.0), (52, 52))
    s.typed("Find Your Inspiration", (790, 523, 1265, 555), 400, INK, "Texto", 65.42, 0.043, centre=True)
    return t


# --- 15. «Share Post to More» with a picture (68.75–72.75 s) -------------------------------------------------------
def share():
    O, D = 68.75, 4.0
    t = _p("compartir", "Comparte la publicación", "Share post to more", 16414, D, 2.8, ["compartir", "publicación"])
    s = P(t, D, O, 72.45, 0.3)
    h0 = tab([(68.78, 1), (68.88, 6), (68.98, 40), (69.08, 55), (69.18, 65), (69.3, 70)])
    x0 = tab([(69.9, 890), (70.0, 841), (70.1, 726), (70.2, 647), (70.3, 616), (70.4, 595), (70.55, 574)])
    x1 = tab([(69.9, 1030), (70.0, 1053), (70.1, 1107), (70.2, 1138), (70.3, 1147), (70.4, 1160), (70.55, 1170)])

    def pill(v):
        if v < 69.9:
            return 960 - h0(v), 540 - h0(v), 960 + h0(v), 540 + h0(v)
        return x0(v), 470, x1(v), 610
    s.box("Pastilla", solid(WHITE), pill, radius=lambda v: 35 + 35 * L(v, 69.9, 0.3))
    px = lambda v: 960 if v < 69.9 else x0(v) + 70  # noqa: E731
    s.icon("Avión", PLANE, RED, 3.5, lambda v: (px(v), 540, E(v, 69.15, 0.2), 1.0), (58, 54))
    s.typed("Share Post to More", (716, 522, 1160, 556), 400, LILAC, "Texto", 70.05, 0.039, centre=True)
    sc = tab([(70.05, 0), (70.15, 0.12), (70.25, 0.2), (70.35, 0.45), (70.45, 0.8), (70.55, 1.0)])
    s.avatar("fx-woman-03", lambda v: (1276, 540, sc(v), tab([(70.25, 0), (70.35, 0.4), (70.45, 0.8), (70.57, 1)])(v),
                                       1.0), 68, RING, 7, 4)
    return t


TEMPLATES = [profile, post, follow_pill, user_pill, story_follow, comment, reply, tag, add_story, bio_link, reels,
             tap_story, double_tap, find, share]
