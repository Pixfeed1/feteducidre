"""
Le Bloom là où il vit depuis Blender 4.2 : un nœud Glare dans le compositeur.

Lancé par `capturer-anime.sh`. Deux images : le compositeur avec la chaîne
Render Layers → Glare → Composite, puis le menu Viewport Shading avec
Compositor réglé sur Always.

----------------------------------------------------------------------------
UNE VRAIE SCÈNE DERRIÈRE LE MONTAGE
----------------------------------------------------------------------------
Un néon émissif dans le noir, ce que l'article donne en exemple. Le nœud Glare
n'est pas posé sur une image vide : il travaille sur un rendu où il a quelque
chose à faire, et la vue 3D montre le résultat.

----------------------------------------------------------------------------
LE MENU DÉROULANT S'OUVRE PAR `wm.call_panel`
----------------------------------------------------------------------------
Le menu Viewport Shading est un popover, pas une zone de l'interface : il
n'existe qu'ouvert. `wm.call_panel` l'ouvre par son identifiant sans qu'on ait
à cliquer à des coordonnées relevées à la main, et `keep_open` l'empêche de se
refermer au premier événement — sinon il aurait disparu avant la photo.
"""

import os
from math import radians

import bpy
from mathutils import Euler

SORTIE = "/sortie"

fen = bpy.context.window_manager.windows[0]
ecran = fen.screen
aire = max(ecran.areas, key=lambda a: a.width * a.height)
reg = next(r for r in aire.regions if r.type == 'WINDOW')
CTX = dict(window=fen, screen=ecran, area=aire, region=reg)

scene = bpy.context.scene

# ------------------------------------------------------------------  la scène
with bpy.context.temp_override(**CTX):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

for reste in list(bpy.data.materials):
    bpy.data.materials.remove(reste)


def emissif(nom, couleur, force):
    m = bpy.data.materials.new(nom)
    m.use_nodes = True
    n = m.node_tree.nodes["Principled BSDF"]
    n.inputs["Base Color"].default_value = (0.02, 0.02, 0.03, 1.0)
    n.inputs["Emission Color"].default_value = (*couleur, 1.0)
    n.inputs["Emission Strength"].default_value = force
    return m


#  Le tube de néon : un tore fin, posé debout, qui brille fort.
bpy.ops.mesh.primitive_torus_add(major_radius=1.5, minor_radius=0.09,
                                 major_segments=96, minor_segments=16,
                                 location=(0.0, 0.0, 1.7),
                                 rotation=(radians(90.0), 0.0, 0.0))
neon = bpy.context.object
neon.name = "Neon"
bpy.ops.object.shade_smooth()
neon.data.materials.append(emissif("Neon", (0.15, 0.85, 1.0), 4.0))

bpy.ops.mesh.primitive_plane_add(size=24.0, location=(0.0, 0.0, 0.0))
sol = bpy.context.object
m_sol = bpy.data.materials.new("Sol")
m_sol.use_nodes = True
n_sol = m_sol.node_tree.nodes["Principled BSDF"]
n_sol.inputs["Base Color"].default_value = (0.04, 0.04, 0.05, 1.0)
n_sol.inputs["Roughness"].default_value = 0.25
sol.data.materials.append(m_sol)

scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[1].default_value = 0.0

bpy.ops.object.camera_add(location=(0.0, -11.0, 1.7))
camera = bpy.context.object
camera.rotation_euler = Euler((radians(90.0), 0.0, 0.0))
scene.camera = camera

moteurs = [i.identifier for i in
           scene.render.bl_rna.properties["engine"].enum_items]
scene.render.engine = next(m for m in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE")
                           if m in moteurs)

# -------------------------------------------------------------  le compositeur
#
#  ATTENTION, ÇA A ENCORE BOUGÉ. En 4.2 le compositeur vivait dans
#  `scene.node_tree` et se terminait par un nœud « Composite ». En 5.x il est
#  devenu un GROUPE DE NŒUDS rangé dans `scene.compositing_node_group`, et le
#  nœud Composite n'existe plus du tout — la sortie est un « Group Output ».
#  Le réglage du Glare a suivi : `glare_type` n'est plus une propriété du nœud
#  mais une ENTRÉE de menu, comme la qualité et le seuil.
#
#  Autrement dit, la manœuvre que l'article décrit pour 4.2 ne se fait plus
#  tout à fait comme ça dans la version que montrent toutes les autres figures.
scene.use_nodes = True
arbre = bpy.data.node_groups.new("Compositing", "CompositorNodeTree")
scene.compositing_node_group = arbre

couches = arbre.nodes.new("CompositorNodeRLayers")
couches.location = (-520.0, 0.0)

glare = arbre.nodes.new("CompositorNodeGlare")
glare.location = (-140.0, 60.0)
glare.inputs["Type"].default_value = 'Bloom'
glare.inputs["Quality"].default_value = 'High'
glare.inputs["Threshold"].default_value = 1.0
glare.inputs["Size"].default_value = 7

#  La sortie du groupe n'existe pas d'office : brancher sur le socket virtuel
#  du Group Output faisait bien une liaison, mais une liaison ROUGE, marquée
#  d'un triangle d'alerte, parce que le groupe n'avait aucune sortie déclarée.
#  Ça se voyait sur la première capture.
arbre.interface.new_socket(name="Image", in_out='OUTPUT',
                           socket_type='NodeSocketColor')
sortie = arbre.nodes.new("NodeGroupOutput")
sortie.location = (300.0, 0.0)

arbre.links.new(couches.outputs["Image"], glare.inputs["Image"])
arbre.links.new(glare.outputs["Image"], sortie.inputs[0])

if glare.inputs["Type"].default_value != 'Bloom':
    raise SystemExit("le nœud Glare n'est pas en mode Bloom : %s"
                     % glare.inputs["Type"].default_value)
if len(arbre.links) != 2:
    raise SystemExit("%d liaisons au lieu de deux" % len(arbre.links))
if any(not lien.is_valid for lien in arbre.links):
    raise SystemExit("une des deux liaisons est invalide")

#  Les nœuds fraîchement créés sortent sélectionnés, cerclés de blanc. On les
#  désélectionne par l'API : l'opérateur `node.select_all` ne passe pas son
#  poll tant que l'éditeur n'a pas été dessiné une fois.
for n in arbre.nodes:
    n.select = False

#  La vue 3D montre le résultat, compositeur compris : c'est le réglage dont
#  parle la seconde moitié de l'article.
espace = aire.spaces.active
espace.shading.type = 'RENDERED'
espace.shading.use_compositor = 'ALWAYS'
espace.region_3d.view_perspective = 'CAMERA'
if espace.shading.use_compositor != 'ALWAYS':
    raise SystemExit("le compositeur de la vue n'est pas sur Always")

fen.cursor_warp(2, 2)

etat = {"i": 0, "phase": "attendre"}


def passer_au_compositeur():
    """La grande aire devient l'éditeur de nœuds, en mode Compositing."""
    aire.type = 'NODE_EDITOR'
    espace2 = aire.spaces.active
    espace2.tree_type = 'CompositorNodeTree'
    #  Le panneau latéral s'ouvre sur les propriétés du groupe, qui n'ont rien
    #  à voir avec la figure et mangent un quart de la largeur.
    espace2.show_region_ui = False
    espace2.show_region_toolbar = False


def cadrer_les_noeuds():
    """
    Recentrer la vue sur les trois nœuds.

    En deux temps, et pas en un : juste après le changement de type d'aire,
    `node.view_all` ne passe pas son poll — l'éditeur n'a pas encore été
    dessiné, sa région n'a pas de vue à recentrer. Une image plus tard, si.
    """
    reg2 = next(r for r in aire.regions if r.type == 'WINDOW')
    with bpy.context.temp_override(window=fen, screen=ecran, area=aire,
                                   region=reg2):
        bpy.ops.node.view_all()


def rouvrir_la_vue():
    """Retour à la vue 3D, et le menu Viewport Shading déroulé par-dessus."""
    aire.type = 'VIEW_3D'
    #  Les réglages d'affichage sont RÉAPPLIQUÉS ici, sur l'espace redevenu
    #  actif. Posés avant le passage par l'éditeur de nœuds, ils ne
    #  revenaient pas : la vue était retombée en Solid, et une figure sur le
    #  compositeur de la vue 3D montrant un viewport non rendu n'aurait rien
    #  valu.
    espace2 = aire.spaces.active
    espace2.shading.type = 'RENDERED'
    espace2.shading.use_compositor = 'ALWAYS'
    espace2.region_3d.view_perspective = 'CAMERA'
    espace2.overlay.show_floor = False
    espace2.overlay.show_axis_x = False
    espace2.overlay.show_axis_y = False
    if espace2.shading.type != 'RENDERED':
        raise SystemExit("la vue n'est pas en rendu")

    reg2 = next(r for r in aire.regions if r.type == 'WINDOW')
    #  Le popover s'ouvre autour du pointeur. Posé trop haut, il sortait par le
    #  bord supérieur de l'écran et arrivait décapité.
    fen.cursor_warp(reg2.x + 240, reg2.y + reg2.height - 420)
    with bpy.context.temp_override(window=fen, screen=ecran, area=aire,
                                   region=reg2):
        #  Le cadre de la caméra occupe le tiers de la vue par défaut ; ajusté,
        #  le néon fait sa taille à l'image.
        bpy.ops.view3d.view_center_camera()
        bpy.ops.wm.call_panel(name="VIEW3D_PT_shading", keep_open=True)


ETAPES = (passer_au_compositeur, cadrer_les_noeuds, rouvrir_la_vue)


def avancer():
    if etat["phase"] == "attendre":
        if not os.path.exists(SORTIE + "/go"):
            return 0.05
        os.remove(SORTIE + "/go")
        if etat["i"] < len(ETAPES):
            ETAPES[etat["i"]]()
            etat["i"] += 1
        etat["phase"] = "montrer"
        return 0.3

    for _ in range(2):
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
    open(SORTIE + "/fait", "w").close()
    if etat["i"] >= len(ETAPES):
        open(SORTIE + "/fini", "w").close()
    etat["phase"] = "attendre"
    return 0.05


print("ETAPES %d" % len(ETAPES))
print("AIRE x=%d y=%d w=%d h=%d" % (aire.x, aire.y, aire.width, aire.height))
print("GLARE %s, %d liaisons, %d objets"
      % (glare.inputs["Type"].default_value, len(arbre.links),
         len(bpy.data.objects)))
bpy.app.timers.register(avancer, first_interval=1.0)
