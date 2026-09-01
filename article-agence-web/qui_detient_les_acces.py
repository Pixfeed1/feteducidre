"""
Figure de la question 3 — « Qui détient les accès ? »

    python3 article-agence-web/qui_detient_les_acces.py

Produit `article-agence-web/qui-detient-les-acces-site-web.webp` et son
équivalent PNG.

----------------------------------------------------------------------------
CE QUI A ÉTÉ JETÉ, ET POURQUOI
----------------------------------------------------------------------------
La première version avait la tête de tous les schémas qu'on voit passer :
quatre cartes à coins arrondis, des pastilles de couleur, un bandeau rouge
d'alerte. Chaque élément était défendable et l'ensemble ne ressemblait à rien
d'autre qu'à un gabarit.

Le rouge d'alerte était le pire. Il crie, et ce paragraphe ne crie pas : il
explique posément qu'un accès sur quatre ne se rattrape pas. Une couleur
d'alarme met les quatre lignes au même niveau de tension, alors que tout le
propos est qu'il y en a une qui n'est pas comme les autres.

----------------------------------------------------------------------------
CE QUI LE REMPLACE
----------------------------------------------------------------------------
De la typographie, et presque rien d'autre.

Le domaine occupe un bandeau plein qui traverse toute l'image, bord à bord —
encre sombre, texte clair. Les trois autres sont posés dessous sur le papier,
séparés par des filets d'un pixel. L'inversion fait le travail que faisait le
rouge, sans le ton d'alarme : une ligne est traitée autrement, on la voit
avant de l'avoir lue.

Le reste suit la même règle. Un serif pour les intitulés, un italique pour les
réserves, des capitales espacées pour les verdicts, et de la marge. Aucun coin
arrondi, aucune pastille, aucune ombre portée.

L'ocre du bandeau n'est pas une couleur d'alerte, c'est la seule teinte chaude
qui tienne le contraste sur l'encre (7,4:1 mesuré). Elle attire l'oeil sans
dire « attention ».
"""

import os

from PIL import Image, ImageDraw

import charte as C

RACINE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(RACINE, "qui-detient-les-acces-site-web")

L = 1600
MARGE = 96

#  Une palette de papier, propre à cette figure. Le fond gris-bleu de la charte
#  va bien aux schémas techniques du site ; ici on cherche une page, pas un
#  écran, et un blanc légèrement chaud fait toute la différence sur un aplat
#  d'encre aussi large.
PAPIER = (250, 249, 245)
ENCRE = (26, 27, 32)
GRIS = (98, 100, 110)
FAIBLE = (136, 137, 147)
FILET = (216, 214, 206)
SUR_ENCRE = (243, 241, 235)
DISCRET = (158, 158, 166)
OCRE = (214, 160, 74)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_G = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"

SURTITRE = "QUESTION 3"
TITRE = "Qui détient les accès ?"

DOMAINE = {
    "numero": "01",
    "titre": "Le nom de domaine",
    "texte": "À votre nom, dans votre compte, chez votre bureau "
             "d'enregistrement.",
    "reserve": "Pas « géré par » l'agence.",
    "verdict": "NE SE RÉCUPÈRE PAS",
    "note": "une procédure de plusieurs mois, quand elle aboutit",
}

AUTRES = (
    {
        "numero": "02",
        "titre": "L'hébergement",
        "texte": "Vous devez pouvoir y accéder et le résilier sans passer par "
                 "un tiers.",
        "verdict": "SE REPREND",
        "note": None,
    },
    {
        "numero": "03",
        "titre": "L'administration du site",
        "texte": "Un compte administrateur à votre nom, pas un identifiant "
                 "partagé transmis par message.",
        "verdict": "SE REPREND",
        "note": None,
    },
    {
        "numero": "04",
        "titre": "Les comptes Google",
        "texte": "Search Console, Analytics, fiche d'établissement : vous "
                 "propriétaire, l'agence ajoutée comme utilisateur.",
        "verdict": "SE REPREND",
        "note": "l'historique, non",
    },
)


def typo(texte):
    """
    L'apostrophe courbe, celle des livres.

    La droite est un caractère de machine à écrire que les claviers ont gardé.
    Sur un titre en serif de 56 points, la différence entre « L'hébergement »
    et « L’hébergement » se voit à un mètre, et c'est le genre de détail qui
    sépare une page composée d'un export de gabarit.
    """
    return texte.replace("'", "’")


def couper(d, texte, f, largeur):
    ligne, lignes = "", []
    for m in texte.split():
        essai = (ligne + " " + m).strip()
        if d.textlength(essai, font=f) > largeur and ligne:
            lignes.append(ligne)
            ligne = m
        else:
            ligne = essai
    lignes.append(ligne)
    return lignes


def largeur_espacee(d, texte, f, tracking):
    """La largeur d'une ligne de capitales espacées."""
    return sum(d.textlength(c, font=f) for c in texte) \
        + tracking * max(len(texte) - 1, 0)


def espace(d, xy, texte, f, teinte, tracking):
    """
    Des capitales, lettre à lettre, avec de l'air entre elles.

    PIL ne sait pas espacer un texte. On le dessine donc caractère par
    caractère — c'est ce qui distingue une petite capitale composée d'une
    étiquette de gabarit, et ça ne coûte que trois lignes.
    """
    x, y = xy
    for c in texte:
        d.text((x, y), c, font=f, fill=teinte)
        x += d.textlength(c, font=f) + tracking
    return x - tracking


def verifier_sur_encre():
    """Les deux couleurs posées sur l'aplat sombre, avant de dessiner."""
    for nom, teinte, seuil in (("papier sur encre", SUR_ENCRE, 4.5),
                               ("ocre sur encre", OCRE, 4.5),
                               ("discret sur encre", DISCRET, 4.5)):
        r = C.contraste(teinte, ENCRE)
        print("  %-20s %-16s %.2f:1  %s"
              % (nom, str(teinte), r, "ok" if r >= seuil else "INSUFFISANT"))
        if r < seuil:
            raise SystemExit("%s : %.2f:1, sous le seuil" % (nom, r))


def principal():
    verifier_sur_encre()
    for nom, teinte, seuil in (("encre sur papier", ENCRE, 4.5),
                               ("gris sur papier", GRIS, 4.5),
                               ("faible sur papier", FAIBLE, 3.0)):
        r = C.contraste(teinte, PAPIER)
        print("  %-20s %-16s %.2f:1  %s"
              % (nom, str(teinte), r, "ok" if r >= seuil else "INSUFFISANT"))
        if r < seuil:
            raise SystemExit("%s : %.2f:1, sous le seuil" % (nom, r))

    mesure = ImageDraw.Draw(Image.new("RGB", (10, 10)))

    f_sur = C.police(C.POLICE_G, 15)
    f_titre = C.police(SERIF, 56)
    f_num_d = C.police(SERIF, 46)
    f_num = C.police(SERIF, 34)
    f_nom_d = C.police(SERIF_G, 36)
    f_nom = C.police(SERIF_G, 27)
    f_txt_d = C.police(C.POLICE_R, 22)
    f_txt = C.police(C.POLICE_R, 20)
    f_res = C.police(SERIF_I, 22)
    f_verd_d = C.police(C.POLICE_G, 16)
    f_verd = C.police(C.POLICE_G, 14)
    f_note = C.police(SERIF_I, 17)

    #  La colonne de droite est dimensionnée sur le plus large des verdicts,
    #  jamais sur une valeur choisie à la main : c'est ce qui garantit que les
    #  quatre lignes s'alignent quoi qu'on écrive dedans.
    droite = max(
        largeur_espacee(mesure, DOMAINE["verdict"], f_verd_d, 2.4),
        mesure.textlength(DOMAINE["note"], font=f_note),
        max(largeur_espacee(mesure, c["verdict"], f_verd, 2.2)
            for c in AUTRES))
    x_droite = L - MARGE - int(droite)

    x_txt = MARGE + 92
    largeur_txt = x_droite - 64 - x_txt

    dom_lignes = couper(mesure, typo(DOMAINE["texte"]), f_txt_d, largeur_txt)
    plies = [couper(mesure, typo(c["texte"]), f_txt, largeur_txt)
             for c in AUTRES]

    h_bande = 46 + 42 + 14 + len(dom_lignes) * 31 + 10 + 30 + 46
    hauteurs = [34 + 34 + 10 + len(p) * 27 + 34 for p in plies]

    y_titre = 96
    y_filet = y_titre + 88
    y_bande = y_filet + 46
    y_lignes = y_bande + h_bande + 4
    H = y_lignes + sum(hauteurs) + 44

    out = Image.new("RGB", (L, H), PAPIER)
    d = ImageDraw.Draw(out)

    # ------------------------------------------------------------  l'en-tête
    espace(d, (MARGE, y_titre - 30), SURTITRE, f_sur, C.VIOLET_TEXTE, 2.6)
    d.text((MARGE - 3, y_titre), typo(TITRE), font=f_titre, fill=ENCRE)
    d.line([MARGE, y_filet, L - MARGE, y_filet], fill=FILET, width=1)

    # ---------------------------------------------------  le bandeau, bord à bord
    #  Il traverse toute l'image, sans marge : c'est ce débord qui le fait lire
    #  comme un bandeau de page et non comme une carte posée sur un fond.
    d.rectangle([0, y_bande, L, y_bande + h_bande], fill=ENCRE)

    y = y_bande + 46
    d.text((MARGE, y - 4), DOMAINE["numero"], font=f_num_d, fill=OCRE)
    d.text((x_txt, y), typo(DOMAINE["titre"]), font=f_nom_d, fill=SUR_ENCRE)
    y += 42 + 14
    for t in dom_lignes:
        d.text((x_txt, y), t, font=f_txt_d, fill=(216, 214, 208))
        y += 31
    y += 10
    d.text((x_txt, y), typo(DOMAINE["reserve"]), font=f_res, fill=DISCRET)

    yv = y_bande + 52
    espace(d, (x_droite, yv), DOMAINE["verdict"], f_verd_d, OCRE, 2.4)
    d.text((x_droite, yv + 34), typo(DOMAINE["note"]), font=f_note,
           fill=DISCRET)

    # ------------------------------------------------------  les trois autres
    y0 = y_lignes
    for carte, lignes, h in zip(AUTRES, plies, hauteurs):
        d.text((MARGE, y0 + 30), carte["numero"], font=f_num, fill=FAIBLE)
        d.text((x_txt, y0 + 30), typo(carte["titre"]), font=f_nom, fill=ENCRE)
        y = y0 + 34 + 34 + 10
        for t in lignes:
            d.text((x_txt, y), t, font=f_txt, fill=GRIS)
            y += 27

        espace(d, (x_droite, y0 + 38), carte["verdict"], f_verd, FAIBLE, 2.2)
        if carte["note"]:
            d.text((x_droite, y0 + 62), typo(carte["note"]), font=f_note,
                   fill=FAIBLE)

        if y > y0 + h - 4:
            raise SystemExit("« %s » déborde de sa ligne de %.0f px"
                             % (carte["titre"], y - (y0 + h - 4)))
        y0 += h
        if carte is not AUTRES[-1]:
            d.line([MARGE, y0, L - MARGE, y0], fill=FILET, width=1)

    out.save(BASE + ".webp", "WEBP", quality=C.QUALITE, method=6)
    out.save(BASE + ".png", "PNG", optimize=True)
    print()
    print("  %d × %d" % out.size)
    for e in (".webp", ".png"):
        print("  %-44s %.0f Ko" % (os.path.basename(BASE + e),
                                   os.path.getsize(BASE + e) / 1024))


if __name__ == "__main__":
    principal()
