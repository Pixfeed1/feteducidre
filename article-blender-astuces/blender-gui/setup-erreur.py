import bpy

fen = bpy.context.window_manager.windows[0]


def appuyer_sur_f12():
    """
    Une VRAIE frappe clavier, pas un appel d'opérateur.

    Appelé depuis un minuteur, `bpy.ops.render.render('INVOKE_DEFAULT')` ne
    signalait rien : ni barre d'état, ni éditeur Info. Le rapport n'existe que
    s'il passe par le gestionnaire de fenêtres. `event_simulate` injecte
    l'événement comme s'il venait du clavier — c'est l'option que Blender
    utilise pour tester sa propre interface.
    """
    vue = next(a for a in fen.screen.areas if a.type == 'VIEW_3D')
    fen.cursor_warp(vue.x + vue.width // 2, vue.y + vue.height // 2)
    try:
        fen.event_simulate(type='F12', value='PRESS')
        fen.event_simulate(type='F12', value='RELEASE')
        print("F12 simulé")
    except Exception as e:
        print("F12 %s" % e)
    return None


def montrer_le_rapport():
    """
    La grande zone devient un éditeur Info, APRÈS la frappe.

    La bande du bas ne fait que 147 pixels : le message y était coupé. La vue
    3D en fait plus de mille, et le rapport tient alors sur une ligne.
    """
    vue = max(fen.screen.areas, key=lambda a: a.width * a.height)
    vue.type = 'INFO'
    #  Le pointeur est ramené loin du texte, sinon il fait apparaître une
    #  infobulle par-dessus la ligne qu'on veut photographier.
    fen.cursor_warp(2, 2)
    for _ in range(3):
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
    print("INFO x=%d y=%d w=%d h=%d" % (vue.x, vue.y, vue.width, vue.height))
    open("/sortie/temoin", "w").close()
    return None


print("PRET x=0 y=0 w=0 h=0")
bpy.app.timers.register(appuyer_sur_f12, first_interval=4.0)
bpy.app.timers.register(montrer_le_rapport, first_interval=8.0)
