"""
Image à la une, version photographique.

    python3 article-agence-web/une_avec_photo.py

Produit `article-agence-web/onze-questions-choisir-agence-web.webp`
à partir de `fond-signature.png`.

----------------------------------------------------------------------------
CE QUE CETTE VERSION CHANGE, ET POURQUOI
----------------------------------------------------------------------------
La version précédente affichait les onze questions en toutes lettres. Elle
était exacte, conforme au brief — et elle ressemblait à une diapositive.

Deux raisons de changer, dont la seconde est la vraie :

  - une image à la une est d'abord vue à 300 px de large, dans une carte ou
    un fil. À cette taille, onze lignes de texte ne se lisent pas. Elles ne
    font qu'un gris uniforme ;
  - la liste, elle, a sa place DANS l'article, où le lecteur a le temps. Une
    image à la une n'a qu'un travail : donner envie d'ouvrir.

Il reste donc le nombre, le titre, et une photographie. Les onze questions ne
disparaissent pas du dépôt : `onze_questions.py` produit toujours la liste, qui
devient une figure d'article.

----------------------------------------------------------------------------
LE VOILE N'EST PAS UN FILTRE, C'EST CE QUI REND LE TEXTE LISIBLE
----------------------------------------------------------------------------
Un titre blanc posé sur une photo est illisible dès que la photo s'éclaircit
sous lui. On assombrit donc, mais pas uniformément : un dégradé qui pèse à
gauche, là où le texte se pose, et qui s'efface à droite pour laisser voir le
contrat et le stylo.

Le script MESURE ensuite la luminance sous chaque ligne de texte et refuse de
produire l'image si le contraste avec le blanc descend sous 4,5:1. C'est le
même contrôle que sur les figures : une image à la une illisible en vignette
est une image ratée, et ça ne se voit pas sur un grand écran.
"""

import os

from PIL import Image, ImageDraw, ImageFilter
import numpy as np

import charte as C

RACINE = os.path.dirname(os.path.abspath(__file__))
FOND = os.path.join(RACINE, "fond-signature.png")
SORTIE = os.path.join(RACINE, "onze-questions-choisir-agence-web.webp")

L, H = 1600, 900
MARGE = 76

TITRE = ("11 questions à poser", "à une agence web", "avant de signer")
ACCROCHE = "Celles dont la réponse engage — pas celles auxquelles tout le monde répond oui."


def voile(im):
    """
    Un dégradé sombre qui pèse à gauche et s'efface à droite.

    Construit dans un tableau plutôt qu'avec un rectangle semi-transparent :
    on veut une transition continue, et un aplat uniforme masquerait le sujet
    autant que le fond.
    """
    l, h = im.size
    x = np.linspace(0.0, 1.0, l)[None, :]
    #  Fort à gauche (0,82), presque nul à droite (0,10), avec une courbe qui
    #  descend vite : le texte occupe les 55 % de gauche.
    a = 0.82 - 0.72 * np.clip((x - 0.06) / 0.62, 0.0, 1.0) ** 1.4
    #  Un léger renfort en bas, où se pose l'accroche.
    y = np.linspace(0.0, 1.0, h)[:, None]
    a = np.clip(a + 0.12 * np.clip((y - 0.72) / 0.28, 0.0, 1.0), 0.0, 0.92)
    base = np.asarray(im, dtype=float)
    sombre = np.array([16.0, 15.0, 24.0])[None, None, :]
    return Image.fromarray(
        (base * (1.0 - a[..., None]) + sombre * a[..., None])
        .clip(0, 255).astype("uint8"))


def luminance_sous(im, boite):
    a = np.asarray(im.convert("RGB").crop(boite), dtype=float) / 255.0
    a = np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
    return float((0.2126 * a[..., 0] + 0.7152 * a[..., 1]
                  + 0.0722 * a[..., 2]).mean())


def principal():
    if not os.path.exists(FOND):
        raise SystemExit("fond absent : %s\n        lancez d'abord "
                         "`python3 article-agence-web/scene_signature.py`"
                         % FOND)
    photo = Image.open(FOND).convert("RGB")
    if photo.size != (L, H):
        photo = photo.resize((L, H), Image.LANCZOS)
    out = voile(photo)
    d = ImageDraw.Draw(out)

    f_marque = C.police(C.POLICE_G, 22)
    f_nombre = C.police(C.POLICE_G, 150)
    f_titre = C.police(C.POLICE_G, 58)
    f_accroche = C.police(C.POLICE_R, 25)

    blanc = (255, 255, 255)

    #  La marque.
    d.rectangle([MARGE, MARGE, MARGE + 8, MARGE + 24], fill=C.VIOLET)
    d.text((MARGE + 22, MARGE - 2), "PIXFEED", font=f_marque, fill=blanc)

    #  LE NOMBRE, en gros : c'est lui qui survit à la vignette.
    y = MARGE + 92
    d.text((MARGE - 8, y), "11", font=f_nombre, fill=C.VIOLET)
    lx = MARGE - 8 + d.textlength("11", font=f_nombre) + 34

    #  Le titre, calé à droite du nombre.
    lignes = ("questions à poser", "à une agence web", "avant de signer")
    for i, t in enumerate(lignes):
        d.text((lx, y + 14 + i * 62), t, font=f_titre, fill=blanc)

    #  L'accroche, en bas.
    ya = H - MARGE - 34
    d.text((MARGE, ya), ACCROCHE, font=f_accroche, fill=(214, 214, 224))

    #  LE CONTRÔLE. On mesure la luminance réelle sous chaque bloc de texte et
    #  on exige 4,5:1 contre le blanc. Sans ça, un fond qui s'éclaircit sous
    #  une ligne passerait inaperçu jusqu'à la publication.
    zones = {
        "nombre": (MARGE - 8, y, int(lx - 20), y + 150),
        "titre": (int(lx), y + 14, L - MARGE, y + 14 + 3 * 62),
        "accroche": (MARGE, ya, MARGE + int(
            d.textlength(ACCROCHE, font=f_accroche)), ya + 30),
    }
    faibles = []
    for nom, b in zones.items():
        lum = luminance_sous(out, b)
        r = 1.05 / (lum + 0.05)
        print("  %-9s luminance %.3f  contraste avec le blanc %.2f:1  %s"
              % (nom, lum, r, "ok" if r >= 4.5 else "INSUFFISANT"))
        if r < 4.5:
            faibles.append("%s (%.2f:1)" % (nom, r))
    if faibles:
        raise SystemExit(
            "le fond est trop clair sous : " + ", ".join(faibles)
            + "\n        renforcez le voile dans `voile()`")

    out.save(SORTIE, "WEBP", quality=C.QUALITE, method=6)
    print()
    print("  %d × %d" % out.size)
    print("  %s  (%.0f Ko)"
          % (os.path.basename(SORTIE), os.path.getsize(SORTIE) / 1024))


if __name__ == "__main__":
    principal()
