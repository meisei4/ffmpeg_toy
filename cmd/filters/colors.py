# color_adjustments.py
from constants import (DEFAULT_COLORBALANCE, DEFAULT_COLORCHANNELMIXER, DEFAULT_CURVES, DEFAULT_EQ)


def create_colorbalance_filter(start, end, label, rs=None, gs=None, bs=None):
    cfg = DEFAULT_COLORBALANCE
    rs = rs if rs is not None else cfg["rs"]
    gs = gs if gs is not None else cfg["gs"]
    bs = bs if bs is not None else cfg["bs"]
    return (
        f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS,"
        f"colorbalance=rs={rs}:gs={gs}:bs={bs}[{label}]"
    )


def create_colorchannelmixer_filter(start, end, label,
                                    rr=None, rg=None, rb=None,
                                    gr=None, gg=None, gb=None,
                                    br=None, bg=None, bb=None):
    d = DEFAULT_COLORCHANNELMIXER
    rr = rr if rr is not None else d["rr"]
    rg = rg if rg is not None else d["rg"]
    rb = rb if rb is not None else d["rb"]
    gr = gr if gr is not None else d["gr"]
    gg = gg if gg is not None else d["gg"]
    gb = gb if gb is not None else d["gb"]
    br = br if br is not None else d["br"]
    bg = bg if bg is not None else d["bg"]
    bb = bb if bb is not None else d["bb"]
    return (
        f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS,"
        f"colorchannelmixer=rr={rr}:rg={rg}:rb={rb}:"
        f"gr={gr}:gg={gg}:gb={gb}:br={br}:bg={bg}:bb={bb}"
        f"[{label}]"
    )


def create_curves_filter(start, end, label, curves=None):
    curves = curves if curves is not None else DEFAULT_CURVES
    if not curves:
        return f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS[{label}]"
    return (
        f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS,"
        f"curves={curves}[{label}]"
    )


def create_eq_filter(start, end, label, brightness=None, contrast=None, gamma=None, saturation=None):
    d = DEFAULT_EQ
    b = brightness if brightness is not None else d["brightness"]
    c = contrast if contrast is not None else d["contrast"]
    g = gamma if gamma is not None else d["gamma"]
    s = saturation if saturation is not None else d["saturation"]
    return (
        f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS,"
        f"eq=brightness={b}:contrast={c}:gamma={g}:saturation={s}[{label}]"
    )
