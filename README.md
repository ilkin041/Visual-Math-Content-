# Visual Math Content

## Qauss inteqralı: ∫ e^(−x²) dx = √π

`gaussian_integral.py` is a silent visual proof in the style of 3Blue1Brown, built with
[Manim Community](https://www.manim.community/). All on-screen text is in Azerbaijani.

The video starts from the 2D bell curve, squares the integral, and lifts it into 3D as the
volume under `z = e^(−(x²+y²))`. Cross-sections show that this volume is `I · I`. Seen from
above, the surface is circularly symmetric, so the volume is split into cylindrical shells.
One shell is pulled out and unrolled into a flat `2πr × e^(−r²) × dr` plate. Adding up the
shells gives `I² = π`, so `I = √π`. At the end, the blue area under the curve pours into a
`1 × √π` rectangle and fills it exactly.

Running time is about 1 min 40 s, rendered at 1080p and 60 fps.

### Install

```bash
# Ubuntu / Debian
sudo apt install ffmpeg libcairo2-dev libpango1.0-dev pkg-config \
                 texlive texlive-latex-extra dvisvgm fonts-noto-core
# macOS
brew install ffmpeg py3cairo pango pkg-config && brew install --cask mactex-no-gui

pip install manim
```

Captions use the **Noto Sans** font, which covers ə, ş, ğ, ı, ö, ü and ç. To use a different
font such as Inter, change `FONT` at the top of the file.

### Render

```bash
manim -pql gaussian_integral.py GaussianIntegral   # 480p15, quick preview
manim -pqh gaussian_integral.py GaussianIntegral   # 1080p60, final quality
```

The output is written to `media/videos/gaussian_integral/1080p60/GaussianIntegral.mp4`.

### Adjusting it

* The file has one method per scene, `scene_1_bell_curve` to `scene_9_final`. Each method's
  header gives its target length and the camera it uses.
* Camera angles are the `FRONT`, `VIEW3D` and `TOP` presets near the top of the file.
* `PACE` scales every animation and pause at once.
* `make_shell(r, dr, ...)` builds a cylindrical shell. `unroll_shell(...)` is the animation
  that flattens it into a plate. `morph_shell(...)` animates any of the shell's parameters,
  such as its height, its position or how far it is unrolled.

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
