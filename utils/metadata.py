import os
import subprocess
from typing import Tuple, Optional, List


def ffprobe(*args: str) -> str:
    output: bytes = subprocess.check_output(["ffprobe", "-v", "error"] + list(args))
    return output.decode().strip()


def get_video_metadata(input_file: str) -> Tuple[Optional[float], Optional[int], Optional[int], Tuple[int, int], int]:
    """Extract video metadata using ffprobe."""
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
    """Calculate the video bitrate in kbps for a target file size."""
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
    """Construct a filter chain based on resolution, denoise and speed parameters."""
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


def has_audio_stream(input_file: str) -> bool:
    """Check whether the input file contains an audio stream."""
    try:
        output = subprocess.check_output(
            ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
             "-of", "csv=p=0", input_file]
        )
        return bool(output.strip())
    except subprocess.CalledProcessError:
        return False
