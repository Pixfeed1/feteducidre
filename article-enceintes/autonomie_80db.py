"""
Autonomie annoncée contre autonomie mesurée à 80 dB.

    python3 article-enceintes/autonomie_80db.py

Produit `enceinte-bluetooth-autonomie-80db.webp`, son PNG et le SVG.

----------------------------------------------------------------------------
UNE BARRE DANS L'AUTRE, PARCE QUE LE SUJET EST UN ÉCART
----------------------------------------------------------------------------
Deux barres côte à côte obligent l'oeil à comparer deux longueurs
voisines, puis à faire la soustraction lui-même. On pose donc la mesure
DANS la promesse : le gris est ce qui était annoncé, l'indigo ce qui a été
tenu. Du gris qui dépasse, c'est une promesse non tenue ; de l'indigo qui
sort du gris, c'est une promesse battue. Il n'y a rien à calculer, et les
deux familles de l'article se séparent d'elles-mêmes à la quatrième ligne.

----------------------------------------------------------------------------
LES DURÉES SONT SAISIES EN HEURES ET MINUTES, PAS EN DÉCIMAL
----------------------------------------------------------------------------
SoundGuys publie des 4 h 33 et des 30 h 06. Les convertir à la main en
4,55 et 30,1 pour les retaper ensuite est le meilleur moyen d'écrire 4,33
un jour de fatigue. La table garde donc la forme publiée, et la conversion
comme les pourcentages sont calculés.

----------------------------------------------------------------------------
DEUX POIDS MANQUENT, ET ON NE LES INVENTE PAS
----------------------------------------------------------------------------
Le classement demandé va de la plus légère à la plus lourde. L'article
donne le poids de cinq enceintes sur sept : la SoundLink Micro et la
SoundLink Flex n'en ont pas. Leur rang ne vient donc pas d'un chiffre que
j'aurais trouvé ailleurs, mais de l'article lui-même, qui les range parmi
« les petites » et dont la légende parle des « quatre plus petites ». La
colonne de poids reste vide pour ces deux-là plutôt que de porter une
valeur dont la figure ne pourrait pas répondre.
"""

import os

import charte as C
import dessin as D

L = 1600
MARGE = 56

INDIGO = C.VIOLET_TEXTE
GRIS_BARRE = (219, 219, 228)

#  ---------------------------------------------------------------------------
#  LES SEPT ENCEINTES, DANS L'ORDRE DE L'ARTICLE
#
#  `mesure` est le relevé SoundGuys à 80 dB à un mètre, tel qu'il est publié.
#  `annonce` est la durée du fabricant, en heures. `poids` vaut None quand
#  l'article ne le donne pas.
#  ---------------------------------------------------------------------------
ENCEINTES = (
    {"nom": "Bose SoundLink Micro 2", "poids": None,
     "mesure": (4, 33), "annonce": 12},
    {"nom": "Bose SoundLink Flex 2", "poids": None,
     "mesure": (7, 3), "annonce": 12},
    {"nom": "JBL Flip 7", "poids": 826,
     "mesure": (6, 16), "annonce": 14},
    {"nom": "JBL Charge 6", "poids": 1370,
     "mesure": (13, 15), "annonce": 24},
    {"nom": "Bose SoundLink Plus", "poids": 1530,
     "mesure": (20, 55), "annonce": 20},
    {"nom": "JBL Xtreme 5", "poids": 2900,
     "mesure": (30, 6), "annonce": 24},
    {"nom": "JBL Boombox 4", "poids": 5890,
     "mesure": (34, 56), "annonce": 28},
)

#  Ce que la légende de l'article affirme, et que les contrôles vérifient.
PERTE_MIN, PERTE_MAX = 41, 62
PETITES = 4

POLICES = {
    "titre": (C.POLICE_G, 19, "bold"),
    "sous": (C.POLICE_R, 17, "normal"),
    "nom": (C.POLICE_G, 17, "bold"),
    "poids": (C.POLICE_R, 14, "normal"),
    "valeur": (C.POLICE_G, 17, "bold"),
    "part": (C.POLICE_R, 15, "normal"),
    "grad": (C.POLICE_R, 13, "normal"),
    "legende": (C.POLICE_R, 15, "normal"),
}
FAMILLE_SVG = "Liberation Sans, Arial, Helvetica, sans-serif"

TITRE = "LES PETITES PERDENT LA MOITIÉ, LES GROSSES DÉPASSENT"
SOUS = ("autonomie annoncée et autonomie mesurée à 80 dB à un mètre par "
        "SoundGuys, de la plus légère à la plus lourde")

X_NOM = MARGE
X_BARRE = 420
X_FIN = 1270
Y_PREMIERE = 252
PAS = 72
HAUTEUR_GRIS = 26
HAUTEUR_INDIGO = 13


def duree(hm):
    h, m = hm
    return "%d h %02d" % (h, m)


def rect(couche, b, r, teinte):
    return {"quoi": "rect", "couche": couche, "b": b, "r": r, "t": teinte}


def trait(couche, b, teinte, epaisseur):
    return {"quoi": "trait", "couche": couche, "b": b, "t": teinte,
            "e": epaisseur}


def texte(couche, xy, contenu, police, teinte, tracking=0.0, centre=False):
    for c, nom in (("—", "cadratin"), ("–", "demi-cadratin")):
        if c in contenu:
            raise SystemExit("%s dans « %s »" % (nom, contenu[:60]))
    return {"quoi": "texte", "couche": couche, "xy": xy, "c": contenu,
            "p": police, "t": teinte, "tr": tracking, "centre": centre}


def composer():
    mesure = D.Toile(L, 10)
    fontes = {k: mesure.police(f, t) for k, (f, t, _) in POLICES.items()}

    for e in ENCEINTES:
        h, m = e["mesure"]
        e["heures"] = h + m / 60.0
        e["part"] = 100.0 * e["heures"] / e["annonce"]

    #  ------------------------------------------------------------------
    #  CONTRÔLES, SUR CE QUE LA LÉGENDE DE L'ARTICLE AFFIRME
    #  ------------------------------------------------------------------
    pertes = [100 - e["part"] for e in ENCEINTES[:PETITES]]
    if min(pertes) < PERTE_MIN - 1 or max(pertes) > PERTE_MAX + 1:
        raise SystemExit(
            "la légende annonce une perte de %d à %d %% ; les quatre "
            "premières perdent de %.0f à %.0f %%"
            % (PERTE_MIN, PERTE_MAX, min(pertes), max(pertes)))
    for e in ENCEINTES[PETITES:]:
        if e["part"] <= 100:
            raise SystemExit(
                "%s est rangée parmi celles qui dépassent leur promesse et "
                "n'en tient que %.0f %%" % (e["nom"], e["part"]))
    #  Le classement par poids, là où l'article le donne.
    connus = [e["poids"] for e in ENCEINTES if e["poids"] is not None]
    if connus != sorted(connus):
        raise SystemExit("les poids connus ne sont pas croissants : %s"
                         % connus)
    if any(e["poids"] is not None for e in ENCEINTES[:2]):
        raise SystemExit(
            "les deux premières portent un poids que l'article ne donne pas")

    maximum = max(max(e["heures"], e["annonce"]) for e in ENCEINTES)
    plafond = 36.0 if maximum <= 36 else maximum * 1.05
    echelle = (X_FIN - X_BARRE) / plafond

    o = []
    o.append(texte("titre", (MARGE, 46), TITRE, "titre", D.ENCRE, 2.2))
    sous = D.typo(SOUS)
    if mesure.mesure(sous, fontes["sous"]) > L - 2 * MARGE:
        raise SystemExit("le sous-titre déborde")
    o.append(texte("titre", (MARGE, 74), sous, "sous", D.FAIBLE))

    #  --------------------------------------------------------  légende
    x = X_BARRE
    for teinte, hauteur, libelle in ((GRIS_BARRE, HAUTEUR_GRIS, "annoncée"),
                                     (INDIGO, HAUTEUR_INDIGO,
                                      "mesurée à 80 dB")):
        o.append(rect("légende", [x, 136 - hauteur / 2.0, x + 26,
                                  136 + hauteur / 2.0], 4, teinte))
        o.append(texte("légende", (x + 36, 127), libelle, "legende", D.GRIS))
        x += 36 + mesure.mesure(libelle, fontes["legende"]) + 40

    #  ---------------------------------------------------------  grille
    bas = Y_PREMIERE + (len(ENCEINTES) - 1) * PAS + HAUTEUR_GRIS
    for heures in range(0, int(plafond) + 1, 12):
        gx = X_BARRE + heures * echelle
        o.append(trait("grille", [gx, Y_PREMIERE - 26, gx, bas + 10],
                       D.FILET, 1))
        o.append(texte("grille", (gx, Y_PREMIERE - 48), "%d h" % heures,
                       "grad", D.FAIBLE, centre=True))

    #  ---------------------------------------------------------  barres
    barres, textes_ = [], []
    for i, e in enumerate(ENCEINTES):
        y = Y_PREMIERE + i * PAS
        cy = y + HAUTEUR_GRIS / 2.0

        #  LA MESURE EST POSÉE DANS LA PROMESSE.
        #
        #  Le gris va jusqu'à l'annonce, l'indigo jusqu'au relevé. Du gris
        #  qui dépasse se lit comme un manque, de l'indigo qui sort se lit
        #  comme un dépassement, sans qu'on ait à comparer deux longueurs.
        fin_gris = X_BARRE + e["annonce"] * echelle
        fin_indigo = X_BARRE + e["heures"] * echelle
        barres.append(rect("barres", [X_BARRE, y, fin_gris,
                                      y + HAUTEUR_GRIS], 4, GRIS_BARRE))
        #  Une seule teinte pour la mesure, qu'elle tienne ou non sa
        #  promesse : c'est la LONGUEUR qui dit laquelle des deux gagne, et
        #  recolorer les dépassements ferait dire deux fois la même chose.
        barres.append(rect("barres",
                           [X_BARRE, cy - HAUTEUR_INDIGO / 2.0, fin_indigo,
                            cy + HAUTEUR_INDIGO / 2.0], 3, INDIGO))

        textes_.append(texte("textes", (X_NOM, y - 1), e["nom"], "nom",
                             D.ENCRE))
        if e["poids"] is not None:
            poids = ("%d g" % e["poids"] if e["poids"] < 1000
                     else ("%.2f kg" % (e["poids"] / 1000.0)).replace(".", ","))
            textes_.append(texte("textes", (X_NOM, y + 21), poids, "poids",
                                 D.FAIBLE))

        bout = max(fin_gris, fin_indigo) + 18
        textes_.append(texte("textes", (bout, y - 1), duree(e["mesure"]),
                             "valeur", INDIGO))
        textes_.append(texte("textes", (bout, y + 21),
                             "%d %% de la promesse" % round(e["part"]),
                             "part", D.GRIS))

    o.extend(barres)
    o.extend(textes_)

    H = int(bas + 56)
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
                        "enceinte-bluetooth-autonomie-80db")
    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5),
               ("indigo", INDIGO, 4.5))

    H, ordres = composer()
    rendre_matriciel(H, ordres, base)
    couches, textes = rendre_svg(H, ordres, base)

    print("  %-46s %.0f Ko"
          % (os.path.basename(base + ".svg"),
             os.path.getsize(base + ".svg") / 1024.0))
    print("  %d calques, %d textes" % (couches, textes))
    print()
    for e in ENCEINTES:
        print("  %-26s %-9s %7s sur %2d h   %3d %%"
              % (e["nom"],
                 "" if e["poids"] is None else "%d g" % e["poids"],
                 duree(e["mesure"]), e["annonce"], round(e["part"])))


if __name__ == "__main__":
    principal()
