"""
La chaîne de blocs : chaque bloc reprend l'empreinte du précédent.

    python3 article-bitcoin/chaine_blocs.py

Produit `bitcoin-chaine-de-blocs.webp`, son PNG et le SVG éditable.

----------------------------------------------------------------------------
LES EMPREINTES SONT CALCULÉES, PAS DESSINÉES
----------------------------------------------------------------------------
Il aurait été facile d'écrire quatre suites hexadécimales plausibles et de
tirer des flèches entre elles. La figure serait fausse au sens qui compte :
elle affirmerait un mécanisme sans le faire tourner, et rien ne garantirait
que la valeur inscrite dans un bloc soit vraiment celle du bloc d'avant.

Ici, chaque empreinte sort d'un vrai SHA-256 calculé sur le contenu du bloc
et l'empreinte du précédent, exactement comme le fait Bitcoin. Conséquence
directe : la deuxième rangée n'est pas une mise en scène. On change une
transaction dans le bloc n, on relance le calcul, et la valeur affichée
change RÉELLEMENT. Les ruptures que la figure montre sont des ruptures
mesurées, et trois contrôles les vérifient avant le tracé.

----------------------------------------------------------------------------
DEUX RANGÉES, PARCE QUE LA CASSE NE SE VOIT QUE PAR COMPARAISON
----------------------------------------------------------------------------
Une seule rangée de blocs chaînés montre un principe ; elle ne montre pas
ce que le brief demande, à savoir qu'une modification casse la suite. La
figure pose donc la même chaîne deux fois, intacte puis retouchée, aux
mêmes positions. L'oeil descend et voit quels champs ont bougé.

----------------------------------------------------------------------------
LA TEINTE EST CELLE DE LA CHARTE, ET ELLE EST PRESQUE SEULE
----------------------------------------------------------------------------
Tout le schéma est dans l'indigo Pixfeed : cartes blanches, filets fins,
valeurs et flèches en VIOLET_TEXTE. Une seule autre teinte apparaît, et
seulement en trait, jamais en aplat : ALERTE, sur les deux liens rompus et
sur le champ modifié. La charte la réserve aux figures qui opposent un état
sain à un état dégradé, et précise qu'elle ne sert jamais de décor. Une
chaîne cassée est exactement ce cas ; l'employer ailleurs dans cette figure
la viderait de son sens.
"""

import hashlib
import os

import charte as C
import dessin as D

L = 1600
MARGE = 56

INDIGO = C.VIOLET_TEXTE       # les valeurs et les flèches
INDIGO_APLAT = C.VIOLET       # les pastilles
ALERTE = C.ALERTE             # uniquement ce qui est rompu

#  ---------------------------------------------------------------------------
#  LA CHAÎNE
#
#  `contenu` est ce que le bloc transporte. `retouche` est la version que
#  l'attaquant y substitue dans la deuxième rangée. Rien d'autre n'est saisi :
#  les empreintes sortent du calcul.
#  ---------------------------------------------------------------------------
BLOCS = (
    {"nom": "Bloc n", "contenu": "184 transactions", "retouche": None},
    {"nom": "Bloc n + 1", "contenu": "212 transactions", "retouche": None},
    {"nom": "Bloc n + 2", "contenu": "97 transactions", "retouche": None},
)
#  Le bloc que l'attaquant retouche, et par quoi.
CIBLE = 0
RETOUCHE = "184 transactions, dont une réécrite"

#  La racine est elle aussi une vraie empreinte : afficher un libellé
#  tronqué en « empreinte … » dans une colonne de valeurs hexadécimales
#  faisait tache et laissait croire à un champ manquant.
RACINE = hashlib.sha256(b"bloc n - 1").hexdigest()

POLICES = {
    "titre": (C.POLICE_G, 19, "bold"),
    "sous": (C.POLICE_R, 17, "normal"),
    "rangee": (C.POLICE_G, 13, "bold"),
    "bloc": (C.POLICE_G, 18, "bold"),
    "champ": (C.POLICE_R, 13, "normal"),
    "valeur": (C.POLICE_G, 15, "bold"),
    "contenu": (C.POLICE_R, 15, "normal"),
    "note": (C.POLICE_R, 13, "normal"),
    "pied": (C.POLICE_R, 16, "normal"),
}
MONO = "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"
POLICES["valeur"] = (MONO, 15, "bold")
FAMILLE_SVG = "Liberation Sans, Arial, Helvetica, sans-serif"
FAMILLE_MONO = "Liberation Mono, Consolas, monospace"

TITRE = "CHANGER UN BLOC ANCIEN CASSE TOUS LES SUIVANTS"
SOUS = ("chaque bloc reprend l’empreinte du précédent ; les valeurs "
        "ci-dessous sont calculées en SHA-256, pas inventées")

LARGEUR_BLOC = 408
ECART = 96
Y_RANGEE = (196, 512)
HAUTEUR_BLOC = 208


def empreinte(precedent, contenu):
    """Le SHA-256 du bloc, sur son contenu ET l'empreinte du précédent.

    C'est ce chaînage-là qui fait tout : l'empreinte d'un bloc dépend de
    tout ce qui le précède, donc toucher au passé change tout l'aval.
    """
    graine = "%s|%s" % (precedent, contenu)
    return hashlib.sha256(graine.encode("utf-8")).hexdigest()


def court(h):
    """Dix caractères, parce que soixante-quatre ne tiennent pas."""
    return h[:10] + "…"


def chainer(contenus, racine):
    """Rend la liste des (empreinte reprise, empreinte produite)."""
    suite, precedent = [], racine
    for c in contenus:
        produite = empreinte(precedent, c)
        suite.append((precedent, produite))
        precedent = produite
    return suite


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


def polygone(couche, points, teinte):
    return {"quoi": "polygone", "couche": couche, "pts": points, "t": teinte}


def texte(couche, xy, contenu, police, teinte, tracking=0.0, centre=False):
    for c, nom in (("—", "cadratin"), ("–", "demi-cadratin")):
        if c in contenu:
            raise SystemExit("%s dans « %s »" % (nom, contenu[:60]))
    return {"quoi": "texte", "couche": couche, "xy": xy, "c": contenu,
            "p": police, "t": teinte, "tr": tracking, "centre": centre}


def fleche(couche, depart, arrivee, teinte, casse=False):
    """Le lien entre deux blocs : sort d'en bas, entre en haut.

    Le champ « donne » est le dernier d'une carte, le champ « reprend » le
    premier de la suivante : le trait doit donc remonter. Un coude à trois
    segments reste lisible là où une diagonale couperait les deux cartes.
    """
    x0, y0 = depart
    x1, y1 = arrivee
    milieu = (x0 + x1) / 2.0
    ops = [trait(couche, [x0, y0, milieu, y0], teinte, 3, casse),
           trait(couche, [milieu, y0, milieu, y1], teinte, 3, casse),
           trait(couche, [milieu, y1, x1 - 11, y1], teinte, 3, casse),
           polygone(couche, [(x1, y1), (x1 - 12, y1 - 6), (x1 - 12, y1 + 6)],
                    teinte)]
    if casse:
        #  La rupture : une croix posée sur le coude, en trait seulement.
        ops += [trait(couche, [milieu - 11, (y0 + y1) / 2.0 - 11,
                               milieu + 11, (y0 + y1) / 2.0 + 11], teinte, 3),
                trait(couche, [milieu - 11, (y0 + y1) / 2.0 + 11,
                               milieu + 11, (y0 + y1) / 2.0 - 11], teinte, 3)]
    return ops


def composer():
    mesure = D.Toile(L, 10)
    fontes = {k: mesure.police(f, t) for k, (f, t, _) in POLICES.items()}

    contenus = [b["contenu"] for b in BLOCS]
    intacte = chainer(contenus, RACINE)

    retouches = list(contenus)
    retouches[CIBLE] = RETOUCHE
    #  L'attaquant modifie le contenu, mais il ne peut pas réécrire ce que
    #  les blocs suivants ont DÉJÀ inscrit : leur champ « reprend » garde
    #  l'ancienne valeur. C'est là que la chaîne rompt.
    cassee = []
    for i, c in enumerate(retouches):
        reprend = intacte[i][0]
        cassee.append((reprend, empreinte(reprend, c)))

    #  ------------------------------------------------------------------
    #  CONTRÔLES
    #  ------------------------------------------------------------------
    for i in range(1, len(BLOCS)):
        if intacte[i][0] != intacte[i - 1][1]:
            raise SystemExit(
                "chaîne intacte incohérente au bloc %d : le champ repris ne "
                "vaut pas l'empreinte du précédent" % i)
    if cassee[CIBLE][1] == intacte[CIBLE][1]:
        raise SystemExit(
            "la retouche ne change pas l'empreinte du bloc visé : elle ne "
            "démontre rien")
    #  UN SEUL LIEN ROMPT, ET C'EST LE BON.
    #
    #  Premier jet : le contrôle exigeait que TOUS les liens en aval soient
    #  rompus, et il a refusé de dessiner. Il avait raison, c'est moi qui
    #  me trompais de mécanisme. La retouche ne casse que la couture entre
    #  le bloc visé et le suivant : les blocs d'après restent cohérents
    #  ENTRE EUX, puisque ni leur contenu ni ce qu'ils ont inscrit n'a
    #  bougé. Ce qui les condamne n'est pas la retouche, c'est la
    #  réparation : refaire le bloc n + 1 change son empreinte, donc casse
    #  le n + 2, et ainsi de suite. La figure doit dire cela, pas autre
    #  chose.
    if cassee[CIBLE + 1][0] == cassee[CIBLE][1]:
        raise SystemExit(
            "le lien du bloc %d au bloc %d devrait être rompu et ne l'est pas"
            % (CIBLE + 1, CIBLE + 2))
    for i in range(CIBLE + 2, len(BLOCS)):
        if cassee[i][0] != cassee[i - 1][1]:
            raise SystemExit(
                "le lien vers le bloc %d est présenté comme rompu alors que "
                "la retouche ne l'atteint pas" % (i + 1))
    if court(intacte[CIBLE][1]) == court(cassee[CIBLE][1]):
        raise SystemExit(
            "les deux empreintes du bloc visé sont identiques une fois "
            "tronquées : la figure ne montrerait pas la différence")

    o = []
    o.append(texte("titre", (MARGE, 46), TITRE, "titre", D.ENCRE, 2.2))
    sous = D.typo(SOUS)
    if mesure.mesure(sous, fontes["sous"]) > L - 2 * MARGE:
        raise SystemExit("le sous-titre déborde")
    o.append(texte("titre", (MARGE, 74), sous, "sous", D.FAIBLE))
    o.append(trait("titre", [MARGE, 124, L - MARGE, 124], D.FILET, 2))

    rangees = (
        {"y": Y_RANGEE[0], "suite": intacte, "contenus": contenus,
         "nom": "LA CHAÎNE INTACTE", "casse": False},
        {"y": Y_RANGEE[1], "suite": cassee, "contenus": retouches,
         "nom": "APRÈS UNE RETOUCHE DU BLOC n", "casse": True},
    )

    cartes, liens, textes_ = [], [], []
    for r in rangees:
        y = r["y"]
        textes_.append(texte("rangées", (MARGE, y - 26), r["nom"], "rangee",
                             D.GRIS))
        for i, b in enumerate(BLOCS):
            x0 = MARGE + i * (LARGEUR_BLOC + ECART)
            x1 = x0 + LARGEUR_BLOC
            #  Trois états : intact, retouché, à refaire. Le troisième
            #  n'est pas cassé, il est condamné par la réparation du
            #  premier, et la nuance est tout le propos.
            retouche = r["casse"] and i == CIBLE
            a_refaire = r["casse"] and i > CIBLE
            bord = ALERTE if retouche else D.FILET

            cartes.append(rect("blocs", [x0, y, x1, y + HAUTEUR_BLOC], 12,
                               D.BLANC))
            cartes.append(cadre("blocs", [x0, y, x1, y + HAUTEUR_BLOC], 12,
                                bord, 2))
            if a_refaire:
                etiquette = "à refaire"
                largeur_e = mesure.mesure(etiquette, fontes["champ"]) + 24
                cartes.append(cadre("blocs", [x1 - largeur_e - 18, y + 16,
                                              x1 - 18, y + 42], 13,
                                    ALERTE, 2))
                textes_.append(texte("blocs",
                                     (x1 - largeur_e / 2.0 - 18, y + 22),
                                     etiquette, "champ", ALERTE, centre=True))

            g = x0 + 22
            textes_.append(disque("blocs", g + 13, y + 30, 13, INDIGO_APLAT))
            textes_.append(texte("blocs", (g + 13, y + 21), str(i + 1),
                                 "rangee", D.BLANC, centre=True))
            textes_.append(texte("blocs", (g + 38, y + 20), b["nom"], "bloc",
                                 INDIGO))

            reprend, produite = r["suite"][i]
            #  Seul le bloc juste après la retouche porte une empreinte
            #  reprise qui ne correspond plus.
            lien_rompu = r["casse"] and i == CIBLE + 1
            champs = (
                ("reprend l’empreinte du précédent", court(reprend),
                 ALERTE if lien_rompu else INDIGO, y + 66),
                ("contenu", r["contenus"][i],
                 ALERTE if (r["casse"] and i == CIBLE) else D.ENCRE, y + 116),
                ("donne son empreinte", court(produite),
                 ALERTE if (r["casse"] and i == CIBLE) else INDIGO, y + 160),
            )
            for libelle, valeur, teinte, yy in champs:
                textes_.append(texte("blocs", (g, yy), D.typo(libelle),
                                     "champ", D.FAIBLE))
                police = "contenu" if libelle == "contenu" else "valeur"
                textes_.append(texte("blocs", (g, yy + 18), D.typo(valeur),
                                     police, teinte))

            if i + 1 < len(BLOCS):
                rompu = r["casse"] and i == CIBLE
                #  Le trait part du BORD de la carte, pas de son intérieur :
                #  vingt pixels de moignon sous le champ donnaient
                #  l'impression d'un trait mal effacé.
                liens.extend(fleche("liens", (x1, y + 178),
                                    (x1 + ECART, y + 84),
                                    ALERTE if rompu else INDIGO, rompu))

    o.extend(cartes)
    o.extend(liens)
    o.extend(textes_)

    #  Une note sous la seconde rangée, qui dit ce que les croix veulent dire.
    y_note = Y_RANGEE[1] + HAUTEUR_BLOC + 22
    note = ("La retouche ne casse qu’un lien, celui du bloc n au suivant : "
            "le bloc n + 1 a déjà inscrit l’ancienne empreinte. Les blocs "
            "d’après restent cohérents entre eux, et c’est la RÉPARATION "
            "qui les condamne : refaire le n + 1 change son empreinte, donc "
            "casse le n + 2, et ainsi de suite jusqu’au bout de la chaîne.")
    lignes = mesure.couper(D.typo(note), fontes["note"], L - 2 * MARGE)
    for i, ligne in enumerate(lignes):
        #  La note explique, elle n'alerte pas : deux lignes entières en
        #  rouge seraient de la couleur décorative, ce que la charte
        #  interdit précisément pour cette teinte.
        o.append(texte("rangées", (MARGE, y_note + i * 20), ligne, "note",
                       D.GRIS))

    # --------------------------------------------------------------  pied
    pied = (
        "Les empreintes ne sont pas décoratives : chacune est un SHA-256 "
        "calculé sur le contenu du bloc et l’empreinte du précédent, comme "
        "le fait Bitcoin. Changer une transaction change réellement la "
        "valeur affichée.",
        "Elles sont tronquées à dix caractères pour tenir dans la figure ; "
        "une empreinte SHA-256 en compte soixante-quatre.",
        "Et il ne suffirait pas de refaire ces trois blocs : il faudrait le "
        "faire sur la majorité des copies du registre en même temps, ce qui "
        "est le vrai coût d’une falsification.",
    )
    y_pied = y_note + len(lignes) * 20 + 26
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
    return H, o, (intacte, cassee)


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
                tirets = ' stroke-dasharray="9 7"' if a["pointille"] else ""
                out.append('    <line x1="%g" y1="%g" x2="%g" y2="%g" '
                           'stroke="%s" stroke-width="%g"%s/>'
                           % (x0, y0, x1, y1, teinte(a["t"]), a["e"], tirets))
            elif a["quoi"] == "disque":
                out.append('    <circle cx="%g" cy="%g" r="%g" fill="%s"/>'
                           % (a["cx"], a["cy"], a["r"], teinte(a["t"])))
            elif a["quoi"] == "polygone":
                out.append('    <polygon points="%s" fill="%s"/>'
                           % (" ".join("%g,%g" % p for p in a["pts"]),
                              teinte(a["t"])))
            else:
                chemin, taille, graisse = POLICES[a["p"]]
                famille = FAMILLE_MONO if "Mono" in chemin else FAMILLE_SVG
                espacement = (' letter-spacing="%g"' % a["tr"]
                              if a["tr"] else "")
                ancre = ' text-anchor="middle"' if a["centre"] else ""
                out.append('    <text x="%g" y="%g" font-family="%s" '
                           'font-size="%g" font-weight="%s" fill="%s"%s%s'
                           ' xml:space="preserve">%s</text>'
                           % (a["xy"][0], a["xy"][1] + montees[a["p"]],
                              famille, taille, graisse, teinte(a["t"]),
                              espacement, ancre, propre(a["c"])))
        out.append('  </g>')
    out.append('</svg>')

    with open(base + ".svg", "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    return len(couches), sum(1 for a in ordres if a["quoi"] == "texte")


def principal():
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "bitcoin-chaine-de-blocs")
    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5),
               ("indigo", INDIGO, 4.5), ("alerte", ALERTE, 4.5))

    H, ordres, (intacte, cassee) = composer()
    rendre_matriciel(H, ordres, base)
    couches, textes = rendre_svg(H, ordres, base)

    print("  %-40s %.0f Ko"
          % (os.path.basename(base + ".svg"),
             os.path.getsize(base + ".svg") / 1024.0))
    print("  %d calques, %d textes" % (couches, textes))
    print()
    print("  chaîne intacte")
    for b, (reprend, produite) in zip(BLOCS, intacte):
        print("    %-12s reprend %s  donne %s"
              % (b["nom"], court(reprend), court(produite)))
    print("  après retouche du bloc %d" % (CIBLE + 1))
    for b, (reprend, produite) in zip(BLOCS, cassee):
        print("    %-12s reprend %s  donne %s"
              % (b["nom"], court(reprend), court(produite)))


if __name__ == "__main__":
    principal()
