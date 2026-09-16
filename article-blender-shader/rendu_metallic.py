"""
Trois sphères, Metallic à 0, 0,5 et 1, dans un seul et même rendu.

Lancé par `rendre.sh`, en arrière-plan.

----------------------------------------------------------------------------
UN SEUL RENDU, TROIS SPHÈRES
----------------------------------------------------------------------------
Le brief demande « même Base Color, même Roughness, même éclairage ». Trois
rendus séparés l'auraient promis ; un seul le démontre. Les trois sphères sont
dans la même scène, sous les mêmes lampes, à la même seconde. Leurs matériaux
sont des COPIES d'un même matériau, et le script vérifie ensuite qu'ils ne
diffèrent que par Metallic.

----------------------------------------------------------------------------
IL FAUT QUELQUE CHOSE À REFLÉTER
----------------------------------------------------------------------------
Un métal n'a pas de couleur propre : il ne fait que renvoyer ce qui l'entoure.
Posé dans le vide, il est noir — c'est la panne du « rendu tout noir » que
connaissent les débutants. La scène comporte donc un fond, un sol et trois
sources de tailles différentes : sans elles, la sphère de droite ne
ressemblerait à rien et la figure dirait le contraire de l'article.

----------------------------------------------------------------------------
LE CUIVRE EST CELUI DES TABLES, PAS UN ORANGE CHOISI À L'OEIL
----------------------------------------------------------------------------
La Base Color est la réflectance du cuivre poli telle qu'elle figure dans les
tables de rendu physique, en linéaire. Un orange pris au jugé aurait donné un
métal plausible mais inventé, dans une section qui reproche justement aux gens
de régler au jugé.
"""

import json
import os
from math import radians

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Euler, Vector

SORTIE = "/sortie"
LARGEUR, HAUTEUR = 1800, 760
ECHANTILLONS = 192

#  Le cuivre poli, en linéaire. Base Color commune aux trois sphères.
CUIVRE = (0.955, 0.638, 0.538)
RUGOSITE = 0.22
RAYON = 1.15
ECART = 2.9

#  La seule chose qui change d'une sphère à l'autre.
METALLIQUES = (0.0, 0.5, 1.0)

scene = bpy.context.scene

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
for reste in list(bpy.data.materials):
    bpy.data.materials.remove(reste)


def matiere(nom, metallique):
    m = bpy.data.materials.new(nom)
    m.use_nodes = True
    n = m.node_tree.nodes["Principled BSDF"]
    n.inputs["Base Color"].default_value = (*CUIVRE, 1.0)
    n.inputs["Roughness"].default_value = RUGOSITE
    n.inputs["Metallic"].default_value = metallique
    return m


# -------------------------------------------------------------------  le décor
bpy.ops.mesh.primitive_plane_add(size=60.0, location=(0.0, 0.0, 0.0))
sol = bpy.context.object
fond = bpy.data.materials.new("Decor")
fond.use_nodes = True
nf = fond.node_tree.nodes["Principled BSDF"]
nf.inputs["Base Color"].default_value = (0.19, 0.19, 0.21, 1.0)
nf.inputs["Roughness"].default_value = 0.55
sol.data.materials.append(fond)

bpy.ops.mesh.primitive_plane_add(size=60.0, location=(0.0, 9.0, 0.0),
                                 rotation=(radians(90.0), 0.0, 0.0))
bpy.context.object.data.materials.append(fond)

# ---------------------------------------------------------------  les sphères
spheres = []
for i, metallique in enumerate(METALLIQUES):
    x = (i - 1) * ECART
    bpy.ops.mesh.primitive_uv_sphere_add(segments=96, ring_count=48,
                                         radius=RAYON,
                                         location=(x, 0.0, RAYON))
    o = bpy.context.object
    o.name = "Metallic %s" % metallique
    bpy.ops.object.shade_smooth()
    o.data.materials.append(matiere(o.name, metallique))
    spheres.append(o)

#  CONTRÔLE : les trois matériaux ne doivent différer QUE par Metallic.
reference = spheres[0].data.materials[0].node_tree.nodes["Principled BSDF"]
#  La comparaison se fait par INDICE et non par nom : deux prises du node
#  portent le libellé « Weight » : la recherche par nom échoue sur la seconde.
for o in spheres[1:]:
    n = o.data.materials[0].node_tree.nodes["Principled BSDF"]
    for i, entree in enumerate(n.inputs):
        if entree.name == "Metallic" or entree.is_linked:
            continue
        a = getattr(entree, "default_value", None)
        b = getattr(reference.inputs[i], "default_value", None)
        a = list(a) if hasattr(a, "__len__") else a
        b = list(b) if hasattr(b, "__len__") else b
        if a != b:
            raise SystemExit("« %s » diffère entre les sphères : %s contre %s"
                             % (entree.name, a, b))

# ----------------------------------------------------------------  la lumière
#
#  CE QUI DISTINGUE UN MÉTAL N'EST PAS LA CLARTÉ, C'EST LA STRUCTURE DU REFLET.
#  Un premier essai avait éclairci tout l'environnement pour que le cuivre
#  ressorte : les trois sphères se sont mises à se ressembler, parce qu'un
#  métal qui reflète un champ uniforme rend la même chose qu'une matière
#  diffuse. Mesuré — les trois médianes tenaient dans six niveaux de gris.
#
#  Il faut donc du contraste : un fond sombre, et de grands panneaux clairs
#  que le métal renvoie en formes nettes. C'est la façon dont on photographie
#  le métal depuis toujours, et la seule qui fasse lire le cuivre.
for place, rotation, taille, force in (
        ((-5.0, -6.0, 7.5), (38.0, 0.0, -32.0), 8.0, 360.0),
        ((3.4, -4.0, 5.2), (52.0, 0.0, 26.0), 0.9, 170.0),
        ((6.5, -7.0, 3.0), (74.0, 0.0, 44.0), 6.0, 105.0)):
    bpy.ops.object.light_add(type='AREA', location=place)
    lampe = bpy.context.object
    lampe.data.size = taille
    lampe.data.energy = force
    lampe.rotation_euler = Euler([radians(a) for a in rotation])

#  Les panneaux réfléchis. Ils sont hors du champ — la vue fait 10,3 unités de
#  large au plan des sphères, donc au-delà de x = ±5,2 rien ne se voit — mais
#  le métal les voit. Ce sont eux qui donnent au cuivre sa couleur.
for place, rotation, taille, force in (
        ((-7.4, -3.0, 3.2), (72.0, 0.0, -62.0), (9.0, 6.0), 3.2),
        ((7.4, -2.2, 4.0), (76.0, 0.0, 58.0), (7.0, 5.0), 2.1),
        ((0.0, -3.0, 8.6), (0.0, 0.0, 0.0), (11.0, 7.0), 1.5)):
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=place)
    panneau = bpy.context.object
    panneau.scale = (taille[0], taille[1], 1.0)
    panneau.rotation_euler = Euler([radians(a) for a in rotation])
    m = bpy.data.materials.new("Panneau")
    m.use_nodes = True
    arbre = m.node_tree
    for n in list(arbre.nodes):
        if n.type != 'OUTPUT_MATERIAL':
            arbre.nodes.remove(n)
    emission = arbre.nodes.new("ShaderNodeEmission")
    emission.inputs["Strength"].default_value = force
    arbre.links.new(emission.outputs["Emission"],
                    arbre.nodes["Material Output"].inputs["Surface"])
    panneau.data.materials.append(m)
    #  Invisibles pour la caméra, présents dans les reflets.
    panneau.visible_camera = False

#  UN CIEL EN DÉGRADÉ, ET PAS UN GRIS UNIFORME.
#
#  Un métal ne montre que ce qu'il reflète. Devant un champ uniforme, sombre ou
#  clair, il rend la même chose qu'une matière diffuse : les trois sphères se
#  ressemblaient, et les médianes tenaient dans six niveaux. Devant un dégradé,
#  il renvoie du clair en haut et du sombre en bas — la signature du métal, et
#  ce qui fait enfin lire le cuivre, puisque la moitié haute de la sphère
#  reflète alors quelque chose d'assez lumineux pour être teinté.
scene.world.use_nodes = True
ciel = scene.world.node_tree
for n in list(ciel.nodes):
    if n.type != 'OUTPUT_WORLD':
        ciel.nodes.remove(n)
coord = ciel.nodes.new("ShaderNodeTexCoord")
separe = ciel.nodes.new("ShaderNodeSeparateXYZ")
plage = ciel.nodes.new("ShaderNodeMapRange")
plage.inputs["From Min"].default_value = -0.35
plage.inputs["From Max"].default_value = 0.55
degrade = ciel.nodes.new("ShaderNodeValToRGB")
degrade.color_ramp.elements[0].color = (0.035, 0.037, 0.045, 1.0)
degrade.color_ramp.elements[1].color = (0.92, 0.93, 0.97, 1.0)
degrade.color_ramp.elements[1].position = 0.9
sortie = ciel.nodes.new("ShaderNodeBackground")
ciel.links.new(coord.outputs["Generated"], separe.inputs["Vector"])
ciel.links.new(separe.outputs["Z"], plage.inputs["Value"])
ciel.links.new(plage.outputs["Result"], degrade.inputs["Fac"])
ciel.links.new(degrade.outputs["Color"], sortie.inputs["Color"])
ciel.links.new(sortie.outputs["Background"],
               ciel.nodes["World Output"].inputs["Surface"])

#  Caméra reculée et objectif long plutôt que grand angle : à 13,5 m et 72 mm
#  le champ ne faisait que 6,75 unités pour 8,5 de sujet, et les deux sphères
#  des extrémités sortaient du cadre.
bpy.ops.object.camera_add(location=(0.0, -20.0, 1.95))
camera = bpy.context.object
camera.rotation_euler = Euler((radians(88.6), 0.0, 0.0))
camera.data.lens = 70.0
scene.camera = camera

# -------------------------------------------------------------------  le rendu
moteurs = [i.identifier for i in
           scene.render.bl_rna.properties["engine"].enum_items]
scene.render.engine = next(m for m in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE")
                           if m in moteurs)
scene.eevee.taa_render_samples = ECHANTILLONS
#  Le lancer de rayons est INDISPENSABLE ici : sans lui, le métal ne reflète
#  que ce qui est déjà à l'écran, et la sphère de droite se vide par les bords.
if hasattr(scene.eevee, "use_raytracing"):
    scene.eevee.use_raytracing = True
scene.render.resolution_x = LARGEUR
scene.render.resolution_y = HAUTEUR
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'None'

scene.render.filepath = "%s/metallic.png" % SORTIE
bpy.ops.render.render(write_still=True)

# ------------------------------------------  où sont les sphères à l'écran
reperes = []
for o, metallique in zip(spheres, METALLIQUES):
    v = world_to_camera_view(scene, camera, o.matrix_world.translation)
    cote = camera.matrix_world.to_3x3() @ Vector((RAYON, 0.0, 0.0))
    bord = world_to_camera_view(scene, camera,
                                o.matrix_world.translation + cote)
    reperes.append({"metallic": metallique,
                    "x": round(v.x * LARGEUR),
                    "y": round((1.0 - v.y) * HAUTEUR),
                    "rayon": round(abs(bord.x - v.x) * LARGEUR)})

with open(os.path.join(SORTIE, "zones.json"), "w", encoding="utf-8") as f:
    json.dump({"spheres": reperes, "base_color": list(CUIVRE),
               "roughness": RUGOSITE, "taille": [LARGEUR, HAUTEUR],
               "echantillons": ECHANTILLONS,
               "version": bpy.app.version_string}, f)

print("RENDU %d x %d, %d échantillons, Blender %s"
      % (LARGEUR, HAUTEUR, ECHANTILLONS, bpy.app.version_string))
for r in reperes:
    print("SPHERE metallic=%.1f x=%d y=%d rayon=%d"
          % (r["metallic"], r["x"], r["y"], r["rayon"]))
