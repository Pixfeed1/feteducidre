# -*- coding: utf-8 -*-
u"""
La mer, et sa vague.

CE QUE MONTRE LE MODELE
  Une masse bleue posee en bas de l'image, dont le bord haut ondule
  largement : environ DEUX CRETES sur toute la largeur, pour une amplitude
  d'a peu pres un vingtieme de cette largeur. C'est une onde LONGUE et BASSE
  - pas une frise de vaguelettes. Rapportee a nos 1800 px : une longueur
  d'onde de 900, une amplitude crete a creux de 84.

  Le bleu est franc et le grain y est bien visible, comme sur la toile des
  parasols : la reference charge ses aplats satures.

VALEURS RETENUES, mesurees et non estimees
  trois ondulations dans le cadre    ->  longueur d'onde 1800 / 3 = 600
  amplitude                          ->  +/- 58 (raideur 0.19)
  ligne moyenne                      ->  0.78 x 1350 = 1053

  La mer occupe alors 26 % de la hauteur, comme sur le modele : 239 px
  d'epaisseur au creux, 355 a la crete.

  MES DEUX ERREURS AVANT D'Y ARRIVER. D'abord une amplitude ESTIMEE a l'oeil
  (+/- 42) alors que la longueur d'onde, elle, avait ete mesuree : une onde
  de bonne periode mais trop plate se lit comme un bord bombe, pas comme une
  vague. Ensuite un banc d'essai qui montrait la vague dans des bandes de
  420 px, ou l'epaisseur du bleu ne veut rien dire. Une proportion ne se
  juge que dans le cadre reel.

LA COURBE
  Une sinusoide echantillonnee en segments donnerait une polyligne - le
  defaut qui faisait ressembler nos membres a du Paint. Chaque DEMI-PERIODE
  est donc une seule cubique, avec ses deux points de controle au tiers et
  aux deux tiers, a hauteur des extremums. L'ecart avec la vraie sinusoide
  est inferieur au demi-pour-cent de l'amplitude, et la courbe est lisse par
  construction : les tangentes sont horizontales aux cretes et aux creux,
  donc la jonction entre deux demi-periodes ne se voit pas.
"""

BLEU = "#3D7BE0"

MOYENNE = 1053.0        # la ligne autour de laquelle la vague oscille
AMPLITUDE = 58.0        # de la moyenne a la crete (le double crete a creux)
CRETES = 3          # combien d'ondulations doivent se voir dans le cadre
# LA PHASE N'EST PLUS UN REGLAGE. Elle est CALCULEE pour que les deux bords
# du cadre tombent sur un CREUX. On voit alors exactement CRETES bosses
# entieres, ni une de plus ni un morceau de plus.
#
# Avec une phase libre, la vague etait coupee n'importe ou : un bout de crete
# apparaissait a droite et on croyait en compter quatre. Le nombre
# d'ondulations VUES ne doit pas dependre de la ou le cadre tombe.


def bord(largeur, moyenne=None, amplitude=None, cretes=None):
    u"""
    Le seul bord haut de la mer, en cubiques, de gauche a droite.

    cretes : le nombre d'ondulations VOULUES dans le cadre. La longueur
    d'onde en decoule - largeur / cretes - et la vague demarre un creux avant
    le bord gauche, ce qui place un creux exactement sur chaque bord.
    """
    moyenne = MOYENNE if moyenne is None else moyenne
    amplitude = AMPLITUDE if amplitude is None else amplitude
    cretes = CRETES if cretes is None else cretes

    longueur = largeur / float(cretes)
    demi = longueur / 2.0
    # Depart un creux AVANT le bord gauche : les creux tombent alors sur
    # 0, longueur, 2.longueur ... c'est-a-dire sur les deux bords, et les
    # cretes au milieu de chaque intervalle.
    x = -longueur
    haut = False                      # la premiere extremite est-elle en haut
    d = "M%.1f %.1f" % (x, moyenne - amplitude if haut else moyenne + amplitude)
    while x < largeur + longueur:
        y0 = moyenne - amplitude if haut else moyenne + amplitude
        y1 = moyenne + amplitude if haut else moyenne - amplitude
        d += " C%.1f %.1f %.1f %.1f %.1f %.1f" % (
            x + demi / 3.0, y0, x + demi * 2.0 / 3.0, y1, x + demi, y1)
        x += demi
        haut = not haut
    return d, x


def bloc(largeur, hauteur, indent=2, **reglages):
    u"""La masse complete : le bord haut, puis les trois cotes du cadre."""
    d, xfin = bord(largeur, **reglages)
    d += " L%.1f %.1f L%.1f %.1f Z" % (xfin, hauteur + 40,
                                       -largeur, hauteur + 40)
    e = " " * indent
    return u'%s<path d="%s" fill="%s"/>' % (e, d, BLEU)


if __name__ == "__main__":
    d, _ = bord(1800)
    print(u"%d ondulations, longueur d'onde %.0f" % (CRETES, 1800.0 / CRETES))
    print(u"cretes a x = %s"
          % ", ".join("%.0f" % (1800.0 / CRETES * (k + 0.5))
                      for k in range(CRETES)))
    print(u"creux sur les deux bords, crete a y=%.0f, creux a y=%.0f"
          % (MOYENNE - AMPLITUDE, MOYENNE + AMPLITUDE))
