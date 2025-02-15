import os
import sys
import math
from typing import List
from utils.ffmpeg_utils import run_command, copy_file

class ProcessAudioCommandBuilder:
    def __init__(self, input_file: str, output_file: str):
        self.input_file = input_file
        self.output_file = output_file
        self.temp_files: List[str] = []

    def cut_audio(self, cut_duration: float) -> str:
        part_file = "temp_part.mp3"
        cmd = [
            "ffmpeg", "-y", "-i", self.input_file,
            "-t", str(cut_duration),
            "-c", "copy", part_file
        ]
        run_command(cmd)
        self.temp_files.append(part_file)
        return part_file

    def loop_audio(self, loop_start: float, loop_end: float, loop_total: float) -> str:
        loop_duration = loop_end - loop_start
        loop_file = "temp_loop.mp3"
        cmd = [
            "ffmpeg", "-y", "-i", self.input_file,
            "-ss", str(loop_start),
            "-t", str(loop_duration),
            "-c", "copy", loop_file
        ]
        run_command(cmd)
        self.temp_files.append(loop_file)

        total_loops = math.ceil(loop_total / loop_duration) - 1
        loop_full_file = "temp_loop_full.mp3"
        cmd = [
            "ffmpeg", "-y", "-stream_loop", str(total_loops),
            "-i", loop_file,
            "-t", str(loop_total),
            "-c", "copy", loop_full_file
        ]
        run_command(cmd)
        self.temp_files.append(loop_full_file)
        return loop_full_file

    def concatenate(self, part_file: str, loop_full_file: str) -> None:
        concat_list_file = "concat_list.txt"
        with open(concat_list_file, "w", encoding="utf-8") as f:
            f.write(f"file '{os.path.abspath(part_file)}'\n")
            f.write(f"file '{os.path.abspath(loop_full_file)}'\n")
        cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", concat_list_file,
            "-c", "copy", self.output_file
        ]
        run_command(cmd)
        print(f"Processed audio saved to {self.output_file}")

    def execute(self, cut_duration: float, loop_start: float, loop_end: float, loop_total: float) -> None:
        if cut_duration is None and loop_start is None and loop_end is None and loop_total is None:
            copy_file(self.input_file, self.output_file)
            return
        part = self.cut_audio(cut_duration)
        loop_full = self.loop_audio(loop_start, loop_end, loop_total)
        self.concatenate(part, loop_full)

def process_audio_command(args) -> None:
    builder = ProcessAudioCommandBuilder(args.input, args.output)
    builder.execute(args.cut_duration, args.loop_start, args.loop_end, args.loop_total)
