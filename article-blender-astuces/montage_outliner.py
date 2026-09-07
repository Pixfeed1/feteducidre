"""
La figure de l'Outliner : les colonnes de restriction, et où on les active.

    python3 article-blender-astuces/montage_outliner.py

Produit `astuces-blender-03-outliner-icone-rendu.webp` et son équivalent PNG.

----------------------------------------------------------------------------
CE SONT DE VRAIES CAPTURES DE BLENDER 5.2.1
----------------------------------------------------------------------------
Pas une reconstitution. Blender 5.2.1 LTS tourne pour de bon, avec sa fenêtre,
sur un écran X virtuel. La chaîne est dans `blender-gui/`, et elle a demandé
trois obstacles de moins qu'il n'y paraît :

  - le module `bpy` du dépôt n'a pas d'interface : il fallait un vrai binaire.
    Les serveurs de Blender sont bloqués ici, mais l'image Docker
    `linuxserver/blender` passe par le miroir, et elle embarque la 5.2.1 —
    exactement la version que l'article annonce ;
  - `bpy.ops.screen.screenshot()` rend une image entièrement noire : elle
    relit le tampon avant, que le GL logiciel ne remplit pas. On capture donc
    l'écran X par en dessous, avec `xwd`, et on décode le format à la main
    dans `xwd.py` faute d'ImageMagick ;
  - l'écran d'accueil de Blender se pose en plein milieu de la fenêtre. On
    ouvre donc un fichier `.blend` préparé d'avance : Blender ne montre pas
    l'accueil quand on lui donne un fichier.

L'interface est dessinée à `ui_scale = 2.0` sur un écran 3840 × 2160. La
colonne de droite fait alors 681 pixels réels pour une largeur d'Outliner
normale : la capture est nette sans avoir à l'agrandir ensuite.

----------------------------------------------------------------------------
DEUX PANNEAUX, PARCE QUE LE MENU CACHE L'ARBRE
----------------------------------------------------------------------------
Le brief demandait une seule image, avec le menu de filtres déroulé ET l'icône
caméra entourée. Ça ne tient pas : l'Outliner est collé au bord droit de
l'écran, donc le menu s'ouvre par-dessus l'arborescence et masque précisément
les lignes qu'il faut montrer. Vérifié en capturant les deux ensemble.

D'où deux panneaux côte à côte, tous deux à leur taille réelle : à gauche
l'état qu'on veut faire reconnaître — la caméra du Cube éteinte —, à droite
l'endroit où l'on active ces colonnes.

----------------------------------------------------------------------------
LE REPÈRE ROUGE
----------------------------------------------------------------------------
Une ellipse, sur la caméra de la ligne Cube, et rien d'autre. Pas de flèche,
pas de halo : sur une capture d'interface, chaque ajout est un élément de plus
que le lecteur doit distinguer de l'interface elle-même.
"""

import os

from PIL import Image, ImageDraw

import charte as C

RACINE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(RACINE, "astuces-blender-03-outliner-icone-rendu")

ARBRE = "outliner-capture-arbre-5.2.1.png"
FILTRE = "outliner-capture-filtre-5.2.1.png"

L = 1600
GOUTTIERE = 32

PAPIER = (250, 249, 246)
ENCRE = (24, 25, 30)
FAIBLE = (140, 141, 150)
FILET = (213, 211, 204)
ROUGE = (208, 52, 44)

#  La capture prend l'Outliner entier, donc un reste de la barre supérieure de
#  la fenêtre, coupée en pleine hauteur. On l'enlève — une bande de texte
#  tranchée par le milieu fait négligé.
#
#  Mais pas du même côté sur les deux panneaux : le menu de filtres commence
#  tout en haut par son titre « Restriction Toggles », et le rogner par le haut
#  le décapitait. On rogne donc l'arbre par le haut, le menu par le bas, et les
#  deux gardent la même hauteur.
HAUT = 34
DECOUPES = ((HAUT, 0), (0, HAUT))          # (haut, bas) pour chaque panneau

#  Le centre de l'icône appareil photo sur la ligne du Cube, relevé sur la
#  capture avant découpe. Les trois icônes de la ligne sont à 553, 595 et 637.
CIBLE = (637, 231 - HAUT)
RAYON = (23, 21)

TITRES = ("L'ÉTAT QUI PROVOQUE LE BUG", "OÙ ON AFFICHE CES COLONNES")
SOUS = ("la caméra du Cube est éteinte : il ne partira pas au rendu",
        "menu Filtre, rangée Restriction Toggles")

PIED = (
    "Captures de Blender 5.2.1 LTS, l'interface dessinée au double pour la "
    "lisibilité. Les deux panneaux sont à leur taille réelle.",
    "Le menu de filtres s'ouvre par-dessus l'arborescence : il ne peut pas "
    "figurer sur la même vue qu'elle.",
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
    chemins = [os.path.join(RACINE, n) for n in (ARBRE, FILTRE)]
    manquants = [os.path.basename(c) for c in chemins if not os.path.exists(c)]
    if manquants:
        raise SystemExit("captures absentes : %s" % ", ".join(manquants))

    C.verifier()
    if C.contraste(ROUGE, (30, 31, 36)) < 3.0:
        raise SystemExit("le repère rouge ne ressort pas sur le fond sombre "
                         "de Blender")

    vues = [Image.open(c).convert("RGB") for c in chemins]
    if len({v.size for v in vues}) != 1:
        raise SystemExit("les deux captures n'ont pas la même taille : %s"
                         % [v.size for v in vues])
    vues = [v.crop((0, hb[0], v.width, v.height - hb[1]))
            for v, hb in zip(vues, DECOUPES)]
    if len({v.size for v in vues}) != 1:
        raise SystemExit("les deux captures n'ont pas la même taille : %s"
                         % [v.size for v in vues])
    vl, vh = vues[0].size

    #  LE REPÈRE, dessiné sur une copie : la capture d'origine reste intacte
    #  dans le dépôt, et on peut la ré-annoter autrement plus tard.
    arbre = vues[0].copy()
    da = ImageDraw.Draw(arbre)
    cx, cy = CIBLE
    rx, ry = RAYON
    if not (0 < cx - rx and cx + rx < vl and 0 < cy - ry and cy + ry < vh):
        raise SystemExit("le repère sort de la capture")
    da.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=ROUGE, width=3)
    vues[0] = arbre

    marge = (L - 2 * vl - GOUTTIERE) // 2
    if marge < 40:
        raise SystemExit("les deux captures ne tiennent pas dans %d px" % L)

    f_titre = C.police(C.POLICE_G, 16)
    f_sous = C.police(C.POLICE_R, 17)
    f_pied = C.police(C.POLICE_R, 18)

    y_titre = 56
    y_vue = y_titre + 52
    y_pied = y_vue + vh + 40
    H = y_pied + 16 + len(PIED) * 24 + 40

    out = Image.new("RGB", (L, H), PAPIER)
    d = ImageDraw.Draw(out)

    for i, vue in enumerate(vues):
        x = marge + i * (vl + GOUTTIERE)
        espace(d, (x, y_titre), TITRES[i], f_titre, ENCRE, 2.2)
        d.text((x, y_titre + 24), typo(SOUS[i]), font=f_sous, fill=FAIBLE)
        if d.textlength(typo(SOUS[i]), font=f_sous) > vl:
            raise SystemExit("le sous-titre %d déborde de sa vignette" % (i + 1))
        out.paste(vue, (x, y_vue))
        d.rectangle([x, y_vue, x + vl - 1, y_vue + vh - 1], outline=FILET,
                    width=1)

    d.line([marge, y_pied, L - marge, y_pied], fill=FILET, width=1)
    for i, ligne in enumerate(PIED):
        ligne = typo(ligne)
        if d.textlength(ligne, font=f_pied) > L - 2 * marge:
            raise SystemExit("la ligne %d du pied déborde" % (i + 1))
        d.text((marge, y_pied + 16 + i * 24), ligne, font=f_pied, fill=FAIBLE)

    out.save(BASE + ".webp", "WEBP", quality=C.QUALITE, method=6)
    out.save(BASE + ".png", "PNG", optimize=True)
    print()
    print("  captures %d × %d  ->  figure %d × %d" % (vl, vh, L, H))
    for e in (".webp", ".png"):
        print("  %-52s %.0f Ko" % (os.path.basename(BASE + e),
                                   os.path.getsize(BASE + e) / 1024))


if __name__ == "__main__":
    principal()
