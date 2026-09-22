#!/bin/sh
#
# Photographier une vraie session de Blender, pour l'afficher sur la dalle.
#
#     sh article-formation-3d/blender-gui/capturer-dalle.sh
#
# ----------------------------------------------------------------------------
# LA DÉFINITION N'EST PAS CELLE D'UN ÉCRAN DU COMMERCE
# ----------------------------------------------------------------------------
# La dalle du modèle a un rapport de 2,273, pas les 2,389 d'un 3440x1440.
# On capture donc en 2728x1200, qui donne exactement 2,2733, plutôt que de
# capturer en 16:9 et de laisser Blender étirer l'image de 28 %. Le rendu
# refuse d'ailleurs de démarrer si les deux rapports ne concordent pas.
set -e

IMAGE=mirror.gcr.io/linuxserver/blender:latest
ICI=$(cd "$(dirname "$0")" && pwd)
TRAVAIL=${TRAVAIL:-/tmp/poste}
ECRAN=${ECRAN:-2728x1200}
POSE=${POSE:-26}

mkdir -p "$TRAVAIL/capture"
rm -f "$TRAVAIL"/capture/plein.xwd "$TRAVAIL"/capture/plein.png
cp "$ICI"/prepare-dalle.py "$ICI"/ui-dalle.py "$TRAVAIL"/capture/
cp "$TRAVAIL"/sources/fauteuil.blend "$TRAVAIL"/capture/

docker run --rm --entrypoint sh -v "$TRAVAIL/capture":/sortie "$IMAGE" -c "
  set -e
  /usr/bin/blender --background --factory-startup -noaudio \
    --python /sortie/prepare-dalle.py > /sortie/log-prepare.txt 2>&1
  xvfb-run -a -s '-screen 0 ${ECRAN}x24' sh -c \"
    /usr/bin/blender -noaudio --factory-startup /sortie/dalle.blend \
      --python /sortie/ui-dalle.py > /sortie/log-ui.txt 2>&1 &
    BL=\\\$!
    sleep ${POSE}
    xwd -root -silent -out /sortie/plein.xwd
    kill \\\$BL 2>/dev/null; sleep 2
  \"
"

grep -E '^(PRET|ESPACE|AIRES|VUE|TOUT|ACTIF|Error)' \
     "$TRAVAIL"/capture/log-prepare.txt "$TRAVAIL"/capture/log-ui.txt || {
    tail -25 "$TRAVAIL"/capture/log-ui.txt
    echo "la capture n'a rien annoncé"
    exit 1
}

python3 "$ICI/../../article-blender-astuces/xwd.py" \
    "$TRAVAIL/capture/plein.xwd" "$TRAVAIL/sources/dalle.png"
echo "  $TRAVAIL/sources/dalle.png"
