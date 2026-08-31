"""
La figure « licences expirées », montée autour de la capture WordPress.

    python3 article-agence-web/montage_licences.py

Produit `article-agence-web/licences-expirees-mises-a-jour-securite.webp`
à partir de `licences-capture-wordpress-7.1.png`.

----------------------------------------------------------------------------
POURQUOI IL N'Y A AUCUNE ANNOTATION SUR L'IMAGE
----------------------------------------------------------------------------
Il n'y a rien à désigner. L'écran dit déjà tout, et il le dit avec les mots de
WordPress : « La mise à jour automatique n'est pas possible pour cette
extension », trois fois, en rouge, sous trois extensions dont deux touchent à
la sécurité et au paiement.

Une flèche ou un cercle par-dessus n'ajouterait rien et retirerait ce qui fait
la valeur de cette image : qu'elle ressemble exactement à ce qu'on voit en
ouvrant le back-office d'un site qu'on récupère.

Le seul ajout est un pied de figure qui dit d'où vient la capture. Une image
d'écran sans provenance ne vaut pas grand-chose, et le lecteur a le droit de
savoir ce qui a été installé pour l'occasion.
"""

import os

from PIL import Image, ImageDraw

import charte as C

RACINE = os.path.dirname(os.path.abspath(__file__))
CAPTURE = os.path.join(RACINE, "licences-capture-wordpress-7.1.png")
BASE = os.path.join(RACINE, "licences-expirees-mises-a-jour-securite")

#  Deux fichiers, et ce n'est pas un doublon inutile : le WebP part sur le
#  site, le PNG sert à REGARDER l'image avant de la mettre en ligne. Windows et
#  macOS n'ouvrent pas le WebP par défaut et proposent d'installer un logiciel,
#  ce qui donne l'impression que le fichier est cassé alors qu'il va très bien.
SORTIE = BASE + ".webp"
APERCU = BASE + ".png"

LARGEUR = 1600

PIED = (
    "Capture d'un WordPress 7.1 installé pour l'article. Les trois extensions "
    "sont écrites pour la démonstration : elles déclarent une version "
    "disponible sans fournir de paquet,",
    "ce que répond un serveur de licences quand l'abonnement est terminé. La "
    "phrase « La mise à jour automatique n'est pas possible » vient de "
    "WordPress lui-même, pas de moi.",
)


def principal():
    if not os.path.exists(CAPTURE):
        raise SystemExit(
            "capture absente : %s\n        lancez d'abord "
            "`python3 article-agence-web/capture_licences.py`" % CAPTURE)
    C.verifier()

    cap = Image.open(CAPTURE).convert("RGB")
    h = int(round(LARGEUR * cap.height / cap.width))

    marge, pied = 34, 76
    L = LARGEUR + marge * 2
    H = marge + h + pied + marge
    out = Image.new("RGB", (L, H), C.FOND)
    d = ImageDraw.Draw(out)

    out.paste(cap.resize((LARGEUR, h), Image.LANCZOS), (marge, marge))
    d.rectangle([marge, marge, marge + LARGEUR - 1, marge + h - 1],
                outline=C.BORD, width=2)

    y = marge + h + 26
    d.line([marge, y, L - marge, y], fill=C.TRAIT, width=1)
    f = C.police(C.POLICE_R, 19)
    #  On vérifie que les deux lignes tiennent : un pied de figure qui déborde
    #  se coupe en plein mot et ça ne se voit qu'une fois publié.
    for i, ligne in enumerate(PIED):
        if d.textlength(ligne, font=f) > LARGEUR:
            raise SystemExit("la ligne %d du pied déborde de %.0f px"
                             % (i + 1, d.textlength(ligne, font=f) - LARGEUR))
        d.text((marge, y + 14 + i * 24), ligne, font=f, fill=C.FAIBLE)

    out.save(SORTIE, "WEBP", quality=C.QUALITE, method=6)
    out.save(APERCU, "PNG", optimize=True)
    print()
    print("  capture %d × %d  ->  figure %d × %d" % (*cap.size, *out.size))
    for f in (SORTIE, APERCU):
        print("  %-48s %.0f Ko"
              % (os.path.basename(f), os.path.getsize(f) / 1024))


if __name__ == "__main__":
    principal()
