"""
IMAGE 6 de l'article — le montage autour de la capture d'écran.

    python3 article/montage_placement.py

Produit `article/placer-irradiance-volume-blender.webp` à partir de
`placer-volume-capture-4.2.3.png`, la capture prise dans Blender 4.2.3 LTS
par le script `placer_volume.py`.

----------------------------------------------------------------------------
CE QU'ON AJOUTE À LA CAPTURE, ET CE QU'ON N'Y TOUCHE PAS
----------------------------------------------------------------------------
La capture est une VRAIE capture. Aucun pixel de l'interface n'est redessiné,
recoloré ni déplacé : ce serait une reconstruction, et une reconstruction ne
prouve rien de ce que fait le logiciel.

On ajoute seulement, AUTOUR d'elle : un cadre blanc qui désigne une zone, un
agrandissement de cette zone, et des chiffres. Le pied de l'image le dit, pour
que personne n'ait à le deviner.

L'agrandissement n'est pas décoratif. Le sujet est un dépassement de 18 cm sur
une pièce de 7 m : à la largeur d'une page, c'est deux pixels. Sans loupe, la
légende affirme quelque chose que l'image ne montre pas.

----------------------------------------------------------------------------
POURQUOI LE COIN BAS-GAUCHE ET PAS LE HAUT
----------------------------------------------------------------------------
En haut, le volume passe loin au-dessus des murs — mais le plafond est masqué
pour qu'on voie l'intérieur, donc il n'y a plus rien à quoi comparer. Un
lecteur y verrait une boîte trop grande, pas un débordement.

En bas à gauche, les trois choses sont dans le même regard : l'arête du mur,
l'épaisseur de la dalle de sol, et l'arête du volume qui passe DEHORS et
DESSOUS. C'est là qu'on peut vérifier, donc c'est là qu'on regarde.
"""

import os

from PIL import Image, ImageDraw, ImageFont

RACINE = os.path.dirname(os.path.abspath(__file__))
CAPTURE = os.path.join(RACINE, "placer-volume-capture-4.2.3.png")
SORTIE = os.path.join(RACINE, "placer-irradiance-volume-blender.webp")

#  La zone de détail, en pixels de la capture d'origine. Mesurée sur l'image,
#  pas choisie à vue : c'est le seul endroit où l'arête du mur, l'épaisseur du
#  sol et l'arête du volume tiennent dans le même cadre.
DETAIL = (140, 495, 410, 700)

LARGEUR = 1600
LOUPE_L = 470
MARGE = 34
BANDE_TITRE = 74

ENCRE = (13, 13, 17)
BLANC = (238, 238, 243)
GRIS = (138, 138, 150)
TEAL = (72, 224, 184)
ORANGE = (232, 146, 62)

POLICE_G = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
POLICE_R = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
QUALITE = 92

VERSION = "Blender 4.2.3 LTS · EEVEE Next"
AVEU = ("capture d'écran non retouchée — le cadre blanc, l'agrandissement "
        "et les chiffres sont les seuls ajouts")

#  Les cotes, reprises de `placer_volume.py`. Écrites ici en clair parce
#  qu'une figure doit pouvoir être relue sans ouvrir le script qui l'a faite.
DEBORD_INT, DEBORD_EXT, CLOISON = 18, 6, 12          # centimètres
RES = (11, 12, 6)


def nb(gabarit, valeur):
    return (gabarit % valeur).replace(".", ",")


def police(chemin, taille):
    try:
        return ImageFont.truetype(chemin, taille)
    except OSError:
        return ImageFont.load_default()


def principal():
    if not os.path.exists(CAPTURE):
        raise SystemExit(
            "capture absente : %s\n        lancez `blender --python "
            "article/placer_volume.py` et deposez l'image ici" % CAPTURE)

    cap = Image.open(CAPTURE).convert("RGB")
    dx0, dy0, dx1, dy1 = DETAIL
    if not (0 <= dx0 < dx1 <= cap.width and 0 <= dy0 < dy1 <= cap.height):
        raise SystemExit("la zone de detail sort de la capture : la capture "
                         "n'a pas les dimensions attendues (%d x %d)"
                         % cap.size)

    k = LARGEUR / float(cap.width)
    hv = int(round(cap.height * k))
    lh = int(round(LOUPE_L * (dy1 - dy0) / float(dx1 - dx0)))

    #  Le facteur d'agrandissement se compte par rapport à la VIGNETTE, pas au
    #  fichier d'origine : c'est la vignette que le lecteur a sous les yeux.
    facteur = LOUPE_L / ((dx1 - dx0) * k)
    if facteur < 1.0:
        raise SystemExit("la loupe reduit au lieu d'agrandir (%.2f) : "
                         "augmentez LOUPE_L" % facteur)

    L = MARGE * 2 + LARGEUR
    #  Deux lignes de pied, pas une. Sur une seule, la mention de version et
    #  la note sur les parois masquées se chevauchaient au milieu : deux
    #  textes alignés l'un à gauche l'autre à droite ne se croisent pas tant
    #  qu'on ne mesure pas leur somme, et je ne l'avais pas mesurée.
    H = MARGE + BANDE_TITRE + hv + 30 + lh + 30 + 76 + MARGE
    out = Image.new("RGB", (L, H), ENCRE)
    d = ImageDraw.Draw(out, "RGBA")

    f_titre = police(POLICE_G, 32)
    f_sous = police(POLICE_G, 24)
    f_legende = police(POLICE_R, 24)
    f_petit = police(POLICE_R, 20)

    d.rectangle([MARGE, MARGE + 14, MARGE + 10, MARGE + 44], fill=TEAL)
    d.text((MARGE + 24, MARGE + 10),
           "LE VOLUME DÉBORDE LES MURS — C'EST LE RÉGLAGE, PAS UNE ERREUR",
           font=f_titre, fill=BLANC)

    y_img = MARGE + BANDE_TITRE
    out.paste(cap.resize((LARGEUR, hv), Image.LANCZOS), (MARGE, y_img))

    #  Le cadre qui désigne la zone agrandie.
    b = [MARGE + dx0 * k, y_img + dy0 * k, MARGE + dx1 * k, y_img + dy1 * k]
    d.rectangle(b, outline=(255, 255, 255, 200), width=2)

    #  LA LOUPE.
    lx, ly = MARGE, y_img + hv + 30
    out.paste(cap.crop(DETAIL).resize((LOUPE_L, lh), Image.LANCZOS), (lx, ly))
    d.rectangle([lx - 1, ly - 1, lx + LOUPE_L, ly + lh],
                outline=(255, 255, 255, 130), width=2)
    #  Un trait qui relie le cadre à la loupe, sinon le lecteur cherche.
    d.line([b[0], b[3], lx + 6, ly - 6], fill=(255, 255, 255, 70), width=1)

    tx = lx + LOUPE_L + 34
    d.text((tx, ly + 2), nb("LE DÉPASSEMENT, AGRANDI %.1f FOIS", facteur),
           font=f_sous, fill=BLANC)

    lignes = [
        ("L'arête orange du volume passe DEHORS et DESSOUS : à gauche du mur,",
         GRIS),
        ("sous l'épaisseur de la dalle. Chaque paroi est donc prise dedans.",
         GRIS),
        ("", GRIS),
        ("%d cm au-delà de la face intérieure. Les cloisons faisant %d cm, le"
         % (DEBORD_INT, CLOISON), GRIS),
        ("volume ressort encore de %d cm derrière leur face extérieure."
         % DEBORD_EXT, GRIS),
        ("", GRIS),
        ("Un mur laissé hors du volume ne reçoit aucune irradiance et rend",
         GRIS),
        ("noir. Sur cette pièce : moyenne d'image 86,5 avec un volume rentré",
         GRIS),
        ("de 45 cm, 129,9 une fois le volume ressorti derrière les parois.",
         GRIS),
    ]
    for i, (ligne, coul) in enumerate(lignes):
        d.text((tx, ly + 44 + i * 29), ligne, font=f_legende, fill=coul)

    #  Les points orange visibles dans le volume SONT les échantillons : le
    #  dire, sinon on les prend pour une décoration de gizmo.
    res = "%d × %d × %d = %d échantillons" % (*RES, RES[0] * RES[1] * RES[2])
    d.text((tx, ly + lh - 30), "Résolution  " + res, font=f_sous,
           fill=ORANGE)

    yf = ly + lh + 30
    d.line([MARGE, yf, L - MARGE, yf], fill=(46, 46, 56), width=1)
    d.text((MARGE, yf + 14), VERSION + " · " + AVEU, font=f_petit,
           fill=(104, 104, 116))
    d.text((MARGE, yf + 42),
           "plafond, mur avant et mur droit masqués pour voir l'intérieur — "
           "ils apparaissent grisés dans l'outliner",
           font=f_petit, fill=(104, 104, 116))

    out.save(SORTIE, "WEBP", quality=QUALITE, method=6)
    print()
    print("  capture  %d × %d" % cap.size)
    print("  figure   %d × %d" % out.size)
    print("  zone de detail %s  agrandie %.2f fois" % (str(DETAIL), facteur))
    print("  %s  (%.0f Ko)"
          % (os.path.basename(SORTIE), os.path.getsize(SORTIE) / 1024))


if __name__ == "__main__":
    principal()
