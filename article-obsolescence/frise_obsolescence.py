"""
Dix ans de dossier obsolescence programmée, en cinq jalons.

    python3 article-obsolescence/frise_obsolescence.py

Produit `obsolescence-frise-2015-2025.webp`, son PNG et le SVG éditable.

----------------------------------------------------------------------------
L'AXE EST PROPORTIONNEL, ET C'EST TOUT L'INTÉRÊT
----------------------------------------------------------------------------
Une frise à jalons régulièrement espacés est un tableau déguisé : elle range
des événements dans l'ordre et perd la seule chose qu'une frise sait dire,
la durée qui les sépare. Les positions sont donc calculées sur la date,
graduation annuelle à l'appui.

Ce que ça donne à voir tient en deux vides. Trois ans entre la création du
délit et la lettre d'Apple, pendant lesquels le texte existe sans servir.
Trois ans de nouveau entre la loi de 2021 et le règlement européen, après
une réforme censée débloquer les poursuites. Un lecteur voit ces deux
silences avant de lire une seule ligne.

----------------------------------------------------------------------------
TROIS JALONS SUR CINQ N'ONT QU'UNE ANNÉE
----------------------------------------------------------------------------
L'article date précisément deux événements, le 28 décembre 2017 et le 15
novembre 2021. Les trois autres ne portent qu'un millésime : 2015, 2020,
2025. Ils sont donc posés au premier jour de leur année, et le pied le dit.

Inventer un mois pour « faire joli sur l'axe » déplacerait un jalon de
plusieurs dizaines de pixels, dans une figure dont la position EST
l'information. C'est le genre de faux qui ne se voit jamais et qui fausse
tout.

----------------------------------------------------------------------------
DEUX FAMILLES DE COULEUR, PARCE QU'IL Y A DEUX HISTOIRES
----------------------------------------------------------------------------
Le brief demande une couleur pour les jalons législatifs et une autre pour
les jalons Apple. Ce n'est pas décoratif : la frise raconte deux séries qui
ne se répondent presque pas. Le législateur écrit un texte en 2015 et le
retouche en 2021 ; Apple bride en 2017 et transige en 2020. Les couleurs
rendent visible que la seconde série ne doit rien à la première, ce qui est
exactement le propos de la section « Trois plaintes, dix ans, zéro
condamnation ».

----------------------------------------------------------------------------
CE QUI MANQUE ENCORE, ET QUI N'EST PAS INVENTÉ
----------------------------------------------------------------------------
Le cinquième jalon, le règlement européen de 2025, n'est décrit nulle part
dans l'extrait fourni : il n'apparaît que dans le texte alternatif et dans
la légende de l'image. Sa ligne ne dit donc que ce que ces deux-là
affirment, à savoir qu'il entre en application et que c'est le seul jalon
qui change quelque chose. Dès que le paragraphe correspondant arrive, la
constante `JALONS` le porte en une ligne.
"""

import os

import charte as C
import dessin as D

L = 1600
MARGE = 56

VIOLET = (98, 44, 200)
AMBRE = (180, 83, 9)

#  ---------------------------------------------------------------------------
#  LES CINQ JALONS
#
#  `annee` est la position sur l'axe, en années décimales. `precis` dit si
#  l'article donne un jour ou seulement un millésime : c'est ce drapeau que
#  le pied de figure rapporte, et il évite de faire passer une approximation
#  pour une date.
#  ---------------------------------------------------------------------------
JALONS = (
    {"annee": 2015.0, "precis": False, "famille": "loi",
     "date": "2015",
     "titre": "L’obsolescence programmée devient un délit",
     "detail": "Deux ans d’emprisonnement et 300 000 € d’amende, jusqu’à "
               "5 % du chiffre d’affaires annuel moyen."},

    {"annee": 2017.0 + 362 / 365.0, "precis": True, "famille": "apple",
     "date": "28 décembre 2017",
     "titre": "Apple reconnaît le bridage dans une lettre à ses clients",
     "detail": "Dans la même lettre, la batterie de remplacement passe de "
               "79 à 29 dollars pour toute l’année 2018."},

    {"annee": 2020.0, "precis": False, "famille": "apple",
     "date": "2020",
     "titre": "Transaction pénale avec la DGCCRF, pour tromperie",
     "detail": "Un accord qui évite le procès : aucun juge n’a tranché sur "
               "le fond, et l’infraction porte sur le silence, pas sur le "
               "bridage."},

    {"annee": 2021.0 + 318 / 365.0, "precis": True, "famille": "loi",
     "date": "15 novembre 2021",
     "titre": "La loi empreinte environnementale simplifie le texte",
     "detail": "Elle retire la condition de prouver la volonté d’augmenter "
               "le taux de remplacement, jugée hors d’atteinte."},

    {"annee": 2025.0, "precis": False, "famille": "loi",
     "date": "2025",
     "titre": "Un règlement européen prend le relais",
     "detail": "Le seul jalon de cette frise qui change quelque chose, "
               "d’après l’article."},
)

FAMILLES = {
    "loi": {"teinte": VIOLET, "fond": (238, 232, 252),
            "libelle": "jalon législatif"},
    "apple": {"teinte": AMBRE, "fond": (250, 240, 228),
              "libelle": "jalon Apple"},
}

POLICES = {
    "titre": (C.POLICE_G, 19, "bold"),
    "sous": (C.POLICE_R, 17, "normal"),
    "date": (C.POLICE_G, 16, "bold"),
    "jalon": (C.POLICE_G, 16, "bold"),
    "detail": (C.POLICE_R, 14, "normal"),
    "annee": (C.POLICE_R, 13, "normal"),
    "legende": (C.POLICE_R, 14, "normal"),
    "pied": (C.POLICE_R, 16, "normal"),
}
FAMILLE_SVG = "Liberation Sans, Arial, Helvetica, sans-serif"

TITRE = "DIX ANS DE DOSSIER, ZÉRO CONDAMNATION"
SOUS = ("les cinq jalons de l’obsolescence programmée en France, du délit "
        "créé en 2015 au règlement européen de 2025")

#  L'axe.
AXE_Y = 476
AXE_X0 = 116
AXE_X1 = 1496
LARGEUR_CARTE = 302
BAS_HAUT = 424        # les cartes du dessus s'alignent par le bas
HAUT_BAS = 528        # celles du dessous par le haut


def rect(couche, b, r, teinte):
    return {"quoi": "rect", "couche": couche, "b": b, "r": r, "t": teinte}


def cadre(couche, b, r, teinte, epaisseur=2):
    return {"quoi": "cadre", "couche": couche, "b": b, "r": r, "t": teinte,
            "e": epaisseur}


def trait(couche, b, teinte, epaisseur):
    return {"quoi": "trait", "couche": couche, "b": b, "t": teinte,
            "e": epaisseur}


def disque(couche, cx, cy, r, teinte, contour=None):
    return {"quoi": "disque", "couche": couche, "cx": cx, "cy": cy, "r": r,
            "t": teinte, "contour": contour}


def texte(couche, xy, contenu, police, teinte, tracking=0.0, centre=False):
    for c, nom in (("—", "cadratin"), ("–", "demi-cadratin")):
        if c in contenu:
            raise SystemExit("%s dans « %s »" % (nom, contenu[:60]))
    return {"quoi": "texte", "couche": couche, "xy": xy, "c": contenu,
            "p": police, "t": teinte, "tr": tracking, "centre": centre}


def composer():
    mesure = D.Toile(L, 10)
    fontes = {k: mesure.police(f, t) for k, (f, t, _) in POLICES.items()}

    #  ------------------------------------------------------------------
    #  CONTRÔLES
    #  ------------------------------------------------------------------
    if len(JALONS) != 5:
        raise SystemExit("le brief demande cinq jalons, la table en a %d"
                         % len(JALONS))
    for a, b in zip(JALONS, JALONS[1:]):
        if b["annee"] <= a["annee"]:
            raise SystemExit("les jalons ne sont pas dans l'ordre : %s puis %s"
                             % (a["date"], b["date"]))
    familles = {j["famille"] for j in JALONS}
    if familles != set(FAMILLES):
        raise SystemExit(
            "le brief demande deux familles de couleur, la table en utilise "
            "%s" % sorted(familles))

    debut, fin = JALONS[0]["annee"], JALONS[-1]["annee"]
    duree = fin - debut

    def abscisse(annee):
        return AXE_X0 + (annee - debut) / duree * (AXE_X1 - AXE_X0)

    o = []
    o.append(texte("titre", (MARGE, 46), TITRE, "titre", D.ENCRE, 2.2))
    sous = D.typo(SOUS)
    if mesure.mesure(sous, fontes["sous"]) > L - 2 * MARGE:
        raise SystemExit("le sous-titre déborde")
    o.append(texte("titre", (MARGE, 74), sous, "sous", D.FAIBLE))
    o.append(trait("titre", [MARGE, 124, L - MARGE, 124], D.FILET, 2))

    #  ------------------------------------------------------------  légende
    x = MARGE
    for cle in ("loi", "apple"):
        f = FAMILLES[cle]
        o.append(disque("titre", x + 7, 150, 7, f["teinte"]))
        o.append(texte("titre", (x + 22, 141), f["libelle"], "legende",
                       D.GRIS))
        x += 22 + mesure.mesure(f["libelle"], fontes["legende"]) + 40

    #  ---------------------------------------------------------------  axe
    o.append(trait("axe", [AXE_X0 - 16, AXE_Y, AXE_X1 + 16, AXE_Y],
                   D.FILET, 3))
    #  Une graduation par année : sans elle, rien ne dit que l'axe est
    #  proportionnel, et la frise redevient une liste.
    an = int(debut)
    while an <= int(fin):
        gx = abscisse(an)
        o.append(trait("axe", [gx, AXE_Y - 6, gx, AXE_Y + 6], D.FILET, 2))
        if an in (int(debut), int(fin)):
            o.append(texte("axe", (gx, AXE_Y + 14), str(an), "annee",
                           D.FAIBLE, centre=True))
        an += 1

    #  ------------------------------------------------------------  cartes
    dessus = []
    for i, j in enumerate(JALONS):
        f = FAMILLES[j["famille"]]
        gauche = abscisse(j["annee"]) - LARGEUR_CARTE / 2.0
        gauche = max(MARGE, min(gauche, L - MARGE - LARGEUR_CARTE))
        largeur_texte = LARGEUR_CARTE - 36

        lignes_t = mesure.couper(D.typo(j["titre"]), fontes["jalon"],
                                 largeur_texte)
        lignes_d = mesure.couper(D.typo(j["detail"]), fontes["detail"],
                                 largeur_texte)
        if len(lignes_t) > 3 or len(lignes_d) > 4:
            raise SystemExit("le jalon %s ne tient pas dans sa carte"
                             % j["date"])
        hauteur = 20 + 22 + 8 + len(lignes_t) * 21 + 10 + len(lignes_d) * 19 \
            + 18
        dessus.append((j, f, gauche, lignes_t, lignes_d, hauteur))

    hauteur = max(d[5] for d in dessus)

    #  TROIS PASSES, ET PAS UNE BOUCLE UNIQUE.
    #
    #  Émis carte par carte, les ordres découpaient le SVG en vingt calques
    #  dont « cartes » et « textes » revenaient cinq fois chacun : dans
    #  Inkscape, autant d'entrées homonymes à ouvrir une à une. On sépare
    #  donc les rappels, les cartes et les textes en trois passes.
    boites = []
    for i, (j, f, gauche, lignes_t, lignes_d, _) in enumerate(dessus):
        haut = (BAS_HAUT - hauteur) if i % 2 == 0 else HAUT_BAS
        boites.append((j, f, gauche, haut, lignes_t, lignes_d))

    for i, (j, f, gauche, haut, _, _) in enumerate(boites):
        y_bord = (haut + hauteur) if i % 2 == 0 else haut
        o.append(trait("rappels", [abscisse(j["annee"]), y_bord,
                                   abscisse(j["annee"]), AXE_Y],
                       f["teinte"], 2))

    for j, f, gauche, haut, _, _ in boites:
        b = [gauche, haut, gauche + LARGEUR_CARTE, haut + hauteur]
        o.append(rect("cartes", b, 10, D.BLANC))
        o.append(cadre("cartes", b, 10, f["teinte"], 2))
        o.append(rect("cartes", [gauche, haut, gauche + LARGEUR_CARTE,
                                 haut + 6], 3, f["teinte"]))

    for j, f, gauche, haut, lignes_t, lignes_d in boites:
        x0 = gauche + 18
        y = haut + 20
        o.append(texte("textes", (x0, y), j["date"], "date", f["teinte"]))
        y += 30
        for ligne in lignes_t:
            o.append(texte("textes", (x0, y), ligne, "jalon", D.ENCRE))
            y += 21
        y += 10
        for ligne in lignes_d:
            o.append(texte("textes", (x0, y), ligne, "detail", D.GRIS))
            y += 19

    for j in JALONS:
        f = FAMILLES[j["famille"]]
        o.append(disque("pastilles", abscisse(j["annee"]), AXE_Y, 10,
                        D.BLANC))
        o.append(disque("pastilles", abscisse(j["annee"]), AXE_Y, 7,
                        f["teinte"]))

    #  ---------------------------------------------------------------  pied
    approx = [j["date"] for j in JALONS if not j["precis"]]
    ecart_1 = JALONS[1]["annee"] - JALONS[0]["annee"]
    ecart_2 = JALONS[4]["annee"] - JALONS[3]["annee"]
    pied = (
        "Trois des cinq jalons ne sont datés que par leur année dans "
        "l’article, %s. Ils sont posés au premier jour de leur année plutôt "
        "qu’à une date précise qui serait inventée ; seuls 2017 et 2021 "
        "portent un jour." % ", ".join(approx),
        "L’axe est proportionnel au temps écoulé, les graduations marquent "
        "les années. C’est ce qui donne à voir près de trois ans entre "
        "la création du délit et la lettre d’Apple, puis les trois ans qui "
        "suivent la réforme de 2021.",
        "Une transaction pénale n’est pas une condamnation, c’est un accord "
        "qui évite le procès. Aucune condamnation n’a été prononcée sur le "
        "fondement de l’article L441-2 depuis sa création.",
    )
    #  Le pied parle de « près de trois ans » et de « trois ans » : deux
    #  contrôles vérifient que les écarts calculés le permettent encore.
    if not 2.7 <= ecart_1 <= 3.0:
        raise SystemExit("le pied annonce près de trois ans, l'écart est de "
                         "%.2f ans" % ecart_1)
    if not 3.0 <= ecart_2 <= 3.3:
        raise SystemExit("le pied annonce trois ans, l'écart est de %.2f ans"
                         % ecart_2)

    bas_cartes = max(HAUT_BAS + hauteur, BAS_HAUT)
    y_pied = bas_cartes + 40
    o.append(trait("pied", [MARGE, y_pied, L - MARGE, y_pied], D.FILET, 2))
    y_texte = y_pied + 22
    for i, ligne in enumerate(pied):
        lignes = mesure.couper(D.typo(ligne), fontes["pied"], L - 2 * MARGE)
        if len(lignes) > 2:
            raise SystemExit("la ligne %d du pied tient en %d lignes"
                             % (i + 1, len(lignes)))
        for coupee in lignes:
            o.append(texte("pied", (MARGE, y_texte), coupee, "pied",
                           D.FAIBLE))
            y_texte += 24
        y_texte += 6

    H = int(y_texte + 20)
    o.insert(0, rect("fond", [0, 0, L, H], 0, D.PAPIER))
    return H, o, (ecart_1, ecart_2)


def rendre_matriciel(H, ordres, base):
    t = D.Toile(L, H)
    fontes = {k: t.police(f, taille) for k, (f, taille, _) in POLICES.items()}
    for a in ordres:
        if a["quoi"] == "rect":
            t.rrect(a["b"], a["r"], teinte=a["t"])
        elif a["quoi"] == "cadre":
            t.rrect(a["b"], a["r"], contour=a["t"], epaisseur=a["e"])
        elif a["quoi"] == "trait":
            t.ligne(a["b"], a["t"], a["e"])
        elif a["quoi"] == "disque":
            t.disque(a["cx"], a["cy"], a["r"], teinte=a["t"],
                     contour=a["contour"], epaisseur=2)
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
    mesure = D.Toile(L, 10)
    fontes = {k: mesure.police(f, t) for k, (f, t, _) in POLICES.items()}
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
            if a["quoi"] in ("rect", "cadre"):
                x0, y0, x1, y1 = a["b"]
                if a["quoi"] == "rect":
                    peinture = 'fill="%s"' % teinte(a["t"])
                else:
                    peinture = ('fill="none" stroke="%s" stroke-width="%g"'
                                % (teinte(a["t"]), a["e"]))
                out.append('    <rect x="%g" y="%g" width="%g" height="%g" '
                           'rx="%g" %s/>'
                           % (x0, y0, x1 - x0, y1 - y0, a["r"], peinture))
            elif a["quoi"] == "trait":
                x0, y0, x1, y1 = a["b"]
                out.append('    <line x1="%g" y1="%g" x2="%g" y2="%g" '
                           'stroke="%s" stroke-width="%g"/>'
                           % (x0, y0, x1, y1, teinte(a["t"]), a["e"]))
            elif a["quoi"] == "disque":
                bord = ('' if not a["contour"] else
                        ' stroke="%s" stroke-width="2"' % teinte(a["contour"]))
                out.append('    <circle cx="%g" cy="%g" r="%g" fill="%s"%s/>'
                           % (a["cx"], a["cy"], a["r"], teinte(a["t"]), bord))
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
                        "obsolescence-frise-2015-2025")
    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5),
               ("violet", VIOLET, 4.5), ("ambre", AMBRE, 4.5))

    H, ordres, ecarts = composer()
    rendre_matriciel(H, ordres, base)
    couches, textes = rendre_svg(H, ordres, base)

    print("  %-44s %.0f Ko"
          % (os.path.basename(base + ".svg"),
             os.path.getsize(base + ".svg") / 1024.0))
    print("  %d calques, %d textes" % (couches, textes))
    print()
    for j in JALONS:
        print("  %-18s %-7s %s"
              % (j["date"], FAMILLES[j["famille"]]["libelle"].split()[-1],
                 "date exacte" if j["precis"] else "année seule"))
    print()
    print("  écart 2015 vers la lettre d'Apple : %.2f ans" % ecarts[0])
    print("  écart 2021 vers 2025              : %.2f ans" % ecarts[1])


if __name__ == "__main__":
    principal()
