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
CONTROLE = (0.44, 0.72, 0.30, 0.78)

ORDRE = ("sans", "avec")
VIGNETTE_L = 1080
LOUPE_L = 300
GOUTTIERE = 30
MARGE = 34
BANDE_TITRE = 74
BANDE_PIED = 232

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
    L = MARGE * 2 + VIGNETTE_L * 2 + GOUTTIERE
    H = MARGE + BANDE_TITRE + hv + BANDE_PIED + MARGE
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
        loupe = im.crop(zone(im))
        lh = int(round(LOUPE_L * loupe.height / loupe.width))
        loupe = loupe.resize((LOUPE_L, lh), Image.LANCZOS)
        lx, ly = x, y_img + hv + 26
        out.paste(loupe, (lx, ly))
        d.rectangle([lx - 1, ly - 1, lx + LOUPE_L, ly + lh],
                    outline=(255, 255, 255, 120), width=2)

        #  Le chiffre, posé À CÔTÉ de la loupe : le nombre et ce qu'il
        #  mesure dans le même regard.
        tx = lx + LOUPE_L + 26
        d.text((tx, ly + 4), "%.1f" % lum[cle], font=f_chiffre, fill=teinte)
        d.text((tx, ly + 60),
               "luminance du cadre blanc" if cle == "avec"
               else "soit %.0f %% de moins" % perte,
               font=f_petit, fill=GRIS)
        d.text((tx, ly + 88), "sur 255", font=f_petit, fill=GRIS)

    yf = y_img + hv + 190
    d.line([MARGE, yf, L - MARGE, yf], fill=(46, 46, 56), width=1)
    d.text((MARGE, yf + 18),
           "Autre point de vue de la même pièce : la fenêtre est derrière "
           "la caméra, plus aucune zone éclairée en direct dans le champ.",
           font=f_legende, fill=GRIS)
    d.text((MARGE, yf + 52), REGLAGES, font=f_reglages, fill=(96, 96, 108))
    g = "×%.2f" % gain
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
