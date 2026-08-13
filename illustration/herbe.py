# -*- coding: utf-8 -*-
u"""
La bande d'herbe au bas de l'image.

RELEVE SUR LA REFERENCE (image de 1232 x 953)
    bord haut de l'herbe    y = 858   ->  0.90 de la hauteur
    la bande occupe donc    0.10 de la hauteur, sur toute la largeur
    teinte                  un vert OLIVE, plus chaud et plus gris que la
                            haie - c'est de l'herbe seche de bord de plage,
                            pas du feuillage

CE QUI FAIT L'HERBE, PAR OPPOSITION A LA HAIE
  La haie est faite de MASSES - touffes, grappes. L'herbe est faite de
  TRAITS : des centaines de petits brins verticaux, legerement inclines,
  qui se lisent un a un sur le bord haut et se fondent en matiere dans le
  corps de la bande. Le meme vocabulaire (des formes semees sur une graine
  fixe), mais la forme elementaire change tout.

LE BORD HAUT N'EST PAS UNE LIGNE
  Ce sont les brins eux-memes qui le font : ils DEPASSENT au-dessus de la
  bande, chacun de sa hauteur propre. Une bande rectiligne surmontee de
  quelques poils ferait une brosse ; ici la limite n'existe que par les
  brins, comme la crete de la haie n'existe que par ses touffes.
"""

import math
import random

BASE = "#8A9A5B"          # le fond de la bande, olive
VERGE = "#A6B172"         # la bande au pied de la haie, plus pale
BRIN_SOMBRE = "#5C6E38"   # les brins a contre-jour
BRIN_CLAIR = "#A5B370"    # les brins eclaires


def brins(y_sol, largeur, pas, h_min, h_max, alea, inclinaison=0.30):
    u"""
    Des traits plantes le long d'une horizontale.

    Chaque brin part du sol et monte, incline d'un angle tire au sort dans
    [-inclinaison, +inclinaison] radians, avec une legere courbure : le
    point de controle est a mi-hauteur, decale de la moitie de l'ecart du
    sommet. Un brin raide est un baton ; c'est cette courbure minuscule qui
    fait l'herbe.
    """
    out, x = [], alea.uniform(0, pas)
    while x < largeur:
        h = alea.uniform(h_min, h_max)
        a = alea.uniform(-inclinaison, inclinaison)
        dx = h * math.tan(a)
        out.append((round(x, 1), round(y_sol, 1),
                    round(x + dx * 0.5, 1), round(y_sol - h * 0.55, 1),
                    round(x + dx, 1), round(y_sol - h, 1)))
        x += alea.uniform(pas * 0.5, pas * 1.5)
    return out


def brins_disperses(y_min, y_max, largeur, nombre, h_min, h_max, alea,
                    inclinaison=0.40, biais=0.0, x0=0.0):
    u"""
    Des brins au pied tire au hasard DANS la bande, pas sur une ligne.

    Deux appels de brins() a hauteur fixe dessinaient deux RANGEES : l'oeil
    voyait les lignes de plantation, comme des poireaux. L'herbe d'une bande
    ne pousse pas en rangs - chaque brin prend son pied ou il veut.
    """
    out = []
    for _ in range(nombre):
        x = x0 + alea.uniform(-4, largeur + 4)
        y = alea.uniform(y_min, y_max)
        h = alea.uniform(h_min, h_max)
        a = biais + alea.uniform(-inclinaison, inclinaison)
        dx = h * math.tan(a)
        out.append((round(x, 1), round(y, 1),
                    round(x + dx * 0.5, 1), round(y - h * 0.55, 1),
                    round(x + dx, 1), round(y - h, 1)))
    return out


def _traits(liste, largeur_trait, indent):
    e = " " * indent
    return "\n".join(
        u'%s<path d="M%s %s Q%s %s %s %s"/>' % ((e,) + b) for b in liste)


def engendrer(largeur, hauteur, part=0.10, indent=2, graine=19):
    u"""
    part : la fraction de la hauteur d'image occupee par la bande.

    Trois plans de brins :
      1. la FRANGE, sur le bord haut - des brins sombres qui depassent dans
         le sable, les plus grands, les plus lisibles ;
      2. les brins SOMBRES du corps, plus courts, qui donnent le fouillis ;
      3. quelques brins CLAIRS par-dessus, la lumiere qui accroche.
    """
    alea = random.Random(graine)
    y_haut = hauteur * (1.0 - part)
    ep = hauteur * part

    e = " " * indent
    morceaux = [
        u'%s<rect x="0" y="%.1f" width="%d" height="%.1f" fill="%s"/>'
        % (e, y_haut, largeur, ep + 2, BASE),

        # LA FRANGE. Premier essai : des brins de 0.28 a 0.62 fois la bande,
        # espaces de 9 px - un PEIGNE, chaque dent lisible une a une. Sur la
        # reference le bord est un DUVET : court, dense, a peine plus haut
        # qu'un dixieme de la bande. C'est la proximite des brins qui fait la
        # matiere, pas leur taille.
        u'%s<g fill="none" stroke="%s" stroke-width="2.8"'
        u' stroke-linecap="round">' % (e, BRIN_SOMBRE),
        _traits(brins(y_haut + ep * 0.08, largeur, 4.6,
                      ep * 0.10, ep * 0.24, alea, 0.42), 2.8, indent + 2),
        u'%s</g>' % e,

        u'%s<g fill="none" stroke="%s" stroke-width="3.0"'
        u' stroke-linecap="round">' % (e, BRIN_SOMBRE),
        _traits(brins_disperses(y_haut + ep * 0.30, y_haut + ep + 6,
                                largeur, int(largeur * 0.36),
                                ep * 0.16, ep * 0.36, alea), 3.0, indent + 2),
        u'%s</g>' % e,

        u'%s<g fill="none" stroke="%s" stroke-width="2.6"'
        u' stroke-linecap="round">' % (e, BRIN_CLAIR),
        _traits(brins_disperses(y_haut + ep * 0.32, y_haut + ep + 6,
                                largeur, int(largeur * 0.20),
                                ep * 0.14, ep * 0.32, alea), 2.6, indent + 2),
        u'%s</g>' % e,
    ]
    corps = "\n".join(morceaux)
    return corps, corps.count("<path")


if __name__ == "__main__":
    corps, n = engendrer(1800, 1350)
    print(u"herbe : %d brins sur une bande de %.0f px" % (n, 1350 * 0.10))


# =====================================================================
#  LE VERT AU SOL de la cinquieme reference - trois morceaux, pas une bande
# =====================================================================
#
# RELEVE (image de 1232 x 928)
#   la VERGE au pied de la haie     y = 0.754 -> 0.803, toute la largeur,
#                                   un olive PALE, presque uni
#   l'herbe des COINS BAS           a gauche de 0 a 0.38 de la largeur,
#                                   a droite de 0.60 au bord ; leur haut
#                                   a 0.93, jusqu'au bas du cadre
#   entre les deux                  RIEN : le sable passe jusqu'au bord.
#                                   C'est ce passage ouvert qui fait entrer
#                                   dans l'image - une bande continue la
#                                   fermait comme un muret.
#
# LE VENT
#   Les brins ne sont pas droits : ils penchent tous vers la DROITE, d'un
#   meme cote, avec leur desordre propre par-dessus. Un biais commun et un
#   alea individuel - comme la houle de la haie : le vent est global, le
#   fouillis est local.

VENT = 0.30               # le biais commun, en radians, vers la droite


def sol_vert(largeur, hauteur, pied_haie, indent=2, graine=23):
    alea = random.Random(graine)
    e = " " * indent
    out = []

    # LA VERGE : une bande plate, sans brins - a cette distance l'herbe
    # n'a plus de texture, c'est le grain global qui fera la matiere.
    # 0.032 et non le 0.048 du releve : notre haie descend deja plus bas
    # que celle du modele (0.81 contre 0.754), une verge pleine hauteur
    # mangeait le sable qui reste.
    verge_h = 0.032 * hauteur
    out.append(u'%s<rect x="0" y="%.1f" width="%d" height="%.1f" fill="%s"/>'
               % (e, pied_haie, largeur, verge_h, VERGE))

    # LES DEUX COINS, avec leur frange au vent.
    y_haut = 0.93 * hauteur
    ep = hauteur - y_haut
    for x0, x1 in ((0.0, 0.38 * largeur), (0.60 * largeur, float(largeur))):
        L = x1 - x0
        out.append(u'%s<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f"'
                   u' fill="%s"/>' % (e, x0, y_haut, L, ep + 2, BASE))
        # le duvet du bord haut, penche par le vent
        out.append(u'%s<g fill="none" stroke="%s" stroke-width="2.8"'
                   u' stroke-linecap="round">' % (e, BRIN_SOMBRE))
        out.append(_traits(brins_disperses(
            y_haut + ep * 0.04, y_haut + ep * 0.16, L, int(L * 0.22),
            ep * 0.22, ep * 0.42, alea, 0.16, VENT, x0), 2.8, indent + 2))
        out.append(u'%s</g>' % e)
        # le fouillis du corps, sombre puis clair
        out.append(u'%s<g fill="none" stroke="%s" stroke-width="3.0"'
                   u' stroke-linecap="round">' % (e, BRIN_SOMBRE))
        out.append(_traits(brins_disperses(
            y_haut + ep * 0.35, hauteur + 6, L, int(L * 0.30),
            ep * 0.20, ep * 0.40, alea, 0.16, VENT, x0), 3.0, indent + 2))
        out.append(u'%s</g>' % e)
        out.append(u'%s<g fill="none" stroke="%s" stroke-width="2.6"'
                   u' stroke-linecap="round">' % (e, BRIN_CLAIR))
        out.append(_traits(brins_disperses(
            y_haut + ep * 0.35, hauteur + 6, L, int(L * 0.16),
            ep * 0.18, ep * 0.36, alea, 0.16, VENT, x0), 2.6, indent + 2))
        out.append(u'%s</g>' % e)
        # LE BORD INTERIEUR s'effiloche : quelques brins epars au-dela de la
        # coupe, sinon la plage d'herbe se termine au rasoir - une pelouse
        # ne s'arrete pas comme un carrelage.
        bord = x1 if x1 < largeur else x0 - 26
        out.append(u'%s<g fill="none" stroke="%s" stroke-width="2.8"'
                   u' stroke-linecap="round">' % (e, BRIN_SOMBRE))
        out.append(_traits(brins_disperses(
            y_haut + ep * 0.10, hauteur, 26, 14,
            ep * 0.18, ep * 0.34, alea, 0.16, VENT, bord), 2.8, indent + 2))
        out.append(u'%s</g>' % e)

    return "\n".join(out)
