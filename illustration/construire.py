# -*- coding: utf-8 -*-
"""
Construit scene.svg en entier. Les proportions sont ici, pas eparpillees
dans le fichier : c'est ce qui permet de tenir le decoupage au pixel.

    python3 construire.py && inkscape --export-type=png \
        --export-filename=scene.png -w 1080 scene.svg
"""
import perspective as P
import verdure
import grillage
import parasols
import nuages
import mer
import serviette
import haie
import herbe
import personnages
import objets
import enfant

# LE FORMAT. 1800 x 1350, soit du 4:3. La hauteur ne change pas : c'est elle
# qui porte l'egalite ciel/sable, il n'y avait aucune raison d'y toucher pour
# elargir. Un seul nombre a changer ici si tu veux un autre cadre - la
# verdure, le bord du sable et le degrade du ciel s'y adaptent tout seuls.
LARGEUR, HAUTEUR = 1800, 1350
verdure.LARGEUR = LARGEUR

# Le grillage est-il dans l'image ? Passe en argument :
#     python3 construire.py            -> scene.svg, avec
#     python3 construire.py sans       -> scene_sans_grillage.svg
import sys
import os
AVEC_GRILLAGE = "sans" not in sys.argv

# L'ANIMATION : ANIM_T dans [0,1[ est la phase de la boucle. Tout mouvement
# est PERIODIQUE en t (sinus de k*2*pi*t, k entier) : l'image 0 et l'image N
# sont identiques, la boucle n'a pas de couture. Chaque image reste un SVG
# complet rendu par Inkscape - aucun contour ne respire, le grain est stable.
ANIM_T = float(os.environ.get("ANIM_T", "-1"))
ANIM_SCENE = os.environ.get("ANIM_SCENE", "boucle")
ANIME = ANIM_T >= 0.0
_t = max(0.0, ANIM_T)
import math as _math
# la derive des nuages : lente, faible, dephasee - une oscillation de
# quelques pixels lit comme du flottement, pas comme un vent qui tourne
DX1 = 10.0 * _math.sin(2 * _math.pi * _t)
DX2 = 7.0 * _math.sin(2 * _math.pi * _t + 2.1)
DX3 = 12.0 * _math.sin(2 * _math.pi * _t + 4.2)

# LA VERDURE EST-ELLE DANS L'IMAGE ? Elle n'y est plus : le modele n'a pas de
# bande de haie, il a du ciel, du sable, puis la mer. Notre mur vert occupait
# exactement la place que sa plage donne au sable.
# Remis a True, tout revient - le buisson, son ombrage, et le bord de sable
# ondule qui le suivait.
AVEC_VERDURE = False

# L'ENFANT est retire : la scene se construit d'abord comme un lieu, les
# personnages viendront apres. Remis a True, il revient avec ses jouets.
AVEC_ENFANT = False

# LA MER et LA SERVIETTE, retirees. La seconde reference ne montre ni l'une
# ni l'autre : du ciel, une haie taillee, du sable. Les deux modules restent
# la, il suffit de repasser a True.
AVEC_MER = False
AVEC_SERVIETTE = False

# LA HAIE remplace le buisson : masse pleine a bord haut finement frisote,
# relevee sur la seconde reference. Voir haie.py.
AVEC_HAIE = True

# L'HERBE, au bas de l'image : le premier plan de la reference. Une bande
# olive de brins, sous le sable. Voir herbe.py.
AVEC_HERBE = False

# LE VERT AU SOL de la cinquieme reference : la verge au pied de la haie et
# les deux coins d'herbe en bas, penches par le vent. Voir herbe.sol_vert().
AVEC_SOL_VERT = False

# LES PERSONNAGES de la cinquieme reference : l'enfant qui creuse, le
# coureur au ballon, le couple sur la serviette rayee. Voir personnages.py.
AVEC_PERSONNAGES = False

# LA SERVIETTE RAYEE, seule : on la regle avant d'y rasseoir le couple.
AVEC_SERVIETTE_RAYEE = True

# L'HOMME sur la serviette - le premier personnage, decalque de la
# reference. Sa MAIN se plante a cote du mat coupe, comme dans le modele :
# c'est elle qui fixe sa place, pas le centre du tissu.
AVEC_HOMME = False

# LA FEMME a sa droite, meme methode. Sa nappe d'ombre est celle du
# COUPLE : quand elle est la, la grande ombre de l'homme s'eteint.
AVEC_FEMME = False

# LES VRAIS PERSONNAGES : a True, le couple est DECOUPE dans la reference
# elle-meme (accorde a nos tons) au lieu des decalques vectoriels - c'est
# le rendu le plus fidele. A False, les aplats vectoriels reviennent.
AVEC_VRAIS_PERSOS = False

# LES ENFANTS AUX SEAUX et LE COUREUR AU BALLON, decoupes eux aussi,
# ancres au pied du parasol de GAUCHE comme dans le modele (leur groupe
# est a -183 px de reference du mat, le coureur a +177).
AVEC_ENFANTS = False

# LA NATURE MORTE - la proposition : l'ete raconte par les objets, tout
# le monde est a l'eau. COMPOSITION ETUDIEE (affiche mid-century + riso) :
#   un seul dominant  le groupe parasol 2 + serviette + chapeau, ancre au
#                     tiers droit ; le parasol 1, coupe par le cadre a
#                     gauche, sert de repoussoir - il cadre, il ne parle pas
#   la diagonale      cerf-volant (tiers haut-gauche) -> nuages -> toile du
#                     parasol 2 -> le mat est une FLECHE vers la serviette
#                     -> chapeau -> tongs -> ballon -> seau : un Z de lecture
#   l'accent rouge    ~10 %, reparti LE LONG du chemin : moitie du
#                     cerf-volant, noeuds de sa queue, croissant du ballon,
#                     brides des tongs, seau terre cuite
#   l'espace negatif  le centre du sable reste VIDE - c'est la respiration ;
#                     le ciel n'a que le cerf-volant et trois nuages
AVEC_NATURE_MORTE = True
PART_HERBE = 0.10

# LE GRAIN GLOBAL. A True, un seul calque de points couvre toute l'image et
# les grains par matiere sont mis en veille : c'est ce que fait la reference.
GRAIN_GLOBAL = True
GRAIN_FINESSE = 0.28      # taille du point : 1/0.34 = 2.9 px
GRAIN_FORCE = 0.90
grillage.LARGEUR = LARGEUR

# LE DECOUPAGE. Ciel et sable ont exactement la meme hauteur ; la verdure
# occupe ce qui reste. C'est une contrainte, pas un reglage a l'oeil :
#     ciel     0 -> 470   =  470
#     verdure  470 -> 880 =  410
#     sable    880 -> 1350 = 470
# L'horizon, donc le point de fuite, est a 470 : c'est lui qui fixe le
# decoupage maintenant que la scene est en perspective. Au milieu de l'image
# le ciel et le sable retrouvent des hauteurs voisines - mais ce n'est plus
# une egalite imposee, c'est une consequence de la geometrie, et cela ne peut
# pas etre autrement sans mentir sur l'espace.
# LE DECOUPAGE VIENT DU MODELE, pas de notre point de fuite.
#   ciel   0   -> 230 sur 760   =  30 %
#   sable  230 -> 562           =  44 %
#   mer    562 -> 760           =  26 %
# Les trois parts sont donnees ici en fractions et TOUT en decoule : la ligne
# d'horizon, le haut du sable, et la ligne moyenne de la vague. Changer une
# fraction suffit ; il n'y a aucun nombre de pixels a rattraper a la main.
# AVEC LA HAIE, le decoupage vient de la SECONDE reference :
#   ciel   0   -> 515 sur 953   =  54 %
#   haie   515 -> 770           =  27 %
#   sable  770 -> 953           =  19 %
# Sans elle, c'est celui de la premiere : ciel 30, sable 44, mer 26.
if AVEC_HAIE:
    PART_CIEL, PART_HAIE, PART_SABLE, PART_MER = 0.54, 0.27, 0.19, 0.0
else:
    PART_CIEL, PART_HAIE, PART_SABLE, PART_MER = 0.30, 0.0, 0.44, 0.26

CIEL_BAS = int(round(PART_CIEL * HAUTEUR))
HAIE_PIED = int(round((PART_CIEL + PART_HAIE) * HAUTEUR))
CRETE_MER = int(round((PART_CIEL + PART_HAIE + PART_SABLE) * HAUTEUR))
# La vague oscille AUTOUR d'une moyenne ; c'est sa CRETE qui doit tomber sur
# la limite mesuree, donc la moyenne descend d'une amplitude.
mer.MOYENNE = CRETE_MER + mer.AMPLITUDE
# Les ombres des parasols ne remontent jamais sur la verge du pied de haie.
parasols.OMBRE_Y_MIN = HAIE_PIED + 0.032 * HAUTEUR + 8

CIEL = "#E4F1FA"
NUAGE_CLAIR, NUAGE_FROID = "#FFFFFF", "#D3E5F1"
SABLE = "#FAFAF6"


def mouchetis(nom, graine, force, commentaire):
    if GRAIN_GLOBAL:
        force = "0.04"      # presque rien : le calque global fait le travail
    """
    Un grain dont l'effet NE DEPEND PAS de la couleur du fond.

    "overlay" mord d'autant plus que l'aplat est de valeur moyenne : sur la
    toile du parasol il donnait 10.8%% de contraste sur le vert et 0%% sur le
    blanc, alors qu'on voulait la meme matiere sur les deux. Un seul reglage
    ne peut pas y arriver, le probleme est dans le mode de fusion lui-meme.

    Ici on ne fusionne pas : on POSE des points, moitie clairs moitie sombres,
    a opacite fixe. Un point blanc a 9%% eclaircit un vert et un blanc de la
    meme quantite absolue. Le grain devient donc constant d'un aplat a
    l'autre - c'est ce qu'il faut pour un objet a deux couleurs.
    """
    return """  <!-- %s -->
  <filter id="%s" x="-2%%" y="-2%%" width="104%%" height="104%%">
    <feTurbulence type="fractalNoise" baseFrequency="1.2" numOctaves="2"
                  seed="%d" result="bruit"/>
    <feColorMatrix in="bruit" type="luminanceToAlpha" result="alpha"/>
    <feComponentTransfer in="alpha" result="hauts">
      <feFuncA type="table" tableValues="0 0 %s"/>
    </feComponentTransfer>
    <feFlood flood-color="#FFFFFF" result="blanc"/>
    <feComposite in="blanc" in2="hauts" operator="in" result="clairs"/>
    <feComponentTransfer in="alpha" result="bas">
      <feFuncA type="table" tableValues="%s 0 0"/>
    </feComponentTransfer>
    <feFlood flood-color="#000000" result="noir"/>
    <feComposite in="noir" in2="bas" operator="in" result="sombres"/>
    <feMerge result="points">
      <feMergeNode in="sombres"/><feMergeNode in="clairs"/>
    </feMerge>
    <feComposite in="points" in2="SourceAlpha" operator="in" result="coupes"/>
    <feMerge>
      <feMergeNode in="SourceGraphic"/><feMergeNode in="coupes"/>
    </feMerge>
  </filter>""" % (commentaire, nom, graine, force, force)


def grain_global(nom, graine, force, finesse, commentaire):
    """
    UN SEUL CALQUE DE GRAIN, pose sur toute l'image.

    POURQUOI CELUI-LA REMPLACE LES AUTRES
      Jusqu'ici chaque matiere portait son propre filtre, chacun regle
      separement : ciel 1.05, haie 0.42, toile verte 0.38, toile blanche 1.00.
      C'est ce qui obligeait a des reglages differents pour obtenir "la meme
      matiere" sur deux couleurs - et ca ne marchait qu'a peu pres.

      La reference ne fait pas cela. Son grain est POSE PAR-DESSUS TOUT, d'un
      bloc : meme densite, meme taille de point sur le ciel, sur le feuillage
      et sur le sable. C'est un tirage, pas sept textures cote a cote. D'ou
      son unite - et d'ou le fait que notre sable, parfaitement lisse, sonnait
      faux au milieu du reste.

    LA FINESSE
      baseFrequency est en unites de dessin : 1.2 donne des points de 0.83 px,
      c'est-a-dire sous la resolution de l'oeil. Sur la reference les points
      font environ 3 px, soit une frequence de 0.33. Notre grain n'etait pas
      trop faible, il etait TROP FIN - a force egale, un bruit trop fin se
      moyenne et disparait.

    Le filtre ne lit jamais SourceGraphic : il ne produit que les points, sur
    du transparent. On le pose donc sur un rectangle, tout en haut.
    """
    return """  <!-- %s -->
  <filter id="%s" x="0%%" y="0%%" width="100%%" height="100%%">
    <feTurbulence type="fractalNoise" baseFrequency="%s" numOctaves="1"
                  seed="%d" result="bruit"/>
    <feColorMatrix in="bruit" type="luminanceToAlpha" result="alpha"/>
    <feComponentTransfer in="alpha" result="hauts">
      <feFuncA type="table" tableValues="0 0 %s"/>
    </feComponentTransfer>
    <feFlood flood-color="#FFFFFF" result="blanc"/>
    <feComposite in="blanc" in2="hauts" operator="in" result="clairs"/>
    <feComponentTransfer in="alpha" result="bas">
      <feFuncA type="table" tableValues="%s 0 0"/>
    </feComponentTransfer>
    <feFlood flood-color="#000000" result="noir"/>
    <feComposite in="noir" in2="bas" operator="in" result="sombres"/>
    <feMerge>
      <feMergeNode in="sombres"/><feMergeNode in="clairs"/>
    </feMerge>
  </filter>""" % (commentaire, nom, finesse, graine, force, force)


def grain(nom, graine, intensite, commentaire):
    if GRAIN_GLOBAL:
        intensite = "0.10"
    return """  <!-- %s -->
  <filter id="%s" x="-2%%" y="-2%%" width="104%%" height="104%%">
    <feTurbulence type="fractalNoise" baseFrequency="1.2" numOctaves="2"
                  seed="%d" result="bruit"/>
    <feColorMatrix in="bruit" type="saturate" values="0" result="gris"/>
    <feComponentTransfer in="gris" result="regle">
      <feFuncA type="linear" slope="%s" intercept="0"/>
    </feComponentTransfer>
    <feComposite in="regle" in2="SourceAlpha" operator="in" result="decoupe"/>
    <feBlend in="SourceGraphic" in2="decoupe" mode="overlay"/>
  </filter>""" % (commentaire, nom, graine, intensite)


# LES NUAGES. Le rapport 5.8 : 1 vient du modele - ses trois nuages y sont
# tous, a un dixieme pres (voir nuages.py). Les notres etaient a 2.6 : 1,
# c'est-a-dire deux fois trop hauts.
#
# (x, ligne de pose, longueur, profil de crete)
# Trois longueurs et trois cretes differentes : trois nuages de meme calibre
# feraient une frise, trois nuages differents font un ciel.
NUAGES = [(140, 232, 430, 0), (760, 330, 360, 1), (1300, 196, 400, 2)]
NUAGE1, NUAGE2, NUAGE3 = [nuages.nuage(*n) for n in NUAGES]
# Le decalage du ton clair est PROPORTIONNEL a la longueur : un decalage fixe
# donnerait une grosse lisiere froide sous le petit nuage et rien sous le
# grand.
DEC1, DEC2, DEC3 = [max(5, n[2] / 46.0) for n in NUAGES]

# LE BORD DU SABLE. Il n'ondule plus : c'est la ligne au sol sur laquelle le
# buisson est plante, donc une droite qui fuit vers l'horizon comme tout le
# reste. Une ondulation la aurait contredit la perspective - le sol ne peut
# pas serpenter et fuir en meme temps.
if AVEC_VERDURE:
    _sol = P.ligne_au_sol(verdure.PIED_DEVANT)
    BORD_SABLE = ("M%.1f %.1f " % _sol[0]
                  + " ".join("L%.1f %.1f" % q for q in _sol[1:])
                  + " L%d %d L0 %d Z" % (LARGEUR, HAUTEUR, HAUTEUR))
else:
    # SANS HAIE, le sable commence a l'horizon. Son bord haut est donc une
    # DROITE : il n'y a plus de vegetation posee dessus pour justifier une
    # ondulation, et une ligne de sol qui serpente contredirait la fuite.
    _haut_sable = HAIE_PIED if AVEC_HAIE else CIEL_BAS
    BORD_SABLE = ("M0 %d L%d %d L%d %d L0 %d Z"
                  % (_haut_sable, LARGEUR, _haut_sable,
                     LARGEUR, HAUTEUR, HAUTEUR))

if AVEC_VERDURE:
    coupes, feuillage, _ = verdure.engendrer()
elif AVEC_HAIE:
    coupes, (feuillage, _nb_touffes) = '', haie.engendrer(LARGEUR, CIEL_BAS,
                                                          HAIE_PIED, indent=2)
else:
    coupes, feuillage = '', '  <!-- verdure retiree -->'

fence, nb_poteaux, nb_fils, _ = grillage.bloc(indent=2)
if not AVEC_GRILLAGE:
    fence = '  <!-- grillage retire -->'
# LES PARASOLS : les coupoles a festons de la quatrieme reference.
# L'eventail reste disponible via parasols.engendrer().
coupes_abris, abris, nb_abris = parasols.engendrer_coupoles(
    LARGEUR, HAUTEUR, indent=4)

# ===================== LA PLACE DU PERSONNAGE =========================
# S'il existe un fichier personnage.svg a cote, C'EST LUI qui est pose, tel
# quel, et le script n'y touche jamais. Sinon seulement, on retombe sur
# l'enfant code en Python.
#
# POURQUOI CE MECANISME EXISTE
#   Parce que tu edites, et que je reconstruisais par-dessus. Un generateur
#   qui ecrase le travail de la main est un generateur inutilisable : il
#   oblige a choisir entre le script et le dessin. Ici les deux cohabitent -
#   le decor se calcule, le personnage se depose.
#
#   Mets-y ce que tu veux : un export d'Inkscape, un Humaaans telecharge, une
#   figure sortie de importer_figure.py. Il est insere sans etre relu.
# LA SERVIETTE, posee sous le parasol. Son bord loin est plus court que son
# bord pres - c'est ce qui la couche au sol - et son lisere clair est un vrai
# decalage a marge constante, pas une reduction vers le centre. Voir
# serviette.py.
# LA PLACE DE LA SERVIETTE, relevee sur le modele et donnee en FRACTIONS du
# cadre, comme le decoupage. Sur l'image de 760 : x = 48 -> 352,
# y = 258 -> 372, soit un rectangle de 0.40 de large et 0.15 de haut, centre
# a 0.263 de la largeur et 0.414 de la hauteur.
SERVIETTE = '' if not AVEC_SERVIETTE else serviette.dessiner(cx=0.263 * LARGEUR, cy=0.414 * HAUTEUR,
                               largeur=0.400 * LARGEUR,
                               hauteur=0.150 * HAUTEUR,
                               pivot=-1.5, pourtour=0.0105 * LARGEUR,
                               indent=2)


def bloc_serviette_rayee():
    u"""
    La serviette rayee, le mat coupe par-dessus, et l'homme si demande.

    k=0.85 : le losange de la reference a sa taille pleine deborderait du
    cadre, notre parasol 2 etant plus a droite que le sien (0.84 contre
    0.70). L'echelle des personnages suit LA MEME reduction : un homme a
    l'echelle 1 sur une serviette a 0.85 serait un geant sur un mouchoir.
    """
    ox, oy, kt = 0.840 * LARGEUR, 0.858 * HAUTEUR, 0.85
    morceaux = [personnages.serviette_rayee(ox, oy, kt, 2)]

    # le mat repasse PAR-DESSUS la serviette et s'arrete net a son premier
    # tiers - l'effet stylise de la reference : le tissu n'est pas au pied
    # du parasol, le parasol se plante dedans
    morceaux.append(parasols.mat_sur_serviette(
        LARGEUR, HAUTEUR, personnages.serviette_coupe_mat(ox, oy, kt)))

    if AVEC_HOMME:
        # pixels de la reference -> notre cadre, fois le 0.85 du tissu
        K = (HAUTEUR / 928.0) * kt
        # SA PLACE : la main a plat a cote du mat coupe, comme le modele -
        # le bout des doigts au bord droit du trait (releve : doigts a 869,
        # mat 863-871 ; MESURE sur notre rendu, pas regle a l'oeil - l'oeil
        # s'etait trompe de sens). Le y s'interroge aupres de la serviette,
        # pli compris.
        # 42.5 et non 36 : la main refaite est plus longue de 6 px -
        # le bout des doigts vise le bord droit du trait, pas son axe
        assise_x = ox + 42.5 * K
        assise_y = personnages.serviette_pose(ox, oy, kt, assise_x, v=0.50)

        if AVEC_FEMME and AVEC_VRAIS_PERSOS:
            # les personnages de la reference, decoupes ; l'ancre du mat
            # est reglee pour le bout des doigts de la decoupe (37.5, pas
            # 42.5 : dans la reference meme, les doigts s'arretent 5 px
            # plus tot que ce que mon releve x30 avait lu)
            assise_x = ox + 37.5 * K
            assise_y = personnages.serviette_pose(ox, oy, kt, assise_x,
                                                  v=0.50)
            assise_fx = assise_x + 101.0 * K
            assise_fy = personnages.serviette_pose(ox, oy, kt, assise_fx,
                                                   v=0.50)
            morceaux.append(personnages.vrais_persos(
                assise_x, assise_y, assise_fx, assise_fy, K, 2))
        elif AVEC_FEMME:
            # SA PLACE A ELLE : dans la reference, 105 px les separent et
            # ses orteils restent SUR la serviette. Notre serviette etant
            # centree sur le mat (pas a 0.36 comme le modele), garder les
            # deux a la fois est impossible - on garde les orteils sur le
            # tissu et le couple se resserre de ~4 %. Pas moins de 101 :
            # en dessous, son bras plante tombait dans le V de fond entre
            # ventre et cuisse de l'homme, puis mordait son genou - il doit
            # passer A DROITE du genou, comme le modele. Elle avant lui.
            assise_fx = assise_x + 101.0 * K
            assise_fy = personnages.serviette_pose(ox, oy, kt, assise_fx,
                                                   v=0.50)
            morceaux.append(personnages.femme_serviette(
                assise_fx, assise_fy, K, 2))

        if not (AVEC_FEMME and AVEC_VRAIS_PERSOS):
            morceaux.append(personnages.homme_serviette(
                assise_x, assise_y, K, 2, grande_ombre=not AVEC_FEMME))

    if AVEC_NATURE_MORTE:
        # LE MODULE. Des qu'une figure humaine entre dans l'image, tout
        # objet se mesure par rapport a ELLE - c'est la regle graduee du
        # graphiste, et c'est elle qui manquait : le ballon faisait 0.71
        # fois l'enfant (un ballon de 78 cm !) quand la reference le tient
        # a 0.34 (mesure : ballon 32 px, coureur 95 px). L'enfant debout
        # fait 130.5 px a l'echelle de la scene (102 px de reference
        # x 1.28) ; les rapports ci-dessous sont MESURES sur la reference
        # ou sur l'objet reel. ET C'EST LE BONHOMME QU'ON A GRANDI
        # (130 -> 180) pour etre credible face au ballon - pas le ballon
        # qu'on a rapetisse une seconde fois :
        #   ballon   d = 0.33 M   (32/95 releve)
        #   seau     h = 0.30 M   (les seaux de la reference)
        #   tongs    l = 0.24 M   (un pied d'adulte, ~26 cm)
        #   chapeau  r = 0.26 M   (un bord de ~57 cm)
        # Le cerf-volant est en l'air, sa profondeur est libre.
        MODULE = 180.0
        morceaux.append(u'  <g inkscape:label="Nature morte">')
        # le cerf-volant dans le CIEL OUVERT entre les deux parasols -
        # au premier essai il se noyait dans la toile du grand
        import math
        morceaux.append(objets.cerf_volant(
            0.588 * LARGEUR + 14.0 * math.sin(2 * math.pi * _t),
            0.155 * HAUTEUR + 8.0 * math.sin(4 * math.pi * _t + 1.3),
            52, 2, phase=_t if ANIME else None))
        # le seau au pied du parasol de gauche, pelle plantee
        morceaux.append(objets.seau(0.425 * LARGEUR, 0.897 * HAUTEUR,
                                    0.30 * MODULE, 2))
        # le ballon, arrete au milieu du sable vide - ou EN VOL dans la
        # scene du gamin : course d'elan, frappe, parabole, rebond, sortie
        # a droite, et quelqu'un hors-champ le renvoie rouler a sa place
        # pour que l'image 192 soit exactement l'image 0
        if ANIME and ANIM_SCENE == "gamin":
            import math
            s = _t * 8.0                       # le temps en secondes
            # la ligne de sol du ballon ne bouge pas ; son rayon vient
            # du module (0.165 M = un ballon de 36 cm pour cet enfant)
            xr, ys, rb = 0.556 * LARGEUR, 0.905 * HAUTEUR + 46, 0.165 * MODULE
            sk = 4.55                          # l'instant de la frappe
            dessine = True
            if s < sk:
                bx, bh, ba = xr, 0.0, 0.0
            elif s < sk + 0.977:               # l'envol
                dt = s - sk
                bx = xr + 640.0 * dt
                bh = 430.0 * dt - 440.0 * dt * dt
                ba = (bx - xr) / rb * 34.0
            elif s < sk + 0.977 + 0.489:       # le rebond
                dt = s - sk - 0.977
                bx = xr + 625.0 + 545.0 * dt
                bh = 215.0 * dt - 440.0 * dt * dt
                ba = (bx - xr) / rb * 34.0
            elif s < 6.9:                      # sorti du cadre
                dessine = False
                bx, bh, ba = 0.0, 0.0, 0.0
            else:                              # le retour roule, decelere
                u = (s - 6.9) / 1.1
                bx = 1900.0 - 899.2 * (1.0 - (1.0 - u) ** 2)
                bh = 0.0
                ba = (bx - xr) / rb * 57.3
            if dessine:
                morceaux.append(objets.ballon_mobile(bx, ys, rb, bh, ba, 2))

            # LE GAMIN : il entre a gauche, court (foulees alternees a
            # 3 Hz avec son rebond vertical), FRAPPE, puis poursuit le
            # ballon et sort du cadre - absent au debut et a la fin, la
            # boucle se referme sans lui
            # LE PANTIN AUTHENTIQUE : le coureur de la reference decoupe
            # en pieces articulees - jambes en ANTI-PHASE a 3.2 Hz (quand
            # l'une avance l'autre recule), rebond vertical au meme
            # rythme, corps penche dans la course
            # LA FOULEE ROTOSCOPEE sur la planche 62 de Muybridge
            # (1887) : les angles de cuisse par phase sont ASYMETRIQUES -
            # la jambe monte haut DEVANT (-48) et revient court DERRIERE
            # (+30), avec un passage rapide ; un sinus symetrique courait
            # faux. 12 phases = une foulee complete (deux pas), la jambe
            # opposee est decalee d'une demi-foulee.
            TABLE = [30.0, 22.0, 8.0, -12.0, -34.0, -48.0,
                     -44.0, -28.0, -8.0, 10.0, 24.0, 30.0]

            def foulee(sd, cadence=2.8):
                ph = (sd * cadence * 12.0) % 12.0
                i = int(ph)
                fr = ph - i
                a1 = TABLE[i] * (1 - fr) + TABLE[(i + 1) % 12] * fr
                j = (i + 6) % 12
                a2 = TABLE[j] * (1 - fr) + TABLE[(j + 1) % 12] * fr
                # le rebond : deux appuis par foulee, plus marque a
                # l'appui - lu sur la planche aussi
                bob = 6.0 * abs(math.sin(math.pi * ph / 6.0))
                return a1, a2, bob

            K_G = 1.75          # le bonhomme AGRANDI : 180 px debout
            oy_g = ys + 4.0
            if 1.5 <= s < 4.4:
                xg = -170.0 + (s - 1.5) / 2.9 * 1110.0
                a_av, a_arr, bob = foulee(s - 1.5)
                morceaux.append(personnages.pantin_coureur(
                    xg, oy_g - bob, K_G, a_arr=a_arr, a_av=a_av,
                    panche=8.0, indent=2))
            elif 4.4 <= s < 4.75:
                # la FRAPPE : la jambe avant en swing vers le ballon
                morceaux.append(personnages.pantin_coureur(
                    940.0, oy_g, K_G, a_arr=24.0, a_av=-66.0,
                    panche=-4.0, indent=2))
            elif 4.75 <= s < 7.2:
                xg = 940.0 + (s - 4.75) * 520.0
                a_av, a_arr, bob = foulee(s - 4.75)
                if xg < 2050.0:
                    morceaux.append(personnages.pantin_coureur(
                        xg, oy_g - bob, K_G, a_arr=a_arr, a_av=a_av,
                        panche=9.0, indent=2))
        else:
            # le centre remonte pour garder la MEME ligne de sol
            morceaux.append(objets.ballon(0.556 * LARGEUR,
                                          0.905 * HAUTEUR + 46.0
                                          - 0.165 * MODULE,
                                          0.165 * MODULE, 2))
        # les tongs quittees en vitesse, en chemin vers la serviette
        morceaux.append(objets.tongs(0.756 * LARGEUR, 0.921 * HAUTEUR,
                                     0.24 * MODULE, indent=2))
        # le chapeau pose sur la serviette - le point d'arrivee du regard
        morceaux.append(objets.chapeau(0.882 * LARGEUR, 0.852 * HAUTEUR,
                                       0.26 * MODULE, 2))
        morceaux.append(u'  </g>')

    if AVEC_ENFANTS and AVEC_VRAIS_PERSOS:
        # le pied du parasol de gauche, la reference de leurs places
        p1x, p1y = 0.347 * LARGEUR, 0.857 * HAUTEUR
        K = (HAUTEUR / 928.0) * 0.85
        morceaux.append(personnages.enfants_et_coureur(
            p1x - 183.0 * K, p1y + 6.0 * K,
            p1x + 177.0 * K, p1y - 2.0 * K, K, 2))

    return "\n".join(morceaux)

import os
if not AVEC_ENFANT:
    GAMIN = "  <!-- enfant retire -->"
    SOURCE_PERSONNAGE = "aucun"
elif os.path.exists("personnage.svg"):
    GAMIN = ('  <!-- personnage.svg, depose tel quel - le script ne le '
             'reecrit jamais -->\n'
             + open("personnage.svg", encoding="utf-8").read())
    SOURCE_PERSONNAGE = "personnage.svg"
else:
    GAMIN = enfant.dessiner(880, 950, 1.05, indent=2,
                            filtre_tissu="grainTissu")
    SOURCE_PERSONNAGE = "enfant.py (trace par le script)"

SVG = u"""<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.0.dtd"
     width="{L}" height="{H}" viewBox="0 0 {L} {H}">
<!--
  UN ETE A FRANCONVILLE - le decor, en trois couches.
  Format {L} x {H} (4:5). Engendre par construire.py, ne pas editer a la main
  si tu comptes relancer le script.

  LE DECOUPAGE
    COUCHE 1 - Le ciel        au-dessus de l'horizon, a {CB}
    LE GRILLAGE               plante au sol, il fuit vers la droite
    COUCHE 2 - Le buisson     plante LE LONG du grillage, il fuit avec lui
    COUCHE 3 - Le sable       le sol devant le buisson

  Ce ne sont plus trois bandes horizontales. Le buisson longe la cloture,
  donc il fuit avec elle : sa crete, son pied et le bord du sable sont trois
  lignes au sol qui convergent toutes vers le meme point. Elles ne peuvent
  pas se croiser, et c'est cette impossibilite qui fait tenir la scene.

  LE GRAIN, MATIERE PAR MATIERE
  "overlay" mord d'autant plus que l'aplat est de valeur moyenne : a reglage
  identique, un vert sombre recoit trois fois plus de bruit qu'un ciel pale.
  Les intensites sont donc reglees separement, par mesure, pour que le grain
  se VOIE sans jamais devenir du bruit.

  ET LE SABLE N'EN A PAS DU TOUT. C'est un aplat pur, sans grain, sans creux,
  sans second ton. Il occupe presque la moitie de l'image : la moindre trame
  y devient une texture, et une texture sur une surface aussi grande tire
  l'oeil vers le vide au lieu de le laisser aux masses colorees. La reference
  fait exactement cela - son sable est un blanc casse parfaitement nu.

  DEUX PIEGES VERIFIES, PAS SUPPOSES
    - au-dela de baseFrequency 1.6 le bruit passe sous la resolution de rendu
      et s'ANNULE : mesure a 0.00 partout a 2.0 ;
    - "soft-light" n'existe pas dans Inkscape 1.2, le grain y disparait.
      D'ou "overlay" partout.
-->

<defs>
{GRAIN_CIEL}

{GRAIN_VERT}

{GRAIN_MER}

{GRAIN_HAIE}

{GRAIN_TOTAL}

{GRAIN_DOUX}

  <!-- Le degrade qui commande la montee du grain du ciel : presque nul en
       haut, complet en bas, la ou la verdure vient s'appuyer. Un filtre SVG
       ne sait pas varier dans l'espace ; on superpose donc l'aplat nu et le
       meme aplat graine, masque par ce degrade. -->
  <linearGradient id="degradeGrain" gradientUnits="userSpaceOnUse"
                  x1="0" y1="0" x2="0" y2="{CB}">
    <stop offset="0"    stop-color="#111111"/>
    <stop offset="0.45" stop-color="#8A8A8A"/>
    <stop offset="1"    stop-color="#FFFFFF"/>
  </linearGradient>
  <mask id="masqueGrain">
    <rect x="0" y="0" width="{L}" height="{H}" fill="url(#degradeGrain)"/>
  </mask>

  <!-- Les silhouettes, dupliquees pour servir de decoupe aux seconds tons -->
  <clipPath id="coupeNuage1">{N1}</clipPath>
  <clipPath id="coupeNuage2">{N2}</clipPath>
  <clipPath id="coupeNuage3">{N3}</clipPath>
{COUPES}
{COUPES_ABRIS}
</defs>


<!-- ################## COUCHE 1 - LE CIEL ################## -->
<g inkscape:groupmode="layer" inkscape:label="COUCHE 1 - Le ciel" id="couche1">

  <g inkscape:groupmode="layer" inkscape:label="01 Aplat" id="palier01">
    <rect x="0" y="0" width="{L}" height="{H}" fill="{CIEL}"/>
    <g mask="url(#masqueGrain)">
      <rect x="0" y="0" width="{L}" height="{H}" fill="{CIEL}"
            filter="url(#grainCiel)"/>
    </g>
  </g>

  <!-- DEUX TONS. Le nuage entier est pose dans le ton froid, puis la MEME
       silhouette decalee VERS LE HAUT et decoupee par elle-meme est repeinte
       en blanc : il reste une bande froide sous le nuage. La verdure fait
       l'inverse - decalage vers le bas, bande claire au-dessus - parce qu'un
       nuage se voit par en dessous et une haie par au-dessus. -->
  <g inkscape:groupmode="layer" inkscape:label="02 Nuages" id="palier02"
     filter="url(#grainCiel)">
    <g inkscape:label="Nuage 1" transform="translate({DX1:.1f},0)">
      <g fill="{NF}">{N1}</g>
      <g clip-path="url(#coupeNuage1)" fill="{NC}"
         transform="translate(0,-{D1:.0f})">{N1}</g>
    </g>
    <g inkscape:label="Nuage 2" transform="translate({DX2:.1f},0)">
      <g fill="{NF}">{N2}</g>
      <g clip-path="url(#coupeNuage2)" fill="{NC}"
         transform="translate(0,-{D2:.0f})">{N2}</g>
    </g>
    <g inkscape:label="Nuage 3" transform="translate({DX3:.1f},0)">
      <g fill="{NF}">{N3}</g>
      <g clip-path="url(#coupeNuage3)" fill="{NC}"
         transform="translate(0,-{D3:.0f})">{N3}</g>
    </g>
  </g>

</g>


<!-- ################## LE GRILLAGE ################## -->
<!-- Entre le ciel et la verdure : la cloture est derriere la haie, dont le
     pied la masquera. Voir grillage.py pour la projection.

     Un <pattern> SVG ne pouvait pas convenir : il se repete a pas CONSTANT,
     alors que des poteaux regulierement espaces dans le monde ne le sont pas
     a l'ecran - leur ecart decroit comme 1/z. Le probleme etait arithmetique,
     pas graphique. Ici tout descend d'un seul facteur s(u) = 1/(1 + k.u),
     applique depuis le point de fuite aux deux coordonnees.

     Mesure : le premier poteau fait {HP0} px de haut, le seizieme {HP15}. Et
     leur ecart passe de {EC0} px a {EC15}. C'est ca, la perspective. -->
<g inkscape:groupmode="layer" inkscape:label="GRILLAGE" id="grillage">

{FENCE}

</g>


<!-- ################## COUCHE 2 - LA VERDURE ################## -->
<!-- La crete n'est pas une vague mais une suite de LOBES : trois cents
     disques semes le long de trois lignes, rayons et hauteurs tires au sort
     sur une graine fixe (voir verdure.py). Une sinusoide reguliere se lit
     comme de l'eau ; ce desordre mesure fait le feuillage. -->
<g inkscape:groupmode="layer" inkscape:label="COUCHE 2 - La verdure"
   id="couche2" filter="url(#grainHaie)">

{FEUILLAGE}

</g>


<!-- ################## COUCHE 3 - LE SABLE ################## -->
<!-- UN APLAT PUR. Pas de grain, pas de creux, pas de second ton. Seul son
     bord superieur ondule, et tres peu : le sable n'a ni feuilles ni vagues,
     sa limite est une limite au sol. C'est le contraste entre ce bord calme
     et les lobes de la haie qui fait lire deux matieres. -->
<g inkscape:groupmode="layer" inkscape:label="COUCHE 3 - Le sable" id="couche3">
  <g inkscape:groupmode="layer" inkscape:label="06 Aplat" id="palier06">
    <path fill="{SABLE}" d="{BORD}"/>
  </g>
</g>


<!-- ################## LE VERT AU SOL ################## -->
<!-- Trois morceaux : la verge du pied de haie, les deux coins d'herbe en
     bas - et entre eux le sable passe jusqu'au bord. Les brins penchent
     tous vers la droite : le vent est commun, le fouillis individuel. -->
<g inkscape:groupmode="layer" inkscape:label="COUCHE 3b - Le vert au sol"
   id="coucheSolVert">

{SOL_VERT}

</g>


<!-- ################## LA SERVIETTE ################## -->
<!-- Posee sur le sable et SOUS le parasol : le mat doit passer par-dessus,
     sinon il a l'air plante devant la serviette au lieu d'a travers. -->
<g inkscape:groupmode="layer" inkscape:label="COUCHE 4 - La serviette"
   id="coucheServiette">

{SERVIETTE}

</g>


<!-- ################## LES ABRIS DE PLAGE ################## -->
<!-- Des coupoles a FUSEAUX, pas des eventails. Les coutures sont reparties
     en azimut, pas en largeur apparente : une couture a l'azimut phi tombe
     sur le bord en x = cx + rx.sin(phi), et le sinus fait le travail. Les
     fuseaux mesurent ici 14 px sur les bords et 82 au centre - c'est ce
     resserrement qui donne le volume. A largeurs egales, on obtient une roue
     de loterie. Voir parasols.py. -->
<!-- Aucun filtre sur ce calque : le grain est porte par le groupe des
     fuseaux, a l'interieur de chaque parasol. Le mat, l'ombre et l'embout
     doivent rester NETS - un trait sombre de 9 px de large qu'on graine ne
     se lit pas comme une matiere mais comme une pixellisation. -->
<g inkscape:groupmode="layer" inkscape:label="COUCHE 4 - Les parasols"
   id="couche4">

{ABRIS}

</g>


<!-- ################## L'ENFANT ################## -->
<!-- Dans le vocabulaire de la reference : aucun visage - les personnages y
     sont lisibles par leur seule posture - des membres traces au trait a
     bouts ronds, deux tons de peau sans degrade, un seul accent sature (le
     short), et un accessoire qui raconte le geste. Voir enfant.py. -->
<g inkscape:groupmode="layer" inkscape:label="COUCHE 5 - L'enfant"
   id="couche5" filter="url(#grainDoux)">

{GAMIN}

</g>


<!-- ################## LA MER ################## -->
<!-- Au PREMIER PLAN, donc dessinee en dernier : dans le modele la mer est
     devant tout le reste, et rien ne passe par-dessus. Son bord haut est une
     onde longue et basse - deux cretes sur la largeur - dont chaque
     demi-periode est une seule cubique. Voir mer.py. -->
<g inkscape:groupmode="layer" inkscape:label="COUCHE 6 - La mer" id="couche6"
   filter="url(#grainMer)">

{MER}

</g>


<!-- ################## L'HERBE ################## -->
<!-- Le premier plan : une bande de brins au bas de l'image, PAR-DESSUS le
     sable. Des traits, pas des masses - c'est la forme elementaire qui
     distingue l'herbe de la haie. Voir herbe.py. -->
<g inkscape:groupmode="layer" inkscape:label="COUCHE 7 - L'herbe"
   id="coucheHerbe">

{HERBE}

</g>


<!-- ################## LES PERSONNAGES ################## -->
<!-- Des silhouettes : une couleur corail, aucun visage, un accent par
     figure. Toute la lecture est dans la posture. Voir personnages.py. -->
<g inkscape:groupmode="layer" inkscape:label="COUCHE 8 - Les personnages"
   id="couchePersonnages">

{PERSONNAGES}

</g>


<!-- ################## LE GRAIN ################## -->
<!-- UN SEUL calque, par-dessus tout le reste : meme densite et meme taille
     de point sur le ciel, le feuillage et le sable. C'est ce que fait la
     reference, et c'est ce qui lui donne son unite. Voir grain_global(). -->
<g inkscape:groupmode="layer" inkscape:label="LE GRAIN" id="coucheGrain">
  <rect x="0" y="0" width="{L}" height="{H}" fill="#808080"
        filter="url(#grainGlobal)"/>
</g>

</svg>
""".format(L=LARGEUR, H=HAUTEUR, CB=CIEL_BAS,
           CIEL=CIEL, NC=NUAGE_CLAIR,
           NF=NUAGE_FROID, SABLE=SABLE, N1=NUAGE1, N2=NUAGE2, N3=NUAGE3,
           D1=DEC1, D2=DEC2, D3=DEC3,
           DX1=DX1, DX2=DX2, DX3=DX3,
           BORD=BORD_SABLE, COUPES=coupes, FEUILLAGE=feuillage,
           FENCE=fence, ABRIS=abris, COUPES_ABRIS=coupes_abris,
           GAMIN=GAMIN, SERVIETTE=SERVIETTE,
           SOL_VERT=(herbe.sol_vert(LARGEUR, HAUTEUR, HAIE_PIED)
                     if AVEC_SOL_VERT
                     else '  <!-- sol vert retire -->'),
           PERSONNAGES=(personnages.engendrer(LARGEUR, HAUTEUR)
                        if AVEC_PERSONNAGES
                        else (bloc_serviette_rayee()
                              if AVEC_SERVIETTE_RAYEE
                              else '  <!-- personnages retires -->')),
           HERBE=(herbe.engendrer(LARGEUR, HAUTEUR, PART_HERBE)[0]
                  if AVEC_HERBE else '  <!-- herbe retiree -->'),
           HP0="%.0f" % (grillage.projeter(0,0)[1]-grillage.projeter(0,1)[1]),
           HP15="%.0f" % (grillage.projeter(15,0)[1]-grillage.projeter(15,1)[1]),
           EC0="%.0f" % (grillage.projeter(1,0)[0]-grillage.projeter(0,0)[0]),
           EC15="%.0f" % (grillage.projeter(16,0)[0]-grillage.projeter(15,0)[0]),
           GRAIN_CIEL=grain("grainCiel", 8, "1.05",
                            "Le grain du ciel. Son intensite est celle du BAS "
                            "du ciel ; le\n       degrade ci-dessous le fait "
                            "monter depuis presque rien."),
           GRAIN_DOUX=mouchetis("grainTissu", 77, "0.15",
                                "Le grain du VETEMENT. Dans la reference le "
                                "maillot est graine\n       comme le decor ; "
                                "un aplat nu au milieu d'une image\n"
                                "       entierement grainee se remarque tout "
                                "de suite.")
                      + "\n\n"
                      + mouchetis("grainDoux", 61, "0.13",
                                "Le grain de l'enfant. Sa peau est de valeur "
                                "moyenne, comme le\n       vert de la toile : "
                                "meme reglage, meme resultat.")
                      + "\n\n"
                      + mouchetis("grainToileVive", 44, "0.38",
                                "Le grain du VERT de la toile. Cale sur le "
                                "MODELE, pas sur le ciel :\n       11.9 niveaux "
                                "d'ecart-type mesures, contre 3.9 avant.\n"
                                "       La reference charge les aplats satures "
                                "bien plus que ses fonds.")
                      + "\n\n"
                      + mouchetis("grainToileBlanche", 44, "1.00",
                                  "Le grain du BLANC de la toile. Trois fois "
                                  "plus fort que celui du\n       vert, pour "
                                  "un resultat IDENTIQUE : a reglage egal le "
                                  "vert\n       recoit trois fois plus de "
                                  "grain que le blanc. Deux reglages\n"
                                  "       differents sont la seule facon "
                                  "d'obtenir la meme matiere\n       sur les "
                                  "deux couleurs d'un meme objet."),
           MER=(mer.bloc(LARGEUR, HAUTEUR, indent=2) if AVEC_MER
                else '  <!-- mer retiree -->'),
           GRAIN_MER=mouchetis("grainMer", 31, "0.38",
                               "Le grain de la MER. Meme force que la toile "
                               "verte du parasol :\n       la reference "
                               "charge ses aplats satures de la meme facon."),
           GRAIN_TOTAL=grain_global("grainGlobal", 3, GRAIN_FORCE,
                                    GRAIN_FINESSE,
                                    "Le grain, pose sur toute l'image d'un seul bloc."),
           GRAIN_HAIE=mouchetis("grainHaie", 12, "0.42",
                                "Le grain de la HAIE. La reference y montre une "
                                "matiere tres\n       piquee, plus forte encore que "
                                "sur la toile des parasols."),
           GRAIN_VERT=grain("grainVert", 21, "0.50",
                            "Le grain de la verdure, deux fois plus doux que "
                            "celui du ciel.\n       A intensite egale le vert "
                            "sombre recevrait 15%% de contraste,\n       "
                            "c'est-a-dire de la neige ; a 0.50 il en recoit "
                            "9%%."))

def ecrire(nom, contenu):
    """
    Ecrit le fichier - SAUF s'il a ete modifie a la main depuis la derniere
    generation. Dans ce cas il est laisse intact et la nouvelle version part
    a cote, sous un autre nom.

    Le script garde l'empreinte de ce qu'il a ecrit dans .empreintes.json. Si
    l'empreinte du fichier trouve ne correspond plus, c'est que quelqu'un y a
    touche - Inkscape, un editeur, peu importe - et ce quelqu'un a la
    priorite. Un travail fait a la main ne se rattrape pas ; une generation,
    si : elle prend une seconde.
    """
    import hashlib
    import json
    suivi = ".empreintes.json"
    try:
        connues = json.load(open(suivi))
    except Exception:
        connues = {}

    if os.path.exists(nom):
        actuelle = hashlib.sha1(open(nom, "rb").read()).hexdigest()
        if connues.get(nom) and connues[nom] != actuelle:
            secours = nom.replace(".svg", "_nouveau.svg")
            open(secours, "w").write(contenu)
            print("!! %s A ETE MODIFIE A LA MAIN - je n'y touche pas." % nom)
            print("   La nouvelle version est dans %s." % secours)
            print("   Compare les deux, garde ce que tu veux, puis efface")
            print("   la ligne \"%s\" de %s pour repartir." % (nom, suivi))
            return False

    open(nom, "w").write(contenu)
    connues[nom] = hashlib.sha1(contenu.encode("utf-8")).hexdigest()
    json.dump(connues, open(suivi, "w"), indent=0, sort_keys=True)
    return True


if __name__ == "__main__":
    nom = "scene.svg" if AVEC_GRILLAGE else "scene_sans_grillage.svg"
    if ANIME:
        nom = "scene_anim.svg"
        open(nom, "w").write(SVG.encode("utf-8") if str is bytes else SVG)
        sys.exit(0)
    if not ecrire(nom, SVG):
        raise SystemExit(1)
    print("%s construit" % nom)
    print("  personnage : %s" % SOURCE_PERSONNAGE)
    print("  horizon a y=%d" % CIEL_BAS)
    print("  mode : %s" % ("VUE DE FACE" if P.FRONTAL else "perspective"))
    import mer as _m
    print("  ciel   0 -> %d      (%.0f%%)" % (CIEL_BAS, 100.0*CIEL_BAS/HAUTEUR))
    print("  sable  %d -> %.0f  (%.0f%%)"
          % (CIEL_BAS, _m.MOYENNE - _m.AMPLITUDE,
             100.0*(_m.MOYENNE - _m.AMPLITUDE - CIEL_BAS)/HAUTEUR))
    print("  mer    %.0f -> %d  (%.0f%% a la crete)"
          % (_m.MOYENNE - _m.AMPLITUDE, HAUTEUR,
             100.0*(HAUTEUR - _m.MOYENNE + _m.AMPLITUDE)/HAUTEUR))
    print("  %d ondulations, creux sur les deux bords" % _m.CRETES)
    print("  %d abris" % nb_abris)
