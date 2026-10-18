"""Vector-ish drawing kit for icon overlays (youtuber, face-cam frames).

Elements are drawn once as supersampled masks (`Pen`), painted with gradients and shadows on a small
`Art` canvas, and turned into a `Sprite`: a premultiplied RGBA image that `put` places on the frame with
sub-pixel position, scale (also squash and stretch), rotation around any pivot and opacity, in one
affine resample. Shrinking a sprite a lot goes through a pre-reduced copy, so pops stay clean.
"""

from __future__ import annotations

import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import fx
from fx import TAU, Canvas

SS = 3


# ---------------------------------------------------------------- easing

def clamp01(x):
    return min(max(x, 0.0), 1.0)


def seg(t, a, b):
    return clamp01((t - a) / (b - a)) if b > a else float(t >= a)


def ease_io(x):
    x = clamp01(x)
    return x * x * (3 - 2 * x)


def ease_io5(x):
    x = clamp01(x)
    return x * x * x * (x * (6 * x - 15) + 10)


def ease_out(x, p=3):
    x = clamp01(x)
    return 1 - (1 - x) ** p


def ease_in(x, p=3):
    return clamp01(x) ** p


def back_out(x, k=1.9):
    x = clamp01(x) - 1
    return 1 + (k + 1) * x ** 3 + k * x ** 2


def back_in(x, k=1.9):
    x = clamp01(x)
    return (k + 1) * x ** 3 - k * x ** 2


def elastic_out(x, period=0.32):
    x = clamp01(x)
    if x in (0.0, 1.0):
        return x
    return 2 ** (-10 * x) * math.sin((x - period / 4) * TAU / period) + 1


def pop_scale(t, t_in, t_out=None, dur_in=0.45, dur_out=0.3):
    """0 -> 1 with an overshoot at t_in; 1 -> 0 (a small swell first) from t_out."""
    v = back_out(seg(t, t_in, t_in + dur_in))
    if t_out is not None and t >= t_out:
        v *= 1 - back_in(seg(t, t_out, t_out + dur_out), 1.4)
    return max(v, 0.0)


def damped(t, freq, decay):
    """A damped sine that starts at t = 0 (0 before)."""
    if t <= 0:
        return 0.0
    return math.exp(-decay * t) * math.sin(TAU * freq * t)


def lerp(a, b, u):
    return a + (b - a) * u


def mix(c0, c1, u):
    return tuple(lerp(x, y, u) for x, y in zip(c0, c1))


def hexc(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    return fx.hex_rgb(h)


# ---------------------------------------------------------------- masks

class Pen:
    """Antialiased coverage drawn at SS x and box-reduced. Coordinates are `u` units from (ox, oy)."""

    def __init__(self, w, h, u=1.0, ox=0.0, oy=0.0, ss=SS):
        self.w, self.h = int(math.ceil(w)), int(math.ceil(h))
        self.k, self.u, self.ox, self.oy = ss, u, ox, oy
        self.im = Image.new("L", (self.w * ss, self.h * ss), 0)
        self.d = ImageDraw.Draw(self.im)

    def at(self, u=None, ox=None, oy=None):
        """Same image, another coordinate frame."""
        p = object.__new__(Pen)
        p.__dict__.update(self.__dict__)
        p.u = self.u if u is None else u
        p.ox = self.ox if ox is None else ox
        p.oy = self.oy if oy is None else oy
        return p

    def P(self, x, y):
        return ((x * self.u + self.ox) * self.k, (y * self.u + self.oy) * self.k)

    def L(self, v):
        return v * self.u * self.k

    def _box(self, box):
        x0, y0 = self.P(box[0], box[1])
        x1, y1 = self.P(box[2], box[3])
        return [x0, y0, x1, y1]

    def ellipse(self, box, fill=255):
        self.d.ellipse(self._box(box), fill=fill)

    def circle(self, x, y, r, fill=255):
        self.ellipse((x - r, y - r, x + r, y + r), fill)

    def ring(self, box, width, fill=255):
        self.d.ellipse(self._box(box), outline=fill, width=max(1, int(round(self.L(width)))))

    def rrect(self, box, r, fill=255):
        self.d.rounded_rectangle(self._box(box), radius=self.L(r), fill=fill)

    def rrect_line(self, box, r, width, fill=255):
        self.d.rounded_rectangle(self._box(box), radius=self.L(r), outline=fill,
                                 width=max(1, int(round(self.L(width)))))

    def rect(self, box, fill=255):
        self.d.rectangle(self._box(box), fill=fill)

    def poly(self, pts, fill=255):
        self.d.polygon([self.P(x, y) for x, y in pts], fill=fill)

    def line(self, pts, width, fill=255, caps=True):
        """A stroke with round joints and caps (stamped discs keep thick curves smooth)."""
        pts = [self.P(x, y) for x, y in pts]
        wk = self.L(width)
        r = wk / 2
        if len(pts) > 1:
            self.d.line(pts, fill=fill, width=max(1, int(round(wk))), joint="curve")
        stamp = pts if len(pts) < 400 else pts[::2] + [pts[-1]]
        for i, (x, y) in enumerate(stamp):
            if caps or 0 < i < len(stamp) - 1:
                self.d.ellipse([x - r, y - r, x + r, y + r], fill=fill)

    def text(self, xy, s, font_name, size, fill=255, anchor="mm"):
        f = fx.font(font_name, max(1, int(round(self.L(size)))))
        self.d.text(self.P(*xy), s, font=f, fill=fill, anchor=anchor)

    def cov(self) -> np.ndarray:
        return np.asarray(self.im.reduce(self.k), np.float32) / 255.0


def text_width(s, font_name, size):
    f = fx.font(font_name, max(1, int(round(size * 4))))
    b = f.getbbox(s)
    return (b[2] - b[0]) / 4


def bezier(p0, p1, p2, n=40, p3=None):
    """Points of a quadratic (or cubic, with p3) Bezier curve."""
    out = []
    for i in range(n + 1):
        t = i / n
        if p3 is None:
            x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]
            y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]
        else:
            x = (1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0] + 3 * (1 - t) * t * t * p2[0] + t ** 3 * p3[0]
            y = (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1] + 3 * (1 - t) * t * t * p2[1] + t ** 3 * p3[1]
        out.append((x, y))
    return out


def partial(pts, u):
    """The first fraction u (by length) of a polyline."""
    if u >= 1:
        return pts
    if u <= 0 or len(pts) < 2:
        return pts[:1]
    seglen = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    total = sum(seglen) * u
    out = [pts[0]]
    for (a, b), L in zip(zip(pts, pts[1:]), seglen):
        if total <= L:
            f = total / L if L else 0
            out.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f))
            return out
        out.append(b)
        total -= L
    return out


def blur(cov, r):
    if r <= 0:
        return cov
    im = Image.fromarray(np.clip(cov * 255, 0, 255).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(r))
    return np.asarray(im, np.float32) / 255.0


def grow(cov, px):
    """Dilates a mask by about px pixels (for outlines)."""
    if px <= 0:
        return cov
    n = int(px) * 2 + 1
    im = Image.fromarray(np.clip(cov * 255, 0, 255).astype(np.uint8), "L").filter(ImageFilter.MaxFilter(n | 1))
    return np.asarray(im, np.float32) / 255.0


def shift(cov, dx, dy):
    out = np.zeros_like(cov)
    h, w = cov.shape
    dx, dy = int(round(dx)), int(round(dy))
    xs0, xs1 = max(0, -dx), min(w, w - dx)
    ys0, ys1 = max(0, -dy), min(h, h - dy)
    out[ys0 + dy:ys1 + dy, xs0 + dx:xs1 + dx] = cov[ys0:ys1, xs0:xs1]
    return out


# ---------------------------------------------------------------- painting

class Art(Canvas):
    """A small canvas for building one element."""

    def __init__(self, w, h):
        super().__init__(int(math.ceil(w)), int(math.ceil(h)))
        self.yy, self.xx = np.mgrid[0:self.h, 0:self.w].astype(np.float32)

    def pen(self, u=1.0, ox=0.0, oy=0.0):
        return Pen(self.w, self.h, u, ox, oy)

    def paint(self, cov, color, opacity=1.0):
        self.layer(np.asarray(color, np.float32), np.clip(cov * opacity, 0, 1).astype(np.float32))

    def vgrad(self, cov, c0, c1, y0=None, y1=None, opacity=1.0):
        """Vertical gradient c0 (at y0) -> c1 (at y1)."""
        y0 = 0 if y0 is None else y0
        y1 = self.h if y1 is None else y1
        t = np.clip((self.yy[:, :1] - y0) / max(y1 - y0, 1e-3), 0, 1)[..., None]
        col = np.asarray(c0, np.float32) * (1 - t) + np.asarray(c1, np.float32) * t
        self.layer(col.astype(np.float32), np.clip(cov * opacity, 0, 1).astype(np.float32))

    def lgrad(self, cov, c0, c1, p0, p1, opacity=1.0):
        """Linear gradient along p0 -> p1."""
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        L2 = dx * dx + dy * dy
        t = np.clip(((self.xx - p0[0]) * dx + (self.yy - p0[1]) * dy) / L2, 0, 1)[..., None]
        col = np.asarray(c0, np.float32) * (1 - t) + np.asarray(c1, np.float32) * t
        self.layer(col.astype(np.float32), np.clip(cov * opacity, 0, 1).astype(np.float32))

    def rgrad(self, cov, cx, cy, r, stops, opacity=1.0, sy=1.0):
        """Radial gradient; stops = [(0, color), ..., (1, color)] by distance / r."""
        d = np.sqrt((self.xx - cx) ** 2 + ((self.yy - cy) / sy) ** 2) / r
        pos = np.array([p for p, _ in stops], np.float32)
        cols = np.array([c for _, c in stops], np.float32)
        col = np.stack([np.interp(d, pos, cols[:, i]) for i in range(3)], -1)
        self.layer(col.astype(np.float32), np.clip(cov * opacity, 0, 1).astype(np.float32))

    def shadow(self, cov, dx=0, dy=8, r=10, opacity=0.35, color=(0, 0, 0)):
        self.paint(shift(blur(cov, r), dx, dy), color, opacity)

    def glow(self, cov, r, color, opacity=1.0, gain=1.6):
        self.paint(np.clip(blur(cov, r) * gain, 0, 1), color, opacity)

    def gloss(self, cov, y0, y1, opacity=0.5):
        """A white sheen fading from y0 down to y1, clipped to cov."""
        t = np.clip((self.yy - y0) / max(y1 - y0, 1), 0, 1)
        self.paint(cov * (1 - t) ** 1.6 * (self.yy >= y0), (1, 1, 1), opacity)

    def clip(self, keep):
        """Keeps only what lies inside `keep` (coverage)."""
        self.rgb *= keep[..., None]
        self.a *= keep

    def erase(self, cov):
        self.clip(1 - np.clip(cov, 0, 1))

    def sprite(self) -> "Sprite":
        return Sprite.from_canvas(self)


# ---------------------------------------------------------------- sprites

class Sprite:
    def __init__(self, img: Image.Image):
        self.img = img          # mode RGBa (premultiplied)
        self.w, self.h = img.size
        self._mips = {1.0: img}

    @staticmethod
    def from_canvas(c: Canvas) -> "Sprite":
        a = np.clip(c.a, 0, 1)
        rgb = np.clip(c.rgb, 0, None)
        rgb = np.minimum(rgb, a[..., None])
        arr = np.empty((c.h, c.w, 4), np.uint8)
        arr[..., :3] = (rgb * 255 + 0.5).astype(np.uint8)
        arr[..., 3] = (a * 255 + 0.5).astype(np.uint8)
        return Sprite(Image.frombytes("RGBa", (c.w, c.h), arr.tobytes()))

    def mip(self, scale):
        f = 1.0
        while scale < 0.5 * f and f > 1 / 32:
            f /= 2
        if f not in self._mips:
            self._mips[f] = self.img.resize((max(1, round(self.w * f)), max(1, round(self.h * f))), Image.LANCZOS)
        return self._mips[f], f


def put(c: Canvas, spr: Sprite, x, y, scale=1.0, rot=0.0, opacity=1.0, pivot=None, sx=1.0, sy=1.0, add=False):
    """Places `spr` so that its `pivot` (sprite pixels, default the centre) lands on (x, y).
    rot in degrees, clockwise; sx/sy squash and stretch on top of `scale` (in the sprite's own axes)."""
    ax, ay = scale * sx, scale * sy
    if opacity <= 0.003 or ax <= 0.004 or ay <= 0.004:
        return
    img, f = spr.mip(min(ax, ay))
    ax, ay = ax / f, ay / f
    pw, ph = img.size
    pu, pv = (pw / 2, ph / 2) if pivot is None else (pivot[0] * f, pivot[1] * f)
    th = math.radians(rot)
    co, si = math.cos(th), math.sin(th)
    xs, ys = [], []
    for u, v in ((-pu, -pv), (pw - pu, -pv), (pw - pu, ph - pv), (-pu, ph - pv)):
        xs.append(x + ax * u * co - ay * v * si)
        ys.append(y + ax * u * si + ay * v * co)
    x0, x1 = max(int(math.floor(min(xs))) - 1, 0), min(int(math.ceil(max(xs))) + 1, c.w)
    y0, y1 = max(int(math.floor(min(ys))) - 1, 0), min(int(math.ceil(max(ys))) + 1, c.h)
    if x0 >= x1 or y0 >= y1:
        return
    a_ = co / ax
    b_ = si / ax
    c_ = pu + (co * (x0 - x) + si * (y0 - y)) / ax
    d_ = -si / ay
    e_ = co / ay
    f_ = pv + (-si * (x0 - x) + co * (y0 - y)) / ay
    out = img.transform((x1 - x0, y1 - y0), Image.AFFINE, (a_, b_, c_, d_, e_, f_), resample=Image.BICUBIC)
    arr = np.asarray(out, np.float32) / 255.0
    al = arr[..., 3] * opacity
    rgb = np.minimum(arr[..., :3], arr[..., 3:4]) * opacity
    region = c.rgb[y0:y1, x0:x1]
    cov = c.a[y0:y1, x0:x1]
    if add:
        region += rgb
        cov[...] = 1 - (1 - cov) * (1 - al)
    else:
        region *= (1 - al)[..., None]
        region += rgb
        cov[...] = cov * (1 - al) + al


def put_cov(c: Canvas, cov, x0, y0, color, opacity=1.0):
    """A coverage array painted with a flat colour, top-left at (x0, y0) (integers)."""
    c.splat(cov, x0 + cov.shape[1] / 2, y0 + cov.shape[0] / 2, color, opacity)


# ---------------------------------------------------------------- icons (drawn in a 100-unit box)

def icon_thumb(p: Pen, fill=255):
    p.rrect((4, 44, 24, 96), 5, fill)                       # cuff
    p.rrect((30, 40, 92, 96), 15, fill)                     # hand
    p.poly([(30, 56), (38, 34), (52, 16), (64, 40), (64, 52)], fill)
    p.line([(46, 44), (56, 8)], 20, fill)                    # thumb
    for y in (56, 70, 83):                                   # finger gaps
        p.line([(70, y), (96, y)], 3.4, 0, caps=False)


def icon_heart(p: Pen, fill=255, cx=50, cy=52, r=44):
    pts = []
    for i in range(96):
        t = i / 96 * TAU
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((cx + x / 17 * r, cy + (y + 1.5) / 17 * r))
    p.poly(pts, fill)


def icon_comment(p: Pen, fill=255, dots=True):
    p.rrect((6, 10, 94, 72), 22, fill)
    p.poly([(22, 64), (18, 94), (48, 70)], fill)
    if dots:
        for x in (30, 50, 70):
            p.circle(x, 41, 7.5, 0)


def icon_share(p: Pen, fill=255):
    p.poly([(56, 10), (96, 42), (56, 74)], fill)
    p.line(bezier((12, 90), (12, 44), (62, 42), 40), 22, fill)


def icon_bell(p: Pen, fill=255, clapper=True):
    p.circle(50, 10, 7.5, fill)
    pts = []
    for i in range(41):
        a = math.pi + i / 40 * math.pi
        pts.append((50 + 27 * math.cos(a), 40 + 26 * math.sin(a)))
    pts += [(80, 62), (88, 74), (12, 74), (20, 62)]
    p.poly(pts, fill)
    p.poly([(23, 38), (77, 38), (80, 64), (20, 64)], fill)
    p.rrect((8, 68, 92, 80), 6, fill)
    if clapper:
        p.circle(50, 88, 9, fill)


def icon_play(p: Pen, fill=255, cx=50, cy=50, r=30):
    pts = [(cx - r * 0.55, cy - r), (cx + r, cy), (cx - r * 0.55, cy + r)]
    p.poly(pts, fill)
    p.line(pts + [pts[0]], r * 0.28, fill)


def icon_person(p: Pen, fill=255):
    p.circle(50, 30, 19, fill)
    p.d.chord(p._box((14, 56, 86, 128)), 180, 360, fill=fill)


def icon_eye(p: Pen, fill=255):
    up = [(50 - 46 * math.cos(t), 50 - 30 * math.sin(t)) for t in np.linspace(0, math.pi, 40)]
    dn = [(50 + 46 * math.cos(t), 50 + 30 * math.sin(t)) for t in np.linspace(0, math.pi, 40)]
    p.poly(up + dn, fill)
    p.circle(50, 50, 21, 0)
    p.circle(50, 50, 12, fill)


def icon_check(p: Pen, fill=255, width=13):
    p.line([(22, 52), (42, 72), (80, 30)], width, fill)


def icon_cross(p: Pen, fill=255, width=14):
    p.line([(26, 26), (74, 74)], width, fill)
    p.line([(74, 26), (26, 74)], width, fill)


def cursor_pts():
    return [(10, 4), (10, 82), (29, 65), (42, 94), (56, 88), (43, 59), (68, 59)]


def icon_cursor(p: Pen, fill=255):
    p.poly(cursor_pts(), fill)


def icon_hand(p: Pen, fill=255):
    """A pointing hand: the index finger up on the left, three folded fingers as knuckles on the right."""
    p.line([(32, 9), (32, 60)], 18, fill)                    # index finger
    p.rrect((23, 50, 90, 98), 17, fill)                      # palm
    for x, y in ((50, 50), (64, 53), (78, 58)):
        p.circle(x, y, 8.5, fill)                            # knuckles
    p.rect((44, 50, 87, 70), fill)
    p.line([(12, 60), (26, 82)], 15, fill)                   # thumb


def hand_details(p: Pen, fill=255):
    """Creases between the folded fingers, drawn in the outline colour."""
    for x, y in ((57, 44), (71, 47)):
        p.line([(x, y), (x, y + 13)], 2.6, fill)


# ---------------------------------------------------------------- composite elements

def badge(icon_fn, size, c_top, c_bot, icon_color=(1, 1, 1), shadow=0.35, ring=None):
    """A glossy round badge with an icon: the 3-D button style used by the like/comment/share pops."""
    pad = size * 0.18
    W = size + 2 * pad
    art = Art(W, W)
    disc = art.pen(size / 100, pad, pad)
    disc.circle(50, 50, 50)
    dc = disc.cov()
    art.shadow(dc, 0, size * 0.06, size * 0.07, shadow)
    art.vgrad(dc, c_top, c_bot, pad, pad + size)
    rim = np.clip(dc - blur(dc, size * 0.04) * 0.0 - shift(dc, 0, -size * 0.03), 0, 1)
    art.paint(rim, (0, 0, 0), 0.18)
    if ring is not None:
        rp = art.pen(size / 100, pad, pad)
        rp.ring((1.5, 1.5, 98.5, 98.5), 3)
        art.paint(rp.cov(), ring, 0.9)
    ip = art.pen(size / 100 * 0.56, pad + size * 0.22, pad + size * 0.22)
    icon_fn(ip)
    ic = ip.cov()
    art.paint(shift(blur(ic, size * 0.012), 0, size * 0.018), (0, 0, 0), 0.22)
    art.paint(ic, icon_color)
    gl = art.pen(size / 100, pad, pad)
    gl.ellipse((14, 4, 86, 52))
    art.gloss(gl.cov() * dc, pad, pad + size * 0.5, 0.32)
    return art.sprite()


def outlined(icon_fn, size, fill_color=(1, 1, 1), line_color=(0.06, 0.06, 0.08), line=5.0, shadow=0.3,
             details=None):
    """An icon with a dark outline and a soft shadow (cursors, hands). Returns (sprite, padding)."""
    pad = size * 0.16
    W = size + 2 * pad
    art = Art(W, W)
    p = art.pen(size / 100, pad, pad)
    icon_fn(p)
    cov = p.cov()
    out = grow(cov, line * size / 100)
    out = blur(out, 0.6)
    art.shadow(out, size * 0.03, size * 0.05, size * 0.04, shadow)
    art.paint(out, line_color)
    art.vgrad(cov, fill_color, mix(fill_color, (0.82, 0.84, 0.88), 0.6), pad, pad + size)
    if details:
        dp = art.pen(size / 100, pad, pad)
        details(dp)
        art.paint(dp.cov() * cov, line_color)
    return art.sprite(), pad


def pill_button(text, font_name, height, c_top, c_bot, text_color, icon=None, icon_color=None, min_w=0,
                radius=0.5, shadow=0.35, outline=None):
    """A rounded button with a label (and an optional icon on the left). Returns (sprite, width)."""
    th = height * 0.40
    tw = text_width(text, font_name, th)
    ic_w = height * 0.62 if icon else 0
    gap = height * 0.22 if icon else 0
    w = max(min_w, tw + ic_w + gap + height * 0.95)
    pad = height * 0.35
    art = Art(w + 2 * pad, height + 2 * pad)
    p = art.pen(1, pad, pad)
    p.rrect((0, 0, w, height), height * radius)
    cov = p.cov()
    art.shadow(cov, 0, height * 0.08, height * 0.12, shadow)
    art.vgrad(cov, c_top, c_bot, pad, pad + height)
    if outline is not None:
        o = art.pen(1, pad, pad)
        o.rrect_line((0, 0, w, height), height * radius, height * 0.035)
        art.paint(o.cov(), outline, 0.8)
    gl = art.pen(1, pad, pad)
    gl.rrect((height * 0.08, height * 0.05, w - height * 0.08, height * 0.5), height * radius * 0.8)
    art.gloss(gl.cov() * cov, pad, pad + height * 0.55, 0.22)
    x = (w - tw - ic_w - gap) / 2
    if icon:
        ip = art.pen(ic_w / 100, pad + x, pad + (height - ic_w) / 2)
        icon(ip)
        art.paint(ip.cov(), icon_color or text_color)
        x += ic_w + gap
    tp = art.pen(1, pad, pad)
    tp.text((x + tw / 2, height * 0.52), text, font_name, th)
    tc = tp.cov()
    art.paint(shift(blur(tc, 1.2), 0, height * 0.02), (0, 0, 0), 0.18)
    art.paint(tc, text_color)
    return art.sprite(), w


def ripple(c: Canvas, x, y, age, r_max, color=(1, 1, 1), width=6.0, dur=0.5):
    """A ring that grows and fades from a click point."""
    if age < 0 or age > dur:
        return
    u = age / dur
    r = int(r_max * ease_out(u))
    if r < 2:
        return
    c.splat(fx.ring(r, width * (1 - 0.5 * u)), x, y, color, (1 - u) ** 1.5 * 0.9)


def burst_lines(c: Canvas, x, y, age, r0, r1, color, n=8, width=10.0, dur=0.45, rot=0.0):
    """Short strokes shooting out from a point (the 'pop' accent)."""
    if age < 0 or age > dur:
        return
    u = age / dur
    head = r0 + (r1 - r0) * ease_out(u, 2)
    tail = r0 + (r1 - r0) * ease_out(max(u - 0.25, 0) / 0.75, 2)
    size = int(2 * r1 + 2 * width + 8)
    p = Pen(size, size)
    for k in range(n):
        a = rot + k / n * TAU
        p.line([(size / 2 + math.cos(a) * tail, size / 2 + math.sin(a) * tail),
                (size / 2 + math.cos(a) * head, size / 2 + math.sin(a) * head)], width * (1 - 0.6 * u))
    c.splat(p.cov(), x, y, color, 1.0)
