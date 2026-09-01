"""
Le rendu des clés, fond de la figure « Qui détient les accès ? ».

    python3 article-agence-web/cles_acces.py

Produit `article-agence-web/fond-cles.png` (1600 × 900).

----------------------------------------------------------------------------
POURQUOI DES CLÉS, ET POURQUOI UN RENDU
----------------------------------------------------------------------------
Les deux versions précédentes de cette figure étaient du texte mis en page. La
seconde était mieux composée que la première, mais elle restait ce qu'elle
était : des lignes de texte. Un lecteur qui voit ça dans un article se demande
pourquoi c'est une image plutôt qu'un paragraphe — et il a raison.

Une image doit porter son sens par l'image. Ici le sens tient en une phrase :
il y a quatre clés, et une seule ne se remplace pas. Ça se montre. Une clé de
laiton, seule, nette, au premier plan ; trois clés d'acier posées ensemble plus
loin, dans le flou. On a compris avant d'avoir lu quoi que ce soit.

Les banques d'images sont refusées par la politique de sortie de cet
environnement, et de toute façon les photos de trousseaux sont vues partout. Un
rendu règle les deux : le cadrage est fait pour cette image-là, et la licence
ne se pose pas.

----------------------------------------------------------------------------
LES CLÉS SONT CONSTRUITES, PAS DÉCOUPÉES
----------------------------------------------------------------------------
Pas de booléens. Le panneton — la partie dentée — est une SUITE DE BOÎTES qui
partagent leur arête supérieure et dont l'arête inférieure varie. Les dents
naissent de cette variation. C'est plus simple qu'une découpe, plus rapide, et
ça ne laisse aucune géométrie douteuse dans les angles.

L'anneau est un tore aplati : un tore brut donnerait une section ronde, alors
qu'un anneau de clé est plat. On l'écrase sur Z jusqu'à l'épaisseur de la clé.

----------------------------------------------------------------------------
LE CADRAGE EST VÉRIFIÉ AVANT LE RENDU
----------------------------------------------------------------------------
`verifier_cadrage()` projette chaque clé dans la vue caméra et refuse de lancer
le calcul si le laiton n'est pas dans la moitié gauche et le bas de l'image, si
les trois autres ne sont pas à droite, ou si le tiers haut n'est pas libre —
c'est là que le titre se posera. Un rendu de deux minutes qu'on découvre mal
cadré, c'est deux minutes perdues et une correction à l'aveugle.
"""

import json
import math
import os
import sys

import bpy
from mathutils import Vector

RACINE = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(RACINE, "fond-cles")
#  Les positions des clés dans le cadre, écrites pour le montage : c'est ce
#  fichier qui lui permet de poser les libellés SUR les clés sans qu'aucune
#  coordonnée ne soit recopiée à la main d'un script à l'autre.
CADRAGE = os.path.join(RACINE, "fond-cles-cadrage.json")

RESOLUTION = (1600, 900)
ECHANTILLONS = 96

EPAISSEUR = 0.0026          # 2,6 mm, l'épaisseur d'une clé plate
ANNEAU_R = 0.0105           # rayon moyen de l'anneau
ANNEAU_T = 0.0034           # largeur du jonc

#  Le profil du panneton : (longueur, hauteur) de chaque tronçon. L'arête du
#  haut est commune, celle du bas suit ces hauteurs — d'où les dents.
PROFIL = ((0.0065, 0.0062), (0.0040, 0.0036), (0.0052, 0.0062),
          (0.0038, 0.0032), (0.0060, 0.0058), (0.0040, 0.0040),
          (0.0055, 0.0050))

#  Les quatre clés : (nom, matière, échelle, x, y, z, angle en degrés).
#  Le laiton est seul, devant, à gauche. Les trois aciers sont posés ensemble,
#  plus loin, légèrement empilés — c'est l'empilement qui les fait lire comme
#  un groupe et non comme trois objets rangés.
CLES = (
    ("Domaine", "LAITON", 1.22, -0.052, -0.034, 0.0000, 24.0),
    ("Acier1", "ACIER", 1.00, 0.040, 0.026, 0.0000, 104.0),
    ("Acier2", "ACIER", 1.00, 0.062, 0.050, 0.0027, 12.0),
    ("Acier3", "ACIER", 1.00, 0.054, 0.016, 0.0054, 158.0),
)


def matiere(nom, base, rugosite, metal=0.0):
    m = bpy.data.materials.new(nom)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*base, 1.0)
    p.inputs["Roughness"].default_value = rugosite
    p.inputs["Metallic"].default_value = metal
    return m


def bois():
    """
    Un plateau de noyer, avec du fil.

    Le premier essai était un aplat sombre uniforme. Sous une lumière rasante
    ça ne donne pas du bois, ça donne un fond de studio — et une clé posée sur
    un fond de studio a l'air découpée. Ce qui manque n'est pas la couleur,
    c'est la MATIÈRE : un bruit très étiré dans un sens, qui module à la fois
    la teinte et le relief. Deux nœuds de plus, et le plateau redevient une
    table.
    """
    m = bpy.data.materials.new("BOIS")
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    p.inputs["Roughness"].default_value = 0.44
    p.inputs["Metallic"].default_value = 0.0

    coord = nt.nodes.new("ShaderNodeTexCoord")
    mapping = nt.nodes.new("ShaderNodeMapping")
    #  Le fil court le long de X : on comprime le bruit sur Y, ce qui l'étire
    #  dans l'autre sens.
    mapping.inputs["Scale"].default_value = (1.0, 26.0, 1.0)
    bruit = nt.nodes.new("ShaderNodeTexNoise")
    bruit.inputs["Scale"].default_value = 14.0
    bruit.inputs["Detail"].default_value = 10.0
    bruit.inputs["Roughness"].default_value = 0.62

    rampe = nt.nodes.new("ShaderNodeValToRGB")
    rampe.color_ramp.elements[0].position = 0.32
    rampe.color_ramp.elements[0].color = (0.026, 0.014, 0.008, 1.0)
    rampe.color_ramp.elements[1].position = 0.72
    rampe.color_ramp.elements[1].color = (0.068, 0.041, 0.024, 1.0)

    bosse = nt.nodes.new("ShaderNodeBump")
    bosse.inputs["Strength"].default_value = 0.22

    nt.links.new(coord.outputs["Object"], mapping.inputs["Vector"])
    nt.links.new(mapping.outputs["Vector"], bruit.inputs["Vector"])
    nt.links.new(bruit.outputs["Fac"], rampe.inputs["Fac"])
    nt.links.new(rampe.outputs["Color"], p.inputs["Base Color"])
    nt.links.new(bruit.outputs["Fac"], bosse.inputs["Height"])
    nt.links.new(bosse.outputs["Normal"], p.inputs["Normal"])
    return m


def boite(nom, x0, x1, y0, y1, z0, z1, mat, parent):
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    ob = bpy.context.object
    ob.name = nom
    ob.location = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    ob.scale = (x1 - x0, y1 - y0, z1 - z0)
    bpy.ops.object.transform_apply(scale=True)
    ob.data.materials.append(mat)
    ob.parent = parent
    return ob


def cle(nom, mat, echelle, x, y, z, angle):
    """Une clé complète, accrochée à un vide qu'on pose ensuite où l'on veut."""
    pivot = bpy.data.objects.new("P_" + nom, None)
    bpy.context.collection.objects.link(pivot)
    pivot.location = (x, y, z + EPAISSEUR * echelle / 2)
    pivot.rotation_euler = (0.0, 0.0, math.radians(angle))
    pivot.scale = (echelle, echelle, echelle)

    demi = EPAISSEUR / 2

    #  L'ANNEAU. Un tore écrasé sur Z : un tore brut a une section ronde, un
    #  anneau de clé est plat.
    bpy.ops.mesh.primitive_torus_add(major_radius=ANNEAU_R,
                                     minor_radius=ANNEAU_T,
                                     major_segments=64, minor_segments=16)
    an = bpy.context.object
    an.name = nom + "_anneau"
    an.scale = (1.0, 1.0, demi / ANNEAU_T)
    bpy.ops.object.transform_apply(scale=True)
    an.data.materials.append(mat)
    an.parent = pivot

    #  LE COLLET, entre l'anneau et la tige : sans lui la tige a l'air posée
    #  contre l'anneau au lieu d'en sortir.
    x0 = ANNEAU_R + ANNEAU_T * 0.4
    boite(nom + "_collet", x0 - 0.0030, x0 + 0.0042, -0.0044, 0.0044,
          -demi, demi, mat, pivot)

    #  LA TIGE, ronde, jusqu'au panneton.
    tige = 0.0155
    bpy.ops.mesh.primitive_cylinder_add(radius=0.0021, depth=tige,
                                        vertices=32)
    ti = bpy.context.object
    ti.name = nom + "_tige"
    ti.rotation_euler = (0.0, math.radians(90.0), 0.0)
    ti.location = (x0 + 0.0042 + tige / 2, 0.0, 0.0)
    ti.data.materials.append(mat)
    ti.parent = pivot

    #  LE PANNETON. Arête haute commune, arête basse variable : les dents
    #  sortent de la différence, sans une seule découpe.
    x = x0 + 0.0042 + tige
    haut = 0.0021
    for i, (longueur, hauteur) in enumerate(PROFIL):
        boite("%s_dent%d" % (nom, i), x, x + longueur,
              haut - hauteur, haut, -demi, demi, mat, pivot)
        x += longueur
    return pivot


def scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

    plateau_mat = bois()
    laiton = matiere("LAITON", (0.746, 0.552, 0.226), 0.21, metal=1.0)
    acier = matiere("ACIER", (0.560, 0.572, 0.596), 0.30, metal=1.0)

    bpy.ops.mesh.primitive_plane_add(size=1.4)
    plateau = bpy.context.object
    plateau.name = "Plateau"
    plateau.data.materials.append(plateau_mat)

    matieres = {"LAITON": laiton, "ACIER": acier}
    pivots = {}
    for nom, mat, ech, x, y, z, a in CLES:
        pivots[nom] = cle(nom, matieres[mat], ech, x, y, z, a)
    return pivots


def lumiere(nom, taille_x, taille_y, position, cible, energie, couleur):
    d = bpy.data.lights.new(nom, type='AREA')
    d.shape = 'RECTANGLE'
    d.size, d.size_y = taille_x, taille_y
    d.energy = energie
    d.color = couleur
    ob = bpy.data.objects.new(nom, d)
    ob.location = position
    #  Les surfaces lumineuses émettent vers leur -Z local. On les oriente donc
    #  par un suivi de cible, jamais à la main : une rotation devinée envoie la
    #  lumière à côté, et ça ne se voit qu'au rendu.
    ob.rotation_euler = (Vector(cible) - Vector(position)) \
        .to_track_quat('-Z', 'Y').to_euler()
    bpy.context.collection.objects.link(ob)
    return ob


def eclairage():
    #  Petite et pas trop forte : une source large noie tout dans une lumière
    #  d'ambiance, et la clé perd son ombre portée — donc son poids.
    lumiere("FENETRE", 0.20, 0.15, (-0.235, -0.050, 0.300),
            (-0.045, -0.020, 0.004), 4.4, (1.0, 0.962, 0.906))
    #  Un remplissage froid et faible à droite : il détache les clés d'acier du
    #  bois sans éclairer le fond, qui doit rester sombre pour le titre.
    lumiere("APPOINT", 0.50, 0.40, (0.300, 0.130, 0.230),
            (0.055, 0.032, 0.004), 1.1, (0.760, 0.820, 1.0))

    m = bpy.data.worlds.new("MONDE")
    m.use_nodes = True
    m.node_tree.nodes["Background"].inputs[0].default_value = \
        (0.010, 0.011, 0.014, 1.0)
    bpy.context.scene.world = m


def camera(pivots):
    d = bpy.data.cameras.new("CAM")
    d.lens = 42.0
    d.dof.use_dof = True
    d.dof.focus_object = pivots["Domaine"]
    #  f/3,2 : le trio doit être flou, pas illisible. À f/2,2 on ne
    #  reconnaissait plus des clés, et une tache n'est pas une information.
    d.dof.aperture_fstop = 3.2
    ob = bpy.data.objects.new("CAM", d)
    ob.location = (0.004, -0.205, 0.152)
    ob.rotation_euler = (Vector((0.004, 0.004, 0.004)) - ob.location) \
        .to_track_quat('-Z', 'Y').to_euler()
    bpy.context.collection.objects.link(ob)
    bpy.context.scene.camera = ob
    return ob


def verifier_cadrage(pivots):
    """
    Le cadrage voulu, vérifié avant de lancer deux minutes de calcul.

    Coordonnées de vue caméra : (0,0) en bas à gauche, (1,1) en haut à droite.
    """
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.context.scene
    cam = sc.camera
    bpy.context.view_layer.update()

    pos = {}
    for nom, pivot in pivots.items():
        v = world_to_camera_view(sc, cam, pivot.matrix_world.translation)
        pos[nom] = (v.x, v.y)
        print("  %-8s x %.2f  y %.2f" % (nom, v.x, v.y))
        if not (0.04 < v.x < 0.96 and 0.04 < v.y < 0.96):
            raise SystemExit("« %s » sort du cadre" % nom)

    dx, dy = pos["Domaine"]
    if dx > 0.45:
        raise SystemExit("le laiton doit rester dans la moitié gauche "
                         "(x = %.2f)" % dx)
    if dy > 0.50:
        raise SystemExit("le laiton doit rester dans le bas (y = %.2f)" % dy)
    for nom in ("Acier1", "Acier2", "Acier3"):
        if pos[nom][0] < 0.50:
            raise SystemExit("« %s » doit être à droite (x = %.2f)"
                             % (nom, pos[nom][0]))
    haut = max(pos[n][1] for n in pos)
    if haut > 0.70:
        raise SystemExit("le tiers haut doit rester libre pour le titre "
                         "(la clé la plus haute est à y = %.2f)" % haut)

    with open(CADRAGE, "w", encoding="utf-8") as f:
        json.dump(pos, f, indent=2)
    return pos


def reglages():
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_EEVEE_NEXT'
    sc.render.resolution_x, sc.render.resolution_y = RESOLUTION
    sc.render.image_settings.file_format = 'PNG'
    e = sc.eevee
    e.taa_render_samples = ECHANTILLONS
    e.use_raytracing = True
    e.ray_tracing_method = 'SCREEN'
    e.use_shadows = True
    e.shadow_ray_count = 4
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - Medium High Contrast'
    sc.view_settings.exposure = -0.30


def main():
    pivots = scene()
    eclairage()
    camera(pivots)
    verifier_cadrage(pivots)
    #  `--cadrage` monte la scène, vérifie et écrit les positions sans lancer
    #  le calcul. Deux secondes au lieu de plusieurs minutes quand on ne veut
    #  que replacer les libellés du montage.
    if "--cadrage" in sys.argv:
        print("  -> %s" % os.path.basename(CADRAGE))
        return
    reglages()
    bpy.context.scene.render.filepath = SORTIE + ".png"
    bpy.ops.render.render(write_still=True)
    print("  -> %s.png" % os.path.basename(SORTIE))


if __name__ == "__main__":
    main()
