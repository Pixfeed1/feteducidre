"""
La sphère de métal brossé, montée avec les valeurs de l'article.

    SORTIE=/tmp/bl-brosse python3 article-blender-shader/rendu_brosse.py

Tourne aussi sous `rendre.sh`, mais l'article annonce Blender 4.5 LTS et le
conteneur porte la 5.2.1 : le `bpy` de cette machine est en 4.5.12 LTS, donc
la figure est rendue ici, dans la version dont le texte parle.

----------------------------------------------------------------------------
LES VALEURS SONT RELUES APRÈS AVOIR ÉTÉ POSÉES
----------------------------------------------------------------------------
L'article promet « les valeurs qui ont produit les images, pas des ordres de
grandeur recopiés ». Une promesse pareille se vérifie : le tableau VALEURS
est posé dans l'arbre, puis relu depuis l'arbre et comparé. Si un réglage ne
prend pas — un nom d'entrée qui change de version en version, une prise qui
n'accepte pas le type —, le rendu s'arrête au lieu de sortir une image dont
la légende mentirait.

----------------------------------------------------------------------------
LE QUART DE TOUR
----------------------------------------------------------------------------
Le Scale de 120 porte sur Y. Les stries sont donc des lignes perpendiculaires
à Y, et une caméra placée sur l'axe Y les verrait par la tranche : des anneaux
concentriques, pas un brossage. On regarde donc la sphère depuis X, ce qui met
l'axe serré à l'horizontale et les stries à la verticale.

Plutôt que de recalculer à la main les places des lampes, on monte le décor
comme pour la figure Metallic — celui-là fonctionne — et on fait pivoter
l'ensemble d'un quart de tour. Attention : `matrix_world` n'est recalculée
qu'à la mise à jour du graphe de dépendances. Sans `view_layer.update()`, on
compose le quart de tour avec une matrice périmée et la caméra part regarder
le vide — trois rendus d'un gris parfaitement uniforme avant de le voir.

----------------------------------------------------------------------------
UN MÉTAL N'A QUE CE QU'IL REFLÈTE
----------------------------------------------------------------------------
Metallic à 1 : la sphère n'a aucune couleur propre, elle ne renvoie que son
entourage. Un brossage ne se lit que dans des reflets étirés, donc il faut
quelque chose à étirer : de grands panneaux clairs hors champ, un ciel en
dégradé, un sol et un fond sombres. Devant un champ uniforme, les stries
disparaissent — non pas parce que le matériau est raté, mais parce qu'il n'y
a rien à déformer.
"""

import json
import os
from math import radians

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Euler, Matrix, Vector

SORTIE = os.environ.get("SORTIE", "/sortie")
LARGEUR, HAUTEUR = 1700, 900
ECHANTILLONS = 600
RAYON = 1.3

#  LE MATÉRIAU DE L'ARTICLE, AU CHIFFRE PRÈS.
VALEURS = {
    "Base Color": (0.69, 0.70, 0.72),
    "Metallic": 1.0,
    "Mapping Scale": (1.0, 120.0, 1.0),
    "Noise Scale": 12.0,
    "Noise Detail": 6.0,
    "Color Ramp": (0.38, 0.62),
    "Map Range To Min": 0.18,
    "Map Range To Max": 0.42,
    "Bump Strength": 0.08,
}

scene = bpy.context.scene

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
for reste in list(bpy.data.materials):
    bpy.data.materials.remove(reste)


# ----------------------------------------------------------------  le matériau
def brosse():
    m = bpy.data.materials.new("Metal brosse")
    m.use_nodes = True
    a = m.node_tree
    p = a.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*VALEURS["Base Color"], 1.0)
    p.inputs["Metallic"].default_value = VALEURS["Metallic"]

    coord = a.nodes.new("ShaderNodeTexCoord")
    mapping = a.nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = VALEURS["Mapping Scale"]

    bruit = a.nodes.new("ShaderNodeTexNoise")
    bruit.inputs["Scale"].default_value = VALEURS["Noise Scale"]
    bruit.inputs["Detail"].default_value = VALEURS["Noise Detail"]

    rampe = a.nodes.new("ShaderNodeValToRGB")
    rampe.color_ramp.elements[0].position = VALEURS["Color Ramp"][0]
    rampe.color_ramp.elements[1].position = VALEURS["Color Ramp"][1]

    plage = a.nodes.new("ShaderNodeMapRange")
    plage.inputs["To Min"].default_value = VALEURS["Map Range To Min"]
    plage.inputs["To Max"].default_value = VALEURS["Map Range To Max"]

    relief = a.nodes.new("ShaderNodeBump")
    relief.inputs["Strength"].default_value = VALEURS["Bump Strength"]

    a.links.new(coord.outputs["Object"], mapping.inputs["Vector"])
    a.links.new(mapping.outputs["Vector"], bruit.inputs["Vector"])
    a.links.new(bruit.outputs["Fac"], rampe.inputs["Fac"])
    a.links.new(rampe.outputs["Color"], plage.inputs["Value"])
    a.links.new(plage.outputs["Result"], p.inputs["Roughness"])
    a.links.new(bruit.outputs["Fac"], relief.inputs["Height"])
    a.links.new(relief.outputs["Normal"], p.inputs["Normal"])
    return m, a


def relire(a):
    """Ce que l'arbre contient VRAIMENT, relu prise par prise."""
    p = a.nodes["Principled BSDF"]
    bruit = next(n for n in a.nodes if n.bl_idname == "ShaderNodeTexNoise")
    mapping = next(n for n in a.nodes if n.bl_idname == "ShaderNodeMapping")
    rampe = next(n for n in a.nodes if n.bl_idname == "ShaderNodeValToRGB")
    plage = next(n for n in a.nodes if n.bl_idname == "ShaderNodeMapRange")
    relief = next(n for n in a.nodes if n.bl_idname == "ShaderNodeBump")
    return {
        "Base Color": tuple(p.inputs["Base Color"].default_value)[:3],
        "Metallic": p.inputs["Metallic"].default_value,
        "Mapping Scale": tuple(mapping.inputs["Scale"].default_value),
        "Noise Scale": bruit.inputs["Scale"].default_value,
        "Noise Detail": bruit.inputs["Detail"].default_value,
        "Color Ramp": (rampe.color_ramp.elements[0].position,
                       rampe.color_ramp.elements[1].position),
        "Map Range To Min": plage.inputs["To Min"].default_value,
        "Map Range To Max": plage.inputs["To Max"].default_value,
        "Bump Strength": relief.inputs["Strength"].default_value,
    }


bpy.ops.mesh.primitive_uv_sphere_add(segments=256, ring_count=128,
                                     radius=RAYON,
                                     location=(0.0, 0.0, RAYON))
sphere = bpy.context.object
bpy.ops.object.shade_smooth()
materiau, arbre = brosse()
sphere.data.materials.append(materiau)

#  CONTRÔLE : l'arbre doit contenir les valeurs annoncées, et rien d'autre.
lu = relire(arbre)
for cle, attendu in VALEURS.items():
    obtenu = lu[cle]
    if hasattr(attendu, "__len__"):
        ecart = max(abs(x - y) for x, y in zip(attendu, obtenu))
    else:
        ecart = abs(attendu - obtenu)
    if ecart > 1e-5:
        raise SystemExit("« %s » vaut %s dans l'arbre, pas %s"
                         % (cle, obtenu, attendu))

#  Le brossage doit venir du matériau, pas d'une déformation de la sphère :
#  une échelle d'objet non uniforme étirerait aussi les coordonnées Object.
if tuple(round(v, 6) for v in sphere.scale) != (1.0, 1.0, 1.0):
    raise SystemExit("la sphère est déformée : le brossage ne serait pas "
                     "celui du matériau")


# -------------------------------------------------------------------  le décor
def mat_decor(nom, couleur, rugosite):
    m = bpy.data.materials.new(nom)
    m.use_nodes = True
    n = m.node_tree.nodes["Principled BSDF"]
    n.inputs["Base Color"].default_value = (*couleur, 1.0)
    n.inputs["Roughness"].default_value = rugosite
    return m


mobiles = []
decor = mat_decor("Decor", (0.055, 0.056, 0.062), 0.62)
for place, rotation in (((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)),
                        ((0.0, 11.0, 0.0), (90.0, 0.0, 0.0))):
    bpy.ops.mesh.primitive_plane_add(
        size=80.0, location=place,
        rotation=tuple(radians(v) for v in rotation))
    bpy.context.object.data.materials.append(decor)
    mobiles.append(bpy.context.object)

for place, rotation, taille, force in (
        ((-5.0, -6.0, 7.5), (38.0, 0.0, -32.0), 8.0, 300.0),
        ((3.4, -4.0, 5.2), (52.0, 0.0, 26.0), 0.9, 150.0),
        ((6.5, -7.0, 3.0), (74.0, 0.0, 44.0), 6.0, 95.0)):
    bpy.ops.object.light_add(type='AREA', location=place)
    lampe = bpy.context.object
    lampe.data.size = taille
    lampe.data.energy = force
    lampe.rotation_euler = Euler([radians(v) for v in rotation])
    mobiles.append(lampe)

#  Les panneaux réfléchis, hors du champ de la caméra mais pas des reflets.
#  Ce sont eux qui donnent aux stries de quoi s'étirer.
for place, rotation, taille, force in (
        ((-7.4, -3.0, 3.2), (72.0, 0.0, -62.0), (9.0, 6.0), 3.0),
        ((7.4, -2.2, 4.0), (76.0, 0.0, 58.0), (7.0, 5.0), 2.0),
        ((0.0, -3.4, 8.6), (0.0, 0.0, 0.0), (11.0, 7.0), 1.4)):
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=place)
    panneau = bpy.context.object
    panneau.scale = (taille[0], taille[1], 1.0)
    panneau.rotation_euler = Euler([radians(v) for v in rotation])
    m = bpy.data.materials.new("Panneau")
    m.use_nodes = True
    a = m.node_tree
    for n in list(a.nodes):
        if n.type != 'OUTPUT_MATERIAL':
            a.nodes.remove(n)
    emission = a.nodes.new("ShaderNodeEmission")
    emission.inputs["Strength"].default_value = force
    a.links.new(emission.outputs["Emission"],
                a.nodes["Material Output"].inputs["Surface"])
    panneau.data.materials.append(m)
    panneau.visible_camera = False
    mobiles.append(panneau)

bpy.ops.object.camera_add(location=(0.0, -14.5, RAYON))
camera = bpy.context.object
camera.rotation_euler = Euler((radians(90.0), 0.0, 0.0))
camera.data.lens = 85.0
scene.camera = camera
mobiles.append(camera)

#  LE QUART DE TOUR. `matrix_world` n'est recalculée qu'ici : sans cet appel,
#  on la compose avec une valeur périmée et la caméra regarde ailleurs.
bpy.context.view_layer.update()
QUART = Matrix.Rotation(radians(-90.0), 4, 'Z')
for o in mobiles:
    o.matrix_world = QUART @ o.matrix_world
bpy.context.view_layer.update()

#  CONTRÔLE : la caméra doit regarder le long de X, sinon les stries se
#  verraient par la tranche et donneraient des anneaux.
vise = (camera.matrix_world.to_3x3() @ Vector((0.0, 0.0, -1.0))).normalized()
if abs(vise.x) < 0.98:
    raise SystemExit("la caméra ne regarde pas le long de X : %s"
                     % [round(v, 3) for v in vise])

scene.world.use_nodes = True
ciel = scene.world.node_tree
for n in list(ciel.nodes):
    if n.type != 'OUTPUT_WORLD':
        ciel.nodes.remove(n)
coord = ciel.nodes.new("ShaderNodeTexCoord")
separe = ciel.nodes.new("ShaderNodeSeparateXYZ")
plage = ciel.nodes.new("ShaderNodeMapRange")
plage.inputs["From Min"].default_value = -0.30
plage.inputs["From Max"].default_value = 0.60
degrade = ciel.nodes.new("ShaderNodeValToRGB")
degrade.color_ramp.elements[0].color = (0.020, 0.021, 0.026, 1.0)
degrade.color_ramp.elements[1].color = (0.88, 0.89, 0.94, 1.0)
degrade.color_ramp.elements[1].position = 0.92
fond = ciel.nodes.new("ShaderNodeBackground")
ciel.links.new(coord.outputs["Generated"], separe.inputs["Vector"])
ciel.links.new(separe.outputs["Z"], plage.inputs["Value"])
ciel.links.new(plage.outputs["Result"], degrade.inputs["Fac"])
ciel.links.new(degrade.outputs["Color"], fond.inputs["Color"])
ciel.links.new(fond.outputs["Background"],
               ciel.nodes["World Output"].inputs["Surface"])


# -------------------------------------------------------------------  le rendu
#
#  Sans débruitage : les stries sont à la limite de ce qu'un pixel peut porter,
#  et un débruiteur les prendrait pour du bruit — c'est exactement le sujet de
#  la figure qu'il effacerait. On paie en échantillons ce qu'on refuse de
#  gagner en lissage.
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = ECHANTILLONS
scene.cycles.use_denoising = False
scene.render.resolution_x = LARGEUR
scene.render.resolution_y = HAUTEUR
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'None'

scene.render.filepath = "%s/brosse.png" % SORTIE
bpy.ops.render.render(write_still=True)

# ---------------------------------------------  où est la sphère à l'écran
centre = world_to_camera_view(scene, camera, sphere.matrix_world.translation)
cote = camera.matrix_world.to_3x3() @ Vector((RAYON, 0.0, 0.0))
bord = world_to_camera_view(scene, camera,
                            sphere.matrix_world.translation + cote)
repere = {"x": round(centre.x * LARGEUR),
          "y": round((1.0 - centre.y) * HAUTEUR),
          "rayon": round(abs(bord.x - centre.x) * LARGEUR)}

with open(os.path.join(SORTIE, "brosse.json"), "w", encoding="utf-8") as f:
    json.dump({"sphere": repere,
               "valeurs": {k: list(v) if hasattr(v, "__len__") else v
                           for k, v in VALEURS.items()},
               "taille": [LARGEUR, HAUTEUR],
               "echantillons": ECHANTILLONS,
               "objectif": camera.data.lens,
               "version": bpy.app.version_string}, f, indent=1)

print("RENDU %d x %d, %d échantillons, Cycles, Blender %s"
      % (LARGEUR, HAUTEUR, ECHANTILLONS, bpy.app.version_string))
print("SPHERE x=%d y=%d rayon=%d" % (repere["x"], repere["y"],
                                     repere["rayon"]))
for cle in VALEURS:
    print("VALEUR %-18s %s" % (cle, lu[cle]))
