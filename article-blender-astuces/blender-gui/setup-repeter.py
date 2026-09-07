"""
Shift+R et F9, joués dans Blender.

Lancé par `anime-repeter.sh`. Même dialogue par fichiers que
`setup-proportionnelle.py` : le script d'appel dépose un `go`, Blender joue
l'étape suivante et répond par un `fait`, `xwd` photographie l'écran, et on
recommence. Chaque image de l'animation est donc un vrai écran.

----------------------------------------------------------------------------
UN CUBE D'UN MÈTRE, PAS DEUX
----------------------------------------------------------------------------
L'article dit « vous le décalez de 2 m », et c'est bien ce qui est joué ici.
Mais le cube de Blender fait DEUX mètres de côté : décalé de deux mètres, il
touche le précédent, et la rangée devient une barre pleine où l'on ne
distingue plus rien. Le cube est donc à un mètre, ce qui laisse un mètre de
jour entre chaque copie sans toucher au chiffre de l'article.

----------------------------------------------------------------------------
LE DÉPLACEMENT EST TAPÉ, PAS TIRÉ
----------------------------------------------------------------------------
Shift+D, puis X, puis 2, puis Entrée. C'est plus lisible qu'un glissement à la
souris — l'en-tête affiche « D: 2 » pendant la frappe — et surtout c'est exact
au centième : les copies suivantes sont alignées parce que l'opération répétée
l'est, pas parce qu'on a bien visé.

----------------------------------------------------------------------------
UN CHIFFRE N'EST PAS UNE TOUCHE
----------------------------------------------------------------------------
`event_simulate(type='TWO')` ne tape pas un 2. La saisie numérique de Blender
lit le CARACTÈRE de l'événement, pas le code de la touche — seul le pavé
numérique est reconnu par son type. Sans `unicode='2'`, le X passait bien, la
contrainte d'axe s'affichait, et le déplacement restait à zéro : les cinq
copies se posaient exactement l'une sur l'autre. Un seul cube à l'écran, et
rien dans le journal pour le dire.

----------------------------------------------------------------------------
LE PANNEAU F9 S'OUVRE SOUS LA SOURIS
----------------------------------------------------------------------------
Blender pose le panneau « Adjust Last Operation » à l'endroit du pointeur. On
descend donc la souris sous la rangée avant d'appuyer, sinon le panneau
recouvre les cubes dont il est question. Pas trop bas non plus : il fait plus
de quatre cents pixels de haut et se ferait rogner par le bord de la vue.

Les coordonnées du champ « Move X » ne sont pas interrogeables — la
disposition d'un popup n'est pas exposée par l'API. Elles ont été relevées au
pixel sur une capture, et le script vérifie au moins qu'elles tombent dans la
vue.
"""

import os
from math import radians

import bpy
from mathutils import Euler

SORTIE = "/sortie"

COTE = 1.0               # côté du cube, en mètres
ECART = 2                # décalage entre deux copies, en mètres
REPETITIONS = 3          # nombre de Shift+R
DISTANCE = 16.0

#  Position du champ « Move X » du panneau F9, en pixels depuis le point où la
#  souris se trouvait à l'ouverture. Relevé sur une capture : le champ y occupe
#  x 785..1170 et y 1050..1086, son centre tombe donc là.
CHAMP = (456, -146)

#  Blender nomme les touches du haut du clavier, mais n'en tire pas le
#  caractère. Il faut lui donner les deux.
CHIFFRES = {"2": "TWO", "3": "THREE"}

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
    bpy.ops.mesh.primitive_cube_add(size=COTE, location=(0.0, 0.0, COTE / 2))

cube = bpy.context.object
cube.name = "Cube"

#  Une vue de trois quarts, mais peu tournée : la rangée part vers +X, et il
#  faut qu'elle se lise de gauche à droite plutôt qu'en fuyant vers le fond.
rv3d.view_perspective = 'PERSP'
#  La rangée ira de 0 à ECART × (REPETITIONS + 1) ; on vise son milieu.
#
#  Et on vise 1,1 m PLUS BAS que les cubes, ce qui les remonte d'autant à
#  l'écran. Le panneau F9 fait quatre cents pixels de haut et doit tenir entre
#  la rangée et le bandeau de légende : centrer les cubes ne laissait pas la
#  place, et le bandeau venait couper le panneau en deux.
rv3d.view_location = (ECART * (REPETITIONS + 1) / 2.0, 0.0, COTE / 2 - 1.1)
rv3d.view_rotation = Euler((radians(74.0), 0.0, radians(24.0))).to_quaternion()
rv3d.view_distance = DISTANCE

CX = reg.x + reg.width // 2
CY = reg.y + reg.height // 2
#  Le point d'où l'on ouvre le panneau : sous la rangée de cubes, à gauche, et
#  assez haut pour que ses quatre cents pixels tiennent dans la vue.
BAS = (reg.x + reg.width // 4, reg.y + int(reg.height * 0.46))

ou = {"x": CX, "y": CY}


def touche(t, **mods):
    for v in ('PRESS', 'RELEASE'):
        fen.event_simulate(type=t, value=v, x=ou["x"], y=ou["y"], **mods)


def souris(x, y):
    ou["x"], ou["y"] = int(x), int(y)
    fen.event_simulate(type='MOUSEMOVE', value='NOTHING', x=ou["x"], y=ou["y"])


def chiffre(c):
    #  `unicode` n'est accepté que sur l'appui : Blender refuse le relâchement
    #  avec un caractère, et l'erreur tue le minuteur — donc la séquence.
    fen.event_simulate(type=CHIFFRES[c], value='PRESS', unicode=c,
                       x=ou["x"], y=ou["y"])
    fen.event_simulate(type=CHIFFRES[c], value='RELEASE',
                       x=ou["x"], y=ou["y"])


def rien():
    pass


def dupliquer():
    souris(CX, CY)
    touche('D', shift=True)


def ouvrir_panneau():
    souris(*BAS)
    touche('F9')


def cliquer_champ():
    x, y = BAS[0] + CHAMP[0], BAS[1] + CHAMP[1]
    if not (reg.x < x < reg.x + reg.width and reg.y < y < reg.y + reg.height):
        raise SystemExit("le champ du panneau F9 tombe hors de la vue")
    souris(x, y)
    #  Ctrl+clic entre directement en saisie de texte ; un clic simple risque
    #  d'être pris pour le début d'un glissement de la valeur.
    for v in ('PRESS', 'RELEASE'):
        fen.event_simulate(type='LEFTMOUSE', value=v, x=x, y=y, ctrl=True)


#  La séquence. D'abord la rangée, ensuite la correction après coup.
ETAPES = ([rien, rien,
           dupliquer,                               # le double suit la souris
           lambda: touche('X'),                     # contraint sur X
           lambda: chiffre('2'),                    # « D: 2 » dans l'en-tête
           lambda: touche('RET'),                   # posé : deux cubes
           rien]
          + [f for _ in range(REPETITIONS)
             for f in (lambda: touche('R', shift=True), rien)]
          + [rien,
             ouvrir_panneau,                        # F9
             rien,
             cliquer_champ,
             lambda: chiffre('3'),
             lambda: touche('RET'),                 # le dernier cube saute
             rien, rien])

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


print("ETAPES %d" % len(ETAPES))
print("AIRE x=%d y=%d w=%d h=%d" % (vue.x, vue.y, vue.width, vue.height))
print("BAS x=%d y=%d" % BAS)
bpy.app.timers.register(avancer, first_interval=1.0)
