"""Horizontal batch 4 (2026-10-16): celebrations, international dates and businesses, 1920x1080.
See BRIEF.md, «Las 400 nuevas». Categories celebration, seasonal, business; order 2300-2399.

Dates are for everyone (no country-only holidays); business texts are short and neutral so any shop in any
country can use them.
"""

from __future__ import annotations

from kit import (Box, appear, bg, bg_gradient, blink, centered, circle_photo, confetti, dots, effect, fill, flash,
                 framed, glow, gradient, grain, keys, kb, label, letterbox, line, math, no_stroke, outline, panels,
                 photo_bg, pill, pop, random, ring, rrect, shade_bottom, shade_full, shade_top, shadow, slide_in, slides,
                 song, spike, stroke, tanim, vignette, wide)


def _info_rows(t, rows, x, y0, step, t0, font="Montserrat", size=46, colour="#FFFFFF", icon_bg="#FFFFFF",
               icon_colour="#111111", width=860, gap=0.25):
    for i, (icon, txt) in enumerate(rows):
        at = t0 + i * gap
        y = y0 + i * step
        t.solid(t.track("shape", "Icono"), icon_bg, at, t.duration - at, centered(x + 40, y + 40, 80, 80), pop(0, 0.35),
                kind="ellipse")
        label(t, t.track("text", "Icono"), icon, at, t.duration - at, centered(x + 40, y + 40, 80, 80), "Inter", 40,
              icon_colour, weight=700, editable=False, motion=pop(0, 0.35))
        label(t, t.track("text", "Dato"), txt, at + 0.1, t.duration - at - 0.1, Box(x + 110, y, width, 80), font, size,
              colour, weight=600, align="left", anim_in=tanim("slide-right", duration=0.35, distance=0.1),
              name=f"Dato {i + 1}")


# --- Celebrations -------------------------------------------------------------------------------

def cele_baby_shower():
    t = wide("h-cele-baby-shower", "Baby shower", "Baby shower", "celebration", 9.0, order=2300,
             tags=["baby shower", "bebé", "invitación", "embarazo", "fiesta"], thumb_at=4.6, background="#FDF3F7")
    bg_gradient(t, [(0, "#FDF3F7"), (1, "#E7F3FC")], angle=90)
    rng = random.Random(300)
    for k in range(8):
        x = rng.uniform(80, 1840)
        s = rng.uniform(110, 160)
        c = rng.choice(["#F9C6D9", "#BDE0FE", "#FFF1B5", "#CDEAC0"])
        at = rng.uniform(0, 1.2)
        t.solid(t.track("shape", "Globo"), c, at, 9.0 - at, centered(x, 260 + rng.uniform(-60, 80), s, s * 1.2),
                [(0, {"dy": 900}, "out"), (2.0, {}, "smooth"), (9.0 - at, {"dy": -40})], kind="ellipse",
                layers=[gradient([(0, "#FFFFFF", 0.6), (0.4, c), (1, c)], angle=135), no_stroke()])
    circle_photo(t, "h-baby-04", 0.5, 8.5, centered(1460, 600, 560, 560), pop(0, 0.6, 0.5), ring_colour="#FFFFFF",
                 ring_width=16, label="Foto")
    label(t, t.track("text", "Título"), "Baby shower", 0.8, 8.2, Box(140, 300, 1000, 200), "Pacifico", 150, "#E07A9B",
          weight=400, layers=[shadow("#FFFFFF", 0, 6, 0, 1.0), fill("#E07A9B")], anim_in=tanim("pop", duration=0.5),
          name="Título")
    label(t, t.track("text", "Mamá"), "para Valentina", 1.3, 7.7, Box(140, 500, 1000, 100), "Quicksand", 64, "#5C7FA3",
          weight=700, anim_in=tanim("fade", duration=0.5), name="Para")
    _info_rows(t, [("📅", "Sábado 21 de noviembre"), ("🕑", "15:00 h"), ("📍", "Casa de la abuela")], 160, 640, 100, 1.8,
               font="Quicksand", size=44, colour="#3D5A80", icon_bg="#F9C6D9", icon_colour="#3D5A80", width=800)
    song(t, "fun", 1, 0.7)
    return t


def cele_graduacion():
    t = wide("h-cele-graduacion", "Graduación", "Graduation", "celebration", 9.0, order=2301,
             tags=["graduación", "birrete", "logro", "universidad", "colegio"], thumb_at=4.6, background="#0A1F44")
    photo_bg(t, "h-graduation-02", s1=1.08, label="Foto de la graduación")
    shade_full(t, 0.55, colour="#0A1F44")
    label(t, t.track("text", "Birrete"), "🎓", 0.4, 8.6, centered(960, 230, 260, 260), "Inter", 190, "#FFFFFF", weight=400,
          editable=False, motion=[(0, {"dy": -400}, "back"), (0.6, {})])
    label(t, t.track("text", "Felicidades"), "¡Felicidades, graduada!", 0.9, 8.1, Box(160, 400, 1600, 200),
          "Playfair Display", 130, "#D4AF37", weight=800, layers=[glow("#D4AF37", 18, 0.5), fill("#F5D98B")],
          anim_in=tanim("rise-by-word", duration=0.5, unit="word", stagger=0.15), name="Felicidades")
    label(t, t.track("text", "Nombre"), "Carla Medina · Ingeniería 2026", 1.5, 7.5, Box(160, 620, 1600, 90), "Montserrat",
          56, "#FFFFFF", weight=600, spacing=2, anim_in=tanim("fade", duration=0.5), name="Nombre")
    confetti(t, ["#D4AF37", "#FFFFFF", "#9FB4D9"], 1.0, 8.0, seed=301, lanes=4, density=0.3)
    song(t, "epic", 2, 0.75)
    return t


def cele_boda_invitacion():
    t = wide("h-cele-boda-invitacion", "Invitación de boda", "Wedding invitation", "celebration", 10.0, order=2302,
             tags=["boda", "invitación", "save the date", "matrimonio", "elegante"], thumb_at=6.0, background="#F7F2EA")
    bg(t, "#F7F2EA")
    t.photo(t.track("video", "Foto"), "h-wedding-04", 0, 10.0, Box(0, 0, 820, 1080), kb(10.0, 1.0, 1.06),
            label="Foto de los novios")
    outline(t, t.track("shape", "Marco"), "#B89B5E", 2, 0.4, 9.6, Box(900, 70, 950, 940), alpha=0.9,
            opacity=keys([(0, 0.0), (0.8, 1.0)]))
    label(t, t.track("text", "Invitan"), "TE INVITAMOS A NUESTRA BODA", 0.8, 9.2, Box(940, 150, 870, 60), "Cinzel", 34,
          "#8C6B2F", weight=500, spacing=8, anim_in=tanim("fade", duration=0.8), name="Invitación")
    label(t, t.track("text", "Nombres"), "Elena\n& Tomás", 1.2, 8.8, Box(940, 230, 870, 380), "Great Vibes", 150, "#3B2C20",
          weight=400, line=0.95, anim_in=tanim("blur-in", duration=1.2, blur=14), name="Nombres")
    line(t, t.track("shape", "Línea"), "#B89B5E", 2.0, 8.0, centered(1375, 650, 300, 2), grow="c", length=0.8)
    label(t, t.track("text", "Fecha"), "SÁBADO 12 · JUNIO · 2027", 2.2, 7.8, Box(940, 680, 870, 70), "Cinzel", 44, "#3B2C20",
          weight=600, spacing=6, anim_in=tanim("fade", duration=0.8), name="Fecha")
    label(t, t.track("text", "Lugar"), "Jardín Las Acacias · 17:00 h", 2.6, 7.4, Box(940, 760, 870, 60), "Cormorant Garamond",
          46, "#6B5640", weight=500, italic=True, anim_in=tanim("fade", duration=0.8), name="Lugar")
    label(t, t.track("text", "RSVP"), "Confirma tu asistencia antes del 1 de mayo", 3.0, 7.0, Box(940, 880, 870, 60),
          "Montserrat", 30, "#8C6B2F", weight=500, anim_in=tanim("fade", duration=0.8), name="Confirmación")
    song(t, "romantic", 0, 0.7)
    return t


def cele_15_16():
    t = wide("h-cele-15-16", "Mis 15 · Sweet 16", "Sweet sixteen", "celebration", 10.0, order=2303,
             tags=["15 años", "sweet 16", "quinceañera", "fiesta", "princesa"], thumb_at=5.0, background="#1B0B2E")
    slides(t, ["h-portrait-06", "h-birthday-03", "h-portrait-04"], 0.0, 3.4, transition="blur_dissolve", tdur=0.8,
           kb_amount=0.07, effects_fn=lambda i: [effect("color.basic", temperature=0.06, fade=0.08)])
    shade_full(t, 0.4, colour="#1B0B2E")
    dots(t, ["#F5D98B", "#FFFFFF", "#F9A8D4"], 32, 0, 10.0, seed=303, size=(8, 20), kinds=("star",), drift=90)
    label(t, t.track("text", "Número"), "16", 0.6, 9.4, Box(160, 170, 1600, 420), "Playfair Display", 400, "#F5D98B",
          weight=800, layers=[glow("#F5D98B", 30, 0.6), gradient([(0, "#FFF4D6"), (0.5, "#E8C27A"), (1, "#B8892E")],
                                                                  angle=90)],
          anim_in=tanim("zoom-out", duration=0.8), name="Edad")
    label(t, t.track("text", "Nombre"), "Isabella", 1.4, 8.6, Box(160, 590, 1600, 220), "Great Vibes", 180, "#FFFFFF",
          weight=400, layers=[glow("#F9A8D4", 20, 0.7), fill("#FFFFFF")], anim_in=tanim("blur-in", duration=1.0),
          name="Nombre")
    label(t, t.track("text", "Fecha"), "22 · 11 · 2026", 2.2, 7.8, Box(560, 820, 800, 80), "Cinzel", 50, "#F5D98B",
          weight=500, spacing=10, anim_in=tanim("fade", duration=0.6), name="Fecha")
    t.adjust([effect("bling_sparkle", intensity=0.6, threshold=0.7, density=0.35)], name="Destellos")
    song(t, "romantic", 2, 0.75)
    return t


def cele_reunion():
    t = wide("h-cele-reunion", "Reunión familiar", "Family reunion", "celebration", 9.0, order=2304,
             tags=["reunión familiar", "familia", "invitación", "encuentro", "almuerzo"], thumb_at=4.6,
             background="#FFF7EC")
    bg(t, "#FFF7EC")
    spots = [("h-family-05", Box(80, 90, 540, 380), -4), ("h-elderly-02", Box(80, 560, 540, 380), 3),
             ("h-family-04", Box(1300, 90, 540, 380), 4), ("h-kids-04", Box(1300, 560, 540, 380), -3)]
    for i, (s, box, r) in enumerate(spots):
        framed(t, s, 0.2 + i * 0.25, 8.8 - i * 0.25, box, [(0, {"s": 1.3}, "out"), (0.45, {})], border=12,
               rotation=keys([(0, r)]), label=f"Foto {i + 1}")
    label(t, t.track("text", "Título"), "Gran reunión\nfamiliar", 1.0, 8.0, Box(640, 200, 640, 360), "Lobster", 110,
          "#D9480F", weight=400, line=0.95, anim_in=tanim("pop", duration=0.5, unit="word", stagger=0.15), name="Título")
    label(t, t.track("text", "Familia"), "Familia Herrera", 1.6, 7.4, Box(640, 560, 640, 80), "Montserrat", 46, "#7C2D12",
          weight=700, anim_in=tanim("fade", duration=0.5), name="Familia")
    label(t, t.track("text", "Datos"), "domingo 6 de diciembre\n13:00 h · casa de los abuelos", 2.0, 7.0,
          Box(640, 660, 640, 160), "Montserrat", 40, "#292524", weight=500, line=1.25, anim_in=tanim("fade", duration=0.5),
          name="Fecha y lugar")
    song(t, "upbeat", 2, 0.7)
    return t


def cele_logro():
    t = wide("h-cele-logro", "¡Lo logramos!", "We did it!", "celebration", 7.0, order=2305,
             tags=["logro", "meta", "trofeo", "éxito", "celebración", "equipo"], thumb_at=3.4, background="#111111")
    photo_bg(t, "h-office-06", s1=1.08, label="Foto del equipo")
    shade_full(t, 0.55)
    ring(t, t.track("shape", "Onda"), "#FFD23F", 10, 0.6, 1.4, centered(960, 360, 300, 300),
         [(0, {"s": 0.5}, "out"), (1.4, {"s": 3.0})], opacity=keys([(0, 0.9), (1.4, 0.0)]))
    label(t, t.track("text", "Trofeo"), "🏆", 0.3, 6.7, centered(960, 360, 320, 320), "Inter", 230, "#FFD23F", weight=400,
          editable=False, motion=[(0, {"s": 0.0, "dy": 200}, "back"), (0.6, {})])
    label(t, t.track("text", "Título"), "¡LO LOGRAMOS!", 0.8, 6.2, Box(160, 560, 1600, 220), "Anton", 190, "#FFFFFF",
          weight=400, spacing=6, layers=[shadow("#000000", 0, 8, 20, 0.6), fill("#FFFFFF")],
          anim_in=tanim("stamp", duration=0.35), name="Título")
    label(t, t.track("text", "Meta"), "10.000 clientes felices", 1.4, 5.6, Box(360, 790, 1200, 90), "Montserrat", 56,
          "#FFD23F", weight=800, anim_in=tanim("rise", duration=0.4), name="Meta")
    confetti(t, ["#FFD23F", "#FFFFFF", "#FF5A5F", "#3EC1FF"], 0.8, 6.2, seed=305, lanes=4, density=0.25)
    flash(t, 0.6, 0.35, peak=0.6)
    song(t, "epic", 3, 0.8)
    return t


def cele_bienvenida_bebe():
    t = wide("h-cele-bienvenida-bebe", "Bienvenida al bebé", "Welcome baby", "celebration", 9.0, order=2306,
             tags=["nacimiento", "bebé", "bienvenida", "recién nacido", "familia"], thumb_at=4.8, background="#F4F9FF")
    bg_gradient(t, [(0, "#F4F9FF"), (1, "#FFF4F8")], angle=120)
    t.photo(t.track("video", "Foto"), "h-baby-03", 0.2, 8.8, Box(120, 120, 840, 840),
            [(0, {"s": 0.85}, "out"), (0.6, {}, "linear"), (8.8, {"s": 1.03})], label="Foto del bebé",
            opacity=keys([(0, 0.0), (0.5, 1.0)]))
    t.mask(t.tracks[-1], t.tracks[-1].clips[0], "ellipse", feather=0)
    label(t, t.track("text", "Hola"), "¡Hola, mundo!", 0.8, 8.2, Box(1020, 140, 820, 160), "Pacifico", 96, "#7FB3D5",
          weight=400, anim_in=tanim("pop", duration=0.45), name="Saludo")
    label(t, t.track("text", "Nombre"), "Emma", 1.2, 7.8, Box(1020, 300, 820, 220), "Playfair Display", 180, "#3D5A80",
          weight=700, anim_in=tanim("blur-in", duration=0.8), name="Nombre")
    for i, (k, v) in enumerate([("NACIÓ", "4 de octubre, 2026"), ("PESO", "3,2 kg"), ("MEDIDA", "50 cm")]):
        at = 1.8 + i * 0.3
        y = 560 + i * 120
        label(t, t.track("text", "Dato"), k, at, 9.0 - at, Box(1030, y, 300, 60), "Montserrat", 32, "#E07A9B", weight=800,
              spacing=6, align="left", anim_in=tanim("fade", duration=0.3), name=f"Etiqueta {i + 1}")
        label(t, t.track("text", "Dato"), v, at + 0.1, 8.9 - at, Box(1030, y + 50, 800, 60), "Montserrat", 46, "#3D5A80",
              weight=600, align="left", anim_in=tanim("fade", duration=0.3), name=f"Dato {i + 1}")
    dots(t, ["#BDE0FE", "#F9C6D9", "#FFFFFF"], 18, 0.3, 8.7, seed=306, size=(16, 36), kinds=("star", "heart"), drift=70)
    song(t, "fun", 4, 0.7)
    return t


def cele_despedida():
    t = wide("h-cele-despedida", "Despedida", "Farewell", "celebration", 9.0, order=2307,
             tags=["despedida", "buen viaje", "adiós", "amigos", "te extrañaremos"], thumb_at=6.8)
    slides(t, ["h-summer-03", "h-birthday-02", "h-travel-05"], 0.0, 2.6, transition="crossfade", tdur=0.6, kb_amount=0.08)
    shade_full(t, 0.45, 5.6, 3.4)
    label(t, t.track("text", "Título"), "¡Buen viaje, Marco!", 5.8, 3.2, Box(160, 340, 1600, 220), "Kaushan Script", 150,
          "#FFFFFF", weight=400, layers=[shadow("#000000", 0, 6, 18, 0.6), fill("#FFFFFF")],
          anim_in=tanim("wipe", duration=0.8, angle=0), name="Título")
    label(t, t.track("text", "Mensaje"), "te vamos a extrañar · vuelve pronto", 6.4, 2.6, Box(360, 580, 1200, 90),
          "Montserrat", 52, "#FFFFFF", weight=600, anim_in=tanim("fade", duration=0.6), name="Mensaje")
    label(t, t.track("text", "Avión"), "✈", 6.0, 3.0, centered(960, 790, 140, 140), "Inter", 100, "#FFFFFF", weight=700,
          editable=False, motion=[(0, {"dx": -1100, "dy": 80}, "out"), (1.2, {}, "linear"), (3.0, {"dx": 1100, "dy": -120})])
    song(t, "upbeat", 3, 0.75)
    return t


def cele_premios():
    t = wide("h-cele-premios", "Entrega de premios", "Awards", "celebration", 8.0, order=2308,
             tags=["premios", "ganador", "reconocimiento", "gala", "trofeo"], thumb_at=5.2, background="#08060A")
    bg_gradient(t, [(0, "#1A1208"), (1, "#050405")], angle=90)
    for i, (x, ang) in enumerate([(400, 20), (1520, -20)]):
        t.solid(t.track("shape", "Foco"), "#F5D98B", 0, 8.0, Box(x - 220, -200, 440, 1400),
                [(0, {}, "smooth"), (4.0, {"dx": -120 if i else 120}, "smooth"), (8.0, {})], kind="triangle",
                layers=[gradient([(0, "#F5D98B", 0.35), (1, "#F5D98B", 0.0)], angle=90), no_stroke()],
                rotation=keys([(0, ang)]))
    circle_photo(t, "h-man-03", 1.2, 6.8, centered(960, 430, 380, 380), pop(0, 0.6), ring_colour="#D4AF37", ring_width=12,
                 label="Foto del ganador")
    label(t, t.track("text", "Categoría"), "MEJOR EMPLEADO DEL AÑO", 0.4, 7.6, Box(360, 90, 1200, 80), "Cinzel", 52,
          "#D4AF37", weight=600, spacing=8, anim_in=tanim("fade", duration=0.6), name="Categoría")
    label(t, t.track("text", "Ganador"), "Andrés Villa", 2.0, 6.0, Box(160, 680, 1600, 180), "Playfair Display", 140,
          "#FFFFFF", weight=700, layers=[glow("#F5D98B", 18, 0.5), fill("#FFFFFF")], anim_in=tanim("blur-in", duration=0.8),
          name="Ganador")
    t.adjust([effect("bling_sparkle", intensity=0.7, threshold=0.65, density=0.4)], name="Destellos")
    confetti(t, ["#D4AF37", "#F5D98B", "#FFFFFF"], 2.0, 6.0, seed=308, lanes=3, density=0.3)
    song(t, "epic", 0, 0.75)
    return t


def cele_fiesta_invitacion():
    t = wide("h-cele-fiesta-invitacion", "Invitación a fiesta", "Party invitation", "celebration", 8.0, order=2309,
             tags=["fiesta", "invitación", "party", "evento", "noche"], thumb_at=4.4, background="#120326")
    bg_gradient(t, [(0, "#2D0B59"), (1, "#0F0320")], angle=135)
    for i, c in enumerate(["#FF2EF7", "#08F7FE", "#FFE600"]):
        t.solid(t.track("shape", "Luz"), c, 0, 8.0, centered(300 + i * 660, 300 + (i % 2) * 500, 700, 700),
                [(0, {}, "smooth"), (4.0, {"dx": 140, "dy": -80}, "smooth"), (8.0, {})], kind="ellipse",
                layers=[gradient([(0, c, 0.35), (1, c, 0.0)], angle=0), no_stroke()])
    label(t, t.track("text", "Título"), "PARTY", 0.3, 7.7, Box(160, 140, 1600, 380), "Monoton", 330, "#FFFFFF", weight=400,
          layers=[glow("#FF2EF7", 30, 0.9), fill("#FFFFFF")], anim_in=tanim("flicker-in", duration=0.8),
          anim_loop=tanim("flicker", intensity=0.15, speed=4), name="Título")
    label(t, t.track("text", "Motivo"), "fin de exámenes", 1.0, 7.0, Box(160, 520, 1600, 120), "Righteous", 84, "#08F7FE",
          weight=400, anim_in=tanim("slide-up", duration=0.4), name="Motivo")
    _info_rows(t, [("📅", "viernes 27 · 22:00 h"), ("📍", "Terraza Azul, calle 9"), ("🎟", "entrada libre con invitación")],
               520, 680, 100, 1.6, font="Righteous", size=44, icon_bg="#FF2EF7", icon_colour="#FFFFFF", width=900)
    t.adjust([effect("bloom_glow", threshold=0.6, intensity=0.8)], name="Brillo")
    song(t, "electro", 1, 0.8)
    return t


# --- International dates ------------------------------------------------------------------------

def fecha_navidad():
    t = wide("h-fecha-navidad", "Feliz Navidad", "Merry Christmas", "seasonal", 9.0, order=2310,
             tags=["navidad", "christmas", "nieve", "familia", "diciembre"], thumb_at=4.6)
    photo_bg(t, "h-christmas-03", s1=1.08, label="Foto familiar")
    shade_full(t, 0.4, colour="#0B1A12")
    rng = random.Random(310)
    for lane in range(4):
        tr = t.track("shape", "Nieve")
        at = lane * 0.3
        while at < 8.5:
            s = rng.uniform(8, 22)
            fall = rng.uniform(4.0, 7.0)
            d = min(fall, 9.0 - at)
            t.solid(tr, "#FFFFFF", at, d, centered(rng.uniform(0, 1920), -30, s, s),
                    [(0, {}, "linear"), (fall, {"dy": 1150, "dx": rng.uniform(-90, 90)})], kind="ellipse", alpha=0.85)
            at += rng.uniform(0.15, 0.35)
    for k in range(14):  # a string of lights along the top
        c = ["#FF4D4D", "#FFD23F", "#4CC9F0", "#7BF06A"][k % 4]
        if k % 7 == 0:
            lights = t.track("shape", "Luces")
        t.solid(lights, c, 0, 9.0, centered(80 + k * 136, 70 + math.sin(k / 13 * math.pi) * 60, 26, 34), kind="ellipse",
                layers=[glow(c, 18, 0.9), fill(c), no_stroke()], opacity=blink(9.0, 0.8 + (k % 3) * 0.2, 0.4))
    label(t, t.track("text", "Título"), "Feliz Navidad", 0.6, 8.4, Box(160, 320, 1600, 260), "Great Vibes", 220, "#FFFFFF",
          weight=400, layers=[glow("#FFD23F", 20, 0.6), fill("#FFFFFF")], anim_in=tanim("blur-in", duration=1.2),
          name="Título")
    label(t, t.track("text", "Familia"), "les desea la familia Ortiz", 1.6, 7.4, Box(360, 620, 1200, 90), "Montserrat", 52,
          "#FFFFFF", weight=500, spacing=2, anim_in=tanim("fade", duration=0.6), name="De parte de")
    song(t, "classic", 2, 0.75)
    return t


def fecha_anio_nuevo():
    t = wide("h-fecha-anio-nuevo", "Feliz Año Nuevo", "Happy New Year", "seasonal", 8.0, order=2311,
             tags=["año nuevo", "new year", "fuegos artificiales", "brindis", "enero"], thumb_at=4.0, background="#050814")
    photo_bg(t, "h-newyear-02", s1=1.08, label="Foto de fondo")
    shade_full(t, 0.35, colour="#050814")
    rng = random.Random(311)
    for b in range(6):
        cx, cy = rng.uniform(250, 1670), rng.uniform(150, 450)
        c = rng.choice(["#FFD23F", "#FF5A5F", "#3EC1FF", "#FFFFFF", "#B26BFF"])
        tr = t.track("shape", "Fuego")
        at = 0.4 + b * 1.1
        for k in range(16):
            a = k / 16 * math.tau
            t.solid(tr, c, at, 1.6, centered(cx, cy, 14, 14),
                    [(0, {}, "out"), (1.0, {"dx": math.cos(a) * 240, "dy": math.sin(a) * 240 + 50}, "linear"),
                     (1.6, {"dx": math.cos(a) * 270, "dy": math.sin(a) * 270 + 150})], kind="ellipse",
                    layers=[glow(c, 14, 0.9), fill(c), no_stroke()], opacity=keys([(0, 1.0), (1.6, 0.0)]))
    label(t, t.track("text", "Año"), "2027", 0.5, 7.5, Box(160, 260, 1600, 420), "Playfair Display", 380, "#F5D98B",
          weight=800, layers=[glow("#F5D98B", 30, 0.6), gradient([(0, "#FFF4D6"), (0.5, "#E8C27A"), (1, "#B8892E")], angle=90)],
          anim_in=tanim("zoom-out", duration=0.8), name="Año")
    label(t, t.track("text", "Saludo"), "¡Feliz Año Nuevo!", 1.2, 6.8, Box(160, 700, 1600, 160), "Great Vibes", 130,
          "#FFFFFF", weight=400, anim_in=tanim("blur-in", duration=0.8), name="Saludo")
    song(t, "upbeat", 0, 0.8)
    return t


def fecha_san_valentin():
    t = wide("h-fecha-san-valentin", "San Valentín", "Valentine's Day", "seasonal", 9.0, order=2312,
             tags=["san valentín", "amor", "14 de febrero", "pareja", "corazones"], thumb_at=4.6, background="#FFE3EA")
    bg_gradient(t, [(0, "#FFD6E0"), (1, "#FFB3C6")], angle=135)
    dots(t, ["#FF4D6D", "#FF8FA3", "#FFFFFF"], 30, 0, 9.0, seed=312, size=(30, 70), kinds=("heart",), drift=200, alpha=0.8)
    t.photo(t.track("video", "Foto"), "h-couple-05", 0.4, 8.6, centered(1340, 540, 760, 760),
            [(0, {"s": 0.5}, "back"), (0.6, {}, "linear"), (8.6, {"s": 1.04})], label="Foto de la pareja")
    t.mask(t.tracks[-1], t.tracks[-1].clips[0], "heart")
    label(t, t.track("text", "Título"), "Te quiero", 0.8, 8.2, Box(120, 300, 900, 240), "Pacifico", 170, "#C9184A",
          weight=400, layers=[shadow("#FFFFFF", 0, 8, 0, 1.0), fill("#C9184A")], anim_in=tanim("pop", duration=0.5),
          name="Título")
    label(t, t.track("text", "Mensaje"), "feliz San Valentín, mi amor", 1.4, 7.6, Box(120, 560, 900, 100), "Dancing Script",
          74, "#590D22", weight=700, anim_in=tanim("fade", duration=0.6), name="Mensaje")
    song(t, "romantic", 1, 0.75)
    return t


def fecha_dia_madre():
    t = wide("h-fecha-dia-madre", "Día de la Madre", "Mother's Day", "seasonal", 9.0, order=2313,
             tags=["día de la madre", "mamá", "flores", "amor", "familia"], thumb_at=4.6, background="#FFF5F7")
    bg(t, "#FFF5F7")
    for i, (x, y, s, c) in enumerate([(160, 160, 260, "#F8C8DC"), (1780, 900, 320, "#F4A7B9"), (1760, 150, 180, "#FADADD"),
                                      (200, 940, 200, "#E8B4C8")]):
        for p in range(6):  # a flower: petals around a centre
            a = p / 6 * math.tau
            t.solid(t.track("shape", "Flor"), c, 0.2 + i * 0.2, 8.8 - i * 0.2,
                    centered(x + math.cos(a) * s * 0.28, y + math.sin(a) * s * 0.28, s * 0.42, s * 0.42),
                    pop(0, 0.5), kind="ellipse", alpha=0.9)
        t.solid(t.track("shape", "Flor"), "#FFD166", 0.3 + i * 0.2, 8.7 - i * 0.2, centered(x, y, s * 0.3, s * 0.3),
                pop(0, 0.5), kind="ellipse")
    framed(t, "h-mother-02", 0.6, 8.4, Box(1040, 200, 620, 680), [(0, {"s": 0.8}, "back"), (0.5, {}, "linear"),
                                                                  (8.4, {"s": 1.03})], border=16, radius=24,
           rotation=keys([(0, 3)]), label="Foto con mamá")
    label(t, t.track("text", "Título"), "Feliz día,\nmamá", 0.9, 8.1, Box(260, 260, 760, 380), "Dancing Script", 150,
          "#9C2C5C", weight=700, line=0.95, anim_in=tanim("typewriter", duration=1.2, unit="character"), name="Título")
    label(t, t.track("text", "Mensaje"), "gracias por todo tu amor", 2.0, 7.0, Box(260, 680, 760, 90), "Cormorant Garamond",
          60, "#5C2340", weight=600, italic=True, anim_in=tanim("fade", duration=0.6), name="Mensaje")
    song(t, "romantic", 3, 0.7)
    return t


def fecha_dia_padre():
    t = wide("h-fecha-dia-padre", "Día del Padre", "Father's Day", "seasonal", 8.0, order=2314,
             tags=["día del padre", "papá", "familia", "héroe", "junio"], thumb_at=4.4, background="#0F1C2E")
    photo_bg(t, "h-father-01", s1=1.08, label="Foto con papá")
    t.solid(t.track("shape", "Panel"), "#0F1C2E", 0, 8.0, Box(0, 0, 820, 1080),
            layers=[gradient([(0, "#0F1C2E", 0.95), (1, "#0F1C2E", 0.0)], angle=0), no_stroke()])
    label(t, t.track("text", "Feliz"), "FELIZ DÍA", 0.4, 7.6, Box(120, 280, 800, 120), "Oswald", 96, "#F2AA4C", weight=700,
          spacing=12, align="left", anim_in=tanim("slide-right", duration=0.4), name="Antetítulo")
    label(t, t.track("text", "Papá"), "PAPÁ", 0.7, 7.3, Box(110, 380, 800, 300), "Anton", 300, "#FFFFFF", weight=400,
          align="left", spacing=10, anim_in=tanim("slide-up", duration=0.5), name="Título")
    label(t, t.track("text", "Mensaje"), "mi primer héroe, siempre", 1.4, 6.6, Box(120, 700, 800, 80), "Montserrat", 48,
          "#DDE6F0", weight=500, align="left", anim_in=tanim("fade", duration=0.5), name="Mensaje")
    line(t, t.track("shape", "Línea"), "#F2AA4C", 1.0, 7.0, Box(124, 680, 200, 8), length=0.5)
    song(t, "epic", 2, 0.7)
    return t


def fecha_halloween():
    t = wide("h-fecha-halloween", "Halloween", "Halloween", "seasonal", 8.0, order=2315,
             tags=["halloween", "terror", "calabazas", "disfraces", "octubre"], thumb_at=4.0, background="#0B0710")
    photo_bg(t, "h-halloween-03", s1=1.08, label="Foto de fondo")
    shade_full(t, 0.5, colour="#0B0710")
    t.solid(t.track("shape", "Luna"), "#FFF1C1", 0, 8.0, centered(1600, 220, 260, 260), kind="ellipse",
            layers=[glow("#FFE8A0", 50, 0.8), fill("#FFF1C1"), no_stroke()])
    rng = random.Random(315)
    for k in range(6):
        label(t, t.track("text", "Murciélago"), "🦇", rng.uniform(0, 2), 6.0, centered(-100, rng.uniform(150, 500), 120, 120),
              "Inter", rng.choice([60, 80, 100]), "#000000", weight=400, editable=False,
              motion=[(0, {}, "linear"), (6.0, {"dx": 2200, "dy": rng.uniform(-150, 150)})],
              anim_loop=tanim("jitter", amount=3, angle=6, speed=6))
    label(t, t.track("text", "Título"), "Feliz Halloween", 0.6, 7.4, Box(160, 340, 1600, 260), "Creepster", 200, "#FF7518",
          weight=400, layers=[glow("#FF7518", 24, 0.8), shadow("#000000", 0, 8, 0, 1.0), fill("#FF7518")],
          anim_in=tanim("flicker-in", duration=0.8), anim_loop=tanim("jitter", amount=1, angle=1, speed=8), name="Título")
    label(t, t.track("text", "Sub"), "¿truco o trato?", 1.4, 6.6, Box(360, 640, 1200, 110), "Creepster", 84, "#B6F35B",
          weight=400, anim_in=tanim("fade", duration=0.6), name="Subtítulo")
    vignette(t, 0.8)
    song(t, "suspense", 3, 0.75)
    return t


def fecha_pascua():
    t = wide("h-fecha-pascua", "Pascua", "Easter", "seasonal", 8.0, order=2316,
             tags=["pascua", "easter", "huevos", "primavera", "conejo"], thumb_at=4.2, background="#F3FBEF")
    bg_gradient(t, [(0, "#F3FBEF"), (1, "#FFF5E1")], angle=90)
    eggs = [("#F9C6D9", 220), ("#BDE0FE", 440), ("#FFF1B5", 660), ("#CDEAC0", 1260), ("#E2C2FF", 1480), ("#FFD6A5", 1700)]
    for i, (c, x) in enumerate(eggs):
        t.solid(t.track("shape", "Huevo"), c, 0.2 + i * 0.15, 7.8 - i * 0.15, centered(x, 900, 150, 190),
                [(0, {"dy": 400}, "back"), (0.5, {}, "smooth"), (4.0, {"dy": -10}, "smooth"), (7.8 - i * 0.15, {})],
                kind="ellipse", layers=[shadow("#000000", 0, 8, 16, 0.15), fill(c), no_stroke()],
                rotation=keys([(0, (-1) ** i * 8)]))
        t.solid(t.track("shape", "Franja"), "#FFFFFF", 0.2 + i * 0.15, 7.8 - i * 0.15, centered(x, 900, 150, 18),
                [(0, {"dy": 400}, "back"), (0.5, {}, "smooth"), (4.0, {"dy": -10}, "smooth"), (7.8 - i * 0.15, {})],
                alpha=0.8, rotation=keys([(0, (-1) ** i * 8)]))
    framed(t, "h-easter-03", 0.6, 7.4, Box(660, 160, 600, 450), pop(0, 0.5, 0.6), border=14, radius=24,
           label="Foto")
    label(t, t.track("text", "Título"), "¡Felices Pascuas!", 1.0, 7.0, Box(160, 630, 1600, 180), "Fredoka", 130, "#6A994E",
          weight=700, anim_in=tanim("bounce", duration=0.5, unit="character", stagger=0.03), name="Título")
    song(t, "fun", 4, 0.7)
    return t


def fecha_anio_nuevo_lunar():
    t = wide("h-fecha-anio-nuevo-lunar", "Año Nuevo Lunar", "Lunar New Year", "seasonal", 8.0, order=2317,
             tags=["año nuevo lunar", "año nuevo chino", "faroles", "rojo", "dorado"], thumb_at=4.0, background="#7A0A0A")
    photo_bg(t, "h-lunar-01", s1=1.06, label="Foto de fondo")
    shade_full(t, 0.45, colour="#4A0505")
    for i, x in enumerate((240, 1680)):
        t.solid(t.track("shape", "Cordón"), "#D4AF37", 0, 8.0, Box(x - 2, 0, 4, 200))
        t.solid(t.track("shape", "Farol"), "#E10600", 0, 8.0, centered(x, 300, 220, 240),
                [(0, {}, "smooth"), (2.0, {"dx": 10}, "smooth"), (4.0, {"dx": -10}, "smooth"), (8.0, {})], kind="ellipse",
                layers=[glow("#FF6A3D", 40, 0.9), gradient([(0, "#FF4D2E"), (1, "#B00000")], angle=90), no_stroke()])
        for y in (205, 395):
            t.solid(t.track("shape", "Farol"), "#D4AF37", 0, 8.0, centered(x, y, 120, 24), radius=6, kind="rounded-rectangle")
    rrect(t, t.track("shape", "Placa"), "#B00000", 0.4, 7.6, centered(960, 520, 1000, 440), 30, pop(0, 0.5, 0.8),
          layers=[shadow("#000000", 0, 14, 30, 0.45), fill("#B00000", 0.9), stroke(6, "#D4AF37")])
    label(t, t.track("text", "Título"), "Feliz\nAño Nuevo Lunar", 0.8, 7.2, centered(960, 480, 940, 320), "Playfair Display",
          104, "#F5D98B", weight=800, line=1.0, layers=[glow("#F5D98B", 14, 0.5), fill("#F5D98B")],
          anim_in=tanim("rise-by-word", duration=0.5, unit="word", stagger=0.15), name="Título")
    label(t, t.track("text", "Deseo"), "prosperidad y salud para tu familia", 1.6, 6.4, centered(960, 680, 940, 80),
          "Montserrat", 40, "#FFFFFF", weight=500, anim_in=tanim("fade", duration=0.6), name="Deseo")
    song(t, "world", 3, 0.7)
    return t


def fecha_ramadan():
    t = wide("h-fecha-ramadan", "Ramadán Kareem", "Ramadan Kareem", "seasonal", 8.0, order=2318,
             tags=["ramadán", "ramadan kareem", "media luna", "faroles", "iftar"], thumb_at=4.2, background="#0B1530")
    bg_gradient(t, [(0, "#14234F"), (1, "#060B1C")], angle=90)
    dots(t, ["#FFFFFF", "#F5D98B"], 40, 0, 8.0, seed=318, size=(4, 10), kinds=("star", "ellipse"), drift=10)
    moon = t.track("shape", "Luna")
    t.solid(moon, "#F5D98B", 0.3, 7.7, centered(960, 300, 300, 300), pop(0, 0.6), kind="ellipse",
            layers=[glow("#F5D98B", 40, 0.7), fill("#F5D98B"), no_stroke()])
    t.solid(t.track("shape", "Luna"), "#101C40", 0.3, 7.7, centered(1040, 260, 280, 280), pop(0, 0.6), kind="ellipse")
    t.photo(t.track("video", "Farol"), "h-ramadan-02", 0.6, 7.4, Box(1380, 380, 420, 560),
            [(0, {"dy": 100}, "out"), (0.8, {})], label="Foto", opacity=keys([(0, 0.0), (0.6, 1.0)]))
    t.mask(t.tracks[-1], t.tracks[-1].clips[0], "ellipse", feather=60)
    label(t, t.track("text", "Título"), "Ramadán Kareem", 1.0, 7.0, Box(160, 520, 1300, 200), "Marcellus", 140, "#F5D98B",
          weight=400, layers=[glow("#F5D98B", 18, 0.5), fill("#F5D98B")], anim_in=tanim("blur-in", duration=1.0),
          name="Título")
    label(t, t.track("text", "Deseo"), "que este mes llene tu hogar de paz", 1.8, 6.2, Box(160, 730, 1300, 80), "Montserrat",
          46, "#DDE3F5", weight=500, anim_in=tanim("fade", duration=0.6), name="Deseo")
    song(t, "world", 2, 0.65)
    return t


def fecha_eid():
    t = wide("h-fecha-eid", "Eid Mubarak", "Eid Mubarak", "seasonal", 8.0, order=2319,
             tags=["eid", "eid mubarak", "fiesta", "familia", "celebración"], thumb_at=4.0, background="#0E3B36")
    bg_gradient(t, [(0, "#14544C"), (1, "#082521")], angle=120)
    for i, x in enumerate((260, 560, 1360, 1660)):
        h = 260 + (i % 2) * 120
        t.solid(t.track("shape", "Cordón"), "#D4AF37", 0, 8.0, Box(x - 2, 0, 4, h - 60))
        t.solid(t.track("shape", "Estrella"), "#F5D98B", 0.2 + i * 0.15, 7.8 - i * 0.15, centered(x, h, 90, 90),
                [(0, {"dy": -300}, "back"), (0.6, {}, "smooth"), (4.0, {"dy": 8}, "smooth"), (7.8 - i * 0.15, {})],
                kind="star", layers=[glow("#F5D98B", 18, 0.8), fill("#F5D98B"), no_stroke()])
    label(t, t.track("text", "Título"), "Eid Mubarak", 0.6, 7.4, Box(160, 360, 1600, 260), "Cinzel Decorative", 170,
          "#F5D98B", weight=700, layers=[glow("#F5D98B", 22, 0.6), fill("#F5D98B")], anim_in=tanim("blur-in", duration=1.0),
          name="Título")
    label(t, t.track("text", "Deseo"), "felicidad y bendiciones para ti y los tuyos", 1.4, 6.6, Box(260, 640, 1400, 90),
          "Montserrat", 48, "#E6F2EF", weight=500, anim_in=tanim("fade", duration=0.6), name="Deseo")
    t.adjust([effect("bling_sparkle", intensity=0.5, threshold=0.7, density=0.3)], name="Destellos")
    song(t, "world", 0, 0.65)
    return t


def fecha_diwali():
    t = wide("h-fecha-diwali", "Feliz Diwali", "Happy Diwali", "seasonal", 8.0, order=2320,
             tags=["diwali", "festival de las luces", "lámparas", "diya", "celebración"], thumb_at=4.0, background="#1A0B05")
    photo_bg(t, "h-diwali-01", s1=1.06, label="Foto de fondo")
    shade_full(t, 0.4, colour="#1A0B05")
    dots(t, ["#FFB703", "#FB8500", "#FFE8A0"], 34, 0, 8.0, seed=320, size=(6, 16), kinds=("ellipse", "star"), drift=120)
    label(t, t.track("text", "Título"), "Feliz Diwali", 0.6, 7.4, Box(160, 330, 1600, 260), "Yeseva One", 180, "#FFD166",
          weight=400, layers=[glow("#FB8500", 26, 0.8), fill("#FFD166")], anim_in=tanim("blur-in", duration=1.0),
          name="Título")
    label(t, t.track("text", "Deseo"), "que la luz llene tu casa de alegría", 1.4, 6.6, Box(260, 620, 1400, 90), "Montserrat",
          50, "#FFF1D6", weight=500, anim_in=tanim("fade", duration=0.6), name="Deseo")
    t.adjust([effect("bloom_glow", threshold=0.55, intensity=0.9, blurRadius=16)], name="Brillo")
    song(t, "world", 1, 0.7)
    return t


def fecha_accion_gracias():
    t = wide("h-fecha-accion-gracias", "Acción de Gracias", "Thanksgiving", "seasonal", 8.0, order=2321,
             tags=["acción de gracias", "thanksgiving", "otoño", "familia", "gratitud"], thumb_at=4.4, background="#3A1F0F")
    photo_bg(t, "h-thanksgiving-02", s1=1.06, label="Foto de la mesa")
    shade_bottom(t, 600, 0.85, colour="#2B1408")
    rng = random.Random(321)
    for k in range(18):
        c = rng.choice(["#D9480F", "#F08C00", "#A61E4D", "#C2A000"])
        s = rng.uniform(40, 80)
        at = rng.uniform(0, 4)
        t.solid(t.track("shape", "Hoja"), c, at, min(4.0, 8.0 - at), centered(rng.uniform(0, 1920), -60, s, s * 0.7),
                [(0, {}, "linear"), (4.0, {"dy": 1200, "dx": rng.uniform(-200, 200)})], kind="diamond",
                rotation=keys([(0, rng.uniform(0, 90)), (4.0, rng.uniform(-300, 300))]), alpha=0.9)
    label(t, t.track("text", "Título"), "Gracias", 0.6, 7.4, Box(120, 620, 1300, 240), "Lobster", 200, "#FFD8A8",
          weight=400, align="left", anim_in=tanim("fade-up-char", duration=0.5, unit="character", stagger=0.05),
          name="Título")
    label(t, t.track("text", "Mensaje"), "por la mesa, la familia y los amigos", 1.4, 6.6, Box(130, 860, 1400, 80),
          "Montserrat", 46, "#FFFFFF", weight=500, align="left", anim_in=tanim("fade", duration=0.6), name="Mensaje")
    song(t, "calm", 3, 0.7)
    return t


def fecha_regreso_clases():
    t = wide("h-fecha-regreso-clases", "Regreso a clases", "Back to school", "seasonal", 8.0, order=2322,
             tags=["regreso a clases", "escuela", "útiles", "estudiantes", "colegio"], thumb_at=4.2, background="#FFF8E6")
    bg(t, "#FFF8E6")
    for k in range(13):
        t.solid(t.track("shape", "Cuadrícula"), "#D6E4F0", 0, 8.0, Box(k * 160, 0, 2, 1080))
    for k in range(7):
        t.solid(t.track("shape", "Cuadrícula"), "#D6E4F0", 0, 8.0, Box(0, k * 160, 1920, 2))
    items = [("✏️", 260, 220, -20), ("📚", 1650, 260, 10), ("🎒", 300, 820, 8), ("📐", 1640, 820, -12), ("🖍", 960, 940, 0)]
    for i, (g, x, y, r) in enumerate(items):
        label(t, t.track("text", "Útil"), g, 0.3 + i * 0.2, 7.7 - i * 0.2, centered(x, y, 260, 260), "Inter", 170, "#000000",
              weight=400, editable=False, motion=[(0, {"s": 0.0}, "back"), (0.5, {})], rotation=keys([(0, r)]),
              anim_loop=tanim("float", amount=0.06, speed=0.5))
    label(t, t.track("text", "Título"), "¡Regreso a clases!", 0.8, 7.2, Box(160, 330, 1600, 220), "Luckiest Guy", 160,
          "#F94144", weight=400, layers=[shadow("#277DA1", 0, 10, 0, 1.0), fill("#F94144")],
          anim_in=tanim("bounce", duration=0.5, unit="character", stagger=0.03), name="Título")
    label(t, t.track("text", "Sub"), "listos para un año increíble", 1.6, 6.4, Box(360, 580, 1200, 90), "Patrick Hand", 70,
          "#277DA1", weight=400, anim_in=tanim("fade", duration=0.5), name="Subtítulo")
    song(t, "fun", 2, 0.7)
    return t


def fecha_dia_mujer():
    t = wide("h-fecha-dia-mujer", "Día de la Mujer", "Women's Day", "seasonal", 8.0, order=2323,
             tags=["día de la mujer", "8 de marzo", "mujeres", "igualdad", "inspiración"], thumb_at=4.2,
             background="#5B2A86")
    bg_gradient(t, [(0, "#7B2CBF"), (1, "#3C096C")], angle=135)
    samples = ["h-portrait-03", "h-portrait-05", "h-portrait-01"]
    for i, s in enumerate(samples):
        circle_photo(t, s, 0.3 + i * 0.3, 7.7 - i * 0.3, centered(1120 + i * 280, 300 + (i % 2) * 480, 360, 360),
                     pop(0, 0.5), ring_colour="#E0AAFF", ring_width=10, label=f"Foto {i + 1}")
    label(t, t.track("text", "Fecha"), "8 DE MARZO", 0.6, 7.4, Box(120, 250, 900, 90), "Montserrat", 56, "#E0AAFF",
          weight=800, spacing=12, align="left", anim_in=tanim("fade", duration=0.5), name="Fecha")
    label(t, t.track("text", "Título"), "Día de la\nMujer", 0.9, 7.1, Box(110, 340, 900, 420), "Playfair Display", 160,
          "#FFFFFF", weight=800, line=0.95, align="left", anim_in=tanim("rise-by-word", duration=0.5, unit="word",
          stagger=0.15), name="Título")
    label(t, t.track("text", "Frase"), "fuertes, libres y capaces de todo", 1.8, 6.2, Box(120, 790, 900, 80), "Montserrat",
          44, "#F3D9FF", weight=500, align="left", anim_in=tanim("fade", duration=0.6), name="Frase")
    song(t, "epic", 2, 0.7)
    return t


def fecha_dia_maestro():
    t = wide("h-fecha-dia-maestro", "Día del Maestro", "Teachers' Day", "seasonal", 8.0, order=2324,
             tags=["día del maestro", "profesor", "docente", "gracias", "escuela"], thumb_at=4.4, background="#1F3B2D")
    bg_gradient(t, [(0, "#2A4A39"), (1, "#16291F")], angle=120)
    outline(t, t.track("shape", "Marco"), "#8B5A2B", 30, 0, 8.0, t.full)
    label(t, t.track("text", "Título"), "¡Feliz Día del Maestro!", 0.4, 7.6, Box(160, 220, 1600, 200), "Gloria Hallelujah",
          120, "#F2F2EA", weight=400, layers=[fill("#F2F2EA", 0.92)],
          anim_in=tanim("typewriter", duration=1.4, unit="character"), name="Título")
    label(t, t.track("text", "Mensaje"), "Gracias por enseñarnos con paciencia y cariño", 2.0, 6.0, Box(260, 460, 1400, 200),
          "Patrick Hand", 72, "#FFE08A", weight=400, line=1.15, anim_in=tanim("fade", duration=0.6), name="Mensaje")
    label(t, t.track("text", "Manzana"), "🍎", 1.6, 6.4, centered(960, 800, 220, 220), "Inter", 160, "#E63946", weight=400,
          editable=False, motion=pop(0, 0.5))
    label(t, t.track("text", "Firma"), "— tus alumnos de 5.º A", 2.6, 5.4, Box(1100, 860, 700, 90), "Gloria Hallelujah", 56,
          "#F2F2EA", weight=400, align="right", anim_in=tanim("fade", duration=0.5), name="Firma")
    grain(t, 0.25, 2.0)
    song(t, "calm", 4, 0.65)
    return t


def fecha_verano():
    t = wide("h-fecha-verano", "Llegó el verano", "Summer is here", "seasonal", 8.0, order=2325,
             tags=["verano", "playa", "sol", "vacaciones", "calor"], thumb_at=4.0)
    photo_bg(t, "h-beach-05", s1=1.08, label="Foto de playa")
    sun = t.track("shape", "Sol")
    t.solid(sun, "#FFD60A", 0.2, 7.8, centered(1620, 240, 260, 260), pop(0, 0.6), kind="ellipse",
            layers=[glow("#FFB703", 50, 0.8), fill("#FFD60A"), no_stroke()])
    for k in range(6):  # rays that turn slowly
        a = k / 6 * 360
        t.solid(t.track("shape", "Rayo"), "#FFD60A", 0.4, 7.6, centered(1620, 240, 16, 420), pop(0, 0.5),
                rotation=keys([(0, a, "linear"), (7.6, a + 60)]), alpha=0.5)
    label(t, t.track("text", "Título"), "¡LLEGÓ EL VERANO!", 0.6, 7.4, Box(120, 360, 1500, 260), "Luckiest Guy", 170,
          "#FFFFFF", weight=400, layers=[shadow("#0077B6", 0, 12, 0, 1.0), stroke(8, "#0077B6"), fill("#FFFFFF")],
          anim_in=tanim("bounce", duration=0.5, unit="word", stagger=0.15), rotation=keys([(0, -4)]), name="Título")
    label(t, t.track("text", "Sub"), "sol, mar y buenos amigos", 1.4, 6.6, Box(160, 640, 1300, 100), "Pacifico", 76,
          "#FFFFFF", weight=400, layers=[shadow("#000000", 0, 4, 12, 0.5), fill("#FFFFFF")],
          anim_in=tanim("fade", duration=0.6), rotation=keys([(0, -4)]), name="Subtítulo")
    song(t, "upbeat", 0, 0.8)
    return t


def fecha_otono():
    t = wide("h-fecha-otono", "Hola otoño", "Hello autumn", "seasonal", 8.0, order=2326,
             tags=["otoño", "hojas", "acogedor", "estación", "café"], thumb_at=4.2, background="#5A3418")
    photo_bg(t, "h-autumn-02", s1=1.08, label="Foto de otoño")
    shade_full(t, 0.3, colour="#3A1F0F")
    rng = random.Random(326)
    for lane in range(3):
        tr = t.track("shape", "Hojas")
        at = lane * 0.4
        while at < 7.4:
            c = rng.choice(["#D9480F", "#F08C00", "#A61E4D", "#C2A000"])
            s = rng.uniform(44, 86)
            fall = rng.uniform(3.6, 5.6)
            d = min(fall, 8.0 - at)
            t.solid(tr, c, at, d, centered(rng.uniform(0, 1920), -60, s, s * 0.6),
                    [(0, {}, "linear"), (fall, {"dy": 1200, "dx": rng.uniform(-250, 250)})], kind="diamond",
                    rotation=keys([(0, rng.uniform(0, 90)), (fall, rng.uniform(-360, 360))]))
            at += rng.uniform(0.4, 0.8)
    label(t, t.track("text", "Título"), "Hola, otoño", 0.6, 7.4, Box(160, 360, 1600, 260), "Amatic SC", 240, "#FFF1E0",
          weight=700, layers=[shadow("#3A1F0F", 0, 6, 16, 0.7), fill("#FFF1E0")],
          anim_in=tanim("rise", duration=0.6, unit="character", stagger=0.05), name="Título")
    label(t, t.track("text", "Sub"), "café caliente · suéteres · hojas secas", 1.5, 6.5, Box(360, 640, 1200, 90),
          "Amatic SC", 72, "#FFD8A8", weight=700, anim_in=tanim("fade", duration=0.6), name="Subtítulo")
    song(t, "calm", 1, 0.7)
    return t


def fecha_invierno():
    t = wide("h-fecha-invierno", "Invierno", "Winter", "seasonal", 8.0, order=2327,
             tags=["invierno", "nieve", "frío", "estación", "acogedor"], thumb_at=4.2, background="#DDE7F0")
    photo_bg(t, "h-winter-02", s1=1.06, label="Foto de invierno")
    rng = random.Random(327)
    for lane in range(4):
        tr = t.track("shape", "Nieve")
        at = lane * 0.25
        while at < 7.6:
            s = rng.uniform(8, 26)
            fall = rng.uniform(4.5, 7.5)
            t.solid(tr, "#FFFFFF", at, min(fall, 8.0 - at), centered(rng.uniform(0, 1920), -30, s, s),
                    [(0, {}, "linear"), (fall, {"dy": 1150, "dx": rng.uniform(-60, 60)})], kind="ellipse",
                    layers=[shadow("#6C8EAD", 0, 0, 6, 0.5), fill("#FFFFFF"), no_stroke()])
            at += rng.uniform(0.12, 0.3)
    label(t, t.track("text", "Título"), "Invierno", 0.6, 7.4, Box(160, 330, 1600, 280), "Cormorant Garamond", 240, "#FFFFFF",
          weight=600, spacing=20, layers=[shadow("#3D5A80", 0, 6, 20, 0.6), fill("#FFFFFF")],
          anim_in=tanim("blur-in", duration=1.0, blur=16), name="Título")
    label(t, t.track("text", "Sub"), "el frío se cuenta mejor en compañía", 1.6, 6.4, Box(360, 640, 1200, 90),
          "Cormorant Garamond", 60, "#1F3B5C", weight=600, italic=True, anim_in=tanim("fade", duration=0.6), name="Subtítulo")
    song(t, "classic", 2, 0.65)
    return t


def fecha_primavera():
    t = wide("h-fecha-primavera", "Primavera", "Spring", "seasonal", 8.0, order=2328,
             tags=["primavera", "flores", "estación", "colores", "naturaleza"], thumb_at=4.2, background="#FDF2F8")
    photo_bg(t, "h-spring-02", s1=1.08, label="Foto de flores")
    shade_full(t, 0.15, colour="#FFFFFF")
    dots(t, ["#FFB3C6", "#FFFFFF", "#FFD6E0", "#C8E7A7"], 36, 0, 8.0, seed=328, size=(20, 44), kinds=("heart", "ellipse"),
         drift=140, alpha=0.85)
    label(t, t.track("text", "Título"), "¡Bienvenida, primavera!", 0.6, 7.4, Box(160, 360, 1600, 240), "Courgette", 140,
          "#FFFFFF", weight=400, layers=[shadow("#B5179E", 0, 6, 16, 0.6), fill("#FFFFFF")],
          anim_in=tanim("rise-by-word", duration=0.5, unit="word", stagger=0.18), name="Título")
    label(t, t.track("text", "Sub"), "días más largos, colores más vivos", 1.6, 6.4, Box(360, 620, 1200, 90), "Montserrat",
          50, "#FFFFFF", weight=600, layers=[shadow("#000000", 0, 3, 10, 0.5), fill("#FFFFFF")],
          anim_in=tanim("fade", duration=0.6), name="Subtítulo")
    song(t, "upbeat", 7, 0.7)
    return t


def fecha_dia_tierra():
    t = wide("h-fecha-dia-tierra", "Día de la Tierra", "Earth Day", "seasonal", 8.0, order=2329,
             tags=["día de la tierra", "planeta", "medio ambiente", "verde", "naturaleza"], thumb_at=4.4,
             background="#0B2E1D")
    photo_bg(t, "h-earth-01", s1=1.06, label="Foto")
    t.solid(t.track("shape", "Panel"), "#0B2E1D", 0, 8.0, Box(0, 0, 900, 1080),
            layers=[gradient([(0, "#0B2E1D", 0.95), (1, "#0B2E1D", 0.0)], angle=0), no_stroke()])
    label(t, t.track("text", "Planeta"), "🌍", 0.3, 7.7, centered(260, 280, 260, 260), "Inter", 190, "#FFFFFF", weight=400,
          editable=False, motion=pop(0, 0.5), rotation=keys([(0, -10, "linear"), (7.7, 10)]))
    label(t, t.track("text", "Título"), "Día de\nla Tierra", 0.7, 7.3, Box(120, 420, 800, 380), "Lexend", 140, "#FFFFFF",
          weight=800, line=0.95, align="left", anim_in=tanim("rise-by-word", duration=0.5, unit="word", stagger=0.15),
          name="Título")
    label(t, t.track("text", "Frase"), "cuidemos el único hogar que tenemos", 1.6, 6.4, Box(124, 820, 800, 120), "Lexend",
          44, "#B7E4C7", weight=500, align="left", line=1.2, anim_in=tanim("fade", duration=0.6), name="Frase")
    song(t, "calm", 4, 0.65)
    return t


# --- Businesses ---------------------------------------------------------------------------------

def neg_restaurante_menu():
    t = wide("h-neg-restaurante-menu", "Menú de restaurante", "Restaurant menu", "business", 10.0, order=2330,
             tags=["restaurante", "menú", "carta", "platos", "precios"], thumb_at=6.0, background="#1C1410")
    bg(t, "#1C1410")
    t.photo(t.track("video", "Plato"), "h-food-02", 0, 10.0, Box(1060, 0, 860, 1080), kb(10.0, 1.0, 1.08),
            label="Foto del plato")
    t.solid(t.track("shape", "Fundido"), "#1C1410", 0, 10.0, Box(1040, 0, 300, 1080),
            layers=[gradient([(0, "#1C1410", 1.0), (1, "#1C1410", 0.0)], angle=0), no_stroke()])
    label(t, t.track("text", "Nombre"), "La Huerta", 0.2, 9.8, Box(120, 80, 900, 160), "Playfair Display", 120, "#F4A261",
          weight=700, align="left", anim_in=tanim("fade", duration=0.6), name="Restaurante")
    label(t, t.track("text", "Sub"), "MENÚ DE LA SEMANA", 0.5, 9.5, Box(124, 240, 900, 60), "Montserrat", 34, "#D6C7B8",
          weight=700, spacing=10, align="left", anim_in=tanim("fade", duration=0.6), name="Subtítulo")
    dishes = [("Crema de calabaza", "$6"), ("Pasta al pesto", "$11"), ("Pollo a las hierbas", "$13"),
              ("Tarta de manzana", "$5")]
    for i, (d, p) in enumerate(dishes):
        at = 1.0 + i * 0.5
        y = 360 + i * 150
        label(t, t.track("text", "Plato"), d, at, 10.0 - at, Box(120, y, 700, 80), "Playfair Display", 56, "#FFFFFF",
              weight=500, align="left", anim_in=tanim("slide-right", duration=0.4, distance=0.1), name=f"Plato {i + 1}")
        label(t, t.track("text", "Precio"), p, at + 0.1, 9.9 - at, Box(820, y, 180, 80), "Montserrat", 52, "#F4A261",
              weight=800, align="right", anim_in=tanim("fade", duration=0.4), name=f"Precio {i + 1}")
        t.solid(t.track("shape", "Puntos"), "#5A4A3C", at, 10.0 - at, Box(120, y + 92, 880, 2), [(0, {"sx": 0.0, "dx": -440},
                                                                                                "out"), (0.5, {})])
    song(t, "jazz", 1, 0.6)
    return t


def neg_cafeteria():
    t = wide("h-neg-cafeteria", "Cafetería", "Coffee shop", "business", 8.0, order=2331,
             tags=["cafetería", "café", "especial del día", "desayuno", "barista"], thumb_at=4.4, background="#F3E9DC")
    bg(t, "#F3E9DC")
    circle_photo(t, "h-cafe-04", 0.3, 7.7, centered(1360, 540, 720, 720), pop(0, 0.6, 0.6), ring_colour="#6F4E37",
                 ring_width=14, label="Foto del café")
    t.photo(t.track("video", "Logo"), "logo-05", 0.4, 7.6, centered(330, 230, 300, 300), pop(0, 0.5), label="Tu logo")
    label(t, t.track("text", "Especial"), "ESPECIAL DEL DÍA", 0.8, 7.2, Box(120, 420, 900, 70), "Montserrat", 40, "#B07D62",
          weight=800, spacing=10, align="left", anim_in=tanim("fade", duration=0.5), name="Antetítulo")
    label(t, t.track("text", "Producto"), "Latte de canela\n+ medialuna", 1.1, 6.9, Box(110, 490, 900, 300),
          "DM Serif Display", 110, "#3E2723", weight=400, line=1.0, align="left",
          anim_in=tanim("rise-by-word", duration=0.5, unit="word", stagger=0.12), name="Producto")
    pill(t, t.track("shape", "Precio"), "#6F4E37", 1.8, 6.2, Box(120, 830, 320, 110), pop(0, 0.4))
    label(t, t.track("text", "Precio"), "$4,50", 1.85, 6.15, Box(120, 830, 320, 110), "Montserrat", 64, "#FFFFFF",
          weight=800, name="Precio")
    song(t, "jazz", 0, 0.6)
    return t


def neg_tienda_barrio():
    t = wide("h-neg-tienda-barrio", "Tienda de barrio", "Corner shop", "business", 8.0, order=2332,
             tags=["tienda", "barrio", "ofertas", "abarrotes", "vecinos"], thumb_at=4.6, background="#FFD23F")
    bg(t, "#FFD23F")
    t.solid(t.track("shape", "Toldo"), "#E63946", 0, 8.0, Box(0, 0, 1920, 120))
    for k in range(10):
        t.solid(t.track("shape", "Toldo"), "#FFFFFF", 0, 8.0, Box(k * 192 + 96, 0, 96, 120))
    scallops = t.track("shape", "Festón")
    for k in range(10):
        t.solid(scallops, "#E63946", 0, 8.0, centered(k * 192 + 48, 120, 96, 60), kind="ellipse")
    framed(t, "h-shop-02", 0.4, 7.6, Box(1060, 220, 740, 560), pop(0, 0.5, 0.6), border=14, radius=20,
           rotation=keys([(0, 3)]), label="Foto de la tienda")
    label(t, t.track("text", "Nombre"), "Tienda Don Pepe", 0.6, 7.4, Box(100, 200, 940, 160), "Lilita One", 110, "#1D3557",
          weight=400, align="left", anim_in=tanim("pop", duration=0.4), name="Tienda")
    label(t, t.track("text", "Oferta"), "OFERTAS DE LA SEMANA", 1.0, 7.0, Box(104, 360, 940, 70), "Lilita One", 52, "#E63946",
          weight=400, spacing=4, align="left", anim_in=tanim("fade", duration=0.4), name="Antetítulo")
    offers = [("Arroz 5 kg", "$7,90"), ("Aceite 1 L", "$3,20"), ("Huevos x30", "$4,50")]
    for i, (p, pr) in enumerate(offers):
        at = 1.4 + i * 0.4
        y = 470 + i * 150
        rrect(t, t.track("shape", "Fila"), "#FFFFFF", at, 8.0 - at, Box(100, y, 900, 120), 24, slide_in(dx=-1000, length=0.4))
        label(t, t.track("text", "Producto"), p, at + 0.1, 7.9 - at, Box(140, y, 520, 120), "Lilita One", 56, "#1D3557",
              weight=400, align="left", name=f"Producto {i + 1}")
        label(t, t.track("text", "Precio"), pr, at + 0.1, 7.9 - at, Box(660, y, 310, 120), "Lilita One", 64, "#E63946",
              weight=400, align="right", name=f"Precio {i + 1}")
    song(t, "fun", 3, 0.65)
    return t


def neg_supermercado():
    t = wide("h-neg-supermercado", "Supermercado", "Supermarket deals", "business", 8.0, order=2333,
             tags=["supermercado", "ofertas", "precios", "frutas", "descuentos"], thumb_at=4.6, background="#0B8A3E")
    photo_bg(t, "h-grocery-02", s1=1.06, label="Foto de fondo")
    t.solid(t.track("shape", "Banda"), "#0B8A3E", 0.2, 7.8, Box(0, 0, 1920, 200), slide_in(dy=-220, length=0.4))
    label(t, t.track("text", "Título"), "¡FRESCURA AL MEJOR PRECIO!", 0.4, 7.6, Box(0, 0, 1920, 200), "Anton", 110, "#FFFFFF",
          weight=400, spacing=4, anim_in=tanim("slide-down", duration=0.4), name="Título")
    tags_ = [("Manzanas", "$1,99 kg", 300), ("Tomates", "$1,49 kg", 960), ("Bananas", "$0,99 kg", 1620)]
    for i, (p, pr, x) in enumerate(tags_):
        at = 1.0 + i * 0.35
        t.solid(t.track("shape", "Etiqueta"), "#FFE600", at, 8.0 - at, centered(x, 700, 460, 300),
                [(0, {"s": 0.0}, "back"), (0.45, {})], kind="burst", points=18, innerRatio=0.88,
                layers=[shadow("#000000", 0, 10, 20, 0.4), fill("#FFE600"), stroke(6, "#D00000")])
        label(t, t.track("text", "Producto"), p, at + 0.1, 7.9 - at, centered(x, 650, 400, 80), "Anton", 60, "#111111",
              weight=400, motion=[(0, {"s": 0.0}, "back"), (0.45, {})], name=f"Producto {i + 1}")
        label(t, t.track("text", "Precio"), pr, at + 0.1, 7.9 - at, centered(x, 740, 420, 100), "Anton", 80, "#D00000",
              weight=400, motion=[(0, {"s": 0.0}, "back"), (0.45, {})], name=f"Precio {i + 1}")
    label(t, t.track("text", "Vigencia"), "válido del 10 al 16 de noviembre", 2.2, 5.8, Box(460, 960, 1000, 70), "Montserrat",
          40, "#FFFFFF", weight=700, layers=[shadow("#000000", 0, 3, 10, 0.7), fill("#FFFFFF")],
          anim_in=tanim("fade", duration=0.4), name="Vigencia")
    song(t, "upbeat", 5, 0.65)
    return t


def neg_ferreteria():
    t = wide("h-neg-ferreteria", "Ferretería", "Hardware store", "business", 8.0, order=2334,
             tags=["ferretería", "herramientas", "construcción", "descuento", "hogar"], thumb_at=4.4, background="#1B1B1B")
    photo_bg(t, "h-tools-03", s1=1.06, label="Foto de la ferretería")
    shade_full(t, 0.55)
    for k in range(18):  # hazard stripe along the bottom
        t.solid(t.track("shape", "Rayas"), "#FFC300" if k % 2 == 0 else "#111111", 0, 8.0,
                Box(-120 + k * 120, 960, 120, 120), rotation=keys([(0, 0)]))
    label(t, t.track("text", "Nombre"), "FERRETERÍA EL MARTILLO", 0.4, 7.6, Box(120, 120, 1680, 130), "Black Ops One", 96,
          "#FFC300", weight=400, anim_in=tanim("slide-right", duration=0.4), name="Ferretería")
    t.solid(t.track("shape", "Descuento"), "#E10600", 0.9, 7.1, centered(1500, 560, 560, 560), [(0, {"s": 0.0}, "back"),
                                                                                               (0.5, {})],
            kind="burst", points=20, innerRatio=0.85, rotation=keys([(0, 0, "linear"), (7.1, 30)]))
    label(t, t.track("text", "Descuento"), "-25%", 1.0, 7.0, centered(1500, 560, 520, 260), "Anton", 210, "#FFFFFF",
          weight=400, anim_in=tanim("stamp", duration=0.3), name="Descuento")
    label(t, t.track("text", "Oferta"), "en herramientas eléctricas", 1.2, 6.8, Box(120, 380, 1000, 200), "Oswald", 90,
          "#FFFFFF", weight=700, align="left", line=1.0, anim_in=tanim("rise", duration=0.4), name="Oferta")
    label(t, t.track("text", "Vigencia"), "solo este fin de semana", 1.6, 6.4, Box(120, 620, 1000, 80), "Oswald", 52,
          "#FFC300", weight=500, align="left", anim_in=tanim("fade", duration=0.4), name="Vigencia")
    song(t, "epic", 6, 0.6)
    return t


def neg_escuela():
    t = wide("h-neg-escuela", "Escuela: matrículas abiertas", "School enrolment", "business", 9.0, order=2335,
             tags=["escuela", "matrículas", "inscripciones", "colegio", "educación"], thumb_at=4.8, background="#E9F5FF")
    bg(t, "#E9F5FF")
    t.photo(t.track("video", "Foto"), "h-classroom-02", 0, 9.0, Box(960, 0, 960, 1080), kb(9.0, 1.0, 1.06),
            label="Foto de la escuela")
    t.solid(t.track("shape", "Onda"), "#E9F5FF", 0, 9.0, centered(960, 540, 300, 1400), kind="ellipse")
    label(t, t.track("text", "Antetítulo"), "AÑO ESCOLAR 2027", 0.4, 8.6, Box(110, 150, 860, 70), "Lexend", 40, "#1565C0",
          weight=800, spacing=8, align="left", anim_in=tanim("fade", duration=0.4), name="Antetítulo")
    label(t, t.track("text", "Título"), "¡Matrículas\nabiertas!", 0.7, 8.3, Box(100, 220, 860, 360), "Lexend", 130,
          "#0D47A1", weight=800, line=0.95, align="left", anim_in=tanim("rise-by-word", duration=0.5, unit="word",
          stagger=0.15), name="Título")
    _info_rows(t, [("🎒", "Inicial, primaria y secundaria"), ("🚌", "Movilidad escolar"), ("📞", "Informes: 000 123 456")],
               110, 620, 110, 1.5, font="Lexend", size=40, colour="#0D47A1", icon_bg="#FFD166", icon_colour="#0D47A1",
               width=760)
    song(t, "fun", 3, 0.65)
    return t


def neg_academia():
    t = wide("h-neg-academia", "Academia y cursos", "Academy courses", "business", 9.0, order=2336,
             tags=["academia", "cursos", "clases", "taller", "inscripciones"], thumb_at=4.8, background="#151530")
    bg_gradient(t, [(0, "#23234D"), (1, "#0E0E22")], angle=135)
    framed(t, "h-classroom-04", 0.3, 8.7, Box(1040, 160, 760, 560), pop(0, 0.5, 0.6), border=10, radius=26,
           colour="#7C83FD", label="Foto del curso")
    label(t, t.track("text", "Curso"), "Curso de fotografía", 0.6, 8.4, Box(110, 160, 900, 260), "Sora", 104, "#FFFFFF",
          weight=800, align="left", line=1.0, anim_in=tanim("rise-by-word", duration=0.4, unit="word", stagger=0.12),
          name="Curso")
    label(t, t.track("text", "Nivel"), "desde cero · 8 clases prácticas", 1.1, 7.9, Box(114, 430, 900, 70), "Sora", 44,
          "#C7CAFF", weight=500, align="left", anim_in=tanim("fade", duration=0.4), name="Detalle")
    _info_rows(t, [("📅", "Empieza el 3 de febrero"), ("🕖", "Martes y jueves · 19:00"), ("👥", "Cupos limitados")], 110, 560,
               110, 1.5, font="Sora", size=40, icon_bg="#7C83FD", icon_colour="#FFFFFF", width=800)
    pill(t, t.track("shape", "Botón"), "#FFD166", 2.6, 6.4, Box(1140, 790, 560, 110), pop(0, 0.4))
    label(t, t.track("text", "Botón"), "¡INSCRÍBETE YA!", 2.65, 6.35, Box(1140, 790, 560, 110), "Sora", 48, "#151530",
          weight=800, anim_loop=tanim("pulse", amount=4, speed=1.2), name="Llamada")
    song(t, "upbeat", 2, 0.6)
    return t


def neg_inmobiliaria():
    t = wide("h-neg-inmobiliaria", "Propiedad en venta", "Property for sale", "business", 9.0, order=2337,
             tags=["inmobiliaria", "venta", "casa", "departamento", "propiedad"], thumb_at=4.8, background="#F5F1EA")
    photo_bg(t, "h-house-04", s1=1.06, label="Foto de la propiedad")
    rrect(t, t.track("shape", "Ficha"), "#FFFFFF", 0.4, 8.6, Box(1180, 140, 640, 800), 30, slide_in(dx=700, length=0.5),
          layers=[shadow("#000000", 0, 16, 40, 0.35), fill("#FFFFFF"), no_stroke()])
    pill(t, t.track("shape", "Insignia"), "#C9A227", 0.8, 8.2, Box(1230, 190, 260, 64), pop(0, 0.35))
    label(t, t.track("text", "Insignia"), "SE VENDE", 0.8, 8.2, Box(1230, 190, 260, 64), "Montserrat", 32, "#FFFFFF",
          weight=800, spacing=6, name="Insignia")
    label(t, t.track("text", "Tipo"), "Casa moderna con jardín", 1.0, 8.0, Box(1230, 280, 560, 180), "Playfair Display", 64,
          "#1F3A5F", weight=700, align="left", line=1.05, anim_in=tanim("fade", duration=0.4), name="Propiedad")
    label(t, t.track("text", "Precio"), "$245.000", 1.3, 7.7, Box(1230, 480, 560, 100), "Montserrat", 74, "#C9A227",
          weight=800, align="left", anim_in=tanim("pop", duration=0.4), name="Precio")
    feats = ["🛏  4 dormitorios", "🛁  3 baños", "🚗  2 cocheras", "📐  210 m²"]
    for i, f in enumerate(feats):
        label(t, t.track("text", "Dato"), f, 1.6 + i * 0.2, 7.4 - i * 0.2, Box(1230, 610 + i * 70, 560, 64), "Montserrat",
              38, "#334155", weight=500, align="left", anim_in=tanim("fade", duration=0.3), name=f"Dato {i + 1}")
    label(t, t.track("text", "Contacto"), "Agente: Laura · 000 123 456", 2.4, 6.6, Box(80, 960, 1060, 70), "Montserrat", 40,
          "#FFFFFF", weight=700, align="left", layers=[shadow("#000000", 0, 3, 10, 0.7), fill("#FFFFFF")],
          anim_in=tanim("fade", duration=0.4), name="Contacto")
    song(t, "calm", 2, 0.6)
    return t


def neg_comunidad():
    t = wide("h-neg-comunidad", "Comunidad: reunión", "Community meeting", "business", 8.0, order=2338,
             tags=["comunidad", "reunión", "iglesia", "grupo", "anuncio", "frase del día"], thumb_at=4.4,
             background="#2F3E46")
    photo_bg(t, "h-community-04", s1=1.06, label="Foto de la comunidad")
    shade_full(t, 0.55, colour="#1B262C")
    label(t, t.track("text", "Antetítulo"), "TE ESPERAMOS", 0.4, 7.6, Box(160, 200, 1600, 80), "Montserrat", 48, "#F6BD60",
          weight=800, spacing=14, anim_in=tanim("fade", duration=0.5), name="Antetítulo")
    label(t, t.track("text", "Título"), "Reunión de la comunidad", 0.7, 7.3, Box(160, 290, 1600, 200), "DM Serif Display",
          130, "#FFFFFF", weight=400, anim_in=tanim("rise-by-word", duration=0.5, unit="word", stagger=0.12), name="Título")
    rrect(t, t.track("shape", "Panel"), "#FFFFFF", 1.3, 6.7, centered(960, 680, 1100, 220), 30, pop(0, 0.4, 0.8),
          layers=[fill("#FFFFFF", 0.14), stroke(2, "#FFFFFF", 0.5)])
    label(t, t.track("text", "Datos"), "todos los jueves · 19:30 h\nsalón principal · entrada libre", 1.5, 6.5,
          centered(960, 680, 1060, 200), "Montserrat", 52, "#FFFFFF", weight=600, line=1.3,
          anim_in=tanim("fade", duration=0.5), name="Día, hora y lugar")
    label(t, t.track("text", "Frase"), "«juntos somos más fuertes»", 2.2, 5.8, Box(160, 860, 1600, 80), "Cormorant Garamond",
          56, "#F6BD60", weight=600, italic=True, anim_in=tanim("fade", duration=0.6), name="Frase")
    song(t, "calm", 3, 0.6)
    return t


def neg_mudanzas():
    t = wide("h-neg-mudanzas", "Mudanzas y transporte", "Moving and transport", "business", 8.0, order=2339,
             tags=["mudanzas", "transporte", "fletes", "camión", "servicio"], thumb_at=4.4, background="#FF7B00")
    bg(t, "#FF7B00")
    t.photo(t.track("video", "Foto"), "h-truck-03", 0.2, 7.8, Box(960, 120, 860, 620), [(0, {"dx": 900}, "out"), (0.6, {})],
            label="Foto del servicio")
    t.solid(t.track("shape", "Camino"), "#1B1B1B", 0, 8.0, Box(0, 860, 1920, 220))
    for k in range(9):
        t.solid(t.track("shape", "Línea"), "#FFFFFF", 0, 8.0, Box(k * 240, 960, 120, 14),
                [(0, {}, "linear"), (8.0, {"dx": -480})])
    label(t, t.track("text", "Camión"), "🚚", 0.5, 7.5, centered(300, 800, 260, 220), "Inter", 180, "#FFFFFF", weight=400,
          editable=False, motion=[(0, {"dx": -600}, "out"), (1.0, {})], anim_loop=tanim("jitter", amount=1, angle=1, speed=10))
    label(t, t.track("text", "Título"), "MUDANZAS\nRÁPIDAS", 0.6, 7.4, Box(100, 120, 860, 380), "Anton", 160, "#FFFFFF",
          weight=400, line=0.95, align="left", anim_in=tanim("slide-right", duration=0.4, unit="word", stagger=0.1),
          name="Título")
    label(t, t.track("text", "Servicio"), "embalaje · carga · seguro incluido", 1.2, 6.8, Box(104, 510, 860, 80), "Montserrat",
          44, "#1B1B1B", weight=700, align="left", anim_in=tanim("fade", duration=0.4), name="Servicio")
    label(t, t.track("text", "Teléfono"), "☎ 000 123 456", 1.6, 6.4, Box(104, 610, 860, 100), "Anton", 80, "#1B1B1B",
          weight=400, align="left", anim_in=tanim("pop", duration=0.35), name="Teléfono")
    song(t, "upbeat", 4, 0.65)
    return t


def neg_presentacion():
    t = wide("h-neg-presentacion", "Presentación de empresa", "Company presentation", "business", 10.0, order=2340,
             tags=["empresa", "presentación", "corporativo", "misión", "cifras"], thumb_at=6.6, background="#FFFFFF")
    bg(t, "#FFFFFF")
    t.photo(t.track("video", "Foto"), "h-office-01", 0, 10.0, Box(0, 0, 900, 1080), kb(10.0, 1.0, 1.06), label="Foto de la empresa")
    t.solid(t.track("shape", "Acento"), "#0B3D91", 0, 10.0, Box(900, 0, 24, 1080), [(0, {"sy": 0.0, "dy": -540}, "out"),
                                                                                (0.8, {})])
    t.photo(t.track("video", "Logo"), "logo-01", 0.4, 9.6, centered(1100, 160, 200, 200), pop(0, 0.4), label="Tu logo")
    label(t, t.track("text", "Misión"), "Construimos espacios que mejoran la vida de las personas.", 0.8, 9.2,
          Box(1000, 290, 840, 300), "Montserrat", 60, "#0B3D91", weight=800, align="left", line=1.15,
          anim_in=tanim("rise-by-word", duration=0.4, unit="word", stagger=0.06), name="Misión")
    stats = [("25", "años"), ("1.200", "proyectos"), ("14", "países")]
    for i, (n, l) in enumerate(stats):
        x = 1000 + i * 290
        at = 2.4 + i * 0.4
        label(t, t.track("text", "Cifra"), n, at, 10.0 - at, Box(x, 680, 280, 130), "Montserrat", 96, "#1E66F5", weight=900,
              align="left", anim_in=tanim("pop", duration=0.4), name=f"Cifra {i + 1}")
        label(t, t.track("text", "Unidad"), l, at + 0.1, 9.9 - at, Box(x, 810, 280, 60), "Montserrat", 38, "#4A5568",
              weight=600, align="left", anim_in=tanim("fade", duration=0.3), name=f"Unidad {i + 1}")
    song(t, "upbeat", 3, 0.6)
    return t


def neg_contratando():
    t = wide("h-neg-contratando", "Estamos contratando", "We're hiring", "business", 9.0, order=2341,
             tags=["empleo", "trabajo", "vacantes", "contratando", "únete"], thumb_at=5.0, background="#FFDD00")
    bg(t, "#FFDD00")
    label(t, t.track("text", "Título"), "¡ESTAMOS\nCONTRATANDO!", 0.3, 8.7, Box(100, 100, 1100, 460), "Anton", 190, "#111111",
          weight=400, line=0.92, align="left", anim_in=tanim("slide-up", duration=0.4, unit="word", stagger=0.12),
          name="Título")
    circle_photo(t, "h-man-01", 0.6, 8.4, centered(1550, 400, 520, 520), pop(0, 0.5), ring_colour="#111111", ring_width=10,
                 label="Foto")
    jobs = ["Cocinero/a", "Atención al cliente", "Repartidor/a"]
    for i, j in enumerate(jobs):
        at = 1.4 + i * 0.35
        pill(t, t.track("shape", "Puesto"), "#111111", at, 9.0 - at, Box(100 + i * 0, 620 + i * 120, 760, 96),
             slide_in(dx=-900, length=0.4))
        label(t, t.track("text", "Puesto"), "✓  " + j, at + 0.1, 8.9 - at, Box(140, 620 + i * 120, 700, 96), "Montserrat",
              46, "#FFDD00", weight=800, align="left", name=f"Puesto {i + 1}")
    label(t, t.track("text", "Contacto"), "envía tu CV a empleos@tunegocio.com", 2.6, 6.4, Box(960, 840, 900, 120),
          "Montserrat", 44, "#111111", weight=700, align="center", line=1.15, anim_in=tanim("fade", duration=0.4),
          name="Contacto")
    song(t, "upbeat", 1, 0.65)
    return t


def neg_testimonio():
    t = wide("h-neg-testimonio", "Testimonio", "Testimonial", "business", 8.0, order=2342,
             tags=["testimonio", "reseña", "cliente", "opinión", "estrellas"], thumb_at=5.0, background="#F7F4EF")
    bg(t, "#F7F4EF")
    circle_photo(t, "h-portrait-04", 0.3, 7.7, centered(420, 540, 520, 520), pop(0, 0.5), ring_colour="#E9C46A",
                 ring_width=12, label="Foto del cliente")
    for k in range(5):
        label(t, t.track("text", "Estrella"), "★", 0.8 + k * 0.12, 7.2 - k * 0.12, centered(860 + k * 90, 260, 90, 90), "Inter",
              76, "#F4A100", weight=400, editable=False, motion=pop(0, 0.35))
    label(t, t.track("text", "Reseña"), "«Me atendieron rápido y el resultado superó lo que esperaba. ¡Volveré!»", 1.4, 6.6,
          Box(800, 340, 1020, 380), "Lora", 64, "#2D2A26", weight=500, italic=True, align="left", line=1.2,
          anim_in=tanim("rise-by-word", duration=0.4, unit="word", stagger=0.05), name="Reseña")
    label(t, t.track("text", "Cliente"), "— Marta G., clienta desde 2024", 2.6, 5.4, Box(800, 760, 1000, 70), "Montserrat",
          40, "#8C6B2F", weight=700, align="left", anim_in=tanim("fade", duration=0.4), name="Cliente")
    song(t, "calm", 2, 0.6)
    return t


def neg_lanzamiento():
    t = wide("h-neg-lanzamiento", "Lanzamiento de producto", "Product launch", "business", 8.0, order=2343,
             tags=["lanzamiento", "nuevo", "producto", "presentación", "novedad"], thumb_at=4.6, background="#050505")
    bg(t, "#050505")
    for i, x in enumerate((560, 1360)):
        t.solid(t.track("shape", "Foco"), "#FFFFFF", 0.3, 7.7, Box(x - 300, -100, 600, 1200), pop(0, 0.6, 0.5),
                kind="triangle", layers=[gradient([(0, "#FFFFFF", 0.0), (1, "#FFFFFF", 0.22)], angle=90), no_stroke()],
                rotation=keys([(0, 14 if i == 0 else -14)]))
    t.solid(t.track("shape", "Pedestal"), "#1F1F1F", 0.4, 7.6, centered(960, 900, 900, 160), kind="ellipse",
            layers=[gradient([(0, "#3A3A3A"), (1, "#111111")], angle=90), no_stroke()])
    t.photo(t.track("video", "Producto"), "h-product-04", 0.8, 7.2, centered(960, 560, 820, 520),
            [(0, {"s": 0.7, "dy": 80}, "back"), (0.6, {}, "linear"), (7.2, {"s": 1.04})], label="Foto del producto")
    label(t, t.track("text", "Nuevo"), "NUEVO", 1.4, 6.6, Box(160, 80, 1600, 100), "Montserrat", 60, "#E9C46A", weight=800,
          spacing=40, anim_in=tanim("tracking-drift", duration=1.0), name="Antetítulo")
    label(t, t.track("text", "Producto"), "Serie Calma", 1.8, 6.2, Box(160, 170, 1600, 160), "Montserrat", 120, "#FFFFFF",
          weight=900, anim_in=tanim("blur-in", duration=0.6), name="Producto")
    label(t, t.track("text", "Fecha"), "disponible desde el 1 de diciembre", 2.4, 5.6, Box(160, 990, 1600, 70), "Montserrat",
          40, "#BBBBBB", weight=500, anim_in=tanim("fade", duration=0.5), name="Disponibilidad")
    flash(t, 0.8, 0.3, peak=0.6)
    song(t, "epic", 5, 0.7)
    return t


def neg_rebajas():
    t = wide("h-neg-rebajas", "Rebajas", "Big sale", "business", 7.0, order=2344,
             tags=["rebajas", "descuentos", "sale", "liquidación", "ofertas"], thumb_at=3.6, background="#E10600")
    bg(t, "#E10600")
    for k in range(6):
        t.solid(t.track("shape", "Franja"), "#FF3B30", 0, 7.0, Box(-400 + k * 420, -200, 180, 1500),
                [(0, {}, "linear"), (7.0, {"dx": 420})], rotation=keys([(0, 20)]))
    label(t, t.track("text", "Hasta"), "HASTA", 0.3, 6.7, Box(160, 120, 1600, 120), "Anton", 110, "#FFFFFF", weight=400,
          spacing=20, anim_in=tanim("drop", duration=0.4), name="Antetítulo")
    label(t, t.track("text", "Porcentaje"), "50%", 0.6, 6.4, Box(160, 200, 1600, 560), "Anton", 520, "#FFE600", weight=400,
          layers=[shadow("#8B0000", 0, 18, 0, 1.0), fill("#FFE600")], anim_in=tanim("stamp", duration=0.35),
          anim_loop=tanim("pulse", amount=3, speed=1.4), name="Porcentaje")
    label(t, t.track("text", "Texto"), "EN TODA LA TIENDA · SOLO 3 DÍAS", 1.2, 5.8, Box(160, 800, 1600, 110), "Anton", 80,
          "#FFFFFF", weight=400, spacing=6, anim_in=tanim("slide-up", duration=0.4), name="Texto")
    t.adjust([effect("beat_shake", animated={"amount": spike([0.6], 0.8, 0.35)})], name="Golpe")
    song(t, "electro", 0, 0.75)
    return t


def neg_webinar():
    t = wide("h-neg-webinar", "Webinar", "Webinar", "business", 9.0, order=2345,
             tags=["webinar", "charla en línea", "evento", "registro", "ponente"], thumb_at=5.0, background="#0B1020")
    bg_gradient(t, [(0, "#16204A"), (1, "#070B18")], angle=135)
    pill(t, t.track("shape", "Etiqueta"), "#22D3EE", 0.3, 8.7, Box(110, 140, 380, 70), pop(0, 0.35))
    label(t, t.track("text", "Etiqueta"), "WEBINAR GRATIS", 0.3, 8.7, Box(110, 140, 380, 70), "Plus Jakarta Sans", 32,
          "#0B1020", weight=800, spacing=4, name="Etiqueta")
    label(t, t.track("text", "Título"), "Vende más en redes sociales", 0.6, 8.4, Box(110, 240, 1000, 300), "Plus Jakarta Sans",
          100, "#FFFFFF", weight=800, align="left", line=1.02,
          anim_in=tanim("rise-by-word", duration=0.4, unit="word", stagger=0.1), name="Título")
    _info_rows(t, [("📅", "Jueves 14 de noviembre"), ("🕖", "19:00 h (hora local)"), ("💻", "En vivo por Zoom")], 110, 590,
               105, 1.4, font="Plus Jakarta Sans", size=42, icon_bg="#22D3EE", icon_colour="#0B1020", width=800)
    circle_photo(t, "h-portrait-01", 0.8, 8.2, centered(1500, 440, 460, 460), pop(0, 0.5), ring_colour="#22D3EE",
                 ring_width=10, label="Foto del ponente")
    label(t, t.track("text", "Ponente"), "con Lucía Paredes", 1.4, 7.6, Box(1200, 700, 600, 70), "Plus Jakarta Sans", 44,
          "#FFFFFF", weight=700, anim_in=tanim("fade", duration=0.4), name="Ponente")
    label(t, t.track("text", "Cargo"), "estratega digital", 1.5, 7.5, Box(1200, 770, 600, 60), "Plus Jakarta Sans", 34,
          "#94A3B8", weight=500, anim_in=tanim("fade", duration=0.4), name="Cargo")
    song(t, "upbeat", 3, 0.6)
    return t


def neg_agenda_evento():
    t = wide("h-neg-agenda-evento", "Programa del evento", "Event schedule", "business", 10.0, order=2346,
             tags=["programa", "agenda", "evento", "horario", "conferencia"], thumb_at=6.6, background="#FAF7F2")
    bg(t, "#FAF7F2")
    t.solid(t.track("shape", "Banda"), "#264653", 0, 10.0, Box(0, 0, 620, 1080), slide_in(dx=-620, length=0.5))
    label(t, t.track("text", "Evento"), "Feria de emprendedores", 0.4, 9.6, Box(60, 300, 530, 360), "DM Serif Display", 74,
          "#FFFFFF", weight=400, align="left", line=1.0, anim_in=tanim("fade", duration=0.6), name="Evento")
    label(t, t.track("text", "Fecha"), "SÁB 15 · NOV", 0.8, 9.2, Box(72, 700, 500, 70), "Montserrat", 44, "#E9C46A",
          weight=800, spacing=6, align="left", anim_in=tanim("fade", duration=0.5), name="Fecha")
    items = [("09:00", "Bienvenida y café"), ("10:00", "Charla: crecer sin deudas"), ("12:00", "Ronda de negocios"),
             ("14:00", "Almuerzo"), ("16:00", "Premiación y cierre")]
    for i, (h, txt) in enumerate(items):
        at = 1.0 + i * 0.5
        y = 160 + i * 160
        label(t, t.track("text", "Hora"), h, at, 10.0 - at, Box(720, y, 220, 90), "Montserrat", 56, "#2A9D8F", weight=800,
              align="left", anim_in=tanim("fade", duration=0.3), name=f"Hora {i + 1}")
        label(t, t.track("text", "Actividad"), txt, at + 0.1, 9.9 - at, Box(960, y, 880, 90), "Montserrat", 50, "#264653",
              weight=600, align="left", anim_in=tanim("slide-right", duration=0.35, distance=0.1), name=f"Actividad {i + 1}")
        t.solid(t.track("shape", "Línea"), "#E5DED3", at, 10.0 - at, Box(720, y + 110, 1120, 2),
                [(0, {"sx": 0.0, "dx": -560}, "out"), (0.5, {})])
    song(t, "upbeat", 2, 0.55)
    return t


def neg_cifras():
    t = wide("h-neg-cifras", "Resultados del año", "Year in numbers", "business", 9.0, order=2347,
             tags=["resultados", "cifras", "informe", "crecimiento", "gráfico"], thumb_at=6.4, background="#0F172A")
    bg(t, "#0F172A")
    label(t, t.track("text", "Título"), "Nuestro 2026 en cifras", 0.2, 8.8, Box(120, 80, 1680, 130), "Sora", 90, "#FFFFFF",
          weight=800, align="left", anim_in=tanim("fade-up-char", duration=0.4, unit="character", stagger=0.02),
          name="Título")
    bars = [("ENE", 0.35), ("MAR", 0.48), ("MAY", 0.55), ("JUL", 0.7), ("SEP", 0.78), ("NOV", 0.95)]
    for i, (m, v) in enumerate(bars):
        x = 160 + i * 190
        h = 620 * v
        at = 0.8 + i * 0.25
        rrect(t, t.track("shape", "Barra"), "#38BDF8", at, 9.0 - at, Box(x, 920 - h, 120, h), 14,
              [(0, {"sy": 0.0, "dy": h / 2}, "out"), (0.7, {})],
              layers=[gradient([(0, "#38BDF8"), (1, "#6366F1")], angle=90), no_stroke()])
        label(t, t.track("text", "Mes"), m, at, 9.0 - at, Box(x - 20, 940, 160, 60), "Sora", 34, "#94A3B8", weight=600,
              editable=False, anim_in=tanim("fade", duration=0.3))
    label(t, t.track("text", "Cifra"), "+38%", 2.8, 6.2, Box(1340, 330, 520, 200), "Sora", 160, "#34D399", weight=800,
          anim_in=tanim("pop", duration=0.4), name="Cifra principal")
    label(t, t.track("text", "Detalle"), "más ventas que el año pasado", 3.2, 5.8, Box(1340, 540, 520, 140), "Sora", 44,
          "#CBD5E1", weight=500, line=1.2, anim_in=tanim("fade", duration=0.4), name="Detalle")
    song(t, "upbeat", 4, 0.55)
    return t


def neg_contacto():
    t = wide("h-neg-contacto", "Contáctanos", "Contact us", "business", 8.0, order=2348,
             tags=["contacto", "dirección", "horario", "teléfono", "negocio"], thumb_at=4.6, background="#FFFFFF")
    bg(t, "#FFFFFF")
    t.photo(t.track("video", "Foto"), "h-shop-05", 0, 8.0, Box(1060, 0, 860, 1080), kb(8.0, 1.0, 1.06),
            label="Foto del local")
    label(t, t.track("text", "Título"), "Visítanos", 0.3, 7.7, Box(110, 120, 900, 180), "DM Serif Display", 140, "#111827",
          weight=400, align="left", anim_in=tanim("rise", duration=0.5), name="Título")
    _info_rows(t, [("📍", "Av. Central 245, local 3"), ("🕘", "Lun a sáb · 9:00 a 20:00"), ("📞", "000 123 456"),
                   ("✉", "hola@tunegocio.com")], 110, 360, 140, 0.8, font="Montserrat", size=46, colour="#111827",
               icon_bg="#111827", icon_colour="#FFFFFF", width=800)
    song(t, "calm", 1, 0.55)
    return t


def neg_gimnasio():
    t = wide("h-neg-gimnasio", "Gimnasio: planes", "Gym plans", "business", 9.0, order=2349,
             tags=["gimnasio", "planes", "precios", "fitness", "membresía"], thumb_at=5.0, background="#0A0A0A")
    photo_bg(t, "h-fitness-04", s1=1.06, label="Foto del gimnasio")
    shade_full(t, 0.7)
    label(t, t.track("text", "Título"), "ELIGE TU PLAN", 0.3, 8.7, Box(160, 80, 1600, 150), "Anton", 130, "#FFFFFF",
          weight=400, spacing=6, anim_in=tanim("slide-down", duration=0.4), name="Título")
    plans = [("BÁSICO", "$25", "sala de pesas", "#2A2A2A"), ("PRO", "$39", "pesas + clases", "#E10600"),
             ("PREMIUM", "$55", "todo + nutricionista", "#2A2A2A")]
    for i, (n, p, d, c) in enumerate(plans):
        x = 380 + i * 580
        at = 0.8 + i * 0.3
        big = i == 1
        rrect(t, t.track("shape", "Plan"), c, at, 9.0 - at, centered(x, 600, 480, 600 if big else 540), 30,
              [(0, {"dy": 600}, "out"), (0.5, {})], layers=[shadow("#000000", 0, 14, 30, 0.5), fill(c), stroke(3, "#FFFFFF", 0.25)])
        label(t, t.track("text", "Plan"), n, at + 0.1, 8.9 - at, centered(x, 400, 440, 80), "Anton", 64, "#FFFFFF",
              weight=400, spacing=6, motion=[(0, {"dy": 600}, "out"), (0.5, {})], name=f"Plan {i + 1}")
        label(t, t.track("text", "Precio"), p, at + 0.1, 8.9 - at, centered(x, 560, 440, 200), "Anton", 170, "#FFFFFF",
              weight=400, motion=[(0, {"dy": 600}, "out"), (0.5, {})], name=f"Precio {i + 1}")
        label(t, t.track("text", "Detalle"), d, at + 0.1, 8.9 - at, centered(x, 720, 440, 70), "Montserrat", 36,
              "#DDDDDD", weight=600, motion=[(0, {"dy": 600}, "out"), (0.5, {})], name=f"Incluye {i + 1}")
    label(t, t.track("text", "Mes"), "por mes · sin matrícula en noviembre", 2.4, 6.6, Box(160, 960, 1600, 70), "Montserrat",
          40, "#FFFFFF", weight=700, anim_in=tanim("fade", duration=0.4), name="Condiciones")
    song(t, "epic", 6, 0.65)
    return t


TEMPLATES = [cele_baby_shower, cele_graduacion, cele_boda_invitacion, cele_15_16, cele_reunion, cele_logro,
             cele_bienvenida_bebe, cele_despedida, cele_premios, cele_fiesta_invitacion,
             fecha_navidad, fecha_anio_nuevo, fecha_san_valentin, fecha_dia_madre, fecha_dia_padre, fecha_halloween,
             fecha_pascua, fecha_anio_nuevo_lunar, fecha_ramadan, fecha_eid, fecha_diwali, fecha_accion_gracias,
             fecha_regreso_clases, fecha_dia_mujer, fecha_dia_maestro, fecha_verano, fecha_otono, fecha_invierno,
             fecha_primavera, fecha_dia_tierra,
             neg_restaurante_menu, neg_cafeteria, neg_tienda_barrio, neg_supermercado, neg_ferreteria, neg_escuela,
             neg_academia, neg_inmobiliaria, neg_comunidad, neg_mudanzas, neg_presentacion, neg_contratando,
             neg_testimonio, neg_lanzamiento, neg_rebajas, neg_webinar, neg_agenda_evento, neg_cifras, neg_contacto,
             neg_gimnasio]
