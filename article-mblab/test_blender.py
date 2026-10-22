"""
MB-Lab et CharMorph, huit étapes dans trois Blender.

    python3 article-mblab/test_blender.py

Produit `mb-lab-test-blender-5-2.webp`, son PNG et le SVG éditable.

----------------------------------------------------------------------------
CE QUE CETTE FIGURE REMPLACE
----------------------------------------------------------------------------
Une première version circulait avec une palette qui n'est pas la nôtre :
fond crème, titres bleu marine, bandes zébrées, pastilles bleues pour
les réussites et orange pour l'échec, plus un filtre de grain par-dessus
le tout. Aucune de ces teintes n'est dans la charte.

Le défaut le plus net n'était pas une affaire de goût : l'orange des
échecs mesurait 3,07:1 sur son fond, sous le seuil de 4,5:1. La seule
case qui portait toute l'information était la moins lisible du dessin.

----------------------------------------------------------------------------
ROUGE ET VERT, ET C'EST ICI QU'ILS SERVENT
----------------------------------------------------------------------------
La charte réserve l'alerte et le vert aux figures qui opposent un état
sain à un état dégradé. Une étape qui passe contre une étape qui casse
est exactement ce cas. Le passé est un disque plein, l'échec un anneau
creux : l'absence se lit comme une absence.

----------------------------------------------------------------------------
QUARANTE-SEPT COCHES POUR UNE CROIX
----------------------------------------------------------------------------
Sur quarante-huit cases, une seule échoue. La grille est donc presque
entièrement du bruit, et c'est volontaire : elle sert à prouver que tout
le reste tient. Le compte sous chaque extension dit en deux mots ce que
la grille met quarante-huit marques à démontrer.
"""

import os

import charte as C
import dessin as D

L = 1600
MARGE = 56

INDIGO = C.VIOLET_TEXTE
VERT = C.VERT
ALERTE = C.ALERTE

#  ---------------------------------------------------------------------------
#  LE TEST
#
#  Chaque étape porte, pour chaque extension, le résultat dans les trois
#  Blender testés. `False` est un échec, et il n'y en a qu'un.
#  ---------------------------------------------------------------------------
BLENDERS = ("4.2", "4.5", "5.2")

OUTILS = (
    {"nom": "MB-Lab 1.8.1", "cle": "mblab"},
    {"nom": "CharMorph 0.4.0", "cle": "charmorph"},
)

ETAPES = (
    {"nom": "Installation du zip",        "mblab": (1, 1, 1),
     "charmorph": (1, 1, 1)},
    {"nom": "Activation",                 "mblab": (1, 1, 1),
     "charmorph": (1, 1, 1)},
    {"nom": "Création d’un personnage",   "mblab": (1, 1, 1),
     "charmorph": (1, 1, 1)},
    {"nom": "Réglage de la morphologie",  "mblab": (1, 1, 1),
     "charmorph": (1, 1, 1)},
    {"nom": "Finalisation avec squelette", "mblab": (1, 1, 1),
     "charmorph": (1, 1, 1)},
    {"nom": "Export FBX",                 "mblab": (1, 1, 1),
     "charmorph": (1, 1, 1)},
    {"nom": "Rendu Cycles",               "mblab": (1, 1, 1),
     "charmorph": (1, 1, 1)},
    {"nom": "Panneau de l’extension",     "mblab": (1, 1, 0),
     "charmorph": (1, 1, 1)},
)

#  Ce que l'article affirme, et que la figure doit retrouver seule.
ANNONCES = {"cas testés": 48, "échecs": 1}
SEUL_ECHEC = ("mblab", "5.2", "Panneau de l’extension")

POLICES = {
    "titre": (C.POLICE_G, 19, "bold"),
    "sous": (C.POLICE_R, 17, "normal"),
    "outil": (C.POLICE_G, 19, "bold"),
    "compte": (C.POLICE_R, 15, "normal"),
    "version": (C.POLICE_R, 15, "normal"),
    "etape": (C.POLICE_R, 17, "normal"),
    "note": (C.POLICE_R, 14, "normal"),
}
FAMILLE_SVG = "Liberation Sans, Arial, Helvetica, sans-serif"

TITRE = "DANS BLENDER 5.2, MB-LAB TOURNE ENCORE, SAUF SON PANNEAU"
SOUS = ("test du 22 octobre 2026 : huit étapes, deux extensions, trois "
        "versions de Blender")
NOTE = ("Les sept premières étapes ont été exécutées dans Blender sans "
        "interface ; le panneau a été contrôlé dans son code.")

Y_OUTIL = 136
Y_VERSION = 190
Y0 = 234                  # première étape
H_LIGNE = 44
X_NOM = MARGE
R_MARQUE = 12
PAS_COLONNE = 112
GROUPES = (880, 1250)     # abscisse de la première colonne de chaque outil


def rect(couche, b, r, teinte):
    return {"quoi": "rect", "couche": couche, "b": b, "r": r, "t": teinte}


def trait(couche, b, teinte, epaisseur, tirets=None):
    return {"quoi": "trait", "couche": couche, "b": b, "t": teinte,
            "e": epaisseur, "tirets": tirets}


def disque(couche, cx, cy, r, teinte=None, contour=None, epaisseur=2):
    return {"quoi": "disque", "couche": couche, "cx": cx, "cy": cy, "r": r,
            "t": teinte, "contour": contour, "e": epaisseur}


def polyligne(couche, points, teinte, epaisseur):
    return {"quoi": "polyligne", "couche": couche, "pts": points,
            "t": teinte, "e": epaisseur}


def texte(couche, xy, contenu, police, teinte, tracking=0.0, centre=False):
    for c, nom in (("—", "cadratin"), ("–", "demi-cadratin")):
        if c in contenu:
            raise SystemExit("%s dans « %s »" % (nom, contenu[:60]))
    return {"quoi": "texte", "couche": couche, "xy": xy, "c": contenu,
            "p": police, "t": teinte, "tr": tracking, "centre": centre}


def marque(couche, cx, cy, passe):
    """Disque plein et coche quand ça passe, anneau creux et croix sinon."""
    r = R_MARQUE
    if passe:
        return [disque(couche, cx, cy, r, teinte=VERT),
                polyligne(couche, [(cx - 5.5, cy + 0.5), (cx - 1.5, cy + 4.5),
                                   (cx + 5.5, cy - 4.5)], D.BLANC, 2.6)]
    d = 4.6
    return [disque(couche, cx, cy, r, contour=ALERTE, epaisseur=2.4),
            polyligne(couche, [(cx - d, cy - d), (cx + d, cy + d)],
                      ALERTE, 2.4),
            polyligne(couche, [(cx - d, cy + d), (cx + d, cy - d)],
                      ALERTE, 2.4)]


def composer():
    mesure = D.Toile(L, 10)
    fontes = {k: mesure.police(f, t) for k, (f, t, _) in POLICES.items()}

    #  ------------------------------------------------------------------
    #  CONTRÔLES
    #  ------------------------------------------------------------------
    cases, echecs = 0, []
    for e in ETAPES:
        for o in OUTILS:
            res = e[o["cle"]]
            if len(res) != len(BLENDERS):
                raise SystemExit("« %s » donne %d résultats pour %d Blender"
                                 % (e["nom"], len(res), len(BLENDERS)))
            for v, ok in zip(BLENDERS, res):
                cases += 1
                if not ok:
                    echecs.append((o["cle"], v, e["nom"]))

    trouve = {"cas testés": cases, "échecs": len(echecs)}
    for quoi, attendu in ANNONCES.items():
        if trouve[quoi] != attendu:
            raise SystemExit("l'article annonce %d %s, la figure en compte %d"
                             % (attendu, quoi, trouve[quoi]))
    if echecs[0] != SEUL_ECHEC:
        raise SystemExit("le seul échec attendu est %s, la figure trouve %s"
                         % (SEUL_ECHEC, echecs[0]))

    #  Le compte par extension, recalculé : c'est lui qui dit en deux mots
    #  ce que la grille met quarante-huit marques à démontrer.
    par_outil = {}
    for o in OUTILS:
        total = len(ETAPES) * len(BLENDERS)
        passes = sum(sum(e[o["cle"]]) for e in ETAPES)
        par_outil[o["cle"]] = (passes, total)

    o_ = []
    o_.append(texte("titre", (MARGE, 46), D.typo(TITRE), "titre", D.ENCRE,
                    2.2))
    sous = D.typo(SOUS)
    if mesure.mesure(sous, fontes["sous"]) > L - 2 * MARGE:
        raise SystemExit("le sous-titre déborde")
    o_.append(texte("titre", (MARGE, 74), sous, "sous", D.FAIBLE))

    #  -----------------------------------------------------  en-tête, par outil
    entetes = []
    colonnes = {}
    for o, x0 in zip(OUTILS, GROUPES):
        xs = [x0 + i * PAS_COLONNE for i in range(len(BLENDERS))]
        colonnes[o["cle"]] = xs
        centre = (xs[0] + xs[-1]) / 2.0

        entetes.append(texte("entetes", (centre, Y_OUTIL), D.typo(o["nom"]),
                             "outil", D.ENCRE, centre=True))
        passes, total = par_outil[o["cle"]]
        compte = "%d cas sur %d" % (passes, total)
        #  Le compte reste neutre. L'alerte ne sert qu'à la case qui
        #  échoue : écrire « 23 cas sur 24 » en rouge ferait un verdict
        #  négatif là où l'article dit que presque tout tient.
        entetes.append(texte("entetes", (centre, Y_OUTIL + 26), compte,
                             "compte", D.GRIS, centre=True))
        entetes.append(trait("entetes",
                             [xs[0] - 34, Y_OUTIL + 52, xs[-1] + 34,
                              Y_OUTIL + 52], D.FILET, 1))
        for x, v in zip(xs, BLENDERS):
            entetes.append(texte("entetes", (x, Y_VERSION),
                                 D.typo("Blender %s" % v), "version",
                                 D.GRIS, centre=True))

    #  Les deux groupes ne doivent pas se toucher, et le second doit tenir
    #  dans le cadre.
    g0 = colonnes[OUTILS[0]["cle"]][-1] + 34
    g1 = colonnes[OUTILS[1]["cle"]][0] - 34
    if g1 - g0 < 40:
        raise SystemExit("les deux groupes se touchent : %d px entre eux"
                         % (g1 - g0))
    if colonnes[OUTILS[-1]["cle"]][-1] + R_MARQUE > L - MARGE:
        raise SystemExit("la dernière colonne sort du cadre")

    o_.extend(entetes)

    #  ------------------------------------------------------------  les lignes
    conduites, marques, libelles = [], [], []
    limite = GROUPES[0] - R_MARQUE - 40

    for i, e in enumerate(ETAPES):
        y = Y0 + i * H_LIGNE
        nom = D.typo(e["nom"])
        libelles.append(texte("etapes", (X_NOM, y), nom, "etape", D.ENCRE))
        bout = X_NOM + mesure.mesure(nom, fontes["etape"])
        if bout > limite:
            raise SystemExit("« %s » finit à %d px et la première colonne "
                             "commence à %d" % (nom, bout, limite))

        #  Une conduite pointillée de l'étape à sa première marque : sans
        #  elle, l'oeil traverse six cents pixels de papier et se trompe
        #  de ligne.
        conduites.append(trait("conduites",
                               [bout + 16, y + 10, GROUPES[0] - R_MARQUE - 16,
                                y + 10], D.FILET, 1, tirets=(3, 7)))

        for o in OUTILS:
            for x, ok in zip(colonnes[o["cle"]], e[o["cle"]]):
                marques.extend(marque("marques", x, y + 9, ok))

    o_.extend(conduites)
    o_.extend(marques)
    o_.extend(libelles)

    bas = Y0 + len(ETAPES) * H_LIGNE
    note = D.typo(NOTE)
    if mesure.mesure(note, fontes["note"]) > L - 2 * MARGE:
        raise SystemExit("la note déborde")
    o_.append(texte("note", (MARGE, bas + 16), note, "note", D.FAIBLE))

    H = int(bas + 70)
    o_.insert(0, rect("fond", [0, 0, L, H], 0, D.PAPIER))
    return H, o_, par_outil, echecs


def rendre_matriciel(H, ordres, base):
    t = D.Toile(L, H)
    fontes = {k: t.police(f, taille) for k, (f, taille, _) in POLICES.items()}
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
        elif a["quoi"] == "disque":
            t.disque(a["cx"], a["cy"], a["r"], teinte=a["t"],
                     contour=a["contour"], epaisseur=a["e"])
        elif a["quoi"] == "polyligne":
            t.polyligne(a["pts"], a["t"], a["e"])
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
                tirets = ('" stroke-dasharray="%g %g'
                          % a["tirets"]) if a.get("tirets") else ""
                out.append('    <line x1="%g" y1="%g" x2="%g" y2="%g" '
                           'stroke="%s" stroke-width="%g%s"/>'
                           % (x0, y0, x1, y1, teinte(a["t"]), a["e"], tirets))
            elif a["quoi"] == "disque":
                remplissage = teinte(a["t"]) if a["t"] else "none"
                bord = ('" stroke="%s" stroke-width="%g'
                        % (teinte(a["contour"]), a["e"])) if a["contour"] \
                    else ""
                out.append('    <circle cx="%g" cy="%g" r="%g" fill="%s%s"/>'
                           % (a["cx"], a["cy"], a["r"], remplissage, bord))
            elif a["quoi"] == "polyligne":
                pts = " ".join("%g,%g" % p for p in a["pts"])
                out.append('    <polyline points="%s" fill="none" '
                           'stroke="%s" stroke-width="%g" '
                           'stroke-linecap="round" stroke-linejoin="round"/>'
                           % (pts, teinte(a["t"]), a["e"]))
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
                        "mb-lab-test-blender-5-2")
    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5),
               ("faible", D.FAIBLE, 3.0), ("alerte", ALERTE, 4.5),
               ("vert", VERT, 4.5))
    r = C.contraste(D.BLANC, VERT)
    print("  %-8s %-16s %.2f:1  %s"
          % ("blanc", str(VERT), r, "ok" if r >= 4.5 else "INSUFFISANT"))
    if r < 4.5:
        raise SystemExit("la coche blanche sur le vert : %.2f:1" % r)

    H, ordres, par_outil, echecs = composer()
    rendre_matriciel(H, ordres, base)
    couches, textes = rendre_svg(H, ordres, base)

    print()
    print("  %-38s %.0f Ko"
          % (os.path.basename(base + ".svg"),
             os.path.getsize(base + ".svg") / 1024.0))
    print("  %d x %d, %d calques, %d textes" % (L, H, couches, textes))
    print()
    for o in OUTILS:
        passes, total = par_outil[o["cle"]]
        print("  %-18s %d cas sur %d" % (o["nom"], passes, total))
    print()
    for cle, v, etape in echecs:
        print("  seul échec : %s, Blender %s, « %s »" % (cle, v, etape))


if __name__ == "__main__":
    principal()
