"""
Les briques de dessin des schémas de l'article.

Rien ici n'est propre à une figure : une toile qui travaille en coordonnées
finales, une palette de papier, et de quoi replier du texte.

----------------------------------------------------------------------------
POURQUOI UNE TOILE PLUTÔT QUE `ImageDraw` DIRECTEMENT
----------------------------------------------------------------------------
PIL ne lisse pas les formes. Un cercle, un arrondi ou une diagonale tracés
directement à la taille finale sortent en escalier, et un schéma aux contours
crénelés a l'air bâclé quoi qu'on mette dedans.

La parade est de dessiner à trois fois la taille puis de réduire en Lanczos.
Faite à la main, elle oblige à multiplier chaque coordonnée par l'échelle, et
il suffit d'en oublier une pour passer une heure à chercher pourquoi un trait
est à côté. La toile s'en charge : on lui parle en pixels de l'image finale,
elle multiplie avant d'atteindre PIL.

Le coût est d'une seconde de calcul. Le gain se voit sur chaque arrondi.
"""

import os

from PIL import Image, ImageDraw

import charte as C

ECHELLE = 3

PAPIER = (250, 249, 246)
ENCRE = (26, 27, 32)
GRIS = (100, 102, 112)
FAIBLE = (140, 141, 150)
FILET = (213, 211, 204)
VIOLET = (98, 44, 200)
VIOLET_PALE = (234, 227, 252)
BLANC = (255, 255, 255)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_G = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"


def typo(t):
    """L'apostrophe courbe : celle des livres, pas celle des claviers."""
    return t.replace("'", "’")


def verifier(*couples):
    """Chaque couleur contre le papier, avant de dessiner quoi que ce soit."""
    for nom, teinte, seuil in couples:
        r = C.contraste(teinte, PAPIER)
        print("  %-8s %-16s %.2f:1  %s"
              % (nom, str(teinte), r, "ok" if r >= seuil else "INSUFFISANT"))
        if r < seuil:
            raise SystemExit("%s : %.2f:1, sous le seuil" % (nom, r))


class Toile:
    """Un calque de dessin qui travaille en coordonnées de l'image finale."""

    def __init__(self, l, h, fond=PAPIER, echelle=ECHELLE):
        self.e = echelle
        self.im = Image.new("RGB", (l * echelle, h * echelle), fond)
        self.d = ImageDraw.Draw(self.im)

    def _b(self, b):
        return [v * self.e for v in b]

    def _p(self, points):
        return [(x * self.e, y * self.e) for x, y in points]

    # ---------------------------------------------------------------  texte
    def police(self, chemin, taille):
        return C.police(chemin, int(round(taille * self.e)))

    def mesure(self, texte, f):
        return self.d.textlength(texte, font=f) / self.e

    def texte(self, xy, t, f, teinte):
        self.d.text((xy[0] * self.e, xy[1] * self.e), t, font=f, fill=teinte)

    def espace(self, xy, texte, f, teinte, tracking):
        """Des capitales lettre à lettre, avec de l'air entre elles."""
        x, y = xy
        for c in texte:
            self.texte((x, y), c, f, teinte)
            x += self.mesure(c, f) + tracking
        return x - tracking

    def largeur_espacee(self, texte, f, tracking):
        return sum(self.mesure(c, f) for c in texte) \
            + tracking * max(len(texte) - 1, 0)

    def couper(self, texte, f, largeur):
        ligne, lignes = "", []
        for m in texte.split():
            essai = (ligne + " " + m).strip()
            if self.mesure(essai, f) > largeur and ligne:
                lignes.append(ligne)
                ligne = m
            else:
                ligne = essai
        lignes.append(ligne)
        return lignes

    # --------------------------------------------------------------  formes
    def ligne(self, b, teinte, epaisseur):
        self.d.line(self._b(b), fill=teinte, width=int(epaisseur * self.e))

    def rrect(self, b, rayon, teinte=None, contour=None, epaisseur=2):
        self.d.rounded_rectangle(self._b(b), radius=rayon * self.e,
                                 fill=teinte, outline=contour,
                                 width=int(epaisseur * self.e))

    def disque(self, cx, cy, r, teinte=None, contour=None, epaisseur=2):
        self.d.ellipse(self._b([cx - r, cy - r, cx + r, cy + r]),
                       fill=teinte, outline=contour,
                       width=int(epaisseur * self.e))

    def arc(self, cx, cy, r, a0, a1, teinte, epaisseur):
        self.d.arc(self._b([cx - r, cy - r, cx + r, cy + r]), a0, a1,
                   fill=teinte, width=int(epaisseur * self.e))

    def polygone(self, points, teinte):
        self.d.polygon(self._p(points), fill=teinte)

    def polyligne(self, points, teinte, epaisseur):
        self.d.line(self._p(points), fill=teinte,
                    width=int(epaisseur * self.e), joint="curve")

    def pointilles(self, points, teinte, epaisseur, plein=9, vide=7):
        """
        Une polyligne en pointillé, mesurée le long du tracé.

        PIL ne sait pas tirer un trait discontinu. On parcourt donc le chemin
        en alternant plein et vide, ce qui donne un pointillé régulier même
        quand la ligne change de direction.
        """
        reste, trace = plein, True
        for (x0, y0), (x1, y1) in zip(points, points[1:]):
            dx, dy = x1 - x0, y1 - y0
            long = (dx * dx + dy * dy) ** 0.5
            if long == 0:
                continue
            ux, uy = dx / long, dy / long
            parcouru = 0.0
            while parcouru < long:
                pas = min(reste, long - parcouru)
                if trace:
                    self.ligne([x0 + ux * parcouru, y0 + uy * parcouru,
                                x0 + ux * (parcouru + pas),
                                y0 + uy * (parcouru + pas)],
                               teinte, epaisseur)
                parcouru += pas
                reste -= pas
                if reste <= 0:
                    trace = not trace
                    reste = plein if trace else vide

    def fleche(self, x0, y0, x1, y1, teinte, epaisseur, pointe=9):
        """Un trait terminé par une pointe pleine, orientée par le trait."""
        long = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
        ux, uy = (x1 - x0) / long, (y1 - y0) / long
        self.ligne([x0, y0, x1 - ux * pointe, y1 - uy * pointe],
                   teinte, epaisseur)
        px, py = -uy, ux
        self.polygone([(x1, y1),
                       (x1 - ux * pointe * 1.7 + px * pointe * 0.72,
                        y1 - uy * pointe * 1.7 + py * pointe * 0.72),
                       (x1 - ux * pointe * 1.7 - px * pointe * 0.72,
                        y1 - uy * pointe * 1.7 - py * pointe * 0.72)], teinte)

    # ---------------------------------------------------------------  sortie
    def final(self, l, h):
        return self.im.resize((l, h), Image.LANCZOS)


def enregistrer(image, base, largeur, hauteur):
    """
    Les deux fichiers : le WebP pour le site, le PNG pour la relecture.

    Windows et macOS n'ouvrent pas le WebP par défaut et proposent d'installer
    un convertisseur, ce qui laisse croire que le fichier est cassé.
    """
    image.save(base + ".webp", "WEBP", quality=C.QUALITE, method=6)
    image.save(base + ".png", "PNG", optimize=True)
    print()
    print("  %d × %d  (dessiné à %d × %d)"
          % (largeur, hauteur, largeur * ECHELLE, hauteur * ECHELLE))
    for e in (".webp", ".png"):
        print("  %-44s %.0f Ko" % (os.path.basename(base + e),
                                   os.path.getsize(base + e) / 1024))
