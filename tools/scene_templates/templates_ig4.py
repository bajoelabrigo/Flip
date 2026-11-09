"""INSTAGRAM folder video 2656838.mp4, source seconds 0-70, as Stock templates (ig4-*). See docs/plan-instagram.md.

«150+ Instagram stories»: from 5.13 s the reference shows three vertical stories side by side on light grey, a new
three every ~3 s, cut hard (no exit). Panels at x 117/717/1317, y 108, 486×864 px; every coordinate below is in
those reference panel pixels (0..486 × 0..864) and is scaled by R = 1080 / 486 to the 1080×1920 story. Frames are
reference frames (29.97 fps) counted from the start of the story's three; the 10 fps study sheets show frame 3·i.
Each story plays its entrance, holds, and leaves with the entrance backwards at 2.5× (templates_tit_h.S).
Kit de Instagram; ids `ig4-*`, order 15400-. Study notes in tienda/plantillas/estudio-2656838/NOTAS-ig4.md.

Shared helpers (IG, words, pics, dots) may be imported by ig5 / ig6.
"""

from __future__ import annotations

import math
import random

import templates_llt_f as f6
from kit import Box, tall
from llt_motion import frames_of
from scene import effect, gradient, keys, no_stroke
from templates_tit_c import FPS, k
from templates_tit_e import solid
from templates_tit_h import EXIT, ring
from templates_tk5 import Story
from templates_yp4 import art_except

W, H = 1080, 1920
R = W / 486.0
WHITE, BLACK = "#FFFFFF", "#000000"
M = "Montserrat"
AR = "Archivo"
PF = "Playfair Display"
POP = "Poppins"
OS = "Oswald"
for _w, _f in ((400, "Regular"), (500, "Medium"), (600, "SemiBold"), (700, "Bold"), (800, "ExtraBold"),
               (900, "Black")):
    f6._FILES[(AR, _w)] = f"fonts.extra/fonts/archivo/Archivo-{_f}.ttf"
    f6._FILES[(PF, _w)] = f"fonts.basic/fonts/playfairdisplay/PlayfairDisplay-{_f}.ttf"
    f6._FILES[(POP, _w)] = f"fonts.basic/fonts/poppins/Poppins-{_f}.ttf"
for _w, _f in ((300, "Light"), (400, "Regular"), (500, "Medium"), (600, "SemiBold"), (700, "Bold")):
    f6._FILES[(OS, _w)] = f"fonts.basic/fonts/oswald/Oswald-{_f}.ttf"
f6._FILES[("Archivo Black", 400)] = "fonts.basic/fonts/archivoblack/ArchivoBlack-Regular.ttf"
f6._FILES[("Anton", 400)] = "fonts.basic/fonts/anton/Anton-Regular.ttf"
f6._FILES[("Great Vibes", 400)] = "fonts.basic/fonts/greatvibes/GreatVibes-Regular.ttf"
f6._FILES[("Dancing Script", 700)] = "fonts.basic/fonts/dancingscript/DancingScript-Bold.ttf"
f6._FILES[("Sacramento", 400)] = "fonts.extra/fonts/sacramento/Sacramento-Regular.ttf"
f6._FILES[("Bebas Neue", 400)] = "fonts.basic/fonts/bebasneue/BebasNeue-Regular.ttf"
for _w, _f in ((400, "Regular"), (700, "Bold"), (900, "Black")):
    f6._FILES[("Lato", _w)] = f"fonts.basic/fonts/lato/Lato-{_f}.ttf"


def _rs(r):
    return tuple(v * R for v in r)


def const(v):
    return v if callable(v) else (lambda fr, v=v: v)


def ease(fr, at, n):
    return k(fr, at, n)


def lerp(a, b, q):
    return a + (b - a) * q


def lerp_rect(a, b, q):
    return tuple(lerp(x, y, q) for x, y in zip(a, b))


def path_of(points, box):
    """A closed custom path (0..100 of box) through points given in panel px."""
    x0, y0, x1, y1 = box
    w, h = max(1e-6, x1 - x0), max(1e-6, y1 - y0)
    return "M " + " L ".join(f"{(x - x0) / w * 100:.2f} {(y - y0) / h * 100:.2f}" for x, y in points) + " Z"


def bbox(points):
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    return min(xs), min(ys), max(xs), max(ys)


class IG(Story):
    """A story in reference panel px (0..486 × 0..864)."""

    def __init__(self, t, dur):
        Story.__init__(self, t, dur)

    # --- shapes -----------------------------------------------------------------------------------------------
    def box(self, name, layers, r, op=None, rot=None, kind="rectangle", radius=0.0, path=None, base=None):
        """A shape covering r(fr) (panel px; a tuple for a still one); op(fr), rot(fr) degrees."""
        rf = const(r)
        if isinstance(layers, str):
            layers = solid(layers)
        b = (base[0] * R, base[1] * R) if base else None
        return self.rect(name, layers, lambda fr, u: _rs(rf(fr)),
                         op=(lambda fr, u: op(fr)) if op else None, rot=(lambda fr, u: rot(fr)) if rot else None,
                         kind=kind, radius=radius * R, path=path, base=b)

    def poly(self, name, layers, points, off=None, op=None, sc=None):
        """A still polygon (panel px) moved by off(fr) = (dx, dy) panel px; sc(fr) scales it about its centre."""
        bb = bbox(points)
        o = off or (lambda fr: (0.0, 0.0))
        s = sc or (lambda fr: 1.0)

        def r(fr):
            dx, dy = o(fr)
            q = s(fr)
            cx, cy = (bb[0] + bb[2]) / 2 + dx, (bb[1] + bb[3]) / 2 + dy
            hw, hh = (bb[2] - bb[0]) / 2 * q, (bb[3] - bb[1]) / 2 * q
            return cx - hw, cy - hh, cx + hw, cy + hh
        return self.box(name, layers, r, op=op, path=path_of(points, bb), base=(bb[2] - bb[0], bb[3] - bb[1]))

    def bar(self, name, colour, r0, r1, at, n, op=None):
        """A box that grows from rect r0 to r1 between frames at and at + n."""
        return self.box(name, colour, lambda fr: lerp_rect(r0, r1, ease(fr, at, n)), op=op)

    def frame_line(self, name, colour, rect, width, at, n, start="tr", clockwise=False):
        """A rectangle outline that draws itself: one stroke around rect, starting at a corner, over n frames.
        Done as four bars that grow one after another."""
        x0, y0, x1, y1 = rect
        hw = width / 2
        W_, H_ = x1 - x0, y1 - y0
        per = 2 * (W_ + H_)
        # edges in drawing order from the top-right corner, anticlockwise (top ←, left ↓, bottom →, right ↑)
        edges = [((x1, y0), (x0, y0)), ((x0, y0), (x0, y1)), ((x0, y1), (x1, y1)), ((x1, y1), (x1, y0))]
        if clockwise:
            edges = [((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))]
        done = 0.0
        for i, (a, b) in enumerate(edges):
            ln = abs(b[0] - a[0]) + abs(b[1] - a[1])
            s0, s1 = done / per, (done + ln) / per
            done += ln

            def r(fr, a=a, b=b, s0=s0, s1=s1):
                q = min(1.0, max(0.0, (lin_e(fr, at, n) - s0) / (s1 - s0)))
                ex, ey = a[0] + (b[0] - a[0]) * q, a[1] + (b[1] - a[1]) * q
                return (min(a[0], ex) - hw, min(a[1], ey) - hw, max(a[0], ex) + hw, max(a[1], ey) + hw)
            self.box(f"{name} {i + 1}", colour, r)

    def outline_box(self, name, colour, width, r, op=None, radius=0.0):
        """A hollow rectangle (stroke centred on r(fr))."""
        return self.box(name, ring(colour, width * R), r, op=op, radius=radius)

    # --- photos -----------------------------------------------------------------------------------------------
    def photo(self, name, sample, rect, win=None, off=None, zoom=None, label="Tu foto", reuse=None, path=None,
              look=None, op=None, matte=True, kind="rectangle", radius=0.0):
        """A photo slot laid out in rect (panel px), shown through the window win(fr) (a rect, default rect) or a
        custom path; off(fr) = (dx, dy) panel px moves photo and window, zoom(fr) scales the photo."""
        x0, y0, x1, y1 = rect
        w0 = const(win if win is not None else rect)
        o = off or (lambda fr: (0.0, 0.0))
        m = None
        if matte:
            def wr(fr):
                a = w0(fr)
                dx, dy = o(fr)
                return (a[0] + dx, a[1] + dy, a[2] + dx, a[3] + dy)
            base = None
            if path:
                a = w0(10000)
                base = (a[2] - a[0], a[3] - a[1])
            if radius:
                kind = "rounded-rectangle"
                a = w0(10000)
                base = (a[2] - a[0], a[3] - a[1])
            m = self.box(f"{name} (forma)", WHITE, wr, path=path, base=base, kind=kind, radius=radius)
        box = Box(x0 * R, y0 * R, (x1 - x0) * R, (y1 - y0) * R)
        motion = []
        for u in frames_of(self.dur):
            fr = self.frame(u)
            dx, dy = o(fr)
            motion.append((u, {"s": zoom(fr) if zoom else 1.0, "dx": dx * R, "dy": dy * R}, "linear"))
        clip = self.t.photo(self.t.track("video", name), sample, 0.0, self.dur, box, motion, label=label,
                            reuse=reuse)
        clip["name"] = name
        if look:
            clip["effects"] = [dict(e) for e in look]
        if m is not None:
            clip["matte"] = {"clip": m["id"], "mode": "alpha"}
        if op:
            clip["opacity"] = keys([(u, round(max(0.0, min(1.0, op(self.frame(u)))), 4), "linear")
                                    for u in frames_of(self.dur)])
        return clip

    # --- words ------------------------------------------------------------------------------------------------
    def words(self, content, edge, top, bottom, width, family=M, weight=700, colour=WHITE, name="Texto",
              align="left", case="upper", spacing=0.0, anim=None, off=None, reveal=None, op=None, rot=None,
              layers=None, track=None, italic=False):
        """One line: its ink is `width` px wide from edge (left edge, centre or right edge by align), its
        capitals span top..bottom (panel px). anim = (preset, at frame, stagger s, duration s, order);
        off(fr) = (dx, dy) panel px; reveal(fr) = panel rect that shows it; track = (at, n, from_em) letter
        spacing that opens from from_em to the line's spacing."""
        p = f6.Piece(self.t, self.dur, 0)
        p.frame = self.frame
        shift = (lambda fr: (off(fr)[0] * R, off(fr)[1] * R)) if off else None
        rv = (lambda fr: _rs(reveal(fr))) if reveal else None
        clip = p.text(content, edge * R, top * R, bottom * R, width * R, family, weight, colour, name, align=align,
                      spacing_em=spacing, shift=shift, reveal=rv, case=case, layers=layers)
        if italic:
            clip["textStyle"]["italic"] = True
        if anim:
            preset, at, stagger, duration, order = (list(anim) + [0.04, 0.3, "forward"][len(anim) - 2:])[:5]
            self.typed(clip, at, stagger=stagger, duration=duration, preset=preset, order=order)
        if op:
            clip["opacity"] = keys([(u, round(max(0.0, min(1.0, op(self.frame(u)))), 4), "linear")
                                    for u in frames_of(self.dur)])
        if rot is not None:
            clip["rotation"] = keys([(0.0, rot, "hold")])
        if track:
            at, n, from_em = track
            size = clip["textStyle"]["pixelSize"]
            to = clip["textStyle"].get("letterSpacing", 0.0)
            clip["textStyle"].setdefault("keyframes", {})["letterSpacing"] = keys(
                [(u, round(lerp(from_em * size, to, ease(self.frame(u), at, n)), 3), "linear")
                 for u in frames_of(self.dur)])
        return clip

    def logo(self, cx, cy, size, op=None, off=None):
        o = (lambda fr: (off(fr)[0] * R, off(fr)[1] * R)) if off else None
        return Story.logo(self, cx * R, cy * R, size * R, op=op, off=o)

    def dots(self, name, rect, step, radius, colour=WHITE, alpha=0.8, op=None, clip_tri=None):
        """A grid of small dots in rect (one shape, a custom path of many octagons); clip_tri = three points: only
        dots inside that triangle are drawn."""
        x0, y0, x1, y1 = rect
        parts = []
        y = y0 + step / 2
        while y < y1:
            x = x0 + step / 2
            while x < x1:
                if not clip_tri or _in_tri((x, y), clip_tri):
                    pts = [(x + radius * math.cos(math.radians(a)), y + radius * math.sin(math.radians(a)))
                           for a in range(0, 360, 45)]
                    parts.append(path_of(pts, rect))
                x += step
            y += step
        return self.box(name, solid(colour, alpha), rect, op=op, path=" ".join(parts))


def lin_e(fr, at, n):
    return k(fr, at, n)


def _in_tri(p, tri):
    (x1, y1), (x2, y2), (x3, y3) = tri
    d = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
    a = ((y2 - y3) * (p[0] - x3) + (x3 - x2) * (p[1] - y3)) / d
    b = ((y3 - y1) * (p[0] - x3) + (x1 - x3) * (p[1] - y3)) / d
    return a >= 0 and b >= 0 and 1 - a - b >= 0


def dur_for(entrance, hold=2.4):
    return round(entrance + hold + entrance / EXIT, 1)


def story(id, es, en, order, entrance, tags=(), ground=WHITE, prefix="ig4"):
    D = dur_for(entrance)
    t = tall(f"{prefix}-{id}", es, en, "instagram", D, order=order,
             tags=["instagram", "historia", "reels"] + list(tags), thumb_at=round(min(D * 0.55, entrance + 1.0), 1))
    s = IG(t, D)
    s.box("Fondo", ground, (-5, -5, 491, 869))
    return t, s


def finish(t):
    """Two invisible corner marks keep the whole story as the art in a horizontal video (layoutfit skips clips that
    cover the frame, so a full-bleed photo alone would leave only the words to fit)."""
    for i, (x, y) in enumerate(((0.0, 0.0), (W - 2.0, H - 2.0))):
        t.solid(t.track("shape", "Esquina"), "#000000", 0.0, t.duration, Box(x, y, 2.0, 2.0),
                layers=[{"id": "fill", "kind": "fill", "enabled": True, "opacity": 1.0,
                         "paint": {"kind": "solid", "color": "#00000000"}}, no_stroke()])["name"] = f"Esquina {i + 1}"
    return art_except(t)


def grow_x(r, at, n, from_right=False):
    """A rect that grows horizontally from its left (or right) edge."""
    x0, y0, x1, y1 = r
    if from_right:
        return lambda fr: (x1 - (x1 - x0) * ease(fr, at, n), y0, x1, y1)
    return lambda fr: (x0, y0, x0 + (x1 - x0) * ease(fr, at, n), y1)


def grow_y(r, at, n, from_bottom=False):
    x0, y0, x1, y1 = r
    if from_bottom:
        return lambda fr: (x0, y1 - (y1 - y0) * ease(fr, at, n), x1, y1)
    return lambda fr: (x0, y0, x1, y0 + (y1 - y0) * ease(fr, at, n))


def slide(dx, dy, at, n):
    """(dx, dy)(fr): from an offset to rest."""
    return lambda fr: (dx * (1 - ease(fr, at, n)), dy * (1 - ease(fr, at, n)))


def zoom_out(s0, at, n):
    return lambda fr: lerp(s0, 1.0, ease(fr, at, n))


# =====================================================================================================================
# s01 (5.13-7.66 s)
# =====================================================================================================================

def dream():
    """City photo; a white frame draws itself round the story, DREAM appears letter by letter from the right while
    its box draws, the line under it opens from the centre."""
    t, s = story("dream", "Historia: DREAM con marco sobre ciudad", "Story: DREAM with a frame over a city", 15400,
                 2.2, ["foto", "ciudad", "marco"])
    s.photo("Foto", "city-01", (0, 0, 486, 864), zoom=zoom_out(1.12, 0, 60), matte=False)
    s.frame_line("Marco", WHITE, (44, 56, 442, 807), 7, 18, 40)
    s.frame_line("Recuadro", WHITE, (112, 386, 375, 477), 6, 27, 30)
    s.words("DREAM", 243, 412, 454, 220, M, 700, WHITE, "Título", align="center",
            anim=("fade", 27, 0.08, 0.2, "backward"))
    s.words("WORK HARD. DREAM BIG.", 243, 495, 512, 268, M, 400, WHITE, "Texto", align="center", case="upper",
            track=(39, 24, -0.45), anim=("fade", 39, 0.0, 0.4))
    return finish(t)


def style_personal():
    """White story: a black line opens from the centre, the photo with its red stepped shadow rises out of it, the
    three red lines of the title rise in turn and the two small lines fade in."""
    t, s = story("style", "Historia: STYLE IS VERY PERSONAL", "Story: STYLE IS VERY PERSONAL", 15401, 2.0,
                 ["foto", "moda", "rojo"])
    red = "#F7344F"
    # the photo and its shadow rise from behind the black line
    rise = slide(0, 440, 45, 18)
    redpts = [(79, 105), (440, 105), (440, 442), (310, 442), (310, 465), (79, 465)]
    s.poly("Sombra", red, redpts, off=rise)
    phpts = [(45, 100), (195, 100), (195, 76), (404, 76), (404, 436), (45, 436)]
    bb = bbox(phpts)
    s.photo("Foto", "fashion-02", bb, off=rise, path=path_of(phpts, bb))
    # mask both with a white cover under the line
    s.box("Tapa", WHITE, (0, 507, 486, 864))
    s.box("Línea", BLACK, lambda fr: (243 - 198 * ease(fr, 9, 21), 507, 243 + 198 * ease(fr, 9, 21), 518))
    s.words("STYLE IS", 243, 566, 608, 266, AR, 900, red, "Título", align="center", anim=("fade-up-char", 39, 0.02, 0.3))
    s.words("VERY", 243, 621, 663, 162, AR, 900, red, "Título 2", align="center", anim=("fade-up-char", 45, 0.02, 0.3))
    s.words("PERSONAL", 243, 675, 717, 338, AR, 900, red, "Título 3", align="center",
            anim=("fade-up-char", 49, 0.02, 0.3))
    s.words("FASHION CHANGES", 243, 766, 783, 226, M, 500, BLACK, "Texto", align="center", anim=("fade", 54, 0.0, 0.3))
    s.words("BUT STYLE ENDURES", 243, 793, 810, 242, M, 500, BLACK, "Texto 2", align="center",
            anim=("fade", 60, 0.0, 0.3))
    # black panel of the cut that slides off to the left at the start
    s.box("Cortina", BLACK, lambda fr: (0, 0, 486 * (1 - ease(fr, 6, 21)), 864))
    return finish(t)


def youth():
    """Photo of a girl on sky blue: colour bands (yellow, coral above; teal, navy below) close to the edges, a coral
    triangle covers the right half, a dot grid sits on the sky and the hashtag opens from the right."""
    t, s = story("youth", "Historia: #YOUTH & FREEDOM con triángulo", "Story: #YOUTH & FREEDOM with a triangle",
                 15402, 1.6, ["foto", "triángulo", "coral"])
    s.photo("Foto", "selfie-02", (0, 0, 486, 864), zoom=zoom_out(1.08, 0, 50), matte=False)
    s.dots("Puntos", (0, 0, 486, 864), 26, 2.2, WHITE, 0.75, op=lambda fr: ease(fr, 30, 15),
           clip_tri=((0, 0), (486, 0), (0, 864)))
    s.poly("Triángulo", "#F26A5A", [(0, 864), (486, 0), (486, 864)], op=lambda fr: 0.88)
    q = lambda fr: ease(fr, 0, 33)  # noqa: E731
    s.box("Banda amarilla", "#FDBE3C", lambda fr: (0, -2, 486, 137 * (1 - q(fr))))
    s.box("Banda coral", "#F26A5A", lambda fr: (0, 137 * (1 - q(fr)) - 1, 486, 295 * (1 - q(fr))))
    s.box("Banda verde", "#008E8A", lambda fr: (0, 864 - 274 * (1 - q(fr)), 486, 864 - 128 * (1 - q(fr)) + 1))
    s.box("Banda azul", "#02327D", lambda fr: (0, 864 - 128 * (1 - q(fr)), 486, 866))
    s.words("#YOUTH & FREEDOM", 437, 797, 825, 387, M, 700, WHITE, "Título", align="right",
            track=(6, 39, -0.32), anim=("fade", 6, 0.06, 0.15, "backward"))
    return finish(t)


# =====================================================================================================================
# s02 (7.66-10.72 s)
# =====================================================================================================================

def diamond(cx, cy, r):
    return [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]


def summer():
    """Aerial beach; a diamond of the same photo turned upside down opens in the centre, #SUMMER fades in letter by
    letter, its white label opens from the centre and four corner triangles of the turned photo close in."""
    t, s = story("summer", "Historia: #SUMMER con rombo de playa", "Story: #SUMMER with a beach diamond", 15403, 2.2,
                 ["foto", "playa", "verano", "rombo"])
    full = (0, 0, 486, 864)
    first = s.photo("Foto", "h-beach-02", full, matte=False, zoom=lambda fr: 1.04)
    pid = first["placeholderId"]

    def turned(name, pts, sc):
        bb = bbox(pts)
        c = s.photo(name, "h-beach-02", full, reuse=pid, zoom=lambda fr: 1.04,
                    win=lambda fr: lerp_rect(((bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2,
                                              (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2), bb, sc(fr)),
                    path=path_of(pts, bb))
        c["rotation"] = keys([(0.0, 180.0, "hold")])
        return c
    turned("Rombo", diamond(243, 432, 231), lambda fr: ease(fr, 12, 21))
    for i, (pts) in enumerate(([(6, 14), (103, 14), (6, 107)], [(480, 14), (383, 14), (480, 107)],
                               [(6, 850), (103, 850), (6, 757)], [(480, 850), (383, 850), (480, 757)])):
        turned(f"Esquina {i + 1}", pts, lambda fr: ease(fr, 54, 12))
    s.box("Etiqueta", WHITE, lambda fr: (242.5 - 146.5 * ease(fr, 48, 10), 378, 243.5 + 146.5 * ease(fr, 48, 10), 489))
    s.words("#SUMMER", 243, 407, 458, 248, "Bebas Neue", 400, "#111111", "Título", align="center",
            anim=("fade", 30, 0.06, 0.25, "random"))
    return finish(t)


def music():
    """Dark photo in two halves that slide into place, a white line drops from the top and another rises from the
    bottom, MUSIC / DANCE / ENJOY fade in blue letter by letter and turn white."""
    t, s = story("music", "Historia: MUSIC DANCE ENJOY", "Story: MUSIC DANCE ENJOY", 15404, 2.4,
                 ["foto", "música", "fiesta"], ground=BLACK)
    full = (0, 0, 486, 864)
    first = s.photo("Foto", "concert-02", full, win=(0, 0, 486, 432), off=slide(140, 0, 0, 27))
    s.photo("Foto (abajo)", "concert-02", full, win=(0, 432, 486, 864), off=slide(-140, 0, 0, 27),
            reuse=first["placeholderId"])
    s.box("Línea", WHITE, grow_y((240, 0, 246, 262), 27, 24))
    s.box("Línea 2", WHITE, grow_y((240, 602, 246, 864), 30, 24, from_bottom=True))
    blue = "#19A6E3"
    for i, (word, top, bot, x0, x1) in enumerate((("MUSIC", 314, 369, 107, 377), ("DANCE", 405, 459, 103, 382),
                                                   ("ENJOY", 496, 550, 115, 369))):
        at = 30 + 9 * i
        s.words(word, 243, top, bot, x1 - x0, M, 700, blue, f"Título {i + 1} (azul)", align="center",
                anim=("fade", at, 0.05, 0.2))
        s.words(word, 243, top, bot, x1 - x0, M, 700, WHITE, f"Título {i + 1}", align="center",
                op=lambda fr, at=at: ease(fr, at + 27, 9))
    return finish(t)


def trendy():
    """Red story: the red wipes in from the left over white, a photo drops from the top with a green tab, another
    slides in from the right, a white bar from the left; #TRENDY and YOUR STYLE slide in from the right."""
    t, s = story("trendy", "Historia: #TRENDY YOUR STYLE en rojo", "Story: red #TRENDY YOUR STYLE", 15405, 1.6,
                 ["foto", "rojo", "moda"])
    red = "#F22E44"
    s.box("Rastro", "#F5949B", lambda fr: (0, 0, 486 * ease(fr, 0, 24), 864))
    s.box("Rojo", red, lambda fr: (0, 0, 486 * ease(fr, 3, 27), 864))
    first = s.photo("Foto", "fx-man-05", (106, 74, 445, 319), off=slide(0, -330, 9, 21))
    s.box("Pestaña", "#00BF96", lambda fr: (53, 73 - 330 * (1 - ease(fr, 9, 21)), 116, 240 - 330 * (1 - ease(fr, 9, 21))))
    s.photo("Foto 2", "fx-man-05", (41, 350, 381, 727), off=slide(450, 0, 12, 21), reuse=first["placeholderId"])
    s.box("Barra", WHITE, lambda fr: (117 - 380 * (1 - ease(fr, 12, 21)), 710, 381 - 380 * (1 - ease(fr, 12, 21)), 774))
    s.words("#TRENDY", 445, 374, 417, 313, M, 800, WHITE, "Título", align="right", off=slide(120, 0, 27, 18),
            anim=("fade", 27, 0.04, 0.2, "backward"))
    s.words("YOUR STYLE", 445, 444, 468, 184, M, 400, WHITE, "Texto", align="right", off=slide(120, 0, 30, 18),
            anim=("fade", 30, 0.03, 0.2, "backward"))
    return finish(t)


# =====================================================================================================================
# s03 (10.72-13.25 s)
# =====================================================================================================================

GOLD = "#8A7A38"
SCRIPT = "Dancing Script"
BW = [effect("color.basic", saturation=-1.0, contrast=0.12)]


def beauty():
    """Leaves; a white card opens from a line in the middle inside a see-through white frame, the script quote
    writes in and the hashtag types."""
    t, s = story("beauty", "Historia: There is beauty in simplicity", "Story: There is beauty in simplicity", 15406,
                 2.0, ["foto", "naturaleza", "frase", "caligrafía"])
    s.photo("Foto", "fx-nature-03", (0, 0, 486, 864), zoom=zoom_out(1.06, 0, 60), matte=False)

    def card(r):
        x0, y0, x1, y1 = r
        return lambda fr: (lerp(232, x0, ease(fr, 21, 12)) if fr >= 21 else 243, y0,
                           lerp(254, x1, ease(fr, 21, 12)) if fr >= 21 else 243, y1)
    s.box("Marco", solid(WHITE, 0.35), card((47, 136, 439, 726)), op=lambda fr: ease(fr, 21, 6))
    s.box("Tarjeta", WHITE, card((73, 162, 413, 700)), op=lambda fr: ease(fr, 18, 3))
    for i, (word, top, bot, x0, x1) in enumerate((("There is", 297, 345, 151, 339), ("beauty in", 372, 420, 114, 372),
                                                   ("simplicity", 477, 525, 132, 370))):
        s.words(word, (x0 + x1) / 2, top, bot, x1 - x0, SCRIPT, 700, GOLD, f"Frase {i + 1}", align="center",
                case="none", anim=("fade", 24 + 4 * i, 0.03, 0.2))
    s.words("# naturelovers", 243, 642, 660, 200, M, 400, "#333333", "Hashtag", align="center", case="none",
            anim=("typewriter", 36, 0.04, 0.05))
    return finish(t)


def hexagon(cx, top, w, h):
    """A pointy-top hexagon in its w × h box (panel px), as (rect, path)."""
    x0, x1, y0 = cx - w / 2, cx + w / 2, top
    q = h * 0.235
    pts = [(cx, y0), (x1, y0 + q), (x1, y0 + h - q), (cx, y0 + h), (x0, y0 + h - q), (x0, y0 + q)]
    r = (x0, y0, x1, y0 + h)
    return r, path_of(pts, r)


def look_deep():
    """A photo slides down into place over itself, three hexagon outlines rise in yellow, spread apart and turn
    white while LOOK DEEP INTO NATURE fades in letter by letter."""
    t, s = story("look-deep", "Historia: LOOK DEEP INTO NATURE con hexágonos", "Story: LOOK DEEP INTO NATURE with hexagons",
                 15407, 2.0, ["foto", "naturaleza", "hexágono"])
    full = (0, 0, 486, 864)
    first = s.photo("Foto", "y5-yoga-02", full, matte=False, zoom=lambda fr: 1.05)
    s.photo("Foto (encima)", "y5-yoga-02", full, reuse=first["placeholderId"], zoom=lambda fr: 1.05,
            off=lambda fr: (0, -864 * (1 - ease(fr, 0, 21))), win=full)
    for colour, name, op in (("#F2C512", "Hexágono", lambda fr: 1.0 - ease(fr, 48, 9)),
                             (WHITE, "Hexágono blanco", lambda fr: ease(fr, 48, 9))):
        for j, dy in enumerate((0, 36, 72)):
            r, path = hexagon(243, 150, 424, 492)

            def rr(fr, r=r, dy=dy):
                yy = dy * ease(fr, 30, 15) + 260 * (1 - ease(fr, 15, 15))
                return (r[0], r[1] + yy, r[2], r[3] + yy)
            s.box(f"{name} {j + 1}", ring(colour, 5 * R), rr, op=lambda fr, op=op: op(fr) * ease(fr, 15, 4),
                  path=path, base=(424, 492))
    s.words("LOOK DEEP", 243, 369, 422, 262, "Bebas Neue", 400, WHITE, "Título", align="center",
            anim=("fade", 45, 0.04, 0.2, "random"))
    s.words("INTO NATURE", 243, 442, 496, 324, "Bebas Neue", 400, WHITE, "Título 2", align="center",
            anim=("fade", 47, 0.04, 0.2, "random"))
    return finish(t)


def motion():
    """A dancer in yellow duotone; a teal ring grows out of a yellow disc and turns the ground teal to purple,
    a thin ring draws round the disc; MOTION, EXPRESS YOURSELF and a three-line quote fade in."""
    t, s = story("motion", "Historia: MOTION con círculo amarillo", "Story: MOTION with a yellow circle", 15408, 2.2,
                 ["foto", "baile", "círculo", "duotono"], ground="#D9D21C")
    yellow = "#D9D21C"
    s.box("Degradado", [gradient([(0.0, "#3B2470"), (0.55, "#1B5E86"), (1.0, "#0E8C8A")], angle=120), no_stroke()],
          lambda fr: (lambda r: (248 - r, 457 - r, 248 + r, 457 + r))(lerp(199, 1050, ease(fr, 3, 24))),
          kind="ellipse", op=lambda fr: ease(fr, 3, 2))
    s.box("Disco", yellow, (49, 258, 447, 656), kind="ellipse")
    ph = s.photo("Foto", "dance-02", (0, 0, 486, 864), matte=False, zoom=zoom_out(1.06, 0, 60), look=BW)
    ph["blendMode"] = "multiply"
    s.box("Aro", ring("#1B6C8A", 4 * R), lambda fr: (lambda r: (248 - r, 457 - r, 248 + r, 457 + r))(
        lerp(150, 182, ease(fr, 36, 12))), kind="ellipse", op=lambda fr: ease(fr, 36, 6))
    s.words("MOTION", 243, 73, 126, 343, M, 800, "#D6E21C", "Título", align="center",
            anim=("fade", 30, 0.04, 0.2, "random"))
    s.words("EXPRESS YOURSELF", 243, 145, 165, 282, M, 400, WHITE, "Texto", align="center", italic=True,
            anim=("fade", 45, 0.03, 0.2, "random"))
    for i, line in enumerate(("When you dance, your purpose is not", "to get to a certain place on the floor.",
                              "It's to enjoy each step along the way.")):
        s.words(line, 66, 714 + 19 * i, 728 + 19 * i, 352, M, 400, WHITE, f"Frase {i + 1}", case="none",
                italic=True, anim=("fade", 48 + 6 * i, 0.01, 0.2))
    return finish(t)


# =====================================================================================================================
# s04 (13.25-16.85 s)
# =====================================================================================================================

def clip_poly(poly, a, b, c):
    """Sutherland-Hodgman: the part of poly where a·x + b·y <= c."""
    out = []
    for i, p in enumerate(poly):
        q = poly[(i + 1) % len(poly)]
        fp, fq = a * p[0] + b * p[1] - c, a * q[0] + b * q[1] - c
        if fp <= 0:
            out.append(p)
        if (fp <= 0) != (fq <= 0):
            t_ = fp / (fp - fq)
            out.append((p[0] + (q[0] - p[0]) * t_, p[1] + (q[1] - p[1]) * t_))
    return out


def circle_pts(cx, cy, r, n=48):
    return [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def skate():
    """A skater photo goes grey outside a colour circle that shrinks into place; the numbers, a yellow bar from
    the left, a red square from the right, a black label for the hashtag."""
    t, s = story("skate", "Historia: 0256 #skatelife", "Story: 0256 #skatelife", 15409, 2.2,
                 ["foto", "skate", "deporte"], ground="#808080")
    full = (0, 0, 486, 864)
    first = s.photo("Foto", "fx-skater-06", full, matte=False, zoom=lambda fr: 1.05, look=BW)
    s.photo("Foto (color)", "fx-skater-06", full, reuse=first["placeholderId"], zoom=lambda fr: 1.05, kind="ellipse",
            win=lambda fr: (lambda r: (243 - r, 244 - r, 243 + r, 244 + r))(lerp(700, 185, ease(fr, 6, 24))))
    s.box("Barra amarilla", solid("#F2DD00", 0.88), grow_x((0, 219, 226, 298), 39, 15))
    s.box("Cuadro rojo", solid("#FF3B30", 0.92), lambda fr: (239 + 260 * (1 - ease(fr, 39, 12)), 414,
                                                              464 + 260 * (1 - ease(fr, 39, 12)), 637))
    s.words("0256", 243, 532, 608, 276, M, 700, WHITE, "Número", align="center", anim=("fade", 30, 0.12, 0.2, "random"))
    s.words("ENJOY EVERY DAY", 243, 667, 689, 250, M, 400, WHITE, "Texto", align="center",
            anim=("typewriter", 33, 0.06, 0.05))
    s.box("Etiqueta", BLACK, grow_x((69, 710, 417, 795), 33, 12))
    s.words("#skatelife", 243, 728, 772, 323, M, 600, WHITE, "Hashtag", align="center", case="none",
            anim=("fade", 39, 0.06, 0.2, "random"))
    return finish(t)


def secrets():
    """A purple story swept away to the left by a red chevron that leaves a red diagonal over a photo; NO MORE
    SECRETS fades in, a white label grows for #IMAGINE."""
    t, s = story("secrets", "Historia: NO MORE SECRETS #IMAGINE", "Story: NO MORE SECRETS #IMAGINE", 15410, 2.2,
                 ["foto", "rojo", "diagonal", "noche"])
    red = "#F0304A"
    s.photo("Foto", "fx-man-03", (0, 0, 486, 864), matte=False, zoom=zoom_out(1.08, 0, 70))
    s.poly("Diagonal", red, [(486, 0), (486, 38), (126, 420), (486, 752), (486, 864), (0, 864), (0, 482),
                             (106, 417)], op=lambda fr: ease(fr, 18, 3))
    a0 = 486
    a = lambda fr: lerp(a0, -620, ease(fr, 9, 21))  # noqa: E731
    off = lambda fr: (a(fr) - a0, 0)  # noqa: E731
    s.poly("Morado", "#A04BFF", [(-1200, -10), (a0 + 440, -10), (a0, 432), (a0 + 440, 874), (-1200, 874)], off=off,
           op=lambda fr: 1 - ease(fr, 30, 1))
    wb = 170
    s.poly("Flecha", red, [(a0 + 440, -10), (a0 + 440 + wb, -10), (a0 + wb, 432), (a0 + 440 + wb, 874),
                           (a0 + 440, 874), (a0, 432)], off=off, op=lambda fr: 1 - ease(fr, 30, 1))
    for i, (word, top, bot, w) in enumerate((("NO", 513, 558, 102), ("MORE", 577, 622, 205),
                                             ("SECRETS", 636, 682, 311))):
        s.words(word, 24, top, bot, w, M, 800, WHITE, f"Título {i + 1}", anim=("fade", 27 + 3 * i, 0.05, 0.2))
    s.words("DREAM NIGHT LIFE", 24, 705, 726, 267, M, 400, WHITE, "Texto", anim=("fade", 33, 0.04, 0.15))
    s.box("Etiqueta", WHITE, grow_x((25, 760, 415, 841), 33, 15))
    s.words("#IMAGINE", 45, 776, 825, 354, M, 800, red, "Hashtag", anim=("fade", 36, 0.05, 0.15))
    return finish(t)


def big():
    """A photo drops in from the top over white, BIG. slides in letter by letter, a circle of diagonal white
    stripes draws over the photo and the line under it fades in."""
    t, s = story("big", "Historia: BIG. con círculo a rayas", "Story: BIG. with a striped circle", 15411, 2.2,
                 ["foto", "moda", "rayas", "círculo"])
    s.box("Bloque", "#08A3B8", lambda fr: (0, lerp(300, 870, ease(fr, 0, 12)), 486, 870))
    s.photo("Foto", "tk7-flora-01", (0, 0, 486, 765), off=slide(0, -765, 9, 24))
    s.words("BIG.", 41, 40, 139, 295, M, 800, WHITE, "Título", off=slide(60, 0, 30, 18),
            anim=("fade", 30, 0.06, 0.2, "backward"))
    circ = circle_pts(243, 432, 165, 64)
    c45 = math.cos(math.radians(45))
    i = 0
    d = -270.0
    while d < 270:
        band = clip_poly(clip_poly(circ, c45, -c45, d + 12 + 0), -c45, c45, -d)
        if len(band) >= 3:
            bb = bbox(band)
            if bb[2] - bb[0] > 2 and bb[3] - bb[1] > 2:
                s.box(f"Raya {i + 1}", WHITE, bb, path=path_of(band, bb), op=lambda fr, i=i: ease(fr, 51 + i * 0.8, 4))
                i += 1
        d += 34
    s.words("NOTHING IS IMPOSSIBLE", 243, 804, 824, 316, M, 700, BLACK, "Texto", align="center",
            anim=("fade", 54, 0.03, 0.2, "random"))
    return finish(t)


# =====================================================================================================================
# s05 (16.85-19.88 s)
# =====================================================================================================================

def meeting():
    """White story with three columns of one photo: the middle one rises, the side ones drop; a white label opens
    from the left and MEETING WITH FRIENDS fades in in gold."""
    t, s = story("meeting", "Historia: MEETING WITH FRIENDS en columnas", "Story: MEETING WITH FRIENDS in columns",
                 15412, 2.0, ["foto", "amigos", "columnas", "café"])
    full = (0, 0, 486, 864)
    first = s.photo("Foto", "y5-cozy-06", full, win=(97, 0, 389, 864), off=slide(0, 864, 6, 21))
    pid = first["placeholderId"]
    s.photo("Foto (izquierda)", "y5-cozy-06", full, win=(0, 288, 83, 864), off=slide(0, -864, 3, 24), reuse=pid)
    s.photo("Foto (derecha)", "y5-cozy-06", full, win=(403, 0, 486, 578), off=slide(0, -864, 0, 27), reuse=pid)
    s.box("Etiqueta", WHITE, lambda fr: (113, lerp(790, 644, ease(fr, 36, 9)), 113 + 260 * ease(fr, 30, 9), 800))
    gold = "#D19A4E"
    for i, (word, top, bot, x0, x1) in enumerate((("MEETING", 665, 700, 135, 349), ("WITH", 705, 739, 173, 297),
                                                   ("FRIENDS", 744, 778, 141, 344))):
        s.words(word, 243, top, bot, x1 - x0, AR, 800, gold, f"Título {i + 1}", align="center",
                anim=("fade", 36 + 4 * i, 0.04, 0.2))
    s.words("COZY LIGHT", 243, 34, 47, 94, M, 500, WHITE, "Texto", align="center", anim=("fade", 27, 0.05, 0.2))
    s.words("TAKE A PAUSE & ENJOY", 243, 823, 835, 181, M, 500, WHITE, "Texto 2", align="center",
            anim=("fade", 42, 0.03, 0.2, "random"))
    return finish(t)


def sunshine():
    """Four photos in a grid open inside a growing diamond, SUNSHINE fades in letter by letter above, a yellow label
    grows from the centre with #instagood."""
    t, s = story("sunshine", "Historia: SUNSHINE con cuatro fotos", "Story: SUNSHINE with four photos", 15413, 2.0,
                 ["foto", "verano", "collage", "playa"])
    dia = s.box("Rombo", WHITE, lambda fr: (lambda r: (243 - r, 463 - r, 243 + r, 463 + r))(
        max(0.5, lerp(0, 700, ease(fr, 3, 24)))), path="M 50 0 L 100 50 L 50 100 L 0 50 Z", base=(700, 700))
    for i, (sample, r) in enumerate((("summer-03", (33, 94, 236, 455)), ("h-beach-05", (249, 94, 453, 455)),
                                     ("selfie-02", (33, 470, 236, 832)), ("beach-02", (249, 470, 453, 832)))):
        c = s.photo(f"Foto {i + 1}", sample, r, matte=False, label=f"Foto {i + 1}")
        c["matte"] = {"clip": dia["id"], "mode": "alpha"}
    s.words("SUNSHINE", 240, 33, 80, 346, AR, 800, BLACK, "Título", align="center",
            anim=("fade", 9, 0.06, 0.2, "random"))
    s.box("Etiqueta", "#FFDD00", lambda fr: (243 - 180 * ease(fr, 33, 12), 419, 243 + 180 * ease(fr, 33, 12), 506))
    s.words("#instagood", 243, 437, 482, 324, M, 700, BLACK, "Hashtag", align="center", case="none",
            anim=("fade", 36, 0.05, 0.2, "random"))
    return finish(t)


def clear_interior():
    """Tan story: an interior photo opens from the right over half the story, the white frame of the title box
    opens from a line in the centre, CLEAR INTERIOR and the quote fade in, # TRENDY at the foot."""
    t, s = story("clear", "Historia: CLEAR INTERIOR en dos mitades", "Story: CLEAR INTERIOR in two halves", 15414, 2.0,
                 ["foto", "interior", "hogar", "decoración"], ground="#D4A383")
    tan = "#D4A383"
    s.photo("Foto", "interior-02", (243, 0, 486, 864), win=lambda fr: (486 - 243 * ease(fr, 9, 21), 0, 486, 864))
    s.box("Velo", solid(tan, 0.55), (79, 185, 410, 420), op=lambda fr: ease(fr, 27, 9))

    def frame_r(fr):
        q = ease(fr, 45, 12)
        return (lerp(243, 65, q), lerp(260, 172, min(1.0, q * 3)), lerp(243, 424, q), lerp(346, 434, min(1.0, q * 3)))
    s.outline_box("Marco", WHITE, 8, frame_r, op=lambda fr: ease(fr, 45, 2))
    s.words("CLEAR", 242, 219, 259, 192, M, 800, WHITE, "Título", align="center", anim=("fade", 27, 0.04, 0.25))
    s.words("INTERIOR", 242, 270, 310, 279, M, 800, WHITE, "Título 2", align="center", anim=("fade", 39, 0.04, 0.25))
    for i, (line, x0, x1) in enumerate((("THE BEST ROOMS HAVE", 140, 344), ("SOMETHING TO SAY ABOUT", 123, 361),
                                        ("THE PEOPLE", 189, 294), ("WHO LIVE IN THEM", 162, 323))):
        s.words(line, 242, 329 + 15.7 * i, 338 + 15.7 * i, x1 - x0, M, 500, WHITE, f"Frase {i + 1}",
                align="center", anim=("fade", 33 + 3 * i, 0.02, 0.2))
    s.words("# TRENDY", 242, 790, 819, 195, M, 700, WHITE, "Hashtag", align="center", track=(36, 15, -0.3),
            anim=("fade", 36, 0.0, 0.3))
    return finish(t)


# =====================================================================================================================
# s06 (19.88-22.98 s)
# =====================================================================================================================

def fun_cart():
    """A full photo shrinks into a white frame, a red label opens from a line for the hashtag and a white tab rises
    at the foot with # photooftheday. (The reference says #BUM; here #FUN.)"""
    t, s = story("fun", "Historia: #FUN con foto enmarcada", "Story: #FUN with a framed photo", 15415, 2.0,
                 ["foto", "marco", "rojo"])
    s.photo("Foto", "y5-street-02", (35, 38, 450, 825),
            win=lambda fr: lerp_rect((-2, -2, 488, 866), (35, 38, 450, 825), ease(fr, 36, 12)),
            zoom=zoom_out(1.15, 0, 48))
    s.box("Etiqueta", "#F03A52", lambda fr: (242.5 - 183.5 * ease(fr, 45, 9), 76, 243.5 + 183.5 * ease(fr, 45, 9), 188),
          op=lambda fr: ease(fr, 45, 2))
    s.words("#FUN", 243, 102, 164, 260, M, 700, WHITE, "Hashtag", align="center", anim=("fade", 54, 0.05, 0.2))
    s.box("Pestaña", WHITE, lambda fr: (122, lerp(825, 785, ease(fr, 51, 6)), 364, 825))
    s.words("# photooftheday", 243, 800, 820, 201, M, 500, BLACK, "Texto", align="center", case="none",
            anim=("fade", 54, 0.03, 0.2))
    return finish(t)


def spring():
    """Teal slides down off a coral story while a white card rises with a slanted photo, a white frame lights up on
    the photo and SPRING IS IN THE AIR fades in in black italics."""
    t, s = story("spring", "Historia: SPRING IS IN THE AIR", "Story: SPRING IS IN THE AIR", 15416, 2.0,
                 ["foto", "primavera", "flores", "coral"], ground="#F47A5E")
    s.box("Azul", "#0E86AE", lambda fr: (-5, lerp(-5, 870, ease(fr, 9, 54)), 491, 870))
    card = slide(0, 760, 12, 18)
    s.box("Tarjeta", WHITE, lambda fr: (63, 62 + card(fr)[1], 421, 802 + card(fr)[1]))
    pts = [(41, 124), (445, 124), (445, 542), (41, 604)]
    bb = bbox(pts)
    s.photo("Foto", "spring-02", bb, path=path_of(pts, bb), off=slide(0, 700, 15, 18))
    fpts = [(70, 154), (418, 154), (418, 516), (70, 572)]
    fb = bbox(fpts)
    s.box("Marco", ring(WHITE, 3.5 * R), fb, path=path_of(fpts, fb), op=lambda fr: ease(fr, 54, 6), base=(fb[2] - fb[0],
                                                                                                         fb[3] - fb[1]))
    s.words("THE BEST TIME FOR WALKING", 243, 89, 100, 212, M, 500, BLACK, "Texto", align="center", italic=True,
            anim=("fade", 51, 0.02, 0.2))
    for i, (word, top, bot, x0, x1) in enumerate((("SPRING", 623, 663, 132, 355), ("IS IN", 674, 714, 178, 308),
                                                   ("THE AIR", 724, 764, 132, 355))):
        s.words(word, 243, top, bot, x1 - x0, M, 800, BLACK, f"Título {i + 1}", align="center", italic=True,
                anim=("fade", 45 + 4 * i, 0.03, 0.3))
    return finish(t)


def stay_strong():
    """A photo; a red diagonal band sweeps in from the left led by purple, magenta and yellow stripes, two thin red
    stripes follow; STAY STRONG / DON'T GIVE UP fade in with a white rule between, # freedom at the foot."""
    t, s = story("stay-strong", "Historia: STAY STRONG DON'T GIVE UP", "Story: STAY STRONG DON'T GIVE UP", 15417, 2.0,
                 ["foto", "motivación", "rojo", "diagonal"], ground="#1E2522")
    s.photo("Foto", "man-04", (0, 0, 486, 864), matte=False, zoom=zoom_out(1.06, 0, 60))
    band = [(0, 432), (486, 237), (486, 452), (0, 640)]
    bb = bbox(band)
    path = path_of(band, bb)
    lead = lambda fr: lerp(-80, 600, ease(fr, 18, 21))  # noqa: E731
    for colour, ahead, alpha in (("#FFE600", 110, 1.0), ("#FF3FD0", 70, 1.0), ("#5B2BFF", 35, 1.0),
                                 ("#F2312B", 0, 0.9)):
        s.box("Banda" if ahead == 0 else "Banda (color)", solid(colour, alpha),
              lambda fr, ahead=ahead: (0, 237, max(0.5, min(486, lead(fr) + ahead)), 640),
              path=path, base=(486, 403), op=(lambda fr: 1.0 - ease(fr, 39, 6)) if ahead else None)
    s.poly("Raya", solid("#F2312B", 0.9), [(0, 72), (263, 0), (330, 0), (0, 115)], op=lambda fr: ease(fr, 24, 6))
    s.poly("Raya 2", solid("#F2312B", 0.9), [(380, 496), (486, 452), (486, 492), (380, 536)],
           op=lambda fr: ease(fr, 33, 6))
    for i, (word, top, bot, w) in enumerate((("STAY", 365, 408, 158), ("STRONG", 417, 460, 276))):
        s.words(word, 52, top, bot, w, M, 800, WHITE, f"Título {i + 1}", anim=("fade", 42 + 4 * i, 0.04, 0.2))
    s.box("Línea", WHITE, grow_x((54, 480, 337, 492), 48, 9))
    for i, (word, top, bot, w) in enumerate((("DON'T", 514, 556, 208), ("GIVE UP", 568, 610, 264))):
        s.words(word, 52, top, bot, w, M, 800, WHITE, f"Título {i + 3}", anim=("fade", 45 + 4 * i, 0.04, 0.2))
    s.words("# freedom", 459, 710, 744, 257, M, 800, "#F0302A", "Hashtag", align="right", case="none",
            anim=("fade", 48, 0.05, 0.2, "backward"))
    s.words("YOU ARE YOUR ONLY LIMIT", 459, 763, 781, 300, M, 400, WHITE, "Texto", align="right",
            anim=("fade", 51, 0.03, 0.2, "backward"))
    return finish(t)


# =====================================================================================================================
# s07 (22.98-26.11 s)
# =====================================================================================================================

def control():
    """White story: the logo draws in, a photo rises at the bottom, a second photo opens upwards from a line above
    it and carries the logo; CONTROL fades in from the right."""
    t, s = story("control", "Historia: CONTROL con logo y dos fotos", "Story: CONTROL with a logo and two photos",
                 15418, 2.2, ["foto", "logo", "yoga", "calma"])
    s.photo("Foto 2", "y5-yoga-01", (15, 349, 471, 845), win=lambda fr: (15, lerp(845, 349, ease(fr, 30, 18)), 471, 845),
            label="Foto 2")
    s.photo("Foto 1", "y5-h-ocean-03", (15, 16, 471, 330),
            win=lambda fr: (15, lerp(328, 16, ease(fr, 39, 15)), 471, lerp(330, 330, 1)), label="Foto 1")
    s.logo(243, 234, 90, op=lambda fr: ease(fr, 3, 12), off=lambda fr: (0, 207 * (1 - ease(fr, 33, 24))))
    s.words("CONTROL", 244, 92, 134, 316, M, 800, WHITE, "Título", align="center",
            anim=("fade", 51, 0.05, 0.2, "backward"))
    return finish(t)


def born_wild():
    """A blue panel and a desert photo slide down into place; BORN TO BE WILD and two lines fade in, a white
    outline draws round # amazing."""
    t, s = story("born-wild", "Historia: BORN TO BE WILD", "Story: BORN TO BE WILD", 15419, 2.0,
                 ["foto", "aventura", "azul", "desierto"])
    down = slide(0, -864, 0, 30)
    s.box("Panel", "#2387D4", lambda fr: (0, down(fr)[1] - 20, 486, 327 + down(fr)[1]))
    s.photo("Foto", "travel-01", (0, 348, 486, 864), off=down)
    s.words("BORN", 242, 74, 117, 174, M, 400, WHITE, "Título", align="center", anim=("fade", 36, 0.04, 0.3))
    s.words("TO BE", 58, 140, 182, 181, M, 400, WHITE, "Título 2", anim=("fade", 42, 0.04, 0.3))
    s.words("WILD", 259, 140, 182, 170, M, 800, WHITE, "Título 3", italic=True, anim=("fade", 44, 0.04, 0.3))
    s.words("Feel free and unashamed", 242, 230, 250, 322, M, 500, WHITE, "Texto", align="center", case="none",
            anim=("fade", 45, 0.02, 0.3))
    s.words("stay wild and untamed", 242, 262, 282, 298, M, 500, WHITE, "Texto 2", align="center", case="none",
            anim=("fade", 51, 0.02, 0.3))
    s.frame_line("Recuadro", WHITE, (165, 777, 321, 829), 3, 27, 24, clockwise=True)
    s.words("# amazing", 243, 792, 812, 134, M, 600, WHITE, "Hashtag", align="center", case="none",
            anim=("fade", 33, 0.05, 0.2, "random"))
    return finish(t)


def stylish():
    """White story: a photo sweeps in from the right; a black frame line, a blue half disc, an orange label with
    #stylish, the number, two dots and a line of upright text come in."""
    t, s = story("stylish", "Historia: #stylish con disco azul", "Story: #stylish with a blue disc", 15420, 2.0,
                 ["foto", "moda", "azul", "naranja"])
    s.box("Barra", BLACK, lambda fr: (86, lerp(864, 79, ease(fr, 36, 15)), 103, 864))
    s.box("Barra 2", BLACK, lambda fr: (86, 79, lerp(86, 189, ease(fr, 45, 9)), 96))
    s.box("Disco", "#0A66F0", lambda fr: (lambda r: (198 - r, 607 - r, 198 + r, 607 + r))(max(0.5, 193 * ease(fr, 36, 15))),
          kind="ellipse")
    s.photo("Foto", "y5-outfit-03", (189, 0, 486, 864), win=lambda fr: (lerp(486, 189, ease(fr, 3, 27)), 0, 486, 864),
            zoom=zoom_out(1.1, 0, 40))
    for i, (cy, colour) in enumerate(((62, "#FF5A1F"), (130, "#0A66F0"))):
        s.box(f"Punto {i + 1}", colour, lambda fr, cy=cy, i=i: (lambda r: (428 - r, cy - r, 428 + r, cy + r))(
            max(0.3, 11 * ease(fr, 39 + 3 * i, 6))), kind="ellipse")
    s.box("Etiqueta", "#FF5A1F", grow_x((55, 509, 311, 606), 36, 12))
    s.words("#stylish", 185, 532, 580, 224, M, 700, WHITE, "Hashtag", align="center", case="none",
            anim=("fade", 39, 0.05, 0.2, "random"))
    s.words("0256", 258, 619, 654, 112, M, 700, BLACK, "Número", align="center", anim=("fade", 42, 0.08, 0.2, "random"))
    s.words("YOU ARE THE ARTIST", 53, 163, 176, 175, M, 400, BLACK, "Texto", align="center", rot=90,
            anim=("typewriter", 36, 0.04, 0.05))
    s.words("OF YOUR LIFE", 30, 132, 145, 112, M, 400, BLACK, "Texto 2", align="center", rot=90,
            anim=("typewriter", 42, 0.04, 0.05))
    return finish(t)


# =====================================================================================================================
# s08 (26.11-29.54 s)
# =====================================================================================================================

def style_beautiful():
    """A photo; a pink diagonal rises at the foot with a black label for #beautiful, then yellow, red and dark bands
    drop at the top and STYLE fades in."""
    t, s = story("style-beautiful", "Historia: STYLE #beautiful con franjas", "Story: STYLE #beautiful with bands",
                 15421, 2.6, ["foto", "moda", "franjas"])
    s.photo("Foto", "y5-outfit-03", (0, 0, 486, 864), matte=False, zoom=zoom_out(1.1, 0, 60))
    s.poly("Rosa", "#DA9A8C", [(0, 740), (486, 654), (486, 870), (0, 870)], off=slide(0, 230, 42, 15))
    s.box("Etiqueta", BLACK, grow_x((101, 735, 385, 813), 48, 9))
    s.words("#beautiful", 243, 750, 790, 248, M, 700, WHITE, "Hashtag", align="center", case="none",
            anim=("fade", 48, 0.05, 0.2, "random"))
    for i, (colour, pts, at) in enumerate((("#FFB400", [(0, 87), (486, 164), (486, 192), (0, 114)], 51),
                                           ("#C13A1E", [(0, 62), (486, 142), (486, 166), (0, 89)], 53),
                                           ("#2A2E22", [(0, -5), (486, -5), (486, 144), (0, 64)], 55))):
        s.poly(["Franja amarilla", "Franja roja", "Franja oscura"][i], colour, pts, off=slide(0, -200, at, 12))
    s.words("STYLE", 243, 58, 94, 146, M, 800, WHITE, "Título", align="center", anim=("fade", 63, 0.05, 0.2, "random"))
    return finish(t)


def ocean():
    """Aerial sea; a thick white frame swings round into place in 3D, OCEAN HAPPY RELAX fades in pale blue and
    turns white."""
    t, s = story("ocean", "Historia: OCEAN HAPPY RELAX con marco", "Story: OCEAN HAPPY RELAX with a frame", 15422, 2.2,
                 ["foto", "mar", "marco", "verano"])
    s.photo("Foto", "h-beach-01", (0, 0, 486, 864), matte=False, zoom=zoom_out(1.1, 0, 60))
    fr_ = s.outline_box("Marco", WHITE, 23, (52.5, 149.5, 432.5, 714.5), op=lambda fr: ease(fr, 18, 3))
    s.d3(fr_, ry=lambda fr, u: 88 * (1 - ease(fr, 18, 18)), persp=1400)
    s.mblur(fr_)
    for i, (word, top, bot, x0, x1) in enumerate((("OCEAN", 316, 369, 101, 387), ("HAPPY", 405, 459, 111, 379),
                                                   ("RELAX", 494, 548, 114, 376))):
        s.words(word, 243, top, bot, x1 - x0, M, 700, "#5BD3F5", f"Título {i + 1} (azul)", align="center",
                anim=("fade", 33 + 3 * i, 0.05, 0.3))
        s.words(word, 243, top, bot, x1 - x0, M, 700, WHITE, f"Título {i + 1}", align="center",
                op=lambda fr, i=i: ease(fr, 57 + 2 * i, 9))
    return finish(t)


def abstract():
    """A navy gradient; a geometric photo rises in on a slant, a white diagonal with a thin white stripe rises over
    its foot, ABSTRACT and GEOMETRIC STYLE gather letter by letter."""
    t, s = story("abstract", "Historia: ABSTRACT GEOMETRIC STYLE", "Story: ABSTRACT GEOMETRIC STYLE", 15423, 2.6,
                 ["foto", "geométrico", "arquitectura"])
    s.box("Degradado", [gradient([(0.0, "#7E98AE"), (1.0, "#0D3558")], angle=90), no_stroke()], (-5, -5, 491, 869))
    s.photo("Foto", "city-03", (0, 0, 486, 864), win=lambda fr: (0, lerp(864, 0, ease(fr, 3, 45)), 486, 864),
            look=[effect("color.basic", saturation=-0.6)])
    rise = slide(0, 420, 45, 15)
    s.poly("Raya", WHITE, [(0, 627), (486, 484), (486, 507), (0, 652)], off=rise)
    s.poly("Blanco", WHITE, [(0, 682), (486, 540), (486, 870), (0, 870)], off=rise)
    s.words("ABSTRACT", 92, 718, 757, 304, M, 800, "#0E2C48", "Título", anim=("ibs-scatter-gather", 54, 0.03, 0.5,
                                                                              "random"))
    s.words("GEOMETRIC STYLE", 92, 771, 797, 302, M, 400, "#36506A", "Texto", anim=("fade", 60, 0.03, 0.3, "random"))
    return finish(t)


# =====================================================================================================================
# s09 (29.54-32.10 s)
# =====================================================================================================================

def sale75():
    """A photo goes pale grey outside a colour window that closes in; two red labels grow, SALE from the left and
    UP TO 75% OFF from the right."""
    t, s = story("sale75", "Historia: SALE UP TO 75% OFF", "Story: SALE UP TO 75% OFF", 15424, 1.8,
                 ["foto", "rebajas", "oferta", "rojo"])
    full = (0, 0, 486, 864)
    first = s.photo("Foto", "y5-outfit-05", full, matte=False, look=BW)
    s.box("Velo", solid(WHITE, 0.3), full)
    s.photo("Foto (color)", "y5-outfit-05", full, reuse=first["placeholderId"],
            win=lambda fr: lerp_rect(full, (51, 47, 435, 817), ease(fr, 3, 24)))
    red = "#FF2E12"
    s.box("Etiqueta", red, grow_x((0, 514, 341, 649), 30, 12))
    s.words("SALE", 24, 544, 625, 292, "Archivo Black", 400, WHITE, "Título", anim=("fade", 33, 0.06, 0.2))
    s.box("Etiqueta 2", red, grow_x((143, 695, 486, 762), 33, 12, from_right=True))
    s.words("UP TO 75% OFF", 473, 714, 744, 310, M, 800, WHITE, "Texto", align="right",
            anim=("fade", 36, 0.04, 0.2, "backward"))
    return finish(t)


def glam():
    """Black story: a pink block opens from a line on the left, a photo slides in from the right over its corner;
    GLAM ROCK fades in from the right and a line of upright text types."""
    t, s = story("glam", "Historia: GLAM ROCK en rosa y negro", "Story: GLAM ROCK in pink and black", 15425, 2.4,
                 ["foto", "moda", "rosa", "negro"], ground=BLACK)
    s.box("Bloque", "#FF3B6E", lambda fr: (34, 302, lerp(36, 406, ease(fr, 3, 15)), 822), op=lambda fr: ease(fr, 2, 2))
    s.photo("Foto", "fx-hair-02", (135, 35, 451, 597), off=slide(360, 0, 6, 18))
    s.words("GLAM", 384, 627, 710, 216, "Bebas Neue", 400, WHITE, "Título", align="right",
            anim=("fade", 51, 0.06, 0.25, "backward"))
    s.words("ROCK", 383, 722, 764, 97, "Bebas Neue", 400, WHITE, "Título 2", align="right",
            anim=("fade", 54, 0.06, 0.25, "backward"))
    s.words("YOU ARE PART OF STYLISH MOVEMENT", 101, 145, 159, 230, "Bebas Neue", 400, WHITE, "Texto", align="center",
            rot=-90, anim=("typewriter", 51, 0.03, 0.05))
    return finish(t)


def summer_event():
    """A beach photo; a purple triangle slides into the top corner and an orange arrow pops up; the date types with
    a hashtag in an outline, summer event fades in."""
    t, s = story("summer-event", "Historia: summer event con fecha", "Story: summer event with a date", 15426, 2.0,
                 ["foto", "verano", "evento", "playa"])
    s.photo("Foto", "fx-beach-02", (0, 0, 486, 864), matte=False, zoom=zoom_out(1.08, 0, 60))
    s.poly("Triángulo", solid("#5A2A8A", 0.92), [(96, 0), (486, 0), (486, 334)], off=slide(300, -200, 6, 21))
    s.poly("Flecha", solid("#F07A10", 0.88), [(88, 490), (328, 382), (345, 582)],
           sc=lambda fr: max(0.01, ease(fr, 15, 12)))
    s.words("02.06", 453, 37, 85, 203, M, 800, WHITE, "Fecha", align="right", anim=("fade", 36, 0.06, 0.2))
    s.frame_line("Recuadro", WHITE, (288, 97, 450, 137), 3, 27, 21)
    s.words("# meeting", 369, 104, 127, 128, M, 700, WHITE, "Hashtag", align="center", case="none",
            anim=("fade", 33, 0.04, 0.2, "backward"))
    s.words("summer", 243, 407, 457, 360, M, 900, WHITE, "Título", align="center", case="none",
            anim=("fade", 36, 0.05, 0.25))
    s.words("event", 242, 470, 508, 164, M, 300, WHITE, "Título 2", align="center", case="none",
            anim=("fade", 39, 0.05, 0.25))
    return finish(t)


# =====================================================================================================================
# s10 (32.10-35.13 s)
# =====================================================================================================================

def masterpiece():
    """Sky blue story: a photo wipes down over it, MAKE EACH DAY YOUR MASTERPIECE fades in with a white rule, the
    second line types and a white outline draws round BEAUTIFUL."""
    t, s = story("masterpiece", "Historia: MAKE EACH DAY YOUR MASTERPIECE", "Story: MAKE EACH DAY YOUR MASTERPIECE",
                 15427, 2.0, ["foto", "frase", "rosa", "motivación"], ground="#7DD6F0")
    s.photo("Foto", "spring-01", (0, 0, 486, 864), win=lambda fr: (0, 0, 486, lerp(0, 864, ease(fr, 0, 45))),
            zoom=zoom_out(1.08, 0, 60))
    for i, (word, top, bot, x0, x1) in enumerate((("MAKE EACH", 190, 220, 118, 366), ("DAY YOUR", 238, 268, 129, 343),
                                                   ("MASTERPIECE", 284, 314, 94, 391))):
        s.words(word, 243, top, bot, x1 - x0, M, 700, WHITE, f"Título {i + 1}", align="center",
                anim=("fade", 33 + 3 * i, 0.03, 0.2))
    s.box("Línea", WHITE, lambda fr: (243 - 153 * ease(fr, 33, 6), 347, 243 + 153 * ease(fr, 33, 6), 354))
    s.words("DREAM BIG. BE CREATIVE", 242, 389, 408, 323, M, 700, WHITE, "Texto", align="center",
            anim=("typewriter", 36, 0.03, 0.05))
    s.frame_line("Recuadro", WHITE, (94.5, 710.5, 394.5, 802.5), 5, 27, 24)
    s.words("BEAUTIFUL", 243, 738, 775, 254, M, 800, WHITE, "Hashtag", align="center",
            anim=("fade", 30, 0.05, 0.2, "backward"))
    return finish(t)


def sale40():
    """White and photo halves: a red block opens from the left edge, the photo slides in from the right; SALE and
    40% read down the white column, letter by letter."""
    t, s = story("sale40", "Historia: SALE 40% en vertical", "Story: upright SALE 40%", 15428, 1.8,
                 ["foto", "rebajas", "oferta", "rojo"])
    s.photo("Foto", "fx-woman-05", (189, 0, 486, 864), off=slide(300, 0, 6, 21))
    s.box("Bloque", "#FF2E12", lambda fr: (0, 0, max(0.5, 173 * ease(fr, 6, 21)), 435))
    s.words("SALE", 85, 162, 270, 368, "Archivo Black", 400, WHITE, "Título", align="center", rot=90,
            anim=("fade", 33, 0.06, 0.25))
    s.words("40%", 86, 599, 705, 346, "Archivo Black", 400, BLACK, "Número", align="center", rot=90,
            anim=("fade", 36, 0.06, 0.3))
    return finish(t)


def life_good():
    """Dark story: five windows of one photo open as purple and red blocks slide down out of them; a red and purple
    bar sweeps the last window and LIFE IS SO GOOD JUST BE YOURSELF types in."""
    t, s = story("life-good", "Historia: LIFE IS SO GOOD JUST BE YOURSELF", "Story: LIFE IS SO GOOD JUST BE YOURSELF",
                 15429, 1.8, ["foto", "frase", "neón", "cuadrícula"], ground="#191919")
    cells = [((20, 47, 234, 279), 0), ((251, 47, 468, 279), 0), ((20, 297, 234, 569), 1),
             ((20, 587, 234, 817), 2), ((251, 587, 468, 817), 2)]
    first = None
    for i, (r, row) in enumerate(cells):
        c = s.photo(f"Foto {i + 1}" if i else "Foto", "fx-hair-01", (20, 47, 468, 817), win=r,
                    reuse=first["placeholderId"] if first else None)
        first = first or c
        x0, y0, x1, y1 = r
        at = 3 * row

        def top(fr, y0=y0, y1=y1, at=at):
            return lerp(y0, y1, ease(fr, at, 21))

        def mid(fr, y0=y0, y1=y1, at=at):
            return lerp((y0 + y1) / 2, y1, ease(fr, at, 21))
        s.box(f"Tapa morada {i + 1}", "#6E3BFF", lambda fr, x0=x0, x1=x1, top=top, mid=mid: (x0, top(fr), x1, mid(fr)))
        s.box(f"Tapa roja {i + 1}", "#FF3355", lambda fr, x0=x0, x1=x1, y1=y1, mid=mid: (x0, mid(fr), x1, y1))
    for colour, d in (("#6E3BFF", 14), ("#FF3355", 0)):
        s.box("Barrido", colour, lambda fr, d=d: (lambda x: (x - 26 + d, 297, x + d, 569))(lerp(468, 250, ease(fr, 27, 15))),
              op=lambda fr: ease(fr, 27, 1) * (1 - ease(fr, 42, 3)))
    for i, (word, top_, bot, w) in enumerate((("LIFE IS", 324, 368, 120), ("SO GOOD", 382, 426, 155),
                                              ("JUST BE", 439, 483, 147), ("YOURSELF", 496, 540, 194))):
        s.words(word, 468, top_, bot, w, "Bebas Neue", 400, WHITE, f"Frase {i + 1}", align="right",
                anim=("typewriter", 33 + 3 * i, 0.04, 0.05))
    return finish(t)


# =====================================================================================================================
# s11 (35.13-38.16 s)
# =====================================================================================================================

def red_tone():
    return [effect("duotone", strength=1.0, shadowColor="#1A0400", highlightColor="#FF3A12")]


def cold_wave():
    """A wave photo; white sweeps in from the left over two thirds of it, COLD WAVE WARM SUN fades in letter by
    letter filled with the photo, the hashtag types at the top."""
    t, s = story("cold-wave", "Historia: COLD WAVE WARM SUN con letras de foto", "Story: COLD WAVE WARM SUN with photo letters",
                 15430, 2.0, ["foto", "mar", "tipografía"])
    full = (0, 0, 486, 864)
    s.photo("Foto", "y5-h-ocean-02", full, matte=False, zoom=zoom_out(1.08, 0, 60))
    s.box("Blanco", WHITE, lambda fr: (-5, -5, 301 * ease(fr, 18, 12), 869))
    pid = None
    for i, (word, top, bot, w) in enumerate((("COLD", 268, 354, 201), ("WAVE", 368, 454, 216),
                                             ("WARM", 468, 556, 251), ("SUN", 570, 658, 159))):
        fill_ = s.photo(f"Foto en letras {i + 1}", "fx-beach-04", full, matte=False, label="Foto de las letras",
                        reuse=pid)
        pid = pid or fill_["placeholderId"]
        w_ = s.words(word, 24, top, bot, w, "Bebas Neue", 400, WHITE, f"Título {i + 1}",
                     anim=("fade", 30 + 4 * i, 0.05, 0.25))
        fill_["matte"] = {"clip": w_["id"], "mode": "alpha"}
    s.words("#PARADISEFOUND", 23, 37, 55, 158, "Bebas Neue", 400, BLACK, "Hashtag", anim=("typewriter", 33, 0.03, 0.05))
    return finish(t)


def employee():
    """A navy panel slides down to a teal band while a round portrait drops in; BEST EMPLOYEE OF THE MONTH fades
    in line by line, the name and hashtag type."""
    t, s = story("employee", "Historia: BEST EMPLOYEE OF THE MONTH", "Story: BEST EMPLOYEE OF THE MONTH", 15431, 2.4,
                 ["foto", "empresa", "empleado", "retrato"])
    s.box("Verde", "#2A6B70", lambda fr: (-5, lerp(130, 493, ease(fr, 12, 33)), 491, 869))
    s.box("Azul", "#0F2A45", lambda fr: (-5, lerp(-5, 869, ease(fr, 9, 48)), 491, 869))
    s.photo("Foto", "portrait-04", (63, 310, 423, 670), kind="ellipse", off=slide(0, -560, 3, 24))
    for i, (word, top, bot, x0, x1) in enumerate((("BEST", 64, 103, 165, 319), ("EMPLOYEE", 119, 158, 78, 407),
                                                   ("OF THE", 174, 212, 124, 343), ("MONTH", 228, 267, 124, 360))):
        s.words(word, 243, top, bot, x1 - x0, AR, 900, BLACK, f"Título {i + 1}", align="center",
                anim=("fade", 51 + 3 * i, 0.03, 0.3))
    s.words("MELISSA JOHNSON", 242, 719, 744, 343, M, 700, WHITE, "Nombre", align="center",
            anim=("typewriter", 54, 0.03, 0.05))
    s.words("# thebestworker", 243, 792, 819, 280, M, 300, "#183040", "Hashtag", align="center", case="none",
            italic=True, anim=("typewriter", 57, 0.03, 0.05))
    return finish(t)


def never_easier():
    """Three red-toned photo columns grow up from a line, a black rule opens from the centre and IT NEVER GETS
    EASIER, YOU JUST GET BETTER fades up in red."""
    t, s = story("never-easier", "Historia: IT NEVER GETS EASIER en rojo", "Story: red IT NEVER GETS EASIER", 15432, 2.0,
                 ["foto", "gimnasio", "motivación", "rojo"])
    for i, (sample, x0, x1, at) in enumerate((("y2b-fit-01", 23, 157, 3), ("y2b-fit-02", 176, 310, 0),
                                              ("y2b-fit-03", 329, 464, 6))):
        s.photo(f"Foto {i + 1}", sample, (x0, 22, x1, 425), look=red_tone(), label=f"Foto {i + 1}",
                win=lambda fr, x0=x0, x1=x1, at=at: (x0, lerp(425, 22, ease(fr, at, 24)), x1, 425))
    s.box("Línea", BLACK, lambda fr: (243 - 221 * ease(fr, 30, 12), 482, 243 + 221 * ease(fr, 30, 12), 490))
    red = "#F5321E"
    for i, (word, top, bot, x0, x1) in enumerate((("IT NEVER", 542, 579, 120, 364), ("GETS EASIER,", 589, 627, 58, 428),
                                                   ("YOU JUST", 635, 673, 111, 374), ("GET BETTER", 682, 720, 78, 407))):
        s.words(word, 243, top, bot, x1 - x0, M, 800, red, f"Frase {i + 1}", align="center",
                anim=("fade-up-char", 33 + 3 * i, 0.02, 0.3))
    s.words("DON'T STOP UNTIL YOU WIN", 242, 784, 801, 303, M, 700, BLACK, "Texto", align="center",
            anim=("typewriter", 36, 0.03, 0.05))
    return finish(t)


# =====================================================================================================================
# s12 (38.16-41.49 s)
# =====================================================================================================================

def sunshine_tag():
    """White story: a photo rises with an arched top that straightens, a navy label drops from the top and the
    hashtag and its line type in."""
    t, s = story("sunshine-tag", "Historia: #sunshine Relaxing holiday", "Story: #sunshine Relaxing holiday", 15433,
                 2.2, ["foto", "verano", "azul"])
    s.photo("Foto", "y5-outfit-07", (24, 63, 461, 840), radius=218.5,
            win=lambda fr: (24, lerp(840, 63, ease(fr, 9, 21)), 461, 1280))
    s.box("Etiqueta", "#172390", lambda fr: (71, -5, 415, lerp(-5, 130, ease(fr, 21, 9))))
    s.words("#sunshine", 243, 25, 68, 295, M, 700, WHITE, "Hashtag", align="center", case="none",
            anim=("typewriter", 48, 0.05, 0.05))
    s.words("Relaxing holiday", 242, 84, 109, 227, M, 500, WHITE, "Texto", align="center", case="none",
            anim=("typewriter", 57, 0.04, 0.05))
    return finish(t)


def shopping_week():
    """White story: a navy block grows down from a line, a grey photo rises under it and a second block opens
    below; #shoppingweek types, 40% and FOR SALE fade in."""
    t, s = story("shopping-week", "Historia: #shoppingweek 40% FOR SALE", "Story: #shoppingweek 40% FOR SALE", 15434,
                 2.4, ["foto", "rebajas", "compras", "azul"])
    navy = "#10174A"
    s.box("Bloque", navy, lambda fr: (59, 59, 426, lerp(60, 147, ease(fr, 3, 12))))
    s.box("Bloque 2", navy, lambda fr: (59, 575, 426, lerp(576, 804, ease(fr, 15, 12))))
    s.photo("Foto", "shopping-03", (30, 148, 456, 575), look=BW,
            win=lambda fr: (30, lerp(575, 148, ease(fr, 6, 21)), 456, 575))
    s.words("#shoppingweek", 242, 88, 117, 258, M, 400, WHITE, "Hashtag", align="center", case="none",
            anim=("typewriter", 54, 0.04, 0.05))
    s.words("40%", 241, 638, 739, 322, M, 800, "#F2272E", "Número", align="center", anim=("fade", 54, 0.08, 0.3))
    s.words("FOR SALE", 241, 672, 707, 215, M, 700, WHITE, "Texto", align="center", anim=("fade", 57, 0.04, 0.2))
    return finish(t)


def summer_look():
    """Two photos and two colour bands drop in one after another; Summer look, #fashion and their lines fade in."""
    t, s = story("summer-look", "Historia: Summer look #fashion en franjas", "Story: Summer look #fashion in bands",
                 15435, 2.2, ["foto", "moda", "verano", "beige"])
    s.photo("Foto 1", "y6-flatlay-02", (0, 0, 486, 207), off=slide(0, -220, 0, 15), label="Foto 1")
    s.box("Gris", "#ABACB0", grow_y((0, 219, 486, 424), 12, 9))
    s.photo("Foto 2", "y6-flatlay-05", (0, 438, 486, 644), win=lambda fr: (0, 438, 486, lerp(438, 644, ease(fr, 21, 6))),
            label="Foto 2")
    s.box("Beige", "#D2AC7E", grow_y((0, 658, 486, 869), 27, 6))
    s.words("Summer look", 242, 275, 325, 442, PF, 700, "#B07A3C", "Título", align="center", case="none",
            anim=("fade", 48, 0.05, 0.25))
    s.words("collections", 242, 345, 368, 171, M, 500, "#5A5A5A", "Texto", align="center", case="none",
            anim=("fade", 51, 0.04, 0.25))
    s.words("#fashion", 242, 692, 742, 282, PF, 700, WHITE, "Hashtag", align="center", case="none",
            anim=("fade", 48, 0.05, 0.25))
    s.words("Stylish weekend", 243, 758, 785, 260, M, 500, WHITE, "Texto 2", align="center", case="none",
            anim=("fade", 51, 0.04, 0.25))
    s.words("in Milan", 248, 794, 821, 124, M, 500, WHITE, "Texto 3", align="center", case="none",
            anim=("fade", 54, 0.04, 0.25))
    return finish(t)


# =====================================================================================================================
# s13 (41.49-45.32 s)
# =====================================================================================================================

def stylish_confident():
    """White story: three windows of one photo open sideways in turn; the number and STYLISH & CONFIDENT type in
    orange with wide letter spacing."""
    t, s = story("confident", "Historia: STYLISH & CONFIDENT en tres ventanas",
                 "Story: STYLISH & CONFIDENT in three windows", 15436, 2.6, ["foto", "moda", "hombre"])
    full = (22, 38, 464, 825)
    pid = None
    for i, (r, at, right) in enumerate((((22, 38, 464, 239), 6, False), ((50, 258, 464, 607), 9, True),
                                        ((22, 623, 464, 825), 3, False))):
        c = s.photo(f"Foto {i + 1}" if i else "Foto", "man-02", full, reuse=pid,
                    win=grow_x(r, at, 21, from_right=right))
        pid = pid or c["placeholderId"]
    orange = "#E8541C"
    s.words("259", 440, 64, 86, 60, OS, 500, orange, "Número", align="right", spacing=0.6,
            anim=("typewriter", 57, 0.08, 0.05))
    s.words("STYLISH", 50, 743, 763, 149, OS, 500, orange, "Texto", spacing=0.6, anim=("typewriter", 54, 0.05, 0.05))
    s.words("& CONFIDENT", 50, 777, 797, 235, OS, 500, orange, "Texto 2", spacing=0.6,
            anim=("typewriter", 60, 0.04, 0.05))
    return finish(t)


def street_fast():
    """A grey photo; two boxes sweep in from the right behind a yellow and a black edge, one darker and one tinted
    yellow; 10/25 #youth and street FAST fade in from the right."""
    t, s = story("street-fast", "Historia: 10/25 #youth street FAST", "Story: 10/25 #youth street FAST", 15437, 2.0,
                 ["foto", "calle", "skate", "amarillo"])
    s.photo("Foto", "y5-street-04", (0, 0, 486, 864), matte=False, look=BW, zoom=zoom_out(1.08, 0, 60))
    edge = lambda fr: lerp(430, 58, ease(fr, 3, 24))  # noqa: E731
    s.box("Caja oscura", solid(BLACK, 0.45), lambda fr: (edge(fr), 72, 430, 395))
    tint = s.box("Caja amarilla", solid("#E6E21C", 0.8), lambda fr: (edge(fr), 458, 430, 781))
    tint["blendMode"] = "multiply"
    s.box("Borde amarillo", "#F5C400", lambda fr: (edge(fr) - 14, 72, edge(fr), 395),
          op=lambda fr: ease(fr, 3, 2) * (1 - ease(fr, 27, 3)))
    s.box("Borde negro", BLACK, lambda fr: (edge(fr) - 14, 458, edge(fr), 781),
          op=lambda fr: ease(fr, 3, 2) * (1 - ease(fr, 27, 3)))
    yellow = "#F1EA2F"
    s.words("10/25", 91, 164, 232, 302, "Archivo Black", 400, yellow, "Fecha", anim=("fade", 33, 0.05, 0.2, "backward"))
    s.words("#youth", 91, 252, 310, 305, "Archivo Black", 400, yellow, "Hashtag", case="none",
            anim=("fade", 33, 0.05, 0.2, "backward"))
    s.words("street", 89, 532, 596, 306, "Archivo Black", 400, "#111111", "Título", case="none",
            anim=("fade", 33, 0.05, 0.2, "backward"))
    s.words("FAST", 91, 612, 692, 307, "Archivo Black", 400, "#111111", "Título 2",
            anim=("fade", 36, 0.05, 0.2, "backward"))
    return finish(t)


def culinary():
    """A tan curtain led by pink and green bands slides away over a food photo while a white frame draws round the
    story; an orange box opens, its outline draws and CULINARY ART and a quote fade in."""
    t, s = story("culinary", "Historia: CULINARY ART #cooking", "Story: CULINARY ART #cooking", 15438, 2.8,
                 ["foto", "cocina", "comida", "naranja"])
    s.photo("Foto", "cooking-03", (0, 0, 486, 864), matte=False, zoom=zoom_out(1.06, 0, 60))
    cut = lambda fr: lerp(869, -5, ease(fr, 3, 33))  # noqa: E731
    s.box("Cortina", "#B8955A", lambda fr: (-5, -5, 491, cut(fr)))
    s.box("Banda rosa", "#FF7A8A", lambda fr: (-5, cut(fr), 491, cut(fr) + 22), op=lambda fr: 1 - ease(fr, 33, 3))
    s.box("Banda verde", "#7CBF2A", lambda fr: (-5, cut(fr) + 22, 491, cut(fr) + 44), op=lambda fr: 1 - ease(fr, 33, 3))
    s.frame_line("Marco", WHITE, (20, 20, 466, 843), 8, 3, 27)
    s.box("Caja", solid("#F58A3A", 0.88), lambda fr: (101, 102, lerp(101, 384, ease(fr, 51, 9)), 390),
          op=lambda fr: ease(fr, 51, 2))
    s.frame_line("Recuadro", WHITE, (93, 93, 393, 399), 8, 66, 15)
    s.words("CULINARY", 242, 179, 213, 244, M, 800, WHITE, "Título", align="center", anim=("fade", 69, 0.04, 0.2))
    s.words("ART", 242, 219, 253, 94, M, 800, WHITE, "Título 2", align="center", anim=("fade", 75, 0.04, 0.2))
    for i, (line, x0, x1) in enumerate((("Cookery requires instinct", 113, 371), ("and taste rather than", 132, 352),
                                        ("exact measurements", 134, 350))):
        s.words(line, 242, 293 + 19 * i, 305 + 19 * i, x1 - x0, M, 500, WHITE, f"Frase {i + 1}", align="center",
                case="none", anim=("fade", 72 + 3 * i, 0.02, 0.2))
    s.words("#cooking", 242, 782, 807, 158, M, 500, WHITE, "Hashtag", align="center", case="none",
            anim=("fade", 75, 0.04, 0.2))
    return finish(t)


# =====================================================================================================================
# s14 (45.32-49.18 s)
# =====================================================================================================================

def natural_beauty():
    """A green panel parts to the sides over white while three photo columns open from their centres; NATURAL
    BEAUTY types over a line that opens from the centre."""
    t, s = story("natural", "Historia: NATURAL BEAUTY en tres columnas", "Story: NATURAL BEAUTY in three columns",
                 15439, 2.0, ["foto", "naturaleza", "columnas"])
    for i, (sample, x0, x1, at) in enumerate((("fx-nature-04", 20, 155, 9), ("spa-03", 175, 310, 3),
                                              ("h-beach-04", 331, 464, 15))):
        cx = (x0 + x1) / 2
        s.photo(f"Foto {i + 1}", sample, (x0, 20, x1, 740), label=f"Foto {i + 1}",
                win=lambda fr, x0=x0, x1=x1, cx=cx, at=at: (lerp(cx, x0, ease(fr, at, 12)), 20,
                                                             lerp(cx, x1, ease(fr, at, 12)), 740))
    green = "#5E8045"
    s.box("Verde", green, lambda fr: (-5, -5, max(-4.0, 243 - 250 * ease(fr, 0, 27)), 869))
    s.box("Verde 2", green, lambda fr: (min(490.0, 243 + 250 * ease(fr, 0, 27)), -5, 491, 869))
    s.words("NATURAL BEAUTY", 243, 772, 799, 309, M, 400, BLACK, "Título", align="center",
            anim=("typewriter", 42, 0.04, 0.05))
    s.box("Línea", BLACK, lambda fr: (243 - 155 * ease(fr, 42, 12), 822, 243 + 155 * ease(fr, 42, 12), 825))
    return finish(t)


def enjoy_music():
    """A grey photo; blue and red halves open from the centre leaving a round window of the photo; the title fades
    in from both sides and two white labels slide out with #INSTA and #DANCING."""
    t, s = story("enjoy-music", "Historia: ENJOY MY MUSIC en azul y rojo", "Story: blue and red ENJOY MY MUSIC", 15440,
                 2.0, ["foto", "música", "baile", "azul", "rojo"])
    full = (0, 0, 486, 864)
    first = s.photo("Foto", "dance-02", full, matte=False, look=BW)
    s.box("Azul", solid("#1E78D8", 0.9), lambda fr: (243 - 248 * ease(fr, 9, 18), -5, 243, 869))
    s.box("Rojo", solid("#E8283C", 0.9), lambda fr: (243, -5, 243 + 248 * ease(fr, 9, 18), 869))
    s.photo("Foto (círculo)", "dance-02", full, reuse=first["placeholderId"], look=BW, kind="ellipse",
            win=lambda fr: (lambda r: (243 - r, 432 - r, 243 + r, 432 + r))(lerp(30, 195, ease(fr, 12, 18))))
    s.words("expression", 243, 52, 80, 180, M, 400, "#111111", "Texto", align="center", case="none",
            anim=("fade", 36, 0.04, 0.2, "random"))
    s.words("ENJOY", 243, 114, 156, 189, M, 700, WHITE, "Título", align="center", anim=("fade", 36, 0.04, 0.25))
    s.words("MY MUSIC", 243, 169, 210, 314, M, 700, WHITE, "Título 2", align="center",
            anim=("fade", 39, 0.04, 0.25, "backward"))
    s.box("Etiqueta", WHITE, grow_x((0, 596, 265, 662), 33, 12))
    s.box("Etiqueta 2", WHITE, grow_x((0, 696, 383, 762), 33, 15))
    red = "#E8283C"
    s.words("#INSTA", 29, 609, 649, 221, M, 800, red, "Hashtag", anim=("fade", 48, 0.04, 0.2))
    s.words("#DANCING", 29, 709, 749, 329, M, 800, red, "Hashtag 2", anim=("fade", 48, 0.04, 0.2))
    return finish(t)


def fitness_body():
    """A dark photo; two purple-to-blue waves slide in from the top and the bottom with small triangle and cross
    marks; FITNESS BODY and ENERGY WORKOUT fade in letter by letter."""
    t, s = story("fitness", "Historia: FITNESS BODY ENERGY WORKOUT", "Story: FITNESS BODY ENERGY WORKOUT", 15441, 2.4,
                 ["foto", "gimnasio", "deporte", "degradado"])
    s.photo("Foto", "dance-03", (0, 0, 486, 864), matte=False, zoom=zoom_out(1.08, 0, 60))
    g = [gradient([(0.0, "#A85CF0"), (1.0, "#4C8EF0")], angle=30), no_stroke()]
    top = [(0, -5), (486, -5), (486, 322), (446, 300), (420, 240), (392, 160), (350, 112), (280, 105), (200, 118),
           (120, 128), (60, 134), (0, 140)]
    bot = [(0, 592), (50, 596), (100, 620), (140, 660), (190, 700), (250, 722), (320, 732), (390, 724), (445, 735),
           (486, 752), (486, 869), (0, 869)]
    s.poly("Ola", g, top, off=slide(0, -340, 6, 18))
    s.poly("Ola 2", g, bot, off=slide(0, 300, 6, 18))
    for i, (x, y, rot) in enumerate(((72, 98, 0), (430, 212, 180), (383, 395, 180), (120, 500, 0), (70, 635, 0),
                                     (395, 783, 90))):
        r = 14
        pts = [(x, y - r), (x + r * 0.87, y + r * 0.5), (x - r * 0.87, y + r * 0.5)]
        if rot == 180:
            pts = [(x, y + r), (x + r * 0.87, y - r * 0.5), (x - r * 0.87, y - r * 0.5)]
        elif rot == 90:
            pts = [(x + r, y), (x - r * 0.5, y + r * 0.87), (x - r * 0.5, y - r * 0.87)]
        bb = bbox(pts)
        s.box(f"Triángulo {i + 1}", ring(WHITE, 1.4 * R), bb, path=path_of(pts, bb), op=lambda fr, i=i: 0.7 * ease(fr, 12 + 2 * i, 6),
              base=(bb[2] - bb[0], bb[3] - bb[1]))
    s.words("FITNESS", 435, 58, 97, 218, M, 800, WHITE, "Título", align="right", anim=("fade", 54, 0.04, 0.2, "random"))
    s.words("BODY", 435, 105, 144, 150, M, 800, WHITE, "Título 2", align="right", anim=("fade", 54, 0.04, 0.2, "random"))
    s.words("ENERGY", 46, 726, 765, 213, M, 800, WHITE, "Título 3", anim=("fade", 57, 0.04, 0.2, "random"))
    s.words("WORKOUT", 46, 775, 814, 285, M, 800, WHITE, "Título 4", anim=("fade", 57, 0.04, 0.2, "random"))
    return finish(t)


# =====================================================================================================================
# s15 (49.18-52.58 s)
# =====================================================================================================================

def blob_pts(cx, cy, rx, ry, seed, n=40, rot=0.0):
    """A soft blob round (cx, cy): an ellipse wobbled by two low harmonics."""
    rng = random.Random(seed)
    a1, a2, p1, p2 = rng.uniform(0.06, 0.14), rng.uniform(0.04, 0.1), rng.uniform(0, 6.28), rng.uniform(0, 6.28)
    out = []
    c, sn = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    for i in range(n):
        th = 2 * math.pi * i / n
        q = 1 + a1 * math.sin(2 * th + p1) + a2 * math.sin(3 * th + p2)
        x, y = rx * q * math.cos(th), ry * q * math.sin(th)
        out.append((cx + x * c - y * sn, cy + x * sn + y * c))
    return out


def plus(s, name, cx, cy, size, colour, op):
    s.box(name, colour, (cx - size / 2, cy - 1.5, cx + size / 2, cy + 1.5), op=op)
    s.box(f"{name} (2)", colour, (cx - 1.5, cy - size / 2, cx + 1.5, cy + size / 2), op=op)


def tri_outline(s, name, cx, cy, r, colour, op, down=True, width=2.0):
    if down:
        pts = [(cx - r * 0.87, cy - r * 0.5), (cx + r * 0.87, cy - r * 0.5), (cx, cy + r)]
    else:
        pts = [(cx, cy - r), (cx + r * 0.87, cy + r * 0.5), (cx - r * 0.87, cy + r * 0.5)]
    bb = bbox(pts)
    s.box(name, ring(colour, width * R), bb, path=path_of(pts, bb), op=op, base=(bb[2] - bb[0], bb[3] - bb[1]))


def double_line(s, name, x0, y0, x1, y1, colour, op, gap=7, width=2.5):
    """Two thin parallel lines from (x0, y0) to (x1, y1)."""
    dx, dy = x1 - x0, y1 - y0
    ln = math.hypot(dx, dy)
    nx, ny = -dy / ln, dx / ln
    for j, off in enumerate((-gap / 2, gap / 2)):
        ox, oy = nx * off, ny * off
        hw = width / 2
        pts = [(x0 + ox - nx * hw, y0 + oy - ny * hw), (x1 + ox - nx * hw, y1 + oy - ny * hw),
               (x1 + ox + nx * hw, y1 + oy + ny * hw), (x0 + ox + nx * hw, y0 + oy + ny * hw)]
        bb = bbox(pts)
        s.box(f"{name} {j + 1}", colour, bb, path=path_of(pts, bb), op=op, base=(bb[2] - bb[0], bb[3] - bb[1]))


def grow_about(bb, q):
    cx, cy = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2
    hw, hh = (bb[2] - bb[0]) / 2 * q, (bb[3] - bb[1]) / 2 * q
    return cx - hw, cy - hh, cx + hw, cy + hh


def insta_music():
    """Black story: two photos in coloured blobs grow out of points with neon double lines, rings, plus signs and
    triangles around them; #instamusic and #yourbeat fade in."""
    t, s = story("instamusic", "Historia: #instamusic #yourbeat con manchas", "Story: #instamusic #yourbeat with blobs",
                 15442, 2.0, ["foto", "música", "neón", "formas"], ground=BLACK)
    groups = (((245, 227), 0, "y7-h-laugh-02",
               (("#FFB400", -45, 20, 120, 95, 3), ("#B5E61D", 60, -25, 70, 60, 4), ("#FF9EB5", 30, 0, 115, 100, 5))),
              ((230, 610), 6, "y7-h-laugh-04",
               (("#E040FB", -60, -10, 95, 110, 6), ("#2020D0", 60, 60, 80, 90, 7), ("#FFB400", 0, 0, 125, 110, 8))))
    for gi, ((cx, cy), at, sample, blobs) in enumerate(groups):
        def grow(fr, at=at):
            return max(0.01, ease(fr, 3 + at, 18))
        for bi, (colour, dx, dy, rx, ry, seed) in enumerate(blobs):
            pts = blob_pts(cx + dx, cy + dy, rx, ry, seed)
            s.poly(f"Mancha {gi + 1}-{bi + 1}", colour, pts, sc=grow,
                   off=lambda fr, dx=dx, dy=dy, g=grow: (-dx * (1 - g(fr)), -dy * (1 - g(fr))))
        pts = blob_pts(cx + 5, cy + 5, 118, 100, 20 + gi)
        bb = bbox(pts)
        s.photo(f"Foto {gi + 1}", sample, bb, path=path_of(pts, bb), label=f"Foto {gi + 1}",
                win=lambda fr, bb=bb, g=grow: grow_about(bb, g(fr)))

    def op(fr):
        return ease(fr, 9, 9)
    double_line(s, "Líneas", 35, 285, 140, 175, "#8C3CFF", op)
    double_line(s, "Líneas 2", 275, 345, 375, 245, "#FF3C8C", op)
    double_line(s, "Líneas 3", 340, 110, 390, 55, "#FF3C5A", op)
    double_line(s, "Líneas 4", 30, 590, 130, 485, "#FFB400", op)
    double_line(s, "Líneas 5", 245, 700, 335, 610, "#FFB400", op)
    double_line(s, "Líneas 6", 395, 550, 450, 495, "#FFB400", op)
    s.box("Aro", ring("#FFB400", 2.5 * R), (165, 24, 195, 54), kind="ellipse", op=op)
    s.box("Aro 2", ring("#A04BFF", 2.5 * R), (413, 271, 443, 301), kind="ellipse", op=op)
    for i, (x, y, c) in enumerate(((44, 92, "#B048F0"), (439, 65, "#FFB400"), (333, 475, "#B048F0"),
                                   (439, 704, "#E040FB"))):
        plus(s, f"Más {i + 1}", x, y, 20, c, op)
    tri_outline(s, "Triángulo", 432, 452, 16, "#FFB400", op)
    tri_outline(s, "Triángulo 2", 67, 780, 16, "#FFB400", op)
    s.words("#instamusic", 29, 370, 414, 401, M, 800, WHITE, "Hashtag", case="none", italic=True,
            anim=("fade", 33, 0.04, 0.2, "random"))
    s.words("#yourbeat", 111, 752, 797, 341, M, 800, WHITE, "Hashtag 2", case="none", italic=True,
            anim=("fade", 36, 0.04, 0.2, "random"))
    return finish(t)


def my_lifestyle():
    """White story: a blue frame opens out of a diagonal, two photos slide in from opposite corners; my lifestyle
    and #followme type in."""
    t, s = story("lifestyle", "Historia: my lifestyle #followme", "Story: my lifestyle #followme", 15443, 2.0,
                 ["foto", "estilo de vida", "azul", "collage"])
    s.box("Marco", "#2A1FE0", lambda fr: grow_about((44, 121, 442, 738), max(0.01, ease(fr, 0, 15))),
          rot=lambda fr: 45 * (1 - ease(fr, 0, 15)))
    s.photo("Foto 1", "y5-grwm-02", (81, 97, 405, 420), off=slide(200, -200, 9, 18), label="Foto 1")
    s.photo("Foto 2", "y5-morning-02", (81, 443, 405, 767), off=slide(-200, 200, 12, 18), label="Foto 2")
    s.words("my lifestyle", 243, 30, 74, 325, M, 800, BLACK, "Título", align="center", case="none",
            anim=("typewriter", 33, 0.05, 0.05))
    s.words("#followme", 243, 794, 829, 237, M, 800, BLACK, "Hashtag", align="center", case="none",
            anim=("typewriter", 36, 0.05, 0.05))
    return finish(t)


def brand_new_day():
    """A photo; coloured triangles fly in and lock into a mosaic down the left side and across the foot; brand new
    day fades in. (The reference spells it brend.)"""
    t, s = story("brand-new-day", "Historia: brand new day con triángulos", "Story: brand new day with triangles",
                 15444, 2.6, ["foto", "triángulos", "geométrico"])
    s.photo("Foto", "y5-street-08", (0, 0, 486, 864), matte=False, zoom=zoom_out(1.08, 0, 60))
    rng = random.Random(11)
    pal = ["#93D3F0", "#A27E58", "#261E1A", "#3F7468"]
    tw, th = 132.0, 122.0
    limits = [70, 140, 210, 330, 480, 520]
    n = 0
    for row in range(6):
        y0 = 257 + th * row
        if y0 > 864:
            break
        for kx in range(-1, 9):
            x0 = kx * tw / 2
            if x0 > limits[row]:
                continue
            if (kx + row) % 2 == 0:
                pts = [(x0, y0 + th), (x0 + tw / 2, y0), (x0 + tw, y0 + th)]
            else:
                pts = [(x0, y0), (x0 + tw, y0), (x0 + tw / 2, y0 + th)]
            at = 6 + rng.uniform(0, 24)
            frm = (rng.uniform(-260, 260), rng.uniform(-300, 120))
            s.poly(f"Triángulo {n + 1}", rng.choice(pal), pts, off=slide(frm[0], frm[1], at, 12),
                   op=lambda fr, at=at: ease(fr, at, 4))
            n += 1
    for i, (pts, c) in enumerate((([(98, 242), (134, 180), (170, 242)], "#93D3F0"),
                                  ([(166, 492), (183, 462), (200, 492)], "#261E1A"),
                                  ([(118, 572), (153, 502), (188, 572)], "#3F7468"),
                                  ([(303, 752), (319, 722), (335, 752)], "#3F7468"),
                                  ([(303, 762), (403, 762), (383, 832)], "#261E1A"))):
        s.poly(f"Triángulo suelto {i + 1}", c, pts, off=slide(0, -120, 12 + 3 * i, 12),
               op=lambda fr, i=i: ease(fr, 12 + 3 * i, 4))
    s.words("brand new", 46, 37, 80, 282, M, 800, WHITE, "Título", case="none", anim=("fade", 54, 0.05, 0.2))
    s.words("day", 46, 102, 137, 99, M, 800, WHITE, "Título 2", case="none", anim=("fade", 63, 0.05, 0.2))
    return finish(t)


# =====================================================================================================================
# s16 (52.58-55.61 s)
# =====================================================================================================================

def simple_life():
    """A navy veil dissolves off a photo, a navy box opens from a line in the centre with a four-line quote and the
    hashtag types at the foot."""
    t, s = story("simplelife", "Historia: When you focus on the good #simplelife",
                 "Story: When you focus on the good #simplelife", 15445, 2.0, ["foto", "frase", "azul"])
    navy = "#2E5580"
    s.photo("Foto", "man-05", (0, 0, 486, 864), matte=False, zoom=zoom_out(1.06, 0, 60))
    s.box("Velo", navy, (-5, -5, 491, 869), op=lambda fr: 1 - ease(fr, 3, 24))
    s.box("Caja", solid(navy, 0.95), lambda fr: (243 - 156 * ease(fr, 33, 9), 82, 243 + 156 * ease(fr, 33, 9), 230),
          op=lambda fr: ease(fr, 33, 2))
    for i, (line, x0, x1, top) in enumerate((("When you focus", 127, 362, 99), ("on the good,", 157, 340, 127),
                                             ("the good", 188, 300, 155), ("gets better.", 164, 333, 183))):
        s.words(line, 243, top, top + 22, x1 - x0, M, 700, WHITE, f"Frase {i + 1}", align="center", case="none",
                anim=("fade", 45 + 3 * i, 0.02, 0.25))
    s.words("#simplelife", 243, 792, 820, 180, M, 700, WHITE, "Hashtag", align="center", case="none",
            anim=("typewriter", 39, 0.05, 0.05))
    return finish(t)


def stripe_pts(l0, l1, r0, r1):
    """A band across the story: its top and bottom at the left edge (l0, l1) and at the right edge (r0, r1)."""
    return [(0, l0), (486, r0), (486, r1), (0, l1)]


def fashion_buy():
    """A blue panel steps away to the right off a grey photo; red and blue slanted bands slide in and two slogans
    type along the red ones."""
    t, s = story("fashion-buy", "Historia: FASHION IS WHAT YOU BUY en franjas", "Story: FASHION IS WHAT YOU BUY on bands",
                 15446, 2.2, ["foto", "moda", "franjas", "rojo", "azul"])
    s.photo("Foto", "fx-hair-01", (0, 0, 486, 864), matte=False, look=BW, zoom=zoom_out(1.06, 0, 60))
    red, blue = "#FF3412", "#0A1ADC"
    for i, (pts, c, at) in enumerate(((stripe_pts(380, 410, 180, 212), red, 18), (stripe_pts(472, 512, 282, 324), blue, 21),
                                      (stripe_pts(582, 614, 382, 412), red, 24), (stripe_pts(672, 712, 480, 522), blue, 27))):
        s.poly(["Franja roja", "Franja azul", "Franja roja 2", "Franja azul 2"][i], c, pts,
               off=slide(500, -205, at, 12))
    s.box("Azul", blue, lambda fr: (lerp(-5, 491, ease(fr, 0, 21)), -5, 491, 869))
    ang = -math.degrees(math.atan2(200, 486))
    s.words("FASHION IS WHAT YOU BUY", 243, 286, 304, 400, OS, 600, WHITE, "Frase", align="center", spacing=0.12,
            rot=ang, anim=("typewriter", 51, 0.04, 0.05))
    s.words("STYLE IS WHAT YOU DO WITH IT", 245, 489, 507, 470, OS, 600, WHITE, "Frase 2", align="center",
            spacing=0.12, rot=ang, anim=("typewriter", 51, 0.04, 0.05))
    return finish(t)


def amazing_dream():
    """Light grey story: two photos flip up into place, Amazing dream and two lines fade in in brown over a rule
    that opens from the centre."""
    t, s = story("amazing-dream", "Historia: Amazing dream con dos fotos", "Story: Amazing dream with two photos",
                 15447, 2.0, ["foto", "frase", "marrón"], ground="#F0F0F0")
    for i, (sample, x0, x1) in enumerate((("tk7-flora-09", 24, 231), ("y5-cozy-03", 256, 463))):
        c = s.photo(f"Foto {i + 1}", sample, (x0, 24, x1, 528), label=f"Foto {i + 1}",
                    win=lambda fr, x0=x0, x1=x1: (x0, lerp(240, 24, ease(fr, 3, 18)), x1, lerp(312, 528, ease(fr, 3, 18))),
                    op=lambda fr: ease(fr, 3, 9))
        s.d3(c, rx=lambda fr, u: 70 * (1 - ease(fr, 3, 18)), persp=1400)
    brown = "#7B5232"
    s.words("Amazing", 244, 557, 600, 314, M, 700, brown, "Título", align="center", case="none",
            anim=("fade", 30, 0.04, 0.3))
    s.words("dream", 256, 637, 689, 233, M, 700, brown, "Título 2", align="center", case="none",
            anim=("fade", 36, 0.04, 0.3))
    s.box("Línea", brown, lambda fr: (243 - 154 * ease(fr, 42, 12), 720, 243 + 154 * ease(fr, 42, 12), 730))
    s.words("EVERYTHING YOU CAN", 243, 762, 783, 308, M, 700, brown, "Texto", align="center", anim=("fade", 33, 0.03, 0.3))
    s.words("IMAGINE IS REAL", 243, 795, 816, 232, M, 700, brown, "Texto 2", align="center", anim=("fade", 39, 0.03, 0.3))
    return finish(t)


# =====================================================================================================================
# s17 (55.61-59.67 s)
# =====================================================================================================================

def thick_line(s, name, pts, width, colour, off=None, op=None):
    """A polyline of `width` panel px through pts, one quad per segment."""
    for j, ((x0, y0), (x1, y1)) in enumerate(zip(pts, pts[1:])):
        dx, dy = x1 - x0, y1 - y0
        ln = math.hypot(dx, dy)
        nx, ny = -dy / ln * width / 2, dx / ln * width / 2
        ex, ey = dx / ln * width / 2, dy / ln * width / 2
        q = [(x0 - ex + nx, y0 - ey + ny), (x1 + ex + nx, y1 + ey + ny), (x1 + ex - nx, y1 + ey - ny),
             (x0 - ex - nx, y0 - ey - ny)]
        s.poly(f"{name} {j + 1}", colour, q, off=off, op=op)


def believe():
    """A photo shrinks into a white frame; BELIEVE / YOU CAN / SO YOU ARE / HALFWAY / THERE fade in from the right,
    YOU CAN in red; two small lines type."""
    t, s = story("believe", "Historia: BELIEVE YOU CAN SO YOU ARE HALFWAY THERE",
                 "Story: BELIEVE YOU CAN SO YOU ARE HALFWAY THERE", 15448, 2.2, ["foto", "motivación", "frase"])
    s.photo("Foto", "travel-04", (24, 24, 461, 840), look=[effect("color.basic", saturation=-0.55)],
            win=lambda fr: lerp_rect((-2, -2, 488, 866), (24, 24, 461, 840), ease(fr, 12, 27)),
            zoom=zoom_out(1.1, 0, 50))
    rows = (("BELIEVE", 389, 440, 201, WHITE), ("YOU CAN", 459, 527, 251, "#F8291E"), ("SO YOU ARE", 544, 600, 273, WHITE),
            ("HALFWAY", 616, 671, 230, WHITE), ("THERE", 687, 742, 154, WHITE))
    for i, (word, top, bot, w, c) in enumerate(rows):
        s.words(word, 446, top, bot, w, "Bebas Neue", 400, c, f"Frase {i + 1}", align="right",
                anim=("fade", 42 + 2 * i, 0.04, 0.2, "backward"))
    s.words("#MOTIVATION", 50, 47, 72, 156, "Bebas Neue", 400, WHITE, "Hashtag", anim=("typewriter", 42, 0.04, 0.05))
    s.words("FULLNESSLIFE", 242, 783, 800, 107, "Bebas Neue", 400, WHITE, "Texto", align="center",
            anim=("typewriter", 45, 0.04, 0.05))
    return finish(t)


def winner():
    """White story: a grey photo comes down behind two white chevrons that slide down through it; THE WINNER NEVER
    QUITS fades in and a black rule opens."""
    t, s = story("winner", "Historia: THE WINNER NEVER QUITS", "Story: THE WINNER NEVER QUITS", 15449, 2.0,
                 ["foto", "motivación", "gimnasio", "blanco y negro"])
    s.photo("Foto", "y2b-gym-06", (29, 29, 456, 590), look=BW,
            win=lambda fr: (29, 29, 456, lerp(29, 590, ease(fr, 3, 27))))
    for j, dy in enumerate((0, 70)):
        thick_line(s, f"Cheurón {j + 1}", [(29, 29 + dy), (243, 243 + dy), (456, 29 + dy)], 8, WHITE,
                   off=lambda fr, dy=dy: (0, -300 + 420 * ease(fr, 3, 30)),
                   op=lambda fr: ease(fr, 3, 3) * (1 - ease(fr, 30, 6)))
    s.box("Tapa", WHITE, (0, 590, 486, 869))
    s.words("THE WINNER", 242, 658, 694, 335, M, 800, BLACK, "Título", align="center", anim=("fade", 42, 0.03, 0.3))
    s.words("NEVER QUITS", 242, 712, 748, 355, M, 800, BLACK, "Título 2", align="center", anim=("fade", 48, 0.03, 0.3))
    s.box("Línea", BLACK, lambda fr: (243 - 174 * ease(fr, 48, 12), 802, 243 + 174 * ease(fr, 48, 12), 813))
    return finish(t)


def brush_pts(cx, cy, rx, ry, rot, seed, n=90):
    """A rough brush stroke: a stretched blob with ragged, bristly edges."""
    rng = random.Random(seed)
    out = []
    c, sn = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    for i in range(n):
        th = 2 * math.pi * i / n
        q = 1 + 0.08 * math.sin(3 * th + 1.3) + rng.uniform(-0.09, 0.09) + (0.12 if i % 7 == 0 else 0)
        x, y = rx * q * math.cos(th), ry * q * math.sin(th)
        out.append((cx + x * c - y * sn, cy + x * sn + y * c))
    return out


def courage():
    """White story: a portrait tears in from the left, an orange brush stroke sweeps across it, #courage fades in and
    COURAGE IS GRACE UNDER PRESSURE fades in below."""
    t, s = story("courage", "Historia: #courage con pincelada", "Story: #courage with a brush stroke", 15450, 2.6,
                 ["foto", "retrato", "naranja", "pincel"])
    s.photo("Foto", "portrait-08", (39, 43, 446, 720),
            win=lambda fr: (39, 43, lerp(39, 446, ease(fr, 15, 12)), 720))
    pts = brush_pts(238, 590, 235, 88, -32, 5)
    bb = bbox(pts)
    s.box("Pincelada", "#FF5A16", lambda fr: (bb[0], bb[1], bb[0] + (bb[2] - bb[0]) * max(0.01, ease(fr, 45, 15)), bb[3]),
          path=path_of(pts, bb), base=(bb[2] - bb[0], bb[3] - bb[1]))
    s.words("#courage", 43, 564, 632, 398, M, 800, "#D7E21A", "Hashtag", case="none",
            anim=("fade", 60, 0.04, 0.2, "random"))
    s.words("COURAGE IS GRACE", 242, 756, 785, 398, M, 800, BLACK, "Texto", align="center", anim=("fade", 81, 0.02, 0.3))
    s.words("UNDER PRESSURE", 242, 797, 826, 357, M, 800, BLACK, "Texto 2", align="center", anim=("fade", 87, 0.02, 0.3))
    return finish(t)


# =====================================================================================================================
# s18 (59.67-63.40 s)
# =====================================================================================================================

def leaf_pts(cx, cy, length, width, angle):
    """A pointed leaf shape (panel px)."""
    pts = []
    for i in range(24):
        t_ = i / 23
        x = (t_ - 0.5) * length
        y = math.sin(math.pi * t_) * width / 2
        pts.append((x, y))
    pts += [(x, -y) for x, y in reversed(pts[1:-1])]
    c, sn = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    return [(cx + x * c - y * sn, cy + x * sn + y * c) for x, y in pts]


def deep_breath():
    """Peach ground with tropical leaves that blow away; a round window of the photo opens and grows to the whole
    story; a green wave drops at the top and a pink one rises at the foot with ENJOY / DEEP BREATH."""
    t, s = story("deep-breath", "Historia: ENJOY DEEP BREATH con hojas", "Story: ENJOY DEEP BREATH with leaves", 15451,
                 2.6, ["foto", "naturaleza", "verde", "rosa"], ground="#FCD9A0")
    rng = random.Random(4)
    for i in range(14):
        cx, cy = rng.uniform(-20, 500), rng.uniform(-20, 880)
        s.poly(f"Hoja {i + 1}", rng.choice(["#3E8A44", "#5C7A1E", "#4E9A4A"]),
               leaf_pts(cx, cy, rng.uniform(150, 260), rng.uniform(60, 110), rng.uniform(0, 180)),
               off=lambda fr, d=rng.choice((-1, 1)), at=rng.uniform(15, 27): (d * 520 * ease(fr, at, 12), 0),
               op=lambda fr: 1 - ease(fr, 40, 1))
    s.photo("Foto", "garden-03", (0, 0, 486, 864), kind="ellipse",
            win=lambda fr: (lambda r: (243 - r, 432 - r, 243 + r, 432 + r))(max(0.5, lerp(0, 560, ease(fr, 27, 30)))),
            op=lambda fr: lerp(0.4, 1.0, ease(fr, 36, 18)))
    green = [gradient([(0.0, "#4E8A3A"), (1.0, "#B2BC14")], angle=0), no_stroke()]
    pink = [gradient([(0.0, "#FF4F6E"), (1.0, "#FF6E58")], angle=0), no_stroke()]
    s.poly("Ola verde", green, [(-5, -5), (465, -5), (430, 60), (380, 100), (300, 120), (220, 128), (160, 150),
                                (100, 165), (-5, 172)], off=slide(0, -190, 57, 12))
    s.poly("Ola rosa", pink, [(-5, 792), (80, 745), (170, 700), (260, 676), (360, 662), (491, 660), (491, 869),
                              (-5, 869)], off=slide(0, 220, 57, 12))
    s.words("#GREENPLANT&NATURE", 32, 35, 59, 274, "Bebas Neue", 400, WHITE, "Hashtag", anim=("typewriter", 69, 0.03, 0.05))
    s.words("ENJOY", 32, 85, 138, 149, "Bebas Neue", 400, WHITE, "Título", anim=("fade", 66, 0.06, 0.2))
    s.words("DEEP", 456, 650, 704, 118, "Bebas Neue", 400, WHITE, "Título 2", align="right",
            anim=("fade", 66, 0.06, 0.2, "backward"))
    s.words("BREATH", 456, 720, 774, 187, "Bebas Neue", 400, WHITE, "Título 3", align="right",
            anim=("fade", 69, 0.06, 0.2, "backward"))
    s.words("FEEL THE FULLNESS OF LIFE", 456, 800, 826, 292, "Bebas Neue", 400, WHITE, "Texto", align="right",
            anim=("typewriter", 72, 0.03, 0.05))
    return finish(t)


def feeling_tropical():
    """Teal story: three photos open through growing diamonds, white rises from the foot and FEELING TROPICAL and
    THIS SUMMER WILL BE HOT fade in."""
    t, s = story("tropical", "Historia: FEELING TROPICAL con tres fotos", "Story: FEELING TROPICAL with three photos",
                 15452, 2.2, ["foto", "verano", "tropical", "collage"], ground="#00A0C0")
    s.poly("Blanco", WHITE, [(-5, 0), (100, 30), (243, -40), (380, 30), (491, 0), (491, 900), (-5, 900)],
           off=slide(0, 900, 45, 18))
    for i, (sample, r, at) in enumerate((("y5-h-ocean-03", (0, 41, 486, 288), 6), ("h-summer-02", (0, 331, 225, 653), 9),
                                         ("summer-04", (261, 331, 486, 653), 9))):
        cx, cy = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2
        rad = ((r[2] - r[0]) + (r[3] - r[1])) / 2
        dia = s.box(f"Rombo {i + 1}", WHITE, lambda fr, cx=cx, cy=cy, rad=rad, at=at: (lambda q: (
            cx - q, cy - q, cx + q, cy + q))(max(0.5, rad * ease(fr, at, 18))),
            path="M 50 0 L 100 50 L 50 100 L 0 50 Z", base=(2 * rad, 2 * rad))
        c = s.photo(f"Foto {i + 1}", sample, r, matte=False, label=f"Foto {i + 1}")
        c["matte"] = {"clip": dia["id"], "mode": "alpha"}
    s.words("FEELING", 242, 689, 729, 261, AR, 900, BLACK, "Título", align="center", anim=("fade", 45, 0.04, 0.3))
    s.words("TROPICAL", 242, 739, 775, 267, AR, 900, BLACK, "Título 2", align="center", anim=("fade", 51, 0.04, 0.3))
    s.words("THIS SUMMER WILL BE HOT", 243, 806, 824, 386, M, 500, BLACK, "Texto", align="center",
            anim=("typewriter", 45, 0.03, 0.05))
    return finish(t)


def ellipse_arc(cx, cy, rx, ry, a0, a1, n=28):
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def sport():
    """A peach curtain with a dark wavy edge slides down off a running photo; a thin white S of two arcs draws
    with a dot at each end; a big W, SPORT and two small lines fade in."""
    t, s = story("sport", "Historia: W SPORT con trazo", "Story: W SPORT with a line", 15453, 2.2,
                 ["foto", "deporte", "correr", "línea"])
    s.photo("Foto", "y5-street-01", (0, 0, 486, 864), matte=False, zoom=zoom_out(1.08, 0, 60))
    wave = [(-5, -1000)] + [(x, 0 + 40 * math.sin(x / 486 * 2 * math.pi * 1.5)) for x in range(-5, 495, 20)] + \
        [(491, -1000)]
    s.poly("Borde", "#2E2E2E", [(x, y + 30) for x, y in wave], off=lambda fr: (0, 900 + 1000 * ease(fr, 0, 39)),
           op=lambda fr: 1 - ease(fr, 39, 1))
    s.poly("Cortina", "#EBCBB8", wave, off=lambda fr: (0, 900 + 1000 * ease(fr, 0, 36)),
           op=lambda fr: 1 - ease(fr, 36, 1))
    op = lambda fr: ease(fr, 39, 3)  # noqa: E731
    right = ellipse_arc(363, 372, 120, 183, 180, 360)
    left = ellipse_arc(123, 372, 120, 183, 180, 0)
    thick_line(s, "Trazo", right, 2.2, WHITE, op=op)
    thick_line(s, "Trazo 2", left, 2.2, WHITE, op=op)
    for i, (x, y) in enumerate(((363, 189), (123, 555))):
        s.box(f"Punto {i + 1}", WHITE, (x - 5, y - 5, x + 5, y + 5), kind="ellipse", op=op)
    s.words("W", 241, 282, 424, 210, M, 600, WHITE, "Letra", align="center", anim=("fade", 45, 0.0, 0.4))
    s.words("SPORT", 243, 449, 500, 240, M, 500, WHITE, "Título", align="center", anim=("fade", 48, 0.05, 0.3))
    s.words("- crossfit -", 241, 42, 66, 193, M, 400, WHITE, "Texto", align="center", case="none",
            anim=("fade", 51, 0.04, 0.3))
    s.words("BUILD THE PERFECT BODY", 241, 797, 820, 397, M, 500, WHITE, "Texto 2", align="center",
            anim=("fade", 48, 0.03, 0.3))
    return finish(t)


# =====================================================================================================================
# s19 (63.40-67.43 s)
# =====================================================================================================================

def moving():
    """A navy panel wipes off diagonally with blue circles riding its edge; a white and a navy ring slide in round
    Mo/ving, and a white outline draws round #BREATHE."""
    t, s = story("moving", "Historia: Moving con dos aros", "Story: Moving with two rings", 15454, 2.2,
                 ["foto", "baile", "aros", "azul"])
    s.photo("Foto", "dance-01", (0, 0, 486, 864), matte=False, zoom=zoom_out(1.08, 0, 60))
    navy, blue = "#06305A", "#1580C8"

    def edge(fr):
        return lerp(-560, 140, ease(fr, 3, 27))
    s.poly("Azul", navy, [(2000, 2000), (-900, 2000), (2000, -900)], off=lambda fr: (edge(fr), edge(fr)),
           op=lambda fr: 1 - ease(fr, 30, 1))
    for i, (cx, cy, r) in enumerate(((150, 150, 120), (430, 300, 150), (60, 520, 110))):
        s.box(f"Círculo {i + 1}", blue, lambda fr, cx=cx, cy=cy, r=r: (cx - r + edge(fr) * 0.5, cy - r + edge(fr) * 0.5,
                                                                        cx + r + edge(fr) * 0.5, cy + r + edge(fr) * 0.5),
              kind="ellipse", op=lambda fr: 1 - ease(fr, 24, 6))
    s.box("Aro", ring(WHITE, 4 * R), lambda fr: (lambda d: (93 + d, 202 - d, 413 + d, 522 - d))(260 * (1 - ease(fr, 30, 21))),
          kind="ellipse", op=lambda fr: ease(fr, 30, 6))
    s.box("Aro 2", ring(navy, 5 * R), lambda fr: (lambda d: (66 - d, 225 + d, 386 - d, 545 + d))(260 * (1 - ease(fr, 33, 21))),
          kind="ellipse", op=lambda fr: ease(fr, 33, 6))
    s.words("Mo", 129, 302, 367, 146, M, 700, WHITE, "Título", case="none", anim=("fade", 51, 0.06, 0.2, "backward"))
    s.words("ving", 161, 377, 425, 195, M, 700, WHITE, "Título 2", case="none", anim=("fade", 39, 0.06, 0.2, "backward"))
    s.frame_line("Recuadro", WHITE, (116.5, 725.5, 369.5, 777.5), 5, 30, 15)
    s.words("#BREATHE", 243, 739, 767, 214, M, 800, WHITE, "Hashtag", align="center",
            anim=("fade", 36, 0.05, 0.2, "random"))
    return finish(t)


def pro_fitness():
    """A peach-veiled photo; two mirrored trapezoid outlines open from the centre into a crossed frame; PRO, fitness
    and a widely spaced hashtag fade in."""
    t, s = story("pro-fitness", "Historia: PRO fitness con marco cruzado", "Story: PRO fitness with a crossed frame",
                 15455, 2.0, ["foto", "deporte", "marco", "melocotón"])
    s.photo("Foto", "y5-grwm-05", (0, 0, 486, 864), matte=False, zoom=zoom_out(1.06, 0, 60))
    s.box("Velo", solid("#FF9A80", 0.55), (-5, -5, 491, 869))
    for i, pts in enumerate(([(100, 195), (366, 227), (366, 516), (100, 549)],
                             [(119, 227), (386, 195), (386, 549), (119, 516)])):
        bb = bbox(pts)
        s.box(f"Marco {i + 1}", ring(WHITE, 2.5 * R), lambda fr, bb=bb: (lambda q: (243 - (243 - bb[0]) * q, bb[1],
                                                                                      243 + (bb[2] - 243) * q, bb[3]))(
            max(0.02, ease(fr, 3, 18))), path=path_of(pts, bb), base=(bb[2] - bb[0], bb[3] - bb[1]),
            op=lambda fr: ease(fr, 3, 3))
    s.words("PRO", 241, 320, 385, 212, M, 500, WHITE, "Título", align="center", anim=("fade", 45, 0.06, 0.25, "random"))
    s.words("fitness", 241, 414, 440, 138, M, 300, WHITE, "Texto", align="center", case="none",
            anim=("fade", 48, 0.05, 0.25, "random"))
    s.words("# fitnessgirl", 245, 578, 596, 266, M, 300, BLACK, "Hashtag", align="center", case="none", spacing=0.55,
            anim=("fade", 48, 0.03, 0.25, "random"))
    return finish(t)


def young():
    """A dark photo; pink, green, yellow and blue blocks stack up in a window and the blue one rolls up to show the
    photo tinted red; YOUNG fades in on a red bar, with #followus and two lines."""
    t, s = story("young", "Historia: YOUNG #followus", "Story: YOUNG #followus", 15456, 2.0,
                 ["foto", "juventud", "rojo", "colores"])
    full = (0, 0, 486, 864)
    first = s.photo("Foto", "y5-street-07", full, matte=False, zoom=zoom_out(1.06, 0, 60))
    s.box("Sombra", solid(BLACK, 0.35), (-5, -5, 491, 869))
    s.photo("Foto (ventana)", "y5-street-07", full, reuse=first["placeholderId"], zoom=zoom_out(1.06, 0, 60),
            win=(47, 47, 443, 642))
    s.box("Tinte", solid("#E8442A", 0.5), (47, 47, 443, 642))
    for i, (c, at) in enumerate((("#FF3D6E", 3), ("#00907C", 9), ("#F0BA00", 15), ("#0E3AB0", 21))):
        last = i == 3
        s.box(f"Bloque {i + 1}", c, lambda fr, at=at, last=last: (
            47, lerp(642, 47, ease(fr, at, 9)), 443, lerp(642, 47, ease(fr, 33, 12)) if last else 642),
            op=(lambda fr, at=at: 1 - ease(fr, at + 15, 1)) if not last else None)
    s.box("Barra", "#F03234", grow_x((47, 537, 443, 642), 42, 9))
    s.words("YOUNG", 89, 564, 616, 307, "Archivo Black", 400, WHITE, "Título", anim=("fade", 30, 0.05, 0.2, "backward"))
    s.words("#followus", 243, 72, 102, 163, M, 700, WHITE, "Hashtag", align="center", case="none",
            anim=("fade", 33, 0.05, 0.2, "random"))
    s.words("THE WHOLE WORLD", 242, 754, 775, 294, M, 800, WHITE, "Texto", align="center",
            anim=("typewriter", 33, 0.03, 0.05))
    s.words("IS OPEN TO US", 242, 789, 810, 214, M, 800, WHITE, "Texto 2", align="center",
            anim=("typewriter", 42, 0.03, 0.05))
    return finish(t)


# =====================================================================================================================
# s20 (67.43-71.36 s)
# =====================================================================================================================

def star_pts(cx, cy, r, inner):
    """A four-pointed star with concave sides (panel px)."""
    pts = []
    for i in range(4):
        a = math.radians(90 * i)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        b = math.radians(90 * i + 45)
        pts.append((cx + inner * math.cos(b), cy + inner * math.sin(b)))
    return pts


def beauty_flowers():
    """Cream story: a small pink cross turns, grows and opens into a four-pointed star of the photo that fills the
    top; a pink band and line come in under it, Beauty writes in and LIFE IS A COLLECTION OF MOMENTS fades in."""
    t, s = story("beauty-flowers", "Historia: Beauty con flores", "Story: Beauty with flowers", 15457, 3.2,
                 ["foto", "flores", "caligrafía", "rosa"], ground="#FDF9EC")
    pink = "#D57C8C"
    for j, ang in enumerate((45, -45)):
        s.box(f"Cruz {j + 1}", pink, lambda fr: (lambda q: (243 - 27 * q, 290 - 2.2, 243 + 27 * q, 290 + 2.2))(
            1 + 4.5 * ease(fr, 42, 9)), rot=lambda fr, ang=ang: ang + 120 * ease(fr, 0, 42),
            op=lambda fr: 1 - ease(fr, 51, 3))
    pts = star_pts(243, 292, 300, 75)
    bb = bbox(pts)
    s.photo("Foto", "flowers-02", (0, 0, 486, 584), path=path_of(pts, bb),
            win=lambda fr: (lambda q: (243 - 300 * q, 292 - 300 * q, 243 + 300 * q, 292 + 300 * q))(
                max(0.002, lerp(0.0, 4.0, ease(fr, 48, 24)))))
    s.box("Banda", "#F9A0A8", lambda fr: (-5, 634, 491, lerp(634, 742, ease(fr, 72, 12))), op=lambda fr: ease(fr, 72, 2))
    s.box("Línea", "#F9A0A8", grow_x((121, 797, 364, 804), 75, 9))
    s.words("Beauty", 258, 212, 337, 350, SCRIPT, 700, WHITE, "Título", align="center", case="none",
            anim=("fade", 84, 0.06, 0.3))
    s.words("LIFE IS A COLLECTION", 243, 673, 688, 308, M, 400, WHITE, "Texto", align="center", spacing=0.35,
            anim=("fade", 87, 0.02, 0.3))
    s.words("OF MOMENTS", 243, 694, 709, 180, M, 400, WHITE, "Texto 2", align="center", spacing=0.35,
            anim=("fade", 90, 0.02, 0.3))
    return finish(t)


def audacious():
    """A red panel sinks away, a black band drops at the top, a photo slides down under it with a green rule;
    #AUDACIOUS types and LET'S DO WHAT WE LOVE fades in in black italics."""
    t, s = story("audacious", "Historia: LET'S DO WHAT WE LOVE #AUDACIOUS", "Story: LET'S DO WHAT WE LOVE #AUDACIOUS",
                 15458, 2.2, ["foto", "motivación", "negro", "verde"])
    s.box("Rojo", "#DC2A3A", lambda fr: (-5, lerp(-5, 869, ease(fr, 0, 33)), 491, 869))
    s.box("Banda", "#16181D", lambda fr: (-5, -5, 491, lerp(-5, 162, ease(fr, 3, 9))))
    s.photo("Foto", "y4c-friends-05", (0, 180, 486, 540), win=lambda fr: (0, 180, 486, lerp(180, 540, ease(fr, 9, 15))))
    s.box("Verde", "#00A07A", grow_x((0, 559, 486, 580), 18, 9))
    s.words("#AUDACIOUS", 244, 63, 98, 333, M, 800, WHITE, "Hashtag", align="center", italic=True,
            anim=("typewriter", 48, 0.04, 0.05))
    for i, (word, top, bot, x0, x1) in enumerate((("LET'S DO", 620, 677, 58, 426), ("WHAT", 692, 749, 109, 356),
                                                   ("WE LOVE", 764, 822, 58, 428))):
        s.words(word, (x0 + x1) / 2, top, bot, x1 - x0, M, 900, BLACK, f"Título {i + 1}", align="center", italic=True,
                anim=("fade", 48 + 4 * i, 0.04, 0.3))
    return finish(t)


def delicious():
    """A grid: a red square grows from the right and a yellow one from the left, three food photos slide in
    between them; PERFECT, #DELICIOUS and taste type in."""
    t, s = story("delicious", "Historia: #DELICIOUS en cuadrícula", "Story: #DELICIOUS grid", 15459, 2.0,
                 ["foto", "comida", "postres", "cuadrícula"])
    s.box("Rojo", "#FF5650", grow_x((243, 0, 486, 242), 3, 12, from_right=True))
    s.box("Amarillo", "#F5B300", grow_x((0, 621, 243, 864), 3, 12))
    s.photo("Foto 1", "food-02", (0, 0, 243, 242), win=grow_x((0, 0, 243, 242), 21, 9, from_right=True), label="Foto 1")
    s.photo("Foto 2", "y6-dessert-01", (0, 242, 486, 621), win=grow_x((0, 242, 486, 621), 15, 12, from_right=True),
            label="Foto 2")
    s.photo("Foto 3", "y6-dessert-03", (243, 621, 486, 864), win=grow_x((243, 621, 486, 864), 18, 9), label="Foto 3")
    s.words("PERFECT", 368, 106, 132, 146, M, 800, WHITE, "Texto", align="center", anim=("typewriter", 39, 0.04, 0.05))
    s.words("#DELICIOUS", 243, 409, 445, 340, M, 800, WHITE, "Hashtag", align="center",
            anim=("typewriter", 45, 0.04, 0.05))
    s.words("taste", 121, 722, 760, 129, M, 800, WHITE, "Texto 2", align="center", case="none",
            anim=("typewriter", 48, 0.05, 0.05))
    return finish(t)


TEMPLATES = [dream, style_personal, youth, summer, music, trendy, beauty, look_deep, motion, skate, secrets, big,
             meeting, sunshine, clear_interior, fun_cart, spring, stay_strong, control, born_wild, stylish,
             style_beautiful, ocean, abstract, sale75, glam, summer_event, masterpiece, sale40, life_good,
             cold_wave, employee, never_easier, sunshine_tag, shopping_week, summer_look, stylish_confident,
             street_fast, culinary, natural_beauty, enjoy_music, fitness_body, insta_music, my_lifestyle,
             brand_new_day, simple_life, fashion_buy, amazing_dream, believe, winner, courage, deep_breath,
             feeling_tropical, sport, moving, pro_fitness, young, beauty_flowers, audacious, delicious]
