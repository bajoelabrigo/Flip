"""Text styles, part B: neon, 3D, retro and Y2K, elegant, kids, gaming, horror and special days.

Same units as styles_a.py. Special days are the ones the whole world shares (plan-stock.md): Christmas,
New Year, Valentine's, birthdays, Easter, Mother's and Father's Day, graduations, Lunar New Year, Eid
and Diwali.
"""

from __future__ import annotations

from kit import (Style, accent, extrude, fill, fx, glow, grad, hard, hollow_fill, neon_stack, shadow, stroke,
                 tslot)


def styled(category, base_tags, anim_in, anim_out, anim_loop=None):
    def make(id, es, en, sample, font, size, weight, layers, *, tags=(), loop=None, anim_in_=None, **kw):
        return Style(id, es, en, category, sample, font, size, weight, layers, anim_in=anim_in_ or anim_in,
                     anim_out=anim_out, anim_loop=loop if loop is not None else anim_loop,
                     tags=[*base_tags, *tags], **kw)
    return make


# --- neon ---------------------------------------------------------------------------------------

neon = styled("neon", ["neon", "luz", "noche"], tslot("flicker-in", 0.8, "linear"), tslot("fade", 0.3, "easeIn"))
N = dict(card="night")

NEON = [
    neon("neon-rosa", "Neón rosa", "Pink neon", ("Abierto", "Open"), "Pacifico", 120, 400, neon_stack("#ff2fd0"),
         tags=["rosa", "script"], **N),
    neon("neon-celeste", "Neón celeste", "Ice-blue neon", ("NOCHE DE CINE", "MOVIE NIGHT"), "Monoton", 96, 400,
         neon_stack("#22d3ff", line=0.02), spacing=0.04, tags=["celeste", "retro"], **N),
    neon("neon-verde", "Neón verde ácido", "Acid green neon", ("NIVEL 2", "LEVEL 2"), "Audiowide", 130, 400,
         neon_stack("#39ff14"), tags=["verde", "gaming"], **N),
    neon("neon-amarillo", "Neón amarillo", "Yellow neon", ("Café & charla", "Coffee & chat"), "Yellowtail", 120, 400,
         neon_stack("#ffd400"), tags=["amarillo", "cafe"], **N),
    neon("neon-violeta", "Neón violeta", "Violet neon", ("DJ SET", "DJ SET"), "Righteous", 150, 400,
         neon_stack("#b026ff"), spacing=0.06, loop=tslot("flicker", intensity=0.15, speed=5), tags=["violeta", "fiesta"], **N),
    neon("neon-rojo", "Neón rojo intermitente", "Flickering red neon", ("ABIERTO 24H", "OPEN 24H"), "Bebas Neue", 150, 400,
         neon_stack("#ff1e3c", pulse=True), spacing=0.05, tags=["rojo", "intermitente", "letrero"], **N),
    neon("neon-azul", "Neón azul eléctrico", "Electric blue neon", ("Bienvenidos", "Welcome"), "Sacramento", 150, 400,
         neon_stack("#2f7bff"), tags=["azul", "bienvenida"], **N),
    neon("neon-naranja", "Neón naranja", "Orange neon", ("Pizza", "Pizza"), "Lobster", 160, 400,
         neon_stack("#ff8a1f"), tags=["naranja", "restaurante"], **N),
    neon("neon-blanco", "Neón blanco cálido", "Warm white neon", ("good vibes only", "good vibes only"), "Satisfy", 120,
         400, neon_stack("#ffd9a0", core="#fffaf0"), tags=["blanco", "calido"], **N),
    neon("neon-dos-tonos", "Neón de dos tonos", "Two-tone neon", ("LOVE", "LOVE"), "Monoton", 150, 400,
         [glow("#00e5ff", 0.8, 0.5, id="glow2"), glow("#ff2fd0", 0.25, 0.95), stroke(0.03, "#ff2fd0"), fill("#ffffff")],
         spacing=0.04, tags=["dos tonos", "amor"], **N),
    neon("neon-tubo-apagado", "Tubo de neón apagado", "Unlit neon tube", ("Cerrado", "Closed"), "Pacifico", 130, 400,
         [glow("#ff4f9a", 0.2, 0.35), stroke(0.05, "#ff4f9a", align="center"), hollow_fill()],
         anim_in_=tslot("fade", 0.6, "easeOut"), tags=["contorno", "apagado"], **N),
    neon("neon-pulso", "Neón que late", "Pulsing neon", ("FIESTA", "PARTY"), "Orbitron", 130, 900,
         neon_stack("#ff3df2", pulse=True), spacing=0.06, loop=tslot("pulse", amount=3, speed=2.0),
         tags=["late", "pulso", "fiesta"], **N),
    neon("neon-letrero", "Letrero con marco", "Framed sign", ("Bar", "Bar"), "Yellowtail", 150, 400,
         neon_stack("#ff6ad5"), box="#00000000", box_pad=(0.5, 0.25), box_radius=0.25, box_border=(0.04, "#5ce1ff"),
         tags=["letrero", "marco", "sign"], **N),
    neon("neon-arcoiris", "Neón arcoíris", "Rainbow neon", ("Vibras", "Vibes"), "Righteous", 160, 400,
         [glow("#ffffff", 0.6, 0.4, id="glow2"),
          glow("#ff4fd8", 0.22, 0.8),
          stroke(0.035, grad([(0, "#ff3b3b"), (0.25, "#ffd400"), (0.5, "#39ff14"), (0.75, "#00e5ff"), (1, "#b026ff")], 0)),
          fill("#ffffff")], tags=["arcoiris", "rainbow", "colores"], **N),
]

# --- 3D -----------------------------------------------------------------------------------------

d3 = styled("3d", ["3d", "relieve", "volumen"], tslot("pop", 0.4, "back"), tslot("fade-scale", 0.3, "easeIn"))

THREE_D = [
    d3("d3-amarillo-rojo", "3D amarillo y rojo", "Yellow-red 3D", ("¡WOW!", "WOW!"), "Titan One", 160, 400,
       [extrude(0.16, "#d7261e"), stroke(0.04, "#5a0d08"), fill("#ffe600")], tags=["amarillo", "comic"], card="#1d6fb8"),
    d3("d3-blanco-negro", "Bloque blanco 3D", "White block 3D", ("NUEVO", "NEW"), "Bungee", 150, 400,
       [extrude(0.2, "#1a1a1a", steps=16, darken=0.1), stroke(0.03, "#1a1a1a"), fill("#ffffff")],
       tags=["blanco", "bloque"], card="#ff5a5f"),
    d3("d3-chicle", "Chicle 3D", "Bubblegum 3D", ("Dulce", "Sweet"), "Lilita One", 160, 400,
       [extrude(0.14, "#9b2d86"), stroke(0.05, "#ffffff"), fill(grad([(0, "#ffd1ec"), (1, "#ff6fc7")], 90))],
       tags=["rosa", "dulce"], card="#7fd1c7"),
    d3("d3-dorado", "Oro macizo", "Solid gold", ("PREMIOS", "AWARDS"), "Alfa Slab One", 130, 400,
       [shadow(dy=0.12, blur=0.16, opacity=0.6), extrude(0.12, "#6b4300", darken=0.4),
        fill(grad([(0, "#fff2b0"), (0.5, "#e8b923"), (1, "#a8700a")], 90))], tags=["dorado", "gold", "premio"],
       card="night"),
    d3("d3-hielo", "Hielo", "Ice", ("FRESCO", "FRESH"), "Passion One", 170, 900,
       [extrude(0.13, "#1b4f9c"), stroke(0.035, "#e8f7ff"), fill(grad([(0, "#ffffff"), (1, "#7fd8ff")], 90))],
       tags=["hielo", "frio", "azul"], card="#0f2a4a"),
    d3("d3-isometrico", "Isométrico", "Isometric", ("CUBO", "CUBE"), "Russo One", 150, 400,
       [extrude(0.18, "#3b1e8a", angle=135, steps=16, darken=0.2), fill("#8ef6e4")], tags=["isometrico", "geometrico"],
       card="#fdf0d5"),
    d3("d3-sombra-larga", "Sombra infinita", "Endless shadow", ("PLAN", "PLAN"), "Archivo Black", 170, 400,
       [extrude(0.45, "#0b3d4a", steps=32, darken=0.0), fill("#ffffff")], tags=["sombra larga", "flat"],
       card="#127c8f"),
    d3("d3-relieve", "Relieve grabado", "Embossed", ("ARTESANAL", "HANDMADE"), "Cinzel", 110, 900,
       [shadow("#ffffff", -0.025, -0.025, 0.02, 0.55, id="shadow2"), shadow("#000000", 0.03, 0.03, 0.03, 0.55),
        fill("#8a8f98")], spacing=0.06, tags=["relieve", "emboss", "piedra"], card="#8a8f98"),
    d3("d3-bloques-retro", "Letras de bloque", "Block letters", ("PLAY", "PLAY"), "Bungee Shade", 160, 400,
       [fill("#ff4f5e")], tags=["bloque", "retro"], card="#fff2cc"),
    d3("d3-plastilina", "Plastilina", "Clay", ("hola", "hello"), "Fredoka", 180, 700,
       [shadow(dy=0.1, blur=0.12, opacity=0.45), extrude(0.09, "#d0631d", steps=10),
        fill(grad([(0, "#ffd08a"), (1, "#ff8a3d")], 90))], tags=["plastilina", "clay", "redondo"], card="#a8e6cf"),
    d3("d3-contorno-pop", "3D con doble borde", "Double-edge 3D", ("TOP 10", "TOP 10"), "Luckiest Guy", 150, 400,
       [extrude(0.12, "#111111"), stroke(0.14, "#ffffff", id="stroke2"), stroke(0.06, "#111111"), fill("#3df5a6")],
       tags=["sticker", "top"], card="#6c4ab6"),
    d3("d3-cristal", "Cristal", "Glass", ("ZEN", "ZEN"), "Outfit", 190, 900,
       [shadow(dy=0.08, blur=0.2, opacity=0.35), extrude(0.08, "#8fd3ff", darken=0.2),
        fill(grad([(0, "#ffffffd9"), (1, "#bfe6ff99")], 135)), stroke(0.02, "#ffffff", align="inside")],
       tags=["cristal", "glass", "suave"], card="#4a6fa5"),
]

# --- retro and Y2K ------------------------------------------------------------------------------

retro = styled("retro", ["retro", "vintage"], tslot("slide-up", 0.45, "back", unit="word"),
               tslot("fade", 0.3, "easeIn"))

RETRO = [
    retro("ret-synthwave", "Synthwave", "Synthwave", ("RETRO\nFUTURO", "RETRO\nFUTURE"), "Orbitron", 120, 900,
          [glow("#ff2bd6", 0.35, 0.6), extrude(0.07, "#3a0b5e"), stroke(0.025, "#ffe9ff"),
           fill(grad([(0, "#ffe259"), (0.55, "#ff6f61"), (1, "#c2187a")], 90))], line=1.0,
          tags=["80s", "synthwave", "ochentas"], card="night"),
    retro("ret-vhs", "VHS", "VHS", ("REC ● 00:12", "REC ● 00:12"), "VT323", 130, 400,
          [fill("#ff2a6d", id="glitcha", offsetX=-0.025, blend="screen", opacity=0.8),
           fill("#05d9e8", id="glitchb", offsetX=0.025, blend="screen", opacity=0.8), fill("#f8f8f2")],
          loop=tslot("jitter", amount=1.0, angle=0, speed=14), tags=["vhs", "90s", "camara"], card="#1b1b2f"),
    retro("ret-pixel", "Pixel arcade", "Arcade pixel", ("GAME OVER", "GAME OVER"), "Press Start 2P", 76, 400,
          [hard("#c1121f", 0.08, 0.08), fill("#ffd60a")], line=1.4, tags=["pixel", "arcade", "8 bits"], card="#0b0b14"),
    retro("ret-setentas", "Groovy 70s", "Groovy 70s", ("Buena onda", "Good vibes"), "Shrikhand", 140, 400,
          [hard("#5c2a0f", 0.12, 0.12, id="shadow3"), hard("#d1495b", 0.08, 0.08, id="shadow2"),
           hard("#edae49", 0.04, 0.04), fill("#fff1d6")], tags=["70s", "setentas", "groovy"], card="#00798c"),
    retro("ret-disco", "Disco", "Disco", ("DISCO", "DISCO"), "Monoton", 160, 400,
          [glow("#ffffff", 0.3, 0.45), fill(fx("shimmer", "#ffffff", speed=0.5, scale=5, intensity=0.85))],
          tags=["disco", "fiesta", "brillo"], card="#2d0b45"),
    retro("ret-y2k-burbuja", "Burbuja Y2K", "Y2K bubble", ("y2k baby", "y2k baby"), "Sniglet", 150, 800,
          [glow("#ff8dc7", 0.3, 0.7), stroke(0.07, "#ffffff"),
           fill(grad([(0, "#ffffff"), (0.4, "#c9b6ff"), (0.6, "#7d6bff"), (1, "#e6dcff")], 90))],
          tags=["y2k", "2000", "burbuja"], card="#b5e8ff"),
    retro("ret-y2k-cromo", "Cromo Y2K", "Y2K chrome", ("STAR", "STAR"), "Righteous", 170, 400,
          [glow("#a0e9ff", 0.25, 0.5), stroke(0.025, "#2b2b3a"),
           fill(fx("chrome", "#ffffff", speed=0.15, bands=2.5, colorA="#f4f8ff", colorB="#3b4a6b"))],
          tags=["y2k", "cromo", "chrome"], card="#ff9fd6"),
    retro("ret-oeste", "Lejano oeste", "Wild West", ("SE BUSCA", "WANTED"), "Rye", 120, 400,
          [hard("#3d1f0a", 0.05, 0.06), fill("#f2d6a2")], spacing=0.04, tags=["oeste", "western", "cowboy"],
          card="#8a4b2a"),
    retro("ret-cafeteria", "Cafetería 50s", "50s diner", ("Malteadas", "Milkshakes"), "Lobster", 140, 400,
          [hard("#ffffff", 0.0, 0.07, id="shadow2"), stroke(0.05, "#ffffff"), fill("#e63946")],
          tags=["50s", "diner", "cafeteria"], card="#a8dadc"),
    retro("ret-noventas", "Sticker 90s", "90s sticker", ("TOTAL", "TOTALLY"), "Bungee", 140, 400,
          [hard("#14b8a6", 0.09, 0.09), stroke(0.09, "#ffffff"), fill("#7c3aed")], tags=["90s", "noventas", "sticker"],
          card="#ffe66d"),
    retro("ret-postal", "Postal vintage", "Vintage postcard", ("Saludos desde la playa", "Greetings from the beach"),
          "Alfa Slab One", 96, 400, [hard("#6b3e26", 0.05, 0.05), stroke(0.04, "#fff3dd"), fill("#e76f51")], line=1.05,
          tags=["postal", "viaje", "vintage"], card="#f4e1c1"),
    retro("ret-cine-mudo", "Cine mudo", "Silent film", ("Fin", "The End"), "Abril Fatface", 150, 400,
          [fill("#f2f2f2")], box="#111111", box_pad=(0.8, 0.45), box_radius=0.06, box_border=(0.03, "#f2f2f2"),
          anim_in_=tslot("flicker-in", 0.8, "linear"), tags=["cine mudo", "blanco y negro"], card="#3a3a3a"),
    retro("ret-arcade-neon", "Arcade neón", "Neon arcade", ("INSERT COIN", "INSERT COIN"), "Press Start 2P", 64, 400,
          neon_stack("#00f5d4", wide=0.6, tight=0.2, line=0.02), loop=tslot("flicker", intensity=0.25, speed=3),
          line=1.5, tags=["arcade", "pixel", "neon"], card="night"),
    retro("ret-ochentas-cromo", "Cromo ochentero", "80s chrome", ("TURBO", "TURBO"), "Exo 2", 160, 900,
          [glow("#00d0ff", 0.25, 0.45), stroke(0.03, "#0a0f2c"),
           fill(grad([(0, "#e8f6ff"), (0.48, "#7aa7d6"), (0.5, "#2b2650"), (0.62, "#d65db1"), (1, "#ffd8f2")], 90))],
          tags=["80s", "cromo", "turbo"], card="#0a0f2c"),
]

# --- elegant and weddings -----------------------------------------------------------------------

elegant = styled("elegante", ["elegante", "boda", "lujo"], tslot("blur-in", 0.9, "easeOut"),
                 tslot("fade", 0.6, "easeIn"))
GOLD = grad([(0, "#fff4cf"), (0.5, "#d9a93f"), (1, "#9c6b17")], 90)
ROSE = grad([(0, "#ffe3dc"), (0.5, "#e8a598"), (1, "#b76e5d")], 90)

ELEGANT = [
    elegant("ele-oro-script", "Oro en caligrafía", "Gold script", ("Nuestra boda", "Our wedding"), "Great Vibes", 140, 400,
            [shadow(dy=0.04, blur=0.12, opacity=0.55), fill(GOLD)], tags=["dorado", "script"], card="night"),
    elegant("ele-brillo-blanco", "Blanco luminoso", "Luminous white", ("Para siempre", "Forever"), "Alex Brush", 150, 400,
            [glow("#ffffff", 0.3, 0.55), fill("#ffffff")], tags=["blanco", "luz"], card="#5a6b7a"),
    elegant("ele-iniciales", "Iniciales", "Monogram", ("A & M", "A & M"), "Cinzel Decorative", 150, 700,
            [fill(GOLD), fill(fx("shine", "#00000000", speed=0.3, width=0.2, angle=25, intensity=0.9), id="shine",
                             blend="screen")], spacing=0.08, tags=["iniciales", "monograma", "dorado"], card="night"),
    elegant("ele-rosa-oro", "Oro rosa", "Rose gold", ("Save the date", "Save the date"), "Parisienne", 130, 400,
            [shadow(dy=0.03, blur=0.1, opacity=0.4), fill(ROSE)], tags=["oro rosa", "save the date"], card="light"),
    elegant("ele-champan", "Champán", "Champagne", ("Celebremos", "Let's celebrate"), "Tangerine", 190, 700,
            [glow("#f7e7b4", 0.25, 0.5), fill("#f7e7c6")], tags=["champan", "fiesta"], card="#2a2320"),
    elegant("ele-marfil", "Marfil espaciado", "Ivory spaced", ("SOFÍA & LUCAS", "SOFÍA & LUCAS"), "Marcellus", 76, 400,
            [fill("#fbf7ee")], spacing=0.22, anim_in_=tslot("snap-together", 1.0, "easeOut"),
            tags=["marfil", "nombres"], card="#8c7b6b"),
    elegant("ele-prata", "Serif de revista", "Magazine serif", ("Elegancia", "Elegance"), "Prata", 130, 400,
            [fill("#1b1b1b")], card="light", tags=["serif", "moda"]),
    elegant("ele-bodoni-negro", "Bodoni negro", "Black Bodoni", ("Alta costura", "Haute couture"), "Bodoni Moda", 120,
            700, [fill("#0d0d0d")], italic=False, spacing=0.01, card="warm", tags=["moda", "couture"]),
    elegant("ele-rubor", "Rubor", "Blush", ("Baby shower", "Baby shower"), "Yeseva One", 120, 400,
            [hard("#f7c6d0", 0.05, 0.05), fill("#b05570")], tags=["rosa", "baby shower"], card="#fff0f3"),
    elegant("ele-plata", "Plata", "Silver", ("25 años", "25 years"), "Cormorant Garamond", 140, 700,
            [shadow(dy=0.04, blur=0.12, opacity=0.6), stroke(0.015, "#5d6670"),
             fill(grad([(0, "#ffffff"), (0.5, "#b8c0c8"), (1, "#7c8590")], 90))], tags=["plata", "aniversario"],
            card="#1d2430"),
    elegant("ele-allura", "Firma", "Signature", ("con cariño, Sofía", "with love, Sofía"), "Allura", 140, 400,
            [fill("#ffffff")], anim_in_=tslot("wipe", 1.0, "easeInOut", angle=0, softness=0.4),
            tags=["firma", "signature"], card="#a47e6b"),
    elegant("ele-esmeralda", "Esmeralda y oro", "Emerald and gold", ("Gala", "Gala"), "Cinzel", 160, 900,
            [glow("#e8c76a", 0.2, 0.4), stroke(0.02, "#e8c76a"), fill("#0f5c45")], spacing=0.1,
            tags=["esmeralda", "gala"], card="#f6efe0"),
]

# --- kids and fun -------------------------------------------------------------------------------

kids = styled("infantil", ["infantil", "ninos", "divertido"], tslot("bounce", 0.7, unit="character", stagger=0.04),
              tslot("shrink", 0.3, "easeIn"))
RAINBOW = grad([(0, "#ff4d4d"), (0.2, "#ffa84d"), (0.4, "#ffe14d"), (0.6, "#5ee36a"), (0.8, "#4db8ff"),
                (1, "#a66bff")], 0, space="glyph")

KIDS = [
    kids("inf-arcoiris", "Arcoíris", "Rainbow", ("¡Hola amigos!", "Hello friends!"), "Chewy", 130, 400,
         [shadow(dy=0.06, blur=0.06, opacity=0.35), stroke(0.09, "#ffffff"), fill(RAINBOW)], tags=["arcoiris", "colores"],
         card="#4d7cff"),
    kids("inf-pastel", "Pastel", "Pastel", ("Hora del cuento", "Story time"), "Bubblegum Sans", 120, 400,
         [stroke(0.1, "#ffffff"), fill("#ff9ec4")], acc=accent("everyOther", "#8fd3ff"), tags=["pastel", "cuento"],
         card="#c8f2e6"),
    kids("inf-comic", "Cómic", "Comic", ("¡ZAS!", "ZAP!"), "Bangers", 180, 400,
         [hard("#000000", 0.06, 0.06), stroke(0.06), fill("#ff3b30")], box="#ffe600", box_shape="burst",
         box_pad=(0.5, 0.45), box_border=(0.04, "#000000"), anim_in_=tslot("stamp", 0.3, "easeIn"),
         tags=["comic", "superheroe"], card="#2f80ed"),
    kids("inf-golosina", "Golosina", "Candy", ("Dulces", "Sweets"), "Luckiest Guy", 150, 400,
         [hard("#7a1fa2", 0.0, 0.08), stroke(0.08, "#7a1fa2"),
          fill(grad([(0, "#ff7eb9"), (0.5, "#ff65a3"), (1, "#7afcff")], 0, space="word"))], tags=["dulce", "candy"],
         card="#fff5b8"),
    kids("inf-burbujas", "Burbujas", "Bubbles", ("¡A jugar!", "Let's play!"), "Sniglet", 140, 800,
         [glow("#8fd3ff", 0.2, 0.6), stroke(0.08, "#1b6fd6"), fill("#ffffff")], loop=tslot("float", amount=0.08, speed=0.7),
         tags=["burbujas", "juego"], card="#6fc3ff"),
    kids("inf-pegatina", "Pegatina", "Sticker", ("súper", "super"), "Titan One", 160, 400,
         [shadow(dy=0.06, blur=0.1, opacity=0.4), stroke(0.2, "#ffffff", id="stroke2"), stroke(0.06, "#ff6b00"),
          fill("#ffcf00")], tags=["sticker", "pegatina"], card="#3ec1a8"),
    kids("inf-crayon", "Crayón", "Crayon", ("Mi dibujo", "My drawing"), "Gloria Hallelujah", 110, 400,
         [stroke(0.03, "#1d3557", align="center", sketchLength=6, sketchDeviation=2), fill("#e63946")],
         acc=accent("everyOther", "#2a9d8f"), tags=["crayon", "dibujo", "escuela"], card="light"),
    kids("inf-globo", "Globo de diálogo", "Speech balloon", ("¡Yo también!", "Me too!"), "Boogaloo", 110, 400,
         [fill("#1a1a1a")], box="#ffffff", box_shape="oval", box_pad=(0.65, 0.45), box_border=(0.06, "#1a1a1a"),
         tags=["dialogo", "globo"], card="#ff8fab"),
    kids("inf-nube", "Nube", "Cloud", ("Dulces sueños", "Sweet dreams"), "Comfortaa", 90, 700, [fill("#4a5aa8")],
         box="#ffffff", box_shape="cloud", box_pad=(0.7, 0.55), tags=["nube", "dormir", "bebe"], card="#9fc5f8"),
    kids("inf-gelatina", "Gelatina", "Jelly", ("¡Fiesta!", "Party!"), "Baloo 2", 150, 800,
         [shadow(dy=0.08, blur=0.08, opacity=0.35), stroke(0.08, "#0f8b5f"),
          fill(grad([(0, "#c8ffb0"), (1, "#26d07c")], 90))], loop=tslot("wave", amount=0.05, frequency=1.4, phase=40),
         tags=["gelatina", "fiesta"], card="#ffd166"),
    kids("inf-tiza-colores", "Tiza de colores", "Coloured chalk", ("ABC", "ABC"), "Patrick Hand", 200, 400,
         [fill(RAINBOW, alpha=None)], spacing=0.06, card="chalk", tags=["tiza", "escuela", "abc"]),
    kids("inf-garabato", "Garabato", "Doodle", ("¡qué divertido!", "so much fun!"), "Indie Flower", 120, 400,
         [fill("#2b2d42")], word_bg="#ffe066", word_bg_pad=0.08, word_bg_radius=0.25,
         tags=["garabato", "doodle", "cuaderno"], card="light"),
]

# --- gaming and sports --------------------------------------------------------------------------

gaming = styled("gaming", ["gaming", "videojuegos", "deportes"], tslot("glitch-in", 0.3, "linear"),
                tslot("fade-scale", 0.25, "easeIn"))
FIRE = grad([(0, "#fff36b"), (0.45, "#ff9f1c"), (1, "#e01e00")], 90)

GAMING = [
    gaming("gam-militar", "Militar", "Tactical", ("MISIÓN CUMPLIDA", "MISSION COMPLETE"), "Black Ops One", 110, 400,
           [hard("#000000", 0.05, 0.05), stroke(0.04, "#1e2a12"), fill("#c2d36b")], tags=["militar", "mision"],
           card="#2f3a22"),
    gaming("gam-cian", "Pantalla de juego", "Game screen", ("JUGADOR 1", "PLAYER 1"), "Orbitron", 110, 900,
           [glow("#00e5ff", 0.35, 0.6), stroke(0.02, "#00e5ff"), fill("#e9fdff")], spacing=0.08,
           tags=["jugador", "cian", "tecnologia"], card="night"),
    gaming("gam-fuego", "En llamas", "On fire", ("RACHA x5", "STREAK x5"), "Russo One", 130, 400,
           [glow("#ff6a00", 0.35, 0.75), stroke(0.05, "#3a0a00"), fill(FIRE)],
           loop=tslot("flicker", intensity=0.12, speed=10), tags=["fuego", "racha", "combo"], card="#1a0d0a"),
    gaming("gam-glitch", "Glitch de juego", "Game glitch", ("ERROR 404", "ERROR 404"), "Audiowide", 120, 400,
           [fill("#ff0055", id="glitcha", offsetX=-0.03, blend="screen", opacity=0.85),
            fill("#00ffd5", id="glitchb", offsetX=0.03, blend="screen", opacity=0.85),
            fill(fx("glitch", "#ffffff", speed=7, amount=9, block=7))],
           loop=tslot("jitter", amount=1.5, angle=0, speed=16), tags=["glitch", "error"], card="#0d0d0d"),
    gaming("gam-victoria", "Victoria", "Victory", ("¡VICTORIA!", "VICTORY!"), "Passion One", 160, 900,
           [shadow(dy=0.1, blur=0.14, opacity=0.6), extrude(0.1, "#7a4b00"), stroke(0.04, "#fff6cc"),
            fill(grad([(0, "#fff7b0"), (0.5, "#ffc400"), (1, "#c77d00")], 90))], case="upper",
           anim_in_=tslot("zoom-in", 0.4, "back", **{"from": 30}), tags=["victoria", "ganar", "dorado"], card="#2b1055"),
    gaming("gam-fin", "Fin del juego", "Game end", ("FIN DEL JUEGO", "GAME END"), "VT323", 140, 400,
           [glow("#ff1f1f", 0.25, 0.6), fill("#ff3b3b")], spacing=0.04,
           loop=tslot("flicker", intensity=0.3, speed=4), tags=["fin", "pixel", "rojo"], card="#000000"),
    gaming("gam-violeta", "Stream violeta", "Purple stream", ("EN DIRECTO", "STREAMING"), "Bungee", 110, 400,
           [glow("#9146ff", 0.35, 0.65), stroke(0.06, "#ffffff"), fill("#9146ff")], tags=["stream", "directo", "violeta"],
           card="#18122b"),
    gaming("gam-deportivo", "Deportivo", "Sporty", ("¡GOOOL!", "GOAL!"), "Teko", 190, 700,
           [hard("#0b3d91", 0.06, 0.06), stroke(0.03, "#0b3d91"), fill("#ffffff")], case="upper",
           anim_in_=tslot("skew-slide", 0.35, "easeOut", unit="block", distance=0.4), tags=["futbol", "gol", "deportes"],
           card="#0fa958"),
    gaming("gam-cromo-rapido", "Velocidad", "Speed", ("TURBO", "TURBO"), "Exo 2", 170, 700,
           [shadow(dy=0.05, blur=0.08, opacity=0.6), stroke(0.03, "#111111"),
            fill(grad([(0, "#ffffff"), (0.45, "#c7ced8"), (0.5, "#3c4452"), (1, "#e9eef5")], 90))], italic=True,
           anim_in_=tslot("skew-slide", 0.3, "easeOut", unit="block", distance=0.6, skew=-25), tags=["carreras", "velocidad"],
           card="#c1121f"),
    gaming("gam-equipo", "Equipo", "Team", ("EQUIPO AZUL", "BLUE TEAM"), "Staatliches", 140, 400,
           [stroke(0.05, "#ffffff", id="stroke2"), fill("#1d4ed8")], box="#ffffff", box_pad=(0.35, 0.1),
           spacing=0.04, tags=["equipo", "torneo"], card="#1d4ed8"),
    gaming("gam-nivel", "Subiste de nivel", "Level up", ("LEVEL UP", "LEVEL UP"), "Kanit", 130, 900,
           [glow("#7cff6b", 0.3, 0.6), stroke(0.06, "#0a3d12"), fill(grad([(0, "#eaffd0"), (1, "#5bd94a")], 90))],
           italic=False, anim_in_=tslot("rise", 0.45, "back", unit="character", stagger=0.03), tags=["nivel", "level up"],
           card="#10162f"),
    gaming("gam-jefe", "Jefe final", "Final boss", ("JEFE FINAL", "FINAL BOSS"), "Black Ops One", 120, 400,
           [glow("#ff2a2a", 0.4, 0.55), extrude(0.08, "#3b0000"), fill(grad([(0, "#ff8a8a"), (1, "#b80000")], 90))],
           loop=tslot("jitter", amount=1.2, angle=1, speed=12), tags=["jefe", "boss"], card="#140404"),
]

# --- horror and Halloween -----------------------------------------------------------------------

horror = styled("terror", ["terror", "halloween", "miedo"], tslot("flicker-in", 1.0, "linear"),
                tslot("fade", 0.6, "easeIn"))

HORROR = [
    horror("ter-baba", "Baba verde", "Green slime", ("¡Buuu!", "Boo!"), "Creepster", 170, 400,
           [glow("#7cff00", 0.3, 0.6), stroke(0.04, "#0d2600"), fill("#a8ff3e")], tags=["baba", "slime", "verde"],
           card="#120a1f"),
    horror("ter-sangre", "Rojo sangre", "Blood red", ("NO MIRES ATRÁS", "DON'T LOOK BACK"), "Creepster", 120, 400,
           [shadow("#000000", 0.0, 0.08, 0.1, 0.9), fill(grad([(0, "#ff2a2a"), (1, "#5c0000")], 90))],
           tags=["sangre", "rojo", "pelicula de terror"], card="#0a0a0a"),
    horror("ter-expediente", "Expediente secreto", "Case file", ("CASO SIN RESOLVER", "UNSOLVED CASE"), "Special Elite",
           90, 400, [fill("#e8e2d0")], loop=tslot("jitter", amount=0.6, angle=0.5, speed=9),
           tags=["misterio", "caso", "true crime"], card="#1c1a17"),
    horror("ter-susurro", "Susurro", "Whisper", ("¿Escuchaste eso?", "Did you hear that?"), "Cormorant Garamond", 100, 600,
           [glow("#9fb4c7", 0.5, 0.55), fill("#dbe6f0", alpha=0.9)], italic=True,
           loop=tslot("breathe", amount=0.35, speed=0.5), tags=["susurro", "misterio", "fantasma"], card="#0b1118"),
    horror("ter-calabaza", "Calabaza", "Pumpkin", ("Halloween", "Halloween"), "Creepster", 160, 400,
           [hard("#3b1361", 0.05, 0.07), stroke(0.05, "#3b1361"), fill(grad([(0, "#ffb347"), (1, "#ff6a00")], 90))],
           tags=["calabaza", "naranja"], card="#1b0f2e"),
    horror("ter-fantasma", "Fantasma", "Ghost", ("Hay alguien aquí", "Someone is here"), "Shadows Into Light", 120, 400,
           [glow("#ffffff", 0.45, 0.6), fill("#ffffff", alpha=0.85)], loop=tslot("float", amount=0.1, speed=0.4),
           tags=["fantasma", "ghost"], card="#141821"),
    horror("ter-peligro", "Peligro", "Danger", ("PELIGRO", "DANGER"), "Black Ops One", 130, 400, [fill("#111111")],
           box="#ffd000", box_pad=(0.5, 0.2), box_border=(0.06, "#111111"), spacing=0.06,
           loop=tslot("jitter", amount=1.0, angle=0, speed=10), anim_in_=tslot("stamp", 0.3, "easeIn"),
           tags=["peligro", "advertencia", "warning"], card="#222222"),
    horror("ter-niebla", "Niebla", "Fog", ("La casa del bosque", "The house in the woods"), "Cinzel", 96, 700,
           [glow("#7f8c99", 0.6, 0.5), fill("#cfd8e0")], spacing=0.06,
           anim_in_=tslot("blur-in", 1.4, "easeOut"), tags=["niebla", "bosque", "suspenso"], card="#0e1216"),
]

# --- special days -------------------------------------------------------------------------------

days = styled("fechas", ["fechas especiales", "celebracion"], tslot("zoom-in", 0.6, "back"), tslot("fade", 0.4, "easeIn"))

DAYS = [
    days("fec-navidad", "Navidad clásica", "Classic Christmas", ("Feliz Navidad", "Merry Christmas"), "Lobster", 140, 400,
         [shadow(dy=0.05, blur=0.1, opacity=0.5), stroke(0.07, "#ffffff"), fill("#c8102e")],
         acc=accent("lastWord", "#1f7a3a"), tags=["navidad", "christmas", "diciembre"], card="#e9f2ea"),
    days("fec-navidad-oro", "Navidad dorada", "Golden Christmas", ("Felices fiestas", "Happy holidays"), "Great Vibes", 150,
         400, [glow("#ffd77a", 0.3, 0.55), fill(GOLD)], loop=tslot("breathe", amount=0.15, speed=0.6),
         tags=["navidad", "fiestas", "dorado"], card="#0f3d2e"),
    days("fec-anio-nuevo", "Año Nuevo", "New Year", ("¡Feliz Año Nuevo!", "Happy New Year!"), "Playfair Display", 110, 900,
         [glow("#ffe7a3", 0.25, 0.5), fill(fx("shimmer", "#ffe6a8", speed=0.4, scale=6, intensity=0.4))],
         tags=["año nuevo", "new year", "brindis"], card="#101826"),
    days("fec-san-valentin", "San Valentín", "Valentine's", ("Te quiero", "Love you"), "Pacifico", 150, 400,
         [shadow(dy=0.05, blur=0.1, opacity=0.4), stroke(0.07, "#ffffff"), fill(grad([(0, "#ff7aa8"), (1, "#e0115f")], 90))],
         loop=tslot("pulse", amount=4, speed=1.3), tags=["san valentin", "amor", "14 de febrero"], card="#ffd6e0"),
    days("fec-cumpleanos", "Cumpleaños", "Birthday", ("¡Feliz cumple!", "Happy birthday!"), "Chewy", 140, 400,
         [hard("#3d2c8d", 0.0, 0.08), stroke(0.08, "#ffffff"), fill(RAINBOW)],
         anim_in_=tslot("bounce", 0.7, unit="character", stagger=0.04), tags=["cumpleaños", "birthday", "fiesta"],
         card="#ffd23f"),
    days("fec-pascua", "Pascua", "Easter", ("Felices Pascuas", "Happy Easter"), "Fredoka", 120, 700,
         [stroke(0.09, "#ffffff"), fill("#8e7cc3")], acc=accent("lastWord", "#f6a5c0"), tags=["pascua", "easter", "primavera"],
         card="#d9f2c4"),
    days("fec-dia-madre", "Día de la Madre", "Mother's Day", ("Te amo, mamá", "Love you, Mom"), "Dancing Script", 140, 700,
         [shadow(dy=0.03, blur=0.1, opacity=0.4), fill("#c2185b")], card="#fde2e4", tags=["mama", "madre", "mothers day"]),
    days("fec-dia-padre", "Día del Padre", "Father's Day", ("Feliz día, papá", "Happy Father's Day"), "Alfa Slab One", 110,
         400, [hard("#f2b134", 0.05, 0.05), fill("#1d3557")], card="#e8eef5", tags=["papa", "padre", "fathers day"]),
    days("fec-graduacion", "Graduación", "Graduation", ("¡Lo logramos!", "We did it!"), "Cinzel", 110, 900,
         [shadow(dy=0.05, blur=0.12, opacity=0.6), fill(GOLD)], spacing=0.04, tags=["graduacion", "promocion"],
         card="#0a1f44"),
    days("fec-anio-lunar", "Año Nuevo Lunar", "Lunar New Year", ("Feliz Año Nuevo Lunar", "Happy Lunar New Year"),
         "Yeseva One", 100, 400, [glow("#ffcc4d", 0.2, 0.45), stroke(0.03, "#ffcc4d"), fill("#ffe08a")], box="#c8102e",
         box_pad=(0.6, 0.4), box_radius=0.12, box_border=(0.04, "#ffcc4d"), tags=["año nuevo lunar", "lunar new year"],
         card="#3a0a0a"),
    days("fec-eid", "Eid Mubarak", "Eid Mubarak", ("Eid Mubarak", "Eid Mubarak"), "Marcellus", 120, 400,
         [glow("#f3d27a", 0.3, 0.5), fill(GOLD)], spacing=0.05, tags=["eid", "ramadan", "mubarak"], card="#0d3b3e"),
    days("fec-diwali", "Diwali", "Diwali", ("Feliz Diwali", "Happy Diwali"), "Kaushan Script", 140, 400,
         [glow("#ff9f1c", 0.4, 0.7), fill(grad([(0, "#fff1a8"), (1, "#ff9f1c")], 90))],
         loop=tslot("flicker", intensity=0.1, speed=3), tags=["diwali", "luces", "festival"], card="#2a0a3d"),
]

STYLES = NEON + THREE_D + RETRO + ELEGANT + KIDS + GAMING + HORROR + DAYS
