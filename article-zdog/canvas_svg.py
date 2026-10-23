"""
Zdog en Canvas et en SVG : le temps par image, selon le nombre de formes.

    python3 article-zdog/canvas_svg.py

Produit `zdog-canvas-svg.webp`, son PNG et le SVG éditable.

----------------------------------------------------------------------------
NEUF AFFIRMATIONS DE L'ARTICLE, NEUF CONTRÔLES
----------------------------------------------------------------------------
C'est la figure du banc d'essai : si elle dérive d'une virgule, la
section entière de l'article devient fausse. Tout ce que le texte
affirme est donc recalculé ici à partir des vingt-huit mesures, et le
dessin s'arrête à la première divergence.

  la fourchette de 1,5 à 3,3 fois          les quatorze rapports
  « le Canvas l'emporte partout »          les quatorze rapports
  le Canvas en 500 px ne décroche jamais   le seuil des 16,7 ms
  les trois autres franchissements         le seuil des 16,7 ms
  « moins de 7 ms » jusqu'à 200 formes     le maximum de la colonne
  le facteur 2,6 du Canvas entre les deux tailles
  le facteur 1,4 du SVG entre les deux tailles

----------------------------------------------------------------------------
L'AXE DES FORMES N'EST PAS PROPORTIONNEL, ET IL LE DIT
----------------------------------------------------------------------------
Les sept nombres de formes doublent à chaque cran. Posés à égale
distance, ils donnent des courbes lisibles ; posés proportionnellement,
les six premiers s'écraseraient contre l'origine. L'axe porte donc la
mention « échelle doublée à chaque cran », sans quoi la figure
laisserait croire à une croissance linéaire.

----------------------------------------------------------------------------
NI ROUGE NI VERT
----------------------------------------------------------------------------
Deux modes de rendu, ce n'est pas un état sain contre un état dégradé :
c'est un choix technique. Indigo pour le Canvas, ambre pour le SVG, les
deux teintes neutres de la charte. La seule ligne qui signale quelque
chose est celle des 16,7 ms, et elle est en gris : au-dessus, le lecteur
perd ses 60 images par seconde, dans les deux modes indifféremment.
"""

import os

import charte as C
import dessin as D

L = 1600
MARGE = 56

CANVAS = C.VIOLET_TEXTE
SVG = (180, 83, 9)

FORMES = (50, 100, 200, 400, 800, 1600, 3200)
SEUIL = 1000.0 / 60.0     # 16,7 ms, la barre des 60 images par seconde

#  ---------------------------------------------------------------------------
#  LE BANC D'ESSAI
#
#  Temps par image en millisecondes, médiane de trois essais de 120 images.
#  Relevé jurojin du 23 octobre 2026, Zdog 1.1.3, Chromium 141 sans carte
#  graphique, deux coeurs, cadence non bridée.
#  ---------------------------------------------------------------------------
PANNEAUX = (
    {"titre": "Image de 500 × 500 pixels",
     "canvas": (0.8, 1.2, 1.4, 2.3, 4.3, 6.7, 12.7),
     "svg": (2.1, 3.9, 3.6, 6.1, 8.8, 14.7, 37.7)},
    {"titre": "Image de 1 500 × 1 500 pixels",
     "canvas": (2.1, 2.8, 4.0, 5.2, 8.5, 15.1, 33.5),
     "svg": (3.1, 5.7, 6.5, 11.0, 18.4, 26.3, 53.3)},
)

#  Ce que l'article affirme, et que le dessin doit retrouver seul.
FOURCHETTE = (1.5, 3.3)           # « de 1,5 à 3,3 fois plus vite »
SANS_DEPART = 7.0                 # « moins de 7 ms » pour quelques dizaines
FORMES_SANS_DEPART = 200
FRANCHISSEMENTS = {
    (0, "canvas"): None,          # le Canvas en 500 px ne décroche jamais
    (0, "svg"): (1600, 3200),
    (1, "canvas"): (1600, 3200),
    (1, "svg"): (400, 800),
}
FACTEURS_TAILLE = {"canvas": 2.6, "svg": 1.4}

POLICES = {
    "titre": (C.POLICE_G, 19, "bold"),
    "sous": (C.POLICE_R, 17, "normal"),
    "legende": (C.POLICE_R, 15, "normal"),
    "panneau": (C.POLICE_G, 17, "bold"),
    "valeur": (C.POLICE_G, 16, "bold"),
    "axe": (C.POLICE_R, 13, "normal"),
    "mention": (C.POLICE_R, 14, "normal"),
    "note": (C.POLICE_G, 15, "bold"),
}
FAMILLE_SVG = "Liberation Sans, Arial, Helvetica, sans-serif"

TITRE = "LE CANVAS DESSINE ZDOG 1,5 À 3,3 FOIS PLUS VITE QUE LE SVG"
SOUS = ("temps pour calculer et afficher une image, selon le nombre de "
        "formes (millisecondes, médiane de trois essais)")
PHRASE = ("Une illustration de 200 formes tient largement les 60 images "
          "par seconde, dans les deux modes et aux deux tailles.")
PIED = ("Banc d’essai jurojin du 23 octobre 2026 : Zdog 1.1.3, Chromium "
        "141 sans carte graphique (rendu logiciel, 2 cœurs), cadence non "
        "bridée.")
SIGNATURE = "jurojin.net"

HAUTEUR = 900             # format demandé pour cette figure
Y_LEGENDE = 142
Y_PANNEAU = 196
Y_HAUT = 250              # le 60 ms
Y_BAS = 700               # le zéro
ECHELLE_MAX = 60.0
PAS_GRADUATION = 20
X_PAS = 96                # entre deux crans de l'axe des formes
R_POINT = 4.5


def rect(couche, b, r, teinte):
    return {"quoi": "rect", "couche": couche, "b": b, "r": r, "t": teinte}


def trait(couche, b, teinte, epaisseur, tirets=None):
    return {"quoi": "trait", "couche": couche, "b": b, "t": teinte,
            "e": epaisseur, "tirets": tirets}


def polyligne(couche, points, teinte, epaisseur):
    return {"quoi": "polyligne", "couche": couche, "pts": points,
            "t": teinte, "e": epaisseur}


def disque(couche, cx, cy, r, teinte):
    return {"quoi": "disque", "couche": couche, "cx": cx, "cy": cy, "r": r,
            "t": teinte}


def texte(couche, xy, contenu, police, teinte, tracking=0.0, centre=False):
    for c, nom in (("—", "cadratin"), ("–", "demi-cadratin")):
        if c in contenu:
            raise SystemExit("%s dans « %s »" % (nom, contenu[:60]))
    return {"quoi": "texte", "couche": couche, "xy": xy, "c": contenu,
            "p": police, "t": teinte, "tr": tracking, "centre": centre}


def ms(v):
    return ("%.1f" % v).replace(".", ",")


def formes_lues(n):
    return "3 200" if n == 3200 else "1 600" if n == 1600 else str(n)


def composer():
    mesure = D.Toile(L, 10)
    fontes = {k: mesure.police(f, t) for k, (f, t, _) in POLICES.items()}

    #  ------------------------------------------------------------------
    #  LES NEUF CONTRÔLES
    #  ------------------------------------------------------------------
    for p in PANNEAUX:
        for mode in ("canvas", "svg"):
            if len(p[mode]) != len(FORMES):
                raise SystemExit("« %s » donne %d mesures en %s pour %d "
                                 "nombres de formes"
                                 % (p["titre"], len(p[mode]), mode,
                                    len(FORMES)))

    rapports = [p["svg"][i] / p["canvas"][i]
                for p in PANNEAUX for i in range(len(FORMES))]
    if min(rapports) <= 1.0:
        raise SystemExit("l'article écrit que le Canvas l'emporte partout, "
                         "mais le SVG passe devant une fois au moins "
                         "(rapport minimal %.2f)" % min(rapports))
    #  On compare à un demi-pas d'arrondi près, et non au round() de
    #  Python : 3,9 / 1,2 vaut exactement 3,25, que l'arrondi commercial
    #  de l'article écrit 3,3 et que Python, qui arrondit au pair,
    #  ramènerait à 3,2. Le contrôle doit vérifier l'article, pas la
    #  convention d'arrondi de l'interpréteur.
    for trouve, attendu, bout in ((min(rapports), FOURCHETTE[0], "basse"),
                                  (max(rapports), FOURCHETTE[1], "haute")):
        if abs(trouve - attendu) > 0.051:
            raise SystemExit("l'article annonce une borne %s de %.1f, les "
                             "mesures donnent %.2f" % (bout, attendu, trouve))

    for j, p in enumerate(PANNEAUX):
        for mode in ("canvas", "svg"):
            au_dessus = [i for i, v in enumerate(p[mode]) if v > SEUIL]
            attendu = FRANCHISSEMENTS[(j, mode)]
            trouve = (None if not au_dessus
                      else (FORMES[au_dessus[0] - 1], FORMES[au_dessus[0]]))
            if trouve != attendu:
                raise SystemExit("en %s sur « %s », l'article place le "
                                 "franchissement des 16,7 ms à %s et les "
                                 "mesures à %s"
                                 % (mode, p["titre"], attendu, trouve))

    i200 = FORMES.index(FORMES_SANS_DEPART)
    pire = max(p[m][i] for p in PANNEAUX for m in ("canvas", "svg")
               for i in range(i200 + 1))
    if pire >= SANS_DEPART:
        raise SystemExit("l'article écrit « moins de %.0f ms » jusqu'à %d "
                         "formes, le maximum mesuré est %.1f"
                         % (SANS_DEPART, FORMES_SANS_DEPART, pire))

    for mode, attendu in FACTEURS_TAILLE.items():
        trouve = PANNEAUX[1][mode][-1] / PANNEAUX[0][mode][-1]
        if abs(trouve - attendu) > 0.051:
            raise SystemExit("l'article annonce un facteur %.1f en %s entre "
                             "les deux tailles, les mesures donnent %.2f"
                             % (attendu, mode, trouve))

    plus_haut = max(p[m][i] for p in PANNEAUX for m in ("canvas", "svg")
                    for i in range(len(FORMES)))
    if plus_haut > ECHELLE_MAX:
        raise SystemExit("une mesure atteint %.1f ms et l'axe s'arrête à %.0f"
                         % (plus_haut, ECHELLE_MAX))

    def ordonnee(v):
        return Y_BAS - v / ECHELLE_MAX * (Y_BAS - Y_HAUT)

    o = []
    o.append(texte("titre", (MARGE, 46), D.typo(TITRE), "titre", D.ENCRE,
                   2.2))
    sous = D.typo(SOUS)
    if mesure.mesure(sous, fontes["sous"]) > L - 2 * MARGE:
        raise SystemExit("le sous-titre déborde")
    o.append(texte("titre", (MARGE, 74), sous, "sous", D.FAIBLE))

    #  -----------------------------------------------------------  légende
    legende = []
    x = MARGE
    for teinte, mot in ((CANVAS, "Canvas"), (SVG, "SVG")):
        legende.append(trait("legende", [x, Y_LEGENDE + 9, x + 30,
                                         Y_LEGENDE + 9], teinte, 3))
        legende.append(disque("legende", x + 15, Y_LEGENDE + 9, R_POINT,
                              teinte))
        legende.append(texte("legende", (x + 40, Y_LEGENDE), mot, "legende",
                             D.ENCRE))
        x += 40 + mesure.mesure(mot, fontes["legende"]) + 44
    legende.append(trait("legende", [x, Y_LEGENDE + 9, x + 30, Y_LEGENDE + 9],
                         D.GRIS, 2, tirets=(6, 5)))
    m = D.typo("%s ms : au-dessus, l’animation passe sous 60 images par "
               "seconde" % ms(SEUIL))
    legende.append(texte("legende", (x + 40, Y_LEGENDE), m, "legende",
                         D.GRIS))
    if x + 40 + mesure.mesure(m, fontes["legende"]) > L - MARGE:
        raise SystemExit("la légende déborde")
    o.extend(legende)

    #  -----------------------------------------------------------  panneaux
    largeur = (L - 2 * MARGE - 60) / 2.0
    pleine = (len(FORMES) - 1) * X_PAS
    grilles, courbes, points, etiquettes = [], [], [], []

    for j, p in enumerate(PANNEAUX):
        gx = MARGE + j * (largeur + 60)
        x0 = gx + 46                       # après la colonne des graduations
        if x0 + pleine > gx + largeur - 60:
            raise SystemExit("les sept crans font %d px pour un panneau de %d"
                             % (pleine, largeur))

        etiquettes.append(texte("panneaux", (gx, Y_PANNEAU),
                                D.typo(p["titre"]), "panneau", D.ENCRE))

        v = 0
        while v <= ECHELLE_MAX + 0.01:
            y = ordonnee(v)
            grilles.append(trait("grilles", [x0 - 10, y, x0 + pleine + 10, y],
                                 D.FILET, 1))
            grilles.append(texte("grilles", (x0 - 18, y - 8), str(int(v)),
                                 "axe", D.FAIBLE))
            v += PAS_GRADUATION

        ys = ordonnee(SEUIL)
        grilles.append(trait("grilles", [x0 - 10, ys, x0 + pleine + 10, ys],
                             D.GRIS, 2, tirets=(6, 5)))

        for mode, teinte in (("svg", SVG), ("canvas", CANVAS)):
            pts = [(x0 + i * X_PAS, ordonnee(val))
                   for i, val in enumerate(p[mode])]
            courbes.append(polyligne("courbes", pts, teinte, 3))
            for px, py in pts:
                points.append(disque("points", px, py, R_POINT, teinte))

            #  Seule la dernière valeur est écrite : c'est elle que
            #  l'article cite, et sept étiquettes par courbe feraient
            #  vingt-huit nombres dans une figure qui en montre déjà la forme.
            lab = ms(p[mode][-1])
            bx, by = pts[-1]
            etiquettes.append(texte("valeurs", (bx + 14, by - 10), lab,
                                    "valeur", teinte))
            if bx + 14 + mesure.mesure(lab, fontes["valeur"]) > gx + largeur:
                raise SystemExit("« %s » sort de son panneau" % lab)

        for i, n in enumerate(FORMES):
            etiquettes.append(texte("axes", (x0 + i * X_PAS, Y_BAS + 14),
                                    formes_lues(n), "axe", D.FAIBLE,
                                    centre=True))
        mention = D.typo("nombre de formes (échelle doublée à chaque cran)")
        etiquettes.append(texte("axes", (x0 + pleine / 2.0, Y_BAS + 40),
                                mention, "mention", D.GRIS, centre=True))

    o.extend(grilles)
    o.extend(courbes)
    o.extend(points)
    o.extend(etiquettes)

    note = D.typo(PHRASE)
    pied = D.typo(PIED)
    for t, police in ((note, "note"), (pied, "mention")):
        if mesure.mesure(t, fontes[police]) > L - 2 * MARGE:
            raise SystemExit("« %s » déborde" % t[:40])
    o.append(texte("note", (MARGE, Y_BAS + 92), note, "note", D.ENCRE))
    o.append(texte("pied", (MARGE, Y_BAS + 128), pied, "mention", D.FAIBLE))
    #  La signature se cale sur la marge droite : on la mesure plutôt que
    #  d'ajouter une ancre de texte pour un seul mot.
    o.append(texte("pied",
                   (L - MARGE - mesure.mesure(SIGNATURE, fontes["mention"]),
                    Y_BAS + 128), SIGNATURE, "mention", D.FAIBLE))

    H = HAUTEUR
    if Y_BAS + 150 > H:
        raise SystemExit("le pied descend à %d px pour une image de %d"
                         % (Y_BAS + 150, H))
    o.insert(0, rect("fond", [0, 0, L, H], 0, D.PAPIER))
    return H, o, (min(rapports), max(rapports), pire)


def rendre_matriciel(H, ordres, base):
    t = D.Toile(L, H)
    fontes = {k: t.police(f, taille) for k, (f, taille, _) in POLICES.items()}
    for a in ordres:
        if a["quoi"] == "rect":
            t.rrect(a["b"], a["r"], teinte=a["t"])
        elif a["quoi"] == "trait":
            if a.get("tirets"):
                plein, vide = a["tirets"]
                x0, y0, x1, y1 = a["b"]
                t.pointilles([(x0, y0), (x1, y1)], a["t"], a["e"], plein,
                             vide)
            else:
                t.ligne(a["b"], a["t"], a["e"])
        elif a["quoi"] == "polyligne":
            t.polyligne(a["pts"], a["t"], a["e"])
        elif a["quoi"] == "disque":
            t.disque(a["cx"], a["cy"], a["r"], teinte=a["t"])
        else:
            f = fontes[a["p"]]
            x, y = a["xy"]
            if a["centre"]:
                x -= t.mesure(a["c"], f) / 2.0
            if a["tr"]:
                t.espace((x, y), a["c"], f, a["t"], a["tr"])
            else:
                t.texte((x, y), a["c"], f, a["t"])
    D.enregistrer(t.final(L, H), base, L, H)


def rendre_svg(H, ordres, base):
    montees = {c: C.police(f, t).getmetrics()[0]
               for c, (f, t, _) in POLICES.items()}

    def teinte(t):
        return "#%02x%02x%02x" % tuple(t)

    def propre(s):
        return (s.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;"))

    couches = []
    for a in ordres:
        if not couches or couches[-1][0] != a["couche"]:
            couches.append((a["couche"], []))
        couches[-1][1].append(a)

    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<svg xmlns="http://www.w3.org/2000/svg" '
           'xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
           'width="%dpx" height="%dpx" viewBox="0 0 %d %d" '
           'version="1.1">' % (L, H, L, H),
           '  <title>%s</title>' % propre(TITRE),
           '  <desc>%s</desc>' % propre(SOUS)]

    for i, (nom, groupe) in enumerate(couches):
        out.append('  <g inkscape:groupmode="layer" inkscape:label="%s" '
                   'id="couche%d">' % (nom, i + 1))
        for a in groupe:
            tirets = ('" stroke-dasharray="%g %g'
                      % a["tirets"]) if a.get("tirets") else ""
            if a["quoi"] == "rect":
                x0, y0, x1, y1 = a["b"]
                out.append('    <rect x="%g" y="%g" width="%g" height="%g" '
                           'rx="%g" fill="%s"/>'
                           % (x0, y0, x1 - x0, y1 - y0, a["r"],
                              teinte(a["t"])))
            elif a["quoi"] == "trait":
                x0, y0, x1, y1 = a["b"]
                out.append('    <line x1="%g" y1="%g" x2="%g" y2="%g" '
                           'stroke="%s" stroke-width="%g%s"/>'
                           % (x0, y0, x1, y1, teinte(a["t"]), a["e"], tirets))
            elif a["quoi"] == "polyligne":
                pts = " ".join("%g,%g" % p for p in a["pts"])
                out.append('    <polyline points="%s" fill="none" '
                           'stroke="%s" stroke-width="%g" '
                           'stroke-linecap="round" stroke-linejoin="round"/>'
                           % (pts, teinte(a["t"]), a["e"]))
            elif a["quoi"] == "disque":
                out.append('    <circle cx="%g" cy="%g" r="%g" fill="%s"/>'
                           % (a["cx"], a["cy"], a["r"], teinte(a["t"])))
            else:
                _, taille, graisse = POLICES[a["p"]]
                espacement = (' letter-spacing="%g"' % a["tr"]
                              if a["tr"] else "")
                ancre = ' text-anchor="middle"' if a["centre"] else ""
                out.append('    <text x="%g" y="%g" font-family="%s" '
                           'font-size="%g" font-weight="%s" fill="%s"%s%s'
                           ' xml:space="preserve">%s</text>'
                           % (a["xy"][0], a["xy"][1] + montees[a["p"]],
                              FAMILLE_SVG, taille, graisse, teinte(a["t"]),
                              espacement, ancre, propre(a["c"])))
        out.append('  </g>')
    out.append('</svg>')

    with open(base + ".svg", "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    return len(couches), sum(1 for a in ordres if a["quoi"] == "texte")


def principal():
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "zdog-canvas-svg")
    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5),
               ("faible", D.FAIBLE, 3.0), ("canvas", CANVAS, 4.5),
               ("svg", SVG, 4.5))

    H, ordres, infos = composer()
    rendre_matriciel(H, ordres, base)
    couches, textes = rendre_svg(H, ordres, base)
    bas, haut, pire = infos

    print()
    print("  %-38s %.0f Ko"
          % (os.path.basename(base + ".svg"),
             os.path.getsize(base + ".svg") / 1024.0))
    print("  %d x %d, %d calques, %d textes" % (L, H, couches, textes))
    print()
    print("  %-26s %s" % ("formes",
                          " ".join("%6s" % formes_lues(n) for n in FORMES)))
    for p in PANNEAUX:
        for mode in ("canvas", "svg"):
            print("  %-26s %s"
                  % ("%s  %s" % (p["titre"][9:21].strip(), mode),
                     " ".join("%6s" % ms(v) for v in p[mode])))
    print()
    print("  le Canvas l'emporte de x%.2f à x%.2f  (article : 1,5 à 3,3)"
          % (bas, haut))
    print("  jusqu'à %d formes, au pire %s ms  (article : moins de 7)"
          % (FORMES_SANS_DEPART, ms(pire)))


if __name__ == "__main__":
    principal()
