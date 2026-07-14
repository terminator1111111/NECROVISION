# NECROVISION // Deep-Frame Resurrection Engine

A Python desktop application for cinematic sci-fi/horror image enhancement — somewhere between a VFX pipeline and a haunted machine. NECROVISION ingests still frames (including sealed HEIF/HEIC containers), resurrects them at 4× scale, and routes them through a rack of seven experimental enhancement modules to give ordinary footage the color science and texture of modern horror and sci-fi cinema.


*Before: an ordinary storefront photo.*


*After: the same frame with Necro Grade engaged — crushed luminance, sickly green-teal shadows, cold highlights.*

---

## Features

- **4× Resurrection Upscaling** — cubic-reconstruction upscaler (CUDA-aware; falls back to CPU).
- **Seven stackable enhancement modules**, each with an enable switch and a 0.00–1.00 intensity dial ("dread level").
- **Live preview** — debounced, low-resolution preview re-renders as you move the sliders, so the feed stays responsive even on large frames.
- **Thread-safe GUI** — all heavy processing runs on worker threads; every UI update is marshaled back to the main thread (`root.after`), which keeps Tkinter stable on macOS.
- **HEIF/HEIC containment unit** — opens Apple-format images directly (Pillow 10+).
- **Apple dark-mode design language** — custom pill buttons, cards, and progress styling on a true-black viewing chamber.
- **Seal & Archive** — saves to PNG/JPEG/HEIF and reveals the result in Finder/Explorer.

## The Anomaly Module Rack

| # | Module | What it does |
|---|--------|--------------|
| 1 | 🩸 **Necro Grade** | Horror color science in LAB space: crushed contrast, sickly green-teal shadows, cold sterile highlights. |
| 2 | 🕳 **Event Horizon HDR** | Filmic (Uncharted 2-style) tone curve pushed past its safety rating — screaming highlights, devouring shadows. |
| 3 | 📡 **Signal Exorcism** | Edge-aware bilateral denoise that purges grain while preserving subject edges, blended with the original. |
| 4 | 🧬 **Xeno-Detail** | Multi-scale forensic sharpening that separates and re-amplifies detail strata (pores, fibers, textures). |
| 5 | 👁 **Retinal Reconstruction** | Canny edge-guided selective sharpening — rebuilds contours the way an eye resolves a shape in a dark hallway. |
| 6 | ☢ **Bioluminescence** | Content-aware vibrance with skin-tone protection; non-human colors glow as if lit from within. |
| 7 | 🌫 **Spectral Drift** | Multi-pass edge-preserving smoothing (domain-transform filter, bilateral fallback) — dreamlike, too calm. |

Modules fire in a fixed order (Exorcism → Necro → Horizon → Xeno → Retinal → Biolume → Drift): the signal is always exorcised before it is graded.

## Installation

```bash
git clone https://github.com/terminator1111111/NECROVISION.git
cd NECROVISION

# Python 3.9+
pip install opencv-python opencv-contrib-python numpy pillow torch

# optional but recommended: opencv-contrib enables the domain-transform
# filter used by Spectral Drift (otherwise it falls back to bilateral)
```

Tkinter ships with the standard Python installer on macOS/Windows; on Linux install `python3-tk`.

## Usage

```bash
python necrovision_enhancer.py
```

1. **Acquire Specimen** — load a JPG/PNG/HEIF/HEIC/BMP/WebP frame.
2. **Resurrect 4×** (optional) — upscale before processing.
3. **Arm modules** in the Anomaly Module Rack and set each dread level; the viewing chamber previews live.
4. **Engage All Modules** — full-resolution render with per-module progress.
5. **Seal & Archive** — export the processed frame.

## Use Cases

- **Pre-vis and look development** — rough in a horror/sci-fi grade on location stills before committing to a full color pipeline.
- **Concept and pitch decks** — turn ordinary reference photos into mood frames that sell a tone (see the before/after above).
- **Poster and thumbnail treatment** — single-frame grading for key art, YouTube thumbnails, or festival one-sheets.
- **Restoring low-resolution source material** — 4× upscale plus Signal Exorcism and Xeno-Detail to make archival or phone footage frames presentable.
- **Photography** — a fast stylized-grade tool for anyone who wants the "abandoned laboratory" look without opening a full editor.

## Theme Configuration

Every theme is just a combination of armed modules and dread levels. Suggested recipes:

### 🧪 Abandoned Laboratory (classic horror grade)
The default look — the palette of every derelict facility in modern cinema.

| Module | Enabled | Dread level |
|---|---|---|
| Signal Exorcism | ✅ | 0.40 |
| Necro Grade | ✅ | 0.70 |
| Xeno-Detail | ✅ | 0.50 |
| all others | ❌ | — |

### 🚀 Derelict Starship (sci-fi cold void)
Deep contrast and cold highlights; edges resolved hard.

| Module | Enabled | Dread level |
|---|---|---|
| Necro Grade | ✅ | 0.50 |
| Event Horizon HDR | ✅ | 0.65 |
| Retinal Reconstruction | ✅ | 0.60 |
| all others | ❌ | — |

### ☣️ Alien Biome (otherworldly glow)
Saturated, unnatural color with humans kept just human enough.

| Module | Enabled | Dread level |
|---|---|---|
| Signal Exorcism | ✅ | 0.30 |
| Bioluminescence | ✅ | 0.80 |
| Necro Grade | ✅ | 0.35 |
| all others | ❌ | — |

### 🌫 Fever Dream (unwakeable)
Too smooth, too calm.

| Module | Enabled | Dread level |
|---|---|---|
| Spectral Drift | ✅ | 0.75 |
| Necro Grade | ✅ | 0.40 |
| Event Horizon HDR | ✅ | 0.30 |
| all others | ❌ | — |

### 🔍 Forensic Restoration (neutral cleanup, no grade)
Rescue detail from a dead frame without stylizing it.

| Module | Enabled | Dread level |
|---|---|---|
| Signal Exorcism | ✅ | 0.55 |
| Xeno-Detail | ✅ | 0.65 |
| Retinal Reconstruction | ✅ | 0.45 |
| all others | ❌ | — |

### Changing the startup defaults

Default arm states and dread levels live in `NecrovisionDeck.__init__` in `necrovision_enhancer.py`:

```python
self.effect_intensities = {
    'necro':   DoubleVar(value=0.5),   # startup dread level per module
    ...
}
self.enabled_effects = {
    'necro':   tk.BooleanVar(value=True),   # armed at startup
    'horizon': tk.BooleanVar(value=False),  # disarmed at startup
    ...
}
```

Set `value=` on any module to bake your preferred theme in as the startup state. Module keys: `necro`, `horizon`, `exorcism`, `xeno`, `retinal`, `biolume`, `drift`. The 4× scale factor can be changed where the upscaler is constructed: `ResurrectionUpscaler(scale_factor=4)`.

## Tech Stack

Python · OpenCV (+contrib) · NumPy · PyTorch · Pillow · Tkinter/ttk · threading

---

*FOR INTERNAL USE ONLY — BLACKLIGHT PICTURES, POST-PRODUCTION DIVISION.*
*Studio legend says the original colorist never logged out.*
