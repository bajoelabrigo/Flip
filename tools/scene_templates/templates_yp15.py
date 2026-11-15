"""Video 60440006.mp4 as Kit de YouTube Stock templates (yp15-*). See docs/plan-youtube-pack-2.md.

«Advanced Edit Lower Thirds»: frosted glass bars over footage (1920×1080, 30 fps, 20 s), each one studied on 10 fps
and 30 fps sheets. Every bar is the union of two rounded boxes with a step between them (the notched outline):
one box opens from a thin upright pill, the other from a small pill at its far end, and they melt into one
outline with soft inner corners; then the green pill pops (line → dot → pill), the words slide up word by word
inside their line, and the photos rise. The exit is the same backwards: words drop, the pill shrinks to a dot,
the boxes pull apart and close. The glass is a blur of what is under it (an adjustment layer masked to the
outline, frame by frame) with a light tint and a thin white edge.

The pack cover and the settings panel are skipped; the green «envato» pill becomes a green pill with a neutral word
and the green round icon holds the `logo-flip` slot. Photos are slots. Kit de YouTube › Tercios; order 18600-.
Study notes in tienda/plantillas/estudio-60440006/NOTAS.md.
"""

from __future__ import annotations

import templates_llt_f as f6
from kit import Box, wide
from llt_motion import frames_of
from scene import effect, keys, tanim, us
from templates_tit_e import solid
from templates_yp0 import W, E

LATO = "Lato"
for _w, _f in ((900, "Black"), (700, "Bold"), (400, "Regular")):
    f6._FILES[(LATO, _w)] = f"fonts.basic/fonts/lato/Lato-{_f}.ttf"
WHITE, GREEN, INK = "#FFFFFF", "#86F43B", "#151515"
BACKDROP = "#1E1F24"   # the reference's dark demo grid behind the bars
# The frosted blur behind the glass (a masked adjustment layer) works in a video but the app does not yet move a
# standalone adjustment's mask when it fits a piece into a Short: off until it does (NOTAS.md › Motor pendiente).
GLASS_BLUR = False
EMPTY = "M -50 -50 L -49.9 -50 L -49.9 -49.9 Z"


# --- the notched outline: union of rounded boxes, round outer corners, soft inner ones -----------------------------
def _loops(rects):
    """Rectilinear outline loops (clockwise on screen) of the union of boxes (x0, y0, x1, y1, r)."""
    rs = [r for r in rects if r[2] - r[0] > 0.5 and r[3] - r[1] > 0.5]
    if not rs:
        return []
    xs = sorted({v for r in rs for v in (r[0], r[2])})
    ys = sorted({v for r in rs for v in (r[1], r[3])})
    nx, ny = len(xs) - 1, len(ys) - 1

    def full(i, j):
        if i < 0 or j < 0 or i >= nx or j >= ny:
            return False
        cx, cy = (xs[i] + xs[i + 1]) / 2, (ys[j] + ys[j + 1]) / 2
        return any(r[0] < cx < r[2] and r[1] < cy < r[3] for r in rs)
    nxt = {}
    for i in range(nx):
        for j in range(ny):
            if not full(i, j):
                continue
            x0, x1, y0, y1 = xs[i], xs[i + 1], ys[j], ys[j + 1]
            if not full(i, j - 1):
                nxt.setdefault((x0, y0), []).append((x1, y0))
            if not full(i + 1, j):
                nxt.setdefault((x1, y0), []).append((x1, y1))
            if not full(i, j + 1):
                nxt.setdefault((x1, y1), []).append((x0, y1))
            if not full(i - 1, j):
                nxt.setdefault((x0, y1), []).append((x0, y0))
    loops = []
    while nxt:
        start = next(iter(nxt))
        loop, p = [start], start
        while True:
            q = nxt[p].pop()
            if not nxt[p]:
                del nxt[p]
            if q == start:
                break
            loop.append(q)
            p = q
            if p not in nxt:
                break
        # drop points in the middle of a straight run
        out = []
        n = len(loop)
        for k in range(n):
            a, b, c = loop[k - 1], loop[k], loop[(k + 1) % n]
            if (a[0] == b[0] == c[0]) or (a[1] == b[1] == c[1]):
                continue
            out.append(b)
        if len(out) >= 4:
            loops.append(out)
    return loops


def _rounded(rects, fillet):
    """Each loop as [(p1, corner, p2)]: the corner cut back by its radius on both sides."""
    out = []
    for loop in _loops(rects):
        n = len(loop)
        corners = []
        for k in range(n):
            a, p, b = loop[k - 1], loop[k], loop[(k + 1) % n]
            la, lb = abs(a[0] - p[0]) + abs(a[1] - p[1]), abs(b[0] - p[0]) + abs(b[1] - p[1])
            cross = (p[0] - a[0]) * (b[1] - p[1]) - (p[1] - a[1]) * (b[0] - p[0])
            if cross > 0:
                rad = next((r[4] for r in rects if p[0] in (r[0], r[2]) and p[1] in (r[1], r[3])),
                           max(r[4] for r in rects))
            else:
                rad = fillet
            rad = max(0.0, min(rad, la / 2, lb / 2))
            da = ((a[0] - p[0]) / max(1e-9, la), (a[1] - p[1]) / max(1e-9, la))
            db = ((b[0] - p[0]) / max(1e-9, lb), (b[1] - p[1]) / max(1e-9, lb))
            corners.append(((p[0] + da[0] * rad, p[1] + da[1] * rad), p, (p[0] + db[0] * rad, p[1] + db[1] * rad)))
        out.append(corners)
    return out


def outline_svg(rects, fillet=22.0, W_=1920.0, H_=1080.0):
    parts = []
    for corners in _rounded(rects, fillet):
        f = lambda q: f"{q[0] * 100 / W_:.3f} {q[1] * 100 / H_:.3f}"  # noqa: E731
        s_ = "M " + f(corners[-1][2])
        for p1, p, p2 in corners:
            s_ += f" L {f(p1)} Q {f(p)} {f(p2)}"
        parts.append(s_ + " Z")
    return " ".join(parts) or EMPTY


def outline_points(rects, fillet=22.0, steps=4):
    """The outline flattened (for a freeform mask), in 0..1 of the frame; the first loop only (one mask)."""
    loops = _rounded(rects, fillet)
    if not loops:
        return [[-0.1, -0.1], [-0.099, -0.1], [-0.099, -0.099]]
    pts = []
    for p1, p, p2 in loops[0]:
        for i in range(steps + 1):
            t_ = i / steps
            x = (1 - t_) ** 2 * p1[0] + 2 * (1 - t_) * t_ * p[0] + t_ ** 2 * p2[0]
            y = (1 - t_) ** 2 * p1[1] + 2 * (1 - t_) * t_ * p[1] + t_ ** 2 * p2[1]
            pts.append([round(x / 1920, 5), round(y / 1080, 5)])
    return pts


def argb(colour, alpha):
    return f"#{round(alpha * 255):02x}{colour.lstrip('#').lower()}"


def glass_layers(tint=WHITE, alpha=0.2, edge=0.75, width=2.2):
    return [{"id": "fill", "kind": "fill", "enabled": True, "opacity": 1.0,
             "paint": {"kind": "solid", "color": argb(tint, alpha)}},
            {"id": "stroke", "kind": "stroke", "enabled": True, "width": width, "strokeAlign": "inside",
             "opacity": 1.0, "paint": {"kind": "solid", "color": argb(WHITE, edge)}}]


def grow(rect, a, n, b, m, side="l", minw=12.0):
    """A box (x0, y0, x1, y1, r) that opens from a thin upright pill on `side` from second a over n seconds, and
    closes back to it from second b over m; None while shut."""
    x0, y0, x1, y1, r = rect

    def at(v):
        if v < a or v > b + m:
            return None
        q = E(v, a, n) * (1 - E(v, b, m))
        if q <= 0.0:
            return None
        w = minw + (x1 - x0 - minw) * q
        rr = min(r, w / 2)
        if side == "l":
            return (x0, y0, x0 + w, y1, rr)
        if side == "r":
            return (x1 - w, y0, x1, y1, rr)
        c = (x0 + x1) / 2
        return (c - w / 2, y0, c + w / 2, y1, rr)
    return at


class G(W):
    """A glass lower third: every geometry is a function of the reference's second v."""

    def glass(self, boxes, fillet=22.0, blur=22.0, layers=None, name="Cristal"):
        """boxes = [fn(v) -> (x0, y0, x1, y1, r) | None]: the frosted outline of their union, redrawn every frame
        (one outline per frame in `pathShapes`) in a box round everything it ever covers, so a Short moves it with
        the rest; under it, a blur of the footage seen only through the glass (a track matte on the shape)."""
        us_ = frames_of(self.dur)
        sets = [[b for b in (fn(u + self.o) for fn in boxes) if b] for u in us_]
        every = [r for rs in sets for r in rs]
        bx0, by0 = min(r[0] for r in every), min(r[1] for r in every)
        bx1, by1 = max(r[2] for r in every), max(r[3] for r in every)
        bw, bh = bx1 - bx0, by1 - by0
        shapes, idx, last = [], [], None
        for u, rs in zip(us_, sets):
            moved = [(r[0] - bx0, r[1] - by0, r[2] - bx0, r[3] - by0, r[4]) for r in rs]
            svg = outline_svg(moved, fillet, bw, bh) if moved else EMPTY
            if svg != last:
                shapes.append(svg)
                idx.append((u, len(shapes) - 1))
                last = svg
        t = self.t
        if GLASS_BLUR:
            # The blur of the footage under the glass: a standalone adjustment layer masked to the outline frame by
            # frame (in frame coordinates). Off until the app fits such a mask into a Short (NOTAS.md, motor).
            adj = t.adjust([effect("builtin.effects.gaussian_blur", u_blurRadius=blur)], 0.0, self.dur,
                           name=f"{name} (desenfoque)")
            pts = [[us(u), outline_points(rs, fillet)] for u, rs in zip(us_, sets)]
            adj["mask"] = {"shape": "freeform", "x": 0.5, "y": 0.5, "w": 1.0, "h": 1.0, "feather": 1.0,
                           "enabled": True, "points": pts[0][1], "pathKeys": pts}
        clip = self.obj(name, layers or glass_layers(), lambda fr, u: ((bx0 + bx1) / 2, (by0 + by1) / 2, bw, bh, 0, 1),
                        path=shapes[0], base=(bw, bh))
        st = clip["shapeStyle"]
        st["customPath"] = shapes[0]
        st["pathShapes"] = shapes
        st.setdefault("keyframes", {})["path"] = keys([(u, i, "hold") for u, i in idx])
        return clip

    def words(self, content, ink, weight, colour, name, a, b, align="left", size=None, band=None, gap=0.07,
              each=0.2):
        """A line whose words slide up into place one after another from second a (inside their own line) and
        drop out the same way from second b."""
        clip = self.say(content, ink, LATO, weight, colour, name, align=align,
                        reveal=lambda fr: band or (ink[0] - 400, ink[1] - (ink[3] - ink[1]) * 0.45, ink[2] + 400,
                                                   ink[3] + (ink[3] - ink[1]) * 0.42))
        n = max(1, len(content.split()))
        out_end = b + each + gap * (n - 1)
        clip["textStyle"]["animation"] = {
            "in": tanim("slide-up", duration=each, unit="word", stagger=gap, ease="easeOut",
                        delay=round(a - self.o, 3), order="forward"),
            "out": tanim("slide-up", duration=each, unit="word", stagger=gap, ease="easeIn",
                         delay=round(max(0.0, self.dur - (out_end - self.o)), 3), order="forward")}
        return clip

    def pill(self, rect, a, b, colour=GREEN, name="Botón", n=0.3, m=0.22):
        """A pill that pops at second a (an upright line, a dot, then it widens) and shrinks back from second b."""
        x0, y0, x1, y1 = rect
        cx, cy, w, h = (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0

        def g(v):
            q = E(v, a, n) * (1 - E(v, b, m))
            if q <= 0:
                return cx, cy, 0, 0, 0, 0.0
            if q < 0.3:
                p = q / 0.3
                return cx, cy, h * (0.12 + 0.88 * p), h * (0.55 + 0.45 * p), 0, 1.0
            p = (q - 0.3) / 0.7
            return cx, cy, h + (w - h) * p, h, 0, 1.0
        return self.shp(name, solid(colour), g, radius=h / 2, base=(w, h))

    def label(self, content, ink, rect, a, b, colour=INK, weight=700, name="Botón (texto)"):
        """The pill's word: it fades in as the pill opens and out before it closes."""
        return self.txt(content, ink, LATO, weight, colour, name,
                        g=lambda v: (0, 0, 1, 0, E(v, a + 0.18, 0.12) * (1 - E(v, b - 0.02, 0.1))))

    def icon(self, cx, cy, r, a, b, colour=GREEN, name="Icono"):
        """The round green badge with the user's logo inside; it pops at a and shrinks from b."""
        def g(v):
            q = E(v, a, 0.25) * (1 - E(v, b, 0.2))
            return cx, cy, 2 * r * q, 2 * r * q, 0, 1.0 if q > 0.01 else 0.0
        self.shp(name, solid(colour), g, kind="ellipse", base=(2 * r, 2 * r))
        lr = r * 0.62
        clip = self.t.photo(self.t.track("video", "Logo"), "logo-flip", 0.0, self.dur,
                            Box(cx - lr, cy - lr, 2 * lr, 2 * lr),
                            [(u, {"s": max(1e-3, E(u + self.o, a + 0.08, 0.22) * (1 - E(u + self.o, b, 0.15)))},
                              "linear") for u in frames_of(self.dur)], label="Tu logo", brandRole="logo")
        clip["name"] = "Logo"
        return clip

    def picture(self, sample, rect, a, b, clip_rect=None, radius=0.0, round_=False, name="Foto", rise=None):
        """A photo slot that rises into rect from second a (shown only inside clip_rect) and sinks from b."""
        x0, y0, x1, y1 = rect
        rise = (y1 - y0) if rise is None else rise
        dy = lambda v: rise * (1 - E(v, a, 0.35)) + rise * E(v, b, 0.25)  # noqa: E731
        track = self.t.track("video", name)
        mo = [(u, {"dy": dy(u + self.o)}, "linear") for u in frames_of(self.dur)]
        clip = self.t.photo(track, sample, 0.0, self.dur, Box(x0, y0, x1 - x0, y1 - y0), mo, label="Tu foto")
        clip["name"] = name
        if round_:
            self.t.mask(track, clip, "ellipse")
            clip["opacity"] = keys([(u, round(E(u + self.o, a, 0.12) * (1 - E(u + self.o, b + 0.13, 0.1)), 4),
                                     "linear") for u in frames_of(self.dur)])
        else:
            cr = clip_rect or rect
            self.mask_to(clip, lambda v: cr)
        return clip


def _p(id, es, en, order, dur, thumb, tags=()):
    t = wide(f"yp15-{id}", es, en, "ytkit", dur, order=order,
             tags=["kit:tercios", "youtube", "tercio", "cristal", "nombre"] + list(tags), thumb_at=thumb)
    t.background = BACKDROP
    return t


# Timing shared by every bar (seconds after the bar starts; studied on 4.87–7.40 s, frames 146–222):
A_IN, B_IN, BOX_N = 0.06, 0.2, 0.17     # the first box opens, the second follows; each in ~5 frames
PILL_IN, TXT_IN = 0.2, 0.36             # the pill pops as the boxes meet; the words after it
HOLD = 1.45
# exit (after the hold): words drop at X, pill shrinks at X+0.1, boxes close at X+0.35 / X+0.4
EXIT_N = 0.75


def bar(id, es, en, order, rects, sides, build, tags=(), fillet=22.0):
    """A bar: rects = its boxes (x0, y0, x1, y1, r) in the order they open; sides = where each opens from;
    build(s, a, x) adds what sits on it (a = when the words start, x = when they leave)."""
    D = round(TXT_IN + HOLD + EXIT_N + 0.1, 2)
    t = _p(id, es, en, order, D, round(TXT_IN + 0.9, 2), tags)
    s = G(t, D, 0.0)
    X = TXT_IN + HOLD
    boxes = [grow(r, (A_IN, B_IN)[min(i, 1)] + 0.04 * max(0, i - 1), BOX_N, X + 0.42 - 0.06 * min(i, 1), 0.24,
                  sides[i]) for i, r in enumerate(rects)]
    s.glass(boxes, fillet)
    build(s, TXT_IN, X)
    return t


# --- 1. Two names with a green pill (4.87–7.40 s) -----------------------------------------------------------------
def dos_nombres():
    def build(s, a, x):
        s.pill((492, 238, 651, 283), PILL_IN, x + 0.1)
        s.label("Studio", (522, 249, 621, 271), None, PILL_IN, x + 0.1, weight=900)
        s.words("Douglas Martinez", (287, 307, 653, 345), 700, WHITE, "Nombre 1", a, x)
        s.words("Louise Simmons", (287, 360, 617, 397), 700, WHITE, "Nombre 2", a + 0.07, x + 0.07)
    return bar("dos-nombres", "Tercio de cristal: dos nombres", "Glass lower third: two names", 18600,
               [(437, 200, 706, 388, 24), (240, 255, 658, 440, 24)], ["r", "l"], build, ["dos personas"])


# --- 2. Role, two names and a photo of the pair (4.95–7.60 s) -----------------------------------------------------
def pareja():
    def build(s, a, x):
        s.words("Concept Artists", (1083, 752, 1310, 778), 400, WHITE, "Cargo", a, x)
        s.words("Leslie & Chris", (1082, 797, 1358, 832), 700, WHITE, "Nombres", a + 0.07, x + 0.07)
        s.picture("h-portrait-04", (1398, 731, 1534, 868), a - 0.05, x + 0.15, name="Foto 1")
        s.picture("man-01", (1538, 731, 1678, 868), a + 0.02, x + 0.2, name="Foto 2")
    return bar("pareja", "Tercio de cristal: dos personas con foto", "Glass lower third: a pair with a photo",
               18601, [(1005, 727, 1722, 815, 24), (1045, 760, 1722, 870, 24)], ["r", "l"], build,
               ["dos personas", "foto"])


# --- 3. Round photo, name on two lines and role (7.40–9.70 s) -----------------------------------------------------
def avatar():
    def build(s, a, x):
        s.shp("Aro", solid(WHITE), lambda v: (1233, 307, 146 * E(v, a - 0.12, 0.25) * (1 - E(v, x + 0.2, 0.18)),
                                             146 * E(v, a - 0.12, 0.25) * (1 - E(v, x + 0.2, 0.18)), 0, 1),
              kind="ellipse", base=(146, 146))
        s.picture("h-man-01", (1163, 237, 1303, 377), a - 0.06, x + 0.12, round_=True, rise=40, name="Foto")
        s.words("Jerome", (1341, 248, 1493, 282), 700, WHITE, "Nombre", a, x)
        s.words("Alexander", (1341, 294, 1553, 328), 700, WHITE, "Apellido", a + 0.07, x + 0.07)
        s.words("Content Creator", (1340, 342, 1578, 368), 400, WHITE, "Cargo", a + 0.14, x + 0.14)
    return bar("foto-redonda", "Tercio de cristal con foto redonda", "Glass lower third with a round photo", 18602,
               [(1127, 214, 1600, 400, 26), (1127, 248, 1632, 400, 26)], ["l", "r"], build, ["foto", "avatar"])


# --- 4. Green logo badge, role, name and a white Subscribe (7.40–9.70 s) -----------------------------------------
def suscribete_logo():
    def build(s, a, x):
        s.icon(389, 800, 46, PILL_IN - 0.05, x + 0.12)
        s.words("Data Scientist", (466, 762, 666, 787), 400, WHITE, "Cargo", a, x)
        s.words("Mark Cook", (466, 800, 693, 833), 700, WHITE, "Nombre", a + 0.07, x + 0.07)
        s.pill((740, 776, 925, 822), PILL_IN + 0.06, x + 0.1, colour=WHITE)
        s.label("Subscribe", (764, 787, 904, 812), None, PILL_IN + 0.06, x + 0.1, weight=400)
    return bar("logo-suscribete", "Tercio de cristal con logo y suscribirse", "Glass lower third, logo and subscribe",
               18603, [(315, 727, 925, 873, 26), (315, 765, 978, 873, 26)], ["l", "r"], build,
               ["suscríbete", "logo"])


# --- 5. One line: green pill, name and role (9.60–11.90 s) --------------------------------------------------------
def una_linea():
    def build(s, a, x):
        s.pill((330, 243, 489, 289), PILL_IN, x + 0.12)
        s.label("Studio", (362, 255, 457, 277), None, PILL_IN, x + 0.12, weight=900)
        s.words("Christopher Baker", (515, 244, 895, 280), 700, WHITE, "Nombre", a, x)
        s.words("Architect", (910, 252, 1045, 280), 400, WHITE, "Cargo", a + 0.14, x + 0.07)
    return bar("una-linea", "Tercio de cristal en una línea", "One-line glass lower third", 18604,
               [(310, 226, 1081, 305, 24)], ["c"], build)


# --- 6. Name with the role in a green pill below (9.60–12.0 s) -----------------------------------------------------
def cargo_verde():
    def build(s, a, x):
        s.words("Dennis Hammond", (1022, 774, 1391, 812), 700, WHITE, "Nombre", a, x)
        s.pill((1257, 840, 1562, 885), PILL_IN + 0.04, x + 0.1)
        s.label("Systems Analyst", (1290, 849, 1527, 875), None, PILL_IN + 0.04, x + 0.1, weight=400)
    return bar("cargo-verde", "Tercio de cristal con cargo en verde", "Glass lower third, role in green", 18605,
               [(985, 744, 1585, 862, 24), (985, 800, 1622, 862, 24)], ["l", "r"], build)


# --- 7. Name and role on one thin bar (11.90–14.30 s) --------------------------------------------------------------
def linea_fina():
    def build(s, a, x):
        s.words("Roger Brooks", (1072, 283, 1351, 316), 700, WHITE, "Nombre", a, x)
        s.words("Brand Designer", (1378, 289, 1602, 316), 400, WHITE, "Cargo", a + 0.14, x + 0.07)
    return bar("linea-fina", "Tercio de cristal fino", "Thin glass lower third", 18606,
               [(1033, 262, 1778, 305, 22), (1033, 262, 1742, 340, 22)], ["l", "r"], build, fillet=18)


# --- 8. Photo, name on two lines and Subscribe (12.0–14.45 s) -----------------------------------------------------
def foto_suscribete():
    def build(s, a, x):
        s.picture("man-04", (398, 676, 586, 880), a - 0.06, x + 0.12, name="Foto")
        s.words("Larry Mark", (620, 704, 850, 738), 700, WHITE, "Nombre", a, x)
        s.words("Anderson", (622, 751, 824, 785), 700, WHITE, "Apellido", a + 0.07, x + 0.07)
        s.pill((622, 806, 808, 853), PILL_IN + 0.06, x + 0.1)
        s.label("Subscribe", (645, 817, 786, 843), None, PILL_IN + 0.06, x + 0.1, weight=400)
    return bar("foto-suscribete", "Tercio de cristal con foto y suscribirse", "Glass lower third, photo and subscribe",
               18607, [(400, 670, 905, 800, 26), (362, 725, 868, 884, 26)], ["r", "l"], build,
               ["suscríbete", "foto"])


# --- 9. Name centred and a Subscribe pill hanging under the bar (14.40–16.70 s) ----------------------------------
def centrado():
    def build(s, a, x):
        s.words("Lucas G. Walker", (548, 243, 876, 280), 700, WHITE, "Nombre", a, x, align="center")
        s.pill((600, 302, 825, 348), PILL_IN + 0.06, x + 0.1)
        s.label("Subscribe", (642, 313, 783, 340), None, PILL_IN + 0.06, x + 0.1, weight=400)
    return bar("centrado", "Tercio de cristal centrado con suscribirse", "Centred glass lower third with subscribe",
               18608, [(460, 212, 965, 318, 24)], ["c"], build, ["suscríbete"])


# --- 10. Logo badge, role, name on two lines and a photo (14.45–16.80 s) ------------------------------------------
def tarjeta_foto():
    def build(s, a, x):
        s.icon(1085, 736, 30, PILL_IN - 0.05, x + 0.12)
        s.words("Influencer", (1137, 752, 1284, 778), 400, WHITE, "Cargo", a, x, align="right")
        s.words("Brenda", (1137, 789, 1284, 825), 700, WHITE, "Nombre", a + 0.07, x + 0.07, align="right")
        s.words("Crawford", (1090, 835, 1286, 872), 700, WHITE, "Apellido", a + 0.14, x + 0.14, align="right")
        s.picture("h-portrait-01", (1325, 690, 1548, 906), a - 0.06, x + 0.12, name="Foto")
    return bar("tarjeta-foto", "Tarjeta de cristal con foto y logo", "Glass card with a photo and logo", 18609,
               [(1032, 685, 1512, 908, 28), (1032, 735, 1550, 908, 28)], ["l", "r"], build, ["foto", "logo"])


# --- 11. Logo badge, name and role (16.90–19.50 s) ---------------------------------------------------------------
def logo_nombre():
    def build(s, a, x):
        s.icon(962, 243, 40, PILL_IN - 0.05, x + 0.12)
        s.words("Joseph McGuire", (1028, 204, 1362, 240), 700, WHITE, "Nombre", a, x)
        s.words("Creative Director", (1028, 252, 1281, 278), 400, WHITE, "Cargo", a + 0.07, x + 0.07)
    return bar("logo-nombre", "Tercio de cristal con logo", "Glass lower third with logo", 18610,
               [(895, 175, 1505, 240, 24), (895, 175, 1462, 313, 24)], ["l", "r"], build, ["logo"])


# --- 12. Name and Subscribe on one line (16.90–19.60 s) -----------------------------------------------------------
def nombre_suscribete():
    def build(s, a, x):
        s.words("Daniel Freeman", (244, 747, 570, 782), 700, WHITE, "Nombre", a, x)
        s.pill((616, 744, 842, 790), PILL_IN + 0.06, x + 0.1)
        s.label("Subscribe", (657, 755, 800, 781), None, PILL_IN + 0.06, x + 0.1, weight=400)
    return bar("nombre-suscribete", "Tercio de cristal con suscribirse", "Glass lower third with subscribe", 18611,
               [(200, 722, 920, 782, 24), (163, 760, 880, 812, 24)], ["r", "l"], build, ["suscríbete"])


TEMPLATES = [dos_nombres, pareja, avatar, suscribete_logo, una_linea, cargo_verde, linea_fina, foto_suscribete,
             centrado, tarjeta_foto, logo_nombre, nombre_suscribete]
