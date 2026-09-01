"""
Figure de la question 3 — « Qui détient les accès ? »

    python3 article-agence-web/cles_acces.py        (le rendu, une fois)
    python3 article-agence-web/qui_detient_les_acces.py

Produit `article-agence-web/qui-detient-les-acces-site-web.webp` et son
équivalent PNG, à partir de `fond-cles.png`.

----------------------------------------------------------------------------
TROISIÈME VERSION, ET LA BONNE RAISON DE JETER LA DEUXIÈME
----------------------------------------------------------------------------
La première était un gabarit à cartes arrondies. La deuxième, mieux composée,
était de la belle typographie — et c'était son défaut : quatre lignes de texte
mises en page restent quatre lignes de texte. Devant, on se demande pourquoi
c'est une image et pas un paragraphe de l'article. La question est juste.

Une image doit dire son sujet par l'image. Celui-ci se montre : quatre clés,
une seule qui ne se remplace pas. Le laiton est seul, devant, net ; les trois
aciers sont posés ensemble, plus loin, dans le flou. La hiérarchie est dans la
profondeur de champ, pas dans une couleur d'alerte ni dans un cadre.

----------------------------------------------------------------------------
LES LIBELLÉS SONT POSÉS SUR LES CLÉS, PAS À CÔTÉ
----------------------------------------------------------------------------
Leurs positions ne sont pas recopiées à la main : `cles_acces.py` projette
chaque clé dans la vue caméra et écrit ses coordonnées dans un fichier que ce
script relit. Bouger une clé dans la scène déplace son libellé tout seul.

Il reste très peu de mots — le titre, une phrase, et le nom de chaque clé.
Le détail de ce que recouvre chaque accès est dans l'article, à sa place.

----------------------------------------------------------------------------
LE VOILE EST MESURÉ
----------------------------------------------------------------------------
Un texte clair posé sur une photo devient illisible dès que la photo s'éclaircit
dessous. Le script mesure donc la luminance réelle sous chaque bloc et refuse de
produire l'image si le contraste tombe sous 4,5:1. C'est le même contrôle que
sur les autres figures : une image illisible en vignette ne se voit pas sur un
grand écran.
"""

import json
import os

from PIL import Image, ImageDraw
import numpy as np

import charte as C

RACINE = os.path.dirname(os.path.abspath(__file__))
FOND = os.path.join(RACINE, "fond-cles.png")
CADRAGE = os.path.join(RACINE, "fond-cles-cadrage.json")
BASE = os.path.join(RACINE, "qui-detient-les-acces-site-web")

L, H = 1600, 900
MARGE = 96

CREME = (243, 240, 232)
CREME_FAIBLE = (196, 192, 184)
OCRE = (226, 176, 96)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"

SURTITRE = "QUESTION 3"
TITRE = "Qui détient les accès ?"
ACCROCHE = "Quatre accès. Un seul ne se récupère pas."

DOMAINE = "le nom de domaine"
VERDICT = "NE SE RÉCUPÈRE PAS"
TROIS = ("l’hébergement", "l’administration du site", "les comptes Google")


def espace(d, xy, texte, f, teinte, tracking):
    """Des capitales dessinées lettre à lettre, avec de l'air entre elles."""
    x, y = xy
    for c in texte:
        d.text((x, y), c, font=f, fill=teinte)
        x += d.textlength(c, font=f) + tracking
    return x - tracking


def largeur_espacee(d, texte, f, tracking):
    return sum(d.textlength(c, font=f) for c in texte) \
        + tracking * max(len(texte) - 1, 0)


def voile(im):
    """
    Un assombrissement qui pèse en haut et sur les bords.

    Construit dans un tableau plutôt qu'avec un rectangle semi-transparent : on
    veut une transition continue. Un aplat uniforme éteindrait le laiton, qui
    est le sujet.
    """
    l, h = im.size
    y = np.linspace(0.0, 1.0, h)[:, None]
    x = np.linspace(0.0, 1.0, l)[None, :]
    #  Le bandeau du haut, là où se pose le titre.
    a = 0.62 * np.clip((0.42 - y) / 0.42, 0.0, 1.0) ** 0.9
    #  Une vignette douce, pour refermer les bords sans qu'on la remarque.
    r = np.sqrt(((x - 0.5) * 1.05) ** 2 + ((y - 0.55) * 1.25) ** 2)
    a = np.clip(a + 0.30 * np.clip((r - 0.44) / 0.46, 0.0, 1.0) ** 1.5,
                0.0, 0.86)
    base = np.asarray(im, dtype=float)
    sombre = np.array([12.0, 11.0, 14.0])[None, None, :]
    return Image.fromarray(
        (base * (1.0 - a[..., None]) + sombre * a[..., None])
        .clip(0, 255).astype("uint8"))


def luminance_sous(im, boite):
    x0, y0, x1, y1 = [int(v) for v in boite]
    x0, y0 = max(x0, 0), max(y0, 0)
    x1, y1 = min(x1, im.width), min(y1, im.height)
    if x1 <= x0 or y1 <= y0:
        raise SystemExit("zone de mesure vide : %s" % (boite,))
    a = np.asarray(im.convert("RGB").crop((x0, y0, x1, y1)),
                   dtype=float) / 255.0
    a = np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
    return float((0.2126 * a[..., 0] + 0.7152 * a[..., 1]
                  + 0.0722 * a[..., 2]).mean())


def principal():
    if not os.path.exists(FOND):
        raise SystemExit("fond absent : %s\n        lancez d'abord "
                         "`python3 article-agence-web/cles_acces.py`" % FOND)
    if not os.path.exists(CADRAGE):
        raise SystemExit("cadrage absent : %s\n        lancez "
                         "`python3 article-agence-web/cles_acces.py "
                         "--cadrage`" % CADRAGE)
    with open(CADRAGE, encoding="utf-8") as f:
        pos = json.load(f)

    photo = Image.open(FOND).convert("RGB")
    if photo.size != (L, H):
        photo = photo.resize((L, H), Image.LANCZOS)
    out = voile(photo)
    d = ImageDraw.Draw(out)

    f_sur = C.police(C.POLICE_G, 15)
    f_titre = C.police(SERIF, 62)
    f_acc = C.police(SERIF_I, 27)
    f_verd = C.police(C.POLICE_G, 15)
    f_nom = C.police(SERIF, 27)
    f_trois = C.police(SERIF_I, 22)

    #  Coordonnées de vue caméra vers pixels : l'origine de Blender est en bas
    #  à gauche, celle de PIL en haut à gauche.
    def px(nom):
        x, y = pos[nom]
        return x * L, (1.0 - y) * H

    zones = {}

    # ------------------------------------------------------------  le titre
    espace(d, (MARGE, MARGE - 4), SURTITRE, f_sur, OCRE, 2.6)
    d.text((MARGE - 3, MARGE + 26), TITRE, font=f_titre, fill=CREME)
    d.text((MARGE, MARGE + 116), ACCROCHE, font=f_acc, fill=CREME_FAIBLE)
    zones["titre"] = (MARGE, MARGE + 30,
                      MARGE + d.textlength(TITRE, font=f_titre),
                      MARGE + 100)
    zones["accroche"] = (MARGE, MARGE + 118,
                         MARGE + d.textlength(ACCROCHE, font=f_acc),
                         MARGE + 152)

    # ---------------------------------------------------  la clé de laiton
    xd, yd = px("Domaine")
    #  Le libellé descend sous la clé, décalé à gauche : c'est le seul endroit
    #  du cadre où le bois est vide sur toute la largeur du texte.
    lx, ly = MARGE, min(yd + 132, H - MARGE - 74)
    d.line([lx, ly - 22, lx + 46, ly - 22], fill=OCRE, width=1)
    espace(d, (lx, ly - 14), VERDICT, f_verd, OCRE, 2.4)
    d.text((lx, ly + 14), DOMAINE, font=f_nom, fill=CREME)
    zones["domaine"] = (lx, ly - 14,
                        lx + max(largeur_espacee(d, VERDICT, f_verd, 2.4),
                                 d.textlength(DOMAINE, font=f_nom)), ly + 50)

    # -------------------------------------------------  les trois d'acier
    xs = max(px(n)[0] for n in ("Acier1", "Acier2", "Acier3"))
    ys = sum(px(n)[1] for n in ("Acier1", "Acier2", "Acier3")) / 3.0
    tx = min(xs + 96, L - MARGE - 260)
    ty = max(ys - 52, MARGE + 190)
    large = max(d.textlength(t, font=f_trois) for t in TROIS)
    if tx + large > L - MARGE:
        tx = L - MARGE - large
    for i, t in enumerate(TROIS):
        d.text((tx, ty + i * 34), t, font=f_trois, fill=CREME_FAIBLE)
    zones["trois"] = (tx, ty, tx + large, ty + 3 * 34)

    # ------------------------------------------------------------  contrôle
    faibles = []
    for nom, b in zones.items():
        lum = luminance_sous(out, b)
        clair = CREME if nom in ("titre", "domaine") else CREME_FAIBLE
        r = (max(_lum(clair), lum) + 0.05) / (min(_lum(clair), lum) + 0.05)
        print("  %-9s fond %.3f  contraste %.2f:1  %s"
              % (nom, lum, r, "ok" if r >= 4.5 else "INSUFFISANT"))
        if r < 4.5:
            faibles.append("%s (%.2f:1)" % (nom, r))
    if faibles:
        raise SystemExit("le fond est trop clair sous : " + ", ".join(faibles)
                         + "\n        renforcez le voile dans `voile()`")

    out.save(BASE + ".webp", "WEBP", quality=C.QUALITE, method=6)
    out.save(BASE + ".png", "PNG", optimize=True)
    print()
    print("  %d × %d" % out.size)
    for e in (".webp", ".png"):
        print("  %-44s %.0f Ko" % (os.path.basename(BASE + e),
                                   os.path.getsize(BASE + e) / 1024))


def _lum(couleur):
    v = []
    for x in couleur[:3]:
        x /= 255.0
        v.append(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4)
    return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]


if __name__ == "__main__":
    principal()
