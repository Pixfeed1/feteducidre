"""
Schéma — une refonte mise en ligne sans plan de redirections.

    python3 article-agence-web/refonte_sans_redirections.py

Produit `article-agence-web/refonte-sans-redirections-404-trafic.webp` et son
équivalent PNG.

----------------------------------------------------------------------------
DEUX TEMPS, DE GAUCHE À DROITE
----------------------------------------------------------------------------
La phrase de l'article contient une cause et une conséquence : les anciennes
adresses tombent en 404, et le trafic s'effondre. Le schéma les met dans
l'ordre où on les lit.

À gauche, le mécanisme, dessiné : une ancienne adresse, une flèche, et une
fenêtre qui répond 404. Trois éléments, aucun mot de plus que nécessaire.

À droite, la conséquence : une courbe de trafic qui tombe. C'est elle le vrai
sujet de l'image — c'est ce que voit le client, et c'est ce qui fait qu'on
n'oublie plus jamais un plan de redirections.

----------------------------------------------------------------------------
LA COURBE N'A PAS DE CHIFFRES, ET C'EST VOLONTAIRE
----------------------------------------------------------------------------
Aucun axe gradué, aucun pourcentage. Je n'ai pas mesuré CE cas-là, et une
courbe qui annonce « −78 % » invente une précision qu'elle n'a pas. Ce qui est
vrai et suffit à comprendre, c'est la FORME : un palier, une chute nette
au moment de la mise en ligne, un plancher qui ne remonte pas tout seul.

L'aire violette entre le pointillé et la courbe est ce qu'on aurait gardé avec
des redirections. Elle n'est pas chiffrée non plus ; elle se voit, ce qui est
exactement ce qu'on demande à un schéma.

Le tremblement de la courbe vient d'une somme de deux sinusoïdes, pas d'un
tirage au hasard : la figure doit être identique à chaque exécution. Sans ce
tremblement, la ligne ressemble à une équation ; avec, elle ressemble à du
trafic.
"""

import math
import os

import dessin as D

RACINE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(RACINE, "refonte-sans-redirections-404-trafic")

L = 1600
MARGE = 88

SURTITRE = "LE RISQUE LE PLUS COURANT"
TITRE = "Une refonte sans plan de redirections"

ANCIENNE = "/nos-services/creation-site.html"
CAUSE_NOM = "Aucune redirection"
CAUSE_TXT = ("Les adresses de l'ancien site ne mènent plus nulle part. Les "
             "liens des autres sites non plus.")

CHUTE_LABEL = "MISE EN LIGNE"
#  Sur deux lignes, et centrée dans l'aire : posée d'un seul tenant elle
#  passait sur le pointillé du palier, où elle devenait illisible.
GARDE = ("ce que des redirections", "auraient gardé")
DELAI = "quelques jours"


def trafic(x):
    """
    La forme du trafic, entre 0 et 1 en abscisse comme en ordonnée.

    Deux sinusoïdes pour le tremblement — déterministes, donc la figure ne
    change pas d'une exécution à l'autre — et une chute nette au moment de la
    mise en ligne.
    """
    bruit = 0.030 * math.sin(7.1 * x * math.pi) \
        + 0.018 * math.sin(13.7 * x * math.pi + 1.2)
    if x < LANCEMENT:
        return 0.640 + 0.070 * x + bruit
    if x < LANCEMENT + DUREE:
        t = (x - LANCEMENT) / DUREE
        haut = 0.640 + 0.070 * LANCEMENT
        #  Une chute en cosinus plutôt qu'en ligne droite : le trafic ne tombe
        #  pas d'un bloc, il s'éteint sur quelques jours, à mesure que les
        #  pages sortent de l'index.
        return 0.118 + (haut - 0.118) * (1 + math.cos(math.pi * t)) / 2 + bruit
    return 0.104 + bruit * 0.6


def plateau(x):
    """Ce que la courbe aurait fait sans la refonte : le palier, poursuivi."""
    return 0.640 + 0.070 * x \
        + 0.030 * math.sin(7.1 * x * math.pi) \
        + 0.018 * math.sin(13.7 * x * math.pi + 1.2)


LANCEMENT = 0.42
DUREE = 0.11


def fenetre_404(t, x0, y0, larg, haut, f_code, f_petit):
    """Une fenêtre de navigateur qui répond 404."""
    t.rrect([x0, y0, x0 + larg, y0 + haut], 8, teinte=D.BLANC,
            contour=D.GRIS, epaisseur=1.8)
    t.ligne([x0, y0 + 30, x0 + larg, y0 + 30], D.GRIS, 1.6)
    for j in range(3):
        t.disque(x0 + 17 + j * 14, y0 + 15, 3.2, teinte=D.FAIBLE)
    code = "404"
    t.texte((x0 + larg / 2 - t.mesure(code, f_code) / 2, y0 + 52), code,
            f_code, D.ENCRE)
    petit = "page introuvable"
    t.texte((x0 + larg / 2 - t.mesure(petit, f_petit) / 2, y0 + haut - 42),
            petit, f_petit, D.GRIS)


def courbe(t, x0, y0, larg, haut, f_petit, f_caps):
    """La courbe de trafic, son palier perdu et le repère de mise en ligne."""
    n = 320

    def pt(f, i):
        x = i / float(n)
        return x0 + x * larg, y0 + haut - f(x) * haut

    trace = [pt(trafic, i) for i in range(n + 1)]
    ideal = [pt(plateau, i) for i in range(int(n * LANCEMENT), n + 1)]

    #  L'AIRE PERDUE, d'abord : tout se dessine par-dessus.
    aire = ideal + list(reversed(trace[int(n * LANCEMENT):]))
    t.polygone(aire, D.VIOLET_PALE)

    t.ligne([x0, y0 + haut, x0 + larg, y0 + haut], D.FILET, 1.6)
    t.pointilles(ideal, (186, 168, 232), 2, plein=8, vide=7)
    t.polyligne(trace, D.VIOLET, 3)

    #  Le repère de mise en ligne, derrière la courbe en valeur mais devant
    #  l'aire : c'est lui qui date la cassure.
    xl = x0 + LANCEMENT * larg
    t.pointilles([(xl, y0 - 6), (xl, y0 + haut)], D.FAIBLE, 1.6,
                 plein=7, vide=6)
    t.espace((xl + 12, y0 - 22), CHUTE_LABEL, f_caps, D.GRIS, 2.2)

    #  L'accolade du délai, sous la chute.
    xa, xb = xl, x0 + (LANCEMENT + DUREE) * larg
    yb = y0 + haut + 20
    t.ligne([xa, yb, xb, yb], D.FAIBLE, 1.4)
    for x in (xa, xb):
        t.ligne([x, yb - 5, x, yb + 5], D.FAIBLE, 1.4)
    t.texte((xa + (xb - xa) / 2 - t.mesure(DELAI, f_petit) / 2, yb + 10),
            DELAI, f_petit, D.FAIBLE)

    #  L'étiquette de l'aire perdue, centrée dans la partie pleine de l'aire —
    #  là où il n'y a ni le pointillé du palier, ni la courbe.
    milieu = (xb + x0 + larg) / 2
    for i, ligne in enumerate(GARDE):
        large = t.mesure(ligne, f_petit)
        if large > x0 + larg - xb - 24:
            raise SystemExit("« %s » ne tient pas dans l'aire" % ligne)
        t.texte((milieu - large / 2, y0 + haut * 0.46 + i * 24), ligne,
                f_petit, (118, 88, 188))


def principal():
    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5),
               ("faible", D.FAIBLE, 3.0), ("violet", D.VIOLET, 4.5))

    m = D.Toile(10, 10)
    f_sur = m.police(D.C.POLICE_G, 15)
    f_titre = m.police(D.SERIF, 50)
    f_nom = m.police(D.SERIF_G, 27)
    f_txt = m.police(D.C.POLICE_R, 19)
    f_url = m.police(D.C.POLICE_R, 20)
    f_code = m.police(D.SERIF_G, 54)
    f_petit = m.police(D.C.POLICE_R, 17)
    f_caps = m.police(D.C.POLICE_G, 13)

    x_sep = 596
    gauche = x_sep - 52 - MARGE
    x_gr = 664
    larg_gr = L - MARGE - x_gr - 40

    cause = m.couper(D.typo(CAUSE_TXT), f_txt, gauche)

    y_haut = 258
    h_url = 60
    y_fen = y_haut + h_url + 62
    h_fen = 172
    y_nom = y_fen + h_fen + 44
    y_txt = y_nom + 44

    h_gr = 250
    y_gr = 276

    bas = max(y_txt + len(cause) * 26, y_gr + h_gr + 74)
    H = bas + MARGE

    t = D.Toile(L, H)

    # ------------------------------------------------------------  l'en-tête
    t.espace((MARGE, 72), SURTITRE, f_sur, D.VIOLET, 2.6)
    t.texte((MARGE - 3, 100), D.typo(TITRE), f_titre, D.ENCRE)
    if t.mesure(D.typo(TITRE), f_titre) > L - 2 * MARGE:
        raise SystemExit("le titre dépasse la largeur utile")
    t.ligne([MARGE, 206, L - MARGE, 206], D.FILET, 1)

    # ------------------------------------------------------  la cause, à gauche
    t.rrect([MARGE, y_haut, MARGE + gauche, y_haut + h_url], h_url / 2,
            teinte=D.BLANC, contour=D.FILET, epaisseur=2)
    url = D.typo(ANCIENNE)
    if t.mesure(url, f_url) > gauche - 56:
        raise SystemExit("l'ancienne adresse ne tient pas dans la barre")
    t.texte((MARGE + 28, y_haut + h_url / 2 - 14), url, f_url, D.GRIS)

    cx = MARGE + gauche / 2
    t.fleche(cx, y_haut + h_url + 14, cx, y_fen - 12, D.FAIBLE, 2, pointe=9)

    fenetre_404(t, MARGE, y_fen, gauche, h_fen, f_code, f_petit)

    t.texte((MARGE, y_nom), D.typo(CAUSE_NOM), f_nom, D.ENCRE)
    y = y_txt
    for ligne in cause:
        t.texte((MARGE, y), ligne, f_txt, D.GRIS)
        y += 26

    t.ligne([x_sep, y_haut - 20, x_sep, bas - 10], D.FILET, 1)

    # ------------------------------------------  la conséquence, à droite
    t.espace((x_gr, y_gr - 46), "TRAFIC DEPUIS LES MOTEURS", f_caps,
             D.FAIBLE, 2.2)
    courbe(t, x_gr, y_gr, larg_gr, h_gr, f_petit, f_caps)

    D.enregistrer(t.final(L, H), BASE, L, H)


if __name__ == "__main__":
    principal()
