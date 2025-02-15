import os
import sys
from constants import (
    DEFAULT_TARGET_SIZE_MB, DEFAULT_RESOLUTION, DEFAULT_DENOISE, DEFAULT_PRESET,
    DEFAULT_PREVIEW_DURATION, DEFAULT_SPEED_FACTOR, DEFAULT_AUDIO_BITRATE,
    DEFAULT_MIN_VIDEO_KBPS, DEFAULT_OVERHEAD, DEFAULT_FALLBACK_FPS
)
from utils.ffmpeg_utils import run_command
from utils.metadata import get_video_metadata, calculate_bitrate_kbps, build_filter_string

class CompressVideoCommandBuilder:
    def __init__(self, input_file: str, output_file: str):
        self.input_file = input_file
        self.output_file = output_file

    def analyze_video(self, speed: float):
        duration_opt, in_w, in_h, fps_tuple, size_bytes = get_video_metadata(self.input_file)
        if duration_opt is None:
            print("Error: Could not parse input or zero duration.")
            sys.exit(1)
        duration = duration_opt
        fps_num, fps_den = fps_tuple
        fps_str = DEFAULT_FALLBACK_FPS if fps_den == 0 else f"{fps_num}/{fps_den}"
        print(f"Input: {self.input_file}")
        print(f"Duration: {duration:.2f}s, Resolution: {in_w}x{in_h}, FPS: {fps_str}, Size: {size_bytes / 1e6:.2f} MB")
        effective_dur = duration
        if speed is not None and speed > 0:
            effective_dur /= speed
            print(f"Speed factor {speed:.2f} => effective duration {effective_dur:.2f}s")
        return duration, fps_str, effective_dur

    def build_first_pass(self, video_kbps: int, fps_str: str, vf_str: str, preset: str, preview: int) -> list:
        log_file = "x265_pass.log"
        cmd = [
            "ffmpeg", "-y", "-i", self.input_file,
            "-c:v", "libx265",
            "-b:v", f"{video_kbps}k",
            "-preset", preset,
            "-x265-params", f"pass=1:stats={log_file}:me=star:subme=7:rc-lookahead=60:"
                            "psy-rd=2.0:psy-rdoq=1.0:aq-mode=3:aq-strength=1.0:"
                            "rdoq-level=2:bframes=5:ref=5",
            "-fps_mode", "cfr",
            "-r", fps_str,
            "-an",
            "-f", "null"
        ]
        if vf_str:
            cmd += ["-vf", vf_str]
        if preview > 0:
            cmd += ["-t", str(preview)]
        cmd.append("/dev/null")
        return cmd

    def build_second_pass(self, video_kbps: int, fps_str: str, vf_str: str, preset: str, preview: int, mute: bool) -> list:
        log_file = "x265_pass.log"
        cmd = [
            "ffmpeg", "-y", "-i", self.input_file,
            "-c:v", "libx265",
            "-b:v", f"{video_kbps}k",
            "-preset", preset,
            "-x265-params", f"pass=2:stats={log_file}:me=star:subme=7:rc-lookahead=60:"
                            "psy-rd=2.0:psy-rdoq=1.0:aq-mode=3:aq-strength=1.0:"
                            "rdoq-level=2:bframes=5:ref=5",
            "-fps_mode", "cfr",
            "-r", fps_str
        ]
        if mute:
            cmd += ["-an"]
        else:
            cmd += ["-c:a", "aac", "-b:a", "64k"]
        if vf_str:
            cmd += ["-vf", vf_str]
        if preview > 0:
            cmd += ["-t", str(preview)]
        cmd.append(self.output_file)
        return cmd

    def execute(self, size: int, resolution: str, denoise: str, preset: str, mute: bool, preview: int, speed: float) -> None:
        target_size_mb = size if size is not None else DEFAULT_TARGET_SIZE_MB
        resolution = resolution if resolution is not None else DEFAULT_RESOLUTION
        denoise = denoise if denoise is not None else DEFAULT_DENOISE
        preset = preset if preset is not None else DEFAULT_PRESET
        preview = preview if preview is not None else DEFAULT_PREVIEW_DURATION
        speed = speed if speed is not None else DEFAULT_SPEED_FACTOR

        duration, fps_str, effective_dur = self.analyze_video(speed)
        audio_bps = 0 if mute else DEFAULT_AUDIO_BITRATE
        video_kbps = calculate_bitrate_kbps(target_size_mb, effective_dur, audio_bps, DEFAULT_OVERHEAD, DEFAULT_MIN_VIDEO_KBPS)
        print(f"Target video bitrate: {video_kbps} kb/s")
        vf_str = build_filter_string(resolution, denoise, speed)
        out_for_preview = self.output_file
        if preview > 0:
            out_for_preview = f"preview_{self.output_file}"
            print(f"Preview: first {preview} seconds will be encoded to {out_for_preview}")

        # First pass
        print("\n=== PASS 1: Analyzing ===")
        pass1 = self.build_first_pass(video_kbps, fps_str, vf_str, preset, preview)
        run_command(pass1)
        # Second pass
        print("\n=== PASS 2: Encoding ===")
        pass2 = self.build_second_pass(video_kbps, fps_str, vf_str, preset, preview, mute)
        run_command(pass2)
        if not os.path.exists(out_for_preview):
            print(f"Error: Output file {out_for_preview} was not created.")
            sys.exit(1)
        out_size = os.path.getsize(out_for_preview) / (1024 * 1024)
        print("\n===== RESULTS =====")
        print(f"Output File: {out_for_preview}")
        print(f"Size: {out_size:.2f} MB")
        if preview > 0:
            print(f"\nPreview done => '{out_for_preview}'. Re-run without --preview for the full encode.\n")

def compress_video_command(args) -> None:
    builder = CompressVideoCommandBuilder(args.input, args.output)
    builder.execute(args.size, args.resolution, args.denoise, args.preset, args.mute, args.preview, args.speed)
