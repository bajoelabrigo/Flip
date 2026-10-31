"""Lower thirds with an orange-to-red gradient, second half (2026-10-30): the other eight of the reference video Jorge
sent (10834571.mp4), copied frame by frame like templates_lt_a: every bar is the measured one (lt_ref/*.json, one
key a frame), every text sits where the reference has it and moves as it does. Order 8504-8529.
"""

from __future__ import annotations

from kit import Box, photo_bg, wide
from lt_motion import (FPS, Ref, caps_box, fit_size, frame_at, last_frame, measured_bar, out_of, outline_layers, text,
                       track_text, typing)

WHITE = "#FFFFFF"
GREY = "#818181"


def _kit(id, es, en, dur, order, tags, **kw):
    return wide(f"lt-{id}", es, en, "ytkit", dur, order=order, tags=["kit:tercios-degradado", "tercio"] + tags, **kw)


def _dur(r):
    return round((last_frame(r) - r.first + 2) / FPS, 2)


def _runs(r, u, band, kind="white"):
    f = frame_at(r, u)
    return f[band][kind] if f else []


def _measured(r, value, hidden, frames=None):
    """offset(u) from value(frame) (None = not measured: `hidden`), limited to frame indexes `frames`."""
    def off(u):
        i = r.first + int(round(u * FPS))
        if frames and not frames[0] <= i <= frames[1]:
            return hidden
        f = frame_at(r, u)
        v = value(f) if f else None
        return hidden if v is None else v
    return off


def _typing_backward(stagger, grow, delay):
    return typing(stagger=stagger, grow=grow, order="backward", delay=delay)


# --- Kerry: a vertical bar, the name outlined -------------------------------------------------------------------------

def kerry():
    """A short gradient bar rises from the bottom behind a white cap; the name, outlined, rises next to it; the role's
    two words come up after it."""
    r = Ref("kerry", first=0)
    D = _dur(r)
    t = _kit("kerry", "Tercio: barra vertical y nombre contorneado", "Lower third: vertical bar, outlined name", D, 8504,
             ["nombre", "contorno", "barra vertical"], thumb_at=2.5)
    photo_bg(t, "h-sport-02", s1=1.03, label="Tu video")
    measured_bar(t, r, "bar", Box(196, 744, 50, 150), axis="y")
    name = "KERRY LEE"
    size = fit_size(name, 703, 900)

    def name_dy(f):
        rs = [a for a, b in f["title"]["white"] if 745 <= a <= 800]
        return rs[0] - 757 if rs else None
    track_text(t, name, caps_box(264, 793, size), size, lambda u: (0.0, _measured(r, name_dy, 80.0)(u)), D,
               mask=lambda u: Box(250, 600, 1000, 232), layers=outline_layers(3.0), name="Nombre")
    rsize = fit_size("WEB DEVELOPER", 456, 800)
    word_in = {"WEB": [(20, 30.0), (21, 15.0), (22, 0.0)], "DEVELOPER": [(26, 30.0), (28, 12.0), (29, 4.0), (31, 0.0)]}
    word_out = {"WEB": 142, "DEVELOPER": 135}
    for word, x in (("WEB", 262), ("DEVELOPER", 410)):
        pts = word_in[word]
        end = word_out[word]

        def dy(u, pts=pts, end=end):
            i = r.first + u * FPS
            k = pts[-1][0] - (i - end) if i > end else i  # the exit is the entrance backwards
            if k <= pts[0][0]:
                return pts[0][1]
            for (a, va), (b, vb) in zip(pts, pts[1:]):
                if k <= b:
                    return va + (vb - va) * (k - a) / (b - a)
            return 0.0
        track_text(t, word, caps_box(x, 868.5, rsize), rsize, lambda u, dy=dy: (0.0, dy(u)), D,
                   mask=lambda u: Box(250, 800, 1000, 86), weight=800, name="Cargo" if word == "WEB" else "Cargo 2")
    return t


# --- Andy: the bar opens from the middle, the name typed and re-centred -------------------------------------------------

def andy():
    """A white line in the middle opens both ways into the bar; the name is typed letter by letter, each one rising
    from under the bar's bottom edge, the line re-centring as it grows; the role drops from behind the bar."""
    r = Ref("andy")
    D = _dur(r)
    t = _kit("andy", "Tercio: barra que se abre desde el centro", "Lower third: bar opening from the middle", D, 8505,
             ["nombre", "centrado", "degradado"], thumb_at=2.5)
    photo_bg(t, "h-podcast-02", s1=1.03, label="Tu video")
    box = Box(498, 759, 924, 110)
    measured_bar(t, r, "bar", box)
    name = "ANDY SCOTT"
    size = fit_size(name, 881, 900)
    ty = {"animators": [
        {"selectors": [{"driver": "stagger", "domain": "chars", "staggerUs": 70000, "durationUs": 0, "order": "forward",
                        "ease": "linear"}], "props": {"opacity": 0}, "collapseHidden": True},
        {"selectors": [{"driver": "stagger", "domain": "chars", "staggerUs": 70000, "durationUs": 180000,
                        "order": "forward", "ease": "easeOut"}], "props": {"position": {"x": 0, "y": 80, "unit": "px"}}}],
        "delayUs": 870000}
    end = (148 - r.first) / FPS
    clip = text(t, name, caps_box(box.x, 813.5, size, box.w), size, align="center", dur=end, anim_in=ty,
                anim_out=out_of(ty), name="Nombre", mask=box)
    role = "MULTIMEDIA ANIMATOR"
    rsize = fit_size(role, 608, 800)

    def role_dy(f):
        rs = [a for a, b in f["sub"]["white"] if a >= 869]
        return rs[0] - 886 if rs else None
    track_text(t, role, caps_box(box.x, 899.5, rsize, box.w), rsize, lambda u: (0.0, _measured(r, role_dy, -60.0)(u)), D,
               mask=lambda u: Box(400, 869, 1200, 200), align="center", weight=800, name="Cargo")
    return t


# --- Elizabeth: the name in three looks, the surname out of the box ---------------------------------------------------

def eliza():
    """«ELIZA» typed in white, «B» in grey, «ETH» outlined; under it the role's box opens to the left and the surname
    slides out from behind its right edge."""
    r = Ref("eliza", first=0)
    D = _dur(r)
    t = _kit("eliza", "Tercio: nombre en tres estilos", "Lower third: name in three styles", D, 8506,
             ["nombre", "contorno", "apellido"], thumb_at=2.6)
    photo_bg(t, "h-office-05", s1=1.03, label="Tu video")
    box = Box(518, 894, 442, 76)
    measured_bar(t, r, "box", box)
    size = fit_size("ELIZA", 360, 900)
    parts = [("ELIZA", 519, None, 0.0, 0.1), ("B", 881, GREY, 0.5, 0.1), ("ETH", 971, "outline", 0.6, 0.1)]
    for word, x, look, delay, stagger in parts:
        layers = outline_layers(3.0) if look == "outline" else None
        ty = typing(stagger=stagger, grow=0.15, delay=delay)
        text(t, word, caps_box(x, 835.5, size), size, colour=GREY if look == GREY else WHITE, dur=D, anim_in=ty,
             anim_out=out_of(ty), layers=layers, name={"ELIZA": "Nombre", "B": "Nombre 2", "ETH": "Nombre 3"}[word])
    rsize = fit_size("IT MANAGER", 327, 800)

    def grad_left(u):
        rs = _runs(r, u, "box", "warm")
        return min(a for a, b in rs) if rs else 960.0
    track_text(t, "IT MANAGER", caps_box(box.x, 931.5, rsize, 944 - box.x, "left"), rsize, lambda u: (0.0, 0.0), D,
               mask=lambda u: Box(grad_left(u), box.y, max(0.0, 960 - grad_left(u)), box.h), align="right", weight=800,
               name="Cargo")
    asize = fit_size("ARDEN", 438, 900)

    def arden_dx(f):
        rs = [b for a, b in f["arden"]["white"] if a >= 962]
        return max(rs) - 1413 if rs else None
    track_text(t, "ARDEN", caps_box(976, 931.5, asize), asize, lambda u: (_measured(r, arden_dx, -500.0)(u), 0.0), D,
               mask=lambda u: Box(960, 880, 700, 120), name="Apellido")
    return t


# --- Morgan: the surname in the box, the name above, the role below -------------------------------------------------------

def morgan():
    """The box opens from the middle with the surname's letters closing in; the name rises from behind its top edge
    and the role drops from behind its bottom one."""
    r = Ref("morgan", first=0)
    D = _dur(r)
    t = _kit("morgan", "Tercio: apellido en caja, nombre encima", "Lower third: surname in a box, name above", D, 8507,
             ["nombre", "apellido", "centrado"], thumb_at=2.6)
    photo_bg(t, "h-man-03", s1=1.03, label="Tu video")
    box = Box(622, 833, 676, 110)
    measured_bar(t, r, "bar", box)
    sur = "KETZNER"
    ssize = fit_size(sur, 616, 900)

    def ketz_width(f):
        rs = [x for x in f["ketz"]["white"] if box.x + 4 <= x[0] and x[1] <= box.x + box.w - 4]
        return (max(b for a, b in rs) - min(a for a, b in rs)) if len(rs) > 2 else None
    widths = [(i, ketz_width(r.frames[i])) for i in range(len(r.frames))]
    spread = {i: (w - 616) / 6.0 for i, w in widths if w is not None}

    def tracking(u):
        i = r.first + int(round(u * FPS))
        if i in spread:
            return max(0.0, spread[i])
        return 0.0
    from scene import keys
    clip = track_text(t, sur, caps_box(box.x, 884.5, ssize, box.w), ssize, lambda u: (0.0, 0.0), D,
                      mask=lambda u: box, align="center", name="Apellido")
    clip["textStyle"]["keyframes"] = {"letterSpacing": keys([(u, tracking(u), "linear") for u in
                                                              [k / FPS for k in range(int(D * FPS) + 1)]])}
    nsize = fit_size("MORGAN", 580, 800)

    def name_dy(f):
        rs = [b for a, b in f["morgan"]["white"] if b <= 832]
        return rs[-1] - 815 if rs else None
    track_text(t, "MORGAN", caps_box(box.x, 779.5, nsize, box.w), nsize, lambda u: (0.0, _measured(r, name_dy, 90.0)(u)),
               D, mask=lambda u: Box(500, 600, 1000, 233), align="center", weight=800, name="Nombre")
    rsize = fit_size("ASSISTANT BUYER", 500, 800)

    def role_dy(f):
        rs = [a for a, b in f["sub"]["white"] if a >= 944]
        return rs[0] - 958 if rs else None
    track_text(t, "ASSISTANT BUYER", caps_box(box.x, 971.5, rsize, box.w), rsize,
               lambda u: (0.0, _measured(r, role_dy, -60.0)(u)), D, mask=lambda u: Box(500, 943, 1000, 120),
               align="center", weight=800, name="Cargo")
    return t


# --- Kim: a thin strip, the role on it, the name dropping under it ------------------------------------------------------

def kim():
    """A white line drops into a strip with the role in it; the strip thins and the role rises above it; the name
    drops from behind the strip."""
    r = Ref("kim")
    D = _dur(r)
    t = _kit("kim", "Tercio: franja con cargo y nombre debajo", "Lower third: strip with role, name below", D, 8508,
             ["nombre", "franja", "derecha"], thumb_at=2.8)
    photo_bg(t, "h-office-02", s1=1.03, label="Tu video")
    strip = Box(1178, 788, 558, 56)
    measured_bar(t, r, "strip", strip, axis="y")

    def strip_bottom(u):
        rs = _runs(r, u, "strip", "warm")
        return max(b for a, b in rs) + 1 if rs else strip.y
    rsize = fit_size("FASHION DESIGNER", 506, 800)

    def role_dy(f):
        rs = [a for a, b in f["fashion"]["white"] if 778 <= a <= 802 and b - a > 18 and b <= 830]
        return rs[0] - 782 if rs else None
    phase = _measured(r, role_dy, 18.0, frames=(45, 145))
    track_text(t, "FASHION DESIGNER", caps_box(1212, 795, rsize), rsize, lambda u: (0.0, phase(u)), D,
               mask=lambda u: Box(1150, 600, 700, strip_bottom(u) - 600), weight=800, name="Cargo")
    nsize = fit_size("KIM YUL", 542, 900)

    def name_dy(f):
        rs = [b for a, b in f["kim"]["white"] if a >= 846]
        return rs[-1] - 926 if rs else None
    track_text(t, "KIM YUL", caps_box(1184, 892, nsize), nsize, lambda u: (0.0, _measured(r, name_dy, -90.0)(u)), D,
               mask=lambda u: Box(1150, 844, 700, 200), name="Nombre")
    return t


# --- Helen: right-aligned, two boxes opening to the left --------------------------------------------------------------

def helen():
    """Two boxes open to the left from the right edge, a white block leading each; the name and the role slide in
    from the right inside them."""
    r = Ref("helen")
    D = _dur(r)
    t = _kit("helen", "Tercio a la derecha: dos cajas", "Lower third on the right: two boxes", D, 8509,
             ["nombre", "derecha", "cajas"], thumb_at=2.6)
    photo_bg(t, "h-portrait-03", s1=1.03, label="Tu video")
    big, small = Box(784, 748, 1048, 110), Box(1298, 873, 535, 50)
    measured_bar(t, r, "big", big)
    measured_bar(t, r, "small", small, name="Caja 2")

    def left_of_text(band, lead_band):
        def fn(f):
            lead = f[lead_band]["white"]
            lead_end = max((b for a, b in lead), default=0)
            rs = [a for a, b in f[band]["white"] if a > lead_end + 2]
            return min(rs) if rs else None
        return fn
    size = fit_size("HELEN MARLEN", 994, 900)
    ndx = _measured(r, lambda f: (lambda v: None if v is None else v - 809)(left_of_text("title", "big")(f)), 1100.0)
    track_text(t, "HELEN MARLEN", caps_box(809, 802.5, size), size, lambda u: (ndx(u), 0.0), D, mask=lambda u: big,
               name="Nombre")
    rsize = fit_size("WEDDING STYLIST", 492, 800)
    rdx = _measured(r, lambda f: (lambda v: None if v is None else v - 1313)(left_of_text("sub", "small")(f)), 600.0)
    track_text(t, "WEDDING STYLIST", caps_box(1313, 897.5, rsize), rsize, lambda u: (rdx(u), 0.0), D,
               mask=lambda u: small, weight=800, name="Cargo")
    return t


# --- Ronald and Victoria: typed from the right ------------------------------------------------------------------------

def ronald():
    """Right-aligned: the name typed from its last letter back, each letter growing from small and grey; the role's
    box opens to the left behind a white block and its letters type in the same way."""
    r = Ref("ronald")
    D = _dur(r)
    t = _kit("ronald", "Tercio a la derecha: escrito hacia atrás", "Lower third on the right: typed backwards", D, 8510,
             ["nombre", "derecha", "escritura"], thumb_at=2.6)
    photo_bg(t, "h-man-04", s1=1.03, label="Tu video")
    box = Box(1045, 850, 775, 50)
    measured_bar(t, r, "box", box)
    size = fit_size("RONALD JOYCE", 989, 900)
    ty = _typing_backward(0.073, 0.15, 0.2)
    text(t, "RONALD JOYCE", caps_box(1820, 799.5, size, 1400, "right"), size, align="right", dur=D, anim_in=ty,
         anim_out=out_of(ty), name="Nombre")
    rsize = fit_size("CLIENT SERVICES MANAGER", 746, 800)
    ty2 = _typing_backward(0.055, 0.15, 0.3)
    text(t, "CLIENT SERVICES MANAGER", caps_box(1804, 875.5, rsize, 1200, "right"), rsize, align="right", weight=800,
         dur=D, anim_in=ty2, anim_out=out_of(ty2), name="Cargo")
    return t


def victoria():
    """Right-aligned: the name typed from its last letter back over a gradient line that opens to the left; the role
    under it typed the same way."""
    r = Ref("victoria")
    D = _dur(r)
    t = _kit("victoria", "Tercio a la derecha: línea degradada", "Lower third on the right: gradient line", D, 8511,
             ["nombre", "derecha", "línea"], thumb_at=2.6)
    photo_bg(t, "h-portrait-06", s1=1.03, label="Tu video")
    measured_bar(t, r, "line", Box(800, 836, 1020, 16))
    size = fit_size("VICTORIA LUISE", 1020, 900)
    ty = _typing_backward(0.06, 0.15, 0.15)
    text(t, "VICTORIA LUISE", caps_box(1822, 786, size, 1400, "right"), size, align="right", dur=D, anim_in=ty,
         anim_out=out_of(ty), name="Nombre")
    rsize = fit_size("MULTIMEDIA ANIMATOR", 608, 800)
    ty2 = _typing_backward(0.045, 0.15, 0.45)
    text(t, "MULTIMEDIA ANIMATOR", caps_box(1821, 879.5, rsize, 1200, "right"), rsize, align="right", weight=800,
         dur=D, anim_in=ty2, anim_out=out_of(ty2), name="Cargo")
    return t


TEMPLATES = [kerry, andy, eliza, morgan, kim, helen, ronald, victoria]
