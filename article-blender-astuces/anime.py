"""
Le montage commun aux figures animées de l'article.

Les deux animations — l'édition proportionnelle et Shift+R / F9 — sont faites
de la même façon : Blender 5.2.1 LTS joue une séquence sur un écran X virtuel,
`xwd` photographie l'écran entre chaque étape, et il reste à rogner, réduire,
légender et assembler. Seuls le plan de la séquence et les légendes changent
d'une figure à l'autre ; tout le reste est ici.

----------------------------------------------------------------------------
TROIS FICHIERS PAR FIGURE, ET UN SEUL VA DANS L'ARTICLE
----------------------------------------------------------------------------
  - `.webp`, l'animation, celle qui est publiée ;
  - `.gif`, la même chose pour les lecteurs qui n'animent pas le WebP —
    l'Explorateur Windows en montre la première image et s'arrête là, ce qui
    donne d'une bonne animation l'impression d'une image fixe et ratée ;
  - `-apercu.jpg`, une planche fixe des moments clés, pour la relecture : une
    image animée ne se relit pas image par image.

----------------------------------------------------------------------------
LE BANDEAU BASCULE, IL NE SE FOND PAS
----------------------------------------------------------------------------
Le texte change d'un coup au changement de phase. Un texte en fondu devient
illisible pendant sa transition, et c'est précisément le moment où le lecteur
cherche à comprendre ce qui vient de se passer.
"""

import glob
import os

import numpy as np
from PIL import Image, ImageDraw

import charte as C

BANDE = 66
ENCRE = (24, 25, 30)
SUR_ENCRE = (243, 241, 235)
DISCRET = (172, 174, 182)
PAPIER = (250, 249, 246)
FILET = (213, 211, 204)

#  La provenance tient dans le bandeau, calée à droite. Une figure doit dire
#  d'où elle vient sans qu'on ait à lire l'article autour.
SOURCE = "BLENDER 5.2.1 LTS — CAPTURE D’ÉCRAN"

#  Une qualité basse pour une image fixe, et c'est voulu : trente images font
#  un fichier lourd, et un aplat gris parcouru de fils noirs ne souffre pas de
#  la compression. Contrôlé à l'oeil sur les images les plus fragiles.
QUALITE = 68

#  Le GIF de secours n'a droit qu'à une palette. Cent vingt-huit teintes
#  suffisent : le viewport est gris, et les seules couleurs vives sont les axes
#  et le contour de sélection.
GIF_COULEURS = 128


def polices():
    """Titre, commentaire, mention de source."""
    return (C.police(C.POLICE_G, 17), C.police(C.POLICE_R, 15),
            C.police(C.POLICE_G, 11))


def espace(d, xy, texte, f, teinte, tracking):
    x, y = xy
    for c in texte:
        d.text((x, y), c, font=f, fill=teinte)
        x += d.textlength(c, font=f) + tracking
    return x - tracking


def charger(dossier, attendu, largeur, bas_coupe):
    """
    Les captures, rognées du bas et réduites à `largeur`.

    La capture couvre toute l'aire de la vue 3D, barre d'outils et en-tête
    compris. On lui retire une bande de sol vide en bas, et rien d'autre : le
    sujet est centré dans la vue, et rogner plus le ferait redescendre.
    """
    chemins = sorted(glob.glob(os.path.join(dossier, "*.png")))
    if not chemins:
        raise SystemExit("captures absentes dans %s : lancez d'abord "
                         "`capturer-anime.sh`" % dossier)
    if len(chemins) != attendu:
        raise SystemExit("%d captures pour %d étapes prévues : la séquence "
                         "jouée dans Blender a changé"
                         % (len(chemins), attendu))

    brutes = [Image.open(c).convert("RGB") for c in chemins]
    if len({b.size for b in brutes}) != 1:
        raise SystemExit("les captures n'ont pas toutes la même taille")
    bl, bh = brutes[0].size
    if bh <= bas_coupe + 200:
        raise SystemExit("la capture est trop courte pour être rognée")

    haut = int(round(largeur * (bh - bas_coupe) / float(bl)))
    return [b.crop((0, 0, bl, bh - bas_coupe)).resize((largeur, haut),
                                                      Image.LANCZOS)
            for b in brutes]


def _gris(vues, i, depuis, jusqu):
    return np.asarray(vues[i].convert("L"), dtype=np.int16)[depuis:jusqu]


def changement(vues, indices, depuis=0, jusqu=None, ref=0):
    """
    La part de la bande `depuis:jusqu` qui a changé, par rapport à `ref`.

    Les bornes verticales sont tout l'intérêt de la mesure : pendant un
    opérateur, Blender écrit ses valeurs juste sous les menus, et une
    comparaison portant sur l'image entière trouverait une belle différence
    même sur une séquence où rien n'a bougé dans la vue. C'est arrivé.
    """
    depart = _gris(vues, ref, depuis, jusqu)
    part = 0.0
    for i in indices:
        v = _gris(vues, i, depuis, jusqu)
        part = max(part, float(np.mean(np.abs(v - depart) > 40)))
    return part


def etendue(vues, i, depuis=0, jusqu=None, ref=0):
    """
    La largeur, en fraction de l'image, sur laquelle deux images diffèrent.

    Une part de pixels modifiés ne dit pas OÙ ils sont : quatre copies posées
    l'une sur l'autre changent autant de pixels qu'une seule. L'étendue, elle,
    distingue une rangée d'un tas — c'est exactement l'erreur qui s'était
    glissée dans la première série, où le chiffre tapé n'arrivait pas et où
    les cinq cubes se superposaient.
    """
    a = _gris(vues, ref, depuis, jusqu)
    b = _gris(vues, i, depuis, jusqu)
    colonnes = np.where((np.abs(b - a) > 40).sum(axis=0) > 3)[0]
    if colonnes.size == 0:
        return 0.0
    return float(colonnes.max() - colonnes.min() + 1) / a.shape[1]


def bandeau(im, titre, commentaire, pol):
    """Une copie de l'image, son bandeau de légende posé en pied."""
    f_titre, f_sous, f_source = pol
    out = im.copy()
    d = ImageDraw.Draw(out)
    l, h = out.size
    d.rectangle([0, h - BANDE, l, h], fill=ENCRE)
    fin = espace(d, (22, h - BANDE + 14), titre, f_titre, SUR_ENCRE, 2.2)
    d.text((22, h - BANDE + 40), commentaire, font=f_sous, fill=DISCRET)

    largeur = sum(d.textlength(c, font=f_source) + 1.6 for c in SOURCE) - 1.6
    depart = l - 22 - largeur
    if max(fin, 22 + d.textlength(commentaire, font=f_sous)) > depart - 24:
        raise SystemExit("le bandeau « %s » touche la mention de source"
                         % titre)
    espace(d, (depart, h - BANDE + 27), SOURCE, f_source, DISCRET, 1.6)
    return out


def gif(base, images, durees):
    """
    La même animation en GIF, pour les lecteurs qui n'animent pas le WebP.

    Une seule palette pour toute la séquence, et surtout PAS de tramage. Le
    viewport de Blender est un aplat gris ; y disperser l'erreur de couleur
    sème un bruit qui change à chaque image, et le GIF ne compresse plus rien
    d'une image à l'autre. Mesuré sur la figure 05 : 491 Ko sans tramage,
    2 534 Ko avec, pour une image moins propre.
    """
    l, h = images[0].size
    bande = Image.new("RGB", (l, h * len(images)))
    for i, im in enumerate(images):
        bande.paste(im, (0, i * h))
    palette = bande.quantize(colors=GIF_COULEURS,
                             method=Image.Quantize.MEDIANCUT)

    reduites = [im.quantize(palette=palette, dither=Image.Dither.NONE)
                for im in images]
    reduites[0].save(base + ".gif", save_all=True, append_images=reduites[1:],
                     duration=durees, loop=0, optimize=True)


def planche(base, images, cles):
    """La planche fixe des moments clés, pour la relecture."""
    marge, gouttiere = 24, 16
    n = len(cles)
    larg = (1600 - 2 * marge - (n - 1) * gouttiere) // n
    ht = int(round(larg * images[0].height / float(images[0].width)))
    out = Image.new("RGB", (1600, ht + 2 * marge), PAPIER)
    d = ImageDraw.Draw(out)
    for i, k in enumerate(cles):
        x = marge + i * (larg + gouttiere)
        out.paste(images[k].resize((larg, ht), Image.LANCZOS), (x, marge))
        d.rectangle([x, marge, x + larg - 1, marge + ht - 1], outline=FILET,
                    width=1)
    out.save(base + "-apercu.jpg", "JPEG", quality=92, optimize=True)


def enregistrer(base, images, durees, cles):
    """Les trois fichiers, et le relevé de ce qui a été écrit."""
    images[0].save(base + ".webp", "WEBP", save_all=True,
                   append_images=images[1:], duration=durees, loop=0,
                   quality=QUALITE, method=6)
    gif(base, images, durees)
    planche(base, images, cles)

    print()
    print("  %d images  %d × %d  %.2f s de boucle"
          % (len(images), images[0].width, images[0].height,
             sum(durees) / 1000.0))
    for e in (".webp", ".gif", "-apercu.jpg"):
        print("  %-56s %.0f Ko" % (os.path.basename(base + e),
                                   os.path.getsize(base + e) / 1024))
