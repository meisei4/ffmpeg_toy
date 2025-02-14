### TEST 3: Synchronization and Insertion of Segment_1

This test demonstrates synchronizing a glitched, time-warped version of the original video with a musical cue, then switching to the first splice (segment_1) whose playback rate is adjusted to finish exactly when the musical cue ends, and finally attaching the audio track.

**Scenario:**  
- **Input Video:** `videos/IMG_1854.mp4`  
- **Audio Track (musical cue):** `audio/Neuron Activator [LPVmIO6Z4r4].mp3`  
  - The musical cue starts at 15 seconds and ends at 16.5 seconds (duration = 1.5 seconds).
- **Segment_1 (splice):** Originally extracted from 4s to 7s (duration = 3 seconds)

**Desired Effect:**  
- For the first 15 seconds, display a glitched version of the original video (from 0 to 4s) slowed down so that 4 seconds of content stretch to 15 seconds.  
- Then, from 15s to 16.5s, play the splice segment (originally 4 to 7 seconds) sped up so that it fits exactly into 1.5 seconds.  
- **Important:** The final output video must be trimmed to span from 0 up to the end of the musical cue (i.e. 16.5 seconds) so that it does not continue for the full length of the song.
- Finally, attach the "Neuron Activator" audio track so that the video is fully synchronized with the musical cue.

#### Step 1. Run the Synchronization Command

This command uses the new `sync` sub-command. It computes:
- **Glitched portion factor:** time_factor_glitch = 15 / 4 = 3.75  
- **Splice speed factor:** splice_speed_factor = (7 - 4) / (16.5 - 15) = 3 / 1.5 = 2.0  
Thus, the splice segment will be played at 2× speed (using setpts=PTS/2).

```bash
 python ffmpeg_toy.py sync videos/IMG_1854.mp4 sync_test_output.mp4 --audio-cue 15 --cue-end 16.5 --segment-start 4 --segment-end 7 --glitch-filter "rgbashift=rh=40:rv=40:gh=-40:gv=-40:bh=20:bv=-20,boxblur=15:1,hue=s=10,noise=alls=50:allf=t,vignette"
```

This produces a video (`sync_test_output.mp4`) that is intended to be 16.5 seconds long.

#### Step 1.5. Add a Silent Audio Stream

If the sync output is silent (or lacks an audio stream), the subsequent mix command may default to using the full duration of the external audio. To ensure the final output remains trimmed to 16.5 seconds, add a silent audio stream to the sync output:

```bash
ffmpeg -y -f lavfi -i anullsrc=cl=stereo:r=48000 -i sync_test_output.mp4 -shortest -c:v copy -c:a aac sync_test_output_silent.mp4
```

This command creates `sync_test_output_silent.mp4` with a silent audio track that matches the 16.5‑second duration of the sync output.

#### Step 2. Attach the Audio Track

Now attach the external "Neuron Activator" audio track using the mix sub‑command. This overlays the external audio onto the video without extending its duration.

```bash
python ffmpeg_toy.py mix sync_test_output_silent.mp4 final_sync_with_audio.mp4 --mix 0 "audio/Neuron Activator [LPVmIO6Z4r4].mp3"
```

#### Expected Outcome

- **Output Video (`final_sync_with_audio.mp4`):**  
  - The video is exactly 16.5 seconds long.  
  - The first 15 seconds show the glitched, slowed version of the video (0 to 4 seconds stretched by a factor of 3.75).  
  - From 15 to 16.5 seconds, the splice segment (originally 4–7 seconds) plays at 2× speed to fit precisely into 1.5 seconds.  
  - The "Neuron Activator" audio track is attached as the sole audio stream, so the final output is fully synchronized and does not extend beyond the first musical cue.