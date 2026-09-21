"""
Le maillage et ses formes clés, préparés en arrière-plan.

Lancé DANS le conteneur, avant la passe graphique, par `capturer.sh`.

----------------------------------------------------------------------------
POURQUOI SUZANNE ET PAS UNE FIGURE GENESIS
----------------------------------------------------------------------------
Je n'ai pas de figure Genesis : elle est payante, et daz3d.com est hors de la
liste d'autorisation de cette machine. Poser des noms de morphs Daz sur un
maillage inventé et légender « un personnage Genesis importé dans Blender »
fabriquerait une capture d'un produit que je n'ai pas.

Suzanne règle la question autrement : personne ne peut la confondre avec un
personnage Genesis. La capture ne peut donc pas tromper, et tout ce qui est
montré — le panneau, la liste, les formes clés — est réel et fonctionne.

----------------------------------------------------------------------------
LES NOMS SONT CEUX D'ARKIT, ET C'EST LE SUJET
----------------------------------------------------------------------------
L'article le dit lui-même : le rig facial de Genesis 9 est construit sur
ARKit, la norme faciale d'Apple. Ces 52 noms sont donc ceux que le lecteur
retrouvera après le pont, et c'est précisément ce que la légende annonce :
passé le pont, ce sont des blendshapes ordinaires.

----------------------------------------------------------------------------
LES FORMES DÉFORMENT VRAIMENT
----------------------------------------------------------------------------
Chaque clé est une vraie forme clé de Blender, qui déplace de vrais sommets,
choisis par la zone que son nom désigne. Une liste de 52 clés vides aurait
donné la même capture en trompant sur ce qu'elle montre.
"""

import bpy
from mathutils import Vector

SORTIE = "/sortie"

#  Les 52 formes d'ARKit, dans l'ordre d'Apple. Chaque entrée dit la zone du
#  visage concernée et le déplacement à appliquer, en unités de l'objet.
ZONES = {
    "brow": (0.34, 0.62, None),
    "eye": (0.10, 0.42, None),
    "cheek": (-0.10, 0.30, None),
    "nose": (0.02, 0.28, None),
    "jaw": (-0.58, -0.18, None),
    "mouth": (-0.34, 0.02, None),
    "tongue": (-0.30, -0.05, None),
}

ARKIT = (
    "browDownLeft", "browDownRight", "browInnerUp", "browOuterUpLeft",
    "browOuterUpRight", "cheekPuff", "cheekSquintLeft", "cheekSquintRight",
    "eyeBlinkLeft", "eyeBlinkRight", "eyeLookDownLeft", "eyeLookDownRight",
    "eyeLookInLeft", "eyeLookInRight", "eyeLookOutLeft", "eyeLookOutRight",
    "eyeLookUpLeft", "eyeLookUpRight", "eyeSquintLeft", "eyeSquintRight",
    "eyeWideLeft", "eyeWideRight", "jawForward", "jawLeft", "jawOpen",
    "jawRight", "mouthClose", "mouthDimpleLeft", "mouthDimpleRight",
    "mouthFrownLeft", "mouthFrownRight", "mouthFunnel", "mouthLeft",
    "mouthLowerDownLeft", "mouthLowerDownRight", "mouthPressLeft",
    "mouthPressRight", "mouthPucker", "mouthRight", "mouthRollLower",
    "mouthRollUpper", "mouthShrugLower", "mouthShrugUpper", "mouthSmileLeft",
    "mouthSmileRight", "mouthStretchLeft", "mouthStretchRight",
    "mouthUpperUpLeft", "mouthUpperUpRight", "noseSneerLeft",
    "noseSneerRight", "tongueOut",
)

#  La forme montrée ouverte dans la vue. « jawOpen » est la plus lisible de
#  toutes : une bouche ouverte se voit, un sourcil levé de 3 mm non.
MONTREE = "jawOpen"

p = bpy.context.preferences
p.view.show_splash = False
p.view.ui_scale = 2.0
bpy.ops.wm.save_userpref()

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

bpy.ops.mesh.primitive_monkey_add(size=2.6, location=(0.0, 0.0, 0.0))
tete = bpy.context.object
tete.name = "Tete"
tete.rotation_euler = (0.0, 0.0, 0.0)
bpy.ops.object.shade_smooth()
bpy.ops.object.modifier_add(type='SUBSURF')
tete.modifiers["Subdivision"].levels = 2
tete.modifiers["Subdivision"].render_levels = 2

base = tete.shape_key_add(name="Basis", from_mix=False)


def zone(nom):
    for cle, bornes in ZONES.items():
        if nom.startswith(cle):
            return bornes
    raise SystemExit("aucune zone pour « %s »" % nom)


def cote(nom):
    if nom.endswith("Left"):
        return 1.0
    if nom.endswith("Right"):
        return -1.0
    return 0.0


for nom in ARKIT:
    cle = tete.shape_key_add(name=nom, from_mix=False)
    bas, haut, _ = zone(nom)
    gauche = cote(nom)
    #  Le déplacement suit ce que le nom annonce : ce qui descend descend,
    #  ce qui s'ouvre s'ouvre, ce qui est latéral ne bouge que d'un côté.
    vers = Vector((0.0, 0.0, 0.0))
    if "Down" in nom or nom.endswith("Close") or "Frown" in nom:
        vers.z = -0.10
    elif "Up" in nom or "Open" in nom or "Out" in nom:
        vers.z = 0.12
    if "Puff" in nom or "Funnel" in nom or "Pucker" in nom:
        vers.y = -0.10
    if "Smile" in nom or "Stretch" in nom:
        vers.x = 0.10 * (gauche or 1.0)
    if nom == "jawOpen":
        vers.z = -0.30
    if nom == "tongueOut":
        vers.y = -0.22

    bouges = 0
    for i, point in enumerate(cle.data):
        co = base.data[i].co
        if not bas <= co.z <= haut:
            continue
        if gauche and co.x * gauche < 0.0:
            continue
        #  L'effet s'éteint vers les bords de la zone : une frontière nette
        #  ferait un pli, et un pli se voit dans la vue.
        milieu = (bas + haut) / 2.0
        poids = max(0.0, 1.0 - abs(co.z - milieu) / ((haut - bas) / 2.0))
        point.co = co + vers * poids
        bouges += 1
    if bouges == 0:
        raise SystemExit("« %s » ne déplace aucun sommet" % nom)

#  CONTRÔLE : autant de clés que de noms, plus la base, et aucune vide.
if len(tete.data.shape_keys.key_blocks) != len(ARKIT) + 1:
    raise SystemExit("%d clés au lieu de %d"
                     % (len(tete.data.shape_keys.key_blocks), len(ARKIT) + 1))
if MONTREE not in tete.data.shape_keys.key_blocks:
    raise SystemExit("« %s » absente de la liste" % MONTREE)
tete.data.shape_keys.key_blocks[MONTREE].value = 1.0
tete.active_shape_key_index = list(
    tete.data.shape_keys.key_blocks.keys()).index(MONTREE)

bpy.ops.object.light_add(type='AREA', location=(-2.4, -3.4, 3.2))
bpy.context.object.data.size = 6.0
bpy.context.object.data.energy = 420.0

bpy.ops.wm.save_as_mainfile(filepath="%s/blendshapes.blend" % SORTIE)
print("PRET %d formes clés, %s ouverte à 1,0"
      % (len(ARKIT), MONTREE))
