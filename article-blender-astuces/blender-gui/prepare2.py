import bpy

#  Les préférences sont enregistrées une fois pour toutes dans le conteneur :
#  l'écran d'accueil ne se montre plus, et l'échelle d'interface est appliquée
#  AVANT le premier dessin. La régler depuis le script de scène marchait pour
#  une capture de coin, mais l'accueil, lui, s'ouvre au centre et avale les
#  messages d'erreur.
p = bpy.context.preferences
p.view.show_splash = False
p.view.ui_scale = 2.0
bpy.ops.wm.save_userpref()

bpy.ops.wm.save_as_mainfile(filepath="/sortie/avec-camera.blend")
bpy.data.objects.remove(bpy.data.objects["Camera"], do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath="/sortie/sans-camera.blend")
