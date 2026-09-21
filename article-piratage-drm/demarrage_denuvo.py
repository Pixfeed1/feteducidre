"""
Quatre jeux, deux lancements chacun, et le temps que Denuvo ajoute.

    python3 article-piratage-drm/demarrage_denuvo.py

Produit `denuvo-temps-de-demarrage` en .webp, .png et .svg.

----------------------------------------------------------------------------
CE QUE CETTE FIGURE MESURE, ET CE QU'ELLE NE MESURE PAS
----------------------------------------------------------------------------
Des TEMPS DE DÉMARRAGE, et rien d'autre. Un lecteur pressé regardera des
barres qui triplent et en conclura que Denuvo divise les performances par
trois. C'est faux, et l'article dit lui-même le contraire deux paragraphes
plus haut : TechPowerUp mesure moins de 1 % d'écart quand la carte graphique
limite, 3 à 4 % quand le processeur limite.

Le pied porte donc cette précision. Une figure qui laisse tirer la mauvaise
conclusion a raté son travail, même quand chacun de ses chiffres est juste.

----------------------------------------------------------------------------
LES ÉCARTS SONT CALCULÉS, PAS SAISIS
----------------------------------------------------------------------------
Seuls les huit temps relevés sont écrits dans le fichier. Les écarts, les
rapports et le total viennent d'eux. Saisir « +146 s » à la main, c'est
s'exposer à corriger un temps sans corriger l'écart, et à publier une figure
qui se contredit dans sa propre colonne.

----------------------------------------------------------------------------
LES DEUX VIOLETS SONT VALIDÉS
----------------------------------------------------------------------------
Un gris neutre pour « sans Denuvo » aurait été le choix évident, et il échoue
au plancher de chroma : il ne porte plus d'identité par la teinte. La paire
retenue est un dégradé d'une seule teinte, séparation 16,9 en vision
protanope et 20,5 en tritanope, toutes deux au-dessus de 3:1 sur le fond. Le
plus foncé porte la version protégée, qui est la plus lourde.
"""

import os

import charte as C
import dessin as D

RACINE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(RACINE, "denuvo-temps-de-demarrage")

L = 1600
MARGE = 56
GOUTTIERE = 20

NOM = 320
PISTE = 880
ECART = L - 2 * MARGE - NOM - PISTE - 2 * GOUTTIERE

VIOLET = (98, 44, 200)
VIOLET_DOUX = (162, 120, 228)
ZEBRE = (244, 243, 238)

#  (jeu, secondes avec Denuvo, secondes sans). Relevés par YetTea, repris
#  par 80 Level en mai 2023. Rien d'autre n'est saisi à la main.
JEUX = (
    ("Ghostwire: Tokyo", 200, 54),
    ("Dying Light 2", 165, 64),
    ("Borderlands 3", 103, 62),
    ("Shadow of the Tomb Raider", 86, 29),
)

POLICES = {
    "titre": (C.POLICE_G, 17, "bold"),
    "sous": (C.POLICE_R, 18, "normal"),
    "nom": (C.POLICE_G, 18, "bold"),
    "petit": (C.POLICE_R, 14, "normal"),
    "valeur": (C.POLICE_G, 16, "bold"),
    "ecart": (C.POLICE_G, 19, "bold"),
    "fait": (C.POLICE_G, 20, "bold"),
    "pied": (C.POLICE_R, 16, "normal"),
}
FAMILLE = "Liberation Sans, Arial, Helvetica, sans-serif"

TITRE = "CE QUE DENUVO AJOUTE AU DÉMARRAGE"
SOUS = "secondes entre le lancement et le jeu, mêmes machines, mêmes jeux"


def secondes(v):
    return "%d s" % v


def duree(v):
    return "%d min %02d s" % (v // 60, v % 60)


def rect(couche, b, r, teinte):
    return {"quoi": "rect", "couche": couche, "b": b, "r": r, "t": teinte}


def trait(couche, b, teinte, epaisseur):
    return {"quoi": "trait", "couche": couche, "b": b, "t": teinte,
            "e": epaisseur}


def texte(couche, xy, contenu, police, teinte, tracking=0.0):
    #  PAS DE CADRATIN, ici comme dans Toile.texte : le SVG ne passe pas par
    #  le dessin matriciel, il lui faut son propre contrôle.
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

    #  CONTRÔLE : une protection ne peut pas raccourcir un démarrage. Si un
    #  relevé disait le contraire, ce serait une faute de saisie.
    for jeu, avec, sans in JEUX:
        if avec <= sans:
            raise SystemExit("« %s » démarre plus vite AVEC Denuvo : %d "
                             "contre %d" % (jeu, avec, sans))

    maxi = max(avec for _, avec, _ in JEUX)
    total = sum(avec - sans for _, avec, sans in JEUX)
    echelle = (PISTE - 78) / float(maxi)

    barre = 22
    ligne_h = 2 * barre + 2 + 46
    y_legende = 112
    y_lignes = 156
    y_fait = y_lignes + len(JEUX) * ligne_h + 34
    y_pied = y_fait + 58
    #  Le doublement du signe pour cent n'a pas lieu d'être : ces lignes ne
    #  passent pas par un formatage. Écrit « %% », il sortait « %% ».
    pied = (
        "Temps relevés par la chaîne YetTea, repris par 80 Level en mai "
        "2023. Les écarts, les rapports et le total sont calculés à partir "
        "de ces huit temps.",
        "Ces barres mesurent le DÉMARRAGE, pas les performances en jeu : "
        "TechPowerUp relève moins de 1 % d’écart quand la carte graphique "
        "limite, 3 à 4 % quand le processeur limite.",
        "Denuvo ne concerne que les grosses sorties. La quasi-totalité des "
        "jeux indépendants sortent sans protection, et la question ne se "
        "pose pas pour eux.",
    )
    H = y_pied + 18 + len(pied) * 24 + 40

    x_piste = MARGE + NOM + GOUTTIERE
    x_ecart = x_piste + PISTE + GOUTTIERE

    o = [rect("Fond", [0, 0, L, H], 0, D.PAPIER)]
    o.append(texte("Titre", (MARGE, 52), TITRE, "titre", D.ENCRE, 2.2))
    o.append(texte("Titre", (MARGE, 78), D.typo(SOUS), "sous", D.FAIBLE))

    x = MARGE
    for teinte, mot in ((VIOLET, "avec Denuvo"),
                        (VIOLET_DOUX, "sans Denuvo")):
        o.append(rect("Titre", [x, y_legende, x + 26, y_legende + 12], 6,
                      teinte))
        o.append(texte("Titre", (x + 36, y_legende - 4), D.typo(mot),
                       "petit", D.GRIS))
        x += 36 + large(mot, "petit") + 34
    if x > L - MARGE:
        raise SystemExit("la légende déborde")

    for i, (jeu, avec, sans) in enumerate(JEUX):
        y = y_lignes + i * ligne_h
        if i % 2 == 1:
            o.append(rect("Jeux", [MARGE, y - 12, L - MARGE,
                                   y + ligne_h - 14], 0, ZEBRE))
        if large(jeu, "nom") > NOM:
            raise SystemExit("« %s » déborde de sa colonne" % jeu)
        o.append(texte("Jeux", (MARGE, y + 4), D.typo(jeu), "nom", D.ENCRE))
        o.append(texte("Jeux", (MARGE, y + 28),
                       D.typo("%s fois plus long" % ("%.1f" % (avec / sans))
                              .replace(".", ",")), "petit", D.FAIBLE))

        for j, (valeur, teinte) in enumerate(((avec, VIOLET),
                                              (sans, VIOLET_DOUX))):
            yb = y + j * (barre + 2)
            w = valeur * echelle
            o.append(rect("Jeux", [x_piste, yb, x_piste + w, yb + barre], 6,
                          teinte))
            o.append(texte("Jeux", (x_piste + w + 12, yb + 2),
                           secondes(valeur), "valeur", D.ENCRE))

        o.append(texte("Jeux", (x_ecart, y + 12),
                       "+ %s" % secondes(avec - sans), "ecart", VIOLET))

    fait = ("Sur ces quatre jeux, un lancement de chacun coûte %s de plus "
            "avec la protection." % duree(total))
    if large(fait, "fait") > L - 2 * MARGE:
        raise SystemExit("le bandeau déborde")
    o.append(trait("Bandeau", [MARGE, y_fait - 22, L - MARGE, y_fait - 22],
                   D.FILET, 2))
    o.append(texte("Bandeau", (MARGE, y_fait), D.typo(fait), "fait", VIOLET))

    o.append(trait("Pied", [MARGE, y_pied, L - MARGE, y_pied], D.FILET, 2))
    for i, ligne in enumerate(pied):
        if large(ligne, "pied") > L - 2 * MARGE:
            raise SystemExit("la ligne %d du pied déborde" % (i + 1))
        o.append(texte("Pied", (MARGE, y_pied + 18 + i * 24), D.typo(ligne),
                       "pied", D.FAIBLE))

    return H, o, total


def rendre_matriciel(H, ordres):
    t = D.Toile(L, H)
    fontes = {k: t.police(f, taille) for k, (f, taille, _) in POLICES.items()}
    for a in ordres:
        if a["quoi"] == "rect":
            t.rrect(a["b"], a["r"], teinte=a["t"])
        elif a["quoi"] == "trait":
            t.ligne(a["b"], a["t"], a["e"])
        elif a["tr"]:
            t.espace(a["xy"], a["c"], fontes[a["p"]], a["t"], a["tr"])
        else:
            t.texte(a["xy"], a["c"], fontes[a["p"]], a["t"])
    D.enregistrer(t.final(L, H), BASE, L, H)


def rendre_svg(H, ordres):
    """Un SVG à ouvrir dans Inkscape : du vrai texte, des calques nommés."""
    #  PIL pose un texte par son coin haut-gauche, SVG par sa ligne de base.
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
    for nom, t in (("violet", VIOLET), ("violet doux", VIOLET_DOUX)):
        if C.contraste(t, C.FOND) < 3.0:
            raise SystemExit("l'aplat %s ne se détache pas du fond" % nom)

    H, ordres, total = composer()
    rendre_matriciel(H, ordres)
    couches, textes = rendre_svg(H, ordres)
    print("  denuvo-temps-de-demarrage.svg              %d Ko"
          % round(os.path.getsize(BASE + ".svg") / 1024.0))
    print("  %d calques, %d textes éditables" % (couches, textes))
    for jeu, avec, sans in JEUX:
        print("    %-28s %3d s -> %3d s   + %3d s   x %.2f"
              % (jeu, avec, sans, avec - sans, avec / float(sans)))
    print("    total des écarts %s" % duree(total))


if __name__ == "__main__":
    principal()
