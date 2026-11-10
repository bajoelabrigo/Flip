"""LOGO folder video 1 as Stock templates (lg1-*). See docs/plan-logo.md.

34063055.mp4 (960×540 at 29.97 fps, 10 s, laid out at 1920×1080): one logo reveal on a bright white-gold haze.
The logo (the user's, the `logo-flip` slot) is built from seven horizontal slices from the top, one every third of
a second, each one born squashed and stretching to its height while a line of light crosses the frame at its lower
edge; a golden glow wraps it while it builds, a hot spot burns at its base, «WWW.YOURWEBSITE.COM» blurs in under it,
two shines cross it and everything fades to black. The camera pulls back slowly the whole time. Measured frame by
frame (tienda/plantillas/estudio-34063055/NOTAS.md). Kit de YouTube › Aperturas, order 13700-.
"""

from __future__ import annotations

import math
import random

from kit import Box, wide
from llt_motion import frames_of
from scene import no_stroke, tanim
from templates_tit_c import FPS, k
from templates_tit_e import solid
from templates_tit_h import S, M, URL

BROWN = "#40291D"
GOLD = "#FFD23C"
WARM = "#FFF4D8"
D = 10.0
ZX, ZY = 956.0, 516.0  # the camera pulls back about this point
LOGO_C = (951.0, 489.0)  # the logo's centre at scale 1 (the frame of 2.5 s)
BOX = 688.0  # the slot's square box; the sample's ink fills 672 px of it (6..506 of 512)
INK_TOP = LOGO_C[1] - BOX / 2 + BOX * 6 / 512
INK_H = BOX * 500 / 512
# Slice edges (fraction of the logo's height) and the frame each slice shows at.
EDGES = [0.0, 0.10, 0.25, 0.40, 0.55, 0.69, 0.845, 1.0]
BORN = [11, 21, 31, 41, 51, 62, 72]
# How tall a slice is (of its height) the frames after it shows: squashed, stretching, a little overshoot.
OPEN = [0.28, 0.45, 0.68, 0.88, 1.03, 1.05, 1.0]
WHOLE = 2.7  # seconds: the slices give way to one whole copy of the logo


def _a(colour, alpha):
    return "#" + format(round(max(0.0, min(1.0, alpha)) * 255), "02x") + colour.lstrip("#").lower()


def radial(colour, alpha, mid=None):
    """A round soft light: colour at alpha in the middle, fading out at the rim (mid = alpha at half radius)."""
    stops = [{"pos": 0, "color": _a(colour, alpha)}]
    if mid is not None:
        stops.append({"pos": 0.5, "color": _a(colour, mid)})
    stops.append({"pos": 1, "color": _a(colour, 0.0)})
    return [{"id": "fill", "kind": "fill", "enabled": True, "opacity": 1.0,
             "paint": {"kind": "gradient", "color": _a(colour, alpha),
                       "gradient": {"kind": "radial", "stops": stops, "angle": 0, "space": "block"}}}, no_stroke()]


def band(colour, alpha, angle=90, core=0.5):
    """A soft line: transparent at both edges, colour at alpha in the middle (angle 90 = across its height)."""
    stops = [(0.0, 0.0), (core * 0.5, alpha * 0.35), (0.5, alpha), (1 - core * 0.5, alpha * 0.35), (1.0, 0.0)]
    return [{"id": "fill", "kind": "fill", "enabled": True, "opacity": 1.0,
             "paint": {"kind": "gradient", "color": _a(colour, alpha),
                       "gradient": {"kind": "linear", "stops": [{"pos": p, "color": _a(colour, a)} for p, a in stops],
                                    "angle": angle, "space": "block"}}}, no_stroke()]


def table(points):
    """[(seconds, value)] -> f(seconds), smooth between the points, held outside."""
    def f(t):
        if t <= points[0][0]:
            return points[0][1]
        for (a, va), (b, vb) in zip(points, points[1:]):
            if t <= b:
                x = (t - a) / (b - a)
                return va + (vb - va) * (x * x * (3 - 2 * x))
        return points[-1][1]
    return f


# The camera: the logo's scale over the clip (measured on its top edge and the address's width).
ZOOM = table([(0.0, 1.16), (1.0, 1.14), (1.5, 1.11), (2.0, 1.04), (2.5, 1.0), (3.0, 0.978), (4.0, 0.936),
              (5.0, 0.899), (6.0, 0.866), (7.0, 0.838), (8.0, 0.818), (9.3, 0.80), (10.0, 0.795)])


def zy(y, t):
    return ZY + (y - ZY) * ZOOM(t)


def zx(x, t):
    return ZX + (x - ZX) * ZOOM(t)


def pulse(fr, at, up, hold, down):
    """0 → 1 over `up` frames from `at`, 1 for `hold`, back to 0 over `down`."""
    return k(fr, at, up) * (1 - k(fr, at + up + hold, down))


class Lg(S):
    """A piece played straight: u seconds = frame u × FPS (no exit played backwards)."""

    def frame(self, u):
        return u * FPS

    def role(self, clip, role):
        clip["layoutRole"] = role
        return clip


def _logo(t, name, motion, t0=0.0, dur=D, reuse=None):
    """The user's logo (one slot: every copy shows the same picture)."""
    return t.photo(t.track("video", name), "logo-flip", t0, dur,
                   Box(LOGO_C[0] - BOX / 2, LOGO_C[1] - BOX / 2, BOX, BOX), motion, label="Tu logo", reuse=reuse,
                   brandRole="logo")


def light_build():
    t = wide("lg1-luz-dorada", "Logo: se arma con luz dorada", "Logo: built with golden light", "ytkit", D,
             order=13700, tags=["kit:aperturas", "logo", "intro", "luz", "dorado", "brillo", "franjas", "elegante"],
             thumb_at=6.6)
    s = Lg(t, D)
    rnd = random.Random(34063055)

    # --- background: grey vignette, a white haze in the middle, warm streaks and dust -----------------------------
    # A neutral grey haze, brightest a little below the middle (the reference's first frames, measured).
    stops = [{"pos": 0, "color": "#ff9c9b9c"}, {"pos": 0.083, "color": "#ffb0afb0"}, {"pos": 0.167, "color": "#ffc3c2c3"}, {"pos": 0.25, "color": "#ffd4d3d4"}, {"pos": 0.333, "color": "#ffe1e0e1"}, {"pos": 0.417, "color": "#ffe8e7e8"}, {"pos": 0.5, "color": "#ffebeaeb"}, {"pos": 0.583, "color": "#ffe9e8e9"}, {"pos": 0.667, "color": "#ffe6e5e6"}, {"pos": 0.75, "color": "#ffd8d7d8"}, {"pos": 0.833, "color": "#ffb7b6b7"}, {"pos": 0.917, "color": "#ffa09fa0"}, {"pos": 1.0, "color": "#ff929192"}]
    bg = s.rect("Fondo", [{"id": "fill", "kind": "fill", "enabled": True, "opacity": 1.0, "paint": {
        "kind": "gradient", "color": stops[0]["color"], "gradient": {"kind": "linear", "angle": 90, "space": "block",
                                                                     "stops": stops}}}, no_stroke()],
                lambda fr, u: (0, 0, 1920, 1080))
    s.role(bg, "cover")
    # The warm light: none at first, it floods in while the logo builds (peak 3.2 s, strongest on the right, top and
    # bottom) and settles to a gentle warmth from 6 s.
    warmth = table([(0.0, 0.0), (0.8, 0.0), (1.4, 0.25), (1.6, 0.12), (2.1, 0.45), (2.4, 0.3), (3.2, 1.0),
                    (3.6, 0.72), (4.4, 0.68), (6.0, 0.45), (10.0, 0.45)])
    for name, (x, y, w, h), a in (("Luz cálida abajo", (1500, 1000, 2400, 760), 0.75),
                                  ("Luz cálida arriba", (1450, 40, 2000, 420), 0.7),
                                  ("Luz cálida al centro", (960, 720, 2600, 260), 0.55)):
        s.role(s.obj(name, radial("#FFCF6A", a, a * 0.55),
                     lambda fr, u, x=x, y=y, w=w, h=h: (x, y, w, h, 0, warmth(u)), kind="ellipse"), "cover")
    # A veil of warm light over everything at the peak (3.2 s), and a little with the slices' flashes.
    veil = table([(0.0, 0.0), (1.2, 0.0), (1.4, 0.12), (1.6, 0.0), (1.9, 0.1), (2.2, 0.12), (2.6, 0.05), (3.0, 0.8),
                  (3.25, 1.0), (3.6, 0.6), (4.4, 0.35), (6.0, 0.12), (10.0, 0.12)])
    s.role(s.obj("Velo de luz", solid("#FFF4D6"), lambda fr, u: (960, 540, 1920, 1080, 0, 0.4 * veil(u))), "cover")
    # The golden streak at the top right, there the whole time.
    s.role(s.obj("Raya dorada", band("#F6E0B0", 0.6, core=0.6),
                 lambda fr, u: (1380 + 12 * u, 96, 1300, 150, 0, 0.45 + 0.4 * warmth(u))), "cover")
    # Streaks: (y, x centre at 0 s, length, thickness, alpha, drift px/s)
    for i, (y, x, w, h, a, v) in enumerate(((312, 520, 640, 22, 0.75, 30), (512, 1380, 1100, 34, 0.85, -22),
                                            (232, 1500, 700, 16, 0.5, 18), (640, 420, 900, 40, 0.6, 26),
                                            (782, 1000, 1500, 30, 0.45, -14), (420, 160, 420, 14, 0.55, 40))):
        c = s.obj(f"Raya de luz {i + 1}", band(WARM, a * 0.6),
                  lambda fr, u, y=y, x=x, w=w, h=h, v=v, i=i: (x + v * u, y, w, h, 0,
                                                               0.75 + 0.25 * math.sin(u * 0.9 + i * 1.7)))
        s.role(c, "cover")
    for i in range(26):
        x0, y0 = rnd.uniform(40, 1880), rnd.uniform(60, 1020)
        r = rnd.uniform(2.5, 5.5)
        vx, vy = rnd.uniform(-8, 14), rnd.uniform(-10, 4)
        ph = rnd.uniform(0, 6.3)
        c = s.obj(f"Mota {i + 1}", radial("#FFFFFF", 1.0, 0.8),
                  lambda fr, u, x0=x0, y0=y0, r=r, vx=vx, vy=vy, ph=ph: (
                      x0 + vx * u, y0 + vy * u, r * 2, r * 2, 0, 0.55 + 0.45 * math.sin(u * 2.1 + ph)),
                  kind="ellipse")
        s.role(c, "cover")

    # --- the golden light that wraps the logo while it builds -----------------------------------------------------
    def halo(fr, u):
        sc = ZOOM(u)
        return (zx(1130, u), zy(150, u), 520 * sc, 560 * sc, 0, 0.8 * k(fr, 10, 25) * (1 - k(fr, 70, 30)))
    s.role(s.obj("Resplandor dorado", radial(GOLD, 0.55, 0.22), halo, kind="ellipse"), "art")
    # A line of light crosses the frame at the lower edge of each slice as it opens.
    for i, b in enumerate(BORN[1:], 1):
        edge = INK_TOP + INK_H * EDGES[i + 1]

        def flash(fr, u, b=b, edge=edge):
            return (960, zy(edge, u), 2600, 70, 0, pulse(fr, b, 2, 2, 9))

        s.role(s.obj(f"Destello {i}", band("#FFF2C0", 1.0, core=0.3), flash), "cover")

        def core(fr, u, b=b, edge=edge):
            return (zx(951, u) + 60 * lin01(fr, b, 14), zy(edge, u), 640 * ZOOM(u), 16, 0, pulse(fr, b, 2, 3, 8))
        s.role(s.obj(f"Destello {i} (núcleo)", band("#FFFFFF", 1.0, core=0.2), core), "art")

    # --- the logo in slices --------------------------------------------------------------------------------------
    glow_op = lambda fr, u: 0.85 * (1 - k(fr, 62, 22))  # noqa: E731
    tint_op = lambda fr, u: 0.42 * (1 - 0.3 * k(fr, 84, 20)) * (1 - k(fr, 100, 90))  # noqa: E731
    first = None
    for i, b in enumerate(BORN):
        e0, e1 = INK_TOP + INK_H * EDGES[i], INK_TOP + INK_H * EDGES[i + 1]
        mid = (e0 + e1) / 2

        def q(fr, b=b):
            n = fr - b
            if n < 0:
                return 0.0
            if n >= len(OPEN) - 1:
                return 1.0
            j = int(n)
            return OPEN[j] + (OPEN[j + 1] - OPEN[j]) * (n - j)

        def gap(fr, i=i):
            """Thin white lines between slices, flickering until about 2.7 s (half the line, project px)."""
            if i == 0:
                return 0.0
            n = fr - BORN[i]
            return 2.5 if (0 <= n < 14 or 19 <= n < 24 or 31 <= n < 34) and fr < 80 else 0.0

        def nxt_gap(fr, i=i):
            return gap(fr, i + 1) if i + 1 < len(BORN) else 0.0

        motion = []
        for u in frames_of(WHOLE):
            fr = u * FPS
            # Full height before it shows: the slot's crop is taken from the first key.
            sc, qq = ZOOM(u), (max(1e-3, q(fr)) if fr >= b else 1.0)
            cy = zy(mid, u) + (zy(LOGO_C[1], u) - zy(mid, u)) * qq
            motion.append((u, {"sx": sc, "sy": sc * qq, "dx": zx(LOGO_C[0], u) - LOGO_C[0], "dy": cy - LOGO_C[1]},
                           "linear"))
        clip = _logo(t, f"Logo (franja {i + 1})", motion, 0.0, WHOLE,
                     reuse=first["placeholderId"] if first else None)
        first = first or clip
        clip["layoutRole"] = "art"
        s.fx(clip, "layer.color_overlay", color="#FFEC4A", animated={"opacity": tint_op})
        s.fx(clip, "layer.outer_glow", color="#FFE680", size=64, spread=0.35, animated={"opacity": glow_op})

        def strip(fr, u, e0=e0, e1=e1, mid=mid, q=q, gap=gap, nxt_gap=nxt_gap):
            qq = q(fr) or 1.0  # before it shows it waits at full size, see-through (op below)
            m, a, b2 = zy(mid, u), zy(e0, u), zy(e1, u)
            top, bot = m + (a - m) * qq + gap(fr), m + (b2 - m) * qq - nxt_gap(fr)
            return (zx(620, u), top, zx(1290, u), max(top + 0.5, bot))
        matte = s.rect(f"Franja {i + 1}", solid("#FFFFFF"), strip, op=lambda fr, u, b=b: 1.0 if fr >= b else 0.0)
        matte["timelineDurationUs"] = clip["timelineDurationUs"]
        matte["srcOutUs"] = clip["srcOutUs"]
        matte["layoutRole"] = "art"
        clip["matte"] = {"clip": matte["id"], "mode": "alpha"}

    # The whole logo from WHOLE on (the slices are closed by then).
    motion = []
    for u in frames_of(D):
        if u < WHOLE - 1e-6:
            continue
        sc = ZOOM(u)
        motion.append((u - WHOLE, {"s": sc, "dx": zx(LOGO_C[0], u) - LOGO_C[0], "dy": zy(LOGO_C[1], u) - LOGO_C[1]},
                       "linear"))
    logo = _logo(t, "Logo", motion, WHOLE, D - WHOLE, reuse=first["placeholderId"])
    logo["layoutRole"] = "art"
    s.fx(logo, "layer.color_overlay", color="#FFEC4A",
         animated={"opacity": lambda fr, u: tint_op(fr, u)})
    # Keyframes of the whole logo's effects are on its own clock (it starts at WHOLE).
    for e in logo["effects"]:
        for kf in e.get("paramKeyframes", {}).values():
            for p in kf["keyframes"]:
                p["timeUs"] -= round(WHOLE * 1e6)
            kf["keyframes"] = [p for p in kf["keyframes"] if p["timeUs"] >= 0]

    # A track matte hides its source: the lights on the logo ride a copy of it kept only as their matte.
    shape_of = _logo(t, "Logo (forma de los brillos)", motion, WHOLE, D - WHOLE, reuse=first["placeholderId"])
    shape_of["layoutRole"] = "art"

    def on_logo(name, layers, geom, blend="screen"):
        c = s.obj(name, layers, geom)
        c["matte"] = {"clip": shape_of["id"], "mode": "alpha"}
        c["blendMode"] = blend
        c["layoutRole"] = "art"
        return c

    # The hot spot at the base of the logo, 2.8-5.9 s.
    def hot(fr):
        return k(fr, 82, 12) * (1 - 0.35 * k(fr, 108, 30)) * (1 - k(fr, 130, 45))
    # (A radial fill does not draw under a track matte: a linear one rising from the base instead.)
    rise = [{"id": "fill", "kind": "fill", "enabled": True, "opacity": 1.0, "paint": {
        "kind": "gradient", "color": _a("#FFE84A", 0.95), "gradient": {"kind": "linear", "angle": 90, "space": "block",
                                                                      "stops": [{"pos": 0, "color": _a("#FFE84A", 0)},
                                                                                {"pos": 0.55, "color": _a("#FFE84A", 0.45)},
                                                                                {"pos": 1, "color": _a("#FFF080", 0.95)}]}}},
            no_stroke()]
    on_logo("Punto caliente", rise,
            lambda fr, u: (zx(951, u), zy(752, u), 700 * ZOOM(u), 230 * ZOOM(u), 0, hot(fr)), blend="normal")
    # Shine 1: a bright upright bar crosses the logo left to right, 5.55-6.15 s.
    on_logo("Brillo 1", band("#FFFF7A", 1.0, angle=0, core=0.35),
            lambda fr, u: (zx(640 + 640 * lin01(fr, 166, 19), u), zy(489, u), 160 * ZOOM(u), 760 * ZOOM(u), 8,
                           pulse(fr, 164, 4, 12, 6)))
    # Shine 2: a soft diagonal band runs down over it, 7.9-8.5 s.
    on_logo("Brillo 2", band("#FFF070", 1.0, angle=90, core=0.6),
            lambda fr, u: (zx(951 - 90 + 180 * lin01(fr, 236, 20), u), zy(250 + 470 * lin01(fr, 236, 20), u),
                           700 * ZOOM(u), 170 * ZOOM(u), -16, pulse(fr, 236, 5, 8, 7)))

    # The hot spot's light spills out: a short upright ray at the base of the logo.
    s.role(s.obj("Rayo vertical", band("#FFE680", 1.0, angle=0, core=0.3),
                 lambda fr, u: (zx(951, u), zy(835, u), 44, 200 * ZOOM(u), 0, 0.6 * hot(fr))), "art")
    # The long golden flare under the logo, 3.1-3.5 s.
    s.role(s.obj("Destello bajo el logo", band("#FFE07A", 0.85, core=0.5),
                 lambda fr, u: (zx(1100, u), zy(836, u), 560, 76, 0, pulse(fr, 92, 3, 6, 8))), "art")
    s.role(s.obj("Destello bajo el logo (núcleo)", radial("#FFE070", 1.0, 0.5),
                 lambda fr, u: (zx(951, u), zy(828, u), 420 * ZOOM(u), 60 * ZOOM(u), 0, hot(fr)),
                 kind="ellipse"), "art")

    # --- the address ---------------------------------------------------------------------------------------------
    ink = (643, 895, 1271, 933)

    def at_zoom(fr, u):
        sc = ZOOM(u)
        cx, cy = (ink[0] + ink[2]) / 2, (ink[1] + ink[3]) / 2
        return zx(cx, u) - cx, zy(cy, u) - cy, sc, 0, 1.0
    web = s.say(URL, ink, M, 700, BROWN, "Web", geom=at_zoom)
    web["layoutRole"] = "art"
    web["textStyle"]["animation"] = {"in": tanim("blur-in", duration=0.22, unit="character", stagger=0.014,
                                                 ease="easeOut", delay=4.5, order="random")}
    s.fx(web, "layer.color_overlay", color="#C8892E",
         animated={"opacity": lambda fr, u: 0.75 * (1 - k(fr, 142, 30)) + 0.35 * pulse(fr, 238, 8, 6, 14)})

    # --- out: fade to black --------------------------------------------------------------------------------------
    s.role(s.obj("Fundido", solid("#000000"), lambda fr, u: (960, 540, 1920, 1080, 0, lin01(fr, 281, 16))), "cover")
    return t


def lin01(fr, at, n):
    return min(1.0, max(0.0, (fr - at) / max(1e-6, n)))


TEMPLATES = [light_build]
