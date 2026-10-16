"""Trend batch 3 (2026-10-15): see BRIEF.md, section «Las 100 de tendencia».

Negocios: 20 reels for small Latin American businesses (menus, salons, gyms, offers, hiring, events...).
Every business detail (name, phone, address, prices) is an editable text with a clear label.
"""

from __future__ import annotations

import random

from scene import (FULL, Box, Template, anim, beat, centered, effect, fill, glow, gradient, keys,
                   no_stroke, shadow, stroke, tanim, text_style)


# --- Helpers ------------------------------------------------------------------------------------


def pop(at: float = 0.0, length: float = 0.45) -> list:
    # Not quite zero: a photo's crop is computed from its first box, which must keep its aspect.
    return [(at, {"s": 0.02}, "back"), (at + length, {})]


def slide_in(dx: float = 0.0, dy: float = 0.0, length: float = 0.5) -> list:
    return [(0, {"dx": dx, "dy": dy}, "out"), (length, {})]


def pill(t: Template, track, colour: str, t0: float, dur: float, box: Box, motion=None, layers=None, **extra):
    return t.solid(track, colour, t0, dur, box, motion, radius=box.h / 2, kind="rounded-rectangle", layers=layers,
                   **extra)


def card(t: Template, track, colour: str, t0: float, dur: float, box: Box, motion=None, radius: float = 36,
         shade: str = "#000000", strength: float = 0.25, **extra):
    return t.solid(track, colour, t0, dur, box, motion, radius=radius, kind="rounded-rectangle",
                   layers=[shadow(shade, 0, 14, 36, strength), fill(colour), no_stroke()], **extra)


def round_photo(t: Template, sample: str, t0: float, dur: float, cx: float, cy: float, d: float, motion=None,
                ring: str | None = None, ring_w: float = 14, label: str | None = None, reuse: str | None = None,
                name: str = "Foto") -> dict:
    if ring:
        t.solid(t.track("shape", "Aro"), ring, t0, dur, centered(cx, cy, d + ring_w * 2, d + ring_w * 2), motion,
                kind="ellipse", layers=[shadow("#000000", 0, 10, 30, 0.25), fill(ring), no_stroke()])
    track = t.track("video", name)
    clip = t.photo(track, sample, t0, dur, centered(cx, cy, d, d), motion, label=label, reuse=reuse)
    t.mask(track, clip, "ellipse")
    return clip


def star_row(t: Template, t0: float, dur: float, cx: float, cy: float, size: float, gap: float, colour: str,
             n: int = 5, stagger: float = 0.12) -> None:
    for i in range(n):
        x = cx + (i - (n - 1) / 2) * (size + gap)
        start = t0 + i * stagger
        t.solid(t.track("shape", f"Estrella {i + 1}"), colour, start, dur - i * stagger, centered(x, cy, size, size),
                pop(0, 0.35), kind="star", layers=[glow(colour, 12, 0.5), fill(colour), no_stroke()])


def confetti(t: Template, t0: float, colours: list[str], lanes: int = 3, seed: int = 1, top: float = -60) -> None:
    rng = random.Random(seed)
    for lane in range(lanes):
        track = t.track("shape", f"Confeti {lane + 1}")
        start = t0 + lane * 0.15
        while start < t.duration - 0.6:
            dur = min(rng.uniform(2.4, 3.6), t.duration - start)
            size = rng.uniform(22, 44)
            x = rng.uniform(40, 1040)
            t.solid(track, rng.choice(colours), start, dur, centered(x, top, size, size * rng.choice([1.0, 0.5])),
                    [(0, {}, "linear"), (dur, {"dy": 2100, "dx": rng.uniform(-140, 140)})],
                    kind=rng.choice(["rectangle", "ellipse", "star"]),
                    rotation=keys([(0, 0), (dur, rng.uniform(-400, 400))]))
            start += dur


def spikes(times: list[float], peak: float, fall: float) -> dict:
    """A peak at each time that drops to 0 and holds there (BRIEF: spike effects need 'hold')."""
    pts: list[tuple] = []
    # Off until the first peak: before its first key a channel holds that key's value.
    if times and times[0] > 0:
        pts.append((0.0, 0.0, "hold"))
    for at in times:
        pts += [(at, peak, "out"), (at + fall, 0.0, "hold")]
    return keys(pts)


def T(t: Template, name: str = "Texto"):
    return t.track("text", name)


def S(t: Template, name: str = "Forma"):
    return t.track("shape", name)


# --- 1. Menú del día ----------------------------------------------------------------------------


def menu_del_dia() -> Template:
    t = Template("menu-del-dia-pizarra", "Menú del día en pizarra", "Daily menu chalkboard", "business", 10.0,
                 order=1200, tags=["menú", "restaurante", "almuerzo", "comida", "precio"], thumb_at=6.2,
                 background="#162720")
    t.solid(S(t, "Pizarra"), "#1E3B2F", layers=[gradient([(0, "#23392F"), (1, "#121F19")], angle=90), no_stroke()])
    ring = S(t, "Aro")
    t.solid(ring, "#F2C14E", 0.5, 9.5, centered(540, 770, 640, 640), pop(), kind="ellipse",
            layers=[stroke(6, "#F2C14E"), {"id": "fill", "kind": "fill", "enabled": False,
                                           "paint": {"kind": "solid", "color": "#00000000"}}])
    dishes = t.track("video", "Platos")
    clips = []
    for i, (sample, label, a, b) in enumerate([("food-03", "Entrada", 0.5, 4.0), ("restaurant-01", "Segundo", 4.0, 7.0),
                                               ("food-01", "Plato del día", 7.0, 10.0)]):
        motion = pop() if i == 0 else [(0, {"s": 1.0}, "linear"), (b - a, {"s": 1.06})]
        clips.append(t.photo(dishes, sample, a, b - a, centered(540, 770, 600, 600), motion, label=label))
    for a, b in zip(clips, clips[1:]):
        t.transition(dishes, a, b, "crossfade", 0.5)
    for clip in clips:
        t.mask(dishes, clip, "ellipse")
    chalk = lambda size, colour="#F5F1E6": text_style("Amatic SC", size, [fill(colour, 0.95)], weight=700)  # noqa: E731
    t.text(T(t, "Título"), "Menú del día", 0.1, 9.9, Box(40, 80, 1000, 230),
           {**chalk(200), "animation": {"in": tanim("typewriter", duration=0.8, unit="character")}}, label="Título")
    t.text(T(t, "Negocio"), "Restaurante Doña Rosa", 0.6, 9.4, Box(40, 300, 1000, 90),
           text_style("Kalam", 56, [fill("#F2C14E")], weight=700, anim_in=tanim("fade", duration=0.5)),
           label="Nombre del negocio")
    items = [("Entrada", "Papa a la huancaína"), ("Segundo", "Lomo saltado"), ("Bebida", "Chicha morada")]
    for i, (kind, dish) in enumerate(items):
        y = 1110 + i * 160
        start = 1.2 + i * 0.4
        t.solid(S(t, "Línea"), "#F5F1E6", start, 10 - start, Box(120, y + 150, 840, 3),
                [(0, {"sx": 0.0, "dx": -420}, "out"), (0.6, {})], alpha=0.3)
        t.text(T(t, kind), kind, start, 10 - start, Box(120, y, 840, 60),
               text_style("Kalam", 44, [fill("#F2C14E")], weight=400, align="left",
                          anim_in=tanim("fade", duration=0.4)), label=f"{kind} (tipo)")
        t.text(T(t, dish), dish, start + 0.15, 9.85 - start, Box(120, y + 45, 840, 110),
               {**chalk(96), "align": "left", "animation": {"in": tanim("wipe", duration=0.6, angle=0)}},
               label=kind)
    t.solid(S(t, "Precio"), "#F2C14E", 2.6, 7.4, centered(860, 1735, 260, 260), pop(0, 0.5), kind="ellipse",
            layers=[shadow("#000000", 0, 10, 24, 0.4), fill("#F2C14E"), no_stroke()], rotation=keys([(0, -8)]))
    t.text(T(t, "Precio"), "S/ 15.00", 2.7, 7.3, centered(860, 1735, 260, 260),
           text_style("Amatic SC", 100, [fill("#162720")], weight=700, line=0.9,
                      anim_in=tanim("stamp", duration=0.35)), label="Precio", rotation=keys([(0, -8)]))
    t.text(T(t, "Teléfono"), "Pide al 999 999 999", 3.0, 7.0, Box(60, 1690, 620, 90),
           text_style("Kalam", 52, [fill("#F5F1E6")], weight=700, align="left",
                      anim_in=tanim("slide-up", duration=0.4)), label="Teléfono")
    t.adjust([effect("stylize.film_grain", amount=0.2, grainSize=2.0), effect("stylize.vignette", amount=0.5)],
             name="Tiza")
    t.song("cumbish", 0.0, 0.85)
    return t


# --- 2. Cafetería: nuevo en la carta ------------------------------------------------------------


def cafe_nuevo_carta() -> Template:
    t = Template("cafe-nuevo-en-la-carta", "Nuevo en la carta", "New on the menu", "product", 8.0,
                 order=1201, tags=["cafetería", "café", "nuevo", "carta", "bebida"], thumb_at=2.4,
                 background="#F3E6D3")
    t.solid(S(t, "Fondo"), "#F3E6D3", layers=[gradient([(0, "#F7EDE0"), (1, "#EAD7BF")], angle=90), no_stroke()])
    enter = [(0, {"dy": 1300}, "out"), (0.7, {}, "linear"), (7.7, {"s": 1.03})]
    card(t, S(t, "Tarjeta"), "#FFFFFF", 0.2, 7.8, centered(540, 830, 860, 1080), enter, radius=48,
         shade="#4B2E1F", strength=0.3)
    photos = t.track("video", "Fotos")
    box = centered(540, 830, 820, 1040)
    a = t.photo(photos, "coffee-03", 0.2, 3.0, box, enter[:2] + [(3.0, {"s": 1.03})], label="Bebida")
    b = t.photo(photos, "coffee-01", 3.2, 2.4, box, [(0, {"s": 1.08}, "linear"), (2.4, {"s": 1.0})], label="Detalle")
    c = t.photo(photos, "coffee-04", 5.6, 2.4, box, [(0, {"s": 1.0}, "linear"), (2.4, {"s": 1.06})], label="Barista")
    t.transition(photos, a, b, "wipe_up", 0.5)
    t.transition(photos, b, c, "wipe_up", 0.5)
    pill(t, S(t, "Etiqueta"), "#4B2E1F", 0.6, 7.4, centered(540, 210, 640, 100), pop())
    t.text(T(t, "Etiqueta"), "NUEVO EN LA CARTA", 0.7, 7.3, centered(540, 210, 640, 100),
           text_style("Quicksand", 44, [fill("#F3E6D3")], weight=700, spacing=6), label="Etiqueta")
    t.solid(S(t, "Precio"), "#C8763B", 1.4, 6.6, centered(880, 1290, 240, 240), pop(0, 0.5), kind="ellipse",
            layers=[shadow("#4B2E1F", 0, 10, 24, 0.35), fill("#C8763B"), no_stroke()])
    t.text(T(t, "Precio"), "S/ 12.90", 1.5, 6.5, centered(880, 1290, 240, 240),
           text_style("Prata", 60, [fill("#FFFFFF")], weight=400, anim_in=tanim("pop", duration=0.4)), label="Precio")
    t.text(T(t, "Nombre"), "Latte de canela", 1.0, 7.0, Box(60, 1400, 960, 150),
           text_style("Prata", 112, [fill("#4B2E1F")], weight=400,
                      anim_in=tanim("rise", duration=0.6, unit="character", stagger=0.03)), label="Producto")
    t.text(T(t, "Descripción"), "Espresso, leche cremosa y un toque de canela", 1.6, 6.4, Box(130, 1550, 820, 140),
           text_style("Quicksand", 46, [fill("#7A5A44")], weight=500, line=1.2,
                      anim_in=tanim("fade", duration=0.6)), label="Descripción")
    t.text(T(t, "Negocio"), "Café La Esquina", 2.0, 6.0, Box(60, 1760, 960, 70),
           text_style("Quicksand", 40, [fill("#4B2E1F")], weight=700, spacing=8, case="upper",
                      anim_in=tanim("fade", duration=0.6)), label="Nombre del negocio")
    t.adjust([effect("light_leak", intensity=0.22, hue=0.08, speed=0.5, softness=0.7)], name="Luz cálida")
    t.song("martini-sunset", 0.0, 0.85)
    return t


# --- 3. Salón de belleza ------------------------------------------------------------------------


def salon_belleza() -> Template:
    t = Template("salon-de-belleza-servicios", "Salón de belleza", "Beauty salon", "business", 12.0,
                 order=1202, tags=["salón", "belleza", "peluquería", "servicios", "citas"], thumb_at=4.2)
    t.solid(S(t, "Fondo"), "#F6D6D0", layers=[gradient([(0, "#FBEAE6"), (1, "#EDC0B8")], angle=90), no_stroke()])
    oval = centered(540, 820, 680, 940)
    t.solid(S(t, "Espejo"), "#C9A27E", 0.3, 11.7, centered(540, 820, 720, 980), pop(0, 0.6), kind="ellipse",
            layers=[glow("#FFFFFF", 30, 0.6), stroke(4, "#C9A27E"), fill("#FFFFFF")])
    photos = t.track("video", "Fotos")
    clips = []
    for i, (sample, label) in enumerate([("salon-01", "Servicio 1"), ("salon-04", "Servicio 2"),
                                         ("salon-02", "Servicio 3"), ("makeup-01", "Servicio 4")]):
        start = 0.3 + i * 2.9
        dur = 2.9 if i < 3 else 12 - start
        motion = pop(0, 0.6) + [(dur, {"s": 1.05})] if i == 0 else [(0, {"s": 1.0}, "linear"), (dur, {"s": 1.06})]
        clips.append(t.photo(photos, sample, start, dur, oval, motion, label=label))
    for a, b in zip(clips, clips[1:]):
        t.transition(photos, a, b, "blur_dissolve", 0.7)
    for clip in clips:
        t.mask(photos, clip, "ellipse")
    t.text(T(t, "Nombre"), "Salón Valentina", 0.4, 11.6, Box(40, 90, 1000, 220),
           text_style("Parisienne", 118, [shadow("#FFFFFF", 0, 0, 14, 0.9), fill("#8C3B4A")], weight=400,
                      anim_in=tanim("blur-in", duration=1.0, blur=18)), label="Nombre del negocio")
    services = [("Corte y cepillado", "S/ 35"), ("Tinte completo", "S/ 90"), ("Peinado de fiesta", "S/ 50")]
    for i, (name, price) in enumerate(services):
        y = 1350 + i * 105
        start = 1.0 + i * 0.35
        slide = [(0, {"dx": -120}, "out"), (0.5, {})]
        t.text(T(t, f"Servicio {i + 1}"), name, start, 12 - start, Box(110, y, 600, 90),
               text_style("Josefin Sans", 52, [fill("#5A2330")], weight=600, align="left",
                          anim_in=tanim("fade", duration=0.5)), slide, label=f"Servicio {i + 1}")
        t.text(T(t, f"Precio {i + 1}"), price, start + 0.1, 11.9 - start, Box(700, y, 270, 90),
               text_style("Josefin Sans", 52, [fill("#8C3B4A")], weight=700, align="right",
                          anim_in=tanim("fade", duration=0.5)), label=f"Precio {i + 1}")
        t.solid(S(t, "Línea"), "#8C3B4A", start, 12 - start, Box(110, y + 92, 860, 2),
                [(0, {"sx": 0.0, "dx": -430}, "out"), (0.6, {})], alpha=0.25)
    pill(t, S(t, "Botón"), "#8C3B4A", 2.4, 9.6, centered(540, 1790, 860, 104), pop())
    t.text(T(t, "Reservas"), "Reserva tu cita · 999 999 999", 2.5, 9.5, centered(540, 1790, 860, 104),
           text_style("Josefin Sans", 44, [fill("#FBEAE6")], weight=700), label="Reservas")
    t.adjust([effect("bling_sparkle", intensity=0.4, density=0.3, threshold=0.8, colorize=0.3)], name="Brillos")
    t.song("and-just-like-that", 0.0, 0.85)
    return t


# --- 4. Uñas ------------------------------------------------------------------------------------


def unas_manicure() -> Template:
    t = Template("unas-nail-art", "Uñas y nail art", "Nails and nail art", "business", 8.0,
                 order=1203, tags=["uñas", "manicure", "nail art", "belleza", "acrílicas"], thumb_at=3.6)
    t.solid(S(t, "Fondo"), "#EBDDFF", layers=[gradient([(0, "#F6EEFF"), (1, "#E2CCFF")], angle=120), no_stroke()])
    rng = random.Random(14)
    for k in range(3):
        hearts = S(t, f"Corazones {k + 1}")
        start = k * 0.6
        while start < 7.4:
            size = rng.uniform(36, 70)
            dur = min(rng.uniform(3.0, 4.2), 8 - start)
            t.solid(hearts, "#FF8FC7", start, dur, centered(rng.uniform(60, 1020), 1990, size, size),
                    [(0, {}, "linear"), (dur, {"dy": -2150, "dx": rng.uniform(-80, 80)})], kind="heart", alpha=0.5)
            start += dur
    bob = lambda a, amp: [(0, {"s": 0.02}, "back"), (0.5, {}, "smooth"), (2.0, {"dy": -amp}, "smooth"),  # noqa: E731
                          (3.5, {}, "smooth"), (5.0, {"dy": -amp}, "smooth"), (8.0 - a, {})]
    round_photo(t, "nails-02", 0.4, 7.6, 380, 830, 560, bob(0.4, 24), ring="#FF8FC7", label="Uñas 1", name="Foto 1")
    round_photo(t, "nails-03", 1.0, 7.0, 770, 1230, 420, bob(1.0, 18), ring="#FFFFFF", label="Uñas 2", name="Foto 2")
    t.text(T(t, "Título"), "Uñas que enamoran", 0.1, 7.9, Box(40, 110, 1000, 330),
           text_style("Sniglet", 124, [shadow("#5B2A86", 0, 8, 0, 0.35), fill("#D63384")], weight=800, line=0.95,
                      anim_in=tanim("bounce", duration=0.6, unit="character", stagger=0.04)), label="Título")
    t.solid(S(t, "Sello"), "#D63384", 1.6, 6.4, centered(300, 1330, 300, 300), pop(0, 0.5), kind="burst",
            layers=[shadow("#5B2A86", 0, 8, 18, 0.35), fill("#D63384"), no_stroke()],
            rotation=keys([(0, -40, "out"), (0.6, -10)]))
    t.text(T(t, "Precio"), "desde\nS/ 45", 1.7, 6.3, centered(300, 1330, 300, 300),
           text_style("Baloo 2", 66, [fill("#FFFFFF")], weight=800, line=0.9, anim_in=tanim("pop", duration=0.4)),
           label="Precio", rotation=keys([(0, -10)]))
    t.text(T(t, "Servicios"), "Acrílicas · Gel · Nail art", 2.0, 6.0, Box(40, 1560, 1000, 90),
           text_style("Baloo 2", 56, [fill("#5B2A86")], weight=700, anim_in=tanim("rise", duration=0.5)),
           label="Servicios")
    pill(t, S(t, "Botón"), "#5B2A86", 2.4, 5.6, centered(540, 1730, 640, 116),
         [(0, {"s": 0.0}, "back"), (0.4, {}, "smooth"), (0.9, {"s": 1.05}, "smooth"), (1.4, {})])
    t.text(T(t, "Llamada"), "Agenda por DM", 2.5, 5.5, centered(540, 1730, 640, 116),
           text_style("Baloo 2", 56, [fill("#FFFFFF")], weight=800, anim_loop=tanim("pulse", amount=4, speed=1.2)),
           label="Llamada")
    t.song("funshine", 0.0, 0.85)
    return t


# --- 5. Barbería antes y después ----------------------------------------------------------------


def barberia_antes_despues() -> Template:
    t = Template("barberia-antes-despues", "Barbería: antes y después", "Barbershop before and after", "business",
                 8.0, order=1204, tags=["barbería", "corte", "barba", "antes y después", "fade"], thumb_at=4.6,
                 background="#111111")
    before = t.track("video", "Antes")
    t.photo(before, "barber-02", 0, 3.6, FULL, [(0, {"s": 1.0}, "linear"), (3.6, {"s": 1.08})], label="Antes",
            effects=[effect("color.basic", saturation=-1.0, contrast=0.15, exposure=-0.1)])
    after = t.track("video", "Después")
    top = t.photo(after, "barber-01", 2.4, 3.2, FULL, [(0, {"s": 1.08}, "linear"), (3.2, {"s": 1.0})],
                  label="Después")
    t.photo(after, "barber-03", 5.6, 2.4, FULL, [(0, {"s": 1.12}, "snap"), (0.25, {"s": 1.02}, "linear"),
                                                 (2.4, {"s": 1.0})], label="Después 2")
    # A gold bar sweeps down at 2.4-3.4 s: the "after" shows above it.
    sweep = [(0, 0.0, "inout"), (1.0, 1.0)]
    t.mask(after, top, "rectangle", h=0.0, y=0.0,
           keyframes={"h": keys(sweep), "y": keys([(p[0], p[1] / 2, *p[2:]) for p in sweep])})
    t.solid(S(t, "Barra"), "#C8A24A", 2.4, 1.1, Box(0, -6, 1080, 12),
            layers=[glow("#C8A24A", 30, 0.9), fill("#E6C46A"), no_stroke()],
            y=keys([(0, -6, "inout"), (1.0, 1914), (1.1, 1914)]))
    shade = S(t, "Sombra")
    t.solid(shade, "#000000", 0, 8.0, Box(0, 1300, 1080, 620),
            layers=[gradient([(0, "#000000", 0.0), (1, "#000000", 0.9)], angle=90), no_stroke()])
    tag = lambda colour, ink: text_style("Staatliches", 80, [fill(ink)], weight=400, spacing=6,  # noqa: E731
                                         box=(colour, 0.92), box_pad=18, box_radius=8,
                                         anim_in=tanim("slide-right", duration=0.35))
    t.text(T(t, "Antes"), "ANTES", 0.2, 2.2, Box(60, 120, 400, 110), {**tag("#111111", "#FFFFFF"), "align": "left"},
           label="Antes")
    t.text(T(t, "Después"), "DESPUÉS", 3.4, 4.6, Box(60, 120, 500, 110), {**tag("#C8A24A", "#111111"), "align": "left"},
           label="Después")
    t.text(T(t, "Nombre"), "Barbería El Clásico", 3.6, 4.4, Box(40, 1520, 1000, 160),
           text_style("Staatliches", 124, [shadow("#000000", 0, 6, 16, 0.6), fill("#E6C46A")], weight=400, spacing=2,
                      anim_in=tanim("wipe", duration=0.5, angle=0)), label="Nombre del negocio")
    t.text(T(t, "Precio"), "Corte + barba  S/ 30", 4.0, 4.0, Box(40, 1680, 1000, 80),
           text_style("Barlow", 56, [fill("#FFFFFF")], weight=600, spacing=2, anim_in=tanim("fade", duration=0.4)),
           label="Precio")
    t.text(T(t, "Dirección"), "Jr. Junín 245 · 999 999 999", 4.4, 3.6, Box(40, 1770, 1000, 70),
           text_style("Barlow", 42, [fill("#BBBBBB")], weight=500, anim_in=tanim("fade", duration=0.4)),
           label="Dirección y teléfono")
    t.adjust([effect("beat_shake", animated={"amount": spikes([3.4, 5.6], 0.8, 0.35)}, rotation=0.3),
              effect("stylize.vignette", amount=0.6)], name="Golpe")
    t.song("bebop-for-joey", 0.0, 0.85)
    return t


# --- 6. Gimnasio --------------------------------------------------------------------------------


def gimnasio_promo() -> Template:
    t = Template("gimnasio-matricula-gratis", "Gimnasio: promo del mes", "Gym: promo of the month", "business", 8.0,
                 order=1205, tags=["gimnasio", "gym", "membresía", "promoción", "fitness"], thumb_at=6.3,
                 background="#000000")
    photos = t.track("video", "Fotos")
    samples = ["gym-01", "gym-02", "gym-04", "gym-06"]
    for i in range(8):
        t.photo(photos, samples[i % 4], i * beat(1), beat(1), FULL, [(0, {"s": 1.18}, "snap"), (0.18, {"s": 1.04})],
                label=f"Foto {i % 4 + 1}", reuse=None if i < 4 else f"p{i % 4 + 1}",
                effects=[effect("color.basic", contrast=0.25, saturation=-0.2)])
    t.photo(photos, "gym-02", 4.0, 4.0, FULL, [(0, {"s": 1.15}, "snap"), (0.2, {"s": 1.05}, "linear"), (4.0, {"s": 1.0})],
            reuse="p2", effects=[effect("duotone", strength=0.85, shadowColor="#0a0a0a", highlightColor="#c6ff00",
                                        contrast=0.6)])
    words = T(t, "Gancho")
    for i, (word, a, b) in enumerate([("¿LISTO?", 0.0, 1.0), ("ENTRENA", 1.0, 2.0), ("CON NOSOTROS", 2.0, 4.0)]):
        size = 230 if len(word) < 9 else 190
        t.text(words, word, a, b - a, Box(30, 640, 1020, 640),
               text_style("Teko", size, [shadow("#000000", 0, 10, 0, 0.8), fill("#C6FF00" if i % 2 else "#FFFFFF")],
                          weight=700, line=0.85, keyframes={"pixelSize": keys([(0, size * 2.2, "snap"), (0.15, size)])}),
               label=f"Gancho {i + 1}")
    band = S(t, "Banda")
    t.solid(band, "#C6FF00", 4.0, 4.0, Box(-100, 1080, 1280, 150), [(0, {"dx": -1300}, "out"), (0.4, {})],
            rotation=keys([(0, -6)]))
    t.text(T(t, "Oferta"), "MATRÍCULA GRATIS", 4.1, 3.9, Box(-100, 1080, 1280, 150),
           text_style("Teko", 120, [fill("#000000")], weight=700, spacing=4), [(0, {"dx": -1300}, "out"), (0.4, {})],
           label="Oferta", rotation=keys([(0, -6)]))
    t.text(T(t, "Precio"), "S/ 79 al mes", 4.4, 3.6, Box(40, 380, 1000, 330),
           text_style("Teko", 180, [shadow("#000000", 0, 10, 24, 0.7), fill("#FFFFFF")], weight=700, line=0.9,
                      accent={"rule": "firstWord", "colorEnabled": True, "color": "#ffc6ff00"},
                      anim_in=tanim("stamp", duration=0.35)), label="Precio")
    t.text(T(t, "Vigencia"), "Solo este mes", 4.8, 3.2, Box(40, 260, 1000, 100),
           text_style("Barlow Condensed", 64, [fill("#C6FF00")], weight=700, spacing=10, case="upper",
                      anim_in=tanim("fade", duration=0.4)), label="Vigencia")
    t.text(T(t, "Negocio"), "Gym Power · Av. Perú 456", 5.0, 3.0, Box(40, 1660, 1000, 90),
           text_style("Barlow Condensed", 60, [shadow("#000000", 0, 4, 12, 0.7), fill("#FFFFFF")], weight=700,
                      anim_in=tanim("slide-up", duration=0.4)), label="Nombre y dirección")
    beats = [beat(k) for k in range(8)] + [4.0]
    t.adjust([effect("rgb_split", animated={"amount": spikes(beats, 26.0, 0.16)}, angle=0),
              effect("beat_shake", animated={"amount": spikes([0.0, 1.0, 2.0, 4.0], 0.7, 0.3)}, rotation=0.4),
              effect("stylize.vignette", amount=0.6)], name="Golpe")
    t.song("city-run", 0.0, 0.9)
    return t


# --- 7. Lanzamiento -----------------------------------------------------------------------------


def lanzamiento_producto() -> Template:
    t = Template("lanzamiento-ya-disponible", "Lanzamiento: ya disponible", "Launch: available now", "product", 10.0,
                 order=1206, tags=["lanzamiento", "producto", "nuevo", "tienda online", "estreno"], thumb_at=8.6,
                 background="#0B0D17")
    t.solid(S(t, "Fondo"), "#0B0D17", layers=[gradient([(0, "#151A3A"), (1, "#05060C")], angle=90), no_stroke()])
    t.text(T(t, "Intriga"), "Algo nuevo llega…", 0.2, 2.2, Box(60, 760, 960, 300),
           text_style("Exo 2", 96, [glow("#3A5BFF", 30, 0.8), fill("#FFFFFF")], weight=700,
                      anim_in=tanim("typewriter", duration=1.2, unit="character"),
                      anim_out=tanim("fade-scale", duration=0.3)), label="Intriga")
    t.solid(S(t, "Halo"), "#3A5BFF", 2.5, 7.5, centered(540, 860, 900, 900), pop(0, 0.7), kind="ellipse",
            layers=[glow("#3A5BFF", 120, 0.9), fill("#3A5BFF", 0.35), no_stroke()])
    hero = [(0, {"s": 0.6}, "back"), (0.7, {}, "linear"), (3.0, {"s": 1.04})]
    spin = keys([(0, -18, "out"), (0.7, -3)])
    end = [(0, {"s": 0.8}, "back"), (0.4, {})]
    cards = S(t, "Tarjeta")
    card(t, cards, "#FFFFFF", 2.5, 3.0, centered(540, 860, 820, 1000), hero, radius=44, rotation=spin, strength=0.5)
    card(t, cards, "#FFFFFF", 7.0, 3.0, centered(540, 860, 820, 1000), end, radius=44, rotation=keys([(0, 3)]),
         strength=0.5)
    photos = t.track("video", "Fotos")
    box = centered(540, 860, 780, 960)
    t.photo(photos, "product-04", 2.5, 3.0, box, hero, label="Producto", rotation=spin)
    t.photo(photos, "shopping-03", 5.5, 1.5, FULL, [(0, {"s": 1.15}, "snap"), (0.25, {"s": 1.03}, "linear"),
                                                     (1.5, {"s": 1.0})], label="En uso")
    t.photo(photos, "product-04", 7.0, 3.0, box, end, reuse="p1", rotation=keys([(0, 3)]))
    t.solid(S(t, "Destello"), "#FFFFFF", 2.5, 0.35, FULL, opacity=keys([(0, 1.0, "out"), (0.35, 0.0)]))
    t.text(T(t, "Ya"), "YA DISPONIBLE", 2.7, 7.3, Box(40, 140, 1000, 160),
           text_style("Exo 2", 112, [glow("#3A5BFF", 24, 0.8), gradient([(0, "#FFFFFF"), (1, "#8FA5FF")], angle=90)],
                      weight=900, spacing=4, anim_in=tanim("glitch-in", duration=0.4)), label="Anuncio")
    t.text(T(t, "Producto"), "Zapatilla Nube", 3.2, 6.8, Box(40, 1420, 1000, 130),
           text_style("Exo 2", 96, [fill("#FFFFFF")], weight=700, anim_in=tanim("rise", duration=0.5)),
           label="Producto")
    pill(t, S(t, "Precio"), "#3A5BFF", 7.2, 2.8, centered(540, 1630, 520, 130), pop(),
         layers=[glow("#3A5BFF", 30, 0.8), fill("#3A5BFF"), no_stroke()])
    t.text(T(t, "Precio"), "S/ 189.90", 7.3, 2.7, centered(540, 1630, 520, 130),
           text_style("Exo 2", 76, [fill("#FFFFFF")], weight=800), label="Precio")
    t.text(T(t, "Dónde"), "Solo en nuestra tienda online", 7.6, 2.4, Box(40, 1730, 1000, 80),
           text_style("Inter", 44, [fill("#AAB4E8")], weight=500, anim_in=tanim("fade", duration=0.5)),
           label="Dónde comprar")
    t.adjust([effect("bloom_glow", threshold=0.7, intensity=0.5, blurRadius=12)], 2.5, 7.5, name="Brillo")
    t.song("new-hero-in-town", 0.0, 0.9)
    return t


# --- 8. Testimonio ------------------------------------------------------------------------------


def testimonio_cliente() -> Template:
    t = Template("testimonio-cliente-estrellas", "Testimonio de cliente", "Customer testimonial", "business", 8.0,
                 order=1207, tags=["testimonio", "cliente", "opinión", "estrellas", "confianza"], thumb_at=5.6)
    t.photo(t.track("video", "Local"), "cafe-02", 0, 8.0, FULL, [(0, {"s": 1.12}, "linear"), (8.0, {"s": 1.0})],
            label="Tu negocio", effects=[effect("builtin.effects.gaussian_blur", u_blurRadius=14)])
    t.solid(S(t, "Velo"), "#1B2A41", alpha=0.55)
    enter = slide_in(dy=1400, length=0.7)
    card(t, S(t, "Tarjeta"), "#FFFFFF", 0.3, 7.7, Box(80, 470, 920, 1180), enter, radius=44, strength=0.4)
    round_photo(t, "portrait-02", 0.9, 7.1, 540, 480, 300, pop(), ring="#FFB800", label="Foto del cliente",
                name="Cliente")
    star_row(t, 1.3, 6.7, 540, 790, 78, 18, "#FFB800")
    t.text(T(t, "Comillas"), "“", 1.0, 7.0, Box(120, 830, 200, 260),
           text_style("Libre Baskerville", 220, [fill("#FFB800")], weight=400, align="left", valign="top",
                      anim_in=tanim("fade", duration=0.4)), editable=False)
    t.text(T(t, "Opinión"), "Me atendieron súper rápido y el café es el mejor de la zona. ¡Vuelvo seguro!", 2.0, 6.0,
           Box(140, 950, 800, 460),
           text_style("Libre Baskerville", 56, [fill("#1B2A41")], weight=400, italic=True, align="left", line=1.25,
                      anim_in=tanim("rise-by-word", duration=0.4, unit="word", stagger=0.07)), label="Opinión")
    t.text(T(t, "Cliente"), "— Carla M.", 3.6, 4.4, Box(140, 1440, 800, 70),
           text_style("DM Sans", 52, [fill("#1B2A41")], weight=700, align="left", anim_in=tanim("fade", duration=0.4)),
           label="Nombre del cliente")
    t.text(T(t, "Detalle"), "Clienta desde 2024", 3.8, 4.2, Box(140, 1515, 800, 60),
           text_style("DM Sans", 40, [fill("#6B7A90")], weight=500, align="left",
                      anim_in=tanim("fade", duration=0.4)), label="Detalle del cliente")
    t.text(T(t, "Mensaje"), "Gracias por confiar en nosotros", 4.2, 3.8, Box(40, 1720, 1000, 90),
           text_style("DM Sans", 50, [shadow("#000000", 0, 3, 10, 0.5), fill("#FFFFFF")], weight=700,
                      anim_in=tanim("slide-up", duration=0.4)), label="Mensaje")
    t.song("happy-whistling-ukulele", 0.0, 0.8)
    return t


# --- 9. Estamos contratando ---------------------------------------------------------------------


def estamos_contratando() -> Template:
    t = Template("estamos-contratando", "¡Estamos contratando!", "We're hiring!", "business", 10.0,
                 order=1208, tags=["empleo", "trabajo", "contratando", "vacante", "convocatoria"], thumb_at=5.2,
                 background="#FFD60A")
    t.solid(S(t, "Fondo"), "#FFD60A")
    t.text(T(t, "Título"), "¡ESTAMOS CONTRATANDO!", 0.1, 9.9, Box(40, 110, 1000, 380),
           text_style("Archivo Black", 106, [shadow("#001D3D", 8, 8, 0, 1.0), fill("#003566")], weight=400, line=0.95,
                      anim_in=tanim("pop", duration=0.45, unit="word", stagger=0.18, ease="back")), label="Título")
    enter = [(0, {"dx": 1200}, "out"), (0.6, {})]
    card(t, S(t, "Marco"), "#003566", 0.6, 9.4, centered(540, 770, 940, 580), enter, radius=30, strength=0.3)
    photos = t.track("video", "Fotos")
    box = centered(540, 770, 900, 540)
    a = t.photo(photos, "office-04", 0.6, 4.8, box, enter + [(4.8, {"s": 1.05})], label="Equipo 1")
    b = t.photo(photos, "office-02", 5.4, 4.6, box, [(0, {"s": 1.0}, "linear"), (4.6, {"s": 1.05})], label="Equipo 2")
    t.transition(photos, a, b, "slide_left", 0.5)
    for i, role in enumerate(["Barista", "Cajero(a)", "Delivery"]):
        cx = 200 + i * 340
        start = 1.2 + i * 0.2
        pill(t, S(t, f"Puesto {i + 1}"), "#003566", start, 10 - start, centered(cx, 1125, 310, 100), pop())
        t.text(T(t, f"Puesto {i + 1}"), role, start + 0.1, 9.9 - start, centered(cx, 1125, 310, 100),
               text_style("Archivo", 46, [fill("#FFD60A")], weight=700), label=f"Puesto {i + 1}")
    for i, req in enumerate(["Mayor de 18 años", "Ganas de aprender", "Horario flexible"]):
        y = 1210 + i * 95
        start = 2.2 + i * 0.4
        t.solid(S(t, f"Check {i + 1}"), "#003566", start, 10 - start, centered(150, y + 42, 56, 56), pop(),
                kind="ellipse")
        t.text(T(t, f"Visto {i + 1}"), "✓", start, 10 - start, centered(150, y + 42, 56, 56),
               text_style("Archivo", 40, [fill("#FFD60A")], weight=800), editable=False)
        t.text(T(t, f"Requisito {i + 1}"), req, start + 0.1, 9.9 - start, Box(200, y, 820, 84),
               text_style("Archivo", 54, [fill("#003566")], weight=600, align="left",
                          anim_in=tanim("slide-left", duration=0.4)), label=f"Requisito {i + 1}")
    t.solid(S(t, "Pie"), "#003566", 3.4, 6.6, Box(0, 1560, 1080, 360), slide_in(dy=360, length=0.5))
    t.text(T(t, "Cómo postular"), "Envía tu CV por WhatsApp", 3.6, 6.4, Box(40, 1600, 1000, 80),
           text_style("Archivo", 52, [fill("#FFD60A")], weight=700, anim_in=tanim("fade", duration=0.4)),
           label="Cómo postular")
    t.text(T(t, "Teléfono"), "999 999 999", 3.8, 6.2, Box(40, 1690, 1000, 140),
           text_style("Archivo Black", 110, [fill("#FFFFFF")], weight=400, anim_in=tanim("stamp", duration=0.35),
                      anim_loop=tanim("pulse", amount=3, speed=1.0)), label="Teléfono")
    t.song("from-page-to-practice", 0.0, 0.85)
    return t


# --- 10. Evento o taller ------------------------------------------------------------------------


def evento_taller() -> Template:
    t = Template("evento-taller-entrada", "Evento o taller", "Event or workshop", "business", 10.0,
                 order=1209, tags=["evento", "taller", "curso", "fecha", "inscripciones"], thumb_at=4.2,
                 background="#264653")
    t.solid(S(t, "Fondo"), "#264653")
    photos = t.track("video", "Fotos")
    top = Box(0, 0, 1080, 1060)
    a = t.photo(photos, "cooking-03", 0, 5.4, top, [(0, {"s": 1.0}, "linear"), (5.4, {"s": 1.1})], label="Foto 1")
    b = t.photo(photos, "restaurant-03", 5.0, 5.0, top, [(0, {"s": 1.1}, "linear"), (5.0, {"s": 1.0})], label="Foto 2")
    t.transition(photos, a, b, "crossfade", 0.4)
    t.solid(S(t, "Fundido"), "#264653", 0, 10.0, Box(0, 640, 1080, 440),
            layers=[gradient([(0, "#264653", 0.0), (1, "#264653", 1.0)], angle=90), no_stroke()])
    pill(t, S(t, "Etiqueta"), "#F4E9D8", 0.3, 9.7, Box(60, 90, 300, 84), slide_in(dx=-400))
    t.text(T(t, "Etiqueta"), "TALLER", 0.4, 9.6, Box(60, 90, 300, 84),
           text_style("Outfit", 44, [fill("#264653")], weight=800, spacing=8), slide_in(dx=-400), label="Tipo de evento")
    enter = slide_in(dy=1000, length=0.7)
    ticket = Box(60, 880, 960, 760)
    t.solid(S(t, "Entrada"), "#E76F51", 0.6, 9.4, ticket, enter, radius=40, kind="rounded-rectangle",
            layers=[shadow("#000000", 0, 18, 40, 0.4), fill("#E76F51"), no_stroke()])
    for x in (60, 1020):
        t.solid(S(t, "Muesca"), "#264653", 0.6, 9.4, centered(x, 1250, 70, 70), enter, kind="ellipse")
    t.text(T(t, "Corte"), "- " * 26, 0.6, 9.4, Box(110, 1225, 860, 50),
           text_style("Outfit", 36, [fill("#F4E9D8", 0.6)], weight=500), enter, editable=False)
    card(t, S(t, "Fecha"), "#F4E9D8", 0.9, 9.1, Box(110, 930, 270, 280), enter, radius=28, strength=0.2)
    date = [("SÁB", 950, 60, 700, "Día"), ("25", 990, 160, 900, "Fecha"), ("OCT", 1130, 60, 700, "Mes")]
    for content, y, size, weight, label in date:
        t.text(T(t, label), content, 0.9, 9.1, Box(110, y, 270, size + 20),
               text_style("Outfit", size, [fill("#264653" if label != "Fecha" else "#E76F51")], weight=weight,
                          line=1.0), enter, label=label)
    t.text(T(t, "Nombre del evento"), "Taller de cocina peruana", 1.1, 8.9, Box(420, 930, 560, 280),
           text_style("Outfit", 72, [fill("#FFFFFF")], weight=800, align="left", valign="middle", line=1.0,
                      anim_in=tanim("rise-by-word", duration=0.4, unit="word", stagger=0.1)), label="Nombre del evento")
    details = [("4:00 p.m. · 3 horas", "Hora"), ("Av. Larco 123, Miraflores", "Dirección"),
               ("Cupos limitados · S/ 60", "Precio")]
    for i, (content, label) in enumerate(details):
        t.text(T(t, label), content, 1.6 + i * 0.25, 8.4 - i * 0.25, Box(120, 1300 + i * 100, 860, 90),
               text_style("Outfit", 52, [fill("#FFFFFF")], weight=500, align="left",
                          anim_in=tanim("slide-left", duration=0.4)), label=label)
    pill(t, S(t, "Botón"), "#F4E9D8", 2.4, 7.6, centered(540, 1770, 820, 112),
         [(0, {"s": 0.0}, "back"), (0.4, {}, "smooth"), (0.9, {"s": 1.04}, "smooth"), (1.4, {})])
    t.text(T(t, "Inscripciones"), "Inscríbete: 999 999 999", 2.5, 7.5, centered(540, 1770, 820, 112),
           text_style("Outfit", 54, [fill("#264653")], weight=800), label="Inscripciones")
    t.song("inspiration", 0.0, 0.85)
    return t


# --- 11. Cupón ----------------------------------------------------------------------------------


def cupon_descuento() -> Template:
    t = Template("cupon-de-descuento", "Cupón de descuento", "Discount coupon", "product", 6.0,
                 order=1210, tags=["cupón", "descuento", "código", "oferta", "regalo"], thumb_at=2.6)
    t.photo(t.track("video", "Fondo"), "shopping-01", 0, 6.0, FULL, [(0, {"s": 1.08}, "linear"), (6.0, {"s": 1.0})],
            label="Fondo", effects=[effect("color.basic", exposure=-0.2, saturation=-0.3)])
    t.solid(S(t, "Velo"), "#0E6E66", alpha=0.72)
    confetti(t, 1.0, ["#FF9F1C", "#FFFFFF", "#FFE066"], lanes=3, seed=5)
    tilt = keys([(0, -14, "back"), (0.5, -3)])
    coupon = centered(540, 960, 900, 600)
    t.solid(S(t, "Cupón"), "#FF9F1C", 0.4, 5.6, coupon, pop(0, 0.5), radius=36, kind="rounded-rectangle",
            layers=[shadow("#000000", 0, 20, 40, 0.45), fill("#FF9F1C"), no_stroke()], rotation=tilt)
    dashed = {**stroke(5, "#FFFFFF"), "dash": "dash", "strokeAlign": "inside"}
    t.solid(S(t, "Borde"), "#FFFFFF", 0.4, 5.6, centered(540, 960, 840, 540), pop(0, 0.5), radius=24,
            kind="rounded-rectangle", layers=[{"id": "fill", "kind": "fill", "enabled": False,
                                               "paint": {"kind": "solid", "color": "#00000000"}}, dashed],
            rotation=tilt)
    t.text(T(t, "Título"), "Un regalo para ti", 0.2, 5.8, Box(40, 470, 1000, 130),
           text_style("Rubik", 84, [shadow("#000000", 0, 4, 12, 0.5), fill("#FFFFFF")], weight=800,
                      anim_in=tanim("drop", duration=0.5)), label="Título")
    t.text(T(t, "Cupón"), "CUPÓN", 0.7, 5.3, centered(540, 735, 700, 70),
           text_style("Rubik", 46, [fill("#FFFFFF")], weight=700, spacing=14), editable=False, rotation=tilt)
    t.text(T(t, "Descuento"), "20% DSCTO", 0.8, 5.2, centered(540, 865, 820, 190),
           text_style("Bungee", 108, [shadow("#B35F00", 0, 8, 0, 1.0), fill("#FFFFFF")], weight=400,
                      keyframes={"pixelSize": keys([(0, 240, "snap"), (0.2, 108)])}), label="Descuento",
           rotation=tilt)
    pill(t, S(t, "Código"), "#FFFFFF", 1.2, 4.8, centered(540, 1060, 520, 110), pop(), rotation=tilt)
    t.text(T(t, "Código"), "FLIP20", 1.3, 4.7, centered(540, 1060, 520, 110),
           text_style("Bungee", 70, [fill("#FF9F1C")], weight=400, spacing=6), label="Código", rotation=tilt)
    t.text(T(t, "Vigencia"), "Válido hasta el 31/10", 1.5, 4.5, centered(540, 1165, 760, 70),
           text_style("Rubik", 42, [fill("#FFFFFF")], weight=500, anim_in=tanim("fade", duration=0.4)),
           label="Vigencia", rotation=tilt)
    t.text(T(t, "Uso"), "Úsalo en tienda o por WhatsApp", 2.0, 4.0, Box(40, 1340, 1000, 80),
           text_style("Rubik", 48, [fill("#FFFFFF")], weight=600, anim_in=tanim("rise", duration=0.4)),
           label="Cómo usarlo")
    t.text(T(t, "Negocio"), "Tienda Mía · 999 999 999", 2.3, 3.7, Box(40, 1700, 1000, 80),
           text_style("Rubik", 44, [fill("#FFE066")], weight=700, anim_in=tanim("fade", duration=0.4)),
           label="Nombre y contacto")
    t.adjust([effect("strobe_flash", animated={"flash": spikes([0.8], 0.6, 0.2)}, tint=0.1)], name="Destello")
    t.song("beat-one", 0.0, 0.85)
    return t


# --- 12. Horario --------------------------------------------------------------------------------


def horario_atencion() -> Template:
    t = Template("horario-de-atencion", "Horario de atención", "Opening hours", "business", 8.0,
                 order=1211, tags=["horario", "atención", "abierto", "local", "información"], thumb_at=4.0,
                 background="#F4F1EA")
    t.solid(S(t, "Fondo"), "#F4F1EA")
    card(t, S(t, "Marco"), "#FFFFFF", 0.0, 8.0, Box(60, 90, 960, 660), slide_in(dy=-800, length=0.6), radius=40,
         shade="#2F3E46", strength=0.2)
    t.photo(t.track("video", "Local"), "cafe-04", 0.0, 8.0, Box(80, 110, 920, 620),
            [(0, {"dy": -800}, "out"), (0.6, {}, "linear"), (8.0, {"s": 1.05})], label="Tu local")
    t.solid(S(t, "Sello"), "#84A98C", 0.8, 7.2, centered(540, 760, 220, 220), pop(),
            kind="ellipse", layers=[shadow("#2F3E46", 0, 8, 20, 0.3), stroke(8, "#F4F1EA"), fill("#84A98C")])
    t.text(T(t, "Sello"), "ABIERTO", 0.9, 7.1, centered(540, 760, 220, 220),
           text_style("Manrope", 40, [fill("#FFFFFF")], weight=800, spacing=3,
                      anim_loop=tanim("pulse", amount=4, speed=1.0)), label="Sello")
    t.text(T(t, "Título"), "Horario de atención", 1.0, 7.0, Box(40, 890, 1000, 120),
           text_style("Manrope", 84, [fill("#2F3E46")], weight=800, anim_in=tanim("rise", duration=0.5)),
           label="Título")
    rows = [("Lun a Vie", "9:00 a.m. – 8:00 p.m."), ("Sábado", "9:00 a.m. – 2:00 p.m."), ("Domingo", "Cerrado")]
    for i, (day, hours) in enumerate(rows):
        y = 1040 + i * 145
        start = 1.4 + i * 0.3
        slide = [(0, {"dx": 1100}, "out"), (0.5, {})]
        card(t, S(t, f"Fila {i + 1}"), "#FFFFFF", start, 8 - start, Box(80, y, 920, 120), slide, radius=24,
             shade="#2F3E46", strength=0.12)
        t.text(T(t, f"Día {i + 1}"), day, start, 8 - start, Box(120, y, 380, 120),
               text_style("Manrope", 50, [fill("#2F3E46")], weight=700, align="left"), slide, label=f"Días {i + 1}")
        t.text(T(t, f"Hora {i + 1}"), hours, start, 8 - start, Box(450, y, 510, 120),
               text_style("Manrope", 44, [fill("#C0504D" if hours == "Cerrado" else "#52796F")], weight=700,
                          align="right"), slide, label=f"Horario {i + 1}")
    t.text(T(t, "Negocio"), "Panadería San José", 2.6, 5.4, Box(40, 1500, 1000, 100),
           text_style("Manrope", 64, [fill("#52796F")], weight=800, anim_in=tanim("fade", duration=0.5)),
           label="Nombre del negocio")
    t.text(T(t, "Dirección"), "Av. Los Olivos 321 · 999 999 999", 2.8, 5.2, Box(40, 1600, 1000, 80),
           text_style("Manrope", 44, [fill("#2F3E46")], weight=500, anim_in=tanim("fade", duration=0.5)),
           label="Dirección y teléfono")
    pill(t, S(t, "Botón"), "#2F3E46", 3.2, 4.8, centered(540, 1770, 560, 110), pop())
    t.text(T(t, "Cierre"), "¡Te esperamos!", 3.3, 4.7, centered(540, 1770, 560, 110),
           text_style("Manrope", 52, [fill("#F4F1EA")], weight=800), label="Cierre")
    t.song("adding-the-sun", 0.0, 0.8)
    return t


# --- 13. Delivery por WhatsApp ------------------------------------------------------------------


def delivery_whatsapp() -> Template:
    t = Template("delivery-pide-por-whatsapp", "Delivery: pide por WhatsApp", "Delivery: order by chat", "business",
                 8.0, order=1212, tags=["delivery", "whatsapp", "pedidos", "comida", "a domicilio"], thumb_at=5.6)
    t.solid(S(t, "Fondo"), "#25D366", layers=[gradient([(0, "#2BD873"), (1, "#0E7C6B")], angle=90), no_stroke()])
    t.text(T(t, "Título"), "Pide por WhatsApp", 0.1, 7.9, Box(40, 60, 1000, 160),
           text_style("Nunito", 100, [shadow("#075E54", 0, 6, 0, 0.8), fill("#FFFFFF")], weight=900,
                      anim_in=tanim("drop", duration=0.5)), label="Título")
    phone = [(0, {"dy": 1500}, "out"), (0.6, {})]
    t.solid(S(t, "Teléfono"), "#111B21", 0.2, 7.8, centered(540, 900, 760, 1300), phone, radius=70,
            kind="rounded-rectangle", layers=[shadow("#000000", 0, 24, 50, 0.45), fill("#111B21"), no_stroke()])
    t.solid(S(t, "Pantalla"), "#ECE5DD", 0.2, 7.8, Box(182, 272, 716, 1256), phone, radius=52,
            kind="rounded-rectangle")
    t.solid(S(t, "Cabecera"), "#075E54", 0.2, 7.8, Box(182, 272, 716, 110), phone, radius=0)
    t.text(T(t, "Contacto"), "Sabor Casero", 0.2, 7.8, Box(220, 272, 640, 110),
           text_style("Nunito", 44, [fill("#FFFFFF")], weight=800, align="left"), phone, label="Nombre del negocio")
    bubble = lambda colour: [shadow("#000000", 0, 3, 6, 0.15), fill(colour), no_stroke()]  # noqa: E731
    chat = lambda: text_style("Nunito", 40, [fill("#111B21")], weight=600, align="left", line=1.15)  # noqa: E731
    msgs = [(1.0, Box(212, 410, 520, 110), "#FFFFFF", "Hola, ¿hacen delivery?", "Mensaje del cliente 1", -1),
            (2.0, Box(388, 545, 480, 150), "#DCF8C6", "¡Sí! Te lo llevamos en 30 minutos", "Respuesta 1", 1),
            (4.0, Box(212, 1250, 520, 110), "#FFFFFF", "¡Quiero 2, por favor!", "Mensaje del cliente 2", -1),
            (5.0, Box(468, 1385, 400, 110), "#DCF8C6", "¡Va en camino!", "Respuesta 2", 1)]
    for at, box, colour, content, label, side in msgs:
        motion = [(0, {"s": 0.02, "dx": side * box.w / 2, "dy": box.h / 2}, "back"), (0.35, {})]
        t.solid(S(t, label), colour, at, 8 - at, box, motion, radius=28, kind="rounded-rectangle",
                layers=bubble(colour))
        t.text(T(t, label), content, at + 0.1, 7.9 - at, Box(box.x + 28, box.y, box.w - 56, box.h), chat(),
               label=label)
    photo_box = Box(448, 720, 420, 500)
    t.solid(S(t, "Burbuja foto"), "#DCF8C6", 2.8, 5.2, Box(432, 704, 452, 532), pop(0, 0.4), radius=28,
            kind="rounded-rectangle", layers=bubble("#DCF8C6"))
    snaps = t.track("video", "Fotos")
    a = t.photo(snaps, "food-01", 2.8, 2.6, photo_box, pop(0, 0.4), label="Plato 1")
    b = t.photo(snaps, "restaurant-02", 5.4, 2.6, photo_box, [(0, {"s": 1.0}, "linear"), (2.6, {"s": 1.05})],
                label="Plato 2")
    t.transition(snaps, a, b, "slide_left", 0.4)
    t.text(T(t, "Número"), "999 999 999", 5.6, 2.4, Box(40, 1590, 1000, 150),
           text_style("Nunito", 116, [shadow("#075E54", 0, 6, 0, 0.8), fill("#FFFFFF")], weight=900,
                      anim_in=tanim("stamp", duration=0.35), anim_loop=tanim("pulse", amount=3, speed=1.2)),
           label="WhatsApp")
    t.text(T(t, "Zona"), "Delivery gratis en Surco", 5.9, 2.1, Box(40, 1750, 1000, 80),
           text_style("Nunito", 50, [fill("#FFFFFF")], weight=700, anim_in=tanim("fade", duration=0.4)),
           label="Zona de reparto")
    t.song("llama-in-pajama", 0.0, 0.85)
    return t


# --- 14. Top 5 más vendidos ---------------------------------------------------------------------


def top5_vendidos() -> Template:
    t = Template("top-5-mas-vendidos", "Top 5 más vendidos", "Top 5 best sellers", "product", 13.0,
                 order=1213, tags=["top 5", "más vendidos", "ranking", "tienda", "ropa"], thumb_at=11.6,
                 background="#240046")
    t.solid(S(t, "Fondo"), "#5A189A", layers=[gradient([(0, "#5A189A"), (1, "#240046")], angle=90), no_stroke()])
    t.text(T(t, "Top"), "TOP 5", 0.0, 1.5, Box(0, 520, 1080, 520),
           text_style("League Gothic", 480, [shadow("#000000", 0, 12, 0, 0.5), fill("#FF9E00")], weight=400,
                      keyframes={"pixelSize": keys([(0, 900, "snap"), (0.2, 480)])}), editable=False)
    t.text(T(t, "Título"), "Lo más vendido del mes", 0.3, 1.2, Box(60, 1060, 960, 120),
           text_style("Figtree", 70, [fill("#FFFFFF")], weight=800, anim_in=tanim("rise", duration=0.4)),
           label="Título")
    items = [("outfit-04", "Casaca jean", "S/ 129.90"), ("shopping-03", "Bolso de tela", "S/ 39.90"),
             ("fashion-05", "Casaca varsity", "S/ 149.90"), ("outfit-03", "Conjunto de lino", "S/ 99.90"),
             ("outfit-01", "Top floral", "S/ 49.90")]
    cards, photos, numbers, names, prices = (S(t, "Tarjetas"), t.track("video", "Productos"), T(t, "Puestos"),
                                             T(t, "Nombres"), T(t, "Precios"))
    for i, (sample, name, price) in enumerate(items):
        rank = 5 - i
        start = 1.5 + i * 2.2
        dur = 2.2 if i < 4 else 13 - start
        enter = [(0, {"dx": 1100}, "out"), (0.45, {}, "linear"), (dur, {"s": 1.03})]
        tilt = keys([(0, 3 if i % 2 else -3)])
        t.solid(cards, "#FF9E00", start, dur, centered(580, 900, 820, 1080), enter, radius=36,
                kind="rounded-rectangle", layers=[shadow("#10002B", 0, 20, 40, 0.5), fill("#FF9E00"), no_stroke()],
                rotation=tilt)
        t.photo(photos, sample, start, dur, centered(580, 900, 780, 1040), enter, label=f"Puesto {rank}",
                rotation=tilt)
        t.text(numbers, f"#{rank}", start + 0.15, dur - 0.15, Box(20, 220, 460, 460),
               text_style("League Gothic", 400, [shadow("#10002B", 0, 10, 0, 0.6), stroke(10, "#FF9E00"),
                                                 fill("#FFFFFF")], weight=400, align="left",
                          keyframes={"pixelSize": keys([(0, 700, "snap"), (0.2, 400)])}), editable=False)
        t.text(names, name, start + 0.25, dur - 0.25, Box(60, 1500, 960, 110),
               text_style("Figtree", 80, [fill("#FFFFFF")], weight=800, anim_in=tanim("slide-up", duration=0.35)),
               label=f"Producto {rank}")
        t.text(prices, price, start + 0.35, dur - 0.35, Box(60, 1610, 960, 90),
               text_style("Figtree", 64, [fill("#FF9E00")], weight=700, anim_in=tanim("fade", duration=0.3)),
               label=f"Precio {rank}")
    t.text(T(t, "Tienda"), "@tutienda", 1.5, 11.5, Box(60, 1780, 960, 70),
           text_style("Figtree", 44, [fill("#E0C3FC")], weight=600), label="Usuario")
    t.adjust([effect("strobe_flash", animated={"flash": spikes([0.0, 10.3], 0.7, 0.25)}, tint=0.2),
              effect("beat_shake", animated={"amount": spikes([1.5 + i * 2.2 for i in range(5)], 0.5, 0.3)},
                     rotation=0.3)], name="Golpe")
    t.song("arpent", 0.0, 0.85)
    return t


# --- 15. Tutorial en 3 pasos --------------------------------------------------------------------


def tutorial_3_pasos() -> Template:
    t = Template("tutorial-en-3-pasos", "Tutorial en 3 pasos", "3-step tutorial", "business", 12.0,
                 order=1214, tags=["tutorial", "pasos", "cómo hacer", "tips", "belleza"], thumb_at=3.6,
                 background="#FFFFFF")
    t.solid(S(t, "Fondo"), "#FFFFFF")
    hook = t.track("video", "Resultado")
    t.photo(hook, "makeup-02", 0, 2.0, FULL, [(0, {"s": 1.12}, "out"), (2.0, {"s": 1.0})], label="Resultado")
    t.text(T(t, "Gancho"), "Maquillaje natural en 3 pasos", 0.2, 1.8, Box(60, 1300, 960, 400),
           text_style("Plus Jakarta Sans", 100, [fill("#FFFFFF")], weight=800, line=1.05, box=("#FF6B6B", 1.0),
                      box_pad=20, box_radius=16,
                      anim_in=tanim("pop", duration=0.4, unit="word", stagger=0.1)), label="Título")
    steps = [("makeup-01", "Prepara la piel", "Hidrata y aplica una base ligera"),
             ("salon-01", "Define las cejas", "Peina y rellena con trazos cortos"),
             ("makeup-03", "Dale color", "Rubor y labial en el mismo tono")]
    cards, photos = S(t, "Tarjetas"), t.track("video", "Pasos")
    badges, digits, titles, notes = S(t, "Número"), T(t, "Número"), T(t, "Paso"), T(t, "Detalle")
    for i, (sample, title, note) in enumerate(steps):
        start = 2.0 + i * 2.8
        enter = [(0, {"dx": 1100}, "out"), (0.45, {}, "linear"), (2.8, {"s": 1.03})]
        card(t, cards, "#FFFFFF", start, 2.8, Box(50, 210, 980, 1170), enter, radius=44, strength=0.2)
        t.photo(photos, sample, start, 2.8, Box(70, 230, 940, 1130), enter, label=f"Paso {i + 1}")
        t.solid(badges, "#FF6B6B", start + 0.3, 2.5, centered(170, 280, 170, 170), pop(), kind="ellipse",
                layers=[shadow("#000000", 0, 8, 20, 0.3), stroke(8, "#FFFFFF"), fill("#FF6B6B")])
        t.text(digits, str(i + 1), start + 0.35, 2.45, centered(170, 280, 170, 170),
               text_style("Plus Jakarta Sans", 100, [fill("#FFFFFF")], weight=800), editable=False)
        t.text(titles, title, start + 0.3, 2.5, Box(60, 1420, 960, 110),
               text_style("Plus Jakarta Sans", 80, [fill("#222222")], weight=800,
                          anim_in=tanim("slide-up", duration=0.4)), label=f"Paso {i + 1}")
        t.text(notes, note, start + 0.5, 2.3, Box(60, 1540, 960, 150),
               text_style("Plus Jakarta Sans", 50, [fill("#666666")], weight=500, line=1.2,
                          anim_in=tanim("fade", duration=0.4)), label=f"Detalle {i + 1}")
        t.solid(S(t, "Progreso"), "#EEEEEE", 2.0, 10.0, Box(60 + i * 330, 110, 300, 16), radius=8,
                kind="rounded-rectangle")
        t.solid(S(t, "Progreso"), "#FF6B6B", start, 2.8, Box(60 + i * 330, 110, 300, 16),
                [(0, {"sx": 0.0, "dx": -150}, "linear"), (2.6, {})], radius=8, kind="rounded-rectangle")
        t.solid(S(t, "Progreso"), "#FF6B6B", start + 2.8, 12 - start - 2.8, Box(60 + i * 330, 110, 300, 16),
                radius=8, kind="rounded-rectangle")
    t.photo(hook, "makeup-02", 10.4, 1.6, FULL, [(0, {"s": 1.0}, "linear"), (1.6, {"s": 1.08})], reuse="p1")
    t.text(T(t, "Cierre"), "¡Listo! Guárdalo para después", 10.5, 1.5, Box(60, 1400, 960, 300),
           text_style("Plus Jakarta Sans", 84, [fill("#FFFFFF")], weight=800, line=1.05, box=("#FF6B6B", 1.0),
                      box_pad=20, box_radius=16, anim_in=tanim("pop", duration=0.4)), label="Cierre")
    t.text(T(t, "Usuario"), "@tunegocio", 2.0, 8.4, Box(60, 1790, 960, 70),
           text_style("Plus Jakarta Sans", 42, [fill("#FF6B6B")], weight=700), label="Usuario")
    t.song("infinite-wonder", 0.0, 0.8)
    return t


# --- 16. Nosotros vs. otros ---------------------------------------------------------------------


def nosotros_vs_otros() -> Template:
    t = Template("nosotros-vs-otros", "Nosotros vs. otros", "Us vs. others", "business", 8.0,
                 order=1215, tags=["comparativa", "nosotros", "calidad", "por qué elegirnos", "vs"], thumb_at=4.6,
                 background="#111111")
    left = t.track("video", "Otros")
    t.photo(left, "food-02", 0.2, 7.8, Box(0, 0, 540, 1160), [(0, {"dx": -600}, "out"), (0.5, {})],
            label="Otros", effects=[effect("color.basic", saturation=-0.9, exposure=-0.15)])
    right = t.track("video", "Nosotros")
    t.photo(right, "food-03", 0.3, 7.7, Box(540, 0, 540, 1160), [(0, {"dx": 600}, "out"), (0.5, {})],
            label="Nosotros", effects=[effect("color.basic", vibrance=0.3, contrast=0.1)])
    t.solid(S(t, "Panel"), "#151515", 0, 8.0, Box(0, 1160, 1080, 760))
    t.solid(S(t, "Divisor"), "#FFFFFF", 0.5, 7.5, Box(536, 0, 8, 1920), [(0, {"sy": 0.0}, "out"), (0.6, {})],
            alpha=0.85)
    for x, colour, ink, word, label in ((60, "#6C757D", "#FFFFFF", "Otros", "Otros (título)"),
                                        (600, "#06D6A0", "#0B3D2E", "Nosotros", "Nosotros (título)")):
        pill(t, S(t, label), colour, 0.6, 7.4, Box(x, 90, 420, 110), pop())
        t.text(T(t, label), word, 0.7, 7.3, Box(x, 90, 420, 110),
               text_style("Kanit", 64, [fill(ink)], weight=800), label=label)
    t.solid(S(t, "VS"), "#E63946", 0.8, 7.2, centered(540, 1160, 200, 200), pop(),
            kind="ellipse", layers=[shadow("#000000", 0, 8, 24, 0.5), stroke(8, "#FFFFFF"), fill("#E63946")])
    t.text(T(t, "VS"), "VS", 0.9, 7.1, centered(540, 1160, 200, 200),
           text_style("Kanit", 96, [fill("#FFFFFF")], weight=900,
                      keyframes={"pixelSize": keys([(0, 220, "snap"), (0.2, 96)])}), editable=False)
    pairs = [("Demora 1 hora", "Llega en 30 min"), ("Porciones chicas", "Porción generosa"),
             ("Precio alto", "Desde S/ 18")]
    for i, (them, us_) in enumerate(pairs):
        y = 1300 + i * 140
        start = 1.4 + i * 0.9
        t.text(T(t, f"Otros {i + 1}"), f"✗ {them}", start, 8 - start, Box(40, y, 480, 120),
               text_style("Kanit", 48, [fill("#9AA1A8")], weight=500, align="left",
                          anim_in=tanim("slide-right", duration=0.35)), label=f"Otros {i + 1}")
        t.text(T(t, f"Nosotros {i + 1}"), f"✓ {us_}", start + 0.3, 7.7 - start, Box(570, y, 490, 120),
               text_style("Kanit", 48, [fill("#06D6A0")], weight=700, align="left",
                          anim_in=tanim("pop", duration=0.35)), label=f"Nosotros {i + 1}")
    pill(t, S(t, "Botón"), "#06D6A0", 4.6, 3.4, centered(540, 1790, 800, 110), pop())
    t.text(T(t, "Llamada"), "Pruébalo hoy · @tunegocio", 4.7, 3.3, centered(540, 1790, 800, 110),
           text_style("Kanit", 52, [fill("#0B3D2E")], weight=700), label="Llamada")
    t.adjust([effect("beat_shake", animated={"amount": spikes([0.9], 0.7, 0.3)}, rotation=0.3)], name="Golpe")
    t.song("fake-it-til-you-fake-it", 0.0, 0.85)
    return t


# --- 17. Preguntas frecuentes -------------------------------------------------------------------


def preguntas_frecuentes() -> Template:
    t = Template("preguntas-frecuentes", "Preguntas frecuentes", "FAQ", "business", 12.0,
                 order=1216, tags=["preguntas", "faq", "dudas", "atención al cliente", "envíos"], thumb_at=5.8,
                 background="#F1F5F9")
    t.solid(S(t, "Fondo"), "#F1F5F9")
    t.photo(t.track("video", "Cabecera"), "shopping-02", 0, 12.0, Box(0, 0, 1080, 560),
            [(0, {"s": 1.0}, "linear"), (12.0, {"s": 1.08})], label="Cabecera")
    t.solid(S(t, "Velo"), "#7C3AED", 0, 12.0, Box(0, 0, 1080, 560), alpha=0.72)
    t.text(T(t, "Negocio"), "Tienda Lucía", 0.2, 11.8, Box(60, 90, 960, 70),
           text_style("Urbanist", 44, [fill("#EDE9FE")], weight=700, spacing=6, case="upper", align="left",
                      anim_in=tanim("fade", duration=0.5)), label="Nombre del negocio")
    t.text(T(t, "Título"), "Preguntas frecuentes", 0.3, 11.7, Box(60, 170, 960, 300),
           text_style("Urbanist", 120, [fill("#FFFFFF")], weight=900, align="left", line=0.95,
                      anim_in=tanim("rise-by-word", duration=0.5, unit="word", stagger=0.15)), label="Título")
    faqs = [("¿Hacen envíos a provincia?", "Sí, enviamos a todo el Perú. Llega en 2 a 4 días hábiles."),
            ("¿Cómo puedo pagar?", "Transferencia, billetera digital o efectivo contra entrega."),
            ("¿Tienen tienda física?", "Sí, en Av. Arequipa 456, Lince. De lunes a sábado.")]
    qs, qtext, ans, atext, count = S(t, "Pregunta"), T(t, "Pregunta"), S(t, "Respuesta"), T(t, "Respuesta"), T(t, "N")
    for i, (q, a) in enumerate(faqs):
        start = 0.8 + i * 3.4
        last = i == len(faqs) - 1
        dur = 12 - start if last else 3.4

        def move(length: float, last: bool = last) -> list:
            enter = [(0, {"dx": 1100}, "out"), (0.45, {})]
            return enter if last else enter[:1] + [(0.45, {}, "linear"), (length - 0.35, {}, "in"),
                                                   (length, {"dx": -1100})]
        t.solid(qs, "#7C3AED", start, dur, Box(60, 640, 960, 220), move(dur), radius=32, kind="rounded-rectangle",
                layers=[shadow("#4C1D95", 0, 12, 30, 0.35), fill("#7C3AED"), no_stroke()])
        t.text(qtext, q, start, dur, Box(110, 640, 860, 220),
               text_style("Urbanist", 64, [fill("#FFFFFF")], weight=800, align="left", line=1.05), move(dur),
               label=f"Pregunta {i + 1}")
        card(t, ans, "#FFFFFF", start + 0.3, dur - 0.3, Box(60, 900, 960, 480), move(dur - 0.3), radius=32,
             shade="#334155", strength=0.12)
        t.text(atext, a, start + 0.5, dur - 0.5, Box(110, 940, 860, 400),
               text_style("Urbanist", 58, [fill("#334155")], weight=500, align="left", valign="top", line=1.25,
                          anim_in=tanim("rise-by-word", duration=0.35, unit="word", stagger=0.05)),
               move(dur - 0.5), label=f"Respuesta {i + 1}")
        t.text(count, f"{i + 1}/{len(faqs)}", start, dur, Box(60, 1420, 960, 80),
               text_style("Urbanist", 48, [fill("#A78BFA")], weight=800), editable=False)
    pill(t, S(t, "Botón"), "#111827", 1.2, 10.8, centered(540, 1720, 920, 130), pop())
    t.text(T(t, "Contacto"), "¿Más dudas? 999 999 999", 1.3, 10.7, centered(540, 1720, 920, 130),
           text_style("Urbanist", 56, [fill("#FFFFFF")], weight=800), label="Contacto")
    t.song("i-guess-what-i-m-trying-to-say", 0.0, 0.8)
    return t


# --- 18. Gran inauguración ----------------------------------------------------------------------


def gran_inauguracion() -> Template:
    t = Template("gran-inauguracion", "Gran inauguración", "Grand opening", "business", 10.0,
                 order=1217, tags=["inauguración", "apertura", "nuevo local", "abrimos", "evento"], thumb_at=4.4)
    photos = t.track("video", "Local")
    a = t.photo(photos, "cafe-01", 0, 5.8, FULL, [(0, {"s": 1.15}, "linear"), (1.4, {"s": 1.08}, "linear"),
                                                  (5.8, {"s": 1.0})], label="Tu local")
    b = t.photo(photos, "cafe-04", 5.4, 4.6, FULL, [(0, {"s": 1.0}, "linear"), (4.6, {"s": 1.08})], label="Foto 2")
    t.transition(photos, a, b, "crossfade", 0.4)
    t.solid(S(t, "Velo"), "#2B0A0A", 1.4, 8.6, alpha=0.5, opacity=keys([(0, 0.0, "smooth"), (0.6, 1.0)]))
    # The ribbon: two halves that meet in the middle, then fly apart when it is "cut".
    for side, x in ((-1, -40), (1, 540)):
        motion = [(0, {}, "linear"), (1.3, {}, "in"), (2.2, {"dx": side * 760, "dy": 520})]
        t.solid(S(t, "Cinta"), "#D62828", 0, 2.2, Box(x, 900, 580, 120), motion,
                layers=[shadow("#000000", 0, 8, 18, 0.4), gradient([(0, "#E63946"), (1, "#A4161A")], angle=90),
                        no_stroke()], rotation=keys([(0, 0), (1.3, 0, "in"), (2.2, side * 35)]))
    t.solid(S(t, "Moño"), "#F7B801", 0, 1.4, centered(540, 960, 200, 200), [(0, {}, "linear"), (1.2, {}, "in"),
                                                                             (1.4, {"s": 0.02})], kind="burst",
            layers=[shadow("#000000", 0, 6, 14, 0.4), fill("#F7B801"), no_stroke()])
    t.text(T(t, "Antes"), "Muy pronto…", 0.1, 1.3, Box(40, 1200, 1000, 140),
           text_style("Montserrat", 70, [shadow("#000000", 0, 4, 14, 0.7), fill("#FFFFFF")], weight=800,
                      anim_in=tanim("fade", duration=0.4)), label="Antes del corte")
    t.solid(S(t, "Destello"), "#FFFFFF", 1.4, 0.3, FULL, opacity=keys([(0, 0.9, "out"), (0.3, 0.0)]))
    confetti(t, 1.4, ["#F7B801", "#D62828", "#FFFFFF", "#FFE08A"], lanes=4, seed=9)
    gold = [shadow("#3A0505", 0, 10, 0, 1.0), stroke(10, "#7A0E0E"), gradient([(0, "#FFE08A"), (1, "#F7B801")], angle=90)]
    t.text(T(t, "Título"), "¡Gran inauguración!", 1.5, 8.5, Box(40, 300, 1000, 520),
           text_style("Shrikhand", 128, gold, weight=400, line=1.0,
                      anim_in=tanim("pop", duration=0.5, unit="word", stagger=0.15, ease="back"),
                      anim_loop=tanim("float", amount=0.08, speed=0.5)), label="Título")
    t.text(T(t, "Negocio"), "Café Aroma", 1.8, 8.2, Box(40, 160, 1000, 110),
           text_style("Montserrat", 64, [shadow("#000000", 0, 4, 12, 0.6), fill("#FFFFFF")], weight=900, spacing=8,
                      case="upper", anim_in=tanim("fade", duration=0.5)), label="Nombre del negocio")
    t.text(T(t, "Fecha"), "Sábado 1 de noviembre · 10 a.m.", 2.4, 7.6, Box(70, 1300, 940, 120),
           text_style("Montserrat", 50, [fill("#FFFFFF")], weight=800, box=("#D62828", 1.0), box_pad=22,
                      box_radius=60, anim_in=tanim("slide-up", duration=0.4)), label="Fecha y hora")
    t.text(T(t, "Dirección"), "Jr. Unión 789, Trujillo", 2.8, 7.2, Box(40, 1460, 1000, 90),
           text_style("Montserrat", 52, [shadow("#000000", 0, 4, 12, 0.7), fill("#FFFFFF")], weight=700,
                      anim_in=tanim("fade", duration=0.4)), label="Dirección")
    t.text(T(t, "Promo"), "¡Regalos para los primeros 50!", 3.2, 6.8, Box(40, 1590, 1000, 110),
           text_style("Montserrat", 58, [shadow("#000000", 0, 4, 12, 0.7), fill("#F7B801")], weight=800,
                      anim_in=tanim("pop", duration=0.4), anim_loop=tanim("pulse", amount=4, speed=1.0)),
           label="Promoción")
    t.adjust([effect("bling_sparkle", intensity=0.45, density=0.35, threshold=0.75, colorize=0.4),
              effect("beat_shake", animated={"amount": spikes([1.4], 0.8, 0.4)}, rotation=0.4)], name="Fiesta")
    t.song("bar-brawl", 0.0, 0.85)
    return t


# --- 19. Nueva colección ------------------------------------------------------------------------


def nueva_coleccion() -> Template:
    t = Template("nueva-coleccion-ropa", "Nueva colección", "New collection", "product", 10.0,
                 order=1218, tags=["nueva colección", "ropa", "moda", "boutique", "temporada"], thumb_at=2.6,
                 background="#EFE9E1")
    t.solid(S(t, "Fondo"), "#EFE9E1")
    t.text(T(t, "Marca"), "Boutique Lucía", 0.2, 9.8, Box(20, 110, 700, 80),
           text_style("Work Sans", 40, [fill("#111111")], weight=600, spacing=12, case="upper", align="left",
                      anim_in=tanim("fade", duration=0.6)), label="Nombre del negocio")
    t.text(T(t, "Disponible"), "Disponible ya", 0.4, 9.6, Box(560, 110, 500, 80),
           text_style("Work Sans", 36, [fill("#7A6E62")], weight=500, spacing=4, align="right",
                      anim_in=tanim("fade", duration=0.6)), label="Disponible")
    t.solid(S(t, "Línea"), "#111111", 0.3, 9.7, Box(20, 200, 1040, 3), [(0, {"sx": 0.0}, "out"), (0.8, {})])
    w, gap = 336, 16
    for i, sample in enumerate(["outfit-03", "outfit-04", "portrait-05"]):
        x = 20 + i * (w + gap)
        drift = 1 if i % 2 else -1
        motion = [(0, {"dy": drift * 1400}, "out"), (0.7 + i * 0.1, {}, "linear"), (4.2, {"dy": -drift * 40})]
        t.photo(t.track("video", f"Tira {i + 1}"), sample, 0.3, 4.2, Box(x, 240, w, 1160), motion,
                label=f"Look {i + 1}")
    big = t.track("video", "Principal")
    box = Box(20, 240, 1040, 1160)
    a = t.photo(big, "fashion-05", 4.2, 3.2, box, [(0, {"s": 1.1}, "linear"), (3.2, {"s": 1.0})],
                label="Foto principal")
    b = t.photo(big, "outfit-01", 7.4, 2.6, box, [(0, {"s": 1.0}, "linear"), (2.6, {"s": 1.06})], label="Look 5")
    t.transition(big, a, b, "crossfade", 0.5)
    reveal = [(0, 0.0, "inout"), (0.7, 1.0)]
    t.mask(big, a, "rectangle", w=0.0, keyframes={"w": keys(reveal)})
    t.text(T(t, "Título"), "Nueva colección", 0.6, 9.4, Box(20, 1420, 1040, 220),
           text_style("Bodoni Moda", 122, [fill("#111111")], weight=700, italic=True, align="left", line=0.9,
                      anim_in=tanim("wipe", duration=0.8, angle=0)), label="Título")
    t.text(T(t, "Temporada"), "Primavera – Verano 2026", 1.2, 8.8, Box(24, 1650, 1040, 70),
           text_style("Work Sans", 44, [fill("#7A6E62")], weight=500, spacing=8, case="upper", align="left",
                      anim_in=tanim("fade", duration=0.6)), label="Temporada")
    t.text(T(t, "Llamada"), "Compra online · link en la bio", 1.8, 8.2, Box(24, 1770, 1040, 70),
           text_style("Work Sans", 40, [fill("#111111")], weight=600, align="left",
                      anim_in=tanim("slide-up", duration=0.5)), label="Llamada")
    t.adjust([effect("stylize.film_grain", amount=0.15, grainSize=1.5),
              effect("color.basic", fade=0.08, temperature=0.05)], name="Editorial")
    t.song("downtown-boogie", 0.0, 0.85)
    return t


# --- 20. Reseñas --------------------------------------------------------------------------------


def resenas_clientes() -> Template:
    t = Template("resenas-lo-que-dicen", "Lo que dicen nuestros clientes", "What our customers say", "business",
                 10.0, order=1219, tags=["reseñas", "opiniones", "clientes", "5 estrellas", "calificación"],
                 thumb_at=6.8, background="#0F172A")
    t.solid(S(t, "Fondo"), "#0F172A", layers=[gradient([(0, "#16213D"), (1, "#0B1120")], angle=90), no_stroke()])
    t.text(T(t, "Título"), "Lo que dicen nuestros clientes", 0.1, 9.9, Box(60, 100, 960, 230),
           text_style("Sora", 84, [fill("#FFFFFF")], weight=800, align="left", line=1.05,
                      anim_in=tanim("rise-by-word", duration=0.45, unit="word", stagger=0.08)), label="Título")
    t.text(T(t, "Nota"), "4.9", 0.5, 9.5, Box(60, 330, 420, 260),
           text_style("Sora", 220, [glow("#FACC15", 30, 0.5), fill("#FACC15")], weight=800, align="left",
                      anim_in=tanim("pop", duration=0.45)), label="Calificación")
    star_row(t, 0.8, 9.2, 800, 420, 66, 10, "#FACC15", stagger=0.1)
    t.text(T(t, "Cantidad"), "+200 reseñas", 1.2, 8.8, Box(560, 480, 480, 70),
           text_style("Sora", 42, [fill("#94A3B8")], weight=500, anim_in=tanim("fade", duration=0.4)),
           label="Cantidad de reseñas")
    reviews = [("portrait-04", "Lucía R.", "Excelente atención, todo llegó rápido y bien empacado."),
               ("man-01", "Diego P.", "Los precios son justos y la calidad es increíble."),
               ("creator-03", "Andrea V.", "Ya es mi tienda favorita. ¡Súper recomendada!")]
    for i, (sample, name, text) in enumerate(reviews):
        y = 640 + i * 360
        start = 1.0 + i * 1.6
        dur = 10 - start
        slide = [(0, {"dx": 1100}, "out"), (0.55, {})]
        t.solid(S(t, f"Reseña {i + 1}"), "#1E293B", start, dur, Box(60, y, 960, 320), slide, radius=32,
                kind="rounded-rectangle", layers=[shadow("#000000", 0, 12, 30, 0.4), stroke(2, "#334155"),
                                                  fill("#1E293B")])
        round_photo(t, sample, start, dur, 160, y + 90, 120, slide, ring="#FACC15", ring_w=5,
                    label=f"Foto cliente {i + 1}", name=f"Cliente {i + 1}")
        t.text(T(t, f"Nombre {i + 1}"), name, start, dur, Box(250, y + 35, 720, 60),
               text_style("Sora", 46, [fill("#FFFFFF")], weight=700, align="left"), slide,
               label=f"Nombre cliente {i + 1}")
        t.text(T(t, f"Estrellas {i + 1}"), "★★★★★", start, dur, Box(250, y + 95, 720, 50),
               text_style("Sora", 38, [fill("#FACC15")], weight=400, align="left", spacing=4), slide,
               editable=False)
        t.text(T(t, f"Opinión {i + 1}"), text, start + 0.3, dur - 0.3, Box(100, y + 170, 880, 130),
               text_style("Sora", 40, [fill("#CBD5E1")], weight=400, align="left", line=1.2,
                      anim_in=tanim("fade", duration=0.5)), label=f"Opinión {i + 1}")
    t.text(T(t, "Negocio"), "Tienda Lucía · @tienda.lucia", 5.0, 5.0, Box(60, 1740, 960, 80),
           text_style("Sora", 44, [fill("#FACC15")], weight=700, anim_in=tanim("slide-up", duration=0.4)),
           label="Nombre del negocio")
    t.song("alls-fair-in-love", 0.0, 0.85)
    return t


TEMPLATES = [menu_del_dia, cafe_nuevo_carta, salon_belleza, unas_manicure, barberia_antes_despues, gimnasio_promo,
             lanzamiento_producto, testimonio_cliente, estamos_contratando, evento_taller, cupon_descuento,
             horario_atencion, delivery_whatsapp, top5_vendidos, tutorial_3_pasos, nosotros_vs_otros,
             preguntas_frecuentes, gran_inauguracion, nueva_coleccion, resenas_clientes]
