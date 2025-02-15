### TEST 2: Video Splice Segments

This test demonstrates extracting multiple segments from a 32‑second video file. The goal is to capture key splices that
you can later fine‑tune by adjusting their start and end times until you have the exact frames you want.

**Segments Defined:**

- **Segment 1:** 4s to 7s
- **Segment 2:** 9s to 12s
- **Segment 3:** 14s to 16s
- **Segment 4:** 17s to 18s
- **Segment 5:** 19s to 20s
- **Segment 6:** 20s to 21s
- **Segment 7:** 22s to 27s
- **Segment 8:** 28s to 31s

#### Step 1. Extract Initial Segments

Use the new `split` sub-command to extract all the segments in one go. This command does the following:

- Reads the input video.
- For each `--segment` pair provided, extracts that time interval.
- Saves each segment as an individual file (named `segment_1.mp4`, `segment_2.mp4`, etc.) in the specified output
  directory (here, `spliced_segments/`).

```bash
python ffmpeg_toy.py split videos/your_32s_video.mp4 spliced_segments/ --segment 4 7 --segment 9 12 --segment 14 16 --segment 17 18 --segment 19 20 --segment 20 21 --segment 22 27 --segment 28 31
```

After running this command, check that the directory `spliced_segments/` contains files
like `segment_1.mp4`, `segment_2.mp4`, etc.

#### Step 2. Review and Fine-Tune Segments

Review each segment individually (e.g., using your favorite media player):

```bash
mpv spliced_segments/segment_3.mp4
```

#### Step 3. Adjust a Segment’s Boundaries

```bash
python ffmpeg_toy.py adjust videos/IMG_1854.mp4 segment_2_adjusted.mp4 --orig-start 4 --orig-end 7 --start-offset 1.5
```

```bash
python ffmpeg_toy.py adjust videos/IMG_1854.mp4 segment_3_adjusted.mp4 --orig-start 14 --orig-end 16 --start-offset 0.6
```

```bash
python ffmpeg_toy.py adjust videos/IMG_1854.mp4 segment_4_adjusted.mp4 --orig-start 17 --orig-end 18 --start-offset 0.8 --end-offset 0.8
```

```bash
python ffmpeg_toy.py adjust videos/IMG_1854.mp4 segment_6_adjusted.mp4 --orig-start 20 --orig-end 21 --end-offset 0.9
```

```bash
python ffmpeg_toy.py adjust videos/IMG_1854.mp4 segment_7_adjusted_1.mp4 --orig-start 22 --orig-end 27 --end-offset -4.0
```

```bash
python ffmpeg_toy.py adjust videos/IMG_1854.mp4 segment_7_adjusted_2.mp4 --orig-start 22 --orig-end 27 --start-offset 1.0 --end-offset -3.0
```

```bash
python ffmpeg_toy.py adjust videos/IMG_1854.mp4 segment_7_adjusted_3.mp4 --orig-start 22 --orig-end 27 --start-offset 2.0 --end-offset -2.0
```

```bash
python ffmpeg_toy.py adjust videos/IMG_1854.mp4 segment_7_adjusted_4.mp4 --orig-start 22 --orig-end 27 --start-offset 3.0 --end-offset -1.0
```

```bash
python ffmpeg_toy.py adjust videos/IMG_1854.mp4 segment_7_adjusted_5.mp4 --orig-start 22 --orig-end 27 --start-offset 4.0 --end-offset 0.3
```

```bash
python ffmpeg_toy.py adjust videos/IMG_1854.mp4 segment_8_adjusted.mp4 --orig-start 28 --orig-end 31 --start-offset 1.0 --end-offset 2.0
```

This command:

- Takes the original video (`videos/IMG_1854.mp4`).
- Knows that Segment 3 originally spans 14s to 16s.
- Applies a start offset of -0.45 (adding 0.45 seconds before) and an end offset of +0.45 (adding 0.45 seconds after).
- Outputs the adjusted segment as `segment_3_adjusted.mp4`.

Repeat this process for any segment until you achieve the precise timing you desire.