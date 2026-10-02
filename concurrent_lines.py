"""
Kəsişmə nöqtəsindən həmişə üçüncü xətt keçirsə, bütün xətlər bir nöqtədən keçir
==============================================================================
3Blue1Brown üslubunda səssiz vizual isbat (Manim Community Edition).

MƏSƏLƏ
    Müstəvidə sonlu sayda, cüt-cüt paralel olmayan düz xətlər verilmişdir.
    Onlardan istənilən ikisinin kəsişmə nöqtəsindən verilmiş xətlərdən daha
    biri keçir. İsbat edin ki, bütün bu xətlər bir nöqtədən keçir.

İSBAT (ziddiyyət yolu ilə, ən kiçik məsafə üsulu)
    (P, ℓ) cütlərinə baxırıq: P kəsişmə nöqtəsi, ℓ isə P-dən keçməyən xətt.
    h = d(P, ℓ) ən kiçik olsun. P-dən ən azı üç xətt keçir, onlar ℓ-i üç
    fərqli nöqtədə kəsir; ikisi (A, B) perpendikulyarın oturacağı H-dan eyni
    tərəfdədir (H – A – B). Onda AB ≤ HB < PB və PAB üçbucağının sahəsindən
    h' = d(A, PB) = (AB/PB)·h < h. (A, PB) da uyğun cütdür — ziddiyyət.

QURAŞDIRMA
    # Sistem paketləri (Cairo/Pango, ffmpeg, LaTeX, CMU Serif şrifti)
    #   Ubuntu/Debian: sudo apt install ffmpeg libcairo2-dev libpango1.0-dev \
    #                      pkg-config texlive texlive-latex-extra dvisvgm fonts-cmu
    #   macOS:         brew install ffmpeg py3cairo pango pkg-config
    #                  brew install --cask mactex-no-gui font-computer-modern
    pip install manim

RENDER
    manim -pql concurrent_lines.py ConcurrentLines              # tez yoxlama (480p, 15 fps)
    manim -pqh --fps 60 concurrent_lines.py ConcurrentLines     # final (1080p, 60 fps)

    Nəticə: media/videos/concurrent_lines/1080p60/ConcurrentLines.mp4

Bütün həndəsə (kəsişmələr, perpendikulyarlar, məsafələr, h') numpy ilə
hesablanır; yalnız kanonik diaqramın əsas nöqtələri aşağıda sabit verilib.
"""

from __future__ import annotations

from functools import lru_cache
from itertools import combinations

import numpy as np
from manim import *

# ═════════════════════════════════════════════════════════════════════════════
#  SABİTLƏR — rənglər, şrift, vaxtlar, koordinatlar
# ═════════════════════════════════════════════════════════════════════════════
config.background_color = BLACK

# ── Rənglər (bütün video boyu eyni) ──────────────────────────────────────────
LINE_COLOR = BLUE            # verilmiş xətlər
POINT_COLOR = YELLOW         # kəsişmə nöqtələri, A, B, C
ELL_COLOR = ORANGE           # seçilmiş ℓ xətti
P_COLOR = RED                # P nöqtəsi və h məsafəsi
NEW_COLOR = GREEN            # yeni cüt (A, PB) və h'
TRI_COLOR = PURPLE           # PAB üçbucağı
FINAL_COLOR = GREEN          # final ortaq nöqtə, ✓
FOOT_COLOR = GREY_A          # H nöqtəsi (perpendikulyarın oturacağı)
TEXT_COLOR = WHITE
AXIS_COLOR = GREY_B          # kiçik ədəd oxu
RAY_TONES = ("#FFD39A", "#E8590C")   # Səhnə 5: ℓ-in iki şüası (açıq / tünd narıncı)

BG_OPACITY = 0.35            # fonda qalan xətlər
DIM_OPACITY = 0.25           # zəiflədilmiş PC xətti və C nöqtəsi
TRI_OPACITY = 0.3            # PAB üçbucağının doluluğu

# ── Şrift və ölçülər ─────────────────────────────────────────────────────────
FONT = "CMU Serif"           # Computer Modern (LaTeX şrifti), Unicode versiyası: ə, Ə, ş, ğ, ı, İ var
CAPTION_SIZE = 34            # aşağıdakı izah mətni
CAPTION_BASELINE = -3.66     # izah mətninin baza xətti (ekranın aşağı kənarı)
LABEL_SIZE = 36              # P, ℓ, H, A, B, C, h, h' etiketləri
FORMULA_SIZE = 40            # sağ tərəfdəki düsturlar
MATH_SCALE = 1.34            # sətir içindəki MathTex hissələri Text-ə nisbətən (böyük hərf hündürlüyü)

LINE_W = 3.0                 # sonsuz xətlər
SEG_W = 7.0                  # ayrıca göstərilən seqmentlər
H_W = 4.0                    # h, h' perpendikulyarları
DOT_R = 0.075                # əsas nöqtələr
SMALL_DOT_R = 0.05           # sxematik kəsişmə nöqtələri
RA_SIZE = 0.2                # düz bucaq işarəsi
DASH = 0.12                  # qırıq xəttin addımı

# ── Vaxtlar (saniyə) ─────────────────────────────────────────────────────────
TEMPO = 1.6                  # bütün keçidləri birlikdə yavaşladır: 1.0 — əvvəlki sürət, böyük — daha yavaş
T_FAST = 0.6 * TEMPO
T_MED = 1.0 * TEMPO
T_SLOW = 1.5 * TEMPO
PAUSE = 0.6 * TEMPO          # mətn oxunsun deyə fasilə
T_PAIR_IN = 0.5 * TEMPO      # Səhnə 3: bir cütün göstərilməsi
T_PAIR_OUT = 0.4 * TEMPO     # Səhnə 3: məsafənin oxa düşməsi
FINAL_HOLD = 2.0             # sonda gözləmə

# ── Səhnə (xətlər yalnız bu düzbucaqlıda çəkilir; aşağı zolaq mətn üçündür) ──
FRAME_X = config.frame_width / 2
FRAME_Y = config.frame_height / 2
STAGE = (-FRAME_X, FRAME_X, -3.15, FRAME_Y)       # (sol, sağ, aşağı, yuxarı)


def pt(x, y):
    return np.array([x, y, 0.0])


# ── Kanonik diaqram (Səhnə 4–8) ──────────────────────────────────────────────
ELL_Y = -2.0
H_PT = pt(-3.0, -2.0)
P_PT = pt(-3.0, 1.5)         # h = 3.5
A_PT = pt(-1.5, -2.0)
B_PT = pt(1.5, -2.0)
C_PT = pt(-5.5, -2.0)

# ── Səhnə 1: ümumi vəziyyətdə 6 xətt  ((nöqtə), bucaq°) ──────────────────────
SCENE1_LINES = [
    ((-3.03, 1.70), 18.6), ((-3.05, 0.44), 174.9), ((-0.29, -2.43), 54.8),
    ((3.20, -1.51), 116.6), ((-0.72, -0.20), 94.3), ((1.33, 2.20), 152.9),
]
SCENE1_PAIR = (1, 4)         # işıqlanan iki xətt (kəsişməsi mərkəzə yaxındır)

EX_LEFT = pt(-3.6, 0.55)     # nümunə 1: dəstə (4 xətt bir nöqtədən)
EX_RIGHT = pt(3.6, 0.45)     # nümunə 2: üçbucaq (3 xətt)
PENCIL_ANGLES = (15, 60, 105, 150)
PENCIL_HALF = 1.7            # dəstə xətlərinin yarım uzunluğu
TRI_RADIUS = 1.15            # üçbucağın xarici çevrəsinin radiusu
TRI_EXT = 0.8                # üçbucaq tərəflərinin təpədən kənara uzantısı

# ── Səhnə 2–3, 9: "sxematik" konfiqurasiya (bir nöqtədən keçmir) ─────────────
# Seçilib ki: sağ yuxarı künc (ədəd oxu) boş qalsın, kəsişmələr bir-birindən
# aralı olsun və ən kiçik məsafəli cüt aydın seçilsin.
SCHEMATIC_LINES = [
    ((-3.82, -1.53), 14.6), ((0.05, 1.62), 172.5), ((-3.12, -1.40), 81.9),
    ((-5.43, -0.99), 37.2), ((-0.16, 1.15), 105.8), ((-5.03, -1.10), 141.8),
]
SCENE2_PICK = ((0, 4), 1)    # Səhnə 2: kəsişmə (xətt 0 ∩ xətt 4) və onu keçməyən xətt 1
SCENE3_DEMO = [              # Səhnə 3: animasiya ilə göstərilən cütlər
    ((0, 4), 2), ((1, 4), 3), ((3, 5), 1), ((2, 3), 0), ((0, 5), 2), ((3, 4), 2),
]
CONCURRENCY_POINT = pt(0.0, 0.45)    # Səhnə 9: xətlərin toplandığı nöqtə

# Etiketlərin nöqtəyə nəzərən yeri (xətlərin və mötərizələrin üstünə düşməsin)
A_LAB_OFF = pt(-0.32, -0.38)
B_LAB_OFF = pt(0.36, 0.3)
C_LAB_OFF = pt(0.36, -0.38)
H_LAB_OFF = pt(-0.34, 0.34)

# ── Sağ tərəf: ədəd oxu və düsturların yerləri ───────────────────────────────
AXIS_CENTER = pt(4.65, 3.45)
AXIS_LENGTH = 4.2
AXIS_MAX = 10
SCENE3_FORMULA_POS = pt(4.65, 2.55)
SCHEMA_LEFT, SCHEMA_RIGHT = pt(4.0, 2.75), pt(5.85, 2.75)   # Səhnə 5: iki "qutu"
ORDER_POS = pt(4.9, 1.45)            # H — A — B
INEQ_POS = pt(4.7, 1.45)             # AB ≤ HB < PB
CORNER_POS = pt(5.75, 3.45)          # çərçivəli AB < PB
COPY_CENTER = pt(4.6, 1.6)           # Səhnə 7: üçbucağın surəti
COPY_SCALE = 0.5
S1_POS, S2_POS = pt(4.6, -0.05), pt(4.6, -0.8)
ALG_POS = pt(4.3, 1.75)              # cəbri addımlar
BAR_X = (6.15, 6.65)                 # h və h' müqayisə sütunları
BAR_BOTTOM = -1.2
CHECK_X = 0.3                        # Səhnə 8: yoxlama siyahısı
CHECK_Y = (2.35, 1.65, 0.95)
DIST_POS = pt(3.7, 0.0)


# ═════════════════════════════════════════════════════════════════════════════
#  HƏNDƏSƏ (numpy)
# ═════════════════════════════════════════════════════════════════════════════
def unit(v):
    v = np.asarray(v, dtype=float)
    return v / np.linalg.norm(v)


def direction(deg):
    a = np.radians(deg)
    return np.array([np.cos(a), np.sin(a), 0.0])


def rotate_vec(v, angle):
    c, s = np.cos(angle), np.sin(angle)
    return np.array([c * v[0] - s * v[1], s * v[0] + c * v[1], 0.0])


def angle_of(v):
    return np.arctan2(v[1], v[0])


def line_through(point, deg):
    """(p, q): verilmiş nöqtədən verilmiş bucaqla keçən xəttin iki nöqtəsi."""
    p = pt(*point)
    return p, p + direction(deg)


def line_points(line):
    """full_line obyektindən və ya (p, q) cütündən xəttin iki nöqtəsi."""
    if isinstance(line, Mobject):
        return line.p, line.q
    return line


def on_stage(x, margin=0.0):
    return (STAGE[0] + margin <= x[0] <= STAGE[1] - margin
            and STAGE[2] + margin <= x[1] <= STAGE[3] - margin)


def clip_to_stage(p, q):
    """pq sonsuz xəttinin səhnə düzbucaqlısı ilə kəsişdiyi iki uc nöqtə."""
    d = q - p
    ts = []
    for axis, lo, hi in ((0, STAGE[0], STAGE[1]), (1, STAGE[2], STAGE[3])):
        if abs(d[axis]) > 1e-12:
            ts += [(lo - p[axis]) / d[axis], (hi - p[axis]) / d[axis]]
    ts = [t for t in ts if on_stage(p + t * d, margin=-1e-7)]
    if len(ts) < 2:                       # xətt səhnəyə düşmür
        return p, p + 1e-3 * unit(d)
    return p + min(ts) * d, p + max(ts) * d


def full_line(p, q, color=LINE_COLOR, width=LINE_W, opacity=1.0):
    """İki nöqtədən keçən, ekran kənarına qədər uzanan xətt.
    Xəttin özü (.p, .q) sonrakı hesablamalar üçün saxlanılır."""
    p, q = np.array(p, dtype=float), np.array(q, dtype=float)
    a, b = clip_to_stage(p, q)
    line = Line(a, b, color=color, stroke_width=width, stroke_opacity=opacity)
    line.p, line.q = p, q
    return line


def intersect(l1, l2):
    """İki xəttin kəsişmə nöqtəsi (numpy ilə xətti sistem)."""
    p1, q1 = line_points(l1)
    p2, q2 = line_points(l2)
    d1, d2 = q1 - p1, q2 - p2
    m = np.array([[d1[0], -d2[0]], [d1[1], -d2[1]]])
    t, _ = np.linalg.solve(m, (p2 - p1)[:2])
    return p1 + t * d1


def foot_of_perpendicular(point, p, q):
    d = q - p
    return p + np.dot(point - p, d) / np.dot(d, d) * d


def dist_point_line(point, p, q):
    return float(np.linalg.norm(point - foot_of_perpendicular(point, p, q)))


def dist_point_segment(x, a, b):
    t = np.clip(np.dot(x - a, b - a) / np.dot(b - a, b - a), 0, 1)
    return float(np.linalg.norm(x - (a + t * (b - a))))


def all_pairs(lines, points):
    """Bütün (kəsişmə nöqtəsi, onu keçməyən xətt) cütləri məsafəyə görə sıralı."""
    pairs = []
    for ij, x in points.items():
        for k, line in enumerate(lines):
            if k not in ij:
                pairs.append((dist_point_line(x, *line_points(line)), ij, k))
    return sorted(pairs)


def free_spot(anchor, lines=(), segments=(), points=(), radii=(0.32, 0.42, 0.55),
              n=24, keep_out=()):
    """Etiket üçün anchor ətrafında xətlərdən, seqmentlərdən və nöqtələrdən
    ən uzaq yeri tapır (mətn heç nəyin üstünə düşməsin)."""
    best, best_score = anchor + radii[0] * UP, -np.inf
    for r in radii:
        for k in range(n):
            c = anchor + r * direction(360 * k / n)
            if not on_stage(c, margin=0.3):
                continue
            if any(x0 <= c[0] <= x1 and y0 <= c[1] <= y1 for x0, x1, y0, y1 in keep_out):
                continue
            clear = min(
                [dist_point_line(c, *line_points(l)) for l in lines]
                + [dist_point_segment(c, a, b) for a, b in segments]
                + [np.linalg.norm(c - p) for p in points if np.linalg.norm(p - anchor) > 0.05]
                + [10.0]
            )
            score = min(clear, 0.45) - 0.08 * r
            if score > best_score:
                best, best_score = c, score
    return best


# ═════════════════════════════════════════════════════════════════════════════
#  MƏTN VƏ İŞARƏLƏR
# ═════════════════════════════════════════════════════════════════════════════
def tex(*pieces, size=FORMULA_SIZE):
    """MathTex hissələrlə: hər hissə ya sətir, ya da (sətir, rəng)."""
    texs = [p if isinstance(p, str) else p[0] for p in pieces]
    mob = MathTex(*texs, font_size=size, color=TEXT_COLOR)
    for part, piece in zip(mob, pieces):
        if not isinstance(piece, str):
            part.set_color(piece[1])
    return mob


@lru_cache(maxsize=None)
def _space_width(size):
    return (Text("a a", font=FONT, font_size=size).width
            - Text("aa", font=FONT, font_size=size).width)


def rich(*parts, size=CAPTION_SIZE):
    """Bir sətirlik qarışıq mətn. Adi hissələr Text, "$...$" hissələr MathTex.
    Hissə: "sətir", ("sətir", rəng) və ya [(tex, rəng), ...] (rəngli MathTex).
    Bütün hissələr eyni baza xəttinə (y = 0) düzülür."""
    space = _space_width(size)
    gap = 0.035 * size / 30
    row, cursor, pending_space = VGroup(), 0.0, False
    for part in parts:
        if isinstance(part, list):                      # rəngli MathTex hissələri
            mob = tex(*part, "x", size=size * MATH_SCALE)
            lead = trail = False
        else:
            text, color = (part, TEXT_COLOR) if isinstance(part, str) else part
            if not text.strip():                        # yalnız boşluq
                pending_space = True
                continue
            if len(text) > 1 and text[0] == text[-1] == "$":
                mob = MathTex(text[1:-1], "x", font_size=size * MATH_SCALE, color=color)
                lead = trail = False
            else:
                lead, trail = text.startswith(" "), text.endswith(" ")
                mob = Text(text.strip() + "x", font=FONT, font_size=size, color=color)
        # sona əlavə olunmuş "x" baza xəttini göstərir, sonra silinir
        ref = mob[-1]
        baseline = ref.get_bottom()[1]
        mob.remove(ref)
        if len(row):
            cursor += space if (lead or pending_space) else gap
        mob.shift(np.array([cursor - mob.get_left()[0], -baseline, 0.0]))
        cursor = mob.get_right()[0]
        pending_space = trail
        row.add(mob)
    return row


def caption(*parts):
    row = rich(*parts, size=CAPTION_SIZE)
    if row.width > config.frame_width - 0.8:
        row.scale_to_fit_width(config.frame_width - 0.8)
    return row.set_x(0).shift(CAPTION_BASELINE * UP)


def label(tex, color, size=LABEL_SIZE):
    return MathTex(tex, color=color, font_size=size).set_z_index(6)


def dot(x, color=POINT_COLOR, radius=DOT_R):
    return Dot(x, radius=radius, color=color).set_z_index(5)


def cross_mark(center, size=0.2, color=P_COLOR, width=6):
    """✗ işarəsi — iki sadə xəttdən."""
    h = size / 2
    return VGroup(
        Line(center + pt(-h, -h), center + pt(h, h), stroke_width=width),
        Line(center + pt(-h, h), center + pt(h, -h), stroke_width=width),
    ).set_color(color).set_z_index(6)


def glow(mob, color, layers=((8, 0.30), (16, 0.14), (28, 0.06))):
    """Yumşaq parıltı: konturun bir neçə enli, solğun surəti."""
    return VGroup(*[
        mob.copy().set_fill(opacity=0).set_stroke(color, width=w, opacity=o)
        for w, o in layers
    ])


def perp_marker(point, p, q, color, side=1, dashed=True, width=H_W):
    """Nöqtədən pq xəttinə qırıq perpendikulyar + oturacaqda düz bucaq işarəsi."""
    f = foot_of_perpendicular(point, p, q)
    if dashed:
        seg = DashedLine(point, f, dash_length=DASH, stroke_width=width, color=color)
    else:
        seg = Line(point, f, stroke_width=width, color=color)
    along = side * unit(q - p)
    mark = RightAngle(Line(f, point), Line(f, f + along), length=RA_SIZE,
                      quadrant=(1, 1), stroke_width=2.5, color=color)
    return VGroup(seg.set_z_index(3), mark.set_z_index(3))


def show_pair(point, line_obj, value, label_pos):
    """Səhnə 3: "cütü göstər" — nöqtə yanır, xətt narıncı olur, qırıq
    perpendikulyar çəkilir, məsafə (DecimalNumber) 0-dan qiymətinə qədər sayır.
    (animasiya, müvəqqəti obyektlər) qaytarır."""
    f = foot_of_perpendicular(point, line_obj.p, line_obj.q)
    spot = dot(point, POINT_COLOR, DOT_R * 1.15)
    perp = DashedLine(point, f, dash_length=DASH, stroke_width=3, color=TEXT_COLOR).set_z_index(3)
    number = DecimalNumber(0, num_decimal_places=2, font_size=26, color=TEXT_COLOR)
    number.move_to(label_pos).set_z_index(6)
    anim = AnimationGroup(
        FadeIn(spot, scale=0.4),
        Flash(point, color=POINT_COLOR, line_length=0.15, flash_radius=0.2, num_lines=10),
        line_obj.animate.set_stroke(ELL_COLOR, width=LINE_W * 1.5),
        Create(perp),
        ChangeDecimalToValue(number, value),
    )
    temps = VGroup(spot, perp, number)
    temps.number = number
    return anim, temps


def base_switch(triangle_copy, base_start, base_end, about_point):
    """Səhnə 7: surəti elə fırladır ki, base_start→base_end tərəfi aşağıda üfüqi
    olsun (üçüncü təpə yuxarıda qalır). Rotate — nöqtələri xətti yox, bucaqla
    hərəkət etdirir, ona görə üçbucaq yolda əyilmir."""
    angle = -angle_of(base_end - base_start)
    return Rotate(triangle_copy, angle=angle, about_point=about_point)


def similarity(t, src_foot, src_point, dst_foot, dst_point):
    """t ∈ [0, 1] üçün hamar oxşarlıq çevirməsi (sürüşmə + fırlanma + miqyas):
    t = 0 — eynilik, t = 1 — src_foot→dst_foot, src_point→dst_point."""
    v0, v1 = src_point - src_foot, dst_point - dst_foot
    k = np.linalg.norm(v1) / np.linalg.norm(v0)
    turn = (angle_of(v1) - angle_of(v0) + PI) % TAU - PI
    center = interpolate(src_foot, dst_foot, t)
    scale, angle = k ** t, turn * t
    return lambda x: center + scale * rotate_vec(x - src_foot, angle)


def slerp_offset(v0, v1, t):
    """İki etiket sürüşməsi arasında bucaq və uzunluq üzrə hamar keçid."""
    a0, a1 = angle_of(v0), angle_of(v1)
    da = (a1 - a0 + PI) % TAU - PI
    r = interpolate(np.linalg.norm(v0), np.linalg.norm(v1), t)
    return r * direction(np.degrees(a0 + da * t))


# ═════════════════════════════════════════════════════════════════════════════
#  VİDEO
# ═════════════════════════════════════════════════════════════════════════════
class ConcurrentLines(Scene):
    def say(self, *parts, extra=(), run_time=T_FAST):
        """Aşağıdakı izah mətnini yenisi ilə əvəz edir (bir sətir)."""
        new = caption(*parts)
        anims = [FadeIn(new, shift=0.15 * UP)]
        if self.cap is not None:
            anims.append(FadeOut(self.cap, shift=0.15 * UP))
        self.play(*anims, *extra, run_time=run_time)
        self.cap = new

    def unsay(self, extra=(), run_time=T_FAST):
        if self.cap is not None:
            self.play(FadeOut(self.cap), *extra, run_time=run_time)
            self.cap = None

    def construct(self):
        self.camera.background_color = BLACK
        self.cap = None
        self.scene1_problem()
        self.scene2_assumption()
        self.scene3_pairs()
        self.scene4_three_lines()
        self.scene5_pigeonhole()
        self.scene6_inequality()
        self.scene7_area_trick()
        self.scene8_contradiction()
        self.scene9_conclusion()

    # ─────────────────────────────────────────────────────────────────────────
    #  SƏHNƏ 1 — Məsələ (≈12 san)
    # ─────────────────────────────────────────────────────────────────────────
    def scene1_problem(self):
        lines = VGroup(*[full_line(*line_through(p, a)) for p, a in SCENE1_LINES])
        self.play(LaggedStart(*[Create(l) for l in lines], lag_ratio=0.15), run_time=T_SLOW)
        self.say("Sonlu sayda düz xətt, heç ikisi paralel deyil")
        self.wait(PAUSE)

        i, j = SCENE1_PAIR
        x = intersect(lines[i], lines[j])
        spot = dot(x)
        self.play(
            *[l.animate.set_stroke(width=LINE_W * 1.8) for k, l in enumerate(lines) if k in (i, j)],
            *[l.animate.set_stroke(opacity=BG_OPACITY) for k, l in enumerate(lines) if k not in (i, j)],
            run_time=T_FAST,
        )
        self.play(FadeIn(spot, scale=0.3), Flash(x, color=POINT_COLOR, flash_radius=0.3),
                  run_time=T_FAST)
        self.say("Hər kəsişmədən daha bir xətt keçməlidir")
        self.wait(PAUSE)
        self.play(FadeOut(lines), FadeOut(spot), run_time=T_FAST)

        # İki kiçik nümunə: dəstə (şərt ödənir) və üçbucaq (ödənmir)
        pencil = VGroup(*[
            Line(EX_LEFT - PENCIL_HALF * direction(a), EX_LEFT + PENCIL_HALF * direction(a),
                 color=LINE_COLOR, stroke_width=LINE_W)
            for a in PENCIL_ANGLES
        ])
        pencil_dot = dot(EX_LEFT)
        check = MathTex(r"\checkmark", color=FINAL_COLOR, font_size=80)
        check.move_to(EX_LEFT + 2.45 * DOWN)

        verts = [EX_RIGHT + TRI_RADIUS * direction(90 + 120 * k) for k in range(3)]
        sides = VGroup()
        for k in range(3):
            a, b = verts[k], verts[(k + 1) % 3]
            sides.add(Line(a + TRI_EXT * unit(a - b), b + TRI_EXT * unit(b - a),
                           color=LINE_COLOR, stroke_width=LINE_W))
        tri_dots = VGroup(*[dot(v) for v in verts])
        crosses = VGroup(*[cross_mark(v + 0.5 * unit(v - EX_RIGHT)) for v in verts])

        self.play(LaggedStart(*[GrowFromCenter(l) for l in pencil], lag_ratio=0.12),
                  LaggedStart(*[Create(s) for s in sides], lag_ratio=0.2), run_time=T_MED)
        self.play(FadeIn(pencil_dot, scale=0.3), FadeIn(tri_dots, scale=0.3), run_time=T_FAST / 2)
        self.play(Write(check), Flash(EX_LEFT, color=FINAL_COLOR, flash_radius=0.35),
                  run_time=T_FAST)
        self.play(LaggedStart(*[Create(c) for c in crosses], lag_ratio=0.25), run_time=T_FAST)
        self.play(Wiggle(crosses, scale_value=1.25), run_time=T_MED)
        self.say("İsbat et: bütün xətlər bir nöqtədən keçir")
        self.wait(2 * PAUSE)
        self.play(FadeOut(VGroup(pencil, pencil_dot, check, sides, tri_dots, crosses)),
                  run_time=T_FAST)

    # ─────────────────────────────────────────────────────────────────────────
    #  SƏHNƏ 2 — Ziddiyyət fərziyyəsi (≈8 san)
    # ─────────────────────────────────────────────────────────────────────────
    def scene2_assumption(self):
        self.say("Fərz edək: xətlər bir nöqtədən keçmir")
        lines = VGroup(*[full_line(*line_through(p, a)) for p, a in SCHEMATIC_LINES])
        points = {ij: intersect(lines[ij[0]], lines[ij[1]])
                  for ij in combinations(range(len(lines)), 2)}
        dots = VGroup(*[dot(x, radius=SMALL_DOT_R) for x in points.values() if on_stage(x)])
        self.play(LaggedStart(*[Create(l) for l in lines], lag_ratio=0.12), run_time=T_SLOW)
        self.play(LaggedStart(*[FadeIn(d, scale=0.3) for d in dots], lag_ratio=0.06),
                  run_time=T_FAST)
        self.wait(PAUSE)

        # Bu şəkil Səhnə 9-da geri qayıdır — toxunulmamış surətini saxlayırıq
        self.sch_saved = VGroup(lines.copy(), dots.copy())
        self.sch_lines, self.sch_dots, self.sch_points = lines, dots, points

        ij, k = SCENE2_PICK
        x = points[ij]
        spot = dot(x, radius=DOT_R * 1.2)
        self.play(FadeIn(spot, scale=0.3), Flash(x, color=POINT_COLOR, flash_radius=0.3),
                  run_time=T_FAST)
        self.play(lines[k].animate.set_stroke(ELL_COLOR, width=LINE_W * 1.6), run_time=T_FAST)
        self.say("Onda hər kəsişməni keçməyən bir xətt var")
        self.wait(3 * PAUSE)
        self.play(FadeOut(spot), lines[k].animate.set_stroke(LINE_COLOR, width=LINE_W),
                  run_time=T_FAST)

    # ─────────────────────────────────────────────────────────────────────────
    #  SƏHNƏ 3 — Cütlər və ən kiçik məsafə (≈14 san)
    # ─────────────────────────────────────────────────────────────────────────
    def scene3_pairs(self):
        lines, dots, points = self.sch_lines, self.sch_dots, self.sch_points
        keep_out = [(2.3, 7.2, 1.9, 4.1)]          # ədəd oxu və düstur sahəsi

        axis = NumberLine(x_range=[0, AXIS_MAX, 1], length=AXIS_LENGTH, color=AXIS_COLOR,
                          stroke_width=2, tick_size=0.05, include_tip=False)
        axis.move_to(AXIS_CENTER)
        zero = MathTex("0", font_size=24, color=AXIS_COLOR).next_to(axis.n2p(0), DOWN, buff=0.12)
        axis_group = VGroup(axis, zero)
        self.say("Cüt: kəsişmə nöqtəsi + onu keçməyən xətt",
                 extra=[Create(axis), FadeIn(zero)])

        def axis_dot(d):
            return Dot(axis.n2p(d), radius=0.045, color=TEXT_COLOR).set_z_index(5)

        pairs = all_pairs(lines, points)
        demo = set(SCENE3_DEMO)

        # İlk cütlər bir-bir: perpendikulyar + məsafə → oxda nöqtə
        for ij, k in SCENE3_DEMO:
            x, line = points[ij], lines[k]
            d = dist_point_line(x, line.p, line.q)
            f = foot_of_perpendicular(x, line.p, line.q)
            spot_pos = free_spot((x + f) / 2, lines=lines, segments=[(x, f)],
                                 points=list(points.values()), keep_out=keep_out)
            anim, temps = show_pair(x, line, d, spot_pos)
            self.play(anim, run_time=T_PAIR_IN)
            target = axis_dot(d)
            axis_group.add(target)
            self.play(TransformFromCopy(temps.number, target), FadeOut(temps),
                      line.animate.set_stroke(LINE_COLOR, width=LINE_W), run_time=T_PAIR_OUT)

        # Qalan bütün cütlər birdən
        rest = [axis_dot(d) for d, ij, k in pairs if (ij, k) not in demo]
        axis_group.add(*rest)
        self.play(LaggedStart(*[FadeIn(r, shift=0.2 * DOWN) for r in rest], lag_ratio=0.04),
                  run_time=T_MED)

        # Ən kiçik məsafə
        h_min, ij0, k0 = pairs[0]
        min_dot = next(m for m in axis_group[2:] if np.allclose(m.get_center(), axis.n2p(h_min)))
        self.say("Cütlər sonludur → ən kiçik məsafə var")
        self.play(min_dot.animate.set_color(P_COLOR).scale(1.5),
                  Circumscribe(min_dot, shape=Circle, color=P_COLOR, buff=0.08,
                               stroke_width=3),
                  run_time=T_MED)

        p_s, ell_s = points[ij0], lines[k0]
        f_s = foot_of_perpendicular(p_s, ell_s.p, ell_s.q)
        others = [l for k, l in enumerate(lines) if k != k0]
        avoid = dict(lines=lines, segments=[(p_s, f_s)], points=list(points.values()),
                     keep_out=keep_out)
        p_off0 = free_spot(p_s, **avoid) - p_s
        h_off0 = free_spot((p_s + f_s) / 2, **avoid) - (p_s + f_s) / 2
        ell_anchor = f_s + 1.3 * unit(ell_s.q - ell_s.p) * np.sign(
            np.dot(ell_s.q - ell_s.p, RIGHT) or 1)
        ell_lab_pos = free_spot(ell_anchor, **avoid)

        p_dot = dot(p_s, P_COLOR)
        h_seg = Line(p_s, f_s, color=P_COLOR, stroke_width=H_W).set_z_index(3)
        p_lab = label("P", P_COLOR).move_to(p_s + p_off0)
        h_lab = label("h", P_COLOR).move_to((p_s + f_s) / 2 + h_off0)
        ell_lab = label(r"\ell", ELL_COLOR).move_to(ell_lab_pos)

        self.play(*[l.animate.set_stroke(opacity=BG_OPACITY) for l in others],
                  dots.animate.set_opacity(BG_OPACITY),
                  ell_s.animate.set_stroke(ELL_COLOR, width=LINE_W * 1.4),
                  FadeIn(p_dot, scale=0.3), Flash(p_s, color=P_COLOR, flash_radius=0.3),
                  run_time=T_FAST)
        self.play(Create(h_seg), FadeIn(p_lab), FadeIn(h_lab), FadeIn(ell_lab),
                  run_time=T_FAST)

        formula = rich([("h", P_COLOR), "=", "d(", ("P", P_COLOR), ",", (r"\ell", ELL_COLOR), ")"],
                       " — ən kiçik", size=30)
        formula.move_to(SCENE3_FORMULA_POS)
        formula.shift(LEFT * max(0.0, formula.get_right()[0] - (FRAME_X - 0.35)))
        self.play(FadeIn(formula, shift=0.2 * DOWN), run_time=T_FAST)
        self.wait(2 * PAUSE)

        # ── P, ℓ və h hamar oxşarlıq çevirməsi ilə kanonik diaqrama keçir ──
        tracker = ValueTracker(0)
        canon_p_off = 0.4 * direction(8)            # kanonikdə P etiketi sağda
        canon_h_off = 0.38 * LEFT                   # h etiketi PH-ın solunda
        ell_dir = unit(ell_s.q - ell_s.p)

        def S():
            return similarity(tracker.get_value(), f_s, p_s, H_PT, P_PT)

        def moving_ell():
            s = S()
            return full_line(s(f_s), s(f_s + ell_dir), color=ELL_COLOR, width=LINE_W * 1.4)

        def moving_p():
            return dot(S()(p_s), P_COLOR)

        def moving_h():
            s = S()
            return Line(s(p_s), s(f_s), color=P_COLOR, stroke_width=H_W).set_z_index(3)

        def moving_p_lab():
            t = tracker.get_value()
            return label("P", P_COLOR).move_to(S()(p_s) + slerp_offset(p_off0, canon_p_off, t))

        def moving_h_lab():
            t, s = tracker.get_value(), S()
            mid = (s(p_s) + s(f_s)) / 2
            return label("h", P_COLOR).move_to(mid + slerp_offset(h_off0, canon_h_off, t))

        movers = VGroup(*[always_redraw(f) for f in
                          (moving_ell, moving_h, moving_p, moving_p_lab, moving_h_lab)])
        self.add(movers)
        self.remove(p_dot, h_seg, p_lab, h_lab)
        self.unsay(extra=[FadeOut(axis_group), FadeOut(formula), FadeOut(lines),
                          FadeOut(dots), FadeOut(ell_lab)])
        self.play(tracker.animate.set_value(1), run_time=T_SLOW, rate_func=smooth)

        # Kanonik obyektlər (eyni yerdə statik surətlər)
        self.remove(movers)
        self.ell = full_line(H_PT, H_PT + RIGHT, color=ELL_COLOR, width=LINE_W * 1.4)
        self.p_dot = dot(P_PT, P_COLOR)
        self.h_seg = Line(P_PT, H_PT, color=P_COLOR, stroke_width=H_W).set_z_index(3)
        self.p_lab = label("P", P_COLOR).move_to(P_PT + canon_p_off)
        self.h_lab = label("h", P_COLOR).move_to((P_PT + H_PT) / 2 + canon_h_off)
        self.ell_lab = label(r"\ell", ELL_COLOR).move_to(pt(6.55, ELL_Y + 0.32))
        self.add(self.ell, self.h_seg, self.p_dot, self.p_lab, self.h_lab)
        self.play(FadeIn(self.ell_lab), run_time=T_FAST / 2)

        self.axis_group, self.axis, self.min_dot, self.h_min = axis_group, axis, min_dot, h_min

    # ─────────────────────────────────────────────────────────────────────────
    #  SƏHNƏ 4 — P-dən keçən üç xətt (≈12 san)
    # ─────────────────────────────────────────────────────────────────────────
    def scene4_three_lines(self):
        h_dash = DashedLine(P_PT, H_PT, dash_length=DASH, stroke_width=H_W,
                            color=P_COLOR).set_z_index(3)
        h_dot = dot(H_PT, FOOT_COLOR, radius=DOT_R * 0.85)
        h_name = label("H", FOOT_COLOR).move_to(H_PT + H_LAB_OFF)
        right = RightAngle(Line(H_PT, P_PT), Line(H_PT, H_PT + RIGHT), length=RA_SIZE,
                           quadrant=(1, 1), stroke_width=2.5, color=P_COLOR).set_z_index(3)
        self.play(ReplacementTransform(self.h_seg, h_dash), FadeIn(h_dot, scale=0.3),
                  FadeIn(h_name), Create(right), run_time=T_MED)
        self.h_dash, self.h_dot, self.h_name, self.right_h = h_dash, h_dot, h_name, right

        self.say(("$P$", P_COLOR), " iki xəttin kəsişməsidir → ondan ən azı üç xətt keçir")
        self.wait(2 * PAUSE)

        # Xətlər P-dən hər iki tərəfə "böyüyür"
        self.pc = full_line(P_PT, C_PT)
        self.pa = full_line(P_PT, A_PT)
        self.pb = full_line(P_PT, B_PT)
        for l in (self.pc, self.pa, self.pb):
            l.set_z_index(0)
            self.play(GrowFromPoint(l, P_PT), run_time=T_FAST * 1.3)

        self.say("Heç biri ", ("$\\ell$", ELL_COLOR), "-ə paralel deyil → hamısı ",
                 ("$\\ell$", ELL_COLOR), "-i kəsir")
        # kəsişmə nöqtələri numpy ilə (A_PT, B_PT, C_PT ilə üst-üstə düşür)
        hits = [intersect(l, self.ell) for l in (self.pc, self.pa, self.pb)]
        self.c_dot, self.a_dot, self.b_dot = [dot(x) for x in hits]
        self.play(LaggedStart(*[
            AnimationGroup(FadeIn(d, scale=0.3), Flash(d.get_center(), color=POINT_COLOR,
                                                       flash_radius=0.28))
            for d in (self.c_dot, self.a_dot, self.b_dot)], lag_ratio=0.35), run_time=T_MED)
        self.wait(PAUSE)
        self.say("Bu nöqtələr fərqlidir")
        self.play(*[Indicate(d, color=POINT_COLOR, scale_factor=1.8)
                    for d in (self.c_dot, self.a_dot, self.b_dot)], run_time=T_MED)

        # Niyə: P-dən keçən xətt ℓ-i başqa xəttin nöqtəsində kəssə, o xəttin özü olar
        turn = ValueTracker(angle_of(B_PT - P_PT))

        def ghost_line():
            return full_line(P_PT, P_PT + rotate_vec(RIGHT, turn.get_value()),
                             color=TEXT_COLOR, width=LINE_W, opacity=0.8).set_z_index(1)

        def ghost_hit():
            return dot(intersect(ghost_line(), self.ell), TEXT_COLOR, DOT_R * 0.8).set_z_index(6)

        ghost, hit = always_redraw(ghost_line), always_redraw(ghost_hit)
        self.play(FadeIn(ghost), FadeIn(hit), run_time=T_FAST / 2)
        self.play(turn.animate.set_value(angle_of(A_PT - P_PT)), run_time=T_MED, rate_func=smooth)
        ghost.clear_updaters()
        hit.clear_updaters()
        self.play(Indicate(self.pa, color=TEXT_COLOR, scale_factor=1.0),
                  Flash(A_PT, color=TEXT_COLOR, flash_radius=0.3), run_time=T_FAST)
        self.play(FadeOut(ghost), FadeOut(hit), run_time=T_FAST / 2)
        self.wait(PAUSE)

    # ─────────────────────────────────────────────────────────────────────────
    #  SƏHNƏ 5 — Göyərçin yuvası prinsipi (≈10 san)
    # ─────────────────────────────────────────────────────────────────────────
    def scene5_pigeonhole(self):
        left_end, right_end = clip_to_stage(H_PT + LEFT, H_PT + RIGHT)
        if left_end[0] > right_end[0]:
            left_end, right_end = right_end, left_end
        ray_l = Line(H_PT, left_end, color=RAY_TONES[0], stroke_width=LINE_W * 2.2).set_z_index(1)
        ray_r = Line(H_PT, right_end, color=RAY_TONES[1], stroke_width=LINE_W * 2.2).set_z_index(1)
        arrow_l = Arrow(pt(-5.75, ELL_Y + 0.38), pt(-6.85, ELL_Y + 0.38), buff=0,
                        color=RAY_TONES[0], stroke_width=4, max_tip_length_to_length_ratio=0.3)
        arrow_r = Arrow(pt(3.0, ELL_Y + 0.38), pt(4.4, ELL_Y + 0.38), buff=0,
                        color=RAY_TONES[1], stroke_width=4, max_tip_length_to_length_ratio=0.25)
        self.play(Create(ray_l), Create(ray_r), GrowArrow(arrow_l), GrowArrow(arrow_r),
                  Flash(H_PT, color=FOOT_COLOR, flash_radius=0.3), run_time=T_MED)
        self.say(("$H$", FOOT_COLOR), " nöqtəsi ", ("$\\ell$", ELL_COLOR), "-i iki şüaya bölür")
        self.wait(PAUSE)

        # Kiçik sxem: 3 nöqtə, 2 qutu
        box_l = RoundedRectangle(corner_radius=0.12, width=1.5, height=0.8)
        box_l.set_stroke(RAY_TONES[0], 3).move_to(SCHEMA_LEFT)
        box_r = RoundedRectangle(corner_radius=0.12, width=1.5, height=0.8)
        box_r.set_stroke(RAY_TONES[1], 3).move_to(SCHEMA_RIGHT)
        self.play(Create(box_l), Create(box_r), run_time=T_FAST)
        flyers = VGroup(*[d.copy() for d in (self.c_dot, self.a_dot, self.b_dot)])
        slots = [SCHEMA_LEFT, SCHEMA_RIGHT + 0.32 * LEFT, SCHEMA_RIGHT + 0.32 * RIGHT]
        self.play(LaggedStart(*[f.animate(path_arc=-0.6).move_to(s)
                                for f, s in zip(flyers, slots)], lag_ratio=0.25),
                  run_time=T_MED)
        self.play(box_r.animate.set_fill(RAY_TONES[1], opacity=0.25),
                  Indicate(flyers[1:], color=POINT_COLOR, scale_factor=1.5), run_time=T_FAST)
        self.say("3 nöqtə, 2 şüa → ikisi eyni tərəfdədir")
        self.wait(PAUSE)

        # Eyni şüadakı iki nöqtə: H-a yaxın A, uzaq B; üçüncü C zəifləyir
        self.a_lab = label("A", POINT_COLOR).move_to(A_PT + A_LAB_OFF)
        self.b_lab = label("B", POINT_COLOR).move_to(B_PT + B_LAB_OFF)
        self.c_lab = label("C", POINT_COLOR).move_to(C_PT + C_LAB_OFF)
        self.play(Indicate(self.a_dot, color=POINT_COLOR, scale_factor=1.8),
                  Indicate(self.b_dot, color=POINT_COLOR, scale_factor=1.8),
                  FadeIn(self.a_lab, shift=0.15 * UP), FadeIn(self.b_lab, shift=0.15 * UP),
                  run_time=T_FAST)
        self.play(FadeIn(self.c_lab), run_time=T_FAST / 2)
        self.play(self.pc.animate.set_stroke(opacity=DIM_OPACITY),
                  self.c_dot.animate.set_opacity(DIM_OPACITY),
                  self.c_lab.animate.set_opacity(DIM_OPACITY), run_time=T_FAST)

        order = tex(("H", FOOT_COLOR), r"\;\text{---}\;", ("A", POINT_COLOR),
                     r"\;\text{---}\;", ("B", POINT_COLOR)).move_to(ORDER_POS)
        self.play(FadeIn(order, shift=0.2 * UP), run_time=T_FAST)
        self.wait(3 * PAUSE)
        self.play(FadeOut(VGroup(ray_l, ray_r, arrow_l, arrow_r, box_l, box_r, flyers, order)),
                  run_time=T_FAST)

    # ─────────────────────────────────────────────────────────────────────────
    #  SƏHNƏ 6 — Əsas bərabərsizlik AB < PB (≈12 san)
    # ─────────────────────────────────────────────────────────────────────────
    def scene6_inequality(self):
        a_x = ValueTracker(A_PT[0])

        def a_pos():
            return pt(a_x.get_value(), ELL_Y)

        # A-ya bağlı obyektlər updater ilə A-nı izləyir
        self.a_dot.add_updater(lambda m: m.move_to(a_pos()))
        self.a_lab.add_updater(lambda m: m.move_to(a_pos() + A_LAB_OFF))
        self.pa.add_updater(lambda m: m.put_start_and_end_on(*clip_to_stage(P_PT, a_pos())))
        ab_seg = always_redraw(lambda: Line(a_pos(), B_PT, color=ELL_COLOR,
                                            stroke_width=SEG_W).set_z_index(1))
        ab_brace = always_redraw(lambda: Brace(Line(a_pos(), B_PT), DOWN, buff=0.12,
                                               sharpness=1.2).set_z_index(2))
        ab_text = always_redraw(lambda: label("AB", TEXT_COLOR, 32).next_to(
            Brace(Line(a_pos(), B_PT), DOWN, buff=0.12).get_tip(), DOWN, buff=0.06))
        hb_brace = Brace(Line(H_PT, B_PT), DOWN, buff=0.75, sharpness=1.2).set_z_index(2)
        hb_text = label("HB", TEXT_COLOR, 32).next_to(hb_brace, LEFT, buff=0.12)

        self.play(Create(ab_seg), run_time=T_FAST)
        self.play(GrowFromCenter(ab_brace), FadeIn(ab_text), run_time=T_FAST)
        self.play(GrowFromCenter(hb_brace), FadeIn(hb_text), run_time=T_FAST)

        tri_phb = Polygon(P_PT, H_PT, B_PT, stroke_width=0, fill_color=P_COLOR,
                          fill_opacity=0.25).set_z_index(-1)
        pb_seg = Line(P_PT, B_PT, color=LINE_COLOR, stroke_width=SEG_W).set_z_index(1)
        self.play(FadeIn(tri_phb), Create(pb_seg), run_time=T_FAST)
        self.say(("$PB$", LINE_COLOR), " — düzbucaqlı üçbucağın hipotenuzudur")
        self.play(FadeOut(tri_phb), run_time=T_FAST)

        ineq = tex("AB", r"\le", "HB", "<", "PB").move_to(INEQ_POS)
        ineq2 = tex("AB", "<", "PB").move_to(INEQ_POS)
        self.play(Write(ineq), run_time=T_MED)
        self.wait(PAUSE)
        # "≤ HB" yerində sönür, qalan hədlər TransformMatchingTex ilə yerinə uçur
        # (uyğunu olmayan hədləri əvvəlcədən çıxarırıq, yoxsa onlar mərkəzə uçur)
        dropped = VGroup(ineq[1], ineq[2])
        self.play(FadeOut(dropped, shift=0.25 * DOWN), run_time=T_FAST / 2)
        ineq.remove(*dropped)
        self.play(TransformMatchingTex(ineq, ineq2), run_time=T_FAST)
        self.wait(PAUSE)

        # Kənar hal: A → H (AB = HB), sonra geri
        self.say(("$A = H$", POINT_COLOR), " olsa belə, ", "$AB < PB$", " doğrudur",
                 extra=[a_x.animate.set_value(H_PT[0])], run_time=T_MED * 1.2)
        self.wait(PAUSE)
        self.play(a_x.animate.set_value(A_PT[0]), run_time=T_MED)
        for m in (self.a_dot, self.a_lab, self.pa, ab_seg, ab_brace, ab_text):
            m.clear_updaters()

        frame = SurroundingRectangle(ineq2, color=TEXT_COLOR, buff=0.15, corner_radius=0.1)
        self.play(Create(frame), run_time=T_FAST)
        boxed = VGroup(ineq2, frame)
        self.play(boxed.animate.scale(0.8).move_to(CORNER_POS),
                  FadeOut(VGroup(ab_brace, ab_text, hb_brace, hb_text, ab_seg, pb_seg)),
                  run_time=T_MED)
        self.boxed = boxed

    # ─────────────────────────────────────────────────────────────────────────
    #  SƏHNƏ 7 — Sahə fəndi (ƏSAS AN, ≈20 san)
    # ─────────────────────────────────────────────────────────────────────────
    def scene7_area_trick(self):
        tri = Polygon(P_PT, A_PT, B_PT, stroke_width=0, fill_color=TRI_COLOR,
                      fill_opacity=TRI_OPACITY).set_z_index(-1)
        self.play(FadeIn(tri), run_time=T_FAST)
        self.say("Eyni üçbucaq, iki fərqli oturacaq")

        # Surət sağa uçur (h hündürlüyü ilə birlikdə)
        center = (np.min([P_PT, A_PT, B_PT, H_PT], axis=0) + np.max([P_PT, A_PT, B_PT, H_PT], axis=0)) / 2

        def to_copy(x):
            return COPY_CENTER + COPY_SCALE * (x - center)

        p2, a2, b2, h2 = (to_copy(x) for x in (P_PT, A_PT, B_PT, H_PT))
        tri2 = Polygon(p2, a2, b2, stroke_width=0, fill_color=TRI_COLOR, fill_opacity=TRI_OPACITY)
        edges2 = VGroup(Line(p2, a2, color=LINE_COLOR, stroke_width=LINE_W),
                        Line(a2, b2, color=ELL_COLOR, stroke_width=LINE_W),
                        Line(b2, p2, color=LINE_COLOR, stroke_width=LINE_W))
        body = VGroup(tri2, edges2)
        ext2 = DashedLine(h2, a2, dash_length=0.08, stroke_width=2, color=GREY_B)
        h2_dash = DashedLine(p2, h2, dash_length=0.08, stroke_width=3, color=P_COLOR)
        h2_right = RightAngle(Line(h2, p2), Line(h2, a2), length=0.14, stroke_width=2,
                              color=P_COLOR)
        h2_lab = label("h", P_COLOR, 30).next_to(h2_dash, LEFT, buff=0.1)
        old_h = VGroup(ext2, h2_dash, h2_right, h2_lab)

        def vertex_labels():
            v = body[0].get_vertices()
            g = v.mean(axis=0)
            return VGroup(*[
                label(name, col, 28).move_to(x + 0.28 * unit(x - g))
                for name, col, x in zip("PAB", (P_COLOR, POINT_COLOR, POINT_COLOR), v)
            ])

        names = always_redraw(vertex_labels)
        sides = VGroup(Line(P_PT, A_PT, color=LINE_COLOR, stroke_width=LINE_W),
                       Line(A_PT, B_PT, color=ELL_COLOR, stroke_width=LINE_W),
                       Line(B_PT, P_PT, color=LINE_COLOR, stroke_width=LINE_W))
        self.play(TransformFromCopy(tri, tri2), ReplacementTransform(sides, edges2),
                  TransformFromCopy(self.h_dash, h2_dash), run_time=T_MED * 1.2)
        self.play(FadeIn(names), Create(ext2), Create(h2_right), FadeIn(h2_lab), run_time=T_FAST)

        s1 = tex(("S", TRI_COLOR), "=", r"\tfrac12", r"\cdot", "AB", r"\cdot", ("h", P_COLOR))
        s1.move_to(S1_POS)
        self.play(Write(s1), run_time=T_MED)
        self.wait(PAUSE)

        # Oturacağı dəyiş: PB aşağıda üfüqi olsun
        verts = body[0].get_vertices()
        pivot = verts.mean(axis=0)
        self.play(base_switch(body, verts[2], verts[0], pivot), FadeOut(old_h), run_time=T_SLOW)
        p3, a3, b3 = body[0].get_vertices()
        f3 = foot_of_perpendicular(a3, p3, b3)
        new_h = perp_marker(a3, p3, b3, NEW_COLOR, side=1, width=3)
        new_h[1].scale(0.7, about_point=f3)
        new_h_lab = label("h'", NEW_COLOR, 30).next_to(new_h[0], RIGHT, buff=0.1)
        self.play(Create(new_h), FadeIn(new_h_lab), run_time=T_FAST)
        s2 = tex(("S", TRI_COLOR), "=", r"\tfrac12", r"\cdot", "PB", r"\cdot", ("h'", NEW_COLOR))
        s2.move_to(S2_POS)
        self.play(Write(s2), run_time=T_MED)
        self.wait(PAUSE)

        # Surət sönür; əsas diaqramda A-dan PB-yə yaşıl perpendikulyar
        names.clear_updaters()
        self.play(FadeOut(VGroup(body, names, new_h, new_h_lab)), run_time=T_FAST)
        foot = foot_of_perpendicular(A_PT, P_PT, B_PT)
        self.hp = perp_marker(A_PT, P_PT, B_PT, NEW_COLOR, side=1)
        u_pb = unit(B_PT - P_PT)
        self.hp_lab = label("h'", NEW_COLOR).move_to((A_PT + foot) / 2 + 0.38 * u_pb)
        self.play(Create(self.hp), run_time=T_FAST)
        self.play(FadeIn(self.hp_lab), run_time=T_FAST / 2)
        self.foot = foot

        # Cəbr: ½·AB·h = ½·PB·h'  →  AB·h = PB·h'  →  h' = AB/PB · h
        eq1 = tex(r"\tfrac12", r"\cdot", "AB", r"\cdot", ("h", P_COLOR), "=",
                   r"\tfrac12", r"\cdot", "PB", r"\cdot", ("h'", NEW_COLOR)).move_to(ALG_POS)
        self.play(
            *[ReplacementTransform(s1[i], eq1[i - 2]) for i in range(2, 7)],
            ReplacementTransform(s1[1], eq1[5]),
            *[ReplacementTransform(s2[i], eq1[i + 4]) for i in range(2, 7)],
            FadeOut(s1[0]), FadeOut(s2[0]), FadeOut(s2[1]),
            run_time=T_MED,
        )
        self.wait(PAUSE / 2)
        eq2 = tex("AB", r"\cdot", ("h", P_COLOR), "=", "PB", r"\cdot", ("h'", NEW_COLOR))
        eq2.move_to(ALG_POS)
        halves = VGroup(eq1[0], eq1[1], eq1[6], eq1[7])          # "½ ·" hər iki tərəfdə
        self.play(FadeOut(halves, shift=0.25 * UP), run_time=T_FAST / 2)
        eq1.remove(*halves)
        self.play(TransformMatchingTex(eq1, eq2), run_time=T_FAST)
        self.wait(PAUSE / 2)
        eq3 = tex(("h'", NEW_COLOR), "=", r"\frac{", "AB", "}{", "PB", "}", r"\cdot", ("h", P_COLOR))
        eq3.move_to(ALG_POS)
        self.play(TransformMatchingTex(eq2, eq3, path_arc=PI / 6), run_time=T_MED)
        self.wait(PAUSE / 2)

        fraction = VGroup(*eq3[2:7])
        arrow = Arrow(self.boxed.get_bottom() + 0.3 * LEFT, fraction.get_top() + 0.25 * RIGHT,
                      buff=0.08, stroke_width=3, color=TEXT_COLOR,
                      max_tip_length_to_length_ratio=0.18)
        frac_lt = tex(r"\frac{AB}{PB}", "<", "1", size=FORMULA_SIZE * 0.9)
        frac_lt.next_to(fraction, DOWN, buff=0.35)
        self.play(GrowArrow(arrow), Indicate(self.boxed, color=TEXT_COLOR, scale_factor=1.08),
                  run_time=T_FAST)
        self.play(FadeIn(frac_lt, shift=0.2 * DOWN), run_time=T_FAST)
        self.wait(PAUSE / 2)

        result = tex(("h'", NEW_COLOR), "<", ("h", P_COLOR), size=FORMULA_SIZE * 1.15)
        result.next_to(frac_lt, DOWN, buff=0.45)
        self.play(TransformFromCopy(eq3[0], result[0]), TransformFromCopy(eq3[8], result[2]),
                  FadeIn(result[1]), run_time=T_MED)
        res_frame = SurroundingRectangle(result, color=YELLOW, buff=0.16, corner_radius=0.1,
                                         stroke_width=4)
        self.play(Create(res_frame), FadeIn(glow(res_frame, YELLOW), rate_func=there_and_back),
                  run_time=T_FAST)

        # Vizual müqayisə: h və h' yan-yana şaquli
        h_len = np.linalg.norm(P_PT - H_PT)
        hp_len = np.linalg.norm(A_PT - foot)
        bar_h = Line(H_PT, P_PT, color=P_COLOR, stroke_width=SEG_W - 1)
        bar_hp = Line(A_PT, foot, color=NEW_COLOR, stroke_width=SEG_W - 1)
        tgt_h = Line(pt(BAR_X[0], BAR_BOTTOM), pt(BAR_X[0], BAR_BOTTOM + h_len))
        tgt_hp = Line(pt(BAR_X[1], BAR_BOTTOM), pt(BAR_X[1], BAR_BOTTOM + hp_len))
        bar_h_lab = label("h", P_COLOR, 32).next_to(tgt_h, UP, buff=0.12)
        bar_hp_lab = label("h'", NEW_COLOR, 32).next_to(tgt_hp, UP, buff=0.12)
        base = DashedLine(pt(BAR_X[0] - 0.3, BAR_BOTTOM), pt(BAR_X[1] + 0.3, BAR_BOTTOM),
                          dash_length=0.06, stroke_width=1.5, color=GREY_B)
        self.add(bar_h, bar_hp)
        self.play(bar_h.animate.put_start_and_end_on(tgt_h.get_start(), tgt_h.get_end()),
                  bar_hp.animate.put_start_and_end_on(tgt_hp.get_start(), tgt_hp.get_end()),
                  run_time=T_MED * 1.2)
        self.play(FadeIn(bar_h_lab), FadeIn(bar_hp_lab), Create(base), run_time=T_FAST)
        self.wait(2 * PAUSE)

        self.tri = tri
        self.right_side = VGroup(eq3, arrow, frac_lt, result, res_frame, self.boxed,
                                 bar_h, bar_hp, bar_h_lab, bar_hp_lab, base)

    # ─────────────────────────────────────────────────────────────────────────
    #  SƏHNƏ 8 — Ziddiyyət (≈12 san)
    # ─────────────────────────────────────────────────────────────────────────
    def scene8_contradiction(self):
        self.unsay(extra=[FadeOut(self.right_side)])

        rows = [
            rich(("$A$", POINT_COLOR), " — kəsişmə nöqtəsidir (", ("$\\ell$", ELL_COLOR),
                 " və ", ("$PA$", LINE_COLOR), ")", size=28),
            rich(("$PB$", LINE_COLOR), " — verilmiş xətlərdən biridir", size=28),
            rich(("$PB$", LINE_COLOR), " ", ("$A$", POINT_COLOR), "-dan keçmir, çünki ",
                 [("A", POINT_COLOR), r"\ne", ("B", POINT_COLOR)], size=28),
        ]
        pb_flash = Line(P_PT, B_PT, color=LINE_COLOR, stroke_width=SEG_W)
        targets = [
            [Indicate(self.a_dot, color=POINT_COLOR, scale_factor=2.0)],
            [ShowPassingFlash(pb_flash.copy().set_color(BLUE_A), time_width=0.6),
             Indicate(self.pb, color=BLUE_A, scale_factor=1.0)],
            [Indicate(self.a_dot, color=POINT_COLOR, scale_factor=2.0),
             Indicate(self.b_dot, color=POINT_COLOR, scale_factor=2.0)],
        ]
        checks = VGroup()
        for row, y, anims in zip(rows, CHECK_Y, targets):
            row.shift(np.array([CHECK_X - row.get_left()[0], y, 0.0]))
            tick = MathTex(r"\checkmark", color=NEW_COLOR, font_size=36)
            tick.next_to(row, RIGHT, buff=0.2)
            checks.add(tick)
            self.play(FadeIn(row, shift=0.15 * RIGHT), *anims, run_time=T_MED * 0.8)
            self.play(Write(tick), run_time=T_FAST / 2)

        dist = tex("d(", ("A", POINT_COLOR), ",", ("PB", LINE_COLOR), ")", "=",
                    ("h'", NEW_COLOR), "<", ("h", P_COLOR)).move_to(DIST_POS)
        self.play(Write(dist), Indicate(self.hp_lab, color=NEW_COLOR), run_time=T_MED)
        self.wait(2 * PAUSE)

        # Ədəd oxu geri qayıdır: h-dan solda yeni yaşıl nöqtə (h')
        self.play(FadeIn(self.axis_group), run_time=T_FAST)
        ratio = np.linalg.norm(A_PT - self.foot) / np.linalg.norm(P_PT - H_PT)
        new_dot = Dot(self.axis.n2p(self.h_min * ratio), radius=0.07,
                      color=NEW_COLOR).set_z_index(6)
        self.play(FadeIn(new_dot, shift=0.35 * DOWN, scale=0.5),
                  Flash(self.axis.n2p(self.h_min * ratio), color=NEW_COLOR, flash_radius=0.2),
                  run_time=T_FAST)

        border = Rectangle(width=config.frame_width, height=config.frame_height)
        border.set_stroke(P_COLOR, width=14, opacity=0.9).set_fill(opacity=0)
        border_glow = VGroup(border, glow(border, P_COLOR, ((30, 0.35), (60, 0.15))))
        self.play(Wiggle(self.min_dot, scale_value=1.8, rotation_angle=0.1 * TAU),
                  FadeIn(border_glow, rate_func=there_and_back), run_time=T_MED * 1.2)
        self.say("Ziddiyyət! ", ("$h$", P_COLOR), " ən kiçik məsafə deyildi")
        self.wait(4 * PAUSE)
        self.remove(border_glow)
        self.checklist = VGroup(*rows, checks, dist, new_dot)

    # ─────────────────────────────────────────────────────────────────────────
    #  SƏHNƏ 9 — Nəticə (≈10 san)
    # ─────────────────────────────────────────────────────────────────────────
    def scene9_conclusion(self):
        everything = Group(*[m for m in self.mobjects if m is not self.cap])
        self.unsay(extra=[FadeOut(everything)])

        lines, dots = self.sch_saved
        self.play(FadeIn(lines), FadeIn(dots), run_time=T_FAST)
        self.play(lines.animate.set_color(P_COLOR), run_time=T_FAST)
        self.play(*[Wiggle(l, scale_value=1.0, rotation_angle=0.015 * TAU) for l in lines],
                  run_time=T_MED * 0.8)
        self.say("Bu şəkil mümkün deyil")
        self.wait(PAUSE)

        # Hər xətt bucağını saxlayır, yalnız ortaq nöqtəyə doğru sürüşür
        t = ValueTracker(0)
        base = [(l.p, l.q) for l in lines]
        shifts = [CONCURRENCY_POINT - foot_of_perpendicular(CONCURRENCY_POINT, p, q)
                  for p, q in base]

        def moving_lines():
            s = t.get_value()
            col = interpolate_color(P_COLOR, LINE_COLOR, s)
            return VGroup(*[full_line(p + s * d, q + s * d, color=col)
                            for (p, q), d in zip(base, shifts)])

        def moving_dots():
            current = moving_lines()
            xs = [intersect(current[i], current[j])
                  for i, j in combinations(range(len(current)), 2)]
            return VGroup(*[dot(x, radius=SMALL_DOT_R) for x in xs if on_stage(x)])

        mover_lines, mover_dots = always_redraw(moving_lines), always_redraw(moving_dots)
        self.add(mover_lines, mover_dots)
        self.remove(lines, dots)
        self.play(t.animate.set_value(1), run_time=T_SLOW * 1.2, rate_func=smooth)
        mover_lines.clear_updaters()
        mover_dots.clear_updaters()

        center = dot(CONCURRENCY_POINT, FINAL_COLOR, DOT_R * 1.4).set_z_index(7)
        self.play(FadeIn(center, scale=0.3), FadeOut(mover_dots),
                  Flash(CONCURRENCY_POINT, color=FINAL_COLOR, flash_radius=0.7,
                        line_length=0.35, num_lines=16),
                  run_time=T_MED)
        self.say("Deməli, bütün xətlər bir nöqtədən keçir ", "$\\blacksquare$")
        self.wait(FINAL_HOLD)
        self.play(FadeOut(Group(*self.mobjects)), run_time=T_MED)
