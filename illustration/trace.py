# -*- coding: utf-8 -*-
u"""
L'EPAISSEUR VARIABLE, calculee.

LE PROBLEME
  Un membre trace au trait d'epaisseur constante donne un tuyau. Dans la
  reference, les membres sont FUSELES : epais a l'attache, fins a
  l'extremite, et ils se courbent. C'est cette variation qui fait la
  souplesse ; sans elle on dessine un bonhomme en tubes.

L'OUTIL D'INKSCAPE, ET POURQUOI JE NE L'UTILISE PAS
  Inkscape sait faire exactement cela : Chemin > Effets de chemin >
  EPAISSEUR VARIABLE (Power Stroke). On y trace une courbe, on y pose des
  poignees de largeur, et il en deduit le contour. C'est le bon outil - si
  l'on dessine a la main.

  Mais un effet de chemin est un objet VIVANT de l'interface : il se regle a
  la souris et se recalcule a l'ouverture. Il ne se genere pas depuis un
  script, et notre chaine est scriptee. J'implemente donc l'algorithme, qui
  tient en quinze lignes : on echantillonne la courbe, on calcule la normale
  en chaque point, on decale de la demi-largeur de part et d'autre, et on
  referme par deux demi-cercles.

  Le resultat est un simple <path> - aucune dependance, editable partout,
  et Inkscape le rouvre comme n'importe quelle forme.
"""

import math


def _bezier(p, t):
    """Un point sur la cubique definie par quatre points de controle."""
    u = 1.0 - t
    return (u * u * u * p[0][0] + 3 * u * u * t * p[1][0]
            + 3 * u * t * t * p[2][0] + t * t * t * p[3][0],
            u * u * u * p[0][1] + 3 * u * u * t * p[1][1]
            + 3 * u * t * t * p[2][1] + t * t * t * p[3][1])


def _tangente(p, t):
    u = 1.0 - t
    dx = (3 * u * u * (p[1][0] - p[0][0]) + 6 * u * t * (p[2][0] - p[1][0])
          + 3 * t * t * (p[3][0] - p[2][0]))
    dy = (3 * u * u * (p[1][1] - p[0][1]) + 6 * u * t * (p[2][1] - p[1][1])
          + 3 * t * t * (p[3][1] - p[2][1]))
    n = math.hypot(dx, dy) or 1.0
    return dx / n, dy / n


def _largeur(profil, t):
    """Interpolation lineaire du profil de largeur, donne en (t, largeur)."""
    for i in range(len(profil) - 1):
        t0, w0 = profil[i]
        t1, w1 = profil[i + 1]
        if t0 <= t <= t1:
            k = (t - t0) / (t1 - t0) if t1 > t0 else 0.0
            return w0 + (w1 - w0) * k
    return profil[-1][1]


def fusele(controle, profil, n=26, place=lambda x, y: (x, y)):
    """
    Le contour d'un membre fusele.

    controle : quatre points, la ligne moyenne du membre
    profil   : [(t, largeur), ...], la largeur le long de cette ligne
    place    : la fonction qui amene les coordonnees locales a leur place
    """
    gauche, droite = [], []
    for i in range(n + 1):
        t = i / float(n)
        x, y = _bezier(controle, t)
        tx, ty = _tangente(controle, t)
        w = _largeur(profil, t) / 2.0
        gauche.append(place(x - ty * w, y + tx * w))
        droite.append(place(x + ty * w, y - tx * w))

    # LES CALOTTES. Je les avais faites avec des arcs A : le sens de parcours
    # depend alors de l'orientation du membre, et un arc pris a l'envers ne
    # bombe pas, il CREUSE - d'ou des encoches blanches a l'epaule et a la
    # taille. Une cubique ne pose pas ce probleme : ses points de controle
    # sont donnes dans le repere du membre, donc elle bombe toujours du bon
    # cote. Le facteur 4/3 est l'approximation classique d'un demi-cercle.
    def calotte(depart, arrivee, direction, rayon):
        c1 = (depart[0] + direction[0] * rayon * 4.0 / 3.0,
              depart[1] + direction[1] * rayon * 4.0 / 3.0)
        c2 = (arrivee[0] + direction[0] * rayon * 4.0 / 3.0,
              arrivee[1] + direction[1] * rayon * 4.0 / 3.0)
        return " C%.1f %.1f %.1f %.1f %.1f %.1f" % (c1 + c2 + arrivee)

    ech = math.hypot(place(1, 0)[0] - place(0, 0)[0],
                     place(1, 0)[1] - place(0, 0)[1]) or 1.0
    r0 = _largeur(profil, 0.0) / 2.0 * ech
    r1 = _largeur(profil, 1.0) / 2.0 * ech
    t0 = _tangente(controle, 0.0)
    t1 = _tangente(controle, 1.0)
    # les tangentes sont locales : on les amene dans le repere final
    o = place(0, 0)
    T0 = (place(*t0)[0] - o[0], place(*t0)[1] - o[1])
    T1 = (place(*t1)[0] - o[0], place(*t1)[1] - o[1])
    n0 = math.hypot(*T0) or 1.0
    n1 = math.hypot(*T1) or 1.0
    T0 = (T0[0] / n0, T0[1] / n0)
    T1 = (T1[0] / n1, T1[1] / n1)

    d = "M%.1f %.1f " % gauche[0]
    d += " ".join("L%.1f %.1f" % q for q in gauche[1:])
    d += calotte(gauche[-1], droite[-1], T1, r1)
    d += " " + " ".join("L%.1f %.1f" % q for q in reversed(droite[:-1]))
    d += calotte(droite[0], gauche[0], (-T0[0], -T0[1]), r0)
    return d + " Z"
