"""
L'interface arrangée pour la capture, puis les coordonnées imprimées.

Lancé DANS le Blender graphique du conteneur, par `capturer.sh`.

----------------------------------------------------------------------------
LE FILTRE DE RECHERCHE OUVRE LE PANNEAU
----------------------------------------------------------------------------
L'état plié ou déplié d'un panneau n'est pas exposé par l'API. Il existe
pourtant un moyen détourné et propre : `SpaceProperties.search_filter`.
Blender n'affiche alors que les panneaux qui correspondent, et il les affiche
DÉPLIÉS. On obtient donc le panneau des formes clés, ouvert, sans cliquer à
des coordonnées mesurées à la main.

----------------------------------------------------------------------------
ON IMPRIME LA GÉOMÉTRIE, ON NE LA SUPPOSE PAS
----------------------------------------------------------------------------
Le rognage se fait ensuite sur les coordonnées imprimées ici. Les deviner,
c'est couper « User Perspective » en deux, ce qui est déjà arrivé.
"""

import bpy

fenetre = bpy.context.window_manager.windows[0]
ecran = fenetre.screen

#  On repère les aires par leur type plutôt que par leur rang : la disposition
#  d'usine a déjà changé d'une version à l'autre.
aires = {}
for aire in ecran.areas:
    aires.setdefault(aire.type, []).append(aire)

if 'PROPERTIES' not in aires or 'VIEW_3D' not in aires:
    raise SystemExit("disposition inattendue : %s" % sorted(aires))

props = aires['PROPERTIES'][0]
vue = max(aires['VIEW_3D'], key=lambda a: a.width * a.height)

#  L'Outliner laisse la place : la liste des formes clés a besoin de hauteur,
#  et c'est elle le sujet de la figure.
for aire in aires.get('OUTLINER', []):
    with bpy.context.temp_override(area=aire):
        bpy.ops.screen.area_close()

tete = bpy.data.objects["Tete"]
bpy.context.view_layer.objects.active = tete
tete.select_set(True)

for espace in props.spaces:
    if espace.type == 'PROPERTIES':
        espace.context = 'DATA'
        #  Ne montrer que ce dont parle la figure, et l'ouvrir au passage.
        espace.search_filter = "Shape Keys"

for espace in vue.spaces:
    if espace.type == 'VIEW_3D':
        espace.shading.type = 'SOLID'
        espace.overlay.show_text = False
        espace.overlay.show_cursor = False
        espace.overlay.show_floor = False
        espace.overlay.show_axis_x = False
        espace.overlay.show_axis_y = False


def cadrer():
    with bpy.context.temp_override(area=vue, region=next(
            r for r in vue.regions if r.type == 'WINDOW')):
        bpy.ops.view3d.view_axis(type='FRONT')
        bpy.ops.view3d.view_selected()
    #  CONTRÔLE : le panneau doit être assez haut pour montrer une liste, et
    #  assez large pour ne pas tronquer « mouthLowerDownLeft ».
    if props.width < 300 or props.height < 500:
        raise SystemExit("le panneau fait %d × %d, trop petit pour la liste"
                         % (props.width, props.height))
    print("PROPS x=%d y=%d w=%d h=%d"
          % (props.x, props.y, props.width, props.height))
    print("VUE x=%d y=%d w=%d h=%d" % (vue.x, vue.y, vue.width, vue.height))
    print("TOUT w=%d h=%d" % (fenetre.width, fenetre.height))
    cles = tete.data.shape_keys.key_blocks
    print("CLES %d, active %s" % (len(cles), tete.active_shape_key.name))
    return None


bpy.app.timers.register(cadrer, first_interval=3.0)
