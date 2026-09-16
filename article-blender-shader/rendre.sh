#!/bin/sh
#
# Un rendu dans le Blender du conteneur, sans interface.
#
#     sh article-blender-astuces/blender-gui/rendre.sh rendu-agx.py agx
#
# Le `bpy` installé sur cette machine est en 4.5.12 ; le conteneur porte la
# 5.2.1 LTS, la version qu'annoncent toutes les autres figures de l'article.
# Une image de comparaison de gestion des couleurs n'a rien à faire dans une
# autre version que celle dont on parle.
#
# Il y a bien un écran virtuel, malgré l'absence d'interface : EEVEE dessine
# sur le GPU et lui faut un contexte, que `--background` seul ne fournit pas
# ici — Blender le disait à sa façon, « EGL_BAD_MATCH », trois fois de suite.
set -e

SETUP=${1:?usage : rendre.sh <script de scène> <nom>}
NOM=${2:?usage : rendre.sh <script de scène> <nom>}

IMAGE=mirror.gcr.io/linuxserver/blender:latest
ICI=$(cd "$(dirname "$0")" && pwd)
TRAVAIL=${TRAVAIL:-/tmp/bl-$NOM}

mkdir -p "$TRAVAIL"
cp "$ICI/$SETUP" "$TRAVAIL"/

docker run --rm --network host --entrypoint sh -v "$TRAVAIL":/sortie "$IMAGE" \
    -c "xvfb-run -a -s '-screen 0 1920x1080x24' \
        /usr/bin/blender --background --factory-startup -noaudio \
        --python /sortie/$SETUP > /sortie/log-$NOM.txt 2>&1"

grep -E '^(RENDU|ROUGE|Error)' "$TRAVAIL/log-$NOM.txt" || {
    tail -20 "$TRAVAIL/log-$NOM.txt"
    echo "le rendu n'a rien annoncé : voir $TRAVAIL/log-$NOM.txt"
    exit 1
}
ls -la "$TRAVAIL"/*.png
