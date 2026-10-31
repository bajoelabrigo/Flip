"""Logo lower thirds (2026-10-31), copied frame by frame from the second reference Jorge sent (15488414.mp4, 24 lower
thirds with a logo: «lo más parecido posible, casi iguales»). Every bar and edge plays its measured curve
(lt_ref/<name>.json, 25 fps scaled to 1080p); texts sit where the reference has them; the logo is a slot («Tu
logo»), shown with the app's premium flame as the sample (logo-09…14, Jorge: «el logo es el del fuego»). Order 8530-8569.
"""

from __future__ import annotations

import math
from pathlib import Path

from kit import Box, centered, label, photo_bg, wide
from llt_motion import RED, WHITE, caps_box, duration, edge, effect_track, mask_track, name_text, rect_track, runs_at
from lt_motion import Ref
from scene import effect, keys


def _kit(id, es, en, dur, order, tags, **kw):
    return wide(f"llt-{id}", es, en, "ytkit", dur, order=order, tags=["kit:lowerthirds", "tercio", "logo"] + tags, **kw)


def _logo_square(t, r, sq: Box, dur, logo="logo-10", logo_share=0.74, colour=RED, white=WHITE):
    """The square logo of «francois»: a white corner (an L) thickens into a white square; the coloured square with the
    logo shows from the top and left while the white shrinks into the bottom-right corner. Bands: lgv (the square's
    right column, rows), lgh (its bottom rows, columns)."""
    x1, y1 = sq.x + sq.w, sq.y + sq.h
    yw = edge(r, "lgv", "warm", "max", before=sq.y, after=sq.y)          # the colour's bottom on the right column
    xw = edge(r, "lgh", "warm", "max", before=sq.x, after=sq.x)          # the colour's right end on the bottom rows
    wt = edge(r, "lgv", "white", "min", before=y1, after=y1)             # the white's top on the right column
    thick = lambda u: y1 - wt(u)  # noqa: E731  the L's stroke
    hole = lambda u: (xw(u), yw(u), x1, y1)  # noqa: E731  what the colour does not cover yet
    base = t.solid(t.track("shape", "Cuadro"), colour, 0.0, dur, sq)
    base["name"] = "Cuadro"
    mask_track(t, base, sq, hole, dur, invert=True)
    side = sq.w * logo_share
    mark = t.photo(t.track("video", "Logo"), logo, 0.0, dur, centered(sq.cx, sq.cy, side, side), label="Tu logo",
                 brandRole="logo")
    mask_track(t, mark, centered(sq.cx, sq.cy, side, side), hole, dur, invert=True)
    rect_track(t, t.track("shape", "Esquina"), sq, lambda u: (xw(u), yw(u), xw(u) + thick(u), y1), dur, white,
               name="Esquina")
    rect_track(t, t.track("shape", "Esquina 2"), sq, lambda u: (xw(u), y1 - thick(u), x1, y1), dur, white,
               name="Esquina 2")


def francois():
    """A red line under the name's top grows into a block that slides down to become the role's bar, uncovering the
    name above it; the role shows inside the bar. The logo: a white corner fills a square, then the red square with
    the logo takes its place from the top left. The exit is the measured one (the bar climbs back over the name)."""
    r = Ref("francois")
    D = duration(r)
    t = _kit("francois", "Tercio con logo: nombre y barra roja", "Logo lower third: name over a red bar", D, 8530,
             ["nombre", "barra", "rojo"], thumb_at=2.5)
    photo_bg(t, "h-city-01", s1=1.03, label="Tu video")
    _logo_square(t, r, Box(306, 700, 147, 148), D)
    bar = Box(463, 700, 881, 248)
    top = edge(r, "bar", "warm", "min", before=700, after=700)
    bottom = edge(r, "bar", "warm", "max", before=700, after=700)
    name = "FRANCOIS BERG"
    nbox, nsize = caps_box(477, 707, 841, name)
    clip = name_text(t, name, nbox, nsize, D, bold_from="BERG", spacing=-5.4, bold_spacing=7, word_spacing=9)
    mask_track(t, clip, nbox, lambda u: (nbox.x, 600, nbox.x + nbox.w, top(u)), D)
    rect_track(t, t.track("shape", "Barra"), bar, lambda u: (bar.x, top(u), bar.x + bar.w, bottom(u)), D, RED,
               name="Barra")
    role = "MECHANICAL ENGINEER"
    rbox, rsize = caps_box(477, 870, 937, role)
    clip = name_text(t, role, rbox, rsize, D, name="Cargo", spacing=-2.4, word_spacing=6)
    mask_track(t, clip, rbox, lambda u: (bar.x, top(u), bar.x + bar.w, bottom(u)), D)
    return t


# Measured on the reference (blob of the square, 1080p): its side and its angle (degrees, the minimum-area rectangle)
# every frame from its first one; after the last value it stays.
_ROGER_SIDE = [2, 8, 17.7, 34, 64, 97, 119, 133, 146, 154, 160.5, 166, 171, 174, 177, 179, 181, 182.4, 183.5, 184.4,
               184.7, 185]
_ROGER_ANGLE = [-90, -90, -85.9, -81.9, -74.1, -66.4, -61.2, -57.7, -54.5, -51.6, -48.9, -45.4, -40.7, -33.6, -25.7,
                -19.9, -15.8, -12.6, -10.3, -8.4, -7.0, -5.8, -4.8, -4.0, -3.4, -2.8, -2.2, -2.0, -1.5, -1.3, -1.1,
                -0.8, -0.8, -0.8, -0.5, 0.0]


def roger():
    """A white dot grows into a square that turns a quarter and becomes the red square with the logo (the logo stays
    upright); white fills it from the top, then the white stretches left and drops into a box over the name's bar
    while the bar opens to the right and the wordmark slides in inside the box. They close back to the left."""
    r = Ref("roger", first=1)
    D = duration(r)
    t = _kit("roger", "Tercio con logo: cuadro que gira y caja con marca", "Logo lower third: spinning square and brand box",
             D, 8531, ["nombre", "barra", "rojo", "marca"], thumb_at=3.0)
    photo_bg(t, "h-city-01", s1=1.03, label="Tu video")
    fps = r.fps
    cx, cy, side = 607.0, 644.0, 185.0
    gone = (48 - r.first) / fps  # the square is all white by then: it leaves, the white box goes on
    sq = centered(cx, cy, side, side)
    motion = [(i / fps, {"s": v / side}, "linear") for i, v in enumerate(_ROGER_SIDE)]
    rot = keys([(i / fps, v, "linear") for i, v in enumerate(_ROGER_ANGLE)])
    red = t.solid(t.track("shape", "Cuadro"), RED, 0.0, gone, sq, motion, rotation=rot)
    red["name"] = "Cuadro"
    lg = centered(cx, cy - 2, 133, 133)
    t.photo(t.track("video", "Logo"), "logo-10", 0.0, gone, lg, motion, label="Tu logo", brandRole="logo")
    # The white the square is born as leaves into its own bottom-right corner (frames 5-8).
    cover = t.solid(t.track("shape", "Destello"), WHITE, 0.0, gone, sq, motion, rotation=rot)
    cover["name"] = "Destello"
    k = [(0.0, 1.0), (4 / fps, 1.0), (5 / fps, 0.82), (6 / fps, 0.5), (7 / fps, 0.18), (8 / fps, 0.0)]
    track = next(tr for tr in t.tracks if cover in tr.clips)
    t.mask(track, cover, "rectangle", x=0.5, y=0.5, w=1.0, h=1.0,
           keyframes={"x": keys([(u, 1 - v / 2, "linear") for u, v in k]),
                      "y": keys([(u, 1 - v / 2, "linear") for u, v in k]),
                      "w": keys([(u, v, "linear") for u, v in k]), "h": keys([(u, v, "linear") for u, v in k])})
    # The white box: from the square's top it fills down, then stretches left and drops (frames 36-75); it closes
    # into its right edge on the way out.
    after = (36 - r.first) / fps
    left = edge(r, "boxh", "white", "min", before=516, after=699)
    top = edge(r, "boxv", "white", "min", before=553, after=643)
    bottom = edge(r, "boxv", "white", "max", before=553, after=736)
    box = Box(306, 540, 400, 200)
    rect = lambda u: (left(u), top(u), 699, bottom(u)) if u >= after else (699, 553, 699, 553)  # noqa: E731
    # The white box's top and bottom come from the column the wordmark does not reach once it is in (its runs
    # there mix with the letters): past frame 75 they hold.
    rect_track(t, t.track("shape", "Caja"), box, rect, D, WHITE, name="Caja")
    # The wordmark slides in from the right inside the box (frames 53-75) and stays while the box closes over it.
    wm_box = Box(318, 657, 331, 70)
    def wm_dx(u):
        f = r.first + u * fps
        if f < 53:
            return 380.0
        if f > 99:
            return 0.0
        rs = runs_at(r, u, "wm", "warm")
        return (rs[0][0] - 318) if rs else 0.0
    from llt_motion import frames_of
    motion = [(u, {"dx": wm_dx(u)}, "linear") for u in frames_of(D)]
    wm = t.photo(t.track("video", "Marca"), "logo-13", 0.0, D, wm_box, motion, label="Tu logo con nombre",
                 brandRole="logo")
    track = next(tr for tr in t.tracks if wm in tr.clips)
    mk = {"x": [], "y": [], "w": [], "h": []}
    for u in frames_of(D):
        x0, y0, x1, y1 = rect(u)
        dx = wm_dx(u)
        mk["x"].append((u, ((x0 + x1) / 2 - wm_box.x - dx) / wm_box.w, "linear"))
        mk["y"].append((u, ((y0 + y1) / 2 - wm_box.y) / wm_box.h, "linear"))
        mk["w"].append((u, max(0.0, x1 - x0) / wm_box.w, "linear"))
        mk["h"].append((u, max(0.0, y1 - y0) / wm_box.h, "linear"))
    t.mask(track, wm, "rectangle", x=mk["x"][0][1], y=mk["y"][0][1], w=mk["w"][0][1], h=mk["h"][0][1],
           keyframes={k2: keys(v) for k2, v in mk.items()})
    # The bar opens to the right with the name in it, and closes back to the left.
    bar = Box(306, 737, 1142, 158)
    right = edge(r, "barh", "warm", "max", before=306, after=306)
    rect_track(t, t.track("shape", "Barra"), bar, lambda u: (306, 737, right(u), 895), D, RED, name="Barra")
    name = "ROGER FRANCKMAN"
    nbox, nsize = caps_box(328, 753, 880, name, weight=300)
    clip = name_text(t, name, nbox, nsize, D, bold_from="FRANCKMAN", weight=300, spacing=-6.9, bold_spacing=4.4,
                     word_spacing=5)
    mask_track(t, clip, nbox, lambda u: (306, 700, right(u), 900), D)
    return t


# --- Jamie: a prism of two faces --------------------------------------------------------------------------------------

_EYE = 2900.0  # the eye's distance that matches the reference (the top face's sliver at rest, the corner's bulge)


def _project(y, z):
    """Screen y of a world point (canvas px, z toward the viewer) seen by the app's 3D camera."""
    return 540 + (y - 540) * _EYE / (_EYE - z)


def _solve(fn, target, lo, hi):
    """The angle in [lo, hi] (degrees) where fn(angle) == target; fn monotonic there."""
    a, b = lo, hi
    fa = fn(a) - target
    for _ in range(60):
        m = (a + b) / 2
        fm = fn(m) - target
        if (fm > 0) == (fa > 0):
            a, fa = m, fm
        else:
            b = m
    return (a + b) / 2


def _height(clip):
    h = clip["height"]
    return h["keyframes"][0]["value"] if isinstance(h, dict) else float(h)


def jamie():
    """A red card with the brand stands up from its bottom edge; then the bar turns over like a prism, top going
    back, and the white face with the name comes round from below. Out, the prism turns back and the red card falls
    back from its top edge. Every angle is solved from the measured edges (lt_ref/jamie.json) with the eye at 2900."""
    r = Ref("jamie", first=3)
    fps = r.fps
    H, AY, X0, X1 = 157.0, 792.0, 326.0, 1387.0  # a face's height, the prism's axis (its centre), the bar's ends
    half = H / 2
    reds = [f["col"]["warm"] for f in r.frames]
    whites = [f["col"]["white"] for f in r.frames]

    def turn(phi):  # the prism turned by phi (0: red face front, 90: white face front): the edge between the faces
        c, s = math.cos(math.radians(phi)), math.sin(math.radians(phi))
        return _project(AY + half * (c - s), -half + half * (s + c))

    def stand(a):  # the red card tipped back by `a` about its bottom edge (870): its top edge
        return _project(870 - H * math.cos(math.radians(a)), -H * math.sin(math.radians(a)))

    def hang(b):  # the red card tipped back by `b` about its top edge (709): its bottom edge
        return _project(709 + H * math.cos(math.radians(b)), -H * math.sin(math.radians(b)))

    poses = []  # per frame from the first: (mode, angle)
    last = max(i for i in range(len(reds)) if reds[i] or whites[i])
    for i in range(r.first, last + 2):
        red = reds[i] if i < len(reds) else []
        white = whites[i] if i < len(whites) else []
        if i <= 20:
            poses.append(("up", _solve(stand, red[0][0] if red else 870, 0, 89.9)))
        elif i <= 35 or 101 <= i <= 112:
            if red and white:
                top_red = red[-1][1] if i <= 35 else white[-1][1]
                edge_y = (top_red + (white[0][0] if i <= 35 else red[0][0])) / 2
                poses.append(("prism", _solve(turn, edge_y, 0, 90)))
            else:
                poses.append(("prism", 90.0 if i > 30 else 0.0))
        elif i < 101:
            poses.append(("prism", 90.0))
        else:
            poses.append(("down", _solve(hang, red[-1][1] if red else 709, 0, 89.9)))
    frames = [k / fps for k in range(len(poses))]
    D = round(len(poses) / fps + 0.01, 2)
    t = _kit("jamie", "Tercio con logo: barra que gira como un prisma", "Logo lower third: bar turning like a prism",
             D, 8532, ["nombre", "3d", "prisma", "marca"], thumb_at=2.4)
    photo_bg(t, "h-city-01", s1=1.03, label="Tu video")

    def pose(which):
        """Per frame (centre y, depth, tilt) of face "a" (red) or "b" (white); the white face hides behind the
        camera while the card stands or falls (it is the prism's underside then)."""
        out = []
        for mode, ang in poses:
            c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
            if mode == "up":
                out.append((870 - half * c, -half * s, ang) if which == "a" else (AY + half, -half, -90.0))
            elif mode == "down":
                out.append((709 + half * c, -half * s, -ang) if which == "a" else (AY + half, -half, -90.0))
            elif which == "a":
                out.append((AY - half * s, -half + half * c, ang))
            else:
                out.append((AY + half * c, -half + half * s, ang - 90))
        return out

    def put(clip, which, dy=0.0):
        """A 3D pose every frame for a clip whose centre sits dy px below its face's centre, in the face's plane."""
        height = _height(clip)
        ys, zs, tilts = [], [], []
        for cy, cz, tilt in pose(which):
            a = math.radians(tilt)
            ys.append(cy + dy * math.cos(a) - height / 2)
            zs.append(cz + dy * math.sin(a))
            tilts.append(tilt)
        clip["layer3d"] = True
        clip["perspective"] = keys([(0, _EYE)])
        clip["y"] = keys([(u, v, "linear") for u, v in zip(frames, ys)])
        clip["positionZ"] = keys([(u, v, "linear") for u, v in zip(frames, zs)])
        clip["rotationX"] = keys([(u, v, "linear") for u, v in zip(frames, tilts)])
        if which == "b":  # the white face only exists while the prism turns (it is the card's underside otherwise)
            clip["opacity"] = keys([(u, 1.0 if mode == "prism" else 0.0, "hold") for u, (mode, _) in zip(frames, poses)])

    red = t.solid(t.track("shape", "Cara roja"), RED, 0.0, D, Box(X0, AY - half, X1 - X0, H))
    red["name"] = "Cara roja"
    put(red, "a")
    lg = t.photo(t.track("video", "Logo"), "logo-11", 0.0, D, centered(388, 795.5, 92, 92), label="Tu logo",
                 brandRole="logo")
    put(lg, "a", 795.5 - AY)
    brand = label(t, t.track("text", "Marca"), "flipstudio", 0.0, D, Box(440, 727, 900, 136), "Poppins", 140, WHITE,
                  weight=600, align="left", name="Marca", line=1.0)
    put(brand, "a", 795.0 - AY)
    white = t.solid(t.track("shape", "Cara blanca"), WHITE, 0.0, D, Box(X0, AY - half, X1 - X0, H))
    white["name"] = "Cara blanca"
    put(white, "b")
    name = "JAMIE SAUNDERS"
    nbox, nsize = caps_box(358, 726, 861, name, weight=400)
    clip = name_text(t, name, nbox, nsize, D, bold_from="SAUNDERS", weight=400, colour=RED, spacing=-5,
                     bold_spacing=5.3, word_spacing=3)
    put(clip, "b", nbox.cy - AY)
    return t


def charlotte():
    """A red line under the name's top grows into a block that slides down into the bar under it; the name is white
    above the block and cut out of it (the letters show the dark video through the red) while the block passes over
    it. The wordmark rises into the bar from its bottom edge. The exit is the entrance backwards, as measured."""
    r = Ref("charlotte")
    D = duration(r)
    t = _kit("charlotte", "Tercio con logo: nombre calado en la barra", "Logo lower third: name cut out of the bar", D,
             8533, ["nombre", "barra", "rojo", "calado", "marca"], thumb_at=2.6)
    photo_bg(t, "h-city-01", s1=1.03, label="Tu video")
    top = edge(r, "bar", "warm", "min", before=589, after=589)
    bottom = edge(r, "bar", "warm", "max", before=589, after=589)
    x0, x1 = 308, 1416
    bar = Box(x0, 560, x1 - x0, 340)
    rect_track(t, t.track("shape", "Barra"), bar, lambda u: (x0, top(u), x1, bottom(u)), D, RED, name="Barra")
    # One name over the bar: white above it, and over it in the dark of the video (the letters look cut out of the
    # red) — a colour overlay scoped to the block by its own mask, so the name stays a single text to edit.
    name = "CHARLOTTE EVANS"
    nbox, nsize = caps_box(320, 673, 811, name)
    clip = name_text(t, name, nbox, nsize, D, spacing=-2.0, word_spacing=9)
    mask_track(t, clip, nbox, lambda u: (x0, 500, x1, bottom(u)), D)
    effect_track(t, clip, nbox, lambda u: (x0, top(u), x1, bottom(u)), D,
                 [effect("layer.color_overlay", color="#262222", opacity=1.0)])
    fps = r.fps

    def rise(u):
        rs = runs_at(r, u, "wm", "white")
        tops = [a for a, b in rs if a > 815]
        f = r.first + u * fps
        if tops and (f <= 32 or f >= 100):
            return tops[0] - 835.0
        return 0.0 if 32 < f < 100 else 60.0
    from llt_motion import frames_of
    wm_box = Box(325, 827, 312, 66)
    motion = [(u, {"dy": rise(u)}, "linear") for u in frames_of(D)]
    wm = t.photo(t.track("video", "Marca"), "logo-12", 0.0, D, wm_box, motion, label="Tu logo con nombre",
                 brandRole="logo")
    track = next(tr for tr in t.tracks if wm in tr.clips)
    mk = {"x": [], "y": [], "w": [], "h": []}
    for u in frames_of(D):
        y0, y1, dy = top(u), bottom(u), rise(u)
        mk["x"].append((u, ((x0 + x1) / 2 - wm_box.x) / wm_box.w, "linear"))
        mk["y"].append((u, ((y0 + y1) / 2 - wm_box.y - dy) / wm_box.h, "linear"))
        mk["w"].append((u, (x1 - x0) / wm_box.w, "linear"))
        mk["h"].append((u, max(0.0, y1 - y0) / wm_box.h, "linear"))
    t.mask(track, wm, "rectangle", x=mk["x"][0][1], y=mk["y"][0][1], w=mk["w"][0][1], h=mk["h"][0][1],
           keyframes={k: keys(v) for k, v in mk.items()})
    return t


# Jason Etheridge, measured frame by frame (25 fps, from 26.2 s): the logo's centre (its bounding box) and its tilt
# (degrees, 0 at rest), the name's shift to its resting place, the underline's left end, and on the way out the
# edge rising from the underline that cuts the logo and the name from below.
_JE_LOGO = {4: (1554, 835, 0.55, -10.0), 5: (1550, 790, 0.95, -11.0), 6: (1552, 774, 1, -12.2),
            7: (1554, 763, 1, -17.5), 8: (1553, 758, 1, -20.2), 9: (1547, 756, 1, -21.4), 10: (1536, 756, 1, -20.8),
            11: (1520, 757, 1, -19.9), 12: (1499, 760, 1, -19.0), 13: (1471, 763, 1, -17.5), 14: (1437, 767, 1, -15.1),
            15: (1395, 772, 1, -12.2), 16: (1345, 778, 1, -8.8), 17: (1284, 784, 1, -4.8), 18: (1210, 790, 1, 3.3),
            19: (1126, 791, 1, 6.0), 20: (1029, 792, 1, 7.5), 21: (920, 794, 1, 8.0), 22: (807, 795, 1, 8.0),
            23: (717, 795, 1, 7.6), 24: (630, 796, 1, 7.2), 25: (554, 797, 1, 6.9), 26: (494, 798, 1, 6.6),
            27: (450, 796, 1, 4.6), 28: (418, 795, 1, 3.0), 29: (398, 793, 1, 2.0), 30: (387.5, 793, 1, 1.5),
            31: (385, 793, 1, 1.2), 32: (386, 792.5, 1, 0.7), 33: (386.3, 792, 1, 0.2), 35: (386.5, 791.5, 1, 0.0)}
_JE_NAME_DX = {18: -330.0, 20: -262.0, 22: -201.0, 24: -149.0, 26: -109.0, 28: -78.0, 30: -54.0, 32: -35.0, 34: -22.0,
               36: -12.0, 38: -6.0, 40: -1.0, 42: 0.0}
_JE_LINE_LEFT = {17: 1455.0, 19: 1356.0, 20: 1234.0, 21: 904.0, 22: 782.0, 23: 708.0, 25: 690.0, 26: 677.0, 27: 622.0,
                 28: 594.0, 29: 576.0, 30: 560.0, 33: 534.0, 40: 514.0}
_JE_CUT = {97: 896.0, 98: 876.0, 99: 855.0, 100: 832.0, 101: 803.0, 102: 773.0, 103: 752.0, 104: 737.0, 105: 726.0,
           106: 717.0, 107: 710.0, 108: 704.0, 109: 699.0, 110: 695.0, 111: 692.0}
_JE_LINE_Y = {96: 892.0, 97: 889.0, 98: 884.0, 99: 873.0, 100: 852.0, 101: 813.0}
_JE_RISE = {93: 0.0, 94: -1.4, 95: -3.4, 96: -6.4, 97: -11.0}


def _table(points, before, after):
    """u-frame -> value, linear between the measured frames; `before`/`after` outside them."""
    fs = sorted(points)

    def f(i):
        if i < fs[0]:
            return before
        if i >= fs[-1]:
            return points[fs[-1]] if after is None else after
        for a, b in zip(fs, fs[1:]):
            if i <= b:
                va, vb = points[a], points[b]
                k = (i - a) / (b - a)
                if isinstance(va, tuple):
                    return tuple(x + (y - x) * k for x, y in zip(va, vb))
                return va + (vb - va) * k
        return points[fs[-1]]
    return f


def jason_e():
    """The logo pops up at the right and rolls left along an arc, rocking; the name shows from behind its right edge,
    sliding right into place, and the underline runs left after it. Out, an edge rises from the underline and takes
    the name and the logo from the bottom up."""
    fps, first, last = 25.0, 4, 111
    D = round((last - first + 2) / fps, 2)
    t = _kit("jason-e", "Tercio con logo: logo que rueda y destapa el nombre", "Logo lower third: rolling logo reveals the name",
             D, 8534, ["nombre", "subrayado", "logo"], thumb_at=2.4)
    photo_bg(t, "h-city-01", s1=1.03, label="Tu video")
    from llt_motion import frames_of
    us = frames_of(D)
    fr = lambda u: first + u * fps  # noqa: E731
    logo = _table(_JE_LOGO, (1554, 835, 0.0, -10.0), None)
    rise = _table(_JE_RISE, 0.0, -11.0)
    cut = _table(_JE_CUT, 2000.0, 692.0)
    name_dx = _table(_JE_NAME_DX, -400.0, 0.0)
    line_left = _table(_JE_LINE_LEFT, 1456.0, 514.0)
    line_y = _table(_JE_LINE_Y, 892.0, 813.0)
    # The underline (4 px), and its rise on the way out; gone once it has climbed.
    bar = Box(514, 600, 942, 300)
    rect_track(t, t.track("shape", "Línea"), bar,
               lambda u: (line_left(fr(u)), line_y(fr(u)), 1456, line_y(fr(u)) + 4) if 17 <= fr(u) <= 101
               else (1456, 892, 1456, 892), D, RED, name="Línea")
    # The name, shifted into place and shown right of the logo's right edge, above the rising edge.
    name = "JASON ETHERIDGE"
    nbox, nsize = caps_box(536, 735, 859, name, weight=300)
    motion = [(u, {"dx": name_dx(fr(u))}, "linear") for u in us]
    clip = name_text(t, name, nbox, nsize, D, weight=300, spacing=-3.9, word_spacing=6, motion=motion)
    track = next(tr for tr in t.tracks if clip in tr.clips)
    mk = {"x": [], "y": [], "w": [], "h": []}
    for u in us:
        f = fr(u)
        left = logo(f)[0] + 79 if f <= 34 else 0.0
        x0, y0, x1, y1 = left, 600, 1500, min(892.0, cut(f))
        dx = name_dx(f)
        mk["x"].append((u, ((x0 + x1) / 2 - nbox.x - dx) / nbox.w, "linear"))
        mk["y"].append((u, ((y0 + y1) / 2 - nbox.y) / nbox.h, "linear"))
        mk["w"].append((u, max(0.0, x1 - x0) / nbox.w, "linear"))
        mk["h"].append((u, max(0.0, y1 - y0) / nbox.h, "linear"))
    t.mask(track, clip, "rectangle", x=mk["x"][0][1], y=mk["y"][0][1], w=mk["w"][0][1], h=mk["h"][0][1],
           keyframes={k: keys(v) for k, v in mk.items()})
    # The logo: its slot sized like the reference's (157 × 175), moved, scaled and turned every frame.
    side = 180.0
    lg = centered(386.5, 791.5, side, side)
    motion, rot = [], []
    for u in us:
        cx, cy, s, a = logo(fr(u))
        motion.append((u, {"s": s, "dx": cx - lg.cx, "dy": cy - lg.cy + rise(fr(u))}, "linear"))
        rot.append((u, a, "linear"))
    mark = t.photo(t.track("video", "Logo"), "logo-09", 0.0, D, lg, motion, label="Tu logo", brandRole="logo",
                   rotation=keys(rot))
    track = next(tr for tr in t.tracks if mark in tr.clips)
    mk = {"x": [], "y": [], "w": [], "h": []}
    for u in us:  # the rising edge, in the logo's own box (it only moves up a little by then, and does not turn)
        f = fr(u)
        cx, cy, s, a = logo(f)
        top = cy + rise(f) - side / 2
        y1 = min(cut(f), top + side + 40)
        mk["x"].append((u, 0.5, "linear"))
        mk["y"].append((u, ((top - 40 + y1) / 2 - top) / side, "linear"))
        mk["w"].append((u, 2.0, "linear"))
        mk["h"].append((u, max(0.0, y1 - (top - 40)) / side, "linear"))
    t.mask(track, mark, "rectangle", x=0.5, y=mk["y"][0][1], w=2.0, h=mk["h"][0][1],
           keyframes={k: keys(v) for k, v in mk.items()})
    return t


# Jessica Branson, measured frame by frame (25 fps from 30.8 s). The logo shows through a slanted slot whose edges
# (on row 862) run right and back; the name slides out from behind the slot's right edge, overshoots and settles;
# the role rises from behind a line; out, the slot closes to the right and a gentler slanted edge sweeps the texts.
_JB_SLOPE, _JB_SLOPE_OUT = 0.65, 0.17  # the edges' lean: px right per px up
_JB_L = {3: 359.0, 4: 372.0, 5: 406.0, 6: 434.0, 7: 455.0, 8: 471.0, 9: 483.0, 10: 492.0, 11: 500.0, 12: 505.0,
         13: 509.0, 14: 512.0, 15: 513.0, 16: 513.0, 17: 512.0, 18: 510.0, 19: 506.0, 20: 500.0, 21: 493.0, 22: 484.0,
         23: 471.0, 24: 454.0, 25: 432.0, 26: 400.0, 27: 360.0, 28: 300.0, 97: 300.0, 98: 382.0, 99: 418.0,
         100: 466.0, 101: 529.0, 102: 600.0}
_JB_R = {3: 379.0, 4: 422.0, 5: 464.0, 6: 500.0, 7: 529.0, 8: 543.0, 10: 535.0, 13: 495.0}
_JB_NAME_DX = {4: -900.0, 5: -658.0, 6: -381.0, 7: -92.0, 8: 54.0, 9: 141.0, 10: 199.0, 11: 205.0, 12: 210.0,
               14: 216.0, 16: 218.0, 18: 215.0, 20: 208.0, 22: 199.0, 23: 190.0, 24: 164.0, 25: 121.0, 26: 93.0,
               27: 73.0, 28: 58.0, 29: 46.0, 30: 36.0, 31: 28.0, 32: 22.0, 33: 17.0, 34: 13.0, 40: 3.0, 45: 0.0}
_JB_ROLE_DY = {20: 100.0, 21: 89.0, 22: 81.0, 23: 68.0, 24: 50.0, 25: 38.0, 26: 29.0, 27: 23.0, 28: 18.0, 29: 14.0,
               30: 11.0, 31: 9.0, 32: 7.0, 33: 5.0, 34: 4.0, 38: 1.0, 42: 0.0}
_JB_OUT = {98: 590.0, 99: 691.0, 100: 716.0, 101: 742.0, 102: 820.0, 103: 923.0, 104: 1059.0, 105: 1194.0,
           106: 1330.0, 107: 1500.0}  # the texts' sweeping edge on row 767


def _slant_mask(t, clip, box, frames, edges, slope, row, dur, dx=None, op=None):
    """A mask on `clip` (laid out in `box`; moved by dx(u) px) showing what lies between two lines leaning `slope`
    px right per px up: edges(u) = (left, right) where they cross screen row `row`. A rectangle turned by the lean."""
    lean = math.degrees(math.atan(slope))
    c = math.cos(math.radians(lean))
    mk = {"x": [], "y": [], "w": [], "h": []}
    for u in frames:
        left, right = edges(u)
        shift = dx(u) if dx else 0.0
        width = max(0.0, right - left) * c
        mk["x"].append((u, ((left + right) / 2 - box.x - shift) / box.w, "linear"))
        mk["y"].append((u, (row - box.y) / box.h, "linear"))
        mk["w"].append((u, width / box.w, "linear"))
        mk["h"].append((u, 4000.0 / box.h, "linear"))
    track = next(tr for tr in t.tracks if clip in tr.clips)
    extra = {"op": op} if op else {}
    t.mask(track, clip, "rectangle", x=mk["x"][0][1], y=mk["y"][0][1], w=mk["w"][0][1], h=mk["h"][0][1],
           rotation=lean, keyframes={k: keys(v) for k, v in mk.items()}, **extra)


def jessica():
    """The logo slides into view through a slanted slot that narrows to a sliver and then opens on the whole logo;
    the name slides out from behind the slot's edge, overshoots and settles; the role rises under it. Out, the slot
    closes and a slanted edge sweeps the name and the role away to the right."""
    fps, first, last = 25.0, 3, 106
    D = round((last - first + 2) / fps, 2)
    t = _kit("jessica", "Tercio con logo: ranura inclinada", "Logo lower third: slanted slot", D, 8535,
             ["nombre", "cargo", "logo", "diagonal"], thumb_at=2.6)
    photo_bg(t, "h-city-01", s1=1.03, label="Tu video")
    from llt_motion import frames_of
    us = frames_of(D)
    fr = lambda u: first + u * fps  # noqa: E731
    L = _table(_JB_L, 600.0, 600.0)
    R = _table(_JB_R, 359.0, 495.0)
    out = _table(_JB_OUT, 590.0, 1500.0)
    name_dx = _table(_JB_NAME_DX, -900.0, 0.0)
    role_dy = _table(_JB_ROLE_DY, 100.0, 0.0)
    lg = centered(448.5, 808.0, 225.0, 225.0)
    mark = t.photo(t.track("video", "Logo"), "logo-09", 0.0, D, lg, label="Tu logo", brandRole="logo")
    _slant_mask(t, mark, lg, us, lambda u: (L(fr(u)), max(R(fr(u)), 600.0) if fr(u) > 8 else R(fr(u))), _JB_SLOPE,
                862.0, D)
    # The texts show right of the slot's right edge (lean 0.65) on the way in and of the sweeping edge (lean 0.17)
    # on the way out: one slanted window each, its left edge the one that matters.
    name = "JESSICA BRANSON"
    nbox, nsize = caps_box(599, 705, 802, name)
    motion = [(u, {"dx": name_dx(fr(u))}, "linear") for u in us]
    clip = name_text(t, name, nbox, nsize, D, bold_from="BRANSON", spacing=-4.0, bold_spacing=3, word_spacing=6,
                     motion=motion)

    # Two slanted masks, both the whole time: right of the slot's edge (steep) and right of the sweeping edge
    # (gentle, still until frame 98) — what shows is right of both.
    _slant_mask(t, clip, nbox, us, lambda u: (R(fr(u)) + _JB_SLOPE * (862.0 - 753.0), 3000.0), _JB_SLOPE, 753.0, D,
                dx=lambda u: name_dx(fr(u)))
    _slant_mask(t, clip, nbox, us, lambda u: (out(fr(u)), 3000.0), _JB_SLOPE_OUT, 767.0, D,
                dx=lambda u: name_dx(fr(u)), op="intersect")
    role = "DIRECTOR"
    rbox, rsize = caps_box(581, 830, 897, role)
    motion = [(u, {"dy": role_dy(fr(u))}, "linear") for u in us]
    rclip = name_text(t, role, rbox, rsize, D, bold_from="DIRECTOR", name="Cargo", spacing=-1.0, bold_spacing=3.3,
                      motion=motion)
    track = next(tr for tr in t.tracks if rclip in tr.clips)
    mk = {"x": [], "y": [], "w": [], "h": []}
    for u in us:
        f, dy = fr(u), role_dy(fr(u))
        x0 = out(f) - _JB_SLOPE_OUT * (890 - 767) if f >= 90 else 0.0
        y0, y1 = 600.0, 920.0
        mk["x"].append((u, ((x0 + 3000) / 2 - rbox.x) / rbox.w, "linear"))
        mk["y"].append((u, ((y0 + y1) / 2 - rbox.y - dy) / rbox.h, "linear"))
        mk["w"].append((u, (3000 - x0) / rbox.w, "linear"))
        mk["h"].append((u, (y1 - y0) / rbox.h, "linear"))
    t.mask(track, rclip, "rectangle", x=mk["x"][0][1], y=mk["y"][0][1], w=mk["w"][0][1], h=mk["h"][0][1],
           keyframes={k: keys(v) for k, v in mk.items()})
    return t


# David Bergman, measured frame by frame (25 fps from 35.12 s): the ring's centre x and outer diameter (its top
# edge stays on row 711 the whole time), and on the way out its diameter and the name's slide into it.
_DB_CX = {1: 871.0, 2: 911.0, 3: 968.5, 4: 1044.0, 5: 1131.0, 6: 1222.5, 7: 1307.0, 8: 1375.5, 9: 1428.5, 10: 1460.5,
          11: 1468.5, 12: 1444.5, 13: 1376.0, 14: 1228.5, 15: 984.0, 16: 796.5, 17: 681.0, 18: 604.0, 19: 549.5,
          20: 509.5, 21: 479.5, 22: 456.5, 23: 440.0, 24: 428.5, 25: 421.0, 26: 417.0, 27: 415.5}
_DB_D = {1: 20.0, 2: 40.0, 3: 69.0, 4: 104.0, 5: 148.0, 6: 193.0, 7: 234.0, 8: 268.0, 9: 293.0, 10: 311.0, 11: 321.0,
         12: 325.0, 13: 318.0, 14: 303.0, 15: 278.0, 16: 257.0, 17: 244.0, 18: 236.0, 19: 231.0, 20: 227.0, 21: 223.0,
         22: 221.0, 23: 218.0, 24: 217.0, 25: 216.0, 27: 215.0, 100: 215.0, 101: 213.0, 102: 212.0, 103: 209.0,
         104: 206.0, 105: 204.0, 106: 200.0, 107: 196.0, 108: 190.0, 109: 182.0, 110: 174.0, 111: 163.0, 112: 149.0,
         113: 127.0, 114: 95.0, 115: 56.0, 116: 30.0, 117: 15.0, 118: 0.0}
_DB_NAME_DX = {97: 0.0, 98: -9.0, 99: -23.0, 100: -45.0, 101: -80.0, 102: -135.0, 103: -226.0, 104: -383.0,
               105: -602.0, 106: -800.0, 107: -1000.0}


def david():
    """A small red ring with the logo grows at the top of the name's place and rolls right, then rolls back left,
    shrinking, and the name shows from behind its right edge as it passes. Out, the name slides left into the ring
    and the ring shrinks to nothing."""
    fps, first, last = 25.0, 1, 117
    D = round((last - first + 2) / fps, 2)
    t = _kit("david", "Tercio con logo: anillo que rueda", "Logo lower third: rolling ring", D, 8536,
             ["nombre", "anillo", "logo", "círculo"], thumb_at=2.4)
    photo_bg(t, "h-city-01", s1=1.03, label="Tu video")
    from llt_motion import frames_of
    us = frames_of(D)
    fr = lambda u: first + u * fps  # noqa: E731
    cx = _table(_DB_CX, 871.0, 415.5)
    dia = _table(_DB_D, 0.0, 0.0)
    name_dx = _table(_DB_NAME_DX, 0.0, -1000.0)
    REST, TOP = 215.0, 711.0
    # Rolling: the ring turns by the way it travels over its radius (clockwise going right); at rest the logo is
    # upright, so the turn is counted back from the end.
    spin, total = [], 0.0
    prev = None
    for u in us:
        f = fr(u)
        x, d = cx(f), max(dia(f), 1.0)
        if prev is not None:
            total += math.degrees((x - prev) / (d / 2))
        spin.append(total)
        prev = x
    spin = [a - spin[-1] for a in spin]
    ring = centered(415.5, TOP + REST / 2, REST, REST)
    motion = [(u, {"s": dia(fr(u)) / REST, "dx": cx(fr(u)) - ring.cx, "dy": dia(fr(u)) / 2 - REST / 2}, "linear")
              for u in us]
    disc = t.solid(t.track("shape", "Anillo"), RED, 0.0, D, ring, motion, kind="ellipse")
    disc["name"] = "Anillo"
    track = next(tr for tr in t.tracks if disc in tr.clips)
    t.mask(track, disc, "ellipse", x=0.5, y=0.5, w=0.56, h=0.56, invert=True)  # the hole: it scales with the ring
    lg = centered(415.5, TOP + REST / 2, 108.0, 108.0)
    mark = t.photo(t.track("video", "Logo"), "logo-09", 0.0, D, lg, motion, label="Tu logo", brandRole="logo",
                   rotation=keys([(u, a, "linear") for u, a in zip(us, spin)]))
    mark["name"] = "Logo"
    name = "DAVID BERGMAN"
    nbox, nsize = caps_box(562, 764, 879, name)
    motion = [(u, {"dx": name_dx(fr(u))}, "linear") for u in us]
    clip = name_text(t, name, nbox, nsize, D, bold_from="BERGMAN", spacing=-5.0, bold_spacing=4, word_spacing=6,
                     motion=motion)
    track = next(tr for tr in t.tracks if clip in tr.clips)
    mk = {"x": [], "y": [], "w": [], "h": []}
    for u in us:  # the name shows right of the ring's right edge (less 15 px)
        f = fr(u)
        left = cx(f) + dia(f) / 2 - 15 if dia(f) > 0 and f >= 12 else 3000.0  # hidden until the ring comes back
        dx = name_dx(f)
        mk["x"].append((u, ((left + 3000) / 2 - nbox.x - dx) / nbox.w, "linear"))
        mk["y"].append((u, 0.5, "linear"))
        mk["w"].append((u, max(0.0, 3000 - left) / nbox.w, "linear"))
        mk["h"].append((u, 2.0, "linear"))
    t.mask(track, clip, "rectangle", x=mk["x"][0][1], y=0.5, w=mk["w"][0][1], h=2.0,
           keyframes={k: keys(v) for k, v in mk.items()})
    return t


# Neil Simpson, measured frame by frame (25 fps from 39.9 s). In: a red card opens from a line (its box per frame),
# the cube turns about Y bringing the white face with the logo round from the right (red left, the edge, white
# right), then slides left; the name slides right from behind it. Out: the name slides back behind it, the cube
# tips forward about X (the red top comes to the front) and the red card folds down onto its bottom edge.
_NS_CARD = {2: (1088, 732, 1093, 880), 3: (1074, 731, 1093, 881), 4: (1040, 727, 1093, 884), 5: (988, 722, 1094, 890),
            6: (960, 720, 1093, 892), 7: (944, 718, 1093, 894), 8: (932, 716, 1092, 895), 9: (920, 716, 1088, 896),
            10: (906, 715, 1080, 898)}
_NS_TURN = {11: (886, 1054, 1108), 12: (871, 997, 1120), 13: (873, 958, 1114), 14: (877, 935, 1105),
            15: (880, 919, 1095), 16: (880, 906, 1085), 17: (880, 895, 1076), 18: (876, 884, 1066)}
_NS_LEFT = {19: 874, 20: 862, 21: 850, 22: 837, 23: 822, 24: 804, 25: 783, 26: 756, 27: 722, 28: 677, 29: 614,
            30: 530, 31: 451, 32: 400, 33: 369, 34: 349, 35: 336, 36: 327, 37: 322, 38: 319, 39: 318}
_NS_NAME_R = {25: 942.0, 26: 987.0, 27: 1035.0, 28: 1075.0, 29: 1109.0, 30: 1139.0, 31: 1164.0, 32: 1187.0,
              33: 1207.0, 34: 1226.0, 35: 1243.0, 36: 1257.0, 37: 1271.0, 38: 1283.0, 39: 1295.0, 40: 1305.0,
              42: 1323.0, 44: 1338.0, 46: 1351.0, 48: 1361.0, 50: 1371.0, 52: 1378.0, 54: 1383.0, 56: 1388.0,
              58: 1392.0, 60: 1395.0, 63: 1397.0, 98: 1397.0, 99: 1207.0, 100: 1167.0, 101: 1119.0, 102: 1059.0,
              103: 983.0, 104: 885.0, 105: 748.0, 106: 556.0, 107: 400.0}
_NS_TIP = {100: 716.0, 101: 720.0, 102: 728.0, 103: 754.0, 104: 810.0, 105: 847.0, 106: 865.0, 107: 877.0,
           108: 884.0, 109: 890.0}  # the white face's top: the edge the cube tips over
_NS_FOLD = {113: 715, 114: 721, 115: 734, 116: 768, 117: 820, 118: 848, 119: 864, 120: 876, 121: 883, 122: 888,
            123: 896}


def neil():
    """A red card opens from a line into a cube that turns, showing its white face with the logo; it slides left
    and the name slides out from behind it. Out, the name slides back in, the cube tips forward to its red top and
    the card folds down. Every pose is solved from the measured edges with the eye at 2900 px."""
    fps, first, last = 25.0, 2, 123
    D = round((last - first + 1) / fps, 2)
    t = _kit("neil", "Tercio con logo: cubo que gira", "Logo lower third: turning cube", D, 8537,
             ["nombre", "3d", "cubo", "logo"], thumb_at=2.6)
    photo_bg(t, "h-city-01", s1=1.03, label="Tu video")
    from llt_motion import frames_of
    us = frames_of(D)
    fr = lambda u: first + u * fps  # noqa: E731
    h, AY = 90.5, 805.5

    def px(x, z):
        return 960 + (x - 960) * _EYE / (_EYE - z)

    def py_(y, z):
        return 540 + (y - 540) * _EYE / (_EYE - z)

    # Per frame: the cube's centre x and its turn about Y (phi: 0 red front, 90 white front) and about X (theta: 0
    # white front, 90 red top at the front).
    poses = {}
    for f, (L, E, R) in _NS_TURN.items():
        best = None
        for k in range(0, 901):
            phi = k / 10
            c, s = math.cos(math.radians(phi)), math.sin(math.radians(phi))
            ez = -h + h * (s + c)
            kk = _EYE / (_EYE - ez)
            cx = (E - 960) / kk + 960 - h * (c - s)
            err = (px(cx + h * (c + s), -h + h * (s - c)) - R) ** 2 + (px(cx - h * (c + s), -h + h * (c - s)) - L) ** 2
            if best is None or err < best[0]:
                best = (err, cx, phi)
        poses[f] = (best[1], best[2], 0.0)
    for f, left in _NS_LEFT.items():
        poses[f] = (left + h, 90.0, 0.0)
    for f in range(40, 100):
        poses[f] = (318 + h, 90.0, 0.0)
    for f, top in _NS_TIP.items():
        def edge_y(th):
            c, s = math.cos(math.radians(th)), math.sin(math.radians(th))
            return py_(AY + h * (s - c), -h + h * (s + c))
        poses[f] = (318 + h, 90.0, _solve(edge_y, top, 0, 90))
    for f in range(110, 113):
        poses[f] = (318 + h, 90.0, 90.0)
    p = lambda u: poses.get(int(round(fr(u))), None)  # noqa: E731

    def place(clip, which):
        """3D keys for a face ("red" or "white") of the cube, or hidden off its frames."""
        xs, ys, zs, rx, ry, op = [], [], [], [], [], []
        w = _height(clip)
        for u in us:
            pose = p(u)
            if pose is None:
                xs.append(318.0); ys.append(AY - w / 2); zs.append(0.0); rx.append(0.0); ry.append(0.0); op.append(0.0)
                continue
            cx, phi, th = pose
            c, s = math.cos(math.radians(phi)), math.sin(math.radians(phi))
            ct, st = math.cos(math.radians(th)), math.sin(math.radians(th))
            if th > 0:  # tipping about X; the red face is now the top one
                if which == "white":
                    fx, fy, fz, ax, ay = cx, AY + h * st, -h + h * ct, -th, 0.0
                else:
                    fx, fy, fz, ax, ay = cx, AY - h * ct, -h + h * st, 90.0 - th, 0.0
            else:  # turning about Y; the red face is the left/front one
                if which == "white":
                    fx, fy, fz, ax, ay = cx + h * c, AY, -h + h * s, 0.0, 90.0 - phi
                else:
                    fx, fy, fz, ax, ay = cx - h * s, AY, -h + h * c, 0.0, -phi
            edge_on = (which == "red" and th == 0 and phi >= 89.5) or (which != "red" and th == 0 and phi <= 0.5)
            xs.append(fx - w / 2); ys.append(fy - w / 2); zs.append(fz); rx.append(ax); ry.append(ay)
            op.append(0.0 if edge_on else 1.0)
        clip["layer3d"] = True
        clip["perspective"] = keys([(0, _EYE)])
        clip["x"] = keys([(u, v, "linear") for u, v in zip(us, xs)])
        clip["y"] = keys([(u, v, "linear") for u, v in zip(us, ys)])
        clip["positionZ"] = keys([(u, v, "linear") for u, v in zip(us, zs)])
        clip["rotationX"] = keys([(u, v, "linear") for u, v in zip(us, rx)])
        clip["rotationY"] = keys([(u, v, "linear") for u, v in zip(us, ry)])
        clip["opacity"] = keys([(u, v, "hold") for u, v in zip(us, op)])

    face = Box(318, AY - h, 2 * h, 2 * h)
    red = t.solid(t.track("shape", "Cara roja"), RED, 0.0, D, face)
    red["name"] = "Cara roja"
    place(red, "red")
    white = t.solid(t.track("shape", "Cara blanca"), WHITE, 0.0, D, face)
    white["name"] = "Cara blanca"
    place(white, "white")
    mark = t.photo(t.track("video", "Logo"), "logo-09", 0.0, D, centered(318 + h, AY, 166, 166), label="Tu logo",
                   brandRole="logo")
    mark["width"], mark["height"] = keys([(0, 166.0)]), keys([(0, 166.0)])
    place(mark, "white")
    # The flat card before the cube turns, and after it tips: measured boxes.
    card = _table({f: v for f, v in _NS_CARD.items()}, (1090, 806, 1090, 806), (906, 715, 1080, 898))
    fold = _table(_NS_FOLD, 715.0, 896.0)

    def card_rect(u):
        f = fr(u)
        if f <= 10.5:
            x0, y0, x1, y1 = card(f)
            return x0, y0, x1, y1
        if f >= 112.5:
            return 318, fold(f), 318 + 2 * h, 896
        return 0, 0, 0, 0
    rect_track(t, t.track("shape", "Tarjeta"), Box(300, 600, 1300, 320), card_rect, D, RED, name="Tarjeta")
    # The name, red, slid right into place from behind the cube's right edge (and back in).
    name_r = _table(_NS_NAME_R, 900.0, 400.0)
    name = "NEIL SIMPSON"
    nbox, nsize = caps_box(554, 719, 867, name, weight=300)
    motion = [(u, {"dx": name_r(fr(u)) - 1397}, "linear") for u in us]
    clip = name_text(t, name, nbox, nsize, D, bold_from="SIMPSON", weight=300, colour=RED, spacing=-4.0,
                     bold_spacing=3, word_spacing=6, motion=motion)
    track = next(tr for tr in t.tracks if clip in tr.clips)
    mk = {"x": [], "w": []}
    for u in us:
        f = fr(u)
        pose = p(u)
        right = 3000.0 if pose is None else (pose[0] + h if pose[1] >= 89 else 3000.0)
        if f < 24:
            right = 3000.0
        dx = name_r(f) - 1397
        mk["x"].append((u, ((right + 3200) / 2 - nbox.x - dx) / nbox.w, "linear"))
        mk["w"].append((u, max(0.0, 3200 - right) / nbox.w, "linear"))
    t.mask(track, clip, "rectangle", x=mk["x"][0][1], y=0.5, w=mk["w"][0][1], h=2.0,
           keyframes={k: keys(v) for k, v in mk.items()})
    return t


def joanna():
    """A white bar opens to the left from its right end, uncovering the red name; a red tab with a slanted edge grows
    out of the bar's left end with the logo in it. The exit is the entrance backwards, as measured."""
    r = Ref("joanna", first=4)
    D = duration(r)
    t = _kit("joanna", "Tercio con logo: barra blanca y pestaña inclinada", "Logo lower third: white bar, slanted tab", D,
             8538, ["nombre", "barra", "blanco", "logo"], thumb_at=2.4)
    photo_bg(t, "h-city-01", s1=1.03, label="Tu video")
    from llt_motion import frames_of
    us = frames_of(D)
    X1, Y0, Y1 = 1459.0, 712.0, 870.0
    L = r.curve(lambda f: min([a for a, b in f["w"]["white"] + f["w"]["warm"]], default=None), before=X1, after=X1)
    tip = r.curve(Ref.edge("r2", "warm"), before=300.0, after=300.0, offset=1)  # the slanted edge on row 864
    has_tab = lambda u: bool(runs_at(r, u, "r1", "warm"))  # noqa: E731
    bar = Box(300, Y0, X1 - 300, Y1 - Y0)
    rect_track(t, t.track("shape", "Barra"), bar, lambda u: (L(u), Y0, X1, Y1), D, WHITE, name="Barra")
    name = "JOANNA FILBURN"
    nbox, nsize = caps_box(540, 723, 849, name)
    clip = name_text(t, name, nbox, nsize, D, bold_from=name, colour=RED, bold_spacing=0.2, word_spacing=4)
    mask_track(t, clip, nbox, lambda u: (L(u), 600, X1, 950), D)
    # The tab: red from the bar's left end to a line leaning 0.32 px right per px up, through tip(u) on row 864.
    slope = 0.322
    tab_box = Box(300, Y0, 260, Y1 - Y0)
    edges = lambda u: ((L(u), tip(u)) if has_tab(u) else (L(u), L(u)))  # noqa: E731
    tab = t.solid(t.track("shape", "Pestaña"), RED, 0.0, D, tab_box)
    tab["name"] = "Pestaña"
    mask_track(t, tab, tab_box, lambda u: (edges(u)[0], Y0, 3000, Y1), D)
    _slant_mask(t, tab, tab_box, us, lambda u: (-3000.0, edges(u)[1]), slope, 864.0, D, op="intersect")
    lg = centered(388.5, 789.5, 140, 140)
    mark = t.photo(t.track("video", "Logo"), "logo-11", 0.0, D, lg, label="Tu logo", brandRole="logo")
    mask_track(t, mark, lg, lambda u: (edges(u)[0], Y0, 3000, Y1), D)
    _slant_mask(t, mark, lg, us, lambda u: (-3000.0, edges(u)[1]), slope, 864.0, D, op="intersect")
    return t


# Hendrick Cluson, measured frame by frame (25 fps from 50.05 s): the red square opens down from its top edge over
# the logo (its bottom per frame), then tumbles away and lands as a thin upright line right of the logo (its centre,
# long side, thickness and the long side's angle per frame), which opens to the right into the name's bar. The exit
# is the entrance backwards (frame f out = frame 154 - f in).
_HC_DROP = {3: 727, 4: 748, 5: 800, 6: 835, 7: 853, 8: 864, 9: 872, 10: 877, 11: 881, 12: 883, 14: 884}
_HC_TUMBLE = {15: (380.2, 805.1, 165.8, 164.1, -1.9), 16: (371.2, 819.3, 166.4, 160.4, -9.3),
              17: (357.9, 858.9, 166.6, 149.5, -28.1), 18: (391.2, 954.7, 166.8, 119.1, -78.4),
              19: (527.0, 953.8, 165.5, 73.2, -155.5), 20: (554.0, 884.4, 166.2, 48.2, -196.5),
              21: (540.7, 843.2, 166.1, 33.6, -220.8), 22: (522.3, 821.4, 166.1, 23.7, -236.9),
              23: (505.4, 810.8, 165.5, 17.3, -248.2), 24: (492.3, 805.8, 164.9, 11.9, -256.2),
              25: (482.6, 803.5, 164.9, 8.4, -261.8), 26: (476.0, 802.5, 163.7, 5.9, -265.6),
              27: (471.6, 802.0, 162.1, 4.3, -268.2), 28: (469.5, 802.0, 162.0, 3.0, -270.0)}
_HC_BAR = {29: 470, 30: 472, 31: 480, 32: 498, 33: 528, 34: 579, 35: 670, 36: 836, 37: 1020, 38: 1144, 39: 1226,
           40: 1288, 41: 1334, 42: 1370, 43: 1400, 44: 1424, 45: 1444, 46: 1460, 47: 1472, 48: 1483, 49: 1492,
           50: 1497, 51: 1502, 52: 1505, 53: 1507, 54: 1508}


def hendrick():
    """A red square opens down over the logo, tumbles off it and lands upright as a thin line, which opens to the
    right into a bar with the name. Out, all of it backwards."""
    fps, first, last = 25.0, 3, 151
    D = round((last - first + 1) / fps, 2)
    t = _kit("hendrick", "Tercio con logo: cuadro que cae y abre la barra", "Logo lower third: tumbling square opens the bar",
             D, 8539, ["nombre", "barra", "rojo", "logo"], thumb_at=2.6)
    photo_bg(t, "h-city-01", s1=1.03, label="Tu video")
    from llt_motion import frames_of
    us = frames_of(D)
    fin = lambda u: (lambda i: i if i <= 77 else 154 - i)(first + u * fps)  # noqa: E731  the entrance's frame
    drop = _table(_HC_DROP, 720.0, 884.0)
    tumble = _table(_HC_TUMBLE, (382.5, 802.0, 165.0, 165.0, 0.0), (469.5, 802.0, 162.0, 3.0, -270.0))
    bar_r = _table(_HC_BAR, 469.0, 1508.0)
    # The square: opening down (to frame 14), tumbling (15-28), gone once it is the bar's line (29 on).
    sq = Box(300, 720, 165, 165)
    motion, rot = [], []
    for u in us:
        f = fin(u)
        if f <= 14.5:
            b = drop(f)
            motion.append((u, {"sx": 1.0, "sy": (b - 720 + 1) / 165, "dy": (720 + b + 1) / 2 - sq.cy}, "linear"))
            rot.append((u, 0.0, "linear"))
        elif f <= 28.99:
            cx, cy, long, thick, a = tumble(f)
            motion.append((u, {"sx": long / 165, "sy": thick / 165, "dx": cx - sq.cx, "dy": cy - sq.cy}, "linear"))
            rot.append((u, a, "linear"))
        else:
            motion.append((u, {"sx": 0.0, "sy": 0.0, "dx": 469.5 - sq.cx, "dy": 802 - sq.cy}, "linear"))
            rot.append((u, -270.0, "linear"))
    cube = t.solid(t.track("shape", "Cuadro"), RED, 0.0, D, sq, motion, rotation=keys(rot))
    cube["name"] = "Cuadro"
    # The logo: inside the square while it opens, then on its own.
    lg = centered(379.5, 802.0, 150, 150)
    mark = t.photo(t.track("video", "Logo"), "logo-11", 0.0, D, lg, label="Tu logo", brandRole="logo")
    mask_track(t, mark, lg, lambda u: (200, 600, 600, drop(fin(u)) + 1 if fin(u) <= 14.5 else 1000), D)
    bar = Box(468, 720, 1040, 165)
    rect_track(t, t.track("shape", "Barra"), bar,
               lambda u: (468, 720, bar_r(fin(u)), 885) if fin(u) > 28.99 else (468, 720, 468, 885), D, RED,
               name="Barra")
    name = "HENDRICK CLUSON"
    nbox, nsize = caps_box(481, 736, 868, name)
    clip = name_text(t, name, nbox, nsize, D, bold_from="CLUSON", spacing=-5.0, bold_spacing=5.4, word_spacing=8)
    mask_track(t, clip, nbox, lambda u: (468, 700, bar_r(fin(u)) if fin(u) > 28.99 else 468, 900), D)
    return t


# Bevan Peterson, measured frame by frame (25 fps from 56.2 s; the exit is the entrance backwards, frame 152 - f).
_BP_LOGO = {0: 0.0, 1: 0.14, 2: 0.34, 5: 0.35, 6: 1.0, 8: 1.0, 9: 1.28, 10: 1.53, 12: 1.55, 13: 0.69, 15: 0.69,
            16: 0.83, 17: 1.0}  # the logo's scale about its bottom centre
_BP_TRIM = {12: (70.0, 70.0), 13: (70.0, 110.0), 14: (10.0, 165.0), 15: (0.0, 231.0), 16: (0.0, 347.2),
            17: (0.0, 527.0)}  # px along the outline: right side up, left side down, bottom, the line
_BP_LINE = {17: 481, 18: 595, 19: 695, 20: 783, 21: 863, 22: 931, 23: 991, 24: 1047, 25: 1095, 26: 1137, 27: 1175,
            28: 1208, 29: 1238, 30: 1264, 31: 1287, 32: 1307, 33: 1325, 34: 1342, 35: 1354, 36: 1365, 37: 1374,
            38: 1380, 39: 1385, 40: 1389, 41: 1391, 42: 1392}
_BP_NAME_TOP = {33: 840, 34: 811, 35: 790, 36: 766, 37: 748, 38: 735, 39: 726, 40: 719, 41: 713, 42: 708, 43: 704,
                44: 701, 45: 698, 46: 696, 47: 694, 48: 693, 49: 692, 51: 690}
_BP_ROLE_BOTTOM = {34: 815, 35: 831, 36: 849, 37: 862, 38: 871, 39: 878, 40: 883, 41: 887, 42: 890, 43: 893, 44: 895,
                   45: 897, 46: 899, 47: 900, 48: 901, 49: 902, 50: 903, 51: 904, 53: 905}


def bevan():
    """The logo pops up and bounces; a thin triangle draws itself round it from the middle of its right side, its
    bottom running on into a long line to the right; the name rises from behind the line and the role drops from
    it. Out, everything backwards."""
    fps, first, last = 25.0, 1, 151
    D = round((last - first + 1) / fps, 2)
    t = _kit("bevan", "Tercio con logo: triángulo que se dibuja", "Logo lower third: self-drawing triangle", D, 8540,
             ["nombre", "cargo", "línea", "triángulo", "logo"], thumb_at=2.6)
    photo_bg(t, "h-city-01", s1=1.03, label="Tu video")
    from llt_motion import frames_of
    from scene import shape_style, stroke
    us = frames_of(D)
    fin = lambda u: (lambda i: i if i <= 76 else 152 - i)(first + u * fps)  # noqa: E731
    apex, base, half, x_end = (387.5, 670.6), 821.0, 86.8, 1392.0
    side = 2 * half
    total = 3 * side + (x_end - (apex[0] + half))
    # The outline as one open path in a box from the triangle's left to the line's end: bottom-right corner, up to
    # the apex, down to the bottom-left, back along the bottom and on to the line's end.
    bx0, by0 = apex[0] - half, apex[1]
    bw, bh = x_end - bx0, base - by0
    P = lambda x, y: f"{(x - bx0) / bw * 100:.3f} {(y - by0) / bh * 100:.3f}"  # noqa: E731
    path = (f"M {P(apex[0] + half, base)} L {P(*apex)} L {P(apex[0] - half, base)} L {P(apex[0] + half, base)} "
            f"L {P(x_end, base)}")
    trim = _table(_BP_TRIM, (70.0, 70.0), None)
    line = _table(_BP_LINE, 474.3, 1392.0)

    def ends(f):
        if f < 12:
            return 0.0, 0.0
        if f <= 17:
            return trim(f)
        return 0.0, 3 * side + (line(f) - (apex[0] + half))
    s = stroke(2.6, RED)
    style = shape_style("custom", [s], customPath=path, customEvenOdd=False)
    style["keyframes"] = {"trimStart": keys([(u, ends(fin(u))[0] / total * 100, "linear") for u in us]),
                          "trimEnd": keys([(u, ends(fin(u))[1] / total * 100, "linear") for u in us])}
    from scene import layout
    box = Box(bx0, by0, bw, bh)
    tri = t._clip("shape", 0.0, D, shapeStyle=style, **layout(box, None))
    tri["name"] = "Triángulo"
    t.track("shape", "Triángulo").clips.append(tri)
    # The logo, scaled about its bottom centre.
    sc = _table(_BP_LOGO, 0.0, 1.0)
    lg = Box(382.5 - 40, 808 - 80, 80, 80)
    motion = [(u, {"s": sc(fin(u)), "dy": 40 - 40 * sc(fin(u))}, "linear") for u in us]
    t.photo(t.track("video", "Logo"), "logo-09", 0.0, D, lg, motion, label="Tu logo", brandRole="logo")
    # The name rises from behind the line; the role drops from it.
    top = _table(_BP_NAME_TOP, 900.0, 690.0)
    bottom = _table(_BP_ROLE_BOTTOM, 800.0, 905.0)
    name = "BEVAN PETERSON"
    nbox, nsize = caps_box(506, 690, 809, name)
    motion = [(u, {"dy": top(fin(u)) - 690}, "linear") for u in us]
    clip = name_text(t, name, nbox, nsize, D, bold_from="PETERSON", spacing=-4.5, bold_spacing=9.3, word_spacing=8,
                     motion=motion)
    track = next(tr for tr in t.tracks if clip in tr.clips)
    mk = {"y": [], "h": []}
    for u in us:
        dy = top(fin(u)) - 690
        y0, y1 = 500.0, 819.0
        mk["y"].append((u, ((y0 + y1) / 2 - nbox.y - dy) / nbox.h, "linear"))
        mk["h"].append((u, (y1 - y0) / nbox.h, "linear"))
    t.mask(track, clip, "rectangle", x=0.5, y=mk["y"][0][1], w=2.0, h=mk["h"][0][1],
           keyframes={k: keys(v) for k, v in mk.items()})
    role = "CHIEF OF SYSTEMS"
    rbox, rsize = caps_box(844, 834, 905, role)
    motion = [(u, {"dy": bottom(fin(u)) - 905}, "linear") for u in us]
    rclip = name_text(t, role, rbox, rsize, D, name="Cargo", spacing=-2.6, word_spacing=6, motion=motion)
    track = next(tr for tr in t.tracks if rclip in tr.clips)
    mk = {"y": [], "h": []}
    for u in us:
        dy = bottom(fin(u)) - 905
        y0, y1 = 823.0, 1080.0
        mk["y"].append((u, ((y0 + y1) / 2 - rbox.y - dy) / rbox.h, "linear"))
        mk["h"].append((u, (y1 - y0) / rbox.h, "linear"))
    t.mask(track, rclip, "rectangle", x=0.5, y=mk["y"][0][1], w=2.0, h=mk["h"][0][1],
           keyframes={k: keys(v) for k, v in mk.items()})
    return t


# Janice Hendrichsen, measured frame by frame (25 fps from 62.4 s): a thin line opens both ways from its middle,
# then the bar (with the role and the wordmark in it) rises out of it and the name rises faster above; out, the
# other way round.
_JH_LINE = {1: (822, 928), 2: (778, 971), 3: (696, 1052), 4: (598, 1152), 5: (530, 1218), 6: (486, 1264),
            7: (454, 1296), 8: (429, 1320), 9: (410, 1340), 10: (394, 1356), 11: (382, 1368), 12: (372, 1378),
            13: (363, 1386), 14: (356, 1392), 15: (350, 1400), 16: (346, 1403), 17: (343, 1406), 18: (340, 1409),
            20: (338, 1411), 21: (337, 1412), 23: (336, 1412), 117: (336, 1412), 118: (337, 1412), 119: (340, 1410),
            120: (350, 1400), 121: (372, 1376), 122: (421, 1328), 123: (532, 1217), 124: (652, 1098),
            125: (720, 1029), 126: (764, 984), 127: (794, 954), 128: (816, 932), 129: (875, 875)}
_JH_BAR = {20: 892, 21: 891, 23: 890, 24: 889, 25: 888, 26: 885, 27: 882, 28: 878, 29: 871, 30: 863, 31: 852,
           32: 843, 33: 837, 34: 832, 35: 828, 36: 824, 37: 821, 38: 819, 39: 816, 40: 815, 41: 813, 42: 811,
           44: 810, 45: 809, 46: 808, 47: 807, 49: 806, 51: 805, 53: 804, 96: 804, 97: 804, 98: 806, 99: 809,
           100: 812, 101: 821, 102: 835, 103: 850, 104: 860, 105: 867, 106: 872, 107: 876, 108: 880, 109: 882,
           110: 884, 111: 886, 112: 887, 113: 888, 114: 889, 115: 890, 116: 891, 118: 892}
_JH_NAME = {26: 895, 27: 877, 28: 866, 29: 849, 30: 825, 31: 798, 32: 775, 33: 758, 34: 744, 35: 733, 36: 724,
            37: 717, 38: 711, 39: 705, 40: 701, 41: 697, 42: 693, 43: 690, 44: 686, 45: 684, 46: 682, 47: 680,
            48: 679, 49: 677, 50: 676, 51: 674, 53: 673, 54: 672, 57: 671, 95: 671, 96: 672, 97: 674, 98: 677,
            99: 684, 100: 695, 101: 715, 102: 752, 103: 792, 104: 820, 105: 838, 106: 852, 107: 862, 108: 870,
            109: 876, 110: 895}


def janice():
    """A thin red line opens both ways from its middle; the bar with the role and the wordmark rises out of it and
    the name rises faster above it. Out, they sink back into the line and it closes into its middle."""
    fps, first, last = 25.0, 1, 129
    D = round((last - first + 1) / fps, 2)
    t = _kit("janice", "Tercio con logo: barra que sube de una línea", "Logo lower third: bar rising from a line", D,
             8541, ["nombre", "cargo", "barra", "rojo", "marca"], thumb_at=2.8)
    photo_bg(t, "h-city-01", s1=1.03, label="Tu video")
    from llt_motion import frames_of
    us = frames_of(D)
    fr = lambda u: first + u * fps  # noqa: E731
    line = _table(_JH_LINE, (875.0, 875.0), (875.0, 875.0))
    bar_top = _table(_JH_BAR, 892.0, 892.0)
    name_top = _table(_JH_NAME, 900.0, 900.0)
    X0, X1, Y1 = 336.0, 1412.0, 896.0
    # The line: 4 px tall, opening and closing; under the bar once that rises.
    rect_track(t, t.track("shape", "Línea"), Box(X0, 880, X1 - X0, 16),
               lambda u: (line(fr(u))[0], 892, line(fr(u))[1], Y1), D, RED, name="Línea")
    bar = Box(X0, 804, X1 - X0, Y1 - 804)
    rect_track(t, t.track("shape", "Barra"), bar, lambda u: (X0, bar_top(fr(u)), X1, Y1), D, RED, name="Barra")
    clip_below = lambda u: (0, 0, 1920, 892)  # noqa: E731  what rises shows only above the line
    role = "TECHNICAL SUPPORT"
    rbox, rsize = caps_box(357, 819, 885, role)
    motion = [(u, {"dy": bar_top(fr(u)) - 804}, "linear") for u in us]
    rclip = name_text(t, role, rbox, rsize, D, name="Cargo", spacing=-2.0, word_spacing=6, motion=motion)
    wm_box = Box(1070, 816, 331, 70)
    wm = t.photo(t.track("video", "Marca"), "logo-12", 0.0, D, wm_box, motion, label="Tu logo con nombre",
                 brandRole="logo")
    for c, b in ((rclip, rbox), (wm, wm_box)):
        track = next(tr for tr in t.tracks if c in tr.clips)
        mk = {"y": [], "h": []}
        for u in us:
            dy = bar_top(fr(u)) - 804
            mk["y"].append((u, ((0 + 892) / 2 - b.y - dy) / b.h, "linear"))
            mk["h"].append((u, 892 / b.h, "linear"))
        t.mask(track, c, "rectangle", x=0.5, y=mk["y"][0][1], w=4.0, h=mk["h"][0][1],
               keyframes={k: keys(v) for k, v in mk.items()})
    name = "JANICE HENDRICHSEN"
    nbox, nsize = caps_box(363, 671, 786, name)
    motion = [(u, {"dy": name_top(fr(u)) - 671}, "linear") for u in us]
    clip = name_text(t, name, nbox, nsize, D, bold_from="HENDRICHSEN", spacing=-4.5, bold_spacing=6.2, word_spacing=6,
                     motion=motion)
    track = next(tr for tr in t.tracks if clip in tr.clips)
    mk = {"y": [], "h": []}
    for u in us:
        dy = name_top(fr(u)) - 671
        mk["y"].append((u, ((0 + 892) / 2 - nbox.y - dy) / nbox.h, "linear"))
        mk["h"].append((u, 892 / nbox.h, "linear"))
    t.mask(track, clip, "rectangle", x=0.5, y=mk["y"][0][1], w=4.0, h=mk["h"][0][1],
           keyframes={k: keys(v) for k, v in mk.items()})
    return t


# Charlie Platinsky, measured frame by frame (25 fps from 67.9 s; out = in backwards, frame 142 - f): two thin white
# lines run in from opposite sides, then part, and the logo and the name rise between them.
_CP_TOP_R = {0: 311, 1: 325, 2: 356, 3: 417, 4: 542, 5: 787, 6: 996, 7: 1119, 8: 1201, 9: 1259, 10: 1304, 11: 1337,
             12: 1363, 13: 1383, 14: 1399, 15: 1410, 16: 1419, 17: 1424, 18: 1429}
_CP_BOT_L = {0: 1426, 1: 1412, 2: 1381, 3: 1320, 4: 1195, 5: 950, 6: 741, 7: 618, 8: 536, 9: 478, 10: 434, 11: 400,
             12: 373, 13: 354, 14: 338, 15: 326, 16: 318, 17: 313, 18: 310, 19: 308}
_CP_TOP_Y = {20: 771, 21: 770, 22: 769, 23: 767, 24: 763, 25: 756, 26: 743, 27: 729, 28: 720, 29: 714, 30: 709,
             31: 705, 32: 703, 33: 700, 34: 698, 35: 697, 36: 696, 37: 695, 38: 694, 39: 693, 41: 692}
_CP_BOT_Y = {20: 790, 21: 791, 22: 792, 23: 795, 24: 799, 25: 806, 26: 820, 27: 835, 28: 845, 29: 852, 30: 857,
             31: 861, 32: 864, 33: 867, 34: 868, 35: 870, 36: 872, 37: 873, 39: 874, 40: 875}
_CP_NAME = {26: 800, 27: 785, 28: 772, 29: 763, 30: 757, 31: 752, 32: 748, 33: 745, 34: 742, 35: 740, 36: 739,
            37: 737, 38: 736, 39: 735, 40: 734, 44: 733}


def charlie():
    """Two thin white lines run in from opposite sides and meet; they part, and the logo and the name rise between
    them. Out, everything backwards."""
    fps, first, last = 25.0, 4, 142
    D = round((last - first) / fps, 2)
    t = _kit("charlie", "Tercio con logo: dos líneas que se abren", "Logo lower third: two lines parting", D, 8542,
             ["nombre", "líneas", "blanco", "logo"], thumb_at=2.4)
    photo_bg(t, "h-city-01", s1=1.03, label="Tu video")
    from llt_motion import frames_of
    us = frames_of(D)
    fin = lambda u: (lambda i: i - 4 if i <= 71 else 138 - i)(first + u * fps)  # noqa: E731  the entrance frame
    X0, X1 = 308.0, 1430.0
    top_r = _table(_CP_TOP_R, 308.0, 1429.0)
    bot_l = _table(_CP_BOT_L, 1430.0, 308.0)
    top_y = _table(_CP_TOP_Y, 771.0, 692.0)
    bot_y = _table(_CP_BOT_Y, 790.0, 875.0)
    name_top = _table(_CP_NAME, 830.0, 733.0)
    area = Box(X0, 680, X1 - X0, 210)
    rect_track(t, t.track("shape", "Línea arriba"), area,
               lambda u: (X0, top_y(fin(u)), top_r(fin(u)) + 1, top_y(fin(u)) + 4) if fin(u) >= 0 else (X0, 771, X0, 771),
               D, WHITE, name="Línea arriba")
    rect_track(t, t.track("shape", "Línea abajo"), area,
               lambda u: (bot_l(fin(u)), bot_y(fin(u)), X1, bot_y(fin(u)) + 4) if fin(u) >= 0 else (X1, 790, X1, 790),
               D, WHITE, name="Línea abajo")
    between = lambda u: (X0, top_y(fin(u)) + 4, X1, bot_y(fin(u)))  # noqa: E731
    dy = lambda u: name_top(fin(u)) - 733  # noqa: E731
    lg = Box(343, 715, 124, 142)
    motion = [(u, {"dy": dy(u)}, "linear") for u in us]
    mark = t.photo(t.track("video", "Logo"), "logo-09", 0.0, D, lg, motion, label="Tu logo", brandRole="logo")
    name = "CHARLIE PLATINSKY"
    nbox, nsize = caps_box(519, 734, 839, name)
    clip = name_text(t, name, nbox, nsize, D, bold_from="PLATINSKY", spacing=-3.0, bold_spacing=5.5, word_spacing=6,
                     motion=motion)
    for c, b in ((mark, lg), (clip, nbox)):
        track = next(tr for tr in t.tracks if c in tr.clips)
        mk = {"y": [], "h": []}
        for u in us:
            x0, y0, x1, y1 = between(u)
            mk["y"].append((u, ((y0 + y1) / 2 - b.y - dy(u)) / b.h, "linear"))
            mk["h"].append((u, max(0.0, y1 - y0) / b.h, "linear"))
        t.mask(track, c, "rectangle", x=0.5, y=mk["y"][0][1], w=4.0, h=mk["h"][0][1],
               keyframes={k: keys(v) for k, v in mk.items()})
    return t


# Lizzie Winson, measured frame by frame (25 fps from 74.6 s; out = in backwards, frame 107 - f): a thin red line,
# leaning at first, sweeps right; the logo and the name show left of it, the role slides along right of it.
_LW_LINE = {0: 325.0, 1: 323.5, 2: 325.0, 3: 330.0, 4: 339.0, 5: 354.5, 6: 379.0, 7: 419.0, 8: 485.0, 9: 574.0,
            10: 647.0, 11: 697.0, 12: 735.0, 13: 763.0, 14: 785.0, 15: 803.0, 16: 819.0, 17: 831.0, 18: 843.0,
            19: 851.0, 20: 859.0, 21: 866.0, 22: 871.0, 23: 877.0, 24: 879.0, 25: 883.0, 26: 885.0, 27: 887.0,
            30: 888.0}
_LW_ROLE_R = {9: 648.0, 10: 834.0, 11: 965.0, 12: 1060.0, 13: 1133.0, 14: 1191.0, 15: 1238.0, 16: 1278.0,
              17: 1310.0, 18: 1338.0, 19: 1362.0, 20: 1382.0, 21: 1398.0, 22: 1413.0, 23: 1424.0, 24: 1434.0,
              25: 1442.0, 26: 1447.0, 27: 1452.0, 28: 1455.0, 29: 1457.0, 30: 1458.0}
_LW_TILT = {0: 3.8, 1: 2.7, 2: 1.5, 3: 1.0, 4: 0.4, 5: 0.0}
_LW_TOP = {0: 743.0, 1: 739.0, 2: 738.0}


def lizzie():
    """A thin red line, leaning at first, sweeps right: the logo and the name show left of it and the role slides
    along right of it. Out, the line sweeps back and takes them."""
    fps, first, last = 25.0, 0, 107
    D = round((last - first + 1) / fps, 2)
    t = _kit("lizzie", "Tercio con logo: línea que barre", "Logo lower third: sweeping line", D, 8543,
             ["nombre", "cargo", "línea", "logo"], thumb_at=2.4)
    photo_bg(t, "h-city-01", s1=1.03, label="Tu video")
    from llt_motion import frames_of
    us = frames_of(D)
    fin = lambda u: (lambda i: i if i <= 53 else 107 - i)(first + u * fps)  # noqa: E731
    L = _table(_LW_LINE, 325.0, 888.0)
    R = _table({8: 300.0, **_LW_ROLE_R}, 300.0, 1458.0)
    tilt = _table(_LW_TILT, 3.8, 0.0)
    top = _table(_LW_TOP, 743.0, 738.0)
    lb = Box(886.5, 738, 3, 152)
    motion = [(u, {"dx": L(fin(u)) - 888, "sy": (890 - top(fin(u))) / 152, "dy": (top(fin(u)) - 738) / 2}, "linear")
              for u in us]
    line = t.solid(t.track("shape", "Línea"), RED, 0.0, D, lb, motion,
                   rotation=keys([(u, tilt(fin(u)), "linear") for u in us]))
    line["name"] = "Línea"
    left_of = lambda u: (0, 600, L(fin(u)), 1000)  # noqa: E731
    lg = Box(350, 772, 73, 92)
    mark = t.photo(t.track("video", "Logo"), "logo-09", 0.0, D, lg, label="Tu logo", brandRole="logo")
    mask_track(t, mark, lg, left_of, D)
    name = "LIZZIE WINSON"
    nbox, nsize = caps_box(449, 781, 851, name)
    clip = name_text(t, name, nbox, nsize, D, bold_from="WINSON", spacing=-3.2, bold_spacing=4.3, word_spacing=6)
    mask_track(t, clip, nbox, left_of, D)
    role = "ENVIRONMENTALIST"
    rbox, rsize = caps_box(911, 781, 851, role)
    motion = [(u, {"dx": R(fin(u)) - 1458}, "linear") for u in us]
    rclip = name_text(t, role, rbox, rsize, D, name="Cargo", spacing=-1.8, motion=motion)
    track = next(tr for tr in t.tracks if rclip in tr.clips)
    mk = {"x": [], "w": []}
    for u in us:
        x0, dx = L(fin(u)) + 2, R(fin(u)) - 1458
        mk["x"].append((u, ((x0 + 3000) / 2 - rbox.x - dx) / rbox.w, "linear"))
        mk["w"].append((u, (3000 - x0) / rbox.w, "linear"))
    t.mask(track, rclip, "rectangle", x=mk["x"][0][1], y=0.5, w=mk["w"][0][1], h=2.0,
           keyframes={k: keys(v) for k, v in mk.items()})
    return t


# Patricia Franklin, measured frame by frame (25 fps from 79.6 s). In: the logo flips down into place (its box per
# frame), the name slides in from the right edge, the role from behind its left edge, the underline runs left. Out:
# the whole lower third tips back about the name's baseline (row 804): the angle is solved from the name's top.
_PF_LOGO = {6: (290, 643, 470, 658), 7: (292, 636, 473, 669), 8: (296, 627, 476, 685), 9: (304, 620, 479, 712),
            10: (312, 623, 479, 760), 11: (320, 663, 479, 850), 12: (320, 712, 479, 908), 13: (321, 698, 479, 894),
            14: (321, 689, 479, 884), 15: (321, 685, 479, 879), 16: (321, 684, 479, 878), 17: (321, 685, 479, 879),
            18: (321, 690, 479, 885), 19: (321, 694, 479, 889)}
_PF_NAME_L = {5: 1600, 6: 1520, 7: 1463, 8: 1355, 9: 1152, 10: 963, 11: 848, 12: 770, 13: 715, 14: 672, 15: 639,
              16: 613, 17: 592, 18: 575, 19: 562, 20: 552, 21: 544, 22: 538, 23: 534, 24: 532}
_PF_ROLE_R = {6: 801, 7: 844, 8: 909, 9: 1030, 10: 1143, 11: 1212, 12: 1258, 13: 1292, 14: 1317, 15: 1337, 16: 1353,
              17: 1365, 18: 1375, 19: 1383, 20: 1389, 21: 1394, 22: 1398, 23: 1400, 24: 1401, 25: 1402}
_PF_LINE_L = {8: 1407, 9: 1393, 10: 1362, 11: 480}
_PF_TOP = {102: 696, 103: 697, 104: 698, 105: 700, 106: 703, 107: 707, 108: 712, 109: 718, 110: 728, 111: 742,
           112: 765, 113: 803}


def patricia():
    """The logo flips down into place with a bounce, the name slides in from the right and the role from behind its
    left edge, the underline runs left between them. Out, the whole lower third tips back and is gone."""
    fps, first, last = 25.0, 5, 115
    D = round((last - first + 1) / fps, 2)
    t = _kit("patricia", "Tercio con logo: logo que gira y nombre que entra", "Logo lower third: flipping logo, sliding name",
             D, 8544, ["nombre", "cargo", "subrayado", "logo", "3d"], thumb_at=2.4)
    photo_bg(t, "h-city-01", s1=1.03, label="Tu video")
    from llt_motion import frames_of
    us = frames_of(D)
    fr = lambda u: first + u * fps  # noqa: E731
    AX = 804.0

    def tip_angle(f):
        if f < 102:
            return 0.0
        if f >= 113:
            return 89.9
        top = _table(_PF_TOP, 696.0, 803.0)(f)
        return _solve(lambda a: _project(AX - 108 * math.cos(math.radians(a)), -108 * math.sin(math.radians(a))),
                      top, 0, 89.9)
    ang = {u: tip_angle(fr(u)) for u in us}

    def tip(clip, box, xs=None, ys=None, hs=None):
        """3D keys: the clip turned with the lower third about row 804 (its own centre y per frame from ys)."""
        yk, zk, rk = [], [], []
        for k, u in enumerate(us):
            cy = ys[k] if ys else box.cy
            h = hs[k] if hs else box.h
            a = math.radians(ang[u])
            d = cy - AX
            yk.append((u, AX + d * math.cos(a) - h / 2, "linear"))
            zk.append((u, d * math.sin(a), "linear"))
            rk.append((u, ang[u], "linear"))
        clip["layer3d"] = True
        clip["perspective"] = keys([(0, _EYE)])
        clip["y"] = keys(yk)
        clip["positionZ"] = keys(zk)
        clip["rotationX"] = keys(rk)
        clip["opacity"] = keys([(u, 0.0 if ang[u] > 89 else 1.0, "hold") for u in us])
    # Logo: its measured box while it flips in.
    logo = _table(_PF_LOGO, (380, 650, 380, 650), (321, 694, 479, 889))
    lg = Box(321, 694, 158, 195)
    xs, ys, ws, hs = [], [], [], []
    for u in us:
        x0, y0, x1, y1 = logo(fr(u))
        xs.append((x0 + x1) / 2); ys.append((y0 + y1) / 2); ws.append(max(0.0, x1 - x0)); hs.append(max(0.0, y1 - y0))
    mark = t.photo(t.track("video", "Logo"), "logo-09", 0.0, D, lg, label="Tu logo", brandRole="logo")
    mark["x"] = keys([(u, x - w / 2, "linear") for u, x, w in zip(us, xs, ws)])
    mark["width"] = keys([(u, w, "linear") for u, w in zip(us, ws)])
    mark["height"] = keys([(u, h, "linear") for u, h in zip(us, hs)])
    tip(mark, lg, ys=ys, hs=hs)
    # The underline under the name, running left.
    line_l = _table(_PF_LINE_L, 1407.0, 480.0)
    ub = Box(480, 820, 927, 3)
    rx0 = [line_l(fr(u)) for u in us]
    ul = t.solid(t.track("shape", "Línea"), RED, 0.0, D, ub)
    ul["name"] = "Línea"
    ul["x"] = keys([(u, x, "linear") for u, x in zip(us, rx0)])
    ul["width"] = keys([(u, 1407 - x, "linear") for u, x in zip(us, rx0)])
    tip(ul, ub)
    name = "PATRICIA FRANKLIN"
    nbox, nsize = caps_box(532, 696, 804, name)
    nl = _table(_PF_NAME_L, 1600.0, 532.0)
    clip = name_text(t, name, nbox, nsize, D, bold_from="FRANKLIN", spacing=-3.2, bold_spacing=5.0, word_spacing=6,
                     motion=[(u, {"dx": nl(fr(u)) - 532}, "linear") for u in us])
    track = next(tr for tr in t.tracks if clip in tr.clips)
    t.mask(track, clip, "rectangle", x=0.5, y=0.5, w=1.0, h=2.0,
           keyframes={"x": keys([(u, ((-1000 + 1560) / 2 - nbox.x - (nl(fr(u)) - 532)) / nbox.w, "linear") for u in us]),
                      "w": keys([(u, 2560 / nbox.w, "linear") for u in us])})
    tip(clip, nbox)
    role = "SECURITY ADVISOR"
    rbox, rsize = caps_box(952, 834, 892, role)
    rr = _table(_PF_ROLE_R, 801.0, 1402.0)
    rclip = name_text(t, role, rbox, rsize, D, name="Cargo", spacing=-2.1, word_spacing=6,
                      motion=[(u, {"dx": rr(fr(u)) - 1402}, "linear") for u in us])
    track = next(tr for tr in t.tracks if rclip in tr.clips)
    t.mask(track, rclip, "rectangle", x=0.5, y=0.5, w=1.0, h=2.0,
           keyframes={"x": keys([(u, ((801 + 3000) / 2 - rbox.x - (rr(fr(u)) - 1402)) / rbox.w, "linear") for u in us]),
                      "w": keys([(u, 2199 / rbox.w, "linear") for u in us])})
    tip(rclip, rbox)
    return t


# Jim Reeves, measured frame by frame (25 fps from 84.3 s): the logo's box every frame (it grows from a dot, slides
# left; out it slides right, swells and comes back shrinking to a dot), and the name's right end coming in. The name
# shows only right of the logo.
_JR_LOGO = {0: (472, 916, 476, 919), 1: (474, 905, 486, 919), 2: (474, 894, 495, 919), 3: (476, 884, 505, 918),
            4: (476, 876, 512, 918), 5: (476, 869, 519, 918), 6: (477, 864, 523, 917), 7: (478, 860, 527, 917),
            8: (478, 857, 531, 917), 9: (480, 843, 543, 916), 10: (494, 694, 682, 908), 11: (498, 662, 711, 906),
            12: (498, 658, 714, 906), 13: (496, 657, 713, 906), 14: (492, 658, 708, 906), 15: (484, 662, 697, 906),
            16: (464, 671, 671, 907), 17: (392, 704, 571, 908), 18: (357, 721, 523, 909), 19: (344, 727, 503, 910),
            20: (336, 731, 491, 910), 21: (330, 733, 485, 910), 22: (326, 735, 480, 910), 23: (324, 736, 477, 910),
            24: (324, 736, 475, 910), 98: (324, 736, 475, 910), 99: (325, 736, 477, 910), 100: (332, 736, 483, 910),
            101: (344, 736, 497, 910), 102: (368, 736, 519, 910), 103: (406, 736, 559, 910), 104: (475, 736, 629, 911),
            105: (604, 736, 757, 911), 106: (760, 736, 913, 911), 107: (866, 736, 1021, 911),
            108: (938, 736, 1091, 911), 109: (988, 736, 1141, 911), 110: (1028, 736, 1180, 911),
            111: (1058, 736, 1211, 911), 112: (1082, 736, 1235, 911), 113: (1102, 736, 1255, 911),
            114: (1078, 724, 1240, 910), 115: (1030, 705, 1209, 909), 116: (988, 688, 1181, 907),
            117: (956, 674, 1161, 907), 118: (939, 665, 1151, 907), 119: (937, 662, 1151, 907),
            120: (939, 664, 1151, 907), 121: (928, 670, 1137, 907), 122: (898, 683, 1095, 907),
            123: (821, 715, 991, 909), 124: (664, 780, 781, 913), 125: (546, 830, 621, 915), 126: (479, 858, 530, 917),
            127: (434, 877, 470, 918), 128: (402, 890, 427, 919), 129: (380, 900, 396, 919), 130: (362, 908, 373, 919),
            131: (350, 913, 355, 919), 132: (340, 917, 343, 919), 133: (340, 919, 340, 919)}
_JR_NAME_R = {15: 600, 16: 835, 17: 906, 18: 949, 19: 978, 20: 997, 21: 1011, 22: 1020, 23: 1026, 24: 1029, 25: 1031}


def jim():
    """The logo grows from a dot and slides left, the name coming out from behind it; out, the logo slides right over
    the name, swells and shrinks back to a dot."""
    fps, first, last = 25.0, 0, 133
    D = round((last - first + 1) / fps, 2)
    t = _kit("jim", "Tercio con logo: logo que destapa el nombre", "Logo lower third: logo uncovering the name", D, 8545,
             ["nombre", "logo", "simple"], thumb_at=2.4)
    photo_bg(t, "h-city-01", s1=1.03, label="Tu video")
    from llt_motion import frames_of
    us = frames_of(D)
    fr = lambda u: first + u * fps  # noqa: E731
    logo = _table(_JR_LOGO, (472, 916, 476, 919), (340, 919, 340, 919))
    name_r = _table(_JR_NAME_R, 600.0, 1031.0)
    name = "JIM REEVES"
    nbox, nsize = caps_box(520, 767, 876, name)
    clip = name_text(t, name, nbox, nsize, D, bold_from="REEVES", spacing=-2.5, bold_spacing=6, word_spacing=6,
                     motion=[(u, {"dx": name_r(fr(u)) - 1031}, "linear") for u in us])
    track = next(tr for tr in t.tracks if clip in tr.clips)
    mk = {"x": [], "w": []}
    for u in us:
        x0 = logo(fr(u))[2] - 8 if 15 <= fr(u) <= 108 else 3000.0
        dx = name_r(fr(u)) - 1031
        mk["x"].append((u, ((x0 + 3000) / 2 - nbox.x - dx) / nbox.w, "linear"))
        mk["w"].append((u, max(0.0, 3000 - x0) / nbox.w, "linear"))
    t.mask(track, clip, "rectangle", x=mk["x"][0][1], y=0.5, w=mk["w"][0][1], h=2.0,
           keyframes={k: keys(v) for k, v in mk.items()})
    # The logo on top, its square slot fitted to the measured box (the mark keeps its shape).
    lg = centered(399.5, 823, 174, 174)
    mark = t.photo(t.track("video", "Logo"), "logo-09", 0.0, D, lg, label="Tu logo", brandRole="logo")
    xs, ys, ss = [], [], []
    for u in us:
        x0, y0, x1, y1 = logo(fr(u))
        s = max(x1 - x0, y1 - y0) * 174 / 174
        xs.append((u, (x0 + x1) / 2 - s / 2, "linear")); ys.append((u, (y0 + y1) / 2 - s / 2, "linear"))
        ss.append((u, s, "linear"))
    mark["x"], mark["y"], mark["width"], mark["height"] = keys(xs), keys(ys), keys(ss), keys(ss)
    return t


# Jason Fletcher, measured frame by frame (25 fps from 89.85 s; out = in backwards, frame 129 - f): a red tab with the
# wordmark grows up and left from the bar's bottom-right corner, then climbs, and the white name bar rises under it
# and opens to the left.
_JF_TOP = {2: 880, 3: 876, 4: 867, 5: 853, 6: 838, 7: 829, 8: 824, 9: 819, 10: 815, 11: 813, 12: 811, 13: 808,
           14: 805, 15: 801, 16: 793, 17: 777, 18: 749, 19: 721, 20: 703, 21: 692, 22: 684, 23: 677, 24: 673, 25: 669,
           26: 666, 27: 664, 28: 662, 29: 661, 30: 660, 31: 659}
_JF_LEFT = {2: 1176, 3: 1152, 4: 1112, 5: 1039, 6: 964, 7: 917, 8: 886, 9: 862, 10: 844, 11: 831, 12: 820, 13: 810,
            14: 803, 15: 797, 16: 792, 17: 789, 18: 786, 19: 784, 20: 782}
_JF_BAR_L = {16: 1197, 17: 1000, 18: 860, 19: 700, 20: 575, 21: 520, 22: 498, 23: 432, 24: 400, 25: 369, 26: 358,
             27: 336, 28: 326, 29: 317, 30: 311, 31: 307, 32: 305}


def jason_f():
    """A red tab with the wordmark grows out of a corner and climbs; the white bar with the red name rises under it
    and opens to the left. Out, backwards."""
    fps, first, last = 25.0, 2, 127
    D = round((last - first + 1) / fps, 2)
    t = _kit("jason-f", "Tercio con logo: pestaña que sube y barra blanca", "Logo lower third: rising tab, white bar", D,
             8546, ["nombre", "barra", "blanco", "marca"], thumb_at=2.4)
    photo_bg(t, "h-city-01", s1=1.03, label="Tu video")
    from llt_motion import frames_of
    us = frames_of(D)
    fin = lambda u: (lambda i: i if i <= 64 else 129 - i)(first + u * fps)  # noqa: E731
    top = _table(_JF_TOP, 882.0, 659.0)
    left = _table(_JF_LEFT, 1197.0, 782.0)
    bar_l = _table(_JF_BAR_L, 1197.0, 305.0)
    R, B = 1197.0, 883.0
    tab_bottom = lambda f: B if f <= 14 else top(f) + 80  # noqa: E731
    bar_top = lambda f: B if f < 15 else tab_bottom(f) + 2  # noqa: E731
    bar = Box(305, 740, R - 305, B - 740)
    rect_track(t, t.track("shape", "Barra"), bar, lambda u: (bar_l(fin(u)), bar_top(fin(u)), R, B), D, WHITE,
               name="Barra")
    name = "JASON FLETCHER"
    nbox, nsize = caps_box(324, 754, 875, name)
    clip = name_text(t, name, nbox, nsize, D, bold_from="FLETCHER", colour=RED, spacing=-1.0, bold_spacing=6.5,
                     word_spacing=6)
    mask_track(t, clip, nbox, lambda u: (bar_l(fin(u)), bar_top(fin(u)), R, B), D)
    tab = Box(782, 659, R - 782, 80)
    tab_rect = lambda u: (left(fin(u)), top(fin(u)), R, tab_bottom(fin(u)))  # noqa: E731
    rect_track(t, t.track("shape", "Pestaña"), Box(782, 640, R - 782, 250), tab_rect, D, RED, name="Pestaña")
    wm = Box(810, 668, 366, 66)
    motion = [(u, {"dx": left(fin(u)) - 782, "dy": top(fin(u)) - 659}, "linear") for u in us]
    mark = t.photo(t.track("video", "Marca"), "logo-12", 0.0, D, wm, motion, label="Tu logo con nombre",
                   brandRole="logo")
    track = next(tr for tr in t.tracks if mark in tr.clips)
    mk = {"x": [], "y": [], "w": [], "h": []}
    for u in us:
        x0, y0, x1, y1 = tab_rect(u)
        dx, dy = left(fin(u)) - 782, top(fin(u)) - 659
        mk["x"].append((u, ((x0 + x1) / 2 - wm.x - dx) / wm.w, "linear"))
        mk["y"].append((u, ((y0 + y1) / 2 - wm.y - dy) / wm.h, "linear"))
        mk["w"].append((u, max(0.0, x1 - x0) / wm.w, "linear"))
        mk["h"].append((u, max(0.0, y1 - y0) / wm.h, "linear"))
    t.mask(track, mark, "rectangle", x=mk["x"][0][1], y=mk["y"][0][1], w=mk["w"][0][1], h=mk["h"][0][1],
           keyframes={k: keys(v) for k, v in mk.items()})
    return t


def _row_runs(path):
    """lt_ref/<name>_rows.txt: per frame the red and white runs on one row (frame -> (red runs, white runs))."""
    import ast
    import re
    out = {}
    for line in (Path(__file__).with_name("lt_ref") / path).read_text(encoding="utf-8").splitlines():
        m = re.match(r"(\d+) red (\[.*?\]) white (\[.*\])", line)
        if m:
            out[int(m.group(1))] = (ast.literal_eval(m.group(2)), ast.literal_eval(m.group(3)))
    return out


def lucas():
    """A red square trailing a white bar slides in from the right; the white shrinks into the square, then a red block
    runs out to the right with the white opening behind it, uncovering the name. Out, backwards. Every edge is the
    measured one on row 725 (lt_ref/lucas_rows.txt)."""
    fps, first, last = 25.0, 2, 145
    D = round((last - first + 1) / fps, 2)
    t = _kit("lucas", "Tercio con logo: bloque que corre y abre la barra", "Logo lower third: running block opens the bar",
             D, 8547, ["nombre", "barra", "blanco", "rojo", "logo"], thumb_at=2.6)
    photo_bg(t, "h-city-01", s1=1.03, label="Tu video")
    from llt_motion import frames_of
    us = frames_of(D)
    rows = _row_runs("lucas_rows.txt")
    fin = lambda u: (lambda i: i if i <= 73 else 146 - i)(first + u * fps)  # noqa: E731
    sq, w1, r2 = {}, {}, {}
    for f in range(0, 50):
        reds, whites = rows.get(f, ([], []))
        sq[f] = (reds[0][0], reds[0][1] + 1) if reds else (1446.0, 1446.0)
        w1[f] = (whites[0][0], whites[-1][1] + 1) if whites else (sq[f][1], sq[f][1])
        r2[f] = (reds[1][0], reds[1][1] + 1) if len(reds) > 1 else (w1[f][1], w1[f][1])
    pick = lambda table, k: _table({f: v[k] for f, v in table.items()}, table[0][k], table[49][k])  # noqa: E731
    sq0, sq1, w0, wr, ra, rb = pick(sq, 0), pick(sq, 1), pick(w1, 0), pick(w1, 1), pick(r2, 0), pick(r2, 1)
    Y0, Y1 = 721.0, 880.0
    area = Box(301, Y0, 1145, Y1 - Y0)
    rect_track(t, t.track("shape", "Barra"), area, lambda u: (w0(fin(u)), Y0, wr(fin(u)), Y1), D, WHITE, name="Barra")
    rect_track(t, t.track("shape", "Bloque"), area, lambda u: (ra(fin(u)), Y0, rb(fin(u)), Y1), D, RED, name="Bloque")
    rect_track(t, t.track("shape", "Cuadro"), area, lambda u: (sq0(fin(u)), Y0, sq1(fin(u)), Y1), D, RED, name="Cuadro")
    name = "LUCAS HEMMINGWAY"
    nbox, nsize = caps_box(484, 749, 854, name)
    clip = name_text(t, name, nbox, nsize, D, bold_from="HEMMINGWAY", colour=RED, spacing=-4.0, bold_spacing=1.6,
                     word_spacing=6)
    # The name only once the block runs out (the white train before it is blank).
    mask_track(t, clip, nbox, lambda u: (w0(fin(u)), Y0, wr(fin(u)), Y1) if fin(u) >= 28 else (0, 0, 0, 0), D)
    # The logo stays put and shows wherever the square passes over it.
    lg = Box(318, 730, 124, 133)
    mark = t.photo(t.track("video", "Logo"), "logo-15", 0.0, D, lg, label="Tu logo", brandRole="logo")
    mask_track(t, mark, lg, lambda u: (sq0(fin(u)), Y0, sq1(fin(u)), Y1), D)
    return t


def _boxes(path):
    """lt_ref/<name>.txt from a per-frame scan: frame -> {"logo": (x0, y0, x1, y1) | None, "name": ... | None}."""
    import re
    out = {}
    for line in (Path(__file__).with_name("lt_ref") / path).read_text(encoding="utf-8").splitlines():
        line = re.sub(r"np\.int64\((\d+)\)", r"\1", line)
        m = re.match(r"(\d+) logo (None|\(.*?\)) name (None|\(.*?\))", line)
        if m:
            out[int(m.group(1))] = {"logo": eval(m.group(2)), "name": eval(m.group(3))}  # noqa: S307 - our own scan
    return out


def brian():
    """A glitchy entrance: the logo flickers in at three sizes, rising from behind a line, then settles; the name
    flashes in small and jumps to full size, easing into place. Out, the same backwards. Every box is the measured
    one (lt_ref/brian.txt, 25 fps from 100.95 s; out = frame 138 - f)."""
    fps, first, last = 25.0, 1, 129
    D = round((last - first + 1) / fps, 2)
    t = _kit("brian", "Tercio con logo: entrada con parpadeo", "Logo lower third: glitch entrance", D, 8548,
             ["nombre", "logo", "glitch"], thumb_at=2.4)
    photo_bg(t, "h-city-01", s1=1.03, label="Tu video")
    from llt_motion import frames_of
    us = frames_of(D)
    scan = _boxes("brian.txt")
    fin = lambda u: (lambda i: i if i <= 69 else 138 - i)(int(round(first + u * fps)))  # noqa: E731
    rest = scan[45]
    LW, LH = 163.0, 187.0
    lg = Box(324, 679, LW, LH)
    lx, ly, lw, lh, lo = [], [], [], [], []
    for u in us:
        b = scan.get(fin(u), {}).get("logo")
        if b is None:
            b, op = rest["logo"], 0.0
        else:
            op = 1.0
        x0, y0, x1, y1 = b
        w = x1 - x0 + 1
        h = w * LH / LW
        lx.append((u, x0, "hold")); ly.append((u, y0, "hold")); lw.append((u, w, "hold")); lh.append((u, h, "hold"))
        lo.append((u, op, "hold"))
    mark = t.photo(t.track("video", "Logo"), "logo-09", 0.0, D, lg, label="Tu logo", brandRole="logo")
    mark.update(x=keys(lx), y=keys(ly), width=keys(lw), height=keys(lh), opacity=keys(lo))
    track = next(tr for tr in t.tracks if mark in tr.clips)
    t.mask(track, mark, "rectangle", x=0.5, y=0.5, w=1.0, h=1.0,
           keyframes={"y": keys([(u, ((0 + 874) / 2 - y[1]) / h[1], "hold") for u, y, h in zip(us, ly, lh)]),
                      "h": keys([(u, 874 / h[1], "hold") for u, y, h in zip(us, ly, lh)]),
                      "w": keys([(u, 2.0, "hold") for u in us])})
    name = "BRIAN HANSON"
    nbox, nsize = caps_box(524, 710, 823, name)
    rx0, ry0, rx1, ry1 = rest["name"]
    rw, rh = rx1 - rx0, ry1 - ry0
    from llt_motion import CAPS_DROP, INSET
    motion, op, sizes = [], [], []
    for u in us:
        b = scan.get(fin(u), {}).get("name")
        if b is None:
            b, o = rest["name"], 0.0
        else:
            o = 1.0
        x0, y0, x1, y1 = b
        size = nsize * (x1 - x0) / rw  # the glyphs scale (a smaller box would only re-wrap the line)
        dx = (x0 - INSET * size) - (rx0 - INSET * nsize)
        dy = ((y0 + y1) / 2 - CAPS_DROP * size) - ((ry0 + ry1) / 2 - CAPS_DROP * nsize)
        motion.append((u, {"dx": dx, "dy": dy}, "hold"))
        sizes.append((u, size, "hold"))
        op.append((u, o, "hold"))
    clip = name_text(t, name, nbox, nsize, D, bold_from="HANSON", spacing=-4.0, bold_spacing=3, word_spacing=6,
                     motion=motion)
    clip["opacity"] = keys(op)
    clip["textStyle"]["keyframes"] = {"pixelSize": keys(sizes)}
    return t


def _scan(path, keys_):
    """lt_ref/<name>.txt: frame -> {key: tuple | None} for lines "N key (a, b, ...) key None ..."."""
    import re
    out = {}
    for line in (Path(__file__).with_name("lt_ref") / path).read_text(encoding="utf-8").splitlines():
        line = re.sub(r"np\.int64\((\d+)\)", r"\1", line)
        m = re.match(r"(\d+) (.*)", line)
        if not m:
            continue
        row = {}
        for k in keys_:
            mm = re.search(rf"\b{k} (None|\([^)]*\))", m.group(2))
            row[k] = eval(mm.group(1)) if mm else None  # noqa: S307 - our own scan
        out[int(m.group(1))] = row
    return out


def harry():
    """A red block with the wordmark runs in from the right, pulling a thin underline after it; the role slides in
    under the line from the left; the block runs on to the left edge, uncovering the name, and shrinks into it. Out,
    backwards (lt_ref/harry.txt, 25 fps from 106.55 s; out = frame 133 - f)."""
    fps, first, last = 25.0, 3, 131
    D = round((last - first + 1) / fps, 2)
    t = _kit("harry", "Tercio con logo: bloque que corre y destapa", "Logo lower third: running block reveals the name", D,
             8549, ["nombre", "cargo", "subrayado", "marca"], thumb_at=2.6)
    photo_bg(t, "h-city-01", s1=1.03, label="Tu video")
    from llt_motion import frames_of
    us = frames_of(D)
    scan = _scan("harry.txt", ("box", "ul", "role"))
    fin = lambda u: (lambda i: i if i <= 66 else 133 - i)(first + u * fps)  # noqa: E731
    boxL = _table({f: r["box"][0] for f, r in scan.items() if f <= 26 and r["box"]}, 1158.0, 298.0)
    boxR = _table({**{f: r["box"][2] + 1 for f, r in scan.items() if f <= 26 and r["box"]}, 27: 298.0}, 1158.0, 298.0)
    ulR = _table({f: r["ul"][1] + 1 for f, r in scan.items() if f <= 40 and r["ul"]}, 298.0, 1158.0)
    roleR = _table({f: r["role"][1] for f, r in scan.items() if 9 <= f <= 40 and r["role"]}, 300.0, 1133.0)
    Y0, Y1 = 703.0, 807.0
    name = "HARRY SABBATA"
    nbox, nsize = caps_box(330, 711, 801, name)
    clip = name_text(t, name, nbox, nsize, D, bold_from="SABBATA", spacing=-4.0, bold_spacing=7.6, word_spacing=6)
    mask_track(t, clip, nbox, lambda u: (boxL(fin(u)) if fin(u) <= 26 else 0, 600, 3000, 900), D)
    rect_track(t, t.track("shape", "Línea"), Box(298, 811, 860, 3), lambda u: (298, 811, ulR(fin(u)), 813), D, RED,
               name="Línea")
    role = "SPORTS SCIENTIST"
    rbox, rsize = caps_box(668, 824, 888, role)
    rclip = name_text(t, role, rbox, rsize, D, name="Cargo", spacing=-2.3, word_spacing=6,
                      motion=[(u, {"dx": roleR(fin(u)) - 1133}, "linear") for u in us])
    track = next(tr for tr in t.tracks if rclip in tr.clips)
    t.mask(track, rclip, "rectangle", x=0.5, y=0.5, w=1.0, h=2.0,
           keyframes={"x": keys([(u, ((297 + 3000) / 2 - rbox.x - (roleR(fin(u)) - 1133)) / rbox.w, "linear")
                                 for u in us]),
                      "w": keys([(u, 2703 / rbox.w, "linear") for u in us])})
    rect = lambda u: (boxL(fin(u)), Y0, boxR(fin(u)), Y1)  # noqa: E731
    rect_track(t, t.track("shape", "Bloque"), Box(298, Y0, 860, Y1 - Y0), rect, D, RED, name="Bloque")
    wm = Box(425, 718, 345, 72)
    wm_dx = lambda u: min(425.0, boxL(fin(u)) + 8) - 425  # noqa: E731
    mark = t.photo(t.track("video", "Marca"), "logo-12", 0.0, D, wm, [(u, {"dx": wm_dx(u)}, "linear") for u in us],
                   label="Tu logo con nombre", brandRole="logo")
    track = next(tr for tr in t.tracks if mark in tr.clips)
    mk = {"x": [], "w": []}
    for u in us:
        x0, _, x1, _ = rect(u)
        mk["x"].append((u, ((x0 + x1) / 2 - wm.x - wm_dx(u)) / wm.w, "linear"))
        mk["w"].append((u, max(0.0, x1 - x0) / wm.w, "linear"))
    t.mask(track, mark, "rectangle", x=mk["x"][0][1], y=0.5, w=mk["w"][0][1], h=2.0,
           keyframes={k: keys(v) for k, v in mk.items()})
    return t


def sarah():
    """A red ring with the logo pops up from below; two red lines run out to the right; the name slides down from
    behind the top line and the role from behind the bottom one. Out, they slide back, the lines run back in and the
    ring drops away. Every value is the measured one (lt_ref/sarah.txt, 25 fps from 112.0 s)."""
    import ast
    import re
    fps, first, last = 25.0, 6, 161
    D = round((last - first + 1) / fps, 2)
    t = _kit("sarah", "Tercio con logo: anillo y dos líneas", "Logo lower third: ring and two lines", D, 8550,
             ["nombre", "cargo", "líneas", "anillo", "logo"], thumb_at=2.6)
    photo_bg(t, "h-city-01", s1=1.03, label="Tu video")
    from llt_motion import frames_of
    us = frames_of(D)
    ring, top_r, top_l, bot_r, bot_l, name_b, role_b = {}, {}, {}, {}, {}, {}, {}
    for line in (Path(__file__).with_name("lt_ref") / "sarah.txt").read_text(encoding="utf-8").splitlines():
        line = re.sub(r"np\.int64\((\d+)\)", r"\1", line)
        m = re.match(r"(\d+) ring (None|\(.*?\)) lines (\[.*?\]) white (\[.*\])", line)
        if not m:
            continue
        f = int(m.group(1))
        r = ast.literal_eval(m.group(2))
        if r:
            ring[f] = (r[1], r[3])
        for (y0, y1), x0, x1 in ast.literal_eval(m.group(3)):
            if y0 < 800:
                top_l[f], top_r[f] = x0, x1 + 1
            else:
                bot_l[f], bot_r[f] = x0, x1 + 1
        for y0, y1 in ast.literal_eval(m.group(4)):
            if y1 < 845:
                name_b[f] = y1
            else:
                role_b[f] = y1
    ring[160], ring[161] = (972, 987), (980, 980)
    fr = lambda u: first + u * fps  # noqa: E731

    def val(table, f, hidden):
        f = int(round(f))
        return table.get(f, hidden)
    CX, D0 = 403.5, 202.0
    disc = centered(CX, 786.5, D0, D0)
    motion = []
    for u in us:
        y0, y1 = ring.get(int(round(fr(u))), (999, 999))
        d = max(0.0, y1 - y0 + 1)
        motion.append((u, {"s": d / D0, "dy": (y0 + y1 + 1) / 2 - disc.cy}, "linear"))
    ringc = t.solid(t.track("shape", "Anillo"), RED, 0.0, D, disc, motion, kind="ellipse")
    ringc["name"] = "Anillo"
    track = next(tr for tr in t.tracks if ringc in tr.clips)
    t.mask(track, ringc, "ellipse", x=0.5, y=0.5, w=0.66, h=0.66, invert=True)
    lg = centered(CX, 786.5, 112, 112)
    t.photo(t.track("video", "Logo"), "logo-09", 0.0, D, lg, motion, label="Tu logo", brandRole="logo")
    rect_track(t, t.track("shape", "Línea arriba"), Box(480, 726, 712, 8),
               lambda u: (val(top_l, fr(u), 480), 726, val(top_r, fr(u), 480), 734), D, RED, name="Línea arriba")
    rect_track(t, t.track("shape", "Línea abajo"), Box(480, 846, 712, 6),
               lambda u: (val(bot_l, fr(u), 480), 846, val(bot_r, fr(u), 480), 851), D, RED, name="Línea abajo")
    name = "SARAH STROEMAN"
    nbox, nsize = caps_box(531, 746, 830, name)
    dyn = lambda u: val(name_b, fr(u), 700) - 830  # noqa: E731
    clip = name_text(t, name, nbox, nsize, D, bold_from="STROEMAN", spacing=-4.0, bold_spacing=4.1, word_spacing=6,
                     motion=[(u, {"dy": dyn(u)}, "linear") for u in us])
    role = "NEWS ANCHOR"
    rbox, rsize = caps_box(856, 859, 911, role)
    dyr = lambda u: val(role_b, fr(u), 820) - 911  # noqa: E731
    rclip = name_text(t, role, rbox, rsize, D, name="Cargo", spacing=-2.0, word_spacing=6,
                      motion=[(u, {"dy": dyr(u)}, "linear") for u in us])
    for c, b, top, dy in ((clip, nbox, 734.0, dyn), (rclip, rbox, 852.0, dyr)):
        track = next(tr for tr in t.tracks if c in tr.clips)
        mk = {"y": [], "h": []}
        for u in us:
            mk["y"].append((u, ((top + 1080) / 2 - b.y - dy(u)) / b.h, "linear"))
            mk["h"].append((u, (1080 - top) / b.h, "linear"))
        t.mask(track, c, "rectangle", x=0.5, y=mk["y"][0][1], w=4.0, h=mk["h"][0][1],
               keyframes={k: keys(v) for k, v in mk.items()})
    return t


# Gabriel Ballentine, measured frame by frame (25 fps from 118.4 s): the red bar's top and right end (it grows from a
# thin line on the bottom row), then the edge between white (left) and red (right) running right; out, the edge
# runs back left and the red's right end follows it in.
_GB_TOP = {9: 852, 10: 838, 11: 812, 12: 784, 13: 764, 14: 751, 15: 742, 16: 735, 17: 729, 18: 724, 19: 720, 20: 717,
           21: 715, 22: 713, 23: 711, 24: 710, 25: 709, 26: 708}
_GB_RIGHT = {9: 394, 10: 420, 11: 456, 12: 512, 13: 594, 14: 719, 15: 872, 16: 1005, 17: 1103, 18: 1178, 19: 1236,
             20: 1284, 21: 1324, 22: 1357, 23: 1386, 24: 1410, 25: 1432, 26: 1450, 27: 1466, 28: 1480, 29: 1493,
             30: 1504, 31: 1513, 32: 1522, 33: 1528, 34: 1534, 35: 1539, 36: 1542, 37: 1546, 38: 1548, 39: 1550,
             40: 1551, 43: 1552, 110: 1552, 114: 1551, 115: 1549, 116: 1544, 117: 1534, 118: 1520, 119: 1496,
             120: 1460, 121: 1408, 122: 1328, 123: 1199, 124: 1026, 125: 874, 126: 763, 127: 681, 128: 616, 129: 566,
             130: 523, 131: 488, 132: 458, 133: 432, 134: 410, 135: 391, 136: 374, 137: 360, 138: 348, 139: 338,
             140: 330, 141: 322, 142: 316, 143: 312, 144: 308, 145: 302}
_GB_EDGE = {30: 302, 31: 311, 32: 327, 33: 354, 34: 401, 35: 482, 36: 628, 37: 822, 38: 966, 39: 1062, 40: 1132,
            41: 1184, 42: 1226, 43: 1259, 44: 1286, 45: 1308, 46: 1326, 47: 1342, 48: 1354, 49: 1364, 50: 1372,
            51: 1378, 52: 1382, 53: 1386, 54: 1388, 110: 1388, 111: 1308, 112: 1274, 113: 1228, 114: 1164,
            115: 1072, 116: 959, 117: 850, 118: 763, 119: 696, 120: 640, 121: 596, 122: 558, 123: 526, 124: 498,
            125: 474, 126: 452, 127: 434, 128: 416, 129: 402, 130: 388, 131: 376, 132: 366, 133: 356, 134: 348,
            135: 340, 136: 333, 137: 328, 138: 322, 139: 318, 140: 314, 141: 310, 142: 308, 143: 306, 144: 304,
            145: 302}


def gabriel():
    """A thin red line on the bottom row grows up and out to the right into a bar; then white sweeps in from the left
    under the red name, the red pushed to a block at the right end. Out, the red sweeps back over the name and the
    bar runs back into its left end."""
    fps, first, last = 25.0, 9, 145
    D = round((last - first + 1) / fps, 2)
    t = _kit("gabriel", "Tercio con logo: barra roja que se vuelve blanca", "Logo lower third: red bar turning white", D, 8551,
             ["nombre", "barra", "rojo", "blanco", "logo"], thumb_at=2.6)
    photo_bg(t, "h-city-01", s1=1.03, label="Tu video")
    from llt_motion import frames_of
    fr = lambda u: first + u * fps  # noqa: E731
    top = _table(_GB_TOP, 852.0, 708.0)
    right = _table(_GB_RIGHT, 394.0, 302.0)
    edge_ = _table(_GB_EDGE, 302.0, 302.0)
    X0, Y1 = 302.0, 858.0
    area = Box(X0, 700, 1252, 160)
    rect_track(t, t.track("shape", "Barra blanca"), area, lambda u: (X0, 708, edge_(fr(u)), Y1), D, WHITE,
               name="Barra blanca")
    name = "GABRIEL BALLENTINE"
    nbox, nsize = caps_box(326, 718, 836, name)
    clip = name_text(t, name, nbox, nsize, D, bold_from=name, colour=RED, bold_spacing=3.4, word_spacing=6)
    mask_track(t, clip, nbox, lambda u: (X0, 708, edge_(fr(u)), Y1), D)
    rect_track(t, t.track("shape", "Barra roja"), area,
               lambda u: (edge_(fr(u)), top(fr(u)), right(fr(u)), Y1 + (1 if fr(u) < 26 else 0)), D, RED,
               name="Barra roja")
    # The white logo sits at the bar's right end and shows only where the red is.
    lg = Box(1412, 716, 116, 133)
    mark = t.photo(t.track("video", "Logo"), "logo-10", 0.0, D, lg, label="Tu logo", brandRole="logo")
    mask_track(t, mark, lg, lambda u: (edge_(fr(u)), top(fr(u)), right(fr(u)), Y1), D)
    return t


TEMPLATES = [francois, roger, jamie, charlotte, jason_e, jessica, david, neil, joanna, hendrick, bevan, janice, charlie,
             lizzie, patricia, jim, jason_f, lucas, brian, harry, sarah, gabriel]
