"""
IMAGE 5 de l'article — le montage final sur la sonde Plane.

    python3 article/montage_plane.py

Produit `article/light-probe-plane-sol-reflechissant.webp` à partir des trois
rendus de `plane_probe_reflexions.py`.

----------------------------------------------------------------------------
POURQUOI IL FAUT UNE TROISIÈME VIGNETTE
----------------------------------------------------------------------------
Les deux grandes images comparent un reflet présent à un reflet absent. Mais
l'objet dont on parle n'est visible NULLE PART : c'est tout le sujet, il est
hors cadre. Le lecteur doit donc croire sur parole qu'il existe, qu'il est
ambre, et qu'il est bien placé là où le reflet le prétend.

D'où l'encart : le même plan, à la même place, au même instant — seule la
focale change, 24 mm devient 12 mm. Le panneau y est, et son reflet aussi. La
figure se vérifie donc toute seule, sans qu'on ait à faire confiance au texte.

----------------------------------------------------------------------------
LE CHIFFRE
----------------------------------------------------------------------------
La zone mesurée n'est pas choisie à l'œil : c'est le rectangle où
`verifier_cadrage()` a projeté les quatre coins de l'image miroir du panneau.
Le cadre blanc dessiné sur les vignettes est exactement ce rectangle-là. On
mesure donc ce qu'on montre, et on montre ce qu'on mesure.
"""

import os

from PIL import Image, ImageDraw, ImageFont
import numpy as np

RACINE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(RACINE, "light-probe-plane-sol-reflechissant")
AVEC = BASE + ".png"
SANS = BASE + "-sans-plane.png"
LARGE = BASE + "-large.png"
SORTIE = BASE + ".webp"

#  La zone du reflet du panneau, en fractions d'image (x0, x1, y0, y1).
#  Sortie telle quelle de la projection des coins, dans le rendu :
#      ZONE_REFLET = (0.3612, 0.6388, 0.7193, 0.8411)
ZONE = (0.3612, 0.6388, 0.7193, 0.8411)

ORDRE = ("sans", "avec")
VIGNETTE_L = 820
ENCART_L = 400
GOUTTIERE = 30
MARGE = 34
BANDE_TITRE = 74

ENCRE = (13, 13, 17)
BLANC = (238, 238, 243)
GRIS = (138, 138, 150)
TEAL = (72, 224, 184)
ROUGE = (214, 118, 96)

POLICE_G = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
POLICE_R = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
QUALITE = 90

REGLAGES = ("EEVEE Next · 160 échantillons · lancer de rayons en espace écran "
            "ACTIVÉ dans les deux images · sol métal, rugosité 0,07")


def nb(gabarit, valeur):
    return (gabarit % valeur).replace(".", ",")


def police(chemin, taille):
    try:
        return ImageFont.truetype(chemin, taille)
    except OSError:
        return ImageFont.load_default()


def boite(im):
    x0, x1, y0, y1 = ZONE
    w, h = im.size
    return (int(w * x0), int(h * y0), int(w * x1), int(h * y1))


def principal():
    for f in (AVEC, SANS, LARGE):
        if not os.path.exists(f):
            raise SystemExit(
                "rendu absent : %s\n        lancez "
                "`python3 article/plane_probe_reflexions.py` avec, sans "
                "(`--sans-plane`) et large (`--large`)" % f)

    ims = {"avec": Image.open(AVEC).convert("RGB"),
           "sans": Image.open(SANS).convert("RGB")}
    large = Image.open(LARGE).convert("RGB")
    if ims["avec"].size != ims["sans"].size:
        raise SystemExit("les deux rendus n'ont pas la même taille")

    lum = {k: np.asarray(v.crop(boite(v)), dtype=float).mean()
           for k, v in ims.items()}

    #  CONTRÔLE D'HONNÊTETÉ. Les blocs témoins doivent être identiques d'une
    #  image à l'autre : s'ils bougent, c'est qu'autre chose que la sonde a
    #  changé, et la comparaison ne vaut plus rien.
    w0, h0 = ims["avec"].size
    bande = (int(w0 * 0.06), int(h0 * 0.06), int(w0 * 0.94), int(h0 * 0.30))
    ecart = float(np.abs(np.asarray(ims["avec"].crop(bande), dtype=float)
                         - np.asarray(ims["sans"].crop(bande),
                                      dtype=float)).mean())
    if ecart > 1.5:
        raise SystemExit("les blocs témoins diffèrent de %.2f/255 : "
                         "les deux rendus ne sont pas comparables" % ecart)

    hv = int(round(VIGNETTE_L * h0 / w0))
    he = int(round(ENCART_L * large.height / large.width))
    L = MARGE * 2 + VIGNETTE_L * 2 + GOUTTIERE
    #  Le pied se compte, il ne s'estime pas. En additionnant de tête j'avais
    #  écrit 116 + he : soixante-dix pixels de moins que nécessaire, et la
    #  ligne de réglages tombait sous le bord de l'image — invisible, mais
    #  toujours écrite dans le code, donc toujours crue présente.
    #      chiffres      86   (44 pt de nombre + deux lignes de 21)
    #      + encart      30 + he
    #      + filet       30
    #      + réglages    46
    pied = 86 + 30 + he + 30 + 46
    H = MARGE + BANDE_TITRE + hv + pied + MARGE
    out = Image.new("RGB", (L, H), ENCRE)
    d = ImageDraw.Draw(out, "RGBA")

    f_titre = police(POLICE_G, 32)
    f_chiffre = police(POLICE_G, 44)
    f_legende = police(POLICE_R, 24)
    f_petit = police(POLICE_R, 21)
    f_reglages = police(POLICE_R, 19)

    y_img = MARGE + BANDE_TITRE
    for i, cle in enumerate(ORDRE):
        im = ims[cle]
        teinte = TEAL if cle == "avec" else ROUGE
        titre = ("AVEC LA SONDE PLANE" if cle == "avec"
                 else "SANS — ESPACE ÉCRAN SEUL")
        x = MARGE + i * (VIGNETTE_L + GOUTTIERE)

        d.rectangle([x, MARGE + 14, x + 10, MARGE + 44], fill=teinte)
        d.text((x + 24, MARGE + 10), titre, font=f_titre, fill=BLANC)

        out.paste(im.resize((VIGNETTE_L, hv), Image.LANCZOS), (x, y_img))

        k = VIGNETTE_L / float(im.width)
        bx0, by0, bx1, by1 = boite(im)
        b = [x + bx0 * k, y_img + by0 * k, x + bx1 * k, y_img + by1 * k]
        d.rectangle(b, outline=(255, 255, 255, 165), width=2)

        #  Le rappel que le sujet est hors cadre : une flèche qui sort par le
        #  haut. Sans elle, on regarde deux sols et on cherche l'objet.
        cx = x + VIGNETTE_L // 2
        d.line([cx, y_img + 16, cx, y_img + 54], fill=(255, 255, 255, 130),
               width=2)
        d.polygon([(cx, y_img + 8), (cx - 8, y_img + 24), (cx + 8, y_img + 24)],
                  fill=(255, 255, 255, 165))
        t = "le panneau est là-haut, hors du cadre"
        d.text((cx - d.textlength(t, font=f_petit) / 2, y_img + 60), t,
               font=f_petit, fill=(214, 214, 224))

        #  Le chiffre, sous la vignette et du côté de sa vignette.
        d.text((x, y_img + hv + 24), nb("%.1f", lum[cle]),
               font=f_chiffre, fill=teinte)
        d.text((x + 128, y_img + hv + 30),
               "luminance du cadre blanc, sur 255",
               font=f_petit, fill=GRIS)
        d.text((x + 128, y_img + hv + 58),
               "le reflet du panneau y est" if cle == "avec"
               else "il n'y a rien à réfléchir : le panneau n'est pas à l'écran",
               font=f_petit, fill=(104, 104, 116))

    #  L'ENCART DE CONTRÔLE, en bas à gauche.
    ex, ey = MARGE, y_img + hv + 30 + 86
    out.paste(large.resize((ENCART_L, he), Image.LANCZOS), (ex, ey))
    d.rectangle([ex - 1, ey - 1, ex + ENCART_L, ey + he],
                outline=(255, 255, 255, 110), width=2)
    tx = ex + ENCART_L + 26
    d.text((tx, ey + 4), "LA PREUVE QUE LE PANNEAU EXISTE",
           font=police(POLICE_G, 24), fill=BLANC)
    for j, ligne in enumerate([
            "Le même plan, la même position de caméra, le même instant :",
            "seule la focale change, 24 mm devient 12 mm. Le panneau ambre",
            "entre alors dans le cadre, en haut — et son reflet avec lui.",
            "",
            "C'est exactement ce que la sonde Plane va chercher : elle rend",
            "la scène une seconde fois depuis le point de vue miroir, où",
            "« hors champ » ne veut plus rien dire."]):
        d.text((tx, ey + 44 + j * 30), ligne, font=f_legende, fill=GRIS)

    yf = ey + he + 30
    d.line([MARGE, yf, L - MARGE, yf], fill=(46, 46, 56), width=1)
    d.text((MARGE, yf + 16), REGLAGES, font=f_reglages, fill=(104, 104, 116))
    ec = nb("blocs témoins identiques à %.2f/255 près", ecart)
    d.text((L - MARGE - d.textlength(ec, font=f_reglages), yf + 16), ec,
           font=f_reglages, fill=(104, 104, 116))

    out.save(SORTIE, "WEBP", quality=QUALITE, method=6)
    print()
    print("  %d × %d" % out.size)
    print("  reflet du panneau : avec %.1f   sans %.1f   (sur 255)"
          % (lum["avec"], lum["sans"]))
    print("  blocs témoins : écart %.2f/255 entre les deux rendus" % ecart)
    print("  %s  (%.0f Ko)"
          % (os.path.basename(SORTIE), os.path.getsize(SORTIE) / 1024))


if __name__ == "__main__":
    principal()
