"""
Ce que la résolution d'une HDRI change, et ce qu'elle ne change pas.

    python3 article-hdri/resolution.py

Produit `hdri-blender-resolution.webp`, son PNG et le SVG éditable.

----------------------------------------------------------------------------
CE QUE CETTE FIGURE REMPLACE
----------------------------------------------------------------------------
Une première version circulait hors charte : fond crème, titres bleu
marine, panneaux encadrés, barres bleues et barre 8K orange. Les données
sont les mêmes, à la virgule près. Seuls le dessin et les teintes
changent.

----------------------------------------------------------------------------
POURQUOI LA 8K N'EST PLUS EN ALERTE
----------------------------------------------------------------------------
La version d'origine peignait la 8K en orange dans les quatre panneaux,
y compris celui de la lumière, où elle vaut exactement comme les trois
autres. Signaler un danger là où rien ne se passe, c'est user le signal
pour rien, et la charte réserve l'alerte aux figures qui opposent un
état sain à un état dégradé.

Toutes les barres sont donc de la même teinte. Le message n'y perd
rien : le premier panneau est plat, les trois autres se cabrent. C'est
la hauteur qui parle, et l'oeil compare des formes au lieu de trier des
couleurs.

----------------------------------------------------------------------------
CHAQUE PANNEAU A SON ÉCHELLE, ET LE RAPPORT EST ÉCRIT
----------------------------------------------------------------------------
Des watts, des mégaoctets, des gigaoctets et des secondes ne partagent
pas d'axe. Chaque panneau est donc à son échelle, et porte en clair son
rapport de la 1K à la 8K : sans lui, on comparerait des hauteurs qui ne
veulent pas dire la même chose. Les quatre rapports sont recalculés à
chaque dessin et comparés à ce que l'article affirme.

Le plafond de chaque panneau vaut 1,15 fois son maximum. Sans cette
marge, les quatre barres de la lumière viendraient buter contre le haut
du cadre et se liraient comme une jauge pleine, pas comme une horizontale.
"""

import os

import charte as C
import dessin as D

L = 1600
MARGE = 56

INDIGO = C.VIOLET_TEXTE
BARRE = (124, 96, 208)        # l'aplat des barres, blanc dessus non utilisé

RESOLUTIONS = ("1K", "2K", "4K", "8K")

#  ---------------------------------------------------------------------------
#  LES QUATRE MESURES
#
#  Relevés du 22 octobre 2026, Blender 5.2.3 LTS, Cycles sur processeur,
#  médiane de trois rendus. `dec` est le nombre de décimales affichées.
#  ---------------------------------------------------------------------------
PANNEAUX = (
    {"titre": "Lumière du soleil", "unite": "éclairement à Strength 1, W/m²",
     "val": (8.36, 8.36, 8.36, 8.36), "dec": 2},
    {"titre": "Poids du fichier", "unite": ".hdr téléchargé, Mo",
     "val": (1.0, 4.0, 16.8, 67.5), "dec": 1},
    {"titre": "Mémoire de Blender", "unite": "RAM au pic du rendu, Go",
     "val": (0.66, 0.69, 0.78, 2.22), "dec": 2},
    {"titre": "Temps de rendu", "unite": "960 × 540 px, 64 échantillons, s",
     "val": (50.5, 50.0, 50.5, 56.0), "dec": 1},
)

#  Ce que l'article affirme, et que le dessin doit retrouver seul.
#  Chaque entrée est (rapport attendu de la 1K à la 8K, tolérance).
ANNONCES = {"Lumière du soleil": (1.0, 0.001),
            "Poids du fichier": (67.0, 1.0),
            "Mémoire de Blender": (3.36, 0.05),
            "Temps de rendu": (1.11, 0.01)}
SURCOUT_8K = 5.5          # secondes de plus que la 4K, dit l'article

POLICES = {
    "titre": (C.POLICE_G, 19, "bold"),
    "sous": (C.POLICE_R, 17, "normal"),
    "panneau": (C.POLICE_G, 18, "bold"),
    "unite": (C.POLICE_R, 13, "normal"),
    "rapport": (C.POLICE_G, 13, "bold"),
    "valeur": (C.POLICE_G, 15, "bold"),
    "res": (C.POLICE_R, 14, "normal"),
    "note": (C.POLICE_R, 14, "normal"),
}
FAMILLE_SVG = "Liberation Sans, Arial, Helvetica, sans-serif"

TITRE = "LA 8K ÉCLAIRE PAREIL, ET TRIPLE LA MÉMOIRE"
SOUS = ("même scène et même HDRI en quatre résolutions, de la 1K à la 8K ; "
        "chaque panneau a son échelle")
NOTE = ("HDRI qwantani_afternoon_puresky (Poly Haven, CC0), Blender 5.2.3 "
        "LTS, Cycles sur processeur, médiane de trois rendus.")

Y_PANNEAU = 150           # titre du panneau
Y_BASE = 540              # ligne de sol des barres
H_UTILE = 268             # hauteur disponible au-dessus du sol
ECART_PANNEAU = 30
LARGEUR_BARRE = 46
ECART_BARRE = 26
MARGE_PLAFOND = 1.15      # air au-dessus de la plus haute barre


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


def nombre(v, dec):
    """8.36 donne « 8,36 », et 67.5 donne « 67,5 »."""
    return ("%.*f" % (dec, v)).replace(".", ",")


def rapport(v):
    """1.0 donne « identique », 67.0 donne « x 67 », 3.36 donne « x 3,4 ».

    Le rapport affiché est celui de l'article, pas celui que donnerait la
    division des valeurs arrondies du dessin : 67,5 / 1,0 ferait « x 68 »,
    alors que les poids réels, non arrondis, donnent 67. Le contrôle plus
    haut vérifie que les deux restent compatibles ; c'est lui qui attrape
    une vraie divergence, pas l'arrondi de l'affichage.
    """
    if abs(v - 1.0) < 0.005:
        return "identique d’un bout à l’autre"
    if v >= 10:
        return "x %d de la 1K à la 8K" % round(v)
    return "x %s de la 1K à la 8K" % nombre(v, 1)


def composer():
    mesure = D.Toile(L, 10)
    fontes = {k: mesure.police(f, t) for k, (f, t, _) in POLICES.items()}

    #  ------------------------------------------------------------------
    #  CONTRÔLES
    #  ------------------------------------------------------------------
    for p in PANNEAUX:
        if len(p["val"]) != len(RESOLUTIONS):
            raise SystemExit("« %s » donne %d valeurs pour %d résolutions"
                             % (p["titre"], len(p["val"]), len(RESOLUTIONS)))
        if min(p["val"]) <= 0:
            raise SystemExit("« %s » contient une valeur nulle ou négative"
                             % p["titre"])

    rapports = {p["titre"]: p["val"][-1] / p["val"][0] for p in PANNEAUX}
    for nom, (attendu, tol) in ANNONCES.items():
        trouve = rapports[nom]
        if abs(trouve - attendu) > tol:
            raise SystemExit("l'article annonce un rapport de %.2f pour "
                             "« %s », les mesures donnent %.2f"
                             % (attendu, nom, trouve))

    #  La légende dit « multipliée par plus de trois » : ce n'est vrai que
    #  parce que la 1K vaut 0,66 Go, pas les 0,8 du corps de l'article.
    if rapports["Mémoire de Blender"] <= 3.0:
        raise SystemExit("la légende annonce une mémoire multipliée par plus "
                         "de trois, les mesures donnent %.2f"
                         % rapports["Mémoire de Blender"])

    temps = dict(zip(RESOLUTIONS, PANNEAUX[3]["val"]))
    surcout = temps["8K"] - temps["4K"]
    if abs(surcout - SURCOUT_8K) > 0.05:
        raise SystemExit("l'article annonce %.1f s de plus en 8K, les mesures "
                         "donnent %.1f" % (SURCOUT_8K, surcout))

    o = []
    o.append(texte("titre", (MARGE, 46), D.typo(TITRE), "titre", D.ENCRE,
                   2.2))
    sous = D.typo(SOUS)
    if mesure.mesure(sous, fontes["sous"]) > L - 2 * MARGE:
        raise SystemExit("le sous-titre déborde")
    o.append(texte("titre", (MARGE, 74), sous, "sous", D.FAIBLE))

    largeur = (L - 2 * MARGE - (len(PANNEAUX) - 1) * ECART_PANNEAU) \
        / float(len(PANNEAUX))
    pleine = len(RESOLUTIONS) * LARGEUR_BARRE \
        + (len(RESOLUTIONS) - 1) * ECART_BARRE
    if pleine > largeur:
        raise SystemExit("les %d barres font %d px pour un panneau de %d"
                         % (len(RESOLUTIONS), pleine, largeur))

    entetes, sols, barres, valeurs, res = [], [], [], [], []

    for i, p in enumerate(PANNEAUX):
        x0 = MARGE + i * (largeur + ECART_PANNEAU)

        for cle, police in (("titre", "panneau"), ("unite", "unite")):
            t = D.typo(p[cle])
            if mesure.mesure(t, fontes[police]) > largeur:
                raise SystemExit("« %s » fait %d px pour un panneau de %d"
                                 % (t, mesure.mesure(t, fontes[police]),
                                    largeur))
        entetes.append(texte("entetes", (x0, Y_PANNEAU), D.typo(p["titre"]),
                             "panneau", D.ENCRE))
        entetes.append(texte("entetes", (x0 + 1, Y_PANNEAU + 25),
                             D.typo(p["unite"]), "unite", D.GRIS))
        r = D.typo(rapport(ANNONCES[p["titre"]][0]))
        if mesure.mesure(r, fontes["rapport"]) > largeur:
            raise SystemExit("« %s » déborde du panneau" % r)
        entetes.append(texte("entetes", (x0 + 1, Y_PANNEAU + 46), r,
                             "rapport", INDIGO))

        sols.append(trait("sols", [x0, Y_BASE, x0 + largeur, Y_BASE],
                          D.FILET, 2))

        plafond = max(p["val"]) * MARGE_PLAFOND
        bx = x0 + (largeur - pleine) / 2.0
        for j, (v, nom_r) in enumerate(zip(p["val"], RESOLUTIONS)):
            gx = bx + j * (LARGEUR_BARRE + ECART_BARRE)
            h = v / plafond * H_UTILE
            barres.append(rect("barres", [gx, Y_BASE - h,
                                          gx + LARGEUR_BARRE, Y_BASE],
                               4, BARRE))

            lab = nombre(v, p["dec"])
            if mesure.mesure(lab, fontes["valeur"]) > LARGEUR_BARRE + 14:
                raise SystemExit("« %s » fait %d px pour une barre de %d"
                                 % (lab, mesure.mesure(lab, fontes["valeur"]),
                                    LARGEUR_BARRE))
            valeurs.append(texte("valeurs",
                                 (gx + LARGEUR_BARRE / 2.0, Y_BASE - h - 24),
                                 lab, "valeur", D.ENCRE, centre=True))
            res.append(texte("res", (gx + LARGEUR_BARRE / 2.0, Y_BASE + 12),
                             nom_r, "res", D.GRIS, centre=True))

    #  La plus haute barre ne doit pas monter dans l'en-tête du panneau.
    haut_barre = Y_BASE - H_UTILE / MARGE_PLAFOND
    if haut_barre - 24 < Y_PANNEAU + 64:
        raise SystemExit("les barres montent jusqu'à %d px et l'en-tête "
                         "descend à %d" % (haut_barre - 24, Y_PANNEAU + 64))

    o.extend(entetes)
    o.extend(sols)
    o.extend(barres)
    o.extend(valeurs)
    o.extend(res)

    note = D.typo(NOTE)
    if mesure.mesure(note, fontes["note"]) > L - 2 * MARGE:
        raise SystemExit("la note déborde")
    o.append(texte("note", (MARGE, Y_BASE + 56), note, "note", D.FAIBLE))

    H = Y_BASE + 108
    o.insert(0, rect("fond", [0, 0, L, H], 0, D.PAPIER))
    return H, o, rapports, surcout


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
                        "hdri-blender-resolution")
    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5),
               ("faible", D.FAIBLE, 3.0), ("indigo", INDIGO, 4.5))

    H, ordres, rapports, surcout = composer()
    rendre_matriciel(H, ordres, base)
    couches, textes = rendre_svg(H, ordres, base)

    print()
    print("  %-38s %.0f Ko"
          % (os.path.basename(base + ".svg"),
             os.path.getsize(base + ".svg") / 1024.0))
    print("  %d x %d, %d calques, %d textes" % (L, H, couches, textes))
    print()
    for p in PANNEAUX:
        print("  %-20s %s"
              % (p["titre"],
                 "  ".join("%s %s" % (r, nombre(v, p["dec"]))
                           for r, v in zip(RESOLUTIONS, p["val"]))))
    print()
    for nom, v in rapports.items():
        print("  %-20s 1K vers 8K : x%.2f" % (nom, v))
    print("  %-20s 4K vers 8K : +%.1f s" % ("Temps de rendu", surcout))


if __name__ == "__main__":
    principal()
