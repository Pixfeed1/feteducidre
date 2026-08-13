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
                    inclinaison=0.40):
    u"""
    Des brins au pied tire au hasard DANS la bande, pas sur une ligne.

    Deux appels de brins() a hauteur fixe dessinaient deux RANGEES : l'oeil
    voyait les lignes de plantation, comme des poireaux. L'herbe d'une bande
    ne pousse pas en rangs - chaque brin prend son pied ou il veut.
    """
    out = []
    for _ in range(nombre):
        x = alea.uniform(-4, largeur + 4)
        y = alea.uniform(y_min, y_max)
        h = alea.uniform(h_min, h_max)
        a = alea.uniform(-inclinaison, inclinaison)
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
