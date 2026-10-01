"""
Why is the area of a circle πr²?
================================
A 3Blue1Brown-style visual proof with voiceover narration: cut a circle into
wedges, unroll them into a strip, and watch the strip become a πr × r
rectangle as the slices get thinner.

INSTALL
-------
    # 1) System packages
    #    macOS:          brew install ffmpeg sox py3cairo pango pkg-config
    #                    brew install --cask mactex-no-gui        # LaTeX for MathTex
    #    Ubuntu/Debian:  sudo apt install ffmpeg sox libsox-fmt-mp3 \
    #                        libcairo2-dev libpango1.0-dev pkg-config \
    #                        texlive texlive-latex-extra dvisvgm
    #    Windows:        choco install ffmpeg sox.portable miktex
    #
    # 2) Python packages (Python 3.10+)
    pip install manim "manim-voiceover[gtts]"

RENDER  (1080p, 60 fps)
-----------------------
    manim -pqh circle_area.py CircleArea

    # fast low-res preview while tweaking timing:
    manim -pql circle_area.py CircleArea

The video lands in media/videos/circle_area/1080p60/CircleArea.mp4 together
with a CircleArea.srt subtitle file. Narration clips are cached in
media/voiceovers/, so re-renders only re-synthesize lines whose text changed.

CHANGING THE VOICE
------------------
Edit the one VOICE line below, or override it from the shell without touching
the file:  VOICE=openai manim -pqh circle_area.py CircleArea
"""

from __future__ import annotations

import os

import numpy as np
from manim import *
from manim_voiceover import VoiceoverScene

# ═════════════════════════════════════════════════════════════════════════════
#  VOICE — change this ONE line to swap the narrator
#    "gtts"        free Google voice, no API key           (manim-voiceover[gtts])
#    "elevenlabs"  most natural; needs ELEVEN_API_KEY      (manim-voiceover[elevenlabs])
#    "openai"      needs OPENAI_API_KEY                    (manim-voiceover[openai])
#    "azure"       needs AZURE_SUBSCRIPTION_KEY and
#                  AZURE_SERVICE_REGION                    (manim-voiceover[azure])
#    "recorder"    record your own voice, line by line     (manim-voiceover[recorder])
# ═════════════════════════════════════════════════════════════════════════════
VOICE = os.environ.get("VOICE", "gtts")


def make_speech_service():
    """Build the speech service named by VOICE (imports are lazy, so only the
    extra you actually use needs to be installed)."""
    if VOICE == "gtts":
        from manim_voiceover.services.gtts import GTTSService
        return GTTSService(lang="en", tld="com")
    if VOICE == "elevenlabs":
        from manim_voiceover.services.elevenlabs import ElevenLabsService
        return ElevenLabsService(voice_name="Adam", model="eleven_multilingual_v2",
                                 transcription_model=None)
    if VOICE == "openai":
        from manim_voiceover.services.openai import OpenAIService
        return OpenAIService(voice="onyx", model="tts-1-hd", transcription_model=None)
    if VOICE == "azure":
        from manim_voiceover.services.azure import AzureService
        return AzureService(voice="en-US-GuyNeural")
    if VOICE == "recorder":
        from manim_voiceover.services.recorder import RecorderService
        return RecorderService(transcription_model=None)
    raise ValueError(f"Unknown VOICE {VOICE!r}")


# ═════════════════════════════════════════════════════════════════════════════
#  LOOK & FEEL
# ═════════════════════════════════════════════════════════════════════════════
config.background_color = BLACK

R = 2.2                     # circle radius in scene units
RADIUS_COLOR = YELLOW       # anything that is a radius
EDGE_COLOR = BLUE           # anything that is circumference
TEAL_LIGHT = TEAL_C
TEAL_DARK = interpolate_color(TEAL_E, BLACK, 0.45)

# True : top half of the circle is one shade, bottom half the other, so the
#        final strip alternates light/dark wedge by wedge (easiest to follow
#        the interleaving).
# False: neighbouring wedges alternate around the circle (classic pizza look),
#        but in the strip the shades then come in pairs.
COLOR_BY_HALF = True

PAUSE = 0.4                 # silent beat after key moments
ROW_GAP = 0.5               # vertical gap between the two unrolled rows (Scene 3)
EXPLODE = 0.12              # how far wedges drift apart after the cut (Scene 2)
DIM = 0.4                   # opacity of the wedges that step back in Scene 5


# ═════════════════════════════════════════════════════════════════════════════
#  SMALL HELPERS
# ═════════════════════════════════════════════════════════════════════════════
def split(total, *weights):
    """Split `total` seconds proportionally to `weights`, so several animations
    inside one voiceover line finish exactly together with the speech."""
    s = sum(weights)
    return [total * w / s for w in weights]


def span(tracker, floor=0.0):
    """Time available for a voiceover line. One-word lines ("More.") are shorter
    than the motion needs to stay readable, so they get a floor; the voice
    simply finishes while the motion completes."""
    return max(tracker.duration, floor)


def unit(angle):
    return np.array([np.cos(angle), np.sin(angle), 0.0])


def wrap(angle):
    """Wrap an angle into [-π, π) so wedges always take the short way round."""
    return (angle + PI) % TAU - PI


def lagged(anims, spread=0.3):
    """LaggedStart whose total stagger is `spread` of the run time, whatever
    the number of animations (4 wedges or 32 wedges feel the same)."""
    n = len(anims)
    lag = 0.0 if n < 2 else spread / ((1 - spread) * (n - 1))
    return LaggedStart(*anims, lag_ratio=lag)


def glow(mob, color, layers=((8, 0.30), (16, 0.14), (28, 0.06))):
    """Soft halo: a few wider, fainter copies of `mob`'s outline."""
    return VGroup(*[
        mob.copy().set_fill(opacity=0).set_stroke(color, width=w, opacity=o)
        for w, o in layers
    ])


# ═════════════════════════════════════════════════════════════════════════════
#  WEDGES + THE REARRANGEMENT (works for any even number of slices n)
# ═════════════════════════════════════════════════════════════════════════════
class RigidMove(Animation):
    """Carry a wedge as a rigid body: it turns about its tip while the tip
    travels, so it never stretches or shrinks on the way (a plain Transform
    would squash it mid-rotation)."""

    def __init__(self, wedge, pivot, heading, **kwargs):
        self.pivot0 = np.array(wedge.pivot, dtype=float)
        self.pivot1 = np.array(pivot, dtype=float)
        self.turn = wrap(heading - wedge.heading)
        # Book-keeping for the next move is updated right away, so several
        # moves can be queued before any of them is played.
        wedge.pivot, wedge.heading = self.pivot1, heading
        super().__init__(wedge, **kwargs)

    def interpolate_submobject(self, sub, start, alpha):
        a = self.turn * alpha
        c, s = np.cos(a), np.sin(a)
        rot = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
        tip = interpolate(self.pivot0, self.pivot1, alpha)
        sub.points = (start.points - self.pivot0) @ rot.T + tip


def make_wedges(n, radius=R):
    """A circle of radius `radius`, centred at ORIGIN, cut into n wedges.

    Wedge i spans the angles [i·dθ, (i+1)·dθ]. Each wedge is a VGroup of
    (teal body, blue arc) and remembers its tip (`pivot`) and the direction
    its arc faces (`heading`), which RigidMove uses.
    """
    dtheta = TAU / n
    outline = {8: 2.0, 16: 1.5, 32: 1.0}.get(n, 0.75)
    arc_width = {8: 6, 16: 5, 32: 4}.get(n, 3)
    wedges = VGroup()
    for i in range(n):
        light = (i < n // 2) if COLOR_BY_HALF else (i % 2 == 0)
        body = Sector(
            radius=radius, angle=dtheta, start_angle=i * dtheta,
            fill_color=TEAL_LIGHT if light else TEAL_DARK, fill_opacity=1,
            stroke_color=BLACK, stroke_width=outline,
        )
        edge = Arc(radius=radius, start_angle=i * dtheta, angle=dtheta,
                   color=EDGE_COLOR, stroke_width=arc_width)
        w = VGroup(body, edge)
        w.body, w.edge, w.index = body, edge, i
        w.pivot, w.heading = ORIGIN.copy(), (i + 0.5) * dtheta
        wedges.add(w)
    return wedges


def strip_geometry(n, radius=R):
    """Numbers that describe the unrolled strip of n wedges.

    c    chord of one wedge (its width in the strip)
    h    tip-to-chord height of one wedge
    x0   x of the leftmost downward tip
    bump how far each arc bulges past its chord
    """
    dtheta = TAU / n
    c = 2 * radius * np.sin(dtheta / 2)
    h = radius * np.cos(dtheta / 2)
    x0 = -(n - 1) * c / 4          # centres the parallelogram on ORIGIN
    return c, h, x0, radius - h


def rows(wedges):
    """(top row, bottom row), each listed left to right in the strip.
    Unrolling the top half left-to-right walks its arc from angle π down to 0;
    the bottom half walks from π up to 2π."""
    n = len(wedges)
    top = [wedges[n // 2 - 1 - k] for k in range(n // 2)]
    bottom = [wedges[n // 2 + k] for k in range(n // 2)]
    return top, bottom


def strip_layout(n, separated=False):
    """Target (tip, heading) for every wedge index in the unrolled strip.

    Top-half wedges hang tip-down with their arcs forming the top edge;
    bottom-half wedges stand tip-up with their arcs forming the bottom edge.
    Each top tip drops into the notch between two bottom wedges, so the rows
    interleave into a parallelogram πr wide (in the limit) and r tall.

    separated=True pulls the rows apart vertically (and lines them up
    horizontally) so the two halves can be unrolled before they meet.
    """
    c, h, x0, _ = strip_geometry(n)
    shift = np.array([c / 4, (h + ROW_GAP) / 2, 0]) if separated else np.zeros(3)
    targets = [None] * n
    for k in range(n // 2):
        targets[n // 2 - 1 - k] = (np.array([x0 + k * c, -h / 2, 0]) + shift, PI / 2)
        targets[n // 2 + k] = (np.array([x0 + (k + 0.5) * c, h / 2, 0]) - shift, -PI / 2)
    return targets


def to_strip(wedges, which="both", separated=False, spread=0.3):
    """Animation: unroll `which` wedges ("top", "bottom" or "both") into the
    strip. This is the reusable rearrangement for any n (8, 16, 32, 64...)."""
    targets = strip_layout(len(wedges), separated)
    top, bottom = rows(wedges)
    if which == "top":
        movers = top
    elif which == "bottom":
        movers = bottom
    else:  # left to right across the finished strip
        movers = [w for pair in zip(top, bottom) for w in pair]
    return lagged([RigidMove(w, *targets[w.index]) for w in movers], spread)


def to_circle(wedges, explode=0.0, spread=0.15):
    """Animation: send every wedge back to its place in the circle
    (optionally pushed out by `explode` along its own direction)."""
    n = len(wedges)
    moves = []
    for w in wedges:
        heading = (w.index + 0.5) * TAU / n
        moves.append(RigidMove(w, explode * unit(heading), heading))
    return lagged(moves, spread)


def new_cut_flash(n):
    """Brief white flash along the cuts that turn n/2 slices into n."""
    dtheta = TAU / n
    return AnimationGroup(*[
        ShowPassingFlash(Line(ORIGIN, R * unit(j * dtheta)).set_stroke(WHITE, 2.5),
                         time_width=0.6)
        for j in range(1, n, 2)
    ])


def bump_guides(n):
    """Dashed straight lines along the chords of the top and bottom rows:
    the edge the strip *would* have if the arcs were perfectly flat."""
    c, h, x0, _ = strip_geometry(n)
    style = dict(dash_length=0.1, dashed_ratio=0.55, stroke_width=2.5, color=WHITE)
    top = DashedLine([x0 - c / 2, h / 2, 0], [x0 + (n / 2 - 0.5) * c, h / 2, 0], **style)
    bottom = DashedLine([x0, -h / 2, 0], [x0 + n / 2 * c, -h / 2, 0], **style)
    return VGroup(top, bottom)


def strip_outline(n):
    """The (nearly rectangular) parallelogram traced by the strip's chords."""
    c, h, x0, _ = strip_geometry(n)
    return Polygon(
        [x0 - c / 2, h / 2, 0], [x0 + (n / 2 - 0.5) * c, h / 2, 0],
        [x0 + n / 2 * c, -h / 2, 0], [x0, -h / 2, 0],
    )


def pulse_edges(wedges, color=BLUE_A, width=9):
    """Make the blue arcs swell and brighten for a moment."""
    return AnimationGroup(*[
        w.edge.animate(rate_func=there_and_back).set_stroke(color, width=width)
        for w in wedges
    ])


# ═════════════════════════════════════════════════════════════════════════════
#  THE VIDEO
# ═════════════════════════════════════════════════════════════════════════════
class CircleArea(VoiceoverScene):
    def drop(self, *mobjects):
        """Remove mobjects and all their parts. (A plain remove() can miss parts
        that a LaggedStart has re-grouped inside the scene.)"""
        self.remove(*[m for mob in mobjects for m in mob.get_family()])

    def construct(self):
        self.camera.background_color = BLACK
        self.set_speech_service(make_speech_service())

        # ─────────────────────────────────────────────────────────────────────
        #  SCENE 1 — The circle
        # ─────────────────────────────────────────────────────────────────────
        circle = Circle(radius=R, color=WHITE, stroke_width=5)
        radius = Line(ORIGIN, R * RIGHT, color=RADIUS_COLOR, stroke_width=6)
        r_label = MathTex("r", color=RADIUS_COLOR).next_to(radius, UP, buff=0.15)

        with self.voiceover(text="Take a circle with radius r.") as tracker:
            t1, t2, t3 = split(tracker.duration, 0.45, 0.35, 0.20)
            self.play(Create(circle), run_time=t1)
            self.play(Create(radius), run_time=t2)          # sweeps out from the centre
            self.play(FadeIn(r_label, shift=0.2 * UP), run_time=t3)

        edge_glow = glow(circle, EDGE_COLOR)
        c_label = MathTex(r"2\pi r", color=EDGE_COLOR).move_to((R + 0.75) * unit(125 * DEGREES))

        with self.voiceover(text="Its edge, the circumference, has length two pi r.") as tracker:
            t1, t2, t3 = split(tracker.duration, 0.15, 0.45, 0.40)
            self.play(FadeOut(r_label), FadeOut(radius), run_time=t1)
            self.play(
                circle.animate.set_stroke(EDGE_COLOR, width=6),
                FadeIn(edge_glow, rate_func=there_and_back),
                run_time=t2,
            )
            self.drop(edge_glow)
            self.play(Write(c_label), run_time=t3)

        area = Circle(radius=R, stroke_width=0, fill_color=TEAL_E, fill_opacity=0.45)
        question = MathTex(r"\pi", "r", "^{2}", "?", font_size=60)
        question[1:3].set_color(RADIUS_COLOR)

        with self.voiceover(text="But why is its area pi r squared?") as tracker:
            t1, t2, t3 = split(tracker.duration, 0.15, 0.45, 0.40)
            self.play(FadeOut(c_label), run_time=t1)
            self.add(area, circle)                          # fill sits behind the edge
            self.play(FadeIn(area), run_time=t2)
            self.play(FadeIn(question, scale=1.2), run_time=t3)
        self.wait(PAUSE)

        # ─────────────────────────────────────────────────────────────────────
        #  SCENE 2 — Slicing
        # ─────────────────────────────────────────────────────────────────────
        wedges = make_wedges(8)
        cuts = VGroup(*[
            DashedLine(R * unit(a), -R * unit(a), dash_length=0.12, stroke_width=3)
            for a in np.arange(4) * PI / 4
        ])

        with self.voiceover(text="Let's cut it like a pizza.") as tracker:
            t1, t2, t3, t4 = split(span(tracker, 2.4), 0.12, 0.40, 0.20, 0.28)
            self.play(FadeOut(question), run_time=t1)
            self.play(lagged([Create(c) for c in cuts], 0.4), run_time=t2)
            self.play(FadeIn(wedges), FadeOut(cuts), run_time=t3)
            self.drop(area, circle)
            self.play(to_circle(wedges, explode=EXPLODE, spread=0), run_time=t4)

        # ─────────────────────────────────────────────────────────────────────
        #  SCENE 3 — Unrolling the edge
        # ─────────────────────────────────────────────────────────────────────
        with self.voiceover(text="Now unroll the top half, and the bottom half,") as tracker:
            t1, t2 = split(tracker.duration, 0.52, 0.48)
            self.play(to_strip(wedges, "top", separated=True), run_time=t1)
            self.play(to_strip(wedges, "bottom", separated=True), run_time=t2)

        with self.voiceover(text="and fit them together.") as tracker:
            # both rows slide as solid rows (no stagger): top down, bottom up
            self.play(to_strip(wedges, "both", spread=0), run_time=span(tracker, 1.2))

        c, h, x0, bump = strip_geometry(8)
        base = Line([x0, -h / 2, 0], [x0 + 4 * c, -h / 2, 0])
        half_brace = Brace(base, DOWN, buff=bump + 0.12)
        half_label = MathTex(r"2\pi r", r"\div 2").next_to(half_brace, DOWN, buff=0.15)
        half_label[0].set_color(EDGE_COLOR)
        pi_r = MathTex(r"\pi r", color=EDGE_COLOR).move_to(half_label)
        _, bottom_row = rows(wedges)

        with self.voiceover(text="Half of the edge ends up on the bottom, so this side is pi r.") as tracker:
            t1, t2, t3 = split(tracker.duration, 0.30, 0.35, 0.35)
            self.play(pulse_edges(bottom_row), run_time=t1)
            self.play(GrowFromCenter(half_brace), FadeIn(half_label, shift=0.15 * UP), run_time=t2)
            self.play(TransformMatchingShapes(half_label, pi_r), run_time=t3)
        self.wait(PAUSE)

        # ─────────────────────────────────────────────────────────────────────
        #  SCENE 4 — More slices (key moment)
        # ─────────────────────────────────────────────────────────────────────
        guides = bump_guides(8)

        with self.voiceover(text="It's a bit bumpy.") as tracker:
            t1, t2, t3 = split(span(tracker, 1.4), 0.25, 0.40, 0.35)
            self.play(FadeOut(half_brace), FadeOut(pi_r), run_time=t1)
            self.play(Create(guides), run_time=t2)
            self.play(pulse_edges(wedges), run_time=t3)

        def more_slices(old, n, total):
            """Reassemble -> cut finer -> unroll again. Returns the new wedges."""
            t_back, t_cut, t_out = split(total, 0.32, 0.20, 0.48)
            self.play(to_circle(old), run_time=t_back)
            new = make_wedges(n)
            self.play(FadeIn(new), new_cut_flash(n), run_time=t_cut)
            self.drop(old)
            self.play(to_strip(new), run_time=t_out)
            return new

        with self.voiceover(text="So let's use more slices.") as tracker:
            self.play(FadeOut(guides), run_time=0.2)
            wedges = more_slices(wedges, 16, span(tracker, 2.6) - 0.2)

        with self.voiceover(text="More.") as tracker:
            wedges = more_slices(wedges, 32, span(tracker, 2.0))

        with self.voiceover(text="And more.") as tracker:
            wedges = more_slices(wedges, 64, span(tracker, 1.6))

        guides = bump_guides(64)
        outline = strip_outline(64).set_stroke(WHITE, 6)

        with self.voiceover(text="The bumps flatten out, and the shape becomes a rectangle.") as tracker:
            t1, t2, t3 = split(tracker.duration, 0.40, 0.40, 0.20)
            self.play(Create(guides), run_time=t1)
            self.play(
                wedges.animate(rate_func=there_and_back).set_fill(WHITE),
                ShowPassingFlash(outline, time_width=0.5),
                run_time=t2,
            )
            self.play(FadeOut(guides), run_time=t3)
        self.wait(PAUSE)

        # ─────────────────────────────────────────────────────────────────────
        #  SCENE 5 — Reading the rectangle
        # ─────────────────────────────────────────────────────────────────────
        n = len(wedges)
        c, h, x0, bump = strip_geometry(n)

        width_brace = Brace(Line([x0, -h / 2, 0], [x0 + n / 2 * c, -h / 2, 0]), DOWN, buff=0.15)
        width_label = MathTex(r"\pi r", color=EDGE_COLOR).next_to(width_brace, DOWN, buff=0.15)

        with self.voiceover(text="Its width is pi r.") as tracker:
            self.play(GrowFromCenter(width_brace), FadeIn(width_label, shift=0.15 * UP),
                      run_time=tracker.duration)

        # the right-most wedge stands tip-up; its axis is exactly one radius
        slice_ = wedges[n - 1]
        tip = slice_.pivot
        axis = Line(tip, tip + R * DOWN, color=RADIUS_COLOR, stroke_width=5)
        right_x = x0 + n / 2 * c + 0.12
        height_brace = Brace(Line([right_x, tip[1], 0], [right_x, tip[1] - R, 0]), RIGHT, buff=0.1)
        height_label = MathTex("r", color=RADIUS_COLOR).next_to(height_brace, RIGHT, buff=0.15)
        others = [w for w in wedges if w is not slice_]
        slice_color = slice_.body.get_fill_color()

        with self.voiceover(text="And its height is just one slice — the radius, r.") as tracker:
            t1, t2, t3 = split(tracker.duration, 0.30, 0.35, 0.35)
            self.play(
                *[w.body.animate.set_fill(opacity=DIM) for w in others],
                *[w.edge.animate.set_stroke(opacity=DIM) for w in others],
                slice_.body.animate.set_fill(TEAL_A),
                run_time=t1,
            )
            self.play(Create(axis), run_time=t2)            # the radius, again
            self.play(GrowFromCenter(height_brace), FadeIn(height_label, shift=0.15 * LEFT),
                      run_time=t3)

        product = MathTex(r"\text{Area}", "=", r"\pi r", r"\cdot", "r", font_size=60)
        product.move_to(2.6 * UP)
        product[2].set_color(EDGE_COLOR)
        product[4].set_color(RADIUS_COLOR)

        with self.voiceover(text="Width times height: pi r times r.") as tracker:
            t1, t2, t3 = split(tracker.duration, 0.25, 0.40, 0.35)
            self.play(Write(product[:2]), run_time=t1)
            self.play(TransformFromCopy(width_label, product[2]), FadeIn(product[3]), run_time=t2)
            self.play(TransformFromCopy(height_label, product[4]), run_time=t3)

        squared = MathTex(r"\text{Area}", "=", r"\pi", "r", "^{2}", font_size=60)
        squared.move_to(product)
        squared[3:].set_color(RADIUS_COLOR)

        with self.voiceover(text="Pi r squared.") as tracker:
            # the two r's merge: the second r flies up and becomes the exponent
            self.play(
                ReplacementTransform(product[0], squared[0]),
                ReplacementTransform(product[1], squared[1]),
                ReplacementTransform(product[2][0], squared[2]),
                ReplacementTransform(product[2][1], squared[3]),
                FadeOut(product[3]),
                ReplacementTransform(product[4], squared[4], path_arc=-PI / 2),
                run_time=span(tracker, 1.0),
            )
        self.add(squared)                                   # regroup the morphed parts
        self.wait(PAUSE)

        # ─────────────────────────────────────────────────────────────────────
        #  SCENE 6 — Payoff
        # ─────────────────────────────────────────────────────────────────────
        final = MathTex("A", "=", r"\pi", "r", "^{2}", font_size=72)
        final[3:].set_color(RADIUS_COLOR)
        frame = RoundedRectangle(corner_radius=0.18, width=final.width + 0.8,
                                 height=final.height + 0.6)
        frame.set_fill(BLACK, 0.85).set_stroke(WHITE, 3)
        halo = glow(frame, WHITE)
        badge = VGroup(halo, frame).set_z_index(5)
        squared.set_z_index(6)                              # stays above the badge
        final.set_z_index(6)

        with self.voiceover(text="So the area of a circle is the area of a rectangle in disguise.") as tracker:
            t1, t2, t3, t4 = split(tracker.duration, 0.15, 0.45, 0.22, 0.18)
            self.play(
                FadeOut(VGroup(width_brace, width_label, height_brace, height_label, axis)),
                *[w.body.animate.set_fill(opacity=1) for w in others],
                *[w.edge.animate.set_stroke(opacity=1) for w in others],
                slice_.body.animate.set_fill(slice_color),
                run_time=t1,
            )
            self.play(to_circle(wedges, spread=0.25), run_time=t2)
            self.play(
                ReplacementTransform(squared[0][0], final[0]),  # "Area" shrinks to "A"
                FadeOut(squared[0][1:], target_position=final[0], scale=0.5),
                *[ReplacementTransform(squared[k], final[k]) for k in range(1, 5)],
                run_time=t3,
            )
            self.play(FadeIn(badge, scale=1.15), run_time=t4)  # glowing outline settles in
        self.wait(2)                                        # let it sink in
        self.play(FadeOut(Group(*self.mobjects)), run_time=1.2)
