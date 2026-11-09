"""INSTAGRAM folder video as Stock templates (ig14-*). See docs/plan-instagram.md.

«instagram sliders.mp4» (960×540, 30 fps, 287 s) presents an «IGTV pack»: eight slideshows (dynamic, fashion,
rhythmic, clean, epic, stomp, minimal, energy), each shown on a phone screen beside an info card. Each slideshow is one
story template (1080×1920): the 254×452 screen crop scaled ×4.25. Times in this module are TENTHS of a second of the
reference video (the numbers of the 10 fps study sheets), so every cut sits where the reference cuts. Photos are slots
filled with our samples; brand logos are the user's `logo-flip` slot. Study notes in
tienda/plantillas/estudio-instagram-sliders/NOTAS.md.
"""

from __future__ import annotations

import random

import templates_llt_f as f6
import templates_tk4 as tk4
from kit import Box, tall
from scene import effect, fill, gradient, keys, no_stroke, shadow

W, H = 1080, 1920
WHITE, BLACK = "#FFFFFF", "#000000"
M = "Montserrat"
ANTON = "Anton"
OSW = "Oswald"
f6._FILES[(ANTON, 400)] = "fonts.basic/fonts/anton/Anton-Regular.ttf"
f6._FILES[(OSW, 700)] = "fonts.basic/fonts/oswald/Oswald-Bold.ttf"
f6._FILES[(OSW, 600)] = "fonts.basic/fonts/oswald/Oswald-SemiBold.ttf"

solid = tk4.solid
outline = tk4.outline


def shade(alpha=0.35, blur=18, dy=4):
    return shadow(BLACK, 0, dy, blur, alpha)


def ghost_layers(colour=WHITE, width=2.0, alpha=0.55):
    """Outlined letters (stroke only), the background words of the epic slideshow."""
    return [{"id": "fill", "kind": "fill", "enabled": False, "paint": {"kind": "solid", "color": "#00000000"}},
            {"id": "stroke", "kind": "stroke", "enabled": True, "width": width, "strokeAlign": "outside",
             "opacity": alpha, "paint": {"kind": "solid", "color": tk4.argb(colour)}}]


class R(tk4.Reel):
    """tk4's Reel with the clock in tenths of a second of the reference video."""

    GROUPS = (("bg", "shape", "Fondo", 3), ("pic", "video", "Foto", 4), ("pic2", "video", "Foto encima", 2), ("tint", "shape", "Tinte", 2),
              ("band", "shape", "Banda", 2), ("ghost", "text", "Palabra de fondo", 2), ("word", "text", "Texto", 4),
              ("fill", "video", "Foto en las letras", 2), ("deco", "shape", "Adornos", 4), ("top", "shape", "Barrido", 2))

    def s(self, fr):
        return max(0.0, (fr - self.f0) / 10.0)

    # --- words ----------------------------------------------------------------------------------------------------
    def say(self, a, b, text, size, y=960, colour=WHITE, family=M, weight=800, x=540, sp=0.0, align="center",
            **kw):
        return self.word(a, b, text, W - 60, y, colour, weight, x=x, sp=sp, family=family, ink_size=size,
                         align=align, **kw)

    def scramble(self, a, b, text, size, seed, **kw):
        """Random letters every tenth from a to b (the «decoding» words of the rhythmic slideshow)."""
        rng = random.Random(seed)
        abc = "abcdefghijklmnopqrstuvwxyz"
        for fr in range(a, b):
            fake = "".join(c if not c.isalpha() else (rng.choice(abc).upper() if c.isupper() else rng.choice(abc))
                           for c in text)
            self.say(fr, fr + 1, fake, size, editable=False, name="Letras al azar", **kw)

    def caption(self, a, b, text, size, x, y, align, enter_glitch=True):
        """A line of condensed type on a black bar (the fashion slideshow captions)."""
        size = size * 1.3  # measured: the reference lines are 1.3x the first estimate
        # the line is centred on its own ink so it starts (left) or ends (right) at x like the reference
        ink = f6._font(OSW, 700).getlength(text) * size / 400
        cx = x + ink / 2 if align == "left" else x - ink / 2
        c = self.say(a, b, text, size, y=y, x=cx, family=OSW, weight=700)
        st = c["textStyle"]
        st.update(boxEnabled=True, boxColor="#ff0d0d0d", boxStyle="line", boxPaddingX=size * 0.14,
                  boxPaddingY=size * 0.04, boxRadius=0)
        if enter_glitch:
            self.glitch(c, a, a, 4, 0.9)
        return c

    # --- effects --------------------------------------------------------------------------------------------------
    def blur(self, clip, a, pts):
        return self.fx(clip, a, "builtin.effects.gaussian_blur", animated={"u_blurRadius": pts})

    def glitch(self, clip, a, at, n=3, k=0.85):
        return self.fx(clip, a, "digital_glitch", animated={"intensity": [(a, 0.0), (at, 0.0), (at + 0.3, k),
                                                                          (at + n, 0.0)]},
                       frequency=0.9, rgbAmount=16, blockAmount=0.8, flashAmount=0.2, seed=float(at))

    def blocks(self, clip, a, at, n=3, k=0.9):
        return self.fx(clip, a, "block_glitch", animated={"intensity": [(a, 0.0), (at, 0.0), (at + 0.3, k),
                                                                        (at + n, 0.0)]},
                       blockSize=90, shiftAmount=60, frequency=0.8, seed=float(at))

    def burst(self, a, b, sample, n=2, s0=1.45, z1=1.05, r0=45, **kw):
        """A photo that enters with a zoom burst (scale down and blur off): the radial zoom of the reference."""
        p = self.pic(a, b, sample, z=None, sc=[(a, s0), (a + n, 1.0), (b, z1)], **kw)
        self.blur(p, a, [(a, r0), (a + n, 0.0)])
        p["motionBlur"] = True
        return p

    def extend(self, clip, n):
        """Lengthens a clip by n tenths (the photo stays under the next one while it whips in)."""
        d = int(round(n * 1e5))
        clip["timelineDurationUs"] += d
        clip["srcOutUs"] += d
        end = (clip["timelineStartUs"] + clip["timelineDurationUs"]) / 1e6
        for lanes in self.lanes.values():
            for lane in lanes:
                if clip in lane[0].clips:
                    lane[1] = max(lane[1], end)
        return clip

    def whip(self, a, b, sample, prev, d, n=2, **kw):
        """A photo that whips in over the previous one (which stays under it for those n tenths): it goes on a
        photo lane above the previous photo's lane."""
        kw.pop("group", None)
        if prev is not None:
            self.extend(prev, n)
            order = self.lanes["pic"] + self.lanes["pic2"]
            idx = next(i for i, lane in enumerate(order) if prev in lane[0].clips)
            # lanes at or below the previous photo are made busy for this placement
            saved = [(lane, lane[1]) for lane in order[:idx + 1]]
            for lane, _ in saved:
                lane[1] = max(lane[1], self.s(b) + 1.0)
            group = "pic" if idx + 1 < len(self.lanes["pic"]) else "pic2"
            if group == "pic2":
                for lane in self.lanes["pic"]:
                    saved.append((lane, lane[1]))
            clip = self.pic(a, b, sample, enter=(d[0], d[1], n), group=group, **kw)
            for lane, end in saved:
                if clip not in lane[0].clips:
                    lane[1] = end
            return clip
        return self.pic(a, b, sample, enter=(d[0], d[1], n), group="pic2", **kw)

    def tint(self, a, b, colour, op, blend="overlay"):
        c = self.bg(a, b, colour, group="tint", name="Destello de color")
        c["blendMode"] = blend
        self.anim(c, a, "opacity", op)
        return c

    def flash(self, a, b, colour=WHITE):
        c = self.bg(a, b, colour, group="top", name="Destello")
        self.anim(c, a, "opacity", [(a, 0.9), (b, 0.0)])
        return c

    def columns(self, a, b, first, offs, n=4, cols=None):
        """The photo cut in vertical strips that slide in from different heights and meet (offs = dy per strip)."""
        k = len(offs)
        cols = cols or [(i * W / k, (i + 1) * W / k) for i in range(k)]
        out = []
        for (x0, x1), dy in zip(cols, offs):
            p = self.again(a, b, first, z=None, mv=[(a, 0, dy), (a + n, 0, 0)], group="pic2")
            self.strip(p, a, [(a, -20, H + 20)], x=[(a, x0, x1)])
            out.append(p)
        return out

    def mosaic(self, a, b, first, cols=3, rows=3, mirror=True):
        """The photo repeated in a grid (mirrored copies), the tile transition of the dynamic slideshow."""
        cw, ch = W / cols, H / rows
        for i in range(cols):
            for j in range(rows):
                p = self.again(a, b, first, z=None, box=Box(i * cw, j * ch, cw, ch), group="pic2")
                p["layoutRole"] = "art"
                if mirror and (i + j) % 2:
                    p["flipH"] = True

    def rings(self, a, b, cx=540, cy=1150, n=3, d0=200, d1=2400, width=7):
        """Thin white circles that open out from the middle before a cut (the arcs of the rhythmic slideshow)."""
        for i in range(n):
            at = a + i
            c = self.shape(at, b, cx, cy, d1, d1, outline(WHITE, width), kind="ellipse",
                           sc=[(at, d0 / d1), (b, 1.0)], name="Aro", op=[(at, 0.0), (at + 1, 1.0), (b, 0.0)])
            c["rotation"] = keys([(0.0, 0.0)])

    def hud(self, a, b, seed, n=3):
        """Small outlined squares with an X, the HUD marks that flicker over the epic slideshow."""
        rng = random.Random(seed)
        for i in range(n):
            at = a + rng.randint(0, max(1, b - a - 4))
            ln = rng.randint(2, 6)
            cx, cy = rng.choice((rng.uniform(90, 300), rng.uniform(780, 1000))), rng.uniform(150, 1780)
            s = rng.uniform(40, 70) if i % 2 == 0 else rng.uniform(260, 560)
            path = "M 0 0 L 100 0 L 100 100 L 0 100 Z M 0 0 L 100 100 M 100 0 L 0 100"
            c = self.shape(at, min(b, at + ln), cx, cy, s, s, outline(WHITE, 2.0), path=path, name="Marca")
            c["opacity"] = keys([(0.0, 0.7)])

    def ghost(self, a, b, text, top=True, size=120):
        """An outlined word that slides along the top or bottom edge."""
        y = 150 if top else 1790
        c = self.say(a, b, text, size, y=y, layers=ghost_layers(), editable=False, name="Palabra de fondo",
                     group="ghost", mv=[(a, -60 if top else 60, 0), (b, 60 if top else -60, 0)], sp=0.06)
        self.anim(c, a, "opacity", [(a, 0.0), (a + 2, 1.0), (b - 2, 1.0), (b, 0.0)])
        return c


def _p(id, es, en, order, dur, tags, thumb):
    t = tall(f"ig14-{id}", es, en, "instagram", round(dur, 2), order=order,
             tags=["instagram", "historia", "reels", "presentación de fotos", "slideshow"] + list(tags),
             thumb_at=thumb)
    t.layout_roles = True
    return t


# ==== 1. DYNAMIC (876–1085) ============================================================================================
def dinamica():
    f0, end = 876, 1085
    t = _p("dinamica", "Presentación dinámica: una palabra por foto", "Dynamic slideshow: one word per photo", 16700,
           (end - f0) / 10, ["dinámica", "palabras", "transiciones"], 6.0)
    r = R(t, f0)
    SZ, NAVY, PLUM = f6.fit("INTRODUCE", 945, M, 800)[0], "#1E2A4A", "#3B3366"
    SH = [shade(), fill(WHITE)]

    def w(a, b, text, **kw):
        kw.setdefault("layers", SH)
        return r.say(a, b, text, SZ, **kw)

    # white card that grows to the full photo
    r.bg(876, 903, WHITE)
    card = r.pic(876, 888, "y6-fog-03", z=None, sc=[(876, 0.62), (883, 0.72), (888, 0.8)], enter=(500, 0, 4),
                 role="art")
    w(876, 883, "IT'S")
    w(883, 886, "TIME")
    w(886, 888, "TO")
    r.say(888, 891, "INTRODUCE", SZ, colour=NAVY)
    r.again(891, 897, card, z=None, sc=[(891, 0.8), (894, 0.88), (897, 0.95)], role="art")
    w(891, 894, "YOUR")
    w(894, 897, "OWN")
    r.again(897, 900, card, z=None, sc=[(897, 1.0), (900, 1.04)])
    w(897, 900, "BRAND")
    r.say(900, 903, "BRAND", SZ, colour=PLUM)
    # swirl into the logo over a blurred sea
    sea = r.pic(903, 914, "y5-h-ocean-03", z=None, sc=[(903, 1.6), (906, 1.1), (914, 1.15)])
    r.fx(sea, 903, "spin_blur", animated={"amount": [(903, 1.0), (906, 0.25), (914, 0.2)]})
    lg = r.logo(905, 914, y=960, size=430, sc=[(905, 0.4), (907, 1.0), (914, 1.03)])
    r.blur(lg, 905, [(905, 30), (907, 0)])
    # tunnel into DYNAMIC, letters meet
    dy = r.burst(914, 931, "fx-man-02", n=4, s0=1.9, r0=60)
    r.anim(dy, 914, "rotation", [(914, 0), (920, 0), (922, -7), (924, 0)])
    w(914, 931, "DYNAMIC", sp=0.05, spread=[(914, 1.3), (918, 0.05)])
    # PROGRESSIVE: mirrored zoom that shrinks into place
    pg = r.pic(931, 949, "hike-02", z=None, sc=[(931, 1.5), (933, 1.0), (949, 1.04)])
    r.fx(pg, 931, "kaleidoscope", animated={"zoom": [(931, 0.6), (933, 1.0)], "segments": [(931, 4), (933, 4)]})
    pk = r.again(933, 949, pg, z=None, sc=[(933, 1.0), (949, 1.04)])
    w(931, 949, "PROGRESSIVE", sc=[(931, 2.8), (933, 1.0)])
    r.blur(pk, 933, [(933, 0), (949, 0)])
    # FUTURISTIC: strips from different heights + letters meet
    fu = r.pic(949, 965, "h-nature-06", z=(1.0, 1.04))
    r.columns(949, 955, fu, [900, -700, 500], n=6)
    w(949, 963, "FUTURISTIC", sp=0.05, spread=[(949, 1.0), (955, 0.05)])
    # MODERN: vertical whip, word comes down
    r.whip(963, 976, "travel-02", None, (0, -1900))
    w(964, 974, "MODERN", mv=[(964, 0, -230), (967, 0, 0)])
    # GROWING: horizontal whip
    r.whip(974, 985, "fx-skater-04", None, (1900, 0), group="pic")
    w(975, 985, "GROWING", sp=0.05, spread=[(975, 0.7), (977, 0.05)])
    # TRENDY: block glitch
    tr = r.pic(985, 997, "y5-h-ocean-01")
    r.blocks(tr, 985, 985, 3)
    w(987, 997, "TRENDY")
    # VIDEO: strips, word falls from the top
    vi = r.pic(997, 1008, "beach-03")
    r.columns(997, 1001, vi, [-900, 600, -400], n=3)
    w(997, 1008, "VIDEO", mv=[(997, 0, -780), (1001, 0, 0)])
    for a, b, word, sample in ((1008, 1011, "THE", "sunset-03"), (1011, 1014, "BEST", "h-nature-02"),
                               (1014, 1018, "WAY", "nature-04"), (1018, 1022, "TO", "h-beach-03")):
        last = r.pic(a, b, sample)
        w(a, b, word)
    # SHOW UP: side whip, then the photo breaks in blocks
    su = r.whip(1022, 1039, "portrait-08", last, (-1900, 0))
    r.blocks(su, 1022, 1030, 8, 0.6)
    w(1022, 1039, "SHOW UP", enter=(-900, 0, 2))
    r.burst(1039, 1051, "y5-h-forest-01", n=4, s0=2.0, r0=70)
    w(1039, 1051, "SHOW", sp=0.05, spread=[(1039, 1.4), (1043, 0.05)])
    yo = r.pic(1051, 1063, "y5-h-ocean-02")
    r.columns(1051, 1056, yo, [800, -900, 600], n=5)
    w(1051, 1063, "YOUR", sp=0.05, spread=[(1051, 1.2), (1056, 0.05)])
    li = r.pic(1063, 1076, "fx-woman-04", z=None, sc=[(1063, 1.0), (1076, 1.05)])
    r.mosaic(1063, 1065, li)
    w(1063, 1076, "LIFESTYLE", sp=0.05, spread=[(1063, 0.9), (1066, 0.05)])
    aw = r.pic(1076, end, "y5-h-volcano-02", z=None, sc=[(1076, 1.3), (1079, 1.0), (end, 1.03)])
    r.mosaic(1076, 1078, aw)
    w(1076, end, "AWESOME", sp=0.6, sc=[(1076, 2.6), (1079, 1.0)], spread=[(1076, 0.3), (1079, 0.6)])
    return r.finish()


# ==== 2. FASHION (1089–1362) ===========================================================================================
def moda():
    f0, end = 1089, 1360
    t = _p("moda", "Presentación de moda con frases", "Fashion slideshow with captions", 16701, (end - f0) / 10,
           ["moda", "frases", "glitch"], 3.0)
    r = R(t, f0)
    DARK = "#0B0710"

    def big(a, b, text, sample, width=620, tone=()):
        r.bg(a, b, DARK)
        wd, ph = r.photo_word(a, b, text, width, sample, family=ANTON, weight=400, z=(1.0, 1.06), tone=tone)
        wd["textStyle"]["lineHeight"] = 1.0
        r.glitch(wd, a, a, 4, 0.9)
        r.glitch(ph, a, a, 4, 0.9)
        return wd

    def cap(a, b, l1, l2, s1=150, s2=130, y1=1490, y2=1690, sx=(45, 1035)):
        r.caption(a, b, l1, s1, sx[0], y1, "left")
        r.caption(a, b, l2, s2, sx[1], y2, "right")

    big(1089, 1116, "SHOW\nYOUR\nSTYLE", "fx-fashion-04", 600)
    g = r.pic(1113, 1143, "fx-hair-02", enter=(0, -1900, 3), group="pic2")
    sp = r.again(1125, 1136, g, z=None, sc=[(1125, 1.25), (1136, 1.3)], group="pic2")
    r.strip(sp, 1125, [(1125, -20, H + 20)], x=[(1125, 640, W)])
    cap(1115, 1143, "The best way", "to be cool")
    ff = r.pic(1143, 1161, "portrait-07")
    r.tint(1159, 1161, "#FFB28A", [(1159, 0.0), (1160, 0.6), (1161, 0.6)])
    r.bg(1161, 1178, BLACK)
    r.again(1161, 1178, ff, box=Box(0, 0, 640, H), role="art")
    r.pic(1161, 1178, "fx-fashion-06", box=Box(660, 0, W - 660, H), role="art")
    cap(1145, 1176, "Feel free", "to be creative", 160, 120)
    r.flash(1176, 1178)
    r.pic(1176, 1197, "fx-fashion-04", enter=(1900, 0, 3), group="pic2")
    cap(1180, 1197, "and", "open-minded", 150, 130, sx=(240, 900))
    cu = r.pic(1197, 1203, "fx-face-06")
    r.glitch(cu, 1197, 1197, 6, 1.0)
    big(1203, 1230, "YOU\nCAN\nDO IT", "fx-woman-07", 560)
    r.pic(1228, 1239, "fx-hair-05", enter=(1900, 0, 2), group="pic2")
    r.pic(1239, 1249, "h-portrait-04")
    cap(1229, 1249, "Don't follow", "the rules", 160, 130)
    r.pic(1249, 1256, "portrait-02")
    st = r.pic(1256, 1274, "travel-10")
    r.pic(1262, 1274, "travel-05", box=Box(740, 0, W - 740, H), role="art", group="pic2")
    r.shape(1262, 1274, 730, 960, 20, H + 40, solid(BLACK), name="Divisor")
    cap(1250, 1274, "It's time", "to blow your mind", 160, 110)
    r.pic(1274, 1287, "fx-woman-03")
    r.caption(1274, 1287, "Trendy", 160, 90, 1130, "left")
    tr2 = r.caption(1276, 1287, "Displace", 130, 1000, 1350, "right")
    r.bg(1287, 1313, BLACK)
    tiles = [(Box(0, 0, 520, 640), "fx-face-04", "fx-face-03"), (Box(540, 0, 540, 660), "fx-hair-01", "portrait-01"),
             (Box(0, 670, 740, H - 670), "fx-face-03", "fx-hair-01"), (Box(760, 680, 320, H - 680), "portrait-01",
                                                                       "fx-face-04")]
    for box, s1, s2 in tiles:
        r.pic(1287, 1293, s1, box=box, role="art", enter=(0, 400, 3))
        r.pic(1293, 1313, s2, box=box, role="art")
    big(1313, 1340, "CAPTURE\nTHE\nMOMENT", "fx-woman-05", 940)
    jk = r.pic(1340, 1350, "fx-man-05")
    r.fx(jk, 1340, "kaleidoscope", animated={"zoom": [(1340, 0.6), (1342, 1.0)], "segments": [(1340, 2), (1342, 2)]})
    jk2 = r.again(1342, 1350, jk)
    r.pic(1350, end, "fx-man-04")
    cap(1342, end, "Have your", "own style", 150, 120)
    return r.finish()


# ==== 3. RHYTHMIC (1363–1583) ==========================================================================================
def ritmica():
    f0, end = 1363, 1580
    t = _p("ritmica", "Presentación rítmica con aros", "Rhythmic slideshow with rings", 16702, (end - f0) / 10,
           ["ritmo", "frases", "aros"], 5.0)
    r = R(t, f0)
    NAVY = "#1B2A47"
    SH = [shade(0.4), fill(WHITE)]

    def phrase(a, b, text, size=118, y=960, sp=0.0):
        c = r.say(a, b, text, size, y=y, weight=700, layers=SH, sp=sp)
        c["textStyle"]["animation"] = {"in": tk4.tanim("fade", duration=0.25, unit="word", stagger=0.5,
                                                       ease="easeOut")}
        return c

    r.bg(1363, 1374, WHITE)
    rd = r.say(1363, 1374, "Ready?", 70, colour=NAVY, weight=700)
    r.blur(rd, 1363, [(1372, 0), (1374, 20)])
    cp = r.burst(1374, 1378, "fx-cyber-03", n=1, s0=1.15, r0=25)
    c = r.say(1374, 1378, "Capture", 150, weight=700, layers=SH)
    r.blur(c, 1374, [(1374, 20), (1375, 0)])
    r.bg(1378, 1382, WHITE)
    r.say(1378, 1382, "Capture", 160, colour=NAVY, weight=700)
    r.again(1382, 1395, cp, z=(1.0, 1.05))
    phrase(1382, 1393, "Capture\nthe moment")
    r.rings(1387, 1394, cx=600, cy=1300)
    r.burst(1393, 1417, "y5-h-skyline-04", n=2)
    c = r.say(1395, 1402, "Keep", 160, weight=700, layers=SH, y=960)
    r.blur(c, 1395, [(1395, 20), (1396, 0)])
    phrase(1402, 1414, "Keep your\nmemories")
    r.rings(1410, 1416, cx=560, cy=1250)
    r.burst(1414, 1436, "fx-citynight-03", n=3)
    c = r.say(1417, 1424, "Share", 160, weight=700, layers=SH, y=975)
    r.blur(c, 1417, [(1417, 20), (1418, 0)])
    phrase(1424, 1436, "Share your\nmoments", y=975)
    r.rings(1433, 1438, cx=700, cy=1200)
    bc = r.burst(1436, 1445, "fx-fashion-03", n=3)
    r.say(1440, 1445, "Be creative!", 112, weight=700, layers=SH, y=975)
    r.bg(1445, 1449, WHITE)
    cc = r.say(1445, 1449, "Be creative!", 112, colour=NAVY, weight=700, y=975)
    tk4.paint(cc, [(3, 11, "#E8743B")])
    r.again(1449, 1461, bc, z=(1.0, 1.06))
    r.say(1449, 1461, "Be creative!", 140, weight=700, layers=SH, y=975)
    r.burst(1461, 1479, "night-03", n=2, r0=30)
    kw = dict(weight=700, layers=SH, y=955, sp=0.12)
    r.say(1461, 1465, "Attention\nto details", 128, **kw)
    r.scramble(1465, 1468, "Attention\nto details", 128, 1, **kw)
    r.say(1468, 1479, "Attention\nto details", 128, weight=700, layers=SH, y=955, sp=0.04)
    r.rings(1464, 1467, cx=560, cy=1250)
    r.rings(1477, 1482, cx=540, cy=1150)
    r.burst(1479, 1500, "fx-hair-01", n=4, s0=1.6)
    kw = dict(weight=700, layers=SH, y=1440, sp=0.1)
    r.say(1483, 1487, "High\nQuality", 130, **kw)
    r.scramble(1487, 1491, "High\nQuality", 130, 2, **kw)
    r.say(1491, 1500, "High\nQuality", 130, **kw)
    r.burst(1500, 1523, "fx-citynight-01", n=4, s0=1.4)
    kw = dict(weight=700, layers=SH, y=975, sp=0.1)
    r.say(1504, 1508, "Catchy\nmusic", 130, **kw)
    r.scramble(1508, 1514, "Catchy\nmusic", 130, 3, **kw)
    r.say(1514, 1523, "Catchy\nmusic", 130, **kw)
    r.rings(1507, 1511, cx=600, cy=1100)
    r.burst(1523, 1544, "fx-citynight-04", n=3)
    kw = dict(weight=700, layers=SH, y=965, sp=0.1)
    r.say(1526, 1530, "Creative\ndesign", 130, **kw)
    r.scramble(1530, 1536, "Creative\ndesign", 130, 4, **kw)
    r.say(1536, 1544, "Creative\ndesign", 130, **kw)
    r.rings(1527, 1531, cx=540, cy=1000)
    r.rings(1541, 1546, cx=500, cy=1200)
    lv = r.pic(1544, 1567, "night-04", z=(1.0, 1.05))
    r.fx(lv, 1544, "kaleidoscope", animated={"zoom": [(1544, 0.5), (1549, 1.0)], "segments": [(1544, 4), (1549, 4)]})
    r.again(1549, 1567, lv)
    kw = dict(weight=700, layers=SH, y=975)
    r.scramble(1550, 1554, "Live!", 120, 5, **kw)
    r.say(1554, 1567, "Live!", 120, **kw)
    r.rings(1563, 1568, cx=560, cy=1350)
    r.burst(1567, end, "fx-cyber-01", n=3, s0=1.5)
    kw = dict(weight=700, layers=SH, y=1145)
    r.scramble(1574, 1577, "Breathe!", 120, 6, **kw)
    r.say(1577, end, "Breathe!", 120, **kw)
    return r.finish()


# ==== 4. CLEAN (1587–1837) =============================================================================================
def limpia():
    f0, end = 1587, 1833
    t = _p("limpia", "Presentación limpia con letras grandes", "Clean slideshow with big type", 16703,
           (end - f0) / 10, ["limpia", "tipografía", "foto en las letras"], 6.3)
    r = R(t, f0)
    DK = "#071410"
    SZ = 235

    def w(a, b, text, size=SZ, **kw):
        kw.setdefault("layers", [shade(0.35), fill(WHITE)])
        return r.say(a, b, text, size, family=ANTON, weight=400, **kw)

    # two photos split by a diagonal; each half changes with a whip
    DIAG = "M 0 0 L 100 0 L 100 34 L 0 62 Z"
    bottoms = [(1587, 1595, "city-01"), (1595, 1601, "y5-h-skyline-03"), (1601, 1613, "h-city-02")]
    tops = [(1587, 1593, "fx-hair-03"), (1593, 1597, "fx-walk-04"), (1597, 1603, "fx-man-03"),
            (1603, 1613, "fx-hair-01")]
    for a, b, s in bottoms:
        r.pic(a, b, s, enter=None if a == 1587 else (0, 1600, 2))
    for a, b, s in tops:
        p = r.pic(a, b, s, enter=None if a == 1587 else (0, -1600, 2), group="pic2")
        tr = next(tr for tr in t.tracks if p in tr.clips)
        t.mask(tr, p, "path", pathData=DIAG)
        p["layoutRole"] = "art"
    # closes into a strip, then the three-line title filled with a photo
    r.band(1612, 1614, DK, [(1612, -20, H + 20), (1614, 700, 1050)])
    r.bg(1614, 1634, DK)
    wd, ph = r.photo_word(1614, 1634, "CLEAN\nMINIMAL\nSLIDESHOW", 980, "fx-citynight-06", family=ANTON, weight=400)
    wd["textStyle"]["lineHeight"] = 0.95
    r.glitch(wd, 1614, 1614, 3)
    # three horizontal bands
    r.bg(1634, 1657, DK)
    r.pic(1634, 1657, "night-01", box=Box(0, 0, W, 420), role="art", enter=(0, -500, 3))
    mid = r.pic(1634, 1657, "y5-h-skyline-05", box=Box(0, 470, W, 1000), role="art", enter=(-1100, 0, 4))
    r.pic(1634, 1657, "fx-citynight-02", box=Box(0, 1520, W, 400), role="art", enter=(0, 500, 3))
    w(1641, 1657, "THE BEST\nWAY", 215, y=960, sc=[(1641, 0.6), (1643, 1.0)])
    tc = r.burst(1657, 1669, "y5-night-01", n=1, s0=1.1, r0=10)
    w(1658, 1669, "TO BE COOL", 255, enter=(0, -300, 2), exit=(0, 300, 2))
    ca = r.whip(1669, 1686, "fx-cyber-01", tc, (0, 1900))
    w(1675, 1686, "CATCHY", sc=[(1675, 2.4), (1677, 1.0)])
    r.whip(1686, 1706, "h-city-02", ca, (0, 1900), group="pic")
    w(1686, 1706, "EXCLUSIVE", 215, spread=[(1686, 0.35), (1689, 0.0)])
    r.bg(1706, 1708, DK)
    r.pic(1708, 1725, "fx-walk-02", enter=(0, -1900, 2))
    w(1709, 1725, "UNIVERSAL", 215, mv=[(1709, 0, -230), (1712, 0, 0)])
    r.bg(1725, 1742, DK)
    r.pic(1726, 1739, "fashion-04", enter=(0, 1900, 3))
    r.pic(1739, 1743, "autumn-03", box=Box(-40, 420, W + 80, 1080), role="art", enter=(0, -900, 2))
    wd, ph = r.photo_word(1743, 1766, "YOUR\nOWN\nBRAND", 760, "fx-face-05", family=ANTON, weight=400, sp=0.12,
                          spread=[(1743, 0.12), (1749, 0.12), (1756, 0.0)])
    wd["textStyle"]["lineHeight"] = 0.95
    r.blocks(wd, 1743, 1743, 5)
    im = r.pic(1766, 1783, "fx-man-06", enter=(0, 1900, 2), group="pic2")
    w(1766, 1783, "IMPRESS", spread=[(1766, 0.35), (1770, 0.0)])
    cr = r.whip(1783, 1802, "fx-cyber-03", im, (1900, 0), group="pic")
    w(1784, 1802, "CREATE", spread=[(1784, 0.3), (1788, 0.0)])
    cl = r.whip(1802, 1823, "fx-face-04", cr, (0, -1900))
    w(1804, 1823, "CLEAN", mv=[(1804, 0, 160), (1806, 0, 0)])
    r.whip(1823, end, "fx-man-04", cl, (0, -1900), group="pic")
    w(1827, end, "BRILLIANT", 215, mv=[(1827, 0, -230), (1829, 0, 0)])
    return r.finish()


# ==== 5. EPIC (1838–2111) ==============================================================================================
def epica():
    f0, end = 1838, 2106
    t = _p("epica", "Presentación épica con glitch", "Epic slideshow with glitches", 16704, (end - f0) / 10,
           ["épica", "cinematográfica", "glitch"], 4.5)
    r = R(t, f0)
    SH = [shade(0.45), fill(WHITE)]
    SZ = 136
    GRADE = (effect("color.basic", exposure=-0.12, contrast=0.15, saturation=-0.35, temperature=-0.25, fade=0.08),)

    def w(a, b, text, y=960, **kw):
        c = r.say(a, b, text, SZ, y=y, layers=SH, **kw)
        r.blur(c, a, [(a, 18), (a + 2, 0)])
        return c

    def g(a, b, sample, gl=True, **kw):
        kw.setdefault("tone", GRADE)
        p = r.pic(a, b, sample, **kw)
        if gl:
            r.glitch(p, a, a, 3)
        return p

    bgc = r.bg(1838, 1850, "#0A1F6E", layers=tk4.grad("#1747C9", "#050A1C", 0))
    r.anim(bgc, 1838, "opacity", [(1838, 1.0)])
    red = r.bg(1846, 1850, "#7A0712", layers=tk4.grad("#C4121F", "#120205", 0), group="tint")
    r.anim(red, 1846, "opacity", [(1846, 0.0), (1847, 1.0)])
    lg = r.logo(1838, 1850, y=960, size=430)
    r.glitch(lg, 1838, 1838, 4)
    r.hud(1838, 1850, 1, 2)
    g(1850, 1859, "nature-02")
    r.ghost(1855, 1859, "CREATIVE")
    g(1859, 1865, "nature-02", gl=False)
    r.tint(1859, 1865, "#C4121F", [(1859, 0.7), (1865, 0.4)])
    g(1865, 1874, "h-travel-02", gl=False)
    w(1859, 1874, "IT'S TIME")
    r.ghost(1859, 1864, "CREATIVE", top=False)
    tb = g(1874, 1885, "hike-01")
    r.fx(tb, 1874, "motion_trail", animated={"amount": [(1874, 0.9), (1878, 0.0)]}, angle=0.25, length=0.8)
    r.tint(1878, 1885, "#6C2BD9", [(1878, 0.7), (1885, 0.2)], blend="screen")
    fw = g(1885, 1904, "y6-h-fog-02", gl=False)
    r.columns(1890, 1904, fw, [120, -60, 90], n=1)
    r.tint(1898, 1904, "#1747C9", [(1898, 0.0), (1900, 0.7), (1904, 0.5)], blend="screen")
    w(1878, 1904, "TO BLOW\nYOUR MIND", y=1320)
    r.ghost(1882, 1886, "POWER")
    r.ghost(1884, 1889, "POWER", top=False)
    g(1904, 1910, "nature-02")
    r.tint(1908, 1909, "#C13BFF", [(1908, 0.8), (1909, 0.8)], blend="screen")
    hat = g(1910, 1928, "portrait-03", gl=False)
    r.glitch(hat, 1910, 1926, 3)
    r.tint(1924, 1927, "#C4121F", [(1924, 0.7), (1927, 0.3)])
    w(1911, 1928, "IT'S TIME")
    r.ghost(1911, 1914, "UNIVERSAL")
    r.ghost(1914, 1916, "UNIVERSAL", top=False)
    r.tint(1930, 1932, "#C13BFF", [(1930, 0.8), (1932, 0.5)], blend="screen")
    g(1928, 1937, "fx-beach-04")
    g(1937, 1943, "fx-lighthouse-02", gl=False)
    g(1943, 1950, "fx-lighthouse-04", gl=False)
    sn = g(1950, 1964, "sunset-01", gl=False)
    r.bg(1950, 1964, BLACK, box=Box(-20, 0, W + 40, 60), group="band", name="Franja")
    w(1935, 1964, "TO\nINTRODUCE", y=1040)
    r.ghost(1935, 1938, "DRAMATIC")
    r.ghost(1937, 1941, "DRAMATIC", top=False)
    pr = g(1964, 1981, "fx-beach-02")
    r.tint(1971, 1973, "#1747C9", [(1971, 0.7), (1973, 0.4)], blend="screen")
    r.tint(1973, 1979, "#C4121F", [(1973, 0.7), (1979, 0.5)])
    g(1981, 1994, "fx-face-04", gl=False)
    w(1971, 1994, "YOUR OWN\nBRAND", y=1500)
    r.ghost(1971, 1973, "EPIC")
    r.ghost(1973, 1976, "EPIC", top=False)
    mb = g(1994, 2021, "fx-couple-02")
    r.tint(1997, 2000, "#C13BFF", [(1997, 0.7), (2000, 0.3)], blend="screen")
    r.tint(2018, 2021, "#1747C9", [(2018, 0.6), (2021, 0.5)], blend="screen")
    g(2021, 2024, "fx-car-01", gl=False)
    w(2003, 2024, "CAPTURE\nTHE\nMOMENT", y=1250)
    r.ghost(2011, 2014, "ADVENTURE")
    r.ghost(2012, 2016, "ADVENTURE", top=False)
    g(2024, 2034, "fx-hair-04")
    r.tint(2026, 2027, "#C13BFF", [(2026, 0.8), (2027, 0.8)], blend="screen")
    km = g(2034, 2052, "fx-beach-01", gl=False)
    r.fx(km, 2034, "rgb_split", animated={"amount": [(2034, 0), (2036, 26), (2038, 0)]}, angle=0)
    r.columns(2038, 2052, km, [60, -40, 30], n=1)
    g(2052, 2056, "fx-figure-06", gl=False)
    w(2029, 2056, "KEEP YOUR\nMEMORIES", y=1100)
    r.ghost(2030, 2034, "GORGEOUS")
    r.ghost(2032, 2035, "GORGEOUS", top=False)
    g(2056, 2072, "travel-01")
    r.tint(2059, 2060, "#C13BFF", [(2059, 0.8), (2060, 0.8)], blend="screen")
    fc = g(2072, 2087, "fx-face-06", gl=False)
    r.tint(2077, 2080, "#C4121F", [(2077, 0.6), (2080, 0.3)])
    sy = w(2062, 2087, "SHARE\nYOUR\nBEST", y=1020)
    r.glitch(sy, 2062, 2084, 3)
    r.ghost(2062, 2065, "SHOWREEL")
    r.ghost(2065, 2067, "SHOWREEL", top=False)
    g(2087, 2093, "fx-beach-04")
    r.tint(2090, 2091, "#C13BFF", [(2090, 0.8), (2091, 0.8)], blend="screen")
    g(2093, end, "fx-couple-04", gl=False)
    w(2093, end, "LIFESTYLE\n& FEELINGS", y=1150)
    r.ghost(2093, 2096, "BRILLIANT")
    r.ghost(2096, 2098, "BRILLIANT", top=False)
    for a, b, seed in ((1850, 1880, 2), (1880, 1930, 3), (1930, 1990, 4), (1990, 2050, 5), (2050, end, 6)):
        r.hud(a, b, seed, 4)
    return r.finish()


# ==== 6. STOMP (2113–2314) =============================================================================================
def stomp():
    f0, end = 2113, 2312
    t = _p("stomp", "Presentación stomp: una palabra por golpe", "Stomp slideshow: one word per beat", 16705,
           (end - f0) / 10, ["stomp", "ritmo", "palabras"], 3.7)
    r = R(t, f0)
    SZ = 150
    SH = [shade(0.3), fill(WHITE)]
    sky = r.pic(2113, 2125, "nature-06", z=(1.0, 1.04), enter=(700, 0, 3))
    r.logo(2113, 2125, y=960, size=430, enter=(700, 0, 3))

    def beat(a, b, word, sample, size=SZ, y=960):
        r.burst(a, b, sample, n=1, s0=1.4, r0=50)
        c = r.say(a, b, word, size, y=y, layers=SH)
        r.blur(c, a, [(a, 16), (a + 1, 0)])

    def white(a, b, word, sample, size=SZ + 10):
        r.bg(a, b, WHITE)
        wd, ph = r.photo_word(a, b, word, 100, sample, ink_size=size, weight=800, z=(1.0, 1.0))

    beat(2125, 2129, "DO", "travel-02")
    beat(2129, 2132, "YOU", "y6-fog-03")
    white(2132, 2137, "YOU", "y6-fog-03")
    beat(2137, 2141, "WANT", "fx-skater-02")
    beat(2141, 2146, "TO", "nature-06")
    white(2146, 2149, "TO", "sunset-04")
    beat(2149, 2153, "CAPTURE", "h-beach-05")
    beat(2153, 2158, "THE", "nature-03")
    white(2158, 2161, "THE", "nature-03")
    beat(2161, 2165, "MOMENT", "y5-h-ocean-03")
    beat(2165, 2170, "SHARE", "autumn-02")
    white(2170, 2173, "SHARE", "y5-h-volcano-02")
    beat(2173, 2177, "YOUR", "fx-couple-04")
    beat(2177, 2180, "BEST", "hike-02")
    white(2180, 2185, "BEST", "travel-02")
    beat(2185, 2189, "MEMORIES", "nature-01")
    beat(2189, 2192, "KEEP", "h-beach-04")
    white(2192, 2197, "KEEP", "h-beach-05")
    beat(2197, 2201, "YOUR", "travel-01")
    beat(2201, 2206, "BEST", "fx-nature-01")
    white(2206, 2209, "BEST", "h-nature-06")
    beat(2209, 2213, "MOMENTS", "fx-hair-02")
    beat(2213, 2221, "RIGHT\nNOW", "h-nature-04", size=140)
    runs = [("JUST", [2221, 2223, 2226, 2229, 2231, 2233],
             ["h-nature-01", "y5-h-volcano-01", "y6-h-fog-03", "autumn-01", "sunset-02"]),
            ("USE", [2233, 2235, 2238, 2240, 2242, 2245],
             ["y5-h-ocean-03", "fx-beach-02", "nature-04", "sunset-01", "travel-02"]),
            ("THIS", [2245, 2247, 2250, 2252, 2254, 2257],
             ["y5-h-ocean-02", "fx-couple-02", "h-travel-02", "autumn-04", "h-beach-05"]),
            ("MODERN", [2257, 2259, 2262, 2264, 2266, 2269],
             ["y6-fog-04", "travel-06", "y5-h-forest-02", "nature-06", "h-nature-06"]),
            ("ENERGY", [2269, 2271, 2274, 2276, 2279, 2281],
             ["y5-h-ocean-01", "nature-04", "h-nature-05", "y5-h-volcano-02", "autumn-01"]),
            ("PROJECT", [2281, 2283, 2286, 2288, 2290, 2293],
             ["sunset-03", "y5-h-ocean-02", "summer-04", "nature-04", "fx-couple-03"]),
            ("TO MAKE", [2293, 2296, 2298, 2301, 2302, 2305],
             ["fx-hair-05", "travel-02", "h-nature-03", "y6-h-fog-04", "h-beach-03"])]
    for word, cuts, samples in runs:
        for i, (a, b) in enumerate(zip(cuts, cuts[1:])):
            r.burst(a, b, samples[i], n=1, s0=1.3, r0=40)
        size = SZ + 15 if word == "ENERGY" else SZ
        c = r.say(cuts[0], cuts[-1], word, size, layers=SH)
        if word == "ENERGY":
            c["textStyle"].setdefault("keyframes", {})["pixelSize"] = keys(
                [(0.0, float(SZ)), (r.s(2279) - r.s(2269), float(SZ)), (r.s(2280) - r.s(2269), 185.0)])
        r.blur(c, cuts[0], [(cuts[0], 16), (cuts[0] + 1, 0)])
    beat(2305, 2309, "YOUR", "fx-hair-03")
    white(2309, end, "YOUR", "y5-h-ocean-03")
    return r.finish()


# ==== 7. MINIMAL (2315–2580) ===========================================================================================
def minimal():
    f0, end = 2315, 2577
    t = _p("minimal", "Presentación minimalista en blanco", "Minimal slideshow on white", 16706, (end - f0) / 10,
           ["minimalista", "blanco", "elegante"], 10.0)
    r = R(t, f0)
    INK, SZ = "#26323A", 94

    def w(a, b, text, x=540, y=960, sp=0.08, **kw):
        return r.say(a, b, text, SZ, x=x, y=y, colour=INK, weight=800, sp=sp, **kw)

    def soft(clip, a, pts):
        r.blur(clip, a, pts)

    r.bg(2315, end, WHITE)
    m = w(2315, 2331, "MINIMAL\nSLIDESHOW", sp=0.0)
    soft(m, 2315, [(2326, 0), (2330, 30)])
    r.anim(m, 2315, "opacity", [(2328, 1.0), (2331, 0.0)])
    lk = r.bg(2329, 2341, WHITE, group="top", name="Destello")
    r.fx(lk, 2329, "light_leak", intensity=1.0, hue=0.7, angle=0.25, speed=0.3, softness=0.8)
    r.anim(lk, 2329, "opacity", [(2329, 0.0), (2333, 1.0), (2338, 1.0), (2341, 0.0)])
    ct = r.pic(2333, 2403, "y6-fog-02", z=(1.06, 1.0))
    r.anim(ct, 2333, "opacity", [(2333, 0.0), (2345, 1.0)])
    r.bg(2333, 2403, WHITE, layers=[gradient([(0.0, "#FFFFFF", 0.95), (0.45, "#FFFFFF", 0.6), (0.72, "#FFFFFF", 0.0),
                                              (1.0, "#FFFFFF", 0.0)], angle=90), no_stroke()],
         group="tint", name="Niebla")
    b = w(2336, 2403, "BUSINESS USE", sp=0.08, spread=[(2336, 0.5), (2342, 0.08)])
    soft(b, 2336, [(2336, 25), (2341, 0)])
    r.blocks(b, 2336, 2397, 6)
    gu = r.pic(2403, 2477, "fx-figure-05", z=(1.0, 1.04))
    r.blocks(gu, 2403, 2403, 6)
    st = w(2404, 2477, "MINIMAL\nSTYLE", x=720, y=690, sp=0.08,
           mv=[(2404, 0, 0), (2468, 0, 0), (2475, -600, 0)])
    st["textStyle"]["animation"] = {"in": tk4.tanim("fade", duration=0.25, unit="character", stagger=0.04,
                                                    order="random", ease="easeOut")}
    soft(st, 2404, [(2468, 0), (2474, 30)])
    soft(gu, 2403, [(2468, 0), (2474, 40)])
    r.anim(gu, 2403, "opacity", [(2470, 1.0), (2476, 0.0)])
    mo = r.pic(2477, 2546, "fx-figure-03", z=(1.04, 1.0))
    r.anim(mo, 2477, "opacity", [(2477, 0.0), (2484, 1.0)])
    soft(mo, 2477, [(2477, 40), (2486, 0)])
    md = w(2477, 2546, "MODULAR\nDESIGN", x=520, y=700, sp=0.14, spread=[(2477, 0.14), (2486, 0.06)])
    soft(md, 2477, [(2477, 25), (2485, 0)])
    r.blocks(md, 2477, 2540, 6)
    r.blocks(mo, 2477, 2540, 6)
    ee = r.pic(2546, end, "fx-figure-02", z=(1.0, 1.03))
    r.blocks(ee, 2546, 2546, 5)
    ez = w(2546, end, "EASY\nTO\nEDIT", x=720, y=700, sp=0.1)
    ez["textStyle"]["animation"] = {"in": tk4.tanim("fade", duration=0.25, unit="character", stagger=0.05,
                                                    order="random", ease="easeOut")}
    return r.finish()


# ==== 8. ENERGY (2582–2820) ============================================================================================
def energia():
    f0, end = 2582, 2818
    t = _p("energia", "Presentación con energía y logo", "Energy slideshow with logo", 16707, (end - f0) / 10,
           ["energía", "palabras", "logo"], 7.5)
    r = R(t, f0)
    SH = [shade(0.35), fill(WHITE)]
    SZ = 145

    r.bg(2582, 2612, WHITE)
    for a, b, word, colour in ((2583, 2587, "It's", "#5A2C44"), (2587, 2589, "time", "#6B2347"),
                               (2589, 2591, "to", "#F2B48C"), (2591, 2595, "introduce", "#1D3550"),
                               (2595, 2599, "your", "#7C7C7C"), (2599, 2603, "own", "#E2874E"),
                               (2603, 2612, "brand", "#3B9AD3")):
        c = r.say(a, b, word, SZ, colour=colour, weight=700)
        if word == "brand":
            r.glitch(c, a, 2609, 2)
    r.flash(2611, 2613, "#7FD8F5")

    def word(a, b, text, sample, n=2, spread=0.5, y=960, size=SZ, enter=None):
        p = r.burst(a, b, sample, n=n, s0=1.5, r0=45, enter=enter)
        r.blocks(p, a, a + 1, 3, 0.5)
        return r.say(a, b, text, size, y=y, weight=700, layers=SH, sp=0.03,
                     spread=[(a, spread), (a + 7, 0.03)])

    word(2612, 2625, "Create", "nature-02")
    word(2625, 2641, "Succeed", "h-nature-06")
    word(2641, 2655, "Enjoy", "fx-couple-03")
    ez = word(2655, 2672, "Easy\nto make", "nature-04")
    r.fx(ez, 2655, "stylize.twirl", animated={"angle": [(2655, 300), (2658, 0)]}, radius=0.9)
    word(2672, 2687, "Travel", "h-beach-05")
    word(2687, 2702, "Move", "h-beach-03")
    word(2702, 2709, "Live!", "fx-woman-02", spread=0.4)
    word(2709, 2717, "Taste!", "fx-nature-01", spread=0.4)
    word(2717, 2724, "Learn!", "y6-h-fog-03", spread=0.3)
    word(2724, 2732, "Create!", "beach-03", spread=0.4)
    r.bg(2732, 2762, WHITE)
    for a, b, text, colour in ((2732, 2737, "Create", "#4A2E3A"), (2737, 2739, "your", "#245563"),
                               (2739, 2741, "amazing", "#E2874E"), (2741, 2745, "amazing", "#3B3A4A"),
                               (2745, 2749, "promo", "#A7B04A"), (2749, 2753, "right", "#6A1F2A"),
                               (2753, 2762, "now", "#6A1F3A")):
        r.say(a, b, text, SZ, colour=colour, weight=700)
    r.pic(2762, 2779, "y5-h-ocean-03", z=(1.0, 1.05))
    lg = r.logo(2762, end, y=960, size=430)
    pan = r.shape(2776, end, 540, 960, W * 1.3, H * 1.2, solid(WHITE), name="Panel blanco",
                  sc=[(2776, 0.02), (2780, 1.0)], group="band")
    r.anim(pan, 2776, "rotation", [(2776, -6), (2780, 0)])
    # the logo sits above the panel: move it to the top lane
    tag = r.say(2784, end, "You can capture every moment", 40, y=1200, colour="#3A3A3A", weight=500)
    tag["textStyle"]["animation"] = {"in": tk4.tanim("fade", duration=0.4)}
    pill = r.shape(2804, end, 540, 1790, 760, 150, [fill(WHITE), {"id": "stroke", "kind": "stroke", "enabled": True,
                   "width": 6, "strokeAlign": "inside", "opacity": 1.0,
                   "paint": {"kind": "solid", "color": "#ff2A1830"}}], name="Botón",
                   enter=(0, 200, 3), group="band")
    pill["shapeStyle"]["cornerRadius"] = 75
    r.say(2804, end, "SHOP NOW", 64, y=1790, colour="#2A1830", weight=800, sp=0.05, enter=(0, 200, 3))
    # the logo sits above the white panel: its lane goes to the top
    lgt = next(tr for tr in t.tracks if lg in tr.clips)
    t.tracks.remove(lgt)
    t.tracks.append(lgt)
    return r.finish()


TEMPLATES = [dinamica, moda, ritmica, limpia, epica, stomp, minimal, energia]
