"""
Les hashtags lisibles : une majuscule par mot, et à la fin.

    python3 article-hashtags/hashtags_lisibles.py

Produit `hashtags-majuscule-par-mot.webp`, son PNG et le SVG éditable.

----------------------------------------------------------------------------
DEUX LÉGENDES, PARCE QUE LA RÈGLE NE SE VOIT QUE PAR CONTRASTE
----------------------------------------------------------------------------
Une seule légende bien écrite ne montre rien : le lecteur la trouve normale
et passe. Ce qui se voit, c'est l'écart. La figure pose donc côte à côte la
même publication écrite de deux façons, et les deux défauts que l'article
nomme sautent aux yeux ensemble : les capitales qui collent les mots, et
les hashtags semés au milieu de la phrase.

----------------------------------------------------------------------------
LA SEGMENTATION EST CALCULÉE, PAS DESSINÉE
----------------------------------------------------------------------------
Sous chaque légende, la figure montre ce qu'une machine a pour découper un
hashtag en mots. Ces frontières ne sont pas placées à la main : la fonction
`segmenter` les calcule depuis la chaîne, au même endroit que le ferait
n'importe quel programme, c'est-à-dire aux passages minuscule vers
majuscule et lettre vers chiffre.

Le résultat est donc une démonstration et non une illustration. Sur
#PRINTEMPSETE2026, la fonction ne trouve qu'une frontière, celle du
chiffre ; sur #PrintempsEte2026, elle en trouve trois. C'est exactement ce
que dit l'article, et ici c'est le code qui le prouve.

Ce que la figure ne prétend PAS faire : simuler la voix d'un lecteur
d'écran en particulier. VoiceOver, NVDA et JAWS n'ont ni les mêmes
heuristiques ni les mêmes réglages. Ce qui est vrai de tous, et seul
affirmé ici, c'est qu'une chaîne sans majuscule interne ne leur offre
aucune frontière de mot.

----------------------------------------------------------------------------
LES RÈGLES DE L'ARTICLE SONT DES CONTRÔLES
----------------------------------------------------------------------------
L'article pose trois consignes : cinq hashtags, une majuscule par mot, en
fin de publication. Les trois sont vérifiées sur la légende de droite avant
le tracé. Une figure qui enseigne une règle et la viole dans son propre
exemple est pire que pas de figure du tout.
"""

import os
import re

import charte as C
import dessin as D

L = 1600
MARGE = 56

VIOLET = (98, 44, 200)
AMBRE = (180, 83, 9)
VERT = (12, 124, 92)

#  Les trois consignes de l'article, qui servent de contrôles.
HASHTAGS_ATTENDUS = 5

COMPTE = "atelier.bonnefoy"

MAUVAISE = (
    "Nouvelle collection #PRINTEMPSETE2026 disponible en boutique. "
    "Fabrication #FRANCAISE, matières #RECYCLEES et teintures "
    "#NATURELLES, venez voir ça ! #MODEDURABLE"
)

BONNE_TEXTE = (
    "Nouvelle collection printemps été 2026 disponible en boutique. "
    "Fabrication française, matières recyclées et teintures naturelles, "
    "venez voir ça !"
)
BONNE_HASHTAGS = ("#PrintempsEte2026", "#ModeDurable", "#FabriqueEnFrance",
                  "#MatieresRecyclees", "#TeintureNaturelle")

#  Les deux hashtags que l'article cite en exemple, montrés en démonstration.
DEMO = ("#PRINTEMPSETE2026", "#PrintempsEte2026")

POLICES = {
    "titre": (C.POLICE_G, 19, "bold"),
    "sous": (C.POLICE_R, 17, "normal"),
    "verdict": (C.POLICE_G, 14, "bold"),
    "compte": (C.POLICE_G, 15, "bold"),
    "legende": (C.POLICE_R, 16, "normal"),
    "etiq": (C.POLICE_R, 13, "normal"),
    "demo": (C.POLICE_G, 20, "bold"),
    "morceau": (C.POLICE_R, 14, "normal"),
    "pied": (C.POLICE_R, 16, "normal"),
}
FAMILLE_SVG = "Liberation Sans, Arial, Helvetica, sans-serif"

TITRE = "UNE MAJUSCULE PAR MOT, ET À LA FIN"
SOUS = ("la seule consigne de hashtag qu’aucune décision de plateforme ne "
        "rendra caduque : celle qui rend la légende lisible à voix haute")

LARGEUR_CARTE = (L - 2 * MARGE - 48) / 2.0
Y_CARTE = 176


def segmenter(mot):
    """Les frontières de mot qu'une machine peut trouver dans une chaîne.

    Aux passages minuscule vers majuscule et lettre vers chiffre, c'est-à-dire
    là où n'importe quel programme couperait. Rien d'autre n'est disponible :
    un hashtag ne contient ni espace ni ponctuation.
    """
    nu = mot.lstrip("#")
    coupe = re.sub(r"(?<=[a-zàâäéèêëîïôöùûüç])(?=[A-ZÀÂÄÉÈÊËÎÏÔÖÙÛÜÇ])",
                   "\u0000", nu)
    coupe = re.sub(r"(?<=[A-Za-zÀ-ÿ])(?=\d)", "\u0000", coupe)
    return [m for m in coupe.split("\u0000") if m]


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


def paragraphe(ops, couche, mesure, fonte, x, y, largeur, mots, teinte,
               teinte_hashtag, interligne=25):
    """Un paragraphe posé mot à mot, pour colorer les hashtags dans le flux.

    `couper` de la toile rend des lignes entières : impossible d'y teinter
    un mot. On place donc chaque mot soi-même, ce qui coûte quelques lignes
    et permet de montrer les hashtags là où ils sont vraiment.
    """
    curseur, debut = x, y
    espace = mesure.mesure(" ", fonte)
    for mot in mots:
        largeur_mot = mesure.mesure(mot, fonte)
        if curseur > x and curseur + largeur_mot > x + largeur:
            curseur = x
            y += interligne
        ops.append(texte(couche, (curseur, y), mot, "legende",
                         teinte_hashtag if mot.startswith("#") else teinte))
        curseur += largeur_mot + espace
    return y + interligne


def composer():
    mesure = D.Toile(L, 10)
    fontes = {k: mesure.police(f, t) for k, (f, t, _) in POLICES.items()}

    #  ------------------------------------------------------------------
    #  LES TROIS CONSIGNES DE L'ARTICLE, VÉRIFIÉES SUR L'EXEMPLE
    #  ------------------------------------------------------------------
    if len(BONNE_HASHTAGS) != HASHTAGS_ATTENDUS:
        raise SystemExit(
            "l'article recommande %d hashtags, l'exemple en montre %d"
            % (HASHTAGS_ATTENDUS, len(BONNE_HASHTAGS)))
    for h in BONNE_HASHTAGS:
        if len(segmenter(h)) < 2:
            raise SystemExit(
                "« %s » n'offre aucune frontière de mot : l'exemple "
                "contredirait la consigne qu'il illustre" % h)
    if "#" in BONNE_TEXTE:
        raise SystemExit(
            "la bonne légende porte un hashtag dans son corps ; la consigne "
            "est de les grouper à la fin")
    for h in DEMO[:1] + tuple(m for m in MAUVAISE.split() if m.startswith("#")):
        nu = h.lstrip("#").rstrip("!,.")
        if nu != nu.upper():
            raise SystemExit(
                "le contre-exemple « %s » n'est pas en capitales, il ne "
                "montre plus le défaut" % h)

    o = []
    o.append(texte("titre", (MARGE, 46), TITRE, "titre", D.ENCRE, 2.2))
    sous = D.typo(SOUS)
    if mesure.mesure(sous, fontes["sous"]) > L - 2 * MARGE:
        raise SystemExit("le sous-titre déborde")
    o.append(texte("titre", (MARGE, 74), sous, "sous", D.FAIBLE))
    o.append(trait("titre", [MARGE, 124, L - MARGE, 124], D.FILET, 2))

    colonnes = (
        {"x": MARGE, "teinte": AMBRE, "verdict": "CE QU’IL NE FAUT PAS FAIRE",
         "mots": D.typo(MAUVAISE).split(), "queue": (),
         "demo": DEMO[0],
         "etiq": "aucune frontière de mot, sauf devant le chiffre"},
        {"x": MARGE + LARGEUR_CARTE + 48, "teinte": VERT,
         "verdict": "CE QU’IL FAUT FAIRE",
         "mots": D.typo(BONNE_TEXTE).split(), "queue": BONNE_HASHTAGS,
         "demo": DEMO[1],
         "etiq": "une frontière à chaque majuscule interne"},
    )

    #  Première passe : on mesure, pour donner aux deux cartes la même
    #  hauteur. Deux cartes inégales feraient croire à une hiérarchie.
    bas = []
    for c in colonnes:
        essai = []
        y = paragraphe(essai, "essai", mesure, fontes["legende"],
                       c["x"] + 22, Y_CARTE + 104, LARGEUR_CARTE - 44,
                       c["mots"], D.ENCRE, VIOLET)
        if c["queue"]:
            y = paragraphe(essai, "essai", mesure, fontes["legende"],
                           c["x"] + 22, y + 10, LARGEUR_CARTE - 44,
                           list(c["queue"]), VIOLET, VIOLET)
        bas.append(y)
    y_separateur = max(bas) + 14
    hauteur = y_separateur + 116 - Y_CARTE

    for c in colonnes:
        x0, x1 = c["x"], c["x"] + LARGEUR_CARTE
        b = [x0, Y_CARTE, x1, Y_CARTE + hauteur]
        o.append(rect("cartes", b, 12, D.BLANC))
        o.append(cadre("cartes", b, 12, D.FILET, 2))
        o.append(rect("cartes", [x0, Y_CARTE, x1, Y_CARTE + 34], 6,
                      c["teinte"]))
        o.append(texte("cartes", (x0 + 18, Y_CARTE + 9), c["verdict"],
                       "verdict", D.BLANC))

        #  L'entête de publication, réduit à ce qu'il faut pour qu'on
        #  reconnaisse une légende de réseau social.
        o.append(disque("cartes", x0 + 40, Y_CARTE + 72, 18, (228, 224, 244)))
        o.append(texte("cartes", (x0 + 68, Y_CARTE + 64), COMPTE, "compte",
                       D.ENCRE))

        y = paragraphe(o, "textes", mesure, fontes["legende"], x0 + 22,
                       Y_CARTE + 104, LARGEUR_CARTE - 44, c["mots"],
                       D.ENCRE, VIOLET)
        if c["queue"]:
            y = paragraphe(o, "textes", mesure, fontes["legende"], x0 + 22,
                           y + 10, LARGEUR_CARTE - 44, list(c["queue"]),
                           VIOLET, VIOLET)

        #  La démonstration : le hashtag, puis ses morceaux.
        o.append(trait("textes", [x0 + 22, y_separateur, x1 - 22,
                                  y_separateur], D.FILET, 1))
        o.append(texte("textes", (x0 + 22, y_separateur + 14),
                       "ce qu’une machine a pour le découper en mots",
                       "etiq", D.FAIBLE))

        morceaux = segmenter(c["demo"])
        x = x0 + 22
        o.append(texte("textes", (x, y_separateur + 44), "#", "demo",
                       D.FAIBLE))
        x += mesure.mesure("#", fontes["demo"])
        for i, m in enumerate(morceaux):
            if i:
                o.append(trait("textes", [x + 3, y_separateur + 40, x + 3,
                                          y_separateur + 66], c["teinte"], 2))
                x += 9
            o.append(texte("textes", (x, y_separateur + 44), m, "demo",
                           D.ENCRE))
            x += mesure.mesure(m, fontes["demo"])

        resume = "%d morceau%s : %s" % (
            len(morceaux), "x" if len(morceaux) > 1 else "",
            D.typo(c["etiq"]))
        o.append(texte("textes", (x0 + 22, y_separateur + 80), resume,
                       "etiq", c["teinte"]))

    # --------------------------------------------------------------  pied
    pied = (
        "Un hashtag est une seule chaîne de caractères : les majuscules "
        "internes sont la seule frontière de mot qu’un programme puisse y "
        "trouver. Les traits ci-dessus ne sont pas dessinés, ils sont "
        "calculés depuis la chaîne.",
        "Les recommandations d’accessibilité d’Orange demandent une "
        "majuscule au début de chaque mot, et de placer les hashtags à la "
        "fin de la publication pour ne pas hacher la lecture du message.",
        "Cette figure ne simule aucun lecteur d’écran en particulier : "
        "VoiceOver, NVDA et JAWS n’ont ni les mêmes heuristiques ni les "
        "mêmes réglages. Ce qui vaut pour tous, c’est qu’une chaîne sans "
        "majuscule interne ne leur offre rien à découper.",
    )
    y_pied = Y_CARTE + hauteur + 34
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
                        "hashtags-majuscule-par-mot")
    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5),
               ("violet", VIOLET, 4.5), ("ambre", AMBRE, 4.5),
               ("vert", VERT, 4.5))

    H, ordres = composer()
    rendre_matriciel(H, ordres, base)
    couches, textes = rendre_svg(H, ordres, base)

    print("  %-42s %.0f Ko"
          % (os.path.basename(base + ".svg"),
             os.path.getsize(base + ".svg") / 1024.0))
    print("  %d calques, %d textes" % (couches, textes))
    print()
    print("  segmentation calculée :")
    for h in DEMO + BONNE_HASHTAGS:
        morceaux = segmenter(h)
        print("    %-22s %d morceau(x)  %s"
              % (h, len(morceaux), " | ".join(morceaux)))
    print()
    print("  %d hashtags dans l'exemple, %d attendus"
          % (len(BONNE_HASHTAGS), HASHTAGS_ATTENDUS))


if __name__ == "__main__":
    principal()
