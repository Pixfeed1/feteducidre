"""
Où partent les cartes : 75 % industriel, 25 % amateurs et éducation.

    python3 article-raspberry-pi/ventes_par_segment.py

Produit `ventes-raspberry-pi-par-segment.webp` et son PNG.

----------------------------------------------------------------------------
UNE BARRE, PAS UN CAMEMBERT
----------------------------------------------------------------------------
Deux parts, c'est le seul cas où un camembert reste lisible. Mais la barre fait
mieux sur un point qui compte ici : elle se lit à la règle. Le lecteur voit que
la part violette fait trois fois l'autre, sans avoir à comparer deux angles.
Et elle tient dans la largeur d'un article sans laisser deux coins vides.

----------------------------------------------------------------------------
DES UNITÉS, PAS DES ACHETEURS
----------------------------------------------------------------------------
La donnée porte sur les CARTES VENDUES, pas sur le nombre de clients. Ce n'est
pas la même chose : un industriel qui commande dix mille cartes est un
acheteur. Le titre de la section — « trois acheteurs sur quatre » — dit donc
plus que la source.

La figure s'en tient à ce que la source mesure : elle parle d'unités, en titre
comme en pied, et la mention « trois cartes sur quatre » remplace les
acheteurs. C'est le genre de glissement qu'un lecteur attentif relève, et la
section entière repose dessus.

----------------------------------------------------------------------------
CE QUI N'A PAS PU ÊTRE VÉRIFIÉ
----------------------------------------------------------------------------
Le site investisseurs de Raspberry Pi Holdings est hors de la liste
d'autorisation de cette machine. Les deux parts sont donc celles fournies par
l'article, et le pied le dit : « d'après Raspberry Pi Holdings ». La figure
attribue, elle ne s'approprie pas la vérification.
"""

import os

import charte as C
import dessin as D

RACINE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(RACINE, "ventes-raspberry-pi-par-segment")

L, H = 1600, 620
MARGE = 56

#  (part en pour cent, intitulé, précision, teinte de l'aplat, teinte du texte)
PARTS = (
    (75, "Industriel et embarqué", "trois cartes sur quatre",
     (98, 44, 200), (255, 255, 255)),
    (25, "Amateurs et éducation", "un quart du volume",
     (234, 227, 252), (26, 27, 32)),
)

BARRE_HAUT, BARRE_BAS = 196, 340

TITRE = "VENTES DE CARTES ET DE MODULES DE CALCUL, EXERCICE 2025"
SOUS = "répartition par segment, en unités vendues"

PIED = (
    "D’après la ventilation publiée par Raspberry Pi Holdings sur son site "
    "investisseurs. La mesure porte sur les unités vendues,",
    "non sur le nombre de clients : un industriel qui commande dix mille "
    "cartes compte pour un acheteur et pour dix mille unités.",
)


def principal():
    D.verifier(("encre", D.ENCRE, 4.5),
               ("gris", D.GRIS, 4.5),
               ("violet", PARTS[0][3], 4.5))

    total = sum(p for p, _, _, _, _ in PARTS)
    if total != 100:
        raise SystemExit("les parts font %d %% et non 100" % total)
    for part, intitule, _, fond, texte in PARTS:
        if C.contraste(texte, fond) < 4.5:
            raise SystemExit("« %s » ne se lit pas sur son aplat (%.2f:1)"
                             % (intitule, C.contraste(texte, fond)))

    t = D.Toile(L, H)

    f_titre = t.police(C.POLICE_G, 17)
    f_sous = t.police(C.POLICE_R, 18)
    f_part = t.police(C.POLICE_G, 54)
    f_nom = t.police(C.POLICE_G, 21)
    f_precision = t.police(C.POLICE_R, 18)
    f_pied = t.police(C.POLICE_R, 16)

    t.espace((MARGE, 52), TITRE, f_titre, D.ENCRE, 2.2)
    t.texte((MARGE, 78), D.typo(SOUS), f_sous, D.FAIBLE)

    # ------------------------------------------------------------  la barre
    largeur = L - 2 * MARGE
    x = MARGE
    bornes = []
    for part, _, _, fond, _ in PARTS:
        w = largeur * part / 100.0
        t.d.rectangle(t._b([x, BARRE_HAUT, x + w, BARRE_BAS]), fill=fond)
        bornes.append((x, w))
        x += w

    #  Un filet sur la part pâle, qui sans lui flotte sur le papier — les deux
    #  sont clairs, et le bord droit de la barre disparaissait.
    x_pale, w_pale = bornes[1]
    t.d.rectangle(t._b([x_pale, BARRE_HAUT,
                        x_pale + w_pale - 1, BARRE_BAS - 1]),
                  outline=D.FILET, width=int(2 * t.e))

    # -------------------------------------------------------  les étiquettes
    for (part, intitule, precision, _, teinte), (x, w) in zip(PARTS, bornes):
        chiffre = "%d %%" % part
        if t.mesure(chiffre, f_part) + 48 > w:
            raise SystemExit("« %s » ne tient pas dans sa part" % chiffre)
        t.texte((x + 26, BARRE_HAUT + 34), chiffre, f_part, teinte)

        #  Le nom sous la barre, aligné sur le début de sa part : dedans, il
        #  aurait fallu réduire le chiffre, qui est ce qu'on vient lire.
        t.ligne([x, BARRE_BAS, x, BARRE_BAS + 22], D.FILET, 2)
        t.texte((x + 2, BARRE_BAS + 34), D.typo(intitule), f_nom, D.ENCRE)
        t.texte((x + 2, BARRE_BAS + 66), D.typo(precision), f_precision,
                D.GRIS)

    # ---------------------------------------------------------------  le pied
    y_pied = BARRE_BAS + 128
    t.ligne([MARGE, y_pied, L - MARGE, y_pied], D.FILET, 2)
    for i, ligne in enumerate(PIED):
        ligne = D.typo(ligne)
        if t.mesure(ligne, f_pied) > L - 2 * MARGE:
            raise SystemExit("la ligne %d du pied déborde" % (i + 1))
        t.texte((MARGE, y_pied + 18 + i * 24), ligne, f_pied, D.FAIBLE)

    D.enregistrer(t.final(L, H), BASE, L, H)
    print("  parts  %s  (total %d %%)"
          % ("  ".join("%d %% %s" % (p, n) for p, n, _, _, _ in PARTS), total))


if __name__ == "__main__":
    principal()
