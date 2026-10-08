"""
La disparition des nouveautés Genesis 8, chez Daz et ailleurs.

    python3 article-genesis/boutiques_nouveautes.py

Produit `genesis-boutiques-nouveautes.webp`, son PNG et le SVG éditable.

----------------------------------------------------------------------------
DEUX MESURES, DEUX BLOCS, UNE SEULE ÉCHELLE
----------------------------------------------------------------------------
L'article compare 0,6 % chez Daz à 43 % sur RenderHub. Les deux nombres
sont justes, mais ils ne comptent pas la même chose : le premier porte
sur TOUS les produits conçus pour une figure, personnages, vêtements,
cheveux et poses ; le second sur les seuls personnages.

Les poser côte à côte sans le dire gonflerait l'écart d'un facteur
soixante-dix. La figure sépare donc les deux populations en deux blocs,
chacun avec son intitulé, et la comparaison entre boutiques se fait sur
la seule base commune : les personnages du 9 septembre au 7 octobre 2026,
1,1 % contre 42,6 %.

L'échelle verticale, elle, est COMMUNE aux deux blocs. Deux échelles
distinctes rendraient les hauteurs incomparables, ce qui est le défaut
classique de ce genre de figure à deux panneaux.

----------------------------------------------------------------------------
LES POURCENTAGES SONT CALCULÉS LÀ OÙ LES COMPTES EXISTENT
----------------------------------------------------------------------------
Trois valeurs sont données en effectifs dans l'article : 18 sur 3 215,
245 sur 575, 1 sur 94. Elles sont donc divisées ici, et comparées à ce
que l'article affirme. Les quatre valeurs annuelles antérieures ne sont
publiées qu'en pourcentage : elles sont reprises telles quelles, et le
script ne prétend pas les avoir vérifiées.
"""

import os

import charte as C
import dessin as D

L = 1600
MARGE = 56

INDIGO = C.VIOLET_TEXTE
INDIGO_PALE = (196, 180, 240)
AMBRE = (180, 83, 9)

#  ---------------------------------------------------------------------------
#  BLOC A : la part annuelle chez Daz.
#
#  `compte` n'est renseigné que lorsque l'article publie les effectifs.
#  Ailleurs, seul le pourcentage est connu, et il est repris tel quel.
#  ---------------------------------------------------------------------------
ANNEES = (
    {"libelle": "fin 2022", "part": 38.0, "compte": None},
    {"libelle": "2023", "part": 26.0, "compte": None},
    {"libelle": "2024", "part": 7.9, "compte": None},
    {"libelle": "2025", "part": 1.2, "compte": None},
    {"libelle": "2026", "part": None, "compte": (18, 3215)},
)
TITRE_A = "Boutique Daz, tous les produits conçus pour une figure"

#  ---------------------------------------------------------------------------
#  BLOC B : la même mesure, sur la seule base comparable.
#  ---------------------------------------------------------------------------
BOUTIQUES = (
    {"libelle": "Boutique Daz", "compte": (1, 94), "teinte": INDIGO},
    {"libelle": "RenderHub", "compte": (245, 575), "teinte": AMBRE},
)
TITRE_B = "Personnages seuls, du 9 septembre au 7 octobre 2026"

#  Ce que l'article affirme, et que le dessin doit continuer de vérifier.
#
#  Chaque valeur porte sa PRÉCISION, parce que l'article n'arrondit pas
#  partout pareil : il écrit « 0,6 % » au dixième et « 43 % » à l'unité.
#  Comparer les deux au dixième ferait échouer le contrôle sur un chiffre
#  pourtant juste.
ANNONCES = {"daz 2026": (0.6, 1), "renderhub": (43.0, 0)}

POLICES = {
    "titre": (C.POLICE_G, 19, "bold"),
    "sous": (C.POLICE_R, 17, "normal"),
    "bloc": (C.POLICE_G, 15, "bold"),
    "valeur": (C.POLICE_G, 17, "bold"),
    "effectif": (C.POLICE_R, 13, "normal"),
    "abscisse": (C.POLICE_R, 15, "normal"),
    "ordonnee": (C.POLICE_R, 13, "normal"),
}
FAMILLE_SVG = "Liberation Sans, Arial, Helvetica, sans-serif"

TITRE = "GENESIS 8 A QUITTÉ LES NOUVEAUTÉS DE LA BOUTIQUE DAZ"
SOUS = ("part des nouveautés qui ne visent que Genesis 8 ; les deux blocs "
        "ne comptent pas la même chose, mais partagent la même échelle")

HAUT, BAS = 212, 572          # le cadre du tracé
A_X0, A_X1 = 112, 940
B_X0, B_X1 = 1064, 1500
SEPARATION = 1002
PLAFOND = 45.0                # le sommet de l'échelle, en pourcent


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
    for a in ANNEES:
        if a["compte"]:
            n, total = a["compte"]
            a["part"] = 100.0 * n / total
        if a["part"] is None:
            raise SystemExit("%s n'a ni part ni effectif" % a["libelle"])
    for b in BOUTIQUES:
        n, total = b["compte"]
        b["part"] = 100.0 * n / total

    #  La chute doit être monotone : c'est ce que la figure raconte.
    for p, s in zip(ANNEES, ANNEES[1:]):
        if s["part"] >= p["part"]:
            raise SystemExit(
                "la série remonte entre %s (%.2f) et %s (%.2f) : ce n'est "
                "plus une chute" % (p["libelle"], p["part"],
                                    s["libelle"], s["part"]))

    verifications = {"daz 2026": ANNEES[-1]["part"],
                     "renderhub": BOUTIQUES[1]["part"]}
    for cle, (attendu, decimales) in ANNONCES.items():
        trouve = verifications[cle]
        if abs(round(trouve, decimales) - attendu) > 1e-9:
            raise SystemExit(
                "l'article annonce %.*f %% pour « %s », le calcul donne "
                "%.2f %%" % (decimales, attendu, cle, trouve))

    #  Une échelle commune, sinon les deux blocs ne se comparent pas.
    maxi = max([a["part"] for a in ANNEES] + [b["part"] for b in BOUTIQUES])
    if maxi > PLAFOND:
        raise SystemExit("une valeur (%.1f) dépasse le plafond de l'échelle "
                         "(%.0f)" % (maxi, PLAFOND))

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

    #  ------------------------------------------------------------  grille
    grille, graduations = [], []
    for p in range(0, int(PLAFOND) + 1, 10):
        gy = ordonnee(p)
        grille.append(trait("grille", [MARGE + 12, gy, L - MARGE, gy],
                            D.FILET, 1))
        graduations.append(texte("grille", (MARGE + 4, gy - 8),
                                 "%d %%" % p, "ordonnee", D.FAIBLE))
    o.extend(grille)
    o.extend(graduations)

    #  La ligne qui sépare les deux populations : sans elle, on croirait
    #  lire une seule série de sept colonnes.
    o.append(trait("grille", [SEPARATION, HAUT - 68, SEPARATION, BAS + 44],
                   (206, 210, 220), 2))

    #  -----------------------------------------------------------  entêtes
    entetes = []
    for x0, x1, t in ((A_X0, A_X1, TITRE_A), (B_X0, B_X1, TITRE_B)):
        lignes = mesure.couper(D.typo(t), fontes["bloc"], x1 - x0)
        if len(lignes) > 2:
            raise SystemExit("l'intitulé « %s » tient en %d lignes"
                             % (t, len(lignes)))
        yy = HAUT - 70 - (len(lignes) - 1) * 20
        for ligne in lignes:
            entetes.append(texte("entêtes", (x0, yy), ligne, "bloc", D.GRIS))
            yy += 20
    o.extend(entetes)

    #  ---------------------------------------------------------  colonnes
    barres, valeurs, abscisses = [], [], []
    hauts_etiquettes = []

    def poser(x0, x1, series, teinte_defaut):
        n = len(series)
        pas = (x1 - x0) / float(n)
        largeur = min(pas * 0.56, 96)
        for i, s in enumerate(series):
            cx = x0 + (i + 0.5) * pas
            hy = ordonnee(s["part"])
            teinte = s.get("teinte", teinte_defaut)
            #  Une valeur quasi nulle doit rester visible : sans ce
            #  minimum, 0,56 % donnerait une colonne de quatre pixels
            #  qu'on prendrait pour une absence de données.
            hauteur = max(BAS - hy, 4)
            barres.append(rect("colonnes",
                               [cx - largeur / 2.0, BAS - hauteur,
                                cx + largeur / 2.0, BAS], 4, teinte))
            #  Les étiquettes SURMONTENT la colonne, empilées de bas en
            #  haut : l'effectif juste au-dessus d'elle, le pourcentage
            #  au-dessus de l'effectif. Posées à une distance fixe du
            #  sommet sans tenir compte de leur nombre, elles
            #  chevauchaient les colonnes courtes et le haut des hautes.
            sommet = BAS - hauteur
            hy_valeur = sommet - (48 if s["compte"] else 26)
            if s["compte"]:
                valeurs.append(texte("valeurs", (cx, sommet - 26),
                                     "%d sur %s" % (s["compte"][0],
                                                    "{:,}".format(
                                                        s["compte"][1])
                                                    .replace(",", " ")),
                                     "effectif", D.FAIBLE, centre=True))
            valeurs.append(texte("valeurs", (cx, hy_valeur),
                                 pourcent(s["part"]), "valeur", teinte,
                                 centre=True))
            hauts_etiquettes.append((s["libelle"], hy_valeur))
            abscisses.append(texte("abscisses", (cx, BAS + 14),
                                   D.typo(s["libelle"]), "abscisse",
                                   D.ENCRE if s.get("teinte") else D.GRIS,
                                   centre=True))

    poser(A_X0, A_X1, ANNEES, INDIGO_PALE)
    poser(B_X0, B_X1, BOUTIQUES, INDIGO)

    #  Aucune étiquette ne doit remonter jusque dans l'intitulé de son
    #  bloc : c'est le seul chevauchement que cette mise en page permet.
    plancher_entete = HAUT - 70 + 22
    for nom, hy in hauts_etiquettes:
        if hy < plancher_entete:
            raise SystemExit(
                "l'étiquette de « %s » remonte à %d alors que l'intitulé de "
                "bloc descend à %d" % (nom, hy, plancher_entete))

    o.append(trait("grille", [MARGE + 12, BAS, L - MARGE, BAS],
                   (170, 174, 186), 2))
    o.extend(barres)
    o.extend(valeurs)
    o.extend(abscisses)

    H = int(BAS + 72)
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
                        "genesis-boutiques-nouveautes")
    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5),
               ("indigo", INDIGO, 4.5), ("ambre", AMBRE, 4.5))

    H, ordres = composer()
    rendre_matriciel(H, ordres, base)
    couches, textes = rendre_svg(H, ordres, base)

    print("  %-42s %.0f Ko"
          % (os.path.basename(base + ".svg"),
             os.path.getsize(base + ".svg") / 1024.0))
    print("  %d x %d, %d calques, %d textes" % (L, H, couches, textes))
    print()
    for a in ANNEES:
        print("  %-10s %6s%s" % (a["libelle"], pourcent(a["part"]),
                                 "   (%d sur %d)" % a["compte"]
                                 if a["compte"] else ""))
    print()
    for b in BOUTIQUES:
        print("  %-14s %6s   (%d sur %d)"
              % (b["libelle"], pourcent(b["part"]), *b["compte"]))
    print()
    print("  écart entre boutiques, base commune : x%.0f"
          % (BOUTIQUES[1]["part"] / BOUTIQUES[0]["part"]))


if __name__ == "__main__":
    principal()
