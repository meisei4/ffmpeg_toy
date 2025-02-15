from constants import DEFAULT_OVERLAY, DEFAULT_BLEND


def create_overlay_filter(start, end, label, x_expr=None, y_expr=None, overlay_source=None,
                          eof_action=None, eval_mode=None, shortest=None, format_=None, opacity=None):
    """
    Creates an overlay filter segment.

    Parameters:
      - start, end: time range in seconds.
      - label: unique label for this segment.
      - x_expr, y_expr: Expressions for the x and y positions.
      - overlay_source: Optional secondary input. If not provided, defaults to "[0:v]" (i.e. duplicate the input).
      - eof_action, eval_mode, shortest, format_: Additional overlay options.
      - opacity: If provided, after overlay the result is passed through a colorchannelmixer
                 to set the alpha channel (e.g. opacity=0.5 yields 50% opacity).

    Returns:
      A filter_complex string segment applying the overlay.
    """
    d = DEFAULT_OVERLAY
    x_val = x_expr if x_expr is not None else d.get("x", "0")
    y_val = y_expr if y_expr is not None else d.get("y", "0")
    # Default to duplicating input if no overlay_source is provided.
    ov = overlay_source if overlay_source is not None else "[0:v]"

    opts = []
    if eof_action is not None:
        opts.append(f"eof_action={eof_action}")
    if eval_mode is not None:
        opts.append(f"eval={eval_mode}")
    if shortest is not None:
        opts.append(f"shortest={shortest}")
    if format_ is not None:
        opts.append(f"format={format_}")
    opts_str = ":" + ":".join(opts) if opts else ""

    overlay_str = (
        f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS[{label}_base]; "
        f"{ov}trim=start={start}:end={end},setpts=PTS-STARTPTS[{label}_ovl]; "
        f"[{label}_base][{label}_ovl]overlay=x={x_val}:y={y_val}{opts_str}"
    )
    if opacity is not None:
        overlay_str += f",format=yuva420p,colorchannelmixer=aa={opacity}"
    overlay_str += f"[{label}]"
    return overlay_str


def create_blend_filter(start, end, label, phase=None, cross_params=None, overrides=None):
    """
    Creates two streams from the same input:
      - [orig_{label}]: Original video (no effect).
      - [fx_{label}]: Video with the supplied effect chain.
    Then blends them together using blend=all_expr with time-based logic.

    Parameters:
      - phase: Determines the blending mode.
      - cross_params: List of time parameters for crossfade.
      - overrides: Dictionary of effect parameters (supports custom names such as red_shift_horizontal, etc.).

    Returns:
      A filter_complex string segment that blends the two streams.
    """
    d = DEFAULT_BLEND
    ph = phase if phase is not None else d.get("phase")
    cp = cross_params if cross_params is not None else d.get("cross_params")
    od = overrides if overrides is not None else d.get("overrides")

    expr = _build_blend_expression(ph, cp)
    effect_chain = _build_effect_chain(od)

    return (
        f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS[orig_{label}]; "
        f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS{effect_chain}[fx_{label}]; "
        f"[orig_{label}][fx_{label}]blend=all_expr='{expr}'[{label}]"
    )


def _build_blend_expression(phase, cross_params):
    """
    Constructs the blend expression based on the phase:
      - Phase 1: always B
      - Phase 2: if(T < cross_start) then B else A
      - Phase 3: if(T < cross_start) then B else if(T > cross_end) then A else B
      - Phase 4: fade from B to A between cross_start and cross_end
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
            f"B*(1-((T-{cs})/({ce}-{cs})))+A*((T-{cs})/({ce}-{cs})))"
        )
    else:
        raise ValueError(f"Unknown blend phase: {phase}")


def _build_effect_chain(overrides):
    """
    Constructs the effect chain from the provided overrides.
    Custom parameter names are mapped as follows:
      - rgbashift_rh: Set amount to shift red horizontally.
      - rgbashift_rv: Set amount to shift red vertically.
      - rgbashift_gh: Set amount to shift green horizontally.
      - rgbashift_gv: Set amount to shift green vertically.
      - rgbashift_bh: Set amount to shift blue horizontally.
      - rgbashift_bv: Set amount to shift blue vertically.
      - rgbashift_edge: Set how the edge is handled.
    Other parameters pass through unchanged.
    """
    if not overrides:
        return ""

    rgbashift_params = {}
    other_filters = []
    for k, v in overrides.items():
        if k.startswith("rgbashift_"):
            param_name = k.split("_", 1)[1]
            rgbashift_params[param_name] = v
        else:
            other_filters.append((k, v))

    rgbashift_filter_str = ""
    if rgbashift_params:
        sub_parts = [f"{p}={val}" for p, val in rgbashift_params.items()]
        joined = ":".join(sub_parts)
        rgbashift_filter_str = f"rgbashift={joined}"

    other_filter_strs = []
    for k, v in other_filters:
        if v == k:
            other_filter_strs.append(k)
        else:
            other_filter_strs.append(f"{k}={v}")

    chain_parts = []
    if rgbashift_filter_str:
        chain_parts.append(rgbashift_filter_str)
    chain_parts.extend(other_filter_strs)

    if chain_parts:
        return f",{','.join(chain_parts)}"
    return ""
