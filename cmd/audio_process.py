import os
from typing import List

import math

from utils.ffmpeg_utils import run_command, copy_file


def process_audio(args) -> None:
    """
    Process an audio file by cutting a segment and looping a portion.
    If no processing parameters are provided, simply copy the file.
    """
    if (args.cut_duration is None and args.loop_start is None and
            args.loop_end is None and args.loop_total is None):
        copy_file(args.input, args.output)
        return

    cut_duration: float = args.cut_duration
    loop_start: float = args.loop_start
    loop_end: float = args.loop_end
    loop_total: float = args.loop_total

    part_file: str = "temp_part.mp3"
    cmd1: List[str] = [
        "ffmpeg", "-y", "-i", args.input,
        "-t", str(cut_duration),
        "-c", "copy", part_file
    ]
    run_command(cmd1)

    loop_duration: float = loop_end - loop_start
    loop_file: str = "temp_loop.mp3"
    cmd2: List[str] = [
        "ffmpeg", "-y", "-i", args.input,
        "-ss", str(loop_start),
        "-t", str(loop_duration),
        "-c", "copy", loop_file
    ]
    run_command(cmd2)

    total_loops: int = math.ceil(loop_total / loop_duration) - 1
    loop_full_file: str = "temp_loop_full.mp3"
    cmd3: List[str] = [
        "ffmpeg", "-y", "-stream_loop", str(total_loops),
        "-i", loop_file,
        "-t", str(loop_total),
        "-c", "copy", loop_full_file
    ]
    run_command(cmd3)

    concat_list_file: str = "concat_list.txt"
    with open(concat_list_file, "w", encoding="utf-8") as f:
        f.write(f"file '{os.path.abspath(part_file)}'\n")
        f.write(f"file '{os.path.abspath(loop_full_file)}'\n")

    cmd4: List[str] = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_list_file,
        "-c", "copy", args.output
    ]
    run_command(cmd4)
    print(f"Processed audio saved to {args.output}")
