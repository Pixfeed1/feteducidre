# -*- coding: utf-8 -*-
u"""
La haie taillee.

RELEVE SUR LA SECONDE REFERENCE (image de 1232 x 953)
    haut de la haie    y = 515   ->  0.54 de la hauteur
    pied de la haie    y = 770   ->  0.81
    epaisseur          255 px    ->  0.27 de la hauteur
    ciel               0.54      sable  0.19

CE QUI LA DISTINGUE DE NOTRE BUISSON PRECEDENT
  Ce n'est pas un buisson, c'est une HAIE TAILLEE : une masse pleine, de
  hauteur constante d'un bord a l'autre, dont seul le bord haut frisotte.

  Et il frisotte FIN. Nos lobes faisaient 40 a 74 px de rayon - de grosses
  boules qui donnaient une frise de nuages verts. Ici les touffes font 8 a
  15 px sur 1232, soit 12 a 22 sur nos 1800 : trois a cinq fois plus petites,
  et bien plus nombreuses. C'est ce changement d'echelle, a lui seul, qui
  fait passer du buisson decoratif au feuillage.

DEUX VALEURS, ET UNE LIMITE MANGEE
  Le haut de la haie est vert clair, le bas vert sombre - la lumiere vient
  d'en haut. Mais la limite entre les deux n'est PAS une ligne : des touffes
  sombres remontent dans le clair, exactement comme des touffes claires
  depassent dans le ciel. Une limite nette y ferait deux bandes empilees.
"""

import random

CLAIR = "#57A34A"
SOMBRE = "#1D5C2B"

# LES DEUX TONS INTERMEDIAIRES, pour la mouchetures du corps.
# Ils sont PROCHES de leur fond - un ton franchement different ferait des
# confettis. Ce qu'on cherche n'est pas un motif mais une matiere : de tres
# nombreuses petites taches a peine distinctes, qui ne se lisent une a une
# qu'en s'approchant.
CLAIR_TACHE = "#3E8438"      # nettement plus sombre que CLAIR
SOMBRE_TACHE = "#39833F"     # nettement plus clair que SOMBRE

# PREMIER ESSAI RATE : des tons a peine differents de leur fond, en pensant
# qu'une matiere se fait de nuances. Resultat, rien ne se voyait - 700 taches
# invisibles. Sur la reference les taches TRANCHENT ; c'est leur petitesse et
# leur nombre qui les empechent de faire des confettis, pas leur discretion.


def frange(y, largeur, pas, rmin, rmax, saut, alea):
    u"""
    Des disques semes le long d'une horizontale.

    pas   : l'ecart moyen entre deux centres
    saut  : de combien le centre monte ou descend au hasard. Sans lui les
            sommets s'alignent et la frange redevient une reglette.
    """
    out, x = [], -rmax
    while x < largeur + rmax:
        r = alea.uniform(rmin, rmax)
        out.append((round(x, 1), round(y + alea.uniform(-saut, saut * 0.5), 1),
                    round(r, 1)))
        x += alea.uniform(pas * 0.55, pas * 1.45)
    return out


def mouchetures(y_haut, y_bas, largeur, densite, rmin, rmax, alea):
    u"""
    Des taches semees DANS la masse, et non sur son bord.

    C'EST CE QUI MANQUAIT. Le bord de notre haie frisottait deja, mais son
    corps restait deux aplats nus : de loin, deux bandes vertes. Sur la
    reference le feuillage est piquete de haut en bas - c'est ce piquetage,
    et non le grain du filtre, qui fait la matiere. Un filtre de bruit ajoute
    du GRAIN ; il n'ajoute pas de FEUILLES.

    densite : nombre de taches pour 10 000 px carres.
    """
    n = int(densite * (y_bas - y_haut) * largeur / 10000.0)
    return [(round(alea.uniform(-rmax, largeur + rmax), 1),
             round(alea.uniform(y_haut, y_bas), 1),
             round(alea.uniform(rmin, rmax), 1)) for _ in range(n)]


def _bloc(disques, y_haut, y_bas, largeur, indent):
    e = " " * indent
    out = [u'%s<rect x="0" y="%.1f" width="%d" height="%.1f"/>'
           % (e, y_haut, largeur, y_bas - y_haut)]
    out += [u'%s<circle cx="%s" cy="%s" r="%s"/>' % (e, x, y, r)
            for x, y, r in disques]
    return "\n".join(out)


def engendrer(largeur, crete, pied, indent=6, graine=7, densite=20.0):
    u"""
    crete, pied : le haut et le bas de la haie, en pixels.

    La limite entre les deux valeurs est posee au tiers de la hauteur : la
    partie eclairee est plus mince que la partie a l'ombre, sinon la haie se
    coupe en deux moities egales et perd son epaisseur.
    """
    alea = random.Random(graine)
    hauteur = pied - crete
    limite = crete + hauteur * 0.38

    # L'echelle des touffes vient du releve : 12 a 22 px sur 1800 de large.
    rmin, rmax = 0.0067 * largeur, 0.0122 * largeur
    pas = rmax * 0.62          # elles se chevauchent largement

    # DEUX RANGS PAR LIMITE, decales en hauteur et semes independamment.
    # Un seul rang, meme irregulier, garde une ligne moyenne visible : l'oeil
    # la reconstitue et la frange redevient une frise. Deux rangs qui se
    # chevauchent a des hauteurs differentes suppriment cette ligne.
    haut = (frange(crete, largeur, pas, rmin, rmax, rmax * 0.8, alea)
            + frange(crete + rmax * 0.75, largeur, pas * 1.1,
                     rmin * 0.8, rmax * 0.85, rmax * 0.9, alea))
    milieu = (frange(limite, largeur, pas * 1.05, rmin, rmax * 1.15,
                     rmax * 1.3, alea)
              + frange(limite - rmax * 1.6, largeur, pas * 2.2,
                       rmin * 0.7, rmax * 0.9, rmax * 1.6, alea))

    # Les taches du corps. Plus petites que les touffes du bord - elles ne
    # decoupent pas une silhouette, elles remplissent.
    rt_min, rt_max = rmin * 0.24, rmax * 0.34
    taches_claires = mouchetures(crete + rmax, limite, largeur,
                                 densite, rt_min, rt_max, alea)
    taches_sombres = mouchetures(limite + rmax, pied, largeur,
                                 densite * 1.35, rt_min, rt_max * 1.15, alea)

    e = " " * indent
    ee = " " * (indent + 2)
    pointer = lambda t: "\n".join(
        u'%s<circle cx="%s" cy="%s" r="%s"/>' % (ee, x, y, r) for x, y, r in t)

    return "\n".join([
        u'%s<g fill="%s">' % (e, CLAIR),
        _bloc(haut, crete, limite + 2, largeur, indent + 2),
        u'%s</g>' % e,
        u'%s<g fill="%s">' % (e, CLAIR_TACHE),
        pointer(taches_claires),
        u'%s</g>' % e,
        u'%s<g fill="%s">' % (e, SOMBRE),
        _bloc(milieu, limite, pied, largeur, indent + 2),
        u'%s</g>' % e,
        u'%s<g fill="%s">' % (e, SOMBRE_TACHE),
        pointer(taches_sombres),
        u'%s</g>' % e]), (len(haut) + len(milieu)
                          + len(taches_claires) + len(taches_sombres))


if __name__ == "__main__":
    corps, n = engendrer(1800, 729, 1091)
    print(u"haie : %d touffes" % n)
    print(u"rayons de %.0f a %.0f px" % (0.0067 * 1800, 0.0122 * 1800))
    print(u"contre 38 a 74 px pour l'ancien buisson : %.1f fois plus petites"
          % (56.0 / (0.0095 * 1800)))
