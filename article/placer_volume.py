"""
IMAGE 6 de l'article — le placement du Volume probe autour de la pièce.

DEUX FAÇONS DE LANCER CE FICHIER, ET IL SAIT LAQUELLE
-----------------------------------------------------------------------------
1. DANS BLENDER, pour obtenir la VRAIE capture d'écran :

       blender --python article/placer_volume.py

   ou, sans terminal : Blender ▸ onglet **Scripting** ▸ **Open** ▸ ce fichier
   ▸ **Run Script**.

   Le script monte la pièce, pose la sonde, règle la vue 3D, ouvre l'onglet
   **Object Data** à droite et déclenche la photo tout seul. Aucune souris à
   placer, rien à survoler : il n'y a pas de menu dans cette image, donc rien
   qui exige d'être « invoqué ». L'image part sur le Bureau.

2. EN LIGNE DE COMMANDE, pour un aperçu sans interface :

       python3 article/placer_volume.py

   Rend `article/placer-irradiance-volume-apercu.png` : un tracé filaire de
   la même scène, qui sert à vérifier le cadrage et le débordement avant
   d'ouvrir Blender. Ce n'est PAS la capture — c'est un schéma.

-----------------------------------------------------------------------------
POURQUOI LE VOLUME DOIT DÉBORDER, ET DE COMBIEN
-----------------------------------------------------------------------------
C'est le sujet de l'image, et ce n'est pas une préférence de goût.

La sonde n'éclaire que ce qu'elle contient. Un mur laissé À L'EXTÉRIEUR du
volume ne reçoit aucune irradiance : il rend noir. Sur cette pièce, un volume
rentré de 45 cm sous les parois donnait une image de moyenne 86,5 ; le même
volume débordant derrière les murs, 129,9. Ce n'était pas une nuance, c'était
la moitié de la pièce.

Ici le volume déborde de 18 cm au-delà de la face INTÉRIEURE des murs. Comme
les cloisons font 12 cm d'épaisseur, il ressort donc de 6 cm derrière leur
face extérieure : chaque paroi est entièrement prise dedans, avec un peu de
marge. C'est ce léger dépassement qu'on voit sur l'image, et c'est lui qui
supprime les fuites de lumière au calcul.

Le sens du réglage est contre-intuitif : on croit protéger le calcul en
rentrant le volume à l'intérieur de la pièce, alors qu'on prive les murs de
la seule chose qui les éclaire.
"""

import math
import os
import sys

import bpy

# ---------------------------------------------------------------------------
#  LA PIÈCE — les mêmes cotes que le rendu d'ouverture de l'article
# ---------------------------------------------------------------------------
X0, X1 = -3.00, 3.00
Y0, Y1 = -3.50, 3.50
Z0, Z1 = 0.00, 3.00
EP = 0.12                      # épaisseur des cloisons

F_Y0, F_Y1 = -0.80, 1.60       # la fenêtre, dans le mur de gauche
F_Z0, F_Z1 = 0.65, 2.50

#  LE DÉBORDEMENT. Positif = la sonde ressort au-delà de la face intérieure.
DEBORD = 0.18
RESOLUTION_SONDE = (11, 12, 6)

#  Le teal des sondes dans Blender, pour le tracé filaire de l'aperçu.
TEAL = (0.28, 0.88, 0.72)
GRIS = (0.62, 0.64, 0.70)


def dossier_bureau():
    """`__file__` n'existe pas quand on lance depuis l'onglet Scripting.
    Le Bureau est le seul endroit qu'on ne peut pas rater."""
    maison = os.path.expanduser("~")
    for nom in ("Desktop", "Bureau"):
        d = os.path.join(maison, nom)
        if os.path.isdir(d):
            return d
    return maison


def matiere(nom, couleur, emission=False):
    m = bpy.data.materials.new(nom)
    m.use_nodes = True
    if emission:
        nt = m.node_tree
        nt.nodes.clear()
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs["Color"].default_value = (*couleur, 1.0)
        em.inputs["Strength"].default_value = 1.0
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    else:
        p = m.node_tree.nodes["Principled BSDF"]
        p.inputs["Base Color"].default_value = (*couleur, 1.0)
        p.inputs["Roughness"].default_value = 0.75
    m.diffuse_color = (*couleur, 1.0)      # la couleur du mode Solid
    return m


def dalle(nom, x0, x1, y0, y1, z0, z1, mat):
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    ob = bpy.context.object
    ob.name = nom
    ob.location = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    ob.scale = (x1 - x0, y1 - y0, z1 - z0)
    ob.data.materials.append(mat)
    return ob


def piece():
    """La coquille. Le mur de gauche est découpé en quatre dalles autour de
    la fenêtre — un trou dans une boîte demanderait un booléen, et un booléen
    dans une image d'interface est une complication qui ne se voit pas."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    mur = matiere("Mur", (0.78, 0.77, 0.75))
    sol = matiere("Sol", (0.42, 0.34, 0.27))

    dalle("Sol", X0 - EP, X1 + EP, Y0 - EP, Y1 + EP, Z0 - EP, Z0, sol)
    dalle("Plafond", X0 - EP, X1 + EP, Y0 - EP, Y1 + EP, Z1, Z1 + EP, mur)
    dalle("Mur_fond", X0 - EP, X1 + EP, Y1, Y1 + EP, Z0, Z1, mur)
    dalle("Mur_avant", X0 - EP, X1 + EP, Y0 - EP, Y0, Z0, Z1, mur)
    dalle("Mur_droite", X1, X1 + EP, Y0, Y1, Z0, Z1, mur)
    #  Le mur de gauche, en quatre morceaux autour de l'ouverture
    dalle("Mur_g_bas", X0 - EP, X0, F_Y0, F_Y1, Z0, F_Z0, mur)
    dalle("Mur_g_haut", X0 - EP, X0, F_Y0, F_Y1, F_Z1, Z1, mur)
    dalle("Mur_g_avant", X0 - EP, X0, Y0, F_Y0, Z0, Z1, mur)
    dalle("Mur_g_arriere", X0 - EP, X0, F_Y1, Y1, Z0, Z1, mur)

    #  Deux meubles : sans eux la pièce est une boîte vide et le lecteur ne
    #  situe plus l'échelle.
    bois = matiere("Bois", (0.35, 0.22, 0.13))
    dalle("Meuble", X1 - 0.55, X1 - 0.05, Y1 - 1.90, Y1 - 0.10, Z0, 1.80, bois)
    dalle("Table", -1.10, 0.90, -1.00, 0.60, 0.34, 0.42, bois)


def sonde():
    """
    Le Volume probe, dimensionné pour ENGLOBER les murs — c'est tout le sujet
    de l'image. Voir l'en-tête pour la mesure qui a tranché.
    """
    bpy.ops.object.lightprobe_add(
        type='VOLUME',
        location=((X0 + X1) / 2, (Y0 + Y1) / 2, (Z0 + Z1) / 2))
    ob = bpy.context.object
    ob.name = "VOLUME_PROBE"
    ob.scale = ((X1 - X0) / 2 + DEBORD,
                (Y1 - Y0) / 2 + DEBORD,
                (Z1 - Z0) / 2 + DEBORD)
    d = ob.data
    d.resolution_x, d.resolution_y, d.resolution_z = RESOLUTION_SONDE
    d.bake_samples = 1024
    d.surfel_density = 28
    d.capture_world = True
    d.capture_indirect = True
    d.capture_emission = True
    return ob


def cotes():
    """Ce que l'image affirme, en chiffres, pour la légende et le journal."""
    demi_x = (X1 - X0) / 2 + DEBORD
    return {
        "piece": (X1 - X0, Y1 - Y0, Z1 - Z0),
        "sonde": (2 * demi_x, (Y1 - Y0) + 2 * DEBORD, (Z1 - Z0) + 2 * DEBORD),
        "debord_interieur": DEBORD,
        "debord_exterieur": DEBORD - EP,
        "resolution": RESOLUTION_SONDE,
        "echantillons": RESOLUTION_SONDE[0] * RESOLUTION_SONDE[1]
                        * RESOLUTION_SONDE[2],
    }


def journal():
    c = cotes()
    print()
    print("  piece      %.2f x %.2f x %.2f m  (cloisons %.0f cm)"
          % (*c["piece"], EP * 100))
    print("  sonde      %.2f x %.2f x %.2f m" % c["sonde"])
    print("  debord     %.0f cm au-dela de la face interieure,"
          "  %.0f cm derriere la face exterieure"
          % (c["debord_interieur"] * 100, c["debord_exterieur"] * 100))
    print("  resolution %d x %d x %d  =  %d echantillons"
          % (*c["resolution"], c["echantillons"]))
    if c["debord_exterieur"] <= 0:
        raise SystemExit(
            "le volume ne ressort pas derriere les murs : avec un debord de "
            "%.0f cm et des cloisons de %.0f cm, les parois restent hors du "
            "volume et rendront noir" % (DEBORD * 100, EP * 100))


# ---------------------------------------------------------------------------
#  MODE 1 : DANS BLENDER — régler l'interface, puis photographier
# ---------------------------------------------------------------------------
def regler_vue_3d(sonde_ob):
    """
    La vue 3D : Solid + rayons X, vue depuis l'extérieur en trois quarts.

    Les rayons X ne sont pas un effet : sans eux le volume est CACHÉ par les
    murs qu'il englobe, et l'image ne montre plus rien du débordement — le
    gizmo d'une sonde est dessiné avec test de profondeur comme le reste.
    """
    from mathutils import Vector, Matrix

    oeil = Vector((9.6, -11.4, 7.6))
    cible = Vector((0.0, 0.0, 1.35))
    rot = (cible - oeil).to_track_quat('-Z', 'Y').to_matrix().to_4x4()
    pose = Matrix.Translation(oeil) @ rot

    n = 0
    for zone in bpy.context.screen.areas:
        if zone.type != 'VIEW_3D':
            continue
        sp = zone.spaces.active
        sp.shading.type = 'SOLID'
        sp.shading.show_xray = True
        sp.shading.xray_alpha = 0.42
        sp.overlay.show_overlays = True
        sp.lens = 42.0
        for region in zone.regions:
            if region.type == 'WINDOW' and region.data is not None:
                rv = region.data
                rv.view_perspective = 'PERSP'
                rv.view_matrix = pose.inverted()
                #  `update()` n'est pas une propriété mais une FONCTION RNA :
                #  la chercher avec `hasattr` sur le type répond False et
                #  laisse croire qu'elle n'existe pas. Elle existe, et sans
                #  elle la matrice posée est écrasée au redessin suivant par
                #  la position et la distance de vue mémorisées.
                rv.update()
                n += 1
        zone.tag_redraw()
    return n


def regler_panneau_data(sonde_ob):
    """L'onglet Object Data, à droite. Il n'affiche les réglages de la sonde
    que si la sonde est l'objet ACTIF — un objet sélectionné ne suffit pas."""
    bpy.ops.object.select_all(action='DESELECT')
    sonde_ob.select_set(True)
    bpy.context.view_layer.objects.active = sonde_ob

    n = 0
    for zone in bpy.context.screen.areas:
        if zone.type == 'PROPERTIES':
            zone.spaces.active.context = 'DATA'
            zone.tag_redraw()
            n += 1
    return n


def photographier():
    """
    La photo.

    `wm.redraw_timer` est indispensable : lancé par `--python`, le script
    s'exécute AVANT le premier dessin de la fenêtre. Sans redessin forcé, la
    capture fige une interface qui n'a pas encore vu nos réglages — vue par
    défaut, onglet par défaut. On photographie alors le cube de démarrage.
    """
    sortie = os.path.join(dossier_bureau(), "placer-volume-capture.png")
    for zone in bpy.context.screen.areas:
        zone.tag_redraw()
    try:
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=3)
    except Exception as e:
        print("  redessin force indisponible (%s), on tente quand meme" % e)
    bpy.ops.screen.screenshot(filepath=sortie)

    ok = os.path.exists(sortie)
    lignes = ([sortie, "%.0f Ko" % (os.path.getsize(sortie) / 1024.0)]
              if ok else ["Aucun fichier ecrit dans :", dossier_bureau()])

    def dessiner(self, _ctx):
        for l in lignes:
            self.layout.label(text=l)
    try:
        bpy.context.window_manager.popup_menu(
            dessiner, title="Capture enregistree" if ok else "Echec",
            icon='CHECKMARK' if ok else 'ERROR')
    except Exception:
        pass
    for l in lignes:
        print("  " + l)


# ---------------------------------------------------------------------------
#  MODE 2 : SANS INTERFACE — un tracé filaire pour vérifier le cadrage
# ---------------------------------------------------------------------------
def filaire(ob, couleur, epaisseur):
    """Le mode Solid n'existe pas au rendu. Pour qu'une arête apparaisse dans
    une image calculée, il faut lui donner de la matière : modificateur
    Wireframe, émission pure."""
    w = ob.modifiers.new("FIL", 'WIREFRAME')
    w.thickness = epaisseur
    w.use_replace = True
    ob.data.materials.clear()
    ob.data.materials.append(matiere("FIL_" + ob.name, couleur, emission=True))


def apercu():
    sortie = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "placer-irradiance-volume-apercu.png")
    for ob in list(bpy.data.objects):
        if ob.type == 'MESH':
            filaire(ob, GRIS, 0.014)

    s = bpy.data.objects["VOLUME_PROBE"]
    bpy.ops.mesh.primitive_cube_add(size=2.0, location=s.location)
    boite = bpy.context.object
    boite.name = "SONDE_FILAIRE"
    boite.scale = s.scale
    bpy.ops.object.transform_apply(scale=True)
    filaire(boite, TEAL, 0.028)

    cd = bpy.data.cameras.new("C")
    cd.lens = 42.0
    cam = bpy.data.objects.new("C", cd)
    cam.location = (9.6, -11.4, 7.6)
    from mathutils import Vector
    cam.rotation_euler = (Vector((0.0, 0.0, 1.35)) - cam.location) \
        .to_track_quat('-Z', 'Y').to_euler()
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam

    w = bpy.data.worlds.new("W")
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = \
        (0.020, 0.021, 0.026, 1.0)
    sc = bpy.context.scene
    sc.world = w
    sc.render.engine = 'BLENDER_EEVEE_NEXT'
    sc.render.resolution_x, sc.render.resolution_y = 1500, 1050
    sc.eevee.taa_render_samples = 32
    sc.eevee.use_raytracing = False
    sc.view_settings.view_transform = 'Standard'
    sc.render.filepath = sortie
    bpy.ops.render.render(write_still=True)
    print("  -> %s" % sortie)


def main():
    piece()
    s = sonde()
    journal()

    if bpy.app.background:
        print("  (pas d'interface : on rend l'apercu filaire)")
        apercu()
        return

    v = regler_vue_3d(s)
    p = regler_panneau_data(s)
    print("  vues 3D reglees : %d      panneaux Properties sur Data : %d"
          % (v, p))
    if p == 0:
        print("  ATTENTION : aucun editeur Properties dans cet espace de "
              "travail. Passez sur l'onglet Layout avant de relancer.")
    photographier()


if __name__ == "__main__":
    main()
