"""
Ce que le sel change à une empreinte de mot de passe.

    python3 article-john/le_sel.py

Produit `john-the-ripper-le-sel.webp`, son PNG et le SVG éditable.

----------------------------------------------------------------------------
LES EMPREINTES SONT CALCULÉES, PAS INVENTÉES
----------------------------------------------------------------------------
Les quatre empreintes affichées sont de vrais SHA-256, calculés à
l'exécution. Écrire des suites hexadécimales plausibles aurait produit
la même image, mais un lecteur qui vérifie, et dans un article sur les
mots de passe il y en aura, trouverait des valeurs fausses.

Deux contrôles font la démonstration à la place du dessin : les deux
empreintes sans sel DOIVENT être égales, les deux empreintes salées
DOIVENT différer. Si un jour ce n'était plus vrai, la figure ne se
dessinerait pas.

----------------------------------------------------------------------------
LA TRONCATURE EST VÉRIFIÉE ELLE AUSSI
----------------------------------------------------------------------------
Une empreinte SHA-256 fait soixante-quatre caractères et ne tient pas
dans la largeur. Elle est donc coupée. Mais une coupe peut mentir : si
les deux empreintes salées partageaient leur début, la figure montrerait
deux lignes identiques alors que les empreintes diffèrent.

Un contrôle compare donc les PRÉFIXES affichés, pas seulement les
empreintes complètes.

----------------------------------------------------------------------------
ROUGE ET VERT, DANS LEUR EMPLOI RÉSERVÉ
----------------------------------------------------------------------------
La charte garde ces teintes aux figures qui opposent un état sain à un
état dégradé. C'en est une, et l'article est formel : sans sel, une
seule table suffit pour tous les comptes.

----------------------------------------------------------------------------
SHA-256 SERT D'EXEMPLE, ET L'ARTICLE DIT POURQUOI C'EST UN MAUVAIS CHOIX
----------------------------------------------------------------------------
La fonction nommée sur le schéma est SHA-256 parce qu'elle est
vérifiable à la main par le lecteur. Le mécanisme du sel est le même
quelle que soit la fonction. bcrypt et Argon2id, eux, fabriquent et
rangent leur sel eux-mêmes : on ne le leur ajoute pas.
"""

import hashlib
import os
import random

import charte as C
import dessin as D

L = 1600
MARGE = 56

ROUGE = C.ALERTE
VERT = C.VERT
PUCE = (238, 240, 246)

MOT_DE_PASSE = "soleil"
COMPTES = ("Alice", "Bob")
FONCTION = "SHA-256"

#  Les sels sont tirés une fois pour toutes, graine fixe, pour que la
#  figure soit reproductible. Un vrai système en tirerait un neuf par
#  compte, et ne les afficherait évidemment jamais.
GRAINE = 1996                 # l'année de naissance de John the Ripper
LONGUEUR_SEL = 32             # 16 octets en hexadécimal

CARACTERES_AFFICHES = 40      # de l'empreinte, le reste est coupé
SEL_AFFICHE = 12

POLICES = {
    "titre": (C.POLICE_G, 19, "bold"),
    "sous": (C.POLICE_R, 17, "normal"),
    "section": (C.POLICE_G, 17, "bold"),
    "compte": (C.POLICE_G, 17, "bold"),
    "puce": (C.POLICE_R, 15, "normal"),
    "fonction": (C.POLICE_G, 14, "bold"),
    "verdict": (C.POLICE_G, 16, "bold"),
    "symbole": (C.POLICE_G, 26, "bold"),
    "mention": (C.POLICE_R, 13, "normal"),
}
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
POLICES["empreinte"] = (MONO, 15, "normal")
FAMILLE_SVG = "Liberation Sans, Arial, Helvetica, sans-serif"
MONO_SVG = "DejaVu Sans Mono, Consolas, monospace"

TITRE = "LE SEL, OU POURQUOI DEUX FOIS LE MÊME MOT DE PASSE NE SE VOIT PLUS"
SOUS = ("empreintes SHA-256 réellement calculées pour le mot de passe "
        "« %s », sans sel puis avec un sel propre à chaque compte"
        % MOT_DE_PASSE)
MENTION = "empreintes tronquées à %d caractères sur 64" % CARACTERES_AFFICHES

X_NOM = 96
X_MDP = 196
X_SEL = 330
X_FONCTION = 606
X_EMPREINTE = 790
X_ACCOLADE = 1498

Y_SECTION = (176, 400)
HAUT_LIGNE = 54


def rect(couche, b, r, teinte):
    return {"quoi": "rect", "couche": couche, "b": b, "r": r, "t": teinte}


def trait(couche, b, teinte, epaisseur):
    return {"quoi": "trait", "couche": couche, "b": b, "t": teinte,
            "e": epaisseur}


def disque(couche, cx, cy, r, teinte):
    return {"quoi": "disque", "couche": couche, "cx": cx, "cy": cy, "r": r,
            "t": teinte}


def polygone(couche, points, teinte):
    return {"quoi": "polygone", "couche": couche, "p": points, "t": teinte}


def texte(couche, xy, contenu, police, teinte, tracking=0.0, centre=False):
    for c, nom in (("—", "cadratin"), ("–", "demi-cadratin")):
        if c in contenu:
            raise SystemExit("%s dans « %s »" % (nom, contenu[:60]))
    return {"quoi": "texte", "couche": couche, "xy": xy, "c": contenu,
            "p": police, "t": teinte, "tr": tracking, "centre": centre}


def empreinte(graine_texte):
    return hashlib.sha256(graine_texte.encode("utf-8")).hexdigest()


def composer():
    mesure = D.Toile(L, 10)
    fontes = {k: mesure.police(f, t) for k, (f, t, _) in POLICES.items()}

    #  ------------------------------------------------------------------
    #  LE CALCUL, PUIS LES CONTRÔLES QUI FONT LA DÉMONSTRATION
    #  ------------------------------------------------------------------
    alea = random.Random(GRAINE)
    sels = ["".join(alea.choice("0123456789abcdef")
                    for _ in range(LONGUEUR_SEL)) for _ in COMPTES]
    if sels[0] == sels[1]:
        raise SystemExit("les deux sels sont identiques : changez la graine")

    sans_sel = [empreinte(MOT_DE_PASSE) for _ in COMPTES]
    avec_sel = [empreinte(s + MOT_DE_PASSE) for s in sels]

    if sans_sel[0] != sans_sel[1]:
        raise SystemExit("sans sel, les deux empreintes diffèrent : la "
                         "figure dirait le contraire de ce qu'elle montre")
    if avec_sel[0] == avec_sel[1]:
        raise SystemExit("avec sel, les deux empreintes coïncident")

    coupe = lambda h: h[:CARACTERES_AFFICHES] + "…"
    #  LA TRONCATURE PEUT MENTIR : deux empreintes différentes qui
    #  partageraient leur début s'afficheraient identiques.
    if coupe(sans_sel[0]) != coupe(sans_sel[1]):
        raise SystemExit("les préfixes sans sel ne coïncident plus")
    if coupe(avec_sel[0]) == coupe(avec_sel[1]):
        raise SystemExit(
            "les deux empreintes salées partagent leurs %d premiers "
            "caractères : allongez l'affichage" % CARACTERES_AFFICHES)

    sections = (
        {"nom": "SANS SEL", "teinte": ROUGE, "sels": None,
         "empreintes": sans_sel, "symbole": "=",
         "verdict": "Deux fois la même empreinte. Une seule table suffit "
                    "pour les deux comptes."},
        {"nom": "AVEC UN SEL PROPRE À CHAQUE COMPTE", "teinte": VERT,
         "sels": sels, "empreintes": avec_sel, "symbole": "≠",
         "verdict": "Deux empreintes sans rapport. L’attaquant recommence "
                    "tout pour chaque compte."},
    )

    o = []
    o.append(texte("titre", (MARGE, 46), TITRE, "titre", D.ENCRE, 2.2))
    sous = D.typo(SOUS)
    if mesure.mesure(sous, fontes["sous"]) > L - 2 * MARGE:
        raise SystemExit("le sous-titre déborde")
    o.append(texte("titre", (MARGE, 74), sous, "sous", D.FAIBLE))

    sect, puces, fleches, textes_c, accolades = [], [], [], [], []
    bas = 0

    for s, y0 in zip(sections, Y_SECTION):
        sect.append(texte("sections", (MARGE, y0), s["nom"], "section",
                          s["teinte"]))
        y_lignes = []
        for i, compte in enumerate(COMPTES):
            y = y0 + 42 + i * HAUT_LIGNE
            y_lignes.append(y)

            textes_c.append(texte("lignes", (X_NOM, y + 4), compte, "compte",
                                  D.ENCRE))

            #  Le mot de passe, dans sa pastille.
            lp = mesure.mesure(MOT_DE_PASSE, fontes["puce"])
            puces.append(rect("pastilles", [X_MDP, y, X_MDP + lp + 26,
                                            y + 30], 8, PUCE))
            textes_c.append(texte("lignes", (X_MDP + 13, y + 6),
                                  MOT_DE_PASSE, "puce", D.ENCRE))

            if s["sels"]:
                lab = "+ sel " + s["sels"][i][:SEL_AFFICHE] + "…"
                ls = mesure.mesure(lab, fontes["puce"])
                if X_SEL + ls + 26 > X_FONCTION - 30:
                    raise SystemExit("la pastille de sel touche la fonction")
                puces.append(rect("pastilles", [X_SEL, y, X_SEL + ls + 26,
                                                y + 30], 8, PUCE))
                textes_c.append(texte("lignes", (X_SEL + 13, y + 6), lab,
                                      "puce", s["teinte"]))

            #  La flèche vers la fonction, puis vers l'empreinte.
            for xa, xb in ((X_SEL + 240 if s["sels"] else X_MDP + lp + 40,
                            X_FONCTION - 12),
                           (X_FONCTION + 150, X_EMPREINTE - 14)):
                fleches.append(trait("flèches", [xa, y + 15, xb, y + 15],
                                     D.FILET, 2))
                fleches.append(polygone("flèches",
                                        [(xb, y + 15), (xb - 9, y + 10),
                                         (xb - 9, y + 20)], D.FILET))

            puces.append(rect("pastilles", [X_FONCTION, y, X_FONCTION + 138,
                                            y + 30], 8, D.ENCRE))
            textes_c.append(texte("lignes", (X_FONCTION + 69, y + 7),
                                  FONCTION, "fonction", D.BLANC,
                                  centre=True))

            h = coupe(s["empreintes"][i])
            if X_EMPREINTE + mesure.mesure(h, fontes["empreinte"]) \
                    > X_ACCOLADE - 34:
                raise SystemExit("l'empreinte touche l'accolade")
            textes_c.append(texte("lignes", (X_EMPREINTE, y + 7), h,
                                  "empreinte", s["teinte"]))

        #  L'accolade qui compare les deux empreintes.
        ya, yb = y_lignes[0] + 15, y_lignes[-1] + 15
        accolades.append(trait("accolades", [X_ACCOLADE, ya, X_ACCOLADE, yb],
                               s["teinte"], 2))
        for yy in (ya, yb):
            accolades.append(trait("accolades",
                                   [X_ACCOLADE - 10, yy, X_ACCOLADE, yy],
                                   s["teinte"], 2))
        textes_c.append(texte("lignes", (X_ACCOLADE + 12,
                                         (ya + yb) / 2.0 - 18),
                              s["symbole"], "symbole", s["teinte"]))

        yv = y_lignes[-1] + 50
        verdict = D.typo(s["verdict"])
        if mesure.mesure(verdict, fontes["verdict"]) > L - X_NOM - MARGE:
            raise SystemExit("le verdict de « %s » déborde" % s["nom"])
        textes_c.append(texte("lignes", (X_NOM, yv), verdict, "verdict",
                              s["teinte"]))
        bas = max(bas, yv + 26)

    o.extend(sect)
    o.extend(fleches)
    o.extend(puces)
    o.extend(accolades)
    o.extend(textes_c)
    o.append(texte("mention", (MARGE, bas + 8), MENTION, "mention",
                   D.FAIBLE))

    H = int(bas + 50)
    o.insert(0, rect("fond", [0, 0, L, H], 0, D.PAPIER))
    return H, o, (sans_sel, avec_sel, sels)


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
        elif a["quoi"] == "polygone":
            t.polygone(a["p"], a["t"])
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
            elif a["quoi"] == "polygone":
                pts = " ".join("%g,%g" % p for p in a["p"])
                out.append('    <polygon points="%s" fill="%s"/>'
                           % (pts, teinte(a["t"])))
            else:
                _, taille, graisse = POLICES[a["p"]]
                famille = MONO_SVG if a["p"] == "empreinte" else FAMILLE_SVG
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
                        "john-the-ripper-le-sel")
    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5),
               ("rouge", ROUGE, 4.5), ("vert", VERT, 4.5))

    H, ordres, (sans, avec, sels) = composer()
    rendre_matriciel(H, ordres, base)
    couches, textes = rendre_svg(H, ordres, base)

    print("  %-36s %.0f Ko"
          % (os.path.basename(base + ".svg"),
             os.path.getsize(base + ".svg") / 1024.0))
    print("  %d x %d, %d calques, %d textes" % (L, H, couches, textes))
    print()
    print("  mot de passe : %s" % MOT_DE_PASSE)
    for n, h in zip(COMPTES, sans):
        print("  sans sel  %-6s %s" % (n, h))
    for n, s, h in zip(COMPTES, sels, avec):
        print("  avec sel  %-6s %s" % (n, h))
        print("            %s sel %s" % (" " * 6, s))
    print()
    print("  identiques sans sel  : %s" % (sans[0] == sans[1]))
    print("  différentes avec sel : %s" % (avec[0] != avec[1]))


if __name__ == "__main__":
    principal()
