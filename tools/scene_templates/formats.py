"""Families for short formats: 15-second stories (9:16), 6-second ads (9:16 and 16:9) and video thumbnails
(1920x1080, almost still). Used by templates_f1.py (stories), templates_f2.py (ads), templates_y1.py (thumbnails).

Stories and ads open with the hook in the first second (one striking line or visual), read with the sound off,
and end on a call to action. Stories carry generic progress segments at the top, the way stories are watched.
"""

from __future__ import annotations

from kit import (Box, bg, bg_gradient, centered, circle_photo, confetti, dots, effect, fill, flash, framed, glow,
                 gradient, grain, keys, kb, label, line, math, no_stroke, outline, photo_bg, pill, pop, random, ring,
                 rrect, shade_bottom, shade_full, shade_top, shadow, slide_in, song, spike, stroke, tall, tanim, vignette,
                 wide)


def _maker(fn, spec, module):
    def maker():
        return fn(spec)
    maker.__module__ = module
    maker.__name__ = spec["id"].replace("-", "_")
    return maker


def _hook(t, spec, box, at=0.0, size=None, style=None, dur=None):
    """The first-second hook: a slam-in line with a box, an outline or a highlight."""
    p = spec["pal"]
    style = style or spec.get("hookstyle", "box")
    f = spec.get("font", "Anton")
    sz = size or spec.get("hsize", 130)
    if style == "box":
        layers, extra = [fill(p.get("ink", "#111111"))], dict(box_bg=(p["accent"], 1.0), box_pad=22, box_radius=18)
    elif style == "outline":
        layers, extra = [shadow("#000000", 0, 10, 0, 0.9), stroke(10, "#111111"), fill(p["accent"])], {}
    else:
        layers, extra = [shadow("#000000", 0, 6, 24, 0.9), fill("#FFFFFF")], {}
    label(t, t.track("text", "Gancho"), spec["hook"], at, dur or (t.duration - at), box, f, sz, "#FFFFFF",
          weight=spec.get("weight", 400), line=0.98, layers=layers, anim_in=tanim("stamp", duration=0.25),
          anim_out=tanim("fade", duration=0.2) if dur else None, name="Gancho", **extra)


def _segments(t, n, each, y=40):
    """Generic story progress bars along the top."""
    w = (1080 - 80 - (n - 1) * 10) / n
    for i in range(n):
        x = 40 + i * (w + 10)
        t.solid(t.track("shape", "Progreso"), "#FFFFFF", 0, t.duration, Box(x, y, w, 8), radius=4, kind="rounded-rectangle",
                alpha=0.35)
        t.solid(t.track("shape", "Progreso"), "#FFFFFF", i * each, t.duration - i * each, Box(x, y, w, 8),
                [(0, {"sx": 0.0, "dx": -w / 2}, "linear"), (each, {})], radius=4, kind="rounded-rectangle")


def _cta_tall(t, spec, at, y=1640):
    p = spec["pal"]
    if not spec.get("cta"):
        return
    pill(t, t.track("shape", "Botón"), p["accent"], at, t.duration - at, Box(190, y, 700, 130), pop(0, 0.4))
    label(t, t.track("text", "Botón"), spec["cta"], at, t.duration - at, Box(190, y, 700, 130), spec.get("body", "Montserrat"),
          50, p.get("ink", "#111111"), weight=800, anim_loop=tanim("pulse", amount=4, speed=1.3), name="Llamada")
    label(t, t.track("text", "Flecha"), "↑", at + 0.2, t.duration - at - 0.2, centered(540, y + 200, 100, 100), "Inter", 80,
          "#FFFFFF", weight=900, editable=False, anim_loop=tanim("float", amount=0.3, speed=1.4))


# --- Stories, 15 s ----------------------------------------------------------------------------------

def story(spec):
    """Hook over the first photo, then a slide per photo with its caption, a call to action at the end."""
    t = tall(spec["id"], spec["es"], spec["en"], "story15", 15.0, order=spec["order"],
             tags=["historia", "15 segundos", "stories"] + spec["tags"], thumb_at=spec.get("thumb", 0.8),
             background=spec["pal"]["bg"])
    p = spec["pal"]
    photos = spec["photos"]
    n = len(photos)
    each = 15.0 / n
    card = spec.get("layout") == "card"
    if card:
        bg_gradient(t, [(0, p["bg"]), (1, p.get("bg2", p["bg"]))], angle=135)
    box = Box(60, 150, 960, 1180) if card else t.full
    v = t.track("video", "Fotos")
    prev = None
    for i, s in enumerate(photos):
        at = i * each
        d = each + (0.3 if i < n - 1 else 0)
        clip = t.photo(v, s, at, min(d, 15.0 - at), box, kb(d, 1.08, 1.0) if i % 2 else kb(d, 1.0, 1.08),
                       label=f"Foto {i + 1}")
        if prev:
            t.transition(v, prev, clip, spec.get("trans", "slide_left"), 0.3)
        prev = clip
    if card:
        outline(t, t.track("shape", "Marco"), "#FFFFFF", 12, 0, 15.0, Box(54, 144, 972, 1192), radius=12)
    else:
        shade_bottom(t, 760, 0.7)
        shade_top(t, 260, 0.45)
    if spec.get("numbers"):
        for i in range(1, n - 1 if spec.get("cta") else n):
            label(t, t.track("text", "Número"), str(i), i * each + 0.1, each - 0.3, Box(60, 180, 400, 360), "Anton", 340,
                  p["accent"], weight=400, align="left", editable=False,
                  layers=[shadow("#000000", 0, 10, 0, 0.9), stroke(8, "#111111"), fill(p["accent"])],
                  anim_in=tanim("stamp", duration=0.25))
    _segments(t, n, each)
    flash(t, 0.0, 0.2, peak=0.7)
    _hook(t, spec, Box(60, 640, 960, 480), at=0.0, dur=each - 0.2)
    caps = spec.get("caps") or []
    for i, c in enumerate(caps):
        at = (i + 1) * each + 0.2 if spec.get("hook_first_slide", True) else i * each + 0.2
        if at >= 15.0:
            break
        label(t, t.track("text", "Pie"), c, at, each - 0.4, Box(70, 1320, 940, 260), spec.get("body", "Montserrat"), 72, "#FFFFFF",
              weight=800, line=1.1, layers=[shadow("#000000", 0, 4, 16, 0.7), fill("#FFFFFF")],
              anim_in=tanim("rise-by-word", duration=0.35, unit="word", stagger=0.06), anim_out=tanim("fade", duration=0.2),
              name=f"Pie {i + 1}")
    _cta_tall(t, spec, 15.0 - each + 0.4)
    if spec.get("deco") == "confetti":
        confetti(t, [p["accent"], "#FFFFFF", p.get("accent2", "#FFFFFF")], 15.0 - each, each, seed=spec["order"], lanes=3,
                 density=0.3)
    t.adjust([effect("zoom_pulse", animated={"punch": spike([each * k for k in range(1, n)], 0.3, 0.25)})], name="Golpe")
    song(t, spec.get("mood", "upbeat"), spec.get("pick", 0), 0.85)
    return t


# --- Ads, 6 s ---------------------------------------------------------------------------------------

def ad(spec):
    """0-2 s hook, 2-4 s the message (product, price or benefit), 4-6 s brand and call to action."""
    is_wide = spec.get("wide", False)
    mk = wide if is_wide else tall
    p = spec["pal"]
    t = mk(spec["id"], spec["es"], spec["en"], "ad6", 6.0, order=spec["order"],
           tags=["anuncio", "6 segundos", "publicidad"] + spec["tags"], thumb_at=spec.get("thumb", 3.0), background=p["bg"])
    W, H = t.w, t.h
    style = spec.get("style", "punch")
    # 0-2 s: hook
    t.photo(t.track("video", "Gancho"), spec["photos"][0], 0, 2.2, t.full, [(0, {"s": 1.25}, "snap"), (0.3, {"s": 1.05}, "linear"),
                                                                          (2.2, {"s": 1.0})], label="Foto del gancho")
    shade_full(t, 0.35, 0, 2.2)
    hb = Box(60, H * 0.30, W - 120, H * 0.4)
    _hook(t, spec, hb, at=0.0, size=spec.get("hsize", 150 if not is_wide else 170), dur=2.0)
    t.solid(t.track("shape", "Corte"), "#FFFFFF", 1.95, 0.25, opacity=keys([(0, 0.0), (0.12, 0.9), (0.25, 0.0)]))
    # 2-4 s: message
    bg_box = Box(0, 0, W, H)
    t.solid(t.track("shape", "Fondo"), p["bg"], 2.0, 4.0, bg_box,
            [(0, {"dx": W}, "out"), (0.3, {})] if style != "reveal" else None)
    if is_wide:
        pb = Box(80, 140, 860, 800)
        tb = Box(1000, 260, 860, 520)
    else:
        pb = Box(150, 240, 780, 840)
        tb = Box(70, 1120, 940, 480)
    framed(t, spec["photos"][1] if len(spec["photos"]) > 1 else spec["photos"][0], 2.1, 3.9, pb,
           [(0, {"s": 0.7}, "back"), (0.4, {}, "linear"), (3.9, {"s": 1.04})], border=0, radius=40, label="Foto del producto",
           reuse=None if len(spec["photos"]) > 1 else "p1")
    label(t, t.track("text", "Mensaje"), spec["msg"], 2.3, 3.7, Box(tb.x, tb.y, tb.w, tb.h * 0.55), spec.get("font", "Anton"),
          spec.get("msize", 110 if len(spec["msg"]) <= 20 else 92), p["fg"], weight=spec.get("weight", 400), align="left" if is_wide else "center", line=1.0,
          anim_in=tanim("slide-up", duration=0.3, unit="word", stagger=0.08), name="Mensaje")
    if spec.get("price"):
        cx = tb.x + (180 if is_wide else tb.w / 2)
        cy = tb.y + tb.h * 0.8
        t.solid(t.track("shape", "Precio"), p["accent"], 2.6, 3.4, centered(cx, cy, 340, 180), pop(0, 0.35), radius=90,
                kind="rounded-rectangle")
        label(t, t.track("text", "Precio"), spec["price"], 2.65, 3.35, centered(cx, cy, 340, 180), "Anton", 110,
              p.get("ink", "#111111"), weight=400, anim_in=tanim("stamp", duration=0.25), name="Precio")
    # 4-6 s: brand and call to action
    t.solid(t.track("shape", "Cierre"), p["accent"], 4.0, 2.0, bg_box, [(0, {"dy": H}, "out"), (0.3, {})])
    lg = centered(W / 2, H * (0.35 if not is_wide else 0.33), 300, 300)
    t.photo(t.track("video", "Logo"), spec.get("logo", "logo-06"), 4.3, 1.7, lg, pop(0, 0.4), label="Tu logo")
    label(t, t.track("text", "Marca"), spec["brand"], 4.4, 1.6, Box(60, H * 0.53, W - 120, 140), spec.get("body", "Montserrat"),
          90 if not is_wide else 96, p.get("ink", "#111111"), weight=900, anim_in=tanim("fade", duration=0.3), name="Marca")
    pill(t, t.track("shape", "Botón"), p.get("ink", "#111111"), 4.6, 1.4, centered(W / 2, H * 0.7, 640, 130), pop(0, 0.35))
    label(t, t.track("text", "Botón"), spec["cta"], 4.6, 1.4, centered(W / 2, H * 0.7, 640, 130), spec.get("body", "Montserrat"),
          52, p["accent"], weight=800, anim_loop=tanim("pulse", amount=4, speed=1.4), name="Llamada")
    t.adjust([effect("zoom_pulse", animated={"punch": spike([0.0, 2.0, 4.0], 0.45, 0.3)}),
              effect("beat_shake", animated={"amount": spike([0.0], 0.6, 0.3)})], name="Golpes")
    song(t, spec.get("mood", "electro"), spec.get("pick", 0), 0.9)
    return t


# --- Video thumbnails (1920x1080, almost still) ---------------------------------------------------

def _big(t, text, box, font, size, colour, at=0.0, outline_c="#000000", rot=0, name="Texto", box_bg=None, weight=400):
    label(t, t.track("text", name), text, at, t.duration - at, box, font, size, colour, weight=weight, line=0.92,
          layers=[shadow(outline_c, 0, 12, 0, 1.0), stroke(14, outline_c), fill(colour)] if not box_bg else [fill(colour)],
          box_bg=box_bg, box_pad=20, box_radius=14, anim_in=tanim("pop", duration=0.25), rotation=keys([(0, rot)]), name=name)


def thumb(spec):
    """A still, bold frame meant to be exported as a picture: face, few words, high contrast."""
    t = wide(spec["id"], spec["es"], spec["en"], "thumbnail", 3.0, order=spec["order"],
             tags=["miniatura", "portada de video", "thumbnail"] + spec["tags"], thumb_at=2.2, background=spec["pal"]["bg"])
    p = spec["pal"]
    kind = spec.get("kind", "face")
    font = spec.get("font", "Luckiest Guy")
    if spec.get("bgphoto"):
        t.photo(t.track("video", "Fondo"), spec["bgphoto"], 0, 3.0, t.full, label="Fondo",
                effects=[effect("color.basic", saturation=0.25, contrast=0.2)] + (
                    [effect("builtin.effects.gaussian_blur", u_blurRadius=10)] if spec.get("blurbg") else []))
        if spec.get("dim"):
            shade_full(t, spec["dim"], colour=p["bg"])
    else:
        bg_gradient(t, [(0, p["bg"]), (1, p.get("bg2", p["bg"]))], angle=spec.get("angle", 120))
    if kind == "face":
        face = Box(1080, 60, 820, 1020) if spec.get("side", "right") == "right" else Box(20, 60, 820, 1020)
        t.photo(t.track("video", "Cara"), spec["face"], 0, 3.0, face, label="Tu cara (recortada)",
                effects=[effect("color.basic", saturation=0.2, contrast=0.15)])
        tx = 60 if spec.get("side", "right") == "right" else 860
        _big(t, spec["text"], Box(tx, 140, 1000, 560), font, spec.get("size", 200), p["accent"], rot=spec.get("rot", -3))
        if spec.get("text2"):
            _big(t, spec["text2"], Box(tx, 700, 1000, 260), font, spec.get("size2", 130), "#FFFFFF", at=0.1,
                 rot=spec.get("rot", -3), name="Texto 2", box_bg=(p.get("accent2", "#111111"), 1.0) if spec.get("boxed") else None)
    elif kind == "vs":
        for i, s in enumerate(spec["photos"][:2]):
            t.photo(t.track("video", f"Opción {i + 1}"), s, 0, 3.0, Box(i * 960, 0, 960, 1080), label=f"Opción {i + 1}")
        t.solid(t.track("shape", "Divisor"), "#FFFFFF", 0, 3.0, Box(950, 0, 20, 1080))
        t.solid(t.track("shape", "VS"), p["accent"], 0, 3.0, centered(960, 540, 300, 300), pop(0, 0.3), kind="ellipse",
                layers=[shadow("#000000", 0, 10, 20, 0.6), fill(p["accent"]), stroke(10, "#FFFFFF")])
        _big(t, "VS", centered(960, 545, 300, 260), font, 150, "#FFFFFF", name="VS")
        _big(t, spec["text"], Box(60, 760, 1800, 280), font, spec.get("size", 160), "#FFFFFF")
    elif kind == "beforeafter":
        for i, s in enumerate(spec["photos"][:2]):
            box = Box(40 + i * 960, 160, 880, 760)
            t.solid(t.track("shape", "Marco"), "#FFFFFF", 0, 3.0, Box(box.x - 12, box.y - 12, box.w + 24, box.h + 24),
                    radius=28, kind="rounded-rectangle", layers=[shadow("#000000", 0, 12, 24, 0.5), fill("#FFFFFF"), no_stroke()],
                    rotation=keys([(0, -2 if i == 0 else 2)]))
            t.photo(t.track("video", f"Foto {i + 1}"), s, 0, 3.0, box, label=["Antes", "Después"][i],
                    rotation=keys([(0, -2 if i == 0 else 2)]),
                    effects=[effect("color.basic", saturation=-0.6)] if i == 0 else [])
        _big(t, "➜", centered(960, 540, 300, 300), "Inter", 260, p["accent"], name="Flecha", weight=900)
        _big(t, spec.get("l1", "ANTES"), Box(60, 30, 860, 160), font, 120, "#FFFFFF", name="Etiqueta 1")
        _big(t, spec.get("l2", "DESPUÉS"), Box(1000, 30, 860, 160), font, 120, p["accent"], name="Etiqueta 2")
        if spec.get("text"):
            _big(t, spec["text"], Box(60, 900, 1800, 170), font, 120, "#FFFFFF", box_bg=(p.get("accent2", "#111111"), 1.0),
                 name="Texto")
    elif kind == "number":
        face = Box(1160, 120, 720, 960)
        t.photo(t.track("video", "Cara"), spec["face"], 0, 3.0, face, label="Tu cara (recortada)")
        _big(t, spec["number"], Box(40, 60, 1150, 620), font, spec.get("nsize", 420), p["accent"], rot=-4, name="Número")
        _big(t, spec["text"], Box(60, 690, 1100, 300), font, spec.get("size", 150), "#FFFFFF", rot=-4)
    elif kind == "reaction":
        circle_photo(t, spec["face"], 0, 3.0, centered(1600, 760, 520, 520), pop(0, 0.3), ring_colour=p["accent"],
                     ring_width=18, label="Tu cara")
        label(t, t.track("text", "Emoji"), spec.get("emoji", "😱"), 0, 3.0, centered(1780, 470, 260, 260), "Inter", 200,
              "#000000", editable=False, motion=pop(0, 0.3))
        _big(t, spec["text"], Box(60, 640, 1300, 400), font, spec.get("size", 170), "#FFFFFF", rot=-3)
        if spec.get("circle"):
            ring(t, t.track("shape", "Círculo"), p["accent"], 16, 0, 3.0, centered(*spec["circle"], 360, 360), pop(0, 0.3))
    elif kind == "list":
        _big(t, spec["number"], Box(60, 80, 760, 640), font, spec.get("nsize", 460), p["accent"], rot=-4, name="Número")
        _big(t, spec["text"], Box(60, 700, 820, 320), font, spec.get("size", 130), "#FFFFFF", rot=-4)
        for i, s in enumerate(spec["photos"][:3]):
            box = Box(900 + (i % 2) * 500, 80 + i * 300, 460, 440)
            t.solid(t.track("shape", "Marco"), "#FFFFFF", 0, 3.0, Box(box.x - 10, box.y - 10, box.w + 20, box.h + 20),
                    rotation=keys([(0, (-1) ** i * 5)]), layers=[shadow("#000000", 0, 10, 20, 0.5), fill("#FFFFFF"), no_stroke()])
            t.photo(t.track("video", f"Foto {i + 1}"), s, 0, 3.0, box, label=f"Foto {i + 1}", rotation=keys([(0, (-1) ** i * 5)]))
    elif kind == "question":
        # the question mark goes over the photo, so it reads whole instead of peeking out behind it
        t.photo(t.track("video", "Cara"), spec["face"], 0, 3.0, Box(820, 160, 700, 920), label="Tu cara (recortada)")
        _big(t, "?", Box(1430, 40, 470, 1000), font, 760, p["accent"], rot=12, name="Pregunta")
        _big(t, spec["text"], Box(60, 200, 900, 700), font, spec.get("size", 170), "#FFFFFF", rot=-3)
    if spec.get("badge"):
        pill(t, t.track("shape", "Insignia"), p.get("accent2", "#111111"), 0, 3.0, Box(60, 60, 380, 110), pop(0, 0.3),
             rotation=keys([(0, -6)]))
        label(t, t.track("text", "Insignia"), spec["badge"], 0, 3.0, Box(60, 60, 380, 110), font, 70, "#FFFFFF", weight=400,
              rotation=keys([(0, -6)]), name="Insignia")
    if spec.get("arrow"):
        ax, ay, ang = spec["arrow"]
        label(t, t.track("text", "Flecha"), "➜", 0, 3.0, centered(ax, ay, 360, 300), "Inter", 280, p["accent"], weight=900,
              editable=False, layers=[shadow("#000000", 0, 8, 0, 1.0), stroke(12, "#000000"), fill(p["accent"])],
              rotation=keys([(0, ang)]), motion=pop(0, 0.3))
    return t
