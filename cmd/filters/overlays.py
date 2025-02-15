# overlays.py

from constants import (
    DEFAULT_OVERLAY, DEFAULT_BLEND, DEFAULT_CHROMAKEY, DEFAULT_COLORKEY,
    DEFAULT_LUMAKEY
)


def create_overlay_filter(start, end, label, x=None, y=None, overlay_source=None):
    d = DEFAULT_OVERLAY
    xx = x if x is not None else d["x"]
    yy = y if y is not None else d["y"]
    ov = overlay_source if overlay_source is not None else "[1:v]"
    return (
        f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS[{label}_base]; "
        f"{ov}trim=start={start}:end={end},setpts=PTS-STARTPTS[{label}_ovl]; "
        f"[{label}_base][{label}_ovl]overlay=x={xx}:y={yy}[{label}]"
    )


def create_blend_filter(start, end, label, phase=None, cross_params=None, overrides=None):
    """
    Creates TWO distinct streams:
      - [orig_{label}] : No effect
      - [fx_{label}]   : With user-supplied effects (including rgbashift).
    Then blends them using blend=all_expr=... with time-based logic.
    """
    # 1) Determine the blend expression
    d = DEFAULT_BLEND
    ph = phase if phase is not None else d["phase"]
    cp = cross_params if cross_params is not None else d["cross_params"]
    od = overrides if overrides is not None else d["overrides"]

    expr = _build_blend_expression(ph, cp)

    # 2) Build the effect chain string from 'overrides'
    effect_chain = _build_effect_chain(od)
    # e.g. ",rgbashift=rh=60:rv=60:...,boxblur=20:1,hue=s=0.5" etc.

    # 3) Return a multi-line filter spec:
    #    - Trim original => [orig_label]
    #    - Trim + apply effect => [fx_label]
    #    - Blend them => [label]
    return (
        f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS[orig_{label}]; "  # no effect
        f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS{effect_chain}[fx_{label}]; "  # with effect
        f"[orig_{label}][fx_{label}]blend=all_expr='{expr}'[{label}]"
    )


def _build_blend_expression(phase, cross_params):
    """
    phase 1 = always B
    phase 2 = if(T < cross_start) then B else A
    phase 3 = if(T < cross_start) then B
              else if(T > cross_end) then A
              else B
    phase 4 = fade from B to A between cross_start..cross_end
    """
    if phase == 1:
        return "B"
    elif phase == 2:
        cross_start = cross_params[0] if cross_params else "0"
        return f"if(lt(T\\,{cross_start})\\, B\\, A)"
    elif phase == 3:
        if len(cross_params) < 2:
            cross_params = ["0", "0"]
        cs, ce = cross_params[:2]
        return f"if(lt(T\\,{cs})\\, B\\, if(gt(T\\,{ce})\\, A\\, B))"
    elif phase == 4:
        if len(cross_params) < 2:
            cross_params = ["0", "0"]
        cs, ce = cross_params[:2]
        return (
            f"if(lt(T\\,{cs})\\, B\\, "
            f"if(gt(T\\,{ce})\\, A\\, "
            f"B*(1-((T-{cs})/({ce}-{cs})))+A*((T-{cs})/({ce}-{cs}))"
            f"))"
        )
    else:
        raise ValueError(f"Unknown blend phase: {phase}")


def _build_effect_chain(overrides):
    """
    Convert user-supplied overrides dict into a comma-separated FFmpeg filter chain.

    - If user sets "rgbashift_rh=60", "rgbashift_rv=60", etc., we unify them into
      `rgbashift=rh=60:rv=60:gh=...`
    - The rest become separate filters like `boxblur=20:1`, `hue=s=0.5`, `noise=alls=80:allf=t`,
      or just `vignette` if the user typed `vignette=vignette`.

    Example:
      overrides = {
        "rgbashift_rh": "60", "rgbashift_rv": "60",
        "boxblur": "20:1", "hue": "s=0.5",
        "noise": "alls=80:allf=t", "vignette": "vignette"
      }
      => ",rgbashift=rh=60:rv=60,boxblur=20:1,hue=s=0.5,noise=alls=80:allf=t,vignette"
    """
    if not overrides:
        return ""

    # 1) Gather rgbashift parameters into a sub-dict
    rgbashift_params = {}
    other_filters = []

    for k, v in overrides.items():
        if k.startswith("rgbashift_"):
            # e.g. k="rgbashift_rh", v="60" => param name "rh" => "rh=60"
            param_name = k.split("_", 1)[1]  # "rh", "rv", "gh", ...
            rgbashift_params[param_name] = v
        else:
            # It's a standard filter, e.g. boxblur=20:1, hue=s=0.5, noise=..., or vignette
            # If value == "vignette", it might be a filter with no params, but let's just treat it as "filter=value"
            # e.g. "vignette=vignette" => "vignette"
            # We'll handle that logic below
            other_filters.append((k, v))

    # 2) Construct the "rgbashift=..." filter if we have any rgbashift params
    # example: "rgbashift=rh=60:rv=10:gh=-60..."
    rgbashift_filter_str = ""
    if rgbashift_params:
        # e.g. param "rh"=60 => "rh=60"
        # join them with colons
        sub_parts = [f"{p}={val}" for p, val in rgbashift_params.items()]
        joined = ":".join(sub_parts)
        rgbashift_filter_str = f"rgbashift={joined}"

    # 3) Construct each "other filter" in the form "filter=value" or just "filter" if value == filter
    #    Example: ("boxblur", "20:1") => "boxblur=20:1"
    #             ("vignette", "vignette") => "vignette"
    #             ("hue", "s=0.5") => "hue=s=0.5"
    other_filter_strs = []
    for k, v in other_filters:
        if v == k:
            # user typed "vignette=vignette" => just "vignette"
            other_filter_strs.append(k)
        else:
            other_filter_strs.append(f"{k}={v}")

    # 4) Combine everything into a single chain
    # Something like: "rgbashift=rh=60:rv=60,boxblur=20:1,hue=s=0.5,noise=alls=80:allf=t,vignette"
    chain_parts = []
    if rgbashift_filter_str:
        chain_parts.append(rgbashift_filter_str)
    chain_parts.extend(other_filter_strs)

    # Join with commas
    if chain_parts:
        final_chain = ",".join(chain_parts)
        # e.g. "rgbashift=rh=60:rv=60,boxblur=20:1,hue=s=0.5,noise=alls=80:allf=t,vignette"
        return f",{final_chain}"  # prepend a comma because we attach after "setpts=PTS-STARTPTS"
    else:
        return ""


def create_chromakey_filter(start, end, label, color=None, similarity=None, blend_val=None):
    d = DEFAULT_CHROMAKEY
    col = color if color is not None else d["color"]
    sim = similarity if similarity is not None else d["similarity"]
    bl = blend_val if blend_val is not None else d["blend"]
    return (
        f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS,"
        f"chromakey=color={col}:similarity={sim}:blend={bl}[{label}]"
    )


def create_colorkey_filter(start, end, label, color=None, similarity=None, blend_val=None):
    d = DEFAULT_COLORKEY
    col = color if color is not None else d["color"]
    sim = similarity if similarity is not None else d["similarity"]
    bl = blend_val if blend_val is not None else d["blend"]
    return (
        f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS,"
        f"colorkey=color={col}:similarity={sim}:blend={bl}[{label}]"
    )


def create_lumakey_filter(start, end, label, threshold=None):
    from constants import DEFAULT_LUMAKEY
    d = DEFAULT_LUMAKEY
    th = threshold if threshold is not None else d["threshold"]
    return (
        f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS,"
        f"lumakey=threshold={th}[{label}]"
    )


def create_alphamerge_filter(start, end, label):
    return (
        f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS,"
        f"alphamerge[{label}]"
    )


def create_alphaextract_filter(start, end, label):
    return (
        f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS,"
        f"alphaextract[{label}]"
    )
