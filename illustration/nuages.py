# -*- coding: utf-8 -*-
u"""
Les nuages.

CE QUE MONTRE LE MODELE
  Trois nuages, tous batis sur le meme rapport : environ SIX FOIS PLUS LARGES
  QUE HAUTS. Releve sur l'image de reference (760 px de large) :

      nuage haut-gauche   170 x 30 px    5.7 : 1
      nuage haut-droite   145 x 25 px    5.8 : 1
      nuage du milieu     140 x 24 px    5.8 : 1

  Rapporte a notre format de 1800 px, cela donne des nuages d'environ
  400 x 70 px. Les notres faisaient 330 x 128 - un rapport de 2.6 : 1. Ils
  n'etaient pas un peu trop gros, ils etaient DEUX FOIS TROP HAUTS.

CE QUI LES REND ALLONGES, ET PAS SEULEMENT PLUS PLATS
  Un nuage etait construit d'une barre surmontee de CERCLES. Un cercle a une
  seule dimension : des qu'il depasse, il gonfle. En l'aplatissant on
  n'obtient qu'une barre bosselee.

  Ici les bosses sont des ELLIPSES largement plus larges que hautes, et
  surtout elles se CHEVAUCHENT : chacune deborde sur sa voisine d'un tiers de
  sa largeur. C'est ce recouvrement qui donne une crete continue plutot
  qu'une file de bulles. Le bas, lui, reste rigoureusement droit - un nuage
  de ce style se pose sur une horizontale.

LA DISSYMETRIE
  Les bosses ne sont pas de meme hauteur ni regulierement espacees : la plus
  haute est placee au tiers, jamais au milieu. Trois bosses egales font une
  chenille ; trois bosses inegales font un nuage.
"""

# Le rapport releve sur le modele. Un seul nombre commande la silhouette.
RAPPORT = 5.8

# Profils de crete : la hauteur de chaque bosse, en fraction de la hauteur
# totale, et sa position le long du nuage. Trois profils pour que les nuages
# d'une meme image ne soient pas des copies.
PROFILS = [
    [(0.30, 0.62), (0.52, 1.00), (0.74, 0.74)],
    [(0.26, 0.78), (0.48, 1.00), (0.70, 0.58), (0.86, 0.34)],
    [(0.34, 0.86), (0.60, 1.00)],
]


def nuage(x, y, longueur, profil=0, rapport=RAPPORT, indent=8):
    u"""
    x, y      : le coin bas-gauche. y est la ligne sur laquelle le nuage pose.
    longueur  : sa largeur totale.
    profil    : lequel des PROFILS de crete utiliser.

    Retourne les formes, sans couleur : c'est l'appelant qui peint, ce qui
    permet de reutiliser la meme silhouette pour le ton froid et pour le ton
    clair (voir le decalage vers le haut dans construire.py).
    """
    hauteur = longueur / float(rapport)
    # LE CORPS : une gelule. Sa hauteur ne fait que la moitie du nuage - le
    # reste est pris par les bosses. Au-dela, le nuage redevient une barre.
    corps = hauteur * 0.52
    formes = [u'<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
              u'rx="%.1f"/>' % (x, y - corps, longueur, corps, corps / 2.0)]

    for pos, haut in PROFILS[profil % len(PROFILS)]:
        # LARGEUR DE BOSSE : un tiers du nuage. Elles se chevauchent donc
        # largement, et la crete devient continue.
        rx = longueur * 0.19
        # LES BOSSES SONT TANGENTES A LA LIGNE DE POSE. Demi-hauteur egale a
        # la moitie de leur elevation, centre remonte d'autant : le bas de
        # l'ellipse tombe alors exactement sur y.
        #
        # Sans cette contrainte, les ellipses debordaient SOUS le nuage et le
        # bas devenait bosselé. Or dans le modele un nuage repose sur une
        # horizontale franche - c'est meme ce qui le distingue d'un mouton.
        ry = hauteur * haut / 2.0
        formes.append(u'<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f"/>'
                      % (x + longueur * pos, y - ry, rx, ry))

    e = " " * indent
    return ("\n" + e).join(formes)


if __name__ == "__main__":
    for i, p in enumerate(PROFILS):
        print(u"profil %d : %d bosses, la plus haute a %.0f%% de la longueur"
              % (i, len(p), 100 * max(p, key=lambda b: b[1])[0]))
    print(u"\nrapport %.1f : un nuage de 400 px fait %.0f px de haut"
          % (RAPPORT, 400 / RAPPORT))
