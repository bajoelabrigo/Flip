"""The 200 looks of Stock › LUTs. A look = (id, es, en, category, steps, tags, sample).

Names are descriptive and our own: no film-stock or brand names.
"""

from __future__ import annotations

CATEGORIES = {
    "cine": {"es": "Cine", "en": "Cinematic"},
    "pelicula": {"es": "Película analógica", "en": "Analog film"},
    "vintage": {"es": "Vintage y retro", "en": "Vintage and retro"},
    "byn": {"es": "Blanco y negro", "en": "Black and white"},
    "verano": {"es": "Verano y viajes", "en": "Summer and travel"},
    "noche": {"es": "Noche y ciudad", "en": "Night and city"},
    "comida": {"es": "Comida", "en": "Food"},
    "retrato": {"es": "Retrato y piel", "en": "Portrait and skin"},
    "pastel": {"es": "Pastel y anime", "en": "Pastel and anime"},
    "estetico": {"es": "Estético y moody", "en": "Aesthetic and moody"},
    "estaciones": {"es": "Estaciones", "en": "Seasons"},
}

LOOKS: list[tuple] = []


def look(id, es, en, cat, steps, tags=(), sample=None):
    LOOKS.append((id, es, en, cat, steps, list(tags), sample))


def C(a):
    return ("contrast", {"amount": a})


def S(a):
    return ("sat", {"amount": a})


def V(a):
    return ("vib", {"amount": a})


def WB(t=0.0, n=0.0):
    return ("wb", {"temp": t, "tint": n})


def SPLIT(sh, hi, bal=0.0, amt=1.0):
    return ("split", {"shadows": sh, "highlights": hi, "balance": bal, "amount": amt})


def FADE(a, tone=(0, 0, 0)):
    return ("fade", {"amount": a, "tone": tone})


def EXP(s):
    return ("exposure", {"stops": s})


def LGG(lift=(0, 0, 0), gamma=(1, 1, 1), gain=(1, 1, 1)):
    return ("lgg", {"lift": lift, "gamma": gamma, "gain": gain})


def HUE(h, w=0.08, shift=0.0, sat=1.0, light=0.0):
    return ("hue", {"hue_from": h, "width": w, "shift": shift, "sat": sat, "light": light})


def MONO(mix=(0.3, 0.59, 0.11), tone=(0, 0, 0)):
    return ("mono", {"mix": mix, "tone": tone})


def CURVE(points, channel=None):
    return ("curve", {"points": points, "channel": channel})


def ROLL(s=0.8):
    return ("roll", {"start": s})


# ================================================================ Cine (25)
c = "cine"
CINE = ["cine", "cinematic", "pelicula", "film", "drama"]
look("cine-teal-naranja", "Turquesa y naranja", "Teal and orange", c,
     [SPLIT((-0.05, 0.02, 0.06), (0.07, 0.01, -0.07)), S(1.12), C(0.25), ROLL()], CINE + ["teal", "orange", "blockbuster"], "city")
look("cine-taquilla", "Éxito de taquilla", "Blockbuster", c,
     [SPLIT((-0.06, 0.02, 0.08), (0.08, 0.02, -0.06)), C(0.4), S(1.18), ROLL(0.78)], CINE + ["accion", "epico"], "man")
look("cine-drama-frio", "Drama frío", "Cold drama", c, [WB(-0.4, 0.05), S(0.75), C(0.3), FADE(0.06)], CINE + ["frio", "triste"], "portrait")
look("cine-drama-calido", "Drama cálido", "Warm drama", c, [WB(0.4), S(0.85), C(0.3), SPLIT((0.0, 0.0, 0.03), (0.04, 0.01, -0.03))], CINE + ["calido"], "portrait")
look("cine-blanqueado", "Blanqueado", "Bleach bypass", c, [S(0.45), C(0.55), EXP(0.05), ROLL(0.75)], CINE + ["bleach bypass", "guerra", "duro"], "man")
look("cine-noir-color", "Noir en color", "Colour noir", c, [S(0.4), C(0.6), WB(-0.2), LGG(gain=(0.95, 0.97, 1.0))], CINE + ["noir", "misterio"], "city")
look("cine-thriller", "Thriller", "Thriller", c, [WB(-0.25, -0.15), S(0.7), C(0.45), SPLIT((-0.02, 0.03, 0.02), (0.0, 0.02, 0.0))], CINE + ["suspenso", "verde"], "city")
look("cine-ciencia-ficcion", "Ciencia ficción", "Sci-fi", c, [SPLIT((-0.04, 0.03, 0.07), (-0.01, 0.04, 0.05)), S(0.85), C(0.35)], CINE + ["futuro", "azul", "tecnologia"], "office")
look("cine-western", "Western", "Western", c, [WB(0.6, 0.05), S(0.8), C(0.4), FADE(0.05, (0.08, 0.04, 0.0)), ROLL(0.75)], CINE + ["desierto", "polvo", "oeste"], "travel")
look("cine-romance", "Romance", "Romance", c, [WB(0.3, 0.12), C(0.15), FADE(0.08, (0.06, 0.02, 0.03)), ROLL(0.82)], CINE + ["romantico", "amor", "suave"], "couple")
look("cine-terror", "Terror", "Horror", c, [S(0.5), WB(-0.3, -0.2), C(0.5), EXP(-0.15)], CINE + ["terror", "miedo"], "halloween")
look("cine-documental", "Documental", "Documentary", c, [C(0.2), S(0.95), FADE(0.03), ROLL()], CINE + ["natural", "real"], "family")
look("cine-epico", "Épico", "Epic", c, [C(0.5), S(1.1), SPLIT((-0.03, 0.0, 0.05), (0.06, 0.03, -0.03)), ROLL(0.76)], CINE + ["epico", "paisaje"], "nature")
look("cine-indie", "Cine indie", "Indie film", c, [FADE(0.12, (0.04, 0.03, 0.06)), S(0.8), C(0.1), WB(0.1, 0.05)], CINE + ["indie", "suave", "mate"], "friends")
look("cine-pastel-indie", "Indie pastel", "Pastel indie", c, [FADE(0.15, (0.08, 0.05, 0.08)), S(0.7), WB(0.15, 0.1)], CINE + ["pastel"], "friends")
look("cine-guerra", "Bélico", "War film", c, [S(0.35), WB(0.2, -0.1), C(0.5), FADE(0.05, (0.03, 0.04, 0.0))], CINE + ["guerra", "duro", "desaturado"], "man")
look("cine-misterio", "Misterio", "Mystery", c, [WB(-0.35), S(0.6), C(0.35), EXP(-0.1), SPLIT((0.0, 0.02, 0.05), (0, 0, 0))], CINE + ["misterio", "noche"], "city")
look("cine-dorado", "Hora dorada de cine", "Cinematic golden hour", c, [WB(0.55), SPLIT((-0.02, 0.0, 0.04), (0.06, 0.03, -0.04)), C(0.3)], CINE + ["dorado", "atardecer"], "beach")
look("cine-acero", "Acero", "Steel", c, [WB(-0.5), S(0.5), C(0.45), LGG(gain=(0.95, 1.0, 1.04))], CINE + ["metal", "frio", "industrial"], "city")
look("cine-musical", "Musical", "Musical", c, [S(1.3), V(0.3), C(0.25), WB(0.1, 0.05)], CINE + ["colorido", "alegre"], "concert")
look("cine-nostalgia", "Nostalgia", "Nostalgia", c, [FADE(0.1, (0.07, 0.04, 0.0)), WB(0.35), S(0.8), ROLL(0.8)], CINE + ["recuerdo", "calido"], "family")
look("cine-oscuro", "Oscuro y dramático", "Dark and dramatic", c, [EXP(-0.25), C(0.55), S(0.8), ROLL(0.7)], CINE + ["oscuro", "moody"], "man")
look("cine-cristal", "Cristalino", "Crystal clear", c, [C(0.25), V(0.35), WB(-0.1), ROLL(0.85)], CINE + ["limpio", "claro", "nitido"], "nature")
look("cine-niebla", "Niebla de cine", "Cinematic haze", c, [FADE(0.18, (0.06, 0.06, 0.07)), C(-0.2), S(0.8)], CINE + ["niebla", "suave", "sueño"], "nature")
look("cine-verde-matrix", "Verde digital", "Digital green", c, [SPLIT((-0.02, 0.05, -0.01), (0.0, 0.05, 0.0)), S(0.7), C(0.4)], CINE + ["verde", "hacker", "digital"], "office")

# ================================================================ Película analógica (25)
p = "pelicula"
PEL = ["pelicula", "analogico", "film", "35mm", "grano"]
look("pel-retrato-400", "Retrato 400", "Portrait 400", p, [WB(0.2, 0.05), S(0.9), C(0.15), FADE(0.04, (0.05, 0.03, 0.0)), ROLL(0.82)], PEL + ["retrato", "piel"], "portrait")
look("pel-retrato-160", "Retrato 160", "Portrait 160", p, [WB(0.1), S(0.85), C(0.05), FADE(0.03), ROLL(0.85)], PEL + ["suave", "piel"], "portrait")
look("pel-diapositiva", "Diapositiva vívida", "Vivid slide", p, [S(1.35), C(0.45), WB(-0.05), ROLL(0.78)], PEL + ["vivido", "diapositiva", "saturado"], "nature")
look("pel-negativo-frio", "Negativo frío", "Cool negative", p, [WB(-0.3, -0.05), S(0.85), FADE(0.06, (0.0, 0.03, 0.05))], PEL + ["frio"], "city")
look("pel-negativo-calido", "Negativo cálido", "Warm negative", p, [WB(0.35, 0.05), S(0.9), FADE(0.06, (0.06, 0.03, 0.0))], PEL + ["calido"], "family")
look("pel-800-noche", "Película 800 nocturna", "Night film 800", p, [SPLIT((0.02, -0.01, 0.06), (0.06, 0.02, -0.03)), FADE(0.07), C(0.25)], PEL + ["noche", "neon"], "city")
look("pel-consumo", "Película de consumo", "Consumer film", p, [WB(0.25, -0.05), S(1.1), C(0.2), FADE(0.04, (0.04, 0.04, 0.0))], PEL + ["casual", "recuerdo"], "friends")
look("pel-instantanea", "Instantánea", "Instant film", p, [FADE(0.16, (0.06, 0.05, 0.02)), WB(0.2, 0.08), S(0.8), C(-0.05), ROLL(0.75)], PEL + ["instantanea", "foto instantanea", "vintage"], "couple")
look("pel-cross", "Proceso cruzado", "Cross process", p,
     [CURVE([(0, 0.05), (0.5, 0.55), (1, 0.95)], 0), CURVE([(0, 0), (0.5, 0.55), (1, 1)], 1), CURVE([(0, 0.15), (0.5, 0.42), (1, 0.8)], 2), S(1.15)],
     PEL + ["cross process", "lomo"], "friends")
look("pel-super8", "Súper 8", "Super 8", p, [WB(0.45, 0.05), S(0.75), FADE(0.12, (0.08, 0.05, 0.0)), C(0.2), ROLL(0.72)], PEL + ["super 8", "8mm", "casero"], "family")
look("pel-16mm", "16 mm", "16 mm", p, [WB(0.15), S(0.8), FADE(0.08), C(0.25)], PEL + ["16mm", "documental"], "man")
look("pel-cine-negativo", "Negativo de cine", "Motion picture negative", p, [SPLIT((-0.02, 0.01, 0.04), (0.04, 0.02, -0.02)), S(0.9), C(0.2), ROLL(0.8)], PEL + ["cine"], "city")
look("pel-verde-sombras", "Sombras verdes", "Green shadows", p, [SPLIT((-0.02, 0.04, 0.0), (0.03, 0.01, -0.02)), FADE(0.06), S(0.85)], PEL + ["verde", "vintage"], "nature")
look("pel-magenta", "Tono magenta", "Magenta cast", p, [WB(0.05, 0.25), FADE(0.06, (0.05, 0.0, 0.05)), S(0.9)], PEL + ["magenta", "rosado"], "portrait")
look("pel-caducada", "Película caducada", "Expired film", p,
     [WB(0.3, 0.2), FADE(0.2, (0.08, 0.02, 0.06)), S(0.7), C(0.15), CURVE([(0, 0.08), (1, 0.92)], 2)], PEL + ["caducada", "expired", "raro"], "friends")
look("pel-desechable", "Cámara desechable", "Disposable camera", p, [WB(0.3, -0.1), S(1.15), C(0.35), FADE(0.05, (0.03, 0.04, 0.0))], PEL + ["desechable", "flash", "fiesta"], "friends")
look("pel-rollo-viajes", "Rollo de viajes", "Travel roll", p, [WB(0.2), V(0.25), C(0.2), FADE(0.05)], PEL + ["viaje"], "travel")
look("pel-iso-alto", "ISO alto", "High ISO", p, [FADE(0.1, (0.03, 0.03, 0.05)), S(0.75), C(0.3), WB(-0.1)], PEL + ["noche", "oscuro"], "concert")
look("pel-tungsteno", "Tungsteno", "Tungsten", p, [WB(-0.55, -0.05), S(0.9), C(0.2)], PEL + ["tungsteno", "azul", "noche"], "city")
look("pel-luz-dia", "Luz de día", "Daylight film", p, [WB(0.1), S(1.0), C(0.2), ROLL(0.82)], PEL + ["dia", "natural"], "nature")
look("pel-sepia-suave", "Sepia suave", "Soft sepia", p, [S(0.4), WB(0.5, 0.05), FADE(0.08, (0.07, 0.04, 0.0))], PEL + ["sepia"], "family")
look("pel-lomo", "Lomo", "Lomo", p, [S(1.3), C(0.55), SPLIT((0.0, 0.0, 0.06), (0.06, 0.04, -0.06))], PEL + ["lomo", "contraste", "vivido"], "friends")
look("pel-mate", "Mate de película", "Matte film", p, [FADE(0.14), C(0.15), S(0.85)], PEL + ["mate", "suave"], "portrait")
look("pel-polvo-dorado", "Película dorada", "Golden film", p, [WB(0.5), FADE(0.08, (0.08, 0.05, 0.0)), S(0.9), ROLL(0.78)], PEL + ["dorado", "calido"], "beach")
look("pel-azul-retro", "Azul retro", "Retro blue", p, [SPLIT((0.0, 0.02, 0.06), (0.0, 0.02, 0.04)), FADE(0.1, (0.0, 0.03, 0.06)), S(0.8)], PEL + ["azul", "retro"], "city")

# ================================================================ Vintage y retro (20)
v = "vintage"
VIN = ["vintage", "retro", "antiguo"]
look("vin-70s", "Años 70", "Seventies", v, [WB(0.5, 0.05), FADE(0.12, (0.08, 0.05, 0.0)), S(0.85), CURVE([(0, 0.05), (1, 0.92)], 2)], VIN + ["70s", "setentas"], "family")
look("vin-80s", "Años 80", "Eighties", v, [WB(0.1, 0.15), S(1.2), C(0.3), SPLIT((0.0, 0.0, 0.06), (0.05, 0.0, 0.02))], VIN + ["80s", "ochentas"], "friends")
look("vin-90s", "Años 90", "Nineties", v, [WB(0.2, -0.05), S(0.95), FADE(0.06, (0.03, 0.04, 0.0)), C(0.2)], VIN + ["90s", "noventas"], "friends")
look("vin-y2k", "Y2K", "Y2K", v, [S(1.25), WB(-0.15, 0.15), C(0.3), EXP(0.08)], VIN + ["y2k", "2000s", "brillante"], "fashion")
look("vin-sepia", "Sepia", "Sepia", v, [MONO(tone=(0.12, 0.05, -0.06)), FADE(0.06)], VIN + ["sepia", "antiguo"], "family")
look("vin-desvanecido", "Desvanecido", "Faded", v, [FADE(0.2), S(0.7), C(-0.05)], VIN + ["desvanecido", "faded"], "couple")
look("vin-revista-antigua", "Color de revista antigua", "Old magazine colour", v, [S(1.2), C(0.35), WB(0.15), HUE(0.0, 0.1, sat=1.2), ROLL(0.78)], VIN + ["revista"], "travel")
look("vin-postal", "Postal antigua", "Old postcard", v, [S(0.75), WB(0.3, 0.1), FADE(0.15, (0.08, 0.06, 0.03)), C(0.1)], VIN + ["postal"], "travel")
look("vin-album-familiar", "Álbum familiar", "Family album", v, [WB(0.4), S(0.8), FADE(0.12, (0.07, 0.04, 0.02)), ROLL(0.75)], VIN + ["familia", "recuerdo"], "family")
look("vin-verde-retro", "Verde retro", "Retro green", v, [SPLIT((-0.02, 0.05, 0.0), (0.03, 0.04, -0.03)), FADE(0.1), S(0.8)], VIN + ["verde"], "nature")
look("vin-rosa-retro", "Rosa retro", "Retro pink", v, [WB(0.1, 0.2), FADE(0.12, (0.08, 0.02, 0.05)), S(0.85)], VIN + ["rosa"], "quince")
look("vin-vhs", "Color VHS", "VHS colour", v, [S(1.1), WB(-0.1, 0.1), FADE(0.08, (0.02, 0.0, 0.06)), C(0.25)], VIN + ["vhs", "cinta"], "friends")
look("vin-camcorder", "Videocámara casera", "Home camcorder", v, [WB(0.25, -0.05), S(1.05), C(0.3), FADE(0.04)], VIN + ["camcorder", "casero"], "family")
look("vin-daguerrotipo", "Daguerrotipo", "Daguerreotype", v, [MONO((0.25, 0.6, 0.15), (0.02, 0.03, 0.05)), C(0.3), FADE(0.1, (0.04, 0.04, 0.05))], VIN + ["antiguo", "siglo xix"], "man")
look("vin-tintado-azul", "Tintado azul", "Blue tint", v, [MONO(tone=(-0.06, 0.0, 0.1)), FADE(0.08)], VIN + ["cianotipo", "azul"], "nature")
look("vin-cine-mudo", "Cine mudo", "Silent movie", v, [MONO((0.3, 0.6, 0.1), (0.06, 0.03, 0.0)), C(0.45), FADE(0.06)], VIN + ["cine mudo", "1920"], "man")
look("vin-revista-moda", "Revista de moda retro", "Retro fashion magazine", v, [S(0.9), C(0.35), WB(0.1, 0.1), FADE(0.05)], VIN + ["moda"], "fashion")
look("vin-tecnicolor", "Tecnicolor", "Technicolour", v, [S(1.4), C(0.4), HUE(0.0, 0.1, sat=1.25), HUE(0.62, 0.1, sat=1.2)], VIN + ["tecnicolor", "clasico"], "fashion")
look("vin-sol-viejo", "Sol de antes", "Old sunshine", v, [WB(0.6), S(0.85), FADE(0.1, (0.1, 0.05, 0.0)), ROLL(0.72)], VIN + ["calido", "verano"], "beach")
look("vin-boulevard", "Bulevar", "Boulevard", v, [SPLIT((0.0, 0.02, 0.05), (0.06, 0.03, -0.02)), FADE(0.1), S(0.85)], VIN + ["ciudad", "paseo"], "city")

# ================================================================ Blanco y negro (15)
b = "byn"
BN = ["blanco y negro", "black and white", "bn", "monocromo", "clasico"]
look("byn-neutro", "Blanco y negro neutro", "Neutral black and white", b, [MONO(), C(0.15)], BN, "portrait")
look("byn-alto-contraste", "Alto contraste", "High contrast", b, [MONO(), C(0.7), ROLL(0.8)], BN + ["contraste", "duro"], "man")
look("byn-suave", "Suave", "Soft mono", b, [MONO(), C(-0.15), FADE(0.06)], BN + ["suave"], "portrait")
look("byn-filtro-rojo", "Filtro rojo", "Red filter", b, [MONO((0.7, 0.25, 0.05)), C(0.35)], BN + ["cielo", "dramatico"], "nature")
look("byn-filtro-verde", "Filtro verde", "Green filter", b, [MONO((0.15, 0.75, 0.1)), C(0.25)], BN + ["paisaje"], "nature")
look("byn-filtro-azul", "Filtro azul", "Blue filter", b, [MONO((0.1, 0.3, 0.6)), C(0.3)], BN + ["melancolico"], "city")
look("byn-selenio", "Virado selenio", "Selenium tone", b, [MONO(tone=(0.03, -0.01, 0.04)), C(0.3)], BN + ["virado"], "man")
look("byn-calido", "Blanco y negro cálido", "Warm mono", b, [MONO(tone=(0.06, 0.03, -0.03)), C(0.2)], BN + ["calido"], "family")
look("byn-frio", "Blanco y negro frío", "Cool mono", b, [MONO(tone=(-0.03, 0.0, 0.05)), C(0.25)], BN + ["frio"], "city")
look("byn-noir", "Noir", "Noir", b, [MONO((0.35, 0.55, 0.1)), C(0.65), EXP(-0.2), ROLL(0.75)], BN + ["noir", "detective", "oscuro"], "city")
look("byn-mate", "Blanco y negro mate", "Matte mono", b, [MONO(), FADE(0.15), C(0.1)], BN + ["mate"], "fashion")
look("byn-periodico", "Periódico", "Newspaper", b, [MONO(), C(0.8), CURVE([(0, 0.08), (0.5, 0.5), (1, 0.95)])], BN + ["periodico", "prensa"], "office")
look("byn-plata", "Plata", "Silver", b, [MONO((0.25, 0.6, 0.15)), C(0.4), EXP(0.08), ROLL(0.82)], BN + ["plata", "brillante"], "wedding")
look("byn-boda", "Boda en blanco y negro", "Wedding black and white", b, [MONO(), C(0.2), FADE(0.04), EXP(0.05)], BN + ["boda", "elegante"], "wedding")
look("byn-calle", "Fotografía callejera", "Street photography", b, [MONO((0.3, 0.6, 0.1)), C(0.5), FADE(0.03)], BN + ["calle", "urbano"], "city")

# ================================================================ Verano y viajes (20)
s = "verano"
VER = ["verano", "summer", "viaje", "travel", "vacaciones"]
look("ver-playa", "Playa", "Beach", s, [WB(0.15), V(0.35), HUE(0.5, 0.12, sat=1.25, light=0.03), C(0.15), EXP(0.08)], VER + ["playa", "mar"], "beach")
look("ver-tropical", "Tropical", "Tropical", s, [V(0.5), HUE(0.33, 0.1, sat=1.25), HUE(0.5, 0.1, sat=1.2), C(0.2)], VER + ["tropical", "verde"], "travel")
look("ver-hora-dorada", "Hora dorada", "Golden hour", s, [WB(0.6, 0.03), S(1.1), C(0.2), ROLL(0.78)], VER + ["dorado", "atardecer", "sunset"], "beach")
look("ver-sol-pop", "Sol pop", "Sunny pop", s, [EXP(0.12), S(1.25), C(0.2), WB(0.2)], VER + ["brillante", "alegre"], "friends")
look("ver-desierto", "Desierto", "Desert", s, [WB(0.5, 0.05), S(0.85), C(0.3), HUE(0.08, 0.1, sat=1.15)], VER + ["desierto", "arena"], "travel")
look("ver-mediterraneo", "Mediterráneo", "Mediterranean", s, [WB(0.1), HUE(0.6, 0.12, sat=1.25), HUE(0.1, 0.1, sat=1.1), C(0.15), EXP(0.05)], VER + ["mediterraneo", "azul", "blanco"], "travel")
look("ver-isla", "Isla", "Island", s, [V(0.4), HUE(0.48, 0.1, shift=0.02, sat=1.3), EXP(0.05)], VER + ["isla", "turquesa"], "beach")
look("ver-piscina", "Piscina", "Pool day", s, [HUE(0.52, 0.12, sat=1.3, light=0.04), WB(-0.05), EXP(0.08), C(0.1)], VER + ["piscina", "agua"], "beach")
look("ver-montana", "Montaña", "Mountain", s, [C(0.3), V(0.25), WB(-0.1), HUE(0.33, 0.1, sat=1.1)], VER + ["montaña", "aventura"], "nature")
look("ver-road-trip", "Viaje en carretera", "Road trip", s, [WB(0.3), FADE(0.06, (0.05, 0.03, 0.0)), S(1.05), C(0.2)], VER + ["carretera", "road trip"], "travel")
look("ver-limonada", "Limonada", "Lemonade", s, [WB(0.2, -0.08), EXP(0.1), S(1.1), HUE(0.15, 0.1, sat=1.2)], VER + ["fresco", "amarillo"], "food")
look("ver-brisa", "Brisa", "Breeze", s, [EXP(0.1), S(0.9), WB(-0.1), FADE(0.06, (0.0, 0.03, 0.05))], VER + ["suave", "aire"], "beach")
look("ver-safari", "Safari", "Safari", s, [WB(0.45), S(0.9), C(0.3), HUE(0.25, 0.12, shift=-0.02, sat=0.9)], VER + ["safari", "naturaleza"], "nature")
look("ver-ciudad-luz", "Ciudad soleada", "Sunny city", s, [EXP(0.08), V(0.3), C(0.15), WB(0.15)], VER + ["ciudad", "turismo"], "city")
look("ver-atardecer-rosa", "Atardecer rosa", "Pink sunset", s, [WB(0.3, 0.18), S(1.1), SPLIT((0.0, 0.0, 0.04), (0.06, 0.0, 0.02))], VER + ["atardecer", "rosa"], "beach")
look("ver-cielo-azul", "Cielo azul intenso", "Deep blue sky", s, [HUE(0.6, 0.12, sat=1.35, light=-0.04), C(0.2)], VER + ["cielo", "azul"], "nature")
look("ver-verde-vivo", "Verde vivo", "Lush green", s, [HUE(0.3, 0.12, sat=1.35, light=0.02), V(0.2), C(0.15)], VER + ["verde", "naturaleza"], "nature")
look("ver-vacaciones", "Vacaciones", "Holiday", s, [V(0.35), EXP(0.08), C(0.15), WB(0.2)], VER + ["vacaciones", "alegre"], "travel")
look("ver-crucero", "Crucero", "Cruise", s, [HUE(0.55, 0.15, sat=1.2), WB(-0.05), C(0.2), ROLL(0.82)], VER + ["mar", "barco"], "beach")
look("ver-festival", "Festival", "Festival", s, [S(1.3), C(0.3), WB(0.15, 0.08)], VER + ["festival", "musica", "fiesta"], "concert")

# ================================================================ Noche y ciudad (15)
n = "noche"
NOC = ["noche", "night", "ciudad", "city", "urbano"]
look("noc-neon", "Neón", "Neon", n, [SPLIT((0.03, -0.02, 0.07), (0.06, -0.02, 0.05)), S(1.3), C(0.35)], NOC + ["neon", "luces"], "city")
look("noc-cyberpunk", "Cyberpunk", "Cyberpunk", n, [SPLIT((-0.04, 0.03, 0.08), (0.08, -0.02, 0.06)), S(1.25), C(0.45), HUE(0.08, 0.15, shift=0.85, sat=1.1)], NOC + ["cyberpunk", "futuro", "magenta"], "city")
look("noc-azul-moody", "Azul nocturno", "Moody night blue", n, [WB(-0.5), S(0.75), C(0.4), EXP(-0.1)], NOC + ["azul", "moody"], "city")
look("noc-luces-ciudad", "Luces de ciudad", "City lights", n, [WB(0.25), S(1.1), C(0.3), SPLIT((0.0, 0.0, 0.05), (0.05, 0.02, -0.02))], NOC + ["luces"], "city")
look("noc-sodio", "Farolas", "Street lamps", n, [WB(0.7, 0.05), S(0.85), C(0.35)], NOC + ["farolas", "naranja"], "city")
look("noc-lluvia", "Noche de lluvia", "Rainy night", n, [WB(-0.35, 0.05), S(0.7), FADE(0.06, (0.0, 0.02, 0.05)), C(0.3)], NOC + ["lluvia", "melancolia"], "city")
look("noc-club", "Discoteca", "Club", n, [S(1.35), C(0.4), SPLIT((0.04, 0.0, 0.08), (0.04, 0.0, 0.06))], NOC + ["discoteca", "fiesta", "baile"], "concert")
look("noc-concierto", "Concierto", "Concert", n, [S(1.2), C(0.45), EXP(-0.05), ROLL(0.75)], NOC + ["concierto", "show"], "concert")
look("noc-medianoche", "Medianoche", "Midnight", n, [WB(-0.3, 0.08), EXP(-0.2), C(0.4), S(0.8)], NOC + ["oscuro"], "city")
look("noc-tokio", "Calles de neón", "Neon streets", n, [SPLIT((-0.02, 0.02, 0.07), (0.07, 0.0, 0.04)), S(1.15), C(0.3), HUE(0.5, 0.1, sat=1.2)], NOC + ["neon", "asia"], "city")
look("noc-luna", "Luz de luna", "Moonlight", n, [WB(-0.6, 0.0), S(0.5), EXP(-0.1), C(0.3)], NOC + ["luna", "frio"], "nature")
look("noc-vela", "Luz de vela", "Candlelight", n, [WB(0.65, 0.05), S(0.9), C(0.25), EXP(-0.05)], NOC + ["vela", "calido", "romantico"], "diwali")
look("noc-verde-noche", "Noche verde", "Green night", n, [SPLIT((-0.02, 0.05, 0.02), (0.02, 0.04, 0.0)), S(0.8), C(0.35)], NOC + ["verde", "misterio"], "city")
look("noc-fiesta", "Fiesta nocturna", "Night party", n, [S(1.25), WB(0.1, 0.12), C(0.3)], NOC + ["fiesta"], "friends")
look("noc-ciudad-fria", "Ciudad fría", "Cold city", n, [WB(-0.4), S(0.65), C(0.45), FADE(0.04)], NOC + ["frio", "invierno"], "city")

# ================================================================ Comida (15)
f = "comida"
COM = ["comida", "food", "restaurante", "receta", "apetitoso"]
look("com-apetitoso", "Apetitoso", "Appetizing", f, [WB(0.25), V(0.35), C(0.2), HUE(0.05, 0.1, sat=1.15)], COM, "food")
look("com-fresco", "Fresco y verde", "Fresh greens", f, [HUE(0.3, 0.12, sat=1.3, light=0.03), EXP(0.08), C(0.15)], COM + ["ensalada", "saludable"], "cooking")
look("com-cafe", "Cafetería", "Coffee shop", f, [WB(0.35), S(0.85), C(0.3), FADE(0.04, (0.05, 0.03, 0.0))], COM + ["cafe", "cafeteria"], "coffee")
look("com-postre", "Postres pastel", "Pastel desserts", f, [EXP(0.1), FADE(0.08, (0.07, 0.04, 0.06)), S(0.95), WB(0.05, 0.08)], COM + ["postre", "dulce", "pastel"], "cake")
look("com-parrilla", "Parrilla", "Grill", f, [WB(0.4), C(0.35), S(1.1), EXP(-0.05)], COM + ["parrilla", "carne", "bbq"], "food")
look("com-panaderia", "Panadería", "Bakery", f, [WB(0.4), S(0.95), C(0.2), ROLL(0.8)], COM + ["pan", "panaderia"], "cooking")
look("com-cocina-luminosa", "Cocina luminosa", "Bright kitchen", f, [EXP(0.15), WB(0.05), V(0.2), C(0.1)], COM + ["cocina", "luminoso"], "cooking")
look("com-moody", "Comida moody", "Moody food", f, [EXP(-0.15), C(0.45), S(0.9), WB(0.15)], COM + ["oscuro", "elegante"], "food")
look("com-fruta", "Fruta jugosa", "Juicy fruit", f, [S(1.25), V(0.3), HUE(0.0, 0.1, sat=1.2), HUE(0.15, 0.1, sat=1.15)], COM + ["fruta", "colorido"], "food")
look("com-bebidas", "Bebidas frías", "Cold drinks", f, [WB(-0.2), V(0.3), C(0.2), EXP(0.05)], COM + ["bebida", "frio"], "coffee")
look("com-picante", "Picante", "Spicy", f, [WB(0.3), HUE(0.0, 0.1, sat=1.3), C(0.3)], COM + ["picante", "rojo"], "cooking")
look("com-mercado", "Mercado", "Market", f, [V(0.4), C(0.2), WB(0.1)], COM + ["mercado", "verduras"], "food")
look("com-brunch", "Brunch", "Brunch", f, [EXP(0.1), WB(0.2), FADE(0.05), S(1.05)], COM + ["desayuno", "brunch"], "coffee")
look("com-chef", "Plato de chef", "Chef's plate", f, [C(0.35), V(0.25), ROLL(0.8)], COM + ["restaurante", "gourmet"], "food")
look("com-helado", "Heladería", "Ice cream", f, [EXP(0.1), WB(-0.05, 0.08), S(1.1), FADE(0.05, (0.05, 0.04, 0.07))], COM + ["helado", "dulce"], "cake")

# ================================================================ Retrato y piel (20)
r = "retrato"
RET = ["retrato", "portrait", "piel", "skin", "belleza"]
look("ret-piel-calida", "Piel cálida", "Warm skin", r, [WB(0.25), HUE(0.06, 0.08, sat=1.05, light=0.02), C(0.1), ROLL(0.82)], RET + ["calido"], "portrait")
look("ret-brillo-suave", "Brillo suave", "Soft glow", r, [EXP(0.08), FADE(0.08, (0.06, 0.04, 0.04)), C(-0.05), S(0.95)], RET + ["suave", "glow"], "makeup")
look("ret-mate", "Retrato mate", "Matte portrait", r, [FADE(0.12), S(0.85), C(0.1)], RET + ["mate"], "portrait")
look("ret-belleza-limpia", "Belleza limpia", "Clean beauty", r, [EXP(0.1), WB(0.05, 0.03), S(0.95), ROLL(0.85)], RET + ["limpio", "natural"], "makeup")
look("ret-bronce", "Bronceado", "Bronze", r, [WB(0.45), S(1.05), C(0.25), HUE(0.07, 0.08, sat=1.1)], RET + ["bronce", "verano"], "fashion")
look("ret-melocoton", "Melocotón", "Peach", r, [WB(0.2, 0.08), FADE(0.06, (0.08, 0.04, 0.03)), S(0.95)], RET + ["melocoton", "suave"], "portrait")
look("ret-porcelana", "Porcelana", "Porcelain", r, [EXP(0.12), S(0.8), WB(-0.05, 0.03), C(0.05)], RET + ["claro", "pálido"], "makeup")
look("ret-estudio", "Estudio", "Studio", r, [C(0.25), S(0.95), ROLL(0.82)], RET + ["estudio", "profesional"], "portrait")
look("ret-editorial", "Editorial", "Editorial", r, [C(0.4), S(0.8), FADE(0.04), WB(0.05)], RET + ["moda", "revista"], "fashion")
look("ret-ensueno", "Ensueño", "Dreamy", r, [FADE(0.15, (0.07, 0.05, 0.08)), EXP(0.08), S(0.85), C(-0.1)], RET + ["sueño", "dreamy"], "quince")
look("ret-quince", "Quinceañera rosada", "Rosy celebration", r, [WB(0.1, 0.12), EXP(0.08), S(1.05), FADE(0.05, (0.06, 0.02, 0.04))], RET + ["fiesta", "rosa"], "quince")
look("ret-novia", "Novia", "Bride", r, [EXP(0.1), WB(0.08), S(0.9), FADE(0.06), ROLL(0.85)], RET + ["boda", "novia", "blanco"], "wedding")
look("ret-calido-moody", "Retrato moody cálido", "Warm moody portrait", r, [WB(0.3), EXP(-0.1), C(0.35), S(0.85)], RET + ["moody"], "portrait")
look("ret-frio-moda", "Moda fría", "Cool fashion", r, [WB(-0.25), S(0.8), C(0.35)], RET + ["moda", "frio"], "fashion")
look("ret-ninos", "Niños felices", "Happy kids", r, [EXP(0.08), V(0.3), WB(0.15)], RET + ["niños", "bebe", "familia"], "baby")
look("ret-bebe", "Bebé suave", "Soft baby", r, [EXP(0.1), FADE(0.08, (0.06, 0.05, 0.05)), S(0.85), WB(0.1)], RET + ["bebe", "recien nacido"], "baby")
look("ret-familia", "Familia", "Family", r, [WB(0.2), V(0.2), C(0.15), ROLL(0.82)], RET + ["familia"], "family")
look("ret-perfil", "Foto de perfil", "Profile photo", r, [C(0.2), V(0.15), EXP(0.05)], RET + ["perfil", "cv", "trabajo"], "man")
look("ret-dorado", "Retrato dorado", "Golden portrait", r, [WB(0.5), SPLIT((0, 0, 0.03), (0.05, 0.03, -0.03)), C(0.2)], RET + ["dorado"], "portrait")
look("ret-ojos", "Mirada intensa", "Intense eyes", r, [C(0.45), S(0.85), EXP(-0.05), ROLL(0.78)], RET + ["intenso"], "man")

# ================================================================ Pastel y anime (15)
a = "pastel"
PAS = ["pastel", "anime", "kawaii", "aesthetic", "suave"]
look("pas-sueno-pastel", "Sueño pastel", "Pastel dream", a, [FADE(0.18, (0.08, 0.06, 0.1)), EXP(0.1), S(0.85)], PAS, "quince")
look("pas-cielo-anime", "Cielo anime", "Anime sky", a, [HUE(0.6, 0.15, sat=1.35, light=0.03), EXP(0.1), V(0.35), C(0.15)], PAS + ["cielo", "azul"], "nature")
look("pas-caricatura", "Caricatura vívida", "Vivid cartoon", a, [S(1.45), C(0.35), EXP(0.05)], PAS + ["caricatura", "vivido"], "friends")
look("pas-rosa-suave", "Rosa suave", "Soft pink", a, [WB(0.05, 0.18), FADE(0.12, (0.08, 0.03, 0.06)), EXP(0.08)], PAS + ["rosa"], "makeup")
look("pas-lavanda", "Lavanda", "Lavender", a, [WB(-0.1, 0.15), FADE(0.12, (0.06, 0.04, 0.1)), S(0.85)], PAS + ["lila", "lavanda"], "portrait")
look("pas-menta", "Menta", "Mint", a, [HUE(0.4, 0.15, sat=1.1), FADE(0.12, (0.03, 0.08, 0.06)), EXP(0.08)], PAS + ["menta", "verde"], "nature")
look("pas-algodon", "Algodón de azúcar", "Cotton candy", a, [WB(0.0, 0.15), HUE(0.55, 0.12, shift=0.04, sat=1.15), FADE(0.12, (0.08, 0.05, 0.08))], PAS + ["dulce"], "friends")
look("pas-ghibli", "Prado de cuento", "Storybook meadow", a, [HUE(0.3, 0.12, sat=1.3), HUE(0.6, 0.12, sat=1.2), EXP(0.08), FADE(0.06)], PAS + ["cuento", "verde"], "nature")
look("pas-melocoton", "Durazno pastel", "Peach pastel", a, [WB(0.25, 0.08), FADE(0.14, (0.1, 0.06, 0.04)), S(0.9)], PAS + ["durazno"], "portrait")
look("pas-cielo-rosa", "Cielo rosa", "Pink sky", a, [SPLIT((0.02, 0.0, 0.05), (0.06, 0.01, 0.04)), FADE(0.08), EXP(0.05)], PAS + ["atardecer"], "beach")
look("pas-kawaii", "Kawaii", "Kawaii", a, [EXP(0.12), S(1.15), FADE(0.08, (0.08, 0.05, 0.08))], PAS + ["tierno"], "baby")
look("pas-acuarela", "Acuarela", "Watercolour", a, [FADE(0.2, (0.08, 0.08, 0.08)), S(0.75), C(-0.1)], PAS + ["acuarela", "arte"], "flowers")
look("pas-crema", "Crema", "Cream", a, [WB(0.15), FADE(0.15, (0.1, 0.08, 0.05)), S(0.8)], PAS + ["crema", "beige"], "interior")
look("pas-nube", "Nube", "Cloud", a, [EXP(0.15), S(0.8), FADE(0.1), C(-0.1)], PAS + ["blanco", "claro"], "wedding")
look("pas-arcoiris", "Arcoíris pastel", "Pastel rainbow", a, [V(0.4), FADE(0.12, (0.06, 0.06, 0.08)), EXP(0.08)], PAS + ["arcoiris"], "friends")

# ================================================================ Estético y moody (15)
e = "estetico"
EST = ["estetico", "aesthetic", "moody", "instagram", "feed"]
look("est-academia", "Academia oscura", "Dark academia", e, [WB(0.3), S(0.7), C(0.35), EXP(-0.15), FADE(0.05, (0.05, 0.03, 0.0))], EST + ["academia", "libros", "otoño"], "study")
look("est-bosque", "Bosque moody", "Moody forest", e, [HUE(0.3, 0.15, shift=0.04, sat=0.8), WB(-0.1), C(0.35), EXP(-0.1)], EST + ["bosque", "verde"], "nature")
look("est-beige", "Beige", "Beige", e, [S(0.6), WB(0.25), FADE(0.1, (0.08, 0.06, 0.03))], EST + ["beige", "minimal"], "interior")
look("est-tierra", "Tonos tierra", "Earth tones", e, [S(0.8), WB(0.35), HUE(0.33, 0.15, shift=-0.05, sat=0.7), C(0.2)], EST + ["tierra", "marron"], "nature")
look("est-crema-moody", "Crema moody", "Moody cream", e, [WB(0.2), S(0.7), C(0.25), FADE(0.08)], EST + ["crema"], "coffee")
look("est-gris", "Gris urbano", "Urban grey", e, [S(0.5), C(0.35), WB(-0.1), FADE(0.04)], EST + ["gris", "urbano"], "city")
look("est-oliva", "Oliva", "Olive", e, [HUE(0.25, 0.15, shift=-0.02, sat=0.75), WB(0.15, -0.1), FADE(0.06)], EST + ["oliva", "verde"], "fashion")
look("est-chocolate", "Chocolate", "Chocolate", e, [WB(0.4), S(0.75), C(0.35), EXP(-0.1)], EST + ["marron", "calido"], "coffee")
look("est-azul-polvo", "Azul empolvado", "Dusty blue", e, [WB(-0.2), S(0.65), FADE(0.1, (0.03, 0.05, 0.08))], EST + ["azul"], "beach")
look("est-minimal", "Minimal blanco", "Minimal white", e, [EXP(0.15), S(0.75), C(0.05)], EST + ["minimal", "blanco", "limpio"], "interior")
look("est-vino", "Vino", "Wine", e, [WB(0.15, 0.12), S(0.8), C(0.35), EXP(-0.1)], EST + ["vino", "rojo", "elegante"], "restaurant")
look("est-musgo", "Musgo", "Moss", e, [HUE(0.3, 0.15, sat=0.8, light=-0.03), WB(0.1), C(0.25)], EST + ["musgo", "verde"], "garden")
look("est-lluvia", "Día de lluvia", "Rainy day", e, [WB(-0.25), S(0.6), FADE(0.08), C(0.15)], EST + ["lluvia", "gris", "calma"], "city")
look("est-ambar", "Ámbar", "Amber", e, [WB(0.55), S(0.85), C(0.3), FADE(0.04)], EST + ["ambar", "calido"], "diwali")
look("est-carbon", "Carbón", "Charcoal", e, [S(0.35), C(0.5), EXP(-0.15), WB(-0.05)], EST + ["oscuro", "carbon"], "man")

# ================================================================ Estaciones (15)
t = "estaciones"
EAS = ["estaciones", "seasons"]
look("est-otono", "Otoño", "Autumn", t, [WB(0.4), HUE(0.1, 0.12, sat=1.3), HUE(0.25, 0.12, shift=-0.06, sat=1.1), C(0.2)], EAS + ["otoño", "autumn", "hojas"], "autumn")
look("est-otono-suave", "Otoño suave", "Soft autumn", t, [WB(0.3), HUE(0.08, 0.12, sat=1.15), FADE(0.08), S(0.9)], EAS + ["otoño"], "autumn")
look("est-invierno", "Invierno", "Winter", t, [WB(-0.45), S(0.7), EXP(0.08), C(0.15)], EAS + ["invierno", "winter", "nieve"], "christmas")
look("est-invierno-calido", "Invierno acogedor", "Cozy winter", t, [WB(0.35), S(0.85), C(0.2), FADE(0.05)], EAS + ["invierno", "acogedor", "navidad"], "christmas")
look("est-primavera", "Primavera", "Spring", t, [EXP(0.1), V(0.35), HUE(0.3, 0.12, sat=1.2), HUE(0.9, 0.12, sat=1.15)], EAS + ["primavera", "spring", "flores"], "flowers")
look("est-flores", "Flores", "Blossom", t, [HUE(0.92, 0.15, sat=1.25, light=0.03), EXP(0.08), FADE(0.05)], EAS + ["flores", "rosa"], "flowers")
look("est-verano-intenso", "Verano intenso", "Hot summer", t, [WB(0.4), S(1.25), C(0.3)], EAS + ["verano", "calor"], "beach")
look("est-navidad", "Navidad", "Christmas", t, [WB(0.25), HUE(0.0, 0.1, sat=1.25), HUE(0.33, 0.12, sat=1.15), C(0.25)], EAS + ["navidad", "christmas", "rojo"], "christmas")
look("est-luces-navidad", "Luces de Navidad", "Christmas lights", t, [WB(0.4), S(1.1), C(0.3), EXP(-0.05)], EAS + ["navidad", "luces"], "xmaslights")
look("est-ano-nuevo", "Año Nuevo dorado", "Golden New Year", t, [WB(0.4), S(1.1), C(0.3), SPLIT((0, 0, 0.04), (0.05, 0.03, -0.03))], EAS + ["año nuevo", "dorado"], "newyear")
look("est-san-valentin", "San Valentín", "Valentine's", t, [WB(0.15, 0.15), HUE(0.97, 0.12, sat=1.2), FADE(0.05)], EAS + ["san valentin", "amor", "rojo"], "couple")
look("est-pascua", "Pascua", "Easter", t, [EXP(0.1), FADE(0.1, (0.08, 0.08, 0.06)), S(1.05)], EAS + ["pascua", "pastel"], "easter")
look("est-lluvias", "Temporada de lluvias", "Rainy season", t, [WB(-0.2), HUE(0.3, 0.12, sat=1.1), S(0.85), C(0.2)], EAS + ["lluvia", "verde"], "nature")
look("est-dia-nieve", "Día de nieve", "Snow day", t, [WB(-0.3), EXP(0.15), S(0.8), ROLL(0.85)], EAS + ["nieve", "blanco"], "christmas")
