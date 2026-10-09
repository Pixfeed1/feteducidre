"""
Jusqu'à quand chaque Windows reçoit encore des correctifs.

    python3 article-windows11/calendrier_maj.py

Produit `windows-calendrier-mises-a-jour.webp`, son PNG et le SVG.

----------------------------------------------------------------------------
LE REPÈRE DU JOUR COUPE CHAQUE BARRE EN DEUX
----------------------------------------------------------------------------
Une frise de Gantt ordinaire répond à « quand ça finit ». La question du
lecteur est autre : « combien il me reste ». Le trait du 9 octobre 2026
traverse donc toutes les barres, et chacune est pâle à gauche, pleine à
droite. Ce qui reste se lit sans compter.

La 24H2 y gagne tout son sens : sa part pleine fait quatre jours, soit
deux pixels. C'est exactement ce que la figure doit faire comprendre.

----------------------------------------------------------------------------
LES DÉBUTS NE SONT PAS TOUS SOURCÉS, LES FINS LE SONT
----------------------------------------------------------------------------
L'article date précisément trois fins : 13 octobre 2026, 12 octobre 2027,
et octobre 2028 pour la dernière. Il ne date qu'une sortie, celle de la
24H2, en octobre 2024.

Les deux autres débuts sont posés au 1er octobre de l'année que porte
leur nom : une version nommée 25H2 paraît par construction au second
semestre 2025. Ce n'est pas une estimation hasardeuse, c'est la
convention de nommage. Un contrôle vérifie néanmoins que chaque durée
reste proche des vingt-quatre mois annoncés par l'article.

L'étiquette de fin de la 26H2 dit « octobre 2028 » et non une date
précise, parce que la source n'en donne pas. La barre, elle, doit bien
s'arrêter quelque part : elle s'arrête au deuxième mardi, comme les
autres, et l'étiquette ne prétend pas le savoir.
"""

import os
from datetime import date

import charte as C
import dessin as D

L = 1600
MARGE = 56

INDIGO = C.VIOLET_TEXTE
INDIGO_PALE = (205, 192, 240)
AMBRE = (180, 83, 9)
AMBRE_PALE = (240, 212, 186)

#  Le jour que l'article prend pour repère.
REPERE = date(2026, 10, 9)

#  ---------------------------------------------------------------------------
#  LES QUATRE PÉRIODES
#
#  `fin_dite` est le libellé affiché : il porte la précision de la source,
#  qui n'est pas la même partout.
#  ---------------------------------------------------------------------------
PERIODES = (
    {"nom": "Windows 10", "detail": "sous ESU, inscription gratuite en France",
     "debut": date(2025, 10, 14), "fin": date(2027, 10, 12),
     "fin_dite": "12 octobre 2027", "teinte": AMBRE, "pale": AMBRE_PALE},

    {"nom": "Windows 11  24H2", "detail": "sortie en octobre 2024",
     "debut": date(2024, 10, 1), "fin": date(2026, 10, 13),
     "fin_dite": "13 octobre 2026", "teinte": INDIGO, "pale": INDIGO_PALE},

    {"nom": "Windows 11  25H2", "detail": "second semestre 2025",
     "debut": date(2025, 10, 1), "fin": date(2027, 10, 12),
     "fin_dite": "12 octobre 2027", "teinte": INDIGO, "pale": INDIGO_PALE},

    {"nom": "Windows 11  26H2", "detail": "second semestre 2026",
     "debut": date(2026, 10, 1), "fin": date(2028, 10, 12),
     "fin_dite": "octobre 2028", "teinte": INDIGO, "pale": INDIGO_PALE},
)

#  L'article annonce deux ans de suivi sur les éditions Famille et Pro.
DUREE_ANNONCEE = 24
TOLERANCE_MOIS = 1.5

POLICES = {
    "titre": (C.POLICE_G, 19, "bold"),
    "sous": (C.POLICE_R, 17, "normal"),
    "nom": (C.POLICE_G, 18, "bold"),
    "detail": (C.POLICE_R, 13, "normal"),
    "fin": (C.POLICE_G, 15, "bold"),
    "reste": (C.POLICE_R, 13, "normal"),
    "annee": (C.POLICE_G, 15, "bold"),
    "repere": (C.POLICE_G, 14, "bold"),
    "legende": (C.POLICE_R, 14, "normal"),
}
FAMILLE_SVG = "Liberation Sans, Arial, Helvetica, sans-serif"

TITRE = "CHAQUE VERSION DE WINDOWS 11 S’ARRÊTE AU BOUT DE DEUX ANS"
SOUS = ""        # rempli au dessin : il porte un nombre calculé

X_NOM = MARGE
X0, X1 = 376, 1420
Y_PREMIERE = 226
PAS = 84
HAUTEUR = 34

DEBUT_AXE = date(2024, 7, 1)
FIN_AXE = date(2029, 1, 1)


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


def mois_entre(a, b):
    return (b.year - a.year) * 12 + (b.month - a.month) + (b.day - a.day) / 30.44


def composer():
    mesure = D.Toile(L, 10)
    fontes = {k: mesure.police(f, t) for k, (f, t, _) in POLICES.items()}

    #  ------------------------------------------------------------------
    #  CONTRÔLES
    #  ------------------------------------------------------------------
    for p in PERIODES:
        if p["fin"] <= p["debut"]:
            raise SystemExit("%s finit avant de commencer" % p["nom"])
        if not DEBUT_AXE <= p["debut"] and p["fin"] <= FIN_AXE:
            raise SystemExit("%s sort de l'axe" % p["nom"])
        duree = mois_entre(p["debut"], p["fin"])
        if abs(duree - DUREE_ANNONCEE) > TOLERANCE_MOIS:
            raise SystemExit(
                "%s dure %.1f mois alors que l'article annonce deux ans de "
                "suivi" % (p["nom"], duree))
        p["reste"] = (p["fin"] - REPERE).days
        p["duree"] = duree

    if not DEBUT_AXE < REPERE < FIN_AXE:
        raise SystemExit("le repère tombe hors de l'axe")

    #  La version la plus proche de sa fin porte le propos de la figure.
    vivantes = [p for p in PERIODES if p["reste"] > 0]
    if not vivantes:
        raise SystemExit("plus aucune période n'est en cours au repère : la "
                         "figure n'a plus rien à montrer")
    urgente = min(vivantes, key=lambda p: p["reste"])

    etendue = (FIN_AXE - DEBUT_AXE).days

    def abscisse(j):
        return X0 + (j - DEBUT_AXE).days / float(etendue) * (X1 - X0)

    o = []
    o.append(texte("titre", (MARGE, 46), TITRE, "titre", D.ENCRE, 2.2))
    sous = ("au %d octobre 2026, la version %s est à %d jours de son dernier "
            "correctif" % (REPERE.day, urgente["nom"].split()[-1],
                           urgente["reste"]))
    if mesure.mesure(sous, fontes["sous"]) > L - 2 * MARGE:
        raise SystemExit("le sous-titre déborde")
    o.append(texte("titre", (MARGE, 74), sous, "sous", D.FAIBLE))

    x = MARGE
    for libelle, teinte_l in (("écoulé", INDIGO_PALE),
                              ("reste à courir", INDIGO)):
        o.append(rect("titre", [x, 118, x + 22, 132], 4, teinte_l))
        o.append(texte("titre", (x + 32, 116), libelle, "legende", D.GRIS))
        x += 32 + mesure.mesure(libelle, fontes["legende"]) + 40

    #  --------------------------------------------------------------  axe
    bas = Y_PREMIERE + (len(PERIODES) - 1) * PAS + HAUTEUR + 24
    axe, annees = [], []
    for an in range(DEBUT_AXE.year + 1, FIN_AXE.year + 1):
        gx = abscisse(date(an, 1, 1))
        axe.append(trait("axe", [gx, Y_PREMIERE - 28, gx, bas], D.FILET, 1))
        annees.append(texte("axe", (gx, bas + 10), str(an), "annee",
                            D.FAIBLE, centre=True))
    o.extend(axe)
    o.extend(annees)

    #  -----------------------------------------------------------  barres
    noms, barres, etiquettes = [], [], []
    for i, p in enumerate(PERIODES):
        y = Y_PREMIERE + i * PAS
        noms.append(texte("noms", (X_NOM, y + 2), D.typo(p["nom"]), "nom",
                          D.ENCRE))
        noms.append(texte("noms", (X_NOM, y + 25), D.typo(p["detail"]),
                          "detail", D.FAIBLE))

        xd, xf = abscisse(p["debut"]), abscisse(p["fin"])
        xr = min(max(abscisse(REPERE), xd), xf)

        #  La part écoulée, puis la part restante par-dessus. Deux
        #  rectangles et non un dégradé : on doit pouvoir mesurer.
        barres.append(rect("barres", [xd, y, xf, y + HAUTEUR], 6,
                           p["pale"]))
        if xf - xr >= 1:
            barres.append(rect("barres", [xr, y, xf, y + HAUTEUR], 6,
                               p["teinte"]))

        etiquettes.append(texte("étiquettes", (xf + 12, y + 8),
                                D.typo(p["fin_dite"]), "fin", p["teinte"]))
        reste = ("%d jours" % p["reste"] if p["reste"] < 100
                 else "%d mois" % round(mois_entre(REPERE, p["fin"])))
        etiquettes.append(texte("étiquettes", (xf + 12, y + 26),
                                "il reste " + reste, "reste", D.FAIBLE))

    o.extend(barres)
    o.extend(noms)
    o.extend(etiquettes)

    #  -------------------------------------------------------------  repère
    xr = abscisse(REPERE)
    o.append(trait("repère", [xr, Y_PREMIERE - 44, xr, bas], C.ALERTE, 2))
    lab = "9 octobre 2026"
    o.append(texte("repère", (xr, Y_PREMIERE - 68), lab, "repere",
                   C.ALERTE, centre=True))

    H = int(bas + 48)
    o.insert(0, rect("fond", [0, 0, L, H], 0, D.PAPIER))
    return H, o, urgente


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


def rendre_svg(H, ordres, base, sous):
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
           '  <desc>%s</desc>' % propre(sous)]

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
                        "windows-calendrier-mises-a-jour")
    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5),
               ("indigo", INDIGO, 4.5), ("ambre", AMBRE, 4.5),
               ("alerte", C.ALERTE, 4.5))

    H, ordres, urgente = composer()
    rendre_matriciel(H, ordres, base)
    sous = [a["c"] for a in ordres if a.get("p") == "sous"][0]
    couches, textes = rendre_svg(H, ordres, base, sous)

    print("  %-46s %.0f Ko"
          % (os.path.basename(base + ".svg"),
             os.path.getsize(base + ".svg") / 1024.0))
    print("  %d x %d, %d calques, %d textes" % (L, H, couches, textes))
    print()
    for p in PERIODES:
        print("  %-20s %s vers %s   %.1f mois   reste %4d jours"
              % (p["nom"], p["debut"], p["fin"], p["duree"], p["reste"]))
    print()
    print("  la plus pressée : %s, %d jours" % (urgente["nom"],
                                                urgente["reste"]))


if __name__ == "__main__":
    principal()
