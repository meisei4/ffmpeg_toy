from cmd.filters.effects_engine import parse_effect_items, create_filter_complex
from utils.ffmpeg_utils import run_command, copy_file


def apply_filters(args) -> None:
    if not args.effect:
        copy_file(args.input, args.output)
        return

    effect_items = parse_effect_items(args.effect)

    filter_complex = create_filter_complex(args.input, effect_items)
    print("Constructed filter_complex:")
    print(filter_complex)

    cmd = [
        "ffmpeg", "-y",
        "-i", args.input,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-c:v", "libx265",
    ]

    if not args.no_audio:
        cmd.extend(["-map", "0:a?", "-c:a", "copy"])

    cmd.append(args.output)
    run_command(cmd)
