#!/bin/sh
#
# Photographier le panneau des formes clés dans le vrai Blender.
#
#     sh article-daz-lipsync/blender-gui/capturer.sh
#
# ----------------------------------------------------------------------------
# LES DEUX PASSES TIENNENT DANS LE MÊME CONTENEUR
# ----------------------------------------------------------------------------
# Les préférences de Blender vivent dans le système de fichiers du conteneur,
# qui repart de l'image à chaque `docker run`. Enregistrer `show_splash =
# False` lors d'une exécution précédente ne sert à rien : la suivante retrouve
# les réglages d'usine et l'écran d'accueil se pose au milieu de la fenêtre.
# Leçon payée une fois, sur vingt-sept images inutilisables.
#
# La fenêtre est HAUTE et plutôt étroite, à l'inverse des figures de viewport :
# ce qu'on photographie est une liste, et une liste a besoin de hauteur.
set -e

IMAGE=mirror.gcr.io/linuxserver/blender:latest
ICI=$(cd "$(dirname "$0")" && pwd)
TRAVAIL=${TRAVAIL:-/tmp/bl-blendshapes}
ECRAN=${ECRAN:-1900x2100}
POSE=${POSE:-40}

mkdir -p "$TRAVAIL"
rm -f "$TRAVAIL"/plein.xwd "$TRAVAIL"/plein.png
cp "$ICI"/prepare-blendshapes.py "$ICI"/ui-blendshapes.py "$TRAVAIL"/

docker run --rm --entrypoint sh -v "$TRAVAIL":/sortie "$IMAGE" -c "
  set -e
  /usr/bin/blender --background --factory-startup -noaudio \
    --python /sortie/prepare-blendshapes.py > /sortie/log-prepare.txt 2>&1
  xvfb-run -a -s '-screen 0 ${ECRAN}x24' sh -c \"
    /usr/bin/blender -noaudio /sortie/blendshapes.blend \
      --python /sortie/ui-blendshapes.py > /sortie/log-ui.txt 2>&1 &
    BL=\\\$!
    sleep ${POSE}
    xwd -root -silent -out /sortie/plein.xwd
    kill \\\$BL 2>/dev/null; sleep 2
  \"
"

grep -E '^(PRET|PROPS|VUE|TOUT|CLES|Error)' "$TRAVAIL"/log-prepare.txt \
    "$TRAVAIL"/log-ui.txt || {
    tail -20 "$TRAVAIL"/log-ui.txt
    echo "la capture n'a rien annoncé"
    exit 1
}

python3 "$ICI/../../article-blender-astuces/xwd.py" \
    "$TRAVAIL/plein.xwd" "$TRAVAIL/plein.png"
echo "  $TRAVAIL/plein.png"
