"""
Le prix du Raspberry Pi 5 16 Go, en escalier, de janvier 2025 à aujourd'hui.

    python3 article-raspberry-pi/prix_pi5_16go.py

Produit `prix-raspberry-pi-5-16go.webp` et son PNG.

----------------------------------------------------------------------------
UN ESCALIER, PARCE QUE C'EST UN ESCALIER
----------------------------------------------------------------------------
Un prix ne glisse pas d'un palier à l'autre : il tient, puis il saute, le jour
d'une annonce. Une courbe lissée entre les quatre points raconterait une
hausse continue qui n'a pas eu lieu, et laisserait croire qu'on pouvait
acheter à 160 dollars en janvier 2026. L'escalier dit la vérité du calendrier.

----------------------------------------------------------------------------
LES VARIATIONS SONT CALCULÉES, PAS RECOPIÉES
----------------------------------------------------------------------------
Le tableau de l'article annonce « + 100 $ » pour la dernière hausse. C'est
+ 130 $ : 305 − 175. La somme des variations telles qu'écrites donne d'ailleurs
275 dollars et non 305, tandis que le total de 154 % que l'article calcule par
ailleurs confirme bien 120 → 305.

Ce script ne recopie donc aucune variation : il les DÉDUIT des prix, et le
pourcentage total avec. La figure ne peut pas porter l'erreur du tableau.

----------------------------------------------------------------------------
L'AXE PART DE ZÉRO
----------------------------------------------------------------------------
Un axe tronqué aurait rendu la marche d'avril spectaculaire à peu de frais.
Elle l'est déjà. Partir de zéro donne la proportion réelle — le prix a plus
que doublé — et retire au lecteur toute raison de soupçonner l'échelle.

----------------------------------------------------------------------------
LA COURBE VA JUSQU'À AUJOURD'HUI
----------------------------------------------------------------------------
Le brief s'arrêtait en avril 2026. Mais la légende dit « aucune baisse n'est
intervenue depuis avril » : c'est le palier qui dure qui le montre, pas le
saut. La courbe court donc jusqu'au 15 septembre 2026, date de la grille
tarifaire citée dans l'article.
"""

import os
from datetime import date

import charte as C
import dessin as D

RACINE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(RACINE, "prix-raspberry-pi-5-16go")

L, H = 1600, 880

#  (date de l'annonce, prix officiel en dollars, intitulé, mention)
PALIERS = (
    (date(2025, 1, 9), 120, "9 janvier 2025", "lancement"),
    (date(2025, 12, 1), 145, "1er décembre 2025", None),
    (date(2026, 2, 2), 175, "2 février 2026", None),
    (date(2026, 4, 1), 305, "1er avril 2026", None),
)
#  Le dernier palier court jusqu'à la date de la grille citée par l'article.
AUJOURD_HUI = date(2026, 9, 15)
FIN_TEXTE = "15 septembre 2026"

#  Le cadre du tracé.
X0, X1 = 152, 1204
Y0, Y1 = 132, 668                 # haut et bas du tracé
PLAFOND = 320                     # dollars en haut de l'axe
GRADUATIONS = (0, 100, 200, 300)

ANNOT = 1248
MARGE = 56

VIOLET_FOND = (238, 232, 252)
VIOLET_TRAIT = (98, 44, 200)

TITRE = "PRIX OFFICIEL DU RASPBERRY PI 5, 16 Go"
SOUS = "annoncé par le fabricant, en dollars, hors taxes"

PIED = (
    "Chiffres tels que publiés sur le blog officiel de Raspberry Pi, une "
    "annonce par palier. Les variations portées sur la figure sont",
    "calculées à partir des prix, non recopiées. L’axe part de zéro et la "
    "courbe court jusqu’à la grille du 15 septembre 2026.",
)


def principal():
    D.verifier(("encre", D.ENCRE, 4.5),
               ("gris", D.GRIS, 4.5),
               ("violet", VIOLET_TRAIT, 4.5))
    if C.contraste(VIOLET_TRAIT, VIOLET_FOND) < 4.5:
        raise SystemExit("le violet ne se lit pas sur son propre aplat")
    if C.contraste(D.ENCRE, VIOLET_FOND) < 4.5:
        raise SystemExit("l'encre ne se lit pas sur l'aplat violet")

    #  LES VARIATIONS, DÉDUITES. Voir l'en-tête : le tableau de l'article en
    #  annonce une fausse, et la figure ne doit pas la reprendre.
    prix = [p for _, p, _, _ in PALIERS]
    ecarts = [None] + [prix[i] - prix[i - 1] for i in range(1, len(prix))]
    total = 100.0 * (prix[-1] - prix[0]) / prix[0]
    mois = ((PALIERS[-1][0].year - PALIERS[0][0].year) * 12
            + PALIERS[-1][0].month - PALIERS[0][0].month)
    if max(prix) > PLAFOND:
        raise SystemExit("le prix le plus haut dépasse le plafond de l'axe")

    t = D.Toile(L, H)

    f_titre = t.police(C.POLICE_G, 17)
    f_sous = t.police(C.POLICE_R, 18)
    f_prix = t.police(C.POLICE_G, 22)
    f_ecart = t.police(C.POLICE_G, 15)
    f_date = t.police(C.POLICE_R, 16)
    f_axe = t.police(C.POLICE_R, 15)
    f_total = t.police(C.POLICE_G, 26)
    f_note = t.police(C.POLICE_R, 17)
    f_pied = t.police(C.POLICE_R, 16)

    jours = (AUJOURD_HUI - PALIERS[0][0]).days

    def ax(j):
        return X0 + (X1 - X0) * (j - PALIERS[0][0]).days / float(jours)

    def ay(p):
        return Y1 - (Y1 - Y0) * p / float(PLAFOND)

    t.espace((MARGE, 52), TITRE, f_titre, D.ENCRE, 2.2)
    t.texte((MARGE, 78), D.typo(SOUS), f_sous, D.FAIBLE)

    # -------------------------------------------------------------  la grille
    for g in GRADUATIONS:
        y = ay(g)
        t.ligne([X0, y, X1, y], D.FILET if g else D.GRIS, 2 if g else 3)
        etiquette = "%d $" % g
        t.texte((X0 - 14 - t.mesure(etiquette, f_axe), y - 10), etiquette,
                f_axe, D.FAIBLE)

    # -----------------------------------------------------------  l'escalier
    #  Les sommets du tracé : on tient, on saute, on tient.
    points = []
    for i, (j, p, _, _) in enumerate(PALIERS):
        if i:
            points.append((ax(j), ay(PALIERS[i - 1][1])))
        points.append((ax(j), ay(p)))
    points.append((ax(AUJOURD_HUI), ay(prix[-1])))

    t.polygone(points + [(X1, Y1), (X0, Y1)], VIOLET_FOND)
    t.polyligne(points, VIOLET_TRAIT, 4)

    # -----------------------------------------------  étiquettes de prix
    for i, (j, p, intitule, mention) in enumerate(PALIERS):
        x = ax(j)
        suivant = i + 1 < len(PALIERS)
        fin = ax(PALIERS[i + 1][0]) if suivant else ax(AUJOURD_HUI)
        place = fin - x

        haut = "%d $" % p
        bas = mention if mention else "+ %d $" % ecarts[i]
        besoin = max(t.mesure(haut, f_prix), t.mesure(bas, f_ecart)) + 18
        if besoin > place:
            raise SystemExit("l'étiquette « %s » ne tient pas sur son palier "
                             "(%d px pour %d)" % (haut, besoin, place))

        #  Au-dessus du palier, sauf pour le plus haut : la place manque entre
        #  le trait et le bord du cadre, l'étiquette passe alors en dessous.
        if ay(p) - 54 < Y0:
            y_haut, y_bas = ay(p) + 16, ay(p) + 44
        else:
            y_haut, y_bas = ay(p) - 54, ay(p) - 26
        t.texte((x + 12, y_haut), haut, f_prix, D.ENCRE)
        t.texte((x + 12, y_bas), D.typo(bas), f_ecart,
                D.FAIBLE if mention else VIOLET_TRAIT)

        #  Le point de l'annonce, sur le nouveau palier.
        t.disque(x, ay(p), 7, teinte=VIOLET_TRAIT)
        t.disque(x, ay(p), 3, teinte=D.PAPIER)

    # ----------------------------------------------------------  les dates
    #  Deux rangées en quinconce : les trois dernières annonces tiennent en
    #  cinq mois, et leurs libellés se chevauchaient sur une seule ligne.
    for i, (j, _, intitule, _) in enumerate(PALIERS):
        x = ax(j)
        y = Y1 + (18 if i % 2 == 0 else 46)
        t.ligne([x, Y1, x, y - 4], D.FILET, 2)
        #  Centré sous son repère, sauf le premier : centré, il débordait à
        #  gauche du cadre et ne s'alignait sur rien.
        gauche = X0 if i == 0 else x - t.mesure(intitule, f_date) / 2.0
        t.texte((gauche, y), intitule, f_date, D.GRIS)
    fin_x = ax(AUJOURD_HUI)
    t.texte((fin_x - t.mesure(FIN_TEXTE, f_date), Y1 + 18), FIN_TEXTE, f_date,
            D.FAIBLE)

    # -------------------------------------------------------------  le total
    y_a, y_b = ay(prix[0]), ay(prix[-1])
    t.polyligne([(ANNOT - 16, y_b), (ANNOT, y_b), (ANNOT, y_a),
                 (ANNOT - 16, y_a)], VIOLET_TRAIT, 3)
    t.texte((ANNOT + 26, (y_a + y_b) / 2.0 - 46), "+ %.0f %%" % total, f_total,
            VIOLET_TRAIT)
    yy = (y_a + y_b) / 2.0 - 6
    for ligne in t.couper(
            D.typo("en %d mois, sur un produit vendu comme abordable" % mois),
            f_note, L - MARGE - ANNOT - 26):
        t.texte((ANNOT + 26, yy), ligne, f_note, D.GRIS)
        yy += 24

    # ---------------------------------------------------------------  le pied
    y_pied = Y1 + 92
    t.ligne([MARGE, y_pied, L - MARGE, y_pied], D.FILET, 2)
    for i, ligne in enumerate(PIED):
        ligne = D.typo(ligne)
        if t.mesure(ligne, f_pied) > L - 2 * MARGE:
            raise SystemExit("la ligne %d du pied déborde" % (i + 1))
        t.texte((MARGE, y_pied + 18 + i * 24), ligne, f_pied, D.FAIBLE)

    D.enregistrer(t.final(L, H), BASE, L, H)
    print("  paliers  %s" % "  ".join("%d $" % p for p in prix))
    print("  écarts   %s" % "  ".join("+ %d $" % e for e in ecarts[1:]))
    print("  total    + %.1f %% en %d mois" % (total, mois))


if __name__ == "__main__":
    principal()
