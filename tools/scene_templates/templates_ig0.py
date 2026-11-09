"""INSTAGRAM folder video 12241495.mp4 as Stock templates (ig0-*). See docs/plan-instagram.md.

«Instagram dynamic intro» (1920×1080 at 30 fps, 17.1 s): one continuous urban story intro (URBAN, INTRO, a wall of
STREETS, PROMO in photo letters, CLEAN, a corner-grow run of photos, RHTHM and a 2×2 collage, SIMPLE, STOMP, a wall
of THANKS over a photo, the brand logo) that the reference shows on one to three story screens at a time. The
largest screen was found and cropped on every frame (552×976 px), laid out flat on 1080×1920 and studied cut for cut
at 30 fps; the template follows the reference frame numbers (`Reel`, from templates_tk4, at 30 fps). The pack card
(«INSTAGRAM DYNAMIC INTRO 1080x1920») and the author line are left out; the brand mark (end and corner) is the
user's `logo-flip` slot. Photos are slots. Kit de Instagram; ids `ig0-*`, order 15000-. Study notes in
tienda/plantillas/estudio-12241495/NOTAS.md.
"""

from __future__ import annotations

import templates_llt_f as f6
from kit import Box, tall
from scene import keys
from templates_tk4 import Reel, outline, shade, solid
from scene import fill

W, H = 1080, 1920
REF_FPS = 30.0
WHITE, PAPER, INK, SLATE = "#FFFFFF", "#F6F6F4", "#2B2F38", "#3A4150"
AE = "Anybody Expanded"
f6._FILES[(AE, 900)] = "fonts.extra/fonts/anybodyexpanded/AnybodyExpanded-Black.ttf"
END = 513


class Intro(Reel):
    """Reel at the reference's 30 fps, with squash / slide moves for photos and words."""

    def s(self, fr):
        return max(0.0, (fr - self.f0) / REF_FPS)

    def lane(self, group, t0, t1):
        """As Reel.lane, but a clip that starts while others of its group still show goes on a lane above them
        all (later cuts cover earlier ones, as in the reference)."""
        lanes = self.lanes[group]
        busy = [i for i, ln in enumerate(lanes) if ln[1] > t0 + 1e-6]
        start = (max(busy) + 1) if busy else 0
        for ln in lanes[start:]:
            if ln[1] <= t0 + 1e-6:
                ln[1] = t1
                return ln[0]
        kind, name = lanes[0][0].type, lanes[0][0].name
        track = self.t.track(kind, name)
        self.t.tracks.remove(track)
        self.t.tracks.insert(self.t.tracks.index(lanes[-1][0]) + 1, track)
        lanes.append([track, t1])
        return track

    def pic2(self, a, b, sample, mot, label=None, reuse=None, group="pic", role="cover", zoom=(1.0, 1.05),
             ease="linear"):
        """A full-frame photo slot from frame a to b; mot = [(frame, dx, dy, sx, sy)] (linear between, eased
        out into each key); a slow push `zoom` multiplies the scale."""
        t0, t1 = self.s(a), self.s(b)
        if reuse is None:
            reuse = next((sl.id for sl in self.t.slots if sl.sample == sample), None)
        pts = sorted(mot or [(a, 0, 0, 1, 1), (b, 0, 0, 1, 1)])
        if pts[0][0] > a:
            pts.insert(0, (a,) + tuple(pts[0][1:]))
        if pts[-1][0] < b:
            pts.append((b,) + tuple(pts[-1][1:]))
        out = []
        for fr, dx, dy, sx, sy in pts:
            z = zoom[0] + (zoom[1] - zoom[0]) * (fr - a) / max(1, b - a)
            out.append((self.s(fr) - t0, {"dx": dx, "dy": dy, "sx": max(1e-4, sx * z), "sy": max(1e-4, sy * z)},
                        ease))
        clip = self.t.photo(self.lane(group, t0, t1), sample, t0, t1 - t0, Box(0, 0, W, H), out, label=label,
                            reuse=reuse)
        clip["layoutRole"] = role
        if any(abs(p[1]) > 1 or abs(p[2]) > 1 for p in pts):
            clip["motionBlur"] = True
        return clip

    # --- the cuts ---------------------------------------------------------------------------------------------
    @staticmethod
    def squash(a, n, anchor):
        """Keys that flatten a full-frame layer onto the top / bottom edge (the reference's push transitions)."""
        sign = -1 if anchor == "top" else 1
        return [(a, 0, 0, 1, 1), (a + n, 0, sign * H / 2, 1, 0.0)]

    @staticmethod
    def rise(a, n, frm="bottom", lead=0.3):
        d = {"bottom": (0, H * (1 + lead)), "top": (0, -H * (1 + lead)), "left": (-W * (1 + lead), 0),
             "right": (W * (1 + lead), 0)}[frm]
        return [(a, d[0], d[1], 1, 1), (a + n, 0, 0, 1, 1)]

    @staticmethod
    def corner(a, n, which, s0=0.05):
        """Grows from a corner (bl, br, tl, tr) of the frame."""
        cx = -W / 2 if which[1] == "l" else W / 2
        cy = -H / 2 if which[0] == "t" else H / 2
        return [(a, cx * (1 - s0), cy * (1 - s0), s0, s0), (a + n, 0, 0, 1, 1)]

    def white_corner(self, a, n, which, b):
        """The white panel that opens from a corner before the next photo grows over it."""
        cx = 0 if which[1] == "l" else W
        cy = 0 if which[0] == "t" else H
        t0, t1 = self.s(a), self.s(b)
        mot = []
        for i in range(0, n + 1):
            p = i / n
            p = 1 - (1 - p) ** 3
            w, h = max(1.0, W * p), max(1.0, H * p)
            x = cx - w if which[1] == "r" else cx
            y = cy - h if which[0] == "b" else cy
            mot.append((self.s(a + i) - t0, {"dx": x + w / 2 - W / 2, "dy": y + h / 2 - H / 2, "sx": w / W,
                                             "sy": h / H}, "linear"))
        clip = self.t.solid(self.lane("pic", t0, t1), PAPER, t0, t1 - t0, Box(0, 0, W, H), mot, layers=solid(PAPER))
        clip["name"] = "Panel blanco"
        clip["layoutRole"] = "cover"
        return clip

    def glitch(self, clip, a, spikes, amount=26):
        """RGB split that flashes at the given frames (the reference's letter glitches)."""
        pts = [(a, 0)]
        for f in spikes:
            pts += [(f - 1, 0), (f, amount), (f + 2, 0)]
        self.fx(clip, a, "rgb_split", animated={"amount": sorted(pts)}, angle=0)

    def column(self, a, b, x, text, size, style, rot, drift, enter=None, exit=None, sample=None, reuse=None,
               ghost_name="Muro de palabras"):
        """One vertical column of a repeated word (turned rot degrees) that drifts drift px while it shows;
        enter / exit = (dy, frames) push it in from / out to a vertical offset."""
        a1 = a + (enter[1] if enter else 0)
        b1 = b - (exit[1] if exit else 0)
        mv = [(a1, 0, -drift / 2), (b1, 0, drift / 2)]
        if enter:
            mv.insert(0, (a, 0, enter[0] - drift / 2))
        if exit:
            mv.append((b, 0, exit[0] + drift / 2))
        kw = dict(ink_size=size, x=x, y=H / 2, weight=900, family=AE, rot=[(a, rot)], editable=False,
                  name=ghost_name, mv=mv)
        if style == "photo":
            w, ph = self.photo_word(a, b, text, 3000, sample, reuse=reuse, z=(1.0, 1.0), label="Foto en las letras",
                                    **kw)
            return w, ph
        layers = {"solid": [fill(SLATE)], "outline": outline(INK, 2.0), "white": [fill(WHITE)],
                  "wline": outline(WHITE, 2.5)}[style]
        return self.word(a, b, text, 3000, layers=layers, group="ghost", **kw), None

    def small_logo(self, a, b):
        t0, t1 = self.s(a), self.s(b)
        first = next((sl.id for sl in self.t.slots if sl.sample == "logo-flip"), None)
        clip = self.t.photo(self.lane("top", t0, t1), "logo-flip", t0, t1 - t0, Box(944, 52, 84, 84), None,
                            label="Tu logo", brandRole="logo", reuse=first)
        clip["name"] = "Logo (esquina)"
        clip["layoutRole"] = "art"
        return clip


def build():
    D = round(END / REF_FPS, 2)
    t = tall("ig0-intro-urbana", "Intro urbana dinámica: URBAN, STREETS, PROMO… y tu logo",
             "Dynamic urban intro: URBAN, STREETS, PROMO… and your logo", "instagram", D, order=15000,
             tags=["instagram", "historia", "reels", "apertura", "urbano", "intro dinámica", "presentación de fotos"],
             thumb_at=round(250 / REF_FPS, 2))
    t.layout_roles = True
    r = Intro(t, 0)
    sh = [shade(alpha=0.25, blur=14, dy=4), fill(WHITE)]
    big = dict(weight=900, family=AE, layers=sh)

    # 0-36: the traffic light fades in from white, URBAN grows, glitches and climbs; the photo flattens upwards
    r.bg(0, END, PAPER, name="Fondo")
    p1 = r.pic2(0, 36, "y5-street-01", [(0, 0, 0, 1.06, 1.06)] + r.squash(28, 6, "top"),
                label="Foto 1", zoom=(1, 1))
    veil = r.bg(0, 14, PAPER, group="top", name="Velo blanco")
    r.anim(veil, 0, "opacity", [(0, 1.0), (3, 1.0), (13, 0.0)])
    u = r.word(9, 31, "URBAN", 820, sc=[(9, 0.15), (12, 1.0)], mv=[(9, 0, 0), (24, 0, 0), (29, 0, -620)], **big)
    r.glitch(u, 9, (22, 25, 27))
    # 30-48: the couple rises from below, the dancer rises over it
    r.pic2(29, 48, "friends-03", r.rise(29, 7, lead=0.1), label="Foto 2")
    p3 = r.pic2(44, 68, "fx-dancer-03", r.rise(44, 4, lead=0.0) + r.squash(61, 6, "top"), label="Foto 3")
    r.word(50, 63, "INTRO", 790, sc=[(50, 1.2), (56, 1.0)], mv=[(50, -40, 520), (56, 0, 0)], **big)

    # 62-96: the STREETS wall rises in, drifting columns (solid, outline, photo letters); the statue drops on it
    r.bg(62, 96, PAPER, enter=(0, H * 1.2, 6), exit=(0, H, 6), group="bg", name="Fondo del muro")
    styles = ("outline", "photo", "outline", "solid", "outline", "photo")
    first = None
    for i, st in enumerate(styles):
        x = 98 + i * 196
        w, ph = r.column(62, 96, x, "STREETS  STREETS  STREETS", 230, st, 90, 260 * (1 if i % 2 else -1),
                         enter=(H * 1.2, 6), exit=(H, 6), sample="fx-citynight-02",
                         reuse=first)
        if ph is not None and first is None:
            first = ph
    r.pic2(90, 120, "city-01", r.rise(90, 6, "top", lead=0.0) + r.squash(111, 8, "bottom"), label="Foto 4")

    # 113-133: PROMO three times in photo letters drops from the top on white
    pf = None
    for i, y in enumerate((707, 987, 1268)):
        _, ph = r.photo_word(115, 133, "PROMO", 1060, "h-autumn-02", y=y, weight=900, family=AE, editable=i == 0,
                             reuse=pf, enter=(0, 230, 5), exit=(0, H, 6), label="Foto en las letras")
        pf = pf or ph
    # 127-161: the dancer under the bridge drops in with CLEAN
    r.pic2(127, 162, "y5-street-07", r.rise(127, 6, "top", lead=0.0), label="Foto 5")
    c = r.word(131, 155, "CLEAN", 790, **big)
    r.glitch(c, 131, (135, 137, 150, 153))

    # 153-180: a white panel opens from a corner and the next photo grows out of it (three times)
    r.white_corner(153, 6, "bl", 162)
    r.pic2(156, 172, "fx-man-03", r.corner(156, 5, "bl"), label="Foto 6", ease="out")
    r.white_corner(164, 5, "br", 172)
    r.pic2(166, 181, "fx-woman-04", r.corner(166, 5, "br"), label="Foto 7", ease="out")
    r.white_corner(174, 4, "tl", 181)
    # 175-245: the laughing woman, RHTHM grows and glitches, then she shrinks into a 2×2 collage
    q = 0.5
    quad = {"tl": (-W / 4, -H / 4), "tr": (W / 4, -H / 4), "bl": (-W / 4, H / 4), "br": (W / 4, H / 4)}
    r.pic2(212, 250, "h-city-03", [(212, *quad["tr"], q, q)], label="Foto 9", zoom=(1, 1))
    r.pic2(212, 250, "h-city-05", [(212, *quad["bl"], q, q)], label="Foto 10", zoom=(1, 1))
    r.pic2(175, 248, "friends-12", r.corner(175, 5, "tl") + [(212, 0, 0, 1, 1), (216, *quad["br"], q, q)],
           label="Foto 8", zoom=(1, 1))
    rh = r.word(188, 244, "RHTHM", 820, sc=[(188, 0.1), (194, 1.0), (212, 1.0), (216, 0.55)],
                mv=[(188, 0, 0), (212, 0, 0), (216, 270, 470)], **big)
    r.glitch(rh, 188, (200, 204, 209))
    # 241-300: the top-left photo grows to the whole frame with SIMPLE; a white corner brings STOMP
    r.pic2(212, 270, "y5-street-02", [(212, *quad["tl"], q, q), (241, *quad["tl"], q, q), (248, 0, 0, 1, 1)],
           label="Foto 11", zoom=(1, 1))
    r.word(244, 262, "SIMPLE", 830, sc=[(244, 0.2), (249, 1.0)], mv=[(244, 0, -60), (249, 0, 0)], **big)
    r.white_corner(260, 5, "br", 270)
    r.pic2(263, 300, "y5-outfit-04", r.corner(263, 6, "br") + r.squash(292, 6, "top"), label="Foto 12", ease="out")
    r.word(278, 293, "STOMP", 820, sc=[(278, 0.15), (284, 1.0)], **big)
    # 294-367: the runner rises, coffee slides in from the left, the group from the right, the couple drops
    r.pic2(293, 318, "fx-skater-01", r.rise(293, 6, lead=0.05), label="Foto 13")
    r.pic2(308, 350, "portrait-07", r.rise(308, 8, "left", lead=0.0), label="Foto 14")
    r.pic2(343, 368, "friends-01", r.rise(343, 7, "right", lead=0.15) + r.squash(360, 6, "bottom"),
           label="Foto 15")
    r.pic2(360, 386, "couple-07", r.rise(360, 7, "top", lead=0.15) + r.squash(378, 6, "top"), label="Foto 16")

    # 378-438: the THANKS wall over a photo rises from below; at the end it all flattens upwards to white
    r.pic2(378, 438, "y5-outfit-06", r.rise(378, 7) + r.squash(428, 10, "top"), label="Foto 17")
    for i, st in enumerate(("white", "wline", "white", "wline", "white", "wline")):
        x = 95 + i * 190
        r.column(378, 438, x, "THANKS  THANKS  THANKS", 220, st, -90, 240 * (1 if i % 2 else -1),
                 enter=(H * 1.3, 7), exit=(-H, 10), ghost_name="Muro de THANKS")

    # 436-513: the logo settles in on white; the user's logo also sits in the top corner through the intro
    r.bg(436, END, PAPER, name="Fondo final")
    lg = r.logo(436, END, y=930, size=420, enter=(-90, 0, 10))
    r.anim(lg, 436, "opacity", [(436, 0.0), (446, 1.0)])
    r.anim(lg, 436, "rotation", [(436, -8.0), (446, 0.0)])
    r.small_logo(13, 436)
    return r.finish()


TEMPLATES = [build]
