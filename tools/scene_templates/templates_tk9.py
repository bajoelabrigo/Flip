"""TIKTOK folder video 9 as Stock templates (tk9-*). See docs/plan-tiktok.md.

«Clean opener» (57608990.mp4, 1920×1080 at 29.97 fps): one vertical opener, one word per beat on black, white and
colour photos: letter-spaced words that close up, a band that opens over the words, a 3D flip, circle irises, photos
cut in bands or split in halves, grey flashes of the photos, twirl transitions and letters that fall. The story is
measured on the phone screen (459×888 → 1080×1920) and laid out flat; mockups, Instagram frames and the info card are
not copied. The brand at the end («envato», «envato.com») is the user's logo slot and «yourwebsite.com».
Study notes: tienda/plantillas/estudio-57608990/NOTAS.md. Built with templates_tk1.Seq (times in story seconds).
"""

from __future__ import annotations

from kit import tall
from scene import effect, gradient, no_stroke, tanim
from templates_tit_f import outline_layers
from templates_tk1 import H, M, W, Seq, argb, ease, ramp, steps


BLACK, WHITE = "#181818", "#FFFFFF"
INK = "#111111"
GREY = [effect("stylize.grayscale")]
CHEVRON = ("M 0 38 L 50 0 L 100 38 L 100 54 L 50 16 L 0 54 Z "
           "M 0 84 L 50 46 L 100 84 L 100 100 L 50 62 L 0 100 Z")


def clean():
    D = 31.3
    t = tall("tk9-limpia", "Apertura limpia: palabras y fotos al ritmo", "Clean opener: words and photos on the beat",
             "tiktok", D, order=14900, tags=["tiktok", "historia", "reels", "apertura", "tipografía", "palabras",
                                             "fotos", "minimalista"], thumb_at=10.3)
    s = Seq(t, 0.0)
    s.group("bg", "shape", "Fondo")
    s.group("foto", "video", "Foto", 7)
    s.group("band", "shape", "Franja", 2)
    s.group("txt", "text", "Texto", 3)
    s.group("fx", "shape", "Flechas", 1)
    s.group("logo", "video", "Logo", 1)

    for a, b, c in ((0.0, 0.60, BLACK), (0.60, 0.70, WHITE), (0.70, 0.90, BLACK), (0.90, 1.60, WHITE),
                    (2.50, 3.00, BLACK), (4.10, 4.50, BLACK), (6.10, 6.90, WHITE), (9.30, 9.90, WHITE),
                    (9.90, 11.60, WHITE), (12.0, 13.0, WHITE), (13.0, 13.90, BLACK), (13.90, 14.0, WHITE),
                    (16.20, 16.80, WHITE), (16.80, 17.50, BLACK), (17.50, 17.90, WHITE), (19.90, 20.70, WHITE),
                    (22.0, 23.60, WHITE), (23.60, 24.50, BLACK), (24.80, 25.30, BLACK), (25.30, 25.60, WHITE),
                    (25.60, 25.90, BLACK), (25.90, 26.20, WHITE), (26.20, 26.60, BLACK), (26.60, 27.0, WHITE),
                    (27.0, D, BLACK)):
        s.bg(a, b, c)

    def full(sample, t0, t1, label, m=None, reuse=None, fx=(), **kw):
        return s.pic(sample, t0, t1, (0, 0, W, H), m=m, label=label, reuse=reuse, fx=fx, role="cover",
                     name=label if reuse is None else f"{label} (copia)", **kw)

    def exit_blur(at, s1=1.4, dx=0.0):
        """Leaves big and blurred from second `at` of its window."""
        return lambda u, d: dict(s=1 + (s1 - 1) * ramp(u, at, 0.08), blur=14 * ramp(u, at, 0.05),
                                 dx=dx * ramp(u, at, 0.08))

    def both(*fns):
        def m(u, d):
            out = {}
            for fn in fns:
                for k_, v in fn(u, d).items():
                    out[k_] = out.get(k_, 1.0) * v if k_ == "s" else (out.get(k_, 0.0) + v if k_ in ("dx", "dy", "blur")
                                                                      else v)
            return out
        return m

    # 0.0 CLEAN in a white band that comes in from the right and closes
    band = lambda u, d: (1080 * (1 - ramp(u, 0, 0.1)), 592 + 368 * ramp(u, 0.3, 0.1),  # noqa: E731
                         1180, 1328 - 368 * ramp(u, 0.3, 0.1))
    s.rect(0.0, 0.40, band, WHITE, key="band", name="Franja", m=lambda u, d: dict(blur=6.0))
    s.word("CLEAN", 0.0, 0.40, 504, INK, angle=180, feather=120,
           m=lambda u, d: dict(wipe=100 * (1 - ramp(u, 0, 0.1)), op=1 - ramp(u, 0.33, 0.06)))
    s.word("FRESH", 0.40, 0.60, 480, WHITE)
    s.word("FRESH", 0.60, 0.70, 480, INK)
    s.word("FAST", 0.70, 0.90, 304, WHITE, lambda u, d: dict(s=steps(u, [(0, 0.53), (0.1, 1.0)]),
                                                         blur=8 if u < 0.07 else 0))
    # 0.90 FAST spaced on white, its letters flicker between solid and outline
    fsp = lambda u, d: dict(sp=0.32 + 0.22 * ramp(u, 0, 0.6))  # noqa: E731
    s.word("FAST", 0.90, 1.60, 520, INK, fsp, sp=0.32, layers=outline_layers(INK, 3), name="Contorno")
    pats = ["oo..", ".o.o", "..oo", "o.o.", ".oo.", "o..o", "oo.."]
    for i, pat in enumerate(pats):
        a = 0.90 + i * 0.1
        runs = [{"start": j, "end": j + 1, "colorEnabled": True, "color": "#00000000"}
                for j, ch in enumerate(pat) if ch == "o"]
        s.word("FAST", a, min(1.60, a + 0.1), 520, INK, lambda u, d, a=a: fsp(u + a - 0.90, d), sp=0.32, runs=runs,
               editable=(i == 0))
    # 1.60 FAST over a photo, leaves big and blurred
    full("h-beach-01", 1.60, 2.20, "Foto 1", m=lambda u, d: dict(s=1.0 + 0.05 * u / d))
    s.word("FAST", 1.60, 2.20, 440, WHITE, exit_blur(0.5, 1.7))
    # 2.20 DARE grows over a photo, then spaced and coloured on black
    full("fx-woman-05", 2.20, 2.50, "Foto 2", m=lambda u, d: dict(s=1.04 - 0.04 * u / d))
    s.word("DARE", 2.20, 2.50, 496, WHITE, lambda u, d: dict(s=steps(u, [(0, 0.52), (0.1, 0.68), (0.2, 1.0)])))
    red, ice = argb("#D3202B"), argb("#9BD9EF")
    s.word("DARE", 2.50, 3.00, 760, WHITE, exit_blur(0.4, 0.75), sp=0.4,
           runs=[{"start": i, "end": i + 1, "colorEnabled": True, "color": c} for i, c in enumerate((red, red, red, ice))])
    # 3.00 TO BREAK: the scene turns round in 3D and straightens, letters close up; a circle closes the photo
    turn = lambda u, d: -180 * (1 - ramp(u, 0.28, 0.07))  # noqa: E731  mirrored, then it turns back
    p3b = full("spring-01", 3.24, 3.38, "Foto 3", m=lambda u, d: dict(blur=24))  # behind the turn: no black edge
    p3 = full("spring-01", 3.00, 4.10, "Foto 3", reuse=p3b["placeholderId"], m=lambda u, d: dict(blur=12 * max(0.0, 1 - abs(u - 0.31) / 0.08),
                                                                    dx=-120 * (1 - ramp(u, 0, 0.25))))
    s.d3(p3, 3.00, 4.10, ry=turn)
    tb = s.word("TO BREAK", 3.00, 4.10, 840, WHITE, sp=0.12,
                m=lambda u, d: dict(sp=0.12 + 0.12 * (1 - ramp(u, 0.4, 0.3)), dx=300 * (1 - ramp(u, 0, 0.25)),
                                    blur=12 * max(0.0, 1 - abs(u - 0.31) / 0.08)))
    s.d3(tb, 3.00, 4.10, ry=turn)
    s.adjust(3.22, 3.40, [("spin_blur", {"amount": lambda u, d: 0.7 * max(0.0, 1 - abs(u - 0.09) / 0.09)},
                           dict(centerX=0.5, centerY=0.5, samples=16))])
    full("spring-01", 4.10, 4.20, "Foto 3", reuse=p3["placeholderId"], mask_shape="ellipse", feather=40,
         mask=lambda u, d: (540 - 1200 * (1 - ramp(u, 0, 0.1)), 960 - 1200 * (1 - ramp(u, 0, 0.1)),
                            540 + 1200 * (1 - ramp(u, 0, 0.1)), 960 + 1200 * (1 - ramp(u, 0, 0.1))))
    s.word("TO BREAK", 4.10, 4.50, 816, WHITE, name="Texto 2")
    # 4.50 THE: a soft circle opens on the photo; grey flash, black flash, colour again
    p4 = full("h-beach-03", 4.50, 5.90, "Foto 4", mask_shape="ellipse", feather=120,
              mask=lambda u, d: (540 - 1500 * ramp(u, 0, 0.12), 960 - 1500 * ramp(u, 0, 0.12),
                                 540 + 1500 * ramp(u, 0, 0.12), 960 + 1500 * ramp(u, 0, 0.12)))
    full("h-beach-03", 5.20, 5.40, "Foto 4", reuse=p4["placeholderId"], fx=GREY)
    s.rect(5.50, 5.60, lambda u, d: (-20, -20, W + 20, H + 20), BLACK, key="band", name="Fondo negro", role="cover")
    grow = lambda u, d, a=0.0: dict(s=0.72 + 0.28 * ramp(u + a, 0, 0.6))  # noqa: E731
    for a, b, c in ((4.50, 5.20, WHITE), (5.20, 5.40, INK), (5.40, 5.50, WHITE), (5.50, 5.60, "#1C9BD0"),
                    (5.60, 5.80, WHITE)):
        s.word("THE", a, b, 424, c, lambda u, d, a=a: grow(u, d, a - 4.50), editable=(a == 4.50))
    # 5.80 RULES: the photo comes in from the right as a band and opens
    p5 = full("fx-hair-04", 5.80, 6.10, "Foto 5",
              mask=lambda u, d: (1080 * (1 - ramp(u, 0, 0.1)), 672 - 672 * ramp(u, 0.12, 0.1), 1100,
                                 1392 + 528 * ramp(u, 0.12, 0.1)))
    s.word("RULES", 5.80, 6.10, 896, WHITE, lambda u, d: dict(dx=1000 * (1 - ramp(u, 0, 0.1))), sp=0.6, mblur=True)
    s.word("RULES", 6.10, 6.90, 936, INK, both(lambda u, d: dict(sp=0.62 - 0.47 * ramp(u, 0.05, 0.5)),
                                               exit_blur(0.7, 0.7)), sp=0.62, name="Texto 2")
    # 6.90 the red wall photo slides in; three bands; STYLE zooms out of a huge letter; grey flashes; bands
    p6 = full("nails-02", 6.90, 9.30, "Foto 6",
              m=lambda u, d: dict(dx=1080 * (1 - ramp(u, 0, 0.1)), blur=12 * (1 - ramp(u, 0, 0.1))))
    slot6 = p6["placeholderId"]
    for i, (y0, y1, grey) in enumerate(((0, 640, True), (640, 1280, False), (1280, 1920, True))):
        s.pic("nails-02", 7.20, 7.55, (0, y0, W, y1), reuse=slot6, fx=GREY if grey else (), name="Foto 6 (franja)",
              role="art")
    full("nails-02", 8.10, 8.30, "Foto 6", reuse=slot6, fx=GREY)
    for i in range(6):
        y0 = i * 320
        s.pic("nails-02", 8.40, 9.30, (0, y0, W, y0 + 320), reuse=slot6, fx=GREY if i % 2 else (),
              name="Foto 6 (franja)", role="art", m=lambda u, d: dict(blur=12 * ramp(u, 0.8, 0.08)))
    zoom = lambda u, d: dict(s=1 + 5 * (1 - ease(min(1.0, u / 0.2))), blur=18 * (1 - ramp(u, 0, 0.2)))  # noqa: E731
    s.word("STYLE", 7.70, 8.10, 840, WHITE, zoom)
    s.word("STYLE", 8.10, 8.20, 848, "#E0233A", editable=False)
    s.word("STYLE", 8.20, 8.40, 640, WHITE, editable=False)
    s.word("STYLE", 8.40, 9.30, 400, "#E0233A", exit_blur(0.8, 1.6), editable=False)
    # 9.30 NEW in a blue-to-pink gradient, grows and leaves to the right
    s.word("NEW", 9.30, 9.90, 496, WHITE, both(lambda u, d: dict(s=0.65 + 0.35 * ramp(u, 0, 0.45)),
                                              exit_blur(0.5, 1.0, 300)),
           layers=[gradient([(0.0, "#1E88E5"), (1.0, "#E0489A")], angle=0), no_stroke()], mblur=True)
    # 9.90 split: photo above, BRAND below; 10.90 white above with PROJECT, photo below
    inn = lambda u, d: dict(dx=1080 * (1 - ramp(u, 0, 0.1)), blur=10 * (1 - ramp(u, 0, 0.1)))  # noqa: E731
    s.pic("fx-woman-07", 9.90, 10.90, (0, 0, W, 960), m=both(inn, exit_blur(0.9, 1.0, 600)), label="Foto 7",
          name="Foto 7", role="art")
    s.word("BRAND", 9.90, 10.90, 620, "#C832C0", both(inn, exit_blur(0.9, 1.0, 600)), cy=1480, mblur=True)
    down = lambda u, d: dict(dy=80 * ramp(u, 0.5, 0.1) + 1200 * ramp(u, 0.6, 0.1),  # noqa: E731
                             blur=16 * ramp(u, 0.58, 0.05))
    s.pic("icecream-01", 10.90, 11.70, (0, 960, W, H), m=down, label="Foto 8", name="Foto 8", role="art")
    s.word("PROJECT", 10.90, 11.70, 832, "#B5002A",
           both(lambda u, d: dict(s=steps(u, [(0, 0.82), (0.1, 0.94), (0.2, 1.0), (0.3, 0.93)])), down), cy=432)
    # 11.60 MODERN: the sunset drops in; the photo shrinks to a band, grey, words spaced that close up
    p9 = full("sunset-01", 11.60, 12.10, "Foto 9", m=lambda u, d: dict(dy=-1920 * (1 - ramp(u, 0, 0.12)),
                                                                     blur=16 * (1 - ramp(u, 0, 0.12))))
    bandm = lambda u, d: (0, 440 * (1 - ramp(u, 0.45, 0.08)), W, 1920 - 440 * (1 - ramp(u, 0.45, 0.08)))  # noqa
    full("sunset-01", 12.10, 12.80, "Foto 9", reuse=p9["placeholderId"], mask=bandm)
    full("sunset-01", 12.20, 12.30, "Foto 9", reuse=p9["placeholderId"], fx=GREY,
         mask=lambda u, d: (0, 440, W, 1480))
    s.word("MODERN", 11.70, 12.20, 656, WHITE, lambda u, d: dict(s=steps(u, [(0, 0.93), (0.3, 1.0)])), cy=944)
    msp = lambda u, d: dict(sp=0.75 - 0.6 * ramp(u, 0.1, 0.3))  # noqa: E731
    s.word("MODERN", 12.20, 12.30, 880, INK, lambda u, d: msp(u, d), sp=0.15, cy=944, editable=False)
    s.word("MODERN", 12.30, 12.80, 880, WHITE, lambda u, d: msp(u + 0.1, d), sp=0.15, cy=944, editable=False)
    s.word("MODERN", 12.80, 13.00, 864, INK, cy=944, editable=False)
    # 13.0 UNIQUE: white on black; a white band opens with the word spaced in black, then it closes
    s.word("UNIQUE", 13.00, 13.30, 696, WHITE)
    s.rect(13.30, 13.90, lambda u, d: (-20, 960 - 544 * ramp(u, 0, 0.08) * (1 - ramp(u, 0.5, 0.1)), W + 20,
                                       960 + 544 * ramp(u, 0, 0.08) * (1 - ramp(u, 0.5, 0.1))),
           WHITE, key="band", name="Franja blanca", m=lambda u, d: dict(blur=10))
    s.word("UNIQUE", 13.30, 13.90, 824, INK, lambda u, d: dict(sp=0.75 - 0.6 * ramp(u, 0.1, 0.4)), sp=0.15,
           editable=False)
    s.word("UNIQUE", 13.90, 14.00, 432, INK, lambda u, d: dict(blur=6), editable=False)
    # 14.0 JUST over the dog photo; grey with yellow word; the photo in three bands; then a twirl
    p10 = full("pet-05", 14.00, 15.45, "Foto 10")
    full("pet-05", 14.50, 14.70, "Foto 10", reuse=p10["placeholderId"], fx=GREY)
    for i, (y0, y1, grey) in enumerate(((0, 640, True), (640, 1280, False), (1280, 1920, True))):
        s.pic("pet-05", 14.70, 15.45, (0, y0, W, y1), reuse=p10["placeholderId"], fx=GREY if grey else (),
              name="Foto 10 (franja)", role="art")
    s.word("JUST", 14.00, 14.50, 840, WHITE, lambda u, d: dict(sp=0.62 - 0.12 * ramp(u, 0, 0.3)), sp=0.5)
    s.word("JUST", 14.50, 14.70, 576, "#F2C21B", sp=0.3, editable=False)
    s.word("JUST", 14.70, 15.45, 440, "#F2C21B", sp=0.3, editable=False,
           m=lambda u, d: dict(rot=-25 * ramp(u, 0.55, 0.2)))
    s.adjust(15.30, 15.62, [("stylize.twirl", {"angle": lambda u, d: 340 * (1 - abs(u - 0.15) / 0.17)},
                             dict(radius=0.9, centerX=0.5, centerY=0.5)),
                            ("spin_blur", {"amount": lambda u, d: 0.8 * max(0.0, 1 - abs(u - 0.15) / 0.17)},
                             dict(centerX=0.5, centerY=0.5, samples=16))])
    # 15.45 USE over the green dog, spaced, shrinks
    full("pet-02", 15.45, 16.20, "Foto 11")
    s.word("USE", 15.45, 16.20, 560, WHITE, lambda u, d: dict(s=1.0 - 0.4 * ramp(u, 0.1, 0.55)), sp=0.3)
    s.word("THIS", 16.20, 16.80, 360, "#1ED574", lambda u, d: dict(s=0.45 + 0.55 * ramp(u, 0, 0.45)))
    s.word("TEMPLATE", 16.80, 17.40, 784, WHITE, both(lambda u, d: dict(blur=8 if u < 0.05 else 0),
                                                      exit_blur(0.5, 1.15)))
    # 17.40 a white wipe from the right; M A K E fade in letter by letter and close up
    s.rect(17.40, 17.50, lambda u, d: (1080 * (1 - ramp(u, 0, 0.1)) - 120, -20, W + 20, H + 20), WHITE, key="band",
           name="Barrido", m=lambda u, d: dict(blur=30))
    mk = s.word("MAKE", 17.45, 17.90, 392, INK, lambda u, d: dict(sp=0.65 - 0.55 * ramp(u, 0.1, 0.2)), sp=0.1)
    mk["textStyle"]["animation"] = {"in": tanim("fade", duration=0.15, unit="character", stagger=0.04,
                                                ease="easeOut", order="random")}
    p12 = full("fx-woman-04", 17.90, 18.45, "Foto 12", m=lambda u, d: dict(s=1.0 + 0.05 * u / d))
    s.word("MAKE", 17.90, 18.30, 680, WHITE, exit_blur(0.3, 1.3), editable=False)
    s.adjust(18.30, 18.60, [("stylize.twirl", {"angle": lambda u, d: -300 * (1 - abs(u - 0.15) / 0.15)},
                             dict(radius=0.9, centerX=0.5, centerY=0.5)),
                            ("spin_blur", {"amount": lambda u, d: 0.85 * max(0.0, 1 - abs(u - 0.15) / 0.15)},
                             dict(centerX=0.5, centerY=0.5, samples=16))])
    # 18.45 SPARKS over the cosmetics photo (grey first), then salmon on white; letters spread and fall
    p13 = full("skincare-03", 18.45, 19.90, "Foto 13")
    full("skincare-03", 18.45, 18.60, "Foto 13", reuse=p13["placeholderId"], fx=GREY)
    s.word("SPARKS", 18.90, 19.90, 640, WHITE, lambda u, d: dict(s=1.0 - 0.11 * ramp(u, 0.1, 0.8),
                                                             blur=10 * (1 - ramp(u, 0, 0.1))))
    sp_ = s.word("SPARKS", 19.90, 20.60, 784, "#EE7468", lambda u, d: dict(sp=0.06 + 0.3 * ramp(u, 0.2, 0.2)),
                 sp=0.06, editable=False)
    sp_["textStyle"]["animation"] = {"out": tanim("drop", duration=0.2, unit="character", stagger=0.03,
                                                  ease="easeIn", order="random")}
    # 20.60 the bubbles photo drops in (grey, then colour); CREATE comes down from the top
    p14 = full("fx-fashion-05", 20.60, 22.00, "Foto 14",
               m=lambda u, d: dict(dy=-1920 * (1 - ramp(u, 0, 0.1)), blur=18 * (1 - ramp(u, 0.15, 0.3))))
    full("fx-fashion-05", 20.60, 20.80, "Foto 14", reuse=p14["placeholderId"], fx=GREY,
         m=lambda u, d: dict(dy=-1920 * (1 - ramp(u, 0, 0.1)), blur=18))
    s.word("CREATE", 21.10, 22.00, 664, WHITE, lambda u, d: dict(dy=-480 * (1 - ramp(u, 0, 0.15)),
                                                             blur=12 * (1 - ramp(u, 0, 0.15))))
    s.word("CREATE", 22.00, 22.30, 872, "#1A6E9E", lambda u, d: dict(s=steps(u, [(0, 0.57), (0.1, 0.82), (0.2, 1.0)]),
                                                                  blur=8 if 0.05 < u < 0.1 else 0), editable=False)
    s.rect(22.30, 22.70, lambda u, d: (-20, 192 + 216 * ramp(u, 0.05, 0.08), W + 20, 1728 - 216 * ramp(u, 0.05, 0.08)),
           BLACK, key="band", name="Caja negra", role="cover")
    s.word("CREATE", 22.30, 22.70, 1150, WHITE, lambda u, d: dict(dx=-260 * u / d), sp=0.28, editable=False)
    s.word("WITH", 22.70, 23.50, 440, INK, both(lambda u, d: dict(sp=0.45 - 0.35 * ramp(u, 0, 0.4)),
                                                exit_blur(0.7, 0.8)), sp=0.1)
    # 23.50 a black wipe from the right; L O V E fade in and close up; leaves big and blurred
    s.rect(23.50, 23.60, lambda u, d: (1080 * (1 - ramp(u, 0, 0.1)) - 120, -20, W + 20, H + 20), BLACK, key="band",
           name="Barrido", m=lambda u, d: dict(blur=30))
    lv = s.word("LOVE", 23.60, 24.50, 352, WHITE, both(lambda u, d: dict(sp=0.55 - 0.45 * ramp(u, 0.1, 0.5)),
                                                       exit_blur(0.8, 2.0)), sp=0.1)
    lv["textStyle"]["animation"] = {"in": tanim("fade", duration=0.12, unit="character", stagger=0.04,
                                                ease="easeOut", order="forward")}
    full("fx-woman-06", 24.50, 24.80, "Foto 15")
    s.word("ENJOY", 24.50, 24.80, 896, "#202020", exit_blur(0.2, 0.75), sp=0.5)
    s.word("ENJOY", 24.80, 25.30, 416, WHITE, lambda u, d: dict(s=steps(u, [(0, 1.25), (0.1, 1.08), (0.2, 1.0)])),
           editable=False)
    s.word("CAN", 25.30, 25.60, 256, INK)
    s.word("DO IT", 25.60, 25.90, 352, WHITE)
    s.word("WITH", 25.90, 26.20, 408, INK)
    s.word("YOUR", 26.20, 26.60, 472, WHITE, lambda u, d: dict(s=0.93 + 0.07 * ramp(u, 0, 0.3)))
    s.word("PROMO", 26.60, 27.00, 816, INK, lambda u, d: dict(s=steps(u, [(0, 0.8), (0.1, 0.87), (0.2, 0.88),
                                                                      (0.3, 1.0)])))
    s.word("PROMO", 27.00, 27.50, 1000, WHITE, lambda u, d: dict(s=1 + 0.9 * ramp(u, 0.2, 0.25),
                                                             dx=-500 * ramp(u, 0.2, 0.25), blur=14 * ramp(u, 0.3, 0.1)),
           mblur=True, editable=False)
    # 27.50 the end card: the user's logo, the web typed under it, double arrows that beat at the bottom
    s.logo(27.50, D, (360, 740, 720, 1100), m=lambda u, d: dict(s=0.75 + 0.25 * ramp(u, 0, 0.1),
                                                                blur=10 * (1 - ramp(u, 0, 0.1))))
    url = s.word("yourwebsite.com", 27.50, D, 430, WHITE, cy=1150, font=(M, 500), name="Web")
    url["textStyle"]["animation"] = {"in": tanim("typewriter", duration=0.05, unit="character", stagger=0.06,
                                                 ease="easeOut", delay=0.2)}

    def beat(u, d):
        c = (u - 0.3) % 0.95
        if u < 0.3:
            return dict(op=0.0)
        return dict(op=ease(c / 0.15) * (1 - ramp(c, 0.55, 0.2)))
    s.rect(27.50, D, lambda u, d: (495, 1700, 585, 1800), WHITE, key="fx", name="Flechas", path=CHEVRON, m=beat)
    return t


TEMPLATES = [clean]
