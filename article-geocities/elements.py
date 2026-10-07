"""
Fabrique les éléments graphiques d'une page perso des années 1990.

    python3 article-geocities/elements.py

Produit le fond étoilé, le compteur de visites, le panneau « en
construction » et le filet arc-en-ciel, dans `elements/`.

----------------------------------------------------------------------------
POURQUOI LES DESSINER PLUTÔT QUE LES RÉCUPÉRER
----------------------------------------------------------------------------
Les GIF d'époque qui circulent encore ont tous un auteur, même quand plus
personne ne sait lequel. Les reprendre dans un article serait reproduire
l'œuvre d'un tiers, et le droit français ne connaît pas le fair use.

Ils sont donc redessinés d'après leurs conventions, qui elles ne
s'approprient pas : des rayures de chantier jaune et noir, un compteur à
chiffres clairs sur fond noir, un fond étoilé en tuile. Ce sont des
codes graphiques, pas des images précises.

----------------------------------------------------------------------------
LA TUILE DOIT SE RACCORDER
----------------------------------------------------------------------------
Un fond d'époque se répète avec `background=`. Les étoiles sont donc
placées en tore : toute étoile proche d'un bord est recopiée sur le bord
opposé, sinon la couture se voit à chaque raccord. Les pages de l'époque
avaient souvent ce défaut ; le reproduire serait du pastiche, pas de la
reconstitution.
"""

import os
import random

from PIL import Image, ImageDraw

ICI = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(ICI, "elements")

FOND = (0, 0, 51)          # le #000033 canonique
TUILE = 140


def fond_etoile(chemin, graine=1997):
    alea = random.Random(graine)
    im = Image.new("RGB", (TUILE, TUILE), FOND)
    d = ImageDraw.Draw(im)

    def etoile(x, y, r, teinte):
        #  Placement en tore : une étoile près d'un bord est recopiée sur
        #  le bord opposé, pour que la tuile se raccorde sans couture.
        for dx in (-TUILE, 0, TUILE):
            for dy in (-TUILE, 0, TUILE):
                d.ellipse([x + dx - r, y + dy - r, x + dx + r, y + dy + r],
                          fill=teinte)

    for _ in range(46):
        x, y = alea.uniform(0, TUILE), alea.uniform(0, TUILE)
        etoile(x, y, alea.choice((0.5, 0.5, 0.5, 1.0)), (210, 210, 235))
    for _ in range(7):
        x, y = alea.uniform(0, TUILE), alea.uniform(0, TUILE)
        etoile(x, y, 1.6, (255, 255, 255))
        #  Les quatre branches de la grosse étoile.
        for a, b in ((-5, 0), (5, 0), (0, -5), (0, 5)):
            d.line([x, y, x + a, y + b], fill=(255, 255, 255))

    im.save(chemin)
    return im.size


def compteur(chemin, valeur="0047213"):
    """L'odomètre blanc sur noir, avec son cadre en relief."""
    ch, cl = 34, 24
    marge = 4
    L = marge * 2 + len(valeur) * cl
    H = marge * 2 + ch
    im = Image.new("RGB", (L, H), (24, 24, 24))
    d = ImageDraw.Draw(im)

    #  Le relief des tableaux de l'époque : clair en haut à gauche,
    #  sombre en bas à droite.
    d.line([0, 0, L - 1, 0], fill=(140, 140, 140))
    d.line([0, 0, 0, H - 1], fill=(140, 140, 140))
    d.line([0, H - 1, L - 1, H - 1], fill=(70, 70, 70))
    d.line([L - 1, 0, L - 1, H - 1], fill=(70, 70, 70))

    from PIL import ImageFont
    try:
        f = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 26)
    except OSError:
        f = ImageFont.load_default()

    for i, c in enumerate(valeur):
        x = marge + i * cl
        d.rectangle([x, marge, x + cl - 2, marge + ch - 1], fill=(0, 0, 0))
        b = d.textbbox((0, 0), c, font=f)
        d.text((x + (cl - 2 - (b[2] - b[0])) / 2 - b[0],
                marge + (ch - (b[3] - b[1])) / 2 - b[1]),
               c, font=f, fill=(245, 245, 245))

    im.save(chemin)
    return im.size


def construction(chemin):
    """Le panneau de chantier, rayures jaune et noir."""
    L, H = 420, 76
    im = Image.new("RGB", (L, H), (255, 204, 0))
    d = ImageDraw.Draw(im)

    #  Les bandes obliques, en haut et en bas.
    for bande in (0, H - 16):
        d.rectangle([0, bande, L, bande + 16], fill=(255, 204, 0))
        x = -H
        while x < L + H:
            d.polygon([(x, bande), (x + 12, bande),
                       (x + 12 - 16, bande + 16), (x - 16, bande + 16)],
                      fill=(20, 20, 20))
            x += 26

    from PIL import ImageFont
    try:
        f = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 25)
    except OSError:
        f = ImageFont.load_default()
    t = "EN CONSTRUCTION"
    b = d.textbbox((0, 0), t, font=f)
    d.text(((L - (b[2] - b[0])) / 2 - b[0], (H - (b[3] - b[1])) / 2 - b[1]),
           t, font=f, fill=(20, 20, 20))

    im.save(chemin)
    return im.size


def filet(chemin):
    """Le séparateur arc-en-ciel qui remplaçait les <hr>."""
    L, H = 500, 10
    im = Image.new("RGB", (L, H))
    d = ImageDraw.Draw(im)
    couleurs = ((255, 0, 0), (255, 136, 0), (255, 255, 0), (0, 200, 0),
                (0, 128, 255), (110, 0, 200))
    n = len(couleurs)
    for x in range(L):
        i = int(x / L * n) % n
        j = (i + 1) % n
        t = (x / L * n) - int(x / L * n)
        c = tuple(int(couleurs[i][k] + (couleurs[j][k] - couleurs[i][k]) * t)
                  for k in range(3))
        d.line([x, 0, x, H], fill=c)
    im.save(chemin)
    return im.size


def principal():
    os.makedirs(SORTIE, exist_ok=True)
    faits = (
        ("etoiles.png", fond_etoile),
        ("compteur.png", compteur),
        ("construction.png", construction),
        ("filet.png", filet),
    )
    for nom, fabrique in faits:
        chemin = os.path.join(SORTIE, nom)
        taille = fabrique(chemin)
        print("  %-18s %s  %.1f Ko"
              % (nom, "x".join(str(v) for v in taille),
                 os.path.getsize(chemin) / 1024.0))


if __name__ == "__main__":
    principal()
