#!/bin/bash
# Le gag du gamin : 192 images, 24 i/s, 8 s, format 4:3 entier.
set -e
cd "$(dirname "$0")"
N=192
mkdir -p anim_gamin
for i in $(seq 0 $((N-1))); do
    t=$(python3 -c "print($i/$N)")
    ANIM_T=$t ANIM_SCENE=gamin python3 construire.py sans >/dev/null 2>&1
    mv scene_anim.svg anim_gamin/f_$i.svg
done
echo "svg faits"
ls anim_gamin/f_*.svg | xargs -P 4 -I{} sh -c \
    'inkscape --export-type=png --export-filename="${1%.svg}.png" -w 1800 "$1" 2>/dev/null' _ {}
echo "png faits"
ffmpeg -y -framerate 24 -i anim_gamin/f_%d.png \
    -c:v libx264 -crf 18 -pix_fmt yuv420p gamin_4x3.mp4 2>/dev/null
ffmpeg -y -framerate 24 -i anim_gamin/f_%d.png \
    -vf "fps=12,scale=560:420:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse" \
    gamin_apercu.gif 2>/dev/null
echo "TERMINE"
