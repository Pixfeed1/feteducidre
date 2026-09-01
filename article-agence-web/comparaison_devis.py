"""
Schéma — deux devis au même montant.

    python3 article-agence-web/comparaison_devis.py

Produit `article-agence-web/comparaison-devis-agence-web.webp` et son
équivalent PNG.

----------------------------------------------------------------------------
CE QUE LA FIGURE DOIT FAIRE VOIR
----------------------------------------------------------------------------
Le paragraphe tient dans une phrase : même montant, deux niveaux
d'engagement. Tout le travail de l'image est de rendre cette égalité évidente
AVANT qu'on lise quoi que ce soit.

D'où deux feuilles de format identique, alignées au pixel, dont les deux
totaux tombent exactement à la même hauteur, avec un signe égal entre les
deux. La différence saute alors aux yeux toute seule : à gauche une ligne et
du vide, à droite sept lignes qui se discutent.

Le vide de la feuille de gauche n'est pas une maladresse de mise en page,
c'est le sujet. Il n'est donc pas comblé.

----------------------------------------------------------------------------
LES MONTANTS SONT UN EXEMPLE, ET ILS TOMBENT JUSTE
----------------------------------------------------------------------------
Ce n'est pas un barème : c'est une répartition plausible pour un site vitrine
sur mesure à 8 000 €, destinée à montrer À QUOI RESSEMBLE un devis décomposé.

Le script vérifie que les sept lignes font exactement le total avant de
dessiner quoi que ce soit. Une figure qui montre une addition fausse détruit
la confiance dans tout ce qu'elle raconte par ailleurs, et personne ne
remarque l'erreur avant qu'un lecteur ne la relève.

La maintenance est mise à part, sous le total, avec son montant mensuel : la
faire entrer dans un prix de projet mélangerait un coût unique et un
abonnement, ce qui est exactement le genre de confusion qu'un devis décomposé
sert à éviter.
"""

import os

import dessin as D

RACINE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(RACINE, "comparaison-devis-agence-web")

L = 1600
MARGE = 88
ECART = 76                      # l'espace entre les deux feuilles

SURTITRE = "COMBIEN ÇA COÛTE, VRAIMENT"
TITRE = "Deux devis au même montant"

TOTAL = 8000

UNE_LIGNE = (("Création site internet", TOTAL),)

DETAIL = (
    ("Conception et maquettes", 1400),
    ("Intégration", 1700),
    ("Développement", 2400),
    ("Contenus (reprise et rédaction)", 900),
    ("Référencement technique", 700),
    ("Formation à l'administration", 400),
    ("Recette et mise en ligne", 500),
)

MAINTENANCE = ("Maintenance mensuelle", "120 € / mois")

GAUCHE = {
    "etiquette": "DEVIS A",
    "verdict": "Ne se compare à rien",
    "texte": "Rien à arbitrer, rien à retirer, et rien à opposer en cas de "
             "litige.",
}
DROITE = {
    "etiquette": "DEVIS B",
    "verdict": "Chaque ligne se discute",
    "texte": "On sait ce qu'on achète, ce qu'on peut décaler et ce qu'on "
             "peut retirer.",
}


def euros(n):
    """Un montant à la française : espace pour les milliers, € après."""
    return "{:,} €".format(n).replace(",", " ")


def feuille(t, x0, y0, larg, haut, etiquette, lignes, y_total, accent,
            f_etiq, f_ligne, f_montant, f_total, f_total_n, f_petit,
            maintenance=False):
    """
    Une feuille de devis : l'étiquette, les lignes, le trait, le total.

    `y_total` est imposé de l'extérieur, identique pour les deux feuilles :
    c'est cet alignement qui fait lire l'égalité des montants.
    """
    t.rrect([x0, y0, x0 + larg, y0 + haut], 4, teinte=D.BLANC,
            contour=D.FILET, epaisseur=2)
    #  Un filet plein en tête de feuille, à la couleur de l'accent : c'est le
    #  seul endroit où les deux devis se distinguent avant d'être lus.
    t.ligne([x0, y0 + 2, x0 + larg, y0 + 2], accent, 5)

    xg, xd = x0 + 36, x0 + larg - 36
    t.espace((xg, y0 + 34), etiquette, f_etiq, accent, 2.4)

    y = y0 + 84
    for intitule, montant in lignes:
        texte = D.typo(intitule)
        t.texte((xg, y), texte, f_ligne, D.ENCRE)
        somme = euros(montant)
        larg_s = t.mesure(somme, f_montant)
        t.texte((xd - larg_s, y + 1), somme, f_montant, D.ENCRE)
        #  Les points de conduite : ils relient l'intitulé à son montant, et
        #  c'est ce qui fait qu'on lit une facture plutôt qu'un tableau.
        x1 = xg + t.mesure(texte, f_ligne) + 12
        x2 = xd - larg_s - 12
        if x2 > x1:
            t.pointilles([(x1, y + 15), (x2, y + 15)], D.FILET, 1.6,
                         plein=2, vide=5)
        y += 38

    t.ligne([xg, y_total - 26, xd, y_total - 26], D.FILET, 1.4)
    t.texte((xg, y_total), "Total", f_total, D.ENCRE)
    somme = euros(TOTAL)
    t.texte((xd - t.mesure(somme, f_total_n), y_total - 8), somme, f_total_n,
            accent)

    if maintenance:
        yl = y_total + 58
        t.texte((xg, yl), D.typo(MAINTENANCE[0]), f_petit, D.GRIS)
        t.texte((xd - t.mesure(MAINTENANCE[1], f_petit), yl), MAINTENANCE[1],
                f_petit, D.GRIS)
        t.texte((xg, yl + 26),
                D.typo("à part, et c'est normal : ce n'est pas un coût "
                       "de projet"), f_petit, D.FAIBLE)


def egal(t, cx, cy, r):
    """Le signe égal, entre les deux totaux."""
    t.disque(cx, cy, r, teinte=D.PAPIER, contour=D.FILET, epaisseur=2)
    for dy in (-5, 5):
        t.ligne([cx - r * 0.42, cy + dy, cx + r * 0.42, cy + dy], D.GRIS, 2.4)


def principal():
    somme = sum(m for _, m in DETAIL)
    if somme != TOTAL:
        raise SystemExit("le détail fait %s, le total annonce %s"
                         % (euros(somme), euros(TOTAL)))

    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5),
               ("faible", D.FAIBLE, 3.0), ("violet", D.VIOLET, 4.5))

    m = D.Toile(10, 10)
    f_sur = m.police(D.C.POLICE_G, 15)
    f_titre = m.police(D.SERIF, 50)
    f_etiq = m.police(D.C.POLICE_G, 14)
    f_ligne = m.police(D.C.POLICE_R, 19)
    f_montant = m.police(D.C.POLICE_R, 19)
    f_total = m.police(D.SERIF_G, 24)
    f_total_n = m.police(D.SERIF_G, 34)
    f_petit = m.police(D.C.POLICE_R, 16)
    f_verdict = m.police(D.SERIF_G, 25)
    f_txt = m.police(D.C.POLICE_R, 18)

    larg = (L - 2 * MARGE - ECART) // 2
    x_g, x_d = MARGE, MARGE + larg + ECART

    y_feuille = 254
    #  La hauteur suit la feuille la plus chargée : sept lignes, le trait, le
    #  total, puis la mention de maintenance.
    y_total = y_feuille + 84 + len(DETAIL) * 38 + 34
    h_feuille = y_total + 58 + 26 + 40 - y_feuille

    verdicts = [m.couper(D.typo(c["texte"]), f_txt, larg - 20)
                for c in (GAUCHE, DROITE)]
    y_verdict = y_feuille + h_feuille + 54
    H = y_verdict + 44 + max(len(v) for v in verdicts) * 26 + MARGE - 10

    t = D.Toile(L, H)

    t.espace((MARGE, 72), SURTITRE, f_sur, D.VIOLET, 2.6)
    t.texte((MARGE - 3, 100), D.typo(TITRE), f_titre, D.ENCRE)
    t.ligne([MARGE, 206, L - MARGE, 206], D.FILET, 1)

    feuille(t, x_g, y_feuille, larg, h_feuille, GAUCHE["etiquette"],
            UNE_LIGNE, y_total, D.GRIS, f_etiq, f_ligne, f_montant,
            f_total, f_total_n, f_petit)
    feuille(t, x_d, y_feuille, larg, h_feuille, DROITE["etiquette"],
            DETAIL, y_total, D.VIOLET, f_etiq, f_ligne, f_montant,
            f_total, f_total_n, f_petit, maintenance=True)

    egal(t, MARGE + larg + ECART / 2, y_total + 8, 26)

    for i, (bloc, lignes) in enumerate(zip((GAUCHE, DROITE), verdicts)):
        x0 = MARGE + i * (larg + ECART)
        t.texte((x0, y_verdict), D.typo(bloc["verdict"]), f_verdict, D.ENCRE)
        y = y_verdict + 44
        for ligne in lignes:
            t.texte((x0, y), ligne, f_txt, D.GRIS)
            y += 26

    D.enregistrer(t.final(L, H), BASE, L, H)


if __name__ == "__main__":
    principal()
