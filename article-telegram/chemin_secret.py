"""
Le chemin vers une conversation secrète sur Telegram, en quatre écrans.

    python3 article-telegram/chemin_secret.py

Produit `telegram-chemin-conversation-secrete.webp`, son PNG et le SVG.

----------------------------------------------------------------------------
UN REDESSIN, ET IL S'ANNONCE COMME TEL
----------------------------------------------------------------------------
Même règle que pour la figure de l'écran batterie : le brief demande une
capture « stylisée », donc on ne fabrique pas une image qui pourrait passer
pour une photographie d'écran. Typographie et palette sont celles des
figures de l'article, pas celles de l'application ; seuls les libellés que
le lecteur devra reconnaître sont ceux du produit.

----------------------------------------------------------------------------
LA FIGURE COMPTE LES MANIPULATIONS, C'EST SON SUJET
----------------------------------------------------------------------------
L'article reproche à Telegram d'enfouir sa seule option réellement chiffrée
« au moins quatre manipulations » plus loin. Une figure qui montrerait le
résultat sans montrer le chemin raterait le propos : ce n'est pas l'écran
final qui est intéressant, c'est sa distance.

Les quatre écrans sont donc dessinés côte à côte, numérotés, et le nombre
d'étapes est contrôlé contre ce que le texte annonce. Si un écran était
ajouté ou retiré, le rendu s'arrêterait plutôt que de laisser la figure
contredire la phrase qu'elle illustre.

----------------------------------------------------------------------------
LE MODE D'EMPLOI PORTE SA LIMITE, SINON IL INDUIT EN ERREUR
----------------------------------------------------------------------------
L'article consacre une section entière à dire que ce chemin ne mène JAMAIS
à un groupe : « Vous n'avez pas sécurisé votre groupe, et vous ne pouvez
pas le faire. » Une marche à suivre publiée sans cette limite ferait
exactement le contraire de ce que le texte cherche, puisque le lecteur
pressé retiendrait qu'il existe une procédure.

La limite est donc dans la figure, en bandeau sous les quatre écrans, et
pas seulement dans le pied.
"""

import os

import charte as C
import dessin as D

L = 1600
MARGE = 56

VIOLET = (98, 44, 200)
AMBRE = (180, 83, 9)
VERT = (12, 124, 92)

#  Ce que l'article annonce, et que la figure doit montrer.
ETAPES_ANNONCEES = 4

POLICES = {
    "titre": (C.POLICE_G, 19, "bold"),
    "sous": (C.POLICE_R, 17, "normal"),
    "num": (C.POLICE_G, 17, "bold"),
    "legende": (C.POLICE_R, 15, "normal"),
    "bandeau": (C.POLICE_G, 17, "bold"),
    "pied": (C.POLICE_R, 16, "normal"),
    #  Les fontes de l'écran redessiné.
    "nav": (C.POLICE_G, 14, "bold"),
    "ligne": (C.POLICE_R, 13, "normal"),
    "note": (C.POLICE_R, 11, "normal"),
}
FAMILLE_SVG = "Liberation Sans, Arial, Helvetica, sans-serif"

TITRE = "QUATRE MANIPULATIONS POUR UN TÊTE-À-TÊTE"
SOUS = ("le chemin vers une conversation secrète sur Telegram, redessiné ; "
        "c’est la seule option chiffrée de bout en bout de l’application")

#  ---------------------------------------------------------------------------
#  LES QUATRE ÉCRANS
#
#  `lignes` décrit le contenu : un libellé, ou None pour une ligne muette
#  faite de deux barres grises, comme une discussion dont le nom n'importe
#  pas ici. `vise` désigne l'élément sur lequel on appuie.
#  ---------------------------------------------------------------------------
ECRANS = (
    {"nav": "Discussions", "retour": False, "crayon": True,
     "lignes": [None, None, None, None],
     "vise": "crayon",
     "legende": "Onglet Discussions, toucher l’icône de nouveau message, "
                "en haut à droite."},

    {"nav": "Nouveau message", "retour": True, "crayon": False,
     "lignes": ["Nouveau groupe", "Nouvelle conversation secrète",
                "Nouvelle chaîne", None, None],
     "vise": 1,
     "legende": "Dans la liste qui s’ouvre, choisir Nouvelle conversation "
                "secrète."},

    {"nav": "Conversation secrète", "retour": True, "crayon": False,
     "lignes": [None, None, None, None, None],
     "vise": 1,
     "legende": "Choisir le correspondant. Un seul : la fonction ne connaît "
                "pas les groupes."},

    {"nav": "Conversation secrète", "retour": True, "crayon": False,
     "cadenas": True,
     "lignes": [],
     "vise": None,
     "legende": "La conversation s’ouvre, marquée d’un cadenas. Elle exige "
                "que vous soyez connectés tous les deux."},
)

BANDEAU = ("Ce chemin ne mène jamais à un groupe ni à un canal, et aucun "
           "réglage ne permet de l’y ajouter.")

#  Géométrie.
ECART = 38
Y_ECRAN = 200
HAUTEUR_LIGNE = 46
#  La hauteur n'est pas une constante : elle se déduit du panneau le plus
#  rempli. Fixée à la main, elle laissait deux cents pixels de blanc sous
#  les listes courtes, ce qui donne l'air d'écrans vides plutôt que
#  d'écrans cadrés.
MARGE_BASSE = 24


def rect(couche, b, r, teinte):
    return {"quoi": "rect", "couche": couche, "b": b, "r": r, "t": teinte}


def cadre(couche, b, r, teinte, epaisseur=2):
    return {"quoi": "cadre", "couche": couche, "b": b, "r": r, "t": teinte,
            "e": epaisseur}


def trait(couche, b, teinte, epaisseur):
    return {"quoi": "trait", "couche": couche, "b": b, "t": teinte,
            "e": epaisseur}


def disque(couche, cx, cy, r, teinte, contour=None, epaisseur=2):
    return {"quoi": "disque", "couche": couche, "cx": cx, "cy": cy, "r": r,
            "t": teinte, "contour": contour, "e": epaisseur}


def polygone(couche, points, teinte):
    return {"quoi": "polygone", "couche": couche, "pts": points, "t": teinte}


def texte(couche, xy, contenu, police, teinte, tracking=0.0, centre=False):
    for c, nom in (("—", "cadratin"), ("–", "demi-cadratin")):
        if c in contenu:
            raise SystemExit("%s dans « %s »" % (nom, contenu[:60]))
    return {"quoi": "texte", "couche": couche, "xy": xy, "c": contenu,
            "p": police, "t": teinte, "tr": tracking, "centre": centre}


def composer():
    mesure = D.Toile(L, 10)
    fontes = {k: mesure.police(f, t) for k, (f, t, _) in POLICES.items()}

    #  CONTRÔLE : la figure illustre une phrase qui compte les étapes. Si
    #  le nombre d'écrans changeait, la figure contredirait le texte.
    if len(ECRANS) != ETAPES_ANNONCEES:
        raise SystemExit(
            "l'article annonce %d manipulations, la figure en montre %d"
            % (ETAPES_ANNONCEES, len(ECRANS)))

    largeur = (L - 2 * MARGE - (len(ECRANS) - 1) * ECART) / float(len(ECRANS))

    #  Le panneau le plus rempli fixe la hauteur commune. Le quatrième
    #  écran ne porte pas de liste mais un bloc de texte, mesuré à part.
    bas = [54 + len(e["lignes"]) * HAUTEUR_LIGNE for e in ECRANS]
    note = ("Les messages de cette conversation sont chiffrés de "
            "bout en bout.")
    for e in ECRANS:
        if e.get("cadenas"):
            n = len(mesure.couper(D.typo(note), fontes["note"],
                                  largeur - 56))
            bas.append(96 + 58 + n * 15)
    HAUTEUR_ECRAN = int(max(bas)) + MARGE_BASSE
    Y_LEGENDE = Y_ECRAN + HAUTEUR_ECRAN + 26

    o = []
    o.append(texte("titre", (MARGE, 46), TITRE, "titre", D.ENCRE, 2.2))
    sous = D.typo(SOUS)
    if mesure.mesure(sous, fontes["sous"]) > L - 2 * MARGE:
        raise SystemExit("le sous-titre déborde")
    o.append(texte("titre", (MARGE, 74), sous, "sous", D.FAIBLE))
    o.append(trait("titre", [MARGE, 124, L - MARGE, 124], D.FILET, 2))

    ecrans, reperes, legendes = [], [], []
    for i, e in enumerate(ECRANS):
        x0 = MARGE + i * (largeur + ECART)
        x1 = x0 + largeur
        b = [x0, Y_ECRAN, x1, Y_ECRAN + HAUTEUR_ECRAN]
        ecrans.append(rect("écrans", b, 14, D.BLANC))
        ecrans.append(cadre("écrans", b, 14, D.FILET, 2))

        g, d = x0 + 16, x1 - 16

        #  Barre de navigation.
        y_nav = Y_ECRAN + 26
        if e["retour"]:
            ecrans.append(texte("écrans", (g, y_nav), "‹", "nav", VIOLET))
        ecrans.append(texte("écrans", ((x0 + x1) / 2.0, y_nav),
                            D.typo(e["nav"]), "nav", D.ENCRE, centre=True))
        if e.get("crayon"):
            #  UN CRAYON, PAS UNE CROIX.
            #
            #  Deux rectangles perpendiculaires donnaient un signe plus, qui
            #  se lit « ajouter » et non « écrire ». Le corps du crayon est
            #  donc un quadrilatère incliné et sa pointe un triangle, ce qui
            #  demande un ordre de tracé polygonal.
            cx, cy = d - 12, y_nav + 1
            ecrans.append(polygone("écrans", [
                (cx - 2, cy + 9), (cx + 7, cy - 9), (cx + 11, cy - 7),
                (cx + 2, cy + 11)], VIOLET))
            ecrans.append(polygone("écrans", [
                (cx - 4, cy + 12), (cx - 2, cy + 8), (cx + 1, cy + 10)],
                D.ENCRE))
        ecrans.append(trait("écrans", [x0, Y_ECRAN + 54, x1, Y_ECRAN + 54],
                            (228, 228, 234), 1))

        #  Corps.
        y = Y_ECRAN + 54
        hauteur_ligne = HAUTEUR_LIGNE
        for j, ligne in enumerate(e["lignes"]):
            cy = y + hauteur_ligne / 2.0
            if ligne is None:
                ecrans.append(disque("écrans", g + 15, cy, 15,
                                     (226, 226, 233)))
                ecrans.append(rect("écrans", [g + 42, cy - 10, g + 130,
                                              cy - 2], 4, (222, 222, 230)))
                ecrans.append(rect("écrans", [g + 42, cy + 3, g + 184,
                                              cy + 9], 3, (234, 234, 240)))
            else:
                ecrans.append(texte("écrans", (g + 8, cy - 9), D.typo(ligne),
                                    "ligne", D.ENCRE))
            if j + 1 < len(e["lignes"]):
                ecrans.append(trait("écrans", [g, y + hauteur_ligne, x1,
                                               y + hauteur_ligne],
                                    (234, 234, 240), 1))
            y += hauteur_ligne

        #  Le quatrième écran montre la conversation elle-même.
        if e.get("cadenas"):
            cy = Y_ECRAN + 96
            ecrans.append(disque("écrans", g + 22, cy, 22, (226, 240, 234)))
            ecrans.append(rect("écrans", [g + 16, cy - 4, g + 28, cy + 8],
                               2, VERT))
            ecrans.append(rect("écrans", [g + 19, cy - 11, g + 25, cy - 3],
                               3, VERT))
            ecrans.append(texte("écrans", (g + 56, cy - 18), "Correspondant",
                                "nav", D.ENCRE))
            ecrans.append(texte("écrans", (g + 56, cy + 4),
                                "conversation secrète", "note", VERT))
            lignes = mesure.couper(D.typo(note), fontes["note"], d - g - 24)
            fond = [g, cy + 52, d, cy + 58 + len(lignes) * 15]
            ecrans.append(rect("écrans", fond, 8, (236, 246, 241)))
            for k, l in enumerate(lignes):
                ecrans.append(texte("écrans", (g + 12, cy + 58 + k * 15), l,
                                    "note", VERT))

        #  Le repère sur l'élément qu'on touche.
        if e["vise"] == "crayon":
            reperes.append(disque("repères", d - 12, y_nav + 1, 19, None,
                                  contour=AMBRE, epaisseur=3))
        elif isinstance(e["vise"], int):
            cy = Y_ECRAN + 54 + e["vise"] * hauteur_ligne
            reperes.append(cadre("repères", [g - 6, cy + 3, d + 6,
                                             cy + hauteur_ligne - 3], 8,
                                 AMBRE, 3))

        #  Pastille numérotée, posée à cheval sur le coin de l'écran.
        reperes.append(disque("repères", x0 + 2, Y_ECRAN + 2, 19, VIOLET))
        reperes.append(texte("repères", (x0 + 2, Y_ECRAN - 9), str(i + 1),
                             "num", D.BLANC, centre=True))

        #  Légende sous l'écran.
        lignes = mesure.couper(D.typo(e["legende"]), fontes["legende"],
                               largeur - 4)
        if len(lignes) > 3:
            raise SystemExit("la légende de l'écran %d tient en %d lignes"
                             % (i + 1, len(lignes)))
        for k, l in enumerate(lignes):
            legendes.append(texte("légendes", (x0, Y_LEGENDE + k * 22), l,
                                  "legende", D.GRIS))

    o.extend(ecrans)
    o.extend(reperes)
    o.extend(legendes)

    #  ------------------------------------------------------------  bandeau
    y_bandeau = Y_LEGENDE + 3 * 22 + 22
    b = [MARGE, y_bandeau, L - MARGE, y_bandeau + 58]
    o.append(rect("bandeau", b, 10, (250, 240, 228)))
    o.append(cadre("bandeau", b, 10, AMBRE, 2))
    bandeau = D.typo(BANDEAU)
    if mesure.mesure(bandeau, fontes["bandeau"]) > L - 2 * MARGE - 80:
        raise SystemExit("le bandeau déborde")
    o.append(texte("bandeau", (L / 2.0, y_bandeau + 19), bandeau, "bandeau",
                   AMBRE, centre=True))

    # --------------------------------------------------------------  pied
    pied = (
        "Redessin stylisé, pas une capture d’écran. La typographie et la "
        "palette sont celles des figures de l’article ; seuls les libellés "
        "que vous devrez reconnaître sont ceux de l’application.",
        "Quatre manipulations, et elles n’ouvrent jamais qu’un tête-à-tête. "
        "Le chiffrement de bout en bout n’existe ni pour les groupes ni pour "
        "les canaux, et cela ne se règle pas : cela se conçoit.",
        "La conversation secrète exige en outre que les deux correspondants "
        "soient connectés au même moment. Une conversation ordinaire, elle, "
        "passe par les serveurs de l’entreprise dans un format qu’elle peut "
        "lire.",
    )
    y_pied = y_bandeau + 58 + 34
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
                     contour=a["contour"], epaisseur=a["e"])
        elif a["quoi"] == "polygone":
            t.polygone(a["pts"], a["t"])
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
                           'stroke="%s" stroke-width="%g"/>'
                           % (x0, y0, x1, y1, teinte(a["t"]), a["e"]))
            elif a["quoi"] == "polygone":
                out.append('    <polygon points="%s" fill="%s"/>'
                           % (" ".join("%g,%g" % p for p in a["pts"]),
                              teinte(a["t"])))
            elif a["quoi"] == "disque":
                remplissage = ('none' if a["t"] is None
                               else teinte(a["t"]))
                bord = ('' if not a["contour"] else
                        ' stroke="%s" stroke-width="%g"'
                        % (teinte(a["contour"]), a["e"]))
                out.append('    <circle cx="%g" cy="%g" r="%g" fill="%s"%s/>'
                           % (a["cx"], a["cy"], a["r"], remplissage, bord))
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
                        "telegram-chemin-conversation-secrete")
    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5),
               ("violet", VIOLET, 4.5), ("ambre", AMBRE, 4.5),
               ("vert", VERT, 4.5))

    H, ordres = composer()
    rendre_matriciel(H, ordres, base)
    couches, textes = rendre_svg(H, ordres, base)

    print("  %-46s %.0f Ko"
          % (os.path.basename(base + ".svg"),
             os.path.getsize(base + ".svg") / 1024.0))
    print("  %d calques, %d textes" % (couches, textes))
    print("  %d écrans, contre %d manipulations annoncées par l'article"
          % (len(ECRANS), ETAPES_ANNONCEES))


if __name__ == "__main__":
    principal()
