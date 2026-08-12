# -*- coding: utf-8 -*-
u"""
Le parasol du modele - la forme est arretee, on regle le GRAIN.

LA FORME, relevee sur l'image de reference
  Une demi-lune en secteurs egaux, tous issus du milieu du bord droit, ou le
  mat vient se planter. Bord bas rectiligne. Aucun contour, aucune couture
  tracee, aucun embout. Nombre impair de secteurs : la couleur pleine se
  retrouve aux deux extremites. Inclinaison -34 deg.

LE GRAIN
  Sur le modele, la toile est franchement mouchetee - bien plus que ne
  l'etaient nos parasols. Le reglage precedent (vert 0.11) avait ete cale
  pour que le grain du parasol EGALE celui du ciel. C'etait le bon calcul
  pour une image homogene, mais pas ce que fait la reference : elle charge
  davantage les aplats satures que les grands fonds.

  Le rapport vert/blanc est conserve (x3.1). Il n'est pas arbitraire : un
  point clair sur du blanc ne se voit pas, donc le blanc a besoin de plus de
  points pour rendre la meme matiere. Deux reglages differents sont la seule
  facon d'obtenir le meme grain sur les deux couleurs d'un meme objet.

    python3 essai_parasol.py && inkscape --export-type=png \
        --export-filename=essai_parasol.png -w 1500 essai_parasol.svg
"""

import construire as K
import parasols as PA

SECTEURS = 5
INCLINAISON = -34.0
RAPPORT = 3.1                 # blanc / vert, cale par mesure

# Les forces de grain a comparer, sur le vert.
FORCES = [0.11, 0.24, 0.38, 0.55]

CASE_L, CASE_H = 420, 600
MARGE = 40
RAYON = 145


def feuille():
    largeur = CASE_L * len(FORCES) + 2 * MARGE
    cases, filtres = [], []
    for i, f in enumerate(FORCES):
        dx = MARGE + i * CASE_L
        nv, nb = "grainV%d" % i, "grainB%d" % i
        filtres.append(K.mouchetis(nv, 44, "%.2f" % f, "vert a %.2f" % f))
        filtres.append(K.mouchetis(
            nb, 44, "%.2f" % min(1.0, f * RAPPORT),
            "blanc a %.2f" % min(1.0, f * RAPPORT)))
        cases.append("\n".join(x for x in (
            (u'  <path d="M%d 30 L%d %d" stroke="#CFE0EE" stroke-width="2"/>'
             % (dx, dx, CASE_H - 60)) if i else u'',
            PA.un_eventail(u"grain %.2f" % f, dx + CASE_L / 2.0, 290,
                           RAYON, SECTEURS, INCLINAISON, indent=2,
                           filtre_a=nv, filtre_b=nb),
            (u'  <text x="%d" y="%d" font-family="sans-serif" font-size="24"'
             u' fill="#4A5560" text-anchor="middle">vert %.2f / blanc %.2f'
             u'</text>' % (dx + CASE_L / 2, CASE_H - 28, f,
                           min(1.0, f * RAPPORT))))
            if x))

    return u"""<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
     width="%d" height="%d" viewBox="0 0 %d %d">
<defs>
%s
</defs>
<rect x="0" y="0" width="%d" height="%d" fill="%s"/>
%s
</svg>
""" % (largeur, CASE_H, largeur, CASE_H, "\n\n".join(filtres),
       largeur, CASE_H, K.CIEL, "\n".join(cases))


if __name__ == "__main__":
    open("essai_parasol.svg", "w").write(feuille())
    print(u"%d forces de grain, forme figee : %d secteurs, %.0f deg"
          % (len(FORCES), SECTEURS, INCLINAISON))
