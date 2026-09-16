"""
Le banc d'essai : une image lue contre des couches procédurales recalculées.

Lancé par `rendre.sh`. Rend quatre fois la même sphère, sous la même lumière,
en ne changeant que le matériau, et chronomètre chaque rendu.

----------------------------------------------------------------------------
CYCLES, ET PAS EEVEE
----------------------------------------------------------------------------
L'article décrit un arbre « recalculé à chaque échantillon, pour chaque rayon,
sur chaque pixel ». C'est le modèle de Cycles. EEVEE compile le matériau en un
programme de carte graphique dont le coût ne se lit pas de la même façon :
mesurer sous EEVEE aurait répondu à une autre question que celle posée.

----------------------------------------------------------------------------
COMMENT LE TEMPS EST PRIS
----------------------------------------------------------------------------
Les quatre matériaux sont rendus dans le MÊME processus, sur la même scène :
la géométrie, l'accélérateur et la lumière ne sont construits qu'une fois, et
ce qui reste entre deux mesures est le matériau.

Un tour de chauffe précède les tours chronométrés — le premier rendu d'un
processus paie des frais qu'aucun des suivants ne paie. On garde ensuite le
MINIMUM des tours et non la moyenne : sur une machine partagée, le bruit ne
peut qu'allonger un rendu, jamais le raccourcir, et le minimum est donc
l'estimation la moins polluée.

Le débruitage est coupé : son coût est le même pour les quatre et n'aurait
servi qu'à diluer l'écart qu'on cherche à mesurer.

----------------------------------------------------------------------------
CE QUE « UNE COUCHE » VEUT DIRE ICI
----------------------------------------------------------------------------
Un noeud de texture procédurale — Noise, Voronoi, Wave. Les noeuds de mélange
et de rampe qui les relient ne sont pas comptés : ils existent dans les quatre
matériaux, à peu de chose près, et ce n'est pas eux que l'article accuse.
"""

import json
import os
import time

import bpy
from mathutils import Euler
from math import radians

SORTIE = "/sortie"
LARGEUR, HAUTEUR = 640, 640
ECHANTILLONS = 96
TOURS = 3

scene = bpy.context.scene

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
for reste in list(bpy.data.materials):
    bpy.data.materials.remove(reste)


# ------------------------------------------------------------------  la scène
bpy.ops.mesh.primitive_uv_sphere_add(segments=128, ring_count=64, radius=1.3,
                                     location=(0.0, 0.0, 0.0))
sphere = bpy.context.object
bpy.ops.object.shade_smooth()

bpy.ops.object.light_add(type='AREA', location=(-3.6, -4.2, 4.4))
cle = bpy.context.object
cle.data.size = 6.0
cle.data.energy = 620.0
cle.rotation_euler = Euler((radians(42.0), 0.0, radians(-38.0)))

bpy.ops.object.light_add(type='AREA', location=(4.2, -3.0, 1.4))
appoint = bpy.context.object
appoint.data.size = 4.0
appoint.data.energy = 180.0
appoint.rotation_euler = Euler((radians(78.0), 0.0, radians(52.0)))

scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (
    0.16, 0.17, 0.20, 1.0)

#  Assez près pour que l'ombrage pèse dans le total, assez loin pour qu'on
#  voie une sphère : à 3,55 m elle débordait du cadre de tous les côtés et la
#  figure ne montrait plus que de la texture.
bpy.ops.object.camera_add(location=(0.0, -5.4, 0.0))
camera = bpy.context.object
camera.rotation_euler = Euler((radians(90.0), 0.0, 0.0))
camera.data.lens = 60.0
scene.camera = camera


# --------------------------------------------------------------  les matériaux
def neuf(nom):
    m = bpy.data.materials.new(nom)
    m.use_nodes = True
    a = m.node_tree
    principled = a.nodes["Principled BSDF"]
    coord = a.nodes.new("ShaderNodeTexCoord")
    return m, a, principled, coord


def brancher(a, source, principled):
    """La sortie d'un arbre vers la couleur et la rugosité."""
    rampe = a.nodes.new("ShaderNodeValToRGB")
    rampe.color_ramp.elements[0].color = (0.06, 0.05, 0.05, 1.0)
    rampe.color_ramp.elements[1].color = (0.78, 0.55, 0.36, 1.0)
    a.links.new(source, rampe.inputs["Fac"])
    a.links.new(rampe.outputs["Color"], principled.inputs["Base Color"])

    rugosite = a.nodes.new("ShaderNodeMapRange")
    rugosite.inputs["To Min"].default_value = 0.18
    rugosite.inputs["To Max"].default_value = 0.72
    a.links.new(source, rugosite.inputs["Value"])
    a.links.new(rugosite.outputs["Result"], principled.inputs["Roughness"])


def matiere_image():
    """Un fichier de 2048 pixels, lu une fois et gardé en mémoire."""
    m, a, principled, coord = neuf("Image")
    image = a.nodes.new("ShaderNodeTexImage")
    image.image = bpy.data.images.load("%s/texture-2048.png" % SORTIE)
    a.links.new(coord.outputs["Generated"], image.inputs["Vector"])
    a.links.new(image.outputs["Color"], principled.inputs["Base Color"])

    clarte = a.nodes.new("ShaderNodeRGBToBW")
    rugosite = a.nodes.new("ShaderNodeMapRange")
    rugosite.inputs["To Min"].default_value = 0.18
    rugosite.inputs["To Max"].default_value = 0.72
    a.links.new(image.outputs["Color"], clarte.inputs["Color"])
    a.links.new(clarte.outputs["Val"], rugosite.inputs["Value"])
    a.links.new(rugosite.outputs["Result"], principled.inputs["Roughness"])
    return m


def matiere_couches(nombre):
    """`nombre` textures procédurales empilées, mélangées deux à deux."""
    m, a, principled, coord = neuf("%d couches" % nombre)
    precedent = None
    for i in range(nombre):
        if i % 3 == 1:
            n = a.nodes.new("ShaderNodeTexVoronoi")
            n.inputs["Scale"].default_value = 3.0 + 2.6 * i
            sortie = n.outputs["Distance"]
        elif i % 3 == 2:
            n = a.nodes.new("ShaderNodeTexWave")
            n.inputs["Scale"].default_value = 1.6 + 1.4 * i
            n.inputs["Distortion"].default_value = 6.0
            sortie = n.outputs["Fac"]
        else:
            n = a.nodes.new("ShaderNodeTexNoise")
            n.inputs["Scale"].default_value = 2.4 + 3.1 * i
            n.inputs["Detail"].default_value = 8.0
            sortie = n.outputs["Fac"]
        a.links.new(coord.outputs["Object"], n.inputs["Vector"])

        if precedent is None:
            precedent = sortie
            continue
        #  Chaque couche pèse moins que la précédente. À parts égales, la
        #  dernière écrasait toutes les autres et six couches rendaient la
        #  même image que trois — ce qui ne montrait plus l'empilement.
        melange = a.nodes.new("ShaderNodeMix")
        melange.data_type = 'FLOAT'
        melange.inputs["Factor"].default_value = 1.0 / (i + 1)
        a.links.new(precedent, melange.inputs[2])
        a.links.new(sortie, melange.inputs[3])
        precedent = melange.outputs[0]

    brancher(a, precedent, principled)
    return m


def matiere_constante():
    """Aucune texture : le plancher, ce que coûte la scène sans matériau."""
    m, a, principled, coord = neuf("Constante")
    principled.inputs["Base Color"].default_value = (0.42, 0.29, 0.19, 1.0)
    principled.inputs["Roughness"].default_value = 0.45
    return m


MATIERES = (("Constante", matiere_constante()),
            ("Image texture", matiere_image()),
            ("1 couche", matiere_couches(1)),
            ("3 couches", matiere_couches(3)),
            ("6 couches", matiere_couches(6)))


# -------------------------------------------------------------------  le rendu
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = ECHANTILLONS
scene.cycles.use_denoising = False
scene.cycles.use_adaptive_sampling = False
scene.render.resolution_x = LARGEUR
scene.render.resolution_y = HAUTEUR
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'None'

sphere.data.materials.append(MATIERES[0][1])


def poser(materiau):
    sphere.data.materials[0] = materiau


def chronometrer(materiau, ecrire=None):
    poser(materiau)
    if ecrire:
        scene.render.filepath = ecrire
    debut = time.perf_counter()
    bpy.ops.render.render(write_still=bool(ecrire))
    return time.perf_counter() - debut


#  Le tour de chauffe : le premier rendu paie des frais qu'aucun autre ne paie.
for nom, materiau in MATIERES:
    chronometrer(materiau)

mesures = []
for nom, materiau in MATIERES:
    tours = [chronometrer(materiau) for _ in range(TOURS)]
    chemin = "%s/sphere-%s.png" % (SORTIE, nom.split()[0].lower())
    chronometrer(materiau, ecrire=chemin)
    mesures.append({"nom": nom, "tours": [round(x, 3) for x in tours],
                    "temps": round(min(tours), 3),
                    "image": os.path.basename(chemin)})
    print("MESURE %-16s %s  ->  %.3f s"
          % (nom, " ".join("%.2f" % x for x in tours), min(tours)))

#  DEUX LECTURES, ET IL FAUT LES DEUX.
#
#  Le temps total comprend ce que la scène coûte de toute façon : la traversée
#  de la géométrie, les lampes, le film. Le rapport des totaux répond donc à
#  « combien de temps de rendu en plus », qui dépend de la scène.
#
#  Le temps moins ce plancher répond à « combien coûte le matériau », qui ne
#  dépend que de lui. Les deux sont vrais, ils ne disent pas la même chose, et
#  n'en donner qu'un serait choisir la réponse qui arrange.
plancher = mesures[0]["temps"]
base = mesures[1]["temps"]
for m in mesures:
    m["rapport"] = round(m["temps"] / base, 3)
    m["ombrage"] = round(m["temps"] - plancher, 3)
for m in mesures:
    m["rapport_ombrage"] = (round(m["ombrage"] / mesures[1]["ombrage"], 3)
                            if mesures[1]["ombrage"] > 0 else None)

with open(os.path.join(SORTIE, "temps.json"), "w", encoding="utf-8") as f:
    json.dump({"mesures": mesures, "taille": [LARGEUR, HAUTEUR],
               "echantillons": ECHANTILLONS, "tours": TOURS,
               "moteur": "Cycles CPU", "coeurs": os.cpu_count(),
               "version": bpy.app.version_string}, f, indent=1)

print("BANC %d x %d, %d échantillons, %d tours, Cycles CPU, %d coeurs"
      % (LARGEUR, HAUTEUR, ECHANTILLONS, TOURS, os.cpu_count()))
print("PLANCHER %.3f s (scène sans texture)" % plancher)
for m in mesures:
    print("RAPPORT %-16s total x %.2f   ombrage seul %.2f s  x %s"
          % (m["nom"], m["rapport"], m["ombrage"],
             ("%.2f" % m["rapport_ombrage"]) if m["rapport_ombrage"] else "-"))
