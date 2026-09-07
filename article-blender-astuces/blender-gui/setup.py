import bpy

#  Interface au double sur un écran 4K : la colonne de droite fait alors 768
#  pixels réels pour 384 points logiques, c'est-à-dire une largeur d'Outliner
#  normale, dessinée deux fois plus finement. Pas besoin de déplacer les
#  bordures : `screen.area_move` refuse de se lancer hors d'un vrai clic.
bpy.context.preferences.view.ui_scale = 2.0

fen = bpy.context.window_manager.windows[0]
ecran = fen.screen
out = next(a for a in ecran.areas if a.type == 'OUTLINER')

sp = out.spaces.active
sp.show_restrict_column_hide = True
sp.show_restrict_column_viewport = True
sp.show_restrict_column_render = True

for _ in range(3):
    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
print("PRET x=%d y=%d w=%d h=%d" % (out.x, out.y, out.width, out.height))


def ouvrir_le_filtre():
    entete = next((r for r in out.regions if r.type == 'HEADER'), None)
    fen.cursor_warp(out.x + out.width - 70, out.y + out.height - 22)
    try:
        with bpy.context.temp_override(window=fen, area=out, region=entete):
            bpy.ops.wm.call_panel(name="OUTLINER_PT_filter", keep_open=True)
        print("FILTRE OUVERT")
    except Exception as e:
        print("FILTRE ECHEC %s" % e)
    return None


bpy.app.timers.register(ouvrir_le_filtre, first_interval=6.0)
