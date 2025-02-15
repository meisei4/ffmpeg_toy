import sys
from typing import List, Tuple
from utils.metadata import get_video_metadata
from cmd.filters.ffmpeg_filter import create_gap_segment_filter

# Import functional “effect creation” utilities:
from cmd.filters.transformations import (
    create_crop_filter, create_fade_filter, create_scale_filter,
    create_rotate_filter, create_transpose_filter,
    create_lenscorrection_filter, create_perspective_filter
)
from cmd.filters.filtering import (
    create_boxblur_filter, create_gblur_filter, create_smartblur_filter,
    create_edgedetect_filter, create_sobel_filter, create_unsharp_filter,
    create_delogo_filter
)
from cmd.filters.overlays import (
    create_overlay_filter, create_blend_filter, create_chromakey_filter,
    create_colorkey_filter, create_lumakey_filter, create_alphamerge_filter,
    create_alphaextract_filter
)
from cmd.filters.colors import (
    create_colorbalance_filter, create_colorchannelmixer_filter,
    create_curves_filter, create_eq_filter, create_lut_filter,
    create_lut3d_filter, create_haldclut_filter
)
from cmd.filters.data_display import create_drawtext_filter


def parse_effect_items(effect_list: List[List[str]]) -> List[Tuple[float, float, str, List[str]]]:
    """
    Given a list of effect specifications from argparse (e.g. [['0','3','crop','640','480'], ...]),
    parse each into (start_time, end_time, effect_type, params).
    """
    items = []
    for item in effect_list:
        try:
            start_time = float(item[0])
            end_time = float(item[1])
            effect_type = item[2].lower()
            params = item[3:]
            items.append((start_time, end_time, effect_type, params))
        except Exception as e:
            print(f"Error parsing effect item {item}: {e}")
            sys.exit(1)
    # Sort by start time so we process them chronologically
    items.sort(key=lambda x: x[0])
    return items

def create_filter_complex(input_file: str, effect_items: List[Tuple[float, float, str, List[str]]]) -> str:
    """
    Builds a single filter_complex string by concatenating segments from 0..duration
    and applying the requested effect for each sub-segment. (Purely functional.)
    """
    filter_complex_parts = []
    seg_count = 0
    current_time = 0.0

    # Get total duration from metadata
    video_duration = get_video_metadata(input_file)[0] or 0.0

    for (start_time, end_time, effect_type, params) in effect_items:
        # If there's a gap between current_time and this effect's start_time, fill it with a no-effect segment
        if current_time < start_time:
            gap_label = f"seg{seg_count}"
            filter_complex_parts.append(
                create_gap_segment_filter(current_time, start_time, gap_label)
            )
            seg_count += 1

        # Build the effect segment
        label = f"seg{seg_count}"

        if effect_type == "crop":
            # e.g. start end crop 640 480 [x y]
            try:
                width = int(params[0])
                height = int(params[1])
                x = int(params[2]) if len(params) > 2 else None
                y = int(params[3]) if len(params) > 3 else None
            except:
                print("Error: crop requires at least width and height.")
                sys.exit(1)
            filter_part = create_crop_filter(start_time, end_time, label, width, height, x, y)

        elif effect_type == "fade":
            try:
                fade_type = params[0]
                fade_dur = float(params[1])
            except:
                print("Error: fade requires fade_type and duration.")
                sys.exit(1)
            filter_part = create_fade_filter(start_time, end_time, label, fade_type, fade_dur)

        elif effect_type == "scale":
            w = params[0] if len(params) > 0 else None
            h = params[1] if len(params) > 1 else None
            filter_part = create_scale_filter(start_time, end_time, label, w, h)

        elif effect_type == "rotate":
            try:
                angle = float(params[0])
            except:
                print("Error: rotate requires an angle.")
                sys.exit(1)
            filter_part = create_rotate_filter(start_time, end_time, label, angle)

        elif effect_type == "transpose":
            # e.g. start end transpose 1
            try:
                direction = int(params[0])
            except:
                print("Error: transpose requires 'dir' (0..3).")
                sys.exit(1)
            filter_part = create_transpose_filter(start_time, end_time, label, direction)

        elif effect_type == "lenscorrection":
            # e.g. start end lenscorrection 0.2 0.2
            k1 = float(params[0]) if len(params) > 0 else None
            k2 = float(params[1]) if len(params) > 1 else None
            filter_part = create_lenscorrection_filter(start_time, end_time, label, k1, k2)

        elif effect_type == "perspective":
            # e.g. start end perspective x0 y0 x1 y1 x2 y2 x3 y3
            try:
                x0, y0, x1, y1, x2, y2, x3, y3 = map(int, params[:8])
            except:
                print("Error: perspective requires 8 integers (x0 y0 x1 y1 x2 y2 x3 y3).")
                sys.exit(1)
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
            try:
                x_ = int(params[0])
                y_ = int(params[1])
                w_ = int(params[2])
                h_ = int(params[3])
                show_ = int(params[4]) if len(params) > 4 else None
            except:
                print("Error: delogo requires x, y, w, h, (optional show).")
                sys.exit(1)
            filter_part = create_delogo_filter(start_time, end_time, label, x_, y_, w_, h_, show_)

        elif effect_type == "overlay":
            # e.g. start end overlay x y [overlay_source]
            try:
                x_ = int(params[0])
                y_ = int(params[1])
                source_ = params[2] if len(params) > 2 else None
            except:
                print("Error: overlay requires x, y, optionally overlay_source.")
                sys.exit(1)
            filter_part = create_overlay_filter(start_time, end_time, label, x_, y_, source_)

        elif effect_type == "blend":
            try:
                phase = int(params[0])
                cross_params = [p for p in params[1:] if "=" not in p]
                overrides = {p.split("=",1)[0]: p.split("=",1)[1] for p in params[1:] if "=" in p}
            except:
                print("Error: blend requires phase and possibly cross_params/overrides.")
                sys.exit(1)
            filter_part = create_blend_filter(start_time, end_time, label, phase, cross_params, overrides)

        elif effect_type == "chromakey":
            color = params[0] if len(params) > 0 else None
            similarity = float(params[1]) if len(params) > 1 else None
            blend_val = float(params[2]) if len(params) > 2 else None
            filter_part = create_chromakey_filter(start_time, end_time, label, color, similarity, blend_val)

        elif effect_type == "colorkey":
            color = params[0] if len(params) > 0 else None
            similarity = float(params[1]) if len(params) > 1 else None
            blend_val = float(params[2]) if len(params) > 2 else None
            filter_part = create_colorkey_filter(start_time, end_time, label, color, similarity, blend_val)

        elif effect_type == "lumakey":
            try:
                threshold = float(params[0])
            except:
                print("Error: lumakey requires a threshold.")
                sys.exit(1)
            filter_part = create_lumakey_filter(start_time, end_time, label, threshold)

        elif effect_type == "alphamerge":
            filter_part = create_alphamerge_filter(start_time, end_time, label)

        elif effect_type == "alphaextract":
            filter_part = create_alphaextract_filter(start_time, end_time, label)

        elif effect_type == "colorbalance":
            try:
                rs = float(params[0])
                gs = float(params[1])
                bs = float(params[2])
            except:
                print("Error: colorbalance requires rs, gs, bs.")
                sys.exit(1)
            filter_part = create_colorbalance_filter(start_time, end_time, label, rs, gs, bs)

        elif effect_type == "colorchannelmixer":
            # e.g. 9 floats
            try:
                rr, rg, rb, gr, gg, gb, br, bg, bb = map(float, params[:9])
            except:
                print("Error: colorchannelmixer requires 9 floats.")
                sys.exit(1)
            filter_part = create_colorchannelmixer_filter(
                start_time, end_time, label, rr, rg, rb, gr, gg, gb, br, bg, bb
            )

        elif effect_type == "curves":
            curves_str = params[0] if params else None
            filter_part = create_curves_filter(start_time, end_time, label, curves_str)

        elif effect_type == "eq":
            try:
                brightness = float(params[0])
                contrast   = float(params[1])
                gamma      = float(params[2])
                saturation = float(params[3])
            except:
                print("Error: eq requires brightness, contrast, gamma, saturation.")
                sys.exit(1)
            filter_part = create_eq_filter(start_time, end_time, label, brightness, contrast, gamma, saturation)

        elif effect_type == "lut":
            lut_file = params[0] if params else None
            filter_part = create_lut_filter(start_time, end_time, label, lut_file)

        elif effect_type == "lut3d":
            lut3d_file = params[0] if params else None
            filter_part = create_lut3d_filter(start_time, end_time, label, lut3d_file)

        elif effect_type == "haldclut":
            haldclut_file = params[0] if params else None
            filter_part = create_haldclut_filter(start_time, end_time, label, haldclut_file)

        elif effect_type == "drawtext":
            text_      = params[0] if params else None
            x_         = params[1] if len(params) > 1 else None
            y_         = params[2] if len(params) > 2 else None
            fontsize_  = int(params[3]) if len(params) > 3 else None
            fontcolor_ = params[4] if len(params) > 4 else None
            filter_part = create_drawtext_filter(start_time, end_time, label, text_, x_, y_, fontsize_, fontcolor_)

        else:
            # If not recognized, we do a no-effect gap
            filter_part = create_gap_segment_filter(start_time, end_time, label)

        filter_complex_parts.append(filter_part)
        seg_count += 1
        current_time = end_time

    # If there's remaining time after the last effect, fill it with no-effect
    if video_duration > current_time:
        gap_label = f"seg{seg_count}"
        filter_complex_parts.append(
            create_gap_segment_filter(current_time, video_duration, gap_label)
        )
        seg_count += 1

    # Finally, concat all segments
    concat_inputs = "".join([f"[seg{i}]" for i in range(seg_count)])
    filter_complex_parts.append(f"{concat_inputs}concat=n={seg_count}:v=1:a=0[outv]")

    return "; ".join(filter_complex_parts)
