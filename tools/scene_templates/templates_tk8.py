"""TIKTOK folder video 8 as Stock templates (tk8-*). See docs/plan-tiktok.md.

«Flow Reels» food/yellow pack (48784008.mp4, 1920×1080 at 29.97 fps): the same reel structure as tk7 (photo
collages on a white page, panels that scroll in and push each other, words that fade in one after another, a
text-only panel that leaves through a white line opening into a gap, an end screen with the logo) in mustard yellow
with a heavy soft-serif face (Cooper-like → Roboto Slab Black) in cream and brown. The helpers are tk7's. Food photos
are our own samples (no brands, no flags). Kit de TikTok; ids `tk8-*`, order 14800-. Study notes in
tienda/plantillas/estudio-48784008/NOTAS.md.
"""

from __future__ import annotations

import templates_llt_f as f6
from templates_tit_c import FPS, k
from templates_tk7 import (FULL, G, H, M, TN, W, R, _p, band, come, cta_screen, finish, lines, mix, off, page, panel,
                           pic, push, text_panel)

SLAB = "Roboto Slab"
f6._FILES[(SLAB, 900)] = "fonts.extra/fonts/robotoslab/RobotoSlab-Black.ttf"
WT = 900
CREAM = "#FFF6DE"
BROWN = "#6E3207"
MUST = ("#C49A1C", "#E6B626")            # full panels: darker on top
P_CRISPY = ("#E4B222", "#DCA91A")
P_ORANGE = ("#F0B02E", "#E9A826")
P_DARK = ("#D29A0C", "#C99006")
P_MID = ("#DCAE1E", "#D4A615")
P_GOLD = ("#EEB416", "#E6AA10")

P = "tk8"
TAGS = ["comida", "restaurante", "amarillo"]


def block(words, bands, cx, max_w):
    return band(words, bands, cx, max_w, SLAB, WT)


def say_lines(s, words, colours, inks, at, holder, rest, **kw):
    return lines(s, words, colours, inks, at, holder=holder, rest=rest, family=SLAB, weight=WT, **kw)


# --- 1. CRISPY GOLDEN FRIES: the photos come in from every side, the panel from the right -------------------------
def crispy():
    D = 4.4
    t = _p(P, "crispy-fries", "Historia: CRISPY GOLDEN FRIES con tres fotos", "Story: CRISPY GOLDEN FRIES with three "
           "photos", 14800, D, TAGS)
    s = R(t, D, out=push("up", round((D - 0.5) * FPS)))
    page(s)
    TOP, BL, PN, BR = (M, M, W - M, 978), (M, 1002, 580, H - M), (604, 1002, W - M, 1472), (604, 1496, W - M, H - M)
    pic(s, "Foto 1", "tk8-drink-02", lambda fr: off(TOP, *come("top", 0)(fr)))
    pic(s, "Foto 2", "tk8-sweet-02", lambda fr: off(BL, *come("left", 4)(fr)))
    hold = lambda fr: off(PN, *come("right", 8)(fr))  # noqa: E731
    panel(s, "Panel", P_CRISPY, hold, rest=PN)
    pic(s, "Foto 3", "tk8-fries-01", lambda fr: off(BR, *come("bottom", 10)(fr)))
    words = ["CRISPY", "GOLDEN", "FRIES"]
    say_lines(s, words, [CREAM] * 3, block(words, [(1110, 1177), (1210, 1267), (1291, 1377)], 830, 420), 24, hold, PN)
    return finish(t)


# --- 2. NEW YORK PIZZA: a photo, a yellow panel rises with the words, it shrinks to a corner of the collage -------
def pizza():
    D = 5.6
    t = _p(P, "new-york-pizza", "Historia: NEW YORK PIZZA de pantalla completa a collage", "Story: NEW YORK PIZZA from "
           "full screen to collage", 14801, D, TAGS + ["pizza"])
    s = R(t, D, out=push("right", round((D - 0.5) * FPS)))
    page(s)
    TL, PN, BIG = (M, M, 530, 720), (554, M, W - M, 720), (M, 744, W - M, H - M)
    a = lambda fr: k(fr, 36, TN)  # noqa: E731  the panel rises over the photo
    b = lambda fr: k(fr, 92, 16)  # noqa: E731  the panel shrinks into the collage
    pic(s, "Foto 1", "tk8-pizza-02", lambda fr: off(FULL, *come("bottom", 0)(fr)), op=lambda fr: 1.0 if fr < 110 else 0.0)
    pic(s, "Foto 3", "tk8-burger-02", lambda fr: off(BIG, 0, (H - BIG[1] + G) * (1 - b(fr))))
    pic(s, "Foto 2", "tk8-fries-03", lambda fr: off(TL, -(TL[2] + G) * (1 - b(fr)), 0))
    hold = lambda fr: mix(off(FULL, 0, (H + G) * (1 - a(fr))), PN, b(fr))  # noqa: E731
    panel(s, "Panel", MUST, hold, rest=FULL)
    words = ["NEW", "YORK", "PIZZA"]
    say_lines(s, words, [CREAM, BROWN, CREAM], block(words, [(606, 822), (900, 1088), (1145, 1312)], 540, 900), 46, hold, FULL)
    return finish(t)


# --- 3. FAST FOOD ADDICTION: the panel slides in from the left, the words follow, the next scene pushes it down ---
def fast_food():
    D = 3.6
    t = _p(P, "fast-food", "Historia: FAST FOOD ADDICTION", "Story: FAST FOOD ADDICTION", 14802, D, TAGS + ["texto"])
    s = R(t, D, out=push("down", round((D - 0.5) * FPS)))
    page(s)
    hold = lambda fr: off(FULL, *come("left", 0)(fr))  # noqa: E731
    panel(s, "Panel", MUST, hold, rest=FULL)
    words = ["FAST", "FOOD", "ADDICTION"]
    say_lines(s, words, [CREAM, BROWN, CREAM], block(words, [(609, 797), (812, 999), (1016, 1126)], 540, 840), 8, hold, FULL,
              way="left")
    return finish(t)


# --- 4. FOOD LOVERS UNITE: two tall photos split into four, the title panel drops in and pushes them down ----------
def lovers():
    D = 5.4
    t = _p(P, "food-lovers", "Historia: FOOD LOVERS UNITE con cuatro fotos", "Story: FOOD LOVERS UNITE with four photos",
           14803, D, TAGS)
    s = R(t, D, out=push("down", round((D - 0.5) * FPS)))
    page(s)
    VL, VR = (M, M, 528, H - M), (552, M, W - M, H - M)
    Q = [(M, M, 528, 948), (552, M, W - M, 948), (M, 972, 528, H - M), (552, 972, W - M, H - M)]
    F = [(M, 860, 528, 1368), (552, 860, W - M, 1368), (M, 1392, 528, H - M), (552, 1392, W - M, H - M)]
    PN = (M, M, W - M, 836)
    a = lambda fr: k(fr, 34, TN)  # noqa: E731  the top row drops in, the tall ones shrink to the bottom row
    b = lambda fr: k(fr, 74, TN)  # noqa: E731  the panel drops in
    drop = lambda r, at: (lambda fr: off(r, *come("top", at)(fr)))  # noqa: E731

    def staged(start, q, f, enter):
        return lambda fr: mix(mix(off(start, *enter(fr)), q, a(fr)), f, b(fr))
    pic(s, "Foto 3", "tk8-fries-01", staged(VL, Q[2], F[2], come("top", 0)), box=VL)
    pic(s, "Foto 4", "tk8-girl-02", staged(VR, Q[3], F[3], come("bottom", 0)), box=VR)
    pic(s, "Foto 1", "tk8-drink-03", lambda fr: mix(drop(Q[0], 34)(fr), F[0], b(fr)), box=Q[0])
    pic(s, "Foto 2", "tk8-burger-02", lambda fr: mix(drop(Q[1], 36)(fr), F[1], b(fr)), box=Q[1])
    hold = lambda fr: off(PN, 0, -(PN[3] + G) * (1 - b(fr)))  # noqa: E731
    panel(s, "Panel", P_GOLD, hold, rest=PN)
    words = ["FOOD", "LOVERS", "UNITE"]
    say_lines(s, words, [CREAM, BROWN, CREAM], block(words, [(176, 338), (381, 495), (543, 681)], 542, 780), 84, hold, PN)
    return finish(t)


# --- 5. HOT DOGS / CRISPY FRIES: a photo is cut in strips into a 2×2, two cells make room for two panels ----------
def hot_dogs():
    D = 5.4
    t = _p(P, "hot-dogs", "Historia: HOT DOGS y CRISPY FRIES", "Story: HOT DOGS and CRISPY FRIES", 14804, D,
           TAGS + ["hot dog"])
    s = R(t, D, out=push("up", round((D - 0.5) * FPS)))
    page(s)
    HD, RT, ML, LT, MR, CF = (M, M, 530, 472), (554, M, W - M, 948), (M, 496, 530, 948), (M, 972, 530, H - M), \
        (554, 972, W - M, 1420), (554, 1444, W - M, H - M)
    Q = [(M, M, 530, 948), (554, M, W - M, 948), (M, 972, 530, H - M), (554, 972, W - M, H - M)]
    cut = 40
    b = lambda fr: k(fr, 70, TN)  # noqa: E731  two cells make room for the panels
    seen = lambda fr: 1.0 if fr >= cut else 0.0  # noqa: E731  the 2×2 shows once the strips start to leave
    pic(s, "Foto 2", "tk8-sweet-02", lambda fr: mix(Q[0], ML, b(fr)), op=seen)
    pic(s, "Foto 3", "tk8-hotdog-03", lambda fr: Q[1], op=seen)
    pic(s, "Foto 4", "tk8-burger-04", lambda fr: Q[2], op=seen)
    pic(s, "Foto 5", "tk8-drink-03", lambda fr: mix(Q[3], MR, b(fr)), op=seen)
    # the full photo on top, cut into four vertical strips that slide away up and down
    edges = [0, 270, 540, 810, W]
    for i in range(4):
        x0, x1 = edges[i], edges[i + 1]
        way = -1 if i % 2 == 0 else 1

        def strip(fr, x0=x0, x1=x1, way=way, i=i):
            r = off(FULL, *come("top", 0)(fr))
            g = 7 * k(fr, cut - 8, 6)  # the white cuts appear just before the strips leave
            r = (max(r[0], x0 + (g if i else 0)), r[1], min(r[2], x1 - (g if i < 3 else 0)), r[3])
            return off(r, 0, way * (H + G) * k(fr, cut + 2 * i, TN))
        pic(s, f"Foto 1 ({i + 1})" if i else "Foto 1", "tk8-fries-01", strip, box=FULL, label="Foto 1",
            follow=(0.0, 1.0), op=lambda fr, i=i: 1.0 if fr < cut + 2 * i + TN + 1 else 0.0)
    # every strip shows the same slot: the later strips reuse the first one's picture
    first = None
    for tr in s.t.tracks:
        for c in tr.clips:
            if c.get("type") == "image" and c.get("placeholderLabel") == "Foto 1":
                if first is None:
                    first = c
                elif c is not first:
                    s.t.slots = [sl for sl in s.t.slots if sl.id != c["placeholderId"]]
                    c["placeholderId"] = first["placeholderId"]
                    c["_sample"] = first["_sample"]
    h1 = lambda fr: off(HD, 0, -(HD[3] + G) * (1 - b(fr)))  # noqa: E731
    h2 = lambda fr: off(CF, 0, (H - CF[1] + G) * (1 - b(fr)))  # noqa: E731
    panel(s, "Panel", P_DARK, h1, rest=HD)
    panel(s, "Panel 2", P_DARK, h2, rest=CF)
    say_lines(s, ["HOT", "DOGS"], [BROWN, BROWN], block(["HOT", "DOGS"], [(129, 238), (262, 353)], 277, 420), 84, h1, HD)
    say_lines(s, ["CRISPY", "FRIES"], [CREAM, BROWN], block(["CRISPY", "FRIES"], [(1577, 1653), (1687, 1777)], 805, 440), 90, h2, CF,
              names=["Texto", "Texto 2"])
    return finish(t)


def fried():
    D = 3.6
    t = _p(P, "fried-chicken", "Historia: FRIED CHICKEN DELIGHT", "Story: FRIED CHICKEN DELIGHT", 14805, D,
           TAGS + ["texto", "pollo"])
    text_panel(t, D, MUST, ["FRIED", "CHICKEN", "DELIGHT"], [CREAM, BROWN, CREAM], [(656, 832), (853, 983), (1007, 1148)], 0, 0,
               come("bottom", 0), family=SLAB, weight=WT, angle=90)
    return finish(t)


# --- 7. BIG -50% SALE: two photos open from the middle, the big one moves down, a photo and the panel come in ------
def big_sale():
    D = 5.0
    t = _p(P, "big-sale", "Historia: BIG -50% SALE con tres fotos", "Story: BIG -50% SALE with three photos", 14806, D,
           TAGS + ["oferta"])
    s = R(t, D, out=push("right", round((D - 0.5) * FPS)))
    page(s)
    TOP, BIG0 = (M, M, W - M, 612), (M, 636, W - M, H - M)
    ML, PN, BIG = (M, 636, 560, 1164), (584, 636, W - M, 1164), (M, 1188, W - M, H - M)
    o = lambda fr: k(fr, 0, 14)  # noqa: E731
    b = lambda fr: k(fr, 46, TN)  # noqa: E731

    def opened(r):
        return lambda fr: (r[0], 960 + (r[1] - 960) * o(fr), r[2], 960 + (r[3] - 960) * o(fr))
    pic(s, "Foto 1", "tk8-pizza-01", opened(TOP), box=TOP)
    pic(s, "Foto 3", "tk8-burger-03", lambda fr: mix(opened(BIG0)(fr), BIG, b(fr)), box=BIG0)
    pic(s, "Foto 2", "tk8-sweet-03", lambda fr: off(ML, *come("left", 50)(fr)))
    hold = lambda fr: off(PN, *come("right", 50)(fr))  # noqa: E731
    panel(s, "Panel", P_GOLD, hold, rest=PN)
    words = ["BIG", "-50%", "SALE"]
    say_lines(s, words, [CREAM, BROWN, CREAM], block(words, [(708, 813), (834, 970), (991, 1075)], 820, 400), 62, hold, PN)
    return finish(t)


# --- grid-only stories: same moves, other layouts ---------------------------------------------------------------
def nice_diners():
    D = 4.6
    t = _p(P, "nice-diners", "Historia: NICE DINERS con foto alta", "Story: NICE DINERS with a tall photo", 14807, D,
           TAGS)
    s = R(t, D, out=push("up", round((D - 0.5) * FPS)))
    page(s)
    TL, RT, PN, BL = (M, M, 500, 712), (524, M, W - M, H - M), (M, 736, 500, 1186), (M, 1210, 500, H - M)
    a = lambda fr: k(fr, 24, TN)  # noqa: E731
    pic(s, "Foto 2", "tk8-girl-02", lambda fr: off(mix(FULL, RT, a(fr)), *come("bottom", 0)(fr)), box=FULL)
    pic(s, "Foto 1", "tk8-fries-02", lambda fr: off(TL, *come("left", 24)(fr)))
    hold = lambda fr: off(PN, *come("left", 27)(fr))  # noqa: E731
    panel(s, "Panel", P_ORANGE, hold, rest=PN)
    pic(s, "Foto 3", "tk8-hotdog-03", lambda fr: off(BL, *come("left", 30)(fr)))
    words = ["NICE", "DINERS"]
    say_lines(s, words, [CREAM, BROWN], block(words, [(843, 948), (986, 1058)], 262, 440), 42, hold, PN)
    return finish(t)


def lowest_price():
    D = 4.4
    t = _p(P, "lowest-price", "Historia: THE LOWEST PRICE", "Story: THE LOWEST PRICE", 14808, D, TAGS + ["oferta"])
    s = R(t, D, out=push("up", round((D - 0.5) * FPS)))
    page(s)
    TOP, BL, PN = (M, M, W - M, 1160), (M, 1184, 530, H - M), (554, 1184, W - M, H - M)
    a = lambda fr: k(fr, 22, TN)  # noqa: E731
    pic(s, "Foto 1", "tk8-burger-03", lambda fr: off(mix(FULL, TOP, a(fr)), *come("top", 0)(fr)), box=FULL)
    pic(s, "Foto 2", "tk8-drink-03", lambda fr: off(BL, 0, (H - BL[1] + G) * (1 - a(fr))))
    hold = lambda fr: off(PN, 0, (H - PN[1] + G) * (1 - k(fr, 25, TN)))  # noqa: E731
    panel(s, "Panel", P_DARK, hold, rest=PN)
    words = ["THE", "LOWEST", "PRICE"]
    say_lines(s, words, [CREAM, BROWN, CREAM], block(words, [(1353, 1486), (1529, 1587), (1625, 1720)], 805, 460), 36, hold, PN)
    return finish(t)


def apple_pie():
    D = 5.0
    t = _p(P, "apple-pie", "Historia: SWEET APPLE PIE y SAVOR EVERY BITE", "Story: SWEET APPLE PIE and SAVOR EVERY BITE",
           14809, D, TAGS + ["postre"])
    s = R(t, D, out=push("up", round((D - 0.5) * FPS)))
    page(s)
    T1, T2, T3 = (M, M, 356, 472), (380, M, 712, 472), (736, M, W - M, 472)
    P1, MP, P2, BIG = (M, 496, 356, 948), (M, 972, 356, 1420), (M, 1444, 356, H - M), (380, 496, W - M, H - M)
    a = lambda fr: k(fr, 24, TN)  # noqa: E731
    pic(s, "Foto 5", "tk8-girl-02", lambda fr: off(mix(FULL, BIG, a(fr)), *come("bottom", 0)(fr)), box=FULL)
    for i, (r, smp) in enumerate(((T1, "tk8-sweet-02"), (T2, "tk8-drink-02"), (T3, "tk8-sweet-03"))):
        pic(s, f"Foto {i + 1}", smp, lambda fr, r=r, i=i: off(r, *come("top", 24 + 3 * i)(fr)))
    h1 = lambda fr: off(P1, *come("left", 30)(fr))  # noqa: E731
    h2 = lambda fr: off(P2, *come("left", 36)(fr))  # noqa: E731
    panel(s, "Panel", P_MID, h1, rest=P1)
    pic(s, "Foto 4", "tk8-fries-04", lambda fr: off(MP, *come("left", 33)(fr)))
    panel(s, "Panel 2", P_MID, h2, rest=P2)
    w1 = ["SWEET", "APPLE", "PIE"]
    w2 = ["SAVOR", "EVERY", "BITE"]
    say_lines(s, w1, [CREAM, BROWN, CREAM], block(w1, [(591, 643), (657, 710), (729, 834)], 190, 290), 44, h1, P1)
    say_lines(s, w2, [CREAM, BROWN, CREAM], block(w2, [(1558, 1610), (1629, 1682), (1701, 1772)], 190, 290), 52, h2, P2,
              names=["Texto", "Texto 2", "Texto 3"])
    return finish(t)


def bbq():
    D = 4.8
    t = _p(P, "bbq", "Historia: BBQ SMOKE RISING con cinco fotos", "Story: BBQ SMOKE RISING with five photos", 14810,
           D, TAGS + ["parrilla"])
    s = R(t, D, out=push("up", round((D - 0.5) * FPS)))
    page(s)
    cells = [(M, M, 530, 634), (554, M, W - M, 634), (M, 658, 530, 1268), (554, 658, W - M, 1268),
             (M, 1292, 530, H - M), (554, 1292, W - M, H - M)]
    VL, VR = (M, M, 530, H - M), (554, M, W - M, H - M)
    a = lambda fr: k(fr, 30, TN)  # noqa: E731
    # two tall photos, then the rows drop in from the top and push them into the bottom row
    pic(s, "Foto 4", "tk8-drink-03", lambda fr: off(mix(VL, cells[4], a(fr)), *come("top", 0)(fr)), box=VL)
    pic(s, "Foto 5", "tk8-hotdog-04", lambda fr: off(mix(VR, cells[5], a(fr)), *come("bottom", 0)(fr)), box=VR)
    drop = lambda r: (lambda fr: off(r, 0, -(1268 + G) * (1 - a(fr))))  # noqa: E731
    pic(s, "Foto 1", "tk8-burger-02", drop(cells[0]))
    pic(s, "Foto 2", "tk8-girl-01", drop(cells[1]))
    hold = drop(cells[2])
    panel(s, "Panel", P_MID, hold, rest=cells[2])
    pic(s, "Foto 3", "tk8-sweet-03", drop(cells[3]))
    words = ["BBQ", "SMOKE", "RISING"]
    say_lines(s, words, [CREAM, BROWN, CREAM], block(words, [(796, 948), (962, 1034), (1072, 1143)], 277, 430), 46, hold, cells[2])
    return finish(t)


def buy_now():
    D = 4.6
    t = _p(P, "buy-now", "Historia: BUY NOW con cinco fotos", "Story: BUY NOW with five photos", 14811, D,
           TAGS + ["oferta"])
    s = R(t, D, out=push("up", round((D - 0.5) * FPS)))
    page(s)
    PN, TR, ML, MR, BL, BR = (M, M, 530, 548), (554, M, W - M, 548), (M, 572, 530, 1348), (554, 572, W - M, 1348), \
        (M, 1372, 530, H - M), (554, 1372, W - M, H - M)
    a = lambda fr: k(fr, 26, TN)  # noqa: E731
    pic(s, "Foto 2", "tk8-girl-02", lambda fr: off(mix(FULL, ML, a(fr)), *come("left", 0)(fr)), box=FULL)
    pic(s, "Foto 3", "tk8-drink-03", lambda fr: off(MR, *come("right", 26)(fr)))
    hold = lambda fr: off(PN, *come("top", 28)(fr))  # noqa: E731
    panel(s, "Panel", P_CRISPY, hold, rest=PN)
    pic(s, "Foto 1", "tk8-sweet-03", lambda fr: off(TR, *come("top", 30)(fr)))
    pic(s, "Foto 4", "tk8-burger-06", lambda fr: off(BL, *come("bottom", 30)(fr)))
    pic(s, "Foto 5", "tk8-hotdog-04", lambda fr: off(BR, *come("bottom", 32)(fr)))
    words = ["BUY", "NOW"]
    say_lines(s, words, [CREAM, BROWN], block(words, [(157, 276), (314, 419)], 277, 430), 44, hold, PN)
    return finish(t)


# --- 12. DISCOVER NEW FLAVORS: a photo, the end panel from the right, logo, words and SWIPE ------------------------
def discover():
    D = 6.0
    t = _p(P, "discover-flavors", "Historia final: DISCOVER NEW FLAVORS con tu logo", "End story: DISCOVER NEW FLAVORS "
           "with your logo", 14812, D, TAGS + ["final", "logo"], thumb=5.0)
    words = ["DISCOVER", "NEW", "FLAVORS"]
    inks = block(words, [(1075, 1167), (1178, 1352), (1368, 1506)], 540, 760)

    def button(s):
        from templates_tk7 import chevrons
        chevrons(s, 540, 1600, 70, CREAM, 86, double=False)
        c = s.say("SWIPE", (466, 1630, 614, 1664), SLAB, WT, CREAM, "Deslizar",
                  geom=lambda fr, u: (0, 0, 1, 0, k(fr, 86, 8)))
        return c
    cta_screen(t, D, "tk8-hotdog-04", MUST, words, [CREAM] * 3, inks, SLAB, WT, button, photo_from="left")
    return finish(t)


TEMPLATES = [crispy, pizza, fast_food, lovers, hot_dogs, fried, big_sale, nice_diners, lowest_price, apple_pie, bbq,
             buy_now, discover]
