python ffmpeg_toy.py effects \
output/final_sync_with_audio.mp4 \
output_shift_trippy_new.mp4 \
--effect 0 15 blend 1 \
rgbashift_rh=60 \
rgbashift_rv=10 \
rgbashift_gh=-40 \
rgbashift_gv=-20 \
rgbashift_bh=80 \
rgbashift_bv=0 \
rgbashift_edge=wrap \
colorchannelmixer=rr=1.0:rg=0.0:rb=0.1:gr=0.0:gg=0.1:gb=0.1:br=0.1:bg=0.0:bb=1.0 \
hue=s=1.5:H=40 \
colorbalance=rs=0.4:gs=0.0:bs=-0.2 \
hue=s=5.0 \
eq=brightness=0.01:contrast=1.2

python ffmpeg_toy.py effects output/final_sync_with_audio.mp4 output_step1.mp4 \
--effect 0 15 blend 1 \
rgbashift_rh=60 rgbashift_rv=10 \
rgbashift_gh=-40 rgbashift_gv=-20 \
rgbashift_bh=80 rgbashift_bv=0 \
rgbashift_edge=wrap \
hue=s=2.0

python ffmpeg_toy.py effects output/final_sync_with_audio.mp4 output_step2.mp4 \
--effect 0 15 blend 1 \
scroll=h=0.005 \
rgbashift_rh=60 rgbashift_rv=10 \
rgbashift_gh=-40 rgbashift_gv=-20 \
rgbashift_bh=80 rgbashift_bv=0 \
rgbashift_edge=wrap \   
hue=s=2.0 \
colorchannelmixer=rr=1.0:rg=0.0:rb=0.1:gr=0.0:gg=0.2:gb=0.0:br=0.1:bg=0.0:bb=1.0

python ffmpeg_toy.py effects output/final_sync_with_audio.mp4 output_glowish.mp4 \
--effect 0 15 blend 1 \
colorbalance=rs=0.4:gs=0.0:bs=-0.2 \
hue=s=5.0 \
eq=brightness=0.80:contrast=1.2


# 2. Example Workflow to Generate Mild, Normal, and Intense Variations

Below is an illustrative “batch test” approach for each major parameter. We’ll assume:
- **Input Video:** `output/final_sync_with_audio.mp4`
- **Output Video Names:** `output/test4_X_mild.mp4`, `output/test4_X_normal.mp4`, `output/test4_X_intense.mp4`
- **Time Range:** `--effect 0 15 blend 1` (apply effect from 0–15 seconds, simple “Phase 1” blend)

You can adapt these commands as needed by mixing and matching parameters or by changing the time range and blend phase.

## 2.1 Testing Color Shift (rgbashift)

Create three variants to see how mild vs. strong shifts look:

```bash
python ffmpeg_toy.py effects \
  output/final_sync_with_audio.mp4 output/test4_shift_mild.mp4 \
  --effect 0 15 blend 1 \
  rgbashift_rh=10 rgbashift_rv=10 \
  rgbashift_gh=-10 rgbashift_gv=-10 \
  rgbashift_bh=5  rgbashift_bv=-5

python ffmpeg_toy.py effects \
  output/final_sync_with_audio.mp4 output/test4_shift_normal.mp4 \
  --effect 0 15 blend 1 \
  rgbashift_rh=30 rgbashift_rv=30 \
  rgbashift_gh=-30 rgbashift_gv=-30 \
  rgbashift_bh=15 rgbashift_bv=-15

python ffmpeg_toy.py effects \
  output/final_sync_with_audio.mp4 output/test4_shift_intense.mp4 \
  --effect 0 15 blend 1 \
  rgbashift_rh=60 rgbashift_rv=60 \
  rgbashift_gh=-60 rgbashift_gv=-60 \
  rgbashift_bh=30 rgbashift_bv=-30
```

Observe how each output looks increasingly “glitched” or “torn” in color.

## 2.2 Testing Box Blur (boxblur)

Again, you can keep the color shift at zero for clarity, or combine it with color shift if you like. Let’s isolate box blur alone:

```bash
# -- Mild Blur
python ffmpeg_toy.py effects \
  output/final_sync_with_audio.mp4 output/test4_blur_mild.mp4 \
  --effect 0 15 blend 1 \
  boxblur=3:1

# -- Normal Blur
python ffmpeg_toy.py effects \
  output/final_sync_with_audio.mp4 output/test4_blur_normal.mp4 \
  --effect 0 15 blend 1 \
  boxblur=10:1

# -- Intense Blur
python ffmpeg_toy.py effects \
  output/final_sync_with_audio.mp4 output/test4_blur_intense.mp4 \
  --effect 0 15 blend 1 \
  boxblur=20:1
```

Compare how detail disappears as the radius and/or power increase.

## 2.3 Testing Hue (Saturation)

We’ll focus on saturation only (`s=`). Feel free to experiment with hue rotation or brightness as well.

```bash
# -- Mild Saturation
python ffmpeg_toy.py effects \
  output/final_sync_with_audio.mp4 output/test4_hue_mild.mp4 \
  --effect 0 15 blend 1 \
  hue=s=0.9

# -- Normal Saturation
python ffmpeg_toy.py effects \
  output/final_sync_with_audio.mp4 output/test4_hue_normal.mp4 \
  --effect 0 15 blend 1 \
  hue=s=1.5

# -- Intense Saturation
python ffmpeg_toy.py effects \
  output/final_sync_with_audio.mp4 output/test4_hue_intense.mp4 \
  --effect 0 15 blend 1 \
  hue=s=2.0
```

Low values (<1) yield muted colors; high values (>1) yield very vivid colors.

## 2.4 Testing Noise

Noise is controlled primarily by `alls=XX`. The higher, the more pronounced the grain or static.

```bash
# -- Mild Noise
python ffmpeg_toy.py effects \
  output/final_sync_with_audio.mp4 output/test4_noise_mild.mp4 \
  --effect 0 15 blend 1 \
  noise=alls=5:allf=t

# -- Normal Noise
python ffmpeg_toy.py effects \
  output/final_sync_with_audio.mp4 output/test4_noise_normal.mp4 \
  --effect 0 15 blend 1 \
  noise=alls=20:allf=t

# -- Intense Noise
python ffmpeg_toy.py effects \
  output/final_sync_with_audio.mp4 output/test4_noise_intense.mp4 \
  --effect 0 15 blend 1 \
  noise=alls=80:allf=t
```

At higher levels, your image can look like vintage film or full “TV static.”

## 2.5 Testing Vignette

By default, `vignette=vignette` applies a standard corner darkening. You can tweak geometry parameters if you want stronger or subtler results.

```bash
# -- No Vignette
python ffmpeg_toy.py effects \
  output/final_sync_with_audio.mp4 output/test4_vignette_off.mp4 \
  --effect 0 15 blend 1

# -- Mild Vignette
python ffmpeg_toy.py effects \
  output/final_sync_with_audio.mp4 output/test4_vignette_mild.mp4 \
  --effect 0 15 blend 1 \
  vignette=vignette \
  # If you want a subtler effect, you might do:
  # vignette='PI/6'

# -- Intense Vignette
python ffmpeg_toy.py effects \
  output/final_sync_with_audio.mp4 output/test4_vignette_intense.mp4 \
  --effect 0 15 blend 1 \
  vignette='PI/2'
```

