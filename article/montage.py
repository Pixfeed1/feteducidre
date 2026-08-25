"""
Le montage comparatif : les deux rendus côte à côte.

    python3 article/montage.py

Produit `article/light-probes-blender-comparaison.webp`.

----------------------------------------------------------------------------
CE QUE DOIT FAIRE UNE COMPARAISON, ET CE QU'ELLE RATE PRESQUE TOUJOURS
----------------------------------------------------------------------------
Une comparaison avant/après ne se lit que si le lecteur est SÛR qu'une seule
chose a changé. C'est pour ça que les deux vignettes sont strictement de même
taille, alignées au pixel, et que rien — ni cadrage, ni exposition, ni
recadrage « pour que ça rentre » — ne diffère entre elles.

Les chiffres sous chaque image ne sont pas décoratifs non plus : ils sont
relevés sur les deux fichiers au moment du montage. Une légende qui annonce
un écart doit pouvoir le prouver, et surtout se corriger toute seule le jour
où on refait les rendus.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont
import numpy as np

RACINE = os.path.dirname(os.path.abspath(__file__))
#  ON PART DES RENDUS BRUTS, PAS DES WEBP FINIS.
#
#  Le WebP de l'image 1 porte le filaire du gizmo superposé. Le témoin, lui,
#  n'en a pas — et ne peut pas en avoir, puisqu'il n'a pas de sonde. Les
#  monter côte à côte ferait donc varier DEUX choses entre les vignettes :
#  l'éclairage, et la présence d'un trait teal. Le lecteur ne saurait plus
#  laquelle des deux il est censé regarder, et la démonstration se dilue.
#
#  Dans une comparaison, une seule variable change. Point.
AVEC = os.path.join(RACINE, "light-probes-blender-eevee-next.png")
SANS = os.path.join(RACINE, "light-probes-blender-eevee-next-sans-sonde.png")
SORTIE = os.path.join(RACINE, "light-probes-blender-comparaison.webp")

#  La zone de contrôle : la bibliothèque, dans le coin le plus éloigné de la
#  fenêtre. Les mêmes bornes que dans finaliser.py — c'est le point où l'on
#  a décidé, une fois pour toutes, que la démonstration se jouait.
CONTROLE = (0.82, 0.96, 0.20, 0.70)

VIGNETTE_L = 1240                  # largeur d'une vignette
GOUTTIERE = 28
MARGE = 34
BANDE_TITRE = 74
BANDE_PIED = 168

ENCRE = (13, 13, 17)
BLANC = (238, 238, 243)
GRIS = (138, 138, 150)
TEAL = (72, 224, 184)              # la couleur du gizmo, reprise pour l'« avec »
ROUGE = (214, 118, 96)             # pour le manque

POLICE_G = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
POLICE_R = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
QUALITE = 90


def police(chemin, taille):
    try:
        return ImageFont.truetype(chemin, taille)
    except OSError:
        return ImageFont.load_default()


def luminance_controle(im):
    a = np.asarray(im.convert("RGB"), dtype=float)
    h, w, _ = a.shape
    x0, x1, y0, y1 = CONTROLE
    return a[int(h * y0):int(h * y1), int(w * x0):int(w * x1)].mean()


def cadre_controle(d, x, y, lv, hv):
    """Le même rectangle sur les deux vignettes : c'est lui qui dit au
    lecteur OÙ regarder. Sans repère, une différence d'éclairage indirect
    passe complètement inaperçue."""
    x0, x1, y0, y1 = CONTROLE
    b = [x + x0 * lv, y + y0 * hv, x + x1 * lv, y + y1 * hv]
    d.rectangle(b, outline=(255, 255, 255, 150), width=2)


def principal():
    for f in (AVEC, SANS):
        if not os.path.exists(f):
            raise SystemExit(
                "rendu absent : %s\n"
                "        lancez `python3 article/light_probes_eevee_next.py`\n"
                "        puis le même avec `--sans-sonde`" % f)

    a_im = Image.open(AVEC).convert("RGB")
    b_im = Image.open(SANS).convert("RGB")
    if a_im.size != b_im.size:
        raise SystemExit("les deux rendus n'ont pas la même taille (%s et "
                         "%s) — une comparaison ne vaut rien si les deux "
                         "images ne sont pas strictement comparables"
                         % (a_im.size, b_im.size))

    la, lb = luminance_controle(a_im), luminance_controle(b_im)
    gain = la / max(lb, 0.01)
    perte = 100.0 * (1.0 - lb / max(la, 0.01))

    hv = int(round(VIGNETTE_L * a_im.height / a_im.width))
    a_v = a_im.resize((VIGNETTE_L, hv), Image.LANCZOS)
    b_v = b_im.resize((VIGNETTE_L, hv), Image.LANCZOS)

    L = MARGE * 2 + VIGNETTE_L * 2 + GOUTTIERE
    H = MARGE + BANDE_TITRE + hv + BANDE_PIED + MARGE
    out = Image.new("RGB", (L, H), ENCRE)
    d = ImageDraw.Draw(out, "RGBA")

    f_titre = police(POLICE_G, 34)
    f_chiffre = police(POLICE_G, 46)
    f_legende = police(POLICE_R, 25)
    f_petit = police(POLICE_R, 22)

    y_img = MARGE + BANDE_TITRE
    for i, (v, titre, teinte, chiffre, sous) in enumerate((
            (a_v, "AVEC LE VOLUME PROBE", TEAL, "%.1f" % la,
             "luminance du coin encadré, sur 255"),
            (b_v, "SANS VOLUME PROBE", ROUGE, "%.1f" % lb,
             "soit %.0f %% de moins, à réglage identique" % perte))):
        x = MARGE + i * (VIGNETTE_L + GOUTTIERE)

        #  Le titre, précédé d'une pastille de couleur
        d.rectangle([x, MARGE + 16, x + 10, MARGE + 46], fill=teinte)
        d.text((x + 24, MARGE + 12), titre, font=f_titre, fill=BLANC)

        out.paste(v, (x, y_img))
        cadre_controle(d, x, y_img, VIGNETTE_L, hv)

        #  Le chiffre relevé, sous la vignette
        yb = y_img + hv + 24
        d.text((x, yb), chiffre, font=f_chiffre, fill=teinte)
        lc = d.textlength(chiffre, font=f_chiffre)
        d.text((x + lc + 16, yb + 22), sous, font=f_petit, fill=GRIS)

    #  Un filet de séparation, puis la ligne de sens : sans lui les deux
    #  niveaux de lecture — le relevé de chaque vignette et la conclusion
    #  commune — se marchaient dessus.
    yf = y_img + hv + 96
    d.line([MARGE, yf, L - MARGE, yf], fill=(46, 46, 56), width=1)
    d.text((MARGE, yf + 22),
           "Même scène, même cadrage, même éclairage. Une seule variable "
           "change : la sonde d'irradiance.",
           font=f_legende, fill=GRIS)
    g = "×%.2f" % gain
    d.text((L - MARGE - d.textlength(g, font=f_chiffre), yf + 12), g,
           font=f_chiffre, fill=TEAL)

    out.save(SORTIE, "WEBP", quality=QUALITE, method=6)
    print()
    print("  %d × %d" % out.size)
    print("  coin de contrôle : avec %.1f   sans %.1f   ×%.2f  (−%.0f %%)"
          % (la, lb, gain, perte))
    print("  %s  (%.0f Ko)"
          % (os.path.basename(SORTIE), os.path.getsize(SORTIE) / 1024))


if __name__ == "__main__":
    principal()
