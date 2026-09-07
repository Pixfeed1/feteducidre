"""
Les quatre cases à cocher qui rendent Blender utilisable sur un portable.

    ECRAN=1700x1300 sh article-blender-astuces/blender-gui/capturer-anime.sh \
        setup-preferences.py preferences
    python3 article-blender-astuces/montage_preferences.py

Produit `astuces-blender-07-preferences-portable.webp` et son PNG.

----------------------------------------------------------------------------
DEUX VRAIES CAPTURES DES PRÉFÉRENCES DE BLENDER 5.2.1
----------------------------------------------------------------------------
Les quatre réglages sont réellement cochés dans les préférences avant la
photo, et le script refuse de continuer si l'un d'eux n'a pas pris. Ce ne sont
pas des cases dessinées.

L'éditeur Preferences occupe une aire de la fenêtre plutôt qu'une seconde
fenêtre : `xwd` photographie l'écran entier, et deux fenêtres l'une sur
l'autre auraient donné une capture illisible.

----------------------------------------------------------------------------
UNE FENÊTRE ÉTROITE, EXPRÈS
----------------------------------------------------------------------------
Sur un écran large, Blender range les propriétés en deux colonnes et rogne les
intitulés : la première capture affichait « Emulate 3 Button ... ». C'est
précisément le nom que le lecteur doit reconnaître. L'écran virtuel est donc
réduit à 1700 pixels, ce qui rend la colonne unique et l'intitulé entier.

----------------------------------------------------------------------------
CE QUE L'ARTICLE APPELLE « AUTO DEPTH »
----------------------------------------------------------------------------
Dans le panneau, ce réglage ne s'écrit pas comme ça : la ligne s'appelle
« Auto » et porte deux cases, « Perspective » et « Depth ». C'est la seconde.
Le nom interne est bien `use_mouse_depth_navigate`, et tout le monde dit Auto
Depth — mais un lecteur qui cherche ces deux mots côte à côte ne les trouvera
pas. Le repère est donc posé sur « Depth », et la légende le dit.

Au passage : « Perspective », juste au-dessus, est cochée par défaut. Elle
n'est pas dans la liste des quatre, et elle n'est pas entourée.

----------------------------------------------------------------------------
LES REPÈRES
----------------------------------------------------------------------------
Quatre rectangles rouges, et rien d'autre. Leurs coordonnées ne sont pas
écrites à la main : les cases cochées sont retrouvées à leur bleu, les
intitulés à leur clarté, et le repère se pose autour de ce qui a été mesuré.
Trois autres cases sont cochées sur ces deux pages — Continuous Grab, Release
Confirms, Auto Perspective — et il fallait justement ne pas les entourer.
"""

import os

from PIL import Image, ImageDraw

import charte as C

RACINE = os.path.dirname(os.path.abspath(__file__))
IMAGES = "/tmp/bl-preferences/frames"
BASE = os.path.join(RACINE, "astuces-blender-07-preferences-portable")

L = 1600
MARGE = 40
GOUTTIERE = 32

PAPIER = (250, 249, 246)
ENCRE = (24, 25, 30)
FAIBLE = (140, 141, 150)
FILET = (213, 211, 204)
#  Un rouge plus clair que celui de la figure de l'Outliner. Le fond des
#  préférences est un gris 61, celui de l'arborescence un gris 30 : la même
#  teinte n'y tenait plus le rapport de 3:1 exigé d'un élément graphique. Le
#  contrôle plus bas l'a refusée, et il avait raison.
ROUGE = (245, 88, 72)
FOND_PANNEAU = (61, 61, 61)
FOND_CHAMP = (48, 48, 48)

#  Le découpage de chaque capture, relevé sur les images : on garde les
#  panneaux entiers, bordure comprise, et on coupe dans le blanc entre deux
#  panneaux — jamais au milieu de l'un d'eux.
#
#  La colonne de gauche est laissée de côté. Elle dit où l'on se trouve, mais
#  elle fait trois cent cinquante pixels de large sur mille quatre cents, et la
#  garder revenait à réduire tout le reste d'un tiers. Les intitulés
#  deviendraient alors moins lisibles que sur l'écran de quelqu'un qui cherche
#  ces cases — ce qui serait manquer le but. Le bandeau dit le chemin.
DECOUPES = ((336, 8, 1380, 676),        # Input : Keyboard et Mouse
            (336, 8, 1380, 786))        # Navigation : Orbit & Pan et Zoom

#  Les lignes où se trouvent les cases cochées, dans la capture d'origine.
#  Elles servent à retrouver la case et son intitulé, pas à dessiner : les
#  bornes du repère sont mesurées autour.
LIGNES = (((134, 159), (310, 335)),     # Emulate Numpad, Emulate 3 Button
          ((334, 359), (648, 673)))     # Auto Depth, Zoom to Mouse Position

#  Le repère déborde de ce qu'il entoure, et un peu plus à gauche pour englober
#  la case elle-même quand l'intitulé est à sa droite.
DEBORD = 8

TITRES = ("PREFERENCES > INPUT", "PREFERENCES > NAVIGATION")
SOUS = ("le pavé numérique et la molette, sans pavé numérique ni molette",
        "le zoom qui vise juste, et celui qui ne se bloque plus")

PIED = (
    "Captures de Blender 5.2.1 LTS, les quatre réglages réellement cochés "
    "avant la photo. Trois autres cases sont cochées sur ces pages",
    "et ne font pas partie des quatre. « Auto Depth » s’affiche en deux "
    "temps : la ligne « Auto », puis la case « Depth ».",
)


def typo(t):
    return t.replace("'", "’")


def espace(d, xy, texte, f, teinte, tracking):
    x, y = xy
    for c in texte:
        d.text((x, y), c, font=f, fill=teinte)
        x += d.textlength(c, font=f) + tracking
    return x - tracking


JOINTURE = 30            # écart maximal entre deux morceaux d'un même intitulé


def repere(im, y0, y1):
    """
    Les bornes du rectangle rouge autour d'une case et de son intitulé.

    L'intitulé n'est pas toujours du même côté. « Emulate Numpad » est à droite
    de sa case, « Emulate 3 Button Mouse » à sa gauche — et à sa droite se
    trouve la liste déroulante Alt. Un repère qui partait de la case et
    s'étendait vers la droite coupait donc l'intitulé en deux : « Emulate 3
    Butto | n Mouse ». Ça se voyait sur l'image.

    On part donc de la case cochée, retrouvée à son bleu, et on s'étend des
    DEUX côtés tant que les caractères se suivent — mais vers la droite
    seulement si la case n'est pas collée à un champ, sinon le repère
    traverserait le widget voisin.
    """
    import numpy as np

    couleur = np.asarray(im.convert("RGB"), dtype=np.int16)[y0:y1 + 1]
    r, g, b = couleur[:, :, 0], couleur[:, :, 1], couleur[:, :, 2]
    bleus = np.where(((b > 150) & (b - r > 60)).sum(axis=0) > 0)[0]
    if bleus.size == 0:
        raise SystemExit("aucune case cochée sur la ligne %d" % y0)
    case = (int(bleus.min()), int(bleus.max()))

    gris = np.asarray(im.convert("L"), dtype=np.int16)
    clair = np.where((gris[y0 - 4:y1 + 5] > 150).sum(axis=0) > 0)[0]

    gauche = case[0]
    for x in clair[clair < case[0]][::-1]:
        if gauche - x > JOINTURE:
            break
        gauche = int(x)

    droite = case[1]
    if abs(int(gris[(y0 + y1) // 2, case[1] + 8]) - FOND_PANNEAU[0]) <= 6:
        for x in clair[clair > case[1]]:
            if x - droite > JOINTURE:
                break
            droite = int(x)

    return gauche, droite


def principal():
    chemins = [os.path.join(IMAGES, "%02d.png" % i) for i in range(2)]
    manquants = [c for c in chemins if not os.path.exists(c)]
    if manquants:
        raise SystemExit(
            "captures absentes : lancez d'abord\n"
            "  ECRAN=1700x1300 sh article-blender-astuces/blender-gui/"
            "capturer-anime.sh setup-preferences.py preferences")

    C.verifier()
    for nom, fond in (("le fond des panneaux", FOND_PANNEAU),
                      ("celui des champs", FOND_CHAMP)):
        if C.contraste(ROUGE, fond) < 3.0:
            raise SystemExit("le repère rouge ne ressort pas assez sur %s "
                             "(%.2f:1)" % (nom, C.contraste(ROUGE, fond)))

    brutes = [Image.open(c).convert("RGB") for c in chemins]
    if len({b.size for b in brutes}) != 1:
        raise SystemExit("les deux captures n'ont pas la même taille")

    #  LES REPÈRES SONT POSÉS AVANT LE DÉCOUPAGE, dans le repère de la capture
    #  d'origine : c'est là que les coordonnées ont été mesurées.
    vues = []
    for brute, lignes, coupe in zip(brutes, LIGNES, DECOUPES):
        marquee = brute.copy()
        d = ImageDraw.Draw(marquee)
        for y0, y1 in lignes:
            g, dr = repere(brute, y0, y1)
            d.rounded_rectangle([g - DEBORD, y0 - DEBORD,
                                 dr + DEBORD, y1 + DEBORD],
                                radius=6, outline=ROUGE, width=3)
        vues.append(marquee.crop(coupe))

    largeur = (L - 2 * MARGE - GOUTTIERE) // 2
    echelles = [largeur / float(v.width) for v in vues]
    if max(echelles) > 1.0:
        raise SystemExit("les captures seraient agrandies : le montage "
                         "perdrait en netteté")
    reduites = [v.resize((largeur, int(round(v.height * e))), Image.LANCZOS)
                for v, e in zip(vues, echelles)]
    hauteur = max(v.height for v in reduites)

    f_titre = C.police(C.POLICE_G, 16)
    f_sous = C.police(C.POLICE_R, 17)
    f_pied = C.police(C.POLICE_R, 18)

    y_titre = 56
    y_vue = y_titre + 52
    y_pied = y_vue + hauteur + 40
    H = y_pied + 16 + len(PIED) * 24 + 40

    out = Image.new("RGB", (L, H), PAPIER)
    d = ImageDraw.Draw(out)

    for i, vue in enumerate(reduites):
        x = MARGE + i * (largeur + GOUTTIERE)
        espace(d, (x, y_titre), TITRES[i], f_titre, ENCRE, 2.2)
        if d.textlength(typo(SOUS[i]), font=f_sous) > largeur:
            raise SystemExit("le sous-titre %d déborde de sa vignette"
                             % (i + 1))
        d.text((x, y_titre + 24), typo(SOUS[i]), font=f_sous, fill=FAIBLE)
        out.paste(vue, (x, y_vue))
        d.rectangle([x, y_vue, x + largeur - 1, y_vue + vue.height - 1],
                    outline=FILET, width=1)

    d.line([MARGE, y_pied, L - MARGE, y_pied], fill=FILET, width=1)
    for i, ligne in enumerate(PIED):
        ligne = typo(ligne)
        if d.textlength(ligne, font=f_pied) > L - 2 * MARGE:
            raise SystemExit("la ligne %d du pied déborde" % (i + 1))
        d.text((MARGE, y_pied + 16 + i * 24), ligne, font=f_pied, fill=FAIBLE)

    out.save(BASE + ".webp", "WEBP", quality=C.QUALITE, method=6)
    out.save(BASE + ".png", "PNG", optimize=True)
    print()
    print("  captures %s  ->  figure %d × %d"
          % (" et ".join("%d × %d" % v.size for v in vues), L, H))
    for e in (".webp", ".png"):
        print("  %-52s %.0f Ko" % (os.path.basename(BASE + e),
                                   os.path.getsize(BASE + e) / 1024))


if __name__ == "__main__":
    principal()
