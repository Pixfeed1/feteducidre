"""
Les quatre surfaces de capteur, emboîtées et à l'échelle.

    python3 article-webcam-2026/surfaces_capteurs.py

Produit `webcam-2026-surfaces-capteurs.webp`, son PNG et le SVG éditable.

----------------------------------------------------------------------------
RIEN N'EST SAISI DEUX FOIS
----------------------------------------------------------------------------
On n'entre que les COTES de chaque capteur, en millimètres. Les surfaces,
les rapports entre elles et le rapport annoncé par le titre en découlent.
Une surface recopiée à la main dans une figure qui dessine des surfaces est
la première chose qui se met à mentir : le rectangle et son étiquette
finissent par ne plus dire la même chose, et rien ne le signale.

Le titre lui-même est contrôlé. Il affirme deux rapports, « treize fois la
surface » et « moins de cinq fois le prix » ; deux contrôles vérifient que
la table les porte encore avant d'autoriser le dessin. Un titre est la
seule ligne qu'un lecteur retient toujours, et c'est celle qu'on oublie de
relire quand une valeur change.

Note de relecture pour l'article : le corps du texte écrit que l'écart
entre le 1/1,28 pouce et l'APS-C est « d'un facteur cinq ». Avec les cotes
ci-dessous, il est de 4,6. Les surfaces étant ici dessinées à l'échelle,
l'écart se mesure à la règle sur l'image, et un lecteur méticuleux ne
retrouverait pas le cinq.

----------------------------------------------------------------------------
LE POUCE DES CAPTEURS N'EST PAS UN POUCE
----------------------------------------------------------------------------
Un capteur « 1/2,5 pouce » ne mesure pas 25,4 / 2,5 millimètres de
diagonale, mais à peu près 16 / 2,5. La convention vient du diamètre
extérieur des anciens tubes vidéo, dont la surface utile occupait environ
les deux tiers. C'est pour ça que les cotes de la table sont écrites en
millimètres réels et que la diagonale est recalculée à côté : elle sert de
contrôle contre le format annoncé.

----------------------------------------------------------------------------
UNE RAMPE POUR LES WEBCAMS, UNE AUTRE TEINTE POUR L'HYBRIDE
----------------------------------------------------------------------------
Les trois webcams forment une série ordonnée : elles reçoivent une rampe de
violet, du plus clair au plus foncé, qui se lit comme un classement. L'APS-C
n'est pas le quatrième terme de cette série, c'est un autre objet ; il
reçoit l'ambre. La couleur dit donc la même chose que l'article, à savoir
qu'à un moment on ne compare plus des webcams entre elles.
"""

import os

import charte as C
import dessin as D

L = 1600
MARGE = 56

VIOLET = (98, 44, 200)
AMBRE = (180, 83, 9)

#  ---------------------------------------------------------------------------
#  LES QUATRE CAPTEURS
#
#  Seules les cotes sont saisies. `teinte` sert au trait et à la pastille,
#  `fond` au remplissage du rectangle, qui doit rester assez pâle pour que
#  les rectangles emboîtés dessous restent lisibles.
#  ---------------------------------------------------------------------------
CAPTEURS = (
    {"format": "1/2,5 pouce", "l": 5.76, "h": 4.29,
     "produit": "Elgato Facecam MK.2", "prix": 119.99,
     "teinte": (150, 120, 226), "fond": (243, 239, 252)},
    {"format": "1/2 pouce", "l": 6.40, "h": 4.80,
     "produit": "Insta360 Link 2C", "prix": 226.74,
     "teinte": (124, 82, 214), "fond": (236, 230, 250)},
    {"format": "1/1,28 pouce", "l": 9.80, "h": 7.30,
     "produit": "OBSBOT Tiny 3", "prix": 379.20,
     "teinte": VIOLET, "fond": (228, 219, 248)},
    {"format": "APS-C", "l": 22.30, "h": 14.90,
     "produit": "Canon EOS R50 V", "prix": 559.99,
     "teinte": AMBRE, "fond": (250, 240, 228)},
)

POLICES = {
    "titre": (C.POLICE_G, 19, "bold"),
    "sous": (C.POLICE_R, 17, "normal"),
    "etiq": (C.POLICE_G, 15, "bold"),
    "nom": (C.POLICE_G, 20, "bold"),
    "surface": (C.POLICE_G, 24, "bold"),
    "produit": (C.POLICE_R, 15, "normal"),
    "detail": (C.POLICE_R, 14, "normal"),
    "pied": (C.POLICE_R, 16, "normal"),
}
FAMILLE = "Liberation Sans, Arial, Helvetica, sans-serif"

#  Le titre ne dit que ce que la table permet : 13,4 est bien « treize
#  fois », et 4,67 est bien « moins de cinq fois ». Écrire « treize fois et
#  demie » aurait été un arrondi de trop dans une figure qui dessine les
#  surfaces à l'échelle, donc mesurables à la règle par le lecteur.
TITRE = "TREIZE FOIS LA SURFACE, MOINS DE CINQ FOIS LE PRIX"
SOUS = ("surfaces de capteur à l’échelle, du 1/2,5 pouce d’une webcam à "
        "120 euros à l’APS-C d’un hybride à 560 euros")

#  Le dessin : coin bas-gauche commun, le plus grand capteur sur LARGEUR_APSC.
X_DESSIN = 92
BAS = 806
LARGEUR_APSC = 742

#  La colonne des fiches.
X_FICHE = 916
HAUTEUR_FICHE = 136
PAS_FICHE = 162
Y_FICHE = 160


def nombre(x, decimales=1):
    """Un nombre à la française, virgule et sans zéro inutile."""
    t = ("%%.%df" % decimales) % x
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",")


def euros(x):
    entier, cents = divmod(round(x * 100), 100)
    milliers = "%d" % entier
    if len(milliers) > 3:
        milliers = milliers[:-3] + " " + milliers[-3:]
    return "%s,%02d €" % (milliers, cents)


# ===========================================================================
#  ORDRES DE DESSIN
# ===========================================================================

def rect(couche, b, r, teinte):
    return {"quoi": "rect", "couche": couche, "b": b, "r": r, "t": teinte}


def cadre(couche, b, r, teinte, epaisseur=2):
    return {"quoi": "cadre", "couche": couche, "b": b, "r": r, "t": teinte,
            "e": epaisseur}


def trait(couche, b, teinte, epaisseur):
    return {"quoi": "trait", "couche": couche, "b": b, "t": teinte,
            "e": epaisseur}


def texte(couche, xy, contenu, police, teinte, tracking=0.0, droite=False):
    for c, nom in (("—", "cadratin"), ("–", "demi-cadratin")):
        if c in contenu:
            raise SystemExit("%s dans « %s »" % (nom, contenu[:60]))
    return {"quoi": "texte", "couche": couche, "xy": xy, "c": contenu,
            "p": police, "t": teinte, "tr": tracking, "droite": droite}


def composer():
    mesure = D.Toile(L, 10)
    fontes = {k: mesure.police(f, t) for k, (f, t, _) in POLICES.items()}

    #  ------------------------------------------------------------------
    #  TOUT SE DÉDUIT DES COTES
    #  ------------------------------------------------------------------
    for c in CAPTEURS:
        c["surface"] = c["l"] * c["h"]
        c["diagonale"] = (c["l"] ** 2 + c["h"] ** 2) ** 0.5

    petit = CAPTEURS[0]
    for c in CAPTEURS:
        c["rapport"] = c["surface"] / petit["surface"]

    #  CONTRÔLE : les rectangles doivent s'emboîter VRAIMENT, sur les deux
    #  côtés. Un capteur plus large mais moins haut casserait le dessin sans
    #  casser le calcul, et la figure mentirait en silence.
    for a, b in zip(CAPTEURS, CAPTEURS[1:]):
        if not (b["l"] > a["l"] and b["h"] > a["h"]):
            raise SystemExit(
                "%s ne contient pas %s : %s x %s contre %s x %s"
                % (b["format"], a["format"], b["l"], b["h"], a["l"], a["h"]))

    #  CONTRÔLE : les deux affirmations du titre viennent de la table.
    grand = CAPTEURS[-1]["rapport"]
    prix = CAPTEURS[-1]["prix"] / CAPTEURS[0]["prix"]
    if not 13.0 <= grand < 14.0:
        raise SystemExit(
            "le titre annonce treize fois la surface, la table donne %s"
            % nombre(grand, 2))
    if not 4.0 <= prix < 5.0:
        raise SystemExit(
            "le titre annonce moins de cinq fois le prix, la table donne %s"
            % nombre(prix, 2))
    if "TREIZE FOIS" not in TITRE or "CINQ FOIS" not in TITRE:
        raise SystemExit("le titre ne reprend plus les rapports calculés")

    echelle = LARGEUR_APSC / CAPTEURS[-1]["l"]

    o = []
    o.append(texte("titre", (MARGE, 46), TITRE, "titre", D.ENCRE, 2.2))
    sous = D.typo(SOUS)
    if mesure.mesure(sous, fontes["sous"]) > L - 2 * MARGE:
        raise SystemExit("le sous-titre déborde")
    o.append(texte("titre", (MARGE, 74), sous, "sous", D.FAIBLE))
    o.append(trait("titre", [MARGE, 124, L - MARGE, 124], D.FILET, 2))

    #  ---------------------------------------------------------  rectangles
    #
    #  Du plus grand au plus petit : chaque rectangle est peint par-dessus le
    #  précédent, et ce qui reste visible de chacun est l'écart de surface.
    for c in reversed(CAPTEURS):
        larg = c["l"] * echelle
        haut = c["h"] * echelle
        b = [X_DESSIN, BAS - haut, X_DESSIN + larg, BAS]
        c["coin"] = (X_DESSIN + larg, BAS - haut)
        o.append(rect("capteurs", b, 3, c["fond"]))
        o.append(cadre("capteurs", b, 3, c["teinte"], 3))

    #  ------------------------------------------------------------  repères
    #
    #  Les deux plus petits capteurs ne sont séparés que de 22 pixels : leurs
    #  étiquettes posées au coin se chevaucheraient. On les écarte
    #  verticalement et on tire un filet jusqu'au coin, pour que chaque nom
    #  désigne sans ambiguïté son rectangle.
    #  Le plus grand rectangle laisse un vide à sa droite, au-dessus de la
    #  pile des trois petits : c'est là que vont les étiquettes. Les tirer
    #  vers l'extérieur les envoyait cogner la colonne des fiches, et les
    #  deux plus petits capteurs, séparés de dix-huit pixels, ne peuvent pas
    #  porter leur nom à même leur bande.
    X_ETIQ = 474
    hauteurs = {"1/2,5 pouce": 752, "1/2 pouce": 664, "1/1,28 pouce": 556}
    for c in CAPTEURS[:-1]:
        x, y = c["coin"]
        cible = hauteurs[c["format"]]
        o.append(trait("repères", [x, y, x + 22, cible], c["teinte"], 2))
        o.append(trait("repères", [x + 22, cible, X_ETIQ - 10, cible],
                       c["teinte"], 2))
        o.append(texte("repères", (X_ETIQ, cible - 9), c["format"], "etiq",
                       c["teinte"]))

    #  L'APS-C n'a pas besoin de repère : c'est le rectangle qui contient
    #  tous les autres. Son nom se pose dans son propre coin.
    apsc_c = CAPTEURS[-1]
    o.append(texte("repères", (X_DESSIN + 18, apsc_c["coin"][1] + 16),
                   apsc_c["format"], "etiq", apsc_c["teinte"]))

    #  ------------------------------------------------------------  fiches
    y = Y_FICHE
    for c in reversed(CAPTEURS):
        o.append(rect("fiches", [X_FICHE, y, L - MARGE, y + HAUTEUR_FICHE],
                      10, D.BLANC))
        o.append(cadre("fiches", [X_FICHE, y, L - MARGE, y + HAUTEUR_FICHE],
                       10, D.FILET, 2))
        o.append(rect("fiches", [X_FICHE, y, X_FICHE + 7, y + HAUTEUR_FICHE],
                      3, c["teinte"]))
        y += PAS_FICHE

    y = Y_FICHE
    for c in reversed(CAPTEURS):
        gauche = X_FICHE + 28
        o.append(texte("textes", (gauche, y + 18), c["format"], "nom",
                       D.ENCRE))
        o.append(texte("textes", (L - MARGE - 22, y + 14),
                       "%s mm²" % nombre(c["surface"], 1), "surface",
                       c["teinte"], droite=True))
        o.append(texte("textes", (gauche, y + 50), D.typo(c["produit"]),
                       "produit", D.GRIS))
        cotes = "%s × %s mm  ·  diagonale %s mm" % (
            nombre(c["l"], 2), nombre(c["h"], 2), nombre(c["diagonale"], 1))
        rapport = ("référence des rapports ci-dessous"
                   if c is CAPTEURS[0]
                   else "× %s la surface du 1/2,5 pouce"
                        % nombre(c["rapport"], 1))
        for j, ligne in enumerate((cotes, "%s  ·  %s"
                                   % (euros(c["prix"]), rapport))):
            if mesure.mesure(ligne, fontes["detail"]) > L - MARGE - gauche - 16:
                raise SystemExit("le détail de %s déborde" % c["format"])
            o.append(texte("textes", (gauche, y + 80 + j * 24), D.typo(ligne),
                           "detail", D.FAIBLE))
        y += PAS_FICHE

    #  ---------------------------------------------------------------  pied
    tiny = next(c for c in CAPTEURS if c["format"] == "1/1,28 pouce")
    apsc = CAPTEURS[-1]
    face = CAPTEURS[0]
    pied = (
        "À l’échelle : l’APS-C couvre %s fois la surface du 1/2,5 pouce et "
        "%s fois celle du 1/1,28 pouce. Sur le côté, ces écarts tombent à "
        "%s et %s, ce qui explique qu’ils paraissent moins spectaculaires "
        "sur une fiche technique."
        % (nombre(apsc["rapport"], 1),
           nombre(apsc["surface"] / tiny["surface"], 1),
           nombre((apsc["surface"] / face["surface"]) ** 0.5, 1),
           nombre((apsc["surface"] / tiny["surface"]) ** 0.5, 1)),
        "Du Facecam MK.2 au Canon EOS R50 V, le prix est multiplié par %s et "
        "la surface de capteur par %s. Du Tiny 3 au R50 V, %s de prix en plus "
        "pour %s fois la surface."
        % (nombre(apsc["prix"] / face["prix"], 1),
           nombre(apsc["rapport"], 1),
           "%s %%" % nombre(100 * (apsc["prix"] / tiny["prix"] - 1), 0),
           nombre(apsc["surface"] / tiny["surface"], 1)),
        "Le « pouce » des capteurs vient du diamètre des anciens tubes "
        "vidéo : la diagonale utile vaut environ 16 mm divisés par le "
        "dénominateur, jamais 25,4. Les cotes ci-dessus sont les cotes "
        "réelles.",
    )

    y_pied = max(BAS, Y_FICHE + (len(CAPTEURS) - 1) * PAS_FICHE
               + HAUTEUR_FICHE) + 34
    o.append(trait("pied", [MARGE, y_pied, L - MARGE, y_pied], D.FILET, 2))
    y_texte = y_pied + 22
    for i, ligne in enumerate(pied):
        lignes = mesure.couper(D.typo(ligne), fontes["pied"], L - 2 * MARGE)
        if len(lignes) > 2:
            raise SystemExit("la ligne %d du pied tient en %d lignes"
                             % (i + 1, len(lignes)))
        for coupee in lignes:
            o.append(texte("pied", (MARGE, y_texte), coupee, "pied",
                           D.FAIBLE))
            y_texte += 24
        y_texte += 6

    H = int(y_texte + 20)
    o.insert(0, rect("fond", [0, 0, L, H], 0, D.PAPIER))
    return H, o


# ===========================================================================
#  LES DEUX RENDUS, DEPUIS LA MÊME LISTE D'ORDRES
# ===========================================================================

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
        else:
            f = fontes[a["p"]]
            x, y = a["xy"]
            if a["droite"]:
                x -= t.mesure(a["c"], f)
            if a["tr"]:
                t.espace((x, y), a["c"], f, a["t"], a["tr"])
            else:
                t.texte((x, y), a["c"], f, a["t"])
    D.enregistrer(t.final(L, H), base, L, H)


def rendre_svg(H, ordres, base):
    mesure = D.Toile(L, 10)
    fontes = {k: mesure.police(f, t) for k, (f, t, _) in POLICES.items()}
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
                           'stroke="%s" stroke-width="%g"/>'
                           % (x0, y0, x1, y1, teinte(a["t"]), a["e"]))
            else:
                _, taille, graisse = POLICES[a["p"]]
                espacement = (' letter-spacing="%g"' % a["tr"]
                              if a["tr"] else "")
                ancre = ' text-anchor="end"' if a["droite"] else ""
                out.append('    <text x="%g" y="%g" font-family="%s" '
                           'font-size="%g" font-weight="%s" fill="%s"%s%s'
                           ' xml:space="preserve">%s</text>'
                           % (a["xy"][0], a["xy"][1] + montees[a["p"]],
                              FAMILLE, taille, graisse, teinte(a["t"]),
                              espacement, ancre, propre(a["c"])))
        out.append('  </g>')
    out.append('</svg>')

    with open(base + ".svg", "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    return len(couches), sum(1 for a in ordres if a["quoi"] == "texte")


def principal():
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "webcam-2026-surfaces-capteurs")
    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5),
               ("violet", VIOLET, 4.5), ("ambre", AMBRE, 4.5))

    H, ordres = composer()
    rendre_matriciel(H, ordres, base)
    couches, textes = rendre_svg(H, ordres, base)

    print("  %-44s %.0f Ko"
          % (os.path.basename(base + ".svg"),
             os.path.getsize(base + ".svg") / 1024.0))
    print("  %d calques, %d textes" % (couches, textes))
    print()
    print("  %-14s %-13s %8s %9s %8s %7s"
          % ("format", "cotes", "diag", "surface", "rapport", "prix"))
    for c in CAPTEURS:
        print("  %-14s %5.2f x %-5.2f %6.2f mm %6.1f mm² %6.2f x %8.2f €"
              % (c["format"], c["l"], c["h"], c["diagonale"], c["surface"],
                 c["rapport"], c["prix"]))


if __name__ == "__main__":
    principal()
