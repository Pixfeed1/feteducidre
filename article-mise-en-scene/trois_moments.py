"""
Les trois moments où l'image d'un film se décide.

    python3 article-mise-en-scene/trois_moments.py

Produit `mise-en-scene-trois-moments.webp`, son PNG et le SVG éditable.

----------------------------------------------------------------------------
CE QUI EST DESSINÉ EST UNE SUITE DANS LE TEMPS
----------------------------------------------------------------------------
Trois zones de gauche à droite, le scénario puis le plateau puis la salle de
montage, et les neuf cinéastes posés dans celle qui leur revient. Le fond de
chaque zone fonce d'un cran en avançant : la progression se lit avant les
mots, et elle dit la seule chose que la figure a à dire, à savoir que ces
méthodes ne diffèrent pas par le talent mais par le MOMENT.

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
     "fond": (246, 243, 253),
     "cineastes": (
         ("Alfred Hitchcock",
          "« tout a déjà été fait pendant l’élaboration du scénario »"),
         ("Bong Joon-ho",
          "« Bong ne tourne pas de couverture », dit son monteur"),
         ("George Miller",
          "3 500 vignettes alignées sur un mur, neuf mois durant"),
     )},
    {"verbe": "PROVOQUER", "moment": "pendant le tournage",
     "fond": (238, 231, 251),
     "cineastes": (
         ("Mike Leigh",
          "six mois de répétitions, aucun scénario au départ"),
         ("Maurice Pialat",
          "« improviser, c’est écrire »"),
         ("Abdellatif Kechiche",
          "plus de cent prises pour trente secondes"),
     )},
    {"verbe": "RÉCOLTER", "moment": "au montage",
     "fond": (228, 218, 248),
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

ECART = 36
Y_ZONE = 168
HAUTEUR_FICHE = 100
ECART_FICHE = 12


def rect(couche, b, r, teinte):
    return {"quoi": "rect", "couche": couche, "b": b, "r": r, "t": teinte}


def polygone(couche, points, teinte):
    return {"quoi": "polygone", "couche": couche, "pts": points, "t": teinte}


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
    #  Le fond doit vraiment foncer, sinon la progression ne se voit pas.
    clartes = [sum(f["fond"]) for f in FAMILLES]
    if not (clartes[0] > clartes[1] > clartes[2]):
        raise SystemExit("les trois fonds ne vont pas du plus clair au plus "
                         "foncé : la suite dans le temps ne se lit plus")

    largeur = (L - 2 * MARGE - (len(FAMILLES) - 1) * ECART) / float(
        len(FAMILLES))
    hauteur = 96 + 3 * HAUTEUR_FICHE + 2 * ECART_FICHE + 22

    o = []
    o.append(texte("titre", (MARGE, 46), TITRE, "titre", D.ENCRE, 2.2))
    sous = D.typo(SOUS)
    if mesure.mesure(sous, fontes["sous"]) > L - 2 * MARGE:
        raise SystemExit("le sous-titre déborde")
    o.append(texte("titre", (MARGE, 74), sous, "sous", D.FAIBLE))

    zones, fiches, textes_ = [], [], []
    for i, f in enumerate(FAMILLES):
        x0 = MARGE + i * (largeur + ECART)
        x1 = x0 + largeur

        zones.append(rect("zones", [x0, Y_ZONE, x1, Y_ZONE + hauteur], 14,
                          f["fond"]))
        zones.append(rect("zones", [x0, Y_ZONE, x1, Y_ZONE + 6], 3,
                          INDIGO_APLAT))

        textes_.append(texte("zones", (x0 + 24, Y_ZONE + 28), f["verbe"],
                             "verbe", INDIGO, 1.4))
        textes_.append(texte("zones", (x0 + 24, Y_ZONE + 64), f["moment"],
                             "moment", D.GRIS))

        y = Y_ZONE + 96
        for nom, source in f["cineastes"]:
            fiches.append(rect("fiches", [x0 + 16, y, x1 - 16,
                                          y + HAUTEUR_FICHE], 10, D.BLANC))
            textes_.append(texte("fiches", (x0 + 34, y + 20), nom, "nom",
                                 D.ENCRE))
            lignes = mesure.couper(D.typo(source), fontes["source"],
                                   largeur - 68)
            if len(lignes) > 2:
                raise SystemExit("la source de %s tient en %d lignes"
                                 % (nom, len(lignes)))
            for j, ligne in enumerate(lignes):
                textes_.append(texte("fiches", (x0 + 34, y + 50 + j * 21),
                                     ligne, "source", D.GRIS))
            y += HAUTEUR_FICHE + ECART_FICHE

        #  Le chevron qui dit le sens de lecture, et rien d'autre.
        if i + 1 < len(FAMILLES):
            cx, cy = x1 + ECART / 2.0, Y_ZONE + hauteur / 2.0
            zones.append(polygone("zones", [(cx - 6, cy - 13),
                                            (cx + 7, cy),
                                            (cx - 6, cy + 13)],
                                  (206, 193, 240)))

    o.extend(zones)
    o.extend(fiches)
    o.extend(textes_)

    H = int(Y_ZONE + hauteur + 46)
    o.insert(0, rect("fond", [0, 0, L, H], 0, D.PAPIER))
    return H, o


def rendre_matriciel(H, ordres, base):
    t = D.Toile(L, H)
    fontes = {k: t.police(f, taille) for k, (f, taille, _) in POLICES.items()}
    for a in ordres:
        if a["quoi"] == "rect":
            t.rrect(a["b"], a["r"], teinte=a["t"])
        elif a["quoi"] == "polygone":
            t.polygone(a["pts"], a["t"])
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
            elif a["quoi"] == "polygone":
                out.append('    <polygon points="%s" fill="%s"/>'
                           % (" ".join("%g,%g" % p for p in a["pts"]),
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
