"""
L'autonomie promise contre l'autonomie mesurée.

    python3 article-pc-portable/autonomie_promesse_mesure.py

Produit `pc-portable-autonomie-promesse-mesure.png`, son WebP et le SVG.

----------------------------------------------------------------------------
QUATRE MACHINES, PAS SIX
----------------------------------------------------------------------------
Le brief en demande six. L'article ne publie les DEUX valeurs que pour
quatre d'entre elles. Pour le MacBook Neo, le MacBook Pro 14 et le
Zephyrus G16, il donne la mesure mais pas la promesse en lecture vidéo.

Dessiner six barres obligerait à inventer trois promesses, dans une
figure dont le seul sujet est l'écart entre ce qui est promis et ce qui
est mesuré. La table est donc à quatre entrées, et il suffit d'ajouter
les valeurs manquantes pour qu'elle en porte six.

----------------------------------------------------------------------------
LA MESURE EST DESSINÉE DANS LA PROMESSE
----------------------------------------------------------------------------
Deux barres côte à côte diraient « deux chiffres ». La mesure est posée
À L'INTÉRIEUR de la promesse : ce qui manque se voit alors comme un vide,
et c'est exactement ce dont parle la section.

----------------------------------------------------------------------------
LES DURÉES SONT SAISIES EN HEURES ET MINUTES
----------------------------------------------------------------------------
20 h 41 n'est pas 20,41 heures mais 20,683. Les durées sont donc écrites
en couples (heures, minutes) et converties une seule fois, au même
endroit. C'est la faute la plus facile à commettre sur ce genre de
tableau, et la plus difficile à repérer ensuite.

----------------------------------------------------------------------------
LES DEUX PROTOCOLES NE SONT PAS LE MÊME EXERCICE
----------------------------------------------------------------------------
La promesse vient d'une lecture vidéo locale, écran assombri : un circuit
dédié décode l'image et le processeur dort. La mesure vient d'une
navigation web en Wi-Fi à 150 nits. Le sous-titre le dit, parce que sans
cette phrase la figure accuserait les fabricants de mentir alors qu'ils
mesurent simplement autre chose.
"""

import os

import charte as C
import dessin as D

L = 1600
MARGE = 56

INDIGO = C.VIOLET_TEXTE
INDIGO_PALE = (221, 211, 246)

#  ---------------------------------------------------------------------------
#  LES MACHINES
#
#  Durées en (heures, minutes). `source` nomme le laboratoire qui a mesuré.
#  Pour ajouter une machine, il suffit des deux durées et de la source.
#  ---------------------------------------------------------------------------
MACHINES = (
    {"nom": "Dell XPS 14", "marque": "windows",
     "promesse": (40, 27), "mesure": (20, 41), "source": "Tom’s Guide"},
    {"nom": "MacBook Air 13 M5", "marque": "apple",
     "promesse": (18, 0), "mesure": (16, 11), "source": "Notebookcheck"},
    {"nom": "Asus Zenbook 14 OLED", "marque": "windows",
     "promesse": (18, 0), "mesure": (9, 4), "source": "Laptop Mag"},
    {"nom": "Lenovo Legion 5", "marque": "windows",
     "promesse": (12, 30), "mesure": (7, 3), "source": "Tom’s Guide"},
)

#  Ce que l'article affirme sur les deux familles.
BORNES = {"windows": (45.0, 60.0), "apple": (75.0, 90.0)}
PLUS_ENDURANT = "Dell XPS 14"

LEGENDE = (("annoncé en lecture vidéo", INDIGO_PALE),
           ("mesuré en navigation web", INDIGO))

POLICES = {
    "titre": (C.POLICE_G, 19, "bold"),
    "sous": (C.POLICE_R, 17, "normal"),
    "legende": (C.POLICE_R, 14, "normal"),
    "nom": (C.POLICE_G, 18, "bold"),
    "source": (C.POLICE_R, 13, "normal"),
    "valeur": (C.POLICE_G, 15, "bold"),
    "mesure": (C.POLICE_R, 14, "normal"),
    "part": (C.POLICE_G, 19, "bold"),
    "echelle": (C.POLICE_R, 13, "normal"),
}
FAMILLE_SVG = "Liberation Sans, Arial, Helvetica, sans-serif"

TITRE = "L’AUTONOMIE PROMISE ET CELLE QU’ON MESURE"
SOUS = ("la promesse vient d’une lecture vidéo locale, écran assombri ; la "
        "mesure d’une navigation web en Wi-Fi à 150 nits")

X_NOM = MARGE
X_BARRE = 320
X_FIN = 1222
X_PART = 1356
Y_PREMIERE = 228
PAS = 92
HAUTEUR_BARRE = 32


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


def heures(hm):
    """(20, 41) vaut 20,683 heures, et surtout pas 20,41."""
    h, m = hm
    if not 0 <= m < 60:
        raise SystemExit("%d minutes : ce n'est pas une durée" % m)
    return h + m / 60.0


def duree(hm):
    h, m = hm
    return "%d h" % h if m == 0 else "%d h %02d" % (h, m)


def composer():
    mesure_t = D.Toile(L, 10)
    fontes = {k: mesure_t.police(f, t) for k, (f, t, _) in POLICES.items()}

    #  ------------------------------------------------------------------
    #  CONTRÔLES
    #  ------------------------------------------------------------------
    for m in MACHINES:
        m["p"] = heures(m["promesse"])
        m["m"] = heures(m["mesure"])
        if m["m"] > m["p"]:
            raise SystemExit(
                "%s : la mesure (%s) dépasse la promesse (%s), la barre "
                "pleine sortirait de la pâle"
                % (m["nom"], duree(m["mesure"]), duree(m["promesse"])))
        m["part"] = 100.0 * m["m"] / m["p"]

    #  Le classement va du plus endurant au moins endurant, sur la MESURE.
    for a, b in zip(MACHINES, MACHINES[1:]):
        if b["m"] > a["m"]:
            raise SystemExit(
                "la table n'est pas triée sur la mesure : %s (%s) précède "
                "%s (%s)" % (a["nom"], duree(a["mesure"]),
                             b["nom"], duree(b["mesure"])))

    #  Ce que la légende de l'article affirme sur chaque famille.
    for m in MACHINES:
        bas, haut = BORNES[m["marque"]]
        if not bas <= m["part"] <= haut:
            raise SystemExit(
                "%s tient %.1f %% de sa promesse, hors de la fourchette "
                "%.0f à %.0f %% annoncée pour les %s"
                % (m["nom"], m["part"], bas, haut, m["marque"]))

    champion = max(MACHINES, key=lambda m: m["m"])
    if champion["nom"] != PLUS_ENDURANT:
        raise SystemExit(
            "l'article désigne %s comme le plus endurant, le tableau donne "
            "%s" % (PLUS_ENDURANT, champion["nom"]))

    maxi = max(m["p"] for m in MACHINES)
    echelle = (X_FIN - X_BARRE) / maxi

    #  La durée la plus longue se pose après sa barre : elle doit rester à
    #  gauche de la colonne des pourcentages.
    plus_long = max((duree(m["promesse"]) for m in MACHINES), key=len)
    bout = X_FIN + 12 + mesure_t.mesure(plus_long, fontes["valeur"])
    if bout > X_PART - 16:
        raise SystemExit("« %s » finit à %d px et la colonne des parts "
                         "commence à %d" % (plus_long, bout, X_PART))

    o = []
    o.append(texte("titre", (MARGE, 46), TITRE, "titre", D.ENCRE, 2.2))
    lignes_s = mesure_t.couper(D.typo(SOUS), fontes["sous"], L - 2 * MARGE)
    if len(lignes_s) > 2:
        raise SystemExit("le sous-titre tient en %d lignes" % len(lignes_s))
    y = 74
    for ligne in lignes_s:
        o.append(texte("titre", (MARGE, y), ligne, "sous", D.FAIBLE))
        y += 24

    x = MARGE
    for libelle, teinte_l in LEGENDE:
        o.append(rect("titre", [x, y + 10, x + 22, y + 24], 4, teinte_l))
        o.append(texte("titre", (x + 32, y + 8), libelle, "legende", D.GRIS))
        x += 32 + mesure_t.mesure(libelle, fontes["legende"]) + 40

    #  ------------------------------------------------------------  échelle
    axe, graduations = [], []
    bas = Y_PREMIERE + (len(MACHINES) - 1) * PAS + HAUTEUR_BARRE + 26
    for e in range(0, int(maxi) + 1, 10):
        gx = X_BARRE + e * echelle
        axe.append(trait("échelle", [gx, Y_PREMIERE - 18, gx, bas],
                         D.FILET, 1))
        graduations.append(texte("échelle", (gx, bas + 8), "%d h" % e,
                                 "echelle", D.FAIBLE, centre=True))
    o.extend(axe)
    o.extend(graduations)

    #  -------------------------------------------------------------  barres
    noms, barres, valeurs, parts = [], [], [], []
    for i, m in enumerate(MACHINES):
        yb = Y_PREMIERE + i * PAS
        noms.append(texte("noms", (X_NOM, yb + 1), D.typo(m["nom"]), "nom",
                          D.ENCRE))
        noms.append(texte("noms", (X_NOM, yb + 25),
                          D.typo("mesuré par " + m["source"]), "source",
                          D.FAIBLE))

        lp = m["p"] * echelle
        lm = m["m"] * echelle
        barres.append(rect("barres", [X_BARRE, yb, X_BARRE + lp,
                                      yb + HAUTEUR_BARRE], 6, INDIGO_PALE))
        barres.append(rect("barres", [X_BARRE, yb, X_BARRE + lm,
                                      yb + HAUTEUR_BARRE], 6, INDIGO))

        valeurs.append(texte("valeurs", (X_BARRE + lp + 12, yb + 7),
                             duree(m["promesse"]), "valeur", D.GRIS))

        #  La mesure s'inscrit DANS sa propre barre, calée sur sa fin.
        #
        #  Premier jet : juste après la barre pleine, dans la part pâle.
        #  Chez le MacBook Air, qui tient 90 % de sa promesse, cet écart
        #  fait quarante pixels pour une étiquette qui en demande
        #  cinquante-cinq. Plus la machine est honnête, moins il y a de
        #  place : le placement était condamné d'avance.
        lab = duree(m["mesure"])
        large = mesure_t.mesure(lab, fontes["mesure"])
        if large > lm - 20:
            raise SystemExit(
                "%s : « %s » fait %d px pour une barre de %d px"
                % (m["nom"], lab, large, lm))
        valeurs.append(texte("valeurs", (X_BARRE + lm - 10 - large, yb + 8),
                             lab, "mesure", D.BLANC))

        parts.append(texte("parts", (X_PART, yb + 4),
                           "%d %%" % round(m["part"]), "part", INDIGO))

    o.extend(barres)
    o.extend(noms)
    o.extend(valeurs)
    o.extend(parts)

    H = int(bas + 56)
    o.insert(0, rect("fond", [0, 0, L, H], 0, D.PAPIER))
    return H, o


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
                        "pc-portable-autonomie-promesse-mesure")
    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5),
               ("indigo", INDIGO, 4.5))

    H, ordres = composer()
    rendre_matriciel(H, ordres, base)
    couches, textes = rendre_svg(H, ordres, base)

    print("  %-52s %.0f Ko"
          % (os.path.basename(base + ".svg"),
             os.path.getsize(base + ".svg") / 1024.0))
    print("  %d x %d, %d calques, %d textes" % (L, H, couches, textes))
    print()
    for m in MACHINES:
        print("  %-22s %8s promis, %8s mesuré   %5.1f %%"
              % (m["nom"], duree(m["promesse"]), duree(m["mesure"]),
                 m["part"]))


if __name__ == "__main__":
    principal()
