#!/bin/sh
#
# Les images de l'animation « édition proportionnelle », prises dans Blender.
#
#     sh article-blender-astuces/blender-gui/capturer-proportionnelle.sh
#
# ----------------------------------------------------------------------------
# CE QUE FAIT CE SCRIPT
# ----------------------------------------------------------------------------
# Il lance UNE fois le conteneur Blender 5.2.1 LTS et lui confie les deux
# passes (`anime.sh`) : d'abord les préférences, ensuite la séquence jouée
# image par image. Puis il rapatrie les XWD, les décode et les rogne sur l'aire
# de la vue 3D, dont les coordonnées sont relues dans le journal de Blender —
# jamais supposées.
#
# Les images brutes restent dans $TRAVAIL ; seule la planche d'images
# recadrées est écrite dans le dépôt, par `anime_proportionnelle.py`.
set -e

IMAGE=mirror.gcr.io/linuxserver/blender:latest
ICI=$(cd "$(dirname "$0")" && pwd)
TRAVAIL=${TRAVAIL:-/tmp/bl}

mkdir -p "$TRAVAIL"
rm -f "$TRAVAIL"/img-*.xwd
cp "$ICI"/prepare2.py "$ICI"/setup-proportionnelle.py "$ICI"/anime.sh \
   "$ICI"/anime-dedans.sh "$TRAVAIL"/
chmod +x "$TRAVAIL"/anime.sh "$TRAVAIL"/anime-dedans.sh

docker run --rm --network host --entrypoint sh -v "$TRAVAIL":/sortie "$IMAGE" \
    /sortie/anime.sh

python3 - "$TRAVAIL" "$ICI/.." <<'PY'
import glob
import os
import re
import sys

travail = sys.argv[1]
sys.path.insert(0, os.path.abspath(sys.argv[2]))

import xwd  # noqa: E402

journal = open("%s/log-prop.txt" % travail, encoding="utf-8",
               errors="replace").read()
m = re.search(r"AIRE x=(\d+) y=(\d+) w=(\d+) h=(\d+)", journal)
if not m:
    raise SystemExit("pas de géométrie d'aire dans le journal de Blender")
x, y, w, h = (int(v) for v in m.groups())

dest = "%s/frames" % travail
os.makedirs(dest, exist_ok=True)
for vieux in glob.glob(dest + "/*.png"):
    os.remove(vieux)

bruts = sorted(glob.glob("%s/img-*.xwd" % travail))
if not bruts:
    raise SystemExit("aucune image capturée")
for chemin in bruts:
    im = xwd.lire(chemin)
    #  Blender compte les ordonnées depuis le bas, PIL depuis le haut.
    im.crop((x, im.height - (y + h), x + w, im.height - y)).save(
        "%s/%s.png" % (dest, os.path.basename(chemin)[4:6]))
print("  %d images, aire %d × %d  ->  %s" % (len(bruts), w, h, dest))
PY

echo "  puis : python3 article-blender-astuces/anime_proportionnelle.py"
