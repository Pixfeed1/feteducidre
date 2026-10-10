"""
Trente ans de FutureSplash à Adobe Animate.

    python3 article-animate/frise_flash.py

Produit `adobe-animate-frise-flash.webp`, son PNG et le SVG éditable.

----------------------------------------------------------------------------
L'AXE EST PROPORTIONNEL, DONC LES JALONS SE BOUSCULENT
----------------------------------------------------------------------------
Les quatre derniers jalons tiennent dans dix ans sur trente. Posés du
même côté de l'axe, leurs libellés se chevaucheraient : octobre 2023 et
février 2026 ne sont séparés que de cent dix pixels.

Chaque jalon porte donc son côté, au-dessus ou au-dessous de l'axe, et
sa profondeur. Deux blocs du même côté et de la même profondeur ne
doivent jamais se croiser, et un contrôle refuse de dessiner sinon.
Espacer les jalons régulièrement aurait réglé le problème en détruisant
la seule chose qu'une frise sait dire.

----------------------------------------------------------------------------
DEUX ÈRES, DEUX TEINTES SUR L'AXE
----------------------------------------------------------------------------
L'axe change de ton en février 2016, quand Flash Professional devient
Adobe Animate. Vingt ans sous le nom de Flash, dix sous celui d'Animate.
C'est la structure même de l'article, et elle se lit sans légende.

----------------------------------------------------------------------------
LA DATE DE L'ANNONCE N'EST PAS DANS L'ARTICLE
----------------------------------------------------------------------------
L'article date le rétablissement au 5 février et dit que la volte-face a
pris deux jours. L'annonce tombe donc vers le 3, mais il ne l'écrit pas.
Le jalon porte « début février 2026 » plutôt qu'une date précise que la
source ne donne pas.

----------------------------------------------------------------------------
LE CHIFFRE QUE L'ARTICLE N'A PAS CALCULÉ
----------------------------------------------------------------------------
Entre la dernière vraie mise à jour et l'annonce d'arrêt, il s'écoule
vingt-huit mois. L'article dit « sa dernière vraie mise à jour datait
d'octobre 2023 » et laisse le lecteur faire la soustraction. La figure
la fait, et un contrôle la recalcule à chaque dessin.
"""

import os

import charte as C
import dessin as D

L = 1600
MARGE = 56

INDIGO = C.VIOLET_TEXTE
INDIGO_PALE = (178, 158, 234)

DEBUT, FIN = 1996.0, 2026.4
BASCULE = 2016.1          # février 2016, Flash Professional devient Animate

#  ---------------------------------------------------------------------------
#  LES SIX JALONS
#
#  `an` est la position sur l'axe, en années décimales. `cote` vaut 1
#  au-dessus de l'axe, -1 au-dessous. `profondeur` écarte deux blocs d'un
#  même côté qui se croiseraient.
#  ---------------------------------------------------------------------------
JALONS = (
    {"an": 1996.0, "cote": 1, "profondeur": 0, "date": "1996",
     "titre": "FutureSplash Animator",
     "detail": "FutureWave le sort. Macromedia le rachète la même année et "
               "le rebaptise Flash."},

    {"an": 2005.0, "cote": -1, "profondeur": 0, "date": "2005",
     "titre": "Adobe rachète Macromedia",
     "detail": "Flash change de maison et devient un produit Adobe."},

    {"an": 2016.1, "cote": 1, "profondeur": 0, "date": "février 2016",
     "titre": "Flash Professional devient Adobe Animate",
     "detail": "Le logiciel se détourne de Flash et vise le HTML5."},

    {"an": 2021.0, "cote": -1, "profondeur": 0, "date": "31 décembre 2020",
     "titre": "Flash Player est débranché",
     "detail": "Les navigateurs bloquent ses contenus dès janvier 2021."},

    {"an": 2023.75, "cote": 1, "profondeur": 1, "date": "octobre 2023",
     "titre": "La dernière vraie mise à jour",
     "detail": "Aucune version 2025 ne sortira, et Animate manque le "
               "dernier Adobe MAX."},

    {"an": 2026.1, "cote": -1, "profondeur": 1,
     "date": "début février 2026",
     "titre": "L’arrêt annoncé, puis annulé",
     "detail": "Deux jours de flottement. Le 5 février, Animate repasse en "
               "vie, en mode maintenance."},
)

#  Ce que l'article affirme, et que le dessin doit continuer de vérifier.
ANNONCES = {"trente ans": (DEBUT, 2026.1, 30),
            "cinq ans après Flash": (2021.0, 2026.1, 5)}
SANS_MAJ = (2023.75, 2026.1)     # d'octobre 2023 à février 2026

POLICES = {
    "titre": (C.POLICE_G, 19, "bold"),
    "sous": (C.POLICE_R, 17, "normal"),
    "ere": (C.POLICE_G, 14, "bold"),
    "date": (C.POLICE_G, 16, "bold"),
    "jalon": (C.POLICE_G, 18, "bold"),
    "detail": (C.POLICE_R, 15, "normal"),
    "annee": (C.POLICE_R, 13, "normal"),
}
FAMILLE_SVG = "Liberation Sans, Arial, Helvetica, sans-serif"

TITRE = "TRENTE ANS, DEUX NOMS, ET DEUX JOURS DE FLOTTEMENT"
SOUS = ("de FutureSplash Animator à Adobe Animate, et l’arrêt annoncé puis "
        "annulé en février 2026")

AXE_Y = 462
PLAFOND = 150             # le bloc le plus haut ne monte pas au-dessus
AXE_X0, AXE_X1 = 104, L - 104
LARGEUR_BLOC = 318
ECART_BRANCHE = 54        # entre l'axe et le premier bloc
PAS_PROFONDEUR = 128


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
    for a, b in zip(JALONS, JALONS[1:]):
        if b["an"] <= a["an"]:
            raise SystemExit("les jalons ne sont pas dans l'ordre : %s puis "
                             "%s" % (a["date"], b["date"]))
    for j in JALONS:
        if not DEBUT <= j["an"] <= FIN:
            raise SystemExit("%s sort de l'axe" % j["date"])

    for nom, (d, f, attendu) in ANNONCES.items():
        trouve = f - d
        if abs(trouve - attendu) > 0.6:
            raise SystemExit(
                "l'article annonce %d ans pour « %s », l'axe en donne %.1f"
                % (attendu, nom, trouve))

    mois_sans_maj = int(round((SANS_MAJ[1] - SANS_MAJ[0]) * 12))
    if not 24 <= mois_sans_maj <= 32:
        raise SystemExit("l'écart sans mise à jour tombe à %d mois, ce n'est "
                         "plus le fait annoncé" % mois_sans_maj)

    etendue = FIN - DEBUT

    def abscisse(an):
        return AXE_X0 + (an - DEBUT) / etendue * (AXE_X1 - AXE_X0)

    o = []
    o.append(texte("titre", (MARGE, 46), TITRE, "titre", D.ENCRE, 2.2))
    sous = D.typo(SOUS)
    if mesure.mesure(sous, fontes["sous"]) > L - 2 * MARGE:
        raise SystemExit("le sous-titre déborde")
    o.append(texte("titre", (MARGE, 74), sous, "sous", D.FAIBLE))

    #  ---------------------------------------------------------------  axe
    xb = abscisse(BASCULE)
    axe = [trait("axe", [AXE_X0 - 12, AXE_Y, xb, AXE_Y], INDIGO_PALE, 6),
           trait("axe", [xb, AXE_Y, AXE_X1 + 12, AXE_Y], INDIGO, 6)]
    #  Une graduation qui tombe sur un jalon se ferait traverser par sa
    #  tige : 2005 est à la fois une décennie et un rachat. On la saute,
    #  le bloc du jalon porte déjà l'année.
    occupe = [abscisse(j["an"]) for j in JALONS]
    an = int(DEBUT)
    while an <= int(FIN):
        gx = abscisse(an)
        if an % 5 == 0 and all(abs(gx - u) > 22 for u in occupe):
            axe.append(trait("axe", [gx, AXE_Y - 9, gx, AXE_Y + 9],
                             D.FILET, 2))
            axe.append(texte("axe", (gx, AXE_Y + 14), str(an), "annee",
                             D.FAIBLE, centre=True))
        an += 1
    o.extend(axe)

    #  Les deux ères, nommées sur leur segment.
    for x0, x1, nom, teinte_e in ((AXE_X0, xb, "l’ère Flash", INDIGO_PALE),
                                  (xb, AXE_X1, "l’ère Animate", INDIGO)):
        o.append(texte("axe", ((x0 + x1) / 2.0, AXE_Y - 34), nom, "ere",
                       teinte_e, centre=True))

    #  ------------------------------------------------------------  jalons
    tiges, blocs, boites = [], [], []
    extremes = [AXE_Y, AXE_Y]

    for j in JALONS:
        x = abscisse(j["an"])
        lignes = mesure.couper(D.typo(j["detail"]), fontes["detail"],
                               LARGEUR_BLOC)
        if len(lignes) > 3:
            raise SystemExit("le détail de « %s » tient en %d lignes"
                             % (j["titre"], len(lignes)))
        hauteur = 22 + 24 + len(lignes) * 22

        #  Le bloc pend à droite de sa tige tant qu'il tient dans le
        #  cadre. Sinon il bascule à gauche d'elle, et son texte se range
        #  sur le bord droit : la tige touche alors le coin du bloc au
        #  lieu de le traverser trois cents pixels plus loin.
        if x + 18 + LARGEUR_BLOC <= L - MARGE:
            gauche, aligne_a_droite = x + 18, False
        else:
            gauche, aligne_a_droite = x - 18 - LARGEUR_BLOC, True
        if gauche < MARGE:
            raise SystemExit("le bloc de « %s » déborde à gauche" % j["date"])
        depart = ECART_BRANCHE + j["profondeur"] * PAS_PROFONDEUR

        if j["cote"] > 0:
            bas_bloc = AXE_Y - depart
            haut = bas_bloc - hauteur
            extremes[0] = min(extremes[0], haut)
        else:
            haut = AXE_Y + depart
            extremes[1] = max(extremes[1], haut + hauteur)

        tiges.append(trait("tiges", [x, AXE_Y, x,
                                     haut + (hauteur if j["cote"] > 0
                                             else 0)], INDIGO, 2))
        tiges.append(disque("tiges", x, AXE_Y, 7, INDIGO))

        def pose(y, contenu, police, teinte):
            gx = (gauche + LARGEUR_BLOC - mesure.mesure(contenu,
                                                        fontes[police])
                  if aligne_a_droite else gauche)
            blocs.append(texte("jalons", (gx, y), contenu, police, teinte))

        y = haut
        pose(y, j["date"], "date", INDIGO)
        y += 24
        pose(y, D.typo(j["titre"]), "jalon", D.ENCRE)
        y += 26
        for ligne in lignes:
            pose(y, ligne, "detail", D.GRIS)
            y += 22

        boites.append({"cote": j["cote"], "prof": j["profondeur"],
                       "g": gauche, "d": gauche + LARGEUR_BLOC,
                       "haut": haut, "bas": haut + hauteur,
                       "x": x, "nom": j["date"]})

    #  Deux blocs du même côté ET de la même profondeur ne doivent pas se
    #  croiser : c'est tout l'intérêt des deux champs.
    for i, a in enumerate(boites):
        for b in boites[i + 1:]:
            if (a["cote"] == b["cote"] and a["prof"] == b["prof"]
                    and a["g"] < b["d"] and b["g"] < a["d"]):
                raise SystemExit(
                    "« %s » et « %s » se chevauchent : changez le côté ou la "
                    "profondeur de l'un des deux" % (a["nom"], b["nom"]))

    #  Et aucune tige ne doit traverser le bloc d'un autre jalon : c'est
    #  le défaut qu'on ne voit qu'une fois l'image tirée.
    for a in boites:
        y0, y1 = ((a["bas"], AXE_Y) if a["cote"] > 0 else (AXE_Y, a["haut"]))
        for b in boites:
            if b is a:
                continue
            if (b["g"] - 6 < a["x"] < b["d"] + 6
                    and y0 < b["bas"] and b["haut"] < y1):
                raise SystemExit(
                    "la tige de « %s » traverse le bloc de « %s »"
                    % (a["nom"], b["nom"]))

    o.extend(tiges)
    o.extend(blocs)

    H = int(extremes[1] + 46)
    decalage = PLAFOND - extremes[0]
    if decalage > 0:
        #  Tout descendre aurait été plus simple en posant l'axe plus bas,
        #  mais la hauteur des blocs n'est connue qu'ici. Le titre, lui,
        #  ne bouge pas : il garde sa place en haut du cadre.
        for a in o:
            if a["couche"] == "titre":
                continue
            if a["quoi"] == "texte":
                a["xy"] = (a["xy"][0], a["xy"][1] + decalage)
            elif a["quoi"] == "trait":
                a["b"] = [a["b"][0], a["b"][1] + decalage,
                          a["b"][2], a["b"][3] + decalage]
            elif a["quoi"] == "disque":
                a["cy"] += decalage
        H += decalage

    o.insert(0, rect("fond", [0, 0, L, H], 0, D.PAPIER))
    return H, o, mois_sans_maj


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
                        "adobe-animate-frise-flash")
    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5),
               ("indigo", INDIGO, 4.5))

    H, ordres, mois = composer()
    rendre_matriciel(H, ordres, base)
    couches, textes = rendre_svg(H, ordres, base)

    print("  %-38s %.0f Ko"
          % (os.path.basename(base + ".svg"),
             os.path.getsize(base + ".svg") / 1024.0))
    print("  %d x %d, %d calques, %d textes" % (L, H, couches, textes))
    print()
    for j in JALONS:
        print("  %-20s %-44s %s"
              % (j["date"], j["titre"],
                 "au-dessus" if j["cote"] > 0 else "au-dessous"))
    print()
    print("  sans vraie mise à jour avant l'annonce : %d mois" % mois)


if __name__ == "__main__":
    principal()
