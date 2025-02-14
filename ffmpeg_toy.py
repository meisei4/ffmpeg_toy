#!/usr/bin/env python3
"""
Generic Video Editing Tool using FFmpeg

Sub-commands:
  audioprocess: Process an audio file by cutting a segment and looping a portion.
  compress: Compress a video to a target file size.
  mix: Mix external audio tracks into the video.
  effects: Apply video effects over specified time segments.
  split: Extract multiple video segments from an input video.
  adjust: Adjust a segment using the original video as source.
  sync: Synchronize video by playing a glitched, time-warped portion until a musical cue,
        then switching to a splice segment whose playback rate is adjusted to finish at the cue end.
"""

import argparse
import subprocess
import os
import sys
import math
from typing import Tuple, Optional, List

# ----------------------------------------------------------------------------
# Global Default Constants for Compression Processing
# ----------------------------------------------------------------------------
DEFAULT_TARGET_SIZE_MB: int = 10  # Target video size in MB
DEFAULT_RESOLUTION: str = "lowest"  # Scale resolution ("lowest", "480p", "720p", or custom)
DEFAULT_DENOISE: str = "med"  # Denoise strength ("off", "low", "med", "high")
DEFAULT_PRESET: str = "slower"  # x265 preset
DEFAULT_MUTE_AUDIO: bool = False  # Whether to strip audio in compress mode
DEFAULT_PREVIEW_DURATION: int = 0  # Seconds to encode for preview (0 means full video)
DEFAULT_SPEED_FACTOR: Optional[float] = None  # Playback speed factor (None means no change)

DEFAULT_AUDIO_BITRATE: int = 64000  # Audio bitrate (in bits per second)
DEFAULT_MIN_VIDEO_KBPS: int = 100  # Minimum video bitrate in kb/s
DEFAULT_OVERHEAD: float = 0.02  # Overhead factor for bitrate calculation
DEFAULT_FALLBACK_FPS: str = "30"  # Fallback frames per second


# ----------------------------------------------------------------------------
# Helper Functions
# ----------------------------------------------------------------------------
def ffprobe(*args: str) -> str:
    output: bytes = subprocess.check_output(["ffprobe", "-v", "error"] + list(args))
    return output.decode().strip()


def get_video_metadata(input_file: str) -> Tuple[Optional[float], Optional[int], Optional[int], Tuple[int, int], int]:
    duration: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    fps_num: int = 30
    fps_den: int = 1
    size_bytes: int = 0
    try:
        duration_str: str = ffprobe("-select_streams", "v:0", "-show_entries", "format=duration",
                                    "-of", "default=noprint_wrappers=1:nokey=1", input_file)
        duration = float(duration_str)
        width_str: str = ffprobe("-select_streams", "v:0", "-show_entries", "stream=width",
                                 "-of", "default=noprint_wrappers=1:nokey=1", input_file)
        width = int(width_str)
        height_str: str = ffprobe("-select_streams", "v:0", "-show_entries", "stream=height",
                                  "-of", "default=noprint_wrappers=1:nokey=1", input_file)
        height = int(height_str)
        fps_str: str = ffprobe("-select_streams", "v:0", "-show_entries", "stream=r_frame_rate",
                               "-of", "default=noprint_wrappers=1:nokey=1", input_file)
        parts: List[str] = fps_str.split("/")
        if len(parts) == 2 and parts[1] != "0":
            fps_num = int(parts[0])
            fps_den = int(parts[1])
        size_bytes = os.path.getsize(input_file)
    except Exception:
        pass
    return duration, width, height, (fps_num, fps_den), size_bytes


def calculate_bitrate_kbps(target_size_mb: int, duration: float, audio_bitrate_bps: int, overhead: float,
                           min_video_kbps: int) -> int:
    if duration <= 0:
        print("Warning: invalid duration; using fallback bitrate of 200 kb/s")
        return 200
    total_bits: int = target_size_mb * 8_000_000
    usable_bits: float = total_bits * (1 - overhead)
    video_bits: float = usable_bits - (audio_bitrate_bps * duration)
    video_bps: float = video_bits / duration
    video_kbps: int = max(min_video_kbps, int(video_bps / 1000))
    return video_kbps


def build_filter_string(resolution: Optional[str], denoise_strength: Optional[str], speed_factor: Optional[float]) -> \
Optional[str]:
    filters: List[str] = []
    if resolution is not None:
        if resolution == "lowest":
            filters.append("scale=640:-2")
        elif resolution == "480p":
            filters.append("scale=854:-2")
        elif resolution == "720p":
            filters.append("scale=1280:-2")
        else:
            filters.append(f"scale={resolution}")
    if denoise_strength is not None and denoise_strength != "off":
        if denoise_strength == "low":
            filters.append("hqdn3d=1:1:2:3")
        elif denoise_strength == "med":
            filters.append("hqdn3d=2:1:2:3")
        elif denoise_strength == "high":
            filters.append("hqdn3d=3:2:3:4")
    if speed_factor is not None and speed_factor > 0:
        factor: float = 1.0 / speed_factor
        filters.append(f"setpts={factor}*PTS")
    return ",".join(filters) if filters else None


def run_command(cmd: List[str]) -> None:
    print("Running command:")
    print(" ".join(cmd))
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print("Command failed!")
        sys.exit(1)


def copy_file(input_file: str, output_file: str) -> None:
    print("No processing parameters provided; copying file directly.")
    cmd: List[str] = ["ffmpeg", "-y", "-i", input_file, "-c", "copy", output_file]
    run_command(cmd)


def has_audio_stream(input_file: str) -> bool:
    try:
        output = subprocess.check_output(
            ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0",
             input_file]
        )
        return bool(output.strip())
    except subprocess.CalledProcessError:
        return False


# ----------------------------------------------------------------------------
# Sub-Command Implementations
# ----------------------------------------------------------------------------
def process_audio(args: argparse.Namespace) -> None:
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


def compress_video(args: argparse.Namespace) -> None:
    target_size_mb: int = args.size if args.size is not None else DEFAULT_TARGET_SIZE_MB
    resolution: str = args.resolution if args.resolution is not None else DEFAULT_RESOLUTION
    denoise: str = args.denoise if args.denoise is not None else DEFAULT_DENOISE
    preset: str = args.preset if args.preset is not None else DEFAULT_PRESET
    mute: bool = args.mute
    preview: int = args.preview if args.preview is not None else DEFAULT_PREVIEW_DURATION
    speed: Optional[float] = args.speed if args.speed is not None else DEFAULT_SPEED_FACTOR
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
    vf_str: Optional[str] = build_filter_string(resolution, denoise, speed)
    out_for_preview: str = args.output
    if preview > 0:
        out_for_preview = f"preview_{args.output}"
        print(f"Preview: first {preview} seconds will be encoded to {out_for_preview}")
    log_file: str = "x265_pass.log"
    pass1_cmd: List[str] = [
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
    pass2_cmd: List[str] = [
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


def mix_audio(args: argparse.Namespace) -> None:
    primary_has_audio: bool = has_audio_stream(args.input)
    inputs: List[str] = ["-i", args.input]
    filter_complex_parts: List[str] = []
    audio_labels: List[str] = []
    if primary_has_audio:
        audio_labels.append("[0:a]")
    input_index: int = 1
    if args.mix is not None:
        for item in args.mix:
            try:
                start_time: float = float(item[0])
                audio_file: str = item[1]
            except Exception as e:
                print(f"Error parsing mix item {item}: {e}")
                sys.exit(1)
            if not os.path.exists(audio_file):
                print(f"Audio file {audio_file} not found!")
                sys.exit(1)
            inputs += ["-i", audio_file]
            delay_ms: int = int(start_time * 1000)
            label: str = f"a{input_index}"
            filter_complex_parts.append(f"[{input_index}:a]adelay={delay_ms}|{delay_ms}[{label}]")
            audio_labels.append(f"[{label}]")
            input_index += 1
    if not audio_labels:
        print("No audio streams available to mix.")
        sys.exit(1)
    audio_inputs: str = "".join(audio_labels)
    num_inputs: int = len(audio_labels)
    filter_complex_parts.append(f"{audio_inputs}amix=inputs={num_inputs}:duration=shortest[outa]")
    filter_complex: str = "; ".join(filter_complex_parts)
    print("Constructed audio filter_complex:")
    print(filter_complex)
    cmd: List[str] = ["ffmpeg", "-y"] + inputs + [
        "-filter_complex", filter_complex,
        "-map", "0:v",
        "-map", "[outa]",
        "-c:v", "copy",
        "-c:a", "aac",
        args.output
    ]
    run_command(cmd)


def apply_video_effects(args: argparse.Namespace) -> None:
    if args.effect is None:
        copy_file(args.input, args.output)
        return
    effect_items: List[Tuple[float, float, str, Optional[float]]] = []
    for item in args.effect:
        try:
            start_time: float = float(item[0])
            end_time: float = float(item[1])
            filters: str = item[2]
            speed: Optional[float] = float(item[3]) if len(item) > 3 else None
            effect_items.append((start_time, end_time, filters, speed))
        except Exception as e:
            print(f"Error parsing effect item {item}: {e}")
            sys.exit(1)
    effect_items.sort(key=lambda x: x[0])
    filter_complex_parts: List[str] = []
    seg_count: int = 0
    current_time: float = 0.0
    for effect in effect_items:
        start_time, end_time, filters, speed = effect
        if current_time < start_time:
            label: str = f"seg{seg_count}"
            filter_complex_parts.append(f"[0:v]trim=start={current_time}:end={start_time},setpts=PTS-STARTPTS[{label}]")
            seg_count += 1
        label = f"seg{seg_count}"
        segment_filters: List[str] = [f"trim=start={start_time}:end={end_time}", "setpts=PTS-STARTPTS"]
        if speed is not None and speed > 0:
            segment_filters.append(f"setpts={1.0 / speed}*PTS")
        if filters:
            segment_filters.append(filters)
        chain: str = ",".join(segment_filters)
        filter_complex_parts.append(f"[0:v]{chain}[{label}]")
        seg_count += 1
        current_time = end_time
    video_duration: float = get_video_metadata(args.input)[0]
    if video_duration is not None and current_time < video_duration:
        label: str = f"seg{seg_count}"
        filter_complex_parts.append(f"[0:v]trim=start={current_time}:end={video_duration},setpts=PTS-STARTPTS[{label}]")
        seg_count += 1
    concat_inputs: str = "".join([f"[seg{i}]" for i in range(seg_count)])
    filter_complex_parts.append(f"{concat_inputs}concat=n={seg_count}:v=1:a=0[outv]")
    filter_complex: str = "; ".join(filter_complex_parts)
    print("Constructed filter_complex:")
    print(filter_complex)
    cmd: List[str] = [
        "ffmpeg", "-y", "-i", args.input,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-c:v", "libx265",
        args.output
    ]
    run_command(cmd)


def split_video(args: argparse.Namespace) -> None:
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
        cmd: List[str] = [
            "ffmpeg", "-y", "-i", args.input,
            "-ss", str(start_time),
            "-t", str(duration),
            "-c", "copy", output_file
        ]
        run_command(cmd)
        print(f"Extracted segment {idx}: {start_time}s to {end_time}s -> {output_file}")


def adjust_segment(args: argparse.Namespace) -> None:
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
    cmd: List[str] = [
        "ffmpeg", "-y", "-i", args.orig,
        "-ss", str(new_start),
        "-t", str(new_duration),
        "-c", "copy", args.output
    ]
    run_command(cmd)
    print(f"Adjusted segment extracted from {new_start}s to {new_end}s -> {args.output}")


def sync_video(args: argparse.Namespace) -> None:
    """
    Create a synchronized video that plays a glitched, time-warped version of the original video
    up until a musical cue, then switches to a splice segment whose playback rate is adjusted to finish exactly
    when the musical cue ends.

    Required parameters:
      --audio-cue: Time (in seconds) in the audio when the splice should start.
      --cue-end: Time (in seconds) in the audio when the splice should end.
      --segment-start: Original start time (in seconds) of the splice segment.
      --segment-end: Original end time (in seconds) of the splice segment.

    Optional parameter:
      --glitch-filter: Custom filter chain for the glitched portion (default: "rgbashift=rh=10:rv=10,boxblur=2:1")

    Process:
      1. Compute time_factor_glitch = audio_cue / segment_start.
         (This stretches the portion from 0 to segment_start to last until the audio cue.)
      2. Compute splice_original_duration = segment_end - segment_start.
      3. Compute desired_splice_duration = cue_end - audio_cue.
         Then, compute splice_speed_factor = splice_original_duration / desired_splice_duration.
         (The splice segment will be sped up by this factor so that its output duration equals desired_splice_duration.)
      4. Build a filter_complex:
         - Part 1: Glitched portion from 0 to segment_start, with setpts=PTS * time_factor_glitch and the glitch filter applied.
         - Part 2: Splice portion from segment_start to segment_end, with setpts adjusted by factor 1/splice_speed_factor.
         - Concatenate the two portions.
    """
    try:
        audio_cue: float = float(args.audio_cue)
        cue_end: float = float(args.cue_end)
        seg_start: float = float(args.segment_start)
        seg_end: float = float(args.segment_end)
    except ValueError:
        print("audio-cue, cue-end, segment-start, and segment-end must be numeric.")
        sys.exit(1)

    if seg_start <= 0 or seg_end <= seg_start:
        print("Invalid segment times: Ensure segment_start > 0 and segment_end > segment_start.")
        sys.exit(1)
    if cue_end <= audio_cue:
        print("Invalid cue times: cue-end must be greater than audio-cue.")
        sys.exit(1)

    # Compute time factor for glitched portion (stretching 0..seg_start to last until audio_cue)
    time_factor_glitch: float = audio_cue / seg_start
    print(f"Calculated time_factor_glitch: {time_factor_glitch:.2f} (to stretch {seg_start}s to {audio_cue}s)")

    # Compute splice segment speed adjustment.
    splice_original_duration: float = seg_end - seg_start
    desired_splice_duration: float = cue_end - audio_cue
    splice_speed_factor: float = splice_original_duration / desired_splice_duration
    # To speed up the splice, use setpts=PTS/(splice_speed_factor)
    print(
        f"Calculated splice_speed_factor: {splice_speed_factor:.2f} (to compress {splice_original_duration}s to {desired_splice_duration}s)")

    glitch_filter: str = args.glitch_filter if args.glitch_filter is not None else "rgbashift=rh=10:rv=10,boxblur=2:1"

    filter_complex: str = (
        f"[0:v]trim=start=0:end={seg_start},setpts=PTS*{time_factor_glitch}[glitch]; "
        f"[glitch]{glitch_filter}[glitch_out]; "
        f"[0:v]trim=start={seg_start}:end={seg_end},setpts=(PTS-STARTPTS)/{splice_speed_factor}[splice]; "
        f"[glitch_out][splice]concat=n=2:v=1:a=0[outv]"
    )
    print("Constructed filter_complex:")
    print(filter_complex)

    cmd: List[str] = [
        "ffmpeg", "-y", "-i", args.input,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-c:v", "libx265",
        args.output
    ]
    run_command(cmd)
    print(f"Synchronized video saved to {args.output}")


# ----------------------------------------------------------------------------
# Main Entry Point
# ----------------------------------------------------------------------------
def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Generic Video Editing Tool using FFmpeg")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Sub-commands")
    # audioprocess sub-command
    audioprocess_parser = subparsers.add_parser("audioprocess", help="Process an audio file: cut and loop segments")
    audioprocess_parser.add_argument("input", help="Input audio file")
    audioprocess_parser.add_argument("output", help="Output processed audio file")
    audioprocess_parser.add_argument("--cut-duration", type=float, help="Duration (in seconds) to cut from start")
    audioprocess_parser.add_argument("--loop-start", type=float, help="Loop segment start time (in seconds)")
    audioprocess_parser.add_argument("--loop-end", type=float, help="Loop segment end time (in seconds)")
    audioprocess_parser.add_argument("--loop-total", type=float, help="Total duration (in seconds) for looped segment")
    # compress sub-command
    compress_parser = subparsers.add_parser("compress", help="Compress video to a target size")
    compress_parser.add_argument("input", help="Input video file")
    compress_parser.add_argument("output", help="Output video file")
    compress_parser.add_argument("--size", type=int, help="Target file size in MB")
    compress_parser.add_argument("--resolution", help="Scale resolution (e.g. '640:-2')")
    compress_parser.add_argument("--denoise", help="Denoise strength (off, low, med, high)")
    compress_parser.add_argument("--preset", help="x265 preset")
    compress_parser.add_argument("--mute", action="store_true", help="Strip audio track")
    compress_parser.add_argument("--preview", type=int, help="Encode only first N seconds for testing")
    compress_parser.add_argument("--speed", type=float, help="Playback speed factor")
    # mix sub-command
    mix_parser = subparsers.add_parser("mix", help="Mix external audio tracks into the video")
    mix_parser.add_argument("input", help="Input video file")
    mix_parser.add_argument("output", help="Output video file")
    mix_parser.add_argument("--mix", nargs=2, action="append", metavar=("START", "FILE"),
                            help="Mix item: start time and audio file (can be repeated)")
    # effects sub-command
    effects_parser = subparsers.add_parser("effects", help="Apply video effects over specified time segments")
    effects_parser.add_argument("input", help="Input video file")
    effects_parser.add_argument("output", help="Output video file")
    effects_parser.add_argument("--effect", nargs="+", action="append",
                                metavar="EFFECT_ITEM",
                                help="Effect item: start, end, filters, [speed] (can be repeated)")
    # split sub-command
    split_parser = subparsers.add_parser("split", help="Extract video segments into separate files")
    split_parser.add_argument("input", help="Input video file")
    split_parser.add_argument("output", help="Output directory for segments")
    split_parser.add_argument("--segment", nargs=2, action="append", metavar=("START", "END"),
                              help="Segment to extract: start and end times in seconds (can be repeated)")
    # adjust sub-command
    adjust_parser = subparsers.add_parser("adjust", help="Adjust a segment using the original video as source")
    adjust_parser.add_argument("orig", help="Original video file")
    adjust_parser.add_argument("output", help="Output adjusted segment file")
    adjust_parser.add_argument("--orig-start", required=True, help="Original start time of the segment in seconds")
    adjust_parser.add_argument("--orig-end", required=True, help="Original end time of the segment in seconds")
    adjust_parser.add_argument("--start-offset", type=float,
                               help="Offset to add to the original start time (negative to add before)")
    adjust_parser.add_argument("--end-offset", type=float,
                               help="Offset to add to the original end time (positive to add after)")
    # sync sub-command (new for TEST 3, extended for splice speed adjustment)
    sync_parser = subparsers.add_parser("sync",
                                        help="Synchronize glitched video with a musical cue and splice in a segment")
    sync_parser.add_argument("input", help="Input video file")
    sync_parser.add_argument("output", help="Output video file")
    sync_parser.add_argument("--audio-cue", required=True,
                             help="Time (in seconds) in the audio when the splice should start")
    sync_parser.add_argument("--cue-end", required=True,
                             help="Time (in seconds) in the audio when the splice should end")
    sync_parser.add_argument("--segment-start", required=True,
                             help="Original start time of the splice segment (in seconds)")
    sync_parser.add_argument("--segment-end", required=True,
                             help="Original end time of the splice segment (in seconds)")
    sync_parser.add_argument("--glitch-filter",
                             help="Custom filter chain for the glitched portion (default: 'rgbashift=rh=10:rv=10,boxblur=2:1')")

    args: argparse.Namespace = parser.parse_args()
    if args.command == "audioprocess":
        process_audio(args)
    elif args.command == "compress":
        compress_video(args)
    elif args.command == "mix":
        mix_audio(args)
    elif args.command == "effects":
        apply_video_effects(args)
    elif args.command == "split":
        split_video(args)
    elif args.command == "adjust":
        adjust_segment(args)
    elif args.command == "sync":
        sync_video(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
