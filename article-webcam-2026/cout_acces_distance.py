"""
Ce que coûte un an d'Agent DVR, et à partir de quand.

    python3 article-webcam-2026/cout_acces_distance.py

Produit `agent-dvr-cout-acces-distance.webp`, son PNG et le SVG éditable.

----------------------------------------------------------------------------
LA FIGURE MONTRE UNE MARCHE, PAS QUATRE PRIX
----------------------------------------------------------------------------
Les quatre formules ne sont pas quatre points d'un même continuum. Entre
la gratuite et la première payante il y a une frontière, et c'est celle
de l'article : chez toi, ou de dehors. La gratuite n'a donc pas de barre
du tout, et un filet la sépare des trois autres. Une barre de hauteur
nulle se serait lue comme une valeur manquante.

----------------------------------------------------------------------------
LES TOTAUX NE SONT PAS RECOPIÉS, ILS SONT CALCULÉS
----------------------------------------------------------------------------
Seuls les tarifs mensuels relevés chez l'éditeur sont écrits dans ce
fichier. Les 95,40 $, 179,40 $ et 239,40 $ de l'article sont le produit
par douze, refait à chaque dessin. Si l'éditeur change un tarif, il n'y a
qu'un nombre à corriger, et la figure ne peut pas se contredire.

----------------------------------------------------------------------------
PAS DE TAPO C200 SUR CET AXE
----------------------------------------------------------------------------
L'article compare l'abonnement à une caméra à 33 €. La comparaison est
juste, mais l'axe est en dollars : poser 33 € dessus demanderait un taux
de change que l'article ne donne pas, et ferait dire à la figure plus
qu'elle ne sait. La comparaison reste dans le texte, où elle est assumée.
"""

import os

import charte as C
import dessin as D

L = 1600
MARGE = 56

INDIGO = C.VIOLET_TEXTE
INDIGO_PLEIN = (108, 56, 212)

#  ---------------------------------------------------------------------------
#  LES QUATRE FORMULES
#
#  `mois` est le tarif mensuel relevé le 12 octobre 2026 sur la page des
#  formules de l'éditeur. `distance` dit si la formule ouvre l'accès
#  depuis l'extérieur : c'est la marche que la figure doit montrer.
#  ---------------------------------------------------------------------------
FORMULES = (
    {"nom": "Gratuit", "mois": 0.0, "distance": False},
    {"nom": "Basic", "mois": 7.95, "distance": True},
    {"nom": "Standard", "mois": 14.95, "distance": True},
    {"nom": "Professional", "mois": 19.95, "distance": True},
)

MOIS = 12

#  Ce que l'article annonce, et que le calcul doit retrouver.
ANNONCES = {"Gratuit": 0.0, "Basic": 95.40, "Standard": 179.40,
            "Professional": 239.40}

POLICES = {
    "titre": (C.POLICE_G, 19, "bold"),
    "sous": (C.POLICE_R, 17, "normal"),
    "nom": (C.POLICE_G, 19, "bold"),

    "valeur": (C.POLICE_G, 19, "bold"),
    "mensuel": (C.POLICE_R, 15, "normal"),
    "bascule": (C.POLICE_G, 14, "bold"),
    "note": (C.POLICE_R, 14, "normal"),
}
FAMILLE_SVG = "Liberation Sans, Arial, Helvetica, sans-serif"

TITRE = "GRATUIT CHEZ SOI, 95,40 $ L’AN POUR REGARDER DE DEHORS"
SOUS = ("coût sur douze mois des formules Agent DVR, au tarif mensuel relevé "
        "le 12 octobre 2026")
BASCULE = "dès qu’on veut voir ses caméras hors du réseau local"
NOTE = ("Tarifs mensuels. L’éditeur propose aussi un paiement annuel, avec "
        "licence locale perpétuelle.")

Y0 = 168                  # haut de la première ligne
H_LIGNE = 78
H_BASCULE = 50            # la bande du filet et de sa phrase
H_BARRE = 34
X_NOM = MARGE
X_BARRE = 352
X_FIN = L - MARGE - 22


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


def dollars(v):
    """239.4 donne « 239,40 $ », et 0 donne « 0 $ »."""
    if v == 0:
        return "0 $"
    return ("%.2f" % v).replace(".", ",") + " $"


def composer():
    mesure = D.Toile(L, 10)
    fontes = {k: mesure.police(f, t) for k, (f, t, _) in POLICES.items()}

    #  ------------------------------------------------------------------
    #  CONTRÔLES
    #  ------------------------------------------------------------------
    annuel = {f["nom"]: f["mois"] * MOIS for f in FORMULES}
    for nom, attendu in ANNONCES.items():
        if abs(annuel[nom] - attendu) > 0.005:
            raise SystemExit("l'article annonce %s pour « %s », douze "
                             "mensualités en font %s"
                             % (dollars(attendu), nom, dollars(annuel[nom])))

    for a, b in zip(FORMULES, FORMULES[1:]):
        if b["mois"] <= a["mois"]:
            raise SystemExit("« %s » n'est pas plus chère que « %s »"
                             % (b["nom"], a["nom"]))

    #  La marche doit exister et être unique : une seule formule gratuite,
    #  et toutes les payantes ouvrent l'accès à distance.
    gratuites = [f for f in FORMULES if f["mois"] == 0]
    if len(gratuites) != 1 or gratuites[0]["distance"]:
        raise SystemExit("la figure raconte une marche entre le local et le "
                         "distant : il faut exactement une formule gratuite, "
                         "et elle ne donne pas l'accès à distance")
    if not all(f["distance"] for f in FORMULES if f["mois"] > 0):
        raise SystemExit("une formule payante n'ouvre pas l'accès à "
                         "distance : la marche n'est plus au bon endroit")

    plafond = max(annuel.values())
    echelle = (X_FIN - X_BARRE) / plafond

    o = []
    o.append(texte("titre", (MARGE, 46), D.typo(TITRE), "titre", D.ENCRE,
                   2.2))
    sous = D.typo(SOUS)
    if mesure.mesure(sous, fontes["sous"]) > L - 2 * MARGE:
        raise SystemExit("le sous-titre déborde")
    o.append(texte("titre", (MARGE, 74), sous, "sous", D.FAIBLE))

    #  ------------------------------------------------------------  lignes
    filets, barres, noms, valeurs = [], [], [], []
    premiere_payante = None

    #  Les formules payantes sont décalées vers le bas, pour ménager la
    #  bande où tient la bascule : son filet et sa phrase.
    rang_payant = next(i for i, f in enumerate(FORMULES) if f["mois"] > 0)

    for i, f in enumerate(FORMULES):
        y = Y0 + i * H_LIGNE + (H_BASCULE if i >= rang_payant else 0)
        total = annuel[f["nom"]]
        yb = y + 24                       # haut de la barre

        if f["mois"] > 0 and premiere_payante is None:
            premiere_payante = y

        #  Premier jet : le tarif mensuel posé après la barre. Chez
        #  Professional, dont la barre touche le bord du cadre, il finissait
        #  cent pixels dehors. Il est donc passé sous le nom, où la place
        #  ne dépend pas de la longueur de la barre.
        mention = (D.typo("pas d’abonnement") if f["mois"] == 0
                   else "%s par mois" % dollars(f["mois"]))
        noms.append(texte("libelles", (X_NOM, y), D.typo(f["nom"]),
                          "nom", D.ENCRE))
        noms.append(texte("libelles", (X_NOM, y + 26), mention,
                          "mensuel", D.GRIS))
        if mesure.mesure(mention, fontes["mensuel"]) > X_BARRE - X_NOM - 24:
            raise SystemExit("« %s » mord sur la colonne des barres"
                             % mention)

        if f["mois"] == 0:
            #  Pas de barre : la valeur se pose seule au départ de l'axe,
            #  là où les autres commencent.
            #  Un petit trait marque le départ de l'axe : sans lui,
            #  le « 0 $ » flotterait sans point d'appui.
            barres.append(trait("barres", [X_BARRE, yb, X_BARRE,
                                           yb + H_BARRE], D.FILET, 3))
            valeurs.append(texte("valeurs", (X_BARRE + 14, yb + 7),
                                 dollars(total), "valeur", INDIGO))
            continue

        lb = total * echelle
        barres.append(rect("barres", [X_BARRE, yb, X_BARRE + lb,
                                      yb + H_BARRE], 5, INDIGO_PLEIN))

        #  La valeur se range dans la barre, calée sur sa droite. Si elle
        #  n'y tient pas, mieux vaut s'arrêter que la laisser déborder.
        lab = dollars(total)
        large = mesure.mesure(lab, fontes["valeur"])
        if large > lb - 28:
            raise SystemExit("« %s » fait %d px pour une barre de %d px"
                             % (lab, large, lb))
        valeurs.append(texte("valeurs",
                             (X_BARRE + lb - 14 - large, yb + 7), lab,
                             "valeur", D.BLANC))

    if premiere_payante is None:
        raise SystemExit("aucune formule payante : il n'y a plus de marche")

    #  --------------------------------------------------------  la bascule
    #  Un filet et une phrase, dans la bande ménagée juste au-dessus de la
    #  première formule payante : c'est tout ce que la figure ajoute.
    yf = premiere_payante - H_BASCULE + 6
    filets.append(trait("bascule", [MARGE, yf, L - MARGE, yf], D.FILET, 1))
    bas = D.typo(BASCULE)
    filets.append(texte("bascule", (MARGE, yf + 7), bas, "bascule", INDIGO))
    if mesure.mesure(bas, fontes["bascule"]) > L - 2 * MARGE:
        raise SystemExit("« %s » déborde du cadre" % bas)

    o.extend(filets)
    o.extend(barres)
    o.extend(noms)
    o.extend(valeurs)

    bas_figure = Y0 + len(FORMULES) * H_LIGNE + H_BASCULE
    note = D.typo(NOTE)
    if mesure.mesure(note, fontes["note"]) > L - 2 * MARGE:
        raise SystemExit("la note déborde")
    o.append(texte("note", (MARGE, bas_figure + 8), note, "note", D.FAIBLE))

    H = int(bas_figure + 60)
    o.insert(0, rect("fond", [0, 0, L, H], 0, D.PAPIER))
    return H, o, annuel


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
                        "agent-dvr-cout-acces-distance")
    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5),
               ("indigo", INDIGO, 4.5))
    r = C.contraste(D.BLANC, INDIGO_PLEIN)
    print("  %-8s %-16s %.2f:1  %s"
          % ("blanc", str(INDIGO_PLEIN), r, "ok" if r >= 4.5 else "INSUFFISANT"))
    if r < 4.5:
        raise SystemExit("blanc sur barre : %.2f:1, sous le seuil" % r)

    H, ordres, annuel = composer()
    rendre_matriciel(H, ordres, base)
    couches, textes = rendre_svg(H, ordres, base)

    print()
    print("  %-38s %.0f Ko"
          % (os.path.basename(base + ".svg"),
             os.path.getsize(base + ".svg") / 1024.0))
    print("  %d x %d, %d calques, %d textes" % (L, H, couches, textes))
    print()
    for f in FORMULES:
        print("  %-14s %8s par mois   %10s sur %d mois"
              % (f["nom"], dollars(f["mois"]), dollars(annuel[f["nom"]]),
                 MOIS))


if __name__ == "__main__":
    principal()
