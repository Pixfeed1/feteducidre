# -*- coding: utf-8 -*-
u"""
Banc d'essai des nuages : les actuels en haut, les nouveaux en bas.

Rien de la scene n'est modifie. construire.py n'est pas touche.

    python3 essai_nuage.py && inkscape --export-type=png \
        --export-filename=essai_nuage.png -w 1800 essai_nuage.svg
"""

import construire as K
import nuages as N

LARGEUR, HAUTEUR = 1800, 900
BANDE = HAUTEUR // 2


def peindre(formes, decalage):
    u"""
    Les deux tons du modele : la silhouette entiere dans le ton froid, puis
    LA MEME decoupee par elle-meme et remontee, repeinte en clair. Il reste
    une lisiere froide sous le nuage - un nuage se voit par en dessous.
    """
    return (u'      <g fill="%s">%s</g>\n'
            u'      <g fill="%s" transform="translate(0,-%d)">%s</g>'
            % (K.NUAGE_FROID, formes, K.NUAGE_CLAIR, decalage, formes))


def feuille():
    # EN HAUT : ce qu'on a aujourd'hui, tel quel.
    anciens = []
    for i, (n, dec) in enumerate(((K.NUAGE1, 17), (K.NUAGE2, 13),
                                  (K.NUAGE3, 15))):
        anciens.append(u'    <g clip-path="url(#coupeA%d)">%s</g>'
                       % (i, peindre(n, dec)))
    coupes = "\n".join(
        u'  <clipPath id="coupeA%d">%s</clipPath>' % (i, n)
        for i, n in enumerate((K.NUAGE1, K.NUAGE2, K.NUAGE3)))

    # EN BAS : les nouveaux, au rapport releve sur le modele.
    # (x, y de pose, longueur, profil)
    NOUVEAUX = [(150, BANDE + 210, 430, 0),
                (760, BANDE + 300, 360, 1),
                (1290, BANDE + 165, 400, 2)]
    bas, coupes_b = [], []
    for i, (x, y, L, p) in enumerate(NOUVEAUX):
        f = N.nuage(x, y, L, p, indent=8)
        coupes_b.append(u'  <clipPath id="coupeB%d">%s</clipPath>' % (i, f))
        bas.append(u'    <g clip-path="url(#coupeB%d)">%s</g>'
                   % (i, peindre(f, max(5, L / 46.0))))

    etiq = (u'  <text x="30" y="%d" font-family="sans-serif" font-size="30"'
            u' fill="#5B6B78">%s</text>')
    return u"""<svg xmlns="http://www.w3.org/2000/svg"
     width="%d" height="%d" viewBox="0 0 %d %d">
<defs>
%s
%s
%s
</defs>
<rect x="0" y="0" width="%d" height="%d" fill="%s"/>
<g filter="url(#grainCiel)">
%s
</g>
<path d="M0 %d L%d %d" stroke="#C9DDEC" stroke-width="2"/>
<g filter="url(#grainCiel)">
%s
</g>
%s
%s
</svg>
""" % (LARGEUR, HAUTEUR, LARGEUR, HAUTEUR,
       K.grain("grainCiel", 8, "1.05", "le grain du ciel"),
       coupes, "\n".join(coupes_b),
       LARGEUR, HAUTEUR, K.CIEL,
       "\n".join(anciens), BANDE, LARGEUR, BANDE, "\n".join(bas),
       etiq % (52, "actuels  -  330 x 128, rapport 2.6 : 1"),
       etiq % (BANDE + 52, "modele  -  400 x 70, rapport 5.8 : 1"))


if __name__ == "__main__":
    open("essai_nuage.svg", "w").write(feuille())
    print(u"essai_nuage.svg ecrit ; construire.py n'a pas ete touche.")
