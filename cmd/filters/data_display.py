# visualization.py

from constants import DEFAULT_DRAWTEXT

def create_drawtext_filter(start, end, label,
                           text=None, x=None, y=None,
                           fontsize=None, fontcolor=None):
    d = DEFAULT_DRAWTEXT
    txt = text if text is not None else d["text"]
    xx  = x if x is not None else d["x"]
    yy  = y if y is not None else d["y"]
    fs  = fontsize if fontsize is not None else d["fontsize"]
    fc  = fontcolor if fontcolor is not None else d["fontcolor"]
    return (
        f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS,"
        f"drawtext=text='{txt}':x={xx}:y={yy}:fontsize={fs}:fontcolor={fc}"
        f"[{label}]"
    )
