"""
Le trajet d'un post sur Bluesky, et qui tient chaque étage.

    python3 article-bluesky/trajet_post.py

Produit `bluesky-trajet-post.webp`, son PNG et le SVG éditable.

----------------------------------------------------------------------------
QUATRE ÉTAGES SUR UN RAIL, PAS QUATRE CASES
----------------------------------------------------------------------------
Le sujet est une chaîne : un post passe par le PDS, le relais, l'AppView,
puis l'appli, dans cet ordre et sans raccourci. Un rail avec quatre
pastilles numérotées dit cette succession ; quatre cartes encadrées
diraient quatre catégories, ce qui est faux.

Les colonnes sont également espacées, et c'est volontaire. Rien ici ne
mesure une durée ou un poids : des largeurs inégales suggéreraient une
grandeur qui n'existe pas. Ce sont les numéros qui portent l'ordre.

----------------------------------------------------------------------------
LA COULEUR REMPLACE LES INTITULÉS DE LIGNE
----------------------------------------------------------------------------
Chaque étage porte deux informations : qui le tient chez Bluesky, et qui
le tient ailleurs. Répéter « Chez Bluesky » et « Ailleurs » sous les
quatre colonnes fabriquerait un tableau à deux lignes.

La légende le dit donc une seule fois, en haut, et la couleur s'en charge
ensuite. L'indigo est l'entreprise, l'ambre les indépendants. Ce sont deux
séries, pas un état sain opposé à un état dégradé : les teintes de
signalisation de la charte n'ont rien à faire ici.

----------------------------------------------------------------------------
LE CHIFFRE QUI FAIT LA DÉMONSTRATION EST CALCULÉ
----------------------------------------------------------------------------
L'article conclut que « la porte existe, mais presque personne ne l'a
prise ». La figure ne se contente pas de le répéter : elle divise les
121 470 comptes ayant publié depuis un serveur indépendant par les 46
millions de comptes inscrits, et pose le résultat sous le dessin.

Le rapport est recalculé à chaque dessin et comparé à la valeur écrite.
Si l'un des deux nombres change et pas l'autre, le script refuse de
dessiner plutôt que d'imprimer un pourcentage faux.
"""

import os

import charte as C
import dessin as D

L = 1600
MARGE = 56

#  Deux séries, deux teintes. Ni ALERTE ni VERT : la charte les réserve aux
#  figures qui opposent un état sain à un état dégradé, et ce n'est pas le
#  cas ici. Un opérateur n'est pas une panne.
INDIGO = C.VIOLET_TEXTE
AMBRE = (180, 83, 9)

#  ---------------------------------------------------------------------------
#  LES CHIFFRES DE L'ARTICLE
#  ---------------------------------------------------------------------------
COMPTES_INDEPENDANTS = 121470     # comptes ayant publié hors Bluesky
SERVEURS_INDEPENDANTS = 3788
COMPTES_INSCRITS = 46_000_000
PART_ANNONCEE = 0.26              # ce que le pied affiche, en pourcent

#  ---------------------------------------------------------------------------
#  LES QUATRE ÉTAGES
#  ---------------------------------------------------------------------------
ETAGES = (
    {"nom": "Le PDS",
     "quoi": "le serveur de données personnelles, qui héberge votre compte "
             "et vos posts",
     "bluesky": "bsky.social, le serveur par défaut",
     #  Le pourcentage est injecté au dessin, jamais recopié : voir le
     #  contrôle dans composer().
     "ailleurs": "3 788 serveurs, 121 470 comptes, soit {part} % du réseau"},

    {"nom": "Le relais",
     "quoi": "il rassemble le flux de tous les serveurs du réseau",
     "bluesky": "le relais de l’entreprise",
     "ailleurs": "Blacksky, Eurosky. Deux cœurs et 12 Go suffisent depuis "
                 "mai 2025"},

    {"nom": "L’AppView",
     "quoi": "elle trie le flux, compte les likes et fabrique les fils",
     "bluesky": "l’AppView de l’entreprise",
     "ailleurs": "Blacksky a la sienne depuis début 2026"},

    {"nom": "L’appli",
     "quoi": "elle affiche ce que l’AppView a préparé",
     "bluesky": "l’appli Bluesky",
     "ailleurs": "près de 200 applis bâties en quatre mois"},
)

LEGENDE = (("tenu par l’entreprise Bluesky", INDIGO),
           ("tenu par des indépendants", AMBRE))

#  Transverse aux quatre étages, donc posé à part et non comme un cinquième.
ANNUAIRE = ("L’annuaire des identités",
            "Il relie chaque compte à son serveur, et ne dépend d’aucun des "
            "quatre étages. Bluesky a annoncé en septembre 2025 le confier à "
            "une association de droit suisse.")

POLICES = {
    "titre": (C.POLICE_G, 19, "bold"),
    "sous": (C.POLICE_R, 17, "normal"),
    "legende": (C.POLICE_R, 14, "normal"),
    "numero": (C.POLICE_G, 17, "bold"),
    "etage": (C.POLICE_G, 21, "bold"),
    "quoi": (C.POLICE_R, 15, "normal"),
    "operateur": (C.POLICE_R, 16, "normal"),
    "annuaire": (C.POLICE_G, 17, "bold"),
    "annuairedet": (C.POLICE_R, 15, "normal"),
}
FAMILLE_SVG = "Liberation Sans, Arial, Helvetica, sans-serif"

TITRE = "LE TRAJET D’UN POST, ET QUI TIENT CHAQUE ÉTAGE"
SOUS = ("du serveur qui héberge votre compte jusqu’à l’appli qui l’affiche, "
        "chacun des quatre étages peut changer de mains")

RAIL_Y = 332
RAIL_X0, RAIL_X1 = 100, L - 100
RAYON = 21
Y_ETAGE = 186
Y_QUOI = 216
Y_OPERATEURS = 392


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
    if len(ETAGES) != 4:
        raise SystemExit("le schéma annonce quatre étages, la table en porte "
                         "%d" % len(ETAGES))
    for e in ETAGES:
        for cle in ("nom", "quoi", "bluesky", "ailleurs"):
            if not e[cle].strip():
                raise SystemExit("« %s » n'a pas de %s : un étage sans "
                                 "alternative ne démontre rien"
                                 % (e["nom"], cle))

    #  LE CHIFFRE EST RECALCULÉ, JAMAIS RECOPIÉ.
    part = 100.0 * COMPTES_INDEPENDANTS / COMPTES_INSCRITS
    if abs(part - PART_ANNONCEE) > 0.005:
        raise SystemExit(
            "le pied annonce %.2f %% et le calcul donne %.3f %% : un des deux "
            "nombres a bougé sans l'autre" % (PART_ANNONCEE, part))
    if SERVEURS_INDEPENDANTS <= 0 or COMPTES_INDEPENDANTS <= 0:
        raise SystemExit("les comptages indépendants sont nuls")

    colonne = (RAIL_X1 - RAIL_X0) / float(len(ETAGES))
    largeur = colonne - 46
    centres = [RAIL_X0 + (i + 0.5) * colonne for i in range(len(ETAGES))]

    o = []
    o.append(texte("titre", (MARGE, 46), TITRE, "titre", D.ENCRE, 2.2))
    sous = D.typo(SOUS)
    if mesure.mesure(sous, fontes["sous"]) > L - 2 * MARGE:
        raise SystemExit("le sous-titre déborde")
    o.append(texte("titre", (MARGE, 74), sous, "sous", D.FAIBLE))

    x = MARGE
    for libelle, teinte_l in LEGENDE:
        o.append(disque("titre", x + 7, 128, 7, teinte_l))
        o.append(texte("titre", (x + 22, 119), libelle, "legende", D.GRIS))
        x += 22 + mesure.mesure(libelle, fontes["legende"]) + 40

    #  --------------------------------------------------------------  rail
    o.append(trait("rail", [centres[0], RAIL_Y, centres[-1], RAIL_Y],
                   D.FILET, 3))

    #  -----------------------------------------------------  mise en page
    #  Les blocs du haut sont calés par le BAS contre le rail, ceux du bas
    #  par le haut : sinon les colonnes à deux lignes décalent tout.
    hauts, pastilles, operateurs = [], [], []
    bas_max = 0

    for i, (e, cx) in enumerate(zip(ETAGES, centres)):
        pastilles.append(disque("pastilles", cx, RAIL_Y, RAYON, D.PAPIER))
        pastilles.append(disque("pastilles", cx, RAIL_Y, RAYON - 3, INDIGO))
        pastilles.append(texte("pastilles", (cx, RAIL_Y - 11), str(i + 1),
                               "numero", D.BLANC, centre=True))

        nom = D.typo(e["nom"])
        if mesure.mesure(nom, fontes["etage"]) > largeur:
            raise SystemExit("le nom « %s » déborde de sa colonne" % nom)
        hauts.append(texte("étages", (cx, Y_ETAGE), nom, "etage", D.ENCRE,
                           centre=True))

        lignes_q = mesure.couper(D.typo(e["quoi"]), fontes["quoi"], largeur)
        if len(lignes_q) > 3:
            raise SystemExit("la description de « %s » tient en %d lignes"
                             % (nom, len(lignes_q)))
        y = Y_QUOI + (3 - len(lignes_q)) * 21
        for ligne in lignes_q:
            hauts.append(texte("étages", (cx, y), ligne, "quoi", D.GRIS,
                               centre=True))
            y += 21

        y = Y_OPERATEURS
        for cle, teinte_o in (("bluesky", INDIGO), ("ailleurs", AMBRE)):
            contenu = e[cle].replace("{part}", ("%.2f" % part)
                                     .replace(".", ","))
            lignes = mesure.couper(D.typo(contenu), fontes["operateur"],
                                   largeur)
            if len(lignes) > 3:
                raise SystemExit("« %s » de l'étage %s tient en %d lignes"
                                 % (cle, nom, len(lignes)))
            for ligne in lignes:
                operateurs.append(texte("opérateurs", (cx, y), ligne,
                                        "operateur", teinte_o, centre=True))
                y += 23
            y += 16
        bas_max = max(bas_max, y)

    o.extend(hauts)
    o.extend(pastilles)
    o.extend(operateurs)

    #  ----------------------------------------------------------  annuaire
    y = bas_max + 14
    o.append(trait("annuaire", [MARGE, y, L - MARGE, y], D.FILET, 2))
    y += 24
    o.append(disque("annuaire", MARGE + 7, y + 9, 7, D.FAIBLE))
    o.append(texte("annuaire", (MARGE + 24, y), D.typo(ANNUAIRE[0]),
                   "annuaire", D.ENCRE))
    y += 26
    lignes_a = mesure.couper(D.typo(ANNUAIRE[1]), fontes["annuairedet"],
                             L - 2 * MARGE - 24)
    if len(lignes_a) > 2:
        raise SystemExit("la note sur l'annuaire tient en %d lignes"
                         % len(lignes_a))
    for ligne in lignes_a:
        o.append(texte("annuaire", (MARGE + 24, y), ligne, "annuairedet",
                       D.GRIS))
        y += 22

    #  PAS DE PIED DE PAGE. Le chiffre qui compte est remonté dans la
    #  colonne du PDS, là où il veut dire quelque chose. Des notes de
    #  fabrication empilées sous le dessin, c'est ce fichier qui les porte.
    H = int(y + 30)
    o.insert(0, rect("fond", [0, 0, L, H], 0, D.PAPIER))
    return H, o, part


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
                        "bluesky-trajet-post")
    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5),
               ("indigo", INDIGO, 4.5), ("ambre", AMBRE, 4.5))

    H, ordres, part = composer()
    rendre_matriciel(H, ordres, base)
    couches, textes = rendre_svg(H, ordres, base)

    print("  %-34s %.0f Ko"
          % (os.path.basename(base + ".svg"),
             os.path.getsize(base + ".svg") / 1024.0))
    print("  %d x %d, %d calques, %d textes" % (L, H, couches, textes))
    print()
    for i, e in enumerate(ETAGES):
        print("  %d. %-12s  Bluesky : %s" % (i + 1, e["nom"], e["bluesky"]))
    print()
    print("  part des comptes indépendants : %.3f %%" % part)


if __name__ == "__main__":
    principal()
