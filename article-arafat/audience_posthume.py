"""
Ce que le compteur de DJ Arafat a gagné depuis sa mort.

    python3 article-arafat/audience_posthume.py

Produit `dj-arafat-audience-posthume.webp`, son PNG et le SVG éditable.

----------------------------------------------------------------------------
UNE SEULE SÉRIE, PARCE QU'IL N'Y EN A QU'UNE
----------------------------------------------------------------------------
Le brief demandait trois plateformes de janvier 2023 à août 2024.
L'article ne donne deux valeurs datées que pour une seule : les vues
YouTube, 260 millions début 2023 et 305 millions à l'été 2024.

Spotify n'a qu'un chiffre, sans date, et Boomplay aucun. Tracer trois
courbes aurait voulu dire en inventer deux, dans une figure dont tout
l'intérêt est de montrer qu'un mort continue d'être écouté.

Les deux valeurs isolées sont donc posées comme des repères, pas comme
des séries : un point n'a pas de pente.

----------------------------------------------------------------------------
LE CHIFFRE QUI MANQUAIT À L'ARTICLE
----------------------------------------------------------------------------
« De 260 à 305 millions » est juste, mais ne parle pas : l'écart se perd
dans l'ordre de grandeur. Rapporté au temps écoulé, il devient
saisissable. Quarante-cinq millions de vues en dix-neuf mois, c'est
environ soixante-dix-huit mille vues par jour, cinq ans après la mort de
l'artiste.

Ce nombre est calculé au dessin, pas recopié, et un contrôle le compare
à la croissance relative affichée.

----------------------------------------------------------------------------
LES BORNES SONT APPROXIMATIVES, ET LA FIGURE LE DIT
----------------------------------------------------------------------------
L'article date ses deux mesures par « début 2023 » et « l'été 2024 », au
mois près et non au jour. La durée retenue, dix-neuf mois, est donc
approchée, et le nombre de vues par jour est arrondi au millier. Donner
« 77 806 vues par jour » afficherait une précision que la source ne
permet pas.
"""

import os

import charte as C
import dessin as D

L = 1600
MARGE = 56

INDIGO = C.VIOLET_TEXTE
INDIGO_PALE = (221, 211, 246)

#  ---------------------------------------------------------------------------
#  LA SEULE SÉRIE DATÉE DE L'ARTICLE, en millions de vues cumulées.
#  ---------------------------------------------------------------------------
DEPART = {"quand": "début 2023", "vues": 260}
ARRIVEE = {"quand": "été 2024", "vues": 305}
MOIS = 19                 # de janvier 2023 à août 2024, au mois près
SOURCE = "d’après sa fondation"

#  Les deux chiffres isolés : un point, pas une série.
REPERES = (
    {"valeur": "1 million", "quoi": "d’abonnés sur sa chaîne YouTube",
     "quand": "janvier 2023"},
    {"valeur": "250 000", "quoi": "auditeurs chaque mois sur Spotify",
     "quand": "chiffre sans date dans l’article"},
)

PLAFOND = 320             # le sommet de l'échelle, en millions

POLICES = {
    "titre": (C.POLICE_G, 19, "bold"),
    "sous": (C.POLICE_R, 17, "normal"),
    "borne": (C.POLICE_G, 17, "bold"),
    "quand": (C.POLICE_R, 14, "normal"),
    "gain": (C.POLICE_G, 20, "bold"),
    "cadence": (C.POLICE_G, 46, "bold"),
    "cadencesous": (C.POLICE_R, 16, "normal"),
    "repere": (C.POLICE_G, 22, "bold"),
    "reperesous": (C.POLICE_R, 15, "normal"),
    "mention": (C.POLICE_R, 13, "normal"),
}
FAMILLE_SVG = "Liberation Sans, Arial, Helvetica, sans-serif"

TITRE = "CINQ ANS APRÈS SA MORT, LE COMPTEUR TOURNE ENCORE"
SOUS = ("vues cumulées des vidéos de DJ Arafat %s, et les deux autres "
        "chiffres que cite l’article" % SOURCE)

X0, X1 = 96, 1180
BARRE_Y, BARRE_H = 252, 46
X_CADENCE = 1246
Y_REPERES = 428


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


def milliers(n):
    return format(int(n), ",d").replace(",", " ")


def composer():
    mesure = D.Toile(L, 10)
    fontes = {k: mesure.police(f, t) for k, (f, t, _) in POLICES.items()}

    #  ------------------------------------------------------------------
    #  CONTRÔLES
    #  ------------------------------------------------------------------
    if ARRIVEE["vues"] <= DEPART["vues"]:
        raise SystemExit("le compteur ne monte pas : la figure n'a rien à "
                         "montrer")
    if ARRIVEE["vues"] > PLAFOND:
        raise SystemExit("la valeur d'arrivée dépasse l'échelle")

    gain = ARRIVEE["vues"] - DEPART["vues"]
    croissance = 100.0 * gain / DEPART["vues"]
    par_jour = gain * 1e6 / (MOIS * 30.44)

    #  Les deux nombres dérivés doivent rester cohérents entre eux : si
    #  l'un bougeait sans l'autre, la figure se contredirait.
    verif = par_jour * MOIS * 30.44 / 1e6
    if abs(verif - gain) > 0.5:
        raise SystemExit("la cadence et le gain ne concordent plus")

    #  La source date au mois : arrondir au millier, pas à l'unité.
    cadence = round(par_jour / 1000.0) * 1000
    if cadence <= 0:
        raise SystemExit("la cadence arrondie tombe à zéro")

    echelle = (X1 - X0) / float(PLAFOND)

    o = []
    o.append(texte("titre", (MARGE, 46), TITRE, "titre", D.ENCRE, 2.2))
    sous = D.typo(SOUS)
    if mesure.mesure(sous, fontes["sous"]) > L - 2 * MARGE:
        raise SystemExit("le sous-titre déborde")
    o.append(texte("titre", (MARGE, 74), sous, "sous", D.FAIBLE))

    #  ------------------------------------------------------------  barre
    xd = X0 + DEPART["vues"] * echelle
    xa = X0 + ARRIVEE["vues"] * echelle

    barre = [rect("barre", [X0, BARRE_Y, xd, BARRE_Y + BARRE_H], 8,
                  INDIGO_PALE),
             rect("barre", [xd, BARRE_Y, xa, BARRE_Y + BARRE_H], 8, INDIGO)]
    o.extend(barre)

    #  Les deux bornes, chacune sous son extrémité.
    bornes = []
    for x, d, teinte_b in ((xd, DEPART, D.GRIS), (xa, ARRIVEE, INDIGO)):
        lab = "%d millions" % d["vues"]
        lb = mesure.mesure(lab, fontes["borne"])
        bornes.append(trait("bornes", [x, BARRE_Y - 14, x, BARRE_Y],
                            teinte_b, 2))
        bornes.append(texte("bornes", (x - lb / 2.0, BARRE_Y - 42), lab,
                            "borne", teinte_b))
        lq = mesure.mesure(d["quand"], fontes["quand"])
        bornes.append(texte("bornes", (x - lq / 2.0, BARRE_Y + BARRE_H + 12),
                            d["quand"], "quand", D.FAIBLE))
    o.extend(bornes)

    #  Le gain, écrit dans le segment qui le représente.
    lab_gain = "+ %d millions" % gain
    lg = mesure.mesure(lab_gain, fontes["gain"])
    if lg > xa - xd - 16:
        #  Le segment est trop court : on écrit au-dessus plutôt que de
        #  déborder sur la partie déjà acquise.
        o.append(texte("gain", ((xd + xa) / 2.0 - lg / 2.0,
                                BARRE_Y + BARRE_H + 40), lab_gain, "gain",
                       INDIGO))
    else:
        o.append(texte("gain", ((xd + xa) / 2.0 - lg / 2.0, BARRE_Y + 11),
                       lab_gain, "gain", D.BLANC))

    #  --------------------------------------------------------  la cadence
    o.append(trait("cadence", [X_CADENCE - 28, BARRE_Y - 30,
                               X_CADENCE - 28, BARRE_Y + BARRE_H + 46],
                   D.FILET, 2))
    o.append(texte("cadence", (X_CADENCE, BARRE_Y - 32), milliers(cadence),
                   "cadence", INDIGO))
    o.append(texte("cadence", (X_CADENCE, BARRE_Y + 32),
                   "vues par jour, en moyenne", "cadencesous", D.GRIS))
    o.append(texte("cadence", (X_CADENCE, BARRE_Y + 56),
                   "sur ces %d mois, soit + %.0f %%" % (MOIS, croissance),
                   "cadencesous", D.GRIS))

    #  ---------------------------------------------------------  repères
    o.append(trait("repères", [MARGE, Y_REPERES - 38, L - MARGE,
                               Y_REPERES - 38], D.FILET, 2))
    largeur = (L - 2 * MARGE) / float(len(REPERES))
    bas = 0
    for i, r in enumerate(REPERES):
        x = MARGE + i * largeur
        o.append(texte("repères", (x, Y_REPERES), r["valeur"], "repere",
                       D.ENCRE))
        y = Y_REPERES + 32
        for contenu, police in ((r["quoi"], "reperesous"),
                                (r["quand"], "mention")):
            lignes = mesure.couper(D.typo(contenu), fontes[police],
                                   largeur - 30)
            if len(lignes) > 2:
                raise SystemExit("« %s » tient en %d lignes"
                                 % (contenu, len(lignes)))
            for ligne in lignes:
                o.append(texte("repères", (x, y), ligne, police,
                               D.GRIS if police == "reperesous"
                               else D.FAIBLE))
                y += 22
        bas = max(bas, y)

    H = int(bas + 40)
    o.insert(0, rect("fond", [0, 0, L, H], 0, D.PAPIER))
    return H, o, (gain, croissance, cadence)


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
                        "dj-arafat-audience-posthume")
    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5),
               ("indigo", INDIGO, 4.5))

    H, ordres, (gain, croissance, cadence) = composer()
    rendre_matriciel(H, ordres, base)
    couches, textes = rendre_svg(H, ordres, base)

    print("  %-40s %.0f Ko"
          % (os.path.basename(base + ".svg"),
             os.path.getsize(base + ".svg") / 1024.0))
    print("  %d x %d, %d calques, %d textes" % (L, H, couches, textes))
    print()
    print("  %s  %3d millions" % (DEPART["quand"], DEPART["vues"]))
    print("  %s  %3d millions" % (ARRIVEE["quand"], ARRIVEE["vues"]))
    print("  gain          + %d millions, soit + %.1f %%" % (gain,
                                                             croissance))
    print("  cadence       %s vues par jour sur %d mois"
          % (milliers(cadence), MOIS))


if __name__ == "__main__":
    principal()
