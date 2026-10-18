"""YouTuber-style templates (0.15.0, part B of docs/plan-stock.md): Miniaturas que se hacen clic, Reseña de
tecnología, Podcast en video. Category youtuber (thumbnail for the thumbnails); order 6100-6199.

Three styles, 18 each:
- **Miniaturas que se hacen clic** (`yt-mini-*`, category thumbnail, 16:9, 3 s almost still: the thumbnail moment
  is the end state). New layouts next to the 50 of templates_y1.py: arrow and circle, diagonal before/after, face to
  face, #1 badge, crossed-out price, phone screen, three levels, magnifier, warning, tier list, right/wrong, rising
  chart, comic burst, sticker face, mystery box, four faces, stopwatch, hidden reveal.
- **Reseña de tecnología** (`yt-tec-*`): unboxing, spec sheet that builds up, side by side, pros and cons, score,
  price tag, verdict, desk setup, benchmark, battery test, camera test, chapters... Generic devices only: no brands.
- **Podcast en video** (`yt-pod-*`): two cameras with name plates, cuts between speakers, audiogram, episode title,
  guest intro, quote card, vertical clips, panel, live, on air, break, best moments.
"""

from __future__ import annotations

from kit import (Box, appear, bg, bg_gradient, blink, centered, circle_photo, confetti, dots, effect, fill, flash,
                 glow, gradient, grain, keys, kb, label, letterbox, line, math, no_stroke, outline, panels, photo_bg,
                 pill, pop, random, ring, rrect, shade_bottom, shade_full, shade_top, shadow, slide_in, song, spike, stroke, tall, tanim,
                 vignette, wide)
from templates_c1 import big, count_up, curve_keys, geo, hollow_ring, smooth

O = 6100

# Sample photos of this batch never used: a brand or logo shows (checked 2026-10-17).
Y3_BLOCKED = {"y3-phone-02", "y3-phone-06", "y3-phone-07", "y3-phonev-01", "y3-phonev-02", "y3-gadget-03",
              "y3-gadget-03", "beach-01", "h-beach-01", "h-beach-02", "y3-cam-02", "h-beach-03", "h-beach-04",
              "y3-unbox-01", "y3-tablet-01"}

MINI_TAGS = ["miniaturas que se hacen clic", "youtuber", "thumbnail"]
TEC_TAGS = ["reseña de tecnología", "youtuber", "tech review"]
POD_TAGS = ["podcast en video", "youtuber", "video podcast"]


def _mini(n, id, es, en, tags, bgc="#000000", thumb=2.2):
    return wide(id, es, en, "thumbnail", 3.0, order=O + n, tags=MINI_TAGS + tags, thumb_at=thumb, background=bgc)


def _tec(maker, n, id, es, en, dur, tags, **kw):
    return maker(id, es, en, "youtuber", dur, order=O + 20 + n, tags=TEC_TAGS + tags, **kw)


def _pod(maker, n, id, es, en, dur, tags, **kw):
    return maker(id, es, en, "youtuber", dur, order=O + 40 + n, tags=POD_TAGS + tags, **kw)


# --- shared pieces ------------------------------------------------------------------------------------

def slab(t, text, box, size, colour, *, font="Luckiest Guy", ink="#000000", ow=14, rot=0.0, at=0.0, name="Texto",
         anim="pop", align="center", editable=True, dy=12, weight=400, dur=None, line_h=0.92, spacing=0):
    """Thumbnail lettering: fat outline and a hard drop shadow."""
    dur = t.duration - at if dur is None else dur
    layers = [shadow(ink, 0, dy, 0, 1.0), stroke(ow, ink), fill(colour)] if ow else [shadow(ink, 0, dy, 0, 1.0), fill(colour)]
    return label(t, t.track("text", name), text, at, dur, box, font, size, colour, weight=weight, line=line_h,
                 layers=layers, anim_in=tanim(anim, duration=0.25) if anim else None, rotation=keys([(0, rot)]),
                 name=name, align=align, editable=editable, spacing=spacing)


def arrow(t, colour, box, angle, at=0.2, ink="#000000", kind="block-arrow", width=10):
    """A fat arrow (the shape points right; angle turns it about its centre)."""
    return t.solid(t.track("shape", "Flecha"), colour, at, t.duration - at, box,
                   [(0, {"s": 0.0}, "back"), (0.35, {})], kind=kind,
                   layers=[shadow(ink, 0, 10, 0, 1.0), stroke(width, ink), fill(colour)], rotation=keys([(0, angle)]))


def sticker(t, sample, box, *, at=0.0, border=16, colour="#FFFFFF", rot=0.0, label_="Tu cara (recortada)",
            motion=None, radius=30, shadow_a=0.45, reuse=None, effects=None, name="Cara"):
    """A photo with a thick white border, as a sticker cut out of a magazine."""
    dur = t.duration - at
    frame = Box(box.x - border, box.y - border, box.w + 2 * border, box.h + 2 * border)
    motion = motion if motion is not None else [(0, {"s": 0.6}, "back"), (0.35, {})]
    t.solid(t.track("shape", "Borde"), colour, at, dur, frame, motion, radius=radius, kind="rounded-rectangle",
            layers=[shadow("#000000", 0, 14, 26, shadow_a), fill(colour), no_stroke()], rotation=keys([(0, rot)]))
    extra = {"effects": effects} if effects else {}
    return t.photo(t.track("video", name), sample, at, dur, box, motion, label=label_, reuse=reuse,
                   rotation=keys([(0, rot)]), **extra)


def round_rect_points(rx, ry, n=8):
    pts = []
    for cx, cy, a0 in ((1 - rx, ry, -90), (1 - rx, 1 - ry, 0), (rx, 1 - ry, 90), (rx, ry, 180)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            pts.append([cx + rx * math.cos(a), cy + ry * math.sin(a)])
    return pts


def rounded_photo(t, sample, t0, dur, box, motion=None, *, radius=36, label_=None, reuse=None, name="Foto", **extra):
    track = t.track("video", name)
    clip = t.photo(track, sample, t0, dur, box, motion, label=label_, reuse=reuse, **extra)
    t.mask(track, clip, "freeform", points=round_rect_points(radius / box.w, radius / box.h), smooth=False)
    return clip


def wave_bars(t, x0, cy, n, step, w, hmax, colours, t0, dur, seed, hmin=0.18, speed=(0.16, 0.32), name="Onda"):
    """An audio level meter: bars that jump up and down about their centre."""
    rng = random.Random(seed)
    track = None
    for i in range(n):
        if i % 8 == 0:
            track = t.track("shape", name)
        h = hmax * (0.55 + 0.45 * math.sin(math.pi * (i + 0.5) / n))
        pts = [(0, {"sy": hmin})]
        at = 0.0
        while at < dur:
            at += rng.uniform(*speed)
            pts.append((min(at, dur), {"sy": rng.uniform(hmin, 1.0)}, "smooth"))
        t.solid(track, colours[i % len(colours)], t0, dur, centered(x0 + i * step, cy, w, h), pts, radius=w / 2,
                kind="rounded-rectangle")


def live_dot(t, x, y, at, dur, colour="#FF3B30", size=26):
    t.solid(t.track("shape", "Punto"), colour, at, dur, centered(x, y, size, size), kind="ellipse",
            opacity=blink(dur, 1.0, 0.25))


def name_plate(t, name, role, x, y, w, colour, at, dur, *, ink="#FFFFFF", font="Montserrat", h=96, role_ink=None,
               bar="#FFFFFF", name_label="Nombre", role_label="Cargo", slide=-60):
    """A podcast name plate: a coloured block with the name, a thin strip with the role under it."""
    track = t.track("shape", "Placa")
    t.solid(track, colour, at, dur, Box(x, y, w, h), slide_in(dx=slide, length=0.45))
    t.solid(t.track("shape", "Placa"), bar, at + 0.1, dur - 0.1, Box(x, y + h, w * 0.75, h * 0.5),
            slide_in(dx=slide, length=0.45))
    label(t, t.track("text", "Nombre"), name, at + 0.1, dur - 0.1, Box(x + 26, y, w - 40, h), font, int(h * 0.48),
          ink, weight=800, align="left", anim_in=tanim("slide-right", duration=0.35), name=name_label)
    label(t, t.track("text", "Cargo"), role, at + 0.2, dur - 0.2, Box(x + 26, y + h, w * 0.75 - 40, h * 0.5), font,
          int(h * 0.26), role_ink or colour, weight=700, align="left", spacing=2, case="upper",
          anim_in=tanim("fade", duration=0.35), name=role_label)


def chip(t, text, box, colour, ink, at, dur=None, *, font="Montserrat", size=None, weight=800, name="Etiqueta",
         motion=None, editable=True, spacing=2, rot=0.0):
    dur = t.duration - at if dur is None else dur
    motion = motion if motion is not None else pop(0, 0.35)
    pill(t, t.track("shape", name), colour, at, dur, box, motion, rotation=keys([(0, rot)]))
    return label(t, t.track("text", name), text, at, dur, box, font, size or int(box.h * 0.48), ink, weight=weight,
                 motion=motion, editable=editable, name=name, spacing=spacing, rotation=keys([(0, rot)]))


def grow_bar(t, colour, at, box, frac, length=0.8, ease="out", track=None, radius=None, alpha=1.0):
    """A bar that grows from its left edge to `frac` of the box width."""
    w = box.w * frac
    b = Box(box.x, box.y, w, box.h)
    return t.solid(track or t.track("shape", "Barra"), colour, at, t.duration - at, b,
                   [(0, {"sx": 0.001, "dx": -w / 2}, ease), (length, {})], radius=radius if radius is not None else box.h / 2,
                   kind="rounded-rectangle", alpha=alpha)


def corners(t, box, colour, at, dur, arm=70, th=8, name="Visor"):
    """Viewfinder corner brackets around `box`."""
    track = t.track("shape", name)
    for (x, y, sx, sy) in ((box.x, box.y, 1, 1), (box.x + box.w, box.y, -1, 1), (box.x, box.y + box.h, 1, -1),
                           (box.x + box.w, box.y + box.h, -1, -1)):
        hx = x if sx > 0 else x - arm
        vy = y if sy > 0 else y - arm
        t.solid(track, colour, at, dur, Box(hx, y if sy > 0 else y - th, arm, th))
        t.solid(t.track("shape", name), colour, at, dur, Box(x if sx > 0 else x - th, vy, th, arm))


# =====================================================================================================
# 1. Miniaturas que se hacen clic (16:9, 3 s)
# =====================================================================================================

def mini_flecha_circulo():
    t = _mini(0, "yt-mini-flecha-circulo", "Flecha y círculo", "Arrow and circle",
              ["flecha roja", "círculo", "curiosidad", "red arrow"], "#FFD400")
    bg_gradient(t, [(0, "#FFE94D"), (1, "#FFB300")], angle=135)
    rays_clip = t.solid(t.track("shape", "Rayos"), "#FFFFFF", 0, 3.0, centered(1400, 430, 1500, 1500), kind="burst",
                        alpha=0.18, rotation=keys([(0, 0), (3.0, 12)]))
    geo(rays_clip, points=16, innerRatio=0.12)
    sticker(t, "y3-gadget-03", Box(1040, 110, 720, 560), rot=3, label_="Foto del objeto", name="Objeto", at=0.1)
    ring(t, t.track("shape", "Círculo"), "#FF2A2A", 22, 0.5, 2.5, centered(1400, 400, 560, 560),
         [(0, {"s": 1.6}, "snap"), (0.3, {})])
    t.photo(t.track("video", "Cara"), "y3-shock-01", 0, 3.0, Box(0, 130, 900, 950), label="Tu cara (recortada)",
            effects=[effect("color.basic", saturation=0.2, contrast=0.15)])
    arrow(t, "#FF2A2A", centered(900, 520, 480, 230), -28, at=0.7, kind="arrow")
    slab(t, "¿QUÉ ES ESTO?", Box(40, 760, 1240, 280), 175, "#FFFFFF", rot=-3, at=0.2)
    return t


def mini_diagonal():
    t = _mini(1, "yt-mini-diagonal", "Antes y después en diagonal", "Diagonal before/after",
              ["antes y después", "transformación", "before after", "diagonal"], "#111111")
    for i, (s, pts, lab) in enumerate((("h-interior-02", [[0, 0], [0.58, 0], [0.42, 1], [0, 1]], "Antes"),
                                       ("h-interior-04", [[0.58, 0], [1, 0], [1, 1], [0.42, 1]], "Después"))):
        track = t.track("video", lab)
        fx = [effect("color.basic", saturation=-0.7, brightness=-0.1)] if i == 0 else \
            [effect("color.basic", saturation=0.3, contrast=0.12)]
        clip = t.photo(track, s, 0, 3.0, t.full, [(0, {"s": 1.08}), (3.0, {"s": 1.0})], label=lab, effects=fx)
        t.mask(track, clip, "freeform", points=pts, smooth=False)
    t.solid(t.track("shape", "Corte"), "#FFFFFF", 0, 3.0, centered(960, 540, 26, 1300), [(0, {"sy": 0}, "out"), (0.4, {})],
            rotation=keys([(0, 8.5)]), layers=[shadow("#000000", 0, 0, 20, 0.6), fill("#FFFFFF"), no_stroke()])
    chip(t, "ANTES", Box(70, 60, 340, 110), "#111111", "#FFFFFF", 0.2, font="Anton", size=70, spacing=4, rot=-4)
    chip(t, "DESPUÉS", Box(1290, 60, 440, 110), "#00E676", "#111111", 0.4, font="Anton", size=70, spacing=4, rot=4)
    circle_photo(t, "y3-shock-04", 0.3, 2.7, centered(960, 640, 380, 380), [(0, {"s": 0.0}, "back"), (0.4, {})],
                 ring_colour="#00E676", ring_width=16, label="Tu cara")
    slab(t, "¡NO LO CREO!", Box(60, 820, 1300, 220), 170, "#FFE600", rot=-2, at=0.5)
    return t


def mini_cara_a_cara():
    t = _mini(2, "yt-mini-cara-a-cara", "Cara a cara", "Face to face",
              ["versus", "vs", "duelo", "reto", "face off"], "#111111")
    t.solid(t.track("shape", "Lado A"), "#1E5BFF", 0, 3.0, Box(0, 0, 1000, 1080),
            layers=[gradient([(0, "#2F6BFF"), (1, "#0A2A8A")], angle=90), no_stroke()])
    t.solid(t.track("shape", "Lado B"), "#FF2A55", 0, 3.0, Box(960, -60, 1100, 1200),
            layers=[gradient([(0, "#FF4D6D"), (1, "#9B0020")], angle=90), no_stroke()], rotation=keys([(0, 6)]))
    t.photo(t.track("video", "Persona A"), "y3-shock-10", 0, 3.0, Box(0, 160, 900, 920),
            [(0, {"dx": -300}, "out"), (0.4, {})], label="Persona A (recortada)")
    t.photo(t.track("video", "Persona B"), "y3-shock-11", 0, 3.0, Box(1020, 160, 900, 920),
            [(0, {"dx": 300}, "out"), (0.4, {})], label="Persona B (recortada)", flipH=True)
    bolt = t.solid(t.track("shape", "Rayo"), "#FFE600", 0.4, 2.6, centered(960, 470, 300, 560),
                   [(0, {"s": 0.0}, "back"), (0.35, {})], kind="lightning-bolt",
                   layers=[shadow("#000000", 0, 12, 0, 1.0), stroke(12, "#000000"), fill("#FFE600")])
    slab(t, "VS", centered(960, 480, 400, 260), 230, "#FFFFFF", at=0.5, name="VS", editable=False)
    slab(t, "YO", Box(60, 50, 500, 200), 170, "#FFFFFF", rot=-4, at=0.2, name="Nombre A")
    slab(t, "MI HERMANO", Box(1080, 50, 800, 200), 140, "#FFFFFF", rot=4, at=0.3, name="Nombre B")
    chip(t, "¿QUIÉN GANA?", Box(560, 900, 800, 130), "#FFE600", "#111111", 0.6, font="Luckiest Guy", size=80, weight=400)
    return t


def mini_numero_uno():
    t = _mini(3, "yt-mini-numero-uno", "El número 1", "Number one",
              ["número 1", "el mejor", "ranking", "badge", "top"], "#3A0CA3")
    bg_gradient(t, [(0, "#5A189A"), (1, "#240046")], angle=120)
    sticker(t, "y3-laptop-01", Box(860, 120, 760, 520), rot=-4, label_="Foto del producto", name="Producto", at=0.1)
    b = t.solid(t.track("shape", "Insignia"), "#FFD60A", 0.3, 2.7, centered(1620, 640, 470, 470),
                [(0, {"s": 0.0}, "back"), (0.4, {})], kind="burst",
                layers=[shadow("#000000", 0, 12, 0, 1.0), stroke(10, "#000000"), fill("#FFD60A")],
                rotation=keys([(0, 0), (2.7, 14)]))
    geo(b, points=16, innerRatio=0.8)
    slab(t, "#1", centered(1620, 650, 420, 300), 240, "#111111", ink="#FFFFFF", ow=0, dy=0, at=0.4, name="Puesto")
    t.photo(t.track("video", "Cara"), "y3-shock-06", 0, 3.0, Box(0, 180, 860, 900), label="Tu cara (recortada)",
            effects=[effect("color.basic", saturation=0.2)])
    slab(t, "EL MEJOR DEL AÑO", Box(40, 30, 900, 330), 140, "#FFD60A", rot=-3, at=0.2)
    slab(t, "Y ES BARATO", Box(840, 760, 640, 160), 100, "#FFFFFF", rot=-3, at=0.5, name="Texto 2")
    return t


def mini_precio_tachado():
    t = _mini(4, "yt-mini-precio-tachado", "Precio tachado", "Crossed-out price",
              ["precio", "oferta", "barato", "caro", "price drop"], "#00C853")
    bg_gradient(t, [(0, "#00E676"), (1, "#00963F")], angle=135)
    sticker(t, "y3-watch-04", Box(70, 110, 760, 560), rot=-3, label_="Foto del producto", name="Producto", at=0.1)
    slab(t, "$999", Box(80, 720, 600, 260), 210, "#FFFFFF", rot=-3, at=0.2, name="Precio anterior")
    t.solid(t.track("shape", "Tachado"), "#FF1744", 0.6, 2.4, centered(380, 845, 600, 34),
            [(0, {"sx": 0.0, "dx": -300}, "out"), (0.3, {})], rotation=keys([(0, -12)]),
            layers=[shadow("#000000", 0, 6, 0, 1.0), fill("#FF1744"), no_stroke()])
    arrow(t, "#FFE600", centered(800, 840, 260, 170), 0, at=0.8)
    t.photo(t.track("video", "Cara"), "y3-shock-12", 0, 3.0, Box(1300, 0, 620, 640), label="Tu cara (recortada)")
    slab(t, "$99", Box(880, 650, 640, 380), 300, "#FFE600", rot=-4, at=0.9, name="Precio nuevo", anim="stamp")
    slab(t, "¿EN SERIO?", Box(1100, 470, 820, 170), 120, "#FFFFFF", rot=4, at=0.4, name="Texto")
    return t


def mini_celular():
    t = _mini(5, "yt-mini-celular", "Mira mi pantalla", "Look at my screen",
              ["celular", "pantalla", "app", "mira esto", "phone screen"], "#00B4D8")
    bg_gradient(t, [(0, "#48CAE4"), (1, "#0077B6")], angle=120)
    dots(t, ["#FFFFFF"], 18, 0, 3.0, seed=6105, size=(10, 26), drift=20, alpha=0.5)
    phone = centered(1340, 540, 470, 920)
    t.solid(t.track("shape", "Celular"), "#111111", 0.1, 2.9, phone, [(0, {"dy": 400, "s": 0.9}, "out"), (0.45, {})],
            radius=70, kind="rounded-rectangle", rotation=keys([(0, 8)]),
            layers=[shadow("#000000", 0, 20, 40, 0.5), fill("#111111"), stroke(6, "#3A3A3A")])
    rounded_photo(t, "h-food-02", 0.1, 2.9, centered(1340, 540, 420, 860), [(0, {"dy": 400, "s": 0.9}, "out"), (0.45, {})],
                  radius=52, label_="Captura de pantalla", name="Pantalla", rotation=keys([(0, 8)]))
    ang = math.radians(8)  # the notch sits at the top of the turned screen
    nx, ny = 1340 + 400 * math.sin(ang), 540 - 400 * math.cos(ang)
    t.solid(t.track("shape", "Cámara"), "#111111", 0.1, 2.9, centered(nx, ny, 130, 30),
            [(0, {"dy": 400}, "out"), (0.45, {})], radius=15, kind="rounded-rectangle", rotation=keys([(0, 8)]))
    t.photo(t.track("video", "Cara"), "y3-shock-02", 0, 3.0, Box(0, 120, 980, 960), label="Tu cara (recortada)")
    arrow(t, "#FFE600", centered(1000, 330, 300, 190), -15, at=0.6)
    slab(t, "MIRA ESTO", Box(40, 760, 1000, 260), 190, "#FFE600", rot=-3, at=0.3)
    return t


def mini_tres_niveles():
    t = _mini(6, "yt-mini-tres-niveles", "Tres niveles", "Three levels",
              ["niveles", "$ vs $$$", "comparación", "barato vs caro", "levels"], "#111111")
    bg(t, "#141414")
    cols = [("#00C853", "$1", "h-food-04"), ("#FFAB00", "$10", "h-food-06"), ("#FF1744", "$100", "h-food-03")]
    for i, (c, price, s) in enumerate(cols):
        x = 30 + i * 630
        at = 0.1 + i * 0.25
        box = Box(x, 230, 600, 700)
        t.solid(t.track("shape", "Marco"), c, at, 3.0 - at, Box(x - 10, 220, 620, 720), [(0, {"dy": 900}, "out"), (0.4, {})],
                radius=34, kind="rounded-rectangle")
        rounded_photo(t, s, at, 3.0 - at, box, [(0, {"dy": 900}, "out"), (0.4, {})], radius=26,
                      label_=f"Nivel {i + 1}", name=f"Nivel {i + 1}")
        chip(t, price, centered(x + 300, 900, 300, 130), c, "#111111", at + 0.3, font="Luckiest Guy", size=90,
             weight=400, name=f"Precio {i + 1}")
    slab(t, "COMIDA DE $1 VS $100", Box(40, 20, 1840, 200), 150, "#FFFFFF", at=0.2)
    return t


def mini_lupa():
    t = _mini(7, "yt-mini-lupa", "Lupa sobre el detalle", "Magnifier on the detail",
              ["lupa", "detalle", "¿lo viste?", "secreto", "zoom"], "#000000")
    t.photo(t.track("video", "Escena"), "h-city-03", 0, 3.0, t.full,
            label="Foto de la escena", effects=[effect("color.basic", saturation=0.2, brightness=-0.15)])
    shade_full(t, 0.25)
    lens = centered(1240, 600, 520, 520)
    t.solid(t.track("shape", "Mango"), "#2B2B2B", 0.3, 2.7, centered(960, 930, 90, 380),
            [(0, {"s": 0.0}, "back"), (0.4, {})], radius=40, kind="rounded-rectangle", rotation=keys([(0, 45)]),
            layers=[shadow("#000000", 0, 10, 20, 0.6), fill("#2B2B2B"), stroke(8, "#000000")])
    # 2x zoom about the lens centre: the photo grows about that point and a circle mask shows only the lens
    px, py, z = 1240, 600, 2.0
    big_box = Box(px - z * px, py - z * py, 1920 * z, 1080 * z)
    zoom = t.photo(t.track("video", "Zoom"), "h-city-03", 0.3, 2.7, big_box, label="Foto de la escena", reuse="p1",
                   opacity=appear(0.0, 0.3))
    t.mask(t.tracks[-1], zoom, "ellipse", x=(px - big_box.x) / big_box.w, y=(py - big_box.y) / big_box.h,
           w=lens.w / big_box.w, h=lens.h / big_box.h)
    ring(t, t.track("shape", "Aro"), "#FFFFFF", 26, 0.3, 2.7, lens, [(0, {"s": 0.0}, "back"), (0.4, {})])
    ring(t, t.track("shape", "Aro"), "#111111", 8, 0.3, 2.7, centered(1240, 600, 560, 560), [(0, {"s": 0.0}, "back"), (0.4, {})])
    t.photo(t.track("video", "Cara"), "y3-shock-08", 0, 3.0, Box(0, 220, 760, 860), label="Tu cara (recortada)")
    slab(t, "¿LO VISTE?", Box(40, 30, 900, 220), 170, "#FFE600", rot=-3, at=0.2)
    return t


def mini_alerta():
    t = _mini(8, "yt-mini-alerta", "Alerta: no lo compres", "Warning: don't buy it",
              ["alerta", "advertencia", "no lo compres", "warning", "error"], "#111111")
    bg(t, "#141414")
    for i in range(14):  # caution stripes along the top and bottom
        for y in (-40, 1000):
            t.solid(t.track("shape", "Cinta"), "#FFD600" if i % 2 == 0 else "#111111", 0, 3.0,
                    Box(-200 + i * 170, y, 170, 120), rotation=keys([(0, 0)]))
    tri = t.solid(t.track("shape", "Señal"), "#FFD600", 0.2, 2.8, centered(1500, 400, 600, 520),
                  [(0, {"s": 0.0}, "back"), (0.4, {})], kind="triangle", radius=30,
                  layers=[shadow("#000000", 0, 14, 0, 1.0), stroke(18, "#000000"), fill("#FFD600")])
    slab(t, "!", centered(1500, 460, 300, 380), 320, "#111111", ow=0, dy=0, at=0.4, name="Signo", editable=False)
    t.photo(t.track("video", "Cara"), "y3-shock-05", 0, 3.0, Box(0, 100, 900, 900), label="Tu cara (recortada)",
            effects=[effect("color.basic", contrast=0.2, saturation=0.1)])
    slab(t, "NO LO COMPRES", Box(40, 720, 1400, 260), 170, "#FFD600", rot=-3, at=0.3)
    t.adjust([effect("stylize.vignette", amount=0.6, softness=0.9)], name="Viñeta")
    return t


def mini_tier_list():
    t = _mini(9, "yt-mini-tier-list", "Tier list", "Tier list",
              ["tier list", "ranking", "clasificación", "S A B C", "mejor a peor"], "#1A1A1A")
    bg(t, "#1A1A1A")
    tiers = [("S", "#FF7F7F"), ("A", "#FFBF7F"), ("B", "#FFDF7F"), ("C", "#BFFF7F")]
    shots = [["h-food-01", "h-food-02", "h-food-04"], ["h-food-06", "h-cafe-01"], ["h-food-03"], ["h-cafe-04"]]
    for r, ((tier, c), row) in enumerate(zip(tiers, shots)):
        y = 30 + r * 215
        at = 0.1 + r * 0.15
        t.solid(t.track("shape", "Fila"), "#2A2A2A", at, 3.0 - at, Box(30, y, 1180, 200), [(0, {"dx": -1300}, "out"), (0.35, {})])
        t.solid(t.track("shape", "Nivel"), c, at, 3.0 - at, Box(30, y, 200, 200), [(0, {"dx": -1300}, "out"), (0.35, {})])
        label(t, t.track("text", "Nivel"), tier, at, 3.0 - at, Box(30, y, 200, 200), "Anton", 140, "#111111", weight=400,
              motion=[(0, {"dx": -1300}, "out"), (0.35, {})], editable=False)
        for k, s in enumerate(row):
            a2 = at + 0.3 + k * 0.12
            t.photo(t.track("video", "Elemento"), s, a2, 3.0 - a2, Box(250 + k * 210, y + 10, 190, 180), pop(0, 0.3),
                    label=f"Elemento {tier}{k + 1}")
    t.photo(t.track("video", "Cara"), "y3-shock-09", 0, 3.0, Box(1180, 260, 740, 820), label="Tu cara (recortada)")
    slab(t, "RANKING DE COMIDA", Box(1200, 20, 700, 300), 120, "#FFE600", rot=3, at=0.3)
    return t


def mini_bien_mal():
    t = _mini(10, "yt-mini-bien-mal", "Bien o mal", "Right or wrong",
              ["bien vs mal", "correcto", "incorrecto", "errores", "do and don't"], "#F5F5F5")
    bg(t, "#F2F2F2")
    for i, (s, c, mark, lab) in enumerate((("h-cooking-03", "#FF1744", "✕", "Mal"), ("h-cooking-01", "#00C853", "✓", "Bien"))):
        x = 60 + i * 620
        sticker(t, s, Box(x, 160, 560, 560), rot=-3 if i == 0 else 3, label_=f"Foto: {lab.lower()}", name=lab,
                at=0.1 + i * 0.2, colour=c, border=14)
        t.solid(t.track("shape", "Marca"), c, 0.5 + i * 0.2, 2.5 - i * 0.2, centered(x + 470, 700, 190, 190),
                [(0, {"s": 0.0}, "back"), (0.35, {})], kind="ellipse",
                layers=[shadow("#000000", 0, 8, 0, 1.0), stroke(10, "#FFFFFF"), fill(c)])
        label(t, t.track("text", "Marca"), mark, 0.5 + i * 0.2, 2.5 - i * 0.2, centered(x + 470, 700, 190, 190), "Inter",
              120, "#FFFFFF", weight=900, motion=[(0, {"s": 0.0}, "back"), (0.35, {})], editable=False)
    t.photo(t.track("video", "Cara"), "y3-shock-03", 0, 3.0, Box(1240, 180, 680, 900), label="Tu cara (recortada)")
    slab(t, "¿LO HACES MAL?", Box(40, 790, 1300, 240), 170, "#111111", ink="#FFE600", ow=12, rot=-2, at=0.3)
    return t


def mini_grafica():
    t = _mini(11, "yt-mini-grafica", "La gráfica que sube", "Rising chart",
              ["gráfica", "crecimiento", "dinero", "estadísticas", "growth"], "#0B1F14")
    bg_gradient(t, [(0, "#0F3D24"), (1, "#05140B")], angle=90)
    for k in range(1, 6):
        t.solid(t.track("shape", "Rejilla"), "#1F6B3E", 0, 3.0, Box(0, k * 180, 1920, 3), alpha=0.6)
    heights = [160, 230, 210, 340, 470, 690]
    for i, h in enumerate(heights):
        x = 760 + i * 170
        at = 0.1 + i * 0.12
        t.solid(t.track("shape", "Barra"), "#00E676" if i == len(heights) - 1 else "#2EBD6B", at, 3.0 - at,
                Box(x, 1000 - h, 130, h), [(0, {"sy": 0.0, "dy": h / 2}, "out"), (0.5, {})], radius=14,
                kind="rounded-rectangle")
    arrow(t, "#00E676", centered(1330, 520, 900, 200), -38, at=0.8, ink="#04210F")
    t.photo(t.track("video", "Cara"), "y3-shock-07", 0, 3.0, Box(0, 180, 760, 900), label="Tu cara (recortada)")
    slab(t, "+300%", Box(40, 30, 900, 300), 260, "#00E676", rot=-4, at=0.3, ink="#04210F", name="Número")
    slab(t, "EN 1 MES", Box(1200, 40, 680, 170), 130, "#FFFFFF", rot=3, at=0.5, ink="#04210F")
    return t


def mini_comic():
    t = _mini(12, "yt-mini-comic", "Viñeta de cómic", "Comic burst",
              ["cómic", "burbuja", "pow", "humor", "comic"], "#FF006E")
    bg(t, "#FF006E")
    r = t.solid(t.track("shape", "Rayos"), "#FFBE0B", 0, 3.0, centered(560, 560, 2000, 2000), kind="burst",
                alpha=1.0, rotation=keys([(0, 0), (3.0, 8)]))
    geo(r, points=22, innerRatio=0.25)
    dots(t, ["#FFFFFF"], 26, 0, 3.0, seed=6112, size=(14, 30), drift=0, alpha=0.35, area=Box(1100, 0, 820, 1080))
    t.photo(t.track("video", "Cara"), "y3-shock-02", 0, 3.0, Box(60, 120, 900, 960), label="Tu cara (recortada)")
    bub = t.solid(t.track("shape", "Burbuja"), "#FFFFFF", 0.3, 2.7, Box(1000, 80, 860, 520),
                  [(0, {"s": 0.0}, "back"), (0.4, {})], kind="speech-bubble",
                  layers=[shadow("#000000", 0, 14, 0, 1.0), stroke(12, "#000000"), fill("#FFFFFF")])
    geo(bub, tailX=0.12, tailSize=0.3)
    label(t, t.track("text", "Burbuja"), "¿¡QUÉ ACABA DE PASAR!?", 0.45, 2.55, Box(1060, 110, 740, 360), "Bangers", 120,
          "#111111", weight=400, line=0.95, motion=[(0, {"s": 0.0}, "back"), (0.4, {})], name="Texto de la burbuja")
    pow_ = t.solid(t.track("shape", "Pow"), "#FFE600", 0.6, 2.4, centered(1500, 820, 560, 380),
                   [(0, {"s": 0.0}, "back"), (0.35, {})], kind="burst", rotation=keys([(0, -8)]),
                   layers=[shadow("#000000", 0, 10, 0, 1.0), stroke(10, "#000000"), fill("#FFE600")])
    geo(pow_, points=12, innerRatio=0.7)
    slab(t, "¡ZAS!", centered(1500, 820, 500, 260), 170, "#FF006E", rot=-8, at=0.7, font="Bangers", name="Onomatopeya")
    return t


def mini_sticker():
    t = _mini(13, "yt-mini-sticker", "Cara gigante", "Giant face sticker",
              ["cara", "sticker", "reacción", "imposible", "big face"], "#7B2CBF")
    bg_gradient(t, [(0, "#9D4EDD"), (0.5, "#5A189A"), (1, "#FF4D6D")], angle=135)
    sticker(t, "y3-shock-06", Box(1000, 60, 860, 920), rot=4, border=22, label_="Tu cara (recortada)", radius=60)
    label(t, t.track("text", "Emoji"), "😱", 0.4, 2.6, centered(980, 230, 260, 260), "Inter", 200, "#000000",
          editable=False, motion=[(0, {"s": 0.0}, "back"), (0.35, {})], rotation=keys([(0, -10)]))
    slab(t, "ESTO ES IMPOSIBLE", Box(40, 300, 940, 600), 170, "#FFFFFF", rot=-4, at=0.2, ink="#240046")
    chip(t, "PARTE 2", Box(60, 60, 340, 110), "#FFE600", "#240046", 0.5, font="Luckiest Guy", size=70, weight=400, rot=-5)
    return t


def mini_caja_misterio():
    t = _mini(14, "yt-mini-caja-misterio", "Caja misteriosa", "Mystery box",
              ["caja", "misterio", "unboxing", "sorpresa", "mystery box"], "#0B0B1E")
    bg_gradient(t, [(0, "#1B1464"), (1, "#05030F")], angle=90)
    h = t.solid(t.track("shape", "Halo"), "#FFC300", 0.0, 3.0, centered(1280, 560, 1100, 1100), kind="ellipse",
                layers=[gradient([(0, "#FFC300", 0.55), (1, "#FFC300", 0.0)], angle=0), no_stroke()])
    h["shapeStyle"]["layers"][0]["paint"]["gradient"]["kind"] = "radial"
    sticker(t, "y3-unbox-05", Box(940, 240, 680, 520), rot=-5, label_="Foto de la caja", name="Caja", colour="#FFC300")
    for k, (x, y, s, a) in enumerate(((880, 180, 220, -15), (1720, 230, 260, 12), (1660, 820, 180, 20))):
        slab(t, "?", centered(x, y, s, s * 1.3), int(s * 1.1), "#FFC300", rot=a, at=0.3 + k * 0.15, name="Signo",
             editable=False, ink="#05030F")
    t.photo(t.track("video", "Cara"), "y3-shock-04", 0, 3.0, Box(0, 180, 780, 900), label="Tu cara (recortada)")
    slab(t, "¿QUÉ HAY ADENTRO?", Box(40, 20, 1300, 200), 140, "#FFFFFF", rot=-2, at=0.2, ink="#05030F")
    return t


def mini_cuatro_caras():
    t = _mini(15, "yt-mini-cuatro-caras", "Cuatro caras", "Four faces",
              ["4 personas", "probamos", "reacciones", "grupo", "four reactions"], "#FFE600")
    bg(t, "#FFE600")
    faces = ["y3-shock-01", "y3-shock-04", "y3-shock-10", "y3-shock-12"]
    for i, s in enumerate(faces):
        x, y = (i % 2) * 520 + 20, (i // 2) * 530 + 10
        at = 0.05 + i * 0.12
        t.photo(t.track("video", f"Cara {i + 1}"), s, at, 3.0 - at, Box(x, y, 500, 520), pop(0, 0.3, 0.5),
                label=f"Cara {i + 1}")
    t.solid(t.track("shape", "Divisor"), "#111111", 0, 3.0, Box(510, 0, 20, 1080))
    t.solid(t.track("shape", "Divisor"), "#111111", 0, 3.0, Box(0, 525, 1060, 20))
    sticker(t, "h-food-01", Box(1150, 330, 680, 460), rot=5, label_="Foto de lo que prueban", name="Objeto", at=0.3,
            colour="#111111", border=14)
    slab(t, "4 PRUEBAN", Box(1080, 40, 820, 220), 130, "#FFFFFF", rot=3, at=0.2)
    chip(t, "¿QUIÉN AGUANTA?", Box(1110, 860, 760, 120), "#111111", "#FFE600", 0.6, font="Luckiest Guy", size=74, weight=400)
    return t


def mini_cronometro():
    t = _mini(16, "yt-mini-cronometro", "En 60 segundos", "In 60 seconds",
              ["cronómetro", "60 segundos", "rápido", "reto", "timer"], "#FF5400")
    bg_gradient(t, [(0, "#FF7900"), (1, "#E63900")], angle=135)
    face = centered(1380, 560, 640, 640)
    t.solid(t.track("shape", "Botón"), "#111111", 0.2, 2.8, centered(1380, 200, 130, 90), pop(0, 0.35), radius=18,
            kind="rounded-rectangle")
    t.solid(t.track("shape", "Reloj"), "#FFFFFF", 0.2, 2.8, face, pop(0, 0.4), kind="ellipse",
            layers=[shadow("#000000", 0, 14, 0, 1.0), stroke(14, "#111111"), fill("#FFFFFF")])
    clip = t.solid(t.track("shape", "Tiempo"), "#FF1744", 0.2, 2.8, centered(1380, 560, 560, 560), kind="ellipse",
                   layers=hollow_ring("#FF1744", 70, trim=0.0), rotation=keys([(0, -90)]))
    clip["shapeStyle"]["keyframes"] = {"layer.stroke.trimEnd": keys([(0, 0.0, "out"), (1.6, 0.8)])}
    slab(t, "60", centered(1380, 580, 400, 260), 220, "#111111", ow=0, dy=0, at=0.4, name="Segundos", font="Anton")
    t.photo(t.track("video", "Cara"), "y3-shock-03", 0, 3.0, Box(0, 220, 780, 860), label="Tu cara (recortada)")
    slab(t, "APRENDE ESTO EN 60 SEG", Box(40, 20, 1000, 420), 150, "#FFFFFF", rot=-3, at=0.2, align="left")
    return t


def mini_revelacion():
    t = _mini(17, "yt-mini-revelacion", "Lo que nadie vio", "Hidden reveal",
              ["revelación", "oculto", "censurado", "misterio", "reveal"], "#000000")
    t.photo(t.track("video", "Escena"), "h-house-02", 0, 3.0, t.full,
            label="Foto de lo oculto", effects=[effect("builtin.effects.gaussian_blur", u_blurRadius=28),
                                                effect("color.basic", saturation=0.3, brightness=-0.1)])
    shade_full(t, 0.3)
    clear = t.photo(t.track("video", "Detalle"), "h-house-02", 0.3, 2.7, t.full,
                    label="Foto de lo oculto", reuse="p1", opacity=appear(0.0, 0.3))
    t.mask(t.tracks[-1], clear, "ellipse", x=1300 / 1920, y=470 / 1080, w=620 / 1920, h=620 / 1080)
    ring(t, t.track("shape", "Aro"), "#FF1744", 22, 0.3, 2.7, centered(1300, 470, 640, 640), [(0, {"s": 0.0}, "back"), (0.4, {})])
    t.solid(t.track("shape", "Censura"), "#111111", 0.5, 2.5, Box(860, 820, 900, 120), slide_in(dx=-900, length=0.3),
            rotation=keys([(0, -3)]))
    label(t, t.track("text", "Censura"), "CENSURADO", 0.6, 2.4, Box(860, 820, 900, 120), "Anton", 90, "#FFFFFF",
          weight=400, spacing=14, rotation=keys([(0, -3)]), name="Banda", anim_in=tanim("fade", duration=0.2))
    t.photo(t.track("video", "Cara"), "y3-shock-11", 0, 3.0, Box(0, 160, 820, 920), label="Tu cara (recortada)")
    slab(t, "NADIE LO VIO", Box(40, 20, 1000, 230), 170, "#FFFFFF", rot=-3, at=0.2)
    return t


# =====================================================================================================
# 2. Reseña de tecnología
# =====================================================================================================

def tec_unboxing():
    t = _tec(wide, 0, "yt-tec-unboxing", "Unboxing limpio", "Clean unboxing", 8.0,
             ["unboxing", "qué trae la caja", "minimal"], thumb_at=6.0, background="#F4F3EF")
    bg(t, "#F4F3EF")
    v = t.track("video", "Unboxing")
    a = t.photo(v, "y3-unbox-05", 0, 4.3, Box(760, 0, 1160, 1080), kb(4.3, 1.0, 1.08), label="Foto o video 1")
    b = t.photo(v, "y3-unbox-01", 3.9, 4.1, Box(760, 0, 1160, 1080), kb(4.1, 1.08, 1.0), label="Foto o video 2")
    t.transition(v, a, b, "slide_left", 0.4)
    label(t, t.track("text", "Antetítulo"), "UNBOXING", 0.3, 7.7, Box(110, 150, 600, 50), "Montserrat", 32, "#8A8A8A",
          weight=700, spacing=16, align="left", anim_in=tanim("fade", duration=0.5), name="Antetítulo")
    line(t, t.track("shape", "Acento"), "#FF5A1F", 0.5, 7.5, Box(110, 214, 90, 8))
    label(t, t.track("text", "Producto"), "Auriculares Pro 2", 0.6, 7.4, Box(110, 240, 620, 250), "Sora", 92,
          "#151515", weight=700, align="left", valign="top", line=1.02,
          anim_in=tanim("rise-by-word", duration=0.6, unit="word", stagger=0.12), name="Producto")
    label(t, t.track("text", "Subtítulo"), "LO QUE TRAE LA CAJA", 1.6, 6.4, Box(110, 520, 620, 50), "Montserrat", 30,
          "#FF5A1F", weight=800, spacing=6, align="left", anim_in=tanim("fade", duration=0.4), name="Subtítulo")
    for i, item in enumerate(["Auriculares", "Cable USB-C", "Estuche de viaje", "Guía rápida"]):
        at = 2.2 + i * 0.6
        y = 590 + i * 86
        t.solid(t.track("shape", "Check"), "#151515", at, 8.0 - at, centered(136, y + 32, 52, 52), pop(0, 0.3), kind="ellipse")
        label(t, t.track("text", "Check"), "✓", at, 8.0 - at, centered(136, y + 32, 52, 52), "Inter", 30, "#FFFFFF",
              weight=900, motion=pop(0, 0.3), editable=False)
        label(t, t.track("text", "Elemento"), item, at + 0.05, 7.95 - at, Box(184, y, 560, 64), "Inter", 42, "#222222",
              weight=600, align="left", anim_in=tanim("slide-right", duration=0.35), name=f"Elemento {i + 1}")
    t.solid(t.track("shape", "Progreso"), "#FF5A1F", 0, 8.0, Box(0, 1072, 1920, 8),
            [(0, {"sx": 0.001, "dx": -960}, "linear"), (8.0, {})])
    song(t, "upbeat", 2, 0.7)
    return t


def tec_ficha():
    t = _tec(wide, 1, "yt-tec-ficha-tecnica", "Ficha técnica", "Spec sheet", 10.0,
             ["ficha técnica", "especificaciones", "specs", "celular"], thumb_at=6.8, background="#0B1020")
    bg_gradient(t, [(0, "#141B33"), (1, "#070A16")], angle=120)
    rrect(t, t.track("shape", "Halo"), "#3DDCFF", 0.1, 9.9, Box(110, 140, 700, 800), 44, pop(0, 0.5, 0.85),
          layers=[glow("#3DDCFF", 40, 0.45), fill("#0B1020"), no_stroke()])
    rounded_photo(t, "y3-phone-06", 0.1, 9.9, Box(110, 140, 700, 800), [(0, {"s": 0.85}, "back"), (0.5, {}, "linear"),
                  (9.9, {"s": 1.03})], radius=44, label_="Foto del producto", name="Producto")
    label(t, t.track("text", "Antetítulo"), "FICHA TÉCNICA", 0.5, 9.5, Box(920, 110, 900, 60), "Sora", 36, "#3DDCFF",
          weight=700, spacing=14, align="left", anim_in=tanim("fade", duration=0.4), name="Antetítulo")
    label(t, t.track("text", "Producto"), "Nova 5 Pro", 0.7, 9.3, Box(920, 170, 900, 130), "Sora", 100, "#FFFFFF",
          weight=800, align="left", anim_in=tanim("snap-together", duration=0.6), name="Producto")
    rows = [("Pantalla", "6,7\" OLED", 0.92), ("Batería", "5.000 mAh", 0.85), ("Cámara", "50 MP", 0.74),
            ("Memoria", "256 GB", 0.6), ("Peso", "190 g", 0.45)]
    for i, (k, v, f) in enumerate(rows):
        at = 1.6 + i * 0.7
        y = 350 + i * 128
        label(t, t.track("text", "Dato"), k, at, 10 - at, Box(920, y, 420, 56), "Inter", 36, "#8B95B2", weight=500,
              align="left", anim_in=tanim("fade", duration=0.3), name=f"Dato {i + 1}")
        label(t, t.track("text", "Valor"), v, at + 0.1, 9.9 - at, Box(1320, y - 6, 500, 64), "Sora", 50, "#FFFFFF",
              weight=700, align="right", anim_in=tanim("slide-left", duration=0.35), name=f"Valor {i + 1}")
        t.solid(t.track("shape", "Pista"), "#1F2A4D", at, 10 - at, Box(920, y + 66, 900, 10), radius=5,
                kind="rounded-rectangle")
        grow_bar(t, "#3DDCFF", at + 0.15, Box(920, y + 66, 900, 10), f, length=0.9)
    song(t, "electro", 1, 0.75)
    return t


def tec_comparacion():
    t = _tec(wide, 2, "yt-tec-comparacion", "Comparación lado a lado", "Side-by-side comparison", 10.0,
             ["comparación", "versus", "cuál comprar", "comparison"], thumb_at=7.6, background="#0F0F14")
    bg(t, "#0F0F14")
    for i, (s, name, c) in enumerate((("y3-laptop-01", "MODELO A", "#3D7BFF"), ("y3-laptop-05", "MODELO B", "#FF8A00"))):
        x = 80 + i * 960
        at = 0.2 + i * 0.2
        rounded_photo(t, s, at, 10 - at, Box(x, 60, 800, 440), [(0, {"dy": -600}, "out"), (0.5, {})], radius=30,
                      label_=f"Producto {'AB'[i]}", name=f"Producto {'AB'[i]}")
        chip(t, name, centered(x + 400, 520, 360, 76), c, "#FFFFFF", at + 0.4, font="Montserrat", size=36,
             name=f"Nombre {'AB'[i]}", spacing=6)
    t.solid(t.track("shape", "VS"), "#FFFFFF", 0.6, 9.4, centered(960, 280, 170, 170), pop(0, 0.4), kind="ellipse",
            layers=[shadow("#000000", 0, 8, 20, 0.6), fill("#FFFFFF"), no_stroke()])
    label(t, t.track("text", "VS"), "VS", 0.6, 9.4, centered(960, 285, 170, 170), "Anton", 86, "#0F0F14", weight=400,
          motion=pop(0, 0.4), editable=False)
    rows = [("Pantalla", "14\"", "16\"", 1), ("Batería", "15 h", "9 h", 0), ("Peso", "1,2 kg", "1,9 kg", 0),
            ("Precio", "$899", "$1.199", 0)]
    for i, (k, a, b, win) in enumerate(rows):
        at = 1.6 + i * 0.75
        y = 600 + i * 112
        t.solid(t.track("shape", "Fila"), "#1A1A22", at, 10 - at, Box(80, y, 1760, 96), slide_in(dy=30, length=0.35),
                radius=18, kind="rounded-rectangle", opacity=appear(0, 0.3))
        label(t, t.track("text", "Dato"), k, at, 10 - at, Box(760, y, 400, 96), "Inter", 34, "#9CA3AF", weight=600,
              anim_in=tanim("fade", duration=0.3), name=f"Dato {i + 1}")
        for j, val in enumerate((a, b)):
            cx = 480 + j * 960
            if j == win:
                pill(t, t.track("shape", "Ganador"), "#16A34A", at + 0.45, 9.55 - at, centered(cx, y + 48, 300, 72),
                     pop(0, 0.3))
            label(t, t.track("text", "Valor"), val, at + 0.1, 9.9 - at, centered(cx, y + 48, 400, 90), "Sora", 50,
                  "#FFFFFF", weight=700, anim_in=tanim("pop", duration=0.3), name=f"Valor {'AB'[j]}{i + 1}")
    chip(t, "★ GANADOR", Box(120, 30, 300, 76), "#FACC15", "#111111", 5.4, font="Montserrat", size=34, rot=-5,
         name="Ganador")
    song(t, "electro", 2, 0.7)
    return t


def tec_pros_contras():
    t = _tec(wide, 3, "yt-tec-pros-contras", "Pros y contras", "Pros and cons", 10.0,
             ["pros y contras", "ventajas", "desventajas", "pros and cons"], thumb_at=6.5, background="#F5F5F7")
    bg(t, "#F5F5F7")
    label(t, t.track("text", "Título"), "PROS Y CONTRAS", 0.2, 9.8, Box(100, 40, 1300, 110), "Archivo Black", 84,
          "#111111", weight=400, align="left", anim_in=tanim("slide-up", duration=0.4, unit="word", stagger=0.1),
          name="Título")
    label(t, t.track("text", "Subtítulo"), "después de un mes de uso", 0.5, 9.5, Box(104, 148, 1200, 56), "Inter", 36,
          "#6B6B6B", weight=500, align="left", anim_in=tanim("fade", duration=0.4), name="Subtítulo")
    circle_photo(t, "y3-watch-01", 0.3, 9.7, centered(1710, 125, 190, 190), pop(0, 0.4), ring_colour="#111111",
                 ring_width=6, label="Foto del producto")
    sides = [("PROS", "#16A34A", "+", ["Batería de dos días", "Pantalla muy brillante", "Carga rapidísima"]),
             ("CONTRAS", "#E11D48", "−", ["Correa incómoda", "Pocas apps", "Precio alto"])]
    for j, (head, c, sign, items) in enumerate(sides):
        x = 100 + j * 880
        at = 0.6 + j * 0.2
        rrect(t, t.track("shape", "Tarjeta"), "#FFFFFF", at, 10 - at, Box(x, 240, 840, 780), 30,
              slide_in(dy=60, length=0.5), layers=[shadow("#000000", 0, 10, 30, 0.12), fill("#FFFFFF"), no_stroke()])
        rrect(t, t.track("shape", "Cabecera"), c, at, 10 - at, Box(x, 240, 840, 120), 30, slide_in(dy=60, length=0.5))
        t.solid(t.track("shape", "Cabecera"), c, at, 10 - at, Box(x, 320, 840, 40), slide_in(dy=60, length=0.5))
        label(t, t.track("text", "Cabecera"), head, at + 0.2, 9.8 - at, Box(x, 240, 840, 120), "Archivo Black", 64,
              "#FFFFFF", weight=400, spacing=6, anim_in=tanim("fade", duration=0.3), name=f"Cabecera {j + 1}")
        for i, item in enumerate(items):
            a2 = 1.4 + i * 1.1 + j * 0.55
            y = 400 + i * 200
            t.solid(t.track("shape", "Signo"), c, a2, 10 - a2, centered(x + 90, y + 70, 84, 84), pop(0, 0.3), kind="ellipse")
            label(t, t.track("text", "Signo"), sign, a2, 10 - a2, centered(x + 90, y + 66, 84, 84), "Inter", 64, "#FFFFFF",
                  weight=900, motion=pop(0, 0.3), editable=False)
            label(t, t.track("text", "Punto"), item, a2 + 0.1, 9.9 - a2, Box(x + 160, y, 650, 140), "Inter", 48, "#1A1A1A",
                  weight=600, align="left", anim_in=tanim("slide-right", duration=0.35),
                  name=f"{'Pro' if j == 0 else 'Contra'} {i + 1}")
    song(t, "upbeat", 3, 0.7)
    return t


def tec_puntaje():
    t = _tec(wide, 4, "yt-tec-puntaje", "Puntaje final", "Final score", 8.0,
             ["puntaje", "calificación", "nota", "rating", "score"], thumb_at=5.8, background="#0B0B10")
    t.photo(t.track("video", "Fondo"), "y3-gadget-03", 0, 8.0, t.full, kb(8.0, 1.05, 1.12), label="Foto del producto",
            effects=[effect("builtin.effects.gaussian_blur", u_blurRadius=24)])
    shade_full(t, 0.78, colour="#0B0B10")
    box = centered(560, 560, 600, 600)
    t.solid(t.track("shape", "Pista"), "#FFFFFF", 0.2, 7.8, box, pop(0, 0.4, 0.6), kind="ellipse",
            layers=hollow_ring("#FFFFFF", 40, 0.14))
    fn = lambda f: smooth(f) * 0.87  # noqa: E731
    clip = t.solid(t.track("shape", "Nota"), "#FFD60A", 0.2, 7.8, box, kind="ellipse",
                   layers=hollow_ring("#FFD60A", 40, trim=0.0), rotation=keys([(0, -90)]))
    clip["shapeStyle"]["keyframes"] = {"layer.stroke.trimEnd": curve_keys(fn, 2.4, at=0.5)}
    count_up(t, t.track("text", "Nota"), 0.0, 8.7, "8,7", 0.7, 2.4, centered(560, 530, 520, 230),
             big("Sora", 180, "#FFFFFF", weight=800), power=2.0, decimals=1)
    label(t, t.track("text", "Escala"), "/ 10", 0.7, 7.3, centered(560, 670, 300, 70), "Inter", 46, "#A1A1AA",
          weight=600, anim_in=tanim("fade", duration=0.4), editable=False)
    label(t, t.track("text", "Antetítulo"), "NOTA FINAL", 0.2, 7.8, centered(560, 175, 700, 70), "Sora", 44, "#FFD60A",
          weight=700, spacing=14, anim_in=tanim("fade", duration=0.4), name="Antetítulo")
    subs = [("Diseño", "9,0"), ("Pantalla", "9,2"), ("Batería", "8,5"), ("Sonido", "8,8"), ("Precio", "7,6")]
    for i, (k, v) in enumerate(subs):
        at = 1.0 + i * 0.35
        y = 250 + i * 130
        label(t, t.track("text", "Dato"), k, at, 8 - at, Box(1060, y, 500, 56), "Inter", 38, "#E4E4E7", weight=600,
              align="left", anim_in=tanim("fade", duration=0.3), name=f"Categoría {i + 1}")
        label(t, t.track("text", "Valor"), v, at + 0.6, 7.4 - at, Box(1620, y, 200, 56), "Sora", 42, "#FFD60A",
              weight=800, align="right", anim_in=tanim("pop", duration=0.3), name=f"Nota {i + 1}")
        t.solid(t.track("shape", "Pista"), "#FFFFFF", at, 8 - at, Box(1060, y + 66, 760, 14), radius=7,
                kind="rounded-rectangle", alpha=0.14)
        grow_bar(t, "#FFD60A", at + 0.1, Box(1060, y + 66, 760, 14), float(v.replace(",", ".")) / 10, length=1.0)
    song(t, "electro", 2, 0.75)
    return t


def tec_precio():
    t = _tec(wide, 5, "yt-tec-etiqueta-precio", "Etiqueta de precio", "Price tag", 6.0,
             ["precio", "lanzamiento", "oferta", "price"], thumb_at=4.0, background="#FF5A00")
    bg_gradient(t, [(0, "#FF8A00"), (1, "#FF3D00")], angle=135)
    dots(t, ["#FFFFFF"], 16, 0, 6.0, seed=6125, size=(10, 24), drift=40, alpha=0.35)
    sticker(t, "y3-watch-02", Box(120, 160, 820, 640), rot=-3, label_="Foto del producto", name="Producto",
            motion=[(0, {"dx": -1000}, "out"), (0.5, {}, "linear"), (6.0, {"s": 1.03})])
    swing = keys([(0, -40, "out"), (0.5, 10, "smooth"), (0.9, -5, "smooth"), (1.3, 0)])
    rrect(t, t.track("shape", "Etiqueta"), "#FFFFFF", 0.4, 5.6, centered(1400, 480, 640, 380), 44,
          [(0, {"dy": -900}, "out"), (0.45, {})],
          layers=[shadow("#000000", 0, 16, 30, 0.35), fill("#FFFFFF"), no_stroke()], rotation=swing)
    label(t, t.track("text", "Precio"), "$499", 0.45, 5.55, centered(1400, 510, 620, 240), "Anton", 210, "#111111",
          weight=400, motion=[(0, {"dy": -900}, "out"), (0.4, {})], rotation=swing, name="Precio")
    label(t, t.track("text", "Antetítulo"), "PRECIO DE LANZAMIENTO", 0.45, 5.55, centered(1400, 345, 620, 60), "Montserrat",
          32, "#FF3D00", weight=800, spacing=4, motion=[(0, {"dy": -900}, "out"), (0.4, {})], rotation=swing,
          name="Antetítulo")
    label(t, t.track("text", "Antes"), "Antes $599", 1.8, 4.2, centered(1400, 760, 500, 80), "Inter", 52, "#FFFFFF",
          weight=700, anim_in=tanim("fade", duration=0.3), name="Precio anterior")
    t.solid(t.track("shape", "Tachado"), "#111111", 2.1, 3.9, centered(1400, 770, 380, 8),
            [(0, {"sx": 0.0, "dx": -190}, "out"), (0.3, {})])
    chip(t, "DISPONIBLE YA", centered(1400, 900, 480, 96), "#111111", "#FFFFFF", 2.4, size=38, spacing=6,
         name="Llamada")
    t.adjust([effect("zoom_pulse", animated={"punch": spike([0.85], 0.35, 0.3)})], name="Golpe")
    song(t, "upbeat", 0, 0.8)
    return t


def tec_vale_la_pena():
    t = _tec(tall, 6, "yt-tec-vale-la-pena", "¿Vale lo que cuesta?", "Is it worth the price?", 8.0,
             ["vale la pena", "precio", "opinión", "vertical", "worth it"], thumb_at=6.0, background="#101014")
    bg(t, "#101014")
    t.photo(t.track("video", "Producto"), "y3-watch-04", 0, 8.0, Box(0, 0, 1080, 1140), kb(8.0, 1.0, 1.1),
            label="Foto del producto")
    t.solid(t.track("shape", "Sombra"), "#101014", 0, 8.0, Box(0, 640, 1080, 500),
            layers=[gradient([(0, "#101014", 0.0), (1, "#101014", 1.0)], angle=90), no_stroke()])
    t.solid(t.track("shape", "Fondo"), "#101014", 0, 8.0, Box(0, 1138, 1080, 782))
    rrect(t, t.track("shape", "Etiqueta"), "#FFD60A", 1.0, 7.0, centered(780, 300, 400, 170), 30, pop(0, 0.4),
          layers=[shadow("#000000", 0, 12, 0, 1.0), fill("#FFD60A"), no_stroke()], rotation=keys([(0, 6)]))
    label(t, t.track("text", "Precio"), "$249", 1.0, 7.0, centered(780, 305, 400, 170), "Anton", 130, "#111111",
          weight=400, motion=pop(0, 0.4), rotation=keys([(0, 6)]), name="Precio")
    label(t, t.track("text", "Pregunta"), "¿VALE LO QUE CUESTA?", 0.3, 7.7, Box(60, 1000, 960, 320), "Anton", 130,
          "#FFFFFF", weight=400, line=1.0, anim_in=tanim("slide-up", duration=0.4, unit="word", stagger=0.1),
          name="Pregunta")
    for i, (txt, c) in enumerate((("SÍ", "#16A34A"), ("NO", "#E11D48"))):
        at = 2.2 + i * 0.25
        box = Box(110 + i * 470, 1400, 390, 170)
        pill(t, t.track("shape", "Opción"), c, at, 8 - at, box, pop(0, 0.35))
        label(t, t.track("text", "Opción"), txt, at, 8 - at, box, "Anton", 110, "#FFFFFF", weight=400,
              motion=pop(0, 0.35), name=f"Opción {i + 1}")
    outline(t, t.track("shape", "Elegido"), "#FFFFFF", 10, 4.0, 4.0, Box(90, 1380, 430, 210),
            [(0, {"s": 1.3}, "snap"), (0.3, {})], kind="rounded-rectangle", radius=105)
    t.solid(t.track("shape", "Check"), "#FFFFFF", 4.1, 3.9, centered(470, 1400, 110, 110), pop(0, 0.35), kind="ellipse")
    label(t, t.track("text", "Check"), "✓", 4.1, 3.9, centered(470, 1400, 110, 110), "Inter", 70, "#16A34A", weight=900,
          motion=pop(0, 0.35), editable=False)
    label(t, t.track("text", "Pie"), "Mi respuesta completa en el video", 4.4, 3.6, Box(60, 1660, 960, 80), "Inter", 44,
          "#A1A1AA", weight=500, anim_in=tanim("fade", duration=0.4), name="Pie")
    t.adjust([effect("zoom_pulse", animated={"punch": spike([4.0], 0.3, 0.3)})], name="Golpe")
    song(t, "upbeat", 4, 0.8)
    return t


def _segments(t, n, each, y=40, colour="#FFFFFF"):
    w = (t.w - 80 - (n - 1) * 10) / n
    for i in range(n):
        x = 40 + i * (w + 10)
        t.solid(t.track("shape", "Progreso"), colour, 0, t.duration, Box(x, y, w, 8), radius=4,
                kind="rounded-rectangle", alpha=0.35)
        t.solid(t.track("shape", "Progreso"), colour, i * each, t.duration - i * each, Box(x, y, w, 8),
                [(0, {"sx": 0.001, "dx": -w / 2}, "linear"), (each, {})], radius=4, kind="rounded-rectangle")


def tec_unboxing_vertical():
    t = _tec(tall, 7, "yt-tec-unboxing-vertical", "Unboxing en 4 pasos", "Unboxing in 4 steps", 12.0,
             ["unboxing", "pasos", "vertical", "abriendo la caja"], thumb_at=4.6, background="#111111")
    shots = ["y3-unbox-01", "y3-unbox-02", "y3-unbox-04", "y3-unbox-06"]
    caps = ["Así llega la caja", "Primer vistazo", "Todo lo que trae", "Listo para usar"]
    v = t.track("video", "Pasos")
    prev = None
    for i, s in enumerate(shots):
        at = i * 3.0
        d = 3.0 + (0.35 if i < 3 else 0)
        clip = t.photo(v, s, at, min(d, 12 - at), t.full, kb(d, 1.0, 1.08) if i % 2 == 0 else kb(d, 1.08, 1.0),
                       label=f"Paso {i + 1}")
        if prev:
            t.transition(v, prev, clip, "push_left", 0.35)
        prev = clip
    shade_top(t, 360, 0.55)
    _segments(t, 4, 3.0, y=60)
    chip(t, "UNBOXING", Box(340, 110, 400, 90), "#FFFFFF", "#111111", 0.2, size=40, spacing=10)
    rrect(t, t.track("shape", "Pie"), "#FFFFFF", 0.3, 11.7, Box(60, 1500, 960, 220), 40, slide_in(dy=300, length=0.5),
          layers=[shadow("#000000", 0, 10, 30, 0.35), fill("#FFFFFF"), no_stroke()])
    t.solid(t.track("shape", "Número"), "#FF5A1F", 0.5, 11.5, centered(180, 1610, 150, 150), pop(0, 0.4), kind="ellipse")
    for i, cap in enumerate(caps):
        at = max(0.5, i * 3.0 + 0.1)
        d = (i + 1) * 3.0 - at if i < 3 else 12 - at
        label(t, t.track("text", "Número"), str(i + 1), at, d, centered(180, 1612, 150, 150), "Anton", 100, "#FFFFFF",
              weight=400, anim_in=tanim("pop", duration=0.3), editable=False)
        label(t, t.track("text", "Paso"), cap, at + 0.1, d - 0.1, Box(290, 1520, 700, 180), "Inter", 60, "#111111",
              weight=800, align="left", anim_in=tanim("slide-up", duration=0.3), name=f"Paso {i + 1}")
    song(t, "upbeat", 1, 0.8)
    return t


def tec_veredicto():
    t = _tec(wide, 8, "yt-tec-veredicto", "Veredicto final", "Final verdict", 7.0,
             ["veredicto", "cómpralo", "recomendación", "verdict"], thumb_at=4.6, background="#0B0B0B")
    photo_bg(t, "y3-laptop-02", s1=1.1, label="Foto del producto")
    shade_full(t, 0.55, colour="#0B0B0B")
    rrect(t, t.track("shape", "Tarjeta"), "#FFFFFF", 0.3, 6.7, centered(960, 540, 1100, 660), 40, pop(0, 0.5, 0.8),
          layers=[shadow("#000000", 0, 20, 40, 0.5), fill("#FFFFFF"), no_stroke()])
    label(t, t.track("text", "Antetítulo"), "VEREDICTO", 0.6, 6.4, centered(960, 300, 1000, 60), "Montserrat", 40,
          "#7A7A7A", weight=800, spacing=20, anim_in=tanim("fade", duration=0.4), name="Antetítulo")
    stamp = [(0, {"s": 2.2}, "snap"), (0.25, {})]
    outline(t, t.track("shape", "Sello"), "#16A34A", 14, 1.2, 5.8, centered(960, 480, 800, 210), stamp,
            kind="rounded-rectangle", radius=30, rotation=keys([(0, -6)]))
    label(t, t.track("text", "Sello"), "CÓMPRALO", 1.2, 5.8, centered(960, 486, 800, 210), "Anton", 160, "#16A34A",
          weight=400, spacing=6, motion=stamp, rotation=keys([(0, -6)]), name="Veredicto")
    label(t, t.track("text", "Nota"), "9 / 10", 1.8, 5.2, centered(960, 680, 600, 90), "Sora", 70, "#111111", weight=800,
          anim_in=tanim("pop", duration=0.3), name="Nota")
    label(t, t.track("text", "Ideal"), "Ideal para estudiar y trabajar", 2.2, 4.8, centered(960, 770, 1000, 60), "Inter",
          42, "#555555", weight=500, anim_in=tanim("fade", duration=0.4), name="Ideal para")
    t.adjust([effect("beat_shake", animated={"amount": spike([1.2], 0.5, 0.3)})], name="Golpe")
    song(t, "upbeat", 5, 0.75)
    return t


def tec_setup():
    t = _tec(wide, 9, "yt-tec-setup", "Mi setup de escritorio", "My desk setup", 10.0,
             ["setup", "escritorio", "desk tour", "equipo"], thumb_at=7.2, background="#000000")
    photo_bg(t, "y3-laptop-04", s1=1.05, label="Foto de tu escritorio")
    shade_top(t, 330, 0.6)
    label(t, t.track("text", "Título"), "MI SETUP 2026", 0.3, 9.7, Box(80, 50, 1200, 130), "Archivo Black", 100,
          "#FFFFFF", weight=400, align="left", layers=[shadow("#000000", 0, 6, 20, 0.5), fill("#FFFFFF")],
          anim_in=tanim("slide-up", duration=0.4, unit="word", stagger=0.1), name="Título")
    label(t, t.track("text", "Subtítulo"), "todo lo que uso para trabajar", 0.7, 9.3, Box(84, 180, 1200, 60), "Inter", 40,
          "#FFFFFF", weight=500, align="left", layers=[shadow("#000000", 0, 3, 12, 0.6), fill("#FFFFFF")],
          anim_in=tanim("fade", duration=0.4), name="Subtítulo")
    callouts = [(660, 560, "Laptop 14\"", -1), (990, 565, "Taza de café", 1), (1250, 670, "Libros y libreta", 1),
                (600, 900, "Escritorio blanco", 1)]
    for i, (px, py, txt, side) in enumerate(callouts):
        at = 1.2 + i * 1.2
        d = 10 - at
        ring(t, t.track("shape", "Punto"), "#FFFFFF", 5, at, d, centered(px, py, 60, 60), pop(0, 0.35))
        t.solid(t.track("shape", "Punto"), "#FFD60A", at, d, centered(px, py, 26, 26), pop(0, 0.35), kind="ellipse")
        lx = px + 30 if side > 0 else px - 30 - 170
        t.solid(t.track("shape", "Línea"), "#FFFFFF", at + 0.2, d - 0.2, Box(lx, py - 2, 170, 4),
                [(0, {"sx": 0.001, "dx": -85 * side}, "out"), (0.3, {})])
        w = 40 + len(txt) * 22
        bx = px + 200 if side > 0 else px - 200 - w
        pill(t, t.track("shape", "Etiqueta"), "#111111", at + 0.4, d - 0.4, Box(bx, py - 38, w, 76), pop(0, 0.3),
             opacity=keys([(0, 0.9)]))
        label(t, t.track("text", "Etiqueta"), txt, at + 0.4, d - 0.4, Box(bx, py - 38, w, 76), "Inter", 36, "#FFFFFF",
              weight=700, motion=pop(0, 0.3), name=f"Elemento {i + 1}")
    song(t, "calm", 4, 0.7)
    return t


def tec_tres_cosas():
    t = _tec(tall, 10, "yt-tec-tres-cosas", "3 cosas que no sabías", "3 things you didn't know", 8.0,
             ["datos", "trucos", "funciones ocultas", "vertical", "tips"], thumb_at=6.2, background="#0E1117")
    bg(t, "#0E1117")
    rounded_photo(t, "y3-watch-03", 0.0, 8.0, Box(80, 130, 920, 620), kb(8.0, 1.0, 1.08), radius=40,
                  label_="Foto del producto", name="Producto")
    label(t, t.track("text", "Título"), "3 COSAS QUE NO SABÍAS", 0.3, 7.7, Box(60, 790, 960, 260), "Anton", 120,
          "#FFE600", weight=400, line=1.0, anim_in=tanim("stamp", duration=0.3), name="Título")
    facts = ["Se carga al 50 % en 20 minutos", "Mide tu sueño sin tocarlo", "Aguanta la lluvia y el sudor"]
    for i, f in enumerate(facts):
        at = 1.4 + i * 1.4
        y = 1090 + i * 245
        rrect(t, t.track("shape", "Tarjeta"), "#1C2230", at, 8 - at, Box(60, y, 960, 215), 30,
              slide_in(dx=1100, length=0.45))
        t.solid(t.track("shape", "Número"), "#FFE600", at + 0.2, 7.8 - at, centered(160, y + 107, 120, 120), pop(0, 0.35),
                kind="ellipse")
        label(t, t.track("text", "Número"), str(i + 1), at + 0.2, 7.8 - at, centered(160, y + 110, 120, 120), "Anton", 80,
              "#111111", weight=400, motion=pop(0, 0.35), editable=False)
        label(t, t.track("text", "Dato"), f, at + 0.3, 7.7 - at, Box(250, y + 10, 740, 195), "Inter", 50, "#FFFFFF",
              weight=700, align="left", anim_in=tanim("fade", duration=0.3), name=f"Dato {i + 1}")
    song(t, "upbeat", 6, 0.8)
    return t


def tec_benchmark():
    t = _tec(wide, 11, "yt-tec-benchmark", "Prueba de rendimiento", "Benchmark race", 9.0,
             ["rendimiento", "benchmark", "velocidad", "prueba", "comparación"], thumb_at=6.5, background="#0A0A0F")
    bg_gradient(t, [(0, "#14141F"), (1, "#07070B")], angle=90)
    label(t, t.track("text", "Título"), "PRUEBA DE RENDIMIENTO", 0.2, 8.8, Box(120, 70, 1680, 100), "Sora", 70,
          "#FFFFFF", weight=800, align="left", anim_in=tanim("snap-together", duration=0.5), name="Título")
    label(t, t.track("text", "Subtítulo"), "puntaje del procesador · más es mejor", 0.5, 8.5, Box(124, 170, 1600, 56),
          "Inter", 36, "#8A8A9A", weight=500, align="left", anim_in=tanim("fade", duration=0.4), name="Subtítulo")
    rows = [("Modelo A", "y3-phone-02", 0.92, "12.840", "#22D3EE"), ("Modelo B", "y3-phone-06", 0.71, "9.910", "#A78BFA"),
            ("Modelo C", "y3-laptop-01", 0.55, "7.630", "#A78BFA")]
    for i, (name, s, f, val, c) in enumerate(rows):
        y = 300 + i * 240
        at = 0.5 + i * 0.2
        rounded_photo(t, s, at, 9 - at, Box(120, y, 180, 180), pop(0, 0.35), radius=28, label_=f"Foto {name}",
                      name=f"Foto {i + 1}")
        label(t, t.track("text", "Nombre"), name, at, 9 - at, Box(340, y, 600, 64), "Inter", 42, "#E4E4E7", weight=700,
              align="left", anim_in=tanim("fade", duration=0.3), name=f"Nombre {i + 1}")
        t.solid(t.track("shape", "Pista"), "#1C1C28", at, 9 - at, Box(340, y + 90, 1460, 70), radius=35,
                kind="rounded-rectangle")
        grow_bar(t, c, 1.4 + i * 0.3, Box(340, y + 90, 1460, 70), f, length=2.2, ease="inout")
        label(t, t.track("text", "Valor"), val, 3.5 + i * 0.3, 5.5 - i * 0.3, Box(360, y + 90, 1460 * f - 50, 70), "Sora",
              44, "#0A0A0F", weight=800, align="right", anim_in=tanim("pop", duration=0.3), name=f"Valor {i + 1}")
    chip(t, "★ EL MÁS RÁPIDO", Box(1460, 290, 360, 64), "#22D3EE", "#0A0A0F", 4.2, size=30, name="Ganador")
    song(t, "electro", 0, 0.75)
    return t


def tec_bateria():
    t = _tec(wide, 12, "yt-tec-bateria", "Prueba de batería", "Battery test", 8.0,
             ["batería", "autonomía", "prueba", "battery test", "duración"], thumb_at=6.6, background="#07140C")
    bg_gradient(t, [(0, "#0E2A19"), (1, "#050C08")], angle=120)
    rounded_photo(t, "y3-phonev-04", 0.1, 7.9, Box(140, 140, 480, 800), [(0, {"dx": -700}, "out"), (0.5, {})],
                  radius=40, label_="Foto del producto", name="Producto")
    label(t, t.track("text", "Título"), "PRUEBA DE BATERÍA", 0.3, 7.7, centered(1210, 170, 1000, 70), "Montserrat", 46,
          "#FFFFFF", weight=800, spacing=10, anim_in=tanim("fade", duration=0.4), name="Título")
    outline(t, t.track("shape", "Batería"), "#FFFFFF", 14, 0.4, 7.6, centered(1210, 470, 760, 340), pop(0, 0.4, 0.8),
            kind="rounded-rectangle", radius=56)
    t.solid(t.track("shape", "Batería"), "#FFFFFF", 0.4, 7.6, Box(1600, 410, 40, 120), pop(0, 0.4, 0.8), radius=12,
            kind="rounded-rectangle")
    inner = Box(858, 328, 704, 284)
    end_f, t0, length = 0.12, 0.8, 5.0
    red_at = 5.0
    f_red = 1 - (1 - end_f) * (red_at - t0) / length
    t.solid(t.track("shape", "Carga"), "#22C55E", t0, red_at - t0, inner,
            [(0, {}, "linear"), (red_at - t0, {"sx": f_red, "dx": -inner.w * (1 - f_red) / 2})], radius=34,
            kind="rounded-rectangle")
    t.solid(t.track("shape", "Carga"), "#EF4444", red_at, 8 - red_at, inner,
            [(0, {"sx": f_red, "dx": -inner.w * (1 - f_red) / 2}, "linear"),
             (t0 + length - red_at, {"sx": end_f, "dx": -inner.w * (1 - end_f) / 2})], radius=34, kind="rounded-rectangle")
    count_up(t, t.track("text", "Porcentaje"), 100, 12, "12%", t0, length, centered(1210, 476, 600, 220),
             big("Sora", 150, "#FFFFFF", weight=800, layers=[shadow("#000000", 0, 4, 16, 0.5), fill("#FFFFFF")]),
             power=1.0, suffix="%")
    count_up(t, t.track("text", "Horas"), 0, 18, "18 h", t0, length, centered(1210, 760, 800, 140),
             big("Sora", 110, "#22C55E", weight=800), power=1.0, suffix=" h")
    label(t, t.track("text", "Pie"), "DE USO REAL", 1.0, 7.0, centered(1210, 860, 800, 60), "Montserrat", 36, "#9AE6B4",
          weight=700, spacing=10, anim_in=tanim("fade", duration=0.4), name="Pie")
    song(t, "electro", 3, 0.7)
    return t


def tec_primeras():
    t = _tec(wide, 13, "yt-tec-primeras-impresiones", "Primeras impresiones", "First impressions", 8.0,
             ["primeras impresiones", "reseña", "cinemático", "first look"], thumb_at=5.0, background="#000000")
    photo_bg(t, "y3-cam-02", s1=1.14, label="Foto o video del producto")
    t.solid(t.track("shape", "Sombra"), "#000000", 0, 8.0, Box(0, 0, 1300, 1080),
            layers=[gradient([(0, "#000000", 0.75), (1, "#000000", 0.0)], angle=0), no_stroke()])
    letterbox(t, 2.39)
    label(t, t.track("text", "Antetítulo"), "RESEÑA HONESTA", 0.5, 7.5, Box(120, 44, 900, 50), "Inter", 28, "#BBBBBB",
          weight=600, spacing=12, align="left", anim_in=tanim("fade", duration=0.5), name="Antetítulo")
    label(t, t.track("text", "Título"), "Primeras impresiones", 0.9, 7.1, Box(120, 380, 1500, 180), "DM Serif Display",
          130, "#FFFFFF", weight=400, align="left", anim_in=tanim("rise-by-word", duration=0.7, unit="word", stagger=0.18),
          name="Título")
    line(t, t.track("shape", "Acento"), "#FFB703", 1.5, 6.5, Box(124, 580, 220, 6))
    label(t, t.track("text", "Subtítulo"), "DESPUÉS DE 7 DÍAS DE USO", 1.7, 6.3, Box(124, 610, 1200, 60), "Montserrat",
          36, "#FFB703", weight=700, spacing=12, align="left", anim_in=tanim("fade", duration=0.5), name="Subtítulo")
    grain(t, 0.12)
    song(t, "cine", 2, 0.75)
    return t


def tec_camara():
    t = _tec(wide, 14, "yt-tec-prueba-camara", "Prueba de cámara", "Camera test", 10.0,
             ["cámara", "fotos de prueba", "modo noche", "camera test"], thumb_at=5.0, background="#000000")
    shots = ["h-city-06", "h-nature-02", "h-portrait-02"]
    modes = ["GRAN ANGULAR", "PAISAJE", "RETRATO"]
    v = t.track("video", "Fotos")
    each = 10.0 / 3
    for i, s in enumerate(shots):
        t.photo(v, s, i * each, each, t.full, kb(each, 1.0, 1.06), label=f"Foto de prueba {i + 1}")
    frame = Box(160, 110, 1600, 860)
    corners(t, frame, "#FFFFFF", 0, 10.0, arm=80, th=6)
    live_dot(t, 226, 172, 0, 10.0, size=24)
    label(t, t.track("text", "REC"), "REC", 0, 10.0, Box(250, 147, 200, 50), "Inter", 34, "#FFFFFF", weight=700,
          align="left", editable=False)
    label(t, t.track("text", "Formato"), "4K · 60 FPS", 0, 10.0, Box(1300, 147, 420, 50), "Inter", 32, "#FFFFFF",
          weight=700, align="right", name="Formato")
    label(t, t.track("text", "Ajustes"), "ISO 100    1/250    f/1.8", 0, 10.0, Box(220, 890, 900, 50), "Inter", 32,
          "#FFFFFF", weight=600, spacing=2, align="left", name="Ajustes",
          layers=[shadow("#000000", 0, 2, 8, 0.6), fill("#FFFFFF")])
    for i, m in enumerate(modes):
        at = i * each
        chip(t, m, centered(960, 175, 420, 70), "#FFD60A", "#111111", at + 0.15, each - 0.15, size=32, spacing=6,
             name=f"Modo {i + 1}")
        outline(t, t.track("shape", "Enfoque"), "#FFD60A", 4, at + 0.3, each - 0.3, centered(960, 560, 220, 220),
                [(0, {"s": 1.6}, "out"), (0.35, {}, "hold"), (0.5, {"s": 0.94}, "out"), (0.7, {})])
    for k in (1, 2):
        flash(t, k * each, 0.25, peak=0.85)
    song(t, "calm", 1, 0.7)
    return t


def tec_top3():
    t = _tec(tall, 15, "yt-tec-top-3", "Top 3 gadgets del año", "Top 3 gadgets of the year", 10.0,
             ["top 3", "ranking", "gadgets", "podio", "vertical"], thumb_at=7.4, background="#0B0620")
    bg_gradient(t, [(0, "#2A1260"), (1, "#0B0620")], angle=90)
    dots(t, ["#FFD60A", "#FFFFFF"], 20, 0, 10, seed=6135, size=(6, 16), drift=60, alpha=0.6)
    glow_ = t.solid(t.track("shape", "Brillo"), "#FFD60A", 4.4, 5.6, centered(540, 1030, 620, 620),
                    [(0, {"s": 0.0}, "out"), (0.6, {})], kind="burst", alpha=0.3, rotation=keys([(0, 0), (5.6, 40)]))
    geo(glow_, points=16, innerRatio=0.2)
    label(t, t.track("text", "Título"), "TOP 3 GADGETS DEL AÑO", 0.2, 9.8, Box(60, 120, 960, 300), "Anton", 128, "#FFFFFF",
          weight=400, line=1.0, anim_in=tanim("stamp", duration=0.3), name="Título")
    base = 1800
    places = [(3, 860, 300, "#CD7F32", "y3-keyb-02", "Teclado", 1.0),
              (2, 220, 420, "#C0C0C0", "y3-gadget-03", "Auriculares", 2.5),
              (1, 540, 600, "#FFD60A", "y3-watch-01", "Reloj", 4.0)]
    for n, cx, h, c, s, name, at in places:
        d = 10 - at
        t.solid(t.track("shape", "Podio"), c, at, d, Box(cx - 160, base - h, 320, h + 140),
                [(0, {"sy": 0.001, "dy": (h + 140) / 2}, "out"), (0.6, {})],
                layers=[gradient([(0, c), (1, c, 0.55)], angle=90), no_stroke()])
        label(t, t.track("text", "Puesto"), str(n), at + 0.4, d - 0.4, Box(cx - 160, base - h + 10, 320, 200), "Anton", 180,
              "#111111", weight=400, anim_in=tanim("pop", duration=0.3), editable=False)
        label(t, t.track("text", "Nombre"), name, at + 0.5, d - 0.5, Box(cx - 160, base - h + 210, 320, 70), "Inter", 40,
              "#111111", weight=800, anim_in=tanim("fade", duration=0.3), name=f"Puesto {n}")
        circle_photo(t, s, at + 0.5, d - 0.5, centered(cx, base - h - 170, 280, 280), pop(0, 0.4), ring_colour=c,
                     ring_width=12, label=f"Foto del puesto {n}")
    confetti(t, ["#FFD60A", "#FFFFFF", "#C0C0C0"], 4.3, 5.7, seed=6135, lanes=3, density=0.3)
    song(t, "upbeat", 0, 0.8)
    return t


def tec_capitulos():
    t = _tec(wide, 16, "yt-tec-capitulos", "Capítulos de la reseña", "Review chapters", 8.0,
             ["capítulos", "índice", "reseña completa", "chapters"], thumb_at=4.2, background="#000000")
    photo_bg(t, "y3-laptop-03", s1=1.08, label="Foto del producto")
    shade_bottom(t, 620, 0.9)
    label(t, t.track("text", "Antetítulo"), "RESEÑA COMPLETA", 0.3, 7.7, Box(120, 600, 1200, 56), "Montserrat", 34,
          "#FFD60A", weight=800, spacing=12, align="left", anim_in=tanim("fade", duration=0.4), name="Antetítulo")
    label(t, t.track("text", "Producto"), "Laptop Air 14", 0.5, 7.5, Box(120, 650, 1400, 140), "Sora", 110, "#FFFFFF",
          weight=800, align="left", anim_in=tanim("slide-up", duration=0.4, unit="word", stagger=0.1), name="Producto")
    chapters = [("Diseño", "0:00"), ("Pantalla", "2:15"), ("Batería", "5:40"), ("Rendimiento", "8:05"), ("Precio", "11:30")]
    x0, w, gap, y = 120, 1680, 12, 920
    seg = (w - gap * 4) / 5
    t.solid(t.track("shape", "Barra"), "#FFFFFF", 0.6, 7.4, Box(x0, y, w, 14), alpha=0.25)
    t.solid(t.track("shape", "Avance"), "#FFD60A", 0.6, 7.4, Box(x0, y, w, 14),
            [(0, {"sx": 0.001, "dx": -w / 2}, "linear"), (6.8, {})])
    for i in range(1, 5):
        t.solid(t.track("shape", "Corte"), "#000000", 0.6, 7.4, Box(x0 + i * (seg + gap) - gap, y - 4, gap, 22))
    t.solid(t.track("shape", "Cabezal"), "#FFFFFF", 0.6, 7.4, centered(x0, y + 7, 34, 34),
            [(0, {}, "linear"), (6.8, {"dx": w})], kind="ellipse")
    for i, (name, tc) in enumerate(chapters):
        x = x0 + i * (seg + gap)
        at = 0.8 + i * 0.15
        label(t, t.track("text", "Capítulo"), name, at, 8 - at, Box(x, y - 70, seg, 56), "Inter", 36, "#FFFFFF",
              weight=700, align="left", anim_in=tanim("fade", duration=0.3), name=f"Capítulo {i + 1}")
        label(t, t.track("text", "Tiempo"), tc, at, 8 - at, Box(x, y + 30, seg, 50), "Inter", 30, "#BBBBBB", weight=500,
              align="left", anim_in=tanim("fade", duration=0.3), name=f"Tiempo {i + 1}")
    song(t, "calm", 3, 0.7)
    return t


def tec_comparacion_vertical():
    t = _tec(tall, 17, "yt-tec-comparacion-vertical", "¿Cuál comprar?", "Which one to buy?", 10.0,
             ["comparación", "versus", "vertical", "cuál comprar", "which one"], thumb_at=7.2, background="#111111")
    for i, (s, y) in enumerate((("y3-phone-02", 0), ("y3-phone-06", 980))):
        t.photo(t.track("video", f"Producto {'AB'[i]}"), s, 0, 10, Box(0, y, 1080, 940),
                kb(10, 1.0, 1.08), label=f"Producto {'AB'[i]}")
    shade_full(t, 0.25)
    for i, (name, specs, y, wins) in enumerate((("MODELO A", ["48 MP", "5.000 mAh", "$499"], 80, [False, True, True]),
                                                ("MODELO B", ["50 MP", "4.500 mAh", "$549"], 1060, [True, False, False]))):
        at = 0.4 + i * 0.3
        label(t, t.track("text", "Nombre"), name, at, 10 - at, Box(60, y, 700, 120), "Anton", 110, "#FFFFFF", weight=400,
              align="left", layers=[shadow("#000000", 0, 6, 20, 0.7), fill("#FFFFFF")],
              anim_in=tanim("slide-right", duration=0.4), name=f"Nombre {'AB'[i]}")
        for k, (sp, w) in enumerate(zip(specs, wins)):
            a2 = 1.6 + k * 0.8 + i * 0.3
            chip(t, sp, Box(620, y + 170 + k * 130, 400, 100), "#16A34A" if w else "#1F1F1F", "#FFFFFF", a2, size=44,
                 name=f"Dato {'AB'[i]}{k + 1}", motion=slide_in(dx=500, length=0.35))
    t.solid(t.track("shape", "Banda"), "#FFE600", 0.2, 9.8, Box(-60, 880, 1200, 160), slide_in(dx=-1200, length=0.4),
            rotation=keys([(0, -4)]))
    label(t, t.track("text", "Banda"), "¿CUÁL COMPRAR?", 0.3, 9.7, Box(0, 880, 1080, 160), "Anton", 100, "#111111",
          weight=400, rotation=keys([(0, -4)]), anim_in=tanim("pop", duration=0.3), name="Pregunta")
    chip(t, "★ GANADOR", Box(60, 220, 340, 84), "#FACC15", "#111111", 5.6, size=36, rot=-5, name="Ganador")
    song(t, "electro", 1, 0.8)
    return t


# =====================================================================================================
# 3. Podcast en video
# =====================================================================================================

def pod_dos_camaras():
    t = _pod(wide, 0, "yt-pod-dos-camaras", "Podcast a dos cámaras", "Two-camera podcast", 10.0,
             ["dos cámaras", "nombres", "entrevista", "two cameras"], thumb_at=5.0, background="#101014")
    bg(t, "#101014")
    t.solid(t.track("shape", "Barra"), "#18181F", 0, 10, Box(0, 0, 1920, 120))
    label(t, t.track("text", "Programa"), "CHARLA ABIERTA", 0.2, 9.8, Box(60, 0, 800, 120), "Montserrat", 42, "#FFFFFF",
          weight=900, spacing=8, align="left", anim_in=tanim("fade", duration=0.4), name="Nombre del podcast")
    label(t, t.track("text", "Episodio"), "EP. 42 · Hábitos que cambian todo", 0.4, 9.6, Box(760, 0, 1040, 120), "Inter",
          34, "#A1A1AA", weight=600, align="right", anim_in=tanim("fade", duration=0.4), name="Episodio")
    live_dot(t, 1855, 60, 0, 10)
    people = [("y3-pod-04", "Daniel Rojas", "Anfitrión", "#7C3AED"), ("y3-pod-02", "Lucía Méndez", "Invitada", "#F59E0B")]
    for i, (s, name, role, c) in enumerate(people):
        x = 40 + i * 940
        at = 0.1 + i * 0.15
        rounded_photo(t, s, at, 10 - at, Box(x, 150, 900, 790), [(0, {"s": 0.9}, "out"), (0.4, {}, "linear"),
                      (10 - at, {"s": 1.03})], radius=30, label_=f"Cámara {i + 1}", name=f"Cámara {i + 1}")
        name_plate(t, name, role, x + 30, 770, 500, c, 0.8 + i * 0.3, 9.2 - i * 0.3, name_label=f"Nombre {i + 1}",
                   role_label=f"Rol {i + 1}")
        wave_bars(t, x + 600, 840, 12, 22, 12, 90, [c], 0.8, 9.2, seed=6140 + i)
    label(t, t.track("text", "Subtítulo"), "«Lo importante es empezar, aunque sea pequeño.»", 1.5, 8.5,
          Box(40, 955, 1840, 110), "Inter", 44, "#FFFFFF", weight=600, anim_in=tanim("fade", duration=0.4),
          name="Subtítulo")
    song(t, "jazz", 1, 0.45)
    return t


def pod_cortes():
    t = _pod(wide, 1, "yt-pod-cortes", "Podcast con cortes", "Podcast with cuts", 12.0,
             ["cortes", "plano general", "conversación", "multicam"], thumb_at=4.0, background="#000000")
    v = t.track("video", "Planos")
    plan = [(0.0, 3.0, "y3-pod-08", "Plano general"), (3.0, 2.0, "y3-pod-04", "Cámara 1"),
            (5.0, 2.0, "y3-pod-02", "Cámara 2"), (7.0, 1.5, "p2", None), (8.5, 1.5, "p3", None), (10.0, 2.0, "p1", None)]
    for i, (at, d, s, lab) in enumerate(plan):
        m = kb(d, 1.0, 1.04) if i % 2 == 0 else kb(d, 1.06, 1.02)
        if lab:
            t.photo(v, s, at, d, t.full, m, label=lab)
        else:
            first = next(sl for sl in t.slots if sl.id == s)
            t.photo(v, first.sample, at, d, t.full, m, reuse=s)
    shade_bottom(t, 420, 0.7)
    label(t, t.track("text", "Título"), "¿Se puede vivir de lo que te gusta?", 0.3, 2.6, Box(100, 820, 1720, 150),
          "Montserrat", 70, "#FFFFFF", weight=800, anim_in=tanim("rise-by-word", duration=0.5, unit="word", stagger=0.08),
          anim_out=tanim("fade", duration=0.2), name="Título del episodio")
    name_plate(t, "Daniel Rojas", "Anfitrión", 100, 840, 520, "#0EA5E9", 3.15, 1.8)
    name_plate(t, "Lucía Méndez", "Invitada", 100, 840, 520, "#F43F5E", 5.15, 1.8, name_label="Nombre 2",
               role_label="Rol 2")
    label(t, t.track("text", "Cierre"), "EPISODIO COMPLETO EN EL CANAL", 10.3, 1.7, Box(100, 880, 1720, 80), "Montserrat",
          44, "#FFFFFF", weight=800, spacing=8, anim_in=tanim("fade", duration=0.4), name="Cierre")
    rrect(t, t.track("shape", "Insignia"), "#FFFFFF", 0, 12, Box(50, 50, 250, 72), 36, alpha=0.92)
    label(t, t.track("text", "Insignia"), "EP. 18", 0, 12, Box(50, 50, 250, 72), "Montserrat", 36, "#111111", weight=900,
          spacing=3, name="Episodio")
    song(t, "jazz", 2, 0.4)
    return t


def pod_audiograma():
    t = _pod(wide, 2, "yt-pod-audiograma", "Audiograma", "Audiogram", 10.0,
             ["audiograma", "onda de audio", "clip", "audiogram", "waveform"], thumb_at=6.0, background="#0F0A24")
    bg_gradient(t, [(0, "#2D1B69"), (1, "#0F0A24")], angle=135)
    circle_photo(t, "y3-pod-05", 0.2, 9.8, centered(420, 470, 520, 520), pop(0, 0.5, 0.6), ring_colour="#FF7AB6",
                 ring_width=14, label="Foto del podcast")
    label(t, t.track("text", "Programa"), "NOCHES DE CHARLA", 0.6, 9.4, centered(420, 800, 760, 60), "Montserrat", 38,
          "#FF7AB6", weight=800, spacing=8, anim_in=tanim("fade", duration=0.4), name="Nombre del podcast")
    label(t, t.track("text", "Episodio"), "EPISODIO 09", 0.8, 9.2, centered(420, 860, 760, 50), "Inter", 32, "#C4B5FD",
          weight=600, spacing=4, anim_in=tanim("fade", duration=0.4), name="Episodio")
    label(t, t.track("text", "Cita"), "«Nadie te cuenta lo difícil que es empezar.»", 0.5, 9.5, Box(840, 140, 980, 380),
          "DM Serif Display", 76, "#FFFFFF", weight=400, align="left", valign="bottom",
          anim_in=tanim("rise-by-word", duration=0.5, unit="word", stagger=0.12), name="Cita")
    wave_bars(t, 852, 650, 40, 24, 12, 200, ["#FF7AB6", "#FFFFFF"], 0.2, 9.8, seed=6142)
    t.solid(t.track("shape", "Pista"), "#FFFFFF", 0.2, 9.8, Box(840, 830, 960, 8), radius=4, kind="rounded-rectangle",
            alpha=0.2)
    t.solid(t.track("shape", "Avance"), "#FF7AB6", 0.2, 9.8, Box(840, 830, 960, 8),
            [(0, {"sx": 0.25, "dx": -960 * 0.75 / 2}, "linear"), (9.8, {"sx": 0.42, "dx": -960 * 0.58 / 2})], radius=4,
            kind="rounded-rectangle")
    label(t, t.track("text", "Tiempo"), "12:41", 0.2, 9.8, Box(840, 850, 300, 50), "Inter", 30, "#C4B5FD", weight=600,
          align="left", editable=False)
    label(t, t.track("text", "Tiempo"), "48:20", 0.2, 9.8, Box(1500, 850, 300, 50), "Inter", 30, "#C4B5FD", weight=600,
          align="right", name="Duración")
    song(t, "calm", 1, 0.5)
    return t


def pod_titulo():
    t = _pod(wide, 3, "yt-pod-titulo-episodio", "Título del episodio", "Episode title card", 6.0,
             ["título", "episodio", "portada", "title card"], thumb_at=3.6, background="#F4EDE4")
    bg(t, "#F4EDE4")
    t.solid(t.track("shape", "Bloque"), "#E85D3F", 0, 6, Box(0, 0, 760, 1080), slide_in(dx=-760, length=0.5))
    label(t, t.track("text", "EP"), "EP.", 0.3, 5.7, Box(90, 90, 600, 170), "Anton", 150, "#F4EDE4", weight=400,
          align="left", anim_in=tanim("slide-up", duration=0.4), editable=False)
    label(t, t.track("text", "Número"), "57", 0.4, 5.6, Box(70, 330, 700, 560), "Anton", 520, "#F4EDE4", weight=400,
          align="left", anim_in=tanim("slide-up", duration=0.5), name="Número de episodio")
    label(t, t.track("text", "Antetítulo"), "NUEVO EPISODIO", 0.6, 5.4, Box(860, 230, 980, 60), "Montserrat", 36,
          "#E85D3F", weight=800, spacing=12, align="left", anim_in=tanim("fade", duration=0.4), name="Antetítulo")
    label(t, t.track("text", "Título"), "Cómo empezar desde cero", 0.8, 5.2, Box(860, 300, 980, 380), "DM Serif Display",
          120, "#1E1E1E", weight=400, align="left", valign="top", line=1.02,
          anim_in=tanim("rise-by-word", duration=0.5, unit="word", stagger=0.12), name="Título")
    line(t, t.track("shape", "Línea"), "#1E1E1E", 1.4, 4.6, Box(864, 700, 160, 8))
    label(t, t.track("text", "Invitado"), "con Sofía Paredes", 1.6, 4.4, Box(860, 730, 700, 70), "Inter", 46, "#3A3A3A",
          weight=600, align="left", anim_in=tanim("fade", duration=0.4), name="Invitado")
    label(t, t.track("text", "Fecha"), "Jueves · 20:00", 1.8, 4.2, Box(860, 805, 700, 60), "Inter", 36, "#8A8A8A",
          weight=500, align="left", anim_in=tanim("fade", duration=0.4), name="Fecha")
    circle_photo(t, "y3-pod-10", 1.2, 4.8, centered(1690, 860, 250, 250), pop(0, 0.4), ring_colour="#E85D3F",
                 ring_width=8, label="Foto del invitado")
    song(t, "jazz", 3, 0.6)
    return t


def pod_invitado():
    t = _pod(wide, 4, "yt-pod-invitado", "Presentación del invitado", "Guest intro", 8.0,
             ["invitado", "presentación", "entrevista", "guest"], thumb_at=5.2, background="#0E1A2B")
    bg(t, "#0E1A2B")
    t.photo(t.track("video", "Invitado"), "y3-pod-10", 0, 8, Box(900, 0, 1020, 1080), kb(8, 1.05, 1.0),
            label="Foto del invitado")
    t.solid(t.track("shape", "Fundido"), "#0E1A2B", 0, 8, Box(900, 0, 360, 1080),
            layers=[gradient([(0, "#0E1A2B", 1.0), (1, "#0E1A2B", 0.0)], angle=0), no_stroke()])
    label(t, t.track("text", "Antetítulo"), "HOY NOS ACOMPAÑA", 0.4, 7.6, Box(120, 210, 800, 60), "Montserrat", 36,
          "#4FD1C5", weight=800, spacing=12, align="left", anim_in=tanim("fade", duration=0.4), name="Antetítulo")
    label(t, t.track("text", "Nombre"), "Valeria Soto", 0.7, 7.3, Box(120, 270, 860, 300), "Playfair Display", 130,
          "#FFFFFF", weight=700, align="left", valign="top", line=1.0,
          anim_in=tanim("rise-by-word", duration=0.6, unit="word", stagger=0.15), name="Nombre del invitado")
    label(t, t.track("text", "Rol"), "Arquitecta y escritora", 1.2, 6.8, Box(120, 580, 800, 70), "Inter", 46, "#CBD5E1",
          weight=500, align="left", anim_in=tanim("fade", duration=0.4), name="A qué se dedica")
    for i, fact in enumerate(["12 años diseñando casas", "Autora de 3 libros", "Vive entre dos países"]):
        at = 2.0 + i * 0.5
        y = 700 + i * 84
        t.solid(t.track("shape", "Viñeta"), "#4FD1C5", at, 8 - at, centered(136, y + 32, 20, 20), pop(0, 0.3),
                kind="ellipse")
        label(t, t.track("text", "Dato"), fact, at, 8 - at, Box(170, y, 740, 64), "Inter", 40, "#FFFFFF", weight=600,
              align="left", anim_in=tanim("slide-right", duration=0.35), name=f"Dato {i + 1}")
    song(t, "calm", 2, 0.55)
    return t


def pod_cita():
    t = _pod(tall, 5, "yt-pod-cita", "Cita para clips", "Quote card", 8.0,
             ["cita", "frase", "clip", "vertical", "quote"], thumb_at=5.6, background="#F3EBDD")
    bg(t, "#F3EBDD")
    label(t, t.track("text", "Comillas"), "“", 0.1, 7.9, Box(50, 120, 500, 520), "DM Serif Display", 560, "#D97757",
          weight=400, align="left", valign="top", anim_in=tanim("pop", duration=0.4), editable=False)
    label(t, t.track("text", "Cita"), "Lo que no se mide, no se puede mejorar.", 0.5, 7.5, Box(80, 560, 920, 720),
          "DM Serif Display", 116, "#1F1A17", weight=400, align="left", valign="top", line=1.08,
          anim_in=tanim("rise-by-word", duration=0.5, unit="word", stagger=0.12), name="Cita")
    circle_photo(t, "y3-pod-02", 1.6, 6.4, centered(190, 1400, 200, 200), pop(0, 0.4), ring_colour="#D97757",
                 ring_width=8, label="Foto de quien lo dijo")
    label(t, t.track("text", "Nombre"), "Lucía Méndez", 1.8, 6.2, Box(330, 1340, 700, 64), "Montserrat", 50, "#1F1A17",
          weight=800, align="left", anim_in=tanim("fade", duration=0.4), name="Nombre")
    label(t, t.track("text", "Rol"), "Invitada · EP. 31", 1.9, 6.1, Box(330, 1408, 700, 60), "Inter", 38, "#7A6A5D",
          weight=500, align="left", anim_in=tanim("fade", duration=0.4), name="Rol")
    wave_bars(t, 100, 1640, 36, 25, 12, 110, ["#D97757", "#1F1A17"], 0.3, 7.7, seed=6145)
    label(t, t.track("text", "Programa"), "CHARLA ABIERTA", 0.3, 7.7, centered(540, 1800, 900, 50), "Montserrat", 32,
          "#7A6A5D", weight=800, spacing=10, anim_in=tanim("fade", duration=0.4), name="Nombre del podcast")
    song(t, "calm", 2, 0.5)
    return t


def pod_clip_vertical():
    t = _pod(tall, 6, "yt-pod-clip-vertical", "Clip vertical a dos cámaras", "Two-camera vertical clip", 15.0,
             ["clip", "vertical", "dos cámaras", "subtítulos", "shorts"], thumb_at=4.5, background="#0B0B0F")
    bg(t, "#0B0B0F")
    label(t, t.track("text", "Programa"), "CHARLA ABIERTA", 0.1, 14.9, centered(540, 105, 1000, 70), "Montserrat", 46,
          "#FFFFFF", weight=900, spacing=8, anim_in=tanim("fade", duration=0.4), name="Nombre del podcast")
    label(t, t.track("text", "Episodio"), "EP. 42 · Hábitos que cambian todo", 0.3, 14.7, centered(540, 170, 1000, 50),
          "Inter", 34, "#A1A1AA", weight=600, anim_in=tanim("fade", duration=0.4), name="Episodio")
    cams = [("y3-pod-04", 250, "Daniel"), ("y3-pod-02", 980, "Lucía")]
    for i, (s, y, name) in enumerate(cams):
        t.photo(t.track("video", f"Cámara {i + 1}"), s, 0, 15, Box(0, y, 1080, 690), kb(15, 1.0, 1.06),
                label=f"Cámara {i + 1}")
        chip(t, name, Box(40, y + 590, 260, 70), "#111111", "#FFFFFF", 0.5, 14.5, size=34, name=f"Nombre {i + 1}",
             motion=slide_in(dx=-300, length=0.4))
    for k in range(5):
        y = 250 if k % 2 == 0 else 980
        outline(t, t.track("shape", "Habla"), "#FFE600", 8, k * 3.0, 3.0, Box(0, y, 1080, 690))
    caps = ["Yo pensaba que necesitaba", "¿Y qué cambió?", "Empecé con diez minutos al día",
            "¿Solo diez?", "Sí, y eso lo cambió todo"]
    for k, c in enumerate(caps):
        label(t, t.track("text", "Subtítulo"), c, k * 3.0 + 0.05, 2.9, Box(60, 895, 960, 130), "Montserrat", 54,
              "#111111", weight=900, box_bg=("#FFE600", 1.0), box_pad=16, box_radius=12,
              anim_in=tanim("pop", duration=0.25, unit="word", stagger=0.06), name=f"Subtítulo {k + 1}")
    label(t, t.track("text", "Pie"), "Mira el episodio completo", 0.5, 14.5, centered(540, 1745, 960, 60), "Inter", 38,
          "#D4D4D8", weight=600, anim_in=tanim("fade", duration=0.4), name="Pie")
    t.solid(t.track("shape", "Pista"), "#FFFFFF", 0, 15, Box(60, 1810, 960, 10), radius=5, kind="rounded-rectangle",
            alpha=0.2)
    t.solid(t.track("shape", "Avance"), "#FFE600", 0, 15, Box(60, 1810, 960, 10),
            [(0, {"sx": 0.001, "dx": -480}, "linear"), (15, {})], radius=5, kind="rounded-rectangle")
    song(t, "jazz", 1, 0.3)
    return t


def pod_clip_subtitulos():
    t = _pod(tall, 7, "yt-pod-clip-subtitulos", "Clip con subtítulos grandes", "Clip with big captions", 12.0,
             ["subtítulos", "clip", "vertical", "frase", "captions"], thumb_at=4.4, background="#000000")
    photo_bg(t, "y3-podv-04", s1=1.1, label="Video del clip")
    shade_bottom(t, 1000, 0.85)
    shade_top(t, 320, 0.5)
    pill(t, t.track("shape", "Episodio"), "#FF4D6D", 0.2, 11.8, Box(60, 110, 220, 80), pop(0, 0.3))
    label(t, t.track("text", "Episodio"), "EP. 31", 0.2, 11.8, Box(60, 110, 220, 80), "Montserrat", 38, "#FFFFFF",
          weight=900, motion=pop(0, 0.3), name="Episodio")
    label(t, t.track("text", "Programa"), "CHARLA ABIERTA", 0.3, 11.7, Box(305, 110, 720, 80), "Montserrat", 38,
          "#FFFFFF", weight=800, spacing=6, align="left", anim_in=tanim("fade", duration=0.4), name="Nombre del podcast")
    label(t, t.track("text", "Nombre"), "LUCÍA MÉNDEZ", 0.4, 11.6, Box(60, 1120, 960, 60), "Montserrat", 40, "#FF4D6D",
          weight=800, spacing=8, anim_in=tanim("fade", duration=0.4), name="Quién habla")
    caps = ["El miedo *nunca* se va del todo", "Solo aprendes a *caminar* con él", "Y un día te das *cuenta*",
            "de que ya *llegaste*"]
    accent = {"rule": "none", "colorEnabled": True, "color": "#ffffe600", "sizeScale": 1.0}
    for k, c in enumerate(caps):
        style = big("Montserrat", 92, "#FFFFFF", weight=900, layers=[shadow("#000000", 0, 6, 0, 0.9), fill("#FFFFFF")],
                    accent=accent, line=1.05, anim_in=tanim("rise-by-word", duration=0.3, unit="word", stagger=0.12))()
        t.text(t.track("text", "Subtítulo"), c, k * 3.0 + 0.1, 2.85, Box(60, 1200, 960, 380), style,
               label=f"Subtítulo {k + 1}")
    t.solid(t.track("shape", "Avance"), "#FF4D6D", 0, 12, Box(60, 1700, 960, 10),
            [(0, {"sx": 0.001, "dx": -480}, "linear"), (12, {})], radius=5, kind="rounded-rectangle")
    song(t, "calm", 0, 0.3)
    return t


def pod_pregunta():
    t = _pod(wide, 8, "yt-pod-pregunta", "La pregunta de hoy", "Today's question", 8.0,
             ["pregunta", "debate", "tema del día", "question"], thumb_at=5.2, background="#FFD23F")
    bg(t, "#FFD23F")
    label(t, t.track("text", "Fondo"), "?", 0, 8, Box(1120, -160, 900, 1400), "Archivo Black", 1300, "#111111",
          weight=400, layers=[fill("#111111", 0.08)], editable=False)
    chip(t, "LA PREGUNTA DE HOY", Box(120, 110, 600, 84), "#111111", "#FFD23F", 0.2, size=36, spacing=4,
         motion=slide_in(dx=-700, length=0.4))
    label(t, t.track("text", "Pregunta"), "¿Qué harías si no tuvieras miedo a fallar?", 0.6, 7.4, Box(120, 250, 1100, 640),
          "Archivo Black", 104, "#111111", weight=400, align="left", valign="top", line=1.05,
          anim_in=tanim("rise-by-word", duration=0.4, unit="word", stagger=0.1), name="Pregunta")
    sticker(t, "y3-podv-02", Box(1320, 170, 500, 640), at=3.0, rot=3, label_="Foto de quien responde", name="Responde",
            motion=[(0, {"dx": 700}, "out"), (0.5, {})])
    chip(t, "RESPONDE: LUCÍA", Box(1320, 860, 500, 90), "#111111", "#FFFFFF", 3.5, size=38, spacing=3,
         name="Quién responde")
    song(t, "upbeat", 5, 0.5)
    return t


def pod_apertura():
    t = _pod(wide, 9, "yt-pod-apertura", "Apertura del episodio", "Cold open", 7.0,
             ["apertura", "avance", "teaser", "cold open", "intro"], thumb_at=5.2, background="#0A0A0A")
    v = t.track("video", "Avance")
    shots = [("y3-pod-01", "Momento 1"), ("y3-pod-07", "Momento 2"), ("y3-pod-09", "Momento 3")]
    for i, (s, lab) in enumerate(shots):
        t.photo(v, s, i * 1.2, 1.2, t.full, [(0, {"s": 1.2}, "snap"), (0.25, {"s": 1.05}, "linear"), (1.2, {"s": 1.0})],
                label=lab, effects=[effect("color.basic", contrast=0.2, saturation=-0.2)])
    for i, q in enumerate(["Nunca lo había contado…", "¿En serio pasó eso?", "Eso lo cambió todo"]):
        label(t, t.track("text", "Frase"), q, i * 1.2 + 0.1, 1.05, Box(160, 800, 1600, 140), "Montserrat", 64, "#FFFFFF",
              weight=900, box_bg=("#000000", 0.85), box_pad=20, box_radius=8, anim_in=tanim("pop", duration=0.2),
              name=f"Frase {i + 1}")
    panels(t, ["#E11D48", "#0A0A0A"], 3.3, "left", length=0.35, hold=0.0)
    t.solid(t.track("shape", "Fondo"), "#0A0A0A", 3.6, 3.4)
    label(t, t.track("text", "Programa"), "SIN FILTRO", 3.8, 3.2, Box(0, 330, 1920, 330), "Anton", 280, "#FFFFFF",
          weight=400, spacing=8, anim_in=tanim("stamp", duration=0.3), name="Nombre del podcast")
    line(t, t.track("shape", "Línea"), "#E11D48", 4.2, 2.8, centered(960, 690, 600, 10), grow="c")
    label(t, t.track("text", "Lema"), "NUEVO EPISODIO CADA LUNES", 4.4, 2.6, Box(0, 720, 1920, 70), "Montserrat", 42,
          "#E11D48", weight=800, spacing=12, anim_in=tanim("fade", duration=0.4), name="Lema")
    t.adjust([effect("digital_glitch", animated={"intensity": spike([1.2, 2.4, 3.8], 0.8, 0.25)}),
              effect("zoom_pulse", animated={"punch": spike([3.8], 0.5, 0.3)})], name="Golpes")
    song(t, "cine", 0, 0.8)
    return t


def pod_panel_tres():
    t = _pod(wide, 10, "yt-pod-panel-tres", "Mesa redonda de tres", "Three-person panel", 10.0,
             ["mesa redonda", "panel", "tres invitados", "debate", "panel show"], thumb_at=5.0, background="#111827")
    bg_gradient(t, [(0, "#1F2937"), (1, "#0B1120")], angle=90)
    label(t, t.track("text", "Antetítulo"), "MESA REDONDA", 0.2, 9.8, Box(0, 40, 1920, 60), "Montserrat", 40, "#60A5FA",
          weight=900, spacing=14, anim_in=tanim("fade", duration=0.4), name="Antetítulo")
    label(t, t.track("text", "Tema"), "El futuro del trabajo", 0.4, 9.6, Box(0, 100, 1920, 110), "DM Serif Display", 80,
          "#FFFFFF", weight=400, anim_in=tanim("rise-by-word", duration=0.5, unit="word", stagger=0.1), name="Tema")
    people = [("y3-pod-07", "Andrés Gil", "Programador"), ("y3-pod-02", "Lucía Méndez", "Psicóloga"),
              ("y3-pod-04", "Daniel Rojas", "Anfitrión")]
    for i, (s, name, role) in enumerate(people):
        x = 40 + i * 627
        at = 0.3 + i * 0.2
        rounded_photo(t, s, at, 10 - at, Box(x, 240, 587, 630), pop(0, 0.4, 0.8), radius=24, label_=f"Cámara {i + 1}",
                      name=f"Cámara {i + 1}")
        label(t, t.track("text", "Nombre"), name, at + 0.3, 9.7 - at, Box(x, 890, 587, 64), "Montserrat", 46, "#FFFFFF",
              weight=800, anim_in=tanim("fade", duration=0.3), name=f"Nombre {i + 1}")
        label(t, t.track("text", "Rol"), role, at + 0.4, 9.6 - at, Box(x, 956, 587, 54), "Inter", 34, "#9CA3AF",
              weight=500, anim_in=tanim("fade", duration=0.3), name=f"Rol {i + 1}")
    for k in range(3):
        x = 40 + k * 627
        outline(t, t.track("shape", "Habla"), "#60A5FA", 8, 1.0 + k * 3.0, 3.0, Box(x - 6, 234, 599, 642),
                kind="rounded-rectangle", radius=28)
    song(t, "calm", 4, 0.45)
    return t


def pod_proximo():
    t = _pod(wide, 11, "yt-pod-proximo", "Próximo episodio", "Next episode", 8.0,
             ["próximo episodio", "pantalla final", "suscríbete", "next episode"], thumb_at=5.0, background="#0F172A")
    bg_gradient(t, [(0, "#1E293B"), (1, "#0F172A")], angle=120)
    label(t, t.track("text", "Antetítulo"), "PRÓXIMO EPISODIO", 0.3, 7.7, Box(120, 180, 900, 60), "Montserrat", 38,
          "#FBBF24", weight=800, spacing=14, align="left", anim_in=tanim("fade", duration=0.4), name="Antetítulo")
    label(t, t.track("text", "Título"), "Dinero, miedo y libertad", 0.5, 7.5, Box(120, 250, 900, 340),
          "DM Serif Display", 108, "#FFFFFF", weight=400, align="left", valign="top", line=1.02,
          anim_in=tanim("rise-by-word", duration=0.5, unit="word", stagger=0.12), name="Título")
    label(t, t.track("text", "Invitado"), "con Martín Vega", 1.0, 7.0, Box(120, 610, 900, 70), "Inter", 46, "#CBD5E1",
          weight=600, align="left", anim_in=tanim("fade", duration=0.4), name="Invitado")
    chip(t, "JUEVES · 20:00", Box(120, 710, 460, 90), "#FBBF24", "#0F172A", 1.4, size=40, spacing=3, name="Fecha")
    pill(t, t.track("shape", "Botón"), "#FFFFFF", 2.0, 6.0, Box(120, 850, 460, 100), pop(0, 0.35))
    label(t, t.track("text", "Botón"), "🔔 SUSCRÍBETE", 2.0, 6.0, Box(120, 850, 460, 100), "Montserrat", 40, "#0F172A",
          weight=900, motion=pop(0, 0.35), anim_loop=tanim("pulse", amount=4, speed=1.2), name="Llamada")
    sticker(t, "y3-pod-07", Box(1100, 170, 700, 740), at=0.2, rot=2, label_="Foto del invitado", name="Invitado",
            motion=[(0, {"dx": 900}, "out"), (0.6, {}, "linear"), (7.8, {"s": 1.02})])
    song(t, "jazz", 0, 0.55)
    return t


def pod_temas():
    t = _pod(wide, 12, "yt-pod-temas", "Temas del episodio", "Episode topics", 9.0,
             ["temas", "índice", "minutos", "capítulos", "topics"], thumb_at=5.6, background="#FAF7F2")
    bg(t, "#FAF7F2")
    t.photo(t.track("video", "Foto"), "y3-pod-09", 0, 9, Box(0, 0, 760, 1080), kb(9, 1.0, 1.08),
            label="Foto del podcast")
    label(t, t.track("text", "Antetítulo"), "EN ESTE EPISODIO", 0.3, 8.7, Box(860, 110, 960, 60), "Montserrat", 38,
          "#C2410C", weight=800, spacing=14, align="left", anim_in=tanim("fade", duration=0.4), name="Antetítulo")
    topics = [("00:00", "Presentación"), ("04:12", "Cómo empezó todo"), ("18:30", "El peor error"),
              ("31:05", "Consejos para empezar"), ("47:40", "Preguntas del público")]
    for i, (tc, topic) in enumerate(topics):
        at = 0.6 + i * 0.55
        y = 210 + i * 160
        label(t, t.track("text", "Tiempo"), tc, at, 9 - at, Box(860, y, 220, 90), "Roboto Slab", 46, "#C2410C",
              weight=700, align="left", anim_in=tanim("fade", duration=0.3), name=f"Minuto {i + 1}")
        label(t, t.track("text", "Tema"), topic, at + 0.1, 8.9 - at, Box(1080, y, 800, 90), "Inter", 50, "#1C1917",
              weight=600, align="left", anim_in=tanim("slide-right", duration=0.35), name=f"Tema {i + 1}")
        line(t, t.track("shape", "Línea"), "#E7E5E4", at, 9 - at, Box(860, y + 120, 960, 3))
    song(t, "calm", 3, 0.5)
    return t


def pod_en_vivo():
    t = _pod(wide, 13, "yt-pod-en-vivo", "Podcast en vivo con chat", "Live podcast with chat", 8.0,
             ["en vivo", "directo", "chat", "live", "stream"], thumb_at=6.4, background="#0E0E14")
    bg(t, "#0E0E14")
    rounded_photo(t, "y3-pod-07", 0, 8, Box(40, 40, 1300, 1000), kb(8, 1.0, 1.04), radius=28, label_="Cámara",
                  name="Cámara")
    pill(t, t.track("shape", "En vivo"), "#E11D48", 0.2, 7.8, Box(80, 80, 230, 70), pop(0, 0.3))
    t.solid(t.track("shape", "En vivo"), "#FFFFFF", 0.2, 7.8, centered(118, 115, 18, 18), kind="ellipse",
            opacity=blink(7.8, 1.0, 0.2))
    label(t, t.track("text", "En vivo"), "EN VIVO", 0.2, 7.8, Box(130, 80, 180, 70), "Montserrat", 32, "#FFFFFF",
          weight=900, spacing=3, name="En vivo")
    pill(t, t.track("shape", "Público"), "#000000", 0.3, 7.7, Box(330, 80, 300, 70), pop(0, 0.3), opacity=keys([(0, 0.6)]))
    label(t, t.track("text", "Público"), "1.248 viendo", 0.3, 7.7, Box(330, 80, 300, 70), "Inter", 32, "#FFFFFF",
          weight=600, name="Personas viendo")
    name_plate(t, "Diego Ramos", "Anfitrión", 80, 860, 560, "#E11D48", 0.8, 7.2)
    label(t, t.track("text", "Chat"), "CHAT EN VIVO", 0.2, 7.8, Box(1380, 50, 500, 50), "Montserrat", 30, "#9CA3AF",
          weight=800, spacing=6, align="left", name="Título del chat")
    msgs = [("@sofi_art", "¡Hola a todos! 👋", "#F472B6"), ("@marco.dev", "¿De qué hablan hoy?", "#60A5FA"),
            ("@lu_viaja", "Gran invitado 🔥", "#FBBF24"), ("@pablo_r", "Saludos desde casa", "#34D399"),
            ("@ana.m", "¡Pregunta para el final!", "#A78BFA")]
    arrivals = [1.0, 2.2, 3.4, 4.6, 5.8]
    for i, (user, text, c) in enumerate(msgs):
        at = arrivals[i]
        motion = [(0, {"dy": 60}, "out"), (0.3, {})]
        for j in range(i + 1, len(msgs)):
            rel = arrivals[j] - at
            motion += [(rel, {"dy": -150 * (j - i - 1)}, "out"), (rel + 0.3, {"dy": -150 * (j - i)})]
        motion = [(p[0], p[1], p[2]) if len(p) > 2 else (p[0], p[1], "linear") for p in motion]
        box = Box(1380, 880, 500, 130)
        rrect(t, t.track("shape", "Mensaje"), "#1F1F2B", at, 8 - at, box, 24, motion, opacity=appear(0, 0.2))
        label(t, t.track("text", "Usuario"), user, at, 8 - at, Box(1405, 890, 460, 46), "Montserrat", 28, c, weight=800,
              align="left", motion=motion, opacity=appear(0, 0.2), name=f"Usuario {i + 1}")
        label(t, t.track("text", "Mensaje"), text, at, 8 - at, Box(1405, 938, 460, 60), "Inter", 34, "#FFFFFF",
              weight=500, align="left", motion=motion, opacity=appear(0, 0.2), name=f"Mensaje {i + 1}")
    song(t, "electro", 2, 0.35)
    return t


def pod_debate():
    t = _pod(tall, 14, "yt-pod-debate", "Debate: a favor o en contra", "Debate: for or against", 10.0,
             ["debate", "a favor", "en contra", "vertical", "opiniones"], thumb_at=7.0, background="#111111")
    t.photo(t.track("video", "A favor"), "y3-podv-06", 0, 10, Box(0, 0, 1080, 900), kb(10, 1.0, 1.06),
            label="Persona a favor")
    t.photo(t.track("video", "En contra"), "y3-podv-02", 0, 10, Box(0, 1020, 1080, 900), kb(10, 1.06, 1.0),
            label="Persona en contra")
    shade_bottom(t, 420, 0.8)
    t.solid(t.track("shape", "Banda"), "#111111", 0, 10, Box(0, 880, 1080, 160))
    label(t, t.track("text", "Tema"), "¿Trabajar desde casa?", 0.2, 9.8, Box(40, 880, 1000, 160), "Montserrat", 70,
          "#FFFFFF", weight=900, anim_in=tanim("pop", duration=0.3), name="Tema")
    chip(t, "A FAVOR", Box(60, 760, 340, 96), "#16A34A", "#FFFFFF", 0.5, size=44, spacing=4, name="Postura 1")
    chip(t, "EN CONTRA", Box(60, 1064, 400, 96), "#E11D48", "#FFFFFF", 0.7, size=44, spacing=4, name="Postura 2")
    label(t, t.track("text", "Votos"), "¿Tú qué opinas?", 3.4, 6.6, Box(60, 1610, 960, 70), "Montserrat", 44, "#FFFFFF",
          weight=800, anim_in=tanim("fade", duration=0.3), name="Pregunta al público")
    bar = Box(60, 1700, 960, 80)
    t.solid(t.track("shape", "Votos"), "#E11D48", 3.6, 6.4, bar, pop(0, 0.3, 0.8), radius=40, kind="rounded-rectangle")
    grow_bar(t, "#16A34A", 3.9, bar, 0.62, length=1.2, ease="inout")
    label(t, t.track("text", "Votos"), "62%", 5.0, 5.0, Box(90, 1700, 300, 80), "Montserrat", 48, "#FFFFFF", weight=900,
          align="left", anim_in=tanim("pop", duration=0.3), name="Porcentaje a favor")
    label(t, t.track("text", "Votos"), "38%", 5.0, 5.0, Box(690, 1700, 300, 80), "Montserrat", 48, "#FFFFFF", weight=900,
          align="right", anim_in=tanim("pop", duration=0.3), name="Porcentaje en contra")
    song(t, "upbeat", 7, 0.45)
    return t


def pod_al_aire():
    t = _pod(wide, 15, "yt-pod-al-aire", "Al aire, estilo radio", "On air, radio style", 8.0,
             ["al aire", "radio", "retro", "on air", "programa"], thumb_at=5.0, background="#1A0F09")
    bg_gradient(t, [(0, "#2B1A10"), (1, "#120A05")], angle=120)
    rounded_photo(t, "h-podcast-01", 0.1, 7.9, Box(1000, 140, 820, 800), kb(7.9, 1.0, 1.06), radius=28,
                  label_="Foto del programa", name="Foto",
                  effects=[effect("color.basic", temperature=0.25, saturation=-0.1, fade=0.1)])
    outline(t, t.track("shape", "Marco"), "#D6B98C", 4, 0.1, 7.9, Box(986, 126, 848, 828), kind="rounded-rectangle",
            radius=34, alpha=0.6)
    rrect(t, t.track("shape", "Al aire"), "#3B0D0D", 0.3, 7.7, centered(470, 250, 600, 180), 24, pop(0, 0.4),
          layers=[glow("#FF4D2E", 30, 0.6), fill("#3B0D0D"), stroke(6, "#FF4D2E")])
    label(t, t.track("text", "Al aire"), "AL AIRE", 0.3, 7.7, centered(470, 256, 600, 180), "Bebas Neue", 150, "#FF4D2E",
          weight=400, spacing=12, motion=pop(0, 0.4), layers=[glow("#FF4D2E", 24, 0.9), fill("#FF6B4A")],
          anim_loop=tanim("flicker", intensity=0.3, speed=3), name="Letrero")
    label(t, t.track("text", "Programa"), "Radio de medianoche", 0.8, 7.2, Box(170, 400, 800, 260), "DM Serif Display",
          104, "#F5E6C8", weight=400, align="left", valign="top", line=1.0,
          anim_in=tanim("rise-by-word", duration=0.5, unit="word", stagger=0.15), name="Nombre del programa")
    label(t, t.track("text", "Episodio"), "Programa 112 · con Tere y Joaquín", 1.4, 6.6, Box(174, 680, 800, 60), "Inter",
          38, "#D6B98C", weight=500, align="left", anim_in=tanim("fade", duration=0.4), name="Episodio")
    wave_bars(t, 186, 880, 26, 30, 18, 140, ["#FFB347", "#FF4D2E"], 0.5, 7.5, seed=6155)
    grain(t, 0.16)
    vignette(t, 0.55)
    song(t, "jazz", 0, 0.55)
    return t


def pod_pausa():
    t = _pod(wide, 16, "yt-pod-pausa", "Ya volvemos", "Be right back", 6.0,
             ["pausa", "ya volvemos", "corte", "be right back", "descanso"], thumb_at=3.4, background="#111111")
    bg(t, "#111111")
    spin = keys([(0, 0), (6.0, 360)])
    disc = centered(560, 540, 660, 660)
    t.solid(t.track("shape", "Disco"), "#050505", 0, 6, disc, pop(0, 0.5, 0.6), kind="ellipse",
            layers=[shadow("#000000", 0, 20, 40, 0.6), fill("#050505"), no_stroke()])
    for k in range(5):
        ring(t, t.track("shape", "Surco"), "#2A2A2A", 2, 0, 6, centered(560, 540, 600 - k * 70, 600 - k * 70),
             pop(0, 0.5, 0.6))
    t.solid(t.track("shape", "Brillo"), "#FFFFFF", 0, 6, centered(560, 540, 640, 640), pop(0, 0.5, 0.6), kind="ellipse",
            layers=[{"id": "fill", "kind": "fill", "enabled": True, "opacity": 1.0,
                     "paint": {"kind": "gradient", "color": "#00ffffff",
                               "gradient": {"kind": "sweep", "angle": 0, "space": "block",
                                            "stops": [{"pos": 0, "color": "#00ffffff"}, {"pos": 0.12, "color": "#30ffffff"},
                                                      {"pos": 0.25, "color": "#00ffffff"}, {"pos": 0.5, "color": "#00ffffff"},
                                                      {"pos": 0.62, "color": "#30ffffff"}, {"pos": 0.75, "color": "#00ffffff"},
                                                      {"pos": 1, "color": "#00ffffff"}]}}}, no_stroke()])
    t.solid(t.track("shape", "Etiqueta"), "#FF6B35", 0, 6, centered(560, 540, 230, 230), pop(0, 0.5, 0.6), kind="ellipse",
            rotation=spin)
    label(t, t.track("text", "Etiqueta"), "CHARLA\nABIERTA", 0, 6, centered(560, 540, 230, 230), "Montserrat", 30,
          "#111111", weight=900, line=1.0, motion=pop(0, 0.5, 0.6), rotation=spin, name="Nombre en el disco")
    t.solid(t.track("shape", "Eje"), "#111111", 0, 6, centered(560, 540, 22, 22), pop(0, 0.5, 0.6), kind="ellipse")
    label(t, t.track("text", "Título"), "YA VOLVEMOS", 0.4, 5.6, Box(1000, 340, 880, 220), "Anton", 150, "#FFFFFF",
          weight=400, align="left", anim_in=tanim("slide-up", duration=0.4, unit="word", stagger=0.12), name="Título")
    label(t, t.track("text", "Pie"), "Una pausa corta y seguimos con Lucía", 0.8, 5.2, Box(1004, 590, 860, 130), "Inter",
          44, "#A3A3A3", weight=500, align="left", anim_in=tanim("fade", duration=0.4), name="Pie")
    t.solid(t.track("shape", "Pista"), "#FFFFFF", 0.8, 5.2, Box(1004, 760, 700, 8), radius=4, kind="rounded-rectangle",
            alpha=0.15)
    t.solid(t.track("shape", "Avance"), "#FF6B35", 0.8, 5.2, Box(1004, 760, 700, 8),
            [(0, {"sx": 0.001, "dx": -350}, "linear"), (5.2, {})], radius=4, kind="rounded-rectangle")
    song(t, "jazz", 3, 0.6)
    return t


def pod_mejores():
    t = _pod(tall, 17, "yt-pod-mejores-momentos", "Mejores momentos", "Best moments", 12.0,
             ["mejores momentos", "resumen", "vertical", "highlights", "clips"], thumb_at=5.2, background="#000000")
    shots = [("y3-podv-05", "Ella aceptó sin pensarlo"), ("y3-podv-06", "«No tenía plan B»"),
             ("y3-podv-03", "La risa que nadie esperaba")]
    v = t.track("video", "Momentos")
    prev = None
    for i, (s, _) in enumerate(shots):
        at = i * 4.0
        d = 4.0 + (0.4 if i < 2 else 0)
        clip = t.photo(v, s, at, min(d, 12 - at), t.full, kb(d, 1.0, 1.1), label=f"Momento {i + 1}")
        if prev:
            t.transition(v, prev, clip, "zoom_in", 0.4)
        prev = clip
    shade_bottom(t, 1000, 0.85)
    shade_top(t, 300, 0.5)
    _segments(t, 3, 4.0, y=60)
    pill(t, t.track("shape", "Cabecera"), "#FFE600", 0.2, 11.8, Box(60, 110, 600, 84), pop(0, 0.3))
    label(t, t.track("text", "Cabecera"), "LO MEJOR DEL EP. 42", 0.2, 11.8, Box(60, 110, 600, 84), "Montserrat", 38,
          "#111111", weight=900, motion=pop(0, 0.3), name="Cabecera")
    for i, (_, q) in enumerate(shots):
        at = i * 4.0 + 0.2
        label(t, t.track("text", "Momento"), f"MOMENTO #{i + 1}", at, 3.7, Box(60, 1120, 960, 130), "Anton", 110,
              "#FFE600", weight=400, align="left", anim_in=tanim("stamp", duration=0.3),
              anim_out=tanim("fade", duration=0.2), editable=False)
        label(t, t.track("text", "Frase"), q, at + 0.3, 3.4, Box(60, 1260, 960, 330), "Montserrat", 74, "#FFFFFF",
              weight=800, align="left", valign="top", line=1.1,
              anim_in=tanim("rise-by-word", duration=0.35, unit="word", stagger=0.08), anim_out=tanim("fade", duration=0.2),
              name=f"Frase {i + 1}")
    song(t, "upbeat", 1, 0.5)
    return t


TEMPLATES = [
    mini_flecha_circulo, mini_diagonal, mini_cara_a_cara, mini_numero_uno, mini_precio_tachado, mini_celular,
    mini_tres_niveles, mini_lupa, mini_alerta, mini_tier_list, mini_bien_mal, mini_grafica, mini_comic, mini_sticker,
    mini_caja_misterio, mini_cuatro_caras, mini_cronometro, mini_revelacion,
    tec_unboxing, tec_ficha, tec_comparacion, tec_pros_contras, tec_puntaje, tec_precio, tec_vale_la_pena,
    tec_unboxing_vertical, tec_veredicto, tec_setup, tec_tres_cosas, tec_benchmark, tec_bateria, tec_primeras,
    tec_camara, tec_top3, tec_capitulos, tec_comparacion_vertical,
    pod_dos_camaras, pod_cortes, pod_audiograma, pod_titulo, pod_invitado, pod_cita, pod_clip_vertical,
    pod_clip_subtitulos, pod_pregunta, pod_apertura, pod_panel_tres, pod_proximo, pod_temas, pod_en_vivo, pod_debate,
    pod_al_aire, pod_pausa, pod_mejores,
]
