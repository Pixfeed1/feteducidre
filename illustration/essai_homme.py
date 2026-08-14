# -*- coding: utf-8 -*-
u"""
Le banc d'essai de l'homme de la serviette.

Il le pose sur un fond de sable nu, a l'echelle finale de la scene
(1350/928 x 0.85 = 1.2365), et a cote en GRAND (x4) pour juger le trait.
La reference en face : ref_homme_serre.png, crop (860,700)-(1010,815)
de la 5e reference.

    python essai_homme.py
    inkscape --export-type=png --export-filename=essai_homme.png \
             -w 1200 essai_homme.svg
"""

import personnages

K_FINAL = (1350.0 / 928.0) * 0.85
SABLE = "#FAFAF6"

corps = [personnages.homme_serviette(180, 190, K_FINAL, 2),
         personnages.homme_serviette(700, 420, K_FINAL * 4.0, 2)]

svg = (u'<svg xmlns="http://www.w3.org/2000/svg"'
       u' xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"'
       u' width="1200" height="460" viewBox="0 0 1200 460">\n'
       u'  <rect x="0" y="0" width="1200" height="460" fill="%s"/>\n%s\n'
       u'</svg>\n') % (SABLE, u"\n".join(corps))

with open("essai_homme.svg", "w") as f:
    f.write(svg.encode("utf-8") if str is bytes else svg)
print(u"essai_homme.svg construit")
