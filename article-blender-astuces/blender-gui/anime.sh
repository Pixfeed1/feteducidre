#!/bin/sh
# Les deux passes de la capture animée. Lancé DANS le conteneur, /sortie monté.
#
# ----------------------------------------------------------------------------
# POURQUOI LA PASSE DE PRÉFÉRENCES EST ICI, ET PAS AILLEURS
# ----------------------------------------------------------------------------
# Les préférences de Blender vivent dans le système de fichiers du conteneur,
# qui repart de l'image à chaque `docker run`. Enregistrer `show_splash = False`
# lors d'une exécution précédente ne sert donc à rien : la suivante retrouve les
# réglages d'usine, et l'écran d'accueil vient se poser en plein milieu de la
# fenêtre.
#
# C'est exactement ce qui est arrivé au premier jeu de vingt-sept images : la
# séquence s'est jouée correctement, mais derrière la photo du lion. Les deux
# passes doivent tenir dans la MÊME exécution du conteneur.
set -e

/usr/bin/blender --background --factory-startup -noaudio \
  --python /sortie/prepare2.py >/dev/null 2>&1

#  Grand écran et interface au double : le viewport fait alors plus de deux
#  mille pixels de large, et la figure reste nette une fois réduite.
xvfb-run -a -s '-screen 0 2560x1600x24' /sortie/anime-dedans.sh
