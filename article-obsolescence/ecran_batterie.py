"""
L'écran État de la batterie d'un iPhone, redessiné et annoté.

    python3 article-obsolescence/ecran_batterie.py

Produit `obsolescence-etat-batterie.webp`, son PNG et le SVG éditable.

----------------------------------------------------------------------------
UN REDESSIN, ET IL DOIT SE VOIR QUE C'EN EST UN
----------------------------------------------------------------------------
Le brief demande une capture « stylisée ». C'est la bonne façon de poser la
question, et la réponse suit : on ne fabrique pas une image qui pourrait
passer pour une photographie d'écran.

La figure est donc dessinée dans la typographie et la palette des autres
figures de l'article, pas dans celles du système. Les libellés courts sont
ceux que le lecteur lira vraiment sur son appareil, sans quoi la figure ne
servirait à rien ; les paragraphes d'explication d'Apple sont RÉSUMÉS et
non recopiés, et le pied de figure le dit.

La distinction n'est pas juridique, elle est éditoriale : une illustration
annonce ce qu'elle est, un faux compte sur le fait qu'on ne regarde pas.

----------------------------------------------------------------------------
LA VALEUR AFFICHÉE EST UN EXEMPLE, ET LE CODE LE SAIT
----------------------------------------------------------------------------
Il faut bien qu'un chiffre s'affiche à l'écran. Celui-ci est choisi juste
sous les 80 % que cite l'article, pour que la figure montre le cas dont
parle le texte. Un contrôle refuse de dessiner si la valeur passait
au-dessus du seuil : la capture illustrerait alors une situation que le
paragraphe voisin ne décrit pas.

----------------------------------------------------------------------------
LA FIGURE PORTE L'AVERTISSEMENT, PAS SEULEMENT LE MODE D'EMPLOI
----------------------------------------------------------------------------
L'article consacre un paragraphe entier à dire de NE PAS désactiver la
gestion des performances sur une batterie usée. Une figure qui montrerait
le lien « Désactiver » sans cet avertissement inviterait exactement au
geste que le texte déconseille, et les images circulent sans leur article.
L'avertissement est donc l'une des quatre annotations, et il est repris en
pied.
"""

import os

import charte as C
import dessin as D

L = 1600
MARGE = 56

VIOLET = (98, 44, 200)
AMBRE = (180, 83, 9)
BLEU = (22, 104, 184)
VERT = (12, 124, 92)

#  La valeur montrée à l'écran. Elle illustre le cas de l'article, batterie
#  sous le seuil, et le contrôle de `composer` s'en assure.
CAPACITE = 79
SEUIL = 80

POLICES = {
    "titre": (C.POLICE_G, 19, "bold"),
    "sous": (C.POLICE_R, 17, "normal"),
    "note": (C.POLICE_G, 16, "bold"),
    "corps": (C.POLICE_R, 15, "normal"),
    "pied": (C.POLICE_R, 16, "normal"),
    #  Les fontes de l'écran redessiné, volontairement celles des figures.
    "barre": (C.POLICE_G, 12, "bold"),
    "nav": (C.POLICE_R, 13, "normal"),
    "navtitre": (C.POLICE_G, 14, "bold"),
    "section": (C.POLICE_R, 10, "normal"),
    "ligne": (C.POLICE_R, 13, "normal"),
    "valeur": (C.POLICE_G, 13, "bold"),
    "explique": (C.POLICE_R, 10, "normal"),
    "lien": (C.POLICE_R, 13, "normal"),
}
FAMILLE_SVG = "Liberation Sans, Arial, Helvetica, sans-serif"

TITRE = "OÙ LIRE L’ÉTAT RÉEL DE LA BATTERIE"
SOUS = ("Réglages, Batterie, État de la batterie : la capacité maximale et "
        "la gestion des performances, sur un redessin de l’écran")

#  Le téléphone. La hauteur n'est PAS une constante : elle se déduit du
#  contenu à la fin du tracé. Fixée à la main, elle laissait deux cents
#  pixels d'écran vide sous la dernière section, ce qui donne l'air d'une
#  maquette bâclée plutôt que d'une page de réglages.
TEL = [630, 168, 970, None]
MARGE_BASSE = 78
RAYON = 40
MARGE_ECRAN = 9

#  Les deux colonnes d'annotations.
X_GAUCHE = (MARGE, 570)
X_DROITE = (1030, L - MARGE)


def rect(couche, b, r, teinte):
    return {"quoi": "rect", "couche": couche, "b": b, "r": r, "t": teinte}


def cadre(couche, b, r, teinte, epaisseur=2):
    return {"quoi": "cadre", "couche": couche, "b": b, "r": r, "t": teinte,
            "e": epaisseur}


def trait(couche, b, teinte, epaisseur):
    return {"quoi": "trait", "couche": couche, "b": b, "t": teinte,
            "e": epaisseur}


def disque(couche, cx, cy, r, teinte, contour=None):
    return {"quoi": "disque", "couche": couche, "cx": cx, "cy": cy, "r": r,
            "t": teinte, "contour": contour}


def texte(couche, xy, contenu, police, teinte, tracking=0.0, centre=False,
          droite=False):
    for c, nom in (("—", "cadratin"), ("–", "demi-cadratin")):
        if c in contenu:
            raise SystemExit("%s dans « %s »" % (nom, contenu[:60]))
    return {"quoi": "texte", "couche": couche, "xy": xy, "c": contenu,
            "p": police, "t": teinte, "tr": tracking, "centre": centre,
            "droite": droite}


def coude(couche, depart, pivot_x, arrivee, teinte):
    """Un rappel en trois segments : horizontal, vertical, horizontal.

    Un trait droit entre une carte et un point d'écran passe en diagonale à
    travers le dessin et croise les autres. Le coude reste dans les marges
    qu'on lui donne et ne coupe jamais le téléphone.
    """
    x0, y0 = depart
    x1, y1 = arrivee
    return [trait(couche, [x0, y0, pivot_x, y0], teinte, 2),
            trait(couche, [pivot_x, y0, pivot_x, y1], teinte, 2),
            trait(couche, [pivot_x, y1, x1, y1], teinte, 2),
            disque(couche, x1, y1, 4, teinte)]


def composer():
    mesure = D.Toile(L, 10)
    fontes = {k: mesure.police(f, t) for k, (f, t, _) in POLICES.items()}

    #  CONTRÔLE : la figure illustre le cas décrit par l'article, une
    #  batterie SOUS le seuil. Au-dessus, elle montrerait autre chose que
    #  le paragraphe d'à côté.
    if CAPACITE >= SEUIL:
        raise SystemExit(
            "la capacité montrée est de %d %%, au-dessus du seuil de %d %% "
            "que cite l'article" % (CAPACITE, SEUIL))

    o = []
    o.append(texte("titre", (MARGE, 46), TITRE, "titre", D.ENCRE, 2.2))
    sous = D.typo(SOUS)
    if mesure.mesure(sous, fontes["sous"]) > L - 2 * MARGE:
        raise SystemExit("le sous-titre déborde")
    o.append(texte("titre", (MARGE, 74), sous, "sous", D.FAIBLE))
    o.append(trait("titre", [MARGE, 124, L - MARGE, 124], D.FILET, 2))

    # ------------------------------------------------------------  l'écran
    #
    #  Le contenu est composé d'abord, dans sa propre liste, parce que la
    #  hauteur du châssis en dépend. Les deux listes sont ensuite remises
    #  dans le bon ordre de tracé, le châssis dessous.
    x0, y0, x1, _ = TEL
    ex0, ey0 = x0 + MARGE_ECRAN, y0 + MARGE_ECRAN
    ex1 = x1 - MARGE_ECRAN
    ecran = []
    o_reel, o = o, ecran

    g = ex0 + 16          # marge de texte à gauche de l'écran
    d = ex1 - 16          # et à droite
    largeur = d - g

    #  Barre d'état, réduite à ce qu'elle est : une heure et une pile.
    o.append(texte("écran", (g + 6, ey0 + 12), "10:24", "barre", D.ENCRE))
    o.append(cadre("écran", [d - 30, ey0 + 12, d - 8, ey0 + 24], 3,
                   D.FAIBLE, 1))
    o.append(rect("écran", [d - 28, ey0 + 14, d - 16, ey0 + 22], 1, D.GRIS))

    #  Barre de navigation.
    y_nav = ey0 + 52
    o.append(texte("écran", (g, y_nav), "‹  Batterie", "nav", BLEU))
    o.append(texte("écran", ((ex0 + ex1) / 2.0, y_nav - 1),
                   "État de la batterie", "navtitre", D.ENCRE, centre=True))
    o.append(trait("écran", [ex0, y_nav + 26, ex1, y_nav + 26],
                   (219, 219, 226), 1))

    y = y_nav + 48

    def entete(libelle, y):
        o.append(texte("écran", (g, y), libelle.upper(), "section", D.FAIBLE))
        return y + 16

    def carte(y, hauteur):
        o.append(rect("écran", [ex0 + 8, y, ex1 - 8, y + hauteur], 10,
                      D.BLANC))
        return y

    #  ---- capacité maximale
    y = entete("Capacité maximale", y)
    haut_carte = y
    y = carte(y, 108)
    o.append(texte("écran", (g, y + 14), "Capacité maximale", "ligne",
                   D.ENCRE))
    o.append(texte("écran", (d, y + 14), "%d %%" % CAPACITE, "valeur",
                   D.ENCRE, droite=True))
    o.append(trait("écran", [g, y + 40, ex1 - 8, y + 40], (228, 228, 234), 1))
    explique = ("Mesure de la capacité actuelle par rapport à celle d’une "
                "batterie neuve. Une capacité plus faible réduit l’autonomie "
                "entre deux recharges.")
    lignes = mesure.couper(D.typo(explique), fontes["explique"], largeur)
    if len(lignes) > 4:
        raise SystemExit("l'explication de capacité déborde de sa carte")
    for i, ligne in enumerate(lignes):
        o.append(texte("écran", (g, y + 52 + i * 14), ligne, "explique",
                       D.GRIS))
    y_capacite = y + 22
    y += 108 + 26

    #  ---- capacité de performance maximale
    y = entete("Capacité de performance maximale", y)
    y_perf = y
    y = carte(y, 152)
    avertit = ("Cet appareil s’est éteint de façon inopinée : la batterie ne "
               "fournissait plus la puissance demandée. La gestion des "
               "performances a été appliquée pour éviter que cela se "
               "reproduise.")
    lignes = mesure.couper(D.typo(avertit), fontes["explique"], largeur)
    if len(lignes) > 6:
        raise SystemExit("l'explication de performance déborde de sa carte")
    for i, ligne in enumerate(lignes):
        o.append(texte("écran", (g, y + 14 + i * 14), ligne, "explique",
                       D.GRIS))
    y_lien = y + 118
    o.append(trait("écran", [g, y_lien - 12, ex1 - 8, y_lien - 12],
                   (228, 228, 234), 1))
    o.append(texte("écran", (g, y_lien), "Désactiver", "lien", BLEU))
    y += 152 + 26

    #  ---- recharge optimisée
    y = entete("Recharge", y)
    y = carte(y, 52)
    o.append(texte("écran", (g, y + 18), "Recharge optimisée", "ligne",
                   D.ENCRE))
    o.append(rect("écran", [d - 38, y + 14, d, y + 36], 11, VERT))
    o.append(disque("écran", d - 11, y + 25, 9, D.BLANC))

    #  La hauteur du châssis découle enfin du dernier élément dessiné.
    bas_contenu = y + 52
    y1 = bas_contenu + MARGE_BASSE
    TEL[3] = y1
    ey1 = y1 - MARGE_ECRAN
    o = o_reel
    o.append(rect("téléphone", TEL, RAYON, (232, 233, 238)))
    o.append(cadre("téléphone", TEL, RAYON, (198, 200, 209), 2))
    o.append(rect("téléphone", [ex0, ey0, ex1, ey1], RAYON - 8,
                  (241, 241, 245)))
    o.extend(ecran)

    # -------------------------------------------------------  annotations
    notes = (
        {"cote": "gauche", "y": 186, "ancre": (x0, y_nav),
         "teinte": VIOLET,
         "titre": "Deux menus, pas trois",
         "corps": "Réglages, puis Batterie, puis État de la batterie. "
                  "C’est tout le chemin."},
        {"cote": "gauche", "y": 336, "ancre": (x0, y_capacite),
         "teinte": VIOLET,
         "titre": "La seule valeur à regarder",
         "corps": "Sous %d %%, une batterie neuve transforme l’appareil, et "
                  "elle coûte le dixième d’un téléphone." % SEUIL},
        {"cote": "droite", "y": 186, "ancre": (x1, y_perf + 40),
         "teinte": AMBRE,
         "titre": "Cette section n’apparaît pas toujours",
         "corps": "Elle ne s’affiche que si un arrêt inopiné a déjà eu lieu "
                  "et que la gestion des performances a été appliquée."},
        {"cote": "droite", "y": 372, "ancre": (x1, y_lien + 4),
         "teinte": AMBRE,
         "titre": "Ne désactivez pas sur une batterie usée",
         "corps": "Ce réglage évite les extinctions brutales. Le couper sur "
                  "une batterie très dégradée les fait revenir. Changez la "
                  "batterie d’abord, décochez ensuite."},
    )

    pivots = {0: x0 - 30, 1: x0 - 46, 2: x1 + 46, 3: x1 + 30}
    cartes = []
    for i, n in enumerate(notes):
        gx0, gx1 = X_GAUCHE if n["cote"] == "gauche" else X_DROITE
        largeur_note = gx1 - gx0
        lignes = mesure.couper(D.typo(n["corps"]), fontes["corps"],
                               largeur_note - 36)
        if len(lignes) > 4:
            raise SystemExit("l'annotation « %s » tient en %d lignes"
                             % (n["titre"], len(lignes)))
        hauteur = 22 + 24 + 8 + len(lignes) * 21 + 20
        cartes.append((n, gx0, gx1, lignes, hauteur))

    #  CONTRÔLE : deux annotations d'une même colonne ne doivent pas se
    #  chevaucher. Un dépassement de quelques pixels ne se voit pas sur la
    #  vignette et saute aux yeux en pleine page.
    for cote in ("gauche", "droite"):
        colonne = [(n["y"], n["y"] + h) for n, _, _, _, h in cartes
                   if n["cote"] == cote]
        for (a0, a1), (b0, b1) in zip(colonne, colonne[1:]):
            if b0 < a1 + 12:
                raise SystemExit(
                    "deux annotations se chevauchent à gauche/droite : "
                    "%d..%d puis %d" % (a0, a1, b0))

    for i, (n, gx0, gx1, lignes, hauteur) in enumerate(cartes):
        b = [gx0, n["y"], gx1, n["y"] + hauteur]
        o.append(rect("annotations", b, 10, D.BLANC))
        o.append(cadre("annotations", b, 10, n["teinte"], 2))

    for i, (n, gx0, gx1, lignes, hauteur) in enumerate(cartes):
        x = gx0 + 18
        y = n["y"] + 18
        o.append(texte("notes", (x, y), D.typo(n["titre"]), "note",
                       n["teinte"]))
        y += 30
        for ligne in lignes:
            o.append(texte("notes", (x, y), ligne, "corps", D.GRIS))
            y += 21

    for i, (n, gx0, gx1, lignes, hauteur) in enumerate(cartes):
        depart = (gx1, n["y"] + hauteur / 2.0) if n["cote"] == "gauche" \
            else (gx0, n["y"] + hauteur / 2.0)
        o.extend(coude("rappels", depart, pivots[i], n["ancre"],
                       n["teinte"]))

    # --------------------------------------------------------------  pied
    pied = (
        "Redessin stylisé, pas une capture d’écran. Les libellés courts sont "
        "ceux de l’écran français, sans quoi la figure ne servirait à rien ; "
        "les explications d’Apple sont résumées, et la typographie est celle "
        "des figures de l’article.",
        "La valeur de %d %% est un exemple, choisie juste sous le seuil de "
        "%d %% que cite l’article. Votre appareil affichera la sienne, et "
        "c’est elle qui compte." % (CAPACITE, SEUIL),
        "La section « capacité de performance maximale » et son lien "
        "« Désactiver » n’apparaissent qu’après un arrêt inopiné. Sur une "
        "batterie très dégradée, désactiver rend les pics de puissance au "
        "processeur et les extinctions reviennent.",
    )
    bas = max(y1, max(n["y"] + h for n, _, _, _, h in cartes))
    y_pied = bas + 38
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
            t.disque(a["cx"], a["cy"], a["r"], teinte=a["t"],
                     contour=a["contour"], epaisseur=2)
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
                out.append('    <line x1="%g" y1="%g" x2="%g" y2="%g" '
                           'stroke="%s" stroke-width="%g"/>'
                           % (x0, y0, x1, y1, teinte(a["t"]), a["e"]))
            elif a["quoi"] == "disque":
                bord = ('' if not a["contour"] else
                        ' stroke="%s" stroke-width="2"' % teinte(a["contour"]))
                out.append('    <circle cx="%g" cy="%g" r="%g" fill="%s"%s/>'
                           % (a["cx"], a["cy"], a["r"], teinte(a["t"]), bord))
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
                        "obsolescence-etat-batterie")
    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5),
               ("violet", VIOLET, 4.5), ("ambre", AMBRE, 4.5),
               ("bleu", BLEU, 4.5), ("vert", VERT, 4.5))

    H, ordres = composer()
    rendre_matriciel(H, ordres, base)
    couches, textes = rendre_svg(H, ordres, base)

    print("  %-44s %.0f Ko"
          % (os.path.basename(base + ".svg"),
             os.path.getsize(base + ".svg") / 1024.0))
    print("  %d calques, %d textes" % (couches, textes))
    print("  capacité montrée %d %%, seuil de l'article %d %%"
          % (CAPACITE, SEUIL))


if __name__ == "__main__":
    principal()
