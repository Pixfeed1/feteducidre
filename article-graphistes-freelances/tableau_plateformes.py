"""
Cinq plateformes, deux modèles, et trois colonnes presque vides.

    python3 article-graphistes-freelances/tableau_plateformes.py

Produit `plateformes-graphistes-comparatif.webp` et son PNG.

----------------------------------------------------------------------------
LES CASES VIDES SONT LE RÉSULTAT, PAS UN TROU
----------------------------------------------------------------------------
Le relevé ne trouve qu'un seul prix d'entrée CHIFFRÉ sur cinq et deux
commissions chiffrées sur cinq. « Sur devis » est une réponse publique, mais
ce n'est pas un prix : les compter ensemble donnait quatre prix sur cinq et
un bandeau faux, ce que le garde-fou a refusé.

Il aurait été facile de combler le reste avec
des ordres de grandeur plausibles : c'est exactement ce que font les
comparatifs qu'on lit partout, et c'est ce qui les rend inutiles.

Les cases portent donc « non relevée », et le pied précise ce que ça veut
dire : pas qu'il n'y a pas de commission, mais que le relevé n'en a pas
trouvé de chiffre public. Les deux comptes affichés sous le tableau sont
calculés à partir des cases, pas saisis à la main : ils ne peuvent pas se
désynchroniser du contenu.

----------------------------------------------------------------------------
UNE SEULE LIGNE EST VIOLETTE, ET C'EST LA THÈSE DE L'ARTICLE
----------------------------------------------------------------------------
L'article tient en une phrase : il n'y a pas cinq offres, il y en a deux. La
pastille de la colonne « Modèle » ne sert qu'à ça. Une seule plateforme fait
travailler des gens qui ne seront pas payés, et on la voit du premier coup
d'oeil sans lire une ligne.

----------------------------------------------------------------------------
CE QUI N'A PAS PU ÊTRE VÉRIFIÉ ICI
----------------------------------------------------------------------------
Les cinq sites sont hors de la liste d'autorisation de cette machine :
malt.fr, 99designs.fr, fiverr.com, graphiste.com et creads.com répondent
tous en échec de connexion. Aucun chiffre n'a donc été recoupé depuis ici.
Le tableau porte la date du relevé et le nomme comme un relevé, il ne
s'approprie pas une vérification qu'il n'a pas faite.
"""

import os

import charte as C
import dessin as D

RACINE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(RACINE, "plateformes-graphistes-comparatif")

L = 1600
MARGE = 56
RELEVE = "20 septembre 2026"

VIOLET = (98, 44, 200)
NEUTRE = (150, 152, 158)
ZEBRE = (244, 243, 238)

#  Ni « non relevé » ni « non relevée » : la case sert à la fois au prix,
#  masculin, et à la commission, féminine. Et « pas de chiffre public »
#  dit mieux ce qui est vrai que « non relevé », qui pourrait passer
#  pour un oubli du relevé.
INCONNU = "Pas de chiffre public"

#  Les colonnes, avec leur largeur. La commission prend le plus de place :
#  c'est la seule case où une plateforme écrit une phrase et non un nombre.
COLONNES = (("Plateforme", 296), ("Modèle", 272), ("Prix d’entrée", 250),
            ("Commission", 670))

#  (plateforme, précision, modèle, spéculatif, prix, précision, commission)
#  Tout vient du relevé du 20 septembre 2026. Rien n'est complété au jugé.
LIGNES = (
    ("99designs by Vista", "concours d’une semaine",
     "Concours", True,
     "289 €", "logo, entrée de gamme",
     INCONNU),
    ("Creads", "5 000 créatifs, 5 % retenus",
     "Mise en relation, encadrée", False,
     "Sur devis", "au forfait, une création un prix",
     INCONNU),
    ("Graphiste.com et Codeur.com", "groupe Freeland, 375 000 profils",
     "Mise en relation, sur devis", False,
     "Sur devis", "devis personnalisés des freelances",
     INCONNU),
    ("Malt", "plus d’un million de profils",
     "Mise en relation, directe", False,
     "Sur devis", "tarif journalier du freelance",
     "5 % HT de frais de service freelance. Sur certaines missions en "
     "France, en Belgique et en Espagne : 10 % HT, puis 5 % après six mois "
     "de mission. Pour un micro-entrepreneur non assujetti à la TVA, "
     "6 % et 12 % TTC."),
    ("Fiverr", "offre Pro : premier centile",
     "Mise en relation, catalogue", False,
     INCONNU, "le plus bas du lot, non chiffré",
     "20 % prélevés sur le vendeur, plus des frais côté acheteur qui "
     "varient selon le montant de la commande et ne sont pas chiffrés "
     "par le relevé."),
)

TITRE = "CINQ PLATEFORMES, DEUX MODÈLES"
SOUS = "ce que chacune publie avant que vous ne commandiez"

PIED = (
    "Relevé du %s sur les pages publiques et les centres d’aide des "
    "plateformes, plus le communiqué Freeland du 9 juin 2022. Les cinq "
    "sites étant" % RELEVE,
    "injoignables depuis la machine qui a produit cette figure, aucun "
    "chiffre n’a été recoupé ici : le tableau rapporte un relevé daté, il "
    "ne le vérifie pas.",
    "« Pas de chiffre public » ne veut pas dire qu’il n’y a pas de "
    "commission, mais que le relevé n’en a trouvé aucun montant affiché. "
    "C’est une information sur la plateforme, pas un trou dans le tableau.",
)


def lettres(n):
    """Les petits nombres s’écrivent en toutes lettres dans une phrase."""
    mots = ("zéro", "une", "deux", "trois", "quatre", "cinq", "six", "sept",
            "huit", "neuf")
    return mots[n] if n < len(mots) else str(n)


def principal():
    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5),
               ("violet", VIOLET, 4.5))
    if sum(w for _, w in COLONNES) != L - 2 * MARGE:
        raise SystemExit("les colonnes font %d px pour %d disponibles"
                         % (sum(w for _, w in COLONNES), L - 2 * MARGE))

    #  Les deux comptes du bandeau sont DÉRIVÉS des cases. Saisis à la main,
    #  ils survivraient à une correction du tableau en disant le contraire.
    #  Ce qui compte n'est pas « la case est remplie » mais « la case porte
    #  un CHIFFRE ». « Sur devis » est une réponse publique, ce n'est
    #  simplement pas un prix : compter ces cases comme des prix donnait
    #  quatre sur cinq et rendait le bandeau faux.
    def chiffre(v):
        return any(c.isdigit() for c in v)

    prix = sum(1 for r in LIGNES if chiffre(r[4]))
    commissions = sum(1 for r in LIGNES if chiffre(r[6]))
    speculatifs = sum(1 for r in LIGNES if r[3])

    t = D.Toile(L, 100)
    f_titre = t.police(C.POLICE_G, 17)
    f_sous = t.police(C.POLICE_R, 18)
    f_tete = t.police(C.POLICE_G, 14)
    f_nom = t.police(C.POLICE_G, 18)
    f_cel = t.police(C.POLICE_R, 16)
    f_pre = t.police(C.POLICE_R, 14)
    f_fait = t.police(C.POLICE_G, 20)
    f_pied = t.police(C.POLICE_R, 16)

    # -------------------------------------------  on mesure avant de dessiner
    #  La hauteur d'une ligne dépend de la case qui se plie en le plus de
    #  lignes. On calcule tout d'abord, on ouvre la toile ensuite.
    plies = []
    for r in LIGNES:
        cases = (t.couper(D.typo(r[0]), f_nom, COLONNES[0][1] - 24),
                 t.couper(D.typo(r[2]), f_cel, COLONNES[1][1] - 24 - 22),
                 t.couper(D.typo(r[4]), f_cel, COLONNES[2][1] - 24),
                 t.couper(D.typo(r[6]), f_cel, COLONNES[3][1] - 24))
        precisions = (t.couper(D.typo(r[1]), f_pre, COLONNES[0][1] - 24),
                      t.couper(D.typo(r[5]), f_pre, COLONNES[2][1] - 24))
        corps = max(len(c) for c in cases) * 21
        bas = max(len(precisions[0]), len(precisions[1])) * 18
        plies.append((cases, precisions, corps + bas + 26))

    y_tete = 150
    y_table = y_tete + 30
    hauteur = sum(p[2] for p in plies)
    y_fait = y_table + hauteur + 42
    y_pied = y_fait + 62
    H = y_pied + 18 + len(PIED) * 24 + 40

    t = D.Toile(L, H)
    f_titre = t.police(C.POLICE_G, 17)
    f_sous = t.police(C.POLICE_R, 18)
    f_tete = t.police(C.POLICE_G, 14)
    f_nom = t.police(C.POLICE_G, 18)
    f_cel = t.police(C.POLICE_R, 16)
    f_pre = t.police(C.POLICE_R, 14)
    f_fait = t.police(C.POLICE_G, 20)
    f_pied = t.police(C.POLICE_R, 16)

    t.espace((MARGE, 52), TITRE, f_titre, D.ENCRE, 2.2)
    t.texte((MARGE, 78), D.typo(SOUS), f_sous, D.FAIBLE)

    # ------------------------------------------------------------  la légende
    x = MARGE
    for teinte, mot in ((VIOLET, "le travail non retenu n’est pas payé"),
                        (NEUTRE, "pas de travail gratuit")):
        t.disque(x + 6, 116, 6, teinte=teinte)
        t.texte((x + 20, 108), D.typo(mot), f_pre, D.GRIS)
        x += 20 + t.mesure(D.typo(mot), f_pre) + 32
    if x > L - MARGE:
        raise SystemExit("la légende déborde")

    # ----------------------------------------------------------  les en-têtes
    x = MARGE
    for nom, w in COLONNES:
        t.espace((x, y_tete), nom.upper(), f_tete, D.GRIS, 1.4)
        x += w
    t.ligne([MARGE, y_table - 6, L - MARGE, y_table - 6], D.ENCRE, 2)

    # -------------------------------------------------------------  les lignes
    y = y_table
    for i, (r, (cases, precisions, haut)) in enumerate(zip(LIGNES, plies)):
        if i % 2 == 1:
            t.rrect([MARGE, y, L - MARGE, y + haut], 0, teinte=ZEBRE)

        x = MARGE
        #  Le nom, puis sa précision en plus petit.
        yy = y + 14
        for ligne in cases[0]:
            t.texte((x, yy), ligne, f_nom, D.ENCRE)
            yy += 21
        for ligne in precisions[0]:
            t.texte((x, yy + 2), ligne, f_pre, D.FAIBLE)
            yy += 18
        x += COLONNES[0][1]

        #  Le modèle, précédé de sa pastille.
        t.disque(x + 6, y + 21, 6, teinte=VIOLET if r[3] else NEUTRE)
        yy = y + 14
        for ligne in cases[1]:
            t.texte((x + 22, yy), ligne, f_cel,
                    VIOLET if r[3] else D.ENCRE)
            yy += 21
        x += COLONNES[1][1]

        #  Le prix, puis sa précision.
        yy = y + 14
        for ligne in cases[2]:
            t.texte((x, yy), ligne, f_cel,
                    D.FAIBLE if r[4] == INCONNU else D.ENCRE)
            yy += 21
        for ligne in precisions[1]:
            t.texte((x, yy + 2), ligne, f_pre, D.FAIBLE)
            yy += 18
        x += COLONNES[2][1]

        #  La commission.
        yy = y + 14
        for ligne in cases[3]:
            t.texte((x, yy), ligne, f_cel,
                    D.FAIBLE if r[6] == INCONNU else D.ENCRE)
            yy += 21

        y += haut
        t.ligne([MARGE, y, L - MARGE, y], D.FILET, 1)

    # -------------------------------------------------------  ce qu'on retient
    fait = ("Un seul prix d’entrée chiffré sur %s, %s commissions chiffrées "
            "sur %s, et une seule plateforme qui fait travailler sans payer."
            % (lettres(len(LIGNES)), lettres(commissions),
               lettres(len(LIGNES))))
    if prix != 1 or speculatifs != 1:
        raise SystemExit("le bandeau est écrit au singulier mais les "
                         "chiffres ont changé : %d prix, %d concours"
                         % (prix, speculatifs))
    if t.mesure(D.typo(fait), f_fait) > L - 2 * MARGE:
        raise SystemExit("le bandeau déborde")
    t.texte((MARGE, y_fait), D.typo(fait), f_fait, VIOLET)

    # ---------------------------------------------------------------  le pied
    t.ligne([MARGE, y_pied, L - MARGE, y_pied], D.FILET, 2)
    for i, ligne in enumerate(PIED):
        ligne = D.typo(ligne)
        if t.mesure(ligne, f_pied) > L - 2 * MARGE:
            raise SystemExit("la ligne %d du pied déborde" % (i + 1))
        t.texte((MARGE, y_pied + 18 + i * 24), ligne, f_pied, D.FAIBLE)

    D.enregistrer(t.final(L, H), BASE, L, H)
    print("  %d lignes, %d prix relevé, %d commissions relevées"
          % (len(LIGNES), prix, commissions))


if __name__ == "__main__":
    principal()
