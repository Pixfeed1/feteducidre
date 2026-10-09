"""
Le DUF a chassé l'OBJ des décors Daz.

    python3 article-daz-decors/decors_duf_seul.py

Produit `daz-decors-duf-seul.webp`, son PNG et le SVG éditable.

----------------------------------------------------------------------------
DES COLONNES AUX ANNÉES RELEVÉES, PAS UNE COURBE
----------------------------------------------------------------------------
L'article couvre dix-sept ans mais ne chiffre que cinq années : 2010,
2011, 2016, 2025 et 2026. Tracer une courbe continue affirmerait qu'on a
mesuré les douze autres, et le lecteur lirait les valeurs intermédiaires
comme des données.

Les colonnes ne se dressent donc qu'aux années chiffrées, sur un axe qui
reste proportionnel au temps. Le vide entre 2016 et 2025 est alors
visible, et il est honnête : c'est le trou de la source, pas un trou
dans le marché.

----------------------------------------------------------------------------
LES DEUX SÉRIES NE SONT PAS COMPLÉMENTAIRES
----------------------------------------------------------------------------
En 2010, 94 % des décors existaient aussi en OBJ et 0 % étaient en DUF
seul, puisque le format n'existe pas encore : il naît avec Daz Studio
4.5, en 2012. Les deux font 94 et non 100, parce que 6 % ne sortaient
ni en OBJ ni en DUF, mais en .daz ou au format Poser.

Déduire une série de l'autre serait donc faux. L'OBJ n'a qu'une seule
valeur dans l'article, 2010 : il est posé comme repère de départ et non
comme série, et un contrôle refuse que la somme soit traitée comme 100.

----------------------------------------------------------------------------
LE PLANCHER DE 2021 EST UNE AFFIRMATION, PAS UN POINT
----------------------------------------------------------------------------
« Depuis 2021, la part ne descend plus sous 93 % » ne donne pas la
valeur de 2021 : elle donne une borne basse valable pour toutes les
années suivantes. Elle est donc dessinée comme un seuil horizontal
courant de 2021 à 2026, et surtout pas comme une colonne de 93 % en
2021, ce qui inventerait une mesure.
"""

import os

import charte as C
import dessin as D

L = 1600
MARGE = 56

INDIGO = C.VIOLET_TEXTE
AMBRE = (180, 83, 9)

#  ---------------------------------------------------------------------------
#  LES ANNÉES CHIFFRÉES PAR L'ARTICLE
#
#  `compte` n'est renseigné que là où l'article publie les effectifs.
#  ---------------------------------------------------------------------------
DUF_SEUL = (
    {"an": 2011, "part": 0.0, "compte": None,
     "note": "le DUF n’existe pas encore", "ligne": 1},
    {"an": 2016, "part": 60.0, "compte": None, "note": "la bascule",
     "ligne": 0},
    {"an": 2025, "part": None, "compte": (915, 919), "note": "",
     "ligne": 0},
    {"an": 2026, "part": 99.0, "compte": None, "note": "",
     "ligne": 0},
)

#  L'OBJ n'a qu'une valeur dans l'article : un repère, pas une série.
OBJ_2010 = {"an": 2010, "part": 94.0,
            "libelle": "aussi en OBJ", "ligne": 0}

#  Première apparition, sans chiffre publié.
PREMIERS_DUF = 2012

#  « Depuis 2021, la part ne descend plus sous 93 % » : une borne, pas un
#  point de mesure.
SEUIL = {"depuis": 2021, "part": 93.0,
         "libelle": "depuis 2021, jamais sous 93 %"}

DEBUT, FIN = 2010, 2026
PLAFOND = 100.0

POLICES = {
    "titre": (C.POLICE_G, 19, "bold"),
    "sous": (C.POLICE_R, 17, "normal"),
    "legende": (C.POLICE_R, 14, "normal"),
    "valeur": (C.POLICE_G, 17, "bold"),
    "effectif": (C.POLICE_R, 13, "normal"),
    "annee": (C.POLICE_G, 15, "bold"),
    "note": (C.POLICE_R, 13, "normal"),
    "seuil": (C.POLICE_G, 14, "bold"),
    "ordonnee": (C.POLICE_R, 13, "normal"),
}
FAMILLE_SVG = "Liberation Sans, Arial, Helvetica, sans-serif"

TITRE = "L’OBJ A QUITTÉ LES DÉCORS DE LA BOUTIQUE DAZ"
SOUS = ("part des nouveaux décors vendus au seul format DUF, aux seules "
        "années que l’article chiffre : entre elles, rien n’a été mesuré")

HAUT, BAS = 236, 592
X0, X1 = 148, 1496
LARGEUR_COL = 52


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


def pourcent(v):
    s = ("%.1f" % v).replace(".", ",")
    return (s[:-2] if s.endswith(",0") else s) + " %"


def composer():
    mesure = D.Toile(L, 10)
    fontes = {k: mesure.police(f, t) for k, (f, t, _) in POLICES.items()}

    #  ------------------------------------------------------------------
    #  CONTRÔLES
    #  ------------------------------------------------------------------
    for d in DUF_SEUL:
        if d["compte"]:
            n, total = d["compte"]
            d["part"] = 100.0 * n / total
        if d["part"] is None:
            raise SystemExit("%d n'a ni part ni effectif" % d["an"])
        if not DEBUT <= d["an"] <= FIN:
            raise SystemExit("%d sort de l'axe" % d["an"])

    #  La progression doit monter jusqu'à l'année la mieux documentée.
    montee = [d for d in DUF_SEUL if d["an"] <= 2025]
    for a, b in zip(montee, montee[1:]):
        if b["part"] <= a["part"]:
            raise SystemExit(
                "la part recule entre %d (%.1f) et %d (%.1f) : ce n'est plus "
                "une bascule" % (a["an"], a["part"], b["an"], b["part"]))

    #  Le plancher que l'article affirme vaut pour TOUTES les années qui
    #  suivent 2021, pas seulement pour celle-là.
    for d in DUF_SEUL:
        if d["an"] >= SEUIL["depuis"] and d["part"] < SEUIL["part"]:
            raise SystemExit(
                "%d tombe à %.1f %% alors que l'article annonce un plancher "
                "de %.0f %% depuis %d"
                % (d["an"], d["part"], SEUIL["part"], SEUIL["depuis"]))

    #  LES DEUX SÉRIES NE SOMMENT PAS À 100, et c'est le fait à ne pas
    #  perdre : en 2010, 6 % des décors ne sortaient ni en OBJ ni en DUF.
    duf_2010 = 0.0
    if abs(OBJ_2010["part"] + duf_2010 - 100.0) < 0.5:
        raise SystemExit(
            "les deux parts de 2010 somment à 100 : l'une se déduirait de "
            "l'autre, et la figure n'aurait plus besoin de deux sources")

    etendue = float(FIN - DEBUT)

    def abscisse(an):
        return X0 + (an - DEBUT) / etendue * (X1 - X0)

    def ordonnee(p):
        return BAS - (p / PLAFOND) * (BAS - HAUT)

    o = []
    o.append(texte("titre", (MARGE, 46), TITRE, "titre", D.ENCRE, 2.2))
    lignes_s = mesure.couper(D.typo(SOUS), fontes["sous"], L - 2 * MARGE)
    if len(lignes_s) > 2:
        raise SystemExit("le sous-titre tient en %d lignes" % len(lignes_s))
    y = 74
    for ligne in lignes_s:
        o.append(texte("titre", (MARGE, y), ligne, "sous", D.FAIBLE))
        y += 24

    x = MARGE
    for libelle, teinte_l in (("au seul format DUF", INDIGO),
                              ("existait aussi en OBJ", AMBRE)):
        o.append(rect("titre", [x, y + 10, x + 22, y + 24], 4, teinte_l))
        o.append(texte("titre", (x + 32, y + 8), libelle, "legende", D.GRIS))
        x += 32 + mesure.mesure(libelle, fontes["legende"]) + 40

    #  ------------------------------------------------------------  grille
    grille, graduations = [], []
    for p in range(0, int(PLAFOND) + 1, 25):
        gy = ordonnee(p)
        grille.append(trait("grille", [MARGE + 10, gy, X1 + 30, gy],
                            D.FILET, 1))
        graduations.append(texte("grille", (MARGE + 2, gy - 8),
                                 "%d %%" % p, "ordonnee", D.FAIBLE))
    o.extend(grille)
    o.extend(graduations)

    #  --------------------------------------------------------------  seuil
    sy = ordonnee(SEUIL["part"])
    sx = abscisse(SEUIL["depuis"])
    o.append(trait("seuil", [sx, sy, X1 + 30, sy], AMBRE, 2))
    o.append(trait("seuil", [sx, sy - 10, sx, sy + 10], AMBRE, 2))
    o.append(texte("seuil", (sx + 12, sy - 26), SEUIL["libelle"], "seuil",
                   AMBRE))

    #  -----------------------------------------------------------  colonnes
    barres, valeurs, annees, notes = [], [], [], []

    #  Les notes d'axe s'échelonnent sur plusieurs lignes.
    #
    #  2010, 2011 et 2012 ne sont séparés que de quatre-vingts pixels. Au
    #  premier rendu, leurs trois libellés se chevauchaient en une bouillie
    #  illisible. Chacun porte donc sa ligne, et le contrôle plus bas
    #  refuse deux notes qui se croiseraient sur la même.
    posees = []

    def poser(an, part, teinte, compte=None, note="", sous_libelle="",
              ligne=0):
        cx = abscisse(an)
        hy = ordonnee(part)
        hauteur = max(BAS - hy, 3)
        barres.append(rect("colonnes",
                           [cx - LARGEUR_COL / 2.0, BAS - hauteur,
                            cx + LARGEUR_COL / 2.0, BAS], 4, teinte))
        sommet = BAS - hauteur
        if compte:
            valeurs.append(texte("valeurs", (cx, sommet - 26),
                                 "%d sur %d" % compte, "effectif", D.FAIBLE,
                                 centre=True))
            hy_v = sommet - 48
        else:
            hy_v = sommet - 26
        valeurs.append(texte("valeurs", (cx, hy_v), pourcent(part),
                             "valeur", teinte, centre=True))
        annees.append(texte("années", (cx, BAS + 14), str(an), "annee",
                            D.ENCRE, centre=True))
        for contenu, teinte_n in ((note, D.FAIBLE), (sous_libelle, AMBRE)):
            if not contenu:
                continue
            large = mesure.mesure(contenu, fontes["note"])
            notes.append(texte("années", (cx, BAS + 36 + ligne * 22),
                               contenu, "note", teinte_n, centre=True))
            posees.append((ligne, cx - large / 2.0, cx + large / 2.0,
                           contenu))

    poser(OBJ_2010["an"], OBJ_2010["part"], AMBRE,
          sous_libelle=OBJ_2010["libelle"], ligne=OBJ_2010["ligne"])
    for d in DUF_SEUL:
        poser(d["an"], d["part"], INDIGO, d["compte"], d["note"],
              ligne=d["ligne"])

    #  Le jalon de 2012 n'a pas de chiffre : un repère sur l'axe, pas une
    #  colonne. Lui en donner une obligerait à inventer sa hauteur.
    jx = abscisse(PREMIERS_DUF)
    jalon = "les premiers décors en DUF seul"
    o.append(trait("jalon", [jx, BAS, jx, BAS + 8], D.FAIBLE, 2))
    o.append(texte("jalon", (jx, BAS + 14), str(PREMIERS_DUF), "note",
                   D.FAIBLE, centre=True))
    o.append(texte("jalon", (jx, BAS + 80), jalon, "note", D.FAIBLE,
                   centre=True))
    large_j = mesure.mesure(jalon, fontes["note"])
    posees.append((2, jx - large_j / 2.0, jx + large_j / 2.0, jalon))

    #  Deux notes de la même ligne ne doivent pas se croiser.
    for i, (li, g0, d0, n0) in enumerate(posees):
        for lj, g1, d1, n1 in posees[i + 1:]:
            if li == lj and g0 < d1 and g1 < d0:
                raise SystemExit(
                    "« %s » et « %s » se chevauchent sur la ligne %d : "
                    "raccourcissez l'une ou descendez-la d'un cran"
                    % (n0, n1, li))

    o.append(trait("grille", [MARGE + 10, BAS, X1 + 30, BAS],
                   (170, 174, 186), 2))
    o.extend(barres)
    o.extend(valeurs)
    o.extend(annees)
    o.extend(notes)

    H = int(BAS + 118)
    o.insert(0, rect("fond", [0, 0, L, H], 0, D.PAPIER))
    return H, o


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
                           'stroke="%s" stroke-width="%g"/>'
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
                        "daz-decors-duf-seul")
    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5),
               ("indigo", INDIGO, 4.5), ("ambre", AMBRE, 4.5))

    H, ordres = composer()
    rendre_matriciel(H, ordres, base)
    couches, textes = rendre_svg(H, ordres, base)

    print("  %-34s %.0f Ko"
          % (os.path.basename(base + ".svg"),
             os.path.getsize(base + ".svg") / 1024.0))
    print("  %d x %d, %d calques, %d textes" % (L, H, couches, textes))
    print()
    print("  %d  %6s  aussi en OBJ" % (OBJ_2010["an"],
                                       pourcent(OBJ_2010["part"])))
    for d in DUF_SEUL:
        print("  %d  %6s  DUF seul%s"
              % (d["an"], pourcent(d["part"]),
                 "   (%d sur %d)" % d["compte"] if d["compte"] else ""))
    print()
    print("  seuil affirmé : jamais sous %s depuis %d"
          % (pourcent(SEUIL["part"]), SEUIL["depuis"]))
    print("  %d : premiers décors en DUF seul, sans chiffre publié"
          % PREMIERS_DUF)


if __name__ == "__main__":
    principal()
