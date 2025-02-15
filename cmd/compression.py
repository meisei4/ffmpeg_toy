import os
import sys

from constants import (
    DEFAULT_TARGET_SIZE_MB, DEFAULT_RESOLUTION, DEFAULT_DENOISE, DEFAULT_PRESET,
    DEFAULT_PREVIEW_DURATION, DEFAULT_SPEED_FACTOR, DEFAULT_AUDIO_BITRATE,
    DEFAULT_MIN_VIDEO_KBPS, DEFAULT_OVERHEAD, DEFAULT_FALLBACK_FPS
)
from utils.ffmpeg_utils import run_command
from utils.metadata import get_video_metadata, calculate_bitrate_kbps, build_filter_string


def compress_video(args) -> None:
    """Compress a video file to a target size using two-pass encoding."""
    target_size_mb: int = args.size if args.size is not None else DEFAULT_TARGET_SIZE_MB
    resolution: str = args.resolution if args.resolution is not None else DEFAULT_RESOLUTION
    denoise: str = args.denoise if args.denoise is not None else DEFAULT_DENOISE
    preset: str = args.preset if args.preset is not None else DEFAULT_PRESET
    mute: bool = args.mute
    preview: int = args.preview if args.preview is not None else DEFAULT_PREVIEW_DURATION
    speed: float = args.speed if args.speed is not None else DEFAULT_SPEED_FACTOR

    duration_opt, in_w, in_h, fps_tuple, size_bytes = get_video_metadata(args.input)
    if duration_opt is None:
        print("Error: Could not parse input or zero duration.")
        sys.exit(1)
    duration: float = duration_opt
    fps_num, fps_den = fps_tuple
    fps_str: str = DEFAULT_FALLBACK_FPS if fps_den == 0 else f"{fps_num}/{fps_den}"
    print(f"Input: {args.input}")
    print(f"Duration: {duration:.2f}s, Resolution: {in_w}x{in_h}, FPS: {fps_str}, Size: {size_bytes / 1e6:.2f} MB")

    effective_dur: float = duration
    if speed is not None and speed > 0:
        effective_dur /= speed
        print(f"Speed factor {speed:.2f} => effective duration {effective_dur:.2f}s")
    audio_bps: int = 0 if mute else DEFAULT_AUDIO_BITRATE
    video_kbps: int = calculate_bitrate_kbps(target_size_mb, effective_dur, audio_bps, DEFAULT_OVERHEAD,
                                             DEFAULT_MIN_VIDEO_KBPS)
    print(f"Target video bitrate: {video_kbps} kb/s")
    vf_str: str = build_filter_string(resolution, denoise, speed)
    out_for_preview: str = args.output
    if preview > 0:
        out_for_preview = f"preview_{args.output}"
        print(f"Preview: first {preview} seconds will be encoded to {out_for_preview}")

    log_file: str = "x265_pass.log"
    # First pass: analysis
    pass1_cmd = [
        "ffmpeg", "-y", "-i", args.input,
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
    if vf_str is not None:
        pass1_cmd += ["-vf", vf_str]
    if preview > 0:
        pass1_cmd += ["-t", str(preview)]
    pass1_cmd.append("/dev/null")
    print("\n=== PASS 1: Analyzing ===")
    run_command(pass1_cmd)

    # Second pass: encoding
    pass2_cmd = [
        "ffmpeg", "-y", "-i", args.input,
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
        pass2_cmd += ["-an"]
    else:
        pass2_cmd += ["-c:a", "aac", "-b:a", "64k"]
    if vf_str is not None:
        pass2_cmd += ["-vf", vf_str]
    if preview > 0:
        pass2_cmd += ["-t", str(preview)]
    pass2_cmd.append(out_for_preview)
    print("\n=== PASS 2: Encoding ===")
    run_command(pass2_cmd)

    if not os.path.exists(out_for_preview):
        print(f"Error: Output file {out_for_preview} was not created.")
        sys.exit(1)
    out_size: float = os.path.getsize(out_for_preview) / (1024 * 1024)
    print("\n===== RESULTS =====")
    print(f"Output File: {out_for_preview}")
    print(f"Size: {out_size:.2f} MB")
    if preview > 0:
        print(f"\nPreview done => '{out_for_preview}'. Re-run without --preview for the full encode.\n")
