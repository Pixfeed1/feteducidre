"""
L'animation Shade Smooth contre Subdivision Surface.

    python3 article-blender-astuces/shade_smooth.py        (les trois rendus)
    python3 article-blender-astuces/anime_shade_smooth.py

Produit `astuces-blender-02-shade-smooth-vs-subdivision.webp` (animé) et
`-apercu.jpg`, une planche fixe des trois états pour la relecture.

----------------------------------------------------------------------------
TROIS IMAGES, PAS TRENTE
----------------------------------------------------------------------------
L'animation ne montre que trois états, et rien ne bouge à l'intérieur d'un
état. Il n'y a donc que trois rendus à calculer : les images intermédiaires
sont des fondus, obtenus en mélangeant deux images. Calculer trente rendus
pour obtenir le même résultat aurait coûté dix minutes de machine.

Les temps sont ceux d'une démonstration qu'on regarde, pas d'un montage :
presque une seconde sur l'état de départ, un peu plus sur chacun des deux
suivants, et des fondus courts. La boucle est infinie — un lecteur qui arrive
en cours de route doit pouvoir attendre le tour suivant.

----------------------------------------------------------------------------
LE BANDEAU CHANGE AU MILIEU DU FONDU
----------------------------------------------------------------------------
Le texte n'est pas fondu avec l'image : il bascule d'un coup à mi-parcours. Un
texte en fondu croisé devient illisible pendant sa transition, et c'est
précisément le moment où le lecteur cherche à comprendre ce qui se passe.

----------------------------------------------------------------------------
LES NOMBRES VIENNENT DU FICHIER DE COMPTES
----------------------------------------------------------------------------
Ils sont relevés sur les maillages évalués par `shade_smooth.py`, pas recopiés
ici. Le nombre de faces après subdivision de niveau 2 est 7 936 et non 8 192,
parce qu'une UV sphere a des triangles aux pôles — une raison de plus pour ne
pas écrire ces chiffres à la main.
"""

import json
import os

from PIL import Image, ImageDraw

import charte as C

RACINE = os.path.dirname(os.path.abspath(__file__))
COMPTES = os.path.join(RACINE, "ss-comptes.json")
BASE = os.path.join(RACINE, "astuces-blender-02-shade-smooth-vs-subdivision")

BANDE = 72
ENCRE = (24, 25, 30)
SUR_ENCRE = (243, 241, 235)
DISCRET = (172, 174, 182)
PAPIER = (250, 249, 246)
FILET = (213, 211, 204)

#  (fichier, intitulé, commentaire) — le compte de faces s'y ajoute.
ETATS = (
    ("ss-1-flat", "SHADE FLAT", "l’état de départ"),
    ("ss-2-smooth", "SHADE SMOOTH", "l’ombrage change, la géométrie non"),
    ("ss-3-subdiv", "SUBDIVISION SURFACE, NIVEAU 2",
     "la géométrie change vraiment"),
)

#  Durées en millisecondes. Le troisième état dure le plus longtemps : c'est
#  la réponse, et c'est sur elle que l'oeil doit rester.
POSE = (900, 1200, 1600)
FONDU_IMAGES = 8
FONDU_DUREE = 45


def nb(n):
    """Un nombre à la française : espace fine pour les milliers."""
    return "{:,}".format(n).replace(",", " ")


def espace(d, xy, texte, f, teinte, tracking):
    x, y = xy
    for c in texte:
        d.text((x, y), c, font=f, fill=teinte)
        x += d.textlength(c, font=f) + tracking
    return x - tracking


def bandeau(im, titre, commentaire, faces, polices):
    """Une copie de l'image avec son bandeau de légende en pied."""
    f_titre, f_sous, f_faces = polices
    out = im.copy()
    d = ImageDraw.Draw(out)
    l, h = out.size
    d.rectangle([0, h - BANDE, l, h], fill=ENCRE)
    espace(d, (24, h - BANDE + 16), titre, f_titre, SUR_ENCRE, 2.2)
    d.text((24, h - BANDE + 44), commentaire, font=f_sous, fill=DISCRET)

    #  Le compte de faces est calé à droite, toujours au même endroit : c'est
    #  ce qui permet de voir le chiffre changer sans chercher où regarder.
    t = "%s faces" % nb(faces)
    largeur = d.textlength(t, font=f_faces)
    if 24 + d.textlength(commentaire, font=f_sous) > l - 32 - largeur:
        raise SystemExit("le commentaire « %s » touche le compte de faces"
                         % commentaire)
    d.text((l - 24 - largeur, h - BANDE + 26), t, font=f_faces, fill=SUR_ENCRE)
    return out


def principal():
    if not os.path.exists(COMPTES):
        raise SystemExit("comptes absents : lancez d'abord "
                         "`python3 article-blender-astuces/shade_smooth.py`")
    with open(COMPTES, encoding="utf-8") as f:
        comptes = json.load(f)

    C.verifier()

    brutes = []
    for nom, _, _ in ETATS:
        chemin = os.path.join(RACINE, "%s.png" % nom)
        if not os.path.exists(chemin):
            raise SystemExit("rendu absent : %s" % os.path.basename(chemin))
        brutes.append(Image.open(chemin).convert("RGB"))
    if len({im.size for im in brutes}) != 1:
        raise SystemExit("les trois rendus n'ont pas la même taille")

    polices = (C.police(C.POLICE_G, 18), C.police(C.POLICE_R, 16),
               C.police(C.POLICE_G, 20))
    etiquetees = [bandeau(im, titre, com, comptes[nom], polices)
                  for im, (nom, titre, com) in zip(brutes, ETATS)]

    #  LE FONDU PORTE SUR L'IMAGE SEULE. On mélange les rendus bruts, puis on
    #  repose un bandeau net par-dessus — celui de l'état vers lequel on va dès
    #  qu'on a passé la moitié.
    images, durees = [], []
    for i, im in enumerate(etiquetees):
        images.append(im)
        durees.append(POSE[i])
        if i == len(etiquetees) - 1:
            break
        for k in range(1, FONDU_IMAGES + 1):
            t = k / float(FONDU_IMAGES + 1)
            melange = Image.blend(brutes[i], brutes[i + 1], t)
            j = i if t < 0.5 else i + 1
            nom, titre, com = ETATS[j]
            images.append(bandeau(melange, titre, com, comptes[nom], polices))
            durees.append(FONDU_DUREE)

    images[0].save(BASE + ".webp", "WEBP", save_all=True,
                   append_images=images[1:], duration=durees, loop=0,
                   quality=88, method=6)

    #  Une planche fixe à côté : une image animée ne se relit pas image par
    #  image, et il faut bien vérifier les trois états avant publication.
    l, h = etiquetees[0].size
    marge, gouttiere = 30, 20
    larg = (1600 - 2 * marge - 2 * gouttiere) // 3
    haut = int(round(larg * h / l))
    planche = Image.new("RGB", (1600, haut + 2 * marge), PAPIER)
    dd = ImageDraw.Draw(planche)
    for i, im in enumerate(etiquetees):
        x = marge + i * (larg + gouttiere)
        planche.paste(im.resize((larg, haut), Image.LANCZOS), (x, marge))
        dd.rectangle([x, marge, x + larg - 1, marge + haut - 1],
                     outline=FILET, width=1)
    planche.save(BASE + "-apercu.jpg", "JPEG", quality=92, optimize=True)

    total = sum(durees)
    print()
    print("  %d images, %.2f s de boucle, %d × %d"
          % (len(images), total / 1000.0, l, h))
    print("  faces : %s puis %s puis %s"
          % tuple(nb(comptes[n]) for n, _, _ in ETATS))
    for e in (".webp", "-apercu.jpg"):
        print("  %-56s %.0f Ko" % (os.path.basename(BASE + e),
                                   os.path.getsize(BASE + e) / 1024))


if __name__ == "__main__":
    principal()
