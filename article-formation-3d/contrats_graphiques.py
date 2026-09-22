"""
Le stage rattrape le CDI, et seules les deux extrémités sont mesurées.

    python3 article-formation-3d/contrats_graphiques.py

Produit `formation-3d-contrats-graphiques` en .webp, .png et .svg.

----------------------------------------------------------------------------
DEUX POINTS MESURÉS, PAS QUATRE
----------------------------------------------------------------------------
Le brief demande « trois courbes de 2022 à 2025 ». L'article ne donne que les
deux BOUTS de chaque série : 57 et 33, 17 et 35, 26 et 32. Les parts de 2023
et 2024 n'y sont nulle part.

Poser quatre points par série aurait demandé d'en inventer deux, et une
courbe inventée ne se distingue pas d'une courbe mesurée une fois dessinée.
Les segments sont donc en POINTILLÉS entre les deux points pleins : le
lecteur voit d'un coup d'oeil ce qui est relevé et ce qui est joint.

----------------------------------------------------------------------------
LE CROISEMENT EST UNE CONSÉQUENCE, PAS UN ÉVÉNEMENT
----------------------------------------------------------------------------
La légende de l'article annonce que les deux premières courbes se croisent
entre 2024 et 2025. En interpolation droite, elles se croisent bien à la fin
de 2024, et le script le calcule au lieu de le supposer.

Mais ce croisement ne dit rien de ce qui s'est passé cette année-là : il
découle du tracé. Il est donc marqué d'un anneau creux et non d'un point
plein, et le pied le dit en toutes lettres.

----------------------------------------------------------------------------
LES TROIS PARTS FONT CENT, ET C'EST VÉRIFIÉ
----------------------------------------------------------------------------
Trois parts d'un même total doivent faire 100 aux deux bouts. Un contrôle le
vérifie avant de dessiner : c'est le genre d'erreur de saisie qu'une figure
publie sans broncher.
"""

import os

import charte as C
import dessin as D

RACINE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(RACINE, "formation-3d-contrats-graphiques")

L = 1600
MARGE = 56

#  LES TROIS TEINTES DOIVENT PASSER DEUX SEUILS, PAS UN.
#
#  Le validateur de palette demande 3:1 sur le fond, ce qui suffit à un
#  aplat. La charte maison demande 4,5:1, parce qu'ici la teinte porte AUSSI
#  du texte : le nom de la série et sa valeur.
#
#  Une sarcelle s'y refuse : assez claire pour garder sa chroma, elle tombe
#  à 3,5:1 ; assez foncée pour lire, elle passe sous le plancher de chroma
#  du validateur et redevient un gris. Mesuré sur six nuances. Le bleu
#  n'a pas ce problème.
#
#  Séparation 23,6 en vision protanope, 24,2 en tritanope, et 4,7:1 au
#  minimum sur le fond.
VIOLET = (98, 44, 200)
AMBRE = (180, 83, 9)
BLEU = (22, 104, 184)

ANNEE_A, ANNEE_B = 2022, 2025

#  (intitulé, part en 2022, part en 2025, teinte). Rien entre les deux.
SERIES = (
    ("CDI", 57, 33, VIOLET),
    ("Stages", 17, 35, AMBRE),
    ("CDD et alternance", 26, 32, BLEU),
)

MAXI = 60

POLICES = {
    "titre": (C.POLICE_G, 17, "bold"),
    "sous": (C.POLICE_R, 18, "normal"),
    "axe": (C.POLICE_R, 15, "normal"),
    "annee": (C.POLICE_G, 16, "bold"),
    "serie": (C.POLICE_G, 17, "bold"),
    "valeur": (C.POLICE_G, 20, "bold"),
    "petit": (C.POLICE_R, 14, "normal"),
    "fait": (C.POLICE_G, 20, "bold"),
    "pied": (C.POLICE_R, 16, "normal"),
}
FAMILLE = "Liberation Sans, Arial, Helvetica, sans-serif"

TITRE = "LE STAGE A RATTRAPÉ LE CDI"
SOUS = ("part des types de contrat dans les offres graphiques du jeu vidéo, "
        "en France")


def pourcent(v):
    return "%d %%" % v


def rect(couche, b, r, teinte):
    return {"quoi": "rect", "couche": couche, "b": b, "r": r, "t": teinte}


def trait(couche, b, teinte, epaisseur, pointille=False):
    return {"quoi": "trait", "couche": couche, "b": b, "t": teinte,
            "e": epaisseur, "pointille": pointille}


def disque(couche, cx, cy, r, teinte, contour=None):
    return {"quoi": "disque", "couche": couche, "cx": cx, "cy": cy, "r": r,
            "t": teinte, "contour": contour}


def texte(couche, xy, contenu, police, teinte, tracking=0.0):
    for c, nom in (("—", "cadratin"), ("–", "demi-cadratin")):
        if c in contenu:
            raise SystemExit("%s dans « %s »" % (nom, contenu[:60]))
    return {"quoi": "texte", "couche": couche, "xy": xy, "c": contenu,
            "p": police, "t": teinte, "tr": tracking}


def composer():
    mesure = D.Toile(L, 10)
    fontes = {k: mesure.police(f, t) for k, (f, t, _) in POLICES.items()}

    def large(contenu, police):
        return mesure.mesure(D.typo(contenu), fontes[police])

    #  CONTRÔLE : trois parts d'un même total font cent, aux deux bouts.
    for i, an in ((1, ANNEE_A), (2, ANNEE_B)):
        somme = sum(s[i] for s in SERIES)
        if somme != 100:
            raise SystemExit("les parts de %d font %d %% et non cent"
                             % (an, somme))

    x0, x1 = MARGE + 76, L - MARGE - 268
    y_haut, y_bas = 178, 566

    def px(an):
        return x0 + (x1 - x0) * (an - ANNEE_A) / float(ANNEE_B - ANNEE_A)

    def py(part):
        return y_bas - (y_bas - y_haut) * part / float(MAXI)

    #  Le croisement des deux premières séries, CALCULÉ sur le tracé droit.
    (_, a0, a1, _), (_, b0, b1, _) = SERIES[0], SERIES[1]
    pente = (a0 - a1) + (b1 - b0)
    t = (a0 - b0) / float(pente) * (ANNEE_B - ANNEE_A)
    an_croise = ANNEE_A + t
    val_croise = a0 - (a0 - a1) * t / float(ANNEE_B - ANNEE_A)

    y_fait = y_bas + 92
    y_pied = y_fait + 54
    pied = (
        "Observatoire de l’emploi de l’AFJV. Seules les parts de %d et de "
        "%d sont données par l’article : les points pleins sont relevés, le "
        "trait entre eux est interpolé." % (ANNEE_A, ANNEE_B),
        "C’est pourquoi il est en pointillés. Les parts de 2023 et 2024 ne "
        "sont pas connues ici, et rien ne dit que la bascule s’est faite "
        "régulièrement d’une année sur l’autre.",
        "Le croisement tombe fin %d sur ce tracé, anneau creux : il découle "
        "de la droite, il n’est pas mesuré. Les trois parts font bien 100 %% "
        "en %d comme en %d." % (int(an_croise), ANNEE_A, ANNEE_B),
    )
    H = y_pied + 18 + len(pied) * 24 + 40

    o = [rect("Fond", [0, 0, L, H], 0, D.PAPIER)]
    o.append(texte("Titre", (MARGE, 52), TITRE, "titre", D.ENCRE, 2.2))
    o.append(texte("Titre", (MARGE, 78), D.typo(SOUS), "sous", D.FAIBLE))

    #  La légende, avec la marque qui dit ce qu'est un point plein.
    x = MARGE
    for nom, _, _, teinte in SERIES:
        o.append(disque("Titre", x + 7, 122, 7, teinte))
        o.append(texte("Titre", (x + 22, 113), D.typo(nom), "petit", D.GRIS))
        x += 22 + large(nom, "petit") + 34
    o.append(disque("Titre", x + 7, 122, 7, D.PAPIER, D.GRIS))
    mot = "croisement interpolé, non mesuré"
    o.append(texte("Titre", (x + 22, 113), D.typo(mot), "petit", D.FAIBLE))
    if x + 22 + large(mot, "petit") > L - MARGE:
        raise SystemExit("la légende déborde")

    # ------------------------------------------------------------  la grille
    for part in range(0, MAXI + 1, 10):
        y = py(part)
        o.append(trait("Grille", [x0, y, x1, y], D.FILET, 1))
        o.append(texte("Grille", (MARGE, y - 10), pourcent(part), "axe",
                       D.FAIBLE))
    for an in range(ANNEE_A, ANNEE_B + 1):
        x = px(an)
        releve = an in (ANNEE_A, ANNEE_B)
        o.append(trait("Grille", [x, y_bas, x, y_bas + (12 if releve else 6)],
                       D.ENCRE if releve else D.FILET, 2 if releve else 1))
        o.append(texte("Grille", (x - large(str(an), "annee") / 2.0,
                                  y_bas + 20), str(an), "annee",
                       D.ENCRE if releve else D.FAIBLE))
        if not releve:
            mot = "non relevé"
            o.append(texte("Grille", (x - large(mot, "petit") / 2.0,
                                      y_bas + 42), D.typo(mot), "petit",
                           D.FAIBLE))

    # -----------------------------------------------------------  les séries
    for nom, va, vb, teinte in SERIES:
        xa, ya = px(ANNEE_A), py(va)
        xb, yb = px(ANNEE_B), py(vb)
        o.append(trait("Series", [xa, ya, xb, yb], teinte, 3, pointille=True))
        o.append(disque("Series", xa, ya, 9, teinte))
        o.append(disque("Series", xb, yb, 9, teinte))
        mot = pourcent(va)
        o.append(texte("Series", (xa - large(mot, "valeur") - 22, ya - 14),
                       mot, "valeur", teinte))

    #  LES ÉTIQUETTES DE DROITE S'ÉCARTENT, SINON ELLES SE MARCHENT DESSUS.
    #
    #  Les trois séries finissent à 33, 35 et 32 : trois points d'écart pour
    #  des blocs qui en font quarante de haut. Posées à leur ordonnée, elles
    #  se superposaient au point d'être illisibles. On les range donc par
    #  hauteur, on impose un écart minimal, et une ligne de rappel relie
    #  chaque étiquette à son point.
    hauteur_bloc = 46
    etiquettes = sorted(((py(vb), nom, vb, teinte)
                         for nom, _, vb, teinte in SERIES),
                        key=lambda e: e[0])
    posees = []
    for i, (y, nom, vb, teinte) in enumerate(etiquettes):
        cible = y - 14
        if posees and cible < posees[-1] + hauteur_bloc:
            cible = posees[-1] + hauteur_bloc
        posees.append(cible)
        xb = px(ANNEE_B)
        #  La ligne de rappel, du point vers son étiquette.
        o.append(trait("Series", [xb + 10, y, xb + 34, cible + 12],
                       teinte, 2))
        o.append(texte("Series", (xb + 42, cible), pourcent(vb), "valeur",
                       teinte))
        o.append(texte("Series", (xb + 42, cible + 24), D.typo(nom),
                       "serie", teinte))
        if xb + 42 + large(nom, "serie") > L - MARGE:
            raise SystemExit("« %s » déborde à droite" % nom)

    #  Le croisement, anneau creux : il n'a pas été mesuré.
    o.append(disque("Series", px(an_croise), py(val_croise), 10, D.PAPIER,
                    D.GRIS))

    fait = ("En %d ans, le CDI perd %d points et le stage en gagne %d."
            % (ANNEE_B - ANNEE_A, SERIES[0][1] - SERIES[0][2],
               SERIES[1][2] - SERIES[1][1]))
    if large(fait, "fait") > L - 2 * MARGE:
        raise SystemExit("le bandeau déborde")
    o.append(trait("Bandeau", [MARGE, y_fait - 24, L - MARGE, y_fait - 24],
                   D.FILET, 2))
    o.append(texte("Bandeau", (MARGE, y_fait), D.typo(fait), "fait", VIOLET))

    o.append(trait("Pied", [MARGE, y_pied, L - MARGE, y_pied], D.FILET, 2))
    for i, ligne in enumerate(pied):
        if large(ligne, "pied") > L - 2 * MARGE:
            raise SystemExit("la ligne %d du pied déborde" % (i + 1))
        o.append(texte("Pied", (MARGE, y_pied + 18 + i * 24), D.typo(ligne),
                       "pied", D.FAIBLE))

    return H, o, (an_croise, val_croise)


def rendre_matriciel(H, ordres):
    t = D.Toile(L, H)
    fontes = {k: t.police(f, taille) for k, (f, taille, _) in POLICES.items()}
    for a in ordres:
        if a["quoi"] == "rect":
            t.rrect(a["b"], a["r"], teinte=a["t"])
        elif a["quoi"] == "trait":
            if a["pointille"]:
                x0, y0, x1, y1 = a["b"]
                t.pointilles([(x0, y0), (x1, y1)], a["t"], a["e"])
            else:
                t.ligne(a["b"], a["t"], a["e"])
        elif a["quoi"] == "disque":
            t.disque(a["cx"], a["cy"], a["r"], teinte=a["t"],
                     contour=a["contour"], epaisseur=3)
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
                tirets = (' stroke-dasharray="9 7"' if a["pointille"]
                          else "")
                out.append('    <line x1="%g" y1="%g" x2="%g" y2="%g" '
                           'stroke="%s" stroke-width="%g"%s/>'
                           % (x0, y0, x1, y1, teinte(a["t"]), a["e"],
                              tirets))
            elif a["quoi"] == "disque":
                bord = ('' if not a["contour"] else
                        ' stroke="%s" stroke-width="3"'
                        % teinte(a["contour"]))
                out.append('    <circle cx="%g" cy="%g" r="%g" fill="%s"%s/>'
                           % (a["cx"], a["cy"], a["r"], teinte(a["t"]), bord))
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
               ("violet", VIOLET, 4.5), ("ambre", AMBRE, 4.5),
               ("bleu", BLEU, 4.5))
    H, ordres, croise = composer()
    rendre_matriciel(H, ordres)
    couches, textes = rendre_svg(H, ordres)
    print("  formation-3d-contrats-graphiques.svg       %d Ko"
          % round(os.path.getsize(BASE + ".svg") / 1024.0))
    print("  %d calques, %d textes" % (couches, textes))
    for nom, a, b, _ in SERIES:
        print("    %-20s %d %% -> %d %%   %+d points" % (nom, a, b, b - a))
    print("    croisement interpolé : %.2f, à %.1f %%" % croise)


if __name__ == "__main__":
    principal()
