"""
IMAGE 5 de l'article « Light probes Blender » — la sonde Plane.

    python3 article/plane_probe_reflexions.py                # avec la sonde
    python3 article/plane_probe_reflexions.py --sans-plane   # sans

Produit `article/light-probe-plane-sol-reflechissant[-sans-plane].png`.

----------------------------------------------------------------------------
CE QUE L'IMAGE DOIT PROUVER
----------------------------------------------------------------------------
Les réflexions en espace écran ne peuvent réfléchir que ce qui est DÉJÀ à
l'écran. Un objet hors cadre n'a aucun pixel à aller chercher : le rayon sort
de l'image et retombe sur le monde, c'est-à-dire sur rien. La sonde Plane, à
l'inverse, rend une seconde fois la scène depuis le point de vue miroir : ce
qui est hors champ y est, puisque ce n'est pas le même champ.

D'où la mise en scène : un panneau ambre suspendu HORS DU CADRE, au-dessus du
bord haut, dont le reflet tombe, lui, EN PLEIN DANS le cadre.

----------------------------------------------------------------------------
LA GÉOMÉTRIE N'EST PAS LIBRE — ELLE EST CONTRAINTE, ET J'AI FAILLI ME PLANTER
----------------------------------------------------------------------------
Premier réflexe : caméra horizontale, objet au-dessus du bord haut. Ça ne
peut PAS marcher, et c'est démontrable en trois lignes.

Caméra à la hauteur h, objet à la hauteur H, à la distance horizontale D.

  - l'objet est vu à l'angle           A = atan((H − h) / D)  au-dessus de l'axe
  - son reflet au sol est vu à         B = atan((H + h) / D)  en dessous

B > A toujours, puisque H + h > H − h. Avec une caméra horizontale, le cadre
est symétrique : si l'objet sort par le haut (A > demi-champ), alors B aussi
et le reflet sort par le bas. On ne montre rien.

Il faut donc PENCHER la caméra vers le bas d'un angle β, ce qui rend le cadre
asymétrique par rapport à l'horizon : il monte de φ − β au-dessus, descend de
φ + β en dessous. Les deux conditions deviennent

        A > φ − β        (l'objet sort par le haut)
        B < φ + β        (le reflet reste dans le cadre)

et elles sont compatibles. Les valeurs ci-dessous les vérifient avec de la
marge, et `verifier_cadrage()` le RECONTRÔLE à la fin sur la vraie caméra, en
projetant les huit coins — celui du panneau et celui de son image miroir.
Une géométrie juste sur le papier et fausse dans le fichier, ça s'est déjà vu.

----------------------------------------------------------------------------
CE QUI CHANGE ENTRE LES DEUX RENDUS : LA SONDE, ET RIEN D'AUTRE
----------------------------------------------------------------------------
Le lancer de rayons est ACTIVÉ dans les deux images. C'est important : sans
lui, EEVEE Next n'irait chercher les réflexions que dans les sondes Sphere et
il n'y aurait pas d'espace écran à prendre en défaut. On compare donc bien
« espace écran seul » à « espace écran + Plane », pas « rien » à « quelque
chose ».

La lampe de remplissage est réglée à `specular_factor = 0`. Sans ça elle
poserait sur le sol poli sa propre tache spéculaire — un reflet analytique,
présent dans les deux images, qui viendrait brouiller le seul reflet dont
l'image parle.
"""

import math
import os
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view

RACINE = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(RACINE, "light-probe-plane-sol-reflechissant")

SANS_PLANE = "--sans-plane" in sys.argv
RAPIDE = "--rapide" in sys.argv

#  UNE TROISIÈME PASSE, QUI N'IRA PAS DANS LA FIGURE PRINCIPALE.
#  Le sujet de l'image est un objet qu'on ne voit pas. Le lecteur doit donc
#  pouvoir vérifier qu'il existe, sinon on lui demande de croire sur parole.
#  `--large` refait exactement le même plan à 14 mm : le panneau y entre, et
#  son reflet aussi. Ça devient la vignette de contrôle du montage.
LARGE = "--large" in sys.argv

RESOLUTION = (1400, 1050)            # 4/3
ECHANTILLONS = 24 if RAPIDE else 160

# ---------------------------------------------------------------------------
#  LA GÉOMÉTRIE, EN MÈTRES — les valeurs résolues plus haut
# ---------------------------------------------------------------------------
CAM_Y = -6.00
CAM_Z = 0.60                          # h — caméra basse : incidence rasante,
                                      # donc réflexion forte (Fresnel)
TANGAGE = 14.0                        # β, vers le bas
FOCALE = 12.0 if LARGE else 24.0      # φ = atan(13.5 / 24) = 29,4°

PAN_D = 7.00                          # D — distance horizontale du panneau
PAN_Z = 3.70                          # H
PAN_L, PAN_H = 3.20, 1.20             # taille du panneau
PAN_Y = CAM_Y + PAN_D

#  LE SOL DOIT ÊTRE UN VRAI MIROIR, ET CE N'EST PAS UN CAPRICE D'IMAGE.
#  Premier essai : diélectrique sombre, rugosité 0,055, couleur de base 0,02.
#  C'est un beau sol ciré — et il renvoie 4 % de ce qu'il reçoit. Sur le rendu,
#  la zone du reflet mesurait 9/255 avec la sonde contre 11 sans : l'effet
#  existait, personne ne pouvait le voir. Une figure qui démontre quelque
#  chose d'invisible ne démontre rien.
#  Deuxième essai : métal, mais à 0,20 de couleur de base. Un miroir qui ne
#  renvoie que 20 % reste un miroir sombre : 19,6/255 contre 22,3, toujours
#  rien à voir. Un test à part l'a tranché — même scène, sol à 0,80 : le sol
#  sous l'objet passe de 23 à 120 dès que le lancer de rayons est actif. Le
#  mécanisme marchait depuis le début, c'est la surface qui l'éteignait.
SOL_METAL = 1.00
SOL_BASE = (0.760, 0.762, 0.780)
SOL_R = 0.070


def materiau(nom, base, rugosite, metal=0.0, emission=None, force=0.0):
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


def bloc(nom, centre, taille, mat):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=centre)
    ob = bpy.context.object
    ob.name = nom
    ob.scale = taille
    ob.data.materials.append(mat)
    return ob


def scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

    sol = materiau("Sol", SOL_BASE, SOL_R, metal=SOL_METAL)
    mur = materiau("Mur", (0.095, 0.095, 0.102), 0.85)
    ambre = materiau("Ambre", (0.0, 0.0, 0.0), 0.5,
                     emission=(1.00, 0.42, 0.13), force=7.0)
    blanc = materiau("Blanc", (0.62, 0.62, 0.60), 0.42)
    vert = materiau("Vert", (0.10, 0.40, 0.34), 0.35)
    terre = materiau("Terre", (0.42, 0.20, 0.13), 0.45)

    #  LE SOL. Assez grand pour que le bord ne rentre jamais dans le cadre :
    #  un reflet qui s'arrête sur une arête de plan se lit comme un bug.
    bpy.ops.mesh.primitive_plane_add(size=60.0, location=(0, 0, 0))
    bpy.context.object.name = "Sol"
    bpy.context.object.data.materials.append(sol)

    #  Un fond, pour que la scène ne flotte pas dans le noir. Dimensionné
    #  pour la passe LARGE, pas pour le cadrage principal : à 26 × 6 il
    #  couvrait le cadre à 24 mm mais laissait, à 12 mm, quatre coins de vide
    #  noir qui donnaient à la vignette de contrôle l'air d'un rendu raté.
    bloc("Fond", (0, 8.4, 8.0), (74.0, 0.2, 16.0), mur)

    #  LES TÉMOINS. Ils sont DANS le cadre : leurs reflets doivent être
    #  identiques dans les deux images. C'est ce qui prouve que l'espace
    #  écran fonctionne, et que la différence ne vient pas d'un réglage.
    bloc("Temoin1", (-2.35, 1.10, 0.70), (0.62, 0.62, 1.40), blanc)
    bloc("Temoin2", (0.15, 2.60, 0.50), (0.55, 0.55, 1.00), vert)
    bloc("Temoin3", (2.55, 0.55, 0.85), (0.70, 0.70, 1.70), terre)

    #  LE PANNEAU HORS CHAMP.
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0.0, PAN_Y, PAN_Z))
    p = bpy.context.object
    p.name = "PanneauHorsChamp"
    p.rotation_euler = (math.radians(90.0), 0.0, 0.0)   # face à la caméra
    p.scale = (PAN_L, PAN_H, 1.0)
    p.data.materials.append(ambre)

    #  L'ÉCLAIRAGE. Le panneau est émissif, mais dans EEVEE une émission de
    #  maillage n'éclaire personne : elle se voit, elle ne rayonne pas. La
    #  lumière vient donc d'une lampe séparée — sans spéculaire, voir l'en-tête.
    ld = bpy.data.lights.new("Remplissage", type='AREA')
    ld.shape = 'RECTANGLE'
    ld.size, ld.size_y = 9.0, 7.0
    ld.energy = 1400.0
    ld.color = (1.0, 0.93, 0.86)
    ld.specular_factor = 0.0
    lo = bpy.data.objects.new("Remplissage", ld)
    lo.location = (-1.2, 1.0, 5.2)
    lo.rotation_euler = (math.radians(12.0), 0.0, 0.0)
    bpy.context.collection.objects.link(lo)

    #  Un monde presque noir : quand le rayon d'espace écran sort de l'image,
    #  c'est LUI qu'EEVEE renvoie. S'il était clair, l'échec de l'espace écran
    #  ressemblerait à un reflet flou plutôt qu'à une absence.
    w = bpy.data.worlds.new("Monde")
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = \
        (0.012, 0.013, 0.016, 1.0)
    bpy.context.scene.world = w
    return p


def camera():
    cd = bpy.data.cameras.new("Camera")
    cd.lens = FOCALE
    cd.sensor_fit = 'AUTO'
    ob = bpy.data.objects.new("Camera", cd)
    ob.location = (0.0, CAM_Y, CAM_Z)
    ob.rotation_euler = (math.radians(90.0 - TANGAGE), 0.0, 0.0)
    bpy.context.collection.objects.link(ob)
    bpy.context.scene.camera = ob
    return ob


def sonde_plane():
    """
    La sonde Plane. Rien à cuire : contrairement à Sphere et Volume, une
    Plane est recalculée à chaque image — c'est un second rendu de la scène,
    vu depuis le miroir. C'est ce qui la rend chère, et exacte.
    """
    d = bpy.data.lightprobes.new("SondePlane", type='PLANE')
    d.influence_distance = 0.30       # le sol est à z = 0, la sonde à ~0 :
                                      # 0,30 laisse de la marge sans déborder
                                      # sur les blocs, qui ne sont pas plans
    #  ON NE TOUCHE PAS À `clip_start`. C'est ce qui m'a coûté le plus de
    #  temps ici : je l'avais mis à 0,01, une valeur d'apparence anodine —
    #  dix fois le défaut, un centimètre. Sur la même scène, la réflexion
    #  sous l'objet tombe de 186,7 à 20,3 sur 255. La capture ne rend plus
    #  que le monde ; toute la géométrie disparaît, donc le reflet aussi.
    #  Symptôme trompeur : la sonde ne se contente pas de ne rien ajouter,
    #  elle REMPLACE le reflet en espace écran par du vide. Ajouter la sonde
    #  rendait l'image PIRE que sans elle, ce qui envoie chercher l'erreur
    #  partout sauf au bon endroit.
    ob = bpy.data.objects.new("SondePlane", d)
    ob.location = (0.0, -1.0, 0.002)  # juste au-dessus du sol
    ob.scale = (16.0, 16.0, 1.0)      # l'étendue couverte, en X/Y locaux
    bpy.context.collection.objects.link(ob)
    return ob


def reglages():
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_EEVEE_NEXT'
    sc.render.resolution_x, sc.render.resolution_y = RESOLUTION
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = 'PNG'

    e = sc.eevee
    e.taa_render_samples = ECHANTILLONS
    #  ACTIVÉ DANS LES DEUX PASSES. Sans lancer de rayons, il n'y a pas
    #  d'espace écran à mettre en défaut, et l'image ne démontre rien.
    e.use_raytracing = True
    e.ray_tracing_method = 'SCREEN'
    e.use_fast_gi = False
    rt = e.ray_tracing_options
    rt.resolution_scale = '1'         # pleine résolution : à moitié, le bord
                                      # du reflet bave et on ne sait plus si
                                      # ce qu'on voit est l'effet ou le bruit
    rt.trace_max_roughness = 1.0
    rt.screen_trace_quality = 0.5
    rt.screen_trace_thickness = 0.2

    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - Punchy'


def verifier_cadrage(cam, panneau):
    """
    La preuve, faite sur la caméra réelle et pas sur mes calculs : les quatre
    coins du panneau doivent tomber HORS du cadre, les quatre coins de son
    image miroir DEDANS. Si l'une des deux conditions tombe, l'image ne
    démontre rien et il vaut mieux le savoir avant vingt minutes de rendu.
    """
    dg = bpy.context.evaluated_depsgraph_get()
    sc = bpy.context.scene
    coins = [panneau.matrix_world @ v.co for v in panneau.data.vertices]
    miroir = [c.copy() for c in coins]
    for m in miroir:
        m.z = -m.z                     # le sol est le plan z = 0

    def uv(pts):
        return [world_to_camera_view(sc, cam, p) for p in pts]

    a, b = uv(coins), uv(miroir)
    dehors = all(not (0.0 <= p.x <= 1.0 and 0.0 <= p.y <= 1.0) for p in a)
    dedans = all(0.02 <= p.x <= 0.98 and 0.02 <= p.y <= 0.98 for p in b)

    print("  panneau   : y de %.3f a %.3f   (hors cadre : %s)"
          % (min(p.y for p in a), max(p.y for p in a),
             "oui" if dehors else "NON"))
    print("  son reflet: y de %.3f a %.3f   x de %.3f a %.3f  (dedans : %s)"
          % (min(p.y for p in b), max(p.y for p in b),
             min(p.x for p in b), max(p.x for p in b),
             "oui" if dedans else "NON"))
    if not dehors:
        raise SystemExit("le panneau est DANS le cadre : "
                         "l'espace ecran saurait le refleter, "
                         "l'image ne prouverait rien")
    if not dedans:
        raise SystemExit("le reflet du panneau sort du cadre : "
                         "il n'y a rien a montrer")
    #  La zone du reflet, en fractions d'image, pour la mesurer plus tard.
    #  L'origine de `world_to_camera_view` est EN BAS ; celle d'une image
    #  l'est en haut. D'où le retournement, qui n'est pas une coquetterie :
    #  sans lui on mesure le ciel.
    x0, x1 = min(p.x for p in b), max(p.x for p in b)
    y0, y1 = 1.0 - max(p.y for p in b), 1.0 - min(p.y for p in b)
    print("  ZONE_REFLET = (%.4f, %.4f, %.4f, %.4f)" % (x0, x1, y0, y1))
    return (x0, x1, y0, y1)


def main():
    panneau = scene()
    cam = camera()
    reglages()

    print()
    print("  ---- cadrage ----")
    if LARGE:
        print("  passe large (14 mm) : le panneau est DANS le cadre, "
              "c'est le but")
    else:
        verifier_cadrage(cam, panneau)

    if not SANS_PLANE:
        sonde_plane()
    print("  sonde Plane : %s" % ("ABSENTE" if SANS_PLANE else "presente"))
    print("  lancer de rayons : %s  (%d echantillons)"
          % (bpy.context.scene.eevee.ray_tracing_method, ECHANTILLONS))

    suffixe = ("-large" if LARGE else "") + \
              ("-sans-plane" if SANS_PLANE else "")
    bpy.context.scene.render.filepath = SORTIE + suffixe + ".png"
    bpy.ops.render.render(write_still=True)
    print("  -> %s" % (SORTIE + suffixe + ".png"))


if __name__ == "__main__":
    main()
