# Paper Songs

Fun scientific papers, sung and drawn. Each paper becomes a song and an
animated short, published as a music video.

**Pipeline:** research paper → lyrics → [Suno](https://suno.com) song →
[Manim](https://www.manim.community/) visuals (with the audio baked in) →
published on GitHub Pages. The site shows only the finished videos — the
tooling stays behind the curtain.

## Project layout

```
index.html                  gallery page
song.html                   per-song page (audio + lyrics + video)
assets/                     site CSS/JS
songs/songs.json            manifest driving the whole site
songs/<song-id>/            one folder per song: song.mp3, video.mp4, lyrics.txt
manim/scenes/               Manim scene code (render output is git-ignored)
.github/workflows/deploy.yml  auto-deploys to GitHub Pages on push to main
```

## Adding a new song

1. **Pick a paper** and write lyrics from it (save as `lyrics.txt`).
2. **Generate the song** in Suno (paste the lyrics in Custom mode) and download
   the MP3 into the song folder as `song.mp3` — the Manim scene bakes it into
   the rendered video automatically.
3. **Make the visual**: add a scene in `manim/scenes/`, render it
   (`manim -pqh scenes/my_scene.py MyScene`), copy the mp4 out of `manim/media/`.
   See [manim/README.md](manim/README.md) for setup and audio-sync tips.
4. **Create the song folder** `songs/<song-id>/` containing `song.mp3`,
   `video.mp4`, `lyrics.txt`.
5. **Add an entry** to `songs/songs.json`:

   ```json
   {
     "id": "song-id",
     "title": "Song Title",
     "hook": "One irresistible sentence about the paper.",
     "paper": { "title": "Paper Title (Authors, Year)", "url": "https://arxiv.org/abs/..." },
     "tags": ["topic"],
     "video": "video.mp4",
     "lyrics": "lyrics.txt",
     "story": "A few short paragraphs telling the paper's story in plain fun language. Separate paragraphs with \\n."
   }
   ```

6. Commit and push — the site redeploys automatically.

> **File size note:** GitHub blocks files over 100 MB and Pages sites are soft-capped
> at 1 GB total. MP3s (~5 MB) and short 1080p MP4s (~20–60 MB) are fine. If videos
> get large, upload them to YouTube and link/embed instead of committing them.

## Local preview

`fetch()` needs a web server (opening index.html directly from disk won't load songs.json):

```powershell
python -m http.server 8000
# then open http://localhost:8000
```

## First-time deployment

1. Create a repo on GitHub, then:

   ```powershell
   git add -A
   git commit -m "Initial site"
   git branch -M main
   git remote add origin https://github.com/<you>/<repo>.git
   git push -u origin main
   ```

2. On GitHub: **Settings → Pages → Source: GitHub Actions**.
3. Push (or re-run the workflow) — the site appears at `https://<you>.github.io/<repo>/`.
