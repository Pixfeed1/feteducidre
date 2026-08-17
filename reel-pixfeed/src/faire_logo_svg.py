"""
Génère `assets/svg/logo.svg` — la marque PixFeed.

La marque est définie par CINQ rectangles posés sur une grille dont les
graduations sont P = [0, 1, 1+j, 2+j, 2+2j, 3+2j] avec j = 0,444 le jeu entre
les blocs. C'est exactement la même définition que celle du film du logo
(voir logo/pixfeed_30s.py, fonction `blocs_logo`) : les deux formats doivent
montrer rigoureusement la même forme.

Ce fichier n'est à relancer que si la marque change.
"""

import os

JEU = 0.444
P = [0.0, 1.0, 1.0 + JEU, 2.0 + JEU, 2.0 + 2 * JEU, 3.0 + 2 * JEU]
#  (colonne_gauche, ligne_haut, colonne_droite, ligne_bas), en indices de P
#
#  ATTENTION — ces cinq rectangles sont DISJOINTS, et ils doivent le rester.
#  La définition d'origine (film du logo) en avait deux qui se chevauchaient :
#  sans conséquence pour un champ de lettres, fatal en SVG, où la règle de
#  remplissage pair-impair transforme tout recouvrement en TROU. La marque
#  ressortait déchiquetée. Les deux blocs fautifs ont été raccourcis de la
#  part déjà couverte par leur voisin : l'union est rigoureusement la même.
BLOCS = [(0, 0, 5, 1), (4, 1, 5, 3), (0, 2, 3, 3), (2, 3, 3, 5), (0, 4, 1, 5)]

COTE = P[5]
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def svg(couleur="#ECECF1"):
    rects = []
    for a, b, c, d in BLOCS:
        x, y = P[a], P[b]
        rects.append('  <rect x="%.4f" y="%.4f" width="%.4f" height="%.4f"/>'
                     % (x, y, P[c] - x, P[d] - y))
    return ('<svg xmlns="http://www.w3.org/2000/svg" '
            'viewBox="0 0 %.4f %.4f" width="%.0f" height="%.0f" '
            'fill="%s">\n%s\n</svg>\n'
            % (COTE, COTE, COTE * 100, COTE * 100, couleur, "\n".join(rects)))


if __name__ == "__main__":
    dossier = os.path.join(RACINE, "assets", "svg")
    os.makedirs(dossier, exist_ok=True)
    chemin = os.path.join(dossier, "logo.svg")
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(svg())
    print("écrit : assets/svg/logo.svg  (%d blocs, côté %.3f)"
          % (len(BLOCS), COTE))
