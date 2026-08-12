# -*- coding: utf-8 -*-
u"""
La serviette posee sur le sable.

CE QUE MONTRE LE MODELE
  Un quadrilatere, pas un rectangle. Son bord LOIN est plus court que son
  bord PRES, et c'est tout ce qui la fait coucher au sol : un rectangle a
  angles droits se lit comme une plaque dressee, meme pose au bon endroit.
  L'ecart est faible - de l'ordre du dixieme - mais il n'est pas nul, et
  c'est cette petite chose qui decide.

  A l'interieur, un LISERE CLAIR, a distance constante du bord. Il double la
  silhouette et lui donne son caractere de textile ; sans lui on dessine un
  tapis de gym.

LE LISERE EST UN VRAI DECALAGE, PAS UNE HOMOTHETIE
  On serait tente de reduire le quadrilatere vers son centre. Ce serait faux :
  une homothetie rapproche d'autant plus les bords qu'ils sont loin du
  centre, donc la marge serait plus large en haut qu'en bas, et l'oeil le
  voit tout de suite sur une forme en perspective.

  On decale donc CHAQUE COTE de la meme distance le long de sa normale, puis
  on recoupe les cotes voisins deux a deux. La marge est alors constante par
  construction. C'est ce que ferait "Chemin > Eroder" dans Inkscape - qui
  n'existe pas en ligne de commande, on l'a verifie.
"""

VERT = "#2F9E52"
LISERE = "#FBFCFA"


def _intersection(p1, d1, p2, d2):
    u"""Le point de rencontre de deux droites, chacune par point + direction."""
    det = d1[0] * (-d2[1]) - d1[1] * (-d2[0])
    if abs(det) < 1e-9:                 # coincidentes ou paralleles
        return p2
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    t = (dx * (-d2[1]) - dy * (-d2[0])) / det
    return (p1[0] + d1[0] * t, p1[1] + d1[1] * t)


def eroder(points, marge):
    u"""
    Le meme polygone, chaque cote rentre de `marge` vers l'interieur.

    Les points sont donnes dans le sens horaire (y vers le bas), ce qui met
    l'interieur a GAUCHE de chaque cote ; la normale interieure d'un vecteur
    (dx, dy) est donc (dy, -dx) normalisee.
    """
    n = len(points)
    cotes = []
    for i in range(n):
        a, b = points[i], points[(i + 1) % n]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = (dx * dx + dy * dy) ** 0.5 or 1.0
        nx, ny = dy / L, -dx / L
        cotes.append(((a[0] + nx * marge, a[1] + ny * marge), (dx, dy)))

    return [_intersection(cotes[i - 1][0], cotes[i - 1][1],
                          cotes[i][0], cotes[i][1]) for i in range(n)]


def quadrilatere(cx, y_pres, largeur, profondeur, fuite=0.88, biais=0.0):
    u"""
    fuite : le bord loin fait `fuite` fois la largeur du bord pres. C'est lui
            qui couche la serviette au sol.
    biais : decalage lateral du bord loin, pour que la serviette ne soit pas
            de face - une serviette parfaitement frontale a l'air posee par
            un geometre.
    """
    y_loin = y_pres - profondeur
    l2, f2 = largeur / 2.0, largeur * fuite / 2.0
    return [(cx - f2 + biais, y_loin), (cx + f2 + biais, y_loin),
            (cx + l2, y_pres), (cx - l2, y_pres)]


def _chemin(points, r=0.0):
    u"""Le contour, coins legerement arrondis si r > 0."""
    if r <= 0:
        return ("M%.1f %.1f " % points[0]
                + " ".join("L%.1f %.1f" % p for p in points[1:]) + " Z")
    n, d = len(points), ""
    for i in range(n):
        a, b, c = points[i - 1], points[i], points[(i + 1) % n]
        def vers(p, q, t):
            dx, dy = q[0] - p[0], q[1] - p[1]
            L = (dx * dx + dy * dy) ** 0.5 or 1.0
            k = min(t, L / 2.0) / L
            return (p[0] + dx * k, p[1] + dy * k)
        e, s = vers(b, a, r), vers(b, c, r)
        d += ("M%.1f %.1f " % e) if i == 0 else (" L%.1f %.1f" % e)
        d += " Q%.1f %.1f %.1f %.1f" % (b + s)
    return d + " Z"


def dessiner(cx, y_pres, largeur, profondeur, fuite=0.88, biais=0.0,
             marge=22.0, rayon=10.0, indent=4, filtre="grainToileVive",
             couleur=VERT, lisere=LISERE, epaisseur=5.0):
    p = quadrilatere(cx, y_pres, largeur, profondeur, fuite, biais)
    e = " " * indent
    return "\n".join([
        u'%s<g inkscape:label="Serviette" filter="url(#%s)">' % (e, filtre),
        u'%s  <path d="%s" fill="%s"/>' % (e, _chemin(p, rayon), couleur),
        u'%s  <path d="%s" fill="none" stroke="%s" stroke-width="%.1f"/>'
        % (e, _chemin(eroder(p, marge), max(0.0, rayon - marge * 0.4)),
           lisere, epaisseur),
        u'%s</g>' % e])


if __name__ == "__main__":
    p = quadrilatere(470, 950, 460, 210, 0.88, -30)
    q = eroder(p, 22)
    print(u"bord pres %.0f px, bord loin %.0f px"
          % (p[2][0] - p[3][0], p[1][0] - p[0][0]))
    print(u"marge mesuree sur les quatre cotes :")
    for i in range(4):
        a, b = p[i], p[(i + 1) % 4]
        m = q[i]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = (dx * dx + dy * dy) ** 0.5
        dist = abs((m[0] - a[0]) * dy - (m[1] - a[1]) * dx) / L
        print(u"   cote %d : %.2f px" % (i, dist))
