"""
Le poste de travail 3D, monté à partir des cinq sources fournies.

    sh article-formation-3d/rendre-poste.sh

----------------------------------------------------------------------------
POURQUOI UNE PIÈCE, ET PAS SEULEMENT UN HDRI
----------------------------------------------------------------------------
Un objet posé dans un HDRI sphérique se voit tout de suite : le fond montre
le lieu du panorama, ici le quai des Zattere à Venise, ce qui n'a aucun
rapport avec un bureau. On construit donc une pièce, et l'HDRI n'est plus vu
que par la fenêtre. La lumière rasante reste la même, le décor devient
crédible, et surtout les reflets de la dalle montrent une baie vitrée, ce
qu'un lecteur reconnaît sans y penser.

----------------------------------------------------------------------------
LES SOURCES SONT DES SCÈNES DE STUDIO, PAS DES OBJETS
----------------------------------------------------------------------------
Le clavier et la souris arrivent avec leur décor de modélisation : un sol de
45 unités, des plans de référence photographiques dressés à la verticale,
des arêtes de construction à deux sommets. Rien de tout ça ne doit entrer
dans la scène.

Le tri ne se fait PAS par nom. `Cube` existe dans le clavier ET dans
l'écran ; à la deuxième bibliothèque chargée, Blender renomme en `Cube.001`
et un filtre par nom laisse passer le décor. Le tri se fait donc sur la
géométrie, qui ne ment pas : un plan de référence est plat et tient en
quatre sommets, un sol de studio dépasse toute dimension plausible.

----------------------------------------------------------------------------
LES ÉCHELLES SONT TOUTES FAUSSES, ET CHACUNE DIFFÉREMMENT
----------------------------------------------------------------------------
Le bureau et le fauteuil sont normalisés à 1 unité, le clavier fait 45
unités, la souris 20. On ne les met donc pas à l'échelle « à l'œil » : pour
chaque meuble on vise UNE cote réelle connue, et le facteur s'en déduit. Les
cotes obtenues sont réimprimées à la fin, et un garde-fou refuse le rendu si
le plateau et l'assise ne tombent pas dans les fourchettes du mobilier réel.
C'est ce contrôle, et non l'œil, qui garantit qu'un lecteur ne verra pas un
fauteuil de poupée devant un bureau de géant.

----------------------------------------------------------------------------
LA DALLE N'EST PAS UNE LAMPE
----------------------------------------------------------------------------
Le matériau d'origine est une pure Emission : l'écran éclaire, mais il ne
reflète rien. Un vrai écran fait les deux, et c'est même le reflet de la
fenêtre qui le rend crédible. On remplace donc l'Emission par un Principled
qui porte l'image en émission ET une couche spéculaire lisse par-dessus.

Deuxième correction : les six matériaux de la coque sont déclarés
`Metallic 1.0` avec une couleur de base quasi noire. Un métal noir absorbe
presque tous ses reflets, ce qui donne un miroir sombre là où il faut du
plastique mat. Seul le pied reste métallique.
"""

import math
import os
import sys

import numpy as np

import bpy
from mathutils import Matrix, Vector

SOURCES = "/w/sources"
SORTIE = "/w/rendus"

#  ---------------------------------------------------------------------------
#  LES COTES RÉELLES VISÉES, EN MÈTRES
#
#  Chaque meuble est mis à l'échelle sur UNE cote connue, jamais sur une
#  impression. Le reste des proportions vient du modèle et n'est pas touché.
#  ---------------------------------------------------------------------------
PLATEAU = 0.740          # hauteur du dessus du bureau, norme du mobilier
FAUTEUIL_HAUT = 0.780    # dossier d'un fauteuil coque à piètement bois
DALLE = 0.800            # largeur de la dalle d'un 34 pouces
CLAVIER = 0.460          # longueur d'un G710+ sans repose-poignets
SOURIS = 0.067           # largeur d'une m510

#  Fourchettes admises. Hors de là, on ne rend pas.
CONTROLES = (
    ("plateau", PLATEAU, 0.70, 0.78),
    ("hauteur du fauteuil", FAUTEUIL_HAUT, 0.72, 0.85),
    ("largeur de la dalle", DALLE, 0.70, 0.90),
    ("longueur du clavier", CLAVIER, 0.40, 0.52),
    ("largeur de la souris", SOURIS, 0.055, 0.080),
)

#  ---------------------------------------------------------------------------
#  LA PIÈCE
#  ---------------------------------------------------------------------------
MUR_X = -1.74            # mur de gauche, celui qui porte la baie
MUR_Y = 1.06             # mur du fond
PLAFOND = 2.85
EPAISSEUR = 0.12

BAIE_Y = (-1.58, 0.52)   # l'ouverture, en profondeur
#  L'appui est sous le plateau, à 0,70 m, et ce n'est pas un détail : un
#  soleil à 3,5 degrés descend de six centimètres par mètre parcouru. Avec
#  un appui à 0,82 m il passait AU-DESSUS du bureau et n'éclairait que le
#  mur. Soixante-dix centimètres, et la lumière vient lécher le plateau.
BAIE_Z = (0.70, 2.40)    # et en hauteur

#  ---------------------------------------------------------------------------
#  L'HDRI
#
#  Mesuré sur le fichier : le soleil est à l'azimut -35,9 degrés depuis +X,
#  et à 3,5 degrés au-dessus de l'horizon. Le noeud Mapping fait tourner le
#  VECTEUR de lecture, donc l'astre apparent tourne en sens inverse : pour
#  amener le soleil à l'azimut visé, on impose Z = azimut_source - azimut_visé.
#  ---------------------------------------------------------------------------
SOLEIL_SOURCE = -35.9
#  200 degrés, et pas 171. À 171 le soleil est plein -X : sa lumière
#  traverse la pièce vers +X et ressort sans rien toucher, puisque ce côté
#  est ouvert. Le premier brouillon était donc uniformément gris, sans une
#  seule tache de soleil. À 200 degrés elle part vers +X ET +Y, et vient
#  frapper le mur du fond, juste derrière l'écran.
SOLEIL_VISE = float(os.environ.get("AZIMUT", "218"))
ROTATION_MONDE = math.radians(SOLEIL_SOURCE - SOLEIL_VISE)

ECHANTILLONS = int(os.environ.get("ECHANTILLONS", "220"))
LARGEUR_RENDU = int(os.environ.get("LARGEUR_RENDU", "1600"))


# ===========================================================================
#  CHARGEMENT
# ===========================================================================

def charger(fichier, seuil=None):
    """Appende les maillages d'une source et jette son décor de studio.

    `seuil` est la plus grande dimension plausible pour l'objet ; au-delà,
    c'est le sol du studio. Le tri ne regarde jamais les noms, qui se font
    renommer dès la deuxième bibliothèque chargée.
    """
    chemin = os.path.join(SOURCES, fichier)
    with bpy.data.libraries.load(chemin) as (source, cible):
        cible.objects = list(source.objects)

    arrives = []
    for o in cible.objects:
        if o is None:
            continue
        if o.type != 'MESH':
            bpy.data.objects.remove(o, do_unlink=True)
            continue
        bpy.context.scene.collection.objects.link(o)
        arrives.append(o)

    #  ON ATTEND LE GRAPHE DE DÉPENDANCES AVANT DE MESURER.
    #
    #  `object.dimensions` est dérivé de la matrice évaluée : juste après
    #  `libraries.load`, il rend (0, 0, 0). Le premier essai a donc gardé le
    #  sol de studio de la souris, vingt unités de côté, puis mis TOUT le
    #  groupe à l'échelle sur lui : la souris est devenue un grain de douze
    #  millimètres, et le contrôle de cote l'a laissée passer puisqu'il
    #  mesurait le sol. Une ligne d'update, et le tri retrouve son sens.
    bpy.context.view_layer.update()

    gardes, jetes = [], []
    for o in arrives:
        d = sorted(o.dimensions)
        if max(d) < 1e-6:
            raise SystemExit(
                "%s : %s mesure zéro, le graphe n'a pas été évalué"
                % (fichier, o.name))
        plat = d[0] < 1e-4 and len(o.data.vertices) <= 4
        trop = seuil is not None and d[2] > seuil
        if plat or trop:
            jetes.append((o.name, tuple(round(v, 2) for v in o.dimensions)))
            bpy.data.objects.remove(o, do_unlink=True)
        else:
            gardes.append(o)

    if not gardes:
        raise SystemExit("%s : plus rien après le tri" % fichier)
    print("  %-14s %3d maillages gardés, %d jetés %s"
          % (fichier, len(gardes), len(jetes), [n for n, _ in jetes][:4]))
    return gardes


def encombrement(objets):
    bpy.context.view_layer.update()
    pts = []
    for o in objets:
        for coin in o.bound_box:
            pts.append(tuple(o.matrix_world @ Vector(coin)))
    a = np.array(pts)
    return a.min(axis=0), a.max(axis=0)


def poser(objets, cote, cible, position, rotation=0.0):
    """Met un groupe à l'échelle sur une cote, l'oriente et le pose.

    `cote` est l'axe qui porte la mesure connue, 'x', 'y', 'z' ou 'max'.
    L'objet est centré en X et Y sur son encombrement, sa base ramenée à
    zéro, puis déplacé en `position`. Seuls les objets sans parent sont
    transformés : leurs enfants suivent.
    """
    bas, haut = encombrement(objets)
    taille = haut - bas
    mesure = {'x': taille[0], 'y': taille[1], 'z': taille[2],
              'max': taille.max()}[cote]
    if mesure < 1e-9:
        raise SystemExit("cote nulle sur %s" % cote)
    k = cible / mesure

    centre = Vector(((bas[0] + haut[0]) / 2, (bas[1] + haut[1]) / 2, bas[2]))
    M = (Matrix.Translation(Vector(position))
         @ Matrix.Rotation(rotation, 4, 'Z')
         @ Matrix.Scale(k, 4)
         @ Matrix.Translation(-centre))
    for o in objets:
        if o.parent is None:
            o.matrix_world = M @ o.matrix_world
    bpy.context.view_layer.update()

    #  LA TAILLE RENDUE EST CELLE DE L'OBJET, PAS DE SA BOÎTE ALIGNÉE.
    #
    #  Après une rotation de 8 degrés, l'encombrement aligné sur les axes
    #  d'une souris de 67 mm de large et 131 mm de long mesure 83 mm : la
    #  diagonale, pas la souris. Un contrôle de cote branché là-dessus
    #  refusait un objet parfaitement à l'échelle. On renvoie donc les
    #  dimensions propres du groupe, prises avant rotation et multipliées
    #  par le facteur, qui ne dépendent pas de l'orientation.
    propre = taille * k
    reel = encombrement(objets)
    print("     échelle %.5f  ->  %.3f x %.3f x %.3f m, base à %.3f"
          % (k, propre[0], propre[1], propre[2], reel[0][2]))
    return k, propre


# ===========================================================================
#  MATIÈRES
# ===========================================================================

def matiere(nom, base, rugosite, metal=0.0):
    m = bpy.data.materials.new(nom)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (base[0], base[1], base[2], 1.0)
    p.inputs["Roughness"].default_value = rugosite
    p.inputs["Metallic"].default_value = metal
    return m


def grain(materiau, echelle, force):
    """Un bruit léger sur la rugosité. Une surface parfaitement uniforme se
    lit comme une image de synthèse ; c'est l'irrégularité qui fait la
    photo."""
    a = materiau.node_tree
    p = a.nodes["Principled BSDF"]
    bruit = a.nodes.new("ShaderNodeTexNoise")
    bruit.inputs["Scale"].default_value = echelle
    bruit.inputs["Detail"].default_value = 6.0
    plage = a.nodes.new("ShaderNodeMapRange")
    plage.inputs["To Min"].default_value = max(
        0.03, p.inputs["Roughness"].default_value - force)
    plage.inputs["To Max"].default_value = min(
        1.0, p.inputs["Roughness"].default_value + force)
    a.links.new(bruit.outputs["Fac"], plage.inputs["Value"])
    a.links.new(plage.outputs["Result"], p.inputs["Roughness"])


def boite(nom, x, y, z, materiau):
    """Un pavé donné par ses intervalles, ce qui évite les erreurs de
    demi-dimensions sur les murs."""
    bpy.ops.mesh.primitive_cube_add(size=2.0)
    o = bpy.context.active_object
    o.name = nom
    o.scale = ((x[1] - x[0]) / 2, (y[1] - y[0]) / 2, (z[1] - z[0]) / 2)
    o.location = ((x[0] + x[1]) / 2, (y[0] + y[1]) / 2, (z[0] + z[1]) / 2)
    o.data.materials.append(materiau)
    return o


def construire_piece():
    sol = matiere("sol", (0.34, 0.32, 0.30), 0.44)
    grain(sol, 14.0, 0.14)
    mur = matiere("mur", (0.56, 0.56, 0.57), 0.80)
    grain(mur, 40.0, 0.06)
    cadre = matiere("cadre de baie", (0.055, 0.055, 0.058), 0.36, metal=0.9)

    bpy.ops.mesh.primitive_plane_add(size=18.0, location=(0, 0, 0))
    bpy.context.active_object.name = "sol"
    bpy.context.active_object.data.materials.append(sol)

    #  Mur du fond, puis plafond.
    boite("mur du fond", (MUR_X - EPAISSEUR, 4.5),
          (MUR_Y, MUR_Y + EPAISSEUR), (0, PLAFOND), mur)
    boite("plafond", (MUR_X - EPAISSEUR, 4.5), (-4.2, MUR_Y + EPAISSEUR),
          (PLAFOND, PLAFOND + EPAISSEUR), mur)

    #  Le mur de gauche est fait de quatre morceaux autour de l'ouverture.
    #  Un booléen ferait le même trou et coûterait une topologie sale.
    x = (MUR_X - EPAISSEUR, MUR_X)
    boite("baie bas", x, (-4.2, MUR_Y), (0, BAIE_Z[0]), mur)
    boite("baie haut", x, (-4.2, MUR_Y), (BAIE_Z[1], PLAFOND), mur)
    boite("baie avant", x, (-4.2, BAIE_Y[0]), BAIE_Z, mur)
    boite("baie arrière", x, (BAIE_Y[1], MUR_Y), BAIE_Z, mur)

    #  LE DORMANT, DEUX MENEAUX ET UNE TRAVERSE.
    #
    #  Avec une ouverture nue, le soleil posait sur le mur du fond un aplat
    #  crème sans forme, qui ne disait rien. Ce sont les BARREAUX qui font
    #  lire une fenêtre : leur ombre découpe la tache en carreaux, et l'oeil
    #  reconnaît la lumière du jour avant même d'avoir vu la baie. Six
    #  pavés, et l'image change de nature.
    pieces = [("dormant bas", BAIE_Y, (BAIE_Z[0], BAIE_Z[0] + 0.055)),
              ("dormant haut", BAIE_Y, (BAIE_Z[1] - 0.055, BAIE_Z[1])),
              ("dormant avant", (BAIE_Y[0], BAIE_Y[0] + 0.055), BAIE_Z),
              ("dormant arrière", (BAIE_Y[1] - 0.055, BAIE_Y[1]), BAIE_Z)]
    largeur = BAIE_Y[1] - BAIE_Y[0]
    for i in (1, 2):
        centre = BAIE_Y[0] + largeur * i / 3.0
        pieces.append(("meneau %d" % i, (centre - 0.019, centre + 0.019),
                       BAIE_Z))
    traverse = BAIE_Z[0] + (BAIE_Z[1] - BAIE_Z[0]) * 0.46
    pieces.append(("traverse", BAIE_Y, (traverse - 0.022, traverse + 0.022)))
    for nom, y, z in pieces:
        boite(nom, (MUR_X - 0.05, MUR_X - 0.005), y, z, cadre)


# ===========================================================================
#  LE MONDE
# ===========================================================================

def monde():
    m = bpy.data.worlds.new("venise")
    m.use_nodes = True
    a = m.node_tree
    for n in list(a.nodes):
        if n.type != 'OUTPUT_WORLD':
            a.nodes.remove(n)
    sortie = next(n for n in a.nodes if n.type == 'OUTPUT_WORLD')

    coord = a.nodes.new("ShaderNodeTexCoord")
    carte = a.nodes.new("ShaderNodeMapping")
    carte.inputs["Rotation"].default_value[2] = ROTATION_MONDE
    env = a.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(os.path.join(SOURCES, "venise.exr"))
    fond = a.nodes.new("ShaderNodeBackground")
    fond.inputs["Strength"].default_value = float(
        os.environ.get("FORCE_MONDE", "2.1"))

    a.links.new(coord.outputs["Generated"], carte.inputs["Vector"])
    a.links.new(carte.outputs["Vector"], env.inputs["Vector"])
    a.links.new(env.outputs["Color"], fond.inputs["Color"])
    a.links.new(fond.outputs["Background"], sortie.inputs["Surface"])
    bpy.context.scene.world = m

    #  LE SOLEIL QUE LE FICHIER NE SAIT PAS PORTER.
    #
    #  Mesuré sur l'EXR : le disque solaire culmine à 2725, soit 6418 fois
    #  la moyenne de l'image. C'est énorme pour un fichier, et très faible
    #  pour un soleil : un astre bas réel envoie plusieurs dizaines de
    #  milliers. Un panorama en demi-flottant écrête toujours son disque,
    #  et l'éclairage qui en sort est celui d'un ciel voilé, gris et sans
    #  ombre portée. C'est exactement ce que donnaient les deux premiers
    #  brouillons.
    #
    #  On rend donc au soleil ce que le capteur lui a pris, avec une lampe
    #  Sun placée à la direction MESURÉE, pas choisie : même azimut que
    #  l'HDRI une fois tourné, même hauteur de 3,5 degrés. La scène garde
    #  l'éclairage du panorama et retrouve son ombre.
    hauteur = math.radians(3.5)
    azimut = math.radians(SOLEIL_VISE)
    vers = Vector((math.cos(hauteur) * math.cos(azimut),
                   math.cos(hauteur) * math.sin(azimut),
                   math.sin(hauteur)))
    soleil = bpy.data.lights.new("soleil", 'SUN')
    soleil.energy = float(os.environ.get("SOLEIL", "11"))
    soleil.color = (1.0, 0.72, 0.47)
    soleil.angle = math.radians(1.6)
    os_ = bpy.data.objects.new("soleil", soleil)
    bpy.context.scene.collection.objects.link(os_)
    os_.rotation_euler = vers.to_track_quat('Z', 'Y').to_euler()
    print("  soleil azimut %.1f deg, hauteur 3,5 deg, %.0f W/m2"
          % (SOLEIL_VISE, soleil.energy))

    #  UN PORTAIL DEVANT LA BAIE.
    #
    #  Éclairer un intérieur à travers une ouverture est le cas le plus
    #  bruyant de Cycles : la plupart des rayons partis du sol tapent un mur.
    #  Le portail dit au moteur où est la lumière. Il ne change pas l'image,
    #  seulement le nombre d'échantillons nécessaires pour y arriver.
    lampe = bpy.data.lights.new("portail", 'AREA')
    lampe.shape = 'RECTANGLE'
    lampe.size = BAIE_Y[1] - BAIE_Y[0]
    lampe.size_y = BAIE_Z[1] - BAIE_Z[0]
    o = bpy.data.objects.new("portail", lampe)
    bpy.context.scene.collection.objects.link(o)
    o.location = (MUR_X - 0.02, (BAIE_Y[0] + BAIE_Y[1]) / 2,
                  (BAIE_Z[0] + BAIE_Z[1]) / 2)
    o.rotation_euler = (0, -math.pi / 2, 0)
    if hasattr(lampe, "cycles") and hasattr(lampe.cycles, "is_portal"):
        lampe.cycles.is_portal = True
        print("  portail actif")
    else:
        bpy.data.objects.remove(o, do_unlink=True)
        print("  pas de portail dans cette version, on montera les "
              "échantillons")


# ===========================================================================
#  L'ÉCRAN
# ===========================================================================

def reparer_ecran(objets):
    """Le plastique redevient du plastique, et la dalle reflète."""
    corrige = 0
    for o in objets:
        for m in [s for s in o.data.materials if s]:
            if not m.use_nodes:
                continue
            p = next((n for n in m.node_tree.nodes
                      if n.type == 'BSDF_PRINCIPLED'), None)
            if p is None:
                continue
            base = list(p.inputs["Base Color"].default_value)
            clair = max(base[0], base[1], base[2])
            metal = p.inputs["Metallic"].default_value
            if metal > 0.5 and clair < 0.5:
                #  Un métal presque noir n'existe pas. C'est du plastique.
                p.inputs["Metallic"].default_value = 0.0
                #  ON NE MONTE PAS LA RUGOSITÉ, ON LA LAISSE BASSE.
                #
                #  Réflexe de départ : rendre le cadre mat pour qu'il cesse
                #  de renvoyer le mur ensoleillé. C'était l'inverse de ce
                #  qu'il fallait faire. La part diffuse ne dépend pas de la
                #  rugosité, seulement de l'albédo : rugosifier n'assombrit
                #  rien, ça ne fait qu'étaler le spéculaire sur toute la
                #  surface au lieu de le concentrer en un reflet. Un cadre
                #  de moniteur noir reste noir en plein jour PARCE QUE son
                #  vernis est net : il ramasse la fenêtre en une bande
                #  brillante et laisse le reste sombre.
                p.inputs["Roughness"].default_value = min(
                    0.30, p.inputs["Roughness"].default_value)
                p.inputs["Base Color"].default_value = (
                    max(base[0], 0.016), max(base[1], 0.016),
                    max(base[2], 0.016), 1.0)
                corrige += 1
            elif metal > 0.5 and clair > 0.5:
                #  LE PIED RESTE MÉTALLIQUE, MAIS PAS CHROMÉ.
                #
                #  À 0,8 de base et 0,4 de rugosité, le pied est un miroir :
                #  dans une pièce sombre il passait pour du métal foncé,
                #  sous le soleil il est devenu une barre blanche qui tire
                #  l'oeil plus que l'écran. Un pied de moniteur est en
                #  aluminium brossé sombre, donc base basse et rugosité
                #  haute. C'est le seul matériau qui garde son métal.
                #  ON RÉAFFECTE LE TABLEAU ENTIER, ON NE LE MODIFIE PAS EN PLACE.
                #
                #  `default_value[i] = x` sur une couleur ne s'écrit pas
                #  toujours dans le noeud. Les premiers correctifs avaient
                #  l'air de fonctionner parce que les valeurs visées
                #  tombaient déjà bien ; seul le pied, à 0,8, révélait la
                #  panne, et il restait un miroir crème au milieu de
                #  l'image. On affecte donc un quadruplet complet, et on
                #  relit derrière.
                p.inputs["Base Color"].default_value = (0.09, 0.09, 0.095, 1.0)
                p.inputs["Roughness"].default_value = max(
                    0.55, p.inputs["Roughness"].default_value)
                corrige += 1
    #  ON RELIT CE QU'ON VIENT D'ÉCRIRE.
    for o in objets:
        for m in [x for x in o.data.materials if x]:
            if not m.use_nodes:
                continue
            p = next((n for n in m.node_tree.nodes
                      if n.type == 'BSDF_PRINCIPLED'), None)
            if p is None:
                continue
            c = p.inputs["Base Color"].default_value
            print("     %-16s base %.3f %.3f %.3f  metal %.2f  rug %.2f"
                  % (m.name[:16], c[0], c[1], c[2],
                     p.inputs["Metallic"].default_value,
                     p.inputs["Roughness"].default_value))
    print("  coque : %d matériaux corrigés" % corrige)

    dalle = None
    for o in objets:
        for m in [s for s in o.data.materials if s]:
            if m.use_nodes and any(n.type == 'TEX_IMAGE'
                                   for n in m.node_tree.nodes):
                dalle = (o, m)
    if dalle is None:
        raise SystemExit("aucune dalle trouvée sur l'écran")
    return dalle


def allumer_dalle(materiau, image, force):
    """Emission seule -> Principled qui émet ET reflète.

    Une pure Emission ne renvoie rien : sous une baie vitrée, l'écran serait
    le seul objet de la pièce à ne pas savoir qu'il y a une fenêtre.
    """
    a = materiau.node_tree
    tex = next(n for n in a.nodes if n.type == 'TEX_IMAGE')
    tex.image = image
    tex.interpolation = 'Cubic'
    for n in list(a.nodes):
        if n.type == 'EMISSION':
            a.nodes.remove(n)
    sortie = next(n for n in a.nodes if n.type == 'OUTPUT_MATERIAL')
    p = a.nodes.new("ShaderNodeBsdfPrincipled")
    p.inputs["Base Color"].default_value = (0.008, 0.008, 0.009, 1.0)
    #  UN TRAITEMENT ANTIREFLET, PARCE QUE LES ÉCRANS DE TRAVAIL EN ONT UN.
    #
    #  Sans lui, la dalle incurvée ramasse la baie sur tout son tiers droit
    #  et la colonne des propriétés de Blender disparaît sous un voile. Ce
    #  n'est pas une erreur de rendu, c'est ce que fait une vitre nue face à
    #  une fenêtre, et c'est précisément pour ça qu'un écran de production
    #  est mat. On baisse donc le niveau spéculaire et on ouvre un peu la
    #  rugosité : le reflet devient un voile sourd au lieu d'un miroir.
    p.inputs["Roughness"].default_value = 0.30
    p.inputs["Specular IOR Level"].default_value = 0.20
    p.inputs["Metallic"].default_value = 0.0
    a.links.new(tex.outputs["Color"], p.inputs["Emission Color"])
    a.links.new(p.outputs["BSDF"], sortie.inputs["Surface"])

    #  LA DALLE BRILLE POUR L'OBJECTIF, PAS POUR LA PIÈCE.
    #
    #  Pour rester lisible à côté d'un mur au soleil, l'écran demandait une
    #  émission forte. À cette force il devenait une LAMPE : le cadre et le
    #  pied, juste à côté, viraient au crème, et le moniteur noir du modèle
    #  ressortait beige. Ce n'est pas ce que fait un écran de 300 candelas
    #  en plein jour.
    #
    #  On sépare donc les deux rôles avec `Is Camera Ray` : plein feu pour
    #  le rayon qui vient de l'objectif, un sixième pour ceux qui repartent
    #  éclairer la scène. L'écran reste lisible et cesse d'éclairer son
    #  propre cadre.
    chemin = a.nodes.new("ShaderNodeLightPath")
    melange = a.nodes.new("ShaderNodeMix")
    melange.data_type = 'FLOAT'
    melange.inputs[2].default_value = force * 0.16   # rayons indirects
    melange.inputs[3].default_value = force          # rayon caméra
    a.links.new(chemin.outputs["Is Camera Ray"], melange.inputs[0])
    a.links.new(melange.outputs[0], p.inputs["Emission Strength"])
    print("  dalle : émission %.1f vue de l'objectif, %.1f pour la scène"
          % (force, force * 0.16))


def image_de_dalle(rapport):
    """L'image affichée. Si la capture de Blender est là, on la prend ;
    sinon on refuse de rendre plutôt que d'inventer un écran."""
    capture = os.path.join(SOURCES, "dalle.png")
    if not os.path.exists(capture):
        raise SystemExit(
            "l'image de la dalle manque : lancez d'abord la capture de "
            "l'interface de Blender (sources/dalle.png)")
    im = bpy.data.images.load(capture)
    r = im.size[0] / float(im.size[1])
    if abs(r - rapport) > 0.02:
        raise SystemExit(
            "la capture est en %.3f alors que la dalle est en %.3f : "
            "l'image serait étirée de %.0f %%"
            % (r, rapport, abs(r / rapport - 1) * 100))
    return im


# ===========================================================================
#  MONTAGE
# ===========================================================================

def principal():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)

    print("chargement")
    bureau = charger("bureau.blend")
    fauteuil = charger("fauteuil.blend")
    ecran = charger("ecran.blend")
    clavier = charger("clavier.blend", seuil=12.0)
    souris = charger("souris.blend", seuil=12.0)

    print("mise à l'échelle et pose")
    #  Le bureau est calé sur la HAUTEUR du plateau, pas sur sa longueur :
    #  c'est la hauteur qu'un lecteur compare inconsciemment au fauteuil.
    print("   bureau")
    _, taille_bureau = poser(bureau, 'z', PLATEAU, (0, 0, 0))
    b_bas, b_haut = encombrement(bureau)
    #  Il est normalisé, donc très allongé une fois mis à la bonne hauteur.
    #  On le pousse contre le mur de gauche et on laisse filer le reste
    #  hors cadre : c'est ce que fait un vrai plan de travail en enfilade.
    longueur = b_haut[0] - b_bas[0]
    decalage = MUR_X + longueur / 2 + 0.02
    for o in bureau:
        if o.parent is None:
            o.matrix_world = Matrix.Translation((decalage, 0.46, 0)) @ o.matrix_world
    bpy.context.view_layer.update()
    b_bas, b_haut = encombrement(bureau)
    dessus = b_haut[2]
    print("     plateau à %.3f m, de x %.2f à %.2f, y %.2f à %.2f"
          % (dessus, b_bas[0], b_haut[0], b_bas[1], b_haut[1]))

    print("   fauteuil")
    #  Le fauteuil regarde -Y dans sa source ; le poste est de l'autre côté,
    #  donc demi-tour, plus douze degrés pour qu'il ne soit pas aligné au
    #  cordeau : personne ne repousse sa chaise droit dans l'axe.
    _, taille_fauteuil = poser(fauteuil, 'z', FAUTEUIL_HAUT, (-0.30, -0.52, 0),
                               rotation=math.radians(192))

    print("   écran")
    dalle_objet, dalle_mat = reparer_ecran(ecran)
    #  LA COTE CONNUE PORTE SUR LA DALLE, PAS SUR LA COQUE.
    #
    #  `poser` met à l'échelle sur l'encombrement du groupe, qui inclut le
    #  cadre. On lui passe donc la largeur de coque qui DONNERA 0,800 m de
    #  dalle, calculée sur le rapport des deux mesures avant toute
    #  transformation. Viser la coque au jugé donnerait un écran de 0,79 m
    #  ou de 0,81 m selon l'épaisseur du cadre, et l'erreur se verrait dans
    #  les proportions du poste entier.
    d_bas, d_haut = encombrement([dalle_objet])
    e_bas, e_haut = encombrement(ecran)
    largeur_dalle = d_haut[0] - d_bas[0]
    largeur_coque = e_haut[0] - e_bas[0]
    rapport = largeur_dalle / (d_haut[2] - d_bas[2])
    poser(ecran, 'x', DALLE * largeur_coque / largeur_dalle,
          (-0.18, 0.66, dessus))
    d_bas, d_haut = encombrement([dalle_objet])
    print("     dalle %.3f x %.3f m, rapport %.3f, haut à %.3f"
          % (d_haut[0] - d_bas[0], d_haut[2] - d_bas[2], rapport, d_haut[2]))

    allumer_dalle(dalle_mat, image_de_dalle(rapport),
                  float(os.environ.get("FORCE_DALLE", "3.2")))

    print("   clavier")
    _, taille_clavier = poser(clavier, 'x', CLAVIER, (-0.20, 0.17, dessus),
                              rotation=math.radians(-2))
    print("   souris")
    _, taille_souris = poser(souris, 'x', SOURIS, (0.16, 0.20, dessus),
                             rotation=math.radians(8))

    construire_piece()
    monde()

    #  ------------------------------------------------------------------
    #  CONTRÔLE DES COTES
    #  ------------------------------------------------------------------
    mesures = {
        "plateau": dessus,
        "hauteur du fauteuil": taille_fauteuil[2],
        "largeur de la dalle": d_haut[0] - d_bas[0],
        "longueur du clavier": taille_clavier[0],
        "largeur de la souris": taille_souris[0],
    }
    print("contrôle des cotes")
    for nom, _, mini, maxi in CONTROLES:
        v = mesures[nom]
        etat = "ok" if mini <= v <= maxi else "HORS FOURCHETTE"
        print("   %-22s %.3f m   (%.2f à %.2f)  %s" % (nom, v, mini, maxi, etat))
        if not mini <= v <= maxi:
            raise SystemExit(
                "%s mesure %.3f m, hors de la fourchette %.2f à %.2f : "
                "le mobilier ne serait pas à la même échelle"
                % (nom, v, mini, maxi))

    #  ------------------------------------------------------------------
    #  CAMÉRA
    #  ------------------------------------------------------------------
    cible = Vector((-0.32, 0.30, 0.85))
    cam = bpy.data.cameras.new("camera")
    cam.lens = float(os.environ.get("FOCALE", "42"))
    oc = bpy.data.objects.new("camera", cam)
    bpy.context.scene.collection.objects.link(oc)
    oc.location = Vector((1.34, -1.98, 1.34))
    oc.rotation_euler = (cible - oc.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = oc

    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = ECHANTILLONS
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.01
    sc.cycles.use_denoising = True
    sc.cycles.caustics_reflective = False
    sc.cycles.caustics_refractive = False
    sc.render.resolution_x = LARGEUR_RENDU
    sc.render.resolution_y = int(round(LARGEUR_RENDU * 9 / 16.0))
    sc.render.film_transparent = False
    sc.view_settings.view_transform = 'AgX'
    #  UN DIAPHRAGME, PAS UN RÉGLAGE DE GOÛT.
    #
    #  Sans correction, toute la scène tient dans les tons clairs : le
    #  moniteur noir du modèle ressort gris pâle, et la tache de soleil ne
    #  se détache plus d'un mur déjà clair. Fermer d'un peu moins d'un
    #  diaphragme remet la pièce dans les tons moyens et rend au soleil son
    #  écart avec l'ombre.
    sc.view_settings.exposure = float(os.environ.get("DIAPH", "-1.0"))
    sc.view_settings.look = 'AgX - Medium High Contrast'

    os.makedirs(SORTIE, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(SORTIE, "poste.blend"))
    sc.render.filepath = os.path.join(SORTIE, "poste.png")
    print("rendu %d x %d, %d échantillons"
          % (sc.render.resolution_x, sc.render.resolution_y, ECHANTILLONS))
    bpy.ops.render.render(write_still=True)
    print("TERMINE %s" % sc.render.filepath)


if __name__ == "__main__":
    principal()
