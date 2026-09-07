import bpy
#  On enregistre la scène de démarrage : lancer Blender AVEC un fichier évite
#  l'écran d'accueil, qui vient sinon se poser en plein milieu de la fenêtre.
bpy.data.objects["Cube"].hide_render = True
bpy.ops.wm.save_as_mainfile(filepath="/sortie/scene.blend")
