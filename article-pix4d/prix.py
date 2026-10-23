"""
Le prix d'appel de Pix4D, et ce qu'il coûte sans engagement.

    python3 article-pix4d/prix.py

Produit `pix4d-prix-engagement.webp`, son PNG et le SVG éditable.

----------------------------------------------------------------------------
CE QUE CETTE FIGURE REMPLACE
----------------------------------------------------------------------------
Une première version circulait hors charte : fond crème, titre bleu
marine, pastilles orange et bleu vif. Les prix sont repris à l'euro près.

----------------------------------------------------------------------------
NI ROUGE NI VERT, PARCE QU'AUCUNE DES DEUX OFFRES N'EST MALADE
----------------------------------------------------------------------------
La charte réserve l'alerte et le vert aux figures qui opposent un état
sain à un état dégradé. Payer d'avance pour trois ans n'est pas sain, et
payer au mois n'est pas dégradé : ce sont deux façons d'acheter. Les
deux séries prennent donc les teintes neutres prévues pour ça, l'indigo
de la maison pour le prix d'appel et l'ambre pour le prix sans
engagement.

----------------------------------------------------------------------------
LE CLASSEMENT EST CELUI DU PRIX FORT, PAS CELUI DE L'ÉCART
----------------------------------------------------------------------------
Les offres sont rangées par prix sans engagement décroissant. L'écart
le plus spectaculaire, PIX4Dfields et son facteur 3,2, se trouve donc au
milieu du tableau et non en tête : c'est la phrase du bas qui le
désigne. Ranger par écart aurait mieux servi la phrase et moins bien le
lecteur, qui cherche d'abord un prix.

Un contrôle vérifie que PIX4Dfields porte bien le plus grand écart de la
figure : sans lui, la phrase du bas pourrait désigner une offre qui
n'est plus la bonne.
"""

import os

import charte as C
import dessin as D

L = 1600
MARGE = 56

APPEL = C.VIOLET_TEXTE          # l'indigo de la maison
SANS = (180, 83, 9)             # l'ambre des figures à plusieurs séries

#  ---------------------------------------------------------------------------
#  LES NEUF OFFRES
#
#  `appel` est le coût mensuel hors taxes avec engagement de trois ans
#  payé d'avance, `sans` le même coût sans engagement, payé au mois.
#  `mention` ne sert qu'à PIX4Dmapper, qui n'a pas d'offre à trois ans.
#  ---------------------------------------------------------------------------
OFFRES = (
    {"nom": "PIX4Dmatic Pro", "appel": 222, "sans": 449},
    {"nom": "PIX4Dcloud Pro", "appel": 222, "sans": 399},
    {"nom": "PIX4Dmatic Standard", "appel": 175, "sans": 349},
    {"nom": "PIX4Dmapper", "appel": 291, "sans": 349,
     "mention": "pas d’offre 3 ans"},
    {"nom": "PIX4Dfields", "appel": 105, "sans": 339},
    {"nom": "PIX4Dmatic Analyst", "appel": 119, "sans": 219},
    {"nom": "PIX4Dcatch Pro", "appel": 111, "sans": 159},
    {"nom": "PIX4Dcloud Starter", "appel": 55, "sans": 99},
    {"nom": "PIX4Dreact", "appel": 50, "sans": 89},
)

#  Ce que la phrase du bas affirme, et que le dessin doit retrouver seul.
VEDETTE = "PIX4Dfields"
FACTEUR = 3.2

GRADUATIONS = (0, 100, 200, 300, 400)
PLAFOND = 470

POLICES = {
    "titre": (C.POLICE_G, 19, "bold"),
    "sous": (C.POLICE_R, 17, "normal"),
    "legende": (C.POLICE_R, 15, "normal"),
    "nom": (C.POLICE_G, 18, "bold"),
    "mention": (C.POLICE_R, 13, "normal"),
    "prix": (C.POLICE_G, 16, "bold"),
    "axe": (C.POLICE_R, 14, "normal"),
    "trouvaille": (C.POLICE_G, 16, "bold"),
}
FAMILLE_SVG = "Liberation Sans, Arial, Helvetica, sans-serif"

TITRE = "CHEZ PIX4D, LE PRIX D’APPEL ENGAGE POUR TROIS ANS"
SOUS = ("coût mensuel hors taxes de chaque offre, relevé le 23 octobre 2026 "
        "sur pix4d.com depuis la France")
LEGENDES = (("appel", "Prix d’appel : engagement de 3 ans, payé d’avance "
                      "(1 an pour PIX4Dmapper)"),
            ("sans", "Sans engagement, payé au mois"))

Y_LEGENDE = 118
Y0 = 184
H_LIGNE = 54
X_NOM = MARGE
X_ZERO = 436
X_PLAFOND = 1424
R_POINT = 9


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


def euros(v):
    return "%d €" % v


def composer():
    mesure = D.Toile(L, 10)
    fontes = {k: mesure.police(f, t) for k, (f, t, _) in POLICES.items()}

    #  ------------------------------------------------------------------
    #  CONTRÔLES
    #  ------------------------------------------------------------------
    for o in OFFRES:
        if o["sans"] <= o["appel"]:
            raise SystemExit("« %s » ne coûte pas plus cher sans engagement "
                             "qu'avec : la figure n'a plus de sens" % o["nom"])
        if o["sans"] > PLAFOND:
            raise SystemExit("« %s » à %d € sort de l'axe, qui s'arrête à %d"
                             % (o["nom"], o["sans"], PLAFOND))

    sans = [o["sans"] for o in OFFRES]
    if sans != sorted(sans, reverse=True):
        raise SystemExit("les offres ne sont plus rangées par prix sans "
                         "engagement décroissant")

    ecarts = {o["nom"]: o["sans"] / float(o["appel"]) for o in OFFRES}
    pire = max(ecarts, key=ecarts.get)
    if pire != VEDETTE:
        raise SystemExit("la phrase du bas désigne « %s », mais le plus grand "
                         "écart est celui de « %s » (x%.2f)"
                         % (VEDETTE, pire, ecarts[pire]))
    if abs(round(ecarts[VEDETTE], 1) - FACTEUR) > 1e-9:
        raise SystemExit("la phrase annonce un facteur %.1f pour « %s », les "
                         "prix donnent %.2f"
                         % (FACTEUR, VEDETTE, ecarts[VEDETTE]))

    v = next(o for o in OFFRES if o["nom"] == VEDETTE)
    trouvaille = ("Sans engagement, %s coûte %s fois son prix d’appel : %s "
                  "par mois au lieu de %s."
                  % (VEDETTE, ("%.1f" % FACTEUR).replace(".", ","),
                     euros(v["sans"]), euros(v["appel"])))

    echelle = (X_PLAFOND - X_ZERO) / float(PLAFOND)

    def abscisse(e):
        return X_ZERO + e * echelle

    o_ = []
    o_.append(texte("titre", (MARGE, 46), D.typo(TITRE), "titre", D.ENCRE,
                    2.2))
    sous = D.typo(SOUS)
    if mesure.mesure(sous, fontes["sous"]) > L - 2 * MARGE:
        raise SystemExit("le sous-titre déborde")
    o_.append(texte("titre", (MARGE, 74), sous, "sous", D.FAIBLE))

    #  -----------------------------------------------------------  légende
    legende = []
    x = MARGE
    for cle, mot in LEGENDES:
        m = D.typo(mot)
        legende.append(disque("legende", x + R_POINT, Y_LEGENDE + 8, R_POINT,
                              APPEL if cle == "appel" else SANS))
        legende.append(texte("legende", (x + 2 * R_POINT + 12, Y_LEGENDE), m,
                             "legende", D.ENCRE))
        x += 2 * R_POINT + 12 + mesure.mesure(m, fontes["legende"]) + 54
    if x > L - MARGE:
        raise SystemExit("la légende finit à %d px et le cadre s'arrête à %d"
                         % (x, L - MARGE))
    o_.extend(legende)

    #  ----------------------------------------------------------  l'échelle
    bas = Y0 + len(OFFRES) * H_LIGNE - 14
    grille = []
    for g in GRADUATIONS:
        gx = abscisse(g)
        grille.append(trait("grille", [gx, Y_LEGENDE + 44, gx, bas],
                            D.FILET, 1))
        grille.append(texte("grille", (gx, bas + 12),
                            "0" if g == 0 else euros(g), "axe", D.FAIBLE,
                            centre=True))
    grille.append(texte("grille", (abscisse(GRADUATIONS[-1]) + 42, bas + 12),
                        "par mois", "axe", D.FAIBLE))
    o_.extend(grille)

    #  -----------------------------------------------------------  les lignes
    liens, points, noms, prix = [], [], [], []
    limite = 1e9

    for i, o in enumerate(OFFRES):
        y = Y0 + i * H_LIGNE
        xa, xs = abscisse(o["appel"]), abscisse(o["sans"])

        noms.append(texte("noms", (X_NOM, y - 10), o["nom"], "nom",
                          D.ENCRE))
        if "mention" in o:
            noms.append(texte("noms", (X_NOM, y + 12),
                              D.typo(o["mention"]), "mention", D.FAIBLE))

        liens.append(trait("liens", [xa, y, xs, y], D.FILET, 3))
        points.append(disque("points", xa, y, R_POINT, APPEL))
        points.append(disque("points", xs, y, R_POINT, SANS))

        #  Le prix d'appel se range à gauche de son point, le prix sans
        #  engagement à droite du sien : les deux étiquettes s'éloignent
        #  l'une de l'autre et ne peuvent pas se toucher.
        la = euros(o["appel"])
        large = mesure.mesure(la, fontes["prix"])
        gauche = xa - R_POINT - 12 - large
        prix.append(texte("prix", (gauche, y - 10), la, "prix", APPEL))
        limite = min(limite, gauche)

        ls = euros(o["sans"])
        prix.append(texte("prix", (xs + R_POINT + 12, y - 10), ls, "prix",
                          SANS))
        bout = xs + R_POINT + 12 + mesure.mesure(ls, fontes["prix"])
        if bout > L - MARGE:
            raise SystemExit("« %s » finit à %d px et le cadre s'arrête à %d"
                             % (ls, bout, L - MARGE))

    #  Aucun prix d'appel ne doit mordre sur la colonne des noms.
    plus_long = max(mesure.mesure(o["nom"], fontes["nom"]) for o in OFFRES)
    if limite < X_NOM + plus_long + 28:
        raise SystemExit("un prix d'appel commence à %d px et le plus long "
                         "nom finit à %d" % (limite, X_NOM + plus_long))

    o_.extend(liens)
    o_.extend(points)
    o_.extend(noms)
    o_.extend(prix)

    t = D.typo(trouvaille)
    if mesure.mesure(t, fontes["trouvaille"]) > L - 2 * MARGE:
        raise SystemExit("la phrase du bas déborde")
    o_.append(texte("trouvaille", (MARGE, bas + 54), t, "trouvaille",
                    D.ENCRE))

    H = int(bas + 112)
    o_.insert(0, rect("fond", [0, 0, L, H], 0, D.PAPIER))
    return H, o_, ecarts


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
                        "pix4d-prix-engagement")
    D.verifier(("encre", D.ENCRE, 4.5), ("faible", D.FAIBLE, 3.0),
               ("indigo", APPEL, 4.5), ("ambre", SANS, 4.5))

    H, ordres, ecarts = composer()
    rendre_matriciel(H, ordres, base)
    couches, textes = rendre_svg(H, ordres, base)

    print()
    print("  %-38s %.0f Ko"
          % (os.path.basename(base + ".svg"),
             os.path.getsize(base + ".svg") / 1024.0))
    print("  %d x %d, %d calques, %d textes" % (L, H, couches, textes))
    print()
    for o in OFFRES:
        print("  %-22s %4s  vers %5s   x%.2f"
              % (o["nom"], euros(o["appel"]), euros(o["sans"]),
                 ecarts[o["nom"]]))
    print()
    print("  plus grand écart : %s, x%.2f"
          % (VEDETTE, ecarts[VEDETTE]))


if __name__ == "__main__":
    principal()
