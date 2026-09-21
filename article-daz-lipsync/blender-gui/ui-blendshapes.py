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

if bas is not None:
    bas.type = 'DOPESHEET_EDITOR'
    for espace in bas.spaces:
        if espace.type == 'DOPESHEET_EDITOR':
            espace.mode = 'SHAPEKEY'
            espace.show_region_ui = False


def elargir():
    """Tirer les bordures, puis vérifier plutôt que d'espérer."""
    #  La bordure verticale entre la vue et les propriétés : on la pousse
    #  vers la gauche pour donner de la largeur aux noms.
    bpy.ops.screen.area_move(x=props.x, y=props.y + props.height // 2,
                             delta=-(LARGEUR_MINIMALE - props.width))
    #  La bordure horizontale au-dessus de la Dope Sheet : on la remonte
    #  pour que la liste des canaux tienne le plus de noms possible.
    if bas is not None:
        bpy.ops.screen.area_move(x=bas.x + bas.width // 2,
                                 y=bas.y + bas.height,
                                 delta=int(fenetre.height * 0.42))
    return None


def cadrer():
    with bpy.context.temp_override(area=vue, region=next(
            r for r in vue.regions if r.type == 'WINDOW')):
        bpy.ops.view3d.view_axis(type='FRONT')
        bpy.ops.view3d.view_selected()
    if bas is not None:
        with bpy.context.temp_override(area=bas, region=next(
                r for r in bas.regions if r.type == 'WINDOW')):
            bpy.ops.action.select_all(action='SELECT')

    if props.width < LARGEUR_MINIMALE - 40:
        raise SystemExit("la colonne fait %d px : « %s » sera tronqué"
                         % (props.width, LE_PLUS_LONG))
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


bpy.app.timers.register(elargir, first_interval=2.0)
bpy.app.timers.register(cadrer, first_interval=5.0)
