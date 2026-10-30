"""Kit de YouTube, batch f (2026-10-30): «Suscríbete en la página». Jorge brought a commercial promo where the
video zooms out into a video page and a cursor subscribes; this is our own take on that idea (no platform logo or
red, the kit's palette, every text and picture editable): the user's video full screen, the page builds around it,
the cursor clicks Subscribe, the button turns into «🔔 Subscribed ⌄» as on the real page, a click on it opens the
notifications menu, «All» is picked and the bell rings, and the video zooms back to full screen so the piece can
sit in the middle of any video. Laid out after the real watch page (Jorge's screenshot, 2026-10-30): search bar in
the middle, the video with even margins, title, channel row with the button beside the name and the actions on
the right edge, description boxes, chips and a recommended column. Dark and light (16:9) and the phone app (9:16).
Section elementos; order 8150-8199.
"""

from __future__ import annotations

import math

from kit import Box, centered, fill, keys, label, no_stroke, rrect, shadow, tall, tanim, wide
from templates_ytkit_a import BELL, CURSOR, OUT, _stroke, path

TEAL = "#2EE6C8"
CORAL = "#FF5D73"
WHITE = "#FFFFFF"

THEMES = {
    "oscura": dict(page="#0F0F10", card="#272727", soft_card="#1F1F1F", ink="#F1F1F1", soft="#AAAAAA",
                   cta="#F1F1F1", cta_ink="#0F0F0F", done="#272727", menu="#282828", badge="#000000"),
    "clara": dict(page="#FFFFFF", card="#F2F2F2", soft_card="#F2F2F2", ink="#0F0F0F", soft="#606060",
                  cta="#0F0F0F", cta_ink="#FFFFFF", done="#F2F2F2", menu="#FFFFFF", badge="#000000"),
}

ZOOM_OUT = (1.2, 2.2)   # the video leaves full screen
ZOOM_IN = (7.6, 8.4)    # and comes back
DUR = 9.0
CHEVRON = "M 0 0 L 50 55 L 100 0"
UI_AT = ZOOM_OUT[1] - 0.3
UI_UNTIL = ZOOM_IN[0] + 0.1


def _kit(id, es, en, order, tags, vertical=False, **kw):
    make = tall if vertical else wide
    return make(f"ytk-{id}", es, en, "ytkit", DUR, order=order,
                tags=["kit:elementos", "youtube"] + (["vertical"] if vertical else []) + tags, **kw)


def _ui(at=UI_AT, until=UI_UNTIL, lag=0.0):
    """Opacity of the page around the video: in after the zoom out, out before the zoom in."""
    at += lag
    return keys([(0, 0.0, "hold"), (at, 0.0, "out"), (at + 0.35, 1.0, "hold"), (until - 0.3, 1.0, "in"), (until, 0.0)])


def _video_motion(box: Box, frame_w: float, frame_h: float):
    """The video slot: full screen at first (scaled to cover the frame), into its box on the page, and back."""
    s = max(frame_w / box.w, frame_h / box.h)
    full = {"s": s, "dx": frame_w / 2 - (box.x + box.w / 2), "dy": frame_h / 2 - (box.y + box.h / 2)}
    a, b = ZOOM_OUT
    c, d = ZOOM_IN
    return [(0, full, "hold"), (a, full, "inout"), (b, {}, "hold"), (c, {}, "inout"), (d, full, "hold")]


class Page:
    """Adds the page's pieces with the page's fade, a track per kind so the timeline reads clearly."""

    def __init__(self, t, theme):
        self.t, self.th = t, theme
        self.tracks = {}

    def _tr(self, kind, name):
        key = (kind, name)
        tr = self.tracks.get(key)
        if tr is None or len(tr.clips) >= 8:
            tr = self.t.track(kind, name)
            self.tracks[key] = tr
        return tr

    def block(self, box, colour=None, radius=10, name="Página", lag=0.0, **extra):
        return rrect(self.t, self._tr("shape", name), colour or self.th["card"], 0.0, DUR, box, radius=radius,
                     opacity=_ui(lag=lag), **extra)

    def circle(self, cx, cy, d, colour=None, name="Página", lag=0.0):
        return self.t.solid(self._tr("shape", name), colour or self.th["card"], 0.0, DUR, centered(cx, cy, d, d),
                            kind="ellipse", opacity=_ui(lag=lag))

    def icon(self, d, box, colour=None, width=4, filled=False, name="Iconos", lag=0.0):
        c = colour or self.th["ink"]
        layers = [fill(c), no_stroke()] if filled else \
            [{"id": "fill", "kind": "fill", "enabled": False, "paint": {"kind": "solid", "color": "#00000000"}},
             _stroke(c, width)]
        return path(self.t, self._tr("shape", name), c, 0.0, DUR, box, d, layers=layers, opacity=_ui(lag=lag))

    def text(self, content, box, size, colour=None, weight=400, name=None, editable=True, align="left",
             font="Inter", lag=0.0):
        return label(self.t, self._tr("text", name or "Textos"), content, 0.0, DUR, box, font, size,
                     colour or self.th["ink"], weight=weight, align=align, opacity=_ui(lag=lag), name=name or content,
                     editable=editable)


def _circle(cx, cy, r):
    """A circle as four cubic curves: custom outlines take M, L, C, Q and Z only (absolute)."""
    k = 0.5523 * r
    return (f"M {cx + r} {cy} C {cx + r} {cy + k} {cx + k} {cy + r} {cx} {cy + r} "
            f"C {cx - k} {cy + r} {cx - r} {cy + k} {cx - r} {cy} C {cx - r} {cy - k} {cx - k} {cy - r} {cx} {cy - r} "
            f"C {cx + k} {cy - r} {cx + r} {cy - k} {cx + r} {cy} Z")

SEARCH = _circle(40, 40, 30) + " M 62 62 L 95 95"
MIC = "M 35 10 L 65 10 L 65 55 L 35 55 Z M 20 45 C 20 85 80 85 80 45 M 50 75 L 50 95"
MENU = "M 0 10 L 100 10 M 0 50 L 100 50 M 0 90 L 100 90"
DOTS3 = " ".join(_circle(x, 50, 9) for x in (10, 50, 90))

SHARE = "M 55 15 L 95 50 L 55 85 L 55 65 C 30 65 15 75 5 90 C 10 55 30 38 55 35 Z"
SAVE = "M 20 5 L 80 5 L 80 95 L 50 72 L 20 95 Z"
THUMB = "M 30 45 L 50 8 C 60 8 64 16 62 26 L 58 40 L 88 40 C 96 40 100 48 98 56 L 90 88 C 88 94 84 96 78 96 " \
        "L 30 96 Z M 5 45 L 22 45 L 22 96 L 5 96 Z"


def _subscribe(t, th, btn: Box, done_w: float, menu_box: Box, cursor_from, size, vertical=False, compact=False,
               tap=False, menu_radius=14, like=None, count=None):
    """Subscribe → «🔔 Subscribed ⌄»; Like (the thumb fills, pops and sparks; the count goes up); a click on the
    subscribed button opens the menu; «All»; the bell in the button rings. like = (cx, cy, size) of the page's
    thumb icon; count = (box, before, after, size) for the likes next to it."""
    click1, clike, click2, click3 = 3.4, 4.3, 5.2, 6.1
    end = UI_UNTIL - 0.1
    done = Box(btn.x, btn.y, done_w, btn.h)
    r = btn.h / 2
    # Subscribe: white on the dark page, black on the light one, as on the real page.
    rrect(t, t.track("shape", "Botón"), th["cta"], 0.0, click1 + 0.12, btn, radius=r,
          motion=[(0, {}, "hold"), (click1, {}, "out"), (click1 + 0.12, {"s": 0.94})], opacity=_ui())
    label(t, t.track("text", "Botón"), "Suscribirse", 0.0, click1 + 0.1, btn, "Inter", size, th["cta_ink"],
          weight=600, opacity=_ui(), name="Botón")
    # Subscribed: grey, with the bell and the arrow.
    keep = keys([(0, 1.0, "hold"), (end - click1 - 0.4, 1.0, "in"), (end - click1 - 0.1, 0.0)])
    rrect(t, t.track("shape", "Botón"), th["done"], click1 + 0.1, end - click1 - 0.1, done, radius=r,
          motion=[(0, {"s": 0.94}, "back"), (0.25, {})], opacity=keep)
    bell_s = btn.h * 0.46
    bell_c = (done.x + r * 0.95, done.y + btn.h / 2)
    wob = [(0, 0, "hold"), (click3 + 0.25 - click1, 0, "smooth"), (click3 + 0.35 - click1, 22, "smooth"),
           (click3 + 0.45 - click1, -20, "smooth"), (click3 + 0.55 - click1, 15, "smooth"),
           (click3 + 0.65 - click1, -10, "smooth"), (click3 + 0.75 - click1, 5, "smooth"), (click3 + 0.85 - click1, 0)]
    path(t, t.track("shape", "Campana"), th["ink"], click1 + 0.15, end - click1 - 0.15,
         centered(bell_c[0], bell_c[1], bell_s, bell_s * 1.08), BELL, filled=True, rotation=keys(wob),
         opacity=keys([(0, 0.0), (0.2, 1.0, "hold"), (end - click1 - 0.45, 1.0, "in"), (end - click1 - 0.15, 0.0)]))
    t.solid(t.track("shape", "Aviso"), TEAL, click3 + 0.25, end - click3 - 0.25,
            centered(bell_c[0] + bell_s * 0.45, bell_c[1] - bell_s * 0.45, bell_s * 0.36, bell_s * 0.36),
            [(0, {"s": 0.0}, "back"), (0.3, {})], kind="ellipse",
            opacity=keys([(0, 1.0, "hold"), (end - click3 - 0.55, 1.0, "in"), (end - click3 - 0.25, 0.0)]))
    # The phone app shows only the bell and the arrow in the button once subscribed.
    if not compact:
        text_box = Box(done.x + r * 1.7, done.y, done_w - r * 1.7 - r * 1.3, btn.h)
        label(t, t.track("text", "Botón"), "Suscrito", click1 + 0.15, end - click1 - 0.15, text_box, "Inter", size,
              th["ink"], weight=600, anim_in=tanim("fade", duration=0.2), anim_out=OUT(0.25), name="Botón tras el clic")
    chev = btn.h * 0.24
    path(t, t.track("shape", "Flecha"), th["ink"], click1 + 0.15, end - click1 - 0.15,
         centered(done.x + done_w - r * 0.85, done.y + btn.h / 2 + 1, chev, chev * 0.6), CHEVRON, width=3,
         opacity=keys([(0, 0.0), (0.2, 1.0, "hold"), (end - click1 - 0.45, 1.0, "in"), (end - click1 - 0.15, 0.0)]),
         layers=[{"id": "fill", "kind": "fill", "enabled": False, "paint": {"kind": "solid", "color": "#00000000"}},
                 _stroke(th["ink"], 3)])
    # Ripples where the first click lands.
    for i, c in enumerate([TEAL, WHITE]):
        t.solid(t.track("shape", "Onda"), c, click1 + i * 0.08, 0.6, centered(btn.x + btn.w * 0.55, btn.y + btn.h / 2, 70, 70),
                [(0, {"s": 0.2}, "out"), (0.6, {"s": 3.0})], kind="ellipse",
                layers=[{"id": "fill", "kind": "fill", "enabled": False, "paint": {"kind": "solid", "color": "#00000000"}},
                        _stroke(c, 4, "inside")], opacity=keys([(0, 1.0), (0.6, 0.0)]))

    # Like: the thumb fills in and pops, sparks fly off it, and the count goes up.
    if like:
        lx, ly, ls = like
        lend = end - clike
        path(t, t.track("shape", "Me gusta"), th["ink"], clike, lend, centered(lx, ly, ls, ls), THUMB, filled=True,
             motion=[(0, {"s": 0.6}, "out"), (0.12, {"s": 1.35}, "back"), (0.42, {})],
             opacity=keys([(0, 1.0, "hold"), (lend - 0.3, 1.0, "in"), (lend, 0.0)]))
        for i in range(8):
            ang = math.radians(i * 45 + 22.5)
            far = ls * 1.5
            c = [TEAL, CORAL, "#FFD23F"][i % 3]
            t.solid(t.track("shape", "Chispas"), c, clike + 0.05, 0.5, centered(lx, ly, ls * 0.2, ls * 0.2),
                    [(0, {"s": 0.4}, "out"), (0.5, {"dx": math.cos(ang) * far, "dy": math.sin(ang) * far, "s": 0.0})],
                    kind="ellipse")
        t.solid(t.track("shape", "Chispas"), TEAL, clike, 0.5, centered(lx, ly, ls, ls), [(0, {"s": 0.5}, "out"), (0.5, {"s": 2.4})],
                kind="ellipse", layers=[{"id": "fill", "kind": "fill", "enabled": False,
                                         "paint": {"kind": "solid", "color": "#00000000"}}, _stroke(TEAL, 3, "inside")],
                opacity=keys([(0, 1.0), (0.5, 0.0)]))
        if count:
            box, before, after, csize = count
            label(t, t.track("text", "Me gusta"), before, 0.0, clike + 0.05, box, "Inter", csize, th["ink"], weight=600,
                  align="left", opacity=_ui(), anim_out=tanim("fade", duration=0.1), name="Me gusta antes")
            label(t, t.track("text", "Me gusta"), after, clike + 0.05, end - clike - 0.05, box, "Inter", csize, th["ink"],
                  weight=600, align="left", anim_in=tanim("slide-up", duration=0.25), anim_out=OUT(0.25),
                  name="Me gusta después")

    # The notifications menu, above the button (the page ends just below it).
    open_at, close_at = click2 + 0.1, click3 + 0.2
    mdur = close_at - open_at
    # A card that pops up over the button, or (phone) a sheet that rises from the bottom.
    rise = [(0, {"dy": menu_box.h}, "out"), (0.25, {}, "hold"), (mdur - 0.2, {}, "in"), (mdur, {"dy": menu_box.h})]
    pop_up = [(0, {"s": 0.9, "dy": 12}, "out"), (0.2, {}, "hold"), (mdur - 0.15, {}, "in"), (mdur, {"s": 0.94})]
    if tap:
        # The phone dims the page behind the sheet.
        t.solid(t.track("shape", "Oscurecer"), "#000000", open_at, mdur, None,
                opacity=keys([(0, 0.0), (0.25, 0.45, "hold"), (mdur - 0.2, 0.45), (mdur, 0.0)]))
    rrect(t, t.track("shape", "Menú"), th["menu"], open_at, mdur, menu_box, radius=menu_radius,
          motion=rise if tap else pop_up,
          layers=[shadow("#000000", 0, 10, 28, 0.45), fill(th["menu"]), no_stroke()],
          opacity=keys([(0, 0.0), (0.15, 1.0, "hold"), (mdur - 0.15, 1.0), (mdur, 0.0)]))
    items = [("Todas", "Menú: todas"), ("Personalizadas", "Menú: personalizadas"), ("Ninguna", "Menú: ninguna"),
             ("Anular suscripción", "Menú: anular")]
    row_h = (menu_box.h - 16) / len(items)
    hi = Box(menu_box.x, menu_box.y + 8, menu_box.w, row_h)
    rrect(t, t.track("shape", "Menú"), th["card"] if th["menu"] != th["card"] else th["soft_card"], click3 - 0.35,
          close_at - (click3 - 0.35), hi, radius=0, opacity=keys([(0, 0.0), (0.15, 1.0)]))
    isz = row_h * 0.42
    for i, (text, name) in enumerate(items):
        y = menu_box.y + 8 + i * row_h
        if i < 3:
            path(t, t.track("shape", "Menú"), th["ink"], open_at + 0.05, mdur - 0.05,
                 centered(menu_box.x + 26 + isz / 2, y + row_h / 2, isz, isz * 1.08), BELL, filled=(i == 0),
                 width=3, layers=None if i == 0 else
                 [{"id": "fill", "kind": "fill", "enabled": False, "paint": {"kind": "solid", "color": "#00000000"}},
                  _stroke(th["ink"], 3)],
                 opacity=keys([(0, 0.0), (0.15, 1.0)]))
        label(t, t.track("text", "Menú"), text, open_at + 0.05, mdur - 0.05,
              Box(menu_box.x + 40 + isz, y, menu_box.w - 56 - isz, row_h), "Inter", size, th["ink"],
              weight=400, align="left", anim_in=tanim("fade", duration=0.2), anim_out=OUT(0.15), name=name)

    # The cursor: to the button, to the subscribed button, up to «All», away.
    tip = (btn.x + btn.w * 0.58, btn.y + btn.h * 0.62)
    to_done = (done.x + done_w * 0.55 - tip[0], 0)
    to_like = (like[0] - tip[0], like[1] - tip[1]) if like else to_done
    to_all = (menu_box.x + menu_box.w * 0.35 - tip[0], menu_box.y + 8 + row_h * 0.55 - tip[1])
    t0 = 2.6
    cs = 0.82
    cw = 40 if not vertical else 54

    def at(x):
        return x - t0
    m = [(0, {"dx": cursor_from[0], "dy": cursor_from[1]}, "out"), (at(click1 - 0.15), {}, "hold"),
         (at(click1), {"s": cs}, "out"), (at(click1 + 0.15), {}, "inout"),
         (at(clike - 0.2), {"dx": to_like[0], "dy": to_like[1]}, "hold"),
         (at(clike), {"dx": to_like[0], "dy": to_like[1], "s": cs}, "out"),
         (at(clike + 0.15), {"dx": to_like[0], "dy": to_like[1]}, "inout"),
         (at(click2 - 0.2), {"dx": to_done[0], "dy": to_done[1]}, "hold"),
         (at(click2), {"dx": to_done[0], "dy": to_done[1], "s": cs}, "out"),
         (at(click2 + 0.15), {"dx": to_done[0], "dy": to_done[1]}, "inout"),
         (at(click3 - 0.2), {"dx": to_all[0], "dy": to_all[1]}, "hold"),
         (at(click3), {"dx": to_all[0], "dy": to_all[1], "s": cs}, "out"),
         (at(click3 + 0.15), {"dx": to_all[0], "dy": to_all[1]}, "inout"),
         (at(end - 0.1), {"dx": to_all[0] + 300, "dy": to_all[1] + 200})]
    vis = keys([(0, 0.0), (0.2, 1.0, "hold"), (at(end - 0.4), 1.0), (at(end - 0.1), 0.0)])
    if tap:
        # A fingertip: a soft round mark centred on the point it touches.
        d = 84
        t.solid(t.track("shape", "Toque"), WHITE, t0, end - 0.1 - t0, centered(tip[0], tip[1], d, d), m, kind="ellipse",
                layers=[shadow("#000000", 0, 4, 14, 0.35), fill(WHITE, 0.55), _stroke("#FFFFFF", 4, "inside")],
                opacity=vis)
        return
    path(t, t.track("shape", "Cursor"), WHITE, t0, end - 0.1 - t0, Box(tip[0], tip[1], cw, cw * 1.45), CURSOR, motion=m,
         layers=[shadow("#000000", 0, 5, 10, 0.45), fill(WHITE), _stroke("#0F0F0F", 3, "inside")], opacity=vis)


def _page_wide(theme_key, id, es, en, order, sample):
    th = THEMES[theme_key]
    t = _kit(id, es, en, order, ["suscríbete", "página", "campana", "cursor", "clic", theme_key], thumb_at=5.3)
    t.solid(t.track("shape", "Fondo de la página"), th["page"])
    p = Page(t, th)
    L, R = 120, 1800          # page margins
    V = Box(L, 84, 1280, 720)  # the video
    col = V.x + V.w + 32       # recommended column

    # Top bar: menu, a brand block, the search box with its button and the mic, account icons.
    p.icon(MENU, Box(L, 24, 30, 24), width=4, name="Barra superior")
    p.block(Box(L + 56, 22, 104, 28), radius=8, name="Barra superior")
    p.block(Box(640, 14, 560, 48), th["soft_card"], radius=24, name="Barra superior")
    p.block(Box(1200, 14, 84, 48), th["card"], radius=24, name="Barra superior")
    p.icon(SEARCH, centered(1242, 38, 24, 24), width=4, name="Barra superior")
    p.circle(1324, 38, 46, name="Barra superior")
    p.icon(MIC, centered(1324, 38, 18, 22), width=4, name="Barra superior")
    p.circle(R - 116, 38, 40, name="Barra superior")
    p.circle(R - 58, 38, 40, name="Barra superior")
    p.circle(R - 18, 38, 36, TEAL, name="Barra superior")

    # Recommended: chips, then thumbnails with their length and text lines beside.
    x = col
    for i, w in enumerate([80, 128, 112, 92]):
        p.block(Box(x, V.y, w, 40), th["ink"] if i == 0 else th["card"], radius=10, name="Etiquetas")
        x += w + 12
    p.text("Todos", Box(col, V.y, 80, 40), 18, th["page"], weight=600, align="center", name="Etiqueta", editable=False)
    for i in range(6):
        y = V.y + 58 + i * 118
        p.block(Box(col, y, 176, 99), radius=10, name="Recomendados", lag=0.03 * i)
        p.block(Box(col + 176 - 54, y + 99 - 26, 48, 20), th["badge"], radius=4, name="Recomendados", lag=0.03 * i)
        for dy, w, h in [(4, 168, 15), (26, 132, 15), (56, 96, 11), (74, 74, 11)]:
            p.block(Box(col + 192, y + dy, w, h), radius=5, name="Recomendados", lag=0.03 * i)

    # The video and its progress line.
    t.photo(t.track("video", "Tu video"), sample, 0.0, DUR, V, _video_motion(V, 1920, 1080), label="Tu video")
    rrect(t, t.track("shape", "Progreso"), CORAL, 0.0, DUR, Box(V.x, V.y + V.h - 5, V.w, 5), radius=0,
          motion=[(0, {"sx": 0.0, "dx": -V.w / 2}, "hold"), (UI_AT, {"sx": 0.0, "dx": -V.w / 2}, "linear"),
                  (DUR, {"sx": 0.5, "dx": -V.w / 4})], opacity=_ui())

    # Title, channel row (logo, name, subscribers, button) and the actions on the right edge.
    p.text("Título de tu video", Box(L, V.y + V.h + 14, V.w, 44), 30, weight=700, font="Sora", name="Título del video")
    cy = V.y + V.h + 98
    t.solid(t.track("shape", "Logo"), TEAL, 0.0, DUR, centered(L + 28, cy, 56, 56), kind="ellipse", opacity=_ui())
    t.photo(t.track("video", "Tu logo"), "logo-07", 0.0, DUR, centered(L + 28, cy, 40, 40), label="Tu logo", opacity=_ui())
    p.text("Tu canal", Box(L + 72, cy - 30, 240, 32), 24, weight=700, name="Nombre del canal")
    p.text("48 mil suscriptores", Box(L + 72, cy + 2, 240, 26), 18, th["soft"], name="Suscriptores")
    right = V.x + V.w
    p.block(Box(right - 50, cy - 25, 50, 50), radius=25, name="Acciones")
    p.icon(DOTS3, centered(right - 25, cy, 22, 22), filled=True, name="Acciones")
    p.block(Box(right - 110, cy - 25, 50, 50), radius=25, name="Acciones")
    p.icon(SAVE, centered(right - 85, cy, 16, 22), width=3, name="Acciones")
    p.block(Box(right - 170, cy - 25, 50, 50), radius=25, name="Acciones")
    p.icon(SHARE, centered(right - 145, cy, 22, 20), width=3, name="Acciones")
    p.block(Box(right - 360, cy - 25, 180, 50), radius=25, name="Acciones")
    p.icon(THUMB, centered(right - 334, cy, 22, 22), width=3, name="Acciones")
    p.block(Box(right - 232, cy - 15, 2, 30), th["soft"], radius=1, name="Acciones")
    dislike = p.icon(THUMB, centered(right - 206, cy + 2, 22, 22), width=3, name="Acciones")
    dislike["rotation"] = keys([(0, 180)])

    # Description box and its neighbour.
    by = cy + 44
    half = (V.w - 20) / 2
    p.block(Box(L, by, half, 1080 - by - 18), th["card"], radius=14, name="Descripción")
    p.text("12 mil vistas  hace 2 días  #TuCanal", Box(L + 18, by + 10, half - 36, 26), 18, weight=700,
           name="Vistas y etiquetas")
    p.text("Cuéntale a tu audiencia de qué trata el video…", Box(L + 18, by + 38, half - 36, 26), 18,
           name="Descripción")
    p.block(Box(L + half + 20, by, half, 1080 - by - 18), th["card"], radius=14, name="Descripción")
    for dy, w in [(16, 220), (46, 420)]:
        p.block(Box(L + half + 38, by + dy, w, 14), th["page"], radius=5, name="Descripción")

    btn = Box(L + 330, cy - 25, 168, 50)
    _subscribe(t, th, btn, 214, Box(btn.x, cy - 25 - 14 - 236, 330, 236), (560, 320), 20,
               like=(right - 334, cy, 22), count=(Box(right - 316, cy - 14, 80, 28), "20 mil", "21 mil", 18))
    return t


def suscribete_pagina_oscura():
    return _page_wide("oscura", "suscribete-pagina-oscura", "Suscríbete en la página oscura",
                      "Subscribe on a dark video page", 8150, "h-podcast-02")


def suscribete_pagina_clara():
    return _page_wide("clara", "suscribete-pagina-clara", "Suscríbete en la página clara",
                      "Subscribe on a light video page", 8151, "h-cooking-02")


SPARKLE = "M 50 0 C 54 34 66 46 100 50 C 66 54 54 66 50 100 C 46 66 34 54 0 50 C 34 46 46 34 50 0 Z"


def suscribete_pagina_movil():
    """The phone app (Jorge's screenshot, 2026-10-30): black player on top, a white sheet below with the title,
    the meta line, the channel row (logo, the button, then like, dislike, share, ✦ and ⋯ as bare icons), the
    comments card and the next video. Subscribed, the button is just the bell and the arrow; the bell's options
    rise as a sheet from the bottom; a fingertip instead of a pointer."""
    th = THEMES["clara"]
    t = _kit("suscribete-pagina-movil", "Suscríbete en el celular", "Subscribe on a phone page", 8152,
             ["suscríbete", "celular", "móvil", "campana", "toque", "clic"], vertical=True, thumb_at=5.3)
    t.solid(t.track("shape", "Fondo de la página"), "#000000")
    p = Page(t, th)
    M = 32
    V = Box(0, 142, 1080, 608)
    t.photo(t.track("video", "Tu video"), "h-portrait-03", 0.0, DUR, V, _video_motion(V, 1080, 1920), label="Tu video")
    # Progress line along the player's bottom edge, with its dot.
    rrect(t, t.track("shape", "Progreso"), "#5A5A5A", 0.0, DUR, Box(0, V.y + V.h - 3, 1080, 6), radius=0, opacity=_ui())
    rrect(t, t.track("shape", "Progreso"), CORAL, 0.0, DUR, Box(0, V.y + V.h - 3, 1080, 6), radius=0,
          motion=[(0, {"sx": 0.0, "dx": -540}, "hold"), (UI_AT, {"sx": 0.0, "dx": -540}, "linear"),
                  (DUR, {"sx": 0.4, "dx": -324})], opacity=_ui())
    t.solid(t.track("shape", "Progreso"), CORAL, 0.0, DUR, centered(0, V.y + V.h, 28, 28),
            [(0, {"dx": 0}, "hold"), (UI_AT, {"dx": 0}, "linear"), (DUR, {"dx": 432})], kind="ellipse", opacity=_ui())

    # The white sheet under the player.
    sheet_y = V.y + V.h + 8
    p.block(Box(0, sheet_y, 1080, 1920 - sheet_y + 40), th["page"], radius=34, name="Hoja")
    p.text("Título de tu video", Box(M, sheet_y + 30, 1016, 58), 40, weight=700, font="Sora", name="Título del video")
    p.text("@tucanal   21 «Me gusta»   222 vistas   hace 3 h   más", Box(M, sheet_y + 94, 1016, 40), 26, th["soft"],
           name="Datos del video")
    cy = sheet_y + 200
    t.solid(t.track("shape", "Logo"), TEAL, 0.0, DUR, centered(M + 42, cy, 84, 84), kind="ellipse", opacity=_ui())
    t.photo(t.track("video", "Tu logo"), "logo-07", 0.0, DUR, centered(M + 42, cy, 58, 58), label="Tu logo", opacity=_ui())
    # Like, dislike, share, sparkle, more: bare icons on the right.
    ix = 1080 - M - 30
    for d, w, h, filled in [(DOTS3, 36, 36, True), (SPARKLE, 40, 40, True), (SHARE, 40, 36, False),
                            ((THUMB, "flip"), 40, 40, False), (THUMB, 40, 40, False)]:
        flip = isinstance(d, tuple)
        c = p.icon(d[0] if flip else d, centered(ix, cy + (4 if flip else 0), w, h), width=4, filled=filled,
                   name="Acciones")
        if flip:
            c["rotation"] = keys([(0, 180)])
        ix -= 104
    # Comments card.
    cc = Box(M, cy + 76, 1080 - 2 * M, 210)
    p.block(cc, th["card"], radius=30, name="Comentarios")
    p.text("Comentarios", Box(cc.x + 30, cc.y + 22, 600, 48), 32, weight=700, name="Comentarios")
    p.circle(cc.x + 66, cc.y + 140, 54, "#D9D9D9", name="Comentarios")
    p.block(Box(cc.x + 112, cc.y + 112, cc.w - 142, 58), "#E5E5E5", radius=29, name="Comentarios")
    p.text("Comentar…", Box(cc.x + 140, cc.y + 118, 500, 46), 28, th["soft"], name="Comentar", editable=False)
    # The next video of the feed.
    ny = cc.y + cc.h + 34
    p.block(Box(0, ny, 1080, 608), "#D9D9D9", radius=0, name="Siguiente video")
    p.block(Box(1080 - 150, ny + 608 - 64, 128, 46), th["badge"], radius=10, name="Siguiente video")
    p.text("12:34", Box(1080 - 150, ny + 608 - 64, 128, 46), 26, WHITE, weight=600, align="center",
           name="Duración", editable=False)

    btn = Box(M + 104, cy - 38, 250, 76)
    sheet = Box(0, 1920 - 560, 1080, 600)
    like_x = 1080 - M - 30 - 4 * 104
    _subscribe(t, th, btn, 150, sheet, (420, 520), 32, vertical=True, compact=True, tap=True, menu_radius=34,
               like=(like_x, cy, 40))
    return t


TEMPLATES = [suscribete_pagina_oscura, suscribete_pagina_clara, suscribete_pagina_movil]
