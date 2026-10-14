"""Fill in the Spanish for the strings the Video tab added.

lupdate leaves new entries as type="unfinished" with empty translations. This maps each new
English source to its Spanish and rewrites the entry as finished, then reports any that are still
unfinished so nothing silently ships in English.
"""

import re
import sys

PATH = r"C:\Users\bajoe\Downloads\FlipStudio\codigo\Flip\i18n\drift_es.ts"

TRANSLATIONS = {
    "Video": "Video",
    "Basic": "Básico",
    "Remove background": "Eliminar fondo",
    "Mask": "Máscara",
    "Retouch": "Retoque",
    "Automatic removal": "Eliminación automática",
    "Cut out people…": "Recortar personas…",
    "Finds the people in the clip and removes the background":
        "Encuentra las personas del clip y quita el fondo",
    "Select a video clip first": "Selecciona primero un clip de video",
    "Select a video clip to remove its background.":
        "Selecciona un clip de video para quitarle el fondo.",
    "Custom removal": "Eliminación personalizada",
    "Cut out a subject…": "Recortar un sujeto…",
    "Mark with a click what you want to keep and it follows it":
        "Marca con un clic lo que quieres conservar y lo sigue",
    "Chroma key": "Chroma key",
    "Remove a colour": "Quitar un color",
    "Adds Chroma Key, with the colour and tolerance to tune in Effects":
        "Agrega Chroma Key; el color y la tolerancia se ajustan en Efectos",
    "Image or video as mask…": "Imagen o video como máscara…",
    "Use a file&apos;s own pixels as the coverage map":
        "Usa los píxeles de un archivo como mapa de cobertura",
    "Choose a mask image or video": "Elige una imagen o un video para la máscara",
    "Media files (*.png *.jpg *.jpeg *.webp *.heic *.heif *.avif *.tif *.tiff *.bmp *.gif *.mp4 *.mov *.mkv *.webm)":
        "Archivos de imagen y video (*.png *.jpg *.jpeg *.webp *.heic *.heif *.avif *.tif *.tiff *.bmp *.gif *.mp4 *.mov *.mkv *.webm)",
    "All files (*)": "Todos los archivos (*)",
    "Add mask": "Agregar máscara",
    "Skin retouch": "Retoque de piel",
    "Smooth, whiten, tone, slim the face, bigger eyes, lipstick and blush":
        "Suavizar, blanquear, tono, adelgazar el rostro, ojos grandes, labial y rubor",
    "Body reshape": "Reformar el cuerpo",
    "Slim or widen what the mesh follows": "Adelgaza o ensancha lo que sigue la malla",
    "Bigger eyes": "Ojos más grandes",
    "Enlarges the eyes the mesh found": "Agranda los ojos que encontró la malla",
    "Whiten teeth": "Blanquear dientes",
    "Needs the lip contour from a face scan": "Necesita el contorno de los labios de un escaneo",
    "Eyeliner": "Delineador",
    "Draws along the eyelid contour": "Dibuja sobre el contorno del párpado",
    "Eyeshadow": "Sombra de ojos",
    "Colours the eyelid": "Colorea el párpado",
    "Brow tint": "Tinte de cejas",
    "Colours the eyebrows": "Colorea las cejas",
    "Eye colour": "Color de ojos",
    "Recolours the iris": "Recolorea el iris",
    "Face, body and hair retouching: skin, makeup and the fun face effects. Add what you want, then scan the clip&apos;s faces so the effect has something to follow.":
        "Retoque de rostro, cuerpo y cabello: piel, maquillaje y los efectos divertidos de cara. "
        "Agrega lo que quieras y después escanea las caras del clip para que el efecto tenga qué seguir.",
    "Select a video clip to retouch a face.": "Selecciona un clip de video para retocar una cara.",
    "Install Face retouch from Extras (it needs the AI engine) to use these.":
        "Instala Retoque de rostro desde Extras (necesita el motor de IA) para usar esto.",
    "What the clip already carries": "Lo que el clip ya lleva",
}


def main():
    with open(PATH, encoding="utf-8") as fh:
        text = fh.read()

    applied = 0
    missed = []
    for source, spanish in TRANSLATIONS.items():
        # Match this source with an unfinished, empty translation.
        pattern = re.compile(
            r"(?s)(<source>" + re.escape(source) + r"</source>\s*)"
            r"<translation type=\"unfinished\"></translation>")
        replacement = r"\1<translation>" + spanish.replace("\\", r"\\") + "</translation>"
        text, n = pattern.subn(replacement, text, count=1)
        if n:
            applied += 1
        else:
            missed.append(source)

    with open(PATH, "w", encoding="utf-8") as fh:
        fh.write(text)

    print(f"traducidos {applied} de {len(TRANSLATIONS)}")
    if missed:
        print("no encontrados (revisar):")
        for m in missed:
            print("  -", m[:70])

    # Anything still unfinished with no text is a string the user would read in English.
    left = re.findall(r"(?s)<source>(.*?)</source>\s*<translation type=\"unfinished\"></translation>",
                      text)
    print(f"quedan sin traducir: {len(left)}")
    for s in left[:15]:
        print("   *", s[:70])
    return 0


if __name__ == "__main__":
    sys.exit(main())
