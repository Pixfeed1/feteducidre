"""
Dix numéros publics, deux annuaires inversés, vingt réponses.

    python3 article-ctqui/test_annuaire_inverse.py

Produit `ctqui-test-annuaire-inverse.webp`, son PNG et le SVG éditable.

----------------------------------------------------------------------------
LES DIX LIGNES VIENNENT DE L'ARTICLE, PAS D'UNE INVENTION
----------------------------------------------------------------------------
L'article ne donne pas la liste des dix numéros, il en donne la
composition : « deux institutions, une mairie, une pharmacie, le
dépannage d'Enedis, quatre artisans et un démarcheur signalé ». Puis les
résultats : zéro pour Ctqui, huit pour le 118712.fr, qui « retrouve
l'Élysée, l'Assemblée, la mairie, la pharmacie, Enedis et l'artisan
joint sur son fixe » et « deux portables d'artisans sur trois ».

Les quatre artisans se répartissent donc en un fixe et trois portables,
et les deux seuls échecs sont un de ces portables et le démarcheur. Le
tableau est entièrement déterminé, et un contrôle le recompose à chaque
dessin : si un chiffre de l'article bougeait, le dessin s'arrêterait.

Aucun numéro n'est affiché. L'article n'en cite qu'un, celui de
l'Élysée, et inventer les neuf autres pour faire joli serait inventer.

----------------------------------------------------------------------------
ROUGE ET VERT, ET C'EST ICI QU'ILS SERVENT
----------------------------------------------------------------------------
La charte réserve l'alerte et le vert aux figures qui opposent un état
sain à un état dégradé. Une recherche qui aboutit contre une recherche
qui échoue est exactement ce cas, et c'est tout le contenu de la figure.

Le trouvé est un disque plein, le non-trouvé un anneau creux : l'absence
se lit comme une absence, et la colonne de Ctqui n'est pas un mur de
rouge plein.

----------------------------------------------------------------------------
L'ORDRE DES LIGNES EST L'ARGUMENT
----------------------------------------------------------------------------
Fixes d'abord, portables ensuite, démarchage en dernier. La colonne du
118712.fr descend alors de six réussites à deux échecs, et la figure
montre sans l'écrire ce que l'article dit après : ses deux seuls ratés
sont justement les appels qu'on voudrait le plus identifier.
"""

import os

import charte as C
import dessin as D

L = 1600
MARGE = 56

VERT = C.VERT
ALERTE = C.ALERTE

#  ---------------------------------------------------------------------------
#  LES DIX NUMÉROS
#
#  `genre` sert aux contrôles de composition, `ctqui` et `cent18` portent
#  le résultat de chaque service. `groupe` ouvre une nouvelle bande.
#  ---------------------------------------------------------------------------
LIGNES = (
    {"groupe": "Fixes d’institutions, de services et de professionnels"},
    {"nom": "Standard de l’Élysée", "genre": "institution",
     "ctqui": False, "cent18": True},
    {"nom": "Standard de l’Assemblée nationale", "genre": "institution",
     "ctqui": False, "cent18": True},
    {"nom": "Mairie", "genre": "mairie",
     "ctqui": False, "cent18": True},
    {"nom": "Pharmacie", "genre": "pharmacie",
     "ctqui": False, "cent18": True},
    {"nom": "Enedis, dépannage", "genre": "enedis",
     "ctqui": False, "cent18": True},
    {"nom": "Artisan, ligne fixe", "genre": "artisan fixe",
     "ctqui": False, "cent18": True},

    {"groupe": "Portables d’artisans, inscrits ou non comme professionnels"},
    {"nom": "Artisan, portable", "genre": "artisan portable",
     "ctqui": False, "cent18": True},
    {"nom": "Artisan, portable", "genre": "artisan portable",
     "ctqui": False, "cent18": True},
    {"nom": "Artisan, portable", "genre": "artisan portable",
     "ctqui": False, "cent18": False},

    {"groupe": "Numéro réservé aux automates d’appel"},
    {"nom": "Démarchage, préfixe 09 48", "genre": "demarcheur",
     "ctqui": False, "cent18": False},
)

SERVICES = (
    {"cle": "ctqui", "nom": "Ctqui", "x": 1160},
    {"cle": "cent18", "nom": "118712.fr", "x": 1440},
)

#  Ce que l'article annonce, et que la figure doit retrouver seule.
ANNONCES = {"numéros testés": 10, "trouvés par Ctqui": 0,
            "trouvés par le 118712.fr": 8}
COMPOSITION = {"institution": 2, "mairie": 1, "pharmacie": 1, "enedis": 1,
               "artisan fixe": 1, "artisan portable": 3, "demarcheur": 1}

POLICES = {
    "titre": (C.POLICE_G, 19, "bold"),
    "sous": (C.POLICE_R, 17, "normal"),
    "service": (C.POLICE_G, 19, "bold"),
    "score": (C.POLICE_G, 26, "bold"),
    "groupe": (C.POLICE_G, 14, "bold"),
    "ligne": (C.POLICE_R, 17, "normal"),
    "note": (C.POLICE_R, 14, "normal"),
}
FAMILLE_SVG = "Liberation Sans, Arial, Helvetica, sans-serif"

TITRE = "DIX NUMÉROS PUBLICS, ZÉRO RÉPONSE CHEZ CTQUI"
SOUS = ("recherche gratuite des deux services, le 21 octobre 2026, sur les "
        "mêmes dix numéros")
NOTE = ("Les deux seuls échecs du 118712.fr sont un portable non inscrit et "
        "un numéro réservé au démarchage.")

Y_SERVICE = 128
Y0 = 236                  # première ligne de numéro
H_LIGNE = 42
H_GROUPE = 40
X_NOM = MARGE
R_MARQUE = 12


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


def marque(couche, cx, cy, trouve):
    """Disque plein et coche quand c'est trouvé, anneau creux et croix sinon."""
    r = R_MARQUE
    if trouve:
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

    numeros = [li for li in LIGNES if "nom" in li]

    #  ------------------------------------------------------------------
    #  CONTRÔLES
    #  ------------------------------------------------------------------
    trouve = {"numéros testés": len(numeros),
              "trouvés par Ctqui": sum(1 for n in numeros if n["ctqui"]),
              "trouvés par le 118712.fr": sum(1 for n in numeros
                                              if n["cent18"])}
    for quoi, attendu in ANNONCES.items():
        if trouve[quoi] != attendu:
            raise SystemExit("l'article annonce %d %s, la figure en compte %d"
                             % (attendu, quoi, trouve[quoi]))

    compte = {}
    for n in numeros:
        compte[n["genre"]] = compte.get(n["genre"], 0) + 1
    if compte != COMPOSITION:
        raise SystemExit("la composition du test ne correspond plus à "
                         "l'article : %s au lieu de %s"
                         % (compte, COMPOSITION))

    #  L'article nomme ses deux échecs : un portable d'artisan et le
    #  démarcheur. Si un autre genre venait s'y glisser, la légende et la
    #  phrase qui suit la figure seraient fausses.
    echecs = sorted(n["genre"] for n in numeros if not n["cent18"])
    if echecs != ["artisan portable", "demarcheur"]:
        raise SystemExit("les échecs du 118712.fr sont %s, l'article dit un "
                         "portable d'artisan et un démarcheur" % echecs)

    o = []
    o.append(texte("titre", (MARGE, 46), D.typo(TITRE), "titre", D.ENCRE,
                   2.2))
    sous = D.typo(SOUS)
    if mesure.mesure(sous, fontes["sous"]) > L - 2 * MARGE:
        raise SystemExit("le sous-titre déborde")
    o.append(texte("titre", (MARGE, 74), sous, "sous", D.FAIBLE))

    #  --------------------------------------------------  en-tête des colonnes
    entetes = []
    for s in SERVICES:
        score = trouve["trouvés par %s"
                       % ("Ctqui" if s["cle"] == "ctqui" else "le 118712.fr")]
        teinte = VERT if score else ALERTE
        entetes.append(texte("entetes", (s["x"], Y_SERVICE), D.typo(s["nom"]),
                             "service", D.ENCRE, centre=True))
        entetes.append(texte("entetes", (s["x"], Y_SERVICE + 28),
                             "%d sur %d" % (score, len(numeros)), "score",
                             teinte, centre=True))
    o.extend(entetes)

    #  -----------------------------------------------------------  les lignes
    bandes, marques, libelles = [], [], []
    y = Y0
    for li in LIGNES:
        if "groupe" in li:
            g = D.typo(li["groupe"])
            bandes.append(trait("bandes", [MARGE, y + 2, L - MARGE, y + 2],
                                D.FILET, 1))
            bandes.append(texte("bandes", (X_NOM, y + 10), g, "groupe",
                                C.VIOLET_TEXTE))
            if mesure.mesure(g, fontes["groupe"]) > L - 2 * MARGE:
                raise SystemExit("« %s » déborde" % g)
            y += H_GROUPE
            continue

        nom = D.typo(li["nom"])
        libelles.append(texte("lignes", (X_NOM, y), nom, "ligne", D.ENCRE))
        bout = X_NOM + mesure.mesure(nom, fontes["ligne"])
        limite = SERVICES[0]["x"] - R_MARQUE - 40
        if bout > limite:
            raise SystemExit("« %s » finit à %d px et la première colonne "
                             "commence à %d" % (nom, bout, limite))

        depart = bout + 16
        arrivee = SERVICES[0]["x"] - R_MARQUE - 16
        if arrivee - depart > 40:
            bandes.append(trait("bandes",
                                [depart, y + 10, arrivee, y + 10],
                                D.FILET, 1, tirets=(3, 7)))

        for s in SERVICES:
            marques.extend(marque("marques", s["x"], y + 9, li[s["cle"]]))
        y += H_LIGNE

    o.extend(bandes)
    o.extend(marques)
    o.extend(libelles)

    note = D.typo(NOTE)
    if mesure.mesure(note, fontes["note"]) > L - 2 * MARGE:
        raise SystemExit("la note déborde")
    o.append(texte("note", (MARGE, y + 20), note, "note", D.FAIBLE))

    H = int(y + 72)
    o.insert(0, rect("fond", [0, 0, L, H], 0, D.PAPIER))
    return H, o, trouve


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
                t.pointilles([(x0, y0), (x1, y1)], a["t"], a["e"],
                             plein, vide)
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
                        "ctqui-test-annuaire-inverse")
    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5),
               ("indigo", C.VIOLET_TEXTE, 4.5),
               ("alerte", ALERTE, 4.5), ("vert", VERT, 4.5))
    r = C.contraste(D.BLANC, VERT)
    print("  %-8s %-16s %.2f:1  %s"
          % ("blanc", str(VERT), r, "ok" if r >= 4.5 else "INSUFFISANT"))
    if r < 4.5:
        raise SystemExit("la coche blanche sur le vert : %.2f:1" % r)

    H, ordres, trouve = composer()
    rendre_matriciel(H, ordres, base)
    couches, textes = rendre_svg(H, ordres, base)

    print()
    print("  %-38s %.0f Ko"
          % (os.path.basename(base + ".svg"),
             os.path.getsize(base + ".svg") / 1024.0))
    print("  %d x %d, %d calques, %d textes" % (L, H, couches, textes))
    print()
    for li in LIGNES:
        if "groupe" in li:
            print("  %s" % li["groupe"])
            continue
        print("    %-36s Ctqui %s    118712.fr %s"
              % (li["nom"], "oui" if li["ctqui"] else "non",
                 "oui" if li["cent18"] else "non"))
    print()
    for quoi, n in trouve.items():
        print("  %-28s %d" % (quoi, n))


if __name__ == "__main__":
    principal()
