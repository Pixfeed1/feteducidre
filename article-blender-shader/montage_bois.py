"""
Le même plateau, deux destinations pour un seul câble.

    SORTIE=/tmp/bl-bois python3 article-blender-shader/rendu_bois.py
    python3 article-blender-shader/montage_bois.py

Produit `blender-bois-vector-vs-distortion.webp` et son PNG.

----------------------------------------------------------------------------
CE QUE LA FIGURE DOIT PROUVER, ET QU'ELLE VÉRIFIE
----------------------------------------------------------------------------
La légende dit « un seul câble change de destination ». Deux choses doivent
donc être vraies, et le montage refuse la figure si l'une manque.

D'abord, le plateau de droite doit avoir des CERNES, c'est-à-dire une
texture ORIENTÉE : elle doit varier bien plus en travers de la planche que
dans sa longueur.

Ensuite, le plateau de gauche ne doit PAS être orienté. C'est le témoin, et
c'est lui qui donne son sens à l'autre : sans la mesure des deux, « regardez
comme c'est différent » resterait une affirmation.

Mesurer la direction plutôt que compter des alternances n'est pas un détail
de méthode, c'est le sujet même de la section : ce qu'un scalaire branché
dans une prise vectorielle détruit, c'est exactement la direction.

----------------------------------------------------------------------------
LES DEUX BRUNS SONT DITS
----------------------------------------------------------------------------
L'article donne les positions des curseurs du Color Ramp, pas les couleurs.
Elles sont donc un choix du dessinateur, et le pied de figure les écrit : un
lecteur qui refait le montage doit pouvoir retrouver l'image, pas s'en
approcher.
"""

import json
import os

import numpy as np
from PIL import Image

import charte as C
import dessin as D

RACINE = os.path.dirname(os.path.abspath(__file__))
TRAVAIL = os.environ.get("TRAVAIL", "/tmp/bl-bois")
BASE = os.path.join(RACINE, "blender-bois-vector-vs-distortion")

L = 1600
MARGE = 56
GOUTTIERE = 26

#  On ignore le pourtour du plateau, où le biseau du cube et l'ombre portée
#  ne disent rien de la texture.
BORD = 0.10

#  CE QU'ON MESURE, ET POURQUOI CELUI-LÀ.
#
#  Un premier jet comptait les alternances clair / sombre sur une bande
#  horizontale. Mauvaise idée, et mesuré comme tel : le plateau cassé en
#  donnait treize, autant que des cernes. Un moucheté alterne lui aussi, il
#  alterne simplement sans ordre — compter les alternances ne distingue donc
#  rien du tout.
#
#  Ce que le câble détruit, c'est la DIRECTION. On mesure donc celle-là : la
#  variation de haut en bas — en travers des cernes — contre la variation de
#  gauche à droite, le long des cernes. Une texture orientée donne beaucoup
#  plus que 1, un moucheté isotrope donne environ 1. Mesuré sur ce rendu :
#  0,83 pour le plateau cassé, 3,99 pour le plateau correct.
DIRECTION_MINIMALE = 2.0
DIRECTION_TEMOIN = 1.5

ETIQUETTES = {
    "Vector": ("Fac du Noise → Vector du Wave",
               "le scalaire recopié sur les trois axes"),
    "Distortion": ("Fac du Noise → ×8 → Distortion du Wave",
                   "le vecteur garde sa direction"),
}

TITRE = "UN SEUL CÂBLE CHANGE DE DESTINATION"
SOUS = "même plateau, même arbre, même rendu ; seule l’arrivée du fil change"


def virgule(x, chiffres=2):
    return (("%." + str(chiffres) + "f") % x).replace(".", ",")


def nombre(x):
    """Un réglage tel qu'il s'écrit : 1 et non 1.0, 0,25 et non 0.25."""
    return ("%g" % x).replace(".", ",")


def direction(vue, boite):
    """À quel point la texture est orientée : en travers contre le long.

    Moyenner une ligne entière divise le bruit du rendu par la racine du
    nombre de pixels et laisse intact ce qui est cohérent sur toute la
    largeur — un cerne. On compare donc la dispersion des moyennes de lignes
    à celle des moyennes de colonnes.
    """
    x, y, large, haut = boite
    m = int(haut * BORD)
    bloc = np.asarray(vue.convert("L"), dtype=np.float32)[
        y + m:y + haut - m, x + m:x + large - m]
    travers = float(bloc.mean(axis=1).std())
    le_long = float(bloc.mean(axis=0).std())
    return travers / le_long if le_long > 0 else float("inf")


def principal():
    fiche = os.path.join(TRAVAIL, "bois.json")
    rendu = os.path.join(TRAVAIL, "bois.png")
    if not os.path.exists(fiche) or not os.path.exists(rendu):
        raise SystemExit(
            "rendu absent : lancez d'abord\n"
            "  SORTIE=%s python3 article-blender-shader/rendu_bois.py"
            % TRAVAIL)

    with open(fiche, encoding="utf-8") as f:
        fait = json.load(f)
    brut = Image.open(rendu).convert("RGB")
    if list(brut.size) != fait["taille"]:
        raise SystemExit("le rendu ne fait pas la taille annoncée")

    v = fait["valeurs"]
    plateaux = fait["plateaux"]
    if [p["nom"] for p in plateaux] != ["Vector", "Distortion"]:
        raise SystemExit("les plateaux ne sont pas dans l'ordre de l'article")

    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5),
               ("violet", D.VIOLET, 4.5))

    a = np.asarray(brut, dtype=np.int16)
    if float((a >= 254).all(axis=2).mean()) > 0.005:
        raise SystemExit("le rendu comporte des aplats brûlés")

    mesures = {}
    for p in plateaux:
        mesures[p["nom"]] = direction(
            brut, (p["x"], p["y"], p["large"], p["haut"]))

    #  CONTRÔLE : la figure doit montrer ce que la légende annonce — d'un
    #  côté une texture orientée, de l'autre pas.
    if mesures["Distortion"] < DIRECTION_MINIMALE:
        raise SystemExit("le plateau correct n'est pas orienté (%s) : ce ne "
                         "sont pas des cernes"
                         % virgule(mesures["Distortion"]))
    if mesures["Vector"] > DIRECTION_TEMOIN:
        raise SystemExit("le plateau cassé reste orienté (%s) : le témoin ne "
                         "témoigne de rien" % virgule(mesures["Vector"]))

    # -----------------------------------------------------------  les vignettes
    large = (L - 2 * MARGE - GOUTTIERE) // 2
    vues = []
    for p in plateaux:
        #  On coupe au ras du plateau, le décor ne dit rien.
        vue = brut.crop((p["x"], p["y"],
                         p["x"] + p["large"], p["y"] + p["haut"]))
        if large > vue.width:
            raise SystemExit("le rendu serait agrandi")
        haut = int(round(large * vue.height / float(vue.width)))
        vues.append(vue.resize((large, haut), Image.LANCZOS))

    haut = max(v_.height for v_ in vues)
    y_nom = 150
    y_vue = y_nom + 60
    y_note = y_vue + haut + 20
    y_pied = y_note + 44
    H = y_pied + 18 + 4 * 24 + 40

    t = D.Toile(L, H)
    f_titre = t.police(C.POLICE_G, 17)
    f_sous = t.police(C.POLICE_R, 18)
    f_nom = t.police(C.POLICE_G, 20)
    f_note = t.police(C.POLICE_R, 16)
    f_pied = t.police(C.POLICE_R, 16)

    t.espace((MARGE, 52), TITRE, f_titre, D.ENCRE, 2.2)
    t.texte((MARGE, 78), D.typo(SOUS), f_sous, D.FAIBLE)

    for i, (p, vue) in enumerate(zip(plateaux, vues)):
        x = MARGE + i * (large + GOUTTIERE)
        nom, sous = ETIQUETTES[p["nom"]]
        teinte = D.VIOLET if p["nom"] == "Vector" else D.ENCRE
        for texte, police, couleur, dy in ((nom, f_nom, teinte, 0),
                                           (sous, f_note, D.GRIS, 30)):
            texte = D.typo(texte)
            if t.mesure(texte, police) > large:
                raise SystemExit("« %s » déborde de son panneau" % texte)
            t.texte((x, y_nom + dy), texte, police, couleur)

        t.im.paste(vue.resize((vue.width * t.e, vue.height * t.e),
                              Image.LANCZOS), (x * t.e, y_vue * t.e))
        t.rrect([x, y_vue, x + vue.width - 1, y_vue + vue.height - 1], 0,
                contour=D.FILET, epaisseur=2)
        #  Au-dessous de 1, « tant de fois plus marquée » ne veut rien dire :
        #  le témoin n'a pas une direction faible, il n'en a pas.
        m = mesures[p["nom"]]
        note = ("texture %s fois plus marquée en travers que le long"
                % virgule(m, 1) if m >= 1.5 else
                "aucune direction : %s, comme un moucheté" % virgule(m, 1))
        t.texte((x, y_note), D.typo(note), f_note, D.FAIBLE)

    # ---------------------------------------------------------------  le pied
    pied = (
        "Un seul rendu, Cycles, Blender %s, %d échantillons, caméra "
        "orthographique. Les deux arbres sortent de la même fonction ; le "
        "script vérifie qu'un seul lien diffère."
        % (fait["version"], fait["echantillons"]),
        "Texture Coordinate Object, Mapping Scale %s / %s / %s, Wave Rings "
        "direction Z profil Sine Scale %s Detail %d Detail Scale %d, Noise "
        "Scale %d Detail %d Roughness %s, Math Multiply %d."
        % (nombre(v["Mapping Scale"][0]), nombre(v["Mapping Scale"][1]),
           nombre(v["Mapping Scale"][2]), virgule(v["Wave Scale"], 1),
           v["Wave Detail"], v["Wave Detail Scale"], v["Noise Scale"],
           v["Noise Detail"], virgule(v["Noise Roughness"], 1),
           v["Multiply"]),
        "Color Ramp à %s et %s, Map Range %s à %s sur Roughness, Bump %s sur "
        "Normal. Les deux bruns, que l’article ne fixe pas : %s et %s en "
        "linéaire."
        % (virgule(v["Color Ramp"][0]), virgule(v["Color Ramp"][1]),
           virgule(v["Map Range To Min"]), virgule(v["Map Range To Max"]),
           virgule(v["Bump Strength"]),
           " / ".join(virgule(c, 3) for c in fait["brun_sombre"]),
           " / ".join(virgule(c, 3) for c in fait["brun_clair"])),
        "À gauche, un scalaire entre dans une prise qui attend trois nombres. "
        "Blender l’accepte sans rien signaler et recopie la valeur sur les "
        "trois axes : le vecteur perd sa direction, la texture ses cernes.",
    )
    t.ligne([MARGE, y_pied, L - MARGE, y_pied], D.FILET, 2)
    for i, ligne in enumerate(pied):
        ligne = D.typo(ligne)
        if t.mesure(ligne, f_pied) > L - 2 * MARGE:
            raise SystemExit("la ligne %d du pied déborde" % (i + 1))
        t.texte((MARGE, y_pied + 18 + i * 24), ligne, f_pied, D.FAIBLE)

    D.enregistrer(t.final(L, H), BASE, L, H)
    for p in plateaux:
        print("  %-12s orientation %.2f  (%dx%d px)"
              % (p["nom"], mesures[p["nom"]], p["large"], p["haut"]))


if __name__ == "__main__":
    principal()
