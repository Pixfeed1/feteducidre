"""
L'animation de l'édition proportionnelle : le même geste, avant et après O.

    sh article-blender-astuces/blender-gui/capturer-proportionnelle.sh
    python3 article-blender-astuces/anime_proportionnelle.py

Produit `astuces-blender-05-edition-proportionnelle.webp` (animé) et
`-apercu.jpg`, une planche fixe pour la relecture.

Les trente-deux écrans bruts restent dans `/tmp/bl/frames` et n'entrent pas
dans le dépôt : ils pèsent vingt-quatre mégaoctets, et la chaîne de capture se
rejoue en trois minutes.

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

import glob
import os

import numpy as np
from PIL import Image, ImageDraw

import charte as C

RACINE = os.path.dirname(os.path.abspath(__file__))
IMAGES = "/tmp/bl/frames"
BASE = os.path.join(RACINE, "astuces-blender-05-edition-proportionnelle")

#  La capture couvre toute l'aire de la vue 3D, barre d'outils et en-tête
#  compris. On lui retire une bande de sol vide en bas, et rien d'autre : la
#  grille est centrée dans la vue, et rogner plus la ferait redescendre dans le
#  bas de l'image. La hauteur de la coupe n'est pas ronde par hasard — elle
#  place le bord du bandeau juste sous la dernière icône entière de la barre
#  d'outils — huit pixels de moins et l'une d'elles dépassait, coupée en deux.
BAS_COUPE = 84
LARGEUR = 1120

#  Une qualité basse pour une image fixe, et c'est voulu : trente-deux écrans
#  font un fichier lourd, et un aplat gris parcouru de fils noirs ne souffre
#  pas de la compression. Contrôlé à l'oeil sur l'image du sommet, là où le
#  cercle gris est ce qu'il y a de plus fragile — il tient.
QUALITE = 68

#  La hauteur, dans l'image réduite, de l'en-tête et de la ligne d'état de
#  l'opérateur. Le contrôle de déformation regarde en dessous.
HAUT_TEXTE = 70

BANDE = 66
ENCRE = (24, 25, 30)
SUR_ENCRE = (243, 241, 235)
DISCRET = (172, 174, 182)
PAPIER = (250, 249, 246)
FILET = (213, 211, 204)

#  La séquence jouée par `setup-proportionnelle.py`, telle qu'elle est écrite
#  là-bas : deux images d'attente, puis deux fois le même geste, séparés par la
#  frappe du O. Le tableau ci-dessous donne à chaque image sa durée.
TIRAGES = 8              # doit valoir TIRAGES dans `setup-proportionnelle.py`
ARRETS = (350, 350, 600)  # ... et en avoir autant que POSE là-bas


def geste(debut):
    """(durée, phase) pour un geste complet, toutes ses images à `debut`."""
    d = [(350, debut)]                                   # G : le cercle paraît
    d += [(80, debut)] * TIRAGES                         # le déplacement
    d += [(t, debut) for t in ARRETS]                    # l'arrêt en haut
    d += [(220, debut), (300, debut)]                    # ESC, retour au plat
    return d


#  (durée en ms, phase) — la phase donne le bandeau, 0 avant le O, 1 après.
ATTENTE = 2              # images d'attente au début, grille plate
PLAN = ([(400, 0)] * ATTENTE + geste(0)
        + [(650, 1), (400, 1)] + geste(1))

#  Les repères qu'on relit ensuite. Ils se déduisent de la séquence : les
#  écrire à la main, c'est se condamner à les oublier au prochain réglage.
def sommets(depart):
    """Les images d'arrêt en haut du geste commencé à `depart`."""
    return tuple(range(depart + 1 + TIRAGES,
                       depart + 1 + TIRAGES + len(ARRETS)))


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

#  La provenance tient dans le bandeau, calée à droite. Une figure doit dire
#  d'où elle vient sans qu'on ait à lire l'article autour.
SOURCE = "BLENDER 5.2.1 LTS — CAPTURE D’ÉCRAN"


def espace(d, xy, texte, f, teinte, tracking):
    x, y = xy
    for c in texte:
        d.text((x, y), c, font=f, fill=teinte)
        x += d.textlength(c, font=f) + tracking
    return x - tracking


def mesurer(vues, depuis, indices):
    """La part du viewport qui a changé, sur les images données."""
    plat = np.asarray(vues[0].convert("L"), dtype=np.int16)[depuis:]
    part = 0.0
    for i in indices:
        v = np.asarray(vues[i].convert("L"), dtype=np.int16)[depuis:]
        part = max(part, float(np.mean(np.abs(v - plat) > 40)))
    return part


def bandeau(im, phase, polices):
    """Une copie de l'image, son bandeau de légende posé en pied."""
    f_titre, f_sous, f_source = polices
    titre, commentaire = BANDEAUX[phase]
    out = im.copy()
    d = ImageDraw.Draw(out)
    l, h = out.size
    d.rectangle([0, h - BANDE, l, h], fill=ENCRE)
    fin = espace(d, (22, h - BANDE + 14), titre, f_titre, SUR_ENCRE, 2.2)
    d.text((22, h - BANDE + 40), commentaire, font=f_sous, fill=DISCRET)

    largeur = sum(d.textlength(c, font=f_source) + 1.6 for c in SOURCE) - 1.6
    depart = l - 22 - largeur
    if max(fin, 22 + d.textlength(commentaire, font=f_sous)) > depart - 24:
        raise SystemExit("le bandeau « %s » touche la mention de source"
                         % titre)
    espace(d, (depart, h - BANDE + 27), SOURCE, f_source, DISCRET, 1.6)
    return out


def principal():
    chemins = sorted(glob.glob(os.path.join(IMAGES, "*.png")))
    if not chemins:
        raise SystemExit(
            "captures absentes : lancez d'abord\n"
            "  sh article-blender-astuces/blender-gui/"
            "capturer-proportionnelle.sh")
    if len(chemins) != len(PLAN):
        raise SystemExit("%d captures pour %d étapes prévues : la séquence de "
                         "`setup-proportionnelle.py` a changé"
                         % (len(chemins), len(PLAN)))

    C.verifier()
    if C.contraste(DISCRET, ENCRE) < 4.5:
        raise SystemExit("le commentaire du bandeau n'est pas assez lisible")

    brutes = [Image.open(c).convert("RGB") for c in chemins]
    if len({b.size for b in brutes}) != 1:
        raise SystemExit("les captures n'ont pas toutes la même taille")
    bl, bh = brutes[0].size
    if bh <= BAS_COUPE + 200:
        raise SystemExit("la capture est trop courte pour être rognée")

    haut = int(round(LARGEUR * (bh - BAS_COUPE) / float(bl)))
    vues = [b.crop((0, 0, bl, bh - BAS_COUPE)).resize((LARGEUR, haut),
                                                      Image.LANCZOS)
            for b in brutes]

    #  CONTRÔLE : la déformation doit vraiment se voir. On compte, au sommet du
    #  geste, la part du viewport qui a changé par rapport à la première image,
    #  restée plate.
    #
    #  La mesure commence sous la ligne de l'en-tête, et c'est tout l'intérêt :
    #  pendant un déplacement, Blender affiche « Proportional Size (Smooth) »
    #  et les trois écarts juste sous les menus. Une comparaison portant sur
    #  l'image entière aurait donc trouvé une belle différence même sur la
    #  série ratée, où la grille n'a jamais bougé d'un pixel.
    sommet = mesurer(vues, HAUT_TEXTE, SOMMETS)
    if sommet < 0.02:
        raise SystemExit("le viewport ne change que de %.2f %% au sommet du "
                         "geste : la séquence n'a pas été jouée"
                         % (100 * sommet))

    polices = (C.police(C.POLICE_G, 17), C.police(C.POLICE_R, 15),
               C.police(C.POLICE_G, 11))
    images = [bandeau(v, phase, polices)
              for v, (_, phase) in zip(vues, PLAN)]
    durees = [d for d, _ in PLAN]

    images[0].save(BASE + ".webp", "WEBP", save_all=True,
                   append_images=images[1:], duration=durees, loop=0,
                   quality=QUALITE, method=6)

    #  Une planche fixe à côté : une image animée ne se relit pas image par
    #  image, et il faut bien vérifier les quatre moments avant publication.
    marge, gouttiere = 24, 16
    larg = (1600 - 2 * marge - 3 * gouttiere) // 4
    ht = int(round(larg * images[0].height / float(images[0].width)))
    planche = Image.new("RGB", (1600, ht + 2 * marge), PAPIER)
    dd = ImageDraw.Draw(planche)
    for i, k in enumerate(CLES):
        x = marge + i * (larg + gouttiere)
        planche.paste(images[k].resize((larg, ht), Image.LANCZOS), (x, marge))
        dd.rectangle([x, marge, x + larg - 1, marge + ht - 1], outline=FILET,
                     width=1)
    planche.save(BASE + "-apercu.jpg", "JPEG", quality=92, optimize=True)

    print()
    print("  %d captures %d × %d  ->  %d × %d, %.2f s de boucle"
          % (len(images), bl, bh, images[0].width, images[0].height,
             sum(durees) / 1000.0))
    print("  viewport modifié au sommet du geste : %.1f %%" % (100 * sommet))
    for e in (".webp", "-apercu.jpg"):
        print("  %-56s %.0f Ko" % (os.path.basename(BASE + e),
                                   os.path.getsize(BASE + e) / 1024))


if __name__ == "__main__":
    principal()
