"""
IMAGE 8 de l'article — la fuite de lumière, montée.

    python3 article/montage_fuite.py

Lit `article/fuite.json` et produit `article/light-probe-fuite-lumiere-erreur.webp`.

----------------------------------------------------------------------------
LA COTE QUI PORTE TOUT : LA MAILLE CONTRE LE MUR
----------------------------------------------------------------------------
La figure n'affiche pas « 4 × 3 × 2 » contre « 40 × 24 × 14 ». Ces nombres ne
disent rien : ils dépendent de la taille de la pièce. Elle affiche la TAILLE
DE MAILLE en mètres à côté de l'ÉPAISSEUR DU MUR, parce que c'est la
comparaison de ces deux longueurs qui décide de la fuite.

    maille 2,12 m  contre  mur 0,30 m   ->  la lumière traverse
    maille 0,21 m  contre  mur 0,30 m   ->  elle ne traverse plus

Un lecteur qui a une autre pièce et un autre mur peut appliquer la règle. Un
lecteur à qui on donne « mettez 40 » ne peut rien en faire.

----------------------------------------------------------------------------
LE TÉMOIN SANS SONDE N'EST PAS UNE TROISIÈME VIGNETTE
----------------------------------------------------------------------------
La passe sans sonde sert à savoir ce que la pièce sombre vaut quand rien ne
peut y entrer. Elle ne mérite pas une image — les deux seraient noires — mais
elle mérite son chiffre : c'est lui qui transforme « la version fine est plus
sombre » en « la version fine ne laisse plus rien passer ».
"""

import json
import os
import re

from PIL import Image, ImageDraw, ImageFont

RACINE = os.path.dirname(os.path.abspath(__file__))
JOURNAL = os.path.join(RACINE, "fuite.json")
SORTIE = os.path.join(RACINE, "light-probe-fuite-lumiere-erreur.webp")

VIGNETTE_L = 830
GOUTTIERE = 30
MARGE = 34
BANDE_TITRE = 76

ENCRE = (13, 13, 17)
BLANC = (238, 238, 243)
GRIS = (138, 138, 150)
FAIBLE = (104, 104, 116)
TEAL = (72, 224, 184)
ROUGE = (214, 118, 96)

POLICE_G = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
POLICE_R = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
QUALITE = 92


def nb(gabarit, valeur):
    """Ne convertit que les points entourés de chiffres — un `replace` global
    transformerait aussi les points de fin de phrase en virgules."""
    return re.sub(r"(?<=\d)\.(?=\d)", ",", gabarit % valeur)


def police(chemin, taille):
    try:
        return ImageFont.truetype(chemin, taille)
    except OSError:
        return ImageFont.load_default()


def principal():
    if not os.path.exists(JOURNAL):
        raise SystemExit("mesures absentes : %s\n        lancez d'abord "
                         "`python3 article/fuite_lumiere.py`" % JOURNAL)
    d0 = json.load(open(JOURNAL))
    par = {p["nom"]: p for p in d0["passes"]}
    gros, fin, nu = par["grossiere"], par["fine"], par["sans-sonde"]
    mur = d0["cloison_m"]

    #  Le plancher, c'est la passe SANS sonde : ce que la pièce close vaut
    #  quand aucune lumière ne peut l'atteindre.
    plancher = nu["luminance"]
    fuite = gros["luminance"] - plancher
    reste = fin["luminance"] - plancher
    if fuite <= 0:
        raise SystemExit("la grille grossiere ne fuit pas (%+.2f) : la figure "
                         "n'a rien a montrer" % fuite)

    ims = {k: Image.open(os.path.join(RACINE, par[k]["image"])).convert("RGB")
           for k in ("grossiere", "fine")}
    w0, h0 = ims["grossiere"].size
    hv = int(round(VIGNETTE_L * h0 / w0))

    L = MARGE * 2 + VIGNETTE_L * 2 + GOUTTIERE
    H = MARGE + BANDE_TITRE + hv + 30 + 118 + 30 + 27 * 4 + 46 + MARGE
    out = Image.new("RGB", (L, H), ENCRE)
    d = ImageDraw.Draw(out, "RGBA")

    f_titre = police(POLICE_G, 31)
    f_col = police(POLICE_G, 26)
    f_chiffre = police(POLICE_G, 42)
    f_txt = police(POLICE_R, 22)
    f_petit = police(POLICE_R, 19)

    d.rectangle([MARGE, MARGE + 14, MARGE + 10, MARGE + 46], fill=ROUGE)
    d.text((MARGE + 24, MARGE + 10),
           "UNE MAILLE PLUS LARGE QUE LE MUR, ET LE MUR N'EXISTE PLUS",
           font=f_titre, fill=BLANC)

    y_img = MARGE + BANDE_TITRE
    ordre = (("grossiere", "LA FUITE", ROUGE),
             ("fine", "LE MUR TIENT", TEAL))
    for i, (cle, titre, teinte) in enumerate(ordre):
        x = MARGE + i * (VIGNETTE_L + GOUTTIERE)
        p = par[cle]
        out.paste(ims[cle].resize((VIGNETTE_L, hv), Image.LANCZOS), (x, y_img))

        #  Le cadre de mesure, le même des deux côtés.
        cx0, cx1, cy0, cy1 = d0["controle"]
        d.rectangle([x + VIGNETTE_L * cx0, y_img + hv * cy0,
                     x + VIGNETTE_L * cx1, y_img + hv * cy1],
                    outline=(255, 255, 255, 150), width=2)

        yb = y_img + hv + 26
        d.rectangle([x, yb, x + 10, yb + 30], fill=teinte)
        d.text((x + 22, yb - 4), titre, font=f_col, fill=BLANC)

        m = p["maille_m"]
        d.text((x, yb + 40),
               nb("maille %.2f m", m[0]) + nb(" × %.2f", m[1])
               + nb(" × %.2f m", m[2]),
               font=f_txt, fill=GRIS)
        d.text((x, yb + 70),
               nb("mur : %.2f m", mur) + "  —  "
               + ("la maille est PLUS LARGE que le mur"
                  if m[0] > mur else "la maille tient sous le mur"),
               font=f_txt, fill=teinte)

        val = p["luminance"]
        d.text((x + 470, yb + 28), nb("%.1f", val), font=f_chiffre,
               fill=teinte)
        d.text((x + 470, yb + 78), "luminance du cadre blanc, sur 255",
               font=f_petit, fill=FAIBLE)

    y = y_img + hv + 30 + 118 + 30
    d.line([MARGE, y - 16, L - MARGE, y - 16], fill=(46, 46, 56), width=1)
    texte = [
        nb("Les deux pièces sont séparées par un refend plein de %.2f m, "
           "du sol au plafond, sans la moindre ouverture.", mur),
        nb("Sans aucune sonde, la pièce de droite mesure %.1f/255 : c'est ce "
           "qu'elle vaut quand rien ne peut l'atteindre.", plancher)
        + nb(" La grille fine en rend %.1f", fin["luminance"])
        + nb(" — %+.1f, elle ne fait donc rien entrer.", reste),
        nb("La grille grossière, elle, en rend %.1f :", gros["luminance"])
        + nb(" %+.1f/255 de lumière", fuite)
        + " qui n'a aucun chemin physique pour arriver là.",
        "",
    ]
    for i, t in enumerate(texte):
        d.text((MARGE, y + i * 27), t, font=f_txt, fill=GRIS)

    yf = H - MARGE - 30
    d.line([MARGE, yf, L - MARGE, yf], fill=(46, 46, 56), width=1)
    d.text((MARGE, yf + 10),
           "EEVEE Next · %d échantillons · lancer de rayons et Fast GI coupés "
           "dans les deux images : la sonde est la seule source d'indirect · "
           "%d surfels · plafond et mur sud invisibles à la caméra, mais "
           "toujours opaques à la lumière"
           % (d0["echantillons"], d0["surfels"]),
           font=f_petit, fill=FAIBLE)

    out.save(SORTIE, "WEBP", quality=QUALITE, method=6)
    print()
    print("  %d × %d" % out.size)
    print("  plancher %.2f   grossiere %.2f (+%.2f)   fine %.2f (%+.2f)"
          % (plancher, gros["luminance"], fuite, fin["luminance"], reste))
    print("  %s  (%.0f Ko)"
          % (os.path.basename(SORTIE), os.path.getsize(SORTIE) / 1024))


if __name__ == "__main__":
    principal()
