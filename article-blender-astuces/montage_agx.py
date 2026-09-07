"""
AgX contre Standard : le même rendu, développé de deux façons.

    sh article-blender-astuces/blender-gui/rendre.sh rendu-agx.py agx
    python3 article-blender-astuces/montage_agx.py

Produit `astuces-blender-09-agx-vs-standard.webp` et son PNG.

----------------------------------------------------------------------------
LA SCÈNE N'EST CALCULÉE QU'UNE FOIS
----------------------------------------------------------------------------
Les deux images sortent du MÊME résultat de rendu : seul `view_transform`
change entre les deux enregistrements. C'est ce qui permet d'écrire sous
l'image que la différence vient de la transformation d'affichage et de rien
d'autre — ni bruit d'échantillonnage, ni lampe déplacée. Deux rendus séparés,
même graine, auraient laissé un doute.

C'est aussi ce que fait la case « Save as Render » dont parle l'article : la
même image, écrite avec ou sans la transformation.

----------------------------------------------------------------------------
LES COULEURS SOUS L'IMAGE SONT RELEVÉES, PAS RACONTÉES
----------------------------------------------------------------------------
Blender calcule où se trouve le cube rouge à l'écran et l'écrit dans
`zones.json` ; le montage y relève la couleur médiane d'un carré de soixante
pixels, des deux côtés, et affiche les deux valeurs. La chute de saturation
est calculée sur ces deux relevés. Personne n'a estimé « ça a l'air moins
saturé » : c'est mesuré, et le script refuse la figure si Standard ne ressort
pas plus saturé qu'AgX.

----------------------------------------------------------------------------
ET IL REFUSE AUSSI UNE IMAGE BRÛLÉE
----------------------------------------------------------------------------
Le premier réglage d'éclairage envoyait quinze pour cent de l'image à 255 du
côté Standard — les cent dernières lignes entièrement à fond. Une image
écrêtée ne démontre plus rien : elle montre une erreur d'exposition. Le
contrôle est resté.
"""

import json
import os

import numpy as np
from PIL import Image, ImageDraw

import charte as C

RACINE = os.path.dirname(os.path.abspath(__file__))
TRAVAIL = "/tmp/bl-agx"
BASE = os.path.join(RACINE, "astuces-blender-09-agx-vs-standard")

L = 1600
MARGE = 40
GOUTTIERE = 32

PAPIER = (250, 249, 246)
ENCRE = (24, 25, 30)
FAIBLE = (140, 141, 150)
FILET = (213, 211, 204)

#  Le rendu fait 1280 × 900 et laisse beaucoup de ciel au-dessus des objets.
#  On rogne haut et bas, également des deux côtés : les deux vignettes doivent
#  cadrer exactement pareil, sinon on compare deux images et plus une seule.
COUPE = (0, 130, 1280, 750)

#  Le carré où l'on relève la couleur du cube, autour du point calculé par
#  Blender. Assez large pour moyenner le grain, assez étroit pour rester sur la
#  face avant sans mordre sur le biseau.
SONDE = 60

TRANSFORMS = ("agx", "standard")
TITRES = ("AGX — LE DÉFAUT DEPUIS BLENDER 4.0",
          "STANDARD — LES COULEURS SAISIES")


def typo(t):
    return t.replace("'", "’")


def espace(d, xy, texte, f, teinte, tracking):
    x, y = xy
    for c in texte:
        d.text((x, y), c, font=f, fill=teinte)
        x += d.textlength(c, font=f) + tracking
    return x - tracking


def saturation(rvb):
    """La saturation HSV d'une couleur 0-255, entre 0 et 1."""
    haut, bas = max(rvb), min(rvb)
    return 0.0 if haut == 0 else (haut - bas) / float(haut)


def sonder(im, centre):
    """La couleur médiane d'un carré, en évitant le grain d'un pixel isolé."""
    x, y = centre
    r = SONDE // 2
    if not (r <= x < im.width - r and r <= y < im.height - r):
        raise SystemExit("la sonde sort de l'image : %s" % (centre,))
    carre = np.asarray(im.crop((x - r, y - r, x + r, y + r)), dtype=np.int16)
    return tuple(int(v) for v in np.median(carre.reshape(-1, 3), axis=0))


def principal():
    fiche = os.path.join(TRAVAIL, "zones.json")
    chemins = [os.path.join(TRAVAIL, "agx-%s.png" % t) for t in TRANSFORMS]
    if not os.path.exists(fiche) or any(not os.path.exists(c)
                                        for c in chemins):
        raise SystemExit(
            "rendus absents : lancez d'abord\n"
            "  sh article-blender-astuces/blender-gui/rendre.sh"
            " rendu-agx.py agx")

    with open(fiche, encoding="utf-8") as f:
        fait = json.load(f)

    C.verifier()

    brutes = [Image.open(c).convert("RGB") for c in chemins]
    if len({b.size for b in brutes}) != 1:
        raise SystemExit("les deux rendus n'ont pas la même taille")
    if list(brutes[0].size) != fait["taille"]:
        raise SystemExit("le rendu ne fait pas la taille annoncée")

    #  CONTRÔLE 1 : aucune des deux images ne doit être brûlée.
    for nom, im in zip(TRANSFORMS, brutes):
        a = np.asarray(im)
        part = float((a >= 254).all(axis=2).mean())
        if part > 0.02:
            raise SystemExit("%.1f %% de l'image %s est à fond : l'exposition "
                             "est fautive, pas la transformation"
                             % (100 * part, nom))

    #  CONTRÔLE 2 : les deux images doivent vraiment différer.
    ecart = float(np.mean(np.abs(np.asarray(brutes[0], dtype=np.int16)
                                 - np.asarray(brutes[1], dtype=np.int16))))
    if ecart < 8.0:
        raise SystemExit("les deux images ne diffèrent que de %.1f niveaux : "
                         "la transformation n'a pas été appliquée" % ecart)

    #  CONTRÔLE 3 : et Standard doit ressortir plus saturé qu'AgX, sans quoi la
    #  figure dit le contraire de l'article.
    releves = [sonder(im, fait["rouge_ecran"]) for im in brutes]
    sats = [saturation(c) for c in releves]
    if sats[1] <= sats[0]:
        raise SystemExit("le rouge est aussi saturé en AgX (%.3f) qu'en "
                         "Standard (%.3f)" % (sats[0], sats[1]))
    chute = 100.0 * (1.0 - sats[0] / sats[1])

    vues = [b.crop((COUPE[0], COUPE[1],
                    COUPE[0] + COUPE[2], COUPE[1] + COUPE[3]))
            for b in brutes]
    largeur = (L - 2 * MARGE - GOUTTIERE) // 2
    if largeur > vues[0].width:
        raise SystemExit("les rendus seraient agrandis")
    hauteur = int(round(vues[0].height * largeur / float(vues[0].width)))
    reduites = [v.resize((largeur, hauteur), Image.LANCZOS) for v in vues]

    sous = tuple("le rouge du cube ressort à #%02X%02X%02X" % c
                 for c in releves)
    saisi = fait["rouge_saisi"]
    pied = (
        "Un seul rendu, écrit deux fois : seul View Transform change d'une "
        "image à l'autre. Blender 5.2.1 LTS, EEVEE, %d échantillons."
        % fait["echantillons"],
        "Le rouge saisi dans le matériau est (%.2f, %.2f, %.2f) ; AgX le rend "
        "%.0f %% moins saturé que Standard, mesuré en HSV sur la face avant."
        % (saisi[0], saisi[1], saisi[2], chute),
    )

    f_titre = C.police(C.POLICE_G, 16)
    f_sous = C.police(C.POLICE_R, 17)
    f_pied = C.police(C.POLICE_R, 18)

    y_titre = 56
    y_vue = y_titre + 52
    y_pied = y_vue + hauteur + 40
    H = y_pied + 16 + len(pied) * 24 + 40

    out = Image.new("RGB", (L, H), PAPIER)
    d = ImageDraw.Draw(out)

    for i, vue in enumerate(reduites):
        x = MARGE + i * (largeur + GOUTTIERE)
        fin = espace(d, (x, y_titre), TITRES[i], f_titre, ENCRE, 2.2)
        if fin > x + largeur:
            raise SystemExit("le titre « %s » déborde" % TITRES[i])
        if d.textlength(typo(sous[i]), font=f_sous) > largeur:
            raise SystemExit("le sous-titre %d déborde" % (i + 1))
        d.text((x, y_titre + 24), typo(sous[i]), font=f_sous, fill=FAIBLE)
        out.paste(vue, (x, y_vue))
        d.rectangle([x, y_vue, x + largeur - 1, y_vue + hauteur - 1],
                    outline=FILET, width=1)

    d.line([MARGE, y_pied, L - MARGE, y_pied], fill=FILET, width=1)
    for i, ligne in enumerate(pied):
        ligne = typo(ligne)
        if d.textlength(ligne, font=f_pied) > L - 2 * MARGE:
            raise SystemExit("la ligne %d du pied déborde" % (i + 1))
        d.text((MARGE, y_pied + 16 + i * 24), ligne, font=f_pied, fill=FAIBLE)

    out.save(BASE + ".webp", "WEBP", quality=C.QUALITE, method=6)
    out.save(BASE + ".png", "PNG", optimize=True)
    print()
    print("  rouge saisi (%.2f, %.2f, %.2f)" % tuple(saisi))
    for nom, c, s in zip(TRANSFORMS, releves, sats):
        print("  %-9s #%02X%02X%02X   saturation %.3f" % ((nom,) + c + (s,)))
    print("  chute de saturation %.0f %%, écart moyen %.1f niveaux"
          % (chute, ecart))
    print("  figure %d × %d" % (L, H))
    for e in (".webp", ".png"):
        print("  %-52s %.0f Ko" % (os.path.basename(BASE + e),
                                   os.path.getsize(BASE + e) / 1024))


if __name__ == "__main__":
    principal()
