#!/bin/sh
#
# Monter et rendre le poste de travail.
#
#     sh article-formation-3d/blender-gui/capturer-dalle.sh   # l'écran
#     sh article-formation-3d/rendre-poste.sh                 # la scène
#
# ECHANTILLONS, LARGEUR_RENDU, FOCALE et FORCE_DALLE se règlent par
# l'environnement, ce qui permet un brouillon à 24 échantillons avant
# d'engager les vingt minutes du rendu définitif.
set -e

IMAGE=mirror.gcr.io/linuxserver/blender:latest
ICI=$(cd "$(dirname "$0")" && pwd)
TRAVAIL=${TRAVAIL:-/tmp/poste}

cp "$ICI/rendu_poste.py" "$TRAVAIL/"

docker run --rm -v "$TRAVAIL":/w \
  -e ECHANTILLONS="${ECHANTILLONS:-220}" \
  -e LARGEUR_RENDU="${LARGEUR_RENDU:-1600}" \
  -e FOCALE="${FOCALE:-42}" \
  -e AZIMUT="${AZIMUT:-218}" \
  -e FORCE_DALLE="${FORCE_DALLE:-13.0}" \
  --entrypoint /usr/bin/blender "$IMAGE" \
  -b --factory-startup -noaudio --python /w/rendu_poste.py 2>&1 \
  | grep -vE "^(Read prefs|Warning: |Fra:)" | tail -60
