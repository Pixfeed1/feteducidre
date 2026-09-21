"""
L'interface arrangée pour la capture, puis les coordonnées imprimées.

Lancé DANS le Blender graphique du conteneur, par `capturer.sh`.

----------------------------------------------------------------------------
LE PANNEAU NE MONTRE QUE CINQ LIGNES, ET C'EST CODÉ EN DUR
----------------------------------------------------------------------------
`DATA_PT_shape_keys` appelle `template_list` avec `rows=5`. La hauteur de la
liste n'est donc pas un réglage : on ne peut pas l'augmenter depuis Python, et
une figure qui annonce « la liste des blendshapes » en montrerait cinq sur
cinquante-deux.

D'où la deuxième vue : l'éditeur de formes clés du Dope Sheet, où chaque forme
est un canal, avec son nom, et où il n'en tient que ce que la hauteur permet.
C'est aussi l'endroit où un animateur travaille vraiment une synchronisation
labiale, donc la capture montre l'outil dans son usage.

----------------------------------------------------------------------------
LA COLONNE DOIT ÊTRE LARGE, SOUS PEINE DE NE RIEN MONTRER
----------------------------------------------------------------------------
Premier essai : la colonne des propriétés faisait sa largeur d'usine, et
Blender a tronqué TOUS les noms, jusqu'à n'afficher que des icônes. Le sujet
même de la figure avait disparu. On élargit donc l'aire avant de photographier,
et un contrôle refuse la capture si la largeur ne suffit pas au plus long nom.

----------------------------------------------------------------------------
LE FILTRE DE RECHERCHE OUVRE LE PANNEAU
----------------------------------------------------------------------------
L'état plié ou déplié d'un panneau n'est pas exposé par l'API.
`SpaceProperties.search_filter` contourne proprement : Blender n'affiche que
les panneaux correspondants, et il les affiche dépliés.
"""

import bpy

#  Le plus long nom d'ARKit. Si la colonne ne peut pas l'écrire, la figure
#  ne montre rien de ce qu'elle annonce.
LE_PLUS_LONG = "mouthLowerDownRight"
LARGEUR_MINIMALE = 520

fenetre = bpy.context.window_manager.windows[0]
ecran = fenetre.screen

aires = {}
for aire in ecran.areas:
    aires.setdefault(aire.type, []).append(aire)

if 'PROPERTIES' not in aires or 'VIEW_3D' not in aires:
    raise SystemExit("disposition inattendue : %s" % sorted(aires))

props = aires['PROPERTIES'][0]
vue = max(aires['VIEW_3D'], key=lambda a: a.width * a.height)
#  Le bas de la fenêtre est une Dope Sheet en mode chronologie ; on la
#  reprend pour y lister les formes clés.
bas = None
for type_ in ('DOPESHEET_EDITOR', 'TIMELINE'):
    if aires.get(type_):
        bas = min(aires[type_], key=lambda a: a.y)
        break

for aire in aires.get('OUTLINER', []):
    with bpy.context.temp_override(area=aire):
        bpy.ops.screen.area_close()

tete = bpy.data.objects["Tete"]
bpy.context.view_layer.objects.active = tete
tete.select_set(True)
for autre in bpy.data.objects:
    autre.select_set(autre is tete)

for espace in props.spaces:
    if espace.type == 'PROPERTIES':
        espace.context = 'DATA'
        espace.search_filter = "Shape Keys"

for espace in vue.spaces:
    if espace.type == 'VIEW_3D':
        espace.shading.type = 'SOLID'
        espace.overlay.show_text = False
        espace.overlay.show_cursor = False
        espace.overlay.show_floor = False
        espace.overlay.show_axis_x = False
        espace.overlay.show_axis_y = False
        espace.overlay.show_relationship_lines = False

#  ON CHANGE LE TYPE D'AIRE, PUIS ON ATTEND UNE IMAGE.
#
#  Poser `area.type` et toucher le nouvel espace dans la même image fait
#  planter Blender : l'espace n'est pas encore construit. C'est la même
#  famille de bogue que le `node.view_all` qui refuse de s'exécuter juste
#  après un changement de type d'aire. On sépare donc en deux temps.
if bas is not None:
    bas.type = 'DOPESHEET_EDITOR'


def regler_bas():
    """Le bas montre la TÊTE, pas une seconde fois la même liste.

    Quand le repli convertit la grande aire en éditeur de formes clés, la
    chronologie du bas en devenait une deuxième, identique : deux fois la
    même chose, et plus aucun sujet à l'écran. Le bas redevient donc une
    vue 3D, et la figure montre enfin le maillage à côté de ses formes.
    """
    if bas is None:
        return None
    bas.type = 'VIEW_3D'
    return None


def regler_bas_suite():
    if bas is None or bas.type != 'VIEW_3D':
        return None
    for espace in bas.spaces:
        if espace.type == 'VIEW_3D':
            espace.shading.type = 'SOLID'
            espace.overlay.show_text = False
            espace.overlay.show_cursor = False
            espace.overlay.show_floor = False
            espace.overlay.show_axis_x = False
            espace.overlay.show_axis_y = False
            espace.overlay.show_object_origins = False
            espace.overlay.show_relationship_lines = False
    return None


def tirer(aire, x, y, delta):
    """Déplacer une bordure d'aire. Rend True si Blender a accepté.

    `screen.area_move` a un poll exigeant : appelé depuis un timer, même
    avec la fenêtre et l'écran dans le contexte, il répond « context is
    incorrect ». On lui donne donc aussi une aire et sa région, et on
    RAPPORTE l'échec au lieu de le laisser passer pour un succès.
    """
    region = next((r for r in aire.regions if r.type == 'WINDOW'), None)
    try:
        with bpy.context.temp_override(window=fenetre, screen=ecran,
                                       area=aire, region=region):
            bpy.ops.screen.area_move(x=int(x), y=int(y), delta=int(delta))
        return True
    except RuntimeError as bug:
        print("TIRER refusé : %s" % bug)
        return False


def elargir():
    """Élargir la colonne, ou basculer la grande aire si c'est refusé."""
    manque = LARGEUR_MINIMALE - props.width
    if manque > 0:
        tirer(props, props.x, props.y + props.height // 2, -manque)
    if bas is not None:
        tirer(bas, bas.x + bas.width // 2, bas.y + bas.height,
              fenetre.height * 0.40)

    #  LE REPLI, ET IL VAUT MIEUX QUE L'ORIGINAL.
    #
    #  Si les bordures n'ont pas bougé, la colonne reste trop étroite pour
    #  les noms et la liste du bas trop courte pour en montrer plus de
    #  quelques-uns. On convertit alors la GRANDE aire centrale en éditeur
    #  de formes clés : elle occupe la moitié de la fenêtre, donc elle
    #  tient des dizaines de noms, ce qui est exactement ce que la figure
    #  annonce. On y perd la vue 3D de la tête, qui n'est qu'un décor.
    if props.width < LARGEUR_MINIMALE - 40:
        print("REPLI la grande aire devient l'éditeur de formes clés")
        vue.type = 'DOPESHEET_EDITOR'
    return None


def regler_vue():
    """Une image plus tard, si la grande aire a changé de type."""
    if vue.type != 'DOPESHEET_EDITOR':
        return None
    for espace in vue.spaces:
        if espace.type == 'DOPESHEET_EDITOR':
            espace.mode = 'SHAPEKEY'
            espace.show_region_ui = False
    return None


def cadrer():
    if vue.type == 'VIEW_3D':
        with bpy.context.temp_override(area=vue, region=next(
                r for r in vue.regions if r.type == 'WINDOW')):
            bpy.ops.view3d.view_axis(type='FRONT')
            bpy.ops.view3d.view_selected()
    if bas is not None and bas.type == 'VIEW_3D':
        with bpy.context.temp_override(area=bas, region=next(
                r for r in bas.regions if r.type == 'WINDOW')):
            bpy.ops.view3d.view_axis(type='FRONT')
            bpy.ops.view3d.view_selected()

    #  CONTRÔLE : il faut qu'une des deux vues montre des noms lisibles.
    #  La colonne assez large, ou la grande aire passée en liste de formes.
    if props.width < LARGEUR_MINIMALE - 40 and vue.type != 'DOPESHEET_EDITOR':
        raise SystemExit("la colonne fait %d px et aucune liste ne la "
                         "remplace : « %s » sera tronqué"
                         % (props.width, LE_PLUS_LONG))
    print("VUE_TYPE %s" % vue.type)
    cles = tete.data.shape_keys.key_blocks
    print("PROPS x=%d y=%d w=%d h=%d"
          % (props.x, props.y, props.width, props.height))
    print("VUE x=%d y=%d w=%d h=%d" % (vue.x, vue.y, vue.width, vue.height))
    if bas is not None:
        print("BAS x=%d y=%d w=%d h=%d" % (bas.x, bas.y, bas.width,
                                           bas.height))
    print("TOUT w=%d h=%d" % (fenetre.width, fenetre.height))
    print("CLES %d, active %s" % (len(cles), tete.active_shape_key.name))
    return None


bpy.app.timers.register(regler_bas, first_interval=1.5)
bpy.app.timers.register(elargir, first_interval=3.0)
bpy.app.timers.register(regler_bas_suite, first_interval=2.5)
bpy.app.timers.register(regler_vue, first_interval=4.5)
bpy.app.timers.register(cadrer, first_interval=6.0)
