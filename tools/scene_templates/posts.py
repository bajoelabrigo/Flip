"""Layout families for the 1:1 feed posts (templates_s*.py), 1080x1080.

Each family takes a spec dict and builds one Template. A spec always has id, es, en, cat, order, tags and a
palette (bg, fg, accent[, accent2, ink]); the rest depends on the family. Families have their own style
switches (where the photo goes, how the title enters, which decoration), so two posts of one family look
like two designs, not a recolour.
"""

from __future__ import annotations

from kit import (Box, appear, bg, bg_gradient, centered, circle_photo, confetti, dots, effect, fill, flash, framed,
                 glow, gradient, grain, keys, kb, label, line, math, no_stroke, outline, photo_bg, pill, pop, random,
                 ring, rrect, shade_bottom, shade_full, shade_top, shadow, slide_in, song, spike, square, stroke, tanim,
                 vignette)

S = 1080


def _lum(c):
    c = c.lstrip("#")[-6:]
    ch = [int(c[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    ch = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in ch]
    return 0.2126 * ch[0] + 0.7152 * ch[1] + 0.0722 * ch[2]


def _ratio(a, b):
    la, lb = sorted((_lum(a), _lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def _readable(back, *cands, need=3.0):
    """The first candidate colour that reads on `back`; else black or white, whichever reads better."""
    for c in cands:
        if c and _ratio(back, c) >= need:
            return c
    return "#111111" if _ratio(back, "#111111") >= _ratio(back, "#FFFFFF") else "#FFFFFF"


def _t(spec, dur_default=8.0):
    p = spec["pal"]
    return square(spec["id"], spec["es"], spec["en"], spec["cat"], spec.get("dur", dur_default), order=spec["order"],
                  tags=spec["tags"], thumb_at=spec.get("thumb"), background=p["bg"])


def _bg(t, spec):
    """Background: solid, gradient, or blurred photo (spec["bgstyle"])."""
    p = spec["pal"]
    style = spec.get("bgstyle", "solid")
    if style == "gradient":
        bg_gradient(t, [(0, p["bg"]), (1, p.get("bg2", p["accent"]))], angle=spec.get("angle", 135))
    elif style == "blur" and spec.get("photo"):
        photo_bg(t, spec["photo"], s1=1.08, label="Fondo",
                 effects=[effect("builtin.effects.gaussian_blur", u_blurRadius=16), effect("color.basic", exposure=-0.25)])
        shade_full(t, 0.35, colour=p["bg"])
    elif style == "dots":
        bg(t, p["bg"])
        tr = t.track("shape", "Puntos")
        for r in range(9):
            for c in range(9):
                t.solid(tr, p.get("accent2", p["accent"]), 0, t.duration, centered(60 + c * 120, 60 + r * 120, 10, 10),
                        kind="ellipse", alpha=0.25)
    elif style == "stripes":
        bg(t, p["bg"])
        for k in range(8):
            t.solid(t.track("shape", "Franja"), p.get("accent2", p["accent"]), 0, t.duration,
                    Box(-300 + k * 220, -200, 90, 1600), [(0, {}, "linear"), (t.duration, {"dx": 220})],
                    rotation=keys([(0, 25)]), alpha=0.18)
    else:
        bg(t, p["bg"])


def _title(t, spec, box, size=None, align="center", at=0.3, colour=None, font=None, anim=None, line_h=1.0,
           name="Título", layers=None, weight=None):
    p = spec["pal"]
    f = font or spec.get("font", "Montserrat")
    w = weight or spec.get("weight", 800)
    a = anim or spec.get("anim", "rise-by-word")
    params = {"rise-by-word": dict(duration=0.45, unit="word", stagger=0.12), "pop": dict(duration=0.45, unit="word",
              stagger=0.1, ease="back"), "stamp": dict(duration=0.3), "typewriter": dict(duration=1.0, unit="character"),
              "slide-up": dict(duration=0.4, unit="character", stagger=0.03), "blur-in": dict(duration=0.8),
              "wipe": dict(duration=0.6, angle=0), "bounce": dict(duration=0.5, unit="character", stagger=0.03),
              "drop": dict(duration=0.5, unit="character", stagger=0.03), "fade-up-char": dict(duration=0.4,
              unit="character", stagger=0.02), "zoom-out": dict(duration=0.5), "flicker-in": dict(duration=0.7),
              "glitch-in": dict(duration=0.4)}[a]
    return label(t, t.track("text", name), spec["title"], at, t.duration - at, box, f, size or spec.get("size", 110),
                 colour or p["fg"], weight=w, align=align, line=line_h, layers=layers, anim_in=tanim(a, **params),
                 name=name)


def _sub(t, spec, key, box, size=44, at=0.9, colour=None, align="center", font=None, name="Texto", weight=600,
         italic=False, spacing=0):
    if not spec.get(key):
        return
    p = spec["pal"]
    label(t, t.track("text", name), spec[key], at, t.duration - at, box, font or spec.get("body", "Montserrat"), size,
          colour or p["fg"], weight=weight, align=align, italic=italic, spacing=spacing, line=1.2,
          anim_in=tanim("fade", duration=0.5), name=name)


def _cta(t, spec, box, at=1.6, colour=None, text_colour=None, font=None, size=40):
    if not spec.get("cta"):
        return
    p = spec["pal"]
    pill(t, t.track("shape", "Botón"), colour or p["accent"], at, t.duration - at, box, pop(0, 0.4))
    label(t, t.track("text", "Botón"), spec["cta"], at, t.duration - at, box, font or spec.get("body", "Montserrat"),
          size, text_colour or p.get("ink", "#FFFFFF"), weight=800, anim_loop=tanim("pulse", amount=3, speed=1.2),
          name="Llamada")


def _badge(t, spec, box, at=0.5):
    if not spec.get("badge"):
        return
    p = spec["pal"]
    back = p.get("accent2", p["accent"])
    pill(t, t.track("shape", "Insignia"), back, at, t.duration - at, box, pop(0, 0.35))
    label(t, t.track("text", "Insignia"), spec["badge"], at, t.duration - at, box, spec.get("body", "Montserrat"),
          int(box.h * 0.45), _readable(back, p.get("ink"), "#FFFFFF"), weight=800, spacing=3, name="Insignia")


def _deco(t, spec):
    """Small decorations that give each post its own character."""
    p = spec["pal"]
    d = spec.get("deco")
    if d == "frame":
        outline(t, t.track("shape", "Marco"), p.get("accent2", p["fg"]), 4, 0.2, t.duration - 0.2, Box(36, 36, 1008, 1008),
                alpha=0.8, opacity=keys([(0, 0.0), (0.6, 1.0)]))
    elif d == "corners":
        for (x, y, dx, dy) in ((50, 50, 1, 1), (1030, 50, -1, 1), (50, 1030, 1, -1), (1030, 1030, -1, -1)):
            t.solid(t.track("shape", "Esquina"), p["accent"], 0.3, t.duration - 0.3,
                    Box(x if dx > 0 else x - 120, y if dy > 0 else y - 10, 120, 10), pop(0, 0.3))
            t.solid(t.track("shape", "Esquina"), p["accent"], 0.3, t.duration - 0.3,
                    Box(x if dx > 0 else x - 10, y if dy > 0 else y - 120, 10, 120), pop(0, 0.3))
    elif d == "sparkles":
        # in the side margins, so they never sit on the text
        for k, area in enumerate((Box(10, 40, 150, 1000), Box(920, 40, 150, 1000))):
            dots(t, [p["accent"], "#FFFFFF", p.get("accent2", p["accent"])], 9, 0.3, t.duration - 0.3,
                 seed=spec["order"] + k, size=(10, 26), kinds=("star",), drift=60, area=area)
    elif d == "confetti":
        confetti(t, [p["accent"], p.get("accent2", "#FFFFFF"), "#FFFFFF"], 0.6, t.duration - 0.6, seed=spec["order"],
                 lanes=3, density=0.35, size=(14, 30))
    elif d == "hearts":
        for k, area in enumerate((Box(10, 120, 120, 960), Box(950, 120, 120, 960))):
            dots(t, [p["accent"], p.get("accent2", "#FFFFFF")], 7, 0.3, t.duration - 0.3, seed=spec["order"] + k,
                 size=(26, 50), kinds=("heart",), drift=160, alpha=0.85, area=area)
    elif d == "blobs":
        rng = random.Random(spec["order"])
        for k in range(3):
            c = [p["accent"], p.get("accent2", p["accent"]), p["fg"]][k]
            s = rng.uniform(380, 560)
            t.solid(t.track("shape", "Mancha"), c, 0, t.duration, centered(rng.choice([80, 1000]), rng.uniform(100, 980), s, s),
                    [(0, {"s": 0.0}, "out"), (0.8, {}, "smooth"), (t.duration, {"s": 1.08})], kind="cloud", alpha=0.18)
    elif d == "grain":
        grain(t, 0.18)
    elif d == "leak":
        t.adjust([effect("light_leak", intensity=0.35, hue=0.07, speed=0.6)], name="Luz")


# --- 1. Poster: a photo, a big title -------------------------------------------------------------

def poster(spec):
    t = _t(spec)
    p = spec["pal"]
    photo_bg(t, spec["photo"], s1=spec.get("zoom", 1.1), label=spec.get("plabel", "Tu foto"))
    shade = spec.get("shade", "bottom")
    if shade == "bottom":
        shade_bottom(t, 800, 0.92, colour=p["bg"])
        tbox, sy = Box(60, 620, 960, 260), 880
    elif shade == "top":
        shade_top(t, 800, 0.92, colour=p["bg"])
        tbox, sy = Box(60, 110, 960, 260), 380
    elif shade == "left":
        t.solid(t.track("shape", "Panel"), p["bg"], 0, t.duration, Box(0, 0, 600, 1080), slide_in(dx=-600, length=0.5),
                alpha=0.86)
        tbox, sy = Box(50, 300, 520, 420), 740
    else:
        shade_full(t, 0.5, colour=p["bg"])
        tbox, sy = Box(80, 330, 920, 300), 660
    align = "left" if shade == "left" else spec.get("align", "center")
    _title(t, spec, tbox, align=align)
    _sub(t, spec, "sub", Box(tbox.x, sy, tbox.w, 120), align=align)
    _badge(t, spec, Box(60, 60, 300, 70) if shade != "top" else Box(60, 960, 300, 70))
    _cta(t, spec, Box(tbox.x if align == "left" else 290, sy + 120 if shade != "top" else 520, 500, 96))
    _deco(t, spec)
    song(t, spec.get("mood", "upbeat"), spec.get("pick", 0), 0.75)
    return t


# --- 2. Split: photo on one side, colour on the other ---------------------------------------------

def split(spec):
    t = _t(spec)
    p = spec["pal"]
    _bg(t, spec)
    side = spec.get("side", "left")
    if side in ("left", "right"):
        pb = Box(0, 0, 540, 1080) if side == "left" else Box(540, 0, 540, 1080)
        tb = Box(600, 200, 430, 680) if side == "left" else Box(50, 200, 430, 680)
        motion = slide_in(dx=-540 if side == "left" else 540, length=0.6)
    elif side == "top":
        pb, tb, motion = Box(0, 0, 1080, 560), Box(70, 600, 940, 420), slide_in(dy=-560, length=0.6)
    else:  # card: photo inset with rounded corners and a shadow
        pb, tb, motion = Box(70, 70, 560, 940), Box(670, 180, 360, 720), pop(0, 0.5, 0.8)
    if side == "card":
        framed(t, spec["photo"], 0.2, t.duration - 0.2, pb, motion, border=0, radius=30, colour=p["accent"],
               label=spec.get("plabel", "Tu foto"))
    else:
        t.photo(t.track("video", "Foto"), spec["photo"], 0.0, t.duration, pb, motion + [(t.duration, {"s": 1.05})],
                label=spec.get("plabel", "Tu foto"))
    align = "left"
    _title(t, spec, Box(tb.x, tb.y, tb.w, tb.h * 0.5), align=align, size=spec.get("size", 84))
    _sub(t, spec, "sub", Box(tb.x, tb.y + tb.h * 0.5, tb.w, 110), size=38, align=align)
    if spec.get("items"):
        for i, it in enumerate(spec["items"]):
            label(t, t.track("text", "Punto"), "• " + it, 1.2 + i * 0.3, t.duration - 1.2 - i * 0.3,
                  Box(tb.x, tb.y + tb.h * 0.5 + 120 + i * 60, tb.w, 56), spec.get("body", "Montserrat"), 36, p["fg"],
                  weight=600, align="left", anim_in=tanim("slide-right", duration=0.3, distance=0.15), name=f"Punto {i + 1}")
    _cta(t, spec, Box(tb.x, tb.y + tb.h - 90, min(tb.w, 420), 90), size=34)
    _badge(t, spec, Box(pb.x + 30, pb.y + 30, 260, 64))
    _deco(t, spec)
    song(t, spec.get("mood", "upbeat"), spec.get("pick", 1), 0.75)
    return t


# --- 3. Price: the product and a price shape ------------------------------------------------------

def price(spec):
    t = _t(spec)
    p = spec["pal"]
    _bg(t, spec)
    look = spec.get("look", "card")
    pc = (540, 520)
    if look == "circle":
        circle_photo(t, spec["photo"], 0.2, t.duration - 0.2, centered(*pc, 600, 600), pop(0, 0.5, 0.5),
                     ring_colour=p["accent"], ring_width=14, label="Foto del producto")
    elif look == "tilt":
        framed(t, spec["photo"], 0.2, t.duration - 0.2, centered(*pc, 560, 620), [(0, {"s": 0.5}, "back"), (0.5, {})],
               border=18, radius=24, rotation=keys([(0, -5)]), label="Foto del producto")
    else:
        framed(t, spec["photo"], 0.2, t.duration - 0.2, centered(*pc, 620, 620), pop(0, 0.5, 0.6), border=0, radius=40,
               label="Foto del producto")
    _title(t, spec, Box(60, 40, 960, 140), size=spec.get("size", 84))
    shape = spec.get("tag", "burst")
    tx, ty = spec.get("tagpos", (830, 760))
    at = 1.2
    if shape == "burst":
        t.solid(t.track("shape", "Precio"), p["accent"], at, t.duration - at, centered(tx, ty, 330, 330),
                [(0, {"s": 0.0}, "back"), (0.45, {})], kind="burst", points=18, innerRatio=0.86,
                rotation=keys([(0, 0, "linear"), (t.duration, 25)]))
    elif shape == "circle":
        t.solid(t.track("shape", "Precio"), p["accent"], at, t.duration - at, centered(tx, ty, 300, 300), pop(0, 0.45),
                kind="ellipse", layers=[shadow("#000000", 0, 10, 20, 0.3), fill(p["accent"]), no_stroke()])
    else:
        pill(t, t.track("shape", "Precio"), p["accent"], at, t.duration - at, centered(tx, ty, 380, 150), pop(0, 0.45))
    label(t, t.track("text", "Precio"), spec["price"], at + 0.1, t.duration - at - 0.1, centered(tx, ty, 320, 160),
          spec.get("pfont", "Anton"), spec.get("psize", 110), p.get("ink", "#FFFFFF"), weight=400,
          anim_in=tanim("stamp", duration=0.3), name="Precio")
    if spec.get("old"):
        label(t, t.track("text", "Antes"), spec["old"], at + 0.4, t.duration - at - 0.4, Box(tx - 160, ty + 100, 320, 60),
              spec.get("body", "Montserrat"), 40, p["fg"], weight=700, name="Precio anterior",
              anim_in=tanim("fade", duration=0.3))
        t.solid(t.track("shape", "Tachado"), p["fg"], at + 0.6, t.duration - at - 0.6, Box(tx - 80, ty + 128, 160, 5),
                [(0, {"sx": 0.0, "dx": -80}, "out"), (0.3, {})])
    _sub(t, spec, "sub", Box(60, 860, 700, 80), size=42, align="left")
    _cta(t, spec, Box(60, 950, 460, 90), at=2.0)
    _deco(t, spec)
    song(t, spec.get("mood", "upbeat"), spec.get("pick", 2), 0.75)
    return t


# --- 4. Quote: a sentence that breathes -----------------------------------------------------------

def quote(spec):
    t = _t(spec, 9.0)
    p = spec["pal"]
    _bg(t, spec)
    mark = spec.get("mark", "“")
    if mark:
        label(t, t.track("text", "Comillas"), mark, 0.2, t.duration - 0.2, Box(60, 60, 400, 300), spec.get("font", "Playfair Display"),
              320, p["accent"], weight=800, align="left", editable=False, anim_in=tanim("pop", duration=0.4))
    _title(t, spec, Box(90, 260, 900, 520), size=spec.get("size", 88), line_h=1.12,
           anim=spec.get("anim", "rise-by-word"), font=spec.get("font", "Playfair Display"), weight=spec.get("weight", 600))
    line(t, t.track("shape", "Línea"), p["accent"], 2.0, t.duration - 2.0, centered(540, 830, 160, 5), grow="c", length=0.5)
    _sub(t, spec, "author", Box(90, 860, 900, 80), size=40, at=2.3,
         colour=_readable(p["bg"], p.get("accent2"), p["accent"], p["fg"]), spacing=4)
    _deco(t, spec)
    song(t, spec.get("mood", "calm"), spec.get("pick", 0), 0.7)
    return t


# --- 5. List card ---------------------------------------------------------------------------------

def listcard(spec):
    t = _t(spec, 9.0)
    p = spec["pal"]
    _bg(t, spec)
    has_photo = bool(spec.get("photo"))
    w = 560 if has_photo else 940
    if has_photo:
        framed(t, spec["photo"], 0.2, t.duration - 0.2, Box(650, 190, 370, 700), pop(0, 0.5, 0.8), border=0, radius=30,
               label="Foto")
    _title(t, spec, Box(70, 60, 940, 160), size=spec.get("size", 76), align="left")
    chip = spec.get("chip", "number")
    for i, it in enumerate(spec["items"]):
        at = 1.0 + i * 0.7
        y = 260 + i * 150
        if chip == "check":
            g = "✓"
        elif chip == "number":
            g = str(i + 1)
        else:
            g = spec["icons"][i]
        t.solid(t.track("shape", "Chip"), p["accent"], at, t.duration - at, centered(115, y + 55, 90, 90), pop(0, 0.35),
                kind="ellipse")
        label(t, t.track("text", "Chip"), g, at, t.duration - at, centered(115, y + 55, 90, 90), "Inter", 46,
              p.get("ink", "#FFFFFF"), weight=800, editable=False, motion=pop(0, 0.35))
        label(t, t.track("text", "Punto"), it, at + 0.1, t.duration - at - 0.1, Box(190, y, w - 120, 110),
              spec.get("body", "Montserrat"), 46, p["fg"], weight=700, align="left", line=1.1,
              anim_in=tanim("slide-right", duration=0.35, distance=0.12), name=f"Punto {i + 1}")
    _sub(t, spec, "sub", Box(70, 960, 940, 70), size=36, at=3.5, align="left",
         colour=_readable(p["bg"], p.get("accent2"), p["fg"]))
    _deco(t, spec)
    song(t, spec.get("mood", "upbeat"), spec.get("pick", 3), 0.7)
    return t


# --- 6. Event poster ------------------------------------------------------------------------------

def event(spec):
    t = _t(spec, 9.0)
    p = spec["pal"]
    _bg(t, spec)
    look = spec.get("look", "circle")
    if look == "circle":
        circle_photo(t, spec["photo"], 0.2, t.duration - 0.2, centered(800, 270, 400, 400), pop(0, 0.5),
                     ring_colour=p["accent"], ring_width=10, label="Foto")
    elif look == "band":
        t.photo(t.track("video", "Foto"), spec["photo"], 0, t.duration, Box(0, 0, 1080, 420), kb(t.duration, 1.0, 1.06),
                label="Foto")
    else:
        framed(t, spec["photo"], 0.2, t.duration - 0.2, Box(600, 70, 400, 440), pop(0, 0.5, 0.7), border=12,
               rotation=keys([(0, 4)]), label="Foto")
    cal = Box(70, 330 if look == "band" else 100, 230, 250)
    rrect(t, t.track("shape", "Calendario"), "#FFFFFF", 0.4, t.duration - 0.4, cal, 26, pop(0, 0.45),
          layers=[shadow("#000000", 0, 10, 20, 0.3), fill("#FFFFFF"), no_stroke()])
    t.solid(t.track("shape", "Calendario"), p["accent"], 0.4, t.duration - 0.4, Box(cal.x, cal.y, cal.w, 74), pop(0, 0.45),
            radius=26, kind="rounded-rectangle")
    mon, day = spec["date"]
    label(t, t.track("text", "Mes"), mon, 0.5, t.duration - 0.5, Box(cal.x, cal.y, cal.w, 74), "Montserrat", 40, "#FFFFFF",
          weight=800, spacing=4, motion=pop(0, 0.45), name="Mes")
    label(t, t.track("text", "Día"), day, 0.5, t.duration - 0.5, Box(cal.x, cal.y + 74, cal.w, 176), "Montserrat",
          120 if len(day) <= 2 else 64,
          p.get("ink2", "#1D3557"), weight=800, motion=pop(0, 0.45), name="Día")
    # band: the calendar overlaps the photo's bottom edge and the title sits beside it
    tbox = Box(330, 450, 700, 220) if look == "band" else Box(70, 560, 940, 220)
    _title(t, spec, tbox, size=spec.get("size", 88) if look != "band" else min(spec.get("size", 88), 80), align="left",
           at=0.8)
    for i, (ic, txt) in enumerate(spec["rows"]):
        at = 1.6 + i * 0.3
        y = (700 if look == "band" else 790) + i * 80
        label(t, t.track("text", "Dato"), f"{ic}  {txt}", at, t.duration - at, Box(70, y, 940, 70),
              spec.get("body", "Montserrat"), 40, p["fg"], weight=600, align="left", anim_in=tanim("fade", duration=0.3),
              name=f"Dato {i + 1}")
    _deco(t, spec)
    song(t, spec.get("mood", "upbeat"), spec.get("pick", 4), 0.7)
    return t


# --- 7. Testimonial -------------------------------------------------------------------------------

def testimonial(spec):
    t = _t(spec, 8.0)
    p = spec["pal"]
    _bg(t, spec)
    rrect(t, t.track("shape", "Tarjeta"), p.get("card", "#FFFFFF"), 0.3, t.duration - 0.3, Box(80, 260, 920, 640), 50,
          pop(0, 0.45, 0.85), layers=[shadow("#000000", 0, 14, 34, 0.18), fill(p.get("card", "#FFFFFF")), no_stroke()])
    circle_photo(t, spec["photo"], 0.5, t.duration - 0.5, centered(540, 260, 240, 240), pop(0, 0.5),
                 ring_colour=p["accent"], ring_width=10, label="Foto del cliente")
    for k in range(5):
        label(t, t.track("text", "Estrella"), "★", 1.0 + k * 0.12, t.duration - 1.0 - k * 0.12,
              centered(380 + k * 80, 450, 80, 80), "Inter", 66, p.get("star", "#F4A100"), weight=400, editable=False,
              motion=[(0, {"s": 0.0}, "back"), (0.3, {})])
    label(t, t.track("text", "Reseña"), spec["title"], 1.6, t.duration - 1.6, Box(140, 510, 800, 280),
          spec.get("font", "Lora"), spec.get("size", 52), p.get("cardfg", "#2D2A26"), weight=500, italic=True, line=1.25,
          anim_in=tanim("rise-by-word", duration=0.35, unit="word", stagger=0.05), name="Reseña")
    _sub(t, spec, "author", Box(140, 800, 800, 70), size=38, at=2.6,
         colour=_readable(p.get("card", "#FFFFFF"), p["accent"], p.get("accent2"), p.get("cardfg", "#2D2A26")), weight=700)
    _sub(t, spec, "brand", Box(80, 960, 920, 70), size=36, at=3.0, weight=700, spacing=4)
    _deco(t, spec)
    song(t, spec.get("mood", "calm"), spec.get("pick", 2), 0.65)
    return t


# --- 8. Grid collage ------------------------------------------------------------------------------

def _grid_boxes(kind, g=14):
    if kind == "2x2":
        c = (S - 3 * g) / 2
        return [Box(g + (i % 2) * (c + g), g + (i // 2) * (c + g), c, c) for i in range(4)]
    if kind == "3x3":
        c = (S - 4 * g) / 3
        return [Box(g + (i % 3) * (c + g), g + (i // 3) * (c + g), c, c) for i in range(9)]
    if kind == "1+2":
        h = (S - 3 * g) / 2
        return [Box(g, g, (S - 3 * g) * 0.6, S - 2 * g), Box(g * 2 + (S - 3 * g) * 0.6, g, (S - 3 * g) * 0.4, h),
                Box(g * 2 + (S - 3 * g) * 0.6, g * 2 + h, (S - 3 * g) * 0.4, h)]
    if kind == "2+1":
        w = (S - 3 * g) / 2
        return [Box(g, g, w, (S - 3 * g) * 0.45), Box(g * 2 + w, g, w, (S - 3 * g) * 0.45),
                Box(g, g * 2 + (S - 3 * g) * 0.45, S - 2 * g, (S - 3 * g) * 0.55)]
    if kind == "strip3":
        w = (S - 4 * g) / 3
        return [Box(g + i * (w + g), g, w, S - 2 * g) for i in range(3)]
    raise ValueError(kind)


def grid(spec):
    t = _t(spec, 8.0)
    p = spec["pal"]
    bg(t, p["bg"])
    boxes = _grid_boxes(spec.get("grid", "2x2"), spec.get("gap", 14))
    order = spec.get("order_in") or list(range(len(boxes)))
    motion = spec.get("motion", "pop")
    for rank, i in enumerate(order):
        box = boxes[i]
        at = 0.2 + rank * spec.get("step", 0.35)
        d = t.duration - at
        m = {"pop": [(0, {"s": 0.0}, "back"), (0.45, {}, "linear"), (d, {"s": 1.03})],
             "snap": [(0, {"s": 1.25}, "snap"), (0.25, {}, "linear"), (d, {"s": 1.03})],
             "slide": [(0, {"dy": 1100 if i % 2 else -1100}, "out"), (0.5, {}, "linear"), (d, {"s": 1.03})]}[motion]
        t.photo(t.track("video", f"Celda {i + 1}"), spec["photos"][i], at, d, box, m, label=f"Foto {i + 1}")
    if spec.get("title"):
        tb = spec.get("tbox", Box(190, 450, 700, 180))
        label(t, t.track("text", "Título"), spec["title"], 0.4 + len(boxes) * spec.get("step", 0.35), t.duration - 1.5, tb,
              spec.get("font", "DM Serif Display"), spec.get("size", 72), p.get("ink", "#FFFFFF"),
              weight=spec.get("weight", 400), box_bg=(p["accent"], 0.92), box_pad=24, box_radius=20, anim_in=tanim("pop", duration=0.4), name="Título")
    _deco(t, spec)
    song(t, spec.get("mood", "upbeat"), spec.get("pick", 5), 0.75)
    return t


# --- 9. Stack of prints ---------------------------------------------------------------------------

def stack(spec):
    t = _t(spec, 9.0)
    p = spec["pal"]
    _bg(t, spec)
    rng = random.Random(spec["order"])
    n = len(spec["photos"])
    for i, s in enumerate(spec["photos"]):
        at = 0.2 + i * spec.get("step", 0.9)
        x, y = rng.uniform(330, 750), rng.uniform(360, 640)
        r = rng.uniform(-11, 11)
        framed(t, s, at, t.duration - at, centered(x, y, 460, 460), [(0, {"s": 1.45, "dy": -160}, "out"), (0.45, {})],
               border=spec.get("border", 18), bottom=spec.get("bottom", 80), colour=p.get("paper", "#FFFDF8"),
               rotation=keys([(0, r * 2, "out"), (0.45, r)]), label=f"Foto {i + 1}")
    if spec.get("title"):
        label(t, t.track("text", "Título"), spec["title"], 0.4 + n * spec.get("step", 0.9), t.duration - 1.0,
              Box(60, 900, 960, 140), spec.get("font", "Caveat"), spec.get("size", 110), p["fg"], weight=700,
              layers=[shadow("#000000", 0, 4, 12, spec.get("tshadow", 0.0)), fill(p["fg"])],
              anim_in=tanim("typewriter", duration=0.8, unit="character"), rotation=keys([(0, -3)]), name="Título")
    _deco(t, spec)
    song(t, spec.get("mood", "upbeat"), spec.get("pick", 6), 0.75)
    return t


# --- 10. Before / after --------------------------------------------------------------------------

def beforeafter(spec):
    t = _t(spec, 7.0)
    p = spec["pal"]
    at = spec.get("at", 2.2)
    t.thumb_at = max(t.thumb_at, at + 1.7)  # the card shows both halves and both labels
    t.photo(t.track("video", "Después"), spec["after"], 0, t.duration, t.full, kb(t.duration, 1.0, 1.05), label="Foto de después")
    host = t.track("video", "Antes")
    clip = t.photo(host, spec["before"], 0, t.duration, t.full, kb(t.duration, 1.0, 1.05), label="Foto de antes",
                   effects=[effect("color.basic", saturation=-0.5, exposure=-0.1)])
    if spec.get("wipe", "v") == "v":
        t.mask(host, clip, "rectangle", keyframes={"w": keys([(0, 1.0, "hold"), (at, 1.0, "inout"), (at + 1.2, 0.5)]),
                                                   "x": keys([(0, 0.5, "hold"), (at, 0.5, "inout"), (at + 1.2, 0.25)])})
        t.solid(t.track("shape", "Divisor"), "#FFFFFF", 0, t.duration, Box(1075, 0, 10, 1080),
                [(0, {}, "hold"), (at, {}, "inout"), (at + 1.2, {"dx": -540})])
    else:
        t.mask(host, clip, "rectangle", keyframes={"h": keys([(0, 1.0, "hold"), (at, 1.0, "inout"), (at + 1.2, 0.5)]),
                                                   "y": keys([(0, 0.5, "hold"), (at, 0.5, "inout"), (at + 1.2, 0.25)])})
        t.solid(t.track("shape", "Divisor"), "#FFFFFF", 0, t.duration, Box(0, 1075, 1080, 10),
                [(0, {}, "hold"), (at, {}, "inout"), (at + 1.2, {"dy": -540})])
    labels = spec.get("labels", ("ANTES", "DESPUÉS"))
    for i, txt in enumerate(labels):
        t0 = 0.2 if i == 0 else at + 1.2
        if spec.get("wipe", "v") == "v":
            box = Box(40, 40, 400, 90) if i == 0 else Box(580, 40, 460, 90)
        else:
            box = Box(40, 40, 420, 90) if i == 0 else Box(40, 580, 460, 90)
        # "before" on a dark chip, "after" in the accent: both have to read over any photo
        back = "#111111" if i == 0 else p["accent"]
        pill(t, t.track("shape", "Etiqueta"), back, t0, t.duration - t0, box, pop(0, 0.3))
        label(t, t.track("text", "Etiqueta"), txt, t0, t.duration - t0, box, spec.get("body", "Montserrat"),
              44 if len(txt) <= 9 else 32, _readable(back, "#FFFFFF", p.get("ink")), weight=800, spacing=3,
              name=f"Etiqueta {i + 1}")
    if spec.get("title"):
        label(t, t.track("text", "Título"), spec["title"], at + 1.4, t.duration - at - 1.4, Box(60, 900, 960, 120),
              spec.get("font", "Montserrat"), 60, "#FFFFFF", weight=800, box_bg=("#000000", 0.55), box_pad=18,
              box_radius=16, anim_in=tanim("pop", duration=0.3), name="Título")
    song(t, spec.get("mood", "upbeat"), spec.get("pick", 7), 0.75)
    return t


# --- 11. Big number -------------------------------------------------------------------------------

def bignumber(spec):
    t = _t(spec, 7.0)
    p = spec["pal"]
    _bg(t, spec)
    if spec.get("photo"):
        circle_photo(t, spec["photo"], 0.3, t.duration - 0.3, centered(860, 220, 300, 300), pop(0, 0.5),
                     ring_colour=p["accent"], ring_width=10, label="Foto")
    label(t, t.track("text", "Antetítulo"), spec.get("pre", ""), 0.2, t.duration - 0.2, Box(70, 120, 700, 100),
          spec.get("body", "Montserrat"), 52, p.get("accent2", p["accent"]), weight=800, spacing=6, align="left",
          anim_in=tanim("fade", duration=0.4), name="Antetítulo")
    label(t, t.track("text", "Número"), spec["number"], 0.5, t.duration - 0.5, Box(40, 230, 1000, 520),
          spec.get("nfont", "Anton"), spec.get("nsize", 420), p["accent"], weight=900,
          layers=[shadow(p.get("shadow", "#000000"), 0, 14, 0, spec.get("nshadow", 0.25)), fill(p["accent"])],
          anim_in=tanim(spec.get("nanim", "zoom-out"), duration=0.5), name="Número")
    _title(t, spec, Box(70, 760, 940, 180), size=spec.get("size", 64), at=1.2, anim="fade-up-char")
    _cta(t, spec, Box(290, 950, 500, 90), at=2.0, size=36)
    _deco(t, spec)
    song(t, spec.get("mood", "upbeat"), spec.get("pick", 0), 0.75)
    return t


# --- 12. Menu board -------------------------------------------------------------------------------

def menu(spec):
    t = _t(spec, 9.0)
    p = spec["pal"]
    _bg(t, spec)
    side = spec.get("side", "right")
    pb = Box(600, 0, 480, 1080) if side == "right" else Box(0, 0, 480, 1080)
    tx = 60 if side == "right" else 540
    t.photo(t.track("video", "Plato"), spec["photo"], 0, t.duration, pb, kb(t.duration, 1.0, 1.08), label="Foto del plato")
    _title(t, spec, Box(tx, 60, 500, 150), size=spec.get("size", 76), align="left", font=spec.get("font", "Lobster"),
           weight=400, anim="fade-up-char")
    _sub(t, spec, "sub", Box(tx, 200, 500, 60), size=30, at=0.6, align="left", colour=p["accent"], weight=800, spacing=6)
    for i, (dish, pr) in enumerate(spec["items"]):
        at = 1.0 + i * 0.45
        y = 300 + i * 150
        label(t, t.track("text", "Plato"), dish, at, t.duration - at, Box(tx, y, 380, 110), spec.get("body", "Montserrat"),
              42, p["fg"], weight=600, align="left", line=1.05, anim_in=tanim("slide-right", duration=0.3, distance=0.1),
              name=f"Plato {i + 1}")
        label(t, t.track("text", "Precio"), pr, at + 0.1, t.duration - at - 0.1, Box(tx + 380, y, 120, 110),
              spec.get("body", "Montserrat"), 42, p["accent"], weight=800, align="right", name=f"Precio {i + 1}")
        t.solid(t.track("shape", "Línea"), p.get("rule", p["fg"]), at, t.duration - at, Box(tx, y + 118, 500, 2),
                [(0, {"sx": 0.0, "dx": -250}, "out"), (0.4, {})], alpha=0.35)
    _deco(t, spec)
    song(t, spec.get("mood", "jazz"), spec.get("pick", 1), 0.7)
    return t


# --- 13. Carousel: still photos with a gentle move, one after another ------------------------------

def carousel(spec):
    t = _t(spec, 12.0)
    p = spec["pal"]
    bg(t, p["bg"])
    n = len(spec["photos"])
    each = t.duration / n
    style = spec.get("style", "full")
    v = t.track("video", "Fotos")
    prev = None
    for i, s in enumerate(spec["photos"]):
        at = i * each
        d = each + (0.5 if i < n - 1 else 0)
        box = t.full if style == "full" else Box(70, 70, 940, 940)
        clip = t.photo(v, s, at, min(d, t.duration - at), box, kb(d, 1.0, 1.05) if i % 2 == 0 else kb(d, 1.05, 1.0),
                       label=f"Foto {i + 1}")
        if prev:
            t.transition(v, prev, clip, spec.get("trans", "slide_left"), 0.5)
        prev = clip
    if style == "framed":
        outline(t, t.track("shape", "Marco"), p["bg"], 70, 0, t.duration, t.full)
    for k in range(n):
        t.solid(t.track("shape", "Página"), "#FFFFFF", 0, t.duration, centered(540 - (n - 1) * 20 + k * 40, 1030, 14, 14),
                kind="ellipse", alpha=0.5)
        t.solid(t.track("shape", "Página"), p["accent"], k * each, each, centered(540 - (n - 1) * 20 + k * 40, 1030, 18, 18),
                kind="ellipse")
    caps = spec.get("caps") or []
    for i, c in enumerate(caps):
        label(t, t.track("text", "Pie"), c, i * each + 0.3, each - 0.5, Box(80, 860, 920, 120), spec.get("font", "DM Serif Display"),
              spec.get("size", 72), "#FFFFFF", weight=spec.get("weight", 400),
              layers=[shadow("#000000", 0, 4, 16, 0.75), fill("#FFFFFF")], anim_in=tanim("slide-up", duration=0.35),
              anim_out=tanim("fade", duration=0.25), name=f"Pie {i + 1}")
    _deco(t, spec)
    song(t, spec.get("mood", "calm"), spec.get("pick", 2), 0.75)
    return t


FAMILIES = {"poster": poster, "split": split, "price": price, "quote": quote, "list": listcard, "event": event,
            "testimonial": testimonial, "grid": grid, "stack": stack, "ba": beforeafter, "number": bignumber,
            "menu": menu, "carousel": carousel}


def make(spec, module):
    """A template maker for a spec, owned by `module` (build.py picks batches by module name)."""
    def maker():
        return FAMILIES[spec["fam"]](spec)
    maker.__module__ = module
    maker.__name__ = spec["id"].replace("-", "_")
    return maker
