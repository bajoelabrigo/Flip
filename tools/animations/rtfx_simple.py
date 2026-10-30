"""Animaciones Extremas · Simples (0.26): RTFX's «Simple» elements are flat versions of ones from the
other families — one or two tones, no glow, no shine. Ours are the same: each of our own elements
for those numbers (rtfx_energy / rtfx_liquid / rtfx_smoke / rtfx_sparks) with its glow and its
lighter tones taken off. (The simple fires are in rtfx_fire.)
"""

from __future__ import annotations

import rtfx_energy
import rtfx_liquid
import rtfx_smoke
import rtfx_sparks

# (family module, label, numbers RTFX has a Simple version of, which tone layers stay)
SETS = [
    (rtfx_energy, "Energía", "Energy", ["015", "017", "020", "021", "027", "086", "108", "114"], [0]),
    (rtfx_liquid, "Líquido", "Liquid", ["001", "003", "005", "011", "012", "014", "015", "016", "017", "020", "021",
                                        "022", "024", "025", "027", "029", "032", "033", "037", "038", "040", "056",
                                        "057", "058"], [1]),
    (rtfx_smoke, "Humo", "Smoke", ["001", "003", "011", "013", "019", "042"], [1]),
    (rtfx_sparks, "Chispas", "Sparks", ["023", "036"], [0]),
]


def simplified(module, es_family, en_family, number, keep, order):
    index = next(i for i, e in enumerate(module.ENTRIES) if e.split(" ", 1)[0] == number)
    s = module.make_one(index, module.ENTRIES[index])
    # The glow and the other tones go; what is left is flat.
    tones = [l for l in s.layers if l["nm"].startswith("tono")]
    keepers = [tones[i] for i in keep if i < len(tones)]
    s.layers = [dict(l, ind=i + 1) for i, l in enumerate(keepers)]
    base = s.id.split("-", 2)[2]
    s.id = f"ex-simple-{module.__name__.split('_')[1]}-{base}"
    s.es = f"Simple · {s.es}"
    s.en = f"Simple · {s.en}"
    s.category = "extremas-simples"
    s.order = order
    s.tags = s.tags + ["simple", "plano", "flat"]
    return s


STICKERS = []
_order = 5300
for module, es, en, numbers, keep in SETS:
    for n in numbers:
        STICKERS.append(lambda m=module, es=es, en=en, n=n, k=keep, o=_order: simplified(m, es, en, n, k, o))
        _order += 1
