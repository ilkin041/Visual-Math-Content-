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

## Ekstremal prinsip: Silvester–Qallai teoremi, onun dualı və nəticələri

`ekstremal_prinsip.py` is a long, silent seminar video in Azerbaijani (3Blue1Brown style,
Manim Community). It follows the lecture notes section by section: the warm-up problems
on the extremal principle, Kelly's proof of the Sylvester–Gallai theorem, the same proof
for the dual problem (20.14), de Bruijn–Erdős, where the method fails (ℤ², the 9-point
finite plane, Hesse), the summary, and the four homework solutions (dual de Bruijn–Erdős,
necessity of the conditions, the 3D version, circles via inversion).

Every part is its own scene, rendered to its own mp4 so a single part can be opened
during the seminar:

| Scene               | Section                                   |
|---------------------|-------------------------------------------|
| `Hisse00_Giris`     | 1. Giriş: məsələ və şərtlərin rolu        |
| `Hisse01_Isinme`    | 2. İsinmə: ekstremal prinsip              |
| `Hisse02_Silvester` | 3. Silvester–Qallai teoremi               |
| `Hisse03_Dual`      | 4. Dual məsələ: 20.14                     |
| `Hisse04_Neticeler` | 5. Nəticələr (de Breyn–Erdöş)             |
| `Hisse05_Serhedler` | 6. Üsul harada işləmir?                   |
| `Hisse06_Yekun`     | 7. Yekun                                  |
| `Hisse07_Hell1`     | 8.1. Dual de Breyn–Erdöş                  |
| `Hisse08_Hell2`     | 8.2. Şərtlərin zəruriliyi                 |
| `Hisse09_Hell3`     | 8.3. Fəzada Silvester–Qallai (3D)         |
| `Hisse10_Hell4`     | 8.4. Çevrələr və inversiya                |

### Install

All text is set with XeLaTeX in CMU Serif (Computer Modern Unicode), so Azerbaijani
letters (Ə ə İ ı Ş ş Ğ ğ …) render in the classic LaTeX look.

```bash
# Ubuntu / Debian
sudo apt install ffmpeg libcairo2-dev libpango1.0-dev pkg-config dvisvgm \
                 texlive-xetex texlive-latex-extra texlive-science fonts-cmu
pip install manim
```

### Render

```bash
./render_preview.sh                    # every part at 480p15 (quick check)
./render_preview.sh Hisse02_Silvester  # one part
JOBS=4 ./render_all.sh                 # every part at 1080p60, then tam_video.mp4
```

Parts land in `media/videos/ekstremal_prinsip/1080p60/`; `render_all.sh` joins them with
`ffmpeg -f concat` into `tam_video.mp4` and prints each part's length.

### Adjusting it

All constants sit at the top of the file: colors, font sizes, the timing constants
(`T_ANIM = 1.8`, `T_SLOW = 3.0`, `WAIT_STEP = 2.0`, `WAIT_SECTION = 3.0`), the reading-time
rule in `read_wait()` (1.5 s + 0.35 s per word), the canonical diagram (`CANON`, `K_SCALE`,
`K_SHIFT`) and the fixed point/line configurations. All geometry (intersections, feet of
perpendiculars, distances, inversion images) is computed with numpy from those base points.
Kelly's proof is written once (`KellyProof`) and runs in `"points"` mode for part 3 and
`"lines"` mode for part 4, so the two proofs really are step-for-step identical.
