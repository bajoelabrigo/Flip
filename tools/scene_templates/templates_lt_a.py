"""Lower thirds with an orange-to-red gradient (2026-10-30), copied frame by frame from the reference video Jorge sent
(10834571.mp4: «lo más parecido posible, no inventes, fíjate las animaciones»). Positions, sizes and curves are the
ones measured on its 1920×1080 frames (see lt_motion.py); the names are placeholders the user edits. Wide type:
Anybody Expanded (fonts.extra). Order 8500-8529.
"""

from __future__ import annotations

from kit import Box, photo_bg, wide
from lt_motion import (Ref, caps_box, curve, fit_size, gradient_fill, out_of, run_where, slid_text, span, text,
                       track_span, track_text, typing)

WHITE = "#FFFFFF"


def _kit(id, es, en, dur, order, tags, **kw):
    return wide(f"lt-{id}", es, en, "ytkit", dur, order=order, tags=["kit:tercios-degradado", "tercio"] + tags, **kw)


def _pts(samples):
    return curve([(tt, v, "linear") for tt, v in samples])


def laura():
    """The bar opens to the right behind a white block that leads it; the role slides out from behind the bar's left
    edge; the name is typed letter by letter, each one growing from small and grey."""
    D = 5.0
    t = _kit("laura", "Tercio: nombre y barra degradada", "Lower third: name over a gradient bar", D, 8500,
             ["nombre", "degradado", "barra"], thumb_at=2.5)
    photo_bg(t, "h-portrait-02", s1=1.03, label="Tu video")
    r = Ref("laura")
    x0, bar = 195, Box(195, 850, 925, 50)
    grad = r.curve(Ref.edge("bar", "warm"), before=-1, after=bar.w + x0 - 1, offset=1 - x0)
    lead = r.curve(Ref.edge("bar", "white"), before=-1, after=bar.w + x0 - 1, offset=1 - x0)
    T = 1.25
    span(t, t.track("shape", "Barra"), bar, lambda u: 0.0, grad, D, T, 0.9, layers=gradient_fill(), name="Barra")
    role = "ADMISSIONS REPRESENTATIVE"
    size = fit_size(role, 801, 800)
    block = lambda f: min((r0 for r0, _ in f["bar"]["white"]), default=None)  # noqa: E731
    shift = r.curve(Ref.edge("sub", "white", below=block), before=-900 + 989, after=989, offset=-989)
    slid_text(t, role, caps_box(212, 875, size), size, lambda u: (shift(u), 0.0), D, T, 0.9, mask=bar, weight=800,
              name="Cargo")
    span(t, t.track("shape", "Borde"), bar, grad, lambda u: max(grad(u), lead(u)), D, T, 0.9, colour=WHITE,
         name="Borde")
    name = "LAURA CLARK"
    nsize = fit_size(name, 920, 900)
    ty = typing(stagger=0.06, grow=0.1, delay=0.0)
    text(t, name, caps_box(195, 801, nsize), nsize, weight=900, dur=D, anim_in=ty, anim_out=out_of(ty), name="Nombre")
    return t


def mari():
    """A white edge opens the bar to the right; the name slides out from behind its left edge inside it, then the
    role, under the bar, slides out from behind the same edge."""
    D = 5.9
    t = _kit("mari", "Tercio: nombre dentro de la barra", "Lower third: name inside the bar", D, 8501,
             ["nombre", "degradado", "caja"], thumb_at=2.5)
    photo_bg(t, "h-portrait-05", s1=1.03, label="Tu video")
    r = Ref("mari")
    x0, box = 196, Box(196, 769, 664, 111)
    grad = r.curve(Ref.edge("bar", "warm"), before=-1, after=box.w + x0 - 1, offset=1 - x0)
    lead = r.curve(Ref.edge("bar", "white"), before=-1, after=box.w + x0 - 1, offset=1 - x0)
    T = 1.15
    span(t, t.track("shape", "Caja"), box, lambda u: 0.0, grad, D, T, 1.0, layers=gradient_fill(), name="Caja")
    block = lambda f: min((r0 for r0, _ in f["bar"]["white"]), default=None)  # noqa: E731
    name, role = "MARI LUE", "GRAPHIC DESIGNER"
    nsize, rsize = fit_size(name, 620, 900), fit_size(role, 513, 800)
    nshift = r.curve(Ref.edge("title", "white", below=block), before="extrapolate", after=835, offset=-835)
    slid_text(t, name, caps_box(217, 822, nsize), nsize, lambda u: (nshift(u), 0.0), D, 1.6, 1.0, mask=box,
              name="Nombre")
    span(t, t.track("shape", "Borde"), box, grad, lambda u: max(grad(u), lead(u)), D, T, 1.0, colour=WHITE,
         name="Borde")
    rshift = r.curve(Ref.edge("sub", "white"), before=-600 + 706, after=706, offset=-706)
    slid_text(t, role, caps_box(196, 909, rsize), rsize, lambda u: (rshift(u), 0.0), D, 2.0, 1.0,
              mask=Box(196, 880, 1000, 60), weight=800, name="Cargo")
    return t


def _u(r, i):
    return (i - r.first) / 30.0


def endrue():
    """A white line draws across, then the box drops from it, a white band leading; the name and the role come down
    from the top inside it. A white line stays above and below the box."""
    r = Ref("endrue")
    D = round((163 - r.first) / 30 + 0.05, 2)
    t = _kit("endrue", "Tercio: caja con líneas blancas", "Lower third: box with white lines", D, 8502,
             ["nombre", "degradado", "caja", "líneas"], thumb_at=2.5)
    photo_bg(t, "h-man-05", s1=1.03, label="Tu video")
    y0, box = 753, Box(197, 753, 1029, 164)
    white = r.curve(Ref.edge("bar", "white"), before=y0 - 1, after=y0 - 1, offset=1 - y0)
    grad = r.curve(Ref.edge("bar", "warm"), before=759, after=759, offset=1 - y0)
    track_span(t, t.track("shape", "Líneas"), box, lambda u: 0.0, white, D, axis="y", colour=WHITE, name="Líneas")
    track_span(t, t.track("shape", "Caja"), box, lambda u: 7.0, grad, D, axis="y", layers=gradient_fill(), name="Caja")
    inside = lambda u: Box(box.x, 760, box.w, max(0.0, grad(u) + y0 - 760))  # noqa: E731
    name, role = "ENDRUE SCOTT", "PUBLIC RELATIONS SPECIALIST"
    nsize, rsize = fit_size(name, 994, 900), fit_size(role, 821, 800)
    ndy = r.curve(run_where("title", lo=764, hi=860), before="extrapolate", after="extrapolate", offset=-847)
    track_text(t, name, caps_box(214, 813.5, nsize), nsize, lambda u: (0.0, ndy(u)), D, mask=inside, name="Nombre")
    rdy = r.curve(run_where("title", lo=850, hi=905), before="extrapolate", after="extrapolate", offset=-885)
    track_text(t, role, caps_box(216, 879.5, rsize), rsize, lambda u: (0.0, rdy(u)), D, mask=inside, weight=800,
               name="Cargo")
    return t


def clara():
    """Like the box with lines, then the name rises out of the box while the box shrinks to a strip with the role
    rising into it; before leaving, it all goes back."""
    r = Ref("clara")
    D = round((189 - r.first) / 30 + 0.05, 2)
    t = _kit("clara", "Tercio: nombre que sale de la caja", "Lower third: name rising out of the box", D, 8503,
             ["nombre", "degradado", "caja", "franja"], thumb_at=2.9)
    photo_bg(t, "h-cafe-05", s1=1.03, label="Tu video")
    y0, box = 754, Box(510, 754, 900, 130)
    wtop = r.curve(Ref.edge("bar", "white", side="min"), before=y0, after=y0, offset=-y0)
    wbot = r.curve(Ref.edge("bar", "white"), before=y0 - 1, after=y0 - 1, offset=1 - y0)
    gtop = r.curve(Ref.edge("bar", "warm", side="min"), before=762, after=762, offset=-y0)
    gbot = r.curve(Ref.edge("bar", "warm"), before=761, after=761, offset=1 - y0)
    track_span(t, t.track("shape", "Líneas"), box, wtop, wbot, D, axis="y", colour=WHITE, name="Líneas")
    track_span(t, t.track("shape", "Caja"), box, gtop, gbot, D, axis="y", layers=gradient_fill(), name="Caja")
    name, role = "CLARA BUILD", "UI DEVELOPER"
    nsize, rsize = fit_size(name, 856, 900), fit_size(role, 375, 800)
    ndy = r.curve(run_where("title", lo=740, hi=862, side="min", pick="first"), before="extrapolate",
                  after="extrapolate", offset=-786)
    above = lambda u: Box(box.x, 600, box.w, max(0.0, gbot(u) + y0 - 600))  # noqa: E731
    track_text(t, name, caps_box(box.x, 816, nsize, box.w), nsize, lambda u: (0.0, ndy(u)), D, mask=above,
               align="center", name="Nombre")
    rdy = r.curve(run_where("sub", lo=836, hi=868, side="min"), before=60, after=60, offset=-842, frames=(62, 130))
    strip = lambda u: Box(box.x, gtop(u) + y0, box.w, max(0.0, gbot(u) - gtop(u)))  # noqa: E731
    track_text(t, role, caps_box(box.x, 851.5, rsize, box.w), rsize, lambda u: (0.0, rdy(u)), D, mask=strip,
               align="center", weight=800, name="Cargo")
    return t


TEMPLATES = [laura, mari, endrue, clara]
