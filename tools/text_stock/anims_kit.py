"""Shorthands for the 200 text animations (anims_a.py, anims_b.py).

rv()     an In / Out reveal: one animator with the motion on the standard stagger selector, plus
         (fade) a faster opacity ramp so letters are visible while they still move.
curve_in / curve_out
         a one-slot preset whose props follow curves over the slot's progress (no stagger): jelly,
         whip, TV on/off… The slot's length is the "duration" param.
lp()     a Loop preset; `period` adds the "period" param (curves loops repeat every period seconds).
"""

from __future__ import annotations

from kit import A, Anim, P, bezier, curve, everything, karaoke, pos, ref, stagger_sel, sweep, wiggle

LOCK_ALL = {"unitLocked": True, "orderLocked": True, "easeLocked": True}


def rv(id, es, en, cat, chip, sample, motion: dict, *, unit="character", stagger=0.04, duration=0.5, ease="easeOut",
       order="forward", fade: float | None = 0.45, slots=("in", "out"), params=(), flags=None, tags=(), extra=(),
       caret=None, look="bold", hold=None, ease_spec=None) -> Anim:
    motion = dict(motion)
    sel = stagger_sel(ease=ease_spec) if ease_spec else "stagger"
    animators = []
    if fade is None:
        animators.append(A([sel], **motion))
    elif fade >= 1.0:
        motion["opacity"] = 0
        animators.append(A([sel], **motion))
    else:
        animators.append(A([sel], **motion))
        animators.append(A([stagger_sel(fade, ease="linear")], opacity=0))
    animators.extend(extra)
    defaults = {"unit": unit, "stagger": stagger, "duration": duration, "ease": ease, "order": order}
    fl = dict(flags or {})
    if ease_spec:
        fl["easeLocked"] = True
    return Anim(id, es, en, cat, chip, list(slots), sample, animators, params=list(params), defaults=defaults,
                flags=fl, caret=caret, tags=list(tags), look=look, hold=hold)


def curve_in(id, es, en, cat, chip, sample, animators, *, duration=0.7, params=(), tags=(), look="bold",
             slot="in") -> Anim:
    return Anim(id, es, en, cat, chip, [slot], sample, animators, params=list(params),
                defaults={"duration": duration, "unit": "block", "ease": "linear"}, flags=dict(LOCK_ALL),
                tags=list(tags), look=look)


def curve_out(*args, **kw) -> Anim:
    return curve_in(*args, slot="out", **kw)


def lp(id, es, en, cat, chip, sample, animators, *, params=(), period: float | None = None, tags=(), look="bold") -> Anim:
    params = list(params)
    if period is not None:
        params.append(P("period", "Duration", default=period, unit="s", min=0.1, max=10, step=0.05))
    return Anim(id, es, en, cat, chip, ["loop"], sample, animators, params=params, common=False, tags=list(tags),
                look=look)


def speed(default: float, lo: float = 0.1, hi: float = 10.0) -> dict:
    return P("speed", "Speed", default=default, unit="Hz", min=lo, max=hi, step=0.1)


def amount(default: float, unit: str = "em", lo: float = 0.0, hi: float = 2.0, step: float = 0.01, id="amount",
           label="Amount") -> dict:
    return P(id, label, default=default, unit=unit, min=lo, max=hi, step=step)


def color(id: str, label: str, default: str) -> dict:
    return P(id, label, type="color", default=default)


def spike(at: float, length: float, peak: float = 100.0) -> list:
    """Amount keys (progress, %) that are 0 except for a held peak from `at` for `length`."""
    pts = [(0.0, 0.0, "hold")] if at > 0 else []
    pts += [(at, peak, "hold"), (min(at + length, 1.0), 0.0, "hold"), (1.0, 0.0, "hold")]
    return pts


def pulse_sel(points: list, domain: str = "character", mode: str = "add") -> dict:
    """A curves selector over the whole text whose amount follows `points` (progress, %)."""
    s = everything(domain)
    s["amount"] = curve(points)
    if mode != "add":
        s["mode"] = mode
    return s


def mode(sel: dict, m: str) -> dict:
    out = dict(sel)
    out["mode"] = m
    return out


__all__ = ["A", "P", "bezier", "curve", "everything", "karaoke", "pos", "ref", "stagger_sel", "sweep", "wiggle",
           "rv", "curve_in", "curve_out", "lp", "speed", "amount", "color", "spike", "pulse_sel", "mode", "LOCK_ALL"]
