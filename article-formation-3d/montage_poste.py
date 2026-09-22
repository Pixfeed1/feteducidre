"""
Le rendu du poste de travail, vérifié puis enregistré aux deux formats.

    sh article-formation-3d/blender-gui/capturer-dalle.sh
    sh article-formation-3d/rendre-poste.sh
    python3 article-formation-3d/montage_poste.py

Produit `formation-3d-poste-travail.webp` et son PNG.

----------------------------------------------------------------------------
PAS DE TITRE NI DE PIED SUR CETTE IMAGE
----------------------------------------------------------------------------
C'est l'image à la une de l'article, pas une figure. Elle est vue en vignette
dans les listes, en bandeau en tête de page, et reprise par les réseaux qui
la recadrent. Tout texte incrusté y serait illisible une fois sur deux et
coupé l'autre fois. Le crédit et la légende sont posés par le site, autour de
l'image, là où ils restent sélectionnables.

----------------------------------------------------------------------------
CE QUE CONTRÔLE CE FICHIER
----------------------------------------------------------------------------
Un rendu peut échouer sans planter : Cycles écrit alors une image noire, ou
grise, ou bien la dalle reste éteinte. Ces trois pannes se ressemblent dans
un journal et ne se voient qu'à l'oeil. On les mesure donc :

  - la richesse de l'image, en nombre de couleurs distinctes ;
  - la luminance moyenne, qui doit tenir dans une plage de scène éclairée ;
  - la LUMINANCE DE LA DALLE comparée à celle du mur, puisque c'est le seul
    objet de la scène qui doit être lumineux par lui-même.
"""

import os

import numpy as np
from PIL import Image

import charte as C

RACINE = os.path.dirname(os.path.abspath(__file__))
TRAVAIL = os.environ.get("TRAVAIL", "/tmp/poste")
RENDU = os.path.join(TRAVAIL, "rendus", "poste.png")
BASE = os.path.join(RACINE, "formation-3d-poste-travail")

LARGEUR = 1600

#  La dalle, en fractions de la largeur et de la hauteur de l'image. Ces
#  quatre nombres suivent le cadrage ; s'il bouge, ils bougent.
DALLE = (0.43, 0.13, 0.80, 0.50)
#  Un coin de mur au soleil, pour la comparaison.
MUR = (0.86, 0.06, 0.98, 0.22)


def luminance(a):
    return float((a @ np.array([0.2126, 0.7152, 0.0722], np.float32)).mean())


def zone(a, boite):
    h, l = a.shape[:2]
    x0, y0, x1, y1 = boite
    return a[int(y0 * h):int(y1 * h), int(x0 * l):int(x1 * l)]


def principal():
    if not os.path.exists(RENDU):
        raise SystemExit(
            "rendu absent : lancez d'abord\n"
            "  sh article-formation-3d/blender-gui/capturer-dalle.sh\n"
            "  sh article-formation-3d/rendre-poste.sh")

    im = Image.open(RENDU).convert("RGB")
    a = np.asarray(im).astype(np.float32) / 255.0

    nuances = len(np.unique(np.asarray(im).reshape(-1, 3), axis=0))
    if nuances < 20000:
        raise SystemExit(
            "l'image ne porte que %d couleurs : le rendu a échoué" % nuances)

    moyenne = luminance(a)
    if not 0.10 < moyenne < 0.72:
        raise SystemExit(
            "luminance moyenne %.3f, hors de la plage d'une scène éclairée "
            "(0,10 à 0,72)" % moyenne)

    #  CONTRÔLE : la dalle doit être lumineuse, sinon l'écran est éteint et
    #  l'image ne montre plus un poste de travail mais un meuble.
    l_dalle = luminance(zone(a, DALLE))
    l_mur = luminance(zone(a, MUR))
    if l_dalle < 0.06:
        raise SystemExit("la dalle est à %.3f : l'écran est éteint" % l_dalle)

    sortie = im
    if im.width != LARGEUR:
        hauteur = int(round(LARGEUR * im.height / float(im.width)))
        sortie = im.resize((LARGEUR, hauteur), Image.LANCZOS)

    sortie.save(BASE + ".webp", "WEBP", quality=C.QUALITE, method=6)
    sortie.save(BASE + ".png", "PNG", optimize=True)

    print("  rendu    %d × %d, %d couleurs" % (im.width, im.height, nuances))
    print("  luminance  moyenne %.3f   dalle %.3f   mur au soleil %.3f"
          % (moyenne, l_dalle, l_mur))
    print("  sortie   %d × %d" % (sortie.width, sortie.height))
    for e in (".webp", ".png"):
        print("  %-44s %.0f Ko" % (os.path.basename(BASE + e),
                                   os.path.getsize(BASE + e) / 1024))


if __name__ == "__main__":
    principal()
