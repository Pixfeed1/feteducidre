"""
Les cinq voies vers la 3D : ce qu'elles coûtent, ce qu'elles durent, et ce
qu'elles donnent en plus de la technique.

    python3 article-formation-3d/voies_formation.py

Produit `formation-3d-cinq-voies.webp`, son PNG et le SVG éditable.

----------------------------------------------------------------------------
CE QUE LA FIGURE REFUSE DE CHIFFRER
----------------------------------------------------------------------------
Le brief demande « son coût, sa durée » pour chacune des cinq voies. L'article
n'en donne que pour une partie :

  - le privé est chiffré, 7 000 à 11 000 euros par an sur cinq ans ;
  - l'alternance et l'autoformation sont à zéro, et l'article le dit ;
  - le consulaire et le public ne sont PAS chiffrés, l'article se contente
    d'écrire que le rapport « n'a rien à voir avec le privé classique » ;
  - la reconversion n'est pas chiffrée non plus, seulement « mobilisable avec
    un CPF ou un financement France Travail ».

Les deux cases vides sont donc écrites « non chiffré » et non remplies au
jugé. Un prix inventé dans une comparaison de prix ne se distingue plus d'un
prix relevé, et c'est la seule chose qu'un lecteur retiendra de la figure.
Même règle pour les durées : trois sont écrites, deux ne le sont pas.

----------------------------------------------------------------------------
LES TROIS MARQUES VIENNENT DU TEXTE, PAS DE MON AVIS
----------------------------------------------------------------------------
L'article nomme lui-même « les trois choses qu'une école vend vraiment » :
le regard de quelqu'un qui sait pourquoi votre travail ne fonctionne pas, le
rythme imposé qui fait finir les projets, et le carnet d'adresses. Ce sont
ces trois-là qui servent de colonnes, et rien d'autre.

Trois états, parce que « l'article dit que non » et « l'article n'en parle
pas » ne sont pas la même information :

  - disque plein : l'article l'affirme ;
  - anneau vide : l'article dit explicitement le contraire ;
  - tiret : l'article ne se prononce pas.

La reconversion en est l'exemple. L'article écrit qu'un format court achète
« un socle technique, pas le réseau ni les trois ans de pratique encadrée ».
Le réseau reçoit donc un anneau vide, c'est écrit noir sur blanc. Le regard
et le rythme reçoivent un tiret : le texte nie la DURÉE de l'encadrement, pas
son existence, et broder là-dessus serait lui faire dire autre chose.

----------------------------------------------------------------------------
LE FOND DE L'AFFAIRE, ET IL EST DANS LES LIGNES IDENTIQUES
----------------------------------------------------------------------------
Les trois premières voies portent les mêmes trois marques. Ça peut passer
pour une faiblesse de la figure ; c'est son résultat. Ce qui sépare une école
privée, les Gobelins et l'alternance n'est pas ce qu'on y apprend ni ce qu'on
y gagne autour, c'est la facture : de 55 000 euros à zéro, et à zéro on est
payé. La légende de l'article dit « un rapport coût sur réseau très
différent » ; la figure montre d'où vient l'écart.
"""

import os

import charte as C
import dessin as D

L = 1600
MARGE = 56

VIOLET = (98, 44, 200)
AMBRE = (180, 83, 9)

POLICES = {
    "titre": (C.POLICE_G, 19, "bold"),
    "sous": (C.POLICE_R, 17, "normal"),
    "entete": (C.POLICE_G, 13, "bold"),
    "nom": (C.POLICE_G, 21, "bold"),
    "statut": (C.POLICE_R, 14, "normal"),
    "cout": (C.POLICE_G, 25, "bold"),
    "vide": (C.POLICE_G, 18, "bold"),
    "duree": (C.POLICE_G, 18, "bold"),
    "plus": (C.POLICE_R, 15, "normal"),
    "pied": (C.POLICE_R, 16, "normal"),
    "num": (C.POLICE_G, 17, "bold"),
}
FAMILLE = "Liberation Sans, Arial, Helvetica, sans-serif"

TITRE = "LE MÊME MÉTIER, DE ZÉRO À 55 000 EUROS"
SOUS = ("cinq voies vers la 3D, ce qu’elles coûtent, ce qu’elles durent, et "
        "ce qu’elles donnent en plus de la technique")

#  ---------------------------------------------------------------------------
#  LES CINQ VOIES, TELLES QUE L'ARTICLE LES ÉCRIT
#
#  `chiffre` et `dure` disent si la valeur vient d'un chiffre publié dans le
#  texte ou si la case est vide. Les marques suivent l'ordre regard, rythme,
#  réseau, avec 1 pour affirmé, -1 pour nié, 0 pour non dit.
#  ---------------------------------------------------------------------------
VOIES = (
    {"nom": "École privée",
     "statut": "Rubika, ArtFX, ESMA, MoPA, Émile Cohl…",
     "cout": "35 000 à 55 000 €", "chiffre": True,
     "cout_note": "7 000 à 11 000 € par an",
     "duree": "5 ans", "dure": True,
     "duree_note": "majoritairement cinq ans",
     "plus": "Un réseau réel, qui vaut plus cher que le diplôme "
             "qu’il accompagne.",
     "marques": (1, 1, 1)},

    {"nom": "Consulaire et public",
     "statut": "Gobelins et ENSAD, sélection sur concours",
     "cout": "Non chiffré", "chiffre": False,
     "cout_note": "« rien à voir avec le privé »",
     "duree": "Non chiffrée", "dure": False,
     "duree_note": "un an de prépa en amont",
     "plus": "La même chose que le privé, pour un rapport entre ce qu’on "
             "paie et ce qu’on reçoit sans commune mesure.",
     "marques": (1, 1, 1)},

    {"nom": "Alternance",
     "statut": "plus d’un étudiant sur trois aux Gobelins",
     "cout": "0 €, et rémunéré", "chiffre": True,
     "cout_note": "l’entreprise finance la formation",
     "duree": "2 à 3 ans", "dure": True,
     "duree_note": "de production réelle",
     "plus": "Deux ou trois ans de production réelle au lieu d’un book "
             "d’exercices scolaires.",
     "marques": (1, 1, 1)},

    {"nom": "Reconversion",
     "statut": "Mon Compte Formation, France Travail, RNCP",
     "cout": "Non chiffré", "chiffre": False,
     "cout_note": "CPF ou France Travail",
     "duree": "Semaines à mois", "dure": True,
     "duree_note": "formats courts",
     "plus": "Un socle technique. L’article écrit : pas le réseau, ni les "
             "trois ans de pratique encadrée.",
     "marques": (0, 0, -1)},

    {"nom": "Autoformation",
     "statut": "Blender, documentation, tutoriels, livres",
     "cout": "0 €", "chiffre": True,
     "cout_note": "logiciel et documentation gratuits",
     "duree": "Non chiffrée", "dure": False,
     "duree_note": "« quelques années de plus »",
     "plus": "Rien des trois. Elles se reconstituent hors école, avec une "
             "discipline que personne ne vous imposera.",
     "marques": (-1, -1, -1)},
)

COLONNES = ("le regard", "le rythme", "le réseau")

#  Géométrie des colonnes, en x.
X_NOM = 132
X_COUT = 472
X_DUREE = 762
X_MARQUES = (984, 1056, 1128)
X_PLUS = 1192
LARGEUR_PLUS = L - MARGE - 14 - X_PLUS

HAUTEUR_BANDE = 108
PAS = 122

PIED = (
    "Les trois premières voies portent les mêmes trois marques, et c’est le "
    "résultat de la figure, pas sa faiblesse : ce qui les sépare n’est pas ce "
    "qu’on y gagne, c’est la facture.",
    "Deux des cinq voies n’ont pas de coût chiffré dans l’article et deux "
    "n’ont pas de durée. Elles portent « non chiffré » plutôt qu’un nombre "
    "vraisemblable, qui serait indiscernable d’un nombre relevé.",
    "Le regard, le rythme et le carnet d’adresses sont, mot pour mot, « les "
    "trois choses qu’une école vend vraiment ». Les marques ne disent que ce "
    "que le texte affirme ou nie.",
)


# ===========================================================================
#  ORDRES DE DESSIN
# ===========================================================================

def rect(couche, b, r, teinte):
    return {"quoi": "rect", "couche": couche, "b": b, "r": r, "t": teinte}


def cadre(couche, b, r, teinte, epaisseur=2):
    return {"quoi": "cadre", "couche": couche, "b": b, "r": r, "t": teinte,
            "e": epaisseur}


def trait(couche, b, teinte, epaisseur):
    return {"quoi": "trait", "couche": couche, "b": b, "t": teinte,
            "e": epaisseur}


def disque(couche, cx, cy, r, teinte, contour=None):
    return {"quoi": "disque", "couche": couche, "cx": cx, "cy": cy, "r": r,
            "t": teinte, "contour": contour}


def texte(couche, xy, contenu, police, teinte, tracking=0.0, centre=False):
    for c, nom in (("—", "cadratin"), ("–", "demi-cadratin")):
        if c in contenu:
            raise SystemExit("%s dans « %s »" % (nom, contenu[:60]))
    return {"quoi": "texte", "couche": couche, "xy": xy, "c": contenu,
            "p": police, "t": teinte, "tr": tracking, "centre": centre}


def marque(couche, cx, cy, etat):
    """Les trois états d'une marque, et ils ne veulent pas dire la même chose."""
    if etat == 1:
        return [disque(couche, cx, cy, 9, VIOLET)]
    if etat == -1:
        return [disque(couche, cx, cy, 9, D.BLANC, contour=(196, 190, 214))]
    return [trait(couche, [cx - 8, cy, cx + 8, cy], D.FAIBLE, 2)]


def composer():
    mesure = D.Toile(L, 10)
    fontes = {k: mesure.police(f, t) for k, (f, t, _) in POLICES.items()}

    #  ------------------------------------------------------------------
    #  CONTRÔLES AVANT DE DESSINER
    #  ------------------------------------------------------------------
    chiffres = sum(1 for v in VOIES if v["chiffre"])
    durees = sum(1 for v in VOIES if v["dure"])
    if chiffres != 3 or durees != 3:
        raise SystemExit(
            "l'article chiffre 3 coûts et 3 durées ; la table en compte "
            "%d et %d" % (chiffres, durees))
    #  Le titre annonce une fourchette : elle doit venir des données.
    hauts = [v["cout"] for v in VOIES if v["chiffre"] and "55 000" in v["cout"]]
    zeros = [v["cout"] for v in VOIES if v["chiffre"]
             and v["cout"].startswith("0 €")]
    if not hauts or len(zeros) < 2:
        raise SystemExit(
            "le titre annonce « de zéro à 55 000 euros » : il faut au moins "
            "une voie à 55 000 et deux à zéro dans la table")
    if "55 000" not in TITRE or "ZÉRO" not in TITRE:
        raise SystemExit("le titre ne reprend plus les bornes de la table")
    for v in VOIES:
        if len(v["marques"]) != len(COLONNES):
            raise SystemExit("%s : %d marques pour %d colonnes"
                             % (v["nom"], len(v["marques"]), len(COLONNES)))

    o = []
    y_entete = 150
    y0 = 176

    #  -------------------------------------------------------------  entête
    o.append(texte("titre", (MARGE, 46), TITRE, "titre", D.ENCRE, 2.2))
    sous = D.typo(SOUS)
    if mesure.mesure(sous, fontes["sous"]) > L - 2 * MARGE:
        raise SystemExit("le sous-titre déborde")
    o.append(texte("titre", (MARGE, 74), sous, "sous", D.FAIBLE))

    o.append(trait("titre", [MARGE, 128, L - MARGE, 128], D.FILET, 2))
    for libelle, x in (("la voie", X_NOM), ("ce qu’elle coûte", X_COUT),
                       ("combien de temps", X_DUREE),
                       ("en plus de la technique", X_PLUS)):
        o.append(texte("titre", (x, y_entete), libelle, "entete", D.GRIS))
    for libelle, x in zip(COLONNES, X_MARQUES):
        o.append(texte("titre", (x, y_entete), libelle, "entete", D.GRIS,
                       centre=True))

    #  -------------------------------------------------------------  bandes
    for i, v in enumerate(VOIES):
        y = y0 + i * PAS
        o.append(rect("cartes", [MARGE, y, L - MARGE, y + HAUTEUR_BANDE],
                      12, D.BLANC))
        o.append(cadre("cartes", [MARGE, y, L - MARGE, y + HAUTEUR_BANDE],
                       12, D.FILET, 2))

    for i, v in enumerate(VOIES):
        y = y0 + i * PAS
        o.append(disque("numéros", MARGE + 40, y + HAUTEUR_BANDE / 2, 18,
                        VIOLET))
        o.append(texte("numéros", (MARGE + 40, y + HAUTEUR_BANDE / 2 - 11),
                       str(i + 1), "num", D.BLANC, centre=True))

    #  LES MARQUES SONT MISES DE CÔTÉ, PUIS POSÉES D'UN BLOC.
    #
    #  Émises au fil des bandes, elles coupaient le calque « textes » en
    #  cinq, et le SVG sortait avec seize calques dont dix homonymes : dans
    #  Inkscape, cinq entrées « textes » et cinq « marques » qu'il faut
    #  ouvrir une à une pour savoir laquelle tient quoi. Regroupées, la
    #  figure garde sept calques nommés et manipulables.
    reportees = []
    for i, v in enumerate(VOIES):
        y = y0 + i * PAS

        o.append(texte("textes", (X_NOM, y + 22), D.typo(v["nom"]), "nom",
                       D.ENCRE))
        statut = D.typo(v["statut"])
        if mesure.mesure(statut, fontes["statut"]) > X_COUT - X_NOM - 24:
            raise SystemExit("le statut de %s déborde sur le coût" % v["nom"])
        o.append(texte("textes", (X_NOM, y + 56), statut, "statut", D.FAIBLE))

        cle = "cout" if v["chiffre"] else "vide"
        teinte = AMBRE if v["chiffre"] else D.GRIS
        cout = D.typo(v["cout"])
        if mesure.mesure(cout, fontes[cle]) > X_DUREE - X_COUT - 24:
            raise SystemExit("le coût de %s déborde sur la durée" % v["nom"])
        o.append(texte("textes", (X_COUT, y + 20 if v["chiffre"] else y + 24),
                       cout, cle, teinte))
        note = D.typo(v["cout_note"])
        if mesure.mesure(note, fontes["statut"]) > X_DUREE - X_COUT - 24:
            raise SystemExit("la note de coût de %s déborde" % v["nom"])
        o.append(texte("textes", (X_COUT, y + 60), note, "statut", D.FAIBLE))

        duree = D.typo(v["duree"])
        if mesure.mesure(duree, fontes["duree"]) > X_MARQUES[0] - 32 - X_DUREE:
            raise SystemExit("la durée de %s déborde sur les marques"
                             % v["nom"])
        o.append(texte("textes", (X_DUREE, y + 24), duree, "duree",
                       D.ENCRE if v["dure"] else D.GRIS))
        note = D.typo(v["duree_note"])
        if mesure.mesure(note, fontes["statut"]) > X_MARQUES[0] - 32 - X_DUREE:
            raise SystemExit("la note de durée de %s déborde sur les marques"
                             % v["nom"])
        o.append(texte("textes", (X_DUREE, y + 60), note, "statut", D.FAIBLE))

        for etat, x in zip(v["marques"], X_MARQUES):
            reportees.extend(marque("marques", x, y + 42, etat))

        lignes = mesure.couper(D.typo(v["plus"]), fontes["plus"],
                               LARGEUR_PLUS)
        if len(lignes) > 4:
            raise SystemExit("« en plus » tient en %d lignes pour %s"
                             % (len(lignes), v["nom"]))
        depart = y + HAUTEUR_BANDE / 2 - len(lignes) * 10 - 4
        for j, ligne in enumerate(lignes):
            o.append(texte("textes", (X_PLUS, depart + j * 21), ligne,
                           "plus", D.GRIS))

    o.extend(reportees)

    #  ---------------------------------------------------------------  pied
    y_pied = y0 + len(VOIES) * PAS + 18
    o.append(trait("pied", [MARGE, y_pied, L - MARGE, y_pied], D.FILET, 2))

    x = MARGE
    y_leg = y_pied + 32
    for etat, libelle in ((1, "l’article l’affirme"),
                          (-1, "l’article dit le contraire"),
                          (0, "l’article ne se prononce pas")):
        o.extend(marque("pied", x + 9, y_leg, etat))
        o.append(texte("pied", (x + 26, y_leg - 10), libelle, "statut",
                       D.GRIS))
        x += 26 + mesure.mesure(libelle, fontes["statut"]) + 46

    y_texte = y_leg + 26
    for i, ligne in enumerate(PIED):
        lignes = mesure.couper(D.typo(ligne), fontes["pied"], L - 2 * MARGE)
        if len(lignes) > 2:
            raise SystemExit("la ligne %d du pied tient en %d lignes"
                             % (i + 1, len(lignes)))
        for ligne_coupee in lignes:
            o.append(texte("pied", (MARGE, y_texte), ligne_coupee, "pied",
                           D.FAIBLE))
            y_texte += 24
        y_texte += 6

    H = int(y_texte + 22)
    o.insert(0, rect("fond", [0, 0, L, H], 0, D.PAPIER))
    return H, o


# ===========================================================================
#  LES DEUX RENDUS, DEPUIS LA MÊME LISTE D'ORDRES
# ===========================================================================

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
                     contour=a["contour"], epaisseur=3)
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
    """Le même dessin, en texte réel et en calques nommés pour Inkscape."""
    mesure = D.Toile(L, 10)
    fontes = {k: mesure.police(f, t) for k, (f, t, _) in POLICES.items()}
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
                bord = ('' if not a["contour"] else
                        ' stroke="%s" stroke-width="3"' % teinte(a["contour"]))
                out.append('    <circle cx="%g" cy="%g" r="%g" fill="%s"%s/>'
                           % (a["cx"], a["cy"], a["r"], teinte(a["t"]), bord))
            else:
                _, taille, graisse = POLICES[a["p"]]
                espacement = (' letter-spacing="%g"' % a["tr"]
                              if a["tr"] else "")
                x = a["xy"][0]
                if a["centre"]:
                    x -= mesure.mesure(a["c"], fontes[a["p"]]) / 2.0
                out.append('    <text x="%g" y="%g" font-family="%s" '
                           'font-size="%g" font-weight="%s" fill="%s"%s'
                           ' xml:space="preserve">%s</text>'
                           % (x, a["xy"][1] + montees[a["p"]], FAMILLE,
                              taille, graisse, teinte(a["t"]), espacement,
                              propre(a["c"])))
        out.append('  </g>')
    out.append('</svg>')

    with open(base + ".svg", "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    return len(couches), sum(1 for a in ordres if a["quoi"] == "texte")


def principal():
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "formation-3d-cinq-voies")
    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5),
               ("violet", VIOLET, 4.5), ("ambre", AMBRE, 4.5))

    H, ordres = composer()
    rendre_matriciel(H, ordres, base)
    couches, textes = rendre_svg(H, ordres, base)

    print("  %-44s %.0f Ko"
          % (os.path.basename(base + ".svg"),
             os.path.getsize(base + ".svg") / 1024.0))
    print("  %d calques, %d textes" % (couches, textes))
    print()
    noms = {1: "affirmé", -1: "nié", 0: "non dit"}
    for i, v in enumerate(VOIES):
        print("  %d. %-22s %-20s %-18s %s"
              % (i + 1, v["nom"],
                 v["cout"] if v["chiffre"] else "(non chiffré)",
                 v["duree"] if v["dure"] else "(non chiffrée)",
                 " ".join("%s:%s" % (c.split()[-1], noms[e])
                          for c, e in zip(COLONNES, v["marques"]))))
    print()
    print("  coûts chiffrés par l'article : %d sur %d"
          % (sum(1 for v in VOIES if v["chiffre"]), len(VOIES)))
    print("  durées chiffrées par l'article : %d sur %d"
          % (sum(1 for v in VOIES if v["dure"]), len(VOIES)))


if __name__ == "__main__":
    principal()
