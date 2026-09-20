"""
Cinq plateformes, deux modèles, et trois colonnes presque vides.

    python3 article-graphistes-freelances/tableau_plateformes.py

Produit `plateformes-graphistes-comparatif` en .webp, .png et .svg.

----------------------------------------------------------------------------
UNE SEULE MISE EN PAGE, TROIS FICHIERS
----------------------------------------------------------------------------
Le SVG et l'image matricielle ne sont pas deux dessins qui se ressemblent :
`composer()` produit UNE liste d'ordres — des rectangles, des traits, des
disques, des textes, en coordonnées de la figure —, et deux rendus la lisent.
Écrire le SVG à part aurait marché le premier jour et divergé au second, à la
première correction faite d'un seul côté.

Le repli des textes est calculé une fois, avec les métriques réelles de la
police, et les deux sorties reçoivent les mêmes lignes déjà coupées.

----------------------------------------------------------------------------
CE QUE LE SVG DOIT ÊTRE POUR ÊTRE UTILISABLE
----------------------------------------------------------------------------
Il est fait pour être ouvert dans Inkscape et retouché, pas seulement affiché.
Donc : du vrai texte et non des courbes, des calques nommés, et une famille de
police avec des replis. Les ordonnées sont converties en LIGNES DE BASE, parce
que PIL pose un texte par son coin haut-gauche et SVG par sa ligne de base :
reprendre les mêmes nombres décalerait tout d'une hauteur de capitale.

----------------------------------------------------------------------------
LES CASES VIDES SONT LE RÉSULTAT, PAS UN TROU
----------------------------------------------------------------------------
Le relevé ne trouve qu'un seul prix d'entrée CHIFFRÉ sur cinq et deux
commissions chiffrées sur cinq. « Sur devis » est une réponse publique, mais
ce n'est pas un prix : les compter ensemble donnait quatre prix sur cinq et un
bandeau faux, ce que le garde-fou a refusé.

Il aurait été facile de combler le reste avec des ordres de grandeur
plausibles : c'est ce que font les comparatifs qu'on lit partout, et c'est ce
qui les rend inutiles.

----------------------------------------------------------------------------
UNE SEULE LIGNE EST VIOLETTE, ET C'EST LA THÈSE DE L'ARTICLE
----------------------------------------------------------------------------
L'article tient en une phrase : il n'y a pas cinq offres, il y en a deux. La
pastille de la colonne « Modèle » ne sert qu'à ça. Une seule plateforme fait
travailler des gens qui ne seront pas payés, et on la voit du premier coup
d'oeil sans lire une ligne.

----------------------------------------------------------------------------
CE QUI N'A PAS PU ÊTRE VÉRIFIÉ ICI
----------------------------------------------------------------------------
Les cinq sites sont hors de la liste d'autorisation de cette machine :
malt.fr, 99designs.fr, fiverr.com, graphiste.com et creads.com répondent tous
en échec de connexion. Aucun chiffre n'a donc été recoupé depuis ici. Le
tableau porte la date du relevé et le nomme comme un relevé, il ne s'approprie
pas une vérification qu'il n'a pas faite.
"""

import os

import charte as C
import dessin as D

RACINE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(RACINE, "plateformes-graphistes-comparatif")

L = 1600
MARGE = 56
RELEVE = "20 septembre 2026"

VIOLET = (98, 44, 200)
NEUTRE = (150, 152, 158)
ZEBRE = (244, 243, 238)

#  Ni « non relevé » ni « non relevée » : la case sert à la fois au prix,
#  masculin, et à la commission, féminine. Et « pas de chiffre public » dit
#  mieux ce qui est vrai que « non relevé », qui pourrait passer pour un
#  oubli du relevé.
INCONNU = "Pas de chiffre public"

#  Les polices, nommées une fois. Le SVG a besoin de la graisse et de la
#  taille en plus du fichier ; l'image matricielle n'a besoin que du fichier.
POLICES = {
    "titre": (C.POLICE_G, 17, "bold"),
    "sous": (C.POLICE_R, 18, "normal"),
    "tete": (C.POLICE_G, 14, "bold"),
    "nom": (C.POLICE_G, 18, "bold"),
    "cellule": (C.POLICE_R, 16, "normal"),
    "precision": (C.POLICE_R, 14, "normal"),
    "bandeau": (C.POLICE_G, 20, "bold"),
    "pied": (C.POLICE_R, 16, "normal"),
}
FAMILLE = "Liberation Sans, Arial, Helvetica, sans-serif"

#  Les colonnes, avec leur largeur. La commission prend le plus de place :
#  c'est la seule case où une plateforme écrit une phrase et non un nombre.
COLONNES = (("Plateforme", 296), ("Modèle", 272), ("Prix d’entrée", 250),
            ("Commission", 670))

#  (plateforme, précision, modèle, spéculatif, prix, précision, commission)
#  Tout vient du relevé du 20 septembre 2026. Rien n'est complété au jugé.
LIGNES = (
    ("99designs by Vista", "concours d’une semaine",
     "Concours", True,
     "289 €", "logo, entrée de gamme",
     INCONNU),
    ("Creads", "5 000 créatifs, 5 % retenus",
     "Mise en relation, encadrée", False,
     "Sur devis", "au forfait, une création un prix",
     INCONNU),
    ("Graphiste.com et Codeur.com", "groupe Freeland, 375 000 profils",
     "Mise en relation, sur devis", False,
     "Sur devis", "devis personnalisés des freelances",
     INCONNU),
    ("Malt", "plus d’un million de profils",
     "Mise en relation, directe", False,
     "Sur devis", "tarif journalier du freelance",
     "5 % HT de frais de service freelance. Sur certaines missions en "
     "France, en Belgique et en Espagne : 10 % HT, puis 5 % après six mois "
     "de mission. Pour un micro-entrepreneur non assujetti à la TVA, "
     "6 % et 12 % TTC."),
    ("Fiverr", "offre Pro : premier centile",
     "Mise en relation, catalogue", False,
     INCONNU, "le plus bas du lot, non chiffré",
     "20 % prélevés sur le vendeur, plus des frais côté acheteur qui "
     "varient selon le montant de la commande et ne sont pas chiffrés "
     "par le relevé."),
)

TITRE = "CINQ PLATEFORMES, DEUX MODÈLES"
SOUS = "ce que chacune publie avant que vous ne commandiez"

PIED = (
    "Relevé du %s sur les pages publiques et les centres d’aide des "
    "plateformes, plus le communiqué Freeland du 9 juin 2022. Les cinq "
    "sites étant" % RELEVE,
    "injoignables depuis la machine qui a produit cette figure, aucun "
    "chiffre n’a été recoupé ici : le tableau rapporte un relevé daté, il "
    "ne le vérifie pas.",
    "« Pas de chiffre public » ne veut pas dire qu’il n’y a pas de "
    "commission, mais que le relevé n’en a trouvé aucun montant affiché. "
    "C’est une information sur la plateforme, pas un trou dans le tableau.",
)


def lettres(n):
    """Les petits nombres s’écrivent en toutes lettres dans une phrase."""
    mots = ("zéro", "une", "deux", "trois", "quatre", "cinq", "six", "sept",
            "huit", "neuf")
    return mots[n] if n < len(mots) else str(n)


def chiffre(v):
    return any(c.isdigit() for c in v)


# ---------------------------------------------------------------  la partition
#
#  Un ordre de dessin, indépendant du rendu. `couche` sert de nom de calque
#  dans le SVG et ne sert à rien dans l'image matricielle.
def rect(couche, b, r, teinte):
    return {"quoi": "rect", "couche": couche, "b": b, "r": r, "t": teinte}


def trait(couche, b, teinte, epaisseur):
    return {"quoi": "trait", "couche": couche, "b": b, "t": teinte,
            "e": epaisseur}


def disque(couche, cx, cy, r, teinte):
    return {"quoi": "disque", "couche": couche, "cx": cx, "cy": cy, "r": r,
            "t": teinte}


def texte(couche, xy, contenu, police, teinte, tracking=0.0):
    #  PAS DE CADRATIN, ici comme dans Toile.texte : le SVG ne passe pas par
    #  le dessin matriciel, il lui faut donc son propre contrôle.
    for c, nom in (("—", "cadratin"), ("–", "demi-cadratin")):
        if c in contenu:
            raise SystemExit("%s dans « %s »" % (nom, contenu[:60]))
    return {"quoi": "texte", "couche": couche, "xy": xy, "c": contenu,
            "p": police, "t": teinte, "tr": tracking}


def composer():
    """La mise en page, une fois, en ordres de dessin."""
    if sum(w for _, w in COLONNES) != L - 2 * MARGE:
        raise SystemExit("les colonnes font %d px pour %d disponibles"
                         % (sum(w for _, w in COLONNES), L - 2 * MARGE))

    #  Les comptes du bandeau sont DÉRIVÉS des cases. Saisis à la main, ils
    #  survivraient à une correction du tableau en disant le contraire. Et ce
    #  qui compte n'est pas « la case est remplie » mais « la case porte un
    #  CHIFFRE » : « sur devis » est une réponse publique, pas un prix.
    prix = sum(1 for r in LIGNES if chiffre(r[4]))
    commissions = sum(1 for r in LIGNES if chiffre(r[6]))
    speculatifs = sum(1 for r in LIGNES if r[3])

    mesure = D.Toile(L, 10)
    fontes = {k: mesure.police(f, t) for k, (f, t, _) in POLICES.items()}

    def couper(contenu, police, largeur):
        return mesure.couper(D.typo(contenu), fontes[police], largeur)

    def large(contenu, police):
        return mesure.mesure(D.typo(contenu), fontes[police])

    plies = []
    for r in LIGNES:
        cases = (couper(r[0], "nom", COLONNES[0][1] - 24),
                 couper(r[2], "cellule", COLONNES[1][1] - 46),
                 couper(r[4], "cellule", COLONNES[2][1] - 24),
                 couper(r[6], "cellule", COLONNES[3][1] - 24))
        precisions = (couper(r[1], "precision", COLONNES[0][1] - 24),
                      couper(r[5], "precision", COLONNES[2][1] - 24))
        corps = max(len(c) for c in cases) * 21
        bas = max(len(p) for p in precisions) * 18
        plies.append((cases, precisions, corps + bas + 26))

    y_tete = 150
    y_table = y_tete + 30
    y_fait = y_table + sum(p[2] for p in plies) + 42
    y_pied = y_fait + 62
    H = y_pied + 18 + len(PIED) * 24 + 40

    o = [rect("Fond", [0, 0, L, H], 0, D.PAPIER)]

    o.append(texte("Titre", (MARGE, 52), TITRE, "titre", D.ENCRE, 2.2))
    o.append(texte("Titre", (MARGE, 78), D.typo(SOUS), "sous", D.FAIBLE))

    x = MARGE
    for teinte, mot in ((VIOLET, "le travail non retenu n’est pas payé"),
                        (NEUTRE, "pas de travail gratuit")):
        o.append(disque("Titre", x + 6, 116, 6, teinte))
        o.append(texte("Titre", (x + 20, 108), D.typo(mot), "precision",
                       D.GRIS))
        x += 20 + large(mot, "precision") + 32
    if x > L - MARGE:
        raise SystemExit("la légende déborde")

    x = MARGE
    for nom, w in COLONNES:
        o.append(texte("En-tetes", (x, y_tete), nom.upper(), "tete", D.GRIS,
                       1.4))
        x += w
    o.append(trait("En-tetes", [MARGE, y_table - 6, L - MARGE, y_table - 6],
                   D.ENCRE, 2))

    y = y_table
    for i, (r, (cases, precisions, haut)) in enumerate(zip(LIGNES, plies)):
        if i % 2 == 1:
            o.append(rect("Lignes", [MARGE, y, L - MARGE, y + haut], 0,
                          ZEBRE))

        x = MARGE
        yy = y + 14
        for ligne in cases[0]:
            o.append(texte("Lignes", (x, yy), ligne, "nom", D.ENCRE))
            yy += 21
        for ligne in precisions[0]:
            o.append(texte("Lignes", (x, yy + 2), ligne, "precision",
                           D.FAIBLE))
            yy += 18
        x += COLONNES[0][1]

        o.append(disque("Lignes", x + 6, y + 21, 6,
                        VIOLET if r[3] else NEUTRE))
        yy = y + 14
        for ligne in cases[1]:
            o.append(texte("Lignes", (x + 22, yy), ligne, "cellule",
                           VIOLET if r[3] else D.ENCRE))
            yy += 21
        x += COLONNES[1][1]

        yy = y + 14
        for ligne in cases[2]:
            o.append(texte("Lignes", (x, yy), ligne, "cellule",
                           D.FAIBLE if r[4] == INCONNU else D.ENCRE))
            yy += 21
        for ligne in precisions[1]:
            o.append(texte("Lignes", (x, yy + 2), ligne, "precision",
                           D.FAIBLE))
            yy += 18
        x += COLONNES[2][1]

        yy = y + 14
        for ligne in cases[3]:
            o.append(texte("Lignes", (x, yy), ligne, "cellule",
                           D.FAIBLE if r[6] == INCONNU else D.ENCRE))
            yy += 21

        y += haut
        o.append(trait("Lignes", [MARGE, y, L - MARGE, y], D.FILET, 1))

    fait = ("Un seul prix d’entrée chiffré sur %s, %s commissions chiffrées "
            "sur %s, et une seule plateforme qui fait travailler sans payer."
            % (lettres(len(LIGNES)), lettres(commissions),
               lettres(len(LIGNES))))
    if prix != 1 or speculatifs != 1:
        raise SystemExit("le bandeau est écrit au singulier mais les "
                         "chiffres ont changé : %d prix, %d concours"
                         % (prix, speculatifs))
    if large(fait, "bandeau") > L - 2 * MARGE:
        raise SystemExit("le bandeau déborde")
    o.append(texte("Bandeau", (MARGE, y_fait), D.typo(fait), "bandeau",
                   VIOLET))

    o.append(trait("Pied", [MARGE, y_pied, L - MARGE, y_pied], D.FILET, 2))
    for i, ligne in enumerate(PIED):
        if large(ligne, "pied") > L - 2 * MARGE:
            raise SystemExit("la ligne %d du pied déborde" % (i + 1))
        o.append(texte("Pied", (MARGE, y_pied + 18 + i * 24), D.typo(ligne),
                       "pied", D.FAIBLE))

    return H, o, (prix, commissions, speculatifs)


# -----------------------------------------------------------------  les rendus
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
    """Un SVG à ouvrir dans Inkscape : du vrai texte, des calques nommés."""
    #  PIL pose un texte par son coin haut-gauche, SVG par sa ligne de base.
    #  Sans cette conversion, tout le texte remonterait d'une capitale.
    montees = {}
    for cle, (chemin, taille, _) in POLICES.items():
        montees[cle] = C.police(chemin, taille).getmetrics()[0]

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
           '  <desc>%s. Relevé du %s.</desc>' % (propre(SOUS), RELEVE)]

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
                chemin, taille, graisse = POLICES[a["p"]]
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
    H, ordres, comptes = composer()
    rendre_matriciel(H, ordres)
    couches, textes = rendre_svg(H, ordres)
    poids = os.path.getsize(BASE + ".svg") / 1024.0
    print("  plateformes-graphistes-comparatif.svg      %d Ko"
          % round(poids))
    print("  %d calques, %d textes éditables, aucune courbe"
          % (couches, textes))
    print("  %d prix chiffré, %d commissions chiffrées, %d concours"
          % comptes)


if __name__ == "__main__":
    principal()
