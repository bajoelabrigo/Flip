"""Kit de YouTube, batch d (see docs/plan-kit-youtube.md and BRIEF-ytkit.md): lower thirds (`tercios`, order
7500-7549) and info bars (`barras-info`, order 7800-7849). Every piece sits over a «Tu video» slot that is its own
bottom track, so the user deletes it and lays the overlay on their footage. Texts that come out of a line or a plate
are wiped out of it (angle 0, or 180 when right-aligned) and wiped back into it on the way out.
"""

from __future__ import annotations

from kit import (Box, blink, centered, circle_photo, fill, gradient, keys, label, line, no_stroke, photo_bg, pill,
                 pop, rrect, shade_bottom, shade_top, shadow, tall, tanim, wide)

NAVY = "#0B1A2E"
DEEP = "#06101F"
TEAL = "#2EE6C8"
CORAL = "#FF5D73"
SUN = "#FFD23F"
WHITE = "#FFFFFF"
MIST = "#A9B8CC"
LIGHT = "#F4F7FB"


def _kit(id, es, en, section, duration, order, tags, **kw):
    return wide(f"ytk-{id}", es, en, "ytkit", duration, order=order, tags=[f"kit:{section}", "youtube"] + tags, **kw)


def _kit_tall(id, es, en, section, duration, order, tags, **kw):
    return tall(f"ytk-{id}", es, en, "ytkit", duration, order=order,
                tags=[f"kit:{section}", "youtube", "vertical"] + tags, **kw)


# --- helpers -------------------------------------------------------------------------------------

def win(angle=0, duration=0.6):
    """Text born from the line/plate on its left (angle 0) or right (180)."""
    return tanim("wipe", duration=duration, angle=angle, softness=0.15)


def wout(angle=0, duration=0.35):
    """Text that goes back into its line. Same angle as the entrance: the slot's angle is shared, and the
    front simply runs back (a different angle would also flip the entrance)."""
    return tanim("wipe", duration=duration, angle=angle, softness=0.15)


def fout(duration=0.25):
    return tanim("fade", duration=duration)


_COLLAPSE = {
    "left": lambda b: {"sx": 0.0, "dx": -b.w / 2},
    "right": lambda b: {"sx": 0.0, "dx": b.w / 2},
    "bottom": lambda b: {"sy": 0.0, "dy": b.h / 2},
    "top": lambda b: {"sy": 0.0, "dy": -b.h / 2},
    "center": lambda b: {"sx": 0.0},
    "scale": lambda b: {"s": 0.0},
}


def grow(box, side, dur, length=0.45, out=0.35, ease="out"):
    """A plate anchored on `side` that grows out of it and retracts into it in the last `out` seconds."""
    z = _COLLAPSE[side](box)
    m = [(0, z, ease), (length, {}, "hold")]
    if out:
        m += [(dur - out, {}, "in"), (dur, z)]
    return m


def popout(dur, length=0.4, out=0.3):
    return [(0, {"s": 0.0}, "back"), (length, {}, "hold"), (dur - out, {}, "in"), (dur, {"s": 0.0})]


def fades(dur, fin=0.25, fout_=0.3):
    return keys([(0, 0.0, "smooth"), (fin, 1.0, "hold"), (dur - fout_, 1.0, "smooth"), (dur, 0.0)])


def plate(t, name, colour, t0, dur, box, side="left", radius=0, length=0.45, out=0.35, alpha=1.0, layers=None,
          **extra):
    return rrect(t, t.track("shape", name), colour, t0, dur, box, radius=radius,
                 motion=grow(box, side, dur, length, out), alpha=alpha, layers=layers, **extra)


# =================================================================================================
# Tercios inferiores
# =================================================================================================

def tercio_pildora():
    t = _kit("tercio-pildora", "Tercio inferior píldora", "Pill lower third", "tercios", 5.0, 7500,
             ["nombre", "rótulo", "tercio inferior", "píldora"], thumb_at=2.4)
    photo_bg(t, "h-portrait-04", s1=1.05, label="Tu video")
    shade_bottom(t, 380, 0.45)
    plate(t, "Placa", WHITE, 0.45, 3.95, Box(170, 800, 660, 90), radius=45,
          layers=[shadow("#000000", 0, 10, 28, 0.35), fill(WHITE), no_stroke()])
    plate(t, "Placa", NAVY, 0.7, 3.55, Box(230, 900, 380, 52), radius=26)
    t.solid(t.track("shape", "Círculo"), TEAL, 0.3, 4.3, centered(170, 845, 104, 104), popout(4.3), kind="ellipse",
            layers=[shadow("#000000", 0, 8, 20, 0.3), fill(TEAL), no_stroke()])
    t.solid(t.track("shape", "Icono"), NAVY, 0.45, 4.1, centered(176, 845, 34, 36), popout(4.1),
            kind="triangle", rotation=keys([(0, 90)]))
    label(t, t.track("text", "Nombre"), "Nombre Apellido", 0.75, 3.4, Box(240, 800, 560, 90), "Sora", 46, NAVY,
          weight=800, align="left", anim_in=win(), anim_out=wout(), name="Nombre")
    label(t, t.track("text", "Cargo"), "Cargo o tema", 0.95, 3.0, Box(254, 900, 340, 52), "Inter", 26, TEAL,
          weight=700, align="left", spacing=2, anim_in=win(), anim_out=wout(), name="Cargo")
    return t


def tercio_corchete():
    t = _kit("tercio-corchete", "Tercio inferior corchete", "Bracket lower third", "tercios", 5.0, 7501,
             ["nombre", "rótulo", "tercio inferior", "corchete"], thumb_at=2.4)
    photo_bg(t, "h-man-01", s1=1.05, label="Tu video")
    shade_bottom(t, 420, 0.7)
    sh = [shadow("#000000", 0, 4, 14, 0.5), fill(WHITE)]
    plate(t, "Corchete", TEAL, 0.3, 4.3, Box(120, 790, 10, 170), side="top", length=0.35)
    plate(t, "Corchete", TEAL, 0.5, 3.9, Box(120, 790, 46, 10), length=0.3, out=0.3)
    plate(t, "Corchete", TEAL, 0.55, 3.85, Box(120, 950, 46, 10), length=0.3, out=0.3)
    label(t, t.track("text", "Nombre"), "NOMBRE APELLIDO", 0.7, 3.4, Box(168, 806, 1000, 84), "Montserrat", 64, WHITE,
          weight=900, align="left", spacing=1, layers=sh, anim_in=win(), anim_out=wout(), name="Nombre")
    label(t, t.track("text", "Cargo"), "DIRECTOR CREATIVO", 0.95, 3.0, Box(172, 892, 900, 46), "Inter", 28, TEAL,
          weight=700, align="left", spacing=8, anim_in=win(), anim_out=wout(), name="Cargo")
    return t


def tercio_minimal():
    t = _kit("tercio-minimal", "Tercio inferior minimalista", "Minimal line lower third", "tercios", 5.0, 7502,
             ["nombre", "rótulo", "tercio inferior", "minimalista", "línea"], thumb_at=2.4)
    photo_bg(t, "h-portrait-02", s1=1.05, label="Tu video")
    shade_bottom(t, 420, 0.6)
    plate(t, "Línea", WHITE, 0.3, 4.3, Box(120, 884, 560, 3), length=0.6, out=0.4)
    plate(t, "Acento", TEAL, 0.45, 4.05, Box(120, 882, 70, 7), length=0.4, out=0.3)
    label(t, t.track("text", "Nombre"), "Nombre Apellido", 0.6, 3.6, Box(118, 800, 1000, 80), "Sora", 58, WHITE,
          weight=700, align="left", valign="bottom",
          anim_in=tanim("wipe", duration=0.6, angle=-90, softness=0.1),
          anim_out=tanim("wipe", duration=0.35, angle=-90, softness=0.1), name="Nombre")
    label(t, t.track("text", "Cargo"), "Fotógrafa y viajera", 0.75, 3.35, Box(120, 896, 1000, 50), "Inter", 30, MIST,
          weight=500, align="left", valign="top", spacing=2,
          anim_in=tanim("wipe", duration=0.6, angle=90, softness=0.1),
          anim_out=tanim("wipe", duration=0.35, angle=90, softness=0.1), name="Cargo")
    return t


def tercio_avatar():
    t = _kit("tercio-avatar", "Tercio inferior con foto", "Avatar lower third", "tercios", 5.0, 7503,
             ["nombre", "rótulo", "tercio inferior", "foto", "perfil"], thumb_at=2.4)
    photo_bg(t, "h-man-04", s1=1.05, label="Tu video")
    shade_bottom(t, 380, 0.45)
    plate(t, "Placa", NAVY, 0.55, 3.75, Box(200, 805, 660, 120), radius=60, alpha=0.95)
    line(t, t.track("shape", "Línea"), TEAL, 0.9, 3.2, Box(306, 868, 120, 4), length=0.4,
         opacity=keys([(0, 1.0, "hold"), (2.9, 1.0, "smooth"), (3.2, 0.0)]))
    circle_photo(t, "h-portrait-05", 0.3, 4.3, centered(200, 865, 150, 150), popout(4.3, 0.45),
                 ring_colour=TEAL, ring_width=7, label="Tu foto")
    label(t, t.track("text", "Nombre"), "Nombre Apellido", 0.8, 3.3, Box(306, 806, 520, 60), "Sora", 42, WHITE,
          weight=800, align="left", valign="bottom", anim_in=win(), anim_out=wout(), name="Nombre")
    label(t, t.track("text", "Cargo"), "@tuusuario", 1.0, 2.95, Box(306, 878, 520, 40), "Inter", 26, MIST,
          weight=600, align="left", valign="top", spacing=1, anim_in=win(), anim_out=wout(), name="Usuario")
    return t


def tercio_derecha():
    t = _kit("tercio-derecha", "Tercio inferior a la derecha", "Right-aligned lower third", "tercios", 5.0, 7504,
             ["nombre", "rótulo", "tercio inferior", "derecha"], thumb_at=2.4)
    photo_bg(t, "h-portrait-06", s1=1.05, label="Tu video")
    line(t, t.track("shape", "Acento"), CORAL, 0.3, 4.4, Box(1788, 790, 12, 150), grow="y", length=0.3,
         opacity=keys([(0, 1.0, "hold"), (4.1, 1.0, "smooth"), (4.4, 0.0)]))
    plate(t, "Placa", WHITE, 0.45, 3.75, Box(1168, 790, 620, 90), side="right")
    plate(t, "Placa", NAVY, 0.6, 3.4, Box(1308, 880, 480, 60), side="right")
    label(t, t.track("text", "Nombre"), "Nombre Apellido", 0.75, 3.15, Box(1160, 790, 600, 90), "Sora", 54, NAVY,
          weight=800, align="right", anim_in=win(180), anim_out=wout(180), name="Nombre")
    label(t, t.track("text", "Cargo"), "Cargo o tema", 0.9, 2.8, Box(1300, 880, 460, 60), "Inter", 32, CORAL,
          weight=600, align="right", spacing=2, anim_in=win(180), anim_out=wout(180), name="Cargo")
    return t


def tercio_entrevista():
    t = _kit("tercio-entrevista", "Tercio inferior entrevista", "Two-person lower thirds", "tercios", 5.0, 7505,
             ["nombre", "rótulo", "tercio inferior", "entrevista", "podcast", "dos personas"], thumb_at=2.6)
    photo_bg(t, "h-podcast-03", s1=1.04, label="Tu video")
    shade_bottom(t, 360, 0.5)
    # Left guest
    line(t, t.track("shape", "Acento"), TEAL, 0.3, 4.3, Box(100, 850, 10, 130), grow="y", length=0.3,
         opacity=keys([(0, 1.0, "hold"), (4.0, 1.0, "smooth"), (4.3, 0.0)]))
    plate(t, "Placa", NAVY, 0.42, 3.7, Box(110, 850, 520, 76))
    plate(t, "Placa", TEAL, 0.55, 3.4, Box(110, 926, 360, 54))
    label(t, t.track("text", "Nombre 1"), "Nombre Apellido", 0.65, 3.2, Box(134, 850, 480, 76), "Sora", 40, WHITE,
          weight=800, align="left", anim_in=win(), anim_out=wout(), name="Nombre 1")
    label(t, t.track("text", "Cargo 1"), "Presentadora", 0.8, 2.9, Box(134, 926, 330, 54), "Inter", 26, NAVY,
          weight=700, align="left", spacing=2, anim_in=win(), anim_out=wout(), name="Cargo 1")
    # Right guest, a beat later
    d = 0.4
    line(t, t.track("shape", "Acento"), CORAL, 0.3 + d, 4.0, Box(1810, 850, 10, 130), grow="y", length=0.3,
         opacity=keys([(0, 1.0, "hold"), (3.7, 1.0, "smooth"), (4.0, 0.0)]))
    plate(t, "Placa", NAVY, 0.42 + d, 3.4, Box(1290, 850, 520, 76), side="right")
    plate(t, "Placa", CORAL, 0.55 + d, 3.1, Box(1450, 926, 360, 54), side="right")
    label(t, t.track("text", "Nombre 2"), "Nombre Apellido", 0.65 + d, 2.9, Box(1306, 850, 480, 76), "Sora", 40,
          WHITE, weight=800, align="right", anim_in=win(180), anim_out=wout(180), name="Nombre 2")
    label(t, t.track("text", "Cargo 2"), "Invitada", 0.8 + d, 2.6, Box(1456, 926, 330, 54), "Inter", 26, WHITE,
          weight=700, align="right", spacing=2, anim_in=win(180), anim_out=wout(180), name="Cargo 2")
    return t


def tercio_ubicacion():
    t = _kit("tercio-ubicacion", "Tercio inferior de lugar", "Location lower third", "tercios", 5.0, 7506,
             ["lugar", "ubicación", "viaje", "tercio inferior", "mapa"], thumb_at=2.4)
    photo_bg(t, "h-nature-01", s1=1.06, label="Tu video")
    shade_bottom(t, 420, 0.65)
    # Map pin: a drop (circle + point) with a hole; it falls in and lifts away.
    drop = lambda dur: [(0, {"dy": -90}, "back"), (0.5, {}, "hold"), (dur - 0.35, {}, "in"), (dur, {"dy": -90})]
    pin_op = lambda dur: keys([(0, 0.0, "smooth"), (0.2, 1.0, "hold"), (dur - 0.25, 1.0, "smooth"), (dur, 0.0)])
    t.solid(t.track("shape", "Pin"), CORAL, 0.3, 4.3, centered(160, 888, 46, 40), drop(4.3), kind="triangle",
            rotation=keys([(0, 180)]), opacity=pin_op(4.3))
    t.solid(t.track("shape", "Pin"), CORAL, 0.3, 4.3, centered(160, 850, 80, 80), drop(4.3), kind="ellipse",
            layers=[shadow("#000000", 0, 6, 16, 0.35), fill(CORAL), no_stroke()], opacity=pin_op(4.3))
    t.solid(t.track("shape", "Pin"), WHITE, 0.3, 4.3, centered(160, 850, 30, 30), drop(4.3), kind="ellipse",
            opacity=pin_op(4.3))
    plate(t, "Línea", TEAL, 0.7, 3.6, Box(224, 878, 520, 4), length=0.5, out=0.35)
    label(t, t.track("text", "Lugar"), "Lago de montaña", 0.8, 3.3, Box(222, 798, 1000, 78), "Sora", 58, WHITE,
          weight=800, align="left", valign="bottom",
          anim_in=tanim("wipe", duration=0.6, angle=-90, softness=0.1),
          anim_out=tanim("wipe", duration=0.35, angle=-90, softness=0.1), name="Lugar")
    label(t, t.track("text", "Región"), "REGIÓN · PAÍS", 0.95, 3.05, Box(224, 892, 900, 44), "Inter", 28, WHITE,
          weight=700, align="left", valign="top", spacing=6,
          anim_in=tanim("wipe", duration=0.6, angle=90, softness=0.1),
          anim_out=tanim("wipe", duration=0.35, angle=90, softness=0.1), name="Región y país")
    label(t, t.track("text", "Coordenadas"), "46.69° N · 12.08° E", 1.2, 2.7, Box(224, 940, 900, 36), "Inter", 22,
          MIST, weight=500, align="left", spacing=3, anim_in=tanim("fade", duration=0.5), anim_out=fout(),
          name="Coordenadas")
    return t


def tercio_claro():
    t = _kit("tercio-claro", "Tercio inferior claro", "Light lower third", "tercios", 5.0, 7507,
             ["nombre", "rótulo", "tercio inferior", "claro", "blanco"], thumb_at=2.4)
    photo_bg(t, "h-man-02", s1=1.05, label="Tu video")
    plate(t, "Placa", LIGHT, 0.35, 3.95, Box(120, 800, 640, 140), radius=14,
          layers=[shadow("#000000", 0, 12, 34, 0.3), fill(LIGHT), no_stroke()])
    plate(t, "Acento", CORAL, 0.6, 3.5, Box(146, 826, 7, 88), side="top", length=0.35, out=0.3, radius=3)
    label(t, t.track("text", "Nombre"), "Nombre Apellido", 0.75, 3.2, Box(176, 812, 560, 66), "Sora", 48, NAVY,
          weight=800, align="left", valign="bottom", anim_in=win(), anim_out=wout(), name="Nombre")
    label(t, t.track("text", "Cargo"), "Maestro artesano", 0.9, 2.95, Box(178, 878, 560, 44), "Inter", 28, CORAL,
          weight=600, align="left", valign="top", spacing=1, anim_in=win(), anim_out=wout(), name="Cargo")
    return t


def tercio_vidrio():
    t = _kit("tercio-vidrio", "Tercio inferior de vidrio", "Glass lower third", "tercios", 5.0, 7508,
             ["nombre", "rótulo", "tercio inferior", "vidrio", "translúcido", "elegante"], thumb_at=2.4)
    photo_bg(t, "h-portrait-03", s1=1.05, label="Tu video")
    glass = [shadow("#000000", 0, 14, 40, 0.35), fill(NAVY, 0.5),
             gradient([(0, WHITE, 0.16), (1, WHITE, 0.03)], angle=90, id="sheen"),
             {"id": "stroke", "kind": "stroke", "enabled": True, "width": 2, "strokeAlign": "inside",
              "paint": {"kind": "solid", "color": "#4dffffff"}, "opacity": 1.0}]
    t.solid(t.track("shape", "Placa"), NAVY, 0.3, 4.3, Box(120, 780, 680, 170),
            [(0, {"s": 0.94, "dx": -30}, "out"), (0.6, {}, "hold"), (3.9, {}, "in"), (4.3, {"s": 0.96, "dx": -20})],
            kind="rounded-rectangle", radius=22, layers=glass, opacity=fades(4.3, 0.35, 0.4))
    t.solid(t.track("shape", "Punto"), TEAL, 0.6, 3.7, centered(166, 815, 14, 14), popout(3.7, 0.3, 0.25),
            kind="ellipse")
    label(t, t.track("text", "Antetítulo"), "INVITADA", 0.65, 3.6, Box(184, 798, 500, 34), "Inter", 22, TEAL,
          weight=800, align="left", spacing=6, anim_in=tanim("fade", duration=0.4), anim_out=fout(),
          name="Antetítulo")
    label(t, t.track("text", "Nombre"), "Nombre Apellido", 0.75, 3.45, Box(156, 832, 620, 66), "Sora", 50, WHITE,
          weight=700, align="left", anim_in=tanim("rise", duration=0.5), anim_out=fout(0.3), name="Nombre")
    label(t, t.track("text", "Cargo"), "Diseñadora de producto", 0.9, 3.25, Box(158, 898, 620, 40), "Inter", 28, MIST,
          weight=500, align="left", spacing=1, anim_in=tanim("fade", duration=0.5), anim_out=fout(0.3),
          name="Cargo")
    return t


def tercio_paso():
    t = _kit("tercio-paso", "Tercio inferior de paso", "Numbered step lower third", "tercios", 5.0, 7509,
             ["paso", "tutorial", "receta", "número", "tercio inferior"], thumb_at=2.4)
    photo_bg(t, "h-cooking-01", s1=1.05, label="Tu video")
    shade_bottom(t, 380, 0.5)
    plate(t, "Placa", NAVY, 0.5, 3.8, Box(270, 790, 660, 96))
    plate(t, "Placa", TEAL, 0.65, 3.45, Box(270, 886, 420, 54))
    t.solid(t.track("shape", "Número"), SUN, 0.3, 4.3, Box(120, 790, 150, 150), popout(4.3),
            layers=[shadow("#000000", 0, 8, 22, 0.3), fill(SUN), no_stroke()])
    label(t, t.track("text", "Número"), "01", 0.45, 4.0, Box(120, 790, 150, 150), "Anton", 96, NAVY, weight=400,
          anim_in=tanim("pop", duration=0.4), anim_out=fout(0.2), name="Número")
    label(t, t.track("text", "Paso"), "Prepara los ingredientes", 0.8, 3.3, Box(300, 790, 610, 96), "Sora", 40, WHITE,
          weight=700, align="left", anim_in=win(), anim_out=wout(), name="Paso")
    label(t, t.track("text", "Detalle"), "PASO 1 DE 5", 0.95, 3.0, Box(300, 886, 380, 54), "Inter", 26, NAVY,
          weight=800, align="left", spacing=4, anim_in=win(), anim_out=wout(), name="Detalle")
    return t


def tercio_diagonal():
    t = _kit("tercio-diagonal", "Tercio inferior diagonal", "Slanted lower third", "tercios", 5.0, 7510,
             ["nombre", "rótulo", "tercio inferior", "deporte", "energía"], thumb_at=2.4)
    photo_bg(t, "h-portrait-05", s1=1.05, label="Tu video")
    shade_bottom(t, 360, 0.45)
    t.solid(t.track("shape", "Placa"), CORAL, 0.35, 3.95, Box(96, 800, 700, 100),
            grow(Box(96, 800, 700, 100), "left", 3.95), kind="parallelogram")
    t.solid(t.track("shape", "Placa"), NAVY, 0.55, 3.55, Box(140, 900, 470, 58),
            grow(Box(140, 900, 470, 58), "left", 3.55), kind="parallelogram")
    for i in range(3):
        t.solid(t.track("shape", "Barras"), SUN, 0.8 + i * 0.07, 3.0 - i * 0.07, Box(820 + i * 34, 806, 14, 88),
                [(0, {"dy": -50, "sy": 0.0}, "out"), (0.35, {}, "hold"), (2.7 - i * 0.07, {}, "in"),
                 (3.0 - i * 0.07, {"dy": 50, "sy": 0.0})], rotation=keys([(0, 20)]))
    label(t, t.track("text", "Nombre"), "NOMBRE APELLIDO", 0.75, 3.15, Box(150, 800, 600, 100), "Oswald", 62, WHITE,
          weight=700, align="left", spacing=2, anim_in=win(), anim_out=wout(), name="Nombre")
    label(t, t.track("text", "Cargo"), "CAPITANA DEL EQUIPO", 0.9, 2.85, Box(180, 900, 420, 58), "Barlow Condensed",
          32, WHITE, weight=700, align="left", spacing=4, anim_in=win(), anim_out=wout(), name="Cargo")
    return t


def tercio_etiqueta():
    t = _kit("tercio-etiqueta", "Tercio inferior con etiqueta", "Tagged lower third", "tercios", 5.0, 7511,
             ["nombre", "rótulo", "tercio inferior", "invitado", "etiqueta"], thumb_at=2.4)
    photo_bg(t, "h-portrait-01", s1=1.05, label="Tu video")
    shade_bottom(t, 460, 0.7)
    pill(t, t.track("shape", "Etiqueta"), SUN, 0.3, 4.1, Box(120, 716, 196, 46), popout(4.1, 0.4, 0.25))
    label(t, t.track("text", "Etiqueta"), "INVITADA", 0.4, 3.95, Box(120, 716, 196, 46), "Inter", 24, NAVY,
          weight=800, spacing=4, anim_in=tanim("fade", duration=0.3), anim_out=fout(0.2), name="Etiqueta")
    plate(t, "Subrayado", TEAL, 0.5, 3.9, Box(124, 902, 460, 8), length=0.5, out=0.35, radius=4)
    label(t, t.track("text", "Nombre"), "NOMBRE APELLIDO", 0.65, 3.45, Box(118, 770, 1100, 130), "Anton", 88, WHITE,
          weight=400, align="left", valign="bottom", spacing=2,
          anim_in=tanim("wipe", duration=0.6, angle=-90, softness=0.1),
          anim_out=tanim("wipe", duration=0.35, angle=-90, softness=0.1), name="Nombre")
    label(t, t.track("text", "Cargo"), "Escritora · Autora de «Tu libro»", 0.85, 3.15, Box(124, 920, 1000, 46),
          "Inter", 30, WHITE, weight=500, align="left", valign="top", spacing=1,
          anim_in=tanim("wipe", duration=0.6, angle=90, softness=0.1),
          anim_out=tanim("wipe", duration=0.35, angle=90, softness=0.1), name="Cargo")
    return t


# Vertical (Shorts): lower-middle, above the app's own buttons and captions; clear of the right-hand icons.

def tercio_doble_vertical():
    t = _kit_tall("tercio-doble-vertical", "Tercio inferior doble vertical", "Two-line lower third (vertical)",
                  "tercios", 5.0, 7520, ["nombre", "rótulo", "tercio inferior", "shorts"], thumb_at=2.4)
    photo_bg(t, "creator-02", s1=1.05, label="Tu video")
    line(t, t.track("shape", "Acento"), TEAL, 0.3, 4.4, Box(80, 1180, 12, 170), grow="y", length=0.3,
         opacity=keys([(0, 1.0, "hold"), (4.1, 1.0, "smooth"), (4.4, 0.0)]))
    plate(t, "Placa", WHITE, 0.45, 3.75, Box(92, 1180, 640, 100))
    plate(t, "Placa", NAVY, 0.6, 3.4, Box(92, 1280, 480, 70))
    label(t, t.track("text", "Nombre"), "Nombre Apellido", 0.75, 3.15, Box(122, 1180, 600, 100), "Sora", 56, NAVY,
          weight=800, align="left", anim_in=win(), anim_out=wout(), name="Nombre")
    label(t, t.track("text", "Cargo"), "Cargo o tema", 0.9, 2.8, Box(122, 1280, 440, 70), "Inter", 34, TEAL,
          weight=600, align="left", spacing=2, anim_in=win(), anim_out=wout(), name="Cargo")
    return t


def tercio_pildora_vertical():
    t = _kit_tall("tercio-pildora-vertical", "Tercio inferior píldora vertical", "Pill lower third (vertical)",
                  "tercios", 5.0, 7521, ["nombre", "rótulo", "tercio inferior", "píldora", "shorts"], thumb_at=2.4)
    photo_bg(t, "creator-03", s1=1.05, label="Tu video")
    shade_bottom(t, 900, 0.45)
    plate(t, "Placa", WHITE, 0.45, 3.95, Box(150, 1200, 640, 100), radius=50,
          layers=[shadow("#000000", 0, 10, 28, 0.35), fill(WHITE), no_stroke()])
    plate(t, "Placa", NAVY, 0.7, 3.55, Box(214, 1312, 420, 60), radius=30)
    t.solid(t.track("shape", "Círculo"), CORAL, 0.3, 4.3, centered(150, 1250, 116, 116), popout(4.3), kind="ellipse",
            layers=[shadow("#000000", 0, 8, 20, 0.3), fill(CORAL), no_stroke()])
    label(t, t.track("text", "Icono"), "@", 0.45, 4.05, centered(150, 1250, 116, 116), "Inter", 60, WHITE,
          weight=800, anim_in=tanim("pop", duration=0.35), anim_out=fout(0.2), editable=False, name="Icono")
    label(t, t.track("text", "Nombre"), "Nombre Apellido", 0.75, 3.4, Box(226, 1200, 550, 100), "Sora", 48, NAVY,
          weight=800, align="left", anim_in=win(), anim_out=wout(), name="Nombre")
    label(t, t.track("text", "Usuario"), "@tuusuario", 0.95, 3.0, Box(240, 1312, 380, 60), "Inter", 30, TEAL,
          weight=700, align="left", spacing=1, anim_in=win(), anim_out=wout(), name="Usuario")
    return t


# =================================================================================================
# Barras de información
# =================================================================================================

def barra_ticker():
    t = _kit("barra-ticker", "Barra de noticias con cinta", "News ticker bar", "barras-info", 6.0, 7800,
             ["barra", "noticias", "cinta", "última hora", "información"], thumb_at=3.0)
    photo_bg(t, "h-city-06", s1=1.05, label="Tu video")
    shade_bottom(t, 300, 0.5)
    y, h = 950, 70
    slide = lambda dur: [(0, {"dy": 130}, "out"), (0.4, {}, "hold"), (dur - 0.4, {}, "in"), (dur, {"dy": 130})]
    t.solid(t.track("shape", "Barra"), NAVY, 0.3, 5.5, Box(0, y, 1920, h), slide(5.5), alpha=0.94)
    t.solid(t.track("shape", "Línea"), TEAL, 0.3, 5.5, Box(0, y - 4, 1920, 4), slide(5.5))
    # The news crawls in from behind the clock and goes out behind the label.
    news = ("Escribe aquí tu noticia principal     •     Segunda noticia del día con más detalles     •     "
            "Tercera noticia: lo que viene en el próximo video     •     Escribe aquí tu noticia principal     •")
    label(t, t.track("text", "Cinta"), news, 0.8, 4.55, Box(1720, y, 4600, h), "Inter", 32, WHITE, weight=600,
          align="left", motion=[(0, {}, "linear"), (4.55, {"dx": -2900})], anim_out=fout(0.2), name="Cinta de noticias")
    t.solid(t.track("shape", "Etiqueta"), CORAL, 0.5, 5.2, Box(0, y, 330, h), grow(Box(0, y, 330, h), "left", 5.2))
    label(t, t.track("text", "Etiqueta"), "ÚLTIMA HORA", 0.75, 4.75, Box(40, y, 280, h), "Inter", 30, WHITE,
          weight=800, align="left", spacing=3, anim_in=win(), anim_out=wout(), name="Etiqueta")
    t.solid(t.track("shape", "Reloj"), DEEP, 0.5, 5.2, Box(1720, y, 200, h), grow(Box(1720, y, 200, h), "right", 5.2))
    label(t, t.track("text", "Hora"), "10:30", 0.75, 4.75, Box(1720, y, 180, h), "Sora", 32, WHITE, weight=700,
          anim_in=tanim("fade", duration=0.4), anim_out=fout(0.2), name="Hora")
    return t


def barra_en_vivo():
    t = _kit("barra-en-vivo", "Etiqueta en vivo", "Live tag", "barras-info", 5.0, 7801,
             ["en vivo", "directo", "transmisión", "barra", "etiqueta"], thumb_at=2.4)
    photo_bg(t, "h-concert-01", s1=1.05, label="Tu video")
    shade_top(t, 300, 0.6)
    rrect(t, t.track("shape", "Etiqueta"), CORAL, 0.3, 4.4, Box(80, 70, 230, 58), radius=10, motion=popout(4.4))
    t.solid(t.track("shape", "Punto"), WHITE, 0.45, 4.15, centered(110, 99, 16, 16), popout(4.15, 0.3, 0.2),
            kind="ellipse", opacity=blink(4.15, 1.0, 0.25))
    label(t, t.track("text", "Etiqueta"), "EN VIVO", 0.5, 4.1, Box(128, 70, 176, 58), "Inter", 28, WHITE, weight=800,
          align="left", spacing=4, anim_in=tanim("fade", duration=0.3), anim_out=fout(0.2), name="Etiqueta")
    plate(t, "Espectadores", DEEP, 0.55, 3.95, Box(310, 70, 270, 58), radius=0, alpha=0.75)
    label(t, t.track("text", "Espectadores"), "1,2 mil viendo", 0.75, 3.6, Box(332, 70, 240, 58), "Inter", 26, WHITE,
          weight=600, align="left", anim_in=win(), anim_out=wout(), name="Espectadores")
    plate(t, "Línea", TEAL, 0.9, 3.4, Box(80, 150, 6, 64), side="top", length=0.3, out=0.3)
    label(t, t.track("text", "Título"), "Concierto en directo", 1.05, 3.1, Box(104, 146, 1000, 72), "Sora", 46, WHITE,
          weight=800, align="left", layers=[shadow("#000000", 0, 4, 14, 0.5), fill(WHITE)],
          anim_in=win(), anim_out=wout(), name="Título")
    return t


def barra_episodio():
    t = _kit("barra-episodio", "Distintivo de episodio", "Episode badge", "barras-info", 5.0, 7802,
             ["episodio", "podcast", "serie", "barra", "temporada"], thumb_at=2.4)
    photo_bg(t, "h-podcast-02", s1=1.04, label="Tu video")
    plate(t, "Placa", NAVY, 0.5, 3.85, Box(210, 70, 640, 80))
    plate(t, "Placa", TEAL, 0.65, 3.5, Box(210, 150, 470, 54))
    t.solid(t.track("shape", "Insignia"), SUN, 0.3, 4.3, Box(80, 70, 134, 134), popout(4.3),
            layers=[shadow("#000000", 0, 8, 22, 0.3), fill(SUN), no_stroke()])
    label(t, t.track("text", "EP"), "EPISODIO", 0.45, 3.95, Box(80, 80, 134, 30), "Inter", 18, NAVY, weight=800,
          spacing=3, anim_in=tanim("fade", duration=0.3), anim_out=fout(0.2), name="Antetítulo")
    label(t, t.track("text", "Número"), "12", 0.45, 3.95, Box(80, 104, 134, 96), "Anton", 82, NAVY, weight=400,
          anim_in=tanim("pop", duration=0.4), anim_out=fout(0.2), name="Número")
    label(t, t.track("text", "Título"), "Título del episodio", 0.8, 3.35, Box(240, 70, 590, 80), "Sora", 42, WHITE,
          weight=800, align="left", anim_in=win(), anim_out=wout(), name="Título")
    label(t, t.track("text", "Detalle"), "TEMPORADA 2 · INVITADA", 0.95, 3.0, Box(236, 150, 440, 54), "Inter",
          22, NAVY, weight=800, align="left", spacing=3, anim_in=win(), anim_out=wout(), name="Detalle")
    return t


def barra_capitulos():
    t = _kit("barra-capitulos", "Barra de capítulos", "Chapter progress bar", "barras-info", 6.0, 7803,
             ["capítulos", "progreso", "barra", "índice", "tutorial"], thumb_at=3.2)
    photo_bg(t, "h-travel-02", s1=1.05, label="Tu video")
    shade_bottom(t, 420, 0.75)
    names = ["Intro", "Subida al mirador", "El valle", "Despedida"]
    x0, total, gap, y = 120, 1680, 14, 970
    w = (total - gap * 3) / 4
    dur = 5.4
    for i, nm in enumerate(names):
        x = x0 + i * (w + gap)
        at = 0.3 + i * 0.08
        d = dur - i * 0.08
        plate(t, "Capítulo", WHITE, at, d, Box(x, y, w, 8), length=0.45, out=0.3, alpha=0.3, radius=4)
        label(t, t.track("text", "Capítulo"), nm, at + 0.35, d - 0.6, Box(x, y - 46, w, 38), "Inter", 24,
              TEAL if i == 1 else WHITE, weight=700 if i == 1 else 500, align="left", valign="bottom",
              anim_in=tanim("wipe", duration=0.5, angle=-90, softness=0.1),
              anim_out=tanim("wipe", duration=0.3, angle=-90, softness=0.1), name=f"Capítulo {i + 1}")
    # Chapter 1 done, chapter 2 playing.
    plate(t, "Progreso", TEAL, 0.6, 4.95, Box(x0, y, w, 8), length=0.4, out=0.3, radius=4)
    x2 = x0 + w + gap
    play = 4.6
    t.solid(t.track("shape", "Progreso"), TEAL, 0.9, play, Box(x2, y, w * 0.8, 8),
            [(0, {"sx": 0.0, "dx": -w * 0.4}, "linear"), (play - 0.3, {}, "in"), (play, {"sx": 0.0, "dx": -w * 0.4})],
            kind="rounded-rectangle", radius=4)
    t.solid(t.track("shape", "Cabezal"), WHITE, 0.9, play, centered(x2, y + 4, 22, 22),
            [(0, {"s": 0.0}, "out"), (0.25, {"dx": w * 0.8 * 0.25 / (play - 0.3)}, "linear"),
             (play - 0.3, {"dx": w * 0.8}, "in"), (play, {"dx": w * 0.8, "s": 0.0})],
            kind="ellipse", layers=[shadow("#000000", 0, 2, 8, 0.5), fill(WHITE), no_stroke()])
    label(t, t.track("text", "Antetítulo"), "CAPÍTULO 02", 0.5, 4.6, Box(x0, 820, 700, 36), "Inter", 24, TEAL,
          weight=800, align="left", spacing=6, anim_in=tanim("fade", duration=0.4), anim_out=fout(0.25),
          name="Antetítulo")
    label(t, t.track("text", "Título"), "Subida al mirador", 0.6, 4.45, Box(x0 - 2, 852, 1200, 66), "Sora", 50, WHITE,
          weight=800, align="left", anim_in=tanim("rise", duration=0.5), anim_out=fout(0.25), name="Título")
    return t


def barra_tema():
    t = _kit("barra-tema", "Barra de tema", "Topic bar", "barras-info", 5.0, 7804,
             ["tema", "barra", "título", "esquina", "información"], thumb_at=2.4)
    photo_bg(t, "h-desk-02", s1=1.05, label="Tu video")
    plate(t, "Línea", CORAL, 0.3, 4.4, Box(80, 70, 10, 128), side="top", length=0.3, out=0.3)
    plate(t, "Placa", TEAL, 0.45, 3.9, Box(90, 70, 270, 42))
    plate(t, "Placa", NAVY, 0.55, 3.75, Box(90, 112, 720, 86))
    label(t, t.track("text", "Antetítulo"), "TEMA DE HOY", 0.7, 3.5, Box(112, 70, 240, 42), "Inter", 22, NAVY,
          weight=800, align="left", spacing=5, anim_in=win(), anim_out=wout(), name="Antetítulo")
    label(t, t.track("text", "Tema"), "Cómo empezar tu canal", 0.8, 3.35, Box(114, 112, 680, 86), "Sora", 46, WHITE,
          weight=800, align="left", anim_in=win(), anim_out=wout(), name="Tema")
    return t


def barra_fecha_lugar():
    t = _kit("barra-fecha-lugar", "Barra de fecha y lugar", "Date and place bar", "barras-info", 5.0, 7805,
             ["fecha", "lugar", "evento", "barra", "calendario"], thumb_at=2.4)
    photo_bg(t, "h-city-03", s1=1.05, label="Tu video")
    shade_bottom(t, 360, 0.5)
    plate(t, "Placa", NAVY, 0.5, 3.85, Box(210, 870, 600, 110), alpha=0.95)
    cal = Box(80, 850, 130, 150)
    t.solid(t.track("shape", "Calendario"), WHITE, 0.3, 4.3, cal, popout(4.3),
            layers=[shadow("#000000", 0, 8, 22, 0.35), fill(WHITE), no_stroke()])
    t.solid(t.track("shape", "Calendario"), CORAL, 0.3, 4.3, Box(80, 850, 130, 42),
            [(0, {"s": 0.0, "dy": 54}, "back"), (0.4, {}, "hold"), (4.0, {}, "in"), (4.3, {"s": 0.0, "dy": 54})])
    label(t, t.track("text", "Mes"), "OCT", 0.45, 3.95, Box(80, 850, 130, 42), "Inter", 24, WHITE, weight=800,
          spacing=4, anim_in=tanim("fade", duration=0.3), anim_out=fout(0.2), name="Mes")
    label(t, t.track("text", "Día"), "30", 0.45, 3.95, Box(80, 890, 130, 110), "Anton", 76, NAVY, weight=400,
          anim_in=tanim("pop", duration=0.4), anim_out=fout(0.2), name="Día")
    label(t, t.track("text", "Lugar"), "Ciudad, País", 0.8, 3.35, Box(240, 876, 550, 60), "Sora", 44, WHITE,
          weight=800, align="left", valign="bottom", anim_in=win(), anim_out=wout(), name="Lugar")
    label(t, t.track("text", "Hora"), "SÁBADO · 20:00 H", 0.95, 3.05, Box(242, 936, 550, 36), "Inter", 24, TEAL,
          weight=700, align="left", valign="top", spacing=4, anim_in=win(), anim_out=wout(), name="Hora")
    return t


def barra_encuesta():
    t = _kit("barra-encuesta", "Barra de encuesta", "Poll bar", "barras-info", 6.0, 7806,
             ["encuesta", "pregunta", "votación", "barra", "comunidad"], thumb_at=3.4)
    photo_bg(t, "h-food-01", s1=1.05, label="Tu video")
    card = Box(120, 700, 840, 290)
    t.solid(t.track("shape", "Tarjeta"), NAVY, 0.3, 5.3, card,
            [(0, {"dy": 60}, "out"), (0.5, {}, "hold"), (4.9, {}, "in"), (5.3, {"dy": 40})], kind="rounded-rectangle",
            radius=20, layers=[shadow("#000000", 0, 14, 40, 0.4), fill(NAVY, 0.94), no_stroke()],
            opacity=fades(5.3, 0.3, 0.4))
    pill(t, t.track("shape", "Etiqueta"), SUN, 0.5, 4.8, Box(156, 676, 196, 46), popout(4.8, 0.4, 0.25))
    label(t, t.track("text", "Etiqueta"), "ENCUESTA", 0.6, 4.6, Box(156, 676, 196, 46), "Inter", 22, NAVY,
          weight=800, spacing=4, anim_in=tanim("fade", duration=0.3), anim_out=fout(0.2), name="Etiqueta")
    label(t, t.track("text", "Pregunta"), "¿Cuál prefieres para el desayuno?", 0.7, 4.5, Box(160, 736, 780, 64),
          "Sora", 40, WHITE, weight=700, align="left", anim_in=tanim("rise", duration=0.5), anim_out=fout(0.25),
          name="Pregunta")
    rows = [("Opción A: dulce", 0.64, TEAL, "64 %"), ("Opción B: salado", 0.36, CORAL, "36 %")]
    for i, (opt, share, c, pct) in enumerate(rows):
        y = 820 + i * 74
        at = 1.0 + i * 0.15
        d = 4.35 - i * 0.15
        rrect(t, t.track("shape", "Barra"), WHITE, at, d, Box(160, y, 780, 56), radius=12, alpha=0.1,
              opacity=fades(d, 0.3, 0.3))
        t.solid(t.track("shape", "Barra"), c, at + 0.3, d - 0.3, Box(160, y, 780 * share, 56),
                [(0, {"sx": 0.0, "dx": -390 * share}, "out"), (1.2, {}, "hold"), (d - 0.6, {}, "in"),
                 (d - 0.3, {"sx": 0.0, "dx": -390 * share})], kind="rounded-rectangle", radius=12, alpha=0.9)
        label(t, t.track("text", "Opción"), opt, at + 0.15, d - 0.2, Box(184, y, 560, 56), "Inter", 28, WHITE,
              weight=700, align="left", anim_in=win(), anim_out=wout(), name=f"Opción {i + 1}")
        label(t, t.track("text", "Porcentaje"), pct, at + 1.2, d - 1.25, Box(760, y, 160, 56), "Sora", 30, WHITE,
              weight=800, align="right", anim_in=tanim("fade", duration=0.4), anim_out=fout(0.2),
              name=f"Porcentaje {i + 1}")
    return t


def barra_patrocinado():
    t = _kit("barra-patrocinado", "Barra de patrocinio", "Sponsor bar", "barras-info", 5.0, 7807,
             ["patrocinado", "patrocinio", "marca", "logo", "barra"], thumb_at=2.4)
    photo_bg(t, "h-summer-01", s1=1.05, label="Tu video")
    card = Box(1220, 850, 620, 140)
    t.solid(t.track("shape", "Tarjeta"), WHITE, 0.3, 4.3, card,
            [(0, {"dx": 720}, "out"), (0.5, {}, "hold"), (3.95, {}, "in"), (4.3, {"dx": 720})],
            kind="rounded-rectangle", radius=18, layers=[shadow("#000000", 0, 12, 34, 0.35), fill(WHITE), no_stroke()])
    plate(t, "Acento", TEAL, 0.55, 3.55, Box(1220, 872, 8, 96), side="top", length=0.3, out=0.25)
    t.photo(t.track("video", "Logo"), "logo-03", 0.6, 3.5, centered(1320, 920, 104, 104), popout(3.5, 0.4, 0.25),
            label="Tu logo")
    label(t, t.track("text", "Antetítulo"), "PATROCINADO POR", 0.75, 3.2, Box(1394, 872, 420, 34), "Inter", 20, CORAL,
          weight=800, align="left", spacing=4, anim_in=win(), anim_out=wout(), name="Antetítulo")
    label(t, t.track("text", "Marca"), "Nombre de la marca", 0.85, 3.05, Box(1394, 906, 430, 52), "Sora", 34, NAVY,
          weight=800, align="left", anim_in=win(), anim_out=wout(), name="Marca")
    label(t, t.track("text", "Lema"), "tusitio.com/codigo", 1.0, 2.8, Box(1394, 952, 420, 30), "Inter", 20, NAVY,
          weight=500, align="left", spacing=1, anim_in=tanim("fade", duration=0.4), anim_out=fout(0.2),
          name="Enlace o código")
    return t


def barra_marcador():
    t = _kit("barra-marcador", "Marcador", "Score bar", "barras-info", 5.0, 7808,
             ["marcador", "deporte", "partido", "fútbol", "barra", "resultado"], thumb_at=2.4)
    photo_bg(t, "h-soccer-03", s1=1.05, label="Tu video")
    shade_top(t, 260, 0.5)
    plate(t, "Equipo", TEAL, 0.45, 3.9, Box(560, 70, 300, 70), side="right")
    plate(t, "Equipo", CORAL, 0.45, 3.9, Box(1060, 70, 300, 70), side="left")
    t.solid(t.track("shape", "Marcador"), NAVY, 0.3, 4.3, Box(860, 70, 200, 70), popout(4.3),
            layers=[shadow("#000000", 0, 8, 22, 0.4), fill(NAVY), no_stroke()])
    plate(t, "Tiempo", DEEP, 0.7, 3.4, Box(900, 140, 120, 40), side="top", length=0.35, out=0.3)
    label(t, t.track("text", "Resultado"), "2 – 1", 0.5, 3.95, Box(860, 70, 200, 70), "Anton", 50, WHITE, weight=400,
          spacing=2, anim_in=tanim("pop", duration=0.4), anim_out=fout(0.2), name="Resultado")
    label(t, t.track("text", "Equipo 1"), "LOCAL", 0.75, 3.35, Box(580, 70, 260, 70), "Oswald", 40, NAVY, weight=700,
          align="right", spacing=3, anim_in=win(180), anim_out=wout(180), name="Equipo 1")
    label(t, t.track("text", "Equipo 2"), "VISITA", 0.75, 3.35, Box(1080, 70, 260, 70), "Oswald", 40, WHITE,
          weight=700, align="left", spacing=3, anim_in=win(), anim_out=wout(), name="Equipo 2")
    label(t, t.track("text", "Minuto"), "45:00", 0.9, 3.0, Box(900, 140, 120, 40), "Inter", 24, SUN, weight=700,
          spacing=2, anim_in=tanim("fade", duration=0.3), anim_out=fout(0.2), name="Minuto")
    return t


def barra_temporizador():
    t = _kit("barra-temporizador", "Barra de cuenta atrás", "Countdown timer bar", "barras-info", 6.0, 7809,
             ["temporizador", "cuenta atrás", "tiempo", "barra", "reto"], thumb_at=2.6)
    photo_bg(t, "h-cooking-03", s1=1.05, label="Tu video")
    shade_bottom(t, 360, 0.5)
    card = Box(80, 860, 840, 130)
    t.solid(t.track("shape", "Placa"), NAVY, 0.3, 5.4, card,
            [(0, {"dy": 200}, "out"), (0.45, {}, "hold"), (5.0, {}, "in"), (5.4, {"dy": 200})],
            kind="rounded-rectangle", radius=18, layers=[shadow("#000000", 0, 12, 30, 0.35), fill(NAVY, 0.95),
                                                          no_stroke()])
    t.solid(t.track("shape", "Reloj"), SUN, 0.45, 5.0, centered(160, 925, 100, 100), popout(5.0), kind="ellipse")
    rrect(t, t.track("shape", "Pista"), WHITE, 0.6, 4.6, Box(234, 944, 650, 14), radius=7, alpha=0.15,
          motion=grow(Box(234, 944, 650, 14), "left", 4.6, 0.4, 0.3))
    # The bar empties over five seconds while the count goes 5…1.
    count0, step = 0.8, 0.9
    bar_d = step * 5
    t.solid(t.track("shape", "Tiempo"), TEAL, count0 - 0.1, bar_d + 0.1, Box(234, 944, 650, 14),
            [(0, {"sx": 0.0, "dx": -325}, "out"), (0.1, {}, "linear"), (bar_d + 0.1, {"sx": 0.0, "dx": -325})],
            kind="rounded-rectangle", radius=7)
    for i in range(5):
        label(t, t.track("text", "Cuenta"), str(5 - i), count0 + i * step, step, centered(160, 925, 100, 100), "Anton",
              64, NAVY, weight=400, anim_in=tanim("pop", duration=0.25), name=f"Cuenta {5 - i}")
    label(t, t.track("text", "Título"), "¿Lo adivinas antes de que acabe?", 0.7, 4.75, Box(236, 870, 660, 60),
          "Sora", 36, WHITE, weight=700, align="left", anim_in=win(), anim_out=wout(), name="Título")
    return t


def barra_dato():
    t = _kit("barra-dato", "Barra de dato curioso", "Fun fact bar", "barras-info", 6.0, 7810,
             ["dato", "sabías que", "curiosidad", "barra", "información"], thumb_at=3.0)
    photo_bg(t, "h-earth-01", s1=1.05, label="Tu video")
    shade_bottom(t, 360, 0.45)
    plate(t, "Placa", WHITE, 0.5, 4.85, Box(120, 886, 1180, 100),
          layers=[shadow("#000000", 0, 10, 30, 0.3), fill(WHITE), no_stroke()])
    rrect(t, t.track("shape", "Etiqueta"), SUN, 0.3, 5.3, Box(120, 830, 330, 56), radius=0,
          motion=grow(Box(120, 830, 330, 56), "bottom", 5.3, 0.35, 0.3))
    label(t, t.track("text", "Etiqueta"), "¿SABÍAS QUE…?", 0.5, 4.95, Box(144, 830, 300, 56), "Inter", 26, NAVY,
          weight=800, align="left", spacing=3, anim_in=tanim("wipe", duration=0.5, angle=-90, softness=0.1),
          anim_out=tanim("wipe", duration=0.3, angle=-90, softness=0.1), name="Etiqueta")
    label(t, t.track("text", "Dato"), "Escribe aquí un dato curioso sobre el tema de tu video.", 0.8, 4.3,
          Box(150, 886, 1130, 100), "Sora", 34, NAVY, weight=700, align="left", anim_in=win(duration=0.9),
          anim_out=wout(), name="Dato")
    return t


def barra_noticia():
    t = _kit("barra-noticia", "Barra de titular", "Headline bar", "barras-info", 6.0, 7811,
             ["noticia", "titular", "barra", "información", "directo"], thumb_at=3.0)
    photo_bg(t, "h-city-05", s1=1.05, label="Tu video")
    shade_bottom(t, 380, 0.55)
    plate(t, "Placa", NAVY, 0.45, 4.95, Box(120, 846, 1680, 100), alpha=0.96)
    plate(t, "Placa", WHITE, 0.6, 4.65, Box(120, 946, 1300, 52))
    plate(t, "Etiqueta", CORAL, 0.3, 5.3, Box(120, 790, 230, 56), side="bottom", length=0.35, out=0.3)
    plate(t, "Reloj", DEEP, 0.7, 4.5, Box(1620, 846, 180, 100), side="right", length=0.4, out=0.3)
    label(t, t.track("text", "Etiqueta"), "NOTICIA", 0.5, 4.95, Box(144, 790, 200, 56), "Inter", 26, WHITE,
          weight=800, align="left", spacing=5, anim_in=tanim("wipe", duration=0.5, angle=-90, softness=0.1),
          anim_out=tanim("wipe", duration=0.3, angle=-90, softness=0.1), name="Etiqueta")
    label(t, t.track("text", "Titular"), "Escribe aquí el titular principal", 0.75, 4.4, Box(150, 846, 1440, 100),
          "Sora", 50, WHITE, weight=800, align="left", anim_in=win(duration=0.8), anim_out=wout(), name="Titular")
    label(t, t.track("text", "Detalle"), "Más detalles de la noticia en una sola línea", 0.95, 4.0,
          Box(150, 946, 1250, 52), "Inter", 26, NAVY, weight=600, align="left", anim_in=win(duration=0.8),
          anim_out=wout(), name="Detalle")
    label(t, t.track("text", "Hora"), "10:30", 1.0, 4.0, Box(1620, 846, 180, 100), "Sora", 40, WHITE, weight=700,
          anim_in=tanim("fade", duration=0.4), anim_out=fout(0.2), name="Hora")
    return t


TEMPLATES = [tercio_pildora, tercio_corchete, tercio_minimal, tercio_avatar, tercio_derecha, tercio_entrevista,
             tercio_ubicacion, tercio_claro, tercio_vidrio, tercio_paso, tercio_diagonal, tercio_etiqueta,
             tercio_doble_vertical, tercio_pildora_vertical,
             barra_ticker, barra_en_vivo, barra_episodio, barra_capitulos, barra_tema, barra_fecha_lugar,
             barra_encuesta, barra_patrocinado, barra_marcador, barra_temporizador, barra_dato, barra_noticia]
