"""
Prix d'appel contre prix de renouvellement, pour cinq hébergements.

    python3 article-hebergement/prix_renouvellement.py

Produit `hebergement-prix-renouvellement.webp`, son PNG et le SVG.

----------------------------------------------------------------------------
LA BARRE PÂLE EST DANS LA BARRE PLEINE, ET C'EST LE PROPOS
----------------------------------------------------------------------------
Deux barres côte à côte diraient « deux prix ». Ce n'est pas ce que vit
l'acheteur : il voit une petite somme, et il en paiera une grande. La
barre pleine est donc le prix réel, et la barre pâle, le prix d'appel,
est dessinée DEDANS. On lit d'un coup l'écart entre ce qui est montré et
ce qui est dû.

----------------------------------------------------------------------------
LE CLASSEMENT EST CELUI DU MULTIPLICATEUR
----------------------------------------------------------------------------
L'ordre du tableau de l'article est arbitraire. Ici les offres descendent
du plus gros écart au plus faible : la figure raconte alors quelque chose
au lieu d'énumérer. Un contrôle refuse de dessiner si la table n'est plus
triée.

----------------------------------------------------------------------------
LE GRAPHIQUE NE CLASSE PERSONNE
----------------------------------------------------------------------------
Les prestations diffèrent du tout au tout : 48 Go de mémoire chez
o2switch, trois sites au plus chez Hostinger. Comparer les prix n'est pas
comparer les offres, et le sous-titre le dit, parce que c'est le genre de
figure qu'on cite de travers.

----------------------------------------------------------------------------
LE CAS INFOMANIAK
----------------------------------------------------------------------------
Son prix d'appel est son prix tout court. Les deux barres se confondent,
et un libellé « même prix » remplace le multiplicateur : écrire « x1,00 »
donnerait à lire une hausse là où il n'y en a aucune.
"""

import os

import charte as C
import dessin as D

L = 1600
MARGE = 56

INDIGO = C.VIOLET_TEXTE
INDIGO_PALE = (221, 211, 246)

#  ---------------------------------------------------------------------------
#  LES CINQ OFFRES, relevées au 7 octobre 2026, en euros hors taxes par mois.
#
#  `mois_appel` est la durée pendant laquelle le prix d'appel s'applique :
#  douze mois pour presque tous, quarante-huit chez Hostinger, qui exige
#  le paiement d'avance. Zéro veut dire qu'il n'y a pas de prix d'appel.
#  ---------------------------------------------------------------------------
OFFRES = (
    {"nom": "IONOS", "offre": "Plus", "appel": 1.00, "ensuite": 11.00,
     "mois_appel": 12},
    {"nom": "o2switch", "offre": "Cloud", "appel": 1.86, "ensuite": 16.00,
     "mois_appel": 12},
    {"nom": "Hostinger", "offre": "Premium", "appel": 2.99, "ensuite": 9.99,
     "mois_appel": 48},
    {"nom": "OVHcloud", "offre": "Perso", "appel": 2.99, "ensuite": 5.99,
     "mois_appel": 12},
    {"nom": "Infomaniak", "offre": "Hébergement Web", "appel": 5.75,
     "ensuite": 5.75, "mois_appel": 0},
)

#  Ce que l'article affirme, et que la figure doit continuer de vérifier.
ANNONCES = {"o2switch": 8.6, "OVHcloud": 2.0, "IONOS": 11.0,
            "Infomaniak": 1.0}

LEGENDE = (("prix d’appel", INDIGO_PALE), ("prix au renouvellement", INDIGO))

POLICES = {
    "titre": (C.POLICE_G, 19, "bold"),
    "sous": (C.POLICE_R, 17, "normal"),
    "legende": (C.POLICE_R, 14, "normal"),
    "nom": (C.POLICE_G, 18, "bold"),
    "offre": (C.POLICE_R, 14, "normal"),
    "valeur": (C.POLICE_G, 15, "bold"),
    "appel": (C.POLICE_R, 14, "normal"),
    "facteur": (C.POLICE_G, 19, "bold"),
    "echelle": (C.POLICE_R, 13, "normal"),
}
FAMILLE_SVG = "Liberation Sans, Arial, Helvetica, sans-serif"

TITRE = "CE QUE VOUS PAIEREZ LA DEUXIÈME ANNÉE"
SOUS = ("cinq offres d’hébergement mutualisé relevées le 7 octobre 2026, "
        "aux prestations très différentes : la figure compare les prix, "
        "pas les services")

X_NOM = MARGE
X_BARRE = 300
X_FIN = 1226
X_FACTEUR = 1344
Y_PREMIERE = 220
PAS = 86
HAUTEUR_BARRE = 30


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


def euros(v):
    return ("%.2f" % v).replace(".", ",") + " €"


def composer():
    mesure = D.Toile(L, 10)
    fontes = {k: mesure.police(f, t) for k, (f, t, _) in POLICES.items()}

    #  ------------------------------------------------------------------
    #  CONTRÔLES
    #  ------------------------------------------------------------------
    for o in OFFRES:
        if o["ensuite"] < o["appel"]:
            raise SystemExit(
                "%s : le renouvellement (%s) est inférieur au prix d'appel "
                "(%s), la barre pâle sortirait de la pleine"
                % (o["nom"], euros(o["ensuite"]), euros(o["appel"])))
        o["facteur"] = o["ensuite"] / o["appel"]

    #  Les quatre rapports que l'article affirme noir sur blanc.
    for nom, attendu in ANNONCES.items():
        trouve = [o for o in OFFRES if o["nom"] == nom]
        if not trouve:
            raise SystemExit("l'article parle de %s, la table l'ignore" % nom)
        f = trouve[0]["facteur"]
        if abs(f - attendu) > 0.05:
            raise SystemExit(
                "l'article annonce un facteur %.2f pour %s, le calcul donne "
                "%.2f" % (attendu, nom, f))

    #  Le classement doit descendre, sinon la figure n'énonce plus rien.
    for a, b in zip(OFFRES, OFFRES[1:]):
        if b["facteur"] > a["facteur"] + 1e-9:
            raise SystemExit(
                "la table n'est pas triée : %s (x%.2f) précède %s (x%.2f)"
                % (a["nom"], a["facteur"], b["nom"], b["facteur"]))

    maxi = max(o["ensuite"] for o in OFFRES)
    echelle = (X_FIN - X_BARRE) / maxi

    #  La valeur de la barre la plus longue se pose APRÈS elle : elle doit
    #  rester à gauche de la colonne des multiplicateurs. Sans ce contrôle,
    #  l'offre la plus chère voit son prix percuter son facteur, et il faut
    #  l'œil pour s'en apercevoir.
    plus_long = max(euros(o["ensuite"]) for o in OFFRES)
    bout = X_FIN + 12 + mesure.mesure(plus_long, fontes["valeur"])
    if bout > X_FACTEUR - 16:
        raise SystemExit(
            "« %s » finit à %d px et la colonne des facteurs commence à %d : "
            "reculez X_FIN" % (plus_long, bout, X_FACTEUR))

    o_ = []
    o_.append(texte("titre", (MARGE, 46), TITRE, "titre", D.ENCRE, 2.2))
    sous = D.typo(SOUS)
    lignes_s = mesure.couper(sous, fontes["sous"], L - 2 * MARGE)
    if len(lignes_s) > 2:
        raise SystemExit("le sous-titre tient en %d lignes" % len(lignes_s))
    y = 74
    for ligne in lignes_s:
        o_.append(texte("titre", (MARGE, y), ligne, "sous", D.FAIBLE))
        y += 24

    x = MARGE
    for libelle, teinte_l in LEGENDE:
        o_.append(rect("titre", [x, y + 10, x + 22, y + 24], 4, teinte_l))
        o_.append(texte("titre", (x + 32, y + 8), libelle, "legende", D.GRIS))
        x += 32 + mesure.mesure(libelle, fontes["legende"]) + 40

    #  ------------------------------------------------------------  échelle
    axe, graduations = [], []
    bas = Y_PREMIERE + (len(OFFRES) - 1) * PAS + HAUTEUR_BARRE + 26
    for e in range(0, int(maxi) + 1, 5):
        gx = X_BARRE + e * echelle
        axe.append(trait("échelle", [gx, Y_PREMIERE - 16, gx, bas],
                         D.FILET, 1))
        graduations.append(texte("échelle", (gx, bas + 8), "%d €" % e,
                                 "echelle", D.FAIBLE, centre=True))
    o_.extend(axe)
    o_.extend(graduations)

    #  -------------------------------------------------------------  barres
    noms, barres, valeurs, facteurs = [], [], [], []
    for i, o in enumerate(OFFRES):
        yb = Y_PREMIERE + i * PAS
        meme = abs(o["facteur"] - 1.0) < 1e-9

        noms.append(texte("noms", (X_NOM, yb + 1), o["nom"], "nom", D.ENCRE))
        noms.append(texte("noms", (X_NOM, yb + 24), D.typo(o["offre"]),
                          "offre", D.FAIBLE))

        le = o["ensuite"] * echelle
        la = o["appel"] * echelle
        barres.append(rect("barres", [X_BARRE, yb, X_BARRE + le,
                                      yb + HAUTEUR_BARRE], 6, INDIGO))
        if not meme:
            barres.append(rect("barres", [X_BARRE, yb, X_BARRE + la,
                                          yb + HAUTEUR_BARRE], 6,
                               INDIGO_PALE))

        valeurs.append(texte("valeurs", (X_BARRE + le + 12, yb + 6),
                             euros(o["ensuite"]), "valeur", INDIGO))
        if not meme:
            #  Le prix d'appel se pose juste après sa barre, à l'intérieur
            #  de la barre pleine : il y a toujours la place, puisque la
            #  barre pâle est par construction la plus courte.
            lab = euros(o["appel"])
            place = le - la - 16
            if mesure.mesure(lab, fontes["appel"]) > place:
                raise SystemExit(
                    "%s : le prix d'appel ne tient pas dans l'écart entre "
                    "les deux barres" % o["nom"])
            valeurs.append(texte("valeurs", (X_BARRE + la + 10, yb + 7),
                                 lab, "appel", D.BLANC))

        if meme:
            facteurs.append(texte("facteurs", (X_FACTEUR, yb + 4),
                                  "même prix", "offre", D.GRIS))
        else:
            facteurs.append(texte("facteurs", (X_FACTEUR, yb + 2),
                                  "x %s" % ("%.1f" % o["facteur"])
                                  .replace(".", ","), "facteur", D.ENCRE))

    o_.extend(barres)
    o_.extend(noms)
    o_.extend(valeurs)
    o_.extend(facteurs)

    H = int(bas + 56)
    o_.insert(0, rect("fond", [0, 0, L, H], 0, D.PAPIER))
    return H, o_


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
                        "hebergement-prix-renouvellement")
    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5),
               ("indigo", INDIGO, 4.5))

    H, ordres = composer()
    rendre_matriciel(H, ordres, base)
    couches, textes = rendre_svg(H, ordres, base)

    print("  %-44s %.0f Ko"
          % (os.path.basename(base + ".svg"),
             os.path.getsize(base + ".svg") / 1024.0))
    print("  %d x %d, %d calques, %d textes" % (L, H, couches, textes))
    print()
    for o in OFFRES:
        trois = (o["appel"] * min(o["mois_appel"] or 36, 36)
                 + o["ensuite"] * max(0, 36 - min(o["mois_appel"] or 36, 36)))
        print("  %-12s %-16s %6s vers %7s   x%-5.2f   %7.2f € sur 3 ans"
              % (o["nom"], o["offre"], euros(o["appel"]),
                 euros(o["ensuite"]), o["facteur"], trois))


if __name__ == "__main__":
    principal()
