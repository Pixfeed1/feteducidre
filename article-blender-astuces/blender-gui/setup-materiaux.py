"""
Les matériaux en .001 dans l'Outliner, et le compteur Statistics.

Lancé par `capturer-anime.sh`. Deux images : la vue 3D avec l'overlay des
statistiques, puis la même aire passée en Outliner « Blender File », filtrée
sur les matériaux.

----------------------------------------------------------------------------
LES QUINZE MATÉRIAUX SONT DE VRAIES COPIES
----------------------------------------------------------------------------
Un cube, un matériau nommé Metal, et quatorze duplications réelles avec
l'option « Duplicate Data > Material » activée. Blender numérote lui-même :
Metal.001 jusqu'à Metal.014. Rien n'est écrit à la main dans la liste.

À NOTER, ET CE N'EST PAS UN DÉTAIL : cette option est DÉCOCHÉE par défaut.
Vérifié dans Blender 5.2.1 LTS lancé en `--factory-startup` —
`use_duplicate_material` vaut False, tandis que `use_duplicate_mesh` vaut
True. Un Shift+D sur une installation neuve duplique donc le MAILLAGE, pas le
matériau. Il faut l'activer ici pour reproduire la situation de l'article.

----------------------------------------------------------------------------
QUATRE OBJETS SONT SUPPRIMÉS ENSUITE
----------------------------------------------------------------------------
Leurs matériaux restent en mémoire, sans utilisateur : ce sont les « copies
fantômes » que Purge Unused Data élimine. Elles figurent toujours dans la vue
Blender File, ce qui est précisément ce qu'il faut montrer.

----------------------------------------------------------------------------
LE FILTRE PAR TYPE, ET PAS PAR NOM
----------------------------------------------------------------------------
L'état déplié d'une catégorie de l'Outliner n'est pas exposé par l'API, comme
l'état plié d'un panneau des Properties. Filtrer sur le nom « Metal » dépliait
bien quelque chose, mais la mauvaise branche : Collections > Collection >
Piece > Sphere > Metal, trois lignes par copie, et la catégorie Materials
repoussée hors de l'écran. `filter_id_type = 'MATERIAL'` ne garde que la liste
des matériaux, à plat, ce qui est exactement la figure demandée.
"""

import json
import os

import bpy

SORTIE = "/sortie"

COPIES = 14              # Metal.001 jusqu'à Metal.014
SUPPRIMES = 4            # objets effacés ensuite, matériaux orphelins
COLONNES = 5
ECART = 2.6
SUBDIVISION = 2          # pour que le compteur affiche un nombre parlant

fen = bpy.context.window_manager.windows[0]
ecran = fen.screen
aire = max(ecran.areas, key=lambda a: a.width * a.height)
reg = next(r for r in aire.regions if r.type == 'WINDOW')
CTX = dict(window=fen, screen=ecran, area=aire, region=reg)

#  L'option de l'article, à activer : elle est décochée d'usine.
bpy.context.preferences.edit.use_duplicate_material = True

with bpy.context.temp_override(**CTX):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24,
                                         location=(0.0, 0.0, 0.0))

modele = bpy.context.object
modele.name = "Piece"
bpy.ops.object.shade_smooth()
modele.modifiers.new("Subdivision", 'SUBSURF').levels = SUBDIVISION

#  Le fichier de démarrage embarque un matériau « Material », celui du cube
#  d'origine. Supprimer les objets ne l'emporte pas : il resterait en tête de
#  la liste et ferait un seizième nom qui n'a rien à y faire.
for reste in list(bpy.data.materials):
    bpy.data.materials.remove(reste)

matiere = bpy.data.materials.new("Metal")
matiere.use_nodes = True
noeud = matiere.node_tree.nodes["Principled BSDF"]
noeud.inputs["Base Color"].default_value = (0.55, 0.57, 0.62, 1.0)
noeud.inputs["Metallic"].default_value = 0.9
noeud.inputs["Roughness"].default_value = 0.3
modele.data.materials.append(matiere)

#  Quatorze duplications, chacune emportant sa copie du matériau.
for k in range(1, COPIES + 1):
    with bpy.context.temp_override(**CTX):
        bpy.ops.object.select_all(action='DESELECT')
        modele.select_set(True)
        bpy.context.view_layer.objects.active = modele
        bpy.ops.object.duplicate(linked=False)
    copie = bpy.context.object
    copie.location = ((k % COLONNES) * ECART, -(k // COLONNES) * ECART, 0.0)

noms = sorted(m.name for m in bpy.data.materials if m.name.startswith("Metal"))
if len(noms) != COPIES + 1:
    raise SystemExit("%d matériaux au lieu de %d : la duplication n'a pas "
                     "copié le matériau" % (len(noms), COPIES + 1))
if noms[-1] != "Metal.%03d" % COPIES:
    raise SystemExit("le dernier matériau s'appelle %s" % noms[-1])

#  Quelques objets effacés, leurs maillages avec. Les matériaux, eux, restent :
#  ils n'ont plus d'utilisateur et attendent le purge. C'est tout le propos —
#  le compteur d'objets descendra à onze pendant que la liste en montrera
#  toujours quinze.
#
#  Supprimer l'objet seul ne suffisait pas : le maillage lui survit et
#  continue de référencer le matériau, qui garde donc un utilisateur. La
#  première version comptait zéro orphelin et refusait de continuer — elle
#  avait raison, et la chaîne est plus longue qu'il n'y paraît.
with bpy.context.temp_override(**CTX):
    bpy.ops.object.select_all(action='DESELECT')
    condamnes = list(bpy.data.objects)[-SUPPRIMES:]
    maillages = [o.data for o in condamnes]
    for objet in condamnes:
        objet.select_set(True)
    bpy.ops.object.delete()
for maillage in maillages:
    bpy.data.meshes.remove(maillage)

orphelins = [m.name for m in bpy.data.materials if m.users == 0]
if len(orphelins) != SUPPRIMES:
    raise SystemExit("%d matériaux orphelins au lieu de %d"
                     % (len(orphelins), SUPPRIMES))

espace = aire.spaces.active
espace.overlay.show_text = True
espace.overlay.show_stats = True
espace.shading.type = 'SOLID'
fen.cursor_warp(2, 2)

with bpy.context.temp_override(**CTX):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.view3d.view_all()

with open(SORTIE + "/zones.json", "w", encoding="utf-8") as f:
    json.dump({"aire": [aire.x, aire.y, aire.width, aire.height],
               "objets": len(bpy.data.objects),
               "materiaux": noms, "orphelins": sorted(orphelins)}, f)

etat = {"i": 0, "phase": "attendre"}


def basculer_en_outliner():
    """La même aire devient l'Outliner, en vue Blender File."""
    aire.type = 'OUTLINER'
    espace2 = aire.spaces.active
    espace2.display_mode = 'LIBRARIES'
    #  Le filtre par TYPE, et pas par nom. Chercher « Metal » dépliait la
    #  branche Collections et montrait le chemin jusqu'à chaque matériau —
    #  Piece, Sphere, Metal, trois lignes par copie, et la catégorie Materials
    #  repoussée hors de l'écran. Le filtre par type ne garde qu'elle.
    espace2.use_filter_id_type = True
    espace2.filter_id_type = 'MATERIAL'


ETAPES = (lambda: None, basculer_en_outliner)


def avancer():
    if etat["phase"] == "attendre":
        if not os.path.exists(SORTIE + "/go"):
            return 0.05
        os.remove(SORTIE + "/go")
        if etat["i"] < len(ETAPES):
            ETAPES[etat["i"]]()
            etat["i"] += 1
        etat["phase"] = "montrer"
        return 0.2

    for _ in range(2):
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
    open(SORTIE + "/fait", "w").close()
    if etat["i"] >= len(ETAPES):
        open(SORTIE + "/fini", "w").close()
    etat["phase"] = "attendre"
    return 0.05


print("ETAPES %d" % len(ETAPES))
print("AIRE x=%d y=%d w=%d h=%d" % (aire.x, aire.y, aire.width, aire.height))
print("MATIERES %d dont %d orphelines" % (len(noms), len(orphelins)))
bpy.app.timers.register(avancer, first_interval=1.0)
