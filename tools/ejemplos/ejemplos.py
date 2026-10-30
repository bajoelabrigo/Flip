"""Builds ejemplos.json (the home screen's examples) from the .flip files present here."""
import hashlib, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
EXAMPLES = [
    {"id": "accion", "file": "ejemplo-1.flip", "thumb": "ejemplo-1.jpg", "format": "9:16",
     "title": {"es": "Reel de acción", "en": "Action reel"},
     "teaches": {"es": "Cortes rápidos, transiciones, música y un título que golpea.",
                 "en": "Quick cuts, transitions, music and a title that hits."},
     "steps": {"es": ["Haz clic en un clip de la línea de tiempo para cambiarlo a la derecha.",
                      "Mueve el cabezal y pulsa S para dividir un clip.",
                      "Pulsa Exportar (arriba a la derecha) para guardar tu video."],
               "en": ["Click a clip on the timeline to change it on the right.",
                      "Move the playhead and press S to split a clip.",
                      "Press Export (top right) to save your video."]}},
    {"id": "viaje", "file": "ejemplo-2.flip", "thumb": "ejemplo-2.jpg", "format": "16:9",
     "title": {"es": "Vlog de viaje", "en": "Travel vlog"},
     "teaches": {"es": "Tercio inferior con el lugar, filtro de cine, cámara lenta y música con fundidos.",
                 "en": "A lower third with the place, a film look, slow motion and music that fades."},
     "steps": {"es": ["Haz doble clic en el texto del lugar y escribe el tuyo.",
                      "Elige un clip y prueba otro look en Filtros.",
                      "En el clip lento, abre Velocidad y cambia cuánto se frena."],
               "en": ["Double-click the place's text and type your own.",
                      "Pick a clip and try another look in Filters.",
                      "On the slow clip, open Speed and change how slow it goes."]}},
    {"id": "voz", "file": "ejemplo-3.flip", "thumb": "ejemplo-3.jpg", "format": "9:16",
     "title": {"es": "Voz y subtítulos", "en": "Voice and captions"},
     "teaches": {"es": "Narración con voz de IA y subtítulos palabra por palabra, como en TikTok.",
                 "en": "An AI voice-over with word-by-word captions, as on TikTok."},
     "steps": {"es": ["Haz clic en los subtítulos para cambiar su estilo a la derecha.",
                      "Corrige una palabra escribiendo sobre ella en el panel de subtítulos.",
                      "Prueba Herramientas › Texto a voz para grabar tu propia narración."],
               "en": ["Click the captions to change their style on the right.",
                      "Fix a word by typing over it in the captions panel.",
                      "Try Tools › Text to speech to record your own voice-over."]}},
    {"id": "fotos", "file": "ejemplo-4.flip", "thumb": "ejemplo-4.jpg", "format": "9:16",
     "title": {"es": "Fotos con música", "en": "Photos with music"},
     "teaches": {"es": "Fotos que se mueven solas, stickers y cortes al ritmo de la canción.",
                 "en": "Photos that move by themselves, stickers and cuts on the beat."},
     "steps": {"es": ["Arrastra tus fotos desde Medios encima de las del ejemplo para cambiarlas.",
                      "Abre Stickers y suelta uno sobre una foto.",
                      "Elige la música y prueba Audio › Volumen igual que en redes."],
               "en": ["Drag your photos from Media onto the example's to replace them.",
                      "Open Stickers and drop one onto a photo.",
                      "Pick the music and try Audio › Same volume as social media."]}},
    {"id": "anuncio", "file": "ejemplo-5.flip", "thumb": "ejemplo-5.jpg", "format": "9:16",
     "title": {"es": "Anuncio de producto", "en": "Product ad"},
     "teaches": {"es": "Texto animado con precio y oferta, formas de color y un llamado a la acción.",
                 "en": "Animated text with a price and an offer, colour shapes and a call to action."},
     "steps": {"es": ["Haz doble clic en el precio y pon el tuyo.",
                      "Elige una forma y cámbiale el color a la derecha.",
                      "En Títulos › Animación, prueba otra entrada para el texto."],
               "en": ["Double-click the price and put yours.",
                      "Pick a shape and change its colour on the right.",
                      "In Titles › Animation, try another entrance for the text."]}},
    {"id": "intro", "file": "ejemplo-6.flip", "thumb": "ejemplo-6.jpg", "format": "16:9",
     "title": {"es": "Intro para YouTube", "en": "YouTube intro"},
     "teaches": {"es": "Un logo que aparece, texto en movimiento y un golpe de sonido.",
                 "en": "A logo that appears, moving text and a sound hit."},
     "steps": {"es": ["Cambia el nombre del canal haciendo doble clic en el texto.",
                      "Pon tu logo arrastrándolo desde Medios sobre el del ejemplo.",
                      "Pasa a Pro (arriba) y abre las filas de claves para ver cómo se anima."],
               "en": ["Change the channel's name by double-clicking the text.",
                      "Put your logo in by dragging it from Media onto the example's.",
                      "Switch to Pro (top) and open the key rows to see how it moves."]}},
]
out = []
for e in EXAMPLES:
    path = os.path.join(HERE, e["file"])
    if not os.path.exists(path):
        continue
    entry = dict(e)
    entry["sha256"] = hashlib.sha256(open(path, "rb").read()).hexdigest()
    entry["size"] = os.path.getsize(path)
    out.append(entry)
json.dump({"version": 1, "examples": out}, open(os.path.join(HERE, "ejemplos.json"), "w", encoding="utf-8", newline=""),
          ensure_ascii=False, indent=1)
print([(e["id"], e["size"]) for e in out])
