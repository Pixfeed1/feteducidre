"""
IMAGE 3 de l'article « PrestaShop headless » — SSR contre rendu client.

    python3 article-headless-prestashop/ssr_contre_client.py

Produit `article-headless-prestashop/rendu-serveur-ssr-contre-rendu-client-indexation.webp`.

----------------------------------------------------------------------------
UNE IMAGE, PAS UN PARAGRAPHE
----------------------------------------------------------------------------
Première version : deux colonnes de code source commentées, quatre puces de
chaque côté, deux lignes de nuance en bas. Tout était exact et personne
n'aurait eu envie de le lire. Une figure qui demande à être lue en entier pour
livrer son idée a déjà échoué — le texte de l'article est là pour ça.

Celle-ci tient dans deux pages posées côte à côte : à gauche ce que le robot
reçoit vraiment d'une page en rendu client, à droite ce qu'il reçoit d'une
page rendue par le serveur. La différence se voit de loin, sans un mot.

----------------------------------------------------------------------------
CE QUI REMPLACE « LA LOUPE QUI NE VOIT RIEN »
----------------------------------------------------------------------------
Le brief demandait une loupe Google aveugle devant une page blanche. C'est
faux : Googlebot exécute le JavaScript et indexe la plupart des pages en rendu
client. Une figure fausse dans un article technique coûte la confiance du
lecteur pour tout le reste.

Ce qui est vrai est plus intéressant, et se dessine : à gauche il faut un
SECOND passage pour que la page existe. Il est donc figuré par une flèche EN
POINTILLÉS, avec une horloge — le pointillé dit l'incertitude mieux qu'une
phrase. À droite, un seul trait plein.

Il ne reste qu'une ligne de texte en bas, celle qu'on ne peut pas dessiner :
les autres robots, eux, n'exécutent jamais ce second passage.
"""

import os

from PIL import Image, ImageDraw

import charte as C

RACINE = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(
    RACINE, "rendu-serveur-ssr-contre-rendu-client-indexation.webp")

L, H = 1600, 858
MARGE = 60
COL_L = 730
GOUTTIERE = 20

Y_TITRE = 116
Y_PAGE = 168
PAGE_H = 400
GRIS_BLOC = (226, 230, 238)


def chassis(d, x, y, w, h, barre=44):
    """
    Le châssis d'une fenêtre de navigateur, sans son contenu.

    Séparé du contenu parce qu'il sert à trois tailles différentes. La
    première version dessinait tout dans une seule fonction : à la taille de
    la vignette, le cadre intérieur devenait plus haut que la page et PIL
    refusait le rectangle.
    """
    d.rounded_rectangle([x, y, x + w, y + h], radius=14, fill=C.CARTE,
                        outline=C.BORD, width=2)
    d.rounded_rectangle([x, y, x + w, y + barre], radius=14,
                        fill=(240, 243, 248))
    d.rectangle([x, y + barre - 14, x + w, y + barre], fill=(240, 243, 248))
    r = 6 if barre < 30 else 12
    for i in range(3):
        d.ellipse([x + 12 + i * (r + 6), y + barre / 2 - r / 2,
                   x + 12 + i * (r + 6) + r, y + barre / 2 + r / 2],
                  fill=(206, 212, 222))
    d.rounded_rectangle([x + 12 + 3 * (r + 6) + 14, y + barre / 2 - r / 2 - 3,
                         x + w - 16, y + barre / 2 + r / 2 + 3],
                        radius=r, fill=(228, 232, 240))


def vignette_pleine(d, x, y, w, h):
    """La page telle qu'elle finira par exister, en petit."""
    chassis(d, x, y, w, h, barre=24)
    d.rounded_rectangle([x + 16, y + 36, x + 82, y + h - 16], radius=6,
                        fill=GRIS_BLOC)
    d.rounded_rectangle([x + 94, y + 38, x + w - 20, y + 50], radius=4,
                        fill=(150, 160, 178))
    d.rounded_rectangle([x + 94, y + 58, x + w - 70, y + 70], radius=4,
                        fill=(196, 202, 214))
    d.rounded_rectangle([x + 94, y + 78, x + w - 46, y + 88], radius=4,
                        fill=(214, 219, 228))


def page(d, x, y, w, h, teinte, pleine, f_prix=None):
    """
    Une page telle que le robot la reçoit.

    Vide, elle n'est pas « blanche » : elle contient l'ossature et rien
    d'autre. C'est ça qu'il faut montrer — un rectangle blanc se lirait comme
    une erreur de rendu, pas comme un fichier sans contenu.
    """
    chassis(d, x, y, w, h)

    if not pleine:
        #  Le conteneur vide, et le seul script. Rien de lisible.
        d.rounded_rectangle([x + 40, y + 92, x + w - 40, y + h - 60],
                            radius=10, outline=(214, 219, 228), width=2)
        t = "vide"
        f = C.police(C.POLICE_G, 30)
        d.text((x + w / 2 - d.textlength(t, font=f) / 2, y + h / 2 - 20), t,
               font=f, fill=(198, 204, 214))
        return

    #  Le contenu : une image, un titre, un prix, trois lignes, un bouton.
    d.rounded_rectangle([x + 40, y + 78, x + 300, y + h - 80], radius=10,
                        fill=GRIS_BLOC)
    d.rounded_rectangle([x + 330, y + 84, x + w - 60, y + 112], radius=5,
                        fill=(120, 130, 150))
    d.rounded_rectangle([x + 330, y + 124, x + w - 150, y + 148], radius=5,
                        fill=(160, 170, 188))
    d.text((x + 330, y + 172), "49,90 €", font=f_prix, fill=teinte)
    #  Les lignes de description s'arrêtent AVANT le bouton : posées à des
    #  ordonnées calculées séparément, la troisième passait dessus.
    for i in range(3):
        d.rounded_rectangle([x + 330, y + 216 + i * 22,
                             x + w - 60 - i * 46, y + 230 + i * 22],
                            radius=4, fill=(214, 219, 228))
    d.rounded_rectangle([x + 330, y + h - 100, x + 500, y + h - 56],
                        radius=10, fill=teinte)


def robot(d, cx, cy, teinte):
    """Un robot d'indexation. Une tête carrée, deux yeux, une antenne."""
    d.line([cx, cy - 30, cx, cy - 20], fill=teinte, width=3)
    d.ellipse([cx - 5, cy - 38, cx + 5, cy - 28], fill=teinte)
    d.rounded_rectangle([cx - 24, cy - 20, cx + 24, cy + 16], radius=8,
                        fill=C.CARTE, outline=teinte, width=3)
    for dx in (-9, 9):
        d.ellipse([cx + dx - 4, cy - 8, cx + dx + 4, cy], fill=teinte)


def horloge(d, cx, cy, r, teinte):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=C.CARTE, outline=teinte,
              width=3)
    d.line([cx, cy, cx, cy - r + 7], fill=teinte, width=3)
    d.line([cx, cy, cx + r - 9, cy], fill=teinte, width=3)


def coche(d, cx, cy, r, teinte):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=teinte)
    d.line([cx - 9, cy, cx - 2, cy + 8], fill=C.CARTE, width=4)
    d.line([cx - 2, cy + 8, cx + 10, cy - 8], fill=C.CARTE, width=4)


def fleche_pointillee(d, x0, x1, y, teinte, pas=16, plein=8):
    x = x0
    while x < x1 - 16:
        d.line([x, y, min(x + plein, x1 - 16), y], fill=teinte, width=3)
        x += pas
    d.polygon([(x1, y), (x1 - 15, y - 8), (x1 - 15, y + 8)], fill=teinte)


def principal():
    C.verifier()

    out = Image.new("RGB", (L, H), C.FOND)
    d = ImageDraw.Draw(out, "RGBA")

    f_titre = C.police(C.POLICE_G, 30)
    f_col = C.police(C.POLICE_G, 27)
    f_note = C.police(C.POLICE_R, 21)
    f_prix = C.police(C.POLICE_G, 30)
    f_bas = C.police(C.POLICE_R, 21)

    d.rectangle([MARGE, 44, MARGE + 10, 78], fill=C.VITRINE)
    d.text((MARGE + 24, 40), "CE QUE LE ROBOT REÇOIT",
           font=f_titre, fill=C.ENCRE)

    xg = MARGE
    xd = MARGE + COL_L + GOUTTIERE

    for x, titre, teinte in ((xg, "RENDU CLIENT", C.ALERTE),
                             (xd, "RENDU SERVEUR (SSR)", C.VITRINE)):
        d.rectangle([x, Y_TITRE, x + 8, Y_TITRE + 28], fill=teinte)
        d.text((x + 22, Y_TITRE - 4), titre, font=f_col, fill=C.ENCRE)

    page(d, xg, Y_PAGE, COL_L, PAGE_H, C.ALERTE, False)
    page(d, xd, Y_PAGE, COL_L, PAGE_H, C.VITRINE, True, f_prix)

    #  Le robot, posé sur chaque page : c'est lui qui la reçoit.
    for x, teinte in ((xg, C.ALERTE), (xd, C.VITRINE)):
        robot(d, x + COL_L - 62, Y_PAGE - 26, teinte)

    # ------------------------------------------------------  la suite, à gauche
    #  Un SECOND passage, en pointillés : le pointillé dit l'incertitude
    #  mieux qu'une phrase.
    y = Y_PAGE + PAGE_H + 56
    horloge(d, xg + 26, y + 34, 22, C.ALERTE)
    fleche_pointillee(d, xg + 62, xg + 214, y + 34, C.ALERTE)

    #  La page telle qu'elle finira par exister — en petit, plus tard.
    vignette_pleine(d, xg + 234, y - 20, 250, 110)
    d.text((xg + 234, y + 106), "plus tard, et pas toujours", font=f_note,
           fill=C.ALERTE)

    # -------------------------------------------------------  la suite, à droite
    coche(d, xd + 26, y + 34, 22, C.VITRINE)
    d.text((xd + 62, y + 20), "tout de suite, et pour tout le monde",
           font=f_note, fill=C.VITRINE)

    # ------------------------------------------------  la seule ligne de texte
    yf = H - 78
    d.line([MARGE, yf, L - MARGE, yf], fill=C.TRAIT, width=1)
    d.text((MARGE, yf + 20),
           "Googlebot finit par exécuter le JavaScript. Les robots des réseaux "
           "sociaux et des outils SEO, non.",
           font=f_bas, fill=C.GRIS)

    out.save(SORTIE, "WEBP", quality=C.QUALITE, method=6)
    print()
    print("  %d × %d" % out.size)
    print("  %s  (%.0f Ko)"
          % (os.path.basename(SORTIE), os.path.getsize(SORTIE) / 1024))


if __name__ == "__main__":
    principal()
