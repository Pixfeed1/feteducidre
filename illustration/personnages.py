# -*- coding: utf-8 -*-
u"""
Les personnages de la cinquieme reference.

CE QUI LES REND SIMPLES, ET POURQUOI CA MARCHE
  Ce sont des SILHOUETTES : une seule couleur corail, aucun visage, aucun
  doigt, et un seul accent par figure (le short, le haut clair). Toute la
  lecture passe par la POSTURE - c'est exactement ce que la reference fait
  de mieux, et c'est ce qui les rend reproductibles par le code la ou notre
  premier enfant detaille avait echoue.

LES TROIS FIGURES
  1. le COUREUR : penche en avant, une jambe arriere tendue, le bras tendu
     vers le ballon qui roule devant lui, sa petite pelle a la main ;
  2. le COUPLE assis sur la serviette rayee, vus de dos trois-quarts, lui
     appuye sur ses bras, elle le haut clair ; l'ombre du groupe s'etale a
     droite sur le sable ;
  3. l'ENFANT PENCHE qui creuse, fesses hautes, la pelle plantee, son seau
     pose a cote.

LA FABRICATION
  Chaque membre est un fusele (trace.py) LISSE par Inkscape (booleen.py) :
  sans le lissage, les contours sortent en polygones - le defaut Paint,
  paye une fois, jamais deux. Le ballon est un cercle creme dont les
  quartiers rouges sont des INTERSECTIONS avec des bandes inclinees : le
  bord du quartier est le bord du ballon, par construction.
"""

import math

import booleen as B
import trace as T

PEAU = "#DC5240"            # le corail des silhouettes
PEAU_SOMBRE = "#B93E2E"     # le short des enfants
SHORT_HOMME = "#44584A"     # le short sombre du pere
HAUT_FEMME = "#C7D3C6"      # le haut clair de la mere
VERT_OBJET = "#3F8A52"      # pelle, seau, rayures de la serviette
CREME = "#F2ECD9"           # le blanc casse du ballon et de la serviette
ROUGE_BALLON = "#D8402E"
OMBRE_SOL = "#CBC6A6"       # l'ombre portee, olive comme sur le modele


def _bande(cx, cy, angle, longueur, largeur):
    u"""Un rectangle penche, pour decouper les quartiers du ballon."""
    a = math.radians(angle)
    ux, uy = math.cos(a), math.sin(a)
    vx, vy = -uy, ux
    l2, w2 = longueur / 2.0, largeur / 2.0
    pts = [(cx + ux * l2 + vx * w2, cy + uy * l2 + vy * w2),
           (cx + ux * l2 - vx * w2, cy + uy * l2 - vy * w2),
           (cx - ux * l2 - vx * w2, cy - uy * l2 - vy * w2),
           (cx - ux * l2 + vx * w2, cy - uy * l2 + vy * w2)]
    return ("M%.1f %.1f " % pts[0]
            + " ".join("L%.1f %.1f" % p for p in pts[1:]) + " Z")


def _aides(ox, oy, k):
    def pose(d, couleur):
        return u'<path d="%s" fill="%s"/>' % (B.placer(d, ox, oy, k), couleur)

    def membre(controle, profil, couleur, avec=None):
        d = T.fusele(controle, profil)
        if avec:
            d = B.union(d, avec)
        return pose(B.lisser(d), couleur)

    def rond(c, r, couleur):
        return (u'<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>'
                % (ox + c[0] * k, oy + c[1] * k, r * k, couleur))

    def ellipse(c, rx, ry, couleur, opacite=None):
        o = u' opacity="%.2f"' % opacite if opacite else u''
        return (u'<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" '
                u'fill="%s"%s/>' % (ox + c[0] * k, oy + c[1] * k,
                                    rx * k, ry * k, couleur, o))
    return pose, membre, rond, ellipse


def coureur(ox, oy, k=1.3, indent=4):
    u"""
    L'enfant qui court apres le ballon, sa pelle a la main.

    Tout le mouvement est dans TROIS obliques paralleles : le torse penche,
    la jambe arriere tendue, le bras tendu vers l'avant. Un coureur dont le
    torse est droit ne court pas, il marche vite.
    """
    pose, membre, rond, ellipse = _aides(ox, oy, k)
    e = " " * indent
    out = [ellipse((10, 2), 46, 7, OMBRE_SOL, 0.55)]

    # la jambe ARRIERE, tendue - c'est elle qui raconte la foulee
    # le genou plie, le talon leve : une jambe arriere qui traine par terre
    # ne court pas, elle glisse
    out.append(membre([(-2, -52), (-16, -42), (-30, -28), (-38, -14)],
                      [(0.0, 17), (0.5, 12), (1.0, 8)], PEAU,
                      avec=B.ellipse(-42, -13, 8.5, 5)))
    # la jambe AVANT, repliee sous le corps
    out.append(membre([(2, -52), (14, -42), (24, -26), (30, -8)],
                      [(0.0, 17), (0.5, 12), (1.0, 8)], PEAU,
                      avec=B.ellipse(34, -6, 9, 5)))
    # le torse, penche dans la course
    out.append(membre([(-2, -50), (4, -72), (10, -88), (14, -102)],
                      [(0.0, 30), (0.6, 26), (1.0, 20)], PEAU))
    # le bras ARRIERE, rejete derriere
    out.append(membre([(8, -96), (0, -89), (-8, -80), (-14, -70)],
                      [(0.0, 10), (1.0, 7)], PEAU, avec=B.ellipse(-16, -68, 5, 5)))
    # le bras AVANT, tendu vers le ballon
    out.append(membre([(16, -94), (27, -89), (38, -83), (46, -76)],
                      [(0.0, 10), (1.0, 7)], PEAU, avec=B.ellipse(49, -74, 5.5, 5.5)))
    # la tete, et le petit chignon du modele
    out.append(rond((20, -114), 15, PEAU))
    out.append(rond((8, -124), 5.5, PEAU))

    # le short, l'accent vert sombre du modele
    # un short couvre la hanche, pas le ventre : au premier essai il
    # mangeait la moitie du torse et l'enfant portait une couche
    out.append(pose("M-14 -58 C-9 -63 7 -63 12 -56 C13 -49 10 -44 4 -42 "
                    "C-3 -41 -11 -43 -13 -49 Z", VERT_OBJET))

    # la pelle, dans la main avant
    out.append(pose(B.lisser(B.union(
        T.fusele([(49, -74), (51, -69), (54, -64), (56, -60)],
                 [(0.0, 4), (1.0, 3.5)]),
        "M52 -62 C50 -55 54 -50 60 -53 C64 -56 62 -61 57 -63 Z")),
        VERT_OBJET))

    # LE BALLON. Un cercle creme ; ses quartiers rouges sont des
    # intersections avec deux bandes inclinees - leur bord est donc
    # exactement le bord du ballon.
    # Les panneaux rouges sont des CROISSANTS : le cercle moins le meme
    # cercle decale vers le centre. Deux bandes qui se croisent faisaient
    # une croix de pharmacie, pas un ballon de plage.
    balle = B.ellipse(86, -18, 16, 16)
    out.append(pose(balle, CREME))
    out.append(pose(B.difference(balle, B.ellipse(78, -18, 16.5, 17.5)),
                    ROUGE_BALLON))
    out.append(pose(B.difference(balle, B.ellipse(94, -18, 16.5, 17.5)),
                    ROUGE_BALLON))

    return u"%s<g inkscape:label=\"Coureur\">\n%s\n%s</g>" % (
        e, "\n".join(u"%s  %s" % (e, x) for x in out), e)


def enfant_penche(ox, oy, k=1.3, indent=4):
    u"""
    L'enfant qui creuse : fesses hautes, torse plonge, pelle plantee.
    La posture entiere tient dans l'angle droit entre les jambes verticales
    et le torse presque horizontal.
    """
    pose, membre, rond, ellipse = _aides(ox, oy, k)
    e = " " * indent
    out = [ellipse((8, 2), 40, 6, OMBRE_SOL, 0.55)]

    # les deux jambes, droites - l'enfant est plie aux hanches, pas aux
    # genoux
    out.append(membre([(-8, -62), (-9, -42), (-10, -22), (-11, -4)],
                      [(0.0, 14), (1.0, 8)], PEAU, avec=B.ellipse(-15, -3, 8, 4.5)))
    out.append(membre([(4, -62), (4, -42), (4, -22), (4, -4)],
                      [(0.0, 14), (1.0, 8)], PEAU, avec=B.ellipse(8, -3, 8, 4.5)))
    # le torse, plonge en avant
    out.append(membre([(-2, -64), (12, -74), (28, -79), (42, -77)],
                      [(0.0, 26), (0.6, 22), (1.0, 18)], PEAU))
    # la tete, basse
    out.append(rond((52, -70), 12, PEAU))
    # le bras qui tient la pelle, tendu vers le sable
    out.append(membre([(36, -72), (38, -59), (40, -45), (41, -32)],
                      [(0.0, 9), (1.0, 6)], PEAU, avec=B.ellipse(42, -28, 4.5, 4.5)))

    # le short
    out.append(pose("M-16 -72 C-9 -78 9 -78 14 -71 L11 -55 "
                    "C3 -51 -8 -51 -13 -55 Z", PEAU_SOMBRE))

    # la pelle, plantee dans le sable
    out.append(pose(B.lisser(B.union(
        T.fusele([(42, -28), (43, -21), (45, -14), (46, -8)], [(0.0, 4.5), (1.0, 4)]),
        "M40 -10 C37 -1 43 5 50 2 C56 -2 54 -9 48 -12 Z")),
        VERT_OBJET))

    # le seau pose a cote, avec son anse - la version miniature du seau
    # qu'on avait construit par booleens
    corps = ("M-46 -26 C-45 -16 -44 -8 -42 -3 C-40 0 -26 0 -24 -3 "
             "C-22 -8 -21 -16 -20 -26 Z")
    out.append(pose(B.union(corps, B.ellipse(-33, -26, 13, 4)), PEAU_SOMBRE))
    anneau = B.difference(B.ellipse(-33, -26, 13.5, 13.5),
                          B.ellipse(-33, -26, 10.5, 10.5))
    out.append(pose(B.difference(anneau, B.boite(-50, -26, -16, -8)),
                    PEAU_SOMBRE))

    return u"%s<g inkscape:label=\"Enfant qui creuse\">\n%s\n%s</g>" % (
        e, "\n".join(u"%s  %s" % (e, x) for x in out), e)


def serviette_rayee_corps(dx, dy):
    u"""(remplace par serviette_rayee ci-dessous - conserve pour le couple)"""
    return u''


def _catmull(points):
    u"""
    Une courbe LISSE passant par tous les points : Catmull-Rom converti en
    cubiques. Des segments droits entre echantillons referaient le defaut
    Paint ; ici la tangente en chaque point est la corde de ses voisins.
    """
    p = [points[0]] + list(points) + [points[-1]]
    d = u"M%.1f %.1f" % p[1]
    for i in range(1, len(p) - 2):
        c1 = (p[i][0] + (p[i + 1][0] - p[i - 1][0]) / 6.0,
              p[i][1] + (p[i + 1][1] - p[i - 1][1]) / 6.0)
        c2 = (p[i + 1][0] - (p[i + 2][0] - p[i][0]) / 6.0,
              p[i + 1][1] - (p[i + 2][1] - p[i][1]) / 6.0)
        d += u" C%.1f %.1f %.1f %.1f %.1f %.1f" % (c1 + c2 + p[i + 1])
    return d


def _catmull_ferme(points):
    u"""
    La meme courbe lisse que _catmull, mais FERMEE : le dernier point se
    raccorde au premier avec la meme continuite. Pour les silhouettes en
    aplat - un contour ferme fait de segments droits refait le defaut
    Paint, et une fermeture en ligne droite fait un coin qui se voit.
    """
    n = len(points)
    p = list(points)
    d = u"M%.1f %.1f" % p[0]
    for i in range(n):
        p0 = p[(i - 1) % n]
        p1 = p[i]
        p2 = p[(i + 1) % n]
        p3 = p[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
        d += u" C%.1f %.1f %.1f %.1f %.1f %.1f" % (c1 + c2 + p2)
    return d + " Z"


# ---------------------------------------------------------------------
#  L'HOMME DE LA SERVIETTE - decalque au pixel sur la 5e reference
# ---------------------------------------------------------------------
#
# LE RELEVE (reference 1232 x 928). Son point d'assise est (905, 800) ;
# toutes les coordonnees locales sont des ecarts a ce point, en pixels de
# la reference - le facteur k les amene a notre echelle (1350/928 fois le
# 0.85 de la serviette).
#
#   pose          appuye en arriere, l'appui derriere lui, genoux releves,
#                 il regarde a droite ; la main a plat, doigts vers le mat
#   deux peaux    le buste est A L'OMBRE de la toile (#BF4020), les jambes
#                 depassent AU SOLEIL (#E95028) - c'est la toile qui coupe
#                 la couleur, pas l'anatomie
#   une encre     cheveux et short dans le meme vert-noir (#203014), et le
#                 short CONTINUE sous les genoux en ombre portee : dans la
#                 reference c'est une seule masse sombre
#
PEAU_OMBRE_H = "#BF4020"    # buste, bras, tete - sous la toile
PEAU_SOLEIL_H = "#E95028"   # cuisses, tibias, pieds - au soleil
ENCRE_H = "#203014"         # cheveux ET short - la meme encre
OMBRE_SERVIETTE = "#2E5E50"  # son ombre sur le tissu - sarcelle profond

# Les contours DECALQUES de la reference (masques de couleur, ouverture
# morphologique contre les mouchetures du grain, suivi de bord,
# simplification Douglas-Peucker). Coordonnees locales en pixels de la
# reference, relatives au point d'assise (905, 800).
#
# CE QUI N'EST PAS A LUI, appris en se trompant : la MAIN de la femme se
# plante juste sous son tibia - le paquet orange en bas a droite est a
# elle, pas un pied a lui. Ses jambes a lui disparaissent sous l'encre
# (l'ombre sous ses genoux) puis sous cette main : le decalque s'arrete
# donc sur l'encre, et elle reviendra avec la femme.

_H_SILHOUETTE = [  # 27 points
    (5.0, -78.0),
    (0.0, -74.0),
    (-3.0, -68.0),
    (-8.0, -67.0),
    (-7.0, -62.0),
    (-9.0, -60.0),
    (-17.0, -58.0),
    (-24.0, -23.0),
    # la main a plat, re-relevee au zoom x30 (crop 860-905 x 780-812) :
    # l'avant-bras descend, le poignet plie, la paume s'etend vers le mat
    # sur 15 px et finit en bout arrondi - pas un moignon de 4 points
    (-27.5, -12.0),
    (-28.4, -7.0),      # l'avant-bras tombe presque vertical...
    (-28.9, -5.4),      # LE DECROCHE DU POIGNET : deux paires de points
    (-29.8, -4.7),      # serres verrouillent l'angle - sans elles le
    (-33.8, -3.6),      # Catmull chanfreine le pli en rampe a 45 degres
    (-34.4, -2.6),      # ...et la main est une BARRE posee : dos presque
    (-34.6, -1.0),      # plat, petite face verticale au bout des doigts,
    (-34.1, 0.4),       # finie net - ni pointe ni sabot
    (-31.5, 1.0),       # (point de calme : le dessous ne pique pas du nez)
    (-28.5, 1.3),       # le dessous suit la pente de la rayure
    (-22.0, 2.2),
    (-20.3, -0.5),      # le poignet, cote interieur
    (-18.8, -8.0),
    (-16.0, -25.0),
    (-13.0, -33.0),
    (-9.0, -19.0),
    (-6.0, -15.0),
    (-3.0, -15.0),
    (23.0, -31.0),
    (30.0, -31.0),
    (20.0, -40.0),
    (15.0, -57.0),
    (11.0, -61.0),
    (1.0, -61.0),
    (-1.0, -63.0),
    (-1.0, -65.0),
    (4.0, -68.0),
    (6.0, -73.0),
]
_H_JAMBES_SOLEIL = [  # 7 points
    (47.0, -34.0),
    (56.0, -28.0),
    (61.0, -17.0),
    (50.0, -16.0),
    (50.0, -20.0),
    (42.0, -21.0),
    (31.0, -29.0),
]
_H_SHORT = [  # 13 points
    (23.0, -29.0),
    (33.0, -27.0),
    (45.0, -17.0),
    (36.0, -14.0),
    (36.0, -3.0),
    (34.0, -1.0),
    (26.0, -1.0),
    (19.0, 2.0),
    (10.0, 2.0),
    (1.0, -1.0),
    (-1.0, -3.0),
    (0.0, -5.0),
    (-7.0, -12.0),
]
_H_CHEVEUX = [  # 10 points
    (-4.0, -89.0),
    (-8.0, -88.0),
    (-12.0, -84.0),
    (-13.0, -80.0),
    (-12.0, -72.0),
    (-7.0, -69.0),
    (-5.0, -70.0),
    (-3.0, -70.0),
    (0.0, -76.0),
    (8.0, -82.0),
]


def homme_serviette(ox, oy, k=1.0, indent=4, grande_ombre=True):
    u"""
    L'homme assis de la reference, a l'identique : ses OMBRES d'abord
    (le sarcelle profond releve sur la serviette : #4F806A), puis quatre
    aplats fermes - silhouette a l'ombre de la toile, jambes au soleil,
    encre du short et de l'ombre sous les genoux, encre des cheveux.

    (ox, oy) : le point d'assise sur la serviette. k : l'echelle.
    """
    e = " " * indent

    def aplat(pts, couleur, opacite=None):
        P = [(ox + x * k, oy + y * k) for (x, y) in pts]
        o = u' opacity="%.2f"' % opacite if opacite else u''
        return u'<path d="%s" fill="%s"%s/>' % (_catmull_ferme(P), couleur, o)

    out = []

    # SES OMBRES SUR LE TISSU, decalquees de la reference : la grande
    # tombe a sa DROITE (le soleil vient de gauche dans cette image, comme
    # la toile au-dessus), la petite sous son bras d'appui. Translucides :
    # dans le modele les rayures restent lisibles DANS l'ombre.
    if grande_ombre:
        # sa nappe a lui seul - quand la femme est la, c'est la nappe du
        # COUPLE (dans femme_serviette) qui fait tout le travail
        out.append(aplat([(-10.0, 5.0), (12.0, -6.0), (40.0, -8.0),
                          (68.0, -2.0), (84.0, 7.0), (76.0, 16.0),
                          (48.0, 22.0), (14.0, 19.0), (-4.0, 12.0)],
                         OMBRE_SERVIETTE, 0.55))
    out.append(aplat([(-43.0, 1.5), (-16.0, -0.5), (-11.0, 6.5),
                      (-25.0, 10.5), (-41.0, 8.0)],
                     OMBRE_SERVIETTE, 0.50))

    out.append(aplat(_H_SILHOUETTE, PEAU_OMBRE_H))
    # le cheveu d'ombre sous les doigts - 2 px dans la reference, c'est
    # lui qui colle la main au tissu au lieu de la laisser flotter
    out.append(aplat([(-34.5, 0.7), (-28.0, 1.6), (-21.5, 2.5),
                      (-21.5, 4.0), (-28.0, 3.3), (-34.3, 2.3)],
                     "#234A40", 0.55))
    out.append(aplat(_H_JAMBES_SOLEIL, PEAU_SOLEIL_H))
    out.append(aplat(_H_SHORT, ENCRE_H))
    out.append(aplat(_H_CHEVEUX, ENCRE_H))
    return u"%s<g inkscape:label=\"Homme de la serviette\">\n%s\n%s</g>" % (
        e, "\n".join(u"%s  %s" % (e, x) for x in out), e)


# ---------------------------------------------------------------------
#  LA FEMME DE LA SERVIETTE - meme methode que lui, decalquee au pixel
# ---------------------------------------------------------------------
#
# LE RELEVE (reference 1232 x 928). Son point d'assise est (1010, 800).
#
#   pose         assise, jambes ALLONGEES vers la droite, orteils
#                releves ; le bras gauche plante vers l'homme, la main
#                posee pres de son tibia a lui ; elle regarde a droite
#   bob auburn   #B43F1E couvre la tete, la joue reste en encoche claire
#   debardeur    #659382 - presque la couleur de l'ombre sur le tissu :
#                les fenetres des masques les separent, pas les seuils
#   la peau      en TROIS morceaux (le debardeur et le short la coupent) :
#                jambes + bras droit / bras plante / tete-cou
#   l'ombre      UNE SEULE nappe pour le couple, qui s'etale a droite
#                sur la serviette puis le sable - quand elle est la, la
#                grande ombre de l'homme s'eteint (grande_ombre=False)
#
PEAU_F_JAMBES = "#F35932"   # jambes et bras droit, au soleil
PEAU_F_BRAS = "#E9805B"     # le bras plante, plus clair
PEAU_F_TETE = "#D84A28"     # la base de la tete - la joue en encoche
CHEVEUX_F = "#B43F1E"       # le bob auburn
HAUT_F = "#659382"          # le debardeur teal
SHORT_F = "#142B11"

# composante 0 : 770 px, x 1019..1082, y 745..802
_F_PEAU_0 = [  # 16 points
    (11.0, -55.0),
    (17.0, -49.0),
    (25.0, -22.0),
    (57.0, -8.0),
    (66.0, -19.0),
    (71.0, -11.0),
    (72.0, -1.0),
    (69.0, 1.0),
    (28.0, 1.0),
    (26.0, -1.0),
    (27.0, -8.0),
    (25.0, -14.0),
    (20.0, -15.0),
    (17.0, -18.0),
    (10.0, -32.0),
    (9.0, -53.0),
]
# composante 1 : 455 px, x 952..987, y 745..810
_F_PEAU_1 = [  # 22 points
    (-25.0, -55.0),
    (-30.0, -50.0),
    (-41.0, -16.0),
    (-53.0, -16.0),
    (-55.0, -14.0),
    (-51.0, -7.0),
    (-46.0, -6.0),
    (-47.0, 1.0),
    (-51.0, 3.0),
    (-55.0, 2.0),
    (-58.0, 6.0),
    (-55.0, 10.0),
    (-46.0, 10.0),
    (-41.0, 5.0),
    (-36.0, -8.0),
    (-34.0, -10.0),
    (-30.0, -8.0),
    (-26.0, -13.0),
    (-31.0, -18.0),
    (-26.0, -28.0),
    (-26.0, -43.0),
    (-23.0, -51.0),
]
# composante 2 : 231 px, x 994..1016, y 719..743
_F_PEAU_2 = [  # 11 points
    (-6.0, -81.0),
    (-15.0, -72.0),
    (-16.0, -64.0),
    (-12.0, -62.0),
    (-9.0, -57.0),
    (-5.0, -57.0),
    (-1.0, -59.0),
    (-1.0, -62.0),
    (4.0, -61.0),
    (6.0, -67.0),
    (4.0, -72.0),
]
_F_HAUT = [  # 12 points
    (-14.0, -58.0),
    (-20.0, -57.0),
    (-23.0, -54.0),
    (-27.0, -18.0),
    (-24.0, -15.0),
    (-3.0, -17.0),
    (4.0, -18.0),
    (8.0, -21.0),
    (10.0, -33.0),
    (8.0, -48.0),
    (10.0, -55.0),
    (2.0, -58.0),
]
_F_SHORT = [  # 18 points
    (9.0, -19.0),
    (6.0, -15.0),
    (-3.0, -18.0),
    (-25.0, -15.0),
    (-27.0, -13.0),
    (-29.0, 0.0),
    (-23.0, 4.0),
    (-11.0, 4.0),
    (9.0, 5.0),
    (13.0, 3.0),
    (16.0, 5.0),
    (19.0, 2.0),
    (18.0, -1.0),
    (20.0, 3.0),
    (26.0, -1.0),
    (26.0, -12.0),
    (23.0, -15.0),
    (12.0, -16.0),
]
_F_CHEVEUX = [  # 10 points
    (-6.0, -81.0),
    (-14.0, -73.0),
    (-14.0, -64.0),
    (-8.0, -57.0),
    (-5.0, -57.0),
    (-2.0, -59.0),
    (-3.0, -61.0),
    (2.0, -62.0),
    (5.0, -67.0),
    (1.0, -75.0),
]


def femme_serviette(ox, oy, k=1.0, indent=4):
    u"""
    La femme assise de la reference, a l'identique - memes outils que
    l'homme : contours decalques, Catmull-Rom ferme, ombres d'abord.

    (ox, oy) : le point d'assise sur la serviette. k : l'echelle.
    """
    e = " " * indent

    def aplat(pts, couleur, opacite=None):
        P = [(ox + x * k, oy + y * k) for (x, y) in pts]
        o = u' opacity="%.2f"' % opacite if opacite else u''
        return u'<path d="%s" fill="%s"%s/>' % (_catmull_ferme(P), couleur, o)

    out = []

    # LA NAPPE D'OMBRE DU COUPLE, relevee sur le patch teal du modele :
    # elle part de sous le genou de l'homme, court sous ses jambes a elle
    # et deborde a droite sur le sable, au-dela des orteils.
    # bornee a +92 : plus loin, la nappe sortait du cadre
    out.append(aplat([(-36.0, -2.0), (5.0, 0.0), (42.0, 1.0),
                      (70.0, 0.0), (92.0, 7.0), (86.0, 16.0),
                      (56.0, 17.0), (18.0, 15.0), (-22.0, 10.0)],
                     OMBRE_SERVIETTE, 0.55))

    out.append(aplat(_F_PEAU_0, PEAU_F_JAMBES))    # jambes + bras droit
    out.append(aplat(_F_PEAU_1, PEAU_F_BRAS))      # le bras plante
    out.append(aplat(_F_PEAU_2, PEAU_F_TETE))      # tete et cou
    out.append(aplat(_F_SHORT, SHORT_F))
    out.append(aplat(_F_HAUT, HAUT_F))
    out.append(aplat(_F_CHEVEUX, CHEVEUX_F))
    return u"%s<g inkscape:label=\"Femme de la serviette\">\n%s\n%s</g>" % (
        e, "\n".join(u"%s  %s" % (e, x) for x in out), e)


def _serviette_champ(ox, oy, k):
    u"""
    La geometrie de la serviette, partagee : les quatre coins releves, le
    champ de plis, et point(u, v) qui interpole tout le reste entre eux.
    Extraite de serviette_rayee pour que le MAT puisse demander ou le tissu
    se trouve - sans dupliquer une seule formule.

    LE RELEVE, REFAIT (reference 1232 x 928). Le premier relevé s'arretait
    a l'homme assis : il mesurait la partie VISIBLE a sa gauche et prenait
    son bord pour le bout du tissu - une serviette a plat, une bande. En
    balayant les rayures de toute la zone (filtre : du creme a moins de
    6 px, pour ne pas gober le short), la serviette CONTINUE sous le
    couple jusqu'a x=1130 :

        pointe gauche  W (723, 798)     coin bas    S (888, 834)
        pointe droite  E (1130, 805)    coin haut   N (965, 769)

    N est cache derriere la femme : reconstruit par W + E - S, et le
    parallelogramme se verifie - les deux grands bords portent le meme
    vecteur (242, -29). C'est un LOSANGE en perspective, profond de 84 px
    sur 407 de large, pas une bande horizontale : on voit le DESSUS du
    tissu, pas sa tranche.
    """
    A = (ox - 56.0 * k, oy + 47.0 * k)      # S - coin pres, en bas
    B = (ox + 297.0 * k, oy + 5.0 * k)      # E - la pointe droite
    C = (ox + 56.0 * k, oy - 47.0 * k)      # N - coin loin, cache
    D = (ox - 297.0 * k, oy - 5.0 * k)      # W - la pointe gauche

    # LE PLI EST UNE BOSSE, PAS UNE ONDE. Une sinusoide met ses cretes ou
    # ses phases les posent - la mienne tombait a cote du milieu - et elle
    # descend autant qu'elle monte, ce qu'un tissu pose ne fait pas : il se
    # SOULEVE par endroits, il ne s'enfonce pas sous le sable. Le champ est
    # donc une somme de bosses gaussiennes, toutes vers le haut :
    #   la principale AU MILIEU du tapis - la ou l'on s'assoit -
    #   une secondaire discrete vers la gauche, pour ne pas etre symetrique,
    #   et un fremissement minuscule par-dessus.
    def pli(u):
        # sigma 0.19 et non 0.14 : sur le losange les rayures sont longues,
        # une bosse etroite les faisait serpenter en S serres - un tissu
        # tresse. La reference montre UNE montee douce, pas des vagues.
        bosse1 = math.exp(-((u - 0.50) / 0.19) ** 2)
        bosse2 = math.exp(-((u - 0.21) / 0.09) ** 2)
        frisson = 0.35 * math.sin(2 * math.pi * 3.1 * u + 1.7)
        att = math.sin(math.pi * min(1.0, max(0.0, u))) ** 0.5
        # La regle du septieme : un accident de surface se voit a partir
        # d'un septieme de la hauteur de l'objet. Le losange fait 94 px de
        # profondeur projetee - la bosse suit (14 px, contre 11 quand le
        # tapis n'en faisait que 74).
        return -(14.0 * bosse1 + 5.0 * bosse2 + frisson * att) * k

    def point(u, v):
        gauche = (A[0] + (D[0] - A[0]) * v, A[1] + (D[1] - A[1]) * v)
        droite = (B[0] + (C[0] - B[0]) * v, B[1] + (C[1] - B[1]) * v)
        # la bosse est plus haute sur le bord pres que sur le bord loin :
        # c'est la perspective du relief, comme celle du contour
        return (gauche[0] + (droite[0] - gauche[0]) * u,
                gauche[1] + (droite[1] - gauche[1]) * u
                + pli(u) * (1.12 - 0.45 * v))

    return A, B, C, D, pli, point


def serviette_pose(ox, oy, k=1.0, x=None, v=0.5):
    u"""
    Le y DU TISSU, pli compris, a l'abscisse x et a la fraction v de la
    profondeur (0 = bord pres, 1 = bord loin). C'est la serviette qu'on
    interroge pour poser quoi que ce soit dessus - le mat comme l'homme.
    """
    _, _, _, _, _, point = _serviette_champ(ox, oy, k)
    if x is None:
        x = ox
    lo, hi = 0.0, 1.0                   # x(u, v) est monotone en u
    for _ in range(40):
        mid = (lo + hi) / 2.0
        if point(mid, v)[0] < x:
            lo = mid
        else:
            hi = mid
    return point((lo + hi) / 2.0, v)[1]


def serviette_coupe_mat(ox, oy, k=1.0, x_mat=None):
    u"""
    Le y ou le mat doit S'ARRETER sur la serviette.

    Sur la reference le mat ne se plante pas derriere le tissu : il continue
    PAR-DESSUS les rayures et s'arrete net A HAUTEUR DE LA MAIN posee de
    l'homme (releve : coupe a y=800, main a 795-802) - c'est elle qui
    donne le sens du trait coupe.
    """
    return serviette_pose(ox, oy, k, x_mat, v=0.52)


def serviette_rayee(ox, oy, k=1.0, indent=4):
    u"""
    La serviette rayee : la geometrie relevee coin par coin, et par-dessus
    LE MOUVEMENT DU TISSU.

    LA GEOMETRIE : le losange releve dans _serviette_champ - les quatre
    coins W, S, E, N du parallelogramme, pas la bande plate du premier
    releve tronque par l'homme assis.

    LE MOUVEMENT
      Un tissu pose sur du sable n'a pas une ligne droite : il epouse les
      creux et les plis. Et le point capital est que TOUTES les rayures
      ondulent AUX MEMES ENDROITS - c'est le meme pli qui les souleve
      toutes. Le mouvement est donc UN SEUL champ d(u), commun au contour
      et aux neuf rayures : deux sinusoides lentes, eteintes aux
      extremites pour que les coins releves restent en place. Des
      ondulations independantes par rayure feraient des spaghettis ; des
      rayures droites faisaient un carrelage. Le tissu, c'est le desordre
      COHERENT - la meme lecon que la houle de la haie et le vent de
      l'herbe.
    """
    e = " " * indent
    A, B, C, D, pli, point = _serviette_champ(ox, oy, k)

    N = 16

    def ligne(v):
        return [point(i / float(N), v) for i in range(N + 1)]

    def ruban(v0, v1, couleur):
        haut = ligne(v1)
        bas = ligne(v0)
        d = _catmull(haut)
        d += u" L%.1f %.1f" % bas[-1]
        d += _catmull(list(reversed(bas))).replace("M", "L", 1)
        return u'<path d="%s Z" fill="%s"/>' % (d, couleur)

    out = []

    # L'EPAISSEUR DU TISSU : une ombre fine sous le bord pres, decalee de
    # quelques pixels. Sans elle la serviette est PEINTE sur le sable ;
    # avec elle, elle est POSEE dessus. C'est le detail qui fait la
    # finition - le meme role que le trait au pied du mat.
    bas_ombre = [(x + 2.5, y + 5.0) for (x, y) in ligne(0.0)]
    haut_ombre = [(x + 2.5, y - 6.0) for (x, y) in bas_ombre]
    d_ombre = _catmull(haut_ombre)
    d_ombre += u" L%.1f %.1f" % bas_ombre[-1]
    d_ombre += _catmull(list(reversed(bas_ombre))).replace("M", "L", 1)
    out.append(u'<path d="%s Z" fill="%s" opacity="0.8"/>'
               % (d_ombre, OMBRE_SOL))

    out.append(ruban(0.0, 1.0, CREME))

    # DIX RAYURES DANS LA LONGUEUR - ce que montre la reference : des
    # lignes fines et serrees, paralleles aux grands bords, qui SERPENTENT
    # avec le pli puisqu'elles le traversent. Les bandes transversales de
    # la version precedente etaient une surinterpretation. Des lisieres
    # unies le long des deux grands bords : l'ourlet.
    n = 10
    v_min, v_max = 0.10, 0.90
    pas_v = (v_max - v_min) / (n - 1)
    demi = pas_v * 0.24
    for i in range(n):
        v = v_min + i * pas_v
        out.append(ruban(v - demi, v + demi, VERT_OBJET))

    # L'OMBRE DU PLI : le flanc droit de la bosse principale, celui qui
    # tourne le dos a la lumiere, porte une bande d'ombre translucide en
    # travers du tapis. C'est elle qui transforme la montee des lignes en
    # RELIEF - sans elle les rayures ondulent, avec elle le tissu bombe.
    # Le flanc est echantillonne le long de u pour SUIVRE la bosse - un
    # quadrilatere droit la coupait - et l'ombre est assez dense pour
    # survivre au grain : a 0.30 elle disparaissait dessous.
    fl0, fl1 = 0.52, 0.66
    Np = 6
    haut_f = [point(fl0 + (fl1 - fl0) * i / Np, 0.0) for i in range(Np + 1)]
    bas_f = [point(fl0 + (fl1 - fl0) * i / Np, 1.0) for i in range(Np + 1)]
    d_f = _catmull(haut_f) + u" L%.1f %.1f" % bas_f[-1]
    d_f += _catmull(list(reversed(bas_f))).replace("M", "L", 1)
    out.append(u'<path d="%s Z" fill="#9E9878" opacity="0.38"/>' % d_f)

    return u"%s<g inkscape:label=\"Serviette rayee\">\n%s\n%s</g>" % (
        e, "\n".join(u"%s  %s" % (e, x) for x in out), e)


def couple(ox, oy, k=1.3, indent=4):
    u"""
    Les deux assis sur la serviette rayee, l'ombre etalee a droite.

    LA SERVIETTE RAYEE est le sol du groupe : un parallelogramme couche,
    raye DANS SA LONGUEUR - cinq vertes, quatre cremes. Les rayures sont
    des bandes pleines, pas des traits : a cette echelle un trait fait une
    grille, une bande fait un tissu.
    """
    pose, membre, rond, ellipse = _aides(ox, oy, k)
    e = " " * indent
    out = []

    out.append(serviette_rayee_corps(0, 0))

    # ---- LUI, a gauche, appuye en arriere, genoux releves ---------------
    # Trois choses le font tenir assis : le torse PENCHE en arriere, les
    # genoux RELEVES devant, et le bras d'appui derriere - plus fin et plus
    # court que les jambes, sinon il devient une troisieme jambe.
    mx = -80.0
    # la cuisse monte vers le genou, le tibia redescend vers le pied
    out.append(membre([(mx, -24), (mx + 12, -30), (mx + 24, -28), (mx + 32, -16)],
                      [(0.0, 17), (0.5, 14), (1.0, 10)], PEAU))
    out.append(membre([(mx + 30, -20), (mx + 36, -14), (mx + 40, -8), (mx + 43, -3)],
                      [(0.0, 10), (1.0, 7)], PEAU,
                      avec=B.ellipse(mx + 47, -3, 7.5, 4)))
    # le torse, franchement incline
    out.append(membre([(mx + 2, -22), (mx - 6, -38), (mx - 12, -48), (mx - 16, -56)],
                      [(0.0, 26), (0.5, 24), (1.0, 20)], PEAU))
    # le bras d'appui, derriere
    out.append(membre([(mx - 14, -48), (mx - 22, -34), (mx - 30, -18), (mx - 35, -4)],
                      [(0.0, 7.5), (1.0, 5.5)], PEAU,
                      avec=B.ellipse(mx - 37, -3, 5, 3.5)))
    # la tete, POSEE sur les epaules - pas de cou : c'est lui qui trapu
    out.append(rond((mx - 19, -64), 12, PEAU))
    # le short sombre, a cheval sur la hanche
    out.append(pose("M%.1f %.1f C%.1f %.1f %.1f %.1f %.1f %.1f L%.1f %.1f "
                    "C%.1f %.1f %.1f %.1f %.1f %.1f Z"
                    % (mx - 12, -32, mx - 6, -38, mx + 10, -38, mx + 16, -30,
                       mx + 18, -18, mx + 8, -13, mx - 6, -13, mx - 12, -19),
                    SHORT_HOMME))

    # ---- ELLE, a droite, plus menue, le carre de cheveux ----------------
    fx = 60.0
    # les jambes repliees devant, en un seul mouvement
    out.append(membre([(fx, -20), (fx + 12, -17), (fx + 24, -11), (fx + 33, -4)],
                      [(0.0, 16), (0.6, 12), (1.0, 8)], PEAU,
                      avec=B.ellipse(fx + 37, -3, 7, 4)))
    # le torse au haut clair, droit avec une pointe de cambrure
    out.append(membre([(fx, -20), (fx - 3, -33), (fx - 4, -42), (fx - 5, -50)],
                      [(0.0, 23), (0.5, 21), (1.0, 17)], HAUT_FEMME))
    # le bras, pose sur le genou
    out.append(membre([(fx - 4, -43), (fx + 3, -35), (fx + 10, -27), (fx + 16, -20)],
                      [(0.0, 7), (1.0, 5)], PEAU,
                      avec=B.ellipse(fx + 18, -18, 4.5, 3.5)))
    # la tete sur les epaules, puis le CARRE de cheveux : la calotte
    # au-dessus, la pointe sur la nuque - c'est lui qui dit "elle"
    out.append(rond((fx - 6, -58), 11, PEAU))
    out.append(pose("M%.1f %.1f C%.1f %.1f %.1f %.1f %.1f %.1f "
                    "C%.1f %.1f %.1f %.1f %.1f %.1f "
                    "L%.1f %.1f C%.1f %.1f %.1f %.1f %.1f %.1f Z"
                    % (fx - 18, -57, fx - 20, -66, fx - 14, -72, fx - 6, -72,
                       fx + 2, -72, fx + 7, -66, fx + 6, -59,
                       fx + 4, -52, fx + 1, -56, fx - 8, -57,
                       fx - 18, -57), PEAU_SOMBRE))

    return u"%s<g inkscape:label=\"Couple sur la serviette\">\n%s\n%s</g>" % (
        e, "\n".join(u"%s  %s" % (e, x) for x in out), e)


def engendrer(largeur, hauteur, indent=2):
    u"""
    Les trois groupes, aux places de la reference (fractions du cadre) :
      enfant qui creuse  a gauche, sous le grand parasol
      coureur            au centre, dans le vide entre les deux
      couple             a droite, sous le petit parasol
    """
    k = 1.3
    morceaux = [
        enfant_penche(0.185 * largeur, 0.895 * hauteur, k, indent + 2),
        coureur(0.475 * largeur, 0.900 * hauteur, k, indent + 2),
        couple(0.775 * largeur, 0.885 * hauteur, k, indent + 2),
    ]
    return "\n\n".join(morceaux)


if __name__ == "__main__":
    s = engendrer(1800, 1350)
    print(u"%d chemins, %d cercles" % (s.count("<path"), s.count("<circle")))
