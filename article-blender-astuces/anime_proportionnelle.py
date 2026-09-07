"""
L'animation de l'édition proportionnelle : le même geste, avant et après O.

    sh article-blender-astuces/blender-gui/capturer-anime.sh \
         setup-proportionnelle.py proportionnelle
    python3 article-blender-astuces/anime_proportionnelle.py

Produit `astuces-blender-05-edition-proportionnelle.webp` — celui de l'article
—, son `.gif` de secours et sa planche `-apercu.jpg`. Le montage lui-même est
dans `anime.py`, partagé avec l'autre figure animée.

Les trente-deux écrans bruts restent dans `/tmp/bl-proportionnelle/frames` et
n'entrent pas dans le dépôt : ils pèsent vingt-quatre mégaoctets, et la chaîne
de capture se rejoue en trois minutes.

----------------------------------------------------------------------------
CE SONT TRENTE-DEUX VRAIS ÉCRANS DE BLENDER
----------------------------------------------------------------------------
Aucune image n'est dessinée ni interpolée. Blender 5.2.1 LTS tourne sur un
écran X virtuel, une séquence de frappes et de mouvements lui est envoyée
étape par étape, et `xwd` photographie l'écran entre chaque. Le cercle gris de
l'édition proportionnelle n'existe QUE pendant l'opérateur modal : il fallait
photographier Blender au milieu d'un G, ce qu'aucune capture interne ne sait
faire ici.

Deux erreurs ont coûté deux séries entières, et toutes deux se voyaient à
l'oeil sur les images — c'est bien pour ça qu'il faut les regarder :

  - les préférences ne survivent pas à la fin du conteneur. Enregistrer
    « ne plus montrer l'écran d'accueil » lors d'une exécution précédente ne
    servait à rien : la photo du lion se posait au milieu de la fenêtre. Les
    deux passes tiennent maintenant dans le même `docker run` ;
  - `event_simulate` place l'événement en 0, 0 quand on ne lui donne pas de
    coordonnées, c'est-à-dire sur la barre d'état. F12 marchait quand même —
    c'est un raccourci de fenêtre — mais G et O appartiennent au clavier de la
    vue 3D et n'arrivaient nulle part. La séquence se jouait « correctement »
    sur une grille parfaitement immobile.

----------------------------------------------------------------------------
LES DURÉES SUIVENT LE PROPOS, PAS L'HORLOGE
----------------------------------------------------------------------------
Le déplacement est rapide — c'est un geste, on le lit d'un coup. Les temps
d'arrêt sont longs : au sommet de la déformation, et surtout sur la frappe du
O, qui est le seul moment où quelque chose change VRAIMENT entre les deux
démonstrations. La boucle est infinie : un lecteur qui arrive en cours de
route doit pouvoir attendre le tour suivant.
"""

import os

import anime as A

RACINE = os.path.dirname(os.path.abspath(__file__))
IMAGES = "/tmp/bl-proportionnelle/frames"
BASE = os.path.join(RACINE, "astuces-blender-05-edition-proportionnelle")

#  La hauteur de la coupe n'est pas ronde par hasard : elle place le bord du
#  bandeau juste sous la dernière icône entière de la barre d'outils — huit
#  pixels de moins et l'une d'elles dépassait, coupée en deux.
BAS_COUPE = 84
LARGEUR = 1120

#  La hauteur, dans l'image réduite, de l'en-tête et de la ligne d'état de
#  l'opérateur. Le contrôle de déformation regarde en dessous.
HAUT_TEXTE = 70

#  La séquence jouée par `setup-proportionnelle.py`, telle qu'elle est écrite
#  là-bas : deux images d'attente, puis deux fois le même geste, séparés par la
#  frappe du O.
TIRAGES = 8               # doit valoir TIRAGES dans `setup-proportionnelle.py`
ARRETS = (350, 350, 600)  # ... et en avoir autant que POSE là-bas
ATTENTE = 2               # images d'attente au début, grille plate


def geste(phase):
    """(durée, phase) pour un geste complet, toutes ses images à `phase`."""
    d = [(350, phase)]                                   # G : le cercle paraît
    d += [(80, phase)] * TIRAGES                         # le déplacement
    d += [(t, phase) for t in ARRETS]                    # l'arrêt en haut
    d += [(220, phase), (300, phase)]                    # ESC, retour au plat
    return d


#  (durée en ms, phase) — la phase donne le bandeau, 0 avant le O, 1 après.
PLAN = ([(400, 0)] * ATTENTE + geste(0)
        + [(650, 1), (400, 1)] + geste(1))


def sommets(depart):
    """Les images d'arrêt en haut du geste commencé à `depart`."""
    return tuple(range(depart + 1 + TIRAGES,
                       depart + 1 + TIRAGES + len(ARRETS)))


#  Les repères qu'on relit ensuite. Ils se déduisent de la séquence : les
#  écrire à la main, c'est se condamner à les oublier au prochain réglage.
SOMMETS = sommets(ATTENTE)              # le geste avec l'édition active
FRAPPE_O = ATTENTE + len(geste(0))      # l'image où la touche O est frappée
SOMMETS_APRES = sommets(FRAPPE_O + 2)   # le même geste, une fois éteinte

#  Les quatre moments de la planche de relecture : le plat, le dôme, la frappe
#  du O, le pic.
CLES = (0, SOMMETS[1], FRAPPE_O, SOMMETS_APRES[1])

BANDEAUX = (
    ("ÉDITION PROPORTIONNELLE ACTIVE",
     "un seul sommet est sélectionné, et tout le voisinage suit"),
    ("ÉDITION PROPORTIONNELLE ÉTEINTE — TOUCHE O",
     "le même geste, et cette fois le sommet part tout seul"),
)


def principal():
    vues = A.charger(IMAGES, len(PLAN), LARGEUR, BAS_COUPE)

    #  CONTRÔLE : la déformation doit vraiment se voir. Sur la série où les
    #  frappes n'arrivaient nulle part, cette part tombait à zéro.
    sommet = A.changement(vues, SOMMETS, depuis=HAUT_TEXTE)
    if sommet < 0.02:
        raise SystemExit("le viewport ne change que de %.2f %% au sommet du "
                         "geste : la séquence n'a pas été jouée"
                         % (100 * sommet))

    pol = A.polices()
    images = [A.bandeau(v, BANDEAUX[phase][0], BANDEAUX[phase][1], pol)
              for v, (_, phase) in zip(vues, PLAN)]
    A.enregistrer(BASE, images, [d for d, _ in PLAN], CLES)
    print("  viewport modifié au sommet du geste : %.1f %%" % (100 * sommet))


if __name__ == "__main__":
    principal()
