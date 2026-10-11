#!/usr/bin/env bash
# Tez yoxlama: hər hissə 480p, 15 fps (-ql). Nəticə: media/videos/ekstremal_prinsip/480p15/
#   ./render_preview.sh                    # bütün hissələr
#   ./render_preview.sh Hisse02_Silvester  # yalnız seçilmiş hissə(lər)
#   JOBS=4 ./render_preview.sh             # paralel render (CPU nüvələrinin sayı qədər)
set -euo pipefail
cd "$(dirname "$0")"
MANIM=${MANIM:-manim}
JOBS=${JOBS:-1}
SCENES=(Hisse00_Giris Hisse01_Isinme Hisse02_Silvester Hisse03_Dual Hisse04_Neticeler
        Hisse05_Serhedler Hisse06_Yekun Hisse07_Hell1 Hisse08_Hell2 Hisse09_Hell3
        Hisse10_Hell4)
[ "$#" -gt 0 ] && SCENES=("$@")
printf '%s\n' "${SCENES[@]}" | xargs -P "$JOBS" -I{} "$MANIM" -ql ekstremal_prinsip.py {}
echo "Hazırdır: media/videos/ekstremal_prinsip/480p15/"
