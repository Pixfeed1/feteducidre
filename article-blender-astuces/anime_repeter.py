"""
L'animation de Shift+R et F9 : refaire la même opération, puis la corriger.

    sh article-blender-astuces/blender-gui/capturer-anime.sh \
         setup-repeter.py repeter
    python3 article-blender-astuces/anime_repeter.py

Produit `astuces-blender-06-shift-r-f9.webp` — celui de l'article —, son `.gif`
de secours et sa planche `-apercu.jpg`. Le montage lui-même est dans
`anime.py`, partagé avec l'autre figure animée.

----------------------------------------------------------------------------
VINGT ET UN VRAIS ÉCRANS DE BLENDER
----------------------------------------------------------------------------
Blender 5.2.1 LTS tourne sur un écran X virtuel, la séquence lui est envoyée
frappe par frappe, et `xwd` photographie l'écran entre chaque. Rien n'est
dessiné : le panneau « Adjust Last Operation », la valeur qui passe en saisie,
le 3 tapé par-dessus le 2, tout est à l'écran au moment de la photo.

Le champ « Move X » est atteint par un ctrl+clic à des coordonnées relevées au
pixel sur une capture — la disposition d'un popup n'est pas exposée par l'API,
il n'y avait pas d'autre moyen que de la mesurer.

----------------------------------------------------------------------------
LE PIÈGE : UN CHIFFRE N'EST PAS UNE TOUCHE
----------------------------------------------------------------------------
`event_simulate(type='TWO')` ne tape pas un 2 : la saisie numérique de Blender
lit le CARACTÈRE de l'événement, pas le code de la touche. Sans `unicode='2'`,
le X passait, la contrainte d'axe s'affichait, et le déplacement restait à
zéro : les cinq copies se posaient exactement l'une sur l'autre. Un seul cube
à l'écran, et rien dans le journal pour le dire.

D'où le contrôle par ÉTENDUE plus bas. Compter les pixels modifiés n'aurait
rien vu — cinq cubes empilés en changent autant qu'un seul.

----------------------------------------------------------------------------
UN CUBE D'UN MÈTRE
----------------------------------------------------------------------------
L'article dit « décalé de 2 m », et c'est ce qui est joué. Mais le cube de
Blender fait deux mètres de côté : décalé de deux mètres il touche le
précédent, et la rangée devient une barre pleine. Le cube est donc à un mètre,
ce qui laisse un mètre de jour entre chaque copie sans toucher au chiffre.
"""

import os

import anime as A

RACINE = os.path.dirname(os.path.abspath(__file__))
IMAGES = "/tmp/bl-repeter/frames"
BASE = os.path.join(RACINE, "astuces-blender-06-shift-r-f9")

#  La coupe tombe entre le bas du panneau F9 (ligne 1150 de la capture) et la
#  barre de reprise du coin (1321) : le panneau reste entier, la barre s'en va.
BAS_COUPE = 60
LARGEUR = 1120

#  Les deux lignes qui découpent l'image réduite, relevées sur les captures :
#  la rangée de cubes occupe les lignes 274 à 372, le panneau F9 s'ouvre à
#  partir de 391. La bande 105-382 ne contient donc QUE les cubes — au-dessus
#  il y a le nom de l'objet, qui change à chaque copie, en dessous le panneau.
HAUT_TEXTE = 105
BAS_CUBES = 382

#  (durée en ms, phase). Les temps d'arrêt sont sur ce qu'il faut lire : la
#  distance tapée, la rangée finie, le panneau qui s'ouvre, le cube qui saute.
PLAN = (
    (450, 0), (300, 0),                      # 0-1   un seul cube
    (400, 1),                                # 2     Shift+D
    (350, 1),                                # 3     X : l'axe rouge
    (450, 1),                                # 4     2 : « D: 2 » s'affiche
    (500, 1),                                # 5     Entrée : deux cubes
    (350, 1),                                # 6
    (300, 2), (260, 2),                      # 7-8   Shift+R
    (300, 2), (260, 2),                      # 9-10  Shift+R
    (300, 2), (280, 2),                      # 11-12 Shift+R
    (650, 2),                                # 13    la rangée finie
    (650, 3),                                # 14    F9 : le panneau
    (380, 3),                                # 15
    (420, 3),                                # 16    le champ passe en saisie
    (480, 3),                                # 17    le 3 tapé
    (800, 3),                                # 18    le dernier cube saute
    (400, 3), (700, 3),                      # 19-20
)

RANGEE = 13              # l'image où la rangée est finie
PANNEAU = 14             # celle où le panneau vient de s'ouvrir
CORRIGE = 18             # celle où la valeur corrigée est appliquée
CLES = (0, 5, RANGEE, CORRIGE)

BANDEAUX = (
    ("AU DÉPART, UN SEUL CUBE",
     "et l’envie de le dupliquer quatre fois"),
    ("SHIFT+D, PUIS X, PUIS 2",
     "dupliquer, contraindre sur X, taper la distance"),
    ("SHIFT+R REFAIT LA MÊME OPÉRATION",
     "trois frappes, trois copies, le même écart à chaque fois"),
    ("F9 ROUVRE LE PANNEAU DE LA DERNIÈRE OPÉRATION",
     "2 m devient 3 m, et le cube suit — sans rien annuler"),
)


def principal():
    vues = A.charger(IMAGES, len(PLAN), LARGEUR, BAS_COUPE)

    #  CONTRÔLE 1 : la rangée doit s'ÉTALER. C'est la mesure qui aurait attrapé
    #  la série où le chiffre tapé n'arrivait pas et où les cinq cubes se
    #  posaient au même endroit.
    largeur = A.etendue(vues, RANGEE, depuis=HAUT_TEXTE, jusqu=BAS_CUBES)
    if largeur < 0.40:
        raise SystemExit("les copies ne s'étalent que sur %.0f %% de la "
                         "largeur : elles se superposent" % (100 * largeur))

    #  CONTRÔLE 2 : le panneau F9 doit s'être ouvert, donc changer le bas de
    #  l'image entre l'image d'avant et celle d'après. Trois pour cent
    #  suffisent à l'affirmer, et il ne faut pas en attendre plus : le fond du
    #  panneau est un gris à peine plus sombre que le sol, sous le seuil de la
    #  mesure. Seuls son texte et ses champs comptent. Sans panneau : zéro.
    ouverture = A.changement(vues, (PANNEAU,), depuis=BAS_CUBES, ref=RANGEE)
    if ouverture < 0.01:
        raise SystemExit("le bas de l'image ne change que de %.2f %% à la "
                         "frappe de F9 : le panneau ne s'est pas ouvert"
                         % (100 * ouverture))

    #  CONTRÔLE 3 : et la valeur corrigée doit déplacer un cube, donc changer
    #  la bande du haut, celle où le panneau n'est pas.
    saut = A.changement(vues, (CORRIGE,), depuis=HAUT_TEXTE, jusqu=BAS_CUBES,
                        ref=RANGEE)
    if saut < 0.003:
        raise SystemExit("la rangée ne bouge que de %.3f %% après la "
                         "correction : la valeur n'a pas été reprise"
                         % (100 * saut))

    pol = A.polices()
    images = [A.bandeau(v, BANDEAUX[phase][0], BANDEAUX[phase][1], pol)
              for v, (_, phase) in zip(vues, PLAN)]
    A.enregistrer(BASE, images, [d for d, _ in PLAN], CLES)
    print("  la rangée s’étale sur %.0f %% de la largeur" % (100 * largeur))
    print("  F9 change %.0f %% du bas, la correction %.2f %% du haut"
          % (100 * ouverture, 100 * saut))


if __name__ == "__main__":
    principal()
