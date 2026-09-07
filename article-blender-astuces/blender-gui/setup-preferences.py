"""
Les quatre réglages qui rendent Blender utilisable sur un portable.

Lancé par `capturer-anime.sh`, comme les séquences animées, mais il n'y a ici
que deux images à prendre : l'onglet Input et l'onglet Navigation.

----------------------------------------------------------------------------
LES PRÉFÉRENCES DANS UNE AIRE, PAS DANS UNE FENÊTRE
----------------------------------------------------------------------------
`wm.window_new` ouvrirait les préférences dans une seconde fenêtre, et `xwd`
photographie l'écran entier : on aurait les deux fenêtres l'une sur l'autre.
L'éditeur Preferences peut occuper n'importe quelle aire, alors on transforme
la plus grande — la vue 3D — et la capture est propre.

L'onglet affiché est `preferences.active_section`, réglé depuis Python : pas
besoin de cliquer dans la colonne de gauche, et la capture montre la même
chose qu'un vrai clic.

----------------------------------------------------------------------------
LE POINTEUR EST RENVOYÉ DANS UN COIN
----------------------------------------------------------------------------
Laissé sur un réglage, il fait apparaître une infobulle par-dessus la ligne
qu'on veut photographier. C'est arrivé sur la figure du rendu noir.
"""

import os

import bpy

SORTIE = "/sortie"

fen = bpy.context.window_manager.windows[0]
ecran = fen.screen

#  Les quatre cases de l'article, cochées pour de bon dans les préférences.
inp = bpy.context.preferences.inputs
inp.use_emulate_numpad = True              # la rangée du haut fait pavé
inp.use_mouse_emulate_3_button = True      # Alt + clic gauche orbite
inp.use_zoom_to_mouse = True               # le zoom vise le pointeur
inp.use_mouse_depth_navigate = True        # Auto Depth : plus de blocage

for nom in ("use_emulate_numpad", "use_mouse_emulate_3_button",
            "use_zoom_to_mouse", "use_mouse_depth_navigate"):
    if not getattr(inp, nom):
        raise SystemExit("le réglage %s n'a pas pris" % nom)

#  La plus grande aire devient l'éditeur des préférences.
aire = max(ecran.areas, key=lambda a: a.width * a.height)
aire.type = 'PREFERENCES'
fen.cursor_warp(2, 2)

ONGLETS = ('INPUT', 'NAVIGATION')
etat = {"i": 0, "phase": "attendre"}


def avancer():
    if etat["phase"] == "attendre":
        if not os.path.exists(SORTIE + "/go"):
            return 0.05
        os.remove(SORTIE + "/go")
        if etat["i"] < len(ONGLETS):
            bpy.context.preferences.active_section = ONGLETS[etat["i"]]
            etat["i"] += 1
        etat["phase"] = "montrer"
        return 0.15

    #  Deux dessins : le premier pose la nouvelle page, le second la trouve
    #  déjà en place. Un seul laissait parfois l'onglet précédent à l'image.
    for _ in range(2):
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
    open(SORTIE + "/fait", "w").close()
    if etat["i"] >= len(ONGLETS):
        open(SORTIE + "/fini", "w").close()
    etat["phase"] = "attendre"
    return 0.05


print("ETAPES %d" % len(ONGLETS))
print("AIRE x=%d y=%d w=%d h=%d" % (aire.x, aire.y, aire.width, aire.height))
bpy.app.timers.register(avancer, first_interval=1.0)
