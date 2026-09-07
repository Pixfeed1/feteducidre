"""
La planche des quatre symptômes.

    python3 article-blender-astuces/symptomes.py          (les rendus)
    python3 article-blender-astuces/montage_symptomes.py

Produit `astuces-blender-00-quatre-symptomes.webp` et son équivalent PNG.

----------------------------------------------------------------------------
PAS DE SURÉCHANTILLONNAGE ICI, ET C'EST VOLONTAIRE
----------------------------------------------------------------------------
Les autres figures du dépôt sont dessinées à trois fois la taille puis
réduites, parce que PIL ne lisse pas les formes. Ici il n'y a aucune forme à
lisser : des rectangles droits et du texte, que PIL rend déjà proprement.

Et surtout, la planche est faite de PHOTOGRAPHIES. Les agrandir de trois fois
pour les réduire ensuite leur ferait traverser deux rééchantillonnages au lieu
d'un seul, et un rendu Blender ne gagne rien à ce voyage.

----------------------------------------------------------------------------
LE GRAIN
----------------------------------------------------------------------------
Un bruit monochrome de ± 5 niveaux, tiré avec une graine fixe pour que la
figure soit identique à chaque exécution. Il fait deux choses : il raccorde
les quatre rendus, qui n'ont pas le même grain de calcul, et il enlève au
montage son côté trop propre.

Appliqué en dernier, sur toute l'image, texte compris — un grain qui s'arrête
au bord des vignettes se voit immédiatement.
"""

import os

from PIL import Image, ImageDraw
import numpy as np

import charte as C

RACINE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(RACINE, "astuces-blender-00-quatre-symptomes")

L = 1600
MARGE = 56
GOUTTIERE = 28
BANDE = 68                      # le bandeau de légende, en pied de vignette

PAPIER = (250, 249, 246)
ENCRE = (24, 25, 30)
GRIS = (100, 102, 112)
FAIBLE = (140, 141, 150)
FILET = (213, 211, 204)
SUR_ENCRE = (243, 241, 235)
DISCRET = (172, 174, 182)

SERIF_G = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"

VIGNETTES = (
    ("symptome-rose.png", "TEXTURE ROSE",
     "Le fichier image est introuvable."),
    ("symptome-objet-noir.png", "OBJET NOIR",
     "Metallic à 1, et rien à refléter."),
    ("symptome-sphere-cabossee.png", "SPHÈRE CABOSSÉE",
     "Un maillage irrégulier, révélé par Shade Smooth."),
    ("symptome-rendu-noir.png", "RENDU NOIR",
     "Aucune lampe dans la scène."),
)

PIED = (
    "Quatre scènes montées et rendues pour l'article : chaque symptôme vient "
    "de sa vraie cause, pas d'un aplat de couleur.",
    "Blender 4.5 LTS, moteur EEVEE Next. Les causes sont identiques en 5.x.",
)


def typo(t):
    """L'apostrophe courbe : celle des livres, pas celle des claviers."""
    return t.replace("'", "\u2019")


def espace(d, xy, texte, f, teinte, tracking):
    """Des capitales lettre à lettre, avec de l'air entre elles."""
    x, y = xy
    for c in texte:
        d.text((x, y), c, font=f, fill=teinte)
        x += d.textlength(c, font=f) + tracking
    return x - tracking


def grain(im, amplitude=5.0, graine=7):
    """
    Un bruit monochrome, identique à chaque exécution.

    Monochrome et non par canal : un bruit tiré séparément sur le rouge, le
    vert et le bleu colore les pixels, ce qui ne ressemble à aucun grain
    photographique.
    """
    rng = np.random.default_rng(graine)
    a = np.asarray(im, dtype=float)
    bruit = rng.normal(0.0, amplitude, a.shape[:2])[..., None]
    return Image.fromarray((a + bruit).clip(0, 255).astype("uint8"))


def principal():
    manquants = [n for n, _, _ in VIGNETTES
                 if not os.path.exists(os.path.join(RACINE, n))]
    if manquants:
        raise SystemExit(
            "rendus absents : %s\n        lancez d'abord "
            "`python3 article-blender-astuces/symptomes.py`"
            % ", ".join(manquants))

    C.verifier()

    #  Les quatre rendus ont la même définition ; on le vérifie plutôt que de
    #  le supposer, sinon une vignette se retrouve à une autre échelle que ses
    #  voisines et ça ne se voit qu'à la relecture.
    tailles = {Image.open(os.path.join(RACINE, n)).size
               for n, _, _ in VIGNETTES}
    if len(tailles) != 1:
        raise SystemExit("les rendus n'ont pas tous la même taille : %s"
                         % tailles)
    rl, rh = tailles.pop()

    col = (L - 2 * MARGE - GOUTTIERE) // 2
    vh = int(round(col * rh / rl))

    f_titre = C.police(C.POLICE_G, 17)
    f_cause = C.police(C.POLICE_R, 16)
    f_pied = C.police(C.POLICE_R, 18)

    y_grille = MARGE
    H = y_grille + 2 * vh + GOUTTIERE + 46 + len(PIED) * 24 + MARGE

    out = Image.new("RGB", (L, H), PAPIER)
    d = ImageDraw.Draw(out)

    for i, (fichier, titre, cause) in enumerate(VIGNETTES):
        x0 = MARGE + (i % 2) * (col + GOUTTIERE)
        y0 = y_grille + (i // 2) * (vh + GOUTTIERE)

        vign = Image.open(os.path.join(RACINE, fichier)).convert("RGB")
        out.paste(vign.resize((col, vh), Image.LANCZOS), (x0, y0))

        #  Le bandeau est POSÉ SUR la vignette, pas en dessous : quatre
        #  légendes dans la marge ajouteraient trois cents pixels de hauteur
        #  pour ne rien dire de plus.
        d.rectangle([x0, y0 + vh - BANDE, x0 + col, y0 + vh], fill=ENCRE)
        espace(d, (x0 + 22, y0 + vh - BANDE + 14), titre, f_titre,
               SUR_ENCRE, 2.2)
        d.text((x0 + 22, y0 + vh - BANDE + 40), typo(cause), font=f_cause,
               fill=DISCRET)
        if d.textlength(typo(cause), font=f_cause) > col - 44:
            raise SystemExit("la légende « %s » déborde de sa vignette"
                             % cause)
        d.rectangle([x0, y0, x0 + col - 1, y0 + vh - 1], outline=FILET,
                    width=1)

    y = y_grille + 2 * vh + GOUTTIERE + 24
    d.line([MARGE, y, L - MARGE, y], fill=FILET, width=1)
    for i, ligne in enumerate(PIED):
        ligne = typo(ligne)
        if d.textlength(ligne, font=f_pied) > L - 2 * MARGE:
            raise SystemExit("la ligne %d du pied déborde" % (i + 1))
        d.text((MARGE, y + 16 + i * 24), ligne, font=f_pied, fill=FAIBLE)

    out = grain(out)
    out.save(BASE + ".webp", "WEBP", quality=C.QUALITE, method=6)
    #  L'APERÇU EST UN JPEG, PAS UN PNG, contrairement aux autres figures. Le
    #  PNG est sans perte : le grain, qui est du bruit par construction, ne se
    #  compresse pas et le fichier montait à 2,7 Mo. Sur une planche
    #  photographique le JPEG est le bon format, et il ouvre partout.
    out.save(BASE + ".jpg", "JPEG", quality=92, optimize=True,
             progressive=True)
    print()
    print("  vignettes %d × %d  ->  planche %d × %d" % (rl, rh, L, H))
    for e in (".webp", ".jpg"):
        print("  %-48s %.0f Ko" % (os.path.basename(BASE + e),
                                   os.path.getsize(BASE + e) / 1024))


if __name__ == "__main__":
    principal()
