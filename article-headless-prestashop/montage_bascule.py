"""
IMAGE 5 de l'article « PrestaShop headless » — le sélecteur de bascule.

    python3 article-headless-prestashop/montage_bascule.py

Produit `article-headless-prestashop/bascule-progressive-back-office-prestashop.webp`
à partir de `bascule-capture-prestashop-8.2.8.png`.

----------------------------------------------------------------------------
C'EST UNE VRAIE CAPTURE, ET VOILÀ CE QU'IL A FALLU
----------------------------------------------------------------------------
La première version de cette figure était une maquette, faute de pouvoir faire
tourner PrestaShop. C'était une conclusion prématurée : le démon Docker était
installé, seul son socket manquait, et le blocage venait du CDN de Docker Hub —
pas des autres registres. En passant par le miroir Google, les images se
téléchargent.

L'installeur bute ensuite sur le téléchargement du pack de traduction, servi
par prestashop.com, injoignable ici. Deux `throw` neutralisés dans
`Install.php` suffisent à passer outre : PrestaShop s'installe alors avec les
chaînes anglaises livrées dans son code. C'est la seule modification apportée
au logiciel, et elle ne touche que l'installeur.

D'où une conséquence visible : l'ossature du back-office est en anglais. Tout
ce qui parle français vient du module, dont les libellés sont à nous.

Le module est réel, installé par `prestashop:module install`, et la page est
rendue par PrestaShop : rien n'est redessiné.

----------------------------------------------------------------------------
ANONYMISATION
----------------------------------------------------------------------------
Boutique de démonstration installée pour l'occasion : aucun nom de client,
aucun domaine, aucun produit. Les adresses du champ sont prises dans
203.0.113.0/24, la plage que la RFC 5737 réserve à la documentation.
"""

import os

from PIL import Image, ImageDraw

import charte as C

RACINE = os.path.dirname(os.path.abspath(__file__))
CAPTURE = os.path.join(RACINE, "bascule-capture-prestashop-8.2.8.png")
SORTIE = os.path.join(
    RACINE, "bascule-progressive-back-office-prestashop.webp")

LARGEUR = 1600
#  La page capturée est plus haute que son contenu : on coupe sous le panneau.
#  Mesuré sur l'image, pas estimé.
BAS = 1180


def principal():
    if not os.path.exists(CAPTURE):
        raise SystemExit("capture absente : %s" % CAPTURE)
    C.verifier()

    cap = Image.open(CAPTURE).convert("RGB")
    if BAS > cap.height:
        raise SystemExit("la capture fait %d px de haut, la coupe en demande %d"
                         % (cap.height, BAS))
    cap = cap.crop((0, 0, cap.width, BAS))
    h = int(round(LARGEUR * cap.height / cap.width))

    marge, pied = 34, 76
    L = LARGEUR + marge * 2
    H = marge + h + pied + marge
    out = Image.new("RGB", (L, H), C.FOND)
    d = ImageDraw.Draw(out)

    vign = cap.resize((LARGEUR, h), Image.LANCZOS)
    out.paste(vign, (marge, marge))
    d.rectangle([marge, marge, marge + LARGEUR - 1, marge + h - 1],
                outline=C.BORD, width=2)

    y = marge + h + 26
    d.line([marge, y, L - marge, y], fill=C.TRAIT, width=1)
    f = C.police(C.POLICE_R, 19)
    d.text((marge, y + 14),
           "Capture d'un back-office PrestaShop 8.2.8 installé pour l'article, "
           "avec le module qui porte le réglage. L'ossature est en anglais : le "
           "pack de traduction français",
           font=f, fill=C.FAIBLE)
    d.text((marge, y + 38),
           "se télécharge depuis prestashop.com, injoignable ici. Boutique de "
           "démonstration — aucun client, aucun domaine ; adresses prises dans "
           "203.0.113.0/24 (RFC 5737).",
           font=f, fill=C.FAIBLE)

    out.save(SORTIE, "WEBP", quality=C.QUALITE, method=6)
    print()
    print("  capture %d × %d  ->  figure %d × %d" % (*cap.size, *out.size))
    print("  %s  (%.0f Ko)"
          % (os.path.basename(SORTIE), os.path.getsize(SORTIE) / 1024))


if __name__ == "__main__":
    principal()
