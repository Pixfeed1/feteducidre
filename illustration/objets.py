# -*- coding: utf-8 -*-
u"""
LA PLAGE SANS PERSONNE - l'ete raconte par les objets.

La proposition : tout le monde est parti se baigner, il reste leur
apres-midi. Un ballon qui roule encore, le seau et sa pelle plantee,
les tongs quittees en vitesse, le chapeau pose sur la serviette, et
la-haut un cerf-volant - le seul personnage de l'image est le vent.

LA FABRIQUE, tout Inkscape :
  le ballon      un cercle creme et des CROISSANTS booleens (le cercle
                 moins le meme cercle decale) - le bord du quartier est
                 le bord du ballon par construction, lecon deja payee
  le seau        trapeze terre cuite, levre en ellipse, anse en arc ;
                 la pelle plantee dedans, manche oblique
  les tongs      deux semelles goutte, brides en V
  le chapeau     la calotte par-dessus le bord en ellipse, un ruban
  le cerf-volant un losange coupe en deux par sa diagonale, la queue en
                 Catmull avec ses noeuds
  les ombres     des ellipses olive (OMBRE_SOL), le sol qui les recoit
"""

import math

import booleen as B

TERRE_CUITE = "#C05A35"
TERRE_SOMBRE = "#9A4526"
CREME = "#F2ECD9"
ROUGE = "#D8402E"
VERT = "#3F8A52"
VERT_SOMBRE = "#1D5C2B"
PAILLE = "#E8D9A8"
PAILLE_OMBRE = "#CDb684".upper()
OMBRE_SOL = "#CBC6A6"


def _catmull_ferme(points):
    n = len(points)
    p = list(points)
    d = u"M%.1f %.1f" % p[0]
    for i in range(n):
        p0, p1, p2, p3 = p[(i-1) % n], p[i], p[(i+1) % n], p[(i+2) % n]
        c1 = (p1[0]+(p2[0]-p0[0])/6., p1[1]+(p2[1]-p0[1])/6.)
        c2 = (p2[0]-(p3[0]-p1[0])/6., p2[1]-(p3[1]-p1[1])/6.)
        d += u" C%.1f %.1f %.1f %.1f %.1f %.1f" % (c1+c2+p2)
    return d + " Z"


def _catmull_ouvert(points):
    p = [points[0]] + list(points) + [points[-1]]
    d = u"M%.1f %.1f" % p[1]
    for i in range(1, len(p) - 2):
        c1 = (p[i][0]+(p[i+1][0]-p[i-1][0])/6., p[i][1]+(p[i+1][1]-p[i-1][1])/6.)
        c2 = (p[i+1][0]-(p[i+2][0]-p[i][0])/6., p[i+1][1]-(p[i+2][1]-p[i][1])/6.)
        d += u" C%.1f %.1f %.1f %.1f %.1f %.1f" % (c1+c2+p[i+1])
    return d


def ombre(cx, cy, rx, ry, op=0.5):
    return (u'<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s"'
            u' opacity="%.2f"/>' % (cx, cy, rx, ry, OMBRE_SOL, op))


def ballon(cx, cy, r, indent=2):
    u"""Le ballon en croissants booleens, pose sur son ombre."""
    e = " " * indent
    balle = B.ellipse(cx, cy, r, r)
    croissant_g = B.difference(balle, B.ellipse(cx - r * 0.52, cy, r * 1.02,
                                                r * 1.10))
    croissant_d = B.difference(balle, B.ellipse(cx + r * 0.52, cy, r * 1.02,
                                                r * 1.10))
    out = [ombre(cx + r * 0.25, cy + r * 0.98, r * 1.15, r * 0.26),
           u'<path d="%s" fill="%s"/>' % (balle, CREME),
           u'<path d="%s" fill="%s"/>' % (croissant_g, ROUGE),
           u'<path d="%s" fill="%s"/>' % (croissant_d, VERT)]
    return u"\n".join(u"%s%s" % (e, x) for x in out)


def seau(cx, cy, h, indent=2):
    u"""
    Le seau pose, la pelle plantee dedans. (cx, cy) : le milieu du fond.
    Le corps est un trapeze aux flancs presque droits ; la levre est une
    ellipse vue d'un peu au-dessus, comme le rebord des parasols.
    """
    e = " " * indent
    r_haut = h * 0.62
    r_bas = h * 0.46
    ry = r_haut * 0.30
    yh = cy - h

    # la PELLE d'abord : plantee dans le seau, elle passe derriere la levre.
    # COUCHEE a 55 degres : dressee, son manche vert sombre montait dans la
    # haie vert sombre et n'existait plus - sur le sable, il se lit
    ang = math.radians(-55)
    lx, ly = math.sin(ang), -math.cos(ang)
    x0, y0 = cx + r_haut * 0.1, yh + ry * 0.2
    manche = h * 1.30
    xm, ym = x0 + lx * manche, y0 + ly * manche
    pelle = [u'<path d="M%.1f %.1f L%.1f %.1f" stroke="%s" stroke-width="%.1f"'
             u' stroke-linecap="round"/>' % (x0, y0, xm, ym, VERT_SOMBRE,
                                             h * 0.10),
             # la poignee en anneau
             u'<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s"'
             u' stroke-width="%.1f"/>' % (xm + lx * h * 0.10,
                                          ym + ly * h * 0.10, h * 0.14,
                                          VERT_SOMBRE, h * 0.09)]

    corps = (u'M%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f Z'
             % (cx - r_haut, yh, cx + r_haut, yh,
                cx + r_bas, cy, cx - r_bas, cy))
    levre = (u'<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s"/>'
             % (cx, yh, r_haut, ry, TERRE_SOMBRE))

    out = [ombre(cx + r_haut * 0.35, cy + 2, r_haut * 1.35, ry * 0.9)]
    out += pelle
    out += [u'<path d="%s" fill="%s"/>' % (corps, TERRE_CUITE), levre]
    # L'ANSE, tombee sur le flanc : c'est elle qui dit "seau" et pas
    # "pot de fleurs" - un arc du bord gauche au bord droit, couche
    out.append(u'<path d="M%.1f %.1f C%.1f %.1f %.1f %.1f %.1f %.1f"'
               u' stroke="%s" stroke-width="%.1f" fill="none"'
               u' stroke-linecap="round"/>'
               % (cx - r_haut * 0.92, yh + ry * 0.4,
                  cx - r_haut * 1.55, yh + h * 0.55,
                  cx - r_haut * 0.9, cy + 2,
                  cx + r_haut * 0.2, cy + ry * 0.5,
                  TERRE_SOMBRE, h * 0.07))
    return u"\n".join(u"%s%s" % (e, x) for x in out)


def tongs(cx, cy, l, ecart=None, indent=2):
    u"""
    Les deux tongs quittees en vitesse : jamais paralleles - l'une part
    de travers, c'est le desordre qui raconte le depart.
    """
    e = " " * indent
    if ecart is None:
        ecart = l * 0.75
    out = [ombre(cx + ecart * 0.5, cy + 3, l * 1.35, l * 0.30, 0.45)]
    for dx, ang, sens in ((0.0, -14.0, 1), (ecart, 22.0, -1)):
        a = math.radians(ang)
        ca, sa = math.cos(a), math.sin(a)
        x0, y0 = cx + dx, cy

        def T(px, py):
            return (x0 + px * ca - py * sa, y0 + px * sa + py * ca)
        # la semelle : une goutte (large a l'avant, etroite au talon)
        w = l * 0.42
        pts = [T(0, -l * 0.5), T(w * 0.5, -l * 0.28), T(w * 0.52, l * 0.05),
               T(w * 0.34, l * 0.46), T(-w * 0.34, l * 0.46),
               T(-w * 0.52, l * 0.05), T(-w * 0.5, -l * 0.28)]
        out.append(u'<path d="%s" fill="%s"/>' % (_catmull_ferme(pts), PAILLE))
        # la bride en V, du milieu vers les deux bords
        m = T(0, -l * 0.12)
        b1 = T(-w * 0.46 * sens, l * 0.16)
        b2 = T(w * 0.40 * sens, l * 0.22)
        for bx in (b1, b2):
            out.append(u'<path d="M%.1f %.1f L%.1f %.1f" stroke="%s"'
                       u' stroke-width="%.1f" stroke-linecap="round"/>'
                       % (m[0], m[1], bx[0], bx[1], ROUGE, l * 0.09))
    return u"\n".join(u"%s%s" % (e, x) for x in out)


def chapeau(cx, cy, r, indent=2):
    u"""
    Le chapeau de paille pose a plat : le bord est une grande ellipse, la
    calotte une plus petite par-dessus, le ruban entre les deux. Vu de
    haut et d'un peu de cote, comme tout le sol de la scene.
    """
    e = " " * indent
    out = [ombre(cx + r * 0.30, cy + r * 0.42, r * 1.15, r * 0.34, 0.45),
           u'<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s"/>'
           % (cx, cy, r, r * 0.46, PAILLE),
           u'<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s"/>'
           % (cx, cy - r * 0.10, r * 0.58, r * 0.30, PAILLE_OMBRE),
           u'<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s"/>'
           % (cx, cy - r * 0.16, r * 0.54, r * 0.26, VERT_SOMBRE),
           u'<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s"/>'
           % (cx, cy - r * 0.22, r * 0.50, r * 0.22, PAILLE)]
    return u"\n".join(u"%s%s" % (e, x) for x in out)


def cerf_volant(cx, cy, t, indent=2):
    u"""
    Le cerf-volant : un losange coupe par sa diagonale - une moitie rouge,
    une moitie creme - deux barres fines en croix, et la queue qui
    serpente avec ses noeuds. Le seul personnage de l'image est le vent.
    """
    e = " " * indent
    # le losange, un peu penche
    a = math.radians(18)
    ca, sa = math.cos(a), math.sin(a)

    def T(px, py):
        return (cx + px * ca - py * sa, cy + px * sa + py * ca)
    haut, bas = T(0, -t), T(0, t * 1.25)
    gauche, droite = T(-t * 0.72, 0), T(t * 0.72, 0)
    out = [u'<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s"/>'
           % (haut + gauche + bas + (CREME,)),
           u'<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s"/>'
           % (haut + droite + bas + (ROUGE,)),
           u'<path d="M%.1f %.1f L%.1f %.1f M%.1f %.1f L%.1f %.1f"'
           u' stroke="%s" stroke-width="1.6" fill="none"/>'
           % (haut + bas + gauche + droite + (VERT_SOMBRE,))]
    # LA QUEUE : elle part de la pointe basse et serpente sous le vent
    q = [bas]
    for i in range(1, 6):
        s = i / 5.0
        q.append((bas[0] - t * (0.5 + 2.6 * s) * sa - t * 2.2 * s * 0.55,
                  bas[1] + t * (0.9 + 2.4 * s) * ca * 0.55
                  + t * 0.5 * math.sin(s * 6.0)))
    out.append(u'<path d="%s" stroke="%s" stroke-width="1.8" fill="none"/>'
               % (_catmull_ouvert(q), VERT_SOMBRE))
    # les noeuds de la queue : des petits papillons
    for i in (1, 2, 3, 4):
        nx, ny = q[i]
        out.append(u'<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f Z"'
                   u' fill="%s"/>'
                   % (nx - 6, ny - 4, nx + 6, ny + 4, nx + 6, ny - 4,
                      nx - 6, ny + 4, ROUGE if i % 2 else VERT))
    return u"\n".join(u"%s%s" % (e, x) for x in out)
