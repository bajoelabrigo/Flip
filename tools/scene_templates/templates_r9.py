"""Reel batch 9 (2026-10-16): products, text formats, intros, endings, countdowns and vertical lower thirds,
1080x1920. See BRIEF.md, «Las 400 nuevas». Order 3300-3399.

Products: unboxing, 360°, colours, combo, best seller, detail with a magnifier, review with stars, size
comparison, sold out → back, benefits list. Text: post thread, notes app, Q&A, three mistakes, myth or
truth, ranking 5 to 1, text recipe, underlined quote, to-do list, star signs, «day X of…», trivia, film
line, money tip, word of the day, translation, things that make me happy, thought of the day, short poem,
30-day challenge. Intros: welcome to my channel, new video, live now. Endings: follow for more, save it,
share it, link in bio, comment, thanks for 1k, see you tomorrow. Countdowns: 5 seconds, reveal, birthday,
holidays, wedding. Lower thirds: name, @handle, location, price, opening hours.
"""

from __future__ import annotations

from kit import (Box, appear, bg, bg_gradient, blink, centered, circle_photo, confetti, dots, effect, fill, flash,
                 framed, glow, gradient, grain, keys, kb, label, letterbox, line, math, no_stroke, outline, panels,
                 photo_bg, pill, pop, random, ring, rrect, shade_bottom, shade_full, shade_top, shadow, slide_in, slides,
                 song, spike, stroke, tall, tanim, vignette)


def _card(t, colour, t0, dur, box, radius=40, motion=None, alpha=1.0, shadow_alpha=0.18):
    return rrect(t, t.track("shape", "Tarjeta"), colour, t0, dur, box, radius, motion or pop(0, 0.4, 0.8),
                 layers=[shadow("#000000", 0, 12, 30, shadow_alpha), fill(colour, alpha), no_stroke()])


def _count(t, track, values, t0, each, box, font, size, colour, layers=None, anim="pop"):
    for i, v in enumerate(values):
        label(t, track, v, t0 + i * each, each, box, font, size, colour, weight=800, layers=layers,
              anim_in=tanim(anim, duration=min(0.35, each * 0.6)), editable=False)


# --- Products -----------------------------------------------------------------------------------

def unboxing():
    t = tall("r-unboxing", "Unboxing", "Unboxing", "product", 9.0, order=3300,
             tags=["unboxing", "abriendo", "pedido", "producto", "compras"], thumb_at=6.0, background="#F2EDE7")
    bg(t, "#F2EDE7")
    slides(t, ["box-02", "shopping-04", "skincare-03"], 0.0, 2.5, Box(80, 300, 920, 1200), transition="zoom_in", tdur=0.3,
           kb_amount=0.06)
    photo_bg(t, "skincare-02", 7.5, 1.5, s1=1.04, label="Producto final")
    label(t, t.track("text", "Título"), "UNBOXING", 0.2, 7.2, Box(60, 120, 960, 150), "Archivo Black", 120, "#2D2A26",
          weight=400, spacing=8, anim_in=tanim("slide-down", duration=0.3), name="Título")
    steps = ["1. llegó la caja 📦", "2. ¿qué habrá adentro?", "3. ¡me encanta! ✨"]
    for i, s in enumerate(steps):
        label(t, t.track("text", "Paso"), s, 0.3 + i * 2.5, 2.3, Box(60, 1560, 960, 120), "DM Sans", 66, "#2D2A26", weight=800,
              anim_in=tanim("pop", duration=0.3), anim_out=tanim("fade", duration=0.2), name=f"Paso {i + 1}")
    flash(t, 7.5, 0.3)
    label(t, t.track("text", "Final"), "link en mi perfil", 7.6, 1.4, Box(60, 1660, 960, 120), "DM Sans", 70, "#FFFFFF",
          weight=800, box_bg=("#2D2A26", 0.8), box_pad=20, box_radius=20, anim_in=tanim("pop", duration=0.3), name="Final")
    song(t, "upbeat", 2, 0.8)
    return t


def producto_360():
    t = tall("r-producto-360", "Producto en 360°", "Product 360", "product", 8.0, order=3301,
             tags=["producto", "360", "giro", "detalle", "tienda"], thumb_at=3.2, background="#111111")
    bg_gradient(t, [(0, "#2B2B2B"), (1, "#0C0C0C")], angle=90)
    t.solid(t.track("shape", "Base"), "#3A3A3A", 0, 8.0, centered(540, 1380, 800, 160), kind="ellipse",
            layers=[gradient([(0, "#555555"), (1, "#1A1A1A")], angle=90), no_stroke()])
    t.photo(t.track("video", "Producto"), "skincare-02", 0.2, 7.8, centered(540, 900, 700, 900), pop(0, 0.5),
            label="Foto del producto", rotationY=keys([(0, -30, "smooth"), (2.0, 30, "smooth"), (4.0, -30, "smooth"),
                                                        (6.0, 30, "smooth"), (7.8, 0)]))
    ring(t, t.track("shape", "Órbita"), "#FFFFFF", 3, 0.6, 7.4, centered(540, 1380, 900, 200), alpha=0.35)
    label(t, t.track("text", "360"), "360°", 0.6, 7.4, Box(60, 150, 960, 200), "Montserrat", 170, "#FFFFFF", weight=900,
          anim_in=tanim("zoom-out", duration=0.5), name="Rótulo")
    label(t, t.track("text", "Nombre"), "Sérum Calma · 30 ml", 1.2, 6.8, Box(60, 1520, 960, 100), "Montserrat", 58,
          "#FFFFFF", weight=700, anim_in=tanim("fade", duration=0.4), name="Producto")
    song(t, "electro", 3, 0.8)
    return t


def colores_disponibles():
    t = tall("r-colores-disponibles", "Colores disponibles", "Available colours", "product", 8.0, order=3302,
             tags=["colores", "variantes", "producto", "moda", "tienda"], thumb_at=5.8, background="#F7F7F7")
    colours = [("#E63946", "rojo"), ("#2A9D8F", "verde"), ("#264653", "azul"), ("#E9C46A", "mostaza")]
    for i, (c, n) in enumerate(colours):
        at = i * 2.0
        t.solid(t.track("shape", "Fondo"), c, at, 2.0, t.full, [(0, {"dy": 1920}, "out"), (0.4, {})])
        t.photo(t.track("video", "Producto"), "handmade-01", at + 0.1, 1.9, centered(540, 860, 760, 960),
                [(0, {"s": 0.8}, "back"), (0.4, {})], label="Foto del producto", reuse="p1" if i else None,
                effects=[effect("color.basic", saturation=-0.6)])
        label(t, t.track("text", "Color"), n, at + 0.2, 1.8, Box(60, 1440, 960, 160), "DM Sans", 120, "#FFFFFF", weight=800,
              anim_in=tanim("slide-up", duration=0.3), name=f"Color {i + 1}")
    for i, (c, _) in enumerate(colours):
        t.solid(t.track("shape", "Muestra"), c, 0.2, 7.8, centered(330 + i * 140, 1700, 100, 100), kind="ellipse",
                layers=[shadow("#000000", 0, 6, 12, 0.3), fill(c), stroke(6, "#FFFFFF")])
    label(t, t.track("text", "Título"), "¿cuál te llevas?", 0.2, 7.8, Box(60, 150, 960, 140), "DM Sans", 90, "#FFFFFF",
          weight=800, layers=[shadow("#000000", 0, 4, 12, 0.4), fill("#FFFFFF")], name="Título")
    song(t, "fun", 3, 0.8)
    return t


def combo():
    t = tall("r-combo", "Combo de productos", "Product bundle", "product", 8.0, order=3303,
             tags=["combo", "pack", "oferta", "regalo", "precio especial"], thumb_at=5.0, background="#FFF4E6")
    bg(t, "#FFF4E6")
    items = [("skincare-02", Box(80, 300, 440, 560), -4), ("skincare-03", Box(560, 300, 440, 560), 4),
             ("handmade-03", Box(320, 820, 440, 520), 0)]
    for i, (s, box, r) in enumerate(items):
        framed(t, s, 0.3 + i * 0.6, 7.7 - i * 0.6, box, [(0, {"s": 0.0}, "back"), (0.45, {})], border=12, radius=30,
               rotation=keys([(0, r)]), label=f"Producto {i + 1}")
    label(t, t.track("text", "Más"), "+", 0.9, 7.1, centered(540, 580, 140, 140), "Montserrat", 130, "#FF5A1F", weight=900,
          editable=False, motion=pop(0, 0.3))
    label(t, t.track("text", "Título"), "COMBO CALMA", 0.2, 7.8, Box(60, 130, 960, 140), "Anton", 120, "#2D2A26", weight=400,
          spacing=6, anim_in=tanim("slide-down", duration=0.3), name="Título")
    t.solid(t.track("shape", "Precio"), "#FF5A1F", 2.4, 5.6, centered(780, 1500, 420, 420), [(0, {"s": 0.0}, "back"), (0.45, {})],
            kind="burst", points=16, innerRatio=0.86, rotation=keys([(0, 0, "linear"), (5.6, 30)]))
    label(t, t.track("text", "Precio"), "$49", 2.5, 5.5, centered(780, 1500, 400, 200), "Anton", 150, "#FFFFFF", weight=400,
          anim_in=tanim("stamp", duration=0.3), name="Precio")
    label(t, t.track("text", "Antes"), "antes $65", 2.8, 5.2, Box(60, 1420, 460, 100), "Montserrat", 56, "#9E9E9E", weight=700,
          align="left", anim_in=tanim("fade", duration=0.3), name="Precio anterior")
    t.solid(t.track("shape", "Tachado"), "#9E9E9E", 3.0, 5.0, Box(60, 1468, 280, 6), [(0, {"sx": 0.0, "dx": -140}, "out"),
                                                                                    (0.3, {})])
    song(t, "upbeat", 6, 0.8)
    return t


def mas_vendido():
    t = tall("r-mas-vendido", "El más vendido", "Best seller", "product", 7.0, order=3304,
             tags=["más vendido", "best seller", "favorito", "producto", "top"], thumb_at=3.6, background="#111111")
    photo_bg(t, "handmade-03", s1=1.08, label="Foto del producto")
    shade_full(t, 0.3)
    t.solid(t.track("shape", "Medalla"), "#FFD23F", 0.5, 6.5, centered(800, 360, 340, 340), [(0, {"s": 0.0}, "back"), (0.5, {})],
            kind="burst", points=20, innerRatio=0.88, layers=[shadow("#000000", 0, 10, 20, 0.4), fill("#FFD23F"), no_stroke()],
            rotation=keys([(0, -10, "linear"), (6.5, 20)]))
    label(t, t.track("text", "Medalla"), "Nº 1", 0.6, 6.4, centered(800, 360, 300, 200), "Anton", 120, "#111111", weight=400,
          motion=[(0, {"s": 0.0}, "back"), (0.5, {})], name="Medalla")
    label(t, t.track("text", "Título"), "EL MÁS\nVENDIDO", 1.0, 6.0, Box(60, 1200, 960, 360), "Anton", 170, "#FFFFFF", weight=400,
          line=0.92, layers=[shadow("#000000", 0, 8, 20, 0.6), fill("#FFFFFF")], anim_in=tanim("slide-up", duration=0.4,
          unit="word", stagger=0.12), name="Título")
    label(t, t.track("text", "Sub"), "+2.000 personas ya lo tienen", 1.6, 5.4, Box(60, 1580, 960, 90), "Montserrat", 50,
          "#FFD23F", weight=800, anim_in=tanim("fade", duration=0.4), name="Subtítulo")
    song(t, "epic", 6, 0.8)
    return t


def detalle_lupa():
    t = tall("r-detalle-lupa", "Detalle con lupa", "Magnifier detail", "product", 8.0, order=3305,
             tags=["detalle", "lupa", "calidad", "producto", "acabado"], thumb_at=4.4, background="#F5F0EB")
    photo_bg(t, "handmade-02", s1=1.04, label="Foto del producto")
    host = t.track("video", "Lupa")
    clip = t.photo(host, "handmade-02", 1.0, 7.0, t.full, [(0, {"s": 2.2, "dx": 200, "dy": 200}, "inout"),
                                                          (3.0, {"s": 2.2, "dx": -200, "dy": -100}, "inout"),
                                                          (7.0, {"s": 2.2, "dx": 100, "dy": 250})],
                   label="Foto del producto", reuse="p1")
    path = keys([(0, 0.5, "inout"), (3.0, 0.4, "inout"), (7.0, 0.55)])
    # A round lens: 0.45 of the width is 486 px, the same 486 px are 0.253 of the height.
    t.mask(host, clip, "ellipse", feather=4, w=0.45, h=0.253,
           keyframes={"x": path, "y": keys([(0, 0.45, "inout"), (3.0, 0.55, "inout"), (7.0, 0.5)])})
    ring(t, t.track("shape", "Aro"), "#FFFFFF", 14, 1.0, 7.0, centered(540, 864, 486, 486),
         [(0, {"dx": 0, "dy": 0}, "inout"), (3.0, {"dx": -108, "dy": 192}, "inout"), (7.0, {"dx": 54, "dy": 96})])
    label(t, t.track("text", "Título"), "mira este acabado 🔍", 0.2, 7.8, Box(60, 150, 960, 140), "DM Sans", 84, "#FFFFFF",
          weight=800, box_bg=("#000000", 0.55), box_pad=20, box_radius=20, anim_in=tanim("pop", duration=0.3), name="Título")
    song(t, "jazz", 2, 0.75)
    return t


def resena_estrellas():
    t = tall("r-resena-estrellas", "Reseña con estrellas", "Star review", "product", 8.0, order=3306,
             tags=["reseña", "estrellas", "opinión", "cliente", "producto"], thumb_at=5.0, background="#FFF8E7")
    bg(t, "#FFF8E7")
    framed(t, "skincare-03", 0.3, 7.7, Box(140, 200, 800, 820), [(0, {"s": 0.8}, "back"), (0.5, {})], border=16, radius=30,
           label="Foto del producto")
    for k in range(5):
        label(t, t.track("text", "Estrella"), "★", 1.0 + k * 0.15, 7.0 - k * 0.15, centered(260 + k * 140, 1120, 140, 140),
              "Inter", 120, "#F4A100", weight=400, editable=False, motion=[(0, {"s": 0.0}, "back"), (0.3, {})])
    rrect(t, t.track("shape", "Burbuja"), "#FFFFFF", 1.8, 6.2, Box(80, 1240, 920, 420), 40, pop(0, 0.4, 0.8),
          layers=[shadow("#000000", 0, 10, 26, 0.15), fill("#FFFFFF"), no_stroke()])
    label(t, t.track("text", "Reseña"), "«La uso todas las noches y mi piel cambió. ¡La recomiendo!»", 2.0, 6.0,
          Box(130, 1280, 820, 260), "Lora", 58, "#2D2A26", weight=500, italic=True, line=1.2,
          anim_in=tanim("typewriter", duration=1.4, unit="character"), name="Reseña")
    label(t, t.track("text", "Cliente"), "— Paula, compra verificada ✓", 3.6, 4.4, Box(130, 1560, 820, 70), "Montserrat", 38,
          "#8C6B2F", weight=700, anim_in=tanim("fade", duration=0.3), name="Cliente")
    song(t, "calm", 2, 0.75)
    return t


def comparar_tamanos():
    t = tall("r-comparar-tamanos", "Comparación de tamaños", "Size comparison", "product", 8.0, order=3307,
             tags=["tamaños", "medidas", "comparación", "producto", "elige"], thumb_at=4.6, background="#EEF2F6")
    bg(t, "#EEF2F6")
    sizes = [("S", 260, "30 ml"), ("M", 360, "50 ml"), ("L", 470, "100 ml")]
    x = 60
    for i, (n, w, cap) in enumerate(sizes):
        at = 0.4 + i * 0.6
        box = Box(x, 1300 - w * 1.5, w, w * 1.5)
        t.photo(t.track("video", f"Talla {n}"), "skincare-02", at, 8.0 - at, box, [(0, {"sy": 0.0, "dy": w * 0.75}, "back"),
                                                                                (0.5, {})], label="Foto del producto",
                reuse="p1" if i else None)
        label(t, t.track("text", "Talla"), n, at + 0.3, 7.7 - at, Box(x, 1340, w, 140), "Anton", 120, "#264653", weight=400,
              anim_in=tanim("pop", duration=0.3), name=f"Talla {i + 1}")
        label(t, t.track("text", "Medida"), cap, at + 0.4, 7.6 - at, Box(x, 1480, w, 70), "Montserrat", 40, "#6B7280", weight=700,
              anim_in=tanim("fade", duration=0.3), name=f"Medida {i + 1}")
        x += w + 40
    t.solid(t.track("shape", "Base"), "#264653", 0.2, 7.8, Box(40, 1300, 1000, 8))
    label(t, t.track("text", "Título"), "elige tu tamaño", 0.2, 7.8, Box(60, 150, 960, 140), "DM Sans", 92, "#264653",
          weight=800, anim_in=tanim("fade", duration=0.4), name="Título")
    song(t, "upbeat", 4, 0.75)
    return t


def agotado_vuelta():
    t = tall("r-agotado-vuelta", "Agotado → ¡de vuelta!", "Back in stock", "product", 7.0, order=3308,
             tags=["agotado", "de vuelta", "reposición", "stock", "producto"], thumb_at=4.6, background="#111111")
    photo_bg(t, "handmade-01", s1=1.06, label="Foto del producto",
             effects=[effect("color.basic", animated={"saturation": keys([(0, -1.0, "hold"), (3.0, 0.0)])})])
    t.solid(t.track("shape", "Gris"), "#000000", 0, 3.0, opacity=keys([(0, 0.55)]))
    label(t, t.track("text", "Agotado"), "AGOTADO", 0.2, 2.8, Box(60, 760, 960, 260), "Anton", 220, "#FFFFFF", weight=400,
          spacing=8, layers=[stroke(8, "#E10600"), fill("#E10600")], anim_in=tanim("stamp", duration=0.3),
          rotation=keys([(0, -10)]), anim_out=tanim("fade", duration=0.2), name="Antes")
    flash(t, 3.0, 0.35, peak=0.9)
    label(t, t.track("text", "Vuelta"), "¡DE VUELTA!", 3.1, 3.9, Box(60, 700, 960, 300), "Anton", 190, "#FFFFFF", weight=400,
          spacing=6, layers=[shadow("#00C2A8", 0, 12, 0, 1.0), fill("#FFFFFF")], anim_in=tanim("stamp", duration=0.3),
          name="Después")
    label(t, t.track("text", "Sub"), "pocas unidades · corre", 3.6, 3.4, Box(60, 1040, 960, 100), "Montserrat", 56, "#FFFFFF",
          weight=800, box_bg=("#00C2A8", 1.0), box_pad=18, box_radius=16, anim_in=tanim("pop", duration=0.3), name="Subtítulo")
    song(t, "electro", 0, 0.85)
    return t


def beneficios():
    t = tall("r-beneficios", "Lista de beneficios", "Benefits list", "product", 9.0, order=3309,
             tags=["beneficios", "ventajas", "producto", "lista", "por qué"], thumb_at=6.6, background="#F0FDF4")
    bg(t, "#F0FDF4")
    circle_photo(t, "skincare-02", 0.3, 8.7, centered(540, 520, 580, 580), pop(0, 0.5), ring_colour="#16A34A", ring_width=12,
                 label="Foto del producto")
    benefits = ["100% natural", "sin perfume", "dura 3 meses", "envío en 24 h"]
    for i, b in enumerate(benefits):
        at = 1.4 + i * 0.9
        _card(t, "#FFFFFF", at, 9.0 - at, Box(120, 900 + i * 200, 840, 160), 30, slide_in(dx=-1000, length=0.4))
        t.solid(t.track("shape", "Check"), "#16A34A", at + 0.2, 8.8 - at, centered(210, 980 + i * 200, 90, 90), pop(0, 0.3),
                kind="ellipse")
        label(t, t.track("text", "Check"), "✓", at + 0.2, 8.8 - at, centered(210, 980 + i * 200, 90, 90), "Inter", 56, "#FFFFFF",
              weight=800, editable=False, motion=pop(0, 0.3))
        label(t, t.track("text", "Beneficio"), b, at + 0.2, 8.8 - at, Box(290, 900 + i * 200, 640, 160), "DM Sans", 64, "#14532D",
              weight=800, align="left", name=f"Beneficio {i + 1}")
    song(t, "upbeat", 5, 0.75)
    return t


# --- Text formats -------------------------------------------------------------------------------

def hilo_post():
    t = tall("r-hilo-post", "Hilo de publicaciones", "Post thread", "text", 10.0, order=3310,
             tags=["hilo", "publicación", "post", "opinión", "texto"], thumb_at=7.0, background="#F7F9F9")
    bg(t, "#F7F9F9")
    posts = ["Cosas que aprendí al cumplir 30: 🧵", "1. Dormir bien lo cambia todo.", "2. Decir «no» también es cuidarte.",
             "3. Tus amigos de verdad se quedan."]
    for i, p in enumerate(posts):
        at = 0.3 + i * 1.8
        y = 220 + i * 380
        _card(t, "#FFFFFF", at, 10.0 - at, Box(60, y, 960, 340), 30, slide_in(dy=200, length=0.4), shadow_alpha=0.1)
        circle_photo(t, "selfie-02", at, 10.0 - at, centered(150, y + 90, 100, 100), slide_in(dy=200, length=0.4),
                     label="Tu foto", reuse="p1" if i else None)
        label(t, t.track("text", "Usuario"), "Valeria  @valeria · 2 h", at + 0.1, 9.9 - at, Box(220, y + 50, 760, 70), "Roboto",
              36, "#536471", weight=700, align="left", editable=i == 0, name="Usuario")
        label(t, t.track("text", "Post"), p, at + 0.2, 9.8 - at, Box(100, y + 150, 880, 170), "Roboto", 54, "#0F1419",
              weight=500, align="left", valign="top", line=1.2, anim_in=tanim("typewriter", duration=0.8, unit="character"),
              name=f"Publicación {i + 1}")
    song(t, "calm", 4, 0.7)
    return t


def nota_celular():
    t = tall("r-nota-celular", "Nota del celular", "Phone note", "text", 10.0, order=3311,
             tags=["notas", "nota", "celular", "carta", "mensaje"], thumb_at=9.4, background="#FFFFFF")
    bg(t, "#FFFFFF")
    t.solid(t.track("shape", "Barra"), "#F2F2F7", 0, 10.0, Box(0, 0, 1080, 240))
    label(t, t.track("text", "Volver"), "‹ Notas", 0, 10.0, Box(40, 130, 400, 80), "Inter", 46, "#E0A800", weight=500,
          align="left", editable=False)
    label(t, t.track("text", "Fecha"), "16 de octubre de 2026, 23:41", 0, 10.0, Box(60, 280, 960, 60), "Inter", 34, "#8E8E93",
          weight=500, editable=False)
    label(t, t.track("text", "Título"), "para mí en 5 años", 0.4, 9.6, Box(60, 370, 960, 120), "Inter", 76, "#000000",
          weight=800, align="left", anim_in=tanim("typewriter", duration=0.8, unit="character"), name="Título")
    label(t, t.track("text", "Nota"), "ojalá sigas riéndote fuerte,\nque hayas visto el mar del norte\ny que no te hayas olvidado\nde lo mucho que te costó llegar.",
          1.4, 8.6, Box(60, 520, 960, 900), "Inter", 58, "#1C1C1E", weight=400, align="left", valign="top", line=1.35,
          anim_in=tanim("typewriter", duration=5.0, unit="character", caret=True), name="Nota")
    song(t, "romantic", 1, 0.7)
    return t


def pregunta_respuesta():
    t = tall("r-pregunta-respuesta", "Pregunta y respuesta", "Q&A", "text", 9.0, order=3312,
             tags=["preguntas", "respuestas", "q&a", "seguidores", "dudas"], thumb_at=5.6, background="#5B5BD6")
    photo_bg(t, "creator-01", s1=1.06, label="Tu video")
    shade_bottom(t, 900, 0.6)
    _card(t, "#FFFFFF", 0.4, 8.6, Box(110, 260, 860, 360), 40, pop(0, 0.45, 0.6))
    t.solid(t.track("shape", "Cabecera"), "#5B5BD6", 0.4, 8.6, Box(110, 260, 860, 110), pop(0, 0.45, 0.6), radius=40,
            kind="rounded-rectangle")
    label(t, t.track("text", "Cabecera"), "hazme una pregunta", 0.5, 8.5, Box(110, 260, 860, 110), "DM Sans", 44, "#FFFFFF",
          weight=800, motion=pop(0, 0.45, 0.6), name="Cabecera")
    label(t, t.track("text", "Pregunta"), "¿cómo empezaste a editar videos?", 0.8, 8.2, Box(150, 390, 780, 210), "DM Sans", 58,
          "#111111", weight=700, line=1.15, anim_in=tanim("typewriter", duration=1.0, unit="character"), name="Pregunta")
    label(t, t.track("text", "Respuesta"), "con el celular y mucha paciencia 😅", 2.6, 6.4, Box(60, 1480, 960, 200), "DM Sans",
          72, "#FFFFFF", weight=800, line=1.15, layers=[shadow("#000000", 0, 4, 14, 0.6), fill("#FFFFFF")],
          anim_in=tanim("pop", duration=0.4, unit="word", stagger=0.08), name="Respuesta")
    song(t, "fun", 3, 0.75)
    return t


def tres_errores():
    t = tall("r-tres-errores", "3 errores que cometes", "3 mistakes you make", "text", 10.0, order=3313,
             tags=["errores", "consejos", "tips", "aprende", "evita"], thumb_at=7.6, background="#111111")
    bg(t, "#111111")
    label(t, t.track("text", "Título"), "3 errores al\nhacer café", 0.2, 9.8, Box(60, 140, 960, 340), "Archivo Black", 120,
          "#FFFFFF", weight=400, line=0.95, anim_in=tanim("slide-down", duration=0.4), name="Título")
    errors = ["usar agua hirviendo", "moler el café muy fino", "no limpiar la cafetera"]
    for i, e in enumerate(errors):
        at = 1.2 + i * 2.4
        y = 560 + i * 420
        t.solid(t.track("shape", "Cruz"), "#E10600", at, 10.0 - at, centered(170, y + 120, 150, 150), pop(0, 0.35), kind="ellipse")
        label(t, t.track("text", "Cruz"), "✕", at, 10.0 - at, centered(170, y + 120, 150, 150), "Inter", 90, "#FFFFFF",
              weight=900, editable=False, motion=pop(0, 0.35))
        t.photo(t.track("video", f"Foto {i + 1}"), ["coffee-03", "coffee-01", "coffee-04"][i], at + 0.1, 9.9 - at,
                Box(280, y, 340, 240), pop(0, 0.4), label=f"Foto {i + 1}")
        label(t, t.track("text", "Error"), e, at + 0.2, 9.8 - at, Box(650, y, 400, 240), "DM Sans", 48, "#FFFFFF", weight=800,
              align="left", line=1.1, anim_in=tanim("fade", duration=0.3), name=f"Error {i + 1}")
    song(t, "upbeat", 3, 0.75)
    return t


def mito_verdad():
    t = tall("r-mito-verdad", "¿Mito o verdad?", "Myth or truth?", "text", 9.0, order=3314,
             tags=["mito", "verdad", "dato", "curiosidad", "pregunta"], thumb_at=6.4, background="#FFE066")
    bg(t, "#FFE066")
    label(t, t.track("text", "Título"), "¿MITO O VERDAD?", 0.2, 8.8, Box(60, 140, 960, 160), "Luckiest Guy", 110, "#111111",
          weight=400, anim_in=tanim("stamp", duration=0.3), name="Título")
    _card(t, "#FFFFFF", 0.6, 8.4, Box(80, 380, 920, 520), 40)
    label(t, t.track("text", "Afirmación"), "«Los gatos siempre caen de pie.»", 0.9, 8.1, Box(130, 420, 820, 440), "DM Sans", 80,
          "#111111", weight=800, line=1.1, anim_in=tanim("typewriter", duration=1.0, unit="character"), name="Afirmación")
    for i, (txt, c) in enumerate([("MITO", "#E10600"), ("VERDAD", "#16A34A")]):
        pill(t, t.track("shape", "Opción"), c, 2.4, 6.6, Box(100 + i * 460, 1000, 420, 150), pop(0, 0.35),
             opacity=keys([(0, 1.0, "hold"), (4.0, 1.0 if i == 0 else 0.25)]))
        label(t, t.track("text", "Opción"), txt, 2.4, 6.6, Box(100 + i * 460, 1000, 420, 150), "Luckiest Guy", 84, "#FFFFFF",
              weight=400, name=f"Opción {i + 1}")
    label(t, t.track("text", "Explicación"), "casi siempre giran, ¡pero no siempre!", 4.2, 4.8, Box(60, 1220, 960, 200),
          "DM Sans", 66, "#111111", weight=700, line=1.15, anim_in=tanim("fade", duration=0.4), name="Explicación")
    t.photo(t.track("video", "Foto"), "puppy-01", 4.6, 4.4, Box(240, 1440, 600, 400), pop(0, 0.4), label="Foto")
    song(t, "fun", 2, 0.75)
    return t


def ranking_5_1():
    t = tall("r-ranking-5-1", "Ranking del 5 al 1", "Ranking 5 to 1", "text", 11.0, order=3315,
             tags=["ranking", "top 5", "favoritos", "lista", "número 1"], thumb_at=9.5, background="#0F0F0F")
    samples = ["food-03", "food-01", "restaurant-02", "h-food-02", "food-02"]
    names = ["empanadas", "tacos", "ramen", "pasta", "pizza"]
    for i, (s, n) in enumerate(zip(samples, names)):
        at = i * 2.2
        num = 5 - i
        t.photo(t.track("video", "Fotos") if i == 0 else ph, s, at, 2.2, t.full, kb(2.2, 1.08, 1.0), label=f"Puesto {num}")
        if i == 0:
            ph = t.tracks[-1]
        label(t, t.track("text", "Número"), f"#{num}", at + 0.1, 2.0, Box(60, 1300, 400, 300), "Anton", 260, "#FFD23F",
              weight=400, align="left", layers=[shadow("#000000", 0, 8, 20, 0.6), fill("#FFD23F")],
              anim_in=tanim("stamp", duration=0.3), editable=False)
        label(t, t.track("text", "Nombre"), n, at + 0.25, 1.85, Box(60, 1600, 960, 160), "Anton", 120, "#FFFFFF", weight=400,
              align="left", layers=[shadow("#000000", 0, 6, 16, 0.6), fill("#FFFFFF")], anim_in=tanim("slide-right", duration=0.3),
              name=f"Puesto {num}")
    label(t, t.track("text", "Título"), "TOP 5 COMIDAS", 0.0, 11.0, Box(60, 120, 960, 140), "Anton", 110, "#FFFFFF", weight=400,
          spacing=6, layers=[shadow("#000000", 0, 6, 16, 0.6), fill("#FFFFFF")], name="Título")
    flash(t, 8.8, 0.3)
    song(t, "upbeat", 1, 0.8)
    return t


def receta_texto():
    t = tall("r-receta-texto", "Receta en texto", "Text recipe", "text", 10.0, order=3316,
             tags=["receta", "pasos", "cocina", "fácil", "texto"], thumb_at=7.4, background="#FFF6E9")
    bg(t, "#FFF6E9")
    t.photo(t.track("video", "Plato"), "cooking-03", 0, 10.0, Box(0, 0, 1080, 760), kb(10.0, 1.0, 1.06), label="Foto del plato")
    label(t, t.track("text", "Título"), "Panqueques de avena", 0.3, 9.7, Box(60, 800, 960, 140), "Lobster", 96, "#C2410C",
          weight=400, anim_in=tanim("fade", duration=0.4), name="Receta")
    steps = ["mezcla 1 taza de avena y 1 banana", "agrega 2 huevos y canela", "cocina 2 min por lado", "¡sirve con miel!"]
    for i, s in enumerate(steps):
        at = 1.2 + i * 1.6
        t.solid(t.track("shape", "Número"), "#C2410C", at, 10.0 - at, centered(120, 1030 + i * 200, 90, 90), pop(0, 0.3),
                kind="ellipse")
        label(t, t.track("text", "Número"), str(i + 1), at, 10.0 - at, centered(120, 1030 + i * 200, 90, 90), "Montserrat", 50,
              "#FFFFFF", weight=800, editable=False, motion=pop(0, 0.3))
        label(t, t.track("text", "Paso"), s, at + 0.1, 9.9 - at, Box(200, 980 + i * 200, 840, 110), "Montserrat", 50, "#292524",
              weight=600, align="left", line=1.15, anim_in=tanim("fade", duration=0.3), name=f"Paso {i + 1}")
    song(t, "jazz", 1, 0.75)
    return t


def frase_subrayada():
    t = tall("r-frase-subrayada", "Frase subrayada", "Underlined quote", "text", 8.0, order=3317,
             tags=["frase", "subrayado", "motivación", "cita", "reflexión"], thumb_at=5.4, background="#FAF7F2")
    bg(t, "#FAF7F2")
    t.solid(t.track("shape", "Marcador"), "#FFE066", 2.2, 5.8, Box(110, 960, 720, 80), [(0, {"sx": 0.0, "dx": -360}, "out"),
                                                                                      (0.6, {})], alpha=0.85,
            rotation=keys([(0, -1)]))
    label(t, t.track("text", "Frase"), "No tienes que ser perfecta para empezar.", 0.3, 7.7, Box(80, 560, 920, 640),
          "DM Serif Display", 128, "#1A1A1A", weight=400, line=1.05, anim_in=tanim("rise-by-word", duration=0.4, unit="word",
          stagger=0.12), name="Frase")
    label(t, t.track("text", "Firma"), "@tuusuario", 2.8, 5.2, Box(80, 1300, 920, 80), "DM Sans", 44, "#6B6B6B", weight=600,
          anim_in=tanim("fade", duration=0.4), name="Firma")
    song(t, "calm", 2, 0.7)
    return t


def lista_pendientes():
    t = tall("r-lista-pendientes", "Lista de pendientes", "To-do list", "text", 10.0, order=3318,
             tags=["pendientes", "to do", "lista", "organización", "productividad"], thumb_at=8.0, background="#FFFDF5")
    bg(t, "#FFFDF5")
    for k in range(20):
        t.solid(t.track("shape", "Renglón") if k == 0 else rl, "#D9E3EA", 0, 10.0, Box(0, 300 + k * 84, 1080, 3))
        if k == 0:
            rl = t.tracks[-1]
    label(t, t.track("text", "Título"), "hoy:", 0.2, 9.8, Box(80, 120, 960, 160), "Caveat", 140, "#1D3557", weight=700,
          align="left", anim_in=tanim("typewriter", duration=0.5, unit="character"), name="Título")
    tasks = ["regar las plantas 🌱", "llamar a la abuela", "salir a caminar", "terminar el libro", "dormir temprano"]
    for i, task in enumerate(tasks):
        at = 0.8 + i * 1.5
        y = 360 + i * 220
        outline(t, t.track("shape", "Casilla"), "#1D3557", 6, at, 10.0 - at, Box(80, y, 90, 90), radius=16, kind="rounded-rectangle")
        label(t, t.track("text", "Tarea"), task, at, 10.0 - at, Box(200, y - 10, 840, 110), "Caveat", 84, "#1D3557", weight=700,
              align="left", anim_in=tanim("fade", duration=0.3), name=f"Tarea {i + 1}")
        label(t, t.track("text", "Check"), "✓", at + 0.7, 9.3 - at, Box(80, y - 30, 120, 120), "Inter", 110, "#16A34A", weight=900,
              editable=False, anim_in=tanim("pop", duration=0.25))
        t.solid(t.track("shape", "Tachado"), "#1D3557", at + 0.8, 9.2 - at, Box(200, y + 42, 600, 6),
                [(0, {"sx": 0.0, "dx": -300}, "out"), (0.3, {})])
    song(t, "upbeat", 5, 0.7)
    return t


def signos():
    t = tall("r-signos", "Signos del zodiaco", "Star signs", "text", 9.0, order=3319,
             tags=["signos", "zodiaco", "horóscopo", "astrología", "estrellas"], thumb_at=5.4, background="#0B0A1F")
    bg_gradient(t, [(0, "#1A1240"), (1, "#05040F")], angle=90)
    dots(t, ["#FFFFFF", "#C9B6FF"], 60, 0, 9.0, seed=3319, size=(3, 9), kinds=("star", "ellipse"), drift=10)
    ring(t, t.track("shape", "Rueda"), "#C9B6FF", 3, 0.2, 8.8, centered(540, 760, 760, 760),
         rotation=keys([(0, 0, "linear"), (8.8, 40)]), alpha=0.6)
    glyphs = "♈♉♊♋♌♍♎♏♐♑♒♓"
    for k, g in enumerate(glyphs):
        a = k / 12 * math.tau - math.pi / 2
        label(t, t.track("text", "Signo") if k % 6 == 0 else sg, g, 0.2 + k * 0.08, 8.8 - k * 0.08,
              centered(540 + math.cos(a) * 380, 760 + math.sin(a) * 380, 110, 110), "Inter", 72, "#E9DDFF", weight=400,
              editable=False, motion=pop(0, 0.3))
        if k % 6 == 0:
            sg = t.tracks[-1]
    label(t, t.track("text", "Pregunta"), "los signos cuando\nles dicen «tranqui»:", 1.4, 7.6, Box(60, 1220, 960, 260), "DM Sans",
          76, "#FFFFFF", weight=800, line=1.1, anim_in=tanim("fade", duration=0.4), name="Texto")
    label(t, t.track("text", "Remate"), "Aries: 🔥🔥🔥", 2.8, 6.2, Box(60, 1520, 960, 140), "DM Sans", 92, "#FFB4A2", weight=900,
          anim_in=tanim("pop", duration=0.3), name="Remate")
    song(t, "fantasy", 2, 0.75)
    return t


def dia_x_de():
    t = tall("r-dia-x-de", "Día X de…", "Day X of…", "text", 7.0, order=3320,
             tags=["día", "reto", "diario", "progreso", "serie"], thumb_at=3.6, background="#000000")
    photo_bg(t, "hike-03", s1=1.08, label="Tu video")
    shade_top(t, 700, 0.7)
    label(t, t.track("text", "Día"), "DÍA 47", 0.2, 6.8, Box(60, 140, 960, 260), "Anton", 240, "#FFFFFF", weight=400, spacing=6,
          anim_in=tanim("stamp", duration=0.3), name="Día")
    label(t, t.track("text", "Reto"), "de caminar 10 km cada día", 0.6, 6.4, Box(60, 420, 960, 120), "DM Sans", 64, "#FFE066",
          weight=800, anim_in=tanim("fade", duration=0.4), name="Reto")
    rrect(t, t.track("shape", "Barra"), "#FFFFFF", 0.8, 6.2, Box(80, 1760, 920, 30), 15, alpha=0.3)
    rrect(t, t.track("shape", "Barra"), "#FFE066", 0.8, 6.2, Box(80, 1760, 920 * 47 / 100, 30), 15,
          [(0, {"sx": 0.0, "dx": -216}, "out"), (1.2, {})])
    label(t, t.track("text", "Meta"), "47 / 100", 1.6, 5.4, Box(60, 1660, 960, 90), "DM Sans", 50, "#FFFFFF", weight=800,
          align="right", anim_in=tanim("fade", duration=0.3), name="Avance")
    song(t, "epic", 2, 0.8)
    return t


def trivia():
    t = tall("r-trivia", "Trivia de opción múltiple", "Multiple-choice trivia", "text", 10.0, order=3321,
             tags=["trivia", "quiz", "pregunta", "juego", "respuestas"], thumb_at=4.6, background="#3A0CA3")
    bg_gradient(t, [(0, "#4361EE"), (1, "#3A0CA3")], angle=135)
    label(t, t.track("text", "Pregunta"), "¿Cuál es el planeta más grande?", 0.3, 9.7, Box(60, 200, 960, 300), "Fredoka", 96,
          "#FFFFFF", weight=700, line=1.1, anim_in=tanim("pop", duration=0.4, unit="word", stagger=0.08), name="Pregunta")
    options = ["A. Marte", "B. Júpiter", "C. Saturno", "D. Tierra"]
    right = 1
    for i, o in enumerate(options):
        at = 1.4 + i * 0.3
        y = 620 + i * 210
        pill(t, t.track("shape", "Opción"), "#FFFFFF", at, 10.0 - at, Box(100, y, 880, 160), slide_in(dx=1000, length=0.35),
             opacity=keys([(0, 1.0, "hold"), (6.0 - at, 1.0 if i == right else 0.35)]))
        if i == right:
            pill(t, t.track("shape", "Correcta"), "#16A34A", 6.0, 4.0, Box(100, y, 880, 160), pop(0, 0.35, 0.9))
        label(t, t.track("text", "Opción"), o, at, 10.0 - at, Box(150, y, 800, 160), "Fredoka", 64, "#3A0CA3",
              weight=700, align="left", name=f"Opción {i + 1}")
    nums = t.track("text", "Tiempo")
    _count(t, nums, ["5", "4", "3", "2", "1"], 1.0, 1.0, centered(540, 1560, 300, 200), "Fredoka", 160, "#FFD166")
    label(t, nums, "¡Júpiter!", 6.0, 4.0, centered(540, 1560, 900, 200), "Fredoka", 120, "#FFD166", weight=800,
          anim_in=tanim("pop", duration=0.3), name="Respuesta")
    song(t, "fun", 3, 0.75)
    return t


def frase_pelicula():
    t = tall("r-frase-pelicula", "Frase de película", "Film line", "text", 8.0, order=3322,
             tags=["frase", "película", "cine", "subtítulo", "escena"], thumb_at=4.6, background="#000000")
    photo_bg(t, "sunset-04", s1=1.06, label="Tu video", effects=[effect("cinematic_grade", strength=0.7)])
    letterbox(t, 1.0)
    label(t, t.track("text", "Subtítulo"), "— Lo nuestro no fue un accidente.", 1.0, 3.0, Box(60, 1440, 960, 160),
          "Roboto", 58, "#FFF4C2", weight=500, layers=[shadow("#000000", 0, 3, 8, 0.9), fill("#FFF4C2")],
          anim_in=tanim("fade", duration=0.2), anim_out=tanim("fade", duration=0.2), name="Diálogo 1")
    label(t, t.track("text", "Subtítulo"), "— Fue lo mejor que nos pasó.", 4.2, 3.4, Box(60, 1440, 960, 160), "Roboto", 58,
          "#FFF4C2", weight=500, layers=[shadow("#000000", 0, 3, 8, 0.9), fill("#FFF4C2")],
          anim_in=tanim("fade", duration=0.2), name="Diálogo 2")
    grain(t, 0.2)
    song(t, "cine", 3, 0.8)
    return t


def consejo_finanzas():
    t = tall("r-consejo-finanzas", "Consejo de dinero", "Money tip", "text", 9.0, order=3323,
             tags=["finanzas", "dinero", "ahorro", "consejo", "presupuesto"], thumb_at=6.0, background="#052E16")
    bg_gradient(t, [(0, "#064E3B"), (1, "#022C22")], angle=90)
    label(t, t.track("text", "Antetítulo"), "CONSEJO DE DINERO 💸", 0.2, 8.8, Box(60, 160, 960, 90), "Plus Jakarta Sans", 52,
          "#6EE7B7", weight=800, spacing=4, anim_in=tanim("fade", duration=0.3), name="Antetítulo")
    label(t, t.track("text", "Título"), "La regla\n50 / 30 / 20", 0.5, 8.5, Box(60, 270, 960, 360), "Plus Jakarta Sans", 120,
          "#FFFFFF", weight=800, line=1.0, anim_in=tanim("rise-by-word", duration=0.4, unit="word", stagger=0.12), name="Título")
    parts = [("50%", "necesidades", "#34D399", 0.5), ("30%", "gustos", "#FBBF24", 0.3), ("20%", "ahorro", "#60A5FA", 0.2)]
    for i, (p, n, c, f) in enumerate(parts):
        at = 2.0 + i * 0.8
        y = 760 + i * 300
        rrect(t, t.track("shape", "Barra"), c, at, 9.0 - at, Box(80, y, 920 * f / 0.5 * 0.9, 120), 30,
              [(0, {"sx": 0.0, "dx": -920 * f / 0.5 * 0.45}, "out"), (0.6, {})])
        label(t, t.track("text", "Porcentaje"), p, at + 0.2, 8.8 - at, Box(100, y, 300, 120), "Plus Jakarta Sans", 70, "#022C22",
              weight=800, align="left", editable=False)
        label(t, t.track("text", "Uso"), n, at + 0.3, 8.7 - at, Box(80, y + 130, 920, 80), "Plus Jakarta Sans", 50, "#FFFFFF",
              weight=700, align="left", anim_in=tanim("fade", duration=0.3), name=f"Uso {i + 1}")
    song(t, "upbeat", 3, 0.75)
    return t


def palabra_del_dia():
    t = tall("r-palabra-del-dia", "Palabra del día", "Word of the day", "text", 8.0, order=3324,
             tags=["palabra del día", "vocabulario", "idioma", "significado", "aprende"], thumb_at=4.6, background="#FDF6EC")
    bg(t, "#FDF6EC")
    label(t, t.track("text", "Antetítulo"), "PALABRA DEL DÍA", 0.2, 7.8, Box(60, 300, 960, 80), "Montserrat", 46, "#B5525F",
          weight=800, spacing=12, anim_in=tanim("fade", duration=0.4), name="Antetítulo")
    label(t, t.track("text", "Palabra"), "Serendipia", 0.5, 7.5, Box(60, 420, 960, 220), "Playfair Display", 150, "#1A1A1A",
          weight=800, anim_in=tanim("blur-in", duration=0.6), name="Palabra")
    label(t, t.track("text", "Tipo"), "sustantivo · se-ren-di-pia", 1.2, 6.8, Box(60, 650, 960, 80), "Lora", 48, "#8C6B2F",
          weight=500, italic=True, anim_in=tanim("fade", duration=0.4), name="Pronunciación")
    line(t, t.track("shape", "Línea"), "#B5525F", 1.4, 6.6, centered(540, 770, 200, 4), grow="c", length=0.5)
    label(t, t.track("text", "Significado"), "un hallazgo valioso que llega por casualidad, cuando buscabas otra cosa",
          1.8, 6.2, Box(100, 820, 880, 400), "Lora", 62, "#2D2A26", weight=500, line=1.3,
          anim_in=tanim("rise-by-word", duration=0.35, unit="word", stagger=0.05), name="Significado")
    song(t, "calm", 4, 0.7)
    return t


def traduccion():
    t = tall("r-traduccion", "¿Cómo se dice?", "How do you say it?", "text", 9.0, order=3325,
             tags=["traducción", "idiomas", "inglés", "aprender", "frases"], thumb_at=6.0, background="#1E3A8A")
    bg_gradient(t, [(0, "#2547A8"), (1, "#152A63")], angle=135)
    label(t, t.track("text", "Título"), "¿cómo se dice…?", 0.2, 8.8, Box(60, 160, 960, 140), "Fredoka", 96, "#FFD166",
          weight=700, anim_in=tanim("pop", duration=0.4), name="Título")
    pairs = [("🇪🇸", "Tengo hambre"), ("🇬🇧", "I'm hungry"), ("🇫🇷", "J'ai faim"), ("🇮🇹", "Ho fame")]
    for i, (flag, phrase) in enumerate(pairs):
        at = 0.8 + i * 1.6
        y = 400 + i * 330
        _card(t, "#FFFFFF", at, 9.0 - at, Box(80, y, 920, 270), 40, slide_in(dx=1000 * (-1) ** i, length=0.4))
        label(t, t.track("text", "Bandera"), flag, at, 9.0 - at, centered(200, y + 135, 160, 160), "Inter", 100, "#000000",
              weight=400, editable=False, motion=slide_in(dx=1000 * (-1) ** i, length=0.4))
        label(t, t.track("text", "Frase"), phrase, at + 0.2, 8.8 - at, Box(310, y, 660, 270), "Fredoka", 72, "#1E3A8A",
              weight=700, align="left", anim_in=tanim("fade", duration=0.3), name=f"Frase {i + 1}")
    song(t, "world", 2, 0.75)
    return t


def cosas_felices():
    t = tall("r-cosas-felices", "Cosas que me hacen feliz", "Things that make me happy", "text", 10.0, order=3326,
             tags=["cosas felices", "gratitud", "pequeñas cosas", "aesthetic", "lista"], thumb_at=7.0, background="#FFF1E6")
    things = [("coffee-01", "el primer café"), ("reading-01", "un libro nuevo"), ("puppy-03", "mi perro feliz"),
              ("sunset-01", "los atardeceres")]
    for i, (s, txt) in enumerate(things):
        at = i * 2.5
        t.photo(t.track("video", "Fotos") if i == 0 else ph, s, at, 2.5, t.full, kb(2.5, 1.0, 1.06), label=f"Foto {i + 1}")
        if i == 0:
            ph = t.tracks[-1]
        label(t, t.track("text", "Cosa"), txt, at + 0.3, 2.1, Box(60, 1500, 960, 180), "Caveat", 130, "#FFFFFF", weight=700,
              layers=[shadow("#000000", 0, 4, 14, 0.6), fill("#FFFFFF")], anim_in=tanim("typewriter", duration=0.6, unit="character"),
              anim_out=tanim("fade", duration=0.2), name=f"Cosa {i + 1}")
    label(t, t.track("text", "Título"), "cosas que me hacen feliz ☺", 0.0, 10.0, Box(60, 140, 960, 140), "Caveat", 96, "#FFFFFF",
          weight=700, layers=[shadow("#000000", 0, 4, 14, 0.5), fill("#FFFFFF")], name="Título")
    song(t, "calm", 4, 0.75)
    return t


def pensamiento_dia():
    t = tall("r-pensamiento-dia", "Pensamiento del día", "Thought of the day", "text", 8.0, order=3327,
             tags=["pensamiento", "reflexión", "fe", "esperanza", "frase del día"], thumb_at=5.0, background="#0E1525")
    photo_bg(t, "sunset-02", s1=1.06, label="Fondo")
    shade_full(t, 0.45, colour="#0E1525")
    label(t, t.track("text", "Antetítulo"), "PENSAMIENTO DEL DÍA", 0.3, 7.7, Box(60, 500, 960, 80), "Montserrat", 44, "#F6BD60",
          weight=800, spacing=10, anim_in=tanim("fade", duration=0.4), name="Antetítulo")
    label(t, t.track("text", "Frase"), "Lo que hoy siembras con paciencia, mañana te dará sombra.", 0.7, 7.3,
          Box(80, 620, 920, 600), "Cormorant Garamond", 104, "#FFFFFF", weight=600, italic=True, line=1.08,
          anim_in=tanim("rise-by-word", duration=0.5, unit="word", stagger=0.16, blur=8), name="Frase")
    song(t, "calm", 0, 0.7)
    return t


def poema_corto():
    t = tall("r-poema-corto", "Poema corto", "Short poem", "text", 10.0, order=3328,
             tags=["poema", "poesía", "versos", "amor", "texto"], thumb_at=8.0, background="#F4EFE6")
    bg(t, "#F4EFE6")
    verses = ["te escribo en la ventana", "con el dedo y el vapor", "y aunque el sol borre la letra", "se queda el calor"]
    for i, v in enumerate(verses):
        label(t, t.track("text", "Verso"), v, 0.5 + i * 1.8, 9.5 - i * 1.8, Box(80, 560 + i * 170, 920, 150),
              "Cormorant Garamond", 84, "#2B2B2B", weight=500, italic=True, align="left",
              anim_in=tanim("blur-in", duration=0.8, blur=10), name=f"Verso {i + 1}")
    line(t, t.track("shape", "Línea"), "#B08D57", 7.8, 2.2, Box(84, 1290, 160, 4), length=0.5)
    label(t, t.track("text", "Firma"), "— M.", 8.0, 2.0, Box(80, 1320, 920, 90), "Cormorant Garamond", 64, "#B08D57",
          weight=600, align="left", anim_in=tanim("fade", duration=0.5), name="Firma")
    grain(t, 0.12)
    song(t, "romantic", 0, 0.7)
    return t


def reto_30_dias():
    t = tall("r-reto-30-dias", "Reto de 30 días", "30-day challenge", "text", 9.0, order=3329,
             tags=["reto", "30 días", "hábitos", "challenge", "calendario"], thumb_at=7.0, background="#FFFFFF")
    bg(t, "#FFFFFF")
    label(t, t.track("text", "Título"), "RETO DE 30 DÍAS", 0.2, 8.8, Box(60, 140, 960, 140), "Archivo Black", 96, "#111111",
          weight=400, anim_in=tanim("slide-down", duration=0.3), name="Título")
    label(t, t.track("text", "Hábito"), "beber 2 litros de agua", 0.5, 8.5, Box(60, 290, 960, 90), "DM Sans", 56, "#2563EB",
          weight=800, anim_in=tanim("fade", duration=0.3), name="Hábito")
    g = 20
    cw = (1080 - 160 - 5 * g) / 6
    for k in range(30):
        r, c = divmod(k, 6)
        x, y = 80 + c * (cw + g), 450 + r * (cw + g)
        rrect(t, t.track("shape", "Día") if k % 10 == 0 else dt, "#F1F5F9", 0.3, 8.7, Box(x, y, cw, cw), 24)
        if k % 10 == 0:
            dt = t.tracks[-1]
    for k in range(18):
        r, c = divmod(k, 6)
        x, y = 80 + c * (cw + g), 450 + r * (cw + g)
        at = 1.0 + k * 0.25
        t.solid(t.track("shape", "Hecho") if k % 9 == 0 else hd, "#2563EB", at, 9.0 - at, Box(x, y, cw, cw), pop(0, 0.25),
                radius=24, kind="rounded-rectangle")
        if k % 9 == 0:
            hd = t.tracks[-1]
    label(t, t.track("text", "Avance"), "18 de 30 ✓", 5.6, 3.4, Box(60, 1440, 960, 160), "Archivo Black", 110, "#111111",
          weight=400, anim_in=tanim("pop", duration=0.3), name="Avance")
    song(t, "upbeat", 4, 0.75)
    return t


# --- Intros ---------------------------------------------------------------------------------------

def bienvenidos_canal():
    t = tall("r-bienvenidos-canal", "Bienvenidos a mi canal", "Welcome to my channel", "intro", 6.0, order=3330,
             tags=["bienvenidos", "canal", "intro", "creador", "suscríbete"], thumb_at=3.6, background="#FF5A5F")
    bg_gradient(t, [(0, "#FF5A5F"), (1, "#FF9A8B")], angle=135)
    circle_photo(t, "creator-02", 0.2, 5.8, centered(540, 700, 640, 640), pop(0, 0.5), ring_colour="#FFFFFF", ring_width=16,
                 label="Tu foto")
    label(t, t.track("text", "Hola"), "¡bienvenidos\na mi canal!", 0.8, 5.2, Box(60, 1100, 960, 360), "Fredoka", 120, "#FFFFFF",
          weight=700, line=1.0, anim_in=tanim("bounce", duration=0.5, unit="word", stagger=0.12), name="Saludo")
    label(t, t.track("text", "Tema"), "recetas fáciles todas las semanas", 1.6, 4.4, Box(60, 1480, 960, 90), "Fredoka", 54,
          "#FFF1E6", weight=600, anim_in=tanim("fade", duration=0.4), name="Tema")
    song(t, "fun", 1, 0.8)
    return t


def nuevo_video():
    t = tall("r-nuevo-video", "¡Nuevo video!", "New video!", "intro", 5.0, order=3331,
             tags=["nuevo video", "estreno", "aviso", "youtube", "link"], thumb_at=2.6, background="#111111")
    photo_bg(t, "creator-04", s1=1.08, label="Miniatura del video")
    shade_full(t, 0.35)
    t.solid(t.track("shape", "Botón"), "#FFFFFF", 0.4, 4.6, centered(540, 880, 240, 240), pop(0, 0.4), kind="ellipse",
            layers=[shadow("#000000", 0, 10, 24, 0.4), fill("#FFFFFF"), no_stroke()])
    t.solid(t.track("shape", "Botón"), "#FF8C42", 0.5, 4.5, centered(555, 880, 80, 96), pop(0, 0.4), kind="triangle",
            rotation=keys([(0, 90)]))
    label(t, t.track("text", "Título"), "¡NUEVO VIDEO!", 0.8, 4.2, Box(60, 1080, 960, 200), "Anton", 150, "#FFFFFF", weight=400,
          spacing=6, layers=[shadow("#000000", 0, 6, 16, 0.6), fill("#FFFFFF")], anim_in=tanim("stamp", duration=0.3),
          name="Título")
    label(t, t.track("text", "Link"), "link en mi perfil ↑", 1.4, 3.6, Box(60, 1300, 960, 100), "Montserrat", 54, "#FFFFFF",
          weight=800, anim_in=tanim("fade", duration=0.3), anim_loop=tanim("float", amount=0.15, speed=1.0), name="Llamada")
    song(t, "electro", 1, 0.85)
    return t


def en_vivo_ahora():
    t = tall("r-en-vivo-ahora", "En vivo ahora", "Live now", "intro", 6.0, order=3332,
             tags=["en vivo", "live", "directo", "transmisión", "aviso"], thumb_at=3.0, background="#0E1020")
    photo_bg(t, "podcast-02", s1=1.06, label="Foto")
    shade_full(t, 0.4, colour="#0E1020")
    pill(t, t.track("shape", "Live"), "#FF2D55", 0.3, 5.7, centered(540, 720, 420, 140), pop(0, 0.4))
    label(t, t.track("text", "Live"), "● EN VIVO", 0.3, 5.7, centered(540, 720, 420, 140), "Outfit", 70, "#FFFFFF", weight=800,
          anim_loop=tanim("flicker", intensity=0.3, speed=1.5), name="Etiqueta")
    for k in range(3):
        ring(t, t.track("shape", "Onda"), "#FF2D55", 6, 0.5 + k * 0.6, 5.0 - k * 0.6, centered(540, 720, 480, 200),
             [(0, {"s": 1.0}, "out"), (1.8, {"s": 2.2})], opacity=keys([(0, 0.8), (1.8, 0.0)]))
    label(t, t.track("text", "Título"), "charla con ustedes\na las 20:00", 1.0, 5.0, Box(60, 900, 960, 300), "Outfit", 92,
          "#FFFFFF", weight=800, line=1.05, anim_in=tanim("rise", duration=0.4), name="Título")
    song(t, "electro", 2, 0.8)
    return t


# --- Endings --------------------------------------------------------------------------------------

def _end(id, es, en, order, tags, thumb_at=3.0, duration=5.0, bgc="#111111"):
    return tall(id, es, en, "outro", duration, order=order, tags=["cierre"] + tags, thumb_at=thumb_at, background=bgc)


def siguenos_mas():
    t = _end("r-siguenos-mas", "Sígueme para más", "Follow for more", 3333, ["sígueme", "seguir", "más contenido"],
             bgc="#FFFFFF")
    bg(t, "#FFFFFF")
    circle_photo(t, "selfie-01", 0.2, 4.8, centered(540, 760, 420, 420), pop(0, 0.5), ring_colour="#FF3B5C", ring_width=10,
                 label="Tu foto")
    pill(t, t.track("shape", "Botón"), "#FF3B5C", 0.6, 1.6, Box(290, 1040, 500, 130), pop(0, 0.35))
    pill(t, t.track("shape", "Botón"), "#E5E5E5", 2.2, 2.6, Box(290, 1040, 500, 130), [(0, {"s": 0.9}, "back"), (0.25, {})])
    label(t, t.track("text", "Botón"), "+ Seguir", 0.6, 1.6, Box(290, 1040, 500, 130), "Poppins", 60, "#FFFFFF", weight=700,
          name="Botón")
    label(t, t.track("text", "Botón"), "Siguiendo ✓", 2.2, 2.6, Box(290, 1040, 500, 130), "Poppins", 60, "#111111", weight=700,
          name="Botón pulsado")
    label(t, t.track("text", "Texto"), "para más ideas como esta", 0.8, 4.0, Box(60, 1240, 960, 100), "Poppins", 54, "#111111",
          weight=600, anim_in=tanim("fade", duration=0.4), name="Texto")
    dots(t, ["#FF3B5C", "#FF8FA3"], 14, 2.2, 2.6, seed=3333, size=(30, 60), kinds=("heart",), area=Box(240, 900, 600, 300),
         drift=300)
    song(t, "fun", 0, 0.8)
    return t


def guardalo():
    t = _end("r-guardalo", "Guárdalo para después", "Save it for later", 3334, ["guardar", "guárdalo", "favoritos"],
             bgc="#1D3557")
    bg(t, "#1D3557")
    t.solid(t.track("shape", "Marcador"), "#FFD166", 0.3, 4.7, centered(540, 760, 360, 480), [(0, {"sy": 0.0, "dy": -240}, "back"),
                                                                                         (0.5, {})], kind="banner")
    label(t, t.track("text", "Icono"), "🔖", 0.4, 4.6, centered(540, 760, 400, 400), "Inter", 280, "#FFFFFF", weight=400,
          editable=False, motion=[(0, {"s": 0.0}, "back"), (0.5, {})])
    label(t, t.track("text", "Texto"), "guárdalo\npara después", 0.9, 4.1, Box(60, 1100, 960, 320), "Poppins", 110, "#FFFFFF",
          weight=800, line=1.0, anim_in=tanim("rise", duration=0.4, unit="word", stagger=0.12), name="Texto")
    label(t, t.track("text", "Sub"), "te va a servir, créeme", 1.6, 3.4, Box(60, 1460, 960, 90), "Poppins", 52, "#A8DADC",
          weight=600, anim_in=tanim("fade", duration=0.4), name="Subtítulo")
    song(t, "upbeat", 1, 0.8)
    return t


def compartelo():
    t = _end("r-compartelo", "Compártelo con alguien", "Share it with someone", 3335, ["compartir", "etiqueta", "amigos"],
             bgc="#06D6A0")
    bg_gradient(t, [(0, "#06D6A0"), (1, "#118AB2")], angle=135)
    label(t, t.track("text", "Icono"), "📤", 0.3, 4.7, centered(540, 700, 400, 400), "Inter", 260, "#FFFFFF", weight=400,
          editable=False, motion=[(0, {"s": 0.0}, "back"), (0.5, {})], anim_loop=tanim("float", amount=0.08, speed=0.8))
    label(t, t.track("text", "Texto"), "mándaselo a\nquien necesita verlo", 0.8, 4.2, Box(60, 980, 960, 420), "Poppins", 84,
          "#FFFFFF", weight=800, line=1.05, anim_in=tanim("pop", duration=0.4, unit="word", stagger=0.1), name="Texto")
    song(t, "fun", 2, 0.8)
    return t


def link_perfil():
    t = _end("r-link-perfil", "Link en mi perfil", "Link in bio", 3336, ["link", "perfil", "bio", "compras"], bgc="#111111")
    photo_bg(t, "creator-03", s1=1.06, label="Tu video")
    shade_bottom(t, 900, 0.8)
    label(t, t.track("text", "Flecha"), "↑", 0.4, 4.6, centered(540, 360, 300, 300), "Inter", 260, "#FFFFFF", weight=900,
          editable=False, layers=[shadow("#000000", 0, 6, 16, 0.6), fill("#FFFFFF")],
          anim_loop=tanim("float", amount=0.25, speed=1.4))
    label(t, t.track("text", "Texto"), "LINK EN MI PERFIL", 0.6, 4.4, Box(60, 1300, 960, 200), "Anton", 112, "#FFFFFF",
          weight=400, spacing=6, anim_in=tanim("stamp", duration=0.3), name="Texto")
    label(t, t.track("text", "Sub"), "ahí encuentras todo lo del video", 1.2, 3.8, Box(60, 1520, 960, 90), "Montserrat", 50,
          "#FFE066", weight=700, anim_in=tanim("fade", duration=0.4), name="Subtítulo")
    song(t, "electro", 3, 0.8)
    return t


def comenta():
    t = _end("r-comenta", "Comenta tu respuesta", "Comment below", 3337, ["comenta", "comentarios", "opinión"], bgc="#7209B7")
    bg_gradient(t, [(0, "#7209B7"), (1, "#3A0CA3")], angle=135)
    for i, (txt, x, y) in enumerate([("¡yo!", 260, 560), ("la segunda 😍", 760, 760), ("¿parte 2?", 300, 960)]):
        rrect(t, t.track("shape", "Burbuja"), "#FFFFFF", 0.3 + i * 0.4, 4.7 - i * 0.4, centered(x, y, 420, 140), 60, pop(0, 0.35),
              layers=[shadow("#000000", 0, 8, 16, 0.3), fill("#FFFFFF"), no_stroke()])
        label(t, t.track("text", "Comentario"), txt, 0.3 + i * 0.4, 4.7 - i * 0.4, centered(x, y, 420, 140), "Poppins", 54,
              "#3A0CA3", weight=700, editable=False, motion=pop(0, 0.35))
    label(t, t.track("text", "Texto"), "¿y tú qué opinas?\n¡comenta! 👇", 1.6, 3.4, Box(60, 1220, 960, 320), "Poppins", 96,
          "#FFFFFF", weight=800, line=1.05, anim_in=tanim("rise", duration=0.4), name="Texto")
    song(t, "fun", 4, 0.8)
    return t


def gracias_1k():
    t = _end("r-gracias-1k", "Gracias por 1.000", "Thanks for 1k", 3338, ["gracias", "1000 seguidores", "hito", "celebración"],
             thumb_at=4.4, duration=6.0, bgc="#0B0B0B")
    bg(t, "#0B0B0B")
    nums = t.track("text", "Número")
    _count(t, nums, ["0", "120", "380", "640", "890", "990"], 0.2, 0.25, Box(60, 600, 960, 360), "Montserrat", 300, "#FFFFFF")
    label(t, nums, "1K", 1.7, 4.3, Box(60, 600, 960, 360), "Montserrat", 360, "#FFD23F", weight=900,
          layers=[glow("#FFD23F", 30, 0.6), fill("#FFD23F")], anim_in=tanim("pop", duration=0.4), name="Número")
    label(t, t.track("text", "Texto"), "¡gracias por ser parte!", 2.2, 3.8, Box(60, 1000, 960, 140), "Poppins", 80, "#FFFFFF",
          weight=800, anim_in=tanim("rise", duration=0.4), name="Texto")
    confetti(t, ["#FFD23F", "#FFFFFF", "#FF5A5F", "#3EC1FF"], 1.7, 4.3, seed=3338, lanes=4, density=0.22)
    flash(t, 1.7, 0.3, peak=0.6)
    song(t, "upbeat", 0, 0.85)
    return t


def nos_vemos_manana():
    t = _end("r-nos-vemos-manana", "Nos vemos mañana", "See you tomorrow", 3339, ["despedida", "mañana", "buenas noches"],
             thumb_at=3.4, duration=6.0, bgc="#0B132B")
    photo_bg(t, "night-03", s1=1.06, label="Fondo")
    shade_full(t, 0.5, colour="#0B132B")
    t.solid(t.track("shape", "Luna"), "#FFF1C1", 0.3, 5.7, centered(760, 420, 240, 240), pop(0, 0.5), kind="ellipse",
            layers=[glow("#FFE8A0", 40, 0.7), fill("#FFF1C1"), no_stroke()])
    t.solid(t.track("shape", "Luna"), "#16213E", 0.3, 5.7, centered(820, 390, 220, 220), pop(0, 0.5), kind="ellipse")
    dots(t, ["#FFFFFF"], 30, 0, 6.0, seed=3339, size=(4, 10), kinds=("star",), area=Box(0, 0, 1080, 900), drift=10)
    label(t, t.track("text", "Texto"), "nos vemos mañana", 0.8, 5.2, Box(60, 1100, 960, 200), "Pacifico", 110, "#FFFFFF",
          weight=400, anim_in=tanim("blur-in", duration=0.8), name="Texto")
    label(t, t.track("text", "Sub"), "descansa ✨", 1.6, 4.4, Box(60, 1320, 960, 100), "Poppins", 60, "#CDE7FF", weight=600,
          anim_in=tanim("fade", duration=0.4), name="Subtítulo")
    song(t, "calm", 0, 0.75)
    return t


# --- Countdowns ---------------------------------------------------------------------------------

def cuenta_5_seg():
    t = tall("r-cuenta-5-seg", "Cuenta de 5 segundos", "5-second countdown", "countdown", 6.0, order=3340,
             tags=["cuenta regresiva", "5 segundos", "inicio", "reto", "timer"], thumb_at=2.4, background="#111111")
    bg(t, "#111111")
    rings = t.track("shape", "Anillo")
    for i in range(5):
        t.solid(rings, "#FF2D55", 0.2 + i, 1.0, centered(540, 900, 720, 720), [(0, {"s": 1.1}, "out"), (1.0, {"s": 0.9})],
                kind="ellipse", layers=[{"id": "fill", "kind": "fill", "enabled": False, "paint": {"kind": "solid", "color": "#00000000"}},
                                        {"id": "stroke", "kind": "stroke", "enabled": True, "width": 16, "strokeAlign": "inside",
                                         "paint": {"kind": "solid", "color": "#ffff2d55"}, "opacity": 1.0}],
                opacity=keys([(0, 1.0), (1.0, 0.25)]))
    nums = t.track("text", "Números")
    _count(t, nums, ["5", "4", "3", "2", "1"], 0.2, 1.0, centered(540, 900, 700, 600), "Bebas Neue", 520, "#FFFFFF")
    label(t, nums, "¡YA!", 5.2, 0.8, centered(540, 900, 900, 600), "Bebas Neue", 420, "#FF2D55", weight=400,
          anim_in=tanim("zoom-in", duration=0.25), name="Final")
    flash(t, 5.2, 0.3)
    song(t, "electro", 0, 0.85)
    return t


def cuenta_revelar():
    t = tall("r-cuenta-revelar", "Cuenta para revelar", "Countdown reveal", "countdown", 7.0, order=3341,
             tags=["revelación", "sorpresa", "cuenta regresiva", "anuncio", "reveal"], thumb_at=5.6, background="#000000")
    host = t.track("video", "Sorpresa")
    clip = t.photo(host, "proposal-02", 0, 7.0, t.full, kb(7.0, 1.0, 1.06), label="Foto sorpresa",
                   effects=[effect("builtin.effects.gaussian_blur", animated={"u_blurRadius": keys([(0, 60, "hold"), (4.0, 60, "out"),
                                                                                                     (4.5, 0)])})])
    shade_full(t, 0.0)
    t.solid(t.track("shape", "Velo"), "#000000", 0, 7.0, opacity=keys([(0, 0.55, "hold"), (4.0, 0.55, "out"), (4.4, 0.0)]))
    label(t, t.track("text", "Arriba"), "la sorpresa en…", 0.2, 3.8, Box(60, 400, 960, 140), "DM Sans", 80, "#FFFFFF", weight=800,
          anim_in=tanim("fade", duration=0.3), anim_out=tanim("fade", duration=0.2), name="Texto")
    nums = t.track("text", "Números")
    _count(t, nums, ["3", "2", "1"], 1.0, 1.0, centered(540, 960, 700, 600), "Bebas Neue", 520, "#FFFFFF")
    flash(t, 4.0, 0.35)
    label(t, t.track("text", "Final"), "¡NOS CASAMOS!", 4.2, 2.8, Box(60, 1440, 960, 220), "Anton", 150, "#FFFFFF", weight=400,
          layers=[shadow("#000000", 0, 8, 20, 0.6), fill("#FFFFFF")], anim_in=tanim("stamp", duration=0.3), name="Revelación")
    confetti(t, ["#FFFFFF", "#F2D59B", "#FFB3C1"], 4.2, 2.8, seed=3341, lanes=4, density=0.22)
    song(t, "epic", 3, 0.85)
    return t


def cuenta_cumple():
    t = tall("r-cuenta-cumple", "Cuenta para mi cumpleaños", "Birthday countdown", "countdown", 6.0, order=3342,
             tags=["cumpleaños", "faltan días", "cuenta regresiva", "fiesta", "emoción"], thumb_at=3.4, background="#FFB3C6")
    bg_gradient(t, [(0, "#FFC8DD"), (1, "#BDE0FE")], angle=135)
    label(t, t.track("text", "Arriba"), "faltan", 0.2, 5.8, Box(60, 380, 960, 140), "Pacifico", 110, "#C9184A", weight=400,
          anim_in=tanim("fade", duration=0.3), name="Antes")
    days = t.track("text", "Días")
    _count(t, days, ["7", "6", "5", "4"], 0.6, 0.5, centered(540, 860, 700, 600), "Luckiest Guy", 480, "#FFFFFF",
           layers=[shadow("#C9184A", 0, 14, 0, 1.0), fill("#FFFFFF")])
    label(t, days, "3", 2.6, 3.4, centered(540, 860, 700, 600), "Luckiest Guy", 480, "#FFFFFF", weight=400,
          layers=[shadow("#C9184A", 0, 14, 0, 1.0), fill("#FFFFFF")], anim_in=tanim("stamp", duration=0.3), name="Días")
    label(t, t.track("text", "Abajo"), "días para mi cumple 🎂", 0.8, 5.2, Box(60, 1200, 960, 140), "Pacifico", 90, "#C9184A",
          weight=400, anim_in=tanim("fade", duration=0.4), name="Después")
    dots(t, ["#FFFFFF", "#FFD166"], 20, 0, 6.0, seed=3342, size=(14, 30), kinds=("star", "heart"), drift=80)
    song(t, "fun", 0, 0.8)
    return t


def cuenta_vacaciones():
    t = tall("r-cuenta-vacaciones", "Cuenta para las vacaciones", "Holiday countdown", "countdown", 6.0, order=3343,
             tags=["vacaciones", "viaje", "faltan días", "cuenta regresiva", "maleta"], thumb_at=3.4, background="#00B4D8")
    photo_bg(t, "beach-01", s1=1.08, label="Foto del destino")
    shade_full(t, 0.2)
    rrect(t, t.track("shape", "Maleta"), "#FFFFFF", 0.3, 5.7, centered(540, 880, 640, 760), 60, pop(0, 0.5, 0.6),
          layers=[shadow("#000000", 0, 16, 30, 0.3), fill("#FFFFFF", 0.92), no_stroke()])
    t.solid(t.track("shape", "Asa"), "#FFFFFF", 0.3, 5.7, centered(540, 470, 240, 70), pop(0, 0.5, 0.6), radius=30,
            kind="rounded-rectangle", alpha=0.92)
    days = t.track("text", "Días")
    _count(t, days, ["10", "9", "8"], 0.6, 0.5, centered(540, 840, 600, 420), "Anton", 340, "#0077B6")
    label(t, days, "7", 2.1, 3.9, centered(540, 840, 600, 420), "Anton", 340, "#0077B6", weight=400,
          anim_in=tanim("stamp", duration=0.3), name="Días")
    label(t, t.track("text", "Abajo"), "días para la playa ✈", 0.8, 5.2, centered(540, 1130, 600, 120), "Montserrat", 50,
          "#0077B6", weight=800, anim_in=tanim("fade", duration=0.4), name="Texto")
    song(t, "upbeat", 0, 0.8)
    return t


def cuenta_boda():
    t = tall("r-cuenta-boda", "Cuenta para la boda", "Wedding countdown", "countdown", 7.0, order=3344,
             tags=["boda", "faltan días", "cuenta regresiva", "novios", "save the date"], thumb_at=4.4, background="#F7F2EA")
    photo_bg(t, "wedding-04", s1=1.06, label="Foto de los novios")
    shade_full(t, 0.35, colour="#2B2118")
    label(t, t.track("text", "Arriba"), "faltan", 0.4, 6.6, Box(60, 560, 960, 120), "Cinzel", 64, "#F2E6CF", weight=500,
          spacing=16, anim_in=tanim("fade", duration=0.6), name="Antes")
    label(t, t.track("text", "Días"), "30", 0.8, 6.2, Box(60, 660, 960, 420), "Playfair Display", 360, "#FFFFFF", weight=700,
          layers=[glow("#F2D59B", 20, 0.5), fill("#FFFFFF")], anim_in=tanim("blur-in", duration=0.8), name="Días")
    label(t, t.track("text", "Abajo"), "días para el sí", 1.4, 5.6, Box(60, 1080, 960, 160), "Great Vibes", 120, "#F2D59B",
          weight=400, anim_in=tanim("fade", duration=0.6), name="Después")
    label(t, t.track("text", "Nombres"), "ANA & LEO · 14.02.2027", 2.0, 5.0, Box(60, 1300, 960, 80), "Cinzel", 46, "#F2E6CF",
          weight=500, spacing=8, anim_in=tanim("fade", duration=0.6), name="Nombres y fecha")
    song(t, "romantic", 1, 0.75)
    return t


# --- Vertical lower thirds -----------------------------------------------------------------------

def _vlt(id, es, en, sample, order, tags):
    t = tall(id, es, en, "lowerthird", 6.0, order=order, tags=["tercio inferior", "rótulo", "vertical"] + tags, thumb_at=2.6)
    photo_bg(t, sample, s1=1.05, label="Tu video")
    shade_bottom(t, 700, 0.55)
    return t


def vt_nombre():
    t = _vlt("r-vt-nombre", "Rótulo de nombre vertical", "Vertical name tag", "portrait-05", 3345, ["nombre", "entrevista"])
    t.solid(t.track("shape", "Barra"), "#FFD23F", 0.5, 4.7, Box(60, 1460, 10, 200), [(0, {"sy": 0.0, "dy": -100}, "out"),
                                                                                  (0.3, {})])
    label(t, t.track("text", "Nombre"), "Laura Méndez", 0.7, 4.5, Box(100, 1450, 900, 110), "Montserrat", 80, "#FFFFFF",
          weight=800, align="left", anim_in=tanim("slide-right", duration=0.4), anim_out=tanim("fade", duration=0.3),
          name="Nombre")
    label(t, t.track("text", "Cargo"), "nutricionista", 0.9, 4.3, Box(102, 1560, 900, 80), "Montserrat", 50, "#FFD23F",
          weight=600, align="left", anim_in=tanim("fade", duration=0.4), anim_out=tanim("fade", duration=0.3), name="Cargo")
    song(t, "calm", 1, 0.6)
    return t


def vt_usuario():
    t = _vlt("r-vt-usuario", "@usuario vertical", "Vertical @handle", "selfie-03", 3346, ["usuario", "redes", "sígueme"])
    pill(t, t.track("shape", "Píldora"), "#FFFFFF", 0.5, 4.7, Box(140, 1520, 800, 140), [(0, {"s": 0.0}, "back"), (0.45, {}, "hold"),
                                                                                      (4.4, {}, "in"), (4.7, {"s": 0.0})])
    t.solid(t.track("shape", "Icono"), "#FF8C42", 0.6, 4.4, centered(230, 1590, 100, 100), pop(0, 0.35), kind="ellipse")
    label(t, t.track("text", "Icono"), "@", 0.6, 4.4, centered(230, 1588, 100, 100), "Poppins", 60, "#FFFFFF", weight=800,
          editable=False, motion=pop(0, 0.35))
    label(t, t.track("text", "Usuario"), "@camiviaja", 0.7, 4.0, Box(300, 1520, 620, 140), "Poppins", 66, "#111111", weight=800,
          align="left", anim_in=tanim("typewriter", duration=0.6, unit="character"), name="Usuario")
    song(t, "upbeat", 4, 0.6)
    return t


def vt_ubicacion():
    t = _vlt("r-vt-ubicacion", "Ubicación vertical", "Vertical location", "travel-07", 3347, ["ubicación", "viaje", "lugar"])
    t.solid(t.track("shape", "Pin"), "#FF4D4D", 0.5, 4.7, centered(140, 1500, 90, 90), [(0, {"dy": -400}, "back"), (0.5, {})],
            kind="ellipse")
    t.solid(t.track("shape", "Pin"), "#FFFFFF", 0.5, 4.7, centered(140, 1500, 34, 34), [(0, {"dy": -400}, "back"), (0.5, {})],
            kind="ellipse")
    label(t, t.track("text", "Lugar"), "Lago Azul", 0.8, 4.4, Box(210, 1430, 820, 140), "Bebas Neue", 140, "#FFFFFF", weight=400,
          align="left", spacing=4, anim_in=tanim("slide-right", duration=0.4, unit="character", stagger=0.03),
          anim_out=tanim("fade", duration=0.3), name="Lugar")
    label(t, t.track("text", "Región"), "PARQUE NACIONAL · 2.300 m", 1.0, 4.2, Box(214, 1580, 820, 70), "Montserrat", 40,
          "#FFFFFF", weight=700, align="left", spacing=4, anim_in=tanim("fade", duration=0.4), anim_out=tanim("fade", duration=0.3),
          name="Detalle")
    song(t, "world", 3, 0.6)
    return t


def vt_precio():
    t = _vlt("r-vt-precio", "Precio vertical", "Vertical price tag", "outfit-04", 3348, ["precio", "producto", "tienda"])
    rrect(t, t.track("shape", "Panel"), "#111111", 0.5, 4.7, Box(60, 1460, 640, 220), 30, slide_in(dx=-700, length=0.4))
    label(t, t.track("text", "Producto"), "Chaqueta de lino", 0.6, 4.6, Box(100, 1480, 580, 90), "Montserrat", 54, "#FFFFFF",
          weight=800, align="left", name="Producto")
    label(t, t.track("text", "Talla"), "tallas S a XL", 0.7, 4.5, Box(100, 1570, 580, 70), "Montserrat", 40, "#BDBDBD", weight=500,
          align="left", name="Detalle")
    t.solid(t.track("shape", "Precio"), "#FF5A1F", 0.9, 4.1, centered(820, 1520, 340, 340), [(0, {"s": 0.0}, "back"), (0.45, {})],
            kind="burst", points=16, innerRatio=0.86, rotation=keys([(0, 0, "linear"), (4.1, 30)]))
    label(t, t.track("text", "Precio"), "$39", 1.0, 4.0, centered(820, 1520, 320, 200), "Anton", 140, "#FFFFFF", weight=400,
          anim_in=tanim("pop", duration=0.3), name="Precio")
    song(t, "upbeat", 6, 0.6)
    return t


def vt_horario():
    t = _vlt("r-vt-horario", "Horario de atención vertical", "Vertical opening hours", "cafe-01", 3349,
             ["horario", "negocio", "atención"])
    rrect(t, t.track("shape", "Panel"), "#FFFFFF", 0.5, 4.7, Box(60, 1300, 960, 440), 40, pop(0, 0.4, 0.8),
          layers=[shadow("#000000", 0, 10, 26, 0.3), fill("#FFFFFF", 0.95), no_stroke()])
    label(t, t.track("text", "Título"), "🕘 HORARIO", 0.6, 4.6, Box(100, 1320, 880, 110), "Montserrat", 60, "#111827", weight=800,
          align="left", name="Título")
    for i, (d, h) in enumerate([("Lun a vie", "8:00 – 20:00"), ("Sábados", "9:00 – 14:00"), ("Domingos", "cerrado")]):
        label(t, t.track("text", "Día"), d, 0.8 + i * 0.2, 4.4 - i * 0.2, Box(100, 1440 + i * 95, 440, 90), "Montserrat", 48,
              "#374151", weight=600, align="left", anim_in=tanim("fade", duration=0.3), name=f"Día {i + 1}")
        label(t, t.track("text", "Hora"), h, 0.8 + i * 0.2, 4.4 - i * 0.2, Box(540, 1440 + i * 95, 440, 90), "Montserrat", 48,
              "#111827", weight=800, align="right", anim_in=tanim("fade", duration=0.3), name=f"Hora {i + 1}")
    song(t, "jazz", 1, 0.6)
    return t


TEMPLATES = [unboxing, producto_360, colores_disponibles, combo, mas_vendido, detalle_lupa, resena_estrellas,
             comparar_tamanos, agotado_vuelta, beneficios,
             hilo_post, nota_celular, pregunta_respuesta, tres_errores, mito_verdad, ranking_5_1, receta_texto,
             frase_subrayada, lista_pendientes, signos, dia_x_de, trivia, frase_pelicula, consejo_finanzas,
             palabra_del_dia, traduccion, cosas_felices, pensamiento_dia, poema_corto, reto_30_dias,
             bienvenidos_canal, nuevo_video, en_vivo_ahora,
             siguenos_mas, guardalo, compartelo, link_perfil, comenta, gracias_1k, nos_vemos_manana,
             cuenta_5_seg, cuenta_revelar, cuenta_cumple, cuenta_vacaciones, cuenta_boda,
             vt_nombre, vt_usuario, vt_ubicacion, vt_precio, vt_horario]
