"""
La chaîne de synchronisation labiale, et où chaque outil s'arrête.

    python3 article-daz-lipsync/chaine_lipsync.py

Produit `daz-lipsync-chaine-outils` en .webp, .png et .svg.

----------------------------------------------------------------------------
LA FIGURE DIT CE QUE DIT LA LÉGENDE
----------------------------------------------------------------------------
« Tous ces outils font la même chose. Ils diffèrent surtout par l'endroit où
ils vous laissent tomber. » Une chaîne en haut, un outil par ligne, une barre
qui couvre les étages franchis et s'interrompt là où l'outil s'arrête. Le
lecteur voit les trous avant de lire un mot.

Ce n'est donc pas un schéma décoratif de la chaîne : c'est une carte de
couverture, et les segments non couverts sont l'information.

----------------------------------------------------------------------------
FACE MOJO SAUTE DEUX ÉTAGES, ET ÇA SE VOIT
----------------------------------------------------------------------------
Il ne travaille pas depuis l'audio : il capture un visage. Il n'y a donc chez
lui ni découpage en phonèmes ni traduction en visèmes. Sa barre est coupée en
deux, reliée par un pointillé, parce qu'une barre pleine prétendrait qu'il
fait une analyse phonétique qu'il ne fait pas.

----------------------------------------------------------------------------
CE QUI VIENT DE L'ARTICLE ET CE QUI VIENT DE MOI
----------------------------------------------------------------------------
Les étages de la chaîne, les prix, les limites et les dates sont ceux de
l'article. Le placement de chaque barre est une LECTURE de ces descriptions :
quand l'article dit que Rhubarb « rend un fichier » sans parler de Daz, la
barre s'arrête aux visèmes.

daz3d.com et developer.nvidia.com sont injoignables depuis cette machine.
Rien n'a été recoupé auprès des éditeurs, et le pied le dit.
"""

import os

import charte as C
import dessin as D

RACINE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(RACINE, "daz-lipsync-chaine-outils")

L = 1600
MARGE = 56
GOUTTIERE = 24

NOM = 260
PISTE = 745
ARRET = 435

VIOLET = (98, 44, 200)
VIOLET_PALE = (226, 216, 250)
ETEINT = (166, 168, 176)
ZEBRE = (244, 243, 238)

#  Les cinq étages, de la piste audio au rendu.
ETAGES = ("Source", "Phonèmes", "Visèmes", "Morphs Daz", "Rendu Iray")

#  (nom, précision, segments couverts, vivant, édition des phonèmes, arrêt)
#  Un segment est une paire d'étages, bornes comprises, numérotées à partir
#  de 1. Deux segments veulent dire que l'outil en saute.
OUTILS = (
    ("Module Lip-Sync 32 bits", "livré avec Daz Studio 32 bits",
     ((1, 4),), True, False,
     "Pas d’Iray en 32 bits. On enregistre la scène et on la rouvre en "
     "64 bits pour rendre."),
    ("Mimic Pro", "plus en vente depuis des années",
     ((1, 4),), False, True,
     "Figures Poser au format CR2, V4 et M4 seulement. Genesis 8 et 9 lui "
     "sont étrangers."),
    ("Mimic Live !", "arrêté, temps réel au micro",
     ((1, 4),), False, False,
     "Arrêté par Daz. Confirmé sur le forum officiel en juillet 2022, pour "
     "cause d’instabilités."),
    ("Anilip 2", "environ 89,95 $",
     ((1, 5),), True, False,
     "Couvre toutes les générations Genesis, mais pas de macOS."),
    ("Anilip3", "90,99 $",
     ((1, 5),), True, False,
     "Genesis 9 uniquement, et seulement sous Windows 11."),
    ("Face Mojo", "99,99 $, plus un iPhone X ou plus récent",
     ((1, 1), (4, 5)), True, False,
     "Capture faciale et non analyse audio : ni phonèmes ni visèmes. "
     "L’iPhone SE est exclu, faute de capteur."),
    ("Rhubarb Lip Sync", "gratuit, licence MIT",
     ((1, 3),), True, False,
     "Rend un fichier de formes de bouche. Le branchement sur la figure "
     "reste à écrire."),
    ("Papagayo et son script d’import", "gratuit",
     ((1, 4),), True, True,
     "Calage à l’aveugle : le personnage Daz n’est pas visible pendant "
     "l’édition des phonèmes."),
    ("NVIDIA Audio2Face", "gratuit, licence MIT",
     ((1, 3),), True, False,
     "Aucun plugin Daz. Passage par Blender, et la correspondance avec les "
     "morphs Genesis reste à écrire."),
)

POLICES = {
    "titre": (C.POLICE_G, 17, "bold"),
    "sous": (C.POLICE_R, 18, "normal"),
    "etage": (C.POLICE_G, 13, "bold"),
    "nom": (C.POLICE_G, 17, "bold"),
    "precision": (C.POLICE_R, 14, "normal"),
    "arret": (C.POLICE_R, 15, "normal"),
    "legende": (C.POLICE_R, 14, "normal"),
    "pied": (C.POLICE_R, 16, "normal"),
}
FAMILLE = "Liberation Sans, Arial, Helvetica, sans-serif"

TITRE = "OÙ CHAQUE OUTIL VOUS LAISSE TOMBER"
SOUS = "la chaîne, de la piste audio au rendu, et le segment que chacun couvre"

PIED = (
    "Étages, prix, limites et dates : ceux de l’article. Le placement des "
    "barres est une lecture de ces descriptions, pas un relevé.",
    "daz3d.com et developer.nvidia.com sont injoignables depuis la machine "
    "qui a produit cette figure : rien n’a été recoupé auprès des éditeurs.",
    "Audio2Face est sous licence MIT pour le SDK et les plugins Maya et "
    "Unreal. Audio2Emotion a une licence plus étroite, limitée à un usage "
    "avec Audio2Face.",
)


# ---------------------------------------------------------------  la partition
def rect(couche, b, r, teinte):
    return {"quoi": "rect", "couche": couche, "b": b, "r": r, "t": teinte}


def trait(couche, b, teinte, epaisseur, pointille=False):
    return {"quoi": "trait", "couche": couche, "b": b, "t": teinte,
            "e": epaisseur, "pointille": pointille}


def disque(couche, cx, cy, r, teinte, contour=None):
    return {"quoi": "disque", "couche": couche, "cx": cx, "cy": cy, "r": r,
            "t": teinte, "contour": contour}


def texte(couche, xy, contenu, police, teinte, tracking=0.0):
    #  PAS DE CADRATIN, ici comme dans Toile.texte : le SVG ne passe pas par
    #  le dessin matriciel, il lui faut son propre contrôle.
    for c, nom in (("—", "cadratin"), ("–", "demi-cadratin")):
        if c in contenu:
            raise SystemExit("%s dans « %s »" % (nom, contenu[:60]))
    return {"quoi": "texte", "couche": couche, "xy": xy, "c": contenu,
            "p": police, "t": teinte, "tr": tracking}


def composer():
    if NOM + PISTE + ARRET + 2 * GOUTTIERE != L - 2 * MARGE:
        raise SystemExit("les colonnes font %d px pour %d disponibles"
                         % (NOM + PISTE + ARRET + 2 * GOUTTIERE,
                            L - 2 * MARGE))

    mesure = D.Toile(L, 10)
    fontes = {k: mesure.police(f, t) for k, (f, t, _) in POLICES.items()}

    def couper(contenu, police, largeur):
        return mesure.couper(D.typo(contenu), fontes[police], largeur)

    def large(contenu, police):
        return mesure.mesure(D.typo(contenu), fontes[police])

    pas = PISTE / float(len(ETAGES))
    x_piste = MARGE + NOM + GOUTTIERE
    x_arret = x_piste + PISTE + GOUTTIERE

    plies = []
    for o in OUTILS:
        #  CONTRÔLE : un segment doit tenir dans la chaîne et aller de
        #  gauche à droite, sinon la barre raconte n'importe quoi.
        for a, b in o[2]:
            if not 1 <= a <= b <= len(ETAGES):
                raise SystemExit("« %s » couvre un segment impossible : %s"
                                 % (o[0], (a, b)))
        nom = couper(o[0], "nom", NOM)
        precision = couper(o[1], "precision", NOM)
        arret = couper(o[5], "arret", ARRET)
        haut = max(len(nom) * 21 + len(precision) * 18,
                   len(arret) * 20, 46) + 26
        plies.append((nom, precision, arret, haut))

    y_etages = 158
    y_lignes = y_etages + 34
    hauteur = sum(p[3] for p in plies)
    y_pied = y_lignes + hauteur + 46
    H = y_pied + 18 + len(PIED) * 24 + 40

    o = [rect("Fond", [0, 0, L, H], 0, D.PAPIER)]
    o.append(texte("Titre", (MARGE, 52), TITRE, "titre", D.ENCRE, 2.2))
    o.append(texte("Titre", (MARGE, 78), D.typo(SOUS), "sous", D.FAIBLE))

    # --------------------------------------------------------  la légende
    x = MARGE
    for teinte, mot in ((VIOLET, "disponible aujourd’hui"),
                        (ETEINT, "arrêté ou plus en vente")):
        o.append(rect("Titre", [x, 110, x + 26, 122], 6, teinte))
        o.append(texte("Titre", (x + 36, 106), D.typo(mot), "legende",
                       D.GRIS))
        x += 36 + large(mot, "legende") + 34
    o.append(disque("Titre", x + 7, 116, 7, D.PAPIER, VIOLET))
    mot = "édition des phonèmes à la main"
    o.append(texte("Titre", (x + 24, 106), D.typo(mot), "legende", D.GRIS))
    if x + 24 + large(mot, "legende") > L - MARGE:
        raise SystemExit("la légende déborde")

    # --------------------------------------------------  les étages en tête
    for i, etage in enumerate(ETAGES):
        xc = x_piste + i * pas
        if large(etage, "etage") > pas - 10:
            raise SystemExit("« %s » déborde de son étage" % etage)
        o.append(texte("Chaine", (xc + 6, y_etages), etage.upper(), "etage",
                       D.GRIS, 1.2))
        if i:
            o.append(trait("Chaine", [xc, y_lignes - 8, xc,
                                      y_lignes + hauteur], D.FILET, 1))
    o.append(trait("Chaine", [x_piste, y_lignes - 8, x_piste + PISTE,
                              y_lignes - 8], D.ENCRE, 2))

    # ----------------------------------------------------------  les outils
    y = y_lignes
    for i, (u, (nom, precision, arret, haut)) in enumerate(zip(OUTILS,
                                                               plies)):
        if i % 2 == 1:
            o.append(rect("Outils", [MARGE, y, L - MARGE, y + haut], 0,
                          ZEBRE))
        teinte = VIOLET if u[3] else ETEINT
        encre = D.ENCRE if u[3] else D.GRIS

        yy = y + 13
        for ligne in nom:
            o.append(texte("Outils", (MARGE, yy), ligne, "nom", encre))
            yy += 21
        for ligne in precision:
            o.append(texte("Outils", (MARGE, yy + 2), ligne, "precision",
                           D.FAIBLE))
            yy += 18

        #  La barre de couverture, un morceau par segment continu.
        milieu = y + 22
        bouts = []
        for a, b in u[2]:
            x0 = x_piste + (a - 1) * pas + 5
            x1 = x_piste + b * pas - 5
            o.append(rect("Outils", [x0, milieu - 9, x1, milieu + 9], 9,
                          teinte))
            bouts.append((x0, x1))
        #  Le pointillé qui dit « ici, rien » entre deux morceaux.
        for (_, fin), (debut, _) in zip(bouts, bouts[1:]):
            o.append(trait("Outils", [fin + 4, milieu, debut - 4, milieu],
                           ETEINT, 2, pointille=True))
        #  L'anneau sur l'étage des phonèmes, pour qui laisse corriger.
        if u[4]:
            o.append(disque("Outils", x_piste + 1.5 * pas, milieu, 7,
                            D.PAPIER, VIOLET_PALE if not u[3] else VIOLET))

        yy = y + 13
        for ligne in arret:
            o.append(texte("Outils", (x_arret, yy), ligne, "arret", D.GRIS))
            yy += 20

        y += haut
        o.append(trait("Outils", [MARGE, y, L - MARGE, y], D.FILET, 1))

    o.append(trait("Pied", [MARGE, y_pied, L - MARGE, y_pied], D.FILET, 2))
    for i, ligne in enumerate(PIED):
        if large(ligne, "pied") > L - 2 * MARGE:
            raise SystemExit("la ligne %d du pied déborde" % (i + 1))
        o.append(texte("Pied", (MARGE, y_pied + 18 + i * 24), D.typo(ligne),
                       "pied", D.FAIBLE))

    return H, o


# -----------------------------------------------------------------  les rendus
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
                     contour=a["contour"], epaisseur=2)
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
                tirets = (' stroke-dasharray="9 7"' if a["pointille"]
                          else "")
                out.append('    <line x1="%g" y1="%g" x2="%g" y2="%g" '
                           'stroke="%s" stroke-width="%g"%s/>'
                           % (x0, y0, x1, y1, teinte(a["t"]), a["e"],
                              tirets))
            elif a["quoi"] == "disque":
                bord = ('' if not a["contour"] else
                        ' stroke="%s" stroke-width="2"' % teinte(a["contour"]))
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
               ("violet", VIOLET, 4.5))
    H, ordres = composer()
    rendre_matriciel(H, ordres)
    couches, textes = rendre_svg(H, ordres)
    print("  daz-lipsync-chaine-outils.svg              %d Ko"
          % round(os.path.getsize(BASE + ".svg") / 1024.0))
    print("  %d outils, %d étages, %d calques, %d textes"
          % (len(OUTILS), len(ETAGES), couches, textes))
    for u in OUTILS:
        couvert = sum(b - a + 1 for a, b in u[2])
        print("    %-34s %d/%d étages%s"
              % (u[0], couvert, len(ETAGES), "" if u[3] else "  (arrêté)"))


if __name__ == "__main__":
    principal()
