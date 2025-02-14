## TESTS

yt-dlp -f bestaudio --extract-audio --audio-format mp3 --cookies cookies.txt <URL>

### TEST 1: Obsession Kit

 **Note on Defaults:**  
 For the compress sub-command, if you omit optional parameters, the tool applies these defaults:  
 - **Target Size:** 10 MB  
 - **Resolution:** "lowest" (i.e. 640px width, preserving aspect ratio)  
 - **Denoise:** "med"  
 - **Preset:** "slower" (for x265 encoding)  
 - **Mute:** False (audio is preserved by default)  
 - **Preview Duration:** 0 (processes the full video)  
 - **Speed Factor:** None (no speed change)  

#### Step 1. Process the Audio

Run the following command to process the audio. This command does the following:
- **Cut Duration:** Takes the first **7 seconds** of the input audio.
- **Loop Segment:** Extracts the segment from **5 to 7 seconds**.
- **Loop Total:** Repeats that 2‑second segment to build an additional **10 seconds** of audio.
- Finally, it concatenates the initial 7‑second segment with the 10‑second looped segment, producing a 17‑second output.

```bash
python ffmpeg_toy.py audioprocess audio/"An Obsession With Kit [y9u2oOnLYek].mp3" processed_audio.mp3 --cut-duration 7 --loop-start 5 --loop-end 7 --loop-total 10
```

Listen to the new audio, tune the durations and looping if needed:
```bash
mpv processed_audio.mp3
```

#### Step 2. Replace Video Audio with Processed Audio

The following command overlays the processed audio onto the video file and removes the original audio track:
- The `--mix` option takes a pair: the start time (in seconds) at which the external audio should begin (here, **0** seconds), and the path to the external audio file.
- In this process, the original video's audio is replaced with the new processed audio.

```bash
python ffmpeg_toy.py mix videos/IMG_1854.mp4 final_output.mp4 --mix 0 processed_audio.mp3
```

*By default, if no `--mix` parameter is provided, the mix sub-command will simply copy the original video (i.e. no audio replacement is performed).*

#### Step 3. Compress the Final Video

Finally, compress the video (now with the new processed audio) to ensure the output file is under **10 MB**. This command uses the following parameters:
- **--size 10:** Targets a 10 MB file size.
- **--resolution lowest:** Applies a scaling filter to reduce resolution (i.e. width=640px, height is auto-adjusted to preserve aspect ratio).

```bash
python ffmpeg_toy.py compress final_output.mp4 final_output_compressed.mp4 --size 10 --resolution lowest
```