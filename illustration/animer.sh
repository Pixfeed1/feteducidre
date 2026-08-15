#!/bin/bash
# La boucle Instagram : 192 images, 24 i/s, 8 s, sans couture.
# 1. les SVG (sequentiel - construire ecrit scene_anim.svg)
# 2. les PNG (inkscape, 4 en parallele)
# 3. les MP4 (ffmpeg : 4:5 pour le feed, 9:16 pour le reel) + GIF apercu
set -e
cd "$(dirname "$0")"
N=192
mkdir -p anim
for i in $(seq 0 $((N-1))); do
    t=$(python3 -c "print($i/$N)")
    ANIM_T=$t python3 construire.py sans >/dev/null 2>&1
    mv scene_anim.svg anim/f_$i.svg
done
echo "svg faits"
ls anim/f_*.svg | xargs -P 4 -I{} sh -c \
    'inkscape --export-type=png --export-filename="${1%.svg}.png" -h 1620 "$1" 2>/dev/null' _ {}
echo "png faits"
ffmpeg -y -framerate 24 -i anim/f_%d.png \
    -vf "crop=1296:1620:840:0,scale=1080:1350" \
    -c:v libx264 -crf 18 -pix_fmt yuv420p boucle_feed_4x5.mp4 2>/dev/null
ffmpeg -y -framerate 24 -i anim/f_%d.png \
    -vf "crop=911:1620:1141:0,scale=1080:1920" \
    -c:v libx264 -crf 18 -pix_fmt yuv420p boucle_reel_9x16.mp4 2>/dev/null
ffmpeg -y -framerate 24 -i anim/f_%d.png \
    -vf "fps=12,crop=1296:1620:840:0,scale=480:600:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse" \
    boucle_apercu.gif 2>/dev/null
echo "TERMINE"
