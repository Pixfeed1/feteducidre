"""
La liste des formes clés faciales, telle que Blender la montre.

    sh article-daz-lipsync/blender-gui/capturer.sh
    python3 article-daz-lipsync/montage_blendshapes.py

Produit `daz-lipsync-blendshapes-blender.webp` et son PNG.

----------------------------------------------------------------------------
CE QUE CETTE FIGURE MONTRE, ET CE QU'ELLE NE MONTRE PAS
----------------------------------------------------------------------------
Le brief demandait la liste des blendshapes d'un personnage Genesis importé
dans Blender. Le panneau, la liste, les 52 noms et les valeurs sont réels :
c'est une capture d'écran de Blender 5.2.1, pas un dessin.

Le maillage, lui, n'est pas une Genesis. Je n'en ai pas, elles sont payantes
et daz3d.com est hors de la liste d'autorisation de cette machine. Le
maillage est donc Suzanne, la tête livrée avec Blender, que personne ne peut
confondre avec un personnage Daz. La figure le dit en sous-titre et en pied
plutôt que de laisser le lecteur le supposer.

Ce choix ne dilue pas le propos, il le sert. La légende de l'article dit que
les morphs de Daz deviennent, passé le pont, des blendshapes ORDINAIRES.
Les voir sur la tête de démonstration de Blender, dans le même panneau que
n'importe quel autre maillage, c'est exactement ça.

----------------------------------------------------------------------------
LES NOMS SONT CEUX D'ARKIT, ET CE N'EST PAS UN DÉTAIL
----------------------------------------------------------------------------
L'article établit que le rig facial de Genesis 9 est construit sur ARKit, la
norme d'Apple. Les 52 noms de la liste sont donc ceux qu'un lecteur retrouve
après le pont, `jawOpen`, `mouthSmileLeft`, `browInnerUp`. C'est la partie
transposable de la figure, et elle est vraie.

----------------------------------------------------------------------------
POURQUOI L'ÉDITEUR DE FORMES CLÉS ET PAS LE PANNEAU
----------------------------------------------------------------------------
`DATA_PT_shape_keys` appelle `template_list` avec `rows=5`, codé en dur. Le
panneau des propriétés ne montrera donc jamais plus de cinq noms, quelle que
soit la taille de la fenêtre. Une figure qui annonce « la liste » en
afficherait cinq sur cinquante-deux. L'éditeur de formes clés du Dope Sheet
en tient une quarantaine, et c'est là qu'une synchronisation labiale se
travaille vraiment.
"""

import os

import numpy as np
from PIL import Image

import charte as C
import dessin as D

RACINE = os.path.dirname(os.path.abspath(__file__))
TRAVAIL = os.environ.get("TRAVAIL", "/tmp/bl-blendshapes")
BASE = os.path.join(RACINE, "daz-lipsync-blendshapes-blender")

L = 1600
MARGE = 56

#  La capture fait 1900 x 2100. On garde la colonne de gauche, qui porte la
#  liste, et la colonne de droite, qui porte le panneau : le vide du milieu,
#  qui est la zone de courbes, ne dit rien.
COUPE = (0, 24, 1900, 1900)

VIOLET = (98, 44, 200)

TITRE = "APRÈS LE PONT, DES FORMES CLÉS ORDINAIRES"
SOUS = ("capture de Blender 5.2.1 ; le maillage est Suzanne, la tête livrée "
        "avec Blender, et non une figure Genesis")

PIED = (
    "Les 52 noms sont ceux d’ARKit, la norme faciale d’Apple sur laquelle "
    "le rig de Genesis 9 est construit : c’est la partie que vous "
    "retrouverez après le pont.",
    "Une figure Genesis n’a pas pu être utilisée ici, daz3d.com étant hors "
    "de la liste d’autorisation de la machine. Le panneau, la liste, les "
    "noms et les valeurs sont réels ;",
    "le personnage, lui, est celui de Blender, et c’est écrit plutôt que "
    "laissé à deviner. Une seule forme est ouverte, jawOpen à 1,000 ; "
    "toutes les autres sont à 0,000.",
)


def principal():
    rendu = os.path.join(TRAVAIL, "plein.png")
    if not os.path.exists(rendu):
        raise SystemExit(
            "capture absente : lancez d'abord\n"
            "  sh article-daz-lipsync/blender-gui/capturer.sh")

    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5),
               ("violet", VIOLET, 4.5))

    brut = Image.open(rendu).convert("RGB")
    a = np.asarray(brut)

    #  CONTRÔLE : une capture ratée sort en aplat. Blender dessine des
    #  dizaines de nuances ; un écran vide n'en a qu'une poignée.
    nuances = len(np.unique(a.reshape(-1, 3), axis=0))
    if nuances < 400:
        raise SystemExit("la capture ne porte que %d couleurs : écran vide"
                         % nuances)
    #  CONTRÔLE : l'interface de Blender est sombre. Une capture claire
    #  voudrait dire qu'on a photographié autre chose.
    if a.mean() > 120:
        raise SystemExit("la capture est trop claire pour être Blender")

    x0, y0, x1, y1 = COUPE
    vue = brut.crop((x0, y0, min(x1, brut.width), min(y1, brut.height)))
    largeur = L - 2 * MARGE
    if largeur > vue.width:
        raise SystemExit("la capture serait agrandie")
    haut = int(round(largeur * vue.height / float(vue.width)))
    vue = vue.resize((largeur, haut), Image.LANCZOS)

    y_vue = 150
    y_pied = y_vue + haut + 46
    H = y_pied + 18 + len(PIED) * 24 + 40

    t = D.Toile(L, H)
    f_titre = t.police(C.POLICE_G, 17)
    f_sous = t.police(C.POLICE_R, 17)
    f_pied = t.police(C.POLICE_R, 16)

    t.espace((MARGE, 52), TITRE, f_titre, D.ENCRE, 2.2)
    sous = D.typo(SOUS)
    if t.mesure(sous, f_sous) > L - 2 * MARGE:
        raise SystemExit("le sous-titre déborde")
    t.texte((MARGE, 78), sous, f_sous, D.FAIBLE)

    t.im.paste(vue.resize((vue.width * t.e, vue.height * t.e), Image.LANCZOS),
               (MARGE * t.e, y_vue * t.e))
    t.rrect([MARGE, y_vue, MARGE + vue.width - 1, y_vue + vue.height - 1], 0,
            contour=D.FILET, epaisseur=2)

    t.ligne([MARGE, y_pied, L - MARGE, y_pied], D.FILET, 2)
    for i, ligne in enumerate(PIED):
        ligne = D.typo(ligne)
        if t.mesure(ligne, f_pied) > L - 2 * MARGE:
            raise SystemExit("la ligne %d du pied déborde" % (i + 1))
        t.texte((MARGE, y_pied + 18 + i * 24), ligne, f_pied, D.FAIBLE)

    D.enregistrer(t.final(L, H), BASE, L, H)
    print("  capture %d × %d, %d nuances, luminance moyenne %.0f"
          % (brut.width, brut.height, nuances, a.mean()))


if __name__ == "__main__":
    principal()
