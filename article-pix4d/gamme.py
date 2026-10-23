"""
La gamme Pix4D au 23 octobre 2026, et ce qui en sort.

    python3 article-pix4d/gamme.py

Produit `pix4d-gamme-2026.webp`, son PNG et le SVG éditable.

----------------------------------------------------------------------------
CE QUE CETTE FIGURE REMPLACE
----------------------------------------------------------------------------
Une première version circulait hors charte : fond crème, titre bleu
marine, sept cartes encadrées sur deux rangées, éditions en bleu vif et
fin de vie en orange. Le contenu est repris mot pour mot.

----------------------------------------------------------------------------
PLUS DE CARTES : LE TITRE DIT UNE PROGRESSION, PAS UNE GRILLE
----------------------------------------------------------------------------
« Sept logiciels, dont un sur le départ. » Sept cartes de même taille
rangées en damier disent le contraire : que tout se vaut. La figure
suit donc le titre, en trois temps séparés par un filet.

  en vente   les six qu'on peut acheter aujourd'hui, sur deux colonnes
  sur le départ   PIX4Dmapper seul, sur toute la largeur
  sortis     les trois qui ne sont plus là, barrés

Le lecteur descend du vivant vers le mort, et PIX4Dmapper occupe la
charnière, qui est exactement sa place.

----------------------------------------------------------------------------
UNE SEULE ALERTE, ET ELLE EST MÉRITÉE
----------------------------------------------------------------------------
La charte réserve l'alerte aux figures qui opposent un état sain à un
état dégradé. Ici elle ne touche qu'une ligne : la date à laquelle
PIX4Dmapper cesse d'être vendu. C'est la seule information de la figure
sur laquelle un lecteur doit agir.

Les trois logiciels déjà sortis ne sont pas en alerte. Ils ne sont plus
là, il n'y a rien à surveiller : ils sont barrés, en gris.
"""

import os

import charte as C
import dessin as D

L = 1600
MARGE = 56

INDIGO = C.VIOLET_TEXTE
ALERTE = C.ALERTE

#  ---------------------------------------------------------------------------
#  LES SEPT LOGICIELS EN VENTE
#
#  `editions` n'existe que pour les trois produits qui en annoncent.
#  `fin` marque celui qui quitte la gamme : il y en a exactement un.
#  ---------------------------------------------------------------------------
EN_VENTE = (
    {"nom": "PIX4Dmatic", "ou": "Logiciel de bureau · Windows et macOS",
     "quoi": "Le logiciel phare : photogrammétrie et LiDAR, de quelques "
             "photos à des dizaines de milliers. Orthomosaïque, nuage de "
             "points, maillage, CAO.",
     "editions": "Analyst · Standard · Pro"},
    {"nom": "PIX4Dcloud", "ou": "Plateforme en ligne",
     "quoi": "Traitement dans le cloud, mesures, partage par lien, suivi de "
             "chantier.",
     "editions": "Starter · Pro · Enterprise"},
    {"nom": "PIX4Dcatch", "ou": "Appli mobile · iOS et Android",
     "quoi": "Scan 3D au smartphone. LiDAR sur iPhone et iPad Pro, RTK sur "
             "iOS seulement.",
     "editions": "Pro · Pro + PIX4Dcloud Pro"},
    {"nom": "PIX4Dfields", "ou": "Bureau · Agriculture",
     "quoi": "Indices de végétation, cartes de préconisation, même sans "
             "connexion."},
    {"nom": "PIX4Dreact", "ou": "Bureau · Secours",
     "quoi": "Carte 2D en quelques minutes, sans internet, pour les équipes "
             "d’urgence."},
    {"nom": "PIX4Dengine", "ou": "Kit de développement",
     "quoi": "Le moteur de Pix4D en modules Python, à intégrer dans ses "
             "propres outils."},
    {"nom": "PIX4Dmapper", "ou": "Bureau · Historique",
     "fin": ("Plus vendu ni renouvelé au 1er janvier 2027.",
             "Support arrêté le 1er décembre 2027.")},
)

SORTIS = (
    {"nom": "PIX4Dsurvey", "quoi": "fondu dans PIX4Dmatic 2.0, janvier 2026"},
    {"nom": "PIX4Dinspect", "quoi": "arrêté, relais assuré par PIX4Dcloud"},
    {"nom": "PIX4Dcapture", "quoi": "appli de vol arrêtée"},
)

#  Ce que le titre annonce, et que la figure doit retrouver seule.
ANNONCES = {"logiciels en vente": 7, "sur le départ": 1, "sortis": 3}

POLICES = {
    "titre": (C.POLICE_G, 19, "bold"),
    "sous": (C.POLICE_R, 17, "normal"),
    "bande": (C.POLICE_G, 13, "bold"),
    "ou": (C.POLICE_R, 13, "normal"),
    "nom": (C.POLICE_G, 20, "bold"),
    "quoi": (C.POLICE_R, 15, "normal"),
    "editions": (C.POLICE_G, 14, "bold"),
    "note": (C.POLICE_R, 14, "normal"),
}
FAMILLE_SVG = "Liberation Sans, Arial, Helvetica, sans-serif"

TITRE = "PIX4D EN 2026 : SEPT LOGICIELS, DONT UN SUR LE DÉPART"
SOUS = ("la gamme de l’éditeur suisse au 23 octobre 2026, par usage, et ce "
        "qui en est sorti")
NOTE = ("Relevé le 23 octobre 2026 sur pix4d.com, support.pix4d.com et "
        "community.pix4d.com.")

Y0 = 132
COLONNES = (MARGE, 830)
LARGEUR_COL = 714
ECART_ENTREE = 26
H_BANDE = 40


def rect(couche, b, r, teinte):
    return {"quoi": "rect", "couche": couche, "b": b, "r": r, "t": teinte}


def trait(couche, b, teinte, epaisseur):
    return {"quoi": "trait", "couche": couche, "b": b, "t": teinte,
            "e": epaisseur}


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
    partants = [p for p in EN_VENTE if "fin" in p]
    trouve = {"logiciels en vente": len(EN_VENTE),
              "sur le départ": len(partants), "sortis": len(SORTIS)}
    for quoi, attendu in ANNONCES.items():
        if trouve[quoi] != attendu:
            raise SystemExit("le titre annonce %d %s, la figure en compte %d"
                             % (attendu, quoi, trouve[quoi]))

    noms = [p["nom"] for p in EN_VENTE] + [s["nom"] for s in SORTIS]
    if len(set(noms)) != len(noms):
        raise SystemExit("un logiciel apparaît deux fois")

    #  Le partant ferme la liste : c'est lui la charnière entre le vivant
    #  et le mort, et il se dessine seul, après les six autres.
    if "fin" not in EN_VENTE[-1]:
        raise SystemExit("le logiciel sur le départ doit être le dernier de "
                         "la liste, c'est lui la charnière de la figure")
    partant = EN_VENTE[-1]
    courants = EN_VENTE[:-1]

    o = []
    o.append(texte("titre", (MARGE, 46), D.typo(TITRE), "titre", D.ENCRE,
                   2.2))
    sous = D.typo(SOUS)
    if mesure.mesure(sous, fontes["sous"]) > L - 2 * MARGE:
        raise SystemExit("le sous-titre déborde")
    o.append(texte("titre", (MARGE, 74), sous, "sous", D.FAIBLE))

    bandes, entrees, barres = [], [], []

    def bande(y, mot):
        m = D.typo(mot)
        bandes.append(trait("bandes", [MARGE, y, L - MARGE, y], D.FILET, 1))
        bandes.append(texte("bandes", (MARGE, y + 10), m, "bande", INDIGO,
                            1.4))
        return y + H_BANDE

    def entree(x, y, p, largeur):
        """Pose un logiciel et rend l'ordonnée juste sous lui."""
        entrees.append(texte("liste", (x, y), D.typo(p["ou"]), "ou",
                             D.FAIBLE, 0.8))
        y += 20
        entrees.append(texte("liste", (x, y), p["nom"], "nom", D.ENCRE))
        y += 28
        if p.get("quoi"):
            for ligne in mesure.couper(D.typo(p["quoi"]), fontes["quoi"],
                                       largeur):
                entrees.append(texte("liste", (x, y), ligne, "quoi", D.GRIS))
                y += 21
        if "editions" in p:
            y += 4
            e = D.typo(p["editions"])
            if mesure.mesure(e, fontes["editions"]) > largeur:
                raise SystemExit("les éditions de « %s » débordent" % p["nom"])
            entrees.append(texte("liste", (x, y), e, "editions", INDIGO))
            y += 22
        return y

    #  -------------------------------------------------  les six en vente
    y = bande(Y0, "EN VENTE AUJOURD’HUI")
    bas = [y, y]
    for i, p in enumerate(courants):
        col = i % 2
        bas[col] = entree(COLONNES[col], bas[col], p, LARGEUR_COL) \
            + ECART_ENTREE
    y = max(bas) + 10

    if COLONNES[0] + LARGEUR_COL > COLONNES[1] - 24:
        raise SystemExit("les deux colonnes se touchent")
    if COLONNES[1] + LARGEUR_COL > L - MARGE:
        raise SystemExit("la colonne de droite sort du cadre")

    #  ---------------------------------------------------  celui qui part
    y = bande(y, "SUR LE DÉPART")
    y = entree(MARGE, y, partant, L - 2 * MARGE)
    y += 8
    for ligne, teinte in zip(partant["fin"], (ALERTE, D.GRIS)):
        entrees.append(texte("liste", (MARGE, y), D.typo(ligne), "editions",
                             teinte))
        y += 22
    y += 18

    #  ------------------------------------------------  ceux qui sont sortis
    y = bande(y, "SORTIS DE LA GAMME")
    pas = (L - 2 * MARGE) / float(len(SORTIS))
    for i, s in enumerate(SORTIS):
        x = MARGE + i * pas
        largeur_nom = mesure.mesure(s["nom"], fontes["nom"])
        entrees.append(texte("liste", (x, y), s["nom"], "nom", D.FAIBLE))
        #  Barré, parce que « sorti de la gamme » se montre mieux qu'il ne
        #  s'écrit. Le trait passe au milieu des capitales.
        barres.append(trait("bandes", [x, y + 15, x + largeur_nom, y + 15],
                            D.FAIBLE, 2))
        q = D.typo(s["quoi"])
        if mesure.mesure(q, fontes["quoi"]) > pas - 24:
            raise SystemExit("« %s » fait %d px pour une colonne de %d"
                             % (q, mesure.mesure(q, fontes["quoi"]), pas - 24))
        entrees.append(texte("liste", (x, y + 30), q, "quoi", D.GRIS))
    y += 86

    o.extend(bandes)
    o.extend(barres)
    o.extend(entrees)

    note = D.typo(NOTE)
    if mesure.mesure(note, fontes["note"]) > L - 2 * MARGE:
        raise SystemExit("la note déborde")
    o.append(texte("note", (MARGE, y), note, "note", D.FAIBLE))

    H = int(y + 52)
    o.insert(0, rect("fond", [0, 0, L, H], 0, D.PAPIER))
    return H, o, trouve


def rendre_matriciel(H, ordres, base):
    t = D.Toile(L, H)
    fontes = {k: t.police(f, taille) for k, (f, taille, _) in POLICES.items()}
    for a in ordres:
        if a["quoi"] == "rect":
            t.rrect(a["b"], a["r"], teinte=a["t"])
        elif a["quoi"] == "trait":
            t.ligne(a["b"], a["t"], a["e"])
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
                        "pix4d-gamme-2026")
    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5),
               ("faible", D.FAIBLE, 3.0), ("indigo", INDIGO, 4.5),
               ("alerte", ALERTE, 4.5))

    H, ordres, trouve = composer()
    rendre_matriciel(H, ordres, base)
    couches, textes = rendre_svg(H, ordres, base)

    print()
    print("  %-38s %.0f Ko"
          % (os.path.basename(base + ".svg"),
             os.path.getsize(base + ".svg") / 1024.0))
    print("  %d x %d, %d calques, %d textes" % (L, H, couches, textes))
    print()
    for p in EN_VENTE:
        print("  %-14s %-38s%s"
              % (p["nom"], p["ou"], "   sur le départ" if "fin" in p else ""))
    for s in SORTIS:
        print("  %-14s sorti : %s" % (s["nom"], s["quoi"]))
    print()
    for quoi, n in trouve.items():
        print("  %-20s %d" % (quoi, n))


if __name__ == "__main__":
    principal()
