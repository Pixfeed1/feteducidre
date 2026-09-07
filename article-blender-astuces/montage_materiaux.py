"""
Les matériaux en .001, et le compteur qui dit ce qu'on traîne.

    sh article-blender-astuces/blender-gui/capturer-anime.sh \
        setup-materiaux.py materiaux
    python3 article-blender-astuces/montage_materiaux.py

Produit `astuces-blender-08-materiaux-001-statistics.webp` et son PNG.

----------------------------------------------------------------------------
DEUX MOMENTS DU MÊME FICHIER
----------------------------------------------------------------------------
La liste de gauche et le compteur de droite viennent du même Blender, à la
même seconde : c'est la même aire de la fenêtre, photographiée une fois en vue
3D et une fois passée en Outliner. Les deux nombres se contredisent, et c'est
tout le propos — onze objets, quinze matériaux.

Les quinze matériaux sont de vraies copies faites par Blender, qui les
numérote lui-même de Metal.001 à Metal.014. Le script de scène refuse de
continuer s'il n'en trouve pas le compte exact, et le montage relit ce compte
dans le fichier écrit par Blender plutôt que de le recopier ici.

----------------------------------------------------------------------------
UNE SEULE ÉCHELLE POUR LES DEUX VIGNETTES
----------------------------------------------------------------------------
Elles sont découpées dans la même capture, à la même définition. Les réduire
chacune à la même LARGEUR aurait donné deux interfaces de tailles différentes
côte à côte, ce qui se voit tout de suite et fait faux. Elles sont donc
réduites du même facteur, et c'est la somme de leurs largeurs qui tient dans
la page.
"""

import json
import os

from PIL import Image, ImageDraw

import charte as C

RACINE = os.path.dirname(os.path.abspath(__file__))
TRAVAIL = "/tmp/bl-materiaux"
IMAGES = os.path.join(TRAVAIL, "frames")
BASE = os.path.join(RACINE, "astuces-blender-08-materiaux-001-statistics")

L = 1600
MARGE = 40
GOUTTIERE = 32

PAPIER = (250, 249, 246)
ENCRE = (24, 25, 30)
FAIBLE = (140, 141, 150)
FILET = (213, 211, 204)

#  Les découpes (x, y, largeur, hauteur), relevées sur les captures.
#
#  Pour l'Outliner : l'en-tête, la ligne « Current File » et les quinze noms,
#  qui s'arrêtent à la ligne 719.
#
#  Pour la vue 3D : sous la barre d'en-tête (dernière ligne de texte à 95) et à
#  droite de la barre d'outils, de quoi tenir tout le bloc du compteur — de
#  « User Perspective » à 132 jusqu'à « Triangles » à 393 — et assez de sphères
#  pour qu'on voie de quelle scène il parle. Le premier découpage partait de la
#  ligne 150 et tranchait « User Perspective » par le milieu.
#
#  Les deux hauteurs sont voisines exprès : les vignettes sont alors côte à
#  côte sans qu'une flotte au milieu du vide de l'autre.
DECOUPES = ((0, 0, 780, 760),            # 01 : l'Outliner
            (110, 112, 1150, 780))       # 00 : la vue 3D et son compteur

#  (fichier de capture, découpe) — la vue 3D est la première image, l'Outliner
#  la seconde ; dans la figure c'est l'inverse, la liste d'abord.
PANNEAUX = (("01.png", 0), ("00.png", 1))

TITRES = ("OUTLINER > BLENDER FILE", "OVERLAY STATISTICS")


def typo(t):
    return t.replace("'", "’")


def espace(d, xy, texte, f, teinte, tracking):
    x, y = xy
    for c in texte:
        d.text((x, y), c, font=f, fill=teinte)
        x += d.textlength(c, font=f) + tracking
    return x - tracking


def principal():
    fiche = os.path.join(TRAVAIL, "zones.json")
    chemins = [os.path.join(IMAGES, n) for n, _ in PANNEAUX]
    if not os.path.exists(fiche) or any(not os.path.exists(c)
                                        for c in chemins):
        raise SystemExit(
            "captures absentes : lancez d'abord\n"
            "  sh article-blender-astuces/blender-gui/capturer-anime.sh"
            " setup-materiaux.py materiaux")

    with open(fiche, encoding="utf-8") as f:
        compte = json.load(f)
    matieres = len(compte["materiaux"])
    objets = compte["objets"]
    orphelins = len(compte["orphelins"])
    if matieres <= objets:
        raise SystemExit("%d matériaux pour %d objets : la figure n'a plus "
                         "rien à montrer" % (matieres, objets))
    if matieres - objets != orphelins:
        raise SystemExit("%d matériaux, %d objets, %d orphelins : les comptes "
                         "ne tombent pas juste"
                         % (matieres, objets, orphelins))

    C.verifier()

    vues = [Image.open(c).convert("RGB").crop(
        (DECOUPES[i][0], DECOUPES[i][1],
         DECOUPES[i][0] + DECOUPES[i][2], DECOUPES[i][1] + DECOUPES[i][3]))
        for c, (_, i) in zip(chemins, PANNEAUX)]

    #  Une seule échelle, calculée sur la somme des largeurs.
    total = sum(v.width for v in vues)
    echelle = (L - 2 * MARGE - GOUTTIERE) / float(total)
    if echelle > 1.0:
        raise SystemExit("les captures seraient agrandies")
    reduites = [v.resize((int(round(v.width * echelle)),
                          int(round(v.height * echelle))), Image.LANCZOS)
                for v in vues]
    hauteur = max(v.height for v in reduites)

    sous = ("filtré sur les matériaux : %d noms, dont %d sans plus aucun objet"
            % (matieres, orphelins),
            "%d objets seulement, et deux cent mille faces" % objets)
    pied = (
        "Captures de Blender 5.2.1 LTS. Les %d matériaux sont de vraies "
        "copies : Blender les a numérotés lui-même, de Metal.001 à Metal.%03d."
        % (matieres, matieres - 1),
        "%d objets pour %d matériaux — %d copies ont perdu leur objet et "
        "restent en mémoire jusqu'à File > Clean Up > Purge Unused Data."
        % (objets, matieres, orphelins),
    )

    f_titre = C.police(C.POLICE_G, 16)
    f_sous = C.police(C.POLICE_R, 17)
    f_pied = C.police(C.POLICE_R, 18)

    y_titre = 56
    y_vue = y_titre + 52
    y_pied = y_vue + hauteur + 40
    H = y_pied + 16 + len(pied) * 24 + 40

    out = Image.new("RGB", (L, H), PAPIER)
    d = ImageDraw.Draw(out)

    x = MARGE
    for i, vue in enumerate(reduites):
        fin = espace(d, (x, y_titre), TITRES[i], f_titre, ENCRE, 2.2)
        #  Le premier jet ne contrôlait que le sous-titre, et les deux TITRES
        #  se sont télescopés au milieu de la figure.
        if fin > x + vue.width:
            raise SystemExit("le titre « %s » déborde de sa vignette"
                             % TITRES[i])
        if d.textlength(typo(sous[i]), font=f_sous) > vue.width:
            raise SystemExit("le sous-titre %d déborde de sa vignette"
                             % (i + 1))
        d.text((x, y_titre + 24), typo(sous[i]), font=f_sous, fill=FAIBLE)
        #  La plus courte est centrée sur la plus haute : posée en haut, elle
        #  flotterait au-dessus d'un vide.
        y = y_vue + (hauteur - vue.height) // 2
        out.paste(vue, (x, y))
        d.rectangle([x, y, x + vue.width - 1, y + vue.height - 1],
                    outline=FILET, width=1)
        x += vue.width + GOUTTIERE

    d.line([MARGE, y_pied, L - MARGE, y_pied], fill=FILET, width=1)
    for i, ligne in enumerate(pied):
        ligne = typo(ligne)
        if d.textlength(ligne, font=f_pied) > L - 2 * MARGE:
            raise SystemExit("la ligne %d du pied déborde" % (i + 1))
        d.text((MARGE, y_pied + 16 + i * 24), ligne, font=f_pied, fill=FAIBLE)

    out.save(BASE + ".webp", "WEBP", quality=C.QUALITE, method=6)
    out.save(BASE + ".png", "PNG", optimize=True)
    print()
    print("  %d matériaux, %d objets, %d orphelins  ->  figure %d × %d"
          % (matieres, objets, orphelins, L, H))
    print("  vignettes réduites à %.0f %%" % (100 * echelle))
    for e in (".webp", ".png"):
        print("  %-52s %.0f Ko" % (os.path.basename(BASE + e),
                                   os.path.getsize(BASE + e) / 1024))


if __name__ == "__main__":
    principal()
