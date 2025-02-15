from typing import List, Tuple

from cmd.filters.colors import (
    create_colorbalance_filter, create_colorchannelmixer_filter,
    create_curves_filter, create_eq_filter
)
from cmd.filters.data_display import create_drawtext_filter
from cmd.filters.blur import (
    create_boxblur_filter, create_gblur_filter, create_smartblur_filter,
    create_edgedetect_filter, create_sobel_filter, create_unsharp_filter,
    create_delogo_filter
)
from cmd.filters.overlays import (
    create_overlay_filter, create_blend_filter
)
from cmd.filters.transformations import (
    create_fade_filter, create_scale_filter,
    create_transpose_filter,
    create_lenscorrection_filter, create_perspective_filter
)
from utils.metadata import get_video_metadata


def parse_effect_items(effect_list: List[List[str]]) -> List[Tuple[float, float, str, List[str]]]:
    items = []
    for item in effect_list:
        if len(item) == 1 and " " in item[0]:
            item = item[0].split()
        start_time = float(item[0])
        end_time = float(item[1])
        effect_type = item[2].lower()
        params = item[3:]
        items.append((start_time, end_time, effect_type, params))
    items.sort(key=lambda x: x[0])
    return items


def create_filter_complex(input_file: str, effect_items: List[Tuple[float, float, str, List[str]]]) -> str:
    filter_complex_parts = []
    seg_count = 0
    current_time = 0.0

    video_duration = get_video_metadata(input_file)[0] or 0.0

    for (start_time, end_time, effect_type, params) in effect_items:
        if current_time < start_time:
            gap_label = f"seg{seg_count}"
            filter_complex_parts.append(
                create_gap_segment_filter(current_time, start_time, gap_label)
            )
            seg_count += 1

        label = f"seg{seg_count}"

        if effect_type == "fade":
            fade_type = params[0]
            fade_dur = float(params[1])
            filter_part = create_fade_filter(start_time, end_time, label, fade_type, fade_dur)

        elif effect_type == "scale":
            w = params[0] if len(params) > 0 else None
            h = params[1] if len(params) > 1 else None
            filter_part = create_scale_filter(start_time, end_time, label, w, h)

        elif effect_type == "transpose":
            direction = int(params[0])
            filter_part = create_transpose_filter(start_time, end_time, label, direction)

        elif effect_type == "lenscorrection":
            k1 = float(params[0]) if len(params) > 0 else None
            k2 = float(params[1]) if len(params) > 1 else None
            filter_part = create_lenscorrection_filter(start_time, end_time, label, k1, k2)

        elif effect_type == "perspective":
            x0, y0, x1, y1, x2, y2, x3, y3 = map(int, params[:8])
            filter_part = create_perspective_filter(start_time, end_time, label, x0, y0, x1, y1, x2, y2, x3, y3)

        elif effect_type == "boxblur":
            val = params[0] if params else None
            filter_part = create_boxblur_filter(start_time, end_time, label, val)

        elif effect_type == "gblur":
            val = params[0] if params else None
            filter_part = create_gblur_filter(start_time, end_time, label, val)

        elif effect_type == "smartblur":
            val = params[0] if params else None
            filter_part = create_smartblur_filter(start_time, end_time, label, val)

        elif effect_type == "edgedetect":
            val = params[0] if params else None
            filter_part = create_edgedetect_filter(start_time, end_time, label, val)

        elif effect_type == "sobel":
            val = params[0] if params else None
            filter_part = create_sobel_filter(start_time, end_time, label, val)

        elif effect_type == "unsharp":
            val = params[0] if params else None
            filter_part = create_unsharp_filter(start_time, end_time, label, val)

        elif effect_type == "delogo":
            x_ = int(params[0])
            y_ = int(params[1])
            w_ = int(params[2])
            h_ = int(params[3])
            show_ = int(params[4]) if len(params) > 4 else None
            filter_part = create_delogo_filter(start_time, end_time, label, x_, y_, w_, h_, show_)

        elif effect_type == "overlay":
            x_expr = params[0]
            y_expr = params[1]
            if len(params) >= 3:
                alpha = float(params[2])
                overlay_source = None
            else:
                alpha = None
                overlay_source = None
            filter_part = create_overlay_filter(start_time, end_time, label,
                                                x_expr=x_expr,
                                                y_expr=y_expr,
                                                overlay_source=overlay_source,
                                                opacity=alpha)

        elif effect_type == "dualoverlay":
            left_x_expr = params[0]
            right_x_expr = params[1]
            opacity = float(params[2]) if len(params) >= 3 else 1.0
            left_label = f"{label}_left"
            right_label = f"{label}_right"
            branch_left = create_overlay_filter(start_time, end_time, left_label,
                                                x_expr=left_x_expr, y_expr="0", opacity=opacity)
            branch_right = create_overlay_filter(start_time, end_time, right_label,
                                                 x_expr=right_x_expr, y_expr="0", opacity=opacity)
            filter_part = f"{branch_left}; {branch_right}; [{left_label}][{right_label}]blend=all_expr='0.5*A+0.5*B'[{label}]"

        elif effect_type == "blend":
            phase = int(params[0])
            cross_params = [p for p in params[1:] if "=" not in p]
            overrides = {p.split("=", 1)[0]: p.split("=", 1)[1] for p in params[1:] if "=" in p}
            filter_part = create_blend_filter(start_time, end_time, label, phase, cross_params, overrides)

        elif effect_type == "colorbalance":
            rs = float(params[0])
            gs = float(params[1])
            bs = float(params[2])
            filter_part = create_colorbalance_filter(start_time, end_time, label, rs, gs, bs)

        elif effect_type == "colorchannelmixer":
            rr, rg, rb, gr, gg, gb, br, bg, bb = map(float, params[:9])
            filter_part = create_colorchannelmixer_filter(start_time, end_time, label, rr, rg, rb, gr, gg, gb, br, bg, bb)

        elif effect_type == "curves":
            curves_str = params[0] if params else None
            filter_part = create_curves_filter(start_time, end_time, label, curves_str)

        elif effect_type == "eq":
            brightness = float(params[0])
            contrast = float(params[1])
            gamma = float(params[2])
            saturation = float(params[3])
            filter_part = create_eq_filter(start_time, end_time, label, brightness, contrast, gamma, saturation)

        elif effect_type == "drawtext":
            text_ = params[0] if params else None
            x_ = params[1] if len(params) > 1 else None
            y_ = params[2] if len(params) > 2 else None
            fontsize_ = int(params[3]) if len(params) > 3 else None
            fontcolor_ = params[4] if len(params) > 4 else None
            filter_part = create_drawtext_filter(start_time, end_time, label, text_, x_, y_, fontsize_, fontcolor_)

        else:
            filter_part = create_gap_segment_filter(start_time, end_time, label)

        filter_complex_parts.append(filter_part)
        seg_count += 1
        current_time = end_time

    if video_duration > current_time:
        gap_label = f"seg{seg_count}"
        filter_complex_parts.append(create_gap_segment_filter(current_time, video_duration, gap_label))
        seg_count += 1

    concat_inputs = "".join([f"[seg{i}]" for i in range(seg_count)])
    filter_complex_parts.append(f"{concat_inputs}concat=n={seg_count}:v=1:a=0[outv]")

    return "; ".join(filter_complex_parts)


# TODO: literally wtf is this, this is actually necessary for the segment splicing??? EWW
def create_gap_segment_filter(from_time: float, to_time: float, label: str) -> str:
    """
    Creates a no-effect segment by trimming the input video from 'from_time'..'to_time',
    labeling it as '[label]'.
    """
    return f"[0:v]trim=start={from_time}:end={to_time},setpts=PTS-STARTPTS[{label}]"
