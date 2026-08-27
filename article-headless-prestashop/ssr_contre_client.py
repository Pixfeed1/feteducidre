"""
IMAGE 3 de l'article « PrestaShop headless » — SSR contre rendu client.

    python3 article-headless-prestashop/ssr_contre_client.py

Produit `article-headless-prestashop/rendu-serveur-ssr-contre-rendu-client-indexation.webp`.

----------------------------------------------------------------------------
POURQUOI PAS LA LOUPE QUI NE VOIT RIEN
----------------------------------------------------------------------------
Le brief demandait une loupe Google qui ne voit rien devant une page blanche.
C'est l'image qu'on trouve partout, et elle est fausse depuis dix ans :
Googlebot exécute le JavaScript — il utilise un Chromium à jour — et indexe
la grande majorité des pages en rendu client. Publier « Google ne voit rien »
dans un article technique, c'est se faire reprendre par le premier lecteur qui
connaît le sujet, et perdre sa confiance pour le reste de l'article.

Ce qui est vrai, et qui suffit largement à justifier le SSR :

  - le HTML livré au robot est VIDE. Ça, c'est un fait, et c'est montrable ;
  - le contenu n'arrive qu'après exécution du JavaScript, mise en file
    d'attente et donc différée — de quelques minutes à plusieurs jours ;
  - ce second passage peut échouer : script en erreur, ressource bloquée,
    délai dépassé ;
  - et la plupart des AUTRES robots — réseaux sociaux, outils SEO, agrégateurs
    — n'exécutent pas de JavaScript du tout.

La figure montre donc la seule chose incontestable et vérifiable par le
lecteur lui-même : le code source des deux pages, côte à côte.

----------------------------------------------------------------------------
LA DÉMONSTRATION EST DANS LA COULEUR DU TEXTE
----------------------------------------------------------------------------
Les deux cartes de code utilisent la même règle : les balises en gris, le
texte lisible par un robot en noir. La colonne de gauche n'a donc AUCUN
caractère noir, la droite en a trois lignes. On voit la différence avant de
lire quoi que ce soit, et elle n'est pas une métaphore — c'est le contenu réel
des deux fichiers.
"""

import os

from PIL import Image, ImageDraw

import charte as C

RACINE = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(
    RACINE, "rendu-serveur-ssr-contre-rendu-client-indexation.webp")

L = 1600
MARGE = 60
COL_L = 730
GOUTTIERE = 20
Y0 = 128

BALISE = (138, 148, 166)         # les balises : présentes, mais muettes
VALEUR = (150, 122, 70)          # les attributs

#  Le code des deux pages. Chaque ligne est une suite de (texte, couleur) :
#  ce qu'un robot peut lire est en ENCRE, le reste en gris.
CLIENT = (
    [("<body>", BALISE)],
    [("  <div ", BALISE), ("id=\"__next\"", VALEUR), ("></div>", BALISE)],
    [("  <script ", BALISE), ("src=\"/_next/app.js\"", VALEUR),
     ("></script>", BALISE)],
    [("</body>", BALISE)],
)
SERVEUR = (
    [("<body>", BALISE)],
    [("  <h1>", BALISE), ("Fauteuil Lisbonne", C.ENCRE), ("</h1>", BALISE)],
    [("  <p ", BALISE), ("class=\"prix\"", VALEUR), (">", BALISE),
     ("49,90 €", C.ENCRE), ("</p>", BALISE)],
    [("  <p>", BALISE), ("Assise en chêne massif…", C.ENCRE),
     ("</p>", BALISE)],
    [("</body>", BALISE)],
)


def ligne_code(d, x, y, segments, f):
    """Une ligne de code, segment par segment, pour que la couleur porte le
    sens : gris ce qui ne dit rien, noir ce qu'un robot peut lire."""
    for texte, couleur in segments:
        d.text((x, y), texte, font=f, fill=couleur)
        x += d.textlength(texte, font=f)
    return x


#  LES DEUX CARTES ONT LA MÊME HAUTEUR, calculée sur la plus longue.
#  Dimensionnée sur son propre contenu, chaque carte prenait la hauteur de son
#  code — quatre lignes à gauche, cinq à droite — et tout ce qui suivait se
#  décalait d'un cran. Dans une figure de comparaison, deux colonnes qui ne
#  s'alignent pas donnent l'impression qu'on ne compare pas la même chose.
LIGNES_MAX = max(len(CLIENT), len(SERVEUR))


def colonne(d, x, titre, sous, teinte, code, lisible, etapes, polices):
    f_titre, f_sous, f_code, f_txt, f_petit, f_etape = polices

    d.rectangle([x, Y0, x + 10, Y0 + 32], fill=teinte)
    d.text((x + 24, Y0 - 4), titre, font=f_titre, fill=C.ENCRE)
    d.text((x + 24, Y0 + 36), sous, font=f_petit, fill=C.FAIBLE)

    #  LA CARTE DE CODE.
    yc = Y0 + 76
    hc = 34 + LIGNES_MAX * 30 + 22
    d.rounded_rectangle([x, yc, x + COL_L, yc + hc], radius=12,
                        fill=(250, 251, 253), outline=C.BORD, width=2)
    d.text((x + 22, yc + 12), "ce que le robot télécharge", font=f_petit,
           fill=C.FAIBLE)
    for i, segments in enumerate(code):
        ligne_code(d, x + 22, yc + 44 + i * 30, segments, f_code)

    #  CE QU'IL PEUT LIRE TOUT DE SUITE.
    y = yc + hc + 30
    d.text((x, y), "ce qu'il peut lire tout de suite", font=f_petit,
           fill=C.FAIBLE)
    d.text((x, y + 26), lisible, font=f_txt, fill=teinte)

    #  LES ÉTAPES QUI RESTENT.
    y += 78
    d.line([x, y, x + COL_L, y], fill=C.TRAIT, width=1)
    y += 22
    for i, (marque, texte) in enumerate(etapes):
        d.ellipse([x, y + 5 + i * 32, x + 12, y + 17 + i * 32], fill=teinte)
        d.text((x + 26, y + i * 32), texte, font=f_etape, fill=C.GRIS)
        if marque:
            d.text((x + 26 + d.textlength(texte, font=f_etape) + 10,
                    y + i * 32), marque, font=f_etape, fill=teinte)
    return y + len(etapes) * 32


def principal():
    C.verifier()

    #  La hauteur se déduit du contenu : on dessine une fois à blanc pour
    #  savoir où finit la colonne la plus longue.
    sonde = Image.new("RGB", (1, 1))
    ds = ImageDraw.Draw(sonde)

    polices = (C.police(C.POLICE_G, 29), C.police(C.POLICE_R, 20),
               C.police(C.POLICE_M, 20), C.police(C.POLICE_G, 24),
               C.police(C.POLICE_R, 18), C.police(C.POLICE_R, 20))

    gauche = dict(
        titre="RENDU CLIENT", sous="la page est fabriquée dans le navigateur",
        teinte=C.ALERTE, code=CLIENT,
        lisible="rien — le contenu n'est pas encore là",
        etapes=(("", "il faut exécuter le JavaScript"),
                ("", "ce second passage est mis en file d'attente"),
                ("", "il peut être différé de plusieurs jours, ou échouer"),
                ("", "les autres robots ne l'exécutent pas du tout")))
    droite = dict(
        titre="RENDU SERVEUR (SSR)", sous="la page arrive déjà écrite",
        teinte=C.VITRINE, code=SERVEUR,
        lisible="le titre, le prix, la description",
        etapes=(("", "aucune étape supplémentaire"),
                ("", "le même HTML pour tous les robots"),
                ("", "rien à mettre en file d'attente"),
                ("", "rien qui puisse échouer plus tard")))

    fin = max(colonne(ds, MARGE, polices=polices, **gauche),
              colonne(ds, MARGE + COL_L + GOUTTIERE, polices=polices,
                      **droite))
    H = int(fin + 46 + 88 + MARGE)

    out = Image.new("RGB", (L, H), C.FOND)
    d = ImageDraw.Draw(out, "RGBA")

    d.rectangle([MARGE, 44, MARGE + 10, 78], fill=C.VITRINE)
    d.text((MARGE + 24, 40),
           "LE MÊME PRODUIT, DEUX FICHIERS TRÈS DIFFÉRENTS",
           font=C.police(C.POLICE_G, 30), fill=C.ENCRE)

    colonne(d, MARGE, polices=polices, **gauche)
    colonne(d, MARGE + COL_L + GOUTTIERE, polices=polices, **droite)

    #  LA NUANCE, ÉCRITE. Sans elle la figure dirait « Google ne voit rien »,
    #  ce qui est faux et se retourne contre l'article.
    yf = fin + 46
    d.line([MARGE, yf, L - MARGE, yf], fill=C.TRAIT, width=1)
    f_bas = C.police(C.POLICE_R, 20)
    for i, t in enumerate((
            "Googlebot sait exécuter le JavaScript et indexe la plupart des "
            "pages en rendu client : l'enjeu n'est pas qu'il ne voie rien, "
            "c'est qu'il voie plus tard,",
            "sans garantie, et que les autres robots — réseaux sociaux, "
            "outils SEO, agrégateurs — ne voient jamais rien. Le rendu "
            "serveur supprime la question.")):
        d.text((MARGE, yf + 18 + i * 28), t, font=f_bas, fill=C.GRIS)

    out.save(SORTIE, "WEBP", quality=C.QUALITE, method=6)
    print()
    print("  %d × %d" % out.size)
    print("  %s  (%.0f Ko)"
          % (os.path.basename(SORTIE), os.path.getsize(SORTIE) / 1024))


if __name__ == "__main__":
    principal()
