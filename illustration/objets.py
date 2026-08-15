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
    Le seau du bac a sable, travaille comme le reste de la scene :

      DEUX TONS      la panse a sa face eclairee et sa face a l'ombre,
                     separees par une couture courbe - exactement le
                     vocabulaire des fuseaux du parasol ;
      DES COURBES    les flancs bombent legerement, le cul est une
                     ellipse - aucune ligne droite, un seau est souffle ;
      LA MATIERE     la levre roulee (deux ellipses), l'interieur sombre,
                     la moulure sous la levre, le reflet du bord ;
      CE QUI LE NOMME l'anse tombee sur le flanc avec ses deux oreilles,
                     la pelle plantee dont l'anneau se detache sur le
                     sable, et le sable remue a son pied.
    """
    e = " " * indent
    rh = h * 0.60                 # demi-largeur en haut
    rb = h * 0.46                 # demi-largeur au cul
    ry = rh * 0.26                # l'aplat de l'ellipse de la levre
    yh = cy - h
    CLAIR = "#CE6B3E"
    SOMBRE_P = "#A34B28"
    INTERIEUR = "#7E3A20"

    out = [ombre(cx + rh * 0.45, cy + 2, rh * 1.45, ry * 0.95)]

    # LA PELLE d'abord (elle passe derriere la levre) : manche couche vers
    # le sable - dresse, il se perdait dans la haie - anneau, et un
    # COLLET plus large la ou le manche plonge dans le seau.
    ang = math.radians(-60)      # couche un peu plus : l'anneau restait
    lx, ly = math.sin(ang), -math.cos(ang)   # a froler la haie
    x0, y0 = cx + rh * 0.12, yh + ry * 0.1
    xm, ym = x0 + lx * h * 1.18, y0 + ly * h * 1.18
    out += [u'<path d="M%.1f %.1f L%.1f %.1f" stroke="%s" stroke-width="%.1f"'
            u' stroke-linecap="round"/>' % (x0, y0, xm, ym, VERT_SOMBRE,
                                            h * 0.105),
            u'<path d="M%.1f %.1f L%.1f %.1f" stroke="%s" stroke-width="%.1f"'
            u' stroke-linecap="round"/>'
            % (x0 - lx * h * 0.06, y0 - ly * h * 0.06,
               x0 + lx * h * 0.16, y0 + ly * h * 0.16, VERT_SOMBRE, h * 0.17),
            u'<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s"'
            u' stroke-width="%.1f"/>' % (xm + lx * h * 0.13,
                                         ym + ly * h * 0.13, h * 0.15,
                                         VERT_SOMBRE, h * 0.095)]

    # LA PANSE : les flancs bombent (controles pousses dehors), le cul est
    # une ellipse - puis la face A L'OMBRE, une couture courbe comme un
    # meridien de parasol.
    panse = (u'M%.1f %.1f C%.1f %.1f %.1f %.1f %.1f %.1f '
             u'Q%.1f %.1f %.1f %.1f C%.1f %.1f %.1f %.1f %.1f %.1f Z'
             % (cx - rh, yh,
                cx - rh * 1.04, yh + h * 0.45, cx - rb * 1.06, cy - h * 0.18,
                cx - rb, cy,
                cx, cy + h * 0.075, cx + rb, cy,
                cx + rb * 1.06, cy - h * 0.18, cx + rh * 1.04, yh + h * 0.45,
                cx + rh, yh))
    out.append(u'<path d="%s" fill="%s"/>' % (panse, CLAIR))
    flanc_ombre = (u'M%.1f %.1f C%.1f %.1f %.1f %.1f %.1f %.1f '
                   u'Q%.1f %.1f %.1f %.1f C%.1f %.1f %.1f %.1f %.1f %.1f Z'
                   % (cx + rh * 0.22, yh,
                      cx + rh * 0.02, yh + h * 0.4, cx + rb * 0.05,
                      cy - h * 0.15, cx + rb * 0.14, cy + h * 0.02,
                      cx + rb * 0.6, cy + h * 0.055, cx + rb, cy,
                      cx + rb * 1.06, cy - h * 0.18, cx + rh * 1.04,
                      yh + h * 0.45, cx + rh, yh))
    out.append(u'<path d="%s" fill="%s"/>' % (flanc_ombre, SOMBRE_P))
    # LA MOULURE sous la levre : le petit bourrelet des seaux moules -
    # un arc qui suit la courbure de l'ellipse, cote face seulement
    ym0 = yh + h * 0.15
    out.append(u'<path d="M%.1f %.1f Q%.1f %.1f %.1f %.1f" stroke="%s"'
               u' stroke-width="%.1f" fill="none" opacity="0.5"/>'
               % (cx - rh * 0.94, ym0, cx, ym0 + ry * 1.5,
                  cx + rh * 0.94, ym0, SOMBRE_P, h * 0.045))

    # LA LEVRE ROULEE : l'ellipse exterieure, l'interieur sombre, et le
    # reflet du bord avant - c'est lui qui fait le plastique
    out += [u'<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s"/>'
            % (cx, yh, rh * 1.06, ry * 1.15, SOMBRE_P),
            u'<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s"/>'
            % (cx, yh - ry * 0.12, rh * 0.88, ry * 0.82, INTERIEUR),
            u'<path d="M%.1f %.1f Q%.1f %.1f %.1f %.1f" stroke="%s"'
            u' stroke-width="%.1f" fill="none" opacity="0.85"/>'
            % (cx - rh * 0.9, yh + ry * 0.4, cx, yh + ry * 1.75,
               cx + rh * 0.9, yh + ry * 0.4, "#E8935F", h * 0.05)]

    # L'ANSE tombee, avec ses deux OREILLES aux flancs
    out += [u'<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>'
            % (cx - rh * 1.0, yh + ry * 0.5, h * 0.075, SOMBRE_P),
            u'<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>'
            % (cx + rh * 1.0, yh + ry * 0.5, h * 0.075, SOMBRE_P),
            u'<path d="M%.1f %.1f C%.1f %.1f %.1f %.1f %.1f %.1f"'
            u' stroke="%s" stroke-width="%.1f" fill="none"'
            u' stroke-linecap="round"/>'
            % (cx - rh * 1.0, yh + ry * 0.5,
               cx - rh * 1.75, yh + h * 0.6,
               cx - rh * 1.15, cy + ry * 1.1,
               cx + rh * 0.15, cy + ry * 0.75,
               TERRE_SOMBRE, h * 0.075),
            # le reflet de l'anse
            u'<path d="M%.1f %.1f C%.1f %.1f %.1f %.1f %.1f %.1f"'
            u' stroke="%s" stroke-width="%.1f" fill="none" opacity="0.6"'
            u' stroke-linecap="round"/>'
            % (cx - rh * 1.02, yh + ry * 0.7,
               cx - rh * 1.6, yh + h * 0.62,
               cx - rh * 1.1, cy + ry * 0.75,
               cx - rh * 0.2, cy + ry * 0.55,
               "#E8935F", h * 0.028)]

    # (les tas de sable remue lisaient comme du lait renverse - retires :
    # l'ombre au sol suffit a poser l'objet)
    return u"\n".join(u"%s%s" % (e, x) for x in out)


def tongs(cx, cy, l, ecart=None, indent=2):
    u"""
    Les claquettes quittees en vitesse - jamais paralleles, l'une chevauche
    presque l'autre. Travaillees comme des objets, pas des symboles :

      L'EPAISSEUR    chaque semelle a sa TRANCHE (la meme forme decalee
                     vers le bas, un ton plus sombre) - sans elle la
                     claquette est peinte sur le sable, pas posee dessus ;
      L'EMPREINTE    le lit de pied, une forme interieure plus claire -
                     la trace du pied qui l'a portee tout l'ete ;
      LA BRIDE       un vrai Y PLEIN : deux lanieres effilees qui se
                     rejoignent au teton d'orteil, et leur ombre fine
                     sur la semelle.
    """
    e = " " * indent
    if ecart is None:
        ecart = l * 0.80
    out = [ombre(cx + ecart * 0.5, cy + 4, l * 1.30, l * 0.30, 0.45)]

    def semelle(x0, y0, ang, sens):
        a = math.radians(ang)
        ca, sa = math.cos(a), math.sin(a)

        def T(px, py):
            return (x0 + px * ca - py * sa, y0 + px * sa + py * ca)
        w = l * 0.46
        forme = [T(0, -l * 0.52), T(w * 0.52, -l * 0.30), T(w * 0.55, l * 0.02),
                 T(w * 0.40, l * 0.44), T(0, l * 0.52),
                 T(-w * 0.40, l * 0.44), T(-w * 0.55, l * 0.02),
                 T(-w * 0.52, -l * 0.30)]
        morceaux = []
        # LA TRANCHE : la meme forme, 3 px plus bas, un ton plus sombre
        tranche = [(px, py + l * 0.09) for (px, py) in forme]
        morceaux.append(u'<path d="%s" fill="%s"/>'
                        % (_catmull_ferme(tranche), "#B89B62"))
        # LE DESSUS
        morceaux.append(u'<path d="%s" fill="%s"/>'
                        % (_catmull_ferme(forme), PAILLE))
        # L'EMPREINTE du pied : la forme interieure, plus claire
        dedans = [T(0, -l * 0.36), T(w * 0.33, -l * 0.18),
                  T(w * 0.36, l * 0.06), T(w * 0.26, l * 0.33),
                  T(0, l * 0.40), T(-w * 0.26, l * 0.33),
                  T(-w * 0.36, l * 0.06), T(-w * 0.33, -l * 0.18)]
        morceaux.append(u'<path d="%s" fill="%s" opacity="0.65"/>'
                        % (_catmull_ferme(dedans), "#F2E7C2"))
        # LA BRIDE en Y plein : l'ombre d'abord, puis les deux lanieres
        # effilees vers le teton, et le teton d'orteil
        teton = T(0, -l * 0.16)
        for cote in (-1, 1):
            attache = T(cote * w * 0.50, l * 0.14)
            milieu = T(cote * w * 0.30, l * 0.015 - 0.04 * l)
            morceaux.append(u'<path d="M%.1f %.1f Q%.1f %.1f %.1f %.1f"'
                            u' stroke="%s" stroke-width="%.1f" fill="none"'
                            u' opacity="0.35"/>'
                            % (teton[0] + 1.2, teton[1] + 2.2,
                               milieu[0] + 1.2, milieu[1] + 2.4,
                               attache[0] + 0.8, attache[1] + 1.6,
                               "#8A7B4E", l * 0.075))
            morceaux.append(u'<path d="M%.1f %.1f Q%.1f %.1f %.1f %.1f"'
                            u' stroke="%s" stroke-width="%.1f" fill="none"'
                            u' stroke-linecap="round"/>'
                            % (teton[0], teton[1], milieu[0], milieu[1],
                               attache[0], attache[1], ROUGE, l * 0.085))
        morceaux.append(u'<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>'
                        % (teton[0], teton[1], l * 0.055, ROUGE))
        return morceaux

    # la premiere bien posee, la seconde de travers qui la chevauche presque
    out += semelle(cx, cy, -12.0, 1)
    out += semelle(cx + ecart, cy - l * 0.10, 27.0, -1)
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


def cerf_volant(cx, cy, t, indent=2, phase=None):
    u"""
    Le cerf-volant : un losange coupe par sa diagonale - une moitie rouge,
    une moitie creme - deux barres fines en croix, et la queue qui
    serpente avec ses noeuds. Le seul personnage de l'image est le vent.
    """
    e = " " * indent
    # le losange, un peu penche - et s'il est anime, il se BALANCE :
    # l'angle respire de +/-6 degres, periodique en phase (la boucle
    # revient exactement sur elle-meme)
    bal = 6.0 * math.sin(2 * math.pi * phase + 0.9) if phase is not None \
        else 0.0
    a = math.radians(18 + bal)
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
                  + t * 0.5 * math.sin(s * 6.0
                  - (2 * math.pi * 2 * phase if phase is not None
                     else 0.0))))
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
