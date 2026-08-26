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

#  UN SECOND POINT DE VUE.
#
#  La première comparaison sert d'ouverture d'article. En redonner une
#  identique plus loin n'apprend rien — pire, ça donne l'impression qu'on
#  n'a qu'une seule image à montrer.
#
#  Celui-ci regarde la pièce DEPUIS la fenêtre, vers le coin le plus
#  éloigné. La source est donc derrière la caméra : il ne reste dans le
#  champ aucune zone directement éclairée pour servir de point de repère
#  rassurant. C'est le cadrage le plus dur pour un moteur — et celui qui
#  montre le mieux ce qu'une sonde apporte.
#
#  Format 4/3 et non 16/9, pour que les deux figures de l'article ne se
#  ressemblent pas au premier coup d'oeil.
VUE2 = "--vue2" in sys.argv
if VUE2:
    RESOLUTION = (1200, 900)

#  Un « --rapide » en argument rend en 800 × 450 et 24 échantillons : c'est
#  ce qui permet de régler l'exposition en une minute au lieu de deux et
#  demie. On ne règle pas une lumière à l'aveugle.
RAPIDE = "--rapide" in sys.argv
#  Diagnostic : coupe la nappe de ciel pour ne garder que le soleil. C'est
#  la seule façon de voir où tombe réellement la flaque.
SANS_CIEL = "--sans-ciel" in sys.argv
#  Le TÉMOIN : la même image, sans Volume probe. C'est la seule preuve
#  vraiment recevable que la sonde travaille — un seuil choisi à la main sur
#  une seule image ne prouve rien du tout.
SANS_SONDE = "--sans-sonde" in sys.argv
#  Diagnostic : force la puissance du monde. Mettre le monde à zéro isole
#  complètement ce que la sonde apporte.
MONDE = (float(sys.argv[sys.argv.index("--monde") + 1])
         if "--monde" in sys.argv else None)

#  LE GIZMO SE REND À PART, ET C'EST LA SEULE FAÇON HONNÊTE DE LE MONTRER.
#
#  Une sonde correctement dimensionnée déborde DERRIÈRE les murs. Son
#  filaire est donc invisible depuis l'intérieur de la pièce — un mur le
#  cache, comme il cacherait n'importe quel objet.
#
#  Or dans Blender, le gizmo n'est pas un objet de la scène : c'est une
#  SURCOUCHE, dessinée par-dessus l'image sans test de profondeur. Le
#  reproduire fidèlement demande donc deux passes — le décor d'un côté, le
#  filaire seul sur fond transparent de l'autre — puis une superposition.
#  Le dessiner « dans » la pièce, rentré de quelques centimètres pour qu'on
#  le voie, reviendrait à montrer une sonde plus petite que la vraie.
GIZMO_SEUL = "--gizmo-seul" in sys.argv

GIZMO = (0.28, 0.88, 0.72)     # le teal des sondes dans Blender
#  Force 1,0 et non 1,9 : la passe gizmo se rend en transformation
#  « Standard », donc sans compression des hautes lumières. À 1,9 le teal
#  écrêtait vers le blanc — 194, 255, 255 relevé sur la passe — et le trait
#  disparaissait sur les murs clairs au moment de la superposition. À 1,0 il
#  sort à sa couleur exacte et contraste partout.
GIZMO_FORCE = 1.0
GIZMO_FIL = 0.016              # épaisseur du filaire, en mètres
#  La transparence est appliquée À LA SUPERPOSITION, pas dans le matériau :
#  la passe doit sortir un trait franc sur fond transparent.
GIZMO_OPACITE = 1.0

#  LE RETRAIT DE LA SONDE — l'erreur qui m'a coûté le plus de rendus.
#
#  J'avais rentré la sonde de 45 cm, uniquement pour que son filaire se
#  détache des angles de la pièce et se lise comme une boîte. Résultat : les
#  six parois se retrouvaient HORS du volume de la sonde. Or hors sonde,
#  EEVEE Next retombe sur l'ambiante du monde — réglée ici à 0,03. Les murs
#  ressortaient donc noirs, et j'ai cherché longtemps du côté de la densité
#  de surfels et de l'albédo des matières avant de regarder la seule chose
#  qui clochait : le volume ne contenait pas ce qu'il devait éclairer.
#
#  Une sonde de volume doit ENGLOBER les surfaces qu'elle éclaire, quitte à
#  déborder légèrement derrière les murs. Jamais s'arrêter avant.
SONDE_RETRAIT = -0.18


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


def boite(nom, centre, taille, mat, biseau=0.0):
    """
    Un pavé, posé par son centre.

    `biseau` casse les arêtes vives. C'est LE réglage qui sépare un meuble
    d'un cube : une arête parfaitement vive n'existe pas dans le réel, elle
    ne renvoie donc aucun liseré de lumière, et l'œil lit « boîte de test ».
    Deux centimètres suffisent — au-delà on voit l'arrondi et ça devient du
    mobilier en mousse.
    """
    bpy.ops.mesh.primitive_cube_add(size=2.0, location=centre)
    ob = bpy.context.object
    ob.name = nom
    ob.scale = tuple(t / 2.0 for t in taille)
    bpy.ops.object.transform_apply(scale=True)
    ob.data.materials.append(mat)
    if biseau > 0.0:
        b = ob.modifiers.new("BISEAU", "BEVEL")
        b.width = biseau
        b.segments = 3
        b.limit_method = "ANGLE"
        bpy.ops.object.shade_auto_smooth()
    return ob


def dalle_b(nom, x0, x1, y0, y1, z0, z1, mat, biseau):
    return boite(nom, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2),
                 (x1 - x0, y1 - y0, z1 - z0), mat, biseau)


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


def meneaux(mat):
    """
    Deux traverses dans l'ouverture. Sans elles, la fenêtre est un
    rectangle blanc : rien n'indique l'échelle, et la source la plus
    importante de l'image n'a aucune lecture.
    """
    ym = (F_Y0 + F_Y1) / 2
    zm = (F_Z0 + F_Z1) / 2
    dalle("MENEAU_V", X0 - 0.07, X0 - 0.02, ym - 0.028, ym + 0.028,
          F_Z0, F_Z1, mat)
    dalle("MENEAU_H", X0 - 0.07, X0 - 0.02, F_Y0, F_Y1,
          zm - 0.028, zm + 0.028, mat)
    #  Le dormant, tout autour
    for a, b, c, d in ((F_Y0 - 0.06, F_Y0, F_Z0 - 0.06, F_Z1 + 0.06),
                       (F_Y1, F_Y1 + 0.06, F_Z0 - 0.06, F_Z1 + 0.06),
                       (F_Y0, F_Y1, F_Z0 - 0.06, F_Z0),
                       (F_Y0, F_Y1, F_Z1, F_Z1 + 0.06)):
        dalle("DORMANT", X0 - 0.09, X0 - 0.02, a, b, c, d, mat)


def mobilier(bois, tissu, tapis, sombre, terre, noir):
    """
    IMPLANTATION.

    Premier essai : canapé contre le mur de droite, c'est-à-dire juste à
    côté de la caméra — il sortait du cadre et se lisait comme une masse
    grise. Le mobilier est donc reporté vers le FOND, de sorte que le
    regard traverse la pièce au lieu de buter dessus.
    """
    #  Le tapis : il rattrape une partie de la flaque et la renvoie vers le
    #  plafond. Sans lui la pièce est nettement plus sourde.
    dalle("TAPIS", -1.55, 1.85, 0.15, 3.25, 0.001, 0.016, tapis)

    #  Le canapé, contre le mur du fond, face à la caméra
    dalle_b("CANAPE", -1.05, 1.45, 2.55, 3.42, 0.0, 0.46, tissu, 0.035)
    dalle_b("CANAPE_DOS", -1.05, 1.45, 3.22, 3.44, 0.46, 0.95, tissu, 0.030)
    dalle_b("CANAPE_ACC1", -1.10, -0.88, 2.55, 3.44, 0.46, 0.70, tissu, 0.028)
    dalle_b("CANAPE_ACC2", 1.28, 1.50, 2.55, 3.44, 0.46, 0.70, tissu, 0.028)
    for x in (-0.62, 0.32):
        dalle_b("COUSSIN", x - 0.24, x + 0.24, 3.02, 3.24, 0.46, 0.86,
                tapis, 0.045)

    #  La table basse, devant le canapé
    dalle_b("TABLE", -0.62, 0.72, 1.35, 2.20, 0.39, 0.435, bois, 0.012)
    for x in (-0.54, 0.64):
        for y in (1.44, 2.11):
            dalle_b("PIED", x - 0.032, x + 0.032, y - 0.032, y + 0.032,
                    0.0, 0.39, bois, 0.008)

    #  LE POINT DE CONTRÔLE : la bibliothèque du coin le plus éloigné de la
    #  fenêtre. Aucun rayon direct ne l'atteint. Si elle est noire, la sonde
    #  n'a pas travaillé ; si on y lit encore la matière, elle a travaillé.
    #  Une bibliothèque OUVERTE, pas un caisson plein.
    #
    #  Un caisson plein posé dans l'ombre est une dalle noire : on ne peut
    #  rien y lire, donc il ne prouve rien. Une bibliothèque ouverte, si :
    #  le fond des rayonnages est l'endroit le plus mal éclairé de toute la
    #  pièce, et c'est précisément là qu'on va vérifier s'il reste de la
    #  matière. Si les casiers sont bouchés, la sonde n'a pas travaillé.
    XA, XB = 2.14, 2.94
    YA, YB = 2.46, 3.34
    for x0, x1 in ((XA, XA + 0.055), (XB - 0.055, XB)):          # les joues
        dalle_b("BIB_JOUE", x0, x1, YA, YB, 0.0, 2.08, sombre, 0.010)
    dalle("BIB_FOND", XA, XB, YB - 0.04, YB, 0.0, 2.08, sombre)
    dalle_b("BIB_TOP", XA, XB, YA, YB, 2.02, 2.08, sombre, 0.010)
    dalle("BIB_BAS", XA, XB, YA, YB - 0.04, 0.0, 0.09, sombre)
    for z in (0.52, 1.02, 1.52):
        dalle("BIB_TAB", XA + 0.055, XB - 0.055, YA, YB - 0.04,
              z, z + 0.035, sombre)

    #  Quelques livres : de la couleur DANS le coin sombre. C'est le test le
    #  plus sévère pour une sonde — une teinte doit y rester une teinte.
    livres = ((0.42, 0.14, 0.11), (0.16, 0.26, 0.36), (0.55, 0.42, 0.16),
              (0.20, 0.32, 0.22), (0.38, 0.20, 0.30))
    for i, z in enumerate((0.09, 0.555, 1.055)):
        x = XA + 0.075
        for j in range(6 - i):
            c = livres[(i * 3 + j) % len(livres)]
            e = 0.048 + 0.018 * ((i + j) % 3)
            dalle("LIVRE", x, x + e, YB - 0.30, YB - 0.06,
                  z, z + 0.26 + 0.03 * ((i + j) % 2),
                  couleur("LIVRE_%d_%d" % (i, j), c, 0.68))
            x += e + 0.012

    #  Le fauteuil est posé JUSTE À CÔTÉ de la flaque, pas dedans : il prend
    #  le rasant du sol éclairé sur son flanc, ce qui donne l'échelle des
    #  valeurs — du direct au rebond — sans venir couper la flaque, qui est
    #  le seul élément vraiment contrasté de l'image.
    dalle_b("FAUTEUIL", -2.20, -1.28, -0.25, 0.78, 0.0, 0.44, tissu, 0.040)
    dalle_b("FAUTEUIL_DOS", -2.20, -1.96, -0.25, 0.78, 0.44, 0.95, tissu,
            0.035)

    #  Le vase, seule forme ronde de la scène — les ombres douces d'un
    #  cylindre se lisent mieux que celles d'un cube.
    bpy.ops.mesh.primitive_cylinder_add(radius=0.082, depth=0.34,
                                        vertices=64,
                                        location=(0.24, 1.78, 0.605))
    v = bpy.context.object
    v.name = "VASE"
    v.data.materials.append(terre)
    bpy.ops.object.shade_smooth()

    #  Deux cadres sur le mur du fond, AU-DESSUS du dossier du canapé
    for i, (xx, zz) in enumerate(((-0.55, 1.88), (0.62, 1.74))):
        dalle_b("CADRE_%d" % i, xx - 0.34, xx + 0.34, Y1 - 0.045, Y1 - 0.005,
                zz - 0.26, zz + 0.26, noir, 0.010)


def eclairage():
    """
    UNE SEULE OUVERTURE, deux composantes — comme dans la réalité.

    Une vraie fenêtre laisse entrer DEUX choses : le disque solaire, qui
    dessine une flaque nette au sol, et la voûte du ciel, qui donne une
    nappe douce. Les confondre en une seule grande surface lumineuse était
    mon erreur du premier rendu : on obtient une pièce parfaitement plate,
    sans direction, sans flaque, et donc sans rien à démontrer. Toute la
    pièce baignait dans la même valeur et le meuble du fond, qui est le
    point de contrôle, ressortait en gris moyen.

    Les deux composantes passent par la MÊME ouverture. Ce n'est pas une
    lampe d'appoint ajoutée pour tricher : c'est la décomposition physique
    d'une fenêtre.
    """
    #  1. LE SOLEIL — il entre en biais et pose la flaque sur le sol.
    sd = bpy.data.lights.new("SOLEIL", type="SUN")
    #  14 et non 9,5 : mesuré sur le rendu, à 9,5 la flaque existait mais
    #  la nappe de ciel la noyait — le sol allait de 60 à 161, un rapport de
    #  2,7 seulement, ce qui se lit comme un dégradé et pas comme une flaque.
    sd.energy = 22.0
    sd.angle = math.radians(1.8)        # pénombre douce des bords de flaque
    sd.color = (1.0, 0.955, 0.885)
    so = bpy.data.objects.new("SOLEIL", sd)
    bpy.context.collection.objects.link(so)
    #  Une lampe SUN éclaire dans la direction de son -Z local. Une rotation
    #  de -52° autour de Y envoie ce -Z vers (sin 52, 0, -cos 52), donc vers
    #  l'intérieur et vers le bas ; la rotation en Z l'oriente vers le fond.
    so.rotation_euler = (0.0, math.radians(-52), math.radians(28))
    import mathutils
    #  matrix_world est en cache : sans cette mise à jour on relit la
    #  matrice d'avant la rotation, et le diagnostic annonce un soleil à la
    #  verticale alors qu'il est correctement orienté au rendu.
    bpy.context.view_layer.update()
    d = (so.matrix_world.to_quaternion()
         @ mathutils.Vector((0.0, 0.0, -1.0)))
    #  Où la flaque tombe-t-elle ? On suit le rayon depuis le centre de
    #  l'ouverture jusqu'au sol. Deviner ça à l'œil coûte un rendu par essai.
    cy, cz = (F_Y0 + F_Y1) / 2, (F_Z0 + F_Z1) / 2
    t = cz / -d.z if d.z < 0 else 0.0
    print("  soleil : direction (%.3f, %.3f, %.3f) — flaque vers "
          "x=%.2f  y=%.2f" % (d.x, d.y, d.z, X0 + d.x * t, cy + d.y * t))

    #  2. LE CIEL — la nappe douce, par la même ouverture.
    ld = bpy.data.lights.new("CIEL_FENETRE", type="AREA")
    ld.shape = "RECTANGLE"
    ld.size = F_Z1 - F_Z0
    ld.size_y = F_Y1 - F_Y0
    ld.energy = 0.0 if SANS_CIEL else 1500.0
    ld.color = (0.86, 0.92, 1.0)        # une nappe de ciel est FROIDE
    ob = bpy.data.objects.new("CIEL_FENETRE", ld)
    bpy.context.collection.objects.link(ob)
    ob.location = (X0 - 0.10, (F_Y0 + F_Y1) / 2, (F_Z0 + F_Z1) / 2)
    #  Une surface émet vers son -Z local : une rotation de -90° autour de Y
    #  envoie ce -Z vers le +X du monde, donc vers l'intérieur de la pièce.
    ob.rotation_euler = (0.0, math.radians(-90), 0.0)

    #  3. LE PANNEAU DE CIEL — ce qu'on VOIT par la fenêtre.
    #
    #  Sous EEVEE, une surface émissive n'éclaire PAS la scène par elle-même :
    #  elle ne contribue à l'éclairage qu'à travers une sonde. Ce panneau ne
    #  sert donc qu'à donner au carreau une vraie valeur de ciel, sans
    #  déverser d'ambiante parasite dans la pièce.
    m = bpy.data.materials.new("CIEL_PANNEAU")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (0.42, 0.56, 0.80, 1.0)
    em.inputs["Strength"].default_value = 5.5
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    pan = dalle("PANNEAU_CIEL", X0 - 3.2, X0 - 3.1, -7.0, 7.0, -2.0, 7.0, m)
    #  IL NE DOIT PAS PORTER D'OMBRE. Posé entre le soleil et la fenêtre, un
    #  panneau opaque intercepte le rayonnement direct : la flaque au sol
    #  disparaît purement et simplement, et on cherche longtemps pourquoi la
    #  pièce est devenue terne.
    pan.visible_shadow = False

    monde = bpy.data.worlds.new("CIEL")
    monde.use_nodes = True
    fond = monde.node_tree.nodes["Background"]
    fond.inputs["Color"].default_value = (0.38, 0.52, 0.76, 1.0)
    #  LE MONDE À 0,03, ET C'EST TOUT LE SUJET.
    #
    #  Sous EEVEE Next, le monde sert d'ambiante DE REPLI partout où aucune
    #  sonde ne couvre le point — y compris à l'intérieur d'une pièce fermée,
    #  là où le ciel n'a physiquement aucune vue. À 0,40, il éclairait donc
    #  tout l'intérieur tout seul, et la sonde ne changeait plus rien :
    #  mesuré, le coin le plus sombre gagnait ×1,03 avec elle.
    #
    #  Le même relevé, monde coupé : ×36,7. La sonde travaillait depuis le
    #  début, elle était noyée. On garde donc juste ce qu'il faut pour que le
    #  repli ne soit pas du noir pur, et la lumière de la pièce entre par la
    #  fenêtre — comme l'annonce la légende de l'image.
    force = 0.02 if SANS_CIEL else 0.03
    fond.inputs["Strength"].default_value = force if MONDE is None else MONDE
    bpy.context.scene.world = monde


def camera():
    cd = bpy.data.cameras.new("CAM")
    #  30 mm sur la seconde vue : le 24 mm creuse trop la diagonale de la
    #  pièce et éloigne le coin de contrôle jusqu'à le rendre minuscule.
    cd.lens = 30.0 if VUE2 else 24.0
    cd.clip_start = 0.05
    cam = bpy.data.objects.new("CAM", cd)
    bpy.context.collection.objects.link(cam)
    cam.location = (-2.35, -2.62, 1.58) if VUE2 else (2.05, -3.22, 1.44)

    #  On VISE par contrainte, jamais en calculant des angles d'Euler à la
    #  main : le calcul manuel introduit toujours un roulis, et un intérieur
    #  dont les verticales penchent est immédiatement faux à l'œil.
    cible = bpy.data.objects.new("CIBLE", None)
    bpy.context.collection.objects.link(cible)
    #  Visée basse : à 24 mm sous un plafond de trois mètres, une visée à
    #  hauteur d'œil remplit le tiers supérieur de l'image de plafond vide.
    cible.location = (1.30, 3.05, 1.00) if VUE2 else (-0.45, 1.90, 0.82)
    c = cam.constraints.new("TRACK_TO")
    c.target = cible
    c.track_axis = "TRACK_NEGATIVE_Z"
    c.up_axis = "UP_Y"
    bpy.context.scene.camera = cam
    return cam


def sonde():
    """
    Le Volume probe. Il tient toute la pièce et DÉBORDE derrière les parois —
    `SONDE_RETRAIT` est négatif, c'est donc un dépassement, pas un retrait.

    Ce commentaire disait l'inverse jusqu'ici : « très légèrement en retrait
    des murs », par crainte d'échantillons capturés dans l'épaisseur de la
    cloison. C'est exactement l'erreur que la mesure a démentie. Une sonde
    rentrée de 45 cm laissait les six parois HORS du volume, donc sans
    irradiance, donc noires : moyenne d'image 86,5 contre 129,9 une fois la
    sonde ressortie derrière les murs. Un mur n'est éclairé que s'il est
    dedans.
    """
    bpy.ops.object.lightprobe_add(type="VOLUME",
                                  location=((X0 + X1) / 2, (Y0 + Y1) / 2,
                                            (Z0 + Z1) / 2))
    ob = bpy.context.object
    ob.name = "VOLUME_PROBE"
    ob.scale = ((X1 - X0) / 2 - SONDE_RETRAIT, (Y1 - Y0) / 2 - SONDE_RETRAIT,
                (Z1 - Z0) / 2 - SONDE_RETRAIT)
    d = ob.data
    d.resolution_x, d.resolution_y, d.resolution_z = 11, 12, 6
    d.bake_samples = 1024
    d.capture_world = True              # le ciel entre par l'ouverture
    d.capture_indirect = True           # les rebonds successifs
    #  True : c'est par là que le panneau de ciel entre dans l'irradiance.
    #  Sous EEVEE une surface émissive n'éclaire que via les sondes.
    d.capture_emission = True
    #  LE RÉGLAGE QUI DÉCIDE DE TOUT, ET QUI NE SE VOIT NULLE PART.
    #
    #  La densité de surfels est la finesse du calcul de rebond. À 5, cette
    #  pièce était découpée en 1 048 surfels pour une centaine de mètres
    #  carrés de parois — dix par mètre carré. Le rebond obtenu est alors
    #  trop grossier pour éclairer quoi que ce soit : la pièce restait une
    #  caverne, et on croit que c'est la sonde qui ne sert à rien.
    d.surfel_density = 28
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

    #  ÉMISSION PURE ET SEMI-TRANSPARENTE, pas un Principled.
    #
    #  Premier essai : un Principled épais et très émissif. Résultat, des
    #  tubes lumineux qui longent les murs — un lecteur y voit un bandeau
    #  de LED, pas un gizmo. Or un gizmo est un TRAIT D'INTERFACE posé sur
    #  l'image : plat, sans ombrage, et laissant voir le mur derrière.
    m = bpy.data.materials.new("MAT_GIZMO")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*GIZMO, 1.0)
    em.inputs["Strength"].default_value = GIZMO_FORCE
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mx = nt.nodes.new("ShaderNodeMixShader")
    mx.inputs["Fac"].default_value = GIZMO_OPACITE
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(tr.outputs["BSDF"], mx.inputs[1])
    nt.links.new(em.outputs["Emission"], mx.inputs[2])
    nt.links.new(mx.outputs["Shader"], out.inputs["Surface"])
    m.blend_method = "BLEND"
    ob.data.materials.append(m)
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
    #  LE PIÈGE, ET IL EST GROS.
    #
    #  Avec `use_raytracing = True`, EEVEE Next calcule l'indirect diffus par
    #  lancer de rayons en ESPACE ÉCRAN. Dans une pièce entièrement visible
    #  au cadre, ça suffit à tout éclairer, et le Volume probe ne sert alors
    #  presque à rien.
    #
    #  Mesuré sur cette scène, en rendant deux fois — avec et sans sonde :
    #  le coin le plus sombre gagnait ×1,03, le reste de l'image ×1,00.
    #  Autrement dit, une image légendée « c'est le travail du Volume probe »
    #  aurait montré le travail d'autre chose.
    #
    #  Pour que la démonstration porte sur ce qu'elle annonce, on coupe le
    #  lancer de rayons et l'approximation « Fast GI ». Il ne reste alors
    #  qu'une seule source d'indirect : la sonde.
    e.use_raytracing = False
    e.use_fast_gi = False
    e.use_shadows = True
    #  La fenêtre est une source ÉTENDUE vue de très près : ses ombres sont
    #  échantillonnées au hasard, et à trois rayons par point le grain sur
    #  les murs rasants était intenable. Six rayons le font disparaître pour
    #  environ un tiers de temps de rendu en plus.
    e.shadow_ray_count = 6
    e.shadow_step_count = 8
    e.gi_diffuse_bounces = 4
    e.gi_irradiance_pool_size = "32"
    sc.render.resolution_x, sc.render.resolution_y = RESOLUTION
    sc.render.resolution_percentage = 50 if RAPIDE else 100
    if RAPIDE:
        e.taa_render_samples = 24
    sc.render.image_settings.file_format = "PNG"
    #  AgX, et non « Standard » : ici on rend une PHOTOGRAPHIE d'intérieur,
    #  pas une capture d'écran. Les hautes lumières de la fenêtre doivent
    #  rouler proprement au lieu de se couper net.
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Base Contrast"
    #  On éclaire fort et on redescend à l'exposition, plutôt que d'éclairer
    #  juste : plus de lumière dans la scène, c'est plus de rebond à capter
    #  pour la sonde, donc un fond de pièce qui tient debout.
    sc.view_settings.exposure = -0.30


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)

    #  UNE PALETTE CLAIRE, ET CE N'EST PAS UNE QUESTION DE GOÛT.
    #
    #  Chaque rebond multiplie la lumière par l'albédo de la surface. Avec un
    #  sol à 0,30 et un canapé à 0,20, le deuxième rebond ne vaut déjà plus
    #  rien et la pièce reste une caverne quoi qu'on fasse à la sonde. En
    #  montant les matières autour de 0,50-0,60, le même éclairage donne un
    #  intérieur qui respire — et la sonde a enfin quelque chose à porter.
    #
    #  La bibliothèque, elle, reste sombre : c'est le point de contrôle.
    mur = couleur("MUR", (0.868, 0.845, 0.802), 0.88)
    plafond = couleur("PLAFOND", (0.912, 0.900, 0.878), 0.92)
    sol = couleur("SOL_CHENE", (0.605, 0.468, 0.322), 0.38)
    bois = couleur("NOYER", (0.262, 0.170, 0.098), 0.36)
    tissu = couleur("TISSU", (0.425, 0.462, 0.505), 0.86)
    tapis = couleur("TAPIS", (0.520, 0.530, 0.472), 0.95)
    sombre = couleur("MEUBLE", (0.145, 0.138, 0.128), 0.55)
    terre = couleur("TERRE", (0.520, 0.238, 0.122), 0.48)
    noir = couleur("CADRE", (0.055, 0.052, 0.050), 0.40)

    piece(mur, plafond, sol)
    meneaux(noir)
    mobilier(bois, tissu, tapis, sombre, terre, noir)
    eclairage()
    camera()
    reglages()
    p = sonde()

    #  La seconde vue porte son propre suffixe : sans quoi elle écraserait
    #  les rendus de la première, qui servent encore à l'ouverture.
    suffixe = "-vue2" if VUE2 else ""
    if SANS_SONDE:
        bpy.data.objects.remove(p, do_unlink=True)
        suffixe += "-sans-sonde"
        print("  TÉMOIN : sonde retirée, aucune cuisson")
    else:
        print("  cuisson du Volume probe (%d × %d × %d, %d échantillons)…"
              % (p.data.resolution_x, p.data.resolution_y,
                 p.data.resolution_z, p.data.bake_samples))
        bpy.context.view_layer.objects.active = p
        bpy.ops.object.lightprobe_cache_bake(subset="ACTIVE")
        print("  cuisson terminée")

    sc = bpy.context.scene
    if GIZMO_SEUL:
        fil = filaire_du_gizmo(p)       # APRÈS la cuisson, jamais avant
        for ob in bpy.data.objects:
            if ob.type in ("MESH", "LIGHT") and ob is not fil:
                ob.hide_render = True
        sc.render.film_transparent = True
        sc.render.image_settings.color_mode = "RGBA"
        sc.view_settings.view_transform = "Standard"
        sc.view_settings.exposure = 0.0
        suffixe += "-gizmo"
        print("  passe GIZMO : filaire seul, fond transparent")

    sc.render.filepath = SORTIE + suffixe + ".png"
    bpy.ops.render.render(write_still=True)
    print("  rendu : %s%s.png" % (SORTIE, suffixe))


main()
