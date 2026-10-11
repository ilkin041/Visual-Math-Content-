"""
Ekstremal prinsip: Silvester–Qallai teoremi, onun dualı və nəticələri
=====================================================================
3Blue1Brown üslubunda, səssiz seminar videosu (Manim Community Edition).

Hər hissə ayrıca Scene sinfidir və ayrıca render olunur:

    Hisse00_Giris        1. Giriş: məsələ və şərtlərin rolu
    Hisse01_Isinme       2. İsinmə: ekstremal prinsip
    Hisse02_Silvester    3. Silvester–Qallai teoremi (Kellinin isbatı)
    Hisse03_Dual         4. Dual məsələ: 20.14
    Hisse04_Neticeler    5. Nəticələr (de Breyn–Erdöş)
    Hisse05_Serhedler    6. Üsul harada işləmir?
    Hisse06_Yekun        7. Yekun
    Hisse07_Hell1        8.1. Dual de Breyn–Erdöş
    Hisse08_Hell2        8.2. Şərtlərin zəruriliyi
    Hisse09_Hell3        8.3. Fəzada Silvester–Qallai (ThreeDScene)
    Hisse10_Hell4        8.4. Çevrələr və inversiya

Render:
    ./render_preview.sh          # 480p15, tez yoxlama
    ./render_all.sh              # 1080p60 + ffmpeg concat -> tam_video.mp4
    manim -qh --fps 60 ekstremal_prinsip.py Hisse02_Silvester   # tək hissə

Tələblər: manim, XeLaTeX (texlive-xetex), CMU Serif şrifti (fonts-cmu), ffmpeg.

Faylın quruluşu:
    0. Şrift şablonu          4. Ümumi köməkçilər (mətn, qutular, başlıqlar)
    1. Rənglər, ölçülər        5. Həndəsə (numpy)
    2. Vaxtlar                 6. Kelli isbatı (Hisse02 və Hisse03 üçün ortaq)
    3. Konfiqurasiyalar        7. Səhnələr (Hisse00 ... Hisse10)
"""

from __future__ import annotations

import itertools
import re

import numpy as np
from manim import *

# ═════════════════════════════════════════════════════════════════════════════
#  0. ŞRİFT — XeLaTeX + Computer Modern Unicode (CMU Serif)
#     Bütün yazılar Tex/MathTex ilə; Text sinfi istifadə olunmur.
#     Düsturlar standart Computer Modern riyazi şriftində qalır (unicode-math yoxdur).
#     \textwidth genişdir: sətirlər yalnız \\ olan yerdə bölünür.
# ═════════════════════════════════════════════════════════════════════════════
AZ_TEMPLATE = TexTemplate(
    tex_compiler="xelatex",
    output_format=".xdv",
)
AZ_TEMPLATE.add_to_preamble(r"""
\usepackage{fontspec}
\setmainfont{CMU Serif}          % Computer Modern Unicode
\usepackage{amsmath,amssymb}
\usepackage{newunicodechar}
\setlength{\textwidth}{60cm}\setlength{\linewidth}{60cm}\setlength{\hsize}{60cm}
""")
config.tex_template = AZ_TEMPLATE
config.background_color = "#000000"

# ═════════════════════════════════════════════════════════════════════════════
#  1. RƏNGLƏR VƏ ÖLÇÜLƏR
# ═════════════════════════════════════════════════════════════════════════════
C_LINE = "#58C4DD"       # verilmiş xətlər (MAVİ)
C_POINT = "#FFFF00"      # verilmiş nöqtələr, kəsişmə nöqtələri (SARI)
C_ELL = "#FF862F"        # seçilmiş ℓ xətti (NARINCI)
C_MIN = "#FC6255"        # ən kiçik cüt: P və h (QIRMIZI); ziddiyyət
C_NEW = "#83C167"        # tapılan daha kiçik obyekt (YAŞIL); "doğru"
C_AUX = "#9A72AC"        # köməkçi üçbucaqlar (BƏNÖVŞƏYİ)
C_TEXT = "#FFFFFF"       # əsas mətn
C_TEXT2 = "#DDDDDD"      # açıq boz mətn
C_DIM = "#9A9A9A"        # künc başlığı, ox, köməkçi boz
C_RED_PT = "#FC6255"     # Məsələ 2: qırmızı nöqtələr
C_BLUE_PT = "#58C4DD"    # Məsələ 2: göy nöqtələr
C_SEG = "#FFFFFF"        # Məsələ 2: parçalar
C_RAY_L = "#FF862F"      # ℓ-in H-dan sol qapalı şüası
C_RAY_R = "#FFD39A"      # ℓ-in H-dan sağ qapalı şüası
FADED = 0.3              # fonda qalan xətlərin şəffaflığı

FS_TEXT = 40             # izah sətirləri
FS_NOTE = 32             # kiçik qeydlər
FS_FORMULA = 48          # düsturlar (44–52)
FS_FORMULA_S = 44
FS_TITLE = 64            # bölmə başlıqları
FS_CORNER = 28           # küncdəki kiçik başlıq
FS_LABEL = 38            # nöqtə etiketləri

DOT_R = 0.08             # nöqtə radiusu
LINE_W = 3               # xətt qalınlığı
SEG_W = 6                # vurğulanan parça qalınlığı

# ═════════════════════════════════════════════════════════════════════════════
#  2. VAXTLAR (saniyə)
# ═════════════════════════════════════════════════════════════════════════════
T_ANIM = 1.8             # adi animasiya
T_SLOW = 3.0             # mürəkkəb çevrilmə (TransformMatchingTex, fırlanma)
WAIT_STEP = 2.0          # hər isbat addımının sonunda "nəfəs"
WAIT_SECTION = 3.0       # hər bölmənin sonunda pauza


def read_wait(text) -> float:
    """Oxunma vaxtı: 1.5 + 0.35 × (sözlərin sayı). Düstur ($...$) uzunluğuna görə sayılır."""
    if isinstance(text, (list, tuple)):
        text = " ".join(text)
    maths = re.findall(r"\$[^$]*\$", text)
    plain = re.sub(r"\$[^$]*\$", " ", text)
    plain = re.sub(r"\\[A-Za-z]+", " ", plain)
    words = [w for w in re.split(r"[\s—–]+", plain) if re.search(r"\w", w)]
    math_words = 0
    for m in maths:
        core = re.sub(r"\\[A-Za-z]+", "x", m.strip("$"))
        core = re.sub(r"[{}\s]", "", core)
        math_words += max(1, round(len(core) / 5))
    return 1.5 + 0.35 * (len(words) + math_words)


# ═════════════════════════════════════════════════════════════════════════════
#  3. EKRAN SAHƏLƏRİ VƏ KONFİQURASİYALAR
# ═════════════════════════════════════════════════════════════════════════════
FW = config.frame_width            # ≈ 14.22
FH = config.frame_height           # 8
X_L, X_R = -FW / 2, FW / 2
CAPTION_TOP = -2.75                # izah sətrinin üst sərhədi: diaqram bundan yuxarıda qalır
TOP_BAND = 3.3                     # küncdəki başlıq zolağının alt sərhədi

# Xətlərin "ekran kənarı": (xmin, xmax, ymin, ymax)
BOX_FULL = (X_L, X_R, CAPTION_TOP, FH / 2)
BOX_DIAG = (X_L, 2.35, CAPTION_TOP, FH / 2)        # sağda düstur sütunu üçün yer
# Yuxarı sol küncdəki başlıq zonası: bu zonaya girən xətt onun altında dayanır
TITLE_ZONE = (X_L, -0.9, 2.95, FH / 2)
COL_X = 4.75                                        # düstur sütununun mərkəzi (x > 2.5)
COL_LEFT = 2.65

# --- KANONİK DİAQRAM 1/2 (riyazi koordinatlar; ekrana K_SCALE, K_SHIFT ilə köçürülür)
CANON = {
    "P": (-3.0, 1.5),
    "H": (-3.0, -2.0),
    "A": (-1.5, -2.0),
    "B": (1.5, -2.0),
    "C": (-5.5, -2.0),
}
K_SCALE = 0.85
K_SHIFT = (-0.9, 0.7)

# --- Hisse02: 7 nöqtəlik sxematik konfiqurasiya (ümumi vəziyyətdə)
SCHEMA_POINTS = [
    (-0.75, 1.68), (-2.84, 2.18), (-5.29, 1.22), (-5.77, -0.58),
    (-4.10, -1.46), (-0.73, -1.81), (0.35, -0.20),
]
# --- Hisse03: 6 xəttlik sxematik konfiqurasiya: (xəttin bir nöqtəsi, bucaq dərəcə ilə)
SCHEMA_LINES = [
    ((-2.350, 0.761), 5.3), ((-1.983, -0.462), 24.8), ((-2.607, 0.525), 45.6),
    ((-3.356, 0.512), 74.8), ((-1.681, 0.704), 127.8), ((-2.533, -0.228), 152.8),
]

# --- Hisse01, Məsələ 1: 8 nöqtə (iki nöqtənin x-i eyni və ən kiçikdir)
MID_POINTS = [
    (-4.5, -0.5), (-4.5, 1.0), (-3.0, 2.0), (-2.0, -1.5),
    (-1.0, 0.5), (0.0, 2.5), (1.0, -1.0), (1.8, 1.2),
]
# --- Hisse01, Məsələ 2: 4 qırmızı, 4 göy nöqtə (heç üçü bir xətt üzərində deyil)
MATCH_RED = [(-4.7, 2.1), (-1.3, 1.9), (-4.7, -0.3), (-0.6, -1.8)]
MATCH_BLUE = [(0.3, 1.4), (-2.6, -0.4), (-5.3, -1.5), (-2.7, -2.0)]


# ═════════════════════════════════════════════════════════════════════════════
#  4. ÜMUMİ KÖMƏKÇİLƏR — mətn, qutular, başlıqlar
# ═════════════════════════════════════════════════════════════════════════════
def az_tex(s, size=FS_TEXT, color=C_TEXT, **kw) -> Tex:
    """AZ_TEMPLATE ilə Tex (Computer Modern serif)."""
    return Tex(s, font_size=size, color=color, tex_template=AZ_TEMPLATE, **kw)


def az_texp(*parts, size=FS_TEXT, color=C_TEXT, **kw) -> Tex:
    """Hissələrə bölünmüş Tex (TransformMatchingTex üçün)."""
    return Tex(*parts, font_size=size, color=color, tex_template=AZ_TEMPLATE, **kw)


def az_math(*parts, size=FS_FORMULA, color=C_TEXT, **kw) -> MathTex:
    return MathTex(*parts, font_size=size, color=color, tex_template=AZ_TEMPLATE, **kw)


def para(lines, size=FS_NOTE, color=C_TEXT, buff=0.16, align=LEFT) -> VGroup:
    """Bir neçə sətirlik, sola düzlənmiş mətn bloku."""
    g = VGroup(*[az_tex(s, size=size, color=color) for s in lines])
    g.arrange(DOWN, aligned_edge=align, buff=buff)
    return g


def check_mark(size=48, color=C_NEW):
    return az_math(r"\checkmark", size=size, color=color)


def cross_mark(size=48, color=C_MIN):
    return az_math(r"\times", size=size, color=color)


def qed_mark(size=40, color=C_TEXT):
    return az_math(r"\blacksquare", size=size, color=color)


class TMT(TransformMatchingTex):
    """TransformMatchingTex; açar müqayisəsində { } və boşluqlar nəzərə alınmır,
    məsələn "AB" ilə "{AB" (kəsrin surəti) eyni hədd sayılır və yerinə uçur.
    Hədəfdə yeni hədd yoxdursa, artıq hədlər ekranın mərkəzinə uçmadan yerində sönür."""

    def __init__(self, mobject, target_mobject, **kwargs):
        super().__init__(mobject, target_mobject, **kwargs)
        for anim in self.animations:
            if isinstance(anim, FadeOut) and getattr(anim, "point_target", False):
                if np.allclose(anim.mobject.get_center() + anim.shift_vector, ORIGIN):
                    anim.shift_vector = ORIGIN

    @staticmethod
    def get_mobject_key(mobject) -> str:
        return re.sub(r"[{}\s]", "", mobject.tex_string)


def tmt(scene, src, tgt, run_time=T_SLOW, **kw):
    """Cəbri addım: hədlər yeni yerlərinə uçur. src bir MathTex və ya VGroup ola bilər."""
    scene.play(TMT(src, tgt, **kw), run_time=run_time)
    scene.remove(src)
    scene.add(tgt)
    return tgt


def fitw(mob, w=4.3):
    """Düsturu sağ sütunun enindən (≈4.3) geniş olmasın deyə kiçildir."""
    if mob.width > w:
        mob.scale_to_fit_width(w)
    return mob


class AZScene(Scene):
    """Bütün 2D hissələrin əsası. remove() obyektin bütün ailəsini çıxarır, belə ki
    FadeOut(VGroup(a, b)) a və b-ni həqiqətən ekrandan götürür (Manim-də qrup səhnədə
    deyilsə, üzvləri qalır və FadeOut-dan sonra yenidən görünür)."""

    def remove(self, *mobjects):
        fam = []
        for m in mobjects:
            fam.extend(m.get_family())
        return super().remove(*fam)


class AZ3DScene(ThreeDScene):
    """ThreeDScene üçün eyni remove() davranışı."""

    def remove(self, *mobjects):
        fam = []
        for m in mobjects:
            fam.extend(m.get_family())
        return super().remove(*fam)


def _fix(scene, *mobs):
    """3D səhnədə yazılar kadra bərkidilir (add_fixed_in_frame_mobjects)."""
    if isinstance(scene, ThreeDScene):
        scene.add_fixed_in_frame_mobjects(*mobs)


def caption(scene, text, size=FS_TEXT, color=C_TEXT, wait=None, extra=0.0):
    """Aşağıdakı izah sətri: köhnəsi sönür, yenisi yazılır, read_wait qədər gözlənilir."""
    new = az_tex(text, size=size, color=color)
    if new.width > FW - 0.8:
        new.scale_to_fit_width(FW - 0.8)
    new.to_edge(DOWN, buff=0.5)
    _fix(scene, new)
    old = getattr(scene, "_caption", None)
    if old is not None:
        scene.play(
            LaggedStart(FadeOut(old, shift=0.2 * DOWN), Write(new), lag_ratio=0.4),
            run_time=T_ANIM,
        )
    else:
        scene.play(Write(new), run_time=T_ANIM)
    scene._caption = new
    scene.wait((read_wait(text) if wait is None else wait) + extra)
    return new


def clear_caption(scene):
    old = getattr(scene, "_caption", None)
    if old is not None:
        scene.play(FadeOut(old, shift=0.2 * DOWN), run_time=T_ANIM)
        scene._caption = None


def section_title(scene, text):
    """Bölmə başlıq kartı: ortada 2.5 san, sonra yuxarı sol küncə kiçilir (28, boz)."""
    t = az_tex(text, size=FS_TITLE)
    if t.width > FW - 1.0:
        t.scale_to_fit_width(FW - 1.0)
    _fix(scene, t)
    scene.play(Write(t), run_time=T_ANIM)
    scene.wait(2.5)
    target = az_tex(text, size=FS_CORNER, color=C_DIM).to_corner(UL, buff=0.3)
    scene.play(Transform(t, target), run_time=T_ANIM)
    scene._section = t
    scene._caption = getattr(scene, "_caption", None)
    return t


def end_section(scene, pause=WAIT_SECTION):
    """Bölmənin sonu: 3 san pauza (seminarda dayandırmaq üçün), sonra hər şey sönür."""
    scene.wait(pause)
    mobs = [m for m in scene.mobjects]
    if mobs:
        scene.play(*[FadeOut(m) for m in mobs], run_time=T_ANIM)
    scene._caption = None
    scene.wait(0.5)


def fade_all_but(scene, keep=(), run_time=T_ANIM):
    """Başlıq və izah sətri istisna olmaqla hər şeyi söndürür."""
    keep = set(keep) | {getattr(scene, "_section", None), getattr(scene, "_caption", None)}
    mobs = [m for m in scene.mobjects if m not in keep]
    if mobs:
        scene.play(*[FadeOut(m) for m in mobs], run_time=run_time)


BOX_KINDS = {
    "masala": ("Məsələ", C_LINE),
    "teorem": ("Teorem", C_LINE),
    "fikir": ("Əsas fikir", C_NEW),
    "qeyd": ("Müəllim üçün qeyd", C_ELL),
}


def problem_box(text_lines, kind="masala", size=36, width=None, header=None):
    """'Məsələ' (mavi), 'Əsas fikir' (yaşıl), 'Müəllim üçün qeyd' (narıncı) qutuları."""
    name, color = BOX_KINDS[kind]
    head = az_tex(r"\textbf{" + (header or name) + "}", size=size, color=color)
    body = para(text_lines, size=size, color=C_TEXT, buff=0.22)
    content = VGroup(head, body).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
    if width is not None and content.width > width:
        content.scale_to_fit_width(width)
    rect = SurroundingRectangle(content, buff=0.35, corner_radius=0.15,
                                color=color, stroke_width=3)
    box = VGroup(rect, head, body)
    box.rect, box.head, box.body, box.lines = rect, head, body, list(text_lines)
    return box


def show_box(scene, box, line_by_line=True, extra=0.0):
    """Qutunu göstərir; sətirlər bir-bir yazılır və hər biri read_wait qədər qalır."""
    _fix(scene, box)
    scene.play(Create(box.rect), Write(box.head), run_time=T_ANIM)
    if line_by_line:
        for mob, txt in zip(box.body, box.lines):
            scene.play(Write(mob), run_time=T_ANIM)
            scene.wait(read_wait(txt))
    else:
        scene.play(Write(box.body), run_time=T_ANIM)
        scene.wait(read_wait(box.lines))
    if extra > 0:
        scene.wait(extra)


def red_frame_flash(scene):
    """Ziddiyyət anı: ekran kənarında qısa qırmızı çərçivə."""
    fr = Rectangle(width=FW - 0.12, height=FH - 0.12, stroke_color=C_MIN, stroke_width=16)
    _fix(scene, fr)
    scene.play(FadeIn(fr, rate_func=there_and_back), run_time=1.5)
    scene.remove(fr)


def step_label(scene, k, mode="points"):
    """'Addım k' etiketi: nöqtələr isbatında yuxarı solda, dual isbatda yuxarı sağda."""
    if mode == "points":
        lab = az_tex(f"Addım {k}", size=FS_CORNER, color=C_TEXT2)
        anchor = getattr(scene, "_section", None)
        if anchor is not None:
            lab.next_to(anchor, DOWN, aligned_edge=LEFT, buff=0.15)
        else:
            lab.to_corner(UL, buff=0.3)
    else:
        lab = az_tex(f"Addım {k}" + r" \;$\cdot$\; dual", size=FS_CORNER, color=C_TEXT2)
        lab.to_corner(UR, buff=0.3)
    old = getattr(scene, "_step", None)
    if old is None:
        scene.play(FadeIn(lab), run_time=1.5)
    else:
        scene.play(FadeOut(old), FadeIn(lab), run_time=1.5)
    scene._step = lab
    return lab


def counter(label, value=0, size=FS_TEXT, color=C_TEXT):
    """Sayğac: Tex etiketi + Integer. Qaytarır: (qrup, Integer)."""
    lab = az_tex(label, size=size, color=color)
    num = Integer(value, font_size=size, color=color)
    grp = VGroup(lab, num).arrange(RIGHT, buff=0.2)
    num.add_updater(lambda m: m.next_to(lab, RIGHT, buff=0.2))
    return grp, num


# ═════════════════════════════════════════════════════════════════════════════
#  5. HƏNDƏSƏ (numpy) — kəsişmə, perpendikulyar, məsafə, inversiya
# ═════════════════════════════════════════════════════════════════════════════
def P2(x, y=None):
    if y is None:
        x, y = x
    return np.array([float(x), float(y), 0.0])


def unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-12 else v


def dir_deg(deg):
    a = np.radians(deg)
    return np.array([np.cos(a), np.sin(a), 0.0])


def intersect(p1, q1, p2, q2):
    """p1q1 və p2q2 xətlərinin kəsişmə nöqtəsi."""
    d1, d2 = q1 - p1, q2 - p2
    m = np.array([[d1[0], -d2[0]], [d1[1], -d2[1]]])
    t, _ = np.linalg.solve(m, (p2 - p1)[:2])
    return p1 + t * d1


def foot_of_perpendicular(x, p, q):
    """x nöqtəsindən pq xəttinə perpendikulyarın oturacağı."""
    d = q - p
    t = np.dot(x - p, d) / np.dot(d, d)
    return p + t * d


def dist_point_line(x, p, q) -> float:
    return float(np.linalg.norm(x - foot_of_perpendicular(x, p, q)))


def clip_line(p, q, box):
    """pq düz xəttinin box = (xmin, xmax, ymin, ymax) daxilindəki hissəsi."""
    xmin, xmax, ymin, ymax = box
    d = q - p
    tmin, tmax = -1e9, 1e9
    for i, lo, hi in ((0, xmin, xmax), (1, ymin, ymax)):
        if abs(d[i]) < 1e-12:
            if p[i] < lo or p[i] > hi:
                return None
            continue
        t1, t2 = (lo - p[i]) / d[i], (hi - p[i]) / d[i]
        tmin, tmax = max(tmin, min(t1, t2)), min(tmax, max(t1, t2))
    if tmin >= tmax:
        return None
    return p + tmin * d, p + tmax * d


def _avoid_zone(a, b, zone):
    """Parçanın zona (künc başlığı) daxilinə düşən ucunu zonanın alt sərhədində kəsir."""
    zx0, zx1, zy0, zy1 = zone
    if max(a[1], b[1]) <= zy0 or abs(a[1] - b[1]) < 1e-9:
        return a, b
    top, low = (a, b) if a[1] > b[1] else (b, a)
    t = (zy0 - low[1]) / (top[1] - low[1])
    c = low + max(t, 0.0) * (top - low)
    if max(c[0], top[0]) >= zx0 and min(c[0], top[0]) <= zx1:
        return low, c
    return a, b


def full_line(p, q, box=BOX_FULL, color=C_LINE, width=LINE_W, avoid=TITLE_ZONE,
              **kw) -> Line:
    """p və q-dan keçən düz xətt, ekran (box) kənarına qədər uzanır;
    künc başlığının zonasına girmir."""
    a, b = clip_line(p, q, box)
    if avoid is not None:
        a, b = _avoid_zone(a, b, avoid)
    return Line(a, b, color=color, stroke_width=width, **kw)


def line_through(p, deg, box=BOX_FULL, **kw) -> Line:
    return full_line(p, p + dir_deg(deg), box=box, **kw)


def in_box(x, box, margin=0.0) -> bool:
    xmin, xmax, ymin, ymax = box
    return xmin + margin <= x[0] <= xmax - margin and ymin + margin <= x[1] <= ymax - margin


def right_angle(foot, along, toward, size=0.2, color=C_TEXT, width=2.5) -> RightAngle:
    """foot nöqtəsində düz bucaq işarəsi: 'along' xətt istiqaməti, 'toward' perpendikulyar."""
    u, v = unit(along), unit(toward)
    return RightAngle(Line(foot, foot + u), Line(foot, foot + v), length=size,
                      quadrant=(1, 1), color=color, stroke_width=width)


def perp_marker(x, p, q, color=C_MIN, size=0.2, side=None, width=3) -> VGroup:
    """x-dən pq xəttinə qırıq perpendikulyar + RightAngle."""
    f = foot_of_perpendicular(x, p, q)
    along = unit(q - p) if side is None else unit(side)
    dash = DashedLine(x, f, color=color, stroke_width=width, dash_length=0.12)
    grp = VGroup(dash)
    if np.linalg.norm(x - f) > 0.25:
        grp.add(right_angle(f, along, x - f, size=size, color=color))
    grp.foot = f
    return grp


def free_spot(x, lines, r=0.36, avoid_pts=()):
    """x nöqtəsinin yanında xətlərdən (p, d) ən uzaq yer — işarəni xəttin üstünə salmamaq üçün."""
    best, best_d = x + r * unit(UR), -1.0
    for ang in range(0, 360, 10):
        c = x + r * dir_deg(ang)
        dmin = min(dist_point_line(c, p, p + d) for p, d in lines)
        for y in avoid_pts:
            dmin = min(dmin, np.linalg.norm(c - y) - 0.15)
        if dmin > best_d + 1e-9:
            best, best_d = c, dmin
    return best


def clipped_circle(center, r, box=BOX_FULL, avoid=TITLE_ZONE, color=C_AUX, width=4,
                   n=2400) -> VMobject:
    """Çevrənin box daxilindəki (və başlıq zonasından kənar) qövsləri — numpy nümunələri.
    Tək VMobject qaytarır (qövslər ayrı alt yollardır), always_redraw üçün təhlükəsizdir."""
    vm = VMobject(color=color, stroke_width=width)
    a = np.linspace(0, TAU, n, endpoint=False)
    pts = center + r * np.column_stack([np.cos(a), np.sin(a), np.zeros(n)])
    ok = np.array([in_box(p, box) and not (avoid is not None and in_box(p, avoid))
                   for p in pts])
    if ok.all():
        return Circle(radius=r, color=color, stroke_width=width).move_to(center)
    start = int(np.argmin(ok))           # dövrü "kənar" nöqtədən başla
    order = np.roll(np.arange(n), -start)
    run, first = [], True
    for i in list(order) + [order[0]]:
        if ok[i]:
            run.append(pts[i])
            continue
        if len(run) >= 2:
            sub = VMobject().set_points_smoothly(run)
            if first:
                vm.set_points(sub.points)
                first = False
            else:
                vm.append_points(sub.points)
        run = []
    if first:
        vm.set_points(np.array([center] * 4))
    return vm


def make_dot(p, color=C_POINT, r=DOT_R, **kw) -> Dot:
    return Dot(p, radius=r, color=color, **kw)


def make_label(tex, p, direction=UR, color=C_TEXT, size=FS_LABEL, buff=0.12):
    return az_math(tex, size=size, color=color).next_to(p, direction, buff=buff)


def invert(x, O, r=1.0):
    """O mərkəzli, r radiuslu çevrəyə görə inversiya: OX · OX' = r²."""
    v = x - O
    return O + (r * r) * v / np.dot(v, v)


def segments_cross(a, b, c, d) -> bool:
    def orient(p, q, r):
        return np.sign((q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0]))
    return orient(a, b, c) != orient(a, b, d) and orient(c, d, a) != orient(c, d, b)


def no_three_collinear(points, tol=0.2) -> bool:
    pts = [np.asarray(p, dtype=float) for p in points]
    for i, j in itertools.combinations(range(len(pts)), 2):
        for k in range(len(pts)):
            if k in (i, j):
                continue
            if dist_point_line(pts[k], pts[i], pts[j]) < tol:
                return False
    return True


def connecting_lines(points, tol=1e-6):
    """Nöqtələr çoxluğunun bütün (fərqli) birləşdirici xətləri:
    [(i, j, üzərindəki nöqtələrin indeksləri)] — numpy ilə."""
    out, seen = [], set()
    for i, j in itertools.combinations(range(len(points)), 2):
        on = frozenset(k for k in range(len(points))
                       if dist_point_line(points[k], points[i], points[j]) < tol)
        if on in seen:
            continue
        seen.add(on)
        out.append((i, j, on))
    return out


def distance_number_line(values, length=4.2, x_max=None, step=None, font=22):
    """Məsafələr ədəd oxu (nazik, boz)."""
    if x_max is None:
        x_max = float(np.ceil(max(values) + 0.2))
    if step is None:
        step = 1 if x_max <= 6 else 2
    axis = NumberLine(x_range=[0, x_max, step], length=length, color=C_DIM,
                      stroke_width=2, include_numbers=True, font_size=font,
                      tick_size=0.06, include_tip=False)
    return axis


def show_pair(scene, point, line_pts, value, axis, line_box, store, color=C_LINE,
              num_pos=None):
    """'Cütü göstər': nöqtə yanır, birləşdirici xətt işıqlanır, qırıq perpendikulyar,
    yanında məsafə (DecimalNumber), sonra məsafə ədəd oxuna nöqtə kimi düşür (≈2.5 san)."""
    p, q = line_pts
    ln = full_line(p, q, box=line_box, color=color, width=4)
    perp = perp_marker(point, p, q, color=C_TEXT2, size=0.16, width=2.5)
    mid = (point + perp.foot) / 2
    num = DecimalNumber(value, num_decimal_places=2, font_size=30, color=C_TEXT)
    offs = unit(np.cross(unit(perp.foot - point), OUT))
    if num_pos is not None:
        num.move_to(num_pos)
    else:
        num.move_to(mid + 0.45 * offs)
    ring = Circle(radius=0.16, color=C_POINT, stroke_width=3).move_to(point)
    scene.play(Create(ln), Create(perp), FadeIn(ring, scale=1.6), FadeIn(num), run_time=1.3)
    d = make_dot(axis.n2p(value), color=C_POINT, r=0.05)
    scene.play(TransformFromCopy(num, d), FadeOut(VGroup(ln, perp, ring, num)), run_time=1.2)
    store.add(d)
    return d


# ═════════════════════════════════════════════════════════════════════════════
#  6. KELLİ İSBATI — Hisse02 (mode="points") və Hisse03 (mode="lines") üçün ortaq
#     Addım 0–8 eyni kodla gedir; yalnız Addım 3 (və mətnlər) fərqlidir.
# ═════════════════════════════════════════════════════════════════════════════
def to_canon(xy, scale=K_SCALE, shift=K_SHIFT):
    """Kanonik diaqramın riyazi koordinatlarını ekrana köçürür."""
    x, y = xy
    return P2(scale * x + shift[0], scale * y + shift[1])


def canon_points(scale=K_SCALE, shift=K_SHIFT):
    return {k: to_canon(v, scale, shift) for k, v in CANON.items()}


def canon_static(mode, scale, shift, box, with_hprime=True, label_size=30):
    """Kanonik diaqramın statik şəkli (müqayisə panelləri üçün)."""
    K = canon_points(scale, shift)
    P, H, A, B, C = (K[k] for k in "PHABC")
    g = VGroup()
    g.add(full_line(H, B, box=box, color=C_ELL, width=3, avoid=None))
    if mode == "lines":
        for X in (A, B, C):
            g.add(full_line(P, X, box=box, color=C_LINE, width=2.5, avoid=None))
    else:
        g.add(full_line(P, B, box=box, color=C_LINE, width=2.5, avoid=None))
    g.add(Polygon(P, A, B, stroke_width=0, fill_color=C_AUX, fill_opacity=0.3))
    g.add(DashedLine(P, H, color=C_MIN, stroke_width=3, dash_length=0.08))
    if with_hprime:
        F = foot_of_perpendicular(A, P, B)
        g.add(DashedLine(A, F, color=C_NEW, stroke_width=3, dash_length=0.08))
    for X, col in ((P, C_MIN), (A, C_POINT), (B, C_POINT), (C, C_POINT)):
        g.add(make_dot(X, color=col, r=0.06))
    for t, X, d in (("P", P, RIGHT + 0.3 * UP), ("A", A, DOWN), ("B", B, DOWN), ("C", C, DOWN),
                    ("h", (P + H) / 2, LEFT)):
        g.add(make_label(t, X, d, size=label_size, buff=0.08,
                         color=C_MIN if t == "h" else C_TEXT))
    return g


class KellyProof:
    """Kellinin isbatı. Addım 0–1 sxematik konfiqurasiya, 2–8 kanonik diaqram."""

    def __init__(self, scene, mode="points"):
        self.s = scene
        self.mode = mode
        self.pts_mode = (mode == "points")
        self.box = BOX_DIAG
        self.K = canon_points()
        self.col = []          # sağ sütundakı obyektlər

    # ── köməkçilər ───────────────────────────────────────────────────────────
    def label(self, k):
        step_label(self.s, k, self.mode)

    def col_clear(self, keep=()):
        out = [m for m in self.col if m not in keep]
        if out:
            self.s.play(*[FadeOut(m) for m in out], run_time=T_ANIM)
        self.col = [m for m in self.col if m in keep]

    def col_add(self, mob, anim=Write):
        self.s.play(anim(mob), run_time=T_ANIM)
        self.col.append(mob)
        return mob

    def breathe(self):
        self.s.wait(WAIT_STEP)

    def run(self):
        self.step0()
        self.step1()
        self.step2()
        self.step3()
        self.step4()
        self.step5()
        self.step6()
        self.step7()
        self.step8()
        old = getattr(self.s, "_step", None)
        if old is not None:
            self.s.play(FadeOut(old), run_time=1.5)
            self.s._step = None

    # ── Addım 0: sxematik konfiqurasiya ─────────────────────────────────────
    def step0(self):
        s = self.s
        self.label(0)
        if self.pts_mode:
            caption(s, "Fərz edək ki, nöqtələr bir xətt üzərində deyil")
            self.pts = [P2(*p) for p in SCHEMA_POINTS]
            self.schema = VGroup(*[make_dot(p) for p in self.pts])
            s.play(LaggedStart(*[GrowFromCenter(d) for d in self.schema], lag_ratio=0.15),
                   run_time=T_ANIM)
            # cütlər: (nöqtə, xəttin iki nöqtəsi, məsafə, nöqtə indeksi, xətt açarı)
            self.pairs = []
            for i, j in itertools.combinations(range(len(self.pts)), 2):
                for k in range(len(self.pts)):
                    if k in (i, j):
                        continue
                    d = dist_point_line(self.pts[k], self.pts[i], self.pts[j])
                    self.pairs.append((self.pts[k], (self.pts[i], self.pts[j]), d, k, (i, j)))
        else:
            caption(s, "Fərz edək ki, xətlər bir nöqtədən keçmir")
            self.lines = [(P2(*p), dir_deg(a)) for p, a in SCHEMA_LINES]
            self.schema = VGroup(*[full_line(p, p + d, box=self.box) for p, d in self.lines])
            self.ipts = []
            for i, j in itertools.combinations(range(len(self.lines)), 2):
                (p1, d1), (p2, d2) = self.lines[i], self.lines[j]
                self.ipts.append((intersect(p1, p1 + d1, p2, p2 + d2), i, j))
            self.idots = VGroup(*[make_dot(x, r=0.065) for x, _, _ in self.ipts])
            s.play(LaggedStart(*[Create(m) for m in self.schema], lag_ratio=0.15),
                   run_time=T_ANIM)
            s.play(LaggedStart(*[GrowFromCenter(d) for d in self.idots], lag_ratio=0.05),
                   run_time=T_ANIM)
            self.pairs = []
            for n, (x, i, j) in enumerate(self.ipts):
                for k in range(len(self.lines)):
                    if k in (i, j):
                        continue
                    p, d = self.lines[k]
                    self.pairs.append((x, (p, p + d), dist_point_line(x, p, p + d), n, k))
        self.breathe()

    # ── Addım 1: cütlər və məsafələr ─────────────────────────────────────────
    def step1(self):
        s = self.s
        self.label(1)
        if self.pts_mode:
            caption(s, "Cüt: nöqtə + ondan keçməyən birləşdirici xətt")
        else:
            caption(s, "Cüt: kəsişmə nöqtəsi + ondan keçməyən verilmiş xətt")
        vals = [pr[2] for pr in self.pairs]
        self.axis = distance_number_line(vals, length=4.2)
        self.axis.move_to(P2(COL_X, 2.65))
        self.axis_lab = az_tex("məsafələr", size=26, color=C_DIM).next_to(self.axis, UP, 0.15)
        s.play(Create(self.axis), FadeIn(self.axis_lab), run_time=T_ANIM)
        self.axis_dots = VGroup()
        order = np.argsort(vals)
        self.imin = int(order[0])
        # nümayiş üçün 6 müxtəlif cüt (perpendikulyarın oturacağı ekranda olsun)
        demo, used = [], set()
        for q in (0.12, 0.3, 0.45, 0.6, 0.75, 0.9, 0.2, 0.52, 0.68, 0.38):
            for idx in order[int(q * len(order)):]:
                idx = int(idx)
                x, (p, qq), d, a, b = self.pairs[idx]
                f = foot_of_perpendicular(x, p, qq)
                if idx == self.imin or (a, b) in used or not in_box(f, self.box, 0.5):
                    continue
                if any(self.pairs[o][3] == a for o in demo):
                    continue
                demo.append(idx)
                used.add((a, b))
                break
            if len(demo) == 6:
                break
        dots_map = {}
        for idx in demo:
            x, lp, d, _, _ = self.pairs[idx]
            dots_map[idx] = show_pair(s, x, lp, d, self.axis, self.box, self.axis_dots)
        rest = [i for i in range(len(self.pairs)) if i not in dots_map]
        rest_dots = VGroup(*[make_dot(self.axis.n2p(self.pairs[i][2]), r=0.05) for i in rest])
        s.play(LaggedStart(*[FadeIn(d, scale=2) for d in rest_dots], lag_ratio=0.01),
               run_time=T_ANIM)
        self.axis_dots.add(*rest_dots)
        allmap = dict(dots_map)
        for i, dmob in zip(rest, rest_dots):
            allmap[i] = dmob
        self.min_dot = allmap[self.imin]

        # "Belə cütlər var"
        caption(s, "Belə cütlər var")
        if self.pts_mode:
            i, j, k = 0, 3, 5
            a, b, c = self.pts[i], self.pts[j], self.pts[k]
            ln = full_line(a, b, box=self.box, width=4)
            s.play(Indicate(self.schema[i], color=C_TEXT, scale_factor=1.8),
                   Indicate(self.schema[j], color=C_TEXT, scale_factor=1.8), run_time=T_ANIM)
            s.play(Create(ln), run_time=T_ANIM)
            perp = perp_marker(c, a, b, color=C_TEXT2, size=0.16, width=2.5)
            s.play(Flash(c, color=C_POINT, flash_radius=0.25), Create(perp), run_time=T_ANIM)
            caption(s, "Nöqtələr bir xətt üzərində deyil — xəttdən kənar nöqtə var")
            s.play(FadeOut(ln), FadeOut(perp), run_time=T_ANIM)
        else:
            x, i, j = self.ipts[0]
            k = [t for t in range(len(self.lines)) if t not in (i, j)][0]
            hi = VGroup(self.schema[i].copy().set_stroke(width=6),
                        self.schema[j].copy().set_stroke(width=6))
            s.play(Create(hi), run_time=T_ANIM)
            s.play(Flash(x, color=C_POINT, flash_radius=0.3), run_time=T_ANIM)
            caption(s, "İki xətt kəsişir: onlar paralel deyil")
            hk = self.schema[k].copy().set_stroke(width=6, color=C_TEXT)
            s.play(Create(hk), run_time=T_ANIM)
            caption(s, "Xətlər bir nöqtədən keçmir — bu nöqtədən keçməyən xətt var")
            s.play(FadeOut(hi), FadeOut(hk), run_time=T_ANIM)
        caption(s, "Belə cütlər sonludur")
        self.breathe()

    # ── Addım 2: ən kiçik məsafə və kanonik diaqram ─────────────────────────
    def step2(self):
        s, K = self.s, self.K
        self.label(2)
        caption(s, "Ən kiçik məsafəli cütü seçək")
        s.play(self.min_dot.animate.set_color(C_MIN).scale(1.6), run_time=1.5)
        s.play(Circumscribe(self.min_dot, shape=Circle, color=C_MIN, buff=0.1), run_time=T_ANIM)
        self.min_lab = make_label("h", self.min_dot.get_center(), UR, color=C_MIN, size=30,
                                  buff=0.08)
        s.play(FadeIn(self.min_lab), run_time=1.5)
        x0, (p, q), d, a, b = self.pairs[self.imin]
        ell0 = full_line(p, q, box=self.box, color=C_ELL, width=4)
        perp0 = perp_marker(x0, p, q, color=C_MIN, size=0.15)
        pdot0 = make_dot(x0, color=C_MIN, r=0.1)
        plab0 = make_label("P", x0, -unit(perp0.foot - x0) + 0.3 * UP, size=36)
        hlab0 = make_label("h", (x0 + perp0.foot) / 2, unit(np.cross(perp0.foot - x0, OUT)),
                           color=C_MIN, size=36, buff=0.12)
        elab0 = make_label(r"\ell", ell0.get_end(), UL, color=C_ELL, size=38)
        s.play(Create(ell0), FadeIn(elab0), run_time=T_ANIM)
        s.play(GrowFromCenter(pdot0), FadeIn(plab0), run_time=T_ANIM)
        s.play(Create(perp0), Write(hlab0), run_time=T_ANIM)
        f = fitw(az_math("h", "=", r"\mathrm{d}(P, \ell)", ">", "0", size=FS_FORMULA))
        ft = fitw(az_tex("— bütün cütlər arasında ən kiçik", size=30, color=C_TEXT2))
        VGroup(f, ft).arrange(DOWN, buff=0.25).move_to(P2(COL_X, 1.2))
        f[0].set_color(C_MIN)
        self.col_add(f)
        self.col_add(ft, FadeIn)
        s.wait(read_wait("h = d(P, l) > 0 — bütün cütlər arasında ən kiçik"))
        # ədəd oxunu yadda saxla (Addım 8-də qayıdacaq)
        self.axis_group = VGroup(self.axis, self.axis_lab, self.axis_dots, self.min_lab)
        s.play(FadeOut(self.axis_group), run_time=T_ANIM)
        schema_out = [self.schema] + ([] if self.pts_mode else [self.idots])
        s.play(*[FadeOut(m) for m in schema_out], run_time=T_ANIM)
        # kanonik diaqram
        P, H = K["P"], K["H"]
        self.ell = full_line(H, K["B"], box=self.box, color=C_ELL, width=4)
        self.ell_lab = make_label(r"\ell", self.ell.get_end(), UL, color=C_ELL, size=38)
        self.Pdot = make_dot(P, color=C_MIN, r=0.1)
        self.Plab = make_label("P", P, RIGHT + 0.3 * UP, size=38, buff=0.14)
        self.hseg = DashedLine(P, H, color=C_MIN, stroke_width=4, dash_length=0.12)
        self.hlab = make_label("h", (P + H) / 2, LEFT, color=C_MIN, size=38, buff=0.15)
        caption(s, "Diaqramı rahat vəziyyətə gətirək: $\\ell$ üfüqi olsun")
        s.play(ReplacementTransform(ell0, self.ell), ReplacementTransform(elab0, self.ell_lab),
               ReplacementTransform(pdot0, self.Pdot), ReplacementTransform(plab0, self.Plab),
               ReplacementTransform(perp0, self.hseg), ReplacementTransform(hlab0, self.hlab),
               run_time=T_SLOW)
        self.Hdot = make_dot(H, color=C_TEXT, r=0.06)
        self.Hlab = make_label("H", H, DL, size=36, buff=0.1)
        self.Hra = right_angle(H, RIGHT, UP, size=0.24, color=C_TEXT2)
        s.play(GrowFromCenter(self.Hdot), Create(self.Hra), Write(self.Hlab), run_time=T_ANIM)
        g = az_math("PH", "=", "h", size=FS_FORMULA).move_to(P2(COL_X, -0.3))
        g[2].set_color(C_MIN)
        self.col_add(g)
        caption(s, "$H$ — perpendikulyarın oturacağı, $PH = h$")
        self.breathe()

    # ── Addım 3: ℓ üzərində üç nöqtə (yeganə fərqli addım) ─────────────────
    def _abc_objects(self):
        K = self.K
        self.Adot, self.Bdot, self.Cdot = (make_dot(K[k]) for k in "ABC")
        self.Alab = make_label("A", K["A"], DL, size=36, buff=0.1)
        self.Blab = make_label("B", K["B"], DR, size=36, buff=0.1)
        self.Clab = make_label("C", K["C"], DOWN, size=36, buff=0.15)

    def step3(self):
        s, K = self.s, self.K
        self.label(3)
        self.col_clear()
        self._abc_objects()
        if self.pts_mode:
            caption(s, "$\\ell$ birləşdirici xətdir: üzərində iki nöqtə var")
            for d, l in ((self.Adot, self.Alab), (self.Bdot, self.Blab)):
                s.play(GrowFromCenter(d), Write(l), Flash(d.get_center(), color=C_POINT,
                                                          flash_radius=0.3), run_time=T_ANIM)
            caption(s, "Şərtə görə üçüncü nöqtə də var")
            s.play(GrowFromCenter(self.Cdot), Write(self.Clab),
                   Flash(K["C"], color=C_POINT, flash_radius=0.3), run_time=T_ANIM)
            self.PAline = self.PCline = None
        else:
            tag = az_tex("yeganə fərq", size=28, color=C_POINT)
            tag_box = SurroundingRectangle(tag, color=C_POINT, buff=0.1, stroke_width=2)
            tag_g = VGroup(tag, tag_box).next_to(s._step, DOWN, buff=0.15).align_to(s._step, RIGHT)
            s.play(FadeIn(tag_g), run_time=T_ANIM)
            caption(s, "$P$ kəsişmə nöqtəsidir — ondan ən azı üç xətt keçir")
            P = K["P"]
            self.PAline = full_line(P, K["A"], box=self.box)
            self.PBline = full_line(P, K["B"], box=self.box)
            self.PCline = full_line(P, K["C"], box=self.box)
            for ln in (self.PAline, self.PBline, self.PCline):
                s.play(GrowFromPoint(ln, P), run_time=T_ANIM)
            s.bring_to_front(self.Pdot)
            caption(s, "Heç biri $\\ell$-ə paralel deyil — hamısı $\\ell$-i kəsir")
            s.play(*[GrowFromCenter(d) for d in (self.Adot, self.Bdot, self.Cdot)],
                   *[Flash(K[k], color=C_POINT, flash_radius=0.3) for k in "ABC"],
                   *[Write(l) for l in (self.Alab, self.Blab, self.Clab)], run_time=T_ANIM)
            caption(s, "Bu nöqtələr fərqlidir")
            # vizual sübut: PA xətti PB-yə doğru fırlanır
            ang_a = angle_of_vector(K["A"] - P)
            ang_b = angle_of_vector(K["B"] - P)
            th = ValueTracker(ang_a)
            ys = K["H"][1]

            def moving_x():
                d = np.array([np.cos(th.get_value()), np.sin(th.get_value()), 0.0])
                return intersect(P, P + d, K["H"], K["B"])

            rot_line = always_redraw(lambda: full_line(
                P, P + np.array([np.cos(th.get_value()), np.sin(th.get_value()), 0.0]),
                box=self.box, color=C_POINT, width=3))
            rot_dot = always_redraw(lambda: make_dot(moving_x(), color=C_POINT, r=0.09))
            s.play(FadeIn(rot_line), FadeIn(rot_dot), run_time=1.5)
            s.play(th.animate.set_value(ang_b), run_time=T_SLOW)
            two = VGroup(Circle(radius=0.2, color=C_MIN, stroke_width=4).move_to(P),
                         Circle(radius=0.2, color=C_MIN, stroke_width=4).move_to(K["B"]))
            s.play(Create(two), run_time=T_ANIM)
            x = cross_mark(size=64).move_to(K["B"] + P2(0.55, 0.45))
            s.play(Write(x), run_time=T_ANIM)
            note = para(["İki ortaq nöqtəsi olan", "xətlər üst-üstə düşür"], size=32)
            note.move_to(P2(COL_X, 0.6))
            self.col_add(note, FadeIn)
            s.wait(read_wait("İki ortaq nöqtəsi olan xətlər üst-üstə düşür"))
            s.play(th.animate.set_value(ang_a), FadeOut(two), FadeOut(x), run_time=T_SLOW)
            rot_line.clear_updaters()
            rot_dot.clear_updaters()
            s.play(FadeOut(rot_line), FadeOut(rot_dot), FadeOut(tag_g), run_time=1.5)
            s.bring_to_front(self.Pdot, self.Adot, self.Bdot, self.Cdot)
        self.breathe()

    # ── Addım 4: iki qapalı şüa, göyərçin yuvası ─────────────────────────────
    def step4(self):
        s, K = self.s, self.K
        self.label(4)
        self.col_clear()
        H = K["H"]
        a, b = self.ell.get_start(), self.ell.get_end()
        left_end, right_end = (a, b) if a[0] < b[0] else (b, a)
        self.ray_l = Line(left_end, H, color=C_RAY_L, stroke_width=6)
        self.ray_r = Line(H, right_end, color=C_RAY_R, stroke_width=6)
        hring = VGroup(
            Arc(radius=0.14, start_angle=PI / 2, angle=PI, color=C_RAY_L, stroke_width=4),
            Arc(radius=0.14, start_angle=-PI / 2, angle=PI, color=C_RAY_R, stroke_width=4),
        ).move_to(H)
        s.play(FadeIn(self.ray_l), FadeIn(self.ray_r), FadeOut(self.ell), run_time=T_ANIM)
        s.play(Create(hring), run_time=T_ANIM)
        s.bring_to_front(self.Hdot, self.Adot, self.Bdot, self.Cdot)
        self.hring = hring
        caption(s, "$H$ nöqtəsi $\\ell$-i iki qapalı şüaya bölür")
        # göyərçin yuvası sxemi (sağ sütunda)
        boxes = VGroup(
            Rectangle(width=1.7, height=0.9, color=C_RAY_L, stroke_width=4),
            Rectangle(width=1.7, height=0.9, color=C_RAY_R, stroke_width=4),
        ).arrange(RIGHT, buff=0.5).move_to(P2(COL_X, 0.7))
        blabs = VGroup(az_tex("sol şüa", size=26, color=C_RAY_L).next_to(boxes[0], DOWN, 0.15),
                       az_tex("sağ şüa", size=26, color=C_RAY_R).next_to(boxes[1], DOWN, 0.15))
        pig = VGroup(*[make_dot(P2(COL_X - 0.7 + 0.7 * i, 2.1), r=0.11) for i in range(3)])
        pl = VGroup(*[make_label(t, d.get_center(), UP, size=30, buff=0.1)
                      for t, d in zip("CAB", pig)])
        s.play(Create(boxes), FadeIn(blabs), run_time=T_ANIM)
        s.play(FadeIn(pig), FadeIn(pl), run_time=T_ANIM)
        targets = [boxes[0].get_center(), boxes[1].get_center() + 0.35 * LEFT,
                   boxes[1].get_center() + 0.35 * RIGHT]
        s.play(*[d.animate.move_to(t) for d, t in zip(pig, targets)],
               *[l.animate.move_to(t + 0.32 * UP) for l, t in zip(pl, targets)],
               run_time=T_SLOW)
        s.play(Indicate(boxes[1], color=C_POINT), run_time=T_ANIM)
        self.col += [boxes, blabs, pig, pl]
        caption(s, "3 nöqtə, 2 şüa — ikisi eyni şüadadır (göyərçin yuvası prinsipi)")
        self.col_clear()
        caption(s, "Eyni şüadakı iki nöqtə: $H$-a yaxın olan $A$, uzaq olan $B$")
        self.c_objs = VGroup(self.Cdot, self.Clab) if self.PCline is None else \
            VGroup(self.Cdot, self.Clab, self.PCline)
        s.play(self.c_objs.animate.set_opacity(0.25), run_time=T_ANIM)
        f = az_math("HA", "<", "HB", size=FS_FORMULA).move_to(P2(COL_X, 2.2))
        self.col_add(f)
        self.f_HA = f
        note = para(["$A$ nöqtəsi $HB$ parçası", "üzərindədir", "(ola bilər ki, $A = H$)"],
                    size=32).move_to(P2(COL_X, 0.9))
        self.col_add(note, FadeIn)
        s.wait(read_wait("A nöqtəsi HB parçası üzərindədir (ola bilər ki, A = H)"))
        caption(s, "$HA = HB$ ola bilməz: onda $A = B$ olardı")
        self.breathe()

    # ── Addım 5: AB < PB ─────────────────────────────────────────────────────
    def step5(self):
        s, K = self.s, self.K
        self.label(5)
        self.col_clear()
        P, H, A, B = K["P"], K["H"], K["A"], K["B"]
        self.ABseg = Line(A, B, color=C_TEXT, stroke_width=SEG_W)
        s.play(Create(self.ABseg), run_time=T_ANIM)
        s.bring_to_front(self.Adot, self.Bdot)
        self.brAB = BraceBetweenPoints(A, B, DOWN, buff=0.12, color=C_TEXT2)
        self.brAB_l = az_math("AB", size=32).next_to(self.brAB, DOWN, buff=0.08)
        self.brHB = BraceBetweenPoints(H + 0.7 * DOWN, B + 0.7 * DOWN, DOWN, buff=0.1,
                                       color=C_TEXT2)
        self.brHB_l = az_math("HB", size=32).next_to(self.brHB, DOWN, buff=0.08)
        s.play(GrowFromCenter(self.brAB), Write(self.brAB_l), run_time=T_ANIM)
        s.play(GrowFromCenter(self.brHB), Write(self.brHB_l), run_time=T_ANIM)
        f1 = fitw(az_math("AB", "=", "HB", "-", "HA", r"\le", "HB", size=FS_FORMULA_S))
        f1.move_to(P2(COL_X, 2.55))
        self.col_add(f1)
        s.wait(read_wait("AB = HB - HA ≤ HB"))
        # PB xətti və PHB düzbucaqlı üçbucağı
        if self.pts_mode:
            self.PBline = full_line(P, B, box=self.box)
            s.play(Create(self.PBline), run_time=T_ANIM)
            s.bring_to_front(self.Pdot, self.Bdot)
        tri = Polygon(P, H, B, stroke_width=0, fill_color=C_TEXT, fill_opacity=0.12)
        self.PBseg = Line(P, B, color=C_LINE, stroke_width=SEG_W)
        s.play(FadeIn(tri), Create(self.PBseg), run_time=T_ANIM)
        s.bring_to_front(self.Pdot, self.Bdot, self.Hdot)
        caption(s, "$PB$ — düzbucaqlı $PHB$ üçbucağının hipotenuzudur")
        # Pifaqor: kiçik surətdə kvadratlar
        k = 0.22
        cpos = P2(COL_X, 0.75)
        ctr = (P + H + B) / 3
        mp = lambda x: cpos + k * (x - ctr)
        mini_tri = Polygon(mp(P), mp(H), mp(B), color=C_TEXT, stroke_width=2,
                           fill_color=C_TEXT, fill_opacity=0.1)

        def square_on(p, q, inside, color):
            v = q - p
            n = unit(np.cross(v, OUT))
            if np.dot(n, inside - p) > 0:
                n = -n
            L = np.linalg.norm(v)
            return Polygon(p, q, q + L * n, p + L * n, stroke_width=2, color=color,
                           fill_color=color, fill_opacity=0.35)

        cen = mp(ctr)
        sqs = VGroup(square_on(mp(P), mp(H), cen, C_MIN), square_on(mp(H), mp(B), cen, C_TEXT2),
                     square_on(mp(P), mp(B), cen, C_LINE))
        s.play(TransformFromCopy(tri, mini_tri), run_time=T_ANIM)
        s.play(LaggedStart(*[FadeIn(q) for q in sqs], lag_ratio=0.3), run_time=T_ANIM)
        g1 = fitw(az_math("PB^2", "=", "PH^2", "+", "HB^2", size=FS_FORMULA_S))
        g1.move_to(P2(COL_X, -0.95))
        s.play(Write(g1), run_time=T_ANIM)
        s.wait(read_wait("PB^2 = PH^2 + HB^2"))
        s.play(FadeOut(mini_tri), FadeOut(sqs), FadeOut(tri), run_time=T_ANIM)
        s.play(g1.animate.move_to(P2(COL_X, 1.55)), run_time=T_ANIM)
        g2 = fitw(az_math("PB^2", "=", "h^2", "+", "HB^2", ">", "HB^2", size=FS_FORMULA_S))
        g2.move_to(g1)
        tmt(s, g1, g2)
        s.wait(read_wait("PB^2 = h^2 + HB^2 > HB^2"))
        g3 = az_math(r"\Rightarrow\;", "HB", "<", "PB", size=FS_FORMULA_S).move_to(P2(COL_X, 0.6))
        tmt(s, g2.copy(), g3)
        g4 = az_math("AB", r"\le", "HB", "<", "PB", size=FS_FORMULA).move_to(P2(COL_X, -0.45))
        tmt(s, VGroup(f1.copy(), g3.copy()), g4)
        s.wait(read_wait("AB ≤ HB < PB"))
        g5 = az_math("AB", "<", "PB", size=FS_FORMULA).move_to(g4)
        tmt(s, g4, g5)
        frame = SurroundingRectangle(g5, color=C_NEW, buff=0.15)
        s.play(Create(frame), run_time=T_ANIM)
        self.col += [f1, g2, g3]
        self.col_clear(keep=[])
        memo = VGroup(g5, frame)
        memo_pos = P2(3.65, 3.45) if self.pts_mode else P2(3.3, 3.45)
        s.play(memo.animate.scale(0.75).move_to(memo_pos), run_time=T_ANIM)
        self.memo = memo
        # kənar hal: A -> H
        caption(s, "Kənar hal: $A$ nöqtəsi $H$-a yaxınlaşsın")
        ax = ValueTracker(A[0])
        Apos = lambda: P2(ax.get_value(), A[1])
        statics = [self.Adot, self.Alab, self.ABseg, self.brAB, self.brAB_l]
        if self.PAline is not None:
            statics.append(self.PAline)
        dyn = VGroup(
            always_redraw(lambda: Line(Apos(), B, color=C_TEXT, stroke_width=SEG_W)),
            always_redraw(lambda: BraceBetweenPoints(Apos(), B, DOWN, buff=0.12,
                                                     color=C_TEXT2)),
            always_redraw(lambda: az_math("AB", size=32).next_to(
                BraceBetweenPoints(Apos(), B, DOWN, buff=0.12), DOWN, buff=0.08)),
            always_redraw(lambda: make_dot(Apos())),
            always_redraw(lambda: make_label("A", Apos(), DL, size=36, buff=0.1)),
        )
        if self.PAline is not None:
            dyn.add(always_redraw(lambda: full_line(P, Apos(), box=self.box)))
        s.remove(*statics)
        s.add(dyn)
        s.play(FadeOut(self.Hlab), run_time=1.5)
        s.bring_to_front(self.Pdot, self.Bdot, dyn[3])
        s.play(ax.animate.set_value(H[0]), run_time=T_SLOW)
        eq = az_math("AB", "=", "HB", size=FS_FORMULA_S).move_to(P2(COL_X, 1.2))
        s.play(Write(eq), run_time=T_ANIM)
        caption(s, "$A = H$ olsa belə, $HB < PB$ ciddi qalır")
        s.play(ax.animate.set_value(A[0]), FadeOut(eq), run_time=T_SLOW)
        for m in dyn:
            m.clear_updaters()
        s.remove(dyn)
        s.add(*statics)
        s.play(FadeIn(self.Hlab), run_time=1.5)
        s.bring_to_front(self.Pdot, self.Adot, self.Bdot)
        s.play(*[FadeOut(m) for m in (self.brAB, self.brAB_l, self.brHB, self.brHB_l)],
               run_time=T_ANIM)
        self.breathe()

    # ── Addım 6: sahə fəndi (ƏSAS AN) ────────────────────────────────────────
    def step6(self):
        s, K = self.s, self.K
        self.label(6)
        P, H, A, B = K["P"], K["H"], K["A"], K["B"]
        self.tri = Polygon(P, A, B, stroke_width=0, fill_color=C_AUX, fill_opacity=0.3)
        s.play(FadeIn(self.tri), run_time=T_ANIM)
        s.bring_to_front(self.ABseg, self.PBseg, self.Pdot, self.Adot, self.Bdot)
        caption(s, "$PAB$ üçbucağı cırlaşmış deyil: $A \\ne B$, $P \\notin \\ell$")
        caption(s, "Eyni üçbucaq, iki fərqli oturacaq")
        S1, S2 = area_trick(s, P, A, B, H)
        # əsas diaqramda h'
        F = foot_of_perpendicular(A, P, B)
        self.hp = DashedLine(A, F, color=C_NEW, stroke_width=4, dash_length=0.12)
        self.hp_ra = right_angle(F, B - P, A - F, size=0.2, color=C_NEW)
        self.hp_lab = make_label("h'", (A + F) / 2, unit(np.cross(F - A, IN)), color=C_NEW,
                                 size=38, buff=0.12)
        s.play(Create(self.hp), run_time=T_ANIM)
        s.play(Create(self.hp_ra), Write(self.hp_lab), run_time=T_ANIM)
        s.bring_to_front(self.Adot)
        # cəbri addımlar
        e1 = az_math(r"\tfrac12", r"\cdot", "AB", r"\cdot", "h", "=",
                     r"\tfrac12", r"\cdot", "PB", r"\cdot", "h'", size=FS_FORMULA_S)
        fitw(e1).move_to(P2(COL_X, 1.9))
        tmt(s, VGroup(S1, S2), e1)
        s.wait(read_wait("1/2 AB h = 1/2 PB h'"))
        e2 = az_math("AB", r"\cdot", "h", "=", "PB", r"\cdot", "h'", size=FS_FORMULA)
        e2.move_to(e1)
        tmt(s, e1, e2)
        s.wait(read_wait("AB h = PB h'"))
        e3 = az_math("h'", "=", r"{AB", r"\over", r"PB}", r"\cdot", "h", size=FS_FORMULA)
        e3.move_to(P2(4.1, 1.9))
        tmt(s, e2, e3)
        e3[0].set_color(C_NEW)
        e3[6].set_color(C_MIN)
        s.wait(read_wait("h' = AB/PB h"))
        frac = VGroup(e3[2], e3[3], e3[4])
        arrow = CurvedArrow(self.memo.get_bottom() + 0.05 * DOWN, frac.get_right() + 0.15 * RIGHT,
                            angle=-PI / 3, color=C_NEW, stroke_width=3)
        s.play(Create(arrow), run_time=T_ANIM)
        e4 = az_math(r"{AB", r"\over", r"PB}", "<", "1", size=FS_FORMULA).move_to(P2(4.1, 0.45))
        s.play(TransformFromCopy(frac, VGroup(*e4[:3])), FadeIn(VGroup(*e4[3:])), run_time=T_ANIM)
        s.wait(read_wait("AB/PB < 1"))
        e5 = az_math("h'", "<", "h", size=FS_FORMULA + 4).move_to(P2(4.1, -0.9))
        e5[0].set_color(C_NEW)
        e5[2].set_color(C_MIN)
        tmt(s, VGroup(e3.copy(), e4.copy()), e5)
        glow = SurroundingRectangle(e5, color=C_NEW, buff=0.18, stroke_width=5)
        s.play(Create(glow), Flash(glow.get_corner(UR), color=C_NEW), run_time=T_ANIM)
        self.col += [e3, e4, arrow]
        # vizual müqayisə: h və h' yan-yana
        base_y = -2.45
        hbar = Line(P2(6.2, base_y), P2(6.2, base_y + np.linalg.norm(P - H)),
                    color=C_MIN, stroke_width=7)
        hpbar = Line(P2(6.75, base_y), P2(6.75, base_y + np.linalg.norm(A - F)),
                     color=C_NEW, stroke_width=7)
        hb_l = make_label("h", hbar.get_top(), UP, color=C_MIN, size=36, buff=0.1)
        hpb_l = make_label("h'", hpbar.get_top(), UP, color=C_NEW, size=36, buff=0.1)
        s.play(TransformFromCopy(self.hseg, hbar), TransformFromCopy(self.hp, hpbar),
               run_time=T_SLOW)
        s.play(FadeIn(hb_l), FadeIn(hpb_l), run_time=1.5)
        self.col += [e5, glow, hbar, hpbar, hb_l, hpb_l]
        self.breathe()

    # ── Addım 7: yeni cüt icazəlidir ─────────────────────────────────────────
    def step7(self):
        s, K = self.s, self.K
        self.label(7)
        self.col_clear()
        s.play(FadeOut(self.memo), run_time=1.5)
        caption(s, "Yeni cüt: $(A,\\; PB)$")
        if self.pts_mode:
            items = [["$A$ — verilmiş nöqtədir"],
                     ["$PB$ — birləşdirici xətdir:", "$P$ və $B$ verilmiş", "nöqtələrdir"],
                     ["$A \\notin PB$: $PB$ və $\\ell$", "yalnız $B$-də kəsişir,",
                      "$A \\ne B$"]]
        else:
            items = [["$A$ — kəsişmə nöqtəsidir:", "ondan $\\ell$ və $PA$ keçir"],
                     ["$PB$ — verilmiş", "xətlərdən biridir"],
                     ["$PB$ xətti $A$-dan keçmir:", "$PB$ və $\\ell$ yalnız", "$B$-də kəsişir"]]
        y = 2.75
        for n, lines in enumerate(items):
            blk = para(lines, size=30, buff=0.1)
            blk.move_to(P2(0, y), aligned_edge=UP).set_x(3.2, LEFT)
            mark = check_mark(size=40).next_to(blk[0], LEFT, buff=0.2)
            s.play(FadeIn(blk, shift=0.1 * LEFT), run_time=T_ANIM)
            if n == 0:
                anims = [Indicate(self.Adot, color=C_POINT, scale_factor=2.0)]
                if not self.pts_mode:
                    anims += [Indicate(self.PAline, color=C_TEXT),
                              Indicate(self.ray_r, color=C_TEXT)]
                s.play(*anims, run_time=T_ANIM)
            elif n == 1:
                s.play(Indicate(self.PBline, color=C_TEXT), Indicate(self.PBseg, color=C_TEXT),
                       run_time=T_ANIM)
            else:
                s.play(Flash(K["B"], color=C_POINT, flash_radius=0.35), run_time=T_ANIM)
                s.play(Indicate(self.Adot, color=C_POINT, scale_factor=2.0),
                       Indicate(self.Bdot, color=C_POINT, scale_factor=2.0), run_time=T_ANIM)
            s.wait(read_wait(lines))
            s.play(Write(mark), run_time=1.5)
            self.col += [blk, mark]
            y = blk.get_bottom()[1] - 0.35
        self.breathe()

    # ── Addım 8: ziddiyyət ───────────────────────────────────────────────────
    def step8(self):
        s, K = self.s, self.K
        self.label(8)
        self.col_clear()
        f = az_math(r"\mathrm{d}(A, PB)", "=", "h'", "<", "h", size=FS_FORMULA)
        f[2].set_color(C_NEW)
        f[4].set_color(C_MIN)
        f.move_to(P2(COL_X, 0.9))
        self.col_add(f)
        s.play(FadeIn(self.axis_group), run_time=T_ANIM)
        hmin = self.pairs[self.imin][2]
        ratio = np.linalg.norm(K["A"] - foot_of_perpendicular(K["A"], K["P"], K["B"])) / \
            np.linalg.norm(K["P"] - K["H"])
        gdot = make_dot(self.axis.n2p(hmin * ratio), color=C_NEW, r=0.09)
        glab = make_label("h'", gdot.get_center(), UL, color=C_NEW, size=30, buff=0.08)
        s.play(GrowFromCenter(gdot), FadeIn(glab), Flash(gdot.get_center(), color=C_NEW),
               run_time=T_ANIM)
        s.play(Wiggle(self.min_dot, scale_value=1.6), run_time=T_ANIM)
        red_frame_flash(s)
        caption(s, "Ziddiyyət! $h$ ən kiçik məsafə deyildi")
        self.breathe()
        # sxematik konfiqurasiya geri qayıdır
        keep = {s._section, s._caption, s._step}
        out = [m for m in s.mobjects if m not in keep]
        s.play(*[FadeOut(m) for m in out], run_time=T_ANIM)
        if self.pts_mode:
            s.play(FadeIn(self.schema), run_time=T_ANIM)
        else:
            s.play(FadeIn(self.schema), FadeIn(self.idots), run_time=T_ANIM)
        caption(s, "Bu şəkil mümkün deyil")
        if self.pts_mode:
            s.play(self.schema.animate.set_color(C_MIN), run_time=T_ANIM)
            s.play(*[Wiggle(d, scale_value=1.8) for d in self.schema], run_time=T_ANIM)
            xs = np.array([p[0] for p in self.pts])
            y_line = lambda x: 0.12 * (x - xs.mean()) + 0.35
            targets = [P2(p[0], y_line(p[0])) for p in self.pts]
            gl = full_line(P2(-6, y_line(-6)), P2(1, y_line(1)), box=self.box, color=C_NEW,
                           width=4)
            s.play(*[d.animate.move_to(t).set_color(C_POINT) for d, t in
                     zip(self.schema, targets)], run_time=T_SLOW)
            s.play(Create(gl), run_time=T_ANIM)
            s.bring_to_front(self.schema)
            final = "Deməli, bütün nöqtələr bir xətt üzərindədir"
        else:
            s.play(self.schema.animate.set_color(C_MIN), FadeOut(self.idots), run_time=T_ANIM)
            s.play(*[Wiggle(m, scale_value=1.05, rotation_angle=0.02 * TAU)
                     for m in self.schema], run_time=T_ANIM)
            O = P2(-2.4, 0.3)
            new_lines = VGroup(*[full_line(O, O + d, box=self.box, color=C_LINE)
                                 for _, d in self.lines])
            s.play(*[Transform(m, t) for m, t in zip(self.schema, new_lines)], run_time=T_SLOW)
            od = make_dot(O, color=C_NEW, r=0.13)
            s.play(GrowFromCenter(od), Flash(O, color=C_NEW, flash_radius=0.6,
                                             line_length=0.4, num_lines=16), run_time=T_ANIM)
            final = "Deməli, bütün xətlər bir nöqtədən keçir"
        caption(s, final + r"\quad $\blacksquare$")
        self.breathe()
        keep = {s._section, s._caption, s._step}
        out = [m for m in s.mobjects if m not in keep]
        s.play(*[FadeOut(m) for m in out], run_time=T_ANIM)


def kelly_proof(scene, mode="points"):
    """Kellinin isbatı (Addım 0–8): mode="points" — Hisse02, mode="lines" — Hisse03."""
    KellyProof(scene, mode).run()


def area_trick(scene, P, A, B, H, center=None, k=0.62):
    """Sahə fəndi: PAB üçbucağının surəti (h ilə) sağa uçur; əvvəl AB oturacaq, sonra
    surət fırlanır və PB oturacaq olur, A-dan PB-yə h' çəkilir.
    Qaytarır: iki sahə düsturu (S1, S2) — sonrakı cəbri addımlar üçün."""
    s = scene
    if center is None:
        center = P2(COL_X, 1.35)
    tri = Polygon(P, A, B, color=C_AUX, stroke_width=2, fill_color=C_AUX, fill_opacity=0.3)
    ext = DashedLine(A, H, color=C_TEXT2, stroke_width=2, dash_length=0.08)
    hseg = DashedLine(P, H, color=C_MIN, stroke_width=3.5, dash_length=0.1)
    hra = right_angle(H, RIGHT, UP, size=0.2, color=C_MIN)
    dots = VGroup(make_dot(P, C_MIN, 0.08), make_dot(A, C_POINT, 0.08),
                  make_dot(B, C_POINT, 0.08))
    copy = VGroup(tri, ext, hseg, hra, dots)
    names = ["P", "A", "B"]
    labs = VGroup(*[az_math(n, size=32) for n in names])

    def place_labels(m):
        cen = (dots[0].get_center() + dots[1].get_center() + dots[2].get_center()) / 3
        for lab, d in zip(m, dots):
            v = unit(d.get_center() - cen)
            lab.move_to(d.get_center() + 0.32 * v)
        return m

    place_labels(labs)
    labs.add_updater(place_labels)
    hl = always_redraw(lambda: az_math("h", size=32, color=C_MIN).next_to(hseg, LEFT, buff=0.08)
                       if hseg.get_stroke_opacity() > 0.5 else VectorizedPoint())
    s.add(copy, labs, hl)
    s.play(copy.animate.scale(k).move_to(center), run_time=T_SLOW)
    S1 = az_math("S_{PAB}", "=", r"\tfrac12", r"\cdot", "AB", r"\cdot", "h", size=FS_FORMULA_S)
    S1[6].set_color(C_MIN)
    fitw(S1).move_to(P2(COL_X, -0.35))
    base = Line(dots[1].get_center(), dots[2].get_center(), color=C_POINT, stroke_width=6)
    s.play(Create(base), run_time=1.5)
    s.play(Write(S1), run_time=T_ANIM)
    s.wait(read_wait("S = 1/2 · AB · h") + 1.0)
    s.play(FadeOut(base), hseg.animate.set_stroke(opacity=0.0), ext.animate.set_stroke(opacity=0),
           hra.animate.set_stroke(opacity=0), run_time=1.5)
    # fırlanma: PB oturacağı aşağıda üfüqi olsun, A yuxarıda
    p, a, b = (d.get_center() for d in dots)
    ang = -angle_of_vector(b - p)
    if np.cross(b - p, a - p)[2] < 0:
        ang += PI
    ang = (ang + PI) % TAU - PI
    rc = copy.get_center()
    s.play(Rotate(copy, angle=ang, about_point=rc), run_time=T_SLOW)
    p, a, b = (d.get_center() for d in dots)
    F = foot_of_perpendicular(a, p, b)
    pb_base = Line(p, b, color=C_LINE, stroke_width=6)
    hp = DashedLine(a, F, color=C_NEW, stroke_width=3.5, dash_length=0.1)
    hp_ra = right_angle(F, b - p, a - F, size=0.18, color=C_NEW)
    hp_l = make_label("h'", (a + F) / 2, RIGHT, color=C_NEW, size=32, buff=0.1)
    s.play(Create(pb_base), run_time=1.5)
    s.play(Create(hp), run_time=T_ANIM)
    s.play(Create(hp_ra), Write(hp_l), run_time=1.5)
    S2 = az_math("S_{PAB}", "=", r"\tfrac12", r"\cdot", "PB", r"\cdot", "h'", size=FS_FORMULA_S)
    S2[6].set_color(C_NEW)
    fitw(S2).next_to(S1, DOWN, buff=0.35)
    s.play(Write(S2), run_time=T_ANIM)
    note = para(["$h' = \\mathrm{d}(A, PB)$ —", "$A$-dan $PB$ xəttinə qədər məsafə"],
                size=30, color=C_TEXT2).next_to(S2, DOWN, buff=0.35)
    s.play(FadeIn(note), run_time=T_ANIM)
    s.wait(read_wait("h' = d(A, PB) — A-dan PB xəttinə qədər məsafə"))
    labs.clear_updaters()
    hl.clear_updaters()
    s.play(FadeOut(VGroup(copy, labs, hl, pb_base, hp, hp_ra, hp_l, note)), run_time=T_ANIM)
    return S1, S2

# ═════════════════════════════════════════════════════════════════════════════
#  7. SƏHNƏLƏR
# ═════════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────────────
#  Hisse00 — 1. Giriş: məsələ və şərtlərin rolu (≈2.5 dəq)
# ─────────────────────────────────────────────────────────────────────────────
class Hisse00_Giris(AZScene):
    # Əks-nümunə cəhdinin xətləri: ilk iki xətt Q0-dan keçir
    Q0 = (-2.0, 0.2)
    ANG_FIRST = (70, 165)      # ilk iki xətt
    ANG_THIRD = 115            # Q0-dan keçən üçüncü xətt
    L4 = ((1.2, -0.6), 32)     # Q0-dan keçməyən dördüncü xətt
    CYCLES = 3                 # "?" -> yeni xətt -> yeni "?" dövrlərinin sayı

    def construct(self):
        self.title_card()
        section_title(self, "1. Giriş: məsələ və şərtlərin rolu")
        statement = self.statement()
        self.counterexample(statement)
        self.conditions()
        end_section(self)

    # --- Başlıq kartı ---------------------------------------------------------
    def title_card(self):
        t1 = az_tex("Ekstremal prinsip", size=84)
        t2 = az_tex("Silvester–Qallai teoremi, onun dualı və nəticələri", size=FS_TEXT,
                    color=C_TEXT2)
        VGroup(t1, t2).arrange(DOWN, buff=0.5)
        self.play(Write(t1), run_time=T_ANIM)
        self.play(FadeIn(t2, shift=0.2 * UP), run_time=T_ANIM)
        self.wait(4)
        self.play(FadeOut(t1), FadeOut(t2), run_time=T_ANIM)

    # --- Məsələnin qoyuluşu ---------------------------------------------------
    def statement(self):
        s = [
            "Müstəvidə sonlu sayda, cüt-cüt paralel olmayan düz xətlər verilmişdir.",
            "İstənilən iki xəttin kəsişmə nöqtəsindən verilmiş xətlərdən daha biri keçir.",
            "İsbat edin ki, bütün xətlər bir nöqtədən keçir.",
        ]
        texts = VGroup(*[az_tex(x, size=36) for x in s]).arrange(DOWN, buff=0.32)
        texts.move_to(DOWN * 1.75)

        win = (-3.4, 3.4, 0.35, 3.05)          # illüstrasiya pəncərəsi
        c = P2(0, 1.7)
        # (1) bir neçə mavi xətt (cüt-cüt paralel deyil)
        offs = [(-1.3, 0.35), (0.9, -0.4), (-0.2, -0.55), (1.5, 0.45), (-0.4, 0.65)]
        angs = [12, 52, 97, 137, 168]
        ill1 = VGroup(*[line_through(c + P2(*o), a, box=win) for o, a in zip(offs, angs)])
        # (2) iki xəttin kəsişməsi və oradan keçən üçüncü xətt
        ill2_lines = VGroup(line_through(c, 25, box=win), line_through(c, 140, box=win))
        ill2_third = line_through(c, 82, box=win)
        ill2_dot = make_dot(c)
        # (3) xətlər dəstəsi
        ill3 = VGroup(*[line_through(c, a, box=win) for a in (0, 36, 72, 108, 144)])
        ill3_dot = make_dot(c)

        self.play(Write(texts[0]), LaggedStart(*[Create(x) for x in ill1], lag_ratio=0.2),
                  run_time=T_ANIM + 0.7)
        self.wait(read_wait(s[0]))
        self.play(FadeOut(ill1), run_time=1.5)
        self.play(Write(texts[1]), Create(ill2_lines), run_time=T_ANIM)
        self.play(GrowFromCenter(ill2_dot), Flash(c, color=C_POINT, flash_radius=0.25),
                  run_time=T_ANIM)
        self.play(GrowFromPoint(ill2_third, c), run_time=T_ANIM)
        self.wait(read_wait(s[1]))
        self.play(FadeOut(VGroup(ill2_lines, ill2_third, ill2_dot)), run_time=1.5)
        self.play(Write(texts[2]), LaggedStart(*[GrowFromPoint(x, c) for x in ill3],
                                               lag_ratio=0.15),
                  FadeIn(ill3_dot), run_time=T_ANIM + 0.5)
        self.wait(read_wait(s[2]))
        self.play(FadeOut(VGroup(ill3, ill3_dot)), run_time=1.5)
        # mətn yuxarı sağ küncə kiçilir (oxunaqlı qalsın deyə, qısa sətirlərə bölünür)
        corner = para([
            "Müstəvidə sonlu sayda, cüt-cüt paralel olmayan",
            "düz xətlər verilmişdir. İstənilən iki xəttin",
            "kəsişmə nöqtəsindən verilmiş xətlərdən daha",
            "biri keçir. İsbat edin ki, bütün xətlər bir",
            "nöqtədən keçir.",
        ], size=26, color=C_TEXT2, buff=0.1).to_corner(UR, buff=0.3)
        self.play(FadeTransform(texts, corner), run_time=T_ANIM)
        return corner

    # --- Əks-nümunə cəhdi -----------------------------------------------------
    def counterexample(self, statement):
        box = BOX_FULL
        caption(self, "Əks-nümunə qurmağa çalışaq")
        q0 = P2(*self.Q0)
        lines = [(q0, dir_deg(a)) for a in self.ANG_FIRST]
        mobs = VGroup(*[full_line(p, p + d, box=box) for p, d in lines])
        self.play(*[GrowFromPoint(m, q0) for m in mobs], run_time=T_ANIM)
        d0 = make_dot(q0)
        self.play(GrowFromCenter(d0), Flash(q0, color=C_POINT, flash_radius=0.3),
                  run_time=T_ANIM)
        q_mark = az_math("?", size=56, color=C_MIN).move_to(
            free_spot(q0, lines + [(q0, dir_deg(self.ANG_THIRD))]))
        self.play(Write(q_mark), run_time=T_ANIM)
        # şərt mətni ~10 san qaldı — sönür
        self.play(FadeOut(statement), run_time=T_ANIM)
        caption(self, "Bu nöqtədən üçüncü xətt keçməlidir")
        third = full_line(q0, q0 + dir_deg(self.ANG_THIRD), box=box)
        self.play(GrowFromPoint(third, q0), run_time=T_ANIM)
        ok = check_mark(size=52).move_to(q_mark)
        self.play(ReplacementTransform(q_mark, ok), run_time=T_ANIM)
        lines.append((q0, dir_deg(self.ANG_THIRD)))
        mobs.add(third)
        caption(self, "Hələlik bu, xətlər dəstəsidir: üç xətt bir nöqtədən keçir")
        caption(self, "Dəstə olmasın deyə, dördüncü xətt bu nöqtədən keçməsin")

        # kəsişmə nöqtələri: {"x": nöqtə, "lines": xətt indeksləri, "dot", "mark"}
        points = [{"x": q0, "lines": {0, 1, 2}, "dot": d0, "mark": ok}]

        def add_line(p, d):
            """Yeni xətt əlavə edir; yeni kəsişmələri qaytarır (hamısı numpy ilə)."""
            idx = len(lines)
            new_pts = []
            for j, (pj, dj) in enumerate(lines):
                x = intersect(p, p + d, pj, pj + dj)
                found = None
                for rec in points:
                    if np.linalg.norm(rec["x"] - x) < 1e-6:
                        found = rec
                if found is not None:
                    found["lines"] |= {idx, j}
                else:
                    rec = {"x": x, "lines": {idx, j}, "dot": None, "mark": None}
                    points.append(rec)
                    new_pts.append(rec)
            lines.append((p, d))
            return new_pts

        def visible(x):
            return in_box(x, (X_L, X_R, CAPTION_TOP, 3.0), margin=0.45) and not (
                x[0] < -0.6 and x[1] > 2.6)

        def show_new(new_pts):
            shown = [r for r in new_pts if visible(r["x"])]
            if not shown:
                return
            for rec in shown:
                rec["dot"] = make_dot(rec["x"])
            self.play(LaggedStart(*[GrowFromCenter(r["dot"]) for r in shown],
                                  lag_ratio=0.2), run_time=T_ANIM)
            for rec in shown:
                rec["mark"] = az_math("?", size=48, color=C_MIN).move_to(
                    free_spot(rec["x"], lines, r=0.34,
                              avoid_pts=[o["x"] for o in points if o is not rec]))
            self.play(LaggedStart(*[Write(r["mark"]) for r in shown], lag_ratio=0.2),
                      run_time=T_ANIM)

        p4, a4 = self.L4
        p4 = P2(*p4)
        l4 = full_line(p4, p4 + dir_deg(a4), box=box)
        self.play(Create(l4), run_time=T_ANIM)
        mobs.add(l4)
        show_new(add_line(p4, dir_deg(a4)))
        caption(self, "Üç yeni kəsişmə — hər birindən üçüncü xətt keçməlidir")
        caption(self, "Hər sual işarəsi üçün yeni xətt çəkək")

        for _ in range(self.CYCLES):
            target, ang = self._best_move(lines, points, visible)
            x = target["x"]
            ln = full_line(x, x + dir_deg(ang), box=box)
            self.play(GrowFromPoint(ln, x), run_time=T_ANIM)
            mobs.add(ln)
            new = add_line(x, dir_deg(ang))
            ok = check_mark(size=48).move_to(
                free_spot(x, lines, r=0.34, avoid_pts=[o["x"] for o in points
                                                       if o is not target]))
            self.play(ReplacementTransform(target["mark"], ok), run_time=T_ANIM)
            target["mark"] = ok
            show_new(new)
            self.wait(WAIT_STEP)
        caption(self, "Hər yeni xətt yeni kəsişmələr yaradır")
        caption(self, "Proses dayanmır: sual işarələri çoxalır")
        caption(self, "Yeganə uğurlu şəkil: bütün xətlər bir nöqtədən keçir")
        fade_all_but(self)
        c = P2(0, 0.35)
        pencil = VGroup(*[line_through(c, a) for a in (0, 30, 60, 90, 120, 150)])
        self.play(LaggedStart(*[GrowFromPoint(m, c) for m in pencil], lag_ratio=0.2),
                  run_time=T_SLOW)
        cdot = make_dot(c, color=C_NEW, r=0.12)
        self.play(GrowFromCenter(cdot), Flash(c, color=C_NEW, flash_radius=0.35),
                  run_time=T_ANIM)
        self.wait(WAIT_STEP)
        fade_all_but(self)

    @staticmethod
    def _best_move(lines, points, visible):
        """Növbəti '?' və yeni xəttin bucağı: yeni kəsişmələr ekranda, bir-birindən və
        mövcud nöqtə/işarələrdən uzaq; xətt başqa nöqtələrin yanından keçmir."""
        best, best_score = None, -1e9
        center = np.array([-0.3, 0.3])
        open_pts = [r for r in points if len(r["lines"]) == 2 and r["dot"] is not None]
        for rec in open_pts:
            x = rec["x"]
            others = [r["x"] for r in points if r is not rec and visible(r["x"])]
            marks = [r["mark"].get_center() for r in points
                     if r is not rec and r["mark"] is not None]
            for ang in np.arange(2.0, 180.0, 3.0):
                d = dir_deg(ang)
                if min(abs(np.cross(d, dj)[2]) for _, dj in lines) < 0.28:
                    continue
                new = [intersect(x, x + d, pj, pj + dj) for pj, dj in lines]
                new = [y for y in new if np.linalg.norm(y - x) > 1e-6]
                vis = [y for y in new if visible(y)]
                if len(vis) < 2:
                    continue
                sep = min([np.linalg.norm(y - o) for y in vis for o in others] or [9.0])
                sep2 = min([np.linalg.norm(a - b) for a, b in itertools.combinations(vis, 2)]
                           or [9.0])
                gap = min([dist_point_line(o, x, x + d) for o in others + marks] or [9.0])
                # yeni nöqtələr özlərindən keçməyən xətlərə çox yaxın olmasın
                clear = 9.0
                for y in vis:
                    for pj, dj in lines:
                        dd = dist_point_line(y, pj, pj + dj)
                        if dd > 1e-6:
                            clear = min(clear, dd)
                score = (min(sep, sep2, 1.1) + min(gap, 0.7) + min(clear, 0.6)
                         + 0.12 * min(len(vis), 3) - 0.06 * np.linalg.norm(x[:2] - center))
                if score > best_score:
                    best, best_score = (rec, ang), score
        return best

    # --- Şərtlərin rolu -------------------------------------------------------
    def conditions(self):
        caption(self, "Hər şərt nə üçün lazımdır?")
        # paralel olmama
        base = P2(-1.6, 0.3)
        par = VGroup(*[line_through(base + P2(k * 1.6, 0), 70) for k in (-1, 0, 1)])
        self.play(LaggedStart(*[Create(m) for m in par], lag_ratio=0.3), run_time=T_ANIM)
        caption(self, "Heç iki xətt kəsişmir — yoxlanılacaq kəsişmə yoxdur")
        caption(self, "Şərt ödənir, amma xətlər bir nöqtədən keçmir")
        x = cross_mark(size=110).move_to(P2(3.9, 0.4))
        self.play(Write(x), run_time=T_ANIM)
        caption(self, "Deməli, paralel olmama şərti lazımdır")
        self.wait(WAIT_STEP)
        self.play(FadeOut(par), FadeOut(x), run_time=T_ANIM)
        # sonluluq
        caption(self, "Sonluluq isbatda bir yerdə işləyir: ən kiçik məsafə mövcuddur")
        nl = NumberLine(x_range=[0, 6, 1], length=8, color=C_DIM, stroke_width=2,
                        include_numbers=True, font_size=28).move_to(P2(0, 0.4))
        vals = [0.8, 1.55, 2.2, 2.9, 3.35, 4.1, 4.7, 5.4]
        dots = VGroup(*[make_dot(nl.n2p(v), r=0.09) for v in vals])
        self.play(Create(nl), run_time=T_ANIM)
        self.play(LaggedStart(*[GrowFromCenter(d) for d in dots], lag_ratio=0.15),
                  run_time=T_ANIM)
        self.play(dots[0].animate.set_color(C_MIN), run_time=1.5)
        self.play(Circumscribe(dots[0], shape=Circle, color=C_MIN, buff=0.12),
                  run_time=T_ANIM)
        cap = az_tex("ən kiçik", size=FS_NOTE, color=C_MIN).next_to(dots[0], UP, buff=0.3)
        self.play(FadeIn(cap, shift=0.1 * DOWN), run_time=T_ANIM)
        caption(self, "Buna 6-cı bölmədə qayıdacağıq")


# ─────────────────────────────────────────────────────────────────────────────
#  Hisse01 — 2. İsinmə: ekstremal prinsip (≈4 dəq)
# ─────────────────────────────────────────────────────────────────────────────
class Hisse01_Isinme(AZScene):
    MID_EXAMPLE = (4, 2, 6)       # MID_POINTS[4] = MID_POINTS[2] və [6]-nın orta nöqtəsi
    AX_ORIGIN = (-6.8, -2.3)      # nazik koordinat oxlarının başlanğıcı (ekranda)
    # Məsələ 2 isbatı üçün böyük 4 nöqtəlik diaqram (solda; düsturlar sağda)
    BIG_R1, BIG_B1 = (-6.3, 1.9), (-2.4, -2.0)
    BIG_R2, BIG_B2 = (-6.1, -1.6), (-2.0, 2.3)
    P2_COL_LEFT = -0.7            # Məsələ 2 isbatında düsturların sol kənarı

    def construct(self):
        section_title(self, "2. İsinmə: ekstremal prinsip")
        self.key_idea()
        self.problem1()
        self.problem2()
        self.summary()
        end_section(self)

    # --- "Əsas fikir" kartı ---------------------------------------------------
    def key_idea(self):
        box = problem_box([
            "Sonlu çoxluqda həmişə ən kiçik (ən böyük) element var",
            "Ən ekstremal obyekti seçirik",
            "İddia yanlış olsaydı, ondan da ekstremal obyekt tapılardı — ziddiyyət",
        ], kind="fikir", size=36)
        show_box(self, box)
        self.wait(WAIT_STEP)
        self.play(FadeOut(box), run_time=T_ANIM)

    # --- Məsələ 1: orta nöqtələr ----------------------------------------------
    def problem1(self):
        box = problem_box([
            "Sonlu $S$ çoxluğunun hər nöqtəsi $S$-in başqa iki nöqtəsinin orta nöqtəsi "
            "ola bilməz",
        ], kind="masala", size=36, header="Məsələ 1")
        show_box(self, box)
        self.play(box.animate.scale(0.62).to_corner(UR, buff=0.3), run_time=T_ANIM)

        o = P2(*self.AX_ORIGIN)
        axes = VGroup(
            Arrow(o + 0.3 * LEFT, P2(2.3, o[1]), buff=0, stroke_width=2, color=C_DIM,
                  max_tip_length_to_length_ratio=0.02),
            Arrow(o + 0.3 * DOWN, P2(o[0], 2.95), buff=0, stroke_width=2, color=C_DIM,
                  max_tip_length_to_length_ratio=0.03),
        )
        ax_lab = VGroup(make_label("x", P2(2.3, o[1]), DOWN, color=C_DIM, size=30),
                        make_label("y", P2(o[0], 2.95), LEFT, color=C_DIM, size=30))
        pts = [P2(*p) for p in MID_POINTS]
        dots = VGroup(*[make_dot(p) for p in pts])
        self.play(Create(axes), FadeIn(ax_lab), run_time=T_ANIM)
        self.play(LaggedStart(*[GrowFromCenter(d) for d in dots], lag_ratio=0.15),
                  run_time=T_ANIM)
        self.wait(WAIT_STEP)

        # nümunə: bir nöqtə iki nöqtənin orta nöqtəsidir
        im, ix, iy = self.MID_EXAMPLE
        assert np.allclose(pts[im], (pts[ix] + pts[iy]) / 2)
        seg = Line(pts[ix], pts[iy], color=C_TEXT2, stroke_width=3)
        tick = Line(UP * 0.14, DOWN * 0.14, color=C_TEXT, stroke_width=4).rotate(
            angle_of_vector(pts[iy] - pts[ix])).move_to(pts[im])
        lbl = VGroup(make_label("X", pts[ix], UL, size=34), make_label("Y", pts[iy], DR, size=34),
                     make_label("M", pts[im], UR, size=34))
        self.play(Create(seg), FadeIn(lbl[:2]), run_time=T_ANIM)
        self.play(FadeIn(tick, scale=2), FadeIn(lbl[2]), Indicate(dots[im], color=C_TEXT),
                  run_time=T_ANIM)
        caption(self, "$M$ — $X$ və $Y$-in orta nöqtəsidir")
        self.play(FadeOut(VGroup(seg, tick, lbl)), run_time=T_ANIM)

        # ən sol nöqtə: şaquli qırıq xətt soldan sağa sürüşür
        xmin = min(p[0] for p in pts)
        tr = ValueTracker(o[0] - 0.4)
        vline = always_redraw(lambda: DashedLine(P2(tr.get_value(), o[1] - 0.25),
                                                 P2(tr.get_value(), 2.95), color=C_TEXT2,
                                                 stroke_width=2.5, dash_length=0.12))
        caption(self, "Ən sol nöqtəni seçək")
        self.add(vline)
        self.play(tr.animate.set_value(xmin), run_time=T_SLOW, rate_func=linear)
        tied = [i for i, p in enumerate(pts) if abs(p[0] - xmin) < 1e-9]
        self.play(*[Indicate(dots[i], color=C_TEXT, scale_factor=1.5) for i in tied],
                  run_time=T_ANIM)
        caption(self, "Bərabərlik olarsa — onlardan ən aşağısını")
        ymin = min(pts[i][1] for i in tied)
        tr2 = ValueTracker(o[1] - 0.3)
        hline = always_redraw(lambda: DashedLine(P2(o[0] - 0.25, tr2.get_value()),
                                                 P2(2.2, tr2.get_value()), color=C_TEXT2,
                                                 stroke_width=2.5, dash_length=0.12))
        self.add(hline)
        self.play(tr2.animate.set_value(ymin), run_time=T_SLOW, rate_func=linear)
        i_m = [i for i in tied if abs(pts[i][1] - ymin) < 1e-9][0]
        M = pts[i_m]
        self.play(dots[i_m].animate.set_color(C_MIN).scale(1.3), run_time=T_ANIM)
        m_lab = make_label(r"M=(x_0,\, y_0)", M, DR, color=C_MIN, size=34)
        self.play(Write(m_lab), run_time=T_ANIM)
        self.play(FadeOut(hline), run_time=1.5)
        self.wait(WAIT_STEP)
        vline.clear_updaters()

        # fərziyyə: M = (X + Y)/2
        caption(self, "Fərz edək ki, $M$ hansısa $X$ və $Y$-in orta nöqtəsidir")
        dvec = P2(1.4, 1.1)
        X0, Y0 = M + dvec, M - dvec
        s = ValueTracker(1.0)
        Xd = always_redraw(lambda: make_dot(M + s.get_value() * dvec))
        Yd = always_redraw(lambda: make_dot(M - s.get_value() * dvec))
        XY = always_redraw(lambda: Line(M - s.get_value() * dvec, M + s.get_value() * dvec,
                                        color=C_TEXT2, stroke_width=3))
        Xl = always_redraw(lambda: make_label("X", M + s.get_value() * dvec, UR, size=34))
        Yl = always_redraw(lambda: make_label("Y", M - s.get_value() * dvec, LEFT, size=34))
        self.play(Create(XY), FadeIn(Xd), FadeIn(Yd), FadeIn(Xl), FadeIn(Yl),
                  run_time=T_ANIM)
        self.bring_to_front(dots[i_m])
        zone = Rectangle(width=xmin - (o[0] - 0.3), height=2.95 - (o[1] - 0.25),
                         stroke_width=0, fill_color=C_MIN, fill_opacity=0.18)
        zone.move_to(P2((xmin + o[0] - 0.3) / 2, (2.95 + o[1] - 0.25) / 2))
        self.play(FadeIn(zone), run_time=T_ANIM)
        caption(self, "$S$-in bütün nöqtələri qırıq xəttin sağında və ya üzərindədir")

        f1 = az_math("x_0", "=", r"{x_1 + x_2", r"\over", "2}", size=FS_FORMULA)
        f2 = az_math("x_1", r"\ge", "x_0", r",\quad", "x_2", r"\ge", "x_0", size=FS_FORMULA)
        f3 = az_math(r"\Rightarrow\;", "x_1", "=", "x_2", "=", "x_0", size=FS_FORMULA)
        f4 = az_texp("Eynilə: ", "$y_1 = y_2 = y_0$", size=FS_FORMULA - 4)
        f5 = az_math(r"\Rightarrow\;", "X", "=", "Y", "=", "M", size=FS_FORMULA)
        col = VGroup(f1, f2, f3, f4, f5).arrange(DOWN, buff=0.42).move_to(P2(COL_X, 0.35))
        self.play(Write(f1), run_time=T_ANIM)
        self.wait(read_wait("x0 = (x1 + x2)/2") + WAIT_STEP)
        self.play(Write(f2), run_time=T_ANIM)
        caption(self, "$M$ ən sol nöqtədir: $x_1 \\ge x_0$, $x_2 \\ge x_0$")
        tmt(self, VGroup(f1, f2).copy(), f3)
        self.wait(WAIT_STEP)
        self.play(Write(f4), run_time=T_ANIM)
        caption(self, "$x$-lər bərabərdir, $M$ isə onların ən aşağısıdır")
        tmt(self, VGroup(f3, f4).copy(), f5)
        self.wait(WAIT_STEP)
        self.play(s.animate.set_value(0.0), run_time=T_SLOW)
        self.play(Flash(M, color=C_MIN, flash_radius=0.4, line_length=0.3), run_time=1.5)
        red_frame_flash(self)
        caption(self, "Ziddiyyət: $X$ və $Y$ fərqli nöqtələr idi")
        self.play(Circumscribe(f5, color=C_MIN), run_time=T_ANIM)
        self.wait(WAIT_STEP)
        for m in (Xd, Yd, XY, Xl, Yl):
            m.clear_updaters()
        fade_all_but(self)

        # sonsuz hal
        dots_inf = VGroup(*[make_dot(P2(k, 0.2)) for k in range(-6, 7)])
        ell_l = az_math(r"\cdots", size=48).move_to(P2(-6.75, 0.2))
        ell_r = az_math(r"\cdots", size=48).move_to(P2(6.75, 0.2))
        axis = Line(P2(X_L, 0.2), P2(X_R, 0.2), color=C_DIM, stroke_width=2)
        labs = VGroup(*[make_label(f"({k},0)", P2(k, 0.2), DOWN, size=24, color=C_TEXT2,
                                   buff=0.25) for k in (-2, -1, 0, 1, 2)])
        self.play(Create(axis), run_time=T_ANIM)
        self.play(LaggedStart(*[GrowFromCenter(d) for d in dots_inf], lag_ratio=0.08),
                  FadeIn(ell_l), FadeIn(ell_r), run_time=T_ANIM)
        self.play(FadeIn(labs), run_time=T_ANIM)
        arcs = VGroup()
        for k in range(-5, 6):
            up = (k % 2 == 0)
            a = ArcBetweenPoints(P2(k - 1, 0.2), P2(k + 1, 0.2),
                                 angle=(-PI / 2.2 if up else PI / 2.2),
                                 color=C_TEXT2, stroke_width=2)
            arcs.add(a)
        self.play(LaggedStart(*[Create(a) for a in arcs], lag_ratio=0.12), run_time=T_SLOW)
        caption(self, "Hər nöqtə öz qonşularının orta nöqtəsidir")
        caption(self, "Sonsuz çoxluqda iddia yanlışdır: ən sol nöqtə yoxdur")
        tr3 = ValueTracker(6.6)
        sweep = always_redraw(lambda: DashedLine(P2(tr3.get_value(), -1.3),
                                                 P2(tr3.get_value(), 1.9), color=C_TEXT2,
                                                 stroke_width=2.5, dash_length=0.12))
        self.add(sweep)
        self.play(tr3.animate.set_value(X_L - 0.3), run_time=4.5, rate_func=linear)
        sweep.clear_updaters()
        self.remove(sweep)
        self.wait(WAIT_STEP)
        fade_all_but(self)

    # --- Məsələ 2: kəsişməyən cütləşmə -----------------------------------------
    def problem2(self):
        box = problem_box([
            "$n$ qırmızı və $n$ göy nöqtə, heç üç nöqtə bir xətt üzərində deyil.",
            "Nöqtələri kəsişməyən parçalarla qırmızı–göy cütlərə ayırmaq olar",
        ], kind="masala", size=36, header="Məsələ 2")
        show_box(self, box)
        self.play(FadeOut(box), run_time=T_ANIM)

        R = [P2(*p) for p in MATCH_RED]
        B = [P2(*p) for p in MATCH_BLUE]
        assert no_three_collinear(R + B, tol=0.2), "Məsələ 2: üç nöqtə bir xətt üzərindədir"
        rdots = VGroup(*[make_dot(p, color=C_RED_PT, r=0.1) for p in R])
        bdots = VGroup(*[make_dot(p, color=C_BLUE_PT, r=0.1) for p in B])
        self.play(LaggedStart(*[GrowFromCenter(d) for d in [*rdots, *bdots]], lag_ratio=0.1),
                  run_time=T_ANIM)

        # bütün 4! cütləşmənin cəmləri (numpy)
        perms = list(itertools.permutations(range(4)))
        sums = {pm: float(sum(np.linalg.norm(R[i] - B[pm[i]]) for i in range(4)))
                for pm in perms}

        def crossings(pm):
            out = []
            for i, j in itertools.combinations(range(4), 2):
                if segments_cross(R[i], B[pm[i]], R[j], B[pm[j]]):
                    out.append(intersect(R[i], B[pm[i]], R[j], B[pm[j]]))
            return out

        best = min(perms, key=lambda pm: sums[pm])
        by_cross = sorted(perms, key=lambda pm: (-len(crossings(pm)), sums[pm]))
        shown = []
        for pm in by_cross:
            if len(shown) == 4:
                break
            if pm != best and all(len(crossings(pm)) != len(crossings(q)) or
                                  abs(sums[pm] - sums[q]) > 1.0 for q in shown):
                shown.append(pm)

        def seg_group(pm, color=C_SEG):
            return VGroup(*[Line(R[i], B[pm[i]], color=color, stroke_width=4)
                            for i in range(4)])

        def cross_marks(pm):
            return VGroup(*[Circle(radius=0.13, color=C_MIN, stroke_width=4).move_to(x)
                            for x in crossings(pm)])

        lab = az_tex("Uzunluqlar cəmi:", size=FS_NOTE)
        num = DecimalNumber(sums[shown[0]], num_decimal_places=2, font_size=FS_NOTE + 4)
        total = VGroup(lab, num).arrange(RIGHT, buff=0.2).move_to(P2(COL_X, 2.85))
        segs = seg_group(shown[0])
        marks = cross_marks(shown[0])
        self.play(LaggedStart(*[Create(s) for s in segs], lag_ratio=0.2), run_time=T_ANIM)
        self.bring_to_front(rdots, bdots)
        self.play(FadeIn(total), run_time=T_ANIM)
        self.play(LaggedStart(*[Create(m) for m in marks], lag_ratio=0.2), run_time=T_ANIM)
        caption(self, "Kəsişən parçalar — qırmızı dairələr")
        for pm in shown[1:]:
            new_segs = seg_group(pm)
            new_marks = cross_marks(pm)
            self.play(Transform(segs, new_segs), FadeOut(marks),
                      ChangeDecimalToValue(num, sums[pm]), run_time=T_ANIM)
            self.bring_to_front(rdots, bdots)
            marks = new_marks
            if len(marks):
                self.play(LaggedStart(*[Create(m) for m in marks], lag_ratio=0.2),
                          run_time=1.5)
            self.wait(WAIT_STEP)

        caption(self, "Cütləşmələr sonludur: $n!$ üsul")
        lo, hi = np.floor(min(sums.values())) - 1, np.ceil(max(sums.values())) + 1
        nl = NumberLine(x_range=[lo, hi, 2], length=4.2, color=C_DIM, stroke_width=2,
                        include_numbers=True, font_size=22, tick_size=0.06)
        nl.move_to(P2(COL_X, 1.45))
        nl_lab = az_tex("$4! = 24$ cəm", size=FS_NOTE - 4, color=C_TEXT2).next_to(nl, UP, 0.35)
        sdots = VGroup(*[make_dot(nl.n2p(sums[pm]), r=0.05) for pm in perms])
        self.play(Create(nl), FadeIn(nl_lab), run_time=T_ANIM)
        self.play(LaggedStart(*[GrowFromCenter(d) for d in sdots], lag_ratio=0.05),
                  run_time=T_ANIM)
        i_best = perms.index(best)
        self.play(sdots[i_best].animate.set_color(C_NEW).scale(1.6), run_time=1.5)
        self.play(Circumscribe(sdots[i_best], shape=Circle, color=C_NEW, buff=0.1),
                  run_time=T_ANIM)
        caption(self, "Uzunluqlar cəmi ən kiçik olan cütləşməni seçək")
        self.play(Transform(segs, seg_group(best)), FadeOut(marks),
                  ChangeDecimalToValue(num, sums[best]), run_time=T_ANIM)
        self.bring_to_front(rdots, bdots)
        self.wait(WAIT_STEP)
        caption(self, "İddia: onda heç bir iki parça kəsişmir")
        fade_all_but(self)
        self.proof2()

    def proof2(self):
        R1, B1, R2, B2 = (P2(*p) for p in (self.BIG_R1, self.BIG_B1, self.BIG_R2, self.BIG_B2))
        assert no_three_collinear([R1, B1, R2, B2], tol=0.5)
        O = intersect(R1, B1, R2, B2)
        dots = VGroup(make_dot(R1, C_RED_PT, 0.11), make_dot(B1, C_BLUE_PT, 0.11),
                      make_dot(R2, C_RED_PT, 0.11), make_dot(B2, C_BLUE_PT, 0.11))
        labs = VGroup(make_label("R_1", R1, UL, size=36), make_label("B_1", B1, DR, size=36),
                      make_label("R_2", R2, DL, size=36), make_label("B_2", B2, UR, size=36))
        s11 = Line(R1, B1, color=C_SEG, stroke_width=4)
        s22 = Line(R2, B2, color=C_SEG, stroke_width=4)
        o_mark = Circle(radius=0.13, color=C_MIN, stroke_width=4).move_to(O)
        o_lab = make_label("O", O, RIGHT, size=36, buff=0.22)
        caption(self, "Fərz edək ki, $R_1B_1$ və $R_2B_2$ parçaları $O$ nöqtəsində kəsişir")
        self.play(GrowFromCenter(dots), FadeIn(labs), run_time=T_ANIM)
        self.play(Create(s11), Create(s22), run_time=T_ANIM)
        self.bring_to_front(dots)
        self.play(Create(o_mark), Write(o_lab), run_time=T_ANIM)
        self.wait(WAIT_STEP)

        # O daxili nöqtədir: kiçik əlavə şəkil
        caption(self, "$O$ parçaların daxili nöqtəsidir")
        inset_c = P2(3.6, 0.4)
        k = 0.42
        mp = lambda p: inset_c + k * (p - (R1 + B1 + R2 + B2) / 4)
        frame = RoundedRectangle(width=4.2, height=3.4, corner_radius=0.12,
                                 color=C_DIM, stroke_width=2).move_to(inset_c)
        r1 = ValueTracker(0.0)
        r1_target = foot_of_perpendicular(R1, R2, B2) * 0 + (R2 + 0.3 * (B2 - R2))
        r1_pos = lambda: mp(R1 + r1.get_value() * (r1_target - R1))
        mini = VGroup(
            Line(mp(R2), mp(B2), color=C_SEG, stroke_width=3),
            make_dot(mp(R2), C_RED_PT, 0.07), make_dot(mp(B2), C_BLUE_PT, 0.07),
            make_dot(mp(B1), C_BLUE_PT, 0.07),
        )
        mini_r1 = always_redraw(lambda: VGroup(
            Line(r1_pos(), mp(B1), color=C_SEG, stroke_width=3),
            make_dot(r1_pos(), C_RED_PT, 0.07)))
        self.play(Create(frame), FadeIn(mini), FadeIn(mini_r1), run_time=T_ANIM)
        self.play(r1.animate.set_value(1.0), run_time=T_SLOW)
        mini_r1.clear_updaters()
        coll = full_line(mp(R2), mp(B2), box=(frame.get_left()[0] + 0.1,
                                               frame.get_right()[0] - 0.1,
                                               frame.get_bottom()[1] + 0.1,
                                               frame.get_top()[1] - 0.1),
                         color=C_MIN, width=3)
        x = cross_mark(size=64).next_to(frame, DOWN, buff=0.12)
        self.play(Create(coll), run_time=T_ANIM)
        self.play(Write(x), run_time=T_ANIM)
        caption(self, "Əks halda üç nöqtə bir xətt üzərində olardı")
        self.play(FadeOut(VGroup(frame, mini, mini_r1, coll, x)), run_time=T_ANIM)

        # cütləri dəyişirik
        caption(self, "Cütləri dəyişək: $R_1B_2$ və $R_2B_1$")
        s12 = Line(R1, B2, color=C_NEW, stroke_width=5)
        s21 = Line(R2, B1, color=C_NEW, stroke_width=5)
        self.play(s11.animate.set_stroke(opacity=0.25), s22.animate.set_stroke(opacity=0.25),
                  run_time=T_ANIM)
        self.play(Create(s12), Create(s21), run_time=T_ANIM)
        self.bring_to_front(dots)
        self.wait(WAIT_STEP)

        # üçbucaq bərabərsizliyi
        path1 = VMobject(color=C_POINT, stroke_width=6).set_points_as_corners([R1, O, B2])
        path2 = VMobject(color=C_POINT, stroke_width=6).set_points_as_corners([R2, O, B1])
        caption(self, "Düz yol — ən qısa yol")
        self.play(Create(path1), run_time=T_ANIM)
        self.play(Indicate(s12, color=C_NEW, scale_factor=1.05), run_time=T_ANIM)
        f1 = az_math("R_1B_2", r"\le", "R_1O", "+", "OB_2", size=FS_FORMULA_S)
        f2 = az_math("R_2B_1", r"\le", "R_2O", "+", "OB_1", size=FS_FORMULA_S)
        f3 = az_math("R_1B_2", "+", "R_2B_1", r"\le", "(", "R_1O", "+", "OB_1", ")", "+",
                     "(", "R_2O", "+", "OB_2", ")", size=FS_FORMULA_S)
        f4 = az_math("R_1B_2", "+", "R_2B_1", r"\le", "R_1B_1", "+", "R_2B_2",
                     size=FS_FORMULA_S)
        f5 = az_math("R_1B_2", "+", "R_2B_1", "<", "R_1B_1", "+", "R_2B_2",
                     size=FS_FORMULA_S)
        left = self.P2_COL_LEFT
        f1.move_to(P2(0, 2.5), aligned_edge=LEFT).set_x(left, LEFT)
        f2.move_to(P2(0, 1.75)).set_x(left, LEFT)
        fitw(f3, X_R - left - 0.3).move_to(P2(0, 0.55)).set_x(left, LEFT)
        f4.move_to(P2(0, -0.85)).set_x(left, LEFT)
        f5.move_to(f4)
        self.play(Write(f1), run_time=T_ANIM)
        self.wait(WAIT_STEP)
        self.play(FadeOut(path1), Create(path2), run_time=T_ANIM)
        self.play(Indicate(s21, color=C_NEW, scale_factor=1.05), run_time=T_ANIM)
        self.play(Write(f2), run_time=T_ANIM)
        self.wait(WAIT_STEP)
        self.play(FadeOut(path2), run_time=1.5)
        tmt(self, VGroup(f1, f2).copy(), f3)
        self.wait(WAIT_STEP)
        # O nöqtəsi R1B1 və R2B2 üzərindədir
        br1 = Brace(VGroup(*f3[4:9]), DOWN, buff=0.08, color=C_TEXT2)
        br2 = Brace(VGroup(*f3[10:15]), DOWN, buff=0.08, color=C_TEXT2)
        bl1 = az_math("R_1B_1", size=34).next_to(br1, DOWN, buff=0.08)
        bl2 = az_math("R_2B_2", size=34).next_to(br2, DOWN, buff=0.08)
        self.play(s11.animate.set_stroke(opacity=1.0), run_time=1.5)
        self.play(GrowFromCenter(br1), Write(bl1), Indicate(s11, color=C_TEXT),
                  run_time=T_ANIM)
        self.play(s22.animate.set_stroke(opacity=1.0), run_time=1.5)
        self.play(GrowFromCenter(br2), Write(bl2), Indicate(s22, color=C_TEXT),
                  run_time=T_ANIM)
        caption(self, "$O$ hər iki parçanın üzərindədir")
        tmt(self, VGroup(f3.copy(), bl1, bl2), f4)
        self.play(FadeOut(br1), FadeOut(br2), s11.animate.set_stroke(opacity=0.25),
                  s22.animate.set_stroke(opacity=0.25), run_time=T_ANIM)
        self.wait(WAIT_STEP)

        # bərabərlik halı
        caption(self, "Bərabərlik yalnız $R_1$, $O$, $B_2$ bir xətt üzərində olduqda")
        ghost = full_line(R1, B1, color=C_MIN, width=2.5, box=(-7.0, 2.3, -2.7, 3.2))
        dashed = DashedVMobject(ghost, num_dashes=40)
        b2_on = R1 + 1.35 * (O - R1)
        b2_ghost = make_dot(b2_on, C_BLUE_PT, 0.11)
        self.play(Create(dashed), run_time=T_ANIM)
        self.play(TransformFromCopy(dots[3], b2_ghost), run_time=T_ANIM)
        trio = VGroup(dots[0], dots[1], b2_ghost)
        self.play(*[Indicate(d, color=C_MIN, scale_factor=1.6) for d in trio], run_time=T_ANIM)
        x = cross_mark(size=72).move_to(b2_on + P2(0.55, 0.35))
        self.play(Write(x), run_time=T_ANIM)
        caption(self, "Onda $R_1$, $B_1$, $B_2$ bir xətt üzərində olardı — bu, şərtə ziddir")
        self.play(FadeOut(VGroup(dashed, b2_ghost, x)), run_time=T_ANIM)
        caption(self, "Bərabərsizlik ciddidir")
        tmt(self, f4, f5)
        frame5 = SurroundingRectangle(f5, color=C_NEW, buff=0.15)
        self.play(Create(frame5), run_time=T_ANIM)
        caption(self, "Yeni cütləşmə daha qısadır — ziddiyyət")
        self.play(Flash(O, color=C_MIN, flash_radius=0.5, line_length=0.35), run_time=1.5)
        red_frame_flash(self)
        self.wait(WAIT_STEP)
        fade_all_but(self)

    # --- Yekun sxem -----------------------------------------------------------
    def summary(self):
        clear_caption(self)
        texts = ["Ekstremal konfiqurasiyanı seç",
                 r"``Pis'' xüsusiyyət varsa,\\onu yaxşılaşdır",
                 "Ziddiyyət"]
        colors = [C_MIN, C_NEW, C_MIN]
        blocks = VGroup()
        for t, c in zip(texts, colors):
            tx = az_tex(t, size=34)
            rect = SurroundingRectangle(tx, buff=0.3, corner_radius=0.12, color=c,
                                        stroke_width=3)
            blocks.add(VGroup(rect, tx))
        blocks.arrange(RIGHT, buff=1.0).move_to(UP * 0.4)
        if blocks.width > FW - 0.8:
            blocks.scale_to_fit_width(FW - 0.8)
        arrows = VGroup(*[Arrow(blocks[i].get_right(), blocks[i + 1].get_left(), buff=0.12,
                                color=C_TEXT2, stroke_width=4) for i in range(2)])
        self.play(FadeIn(blocks[0], shift=0.2 * UP), run_time=T_ANIM)
        for i in range(2):
            self.play(GrowArrow(arrows[i]), run_time=1.5)
            self.play(FadeIn(blocks[i + 1], shift=0.2 * UP), run_time=T_ANIM)
        self.wait(read_wait(texts))
        caption(self, "Bu sxem sonrakı bütün isbatlarda olacaq")


# ─────────────────────────────────────────────────────────────────────────────
#  Hisse02 — 3. Silvester–Qallai teoremi, Kellinin isbatı (≈5 dəq)
# ─────────────────────────────────────────────────────────────────────────────
class Hisse02_Silvester(AZScene):
    def construct(self):
        section_title(self, "3. Silvester–Qallai teoremi")
        self.theorem()
        self.history()
        self.terms()
        kelly_proof(self, "points")
        self.teacher_note()
        self.alternative()
        end_section(self)

    def theorem(self):
        box = problem_box([
            "Müstəvidə sonlu sayda nöqtə verilmişdir.",
            "İstənilən ikisindən keçən xətt daha bir nöqtəni də saxlayır.",
            "İsbat edin ki, bütün nöqtələr bir xətt üzərindədir.",
        ], kind="teorem", size=38)
        show_box(self, box)
        self.wait(WAIT_STEP)
        self.play(FadeOut(box), run_time=T_ANIM)

    def history(self):
        line = Line(P2(-5.6, 0.4), P2(5.6, 0.4), color=C_DIM, stroke_width=3)
        self.play(Create(line), run_time=T_ANIM)
        events = [(-4.2, "1893", ["Silvester sual verir"]),
                  (0.0, "1940-cı illər", ["ilk isbatlar (Qallai)"]),
                  (4.2, "1948", ["Kellinin qısa isbatı", "(Koksterin məqaləsində)"])]
        for x, year, desc in events:
            d = make_dot(P2(x, 0.4), color=C_POINT, r=0.1)
            y = az_tex(r"\textbf{" + year + "}", size=36, color=C_POINT).next_to(d, UP, 0.3)
            t = para(desc, size=32, align=ORIGIN).next_to(d, DOWN, 0.35)
            self.play(GrowFromCenter(d), Write(y), FadeIn(t, shift=0.1 * UP), run_time=T_ANIM)
            self.wait(2.0)
        self.wait(WAIT_STEP)
        fade_all_but(self)

    def terms(self):
        # birləşdirici xətt
        box_l = (-6.9, -0.6, -2.4, 2.9)
        a, b = P2(-5.2, -1.0), P2(-2.3, 0.9)
        l1 = full_line(a, b, box=box_l, avoid=None)
        d1 = VGroup(make_dot(a), make_dot(b))
        t1 = az_tex("birləşdirici xətt", size=34).move_to(P2(-3.9, 1.9))
        arr1 = Arrow(t1.get_bottom(), a + 0.62 * (b - a), buff=0.12,
                     color=C_TEXT2, stroke_width=3)
        self.play(GrowFromCenter(d1), run_time=T_ANIM)
        self.play(Create(l1), run_time=T_ANIM)
        self.play(Write(t1), GrowArrow(arr1), run_time=T_ANIM)
        self.wait(read_wait("birləşdirici xətt"))
        # nöqtədən xəttə qədər məsafə
        box_r = (0.4, 6.9, -2.4, 2.9)
        m0, m1 = P2(0.8, -1.4), P2(6.5, -0.6)
        X = P2(3.0, 1.1)
        l2 = full_line(m0, m1, box=box_r, avoid=None)
        m_lab = make_label("m", l2.get_end(), UL, color=C_LINE, size=36)
        Xd = make_dot(X)
        X_lab = make_label("X", X, UP, size=36)
        perp = perp_marker(X, m0, m1, color=C_TEXT, size=0.2)
        self.play(Create(l2), FadeIn(m_lab), run_time=T_ANIM)
        self.play(GrowFromCenter(Xd), FadeIn(X_lab), run_time=T_ANIM)
        self.play(Create(perp), run_time=T_ANIM)
        t2 = az_tex(r"$\mathrm{d}(X, m)$ — nöqtədən xəttə qədər məsafə", size=32)
        t2.move_to(P2(3.65, 2.35))
        self.play(Write(t2), run_time=T_ANIM)
        self.wait(read_wait("d(X, m) — nöqtədən xəttə qədər məsafə"))
        self.wait(WAIT_STEP)
        fade_all_but(self)
        clear_caption(self)

    def teacher_note(self):
        clear_caption(self)
        box = problem_box([
            "Ən çox səhv: yeni cütün icazəli olduğunu yoxlamamaq",
            "1) $A$ verilmiş nöqtədirmi?",
            "2) $PB$ birləşdirici xətdirmi?",
            "3) $A$ bu xəttin üzərində deyilmi?",
        ], kind="qeyd", size=38)
        self.play(Create(box.rect), Write(box.head), Write(box.body), run_time=T_ANIM)
        self.wait(6)
        self.play(FadeOut(box), run_time=T_ANIM)

    def alternative(self):
        caption(self, "Alternativ arqument: $PHB$ üçbucağında hündürlük")
        K = canon_points()
        P, H, B = K["P"], K["H"], K["B"]
        ell = full_line(H, B, box=BOX_DIAG, color=C_ELL, width=4)
        pb = full_line(P, B, box=BOX_DIAG, color=C_LINE)
        tri = Polygon(P, H, B, stroke_width=0, fill_color=C_TEXT, fill_opacity=0.1)
        hseg = DashedLine(P, H, color=C_MIN, stroke_width=4, dash_length=0.12)
        dots = VGroup(make_dot(P, C_MIN, 0.1), make_dot(H, C_TEXT, 0.06), make_dot(B))
        labs = VGroup(make_label("P", P, RIGHT + 0.3 * UP, size=36),
                      make_label("H", H, DL, size=36),
                      make_label("B", B, DR, size=36),
                      make_label("h", (P + H) / 2, LEFT, color=C_MIN, size=36))
        ra = right_angle(H, RIGHT, UP, size=0.24, color=C_TEXT2)
        self.play(Create(ell), Create(pb), FadeIn(tri), run_time=T_ANIM)
        self.play(Create(hseg), Create(ra), FadeIn(dots), FadeIn(labs), run_time=T_ANIM)
        FH_ = foot_of_perpendicular(H, P, B)
        alt = DashedLine(H, FH_, color=C_NEW, stroke_width=4, dash_length=0.1)
        alt_ra = right_angle(FH_, B - P, H - FH_, size=0.18, color=C_NEW)
        self.play(Create(alt), Create(alt_ra), run_time=T_ANIM)
        f = az_math(r"\mathrm{d}(H, PB)", "=", r"{PH \cdot HB", r"\over", "PB}",
                    size=FS_FORMULA_S)
        f2 = az_math("<", "PH", "=", "h", size=FS_FORMULA_S)
        f2[3].set_color(C_MIN)
        VGroup(f, f2).arrange(DOWN, buff=0.3).move_to(P2(COL_X, 2.0))
        f2.align_to(f[1], LEFT)
        self.play(Write(f), run_time=T_ANIM)
        self.play(Write(f2), run_time=T_ANIM)
        caption(self, "Hipotenuz katetdən uzundur: $HB < PB$")
        # nöqtə H-dan B-yə hərəkət edir, PB-yə qədər məsafəsi xətti azalır
        t = ValueTracker(0.0)
        X = lambda: H + t.get_value() * (B - H)
        dist_seg = always_redraw(lambda: Line(X(), foot_of_perpendicular(X(), P, B),
                                              color=C_NEW, stroke_width=6))
        xdot = always_redraw(lambda: make_dot(X(), color=C_NEW, r=0.09))
        scale = 1.0 / K_SCALE    # ekran -> riyazi vahid
        num = always_redraw(lambda: DecimalNumber(
            dist_point_line(X(), P, B) * scale, num_decimal_places=2, font_size=36,
            color=C_NEW).move_to(P2(COL_X + 0.5, 0.2)))
        num_lab = az_tex("məsafə:", size=32, color=C_TEXT2).next_to(P2(COL_X, 0.2), LEFT,
                                                                   buff=0.1)
        self.play(FadeOut(alt), FadeOut(alt_ra), FadeIn(dist_seg), FadeIn(xdot), FadeIn(num),
                  FadeIn(num_lab), run_time=1.5)
        self.play(t.animate.set_value(1.0), run_time=4.0, rate_func=linear)
        self.wait(1.0)
        A = K["A"]
        ta = (A[0] - H[0]) / (B[0] - H[0])
        self.play(t.animate.set_value(ta), run_time=T_SLOW)
        alab = make_label("A", A, DL, size=36)
        self.play(FadeIn(alab), Flash(A, color=C_POINT, flash_radius=0.3), run_time=T_ANIM)
        caption(self, "$A$ bu yolun üzərindədir: $\\mathrm{d}(A, PB) \\le "
                      "\\mathrm{d}(H, PB) < h$")
        for m in (dist_seg, xdot, num):
            m.clear_updaters()
        self.wait(WAIT_STEP)


# ─────────────────────────────────────────────────────────────────────────────
#  Hisse03 — 4. Dual məsələ: 20.14 (≈4.5 dəq)
# ─────────────────────────────────────────────────────────────────────────────
class Hisse03_Dual(AZScene):
    # Duallıq cədvəli: sözlər hissələrə bölünüb ki, "nöqtə" və "xət(t)" hissələri
    # TransformMatchingTex ilə yer dəyişsin (qövs boyunca fırlanaraq).
    ROWS = [
        (["sonlu sayda ", "nöqtə"], ["sonlu sayda ", "xətt"]),
        (["iki ", "nöqtədə", "n", " bir ", "xətt", " keçir"],
         ["iki ", "xətt", " bir ", "nöqtədə", " kəsişir"]),
        (["bu ", "xətt", " üçüncü ", "nöqtə", "ni", " saxlayır"],
         ["bu ", "nöqtə", "dən", " üçüncü ", "xətt", " keçir"]),
        (["nöqtə", "lər", " bir ", "xət", "t", " üzərindədir"],
         ["xət", "lər", " bir ", "nöqtə", "dən", " keçir"]),
    ]

    def construct(self):
        section_title(self, "4. Dual məsələ: 20.14")
        self.duality()
        self.terms()
        kelly_proof(self, "lines")
        self.compare()
        end_section(self)

    @staticmethod
    def _row(parts):
        t = az_texp(*parts, size=34)
        for part in t:
            key = re.sub(r"\s", "", part.tex_string)
            if key.startswith("nöqtə"):
                part.set_color(C_POINT)
            elif key.startswith("xət"):
                part.set_color(C_LINE)
        return t

    def _icons(self, k):
        """k-cı sətir üçün kiçik illüstrasiya: (nöqtələr versiyası, xətlər versiyası)."""
        def win(cx):
            return (cx - 1.35, cx + 1.35, -2.45, -1.05)
        cl, cr = -3.6, 3.6
        c_l, c_r = P2(cl, -1.75), P2(cr, -1.75)
        L, Rr = VGroup(), VGroup()
        if k == 0:
            for o in ((-0.9, 0.3), (-0.2, -0.4), (0.5, 0.45), (0.95, -0.25)):
                L.add(make_dot(c_l + P2(*o), r=0.07))
            for o, a in (((-0.6, 0), 70), ((0.1, 0.1), 20), ((0.5, -0.1), 120),
                         ((-0.2, -0.2), 155)):
                Rr.add(line_through(c_r + P2(*o), a, box=win(cr), avoid=None, width=2.5))
        elif k == 1:
            a, b = c_l + P2(-0.7, -0.35), c_l + P2(0.7, 0.35)
            L.add(full_line(a, b, box=win(cl), avoid=None, width=2.5),
                  make_dot(a, r=0.07), make_dot(b, r=0.07))
            Rr.add(line_through(c_r, 25, box=win(cr), avoid=None, width=2.5),
                   line_through(c_r, 140, box=win(cr), avoid=None, width=2.5),
                   make_dot(c_r, r=0.07))
        elif k == 2:
            a, b = c_l + P2(-0.9, -0.3), c_l + P2(0.9, 0.3)
            L.add(full_line(a, b, box=win(cl), avoid=None, width=2.5),
                  make_dot(a, r=0.07), make_dot(b, r=0.07),
                  make_dot(c_l + P2(0.15, 0.05), color=C_NEW, r=0.09))
            Rr.add(line_through(c_r, 25, box=win(cr), avoid=None, width=2.5),
                   line_through(c_r, 140, box=win(cr), avoid=None, width=2.5),
                   line_through(c_r, 82, box=win(cr), avoid=None, width=2.5, color=C_NEW),
                   make_dot(c_r, r=0.07))
        else:
            for t in (-1.0, -0.45, 0.2, 0.8):
                L.add(make_dot(c_l + P2(t, 0.25 * t), r=0.07))
            L.add(full_line(c_l + P2(-1, -0.25), c_l + P2(1, 0.25), box=win(cl), avoid=None,
                            width=2.5, color=C_NEW))
            L.submobjects = L.submobjects[-1:] + L.submobjects[:-1]
            for a in (10, 50, 95, 140):
                Rr.add(line_through(c_r, a, box=win(cr), avoid=None, width=2.5))
            Rr.add(make_dot(c_r, color=C_NEW, r=0.09))
        return L, Rr

    def duality(self):
        hl = az_tex("20.13 (nöqtələr)", size=38, color=C_POINT).move_to(P2(-3.6, 2.65))
        hr = az_tex("20.14 (xətlər)", size=38, color=C_LINE).move_to(P2(3.6, 2.65))
        div = Line(P2(0, 3.0), P2(0, -0.85), color=C_DIM, stroke_width=2)
        ul = Line(P2(-6.6, 2.3), P2(6.6, 2.3), color=C_DIM, stroke_width=2)
        self.play(Write(hl), Create(div), Create(ul), run_time=T_ANIM)
        ys = [1.8, 1.05, 0.3, -0.45]
        lefts = [self._row(l).move_to(P2(-3.6, y)) for (l, _), y in zip(self.ROWS, ys)]
        for t in lefts:
            self.play(Write(t), run_time=T_ANIM)
        self.wait(read_wait([" ".join(l) for l, _ in self.ROWS]))
        self.play(Write(hr), run_time=T_ANIM)
        arrow = az_math(r"\longleftrightarrow", size=60, color=C_TEXT2).move_to(P2(0, -1.75))
        icons = None
        for k, ((lp, rp), y, lt) in enumerate(zip(self.ROWS, ys, lefts)):
            target = self._row(rp).move_to(P2(3.6, y))
            cp = lt.copy()
            self.play(cp.animate.move_to(P2(3.6, y)), lt.animate.set_opacity(0.6),
                      run_time=T_ANIM)
            new_icons = self._icons(k)
            if icons is None:
                self.play(FadeIn(new_icons[0]), FadeIn(arrow), run_time=1.5)
            else:
                self.play(FadeOut(icons[0]), FadeOut(icons[1]), FadeIn(new_icons[0]),
                          run_time=1.5)
            tmt(self, cp, target, path_arc=-PI / 2)
            self.play(FadeIn(new_icons[1]), run_time=1.5)
            icons = new_icons
            self.wait(read_wait(" ".join(rp)))
        self.play(*[t.animate.set_opacity(1) for t in lefts], run_time=1.5)
        caption(self, "Bu uyğunluq duallıq adlanır")
        caption(self, "Müstəvidə iki xətt həmişə kəsişsin deyə, paralel olmama şərti lazımdır")
        caption(self, "Duallığa istinad etmədən 20.14-ü eyni üsulla birbaşa isbat edirik")
        self.wait(WAIT_STEP)
        fade_all_but(self)

    def terms(self):
        c = P2(0, 0.6)
        box = (-3.2, 3.2, -1.2, 2.5)
        l1 = line_through(c, 20, box=box, avoid=None)
        l2 = line_through(c, 125, box=box, avoid=None)
        d = make_dot(c)
        self.play(Create(l1), Create(l2), run_time=T_ANIM)
        self.play(GrowFromCenter(d), Flash(c, color=C_POINT, flash_radius=0.3), run_time=T_ANIM)
        caption(self, "Kəsişmə nöqtəsi — ən azı iki verilmiş xəttin keçdiyi nöqtə")
        l3 = line_through(c, 75, box=box, avoid=None)
        self.play(GrowFromPoint(l3, c), run_time=T_ANIM)
        self.bring_to_front(d)
        caption(self, "Şərtə görə hər kəsişmə nöqtəsindən ən azı üç xətt keçir")
        self.wait(WAIT_STEP)
        fade_all_but(self)
        clear_caption(self)

    def compare(self):
        clear_caption(self)
        s_ = K_SCALE * 0.55
        div = Line(P2(0, 3.3), P2(0, -2.6), color=C_DIM, stroke_width=2)
        boxL = (-6.9, -0.3, 0.8, 3.3)
        boxR = (0.3, 6.9, 0.8, 3.3)
        left = canon_static("points", s_, (-3.55 + 2 * s_, 2.05 + 0.25 * s_), boxL,
                            label_size=24)
        right = canon_static("lines", s_, (3.55 + 2 * s_, 2.05 + 0.25 * s_), boxR,
                             label_size=24)
        self.play(Create(div), FadeIn(left), FadeIn(right), run_time=T_ANIM)
        names = ["Cütlər və məsafələr", "Ən kiçik məsafə: $h$", None,
                 "İki şüa, göyərçin yuvası", "$AB < PB$", "Sahə fəndi: $h' < h$",
                 "Yeni cüt icazəlidir", "Ziddiyyət"]
        third_l = r"$\ell$ üzərində üç nöqtə (şərtdən)"
        third_r = r"$P$-dən üç xətt (şərtdən) $\to$ $\ell$-i üç nöqtədə kəsir"
        y0, dy = 0.45, 0.4
        for i, nm in enumerate(names):
            y = y0 - i * dy
            tl = az_tex(f"{i + 1}. " + (nm or third_l), size=28)
            tr = az_tex(f"{i + 1}. " + (nm or third_r), size=28)
            tl.move_to(P2(-3.55, y))
            tr.move_to(P2(3.55, y))
            if nm is None:
                fl = SurroundingRectangle(tl, color=C_POINT, buff=0.08)
                fr = SurroundingRectangle(tr, color=C_POINT, buff=0.08)
                self.play(FadeIn(tl), FadeIn(tr), Create(fl), Create(fr), run_time=1.5)
            else:
                ml = check_mark(size=32).next_to(tl, LEFT, buff=0.15)
                mr = check_mark(size=32).next_to(tr, LEFT, buff=0.15)
                self.play(FadeIn(tl), FadeIn(tr), FadeIn(ml), FadeIn(mr), run_time=1.5)
        self.wait(read_wait(names[:2] + names[3:] + [third_l, third_r]) * 0.5)
        caption(self, "İki isbat demək olar ki, eynidir")


# ─────────────────────────────────────────────────────────────────────────────
#  Hisse04 — 5. Nəticələr: de Breyn–Erdöş teoremi (≈4 dəq)
# ─────────────────────────────────────────────────────────────────────────────
class Hisse04_Neticeler(AZScene):
    # İnduksiya keçidi üçün 7 nöqtə: üçbucağın təpələri, tərəflərin ortaları, mərkəz
    V1, V2, V3 = (-4.0, -2.3), (3.0, -2.3), (-0.5, 2.6)

    def construct(self):
        section_title(self, "5. Nəticələr")
        self.inverse_form()
        self.theorem_and_examples()
        self.induction()
        self.teacher_note()
        self.dual_box()
        end_section(self)

    # --- Əks forma --------------------------------------------------------------
    def inverse_form(self):
        box = problem_box([
            "Nöqtələr bir xətt üzərində deyilsə, adi xətt var: onun üzərində dəqiq iki "
            "nöqtə var",
            "Xətlər bir nöqtədən keçmirsə, adi nöqtə var: ondan dəqiq iki xətt keçir",
        ], kind="fikir", size=32)
        box.move_to(P2(0, 2.35))
        self.play(Create(box.rect), Write(box.head), run_time=T_ANIM)
        # (1) adi xətt
        self.play(Write(box.body[0]), run_time=T_ANIM)
        bl = (-6.9, -0.3, -2.7, 1.1)
        pts = [P2(-5.8, -2.1), P2(-4.4, -1.4), P2(-3.0, -0.7), P2(-5.3, 0.5), P2(-2.3, -2.25)]
        assert min(dist_point_line(pts[k], pts[3], pts[4]) for k in range(3)) > 0.5
        dots = VGroup(*[make_dot(p) for p in pts])
        three = full_line(pts[0], pts[2], box=bl, avoid=None).set_stroke(opacity=0.45)
        ordl = full_line(pts[3], pts[4], box=bl, avoid=None, color=C_NEW, width=4)
        lab = az_tex("adi xətt", size=32, color=C_NEW).move_to(P2(-3.0, 0.45))
        self.play(LaggedStart(*[GrowFromCenter(d) for d in dots], lag_ratio=0.15),
                  run_time=T_ANIM)
        self.play(Create(three), run_time=T_ANIM)
        self.play(Create(ordl), run_time=T_ANIM)
        self.bring_to_front(dots)
        self.play(Write(lab), Indicate(dots[3], color=C_NEW), Indicate(dots[4], color=C_NEW),
                  run_time=T_ANIM)
        self.wait(read_wait(box.lines[0]))
        # (2) adi nöqtə
        self.play(Write(box.body[1]), run_time=T_ANIM)
        br = (0.3, 6.9, -2.7, 1.1)
        T = P2(2.3, -1.3)
        ls = [(T, dir_deg(a)) for a in (15, 70, 125)] + [(P2(4.6, -1.2), dir_deg(112))]
        lm = VGroup(*[full_line(p, p + d, box=br, avoid=None) for p, d in ls])
        tdot = make_dot(T)
        X = intersect(ls[3][0], ls[3][0] + ls[3][1], ls[0][0], ls[0][0] + ls[0][1])
        xdot = make_dot(X, color=C_NEW, r=0.11)
        others = [intersect(ls[3][0], ls[3][0] + ls[3][1], p, p + d) for p, d in ls[1:3]]
        odots = VGroup(*[make_dot(y) for y in others if in_box(y, br)])
        lab2 = az_tex("adi nöqtə", size=32, color=C_NEW).move_to(X + P2(1.25, -0.45))
        self.play(LaggedStart(*[Create(m) for m in lm], lag_ratio=0.2), run_time=T_ANIM)
        self.play(GrowFromCenter(tdot), FadeIn(odots), run_time=T_ANIM)
        self.play(GrowFromCenter(xdot), Flash(X, color=C_NEW, flash_radius=0.3), Write(lab2),
                  run_time=T_ANIM)
        self.wait(read_wait(box.lines[1]))
        caption(self, "Bu, Silvester–Qallai teoreminin əks formasıdır")
        self.wait(WAIT_STEP)
        fade_all_but(self)
        clear_caption(self)

    # --- de Breyn–Erdöş teoremi və nümunələr ------------------------------------
    def theorem_and_examples(self):
        box = problem_box([
            "Bir xətt üzərində olmayan $n \\ge 3$ nöqtə ən azı $n$ müxtəlif",
            "birləşdirici xətt müəyyən edir",
        ], kind="teorem", size=36, header="de Breyn–Erdöş teoremi")
        show_box(self, box, line_by_line=False)
        self.play(box.animate.scale(0.7).to_edge(UP, buff=0.25).set_x(1.4), run_time=T_ANIM)
        self.thm = box
        grp, num = counter("xətlər:", 0, size=FS_TEXT)
        grp.move_to(P2(5.3, 1.3))
        self.play(FadeIn(grp), run_time=T_ANIM)
        ebox = (-6.9, 2.7, -2.7, 2.15)
        note_pos = P2(5.3, 0.2)

        def run_example(points, order, note, extra_first=None):
            dots = VGroup(*[make_dot(P2(*p)) for p in points])
            self.play(LaggedStart(*[GrowFromCenter(d) for d in dots], lag_ratio=0.15),
                      run_time=T_ANIM)
            lines = VGroup()
            for k, (i, j) in enumerate(order, start=1):
                ln = full_line(P2(*points[i]), P2(*points[j]), box=ebox, avoid=None)
                self.play(Create(ln), ChangeDecimalToValue(num, k), run_time=1.5)
                lines.add(ln)
            self.bring_to_front(dots)
            t = fitw(az_tex(note, size=36), 3.6).move_to(note_pos)
            self.play(Write(t), run_time=T_ANIM)
            self.wait(read_wait(note) + 1.0)
            self.play(FadeOut(dots), FadeOut(lines), FadeOut(t), ChangeDecimalToValue(num, 0),
                      run_time=T_ANIM)

        caption(self, "Üçbucaq: $n = 3$")
        tri = [(-4.5, -2.0), (-0.5, -2.0), (-2.5, 1.5)]
        run_example(tri, [(0, 1), (1, 2), (0, 2)], "$n = 3$: 3 xətt")
        caption(self, "Kvadrat: $n = 4$")
        sq = [(-4.0, -1.9), (-1.0, -1.9), (-1.0, 1.1), (-4.0, 1.1)]
        run_example(sq, [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2), (1, 3)], "$6 \\ge 4$")
        caption(self, "Bərabərlik: 5 nöqtə bir xətt üzərində, biri kənarda")
        near = [(-5.6, -1.8), (-4.4, -1.8), (-3.2, -1.8), (-2.0, -1.8), (-0.8, -1.8),
                (-3.2, 1.5)]
        run_example(near, [(0, 4), (5, 0), (5, 1), (5, 2), (5, 3), (5, 4)],
                    "$1 + (n-1) = n$ — bərabərlik")
        self.play(FadeOut(grp), FadeOut(box), run_time=T_ANIM)
        num.clear_updaters()

    # --- İnduksiya isbatı -----------------------------------------------------
    def induction(self):
        badge = az_tex(r"İnduksiya: $n-1 \Rightarrow n$", size=30, color=C_POINT)
        badge.next_to(self._section, DOWN, aligned_edge=LEFT, buff=0.15)
        self.play(FadeIn(badge), run_time=T_ANIM)
        # baza
        tri = [P2(-2.0, -2.0), P2(2.0, -2.0), P2(0.0, 1.6)]
        tdots = VGroup(*[make_dot(p) for p in tri])
        tl = VGroup(*[full_line(tri[i], tri[j], box=(-5, 5, -2.7, 2.6), avoid=None)
                      for i, j in ((0, 1), (1, 2), (0, 2))])
        self.play(GrowFromCenter(tdots), run_time=T_ANIM)
        self.play(LaggedStart(*[Create(l) for l in tl], lag_ratio=0.3), run_time=T_ANIM)
        caption(self, "Baza: $n = 3$ — üçbucağın təpələri 3 xətt verir")
        self.wait(WAIT_STEP)
        self.play(FadeOut(tdots), FadeOut(tl), run_time=T_ANIM)

        # keçid: 7 nöqtə
        V1, V2, V3 = (P2(*v) for v in (self.V1, self.V2, self.V3))
        M1, M2, M3 = (V2 + V3) / 2, (V1 + V3) / 2, (V1 + V2) / 2
        G = (V1 + V2 + V3) / 3
        S = [V1, V2, V3, M1, M2, M3, G]
        iA, iB = 4, 3                        # adi xətt: M2M1
        caption(self, "Keçid: $n$ nöqtə, bir xətt üzərində deyil")
        dots = VGroup(*[make_dot(p) for p in S])
        cl = connecting_lines(S)
        lines = VGroup(*[full_line(S[i], S[j]).set_stroke(opacity=0.35) for i, j, _ in cl])
        self.play(LaggedStart(*[GrowFromCenter(d) for d in dots], lag_ratio=0.1),
                  run_time=T_ANIM)
        self.play(LaggedStart(*[Create(l) for l in lines], lag_ratio=0.1), run_time=T_ANIM)
        self.bring_to_front(dots)
        caption(self, "Silvester–Qallai: adi xətt var")
        k_ord = [n for n, (_, _, on) in enumerate(cl) if on == frozenset({iA, iB})][0]
        ordl = full_line(S[iA], S[iB], color=C_NEW, width=5)
        la = make_label("A", S[iA], UL, size=36)
        lb = make_label("B", S[iB], UR, size=36)
        self.play(Create(ordl), FadeOut(lines[k_ord]), run_time=T_ANIM)
        self.bring_to_front(dots)
        self.play(Write(la), Write(lb), Indicate(dots[iA], color=C_NEW),
                  Indicate(dots[iB], color=C_NEW), run_time=T_ANIM)
        caption(self, "$A$ nöqtəsini ataq: $S' = S \\setminus \\{A\\}$")
        ghost = DashedVMobject(Circle(radius=0.17, color=C_DIM, stroke_width=2),
                               num_dashes=12).move_to(S[iA])
        aside = S[iA] + P2(-1.0, 0.9)
        self.play(dots[iA].animate.set_color(C_DIM).move_to(aside),
                  la.animate.set_color(C_DIM).next_to(aside, UL, buff=0.1),
                  ordl.animate.set_stroke(opacity=0.25), FadeIn(ghost), run_time=T_ANIM)
        self.wait(WAIT_STEP)

        # ekran ikiyə bölünür: solda Hal 1, sağda Hal 2
        rbox = (0.3, 6.95, -1.75, 2.05)
        ctr = (V1 + V2 + V3) / 3 + 0.35 * UP
        k = 0.48
        mp = lambda p: P2(3.65, -0.1) + k * (p - ctr)
        S2 = [mp(p) for p in S]
        new_dots = VGroup(*[make_dot(q, r=0.07) for q in S2])
        new_dots[iA].set_color(C_DIM).move_to(mp(aside))
        new_lines = VGroup(*[full_line(S2[i], S2[j], box=rbox, avoid=None)
                             .set_stroke(opacity=0.0 if n == k_ord else 0.35)
                             for n, (i, j, _) in enumerate(cl)])
        new_ord = full_line(S2[iA], S2[iB], box=rbox, avoid=None, color=C_NEW, width=4)
        new_ord.set_stroke(opacity=0.25)
        new_ghost = ghost.copy().scale(0.6).move_to(S2[iA])
        nla = make_label("A", mp(aside), UL, size=30, color=C_DIM, buff=0.08)
        nlb = make_label("B", S2[iB], UR, size=30, buff=0.08)
        div = Line(P2(0, 2.55), P2(0, -2.65), color=C_DIM, stroke_width=2)
        self.play(*[Transform(a, b) for a, b in zip(dots, new_dots)],
                  *[Transform(a, b) for a, b in zip(lines, new_lines)],
                  Transform(ordl, new_ord), Transform(ghost, new_ghost), Transform(la, nla),
                  Transform(lb, nlb), Create(div), run_time=T_SLOW)

        # Hal 1 (sol yarı)
        lbox = (-6.95, -0.3, -1.75, 2.05)
        h1 = az_tex("Hal 1", size=32, color=C_POINT).move_to(P2(-3.6, 2.35))
        self.play(Write(h1), run_time=1.5)
        caption(self, "Hal 1: $S'$ bir xətt üzərindədir")
        mx = [-6.2, -5.1, -4.0, -2.9, -1.8, -0.8]
        my = -1.3
        Xs = [P2(x, my) for x in mx]
        A1 = P2(-3.5, 1.4)
        m_line = full_line(Xs[0], Xs[-1], box=lbox, avoid=None)
        m_lab = make_label("m", m_line.get_end(), UL, color=C_LINE, size=34)
        xdots = VGroup(*[make_dot(x, r=0.07) for x in Xs])
        adot = make_dot(A1, r=0.08)
        alab = make_label("A", A1, UP, size=32)
        self.play(GrowFromCenter(xdots), Create(m_line), FadeIn(m_lab), run_time=T_ANIM)
        cnt = az_math("1", size=40).move_to(P2(-3.6, -2.25))
        self.play(Write(cnt), run_time=1.5)
        self.play(GrowFromCenter(adot), FadeIn(alab), run_time=1.5)
        ax_lines = VGroup(*[full_line(A1, x, box=lbox, avoid=None) for x in Xs])
        self.play(LaggedStart(*[Create(l) for l in ax_lines], lag_ratio=0.15), run_time=T_ANIM)
        self.bring_to_front(xdots, adot)
        cnt2 = az_math("1", "+", "(n-1)", size=40).move_to(cnt)
        tmt(self, cnt, cnt2)
        cnt3 = az_math("1", "+", "(n-1)", "=", "n", size=40).move_to(cnt)
        tmt(self, cnt2, cnt3)
        caption(self, "$AX$ xətləri fərqlidir: əks halda $A \\in m$ olardı")
        # iki AX xətti üst-üstə düşsəydi: A m üzərinə sürüşərdi
        at = ValueTracker(0.0)
        Apos = lambda: A1 + at.get_value() * (P2(-3.5, my) - A1)
        two = always_redraw(lambda: VGroup(
            full_line(Apos(), Xs[1], box=lbox, avoid=None, color=C_POINT, width=4),
            full_line(Apos(), Xs[4], box=lbox, avoid=None, color=C_POINT, width=4)))
        amov = always_redraw(lambda: make_dot(Apos(), color=C_POINT, r=0.09))
        self.play(FadeIn(two), FadeIn(amov), ax_lines.animate.set_stroke(opacity=0.2),
                  run_time=1.5)
        self.play(at.animate.set_value(1.0), run_time=T_SLOW)
        x1 = cross_mark(size=60).move_to(P2(-3.5, my) + P2(0.0, 0.55))
        self.play(Write(x1), run_time=T_ANIM)
        self.wait(1.5)
        self.play(at.animate.set_value(0.0), FadeOut(x1), run_time=T_ANIM)
        two.clear_updaters()
        amov.clear_updaters()
        self.play(FadeOut(two), FadeOut(amov), ax_lines.animate.set_stroke(opacity=1.0),
                  run_time=1.5)
        self.bring_to_front(xdots, adot)
        self.wait(WAIT_STEP)

        # Hal 2 (sağ yarı)
        h2 = az_tex("Hal 2", size=32, color=C_POINT).move_to(P2(3.6, 2.35))
        self.play(Write(h2), run_time=1.5)
        caption(self, "Hal 2: induksiya fərziyyəsinə görə $S'$ ən azı $n-1$ xətt verir")
        sp = [q for n, q in enumerate(S2) if n != iA]
        spl = connecting_lines(sp)
        sp_lines = VGroup(*[full_line(sp[i], sp[j], box=rbox, avoid=None) for i, j, _ in spl])
        self.play(*[l.animate.set_stroke(opacity=0.12) for l in lines],
                  LaggedStart(*[Create(l) for l in sp_lines], lag_ratio=0.1), run_time=T_ANIM)
        self.bring_to_front(dots)
        c2 = az_math(r"\ge", "n-1", size=40).move_to(P2(3.6, -2.25))
        self.play(Write(c2), run_time=1.5)
        self.wait(WAIT_STEP)
        # A geri qayıdır, AB adi xətti parlayır
        self.play(dots[iA].animate.set_color(C_POINT).move_to(S2[iA]),
                  la.animate.set_color(C_TEXT).next_to(S2[iA], UL, buff=0.08),
                  FadeOut(ghost), run_time=T_ANIM)
        self.play(ordl.animate.set_stroke(opacity=1.0, width=6), run_time=T_ANIM)
        self.play(Indicate(ordl, color=C_NEW), run_time=T_ANIM)
        self.bring_to_front(dots)
        caption(self, "$AB$ yenidir: üzərində $S'$-in yalnız bir nöqtəsi var ($B$)")
        c3 = az_math(r"\ge", "(n-1)", "+", "1", "=", "n", size=40).move_to(c2)
        tmt(self, c2, c3)
        fin = az_math("(n-1)", "+", "1", "=", "n", size=FS_FORMULA).move_to(P2(0, 3.1))
        fin_box = SurroundingRectangle(fin, color=C_NEW, buff=0.15)
        qed = qed_mark().next_to(fin_box, RIGHT, buff=0.3)
        self.play(TransformFromCopy(c3, fin), run_time=T_ANIM)
        self.play(Create(fin_box), FadeIn(qed), run_time=T_ANIM)
        self.wait(WAIT_STEP + 1.0)
        fade_all_but(self)
        clear_caption(self)

    # --- Müəllim qeydi ----------------------------------------------------------
    def teacher_note(self):
        box = problem_box([
            "İnduksiya adi xətti atmaqla işləyir — ixtiyari nöqtəni atsaq,",
            "yeni xətt zəmanəti olmazdı",
        ], kind="qeyd", size=34).move_to(P2(0, 2.35))
        self.play(Create(box.rect), Write(box.head), Write(box.body), run_time=T_ANIM)
        self.wait(read_wait(box.lines))
        c = P2(-1.0, -0.9)
        g = 0.85
        pts = [c + g * P2(i, j) for j in (-1, 0, 1) for i in (-1, 0, 1)]
        gb = (-4.6, 2.6, -2.7, 1.0)
        dots = VGroup(*[make_dot(p) for p in pts])
        self.play(LaggedStart(*[GrowFromCenter(d) for d in dots], lag_ratio=0.08),
                  run_time=T_ANIM)
        X = pts[4]
        xl = az_math("X", size=32).move_to(
            free_spot(X, [(X, d) for d in (RIGHT, UP, UR, UL)], r=0.32))
        self.play(dots[4].animate.set_color(C_MIN), FadeIn(xl), run_time=1.5)
        ls = VGroup(*[full_line(X, X + d, box=gb, avoid=None)
                      for d in (RIGHT, UP, UR, UL)])
        self.play(LaggedStart(*[GrowFromPoint(l, X) for l in ls], lag_ratio=0.2),
                  run_time=T_ANIM)
        self.bring_to_front(dots)
        caption(self, "İxtiyari $X$ nöqtəsini ataq")
        self.play(dots[4].animate.set_color(C_DIM).scale(0.7), run_time=1.5)
        self.play(*[Indicate(l, color=C_TEXT) for l in ls], run_time=T_ANIM)
        caption(self, "$X$-dən keçən hər xətdə hələ iki nöqtə qalır — yeni xətt yoxdur")
        x = cross_mark(size=80).move_to(P2(3.6, -0.9))
        self.play(Write(x), run_time=T_ANIM)
        self.wait(WAIT_STEP)
        fade_all_but(self)
        clear_caption(self)

    def dual_box(self):
        box = problem_box([
            "Bir nöqtədən keçməyən, cüt-cüt paralel olmayan $n \\ge 3$ xəttin",
            "ən azı $n$ kəsişmə nöqtəsi var",
        ], kind="teorem", size=38, header="Dual teorem")
        show_box(self, box, line_by_line=False)
        caption(self, "Bu — ev tapşırığıdır (həlli videonun sonunda)")


# ─────────────────────────────────────────────────────────────────────────────
#  Hisse05 — 6. Üsul harada işləmir? (≈3 dəq)
# ─────────────────────────────────────────────────────────────────────────────
class Hisse05_Serhedler(AZScene):
    LAT = 0.75                    # tam nöqtələr şəbəkəsinin addımı (ekranda)
    LAT_Y0 = -0.15
    LAT_PAIRS = [((-4, -2), (-2, -1)), ((1, -3), (2, 0)), ((-6, 3), (-3, 2))]
    FF_COLORS = ["#58C4DD", "#FF862F", "#83C167", "#E07A9B"]
    FF_DIRS = [(1, 0), (0, 1), (1, 1), (1, 2)]

    def construct(self):
        section_title(self, "6. Üsul harada işləmir?")
        self.lattice()
        self.finite_field()
        self.complex_card()
        self.modern()
        end_section(self)

    # --- Sonsuz çoxluq: tam nöqtələr şəbəkəsi ---------------------------------
    def lattice(self):
        sp, y0 = self.LAT, self.LAT_Y0
        to_s = lambda ij: P2(sp * ij[0], sp * ij[1] + y0)
        I, J = range(-9, 10), range(-3, 5)
        dots = {(i, j): make_dot(to_s((i, j)), r=0.05) for j in J for i in I}
        grid = VGroup(*dots.values())
        caption(self, "Sonsuz çoxluq: müstəvinin bütün tam nöqtələri, $\\mathbb{Z}^2$")
        self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in grid], lag_ratio=0.004),
                  run_time=T_SLOW)
        box = (X_L, X_R, -2.6, 3.05)
        for n, (X, Y) in enumerate(self.LAT_PAIRS):
            X, Y = np.array(X), np.array(Y)
            d = Y - X
            ks = [k for k in range(-20, 21) if tuple(X + k * d) in dots]
            on = [dots[tuple(X + k * d)] for k in ks]
            big = VGroup(make_dot(to_s(X), r=0.1), make_dot(to_s(Y), r=0.1))
            labs = VGroup()
            if n == 0:
                labs = VGroup(az_math("X", size=34).move_to(to_s(X) + P2(-0.32, sp / 2)),
                              az_math("Y", size=34).move_to(to_s(Y) + P2(-0.32, sp / 2)))
            self.play(GrowFromCenter(big), FadeIn(labs), run_time=1.5)
            ln = full_line(to_s(X), to_s(Y), box=box)
            self.play(Create(ln), run_time=1.5)
            self.play(LaggedStart(*[d_.animate.set_color(C_NEW).scale(1.9) for d_ in on],
                                  lag_ratio=0.25), run_time=T_SLOW)
            if n == 0:
                caption(self, "$X$ və $Y$ tamdırsa, $X + k(Y - X)$ nöqtələri də tamdır")
            if n == 1:
                caption(self, "Hər belə xətt üzərində başqa tam nöqtələr də var — şərt ödənir")
            else:
                self.wait(WAIT_STEP)
            self.play(FadeOut(ln), FadeOut(big), FadeOut(labs),
                      *[d_.animate.set_color(C_POINT).scale(1 / 1.9) for d_ in on],
                      run_time=1.5)
        caption(self, "Amma bütün nöqtələr bir xətt üzərində deyil")
        tri = [to_s((0, 0)), to_s((1, 0)), to_s((0, 1))]
        poly = Polygon(*tri, color=C_NEW, stroke_width=4, fill_color=C_NEW, fill_opacity=0.25)
        self.play(Create(poly), *[dots[k].animate.set_color(C_NEW).scale(1.8)
                                  for k in ((0, 0), (1, 0), (0, 1))], run_time=T_ANIM)
        self.wait(WAIT_STEP)
        caption(self, "Səbəb: cütlər sonsuzdur — ən kiçik məsafə olmaya bilər")
        self.play(FadeOut(grid), FadeOut(poly), run_time=T_ANIM)
        nl = NumberLine(x_range=[0, 1.05, 0.25], length=11, color=C_DIM, stroke_width=2,
                        include_numbers=False, tick_size=0.06).move_to(P2(0, 0.4))
        zero = Circle(radius=0.1, color=C_TEXT, stroke_width=3).move_to(nl.n2p(0))
        nums = VGroup(*[az_math(t, size=32).next_to(nl.n2p(v), DOWN, buff=0.25)
                        for t, v in (("0", 0), ("1", 1), (r"\tfrac12", 0.5),
                                     (r"\tfrac13", 1 / 3), (r"\tfrac14", 0.25))])
        pts = VGroup(*[make_dot(nl.n2p(1 / k), r=0.07) for k in range(1, 41)])
        self.play(Create(nl), FadeIn(nums), run_time=T_ANIM)
        self.play(LaggedStart(*[GrowFromCenter(p) for p in pts], lag_ratio=0.12),
                  run_time=T_SLOW + 1.0)
        self.play(Create(zero), run_time=1.5)
        self.play(Indicate(zero, color=C_MIN, scale_factor=1.6), run_time=T_ANIM)
        note = az_tex("0 heç bir cütün məsafəsi deyil — ən kiçik element yoxdur", size=FS_NOTE,
                      color=C_TEXT2).move_to(P2(0, 1.4))
        self.play(FadeIn(note), run_time=T_ANIM)
        self.wait(read_wait("0 heç bir cütün məsafəsi deyil — ən kiçik element yoxdur"))
        self.wait(WAIT_STEP)
        fade_all_but(self)

    # --- Sonlu cisim: 9 nöqtə ---------------------------------------------------
    def finite_field(self):
        sp = 0.6
        c = P2(-1.2, 0.3)
        to_s = lambda a, b: c + sp * P2(a - 1, b - 1)
        rng = range(-3, 6)
        dots = {}
        for a in rng:
            for b in rng:
                main = (0 <= a <= 2 and 0 <= b <= 2)
                d = make_dot(to_s(a, b), r=0.09 if main else 0.05)
                if not main:
                    d.set_opacity(0.35)
                dots[(a, b)] = d
        frame = Square(side_length=2 * sp + 0.5, color=C_TEXT2, stroke_width=2).move_to(
            to_s(1, 1))
        main = VGroup(*[dots[(a, b)] for a in range(3) for b in range(3)])
        copies = VGroup(*[d for k, d in dots.items() if not (0 <= k[0] <= 2 and 0 <= k[1] <= 2)])
        caption(self, "Sonlu cisim: 9 nöqtə")
        self.play(LaggedStart(*[GrowFromCenter(d) for d in main], lag_ratio=0.1),
                  Create(frame), run_time=T_ANIM)
        caption(self, "Ədədlər: $\\{0, 1, 2\\}$, əməllər 3-ə görə qalıqla")
        caption(self, "``Xətt'' $= \\{X + tV : t = 0, 1, 2\\}$")
        caption(self, "Şəbəkəni yanlara təkrarlayaq: düz xətt qıvrılıb geri qayıdır")
        self.play(FadeIn(copies), run_time=T_ANIM)
        tbox = (to_s(-3, 0)[0] - 0.25, to_s(5, 0)[0] + 0.25,
                to_s(0, -3)[1] - 0.25, to_s(0, 5)[1] + 0.25)
        legend = VGroup()
        for vi, (V, col) in enumerate(zip(self.FF_DIRS, self.FF_COLORS)):
            vx, vy = V
            reps = [(0, 0), (1, 0), (2, 0)] if V == (0, 1) else [(0, 0), (0, 1), (0, 2)]
            caption(self, f"İstiqamət $V = ({vx}, {vy})$: üç paralel ``xətt''")
            drawn = VGroup()
            lit = []
            for X in reps:
                trip = [((X[0] + t * vx) % 3, (X[1] + t * vy) % 3) for t in range(3)]
                ln = full_line(to_s(*X), to_s(X[0] + vx, X[1] + vy), box=tbox, avoid=None,
                               color=col, width=3.5)
                on_line = [k for k in dots
                           if dist_point_line(to_s(*k), to_s(*X), to_s(X[0] + vx, X[1] + vy))
                           < 1e-6]
                self.play(Create(ln), *[dots[k].animate.set_color(col).set_opacity(0.9)
                                        for k in on_line if k not in trip], run_time=1.5)
                self.play(*[dots[k].animate.set_color(col).scale(1.5) for k in trip],
                          run_time=1.5)
                drawn.add(ln)
                lit.append((X, on_line, trip))
            item = az_tex(f"$V = ({vx}, {vy})$: 3 xətt", size=30, color=col)
            legend.add(item)
            item.move_to(P2(4.6, 1.9 - 0.6 * vi))
            self.play(FadeIn(item), run_time=1.5)
            self.wait(WAIT_STEP)
            anims = [FadeOut(drawn)]
            for _, on_line, trip in lit:
                for k in on_line:
                    if k not in trip:
                        anims.append(dots[k].animate.set_color(C_POINT).set_opacity(0.35))
                for k in trip:
                    anims.append(dots[k].animate.set_color(C_POINT).scale(1 / 1.5))
            self.play(*anims, run_time=1.5)
        total = az_tex("cəmi 12 ``xətt''", size=32).move_to(P2(4.6, 1.9 - 0.6 * 4))
        self.play(Write(total), run_time=1.5)
        caption(self, "Hər xətt dəqiq üç nöqtədən ibarətdir, amma 9 nöqtə bir xətt üzərində deyil")
        caption(self, "Burada məsafə və ``arasında olmaq'' anlayışları yoxdur")
        caption(self, "Kellinin isbatı məhz bu anlayışlardan istifadə edir")
        self.wait(WAIT_STEP)
        fade_all_but(self)
        clear_caption(self)

    # --- Kompleks müstəvi ------------------------------------------------------
    def complex_card(self):
        box = problem_box([
            "Kompleks ədədlər üzərində də teorem doğru deyil: Hesse konfiqurasiyası",
            "9 nöqtə, hər birləşdirici xəttdə dəqiq 3 nöqtə",
            "(məsələn, $x^3 + y^3 + z^3 = 0$ əyrisinin 9 dönüş nöqtəsi)",
        ], kind="teorem", size=36, header="Kompleks müstəvi")
        self.play(Create(box.rect), Write(box.head), Write(box.body), run_time=T_ANIM)
        self.wait(8)
        self.play(FadeOut(box), run_time=T_ANIM)

    # --- Müasir nəticələr --------------------------------------------------------
    def modern(self):
        head = az_tex(r"\textbf{Müasir nəticələr}", size=44, color=C_TEXT).move_to(P2(0, 3.0))
        self.play(Write(head), run_time=T_ANIM)
        cards = [
            ["Kelli–Mozer (1958): ən azı $3n/7$ adi xətt"],
            ["Qrin–Tao (2013): kifayət qədər böyük $n$ üçün ən azı $n/2$ adi xətt"],
            ["Motskin–Rabin: rəngli variant — nöqtələr qırmızı və göy;",
             "eyni rəngli iki nöqtənin xəttində başqa rəngli nöqtə var",
             r"$\Rightarrow$ hamısı bir xətt üzərindədir"],
        ]
        y = 2.25
        for n, lines in enumerate(cards):
            body = para(lines, size=34, buff=0.14)
            rect = SurroundingRectangle(body, buff=0.25, corner_radius=0.12, color=C_LINE,
                                        stroke_width=2.5)
            card = VGroup(rect, body)
            card.move_to(P2(0, y), aligned_edge=UP)
            if n == 2:
                card.set_x(-1.3)
            self.play(Create(rect), Write(body), run_time=T_ANIM)
            self.wait(max(6.0, read_wait(lines)))
            y = card.get_bottom()[1] - 0.3
            last = card
        # Motskin–Rabin illüstrasiyası
        c = P2(5.3, last.get_center()[1])
        bx = (3.9, 6.9, c[1] - 1.0, c[1] + 1.0)
        r1, r2 = c + P2(-1.1, -0.55), c + P2(1.0, 0.5)
        bmid = (r1 + r2) / 2
        ill = VGroup(full_line(r1, r2, box=bx, avoid=None, color=C_TEXT2, width=2.5),
                     make_dot(r1, C_RED_PT, 0.1), make_dot(r2, C_RED_PT, 0.1),
                     make_dot(bmid, C_BLUE_PT, 0.1),
                     make_dot(c + P2(-0.6, 0.6), C_BLUE_PT, 0.1),
                     make_dot(c + P2(0.9, -0.6), C_RED_PT, 0.1))
        self.play(FadeIn(ill), run_time=T_ANIM)
        note = az_tex("İsbatı Eyler düsturu tələb edir", size=FS_NOTE, color=C_TEXT2)
        note.next_to(last, DOWN, buff=0.25).align_to(last, LEFT)
        self.play(FadeIn(note), run_time=T_ANIM)
        self.wait(read_wait("İsbatı Eyler düsturu tələb edir") + 2.0)


# ─────────────────────────────────────────────────────────────────────────────
#  Hisse06 — 7. Yekun: xülasə və ev tapşırığı (≈1.5 dəq)
# ─────────────────────────────────────────────────────────────────────────────
class Hisse06_Yekun(AZScene):
    def construct(self):
        section_title(self, "7. Yekun")
        self.scheme()
        caption(self, "Silvester–Qallai teoremi və onun dualı eyni isbata malikdir")
        self.wait(WAIT_STEP)
        fade_all_but(self)
        clear_caption(self)
        self.homework()
        end_section(self, pause=5.0)

    # kiçik ikonalar: (sətir = isbat, sütun = addım), hər biri ~2.2 × 1.0
    @staticmethod
    def icon(row, col, c):
        g = VGroup()
        sc = 0.42
        if col == 3:
            return cross_mark(size=44).move_to(c)
        if row == 0:                                   # orta nöqtə — ən sol nöqtə
            if col == 0:
                pts = [(-0.6, -0.2), (0.1, 0.35), (0.5, -0.3), (0.9, 0.2)]
                g.add(*[make_dot(c + P2(*p), r=0.05) for p in pts])
                g[0].set_color(C_MIN)
                g.add(DashedLine(c + P2(-0.6, -0.5), c + P2(-0.6, 0.5), color=C_TEXT2,
                                 stroke_width=2, dash_length=0.06))
            elif col == 1:
                M = c + P2(-0.3, 0)
                g.add(DashedLine(M + 0.5 * DOWN, M + 0.5 * UP, color=C_TEXT2, stroke_width=2,
                                 dash_length=0.06),
                      Line(M + P2(-0.55, -0.3), M + P2(0.55, 0.3), color=C_TEXT2, stroke_width=2),
                      make_dot(M, C_MIN, 0.05), make_dot(M + P2(0.55, 0.3), r=0.05),
                      make_dot(M + P2(-0.55, -0.3), C_NEW, 0.06))
            else:
                g.add(az_math(r"X, Y \in S", size=26), check_mark(size=30))
                g.arrange(RIGHT, buff=0.12).move_to(c)
        elif row == 1:                                 # cütləşmə — ən qısa cəm
            r1, b1, r2, b2 = (c + sc * P2(*p) for p in ((-1.2, 0.8), (1.2, -0.8),
                                                         (-1.2, -0.8), (1.2, 0.8)))
            dots = [make_dot(r1, C_RED_PT, 0.05), make_dot(b1, C_BLUE_PT, 0.05),
                    make_dot(r2, C_RED_PT, 0.05), make_dot(b2, C_BLUE_PT, 0.05)]
            if col == 0:
                g.add(Line(r1, b1, color=C_SEG, stroke_width=2),
                      Line(r2, b2, color=C_SEG, stroke_width=2),
                      Circle(radius=0.07, color=C_MIN, stroke_width=2).move_to(c), *dots)
            elif col == 1:
                g.add(Line(r1, b2, color=C_NEW, stroke_width=2.5),
                      Line(r2, b1, color=C_NEW, stroke_width=2.5), *dots)
            else:
                g.add(az_tex("qırmızı–göy", size=24), check_mark(size=30))
                g.arrange(RIGHT, buff=0.12).move_to(c)
        else:                                          # Kelli — ən kiçik məsafə
            P, H = c + P2(-0.5, 0.4), c + P2(-0.5, -0.4)
            B = c + P2(0.8, -0.4)
            if col == 0:
                g.add(Line(c + P2(-1.0, -0.4), c + P2(1.0, -0.4), color=C_ELL, stroke_width=2.5),
                      DashedLine(P, H, color=C_MIN, stroke_width=2.5, dash_length=0.06),
                      make_dot(P, C_MIN, 0.05))
            elif col == 1:
                A = c + P2(0.0, -0.4)
                F = foot_of_perpendicular(A, P, B)
                g.add(Line(c + P2(-1.0, -0.4), c + P2(1.0, -0.4), color=C_ELL, stroke_width=2),
                      Line(P, B, color=C_LINE, stroke_width=2),
                      DashedLine(A, F, color=C_NEW, stroke_width=2.5, dash_length=0.06),
                      make_dot(P, C_MIN, 0.05), make_dot(A, r=0.05), make_dot(B, r=0.05))
            else:
                g.add(az_math(r"(A,\, PB)", size=28), check_mark(size=30))
                g.arrange(RIGHT, buff=0.12).move_to(c)
        return g

    def scheme(self):
        texts = [r"1. Ekstremal\\obyekti seç", r"2. Daha kiçiyini\\qur",
                 r"3. İcazəli olduğunu\\yoxla", r"4. Ziddiyyət"]
        colors = [C_MIN, C_NEW, C_LINE, C_MIN]
        xs = [-3.75, -0.75, 2.25, 5.25]
        blocks = VGroup()
        for t, col, x in zip(texts, colors, xs):
            tx = fitw(az_tex(t, size=30), 2.35)
            rect = RoundedRectangle(width=2.6, height=1.15, corner_radius=0.12, color=col,
                                    stroke_width=3)
            blocks.add(VGroup(rect, tx).move_to(P2(x, 2.15)))
        arrows = VGroup(*[Arrow(blocks[i].get_right(), blocks[i + 1].get_left(), buff=0.06,
                                color=C_TEXT2, stroke_width=3, max_tip_length_to_length_ratio=0.4)
                          for i in range(3)])
        rows = ["Orta nöqtə", "Cütləşmə", "Kelli"]
        ys = [0.75, -0.45, -1.65]
        rlabs = VGroup(*[az_tex(r, size=28, color=C_TEXT2).move_to(P2(-6.05, y))
                         for r, y in zip(rows, ys)])
        self.play(FadeIn(rlabs), run_time=T_ANIM)
        for i in range(4):
            if i > 0:
                self.play(GrowArrow(arrows[i - 1]), run_time=1.5)
            self.play(FadeIn(blocks[i], shift=0.2 * DOWN), run_time=T_ANIM)
            icons = [self.icon(r, i, P2(xs[i], ys[r])) for r in range(3)]
            self.play(LaggedStart(*[FadeIn(ic) for ic in icons], lag_ratio=0.3),
                      run_time=T_ANIM)
            self.wait(read_wait(texts[i]))
        self.wait(WAIT_STEP)

    def homework(self):
        head = az_tex(r"\textbf{Ev tapşırığı}", size=48, color=C_POINT).move_to(P2(0, 2.6))
        self.play(Write(head), run_time=T_ANIM)
        items = [
            "1. Dual de Breyn–Erdöş teoremi",
            "2. 20.14-də paralel olmama, 20.13-də sonluluq şərti lazımdır",
            "3. Fəzada Silvester–Qallai teoremi",
            "4. Çevrələr: üç nöqtədən keçən çevrə dördüncü nöqtəni saxlayır "
            "(göstəriş: inversiya)",
        ]
        lst = para(items, size=36, buff=0.45).move_to(P2(0, 0.0))
        fitw(lst, FW - 1.0)
        for mob, t in zip(lst, items):
            self.play(Write(mob), run_time=T_ANIM)
            self.wait(read_wait(t))


# ─────────────────────────────────────────────────────────────────────────────
#  Hisse07 — 8.1. Tapşırıq 1: dual de Breyn–Erdöş (≈2 dəq)
# ─────────────────────────────────────────────────────────────────────────────
class Hisse07_Hell1(AZScene):
    V1, V2, V3 = (-4.0, -2.3), (3.0, -2.3), (-0.5, 2.6)

    def construct(self):
        card = az_tex("8. Həllər", size=FS_TITLE + 8)
        self.play(Write(card), run_time=T_ANIM)
        self.wait(2.0)
        self.play(FadeOut(card), run_time=T_ANIM)
        section_title(self, "8.1. Tapşırıq 1: dual de Breyn–Erdöş")
        box = problem_box([
            "Əks forma (20.14-dən): xətlər bir nöqtədən keçmirsə,",
            "dəqiq iki xəttin keçdiyi nöqtə var",
        ], kind="fikir", size=36)
        show_box(self, box, line_by_line=False)
        self.play(FadeOut(box), run_time=T_ANIM)
        self.base()
        self.step()
        end_section(self)

    def base(self):
        caption(self, "Baza: üç xətt üçbucaq əmələ gətirir — 3 kəsişmə nöqtəsi")
        box = (-5.5, 5.5, -2.7, 3.0)
        A, B, C = P2(-2.5, -1.8), P2(2.5, -1.8), P2(0.2, 2.0)
        la = full_line(A, B, box=box, avoid=None)
        lb = full_line(B, C, box=box, avoid=None)
        sh = ValueTracker(0.0)
        # c xətti öz bucağını saxlayaraq sürüşür: c∩a təpəsi a∩b təpəsinə doğru
        lc = always_redraw(lambda: full_line(A + sh.get_value() * (B - A),
                                             C + sh.get_value() * (B - A),
                                             box=box, avoid=None, color=C_LINE))
        va = always_redraw(lambda: make_dot(A + sh.get_value() * (B - A)))
        vc = always_redraw(lambda: make_dot(intersect(B, C, A + sh.get_value() * (B - A),
                                                      C + sh.get_value() * (B - A))))
        vb = make_dot(B)
        self.play(Create(la), Create(lb), Create(lc), run_time=T_ANIM)
        self.play(GrowFromCenter(va), GrowFromCenter(vb), GrowFromCenter(vc), run_time=T_ANIM)
        caption(self, "Nöqtələr fərqlidir: əks halda üç xətt bir nöqtədən keçərdi")
        self.play(sh.animate.set_value(1.0), run_time=T_SLOW)
        x = cross_mark(size=80).move_to(B + P2(0.7, 0.6))
        self.play(Write(x), Flash(B, color=C_MIN, flash_radius=0.4), run_time=T_ANIM)
        self.wait(1.5)
        self.play(sh.animate.set_value(0.0), FadeOut(x), run_time=T_SLOW)
        for m in (lc, va, vc):
            m.clear_updaters()
        self.wait(WAIT_STEP)
        fade_all_but(self)

    def step(self):
        V1, V2, V3 = (P2(*v) for v in (self.V1, self.V2, self.V3))
        M1, M2, M3 = (V2 + V3) / 2, (V1 + V3) / 2, (V1 + V2) / 2
        # xətlər: a = V2V3, b = V1M1 (median), qalanları
        L = {"a": (V2, V3), "b": (V1, M1), "s2": (V1, V3), "s3": (V1, V2),
             "m2": (V2, M2), "m3": (V3, M3)}
        names = list(L)

        def points_of(keys):
            out = []
            for k1, k2 in itertools.combinations(keys, 2):
                x = intersect(*L[k1], *L[k2])
                if not any(np.linalg.norm(x - y) < 1e-6 for y in out):
                    out.append(x)
            return out

        caption(self, "Keçid: $n$ xətt, bir nöqtədən keçmir")
        lines = {k: full_line(*L[k]) for k in names}
        pts = points_of(names)
        grp, num = counter("kəsişmə nöqtələri:", 0, size=34)
        grp.to_corner(UR, buff=0.35)
        self.play(*[Create(lines[k]) for k in names], run_time=T_ANIM)
        self.play(FadeIn(grp), run_time=1.5)
        dots = VGroup(*[make_dot(p) for p in pts])
        self.play(LaggedStart(*[GrowFromCenter(d) for d in dots], lag_ratio=0.2),
                  ChangeDecimalToValue(num, len(pts)), run_time=T_ANIM)
        caption(self, "Silvester–Qallai (dual): dəqiq iki xəttin keçdiyi nöqtə var")
        X = intersect(*L["a"], *L["b"])
        xdot = make_dot(X, color=C_NEW, r=0.12)
        xl = az_math("X", size=34, color=C_NEW).move_to(free_spot(X, [L["a"][:1] + (
            unit(L["a"][1] - L["a"][0]),), (L["b"][0], unit(L["b"][1] - L["b"][0]))], r=0.38))
        al = make_label("a", lines["a"].get_end(), LEFT, color=C_LINE, size=34, buff=0.15)
        bl = make_label("b", lines["b"].get_end(), LEFT, color=C_LINE, size=34, buff=0.15)
        self.play(GrowFromCenter(xdot), Write(xl), FadeIn(al), FadeIn(bl),
                  Flash(X, color=C_NEW, flash_radius=0.35), run_time=T_ANIM)
        caption(self, "$a$ xəttini ataq: $L' = L \\setminus \\{a\\}$")
        a_dash = DashedVMobject(lines["a"].copy().set_color(C_DIM), num_dashes=50)
        self.play(ReplacementTransform(lines["a"], a_dash), al.animate.set_color(C_DIM),
                  run_time=T_ANIM)
        self.play(FadeOut(grp), run_time=1.5)
        num.clear_updaters()
        self.wait(WAIT_STEP)

        # ekran ikiyə bölünür
        rbox = (0.3, 6.95, -1.75, 2.05)
        ctr = (V1 + V2 + V3) / 3 + 0.35 * UP
        k = 0.48
        mp = lambda p: P2(3.65, -0.1) + k * (p - ctr)
        new_lines = {n: full_line(mp(L[n][0]), mp(L[n][1]), box=rbox, avoid=None)
                     for n in names if n != "a"}
        new_a_line = full_line(mp(L["a"][0]), mp(L["a"][1]), box=rbox, avoid=None, color=C_DIM)
        new_a = DashedVMobject(new_a_line, num_dashes=40)
        new_pts = [mp(p) for p in pts]
        div = Line(P2(0, 2.55), P2(0, -2.65), color=C_DIM, stroke_width=2)
        anims = [Transform(lines[n], new_lines[n]) for n in new_lines]
        anims += [Transform(a_dash, new_a), Create(div)]
        anims += [d.animate.move_to(q).scale(0.75) for d, q in zip(dots, new_pts)]
        anims += [xdot.animate.move_to(mp(X)).scale(0.75), xl.animate.scale(0.8).move_to(
            mp(X) + 0.48 * (xl.get_center() - X)),
                  al.animate.scale(0.8).next_to(new_a_line.get_end(), LEFT, buff=0.1),
                  bl.animate.scale(0.8).next_to(new_lines["b"].get_end(), LEFT, buff=0.1)]
        self.play(*anims, run_time=T_SLOW)

        # Hal 1 (sol yarı): L' dəstədir
        lbox = (-6.95, -0.3, -1.75, 2.05)
        h1 = az_tex("Hal 1", size=32, color=C_POINT).move_to(P2(-3.6, 2.35))
        self.play(Write(h1), run_time=1.5)
        caption(self, "Hal 1: $L'$ bir $O$ nöqtəsindən keçən dəstədir")
        O = P2(-3.6, 0.6)
        angs = [35, 65, 90, 115, 145]
        pen = VGroup(*[line_through(O, a, box=lbox, avoid=None) for a in angs])
        od = make_dot(O)
        ol = make_label("O", O, LEFT, size=32, buff=0.15)
        self.play(LaggedStart(*[GrowFromPoint(l, O) for l in pen], lag_ratio=0.15),
                  run_time=T_ANIM)
        self.play(GrowFromCenter(od), FadeIn(ol), run_time=1.5)
        ya = -1.1
        a1 = full_line(P2(-6, ya), P2(-1, ya), box=lbox, avoid=None, color=C_ELL)
        a1l = make_label("a", a1.get_end(), UL, color=C_ELL, size=32, buff=0.1)
        self.play(Create(a1), FadeIn(a1l), run_time=T_ANIM)
        caption(self, "$a$ dəstənin $O$ nöqtəsindən keçmir")
        Ys = [intersect(O, O + dir_deg(a), P2(-6, ya), P2(-1, ya)) for a in angs]
        cnt = az_math("1", size=40).move_to(P2(-3.6, -2.25))
        self.play(Flash(O, color=C_POINT, flash_radius=0.3), Write(cnt), run_time=1.5)
        ydots = VGroup(*[make_dot(y) for y in Ys])
        self.play(LaggedStart(*[GrowFromCenter(d) for d in ydots], lag_ratio=0.3),
                  run_time=T_ANIM)
        cnt2 = az_math("1", "+", "(n-1)", "=", "n", size=40).move_to(cnt)
        tmt(self, cnt, cnt2)
        caption(self, "$a \\cap m$ nöqtələri fərqlidir: əks halda iki xəttin "
                      "iki ortaq nöqtəsi olardı ($Y$ və $O$)")
        th = ValueTracker(angs[1])
        rot = always_redraw(lambda: line_through(O, th.get_value(), box=lbox, avoid=None,
                                                 color=C_POINT, width=4))
        rdot = always_redraw(lambda: make_dot(intersect(O, O + dir_deg(th.get_value()),
                                                        P2(-6, ya), P2(-1, ya)),
                                              color=C_POINT, r=0.1))
        self.play(FadeIn(rot), FadeIn(rdot), run_time=1.5)
        self.play(th.animate.set_value(angs[2]), run_time=T_SLOW)
        yl = make_label("Y", Ys[2], DR, size=32, buff=0.1)
        x = cross_mark(size=60).move_to(Ys[2] + P2(0.75, -0.55))
        self.play(Write(yl), Write(x), run_time=T_ANIM)
        self.wait(1.5)
        self.play(th.animate.set_value(angs[1]), FadeOut(x), FadeOut(yl), run_time=T_ANIM)
        rot.clear_updaters()
        rdot.clear_updaters()
        self.play(FadeOut(rot), FadeOut(rdot), run_time=1.5)
        self.wait(WAIT_STEP)

        # Hal 2 (sağ yarı)
        h2 = az_tex("Hal 2", size=32, color=C_POINT).move_to(P2(3.6, 2.35))
        self.play(Write(h2), run_time=1.5)
        caption(self, "Hal 2: $L'$ bir nöqtədən keçmir — induksiyaya görə ən azı "
                      "$n-1$ nöqtə")
        lp_pts = [mp(p) for p in points_of([n for n in names if n != "a"])]
        lp_dots = VGroup(*[Circle(radius=0.13, color=C_LINE, stroke_width=3).move_to(q)
                           for q in lp_pts])
        self.play(LaggedStart(*[Create(c) for c in lp_dots], lag_ratio=0.15), run_time=T_ANIM)
        c2 = az_math(r"\ge", "n-1", size=40).move_to(P2(3.6, -2.25))
        self.play(Write(c2), run_time=1.5)
        self.wait(WAIT_STEP)
        self.play(Transform(a_dash, full_line(mp(L["a"][0]), mp(L["a"][1]), box=rbox,
                                              avoid=None)),
                  al.animate.set_color(C_LINE), run_time=T_ANIM)
        self.play(Indicate(xdot, color=C_NEW, scale_factor=2.0),
                  Flash(mp(X), color=C_NEW, flash_radius=0.3), run_time=T_ANIM)
        caption(self, "$X$ yenidir: $X$-dən $L'$-in yalnız bir xətti ($b$) keçir")
        c3 = az_math(r"\ge", "(n-1)", "+", "1", "=", "n", size=40).move_to(c2)
        tmt(self, c2, c3)
        qed = qed_mark().next_to(c3, RIGHT, buff=0.3)
        self.play(FadeIn(qed), run_time=1.5)
        self.wait(WAIT_STEP)


# ─────────────────────────────────────────────────────────────────────────────
#  Hisse08 — 8.2. Tapşırıq 2: şərtlərin zəruriliyi (≈1 dəq)
# ─────────────────────────────────────────────────────────────────────────────
class Hisse08_Hell2(AZScene):
    def construct(self):
        section_title(self, "8.2. Tapşırıq 2: şərtlərin zəruriliyi")
        # paralel xətlər
        u = 1.6
        xs = [-0.4, 1.2, 2.8]
        ls = VGroup(*[full_line(P2(x, 0), P2(x, 1)) for x in xs])
        labs = VGroup(*[az_math(f"x = {k}", size=32, color=C_LINE).next_to(
            P2(x, 2.6), RIGHT, buff=0.1) for k, x in enumerate(xs)])
        self.play(LaggedStart(*[Create(l) for l in ls], lag_ratio=0.3), run_time=T_ANIM)
        self.play(FadeIn(labs), run_time=1.5)
        caption(self, "Kəsişmə yoxdur — şərt boş yerə ödənir")
        caption(self, "Amma xətlər bir nöqtədən keçmir")
        x = cross_mark(size=100).move_to(P2(5.2, 0.3))
        self.play(Write(x), run_time=T_ANIM)
        self.wait(WAIT_STEP)
        fade_all_but(self)
        # sonluluq: tam nöqtələr
        sp, y0 = 0.75, -0.15
        to_s = lambda i, j: P2(sp * i, sp * j + y0)
        grid = VGroup(*[make_dot(to_s(i, j), r=0.05) for j in range(-3, 5) for i in range(-9, 10)])
        caption(self, "Sonsuz çoxluq: tam nöqtələr")
        self.play(LaggedStart(*[FadeIn(d) for d in grid], lag_ratio=0.004), run_time=T_ANIM)
        X, Y = np.array([-3, -1]), np.array([-1, 0])
        Z = 2 * Y - X
        ln = full_line(to_s(*X), to_s(*Y), box=(X_L, X_R, -2.6, 3.05))
        big = VGroup(make_dot(to_s(*X), r=0.1), make_dot(to_s(*Y), r=0.1))
        lab = VGroup(az_math("X", size=34).move_to(to_s(*X) + P2(-0.32, sp / 2)),
                     az_math("Y", size=34).move_to(to_s(*Y) + P2(-0.32, sp / 2)))
        self.play(GrowFromCenter(big), FadeIn(lab), Create(ln), run_time=T_ANIM)
        zd = make_dot(to_s(*Z), color=C_NEW, r=0.12)
        zl = az_math("2Y - X", size=34, color=C_NEW)
        zl.move_to(to_s(*Z) + P2(-0.15 - zl.width / 2, sp / 2))
        self.play(GrowFromCenter(zd), Write(zl), Flash(to_s(*Z), color=C_NEW), run_time=T_ANIM)
        caption(self, "$2Y - X$ tamdır, $X$ və $Y$-dən fərqlidir və həmin xətt üzərindədir")
        self.play(FadeOut(ln), FadeOut(big), FadeOut(lab), FadeOut(zd), FadeOut(zl),
                  run_time=1.5)
        tri = [to_s(0, 0), to_s(1, 0), to_s(0, 1)]
        poly = Polygon(*tri, color=C_NEW, stroke_width=4, fill_color=C_NEW, fill_opacity=0.25)
        tdots = VGroup(*[make_dot(p, color=C_NEW, r=0.1) for p in tri])
        self.play(Create(poly), GrowFromCenter(tdots), run_time=T_ANIM)
        caption(self, "$(0,0)$, $(1,0)$, $(0,1)$ bir xətt üzərində deyil")
        self.wait(WAIT_STEP)
        end_section(self)


# ─────────────────────────────────────────────────────────────────────────────
#  Hisse09 — 8.3. Tapşırıq 3: fəzada Silvester–Qallai (≈1.5 dəq, ThreeDScene)
# ─────────────────────────────────────────────────────────────────────────────
# Fəzada 8 nöqtə (ən kiçik cüt: 0-cı nöqtə və 1–4 xətti; numpy ilə yoxlanılır)
SPACE_POINTS = [(-0.3, 1.6, -0.6), (2.6, 1.9, 0.7), (-1.0, 2.2, 0.7), (-0.5, -2.3, -1.2),
                (-2.9, 0.7, -0.8), (-0.9, -1.3, 1.2), (-2.8, -2.5, -1.1), (2.4, -1.5, 1.6)]


class Hisse09_Hell3(AZ3DScene):
    PHI0, THETA0 = 65 * DEGREES, -45 * DEGREES
    S_PLANE = 0.6                 # kanonik diaqramın Π müstəvisindəki miqyası

    def construct(self):
        self.set_camera_orientation(phi=self.PHI0, theta=self.THETA0)
        section_title(self, "8.3. Tapşırıq 3: fəzada Silvester–Qallai")
        pts = [np.array(p, dtype=float) for p in SPACE_POINTS]
        axes = ThreeDAxes(x_range=[-4, 4, 1], y_range=[-4, 4, 1], z_range=[-2, 3, 1],
                          x_length=8, y_length=8, z_length=5, axis_config={
                              "stroke_width": 1.5, "color": C_DIM, "include_ticks": False,
                              "tip_width": 0.15, "tip_height": 0.15})
        dots = Group(*[Dot3D(p, radius=0.09, color=C_POINT, resolution=(8, 8)) for p in pts])
        self.play(Create(axes), run_time=T_ANIM)
        self.play(LaggedStart(*[FadeIn(d) for d in dots], lag_ratio=0.15), run_time=T_ANIM)
        caption(self, "Fəzada sonlu sayda nöqtə: cütlər yenə sonludur")
        self.begin_ambient_camera_rotation(rate=0.12)
        self.wait(5)
        self.stop_ambient_camera_rotation()
        self.move_camera(phi=self.PHI0, theta=self.THETA0, run_time=T_ANIM)

        # ən kiçik cüt (3D məsafələr)
        best = None
        for i, j in itertools.combinations(range(len(pts)), 2):
            for k in range(len(pts)):
                if k in (i, j):
                    continue
                d = dist_point_line(pts[k], pts[i], pts[j])
                if best is None or d < best[0]:
                    best = (d, k, i, j)
        h, kP, i1, i2 = best
        P, X1, X2 = pts[kP], pts[i1], pts[i2]
        Hf = foot_of_perpendicular(P, X1, X2)
        u = unit(X2 - X1)
        ell0 = Line(Hf - 5 * u, Hf + 5 * u, color=C_ELL, stroke_width=4)
        hseg0 = DashedLine(P, Hf, color=C_MIN, stroke_width=4, dash_length=0.08)
        caption(self, "Ən kiçik məsafəli cüt: $P$ və $\\ell$")
        self.play(Create(ell0), run_time=T_ANIM)
        self.play(dots[kP].animate.set_color(C_MIN), Create(hseg0), run_time=T_ANIM)

        # kanonik diaqram Π müstəvisində (mərkəz koordinat başlanğıcında).
        # u, v, n sağ üçlükdür və n yuxarı baxır — perpendikulyar baxış güzgü əksi olmasın.
        v = unit(P - Hf)
        if np.cross(u, v)[2] < 0:
            u = -u
        n = unit(np.cross(u, v))
        sc = self.S_PLANE
        cx, cy = -0.6, -0.25          # diaqram bir az sola: sağda siyahı üçün yer

        def E(xy):
            return sc * ((xy[0] - cx) * u + (xy[1] - cy) * v)

        Pc, Hc, Ac, Bc, Cc = (E(CANON[k]) for k in "PHABC")
        others = [d for t, d in enumerate(dots) if t not in (kP, i1, i2)]
        self.play(*[FadeOut(d) for d in others], FadeOut(axes), run_time=T_ANIM)
        ell = Line(Hc - 5.2 * u, Hc + 5.2 * u, color=C_ELL, stroke_width=4)
        hseg = DashedLine(Pc, Hc, color=C_MIN, stroke_width=4, dash_length=0.1)
        self.play(Transform(ell0, ell), Transform(hseg0, hseg),
                  dots[kP].animate.move_to(Pc), dots[i1].animate.move_to(Ac),
                  dots[i2].animate.move_to(Bc), run_time=T_SLOW)
        corners = [E((-7.6, -3.3)), E((3.6, -3.3)), E((3.6, 2.8)), E((-7.6, 2.8))]
        plane = Polygon(*corners, stroke_width=1, stroke_color=C_DIM, fill_color=GREY,
                        fill_opacity=0.15)
        self.play(FadeIn(plane), run_time=T_ANIM)
        pi_lab = az_math(r"\Pi", size=40, color=C_TEXT2).move_to(E((2.6, 2.2)))
        self.add_fixed_orientation_mobjects(pi_lab)
        self.play(FadeIn(pi_lab), run_time=1.5)
        caption(self, "$P$ və $\\ell$ bir $\\Pi$ müstəvisini müəyyən edir")

        def lab(t, pos, off, color=C_TEXT):
            m = az_math(t, size=34, color=color).move_to(pos + off)
            self.add_fixed_orientation_mobjects(m)
            return m

        labs = [lab("P", Pc, 0.35 * v + 0.2 * u), lab("A", Ac, -0.35 * v - 0.15 * u),
                lab("B", Bc, -0.35 * v + 0.15 * u), lab(r"\ell", Hc + 4.6 * u, 0.3 * v, C_ELL)]
        self.play(*[FadeIn(m) for m in labs], run_time=1.5)
        Cdot = Dot3D(Cc, radius=0.09, color=C_POINT, resolution=(8, 8))
        Hdot = Dot3D(Hc, radius=0.06, color=C_TEXT, resolution=(8, 8))
        ra = VMobject(color=C_TEXT2, stroke_width=2.5).set_points_as_corners(
            [Hc + 0.2 * u, Hc + 0.2 * u + 0.2 * v, Hc + 0.2 * v])
        caption(self, "$\\ell$ üzərində $A$, $B$, $C$; perpendikulyarın oturacağı $H$")
        self.play(FadeIn(Cdot), FadeIn(Hdot), Create(ra), run_time=T_ANIM)
        l2 = [lab("C", Cc, -0.35 * v), lab("H", Hc, -0.35 * v - 0.2 * u)]
        self.play(*[FadeIn(m) for m in l2], run_time=1.5)
        pb = Line(Pc - 0.6 * unit(Bc - Pc), Bc + 1.2 * unit(Bc - Pc), color=C_LINE,
                  stroke_width=3.5)
        F = foot_of_perpendicular(Ac, Pc, Bc)
        hp = DashedLine(Ac, F, color=C_NEW, stroke_width=4, dash_length=0.08)
        tri = Polygon(Pc, Ac, Bc, stroke_width=0, fill_color=C_AUX, fill_opacity=0.3)
        self.play(Create(pb), FadeIn(tri), run_time=T_ANIM)
        self.play(Create(hp), run_time=T_ANIM)
        hpl = lab("h'", (Ac + F) / 2, 0.25 * unit(np.cross(n, F - Ac)), C_NEW)
        self.play(FadeIn(hpl), run_time=1.5)
        caption(self, "Bütün qurmalar $\\Pi$ müstəvisinin içindədir")

        # kamera Π-yə perpendikulyar baxışa fırlanır
        phi_n = np.arccos(np.clip(n[2], -1, 1))
        theta_n = np.arctan2(n[1], n[0])
        theta_n = self.THETA0 + ((theta_n - self.THETA0 + PI) % TAU - PI)
        m_ = rotation_matrix(-phi_n, RIGHT) @ rotation_about_z(-theta_n - 90 * DEGREES)
        u2, v2 = m_ @ u, m_ @ v
        gamma = -np.arctan2(u2[1], u2[0])
        if (rotation_about_z(gamma) @ v2)[1] < 0:
            gamma += PI
        self.move_camera(phi=phi_n, theta=theta_n, gamma=gamma, run_time=4.0)
        caption(self, "Qalan addımlar müstəvidəki kimidir")
        items = VGroup(*[VGroup(check_mark(size=34), az_tex(t, size=30)).arrange(RIGHT, buff=0.15)
                         for t in ("Addım 4: göyərçin yuvası", "Addım 5: $AB < PB$",
                                   "Addım 6: sahə fəndi", "Addım 7: yeni cüt icazəlidir",
                                   "Addım 8: ziddiyyət")])
        items.arrange(DOWN, aligned_edge=LEFT, buff=0.22).to_edge(RIGHT, buff=0.2).shift(0.6 * UP)
        self.add_fixed_in_frame_mobjects(items)
        self.remove(items)
        for it in items:
            self.add_fixed_in_frame_mobjects(it)
            self.play(FadeIn(it, shift=0.1 * LEFT), run_time=1.5)
        self.wait(WAIT_STEP)
        self.play(FadeOut(items), run_time=1.5)
        self.move_camera(phi=self.PHI0, theta=self.THETA0, gamma=0, run_time=4.0)
        caption(self, "Deməli, fəzada da bütün nöqtələr bir xətt üzərindədir"
                      r"\quad $\blacksquare$")
        self.wait(WAIT_STEP)
        end_section(self)


# ─────────────────────────────────────────────────────────────────────────────
#  Hisse10 — 8.4. Tapşırıq 4: çevrələr və inversiya (≈3 dəq)
# ─────────────────────────────────────────────────────────────────────────────
class Hisse10_Hell4(AZScene):
    R_INV = 1.6        # inversiya çevrəsinin ekrandakı radiusu ("vahid çevrə")

    def construct(self):
        section_title(self, "8.4. Tapşırıq 4: çevrələr və inversiya")
        self.generalized_circle()
        self.inversion_intro()
        self.solution()
        self.final_card()

    @staticmethod
    def circle_through(a, b, c):
        """Üç nöqtədən keçən çevrə (mərkəz, radius); numpy ilə."""
        ax, ay = a[:2]
        bx, by = b[:2]
        cx, cy = c[:2]
        d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
        ux = ((ax**2 + ay**2) * (by - cy) + (bx**2 + by**2) * (cy - ay)
              + (cx**2 + cy**2) * (ay - by)) / d
        uy = ((ax**2 + ay**2) * (cx - bx) + (bx**2 + by**2) * (ax - cx)
              + (cx**2 + cy**2) * (bx - ax)) / d
        o = P2(ux, uy)
        return o, float(np.linalg.norm(a - o))

    def generalized_circle(self):
        caption(self, "Ümumiləşmiş çevrə — çevrə və ya xətt")
        y0 = 0.6
        p1, p3 = P2(-2.2, y0), P2(2.2, y0)
        t = ValueTracker(2.0)
        p2 = lambda: P2(0.3, y0 - t.get_value())

        def shape():
            if t.get_value() < 0.02:
                return full_line(p1, p3, color=C_AUX, width=4)
            o, r = self.circle_through(p1, p2(), p3)
            return clipped_circle(o, r, color=C_AUX, width=4)

        circ = always_redraw(shape)
        d1, d3 = make_dot(p1), make_dot(p3)
        d2 = always_redraw(lambda: make_dot(p2()))
        self.play(GrowFromCenter(d1), GrowFromCenter(d3), FadeIn(d2), run_time=1.5)
        self.play(Create(circ), run_time=T_ANIM)
        self.play(t.animate.set_value(0.0), run_time=5.0, rate_func=smooth)
        self.wait(1.0)
        caption(self, "Üç nöqtə bir xətt üzərinə düşəndə çevrə xəttə çevrilir")
        caption(self, "Şərt: üç nöqtədən keçən ümumiləşmiş çevrə dördüncü nöqtəni də saxlayır")
        for m in (circ, d2):
            m.clear_updaters()
        self.wait(WAIT_STEP)
        fade_all_but(self)

    def inv(self, x, O):
        return invert(x, O, self.R_INV)

    def inversion_intro(self):
        O = P2(-3.0, -0.3)
        R = self.R_INV
        circ = Circle(radius=R, color=C_DIM, stroke_width=2).move_to(O)
        od = make_dot(O, color=C_MIN)
        ol = make_label("O", O, DL, size=34, buff=0.1)
        caption(self, "İnversiya: $O$ mərkəzli vahid çevrə")
        self.play(Create(circ), GrowFromCenter(od), FadeIn(ol), run_time=T_ANIM)
        f = az_math("OX", r"\cdot", "OX'", "=", "1", size=FS_FORMULA).move_to(P2(4.4, 2.2))
        self.play(Write(f), run_time=T_ANIM)
        dvec = unit(P2(1.0, 0.45))
        r = ValueTracker(3.4)
        X = lambda: O + r.get_value() * dvec
        ray = Line(O, O + 7.5 * dvec, color=C_DIM, stroke_width=2)
        ray = DashedVMobject(ray, num_dashes=40)
        xd = always_redraw(lambda: make_dot(X(), color=C_POINT))
        xpd = always_redraw(lambda: make_dot(self.inv(X(), O), color=C_NEW))
        xl = always_redraw(lambda: make_label("X", X(), UP, size=32, buff=0.12))
        xpl = always_redraw(lambda: make_label("X'", self.inv(X(), O), DOWN, size=32,
                                               color=C_NEW, buff=0.12))
        self.play(Create(ray), FadeIn(xd), FadeIn(xl), run_time=T_ANIM)
        self.play(FadeIn(xpd), FadeIn(xpl), run_time=1.5)
        caption(self, "$X'$ — $OX$ şüası üzərində, $OX \\cdot OX' = 1$")
        self.play(r.animate.set_value(R), run_time=T_SLOW)
        caption(self, "$X$ çevrə üzərində olanda $X' = X$")
        self.play(r.animate.set_value(0.95), run_time=T_SLOW)
        self.play(r.animate.set_value(2.6), run_time=T_SLOW)
        for m in (xd, xpd, xl, xpl):
            m.clear_updaters()
        self.play(FadeOut(xd), FadeOut(xpd), FadeOut(xl), FadeOut(xpl), FadeOut(ray),
                  run_time=1.5)

        # əsas xassə: O-dan keçən çevrə -> O-dan keçməyən xətt
        rho = 1.1
        c = O + rho * RIGHT
        gcirc = Circle(radius=rho, color=C_AUX, stroke_width=4).move_to(c)
        self.play(Create(gcirc), run_time=T_ANIM)
        # yalnız obrazı ekranda qalan nöqtələr (obraz xətti O-dan R²/(2ρ) məsafədədir)
        angs = np.radians(np.linspace(-124, 118, 36))
        src = [c + rho * P2(np.cos(a), np.sin(a)) for a in angs]
        src = [p for p in src if in_box(self.inv(p, O), BOX_FULL, margin=0.15)]
        sdots = VGroup(*[make_dot(p, r=0.06) for p in src])
        self.play(LaggedStart(*[GrowFromCenter(d) for d in sdots], lag_ratio=0.03),
                  run_time=T_ANIM)
        imgs = [self.inv(p, O) for p in src]
        self.play(*[d.animate.move_to(q) for d, q in zip(sdots, imgs)], run_time=T_SLOW)
        xline = O[0] + R * R / (2 * rho)
        img_line = full_line(P2(xline, 0), P2(xline, 1), color=C_LINE, width=4)
        self.play(Create(img_line), run_time=T_ANIM)
        caption(self, "$O$-dan keçən çevrə $O$-dan keçməyən xəttə keçir")
        self.play(FadeOut(sdots), FadeOut(img_line), FadeOut(gcirc), run_time=1.5)
        # O-dan keçən xətt özünə keçir
        d2 = dir_deg(28)
        lO = full_line(O, O + d2, color=C_LINE, width=3)
        self.play(Create(lO), run_time=T_ANIM)
        ts = [-2.6, -1.9, -1.2, -0.7, 0.6, 1.0, 1.7, 2.4, 3.3, 4.2]
        ldots = VGroup(*[make_dot(O + t_ * d2, r=0.07) for t_ in ts])
        self.play(FadeIn(ldots), run_time=1.5)
        self.play(*[d.animate.move_to(self.inv(O + t_ * d2, O)) for d, t_ in zip(ldots, ts)],
                  run_time=T_SLOW)
        caption(self, "$O$-dan keçən xətt özünə keçir")
        self.wait(WAIT_STEP)
        fade_all_but(self)

    def solution(self):
        caption(self, "Həll: $S$-dən bir $O$ nöqtəsi seçək")
        c = P2(-1.6, 0.2)
        rho = 1.9
        angs = [180, 20, 80, 130, 260, 320]
        S = [c + rho * P2(np.cos(np.radians(a)), np.sin(np.radians(a))) for a in angs]
        O = S[0]
        dots = VGroup(*[make_dot(p) for p in S])
        self.play(LaggedStart(*[GrowFromCenter(d) for d in dots], lag_ratio=0.12),
                  run_time=T_ANIM)
        self.play(dots[0].animate.set_color(C_MIN).scale(1.3), run_time=1.5)
        ol = make_label("O", O, LEFT, size=34, color=C_MIN, buff=0.15)
        self.play(FadeIn(ol), run_time=1.5)
        caption(self, "Qalan nöqtələr inversiya ilə obrazlarına keçir")
        imgs = [invert(p, O, 2.2) for p in S[1:]]
        rays = VGroup(*[DashedLine(O, q + 0.6 * unit(q - O), color=C_DIM, stroke_width=2,
                                   dash_length=0.1) for q in imgs])
        self.play(LaggedStart(*[Create(r) for r in rays], lag_ratio=0.1), run_time=T_ANIM)
        ghosts = VGroup(*[make_dot(p, r=0.06).set_opacity(0.35) for p in S[1:]])
        self.add(ghosts)
        self.play(*[d.animate.move_to(q).set_color(C_NEW) for d, q in zip(dots[1:], imgs)],
                  run_time=T_SLOW)
        names = {2: "A", 5: "B", 1: "D"}
        plabs = VGroup(*[make_label(names[i] + "'", imgs[i - 1], RIGHT, size=32, color=C_NEW,
                                    buff=0.15) for i in names])
        self.play(FadeIn(plabs), run_time=1.5)
        # γ = O, A, B-dən keçən çevrə -> A'B' xətti
        gc, gr = self.circle_through(O, S[2], S[5])
        gamma = Circle(radius=gr, color=C_AUX, stroke_width=4).move_to(gc)
        glab = az_math(r"\gamma", size=40, color=C_AUX).move_to(gc + gr * P2(-0.55, -0.95))
        orig_labs = VGroup(*[make_label(names[i], S[i], UR, size=30, buff=0.08)
                             for i in names])
        caption(self, "$O$, $A$, $B$-dən keçən $\\gamma$ çevrəsi")
        self.play(Create(gamma), FadeIn(glab), FadeIn(orig_labs), run_time=T_ANIM)
        caption(self, "Şərtə görə $\\gamma$ dördüncü nöqtəni də saxlayır: $D$")
        self.play(Indicate(ghosts[0], color=C_POINT, scale_factor=2.5), run_time=T_ANIM)
        gl = full_line(imgs[1], imgs[4], color=C_LINE, width=4)
        self.play(ReplacementTransform(gamma.copy(), gl), run_time=T_SLOW)
        caption(self, "İnversiya ilə $\\gamma$ $A'B'$ xəttinə keçir, $D'$ də onun üzərindədir")
        self.play(Indicate(dots[1], color=C_NEW, scale_factor=2.0), run_time=T_ANIM)
        caption(self, "Deməli, $S'$ Silvester şərtini ödəyir")
        caption(self, "Silvester–Qallai: $S'$ bir $m$ xətti üzərindədir")
        ml = make_label("m", gl.get_end(), LEFT, size=36, color=C_LINE, buff=0.2)
        self.play(FadeIn(ml), run_time=1.5)
        self.wait(WAIT_STEP)
        fade_all_but(self)
        clear_caption(self)

        # geri inversiya: iki hal
        div = Line(P2(0, 2.7), P2(0, -2.6), color=C_DIM, stroke_width=2)
        self.play(Create(div), run_time=1.5)
        # sol: m O-dan keçir
        lb = (-6.9, -0.3, -1.9, 2.4)
        O1 = P2(-4.6, -0.6)
        d1 = dir_deg(30)
        m1 = full_line(O1, O1 + d1, box=lb, avoid=None, color=C_LINE)
        pts1 = VGroup(*[make_dot(O1 + t_ * d1, r=0.07) for t_ in (-2.0, -1.1, 1.0, 2.4)])
        m1l = make_label("m", m1.get_end(), DL, size=32, color=C_LINE, buff=0.12)
        o1 = VGroup(make_dot(O1, color=C_MIN), make_label("O", O1, DOWN, size=30, buff=0.15,
                                                          color=C_MIN))
        t1 = para(["$m$ $O$-dan keçir $\\Rightarrow$", "$S$ bir xətt üzərindədir"], size=32,
                  align=ORIGIN).move_to(P2(-3.6, -2.25))
        self.play(Create(m1), FadeIn(m1l), FadeIn(o1), FadeIn(pts1), run_time=T_ANIM)
        self.play(*[d.animate.move_to(invert(d.get_center(), O1, 1.6)) for d in pts1],
                  run_time=T_SLOW)
        self.play(Write(t1), run_time=T_ANIM)
        self.wait(read_wait(" ".join(["m O-dan keçir", "S bir xətt üzərindədir"])))
        # sağ: m O-dan keçmir — xətt O-dan keçən çevrəyə "əyilir"
        rb = (0.3, 6.9, -1.9, 2.4)
        O2 = P2(2.0, -0.4)
        Rr = 1.8
        xm = O2[0] + 1.4
        m2 = full_line(P2(xm, -1), P2(xm, 1), box=rb, avoid=None, color=C_LINE)
        o2 = VGroup(make_dot(O2, color=C_MIN), make_label("O", O2, LEFT, size=30, buff=0.15,
                                                          color=C_MIN))
        ys = [-1.2, -0.5, 0.4, 1.1, 1.9]
        pts2 = VGroup(*[make_dot(P2(xm, y), r=0.07) for y in ys])
        m2l = make_label("m", m2.get_end(), LEFT, size=32, color=C_LINE, buff=0.15)
        self.play(Create(m2), FadeIn(m2l), FadeIn(o2), FadeIn(pts2), run_time=T_ANIM)
        rho2 = Rr * Rr / (2 * (xm - O2[0]))
        circ2 = Circle(radius=rho2, color=C_LINE, stroke_width=4).move_to(O2 + rho2 * RIGHT)
        self.play(Transform(m2, circ2), FadeOut(m2l),
                  *[d.animate.move_to(invert(d.get_center(), O2, Rr)) for d in pts2],
                  run_time=T_SLOW)
        t2 = para(["$m$ $O$-dan keçmir $\\Rightarrow$", "$S$ bir çevrə üzərindədir"], size=32,
                  align=ORIGIN).move_to(P2(3.6, -2.25))
        self.play(Write(t2), run_time=T_ANIM)
        self.wait(read_wait(" ".join(["m O-dan keçmir", "S bir çevrə üzərindədir"])))
        qed = qed_mark(size=48).move_to(P2(6.5, -2.25))
        self.play(FadeIn(qed), run_time=1.5)
        self.wait(WAIT_STEP)
        fade_all_but(self)

    def final_card(self):
        t = az_tex("Düzgün çevirmə yeni məsələni artıq isbat etdiyimiz", size=44)
        t2 = az_tex("teoremə gətirir", size=44)
        g = VGroup(t, t2).arrange(DOWN, buff=0.3)
        self.play(FadeOut(self._section), Write(g), run_time=T_ANIM)
        self.wait(4)
        self.play(FadeOut(g), run_time=T_ANIM)
        self.wait(1.0)
