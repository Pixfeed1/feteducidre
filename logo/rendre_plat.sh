#!/bin/bash
set -e
cd "$(dirname "$0")"
rm -rf sortie_plat && mkdir -p sortie_plat
blender -b --python pixfeed_plat.py --python-expr "
import bpy
sc = bpy.context.scene
sc.render.filepath = '$(pwd)/sortie_plat/f'
bpy.ops.render.render(animation=True)
" > rendu_plat.log 2>&1
ffmpeg -y -framerate 30 -i sortie_plat/f%04d.png -c:v libx264 -crf 18 \
    -pix_fmt yuv420p pixfeed_recul.mp4 2>/dev/null
ffmpeg -y -i pixfeed_recul.mp4 -vf "fps=10,scale=300:533:flags=lanczos,split[a][b];[a]palettegen=max_colors=32[p];[b][p]paletteuse" -loop 0 pixfeed_recul.gif 2>/dev/null
echo TERMINE
