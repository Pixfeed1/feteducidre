# -*- coding: utf-8 -*-
u"""
Greffer un personnage tout fait dans la scene.

POURQUOI CET OUTIL
  Un decor est un probleme geometrique : une cloture, une haie, une coupole
  se CALCULENT, et le code y est meilleur que la main. Un personnage, non.
  Le tracer point par point en Python donne toujours de l'a-peu-pres - tu
  l'as vu, et tu as eu raison de le dire. La bonne reponse est de partir d'un
  personnage deja dessine par quelqu'un dont c'est le metier, puis de
  l'ACCORDER a notre image.

  C'est ce que fait ce script : il prend un SVG de personnage, remplace ses
  couleurs par les notres, le met a l'echelle, le pose au bon endroit et lui
  applique notre grain. Le resultat s'insere tel quel dans scene.svg.

OU TROUVER LES PERSONNAGES
  Aucune de ces adresses n'est joignable depuis la machine ou ce script a ete
  ecrit - le proxy les refuse - donc tu devras telecharger toi-meme.

    humaaans.com       Le plus proche de ta reference, et de loin. Des gens
                       a plat, en pieces detachees : corps, poses, tetes,
                       vetements, qu'on recombine. Membres fuseles, peau
                       coraline, aucun detail de visage. C'est exactement le
                       vocabulaire de ton image.
    openpeeps.com      Dessin a la main, plus croque. CC0.
    undraw.co          Scenes completes, recolorables par une seule couleur
                       d'accent. Style plus fin, moins charnu.
    opendoodles.com    Silhouettes tres libres, CC0.

  VERIFIE LA LICENCE avant de livrer a une ville. Elles different d'un pack a
  l'autre et changent avec le temps ; je ne les affirme pas ici.

USAGE
    python3 importer_figure.py enfant_telecharge.svg --y 1218 --x 880 \\
        --hauteur 300 --couleurs

  --couleurs seul liste les couleurs trouvees dans le fichier, sans rien
  produire : c'est par la qu'on commence, pour savoir quoi remplacer.
"""

import re
import sys
import xml.dom.minidom as minidom

# NOTRE PALETTE. Chaque couleur du fichier source sera remplacee par la plus
# proche d'entre elles. C'est ce qui fait qu'un personnage venu d'ailleurs
# appartient d'un coup a l'image : ce n'est pas le dessin qui fait l'unite
# d'une illustration, c'est la palette.
PALETTE = {
    "peau":         "#F2A07B",
    "peau_ombre":   "#DB8760",
    "cheveux":      "#5A3A28",
    "cheveux_clair": "#7A5238",
    "accent":       "#E8433F",
    "accent_ombre": "#C7332F",
    "bleu":         "#2E6FE0",
    "bleu_ombre":   "#2455B0",
    "jaune":        "#F5C542",
    "vert":         "#2F9E52",
    "vert_ombre":   "#22753A",
    "blanc":        "#FBFCFA",
    "sombre":       "#1B2026",
}


def _rvb(c):
    c = c.strip().lstrip("#")
    if len(c) == 3:
        c = "".join(x * 2 for x in c)
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def _ycbcr(c):
    r, g, b = _rvb(c)
    y = 0.299 * r + 0.587 * g + 0.114 * b
    return y, 128 + (b - y) * 0.564, 128 + (r - y) * 0.713


def _distance(a, b):
    """
    Ecart entre deux couleurs, la TEINTE pesant plus que la luminosite.

    J'avais fait l'inverse, en me disant qu'une correspondance se fait
    d'abord sur la valeur. Resultat au premier essai : une peau claire
    (#EFC7A3) est partie sur le JAUNE, parce qu'ils ont la meme luminosite.
    C'est le pire echec possible pour un personnage.

    On compare donc en YCbCr, ou la couleur est separee de la luminosite, et
    on pese les deux composantes de couleur une fois et demie plus que la
    luminosite. La meme peau tombe alors sur notre peau.
    """
    ya, cba, cra = _ycbcr(a)
    yb, cbb, crb = _ycbcr(b)
    return abs(ya - yb) + 1.6 * abs(cba - cbb) + 1.6 * abs(cra - crb)


def couleurs_du_fichier(chemin):
    texte = open(chemin, encoding="utf-8", errors="ignore").read()
    trouvees = {}
    for c in re.findall(r'#[0-9A-Fa-f]{3,6}\b', texte):
        c = c.upper()
        trouvees[c] = trouvees.get(c, 0) + 1
    return sorted(trouvees.items(), key=lambda kv: -kv[1])


def correspondance(couleurs):
    """A chaque couleur du source, la plus proche de notre palette."""
    table = {}
    for c, _ in couleurs:
        nom, cible = min(PALETTE.items(), key=lambda kv: _distance(c, kv[1]))
        table[c] = (cible, nom)
    return table


def greffer(chemin, x, y, hauteur, table=None, filtre="grainDoux", indent=2):
    """
    Rend le fragment SVG a coller dans scene.svg.

    x, y    : le point ou le personnage touche le sable
    hauteur : sa hauteur voulue, en unites de la scene
    """
    doc = minidom.parse(chemin)
    svg = doc.documentElement

    boite = svg.getAttribute("viewBox").split()
    if len(boite) == 4:
        bx, by, bl, bh = (float(v) for v in boite)
    else:
        bl = float(re.sub(r"[^0-9.]", "", svg.getAttribute("width") or "100"))
        bh = float(re.sub(r"[^0-9.]", "", svg.getAttribute("height") or "100"))
        bx = by = 0.0
    k = hauteur / bh

    corps = "".join(n.toxml() for n in svg.childNodes
                    if n.nodeType == n.ELEMENT_NODE
                    and n.tagName not in ("title", "desc", "metadata"))

    table = table or correspondance(couleurs_du_fichier(chemin))
    # on remplace en une passe, sinon une couleur deja remplacee pourrait
    # etre re-remplacee par la suivante
    def remplacer(m):
        return table.get(m.group(0).upper(), (m.group(0),))[0]
    corps = re.sub(r'#[0-9A-Fa-f]{3,6}\b', remplacer, corps)

    e = " " * indent
    # Le personnage est POSE par son point de contact : on ramene son coin
    # haut-gauche de sorte que le bas de sa boite tombe sur (x, y).
    tx = x - (bx + bl / 2.0) * k
    ty = y - (by + bh) * k
    return (u'%s<g inkscape:groupmode="layer" inkscape:label="Personnage" '
            u'id="personnage" filter="url(#%s)">\n'
            u'%s  <g transform="translate(%.2f %.2f) scale(%.4f)">\n'
            u'%s\n'
            u'%s  </g>\n'
            u'%s</g>' % (e, filtre, e, tx, ty, k, corps, e, e))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    source = sys.argv[1]
    trouvees = couleurs_du_fichier(source)
    table = correspondance(trouvees)

    if "--couleurs" in sys.argv or len(sys.argv) == 2:
        print(u"%d couleurs dans %s\n" % (len(trouvees), source))
        print(u"  %-10s %-7s -> %-10s %s" % ("source", "usages", "notre", "role"))
        for c, n in trouvees[:24]:
            cible, nom = table[c]
            print(u"  %-10s %-7d -> %-10s %s" % (c, n, cible, nom))
        print(u"\nRelance sans --couleurs pour produire le fragment.")
        sys.exit(0)

    def arg(nom, defaut):
        return (float(sys.argv[sys.argv.index(nom) + 1])
                if nom in sys.argv else defaut)

    fragment = greffer(source, arg("--x", 880), arg("--y", 1218),
                       arg("--hauteur", 300), table)
    open("figure.svg", "w").write(fragment)
    print(u"figure.svg ecrit (%d caracteres)." % len(fragment))
    print(u"Colle-le dans scene.svg avant </svg>, ou ajoute dans "
          u"construire.py :")
    print(u'    FIGURE = open("figure.svg").read()')
