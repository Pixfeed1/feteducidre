#!/bin/sh
set -e
/usr/bin/blender --background --factory-startup -noaudio --python /sortie/prepare2.py >/dev/null 2>&1

capture() {
  SCRIPT=$1; SCENE=$2; NOM=$3
  rm -f /sortie/temoin
  export SCRIPT SCENE NOM
  xvfb-run -a -s '-screen 0 3840x2160x24' /sortie/dedans.sh
}

capture setup-erreur.py sans-camera.blend erreur
capture setup-sequencer.py avec-camera.blend sequencer
