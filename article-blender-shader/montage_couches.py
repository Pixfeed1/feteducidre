"""
Quatre matériaux, quatre temps de rendu, et ce que le total cache.

    python3 article-blender-shader/texture_source.py
    TRAVAIL=/tmp/bl-couches sh article-blender-shader/rendre.sh \
        bench_couches.py couches
    python3 article-blender-shader/montage_couches.py

Produit `blender-procedural-couches-temps.webp` et son PNG.

----------------------------------------------------------------------------
LA BARRE EST COUPÉE EN DEUX, ET C'EST TOUT LE PROPOS
----------------------------------------------------------------------------
Le temps total d'un rendu comprend ce que la scène coûte de toute façon : la
traversée de la géométrie, les lampes, le film. Ce plancher ne doit rien au
matériau, et il pèse ici les deux tiers du total.

Ne montrer que les totaux aurait donné un écart modeste — une fois et demie
entre l'image et six couches — et laissé croire que le procédural coûte peu.
Ne montrer que la part du matériau aurait donné neuf fois, et laissé croire
qu'il triple tous les rendus. Les deux sont vrais et ne répondent pas à la
même question. La barre les montre ensemble : le gris ne bouge pas, le violet
enfle.

----------------------------------------------------------------------------
CE QUE LA MESURE DIT DE LA PHRASE DE L'ARTICLE
----------------------------------------------------------------------------
« Six couches coûtent trois fois le prix d'une image » ne se retrouve ni dans
une lecture ni dans l'autre : 1,55 fois sur le total, 9,3 fois sur le matériau
seul. Le rapport des totaux dépend d'ailleurs entièrement de la scène — de la
place que le sujet occupe à l'écran et du poids du reste. Un chiffre unique ne
peut pas être vrai partout, et c'est écrit sous la figure.
"""

import json
import os

from PIL import Image

import charte as C
import dessin as D

RACINE = os.path.dirname(os.path.abspath(__file__))
TRAVAIL = "/tmp/bl-couches"
BASE = os.path.join(RACINE, "blender-procedural-couches-temps")

L = 1600
MARGE = 56
GOUTTIERE = 24

#  La mesure de plancher sert au calcul, pas à l'affichage : l'article compare
#  quatre matériaux, pas cinq.
PLANCHER = "Constante"

VIOLET_FOND = (238, 232, 252)
VIOLET = (98, 44, 200)
GRIS_BARRE = (206, 205, 200)

TITRE = "LE MÊME RENDU, QUATRE MATÉRIAUX"
SOUS = "temps de calcul, même scène, même lumière, même nombre d’échantillons"


def duree(s):
    return ("%.2f" % s).replace(".", ",") + " s"


def principal():
    fiche = os.path.join(TRAVAIL, "temps.json")
    if not os.path.exists(fiche):
        raise SystemExit(
            "mesures absentes : lancez d'abord\n"
            "  TRAVAIL=/tmp/bl-couches sh article-blender-shader/rendre.sh"
            " bench_couches.py couches")
    with open(fiche, encoding="utf-8") as f:
        banc = json.load(f)

    toutes = banc["mesures"]
    plancher = next(m for m in toutes if m["nom"] == PLANCHER)["temps"]
    mesures = [m for m in toutes if m["nom"] != PLANCHER]
    if len(mesures) != 4:
        raise SystemExit("%d matériaux à montrer au lieu de quatre"
                         % len(mesures))

    #  CONTRÔLE : les temps doivent croître, sinon la figure dit le contraire
    #  de la légende. Et les tours doivent être serrés, sinon la mesure ne vaut
    #  rien — sur une machine partagée, c'est la première chose à vérifier.
    temps = [m["temps"] for m in mesures]
    if temps != sorted(temps):
        raise SystemExit("les temps ne croissent pas : %s" % temps)
    for m in toutes:
        etendue = (max(m["tours"]) - min(m["tours"])) / min(m["tours"])
        if etendue > 0.05:
            raise SystemExit("« %s » varie de %.1f %% d'un tour à l'autre : "
                             "la machine n'était pas au repos"
                             % (m["nom"], 100 * etendue))

    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5),
               ("violet", VIOLET, 4.5))

    images = []
    for m in mesures:
        chemin = os.path.join(TRAVAIL, m["image"])
        if not os.path.exists(chemin):
            raise SystemExit("rendu absent : %s" % m["image"])
        images.append(Image.open(chemin).convert("RGB"))

    large = (L - 2 * MARGE - 3 * GOUTTIERE) // 4
    if large > images[0].width:
        raise SystemExit("les rendus seraient agrandis")

    y_nom = 148
    y_vue = y_nom + 34
    y_barre = y_vue + large + 42
    y_temps = y_barre + 34
    y_pied = y_temps + 72
    H = y_pied + 18 + 3 * 24 + 40

    t = D.Toile(L, H)
    f_titre = t.police(C.POLICE_G, 17)
    f_sous = t.police(C.POLICE_R, 18)
    f_nom = t.police(C.POLICE_G, 20)
    f_temps = t.police(C.POLICE_G, 24)
    f_note = t.police(C.POLICE_R, 16)
    f_pied = t.police(C.POLICE_R, 16)

    t.espace((MARGE, 52), TITRE, f_titre, D.ENCRE, 2.2)
    t.texte((MARGE, 78), D.typo(SOUS), f_sous, D.FAIBLE)

    # ------------------------------------------------------------  la légende
    #  Elle vit en tête, à droite du titre. Placée sous les panneaux, elle
    #  passait par-dessus la ligne « dont ... de matériau » de chacun d'eux.
    pieces = []
    for teinte, mot in ((GRIS_BARRE, "ce que la scène coûte sans texture"),
                        (VIOLET, "ce que le matériau ajoute")):
        mot = D.typo(mot)
        pieces.append((teinte, mot, t.mesure(mot, f_note)))
    largeur_legende = sum(38 + p[2] for p in pieces) + 34 * (len(pieces) - 1)
    x = L - MARGE - largeur_legende
    occupe = MARGE + max(t.mesure(D.typo(SOUS), f_sous),
                         t.mesure(TITRE, f_titre) + 2.2 * len(TITRE))
    if x < occupe + 40:
        raise SystemExit("la légende touche le titre")
    for teinte, mot, mesure in pieces:
        t.rrect([x, 68, x + 26, 82], 7, teinte=teinte)
        t.texte((x + 38, 64), mot, f_note, D.GRIS)
        x += 38 + mesure + 34

    maxi = max(temps)
    for i, (m, im) in enumerate(zip(mesures, images)):
        x = MARGE + i * (large + GOUTTIERE)
        t.texte((x, y_nom), D.typo(m["nom"]), f_nom, D.ENCRE)

        vue = im.resize((large * t.e, large * t.e), Image.LANCZOS)
        t.im.paste(vue, (x * t.e, y_vue * t.e))
        t.rrect([x, y_vue, x + large - 1, y_vue + large - 1], 0,
                contour=D.FILET, epaisseur=2)

        #  LA BARRE : le plancher en gris, le matériau en violet. Les deux
        #  parts sont à la même échelle d'un panneau à l'autre.
        pleine = large * m["temps"] / maxi
        part = large * plancher / maxi
        t.rrect([x, y_barre, x + pleine, y_barre + 18], 9, teinte=VIOLET)
        t.rrect([x, y_barre, x + part, y_barre + 18], 9, teinte=GRIS_BARRE)

        t.texte((x, y_temps), duree(m["temps"]), f_temps, D.ENCRE)
        note = "dont %s de matériau" % duree(m["ombrage"])
        if t.mesure(note, f_note) > large:
            raise SystemExit("« %s » déborde de son panneau" % note)
        t.texte((x, y_temps + 32), D.typo(note), f_note, VIOLET)

    # ---------------------------------------------------------------  le pied
    image, six = mesures[0], mesures[-1]
    pied = (
        "Cycles sur processeur, %d coeurs, %d × %d, %d échantillons, sans "
        "débruitage. Minimum de %d tours après un tour de chauffe, dans le "
        "même processus."
        % (banc["coeurs"], banc["taille"][0], banc["taille"][1],
           banc["echantillons"], banc["tours"]),
        "Le plancher — la scène sans aucune texture — pèse %s. Sur le TOTAL, "
        "six couches coûtent %s fois une image ; sur le MATÉRIAU seul, %s "
        "fois."
        % (duree(plancher),
           ("%.2f" % (six["temps"] / image["temps"])).replace(".", ","),
           ("%.1f" % (six["ombrage"] / image["ombrage"])).replace(".", ",")),
        "Le rapport des totaux dépend de la scène : ici la sphère occupe "
        "presque tout le cadre. Dans un plan chargé, la part du matériau "
        "compte moins.",
    )
    t.ligne([MARGE, y_pied, L - MARGE, y_pied], D.FILET, 2)
    for i, ligne in enumerate(pied):
        ligne = D.typo(ligne)
        if t.mesure(ligne, f_pied) > L - 2 * MARGE:
            raise SystemExit("la ligne %d du pied déborde" % (i + 1))
        t.texte((MARGE, y_pied + 18 + i * 24), ligne, f_pied, D.FAIBLE)

    D.enregistrer(t.final(L, H), BASE, L, H)
    print("  plancher %s" % duree(plancher))
    for m in mesures:
        print("  %-16s %s total, %s de matériau, × %.2f sur le total"
              % (m["nom"], duree(m["temps"]), duree(m["ombrage"]),
                 m["temps"] / image["temps"]))


if __name__ == "__main__":
    principal()
