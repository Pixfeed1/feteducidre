"""
La charte des figures de l'article « PrestaShop headless avec Next.js ».

Volontairement autonome : ce dossier doit pouvoir être déplacé ou repris seul.
Les neutres sont ceux des autres articles du site — même fond clair, même
encre — mais les deux teintes d'accent lui sont propres, parce qu'ici elles ne
désignent pas les mêmes choses.

Le contrôle de contraste est le même qu'ailleurs, et pour la même raison : une
couleur choisie à l'œil sur fond clair peut très bien passer sur l'écran où on
la choisit et devenir illisible en vignette. On mesure avant de dessiner.
"""

from PIL import ImageFont

FOND = (246, 247, 250)
CARTE = (255, 255, 255)
BORD = (216, 220, 228)
ENCRE = (24, 26, 34)
GRIS = (92, 98, 112)
FAIBLE = (132, 138, 152)
TRAIT = (206, 211, 220)
BLOC = (231, 234, 240)          # les aplats qui figurent du contenu

#  LES DEUX RÔLES.
#  Le back-office est gris de fer : c'est l'outil, il n'a pas à séduire.
#  La vitrine porte le violet de la charte Pixfeed : c'est ce que le client
#  voit. La flèche d'API prend la teinte de la vitrine, parce que c'est elle
#  qui va chercher, et non l'inverse.
ADMIN = (46, 58, 80)
VITRINE = (98, 44, 200)

#  Une troisième teinte, pour les figures qui opposent un cas fragile à un cas
#  sûr. Rouge brique plutôt que rouge vif : on signale une fragilité, on ne
#  crie pas à la panne.
ALERTE = (176, 46, 38)

POLICE_G = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
POLICE_R = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
POLICE_M = "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"

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


def verifier(fond=FOND):
    liste = (("texte fort", ENCRE, 4.5), ("texte gris", GRIS, 4.5),
             ("mention faible", FAIBLE, 3.0),
             ("teinte back-office", ADMIN, 4.5),
             ("teinte vitrine", VITRINE, 4.5),
             ("teinte alerte", ALERTE, 4.5))
    faibles = []
    for nom, couleur, seuil in liste:
        r = contraste(couleur, fond)
        print("  %-20s %-16s %.2f:1  %s"
              % (nom, str(couleur), r, "ok" if r >= seuil else "INSUFFISANT"))
        if r < seuil:
            faibles.append("%s (%.2f:1 < %.1f)" % (nom, r, seuil))
    if faibles:
        raise SystemExit("contraste insuffisant : " + ", ".join(faibles))
