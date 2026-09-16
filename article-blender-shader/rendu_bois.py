"""
Deux plateaux, un seul câble de différence.

    SORTIE=/tmp/bl-bois python3 article-blender-shader/rendu_bois.py

À gauche le Fac du Noise branché sur le Vector du Wave — l'erreur —, à
droite le même Fac passé par un Math Multiply vers la Distortion. Tout le
reste est identique, et pas seulement « réglé pareil » : les deux arbres
sont construits par la MÊME fonction, et le script compare ensuite prise par
prise que rien d'autre ne diffère.

----------------------------------------------------------------------------
UN SEUL RENDU, DEUX PLATEAUX
----------------------------------------------------------------------------
Les deux planches sont dans la même image, sous les mêmes lampes, à la même
seconde. « Seul le câble change » n'est donc pas une promesse faite sous la
figure : c'est une propriété du fichier.

Caméra orthographique, et pas par coquetterie : deux objets côte à côte vus
en perspective ne sont pas vus pareil — celui de gauche montrerait un peu sa
tranche gauche, celui de droite sa tranche droite. Pour une comparaison, cet
écart-là est du bruit.

----------------------------------------------------------------------------
L'ÉCHELLE DE L'OBJET EST APPLIQUÉE, ET C'EST INDISPENSABLE
----------------------------------------------------------------------------
Le plateau est un cube étiré. Or Texture Coordinate Object lit les
coordonnées LOCALES : une échelle d'objet non uniforme étirerait la texture
en plus du Mapping, et le 0,25 de l'article ne vaudrait plus 0,25. On applique
donc l'échelle à la géométrie avant de poser le matériau, et on vérifie
ensuite que l'objet est bien revenu à 1 / 1 / 1.

----------------------------------------------------------------------------
LES DEUX BRUNS
----------------------------------------------------------------------------
L'article donne les POSITIONS des deux curseurs du Color Ramp — 0,32 et
0,70 — mais pas les deux bruns. Ceux-ci sont donc un choix, et il est écrit
sous la figure plutôt que passé sous silence.
"""

import json
import os
from math import radians

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Euler

SORTIE = os.environ.get("SORTIE", "/sortie")
LARGEUR = int(os.environ.get("LARGEUR", "1700"))
HAUTEUR = int(os.environ.get("HAUTEUR", "760"))
ECHANTILLONS = int(os.environ.get("ECHANTILLONS", "400"))

#  Le plateau. Long sur Y, qui est l'axe que le Mapping étire : les cernes
#  s'allongent donc dans le sens de la planche, comme sur une vraie.
#  Le plateau est volontairement GRAND devant la texture. Un premier essai
#  de 1,15 × 1,45 ne montrait que quatre cernes : au Scale de 2,2 de
#  l'article, une petite planche donne une cible de tir à l'arc plutôt qu'un
#  plateau. L'article fixe les valeurs du matériau, pas les dimensions de
#  l'objet — c'est donc l'objet qu'on ajuste.
PLATEAU = (2.20, 2.90, 0.12)
ECART = 1.60
CADRE = 6.60

#  LES VALEURS DE L'ARTICLE.
VALEURS = {
    "Mapping Scale": (1.0, 0.25, 1.0),
    "Wave Scale": 2.2,
    "Wave Detail": 3.0,
    "Wave Detail Scale": 1.0,
    "Noise Scale": 3.0,
    "Noise Detail": 6.0,
    "Noise Roughness": 0.5,
    "Multiply": 8.0,
    "Color Ramp": (0.32, 0.70),
    "Map Range To Min": 0.28,
    "Map Range To Max": 0.58,
    "Bump Strength": 0.25,
}
#  Ce que l'article ne donne pas : les deux bruns, en linéaire.
BRUN_SOMBRE = (0.055, 0.026, 0.012)
BRUN_CLAIR = (0.340, 0.190, 0.086)

scene = bpy.context.scene

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
for reste in list(bpy.data.materials):
    bpy.data.materials.remove(reste)


def bois(nom, casse):
    """L'arbre de l'article. `casse` rebranche le seul câble en cause."""
    m = bpy.data.materials.new(nom)
    m.use_nodes = True
    a = m.node_tree
    p = a.nodes["Principled BSDF"]
    p.inputs["Metallic"].default_value = 0.0

    coord = a.nodes.new("ShaderNodeTexCoord")
    mapping = a.nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = VALEURS["Mapping Scale"]

    vague = a.nodes.new("ShaderNodeTexWave")
    vague.wave_type = 'RINGS'
    vague.rings_direction = 'Z'
    vague.wave_profile = 'SIN'
    vague.inputs["Scale"].default_value = VALEURS["Wave Scale"]
    vague.inputs["Detail"].default_value = VALEURS["Wave Detail"]
    vague.inputs["Detail Scale"].default_value = VALEURS["Wave Detail Scale"]

    bruit = a.nodes.new("ShaderNodeTexNoise")
    bruit.inputs["Scale"].default_value = VALEURS["Noise Scale"]
    bruit.inputs["Detail"].default_value = VALEURS["Noise Detail"]
    bruit.inputs["Roughness"].default_value = VALEURS["Noise Roughness"]

    fois = a.nodes.new("ShaderNodeMath")
    fois.operation = 'MULTIPLY'
    fois.inputs[1].default_value = VALEURS["Multiply"]

    a.links.new(coord.outputs["Object"], mapping.inputs["Vector"])
    a.links.new(bruit.outputs["Fac"], fois.inputs[0])

    #  LE SEUL CÂBLE QUI CHANGE.
    if casse:
        #  Un scalaire dans une entrée qui attend trois nombres. Blender
        #  l'accepte, recopie la valeur sur les trois axes — vérifié : un 0,30
        #  ainsi branché ressort en (0,30 ; 0,30 ; 0,30) — et le vecteur perd
        #  toute direction. Le Mapping reste dans l'arbre, débranché, comme
        #  dans le cas raconté par l'article.
        a.links.new(bruit.outputs["Fac"], vague.inputs["Vector"])
    else:
        a.links.new(mapping.outputs["Vector"], vague.inputs["Vector"])
        a.links.new(fois.outputs["Value"], vague.inputs["Distortion"])

    rampe = a.nodes.new("ShaderNodeValToRGB")
    rampe.color_ramp.elements[0].position = VALEURS["Color Ramp"][0]
    rampe.color_ramp.elements[0].color = (*BRUN_SOMBRE, 1.0)
    rampe.color_ramp.elements[1].position = VALEURS["Color Ramp"][1]
    rampe.color_ramp.elements[1].color = (*BRUN_CLAIR, 1.0)

    plage = a.nodes.new("ShaderNodeMapRange")
    plage.inputs["To Min"].default_value = VALEURS["Map Range To Min"]
    plage.inputs["To Max"].default_value = VALEURS["Map Range To Max"]

    relief = a.nodes.new("ShaderNodeBump")
    relief.inputs["Strength"].default_value = VALEURS["Bump Strength"]

    a.links.new(vague.outputs["Fac"], rampe.inputs["Fac"])
    a.links.new(rampe.outputs["Color"], p.inputs["Base Color"])
    a.links.new(vague.outputs["Fac"], plage.inputs["Value"])
    a.links.new(plage.outputs["Result"], p.inputs["Roughness"])
    a.links.new(vague.outputs["Fac"], relief.inputs["Height"])
    a.links.new(relief.outputs["Normal"], p.inputs["Normal"])
    return m


def cables(materiau):
    """Les liens de l'arbre, sous une forme comparable."""
    return sorted("%s.%s -> %s.%s" % (l.from_node.bl_idname,
                                      l.from_socket.name,
                                      l.to_node.bl_idname, l.to_socket.name)
                  for l in materiau.node_tree.links)


def plateau(nom, y, materiau):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, y, 0.0))
    o = bpy.context.object
    o.name = nom
    o.scale = PLATEAU
    #  L'échelle passe dans la géométrie : Texture Coordinate Object lit les
    #  coordonnées locales, et une échelle non uniforme les étirerait.
    bpy.ops.object.transform_apply(location=False, rotation=False,
                                   scale=True)
    if tuple(round(v, 6) for v in o.scale) != (1.0, 1.0, 1.0):
        raise SystemExit("l'échelle de « %s » n'a pas été appliquée" % nom)
    o.data.materials.append(materiau)
    return o


casse = bois("Bois casse", True)
juste = bois("Bois juste", False)
#  La caméra est pivotée de -90° : la droite de l'écran est le -Y du
#  monde. Pour que « Vector » tombe à GAUCHE comme dans l'article, il
#  lui faut donc le +Y. Vérifié après coup sur les repères mesurés.
gauche = plateau("Vector", ECART, casse)
droite = plateau("Distortion", -ECART, juste)

#  CONTRÔLE : un seul câble doit différer entre les deux arbres.
a, b = set(cables(casse)), set(cables(juste))
seulement_casse = sorted(a - b)
seulement_juste = sorted(b - a)
if seulement_casse != ["ShaderNodeTexNoise.Fac -> ShaderNodeTexWave.Vector"]:
    raise SystemExit("le cas cassé diffère par autre chose : %s"
                     % seulement_casse)
if seulement_juste != ["ShaderNodeMapping.Vector -> ShaderNodeTexWave.Vector",
                       "ShaderNodeMath.Value -> ShaderNodeTexWave.Distortion"]:
    raise SystemExit("le cas correct diffère par autre chose : %s"
                     % seulement_juste)
#  Et les réglages des noeuds doivent être identiques des deux côtés.
for n1, n2 in zip(sorted(casse.node_tree.nodes, key=lambda n: n.bl_idname),
                  sorted(juste.node_tree.nodes, key=lambda n: n.bl_idname)):
    if n1.bl_idname != n2.bl_idname:
        raise SystemExit("les deux arbres n'ont pas les mêmes noeuds")
    for i, (e1, e2) in enumerate(zip(n1.inputs, n2.inputs)):
        if e1.is_linked or e2.is_linked:
            continue
        v1 = getattr(e1, "default_value", None)
        v2 = getattr(e2, "default_value", None)
        v1 = list(v1) if hasattr(v1, "__len__") else v1
        v2 = list(v2) if hasattr(v2, "__len__") else v2
        if v1 != v2:
            raise SystemExit("« %s » de %s diffère : %s contre %s"
                             % (e1.name, n1.bl_idname, v1, v2))


# -------------------------------------------------------------------  le décor
bpy.ops.mesh.primitive_plane_add(size=40.0, location=(0.0, 0.0, -0.05))
fond = bpy.data.materials.new("Fond")
fond.use_nodes = True
nf = fond.node_tree.nodes["Principled BSDF"]
nf.inputs["Base Color"].default_value = (0.021, 0.021, 0.024, 1.0)
nf.inputs["Roughness"].default_value = 0.72
bpy.context.object.data.materials.append(fond)

for place, rotation, taille, force in (
        ((-4.7, -3.2, 8.3), (26.0, 0.0, -24.0), 12.0, 1150.0),
        ((5.2, 4.0, 6.1), (-30.0, 0.0, 20.0), 7.0, 420.0),
        ((0.0, -6.5, 4.0), (62.0, 0.0, 0.0), 9.0, 250.0)):
    bpy.ops.object.light_add(type='AREA', location=place)
    lampe = bpy.context.object
    lampe.data.size = taille
    lampe.data.energy = force
    lampe.rotation_euler = Euler([radians(v) for v in rotation])

scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (
    0.035, 0.036, 0.042, 1.0)

#  Vue de dessus, pivotée d'un quart de tour pour que l'axe étiré par le
#  Mapping — Y — coure à l'horizontale : les planches sont alors côte à côte
#  et leurs cernes dans le sens de la longueur.
bpy.ops.object.camera_add(location=(0.0, 0.0, 6.0))
camera = bpy.context.object
camera.rotation_euler = Euler((0.0, 0.0, radians(-90.0)))
camera.data.type = 'ORTHO'
camera.data.ortho_scale = CADRE
scene.camera = camera

scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = ECHANTILLONS
scene.cycles.use_denoising = False
scene.render.resolution_x = LARGEUR
scene.render.resolution_y = HAUTEUR
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'None'

scene.render.filepath = "%s/bois.png" % SORTIE
bpy.ops.render.render(write_still=True)

# -------------------------------------------  où sont les plateaux à l'écran
bpy.context.view_layer.update()
reperes = []
for o, etiquette in ((gauche, "Vector"), (droite, "Distortion")):
    coins = [world_to_camera_view(scene, camera, o.matrix_world @ v.co)
             for v in o.data.vertices]
    xs = [c.x * LARGEUR for c in coins]
    ys = [(1.0 - c.y) * HAUTEUR for c in coins]
    reperes.append({"nom": etiquette,
                    "x": round(min(xs)), "y": round(min(ys)),
                    "large": round(max(xs) - min(xs)),
                    "haut": round(max(ys) - min(ys))})
reperes.sort(key=lambda r: r["x"])
#  CONTRÔLE : l'article annonce « à gauche le Noise sur Vector, à droite sur
#  Distortion ». La figure doit le respecter, et on le lit sur les repères.
if [r["nom"] for r in reperes] != ["Vector", "Distortion"]:
    raise SystemExit("les plateaux sont dans l'ordre inverse de l'article : %s"
                     % [r["nom"] for r in reperes])

with open(os.path.join(SORTIE, "bois.json"), "w", encoding="utf-8") as f:
    json.dump({"plateaux": reperes,
               "valeurs": {k: list(v) if hasattr(v, "__len__") else v
                           for k, v in VALEURS.items()},
               "brun_sombre": list(BRUN_SOMBRE),
               "brun_clair": list(BRUN_CLAIR),
               "taille": [LARGEUR, HAUTEUR],
               "echantillons": ECHANTILLONS,
               "version": bpy.app.version_string}, f, indent=1)

print("RENDU %d x %d, %d échantillons, Cycles, Blender %s"
      % (LARGEUR, HAUTEUR, ECHANTILLONS, bpy.app.version_string))
for r in reperes:
    print("PLATEAU %-12s x=%d y=%d %dx%d"
          % (r["nom"], r["x"], r["y"], r["large"], r["haut"]))
