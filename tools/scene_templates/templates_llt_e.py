"""Photo lower thirds, fifth set (2026-11-07): the nine of 49176330.mp4 (1920×1080 at 29.97 fps), a person's photo
in a white frame (square or round, a photo slot), the name in a heavy wide sans that pops in letter by letter (one
word filled, one outlined), and the role on a grey band (#6F717F) that wipes open. Measured frame by frame (notes in
tienda/plantillas/estudio-49176330/NOTAS.md). The reference shows each one big in the middle of the frame: here it
is the same piece at 0.62 of that size on the bottom left, as a lower third, with no background (the user's video
is the background; the app fits it into a Short). Each piece leaves with its entrance played backwards, as the
reference does. Order 8590-. Not published until Jorge says the group is complete.

Type: Archivo Black stretched 1.12 wide (the reference's face is a wide heavy grotesque; Archivo Black measures
6.44 caps-widths for «MARTIN» where the reference has 7.16, Anybody Expanded 9.4).
"""

from __future__ import annotations

from kit import Box, label, wide
from llt_motion import frames_of, mask_track
from scene import fill, keys, no_stroke, stroke, tanim

FONT = "Archivo"
WEIGHT = 900
STRETCH = 1.12
CAP = 0.688  # Archivo Black's capitals, em
WHITE = "#FFFFFF"
BAND = "#6F717F"   # the role's grey band
DARK = "#303136"   # the darker band some pieces put behind the name
FPS = 29.97
K = 0.62  # the reference's size -> ours


def _kit(id, es, en, dur, order, tags, **kw):
    return wide(f"llt5-{id}", es, en, "ytkit", dur, order=order, tags=["kit:lowerthirds", "tercio", "foto"] + tags,
                **kw)


def curve(points):
    """[(frame, value), ...] -> f(frame), linear between, held outside."""
    def f(fr):
        if fr <= points[0][0]:
            return points[0][1]
        for (a, va), (b, vb) in zip(points, points[1:]):
            if fr <= b:
                return va + (vb - va) * (fr - a) / (b - a)
        return points[-1][1]
    return f


# Martin's photo (400 px inside its frame) growing from nothing, frame by frame from his first frame.
GROW = curve([(0, 0), (1, 20), (2, 26), (3, 32), (4, 40), (5, 48), (6, 58), (7, 72), (8, 88), (9, 115), (10, 160),
              (11, 240), (12, 288), (13, 314), (14, 330), (15, 343), (16, 353), (17, 362), (18, 369), (19, 374),
              (20, 379), (21, 383), (22, 387), (23, 390), (24, 392), (25, 394), (26, 396), (27, 398), (29, 400)])


def _placed(edge, w, align):
    """The left of a w-wide text box that, stretched STRETCH wide about its centre, puts its left edge (or right
    edge, or centre) on `edge`."""
    if align == "left":
        return edge + (STRETCH - 1) * w / 2
    if align == "right":
        return edge - w - (STRETCH - 1) * w / 2
    return edge - w / 2


class Piece:
    """One lower third laid out in the reference's coordinates, drawn at K of that size with the reference point
    (rx, ry) landing on (ox, oy); u = 0 plays the piece's first frame and the end plays it backwards."""

    def __init__(self, t, dur, rx, ry, ox=120, oy=960):
        self.t, self.dur, self.rx, self.ry, self.ox, self.oy = t, dur, rx, ry, ox, oy

    def frame(self, u):
        return min(u, self.dur - u) * FPS

    def X(self, x):
        return self.ox + (x - self.rx) * K

    def Y(self, y):
        return self.oy + (y - self.ry) * K

    def R(self, r):
        x0, y0, x1, y1 = r
        return (self.X(x0), self.Y(y0), self.X(x1), self.Y(y1))

    def box(self, r):
        x0, y0, x1, y1 = self.R(r)
        return Box(x0, y0, x1 - x0, y1 - y0)

    def moving(self, full, rect):
        """Keys that make a clip laid out in `full` (reference rect) cover rect(frame) (reference) every frame."""
        box = self.box(full)
        out = []
        for u in frames_of(self.dur):
            x0, y0, x1, y1 = self.R(rect(self.frame(u)))
            w, h = max(0.0, x1 - x0), max(0.0, y1 - y0)
            out.append((u, {"sx": max(1e-4, w / box.w), "sy": max(1e-4, h / box.h), "dx": (x0 + x1) / 2 - box.cx,
                            "dy": (y0 + y1) / 2 - box.cy}, "linear"))
        return box, out

    def shape(self, name, colour, full, rect, kind="rectangle", layers=None, radius=0):
        box, motion = self.moving(full, rect)
        clip = self.t.solid(self.t.track("shape", name), colour, 0.0, self.dur, box, motion, kind=kind,
                            radius=radius, layers=layers or [fill(colour), no_stroke()])
        clip["name"] = name
        return clip

    def photo(self, sample, frame_r, grow_from, round_=False, delay=0.0):
        """The white frame and the photo slot in it, both growing from the frame's corner or edge `grow_from`
        ((ax, ay) in 0..1 of the frame), following Martin's measured growth, `delay` frames late."""
        x0, y0, x1, y1 = frame_r
        side = x1 - x0
        border = 7

        def at(fr, inset):
            s = GROW(fr - delay) / 400
            w, h = (x1 - x0) * s, (y1 - y0) * s
            ax, ay = x0 + grow_from[0] * (x1 - x0), y0 + grow_from[1] * (y1 - y0)
            r = (ax - grow_from[0] * w, ay - grow_from[1] * h, ax + (1 - grow_from[0]) * w, ay + (1 - grow_from[1]) * h)
            return (r[0] + inset * s, r[1] + inset * s, r[2] - inset * s, r[3] - inset * s)
        kind = "ellipse" if round_ else "rectangle"
        self.shape("Marco", WHITE, frame_r, lambda fr: at(fr, 0), kind=kind)
        inner = (x0 + border, y0 + border, x1 - border, y1 - border)
        box, motion = self.moving(inner, lambda fr: at(fr, border))
        clip = self.t.photo(self.t.track("video", "Foto"), sample, 0.0, self.dur, box, motion, label="Tu foto")
        if round_:
            self.t.mask(next(tr for tr in self.t.tracks if clip in tr.clips), clip, "ellipse", x=0.5, y=0.5, w=1.0,
                        h=1.0)
        return clip

    def name(self, content, ink_left, caps_top, caps_bottom, start, name, outline=False, align="left",
             stagger=3.5, per_letter=12.0, preset="pop"):
        """A line of capitals that pops in letter by letter from frame `start` (each letter `per_letter` frames,
        `stagger` frames apart) and leaves the same way backwards; ink_left is its left (or right, align right;
        centre, align center) in reference px."""
        size = round((caps_bottom - caps_top - 1) * K / CAP, 1)
        n = len(content.replace(" ", ""))
        w = size * 0.7 * len(content) + size * 2
        h = size * 1.6
        cy = self.Y((caps_top + caps_bottom) / 2) + size * 0.01
        edge = self.X(ink_left)
        # Laid out unstretched, then stretched about the box centre: place the box so the stretched ink lands on
        # the measured edge.
        box = Box(_placed(edge, w, align), cy - h / 2, w, h)
        # Round seconds: the app before 0.31 drops a stagger or duration that is not a whole number of µs.
        dur_in = round(per_letter / FPS, 2)
        stag = round(stagger / FPS, 2)
        extra = {"from": 0} if preset == "pop" else {}
        anim_in = tanim(preset, duration=dur_in, unit="character", stagger=stag, ease="easeInOut", **extra)
        anim_out = tanim(preset, duration=dur_in, unit="character", stagger=stag, ease="easeInOut", order="backward",
                         **extra)
        t0 = start / FPS
        layers = [stroke(3 * K, WHITE)] if outline else [fill(WHITE)]
        clip = label(self.t, self.t.track("text", name), content, t0, self.dur - 2 * t0, box, FONT, size, WHITE,
                     weight=WEIGHT, align=align, name=name, line=1.0, layers=layers, case="upper",
                     motion=[(0.0, {"sx": STRETCH}, "linear")], anim_in=anim_in, anim_out=anim_out)
        return clip, n

    def band(self, name, colour, full, frac, side="left", alpha=1.0, delay=0.0):
        """A band laid out in `full` that opens from its `side` (left, right, top: the edge that stays; centre
        opens both ways) as Martin's grey band does, frac(frame) of the way, `delay` frames late. Returns the clip
        and rect(frame), the band's reference rect."""
        x0, y0, x1, y1 = full

        def rect(fr):
            k = frac(fr - delay)
            if side == "left":
                return (x0, y0, x0 + (x1 - x0) * k, y1)
            if side == "right":
                return (x1 - (x1 - x0) * k, y0, x1, y1)
            if side == "top":
                return (x0, y0, x1, y0 + (y1 - y0) * k)
            cx = (x0 + x1) / 2
            return (cx - (x1 - x0) * k / 2, y0, cx + (x1 - x0) * k / 2, y1)
        clip = self.shape(name, colour, full, rect, layers=[fill(colour, alpha), no_stroke()])
        return clip, rect

    def role(self, content, ink_left, caps_top, caps_bottom, shift, shown, name="Cargo", align="left",
             line_pitch=None, opacity=None, outline=False):
        """The role, sliding by shift(frame) reference px, shown only inside shown(frame) (a reference rect);
        caps_top/bottom are its first line's, line_pitch the distance between lines (reference px)."""
        size = round((caps_bottom - caps_top - 1) * K / CAP, 1)
        lines = content.split("\n")
        longest = max(len(x) for x in lines)
        w = size * 0.75 * longest + size * 2
        line = (line_pitch * K / size) if line_pitch else 1.0
        h = size * 1.6 + size * line * (len(lines) - 1)
        cy = self.Y((caps_top + caps_bottom) / 2) + size * line * (len(lines) - 1) / 2
        edge = self.X(ink_left)
        box = Box(_placed(edge, w, align), cy - h / 2, w, h)
        two = lambda fr: (lambda v: v if isinstance(v, tuple) else (v, 0.0))(shift(fr))  # noqa: E731
        motion = [(u, {"sx": STRETCH, "dx": two(self.frame(u))[0] * K, "dy": two(self.frame(u))[1] * K}, "linear")
                  for u in frames_of(self.dur)]
        layers = [stroke(3 * K, WHITE)] if outline else [fill(WHITE)]
        clip = label(self.t, self.t.track("text", name), content, 0.0, self.dur, box, FONT, size, WHITE,
                     weight=WEIGHT, align=align, name=name, line=line, case="upper", motion=motion, layers=layers)
        if opacity:
            clip["opacity"] = keys([(u, opacity(self.frame(u)), "linear") for u in frames_of(self.dur)])

        def local(u):
            # The mask lives in the clip's own frame: undo the slide and the stretch about the box centre.
            x0, y0, x1, y1 = self.R(shown(self.frame(u)))
            if x1 - x0 < 0.5:
                return (-4000.0, -4000.0, -3999.0, -3999.0)
            dx, dy = (v * K for v in two(self.frame(u)))
            cx = box.cx + dx
            return (box.cx + (x0 - cx) / STRETCH, y0 - dy, box.cx + (x1 - cx) / STRETCH, y1 - dy)
        mask_track(self.t, clip, box, local, self.dur)
        return clip


# Martin's grey band: how far its right edge is (909 -> 1429 over frames 26-55), and his role's slide.
_OPEN = curve([(26, 909), (27, 915), (28, 918), (29, 922), (30, 927), (31, 932), (32, 939), (33, 946), (34, 956),
               (35, 967), (36, 980), (37, 998), (38, 1021), (39, 1055), (40, 1117), (41, 1224), (42, 1286),
               (43, 1320), (44, 1344), (45, 1361), (46, 1375), (47, 1386), (48, 1395), (49, 1402), (50, 1409),
               (51, 1414), (52, 1419), (53, 1423), (54, 1426), (55, 1429)])
OPEN = lambda fr: (_OPEN(fr) - 909) / 520  # noqa: E731
SLIDE = curve([(38, -300), (40, -220), (41, -162), (42, -115), (43, -89), (44, -71), (45, -58), (46, -47),
               (47, -39), (48, -32), (49, -26), (50, -22), (51, -17), (52, -14), (53, -11), (54, -8), (55, -6),
               (56, -4), (58, -2), (60, 0)])
LEFTWARD = lambda fr: -SLIDE(fr)  # noqa: E731
# A name sliding out to the left from behind a photo on its right (Rachel's measured at 0.8 / 1.2 / 1.6 s).
OUT_OF_PHOTO = curve([(14, 520), (20, 490), (24, 430), (28, 300), (32, 120), (36, 15), (42, 0)])
GREY_TO_WHITE = curve([(20, 0.5), (40, 1.0)])
# Kris's lines rising from under a line.
RISE = curve([(24, 95), (27, 50), (30, 20), (33, 6), (36, 0)])
STILL = lambda fr: 0.0  # noqa: E731
D = 5.2  # every piece plays its entrance backwards to leave (6.37 s -> 11.57 s of the video for Martin)


def _piece(id, es, en, order, tags, origin):
    t = _kit(id, es, en, D, order, tags, thumb_at=2.5)
    return t, Piece(t, D, origin[0], origin[1])


def martin():
    """1: square photo on the left growing from its bottom right corner; the first name pops in filled, the last
    name outlined under it, and the grey band with the role opens under them to the right."""
    t, p = _piece("martin", "Tercio con foto: foto cuadrada y nombre a la derecha",
                  "Photo lower third: square photo, name on the right", 8590, ["nombre", "gris"], (494, 729))
    p.photo("man-04", (494, 315, 908, 729), (1.0, 1.0))
    p.name("Martin", 929, 488, 558, 15, "Nombre")
    p.name("Carol", 930, 581, 651, 25, "Apellido", outline=True, stagger=2.5)
    _, band = p.band("Banda", BAND, (909, 675, 1429, 729), OPEN)
    p.role("Photographer", 929, 689, 714, SLIDE, band)
    return t


def rose():
    """2: square photo growing up from its bottom edge; the full name pops in under it and the grey band with the
    role opens down from a line under the name."""
    t, p = _piece("rose", "Tercio con foto: foto arriba y nombre debajo", "Photo lower third: photo above, name below",
                  8591, ["nombre", "gris", "centrado"], (654, 825))
    p.photo("portrait-02", (753, 243, 1167, 657), (0.5, 1.0))
    p.name("Rose Lee", 960.5, 679, 750, 15, "Nombre", align="center", stagger=3.0)
    _, band = p.band("Banda", BAND, (654, 770, 1266, 825), OPEN, side="top")
    p.role("Tv presenter", 960, 785, 810, STILL, band, align="center")
    return t


def monika():
    """3: square photo on the right growing from its left edge; the name pops in on its left, right aligned, and the
    grey band with a two-line role opens to the left from the photo."""
    t, p = _piece("monika", "Tercio con foto: foto a la derecha y nombre a la izquierda",
                  "Photo lower third: photo on the right, name on the left", 8592, ["nombre", "gris"], (475, 750))
    p.photo("h-portrait-01", (1014, 336, 1429, 750), (0.0, 0.5))
    p.role("Monika", 993, 459, 530, OUT_OF_PHOTO, lambda fr: (300, 430, 1014, 560), name="Nombre", align="right",
           opacity=GREY_TO_WHITE)
    _, band = p.band("Banda", BAND, (475, 550, 1022, 653), OPEN, side="right", delay=-8)
    p.role("Vice president\nof marketing", 994, 568, 593, lambda fr: LEFTWARD(fr + 8), band, align="right",
           line_pitch=41)
    return t


def elis():
    """4: round photo growing from its centre; the full name pops in on its right and the grey band with the role
    opens to the right from under the photo."""
    t, p = _piece("elis", "Tercio con foto: foto redonda y nombre a la derecha",
                  "Photo lower third: round photo, name on the right", 8593, ["nombre", "gris", "redonda"],
                  (367, 728))
    _, band = p.band("Banda", BAND, (765, 551, 1549, 605), OPEN, delay=-6)
    p.photo("h-portrait-05", (367, 314, 782, 728), (0.5, 0.5), round_=True)
    p.name("Elis Kuper", 802, 460, 530, 10, "Nombre", stagger=3.8, per_letter=8.0, preset="fade")
    p.role("Brand manager", 834, 566, 590, lambda fr: SLIDE(fr + 6), band)
    return t


def kris():
    """5: round photo growing up from its bottom; the first name outlined and the last name filled pop in under it,
    and the grey band with the role opens down under them."""
    t, p = _piece("kris", "Tercio con foto: foto redonda arriba y nombre debajo",
                  "Photo lower third: round photo above, name below", 8594, ["nombre", "gris", "redonda", "centrado"],
                  (752, 870))
    p.photo("man-01", (753, 194, 1167, 609), (0.5, 1.0), round_=True)
    p.role("Kris", 960, 631, 701, lambda fr: (0.0, RISE(fr)), lambda fr: (700, 600, 1220, 704), name="Nombre",
           align="center", outline=True, opacity=GREY_TO_WHITE)
    p.role("Force", 960, 722, 793, lambda fr: (0.0, RISE(fr - 4)), lambda fr: (700, 708, 1220, 796),
           name="Apellido", align="center", opacity=lambda fr: GREY_TO_WHITE(fr - 4))
    _, band = p.band("Banda", BAND, (752, 815, 1168, 870), OPEN, side="top")
    p.role("Media buyer", 960, 830, 855, STILL, band, align="center")
    return t


def eddy():
    """6: round photo on the right growing from its left edge; a see-through band slides out to the left from
    behind it and the name pops in on it in two lines, right aligned; the role slides in under it from the photo."""
    t, p = _piece("eddy", "Tercio con foto: foto redonda a la derecha y banda oscura",
                  "Photo lower third: round photo on the right, dark band", 8595, ["nombre", "oscuro", "redonda"],
                  (543, 724))
    p.band("Banda oscura", BAND, (543, 480, 1054, 679), OPEN, side="right", alpha=0.43, delay=-8)
    p.photo("man-03", (978, 309, 1392, 724), (0.0, 0.5), round_=True)
    p.role("Eddy", 955, 500, 570, OUT_OF_PHOTO, lambda fr: (400, 470, 978, 580), name="Nombre", align="right",
           opacity=GREY_TO_WHITE)
    p.role("Brian", 957, 589, 659, lambda fr: OUT_OF_PHOTO(fr - 4), lambda fr: (400, 580, 978, 670),
           name="Apellido", align="right", opacity=lambda fr: GREY_TO_WHITE(fr - 4))
    p.role("Director", 978, 698, 722, LEFTWARD, lambda fr: (500, 690, 978, 730), align="right")
    return t


def emma():
    """7: tall photo growing up from its bottom; a see-through band and the grey band open to the right across its
    bottom; the full name pops in on the first and the role slides in on the second."""
    t, p = _piece("emma", "Tercio con foto: foto vertical con bandas encima",
                  "Photo lower third: tall photo with bands across", 8596, ["nombre", "gris", "vertical"], (499, 792))
    p.photo("portrait-07", (499, 277, 913, 792), (0.15, 1.0))
    p.band("Banda oscura", BAND, (506, 624, 1416, 729), OPEN, alpha=0.43, delay=-8)
    p.name("Emma Stone", 525, 643, 714, 15, "Nombre", stagger=3.0)
    _, band = p.band("Banda", BAND, (506, 729, 1416, 784), OPEN)
    p.role("Operations director", 528, 744, 768, SLIDE, band)
    return t


def adam():
    """8: tall photo growing from its centre; a see-through band opens across it both ways and the name pops in on
    it in two lines; the role pops in under the photo."""
    t, p = _piece("adam", "Tercio con foto: foto vertical y nombre encima",
                  "Photo lower third: tall photo, name across it", 8597, ["nombre", "gris", "vertical", "centrado"],
                  (698, 813))
    p.photo("man-05", (753, 255, 1167, 770), (0.5, 0.5))
    p.band("Banda oscura", BAND, (698, 570, 1222, 769), OPEN, side="centre", alpha=0.43, delay=-14)
    p.name("Adam", 960, 592, 662, 12, "Nombre", align="center", stagger=4.0, per_letter=8.0, preset="fade")
    p.name("Driver", 960, 681, 752, 22, "Apellido", align="center", stagger=3.0, per_letter=8.0, preset="fade")
    p.name("Finance director", 960, 788, 813, 33, "Cargo", align="center", stagger=1.5, per_letter=8.0,
           preset="fade")
    return t


def rachel():
    """9: tall photo on the right growing up from its bottom left corner; the first name pops in on its left, the
    last name outlined on a see-through band that opens to the left from the photo; the role slides in under."""
    t, p = _piece("rachel", "Tercio con foto: foto vertical a la derecha y apellido en contorno",
                  "Photo lower third: tall photo on the right, outlined last name", 8598,
                  ["nombre", "oscuro", "vertical"], (490, 786))
    p.band("Banda oscura", BAND, (490, 586, 1024, 695), OPEN, side="right", alpha=0.43, delay=-8)
    p.photo("portrait-04", (1024, 272, 1439, 786), (0.0, 1.0))
    p.role("Rachel", 1004, 493, 564, OUT_OF_PHOTO, lambda fr: (300, 470, 1024, 580), name="Nombre", align="right",
           opacity=GREY_TO_WHITE)
    p.role("Keller", 1003, 606, 675, lambda fr: OUT_OF_PHOTO(fr - 4), lambda fr: (300, 586, 1024, 695),
           name="Apellido", align="right", outline=True, opacity=lambda fr: GREY_TO_WHITE(fr - 4))
    p.role("Auditor", 1004, 716, 740, LEFTWARD, lambda fr: (500, 705, 1024, 750), align="right")
    return t


TEMPLATES = [martin, rose, monika, elis, kris, eddy, emma, adam, rachel]
