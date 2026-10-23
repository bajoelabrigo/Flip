"""The voice effects of Efectos › Tendencias (Filmora's «Ardilla listada», «Cueva», «Walkie-talkies»…): effect
presets with only audio effects, delivered as «effect-preset» (AppController::installStockFile imports them, and
EffectBrowser applies them to the selected clip).

    py tools/effects_trends/voices.py

<out>/<id>/<id>.json      the preset (label = the Spanish name: EffectBrowser finds it again by its slug)
<out>/<id>/thumbnail.png  768 x 432 card drawn here: a waveform shaped by the voice, and its icon colour
<out>/<id>/meta.json
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from kit import CATEGORIES, OUT  # noqa: E402

# id, es, en, colour, waveform shape, audio effects (catalogId, parameters)
VOICES = [
    ("ardilla-listada", "Ardilla listada", "Chipmunk", "#f59e0b", "fast",
     [("voice.chipmunk", {"pitch": 1.6})]),
    ("corredor", "Corredor", "Hallway", "#60a5fa", "echo",
     [("space.slapback", {"delay": 45, "decay": 0.45, "in_gain": 0.8, "out_gain": 0.6})]),
    ("vinilo", "Vinilo", "Vinyl", "#d97706", "soft",
     [("texture.vinyl", {"flutter": 0.2, "highpass": 250, "lowpass": 5000, "wobble": 0.6})]),
    ("walkie-talkies", "Walkie-talkies", "Walkie-talkie", "#22c55e", "clipped",
     [("transmission.walkie", {"grit": 0.5, "low_cut": 450, "high_cut": 2800})]),
    ("cueva", "Cueva", "Cave", "#a78bfa", "echo",
     [("space.echo", {"delay": 220, "decay": 0.5, "in_gain": 0.8, "out_gain": 0.7})]),
    ("sonido-envolvente", "Sonido envolvente", "Surround sound", "#06b6d4", "wide",
     [("space.autopan", {"rate": 0.35, "amount": 0.9, "level_in": 1.0, "level_out": 1.0}),
      ("space.widen", {"drymix": 0.7, "delay": 25, "feedback": 0.3, "crossfeed": 0.3})]),
    ("profundo", "Profundo", "Deep", "#64748b", "slow",
     [("voice.deep", {"pitch": 0.68})]),
    ("fonografo", "Fonógrafo", "Phonograph", "#b45309", "soft",
     [("transmission.telephone", {"low_cut": 500, "high_cut": 2600}),
      ("texture.vinyl", {"flutter": 0.3, "highpass": 400, "lowpass": 3500, "wobble": 0.8})]),
    ("siniestra", "Siniestra", "Sinister", "#ef4444", "slow",
     [("voice.vader", {"pitch": 0.72, "echo_delay": 60, "echo_decay": 0.5, "grit": 0.45})]),
]


def hex_rgb(s: str) -> tuple[int, int, int]:
    return tuple(int(s[i:i + 2], 16) for i in (1, 3, 5))


def card(colour: str, shape: str) -> Image.Image:
    w, h = 768, 432
    c = hex_rgb(colour)
    im = Image.new("RGB", (w, h), (24, 26, 32))
    glow = Image.new("RGB", (w, h), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((w / 2 - 230, h / 2 - 170, w / 2 + 230, h / 2 + 170), fill=tuple(int(v * 0.45) for v in c))
    im = Image.blend(im, glow.filter(ImageFilter.GaussianBlur(70)), 0.6)
    d = ImageDraw.Draw(im)
    bars = 46
    for i in range(bars):
        x = 84 + i * (w - 168) / (bars - 1)
        t = i / (bars - 1)
        env = math.sin(math.pi * t) ** 0.8
        if shape == "fast":
            a = env * (0.55 + 0.45 * abs(math.sin(i * 1.9)))
        elif shape == "slow":
            a = env * (0.6 + 0.4 * math.sin(i * 0.35)) ** 2
        elif shape == "echo":
            a = sum(math.exp(-((t - p) / 0.06) ** 2) * k for p, k in ((0.25, 1.0), (0.5, 0.6), (0.72, 0.35), (0.88, 0.18)))
        elif shape == "clipped":
            a = min(0.55, env * (0.5 + 0.5 * abs(math.sin(i * 2.7))))
        elif shape == "wide":
            a = env * (0.5 + 0.5 * math.sin(i * 0.6) ** 2)
        else:  # soft
            a = env * (0.45 + 0.25 * math.sin(i * 0.9))
        a = max(0.04, min(1.0, a))
        half = a * 130
        d.rounded_rectangle((x - 4, h / 2 - half, x + 4, h / 2 + half), radius=4, fill=c)
    return im


def main() -> int:
    for vid, es, en, colour, shape, chain in VOICES:
        folder = OUT / vid
        folder.mkdir(parents=True, exist_ok=True)
        preset = {"drift": "effectStack", "version": 1, "label": es, "labels": {"es": es, "en": en},
                  "sourceDurationUs": 0, "effects": [],
                  "audioEffects": [{"name": "juce", "catalogId": cid, "parameters": params} for cid, params in chain]}
        (folder / f"{vid}.json").write_text(json.dumps(preset, ensure_ascii=False, indent=1), encoding="utf-8")
        card(colour, shape).save(folder / "thumbnail.png", optimize=True)
        meta = {"id": vid, "names": {"es": es, "en": en}, "category": "audio", "categoryNames": CATEGORIES["audio"],
                "family": "voces", "durationSec": 0, "delivery": "effect-preset",
                "tags": ["voz", "voice", "audio", "efecto de voz", "voice changer", "tendencia", "trending"],
                "width": 768, "height": 432}
        (folder / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(VOICES)} voices -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
