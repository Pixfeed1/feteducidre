"""L'interface arrangée pour la capture qui servira de contenu d'écran.

----------------------------------------------------------------------------
ON PREND UN ESPACE DE TRAVAIL LIVRÉ, ON N'EN BRICOLE PAS UN
----------------------------------------------------------------------------
Découper des aires à la main veut dire `screen.area_move`, dont le poll
refuse d'être appelé depuis un timer : c'est la panne qui avait coûté la
vue 3D de la figure des formes clés. Blender livre déjà un espace de travail
« Shading », vue 3D en haut et éditeur de shader en bas. On le sélectionne,
et il n'y a plus une seule bordure à déplacer.

----------------------------------------------------------------------------
L'APERÇU MATÉRIAU FIGE BLENDER, ET IL FAUT L'ÉTEINDRE AVANT D'ENTRER
----------------------------------------------------------------------------
Premier essai : la capture sortait toujours identique, avec « Compiling
EEVEE engine shaders » écrit dans la vue et pas une seule ligne de trace
dans le journal. L'espace « Shading » ouvre ses vues en aperçu matériau ;
sans GPU, EEVEE compile ses shaders via llvmpipe, et cette compilation
BLOQUE la boucle principale. Les timers suivants ne s'exécutaient donc
jamais, et l'écran photographié était celui d'un Blender gelé.

Passer les vues en ombrage solide APRÈS avoir changé d'espace ne sert à
rien : le gel commence dans la même image que le changement. On règle donc
l'ombrage sur les écrans de l'espace AVANT de l'activer, ce que l'API
permet, `bpy.data.workspaces[...].screens` étant accessible même pour un
espace qui n'est pas au premier plan.

----------------------------------------------------------------------------
LES `print` SONT VIDÉS À LA MAIN
----------------------------------------------------------------------------
Le conteneur tue Blender à la fin de la pose. Sans `flush`, la sortie
standard part avec le processus et le journal reste muet, ce qui fait
passer un timer qui n'a pas tourné pour un timer sans rien à dire.
"""

import sys

import bpy

fenetre = bpy.context.window_manager.windows[0]
ESPACE = "Shading"


def dire(ligne):
    print(ligne)
    sys.stdout.flush()


def ecran_actif():
    """L'écran de l'espace visé, PAS `fenetre.screen`.

    Deuxième panne de la même capture : après `fenetre.workspace = espace`,
    l'interface affichée est bien celle de « Shading », mais `fenetre.screen`
    continue de rendre l'écran de « Layout ». Les aires listées étaient donc
    celles d'un espace invisible : la fermeture ne trouvait aucun navigateur
    de fichiers à fermer, et le cadrage recadrait une vue que personne ne
    photographierait. On demande l'écran à l'espace de travail, qui lui sait
    de quoi il est fait.
    """
    ecrans = bpy.data.workspaces[ESPACE].screens
    if not ecrans:
        raise SystemExit("l'espace « %s » n'a aucun écran" % ESPACE)
    return ecrans[0]


def choisir_espace():
    if ESPACE not in bpy.data.workspaces:
        raise SystemExit("espace « %s » absent : %s"
                         % (ESPACE, list(bpy.data.workspaces.keys())))
    espace = bpy.data.workspaces[ESPACE]

    #  L'ombrage est réglé pendant que l'espace est encore en coulisses.
    eteintes = 0
    for ecran in espace.screens:
        for aire in ecran.areas:
            for vue in aire.spaces:
                if vue.type == 'VIEW_3D':
                    vue.shading.type = 'SOLID'
                    vue.shading.color_type = 'MATERIAL'
                    eteintes += 1
    dire("PREREGLE %d vue(s) en ombrage solide" % eteintes)

    fenetre.workspace = espace
    dire("ESPACE %s" % ESPACE)
    return None


def fermer_colonne():
    """La colonne de gauche de « Shading » ne sert à rien ici.

    L'espace livré met un navigateur de fichiers et un éditeur d'image à
    gauche ; sans fichier ouvert, les deux sont des rectangles vides. On les
    ferme, et la vue 3D et l'éditeur de shader prennent toute la largeur.
    `screen.area_close` n'a pas le poll capricieux de `screen.area_move`, il
    accepte d'être appelé depuis un timer.
    """
    ecran = ecran_actif()
    for aire in [a for a in ecran.areas
                 if a.type in ('FILE_BROWSER', 'IMAGE_EDITOR')]:
        type_ = aire.type
        try:
            with bpy.context.temp_override(window=fenetre, screen=ecran,
                                           area=aire):
                bpy.ops.screen.area_close()
            dire("FERME %s" % type_)
        except RuntimeError as bug:
            dire("FERMETURE refusée sur %s : %s" % (type_, bug))
    dire("RESTE %s" % sorted({a.type for a in ecran_actif().areas}))
    return None


def regler():
    ecran = ecran_actif()
    types = {}
    for aire in ecran.areas:
        types.setdefault(aire.type, []).append(aire)
    dire("AIRES %s" % {k: len(v) for k, v in types.items()})

    if not types.get('VIEW_3D'):
        raise SystemExit("pas de vue 3D dans %s" % sorted(types))
    for aire in types['VIEW_3D']:
        for vue in aire.spaces:
            if vue.type == 'VIEW_3D':
                #  CONTRÔLE : si l'ombrage a repris l'aperçu matériau, on
                #  le dit, parce que la capture suivante sera gelée.
                if vue.shading.type != 'SOLID':
                    dire("ALERTE ombrage %s, on repasse en solide"
                         % vue.shading.type)
                    vue.shading.type = 'SOLID'
                vue.overlay.show_floor = True
                vue.overlay.show_axis_x = True
                vue.overlay.show_axis_y = True
                vue.overlay.show_text = True
    return None


def cadrer():
    ecran = ecran_actif()
    vue = max((a for a in ecran.areas if a.type == 'VIEW_3D'),
              key=lambda a: a.width * a.height)
    region = next(r for r in vue.regions if r.type == 'WINDOW')
    with bpy.context.temp_override(window=fenetre, screen=ecran,
                                   area=vue, region=region):
        bpy.ops.view3d.view_axis(type='FRONT')
        bpy.ops.view3d.view_orbit(angle=0.62, type='ORBITRIGHT')
        bpy.ops.view3d.view_orbit(angle=0.30, type='ORBITUP')
        bpy.ops.view3d.view_selected()

    espace = next(e for e in vue.spaces if e.type == 'VIEW_3D')
    dire("VUE x=%d y=%d w=%d h=%d distance %.3f ombrage %s"
         % (vue.x, vue.y, vue.width, vue.height,
            espace.region_3d.view_distance, espace.shading.type))
    dire("TOUT w=%d h=%d" % (fenetre.width, fenetre.height))
    actif = bpy.context.view_layer.objects.active
    dire("ACTIF %s" % (actif.name if actif else "aucun"))
    return None


bpy.app.timers.register(choisir_espace, first_interval=1.5)
bpy.app.timers.register(fermer_colonne, first_interval=3.0)
bpy.app.timers.register(regler, first_interval=4.5)
bpy.app.timers.register(cadrer, first_interval=6.0)
