"""
La charte des figures de l'article « Onze questions à poser à une agence web ».

Mêmes neutres que les autres articles du site — fond clair, encre sombre,
mêmes graisses — et le même contrôle de contraste avant dessin. Ce qui change
ici : une seule teinte d'accent, le violet Pixfeed, parce que l'image ne met
rien en opposition. Elle énumère.

Deux violets, et ce n'est pas une hésitation :

  - VIOLET sert aux APLATS (pastilles de numéro, filets). Un aplat n'a pas à
    passer le seuil de lisibilité d'un texte, il doit se voir ;
  - VIOLET_TEXTE, plus foncé, sert dès qu'on écrit en violet SUR le fond.

Confondre les deux, c'est soit un aplat terne, soit un texte qu'on devine.
"""

from PIL import ImageFont

FOND = (246, 247, 250)
CARTE = (255, 255, 255)
BORD = (216, 220, 228)
ENCRE = (24, 26, 34)
GRIS = (92, 98, 112)
FAIBLE = (132, 138, 152)
TRAIT = (206, 211, 220)

VIOLET = (148, 66, 250)          # la charte Pixfeed, pour les aplats
VIOLET_TEXTE = (98, 44, 200)     # sa version lisible sur fond clair

POLICE_G = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
POLICE_R = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

QUALITE = 92


def police(chemin, taille):
    try:
        return ImageFont.truetype(chemin, taille)
    except OSError:
        return ImageFont.load_default()


def contraste(a, b):
    def lum(c):
        v = []
        for x in c[:3]:
            x /= 255.0
            v.append(x / 12.92 if x <= 0.04045
                     else ((x + 0.055) / 1.055) ** 2.4)
        return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]
    l1, l2 = sorted((lum(a), lum(b)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


def verifier():
    """Chaque couleur de texte contre le fond qu'elle occupe réellement."""
    liste = (("texte fort", ENCRE, FOND, 4.5),
             ("texte gris", GRIS, FOND, 4.5),
             ("mention faible", FAIBLE, FOND, 3.0),
             ("violet sur fond", VIOLET_TEXTE, FOND, 4.5),
             ("blanc sur pastille", (255, 255, 255), VIOLET, 4.5))
    faibles = []
    for nom, couleur, fond, seuil in liste:
        r = contraste(couleur, fond)
        print("  %-20s %-16s %.2f:1  %s"
              % (nom, str(couleur), r, "ok" if r >= seuil else "INSUFFISANT"))
        if r < seuil:
            faibles.append("%s (%.2f:1 < %.1f)" % (nom, r, seuil))
    if faibles:
        raise SystemExit("contraste insuffisant : " + ", ".join(faibles))
