# video_effects.py

from utils.ffmpeg_utils import run_command, copy_file
from cmd.filters.effects_engine import parse_effect_items, create_filter_complex

def apply_video_effects(args) -> None:
    """
    Plain function that applies effects to a video by constructing a single ffmpeg
    command with a complex filter (no classes, no builder).
    """
    # If no --effect given, just copy input to output
    if not args.effect:
        copy_file(args.input, args.output)
        return

    # Parse the effect items from the argument list
    effect_items = parse_effect_items(args.effect)

    # Create the final filter_complex string
    filter_complex = create_filter_complex(args.input, effect_items)
    print("Constructed filter_complex:")
    print(filter_complex)

    # Build a basic ffmpeg command
    cmd = [
        "ffmpeg", "-y",
        "-i", args.input,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-c:v", "libx265",
        args.output
    ]
    run_command(cmd)
