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


def serviette_rayee(ox, oy, k=1.3, indent=4):
    u"""
    La serviette rayee, regardee de pres cette fois.

    CE QUE MONTRE LE MODELE
      Des rayures CONTINUES, FINES et SERREES : une dizaine sur la hauteur
      du tapis, a trame presque egale - autant de vert que de blanc. De
      loin, le tapis lit VERT RAYE ; ma version a tirets espaces sur fond
      creme lisait creme taponne de vert, rien a voir.

      Et le tapis n'est pas un rectangle : un leger BIAIS en
      parallelogramme - le bord haut decale vers la droite - le couche au
      sol sans vraie perspective, comme la serviette de la premiere
      reference etait inclinee d'un degre et demi.

    RELEVE (1232 x 928) : ~210 x 44 px, soit 0.17 x 0.047 du cadre ;
    une dizaine de rayures -> un pas d'environ 4.4 px la-bas, 6.5 ici.
    """
    e = " " * indent
    L2, H = 118.0, 50.0          # demi-longueur, hauteur
    BIAIS = 10.0                 # le decalage du bord haut, vers la droite

    def P(x, y):
        # y va de 0 (bord pres) a -H (bord loin) ; le decalage suit
        return (ox + (x + BIAIS * (-y / H)) * k, oy + y * k)

    coins = [P(-L2, -H), P(L2, -H), P(L2, 0), P(-L2, 0)]
    out = [u'<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f Z" '
           u'fill="%s"/>'
           % (coins[0][0], coins[0][1], coins[1][0], coins[1][1],
              coins[2][0], coins[2][1], coins[3][0], coins[3][1], CREME)]

    # NEUF rayures continues : le pas vaut H/10, le trait la moitie du pas -
    # autant de vert que de blanc, c'est la trame du modele.
    n = 9
    pas = H / (n + 1.0)
    for i in range(1, n + 1):
        y = -H + pas * i
        A, Bp = P(-L2, y), P(L2, y)
        out.append(u'<path d="M%.1f %.1f L%.1f %.1f" stroke="%s" '
                   u'stroke-width="%.1f" fill="none"/>'
                   % (A[0], A[1], Bp[0], Bp[1], VERT_OBJET, pas * 0.52 * k))

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
