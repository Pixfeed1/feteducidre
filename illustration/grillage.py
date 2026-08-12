# -*- coding: utf-8 -*-
u"""
Le grillage, en perspective a un point de fuite - une vraie projection, pas
un motif plaque.

POURQUOI UN MOTIF NE PEUT PAS MARCHER
  Un <pattern> SVG se repete a pas constant. Or en perspective, des poteaux
  regulierement espaces dans le monde ne le sont PAS a l'ecran : leur ecart
  decroit comme 1/z. Un motif donne donc toujours une cloture vue de face,
  quel que soit le soin qu'on y met. Le probleme est arithmetique, pas
  graphique.

LA PROJECTION
  Un point de la cloture est repere par (u, v) : u = distance le long de la
  cloture, comptee en ecarts de poteaux ; v = hauteur, 0 en bas, 1 en haut.
  Tout le reste decoule d'un seul facteur d'echelle :

      s(u) = 1 / (1 + RECUL . u)

  C'est la decroissance en 1/z de la perspective. On l'applique aux deux
  coordonnees depuis le point de fuite :

      x = xf + (x0 - xf) . s(u)
      y = yf + (y0 - yf) . s(u)          avec y0 pris a la hauteur v

  Consequences, et ce sont elles qu'on voulait :
    - les poteaux se resserrent vers la droite, de plus en plus vite ;
    - la cloture RAPETISSE en s'eloignant, haut et bas convergeant tous deux
      vers l'horizon ;
    - les fils du treillis, qui sont des droites dans le plan de la cloture,
      restent des droites a l'ecran - c'est une propriete de la projection
      perspective, donc on peut les tracer par leurs deux extremites.

LE TREILLIS
  Deux familles de fils a 45 degres dans le plan de la cloture : les uns
  montent vers la droite, les autres vers la gauche. Chacun va du pied au
  sommet, donc d'un point (a, 0) a un point (a +/- HAUTEUR_MONDE, 1). Leur
  espacement se resserre a l'ecran exactement comme les poteaux, sans qu'on
  ait a s'en occuper : c'est la projection qui le fait.
"""

import perspective as P

LARGEUR = P.LARGEUR

# Le pied et le sommet de la cloture AU PLUS PRES du spectateur. Le pied est
# donne un peu plus haut que celui du buisson (990) : la cloture est donc
# DERRIERE lui, et c'est le buisson qui masquera son pied.
Y_BAS0, Y_HAUT0 = 946.0, 60.0

# LA MAILLE, DEDUITE ET NON CODEE EN DUR.
# Je l'avais reglee en unites du monde, valeurs trouvees a l'oeil pour la
# perspective. En passant en vue de face elles sont restees telles quelles, et
# les losanges se sont etires : l'ecart entre poteaux avait change de 254 a
# 148 px, mais pas la pente des fils. Un reglage juste dans un mode est faux
# dans l'autre.
# On declare donc ce qu'on veut A L'ECRAN - des fils a 45 degres, des mailles
# d'une cinquantaine de pixels - et on convertit. Les deux modes deviennent
# justes tout seuls.
MAILLE_PX = 108.0        # cote d'une maille, en pixels, au plus pres
U_MAX = 70               # on s'arrete bien avant, quand ca devient illisible


def _ecart_px():
    """L'ecart entre deux poteaux a l'ecran, au plus pres du spectateur."""
    return projeter(1.0, 0.0)[0] - projeter(0.0, 0.0)[0]


def _reglages_maille():
    ecart = _ecart_px()
    hauteur = Y_BAS0 - Y_HAUT0
    return hauteur / ecart, MAILLE_PX / ecart   # pente a 45 deg, pas


HAUTEUR_MONDE, MAILLE = None, None   # calcules au premier appel

# LE GRILLAGE EST UN FOND, et il faut le traiter comme tel.
# Il a commence noir plein, poteaux de 13 px, opacite 0.90 : il passait
# devant la scene. Une premiere passe l'a mis a 0.52 - encore trop, l'oeil
# s'y accrochait toujours. On reste dans le NOIR, mais tres attenue : a 0.30
# les poteaux se lisent comme un gris moyen, presents sans appeler. Le
# treillis, lui, ne doit etre qu'un voile.
NOIR = "#14181C"
LARGEUR_POTEAU = 7.0
OPACITE_POTEAUX = 0.30
OPACITE_TREILLIS = 0.11
EPAISSEUR_FIL = 1.2


def echelle(u):
    return P.echelle(u)


def projeter(u, v):
    """(distance le long de la cloture, hauteur 0..1) -> (x, y) a l'ecran."""
    return P.projeter(u, Y_BAS0 + v * (Y_HAUT0 - Y_BAS0))


def dedans(p):
    return -80 <= p[0] <= LARGEUR + 80


def couper(a, b):
    """Garde le morceau de segment visible ; rend None s'il ne l'est pas."""
    if not dedans(a) and not dedans(b):
        return None
    return (a, b)


def engendrer(indent=4):
    e = " " * indent
    poteaux, fils, lisses = [], [], []

    # ---- les poteaux ----------------------------------------------------
    u = 0.0
    precedent = None
    while u <= U_MAX:
        bas, haut = projeter(u, 0.0), projeter(u, 1.0)
        largeur = LARGEUR_POTEAU * echelle(u)
        # on cesse de dessiner quand deux poteaux se touchent : au-dela ce
        # n'est plus une cloture, c'est un aplat gris
        if precedent is not None and abs(bas[0] - precedent) < largeur * 1.6:
            break
        if dedans(bas):
            poteaux.append(
                u'%s<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f"/>'
                % (e, bas[0] - largeur / 2, haut[1], largeur, bas[1] - haut[1]))
        precedent = bas[0]
        u += 1.0
    dernier_u = u

    # ---- les lisses horizontales ---------------------------------------
    # Ce sont des droites du plan, donc des droites a l'ecran : deux points
    # suffisent. Leur epaisseur, elle, ne peut pas varier le long d'un trait
    # en SVG - on prend celle du milieu, l'ecart ne se voit pas.
    for v, ep in ((1.0, 5.0), (0.46, 3.2)):
        a, b = projeter(0.0, v), projeter(dernier_u, v)
        lisses.append(u'%s<path d="M%.1f %.1f L%.1f %.1f" stroke-width="%.1f"/>'
                      % (e, a[0], a[1], b[0], b[1], ep * 0.7))

    # ---- le treillis ----------------------------------------------------
    hauteur_monde, maille = _reglages_maille()
    a = -hauteur_monde
    while a <= dernier_u + hauteur_monde:
        for sens in (+1, -1):
            p, q = projeter(a, 0.0), projeter(a + sens * hauteur_monde, 1.0)
            if couper(p, q):
                fils.append(u'%s<path d="M%.1f %.1f L%.1f %.1f"/>'
                            % (e, p[0], p[1], q[0], q[1]))
        a += maille

    return poteaux, lisses, fils, dernier_u


def bloc(indent=4):
    """Le fragment SVG complet du grillage, pret a etre insere."""
    poteaux, lisses, fils, dernier = engendrer(indent + 4)
    e = " " * indent
    morceaux = [
        u'%s<g inkscape:groupmode="layer" inkscape:label="03 Treillis" id="palierT">' % e,
        u'%s  <g stroke="%s" stroke-width="%.1f" fill="none" opacity="%.2f">'
        % (e, NOIR, EPAISSEUR_FIL, OPACITE_TREILLIS),
        u"\n".join(fils),
        u'%s  </g>' % e,
        u'%s</g>' % e,
        u'',
        u'%s<g inkscape:groupmode="layer" inkscape:label="04 Poteaux" id="palierP">' % e,
        u'%s  <g stroke="%s" fill="none" opacity="%.2f">' % (e, NOIR, OPACITE_POTEAUX),
        u"\n".join(lisses),
        u'%s  </g>' % e,
        u'%s  <g fill="%s" opacity="%.2f">' % (e, NOIR, OPACITE_POTEAUX),
        u"\n".join(poteaux),
        u'%s  </g>' % e,
        u'%s</g>' % e,
    ]
    return u"\n".join(morceaux), len(poteaux), len(fils), dernier


if __name__ == "__main__":
    corps, np_, nf, dernier = bloc()
    print(u"grillage : %d poteaux, %d fils, fuite jusqu'a u=%.0f" %
          (np_, nf, dernier))
    hm, ma = _reglages_maille()
    import math
    print(u"  ecart entre poteaux : %.0f px" % _ecart_px())
    print(u"  fil : pente %.0f degres, maille %.0f px" %
          (math.degrees(math.atan2(Y_BAS0 - Y_HAUT0, hm * _ecart_px())),
           ma * _ecart_px()))
    for u in (0, 3, 6, 10, 15):
        b, h = projeter(u, 0.0), projeter(u, 1.0)
        print(u"  poteau %2d : x=%7.1f   hauteur %5.1f" % (u, b[0], b[1] - h[1]))
