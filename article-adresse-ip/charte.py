"""
La charte des figures de l'article « Comment obtenir son adresse IP ».

Palette, polices, et le contrôle de contraste. Sorti dans un module à part
pour que toutes les images de l'article partagent les mêmes valeurs : deux
figures qui se suivent avec deux verts différents se lisent comme deux
articles différents.

----------------------------------------------------------------------------
POURQUOI UN CONTRÔLE DE CONTRASTE ET PAS UN CHOIX À L'ŒIL
----------------------------------------------------------------------------
Sur fond clair, une couleur peut paraître très bien sur l'écran où on la
choisit et devenir illisible en vignette. C'est arrivé sur la première figure :
le vert d'eau retenu tombait à 4,33:1, sous le seuil de confort de 4,5. Rien
ne le signalait — il fallait le mesurer.

Les scripts appellent donc `verifier()` AVANT de dessiner, et refusent de
produire une figure dont une couleur de texte ne passe pas.
"""

from PIL import ImageFont

# ---------------------------------------------------------------------------
#  LA PALETTE, EN CLAIR
# ---------------------------------------------------------------------------
FOND = (246, 247, 250)
PANNEAU = (255, 255, 255)
BORD = (216, 220, 228)
ENCRE = (24, 26, 34)            # le texte fort
GRIS = (92, 98, 112)
FAIBLE = (132, 138, 152)
TRAIT = (206, 211, 220)
ECRAN = (234, 237, 242)

#  Les deux teintes qui portent le sens. Reprises foncées : choisies pour du
#  fond sombre, elles ne tenaient pas sur du blanc.
LOCAL = (6, 119, 97)            # 5,13:1 — ce qui reste chez vous, IPv4
PUBLIC = (98, 44, 200)          # 7,22:1 — ce qui circule, IPv6

POLICE_G = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
POLICE_R = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
POLICE_M = "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"
POLICE_MR = "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf"

QUALITE = 92


def police(chemin, taille):
    try:
        return ImageFont.truetype(chemin, taille)
    except OSError:
        return ImageFont.load_default()


def contraste(a, b):
    """Le rapport de contraste WCAG entre deux couleurs."""
    def lum(c):
        v = []
        for x in c[:3]:
            x /= 255.0
            v.append(x / 12.92 if x <= 0.04045
                     else ((x + 0.055) / 1.055) ** 2.4)
        return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]
    l1, l2 = sorted((lum(a), lum(b)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


def verifier(fond=FOND, extra=()):
    """
    Mesure le contraste de chaque couleur de texte contre le fond et refuse
    de continuer si l'une passe sous son seuil. 4,5:1 pour du texte courant,
    3:1 pour les mentions accessoires.
    """
    liste = [("texte fort", ENCRE, 4.5), ("texte gris", GRIS, 4.5),
             ("mention faible", FAIBLE, 3.0),
             ("teinte IPv4", LOCAL, 4.5), ("teinte IPv6", PUBLIC, 4.5)]
    liste.extend(extra)
    faibles = []
    for nom, couleur, seuil in liste:
        r = contraste(couleur, fond)
        print("  %-18s %-16s %.2f:1  %s"
              % (nom, str(couleur), r, "ok" if r >= seuil else "INSUFFISANT"))
        if r < seuil:
            faibles.append("%s (%.2f:1 < %.1f)" % (nom, r, seuil))
    if faibles:
        raise SystemExit("contraste insuffisant : " + ", ".join(faibles))


def fr(gabarit, *valeurs):
    """
    Un nombre décimal à la française, DANS une phrase.

    On ne convertit que les points entourés de chiffres : un `replace` global
    transformerait aussi les points de fin de phrase en virgules.
    """
    import re
    return re.sub(r"(?<=\d)\.(?=\d)", ",", gabarit % valeurs)


def espacer(n):
    """Un grand nombre à la française : groupes de trois séparés par une
    espace. `format(n, ',')` mettrait des virgules, qui en français sont des
    séparateurs DÉCIMAUX — le lecteur lirait autre chose."""
    return format(n, ",").replace(",", " ")
