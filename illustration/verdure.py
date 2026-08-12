# -*- coding: utf-8 -*-
u"""
Le buisson qui longe le grillage.

CE QUI N'ALLAIT PAS AVANT
  La verdure etait une bande horizontale : meme hauteur, memes touffes, du
  bord gauche au bord droit. Or sur la photo ce n'est pas une bande, c'est
  une haie PLANTEE LE LONG DE LA CLOTURE. Elle doit donc fuir avec elle,
  vers le meme point, et rapetisser au meme rythme. Une haie de hauteur
  constante pendant que le grillage rapetisse se voit tout de suite : les
  deux se contredisent, et c'est la scene entiere qui cesse d'exister.

CE QUI EN DECOULE
  Les touffes ne sont plus semees a pas constant a l'ecran mais a pas
  constant DANS LE MONDE, puis projetees : elles se resserrent et se
  reduisent d'elles-memes vers la droite. Leur rayon est multiplie par le
  meme facteur s(u) que le reste. Rien n'est dessine en coordonnees ecran.

DEUX RANGS, PAS TROIS
  J'en avais mis trois, en pensant creuser la profondeur. Un de trop : a
  cette echelle le rang du milieu ne se distingue plus vraiment de ses
  voisins, il epaissit la masse verte sans rien ajouter. Deux valeurs
  suffisent a poser un devant et un derriere - et la masse pese moins lourd
  dans l'image, ce qui compte quand elle occupe deja un tiers du cadre.

LES DEUX TONS
  Chaque rang est peint clair, puis la meme silhouette decalee VERS LE BAS et
  decoupee par elle-meme est repeinte sombre : il reste une bande claire sur
  le dessus du feuillage. Les nuages font l'inverse, parce qu'un nuage se
  voit par en dessous et une haie par au-dessus.
"""

import random
import perspective as P

# (nom, crete au plus pres, pied au plus pres, rayon mini, rayon maxi,
#  pas dans le monde, ton clair, ton sombre, bande eclairee)
# Rayons, pied et bande sont donnes AU PLUS PRES ; la perspective les reduit
# ensuite d'elle-meme.
# Le pas est donne en PIXELS et converti en unites du monde a l'usage. Il
# etait auparavant exprime directement en unites du monde, c'est-a-dire en
# ecarts de poteaux : changer l'espacement de la cloture eclaircissait donc
# aussi le buisson, qui n'a rien a y voir.
RANGS = [
    ("Rang 1 - fond",   500, 900, 26, 50, 38, "#B4D6A0", "#96C285", 14),
    ("Rang 2 - devant", 668, 880, 38, 74, 56, "#6BA867", "#4E9354", 22),
]

# Le pied du rang le plus proche : c'est LUI qui donnera le bord du sable,
# pour que la haie soit posee dessus et non flottante au-dessus.
PIED_DEVANT = 880

# Quelques houppiers plus hauts, sur le rang du fond, donnes par leur
# distance u : ils rapetissent donc eux aussi en s'eloignant.
# Donnes par leur abscisse a l'ecran, eux aussi : leur place dans l'image ne
# doit pas dependre de l'espacement des poteaux.
ARBRES = [(180, -52, 1.30), (240, -34, 0.95), (610, -58, 1.40),
          (668, -38, 1.00), (1245, -50, 1.20), (1305, -32, 0.90),
          (1700, -46, 1.15)]


def touffes(crete, rmin, rmax, pas_px, alea, arbres=None):
    """Les disques semes le long de la haie, a pas constant DANS LE MONDE."""
    pas = pas_px / P.ecart_px()
    sortie, u = [], -pas * 2
    while True:
        r0 = alea.uniform(rmin, rmax)
        # le centre monte ou descend un peu, sinon les sommets s'alignent
        dy = alea.uniform(-r0 * 0.30, r0 * 0.20)
        x, y = P.projeter(u, crete + dy)
        r = r0 * P.echelle(u)
        if x > P.LARGEUR + rmax or r < 2.5:
            break
        sortie.append((round(x, 1), round(y, 1), round(r, 1)))
        u += alea.uniform(pas * 0.6, pas * 1.2)

    for x_px, dy, k in (arbres or []):
        uu = P.u_de_x(x_px)
        x, y = P.projeter(uu, crete + dy)
        sortie.append((round(x, 1), round(y, 1),
                       round(rmax * k * P.echelle(uu), 1)))
    return sortie


def corps(disques, crete, indent=8):
    """La masse pleine sous la crete, puis ses touffes."""
    e = " " * indent
    sol = P.ligne_au_sol(crete)
    d = "M%.1f %.1f " % sol[0] + " ".join("L%.1f %.1f" % p for p in sol[1:])
    d += " L%d %d L0 %d Z" % (P.LARGEUR, P.HAUTEUR, P.HAUTEUR)
    out = [u'%s<path d="%s"/>' % (e, d)]
    for cx, cy, r in disques:
        out.append(u'%s<circle cx="%s" cy="%s" r="%s"/>' % (e, cx, cy, r))
    return "\n".join(out)


def engendrer():
    alea = random.Random(2024)
    coupes, morceaux = [], []
    for i, (nom, crete, pied, rmin, rmax, pas, clair, sombre, bande) in \
            enumerate(RANGS, start=1):
        disques = touffes(crete, rmin, rmax, pas, alea,
                          ARBRES if i == 1 else None)
        forme = corps(disques, crete)
        cid = "coupeVert%d" % i
        coupes.append(u'  <clipPath id="%s">\n%s\n  </clipPath>'
                      % (cid, corps(disques, crete, indent=4)))
        morceaux.append(u"""    <g inkscape:groupmode="layer" inkscape:label="%02d %s" id="palierV%d">
      <g fill="%s">
%s
      </g>
      <g clip-path="url(#%s)" fill="%s" transform="translate(0,%d)">
%s
      </g>
    </g>""" % (4 + i, nom, i, clair, forme, cid, sombre, bande, forme))
    total = sum(m.count("<circle") for m in morceaux)
    return "\n".join(coupes), "\n\n".join(morceaux), total


if __name__ == "__main__":
    _, _, n = engendrer()
    print(u"buisson : %d touffes sur %d rangs" % (n, len(RANGS)))
    print(u"le rang de devant, en fuite :")
    for u in (0, 3, 6, 12, 20):
        x, y = P.projeter(u, RANGS[-1][1])
        _, yp = P.projeter(u, RANGS[-1][2])
        print(u"  u=%2d  x=%7.1f  crete %6.1f  pied %6.1f  hauteur %5.1f"
              % (u, x, y, yp, yp - y))
