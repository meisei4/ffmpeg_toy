import os
import sys
from typing import List
from utils.ffmpeg_utils import run_command
from utils.metadata import has_audio_stream

class MixAudioCommandBuilder:
    def __init__(self, primary_input: str, output: str):
        self.primary_input = primary_input
        self.output = output
        self.inputs: List[str] = ["-i", primary_input]
        self.filter_complex_parts: List[str] = []
        self.audio_labels: List[str] = []
        self.input_index: int = 1

        if has_audio_stream(primary_input):
            self.audio_labels.append("[0:a]")

    def add_mix_item(self, start_time: float, audio_file: str) -> "MixAudioCommandBuilder":
        if not os.path.exists(audio_file):
            print(f"Audio file {audio_file} not found!")
            sys.exit(1)
        self.inputs += ["-i", audio_file]
        delay_ms: int = int(start_time * 1000)
        label: str = f"a{self.input_index}"
        self.filter_complex_parts.append(
            f"[{self.input_index}:a]adelay={delay_ms}|{delay_ms}[{label}]"
        )
        self.audio_labels.append(f"[{label}]")
        self.input_index += 1
        return self

    def build_filter_complex(self) -> str:
        if not self.audio_labels:
            print("No audio streams available to mix.")
            sys.exit(1)
        audio_inputs = "".join(self.audio_labels)
        num_inputs = len(self.audio_labels)
        self.filter_complex_parts.append(f"{audio_inputs}amix=inputs={num_inputs}:duration=shortest[outa]")
        return "; ".join(self.filter_complex_parts)

    def build_command(self) -> List[str]:
        filter_complex = self.build_filter_complex()
        print("Constructed audio filter_complex:")
        print(filter_complex)
        cmd: List[str] = (
            ["ffmpeg", "-y"] +
            self.inputs +
            ["-filter_complex", filter_complex,
             "-map", "0:v",
             "-map", "[outa]",
             "-c:v", "copy",
             "-c:a", "aac",
             self.output]
        )
        return cmd

    def execute(self) -> None:
        cmd = self.build_command()
        run_command(cmd)

def mix_audio_command(args) -> None:
    builder = MixAudioCommandBuilder(args.input, args.output)
    if args.mix is not None:
        for item in args.mix:
            try:
                start_time = float(item[0])
                audio_file = item[1]
            except Exception as e:
                print(f"Error parsing mix item {item}: {e}")
                sys.exit(1)
            builder.add_mix_item(start_time, audio_file)
    builder.execute()
