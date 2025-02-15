import argparse

from cmd.audio_mixing import MixAudioCommandBuilder, mix_audio_command
from cmd.audio_process import ProcessAudioCommandBuilder, process_audio_command
from cmd.compression import CompressVideoCommandBuilder, compress_video_command
from cmd.split_splice import SplitVideoCommandBuilder, AdjustSegmentCommandBuilder, split_video_command, adjust_segment_command
from cmd.sync import SyncVideoCommandBuilder, sync_video_command
from cmd.filters.video_effects_builder import VideoEffectsCommandBuilder, video_effects_command

class CLICommandBuilder:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="Generic Video Editing Tool using FFmpeg"
        )
        self.subparsers = self.parser.add_subparsers(
            dest="command", required=True, help="Sub-commands"
        )

    def add_audio_process(self):
        sub = self.subparsers.add_parser(
            "audioprocess", help="Process an audio file: cut and loop segments"
        )
        sub.add_argument("input", help="Input audio file")
        sub.add_argument("output", help="Output processed audio file")
        sub.add_argument("--cut-duration", type=float, help="Duration (in seconds) to cut from start")
        sub.add_argument("--loop-start", type=float, help="Loop segment start time (in seconds)")
        sub.add_argument("--loop-end", type=float, help="Loop segment end time (in seconds)")
        sub.add_argument("--loop-total", type=float, help="Total duration (in seconds) for looped segment")
        sub.set_defaults(func=process_audio_command)
        return self

    def add_compress(self):
        sub = self.subparsers.add_parser("compress", help="Compress video to a target size")
        sub.add_argument("input", help="Input video file")
        sub.add_argument("output", help="Output video file")
        sub.add_argument("--size", type=int, help="Target file size in MB")
        sub.add_argument("--resolution", help="Scale resolution (e.g. '640:-2')")
        sub.add_argument("--denoise", help="Denoise strength (off, low, med, high)")
        sub.add_argument("--preset", help="x265 preset")
        sub.add_argument("--mute", action="store_true", help="Strip audio track")
        sub.add_argument("--preview", type=int, help="Encode only first N seconds for testing")
        sub.add_argument("--speed", type=float, help="Playback speed factor")
        sub.set_defaults(func=compress_video_command)
        return self

    def add_mix(self):
        sub = self.subparsers.add_parser("mix", help="Mix external audio tracks into the video")
        sub.add_argument("input", help="Input video file")
        sub.add_argument("output", help="Output video file")
        sub.add_argument("--mix", nargs=2, action="append", metavar=("START", "FILE"),
                         help="Mix item: start time and audio file (can be repeated)")
        sub.set_defaults(func=mix_audio_command)
        return self

    def add_effects(self):
        sub = self.subparsers.add_parser("effects", help="Apply video effects over specified time segments")
        sub.add_argument("input", help="Input video file")
        sub.add_argument("output", help="Output video file")
        sub.add_argument("--effect", nargs="+", action="append",
                         metavar="EFFECT_ITEM",
                         help=("Effect item parameters. For a normal effect: start end filter_chain [speed]. "
                               "For a blend effect: start end blend phase [crossfade_start crossfade_end]."))
        sub.set_defaults(func=video_effects_command)
        return self

    def add_split(self):
        sub = self.subparsers.add_parser("split", help="Extract video segments into separate files")
        sub.add_argument("input", help="Input video file")
        sub.add_argument("output", help="Output directory for segments")
        sub.add_argument("--segment", nargs=2, action="append", metavar=("START", "END"),
                         help="Segment to extract: start and end times in seconds (can be repeated)")
        sub.set_defaults(func=split_video_command)
        return self

    def add_adjust(self):
        sub = self.subparsers.add_parser("adjust", help="Adjust a segment using the original video as source")
        sub.add_argument("orig", help="Original video file")
        sub.add_argument("output", help="Output adjusted segment file")
        sub.add_argument("--orig-start", required=True, help="Original start time of the segment in seconds")
        sub.add_argument("--orig-end", required=True, help="Original end time of the segment in seconds")
        sub.add_argument("--start-offset", type=float,
                         help="Offset to add to the original start time (negative to add before)")
        sub.add_argument("--end-offset", type=float,
                         help="Offset to add to the original end time (positive to add after)")
        sub.set_defaults(func=adjust_segment_command)
        return self

    def add_sync(self):
        sub = self.subparsers.add_parser("sync", help="Synchronize glitched video with a musical cue and splice in a segment")
        sub.add_argument("input", help="Input video file")
        sub.add_argument("output", help="Output video file")
        sub.add_argument("--audio-cue", required=True,
                         help="Time (in seconds) in the audio when the splice should start")
        sub.add_argument("--cue-end", required=True,
                         help="Time (in seconds) in the audio when the splice should end")
        sub.add_argument("--segment-start", required=True,
                         help="Original start time of the splice segment (in seconds)")
        sub.add_argument("--segment-end", required=True,
                         help="Original end time of the splice segment (in seconds)")
        sub.add_argument("--glitch-filter",
                         help="Custom filter chain for the glitched portion (default: 'rgbashift=rh=10:rv=10,boxblur=2:1')")
        sub.set_defaults(func=sync_video_command)
        return self

    def build(self) -> argparse.ArgumentParser:
        return self.parser
