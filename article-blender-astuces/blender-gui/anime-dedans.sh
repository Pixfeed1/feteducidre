#!/bin/sh
# Joue une séquence Blender et photographie l'écran entre chaque étape.
# Lancé sous `xvfb-run`, par `anime.sh`, dans le conteneur. $SETUP nomme le
# script de scène, $NOM sert à nommer le journal.
rm -f /sortie/go /sortie/fait /sortie/fini /sortie/img-*.xwd

/usr/bin/blender --enable-event-simulate -noaudio /sortie/avec-camera.blend \
  --python "/sortie/$SETUP" > "/sortie/log-$NOM.txt" 2>&1 &
BL=$!

#  Le premier dessin compile les nuanceurs et prend plusieurs secondes ; on
#  laisse Blender se poser avant d'entamer le dialogue.
sleep 20

n=0
while [ $n -lt 80 ]; do
  touch /sortie/go
  i=0
  while [ $i -lt 300 ]; do
    [ -f /sortie/fait ] && break
    i=$((i + 1)); sleep 0.1
  done
  if [ ! -f /sortie/fait ]; then
    echo "ABANDON : Blender n'a pas répondu à l'étape $n"
    break
  fi
  rm -f /sortie/fait
  xwd -root -silent -out "/sortie/img-$(printf %02d $n).xwd"
  n=$((n + 1))
  [ -f /sortie/fini ] && break
done

kill $BL 2>/dev/null || true
sleep 2
echo "IMAGES $n"
