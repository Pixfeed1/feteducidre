#!/bin/bash
set -e
cd "$(dirname "$0")"
rm -rf sortie30 && mkdir -p sortie30
blender -b --python pixfeed_30s.py --python-expr "
import bpy
sc = bpy.context.scene
sc.render.filepath = '$(pwd)/sortie30/f'
bpy.ops.render.render(animation=True)
" 2>&1 | grep -E "^Saved|Error|Traceback|Courant|PIXFEED" > rendu30.log
ffmpeg -y -framerate 30 -i sortie30/f%04d.png -c:v libx264 -crf 18 \
    -pix_fmt yuv420p -movflags +faststart pixfeed_30s.mp4 2>/dev/null
ffmpeg -y -i pixfeed_30s.mp4 -vf "fps=12,scale=270:480:flags=lanczos,split[a][b];[a]palettegen=max_colors=48[p];[b][p]paletteuse" -loop 0 pixfeed_30s.gif 2>/dev/null
echo TERMINE
