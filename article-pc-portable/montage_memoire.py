"""
Les trois façons de monter la mémoire d'un portable.

    python3 article-pc-portable/montage_memoire.py

Produit `pc-portable-montage-memoire.webp`, son PNG et le SVG éditable.

----------------------------------------------------------------------------
UN SCHÉMA PLUTÔT QU'UNE PHOTO DE PRESSE
----------------------------------------------------------------------------
Le brief demandait un visuel Framework. Les salles de presse ne sont pas
joignables depuis ici, et reprendre une photo de constructeur dans un
guide qui porte de l'affiliation sort du cadre éditorial que ces
dossiers de presse autorisent.

Surtout, la photo ne répond pas à la question du lecteur. Elle montre un
module posé à côté de son emplacement ; lui veut savoir s'il pourra
augmenter sa mémoire plus tard. Les trois montages répondent, et la
section s'appelle « Soudée un jour, soudée toujours ».

----------------------------------------------------------------------------
ROUGE ET VERT, ET C'EST LE CAS PRÉVU PAR LA CHARTE
----------------------------------------------------------------------------
Les teintes de signalisation sont réservées aux figures qui opposent un
état sain à un état dégradé. C'en est une : d'un côté une quantité fixée
pour toute la vie de la machine, de l'autre une mémoire qu'on remplace.
L'article lui-même traite le premier cas en encadré d'avertissement.

Un contrôle vérifie qu'une seule famille porte le rouge, et que c'est
bien celle qui n'est pas démontable. Le jour où la table changerait sans
que les couleurs suivent, la figure refuse de se dessiner.

----------------------------------------------------------------------------
LES DEUX LIGNES DE TEXTE N'ONT PAS D'INTITULÉ
----------------------------------------------------------------------------
Chaque colonne porte les machines concernées puis ce qu'on peut en
faire. Écrire « Machines » et « Après l'achat » sous les trois colonnes
fabriquerait un tableau. Le gris dit la liste, la couleur dit la
conséquence, et le lecteur comprend sans qu'on le lui épelle.
"""

import os

import charte as C
import dessin as D

L = 1600
MARGE = 56

ROUGE = C.ALERTE
VERT = C.VERT
CARTE = (236, 238, 243)
CARTE_BORD = (198, 203, 214)

#  ---------------------------------------------------------------------------
#  LES TROIS MONTAGES
#
#  `amovible` commande la couleur, et le contrôle vérifie qu'un seul
#  montage ne l'est pas.
#  ---------------------------------------------------------------------------
MONTAGES = (
    {"cle": "soudee", "nom": "Soudée", "amovible": False,
     "machines": "Tous les MacBook, le Zenbook 14 OLED, les Yoga Slim 7 "
                 "et le Dell XPS 14",
     "action": "La quantité choisie à la commande est définitive."},

    {"cle": "sodimm", "nom": "SO-DIMM", "amovible": True,
     "machines": "Acer Aspire Go 15, Acer Nitro V 17 AI, et la version "
                 "AMD du Framework Laptop 13 Pro",
     "action": "Deux barrettes du commerce, à changer pour monter jusqu’à "
               "32 Go."},

    {"cle": "lpcamm2", "nom": "LPCAMM2", "amovible": True,
     "machines": "La version Intel du Framework Laptop 13 Pro",
     "action": "Un module qui se dévisse. Rapide, amovible, mais encore "
               "cher."},
)

POLICES = {
    "titre": (C.POLICE_G, 19, "bold"),
    "sous": (C.POLICE_R, 17, "normal"),
    "nom": (C.POLICE_G, 24, "bold"),
    "machines": (C.POLICE_R, 15, "normal"),
    "action": (C.POLICE_G, 16, "bold"),
    "mention": (C.POLICE_R, 13, "normal"),
}
FAMILLE_SVG = "Liberation Sans, Arial, Helvetica, sans-serif"

TITRE = "CE QUI SE CHANGE APRÈS L’ACHAT, ET CE QUI NE SE CHANGE PAS"
SOUS = ("les trois façons de monter la mémoire d’un portable, et les "
        "machines de ce guide qui les utilisent")

COL_X0, COL_X1 = 72, L - 72
SCHEMA_Y, SCHEMA_H = 164, 182
Y_NOM = 384
Y_MACHINES = 420
MENTION = "vue de dessus, schématique"


def rect(couche, b, r, teinte):
    return {"quoi": "rect", "couche": couche, "b": b, "r": r, "t": teinte}


def cadre(couche, b, r, teinte, epaisseur=2):
    return {"quoi": "cadre", "couche": couche, "b": b, "r": r, "t": teinte,
            "e": epaisseur}


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


def dessiner_schema(cle, x0, y0, l, h, teinte, formes):
    """La carte mère et ce qui porte la mémoire, vus de dessus."""
    formes.append(rect("schémas", [x0, y0, x0 + l, y0 + h], 10, CARTE))
    formes.append(cadre("schémas", [x0, y0, x0 + l, y0 + h], 10,
                        CARTE_BORD, 2))
    cx = x0 + l / 2.0
    cy = y0 + h / 2.0

    if cle == "soudee":
        #  Quatre puces posées à plat sur la carte, sans connecteur.
        pl, ph, ecart = 92, 54, 18
        tl = 2 * pl + ecart
        th = 2 * ph + ecart
        for i in range(2):
            for j in range(2):
                px = cx - tl / 2.0 + i * (pl + ecart)
                py = cy - th / 2.0 + j * (ph + ecart)
                formes.append(rect("schémas", [px, py, px + pl, py + ph],
                                   4, teinte))
                #  Les pattes, qui disent que c'est brasé.
                for k in range(5):
                    bx = px + 12 + k * (pl - 24) / 4.0
                    formes.append(trait("schémas", [bx, py + ph, bx,
                                                    py + ph + 7],
                                        teinte, 2))

    elif cle == "sodimm":
        #  Deux barrettes dans leurs supports, avec leurs clips.
        bl, bh, ecart = 300, 34, 26
        for j in range(2):
            by = cy - (2 * bh + ecart) / 2.0 + j * (bh + ecart)
            bx = cx - bl / 2.0
            formes.append(rect("schémas", [bx, by, bx + bl, by + bh], 5,
                               teinte))
            #  Le détrompeur, cette encoche qui empêche de monter à
            #  l'envers une barrette.
            formes.append(rect("schémas", [bx + bl * 0.62, by + bh - 10,
                                           bx + bl * 0.62 + 7, by + bh],
                               1, CARTE))
            for cxx in (bx - 14, bx + bl + 14):
                formes.append(disque("schémas", cxx, by + bh / 2.0, 7,
                                     CARTE_BORD))

    else:
        #  Un module plat, retenu par quatre vis.
        ml, mh = 330, 104
        mx, my = cx - ml / 2.0, cy - mh / 2.0
        formes.append(rect("schémas", [mx, my, mx + ml, my + mh], 8, teinte))
        for vx in (mx + 18, mx + ml - 18):
            for vy in (my + 18, my + mh - 18):
                formes.append(disque("schémas", vx, vy, 8, CARTE))
                formes.append(disque("schémas", vx, vy, 3, teinte))


def composer():
    mesure = D.Toile(L, 10)
    fontes = {k: mesure.police(f, t) for k, (f, t, _) in POLICES.items()}

    #  ------------------------------------------------------------------
    #  CONTRÔLES
    #  ------------------------------------------------------------------
    if len(MONTAGES) != 3:
        raise SystemExit("la figure annonce trois montages, la table en "
                         "porte %d" % len(MONTAGES))
    fixes = [m for m in MONTAGES if not m["amovible"]]
    if len(fixes) != 1:
        raise SystemExit(
            "un seul montage n'est pas démontable, la table en compte %d : "
            "le rouge de la charte ne saurait plus quoi désigner"
            % len(fixes))
    for m in MONTAGES:
        for cle in ("machines", "action"):
            if not m[cle].strip():
                raise SystemExit("« %s » n'a pas de %s" % (m["nom"], cle))
        m["teinte"] = ROUGE if not m["amovible"] else VERT

    colonne = (COL_X1 - COL_X0) / float(len(MONTAGES))
    largeur = colonne - 56

    o = []
    o.append(texte("titre", (MARGE, 46), TITRE, "titre", D.ENCRE, 2.2))
    sous = D.typo(SOUS)
    if mesure.mesure(sous, fontes["sous"]) > L - 2 * MARGE:
        raise SystemExit("le sous-titre déborde")
    o.append(texte("titre", (MARGE, 74), sous, "sous", D.FAIBLE))

    schemas, noms, textes_c = [], [], []
    bas = 0
    lignes_machines = max(
        len(mesure.couper(D.typo(m["machines"]), fontes["machines"],
                          largeur)) for m in MONTAGES)
    for i, m in enumerate(MONTAGES):
        cx = COL_X0 + (i + 0.5) * colonne
        sl = largeur
        dessiner_schema(m["cle"], cx - sl / 2.0, SCHEMA_Y, sl, SCHEMA_H,
                        m["teinte"], schemas)

        noms.append(texte("noms", (cx, Y_NOM), m["nom"], "nom", m["teinte"],
                          centre=True))

        y = Y_MACHINES
        for contenu, police, teinte_t in ((m["machines"], "machines", D.GRIS),
                                          (m["action"], "action",
                                           m["teinte"])):
            lignes = mesure.couper(D.typo(contenu), fontes[police], largeur)
            if len(lignes) > 3:
                raise SystemExit("« %s » de %s tient en %d lignes"
                                 % (police, m["nom"], len(lignes)))
            for ligne in lignes:
                textes_c.append(texte("colonnes", (cx, y), ligne, police,
                                      teinte_t, centre=True))
                y += 23
            #  La liste de machines est RÉSERVÉE à sa hauteur maximale,
            #  pas seulement à la sienne : sans ça, la colonne qui en
            #  nomme le moins remonte sa conclusion et les trois phrases
            #  qu'on veut comparer ne sont plus sur la même ligne.
            if police == "machines":
                y += (lignes_machines - len(lignes)) * 23 + 14
            else:
                y += 14
        bas = max(bas, y)

    o.extend(schemas)
    o.extend(noms)
    o.extend(textes_c)

    #  Une seule ligne sous le dessin, pour dire que les schémas ne sont
    #  pas à l'échelle. Le reste des notes vit dans ce fichier.
    o.append(texte("mention", (MARGE, bas + 2), MENTION, "mention",
                   D.FAIBLE))

    H = int(bas + 46)
    o.insert(0, rect("fond", [0, 0, L, H], 0, D.PAPIER))
    return H, o


def rendre_matriciel(H, ordres, base):
    t = D.Toile(L, H)
    fontes = {k: t.police(f, taille) for k, (f, taille, _) in POLICES.items()}
    for a in ordres:
        if a["quoi"] == "rect":
            t.rrect(a["b"], a["r"], teinte=a["t"])
        elif a["quoi"] == "cadre":
            t.rrect(a["b"], a["r"], contour=a["t"], epaisseur=a["e"])
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
            if a["quoi"] in ("rect", "cadre"):
                x0, y0, x1, y1 = a["b"]
                if a["quoi"] == "rect":
                    peinture = 'fill="%s"' % teinte(a["t"])
                else:
                    peinture = ('fill="none" stroke="%s" stroke-width="%g"'
                                % (teinte(a["t"]), a["e"]))
                out.append('    <rect x="%g" y="%g" width="%g" height="%g" '
                           'rx="%g" %s/>'
                           % (x0, y0, x1 - x0, y1 - y0, a["r"], peinture))
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
                        "pc-portable-montage-memoire")
    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5),
               ("rouge", ROUGE, 4.5), ("vert", VERT, 4.5))

    H, ordres = composer()
    rendre_matriciel(H, ordres, base)
    couches, textes = rendre_svg(H, ordres, base)

    print("  %-40s %.0f Ko"
          % (os.path.basename(base + ".svg"),
             os.path.getsize(base + ".svg") / 1024.0))
    print("  %d x %d, %d calques, %d textes" % (L, H, couches, textes))
    print()
    for m in MONTAGES:
        print("  %-10s %s" % (m["nom"],
                              "amovible" if m["amovible"] else "DÉFINITIVE"))


if __name__ == "__main__":
    principal()
