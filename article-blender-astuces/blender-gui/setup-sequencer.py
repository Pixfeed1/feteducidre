import bpy

fen = bpy.context.window_manager.windows[0]
props = next(a for a in fen.screen.areas if a.type == 'PROPERTIES')
sp = props.spaces.active
sp.context = 'OUTPUT'
#  La recherche des Properties déplie les panneaux qui contiennent le terme.
#  C'est le seul moyen d'ouvrir « Post Processing » depuis un script — l'état
#  plié d'un panneau n'est pas exposé par l'API — et c'est en prime la façon
#  dont un utilisateur trouve ce réglage.
sp.search_filter = "Sequencer"
for _ in range(3):
    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
print("PRET x=%d y=%d w=%d h=%d" % (props.x, props.y, props.width, props.height))
open("/sortie/temoin", "w").close()
