import os
import sys

from utils.ffmpeg_utils import run_command
from utils.metadata import get_video_metadata


def split_video(args) -> None:
    """Extract multiple video segments from an input video."""
    if args.segment is None:
        print("No segments provided; nothing to split.")
        sys.exit(1)
    if not os.path.exists(args.output):
        os.makedirs(args.output)
    for idx, seg in enumerate(args.segment, start=1):
        try:
            start_time: float = float(seg[0])
            end_time: float = float(seg[1])
        except ValueError:
            print(f"Segment {idx} times must be numeric.")
            sys.exit(1)
        duration: float = end_time - start_time
        if duration <= 0:
            print(f"Segment {idx}: End time must be greater than start time.")
            continue
        output_file: str = os.path.join(args.output, f"segment_{idx}.mp4")
        cmd = [
            "ffmpeg", "-y", "-i", args.input,
            "-ss", str(start_time),
            "-t", str(duration),
            "-c", "copy", output_file
        ]
        run_command(cmd)
        print(f"Extracted segment {idx}: {start_time}s to {end_time}s -> {output_file}")


def adjust_segment(args) -> None:
    """Adjust a segment of a video using the original as source."""
    try:
        orig_start: float = float(args.orig_start)
        orig_end: float = float(args.orig_end)
    except ValueError:
        print("orig_start and orig_end must be numeric.")
        sys.exit(1)
    start_offset: float = float(args.start_offset) if args.start_offset is not None else 0.0
    end_offset: float = float(args.end_offset) if args.end_offset is not None else 0.0
    duration_opt, _, _, _, _ = get_video_metadata(args.orig)
    if duration_opt is None:
        print("Error: Could not determine original video duration.")
        sys.exit(1)
    video_duration: float = duration_opt
    new_start: float = orig_start + start_offset
    new_end: float = orig_end + end_offset
    if new_start < 0:
        new_start = 0.0
    if new_end > video_duration:
        new_end = video_duration
    if new_end <= new_start:
        print("Error: new end time must be greater than new start time.")
        sys.exit(1)
    new_duration: float = new_end - new_start
    cmd = [
        "ffmpeg", "-y", "-i", args.orig,
        "-ss", str(new_start),
        "-t", str(new_duration),
        "-c", "copy", args.output
    ]
    run_command(cmd)
    print(f"Adjusted segment extracted from {new_start}s to {new_end}s -> {args.output}")
