# -*- coding: utf-8 -*-
u"""
Banc d'essai de la haie seule, a taille reelle et dans son cadre.

    python3 essai_haie.py && inkscape --export-type=png \
        --export-filename=essai_haie.png -w 1800 essai_haie.svg
"""
import construire as K
import haie

LARGEUR = 1800
CRETE, PIED = K.CIEL_BAS, K.HAIE_PIED
BANDE = PIED - CRETE + 120

DENSITES = [4.0, 10.0, 20.0]


def feuille():
    hauteur = BANDE * len(DENSITES)
    blocs = []
    for i, d in enumerate(DENSITES):
        dy = i * BANDE - CRETE + 60
        corps, n = haie.engendrer(LARGEUR, CRETE + dy, PIED + dy,
                                  indent=2, densite=d)
        blocs.append(
            u'  <rect x="0" y="%d" width="%d" height="%d" fill="%s"/>\n%s\n'
            u'  <text x="24" y="%d" font-family="sans-serif" font-size="28"'
            u' fill="#3A4A55">densite %.1f  -  %d formes</text>'
            % (i * BANDE, LARGEUR, BANDE, K.CIEL, corps,
               i * BANDE + 40, d, n))
    return u"""<svg xmlns="http://www.w3.org/2000/svg"
     width="%d" height="%d" viewBox="0 0 %d %d">
<defs>
%s
</defs>
%s
<!-- Le grain est un CALQUE POSE PAR-DESSUS. Applique au contenu lui-meme il
     le remplace : ce filtre ne lit jamais SourceGraphic. -->
<rect x="0" y="0" width="%d" height="%d" fill="#808080"
      filter="url(#grainGlobal)"/>
</svg>
""" % (LARGEUR, hauteur, LARGEUR, hauteur,
       K.grain_global("grainGlobal", 3, K.GRAIN_FORCE, K.GRAIN_FINESSE, "grain"),
       "\n".join(blocs), LARGEUR, hauteur)


if __name__ == "__main__":
    open("essai_haie.svg", "w").write(feuille())
    print("essai_haie.svg : %d densites" % len(DENSITES))
