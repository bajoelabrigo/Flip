"""Text animations, part A: typewriter, karaoke, bounce and rhythm, neon, glitch, slides and wipes.

Research (2026-10-16): CapCut's text In / Out / Loop galleries, TikTok and Instagram caption motion,
After Effects text animator presets (Animate In/Out, Blurs, Mechanical, Rotation, Multi-Line) and
Premiere / Filmora title animations. None of these duplicate the 47 the app ships
(presets/text-animations); where a built-in already does a motion, the variant here changes the unit,
order, easing or adds a second property.

Units: positions in em unless the unit says otherwise (+y is down); scale in %; durations in s.
"""

from __future__ import annotations

from anims_kit import (A, P, amount, bezier, color, curve, curve_in, curve_out, everything, karaoke, lp, mode, pos,
                       pulse_sel, ref, rv, speed, spike, stagger_sel, sweep, wiggle)

SNAP = bezier(0.05, 0.9, 0.1, 1.0)
SPRING = bezier(0.2, 2.1, 0.45, 1.0)


def caret(shape="bar", width=0.08, height=1.0, colour="") -> dict:
    return {"enabled": "{caret}", "leadUs": ref("lead", 1_000_000), "blinkOnUs": 220000, "blinkOffUs": 280000,
            "holdAfterUs": ref("hold", 1_000_000), "widthEm": width, "heightEm": height, "shape": shape,
            "color": colour}


CARET_PARAMS = [P("caret", "Caret", type="bool", default=True),
                P("lead", "Caret lead", default=0.3, unit="s", min=0, max=2, step=0.05),
                P("hold", "Hold after", default=0.6, unit="s", min=0, max=5, step=0.1)]

T = ("Escribe tu historia", "Write your story")

# --- typewriter ---------------------------------------------------------------------------------
TYPE = [
    rv("maq-cursor", "Tecleo con cursor", "Typing with cursor", "maquina", "character", T, {}, stagger=0.07,
       duration=0.0, ease="linear", fade=1.0, slots=["in"], params=CARET_PARAMS, caret=caret(),
       flags={"durationLocked": True}, tags=["maquina de escribir", "typewriter", "cursor"]),
    rv("maq-terminal", "Terminal", "Terminal", "maquina", "character", ("> iniciando sistema…", "> booting system…"),
       {}, stagger=0.035, duration=0.0, ease="linear", fade=1.0, slots=["in"], params=CARET_PARAMS,
       caret=caret("block", 0.55, 1.0), flags={"durationLocked": True}, tags=["terminal", "codigo", "hacker"],
       look="mono"),
    rv("maq-guion", "Cursor de guion bajo", "Underscore cursor", "maquina", "character", ("Hola, soy Sam", "Hi, I'm Sam"),
       {}, stagger=0.08, duration=0.0, ease="linear", fade=1.0, slots=["in"], params=CARET_PARAMS,
       caret=caret("underscore", 0.6, 0.1), flags={"durationLocked": True}, tags=["cursor", "guion"], look="mono"),
    rv("maq-palabra", "Palabra por palabra", "Word by word", "maquina", "word", ("Una palabra a la vez", "One word at a time"),
       {}, unit="word", stagger=0.22, duration=0.0, ease="linear", fade=1.0, slots=["in", "out"],
       flags={"durationLocked": True}, tags=["palabra", "subtitulos", "ritmo"]),
    rv("maq-suave", "Tecleo suave", "Soft typing", "maquina", "character", T, {"position": pos(0, 0.12)}, stagger=0.045,
       duration=0.16, ease="smooth", fade=1.0, tags=["suave", "tecleo"]),
    rv("maq-tecla", "Golpe de tecla", "Key strike", "maquina", "character", ("CLIC CLIC CLIC", "CLICK CLICK CLICK"),
       {"scale": 170}, stagger=0.06, duration=0.14, ease="easeOut", fade=0.3, ease_spec=SNAP,
       tags=["tecla", "golpe"]),
    rv("maq-borrar", "Borrado de teclado", "Backspace", "maquina", "character", ("Mejor no lo digo", "Better not say it"),
       {}, stagger=0.045, duration=0.0, ease="linear", fade=1.0, slots=["out"], flags={"durationLocked": True},
       extra=[], tags=["borrar", "backspace", "salida"]),
    rv("maq-centrado", "Tecleo centrado", "Centred typing", "maquina", "character", ("Siempre al centro", "Always centred"),
       {"collapse": True}, stagger=0.06, duration=0.0, ease="linear", fade=1.0, slots=["in"],
       flags={"durationLocked": True}, tags=["centrado", "tecleo"]),
    rv("maq-chat", "Mensaje de chat", "Chat message", "maquina", "word", ("hola 👋 ¿cómo estás?", "hi 👋 how are you?"),
       {"position": pos(0, 0.35), "scale": 85}, unit="word", stagger=0.14, duration=0.25, ease="back", fade=0.5,
       tags=["chat", "mensaje", "conversacion"]),
    rv("maq-luminoso", "Tecleo luminoso", "Glowing typing", "maquina", "character", ("Brilla con cada letra", "Glow with every letter"),
       {}, stagger=0.05, duration=0.0, ease="linear", fade=1.0, slots=["in"],
       params=[color("flash", "Arrive colour", "#ffe26a"), amount(0.5, "s", 0.05, 3, id="decay", label="Decay")],
       extra=[A([{**stagger_sel(), "durationUs": ref("decay", 1_000_000), "ease": "easeOut"}], fillColor="{flash}")],
       flags={"durationLocked": True}, tags=["brillo", "color", "tecleo"]),
    rv("maq-azar", "Letras al azar", "Random letters", "maquina", "character", ("Sorpresa", "Surprise"), {},
       stagger=0.05, duration=0.0, ease="linear", order="random", fade=1.0, flags={"durationLocked": True},
       tags=["azar", "random", "letras"]),
    rv("maq-centro", "Desde el centro", "From the centre", "maquina", "character", ("EQUILIBRIO", "BALANCE"), {},
       stagger=0.06, duration=0.0, ease="linear", order="centerOut", fade=1.0, flags={"durationLocked": True},
       tags=["centro", "simetria"]),
    rv("maq-lineas", "Línea por línea", "Line by line", "maquina", "line", ("Primera línea\nsegunda línea\ntercera línea",
                                                                            "First line\nsecond line\nthird line"),
       {"position": pos(0, 0.15)}, unit="line", stagger=0.45, duration=0.2, ease="easeOut", fade=1.0,
       tags=["lineas", "lista", "guion"]),
    rv("maq-rapido", "Tecleo rápido", "Fast typing", "maquina", "character", ("Esto va muy rápido", "This goes really fast"),
       {}, stagger=0.025, duration=0.0, ease="linear", fade=1.0, slots=["in"], params=CARET_PARAMS, caret=caret(),
       flags={"durationLocked": True}, tags=["rapido", "fast", "cursor"]),
    rv("maq-antigua", "Máquina antigua", "Old typewriter", "maquina", "character", ("Querido diario", "Dear diary"),
       {"position": pos(0, -0.18), "rotation": 9}, stagger=0.08, duration=0.09, ease="linear", fade=0.2,
       tags=["antigua", "vintage", "diario"], look="mono"),
    rv("maq-codigo", "Código", "Code", "maquina", "character", ("acceso concedido", "access granted"), {},
       stagger=0.03, duration=0.0, ease="linear", fade=1.0, slots=["in"],
       params=CARET_PARAMS + [color("flash", "Arrive colour", "#36ff8f")],
       extra=[A([{**stagger_sel(), "durationUs": 450000, "ease": "easeIn"}], fillColor="{flash}")],
       caret=caret("block", 0.55, 1.0, "#ff36ff8f"), flags={"durationLocked": True},
       tags=["codigo", "hacker", "verde"], look="mono"),
]

# --- karaoke ------------------------------------------------------------------------------------
K = ("Canta conmigo esta canción", "Sing this song with me")
K2 = ("Cada palabra cuenta aquí", "Every single word counts here")


def kar(id, es, en, props, *, params=(), sample=K, tags=(), sels=None, look="caption"):
    return lp(id, es, en, "karaoke", "word", sample, [A(sels or [karaoke()], **props)], params=params,
              tags=["karaoke", "subtitulos", "palabra", *tags], look=look)


KARAOKE = [
    kar("kar-salto", "Salto karaoke", "Karaoke hop", {"position": pos(0, ref("lift", -1)), "scale": 108},
        params=[amount(0.22, "em", 0, 1, id="lift", label="Lift")], tags=["salto"]),
    kar("kar-crecer", "Palabra que crece", "Growing word", {"scale": "{scale}"},
        params=[P("scale", "Scale", default=128, unit="%", min=100, max=250, step=1)], tags=["crecer", "grande"]),
    kar("kar-amarillo", "Karaoke amarillo", "Yellow karaoke", {"fillColor": "{color}"},
        params=[color("color", "Colour A", "#ffe600")], tags=["amarillo", "color"]),
    kar("kar-verde", "Karaoke verde", "Green karaoke", {"fillColor": "{color}", "scale": 104},
        params=[color("color", "Colour A", "#3dff6e")], sample=K2, tags=["verde", "color"]),
    kar("kar-contorno", "Contorno de color", "Coloured outline", {"strokeColor": "{color}", "strokeWidth": 5},
        params=[color("color", "Colour A", "#ffd23f")], tags=["contorno", "outline"]),
    kar("kar-inclinar", "Inclinación", "Tilt", {"rotation": -7, "scale": 112}, sample=K2, tags=["inclinar", "giro"]),
    kar("kar-temblor", "Palabra que tiembla", "Shaking word",
        {"position": pos(ref("amount"), ref("amount"), "px"), "rotation": 4},
        sels=[karaoke(), mode(wiggle("character", "noise", hz=14, phase=97), "intersect")],
        params=[amount(4, "px", 0, 20, 0.5)], tags=["temblor", "shake"]),
    kar("kar-latido", "Latido", "Heartbeat", {"scale": 120},
        sels=[karaoke(), mode(wiggle("word", "sine", hz="{speed}", phase=0, lo=0, hi=100), "intersect")],
        params=[speed(4.0, 0.5, 10)], tags=["latido", "pulso"]),
    kar("kar-atenuar", "Resto atenuado", "Dim the rest", {"opacity": "{opacity}"},
        sels=[everything("word"), mode(karaoke(), "subtract")],
        params=[P("opacity", "Amount", default=40, unit="%", min=0, max=100, step=1)], tags=["atenuar", "foco"]),
    kar("kar-enfoque", "Enfoque en la palabra", "Focus on the word", {"blur": "{blur}", "opacity": 70},
        sels=[everything("word"), mode(karaoke(), "subtract")],
        params=[P("blur", "Blur", default=5, unit="px", min=0, max=30, step=1)], sample=K2, tags=["enfoque", "blur"]),
    kar("kar-gigante-rosa", "Golpe rosa", "Pink punch", {"scale": 135, "fillColor": "{color}"},
        params=[color("color", "Colour A", "#ff4fb8")], tags=["rosa", "grande"]),
    kar("kar-ola", "Ola en la palabra", "Wave in the word", {"position": pos(0, ref("amount", -1))},
        sels=[karaoke(), mode(wiggle("character", "sine", hz="{speed}", phase=55, lo=0, hi=100), "intersect")],
        params=[amount(0.16, "em", 0, 1), speed(3.0, 0.5, 8)], tags=["ola", "wave"]),
    kar("kar-estirar", "Estirar", "Stretch", {"scaleY": 135, "scaleX": 92}, sample=K2, tags=["estirar"]),
    kar("kar-celeste", "Sube en celeste", "Rise in cyan", {"position": pos(0, -0.14), "fillColor": "{color}"},
        params=[color("color", "Colour A", "#3be8ff")], tags=["celeste", "subir"]),
    kar("kar-rojo", "Golpe rojo", "Red punch", {"scale": 122, "fillColor": "{color}", "strokeWidth": 2},
        params=[color("color", "Colour A", "#ff3347")], sample=K2, tags=["rojo", "golpe"]),
    kar("kar-baile", "Palabra que baila", "Dancing word", {"rotation": "{angle}"},
        sels=[karaoke(), mode(wiggle("word", "sine", hz="{speed}", phase=0), "intersect")],
        params=[P("angle", "Angle", default=9, unit="°", min=0, max=45, step=0.5), speed(5.0, 0.5, 12)],
        tags=["baile", "dance"]),
    kar("kar-protagonista", "Protagonista", "Spotlight", {"scale": 88, "opacity": 55},
        sels=[everything("word"), mode(karaoke(), "subtract")], tags=["protagonista", "foco"]),
    kar("kar-neon", "Neón por palabra", "Neon per word",
        {"fillColor": "#ffffffff", "strokeColor": "{color}", "strokeWidth": 4, "scale": 106},
        params=[color("color", "Colour A", "#ff2bd6")], sample=K2, tags=["neon"]),
]

# --- bounce and rhythm --------------------------------------------------------------------------
B = ("¡Salta conmigo!", "Jump with me!")
BEAT = ("AL RITMO", "ON THE BEAT")

BOUNCE = [
    rv("reb-letras", "Rebote de letras", "Bouncing letters", "rebote", "character", B, {"position": pos(0, -1.4)},
       stagger=0.04, duration=0.7, ease="bounce", order="random", fade=0.2, flags={"easeLocked": True},
       tags=["rebote", "letras"]),
    rv("reb-trampolin", "Trampolín", "Trampoline", "rebote", "character", ("¡Arriba!", "Up!"),
       {"position": pos(0, 1.0), "scaleY": 60, "scaleX": 120}, stagger=0.035, duration=0.55, ease="back", fade=0.35,
       tags=["trampolin", "salto"]),
    lp("reb-pelota", "Pelota al ritmo", "Ball on the beat", "rebote", "kinetic", BEAT,
       [A([everything("character")],
          position=pos(0, curve([(0, 0), (0.15, -0.3), (0.3, -0.42), (0.45, -0.3), (0.62, 0), (0.7, 0), (1, 0)]), "em"),
          scaleY=curve([(0, 92), (0.1, 104), (0.6, 100), (0.64, 88), (0.72, 100), (1, 100)]),
          scaleX=curve([(0, 106), (0.1, 98), (0.6, 100), (0.64, 110), (0.72, 100), (1, 100)]))],
       period=0.5, tags=["120 bpm", "ritmo", "beat"]),
    lp("reb-golpe-ritmo", "Golpe al ritmo", "Beat punch", "rebote", "kinetic", BEAT,
       [A([], scale=curve([(0, "{punch}"), (0.18, 100), (1, 100)]))],
       params=[P("punch", "Scale", default=114, unit="%", min=100, max=200, step=1)], period=0.5,
       tags=["120 bpm", "ritmo", "beat", "zoom"]),
    lp("reb-cadena", "Saltos en cadena", "Chain hops", "rebote", "character", B,
       [A([wiggle("character", "sine", hz="{speed}", phase=40, lo=0, hi=100)], position=pos(0, ref("amount", -1)))],
       params=[amount(0.22, "em", 0, 1), speed(2.0, 0.2, 6)], tags=["cadena", "saltos"]),
    curve_in("reb-gelatina", "Gelatina", "Jelly", "rebote", "kinetic", ("¡Boing!", "Boing!"),
             [A([everything("character")],
                scaleX=curve([(0, 0), (0.32, 128), (0.52, 88), (0.7, 106), (0.86, 97), (1, 100)]),
                scaleY=curve([(0, 0), (0.32, 78), (0.52, 114), (0.7, 95), (0.86, 102), (1, 100)]),
                opacity=curve([(0, 0), (0.18, 100), (1, 100)]))], duration=0.85, tags=["gelatina", "elastico"]),
    rv("reb-resorte", "Resorte", "Spring", "rebote", "word", ("Arranca con fuerza", "Start strong"), {"scale": 0},
       unit="word", stagger=0.09, duration=0.55, ease="easeOut", fade=0.3, ease_spec=SPRING, tags=["resorte", "spring"]),
    lp("reb-palabras", "Palabras que saltan", "Hopping words", "rebote", "word", ("uno dos tres cuatro", "one two three four"),
       [A([wiggle("word", "sine", hz="{speed}", phase=180, lo=0, hi=100)], position=pos(0, ref("amount", -1)))],
       params=[amount(0.2, "em", 0, 1), speed(1.0, 0.2, 4)], tags=["palabras", "saltos"]),
    lp("reb-estira", "Estira y encoge", "Squash loop", "rebote", "character", ("blandito", "squishy"),
       [A([wiggle("character", "sine", hz="{speed}", phase=0)], scaleY=112, scaleX=94)],
       params=[speed(2.0, 0.2, 6)], tags=["estirar", "squash"]),
    rv("reb-elastico", "Elástico lateral", "Side elastic", "rebote", "character", ("¡Llegué!", "I'm here!"),
       {"position": pos(1.4, 0)}, stagger=0.03, duration=0.6, ease="easeOut", fade=0.25,
       ease_spec=bezier(0.25, 1.8, 0.5, 1.0), tags=["elastico", "lateral"]),
    rv("reb-pesada", "Caída pesada", "Heavy drop", "rebote", "basic", ("PESADO", "HEAVY"),
       {"position": pos(0, -0.9, "box"), "scale": 110}, unit="block", duration=0.75, ease="bounce", fade=0.15,
       flags={"unitLocked": True, "orderLocked": True, "easeLocked": True}, tags=["caida", "pesado"]),
    rv("reb-salto-salida", "Salto y caída", "Hop and drop", "rebote", "character", ("¡Adiós!", "Bye!"),
       {"position": pos(0, 2.6)}, stagger=0.03, duration=0.55, ease="back", order="random", fade=0.4,
       slots=["out"], tags=["salida", "caida"]),
    lp("reb-redoble", "Redoble", "Drum roll", "rebote", "kinetic", ("TA-RA-RÁ", "DRUM ROLL"),
       [A([], scale=curve([(0, 106), (0.35, 100), (1, 100)]), position=pos(0, curve([(0, -0.03), (0.35, 0), (1, 0)])))],
       period=0.25, tags=["redoble", "tambor", "rapido"]),
    lp("reb-color-ritmo", "Color al ritmo", "Colour on the beat", "rebote", "colour", BEAT,
       [A([pulse_sel([(0, 100), (0.35, 0), (1, 0)])], fillColor="{color}", scale=108)],
       params=[color("color", "Colour A", "#ffe600")], period=0.5, tags=["color", "120 bpm", "beat"]),
    lp("reb-ola-salta", "Ola que salta", "Leaping wave", "rebote", "character", ("ola de energía", "wave of energy"),
       [A([sweep("character", 30, "smooth")], position=pos(0, ref("amount", -1)), scale=112)],
       params=[amount(0.35, "em", 0, 1.5)], period=1.0, tags=["ola", "recorre"]),
    rv("reb-pop-giro", "Pop con giro", "Pop and twist", "rebote", "word", ("Nuevo episodio", "New episode"),
       {"scale": 0, "rotation": -14}, unit="word", stagger=0.09, duration=0.45, ease="back", fade=0.3,
       tags=["pop", "giro"]),
    rv("reb-aterrizaje", "Aterrizaje", "Landing", "rebote", "word", ("Ya llegamos", "We have landed"),
       {"position": pos(0, -1.2), "scaleY": 140, "scaleX": 80}, unit="word", stagger=0.12, duration=0.7,
       ease="bounce", fade=0.2, flags={"easeLocked": True}, tags=["aterrizaje", "caida"]),
    lp("reb-metronomo", "Metrónomo", "Metronome", "rebote", "kinetic", ("tic tac", "tick tock"),
       [A([wiggle("all", "triangle", hz="{speed}", phase=0)], rotation="{angle}")],
       params=[P("angle", "Angle", default=6, unit="°", min=0, max=30, step=0.5), speed(1.0, 0.1, 4)],
       tags=["metronomo", "balanceo"]),
]

# --- neon and lights ----------------------------------------------------------------------------
NE = ("ABIERTO", "OPEN")


def flicker_sel(domain="{unit}", order="{order}") -> list:
    return [{"driver": "stagger", "domain": domain, "order": order, "staggerUs": ref("stagger", 1_000_000),
             "durationUs": ref("duration", 1_000_000), "ease": "linear"},
            mode(wiggle(domain if not domain.startswith("{") else "character", "noise", hz=18, phase=97, lo=0, hi=100),
                 "intersect")]


def flicker_on(id, es, en, sample, *, unit="character", stagger=0.07, duration=0.4, order="random",
               slots=("in",), tags=()):
    """Each piece flickers (noise) while it lights up, then stays on: a neon tube striking."""
    anim = rv(id, es, en, "neon", "light", sample, {}, unit=unit, stagger=stagger, duration=duration, ease="linear",
              order=order, fade=None, slots=slots, tags=tags)
    domain = "{unit}" if unit == "character" else unit
    anim.animators = [A(flicker_sel(domain), opacity=0), A([{**stagger_sel(unit=domain), "durationUs": 0}], opacity=0)]
    anim.flags = {"easeLocked": True} if unit == "character" else {"easeLocked": True, "unitLocked": True}
    return anim


NEON = [
    flicker_on("neo-letras", "Encendido letra por letra", "Lighting up letter by letter", NE,
               tags=["encendido", "letrero"]),
    lp("neo-zumbido", "Zumbido por letra", "Buzzing letters", "neon", "light", NE,
       [A([wiggle("character", "noise", hz="{speed}", phase=97, lo=0, hi=100)], opacity=ref("depth", -100, 100))],
       params=[speed(16, 1, 30), P("depth", "Intensity", default=0.35, min=0, max=1, step=0.05)],
       tags=["zumbido", "buzz"]),
    lp("neo-falla", "Letra que falla", "Faulty letter", "neon", "light", ("BAR ABIERTO", "BAR OPEN"),
       [A([{"driver": "curves", "domain": "character", "units": "percent", "shape": "square", "start": 55,
            "end": 68, "amount": curve([(0, 0, "hold"), (0.6, 100, "hold"), (0.64, 0, "hold"), (0.7, 100, "hold"),
                                       (0.73, 0, "hold"), (0.86, 100, "hold"), (0.88, 0, "hold"), (1, 0, "hold")])}],
          opacity=12)], period=2.4, tags=["falla", "letrero", "realista"]),
]

word_flicker = flicker_on("neo-palabras", "Encendido por palabra", "Word by word sign",
                          ("CAFÉ · BAR · MÚSICA", "CAFE · BAR · MUSIC"), unit="word", stagger=0.35, duration=0.45,
                          order="forward", tags=["palabras", "letrero"])
off_flicker = flicker_on("neo-apagado", "Apagado", "Switch off", ("CERRADO", "CLOSED"), stagger=0.06, duration=0.35,
                         slots=("out",), tags=["apagado", "salida"])
line_flicker = flicker_on("neo-tubos", "Tubo por tubo", "Tube by tube", ("ABIERTO\nTODA LA NOCHE", "OPEN\nALL NIGHT"),
                          unit="line", stagger=0.5, duration=0.5, order="forward", tags=["lineas", "tubos"])

NEON += [
    word_flicker, off_flicker, line_flicker,
    lp("neo-respira", "Brillo que respira", "Breathing glow", "neon", "light", ("Buenas noches", "Good night"),
       [A([wiggle("all", "sine", hz="{speed}", phase=0, lo=0, hi=100)], opacity=60, blur=2.5)],
       params=[speed(0.5, 0.05, 3)], tags=["respira", "suave"]),
    lp("neo-estrobo", "Estroboscopio", "Strobe", "neon", "light", ("FIESTA", "PARTY"),
       [A([pulse_sel([(0, 0, "hold"), (0.5, 100, "hold"), (1, 100, "hold")], "all")], opacity=15)],
       period=0.25, tags=["estrobo", "fiesta", "rapido"]),
    lp("neo-bicolor", "Letrero bicolor", "Two-colour sign", "neon", "colour", NE,
       [A([pulse_sel([(0, 0, "hold"), (0.5, 100, "hold"), (1, 100, "hold")], "all")], fillColor="{colorB}",
          strokeColor="{colorB}")],
       params=[color("colorB", "Colour B", "#3be8ff")], period=1.2, tags=["bicolor", "cambio de color"]),
    lp("neo-secuencia", "Luces en secuencia", "Chasing lights", "neon", "light", ("CINE", "CINEMA"),
       [A([everything("character"), mode(sweep("character", 34, "square", -34, 100), "subtract")], opacity=30)],
       period=1.2, tags=["secuencia", "marquesina"]),
    lp("neo-marquesina", "Marquesina", "Marquee", "neon", "light", ("ESTRENO", "PREMIERE"),
       [A([wiggle("character", "sine", hz="{speed}", phase=180, lo=0, hi=100)], opacity=25)],
       params=[speed(2.0, 0.2, 8)], tags=["marquesina", "teatro", "bombillas"]),
    rv("neo-destello", "Destello de luz", "Light burst", "neon", "light", ("BRILLA", "SHINE"),
       {"scale": 116, "blur": 22}, unit="block", duration=0.5, ease="easeOut", fade=0.4,
       flags={"unitLocked": True, "orderLocked": True}, tags=["destello", "flash"]),
    lp("neo-latido", "Latido luminoso", "Glowing pulse", "neon", "light", ("LIVE", "LIVE"),
       [A([wiggle("all", "sine", hz="{speed}", phase=0, lo=0, hi=100)], scale=103, strokeWidth=4)],
       params=[speed(1.2, 0.1, 5)], tags=["latido", "contorno"]),
    lp("neo-chispa", "Chispazos", "Sparks", "neon", "light", ("ELECTRICIDAD", "ELECTRICITY"),
       [A([wiggle("character", "noise", hz="{speed}", phase=97, lo=-300, hi=100)], fillColor="#ffffffff",
          strokeColor="#ffffffff")], params=[speed(6, 1, 20)], tags=["chispa", "electrico"]),
    curve_out("neo-apagon", "Apagón", "Blackout", "neon", "light", ("SIN LUZ", "NO POWER"),
              [A([], opacity=curve([(0, 100, "hold"), (0.18, 20, "hold"), (0.28, 100, "hold"), (0.5, 0, "hold"),
                                    (0.58, 85, "hold"), (0.72, 0, "hold"), (1, 0, "hold")]))], duration=0.9,
              tags=["apagon", "salida"]),
    rv("neo-encender", "Letrero que se enciende", "Sign switching on", "neon", "light", ("BIENVENIDOS", "WELCOME"),
       {"fillColor": "#ff3a3a3a", "strokeColor": "#ff3a3a3a"}, unit="block", duration=0.9, ease="linear", fade=None,
       slots=["in"], extra=[A([mode(stagger_sel(0.6, ease="linear"), "add"),
                               mode(wiggle("all", "noise", hz=16, phase=0, lo=0, hi=100), "intersect")], opacity=30)],
       flags={"unitLocked": True, "orderLocked": True, "easeLocked": True}, tags=["encender", "letrero"]),
]

# --- glitch -------------------------------------------------------------------------------------
G = ("SEÑAL PERDIDA", "SIGNAL LOST")

GLITCH = [
    rv("gli-rgb", "Glitch RGB", "RGB glitch", "glitch", "kinetic", G, {"position": pos(0.3, 0), "skew": 25},
       stagger=0.02, duration=0.3, ease="linear", order="random", fade=0.5,
       params=[color("colorA", "Colour A", "#ff00d4")],
       extra=[A([stagger_sel(1.4, ease="linear")], fillColor="{colorA}")], tags=["rgb", "glitch"], look="tech"),
    lp("gli-rafagas", "Ráfagas de glitch", "Glitch bursts", "glitch", "kinetic", G,
       [A([wiggle("character", "noise", hz=16, phase=97),
           mode(pulse_sel([*spike(0.0, 0.1), ], "all"), "intersect")],
          position=pos(ref("amount"), 0), skew=18)],
       params=[amount(0.18, "em", 0, 1)], period=1.6, tags=["rafagas", "interferencia"], look="tech"),
    rv("gli-decodificar", "Decodificar", "Decode", "glitch", "kinetic", ("CONTRASEÑA", "PASSWORD"), {},
       stagger=0.018, duration=0.0, ease="linear", order="random", fade=1.0, slots=["in"],
       params=[color("colorA", "Arrive colour", "#00ff9c")],
       extra=[A([{**stagger_sel(), "durationUs": 500000, "ease": "easeIn"}], fillColor="{colorA}", blur=3)],
       flags={"durationLocked": True}, tags=["decodificar", "hacker"], look="tech"),
    lp("gli-lineas", "Desfase de líneas", "Line slip", "glitch", "kinetic", ("ERROR\nDE SISTEMA", "SYSTEM\nERROR"),
       [A([wiggle("line", "noise", hz="{speed}", phase=120)], position=pos(ref("amount"), 0))],
       params=[amount(0.1, "em", 0, 1), speed(7, 1, 25)], tags=["lineas", "desfase"], look="tech"),
    rv("gli-salida", "Salida glitch", "Glitch out", "glitch", "kinetic", G, {"position": pos(-0.4, 0), "skew": -30},
       stagger=0.015, duration=0.25, ease="easeIn", order="random", fade=0.6, slots=["out"], tags=["salida"],
       look="tech"),
    rv("gli-escaner", "Escáner", "Scanner", "glitch", "kinetic", ("ESCANEANDO", "SCANNING"),
       {"wipe": {"enabled": True, "angleDeg": 90, "softness": 0.04}}, unit="block", duration=0.9, ease="linear",
       fade=None, params=[color("colorA", "Colour A", "#00e5ff")],
       extra=[A([stagger_sel(1.25, ease="easeIn")], fillColor="{colorA}")],
       flags={"unitLocked": True, "orderLocked": True}, tags=["escaner", "scan"], look="tech"),
    lp("gli-destellos", "Destellos de color", "Colour flashes", "glitch", "colour", G,
       [A([wiggle("character", "noise", hz=9, phase=97, lo=-200, hi=100)], fillColor="#ffff00d4"),
        A([wiggle("character", "noise", hz=11, phase=61, lo=-200, hi=100, seed=7)], fillColor="#ff00f0ff")],
       tags=["destellos", "colores"], look="tech"),
    curve_in("gli-enfoque", "Enfoque digital", "Digital focus", "glitch", "kinetic", ("CARGANDO", "LOADING"),
             [A([], blur=curve([(0, 26, "hold"), (0.25, 13, "hold"), (0.5, 6, "hold"), (0.75, 2, "hold"), (1, 0)]),
                opacity=curve([(0, 30, "hold"), (0.25, 60, "hold"), (0.5, 85, "hold"), (0.75, 100)]))],
             duration=0.8, tags=["pixel", "enfoque", "carga"], look="tech"),
    curve_in("gli-tiron", "Tirón", "Yank", "glitch", "kinetic", ("¡ZAS!", "ZAP!"),
             [A([], position=pos(curve([(0, 0.6, "hold"), (0.14, -0.45, "hold"), (0.28, 0.28, "hold"),
                                        (0.42, -0.12, "hold"), (0.56, 0.05, "hold"), (0.68, 0)]), 0, "em"),
                opacity=curve([(0, 0, "hold"), (0.07, 100)]))], duration=0.6, tags=["tiron", "rapido"]),
    lp("gli-inestable", "Señal inestable", "Unstable signal", "glitch", "kinetic", G,
       [A([wiggle("character", "noise", hz="{speed}", phase=97)],
          position=pos(ref("amount"), ref("amount"), "px"), rotation=4, skew=10)],
       params=[amount(4, "px", 0, 20, 0.5), speed(20, 1, 30)], tags=["inestable", "temblor"], look="tech"),
    curve_out("gli-tv-off", "Apagar televisor", "TV switch-off", "glitch", "kinetic", ("FIN DE LA TRANSMISIÓN",
                                                                                       "END OF BROADCAST"),
              [A([everything("character")], scaleY=curve([(0, 100), (0.55, 6), (1, 0)]),
                 scaleX=curve([(0, 100), (0.55, 135), (0.8, 140), (1, 0)]),
                 fillColor="#ffffffff", opacity=curve([(0, 100), (0.85, 100), (1, 0)]))],
              duration=0.5, tags=["tv", "apagar", "salida"], look="tech"),
    curve_in("gli-tv-on", "Encender televisor", "TV switch-on", "glitch", "kinetic", ("EN EL AIRE", "ON AIR"),
             [A([everything("character")], scaleY=curve([(0, 0), (0.4, 6), (1, 100)]),
                scaleX=curve([(0, 0), (0.2, 140), (0.4, 135), (1, 100)]),
                opacity=curve([(0, 0), (0.15, 100)]))], duration=0.5, tags=["tv", "encender"], look="tech"),
    lp("gli-fallan", "Letras que fallan", "Glitching letters", "glitch", "light", G,
       [A([wiggle("character", "noise", hz="{speed}", phase=97, lo=-300, hi=100)], opacity=15)],
       params=[speed(8, 1, 25)], tags=["fallan", "parpadeo"], look="tech"),
    rv("gli-corte", "Corte rápido", "Quick cut", "glitch", "word", ("CORTE · CORTE · YA", "CUT · CUT · NOW"),
       {"position": pos(0.6, 0), "skew": -30}, unit="word", stagger=0.08, duration=0.16, ease="easeOut",
       order="random", fade=0.3, ease_spec=SNAP, tags=["corte", "rapido"]),
    rv("gli-estatica", "Estática", "Static", "glitch", "character", ("SINTONIZANDO", "TUNING IN"),
       {"scale": 145, "blur": 9}, stagger=0.012, duration=0.12, ease="linear", order="random", fade=0.2,
       tags=["estatica", "ruido"], look="tech"),
    lp("gli-error", "Error de sistema", "System error", "glitch", "kinetic", ("ERROR 404", "ERROR 404"),
       [A([mode(pulse_sel(spike(0.0, 0.08)), "add")], scale=112, skew=22, position=pos(0.06, 0)),
        A([pulse_sel(spike(0.45, 0.05))], skew=-18, position=pos(-0.1, 0), fillColor="#ffff2bd6")],
       period=2.0, tags=["error", "sistema"], look="tech"),
]

# --- slides and wipes ---------------------------------------------------------------------------
S = ("Desliza hacia aquí", "Slide over here")
ZIGZAG = mode(wiggle("word", "sine", hz=0, phase=180, tphase=90), "intersect")

SLIDE = [
    rv("des-izq-palabras", "Desde la izquierda por palabra", "From the left by word", "deslizar", "word", S,
       {"position": pos(-1.1, 0)}, unit="word", stagger=0.08, duration=0.5, ease="easeOut", fade=0.5,
       tags=["izquierda", "palabras"]),
    rv("des-der-letras", "Desde la derecha por letra", "From the right by letter", "deslizar", "character", S,
       {"position": pos(0.9, 0)}, stagger=0.025, duration=0.45, ease="easeOut", fade=0.5, tags=["derecha", "letras"]),
    rv("des-arriba-lineas", "Líneas desde arriba", "Lines from above", "deslizar", "word",
       ("Primero esto\ny luego aquello", "First this\nthen that"), {"position": pos(0, -0.8)}, unit="line",
       stagger=0.15, duration=0.5, ease="easeOut", fade=0.5, tags=["arriba", "lineas"]),
    rv("des-mascara", "Subir con máscara", "Masked rise", "deslizar", "character", ("Revelación", "Revelation"),
       {"position": pos(0, 0.7), "wipe": {"enabled": True, "angleDeg": -90, "softness": 0.15}}, stagger=0.03,
       duration=0.5, ease="easeOut", fade=None, tags=["mascara", "revelar"]),
    rv("des-cortina", "Cortina por palabra", "Curtain by word", "deslizar", "word", ("Abre el telón", "Raise the curtain"),
       {"wipe": {"enabled": True, "angleDeg": 0, "softness": 0.12}}, unit="word", stagger=0.12, duration=0.45,
       ease="easeInOut", fade=None, tags=["cortina", "barrido"]),
    rv("des-diagonal", "Barrido diagonal", "Diagonal wipe", "deslizar", "kinetic", ("NUEVA ERA", "NEW ERA"),
       {"wipe": {"enabled": True, "angleDeg": -45, "softness": 0.45}}, unit="block", duration=0.7, ease="easeInOut",
       fade=None, flags={"unitLocked": True, "orderLocked": True}, tags=["diagonal", "barrido"]),
    rv("des-centro", "Barrido desde el centro", "Wipe from the centre", "deslizar", "character", ("CENTRO", "CENTRE"),
       {"wipe": {"enabled": True, "angleDeg": -90, "softness": 0.2}}, stagger=0.04, duration=0.35, ease="easeOut",
       order="centerOut", fade=None, tags=["centro", "barrido"]),
    rv("des-empuje", "Empuje con desenfoque", "Motion-blur push", "deslizar", "kinetic", ("RÁPIDO", "FAST"),
       {"position": pos(0.55, 0, "box"), "blur": 14}, unit="block", duration=0.35, ease="easeOut", fade=0.3,
       ease_spec=SNAP, flags={"unitLocked": True, "orderLocked": True}, tags=["empuje", "velocidad"]),
    rv("des-zigzag", "Zigzag", "Zigzag", "deslizar", "word", ("izquierda derecha izquierda", "left right left"),
       {"position": pos(1.4, 0)}, unit="word", stagger=0.08, duration=0.5, ease="easeOut", fade=0.4,
       extra=[], tags=["zigzag", "alterno"]),
    rv("des-cascada", "Cascada diagonal", "Diagonal cascade", "deslizar", "character", ("Cascada", "Cascade"),
       {"position": pos(0.35, -0.6)}, stagger=0.03, duration=0.5, ease="back", fade=0.4, tags=["cascada", "diagonal"]),
    rv("des-expandir", "Expandir", "Expand", "deslizar", "character", ("RESPIRA", "BREATHE"),
       {"tracking": -0.22, "trackingUnit": "em", "scale": 90}, stagger=0.0, duration=0.7, ease="easeOut", fade=0.5,
       tags=["expandir", "espaciado"]),
    rv("des-tren", "Tren de letras", "Letter train", "deslizar", "character", ("Todos a bordo", "All aboard"),
       {"position": pos(2.2, 0)}, stagger=0.025, duration=0.6, ease="easeInOut", fade=0.3, order="backward",
       tags=["tren", "lateral"]),
    rv("des-sale-derecha", "Salir hacia la derecha", "Exit right", "deslizar", "word", ("Nos vemos", "See you"),
       {"position": pos(1.2, 0), "blur": 6}, unit="word", stagger=0.06, duration=0.4, ease="easeIn", fade=0.6,
       order="backward", slots=["out"], flags={"mirrorForOut": False}, tags=["salida", "derecha"]),
    rv("des-sale-arriba", "Salir hacia arriba", "Exit up", "deslizar", "word", ("Hasta pronto\nnos vemos", "Until soon\nsee you"),
       {"position": pos(0, -0.8), "blur": 10}, unit="line", stagger=0.12, duration=0.45, ease="easeIn", fade=0.6,
       slots=["out"], flags={"mirrorForOut": False}, tags=["salida", "arriba"]),
    rv("des-derrape", "Derrape", "Drift", "deslizar", "character", ("DERRAPE", "DRIFT"),
       {"position": pos(1.6, 0), "skew": -35}, stagger=0.015, duration=0.45, ease="easeOut", fade=0.4,
       tags=["derrape", "carreras"]),
    rv("des-persiana", "Persiana", "Blinds", "deslizar", "line", ("una línea\ndos líneas\ntres líneas", "one line\ntwo lines\nthree lines"),
       {"wipe": {"enabled": True, "angleDeg": 90, "softness": 0.06}}, unit="line", stagger=0.12, duration=0.4,
       ease="easeOut", fade=None, tags=["persiana", "lineas"]),
    rv("des-ascenso", "Ascenso cinematográfico", "Cinematic rise", "deslizar", "basic", ("UNA HISTORIA REAL", "A TRUE STORY"),
       {"position": pos(0, 0.35, "box"), "blur": 8}, unit="block", duration=1.1, ease="smooth", fade=0.7,
       flags={"unitLocked": True, "orderLocked": True}, tags=["cine", "suave"]),
    rv("des-palabras-linea", "Palabras desde la línea", "Words from the baseline", "deslizar", "word",
       ("Cada palabra sube", "Every word rises"),
       {"position": pos(0, 0.85), "wipe": {"enabled": True, "angleDeg": -90, "softness": 0.1}}, unit="word",
       stagger=0.1, duration=0.5, ease="easeOut", fade=None, tags=["mascara", "palabras"]),
    rv("des-carrusel", "Carrusel", "Carousel", "deslizar", "word", ("Siguiente diapositiva", "Next slide"),
       {"position": pos(0.9, 0), "scaleX": 40}, unit="word", stagger=0.07, duration=0.5, ease="easeOut", fade=0.4,
       tags=["carrusel", "perspectiva"]),
    lp("des-teletipo", "Teletipo", "News ticker", "deslizar", "kinetic", ("ÚLTIMAS NOTICIAS · EN VIVO ·", "LATEST NEWS · LIVE ·"),
       [A([], position=pos(curve([(0, 0.55), (1, -0.55)]), 0, "box"))], period=6.0, tags=["teletipo", "noticias", "ticker"]),
]
# Zigzag: alternate words come from opposite sides (the wiggle at 0 Hz is a fixed ±1 per word).
SLIDE[8].animators[0]["selectors"] = ["stagger", ZIGZAG]

ANIMS = TYPE + KARAOKE + BOUNCE + NEON + GLITCH + SLIDE
