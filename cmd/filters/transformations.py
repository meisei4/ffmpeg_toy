# transformations.py

import math
from constants import (
    DEFAULT_CROP, DEFAULT_FADE, DEFAULT_SCALE, DEFAULT_ROTATE,
    DEFAULT_TRANSPOSE, DEFAULT_LENSCORRECTION, DEFAULT_PERSPECTIVE
)

def create_crop_filter(start, end, label, width=None, height=None, x=None, y=None):
    d = DEFAULT_CROP
    w = width  if width  is not None else d["width"]
    h = height if height is not None else d["height"]
    xx = x if x is not None else d["x"]
    yy = y if y is not None else d["y"]
    return (
        f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS,"
        f"crop={w}:{h}:{xx}:{yy}[{label}]"
    )

def create_fade_filter(start, end, label, fade_type=None, duration=None):
    d = DEFAULT_FADE
    ft = fade_type if fade_type is not None else d["type"]
    fd = duration  if duration  is not None else d["duration"]
    return (
        f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS,"
        f"fade=type={ft}:st=0:d={fd}[{label}]"
    )

def create_scale_filter(start, end, label, w=None, h=None):
    d = DEFAULT_SCALE
    ww = w if w is not None else d["w"]
    hh = h if h is not None else d["h"]
    return (
        f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS,"
        f"scale={ww}:{hh}[{label}]"
    )

def create_rotate_filter(start, end, label, angle=None):
    d = DEFAULT_ROTATE
    ang = angle if angle is not None else d["angle"]
    radians = math.radians(ang)
    return (
        f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS,"
        f"rotate={radians}[{label}]"
    )

def create_transpose_filter(start, end, label, direction=None):
    d = DEFAULT_TRANSPOSE
    dir_ = direction if direction is not None else d["dir"]
    return (
        f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS,"
        f"transpose={dir_}[{label}]"
    )

def create_lenscorrection_filter(start, end, label, k1=None, k2=None):
    d = DEFAULT_LENSCORRECTION
    k1_ = k1 if k1 is not None else d["k1"]
    k2_ = k2 if k2 is not None else d["k2"]
    return (
        f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS,"
        f"lenscorrection=k1={k1_}:k2={k2_}[{label}]"
    )

def create_perspective_filter(start, end, label,
                              x0=None, y0=None, x1=None, y1=None,
                              x2=None, y2=None, x3=None, y3=None):
    d = DEFAULT_PERSPECTIVE
    xx0 = x0 if x0 is not None else d["x0"]
    yy0 = y0 if y0 is not None else d["y0"]
    xx1 = x1 if x1 is not None else d["x1"]
    yy1 = y1 if y1 is not None else d["y1"]
    xx2 = x2 if x2 is not None else d["x2"]
    yy2 = y2 if y2 is not None else d["y2"]
    xx3 = x3 if x3 is not None else d["x3"]
    yy3 = y3 if y3 is not None else d["y3"]
    return (
        f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS,"
        f"perspective="
        f"x0={xx0}:y0={yy0}:x1={xx1}:y1={yy1}:"
        f"x2={xx2}:y2={yy2}:x3={xx3}:y3={yy3}[{label}]"
    )
