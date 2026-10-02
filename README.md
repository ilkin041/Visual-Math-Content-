# Visual Math Content

## Why is the area of a circle πr²?

`circle_area.py` is a narrated visual proof in the style of 3Blue1Brown, built with
[Manim Community](https://www.manim.community/) and
[manim-voiceover](https://voiceover.manim.community/). The circle is cut into wedges,
the wedges are unrolled into a strip, and as the slices get thinner (8 → 16 → 32 → 64)
the strip becomes a rectangle πr wide and r tall, so its area is πr².

Running time is about 55 seconds, rendered at 1080p and 60 fps.

### Install

System packages (ffmpeg, sox, Cairo/Pango, and LaTeX for the formulas):

```bash
# macOS
brew install ffmpeg sox py3cairo pango pkg-config
brew install --cask mactex-no-gui

# Ubuntu / Debian
sudo apt install ffmpeg sox libsox-fmt-mp3 libcairo2-dev libpango1.0-dev pkg-config \
                 texlive texlive-latex-extra dvisvgm

# Windows (Chocolatey)
choco install ffmpeg sox.portable miktex
```

Python packages (Python 3.10 or newer):

```bash
pip install manim "manim-voiceover[gtts]"
```

### Render

```bash
manim -pqh circle_area.py CircleArea      # 1080p60, final quality
manim -pql circle_area.py CircleArea      # 480p15, quick preview
```

The output is written to `media/videos/circle_area/1080p60/CircleArea.mp4`, with a
`CircleArea.srt` subtitle file beside it. Narration clips are cached in `media/voiceovers/`,
so a re-render only synthesizes lines whose text has changed.

gTTS calls Google Translate's speech endpoint, so the first render needs internet access.

### Changing the voice

The `VOICE` line near the top of `circle_area.py` selects the narrator. You can also
override it from the shell:

| `VOICE`      | Install                                       | Needs                                            |
|--------------|-----------------------------------------------|--------------------------------------------------|
| `gtts`       | `pip install "manim-voiceover[gtts]"`         | nothing (default)                                |
| `elevenlabs` | `pip install "manim-voiceover[elevenlabs]"`   | `ELEVEN_API_KEY`                                 |
| `openai`     | `pip install "manim-voiceover[openai]"`       | `OPENAI_API_KEY`                                 |
| `azure`      | `pip install "manim-voiceover[azure]"`        | `AZURE_SUBSCRIPTION_KEY`, `AZURE_SERVICE_REGION` |
| `recorder`   | `pip install "manim-voiceover[recorder]"`     | a microphone; it prompts you line by line        |

```bash
VOICE=openai manim -pqh circle_area.py CircleArea
```

Animation timing comes from the length of each spoken line, so a different voice
re-times the whole video automatically.

### Adjusting it

The file is split into commented `SCENE 1` to `SCENE 6` blocks. Each narration line is a
`with self.voiceover(text=...)` block, and `split(tracker.duration, ...)` divides that
line's time among its animations. Constants at the top control the radius, colors, pause
length, and how the wedges are shaded (`COLOR_BY_HALF`).

## If every intersection has a third line, all the lines are concurrent

`concurrent_lines.py` is a silent visual proof (no narration, no branding) with all
on-screen text in Azerbaijani, set in CMU Serif (the Unicode version of LaTeX's Computer
Modern) so captions match the formulas. The problem: finitely many pairwise non-parallel lines are
given, and through the intersection of any two of them passes another one of the lines.
Then all the lines pass through one point.

The proof is by contradiction with the smallest-distance argument. Among all pairs
(intersection point P, given line ℓ not through P) take the one with the smallest distance
h = d(P, ℓ). At least three lines pass through P and they cut ℓ at three distinct points, two
of which (A, B) lie on the same side of the foot H of the perpendicular. Then
AB ≤ HB < PB, and comparing two expressions for the area of triangle PAB gives
h' = d(A, PB) = (AB/PB)·h < h, although (A, PB) is also such a pair.

Running time is about 1 minute 45 seconds, rendered at 1080p and 60 fps.

### Install

System packages (Cairo/Pango, ffmpeg, LaTeX for the formulas, and the CMU Serif font,
which has the Azerbaijani letters ə, Ə, ş, ğ, ı, İ):

```bash
# Ubuntu / Debian
sudo apt install ffmpeg libcairo2-dev libpango1.0-dev pkg-config \
                 texlive texlive-latex-extra dvisvgm fonts-cmu

# macOS
brew install ffmpeg py3cairo pango pkg-config
brew install --cask mactex-no-gui font-computer-modern
```

```bash
pip install manim
```

### Render

```bash
manim -pql concurrent_lines.py ConcurrentLines             # 480p15, quick preview
manim -pqh --fps 60 concurrent_lines.py ConcurrentLines    # 1080p60, final quality
```

The output is written to `media/videos/concurrent_lines/1080p60/ConcurrentLines.mp4`.

### Adjusting it

Everything you are likely to change is defined as a constant at the top of the file:
colors, the font (`FONT`), transition times (`T_FAST`, `T_MED`, `T_SLOW`, `PAUSE`), the
canonical points (`H_PT`, `P_PT`, `A_PT`, `B_PT`, `C_PT`), and the line configurations for
scenes 1, 2–3 and 9 (`SCENE1_LINES`, `SCHEMATIC_LINES`). Each scene is a separate
`sceneN_...` method of `ConcurrentLines`. All geometry (intersections, feet of perpendiculars,
distances, h') is computed with numpy from those constants.

Lines are clipped to the area above the caption strip (`STAGE`), so captions at the bottom
never overlap a line. Set the bottom of `STAGE` to `-FRAME_Y` to run the lines to the
bottom edge of the frame instead.
