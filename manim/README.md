# Manim visuals

Scenes for the song videos, using [Manim Community Edition](https://www.manim.community/)
(the maintained fork of 3Blue1Brown's manim — better docs and easier install than
[3b1b/manim](https://github.com/3b1b/manim), and what you want for your own projects).

## Setup (once)

Manim lives in the project's own virtual environment (`.venv/` at the repo root)
so it doesn't interfere with the base Anaconda install:

```powershell
python -m venv .venv          # from the repo root (already done)
.venv\Scripts\pip install manim
```

Then either activate it (`.venv\Scripts\Activate.ps1`) or call the exe directly:
`..\.venv\Scripts\manim.exe` from this directory.

You also need FFmpeg (bundled with recent manim wheels) and, for `MathTex`/LaTeX
formulas, a LaTeX distribution such as [MiKTeX](https://miktex.org/download).
If you skip LaTeX, use `Text(...)` instead of `MathTex(...)`.

## Rendering

From this `manim/` directory:

```powershell
# quick low-quality preview (fast iteration)
..\.venv\Scripts\manim.exe -pql scenes/one_water_two_souls.py OneWaterTwoSouls

# final render, 1080p60
..\.venv\Scripts\manim.exe -pqh scenes/one_water_two_souls.py OneWaterTwoSouls
```

Output goes to `manim/media/videos/...` (git-ignored). Copy the final mp4 into the
song's folder, e.g. `songs/example-attention/video.mp4`.

## Syncing to the song

1. Listen to the Suno track and write down timestamps for each section
   (intro / verse / chorus / bridge).
2. Structure your scene so each visual block matches a section, padding with
   `self.wait(seconds)` to hit the timestamps.
3. To combine the rendered video with the song audio into one file:

```powershell
ffmpeg -i video_silent.mp4 -i song.mp3 -c:v copy -c:a aac -shortest video.mp4
```

(Alternatively keep them separate — the site plays the mp4 and mp3 in separate
players. Muxing them into one video makes sharing easier.)
