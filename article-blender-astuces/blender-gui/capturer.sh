#!/bin/sh
#
# Capturer l'interface de Blender 5.2.1, sans écran.
#
#     sh article-blender-astuces/blender-gui/capturer.sh
#
# ----------------------------------------------------------------------------
# CE QUE FAIT CE SCRIPT, ET POURQUOI CHAQUE MORCEAU EST LÀ
# ----------------------------------------------------------------------------
# Le module `bpy` installé sur cette machine n'a pas d'interface graphique : il
# rend des images, il n'ouvre pas de fenêtre. Pour capturer un panneau de
# Blender il faut donc un vrai binaire, un écran, et de quoi photographier cet
# écran. Aucun des trois n'est là au départ.
#
#   - LE BINAIRE. Les serveurs de Blender sont refusés par la politique de
#     sortie. L'image Docker `linuxserver/blender` passe, elle, par le miroir
#     Google, et embarque la 5.2.1 LTS — la version qu'annonce l'article.
#   - L'ÉCRAN. Xvfb, un serveur X sans écran physique. En 3840 × 2160, avec
#     l'interface de Blender à `ui_scale = 2.0`, la colonne de droite fait 681
#     pixels réels : net sans agrandissement.
#   - LA PHOTO. `bpy.ops.screen.screenshot()` rend une image entièrement noire
#     ici — elle relit le tampon avant, que le GL logiciel ne remplit pas.
#     `xwd` demande le contenu à X lui-même et ne s'en soucie pas. Son format
#     est décodé par `xwd.py`, faute d'ImageMagick sur la machine.
#
# Deux passes : `prepare.py` enregistre la scène en arrière-plan, puis Blender
# est lancé AVEC ce fichier. Ouvrir un fichier évite l'écran d'accueil, qui
# vient sinon se poser en plein milieu de la fenêtre.
#
# Blender reste vivant pendant que `xwd` photographie : c'est ce qui permet de
# capturer un menu déroulé, lequel disparaîtrait à la fin d'un script.

set -e

IMAGE=mirror.gcr.io/linuxserver/blender:latest
ICI=$(cd "$(dirname "$0")" && pwd)
TRAVAIL=${TRAVAIL:-/tmp/bl}
POSE=${POSE:-45}                 # secondes avant la photo, GL logiciel oblige

mkdir -p "$TRAVAIL"
cp "$ICI"/prepare.py "$ICI"/setup.py "$ICI"/setup-arbre.py "$TRAVAIL"/

capture() {
    script=$1
    sortie=$2
    docker run --rm --entrypoint sh -v "$TRAVAIL":/sortie "$IMAGE" -c "
      xvfb-run -a -s '-screen 0 3840x2160x24' sh -c \"
        /usr/bin/blender --factory-startup -noaudio /sortie/scene.blend \
          --python /sortie/$script > /sortie/log-$sortie.txt 2>&1 &
        BL=\\\$!
        sleep $POSE
        xwd -root -silent -out /sortie/$sortie.xwd
        kill \\\$BL 2>/dev/null; sleep 2
      \""
    python3 "$ICI/../xwd.py" "$TRAVAIL/$sortie.xwd" "$TRAVAIL/$sortie-plein.png"
}

docker run --rm --entrypoint sh -v "$TRAVAIL":/sortie "$IMAGE" -c \
    '/usr/bin/blender --background --factory-startup -noaudio \
       --python /sortie/prepare.py' > /dev/null

capture setup-arbre.py arbre
capture setup.py filtre

#  L'Outliner occupe le coin haut droit ; ses coordonnées sont imprimées par
#  les scripts Blender, on les relit plutôt que de les supposer.
python3 - "$TRAVAIL" "$ICI/.." <<'PY'
import re
import sys

from PIL import Image

travail, dest = sys.argv[1], sys.argv[2]
for brut, nom in (("arbre", "outliner-capture-arbre-5.2.1.png"),
                  ("filtre", "outliner-capture-filtre-5.2.1.png")):
    texte = open("%s/log-%s.txt" % (travail, brut), encoding="utf-8",
                 errors="replace").read()
    m = re.search(r"PRET x=(\d+) y=(\d+) w=(\d+) h=(\d+)", texte)
    if not m:
        raise SystemExit("pas de position d'Outliner dans le journal de " + brut)
    x, y, w, h = (int(v) for v in m.groups())
    im = Image.open("%s/%s-plein.png" % (travail, brut))
    #  Blender compte les ordonnées depuis le bas, PIL depuis le haut.
    im.crop((x, im.height - (y + h), x + w, im.height - y)).save(
        "%s/%s" % (dest, nom))
    print("  %s  %d × %d" % (nom, w, h))
PY

echo "  puis : python3 article-blender-astuces/montage_outliner.py"
