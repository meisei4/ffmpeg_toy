import argparse

from cmd.audio_mixing import mix_audio
from cmd.audio_process import process_audio
from cmd.compression import compress_video
from cmd.filters.filter import apply_filters
from cmd.split_splice import split_video, adjust_segment
from cmd.sync import sync_video


def main() -> None:
    parser = argparse.ArgumentParser(description="Generic Video Editing Tool using FFmpeg")
    # Global argument: by default audio is kept. Use --no-audio to remove audio.
    parser.add_argument("--no-audio", action="store_true",
                        help="Remove audio track from the output (default: keep audio)")

    subparsers = parser.add_subparsers(dest="command", required=True, help="Sub-commands")

    # audioprocess sub-command
    audioprocess_parser = subparsers.add_parser("audioprocess", help="Process an audio file: cut and loop segments")
    audioprocess_parser.add_argument("input", help="Input audio file")
    audioprocess_parser.add_argument("output", help="Output processed audio file")
    audioprocess_parser.add_argument("--cut-duration", type=float, help="Duration (in seconds) to cut from start")
    audioprocess_parser.add_argument("--loop-start", type=float, help="Loop segment start time (in seconds)")
    audioprocess_parser.add_argument("--loop-end", type=float, help="Loop segment end time (in seconds)")
    audioprocess_parser.add_argument("--loop-total", type=float, help="Total duration (in seconds) for looped segment")
    audioprocess_parser.set_defaults(func=process_audio)

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
    compress_parser.set_defaults(func=compress_video)

    # mix sub-command
    mix_parser = subparsers.add_parser("mix", help="Mix external audio tracks into the video")
    mix_parser.add_argument("input", help="Input video file")
    mix_parser.add_argument("output", help="Output video file")
    mix_parser.add_argument("--mix", nargs=2, action="append", metavar=("START", "FILE"),
                            help="Mix item: start time and audio file (can be repeated)")
    mix_parser.set_defaults(func=mix_audio)

    # effects sub-command
    effects_parser = subparsers.add_parser("effects", help="Apply video effects over specified time segments")
    effects_parser.add_argument("input", help="Input video file")
    effects_parser.add_argument("output", help="Output video file")
    effects_parser.add_argument("--effect", nargs="+", action="append",
                                metavar="EFFECT_ITEM",
                                help=("Effect item parameters. For a normal effect: start end filter_chain [speed]. "
                                      "For a blend effect: start end blend phase [crossfade_start crossfade_end]."))
    effects_parser.set_defaults(func=apply_filters)

    # split sub-command
    split_parser = subparsers.add_parser("split", help="Extract video segments into separate files")
    split_parser.add_argument("input", help="Input video file")
    split_parser.add_argument("output", help="Output directory for segments")
    split_parser.add_argument("--segment", nargs=2, action="append", metavar=("START", "END"),
                              help="Segment to extract: start and end times in seconds (can be repeated)")
    split_parser.set_defaults(func=split_video)

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
    adjust_parser.set_defaults(func=adjust_segment)

    # sync sub-command
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
    sync_parser.set_defaults(func=sync_video)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
