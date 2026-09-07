#!/bin/sh
/usr/bin/blender --enable-event-simulate -noaudio "/sortie/$SCENE" --python "/sortie/$SCRIPT" > "/sortie/log-$NOM.txt" 2>&1 &
BL=$!
i=0
while [ $i -lt 90 ]; do
  [ -f /sortie/temoin ] && break
  i=$((i+1)); sleep 1
done
sleep 1
xwd -root -silent -out "/sortie/$NOM.xwd"
kill $BL 2>/dev/null
sleep 2
