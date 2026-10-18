"""Shared building blocks for the 2026-10-16 batches (templates_h*.py, 16:9; templates_r6+.py, 9:16).

Everything here reads the template's own size (t.w, t.h), so one helper serves both formats. Times in
seconds, boxes in project pixels; tracks are still added bottom-up (see scene.py).
"""

from __future__ import annotations

import math
import random

from scene import (SQUARE, WIDE, Box, Template, anim, beat, centered, effect, fill, glow, gradient, keys,
                   no_stroke, shadow, stroke, tanim, text_style)

__all__ = ["SQUARE", "WIDE", "Box", "Template", "anim", "beat", "centered", "effect", "fill", "glow", "gradient", "keys",
           "no_stroke", "shadow", "stroke", "tanim", "text_style", "math", "random",
           "wide", "tall", "square", "pill", "rrect", "pop", "kb", "spike", "blink", "hollow", "flash", "shade_bottom",
           "shade_top", "shade_full", "letterbox", "bg", "bg_gradient", "photo_bg", "framed", "circle_photo",
           "panels", "song", "fade_kf", "appear", "label", "line", "grain", "vignette", "dots", "confetti",
           "slides", "ring", "outline", "BLOCKED", "slide_in", "type_style"]

# Sample photos never used: a brand or logo shows (CLAUDE.md) or the scene does not travel.
BLOCKED = {"h-desk-01", "h-community-03", "h-truck-02", "h-soccer-04", "h-product-02", "h-studio-03",
           "h-gaming-04", "h-tools-01", "bakery-01", "winter-02", "spring-03", "skincare-01", "music-01",
           # reviewed by the coordinator (2026-10-16): sneaker and sportswear brands, sponsors on shirts
           "product-01", "product-02", "product-03", "product-04", "gym-03", "fashion-05", "fashion-06", "family-06",
           "barber-04", "nails-01", "skate-02", "sport-01", "sport-02", "sport-03", "restaurant-05", "restaurant-04", "box-01", "box-03", "car-01", "car-02", "car-03",
           # 0.15.0 batches (2026-10-17): Yeezy sneakers, gym machine and shirt logos, a surf-brand print
           "h-fitness-01", "h-fitness-02", "h-fitness-04", "h-fitness-05", "friends-05", "friends-06", "friends-07",
           "y4-habla-01", "y4-viral-02", "y4b-h-dog-02", "y4b-h-dog-03", "y4b-h-dog-04", "y4b-h-dance-02",
           "friends-04", "y4c-friends-02", "y4c-friends-03", "y4c-friends-04", "y4c-friends-07", "y4c-friends-08",
           "y4c-party-03", "y4c-h-gym-01", "y4c-h-gym-02", "y4c-h-gym-06", "y4c-talk-01", "y4c-talk-04", "y2b-h-gym-03",
           "y2b-h-gym-02", "y4-viral-01",
           # y2: Nike, Puma, Under Armour, logos on dumbbells, mats and gym signs
           "y2-gym-02", "y2-gym-03", "y2-gym-04", "y2-gym-05", "y2-gym-06", "y2-gym-07", "y2-gym-08", "y2-work-03",
           "y2-work-04", "y2-work-06", "y2-run-03", "y2-run-04", "y2-dish-03", "y2-fun-02", "y2-fun-05", "y2-h-gym-02",
           "y2-h-gym-03", "y2-h-gym-04", "y2-h-gym-08", "y2-h-fun-02", "y2-h-fun-03", "y2-h-fun-04", "y2b-gym-01",
           "y2b-gym-02", "y2b-gym-03", "y2b-gym-05", "y2b-fit-04", "y2b-fit-05", "y2b-fit-06", "y2b-h-gym-05", "y2b-h-fun-05",
           # y3: phones, gadgets and cameras with their maker's logo
           "y3-phone-01", "y3-phone-03", "y3-phone-04", "y3-phone-05", "y3-phone-08", "y3-gadget-01", "y3-gadget-02",
           "y3-gadget-04", "y3-gadget-05", "y3-gadget-06", "y3-cam-01", "y3-cam-03", "y3-cam-04", "y3-unbox-03",
           "y3-tablet-03",
           # y4: TV channel logos on microphones, Sennheiser, Fujifilm, shop signs, skate brands, three-stripe sneakers
           "y4-entrevista-01", "y4-entrevista-02", "y4-entrevista-04", "y4-entrevista-05", "y4-calle-05", "y4-calle-08",
           "y4-habla-02", "y4-habla-03", "y4-habla-04", "y4-viral-h-01", "y4-viral-h-02", "y4-viral-h-03", "y4-viral-h-04",
           "y4-viral-04", "y4-mic-h-01", "y4-mic-h-02", "y4-mic-h-03",
           # y5 / y6: signs, logos on clothes, race cars and gaming gear
           "y5-night-02", "y5-night-03", "y5-street-03", "y5-street-05", "y5-street-06", "y5-outfit-08", "y5-cozy-01",
           "y5-cozy-02", "y5-sci-04", "y5-h-street-02", "y5-h-street-07", "y6-oldphoto-02", "y6-h-dish-03",
           "y6-h-race-01", "y6-h-race-02", "y6-h-race-03", "y6-h-race-04", "y6-h-gamer-01", "y6-h-gamer-02", "y6-h-gamer-03",
           "y6-h-gamer-04", "y6-h-gamer-05", "y6-h-gamer-06",

           # brand audit of the old sample photos (2026-10-17): logos, signs, gear and film IP
           "barber-03", "cafe-03", "cake-03", "christmas-01", "city-02", "coffee-02", "fashion-01",
           "graduation-02", "gym-05", "gym-06", "h-cafe-02", "h-community-01", "h-desk-03", "h-desk-04",
           "h-elderly-01", "h-father-01", "h-gaming-02", "h-gaming-05", "h-graduation-04", "h-grocery-04",
           "h-newyear-02", "h-pet-01", "h-product-04", "h-shop-02", "h-shop-04", "h-soccer-02", "h-sport-05",
           "h-thanksgiving-02", "h-tools-03", "h-travel-01", "h-travel-04", "h-travel-06", "h-travel-08",
           "kids-01", "makeup-03", "music-02", "music-03", "outfit-02", "podcast-01", "puppy-02", "school-02",
           "skate-03", "sport-04", "y2-h-fun-01", "y2-h-gym-05", "y2b-gym-04"}


MOODS = {
    "upbeat": [("city-sunshine", 8), ("funshine", 4), ("fresh-focus", 2), ("inspiration", 6), ("advertime", 3),
               ("happy-whistling-ukulele", 2), ("and-just-like-that", 5), ("from-page-to-practice", 4)],
    "calm": [("infinite-peace", 0), ("adding-the-sun", 6), ("i-guess-what-i-m-trying-to-say", 4),
             ("infinite-wonder", 10), ("energizing", 8)],
    "epic": [("new-hero-in-town", 0), ("strength-of-the-titans", 2), ("honor-bound", 12), ("adventure", 4),
             ("emotional-blockbuster-2", 20), ("behind-enemy-lines", 6)],
    "cine": [("action-strike", 4), ("city-run", 0), ("dreams-of-vain", 6), ("magic-in-the-garden", 10)],
    "fun": [("llama-in-pajama", 0), ("my-giant-bunny-friend", 4), ("bebop-for-joey", 6), ("hopeful", 6),
            ("dance-of-the-tuba-plum-fairy", 0)],
    "romantic": [("piano-magic-motive", 0), ("landra-s-dream", 4), ("night-in-venice", 10), ("amazing-grace", 6),
                 ("isolation-waltz", 8)],
    "jazz": [("martini-sunset", 6), ("groovin", 4), ("funkeriffic", 8), ("fake-it-til-you-fake-it", 6)],
    "electro": [("beat-one", 0), ("backbeat", 0), ("arpent", 8), ("bit-bit-loop", 0)],
    "world": [("cumbish", 6), ("breaking-bollywood", 10), ("aquatic-city-vanished", 6), ("hillbilly-swing", 4)],
    "classic": [("the-celebrated-minuet-for-piano", 4), ("aquarium", 6), ("icicles-melting", 8)],
    "suspense": [("hidden-truth", 4), ("cursed-intro", 0), ("alien-invasion", 6), ("horroriffic", 8),
                 ("dark-hallway", 0)],
    "fantasy": [("forest-night", 6), ("one-step-closer", 4), ("brewing-potions", 4)],
}


def song(t: Template, mood: str, pick: int = 0, volume: float = 0.85) -> None:
    options = MOODS[mood]
    music_id, start = options[pick % len(options)]
    t.song(music_id, float(start), volume)


def wide(id: str, es: str, en: str, category: str, duration: float, **kw) -> Template:
    return Template(id, es, en, category, duration, size=WIDE, **kw)


def square(id: str, es: str, en: str, category: str, duration: float, **kw) -> Template:
    return Template(id, es, en, category, duration, size=SQUARE, **kw)


def tall(id: str, es: str, en: str, category: str, duration: float, **kw) -> Template:
    return Template(id, es, en, category, duration, **kw)


# --- motion --------------------------------------------------------------------------------------

def pop(at: float = 0.0, length: float = 0.45, s0: float = 0.0) -> list:
    return [(at, {"s": s0}, "back"), (at + length, {})]


def slide_in(dx: float = 0, dy: float = 0, length: float = 0.5, ease: str = "out", at: float = 0.0) -> list:
    return [(at, {"dx": dx, "dy": dy}, ease), (at + length, {})]


def kb(dur: float, s0: float = 1.0, s1: float = 1.08, **end) -> list:
    """Slow Ken Burns push."""
    return [(0, {"s": s0}, "linear"), (dur, {"s": s1, **end})]


def spike(times: list[float], peak: float, fall: float) -> dict:
    """Peaks that drop to 0 and hold (trap: the decay key must hold; the channel is 0 before the first)."""
    pts = []
    if times and times[0] > 0:
        pts.append((0.0, 0.0, "hold"))
    for at in times:
        pts += [(at, peak, "out"), (at + fall, 0.0, "hold")]
    return keys(pts)


def blink(dur: float, period: float, low: float = 0.15) -> dict:
    pts, at = [], 0.0
    while at < dur:
        pts += [(at, 1.0, "hold"), (at + period / 2, low, "hold")]
        at += period
    return keys(pts)


def fade_kf(dur: float, fin: float = 0.3, fout: float = 0.3, peak: float = 1.0) -> dict:
    """Opacity that fades in and out inside a clip of `dur`."""
    pts = [(0, 0.0, "smooth"), (fin, peak)]
    if fout:
        pts[-1] = (fin, peak, "hold") if dur - fout - fin <= 0 else (fin, peak)
        pts += [(max(fin, dur - fout), peak, "smooth"), (dur, 0.0)]
    return keys(pts)


def appear(at: float, length: float = 0.3) -> dict:
    """Opacity 0 until `at` (clip-relative), then up."""
    return keys([(0, 0.0, "hold"), (at, 0.0, "smooth"), (at + length, 1.0)]) if at > 0 else \
        keys([(0, 0.0, "smooth"), (length, 1.0)])


def hollow() -> dict:
    return {"id": "fill", "kind": "fill", "enabled": False, "paint": {"kind": "solid", "color": "#00000000"}}


# --- shapes --------------------------------------------------------------------------------------

def pill(t: Template, track, colour: str, t0: float, dur: float, box: Box, motion=None, **extra):
    return t.solid(track, colour, t0, dur, box, motion, radius=box.h / 2, kind="rounded-rectangle", **extra)


def rrect(t: Template, track, colour: str, t0: float, dur: float, box: Box, radius: float = 24, motion=None,
          layers=None, **extra):
    return t.solid(track, colour, t0, dur, box, motion, radius=radius, kind="rounded-rectangle", layers=layers,
                   **extra)


def outline(t: Template, track, colour: str, width: float, t0: float, dur: float, box: Box, motion=None, *,
            kind="rectangle", radius: float = 0, alpha: float = 1.0, **extra):
    """A hollow frame (stroke only)."""
    layers = [hollow(), {"id": "stroke", "kind": "stroke", "enabled": True, "width": width, "strokeAlign": "inside",
                         "paint": {"kind": "solid", "color": _argb(colour, alpha)}, "opacity": 1.0}]
    return t.solid(track, colour, t0, dur, box, motion, radius=radius, kind=kind, layers=layers, **extra)


def ring(t: Template, track, colour: str, width: float, t0: float, dur: float, box: Box, motion=None, **extra):
    return outline(t, track, colour, width, t0, dur, box, kind="ellipse", motion=motion, **extra)


def line(t: Template, track, colour: str, t0: float, dur: float, box: Box, grow: str = "x", length: float = 0.5,
         ease: str = "out", **extra):
    """A bar that draws itself from its left (grow="x") or top (grow="y") edge."""
    if grow == "x":
        motion = [(0, {"sx": 0.0, "dx": -box.w / 2}, ease), (length, {})]
    elif grow == "y":
        motion = [(0, {"sy": 0.0, "dy": -box.h / 2}, ease), (length, {})]
    elif grow == "c":
        motion = [(0, {"sx": 0.0}, ease), (length, {})]
    else:
        motion = None
    return t.solid(track, colour, t0, dur, box, motion, **extra)


def _argb(colour: str, alpha: float) -> str:
    return f"#{max(0, min(255, round(alpha * 255))):02x}{colour.lstrip('#').lower()[-6:]}"


def bg(t: Template, colour: str, name: str = "Fondo"):
    track = t.track("shape", name)
    t.solid(track, colour)
    return track


def bg_gradient(t: Template, stops: list[tuple], angle: float = 90.0, name: str = "Fondo"):
    track = t.track("shape", name)
    t.solid(track, stops[0][1], layers=[gradient(stops, angle=angle), no_stroke()])
    return track


def shade_bottom(t: Template, height: float, alpha: float = 0.8, t0: float = 0.0, dur: float | None = None,
                 colour: str = "#000000"):
    track = t.track("shape", "Sombra")
    t.solid(track, colour, t0, dur, Box(0, t.h - height, t.w, height),
            layers=[gradient([(0, colour, 0.0), (1, colour, alpha)], angle=90), no_stroke()])
    return track


def shade_top(t: Template, height: float, alpha: float = 0.75, t0: float = 0.0, dur: float | None = None,
              colour: str = "#000000"):
    track = t.track("shape", "Sombra")
    t.solid(track, colour, t0, dur, Box(0, 0, t.w, height),
            layers=[gradient([(0, colour, alpha), (1, colour, 0.0)], angle=90), no_stroke()])
    return track


def shade_full(t: Template, alpha: float = 0.45, t0: float = 0.0, dur: float | None = None, colour="#000000"):
    track = t.track("shape", "Oscurecer")
    t.solid(track, colour, t0, dur, alpha=alpha)
    return track


def letterbox(t: Template, ratio: float = 2.39, t0: float = 0.0, dur: float | None = None, slide: bool = True):
    """Black cinema bars for a 2.39:1 window."""
    bar = max(0.0, (t.h - t.w / ratio) / 2)
    track = t.track("shape", "Barras")
    m_top = [(0, {"dy": -bar}, "out"), (0.8, {})] if slide else None
    m_bot = [(0, {"dy": bar}, "out"), (0.8, {})] if slide else None
    t.solid(track, "#000000", t0, dur, Box(0, 0, t.w, bar), m_top)
    t.solid(t.track("shape", "Barras"), "#000000", t0, dur, Box(0, t.h - bar, t.w, bar), m_bot)
    return bar


def flash(t: Template, at: float, length: float = 0.3, colour: str = "#FFFFFF", peak: float = 0.9, track=None):
    track = track or t.track("shape", "Destello")
    t.solid(track, colour, at, length, opacity=keys([(0, peak, "out"), (length, 0.0)]))
    return track


def photo_bg(t: Template, sample: str, t0: float = 0.0, dur: float | None = None, s1: float = 1.1, label=None,
             track=None, **extra):
    dur = t.duration - t0 if dur is None else dur
    track = track or t.track("video", "Foto")
    return t.photo(track, sample, t0, dur, t.full, kb(dur, 1.0, s1), label=label, **extra)


def framed(t: Template, sample: str, t0: float, dur: float, box: Box, motion=None, *, border: float = 14,
           colour: str = "#FFFFFF", radius: float = 6, shadow_alpha: float = 0.35, rotation=None, label=None,
           reuse=None, bottom: float = 0, name: str = "Foto"):
    """A print: white border (thicker at the bottom for a Polaroid), soft shadow, the photo inside."""
    frame_box = Box(box.x - border, box.y - border, box.w + 2 * border, box.h + 2 * border + bottom)
    fm = None
    if motion:
        # The frame moves with the photo: same centre offsets and scale about its own centre.
        fm = motion
    extra = {"rotation": rotation} if rotation is not None else {}
    t.solid(t.track("shape", "Marco"), colour, t0, dur, frame_box, fm, radius=radius, kind="rounded-rectangle",
            layers=[shadow("#000000", 0, 12, 30, shadow_alpha), fill(colour), no_stroke()], **extra)
    # Scale about the frame centre means the photo drifts when bottom > 0; keep motion simple there.
    pm = motion
    if motion and bottom:
        pm = []
        for p in motion:
            s = p[1].get("s", 1.0)
            m = dict(p[1])
            m["dy"] = m.get("dy", 0.0) - bottom / 2 * (s - 1.0)
            pm.append((p[0], m) + tuple(p[2:]))
    return t.photo(t.track("video", name), sample, t0, dur, box, pm, label=label, reuse=reuse, **extra)


def circle_photo(t: Template, sample: str, t0: float, dur: float, box: Box, motion=None, *, ring_colour=None,
                 ring_width: float = 10, label=None, reuse=None):
    if ring_colour:
        r = Box(box.x - ring_width, box.y - ring_width, box.w + 2 * ring_width, box.h + 2 * ring_width)
        t.solid(t.track("shape", "Aro"), ring_colour, t0, dur, r, motion, kind="ellipse",
                layers=[shadow("#000000", 0, 10, 26, 0.3), fill(ring_colour), no_stroke()])
    track = t.track("video", "Foto")
    clip = t.photo(track, sample, t0, dur, box, motion, label=label, reuse=reuse)
    t.mask(track, clip, "ellipse")
    return clip


def panels(t: Template, colours: list[str], at: float, direction: str = "left", length: float = 0.6,
           hold: float = 0.0, stagger: float = 0.08, angle: float = 0.0):
    """Colour panels that sweep across the frame (cover, optional hold, uncover): a wipe that hides a cut."""
    for i, colour in enumerate(colours):
        track = t.track("shape", "Cortinilla")
        d = at + i * stagger
        total = length * 2 + hold
        w, h = t.w * 1.6, t.h * 1.6
        box = centered(t.w / 2, t.h / 2, w, h)
        off = {"left": (t.w * 1.6, 0), "right": (-t.w * 1.6, 0), "up": (0, t.h * 1.6), "down": (0, -t.h * 1.6)}[direction]
        motion = [(0, {"dx": off[0], "dy": off[1]}, "inout"), (length, {}, "hold" if hold else "inout"),
                  (length + hold, {}, "inout"), (total, {"dx": -off[0], "dy": -off[1]})]
        t.solid(track, colour, d, total, box, motion, rotation=keys([(0, angle)]))


def label(t: Template, track, content: str, t0: float, dur: float, box: Box, font: str, size: int, colour: str,
          *, weight: int = 700, align: str = "center", valign: str = "middle", anim_in=None, anim_out=None,
          anim_loop=None, layers=None, spacing: float = 0, line: float = 1.1, case: str = "none", motion=None,
          editable: bool = True, name=None, box_bg=None, box_pad: float = 18, box_radius: float = 0, italic=False,
          **extra):
    """A text clip with the usual knobs; `layers` replaces the plain fill."""
    style = text_style(font, size, layers or [fill(colour)], weight=weight, align=align, valign=valign,
                       spacing=spacing, line=line, case=case, anim_in=anim_in, anim_out=anim_out, anim_loop=anim_loop,
                       box=box_bg, box_pad=box_pad, box_radius=box_radius, italic=italic)
    return t.text(track, content, t0, dur, box, style, motion, label=name or content, editable=editable, **extra)


def type_style(font: str, size: int, colour: str, **kw) -> dict:
    return text_style(font, size, [fill(colour)], **kw)


def grain(t: Template, amount: float = 0.2, size: float = 1.5):
    return t.adjust([effect("stylize.film_grain", amount=amount, grainSize=size)], name="Grano")


def vignette(t: Template, amount: float = 0.5):
    return t.adjust([effect("stylize.vignette", amount=amount, softness=0.9)], name="Viñeta")


def dots(t: Template, colours: list[str], n: int, t0: float, dur: float, seed: int = 1, size=(14, 40),
         kinds=("ellipse",), drift: float = 60, area: Box | None = None, alpha: float = 1.0):
    """Little shapes that float gently: bokeh, stars, sparkles."""
    rng = random.Random(seed)
    area = area or Box(0, 0, t.w, t.h)
    track = t.track("shape", "Adornos")
    for i in range(n):
        s = rng.uniform(*size)
        x, y = rng.uniform(area.x, area.x + area.w), rng.uniform(area.y, area.y + area.h)
        start = t0 + rng.uniform(0, 0.6)
        d = dur - (start - t0)
        if d <= 0.2:
            continue
        if i and i % 6 == 0:
            track = t.track("shape", "Adornos")
        t.solid(track, rng.choice(colours), start, d, centered(x, y, s, s),
                [(0, {"s": 0.0}, "back"), (0.4, {}, "linear"), (d, {"dy": -drift * rng.uniform(0.5, 1.5)})],
                kind=rng.choice(kinds), alpha=alpha)


def confetti(t: Template, colours: list[str], t0: float, dur: float, seed: int = 3, lanes: int = 4,
             density: float = 0.4, size=(18, 40)):
    """Confetti that falls through the frame."""
    rng = random.Random(seed)
    for lane in range(lanes):
        track = t.track("shape", "Confeti")
        start = t0 + lane * density / lanes
        while start < t0 + dur - 0.5:
            s = rng.uniform(*size)
            fall = rng.uniform(2.4, 4.0)
            d = min(fall, t0 + dur - start)
            t.solid(track, rng.choice(colours), start, d, centered(rng.uniform(20, t.w - 20), -60, s, s * 0.6),
                    [(0, {}, "linear"), (fall, {"dy": t.h + 160, "dx": rng.uniform(-120, 120)})],
                    kind=rng.choice(["rectangle", "ellipse", "star"]), radius=3,
                    rotation=keys([(0, rng.uniform(0, 90)), (fall, rng.uniform(-400, 400))]))
            start += rng.uniform(density * 0.6, density * 1.4)


def slides(t: Template, samples: list[str], start: float, each: float, box: Box | None = None, *,
           transition: str | None = "crossfade", tdur: float = 0.5, kb_amount: float = 0.08, track=None,
           labels=None, alternate: bool = True, motion_fn=None, effects_fn=None):
    """Photos one after another on one track, each a slot, with Ken Burns and transitions between them."""
    box = box or t.full
    track = track or t.track("video", "Fotos")
    clips = []
    for i, sample in enumerate(samples):
        t0 = start + i * each
        d = each + (tdur if transition and i < len(samples) - 1 else 0)
        d = min(d, t.duration - t0)
        if motion_fn:
            motion = motion_fn(i, d)
        elif alternate and i % 2:
            motion = kb(d, 1.0 + kb_amount, 1.0)
        else:
            motion = kb(d, 1.0, 1.0 + kb_amount)
        extra = {}
        if effects_fn:
            extra["effects"] = effects_fn(i)
        clip = t.photo(track, sample, t0, d, box, motion, label=(labels[i] if labels else None), **extra)
        if clips and transition:
            t.transition(track, clips[-1], clip, transition, tdur)
        clips.append(clip)
    return clips
