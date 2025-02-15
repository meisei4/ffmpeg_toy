import sys
from utils.ffmpeg_utils import run_command

class SyncVideoCommandBuilder:
    def __init__(self, input_file: str, output_file: str):
        self.input_file = input_file
        self.output_file = output_file

    def compute_factors(self, audio_cue: float, seg_start: float, seg_end: float, cue_end: float):
        time_factor = audio_cue / seg_start
        splice_original_duration = seg_end - seg_start
        desired_splice_duration = cue_end - audio_cue
        speed_factor = splice_original_duration / desired_splice_duration
        print(f"Time stretch factor: {time_factor:.2f}")
        print(f"Speed factor: {speed_factor:.2f}")
        return time_factor, speed_factor

    def build_filter_complex(self, seg_start: float, seg_end: float, time_factor: float, speed_factor: float) -> str:
        return (
            f"[1:v]trim=start=0:end={seg_start},setpts=PTS*{time_factor}[seg1]; "
            f"[1:v]trim=start={seg_start}:end={seg_end},setpts=(PTS-STARTPTS)/{speed_factor}[seg2]; "
            f"[seg1][seg2]concat=n=2:v=1:a=0[outv]"
        )

    def execute(self, audio_cue: float, cue_end: float, seg_start: float, seg_end: float) -> None:
        if seg_start <= 0 or seg_end <= seg_start:
            print("Invalid segment times.")
            sys.exit(1)
        if cue_end <= audio_cue:
            print("Invalid cue times.")
            sys.exit(1)
        time_factor, speed_factor = self.compute_factors(audio_cue, seg_start, seg_end, cue_end)
        filter_complex = self.build_filter_complex(seg_start, seg_end, time_factor, speed_factor)
        print("Constructed filter_complex:")
        print(filter_complex)
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "anullsrc=cl=stereo:r=48000",
            "-i", self.input_file,
            "-filter_complex", filter_complex,
            "-map", "[outv]",
            "-map", "0:a",
            "-shortest",
            "-c:v", "libx265",
            "-c:a", "aac",
            self.output_file
        ]
        run_command(cmd)
        print(f"Synchronized video saved to {self.output_file}")

def sync_video_command(args) -> None:
    try:
        audio_cue = float(args.audio_cue)
        cue_end = float(args.cue_end)
        seg_start = float(args.segment_start)
        seg_end = float(args.segment_end)
    except ValueError:
        print("Numeric values required for audio-cue, cue-end, segment-start, and segment-end.")
        sys.exit(1)
    builder = SyncVideoCommandBuilder(args.input, args.output)
    builder.execute(audio_cue, cue_end, seg_start, seg_end)
