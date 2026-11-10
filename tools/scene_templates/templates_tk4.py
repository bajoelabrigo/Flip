"""TIKTOK folder video 4 as Stock templates (tk4-*). See docs/plan-tiktok.md.

«Instagram slideshow pack» (4714855.mp4, 1920×1080 at 29.97 fps, 175 s): six vertical openers (stomp, typo,
dynamic, fast, rhythm, modern), each shown on a 458×888 story screen beside an info card and then finished on three
Instagram phones. Each opener is one template: the screen part and the end the phones show, laid out on 1080×1920
(×2.162 from the screen; ×7.73 from the 128 px tiles of the 10 fps study sheets). One word per beat over photos and
colours, as the reference, cut for cut. Photos are slots filled with our samples; the brand logo at the end is the
user's `logo-flip` slot. Study notes in tienda/plantillas/estudio-4714855/NOTAS.md.
"""

from __future__ import annotations

import math
import random

import templates_llt_f as f6
from kit import Box, tall
from scene import effect, fill, gradient, keys, no_stroke, shadow, tanim, text_style

FPS = 29.97
W, H = 1080, 1920
WHITE, BLACK = "#FFFFFF", "#000000"
M = "Montserrat"
for _w, _f in ((900, "Black"), (800, "ExtraBold"), (700, "Bold"), (600, "SemiBold"), (500, "Medium"),
               (400, "Regular")):
    f6._FILES[(M, _w)] = f"fonts.basic/fonts/montserrat/Montserrat-{_f}.ttf"

TAGLINE = "Your tagline here"
TRIANGLE = "M 0 0 L 100 50 L 0 100 Z"


def poly(points):
    return "M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y in points) + " Z"


PLUS = poly([(40, 0), (60, 0), (60, 40), (100, 40), (100, 60), (60, 60), (60, 100), (40, 100), (40, 60), (0, 60),
             (0, 40), (40, 40)])
CHEVRONS = (poly([(0, 40), (50, 0), (100, 40), (100, 54), (50, 14), (0, 54)]) + " " +
            poly([(0, 86), (50, 46), (100, 86), (100, 100), (50, 60), (0, 100)]))


def dot_grid(cols, rows, dot=0.32):
    out = []
    for i in range(cols):
        for j in range(rows):
            x0, y0 = 100 * i / cols, 100 * j / rows
            dx, dy = 100 / cols * dot, 100 / rows * dot
            out.append(poly([(x0, y0), (x0 + dx, y0), (x0 + dx, y0 + dy), (x0, y0 + dy)]))
    return " ".join(out)


def argb(colour, alpha=1.0):
    return f"#{max(0, min(255, round(alpha * 255))):02x}{colour.lstrip('#').lower()[-6:]}"


def solid(colour, alpha=1.0):
    return [fill(colour, alpha), no_stroke()]


def outline(colour, width=3.0):
    return [{"id": "fill", "kind": "fill", "enabled": False, "paint": {"kind": "solid", "color": "#00000000"}},
            {"id": "stroke", "kind": "stroke", "enabled": True, "width": width, "strokeAlign": "outside",
             "opacity": 1.0, "paint": {"kind": "solid", "color": argb(colour)}}]


def grad(c0, c1, angle=0.0):
    return [gradient([(0.0, c0), (1.0, c1)], angle=angle)]


def stripes(on, off, n=16):
    """Horizontal lines of `on` on `off`: the «text texture» fill of the typo opener."""
    stops = []
    for i in range(n):
        a, b, c = i / n, (i + 0.55) / n, (i + 1) / n
        stops += [(a, on), (b, on), (min(1.0, b + 0.001), off), (c, off)]
    return [gradient(stops, angle=90)]


def shade(colour=BLACK, alpha=0.35, blur=18, dy=6):
    return shadow(colour, 0, dy, blur, alpha)


def duo(dark, light, strength=1.0, contrast=0.55):
    return effect("duotone", strength=strength, shadowColor=dark, highlightColor=light, contrast=contrast)


RED_DUO = duo("#1A0003", "#FF1B2D")
YELLOW_DUO = duo("#14120A", "#F3E33A")
GREY = effect("stylize.grayscale")


class Reel:
    """An opener on 1080×1920: every clip is placed between two reference frames (absolute numbers of the video);
    `f0` is the frame the template starts at. Clips go on pooled lanes per layer group, so the timeline keeps a few
    tracks in a fixed order (backgrounds under photos under words)."""

    GROUPS = (("bg", "shape", "Fondo", 3), ("pic", "video", "Foto", 4), ("tint", "shape", "Tinte", 2),
              ("band", "shape", "Banda", 3), ("ghost", "text", "Palabra de fondo", 3), ("word", "text", "Palabra", 7),
              ("fill", "video", "Foto en las letras", 4), ("deco", "shape", "Adornos", 6), ("top", "shape", "Barrido", 2))

    def __init__(self, t, f0):
        self.t, self.f0 = t, f0
        self.lanes = {g: [[t.track(kind, name), -1.0] for _ in range(n)] for g, kind, name, n in self.GROUPS}

    def s(self, fr):
        return max(0.0, (fr - self.f0) / FPS)

    def skip(self, n):
        """The reference has `n` frames (an info card) that the template leaves out: later frames come earlier."""
        self.f0 += n

    def lane(self, group, t0, t1):
        for lane in self.lanes[group]:
            if lane[1] <= t0 + 1e-6:
                lane[1] = t1
                return lane[0]
        kind = self.lanes[group][0][0].type
        name = self.lanes[group][0][0].name
        track = self.t.track(kind, name)
        # keep the group order: move the new track right above the group's last one
        self.t.tracks.remove(track)
        last = self.lanes[group][-1][0]
        self.t.tracks.insert(self.t.tracks.index(last) + 1, track)
        self.lanes[group].append([track, t1])
        return track

    def finish(self):
        self.t.tracks = [tr for tr in self.t.tracks if tr.clips or tr.type == "audio"]
        return self.t

    # --- motion -----------------------------------------------------------------------------------------------
    def path(self, a, b, enter=None, exit=None, mv=None, sc=None):
        """Key frames (clip seconds, dx, dy, scale) between a and b: enter / exit = (dx, dy, frames) whips in from /
        out to an offset; mv = [(frame, dx, dy)] and sc = [(frame, scale)] pieces in between."""
        frames = {a, b}
        pts_d = []
        if enter:
            pts_d += [(a, enter[0], enter[1]), (a + enter[2], 0.0, 0.0)]
        for p in mv or []:
            pts_d.append(p)
        if exit:
            last = pts_d[-1][1:] if pts_d and pts_d[-1][0] <= b - exit[2] else (0.0, 0.0)
            pts_d += [(b - exit[2], *last), (b, exit[0], exit[1])]
        sc = sc or []
        for p in pts_d:
            frames.add(p[0])
        for p in sc:
            frames.add(p[0])
        frames = sorted(f for f in frames if a <= f <= b)

        def lerp(pts, fr, i0):
            if not pts:
                return (0.0,) * i0
            pts = sorted(pts, key=lambda p: p[0])
            if fr <= pts[0][0]:
                return tuple(pts[0][1:])
            for p, q in zip(pts, pts[1:]):
                if fr <= q[0]:
                    u = (fr - p[0]) / max(1e-6, q[0] - p[0])
                    return tuple(x + (y - x) * u for x, y in zip(p[1:], q[1:]))
            return tuple(pts[-1][1:])
        t0 = self.s(a)
        out = []
        for fr in frames:
            dx, dy = lerp(pts_d, fr, 2)
            (s,) = lerp(sc, fr, 1) if sc else (1.0,)
            out.append((self.s(fr) - t0, dx, dy, s))
        return out

    def motion(self, path):
        if len(path) == 2 and all(abs(p[1]) < 1e-6 and abs(p[2]) < 1e-6 and abs(p[3] - 1) < 1e-6 for p in path):
            return None
        return [(p[0], {"dx": p[1], "dy": p[2], "s": p[3]}, "linear") for p in path]

    def anim(self, clip, a, prop, pts):
        """Keys a clip property from [(frame, value)] (opacity, rotation)."""
        t0 = self.s(a)
        clip[prop] = keys([(max(0.0, self.s(fr) - t0), v, "linear") for fr, v in pts])

    def hold_op(self, clip, a, spans):
        """Opacity 1 inside the [(f0, f1)] spans, 0 elsewhere (a flicker between two copies)."""
        t0 = self.s(a)
        pts = [(0.0, 0.0, "hold")]
        for f0, f1 in spans:
            pts += [(max(0.0, self.s(f0) - t0), 1.0, "hold"), (max(0.0, self.s(f1) - t0), 0.0, "hold")]
        clip["opacity"] = keys(sorted(pts, key=lambda p: p[0]))

    def fx(self, clip, a, catalog_id, animated=None, **params):
        t0 = self.s(a)
        kf = None
        if animated:
            kf = {k: keys([(max(0.0, self.s(fr) - t0), v, "linear") for fr, v in pts]) for k, pts in animated.items()}
        clip.setdefault("effects", []).append(effect(catalog_id, kf, **params))
        return clip

    # --- pieces -----------------------------------------------------------------------------------------------
    def bg(self, a, b, colour, layers=None, enter=None, exit=None, box=None, name=None, group="bg"):
        t0, t1 = self.s(a), self.s(b)
        box = box or Box(-20, -20, W + 40, H + 40)
        p = self.path(a, b, enter, exit)
        clip = self.t.solid(self.lane(group, t0, t1), colour, t0, t1 - t0, box, self.motion(p),
                            layers=layers or solid(colour))
        if name:
            clip["name"] = name
        if enter or exit:
            clip["motionBlur"] = True
        clip["layoutRole"] = "cover"
        return clip

    def pic(self, a, b, sample, z=(1.0, 1.06), enter=None, exit=None, mv=None, sc=None, tone=(), box=None,
            label=None, reuse=None, group="pic", role="cover"):
        t0, t1 = self.s(a), self.s(b)
        box = box or Box(0, 0, W, H)
        if sc is None and z:
            sc = [(a, z[0]), (b, z[1])]
        p = self.path(a, b, enter, exit, mv, sc)
        if reuse is None:
            # the same sample twice in a piece is the same photo: one slot, filled once
            reuse = next((s.id for s in self.t.slots if s.sample == sample), None)
        clip = self.t.photo(self.lane(group, t0, t1), sample, t0, t1 - t0, box, self.motion(p), label=label,
                            reuse=reuse)
        for e in tone:
            clip.setdefault("effects", []).append(dict(e))
        if enter or exit or mv:
            clip["motionBlur"] = True
        clip["layoutRole"] = role
        return clip

    def again(self, a, b, first, **kw):
        """The same photo slot shown again."""
        return self.pic(a, b, first["_sample"], reuse=first["placeholderId"], **kw)

    def word(self, a, b, text, width, y=960, colour=WHITE, weight=800, x=540, sp=0.0, layers=None, enter=None,
             exit=None, mv=None, sc=None, spread=None, rot=None, anim=None, name=None, family=M, editable=True,
             group="word", align="center", ink_size=None):
        """A word whose ink is `width` px wide (at spacing `sp` em) centred on (x, y); spread = [(frame, em)] keys
        the letter spacing; rot = [(frame, deg)]."""
        t0, t1 = self.s(a), self.s(b)
        widest = max(text.split("\n"), key=len)
        size = ink_size or f6.fit(widest, width, family, weight, sp)[0]
        lines = text.count("\n") + 1
        bw, bh = width + size * 4, size * (1.25 * lines + 0.35)
        box = Box(x - bw / 2, y - bh / 2, bw, bh)
        style = text_style(family, int(round(size)), layers or [fill(colour)], weight=weight, align=align,
                           spacing=sp * size, line=1.12)
        style["wordWrap"] = False
        clip = self.t.text(self.lane(group, t0, t1), text, t0, t1 - t0, box, style, None,
                           label=name or text.replace("\n", " "), editable=editable)
        clip["textStyle"]["pixelSize"] = size
        p = self.path(a, b, enter, exit, mv, sc)
        self._text_keys(clip, box, size, p)
        if enter or exit or mv:
            clip["motionBlur"] = True
        if spread:
            clip["textStyle"].setdefault("keyframes", {})["letterSpacing"] = keys(
                [(max(0.0, self.s(fr) - t0), em * size, "linear") for fr, em in spread])
        if rot:
            self.anim(clip, a, "rotation", rot)
        if anim:
            clip["textStyle"]["animation"] = anim
        clip["layoutRole"] = "art"
        return clip

    def _text_keys(self, clip, box, size, path):
        if len(path) == 2 and all(abs(q[1]) < 1e-6 and abs(q[2]) < 1e-6 and abs(q[3] - 1) < 1e-6 for q in path):
            return
        xs, ys, ws, hs, ss = [], [], [], [], []
        for u, dx, dy, s in path:
            s = max(1e-3, s)
            xs.append((u, box.cx + dx - box.w * s / 2))
            ys.append((u, box.cy + dy - box.h * s / 2))
            ws.append((u, box.w * s))
            hs.append((u, box.h * s))
            ss.append((u, size * s))
        clip["x"], clip["y"], clip["width"], clip["height"] = keys(xs), keys(ys), keys(ws), keys(hs)
        if any(abs(v[1] - size) > 1e-3 for v in ss):
            clip["textStyle"].setdefault("keyframes", {})["pixelSize"] = keys(ss)

    def photo_word(self, a, b, text, width, sample, y=960, weight=900, sp=0.0, z=(1.0, 1.05), reuse=None,
                   tone=(), label=None, **kw):
        """A word filled with a photo slot (the photo's track matte is the word)."""
        w = self.word(a, b, text, width, y, WHITE, weight, sp=sp, **kw)
        if reuse is not None:
            ph = self.again(a, b, reuse, z=z, tone=tone, group="fill", role="art")
        else:
            ph = self.pic(a, b, sample, z=z, tone=tone, label=label, group="fill", role="art")
        ph["matte"] = {"clip": w["id"], "mode": "alpha"}
        return w, ph

    def band(self, a, b, colour, rect, layers=None, name="Banda"):
        """A full-width strip whose (y0, y1) follows rect = [(frame, y0, y1)]."""
        t0, t1 = self.s(a), self.s(b)
        box = Box(-20, 0, W + 40, H)
        pts = sorted(rect)
        mot = [(max(0.0, self.s(fr) - t0), {"dx": 0.0, "dy": (y0 + y1) / 2 - H / 2, "sx": 1.0,
                                           "sy": max(1e-4, (y1 - y0) / H)}, "linear") for fr, y0, y1 in pts]
        if len(mot) == 1:
            mot.append((t1 - t0, dict(mot[0][1]), "linear"))
        clip = self.t.solid(self.lane("band", t0, t1), colour, t0, t1 - t0, box, mot, layers=layers or solid(colour))
        clip["name"] = name
        clip["motionBlur"] = True
        clip["layoutRole"] = "cover"
        return clip

    def strip(self, clip, a, rect, x=None):
        """Shows `clip` (a full-frame photo) only inside the strip rect = [(frame, y0, y1)] (x = [(frame, x0, x1)])."""
        t0 = self.s(a)
        # a masked strip is part of the story's drawing: in a horizontal video it stays with the column (a mask
        # on a "cover" clip is remapped with the art scale by the fit and the strip lands in the wrong place)
        clip["layoutRole"] = "art"
        track = next(tr for tr in self.t.tracks if clip in tr.clips)
        pts = sorted(rect)
        xs = sorted(x) if x else [(pts[0][0], 0.0, W)]
        frames = sorted({p[0] for p in pts} | {p[0] for p in xs})

        def at(lst, fr):
            if fr <= lst[0][0]:
                return lst[0][1:]
            for p, q in zip(lst, lst[1:]):
                if fr <= q[0]:
                    u = (fr - p[0]) / max(1e-6, q[0] - p[0])
                    return tuple(v + (w - v) * u for v, w in zip(p[1:], q[1:]))
            return lst[-1][1:]
        mk = {"x": [], "y": [], "w": [], "h": []}
        for fr in frames:
            y0, y1 = at(pts, fr)
            x0, x1 = at(xs, fr)
            u = max(0.0, self.s(fr) - t0)
            mk["x"].append((u, (x0 + x1) / 2 / W))
            mk["y"].append((u, (y0 + y1) / 2 / H))
            mk["w"].append((u, max(0.0, x1 - x0) / W))
            mk["h"].append((u, max(0.0, y1 - y0) / H))
        self.t.mask(track, clip, "rectangle", x=mk["x"][0][1], y=mk["y"][0][1], w=mk["w"][0][1], h=mk["h"][0][1],
                    keyframes={k: keys(v) for k, v in mk.items()})

    def shape(self, a, b, cx, cy, w, h, layers, kind="rectangle", path=None, enter=None, exit=None, sc=None,
              rot=None, name="Adorno", group="deco", op=None):
        t0, t1 = self.s(a), self.s(b)
        box = Box(cx - w / 2, cy - h / 2, w, h)
        p = self.path(a, b, enter, exit, None, sc)
        clip = self.t.solid(self.lane(group, t0, t1), "#000000", t0, t1 - t0, box, self.motion(p), kind=kind,
                            layers=layers)
        clip["name"] = name
        if path:
            clip["shapeStyle"]["kind"] = "custom"
            clip["shapeStyle"]["customPath"] = path
            clip["shapeStyle"]["customEvenOdd"] = False
        if rot:
            self.anim(clip, a, "rotation", rot)
        if op:
            self.anim(clip, a, "opacity", op)
        clip["layoutRole"] = "art"
        return clip

    def deco(self, a, b, seed, colours, n=6, kinds=("ring", "tri", "plus", "x", "square", "grid", "play", "dot"),
             size=1.0):
        """Small shapes that pop in around the word (outside the middle band), as the typo and rhythm openers."""
        rng = random.Random(seed)
        for i in range(n):
            kind = kinds[(seed + i) % len(kinds)]
            top = i % 2 == 0
            cx = rng.uniform(110, 970)
            cy = rng.uniform(260, 700) if top else rng.uniform(1220, 1700)
            c = rng.choice(colours)
            at = a + rng.randint(0, 5)
            s = size * rng.uniform(0.8, 1.2)
            pop = [(at, 0.0), (at + 4, 1.0)]
            if kind == "ring":
                self.shape(at, b, cx, cy, 40 * s, 40 * s, outline(c, 4), kind="ellipse", sc=pop)
            elif kind == "dot":
                self.shape(at, b, cx, cy, 34 * s, 34 * s, solid(c), kind="ellipse", sc=pop)
            elif kind == "tri":
                self.shape(at, b, cx, cy, 44 * s, 44 * s, outline(c, 3), path=TRIANGLE, sc=pop,
                           rot=[(at, rng.choice((0, 90, -90)))])
            elif kind == "play":
                self.shape(at, b, cx, cy, 40 * s, 44 * s, solid(c), path=TRIANGLE, sc=pop)
            elif kind == "plus":
                self.shape(at, b, cx, cy, 36 * s, 36 * s, solid(c), path=PLUS, sc=pop)
            elif kind == "x":
                self.shape(at, b, cx, cy, 36 * s, 36 * s, solid(c), path=PLUS, sc=pop, rot=[(at, 45)])
            elif kind == "square":
                self.shape(at, b, cx, cy, 30 * s, 30 * s, solid(c), sc=pop)
            elif kind == "grid":
                cols, rows = rng.choice(((8, 3), (3, 8), (10, 2), (6, 4)))
                self.shape(at, b, cx, cy, cols * 20 * s, rows * 20 * s, solid(c), path=dot_grid(cols, rows),
                           sc=[(at, 0.0), (at + 4, 1.0)])

    def chevrons(self, a, b, y, colour=WHITE, w=74):
        """The «swipe up» arrows of the end card: they grow in and bob."""
        bob = [(a, 0.0)]
        fr = a + 6
        while fr < b:
            bob.append((fr, -10.0 if len(bob) % 2 else 0.0))
            fr += 9
        clip = self.shape(a, b, 540, y, w, w * 0.9, solid(colour), path=CHEVRONS, sc=[(a, 0.0), (a + 6, 1.0)],
                          name="Flechas")
        t0 = self.s(a)
        clip["y"] = keys([(max(0.0, self.s(f) - t0), y - w * 0.45 + d, "linear") for f, d in bob])
        return clip

    def tagline(self, a, b, y, colour=WHITE, width=420, start=0.25):
        c = self.word(a, b, TAGLINE, width, y, colour, 500, name="Lema")
        c["textStyle"]["animation"] = {"in": tanim("fade", duration=0.12, unit="character", stagger=0.04,
                                                   ease="easeOut", delay=start, order="random")}
        return c

    def logo(self, a, b, y=900, size=300, enter=None, sc=None):
        t0, t1 = self.s(a), self.s(b)
        box = Box(540 - size / 2, y - size / 2, size, size)
        p = self.path(a, b, enter, None, None, sc)
        clip = self.t.photo(self.lane("fill", t0, t1), "logo-flip", t0, t1 - t0, box, self.motion(p),
                            label="Tu logo", brandRole="logo")
        if enter:
            clip["motionBlur"] = True
        clip["layoutRole"] = "art"
        return clip

    def montage(self, cuts, samples, enter=(0, -1400, 3), tone=()):
        """Photos one per cut (frames) that whip in."""
        out = []
        for (a, b), sample in zip(zip(cuts, cuts[1:]), samples):
            out.append(self.pic(a, b, sample, enter=enter, tone=tone))
        return out


def tx(x):
    """Tile x of a 128 px study sheet → template x."""
    return (x - 64) * 7.73 + 540


def ty(y):
    return (y - 124) * 7.73 + 960


def _p(id, es, en, order, dur, tags=()):
    t = tall(f"tk4-{id}", es, en, "tiktok", dur, order=order,
             tags=["tiktok", "historia", "reels", "apertura", "presentación de fotos"] + list(tags),
             thumb_at=round(dur * 0.3, 1))
    t.layout_roles = True
    return t


# ==== 1. STOMP OPENER (577–1420) ====================================================================================
def stomp():
    f0, end = 577, 1420
    D = round((end - f0) / FPS, 2)
    t = _p("stomp", "Apertura stomp: una palabra por golpe con fotos", "Stomp opener: one word per beat with photos",
           14400, D, ["stomp", "ritmo", "palabras"])
    t.thumb_at = round((785 - f0) / FPS, 2)
    r = Reel(t, f0)
    DARK, WH = "#1A1A1A", WHITE
    whip_r, whip_l = (900, 0, 3), (-900, 0, 3)
    r.bg(577, 592, WH)
    r.word(577, 592, "CREATE", 500, colour=BLACK, enter=(700, 0, 4))
    r.bg(592, 598, DARK)
    r.word(592, 598, "YOUR", 355)
    r.bg(598, 607, WH)
    r.word(598, 607, "BEST", 325, colour=BLACK)
    r.bg(607, 622, WH)
    r.band(607, 622, DARK, [(607, 900, 1020), (610, 700, 1220), (613, 520, 1400), (617, -20, 1940)])
    r.word(607, 622, "VIDEO", 940, sp=0.3, sc=[(607, 0.66), (617, 1.0)])
    r.bg(622, 646, WH)
    _, ph = r.photo_word(622, 646, "VIDEO", 920, "fx-woman-01", sp=0.3, sc=[(622, 1.03), (646, 0.97)])
    r.fx(ph, 622, "rgb_split", animated={"amount": [(622, 22), (628, 0)]}, angle=0)
    r.deco(624, 646, 3, ["#F25C9A", "#2BBF6A", "#9A9A9A"], n=6, kinds=("dot", "dot", "plus"), size=0.35)
    r.pic(646, 658, "fx-woman-05", enter=(0, -1600, 3))
    r.word(649, 658, "MODERN", 800, layers=[shade(), fill(WH)])
    r.bg(658, 682, DARK)
    m = r.word(658, 682, "MODERN", 800, layers=grad("#4E6BFF", "#FF4FA8"), sc=[(658, 1.0), (672, 1.0), (681, 0.55)],
               rot=[(658, 0), (672, 0), (676, 14), (681, 40)])
    r.fx(m, 658, "stylize.twirl", animated={"angle": [(658, 0), (673, 0), (681, 540)]}, radius=0.9)
    r.deco(660, 676, 5, ["#7D6BFF", "#FF4FA8"], n=8, kinds=("dot",), size=0.3)
    r.pic(682, 709, "fx-figure-01", z=(1.04, 1.0))
    r.word(682, 709, "TRENDY", 640, y=ty(115), layers=[shade(), fill(WH)], sp=0.04,
           spread=[(682, 0.04), (691, 0.04), (700, 0.3)], rot=[(682, -12), (687, 0)], exit=(900, 0, 5),
           sc=[(682, 0.8), (687, 1.0)])
    r.montage([709, 716, 724, 733, 742, 748, 754],
              ["fx-man-04", "fx-woman-08", "y5-outfit-04", "fx-woman-07", "portrait-08", "fx-cyber-03"])
    r.pic(754, 763, "fx-woman-02", enter=(0, -1600, 3))
    r.word(754, 763, "FRESH", 730, y=ty(124), layers=[shade(), fill(WH)], sc=[(754, 0.6), (760, 1.0)])
    r.bg(763, 778, WH)
    r.photo_word(763, 778, "FRESH", 780, "fx-fashion-02")
    r.montage([778, 787, 793, 802, 811, 817], ["fx-face-04", "fx-cyber-02", "portrait-02", "fx-woman-04", "fx-man-03"])
    r.bg(817, 832, WH)
    r.band(817, 832, DARK, [(817, 728, 1180)])
    bandp = r.pic(817, 832, "fx-cyber-01", z=(1.0, 1.0), tone=(effect("adjust.brightness", brightness=-0.25),))
    r.strip(bandp, 817, [(817, 728, 1180)], x=[(817, 540, 540), (820, -20, 1100)])
    r.word(817, 832, "· CAPTURE ·", 760, sp=0.04, enter=(-500, 0, 3))
    ev = r.pic(832, 850, "fx-hair-03", z=(1.0, 1.04))
    r.word(832, 850, "EVERY", 600, sc=[(832, 0.35), (842, 1.0)], layers=[shade(), fill(WH)])
    TEAL = "#16B9A2"
    for a, b, photo in ((850, 853, False), (853, 856, True), (856, 862, False)):
        if photo:
            r.again(a, b, ev)
            r.word(a, b, "EVERY", 640, layers=[shade(), fill(WH)])
        else:
            r.bg(a, b, WH)
            r.word(a, b, "EVERY", 720, colour=TEAL, weight=900)
    r.again(862, 880, ev)
    r.word(862, 880, "EVERY", 640, sp=0.08, spread=[(862, 0.08), (877, 0.3)], exit=(-900, 0, 3),
           layers=[shade(), fill(WH)])
    mo = r.pic(880, 892, "fx-woman-06", enter=(0, -1600, 3))
    r.word(883, 892, "MOMENT", 720, sc=[(883, 0.5), (889, 1.0)], layers=[shade(), fill(WH)])
    PINK = "#F06A9B"
    for a, b, photo in ((892, 895, False), (895, 901, True), (901, 904, False)):
        if photo:
            r.again(a, b, mo)
            r.word(a, b, "MOMENT", 780, layers=[shade(), fill(WH)])
        else:
            r.bg(a, b, WH)
            r.word(a, b, "MOMENT", 940, colour=PINK, weight=900)
    r.again(904, 940, mo)
    r.word(904, 940, "MOMENT", 820, sp=0.1, spread=[(904, 0.1), (937, 0.22)], exit=(900, 0, 4),
           layers=[shade(), fill(WH)])
    r.bg(940, 979, "#C2207A")
    bowl = r.pic(943, 979, "y7-h-beauty-04", z=None, box=Box(-30, 730, 460, 460), enter=(-500, 0, 6),
                 exit=(-700, 0, 3), role="art")
    t.mask(next(tr for tr in t.tracks if bowl in tr.clips), bowl, "ellipse")
    r.word(946, 979, "OF", 300, x=tx(80), enter=(500, 0, 6), exit=(-700, 0, 3))
    r.pic(979, 1009, "fx-hair-04", exit=(260, 0, 6), sc=[(979, 1.1), (1009, 1.16)])
    r.word(979, 1009, "YOUR", 520, layers=[shade(), fill(WH)], exit=(320, 0, 6))
    r.bg(1009, 1036, WH)
    r.pic(1009, 1036, "y7-h-beauty-01", box=Box(0, 0, W, 960), enter=(-1080, 0, 3), role="art")
    r.word(1012, 1036, "LIFE", 300, y=1440, colour="#F08CB4", weight=900, enter=(-600, 0, 3))
    r.bg(1036, 1066, WH)
    r.word(1036, 1066, "CREATIVE", 800, y=ty(1053 - 992), colour="#EFD936", weight=900, enter=(800, 0, 3))
    r.pic(1036, 1066, "fx-fashion-04", box=Box(0, 960, W, 960), enter=(1080, 0, 3), exit=(0, 1100, 3), role="art")
    r.pic(1066, 1102, "fx-cyber-04", enter=(0, 1700, 4))
    r.word(1069, 1102, "DESIGN", 560, layers=[shade(), fill(WH)], spread=[(1069, 0.02), (1084, 0.02), (1094, 0.3)],
           rot=[(1069, 0), (1074, -6), (1094, -6), (1101, 30)], exit=(0, -700, 4))
    un = r.pic(1102, 1159, "fx-concert-03", z=(1.0, 1.0), sc=[(1102, 1.3), (1108, 1.0)], exit=(-1200, 0, 5),
               tone=(duo("#12001A", "#C2407E", contrast=0.6),))
    r.fx(un, 1102, "spin_blur", animated={"amount": [(1102, 0.7), (1108, 0.0)]})
    r.strip(un, 1102, [(1102, -20, 1940), (1126, -20, 1940), (1135, 751, 1161)])
    r.bg(1126, 1192, WH)
    r.word(1102, 1159, "UNIQUE", 770, layers=[shade(), fill(WH)], rot=[(1102, 70), (1108, 0)],
           sc=[(1102, 0.6), (1108, 1.0), (1126, 1.0), (1135, 0.56)], exit=(-1200, 0, 5))
    pj = r.pic(1153, 1192, "fx-citynight-04", z=(1.0, 1.0), enter=(1200, 0, 6))
    r.strip(pj, 1153, [(1153, 751, 1161), (1183, 751, 1161), (1192, -20, 1940)])
    r.word(1159, 1192, "PROJECT", 740, sp=0.3, enter=(900, 0, 6))
    r.pic(1192, 1225, "fx-dancer-06", enter=(0, -1600, 3))
    r.word(1192, 1225, "RHYTHM", 980, sp=0.3, sc=[(1192, 1.0), (1218, 1.0), (1225, 0.6)],
           layers=[shade(), fill(WH)])
    for a, b, word, w, dark in ((1225, 1252, "OPENER", 700, False), (1252, 1276, "YOU", 280, True),
                                (1276, 1288, "CAN", 300, False), (1288, 1303, "DO IT", 430, True),
                                (1303, 1312, "WITH", 500, False), (1312, 1321, "YOUR", 570, True),
                                (1321, 1327, "PROMO", 780, False), (1327, 1336, "PROMO", 980, True)):
        r.bg(a, b, DARK if dark else WH, enter=(1080, 0, 3) if a == 1252 else None)
        r.word(a, b, word, w, colour=WH if dark else BLACK, enter=(700, 0, 3) if a == 1252 else None)
    r.bg(1336, end, DARK)
    r.word(1336, end, "YOUR TITLE", 900, sc=[(1336, 0.4), (1340, 1.0)])
    r.tagline(1336, end, 1095, WH, 640, start=0.5)
    r.chevrons(1381, end, 1764)
    return r.finish()


# ==== 2. TYPO OPENER (1459–2061) =====================================================================================
def typo():
    f0, end = 1459, 2061
    D = round((end - f0) / FPS, 2)
    t = _p("typo", "Apertura tipográfica: palabras negras y fotos", "Typo opener: black words and photos", 14401, D,
           ["tipografía", "blanco y negro", "palabras"])
    t.thumb_at = round((1600 - f0) / FPS, 2)
    r = Reel(t, f0)
    DK, GH, INK = "#1F1F1F", "#ECECEC", "#141414"
    DECO = ["#1F1F1F", "#B5B5B5", "#1F1F1F"]

    def plain(a, b, word, w, ghost=2.1, enter=None, sc=None, seed=None, exit=None):
        r.bg(a, b, WHITE)
        if ghost:
            r.word(a, b, word, w * ghost, y=985, colour=GH, weight=900, editable=False, group="ghost",
                   name="Palabra de fondo", sc=sc, enter=enter)
        r.deco(a, b, seed if seed is not None else a, DECO, n=6, size=0.9)
        return r.word(a, b, word, w, colour=INK, weight=900, enter=enter, sc=sc, exit=exit)

    def tex(a, b, word, w):
        r.bg(a, b, DK)
        return r.word(a, b, word, w, weight=900, layers=stripes("#D2D2D2", DK, 11))

    def photo(a, b, word, w, sample, sc=None, enter=None, ghost=False, reuse=None):
        r.bg(a, b, WHITE)
        r.deco(a, b, a, DECO, n=5, size=0.9)
        return r.photo_word(a, b, word, w, sample, sc=sc, enter=enter, reuse=reuse)

    r.bg(1459, 1462, WHITE)
    plain(1462, 1480, "THE", 655, sc=[(1462, 3.2), (1466, 1.0)])
    tex(1480, 1489, "BEST", 700)
    plain(1489, 1501, "WAY", 695)
    tex(1501, 1513, "WAY", 625)
    photo(1513, 1522, "TO", 620, "fx-face-04")
    plain(1522, 1540, "TO", 385, sc=[(1522, 0.4), (1525, 1.0)])
    tex(1540, 1558, "TO", 480)
    plain(1558, 1576, "SHOW", 720)
    photo(1576, 1593, "UP", 660, "fx-cyber-02")
    r.bg(1593, 1596, WHITE)
    plain(1596, 1617, "IS", 380, enter=(-700, 0, 4))
    tex(1617, 1629, "IS", 560)
    r.bg(1629, 1650, WHITE)
    r.deco(1629, 1650, 7, DECO, n=6)
    r.word(1629, 1650, "VIDEO", 900, y=519, colour=INK, weight=900, enter=(900, 0, 9), exit=(-900, 0, 4))
    r.word(1629, 1650, "VIDEO", 930, colour=INK, weight=900, exit=(900, 0, 4))
    r.word(1629, 1650, "VIDEO", 900, y=1393, colour=INK, weight=900, enter=(-900, 0, 9), exit=(-900, 0, 4))
    r.bg(1650, 1680, WHITE)
    yp = r.pic(1650, 1680, "fx-woman-03", z=(1.0, 1.0))
    r.strip(yp, 1650, [(1650, -20, 1940), (1659, 612, 1424), (1668, 744, 1184), (1677, 760, 1160)])
    r.word(1650, 1680, "YOU", 810, sp=0.3, sc=[(1650, 1.25), (1656, 1.0), (1677, 0.72)],
           layers=[shade(alpha=0.3), fill(WHITE)])
    plain(1680, 1695, "CAN", 690)
    tex(1695, 1707, "CREATE", 860)
    plain(1707, 1713, "CREATE", 930)
    r.bg(1713, 1725, WHITE)
    r.photo_word(1713, 1725, "CREATE", 2300, "fx-fashion-01", mv=[(1713, 300, 0), (1725, -300, 0)])
    burst = ["fx-woman-05", "portrait-04", "fx-man-05", "portrait-06", "fx-cyber-05", "fx-man-02", "y5-outfit-01",
             "fx-face-01", "portrait-07", "fx-hair-01"]
    cuts = [1725, 1728, 1734, 1737, 1740, 1746, 1749, 1755, 1758, 1761, 1767, 1770, 1776, 1779, 1782, 1785]
    first = []
    for i, (a, b) in enumerate(zip(cuts, cuts[1:])):
        dirn = (0, -160, 1) if i % 2 else (160, 0, 1)
        if i < len(burst):
            first.append(r.pic(a, b, burst[i], enter=dirn))
        else:
            r.again(a, b, first[(i * 3) % len(first)], enter=dirn)
    photo(1785, 1806, "ONE", 695, "fx-face-03", sc=[(1785, 1.0), (1800, 1.0), (1806, 0.6)])
    photo(1806, 1818, "YOUR", 700, "fx-man-06", sc=[(1806, 1.4), (1809, 1.0), (1815, 1.0), (1818, 0.7)])
    photo(1818, 1830, "BEST", 720, "fx-face-05", sc=[(1818, 1.4), (1821, 1.0)])
    photo(1830, 1851, "VIDEO", 860, "fx-woman-06")
    r.bg(1851, 1863, DK, enter=(1080, 0, 3))
    r.word(1851, 1863, "JUST", 480, weight=900, enter=(800, 0, 4))
    plain(1863, 1884, "JUST", 800)
    tex(1884, 1896, "USE", 700)
    r.pic(1896, 1899, "fx-woman-02")
    plain(1899, 1911, "AE", 560, exit=(-400, 0, 3))
    r.bg(1911, 1923, DK)
    r.word(1911, 1923, "TO", 470, weight=900)
    photo(1923, 1947, "MAKE IT", 980, "fx-dancer-03", enter=(-900, 0, 5))
    photo(1947, 1974, "MAKE IT", 690, "fx-woman-01", sc=[(1947, 1.0), (1968, 1.0), (1974, 0.4)])
    r.bg(1974, end, DK)
    r.logo(1974, end, y=900, size=300, enter=(500, 0, 4))
    r.tagline(1974, end, 1110, WHITE, 560, start=0.3)
    r.chevrons(2010, end, 1764)
    return r.finish()


def paint(clip, runs):
    """Colours letters of a text: runs = [(start, end, colour)]."""
    clip["textStyle"]["runs"] = [{"start": a, "end": b, "colorEnabled": True, "color": argb(c)} for a, b, c in runs]
    return clip


# ==== 3. DYNAMIC OPENER (2073–2693) ==================================================================================
def dynamic():
    f0, end = 2073, 2693
    D = round((end - f0) / FPS, 2)
    t = _p("dynamic", "Apertura dinámica: fotos en rojo y negro", "Dynamic opener: red and black photos", 14402, D,
           ["dinámico", "rojo", "duotono", "palabras"])
    t.thumb_at = round((2160 - f0) / FPS, 2)
    r = Reel(t, f0)
    GREY_BG, RED, DK = "#DEDEDE", "#E3122C", "#141414"
    SH = shade(alpha=0.4)

    def red(a, b, sample, flick=(), enter=None, z=(1.0, 1.06), reuse=None):
        p = r.again(a, b, reuse, tone=(RED_DUO,), enter=enter, z=z) if reuse else             r.pic(a, b, sample, tone=(RED_DUO,), enter=enter, z=z)
        if flick:
            g = r.again(a, b, p, tone=(GREY,), z=z)
            r.hold_op(g, a, flick)
        return p

    def white(a, b, word, w, **kw):
        kw.setdefault("layers", [SH, fill(WHITE)])
        return r.word(a, b, word, w, **kw)

    def giant(a, b, word, sample, size=900, x0=1500, x1=-1500):
        r.bg(a, b, GREY_BG)
        r.photo_word(a, b, word, 100, sample, ink_size=size, weight=900, tone=(RED_DUO,),
                     mv=[(a, x0, 0), (b, x1, 0)])

    p = r.pic(2073, 2091, "fx-woman-07", z=(1.0, 1.05))
    white(2073, 2085, "YOUR BRAND", 740, sp=0.18, spread=[(2073, 0.18), (2085, 0.3)])
    r.word(2085, 2091, "YOUR BRAND", 740, sp=0.3, spread=[(2085, 0.3), (2091, 0.45)], layers=outline(WHITE, 2),
           editable=False)
    r.bg(2091, 2106, DK)
    pr = red(2091, 2100, "fx-man-02")
    r.strip(pr, 2091, [(2091, 465, 1470), (2100, 465, 1470)])
    paint(white(2091, 2100, "PRESENT", 590), [(2, 4, "#FFB3BC")])
    nw = red(2100, 2106, "fx-face-06")
    r.strip(nw, 2100, [(2100, 249, 1663)])
    white(2100, 2106, "NEW", 330)
    red(2106, 2109, "fx-woman-03")
    paint(white(2106, 2115, "DYNAMIC", 650), [(3, 5, "#FF8C99")])
    red(2109, 2115, "fx-man-05")
    giant(2115, 2127, "AMAZING", "fx-cyber-01")
    pj = red(2127, 2145, "fx-dancer-03", flick=[(2130, 2134), (2137, 2139)])
    c = white(2127, 2145, "PROJECT", 780, exit=(0, 0, 3))
    paint(c, [(0, 3, RED)])
    r.fx(c, 2127, "builtin.effects.gaussian_blur", animated={"u_blurRadius": [(2127, 0), (2139, 0), (2145, 30)]})
    r.pic(2145, 2157, "fx-man-04", tone=(effect("adjust.brightness", brightness=-0.3),))
    white(2145, 2157, "IT'S", 330, enter=(-300, 0, 4))
    red(2157, 2181, "fx-hair-05")
    c = white(2157, 2181, "TIME", 940, sc=[(2157, 0.6), (2163, 1.0)], weight=900)
    paint(c, [(1, 2, "#BDBDBD"), (3, 4, "#9A9A9A")])
    r.bg(2181, 2187, GREY_BG)
    r.word(2181, 2187, "TO", 600, weight=900, layers=grad("#7A0010", "#F2A3AE"))
    red(2187, 2208, "fx-face-01", flick=[(2190, 2193), (2196, 2199)])
    white(2187, 2202, "BLOW", 800, weight=900)
    r.word(2202, 2208, "BLOW", 800, weight=900, layers=outline(WHITE, 3), editable=False)
    r.bg(2208, 2226, DK)
    yr = red(2208, 2226, "fx-man-06")
    r.strip(yr, 2208, [(2208, 300, 1620)], x=[(2208, 300, 780), (2220, 340, 740), (2226, 540, 540)])
    paint(white(2208, 2226, "YOUR", 600, exit=(-400, 0, 3)), [(1, 2, RED)])
    giant(2226, 2250, "MIND", "fx-woman-04", size=950, x0=1300, x1=-900)
    mp = r.pic(2250, 2274, "fx-face-02", z=(1.0, 1.05))
    r.word(2250, 2262, "MIND", 520, colour=RED, weight=900, rot=[(2250, -70), (2259, 0)],
           sc=[(2250, 1.8), (2259, 1.0)])
    r.word(2262, 2274, "MIND", 520, weight=900, layers=outline(RED, 3), editable=False)
    red(2274, 2286, None, reuse=mp)
    paint(white(2274, 2286, "AND", 560), [(0, 1, "#FFB3BC")])
    red(2286, 2301, "fx-cyber-05", flick=[(2289, 2292), (2298, 2301)])
    c = white(2286, 2301, "CREATE", 860, sp=0.18)
    paint(c, [(0, 2, "#FF6070")])
    r.bg(2301, 2343, GREY_BG)
    stack = [("YOUR", 728, 680, grad("#5A0008", "#E3122C")), ("RHYTHM", 960, 980, outline(RED, 3)),
             ("PROMO", 1161, 850, grad("#E3122C", "#8A0010"))]
    for i, (w_, y_, wd, lay) in enumerate(stack):
        r.word(2301 + 3 * i, 2343, w_, wd, y=y_, weight=900, layers=lay, enter=(-300, 0, 4),
               mv=[(2328, 0, 0), (2337, -260, 80)], sc=[(2328, 1.0), (2337, 0.8), (2343, 1.6)],
               editable=True)
    r.pic(2343, 2364, "fx-dancer-06", z=(1.0, 1.08))
    white(2343, 2364, "CREATE", 900, sp=0.1, spread=[(2343, 0.1), (2361, 0.35)])
    r.bg(2364, 2376, GREY_BG)
    r.word(2364, 2376, "YOUR", 980, weight=900, layers=grad("#2A0006", "#B0001E"))
    red(2376, 2397, "fx-woman-08", flick=[(2385, 2388)])
    white(2376, 2388, "TRENDY", 980, sp=0.18)
    r.word(2388, 2397, "TRENDY", 900, sp=0.12, layers=outline(WHITE, 2), editable=False)
    red(2397, 2422, "fx-face-06")
    white(2397, 2422, "STORY", 800, sp=0.15, sc=[(2397, 1.25), (2403, 1.0), (2418, 0.95)])
    giant(2422, 2433, "IT'S", "fx-man-03", size=980, x0=700, x1=-200)
    its = red(2433, 2469, "fx-man-03", flick=[(2442, 2445)])
    white(2433, 2442, "IT'S", 520, weight=900)
    r.word(2442, 2469, "IT'S", 520, weight=900, layers=outline("#E8A0A8", 3), editable=False)
    r.pic(2469, 2484, "fx-woman-05", enter=(0, -1200, 3))
    r.word(2469, 2484, "TIME", 420, colour=RED, weight=900, enter=(-300, 0, 4))
    red(2484, 2496, "fx-woman-06")
    white(2484, 2496, "TO LET", 980, sp=0.15)
    r.pic(2496, 2523, "fx-hair-02")
    r.word(2496, 2505, "EVERYONE", 1000, weight=800, layers=outline(WHITE, 2), editable=False)
    white(2505, 2523, "EVERYONE", 1000, exit=(0, 300, 4))
    r.pic(2523, 2529, "fx-man-02", enter=(0, 1200, 3))
    kn = red(2529, 2559, "fx-man-05", flick=[(2529, 2535), (2544, 2547)])
    c = white(2529, 2559, "KNOW", 700, sp=0.1, rot=[(2529, 0), (2550, 0), (2559, 35)], exit=(200, -400, 6))
    paint(c, [(0, 4, RED)])
    ab = r.pic(2559, 2580, "fx-woman-07", z=(1.0, 1.04))
    r.word(2559, 2580, "ABOUT", 760, colour=RED, weight=900, rot=[(2559, -90), (2568, 0)], sc=[(2559, 1.8), (2568, 1.0)])
    red(2580, 2601, None, reuse=ab)
    paint(white(2580, 2601, "YOU", 640, weight=900), [(1, 2, "#FFB3BC")])
    r.pic(2601, end, "fx-woman-02", z=(1.0, 1.06))
    r.logo(2601, end, y=900, size=300, enter=(400, 0, 4))
    r.tagline(2601, end, 1110, WHITE, 560, start=0.3)
    r.chevrons(2639, end, 1764)
    return r.finish()


# ==== 4. FAST OPENER (2705–3540, the info card 3266–3281 left out) ===================================================
def fast():
    f0, end, gap = 2705, 3540, 15
    D = round((end - f0 - gap) / FPS, 2)
    t = _p("fast", "Apertura rápida: palabras sobre fotos de color", "Fast opener: words over colour photos", 14403, D,
           ["rápido", "color", "palabras"])
    t.thumb_at = round((2840 - f0) / FPS, 2)
    r = Reel(t, f0)
    RED, NAVY = "#C8202E", "#0A1748"
    REDL = grad("#D62837", "#B01522", 90)
    NAVYL = grad("#13245E", "#050D2E", 90)
    SH = shade(alpha=0.45, blur=20)

    def bgc(a, b, kind):
        if kind == "red":
            return r.bg(a, b, RED, layers=REDL)
        if kind == "navy":
            return r.bg(a, b, NAVY, layers=NAVYL)
        if kind == "plum":
            return r.bg(a, b, NAVY, layers=grad("#1A1F6A", "#5A1A5E", 90))
        return r.bg(a, b, WHITE)

    def shot(a, b, back, word, w, o=False, y=960, colour=WHITE, enter=None, sp=0.0, spread=None, sc=None, glitch=False,
             blur_in=False, exit=None):
        if back.startswith("#") or back in ("red", "navy", "plum", "white"):
            bgc(a, b, back)
        else:
            p = r.pic(a, b, back, enter=(0, -1400, 3) if enter == "photo" else None)
            if glitch:
                r.fx(p, a, "rgb_split", animated={"amount": [(a, 26), (a + 4, 0)]})
        lay = outline(colour, 3) if o else [SH, fill(colour)]
        c = r.word(a, b, word, w, y=y, layers=lay, sp=sp, spread=spread, sc=sc,
                   enter=enter if isinstance(enter, tuple) else None, exit=exit)
        if blur_in:
            r.fx(c, a, "builtin.effects.gaussian_blur", animated={"u_blurRadius": [(a, 30), (a + 5, 0)]})
        if glitch:
            r.fx(c, a, "rgb_split", animated={"amount": [(a, 20), (a + 5, 0)]})
        return c

    r.pic(2705, 2771, "fx-hair-04", z=(1.0, 1.05))
    c = r.word(2705, 2771, "TRENDY", 740, layers=[SH, fill(WHITE)])
    c["textStyle"]["animation"] = {"in": tanim("fade", duration=0.12, unit="character", stagger=0.12, ease="easeOut",
                                               delay=0.1, order="random")}
    shot(2771, 2780, "navy", "FAST", 330)
    shot(2780, 2792, "fx-cyber-03", "FAST", 500, glitch=True)
    shot(2792, 2807, "fx-hair-05", "CLEAN", 420, enter=(400, 0, 4))
    shot(2807, 2819, "fx-hair-05", "CLEAN", 1000, o=True, sc=[(2807, 1.0), (2819, 1.06)])
    shot(2819, 2834, "fx-woman-03", "TEMPLATE", 950, blur_in=True)
    shot(2834, 2846, "fx-woman-07", "AMAZING", 880, sp=0.08)
    shot(2846, 2858, "portrait-03", "PICTURES", 760)
    shot(2858, 2870, "fx-woman-04", "IMPRESSIVE", 1000, sc=[(2858, 1.0), (2867, 0.62)])
    bgc(2870, 2894, "red")
    kids = r.pic(2870, 2885, "y5-grwm-04", z=(1.0, 1.0))
    r.strip(kids, 2870, [(2870, -20, 1940), (2876, -20, 1940), (2885, 960, 960)])
    r.word(2870, 2894, "RHYTHM", 620, sp=0.4, sc=[(2870, 0.5), (2885, 1.0)])
    shot(2894, 2909, "fx-figure-04", "CATCHY", 640, enter="photo")
    shot(2909, 2918, "fx-citynight-02", "BRIGHT", 990)
    shot(2918, 2927, "navy", "VIDEO", 640, sp=0.1, enter=(-600, 0, 4))
    shot(2927, 2939, "white", "COLORFUL", 830, colour=NAVY, enter=(-600, 0, 4))
    shot(2939, 2945, "red", "STYLE", 860, o=True)
    shot(2945, 2951, "red", "STYLE", 860)
    shot(2951, 2969, "fx-woman-06", "TRENDY", 700, spread=[(2951, 0.0), (2969, 0.15)], blur_in=True)
    shot(2969, 2984, "fx-dancer-06", "TRENDY", 1000, sp=0.3)
    shot(2984, 2993, "fx-woman-08", "EASY", 500, y=635, enter=(0, 200, 4))
    r.pic(2993, 3002, "fx-hair-01")
    r.word(2993, 3002, "EASY", 500, y=635, layers=[SH, fill(WHITE)])
    r.word(2993, 3002, "TO", 260, y=952, layers=[SH, fill(WHITE)], enter=(0, 200, 4))
    r.pic(3002, 3014, "fx-man-05")
    for i, (w_, y_, wd) in enumerate((("EASY", 635, 500), ("TO", 952, 260), ("USE", 1277, 420))):
        r.word(3002, 3014, w_, wd, y=y_, layers=[SH, fill(WHITE)], enter=(0, 200, 4) if i == 2 else None)
    shot(3014, 3032, "y5-outfit-07", "PROJECT", 980, enter=(-700, 0, 5))
    shot(3032, 3047, "fx-hair-02", "BEST", 640, o=True)
    shot(3047, 3059, "red", "BEST", 780, sc=[(3047, 1.2), (3051, 1.0)])
    shot(3059, 3077, "portrait-06", "WAY", 420, spread=[(3059, 0.0), (3077, 0.1)], sc=[(3059, 1.0), (3070, 1.3)])
    shot(3077, 3092, "fx-man-02", "TO SHOW", 940, enter=(-500, 0, 5))
    shot(3092, 3107, "plum", "YOURSELF", 1000, o=True)
    shot(3107, 3122, "fx-dancer-02", "CREATE", 760, glitch=True)
    shot(3122, 3137, "portrait-02", "YOUR", 640, o=True)
    shot(3137, 3158, "fx-man-03", "TRENDY", 660, glitch=True)
    shot(3158, 3170, "red", "PROMO", 640)
    r.montage([3170, 3176, 3182, 3188, 3194, 3203, 3206],
              ["portrait-07", "fx-fashion-03", "fx-woman-04", "fx-man-06", "fx-face-01", "fx-woman-07"])
    shot(3206, 3218, "fx-woman-07", "IT'S TIME", 1000, o=True)
    shot(3218, 3237, "navy", "TO", 480, glitch=True, exit=(500, 0, 3))
    shot(3237, 3254, "y5-grwm-01", "INTRODUCE", 1000, glitch=True)
    k = r.pic(3254, 3263, "fx-face-04", z=(1.0, 1.0))
    r.fx(k, 3254, "kaleidoscope", animated={"zoom": [(3254, 1.0), (3263, 1.6)]}, segments=6)
    r.word(3254, 3263, "YOUR", 560, layers=[SH, fill(WHITE)], sc=[(3254, 1.0), (3261, 0.6)])
    shot(3263, 3266, "y5-outfit-03", "OWN", 500)
    r.skip(gap)
    shot(3281, 3293, "red", "BRAND", 800, enter=(700, 0, 4))
    shot(3293, 3311, "fx-skater-03", "FRESH", 700, o=True)
    shot(3311, 3329, "fx-hair-04", "CREATIVE", 950, sp=0.2, blur_in=True)
    shot(3329, 3344, "navy", "CLEAN", 880, sp=0.2)
    shot(3344, 3356, "fx-face-02", "NEW", 640, o=True)
    shot(3356, 3365, "fx-woman-02", "FAST", 640, sc=[(3356, 1.0), (3365, 1.12)])
    shot(3365, 3377, "red", "COLORFUL", 760, enter=(-700, 0, 5))
    shot(3377, 3386, "navy", "STYLISH", 760, enter=(-700, 0, 5))
    shot(3386, 3404, "fx-woman-05", "ENERGY", 880, enter=(600, 0, 5))
    shot(3404, 3419, "fx-man-04", "STYLISH", 880, o=True)
    shot(3419, 3434, "fx-cyber-04", "RHYTHM", 940)
    shot(3434, 3449, "fx-citynight-03", "TEMPLATE", 980, blur_in=True)
    bgc(3449, end, "red")
    lg = r.logo(3449, end, y=900, size=300)
    r.fx(lg, 3449, "builtin.effects.gaussian_blur", animated={"u_blurRadius": [(3449, 30), (3455, 0)]})
    r.tagline(3449, end, 1110, WHITE, 560, start=0.3)
    r.chevrons(3497, end, 1764)
    return r.finish()


# ==== 5. RHYTHM OPENER (3550–4425) ===================================================================================
def rhythm():
    f0, end = 3550, 4425
    D = round((end - f0) / FPS, 2)
    t = _p("rhythm", "Apertura de ritmo: palabras en degradado", "Rhythm opener: gradient words", 14404, D,
           ["ritmo", "degradado", "violeta", "palabras"])
    t.thumb_at = round((3700 - f0) / FPS, 2)
    r = Reel(t, f0)
    GBG = "#D9D9D9"
    OP, PU, GO = ("#F2A100", "#A21CCF"), ("#6A1FD6", "#C42BD3"), ("#F5B400", "#D2620A")
    DECO = ["#8A2BE2", "#B44CE0", "#F0A500"]
    SH = shade(alpha=0.4)

    def grey(a, b):
        r.bg(a, b, GBG)
        r.bg(a, b, WHITE, layers=[gradient([(0.0, GBG), (0.5, "#F7F7F7"), (1.0, GBG)], angle=90)], name="Luz")

    def gw(a, b, word, w, pal=OP, ghost=True, sc=None, enter=None, sp=0.0, spread=None, y=960, deco=True):
        grey(a, b)
        if ghost:
            r.word(a, b, word, w * 2.0, y=y, weight=900, layers=outline(pal[1], 2), editable=False, group="ghost",
                   name="Palabra de fondo", sc=sc)
        if deco:
            r.deco(a, b, a, DECO, n=5, size=0.9)
        return r.word(a, b, word, w, y=y, weight=900, layers=grad(*pal), sc=sc, enter=enter, sp=sp, spread=spread)

    def pw(a, b, sample, word, w, sp=0.0, spread=None, sc=None, enter=None, y=960, blur_in=False, reuse=None):
        if reuse is not None:
            r.again(a, b, reuse)
            p = reuse
        else:
            p = r.pic(a, b, sample, enter=(0, -1400, 3) if enter == "photo" else None)
        c = r.word(a, b, word, w, y=y, weight=900, layers=[SH, fill(WHITE)], sp=sp, spread=spread, sc=sc,
                   enter=enter if isinstance(enter, tuple) else None)
        if blur_in:
            r.fx(c, a, "builtin.effects.gaussian_blur", animated={"u_blurRadius": [(a, 30), (a + 6, 0)]})
        return p

    def stack(a, b, sample, words):
        r.pic(a, b, sample)
        for w_, y_, wd, at in words:
            r.word(max(a, at), b, w_, wd, y=y_, weight=900, layers=[SH, fill(WHITE)], enter=(0, 120, 4))

    def bands(a, b, sample, word, w, ys, hops, colour):
        r.pic(a, b, sample)
        for y_ in ys:
            r.word(a, b, word, w, y=y_, weight=900, layers=outline(WHITE, 2), editable=False,
                   name="Palabra de fondo", group="ghost")
        for i, (fr, y_) in enumerate(hops):
            nxt = hops[i + 1][0] if i + 1 < len(hops) else b
            r.bg(fr, nxt, colour, box=Box(0, y_ - 105, W, 210), group="band", name="Banda")
            r.word(fr, nxt, word, w, y=y_, weight=900, editable=i == 0)

    grey(3550, 3601)
    lg = r.logo(3550, 3601, y=960, size=280, sc=[(3550, 1.0), (3595, 1.04), (3601, 1.6)])
    r.fx(lg, 3550, "builtin.effects.gaussian_blur", animated={"u_blurRadius": [(3550, 0), (3596, 0), (3601, 40)]})
    gw(3601, 3616, "DYNAMIC", 640, PU, sc=[(3601, 3.0), (3604, 1.0)])
    bal = pw(3616, 3628, "fx-figure-03", "MODERN", 640, blur_in=True)
    pw(3628, 3643, None, "CLEAN", 700, sp=0.05, spread=[(3628, 0.05), (3643, 0.3)], reuse=bal)
    gw(3643, 3655, "RHYTHM", 800, PU)
    pw(3655, 3667, "fx-cyber-03", "PROMO", 820)
    stack(3667, 3694, "fx-woman-03", [("COOL", 759, 420, 3667), ("SOUND", 960, 560, 3673),
                                       ("EFFECTS", 1161, 640, 3679)])
    gw(3694, 3730, "LIVE", 470, OP, sc=[(3694, 3.0), (3698, 1.0), (3724, 1.0), (3730, 0.55)])
    pw(3730, 3745, "fx-woman-05", "BREATHE", 700, blur_in=True)
    bands(3745, 3757, "fx-woman-07", "ENJOY", 520, [1586, 1254, 937, 620, 303],
          [(3745, 1586), (3748, 1254), (3751, 937), (3754, 620)], "#1E2BD8")
    grey(3757, 3784)
    r.deco(3757, 3784, 3, DECO, n=6, size=0.9)
    for w_, y_, wd, at in (("EASY", 705, 360, 3757), ("TO", 960, 170, 3763), ("USE", 1207, 300, 3766)):
        c = r.word(at, 3784, w_, wd, y=y_, weight=900, layers=grad(*OP), exit=(0, 0, 3))
        c["textStyle"]["animation"] = {"in": tanim("fade", duration=0.1, unit="character", stagger=0.05,
                                                   ease="easeOut")}
    pw(3784, 3799, "fx-woman-06", "FRESH", 520, blur_in=True, sc=[(3784, 0.8), (3796, 1.05)])
    r.pic(3799, 3820, "fx-cyber-06")
    r.word(3799, 3808, "CREATIVE", 900, weight=900, layers=outline(WHITE, 2), editable=False)
    r.word(3808, 3820, "CREATIVE", 900, weight=900, layers=[SH, fill(WHITE)])
    pw(3820, 3838, "fx-woman-04", "TEMPLATE", 960, enter="photo")
    gw(3838, 3850, "YOUR", 650, PU, ghost=False, sc=[(3838, 0.8), (3847, 1.1)])
    gw(3850, 3871, "VIDEO", 640, PU, ghost=False, spread=[(3850, 0.0), (3871, 0.15)], sc=[(3850, 0.4), (3855, 1.0)])
    pw(3871, 3889, "fx-woman-07", "CAN BE", 580)
    gw(3889, 3898, "SHORT", 840, OP, sc=[(3889, 3.0), (3892, 1.0)])
    gw(3898, 3907, "BUT", 380, PU)
    gw(3907, 3925, "UNIQUE", 800, OP, sc=[(3907, 2.5), (3911, 1.0)])
    stack(3925, 3964, "fx-cyber-04", [("BLOW", 705, 480, 3925), ("THEM", 960, 440, 3934), ("AWAY", 1207, 470, 3946)])
    bands(3964, 3976, "fx-woman-05", "TRENDY", 600, [311, 635, 960, 1277, 1601],
          [(3964, 635), (3967, 960), (3970, 1601)], "#151A6E")
    pw(3976, 3997, "fx-hair-04", "BLOW", 600, sp=0.1, spread=[(3976, 0.1), (3994, 0.3)])
    gw(3997, 4009, "YOUR", 460, GO, ghost=False)
    gw(4009, 4024, "MIND", 470, PU, ghost=False)
    gw(4024, 4036, "TRENDY", 880, OP, ghost=False)
    pw(4036, 4051, "fx-man-06", "DESIGN", 980, enter=(-500, 0, 4))
    r.pic(4051, 4090, "fx-fashion-01")
    r.word(4051, 4060, "GOOD", 460, y=705, weight=900, layers=[SH, fill(WHITE)])
    r.word(4060, 4090, "GOOD", 460, y=705, weight=900, layers=outline(WHITE, 2), editable=False)
    r.word(4063, 4075, "FOR", 300, y=960, weight=900, layers=[SH, fill(WHITE)])
    r.word(4075, 4090, "FOR", 300, y=960, weight=900, layers=outline(WHITE, 2), editable=False)
    r.word(4075, 4090, "STORY", 520, y=1207, weight=900, layers=[SH, fill(WHITE)])
    gw(4090, 4105, "UNIQUE", 980, OP, ghost=False, sc=[(4090, 0.9), (4099, 1.3), (4105, 3.0)])
    pw(4105, 4120, "fx-cyber-03", "COOL", 760, sp=0.2)
    gw(4120, 4135, "LOOKING", 1000, OP, sp=0.1)
    pw(4135, 4147, "fx-hair-04", "STYLE", 700)
    pw(4147, 4159, "fx-hair-05", "EASY", 680)
    pw(4159, 4174, "fx-figure-01", "EDIT", 560, sc=[(4159, 1.0), (4171, 0.85)])
    gw(4174, 4186, "IMPRESSIVE", 1000, OP)
    gw(4186, 4195, "DESIGN", 780, OP, sc=[(4186, 3.0), (4189, 1.0), (4192, 1.0), (4195, 0.4)])
    gw(4195, 4213, "THIS", 520, PU)
    pw(4213, 4228, "y6-dessert-02", "TEMPLATE", 950, enter=(600, 0, 5))
    gw(4228, 4240, "BLOW", 760, OP)
    pw(4240, 4255, "y7-h-beauty-04", "YOUR", 640, sc=[(4240, 1.0), (4252, 0.85)])
    gw(4255, 4264, "AUDIENCE", 1000, OP, ghost=False)
    pw(4264, 4276, "fx-woman-07", "AUDIENCE", 1000)
    gw(4276, 4291, "MAKE", 500, ("#C0306A", "#E0902A"), ghost=False)
    pw(4291, 4303, "fx-beach-02", "YOUR", 560, blur_in=True)
    gw(4303, 4312, "DREAMS", 640, PU, ghost=False, sc=[(4303, 0.8), (4306, 1.0)])
    gw(4312, 4324, "COME", 620, OP, ghost=False, sc=[(4312, 3.0), (4315, 1.0)])
    gw(4324, 4354, "TRUE", 1000, OP, ghost=False, sc=[(4324, 0.25), (4342, 1.0)])
    grey(4354, end)
    r.word(4354, end, "YOUR TITLE", 980, weight=900, layers=grad(*PU), sc=[(4354, 0.4), (4357, 1.0)])
    r.tagline(4354, end, 1080, "#7A22D6", 520, start=0.2)
    r.chevrons(4390, end, 1764, "#7A22D6")
    return r.finish()


GOLD = [shade(alpha=0.55, blur=14), gradient([(0.0, "#FFF0A0"), (0.45, "#F2C21A"), (1.0, "#8A5600")], angle=90),
        {"id": "stroke", "kind": "stroke", "enabled": True, "width": 3, "strokeAlign": "outside", "opacity": 1.0,
         "paint": {"kind": "solid", "color": argb("#FFE45A")}}]
PARA = ("YOU CAN CAPTURE EVERY\nMOMENT OF YOUR LIFE\nAND SHARE IT. KEEP\nYOUR BEST MOMENTS\nENJOY! TASTE! TOUCH!\n"
        "FEEL! DEVELOP! GROW!")


# ==== 6. MODERN OPENER (4440–5085, the card 4855–4863 left out) ======================================================
def modern():
    f0, end, gap = 4440, 5085, 8
    D = round((end - f0 - gap) / FPS, 2)
    t = _p("modern", "Apertura moderna: amarillo, dorado y rejilla", "Modern opener: yellow, gold and grid", 14405, D,
           ["moderno", "dorado", "amarillo", "palabras"])
    t.thumb_at = round((4560 - f0) / FPS, 2)
    r = Reel(t, f0)
    YEL = "#F4E21C"
    SH = shade(alpha=0.5)

    def grid(a, b, tilt=4.0):
        for x in (150, 560, 960):
            r.shape(a, b, x, 960, 6, 2300, solid(WHITE, 0.85), rot=[(a, tilt)], name="Rejilla",
                    sc=[(a, 0.0), (a + 4, 1.0)])
        for y in (330, 1500):
            r.shape(a, b, 540, y, 1500, 6, solid(WHITE, 0.85), rot=[(a, tilt)], name="Rejilla",
                    sc=[(a, 0.0), (a + 4, 1.0)])

    def para(a, b, xs=(190, 890), y=960):
        for x in xs:
            r.word(a, b, PARA, 230, x=x, y=y, weight=600, editable=False, name="Párrafo", group="deco",
                   ink_size=17)

    def copies(a, b, word, w, colour, n=2, gap_y=150, y=960):
        for i in range(1, n + 1):
            for sgn in (-1, 1):
                r.word(a, b, word, w, y=y + sgn * i * gap_y, weight=900, layers=outline(colour, 2), editable=False,
                       name="Palabra de fondo", group="ghost")

    dark = r.pic(4440, 4486, "fx-man-06", tone=(effect("adjust.brightness", brightness=-0.35),), z=(1.08, 1.0))
    r.word(4468, 4471, "THE", 470, weight=900, layers=outline(WHITE, 3), editable=False, sc=[(4468, 2.5), (4471, 1.2)])
    r.word(4471, 4486, "THE", 470, weight=900, sc=[(4471, 1.1), (4477, 1.0)])
    r.again(4486, 4534, dark, tone=(duo("#05060F", "#5A78C8", contrast=0.5),), z=(1.0, 1.04))
    grid(4486, 4534)
    para(4486, 4516)
    r.word(4486, 4516, "THE", 420, weight=900, sc=[(4486, 1.0), (4510, 0.8)])
    r.word(4516, 4534, "THE", 600, weight=900, layers=stripes(YEL, "#000000", 9))
    bp = r.pic(4534, 4546, "fx-man-05")
    r.fx(bp, 4534, "builtin.effects.gaussian_blur", animated={"u_blurRadius": [(4534, 20), (4546, 4)]})
    r.word(4534, 4546, "BEST", 520, weight=900, layers=[SH, fill(YEL)])
    r.again(4546, 4564, bp, tone=(YELLOW_DUO,))
    copies(4546, 4564, "BEST", 760, "#1A2A6A", gap_y=125)
    r.word(4546, 4564, "BEST", 760, weight=900, layers=[SH, fill(WHITE)])
    wp = r.pic(4564, 4579, "fx-woman-06")
    copies(4564, 4579, "WAY", 700, YEL, gap_y=170)
    r.word(4564, 4579, "WAY", 700, weight=900, layers=[SH, fill(YEL)])
    r.again(4579, 4605, wp, tone=(YELLOW_DUO,))
    para(4579, 4605, xs=(170, 540, 910))
    copies(4588, 4605, "WAY", 700, "#5A78C8", n=1, gap_y=380)
    kp = r.pic(4605, 4629, "fx-man-03", z=(1.0, 1.0))
    r.fx(kp, 4605, "kaleidoscope", animated={"zoom": [(4605, 1.6), (4628, 1.0)]}, segments=4)
    r.fx(kp, 4605, "builtin.effects.gaussian_blur", animated={"u_blurRadius": [(4605, 30), (4611, 0)]})
    r.word(4614, 4629, "TO BE", 900, weight=900, layers=outline(YEL, 3), editable=False,
           spread=[(4614, 0.6), (4629, 0.1)])
    r.again(4629, 4665, kp, tone=(YELLOW_DUO,))
    r.word(4629, 4665, "TO BE", 900, weight=900, layers=[SH, fill(YEL)], enter=(-700, 0, 6))
    r.pic(4665, 4668, "fx-woman-03")
    r.pic(4668, 4689, "fx-dancer-03", tone=(YELLOW_DUO,))
    r.shape(4668, 4689, 540, 960, 560, 560, outline(WHITE, 4), kind="ellipse", sc=[(4668, 0.2), (4674, 1.0)])
    para(4668, 4689)
    r.word(4668, 4689, "COOL", 1000, weight=900, sp=0.05, layers=[SH, fill(WHITE)], sc=[(4668, 1.4), (4672, 1.0)])
    ch = r.pic(4689, 4731, "portrait-04")
    r.fx(ch, 4689, "builtin.effects.gaussian_blur", u_blurRadius=8)
    r.word(4689, 4704, "CHIC", 900, weight=900, layers=[SH, fill(YEL)], enter=(-600, 0, 4))
    r.again(4704, 4719, ch, tone=(YELLOW_DUO,))
    para(4704, 4719)
    r.word(4704, 4719, "CHIC", 900, weight=900, layers=outline(WHITE, 2), editable=False)
    r.word(4719, 4731, "CHIC", 900, weight=900, layers=outline("#E8B020", 3), editable=False,
           spread=[(4719, 0.0), (4731, 1.4)], sc=[(4719, 1.0), (4731, 1.5)])
    burst = ["fx-cyber-04", "fx-man-04", "fx-man-02", "fx-cyber-02", "fx-face-04", "fx-woman-02", "fx-face-05",
             "portrait-08", "fx-dancer-02", "fx-hair-05"]
    cuts = [4731, 4737, 4740, 4746, 4749, 4752, 4758, 4761, 4767, 4770, 4773, 4776, 4780, 4785, 4791]
    first = []
    for i, (a, b) in enumerate(zip(cuts, cuts[1:])):
        if i < len(burst):
            first.append(r.pic(a, b, burst[i]))
        else:
            r.again(a, b, first[i - len(burst)])
    r.pic(4791, 4815, "fx-face-05", z=(1.0, 1.06), tone=(duo("#12060F", "#D8C8D0", contrast=0.6),))
    r.word(4791, 4815, "UNIQUE", 900, weight=900, layers=GOLD, sc=[(4791, 1.4), (4795, 1.0), (4809, 1.0), (4815, 0.3)])
    r.pic(4815, 4827, "fx-face-03", tone=(effect("adjust.brightness", brightness=-0.2),))
    r.word(4815, 4827, "TRENDY", 980, weight=900, layers=GOLD)
    r.pic(4827, 4842, "fx-hair-02", tone=(duo("#120812", "#D8C8D0", contrast=0.5),))
    r.word(4827, 4842, "MODERN", 960, weight=900, layers=GOLD)
    r.pic(4842, 4855, "fx-woman-08", tone=(YELLOW_DUO,))
    grid(4842, 4855, tilt=-6)
    para(4842, 4855)
    r.word(4842, 4855, "CATCHY", 1000, weight=900, layers=[SH, fill(WHITE)], enter=(-600, 0, 5))
    r.skip(gap)
    r.pic(4863, 4884, "fx-face-04", tone=(YELLOW_DUO,))
    copies(4863, 4884, "BLOW", 740, "#7A6A10", gap_y=125)
    r.word(4863, 4884, "BLOW", 740, weight=900, layers=[SH, fill(WHITE)])
    tp = r.pic(4884, 4899, "fx-man-04")
    r.word(4884, 4899, "THEM", 640, weight=900, layers=[SH, fill(YEL)], enter=(-500, 0, 4))
    r.again(4899, 4923, tp, tone=(YELLOW_DUO,))
    para(4899, 4923)
    copies(4899, 4923, "THEM", 640, "#FFFFFF", n=2, gap_y=330)
    r.pic(4923, 4983, "fx-face-05", z=(1.0, 1.05))
    aw = r.word(4923, 4983, "AWAY", 780, weight=900, layers=GOLD, sc=[(4923, 1.5), (4929, 1.0)])
    r.fx(aw, 4923, "builtin.effects.gaussian_blur", animated={"u_blurRadius": [(4923, 25), (4929, 0)]})
    r.pic(4983, end, "fx-man-02", tone=(effect("adjust.brightness", brightness=-0.25),), enter=(-1080, 0, 4))
    r.logo(4983, end, y=900, size=300, enter=(-500, 0, 5))
    r.tagline(4983, end, 1110, WHITE, 560, start=0.6)
    r.chevrons(5010, end, 1764)
    return r.finish()


TEMPLATES = [stomp, typo, dynamic, fast, rhythm, modern]
