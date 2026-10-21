"""Shared helpers for Stock › Tendencias: the trending title looks of 2026 (Filmora's and CapCut's
"Trending" text galleries, studied from screenshots), rebuilt as our own designs.

Every design is a `Style` (kit.py) in the "tendencias" category with its In / Out / Loop motion from
the app's built-in presets (presets/text-animations), so it works in any installed app with no
extra download. Samples are our own words: no brand names, film titles or logos.
"""

from __future__ import annotations

import re

from kit import Style, tslot

# The built-in presets a slot may name (presets/text-animations/*.json) and the slots each supports.
BUILTIN = {
    "blur-in-words": "io", "blur-in": "io", "bounce": "io", "breathe": "l", "color-wave": "i",
    "colour-pulse": "l", "converge": "io", "drop": "i", "fade-scale": "o", "fade-shift": "o",
    "fade-up-char": "io", "fade": "io", "fall": "o", "flicker-in": "i", "flicker": "l", "flip": "io",
    "float": "l", "glitch-in": "io", "jitter": "l", "karaoke-bounce": "l", "karaoke-pop": "l", "pop": "io",
    "pulse": "l", "rain": "io", "remove-by-word": "o", "rise-by-word": "io", "rise": "io", "shrink": "o",
    "skew-slide": "io", "slide-down": "io", "slide-left": "io", "slide-right": "io", "slide-up": "io",
    "slow-zoom": "l", "snap-together": "i", "spin-in": "io", "squash": "i", "stamp": "i", "sway": "l",
    "swing": "l", "tracking-drift": "l", "type-on-blur": "io", "typewriter": "io", "wave": "l", "wipe": "io",
    "zoom-in": "io", "zoom-out": "io",
}

FADE_OUT = tslot("fade", 0.3, "easeIn")


def mark_words(text: str) -> str:
    """The engine marks words one at a time (`*POR* *VER!*`): a span over several words
    (`*POR VER!*`) would show its asterisks, so each word of a span gets its own pair."""
    def split(m: re.Match) -> str:
        return re.sub(r"\S+", lambda w: f"*{w.group(0)}*", m.group(1))
    return re.sub(r"(?<!\S)\*(\S[^*]*\s[^*]*\S)\*(?![^\s.,;:!?¡¿)\]])", split, text)


def trend(id: str, es: str, en: str, sample: tuple[str, str], font: str, size: int, weight: int, layers: list,
          *, anim_in=None, anim_out=FADE_OUT, anim_loop=None, tags=(), **kw) -> Style:
    """A Tendencias title. `id` gets the "tend-" prefix; sizes are project px on a 1080 x 1920 reel."""
    sample = (mark_words(sample[0]), mark_words(sample[1]))
    return Style(f"tend-{id}", es, en, "tendencias", sample, font, size, weight, layers, anim_in=anim_in,
                 anim_out=anim_out, anim_loop=anim_loop, tags=["tendencias", "trending", "titulo", *tags], **kw)


def check_slots(styles: list[Style]) -> list[str]:
    """Every slot names a built-in preset that supports it."""
    problems = []
    for st in styles:
        for slot, value, code in (("in", st.anim_in, "i"), ("out", st.anim_out, "o"), ("loop", st.anim_loop, "l")):
            if not value:
                continue
            preset = value.get("preset", "")
            if preset not in BUILTIN:
                problems.append(f"{st.id}: {slot} names unknown preset {preset!r}")
            elif code not in BUILTIN[preset]:
                problems.append(f"{st.id}: preset {preset} has no {slot} slot")
    return problems
