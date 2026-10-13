"""
Trente-quatre ans de RPG Maker, et trois façons de scripter.

    python3 article-rpgmaker/frise_versions.py

Produit `rpg-maker-frise-versions.webp`, son PNG et le SVG éditable.

----------------------------------------------------------------------------
LES DATES SONT CELLES DU JAPON
----------------------------------------------------------------------------
La série sort d'abord au Japon, parfois des années avant l'Occident :
RPG Maker XP est de juillet 2004 à Tokyo et de septembre 2005 sur Steam.
Mélanger les deux calendriers décalerait la frise d'un an par endroits,
et ferait mentir la phrase de l'article, « RPG Maker XP, en 2004 au
Japon ». Toute la frise est donc en dates japonaises.

Quatre sorties ne sont connues ici qu'à l'année : Dante 98 II, RPG Maker
2000, MV et With. Elles sont posées au milieu de leur année, et leur
étiquette ne porte que l'année. Un décalage de six mois fait vingt
pixels sur trente-quatre ans : il ne change rien à ce que la figure dit.

----------------------------------------------------------------------------
TROIS ÈRES DE ONZE ANS, ET C'EST LA FIGURE QUI LE DÉCOUVRE
----------------------------------------------------------------------------
L'article parle d'un « glissement discret » du tout-événement au Ruby
puis au JavaScript. Posé sur un axe proportionnel, ce glissement se
révèle régulier : onze à douze ans par ère, trois fois de suite. Les
durées sont recalculées à chaque dessin, et le dessin s'arrête si les
mots ne collent plus aux années.

----------------------------------------------------------------------------
LE NOM NE DIT PAS L'ANNÉE
----------------------------------------------------------------------------
RPG Maker 2003 est sorti en décembre 2002. L'étiquette porte les deux,
et le repère tombe à gauche de la graduation 2003 : la figure montre le
décalage au lieu de l'expliquer. Un contrôle vérifie qu'il est toujours
là, sans quoi l'étiquette « 2003 / 2002 » n'aurait plus de sens.

----------------------------------------------------------------------------
TROIS TITRES QUI NE SONT PAS DE LA SÉRIE PRINCIPALE
----------------------------------------------------------------------------
Unite, With et U2U ne tiennent pas dans les trois ères : l'un vise les
consoles, les deux autres tournent sous Unity, en C#. Ils portent donc
un repère creux et une étiquette grise, et se tiennent un cran en
retrait. U2U n'a pas de date de sortie, seulement une annonce de mai
2026 : son étiquette le dit.
"""

import os

import charte as C
import dessin as D

L = 1600
MARGE = 56

INDIGO = C.VIOLET_TEXTE

#  Les trois ères, de la plus claire à la plus dense. Le blanc doit tenir
#  sur chacune : c'est vérifié avant le premier trait.
ERE_CLAIRE = (124, 96, 208)
ERE_MOYENNE = (104, 56, 202)
ERE_DENSE = (74, 28, 160)

DEBUT, FIN = 1992.4, 2027.0
AUJOURD_HUI = 2026.78          # octobre 2026, la fin du segment JavaScript

#  ---------------------------------------------------------------------------
#  LES TREIZE VERSIONS
#
#  `an` est la date japonaise en années décimales. `annee` est ce que
#  l'étiquette affiche, et vaut l'année seule quand le mois n'est pas
#  établi. `cote` vaut 1 au-dessus de la bande, -1 au-dessous.
#  `principale` distingue la série principale des trois titres à côté.
#  ---------------------------------------------------------------------------
VERSIONS = (
    {"an": 1992.96, "nom": "Dante 98",    "annee": "1992",
     "cote": 1,  "prof": 0, "principale": True},
    {"an": 1996.50, "nom": "Dante 98 II", "annee": "1996",
     "cote": -1, "prof": 0, "principale": True},
    {"an": 1997.24, "nom": "95",          "annee": "1997",
     "cote": 1,  "prof": 0, "principale": True},
    {"an": 2000.50, "nom": "2000",        "annee": "2000",
     "cote": -1, "prof": 0, "principale": True},
    {"an": 2002.96, "nom": "2003",        "annee": "2002",
     "cote": 1,  "prof": 0, "principale": True},
    {"an": 2004.56, "nom": "XP",          "annee": "juillet 2004",
     "cote": -1, "prof": 0, "principale": True},
    {"an": 2007.99, "nom": "VX",          "annee": "2007",
     "cote": 1,  "prof": 0, "principale": True},
    {"an": 2011.96, "nom": "VX Ace",      "annee": "2011",
     "cote": -1, "prof": 0, "principale": True},
    {"an": 2015.90, "nom": "MV",          "annee": "2015",
     "cote": 1,  "prof": 0, "principale": True},
    {"an": 2020.64, "nom": "MZ",          "annee": "août 2020",
     "cote": -1, "prof": 0, "principale": True},

    {"an": 2023.26, "nom": "Unite",       "annee": "2023",
     "cote": 1,  "prof": 1, "principale": False},
    {"an": 2024.80, "nom": "With",        "annee": "2024",
     "cote": -1, "prof": 1, "principale": False},
    {"an": 2026.38, "nom": "U2U",         "annee": "annoncé 2026",
     "cote": 1,  "prof": 1, "principale": False},
)

#  Les trois ères. Chacune commence à la version qui l'ouvre, et son
#  libellé annonce une durée que le dessin recalcule.
ERES = (
    {"depuis": "Dante 98", "mot": "douze ans sans écrire une ligne",
     "ans": 12, "teinte": ERE_CLAIRE},
    {"depuis": "XP", "mot": "onze ans de Ruby", "ans": 11,
     "teinte": ERE_MOYENNE},
    {"depuis": "MV", "mot": "onze ans de JavaScript", "ans": 11,
     "teinte": ERE_DENSE},
)

#  Ce que l'article affirme et que la figure ne doit pas démentir.
ANNONCES = {"XP": 2004, "MV": 2015, "Dante 98": 1992}

POLICES = {
    "titre": (C.POLICE_G, 19, "bold"),
    "sous": (C.POLICE_R, 17, "normal"),
    "ere": (C.POLICE_G, 15, "bold"),
    "nom": (C.POLICE_G, 18, "bold"),
    "annee": (C.POLICE_R, 15, "normal"),
    "note": (C.POLICE_R, 14, "normal"),
}
FAMILLE_SVG = "Liberation Sans, Arial, Helvetica, sans-serif"

TITRE = "TREIZE TITRES, TRENTE-QUATRE ANS, TROIS FAÇONS DE SCRIPTER"
COMPTES = {"titres": 13, "serie principale": 10}
SOUS = ("de RPG Tsukūru Dante 98 en 1992 à RPG Maker U2U, annoncé en 2026 ; "
        "dates japonaises")
NOTE = ("Repère creux : les titres qui avancent à côté de la série "
        "principale, sur consoles ou sous Unity.")

#  ---------------------------------------------------------------------------
#  LE RUBAN A TROIS LIGNES, ET AUCUNE NE SE MARCHE DESSUS
#
#  Premier jet : les repères au centre du ruban, le nom de l'ère au centre
#  aussi. Les repères de Dante 98 II et de 95 traversaient « douze ans sans
#  écrire une ligne », et celui de VX coupait « onze ans de Ruby » en deux.
#
#  Le ruban se divise donc en trois lignes. Les repères des versions
#  étiquetées au-dessus occupent la lèvre haute, ceux des versions
#  étiquetées au-dessous la lèvre basse, et le nom de l'ère court entre
#  les deux. Chaque tige s'arrête à son repère, sans jamais couper le nom.
#  ---------------------------------------------------------------------------
AXE_Y = 310
AXE_X0, AXE_X1 = 112, L - 112
BANDE = 52                # hauteur du ruban des ères
LEVRE = 19                # du centre du ruban à la ligne des repères
R_REPERE = 6              # rayon des repères de version
ECART = 30                # du ruban au premier bloc
PAS_PROFONDEUR = 64
H_BLOC = 46               # nom puis année


def rect(couche, b, r, teinte):
    return {"quoi": "rect", "couche": couche, "b": b, "r": r, "t": teinte}


def trait(couche, b, teinte, epaisseur):
    return {"quoi": "trait", "couche": couche, "b": b, "t": teinte,
            "e": epaisseur}


def disque(couche, cx, cy, r, teinte=None, contour=None, epaisseur=2):
    return {"quoi": "disque", "couche": couche, "cx": cx, "cy": cy, "r": r,
            "t": teinte, "contour": contour, "e": epaisseur}


def texte(couche, xy, contenu, police, teinte, tracking=0.0, centre=False):
    for c, nom in (("—", "cadratin"), ("–", "demi-cadratin")):
        if c in contenu:
            raise SystemExit("%s dans « %s »" % (nom, contenu[:60]))
    return {"quoi": "texte", "couche": couche, "xy": xy, "c": contenu,
            "p": police, "t": teinte, "tr": tracking, "centre": centre}


def composer():
    mesure = D.Toile(L, 10)
    fontes = {k: mesure.police(f, t) for k, (f, t, _) in POLICES.items()}
    par_nom = {v["nom"]: v for v in VERSIONS}

    #  ------------------------------------------------------------------
    #  CONTRÔLES SUR LES DONNÉES
    #  ------------------------------------------------------------------
    for a, b in zip(VERSIONS, VERSIONS[1:]):
        if b["an"] <= a["an"]:
            raise SystemExit("« %s » et « %s » ne sont pas dans l'ordre"
                             % (a["nom"], b["nom"]))
    for v in VERSIONS:
        if not DEBUT <= v["an"] <= FIN:
            raise SystemExit("« %s » sort de l'axe" % v["nom"])

    #  Le titre compte les titres, et la note en distingue trois : les deux
    #  chiffres se recalculent plutôt que de se recopier à la main.
    trouve = {"titres": len(VERSIONS),
              "serie principale": sum(1 for v in VERSIONS if v["principale"])}
    for quoi, attendu in COMPTES.items():
        if trouve[quoi] != attendu:
            raise SystemExit("la figure annonce %d %s et en dessine %d"
                             % (attendu, quoi, trouve[quoi]))

    for nom, annee in ANNONCES.items():
        if int(par_nom[nom]["an"]) != annee:
            raise SystemExit("l'article date « %s » de %d, la frise la pose "
                             "en %d" % (nom, annee, int(par_nom[nom]["an"])))

    #  Le nom ne dit pas l'année : RPG Maker 2003 est sorti en 2002.
    if par_nom["2003"]["an"] >= 2003.0:
        raise SystemExit("« 2003 » ne tombe plus avant la graduation 2003 : "
                         "l'étiquette « 2003 / 2002 » perd son sens")

    bornes = [par_nom[e["depuis"]]["an"] for e in ERES] + [AUJOURD_HUI]
    for i, e in enumerate(ERES):
        duree = bornes[i + 1] - bornes[i]
        if int(round(duree)) != e["ans"]:
            raise SystemExit("« %s » annonce %d ans, l'axe en donne %.1f"
                             % (e["mot"], e["ans"], duree))

    #  Les trois lignes du ruban ne doivent pas se recouvrir : c'est le
    #  défaut du premier jet, et il ne se voit qu'une fois l'image tirée.
    #  Le nom de l'ère est posé par son coin haut gauche, pas par sa ligne
    #  de base : sa hauteur vient donc des métriques de la police.
    h_ere = sum(C.police(*POLICES["ere"][:2]).getmetrics())
    y_ere = AXE_Y - h_ere / 2.0
    if LEVRE - R_REPERE <= h_ere / 2.0:
        raise SystemExit("le nom de l'ère fait %d px de haut et les repères "
                         "sont à %d du centre : ils se croisent"
                         % (h_ere, LEVRE - R_REPERE))
    if LEVRE + R_REPERE > BANDE / 2.0:
        raise SystemExit("les repères débordent du ruban")

    etendue = FIN - DEBUT

    def abscisse(an):
        return AXE_X0 + (an - DEBUT) / etendue * (AXE_X1 - AXE_X0)

    o = []
    o.append(texte("titre", (MARGE, 46), TITRE, "titre", D.ENCRE, 2.2))
    sous = D.typo(SOUS)
    if mesure.mesure(sous, fontes["sous"]) > L - 2 * MARGE:
        raise SystemExit("le sous-titre déborde")
    o.append(texte("titre", (MARGE, 74), sous, "sous", D.FAIBLE))

    #  ------------------------------------------------------  le ruban des ères
    #  Pas de graduation décennale : les treize étiquettes portent déjà
    #  leur année, et les trois segments sont proportionnels. Une grille
    #  en plus ne faisait que barrer « 2000 » et « août 2020 ».
    haut_b, bas_b = AXE_Y - BANDE / 2.0, AXE_Y + BANDE / 2.0
    bande = []
    for i, e in enumerate(ERES):
        x0 = abscisse(bornes[i]) if i else AXE_X0
        x1 = abscisse(bornes[i + 1]) if i + 1 < len(ERES) else AXE_X1
        #  Les segments se touchent, sans filet de papier entre eux : les
        #  repères de XP et de MV tombent pile sur une frontière, et un
        #  disque blanc posé sur une fente de papier disparaissait. La
        #  marche de teinte suffit à montrer le passage d'une ère à l'autre.
        bande.append(rect("eres", [x0, haut_b, x1, bas_b], 0, e["teinte"]))
        large = mesure.mesure(e["mot"], fontes["ere"])
        if large > (x1 - x0) - 28:
            raise SystemExit("« %s » fait %d px pour un segment de %d px"
                             % (e["mot"], large, x1 - x0))
        bande.append(texte("eres", ((x0 + x1) / 2.0, y_ere), e["mot"],
                           "ere", D.BLANC, centre=True))
    o.extend(bande)

    #  ------------------------------------------------------  les versions
    tiges, reperes, blocs, boites = [], [], [], []

    for v in VERSIONS:
        x = abscisse(v["an"])
        depart = BANDE / 2.0 + ECART + v["prof"] * PAS_PROFONDEUR

        #  Le repère se pose sur la lèvre du ruban qui regarde l'étiquette,
        #  et la tige va jusqu'à lui : elle ne traverse donc jamais la
        #  ligne du milieu, où court le nom de l'ère.
        y_repere = AXE_Y - v["cote"] * LEVRE
        if v["cote"] > 0:
            bas = AXE_Y - depart
            haut = bas - H_BLOC
            tiges.append(trait("tiges", [x, y_repere, x, bas], INDIGO, 2))
        else:
            haut = AXE_Y + depart
            tiges.append(trait("tiges", [x, y_repere, x, haut], INDIGO, 2))

        if v["principale"]:
            reperes.append(disque("tiges", x, y_repere, R_REPERE, teinte=D.BLANC))
        else:
            reperes.append(disque("tiges", x, y_repere, R_REPERE, contour=D.BLANC,
                                  epaisseur=3))

        nom = D.typo(v["nom"])
        annee = D.typo(v["annee"])
        ln = mesure.mesure(nom, fontes["nom"])
        la = mesure.mesure(annee, fontes["annee"])
        demi = max(ln, la) / 2.0

        teinte_nom = D.ENCRE if v["principale"] else D.GRIS
        blocs.append(texte("versions", (x - ln / 2.0, haut), nom, "nom",
                           teinte_nom))
        blocs.append(texte("versions", (x - la / 2.0, haut + 24), annee,
                           "annee", INDIGO))

        if x - demi < MARGE or x + demi > L - MARGE:
            raise SystemExit("l'étiquette de « %s » sort du cadre" % v["nom"])
        boites.append((v["cote"], v["prof"], x - demi, x + demi, v["nom"]))

    #  Deux étiquettes du même côté ET de la même profondeur ne doivent
    #  pas se croiser : c'est tout l'intérêt des deux champs.
    for i, (c0, p0, g0, d0, n0) in enumerate(boites):
        for c1, p1, g1, d1, n1 in boites[i + 1:]:
            if c0 == c1 and p0 == p1 and g0 < d1 + 14 and g1 < d0 + 14:
                raise SystemExit(
                    "« %s » et « %s » se chevauchent : changez le côté ou la "
                    "profondeur de l'un des deux" % (n0, n1))

    o.extend(tiges)
    o.extend(reperes)
    o.extend(blocs)

    bas_figure = AXE_Y + BANDE / 2.0 + ECART + PAS_PROFONDEUR + H_BLOC
    note = D.typo(NOTE)
    if mesure.mesure(note, fontes["note"]) > L - 2 * MARGE:
        raise SystemExit("la note déborde")
    o.append(texte("note", (MARGE, bas_figure + 30), note, "note", D.FAIBLE))

    H = int(bas_figure + 76)
    o.insert(0, rect("fond", [0, 0, L, H], 0, D.PAPIER))
    return H, o, [bornes[i + 1] - bornes[i] for i in range(len(ERES))]


def rendre_matriciel(H, ordres, base):
    t = D.Toile(L, H)
    fontes = {k: t.police(f, taille) for k, (f, taille, _) in POLICES.items()}
    for a in ordres:
        if a["quoi"] == "rect":
            t.rrect(a["b"], a["r"], teinte=a["t"])
        elif a["quoi"] == "trait":
            t.ligne(a["b"], a["t"], a["e"])
        elif a["quoi"] == "disque":
            t.disque(a["cx"], a["cy"], a["r"], teinte=a["t"],
                     contour=a["contour"], epaisseur=a["e"])
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
                remplissage = teinte(a["t"]) if a["t"] else "none"
                bord = ('" stroke="%s" stroke-width="%g'
                        % (teinte(a["contour"]), a["e"])) if a["contour"] \
                    else ""
                out.append('    <circle cx="%g" cy="%g" r="%g" fill="%s%s"/>'
                           % (a["cx"], a["cy"], a["r"], remplissage, bord))
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
                        "rpg-maker-frise-versions")
    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5),
               ("indigo", INDIGO, 4.5))
    #  Le blanc des libellés d'ère tient sur les trois fonds qu'il occupe.
    for nom, fond in (("ère 1", ERE_CLAIRE), ("ère 2", ERE_MOYENNE),
                      ("ère 3", ERE_DENSE)):
        r = C.contraste(D.BLANC, fond)
        print("  blanc sur %-5s %-16s %.2f:1  %s"
              % (nom, str(fond), r, "ok" if r >= 4.5 else "INSUFFISANT"))
        if r < 4.5:
            raise SystemExit("%s : %.2f:1, sous le seuil" % (nom, r))

    H, ordres, durees = composer()
    rendre_matriciel(H, ordres, base)
    couches, textes = rendre_svg(H, ordres, base)

    print()
    print("  %-38s %.0f Ko"
          % (os.path.basename(base + ".svg"),
             os.path.getsize(base + ".svg") / 1024.0))
    print("  %d x %d, %d calques, %d textes" % (L, H, couches, textes))
    print()
    for v in VERSIONS:
        print("  %-12s %-14s %s%s"
              % (v["nom"], v["annee"],
                 "au-dessus" if v["cote"] > 0 else "au-dessous",
                 "" if v["principale"] else "   (hors série principale)"))
    print()
    for e, d in zip(ERES, durees):
        print("  %-34s %.1f ans" % (e["mot"], d))


if __name__ == "__main__":
    principal()
