"""
De la retraite d'EMPRESS aux contournements de 2026.

    python3 article-piratage-drm/frise_2026.py

Produit `piratage-frise-2025-2026` en .webp, .png et .svg.

----------------------------------------------------------------------------
LA LÉGENDE DE L'ARTICLE SE CONTREDIT, LA FRISE TRANCHE
----------------------------------------------------------------------------
La légende annonce « neuf mois entre une retraite annoncée et un crack le
jour de la sortie ». Le corps du texte, lui, écrit « six mois plus tard, en
mai 2026 ». Neuf mois avant mai 2026 tombent en août 2025, qui n'est pas
« fin 2025 ».

La frise porte donc SIX, calculé à partir des deux dates et non recopié, et
un contrôle refuse la figure si le calcul cesse de donner six.

----------------------------------------------------------------------------
UNE TECHNIQUE N'EST PAS UN ÉVÉNEMENT
----------------------------------------------------------------------------
Les contournements par hyperviseur n'ont pas de date : l'article les situe
« en 2026 », sans plus. Les poser sur un point de la frise aurait inventé une
précision que la source ne donne pas. Ils sont donc une BANDE, qui court sous
l'axe sur toute l'année, et la figure dit que la date n'est pas connue.

Cette bande porte aussi la tension de la section : les deux cracks les plus
commentés de l'année se sont passés de la technique qui faisait parler.

----------------------------------------------------------------------------
DEUX PRÉCISIONS DE DATE, DEUX MARQUES DIFFÉRENTES
----------------------------------------------------------------------------
Un seul des quatre événements a un jour connu, le 14 mars 2026. Les trois
autres ne sont datés qu'au mois. Un point rond pour le jour, une barre large
sur tout le mois pour les autres : la figure montre ce qu'elle sait et ce
qu'elle ne sait pas, au lieu d'aligner quatre points également assurés.
"""

import os
from datetime import date

import charte as C
import dessin as D

RACINE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(RACINE, "piratage-frise-2025-2026")

L = 1600
MARGE = 56

VIOLET = (98, 44, 200)
VIOLET_DOUX = (162, 120, 228)
VIOLET_BANDE = (233, 224, 252)
ZEBRE = (244, 243, 238)

DEBUT = date(2025, 11, 1)
FIN = date(2026, 12, 31)

#  (date, jour connu, niveau, titre, détail)
#  `jour connu` dit si la source donne mieux que le mois.
EVENEMENTS = (
    (date(2025, 11, 15), False, 0, "EMPRESS annonce son retrait",
     "« End of an Era ». Elle invoque des problèmes de santé et une "
     "lassitude vis-à-vis du milieu."),
    (date(2026, 3, 14), True, 1, "Doom: The Dark Ages craqué",
     "Par un dénommé voices38, et sans hyperviseur."),
    (date(2026, 5, 15), False, 0, "Lego Batman craqué le jour de sa sortie",
     "Sans hyperviseur non plus. Premier Denuvo tombé le jour J en 2026."),
    (date(2026, 7, 15), False, 1, "id Software retire Denuvo de Doom",
     "À l’occasion d’une grosse mise à jour. Le studio n’a pas expliqué "
     "pourquoi."),
)

#  Les deux bornes de l'intervalle que la légende de l'article annonce.
DEPART, ARRIVEE = 0, 2

BANDE = ("Contournements par hyperviseur, sous le noyau Windows",
         "courant 2026, aucune date précisée par les sources")

POLICES = {
    "titre": (C.POLICE_G, 17, "bold"),
    "sous": (C.POLICE_R, 18, "normal"),
    "date": (C.POLICE_G, 14, "bold"),
    "nom": (C.POLICE_G, 17, "bold"),
    "detail": (C.POLICE_R, 15, "normal"),
    "axe": (C.POLICE_R, 13, "normal"),
    "bande": (C.POLICE_G, 15, "bold"),
    "petit": (C.POLICE_R, 14, "normal"),
    "pied": (C.POLICE_R, 16, "normal"),
}
FAMILLE = "Liberation Sans, Arial, Helvetica, sans-serif"

MOIS = ("janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août",
        "sept.", "oct.", "nov.", "déc.")

TITRE = "LA COURSE CONTINUE SANS SA CHAMPIONNE"
SOUS = "de la retraite d’EMPRESS aux contournements de 2026"

CARTE = 336


def mois_francais(d):
    return "%s %d" % (MOIS[d.month - 1], d.year)


def rect(couche, b, r, teinte):
    return {"quoi": "rect", "couche": couche, "b": b, "r": r, "t": teinte}


def trait(couche, b, teinte, epaisseur):
    return {"quoi": "trait", "couche": couche, "b": b, "t": teinte,
            "e": epaisseur}


def disque(couche, cx, cy, r, teinte):
    return {"quoi": "disque", "couche": couche, "cx": cx, "cy": cy, "r": r,
            "t": teinte}


def texte(couche, xy, contenu, police, teinte, tracking=0.0):
    for c, nom in (("—", "cadratin"), ("–", "demi-cadratin")):
        if c in contenu:
            raise SystemExit("%s dans « %s »" % (nom, contenu[:60]))
    return {"quoi": "texte", "couche": couche, "xy": xy, "c": contenu,
            "p": police, "t": teinte, "tr": tracking}


def composer():
    mesure = D.Toile(L, 10)
    fontes = {k: mesure.police(f, t) for k, (f, t, _) in POLICES.items()}

    def couper(contenu, police, largeur):
        return mesure.couper(D.typo(contenu), fontes[police], largeur)

    def large(contenu, police):
        return mesure.mesure(D.typo(contenu), fontes[police])

    piste = L - 2 * MARGE
    jours = float((FIN - DEBUT).days)

    def pos(d):
        return MARGE + piste * (d - DEBUT).days / jours

    #  L'INTERVALLE EST CALCULÉ, PAS RECOPIÉ.
    a = EVENEMENTS[DEPART][0]
    b = EVENEMENTS[ARRIVEE][0]
    ecart = (b.year - a.year) * 12 + b.month - a.month
    if ecart != 6:
        raise SystemExit("l'intervalle vaut %d mois : la figure annonce six"
                         % ecart)
    #  Et le titre ne doit pas reprendre le compte de la légende de
    #  l'article, qui est celui qu'on corrige. Écrit une fois par étourderie,
    #  il faisait dire « neuf » à une frise qui montre six.
    for mot in ("NEUF", "HUIT", "SEPT", "CINQ"):
        if mot in TITRE.upper():
            raise SystemExit("le titre annonce « %s » alors que "
                             "l'intervalle mesuré vaut six mois" % mot)

    y_cartes = 150
    #  Hauteur relevée sur le contenu réel : à 118 px, le détail de la
    #  carte EMPRESS, qui se plie en trois lignes, débordait.
    haut_carte = 156
    y_axe = y_cartes + 2 * haut_carte + 34
    y_bande = y_axe + 62
    y_pied = y_bande + 92
    pied = (
        "Dates de l’article. Un seul événement a un jour connu, le 14 mars "
        "2026 : point plein. Les trois autres ne sont datés qu’au mois, "
        "marqués par une barre sur tout le mois.",
        "Les contournements par hyperviseur n’ont pas de date dans les "
        "sources, seulement l’année : ils forment une bande et non un point, "
        "faute de quoi la figure inventerait une précision.",
        "L’intervalle de six mois est calculé à partir des deux dates. Le "
        "corps de l’article écrit « six mois plus tard, en mai 2026 » ; la "
        "légende annonce neuf, ce qui placerait le retrait en août 2025.",
    )
    H = y_pied + 18 + len(pied) * 24 + 40

    o = [rect("Fond", [0, 0, L, H], 0, D.PAPIER)]
    o.append(texte("Titre", (MARGE, 52), TITRE, "titre", D.ENCRE, 2.2))
    o.append(texte("Titre", (MARGE, 78), D.typo(SOUS), "sous", D.FAIBLE))

    # ----------------------------------------------------------  les cartes
    places = {0: [], 1: []}
    for quand, jour, niveau, nom, detail in EVENEMENTS:
        x = pos(quand)
        x = max(MARGE, min(x, L - MARGE - CARTE))
        for autre in places[niveau]:
            if abs(x - autre) < CARTE + 14:
                raise SystemExit("deux cartes se chevauchent au niveau %d"
                                 % niveau)
        places[niveau].append(x)

        y = y_cartes + niveau * haut_carte
        o.append(rect("Cartes", [x, y, x + CARTE, y + haut_carte - 20], 10,
                      ZEBRE))
        o.append(rect("Cartes", [x, y, x + 4, y + haut_carte - 20], 2,
                      VIOLET))
        o.append(texte("Cartes", (x + 18, y + 14),
                       D.typo(mois_francais(quand) if not jour
                              else "14 mars 2026"), "date", VIOLET, 1.0))
        lignes = couper(nom, "nom", CARTE - 36)
        yy = y + 36
        for ligne in lignes:
            o.append(texte("Cartes", (x + 18, yy), ligne, "nom", D.ENCRE))
            yy += 20
        for ligne in couper(detail, "detail", CARTE - 36):
            if yy > y + haut_carte - 38:
                raise SystemExit("« %s » déborde de sa carte" % nom)
            o.append(texte("Cartes", (x + 18, yy + 4), ligne, "detail",
                           D.GRIS))
            yy += 18

        #  Le fil qui relie la carte à sa marque sur l'axe.
        o.append(trait("Cartes", [pos(quand), y + haut_carte - 20,
                                  pos(quand), y_axe], D.FILET, 2))

    # ------------------------------------------------------------  l'axe
    o.append(trait("Axe", [MARGE, y_axe, L - MARGE, y_axe], D.ENCRE, 2))
    an = DEBUT
    while an <= FIN:
        x = pos(an)
        grand = an.month == 1
        o.append(trait("Axe", [x, y_axe, x, y_axe + (12 if grand else 6)],
                       D.ENCRE if grand else D.FILET, 2 if grand else 1))
        if grand or an.month == 7:
            o.append(texte("Axe", (x + 6, y_axe + 14),
                           D.typo(mois_francais(an)), "axe", D.FAIBLE))
        an = date(an.year + (an.month == 12), an.month % 12 + 1, 1)

    for quand, jour, _, _, _ in EVENEMENTS:
        x = pos(quand)
        if jour:
            o.append(disque("Axe", x, y_axe, 8, VIOLET))
        else:
            #  Toute la largeur du mois : la source ne donne pas mieux.
            debut_mois = date(quand.year, quand.month, 1)
            fin_mois = date(quand.year + (quand.month == 12),
                            quand.month % 12 + 1, 1)
            o.append(rect("Axe", [pos(debut_mois), y_axe - 7,
                                  pos(fin_mois), y_axe + 7], 6,
                          VIOLET_DOUX))

    #  L'intervalle que la légende annonce, mesuré sur l'axe.
    xa, xb = pos(a), pos(b)
    o.append(trait("Axe", [xa, y_axe - 26, xb, y_axe - 26], VIOLET, 2))
    for x in (xa, xb):
        o.append(trait("Axe", [x, y_axe - 32, x, y_axe - 20], VIOLET, 2))
    mot = D.typo("six mois")
    o.append(texte("Axe", ((xa + xb) / 2.0 - large(mot, "date") / 2.0,
                           y_axe - 50), mot, "date", VIOLET, 1.0))

    # ----------------------------------------------------------  la bande
    x0, x1 = pos(date(2026, 1, 1)), pos(date(2026, 12, 31))
    o.append(rect("Bande", [x0, y_bande, x1, y_bande + 52], 10,
                  VIOLET_BANDE))
    o.append(texte("Bande", (x0 + 18, y_bande + 10), D.typo(BANDE[0]),
                   "bande", VIOLET))
    o.append(texte("Bande", (x0 + 18, y_bande + 31), D.typo(BANDE[1]),
                   "petit", D.GRIS))
    if large(BANDE[0], "bande") > x1 - x0 - 36:
        raise SystemExit("le titre de la bande déborde")

    o.append(trait("Pied", [MARGE, y_pied, L - MARGE, y_pied], D.FILET, 2))
    for i, ligne in enumerate(pied):
        if large(ligne, "pied") > L - 2 * MARGE:
            raise SystemExit("la ligne %d du pied déborde" % (i + 1))
        o.append(texte("Pied", (MARGE, y_pied + 18 + i * 24), D.typo(ligne),
                       "pied", D.FAIBLE))

    return H, o, ecart


def rendre_matriciel(H, ordres):
    t = D.Toile(L, H)
    fontes = {k: t.police(f, taille) for k, (f, taille, _) in POLICES.items()}
    for a in ordres:
        if a["quoi"] == "rect":
            t.rrect(a["b"], a["r"], teinte=a["t"])
        elif a["quoi"] == "trait":
            t.ligne(a["b"], a["t"], a["e"])
        elif a["quoi"] == "disque":
            t.disque(a["cx"], a["cy"], a["r"], teinte=a["t"])
        elif a["tr"]:
            t.espace(a["xy"], a["c"], fontes[a["p"]], a["t"], a["tr"])
        else:
            t.texte(a["xy"], a["c"], fontes[a["p"]], a["t"])
    D.enregistrer(t.final(L, H), BASE, L, H)


def rendre_svg(H, ordres):
    montees = {c: C.police(f, t).getmetrics()[0]
               for c, (f, t, _) in POLICES.items()}

    def teinte(t):
        return "#%02x%02x%02x" % t

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
                out.append('    <text x="%g" y="%g" font-family="%s" '
                           'font-size="%g" font-weight="%s" fill="%s"%s'
                           ' xml:space="preserve">%s</text>'
                           % (a["xy"][0], a["xy"][1] + montees[a["p"]],
                              FAMILLE, taille, graisse, teinte(a["t"]),
                              espacement, propre(a["c"])))
        out.append('  </g>')
    out.append('</svg>')

    with open(BASE + ".svg", "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    return len(couches), sum(1 for a in ordres if a["quoi"] == "texte")


def principal():
    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5),
               ("violet", VIOLET, 4.5))
    H, ordres, ecart = composer()
    rendre_matriciel(H, ordres)
    couches, textes = rendre_svg(H, ordres)
    print("  piratage-frise-2025-2026.svg               %d Ko"
          % round(os.path.getsize(BASE + ".svg") / 1024.0))
    print("  %d calques, %d textes, %d événements"
          % (couches, textes, len(EVENEMENTS)))
    print("  intervalle calculé : %d mois" % ecart)
    for quand, jour, _, nom, _ in EVENEMENTS:
        print("    %-12s %-42s %s"
              % (quand.isoformat(), nom,
                 "jour connu" if jour else "mois seulement"))


if __name__ == "__main__":
    principal()
