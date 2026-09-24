"""
Les demandes judiciaires françaises satisfaites par Telegram en 2024.

    python3 article-telegram/demandes_2024.py

Produit `telegram-demandes-france-2024.webp`, son PNG et le SVG éditable.

----------------------------------------------------------------------------
LES BARRES OCCUPENT LEUR TRIMESTRE, ET C'EST CE QUI PERMET LES REPÈRES
----------------------------------------------------------------------------
Un histogramme ordinaire pose quatre barres également espacées et laisse le
lecteur deviner ce qu'il y a entre elles. Ici les barres couvrent la DURÉE
de leur trimestre, bord à bord, ce qui transforme l'axe des abscisses en
axe du temps.

Le bénéfice est immédiat : les deux repères se posent à leur date réelle et
non « quelque part sur la troisième barre ». L'arrestation du 24 août tombe
au jour 55 sur 92 du trimestre, la réécriture des conditions du 22 septembre
au jour 84. Les deux fractions sont calculées, pas placées à l'oeil, et un
contrôle vérifie qu'elles tombent bien dans le troisième trimestre.

----------------------------------------------------------------------------
L'ÉCHELLE EST LINÉAIRE, ET LES DEUX PREMIÈRES BARRES SONT DONC INVISIBLES
----------------------------------------------------------------------------
Quatre et six contre six cent soixante-treize : à l'échelle, les deux
premières barres font trois et cinq pixels. La tentation est de passer en
échelle logarithmique, ou de leur imposer une hauteur minimale « pour
qu'on les voie ».

Les deux trahiraient la figure. Le log écrase précisément l'écart qui est
le sujet ; une hauteur plancher fabrique une proportion qui n'existe pas,
et rien sur l'image ne signalerait le trucage. On garde donc le linéaire,
on écrit les valeurs au-dessus des barres, et le pied prévient que ces
deux trois pixels ne sont pas un défaut de tracé.

----------------------------------------------------------------------------
DEUX DÉCOMPTES QUI NE SE CONFONDENT PAS
----------------------------------------------------------------------------
Le tableau de l'article compte des DEMANDES satisfaites, et leur somme fait
893. La phrase qui suit cite 2 072 UTILISATEURS concernés : ce n'est pas le
même objet, une demande pouvant viser plusieurs comptes. La figure ne
mélange donc pas les deux, elle titre sur les demandes et signale l'autre
décompte en pied.
"""

import datetime as dt
import os

import charte as C
import dessin as D

L = 1600
MARGE = 56

VIOLET = (98, 44, 200)
AMBRE = (180, 83, 9)

#  ---------------------------------------------------------------------------
#  LES QUATRE TRIMESTRES, TELS QUE LES RAPPORTS DE TELEGRAM LES DONNENT
#  ---------------------------------------------------------------------------
TRIMESTRES = (
    {"nom": "T1 2024", "debut": dt.date(2024, 1, 1), "valeur": 4},
    {"nom": "T2 2024", "debut": dt.date(2024, 4, 1), "valeur": 6},
    {"nom": "T3 2024", "debut": dt.date(2024, 7, 1), "valeur": 210},
    {"nom": "T4 2024", "debut": dt.date(2024, 10, 1), "valeur": 673},
)
FIN = dt.date(2025, 1, 1)

#  Les deux événements datés de l'article. Le second n'est pas au brief ;
#  il y est parce que c'est lui qui explique la bascule, et qu'il tombe dans
#  le même trimestre que l'arrestation.
#  LE PLUS RÉCENT EST LE PLUS HAUT, ET CE N'EST PAS UN CAPRICE.
#
#  Les étiquettes sont posées à gauche de leur pointillé. Avec le 24 août
#  en haut, son trait descendait jusqu'à la base et traversait l'étiquette
#  du 22 septembre, posée plus bas. En remontant le repère le plus à
#  DROITE, chaque étiquette se retrouve à gauche de tous les traits encore
#  tracés à sa hauteur. Un contrôle le vérifie plus bas.
REPERES = (
    {"date": dt.date(2024, 8, 24), "haut": 392,
     "titre": "Arrestation de Durov, 24 août",
     "detail": "interpellé au Bourget, mis en examen quatre jours plus tard"},
    {"date": dt.date(2024, 9, 22), "haut": 306,
     "titre": "Réécriture des conditions, 22 septembre",
     "detail": "le partage aux autorités passe du seul terrorisme à toute "
               "activité criminelle"},
)

#  L'autre décompte cité par l'article, qui n'est pas celui du graphique.
UTILISATEURS = 2072

POLICES = {
    "titre": (C.POLICE_G, 19, "bold"),
    "sous": (C.POLICE_R, 17, "normal"),
    "valeur": (C.POLICE_G, 22, "bold"),
    "petite": (C.POLICE_G, 17, "bold"),
    "axe": (C.POLICE_R, 14, "normal"),
    "grad": (C.POLICE_R, 13, "normal"),
    "repere": (C.POLICE_G, 15, "bold"),
    "detail": (C.POLICE_R, 13, "normal"),
    "stat": (C.POLICE_G, 26, "bold"),
    "statnom": (C.POLICE_R, 14, "normal"),
    "pied": (C.POLICE_R, 16, "normal"),
}
FAMILLE_SVG = "Liberation Sans, Arial, Helvetica, sans-serif"

TITRE = "DIX DEMANDES AU PREMIER SEMESTRE, 883 AU SECOND"
SOUS = ("demandes judiciaires françaises satisfaites par Telegram en 2024, "
        "par trimestre, d’après ses propres rapports de transparence")

#  Le cadre du graphique.
X0, X1 = 112, 1188
BASE = 736
SOMMET = 208
ECART_BARRE = 7

#  La colonne des trois chiffres.
X_STAT = 1262


def nombre(n):
    """Un entier à la française, espace insécable pour les milliers."""
    t = "%d" % n
    return t if len(t) <= 3 else t[:-3] + " " + t[-3:]


def rect(couche, b, r, teinte):
    return {"quoi": "rect", "couche": couche, "b": b, "r": r, "t": teinte}


def cadre(couche, b, r, teinte, epaisseur=2):
    return {"quoi": "cadre", "couche": couche, "b": b, "r": r, "t": teinte,
            "e": epaisseur}


def trait(couche, b, teinte, epaisseur, pointille=False):
    return {"quoi": "trait", "couche": couche, "b": b, "t": teinte,
            "e": epaisseur, "pointille": pointille}


def disque(couche, cx, cy, r, teinte):
    return {"quoi": "disque", "couche": couche, "cx": cx, "cy": cy, "r": r,
            "t": teinte}


def texte(couche, xy, contenu, police, teinte, tracking=0.0, centre=False,
          droite=False):
    for c, nom in (("—", "cadratin"), ("–", "demi-cadratin")):
        if c in contenu:
            raise SystemExit("%s dans « %s »" % (nom, contenu[:60]))
    return {"quoi": "texte", "couche": couche, "xy": xy, "c": contenu,
            "p": police, "t": teinte, "tr": tracking, "centre": centre,
            "droite": droite}


def composer():
    mesure = D.Toile(L, 10)
    fontes = {k: mesure.police(f, t) for k, (f, t, _) in POLICES.items()}

    #  ------------------------------------------------------------------
    #  TOUT SE DÉDUIT DES QUATRE VALEURS
    #  ------------------------------------------------------------------
    total = sum(t["valeur"] for t in TRIMESTRES)
    semestre_1 = TRIMESTRES[0]["valeur"] + TRIMESTRES[1]["valeur"]
    semestre_2 = TRIMESTRES[2]["valeur"] + TRIMESTRES[3]["valeur"]
    facteur = semestre_2 / float(semestre_1)
    part_t4 = 100.0 * TRIMESTRES[3]["valeur"] / total

    #  CONTRÔLE : le titre affirme deux nombres, ils doivent venir des
    #  quatre valeurs et non d'une saisie parallèle.
    #
    #  Le contrôle accepte le chiffre ET les lettres : un titre qui écrit
    #  « dix » plutôt que « 10 » n'est pas moins exact, et forcer le
    #  chiffre pour satisfaire un test serait laisser le test décider de
    #  la typographie.
    LETTRES = {4: "QUATRE", 6: "SIX", 10: "DIX", 210: "DEUX CENT DIX"}

    def porte(valeur):
        formes = {str(valeur), nombre(valeur),
                  nombre(valeur).replace("\u00a0", " "),
                  LETTRES.get(valeur, "")}
        return any(f and f in TITRE for f in formes)

    for attendu in (semestre_1, semestre_2):
        if not porte(attendu):
            raise SystemExit(
                "le titre ne porte plus le semestre calculé : %d manque"
                % attendu)

    debut, fin = TRIMESTRES[0]["debut"], FIN
    jours = (fin - debut).days

    def abscisse(date):
        return X0 + (date - debut).days / float(jours) * (X1 - X0)

    #  CONTRÔLE : les repères doivent tomber dans le trimestre annoncé.
    t3_debut, t3_fin = TRIMESTRES[2]["debut"], TRIMESTRES[3]["debut"]
    for r in REPERES:
        if not t3_debut <= r["date"] < t3_fin:
            raise SystemExit(
                "le repère « %s » est daté du %s, hors du troisième trimestre"
                % (r["titre"], r["date"]))

    maximum = max(t["valeur"] for t in TRIMESTRES)
    hauteur = BASE - SOMMET

    def ordonnee(v):
        return BASE - v / float(maximum) * hauteur

    o = []
    o.append(texte("titre", (MARGE, 46), TITRE, "titre", D.ENCRE, 2.2))
    sous = D.typo(SOUS)
    if mesure.mesure(sous, fontes["sous"]) > L - 2 * MARGE:
        raise SystemExit("le sous-titre déborde")
    o.append(texte("titre", (MARGE, 74), sous, "sous", D.FAIBLE))
    o.append(trait("titre", [MARGE, 124, L - MARGE, 124], D.FILET, 2))

    #  ------------------------------------------------------------  grille
    for v in (0, 200, 400, 600):
        y = ordonnee(v)
        o.append(trait("grille", [X0, y, X1, y], D.FILET,
                       2 if v == 0 else 1))
        o.append(texte("grille", (X0 - 14, y - 9), nombre(v), "grad",
                       D.FAIBLE, droite=True))

    #  ------------------------------------------------------------  barres
    for i, t in enumerate(TRIMESTRES):
        suivant = TRIMESTRES[i + 1]["debut"] if i + 1 < len(TRIMESTRES) else FIN
        gx0 = abscisse(t["debut"]) + ECART_BARRE / 2.0
        gx1 = abscisse(suivant) - ECART_BARRE / 2.0
        gy = ordonnee(t["valeur"])
        o.append(rect("barres", [gx0, gy, gx1, BASE], 0, VIOLET))
        #  La valeur au-dessus : sans elle, quatre et six ne se lisent pas.
        police = "valeur" if t["valeur"] >= 100 else "petite"
        o.append(texte("barres", ((gx0 + gx1) / 2.0, gy - 32), nombre(
            t["valeur"]), police, VIOLET, centre=True))
        o.append(texte("axe", ((gx0 + gx1) / 2.0, BASE + 14), t["nom"],
                       "axe", D.GRIS, centre=True))

    #  -----------------------------------------------------------  repères
    #
    #  CONTRÔLE : aucune étiquette ne doit chevaucher le pointillé d'un
    #  AUTRE repère. Un trait qui traverse un mot ne se voit pas sur la
    #  vignette et saute aux yeux en pleine page.
    for r in REPERES:
        gauche = min(
            abscisse(r["date"]) - 12
            - mesure.mesure(D.typo(r[cle]), fontes[police])
            for cle, police in (("titre", "repere"), ("detail", "detail")))
        for autre in REPERES:
            if autre is r:
                continue
            ax = abscisse(autre["date"])
            couvre = autre["haut"] <= r["haut"] + 26
            if couvre and gauche <= ax <= abscisse(r["date"]):
                raise SystemExit(
                    "l'étiquette « %s » est traversée par le pointillé du "
                    "%s" % (r["titre"], autre["date"]))

    for r in REPERES:
        x = abscisse(r["date"])
        o.append(trait("repères", [x, BASE, x, r["haut"]], AMBRE, 2,
                       pointille=True))
        o.append(disque("repères", x, r["haut"], 5, AMBRE))
        o.append(texte("repères", (x - 12, r["haut"] - 10),
                       D.typo(r["titre"]), "repere", AMBRE, droite=True))
        detail = D.typo(r["detail"])
        largeur = mesure.mesure(detail, fontes["detail"])
        if x - 12 - largeur < MARGE:
            raise SystemExit("le détail du repère « %s » sort du cadre"
                             % r["titre"])
        o.append(texte("repères", (x - 12, r["haut"] + 12), detail, "detail",
                       D.GRIS, droite=True))

    #  ----------------------------------------------------------  chiffres
    stats = (
        (nombre(semestre_1), "demandes au premier semestre"),
        (nombre(semestre_2), "demandes au second"),
        ("× %.0f" % facteur, "entre les deux semestres"),
    )
    y = 224
    for valeur, libelle in stats:
        o.append(texte("chiffres", (X_STAT, y), valeur, "stat", VIOLET))
        lignes = mesure.couper(libelle, fontes["statnom"],
                               L - MARGE - X_STAT)
        if len(lignes) > 2:
            raise SystemExit("le libellé « %s » tient en %d lignes"
                             % (libelle, len(lignes)))
        for j, ligne in enumerate(lignes):
            o.append(texte("chiffres", (X_STAT, y + 38 + j * 20), ligne,
                           "statnom", D.GRIS))
        y += 38 + len(lignes) * 20 + 40

    # --------------------------------------------------------------  pied
    pied = (
        "Les deux premières barres mesurent trois et cinq pixels de haut. "
        "Ce n’est pas un défaut de tracé, c’est l’échelle : %d et %d demandes "
        "contre %d. Passer en logarithmique écraserait justement l’écart qui "
        "est le sujet." % (TRIMESTRES[0]["valeur"], TRIMESTRES[1]["valeur"],
                           TRIMESTRES[3]["valeur"]),
        "Chaque barre occupe la durée de son trimestre, ce qui fait de l’axe "
        "un axe du temps et permet de poser les deux repères à leur date "
        "réelle. L’arrestation tombe au jour 55 sur 92 du troisième "
        "trimestre, la réécriture des conditions au jour 84.",
        "Total 2024 : %d demandes satisfaites, dont %.0f %% sur le seul "
        "quatrième trimestre. L’article cite par ailleurs %s utilisateurs "
        "concernés, qui est un autre décompte : une demande peut viser "
        "plusieurs comptes." % (total, part_t4, nombre(UTILISATEURS)),
    )
    y_pied = max(BASE + 54, y) + 16
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
    return H, o, (total, semestre_1, semestre_2, facteur, part_t4)


def rendre_matriciel(H, ordres, base):
    t = D.Toile(L, H)
    fontes = {k: t.police(f, taille) for k, (f, taille, _) in POLICES.items()}
    for a in ordres:
        if a["quoi"] == "rect":
            t.rrect(a["b"], a["r"], teinte=a["t"])
        elif a["quoi"] == "cadre":
            t.rrect(a["b"], a["r"], contour=a["t"], epaisseur=a["e"])
        elif a["quoi"] == "trait":
            if a["pointille"]:
                x0, y0, x1, y1 = a["b"]
                t.pointilles([(x0, y0), (x1, y1)], a["t"], a["e"])
            else:
                t.ligne(a["b"], a["t"], a["e"])
        elif a["quoi"] == "disque":
            t.disque(a["cx"], a["cy"], a["r"], teinte=a["t"])
        else:
            f = fontes[a["p"]]
            x, y = a["xy"]
            if a["centre"]:
                x -= t.mesure(a["c"], f) / 2.0
            elif a["droite"]:
                x -= t.mesure(a["c"], f)
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
                tirets = ' stroke-dasharray="9 7"' if a["pointille"] else ""
                out.append('    <line x1="%g" y1="%g" x2="%g" y2="%g" '
                           'stroke="%s" stroke-width="%g"%s/>'
                           % (x0, y0, x1, y1, teinte(a["t"]), a["e"], tirets))
            elif a["quoi"] == "disque":
                out.append('    <circle cx="%g" cy="%g" r="%g" fill="%s"/>'
                           % (a["cx"], a["cy"], a["r"], teinte(a["t"])))
            else:
                _, taille, graisse = POLICES[a["p"]]
                espacement = (' letter-spacing="%g"' % a["tr"]
                              if a["tr"] else "")
                ancre = (' text-anchor="middle"' if a["centre"]
                         else ' text-anchor="end"' if a["droite"] else "")
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
                        "telegram-demandes-france-2024")
    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5),
               ("violet", VIOLET, 4.5), ("ambre", AMBRE, 4.5))

    H, ordres, chiffres = composer()
    rendre_matriciel(H, ordres, base)
    couches, textes = rendre_svg(H, ordres, base)
    total, s1, s2, facteur, part = chiffres

    print("  %-44s %.0f Ko"
          % (os.path.basename(base + ".svg"),
             os.path.getsize(base + ".svg") / 1024.0))
    print("  %d calques, %d textes" % (couches, textes))
    print()
    for t in TRIMESTRES:
        print("  %-9s %4d demandes" % (t["nom"], t["valeur"]))
    print()
    print("  total %d   semestres %d puis %d   facteur %.1f"
          % (total, s1, s2, facteur))
    print("  le T4 pèse %.1f %% de l'année" % part)
    print("  autre décompte cité par l'article : %s utilisateurs"
          % nombre(UTILISATEURS))


if __name__ == "__main__":
    principal()
