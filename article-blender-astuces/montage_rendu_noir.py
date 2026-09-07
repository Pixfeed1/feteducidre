"""
Les deux causes de rendu noir qui n'ont rien à voir avec la lumière.

    python3 article-blender-astuces/montage_rendu_noir.py

Produit `astuces-blender-04-rendu-noir-sequencer.webp` et son équivalent PNG.

----------------------------------------------------------------------------
DEUX VRAIES CAPTURES DE BLENDER 5.2.1
----------------------------------------------------------------------------
Mêmes moyens que la figure de l'Outliner : Blender 5.2.1 LTS tourne avec sa
fenêtre sur un écran X virtuel, et `xwd` photographie l'écran. Les scripts
sont dans `blender-gui/`.

Deux difficultés propres à celle-ci, et ce qu'elles ont appris.

LE MESSAGE D'ERREUR NE S'OBTIENT PAS EN APPELANT L'OPÉRATEUR. Trois tentatives
avec `bpy.ops.render.render('INVOKE_DEFAULT')`, avec et sans substitution de
contexte : rien dans la barre d'état, rien dans l'éditeur Info. Un rapport
n'existe que s'il passe par le gestionnaire de fenêtres. Il a fallu simuler
une VRAIE frappe de F12, avec `window.event_simulate()` et l'option
`--enable-event-simulate` que Blender utilise pour tester sa propre interface.

ET LES DEUX CHEMINS NE DISENT PAS LA MÊME CHOSE. Appelé depuis Python,
l'opérateur lève « Cannot render, no camera ». Déclenché au clavier, il écrit
« No camera found in scene "Scene" ». J'avais d'abord relevé le premier
message et cru l'article fautif : c'est l'article qui avait raison, et ma
méthode de mesure qui regardait le mauvais chemin de code.

----------------------------------------------------------------------------
LE PANNEAU POST PROCESSING S'OUVRE PAR LA RECHERCHE
----------------------------------------------------------------------------
L'état plié d'un panneau n'est pas exposé par l'API : impossible de déplier
« Post Processing » depuis un script. Mais le champ de recherche des
Properties déplie tout panneau qui contient le terme cherché. C'est ce qui est
fait ici — et accessoirement, c'est aussi la façon la plus rapide de trouver
ce réglage quand on le cherche à la main.
"""

import os

from PIL import Image, ImageDraw

import charte as C

RACINE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(RACINE, "astuces-blender-04-rendu-noir-sequencer")

L = 1600
GOUTTIERE = 40

PAPIER = (250, 249, 246)
ENCRE = (24, 25, 30)
FAIBLE = (140, 141, 150)
FILET = (213, 211, 204)

PANNEAUX = (
    ("rendu-noir-capture-barre-5.2.1.png",
     "CE QUE BLENDER ÉCRIT, EN BAS, APRÈS F12",
     "pas de caméra active dans la scène"),
    ("rendu-noir-capture-post-5.2.1.png",
     "L'AUTRE CAUSE, QUE PERSONNE NE CHERCHE",
     "Output Properties, Post Processing, la case Sequencer"),
)

PIED = (
    "Captures de Blender 5.2.1 LTS. Le message vient d'un vrai F12 : l'appel "
    "de l'opérateur depuis Python ne produit aucun rapport,",
    "et dit d'ailleurs autre chose — « Cannot render, no camera ». Les deux "
    "panneaux sont à leur taille réelle.",
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
    chemins = [os.path.join(RACINE, n) for n, _, _ in PANNEAUX]
    manquants = [os.path.basename(c) for c in chemins if not os.path.exists(c)]
    if manquants:
        raise SystemExit("captures absentes : %s" % ", ".join(manquants))

    C.verifier()

    vues = [Image.open(c).convert("RGB") for c in chemins]
    largeurs = [v.width for v in vues]
    hauteur = max(v.height for v in vues)

    marge = (L - sum(largeurs) - GOUTTIERE) // 2
    if marge < 40:
        raise SystemExit("les deux captures ne tiennent pas dans %d px" % L)

    f_titre = C.police(C.POLICE_G, 16)
    f_sous = C.police(C.POLICE_R, 17)
    f_pied = C.police(C.POLICE_R, 18)

    y_titre = 56
    y_bande = y_titre + 52
    y_pied = y_bande + hauteur + 40
    H = y_pied + 16 + len(PIED) * 24 + 40

    out = Image.new("RGB", (L, H), PAPIER)
    d = ImageDraw.Draw(out)

    x = marge
    for vue, (_, titre, sous) in zip(vues, PANNEAUX):
        espace(d, (x, y_titre), titre, f_titre, ENCRE, 2.2)
        if d.textlength(typo(sous), font=f_sous) > vue.width + GOUTTIERE:
            raise SystemExit("le sous-titre « %s » déborde" % sous)
        d.text((x, y_titre + 24), typo(sous), font=f_sous, fill=FAIBLE)

        #  Les deux captures n'ont pas la même hauteur — un bandeau d'état fait
        #  soixante-douze pixels, un panneau de propriétés deux cent quarante.
        #  On centre la plus courte sur la plus haute : posée en haut, elle
        #  flotterait au-dessus d'un vide.
        y = y_bande + (hauteur - vue.height) // 2
        out.paste(vue, (x, y))
        d.rectangle([x, y, x + vue.width - 1, y + vue.height - 1],
                    outline=FILET, width=1)
        x += vue.width + GOUTTIERE

    d.line([marge, y_pied, L - marge, y_pied], fill=FILET, width=1)
    for i, ligne in enumerate(PIED):
        ligne = typo(ligne)
        if d.textlength(ligne, font=f_pied) > L - 2 * marge:
            raise SystemExit("la ligne %d du pied déborde" % (i + 1))
        d.text((marge, y_pied + 16 + i * 24), ligne, font=f_pied, fill=FAIBLE)

    out.save(BASE + ".webp", "WEBP", quality=C.QUALITE, method=6)
    out.save(BASE + ".png", "PNG", optimize=True)
    print()
    print("  panneaux %s  ->  figure %d × %d"
          % (" et ".join("%d × %d" % v.size for v in vues), L, H))
    for e in (".webp", ".png"):
        print("  %-52s %.0f Ko" % (os.path.basename(BASE + e),
                                   os.path.getsize(BASE + e) / 1024))


if __name__ == "__main__":
    principal()
