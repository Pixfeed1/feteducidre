# -*- coding: utf-8 -*-
u"""
LA PERSPECTIVE, PARTAGEE.

Le grillage, le buisson qui le longe et le bord du sable appartiennent a la
MEME scene : ils doivent fuir vers le meme point. Tant que chacun portait sa
propre geometrie, rien ne garantissait qu'ils soient d'accord - et un
buisson qui ne suit pas la cloture le long de laquelle il est plante se voit
immediatement. D'ou ce module : un seul point de fuite, une seule loi.

LE MODELE
  Un point est repere par (u, y0) :
    u  = distance le long de la ligne de fuite, comptee en ecarts de poteaux
    y0 = ou ce point se trouverait a l'ecran si u valait 0, c'est-a-dire au
         plus pres du spectateur.
  Tout descend d'un seul facteur, la decroissance en 1/z de la perspective :

      s(u) = 1 / (1 + RECUL . u)
      x = xf + (X0 - xf) . s(u)
      y = yf + (y0 - yf) . s(u)

  Une longueur quelconque - hauteur de poteau, rayon d'une touffe, epaisseur
  d'un fil - se projette en la multipliant par ce meme s(u).

L'HORIZON
  FUITE_Y est l'horizon : toute ligne posee AU SOL y converge. C'est pour
  cela que le pied du grillage, le pied du buisson et le bord du sable
  montent tous les trois vers lui en s'eloignant, chacun a son rythme selon
  sa distance au spectateur. Ils ne peuvent pas se croiser, et c'est cette
  impossibilite qui fait tenir la scene.
"""

LARGEUR, HAUTEUR = 1800, 1350

# ==========================================================================
# LE MODE. C'est le seul interrupteur de tout le decor.
#
#   FRONTAL = True    vue de face, aucune fuite. C'est le parti de la
#                     reference : rien n'y converge, tout est parallele au
#                     cadre. Le style tient a cette platitude assumee - une
#                     fuite, meme juste, y introduit une profondeur qui
#                     contredit les aplats.
#   FRONTAL = False   perspective a un point de fuite. Geometriquement
#                     exacte, mais c'est une autre image.
#
# Les generateurs - grillage, buisson, sable - ne connaissent que projeter()
# et echelle(). Basculer l'interrupteur les fait tous changer ensemble, sans
# qu'aucun ne soit modifie.
# ==========================================================================
FRONTAL = True

PAS_X = 268.0        # en vue de face : ecart entre deux poteaux, en pixels
X0 = -60.0           # la ligne entre par la gauche, hors cadre

FUITE_X = 2400.0     # en perspective seulement : hors cadre a droite
FUITE_Y = 470.0      # l'horizon
RECUL = 0.115        # vitesse de fuite


def echelle(u):
    """Le facteur de reduction a la distance u. Toujours 1 en vue de face."""
    if FRONTAL:
        return 1.0
    return 1.0 / (1.0 + RECUL * u)


def projeter(u, y0):
    """(distance le long de la ligne, hauteur au plus pres) -> (x, y)."""
    if FRONTAL:
        return (X0 + u * PAS_X, y0)
    k = echelle(u)
    return (FUITE_X + (X0 - FUITE_X) * k, FUITE_Y + (y0 - FUITE_Y) * k)


def u_de_x(x):
    """L'inverse : a quelle distance correspond une abscisse a l'ecran."""
    if FRONTAL:
        return (x - X0) / PAS_X
    k = (x - FUITE_X) / (X0 - FUITE_X)
    return (1.0 / k - 1.0) / RECUL


def ecart_px():
    """
    L'ecart entre deux poteaux a l'ecran, au plus pres du spectateur.

    Sert a convertir en unites du monde tout ce qui se pense en pixels -
    l'espacement des touffes, la maille du treillis. Sans cette conversion,
    changer l'ecart entre poteaux deplacerait aussi la vegetation, qui n'a
    pourtant rien a voir avec la cloture.
    """
    return projeter(1.0, 0.0)[0] - projeter(0.0, 0.0)[0]


def ligne_au_sol(y0, pas=0.5):
    """
    Le trace d'une ligne posee au sol, de la gauche du cadre jusqu'au bord
    droit. C'est une droite - une projection perspective conserve les droites
    - mais on l'echantillonne quand meme : cela permet de la refermer et de
    la reutiliser telle quelle comme bord de remplissage.
    """
    import math
    points, u = [], 0.0
    while True:
        x, y = projeter(u, y0)
        # En vue de face, une ligne au sol strictement droite fige l'image.
        # On lui donne une ondulation tres calme - 14 px d'amplitude sur
        # 1800 de large - qui suffit a la faire respirer sans jamais
        # ressembler a une vague. En perspective on n'y touche pas : le sol
        # ne peut pas serpenter ET fuir.
        if FRONTAL:
            y += 14.0 * math.sin(x / 340.0) + 6.0 * math.sin(x / 131.0 + 1.7)
        points.append((x, y))
        if x > LARGEUR + 40:
            break
        u += pas
        if u > 400:
            break
    return points
