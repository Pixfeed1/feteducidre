"""Le fichier que Blender aura ouvert sur l'écran du poste.

Lancé en arrière-plan par `capturer-dalle.sh`, avant la passe graphique.

C'est le FAUTEUIL de la scène qui est chargé, pas un objet quelconque :
l'écran du poste montre alors le meuble qui se trouve à côté du poste. Le
lecteur n'a pas besoin de le remarquer, mais rien ne sonne faux.
"""

import bpy

for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)

avant = set(bpy.data.objects)
with bpy.data.libraries.load("/sortie/fauteuil.blend") as (source, cible):
    cible.objects = list(source.objects)
for o in cible.objects:
    if o is not None and o.type == 'MESH':
        bpy.context.scene.collection.objects.link(o)
        o.name = "Fauteuil"

mailles = [o for o in bpy.data.objects if o.type == 'MESH']
if not mailles:
    raise SystemExit("le fauteuil n'est pas arrivé")

bpy.context.view_layer.objects.active = mailles[0]
for o in bpy.data.objects:
    o.select_set(o is mailles[0])

bpy.ops.wm.save_as_mainfile(filepath="/sortie/dalle.blend")
print("PRET %d maillage(s), %d matériaux, %d images"
      % (len(mailles), len(bpy.data.materials),
         len([i for i in bpy.data.images if i.name != 'Render Result'])))
