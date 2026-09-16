"""
Metallic à 0, à 0,5 et à 1 : la même sphère, le même éclairage.

    sh article-blender-shader/rendre.sh rendu_metallic.py metallic
    python3 article-blender-shader/montage_metallic.py

Produit `blender-metallic-0-05-1.webp` et son PNG.

----------------------------------------------------------------------------
UN SEUL RENDU, ET C'EST TOUT L'ARGUMENT
----------------------------------------------------------------------------
Les trois sphères sont dans la même image, calculées ensemble. « Même Base
Color, même Roughness, même éclairage » n'est donc pas une promesse faite sous
la figure : c'est une propriété du fichier. Le script de scène vérifie en plus,
prise par prise, que les trois matériaux ne diffèrent que par Metallic.

----------------------------------------------------------------------------
LA MESURE QUI DIT CE QUE L'OEIL VOIT
----------------------------------------------------------------------------
Ce qui sépare un métal d'une matière diffuse n'est pas sa clarté : c'est la
STRUCTURE de son reflet. Un métal renvoie son entourage en formes nettes, une
matière diffuse le moyenne. L'écart-type des valeurs à l'intérieur de chaque
sphère mesure exactement ça, et il monte régulièrement avec Metallic.

Le montage le relève sur l'image et refuse la figure si la progression n'est
pas dans le bon ordre — sans quoi l'image dirait autre chose que la légende.

----------------------------------------------------------------------------
LE CUIVRE EST PÂLE, ET C'EST NORMAL
----------------------------------------------------------------------------
La Base Color est la réflectance du cuivre poli des tables de rendu physique.
Converti pour l'écran, ce cuivre-là est un rose saumon clair, pas l'orange
soutenu qu'on imagine — celui-là est du cuivre oxydé, ou du cuivre sous une
lumière chaude. Il aurait été facile de forcer la teinte pour « faire cuivre »
dans une section qui reproche justement de régler au jugé.
"""

import json
import os

import numpy as np
from PIL import Image

import charte as C
import dessin as D

RACINE = os.path.dirname(os.path.abspath(__file__))
TRAVAIL = "/tmp/bl-metallic"
BASE = os.path.join(RACINE, "blender-metallic-0-05-1")

L = 1600
MARGE = 56

#  Le rendu fait 1800 × 760 et laisse du ciel au-dessus des sphères, qui
#  occupent les lignes 242 à 498. On coupe au-dessus et sous le sol.
COUPE = (120, 150, 1560, 470)

#  La part du rayon sur laquelle on relève la couleur : le coeur de la sphère,
#  sans son bord, où la silhouette se mêlerait au fond.
SONDE = 0.45

TITRE = "LA MÊME SPHÈRE, SEUL METALLIC CHANGE"
SOUS = "un seul rendu, une seule scène, un seul éclairage"


def principal():
    fiche = os.path.join(TRAVAIL, "zones.json")
    rendu = os.path.join(TRAVAIL, "metallic.png")
    if not os.path.exists(fiche) or not os.path.exists(rendu):
        raise SystemExit(
            "rendu absent : lancez d'abord\n"
            "  sh article-blender-shader/rendre.sh rendu_metallic.py metallic")

    with open(fiche, encoding="utf-8") as f:
        fait = json.load(f)
    brute = Image.open(rendu).convert("RGB")
    if list(brute.size) != fait["taille"]:
        raise SystemExit("le rendu ne fait pas la taille annoncée")

    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5),
               ("violet", D.VIOLET, 4.5))

    a = np.asarray(brute, dtype=np.int16)

    #  CONTRÔLE 1 : aucune sphère brûlée, sans quoi on compare des aplats.
    part = float((a >= 254).all(axis=2).mean())
    if part > 0.01:
        raise SystemExit("%.2f %% du rendu est à fond" % (100 * part))

    releves = []
    for s in fait["spheres"]:
        x, y, r = s["x"], s["y"], int(s["rayon"] * SONDE)
        bloc = a[y - r:y + r, x - r:x + r].reshape(-1, 3)
        releves.append({
            "metallic": s["metallic"],
            "couleur": tuple(int(v) for v in np.median(bloc, axis=0)),
            "structure": float(np.std(bloc.mean(axis=1))),
        })

    #  CONTRÔLE 2 : la structure du reflet doit croître avec Metallic. C'est la
    #  signature du métal, et c'est ce que la figure prétend montrer.
    structures = [r["structure"] for r in releves]
    if not all(b > a_ + 3 for a_, b in zip(structures, structures[1:])):
        raise SystemExit("le reflet ne se structure pas avec Metallic : %s"
                         % ["%.1f" % s for s in structures])

    x0, y0, w, h = COUPE
    vue = brute.crop((x0, y0, x0 + w, y0 + h))
    largeur = L - 2 * MARGE
    if largeur > w:
        raise SystemExit("le rendu serait agrandi")
    echelle = largeur / float(w)
    vue = vue.resize((largeur, int(round(h * echelle))), Image.LANCZOS)

    #  La hauteur de la figure dépend de la vignette : on la calcule d'abord,
    #  on ouvre la toile ensuite.
    y_titre, y_vue = 52, 150
    y_legende = y_vue + vue.height + 34
    y_pied = y_legende + 74
    H = y_pied + 18 + 2 * 24 + 40

    t = D.Toile(L, H)
    f_titre = t.police(C.POLICE_G, 17)
    f_sous = t.police(C.POLICE_R, 18)
    f_nom = t.police(C.POLICE_G, 22)
    f_note = t.police(C.POLICE_R, 17)
    f_pied = t.police(C.POLICE_R, 16)

    t.espace((MARGE, y_titre), TITRE, f_titre, D.ENCRE, 2.2)
    t.texte((MARGE, y_titre + 26), D.typo(SOUS), f_sous, D.FAIBLE)

    t.im.paste(vue.resize((vue.width * t.e, vue.height * t.e), Image.LANCZOS),
               (MARGE * t.e, y_vue * t.e))
    t.rrect([MARGE, y_vue, MARGE + vue.width - 1, y_vue + vue.height - 1], 0,
            contour=D.FILET, epaisseur=2)

    # ---------------------------------------------------------  les étiquettes
    notes = ("une matière diffuse", "ne correspond à rien", "un métal")
    for r, s, note in zip(releves, fait["spheres"], notes):
        milieu = MARGE + (s["x"] - x0) * echelle
        nom = "Metallic %s" % ("%.1f" % r["metallic"]).rstrip("0").rstrip(
            ".").replace(".", ",")
        alerte = r["metallic"] not in (0.0, 1.0)
        largeur_nom = t.mesure(nom, f_nom)
        t.ligne([milieu, y_vue + vue.height, milieu, y_legende - 8],
                D.FILET, 2)
        t.texte((milieu - largeur_nom / 2.0, y_legende), nom, f_nom,
                D.VIOLET if alerte else D.ENCRE)
        largeur_note = t.mesure(D.typo(note), f_note)
        t.texte((milieu - largeur_note / 2.0, y_legende + 34), D.typo(note),
                f_note, D.VIOLET if alerte else D.GRIS)

    # ---------------------------------------------------------------  le pied
    couleurs = "  ".join("#%02X%02X%02X" % r["couleur"] for r in releves)
    pied = (
        "Un seul rendu, Blender %s, EEVEE, %d échantillons. Base Color "
        "commune (%.3f, %.3f, %.3f) — le cuivre poli des tables —, Roughness "
        "%.2f." % (fait["version"], fait["echantillons"],
                   *fait["base_color"], fait["roughness"]),
        "Couleurs relevées au coeur des sphères : %s. Le script de scène "
        "vérifie prise par prise que seul Metallic diffère."
        % couleurs,
    )
    t.ligne([MARGE, y_pied, L - MARGE, y_pied], D.FILET, 2)
    for i, ligne in enumerate(pied):
        ligne = D.typo(ligne)
        if t.mesure(ligne, f_pied) > L - 2 * MARGE:
            raise SystemExit("la ligne %d du pied déborde" % (i + 1))
        t.texte((MARGE, y_pied + 18 + i * 24), ligne, f_pied, D.FAIBLE)

    D.enregistrer(t.final(L, H), BASE, L, H)
    for r in releves:
        print("  metallic %.1f  #%02X%02X%02X  structure du reflet %.1f"
              % ((r["metallic"],) + r["couleur"] + (r["structure"],)))


if __name__ == "__main__":
    principal()
