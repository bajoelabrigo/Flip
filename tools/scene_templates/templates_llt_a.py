"""Logo lower thirds (2026-10-31), copied frame by frame from the second reference Jorge sent (15488414.mp4, 24 lower
thirds with a logo: «lo más parecido posible, casi iguales»). Every bar and edge plays its measured curve
(lt_ref/<name>.json, 25 fps scaled to 1080p); texts sit where the reference has them; the logo is a slot («Tu
logo»), shown with the app's premium flame as the sample (logo-09…14, Jorge: «el logo es el del fuego»). Order 8530-8569.
"""

from __future__ import annotations

import math

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


TEMPLATES = [francois, roger, jamie, charlotte, jason_e, jessica, david, neil, joanna, hendrick, bevan, janice]
