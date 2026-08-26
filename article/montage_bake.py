"""
IMAGE 7 de l'article — le coût de la résolution et des surfels, mesuré.

    python3 article/montage_bake.py

Lit `article/mesures-bake.json` et produit
`article/surfel-resolution-temps-de-bake-mesures.webp`.

----------------------------------------------------------------------------
DEUX COLONNES, PARCE QUE LES DEUX RÉGLAGES FONT L'INVERSE L'UN DE L'AUTRE
----------------------------------------------------------------------------
On les confond volontiers : ce sont les deux curseurs du même panneau, et on
suppose que « plus fin » veut dire « plus lent » des deux côtés. La campagne
dit autre chose, et c'est le sujet de l'image :

  - la RÉSOLUTION du volume ne coûte presque rien. Multipliée par 352 en
    nombre d'échantillons, elle ajoute 11 % de temps de cuisson — et c'est
    elle qui change l'image.
  - la DENSITÉ DE SURFELS coûte tout le temps de calcul, plafonne vite en
    qualité, et finit par faire échouer la cuisson faute de mémoire.

----------------------------------------------------------------------------
CHAQUE SÉRIE SE COMPARE À SON PROPRE SOMMET
----------------------------------------------------------------------------
Les écarts affichés ne sont pas mesurés contre une référence commune mais
contre le réglage le plus fin DE LA MÊME SÉRIE. Sans ça les deux variables se
contaminent : la série des surfels est rendue en 11 × 12 × 6, et comparée à
une référence en 22 × 24 × 12 elle ne descendait jamais sous 14/255 — un
écart de RÉSOLUTION qu'on aurait mis sur le dos des surfels.

----------------------------------------------------------------------------
LE PLANCHER DE BRUIT VAUT ZÉRO, ET C'EST UNE INFORMATION
----------------------------------------------------------------------------
La campagne cuit deux fois le même réglage pour savoir en deçà de quel écart
on ne sait rien. Résultat : 0,000/255, pas un pixel de différence. La cuisson
d'EEVEE Next est donc DÉTERMINISTE, contrairement à ce que je supposais en
écrivant la campagne. Tout écart lu dans ce tableau est réel.
"""

import json
import os
import re

from PIL import Image, ImageDraw, ImageFont

RACINE = os.path.dirname(os.path.abspath(__file__))
JOURNAL = os.path.join(RACINE, "mesures-bake.json")
SORTIE = os.path.join(RACINE, "surfel-resolution-temps-de-bake-mesures.webp")

MARGE = 34
BANDE_TITRE = 82
COL_L = 790
GOUTTIERE = 34
LIGNE_H = 38
#  Hauteur réservée au titre de colonne PLUS son sous-titre PLUS la ligne
#  d'en-têtes. À 68 px le sous-titre passait sous les en-têtes : deux textes
#  posés à des offsets calculés séparément finissent toujours par se croiser.
TETE = 96

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

BASE = "resolution-11x12x6"          # le réglage retenu pour l'article


def nb(gabarit, valeur):
    """
    Un nombre écrit en français, DANS une phrase.

    La version naïve — `(gabarit % valeur).replace(".", ",")` — remplace tous
    les points de la chaîne, y compris ceux qui terminent les phrases. Sur
    cette figure ça donnait « Les surfels font l'inverse, Passé 20 » et un
    paragraphe qui se terminait par une virgule. On ne convertit donc que les
    points ENTOURÉS DE CHIFFRES.
    """
    return re.sub(r"(?<=\d)\.(?=\d)", ",", gabarit % valeur)


def police(chemin, taille):
    try:
        return ImageFont.truetype(chemin, taille)
    except OSError:
        return ImageFont.load_default()


def principal():
    if not os.path.exists(JOURNAL):
        raise SystemExit("mesures absentes : %s\n        lancez d'abord "
                         "`python3 article/mesurer_bake.py`" % JOURNAL)
    d0 = json.load(open(JOURNAL))
    mes = {m["nom"]: m for m in d0["mesures"]}
    base = mes[BASE]

    pd = d0.get("plancher_direct")
    if not pd:
        raise SystemExit("plancher de bruit absent du journal")
    bruit = pd["ecart_moyen"]

    res = sorted([m for n, m in mes.items() if n.startswith("resolution-")],
                 key=lambda m: m["echantillons"])
    sur = sorted([m for n, m in mes.items() if n.startswith("surfel-")],
                 key=lambda m: m["surfels"])

    L = MARGE * 2 + COL_L * 2 + GOUTTIERE
    lignes = max(len(res), len(sur))
    H = (MARGE + BANDE_TITRE + TETE + LIGNE_H * lignes
         + 42 + 40 + 27 * 7 + 44 + MARGE)
    out = Image.new("RGB", (L, H), ENCRE)
    d = ImageDraw.Draw(out, "RGBA")

    f_titre = police(POLICE_G, 31)
    f_col = police(POLICE_G, 25)
    f_tete = police(POLICE_R, 18)
    f_val = police(POLICE_M, 21)
    f_val_g = police(POLICE_MG, 21)
    f_txt = police(POLICE_R, 21)
    f_petit = police(POLICE_R, 18)

    d.rectangle([MARGE, MARGE + 16, MARGE + 10, MARGE + 48], fill=TEAL)
    d.text((MARGE + 24, MARGE + 12),
           "CE N'EST PAS LA RÉSOLUTION QUI COÛTE — CE SONT LES SURFELS",
           font=f_titre, fill=BLANC)

    def colonne(x, titre, sous, serie, etiquette_de):
        d.text((x, MARGE + BANDE_TITRE), titre, font=f_col, fill=BLANC)
        d.text((x, MARGE + BANDE_TITRE + 34), sous, font=f_petit, fill=FAIBLE)
        y = MARGE + BANDE_TITRE + TETE
        cols = (x, x + 250, x + 420, x + 590)
        for c, t in zip(cols, ("réglage", "cuisson", "écart /255",
                               "pixels vus")):
            d.text((c, y - 26), t, font=f_tete, fill=FAIBLE)
        d.line([x, y, x + COL_L - 24, y], fill=(46, 46, 56), width=1)
        y += 10

        for m in serie:
            gras = m["nom"] == BASE
            f = f_val_g if gras else f_val
            couleur = BLANC if gras else GRIS
            d.text((cols[0], y), etiquette_de(m), font=f, fill=couleur)
            if m.get("echec"):
                #  Le refus est une mesure : on l'écrit avec les autres.
                mo = m["echec"].split("(")[-1].split(")")[0].strip()
                d.text((cols[1], y), "refusée — %s" % mo, font=f_val,
                       fill=ROUGE)
            else:
                sommet = m.get("ecart_serie", 0.0) <= bruit
                d.text((cols[1], y), nb("%.1f s", m["cuisson_s"]), font=f,
                       fill=BLANC if gras else ORANGE)
                d.text((cols[2], y),
                       "référence" if sommet
                       else nb("%.2f", m["ecart_serie"]),
                       font=f, fill=TEAL if sommet else couleur)
                d.text((cols[3], y),
                       "—" if sommet else nb("%.0f %%", m["pixels_serie_pc"]),
                       font=f, fill=couleur)
            y += LIGNE_H
        return y

    yA = colonne(MARGE, "RÉSOLUTION DU VOLUME",
                 "densité de surfels fixée à %d · écarts mesurés contre le "
                 "plus fin de la colonne" % base["surfels"],
                 res, lambda m: "%d × %d × %d" % tuple(m["resolution"]))
    yB = colonne(MARGE + COL_L + GOUTTIERE, "DENSITÉ DE SURFELS",
                 "résolution fixée à %d × %d × %d · écarts mesurés contre le "
                 "plus fin de la colonne" % tuple(base["resolution"]),
                 sur, lambda m: "%d surfels" % m["surfels"])

    #  Les rapports qui portent la conclusion, tous calculés sur les mesures.
    r_bas, r_haut = res[0], res[-1]
    gain_ech = r_haut["echantillons"] / float(r_bas["echantillons"])
    gain_tps = 100.0 * (r_haut["cuisson_s"] / r_bas["cuisson_s"] - 1.0)
    ok = [m for m in sur if not m.get("echec")]
    palier = min(ok, key=lambda m: abs(m["surfels"] - 20))
    s_haut = ok[-1]
    fois = s_haut["cuisson_s"] / palier["cuisson_s"]
    refus = next((m for m in sur if m.get("echec")), None)

    y = max(yA, yB) + 22
    d.line([MARGE, y, L - MARGE, y], fill=(46, 46, 56), width=1)
    y += 24
    d.text((MARGE, y), "CE QUE DISENT CES CHIFFRES", font=f_col, fill=BLANC)
    y += 42

    texte = [
        nb("La résolution est presque gratuite : × %.0f échantillons",
           gain_ech)
        + nb(" pour + %.0f %% de temps de cuisson — et c'est elle qui change",
             gain_tps)
        + " l'image.",
        nb("De 3 × 3 × 2 à 22 × 24 × 12, l'écart tombe de %.1f/255 à zéro.",
           r_bas["ecart_serie"]),
        "",
        nb("Les surfels font l'inverse. Passé %d, le gain est fini :",
           palier["surfels"])
        + nb(" on paie %.1f fois le temps", fois)
        + nb(" pour %.2f/255 d'écart.", palier["ecart_serie"]),
    ]
    if refus:
        texte.append("Et au-delà de %d surfels, la cuisson n'est plus lente : "
                     "elle est refusée, faute de mémoire vidéo."
                     % s_haut["surfels"])
    texte += [
        "",
        nb("Plancher de bruit : %.2f/255. Deux cuissons du même réglage "
           "donnent la même image au pixel près —", bruit)
        + " la cuisson est déterministe, donc tout écart ci-dessus est réel.",
    ]
    for i, t in enumerate(texte):
        d.text((MARGE, y + i * 27), t, font=f_txt, fill=GRIS)

    yf = H - MARGE - 30
    d.line([MARGE, yf, L - MARGE, yf], fill=(46, 46, 56), width=1)
    d.text((MARGE, yf + 10),
           "Blender 4.5.12 LTS · EEVEE Next · rendus de comparaison "
           "%d × %d, %d échantillons · %d échantillons de cuisson · "
           "temps mesurés autour de l'opérateur de cuisson seul"
           % (*d0["comparaison"], d0["echantillons_rendu"],
              d0["bake_samples"]),
           font=f_petit, fill=FAIBLE)

    out.save(SORTIE, "WEBP", quality=QUALITE, method=6)
    print()
    print("  %d × %d" % out.size)
    print("  resolution : x%.0f echantillons pour +%.0f %% de temps"
          % (gain_ech, gain_tps))
    print("  surfels    : x%.1f de temps au-dela de %d pour %.2f/255"
          % (fois, palier["surfels"], palier["ecart_serie"]))
    print("  plancher de bruit : %.3f/255" % bruit)
    print("  %s  (%.0f Ko)"
          % (os.path.basename(SORTIE), os.path.getsize(SORTIE) / 1024))


if __name__ == "__main__":
    principal()
