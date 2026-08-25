"""
IMAGE 1 de l'article « Light probes Blender » — le rendu d'illustration.

    python3 article/light_probes_eevee_next.py

Produit `article/light-probes-blender-eevee-next.webp` :
un intérieur éclairé par UNE SEULE fenêtre, rendu en EEVEE Next, avec le
gizmo du Volume probe visible en filaire.

----------------------------------------------------------------------------
POURQUOI CETTE SCÈNE PLUTÔT QU'UNE AUTRE
----------------------------------------------------------------------------
L'image doit prouver quelque chose, pas décorer. Ce qu'elle doit rendre
évident, c'est que la pièce est lisible LOIN de la fenêtre — dans le coin du
fond, là où aucun rayon direct n'arrive. Si on ne voit que la flaque de
lumière au sol, on n'a rien montré : n'importe quel moteur sait faire ça.

D'où trois choix de mise en scène :

  - la fenêtre est sur le mur de GAUCHE, pas face à la caméra. On regarde
    donc la profondeur de la pièce, pas la source ;
  - le meuble sombre est posé dans le coin le plus éloigné de l'ouverture,
    contre le mur du fond : c'est le point de contrôle ;
  - une seule source. Pas de lampe d'appoint, pas de « fill » : tout ce qui
    éclaire le fond de la pièce vient du rebond, donc du Volume probe.

----------------------------------------------------------------------------
L'ORDRE DES OPÉRATIONS, QUI N'EST PAS NÉGOCIABLE
----------------------------------------------------------------------------
On CUIT la sonde AVANT de poser le gizmo. Le gizmo est un objet émissif : s'il
est présent pendant la cuisson, son émission entre dans l'irradiance et
teinte la pièce en vert. Ça ne se voit pas tout de suite, et ça fausse tout.
"""

import math
import os
import sys

import bpy

RACINE = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(RACINE, "light-probes-blender-eevee-next")

# ---------------------------------------------------------------------------
#  LA PIÈCE, EN MÈTRES
# ---------------------------------------------------------------------------
X0, X1 = -3.00, 3.00           # largeur
Y0, Y1 = -3.50, 3.50           # profondeur
Z0, Z1 = 0.00, 3.00            # hauteur
EP = 0.12                      # épaisseur des murs

#  La fenêtre, dans le mur de gauche (x = X0)
F_Y0, F_Y1 = -0.80, 1.60
F_Z0, F_Z1 = 0.65, 2.50

RESOLUTION = (1600, 900)
ECHANTILLONS = 128

GIZMO = (0.28, 0.88, 0.72)     # le teal des sondes dans Blender
GIZMO_FORCE = 2.6
GIZMO_FIL = 0.022              # épaisseur du filaire, en mètres


def couleur(nom, base, rugosite, metal=0.0, emission=None, force=0.0):
    m = bpy.data.materials.new(nom)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*base, 1.0)
    p.inputs["Roughness"].default_value = rugosite
    p.inputs["Metallic"].default_value = metal
    if emission is not None:
        p.inputs["Emission Color"].default_value = (*emission, 1.0)
        p.inputs["Emission Strength"].default_value = force
    return m


def boite(nom, centre, taille, mat):
    """Un pavé, posé par son centre."""
    bpy.ops.mesh.primitive_cube_add(size=2.0, location=centre)
    ob = bpy.context.object
    ob.name = nom
    ob.scale = tuple(t / 2.0 for t in taille)
    bpy.ops.object.transform_apply(scale=True)
    ob.data.materials.append(mat)
    return ob


def dalle(nom, x0, x1, y0, y1, z0, z1, mat):
    """Un pavé posé par ses bornes — plus lisible pour de l'architecture."""
    return boite(nom, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2),
                 (x1 - x0, y1 - y0, z1 - z0), mat)


# ---------------------------------------------------------------------------

def piece(mur, plafond, sol):
    """
    Le mur percé est découpé en QUATRE dalles — au-dessus, au-dessous, et de
    part et d'autre de l'ouverture — plutôt qu'en une dalle trouée par un
    booléen. Quatre pavés ne peuvent pas produire de face dégénérée ; un
    booléen sur un mur de douze centimètres, si.
    """
    dalle("SOL", X0 - EP, X1 + EP, Y0 - EP, Y1 + EP, Z0 - EP, Z0, sol)
    dalle("PLAFOND", X0 - EP, X1 + EP, Y0 - EP, Y1 + EP, Z1, Z1 + EP, plafond)
    dalle("MUR_FOND", X0 - EP, X1 + EP, Y1, Y1 + EP, Z0, Z1, mur)
    dalle("MUR_DOS", X0 - EP, X1 + EP, Y0 - EP, Y0, Z0, Z1, mur)
    dalle("MUR_DROIT", X1, X1 + EP, Y0, Y1, Z0, Z1, mur)

    dalle("FEN_BAS", X0 - EP, X0, Y0, Y1, Z0, F_Z0, mur)
    dalle("FEN_HAUT", X0 - EP, X0, Y0, Y1, F_Z1, Z1, mur)
    dalle("FEN_AV", X0 - EP, X0, Y0, F_Y0, F_Z0, F_Z1, mur)
    dalle("FEN_AR", X0 - EP, X0, F_Y1, Y1, F_Z0, F_Z1, mur)


def mobilier(bois, tissu, tapis, sombre, terre, noir):
    #  Le tapis : il rattrape une partie de la flaque de lumière et la
    #  renvoie vers le plafond. Sans lui la pièce est nettement plus sourde.
    dalle("TAPIS", -0.60, 2.30, -0.40, 2.40, 0.001, 0.014, tapis)

    #  Le canapé, contre le mur de droite, face à la fenêtre
    dalle("CANAPE", 1.60, 2.55, 0.30, 2.50, 0.06, 0.44, tissu)
    dalle("CANAPE_DOS", 2.32, 2.58, 0.30, 2.50, 0.44, 0.92, tissu)
    dalle("CANAPE_ACC1", 1.60, 2.58, 0.30, 0.50, 0.44, 0.66, tissu)
    dalle("CANAPE_ACC2", 1.60, 2.58, 2.30, 2.50, 0.44, 0.66, tissu)

    #  La table basse
    dalle("TABLE", 0.15, 1.05, 0.55, 1.95, 0.38, 0.42, bois)
    for x in (0.22, 0.96):
        for y in (0.64, 1.86):
            dalle("PIED", x - 0.03, x + 0.03, y - 0.03, y + 0.03, 0.0, 0.38,
                  bois)

    #  LE POINT DE CONTRÔLE : le meuble du coin du fond, celui qu'aucun
    #  rayon direct n'atteint. S'il est noir, la sonde n'a pas travaillé.
    dalle("MEUBLE", -0.20, 1.30, 3.00, 3.48, 0.0, 1.85, sombre)

    #  Le fauteuil, lui, est posé DANS la flaque : il donne l'échelle des
    #  valeurs, du direct au rebond, dans la même image.
    dalle("FAUTEUIL", -2.35, -1.45, -1.30, -0.40, 0.06, 0.42, tissu)
    dalle("FAUTEUIL_DOS", -2.35, -2.15, -1.30, -0.40, 0.42, 0.88, tissu)

    #  Le vase, seule forme ronde de la scène — les ombres douces d'un
    #  cylindre se lisent mieux que celles d'un cube.
    bpy.ops.mesh.primitive_cylinder_add(radius=0.085, depth=0.30,
                                        vertices=48,
                                        location=(0.60, 1.25, 0.57))
    v = bpy.context.object
    v.name = "VASE"
    v.data.materials.append(terre)
    bpy.ops.object.shade_smooth()

    #  Deux cadres sur le mur du fond
    for i, y in enumerate((1.70, 2.35)):
        dalle("CADRE%d" % i, -2.40, -2.38, 0, 0, 0, 0, noir)
    for i, (yy, zz) in enumerate(((-2.30, 1.70), (-1.55, 1.60))):
        dalle("CADRE_%d" % i, yy - 0.32, yy + 0.32, Y1 - 0.03, Y1 - 0.01,
              zz - 0.24, zz + 0.24, noir)


def eclairage():
    """
    UNE SEULE SOURCE. Une surface rectangulaire posée juste dehors, plus un
    ciel qui passe par l'ouverture.

    Une lampe de type SUN donnerait une flaque aux bords nets, très
    photogénique — et un rebond beaucoup plus faible. Une surface de la
    taille de la fenêtre est à la fois plus proche de la réalité et plus
    honnête vis-à-vis de ce qu'on veut démontrer.
    """
    ld = bpy.data.lights.new("FENETRE", type="AREA")
    ld.shape = "RECTANGLE"
    ld.size = F_Z1 - F_Z0 + 0.2
    ld.size_y = F_Y1 - F_Y0 + 0.2
    ld.energy = 1400.0
    ld.color = (1.0, 0.97, 0.92)
    ob = bpy.data.objects.new("FENETRE", ld)
    bpy.context.collection.objects.link(ob)
    ob.location = (X0 - 0.22, (F_Y0 + F_Y1) / 2, (F_Z0 + F_Z1) / 2)
    #  Une surface émet vers son -Z local : une rotation de -90° autour de Y
    #  envoie ce -Z vers le +X du monde, donc vers l'intérieur de la pièce.
    ob.rotation_euler = (0.0, math.radians(-90), 0.0)

    monde = bpy.data.worlds.new("CIEL")
    monde.use_nodes = True
    fond = monde.node_tree.nodes["Background"]
    fond.inputs["Color"].default_value = (0.42, 0.55, 0.75, 1.0)
    fond.inputs["Strength"].default_value = 1.1
    bpy.context.scene.world = monde


def camera():
    cd = bpy.data.cameras.new("CAM")
    cd.lens = 26.0                      # grand angle d'intérieur, sans excès
    cd.clip_start = 0.05
    cam = bpy.data.objects.new("CAM", cd)
    bpy.context.collection.objects.link(cam)
    cam.location = (2.05, -3.05, 1.62)

    #  On VISE par contrainte, jamais en calculant des angles d'Euler à la
    #  main : le calcul manuel introduit toujours un roulis, et un intérieur
    #  dont les verticales penchent est immédiatement faux à l'œil.
    cible = bpy.data.objects.new("CIBLE", None)
    bpy.context.collection.objects.link(cible)
    cible.location = (-1.30, 1.35, 1.05)
    c = cam.constraints.new("TRACK_TO")
    c.target = cible
    c.track_axis = "TRACK_NEGATIVE_Z"
    c.up_axis = "UP_Y"
    bpy.context.scene.camera = cam
    return cam


def sonde():
    """
    Le Volume probe. Il tient toute la pièce, très légèrement en retrait des
    murs : une sonde qui affleure la paroi capture des échantillons situés
    DANS le mur, et ces échantillons-là rendent des taches sombres près des
    plinthes.
    """
    bpy.ops.object.lightprobe_add(type="VOLUME",
                                  location=((X0 + X1) / 2, (Y0 + Y1) / 2,
                                            (Z0 + Z1) / 2))
    ob = bpy.context.object
    ob.name = "VOLUME_PROBE"
    ob.scale = ((X1 - X0) / 2 - 0.10, (Y1 - Y0) / 2 - 0.10,
                (Z1 - Z0) / 2 - 0.08)
    d = ob.data
    d.resolution_x, d.resolution_y, d.resolution_z = 8, 9, 4
    d.bake_samples = 768
    d.capture_world = True              # le ciel entre par l'ouverture
    d.capture_indirect = True           # les rebonds successifs
    d.capture_emission = False
    d.surfel_density = 5
    return ob


def filaire_du_gizmo(ob_sonde):
    """
    Le gizmo, en géométrie réelle.

    Le gizmo d'une sonde est un affichage de FENÊTRE 3D : il n'existe pas au
    rendu. Pour qu'il apparaisse dans l'image finale il faut le dessiner —
    ici un cube aux dimensions exactes de la sonde, passé au modificateur
    Wireframe et rendu en émission.

    Posé APRÈS la cuisson, sans quoi son émission entrerait dans
    l'irradiance et verdirait toute la pièce.
    """
    bpy.ops.mesh.primitive_cube_add(size=2.0, location=ob_sonde.location)
    ob = bpy.context.object
    ob.name = "GIZMO_FILAIRE"
    ob.scale = ob_sonde.scale
    bpy.ops.object.transform_apply(scale=True)
    w = ob.modifiers.new("FIL", "WIREFRAME")
    w.thickness = GIZMO_FIL
    w.use_replace = True
    ob.data.materials.append(
        couleur("MAT_GIZMO", GIZMO, 0.4, emission=GIZMO, force=GIZMO_FORCE))
    #  Il ne doit ni projeter d'ombre ni apparaître dans les réflexions :
    #  c'est une annotation posée sur l'image, pas un objet de la pièce.
    ob.visible_shadow = False
    ob.visible_glossy = False
    ob.visible_diffuse = False
    return ob


def reglages():
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE_NEXT"
    e = sc.eevee
    e.taa_render_samples = ECHANTILLONS
    e.use_raytracing = True             # réflexions et occlusion tracées
    e.use_shadows = True
    e.gi_diffuse_bounces = 4
    e.gi_irradiance_pool_size = "32"
    sc.render.resolution_x, sc.render.resolution_y = RESOLUTION
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "PNG"
    #  AgX, et non « Standard » : ici on rend une PHOTOGRAPHIE d'intérieur,
    #  pas une capture d'écran. Les hautes lumières de la fenêtre doivent
    #  rouler proprement au lieu de se couper net.
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Base Contrast"


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)

    mur = couleur("MUR", (0.845, 0.815, 0.762), 0.88)
    plafond = couleur("PLAFOND", (0.900, 0.885, 0.860), 0.92)
    sol = couleur("SOL_CHENE", (0.395, 0.258, 0.140), 0.44)
    bois = couleur("NOYER", (0.170, 0.108, 0.062), 0.36)
    tissu = couleur("TISSU", (0.185, 0.222, 0.258), 0.86)
    tapis = couleur("TAPIS", (0.268, 0.290, 0.225), 0.95)
    sombre = couleur("MEUBLE", (0.108, 0.104, 0.098), 0.55)
    terre = couleur("TERRE", (0.520, 0.238, 0.122), 0.48)
    noir = couleur("CADRE", (0.055, 0.052, 0.050), 0.40)

    piece(mur, plafond, sol)
    mobilier(bois, tissu, tapis, sombre, terre, noir)
    eclairage()
    camera()
    reglages()
    p = sonde()

    print("  cuisson du Volume probe (%d × %d × %d, %d échantillons)…"
          % (p.data.resolution_x, p.data.resolution_y, p.data.resolution_z,
             p.data.bake_samples))
    bpy.context.view_layer.objects.active = p
    bpy.ops.object.lightprobe_cache_bake(subset="ACTIVE")
    print("  cuisson terminée")

    filaire_du_gizmo(p)                 # APRÈS la cuisson, jamais avant

    bpy.context.scene.render.filepath = SORTIE + ".png"
    bpy.ops.render.render(write_still=True)
    print("  rendu : %s.png" % SORTIE)


main()
