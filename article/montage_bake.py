"""
IMAGE 7 de l'article — le coût de la résolution et des surfels, mesuré.

    python3 article/montage_bake.py

Lit `article/mesures-bake.json` et produit
`article/surfel-resolution-temps-de-bake-mesures.webp`.

----------------------------------------------------------------------------
DEUX COLONNES, PARCE QU'IL Y A DEUX RÉGLAGES ET QU'ILS NE SE COMPORTENT PAS
PAREIL
----------------------------------------------------------------------------
On les confond volontiers — ce sont les deux curseurs du même panneau — mais
la campagne les sépare nettement :

  - la RÉSOLUTION du volume coûte du temps et presque pas de mémoire ;
  - la DENSITÉ DE SURFELS coûte du temps ET de la mémoire, et c'est elle qui
    finit par faire échouer la cuisson.

Les mettre côte à côte est donc le sujet de l'image, pas une commodité de
mise en page.

----------------------------------------------------------------------------
LA COLONNE QUI COMPTE EST LA DERNIÈRE
----------------------------------------------------------------------------
Un tableau de temps de calcul ne démontre rien tout seul : il montre qu'on
paye, pas qu'on paye pour rien. C'est l'écart à la référence qui porte la
démonstration, et il ne se lit qu'à côté du PLANCHER DE BRUIT — l'écart entre
deux cuissons du même réglage.

Tout réglage dont l'écart est sous ce plancher est indiscernable du réglage le
plus cher. La figure le dit en toutes lettres plutôt que de laisser le lecteur
comparer des décimales.
"""

import json
import os

from PIL import Image, ImageDraw, ImageFont

RACINE = os.path.dirname(os.path.abspath(__file__))
JOURNAL = os.path.join(RACINE, "mesures-bake.json")
SORTIE = os.path.join(RACINE, "surfel-resolution-temps-de-bake-mesures.webp")

MARGE = 34
BANDE_TITRE = 78
COL_L = 800
GOUTTIERE = 30
LIGNE_H = 40

ENCRE = (13, 13, 17)
BLANC = (238, 238, 243)
GRIS = (138, 138, 150)
FAIBLE = (104, 104, 116)
TEAL = (72, 224, 184)
ORANGE = (232, 146, 62)
ROUGE = (214, 118, 96)

POLICE_G = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
POLICE_R = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
POLICE_M = "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf"
POLICE_MG = "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"
QUALITE = 92


def nb(gabarit, valeur):
    return (gabarit % valeur).replace(".", ",")


def police(chemin, taille):
    try:
        return ImageFont.truetype(chemin, taille)
    except OSError:
        return ImageFont.load_default()


def duree(s):
    return nb("%.0f s", s) if s < 60 else nb("%.1f min", s / 60.0)


def principal():
    if not os.path.exists(JOURNAL):
        raise SystemExit("mesures absentes : %s\n        lancez d'abord "
                         "`python3 article/mesurer_bake.py`" % JOURNAL)
    d0 = json.load(open(JOURNAL))
    mes = {m["nom"]: m for m in d0["mesures"]}

    base = mes["resolution-11x12x6"]
    #  Le plancher de bruit : l'écart DIRECT entre deux cuissons du même
    #  réglage. Pas la différence de leurs écarts à la référence — deux images
    #  peuvent être à la même distance d'une troisième et très loin l'une de
    #  l'autre.
    pd = d0.get("plancher_direct")
    if not pd:
        raise SystemExit("plancher de bruit absent du journal : relancez "
                         "`python3 article/mesurer_bake.py`")
    bruit = pd["ecart_moyen"]

    serie_res = [m for n, m in mes.items() if n.startswith("resolution-")]
    serie_res.sort(key=lambda m: m["echantillons"])
    serie_sur = [m for n, m in mes.items() if n.startswith("surfel-")]
    serie_sur.sort(key=lambda m: m["surfels"])

    lignes = max(len(serie_res), len(serie_sur))
    L = MARGE * 2 + COL_L * 2 + GOUTTIERE
    H = (MARGE + BANDE_TITRE + 34 + 30 + LIGNE_H * (lignes + 1)
         + 40 + 130 + 46 + MARGE)
    out = Image.new("RGB", (L, H), ENCRE)
    d = ImageDraw.Draw(out, "RGBA")

    f_titre = police(POLICE_G, 32)
    f_col = police(POLICE_G, 25)
    f_tete = police(POLICE_R, 19)
    f_val = police(POLICE_M, 21)
    f_val_g = police(POLICE_MG, 21)
    f_txt = police(POLICE_R, 21)
    f_petit = police(POLICE_R, 19)

    d.rectangle([MARGE, MARGE + 14, MARGE + 10, MARGE + 46], fill=TEAL)
    d.text((MARGE + 24, MARGE + 10),
           "CE QUE COÛTE UNE CUISSON, ET CE QU'ELLE RAPPORTE",
           font=f_titre, fill=BLANC)

    def colonne(x, titre, sous, serie, etiquette_de):
        d.text((x, MARGE + BANDE_TITRE), titre, font=f_col, fill=BLANC)
        d.text((x, MARGE + BANDE_TITRE + 32), sous, font=f_petit, fill=FAIBLE)
        y = MARGE + BANDE_TITRE + 34 + 30
        cols = (x, x + 236, x + 400, x + 560)
        for c, t in zip(cols, ("réglage", "cuisson", "écart /255",
                               "pixels vus")):
            d.text((c, y), t, font=f_tete, fill=FAIBLE)
        y += 28
        d.line([x, y, x + COL_L - 20, y], fill=(46, 46, 56), width=1)

        for m in serie:
            y += 6
            echec = m.get("echec")
            etiquette = etiquette_de(m)
            gras = m["nom"] == base["nom"]
            f = f_val_g if gras else f_val
            d.text((cols[0], y), etiquette, font=f,
                   fill=BLANC if gras else GRIS)
            if echec:
                mo = echec.split("(")[-1].rstrip(").").strip()
                d.text((cols[1], y), "refusée — %s" % mo, font=f_val,
                       fill=ROUGE)
            else:
                d.text((cols[1], y), duree(m["cuisson_s"]), font=f,
                       fill=ORANGE if not gras else BLANC)
                sous_bruit = m["ecart_moyen"] <= bruit
                d.text((cols[2], y), nb("%.2f", m["ecart_moyen"]), font=f,
                       fill=TEAL if sous_bruit else (GRIS if not gras
                                                     else BLANC))
                d.text((cols[3], y), nb("%.1f %%", m["pixels_visibles_pc"]),
                       font=f, fill=GRIS if not gras else BLANC)
            y += LIGNE_H - 6
        return y

    #  Chaque colonne compose ses propres étiquettes : un triplet de
    #  résolution et un entier de densité n'ont pas la même forme, et un
    #  gabarit unique obligerait à tordre l'un des deux.
    yA = colonne(MARGE, "RÉSOLUTION DU VOLUME",
                 "densité de surfels fixée à %d" % base["surfels"],
                 serie_res,
                 lambda m: "%d × %d × %d" % tuple(m["resolution"]))
    yB = colonne(MARGE + COL_L + GOUTTIERE, "DENSITÉ DE SURFELS",
                 "résolution fixée à %d × %d × %d" % tuple(base["resolution"]),
                 serie_sur,
                 lambda m: "%d surfels" % m["surfels"])

    y = max(yA, yB) + 10
    d.line([MARGE, y, L - MARGE, y], fill=(46, 46, 56), width=1)
    y += 22

    plus_cher = max((m for m in serie_res + serie_sur if not m.get("echec")),
                    key=lambda m: m["cuisson_s"])
    rapport = plus_cher["cuisson_s"] / max(base["cuisson_s"], 0.001)
    indiscernables = [m for m in serie_res + serie_sur
                      if not m.get("echec") and m["ecart_moyen"] <= bruit
                      and m["cuisson_s"] > base["cuisson_s"]]

    d.text((MARGE, y), "CE QUE DISENT CES CHIFFRES", font=f_col, fill=BLANC)
    y += 36
    texte = [
        nb("Le plancher de bruit est de %.2f/255 : c'est l'écart entre DEUX "
           "cuissons du même réglage.", bruit),
        "Sous ce plancher, deux images ne sont pas seulement proches — elles "
        "sont indiscernables.",
        "",
        nb("Le réglage le plus cher qui passe coûte %.1f fois le temps du "
           "réglage retenu pour l'article,", rapport)
        + nb(" pour un écart de %.2f/255.", plus_cher["ecart_moyen"]),
    ]
    if indiscernables:
        texte.append(
            "%d réglages plus chers que celui de l'article rendent une image "
            "indiscernable de la référence." % len(indiscernables))
    texte.append(
        "La densité de surfels ne coûte pas que du temps : au-delà de "
        "%d elle est refusée faute de mémoire vidéo."
        % max((m["surfels"] for m in serie_sur if not m.get("echec")),
              default=0))
    for i, t in enumerate(texte):
        d.text((MARGE, y + i * 27), t, font=f_txt, fill=GRIS)

    yf = H - MARGE - 32
    d.line([MARGE, yf, L - MARGE, yf], fill=(46, 46, 56), width=1)
    pied = ("Blender %s · EEVEE Next · rendus de comparaison %d × %d, "
            "%d échantillons · %d échantillons de cuisson · référence %d × %d "
            "× %d, %d surfels"
            % (d0.get("blender", "4.5.12 LTS"), *d0["comparaison"],
               d0["echantillons_rendu"], d0["bake_samples"],
               *d0["reference"]["resolution"], d0["reference"]["surfels"]))
    d.text((MARGE, yf + 12), pied, font=f_petit, fill=FAIBLE)

    out.save(SORTIE, "WEBP", quality=QUALITE, method=6)
    print()
    print("  %d × %d" % out.size)
    print("  plancher de bruit : %.3f/255" % bruit)
    print("  %s  (%.0f Ko)"
          % (os.path.basename(SORTIE), os.path.getsize(SORTIE) / 1024))


if __name__ == "__main__":
    principal()
