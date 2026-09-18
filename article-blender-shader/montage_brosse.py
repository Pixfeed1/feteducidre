"""
Le métal brossé, et la preuve que les stries sont des stries.

    SORTIE=/tmp/bl-brosse python3 article-blender-shader/rendu_brosse.py
    python3 article-blender-shader/montage_brosse.py

Produit `blender-metal-brosse.webp` et son PNG.

----------------------------------------------------------------------------
UN DÉTAIL À L'ÉCHELLE, PARCE QUE LA FIGURE EST ILLISIBLE SANS LUI
----------------------------------------------------------------------------
Le brossage vit à la limite de ce qu'un pixel peut porter : réduite à la
largeur d'une colonne d'article, la sphère redevient une bille grise. Le
panneau de droite est un morceau du même rendu, agrandi, non retouché. Sans
lui, la légende parlerait de stries que personne ne verrait.

----------------------------------------------------------------------------
LA MESURE QUI REMPLACE « ON VOIT BIEN QUE »
----------------------------------------------------------------------------
Dire que des reflets sont « étirés » est une impression. On peut la vérifier.

L'image est d'abord passée en haute fréquence — on lui retire sa version
floue —, ce qui enlève l'ombrage de la sphère et ne laisse que le grain. On
compare ensuite, sur ce grain, la variation d'un pixel à son voisin de droite
et à son voisin du dessous. Du bruit isotrope donne un rapport de 1. Des
stries verticales donnent beaucoup plus.

Le montage refuse la figure si le rapport n'y est pas : une sphère grise et
lisse ne doit pas pouvoir sortir d'ici avec une légende qui parle de brossage.
"""

import json
import os

import numpy as np
from PIL import Image, ImageFilter

import charte as C
import dessin as D

RACINE = os.path.dirname(os.path.abspath(__file__))
TRAVAIL = os.environ.get("TRAVAIL", "/tmp/bl-brosse")
BASE = os.path.join(RACINE, "blender-metal-brosse")

L = 1600
MARGE = 56
GOUTTIERE = 24

LARGE_VUE = 1010
LARGE_DETAIL = L - 2 * MARGE - GOUTTIERE - LARGE_VUE

#  Le détail est pris en bas à gauche, dans la bande sombre. Un premier essai
#  le prenait en haut à droite, en plein sur la tache de lumière : les stries
#  y sont lavées par la haute lumière et l'agrandissement ne montrait qu'un
#  flou clair. Mesuré — le grain y vaut 0,27 en travers contre 0,54 ici.
#  Repéré en fractions de rayon, donc valable quelle que soit la focale.
DETAIL_CENTRE = (-0.34, 0.34)
DETAIL_COTE = 0.22

#  La vue d'ensemble est recadrée autour de la sphère : le rendu laisse de
#  part et d'autre un fond vide qui, à la largeur d'une colonne d'article,
#  ne sert qu'à rapetisser le sujet.
CADRE = 2.05
#  Le seuil ne sort pas du chapeau : il vient d'un témoin, la MÊME scène
#  rendue avec un Mapping Scale de 1 / 1 / 1, c'est-à-dire le bruit sans
#  l'écrasement, rendu à la MÊME définition — sans quoi on comparerait deux
#  conditions. Le témoin mesure 1,28, le 1 / 120 / 1 de l'article 5,19 ; on
#  coupe entre les deux, en moyenne géométrique.
#
#  Le rapport dépend de la définition du rendu, et il faut le dire : à
#  700 × 380 le même matériau ne mesure plus que 1,90, parce que les stries
#  passent sous le pixel. Le seuil vaut donc pour la taille livrée ici — et
#  c'est aussi pourquoi la figure porte un détail agrandi.
ANISOTROPIE_MINIMALE = 2.8

TITRE = "LE MÉTAL BROSSÉ, VALEURS COMPRISES"
SOUS = "un bruit écrasé sur un seul axe, et rien d’autre"


def virgule(x, chiffres=2):
    return (("%." + str(chiffres) + "f") % x).replace(".", ",")


def anisotropie(vue, centre, rayon):
    """Variation en travers des stries contre variation le long des stries.

    On ne compare PAS un pixel à son voisin : à cette échelle, le bruit du
    rendu — isotrope, et non débruité ici — domine tout et écrase le rapport
    à 1,5 quelle que soit l'image. Mesuré.

    On compare les MOYENNES de colonnes aux moyennes de lignes. Moyenner une
    colonne entière divise le bruit par la racine du nombre de pixels et
    laisse intact ce qui est cohérent sur toute la hauteur : une strie
    verticale. C'est exactement la distinction que la figure prétend montrer.
    """
    gris = vue.convert("L")
    #  On retire d'abord l'image floue de l'image nette : il ne reste que le
    #  grain. Sans ça, on mesurerait surtout l'ombrage de la sphère, qui
    #  varie beaucoup du haut vers le bas et fausserait tout.
    haute = (np.asarray(gris, dtype=np.float32)
             - np.asarray(gris.filter(ImageFilter.GaussianBlur(2.6)),
                          dtype=np.float32))
    r = int(rayon * 0.62)
    x, y = centre
    bloc = haute[y - r:y + r, x - r:x + r]
    travers = float(bloc.mean(axis=0).std())
    long = float(bloc.mean(axis=1).std())
    return travers, long, travers / long if long > 0 else float("inf")


def principal():
    fiche = os.path.join(TRAVAIL, "brosse.json")
    rendu = os.path.join(TRAVAIL, "brosse.png")
    if not os.path.exists(fiche) or not os.path.exists(rendu):
        raise SystemExit(
            "rendu absent : lancez d'abord\n"
            "  SORTIE=%s python3 article-blender-shader/rendu_brosse.py"
            % TRAVAIL)

    with open(fiche, encoding="utf-8") as f:
        fait = json.load(f)
    brut = Image.open(rendu).convert("RGB")
    if list(brut.size) != fait["taille"]:
        raise SystemExit("le rendu ne fait pas la taille annoncée")

    v = fait["valeurs"]
    s = fait["sphere"]
    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5),
               ("violet", D.VIOLET, 4.5))

    a = np.asarray(brut, dtype=np.int16)
    #  CONTRÔLE 1 : rien de brûlé, sinon les stries seraient mangées par les
    #  hautes lumières là où justement on prétend les montrer.
    brule = float((a >= 254).all(axis=2).mean())
    if brule > 0.005:
        raise SystemExit("%s %% du rendu est à fond" % virgule(100 * brule))

    #  CONTRÔLE 2 : les stries doivent être des stries.
    travers, long, rapport = anisotropie(brut, (s["x"], s["y"]), s["rayon"])
    if rapport < ANISOTROPIE_MINIMALE:
        raise SystemExit(
            "le grain est isotrope (rapport %s) : ce n'est pas du brossage"
            % virgule(rapport))

    # -----------------------------------------------------  la vue d'ensemble
    #  Un recadrage horizontal centré sur la sphère, jamais plus large que le
    #  rendu et toujours assez large pour contenir la sphère entière.
    demi = int(round(CADRE * s["rayon"]))
    if demi < s["rayon"] + 12:
        raise SystemExit("le recadrage couperait la sphère")
    x0 = max(0, min(s["x"] - demi, brut.width - 2 * demi))
    coupe = brut.crop((x0, 0, min(x0 + 2 * demi, brut.width), brut.height))
    hauteur_vue = int(round(LARGE_VUE * coupe.height / float(coupe.width)))
    if LARGE_VUE > coupe.width:
        raise SystemExit("le rendu serait agrandi")
    vue = coupe.resize((LARGE_VUE, hauteur_vue), Image.LANCZOS)
    echelle = LARGE_VUE / float(coupe.width)

    # -----------------------------------------------------------  le détail
    cote = int(round(s["rayon"] * DETAIL_COTE))
    dx = int(round(s["x"] + DETAIL_CENTRE[0] * s["rayon"]))
    dy = int(round(s["y"] + DETAIL_CENTRE[1] * s["rayon"]))
    boite = (dx - cote, dy - cote, dx + cote, dy + cote)
    #  Le morceau doit rester sur la sphère : hors d'elle, il ne montrerait
    #  que du décor et la figure prouverait le contraire de ce qu'elle dit.
    for px, py in ((boite[0], boite[1]), (boite[2], boite[1]),
                   (boite[0], boite[3]), (boite[2], boite[3])):
        if (px - s["x"]) ** 2 + (py - s["y"]) ** 2 > (0.92 * s["rayon"]) ** 2:
            raise SystemExit("le détail déborde de la sphère")
    #  NEAREST et non LANCZOS : on agrandit pour montrer les pixels du rendu,
    #  pas pour en inventer d'intermédiaires.
    detail = brut.crop(boite).resize((LARGE_DETAIL, LARGE_DETAIL),
                                     Image.NEAREST)
    facteur = LARGE_DETAIL / float(2 * cote)

    hauteur_panneau = max(hauteur_vue, LARGE_DETAIL)
    y_vue = 150
    y_note = y_vue + hauteur_panneau + 20
    y_pied = y_note + 46
    H = y_pied + 18 + 3 * 24 + 40

    t = D.Toile(L, H)
    f_titre = t.police(C.POLICE_G, 17)
    f_sous = t.police(C.POLICE_R, 18)
    f_note = t.police(C.POLICE_R, 16)
    f_pied = t.police(C.POLICE_R, 16)

    t.espace((MARGE, 52), TITRE, f_titre, D.ENCRE, 2.2)
    t.texte((MARGE, 78), D.typo(SOUS), f_sous, D.FAIBLE)

    y_haut = y_vue + (hauteur_panneau - hauteur_vue) // 2
    t.im.paste(vue.resize((vue.width * t.e, vue.height * t.e), Image.LANCZOS),
               (MARGE * t.e, y_haut * t.e))
    t.rrect([MARGE, y_haut, MARGE + vue.width - 1,
             y_haut + vue.height - 1], 0, contour=D.FILET, epaisseur=2)

    x_detail = MARGE + LARGE_VUE + GOUTTIERE
    y1 = y_vue + (hauteur_panneau - LARGE_DETAIL) // 2
    t.im.paste(detail.resize((detail.width * t.e, detail.height * t.e),
                             Image.NEAREST),
               (x_detail * t.e, y1 * t.e))
    t.rrect([x_detail, y1, x_detail + LARGE_DETAIL - 1,
             y1 + LARGE_DETAIL - 1], 0, contour=D.VIOLET, epaisseur=3)

    #  Le cadre qui dit d'où vient le morceau, ramené dans le repère de la
    #  vue recadrée puis mis à son échelle.
    t.rrect([MARGE + (boite[0] - x0) * echelle, y_haut + boite[1] * echelle,
             MARGE + (boite[2] - x0) * echelle, y_haut + boite[3] * echelle],
            0, contour=D.VIOLET, epaisseur=3)

    t.texte((MARGE, y_note), D.typo("la sphère entière, telle qu'elle sort "
                                    "de Cycles"), f_note, D.GRIS)
    note = D.typo("le cadre violet, agrandi %s fois" % virgule(facteur, 1))
    if t.mesure(note, f_note) > LARGE_DETAIL:
        raise SystemExit("la note du détail déborde de son panneau")
    t.texte((x_detail, y_note), note, f_note, D.VIOLET)

    # ---------------------------------------------------------------  le pied
    pied = (
        "Cycles, Blender %s, %d échantillons, sans débruitage, objectif "
        "%d mm. Base Color %s / %s / %s, Metallic %d."
        % (fait["version"], fait["echantillons"], fait["objectif"],
           virgule(v["Base Color"][0]), virgule(v["Base Color"][1]),
           virgule(v["Base Color"][2]), v["Metallic"]),
        "Texture Coordinate Object, Mapping Scale %d / %d / %d, Noise Scale "
        "%d Detail %d, Color Ramp %s et %s, Map Range %s à %s sur Roughness, "
        "Fac vers Bump %s sur Normal."
        % (v["Mapping Scale"][0], v["Mapping Scale"][1], v["Mapping Scale"][2],
           v["Noise Scale"], v["Noise Detail"],
           virgule(v["Color Ramp"][0]), virgule(v["Color Ramp"][1]),
           virgule(v["Map Range To Min"]), virgule(v["Map Range To Max"]),
           virgule(v["Bump Strength"])),
        "Le grain varie %s fois plus en travers des stries que le long : "
        "c'est du brossage et pas du bruit. Le Scale porte sur Y, donc la "
        "caméra regarde depuis X ; depuis Y, on verrait des anneaux."
        % virgule(rapport, 1),
    )
    t.ligne([MARGE, y_pied, L - MARGE, y_pied], D.FILET, 2)
    for i, ligne in enumerate(pied):
        ligne = D.typo(ligne)
        if t.mesure(ligne, f_pied) > L - 2 * MARGE:
            raise SystemExit("la ligne %d du pied déborde" % (i + 1))
        t.texte((MARGE, y_pied + 18 + i * 24), ligne, f_pied, D.FAIBLE)

    D.enregistrer(t.final(L, H), BASE, L, H)
    print("  sphère x=%d y=%d rayon=%d" % (s["x"], s["y"], s["rayon"]))
    print("  grain : %.3f en travers, %.3f le long, rapport %.2f"
          % (travers, long, rapport))
    print("  détail : %d px du rendu agrandis %.1f fois" % (2 * cote, facteur))


if __name__ == "__main__":
    principal()
