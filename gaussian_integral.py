"""
Qauss inteqralı:  ∫ e^(−x²) dx = √π   (−∞ … +∞)
================================================
3Blue1Brown üslubunda, səssiz vizual isbat (Manim Community Edition).

Yol: 2D zəng əyrisi → inteqralı kvadrata yüksəltmək → 3D zəng səthi →
dairəvi simmetriya → silindrik təbəqələr → I² = π → I = √π.

QURAŞDIRMA
----------
    # 1) Sistem paketləri
    #    macOS:          brew install ffmpeg py3cairo pango pkg-config
    #                    brew install --cask mactex-no-gui
    #    Ubuntu/Debian:  sudo apt install ffmpeg libcairo2-dev libpango1.0-dev pkg-config \
    #                        texlive texlive-latex-extra dvisvgm fonts-cmu
    #    Windows:        choco install ffmpeg miktex   (+ "CMU Serif" şriftini quraşdırın, aşağıya baxın)
    #
    #    "CMU Serif" şrifti Linux-da fonts-cmu paketindədir; macOS/Windows üçün
    #    https://ctan.org/pkg/cm-unicode ünvanından yükləyib .otf fayllarını quraşdırın.
    #
    # 2) Python paketi (Python 3.10+)
    pip install manim

RENDER
------
    # 1) Tez yoxlama (480p, 15 fps):
    manim -pql gaussian_integral.py GaussianIntegral

    # 2) Yekun keyfiyyət (1080p, 60 fps):
    manim -pqh gaussian_integral.py GaussianIntegral

    # Bir kadrı yoxlamaq üçün (məs. son kadr):
    manim -sql gaussian_integral.py GaussianIntegral

Video media/videos/gaussian_integral/1080p60/GaussianIntegral.mp4 faylına yazılır.

TƏNZİMLƏMƏ
----------
* Kamera bucaqları: aşağıdakı FRONT / VIEW3D / TOP lüğətləri.
* Sürət: PACE (1.0 = normal; 0.8 hər şeyi 20 % sürətləndirir).
  Hər səhnənin öz run_time dəyərləri həmin səhnənin metodundadır.
* Rənglər, ölçülər, şrift: faylın yuxarısındakı sabitlər.
"""

from __future__ import annotations

from math import erf

import numpy as np
from manim import *
from manim.animation.animation import prepare_animation

config.background_color = BLACK


# ═════════════════════════════════════════════════════════════════════════════
#  MƏTN
# ═════════════════════════════════════════════════════════════════════════════
# Computer Modern (LaTeX-in və 3Blue1Brown videolarının şrifti) — Unicode versiyası
# ə ş ğ ı İ ö ü ç hərflərinin hamısını dəstəkləyir və düsturlarla eyni görünür.
FONT = "CMU Serif"
CAPTION_SIZE = 34           # alt yazıların ölçüsü
TEX_SIZE = 48               # yuxarıdakı düsturların ölçüsü
BIG_TEX = 58                # ekranın ortasındakı düsturların ölçüsü

# ═════════════════════════════════════════════════════════════════════════════
#  RƏNGLƏR (bütün video boyu eyni qalır)
# ═════════════════════════════════════════════════════════════════════════════
C_X = BLUE                  # e^(−x²) əyrisi və altındakı sahə
C_Y = YELLOW                # e^(−y²) əyrisi
C_SURF_LOW = BLUE           # 3D səth: aşağı hissə …
C_SURF_HIGH = YELLOW        # … zirvə
C_SHELL = RED               # silindrik təbəqə
C_RESULT = GREEN            # √π
C_AXIS = GREY_C             # nazik boz oxlar
C_SOFT = GREY_B             # köməkçi yazılar

# ═════════════════════════════════════════════════════════════════════════════
#  ÖLÇÜLƏR
#  Riyazi koordinat (x, y, z) → səhnə koordinatı (x·U, y·U, z·H)
# ═════════════════════════════════════════════════════════════════════════════
U = 1.2                     # x və y vahidi
H = 2.6                     # hündürlük vahidi (z = 1 → 2.6 vahid)
X_MAX = 3.4                 # 2D əyrinin uzunluğu: −X_MAX … X_MAX
AXIS_LEN = 3.6              # x və y oxlarının yarı uzunluğu
Z_AXIS_LEN = 1.3            # z oxunun uzunluğu
R_MAX = 2.6                 # 3D səthin radiusu
SURF_RES = (26, 48)         # səthin şəbəkəsi: (radial, bucaq)
SURF_OPACITY = 0.6
SURF_DIM = 0.25             # təbəqələr görünəndə səthin şəffaflığı

SHELL_R = 0.65              # Səhnə 6: əsas təbəqənin radiusu r
SHELL_DR = 0.25             # … və qalınlığı dr (görünsün deyə şişirdilib)
SHELL_RES = 40              # təbəqə divarının hissə sayı
SHELL_OPACITY = 0.9
N_SHELLS = 10               # həcmi dolduran təbəqələrin sayı

# ═════════════════════════════════════════════════════════════════════════════
#  KAMERA
# ═════════════════════════════════════════════════════════════════════════════
# 2D: öndən baxış — zəng əyrisi xz-müstəvisində durur, ona görə 3D-yə keçəndə
# əyri yerində qalır, sadəcə kamera fırlanır.
FRONT = dict(phi=90 * DEGREES, theta=-90 * DEGREES, zoom=1.0, frame_center=[0, 0, 0.9])
# 3D: əsas bucaq
VIEW3D = dict(phi=65 * DEGREES, theta=-45 * DEGREES, zoom=1.1, frame_center=[0, 0, 0.6])
# Yuxarıdan baxış (Səhnə 5). Səth ortada qalır (perspektiv simmetrik olsun), düstur sağdadır.
TOP = dict(phi=0 * DEGREES, theta=-90 * DEGREES, zoom=0.85, frame_center=[0, 0, 0])
AMBIENT_RATE = 0.12         # Səhnə 4: kameranın fırlanma sürəti (rad/san)
SIDE_SHIFT = 2.6            # Səhnə 6: kamera təbəqənin ardınca sağa nə qədər sürüşür
SIDE_ZOOM = 0.78            # … və o anda zoom
SHELL_FLY = 5.8             # Səhnə 6: təbəqənin yan tərəfə uçduğu məsafə

PACE = 1.0                  # bütün vaxtların ümumi əmsalı


def rt(seconds):
    """Hər run_time / wait bu funksiyadan keçir — PACE ilə hamısı birlikdə dəyişir."""
    return seconds * PACE


# ═════════════════════════════════════════════════════════════════════════════
#  KİÇİK KÖMƏKÇİLƏR
# ═════════════════════════════════════════════════════════════════════════════
INT = r"\int_{-\infty}^{\infty}"
IINT = r"\iint_{\mathbb{R}^2}"


def P(x, y=0.0, z=0.0):
    """Riyazi koordinatdan səhnə koordinatına."""
    return np.array([x * U, y * U, z * H])


def gauss(x):
    return np.exp(-x * x)


def az_text(text, size, color=WHITE):
    """Azərbaycanca mətn. 4 dəfə böyük render edilib kiçildilir: kiçik ölçüdə
    Pango hərf aralıqlarını qeyri-bərabər qoyur ("kəsi yin" kimi)."""
    return Text(text, font=FONT, font_size=4 * size, color=color).scale(0.25)


def caption(text):
    """Ekranın altında bir sətirlik izah."""
    return az_text(text, CAPTION_SIZE).to_edge(DOWN, buff=0.5)


def words(text, size=26, color=C_SOFT):
    """Kiçik köməkçi söz (ölçü etiketləri üçün)."""
    return az_text(text, size, color)


def row(*items, buff=0.2):
    """Text və MathTex-i bir sətirdə düzür: düsturun baza xətti mətninkinə hizalanır."""
    group = VGroup(*items).arrange(RIGHT, buff=buff)
    text = next(m for m in items if isinstance(m, Text))
    base = float(np.median([g.get_bottom()[1] for g in text.family_members_with_points()]))
    for m in items:
        if isinstance(m, MathTex):
            m.shift((base - min(g.get_bottom()[1] for g in m.family_members_with_points())) * UP)
    return group


def glow(mob, color, layers=((8, 0.30), (16, 0.12), (26, 0.05))):
    """Yumşaq parıltı: konturun bir neçə enli, solğun nüsxəsi."""
    return VGroup(*[
        mob.copy().set_fill(opacity=0).set_stroke(color, width=w, opacity=o)
        for w, o in layers
    ])


# ─── 2D zəng əyriləri (xz- və yz-müstəvilərində) ────────────────────────────
def x_bell(color=C_X, width=4):
    """z = e^(−x²), y = 0 müstəvisində."""
    return ParametricFunction(lambda s: P(s, 0, gauss(s)), t_range=[-X_MAX, X_MAX, 0.04],
                              color=color, stroke_width=width)


def y_bell(color=C_Y, width=4):
    """z = e^(−y²), x = 0 müstəvisində."""
    return ParametricFunction(lambda s: P(0, s, gauss(s)), t_range=[-X_MAX, X_MAX, 0.04],
                              color=color, stroke_width=width)


def x_area(x0=-X_MAX, x1=X_MAX, color=C_X, opacity=0.35):
    """Mavi əyrinin altındakı sahə, x0-dan x1-ə qədər."""
    x1 = max(x1, x0 + 1e-3)
    xs = np.linspace(x0, x1, max(3, int((x1 - x0) / 0.04)))
    pts = [P(x, 0, gauss(x)) for x in xs] + [P(x1), P(x0)]
    return Polygon(*pts, stroke_width=0, fill_color=color, fill_opacity=opacity)


def y_area(color=C_Y, opacity=0.3):
    ys = np.linspace(-X_MAX, X_MAX, 170)
    pts = [P(0, y, gauss(y)) for y in ys] + [P(0, X_MAX), P(0, -X_MAX)]
    return Polygon(*pts, stroke_width=0, fill_color=color, fill_opacity=opacity)


def make_axes():
    style = dict(color=C_AXIS, stroke_width=1.5)
    return (
        Line(P(-AXIS_LEN), P(AXIS_LEN), **style),
        Line(P(0, -AXIS_LEN), P(0, AXIS_LEN), **style),
        Line(P(0, 0, 0), P(0, 0, Z_AXIS_LEN), **style),
    )


# ─── 3D zəng səthi z = e^(−(x²+y²)) ─────────────────────────────────────────
def height_color(h):
    return interpolate_color(C_SURF_LOW, C_SURF_HIGH, float(np.clip(h, 0, 1)))


def paint_surface(surface, opacity=SURF_OPACITY, bands=False):
    """Hündürlüyə görə mavidən sarıya qradiyent. bands=True: konsentrik zolaqlar."""
    for face in surface.submobjects:
        r = 0.5 * (face.u1 + face.u2)
        color = height_color(gauss(r))
        if bands and (face.u_index // 3) % 2:
            color = interpolate_color(color, BLACK, 0.55)
        face.set_fill(color, opacity=opacity)
        face.set_stroke(color, width=0.5, opacity=0.35 * opacity)
    return surface


def bell_surface(opacity=SURF_OPACITY):
    """Qütb koordinatlarında qurulur: şəbəkə xətləri özləri dairə və radiuslardır."""
    surface = Surface(
        lambda u, v: P(u * np.cos(v), u * np.sin(v), gauss(u)),
        u_range=[0, R_MAX], v_range=[0, TAU], resolution=SURF_RES,
        checkerboard_colors=False, fill_opacity=opacity, stroke_width=0,
    )
    return paint_surface(surface, opacity)


# ─── Səhnə 4: x = c kəsiyi ──────────────────────────────────────────────────
def slice_plane(c):
    return Polygon(
        P(c, -AXIS_LEN), P(c, AXIS_LEN), P(c, AXIS_LEN, 1.15), P(c, -AXIS_LEN, 1.15),
        stroke_color=GREY_B, stroke_width=1, fill_color=GREY_A, fill_opacity=0.08,
    )


def slice_curve(c):
    """Kəsik əyrisi z = e^(−c²)·e^(−y²): yenə zəng, sadəcə e^(−c²) dəfə alçaq."""
    y_max = np.sqrt(max(R_MAX ** 2 - c ** 2, 0.04))
    k = gauss(c)
    return ParametricFunction(lambda s: P(c, s, k * gauss(s)), t_range=[-y_max, y_max, 0.04],
                              color=WHITE, stroke_width=4)


def slice_fill(c):
    """Kəsiyin sahəsi + əyrinin parıltısı."""
    y_max = np.sqrt(max(R_MAX ** 2 - c ** 2, 0.04))
    k = gauss(c)
    ys = np.linspace(-y_max, y_max, 90)
    area = Polygon(*[P(c, y, k * gauss(y)) for y in ys], P(c, y_max), P(c, -y_max),
                   stroke_width=0, fill_color=WHITE, fill_opacity=0.22)
    return VGroup(area, glow(slice_curve(c), WHITE))


# ═════════════════════════════════════════════════════════════════════════════
#  SİLİNDRİK TƏBƏQƏ  və onu düz lövhəyə AÇAN animasiya
# ═════════════════════════════════════════════════════════════════════════════
def make_shell(r, dr, height=None, unroll=0.0, center=ORIGIN, facing=VIEW3D["theta"],
               color=C_SHELL, opacity=SHELL_OPACITY, inner=True, res=SHELL_RES):
    """Daxili radiusu r, qalınlığı dr, hündürlüyü e^(−r²) olan silindrik təbəqə.

    unroll = 0 → silindr, unroll = 1 → uzunluğu 2πr olan düz lövhə.
    Açılma zamanı divarın əyriliyi 1/r-dən 0-a enir, uzunluq isə dəyişmir:
    divar kameraya baxan nöqtədən (facing bucağı) yapışıb qalır, arxadan kəsilir
    və iki yana açılır. Qalınlıq istiqaməti həmişə divara perpendikulyardır.
    r, dr, height riyazi vahidlərdədir; center səhnə koordinatıdır.
    """
    h = gauss(r) if height is None else height
    R0, Dw, Hw = r * U, dr * U, max(h, 1e-3) * H
    front = np.array([np.cos(facing), np.sin(facing), 0.0])     # kameraya doğru
    side = np.array([-np.sin(facing), np.cos(facing), 0.0])     # ekranda sağa
    inward = -front
    kappa = 1.0 - unroll                                        # nisbi əyrilik
    center = np.array(center, dtype=float)

    def point(t, d, z):
        """t ∈ [−π, π]: ön nöqtədən bucaq, d: xaricə qalınlıq, z: hündürlük."""
        if kappa > 1e-4:
            along = R0 * np.sin(kappa * t) / kappa
            depth = R0 * (1 - np.cos(kappa * t)) / kappa
            ang = kappa * t
        else:
            along, depth, ang = R0 * t, 0.0, 0.0
        normal_in = -np.sin(ang) * side + np.cos(ang) * inward
        return center + R0 * front + along * side + depth * inward - d * normal_in + z * OUT

    style = dict(checkerboard_colors=False, fill_color=color, fill_opacity=opacity,
                 stroke_color=color, stroke_width=0.6, stroke_opacity=0.6 * opacity)
    parts = [
        Surface(lambda t, z: point(t, Dw, z), u_range=[-PI, PI], v_range=[0, Hw],
                resolution=(res, 1), **style),                  # xarici divar
        Surface(lambda t, d: point(t, d, Hw), u_range=[-PI, PI], v_range=[0, Dw],
                resolution=(res, 1), **style),                  # üst halqa
        Surface(lambda d, z: point(-PI, d, z), u_range=[0, Dw], v_range=[0, Hw],
                resolution=(1, 1), **style),                    # kəsik ucu
        Surface(lambda d, z: point(PI, d, z), u_range=[0, Dw], v_range=[0, Hw],
                resolution=(1, 1), **style),                    # digər uc
    ]
    if inner:
        parts.append(Surface(lambda t, z: point(t, 0, z), u_range=[-PI, PI], v_range=[0, Hw],
                             resolution=(res, 1), **style))     # daxili divar
    return VGroup(*parts)


def morph_shell(shell, r, dr, start, end, **fixed):
    """Təbəqəni iki parametr vəziyyəti arasında hərəkət etdirir
    (height, unroll, center, opacity ...). Hər kadrda yenidən qurulur."""
    def update(mob, alpha):
        params = {k: interpolate(np.array(start[k], dtype=float), np.array(end[k], dtype=float), alpha)
                  for k in start}
        params = {k: (float(v) if v.ndim == 0 else v) for k, v in params.items()}
        mob.become(make_shell(r, dr, **fixed, **params))
    return UpdateFromAlphaFunc(shell, update)


def unroll_shell(shell, r, dr, center=ORIGIN, **fixed):
    """Silindrik təbəqəni düz lövhəyə açan animasiya (2πr × e^(−r²) × dr)."""
    return morph_shell(shell, r, dr, dict(unroll=0.0), dict(unroll=1.0), center=center, **fixed)


# ─── Səhnə 8: sahəni zolaqlara bölüb düzbucaqlıya tökmək ────────────────────
def strip_shape(a, b, color=C_X):
    xs = np.linspace(a, b, 6)
    pts = [P(x, 0, gauss(x)) for x in xs] + [P(b), P(a)]
    return Polygon(*pts, fill_color=color, fill_opacity=0.6, stroke_color=BLACK, stroke_width=1)


# ═════════════════════════════════════════════════════════════════════════════
#  DÜSTUR KEÇİDİ
# ═════════════════════════════════════════════════════════════════════════════
class MatchTex(AnimationGroup):
    """TransformMatchingTex ilə eyni iş: eyni hədlər (eyni TeX parçası) yeni
    yerinə uçur, qalanları itir/yaranır. Fərq yalnız key_map cütlərindədir:
    onlar adi Transform ilə uçur, ona görə "I" → "I^2" kimi simvol sayı fərqli
    parçalar da işləyir (TransformMatchingTex orada xəta verir)."""

    def __init__(self, source, target, key_map=None, **kwargs):
        def parts(mob):
            groups = {}
            for part in mob.submobjects:
                groups.setdefault(part.tex_string, VGroup()).add(part)
            return groups

        src, tgt = parts(source), parts(target)
        pairs = [(k, k) for k in src if k in tgt]
        pairs += [(a, b) for a, b in (key_map or {}).items()
                  if a in src and b in tgt and a not in tgt and b not in src]
        anims = [Transform(src[a], tgt[b]) for a, b in pairs]
        gone = VGroup(*[g for k, g in src.items() if k not in {a for a, _ in pairs}])
        new = VGroup(*[g for k, g in tgt.items() if k not in {b for _, b in pairs}]).copy()
        if len(gone):
            anims.append(FadeOut(gone))
        if len(new):
            anims.append(FadeIn(new))
        super().__init__(*anims, **kwargs)
        self.source, self.new, self.to_add = source, new, target

    def clean_up_from_scene(self, scene):
        for anim in self.animations:
            anim.interpolate(0)
        scene.remove(self.mobject, self.source, self.new)
        scene.add(self.to_add)


# ═════════════════════════════════════════════════════════════════════════════
#  VİDEO
# ═════════════════════════════════════════════════════════════════════════════
class GaussianIntegral(ThreeDScene):

    # ─── ekrana sabitlənmiş mətn/düstur köməkçiləri ─────────────────────────
    def fix(self, *mobs):
        """Mətni/düsturu ekrana sabitləyir (kamera fırlansa da oxunaqlı qalır).
        Səhnəyə əlavə ETMİR — bunu sonrakı animasiya edir."""
        for m in mobs:
            m.set_z_index(10)
        self.camera.add_fixed_in_frame_mobjects(*mobs)
        return mobs[0] if len(mobs) == 1 else mobs

    def fx(self, anim):
        """Animasiyanın yaratdığı bütün köməkçi obyektləri də ekrana sabitləyir
        (TransformMatchingTex-in kəsik parçaları, Flash xətləri və s.)."""
        anim = prepare_animation(anim)
        todo = [anim]
        while todo:
            a = todo.pop()
            todo.extend(getattr(a, "animations", ()) or ())
            for name in ("mobject", "target_mobject", "to_add", "to_add_on_completion"):
                m = getattr(a, name, None)
                if isinstance(m, Mobject):
                    self.camera.add_fixed_in_frame_mobjects(m)
        return anim

    def to_screen(self, point):
        """3D nöqtənin hazırkı kamerada ekrandakı yeri."""
        q = self.camera.project_point(np.array(point, dtype=float))
        q[2] = 0
        return q

    def sbrace(self, p1, p2, label, direction, color=WHITE, buff=0.08, size=34, label_buff=0.12):
        """İki 3D nöqtə arasında, ekrana sabitlənmiş mötərizə + etiket."""
        brace = BraceBetweenPoints(self.to_screen(p1), self.to_screen(p2),
                                   direction=direction, buff=buff, color=color)
        if isinstance(label, str):
            label = MathTex(label, font_size=size, color=color)
        brace.put_at_tip(label, buff=label_buff)
        group = VGroup(brace, label)
        return self.fix(group)

    def say(self, text, run_time=0.6):
        """Alt yazını göstərir (köhnəsi varsa, eyni anda yox olur)."""
        new = self.fix(caption(text) if isinstance(text, str) else text)
        anims = [FadeIn(new, shift=0.2 * UP)]
        if self.cap is not None:
            anims.append(FadeOut(self.cap, shift=0.2 * UP))
        self.play(*[self.fx(a) for a in anims], run_time=rt(run_time))
        self.cap = new

    def unsay(self):
        """Alt yazını gizlədən animasiya siyahısı (play(..., *self.unsay()) kimi istifadə)."""
        cap, self.cap = self.cap, None
        return [self.fx(FadeOut(cap))] if cap is not None else []

    def tmt(self, source, target, key_map=None, **kwargs):
        """Ekrana sabitlənmiş düsturlar üçün TransformMatchingTex.
        key_map lazım olanda eyni məntiqli MatchTex işlənir (yuxarıya baxın)."""
        self.fix(target)
        if key_map:
            return self.fx(MatchTex(source, target, key_map=key_map, **kwargs))
        return self.fx(TransformMatchingTex(source, target, **kwargs))

    # ─── ssenari ────────────────────────────────────────────────────────────
    def construct(self):
        self.cap = None
        self.set_camera_orientation(**FRONT)
        self.scene_1_bell_curve()
        self.scene_2_problem()
        self.scene_3_square_it()
        self.scene_4_bell_surface()
        self.scene_5_symmetry()
        self.scene_6_shells()
        self.scene_7_compute()
        self.scene_8_see_it()
        self.scene_9_final()

    # ═════════════════════════════════════════════════════════════════════════
    #  SƏHNƏ 1 — Zəng əyrisi                       (≈10 san · kamera: FRONT)
    # ═════════════════════════════════════════════════════════════════════════
    def scene_1_bell_curve(self):
        self.x_axis, self.y_axis, self.z_axis = make_axes()
        self.curve = x_bell().set_z_index(2)

        self.play(Create(self.x_axis), run_time=rt(0.8))
        self.play(Create(self.curve), run_time=rt(1.4))

        # sahə soldan sağa dolur
        x_end = ValueTracker(-X_MAX)
        self.area = always_redraw(lambda: x_area(-X_MAX, x_end.get_value()))
        self.add(self.area)
        self.play(x_end.animate.set_value(X_MAX), run_time=rt(1.7), rate_func=linear)
        self.area.clear_updaters()
        self.wait(rt(0.5))

        self.I = MathTex("I", "=", INT, "e^{-x^2}", r"\,dx", font_size=TEX_SIZE)
        self.I[3].set_color(C_X)
        self.I.to_edge(UP, buff=0.5)
        self.fix(self.I)
        self.play(self.fx(Write(self.I)), run_time=rt(1.0))

        self.say("Bu sahə nəyə bərabərdir?")
        self.play(self.area.animate(rate_func=there_and_back).set_fill(opacity=0.75),
                  run_time=rt(1.0))
        self.wait(rt(2.6))

    # ═════════════════════════════════════════════════════════════════════════
    #  SƏHNƏ 2 — Problem                            (≈8 san · kamera: FRONT)
    # ═════════════════════════════════════════════════════════════════════════
    def scene_2_problem(self):
        question = MathTex(r"\int", "e^{-x^2}", r"\,dx", "=", "?", font_size=TEX_SIZE)
        question[1].set_color(C_X)
        row = VGroup(self.I.copy(), question).arrange(RIGHT, buff=1.6).to_edge(UP, buff=0.5)
        self.fix(question)

        self.play(self.I.animate.move_to(row[0]),
                  self.fx(FadeIn(question, shift=0.3 * LEFT)), run_time=rt(0.9))
        self.say("Bu funksiyanın elementar ibtidai funksiyası yoxdur")
        self.wait(rt(1.0))

        mark = question[4]
        self.play(mark.animate.set_color(RED).scale(1.4), run_time=rt(0.4))
        self.play(Wiggle(mark, scale_value=1.3, rotation_angle=0.08 * TAU, n_wiggles=6),
                  run_time=rt(1.0))
        self.wait(rt(0.4))

        # hər şey yox olur, yalnız I qalır (ortaya gəlir)
        self.play(self.fx(FadeOut(question)), *self.unsay(),
                  FadeOut(self.curve), FadeOut(self.area), FadeOut(self.x_axis),
                  self.I.animate.scale(BIG_TEX / TEX_SIZE).move_to(0.6 * UP),
                  run_time=rt(0.9))
        self.say("Fənd: inteqralı kvadrata yüksəldək")
        self.wait(rt(2.2))

    # ═════════════════════════════════════════════════════════════════════════
    #  SƏHNƏ 3 — I² və ikinci ölçü        (≈14 san · kamera: FRONT → VIEW3D)
    # ═════════════════════════════════════════════════════════════════════════
    def scene_3_square_it(self):
        squared = MathTex("I^2", "=", r"\Big(", INT, "e^{-x^2}", r"\,dx", r"\Big)",
                          r"\Big(", INT, "e^{-y^2}", r"\,dy", r"\Big)", font_size=BIG_TEX)
        squared[4].set_color(C_X)
        squared[9].set_color(C_Y)

        double = MathTex("I^2", "=", IINT, "e^{-x^2}", "e^{-y^2}", r"\,dx", r"\,dy",
                         font_size=BIG_TEX)
        double[3].set_color(C_X)
        double[4].set_color(C_Y)

        joined = MathTex("I^2", "=", IINT, "e^{-(x^2+y^2)}", r"\,dx", r"\,dy", font_size=BIG_TEX)
        joined[3][3:5].set_color(C_X)       # x²
        joined[3][6:8].set_color(C_Y)       # y²

        for m in (squared, double, joined):
            m.move_to(0.6 * UP)

        # I → I² = (∫…dx)(∫…dy)
        self.play(self.tmt(self.I, squared, key_map={"I": "I^2"}), *self.unsay(),
                  run_time=rt(1.1))
        self.wait(rt(0.9))
        # → ∬ e^{-x²} e^{-y²} dx dy
        self.play(self.tmt(squared, double, key_map={INT: IINT}), run_time=rt(1.0))
        self.wait(rt(0.9))
        # → ∬ e^{-(x²+y²)} dx dy   (iki e bir e-yə birləşir: simvol səviyyəsində uyğunlaşma)
        self.fix(joined)
        self.play(self.fx(TransformMatchingShapes(double, joined)), run_time=rt(1.0))
        self.wait(rt(0.9))

        # düstur yuxarı qalxır, mavi əyri geri gəlir
        self.eq = joined
        self.play(joined.animate.scale(TEX_SIZE / BIG_TEX).to_edge(UP, buff=0.4),
                  FadeIn(self.x_axis), FadeIn(self.curve), FadeIn(self.area),
                  run_time=rt(0.9))

        # 2D → 3D: kamera hamar fırlanır, y və z oxları yaranır
        self.move_camera(**VIEW3D, run_time=rt(2.5),
                         added_anims=[Create(self.y_axis), Create(self.z_axis)])

        # sarı e^(−y²) əyrisi y oxu boyunca
        self.y_curve = y_bell().set_z_index(2)
        self.y_area = y_area()
        self.play(Create(self.y_curve), run_time=rt(1.2))
        self.play(FadeIn(self.y_area), run_time=rt(0.5))
        self.say("Bu, səth altındakı həcmdir")
        self.wait(rt(2.2))

    # ═════════════════════════════════════════════════════════════════════════
    #  SƏHNƏ 4 — 3D zəng səthi            (≈12 san · kamera: VIEW3D + fırlanma)
    # ═════════════════════════════════════════════════════════════════════════
    def scene_4_bell_surface(self):
        # səth yerdən yuxarı qalxır
        self.surface = bell_surface()
        flat = self.surface.copy().stretch(1e-3, 2, about_point=ORIGIN)
        self.play(ReplacementTransform(flat, self.surface),
                  FadeOut(self.area), FadeOut(self.y_area), *self.unsay(),
                  run_time=rt(2.0))
        self.begin_ambient_camera_rotation(rate=AMBIENT_RATE)

        # x = c müstəvisi
        c = ValueTracker(-1.0)
        self.cut_plane = always_redraw(lambda: slice_plane(c.get_value()))
        self.cut_fill = always_redraw(lambda: slice_fill(c.get_value()))
        self.cut_line = always_redraw(lambda: slice_curve(c.get_value()).set_z_index(3))
        self.play(FadeIn(self.cut_plane), self.fx(FadeOut(self.eq)), run_time=rt(0.6))

        # sarı zəng sürüşüb kəsiyə çevrilir → kəsik də zəngdir, sadəcə e^{-c²} dəfə alçaq
        ghost = self.y_curve.copy().set_z_index(3)
        self.play(Transform(ghost, slice_curve(c.get_value()).set_z_index(3)), run_time=rt(1.0))
        self.remove(ghost)
        self.add(self.cut_line)
        self.play(FadeIn(self.cut_fill),
                  ShowPassingFlash(slice_curve(c.get_value()).set_stroke(WHITE, 10),
                                   time_width=0.5),
                  run_time=rt(0.8))

        # hər kəsiyin sahəsi = e^{-x²}·I
        area_tex = MathTex("=", "e^{-x^2}", r"\cdot", "I", font_size=TEX_SIZE)
        area_tex[1].set_color(C_X)
        self.cut_formula = row(words("Hər kəsiyin sahəsi", size=34, color=WHITE), area_tex,
                               buff=0.25).to_edge(UP, buff=0.45)
        self.fix(self.cut_formula)
        self.play(self.fx(FadeIn(self.cut_formula, shift=0.2 * DOWN)), run_time=rt(0.8))
        self.wait(rt(0.4))

        # müstəvi x oxu boyunca hərəkət edir
        self.play(c.animate.set_value(1.3), run_time=rt(3.2))
        total = row(words("Bütün kəsiklər toplanırsa:", size=CAPTION_SIZE, color=WHITE),
                    MathTex(r"I\cdot I", "=", "I^2", font_size=TEX_SIZE), buff=0.3)
        total.to_edge(DOWN, buff=0.45)
        self.say(total, run_time=0.7)
        self.wait(rt(2.3))

    # ═════════════════════════════════════════════════════════════════════════
    #  SƏHNƏ 5 — Dairəvi simmetriya       (≈12 san · kamera: VIEW3D → TOP → VIEW3D)
    # ═════════════════════════════════════════════════════════════════════════
    def scene_5_symmetry(self):
        self.play(FadeOut(self.cut_plane), FadeOut(self.cut_fill), FadeOut(self.cut_line),
                  self.fx(FadeOut(self.cut_formula)), *self.unsay(), run_time=rt(0.5))
        self.stop_ambient_camera_rotation()

        # yuxarıdan baxış; səth konsentrik zolaqlarla rənglənir
        plain = self.surface.copy()
        banded = paint_surface(self.surface.copy(), bands=True)
        self.move_camera(**TOP, run_time=rt(1.5),
                         added_anims=[FadeOut(self.curve), FadeOut(self.y_curve)])
        self.play(Transform(self.surface, banded), run_time=rt(0.8))

        # mərkəzdən nöqtəyə qədər məsafə r; düzbucaqlı üçbucaq
        px, py = 1.3, 0.8
        O, X, Q = P(0, 0), P(px, 0), P(px, py)
        r_line = Line(O, Q, color=WHITE, stroke_width=4)
        x_leg = Line(O, X, color=C_X, stroke_width=4)
        y_leg = Line(X, Q, color=C_Y, stroke_width=4)
        s = 0.16
        corner = VMobject(stroke_color=WHITE, stroke_width=2).set_points_as_corners(
            [X + s * LEFT, X + s * LEFT + s * UP, X + s * UP])
        dot = Dot(Q, radius=0.07, color=WHITE)
        VGroup(x_leg, y_leg, r_line, corner, dot).set_z_index(4)

        def at(point, offset):
            return self.to_screen(point) + offset

        normal = np.array([-py, px, 0]) / np.hypot(px, py)
        r_lab = MathTex("r", font_size=40).move_to(at((O + Q) / 2, 0.3 * normal))
        x_lab = MathTex("x", font_size=40, color=C_X).move_to(at((O + X) / 2, 0.3 * DOWN))
        y_lab = MathTex("y", font_size=40, color=C_Y).move_to(at((X + Q) / 2, 0.3 * RIGHT))
        self.fix(r_lab, x_lab, y_lab)

        self.play(Create(r_line), FadeIn(dot), self.fx(FadeIn(r_lab)), run_time=rt(0.8))
        self.play(Create(x_leg), Create(y_leg), Create(corner),
                  self.fx(FadeIn(x_lab)), self.fx(FadeIn(y_lab)), run_time=rt(0.8))

        pyth = MathTex("x^2+y^2", "=", "r^2", font_size=TEX_SIZE).move_to([4.9, 1.6, 0])
        pyth[0][0:2].set_color(C_X)
        pyth[0][3:5].set_color(C_Y)
        self.fix(pyth)
        self.play(self.fx(Write(pyth)), run_time=rt(0.8))

        height = MathTex("e^{-(", "x^2+y^2", ")}", "=", "e^{-", "r^2}", font_size=TEX_SIZE)
        height.move_to(pyth)
        height[1][0:2].set_color(C_X)
        height[1][3:5].set_color(C_Y)
        self.play(self.tmt(pyth, height, key_map={"r^2": "r^2}"}), run_time=rt(1.0))
        self.say("Səthin hündürlüyü yalnız r-dən asılıdır")
        self.wait(rt(0.4))

        # radiusu r olan bütün dairədə hündürlük eynidir
        ring = DashedVMobject(Circle(radius=np.hypot(px, py) * U, color=WHITE, stroke_width=3)
                              .rotate(np.arctan2(py, px)), num_dashes=48).set_z_index(4)
        legs = VGroup(x_leg, y_leg, corner)
        self.play(Create(ring), FadeOut(legs), self.fx(FadeOut(VGroup(x_lab, y_lab, r_lab))),
                  run_time=rt(0.9))
        self.play(Rotate(VGroup(r_line, dot), angle=TAU, about_point=ORIGIN), run_time=rt(1.2))
        self.wait(rt(0.6))

        # yenidən 3D
        self.play(FadeOut(r_line), FadeOut(dot), FadeOut(ring),
                  self.fx(FadeOut(height)), *self.unsay(),
                  Transform(self.surface, plain), run_time=rt(0.6))
        self.move_camera(**VIEW3D, run_time=rt(1.5),
                         added_anims=[FadeIn(self.curve), FadeIn(self.y_curve)])

    # ═════════════════════════════════════════════════════════════════════════
    #  SƏHNƏ 6 — Silindrik təbəqələr  ƏSAS AN  (≈20 san · kamera: VIEW3D ↔ sağa)
    # ═════════════════════════════════════════════════════════════════════════
    def scene_6_shells(self):
        r, dr = SHELL_R, SHELL_DR
        h = gauss(r)
        th = VIEW3D["theta"]
        side = np.array([-np.sin(th), np.cos(th), 0.0])     # ekranda sağa
        front = np.array([np.cos(th), np.sin(th), 0.0])     # kameraya doğru

        # səth solğunlaşır, altında qırmızı təbəqə yerdən qalxır
        shell = make_shell(r, dr, height=1e-3)
        self.play(self.surface.animate.set_fill(opacity=SURF_DIM).set_stroke(opacity=0.1),
                  run_time=rt(0.6))
        self.play(morph_shell(shell, r, dr, dict(height=1e-3), dict(height=h)), run_time=rt(1.0))

        # radius r, qalınlıq dr, hündürlük e^{-r²}
        p_r, p_out = r * U * side, (r + dr) * U * side
        r_line = Line(ORIGIN, p_r, color=WHITE, stroke_width=3).set_z_index(4)
        r_lab = self.fix(MathTex("r", font_size=36).move_to(self.to_screen(p_r / 2) + 0.28 * UP))
        dr_brace = self.sbrace(p_r, p_out, "dr", DOWN, buff=0.06, size=32)
        h_brace = self.sbrace(p_out, p_out + h * H * OUT, "e^{-r^2}", RIGHT, buff=0.1)
        self.play(Create(r_line), self.fx(FadeIn(r_lab)), run_time=rt(0.6))
        self.play(self.fx(GrowFromCenter(dr_brace)), run_time=rt(0.6))
        self.play(self.fx(GrowFromCenter(h_brace)), run_time=rt(0.6))
        self.wait(rt(1.2))
        self.play(FadeOut(r_line), self.fx(FadeOut(VGroup(r_lab, dr_brace, h_brace))),
                  run_time=rt(0.4))

        # təbəqə səthin altından çıxıb yan tərəfə uçur (kamera ardınca sürüşür)
        shift = SHELL_FLY * side
        start = shell.get_center()
        hop = ParametricFunction(lambda a: start + a * shift + 4 * a * (1 - a) * 1.4 * OUT,
                                 t_range=[0, 1])
        self.move_camera(frame_center=np.array(VIEW3D["frame_center"]) + SIDE_SHIFT * side,
                         zoom=SIDE_ZOOM, run_time=rt(1.3),
                         added_anims=[MoveAlongPath(shell, hop)])

        # əyilmiş divar düzlənir: silindr → lövhə
        self.play(unroll_shell(shell, r, dr, center=shift), run_time=rt(2.2))
        self.wait(rt(0.3))

        # lövhənin ölçüləri
        A = shift + r * U * front                         # lövhənin arxa üzünün ortası
        L, Dw, Hw = PI * r * U, dr * U, h * H
        bottom_left = A - L * side + Dw * front
        bottom_right = A + L * side + Dw * front
        top_right = bottom_right + Hw * OUT
        top_left = bottom_left + Hw * OUT

        len_lab = MathTex(r"2\pi r", font_size=38)
        len_brace = self.sbrace(bottom_left, bottom_right,
                                row(words("uzunluq"), len_lab, buff=0.15),
                                DOWN, buff=0.12)
        h_lab = MathTex("e^{-r^2}", font_size=38)
        h_brace = self.sbrace(bottom_right, top_right,
                              VGroup(words("hündürlük"), h_lab).arrange(DOWN, buff=0.1),
                              RIGHT, buff=0.12)
        dr_lab = MathTex("dr", font_size=38)
        thick = row(words("qalınlıq"), dr_lab, buff=0.15)
        tip = self.to_screen(top_left - 0.5 * Dw * front + 0.6 * U * side)
        thick.move_to(tip + 1.0 * UP + 0.3 * LEFT)
        thick_arrow = Arrow(thick.get_bottom(), tip, buff=0.08, stroke_width=3,
                            max_tip_length_to_length_ratio=0.25, color=WHITE)
        thick_group = self.fix(VGroup(thick, thick_arrow))

        self.play(self.fx(GrowFromCenter(len_brace)), run_time=rt(0.6))
        self.play(self.fx(GrowFromCenter(h_brace)), run_time=rt(0.6))
        self.play(self.fx(FadeIn(thick)), self.fx(GrowArrow(thick_arrow)), run_time=rt(0.6))

        # dV = 2πr · e^{-r²} · dr — ölçülər düstura uçur
        self.dV = MathTex("dV", "=", "2", r"\pi", "r", r"\cdot", "e^{-r^2}", r"\cdot", "dr",
                          font_size=TEX_SIZE).to_edge(UP, buff=0.45)
        self.dV[0].set_color(C_SHELL)
        self.fix(self.dV)
        self.play(self.fx(FadeIn(self.dV[0:2])), self.fx(FadeIn(self.dV[5])),
                  self.fx(FadeIn(self.dV[7])),
                  self.fx(TransformFromCopy(len_lab, VGroup(*self.dV[2:5]))),
                  self.fx(TransformFromCopy(h_lab, self.dV[6])),
                  self.fx(TransformFromCopy(dr_lab, self.dV[8])),
                  run_time=rt(1.2))
        self.add(self.dV)
        self.play(self.fx(Indicate(self.dV, color=WHITE, scale_factor=1.08)), run_time=rt(0.7))
        self.wait(rt(0.6))

        # lövhə gedir, kamera geri qayıdır
        self.play(FadeOut(shell), self.fx(FadeOut(VGroup(len_brace, h_brace, thick_group))),
                  run_time=rt(0.5))
        self.move_camera(**VIEW3D, run_time=rt(1.0))

        # 10 təbəqə mərkəzdən xaricə doğru bir-birinin içində yaranır
        step = R_MAX / N_SHELLS
        self.shells = VGroup()
        grow = []
        for k in range(N_SHELLS):
            rk = k * step
            style = dict(color=interpolate_color(RED, RED_E, k / N_SHELLS), inner=False,
                         res=24 + 4 * k)
            piece = make_shell(rk, step, height=1e-3, opacity=0, **style)
            self.shells.add(piece)
            grow.append(morph_shell(piece, rk, step,
                                    dict(height=1e-3, opacity=0.0),
                                    dict(height=gauss(rk), opacity=SHELL_OPACITY), **style))
        self.play(LaggedStart(*grow, lag_ratio=0.18), run_time=rt(2.2))
        self.say("Bütün təbəqələri toplayaq")
        self.wait(rt(2.0))

    # ═════════════════════════════════════════════════════════════════════════
    #  SƏHNƏ 7 — Hesablama                   (≈12 san · kamera: VIEW3D → FRONT)
    # ═════════════════════════════════════════════════════════════════════════
    def scene_7_compute(self):
        E1 = MathTex("I^2", "=", r"\int_0^{\infty}", "2", r"\pi", "r", "e^{-r^2}", r"\,dr",
                     font_size=BIG_TEX).move_to(0.8 * UP)

        # ekran təmizlənir, kamera 2D-yə qayıdır, dV → I² = ∫ 2πr e^{-r²} dr
        scene_3d = Group(self.surface, self.shells, self.x_axis, self.y_axis, self.z_axis,
                         self.curve, self.y_curve)
        self.move_camera(**FRONT, run_time=rt(1.2),
                         added_anims=[FadeOut(scene_3d), *self.unsay()])
        self.play(self.tmt(self.dV, E1, key_map={"dV": "I^2", "dr": r"\,dr"}), run_time=rt(1.0))

        # kiçik qeyd: (−e^{−r²})' = 2r e^{−r²}
        note = MathTex(r"\big(-e^{-r^2}\big)'", "=", r"2r\,e^{-r^2}", font_size=36, color=C_SOFT)
        note.next_to(E1, DOWN, buff=1.2).shift(0.8 * RIGHT)
        arrow = Arrow(note.get_top(), VGroup(*E1[3:7]).get_bottom(), buff=0.15,
                      stroke_width=3, color=C_SOFT, max_tip_length_to_length_ratio=0.2)
        self.fix(note, arrow)
        self.play(self.fx(FadeIn(note, shift=0.2 * UP)), self.fx(GrowArrow(arrow)),
                  run_time=rt(0.8))
        self.wait(rt(1.0))

        E2 = MathTex("I^2", "=", r"\pi", r"\Big[", "-e^{-r^2}", r"\Big]_0^{\infty}",
                     font_size=BIG_TEX).move_to(E1)
        self.play(self.tmt(E1, E2, key_map={"e^{-r^2}": "-e^{-r^2}",
                                            r"\int_0^{\infty}": r"\Big]_0^{\infty}"}),
                  self.fx(FadeOut(VGroup(note, arrow))), run_time=rt(1.1))
        self.wait(rt(0.7))

        E3 = MathTex("I^2", "=", r"\pi", r"\big(", "0", "-", "(-1)", r"\big)",
                     font_size=BIG_TEX).move_to(E1)
        self.play(self.tmt(E2, E3, key_map={r"\Big[": r"\big(", r"\Big]_0^{\infty}": r"\big)"}),
                  run_time=rt(1.0))
        self.wait(rt(0.7))

        E4 = MathTex("I^2", "=", r"\pi", font_size=BIG_TEX).move_to(E1)
        self.play(self.tmt(E3, E4), run_time=rt(0.9))

        frame = SurroundingRectangle(E4, buff=0.3, corner_radius=0.12, color=WHITE, stroke_width=3)
        halo = glow(frame, WHITE)
        self.fix(frame, halo)
        self.play(self.fx(Create(frame)), self.fx(FadeIn(halo, rate_func=there_and_back)),
                  run_time=rt(0.8))
        self.wait(rt(0.5))

        # kök işarəsi hər iki tərəfin üzərində böyüyür
        E5 = MathTex(r"\sqrt{I^2}", "=", r"\sqrt{\pi}", font_size=BIG_TEX).move_to(E1)
        self.fix(E5)
        roots = [E5[0][0], E5[0][1], E5[2][0], E5[2][1]]     # √ işarələri və üst xətləri
        self.play(self.fx(FadeOut(frame)),
                  self.fx(ReplacementTransform(E4[0][0], E5[0][2])),
                  self.fx(ReplacementTransform(E4[0][1], E5[0][3])),
                  self.fx(ReplacementTransform(E4[1], E5[1])),
                  self.fx(ReplacementTransform(E4[2][0], E5[2][2])),
                  *[self.fx(GrowFromEdge(m, LEFT)) for m in roots],
                  run_time=rt(1.0))
        self.add(E5)
        self.wait(rt(0.4))

        self.result = MathTex("I", "=", r"\sqrt{\pi}", font_size=BIG_TEX + 6).move_to(E1)
        self.result[2].set_color(C_RESULT)
        self.play(self.tmt(E5, self.result, key_map={r"\sqrt{I^2}": "I"}), run_time=rt(1.0))
        self.play(self.fx(Flash(self.result[2], color=C_RESULT, flash_radius=0.75,
                                line_length=0.3)), run_time=rt(0.7))
        self.wait(rt(0.9))

    # ═════════════════════════════════════════════════════════════════════════
    #  SƏHNƏ 8 — Nəticəni görmək                    (≈8 san · kamera: FRONT)
    # ═════════════════════════════════════════════════════════════════════════
    def scene_8_see_it(self):
        shift = 2.4 * LEFT
        x0 = 2.6                                       # düzbucaqlının sol kənarı (səhnə x)
        w, hgt = np.sqrt(PI) * U, 1.0 * H              # en √π, hündürlük 1

        axis = Line(P(-X_MAX) + shift, [x0 + w + 0.6, 0, 0], color=C_AXIS, stroke_width=1.5)
        curve = x_bell().shift(shift).set_z_index(2)
        area = x_area().shift(shift)
        self.play(self.result.animate.scale(0.75).to_edge(UP, buff=0.4),
                  FadeIn(axis), Create(curve), FadeIn(area), run_time=rt(1.0))

        bl, br = np.array([x0, 0, 0]), np.array([x0 + w, 0, 0])
        tr, tl = br + hgt * OUT, bl + hgt * OUT
        rect = Polygon(bl, br, tr, tl, stroke_color=C_RESULT, stroke_width=4,
                       fill_opacity=0).set_z_index(3)
        w_brace = self.sbrace(bl, br, r"\sqrt{\pi}", DOWN, color=C_RESULT, buff=0.12, size=40)
        h_brace = self.sbrace(br, tr, "1", RIGHT, buff=0.12, size=40)
        self.play(Create(rect), self.fx(GrowFromCenter(w_brace)), self.fx(GrowFromCenter(h_brace)),
                  run_time=rt(0.9))

        # sahə zolaqlara bölünür …
        n, a, b = 28, -2.8, 2.8
        xs = np.linspace(a, b, n + 1)
        strips = VGroup(*[strip_shape(xs[i], xs[i + 1]).shift(shift) for i in range(n)])
        self.play(FadeIn(strips), FadeOut(area), run_time=rt(0.4))

        # … və düzbucaqlının içinə axıb onu alt-alta doldurur (hər zolağın sahəsi qorunur)
        layers, level = [], 0.0
        for i in range(n):
            dz = (erf(xs[i + 1]) - erf(xs[i])) / 2          # sahə / √π  (riyazi vahid)
            layers.append(Polygon(bl + level * H * OUT, br + level * H * OUT,
                                  br + (level + dz) * H * OUT, bl + (level + dz) * H * OUT,
                                  fill_color=C_X, fill_opacity=0.6,
                                  stroke_color=BLACK, stroke_width=1))
            level += dz
        self.play(LaggedStart(*[Transform(s, l, path_arc=PI / 3, path_arc_axis=UP)
                                for s, l in zip(strips, layers)], lag_ratio=0.12),
                  run_time=rt(2.4))
        self.play(rect.animate(rate_func=there_and_back).set_stroke(width=10), run_time=rt(0.6))

        self.say(MathTex(r"\sqrt{\pi}", r"\approx", "1.7725", font_size=44)
                 .set_color_by_tex(r"\sqrt{\pi}", C_RESULT).to_edge(DOWN, buff=0.5))
        self.wait(rt(2.0))
        self.s8 = Group(axis, curve, strips, rect, w_brace, h_brace)

    # ═════════════════════════════════════════════════════════════════════════
    #  SƏHNƏ 9 — Final                               (≈4 san · kamera: FRONT)
    # ═════════════════════════════════════════════════════════════════════════
    def scene_9_final(self):
        final = MathTex(INT, "e^{-x^2}", r"\,dx", "=", r"\sqrt{\pi}", font_size=84)
        final[1].set_color(C_X)
        final[4].set_color(C_RESULT)
        box = RoundedRectangle(corner_radius=0.2, width=final.width + 1.0,
                               height=final.height + 0.8, stroke_color=C_RESULT, stroke_width=4)
        halo = glow(box, C_RESULT)
        self.fix(box, halo)

        self.play(FadeOut(self.s8), *self.unsay(),
                  self.tmt(self.result, final, key_map={"I": INT}), run_time=rt(0.9))
        self.play(self.fx(Create(box)), self.fx(FadeIn(halo)), run_time=rt(0.6))
        self.wait(rt(2.0))
        self.play(FadeOut(Group(*self.mobjects)), run_time=rt(1.0))
