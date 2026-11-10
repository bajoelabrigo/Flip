"""TIKTOK folder video 7 as Stock templates (tk7-*). See docs/plan-tiktok.md.

«Flow Reels» colour/flowers pack (48513831.mp4, 1920×1080 at 29.97 fps): vertical 9:16 photo-collage stories on a
white page (panels inset 24 px, 24 px gaps, rounded corners), shown in the reference inside floating phones and in a
«PREVIEW OF ALL SCENES» grid. Each story is laid out on 1080×1920 from the grid cells (×4.7) and its moves are copied
from the phone shots (10 fps sheets): photos and colour panels scroll in and push each other (from the top, the
bottom or the sides), a full photo shrinks to make room for a panel, the words of a panel fade in one after another
rising a little, a text-only panel leaves through a white line that strikes its middle word and opens into a gap.
Kit de TikTok; ids `tk7-*`, order 14700-. Study notes in tienda/plantillas/estudio-48513831/NOTAS.md.

The helpers here (class `R`, `pic`, `panel`, `lines`, `strike_split`, `cta`) are shared with `templates_tk8`.
"""

from __future__ import annotations

import templates_llt_f as f6
from scene import gradient, keys, no_stroke
from kit import Box, tall
from llt_motion import frames_of
from templates_tit_c import FPS, k
from templates_tit_e import solid
from templates_yp4 import T, art_except

W, H = 1080, 1920
WHITE = "#FFFFFF"
M, G, RAD = 24, 24, 30          # outer margin, gap between panels, panel corner radius (story px)
TN = 14                         # frames of a scroll / push (≈0.47 s)
FULL = (M, M, W - M, H - M)
OPEN = "Open Sans"
for w, f in ((700, "Bold"), (800, "ExtraBold")):
    f6._FILES[(OPEN, w)] = f"fonts.basic/fonts/opensans/OpenSans-{f}.ttf"

# Colours measured on the grid of the reference (top/left colour, bottom/right colour).
RUST = ("#A63B15", "#822207")
TEAL = ("#215272", "#2E5F80")
BLUE = ("#3A75BC", "#1C5687")
CREAM = ("#F2E7A2", "#EADB86")
OCHRE = ("#D4BD52", "#C9B246")
BRICK = ("#B4493A", "#A63E2B")
GOLD = ("#D2A923", "#C99F17")
RED = ("#C66D6B", "#92311B")
SKY = ("#4F80D6", "#2F5A9E")
DARK = "#4A3A1C"
INK_RED = "#4F1B0B"


def _p(prefix, id, es, en, order, dur, tags=(), thumb=None):
    return tall(f"{prefix}-{id}", es, en, "tiktok", dur, order=order,
                tags=["tiktok", "historia", "reels"] + list(tags), thumb_at=thumb or round(dur * 0.6, 1))


def grad(c, angle=90):
    return [gradient([(0.0, c[0]), (1.0, c[1])], angle=angle), no_stroke()]


def off(r, dx, dy):
    return (r[0] + dx, r[1] + dy, r[2] + dx, r[3] + dy)


def mix(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(4))


def cen(r):
    return (r[0] + r[2]) / 2, (r[1] + r[3]) / 2


def size(r):
    return r[2] - r[0], r[3] - r[1]


def push(direction, at, n=TN):
    """A whole-scene push off the frame: direction "up" | "down" | "left" | "right", from frame `at`."""
    vx, vy = {"up": (0, -(H + G)), "down": (0, H + G), "left": (-(W + G), 0), "right": (W + G, 0)}[direction]
    return lambda fr: (vx * k(fr, at, n), vy * k(fr, at, n))


def come(direction, at, n=TN):
    """Offset of something that comes in from `direction` side ("top", "bottom", "left", "right") at frame `at`."""
    vx, vy = {"top": (0, -(H + G)), "bottom": (0, H + G), "left": (-(W + G), 0), "right": (W + G, 0)}[direction]
    return lambda fr: (vx * (1 - k(fr, at, n)), vy * (1 - k(fr, at, n)))


class R(T):
    """A reel story on a white page: frames count straight from the start (no mirrored exit); `out(fr)` is the
    whole-scene offset of the exit (a push), added to everything placed after it is set."""

    def __init__(self, t, dur, out=None):
        T.__init__(self, t, dur)
        self.out = out or (lambda fr: (0.0, 0.0))

    def frame(self, u):
        return u * FPS

    def placed(self, rect):
        return lambda fr: off(rect(fr), *self.out(fr))


def page(s, colour=WHITE):
    return s.rect("Fondo", solid(colour), lambda fr, u: (-10, -10, W + 10, H + 10))


def panel(s, name, colours, rect, angle=90, rest=None):
    """A colour panel with rounded corners following rect(fr) (story px); rest = its size at rest (radius)."""
    r = s.placed(rect)
    rw, rh = size(rest or rect(10 ** 6))
    return s.rect(name, grad(colours, angle), lambda fr, u: r(fr), radius=RAD, base=(rw, rh))


def pic(s, name, sample, rect, box=None, label=None, op=None, zoom=None, follow=(1.0, 1.0)):
    """A photo slot shown through a rounded window that follows rect(fr). The picture covers `box` (the biggest
    window by default) and travels with the window's centre; zoom(fr) scales it about that centre."""
    t = s.t
    r = s.placed(rect)
    rs = [r(fr) for _, fr in s.each()]
    if box is None:
        bw = max(size(x)[0] for x in rs)
        bh = max(size(x)[1] for x in rs)
        cx, cy = cen(rect(10 ** 6))
        box = (cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2)
    b = Box(box[0], box[1], box[2] - box[0], box[3] - box[1])
    motion = []
    for u, fr in s.each():
        x0, y0, x1, y1 = r(fr)
        sc = zoom(fr) if zoom else 1.0
        motion.append((u, {"s": sc, "dx": follow[0] * ((x0 + x1) / 2 - b.cx), "dy": follow[1] * ((y0 + y1) / 2 - b.cy)},
                       "linear"))
    clip = t.photo(t.track("video", name), sample, 0.0, s.dur, b, motion, label=label or name)
    clip["name"] = name
    rw, rh = size(rect(10 ** 6))
    window = s.rect(f"{name} (marco)", solid(WHITE), lambda fr, u: r(fr), radius=RAD, base=(rw, rh),
                    op=(lambda fr, u: op(fr)) if op else None)
    clip["matte"] = {"clip": window["id"], "mode": "alpha"}
    if op:
        clip["opacity"] = keys([(u, round(max(0.0, min(1.0, op(fr))), 4), "linear") for u, fr in s.each()])
    return clip


def stack(words, cx, width, top, gap, family=OPEN, weight=800, widths=None):
    """Ink boxes of words stacked as one justified block: every line `width` px wide (or widths[i]), centred on
    cx, their heights from the face's own proportions, `gap` px apart, the first one's top at `top`."""
    f = f6._font(family, weight)
    cap = f.getbbox("H")
    ch = cap[3] - cap[1]
    out, y = [], top
    for i, wd in enumerate(words):
        bb = f.getbbox(wd)
        wdt = widths[i] if widths else width
        h = wdt * ch / max(1, bb[2] - bb[0])
        out.append((cx - wdt / 2, y, cx + wdt / 2, y + h))
        y += h + gap
    return out


def band(words, bands, cx, max_w, family=OPEN, weight=800, dy=0.0):
    """Ink boxes of words at the heights measured on the reference (bands = [(top, bottom)] story px), each as wide
    as the face makes it, centred on cx; a line wider than max_w is shrunk about its band's centre."""
    f = f6._font(family, weight)
    cap = f.getbbox("H")
    ch = cap[3] - cap[1]
    out = []
    for wd, (y0, y1) in zip(words, bands):
        bb = f.getbbox(wd)
        h = y1 - y0
        w = h * (bb[2] - bb[0]) / ch
        if w > max_w:
            h *= max_w / w
            w = max_w
        cy = (y0 + y1) / 2 + dy
        out.append((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2))
    return out


def block_height(words, width, gap, family=OPEN, weight=800, widths=None):
    inks = stack(words, 0, width, 0, gap, family, weight, widths)
    return inks[-1][3]


def lines(s, words, colours, inks, at, step=5, n=10, rise=36, holder=None, rest=None, family=OPEN, weight=800,
          names=None, way="up", order=None, out=None):
    """The words of a panel, one text each, fading in one after another from frame `at` (`step` frames apart)
    and rising `rise` px (way "left": sliding in from the left instead). holder(fr) = the panel's rect, rest = that
    rect at rest: the words ride and scale with it. out(i) = the exit offset fn of line i (default the scene's)."""
    clips = []
    order = order or list(range(len(words)))
    for i, (wd, colour, ink) in enumerate(zip(words, colours, inks)):
        at_i = at + step * order.index(i)
        ex = out(i) if out else s.out

        def geom(fr, u, ink=ink, at_i=at_i, ex=ex):
            p = k(fr, at_i, n)
            dx, dy, sc = 0.0, 0.0, 1.0
            if holder:
                hr, rr = holder(fr), rest
                sc = size(hr)[0] / size(rr)[0]
                hx, hy = cen(hr)
                rx, ry = cen(rr)
                ix, iy = cen(ink)
                dx, dy = hx + (ix - rx) * sc - ix, hy + (iy - ry) * sc - iy
            if way == "left":
                dx -= 140 * (1 - p)
            else:
                dy += rise * (1 - p)
            ox, oy = ex(fr)
            return dx + ox, dy + oy, max(1e-3, sc), 0, p
        name = names[i] if names else ("Título" if i == 0 else f"Texto {i}")
        clips.append(s.say(wd, ink, family, weight, colour, name, geom=geom))
    return clips


def strike_split(s, y, at, colour=WHITE, n=12):
    """The exit of a text-only panel: a thin white line strikes across at height y (left to right), then opens into a
    white gap that grows until it fills the frame (the halves leave up and down). Returns the offset fns of what is
    above and below the line."""
    gap = lambda fr: (H * 1.05) * k(fr, at + 6, n)  # noqa: E731
    s.rect("Línea", solid(colour), lambda fr, u: (0, y - 5 - gap(fr) / 2, W * k(fr, at, 6),
                                                   y + 5 + gap(fr) / 2), op=lambda fr, u: 1.0 if fr >= at else 0.0)
    return (lambda fr: (0.0, -gap(fr) / 2)), (lambda fr: (0.0, gap(fr) / 2))


def chevrons(s, cx, cy, size, colour, at, name="Flechas", period=24, double=True):
    """An up chevron (a second one above it, blinking) that bobs up every `period` frames."""
    path = "M 0 70 L 50 20 L 100 70 L 88 82 L 50 44 L 12 82 Z"

    def bob(fr):
        if fr < at:
            return 0.0
        ph = ((fr - at) % period) / period
        return -10 * (1 - abs(2 * ph - 1))
    s.obj(name, solid(colour), lambda fr, u: (cx, cy + bob(fr), size, size, 0, k(fr, at, 8)), path=path,
          base=(size, size))
    if double:
        def op2(fr):
            if fr < at:
                return 0.0
            ph = ((fr - at) % period) / period
            return k(fr, at, 8) * (0.35 + 0.65 * (1 - abs(2 * ph - 1)))
        s.obj(f"{name} 2", solid(colour), lambda fr, u: (cx, cy - size * 0.32 + bob(fr), size, size, 0, op2(fr)),
              path=path, base=(size, size))


def logo(s, box, at, n=12, out=None):
    """The user's logo slot (logo-flip) fading in at frame `at` (growing from 90 %)."""
    t = s.t
    b = Box(box[0], box[1], box[2] - box[0], box[3] - box[1])
    ex = out or s.out
    motion = []
    for u, fr in s.each():
        ox, oy = ex(fr)
        motion.append((u, {"s": 0.9 + 0.1 * k(fr, at, n), "dx": ox, "dy": oy}, "linear"))
    clip = t.photo(t.track("video", "Logo"), "logo-flip", 0.0, s.dur, b, motion, label="Tu logo", brandRole="logo")
    clip["name"] = "Logo"
    clip["opacity"] = keys([(u, round(k(fr, at, n), 4), "linear") for u, fr in s.each()])
    return clip


def finish(t):
    """Roles for the other shape: the white page stretches (backdrop), the story is one column of art. Four white
    bands just outside the story frame, on top of everything, hide in a horizontal video what slides in from off the
    frame (in the 9:16 frame they are off the canvas)."""
    for i, (x0, y0, x1, y1) in enumerate(((-3 * W, -3 * H, 0, 4 * H), (W, -3 * H, 4 * W, 4 * H), (0, -3 * H, W, 0),
                                          (0, H, W, 4 * H))):
        c = t.solid(t.track("shape", f"Marco {i + 1}"), WHITE, 0.0, t.duration, Box(x0, y0, x1 - x0, y1 - y0))
        c["name"] = f"Marco {i + 1}"
    return art_except(t, keep=("Fondo",))


# ======================================================================================================================
# tk7 — colour / flowers
# ======================================================================================================================

P = "tk7"
TAGS = ["flores", "colores", "moda"]


# --- 1. CANVAS / LIFE / BODY: the collage comes out of a horizontal opening, the words fade up, the reel scrolls up -
def canvas():
    D = 4.2
    t = _p(P, "canvas", "Historia: collage CANVAS LIFE BODY", "Story: CANVAS LIFE BODY collage", 14700, D, TAGS)
    s = R(t, D, out=push("up", round((D - 0.5) * FPS)))
    page(s)
    a = lambda fr: k(fr, 0, 16)  # noqa: E731  the panels settle
    top, bot = (M, M, W - M, 800), (M, 1190, W - M, H - M)
    row = [(M, 824, 352, 1166), (376, 824, 704, 1166), (728, 824, W - M, 1166)]
    pic(s, "Foto 1", "tk7-flora-07", lambda fr: off(top, 0, -420 * (1 - a(fr))))
    pic(s, "Foto 4", "tk7-flora-03", lambda fr: off(bot, 0, 420 * (1 - a(fr))))

    def grow(r):
        cy = (r[1] + r[3]) / 2
        return lambda fr: (r[0], cy - (r[3] - r[1]) / 2 * a(fr), r[2], cy + (r[3] - r[1]) / 2 * a(fr))
    pic(s, "Foto 2", "tk7-flora-09", grow(row[0]), box=row[0])
    holder = grow(row[1])
    panel(s, "Panel", RUST, holder, rest=row[1], angle=0)
    pic(s, "Foto 3", "tk7-flora-11", grow(row[2]), box=row[2])
    words = ["CANVAS", "LIFE", "BODY"]
    inks = band(words, [(881, 929), (943, 1029), (1048, 1110)], 540, 280)
    lines(s, words, [WHITE] * 3, inks, 12, holder=lambda fr: row[1], rest=row[1])
    return finish(t)


# --- 2. COLORFUL / AND / CONFIDENCE: a photo, a teal panel pushes it down, then another photo pushes both down ----
def colorful_and():
    D = 4.6
    t = _p(P, "colorful-and", "Historia: COLORFUL AND CONFIDENCE entre dos fotos",
           "Story: COLORFUL AND CONFIDENCE between two photos", 14701, D, TAGS)
    s = R(t, D, out=push("up", round((D - 0.5) * FPS)))
    page(s)
    L1p, L1b = (M, M, W - M, 642), (M, 666, W - M, H - M)
    L2t, L2p, L2b = (M, M, W - M, 620), (M, 644, W - M, 1262), (M, 1286, W - M, H - M)
    enter = come("bottom", 0)
    a, b = (lambda fr: k(fr, 22, TN)), (lambda fr: k(fr, 64, TN))

    def bottom(fr):
        r = mix(FULL, L1b, a(fr))
        r = mix(r, L2b, b(fr))
        return off(r, *enter(fr))

    def mid(fr):
        r = off(L1p, 0, -(L1p[3] + G) * (1 - a(fr)))
        return mix(r, L2p, b(fr))

    def top(fr):
        return off(L2t, 0, -(L2t[3] + G) * (1 - b(fr)))
    pic(s, "Foto 2", "tk7-flora-10", bottom, box=FULL)
    panel(s, "Panel", TEAL, mid, rest=L2p)
    pic(s, "Foto 1", "tk7-flora-01", top)
    words = ["COLORFUL", "AND", "CONFIDENCE"]
    inks = band(words, [(743, 819), (848, 1072), (1101, 1182)], 540, 860)
    lines(s, words, [WHITE] * 3, inks, 32, step=5, holder=mid, rest=L2p, order=[2, 1, 0])
    return finish(t)


# --- 3. EMBRACE / EXPRESSION: two rust bands push a photo from the top and the bottom -----------------------------
def embrace():
    D = 4.0
    t = _p(P, "embrace", "Historia: EMBRACE y EXPRESSION con foto en medio", "Story: EMBRACE and EXPRESSION around a "
           "photo", 14702, D, TAGS)
    s = R(t, D, out=push("up", round((D - 0.5) * FPS)))
    page(s)
    up, mid, dn = (M, M, W - M, 420), (M, 444, W - M, 1450), (M, 1474, W - M, H - M)
    enter = come("bottom", 0)
    a = lambda fr: k(fr, 20, TN)  # noqa: E731
    pic(s, "Foto", "tk7-bloom-06", lambda fr: off(mix(FULL, mid, a(fr)), *enter(fr)),
        box=FULL)
    h1 = lambda fr: off(up, 0, -(up[3] + G) * (1 - a(fr)))  # noqa: E731
    h2 = lambda fr: off(dn, 0, (H - dn[1] + G) * (1 - a(fr)))  # noqa: E731
    panel(s, "Panel", RUST, h1, rest=up, angle=0)
    panel(s, "Panel 2", RUST, h2, rest=dn, angle=0)
    i1 = band(["EMBRACE"], [(167, 286)], 540, 860)[0]
    i2 = band(["EXPRESSION"], [(1639, 1739)], 540, 860)[0]
    lines(s, ["EMBRACE"], [WHITE], [i1], 30, holder=h1, rest=up)
    lines(s, ["EXPRESSION"], [WHITE], [i2], 36, holder=h2, rest=dn, names=["Texto"])
    return finish(t)


# --- 4. COLORFUL / CHARACTERS: a blue panel rises and the photo shrinks to the top -------------------------------
def characters():
    D = 3.6
    t = _p(P, "characters", "Historia: COLORFUL CHARACTERS bajo una foto", "Story: COLORFUL CHARACTERS under a photo",
           14703, D, TAGS)
    s = R(t, D, out=push("up", round((D - 0.5) * FPS)))
    page(s)
    ph, pn = (M, M, W - M, 1280), (M, 1304, W - M, H - M)
    enter = come("top", 0)
    a = lambda fr: k(fr, 18, TN)  # noqa: E731
    pic(s, "Foto", "tk7-flora-10", lambda fr: off(mix(FULL, ph, a(fr)), *enter(fr)), box=FULL)
    hold = lambda fr: off(pn, 0, (H - pn[1] + G) * (1 - a(fr)))  # noqa: E731
    panel(s, "Panel", BLUE, hold, rest=pn, angle=180)
    words = ["COLORFUL", "CHARACTERS"]
    inks = band(words, [(1472, 1582), (1639, 1725)], 540, 880)
    lines(s, words, [WHITE] * 2, inks, 26, holder=hold, rest=pn)
    return finish(t)


# --- 5. SALE SALE SALE: two photos scroll by, the second shrinks to the top and a cream panel rises with SALE ×3 -
def sale():
    D = 5.4
    t = _p(P, "sale", "Historia: SALE SALE SALE con dos fotos", "Story: SALE SALE SALE with two photos", 14704, D,
           TAGS + ["oferta"])
    s = R(t, D, out=push("up", round((D - 0.5) * FPS)))
    page(s)
    b1 = lambda fr: k(fr, 40, TN)  # noqa: E731  photo 2 scrolls up over photo 1
    b2 = lambda fr: k(fr, 70, TN)  # noqa: E731  the panel rises
    ph, pn = (M, M, W - M, 940), (M, 964, W - M, H - M)
    pic(s, "Foto 1", "tk7-bloom-04", lambda fr: off(off(FULL, *come("top", 0)(fr)), 0, -(H + G) * b1(fr)))

    def p2(fr):
        return mix(off(FULL, 0, (H + G) * (1 - b1(fr))), ph, b2(fr))
    pic(s, "Foto 2", "tk7-flora-05", p2, box=FULL)
    hold = lambda fr: off(pn, 0, (H - pn[1] + G) * (1 - b2(fr)))  # noqa: E731
    panel(s, "Panel", CREAM, hold, rest=pn, angle=0)
    words = ["SALE"] * 3
    inks = band(words, [(1158, 1310), (1367, 1520), (1577, 1729)], 540, 640)
    lines(s, words, [DARK] * 3, inks, 74, step=4, holder=hold, rest=pn)
    return finish(t)


# --- text-only panel with the strike-and-split exit (BLOOMS ALL AROUND, FLOWER PARADISE DELIGHT, tk8 ones) --------
def text_panel(t, D, colours, words, colours_txt, bands, cy, gap, enter, way="up", family=OPEN, weight=800, angle=45,
               step=5, word_at=6):
    s = R(t, D)
    page(s)
    hold = lambda fr: off(FULL, *enter(fr))  # noqa: E731
    split_at = round((D - 0.75) * FPS)
    inks = band(words, bands, 540, 800, family, weight)
    mid = len(words) // 2
    y_line = (inks[mid][1] + inks[mid][3]) / 2
    # the panel and the words, then the white line on top
    gap_fn = lambda fr: (H * 1.05) * k(fr, split_at + 6, 12)  # noqa: E731
    panel(s, "Panel", colours, hold, rest=FULL, angle=angle)

    def out_of(i):
        if i < mid:
            return lambda fr: (0.0, -gap_fn(fr) / 2)
        if i > mid:
            return lambda fr: (0.0, gap_fn(fr) / 2)
        return lambda fr: (0.0, 0.0)
    clips = lines(s, words, colours_txt, inks, word_at, step=step, holder=hold, rest=FULL, family=family,
                  weight=weight, way=way, out=out_of)
    strike_split(s, y_line, split_at)
    return s, clips


def blooms():
    D = 3.6
    t = _p(P, "blooms", "Historia: BLOOMS ALL AROUND en rojo", "Story: BLOOMS ALL AROUND in red", 14705, D,
           TAGS + ["texto"])
    text_panel(t, D, RED, ["BLOOMS", "ALL", "AROUND"], [WHITE] * 3, [(562, 705), (713, 1009), (1028, 1175)], 0, 0,
               come("bottom", 0), angle=135)
    return finish(t)


def flower():
    D = 3.6
    t = _p(P, "flower", "Historia: FLOWER PARADISE DELIGHT en azul", "Story: FLOWER PARADISE DELIGHT in blue", 14706,
           D, TAGS + ["texto"])
    text_panel(t, D, SKY, ["FLOWER", "PARADISE", "DELIGHT"], [WHITE] * 3, [(644, 804), (825, 968), (990, 1159)], 0,
               0, come("left", 0), way="left", angle=90)
    return finish(t)


# --- 6. BREEZY SPRING ATTIRE: a photo, three photos come in from the sides and rearrange into the collage --------
def breezy():
    D = 5.6
    t = _p(P, "breezy", "Historia: collage BREEZY SPRING ATTIRE", "Story: BREEZY SPRING ATTIRE collage", 14707, D,
           TAGS)
    s = R(t, D, out=push("right", round((D - 0.5) * FPS)))
    page(s)
    S1, S2, S3 = (M, M, W - M, 620), (M, 644, W - M, 1262), (M, 1286, W - M, H - M)
    TL, TR = (M, M, 580, 946), (604, M, W - M, 946)
    ML, MR = (M, 970, 580, 1426), (604, 970, W - M, 1426)
    B1, B2, B3 = (M, 1450, 580, H - M), (604, 1450, 818, H - M), (842, 1450, W - M, H - M)
    pic(s, "Foto 1", "tk7-flora-02", lambda fr: off(FULL, *come("bottom", 0)(fr)), op=lambda fr: 1.0 if fr < 56 else 0.0)
    r = lambda fr: k(fr, 74, 16)  # noqa: E731  rearrange
    pic(s, "Foto 2", "tk7-flora-01", lambda fr: mix(off(S1, *come("right", 34)(fr)), TL, r(fr)))
    pic(s, "Foto 3", "tk7-flora-07", lambda fr: mix(off(S2, *come("left", 37)(fr)), MR, r(fr)))
    pic(s, "Foto 4", "tk7-bloom-06", lambda fr: mix(off(S3, *come("right", 40)(fr)), B3, r(fr)))
    pic(s, "Foto 5", "tk7-flora-11", lambda fr: off(TR, *come("right", 76)(fr)))
    hold = lambda fr: off(ML, *come("left", 80)(fr))  # noqa: E731
    panel(s, "Panel", BLUE[::-1], hold, rest=ML, angle=0)
    pic(s, "Foto 6", "tk7-flora-09", lambda fr: off(B1, *come("bottom", 80)(fr)))
    pic(s, "Foto 7", "tk7-bloom-03", lambda fr: off(B2, *come("bottom", 83)(fr)))
    words = ["BREEZY", "SPRING", "ATTIRE"]
    inks = band(words, [(1053, 1124), (1162, 1239), (1277, 1353)], 302, 470)
    lines(s, words, [WHITE] * 3, inks, 92, holder=hold, rest=ML)
    return finish(t)


# --- 7. BOLD COLORS SWAY: two tall photos open from the middle, a photo drops in, an ochre panel rises ------------
def bold():
    D = 5.0
    t = _p(P, "bold", "Historia: collage BOLD COLORS SWAY", "Story: BOLD COLORS SWAY collage", 14708, D, TAGS)
    s = R(t, D, out=push("left", round((D - 0.5) * FPS)))
    page(s)
    L0, R0 = (M, M, 530, H - M), (554, M, W - M, H - M)
    L1, RT, RM = (M, M, 530, 1266), (554, M, W - M, 634), (554, 658, W - M, 1266)
    PB, RB = (M, 1290, 530, H - M), (554, 1290, W - M, H - M)
    o = lambda fr: k(fr, 0, 14)  # noqa: E731  the opening from the middle line
    b = lambda fr: k(fr, 44, TN)  # noqa: E731

    def opened(r):
        return lambda fr: (r[0], 960 + (r[1] - 960) * o(fr), r[2], 960 + (r[3] - 960) * o(fr))
    pic(s, "Foto 1", "tk7-flora-09", lambda fr: mix(opened(L0)(fr), L1, b(fr)), box=L0)
    pic(s, "Foto 2", "tk7-bloom-04", lambda fr: mix(opened(R0)(fr), RM, b(fr)), box=R0)
    pic(s, "Foto 3", "tk7-bloom-01", lambda fr: off(RT, 0, -(RT[3] + G) * (1 - b(fr))))
    hold = lambda fr: off(PB, 0, (H - PB[1] + G) * (1 - k(fr, 48, TN)))  # noqa: E731
    panel(s, "Panel", OCHRE, hold, rest=PB)
    pic(s, "Foto 4", "tk7-flora-06", lambda fr: off(RB, 0, (H - RB[1] + G) * (1 - k(fr, 48, TN))))
    words = ["BOLD", "COLORS", "SWAY"]
    inks = band(words, [(1429, 1529), (1563, 1629), (1663, 1758)], 277, 420)
    lines(s, words, [WHITE, "#523F0E", WHITE], inks, 58, holder=hold, rest=PB)
    return finish(t)


# --- 8. EMBRACE YOUR LIFE: a big photo, the grid above it drops in from the top and pushes it down -----------------
def your_life():
    D = 4.6
    t = _p(P, "embrace-your-life", "Historia: EMBRACE YOUR LIFE con cuatro fotos", "Story: EMBRACE YOUR LIFE with four "
           "photos", 14709, D, TAGS)
    s = R(t, D, out=push("up", round((D - 0.5) * FPS)))
    page(s)
    TL, TR, ML, MR, BIG = (M, M, 528, 530), (552, M, W - M, 530), (M, 554, 528, 1058), (552, 554, W - M, 1058), \
        (M, 1082, W - M, H - M)
    a = lambda fr: k(fr, 26, TN)  # noqa: E731
    drop = lambda r: (lambda fr: off(r, 0, -(1058 + G) * (1 - a(fr))))  # noqa: E731
    pic(s, "Foto 4", "tk7-flora-05", lambda fr: off(mix(FULL, BIG, a(fr)), *come("bottom", 0)(fr)), box=FULL)
    pic(s, "Foto 1", "tk7-flora-07", drop(TL))
    hold = drop(TR)
    panel(s, "Panel", BRICK, hold, rest=TR)
    pic(s, "Foto 2", "tk7-flora-11", drop(ML))
    pic(s, "Foto 3", "tk7-bloom-03", drop(MR))
    words = ["EMBRACE", "YOUR", "LIFE"]
    inks = band(words, [(119, 172), (200, 286), (310, 438)], 804, 420)
    lines(s, words, [WHITE, INK_RED, WHITE], inks, 40, holder=hold, rest=TR)
    return finish(t)


# --- 9. SAVOR MOMENTS NOW: a tall photo makes room for a column of photos and a gold panel sliding in from the left -
def savor():
    D = 4.6
    t = _p(P, "savor", "Historia: SAVOR MOMENTS NOW con columna de fotos", "Story: SAVOR MOMENTS NOW with a column of "
           "photos", 14710, D, TAGS)
    s = R(t, D, out=push("up", round((D - 0.5) * FPS)))
    page(s)
    BIG = (504, M, W - M, H - M)
    col = [(M, M, 480, 476), (M, 500, 480, 952), (M, 976, 480, 1420), (M, 1444, 480, H - M)]
    a = lambda fr: k(fr, 22, TN)  # noqa: E731
    pic(s, "Foto 1", "tk7-flora-01", lambda fr: off(mix(FULL, BIG, a(fr)), *come("right", 0)(fr)), box=FULL)
    pic(s, "Foto 2", "tk7-flora-10", lambda fr: off(col[0], *come("left", 22)(fr)))
    pic(s, "Foto 3", "tk7-flora-02", lambda fr: off(col[1], *come("left", 25)(fr)))
    pic(s, "Foto 4", "tk7-flora-06", lambda fr: off(col[2], *come("left", 28)(fr)))
    hold = lambda fr: off(col[3], *come("left", 31)(fr))  # noqa: E731
    panel(s, "Panel", GOLD, hold, rest=col[3])
    words = ["SAVOR", "MOMENTS", "NOW"]
    inks = band(words, [(1534, 1610), (1634, 1687), (1706, 1810)], 252, 400)
    lines(s, words, [WHITE, "#4B3408", WHITE], inks, 44, holder=hold, rest=col[3])
    return finish(t)


# --- 10. DISCOVER MORE: a photo slides in, the blue end panel covers it, the logo, the words and the button --------
def cta_screen(t, D, sample, colours, words, colours_txt, inks, family, weight, button, angle=90, photo_from="right"):
    s = R(t, D)
    page(s)
    pic(s, "Foto", sample, lambda fr: off(FULL, *come(photo_from, 0)(fr)), op=lambda fr: 1.0 if fr < 60 else 0.0)
    hold = lambda fr: off(FULL, *come("right", 40)(fr))  # noqa: E731
    panel(s, "Panel", colours, hold, rest=FULL, angle=angle)
    logo(s, (330, 500, 750, 980), 52)
    lines(s, words, colours_txt, inks, 62, step=7, family=family, weight=weight,
          holder=hold, rest=FULL, names=["Título", "Texto"][:len(words)] + ["Texto 2"] * max(0, len(words) - 2))
    button(s)
    return s


def discover():
    D = 6.0
    t = _p(P, "discover-more", "Historia final: DISCOVER MORE con tu logo", "End story: DISCOVER MORE with your logo",
           14711, D, TAGS + ["final", "logo"], thumb=5.0)
    inks = band(["DISCOVER", "MORE"], [(1157, 1250), (1259, 1413)], 540, 760)

    def button(s):
        s.obj("Botón", [{"id": "fill", "kind": "fill", "enabled": False,
                         "paint": {"kind": "solid", "color": "#00000000"}},
                        {"id": "stroke", "kind": "stroke", "enabled": True, "width": 6, "strokeAlign": "center",
                         "opacity": 1.0, "paint": {"kind": "solid", "color": "#ffffffff"}}],
              lambda fr, u: (540, 1660, 156, 156, 0, k(fr, 78, 10)), kind="ellipse", base=(156, 156))
        chevrons(s, 540, 1668, 64, WHITE, 82)
    cta_screen(t, D, "tk7-flora-06", SKY, ["DISCOVER", "MORE"], [WHITE, WHITE], inks, OPEN, 800, button)
    return finish(t)


TEMPLATES = [canvas, colorful_and, embrace, characters, sale, blooms, flower, breezy, bold, your_life, savor, discover]
