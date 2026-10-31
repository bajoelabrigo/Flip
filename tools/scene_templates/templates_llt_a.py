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


TEMPLATES = [francois, roger, jamie, charlotte, jason_e]
