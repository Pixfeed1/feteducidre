"""
Le même rendu, développé en AgX puis en Standard.

Lancé par `rendre.sh`, en arrière-plan — il n'y a pas d'interface à
photographier ici, seulement deux images à sortir.

----------------------------------------------------------------------------
UN SEUL RENDU, DEUX DÉVELOPPEMENTS
----------------------------------------------------------------------------
La scène n'est calculée QU'UNE FOIS. Les deux images sont écrites depuis le
même résultat de rendu, en changeant seulement `view_transform` entre les deux
enregistrements. C'est ce qui permet d'affirmer que la différence vient de la
transformation d'affichage et de rien d'autre : ni bruit d'échantillonnage, ni
lampe déplacée, ni hasard de moteur. Deux rendus séparés, même avec la même
graine, auraient laissé planer le doute.

C'est aussi, très exactement, ce que fait la case « Save as Render » de la
fenêtre d'enregistrement dont parle l'article : la même image, écrite avec ou
sans la transformation.

----------------------------------------------------------------------------
DES COULEURS FRANCHES, PARCE QUE C'EST LÀ QUE ÇA SE VOIT
----------------------------------------------------------------------------
AgX comprime les hautes lumières et désature les teintes très vives. Sur une
scène photoréaliste en tons rompus, l'écart est subtil ; sur un rouge saturé
et un fond clair — le cas du motion design et du logo, celui de l'article —
il saute aux yeux. La scène est donc faite de ça.

La position à l'écran du cube rouge est calculée et écrite dans `zones.json` :
le montage y relève la couleur obtenue de chaque côté, plutôt que de la
supposer.
"""

import json
import os
from math import radians

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Euler

SORTIE = "/sortie"
LARGEUR, HAUTEUR = 1280, 900
ECHANTILLONS = 128

#  Les couleurs saisies dans les matériaux, en linéaire, telles que l'article
#  les appelle : « le rouge qu'on a mis ».
ROUGE = (0.90, 0.03, 0.03)
JAUNE = (0.95, 0.72, 0.04)
BLEU = (0.03, 0.25, 0.85)
MUR = (0.86, 0.86, 0.87)
SOL = (0.46, 0.46, 0.48)

scene = bpy.context.scene

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
for reste in list(bpy.data.materials):
    bpy.data.materials.remove(reste)


def matiere(nom, couleur, rugosite=0.45):
    m = bpy.data.materials.new(nom)
    m.use_nodes = True
    n = m.node_tree.nodes["Principled BSDF"]
    n.inputs["Base Color"].default_value = (*couleur, 1.0)
    n.inputs["Roughness"].default_value = rugosite
    n.inputs["Metallic"].default_value = 0.0
    return m


# ------------------------------------------------------------------  la scène
#  Le sol est plus sombre que le mur, et ce n'est pas une coquetterie : posé à
#  la même clarté, il partait à fond dès qu'on éclairait assez pour que le mur
#  lise « blanc ». Les cent dernières lignes de l'image étaient à 255, ce qui
#  ne prouve plus rien — ça montre une erreur d'exposition, pas une différence
#  de transformation.
bpy.ops.mesh.primitive_plane_add(size=40.0, location=(0.0, 0.0, 0.0))
sol = bpy.context.object
sol.data.materials.append(matiere("Sol", SOL, 0.75))

#  Un fond qui remonte derrière les objets : sans lui, l'horizon coupe l'image
#  en deux et l'on ne juge plus la couleur du fond, seulement celle du ciel.
bpy.ops.mesh.primitive_plane_add(size=40.0, location=(0.0, 6.0, 0.0),
                                 rotation=(radians(90.0), 0.0, 0.0))
mur = bpy.context.object
mur.data.materials.append(matiere("Mur", MUR, 0.8))

bpy.ops.mesh.primitive_cube_add(size=2.2, location=(-2.1, 0.0, 1.1))
cube = bpy.context.object
cube.rotation_euler = Euler((0.0, 0.0, radians(22.0)))
biseau = cube.modifiers.new("Bevel", 'BEVEL')
biseau.width = 0.08
biseau.segments = 4
bpy.ops.object.shade_smooth()
cube.data.materials.append(matiere("Rouge", ROUGE))

bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=1.15,
                                     location=(0.6, -0.4, 1.15))
boule = bpy.context.object
bpy.ops.object.shade_smooth()
boule.data.materials.append(matiere("Jaune", JAUNE))

bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.85, depth=2.6,
                                    location=(3.0, 0.6, 1.3))
colonne = bpy.context.object
bpy.ops.object.shade_smooth()
colonne.data.materials.append(matiere("Bleu", BLEU, 0.35))

#  Une grande lampe douce. Assez forte pour que les hautes lumières entrent
#  dans la zone où AgX travaille — c'est là que se joue la moitié de l'écart —
#  mais pas au point de brûler le fond en Standard : une image écrêtée ne
#  prouverait plus rien, elle montrerait une erreur d'exposition. Le montage
#  refuse la figure au-delà de 2 % de pixels à fond.
bpy.ops.object.light_add(type='AREA', location=(-3.0, -4.5, 7.0))
lampe = bpy.context.object
lampe.data.energy = 520.0
lampe.data.size = 7.0
lampe.rotation_euler = Euler((radians(38.0), 0.0, radians(-28.0)))

bpy.ops.object.light_add(type='AREA', location=(5.0, -5.0, 3.0))
appoint = bpy.context.object
appoint.data.energy = 114.4
appoint.data.size = 5.0
appoint.rotation_euler = Euler((radians(72.0), 0.0, radians(48.0)))

scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (
    0.35, 0.37, 0.40, 1.0)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = 1.60

bpy.ops.object.camera_add(location=(0.2, -11.5, 4.6))
camera = bpy.context.object
camera.rotation_euler = Euler((radians(76.0), 0.0, radians(1.0)))
camera.data.lens = 50.0
scene.camera = camera

# ------------------------------------------------------------------  le rendu
#  Le nom du moteur a changé entre les versions : `BLENDER_EEVEE_NEXT` en 4.2,
#  redevenu `BLENDER_EEVEE` en 5.x, où c'est le seul EEVEE. On prend celui qui
#  existe plutôt que d'en écrire un au hasard.
moteurs = [i.identifier for i in
           scene.render.bl_rna.properties["engine"].enum_items]
scene.render.engine = next(m for m in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE")
                           if m in moteurs)
scene.eevee.taa_render_samples = ECHANTILLONS
if hasattr(scene.eevee, "use_raytracing"):
    scene.eevee.use_raytracing = False
scene.render.resolution_x = LARGEUR
scene.render.resolution_y = HAUTEUR
scene.render.resolution_percentage = 100
scene.render.film_transparent = False

#  Le « look » reste neutre des deux côtés : l'article compare les View
#  Transform, pas les contrastes. AgX Base Contrast aurait ajouté un second
#  écart et brouillé la démonstration.
scene.view_settings.look = 'None'
scene.view_settings.exposure = 0.0
scene.view_settings.gamma = 1.0

bpy.ops.render.render(write_still=False)
rendu = bpy.data.images["Render Result"]

#  On règle, puis on relit. La liste des transformations vient de la
#  configuration OCIO et n'est pas interrogeable d'avance : `enum_items` ne
#  renvoyait que ['NONE'] alors que les deux existent bel et bien. Écrire puis
#  vérifier est la seule façon honnête de s'en assurer.
for nom in ("AgX", "Standard"):
    scene.view_settings.view_transform = nom
    if scene.view_settings.view_transform != nom:
        raise SystemExit("la transformation %s n'a pas pris : reste %s"
                         % (nom, scene.view_settings.view_transform))
    rendu.save_render(filepath="%s/agx-%s.png" % (SORTIE, nom.lower()),
                      scene=scene)
    print("ECRIT %s avec view_transform=%s"
          % (nom.lower(), scene.view_settings.view_transform))

#  Où se trouve le cube rouge à l'image, pour que le montage y relève la
#  couleur obtenue au lieu de la deviner.
vue = world_to_camera_view(scene, camera, cube.matrix_world.translation)
with open(os.path.join(SORTIE, "zones.json"), "w", encoding="utf-8") as f:
    json.dump({"rouge_saisi": ROUGE,
               "rouge_ecran": [round(vue.x * LARGEUR),
                               round((1.0 - vue.y) * HAUTEUR)],
               "taille": [LARGEUR, HAUTEUR],
               "version": bpy.app.version_string,
               "echantillons": ECHANTILLONS}, f)

print("RENDU %d x %d, %d échantillons, Blender %s"
      % (LARGEUR, HAUTEUR, ECHANTILLONS, bpy.app.version_string))
print("ROUGE à l'écran x=%d y=%d"
      % (round(vue.x * LARGEUR), round((1.0 - vue.y) * HAUTEUR)))
