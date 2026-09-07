"""
La démonstration de l'édition proportionnelle, jouée dans Blender.

Lancé par `anime.sh`. Le script ne rend rien lui-même : il met la scène en
place, puis joue une séquence de frappes clavier et de mouvements de souris,
une étape à la fois, en attendant qu'on lui dise d'avancer.

----------------------------------------------------------------------------
POURQUOI UN DIALOGUE PAR FICHIERS
----------------------------------------------------------------------------
Le cercle gris de l'édition proportionnelle n'existe QUE pendant l'opérateur
modal de déplacement. Il faut donc photographier l'écran pendant que Blender
est au milieu d'un G — ce qu'aucune capture interne ne sait faire ici.

La photo est donc prise de l'extérieur, par `xwd`, et il faut synchroniser :
le script d'appel dépose un fichier `go`, Blender joue l'étape suivante et
répond par un fichier `fait`, la photo est prise, et on recommence. Chaque
image de l'animation est ainsi un vrai écran, à un vrai instant de la
manipulation.

----------------------------------------------------------------------------
POURQUOI CHAQUE ÉTAPE PREND DEUX TOURS
----------------------------------------------------------------------------
`event_simulate` ne fait que DÉPOSER l'événement dans la file. Il n'est traité
qu'au tour suivant de la boucle principale, donc après le retour du minuteur.
Redessiner dans la foulée montrerait l'écran d'avant.

Chaque étape se fait donc en deux temps : un tour qui envoie l'événement, un
tour qui redessine et prévient. C'est la première chose qui a cassé, et le
symptôme était trompeur — une animation d'une image de retard sur elle-même.

----------------------------------------------------------------------------
CHAQUE ÉVÉNEMENT PORTE SA POSITION
----------------------------------------------------------------------------
`event_simulate` place l'événement en 0, 0 quand on ne lui donne pas de
coordonnées — c'est-à-dire dans le coin de la fenêtre, sur la barre d'état.
F12 marchait quand même, parce que le rendu est un raccourci de fenêtre ; G et
O, eux, appartiennent au clavier de la vue 3D et n'arrivaient nulle part. La
séquence se jouait donc « correctement » sur une grille qui ne bougeait pas.

D'où `x=` et `y=` sur TOUTES les frappes, pas seulement sur les mouvements.

----------------------------------------------------------------------------
LA SÉLECTION SE FAIT EN MODE ÉDITION
----------------------------------------------------------------------------
Décocher `select` sur les sommets du maillage avant d'entrer en mode édition
ne suffit pas : les arêtes et les faces restent sélectionnées, et Blender les
répercute sur les sommets à l'entrée. Toute la grille se retrouvait
sélectionnée, et le déplacement aurait emporté le plan entier.

----------------------------------------------------------------------------
L'AMPLITUDE SE DÉDUIT DE LA VUE
----------------------------------------------------------------------------
Le déplacement est donné en pixels de souris, et il doit se lire quelle que
soit la taille de l'écran virtuel. Il est donc exprimé en fraction de la
hauteur du viewport, mesurée sur place, plutôt qu'en pixels écrits à la main :
la même séquence rejouée sur un écran deux fois plus grand donne exactement le
même geste à l'image près.
"""

import os
from math import radians

import bmesh
import bpy
from mathutils import Euler

SORTIE = "/sortie"

TIRAGES = 8              # images pendant le déplacement
POSE = 3                 # images d'arrêt en haut du déplacement
COURSE = 0.32            # course de la souris, en fraction de hauteur de vue
DISTANCE = 9.5           # la grille remplit alors la moitié de la vue

fen = bpy.context.window_manager.windows[0]
ecran = fen.screen
vue = next(a for a in ecran.areas if a.type == 'VIEW_3D')
reg = next(r for r in vue.regions if r.type == 'WINDOW')
rv3d = vue.spaces.active.region_3d
CTX = dict(window=fen, screen=ecran, area=vue, region=reg)

# -------------------------------------------------------------------  la scène
with bpy.context.temp_override(**CTX):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    #  Une grille assez dense pour que l'influence proportionnelle se lise, pas
    #  au point d'écraser la machine : 24 subdivisions font 625 sommets.
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=24, y_subdivisions=24,
                                    size=5.0)

grille = bpy.context.object
grille.name = "Grille"

with bpy.context.temp_override(**CTX):
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')

#  Un seul sommet sélectionné, celui du centre : c'est celui qu'on va tirer.
bm = bmesh.from_edit_mesh(grille.data)
min(bm.verts, key=lambda v: v.co.length).select = True
bm.select_flush(True)
bmesh.update_edit_mesh(grille.data)
CHOISIS = sum(1 for v in bm.verts if v.select)
if CHOISIS != 1:
    raise SystemExit("%d sommets sélectionnés au lieu d'un seul" % CHOISIS)

ts = bpy.context.scene.tool_settings
ts.use_proportional_edit = True
ts.proportional_edit_falloff = 'SMOOTH'
ts.proportional_size = 1.7

#  Une vue de trois quarts : de face la grille serait un trait, de dessus le
#  relief ne se verrait pas du tout.
rv3d.view_perspective = 'PERSP'
rv3d.view_location = (0.0, 0.0, 0.0)
rv3d.view_rotation = Euler((radians(66.0), 0.0, radians(38.0))).to_quaternion()
rv3d.view_distance = DISTANCE

CX = reg.x + reg.width // 2
CY = reg.y + reg.height // 2
PAS = max(4, int(reg.height * COURSE) // TIRAGES)


#  La position courante de la souris simulée. Elle voyage avec CHAQUE
#  événement : sans elle, la frappe arrive en bas à gauche de la fenêtre.
ou = {"x": CX, "y": CY}


def touche(t):
    for v in ('PRESS', 'RELEASE'):
        fen.event_simulate(type=t, value=v, x=ou["x"], y=ou["y"])


def souris(x, y):
    ou["x"], ou["y"] = int(x), int(y)
    fen.event_simulate(type='MOUSEMOVE', value='NOTHING', x=ou["x"], y=ou["y"])


def rien():
    pass


def saisir():
    souris(CX, CY)
    touche('G')


def tirer(k):
    return lambda: souris(CX, CY + k * PAS)


def geste():
    """Prendre le sommet, le tirer, marquer un temps, annuler."""
    return ([saisir]
            + [tirer(k) for k in range(1, TIRAGES + 1)]
            + [rien] * POSE
            + [lambda: touche('ESC'), rien])


#  La séquence. Deux fois le même geste, la seule différence étant la touche O
#  qui sépare les deux — c'est tout le propos de la figure.
ETAPES = [rien, rien] + geste() + [lambda: touche('O'), rien] + geste()

etat = {"i": 0, "phase": "attendre"}


def avancer():
    """Un dialogue en trois phases : attendre, agir, montrer."""
    if etat["phase"] == "attendre":
        if not os.path.exists(SORTIE + "/go"):
            return 0.05
        os.remove(SORTIE + "/go")
        if etat["i"] < len(ETAPES):
            ETAPES[etat["i"]]()
            etat["i"] += 1
        etat["phase"] = "montrer"
        #  Le délai laisse la boucle principale consommer l'événement qu'on
        #  vient de déposer : sans lui, on photographie l'écran d'avant.
        return 0.15

    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
    open(SORTIE + "/fait", "w").close()
    if etat["i"] >= len(ETAPES):
        open(SORTIE + "/fini", "w").close()
    etat["phase"] = "attendre"
    return 0.05


print("ETAPES %d pas=%d sommets=%d" % (len(ETAPES), PAS, CHOISIS))
print("AIRE x=%d y=%d w=%d h=%d" % (vue.x, vue.y, vue.width, vue.height))
print("VUE x=%d y=%d w=%d h=%d" % (reg.x, reg.y, reg.width, reg.height))
bpy.app.timers.register(avancer, first_interval=1.0)
