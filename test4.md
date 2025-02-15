# Test 4: Time-Controlled Blend Effects

## 1. Default Run (No Effect Applied)

Since the defaults produce no change, running the blend effect without any parameter overrides will output a video identical to the input.

```bash
python ffmpeg_toy.py effects output/final_sync_with_audio.mp4 output/test4_blend_no_effect.mp4 --effect 0 15 blend 1
```

**Explanation**  
- **Time Range:** 0–15 seconds  
- **Blend Phase:** 1 (directly output branch B)  
- **Parameters:** No overrides provided, so the default effect chain is used  
- **Result:** No visual changes (i.e., "no effect")

---

## 2. Example 1: Mild Subtle Effect

This example applies a very subtle visual modification. The colors are only slightly shifted, the blur is minimal, and noise is very low.

```bash
python ffmpeg_toy.py effects output/final_sync_with_audio.mp4 output/test4_blend_mild.mp4 --effect 0 15 blend 1 rgbashift_rh=10 rgbashift_rv=10 rgbashift_gh=-10 rgbashift_gv=-10 rgbashift_bh=5 rgbashift_bv=-5 boxblur=3:1 hue=s=0.9 noise=alls=5:allf=t
```

**Explanation**  
- **Color Shift:** Mild shifts (e.g., red channels at 10 instead of 0)  
- **Box Blur:** Light blur (`3:1`)  
- **Hue:** Slightly reduced saturation (`s=0.9`)  
- **Noise:** Minimal (`alls=5:allf=t`)  
- **Vignette:** Off (no vignette parameter specified)  
- **Result:** A gentle effect that subtly modifies the image

---

## 3. Example 2: Strong Dramatic Effect

This example dramatically increases the color shift and blur while reducing hue saturation for a strong, “glitchy” appearance.

```bash
python ffmpeg_toy.py effects output/final_sync_with_audio.mp4 output/test4_blend_strong.mp4 --effect 0 15 blend 1 rgbashift_rh=60 rgbashift_rv=60 rgbashift_gh=-60 rgbashift_gv=-60 rgbashift_bh=30 rgbashift_bv=-30 boxblur=20:1 hue=s=0.5 noise=alls=80:allf=t vignette=vignette
```

**Explanation**  
- **Color Shift:** Intense (e.g., red channels at 60, green channels at –60)  
- **Box Blur:** Heavy (`20:1`)  
- **Hue:** Low saturation (`s=0.5`) for a washed-out look  
- **Noise:** High (`alls=80:allf=t`)  
- **Vignette:** Applied  
- **Result:** A strong, dramatic visual effect with a glitchy, altered appearance

---

## 4. Example 3: Inverted/Unconventional Colors

This test uses reversed values on some channels to create an unconventional, artistic color inversion alongside moderate blur and noise.

```bash
python ffmpeg_toy.py effects output/final_sync_with_audio.mp4 output/test4_blend_inverted.mp4 --effect 0 15 blend 1 rgbashift_rh=-30 rgbashift_rv=-30 rgbashift_gh=30 rgbashift_gv=30 rgbashift_bh=0 rgbashift_bv=0 boxblur=10:1 hue=s=1.2 noise=alls=40:allf=t vignette=
```

**Explanation**  
- **Color Shift:** Inverted values (negative on red channels, positive on green channels)  
- **Box Blur:** Moderate (`10:1`)  
- **Hue:** Increased saturation (`s=1.2`) for a punchier look  
- **Noise:** Moderate (`alls=40:allf=t`)  
- **Vignette:** Off (set to empty)  
- **Result:** An unconventional, artistic effect with reversed color emphasis and noticeable changes in contrast

---

## 5. Example 4: Vibrant, Cartoonish Look

In this example, parameters are tuned to produce a vibrant, almost cartoon-like effect with bright colors and strong contrast.

```bash
python ffmpeg_toy.py effects output/final_sync_with_audio.mp4 output/test4_blend_vibrant.mp4 --effect 0 15 blend 1 rgbashift_rh=30 rgbashift_rv=30 rgbashift_gh=-10 rgbashift_gv=-10 rgbashift_bh=5 rgbashift_bv=-5 boxblur=5:1 hue=s=1.8 noise=alls=20:allf=t vignette=vignette
```

**Explanation**  
- **Color Shift:** Moderate red/green shifts, creating a brighter red component  
- **Box Blur:** Light blur (`5:1`) to slightly smooth details  
- **Hue:** High saturation (`s=1.8`) for bold, vibrant colors  
- **Noise:** Low-to-moderate (`alls=20:allf=t`)  
- **Vignette:** Applied  
- **Result:** A cartoonish style with exaggerated colors and contrast

---

## 6. Example 5: Artistic Grunge Effect

This example produces an artistic “grunge” look with unusual color distortions, moderate blur, and pronounced noise.

```bash
python ffmpeg_toy.py effects output/final_sync_with_audio.mp4 output/test4_blend_grunge.mp4 --effect 0 15 blend 1 rgbashift_rh=50 rgbashift_rv=10 rgbashift_gh=-20 rgbashift_gv=-40 rgbashift_bh=0 rgbashift_bv=0 boxblur=12:1 hue=s=0.7 noise=alls=60:allf=t vignette=vignette
```

**Explanation**  
- **Color Shift:** Uneven shifts (e.g., large shift on red, smaller on blue) for a grunge look  
- **Box Blur:** Moderate-to-heavy (`12:1`)  
- **Hue:** Lower saturation (`s=0.7`) for a subdued palette  
- **Noise:** Pronounced (`alls=60:allf=t`)  
- **Vignette:** Applied  
- **Result:** An artistic, grungy style with distinct color distortions and a textured, noisy appearance

---

## Final Test: Time-Controlled Diminishing Effect

For the final test, we demonstrate a time-controlled blend effect (using blend phase 4) that starts with a strong effect and gradually diminishes. In this example, the effect is applied over the interval 0–15 seconds, with a full effect for t < 5 seconds and fading out to no effect by t > 10 seconds.

```bash
python ffmpeg_toy.py effects output/final_sync_with_audio.mp4 output/test4_blend_dynamic.mp4 --effect 0 15 blend 4 5 10 rgbashift_rh=60 rgbashift_rv=60 rgbashift_gh=-60 rgbashift_gv=-60 rgbashift_bh=30 rgbashift_bv=-30 boxblur=20:1 hue=s=0.5 noise=alls=80:allf=t vignette=vignette
```

**Explanation**  
- **Blend Phase:** 4 (gradual crossfade mode)  
- **Crossfade Parameters:** Full effect until t < 5 s; no effect after t > 10 s  
- **Overrides:** Same parameters as Example 2’s strong effect branch  
- **Result:**  
  - From 0 to 5 seconds, strong visual changes (full effect)  
  - From 5 to 10 seconds, gradual fade-out of the effect  
  - After 10 seconds, no effect remains  

You thus achieve a **dynamic, time-controlled** visual effect that changes over the course of the segment.
