"""
Dix-huit versions du Bluetooth, et quatre qui ont changé l'usage.

    python3 article-bluetooth-versions/frise_versions.py

Produit `bluetooth-versions-frise.webp`, son PNG et le SVG éditable.

----------------------------------------------------------------------------
L'AXE EST PROPORTIONNEL, ET C'EST TOUT L'INTÉRÊT
----------------------------------------------------------------------------
Dix-huit versions réparties régulièrement ne diraient rien. Posées sur
un axe proportionnel, elles montrent ce que l'article affirme : la norme
accélère. Sept versions pour les onze premières années, huit pour les
sept dernières.

Les trois dernières se suivent de six mois. À cette échelle, 6.1 et 6.3
ne tiennent plus sur la même ligne que leurs voisines et descendent
d'un cran. Ce n'est pas un défaut de mise en page, c'est la cadence
semestrielle qui se voit : la figure se bouscule là où la norme se
bouscule.

----------------------------------------------------------------------------
DEUX ÉTAGES, DEUX PUBLICS
----------------------------------------------------------------------------
Au-dessus de l'axe, les quatre versions qui ont changé quelque chose
pour le lecteur, avec ce qu'elles ont apporté. Au-dessous, les dix-huit,
sans commentaire. Le haut raconte, le bas recense.

----------------------------------------------------------------------------
UNE DATE DISCUTÉE, ET ELLE EST SIGNALÉE
----------------------------------------------------------------------------
La 1.1 est datée de 2001 par le Bluetooth SIG et de 2002 par l'IEEE,
qui l'a ratifiée comme 802.15.1. La frise retient 2001, la date du
consortium, comme pour toutes les autres versions.
"""

import os

import charte as C
import dessin as D

L = 1600
MARGE = 56

INDIGO = C.VIOLET_TEXTE
INDIGO_PALE = (178, 158, 234)

DEBUT, FIN = 1999.2, 2026.7

#  ---------------------------------------------------------------------------
#  LES DIX-HUIT VERSIONS
#
#  `an` est la date d'adoption par le Bluetooth SIG, en années décimales.
#  `apport` n'est rempli que pour les quatre versions mises en avant, et
#  `prof` écarte deux de leurs blocs qui se croiseraient.
#  ---------------------------------------------------------------------------
VERSIONS = (
    {"v": "1.0", "an": 1999.50, "annee": "1999"},
    {"v": "1.1", "an": 2001.10, "annee": "2001"},
    {"v": "1.2", "an": 2003.85, "annee": "2003"},
    {"v": "2.0", "an": 2004.85, "annee": "2004"},
    {"v": "2.1", "an": 2007.55, "annee": "2007", "prof": 0,
     "apport": "l’appairage simplifié, sans code à taper"},
    {"v": "3.0", "an": 2009.30, "annee": "2009"},
    {"v": "4.0", "an": 2010.50, "annee": "2010", "prof": 1,
     "apport": "le Low Energy, et avec lui les objets connectés"},
    {"v": "4.1", "an": 2013.95, "annee": "2013"},
    {"v": "4.2", "an": 2014.95, "annee": "2014"},
    {"v": "5.0", "an": 2016.93, "annee": "2016", "prof": 0,
     "apport": "quatre fois la portée, deux fois le débit"},
    {"v": "5.1", "an": 2019.05, "annee": "2019"},
    {"v": "5.2", "an": 2020.02, "annee": "2020", "prof": 1,
     "apport": "les bases de LE Audio"},
    {"v": "5.3", "an": 2021.50, "annee": "2021"},
    {"v": "5.4", "an": 2023.10, "annee": "2023"},
    {"v": "6.0", "an": 2024.67, "annee": "2024"},
    {"v": "6.1", "an": 2025.35, "annee": "2025"},
    {"v": "6.2", "an": 2025.84, "annee": "2025"},
    {"v": "6.3", "an": 2026.35, "annee": "2026"},
)

#  Ce que l'article annonce, et que la figure doit retrouver seule.
ANNONCES = {"versions": 18, "mises en avant": 4, "années couvertes": 27}
CADENCE = {"depuis": 2025.0, "par an": 2}

POLICES = {
    "titre": (C.POLICE_G, 19, "bold"),
    "sous": (C.POLICE_R, 17, "normal"),
    "phare": (C.POLICE_G, 18, "bold"),
    "apport": (C.POLICE_R, 15, "normal"),
    "num": (C.POLICE_G, 16, "bold"),
    "annee": (C.POLICE_R, 12, "normal"),
    "note": (C.POLICE_R, 14, "normal"),
}
FAMILLE_SVG = "Liberation Sans, Arial, Helvetica, sans-serif"

TITRE = "DIX-HUIT VERSIONS EN VINGT-SEPT ANS, QUATRE QUI COMPTENT"
SOUS = ("dates d’adoption par le Bluetooth SIG, de la 1.0 en juillet 1999 à "
        "la 6.3 en mai 2026")
NOTE = ("Depuis 2025, il sort deux versions par an : les trois dernières se "
        "suivent de six mois.")

AXE_Y = 330
AXE_X0, AXE_X1 = 112, L - 108
LARGEUR_BLOC = 260
ECART = 30                # de l'axe au premier bloc
PAS_PROFONDEUR = 84
H_BLOC = 66
H_RANGEE = 44             # entre les deux rangées de numéros
ECART_NUM = 22            # de l'axe à la première rangée


def rect(couche, b, r, teinte):
    return {"quoi": "rect", "couche": couche, "b": b, "r": r, "t": teinte}


def trait(couche, b, teinte, epaisseur):
    return {"quoi": "trait", "couche": couche, "b": b, "t": teinte,
            "e": epaisseur}


def disque(couche, cx, cy, r, teinte):
    return {"quoi": "disque", "couche": couche, "cx": cx, "cy": cy, "r": r,
            "t": teinte}


def texte(couche, xy, contenu, police, teinte, tracking=0.0, centre=False):
    for c, nom in (("—", "cadratin"), ("–", "demi-cadratin")):
        if c in contenu:
            raise SystemExit("%s dans « %s »" % (nom, contenu[:60]))
    return {"quoi": "texte", "couche": couche, "xy": xy, "c": contenu,
            "p": police, "t": teinte, "tr": tracking, "centre": centre}


def composer():
    mesure = D.Toile(L, 10)
    fontes = {k: mesure.police(f, t) for k, (f, t, _) in POLICES.items()}

    phares = [v for v in VERSIONS if "apport" in v]

    #  ------------------------------------------------------------------
    #  CONTRÔLES
    #  ------------------------------------------------------------------
    trouve = {"versions": len(VERSIONS), "mises en avant": len(phares),
              "années couvertes": int(round(VERSIONS[-1]["an"]
                                            - VERSIONS[0]["an"]))}
    for quoi, attendu in ANNONCES.items():
        if trouve[quoi] != attendu:
            raise SystemExit("l'article annonce %d %s, la figure en compte %d"
                             % (attendu, quoi, trouve[quoi]))

    for a, b in zip(VERSIONS, VERSIONS[1:]):
        if b["an"] <= a["an"]:
            raise SystemExit("« %s » et « %s » ne sont pas dans l'ordre"
                             % (a["v"], b["v"]))
        if int(a["an"]) != int(a["annee"]):
            raise SystemExit("« %s » est posée en %.2f et étiquetée %s"
                             % (a["v"], a["an"], a["annee"]))
    for v in VERSIONS:
        if not DEBUT <= v["an"] <= FIN:
            raise SystemExit("« %s » sort de l'axe" % v["v"])

    #  La cadence semestrielle annoncée par l'article : deux versions par
    #  an depuis 2025. C'est elle qui fait se bousculer la fin de la frise.
    recentes = [v for v in VERSIONS if v["an"] >= CADENCE["depuis"]]
    annees = {v["annee"] for v in recentes}
    for a in sorted(annees)[:-1]:          # l'année en cours est incomplète
        n = sum(1 for v in recentes if v["annee"] == a)
        if n != CADENCE["par an"]:
            raise SystemExit("l'article annonce %d versions par an depuis "
                             "%d, la figure en compte %d en %s"
                             % (CADENCE["par an"], CADENCE["depuis"], n, a))

    etendue = FIN - DEBUT

    def abscisse(an):
        return AXE_X0 + (an - DEBUT) / etendue * (AXE_X1 - AXE_X0)

    o = []
    o.append(texte("titre", (MARGE, 46), D.typo(TITRE), "titre", D.ENCRE,
                   2.2))
    sous = D.typo(SOUS)
    if mesure.mesure(sous, fontes["sous"]) > L - 2 * MARGE:
        raise SystemExit("le sous-titre déborde")
    o.append(texte("titre", (MARGE, 74), sous, "sous", D.FAIBLE))

    #  ---------------------------------------------------------------  axe
    axe = [trait("axe", [AXE_X0 - 14, AXE_Y, AXE_X1 + 14, AXE_Y],
                 INDIGO_PALE, 5)]
    o.extend(axe)

    #  ------------------------------------------  les quatre mises en avant
    tiges, blocs, boites = [], [], []
    for v in phares:
        x = abscisse(v["an"])
        lignes = mesure.couper(D.typo(v["apport"]), fontes["apport"],
                               LARGEUR_BLOC)
        if len(lignes) > 2:
            raise SystemExit("l'apport de « %s » tient en %d lignes"
                             % (v["v"], len(lignes)))

        depart = ECART + v["prof"] * PAS_PROFONDEUR
        bas = AXE_Y - depart
        haut = bas - H_BLOC

        #  Premier jet : tous les blocs à droite de leur tige. Celle de la
        #  4.0, qui monte d'un cran plus haut, traversait « l'appairage
        #  simplifié », et celle de la 5.2 coupait « quatre fois la
        #  portée ». Les blocs du cran bas passent donc à gauche de leur
        #  tige, texte rangé sur le bord droit : la tige touche alors le
        #  coin du bloc au lieu de le barrer.
        a_gauche = v["prof"] == 0
        if a_gauche:
            droite = x - 14
            gauche = droite - LARGEUR_BLOC
        else:
            gauche = x + 14
            droite = gauche + LARGEUR_BLOC
        if gauche < MARGE or droite > L - MARGE:
            raise SystemExit("le bloc de « %s » sort du cadre" % v["v"])

        tiges.append(trait("tiges", [x, AXE_Y, x, bas], INDIGO, 2))

        def pose(yy, contenu, police, teinte):
            gx = (droite - mesure.mesure(contenu, fontes[police])
                  if a_gauche else gauche)
            blocs.append(texte("phares", (gx, yy), contenu, police, teinte))

        pose(haut, D.typo("%s, en %s" % (v["v"], v["annee"])), "phare",
             INDIGO)
        y = haut + 26
        for ligne in lignes:
            pose(y, ligne, "apport", D.GRIS)
            y += 21

        boites.append({"prof": v["prof"], "g": gauche, "d": droite,
                       "haut": haut, "bas": bas, "x": x, "v": v["v"]})

    for i, a in enumerate(boites):
        for b in boites[i + 1:]:
            if a["prof"] == b["prof"] and a["g"] < b["d"] and b["g"] < a["d"]:
                raise SystemExit("les blocs de « %s » et « %s » se "
                                 "chevauchent : changez la profondeur de "
                                 "l'un des deux" % (a["v"], b["v"]))

    #  Et aucune tige ne doit barrer le bloc d'une autre version : c'est le
    #  défaut qu'on ne voit qu'une fois l'image tirée.
    for a in boites:
        for b in boites:
            if b is a:
                continue
            if (b["g"] - 6 < a["x"] < b["d"] + 6
                    and a["bas"] < b["bas"] and b["haut"] < AXE_Y):
                raise SystemExit("la tige de « %s » barre le bloc de « %s »"
                                 % (a["v"], b["v"]))

    #  ------------------------------------------------  les dix-huit numéros
    #  Chaque numéro se range sur la première rangée libre. Quand deux
    #  versions se suivent de trop près, la seconde descend d'un cran :
    #  c'est la cadence semestrielle qui déborde de sa ligne.
    reperes, numeros = [], []
    fin_rangee = {}
    rangees = {}

    for v in VERSIONS:
        x = abscisse(v["an"])
        demi = max(mesure.mesure(v["v"], fontes["num"]),
                   mesure.mesure(v["annee"], fontes["annee"])) / 2.0

        rang = 0
        while fin_rangee.get(rang, -1e9) + 8 > x - demi:
            rang += 1
            if rang > 1:
                raise SystemExit("« %s » ne tient sur aucune des deux "
                                 "rangées : il en faudrait une troisième"
                                 % v["v"])
        fin_rangee[rang] = x + demi
        rangees[v["v"]] = rang

        y = AXE_Y + ECART_NUM + rang * H_RANGEE
        phare = "apport" in v
        reperes.append(disque("axe", x, AXE_Y, 7 if phare else 4,
                              INDIGO if phare else INDIGO_PALE))
        if rang:
            reperes.append(trait("axe", [x, AXE_Y + 6, x, y - 4],
                                 INDIGO_PALE, 1))
        numeros.append(texte("numeros", (x, y), v["v"], "num",
                             INDIGO if phare else D.ENCRE, centre=True))
        numeros.append(texte("numeros", (x, y + 19), v["annee"], "annee",
                             D.FAIBLE, centre=True))

        if x - demi < MARGE or x + demi > L - MARGE:
            raise SystemExit("le numéro de « %s » sort du cadre" % v["v"])

    o.extend(reperes)
    o.extend(tiges)
    o.extend(blocs)
    o.extend(numeros)

    bas_figure = AXE_Y + ECART_NUM + max(rangees.values()) * H_RANGEE + 38
    note = D.typo(NOTE)
    if mesure.mesure(note, fontes["note"]) > L - 2 * MARGE:
        raise SystemExit("la note déborde")
    o.append(texte("note", (MARGE, bas_figure + 22), note, "note", D.FAIBLE))

    H = int(bas_figure + 72)
    o.insert(0, rect("fond", [0, 0, L, H], 0, D.PAPIER))
    return H, o, rangees


def rendre_matriciel(H, ordres, base):
    t = D.Toile(L, H)
    fontes = {k: t.police(f, taille) for k, (f, taille, _) in POLICES.items()}
    for a in ordres:
        if a["quoi"] == "rect":
            t.rrect(a["b"], a["r"], teinte=a["t"])
        elif a["quoi"] == "trait":
            t.ligne(a["b"], a["t"], a["e"])
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
            if a["quoi"] == "rect":
                x0, y0, x1, y1 = a["b"]
                out.append('    <rect x="%g" y="%g" width="%g" height="%g" '
                           'rx="%g" fill="%s"/>'
                           % (x0, y0, x1 - x0, y1 - y0, a["r"],
                              teinte(a["t"])))
            elif a["quoi"] == "trait":
                x0, y0, x1, y1 = a["b"]
                out.append('    <line x1="%g" y1="%g" x2="%g" y2="%g" '
                           'stroke="%s" stroke-width="%g" '
                           'stroke-linecap="round"/>'
                           % (x0, y0, x1, y1, teinte(a["t"]), a["e"]))
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
                        "bluetooth-versions-frise")
    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5),
               ("indigo", INDIGO, 4.5), ("faible", D.FAIBLE, 3.0))

    H, ordres, rangees = composer()
    rendre_matriciel(H, ordres, base)
    couches, textes = rendre_svg(H, ordres, base)

    print()
    print("  %-38s %.0f Ko"
          % (os.path.basename(base + ".svg"),
             os.path.getsize(base + ".svg") / 1024.0))
    print("  %d x %d, %d calques, %d textes" % (L, H, couches, textes))
    print()
    for v in VERSIONS:
        print("  %-5s %-6s rangée %d%s"
              % (v["v"], v["annee"], rangees[v["v"]],
                 "   " + v["apport"] if "apport" in v else ""))
    bas = [v["v"] for v in VERSIONS if rangees[v["v"]]]
    print()
    print("  descendues d'un cran, faute de place : %s" % ", ".join(bas))


if __name__ == "__main__":
    principal()
