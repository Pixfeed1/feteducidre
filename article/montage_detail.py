"""
La seconde comparaison : autre point de vue, avec loupe sur le coin sombre.

    python3 article/montage_detail.py

Produit `article/eclairage-indirect-blender-avec-sans-probe-2.webp`.

----------------------------------------------------------------------------
POURQUOI UNE SECONDE FIGURE, ET POURQUOI PAS LA MÊME
----------------------------------------------------------------------------
La première comparaison ouvre l'article. En redonner une identique plus loin
n'apprend rien, et laisse penser qu'on n'avait qu'une image à montrer.

Celle-ci change deux choses :

  - LE POINT DE VUE. On regarde depuis la fenêtre vers le coin le plus
    éloigné : la source est derrière la caméra, il ne reste dans le champ
    aucune zone directement éclairée pour servir de repère rassurant. Si
    l'effet tenait au cadrage de la première image, il s'effondrerait ici.

  - LA LOUPE. Les chiffres de la première figure — 6,4 contre 25,2 sur 255 —
    portent sur une zone qu'on distingue à peine à l'échelle de la page. On
    la montre donc agrandie, sous chaque vignette, à côté du chiffre qui la
    décrit. Un nombre qu'on ne peut pas rapprocher de ce qu'il mesure ne
    convainc personne.

Et un format 4/3 au lieu du 16/9 de la première : deux figures qui se
ressemblent au premier coup d'œil se lisent comme un doublon.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont
import numpy as np

RACINE = os.path.dirname(os.path.abspath(__file__))
AVEC = os.path.join(RACINE, "light-probes-blender-eevee-next-vue2.png")
SANS = os.path.join(RACINE,
                    "light-probes-blender-eevee-next-vue2-sans-sonde.png")
SORTIE = os.path.join(RACINE,
                      "eclairage-indirect-blender-avec-sans-probe-2.webp")

#  La zone de contrôle, en fractions du cadre : le meuble sombre du fond,
#  celui qu'aucun rayon direct n'atteint. Mesurée sur le rendu, pas devinée.
#  Bornes choisies pour que la zone soit PRESQUE CARRÉE. Cadrée serrée sur
#  le seul meuble, elle donnait un rectangle deux fois plus haut que large :
#  une loupe de cette forme oblige soit à la réduire jusqu'à l'inutile, soit
#  à doubler la hauteur de la figure. En élargissant à l'angle et au mur, on
#  gagne en plus deux surfaces qui s'effondrent elles aussi sans la sonde.
CONTROLE = (0.52, 0.82, 0.28, 0.70)

ORDRE = ("sans", "avec")
#  UNE LOUPE DOIT AGRANDIR, SINON CE N'EST PAS UNE LOUPE.
#
#  Premier essai : vignettes à 1 080 px, loupe à 280. La zone de contrôle
#  occupe 323 px dans la vignette — la « loupe » était donc PLUS PETITE que
#  ce qu'elle prétendait grossir, et l'image annonçait fièrement « agrandi
#  0,8 fois ». Un facteur d'agrandissement inférieur à 1 est un aveu.
#
#  Vignettes réduites à 900, loupe portée à 430 : la zone passe de 269 px
#  dans la vue à 430 px dans la loupe, soit 1,6 fois. Le facteur est calculé
#  et écrit sur l'image, il ne peut donc plus mentir.
VIGNETTE_L = 900
LOUPE_L = 430
GOUTTIERE = 30
MARGE = 34
BANDE_TITRE = 74
BANDE_PIED = 0     # calculée : elle dépend de la hauteur de la loupe

ENCRE = (13, 13, 17)
BLANC = (238, 238, 243)
GRIS = (138, 138, 150)
TEAL = (72, 224, 184)
ROUGE = (214, 118, 96)

POLICE_G = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
POLICE_R = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
QUALITE = 90

REGLAGES = ("EEVEE Next · 128 échantillons · lancer de rayons en espace "
            "écran désactivé dans les deux images · monde à 0,03")


def nb(gabarit, valeur):
    """Un nombre écrit en français. La ligne de réglages dit « monde à 0,03 » ;
    une figure qui annonce « 4.74 » deux centimètres plus bas se lit comme
    deux images collées l'une à l'autre."""
    return (gabarit % valeur).replace(".", ",")


def police(chemin, taille):
    try:
        return ImageFont.truetype(chemin, taille)
    except OSError:
        return ImageFont.load_default()


def zone(im):
    x0, x1, y0, y1 = CONTROLE
    w, h = im.size
    return (int(w * x0), int(h * y0), int(w * x1), int(h * y1))


def luminance(im):
    a = np.asarray(im.convert("RGB").crop(zone(im)), dtype=float)
    return a.mean()


def principal():
    for f in (AVEC, SANS):
        if not os.path.exists(f):
            raise SystemExit(
                "rendu absent : %s\n"
                "        lancez `python3 article/light_probes_eevee_next.py "
                "--vue2`\n        puis le même avec `--sans-sonde`" % f)

    ims = {"avec": Image.open(AVEC).convert("RGB"),
           "sans": Image.open(SANS).convert("RGB")}
    if ims["avec"].size != ims["sans"].size:
        raise SystemExit("les deux rendus n'ont pas la même taille : une "
                         "comparaison ne vaut rien si les deux images ne "
                         "sont pas strictement comparables")

    lum = {k: luminance(v) for k, v in ims.items()}
    gain = lum["avec"] / max(lum["sans"], 0.01)
    perte = 100.0 * (1.0 - lum["sans"] / max(lum["avec"], 0.01))

    hv = int(round(VIGNETTE_L * ims["avec"].height / ims["avec"].width))
    #  La hauteur de la loupe se déduit de la zone de contrôle : la figure
    #  s'ajuste donc toute seule si on rebornes la zone.
    zx0, zy0, zx1, zy1 = zone(ims["avec"])
    lh = int(round(LOUPE_L * (zy1 - zy0) / float(zx1 - zx0)))
    pied = 26 + lh + 34 + 76
    L = MARGE * 2 + VIGNETTE_L * 2 + GOUTTIERE
    H = MARGE + BANDE_TITRE + hv + pied + MARGE
    out = Image.new("RGB", (L, H), ENCRE)
    d = ImageDraw.Draw(out, "RGBA")

    f_titre = police(POLICE_G, 34)
    f_chiffre = police(POLICE_G, 46)
    f_legende = police(POLICE_R, 25)
    f_petit = police(POLICE_R, 22)
    f_reglages = police(POLICE_R, 20)

    y_img = MARGE + BANDE_TITRE
    for i, cle in enumerate(ORDRE):
        im = ims[cle]
        teinte = TEAL if cle == "avec" else ROUGE
        titre = ("AVEC LE VOLUME PROBE" if cle == "avec"
                 else "SANS VOLUME PROBE")
        x = MARGE + i * (VIGNETTE_L + GOUTTIERE)

        d.rectangle([x, MARGE + 16, x + 10, MARGE + 46], fill=teinte)
        d.text((x + 24, MARGE + 12), titre, font=f_titre, fill=BLANC)

        out.paste(im.resize((VIGNETTE_L, hv), Image.LANCZOS), (x, y_img))

        #  Le repère sur la vignette : même rectangle des deux côtés, c'est
        #  lui qui dit au lecteur OÙ regarder.
        zx0, zy0, zx1, zy1 = zone(im)
        k = VIGNETTE_L / float(im.width)
        b = [x + zx0 * k, y_img + zy0 * k, x + zx1 * k, y_img + zy1 * k]
        d.rectangle(b, outline=(255, 255, 255, 170), width=2)

        #  LA LOUPE, sous la vignette, à pleine résolution du rendu.
        loupe = im.crop(zone(im)).resize((LOUPE_L, lh), Image.LANCZOS)
        lx, ly = x, y_img + hv + 26
        out.paste(loupe, (lx, ly))
        d.rectangle([lx - 1, ly - 1, lx + LOUPE_L, ly + lh],
                    outline=(255, 255, 255, 120), width=2)

        #  Le chiffre, posé À CÔTÉ de la loupe : le nombre et ce qu'il
        #  mesure dans le même regard.
        tx = lx + LOUPE_L + 30
        d.text((tx, ly + 6), nb("%.1f", lum[cle]), font=f_chiffre, fill=teinte)
        d.text((tx, ly + 64), "luminance du cadre blanc, sur 255"
               if cle == "avec" else "soit %.0f %% de moins" % perte,
               font=f_petit, fill=GRIS)
        #  Le facteur se compte par rapport à la VIGNETTE, pas au fichier
        #  source : c'est la vignette que le lecteur a sous les yeux.
        facteur = LOUPE_L / ((zx1 - zx0) * VIGNETTE_L / float(im.width))
        d.text((tx, ly + 96),
               nb("agrandi %.1f fois", facteur) if cle == "avec"
               else "à réglage identique",
               font=f_petit, fill=(96, 96, 108))

    yf = y_img + hv + 26 + lh + 34
    d.line([MARGE, yf, L - MARGE, yf], fill=(46, 46, 56), width=1)
    d.text((MARGE, yf + 18),
           "Autre point de vue de la même pièce : la fenêtre est derrière "
           "la caméra, plus aucune zone éclairée en direct dans le champ.",
           font=f_legende, fill=GRIS)
    d.text((MARGE, yf + 52), REGLAGES, font=f_reglages, fill=(96, 96, 108))
    g = nb("×%.2f", gain)
    d.text((L - MARGE - d.textlength(g, font=f_chiffre), yf + 12), g,
           font=f_chiffre, fill=TEAL)

    out.save(SORTIE, "WEBP", quality=QUALITE, method=6)
    print()
    print("  %d × %d" % out.size)
    print("  coin de contrôle : avec %.1f   sans %.1f   ×%.2f  (−%.0f %%)"
          % (lum["avec"], lum["sans"], gain, perte))
    print("  %s  (%.0f Ko)"
          % (os.path.basename(SORTIE), os.path.getsize(SORTIE) / 1024))


if __name__ == "__main__":
    principal()
