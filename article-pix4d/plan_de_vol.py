"""
Le plan de vol type : 75 % devant, 60 % sur le côté.

    python3 article-pix4d/plan_de_vol.py

Produit `pix4d-plan-de-vol.webp`, son PNG et le SVG éditable.

----------------------------------------------------------------------------
CE QUE CETTE FIGURE REMPLACE
----------------------------------------------------------------------------
Une première version circulait hors charte : fond crème, titre bleu
marine, photos bleu vif et orange. Les valeurs sont identiques.

----------------------------------------------------------------------------
LE SCHÉMA EST CALCULÉ, PAS DESSINÉ À L'ESTIME
----------------------------------------------------------------------------
Rien n'est posé à la main. Le décalage de la deuxième photo vaut
(1 moins 75 %) de la largeur, l'écart entre deux lignes vaut
(1 moins 60 %) de la hauteur, l'espacement des déclenchements vaut ce
même décalage, et les lignes de vol sont espacées de ce même écart.

Les quatre grandeurs sortent donc des deux seuls pourcentages de
l'article. Un contrôle remesure ensuite les rectangles effectivement
tracés et refuse de dessiner si leur recouvrement n'est plus de 75 % et
de 60 % : une figure de géométrie qui ment sur sa géométrie ne sert à
rien.

----------------------------------------------------------------------------
LE « 8 À 12 » EST UNE DIVISION, PAS UN RELEVÉ
----------------------------------------------------------------------------
Quatre photos voient un même point sur une ligne, parce que le drone
avance d'un quart de photo entre deux déclenchements. Deux lignes et
demie le voient de côté, parce qu'elles sont espacées de deux cinquièmes
de photo. D'où huit à douze. Le calcul est refait à chaque dessin, et
les trois nombres de la colonne de droite en sortent.

----------------------------------------------------------------------------
NI ROUGE NI VERT
----------------------------------------------------------------------------
Deux photos qui se recouvrent, ce n'est pas un état sain contre un état
dégradé : c'est deux prises de vue. Elles prennent donc l'indigo de la
maison et l'ambre, les deux teintes neutres de la charte.
"""

import os

import charte as C
import dessin as D

L = 1600
MARGE = 56

INDIGO = C.VIOLET_TEXTE
AMBRE = (180, 83, 9)
PHOTO_1 = (238, 234, 250)       # l'aplat très pâle de la première photo
PHOTO_2 = (252, 242, 228)       # celui de la seconde
RECOUVREMENT = (226, 216, 240)  # là où les deux se superposent
SUIVANTE = (242, 241, 238)      # la photo de la ligne d'à côté

#  ---------------------------------------------------------------------------
#  LES DEUX SEULS CHIFFRES DE LA FIGURE
#
#  Tout le reste du schéma en découle : décalage, écart entre lignes,
#  espacement des déclenchements, et le nombre de photos par point.
#  ---------------------------------------------------------------------------
AVANT = 0.75              # recouvrement entre deux photos d'une même ligne
LATERAL = 0.60            # recouvrement entre deux lignes voisines

CAS_DIFFICILES = (("sur des champs", 0.80, 0.80),
                  ("en forêt", 0.85, 0.85),
                  ("sur la neige ou le sable", 0.85, 0.70))

POLICES = {
    "titre": (C.POLICE_G, 19, "bold"),
    "sous": (C.POLICE_R, 17, "normal"),
    "chiffre": (C.POLICE_G, 40, "bold"),
    "explique": (C.POLICE_R, 15, "normal"),
    "cote": (C.POLICE_G, 18, "bold"),
    "photo": (C.POLICE_G, 14, "bold"),
    "mention": (C.POLICE_R, 14, "normal"),
    "note": (C.POLICE_G, 15, "bold"),
}
FAMILLE_SVG = "Liberation Sans, Arial, Helvetica, sans-serif"

TITRE = "LE PLAN DE VOL TYPE : 75 % DEVANT, 60 % SUR LE CÔTÉ"
SOUS = ("recouvrement minimal conseillé par Pix4D dans le cas général, vu de "
        "dessus")

#  -------------------------------------------------------------  géométrie
W, H_PH = 212.0, 300.0    # la photo au sol, en pixels de dessin
PX, PY = 420.0, 222.0     # coin haut gauche de la première photo
X_PISTE = (124.0, 968.0)  # début et fin des lignes de vol
R_VIRAGE = 60.0
R_POINT = 4.5
X_TEXTE = 1104            # la colonne de droite


def rect(couche, b, r, teinte):
    return {"quoi": "rect", "couche": couche, "b": b, "r": r, "t": teinte}


def trait(couche, b, teinte, epaisseur, tirets=None):
    return {"quoi": "trait", "couche": couche, "b": b, "t": teinte,
            "e": epaisseur, "tirets": tirets}


def cadre(couche, b, teinte, epaisseur, tirets=None):
    return {"quoi": "cadre", "couche": couche, "b": b, "t": teinte,
            "e": epaisseur, "tirets": tirets}


def arc(couche, cx, cy, r, a0, a1, teinte, epaisseur):
    return {"quoi": "arc", "couche": couche, "cx": cx, "cy": cy, "r": r,
            "a0": a0, "a1": a1, "t": teinte, "e": epaisseur}


def disque(couche, cx, cy, r, teinte):
    return {"quoi": "disque", "couche": couche, "cx": cx, "cy": cy, "r": r,
            "t": teinte}


def fleche(couche, x0, y0, x1, y1, teinte, epaisseur):
    return {"quoi": "fleche", "couche": couche, "b": [x0, y0, x1, y1],
            "t": teinte, "e": epaisseur}


def texte(couche, xy, contenu, police, teinte, tracking=0.0, centre=False,
          droite=False):
    for c, nom in (("—", "cadratin"), ("–", "demi-cadratin")):
        if c in contenu:
            raise SystemExit("%s dans « %s »" % (nom, contenu[:60]))
    return {"quoi": "texte", "couche": couche, "xy": xy, "c": contenu,
            "p": police, "t": teinte, "tr": tracking, "centre": centre,
            "droite": droite}


def pourcent(v):
    return "%d %%" % round(v * 100)


def composer():
    mesure = D.Toile(L, 10)
    fontes = {k: mesure.police(f, t) for k, (f, t, _) in POLICES.items()}

    #  ------------------------------------------------------------------
    #  TOUT DÉCOULE DES DEUX POURCENTAGES
    #  ------------------------------------------------------------------
    for nom, v in (("avant", AVANT), ("latéral", LATERAL)):
        if not 0.0 < v < 1.0:
            raise SystemExit("le recouvrement %s vaut %.2f : ce n'est pas un "
                             "recouvrement" % (nom, v))

    pas_x = (1.0 - AVANT) * W      # ce dont le drone avance entre deux photos
    pas_y = (1.0 - LATERAL) * H_PH  # l'écart entre deux lignes de vol

    par_ligne = 1.0 / (1.0 - AVANT)
    par_cote = 1.0 / (1.0 - LATERAL)
    mini = int(round(par_ligne)) * int(par_cote)            # 4 x 2
    maxi = int(round(par_ligne)) * (int(par_cote) + 1)      # 4 x 3
    if mini != 8 or maxi != 12:
        raise SystemExit("le calcul donne %d à %d photos par point, "
                         "l'article annonce 8 à 12" % (mini, maxi))

    for ou, av, lat in CAS_DIFFICILES:
        if av < AVANT or lat < LATERAL:
            raise SystemExit("le cas « %s » demande moins que le cas "
                             "général : ce n'est plus un cas difficile" % ou)

    #  --------------------------------------------------------  rectangles
    p1 = [PX, PY, PX + W, PY + H_PH]
    p2 = [PX + pas_x, PY, PX + pas_x + W, PY + H_PH]
    rec = [p2[0], PY, p1[2], PY + H_PH]                 # le recouvrement
    suiv = [PX, PY + pas_y, PX + W, PY + pas_y + H_PH]  # la ligne suivante

    #  On remesure ce qui est réellement tracé, plutôt que de faire
    #  confiance au calcul d'au-dessus.
    mesure_av = (rec[2] - rec[0]) / W
    mesure_lat = (p1[3] - suiv[1]) / H_PH
    for nom, trouve, attendu in (("avant", mesure_av, AVANT),
                                 ("latéral", mesure_lat, LATERAL)):
        if abs(trouve - attendu) > 1e-9:
            raise SystemExit("les rectangles tracés donnent un recouvrement "
                             "%s de %.1f %%, la figure en annonce %.0f"
                             % (nom, trouve * 100, attendu * 100))

    lignes = [PY + H_PH / 2.0 + i * pas_y for i in range(3)]

    o = []
    o.append(texte("titre", (MARGE, 46), D.typo(TITRE), "titre", D.ENCRE,
                   2.2))
    sous = D.typo(SOUS)
    if mesure.mesure(sous, fontes["sous"]) > L - 2 * MARGE:
        raise SystemExit("le sous-titre déborde")
    o.append(texte("titre", (MARGE, 74), sous, "sous", D.FAIBLE))

    #  --------------------------------------------------------  les aplats
    aplats = [rect("aplats", suiv, 0, SUIVANTE),
              rect("aplats", p1, 0, PHOTO_1),
              rect("aplats", p2, 0, PHOTO_2),
              rect("aplats", rec, 0, RECOUVREMENT)]
    o.extend(aplats)

    #  ----------------------------------------------------  le trajet du vol
    #  Les déclenchements sont espacés de ce dont le drone avance entre
    #  deux photos : l'espacement des points EST le 25 %.
    piste = []
    for i, ly in enumerate(lignes):
        piste.append(trait("piste", [X_PISTE[0], ly, X_PISTE[1], ly],
                           D.FAIBLE, 2, tirets=(7, 7)))
        x = X_PISTE[0]
        while x <= X_PISTE[1] + 0.01:
            piste.append(disque("piste", x, ly, R_POINT, D.ENCRE))
            x += pas_x
        sens = 1 if i % 2 == 0 else -1
        mx = (X_PISTE[0] + X_PISTE[1]) / 2.0 + sens * 250
        piste.append(fleche("piste", mx - sens * 26, ly, mx + sens * 26, ly,
                            D.ENCRE, 2.4))

    #  Les virages, à droite puis à gauche, qui ferment le serpentin.
    piste.append(arc("piste", X_PISTE[1], (lignes[0] + lignes[1]) / 2.0,
                     R_VIRAGE, -90, 90, D.FAIBLE, 2))
    piste.append(arc("piste", X_PISTE[0], (lignes[1] + lignes[2]) / 2.0,
                     R_VIRAGE, 90, 270, D.FAIBLE, 2))
    o.extend(piste)

    #  ---------------------------------------------------------  les cadres
    cadres = [cadre("cadres", suiv, INDIGO, 2, tirets=(8, 6)),
              cadre("cadres", p1, INDIGO, 2),
              cadre("cadres", p2, AMBRE, 2)]
    o.extend(cadres)

    #  --------------------------------------------------------  les cotes
    cotes, libelles = [], []

    #  Le 75 %, au-dessus, sur la largeur du recouvrement.
    yc = PY - 28
    cotes.append(trait("cotes", [rec[0], yc, rec[2], yc], AMBRE, 2))
    for x in (rec[0], rec[2]):
        cotes.append(trait("cotes", [x, yc, x, yc + 12], AMBRE, 2))
    libelles.append(texte("cotes", ((rec[0] + rec[2]) / 2.0, yc - 26),
                          pourcent(AVANT), "cote", AMBRE, centre=True))

    #  Le 60 %, à gauche, sur la hauteur du recouvrement latéral.
    xc = PX - 26
    cotes.append(trait("cotes", [xc, suiv[1], xc, p1[3]], INDIGO, 2))
    for y in (suiv[1], p1[3]):
        cotes.append(trait("cotes", [xc, y, xc + 12, y], INDIGO, 2))
    libelles.append(texte("cotes", (xc - 12, (suiv[1] + p1[3]) / 2.0 - 11),
                          pourcent(LATERAL), "cote", INDIGO, droite=True))

    libelles.append(texte("cotes", (p1[0] - 14, PY + 6), "photo 1", "photo",
                          INDIGO, droite=True))
    libelles.append(texte("cotes", (p2[2] + 14, PY + 6), "photo 2", "photo",
                          AMBRE))
    libelles.append(texte("cotes", ((suiv[0] + suiv[2]) / 2.0, suiv[3] + 14),
                          D.typo("photo de la ligne suivante"), "photo",
                          INDIGO, centre=True))
    libelles.append(texte("cotes", (X_PISTE[0], lignes[0] - 42),
                          "sens du vol", "mention", D.GRIS))

    o.extend(cotes)
    o.extend(libelles)

    #  -------------------------------------------------  la colonne de droite
    entrees = []
    largeur = L - MARGE - X_TEXTE
    blocs = (
        (pourcent(AVANT), AMBRE,
         "entre deux photos d’une même ligne : le drone déclenche chaque "
         "fois qu’il a avancé d’un %s de photo."
         % ("quart" if abs(par_ligne - 4) < 1e-9 else "%.2f" % (1 / par_ligne))),
        (pourcent(LATERAL), INDIGO,
         "entre deux lignes voisines, espacées de %s de la largeur d’une "
         "photo." % pourcent(1 - LATERAL)),
        ("%d à %d" % (mini, maxi), D.ENCRE,
         "photos voient chaque point du sol : %d sur une même ligne, et "
         "%d ou %d lignes." % (round(par_ligne), int(par_cote),
                               int(par_cote) + 1)),
    )
    y = PY - 14
    for chiffre, teinte, propos in blocs:
        entrees.append(texte("colonne", (X_TEXTE, y), chiffre, "chiffre",
                             teinte))
        y += 56
        for ligne in mesure.couper(D.typo(propos), fontes["explique"],
                                   largeur):
            entrees.append(texte("colonne", (X_TEXTE, y), ligne, "explique",
                                 D.GRIS))
            y += 23
        y += 34
    if y > suiv[3] + 60:
        raise SystemExit("la colonne de droite descend à %d px, plus bas que "
                         "le schéma qui finit à %d" % (y, suiv[3]))
    o.extend(entrees)

    bas = max(y, suiv[3] + 52)
    note = D.typo("Cas difficiles : "
                  + ", ".join("%s et %s %s" % (pourcent(a), pourcent(l),
                                               ou)
                              for ou, a, l in CAS_DIFFICILES) + ".")
    if mesure.mesure(note, fontes["note"]) > L - 2 * MARGE:
        raise SystemExit("la ligne des cas difficiles déborde")
    o.append(texte("note", (MARGE, bas + 22), note, "note", D.ENCRE))

    Ht = int(bas + 84)
    o.insert(0, rect("fond", [0, 0, L, Ht], 0, D.PAPIER))
    return Ht, o, (mini, maxi, par_ligne, par_cote, pas_x, pas_y)


def rendre_matriciel(Ht, ordres, base):
    t = D.Toile(L, Ht)
    fontes = {k: t.police(f, taille) for k, (f, taille, _) in POLICES.items()}

    def lignes_du_cadre(b):
        x0, y0, x1, y1 = b
        return ([(x0, y0), (x1, y0)], [(x1, y0), (x1, y1)],
                [(x1, y1), (x0, y1)], [(x0, y1), (x0, y0)])

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
        elif a["quoi"] == "cadre":
            for seg in lignes_du_cadre(a["b"]):
                if a.get("tirets"):
                    plein, vide = a["tirets"]
                    t.pointilles(seg, a["t"], a["e"], plein, vide)
                else:
                    t.ligne([seg[0][0], seg[0][1], seg[1][0], seg[1][1]],
                            a["t"], a["e"])
        elif a["quoi"] == "arc":
            t.arc(a["cx"], a["cy"], a["r"], a["a0"], a["a1"], a["t"], a["e"])
        elif a["quoi"] == "disque":
            t.disque(a["cx"], a["cy"], a["r"], teinte=a["t"])
        elif a["quoi"] == "fleche":
            x0, y0, x1, y1 = a["b"]
            t.fleche(x0, y0, x1, y1, a["t"], a["e"])
        else:
            f = fontes[a["p"]]
            x, y = a["xy"]
            if a["centre"]:
                x -= t.mesure(a["c"], f) / 2.0
            elif a.get("droite"):
                x -= t.mesure(a["c"], f)
            if a["tr"]:
                t.espace((x, y), a["c"], f, a["t"], a["tr"])
            else:
                t.texte((x, y), a["c"], f, a["t"])
    D.enregistrer(t.final(L, Ht), base, L, Ht)


def rendre_svg(Ht, ordres, base):
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
           'version="1.1">' % (L, Ht, L, Ht),
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
            elif a["quoi"] == "cadre":
                x0, y0, x1, y1 = a["b"]
                out.append('    <rect x="%g" y="%g" width="%g" height="%g" '
                           'fill="none" stroke="%s" stroke-width="%g%s"/>'
                           % (x0, y0, x1 - x0, y1 - y0, teinte(a["t"]),
                              a["e"], tirets))
            elif a["quoi"] == "trait":
                x0, y0, x1, y1 = a["b"]
                out.append('    <line x1="%g" y1="%g" x2="%g" y2="%g" '
                           'stroke="%s" stroke-width="%g%s"/>'
                           % (x0, y0, x1, y1, teinte(a["t"]), a["e"], tirets))
            elif a["quoi"] == "arc":
                import math
                x0 = a["cx"] + a["r"] * math.cos(math.radians(a["a0"]))
                y0 = a["cy"] + a["r"] * math.sin(math.radians(a["a0"]))
                x1 = a["cx"] + a["r"] * math.cos(math.radians(a["a1"]))
                y1 = a["cy"] + a["r"] * math.sin(math.radians(a["a1"]))
                out.append('    <path d="M %g %g A %g %g 0 0 1 %g %g" '
                           'fill="none" stroke="%s" stroke-width="%g"/>'
                           % (x0, y0, a["r"], a["r"], x1, y1,
                              teinte(a["t"]), a["e"]))
            elif a["quoi"] == "disque":
                out.append('    <circle cx="%g" cy="%g" r="%g" fill="%s"/>'
                           % (a["cx"], a["cy"], a["r"], teinte(a["t"])))
            elif a["quoi"] == "fleche":
                x0, y0, x1, y1 = a["b"]
                s = 1 if x1 > x0 else -1
                out.append('    <line x1="%g" y1="%g" x2="%g" y2="%g" '
                           'stroke="%s" stroke-width="%g"/>'
                           % (x0, y0, x1 - s * 7, y1, teinte(a["t"]), a["e"]))
                out.append('    <polygon points="%g,%g %g,%g %g,%g" '
                           'fill="%s"/>'
                           % (x1, y1, x1 - s * 11, y1 - 6, x1 - s * 11,
                              y1 + 6, teinte(a["t"])))
            else:
                _, taille, graisse = POLICES[a["p"]]
                espacement = (' letter-spacing="%g"' % a["tr"]
                              if a["tr"] else "")
                ancre = ""
                if a["centre"]:
                    ancre = ' text-anchor="middle"'
                elif a.get("droite"):
                    ancre = ' text-anchor="end"'
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
                        "pix4d-plan-de-vol")
    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5),
               ("faible", D.FAIBLE, 3.0), ("indigo", INDIGO, 4.5),
               ("ambre", AMBRE, 4.5))

    Ht, ordres, infos = composer()
    rendre_matriciel(Ht, ordres, base)
    couches, textes = rendre_svg(Ht, ordres, base)
    mini, maxi, par_ligne, par_cote, pas_x, pas_y = infos

    print()
    print("  %-38s %.0f Ko"
          % (os.path.basename(base + ".svg"),
             os.path.getsize(base + ".svg") / 1024.0))
    print("  %d x %d, %d calques, %d textes" % (L, Ht, couches, textes))
    print()
    print("  recouvrement avant   %s   le drone avance de %s de photo"
          % (pourcent(AVANT), pourcent(1 - AVANT)))
    print("  recouvrement latéral %s   lignes espacées de %s de photo"
          % (pourcent(LATERAL), pourcent(1 - LATERAL)))
    print("  déclenchements espacés de %.1f px, lignes de %.1f px"
          % (pas_x, pas_y))
    print()
    print("  %.0f photos par point sur une ligne, %.1f lignes de côté"
          % (par_ligne, par_cote))
    print("  soit %d à %d photos par point du sol" % (mini, maxi))


if __name__ == "__main__":
    principal()
