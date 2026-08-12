# -*- coding: utf-8 -*-
u"""
Banc d'essai de la vague. Rien de la scene n'est modifie.

RELEVE SUR L'IMAGE DE REFERENCE (760 px de large)

    bord gauche de la mer      y = 592
    crete 1                    x = 190   y = 562
    creux                      x = 400   y = 628
    crete 2                    x = 610   y = 565
    bord droit                 y = 600

  d'ou :
    longueur d'onde   610 - 190          = 420 px   soit 0.55 x la largeur
    crete a creux     628 - 562          =  66 px   soit 0.087 x la largeur
    ligne moyenne     (562 + 628) / 2    = 595      soit 0.78 x la hauteur

  Rapporte a nos 1800 x 1350 :
    longueur d'onde   1000 px
    amplitude         +/- 78 px   (156 crete a creux)
    ligne moyenne     y = 1057

CE QUE J'AVAIS FAIT, ET L'ERREUR
  Amplitude +/- 42 pour une longueur d'onde de 900 : l'onde etait deux fois
  trop PLATE. J'avais releve la longueur d'onde correctement mais estime
  l'amplitude a l'oeil au lieu de la mesurer, et une onde de bonne periode
  mais de faible amplitude ne se lit pas comme une vague - elle se lit comme
  un bord legerement bombe.

    python3 essai_vague.py && inkscape --export-type=png \
        --export-filename=essai_vague.png -w 1800 essai_vague.svg
"""

import construire as K
import mer

LARGEUR, HAUTEUR = 1800, 1350

# LA HAUTEUR DE LA MER, mesuree sur le modele et non estimee.
#   haut du bleu (crete)   y = 562 sur 760   ->  0.74 de la hauteur
#   bas de l'image                              1.00
#   la mer occupe donc     198 / 760          =  0.26 de la hauteur
# Sur nos 1350 : la ligne moyenne tombe a 0.78 x 1350 = 1053, et le bleu
# descend jusqu'en bas. Son epaisseur va de 239 px au creux a 355 a la crete.
#
# MON BANC D'ESSAI PRECEDENT MENTAIT : il montrait la vague dans des bandes de
# 420 px de haut, ou l'epaisseur du bleu ne signifie rien. Une proportion ne
# se juge que dans le cadre reel.
MOYENNE = 0.78 * HAUTEUR

# (titre, amplitude)
ESSAIS = [(u"3 ondulations, amplitude +/- 78", 78),
          (u"3 ondulations, amplitude +/- 58", 58)]
ONDE = LARGEUR / 3.0


def feuille(amplitude, titre):
    d, xfin = mer.bord(LARGEUR, moyenne=MOYENNE, amplitude=amplitude,
                       longueur=ONDE)
    d += " L%.1f %.1f L%.1f %.1f Z" % (xfin, HAUTEUR, -ONDE, HAUTEUR)
    return u"""<svg xmlns="http://www.w3.org/2000/svg"
     width="%d" height="%d" viewBox="0 0 %d %d">
<defs>
%s
</defs>
<rect x="0" y="0" width="%d" height="%d" fill="%s"/>
<g filter="url(#grainMer)"><path d="%s" fill="%s"/></g>
<text x="30" y="56" font-family="sans-serif" font-size="34"
      fill="#5B6B78">%s</text>
</svg>
""" % (LARGEUR, HAUTEUR, LARGEUR, HAUTEUR,
       K.mouchetis("grainMer", 31, "0.38", "le grain de la mer"),
       LARGEUR, HAUTEUR, K.SABLE, d, mer.BLEU, titre)


if __name__ == "__main__":
    for k, (titre, a) in enumerate(ESSAIS, start=1):
        open("essai_vague%d.svg" % k, "w").write(feuille(a, titre))
        print(u"  %s  ->  epaisseur %.0f px au creux, %.0f a la crete "
              u"(%.0f%% et %.0f%% de la hauteur)"
              % (titre, HAUTEUR - MOYENNE - a, HAUTEUR - MOYENNE + a,
                 100 * (HAUTEUR - MOYENNE - a) / HAUTEUR,
                 100 * (HAUTEUR - MOYENNE + a) / HAUTEUR))
