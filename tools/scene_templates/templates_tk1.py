"""TIKTOK folder video 1 as Stock templates (tk1-*). See docs/plan-tiktok.md.

«Typography opener» (34221988.mp4, 1920×1080 at 29.97 fps): one vertical opener, one word per beat on dark and light
grey, with photo flashes (a band, 2×2 and 4×2 grids, three strips over huge outlined letters, a negative statue),
liquid-paint reveals, stacked striped echoes and words that grow or shrink on the beat. The story is measured on the
phone screen (477×924 → 1080×1920, ×2.078) and laid out flat; the mockups, the Instagram frames and the info card are
not copied. The brand mark at the start and the end («BRAXXU», «ENVATO») is the user's logo slot; «MAKE SPARKS FLY»
becomes neutral words. Study notes: tienda/plantillas/estudio-34221988/NOTAS.md.

The sequence builder `Seq` (also used by templates_tk9) writes each word, shape and photo as its own short clip,
keyed every frame of its window, with times given in seconds of the reference story.
"""

from __future__ import annotations

import math

import templates_llt_f as f6
from kit import Box, tall
from scene import effect, fill, gradient, keys, no_stroke, us
from templates_tit_f import outline_layers

FPS = 30000 / 1001
W, H = 1080, 1920
M, P = "Montserrat", "Poppins"
for _w, _f in ((900, "Black"), (800, "ExtraBold"), (700, "Bold"), (600, "SemiBold"), (500, "Medium"),
               (400, "Regular")):
    f6._FILES[(M, _w)] = f"fonts.basic/fonts/montserrat/Montserrat-{_f}.ttf"
    f6._FILES[(P, _w)] = f"fonts.basic/fonts/poppins/Poppins-{_f}.ttf"


def ease(x):
    """Ease out (cubic), 0..1."""
    x = min(1.0, max(0.0, x))
    return 1 - (1 - x) ** 3


def ramp(u, a, n):
    """0 → 1 eased between seconds a and a + n."""
    return ease((u - a) / max(1e-6, n))


def steps(u, pts, n=0.067):
    """Values that jump on the beat: pts = [(second, value), ...]; each change eases over n seconds."""
    v = pts[0][1]
    for (a, va), (b, vb) in zip(pts, pts[1:]):
        if u >= b:
            v = vb
        elif u >= b - n:
            return va + (vb - va) * ease((u - (b - n)) / n)
        else:
            break
    return v


def argb(colour, a=1.0):
    return "#%02x%s" % (max(0, min(255, round(a * 255))), colour.lstrip("#").lower()[-6:])


def wave_path(n=24, amp=0.32):
    """A wavy band (the liquid paint) in a 0..100 box."""
    top = [(100 * i / n, 50 - 50 * (0.45 + amp * math.sin(i * 1.3))) for i in range(n + 1)]
    bot = [(100 * i / n, 50 + 50 * (0.45 - amp * math.sin(i * 1.3 + 0.9))) for i in reversed(range(n + 1))]
    return "M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y in top + bot) + " Z"


def dust_path(seed=11, n=46):
    """Small specks spread over the frame, as one path in the 0..100 box of a 1080×1920 clip."""
    import random
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        x, y, r = rnd.uniform(2, 98), rnd.uniform(2, 98), rnd.choice((2.5, 3, 4, 5, 7, 12))
        rx, ry = r / W * 100, r / H * 100
        pts = [(x + rx * math.cos(2 * math.pi * i / 8), y + ry * math.sin(2 * math.pi * i / 8)) for i in range(8)]
        out.append("M " + " L ".join(f"{a:.3f} {b:.3f}" for a, b in pts) + " Z")
    return " ".join(out)


class Seq:
    """A long opener: clips in short windows, times in seconds of the reference story (`off` = its template 0)."""

    def __init__(self, t, off=0.0):
        self.t, self.off = t, off
        t.layout_roles = True
        self.groups = {}

    def group(self, key, ttype, name, n=1):
        self.groups[key] = [self.t.track(ttype, name if n == 1 else f"{name} {i + 1}") for i in range(n)]

    def _track(self, key, t0, t1):
        a, b = us(t0 - self.off), us(t1 - self.off)
        for tr in self.groups[key]:
            if all(c["timelineStartUs"] + c["timelineDurationUs"] <= a + 2 or c["timelineStartUs"] >= b - 2
                   for c in tr.clips):
                return tr
        raise RuntimeError(f"no free track in {key} at {t0}")

    def times(self, t0, t1):
        d = t1 - t0
        n = max(1, int(round(d * FPS)))
        return [min(d, i / FPS) for i in range(n + 1)]

    @staticmethod
    def _keys(pts):
        if all(abs(v - pts[0][1]) < 1e-4 for _, v in pts):
            return keys([(0.0, round(pts[0][1], 4))])
        return keys([(u, round(v, 4), "linear") for u, v in pts])

    # --- text ------------------------------------------------------------------------------------------------
    def word(self, text, t0, t1, width, colour, m=None, cy=960, cx=540, font=(M, 800), sp=0.0, layers=None,
             key="txt", name="Texto", feather=60, mblur=False, editable=True, runs=None, role="art", angle=0.0):
        """A word whose ink is `width` px wide at rest (letter spacing sp em included); m(u, d) returns any of s
        (scale), dx, dy, op, blur (px), sp (em), wipe (linear wipe completion 0..100), rot."""
        fam, wt = font
        size, _ = f6.fit(text, width, fam, wt, sp)
        d = t1 - t0
        us_ = self.times(t0, t1)
        vals = []
        for u in us_:
            v = dict(s=1.0, dx=0.0, dy=0.0, op=1.0, blur=0.0, sp=sp, wipe=None, rot=0.0)
            if m:
                v.update(m(u, d))
            vals.append(v)
        n = max(1, len(text) - 1)
        wmax = max(v["s"] * (width + (v["sp"] - sp) * size * n) for v in vals)
        smax = max(v["s"] for v in vals)
        bw, bh = wmax + size * smax * 0.8, size * smax * 1.5
        tr = self._track(key, t0, t1)
        style_layers = layers or [fill(colour), no_stroke()]
        style = {"fontFamily": fam, "pixelSize": round(size, 2), "fontWeight": wt, "italic": False,
                 "layers": style_layers, "align": "center", "valign": "middle", "wordWrap": False, "lineHeight": 1.0,
                 "letterSpacing": round(sp * size, 3), "textCase": "none", "boxEnabled": False,
                 "boxColor": "#80000000", "boxPadding": 18, "boxRadius": 0, "accent": {"rule": "none"},
                 "animation": {}}
        clip = self.t.text(tr, text, t0 - self.off, d, Box(cx - bw / 2, cy - bh / 2, bw, bh), style,
                           label=text if name == "Texto" else f"{text} ({name.lower()})", editable=editable)
        clip["name"] = name
        clip["x"] = self._keys([(u, cx + v["dx"] - bw / 2) for u, v in zip(us_, vals)])
        clip["y"] = self._keys([(u, cy + v["dy"] - bh / 2) for u, v in zip(us_, vals)])
        kf = {"pixelSize": self._keys([(u, size * v["s"]) for u, v in zip(us_, vals)]),
              "letterSpacing": self._keys([(u, v["sp"] * size * v["s"]) for u, v in zip(us_, vals)])}
        style["keyframes"] = {k_: v_ for k_, v_ in kf.items() if len(v_["keyframes"]) > 1}
        self._common(clip, us_, vals, feather, angle)
        if mblur:
            clip["motionBlur"] = True
        if runs:
            style["runs"] = runs
        clip["layoutRole"] = role
        return clip

    def _common(self, clip, us_, vals, feather=60, angle=0.0):
        if any(v["op"] < 0.999 for v in vals):
            clip["opacity"] = self._keys([(u, max(0.0, min(1.0, v["op"]))) for u, v in zip(us_, vals)])
        if any(abs(v.get("rot", 0.0)) > 1e-6 for v in vals):
            clip["rotation"] = self._keys([(u, v.get("rot", 0.0)) for u, v in zip(us_, vals)])
        if any(v.get("blur", 0) > 0.05 for v in vals):
            clip.setdefault("effects", []).append(effect(
                "builtin.effects.gaussian_blur",
                {"u_blurRadius": self._keys([(u, v.get("blur", 0.0)) for u, v in zip(us_, vals)])}, u_blurRadius=0.0))
        if any(v.get("wipe") is not None for v in vals):
            clip.setdefault("effects", []).append(effect(
                "ae.linear_wipe", {"completion": self._keys([(u, v["wipe"] if v.get("wipe") is not None else 0.0)
                                                             for u, v in zip(us_, vals)])},
                completion=0.0, angle=angle, feather=feather))

    # --- shapes ----------------------------------------------------------------------------------------------
    def rect(self, t0, t1, r, colour="#000000", layers=None, key="shp", name="Forma", kind="rectangle", path=None,
             m=None, role="art", radius=0.0):
        """A box covering r(u, d) = (x0, y0, x1, y1); m(u, d) may give op, rot, blur."""
        d = t1 - t0
        us_ = self.times(t0, t1)
        rs = [r(u, d) for u in us_]
        vals = []
        for u in us_:
            v = dict(op=1.0, rot=0.0, blur=0.0)
            if m:
                v.update(m(u, d))
            vals.append(v)
        bw = max(1.0, max(x1 - x0 for x0, y0, x1, y1 in rs))
        bh = max(1.0, max(y1 - y0 for x0, y0, x1, y1 in rs))
        box = Box(540 - bw / 2, 960 - bh / 2, bw, bh)
        motion = [(u, {"sx": max(1e-4, (x1 - x0) / bw), "sy": max(1e-4, (y1 - y0) / bh),
                       "dx": (x0 + x1) / 2 - 540, "dy": (y0 + y1) / 2 - 960}, "linear")
                  for u, (x0, y0, x1, y1) in zip(us_, rs)]
        if all(mo[1] == motion[0][1] for mo in motion):
            motion = [motion[0]]
        tr = self._track(key, t0, t1)
        clip = self.t.solid(tr, colour, t0 - self.off, d, box, motion, kind=kind, layers=layers, radius=radius)
        clip["name"] = name
        if path:
            clip["shapeStyle"]["kind"] = "custom"
            clip["shapeStyle"]["customPath"] = path
            clip["shapeStyle"]["customEvenOdd"] = False
        self._common(clip, us_, vals)
        clip["layoutRole"] = role
        return clip

    def bg(self, t0, t1, colour, key="bg"):
        return self.rect(t0, t1, lambda u, d: (-20, -20, W + 20, H + 20), colour, key=key, name="Fondo", role="cover")

    # --- photos ----------------------------------------------------------------------------------------------
    def pic(self, sample, t0, t1, box, m=None, key="foto", name="Foto", label=None, reuse=None, mask=None, fx=(),
            role="art", mask_shape="rectangle", feather=0.0):
        """A photo slot laid out in box = (x0, y0, x1, y1), cover crop; m(u, d) gives s, dx, dy, op, blur;
        mask(u, d) = the screen rect it shows in."""
        d = t1 - t0
        us_ = self.times(t0, t1)
        vals = []
        for u in us_:
            v = dict(s=1.0, dx=0.0, dy=0.0, op=1.0, blur=0.0)
            if m:
                v.update(m(u, d))
            vals.append(v)
        x0, y0, x1, y1 = box
        b = Box(x0, y0, x1 - x0, y1 - y0)
        motion = [(u, {"s": v["s"], "dx": v["dx"], "dy": v["dy"]}, "linear") for u, v in zip(us_, vals)]
        if all(mo[1] == motion[0][1] for mo in motion):
            motion = [motion[0]] if motion[0][1] != {"s": 1.0, "dx": 0.0, "dy": 0.0} else None
        tr = self._track(key, t0, t1)
        clip = self.t.photo(tr, sample, t0 - self.off, d, b, motion, label=label, reuse=reuse)
        clip["name"] = name
        for e in fx:
            clip.setdefault("effects", []).append(e)
        self._common(clip, us_, vals)
        if mask:
            mk = {"x": [], "y": [], "w": [], "h": []}
            for u, v in zip(us_, vals):
                mx0, my0, mx1, my1 = mask(u, d)
                bw_, bh_ = b.w * v["s"], b.h * v["s"]
                bx = b.x + b.w / 2 + v["dx"] - bw_ / 2
                by = b.y + b.h / 2 + v["dy"] - bh_ / 2
                mk["x"].append((u, ((mx0 + mx1) / 2 - bx) / bw_))
                mk["y"].append((u, ((my0 + my1) / 2 - by) / bh_))
                mk["w"].append((u, max(0.0, mx1 - mx0) / bw_))
                mk["h"].append((u, max(0.0, my1 - my0) / bh_))
            self.t.mask(tr, clip, mask_shape, feather=feather, x=mk["x"][0][1], y=mk["y"][0][1], w=mk["w"][0][1],
                        h=mk["h"][0][1], keyframes={k_: self._keys(v_) for k_, v_ in mk.items()})
        clip["layoutRole"] = role
        return clip

    def d3(self, clip, t0, t1, ry=None, rx=None, persp=1600):
        """A 3D turn on a clip: ry / rx(u, d) in degrees, every frame of its window."""
        clip["layer3d"] = True
        us_ = self.times(t0, t1)
        for key_, fn in (("rotationY", ry), ("rotationX", rx)):
            if fn:
                clip[key_] = self._keys([(u, fn(u, t1 - t0)) for u in us_])
        clip["perspective"] = keys([(0.0, float(persp), "hold")])
        return clip

    def adjust(self, t0, t1, fx):
        """An adjustment layer over everything in [t0, t1]; fx = [(catalog id, {param: fn(u, d)}, fixed params)]."""
        us_ = self.times(t0, t1)
        effects = [effect(cid, {k_: self._keys([(u, fn(u, t1 - t0)) for u in us_]) for k_, fn in anim.items()},
                          **fixed) for cid, anim, fixed in fx]
        clip = self.t.adjust(effects, t0 - self.off, t1 - t0, name="Transición")
        return clip

    def logo(self, t0, t1, box, m=None, key="logo", feather=60):
        """The user's logo slot in box (x0, y0, x1, y1); m as in pic, plus wipe."""
        d = t1 - t0
        us_ = self.times(t0, t1)
        vals = []
        for u in us_:
            v = dict(s=1.0, dx=0.0, dy=0.0, op=1.0, blur=0.0, wipe=None)
            if m:
                v.update(m(u, d))
            vals.append(v)
        x0, y0, x1, y1 = box
        b = Box(x0, y0, x1 - x0, y1 - y0)
        motion = [(u, {"s": v["s"], "dx": v["dx"], "dy": v["dy"]}, "linear") for u, v in zip(us_, vals)]
        tr = self._track(key, t0, t1)
        first = next((sl.id for sl in self.t.slots if sl.sample == "logo-flip"), None)
        clip = self.t.photo(tr, "logo-flip", t0 - self.off, d, b, motion, label="Tu logo", brandRole="logo",
                            reuse=first)
        clip["name"] = "Tu logo"
        self._common(clip, us_, vals, feather)
        clip["layoutRole"] = "art"
        return clip

    # --- recipes ---------------------------------------------------------------------------------------------
    def stripes(self, t0, t1, cy, size, x0, x1, colour, n=6, m=None, thick=0.05):
        """Thin bars of the background colour across a word (its ink cut in slices)."""
        span = 0.72 * size + thick * size  # the bars' block, one path
        bars = []
        for i in range(n):
            c = 50 + (i - (n - 1) / 2) * 0.72 * size / (n - 1) / span * 100
            hh = thick * size / span * 50
            bars.append(f"M 0 {c - hh:.3f} L 100 {c - hh:.3f} L 100 {c + hh:.3f} L 0 {c + hh:.3f} Z")

        def r(u, d):
            s = (m(u, d).get("s", 1.0) if m else 1.0)
            dy = (m(u, d).get("dy", 0.0) if m else 0.0)
            y = cy + dy - size * 0.04 * s
            return 540 + (x0 - 540) * s, y - span * s / 2, 540 + (x1 - 540) * s, y + span * s / 2
        self.rect(t0, t1, r, colour, key="raya", name="Rayas", path=" ".join(bars))

    def paint(self, t0, reveal, x0, x1, cy, h, colours=("#FFFFFF", "#FFF6D8", "#FFB45A")):
        """The liquid paint wave that runs ahead of a wipe from x0 to x1 over `reveal` seconds."""
        stops = [(0.0, colours[0]), (0.75, colours[0]), (0.88, colours[1]), (1.0, colours[2])]
        lay = [gradient(stops, angle=0), no_stroke()]

        def r(u, d):
            p = ramp(u, 0, reveal)
            front = x0 + (x1 - x0) * p
            hh = h * (1.0 - 0.75 * p)
            return front - 40, cy - hh / 2 + 18 * math.sin(u * 22), x1 + 60 * (1 - p) + 10, cy + hh / 2
        self.rect(t0, t0 + reveal + 0.1, r, layers=lay, key="fx", name="Pintura", path=wave_path(),
                  m=lambda u, d: dict(op=1.0 - ramp(u, reveal * 0.7, 0.2)))


# ==================================================================================================================

DARK, LIGHT = "#16161E", "#E0E5EB"
ON_DARK, ON_LIGHT = "#E6EBF0", "#16161E"
OUTLINE = "#5C606C"
BAND = (0, 416, W, 1504)


def grow_steps(pts, blur0=8.0):
    """Scale jumps on the beat; blurred while it jumps."""
    def m(u, d):
        s = steps(u, pts)
        growing = any(b - 0.067 <= u < b and vb > va for (a, va), (b, vb) in zip(pts, pts[1:]))
        first = u < 0.034 and pts[0][1] < 0.9
        return dict(s=s, blur=blur0 if (first or growing) else 0.0)
    return m


def slide_left(scale_pts=((0.0, 1.2), (0.1, 1.0)), dist=-900):
    def m(u, d):
        return dict(dx=dist * (1 - ramp(u, 0, 0.1)), s=steps(u, list(scale_pts)))
    return m


def typography():
    off, end = 0.70, 28.80
    D = round(end - off, 2)
    t = tall("tk1-tipografia", "Apertura tipográfica: una palabra por golpe", "Typography opener: one word per beat",
             "tiktok", D, order=14100, tags=["tiktok", "historia", "reels", "apertura", "tipografía", "palabras",
                                             "blanco y negro"], thumb_at=round(9.9 - off, 2))
    s = Seq(t, off)
    s.group("bg", "shape", "Fondo")
    s.group("deco", "text", "Letras de fondo", 1)
    s.group("foto", "video", "Foto", 8)
    s.group("txt", "text", "Texto", 3)
    s.group("raya", "shape", "Rayas", 3)
    s.group("fx", "shape", "Pintura", 1)
    s.group("logo", "video", "Logo", 1)
    s.group("dust", "shape", "Polvo", 1)

    # backgrounds, in order
    for a, b, c in ((0.70, 1.80, DARK), (1.80, 2.40, LIGHT), (2.40, 3.50, DARK), (3.50, 4.40, LIGHT),
                    (4.40, 7.40, DARK), (7.40, 8.50, LIGHT), (8.50, 9.00, DARK), (9.00, 9.60, LIGHT),
                    (9.60, 12.50, DARK), (12.50, 13.60, LIGHT), (13.60, 15.60, DARK), (15.60, 16.00, LIGHT),
                    (16.00, 16.60, DARK), (16.60, 17.60, LIGHT), (17.60, 18.40, DARK), (18.40, 19.50, LIGHT),
                    (19.50, 21.00, DARK), (21.00, 22.30, LIGHT), (22.30, 22.90, DARK), (22.90, 23.80, LIGHT),
                    (23.80, 24.60, DARK), (24.60, 25.70, LIGHT), (25.70, end, DARK)):
        s.bg(a, b, c)
    s.rect(off, end, lambda u, d: (0, -30 * u / d, W, H - 30 * u / d), "#8C919C", key="dust", name="Polvo",
           path=dust_path(), m=lambda u, d: dict(op=0.45), role="backdrop")

    def liquid(text, t0, t1, width, colour, reveal_at, reveal, sp=0.12, size_mul=1.0):
        size, _ = f6.fit(text, width, M, 800, sp)
        s.word(text, t0, t1, width, colour, sp=sp, feather=90,
               m=lambda u, d: dict(wipe=100 * (1 - ramp(u, reveal_at - t0, reveal)), s=1 + 0.03 * u / d))
        s.paint(reveal_at, reveal, 540 - width / 2, 540 + width / 2, 960, size * 0.8)

    # 0.70 the brand mark (the user's logo) drawn by the paint
    s.logo(0.70, 1.80, (360, 780, 720, 1140), feather=90,
           m=lambda u, d: dict(wipe=100 * (1 - ramp(u, 0.0, 0.57)), s=1 + 0.03 * u / d))
    s.paint(0.70, 0.57, 360, 720, 960, 220)
    # 1.80 PRESENTS shrinks on the beat
    s.word("PRESENTS", 1.80, 2.40, 920, ON_LIGHT, grow_steps([(0, 1.0), (0.37, 0.57), (0.5, 0.51)]))
    s.word("BRAND", 2.40, 3.00, 656, ON_DARK, grow_steps([(0, 0.5), (0.04, 0.82), (0.3, 1.0)]))
    s.word("NEW", 3.00, 3.50, 432, ON_DARK, grow_steps([(0, 0.54), (0.2, 1.0)]))
    # 3.50 RHYTHM with striped echoes above (3.8) and below (4.1)
    size = f6.fit("RHYTHM", 808, M, 900)[0]
    s.word("RHYTHM", 3.50, 4.40, 808, ON_LIGHT, font=(M, 900))
    s.word("RHYTHM", 3.80, 4.40, 808, ON_LIGHT, cy=960 - size * 0.82, font=(M, 900), name="Eco")
    s.word("RHYTHM", 4.10, 4.40, 808, ON_LIGHT, cy=960 + size * 0.82, font=(M, 900), name="Eco 2")
    s.stripes(3.80, 4.40, 960 - size * 0.82, size, 120, 960, LIGHT)
    s.stripes(4.10, 4.40, 960 + size * 0.82, size, 120, 960, LIGHT)

    def echo_word(text, t0, t_join, t1, big_w, rest_w, rest_pts):
        """Huge letter-spaced word with outline copies above and below, sliding left; joins at t_join."""
        bsize = f6.fit(text, big_w, M, 800, 0.18)[0]
        dxf = lambda u: 900 * (1 - ramp(u, 0, 0.1)) + 120 - 220 * u  # noqa: E731
        s.word(text, t0, t_join, big_w, ON_DARK, sp=0.18, m=lambda u, d: dict(dx=dxf(u), blur=8 if u < 0.07 else 0),
               mblur=True)
        for i, dy in enumerate((-0.55, 0.55)):
            s.word(text, t0 + 0.03, t_join, big_w, ON_DARK, sp=0.18, cy=960 + dy * bsize, name=f"Eco {i + 1}",
                   layers=outline_layers(OUTLINE, 2), key="txt",
                   m=lambda u, d: dict(dx=dxf(u + 0.03), op=0.8))
        m = grow_steps(rest_pts)
        rs = f6.fit(text, rest_w, M, 900)[0]
        s.word(text, t_join, t1, rest_w, ON_DARK, m, font=(M, 900))
        s.stripes(t_join, t1, 960, rs, 540 - rest_w / 2 - 20, 540 + rest_w / 2 + 20, DARK, n=5, m=m, thick=0.035)

    echo_word("PROJECT", 4.43, 4.80, 5.20, 2900, 760, [(0, 1.35), (0.05, 1.0)])
    s.word("MODERN", 5.20, 5.67, 736, ON_DARK, grow_steps([(0, 0.54), (0.3, 1.0)]))
    s.word("BE BOLD", 5.80, 6.07, 864, ON_DARK, grow_steps([(0, 1.38), (0.1, 1.16), (0.2, 1.0)]))
    s.word("CREATIVE", 6.20, 6.47, 904, ON_DARK, slide_left(((0, 1.3), (0.14, 1.0)), dist=-500), mblur=True)

    # 6.50 photo 1: a band, then 2×2, then 4×2
    p1 = s.pic("fx-cyber-02", 6.50, 6.90, BAND, m=lambda u, d: dict(s=1.0 + 0.08 * u / d), label="Foto 1")
    slot1 = p1["placeholderId"]
    for (a, b, cols) in ((6.90, 7.00, 2), (7.00, 7.40, 4)):
        cw, ch = W / cols, (BAND[3] - BAND[1]) / 2
        for r_ in range(2):
            for c_ in range(cols):
                s.pic("fx-cyber-02", a, b, (c_ * cw, BAND[1] + r_ * ch, (c_ + 1) * cw, BAND[1] + (r_ + 1) * ch),
                      reuse=slot1, name="Foto 1 (copia)")

    liquid("AND", 7.40, 8.50, 600, ON_LIGHT, 7.50, 0.30, sp=0.06)
    s.word("UNIQUE", 8.50, 8.97, 704, ON_DARK, grow_steps([(0, 0.51), (0.1, 0.8), (0.3, 1.0)]))
    s.word("BREAK", 9.00, 9.30, 848, ON_LIGHT, grow_steps([(0, 1.0), (0.1, 0.84), (0.2, 0.74)]))
    s.word("THE", 9.30, 9.60, 488, ON_LIGHT, grow_steps([(0, 1.0), (0.1, 0.8), (0.2, 0.69)]))
    # 9.60 STEREOTYPES slides in; faint copies above and below from 10.0
    ss = f6.fit("STEREOTYPES", 952, M, 800)[0]
    s.word("STEREOTYPES", 9.60, 10.50, 952, ON_DARK, slide_left(((0, 1.25), (0.15, 1.0)), dist=-500), mblur=True)
    for i, dy in enumerate((-0.5, 0.5)):
        s.word("STEREOTYPES", 10.0, 10.50, 952, ON_DARK, cy=960 + dy * ss, name=f"Eco {i + 1}",
               m=lambda u, d: dict(op=0.25))

    def big_letters(text, t0, t1):
        s.word(text, t0, t1, 2600, OUTLINE, key="deco", name="Letras de fondo", layers=outline_layers(OUTLINE, 2),
               m=lambda u, d: dict(rot=-62, dx=-60 + 120 * u / d, dy=-40, op=0.7), editable=False, role="backdrop")

    def strips(sample, t0, t1, xs, order, label):
        big_letters("STEREOTYPES" if label == "Foto 2" else "PROJECT", t0, t1)
        first = None
        for i, (x0, x1) in enumerate(xs):
            at = order[i]
            clip = s.pic(sample, t0 + at, t1, (xs[0][0], BAND[1], xs[-1][1], BAND[3]), reuse=first,
                         label=label if first is None else None, mask=lambda u, d, x0=x0, x1=x1: (x0, BAND[1], x1, BAND[3]),
                         name=label if first is None else f"{label} (tira)")
            first = first or clip["placeholderId"]

    strips("fx-woman-06", 10.53, 11.17, [(84, 360), (384, 684), (708, 990)], (0.13, 0.0, 0.3), "Foto 2")
    neg = [effect("duotone", strength=1.0, shadowColor="#E9ECF6", highlightColor="#20232E", contrast=0.6)]
    p3 = s.pic("fx-face-05", 11.17, 11.33, BAND, label="Foto 3", fx=neg)
    s.pic("fx-face-05", 11.33, 11.50, (184, 608, 896, 1312), reuse=p3["placeholderId"], fx=neg, name="Foto 3 (cuadro)")
    s.word("EXPRESS", 11.50, 11.97, 792, ON_DARK, grow_steps([(0, 0.5), (0.3, 0.92), (0.4, 1.0)]))
    s.word("YOURSELF", 12.10, 12.47, 928, ON_DARK, slide_left(((0, 1.2), (0.17, 1.0))), mblur=True)

    def striped(text, t0, t1, width, pts, colour=ON_LIGHT, bgc=LIGHT):
        m = lambda u, d: dict(s=steps(u, pts, 0.1))  # noqa: E731
        sz = f6.fit(text, width, M, 900)[0]
        s.word(text, t0, t1, width, colour, m, font=(M, 900))
        s.stripes(t0, t1, 960, sz, 540 - width / 2 - 20, 540 + width / 2 + 20, bgc, n=5, m=m, thick=0.04)

    striped("WITH", 12.50, 13.00, 688, [(0, 0.71), (0.2, 0.8), (0.3, 0.96), (0.4, 1.0)])
    striped("YOUR", 13.00, 13.60, 736, [(0, 0.7), (0.2, 0.76), (0.3, 0.92), (0.4, 0.98), (0.5, 1.0)])
    echo_word("FRESH", 13.62, 13.90, 14.35, 1900, 528, [(0, 1.25), (0.1, 1.0), (0.3, 0.94)])
    liquid("INCREDIBLE", 14.40, 15.60, 976, ON_DARK, 14.42, 0.6, sp=0.1)
    s.word("IDEAS", 15.60, 16.00, 544, ON_LIGHT, grow_steps([(0, 0.8), (0.2, 1.0)]))
    s.word("DON'T", 16.00, 16.30, 808, ON_DARK, grow_steps([(0, 1.0), (0.1, 0.9), (0.2, 0.73)]))
    s.word("FOLLOW", 16.30, 16.60, 1088, ON_DARK, grow_steps([(0, 1.0), (0.1, 0.88), (0.2, 0.72)]))
    # 16.60 RULES: striped, shrinks, then echoes above (17.1) and below (17.3)
    rs_ = f6.fit("RULES", 768, M, 900)[0]
    rp = [(0, 1.0), (0.2, 0.74), (0.3, 0.71)]
    striped("RULES", 16.60, 17.60, 768, rp)
    for i, (a, dy) in enumerate(((17.1, -0.6), (17.3, 0.6))):
        cy = 960 + (-150 if dy < 0 else 150)
        s.word("RULES", a, 17.60, 768 * 0.71, ON_LIGHT, cy=cy, font=(M, 900), name=f"Eco {i + 1}")
        s.stripes(a, 17.60, cy, rs_ * 0.71, 540 - 300, 540 + 300, LIGHT, n=5, thick=0.04)

    def rise(text, t0, t1, width, s_big):
        s.word(text, t0, t1, width, ON_DARK,
               m=lambda u, d: dict(dy=90 * (1 - ramp(u, 0, 0.1)), s=steps(u, [(0, s_big), (0.2, 1.0)]),
                                   blur=8 if u < 0.1 else 0), mblur=True)

    rise("GET", 17.60, 18.00, 360, 1.45)
    rise("YOUR", 18.00, 18.40, 536, 1.48)
    s.word("BRAND", 18.40, 18.90, 664, ON_LIGHT, grow_steps([(0, 0.61), (0.1, 0.81), (0.3, 1.0)]))
    s.word("NOTICED", 18.90, 19.50, 824, ON_LIGHT, grow_steps([(0, 0.51), (0.1, 0.8), (0.4, 1.0)]))
    thick = [fill(DARK), {"id": "stroke", "kind": "stroke", "enabled": True, "width": 12, "strokeAlign": "outside",
                          "opacity": 1.0, "paint": {"kind": "solid", "color": argb("#C9CED8")}}]
    s.word("YOU", 19.50, 20.10, 752, ON_DARK, layers=thick,
           m=lambda u, d: dict(op=1.0 - 0.55 * u / d, s=1.0 - 0.04 * u / d))
    s.word("YOU", 19.50, 20.10, 752, ON_DARK, layers=outline_layers("#8A8F9C", 2), name="Eco",
           m=lambda u, d: dict(op=0.8 - 0.4 * u / d, s=0.96 - 0.04 * u / d))
    # 20.10 photo 4: band, then 2×2
    p4 = s.pic("fx-woman-03", 20.10, 20.50, BAND, m=lambda u, d: dict(s=1.0 + 0.06 * u / d), label="Foto 4")
    cw, ch = W / 2, (BAND[3] - BAND[1]) / 2
    for r_ in range(2):
        for c_ in range(2):
            s.pic("fx-woman-03", 20.50, 21.00, (c_ * cw, BAND[1] + r_ * ch, (c_ + 1) * cw, BAND[1] + (r_ + 1) * ch),
                  reuse=p4["placeholderId"], name="Foto 4 (copia)")
    liquid("CAN", 21.00, 22.30, 600, ON_LIGHT, 21.10, 0.4, sp=0.14)
    s.word("CREATE", 22.30, 22.60, 984, ON_DARK, grow_steps([(0, 1.0), (0.1, 0.83), (0.2, 0.73)]))
    s.word("ONE", 22.60, 22.90, 528, ON_DARK, grow_steps([(0, 1.0), (0.1, 0.88), (0.2, 0.73)]))
    ys_ = f6.fit("YOUR", 720, M, 900)[0]
    striped("YOUR", 22.90, 23.80, 720, [(0, 1.0), (0.1, 0.78), (0.2, 0.73), (0.3, 0.72)])
    for i, (a, dy) in enumerate(((23.3, -0.6), (23.5, 0.6))):
        cy = 960 + (-150 if dy < 0 else 150)
        s.word("YOUR", a, 23.80, 720 * 0.72, ON_LIGHT, cy=cy, font=(M, 900), name=f"Eco {i + 1}")
        s.stripes(a, 23.80, cy, ys_ * 0.72, 540 - 290, 540 + 290, LIGHT, n=5, thick=0.04)
    s.word("BEST", 23.90, 24.20, 672, ON_DARK, grow_steps([(0, 1.0), (0.1, 0.77), (0.2, 0.64)]))
    s.word("VIDEO", 24.30, 24.60, 848, ON_DARK, grow_steps([(0, 1.0), (0.1, 0.78), (0.2, 0.68)], blur0=10))
    s.word("WITH", 24.60, 25.20, 504, ON_LIGHT, grow_steps([(0, 0.52), (0.1, 0.81), (0.3, 0.89), (0.4, 1.0)]))
    s.word("THIS", 25.20, 25.70, 408, ON_LIGHT, grow_steps([(0, 0.8), (0.3, 1.0)]))
    # 25.70 PROJECT in outline with echoes slid sideways, letter-spaced, then joined
    pm = lambda u, d: dict(s=steps(u, [(0, 1.75), (0.4, 1.15), (0.5, 1.0)]))  # noqa: E731
    s.word("PROJECT", 25.70, 26.30, 752, ON_DARK, pm, sp=0.08, layers=outline_layers("#C9CED8", 3))
    for i, dx in enumerate((-14, 16)):
        s.word("PROJECT", 25.70, 26.10, 752, ON_DARK, lambda u, d, dx=dx: dict(pm(u, d), dx=dx * (1 + math.sin(u * 40)),
                                                                              op=0.6), sp=0.08, name=f"Eco {i + 1}",
               layers=outline_layers("#7A7F8C", 2))
    strips("fx-fashion-04", 26.30, 26.80, [(88, 382), (397, 691), (706, 1000)], (0.0, 0.0, 0.0), "Foto 5")
    s.pic("fx-face-05", 26.80, 27.20, (208, 608, 904, 1312), reuse=p3["placeholderId"], fx=neg,
          name="Foto 3 (cuadro 2)")

    # 27.20 the end card: the user's logo and a tagline slide in from the left
    sl = lambda u, d: dict(dx=-700 * (1 - ramp(u, 0, 0.13)), blur=6 if u < 0.1 else 0)  # noqa: E731
    s.logo(27.20, end, (360, 740, 720, 1100), m=sl)
    s.word("YOUR TAGLINE HERE", 27.20, end, 640, ON_DARK, sl, cy=1150, font=(M, 800), sp=0.06, mblur=True,
           name="Lema")
    return t


TEMPLATES = [typography]
