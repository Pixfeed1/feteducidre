# -*- coding: utf-8 -*-
u"""
La serviette posee sur le sable.

RELEVE SUR LE MODELE (image de 760 x 760)
  bords         x = 48 -> 352      y = 258 -> 372
  dimensions    304 x 114 px       soit 0.40 de la largeur, 0.15 de la hauteur
  forme         un RECTANGLE, incline d'un degre et demi a peine

  MON ERREUR : je l'avais construite en trapeze fuyant, en me disant qu'un
  rectangle a angles droits se lit comme une plaque dressee. C'est vrai dans
  une image en perspective. Celle-ci n'en a pas : elle est entierement plate,
  et tout y est vu de face - la mer, le parasol, le batiment. Une serviette
  fuyante au milieu d'une image plate ne fait pas plus vrai, elle fait faux.
  Le modele decide, pas la regle generale.

  Et elle etait deux fois trop petite : 470 px de large au lieu de 720.

LE POURTOUR EST BLANC, ET IL EST DEHORS
  J'avais mis un lisere clair a l'INTERIEUR du vert. Sur le modele c'est
  l'inverse : le vert est pose sur un rectangle blanc un peu plus grand, qui
  deborde tout autour. C'est le bord du tissu, pas un motif imprime dessus.

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

# BLANC PUR, et non le blanc casse des toiles (#FBFCFA). Le sable est a
# #FAFAF6 : un pourtour a #FBFCFA s'y fond, un point d'ecart sur trois
# canaux. A #FFFFFF il reste discret mais il EXISTE - c'est ce que fait le
# modele, dont le sable est chaud et le bord de serviette franchement blanc.
LISERE = "#FFFFFF"


def aire(points):
    u"""L'aire du polygone, par la formule du lacet. Positive si horaire."""
    n = len(points)
    return 0.5 * sum(points[i][0] * points[(i + 1) % n][1]
                     - points[(i + 1) % n][0] * points[i][1] for i in range(n))


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

    Les points sont donnes dans le sens horaire A L'ECRAN, y vers le bas.
    L'interieur est alors a DROITE de chaque cote, et la normale interieure
    d'un vecteur (dx, dy) est (-dy, dx) normalisee.

    JE L'AVAIS PRISE A L'ENVERS, et le contour se dilatait au lieu de se
    reduire : le vert debordait le blanc, donc le pourtour n'existait plus.
    Le test ne l'a pas vu parce qu'il mesurait une distance NON SIGNEE - il
    affichait fierement 19.00 px sur les quatre cotes, du mauvais cote. Une
    verification qui ne peut pas echouer ne verifie rien ; on compare donc
    maintenant les AIRES, qui portent le signe.
    """
    n = len(points)
    cotes = []
    for i in range(n):
        a, b = points[i], points[(i + 1) % n]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = (dx * dx + dy * dy) ** 0.5 or 1.0
        nx, ny = -dy / L, dx / L
        cotes.append(((a[0] + nx * marge, a[1] + ny * marge), (dx, dy)))

    return [_intersection(cotes[i - 1][0], cotes[i - 1][1],
                          cotes[i][0], cotes[i][1]) for i in range(n)]


def quadrilatere(cx, cy, largeur, hauteur, pivot=0.0, fuite=1.0):
    u"""
    cx, cy : le CENTRE du rectangle.
    pivot  : son inclinaison en degres. Un degre ou deux suffisent - ils
             suppriment la raideur du rectangle parfaitement horizontal sans
             introduire de perspective, que l'image n'a pas.
    fuite  : laisse a 1.0 pour un rectangle. En dessous, le bord du haut se
             raccourcit et la forme redevient un trapeze fuyant.
    """
    import math
    l2, h2 = largeur / 2.0, hauteur / 2.0
    f2 = l2 * fuite
    pts = [(-f2, -h2), (f2, -h2), (l2, h2), (-l2, h2)]
    a = math.radians(pivot)
    ca, sa = math.cos(a), math.sin(a)
    return [(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in pts]


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


def dessiner(cx, cy, largeur, hauteur, pivot=-1.5, fuite=1.0,
             pourtour=19.0, rayon=8.0, indent=4, filtre="grainToileVive",
             couleur=VERT, bord_couleur=LISERE):
    u"""
    Le blanc DESSOUS et debordant, le vert PAR-DESSUS et rentre de `pourtour`.

    On pourrait peindre le blanc en contour du vert ; ce serait moins juste.
    Un contour se centre sur le trace, donc la moitie de son epaisseur mord
    sur le vert : la couleur du tapis maigrirait quand on epaissit le bord.
    Ici les deux formes sont pleines et independantes.
    """
    dehors = quadrilatere(cx, cy, largeur, hauteur, pivot, fuite)
    dedans = eroder(dehors, pourtour)
    e = " " * indent
    return "\n".join([
        u'%s<g inkscape:label="Serviette" filter="url(#%s)">' % (e, filtre),
        u'%s  <path d="%s" fill="%s"/>'
        % (e, _chemin(dehors, rayon), bord_couleur),
        u'%s  <path d="%s" fill="%s"/>'
        % (e, _chemin(dedans, max(0.0, rayon - pourtour * 0.5)), couleur),
        u'%s</g>' % e])


if __name__ == "__main__":
    p = quadrilatere(473, 559, 721, 203, -1.5)
    q = eroder(p, 19)
    print(u"%.0f x %.0f px, soit %.2f de la largeur et %.2f de la hauteur"
          % (721, 203, 721 / 1800.0, 203 / 1350.0))
    print(u"aire du contour %.0f, aire du vert %.0f  ->  %s"
          % (aire(p), aire(q),
             "le vert est DEDANS" if abs(aire(q)) < abs(aire(p))
             else "ERREUR : le vert deborde"))
    print(u"marge mesuree sur les quatre cotes :")
    for i in range(4):
        a, b = p[i], p[(i + 1) % 4]
        m = q[i]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = (dx * dx + dy * dy) ** 0.5
        dist = abs((m[0] - a[0]) * dy - (m[1] - a[1]) * dx) / L
        print(u"   cote %d : %.2f px" % (i, dist))
