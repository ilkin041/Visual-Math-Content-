#!/usr/bin/env bash
# Tam keyfiyyət: hər hissə 1080p, 60 fps ayrıca mp4; sonra ffmpeg concat ilə tam_video.mp4.
#   ./render_all.sh               # ardıcıl render
#   JOBS=4 ./render_all.sh        # paralel render (hər hissə ayrı prosesdə)
# Hissələr: media/videos/ekstremal_prinsip/1080p60/HisseXX_*.mp4
# Tam video: tam_video.mp4 (bu qovluqda)
set -euo pipefail
cd "$(dirname "$0")"
MANIM=${MANIM:-manim}
JOBS=${JOBS:-1}
OUT_DIR=media/videos/ekstremal_prinsip/1080p60
SCENES=(Hisse00_Giris Hisse01_Isinme Hisse02_Silvester Hisse03_Dual Hisse04_Neticeler
        Hisse05_Serhedler Hisse06_Yekun Hisse07_Hell1 Hisse08_Hell2 Hisse09_Hell3
        Hisse10_Hell4)

printf '%s\n' "${SCENES[@]}" | \
    xargs -P "$JOBS" -I{} "$MANIM" -qh --fps 60 ekstremal_prinsip.py {}

LIST=$(mktemp)
trap 'rm -f "$LIST"' EXIT
for s in "${SCENES[@]}"; do
    f="$OUT_DIR/$s.mp4"
    [ -f "$f" ] || { echo "Tapılmadı: $f" >&2; exit 1; }
    echo "file '$PWD/$f'" >> "$LIST"
done
ffmpeg -y -loglevel error -f concat -safe 0 -i "$LIST" -c copy tam_video.mp4
echo "Hazırdır: tam_video.mp4"
for s in "${SCENES[@]}"; do
    printf '%-20s %8.1f san\n' "$s" \
        "$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT_DIR/$s.mp4")"
done
printf '%-20s %8.1f san\n' "CƏMİ" \
    "$(ffprobe -v error -show_entries format=duration -of csv=p=0 tam_video.mp4)"
