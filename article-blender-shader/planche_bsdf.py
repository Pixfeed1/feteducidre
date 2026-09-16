"""
La planche des entrées du Principled BSDF, avec leurs valeurs de départ.

    python3 article-blender-shader/planche_bsdf.py          (Blender 5.2.1)
    python3 article-blender-shader/planche_bsdf.py 4.5      (Blender 4.5.12)

Produit `blender-principled-bsdf-32-entrees.webp` et son PNG.

----------------------------------------------------------------------------
RIEN N'EST RECOPIÉ : TOUT EST ÉNUMÉRÉ
----------------------------------------------------------------------------
Les noms, les types, les valeurs par défaut et jusqu'aux couleurs des prises
viennent de Blender, interrogé par son API (`enumerer.py`), et non d'une
capture relue ou d'un souvenir. Deux versions ont été passées : la 4.5.12 LTS
installée sur cette machine, la 5.2.1 LTS du conteneur. Les deux relevés sont
dans le dépôt, à côté de ce script.

----------------------------------------------------------------------------
IL Y EN A TRENTE-DEUX, PAS TRENTE ET UNE
----------------------------------------------------------------------------
L'article annonce trente et une entrées, relevées en 4.5 et recoupées en 5.0.
C'est exact pour ces versions-là. Mais l'article dit aussi que la version
courante est la 5.2.2, et la 5.2 en compte TRENTE-DEUX : une entrée « Thin
Wall » est venue s'intercaler en sixième position, juste après Alpha.

Une valeur par défaut a bougé au passage, elle aussi : « Subsurface Scale »
passe de 0,05 à 0,005.

Un lecteur qui ouvre Blender aujourd'hui compte donc trente-deux prises. La
planche est faite sur la 5.2 pour cette raison, et les deux écarts y sont
signalés — c'est le sujet même de l'avertissement qui ouvre l'article.

----------------------------------------------------------------------------
LES CINQ ESSENTIELLES SONT UN CHOIX, PAS UN RELEVÉ
----------------------------------------------------------------------------
Le reste de la planche est de la donnée ; ces cinq-là sont une opinion, et il
faut le dire. Ce sont celles qu'on touche pour passer d'une sphère grise à une
matière : la couleur, le caractère métallique ou non, l'état de surface, la
réfraction, et le relief. Alpha, qui figure pourtant en tête de liste chez
Blender, n'entre en jeu que pour la transparence.

Une ligne à changer dans ESSENTIELLES si l'article en retient d'autres.

----------------------------------------------------------------------------
UNE PLANCHE SOMBRE
----------------------------------------------------------------------------
Le reste des figures de ces articles est sur papier. Celle-ci ne l'est pas :
elle reprend le fond du node tel qu'il s'affiche dans l'éditeur, et les
couleurs de prises exactes de Blender. Le lecteur retrouve alors ses repères
d'un coup d'oeil — et « les cinq en blanc », que demandait le brief, n'a de
sens que sur un fond sombre.
"""

import json
import os
import sys

import charte as C
import dessin as D

RACINE = os.path.dirname(os.path.abspath(__file__))

#  Celles qu'on touche pour faire une matière. Voir l'en-tête : c'est un choix.
ESSENTIELLES = ("Base Color", "Metallic", "Roughness", "IOR", "Normal")

#  Les écarts entre la 4.5 et la 5.2, relevés par comparaison des deux
#  énumérations et non écrits à la main.
NOUVEAU = "nouveau en 5.x"
CHANGE = "0,05 en 4.5"

L = 1600
MARGE = 56
COLONNES = 2
LIGNE = 34                        # hauteur d'une ligne de la planche

#  Le fond du node et ses gris, relevés sur les captures de l'éditeur.
FOND = (42, 42, 44)
BLANC = (255, 255, 255)
GRIS_CLAIR = (172, 174, 180)
#  Éclairci après refus du contrôle : à (140, 142, 148) il ne faisait que
#  4,37:1 sur le fond du node, sous le seuil du texte courant.
GRIS_VALEUR = (150, 152, 158)
SEPARATEUR = (62, 62, 66)
BANDE = (56, 54, 66)

TYPES = (("VALUE", "valeur"), ("RGBA", "couleur"),
         ("VECTOR", "vecteur"), ("BOOLEAN", "booléen"))

LETTRES = {31: "trente et une", 32: "trente-deux"}


def teinte(couleur):
    return tuple(int(round(255 * c)) for c in couleur[:3])


def nombre(v):
    """Un flottant à la française, sans zéros inutiles."""
    s = ("%.4f" % v).rstrip("0").rstrip(".")
    return (s if s else "0").replace(".", ",")


def valeur(e):
    """La valeur par défaut, écrite comme Blender l'affiche."""
    v = e["defaut"]
    if e["type"] == "BOOLEAN":
        return "activé" if v else "désactivé"
    if isinstance(v, list):
        if e["type"] == "RGBA" and len(v) == 4 and v[3] == 1.0:
            v = v[:3]
        return ", ".join(nombre(x) for x in v)
    return nombre(v)


def ecart_de_version(version, entrees):
    """La phrase qui dit ce que l'autre version compte, en la comparant."""
    autre = "4.5" if version == "5.2" else "5.2"
    fiche = os.path.join(RACINE, "bsdf-%s.json" % autre)
    if not os.path.exists(fiche):
        return "Relevé unique : pas d’autre version à comparer."
    with open(fiche, encoding="utf-8") as f:
        ailleurs = json.load(f)

    ici = {e["nom"]: e for e in entrees}
    la_bas = {e["nom"]: e for e in ailleurs["entrees"]}
    ajoutees = [n for n in ici if n not in la_bas]
    bougees = [n for n in ici
               if n in la_bas and ici[n]["defaut"] != la_bas[n]["defaut"]]

    phrase = "La %s en compte %s" % (ailleurs["version"],
                                     LETTRES.get(len(la_bas), len(la_bas)))
    if ajoutees:
        phrase += " : « %s » n’y est pas" % ", ".join(ajoutees)
    if bougees:
        n = bougees[0]
        phrase += ", et « %s » y vaut %s" % (n, valeur(la_bas[n]))
    return phrase + "."


def principal():
    version = sys.argv[1] if len(sys.argv) > 1 else "5.2"
    fiche = os.path.join(RACINE, "bsdf-%s.json" % version)
    if not os.path.exists(fiche):
        raise SystemExit("relevé absent : %s" % os.path.basename(fiche))
    with open(fiche, encoding="utf-8") as f:
        releve = json.load(f)
    entrees = releve["entrees"]
    if len(entrees) != releve["nombre"]:
        raise SystemExit("le relevé ne se compte pas lui-même correctement")

    manquantes = [n for n in ESSENTIELLES
                  if n not in {e["nom"] for e in entrees}]
    if manquantes:
        raise SystemExit("essentielles absentes du relevé : %s"
                         % ", ".join(manquantes))

    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5))
    for nom, couleur in (("blanc", BLANC), ("gris clair", GRIS_CLAIR),
                         ("gris valeur", GRIS_VALEUR)):
        r = C.contraste(couleur, FOND)
        print("  %-12s sur le node   %.2f:1  %s"
              % (nom, r, "ok" if r >= 4.5 else "INSUFFISANT"))
        if r < 4.5:
            raise SystemExit("%s ne se lit pas sur le node" % nom)

    par_colonne = -(-len(entrees) // COLONNES)
    panneau_haut = 150
    panneau_bas = panneau_haut + 28 + par_colonne * LIGNE + 20
    legende = panneau_bas + 34
    y_pied = legende + 52
    H = y_pied + 18 + 2 * 24 + 40

    t = D.Toile(L, H)

    f_titre = t.police(C.POLICE_G, 17)
    f_sous = t.police(C.POLICE_R, 18)
    f_nom = t.police(C.POLICE_R, 17)
    f_nom_g = t.police(C.POLICE_G, 17)
    f_val = t.police(C.POLICE_R, 16)
    f_note = t.police(C.POLICE_R, 13)
    f_leg = t.police(C.POLICE_R, 15)
    f_pied = t.police(C.POLICE_R, 16)

    titre = "LES %d ENTRÉES DU PRINCIPLED BSDF" % len(entrees)
    t.espace((MARGE, 52), titre, f_titre, D.ENCRE, 2.2)
    t.texte((MARGE, 78), D.typo("et leurs valeurs de départ, relevées dans "
                                "Blender %s" % releve["version"]),
            f_sous, D.FAIBLE)

    t.rrect([MARGE, panneau_haut, L - MARGE, panneau_bas], 10, teinte=FOND)

    large = (L - 2 * MARGE) / float(COLONNES)
    for i, e in enumerate(entrees):
        col, rang = divmod(i, par_colonne)
        x = MARGE + col * large
        y = panneau_haut + 28 + rang * LIGNE
        essentielle = e["nom"] in ESSENTIELLES

        if essentielle:
            t.rrect([x + 10, y - 4, x + large - 14, y + LIGNE - 10], 6,
                    teinte=BANDE)
        elif rang:
            t.ligne([x + 26, y - 5, x + large - 14, y - 5], SEPARATEUR, 1)

        #  La pastille de la prise, à la couleur que Blender lui donne.
        t.disque(x + 30, y + 11, 7, teinte=teinte(e["couleur"]),
                 contour=(24, 24, 26), epaisseur=1)

        police = f_nom_g if essentielle else f_nom
        couleur = BLANC if essentielle else GRIS_CLAIR
        t.texte((x + 48, y), "%2d" % (i + 1), f_val, (108, 110, 116))
        t.texte((x + 78, y), e["nom"], police, couleur)

        #  Le repère de version, collé au nom qu'il concerne.
        note = None
        if e["nom"] == "Thin Wall":
            note = NOUVEAU
        elif e["nom"] == "Subsurface Scale" and version == "5.2":
            note = CHANGE
        if note:
            t.texte((x + 84 + t.mesure(e["nom"], police), y + 4), note, f_note,
                    (190, 160, 110))

        v = valeur(e)
        t.texte((x + large - 24 - t.mesure(v, f_val), y + 1), v, f_val,
                BLANC if essentielle else GRIS_VALEUR)

    # ------------------------------------------------------------  la légende
    x = MARGE
    for code, nom in TYPES:
        e = next((e for e in entrees if e["type"] == code), None)
        if e is None:
            continue
        t.disque(x + 7, legende + 10, 7, teinte=teinte(e["couleur"]),
                 contour=D.FILET, epaisseur=1)
        t.texte((x + 22, legende), nom, f_leg, D.GRIS)
        x += 30 + t.mesure(nom, f_leg) + 34
    #  Une pastille de la couleur de la bande se lirait presque noire sur le
    #  papier, et ne dirait rien. On dessine donc une miniature de la ligne
    #  mise en avant : le bandeau sombre, et le trait blanc du nom dedans.
    t.rrect([x, legende + 1, x + 30, legende + 19], 5, teinte=BANDE)
    t.rrect([x + 6, legende + 8, x + 24, legende + 12], 2, teinte=BLANC)
    t.texte((x + 42, legende),
            D.typo("les cinq qu'on touche pour faire une matière"), f_leg,
            D.ENCRE)

    # ---------------------------------------------------------------  le pied
    #  La seconde ligne du pied est DÉDUITE de la comparaison des deux
    #  relevés : écrite à la main, elle aurait menti sur la planche 4.5, où
    #  c'est la 5.2 qui fait figure d'autre version.
    pied = (
        "Noms, types, valeurs et couleurs de prises énumérés dans Blender "
        "%s par son API Python, non recopiés d’une capture."
        % releve["version"],
        ecart_de_version(version, entrees),
    )
    t.ligne([MARGE, y_pied, L - MARGE, y_pied], D.FILET, 2)
    for i, ligne in enumerate(pied):
        ligne = D.typo(ligne)
        if t.mesure(ligne, f_pied) > L - 2 * MARGE:
            raise SystemExit("la ligne %d du pied déborde" % (i + 1))
        t.texte((MARGE, y_pied + 18 + i * 24), ligne, f_pied, D.FAIBLE)

    base = os.path.join(RACINE,
                        "blender-principled-bsdf-%d-entrees" % len(entrees))
    D.enregistrer(t.final(L, H), base, L, H)
    print("  %d entrées, %d essentielles, Blender %s"
          % (len(entrees), len(ESSENTIELLES), releve["version"]))


if __name__ == "__main__":
    principal()
