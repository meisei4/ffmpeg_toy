# filtering.py

from constants import (
    DEFAULT_BOXBLUR, DEFAULT_GBLUR, DEFAULT_SMARTBLUR, DEFAULT_EDGEDETECT,
    DEFAULT_SOBEL, DEFAULT_UNSHARP, DEFAULT_DELOGO
)

def create_boxblur_filter(start, end, label, boxblur_val=None):
    val = boxblur_val if boxblur_val is not None else DEFAULT_BOXBLUR
    return (
        f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS,"
        f"boxblur={val}[{label}]"
    )

def create_gblur_filter(start, end, label, gblur_val=None):
    val = gblur_val if gblur_val is not None else DEFAULT_GBLUR
    return (
        f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS,"
        f"gblur={val}[{label}]"
    )

def create_smartblur_filter(start, end, label, sb_val=None):
    val = sb_val if sb_val is not None else DEFAULT_SMARTBLUR
    return (
        f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS,"
        f"smartblur={val}[{label}]"
    )

def create_edgedetect_filter(start, end, label, ed_val=None):
    val = ed_val if ed_val is not None else DEFAULT_EDGEDETECT
    return (
        f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS,"
        f"edgedetect={val}[{label}]"
    )

def create_sobel_filter(start, end, label, sobel_val=None):
    val = sobel_val if sobel_val is not None else DEFAULT_SOBEL
    return (
        f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS,"
        f"sobel={val}[{label}]"
    )

def create_unsharp_filter(start, end, label, unsharp_val=None):
    val = unsharp_val if unsharp_val is not None else DEFAULT_UNSHARP
    return (
        f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS,"
        f"unsharp={val}[{label}]"
    )

def create_delogo_filter(start, end, label,
                         x=None, y=None, w=None, h=None, show=None):
    d = DEFAULT_DELOGO
    xx = x if x is not None else d["x"]
    yy = y if y is not None else d["y"]
    ww = w if w is not None else d["w"]
    hh = h if h is not None else d["h"]
    sh = show if show is not None else d["show"]
    return (
        f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS,"
        f"delogo=x={xx}:y={yy}:w={ww}:h={hh}:show={sh}[{label}]"
    )
