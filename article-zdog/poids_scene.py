"""
Ce que pèse une boule qui tourne, selon la bibliothèque.

    python3 article-zdog/poids_scene.py

Produit `zdog-poids-scene.webp`, son PNG et le SVG éditable.

----------------------------------------------------------------------------
L'ÉCHELLE RESTE LINÉAIRE, ET C'EST LE SUJET
----------------------------------------------------------------------------
Sur une échelle linéaire, la barre de Zdog ne fait que 2,3 % de celle de
Babylon.js : un trait de vingt-six pixels contre onze cents. La tentation
serait de passer en échelle logarithmique pour « équilibrer » la figure.
Ce serait détruire la seule chose qu'elle a à dire.

La disproportion est le propos de l'article, pas un défaut de dessin. Les
valeurs sont donc posées à côté de chaque barre, où elles tiennent quelle
que soit sa longueur.

----------------------------------------------------------------------------
NI ROUGE NI VERT
----------------------------------------------------------------------------
Trois bibliothèques qui pèsent trois poids, ce n'est pas un état sain
contre un état dégradé : c'est un classement. Rien ne justifie une teinte
de signalisation, et les trois barres sont du même indigo.

----------------------------------------------------------------------------
LE RAPPORT DE L'ARTICLE EST RECALCULÉ
----------------------------------------------------------------------------
« Zdog pèse 17 fois moins que three.js » : 129,3 divisé par 7,8 fait
16,58, qui s'arrondit bien à 17. Le contrôle le refait à chaque dessin.
Le rapport à Babylon.js, 43, n'est pas dans l'article : c'est la même
division sur les mêmes chiffres, et la figure l'écrit parce qu'elle a
la place de le faire.
"""

import os

import charte as C
import dessin as D

L = 1600
MARGE = 56

INDIGO = C.VIOLET_TEXTE
BARRE = (124, 96, 208)

#  ---------------------------------------------------------------------------
#  LA MÊME SCÈNE, TROIS FOIS
#
#  Poids en kibioctets d'une boule qui tourne, empaquetée et minifiée avec
#  esbuild puis compressée. `dec` est le nombre de décimales affichées.
#  ---------------------------------------------------------------------------
REFERENCE = "Zdog"
BIBLIOTHEQUES = (
    {"nom": "Zdog", "kio": 7.8, "dec": 1},
    {"nom": "three.js", "kio": 129.3, "dec": 1},
    {"nom": "Babylon.js", "kio": 332.0, "dec": 0},
)

#  Ce que l'article affirme, et que la figure doit retrouver seule.
ANNONCES = {"three.js": 17}

POLICES = {
    "titre": (C.POLICE_G, 19, "bold"),
    "sous": (C.POLICE_R, 17, "normal"),
    "nom": (C.POLICE_G, 20, "bold"),
    "rapport": (C.POLICE_R, 14, "normal"),
    "valeur": (C.POLICE_G, 18, "bold"),
    "note": (C.POLICE_R, 14, "normal"),
}
FAMILLE_SVG = "Liberation Sans, Arial, Helvetica, sans-serif"

TITRE = "LA MÊME BOULE QUI TOURNE, DE 7,8 À 332 KIO"
SOUS = ("poids compressé d’une scène minimale, empaquetée et minifiée avec "
        "esbuild")
NOTE = ("Kibioctets après compression. Zdog 1.1.3, et pour chaque "
        "bibliothèque la même sphère animée, rien de plus.")

Y0 = 164
H_LIGNE = 84
H_BARRE = 38
X_NOM = MARGE
X_BARRE = 376
X_FIN = L - MARGE - 128


def rect(couche, b, r, teinte):
    return {"quoi": "rect", "couche": couche, "b": b, "r": r, "t": teinte}


def texte(couche, xy, contenu, police, teinte, tracking=0.0, centre=False):
    for c, nom in (("—", "cadratin"), ("–", "demi-cadratin")):
        if c in contenu:
            raise SystemExit("%s dans « %s »" % (nom, contenu[:60]))
    return {"quoi": "texte", "couche": couche, "xy": xy, "c": contenu,
            "p": police, "t": teinte, "tr": tracking, "centre": centre}


def kio(v, dec):
    return ("%.*f" % (dec, v)).replace(".", ",") + " Kio"


def composer():
    mesure = D.Toile(L, 10)
    fontes = {k: mesure.police(f, t) for k, (f, t, _) in POLICES.items()}

    #  ------------------------------------------------------------------
    #  CONTRÔLES
    #  ------------------------------------------------------------------
    ref = next((b for b in BIBLIOTHEQUES if b["nom"] == REFERENCE), None)
    if ref is None:
        raise SystemExit("« %s » sert de référence aux rapports, mais ne "
                         "figure pas dans la liste" % REFERENCE)

    rapports = {b["nom"]: b["kio"] / ref["kio"] for b in BIBLIOTHEQUES}
    for nom, attendu in ANNONCES.items():
        trouve = round(rapports[nom])
        if trouve != attendu:
            raise SystemExit("l'article annonce un rapport de %d pour "
                             "« %s », les poids donnent %.2f"
                             % (attendu, nom, rapports[nom]))

    poids = [b["kio"] for b in BIBLIOTHEQUES]
    if poids != sorted(poids):
        raise SystemExit("les bibliothèques ne sont plus rangées de la plus "
                         "légère à la plus lourde")

    plafond = max(poids)
    echelle = (X_FIN - X_BARRE) / plafond

    o = []
    o.append(texte("titre", (MARGE, 46), D.typo(TITRE), "titre", D.ENCRE,
                   2.2))
    sous = D.typo(SOUS)
    if mesure.mesure(sous, fontes["sous"]) > L - 2 * MARGE:
        raise SystemExit("le sous-titre déborde")
    o.append(texte("titre", (MARGE, 74), sous, "sous", D.FAIBLE))

    barres, noms, valeurs = [], [], []

    for i, b in enumerate(BIBLIOTHEQUES):
        y = Y0 + i * H_LIGNE
        yb = y + 22

        noms.append(texte("noms", (X_NOM, y), b["nom"], "nom", D.ENCRE))
        #  Le rapport à la référence, sauf pour la référence elle-même :
        #  « Zdog pèse 1 fois Zdog » n'apprendrait rien à personne.
        if b["nom"] != REFERENCE:
            r = "%d fois %s" % (round(rapports[b["nom"]]), REFERENCE)
            noms.append(texte("noms", (X_NOM, y + 28), r, "rapport", D.GRIS))

        lb = b["kio"] * echelle
        barres.append(rect("barres", [X_BARRE, yb, X_BARRE + lb,
                                      yb + H_BARRE], 4, BARRE))

        #  La valeur se pose APRÈS la barre, jamais dedans : celle de Zdog
        #  ne fait que vingt-six pixels de long, aucune étiquette n'y tient.
        lab = kio(b["kio"], b["dec"])
        valeurs.append(texte("valeurs", (X_BARRE + lb + 16, yb + 9), lab,
                             "valeur", D.ENCRE))
        bout = X_BARRE + lb + 16 + mesure.mesure(lab, fontes["valeur"])
        if bout > L - MARGE:
            raise SystemExit("« %s » finit à %d px et le cadre s'arrête à %d"
                             % (lab, bout, L - MARGE))

    plus_long = max(mesure.mesure(b["nom"], fontes["nom"])
                    for b in BIBLIOTHEQUES)
    if X_NOM + plus_long + 28 > X_BARRE:
        raise SystemExit("la colonne des noms finit à %d px et les barres "
                         "commencent à %d" % (X_NOM + plus_long, X_BARRE))

    o.extend(barres)
    o.extend(noms)
    o.extend(valeurs)

    bas = Y0 + len(BIBLIOTHEQUES) * H_LIGNE
    note = D.typo(NOTE)
    if mesure.mesure(note, fontes["note"]) > L - 2 * MARGE:
        raise SystemExit("la note déborde")
    o.append(texte("note", (MARGE, bas + 4), note, "note", D.FAIBLE))

    H = int(bas + 56)
    o.insert(0, rect("fond", [0, 0, L, H], 0, D.PAPIER))
    return H, o, rapports


def rendre_matriciel(H, ordres, base):
    t = D.Toile(L, H)
    fontes = {k: t.police(f, taille) for k, (f, taille, _) in POLICES.items()}
    for a in ordres:
        if a["quoi"] == "rect":
            t.rrect(a["b"], a["r"], teinte=a["t"])
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
                        "zdog-poids-scene")
    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5),
               ("faible", D.FAIBLE, 3.0), ("indigo", INDIGO, 4.5))

    H, ordres, rapports = composer()
    rendre_matriciel(H, ordres, base)
    couches, textes = rendre_svg(H, ordres, base)

    print()
    print("  %-38s %.0f Ko"
          % (os.path.basename(base + ".svg"),
             os.path.getsize(base + ".svg") / 1024.0))
    print("  %d x %d, %d calques, %d textes" % (L, H, couches, textes))
    print()
    for b in BIBLIOTHEQUES:
        print("  %-12s %10s   x%.2f par rapport à %s"
              % (b["nom"], kio(b["kio"], b["dec"]), rapports[b["nom"]],
                 REFERENCE))


if __name__ == "__main__":
    principal()
