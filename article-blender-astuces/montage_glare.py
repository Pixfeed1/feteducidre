"""
Où vit le Bloom depuis Blender 4.2 : un nœud Glare dans le compositeur.

    sh article-blender-astuces/blender-gui/capturer-anime.sh \
        setup-glare.py glare
    python3 article-blender-astuces/montage_glare.py

Produit `astuces-blender-10-glare-bloom.webp` et son PNG.

----------------------------------------------------------------------------
DEUX PANNEAUX, L'UN SOUS L'AUTRE
----------------------------------------------------------------------------
Les autres figures de l'article mettent leurs deux vignettes côte à côte. Pas
celle-ci : la chaîne de nœuds est large et basse, le menu déroulant est haut
et étroit. Réduits à la même largeur, l'un devenait illisible pour que l'autre
tienne. Empilés, chacun garde sa taille.

----------------------------------------------------------------------------
CE QUE LA CAPTURE APPREND ET QUE L'ARTICLE NE DIT PAS
----------------------------------------------------------------------------
Le montage est fait dans Blender 5.2.1 LTS, comme toutes les autres figures.
Or le compositeur a encore bougé depuis la 4.2 :

  - il n'est plus un arbre attaché à la scène mais un GROUPE DE NŒUDS ;
  - le nœud « Composite » n'existe plus, la sortie est un « Group Output » ;
  - le type du Glare n'est plus une propriété du nœud mais une entrée, au
    même titre que la taille et le seuil.

La manœuvre décrite pour la 4.2 reste juste pour la 4.2. En 5.x on branche sur
Group Output. C'est dit sous l'image, faute de quoi la figure dirait autre
chose que la légende — et un article sur les tutos périmés qui vieillit mal,
ce serait dommage.
"""

import os

from PIL import Image, ImageDraw

import charte as C

RACINE = os.path.dirname(os.path.abspath(__file__))
IMAGES = "/tmp/bl-glare/frames"
BASE = os.path.join(RACINE, "astuces-blender-10-glare-bloom")

L = 1600
MARGE = 40
INTERLIGNE = 44

PAPIER = (250, 249, 246)
ENCRE = (24, 25, 30)
FAIBLE = (140, 141, 150)
FILET = (213, 211, 204)

#  (capture, découpe x/y/largeur/hauteur). Les bornes sont relevées sur les
#  images : les nœuds occupent les lignes 424 à 1021 de la première, et
#  l'étagère d'assets commence à 1213 — on coupe entre les deux.
#
#  La seconde découpe est LARGE exprès. À 1800 pixels elle coupait l'anneau par
#  le bas ; à 2000, elle le contient en entier et, comme la vignette fait de
#  toute façon 1520 de large dans la page, l'élargir la raccourcit.
PANNEAUX = (
    ("01.png", (40, 400, 2020, 650),
     "ONGLET COMPOSITING",
     "Shift+A > Filter > Glare, le type réglé sur Bloom"),
    ("02.png", (0, 80, 2000, 1200),
     "MENU VIEWPORT SHADING, DANS LA VUE 3D",
     "Compositor sur Always : le bloom se voit sans rendre"),
)

PIED = (
    "Captures de Blender 5.2.1 LTS. Le nœud est bien en mode Bloom et les "
    "deux liaisons sont valides : le script de scène le vérifie",
    "avant la photo. Depuis la 5.0, le compositeur est un groupe de nœuds et "
    "la sortie s’appelle Group Output, non plus Composite.",
)


def typo(t):
    return t.replace("'", "’")


def espace(d, xy, texte, f, teinte, tracking):
    x, y = xy
    for c in texte:
        d.text((x, y), c, font=f, fill=teinte)
        x += d.textlength(c, font=f) + tracking
    return x - tracking


def principal():
    chemins = [os.path.join(IMAGES, n) for n, _, _, _ in PANNEAUX]
    if any(not os.path.exists(c) for c in chemins):
        raise SystemExit(
            "captures absentes : lancez d'abord\n"
            "  sh article-blender-astuces/blender-gui/capturer-anime.sh"
            " setup-glare.py glare")

    C.verifier()

    largeur = L - 2 * MARGE
    vues = []
    for chemin, (x, y, w, h) in zip(chemins, [p[1] for p in PANNEAUX]):
        brute = Image.open(chemin).convert("RGB")
        if x + w > brute.width or y + h > brute.height:
            raise SystemExit("la découpe sort de la capture %s"
                             % os.path.basename(chemin))
        if w < largeur:
            raise SystemExit("la découpe de %s serait agrandie : %d px pour "
                             "%d" % (os.path.basename(chemin), w, largeur))
        coupe = brute.crop((x, y, x + w, y + h))
        vues.append(coupe.resize((largeur, int(round(h * largeur / float(w)))),
                                 Image.LANCZOS))

    f_titre = C.police(C.POLICE_G, 16)
    f_sous = C.police(C.POLICE_R, 17)
    f_pied = C.police(C.POLICE_R, 18)

    #  On calcule d'abord la hauteur totale, puis on dessine : le pied doit
    #  savoir où il tombe.
    y = 56
    places = []
    for vue in vues:
        places.append((y, y + 52, vue))
        y += 52 + vue.height + INTERLIGNE
    y_pied = y - INTERLIGNE + 40
    H = y_pied + 16 + len(PIED) * 24 + 40

    out = Image.new("RGB", (L, H), PAPIER)
    d = ImageDraw.Draw(out)

    for (y_titre, y_vue, vue), (_, _, titre, sous) in zip(places, PANNEAUX):
        fin = espace(d, (MARGE, y_titre), titre, f_titre, ENCRE, 2.2)
        if fin > L - MARGE:
            raise SystemExit("le titre « %s » déborde" % titre)
        if d.textlength(typo(sous), font=f_sous) > largeur:
            raise SystemExit("le sous-titre « %s » déborde" % sous)
        d.text((MARGE, y_titre + 24), typo(sous), font=f_sous, fill=FAIBLE)
        out.paste(vue, (MARGE, y_vue))
        bas = y_vue + vue.height - 1
        d.rectangle([MARGE, y_vue, MARGE + largeur - 1, bas], outline=FILET,
                    width=1)

    d.line([MARGE, y_pied, L - MARGE, y_pied], fill=FILET, width=1)
    for i, ligne in enumerate(PIED):
        ligne = typo(ligne)
        if d.textlength(ligne, font=f_pied) > L - 2 * MARGE:
            raise SystemExit("la ligne %d du pied déborde" % (i + 1))
        d.text((MARGE, y_pied + 16 + i * 24), ligne, font=f_pied, fill=FAIBLE)

    out.save(BASE + ".webp", "WEBP", quality=C.QUALITE, method=6)
    out.save(BASE + ".png", "PNG", optimize=True)
    print()
    print("  vignettes %s  ->  figure %d × %d"
          % (" et ".join("%d × %d" % v.size for v in vues), L, H))
    for e in (".webp", ".png"):
        print("  %-52s %.0f Ko" % (os.path.basename(BASE + e),
                                   os.path.getsize(BASE + e) / 1024))


if __name__ == "__main__":
    principal()
