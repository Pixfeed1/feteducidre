"""
IMAGE 1 de l'article « PrestaShop headless avec Next.js » — le hero.

    python3 article-headless-prestashop/hero_headless.py

Produit `article-headless-prestashop/architecture-headless-prestashop-nextjs.webp`.

----------------------------------------------------------------------------
POURQUOI LE MONTAGE CÔTE À CÔTE PLUTÔT QUE LES DEUX LOGOS
----------------------------------------------------------------------------
Le brief proposait une variante : deux logos reliés par une flèche « API ».
C'est plus rapide à faire et ça ne dit rien — deux logos reliés par une flèche
décrivent aussi bien une intégration, un partenariat ou un rachat. Le lecteur
qui arrive sur l'article ne sait toujours pas ce que « headless » change pour
lui.

Le montage, lui, montre la seule chose qui compte : ce sont DEUX INTERFACES
DISTINCTES. À gauche l'outil de gestion, gris de fer, avec ses tableaux et ses
compteurs. À droite la boutique, qui n'a plus rien à voir avec lui. C'est
exactement ce que veut dire « découplé », et ça se voit sans légende.

On évite en plus de redessiner des logos de mémoire — un logo approximatif
dans un article technique se remarque tout de suite, et rien ne garantit qu'on
ait le droit de le retoucher.

----------------------------------------------------------------------------
LA FLÈCHE VA DANS LES DEUX SENS, ET CE N'EST PAS UN DÉTAIL
----------------------------------------------------------------------------
On représente presque toujours le headless par une flèche unique, du back
vers le front. Elle est fausse à moitié : le catalogue descend vers la
vitrine, mais les commandes remontent. Un lecteur qui ne voit qu'une flèche se
demande à juste titre où atterrit un panier.

D'où deux traits, deux sens, et ce qui circule écrit sur chacun.

----------------------------------------------------------------------------
CE QU'ON NE MET PAS SUR L'IMAGE
----------------------------------------------------------------------------
Aucun chiffre de performance. « Rapide » se démontre avec des mesures, pas
avec un éclair posé sur une maquette, et je n'en ai pas ici. La colonne de
droite dit donc « pages pré-rendues », qui est une propriété du procédé et non
une promesse de résultat.
"""

import os

from PIL import Image, ImageDraw

import charte as C

RACINE = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(
    RACINE, "architecture-headless-prestashop-nextjs.webp")

L, H = 1600, 900
MARGE = 60
PANNEAU_L = 640
PANNEAU_H = 560
Y0 = 96
PONT = 200                       # l'espace entre les deux panneaux


def carte(d, x, y, w, h, radius=16, fill=None, outline=None, width=2):
    d.rounded_rectangle([x, y, x + w, y + h], radius=radius,
                        fill=fill if fill is not None else C.CARTE,
                        outline=outline if outline is not None else C.BORD,
                        width=width)


def bloc(d, x, y, w, h, couleur=None, radius=6):
    d.rounded_rectangle([x, y, x + w, y + h], radius=radius,
                        fill=couleur if couleur is not None else C.BLOC)


def back_office(d, x, y, f_petit, f_min):
    """
    Le back-office : barre latérale sombre, compteurs, tableau.

    Une maquette, pas une capture. Elle est assez générique pour qu'on la
    reconnaisse comme « un outil de gestion » et assez peu détaillée pour
    qu'on ne la prenne pas pour une photographie de PrestaShop.
    """
    carte(d, x, y, PANNEAU_L, PANNEAU_H)

    #  La barre latérale, dans l'arrondi de la carte.
    d.rounded_rectangle([x, y, x + 132, y + PANNEAU_H], radius=16,
                        fill=C.ADMIN)
    d.rectangle([x + 100, y, x + 132, y + PANNEAU_H], fill=C.ADMIN)
    bloc(d, x + 22, y + 24, 66, 14, (150, 162, 186))
    for i in range(6):
        actif = i == 1
        bloc(d, x + 22, y + 70 + i * 38, 88, 12,
             (232, 236, 244) if actif else (96, 110, 136))

    #  L'en-tête : un titre et une barre de recherche.
    d.text((x + 160, y + 26), "Catalogue", font=f_petit, fill=C.ENCRE)
    bloc(d, x + PANNEAU_L - 220, y + 24, 190, 24, (238, 241, 246), 12)
    d.line([x + 160, y + 62, x + PANNEAU_L - 30, y + 62], fill=C.TRAIT,
           width=1)

    #  Trois compteurs.
    for i in range(3):
        cx = x + 160 + i * 152
        carte(d, cx, y + 82, 132, 74, 10, (250, 251, 253), C.BORD, 1)
        bloc(d, cx + 14, y + 96, 48, 9, (196, 202, 214))
        bloc(d, cx + 14, y + 116, 76, 18, (150, 160, 180))

    #  Un tableau : la matière même du back-office.
    d.line([x + 160, y + 186, x + PANNEAU_L - 30, y + 186], fill=C.TRAIT,
           width=1)
    for i in range(7):
        yy = y + 202 + i * 44
        bloc(d, x + 160, yy, 26, 26, (226, 231, 239), 5)
        bloc(d, x + 198, yy + 6, 150 - (i % 3) * 26, 13,
             (176, 184, 200) if i else (120, 132, 154))
        bloc(d, x + 396, yy + 6, 62, 13, (206, 212, 224))
        bloc(d, x + 486, yy + 6, 44, 13, (206, 212, 224))
        if i < 6:
            d.line([x + 160, yy + 36, x + PANNEAU_L - 30, yy + 36],
                   fill=(238, 241, 246), width=1)


def vitrine(d, x, y, f_petit, f_min, f_prix):
    """
    La boutique : peu d'éléments, beaucoup d'air, un seul bouton coloré.

    C'est le contraire du panneau de gauche, et c'est voulu — la différence
    d'occupation entre les deux cartes fait la moitié du propos.
    """
    carte(d, x, y, PANNEAU_L, PANNEAU_H)

    #  Barre de navigation.
    bloc(d, x + 34, y + 28, 78, 16, (60, 66, 84), 4)
    for i in range(3):
        bloc(d, x + 300 + i * 78, y + 32, 56, 10, (196, 202, 214))
    d.ellipse([x + PANNEAU_L - 66, y + 26, x + PANNEAU_L - 44, y + 48],
              outline=(176, 184, 200), width=2)
    d.line([x + 34, y + 72, x + PANNEAU_L - 34, y + 72], fill=C.TRAIT,
           width=1)

    #  Le bloc produit : image à gauche, texte et bouton à droite.
    bloc(d, x + 34, y + 100, 250, 210, (236, 239, 245), 12)
    bloc(d, x + 310, y + 108, 210, 16, (176, 184, 200))
    bloc(d, x + 310, y + 136, 260, 16, (176, 184, 200))
    d.text((x + 310, y + 176), "49,90 €", font=f_prix, fill=C.ENCRE)
    d.rounded_rectangle([x + 310, y + 232, x + 470, y + 276], radius=10,
                        fill=C.VITRINE)
    t = "Ajouter"
    d.text((x + 390 - d.textlength(t, font=f_min) / 2, y + 247), t,
           font=f_min, fill=(255, 255, 255))

    #  Trois produits en dessous.
    for i in range(3):
        cx = x + 34 + i * 194
        bloc(d, cx, y + 344, 178, 128, (236, 239, 245), 10)
        bloc(d, cx, y + 486, 120, 12, (186, 194, 210))
        bloc(d, cx, y + 508, 66, 12, (210, 216, 226))


def pont(d, x, y, f_min, f_micro):
    """
    Le lien entre les deux, dans les DEUX sens.

    Une flèche unique du back vers le front laisserait croire que la boutique
    ne renvoie rien — et le lecteur se demanderait où atterrit un panier.
    """
    cx = x + PONT // 2

    def trait(yy, sens, couleur):
        x0, x1 = x + 14, x + PONT - 14
        d.line([x0, yy, x1, yy], fill=couleur, width=3)
        px = x1 if sens > 0 else x0
        d.polygon([(px, yy), (px - sens * 14, yy - 7),
                   (px - sens * 14, yy + 7)], fill=couleur)

    trait(y + 172, +1, C.VITRINE)
    trait(y + 388, -1, (150, 160, 180))

    a = "produits · prix · stock"
    d.text((cx - d.textlength(a, font=f_micro) / 2, y + 186), a,
           font=f_micro, fill=C.VITRINE)
    b = "commandes"
    d.text((cx - d.textlength(b, font=f_micro) / 2, y + 402), b,
           font=f_micro, fill=C.GRIS)

    #  La pastille « API », au milieu, posée par-dessus les deux traits.
    w = d.textlength("API", font=f_min) + 44
    d.rounded_rectangle([cx - w / 2, y + 252, cx + w / 2, y + 300],
                        radius=24, fill=C.VITRINE)
    d.text((cx - d.textlength("API", font=f_min) / 2, y + 265), "API",
           font=f_min, fill=(255, 255, 255))


def principal():
    C.verifier()

    out = Image.new("RGB", (L, H), C.FOND)
    d = ImageDraw.Draw(out, "RGBA")

    f_grand = C.police(C.POLICE_G, 27)
    f_petit = C.police(C.POLICE_G, 20)
    f_min = C.police(C.POLICE_G, 18)
    f_micro = C.police(C.POLICE_R, 15)
    f_txt = C.police(C.POLICE_R, 21)
    f_prix = C.police(C.POLICE_G, 26)
    f_bas = C.police(C.POLICE_R, 20)

    xg = MARGE
    xp = xg + PANNEAU_L
    xd = xp + PONT

    back_office(d, xg, Y0, f_petit, f_min)
    vitrine(d, xd, Y0, f_petit, f_min, f_prix)
    pont(d, xp, Y0, f_min, f_micro)

    #  Les étiquettes, sous chaque panneau.
    yl = Y0 + PANNEAU_H + 34
    for x, teinte, titre, sous in (
            (xg, C.ADMIN, "LE BACK-OFFICE",
             "PrestaShop garde le catalogue, les prix, les stocks "
             "et les commandes."),
            (xd, C.VITRINE, "LA VITRINE",
             "Next.js dessine les pages, en les pré-rendant.")):
        d.rectangle([x, yl + 2, x + 8, yl + 28], fill=teinte)
        d.text((x + 22, yl - 2), titre, font=f_grand, fill=C.ENCRE)
        d.text((x, yl + 48), sous, font=f_txt, fill=C.GRIS)

    yb = H - 62
    d.line([MARGE, yb - 22, L - MARGE, yb - 22], fill=C.TRAIT, width=1)
    d.text((MARGE, yb),
           "« Headless » veut dire exactement ça : le logiciel qui gère la "
           "boutique n'est plus celui qui l'affiche. Les deux ne se parlent "
           "que par l'API.",
           font=f_bas, fill=C.GRIS)

    out.save(SORTIE, "WEBP", quality=C.QUALITE, method=6)
    print()
    print("  %d × %d" % out.size)
    print("  %s  (%.0f Ko)"
          % (os.path.basename(SORTIE), os.path.getsize(SORTIE) / 1024))


if __name__ == "__main__":
    principal()
