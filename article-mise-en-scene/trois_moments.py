"""
Les trois moments où l'image d'un film se décide.

    python3 article-mise-en-scene/trois_moments.py

Produit `mise-en-scene-trois-moments.webp`, son PNG et le SVG éditable.

----------------------------------------------------------------------------
UN AXE, PAS DES CASES
----------------------------------------------------------------------------
Premier jet : trois zones teintées, chacune contenant trois fiches blanches.
Neuf rectangles alignés sur trois colonnes, autrement dit un tableau. Le
brief ne demandait pas un tableau, il demandait une FRISE, et la différence
n'est pas cosmétique : un tableau classe, une frise situe dans le temps.

La figure est donc réduite à trois traits. Un axe horizontal, trois branches
qui en descendent, neuf points accrochés dessus. Plus un seul cadre, plus un
seul aplat de fond. Le temps est porté par l'axe, dont les trois segments
foncent en avançant, et par rien d'autre.

----------------------------------------------------------------------------
CHAQUE NOM PORTE SA SOURCE, EN SIX MOTS
----------------------------------------------------------------------------
La légende de l'article promet que chaque cinéaste est placé « d'après ses
déclarations ou celles de ses collaborateurs ». Une figure qui alignerait
neuf noms sans rien d'autre ferait de ce classement une opinion. Chacun
porte donc la phrase qui le place, ramenée à une ligne : « ne tourne pas de
couverture » pour Bong, « improviser, c'est écrire » pour Pialat.

Un contrôle refuse de dessiner si un nom arrive sans sa justification.

----------------------------------------------------------------------------
PAS DE PIED DE PAGE
----------------------------------------------------------------------------
Les figures précédentes portaient trois paragraphes de notes sous le dessin.
C'étaient mes notes de fabrication, et leur place est ici, dans ce fichier,
ou dans la légende que le site pose autour de l'image. Une image à la une
se regarde ; elle ne se lit pas.
"""

import os

import charte as C
import dessin as D

L = 1600
MARGE = 56

INDIGO = C.VIOLET_TEXTE
INDIGO_APLAT = C.VIOLET

#  ---------------------------------------------------------------------------
#  LES TROIS FAMILLES
#
#  `fond` fonce d'une zone à l'autre : c'est la seule chose qui porte le
#  temps, et elle se lit sans être lue.
#  ---------------------------------------------------------------------------
FAMILLES = (
    {"verbe": "PRÉVOIR", "moment": "avant le tournage",
     "cineastes": (
         ("Alfred Hitchcock",
          "« tout a déjà été fait pendant l’élaboration du scénario »"),
         ("Bong Joon-ho",
          "« Bong ne tourne pas de couverture », dit son monteur"),
         ("George Miller",
          "3 500 vignettes alignées sur un mur, neuf mois durant"),
     )},
    {"verbe": "PROVOQUER", "moment": "pendant le tournage",
     "cineastes": (
         ("Mike Leigh",
          "six mois de répétitions, aucun scénario au départ"),
         ("Maurice Pialat",
          "« improviser, c’est écrire »"),
         ("Abdellatif Kechiche",
          "plus de cent prises pour trente secondes"),
     )},
    {"verbe": "RÉCOLTER", "moment": "au montage",
     "cineastes": (
         ("Stanley Kubrick",
          "au moins deux prises parfaites par scène"),
         ("David Fincher",
          "la caméra comme « récolte de performances »"),
         ("Ridley Scott",
          "jusqu’à onze caméras, l’angle se choisit après"),
     )},
)

POLICES = {
    "titre": (C.POLICE_G, 19, "bold"),
    "sous": (C.POLICE_R, 17, "normal"),
    "verbe": (C.POLICE_G, 25, "bold"),
    "moment": (C.POLICE_R, 15, "normal"),
    "nom": (C.POLICE_G, 19, "bold"),
    "source": (C.POLICE_R, 15, "normal"),
}
FAMILLE_SVG = "Liberation Sans, Arial, Helvetica, sans-serif"

TITRE = "PRÉVOIR, PROVOQUER, RÉCOLTER"
SOUS = ("le moment où l’image se décide, et les neuf cinéastes de l’article "
        "placés d’après leurs déclarations ou celles de leurs collaborateurs")

AXE_Y = 214
AXE_X0, AXE_X1 = 90, L - 90
Y_PREMIER = 302        # la première entrée sous l'axe
PAS_ENTREE = 104       # ce qui les sépare

#  Les trois segments de l'axe foncent en avançant : c'est le seul endroit
#  où le temps est dessiné.
TEINTES_AXE = ((176, 156, 232), (140, 98, 224), (98, 44, 200))


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


def composer():
    mesure = D.Toile(L, 10)
    fontes = {k: mesure.police(f, t) for k, (f, t, _) in POLICES.items()}

    #  ------------------------------------------------------------------
    #  CONTRÔLES
    #  ------------------------------------------------------------------
    total = sum(len(f["cineastes"]) for f in FAMILLES)
    if len(FAMILLES) != 3 or total != 9:
        raise SystemExit(
            "le brief demande trois familles et neuf cinéastes, la table en "
            "porte %d et %d" % (len(FAMILLES), total))
    for f in FAMILLES:
        if len(f["cineastes"]) != 3:
            raise SystemExit("la famille %s compte %d cinéastes au lieu de 3"
                             % (f["verbe"], len(f["cineastes"])))
        for nom, source in f["cineastes"]:
            if not source.strip():
                raise SystemExit(
                    "%s est placé sans la phrase qui le place : le classement "
                    "deviendrait une opinion" % nom)
    #  L'axe doit vraiment foncer, sinon la progression ne se voit pas.
    clartes = [sum(t) for t in TEINTES_AXE]
    if not (clartes[0] > clartes[1] > clartes[2]):
        raise SystemExit("les trois segments d'axe ne vont pas du plus clair "
                         "au plus foncé : la suite dans le temps ne se lit "
                         "plus")

    largeur = (AXE_X1 - AXE_X0) / float(len(FAMILLES))

    o = []
    o.append(texte("titre", (MARGE, 46), TITRE, "titre", D.ENCRE, 2.2))
    sous = D.typo(SOUS)
    if mesure.mesure(sous, fontes["sous"]) > L - 2 * MARGE:
        raise SystemExit("le sous-titre déborde")
    o.append(texte("titre", (MARGE, 74), sous, "sous", D.FAIBLE))

    axe, branches, textes_ = [], [], []
    for i, f in enumerate(FAMILLES):
        x0 = AXE_X0 + i * largeur
        x1 = x0 + largeur
        teinte_axe = TEINTES_AXE[i]

        #  Le segment d'axe, et la graduation qui le ferme.
        axe.append(trait("axe", [x0, AXE_Y, x1 - 10, AXE_Y], teinte_axe, 5))
        axe.append(trait("axe", [x0, AXE_Y - 9, x0, AXE_Y + 9], teinte_axe, 3))

        textes_.append(texte("axe", (x0, AXE_Y - 62), f["verbe"], "verbe",
                             INDIGO, 1.4))
        textes_.append(texte("axe", (x0, AXE_Y - 28), f["moment"], "moment",
                             D.GRIS))

        #  La branche qui descend, et les points accrochés dessus.
        tige = x0 + 14
        dernier = Y_PREMIER + (len(f["cineastes"]) - 1) * PAS_ENTREE
        branches.append(trait("branches", [tige, AXE_Y, tige, dernier],
                              teinte_axe, 2))

        for j, (nom, source) in enumerate(f["cineastes"]):
            y = Y_PREMIER + j * PAS_ENTREE
            branches.append(disque("branches", tige, y, 6, teinte_axe))
            textes_.append(texte("entrées", (tige + 22, y - 11), nom, "nom",
                                 D.ENCRE))
            lignes = mesure.couper(D.typo(source), fontes["source"],
                                   largeur - 48)
            if len(lignes) > 2:
                raise SystemExit("la source de %s tient en %d lignes"
                                 % (nom, len(lignes)))
            for k, ligne in enumerate(lignes):
                textes_.append(texte("entrées", (tige + 22, y + 16 + k * 21),
                                     ligne, "source", D.GRIS))

    o.extend(axe)
    o.extend(branches)
    o.extend(textes_)

    bas = Y_PREMIER + (max(len(f["cineastes"]) for f in FAMILLES) - 1) \
        * PAS_ENTREE
    H = int(bas + 92)
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
                        "mise-en-scene-trois-moments")
    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5),
               ("indigo", INDIGO, 4.5))

    H, ordres = composer()
    rendre_matriciel(H, ordres, base)
    couches, textes = rendre_svg(H, ordres, base)

    print("  %-40s %.0f Ko"
          % (os.path.basename(base + ".svg"),
             os.path.getsize(base + ".svg") / 1024.0))
    print("  %d calques, %d textes" % (couches, textes))
    print()
    for f in FAMILLES:
        print("  %-10s %-20s %s"
              % (f["verbe"], f["moment"],
                 ", ".join(n for n, _ in f["cineastes"])))


if __name__ == "__main__":
    principal()
