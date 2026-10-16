"""Text styles, part A: viral subtitles, titles, calls to action, lower thirds, prices, quotes.

Sizes are project pixels for a 1080 x 1920 reel; every other length is em (see kit.py).
Research (2026-10-16): CapCut "Trending" captions and text templates, the Instagram/TikTok caption
looks (word highlighted as it is said, thick outline, block per line, hard shadow, emoji), Premiere's
Essential Graphics caption packs and Filmora's title library. No brand names, logos or brand colours
used as a look of their own.
"""

from __future__ import annotations

from kit import (Style, accent, extrude, fill, fx, glow, grad, hard, hollow_fill, neon_stack, shadow, stroke,
                 tslot)

# Caption motion: quick pop by word in, short fade out, as the trend packs do.
POP_WORD = tslot("pop", 0.22, "back", unit="word", stagger=0.05)
FADE_OUT = tslot("fade", 0.15, "easeIn")
KARAOKE_POP = tslot("karaoke-pop", scale=108)
KARAOKE_BOUNCE = tslot("karaoke-bounce", lift=0.08, scale=106)


def sub(id, es, en, sample, font, size, weight, layers, *, acc=None, loop=None, anim_in=POP_WORD, tags=(), **kw):
    return Style(id, es, en, "subtitulos", sample, font, size, weight, layers, acc=acc, anim_in=anim_in,
                 anim_out=FADE_OUT, anim_loop=loop, valign="bottom", subtitle=True,
                 tags=["subtitulos", "captions", "reels", *tags], **kw)


def karaoke_color(id, es, en, font, weight, color, sample, *, size=80, line=0.09, case="none", tags=()):
    return sub(id, es, en, sample, font, size, weight,
               [shadow(dy=0.05, blur=0.1, opacity=0.65), stroke(line), fill("#ffffff")],
               acc=accent("karaoke", color, size=1.08), loop=KARAOKE_POP, case=case,
               tags=["karaoke", "palabra resaltada", "highlight", *tags])


def karaoke_pill(id, es, en, font, weight, pill, text, sample, *, size=78, tags=()):
    return sub(id, es, en, sample, font, size, weight, [stroke(0.05), fill("#ffffff")],
               acc=accent("karaoke", text, pill=pill, pad=0.12, radius=0.16), loop=KARAOKE_BOUNCE,
               tags=["karaoke", "caja", "box", "highlight", *tags])


SAY = ("Esto cambió mi vida para siempre", "This changed my life forever")
SAY2 = ("Nadie te cuenta este secreto", "Nobody tells you this secret")
SAY3 = ("Mira lo que pasa al final", "Watch what happens at the end")
SAY4 = ("Hoy te enseño cómo hacerlo", "Today I show you how to do it")

SUBTITLES = [
    karaoke_color("sub-karaoke-amarillo", "Karaoke amarillo", "Yellow karaoke", "Montserrat", 900, "#ffe600", SAY,
                  tags=["amarillo", "yellow"]),
    karaoke_color("sub-karaoke-verde", "Karaoke verde lima", "Lime karaoke", "Poppins", 900, "#4dff6a", SAY2,
                  tags=["verde", "green"]),
    karaoke_color("sub-karaoke-cian", "Karaoke celeste", "Cyan karaoke", "Inter", 900, "#2ee6ff", SAY3,
                  tags=["celeste", "cyan"]),
    karaoke_color("sub-karaoke-rosa", "Karaoke rosa", "Pink karaoke", "Outfit", 900, "#ff4fb8", SAY4,
                  tags=["rosa", "pink"]),
    karaoke_color("sub-karaoke-naranja", "Karaoke naranja", "Orange karaoke", "Figtree", 900, "#ff9100",
                  ("Tres cosas que debes saber", "Three things you should know"), tags=["naranja", "orange"]),
    karaoke_color("sub-karaoke-rojo", "Karaoke rojo en mayúsculas", "Red caps karaoke", "Archivo Black", 400,
                  "#ff3347", ("No vas a creer esto", "You won't believe this"), size=78, line=0.1, case="upper",
                  tags=["rojo", "red", "mayusculas"]),
    karaoke_pill("sub-caja-morada", "Palabra en caja morada", "Purple word box", "Inter", 900, "#7c3aed", "#ffffff",
                 SAY2, tags=["morado", "purple"]),
    karaoke_pill("sub-caja-verde", "Palabra en caja verde", "Green word box", "Plus Jakarta Sans", 800, "#22c55e",
                 "#0b1a10", SAY3, tags=["verde", "green"]),
    karaoke_pill("sub-caja-amarilla", "Palabra en caja amarilla", "Yellow word box", "Montserrat", 900, "#ffd60a",
                 "#111111", SAY, tags=["amarillo", "yellow"]),
    karaoke_pill("sub-caja-roja", "Palabra en caja roja", "Red word box", "Poppins", 800, "#ff2d55", "#ffffff",
                 SAY4, tags=["rojo", "red"]),
    sub("sub-youtuber", "Estilo youtuber", "Creator style", ("ESTO ES LO MEJOR QUE VAS A VER HOY",
                                                             "THIS IS THE BEST THING YOU'LL SEE TODAY"),
        "Montserrat", 86, 900, [hard(dx=0.0, dy=0.09), stroke(0.14), fill("#ffffff")],
        acc=accent("keywords", "#ffe600", size=1.1), case="upper", tags=["youtuber", "creator", "mayusculas"]),
    sub("sub-youtuber-rojo", "Youtuber con golpe rojo", "Creator red punch", ("ESTO NADIE LO SABE TODAVÍA",
                                                                              "NOBODY KNOWS THIS YET"),
        "Anton", 104, 400, [hard(dy=0.07), stroke(0.08), fill("#ffffff")],
        acc=accent("everyNth", "#ff2b2b", n=3, phase=2, size=1.12), case="upper", spacing=0.01,
        tags=["youtuber", "rojo", "mayusculas"]),
    sub("sub-contorno-grueso", "Contorno grueso", "Thick outline", ("¡No te pierdas lo que viene!",
                                                                    "Don't miss what's next!"),
        "Lilita One", 90, 400, [shadow(dy=0.06, blur=0.08, opacity=0.5), stroke(0.17), fill("#ffffff")],
        tags=["contorno", "outline", "grueso"]),
    sub("sub-doble-contorno", "Doble contorno", "Double outline", ("Esto sí que es divertido", "Now this is fun"),
        "Luckiest Guy", 88, 400, [stroke(0.22, "#ffffff", id="stroke2"), stroke(0.1, "#151515"), fill("#ffffff")],
        acc=accent("karaoke", "#ff3b6b", size=1.06), loop=KARAOKE_POP, tags=["contorno", "sticker", "karaoke"]),
    sub("sub-sombra-dura", "Sombra dura", "Hard shadow", ("El truco que cambia todo", "The trick that changes everything"),
        "Kanit", 84, 800, [hard("#000000", 0.07, 0.08), stroke(0.04), fill("#ffffff")],
        acc=accent("karaoke", "#c6ff3d"), loop=KARAOKE_POP, tags=["sombra", "shadow", "karaoke"]),
    sub("sub-caja-lineas", "Caja negra por línea", "Black box per line", ("Lo más importante es empezar hoy mismo",
                                                                          "The most important thing is to start today"),
        "Inter", 64, 700, [fill("#ffffff")], box="#000000d9", box_style="line", box_pad=(0.32, 0.14),
        box_radius=0.16, acc=accent("keywords", "#ffd84d"), line=1.3, tags=["caja", "box", "linea", "tiktok"]),
    sub("sub-caja-blanca", "Caja blanca por línea", "White box per line", ("POV: por fin aprendiste a editar",
                                                                            "POV: you finally learned to edit"),
        "Plus Jakarta Sans", 64, 800, [fill("#111111")], box="#ffffff", box_style="line", box_pad=(0.34, 0.16),
        box_radius=0.24, line=1.32, tags=["caja", "blanca", "pov", "tiktok"], card="#3a4150"),
    sub("sub-translucido", "Fondo translúcido", "Frosted caption", ("Así se ve una mañana tranquila",
                                                                   "This is what a calm morning looks like"),
        "Lexend", 62, 600, [fill("#ffffff")], box="#0000007a", box_pad=(0.5, 0.3), box_radius=0.35, line=1.25,
        tags=["translucido", "suave", "vlog"]),
    sub("sub-limpio", "Limpio con borde fino", "Clean thin edge", ("Un día normal en mi vida", "A normal day in my life"),
        "Figtree", 68, 700, [shadow(dy=0.04, blur=0.14, opacity=0.8), stroke(0.035), fill("#ffffff")],
        anim_in=tslot("fade", 0.18, "easeOut"), tags=["minimal", "vlog", "limpio"]),
    sub("sub-emoji-pop", "Emoji pop", "Emoji pop", ("¡Esto está buenísimo! 🔥", "This is so good! 🔥"),
        "Baloo 2", 88, 800, [shadow(dy=0.05, blur=0.08, opacity=0.6), stroke(0.11), fill("#ffffff")],
        acc=accent("karaoke", "#ffd23f", size=1.15), loop=KARAOKE_POP, tags=["emoji", "karaoke", "divertido"]),
    sub("sub-emoji-burbuja", "Burbuja con emoji", "Emoji bubble", ("Me encantó el resultado 😍", "I loved how it turned out 😍"),
        "Nunito", 66, 900, [fill("#141414")], box="#ffffff", box_shape="pill", box_pad=(0.55, 0.3),
        tags=["emoji", "burbuja", "pill"], card="#3b3550"),
    sub("sub-podcast", "Podcast", "Podcast", ("La clave está en la constancia", "The key is consistency"),
        "Sora", 70, 700, [shadow(dy=0.03, blur=0.1, opacity=0.7), fill("#ffffff")],
        acc=accent("keywords", "#a3e635", size=1.05), anim_in=tslot("rise-by-word", 0.3, "easeOut", unit="word",
                                                                     stagger=0.06, rise=0.3, blur=4),
        tags=["podcast", "entrevista", "clave"]),
    sub("sub-documental", "Documental", "Documentary", ("En lo alto de la montaña, el silencio", "High on the mountain, silence"),
        "Barlow Condensed", 70, 600, [shadow(dy=0.03, blur=0.12, opacity=0.8), fill("#f4f1ea")], case="upper",
        spacing=0.04, anim_in=tslot("fade", 0.4, "easeOut"), tags=["documental", "cine", "elegante"]),
    sub("sub-gamer", "Gamer", "Gamer", ("¡Qué jugada tan increíble!", "What an incredible play!"),
        "Russo One", 80, 400, [glow("#00ff9c", 0.25, 0.55), stroke(0.09, "#04140c"), fill("#ffffff")],
        acc=accent("karaoke", "#00ff9c", size=1.08), loop=KARAOKE_POP, tags=["gaming", "gamer", "verde"]),
    sub("sub-karaoke-neon", "Karaoke neón", "Neon karaoke", ("Esta noche brilla la ciudad", "Tonight the city shines"),
        "Montserrat", 80, 800, [glow("#ff2bd6", 0.35, 0.7), stroke(0.04, "#ff2bd6"), fill("#ffffff")],
        acc=accent("karaoke", "#7cf4ff", size=1.08), loop=KARAOKE_POP, tags=["neon", "karaoke", "noche"], card="night"),
    sub("sub-palabra-gigante", "Palabra gigante", "Giant word", ("BOOM", "BOOM"),
        "Anton", 170, 400, [hard("#000000", 0.0, 0.06), stroke(0.06), fill("#ffe600")], case="upper",
        anim_in=tslot("zoom-in", 0.16, "back", **{"from": 40}),
        tags=["una palabra", "single word", "gigante"]),
    sub("sub-primera-grande", "Primera palabra grande", "Big first word", ("NUNCA pares de aprender", "NEVER stop learning"),
        "Archivo Black", 76, 400, [stroke(0.07), fill("#ffffff")], acc=accent("firstWord", "#ffd60a", size=1.4),
        tags=["primera palabra", "jerarquia"]),
    sub("sub-remate-caja", "Remate en caja", "Punchline box", ("Y entonces pasó lo impensable", "And then the unthinkable happened"),
        "Poppins", 76, 900, [stroke(0.06), fill("#ffffff")],
        acc=accent("lastWord", "#ffffff", pill="#ff2d55", pad=0.14, radius=0.14), tags=["ultima palabra", "caja"]),
    sub("sub-palabras-clave", "Palabras clave en color", "Coloured keywords", ("Ahorrar dinero es más fácil de lo que crees",
                                                                               "Saving money is easier than you think"),
        "Montserrat", 74, 800, [shadow(dy=0.05, blur=0.1, opacity=0.6), stroke(0.07), fill("#ffffff")],
        acc=accent("keywords", "#ffe600", size=1.12), tags=["palabras clave", "keywords"]),
    sub("sub-dos-colores", "Dos colores", "Two-tone words", ("Una palabra sí y otra también", "One word on, one word off"),
        "Rubik", 78, 800, [stroke(0.07, "#0b1630"), fill("#ffffff")], acc=accent("everyOther", "#4dd9ff"),
        tags=["dos colores", "alterno"]),
    sub("sub-contorno-relleno", "Contorno que se rellena", "Outline to fill", ("Escucha bien cada palabra", "Listen to every word"),
        "Montserrat", 84, 900, [stroke(0.04, "#ffffff"), hollow_fill()], acc=accent("karaoke", "#ffffff"),
        loop=KARAOKE_POP, tags=["contorno", "hueco", "karaoke"]),
    sub("sub-degradado", "Degradado por palabra", "Gradient words", ("Colores que se mueven contigo", "Colours that move with you"),
        "Outfit", 82, 900, [stroke(0.07, "#2a0d2e"), fill(grad([(0, "#ffd36e"), (1, "#ff4f9a")], 90, space="word"))],
        tags=["degradado", "gradient", "colores"]),
    sub("sub-maquina", "Máquina de escribir", "Typewriter caption", ("Querido diario: hoy fue un buen día",
                                                                     "Dear diary: today was a good day"),
        "Special Elite", 66, 400, [shadow(dy=0.03, blur=0.08, opacity=0.8), fill("#f8f4e8")],
        anim_in=tslot("typewriter", 0.4, "linear", unit="character", stagger=0.035), tags=["maquina de escribir", "diario"]),
    sub("sub-cine", "Subtítulo de cine", "Film subtitle", ("No sabía que volvería a verte", "I didn't know I'd see you again"),
        "Lato", 60, 700, [shadow(dy=0.04, blur=0.1, opacity=0.9), stroke(0.025, "#000000"), fill("#fff3a8")],
        anim_in=tslot("fade", 0.12, "easeOut"), tags=["cine", "pelicula", "clasico"]),
    sub("sub-noticias", "Titular de noticias", "News strap", ("ÚLTIMA HORA: llega la nueva temporada",
                                                              "BREAKING: the new season is here"),
        "Oswald", 62, 600, [fill("#ffffff")], box="#d62828", box_style="line", box_pad=(0.3, 0.12), line=1.28,
        acc=accent("firstWord", "#ffe08a"), anim_in=tslot("wipe", 0.35, "easeOut", angle=0), tags=["noticias", "news"]),
    sub("sub-tierno", "Tierno pastel", "Pastel cute", ("Mi gatito aprendió un truco nuevo", "My kitten learned a new trick"),
        "Fredoka", 76, 700, [stroke(0.07, "#5a1a3a"), fill("#ffffff")],
        acc=accent("karaoke", "#5a1a3a", pill="#ffb3d9", pad=0.12, radius=0.3), loop=KARAOKE_BOUNCE,
        tags=["tierno", "pastel", "cute", "karaoke"]),
]

# --- titles -------------------------------------------------------------------------------------

def title(id, es, en, sample, font, size, weight, layers, *, tags=(), anim_in=None, anim_out=None, **kw):
    return Style(id, es, en, "titulos", sample, font, size, weight, layers,
                 anim_in=anim_in or tslot("rise", 0.5, "easeOut", unit="word"),
                 anim_out=anim_out or tslot("fade-scale", 0.35, "easeIn"), tags=["titulo", "title", *tags], **kw)


TITLES = [
    title("tit-bloque-blanco", "Bloque blanco", "White block", ("HAZLO HOY", "DO IT TODAY"), "Anton", 170, 400,
          [hard("#000000", 0.08, 0.08), fill("#ffffff")], case="upper", anim_in=tslot("stamp", 0.35, "easeIn"),
          tags=["impacto", "bold"]),
    title("tit-trailer-dorado", "Tráiler dorado", "Gold trailer", ("LA LEYENDA REGRESA", "THE LEGEND RETURNS"),
          "Cinzel", 96, 700, [glow("#ffcc66", 0.35, 0.45), stroke(0.02, "#4a3200"),
                              fill(grad([(0, "#fff4c4"), (0.5, "#e2b04a"), (1, "#8a5a12")], 90))],
          spacing=0.12, anim_in=tslot("blur-in", 0.9, "easeOut"), tags=["cine", "trailer", "dorado"], card="night"),
    title("tit-espaciado", "Minimal espaciado", "Wide minimal", ("NUEVA COLECCIÓN", "NEW COLLECTION"), "Josefin Sans", 78,
          400, [fill("#ffffff")], spacing=0.32, case="upper", anim_in=tslot("snap-together", 0.8, "easeOut"),
          tags=["minimal", "moda", "limpio"]),
    title("tit-editorial", "Editorial en cursiva", "Editorial italic", ("La belleza de lo simple", "The beauty of simple things"),
          "Bodoni Moda", 112, 400, [fill("#141414")], italic=True, line=1.05, card="light",
          anim_in=tslot("fade-up-char", 0.6, "easeOut", unit="word"), tags=["editorial", "revista", "elegante"]),
    title("tit-condensado", "Titular condensado", "Condensed headline", ("MÁS ALTO, MÁS LEJOS", "HIGHER, FURTHER"),
          "League Gothic", 190, 400, [shadow(dy=0.03, blur=0.08, opacity=0.6),
                                      fill(grad([(0, "#ffffff"), (1, "#b9c0cc")], 90))], case="upper", line=0.95,
          tags=["condensado", "deportes", "fuerte"]),
    title("tit-portada-roja", "Portada roja", "Red cover", ("EDICIÓN ESPECIAL", "SPECIAL EDITION"), "Archivo Black", 120,
          400, [fill("#e10600")], case="upper", line=0.95, card="light", anim_in=tslot("slide-up", 0.45, "easeOut", unit="word"),
          tags=["revista", "portada", "rojo"]),
    title("tit-serif-clasico", "Serif clásico", "Classic serif", ("Capítulo uno", "Chapter one"), "DM Serif Display", 140, 400,
          [fill("#151515")], card="warm", anim_in=tslot("blur-in-words", 0.7, "easeOut"), tags=["serif", "capitulo", "libro"]),
    title("tit-solo-contorno", "Solo contorno", "Outline only", ("SIN LÍMITES", "NO LIMITS"), "Big Shoulders Display", 180,
          900, [stroke(0.025, "#ffffff", align="center"), hollow_fill()], case="upper",
          anim_in=tslot("converge", 0.6, "easeOut"), tags=["contorno", "outline", "minimal"]),
    title("tit-metal-azul", "Metal azul", "Blue metal", ("NIVEL MÁXIMO", "MAX LEVEL"), "Exo 2", 120, 900,
          [shadow(dy=0.06, blur=0.1, opacity=0.7), stroke(0.035, "#0b1d3a"),
           fill(grad([(0, "#ffffff"), (0.45, "#9cc9ff"), (0.52, "#1d4ea3"), (1, "#cfe4ff")], 90))],
          case="upper", tags=["metal", "cromo", "azul"]),
    title("tit-aurora", "Aurora", "Aurora", ("Buenos días", "Good morning"), "Poppins", 140, 900,
          [glow("#8a7dff", 0.4, 0.35), fill(grad([(0, "#3ef0c8"), (0.5, "#8a7dff"), (1, "#ff6fc2")], 0))],
          tags=["degradado", "aurora", "colores"]),
    title("tit-recorte-papel", "Recorte de papel", "Paper cut-out", ("ASÍ LO HICE", "HOW I DID IT"), "Archivo Black", 96, 400,
          [fill("#111111")], word_bg="#ffffff", word_bg_pad=0.16, word_bg_radius=0.04, case="upper", spacing=0.02,
          card="#c96a4a", anim_in=tslot("pop", 0.3, "back", unit="word", stagger=0.08), tags=["papel", "recorte", "collage"]),
    title("tit-resaltador", "Resaltador", "Highlighter", ("Apunta esto", "Write this down"), "Permanent Marker", 120, 400,
          [fill("#141414")], word_bg="#ffe94d", word_bg_pad=0.08, word_bg_radius=0.02, card="light",
          anim_in=tslot("wipe", 0.5, "easeOut", angle=0), tags=["resaltador", "marcador", "escuela"]),
    title("tit-sombras-color", "Sombras de colores", "Colour echoes", ("¡Vamos!", "Let's go!"), "Titan One", 150, 400,
          [hard("#00c9c8", 0.14, 0.14, id="shadow2"), hard("#ff5e5b", 0.07, 0.07), fill("#fff6d6")],
          anim_in=tslot("bounce", 0.6), tags=["sombra", "colores", "divertido"], card="#2b2f6b"),
    title("tit-destello", "Destello que recorre", "Shine sweep", ("ESTRENO", "PREMIERE"), "Montserrat", 150, 900,
          [shadow(dy=0.05, blur=0.12, opacity=0.6), fill("#ffffff"),
           fill(fx("shine", "#00000000", speed=0.45, width=0.18, angle=20, intensity=1.1), id="shine", blend="screen")],
          case="upper", tags=["brillo", "shine", "estreno"], card="#2a1d4f"),
    title("tit-holografico", "Holográfico", "Holographic", ("FUTURO", "FUTURE"), "Outfit", 170, 900,
          [glow("#b9a6ff", 0.3, 0.45), fill(fx("shimmer", "#ffffff", speed=0.3, scale=3, intensity=0.75))],
          case="upper", tags=["holografico", "y2k", "futuro"], card="night"),
    title("tit-rgb", "RGB desplazado", "RGB split", ("SEÑAL", "SIGNAL"), "Bebas Neue", 190, 400,
          [fill("#ff00d4", id="glitcha", offsetX=-0.035, opacity=0.85, blend="screen"),
           fill("#00f0ff", id="glitchb", offsetX=0.035, opacity=0.85, blend="screen"), fill("#ffffff")],
          spacing=0.04, anim_in=tslot("glitch-in", 0.3, "linear"), tags=["glitch", "rgb", "tecnologia"], card="night"),
    title("tit-pincelada", "Pincelada", "Brush stroke", ("Sabor casero", "Homemade taste"), "Kaushan Script", 104, 400,
          [fill("#ffffff")], box="#e2412f", box_shape="brush", box_pad=(0.55, 0.32),
          anim_in=tslot("wipe", 0.5, "easeOut", angle=0), tags=["pincel", "comida", "artesanal"]),
    title("tit-arco", "Título en arco", "Arched title", ("SÚPER VERANO", "SUPER SUMMER"), "Luckiest Guy", 120, 400,
          [hard("#c2185b", 0.0, 0.07), stroke(0.08, "#c2185b"), fill("#ffe94d")], bend=35, case="upper",
          anim_in=tslot("drop", 0.6, unit="character", stagger=0.04), tags=["arco", "verano", "divertido"],
          card="#1f8fbf"),
]

# --- calls to action ----------------------------------------------------------------------------

def cta(id, es, en, sample, font, size, weight, layers, *, tags=(), loop=None, anim_in=None, **kw):
    return Style(id, es, en, "llamadas", sample, font, size, weight, layers,
                 anim_in=anim_in or tslot("pop", 0.35, "back"), anim_out=tslot("shrink", 0.25, "easeIn"),
                 anim_loop=loop, tags=["llamada", "cta", "redes", *tags], **kw)


CTAS = [
    cta("cta-suscribete", "Suscríbete en rojo", "Red subscribe", ("SUSCRÍBETE", "SUBSCRIBE"), "Roboto", 76, 900,
        [fill("#ffffff")], box="#ff3040", box_shape="pill", box_pad=(0.65, 0.34), case="upper", spacing=0.03,
        loop=tslot("pulse", amount=5, speed=1.2), tags=["suscribete", "subscribe", "rojo"]),
    cta("cta-corazon", "Dale amor", "Show some love", ("Dale ❤", "Tap ❤"), "Fredoka", 86, 700, [fill("#ffffff")],
        box="#ff4d7d", box_shape="heart", box_pad=(0.75, 0.6), loop=tslot("pulse", amount=7, speed=1.6),
        tags=["like", "corazon", "amor"]),
    cta("cta-flecha", "Sígueme con flecha", "Follow arrow", ("Sígueme", "Follow me"), "Poppins", 80, 900,
        [fill("#111111")], box="#ffe600", box_shape="arrow", box_pad=(0.7, 0.32),
        loop=tslot("sway", angle=0, lift=0.0, speed=1.0), anim_in=tslot("slide-right", 0.4, "back"),
        tags=["sigueme", "follow", "flecha"]),
    cta("cta-comenta", "Comenta abajo", "Comment below", ("¡Comenta abajo!", "Comment below!"), "Nunito", 74, 900,
        [fill("#141414")], box="#ffffff", box_shape="speech", box_pad=(0.6, 0.38), box_border=(0.05, "#141414"),
        tags=["comenta", "comment", "dialogo"]),
    cta("cta-guarda", "Guarda este video", "Save this video", ("Guarda este video 📌", "Save this video 📌"), "Poppins",
        64, 800, [fill("#111111")], box="#ffffff", box_shape="pill", box_pad=(0.6, 0.32), box_border=(0.06, "#111111"),
        box_offset=(0.0, 0.0), tags=["guardar", "save"], card="#4b6cb7"),
    cta("cta-comparte", "Compártelo", "Share it", ("Compártelo con alguien", "Share it with someone"), "Montserrat", 74,
        900, [glow("#00e5ff", 0.25, 0.5), stroke(0.07, "#05212b"), fill("#ffffff")],
        acc=accent("lastWord", "#00e5ff"), tags=["compartir", "share"]),
    cta("cta-perfil", "Enlace en el perfil", "Link in profile", ("Enlace en el perfil 👆", "Link in profile 👆"), "Inter",
        62, 800, [fill("#ffffff")], box="#111111", box_shape="pill", box_pad=(0.6, 0.34),
        loop=tslot("float", amount=0.08, speed=0.8), tags=["link", "bio", "perfil"], card="#e9b949"),
    cta("cta-nuevo", "¡Nuevo!", "New!", ("¡NUEVO!", "NEW!"), "Bangers", 110, 400, [fill("#e3001b")], box="#ffe600",
        box_shape="burst", box_pad=(0.8, 0.7), box_border=(0.05, "#e3001b"), spacing=0.03,
        loop=tslot("jitter", amount=1.2, angle=2.5, speed=10), tags=["nuevo", "new", "comic"]),
    cta("cta-espera-final", "Espera al final", "Wait for the end", ("Espera al final… ⏳", "Wait for the end… ⏳"),
        "Bangers", 100, 400, [hard("#000000", 0.06, 0.07), stroke(0.06), fill("#ffffff")],
        acc=accent("lastWord", "#ffd23f"), spacing=0.02, tags=["espera", "gancho", "hook"]),
    cta("cta-parte-dos", "Parte 2", "Part 2", ("Parte 2 ➜", "Part 2 ➜"), "Archivo Black", 84, 400, [fill("#ffffff")],
        box="#7c3aed", box_shape="ticket", box_pad=(0.65, 0.34), anim_in=tslot("slide-left", 0.4, "back"),
        tags=["parte 2", "serie", "continuara"]),
    cta("cta-desliza", "Desliza", "Swipe", ("Desliza ➜", "Swipe ➜"), "Outfit", 92, 800,
        [glow("#ffffff", 0.3, 0.45), fill("#ffffff")], spacing=0.08, case="upper",
        loop=tslot("wave", amount=0.04, frequency=1.2, phase=20), tags=["desliza", "carrusel", "swipe"], card="#ff6a3d"),
    cta("cta-mira-esto", "¡Mira esto!", "Look at this!", ("¡MIRA ESTO!", "LOOK AT THIS!"), "Luckiest Guy", 90, 400,
        [fill("#141414")], box="#ffffff", box_shape="shout", box_pad=(0.75, 0.55), box_border=(0.06, "#141414"),
        loop=tslot("jitter", amount=1.0, angle=1.5, speed=8), tags=["mira", "comic", "gancho"], card="#ff8a00"),
    cta("cta-en-vivo", "En vivo", "Live now", ("● EN VIVO", "● LIVE"), "Inter", 66, 800, [fill("#ffffff")],
        box="#e8112d", box_pad=(0.5, 0.26), box_radius=0.16, spacing=0.12, case="upper",
        loop=tslot("breathe", amount=0.25, speed=0.9), tags=["en vivo", "live", "directo"]),
    cta("cta-opina", "¿Tú qué opinas?", "What do you think?", ("¿Tú qué opinas?", "What do you think?"), "Patrick Hand",
        92, 400, [fill("#333333")], box="#fff27a", box_shape="note", box_pad=(0.6, 0.45),
        anim_in=tslot("drop", 0.5, unit="block"), tags=["pregunta", "opinion", "nota"], card="#2f6f62"),
]

# --- lower thirds -------------------------------------------------------------------------------

def lower(id, es, en, sample, font, size, weight, layers, *, tags=(), anim_in=None, anim_out=None, **kw):
    kw.setdefault("align", "left")
    return Style(id, es, en, "tercios", sample, font, size, weight, layers,
                 anim_in=anim_in or tslot("slide-right", 0.45, "easeOut"),
                 anim_out=anim_out or tslot("slide-left", 0.35, "easeIn"), valign="bottom",
                 tags=["tercio inferior", "lower third", "nombre", *tags], **kw)


NAME = ("Ana Torres\nDiseñadora gráfica", "Ana Torres\nGraphic designer")

LOWER_THIRDS = [
    lower("ter-caja-oscura", "Nombre en caja oscura", "Dark name box", NAME, "Poppins", 56, 700, [fill("#ffffff")],
          box="#111111e6", box_pad=(0.45, 0.3), box_radius=0.12, acc=accent("firstWord", "#ffc83d"), line=1.25,
          tags=["entrevista", "caja"]),
    lower("ter-cinta-azul", "Cinta azul", "Blue ribbon", ("Carlos Méndez · Chef", "Carlos Méndez · Chef"), "Montserrat",
          58, 800, [fill("#ffffff")], box="#2f5bff", box_shape="ribbon", box_pad=(0.7, 0.32), tags=["cinta", "ribbon"]),
    lower("ter-etiqueta", "Etiqueta amarilla", "Yellow tag", ("Laura Kim · Fotógrafa", "Laura Kim · Photographer"), "Inter",
          54, 800, [fill("#151515")], box="#ffd60a", box_shape="tag", box_pad=(0.6, 0.3), tags=["etiqueta", "tag"]),
    lower("ter-subrayado", "Subrayado de color", "Colour underline", NAME, "Montserrat", 58, 700, [fill("#ffffff")],
          underline=("#ff4d4d", 0.09, 0.14), acc=accent("firstWord", "#ffffff", size=1.15), line=1.3,
          tags=["subrayado", "minimal"]),
    lower("ter-ubicacion", "Ubicación", "Location", ("📍 Casco antiguo", "📍 Old town"), "Outfit", 62, 700,
          [fill("#ffffff")], box="#00000099", box_shape="pill", box_pad=(0.55, 0.28), tags=["ubicacion", "location", "viaje"]),
    lower("ter-usuario", "Usuario de redes", "Social handle", ("@tu_usuario", "@your_handle"), "Plus Jakarta Sans", 60, 800,
          [fill("#111111")], box="#ffffff", box_shape="pill", box_pad=(0.6, 0.3), box_border=(0.05, "#ff4fb8"),
          tags=["usuario", "handle", "redes"], card="#5a3fd1"),
    lower("ter-serif-oro", "Serif con línea dorada", "Serif gold line", ("Isabel Rojas\nAbogada", "Isabel Rojas\nLawyer"),
          "Cormorant Garamond", 72, 600, [shadow(dy=0.03, blur=0.1, opacity=0.6), fill("#fbf6ec")], italic=True,
          underline=("#d4af37", 0.04, 0.18), line=1.2, anim_in=tslot("fade-up-char", 0.6, "easeOut", unit="word"),
          tags=["elegante", "serif", "dorado"]),
    lower("ter-entrevista", "Rótulo de entrevista", "Interview strap", ("MARTA DÍAZ\nDirectora del proyecto",
                                                                        "MARTA DÍAZ\nProject director"),
          "Barlow", 54, 700, [fill("#ffffff")], box="#1e40af", box_style="line", box_pad=(0.4, 0.16),
          acc=accent("firstWord", "#ffd84d"), line=1.35, anim_in=tslot("wipe", 0.4, "easeOut", angle=0),
          tags=["entrevista", "noticias"]),
    lower("ter-vidrio", "Vidrio esmerilado", "Frosted glass", ("Diego Ruiz · Músico", "Diego Ruiz · Musician"), "Manrope",
          56, 700, [fill("#ffffff")], box="#ffffff2e", box_pad=(0.55, 0.32), box_radius=0.3,
          box_border=(0.03, "#ffffff80"), tags=["vidrio", "glass", "moderno"], card="#355c7d"),
    lower("ter-a-mano", "Nota a mano", "Handwritten note", ("mi lugar favorito ♡", "my favourite place ♡"), "Caveat", 90,
          700, [shadow(dy=0.03, blur=0.08, opacity=0.6), fill("#ffffff")],
          underline=("#ffffff", 0.035, 0.1), anim_in=tslot("typewriter", 0.3, "linear", unit="character", stagger=0.05),
          tags=["a mano", "vlog", "nota"]),
    lower("ter-fecha", "Fecha", "Date", ("12 · 05 · 2026", "05 · 12 · 2026"), "Teko", 84, 600, [fill("#ffffff")],
          box="#00000099", box_pad=(0.4, 0.12), spacing=0.12, tags=["fecha", "date", "vlog"]),
    lower("ter-marcador", "Marcador deportivo", "Sports strap", ("GOL · MINUTO 89", "GOAL · MINUTE 89"), "Teko", 78, 700,
          [fill("#111111")], box="#facc15", box_style="line", box_pad=(0.35, 0.06), case="upper", spacing=0.04,
          anim_in=tslot("skew-slide", 0.35, "easeOut", unit="block"), tags=["deportes", "sports", "marcador"]),
]

# --- prices and offers --------------------------------------------------------------------------

def price(id, es, en, sample, font, size, weight, layers, *, tags=(), loop=None, anim_in=None, **kw):
    return Style(id, es, en, "precios", sample, font, size, weight, layers,
                 anim_in=anim_in or tslot("zoom-in", 0.35, "back"), anim_out=tslot("shrink", 0.25, "easeIn"),
                 anim_loop=loop, tags=["precio", "oferta", "venta", *tags], **kw)


PRICES = [
    price("pre-estallido", "Estallido de oferta", "Sale burst", ("-50%", "-50%"), "Anton", 150, 400, [fill("#ffffff")],
          box="#ff1f3d", box_shape="burst", box_pad=(0.6, 0.55), box_border=(0.04, "#ffffff"),
          loop=tslot("pulse", amount=6, speed=1.5), tags=["descuento", "porcentaje"]),
    price("pre-etiqueta-verde", "Etiqueta de precio", "Price tag", ("$9.99", "$9.99"), "Poppins", 110, 800,
          [fill("#ffffff")], box="#16a34a", box_shape="tag", box_pad=(0.55, 0.28), tags=["etiqueta", "tag"]),
    price("pre-ticket", "Ticket 2x1", "2-for-1 ticket", ("2x1", "2 FOR 1"), "Archivo Black", 130, 400,
          [fill("#ffffff")], box="#ff7a00", box_shape="ticket", box_pad=(0.65, 0.32), tags=["2x1", "promo"]),
    price("pre-cinta-oferta", "Cinta de oferta", "Offer ribbon", ("OFERTA", "SALE"), "Bebas Neue", 130, 400,
          [fill("#ffffff")], box="#d90429", box_shape="ribbon", box_pad=(0.8, 0.22), spacing=0.08,
          anim_in=tslot("wipe", 0.4, "easeOut", angle=0), tags=["cinta", "ribbon"]),
    price("pre-precio-gigante", "Precio gigante", "Giant price", ("$29", "$29"), "Anton", 220, 400,
          [hard("#000000", 0.07, 0.07), stroke(0.05), fill("#ffe600")], loop=tslot("jitter", amount=0.8, angle=1, speed=6),
          tags=["precio", "grande"], card="#e63946"),
    price("pre-tachado", "Antes y ahora", "Was and now", ("Antes $49 · Hoy $29", "Was $49 · Now $29"), "Montserrat", 74,
          900, [stroke(0.06, "#111111"), fill("#ffffff")], acc=accent("lastWord", "#111111", pill="#ffe600", size=1.35),
          tags=["antes", "ahora", "rebaja"]),
    price("pre-envio-gratis", "Envío gratis", "Free shipping", ("ENVÍO GRATIS 🚚", "FREE SHIPPING 🚚"), "Inter", 66, 900,
          [fill("#ffffff")], box="#10b981", box_shape="pill", box_pad=(0.55, 0.3), spacing=0.04,
          anim_in=tslot("slide-right", 0.4, "back"), tags=["envio", "gratis", "delivery"]),
    price("pre-viernes-negro", "Viernes de ofertas", "Big sale Friday", ("BLACK FRIDAY", "BLACK FRIDAY"), "Bebas Neue", 150,
          400, [fill("#ffd400")], box="#000000", box_pad=(0.45, 0.16), spacing=0.06,
          anim_in=tslot("glitch-in", 0.3, "linear"), tags=["black friday", "viernes", "ofertas"], card="#c9c9c9"),
    price("pre-sello", "Sello de liquidación", "Clearance stamp", ("LIQUIDACIÓN", "CLEARANCE"), "Black Ops One", 100, 400,
          [stroke(0.04, "#d7263d", align="center", sketchLength=8, sketchDeviation=2.5), fill("#d7263d", alpha=0.92)],
          box="#00000000", box_pad=(0.35, 0.2), box_border=(0.06, "#d7263d"), box_radius=0.1, card="light",
          anim_in=tslot("stamp", 0.35, "easeIn"), tags=["sello", "stamp", "liquidacion"]),
    price("pre-solo-hoy", "Solo hoy", "Today only", ("Solo hoy", "Today only"), "Shrikhand", 130, 400,
          [glow("#ff8a3d", 0.3, 0.6), stroke(0.05, "#5b1600"), fill(grad([(0, "#fff3b0"), (1, "#ff7a2f")], 90))],
          tags=["solo hoy", "urgente"], card="#3b0d3f"),
    price("pre-cupon", "Cupón", "Coupon", ("CUPÓN: AHORRA10", "COUPON: SAVE10"), "Sora", 62, 800,
          [fill("#7a1fa2")], box="#ffffff", box_shape="ticket", box_pad=(0.6, 0.32), box_border=(0.04, "#7a1fa2"),
          spacing=0.04, tags=["cupon", "codigo", "coupon"], card="#7a1fa2"),
    price("pre-neon-descuento", "Descuento neón", "Neon discount", ("-30%", "-30%"), "Audiowide", 170, 400,
          neon_stack("#39ff14"), loop=tslot("flicker", intensity=0.2, speed=6), tags=["neon", "descuento"], card="night"),
]

# --- quotes -------------------------------------------------------------------------------------

def quote(id, es, en, sample, font, size, weight, layers, *, tags=(), anim_in=None, **kw):
    kw.setdefault("line", 1.3)
    return Style(id, es, en, "citas", sample, font, size, weight, layers,
                 anim_in=anim_in or tslot("blur-in-words", 0.8, "easeOut"), anim_out=tslot("fade", 0.5, "easeIn"),
                 tags=["cita", "frase", "quote", *tags], **kw)


Q1 = ("La vida es lo que pasa mientras haces planes", "Life is what happens while you make plans")
Q2 = ("Sé la energía que quieres atraer", "Be the energy you want to attract")
Q3 = ("Poco a poco se llega lejos", "Little by little, one goes far")

QUOTES = [
    quote("cita-serif-cursiva", "Serif en cursiva", "Italic serif", Q1, "Playfair Display", 76, 400,
          [shadow(dy=0.03, blur=0.14, opacity=0.7), fill("#ffffff")], italic=True, tags=["serif", "elegante"]),
    quote("cita-a-mano", "Escrita a mano", "Handwritten", Q2, "Caveat", 104, 600, [fill("#ffffff")],
          anim_in=tslot("typewriter", 0.3, "linear", unit="character", stagger=0.04), tags=["a mano", "diario"]),
    quote("cita-maquina", "Hoja de máquina", "Typewritten page", Q3, "Special Elite", 70, 400, [fill("#1d1d1d")],
          card="warm", anim_in=tslot("typewriter", 0.3, "linear", unit="character", stagger=0.05, caret=True),
          tags=["maquina de escribir", "vintage"]),
    quote("cita-oro", "Comillas doradas", "Golden quote", ("«Todo llega a su tiempo»", "“Everything comes in its time”"),
          "Cormorant Garamond", 96, 600, [glow("#ffd27a", 0.25, 0.4),
                                          fill(grad([(0, "#fff3cf"), (1, "#c99a3c")], 90))], italic=True,
          tags=["dorado", "elegante"], card="night"),
    quote("cita-minimal", "Minimal negra", "Black minimal", Q2, "Inter", 66, 500, [fill("#1a1a1a")], spacing=0.01,
          card="light", anim_in=tslot("rise-by-word", 0.5, "easeOut", unit="word", stagger=0.08, rise=0.3, blur=6),
          tags=["minimal", "limpio"]),
    quote("cita-tarjeta", "Tarjeta blanca", "White card", Q3, "Lora", 64, 400, [fill("#222222")], italic=True,
          box="#ffffff", box_pad=(0.9, 0.7), box_radius=0.35, tags=["tarjeta", "card"], card="#8fb8b0"),
    quote("cita-resaltada", "Palabra resaltada", "Highlighted word", ("La paciencia también es una forma de fe",
                                                                       "Patience is a form of faith too"),
          "Merriweather", 66, 700, [fill("#ffffff")], acc=accent("keywords", "#111111", pill="#ffe36e", pad=0.08,
                                                                 radius=0.04), tags=["resaltado", "clave"]),
    quote("cita-luz-calida", "Luz cálida", "Warm glow", Q1, "DM Serif Display", 80, 400,
          [glow("#ffb36b", 0.4, 0.5), fill("#fff1e0")], tags=["calido", "suave"], card="#2b1a12"),
    quote("cita-caligrafia", "Caligrafía", "Calligraphy", ("Siempre juntos", "Always together"), "Pinyon Script", 130, 400,
          [shadow(dy=0.03, blur=0.1, opacity=0.6), fill("#ffffff")], tags=["caligrafia", "boda", "amor"]),
    quote("cita-pizarra", "Pizarra", "Chalkboard", ("HOY ES UN BUEN DÍA PARA EMPEZAR", "TODAY IS A GOOD DAY TO START"),
          "Amatic SC", 110, 700, [fill("#f4f1e8", alpha=0.95)], line=1.05, card="chalk",
          anim_in=tslot("wipe", 0.8, "easeOut", angle=0), tags=["pizarra", "tiza", "escuela"]),
    quote("cita-poema", "Poema", "Poem", ("y en el silencio\nencontré mi voz", "and in the silence\nI found my voice"),
          "EB Garamond", 78, 400, [fill("#f6f0e6")], italic=True, line=1.45,
          anim_in=tslot("fade-up-char", 0.7, "easeOut", unit="line", stagger=0.4), tags=["poema", "poesia"]),
    quote("cita-neon-suave", "Neón suave", "Soft neon", ("Hazlo con amor", "Do it with love"), "Courgette", 110, 400,
          [glow("#ff7eb6", 0.45, 0.6), glow("#ff7eb6", 0.12, 0.9, id="glow2"), fill("#fff0f6")],
          tags=["neon", "amor", "rosa"], card="night"),
]

STYLES = SUBTITLES + TITLES + CTAS + LOWER_THIRDS + PRICES + QUOTES
