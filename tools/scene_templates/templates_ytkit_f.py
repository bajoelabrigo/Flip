"""Kit de YouTube, batch f (2026-10-30): «Suscríbete en la página». Jorge brought a commercial promo where the
video zooms out into a video page and a cursor subscribes; this is our own take on that idea (no platform logo or
red, the kit's palette, every text and picture editable): the user's video full screen, the page builds around it,
the cursor clicks Subscribe (→ Subscribed), then the bell, picks «All» in its menu, the bell rings, and the video
zooms back to full screen so the piece can sit in the middle of any video. Dark and light pages (16:9) and a phone
page (9:16). Section pantallas-finales? No: elementos (it is an insert); order 8150-8199.
"""

from __future__ import annotations

from kit import Box, centered, fill, keys, label, no_stroke, pill, rrect, shadow, tall, tanim, wide
from templates_ytkit_a import BELL, CURSOR, OUT, _stroke, path

TEAL = "#2EE6C8"
CORAL = "#FF5D73"
SUN = "#FFD23F"
WHITE = "#FFFFFF"

THEMES = {
    "oscura": dict(page="#0E1116", card="#1C2129", line="#2A303A", ink=WHITE, soft="#A9B8CC", done="#2A303A",
                   done_ink="#E6EAF0", menu="#20252E"),
    "clara": dict(page="#F7F8FA", card="#E6E9EE", line="#D5DAE1", ink="#0B1A2E", soft="#5B6878", done="#E3E7EC",
                  done_ink="#0B1A2E", menu=WHITE),
}

ZOOM_OUT = (1.2, 2.2)   # the video leaves full screen
ZOOM_IN = (7.0, 7.8)    # and comes back
DUR = 8.4


def _kit(id, es, en, order, tags, vertical=False, **kw):
    make = tall if vertical else wide
    return make(f"ytk-{id}", es, en, "ytkit", DUR, order=order,
                tags=["kit:elementos", "youtube"] + (["vertical"] if vertical else []) + tags, **kw)


def _ui(at=ZOOM_OUT[1] - 0.3, until=ZOOM_IN[0] + 0.1):
    """Opacity of the page around the video: in after the zoom out, out before the zoom in."""
    return keys([(0, 0.0, "hold"), (at, 0.0, "out"), (at + 0.35, 1.0, "hold"), (until - 0.3, 1.0, "in"), (until, 0.0)])


def _video_motion(box: Box, frame_w: float, frame_h: float):
    """The video slot: full screen at first (scaled to cover the frame), into its box on the page, and back."""
    s = max(frame_w / box.w, frame_h / box.h)
    dx = frame_w / 2 - (box.x + box.w / 2)
    dy = frame_h / 2 - (box.y + box.h / 2)
    full = {"s": s, "dx": dx, "dy": dy}
    a, b = ZOOM_OUT
    c, d = ZOOM_IN
    return [(0, full, "hold"), (a, full, "inout"), (b, {}, "hold"), (c, {}, "inout"), (d, full, "hold")]


def _bars(t, theme, rects, at, name="Página"):
    """Grey placeholder blocks of the page (thumbnails, text lines), fading in with the page."""
    tr = t.track("shape", name)
    for i, (x, y, w, h, r) in enumerate(rects):
        if i and i % 8 == 0:
            tr = t.track("shape", name)
        rrect(t, tr, theme["card"], 0.0, DUR, Box(x, y, w, h), radius=r, opacity=_ui(at + 0.02 * (i % 6)))


def _subscribe_sequence(t, theme, btn: Box, bell_c, menu_box: Box, cursor_from, vertical=False):
    """Subscribe → Subscribed, the bell, its menu, «All», the bell rings. Times are the piece's."""
    click1, click2, click3 = 3.6, 4.7, 5.6
    end = ZOOM_IN[0]
    sh = shadow("#000000", 0, 6, 16, 0.3)
    fs = 28 if not vertical else 32
    # The button before and after the click.
    pill(t, t.track("shape", "Botón"), CORAL, 0.0, click1 + 0.12, btn,
         [(0, {}, "hold"), (click1, {}, "out"), (click1 + 0.12, {"s": 0.94})], opacity=_ui(), layers=[sh, fill(CORAL), no_stroke()])
    pill(t, t.track("shape", "Botón"), theme["done"], click1 + 0.1, end - click1 - 0.1, btn,
         [(0, {"s": 0.94}, "back"), (0.25, {})], opacity=keys([(0, 1.0, "hold"), (end - click1 - 0.4, 1.0, "in"), (end - click1 - 0.1, 0.0)]))
    label(t, t.track("text", "Botón"), "SUSCRIBIRSE", 0.0, click1 + 0.1, btn, "Sora", fs, WHITE, weight=800, spacing=2,
          opacity=_ui(), name="Botón")
    label(t, t.track("text", "Botón"), "SUSCRITO", click1 + 0.1, end - click1 - 0.1, btn, "Sora", fs, theme["done_ink"],
          weight=700, spacing=2, anim_in=tanim("fade", duration=0.2), anim_out=OUT(0.25), name="Botón tras el clic")
    # A ripple where the click lands.
    for i, c in enumerate([TEAL, WHITE]):
        t.solid(t.track("shape", "Onda"), c, click1 + i * 0.08, 0.6, centered(btn.x + btn.w / 2, btn.y + btn.h / 2, 90, 90),
                [(0, {"s": 0.2}, "out"), (0.6, {"s": 3.0})], kind="ellipse",
                layers=[{"id": "fill", "kind": "fill", "enabled": False, "paint": {"kind": "solid", "color": "#00000000"}},
                        _stroke(c, 5, "inside")], opacity=keys([(0, 1.0), (0.6, 0.0)]))

    # The bell, on its round button, from the first click.
    bx, by = bell_c
    t.solid(t.track("shape", "Campana"), theme["done"], click1 + 0.2, end - click1 - 0.2, centered(bx, by, btn.h, btn.h),
            [(0, {"s": 0.0}, "back"), (0.35, {})], kind="ellipse",
            opacity=keys([(0, 1.0, "hold"), (end - click1 - 0.5, 1.0, "in"), (end - click1 - 0.2, 0.0)]))
    wob = [(0, 0, "hold"), (click3 + 0.25 - click1, 0, "smooth"), (click3 + 0.35 - click1, 22, "smooth"),
           (click3 + 0.45 - click1, -20, "smooth"), (click3 + 0.55 - click1, 15, "smooth"),
           (click3 + 0.65 - click1, -10, "smooth"), (click3 + 0.75 - click1, 5, "smooth"), (click3 + 0.85 - click1, 0)]
    bs = btn.h * 0.5
    path(t, t.track("shape", "Campana"), theme["done_ink"], click1 + 0.3, end - click1 - 0.3,
         centered(bx, by, bs, bs * 1.08), BELL, filled=True, motion=[(0, {"s": 0.0}, "back"), (0.3, {})],
         rotation=keys(wob), opacity=keys([(0, 1.0, "hold"), (end - click1 - 0.6, 1.0, "in"), (end - click1 - 0.3, 0.0)]))
    t.solid(t.track("shape", "Aviso"), TEAL, click3 + 0.25, end - click3 - 0.25, centered(bx + bs * 0.55, by - bs * 0.55, 22, 22),
            [(0, {"s": 0.0}, "back"), (0.3, {})], kind="ellipse",
            opacity=keys([(0, 1.0, "hold"), (end - click3 - 0.55, 1.0, "in"), (end - click3 - 0.25, 0.0)]))

    # The bell's menu: three choices, «All» picked.
    open_at, close_at = click2 + 0.1, click3 + 0.2
    mdur = close_at - open_at
    rrect(t, t.track("shape", "Menú"), theme["menu"], open_at, mdur, menu_box, radius=14,
          motion=[(0, {"s": 0.85, "dy": -10}, "out"), (0.2, {}, "hold"), (mdur - 0.15, {}, "in"), (mdur, {"s": 0.9})],
          layers=[shadow("#000000", 0, 12, 30, 0.45), fill(theme["menu"]), no_stroke()],
          opacity=keys([(0, 0.0), (0.15, 1.0, "hold"), (mdur - 0.15, 1.0), (mdur, 0.0)]))
    row_h = menu_box.h / 3
    hi = Box(menu_box.x + 8, menu_box.y + 8, menu_box.w - 16, row_h - 10)
    rrect(t, t.track("shape", "Menú"), theme["card"], click3 - 0.35, close_at - (click3 - 0.35), hi, radius=10,
          opacity=keys([(0, 0.0), (0.15, 1.0)]))
    for i, (text, name) in enumerate([("Todas", "Menú: todas"), ("Personalizadas", "Menú: personalizadas"),
                                      ("Ninguna", "Menú: ninguna")]):
        rb = Box(menu_box.x + 34, menu_box.y + i * row_h, menu_box.w - 50, row_h)
        label(t, t.track("text", "Menú"), text, open_at + 0.05, mdur - 0.05, rb, "Inter", 30 if not vertical else 36,
              theme["ink"], weight=600 if i == 0 else 400, align="left", anim_in=tanim("fade", duration=0.2),
              anim_out=OUT(0.15), name=name)

    # The cursor: in to the button, to the bell, down to «All», away.
    tip = (btn.x + btn.w * 0.62, btn.y + btn.h * 0.62)
    to_bell = (bx + 8 - tip[0], by + 10 - tip[1])
    to_all = (menu_box.x + 90 - tip[0], menu_box.y + row_h * 0.55 - tip[1])
    t0 = 2.6
    cs = 0.82
    m = [(0, {"dx": cursor_from[0], "dy": cursor_from[1]}, "out"), (click1 - 0.15 - t0, {}, "hold"),
         (click1 - t0, {"s": cs}, "out"), (click1 + 0.15 - t0, {}, "inout"),
         (click2 - 0.2 - t0, {"dx": to_bell[0], "dy": to_bell[1]}, "hold"),
         (click2 - t0, {"dx": to_bell[0], "dy": to_bell[1], "s": cs}, "out"),
         (click2 + 0.15 - t0, {"dx": to_bell[0], "dy": to_bell[1]}, "inout"),
         (click3 - 0.2 - t0, {"dx": to_all[0], "dy": to_all[1]}, "hold"),
         (click3 - t0, {"dx": to_all[0], "dy": to_all[1], "s": cs}, "out"),
         (click3 + 0.15 - t0, {"dx": to_all[0], "dy": to_all[1]}, "inout"),
         (end - 0.2 - t0, {"dx": to_all[0] + 260, "dy": to_all[1] + 220})]
    path(t, t.track("shape", "Cursor"), WHITE, t0, end - 0.2 - t0, Box(tip[0], tip[1], 48, 70), CURSOR, motion=m,
         layers=[shadow("#000000", 0, 6, 12, 0.45), fill(WHITE), _stroke("#0B1A2E", 4, "inside")],
         opacity=keys([(0, 0.0), (0.2, 1.0, "hold"), (end - 0.5 - t0, 1.0), (end - 0.2 - t0, 0.0)]))


def _page_wide(theme_key, id, es, en, order, sample):
    theme = THEMES[theme_key]
    t = _kit(id, es, en, order, ["suscríbete", "página", "campana", "cursor", "clic", theme_key], thumb_at=5.2)
    t.solid(t.track("shape", "Fondo de la página"), theme["page"])
    at = ZOOM_OUT[1] - 0.3
    # Top bar: search box and a round account picture.
    _bars(t, theme, [(610, 18, 700, 46, 23), (1780, 18, 46, 46, 23), (96, 26, 150, 30, 8)], at, "Barra superior")
    # Recommended column.
    rec = []
    for i in range(6):
        y = 100 + i * 150
        rec += [(1340, y, 230, 130, 10), (1590, y + 6, 260, 20, 6), (1590, y + 40, 200, 16, 6), (1590, y + 68, 150, 16, 6)]
    _bars(t, theme, rec, at, "Recomendados")
    # Under the video: action pills.
    _bars(t, theme, [(860, 776, 140, 52, 26), (1016, 776, 120, 52, 26), (1152, 776, 120, 52, 26)], at, "Acciones")
    video = Box(96, 92, 1200, 675)
    t.photo(t.track("video", "Tu video"), sample, 0.0, DUR, video, _video_motion(video, 1920, 1080), label="Tu video")
    # Progress line along the bottom of the video.
    rrect(t, t.track("shape", "Progreso"), CORAL, 0.0, DUR, Box(96, 762, 1200, 6), radius=3,
          motion=[(0, {"sx": 0.0, "dx": -600}, "hold"), (at, {"sx": 0.0, "dx": -600}, "linear"), (DUR, {"sx": 0.55, "dx": -270})],
          opacity=_ui())
    label(t, t.track("text", "Título"), "Título de tu video", 0.0, DUR, Box(96, 780, 740, 56), "Sora", 38, theme["ink"],
          weight=700, align="left", opacity=_ui(), name="Título del video")
    label(t, t.track("text", "Vistas"), "12 mil vistas · hace 2 días", 0.0, DUR, Box(96, 832, 740, 40), "Inter", 26,
          theme["soft"], weight=400, align="left", opacity=_ui(), name="Vistas")
    # Channel row: logo, name, subscribers, the button.
    cy = 950
    t.solid(t.track("shape", "Logo"), TEAL, 0.0, DUR, centered(146, cy, 92, 92), kind="ellipse", opacity=_ui())
    t.photo(t.track("video", "Tu logo"), "logo-07", 0.0, DUR, centered(146, cy, 64, 64), label="Tu logo", opacity=_ui())
    label(t, t.track("text", "Canal"), "Tu canal", 0.0, DUR, Box(212, cy - 46, 420, 50), "Sora", 34, theme["ink"],
          weight=700, align="left", opacity=_ui(), name="Nombre del canal")
    label(t, t.track("text", "Suscriptores"), "48 mil suscriptores", 0.0, DUR, Box(212, cy + 4, 420, 40), "Inter", 24,
          theme["soft"], weight=400, align="left", opacity=_ui(), name="Suscriptores")
    btn = Box(640, cy - 34, 300, 68)
    _subscribe_sequence(t, theme, btn, (btn.x + btn.w + 60, cy), Box(990, cy - 330, 380, 240), (520, 330))
    return t


def suscribete_pagina_oscura():
    return _page_wide("oscura", "suscribete-pagina-oscura", "Suscríbete en la página oscura",
                      "Subscribe on a dark video page", 8150, "h-podcast-02")


def suscribete_pagina_clara():
    return _page_wide("clara", "suscribete-pagina-clara", "Suscríbete en la página clara",
                      "Subscribe on a light video page", 8151, "h-cooking-02")


def suscribete_pagina_movil():
    theme = THEMES["oscura"]
    t = _kit("suscribete-pagina-movil", "Suscríbete en el celular", "Subscribe on a phone page", 8152,
             ["suscríbete", "celular", "móvil", "campana", "cursor", "clic"], vertical=True, thumb_at=5.2)
    t.solid(t.track("shape", "Fondo de la página"), theme["page"])
    at = ZOOM_OUT[1] - 0.3
    _bars(t, theme, [(60, 70, 180, 40, 10), (900, 64, 54, 54, 27), (820, 64, 54, 54, 27)], at, "Barra superior")
    rec = []
    for i in range(2):
        y = 1290 + i * 330
        rec += [(0, y, 1080, 230, 0), (60, y + 248, 700, 26, 8), (60, y + 288, 420, 22, 8)]
    _bars(t, theme, rec, at, "Recomendados")
    _bars(t, theme, [(60, 1010, 210, 64, 32), (290, 1010, 170, 64, 32), (480, 1010, 170, 64, 32)], at, "Acciones")
    video = Box(0, 160, 1080, 608)
    t.photo(t.track("video", "Tu video"), "h-portrait-03", 0.0, DUR, video, _video_motion(video, 1080, 1920), label="Tu video")
    rrect(t, t.track("shape", "Progreso"), CORAL, 0.0, DUR, Box(0, 762, 1080, 6), radius=0,
          motion=[(0, {"sx": 0.0, "dx": -540}, "hold"), (at, {"sx": 0.0, "dx": -540}, "linear"), (DUR, {"sx": 0.55, "dx": -243})],
          opacity=_ui())
    label(t, t.track("text", "Título"), "Título de tu video", 0.0, DUR, Box(60, 790, 960, 70), "Sora", 46, theme["ink"],
          weight=700, align="left", opacity=_ui(), name="Título del video")
    label(t, t.track("text", "Vistas"), "12 mil vistas · hace 2 días", 0.0, DUR, Box(60, 860, 960, 50), "Inter", 32,
          theme["soft"], weight=400, align="left", opacity=_ui(), name="Vistas")
    cy = 1170
    t.solid(t.track("shape", "Logo"), TEAL, 0.0, DUR, centered(116, cy, 100, 100), kind="ellipse", opacity=_ui())
    t.photo(t.track("video", "Tu logo"), "logo-07", 0.0, DUR, centered(116, cy, 70, 70), label="Tu logo", opacity=_ui())
    label(t, t.track("text", "Canal"), "Tu canal", 0.0, DUR, Box(186, cy - 50, 400, 56), "Sora", 40, theme["ink"],
          weight=700, align="left", opacity=_ui(), name="Nombre del canal")
    label(t, t.track("text", "Suscriptores"), "48 mil", 0.0, DUR, Box(186, cy + 6, 400, 44), "Inter", 30,
          theme["soft"], weight=400, align="left", opacity=_ui(), name="Suscriptores")
    btn = Box(540, cy - 40, 340, 80)
    _subscribe_sequence(t, theme, btn, (btn.x + btn.w + 70, cy), Box(560, cy - 380, 460, 290), (260, 420), vertical=True)
    return t


TEMPLATES = [suscribete_pagina_oscura, suscribete_pagina_clara, suscribete_pagina_movil]
