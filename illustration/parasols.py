# -*- coding: utf-8 -*-
u"""
Les parasols de plage.

MES DEUX PREMIERES VERSIONS, ET POURQUOI ELLES SONNAIENT FAUX
  1. Des EVENTAILS : des secteurs partant du milieu du bord bas, tous de meme
     ouverture. Une coupole n'a pas de secteurs, elle a des fuseaux.
  2. Des COUPOLES posees a meme le sable, bord bas rectiligne. Deux erreurs,
     et la seconde est la plus grave : un parasol n'a pas de bord droit. Sa
     toile PEND entre les baleines, et c'est ce feston qui le rend
     reconnaissable au premier coup d'oeil. Sans lui on dessine une tente, un
     igloo, une soucoupe - jamais un parasol. Et sans pied, l'objet flotte.

CE QUI FAIT UN PARASOL, DANS L'ORDRE D'IMPORTANCE
  a) le FESTON du bord bas - la toile qui pend entre les baleines ;
  b) le PIED, qui le plante dans le sable au lieu de l'y poser ;
  c) l'INCLINAISON, qui le sort de la vue de face ;
  d) l'espacement des fuseaux, reparti en azimut et non en largeur ;
  e) l'embout au sommet.

L'INCLINAISON : UN MAT DROIT, PENCHE D'UN BLOC
  J'avais d'abord mis une CHARNIERE a mi-hauteur, en imitant le vrai
  mecanisme des parasols de plage : mat bas vertical, partie haute basculee.
  C'est juste techniquement et faux graphiquement - a cette echelle le mat ne
  se lit plus comme incline mais comme PLIE EN DEUX, cassé. Un objet dessine
  doit rester lisible avant d'etre exact.

  Le parasol penche donc d'un seul tenant, autour de son point d'ancrage dans
  le sable. Le mat reste rigoureusement droit. Les deux penchent d'angles
  differents et en sens contraire : c'est ce qui leur donne du relief sans
  introduire de vraie perspective, qui jurerait avec le reste.

  LA ROTATION EST CALCULEE, PAS DELEGUEE. Un transform="rotate(...)" aurait
  ete plus court, mais le grain applique DANS un groupe tourne se calcule dans
  l'espace tourne : Inkscape le rend alors par bandes, et de fines rayures
  horizontales traversent la toile. On fait donc tourner les coordonnees
  elles-memes. Les arcs d'ellipse suivent sans peine : une ellipse tournee
  reste une ellipse de memes demi-axes, il suffit de renseigner l'angle dans
  le parametre x-axis-rotation du parametre A.

L'ESPACEMENT DES FUSEAUX
  Les coutures sont regulierement reparties en AZIMUT : celle a l'azimut phi
  tombe sur le bord en x = cx + rx.sin(phi). Le sinus fait le travail - larges
  au centre, de plus en plus etroites vers les cotes. C'est ce resserrement
  qui donne le volume ; a largeurs egales on obtient une roue de loterie.

LA FORME D'UN FUSEAU
  Le feston en bas, puis deux arcs d'ellipse jusqu'au sommet. Une couture est
  un demi-meridien du dome, et un meridien se projette en arc d'ellipse : meme
  demi-hauteur que la coupole, mais demi-largeur |x - cx|, celle de son propre
  plan. Avec des segments droits on obtient un cone.

  La fleche du feston est proportionnelle a la largeur du fuseau : les fuseaux
  du centre, vus de face, pendent franchement ; ceux des bords, vus par la
  tranche, sont presque plats. C'est la meme raison qui commande les deux.
"""

import math

VERT = "#2F9E52"
VERT_SOMBRE = "#22753A"
BLANC = "#FBFCFA"
BLANC_SOMBRE = "#DCE4D8"
PIED = "#1B2026"
OMBRE = "#EDEBE0"

# (nom, cx, cy, demi-largeur, demi-hauteur, fuseaux, decalage, longueur du
#  pied, inclinaison en degres)
# Deux seulement, de tailles et de phases differentes : deux parasols
# identiques cote a cote se lisent comme un motif, pas comme deux objets.
# LA FORME EST CELLE DU MODELE : un eventail, pas une coupole. Voir
# un_eventail() plus bas et METHODE.md pour le releve des mesures.
#
# (nom, x du milieu du bord droit, y de ce point, rayon, secteurs,
#  inclinaison en degres)
# Les deux penchent en sens contraire et n'ont ni la meme taille ni le meme
# nombre de secteurs : deux exemplaires identiques cote a cote se lisent
# comme un motif, pas comme deux objets. Tous deux gardent un nombre IMPAIR,
# qui met la couleur pleine aux deux extremites - c'est ce que fait la
# reference.
# UN SEUL. Le second, a droite, encadrait la scene de facon trop reguliere -
# deux parasols de part et d'autre de l'enfant font une composition en
# balance, et le modele ne fait pas cela : son parasol est seul, planté dans
# un coin, et c'est le vide autour de lui qui fait la plage.
# LA PLACE, relevee sur le modele et donnee en fractions du cadre.
#   ancrage du mat   (80, 237) sur 760   ->  0.105 de large, 0.312 de haut
#   rayon            67 / 760            ->  0.088 de la largeur
# L'ancrage tombe JUSTE SOUS L'HORIZON : le parasol est plante au fond de la
# plage, et sa toile monte donc DANS LE CIEL. C'est ce qui la rend lisible -
# le blanc de ses secteurs se detache sur le bleu, alors qu'il disparait sur
# le sable. Rien de tout cela ne tient si on le pose au premier plan.
#
# (nom, x du milieu du bord droit, y de ce point, rayon, secteurs, inclinaison)
# Le point donne est le HAUT du mat ; l'ancrage est 0.95 rayon plus bas.
# AVEC LA HAIE, le parasol change de place : il est plante DANS LE SABLE,
# devant la haie, et son mat est assez long pour que la toile passe au-dessus
# d'elle. Releve sur la seconde reference :
#   pied du mat      y = 840 sur 953   ->  0.88 de la hauteur
#   centre de toile  y = 500           ->  0.52
#   longueur du mat  340 px            ->  0.36 de la hauteur
# Le mat vaut donc pres de TROIS FOIS le rayon, la ou il en valait 0.95 :
# un parasol plante au premier plan devant une haie n'a rien a voir avec un
# parasol pose au fond d'une plage vide.
_RAYON = 0.088 * 1800
_ANCRE = 0.87 * 1350
_MAT = 0.36 * 1350
PARASOLS = [
    ("Parasol", 0.20 * 1800, _ANCRE - _MAT, _RAYON, 5, -22.0, _MAT / _RAYON),
]


def tourner(p, centre, angle):
    """Un point, pivote autour de la charniere."""
    a = math.radians(angle)
    dx, dy = p[0] - centre[0], p[1] - centre[1]
    return (centre[0] + dx * math.cos(a) - dy * math.sin(a),
            centre[1] + dx * math.sin(a) + dy * math.cos(a))


def cubiques(centre, U, V, th1, th2, place, morceaux=2):
    u"""
    Un arc d'ellipse QUELCONQUE, rendu en cubiques exactes.

    L'ellipse est donnee sous sa forme vectorielle P(t) = centre + U.cos(t)
    + V.sin(t). Cette forme accepte les ellipses inclinees, ce dont on a
    besoin ici : un meridien de la coupole n'est pas droit quand le bord bas
    est bombe.

    POURQUOI PAS LA COMMANDE A DE SVG
      Elle prend des RAYONS et des drapeaux, pas une parametrisation. Deux
      ellipses de memes rayons passent par deux points donnes, et les
      drapeaux tranchent - mal, sur les fuseaux des bords. Pire : quand les
      rayons sont trop petits pour joindre les deux points, la norme impose
      de les AGRANDIR silencieusement, et la courbe obtenue n'est plus celle
      qu'on avait decrite. C'est ce qui decollait le remplissage du bord.

    Le facteur alpha est l'approximation classique d'un arc par une cubique ;
    a deux morceaux par quart d'ellipse, l'ecart est de l'ordre du
    dix-millieme de rayon - invisible, et surtout SANS ambiguite.
    """
    def P(t):
        return (centre[0] + U[0] * math.cos(t) + V[0] * math.sin(t),
                centre[1] + U[1] * math.cos(t) + V[1] * math.sin(t))

    def D(t):
        return (-U[0] * math.sin(t) + V[0] * math.cos(t),
                -U[1] * math.sin(t) + V[1] * math.cos(t))

    out = []
    for i in range(morceaux):
        a1 = th1 + (th2 - th1) * i / float(morceaux)
        a2 = th1 + (th2 - th1) * (i + 1) / float(morceaux)
        d = a2 - a1
        alpha = (math.sin(d)
                 * (math.sqrt(4.0 + 3.0 * math.tan(d / 2.0) ** 2) - 1.0) / 3.0)
        p1, p2 = P(a1), P(a2)
        d1, d2 = D(a1), D(a2)
        c1 = (p1[0] + alpha * d1[0], p1[1] + alpha * d1[1])
        c2 = (p2[0] - alpha * d2[0], p2[1] - alpha * d2[1])
        # La rotation est affine : transformer les points de controle
        # transforme la courbe. On peut donc pencher le parasol ici.
        c1, c2, p2 = place(c1), place(c2), place(p2)
        out.append(u"C%.1f %.1f %.1f %.1f %.1f %.1f" % (c1 + c2 + p2))
    return " ".join(out)


def coutures(cx, rx, n, decalage):
    """Les abscisses des coutures sur le bord, reparties en AZIMUT."""
    return [cx + rx * math.sin(-math.pi / 2
                               + math.pi * (k + decalage) / n)
            for k in range(n + 1)]


def descente_inverse(cx, cy, xa, ya, ry, S, facettes, T):
    """Le trace d'une couture, du bord au sommet : droite ou arc."""
    if facettes:
        return u"L%.1f %.1f" % S
    return cubiques((cx, cy), (xa - cx, ya - cy), (0.0, -ry),
                    0.0, math.pi / 2, T)


def un_parasol(nom, cx, cy, rx, ry, n, decalage, pied, inclinaison, indent=4,
               bord=None, facettes=False, symetrique=False,
               coutures_vues=None):
    u"""
    bord = None   le bord bas ONDULE : un feston par fuseau (version d'avant).
    bord = 0.0    le bord bas est DROIT.
    bord = 0.15   le bord bas est un ARC unique, bombe de 0.15 x la
                  demi-largeur. Un seul galbe continu, pas une vaguelette
                  par fuseau.

    POURQUOI CE CHOIX EXISTE
      J'avais impose le feston, en soutenant que c'est lui qui rend un
      parasol reconnaissable. C'est vrai des parasols a baleines apparentes ;
      ce n'est pas vrai de tous, et surtout ce n'etait pas vrai du modele.

      Sans feston, la PROFONDEUR doit venir d'ailleurs - et elle vient d'ou
      elle devrait toujours venir : du bombe de la coupole et de la courbure
      du bord. Le bord bas d'un dome vu legerement par en dessous ne se
      projette pas en droite, mais en demi-ellipse. C'est ce seul arc qui
      fait qu'on voit un volume et non un eventail a plat.

    symetrique = True  la coloration se compte depuis le MILIEU et non depuis
                       le bord gauche.

      A nombre PAIR de pans, l'alternance stricte donne vert-blanc-vert-blanc:
      le pan de gauche est vert, celui de droite blanc, et l'objet penche a
      l'oeil alors qu'il est parfaitement droit. Un parasol est symetrique -
      sa coloration doit l'etre aussi. On indexe donc les pans par leur
      distance au centre : vert-blanc-blanc-vert.

    facettes = True  les meridiens sont des SEGMENTS DROITS, plus des arcs :
                     chaque panneau devient un vrai triangle. Avec n = 3 on
                     obtient l'ombrelle a trois pans.

      Ce n'est pas un dome dessine moins bien, c'est un autre parti : la
      coupole n'est plus rendue par sa courbure mais par la seule alternance
      des pans. Le dessin y gagne en franchise ce qu'il perd en volume - et
      c'est un choix tres courant dans ce style d'illustration, ou l'objet
      doit se reconnaitre a sa silhouette avant tout.
    """
    e = " " * indent
    xs = coutures(cx, rx, n, decalage)
    sommet = (cx, cy - ry)
    # La demi-hauteur du bord bas, en unites de dessin.
    ry_bord = 0.0 if bord is None else bord * rx

    def y_bord(x):
        """L'ordonnee du bord bas a l'abscisse x, sur la demi-ellipse."""
        if not ry_bord:
            return cy
        t = max(-1.0, min(1.0, (x - cx) / rx))
        return cy + ry_bord * math.sqrt(max(0.0, 1.0 - t * t))
    # le point d'ancrage dans le sable : c'est autour de LUI que tout pivote,
    # d'un seul bloc, mat compris
    sol = (cx, cy + pied)

    def T(p):
        return tourner(p, sol, inclinaison)

    verts, blancs, festons, seams = [], [], [], []
    for k in range(n):
        xa, xb = xs[k], xs[k + 1]
        ra, rb = abs(xa - cx), abs(xb - cx)
        # la toile pend d'autant plus que le fuseau est large : ceux du centre
        # se voient de face, ceux des bords par la tranche
        sb = 1 if xb < cx else 0        # du bord droit du fuseau au sommet
        sa = 0 if xa < cx else 1        # du sommet au bord gauche
        A, B = T((xa, y_bord(xa))), T((xb, y_bord(xb)))
        S = T(sommet)
        if bord is None:
            # LE FESTON : la toile pend d'autant plus que le fuseau est large.
            fleche = min(0.30 * (xb - xa), ry * 0.30)
            M = T(((xa + xb) / 2, cy + 2 * fleche))
        else:
            # LE BORD DU DOME. On veut le morceau d'ellipse compris entre les
            # deux coutures.
            #
            # PAS avec une commande A : entre deux points, deux ellipses de
            # memes rayons passent, et les drapeaux choisissent laquelle. Sur
            # les fuseaux des bords, la mauvaise etait retenue - d'ou le filet
            # vert qui pendait sous la toile. Une quadratique n'a pas ce
            # choix a faire : elle est entierement determinee par ses trois
            # points.
            M = T(((xa + xb) / 2.0, y_bord((xa + xb) / 2.0)))

        # Le point de controle qui fait passer la quadratique PAR M : au
        # parametre 1/2 une quadratique vaut (A + 2C + B)/4, d'ou C.
        C = (2.0 * M[0] - (A[0] + B[0]) / 2.0,
             2.0 * M[1] - (A[1] + B[1]) / 2.0)
        feston = u'M%.1f %.1f Q%.1f %.1f %.1f %.1f' % (A + C + B)
        # LES DEUX MERIDIENS. Celui de droite monte du bord au sommet, celui
        # de gauche redescend. Chacun est l'arc d'ellipse qui va du point de
        # bord au sommet : demi-largeur |x - cx|, demi-hauteur ry, plus le
        # decalage vertical du bord bombe, qui s'annule au sommet.
        if facettes:
            montee = u"L%.1f %.1f" % S
            descente = u"L%.1f %.1f" % A
        else:
            montee = cubiques((cx, cy),
                              (xb - cx, y_bord(xb) - cy), (0.0, -ry),
                              0.0, math.pi / 2, T)
            descente = cubiques((cx, cy),
                                (xa - cx, y_bord(xa) - cy), (0.0, -ry),
                                math.pi / 2, 0.0, T)
        rang = min(k, n - 1 - k) if symetrique else k
        (verts if rang % 2 == 0 else blancs).append(
            u'%s      <path d="%s %s %s Z"/>' % (e, feston, montee, descente))
        festons.append(feston)
        # LA COUTURE INTERIEURE. Sans elle, deux pans voisins de meme couleur
        # fondent en une seule masse : la coloration symetrique donnait quatre
        # pans dont on n'en lisait que trois. La couture est aussi ce qui
        # raconte la baleine dessous - donc le volume.
        # Par defaut on ne les trace QUE si deux pans voisins peuvent
        # partager une couleur - c'est-a-dire en coloration symetrique.
        # Les parasols deja valides de la scene ne changent donc pas.
        if k and (symetrique if coutures_vues is None
                  else coutures_vues):
            seams.append(u'M%.1f %.1f %s' % (A[0], A[1], descente_inverse(
                cx, cy, xa, y_bord(xa), ry, S, facettes, T)))

    # Un gabarit a quinze trous positionnels est ingerable - je m'y suis
    # trompe une fois. On assemble donc des morceaux nommes.
    ombre = (u'<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s"'
             u' opacity="0.6"/>'
             % (sol[0] + rx * 0.24, sol[1] + 6, rx * 0.42, ry * 0.13, OMBRE))
    # LE MAT : un seul trait, du sable au sommet. Pas de coude, pas de
    # charniere - il penche, il ne plie pas.
    #
    # 14 px et non 9. Le mat n'a jamais ete graine - mesure a 0.00 - mais il
    # paraissait pixellise quand meme : un trait FIN, TRES SOMBRE et OBLIQUE
    # sur un fond presque blanc montre l'escalier de l'anticrenelage, et
    # aucun reglage de filtre n'y change rien. Le seul remede est de
    # l'epaissir : la marche reste la meme, mais elle ne represente plus
    # qu'un quinzieme de la largeur au lieu d'un neuvieme.
    _h = T((cx, cy - ry * 0.55))
    mat = (u'<path d="M%.1f %.1f L%.1f %.1f" stroke="%s" stroke-width="14"'
           u' stroke-linecap="round"/>'
           % (sol[0], sol[1], _h[0], _h[1], PIED))
    lisere = (u'<path d="%s" fill="none" stroke="%s" stroke-width="3.5"'
              u' opacity="0.55"/>' % (" ".join(festons), VERT_SOMBRE))
    trace_coutures = (u'<path d="%s" fill="none" stroke="%s" '
                     u'stroke-width="2.2" opacity="0.35"/>'
                      % (" ".join(seams), VERT_SOMBRE)) if seams else u''

    _s1, _s2 = T(sommet), T((cx, sommet[1] - ry * 0.16))
    embout = (u'<path d="M%.1f %.1f L%.1f %.1f" stroke="%s" stroke-width="10"'
              u' stroke-linecap="round"/>'
              % (_s1[0], _s1[1], _s2[0], _s2[1], PIED))

    lignes = [u'%s<g inkscape:label="%s">' % (e, nom),
              u'%s  %s' % (e, ombre),
              u'%s  %s' % (e, mat),
              u'%s  <g fill="%s" filter="url(#grainToileVerte)">' % (e, VERT),
              "\n".join(verts),
              u'%s  </g>' % e,
              u'%s  <g fill="%s" filter="url(#grainToileBlanche)">' % (e, BLANC),
              "\n".join(blancs),
              u'%s  </g>' % e,
              u'%s  %s' % (e, lisere),
              u'%s  %s' % (e, trace_coutures),
              u'%s  %s' % (e, embout),
              u'%s</g>' % e]
    return "\n".join(lignes)


def engendrer(indent=4):
    corps = [un_eventail(*p, indent=indent, pans=PANS_ACTIFS)
             for p in PARASOLS]
    return "", "\n\n".join(corps), len(PARASOLS)


# =====================================================================
#  L'EVENTAIL - la forme de la reference
# =====================================================================
#
# CE QUE MONTRE LE MODELE, ET QUE J'AVAIS REFUSE DE VOIR
#   Le parasol de l'image de reference n'est pas une coupole. C'est une
#   DEMI-LUNE decoupee en secteurs egaux, tous issus d'un meme point : le
#   milieu du bord droit. Le mat est plante dans ce point, perpendiculaire au
#   diametre, et le tout est bascule.
#
#   J'avais construit exactement cela en premiere version, puis je l'ai
#   remplace en soutenant qu'"une coupole n'a pas de secteurs, elle a des
#   fuseaux". C'est vrai d'un parasol photographie. Ce n'est pas vrai de
#   celui-la, qui est un DESSIN : il ne represente pas le volume, il le
#   resume. Le modele avait raison contre ma theorie.
#
# CE QU'IL N'A PAS, ET C'EST AUSSI IMPORTANT
#   Pas de feston. Pas de liseré. Pas de couture tracee. Pas d'embout au
#   sommet. Les secteurs ne sont QUE des changements de couleur, bord a bord.
#
# MESURES RELEVEES SUR L'IMAGE
#   inclinaison  ~34 deg      secteurs  5 (impair : colore aux deux bouts)
#   mat          ~0.95 x R    largeur du mat  ~0.04 x R, tres fin

ROUGE = "#E8433F"
JAUNE = "#F5C542"

# LES PANS, dans l'ordre, repetes en boucle. Chaque entree est un couple
# (couleur, filtre de grain) : le grain ne peut pas etre commun, un point
# clair sur du blanc ne se voit pas alors qu'il creve un aplat sature.
# Le filtre est nomme d'apres la SATURATION du pan, pas d'apres sa couleur :
# le mouchetis pose des points a opacite fixe, son effet ne depend pas de la
# teinte. Un rouge et un vert de meme saturation prennent le meme reglage ;
# seul le blanc en demande un autre, parce qu'un point clair sur du blanc ne
# se voit pas.
VIF, PALE = "grainToileVive", "grainToileBlanche"

PANS_VERT      = [(VERT, VIF), (BLANC, PALE)]
PANS_ROUGE     = [(ROUGE, VIF), (BLANC, PALE)]
PANS_TRICOLORE = [(ROUGE, VIF), (BLANC, PALE), (VERT, VIF), (BLANC, PALE),
                  (ROUGE, VIF)]

# Celui qui sert dans la scene.
PANS_ACTIFS = PANS_VERT


def un_eventail(nom, cx, cy, rayon, n, inclinaison, pied=None,
                largeur_mat=0.045, indent=4, pans=None,
                couleurs=None, filtre_a=None, filtre_b=None):
    u"""
    (cx, cy) est le MILIEU DU BORD DROIT, avant inclinaison - c'est le point
    ou le mat rejoint la toile, et le centre de tous les secteurs.

    pied et largeur_mat sont donnes en fraction du rayon : le parasol reste
    ainsi proportionne a lui-meme quelle que soit sa taille dans la scene.
    """
    e = " " * indent
    # pied est donne en fraction du rayon ; None reprend la longueur du
    # premier modele, ou le mat valait 0.95 rayon.
    L = (0.95 if pied is None else pied) * rayon
    ancre = (cx, cy + L)                 # le point plante dans le sable

    def T(p):
        return tourner(p, ancre, inclinaison)

    # Compatibilite avec l'ancien appel a deux couleurs.
    if pans is None:
        pans = (PANS_VERT if couleurs is None else
                [(couleurs[0], filtre_a or "grainToileVerte"),
                 (couleurs[1], filtre_b or "grainToileBlanche")])
    groupes = [[] for _ in pans]
    for k in range(n):
        # Les secteurs sont egaux EN ANGLE. C'est ce qui les distingue des
        # fuseaux d'une coupole, resserres vers les bords.
        t1 = math.pi - math.pi * k / n
        t2 = math.pi - math.pi * (k + 1) / n
        O = T((cx, cy))
        A = T((cx + rayon * math.cos(t1), cy - rayon * math.sin(t1)))
        arc = cubiques((cx, cy), (rayon, 0.0), (0.0, -rayon), t1, t2, T)
        groupes[k % len(pans)].append(
            u'%s      <path d="M%.1f %.1f L%.1f %.1f %s Z"/>'
            % (e, O[0], O[1], A[0], A[1], arc))

    # LE MAT. Un seul trait droit, du sable au centre du bord. Sur le modele
    # il est tres fin - environ un vingtieme du rayon - et sans embout.
    haut = T((cx, cy))
    mat = (u'<path d="M%.1f %.1f L%.1f %.1f" stroke="%s" stroke-width="%.1f"'
           u' stroke-linecap="round"/>'
           % (ancre[0], ancre[1], haut[0], haut[1], PIED,
              max(3.0, largeur_mat * rayon)))
    ombre = (u'<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s"'
             u' opacity="0.55"/>'
             % (ancre[0], ancre[1] + 4, rayon * 0.30, rayon * 0.09, OMBRE))

    lignes = [u'%s<g inkscape:label="%s">' % (e, nom),
              u'%s  %s' % (e, ombre),
              u'%s  %s' % (e, mat)]
    for (couleur, filtre), formes in zip(pans, groupes):
        if not formes:
            continue
        lignes += [u'%s  <g fill="%s" filter="url(#%s)">' % (e, couleur, filtre),
                   "\n".join(formes),
                   u'%s  </g>' % e]
    lignes.append(u'%s</g>' % e)
    return "\n".join(lignes)


if __name__ == "__main__":
    _, _, n = engendrer()
    print(u"%d parasols, forme du modele (eventail)" % n)
    for nom, cx, cy, rayon, nf, inclinaison, mat in PARASOLS:
        print(u"  %-22s rayon %3d, %d secteurs de %.0f deg, penche de %+.0f"
              % (nom, rayon, nf, 180.0 / nf, inclinaison))
        print(u"  %-22s mat de %.0f px (%.2f rayon), plante en (%.0f, %.0f)"
              % ("", mat * rayon, mat, cx, cy + mat * rayon))