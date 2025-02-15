import os
import sys
from typing import List
from utils.ffmpeg_utils import run_command

class SplitVideoCommandBuilder:
    def __init__(self, input_file: str, output_dir: str):
        self.input_file = input_file
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def build_segment(self, start_time: float, end_time: float, segment_idx: int) -> List[str]:
        duration = end_time - start_time
        if duration <= 0:
            print(f"Segment {segment_idx}: End time must be greater than start time.")
            sys.exit(1)
        output_file = os.path.join(self.output_dir, f"segment_{segment_idx}.mp4")
        cmd = [
            "ffmpeg", "-y", "-i", self.input_file,
            "-ss", str(start_time),
            "-t", str(duration),
            "-c", "copy", output_file
        ]
        return cmd

    def execute(self, segments: List[List[str]]) -> None:
        for idx, seg in enumerate(segments, start=1):
            try:
                start_time = float(seg[0])
                end_time = float(seg[1])
            except ValueError:
                print(f"Segment {idx} times must be numeric.")
                sys.exit(1)
            cmd = self.build_segment(start_time, end_time, idx)
            run_command(cmd)
            print(f"Extracted segment {idx}: {start_time}s to {end_time}s -> {os.path.join(self.output_dir, f'segment_{idx}.mp4')}")

class AdjustSegmentCommandBuilder:
    def __init__(self, orig_file: str, output_file: str):
        self.orig_file = orig_file
        self.output_file = output_file

    def execute(self, orig_start: float, orig_end: float, start_offset: float, end_offset: float) -> None:
        from utils.metadata import get_video_metadata
        try:
            duration_opt, _, _, _, _ = get_video_metadata(self.orig_file)
        except Exception:
            print("Error: Could not determine original video duration.")
            sys.exit(1)
        video_duration = duration_opt if duration_opt is not None else 0.0
        new_start = orig_start + (start_offset if start_offset is not None else 0.0)
        new_end = orig_end + (end_offset if end_offset is not None else 0.0)
        if new_start < 0:
            new_start = 0.0
        if new_end > video_duration:
            new_end = video_duration
        if new_end <= new_start:
            print("Error: new end time must be greater than new start time.")
            sys.exit(1)
        cmd = [
            "ffmpeg", "-y", "-i", self.orig_file,
            "-ss", str(new_start),
            "-t", str(new_end - new_start),
            "-c", "copy", self.output_file
        ]
        run_command(cmd)
        print(f"Adjusted segment extracted from {new_start}s to {new_end}s -> {self.output_file}")

def split_video_command(args) -> None:
    if args.segment is None:
        print("No segments provided; nothing to split.")
        sys.exit(1)
    builder = SplitVideoCommandBuilder(args.input, args.output)
    builder.execute(args.segment)

def adjust_segment_command(args) -> None:
    try:
        orig_start = float(args.orig_start)
        orig_end = float(args.orig_end)
    except ValueError:
        print("orig_start and orig_end must be numeric.")
        sys.exit(1)
    start_offset = float(args.start_offset) if args.start_offset is not None else 0.0
    end_offset = float(args.end_offset) if args.end_offset is not None else 0.0
    builder = AdjustSegmentCommandBuilder(args.orig, args.output)
    builder.execute(orig_start, orig_end, start_offset, end_offset)
