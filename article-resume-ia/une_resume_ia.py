"""
L'image à la une : le résumé IA en haut, les liens classiques repoussés.

    python3 article-resume-ia/une_resume_ia.py

Produit `resume-ia-au-dessus-des-liens.webp` et son PNG, en 1600 × 900.

----------------------------------------------------------------------------
UN SCHÉMA, ET PAS UNE CAPTURE
----------------------------------------------------------------------------
Le brief demandait une capture d'écran de Google. Deux raisons de ne pas la
faire, et la seconde compte plus que la première.

D'abord, Google est refusé par la politique de sortie de la machine qui
fabrique ces images : impossible d'aller la chercher ici.

Ensuite et surtout, un faux Google dessiné au pixel près et présenté comme une
capture serait une contrefaçon d'interface donnée pour un relevé réel. Une
image publiée sous une légende qui affirme un fait doit être ce qu'elle
prétend être. Ce schéma-ci ne se fait passer pour rien : pas de logo, pas de
marque, pas de couleurs empruntées.

Et ce n'est pas qu'un pis-aller. Une capture de résultats, c'est UNE requête un
jour donné, encombrée de son contenu propre, et périmée au prochain
remaniement de la page. Un schéma montre l'anatomie : deux zones, une ligne de
flottaison entre elles. C'est ce que dit la légende.

----------------------------------------------------------------------------
AUCUN CHIFFRE INVENTÉ
----------------------------------------------------------------------------
La tentation serait d'écrire « le résumé occupe 68 % de la première vue ». Ce
serait un fait sur ce dessin, pas sur Google, et le lecteur le prendrait pour
le second. Les deux zones sont donc nommées, pas chiffrées.

----------------------------------------------------------------------------
LA PAGE EST CONTINUE, LA FLOTTAISON EST DESSUS
----------------------------------------------------------------------------
Le premier jet coupait la page à la ligne de flottaison et posait les liens en
dessous, sur le papier. Ça racontait deux pages au lieu d'une. La page est
donc un seul bloc blanc qui déborde vers le bas, et la ligne de flottaison est
un trait posé par-dessus : ce qui est en dessous existe, il faut juste aller
le chercher.
"""

import os

import charte as C
import dessin as D

RACINE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(RACINE, "resume-ia-au-dessus-des-liens")

L, H = 1600, 900

#  La page, à gauche ; les annotations, à droite.
#  La page DÉBORDE par le bas, au-delà du bord de l'image. Fermée par un bord
#  arrondi, elle donnait un cadre net coupant un résultat par le milieu, ce qui
#  se lit comme une erreur de découpe. Ouverte, elle dit ce qu'il faut : ça
#  continue en dessous.
PAGE = (88, 92, 968, 980)          # gauche, haut, droite, bas hors cadre
MARGE_INT = 34                     # air entre le bord de la page et le contenu

#  La ligne de flottaison : le bas de ce qu'on voit sans faire défiler.
FLOTTAISON = 690

ANNOT = 1046                       # où commence la colonne d'annotations
FIN = 1512

#  Le bleu des liens de résultats. Ce n'est la marque de personne : c'est la
#  convention du web depuis trente ans, et l'article les appelle comme ça.
LIEN = (43, 76, 158)
LIEN_PALE = (150, 166, 202)
BARRE = (222, 221, 216)            # les fausses lignes de texte
BARRE_PALE = (236, 235, 231)
CHIP = (243, 242, 238)

REQUETE = "combien coûte la refonte d’un site internet"

#  Les largeurs des fausses lignes de texte du résumé, en fraction de la
#  colonne. Neuf lignes, pas six : à six, l'aplat violet gardait un grand vide
#  sous le texte, et un bloc à moitié plein n'illustre pas un bloc envahissant.
#  Les fins de paragraphe sont courtes, comme dans du vrai texte.
LIGNES_RESUME = (1.0, 0.97, 1.0, 0.94, 0.58,
                 1.0, 0.96, 0.99, 0.71)


def barre(t, x, y, largeur, hauteur, teinte):
    t.rrect([x, y, x + largeur, y + hauteur], hauteur / 2.0, teinte=teinte)


def resultat(t, x, y, largeur, titre_l, pale):
    """Un résultat classique : un lien, son adresse, deux lignes de texte."""
    lien = LIEN_PALE if pale else LIEN
    fond = BARRE_PALE if pale else BARRE
    barre(t, x, y, largeur * 0.34, 11, fond)                 # le fil d'Ariane
    barre(t, x, y + 26, largeur * titre_l, 17, lien)         # le titre bleu
    barre(t, x, y + 58, largeur * 0.98, 11, fond)
    barre(t, x, y + 78, largeur * 0.71, 11, fond)
    return y + 78 + 11


def accolade(t, x, y0, y1, teinte, epaisseur=3, patte=14):
    """Une accolade droite, ouverte vers la gauche."""
    t.polyligne([(x - patte, y0), (x, y0), (x, y1), (x - patte, y1)],
                teinte, epaisseur)


def principal():
    D.verifier(("encre", D.ENCRE, 4.5),
               ("gris", D.GRIS, 4.5),
               ("violet", D.VIOLET, 4.5),
               ("lien", LIEN, 4.5))
    if C.contraste(D.VIOLET, D.VIOLET_PALE) < 4.5:
        raise SystemExit("le violet ne se lit pas sur son propre aplat")

    t = D.Toile(L, H)

    f_req = t.police(C.POLICE_R, 21)
    f_onglet = t.police(C.POLICE_R, 15)
    f_ia = t.police(C.POLICE_G, 15)
    f_titre = t.police(C.POLICE_G, 19)
    f_sous = t.police(C.POLICE_R, 18)
    f_flot = t.police(C.POLICE_G, 13)
    f_pied = t.police(C.POLICE_R, 15)

    gx0, gy0, gx1, gy1 = PAGE
    dedans = gx0 + MARGE_INT
    colonne = (gx1 - MARGE_INT) - dedans

    #  LA PAGE. Elle déborde par le bas : le contenu continue au-delà de ce que
    #  le dessin montre, comme une vraie page.
    t.rrect([gx0, gy0, gx1, gy1], 14, teinte=D.BLANC, contour=D.FILET,
            epaisseur=2)

    #  Le champ de recherche et la requête.
    y = gy0 + 26
    t.rrect([dedans, y, gx1 - MARGE_INT, y + 52], 26, teinte=(250, 250, 249),
            contour=D.FILET, epaisseur=2)
    t.disque(dedans + 30, y + 26, 8, contour=D.GRIS, epaisseur=3)
    t.ligne([dedans + 36, y + 32, dedans + 44, y + 40], D.GRIS, 3)
    t.texte((dedans + 60, y + 14), D.typo(REQUETE), f_req, D.ENCRE)

    #  Les onglets. Du texte gris pâle, sans soulignement d'onglet actif : la
    #  figure ne parle pas de ça.
    y += 78
    x = dedans
    for mot in ("Tous", "Images", "Vidéos", "Actualités", "Cartes"):
        t.texte((x, y), mot, f_onglet, D.FAIBLE)
        x += t.mesure(mot, f_onglet) + 34
    t.ligne([dedans, y + 30, gx1 - MARGE_INT, y + 30], (238, 237, 233), 2)

    # ------------------------------------------------------------  le résumé
    ia0 = y + 52
    ia1 = FLOTTAISON - 30
    t.rrect([dedans, ia0, gx1 - MARGE_INT, ia1], 12, teinte=D.VIOLET_PALE)

    #  Une étoile à quatre branches, le signe devenu commun pour « généré ».
    cx, cy, r = dedans + 30, ia0 + 32, 11
    t.polygone([(cx, cy - r), (cx + r * 0.3, cy - r * 0.3),
                (cx + r, cy), (cx + r * 0.3, cy + r * 0.3),
                (cx, cy + r), (cx - r * 0.3, cy + r * 0.3),
                (cx - r, cy), (cx - r * 0.3, cy - r * 0.3)], D.VIOLET)
    t.espace((dedans + 54, ia0 + 24), "RÉSUMÉ GÉNÉRÉ PAR IA", f_ia, D.VIOLET,
             1.8)

    yy = ia0 + 72
    for part in LIGNES_RESUME:
        barre(t, dedans + 24, yy, (colonne - 48) * part, 13, (215, 205, 243))
        yy += 30

    #  Les trois sources citées, en pastilles.
    yy += 8
    xx = dedans + 24
    for largeur in (150, 128, 166):
        t.rrect([xx, yy, xx + largeur, yy + 34], 17, teinte=(245, 241, 254),
                contour=(219, 208, 246), epaisseur=2)
        t.disque(xx + 19, yy + 17, 7, teinte=(206, 192, 240))
        barre(t, xx + 34, yy + 12, largeur - 50, 10, (214, 203, 242))
        xx += largeur + 14

    # ------------------------------------------------  ce qu'il faut chercher
    y_res = FLOTTAISON + 32
    y_res = resultat(t, dedans, y_res, colonne, 0.78, True) + 34
    resultat(t, dedans, y_res, colonne, 0.64, True)

    # -------------------------------------------------  la ligne de flottaison
    t.pointilles([(gx0 - 28, FLOTTAISON), (FIN, FLOTTAISON)], D.ENCRE, 2,
                 plein=10, vide=8)
    etiquette = "LIGNE DE FLOTTAISON"
    largeur = t.largeur_espacee(etiquette, f_flot, 1.6)
    t.rrect([gx0 - 28, FLOTTAISON - 15, gx0 - 28 + largeur + 28,
             FLOTTAISON + 15], 15, teinte=D.ENCRE)
    t.espace((gx0 - 14, FLOTTAISON - 8), etiquette, f_flot, D.PAPIER, 1.6)

    # ------------------------------------------------------  les annotations
    #
    #  La mention de nature vient EN TÊTE de la colonne, et pas en pied. Posée
    #  en bas, elle tombait sur le second bloc d'annotation, et le coin haut
    #  droit restait vide. Elle y remplit la page et se lit avant le reste, ce
    #  qui est le bon ordre : on doit savoir ce qu'on regarde avant de le lire.
    yy = 120
    for ligne in t.couper(
            D.typo("Schéma. Ni capture d'écran, ni reproduction d'une "
                   "interface existante : les proportions illustrent le "
                   "propos, elles ne le mesurent pas."),
            f_pied, FIN - ANNOT):
        t.texte((ANNOT, yy), ligne, f_pied, D.FAIBLE)
        yy += 22
    bas_mention = yy + 20
    t.ligne([ANNOT, bas_mention, FIN, bas_mention], D.FILET, 2)

    def bloc(y0, y1, teinte, titre, propos):
        accolade(t, ANNOT, y0, y1, teinte)
        yy = y0 + 4
        t.texte((ANNOT + 30, yy), titre, f_titre, D.ENCRE)
        yy += 32
        for morceau in t.couper(D.typo(propos), f_sous, FIN - ANNOT - 30):
            t.texte((ANNOT + 30, yy), morceau, f_sous, D.GRIS)
            yy += 26
        return yy

    if bas_mention >= ia0 - 20:
        raise SystemExit("la mention de nature touche le premier bloc")
    fin_1 = bloc(ia0, ia1, D.VIOLET, "Le résumé généré par IA",
                 "Il occupe la zone la plus regardée de la page, celle "
                 "qu'on voit sans faire défiler.")
    fin_2 = bloc(FLOTTAISON + 32, H - 14, D.FAIBLE, "Les liens classiques",
                 "Ils commencent sous la ligne de flottaison. Il faut "
                 "vouloir les atteindre.")
    if fin_1 >= FLOTTAISON + 32:
        raise SystemExit("le premier bloc d'annotation déborde sur le second")
    if fin_2 >= H:
        raise SystemExit("le second bloc d'annotation sort de l'image")

    D.enregistrer(t.final(L, H), BASE, L, H)


if __name__ == "__main__":
    principal()
