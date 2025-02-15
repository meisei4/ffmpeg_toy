import os
import sys
from typing import List

from utils.ffmpeg_utils import run_command
from utils.metadata import has_audio_stream


def mix_audio(args) -> None:
    """Mix external audio tracks into the video."""
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
