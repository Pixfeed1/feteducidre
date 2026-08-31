"""
Image à la une de l'article « Onze questions à poser à une agence web ».

    python3 article-agence-web/onze_questions.py

Produit `article-agence-web/onze-questions-choisir-agence-web.webp`.

----------------------------------------------------------------------------
LES ONZE LIBELLÉS SONT À REMPLACER
----------------------------------------------------------------------------
Ceux d'ici sont une PROPOSITION : l'image est la liste, et une liste qui ne
correspond pas au texte de l'article la dessert au lieu de la servir. Ils sont
rassemblés dans `QUESTIONS`, une ligne chacun — les changer ne demande rien
d'autre que de réécrire ces onze chaînes et de relancer le script.

Le choix qui les guide : des questions dont la réponse ENGAGE. « Faites-vous
du responsive » n'apprend rien, tout le monde répond oui. « Qui sera
propriétaire du code » sépare les agences en deux camps dès la première
réunion.

----------------------------------------------------------------------------
FORMAT VERTICAL, DONC LISIBLE EN PETIT
----------------------------------------------------------------------------
Une image à la une est vue en vignette avant d'être vue en grand. Onze lignes
dans un format vertical, c'est peu de place par ligne : le texte est donc
composé au plus gros corps qui tienne, et le script REFUSE de produire la
figure si une question déborde sur trois lignes. Mieux vaut un script qui
s'arrête qu'une vignette illisible.

Le numéro est dans une pastille pleine plutôt qu'en simple chiffre : à la
taille d'une vignette, c'est la seule chose qui reste lisible, et elle suffit
à faire lire « une liste de onze points ».
"""

import os

from PIL import Image, ImageDraw

import charte as C

RACINE = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(RACINE, "onze-questions-choisir-agence-web.webp")

L, H = 1080, 1620               # 2/3, format vertical
MARGE = 64

TITRE = ("11 QUESTIONS", "À POSER À UNE AGENCE WEB", "AVANT DE SIGNER")

#  À REMPLACER par les onze questions de l'article.
QUESTIONS = (
    "Qui sera propriétaire du code et des accès ?",
    "Le site est-il livré avec ses fichiers sources ?",
    "Où est-il hébergé, et puis-je partir avec ?",
    "Que devient le site si on arrête ensemble ?",
    "Combien coûte une modification après la livraison ?",
    "Qui rédige les contenus, est-ce compris dans le prix ?",
    "Quelle technologie, et pourquoi celle-là ?",
    "Comment saura-t-on que le site fonctionne ?",
    "Qui applique les mises à jour de sécurité ?",
    "Quel délai, et que se passe-t-il en cas de retard ?",
    "Puis-je parler à deux de vos clients actuels ?",
)

PASTILLE = 52                    # diamètre de la pastille du numéro
COLONNE = 30                     # espace entre la pastille et le texte


def couper(d, texte, f, largeur):
    """Le texte replié sur la largeur disponible, mot à mot."""
    mots, ligne, lignes = texte.split(), "", []
    for m in mots:
        essai = (ligne + " " + m).strip()
        if d.textlength(essai, font=f) > largeur and ligne:
            lignes.append(ligne)
            ligne = m
        else:
            ligne = essai
    lignes.append(ligne)
    return lignes


def principal():
    C.verifier()
    if len(QUESTIONS) != 11:
        raise SystemExit("il y a %d questions, l'image en annonce onze"
                         % len(QUESTIONS))

    out = Image.new("RGB", (L, H), C.FOND)
    d = ImageDraw.Draw(out)

    f_marque = C.police(C.POLICE_G, 22)
    f_titre = C.police(C.POLICE_G, 52)
    f_num = C.police(C.POLICE_G, 25)
    f_q = C.police(C.POLICE_R, 27)

    #  La marque, discrète : l'image à la une n'est pas une affiche.
    d.rectangle([MARGE, MARGE, MARGE + 8, MARGE + 24], fill=C.VIOLET)
    d.text((MARGE + 22, MARGE - 2), "PIXFEED", font=f_marque,
           fill=C.VIOLET_TEXTE)

    y = MARGE + 78
    for i, ligne in enumerate(TITRE):
        d.text((MARGE, y + i * 62), ligne, font=f_titre,
               fill=C.VIOLET_TEXTE if i == 0 else C.ENCRE)
    y += len(TITRE) * 62 + 26
    d.line([MARGE, y, L - MARGE, y], fill=C.TRAIT, width=2)

    #  LES ONZE LIGNES. On mesure d'abord, on dessine ensuite : c'est la seule
    #  façon de savoir si tout tient avant d'avoir produit une image fausse.
    largeur_texte = L - MARGE * 2 - PASTILLE - COLONNE
    plies = [couper(d, q, f_q, largeur_texte) for q in QUESTIONS]
    trop = [q for q, p in zip(QUESTIONS, plies) if len(p) > 2]
    if trop:
        raise SystemExit(
            "ces questions tiennent sur plus de deux lignes, elles seront "
            "illisibles en vignette :\n        - " + "\n        - ".join(trop))

    haut = y + 34
    reste = H - haut - MARGE
    pas = reste / float(len(QUESTIONS))
    if pas < PASTILLE + 12:
        raise SystemExit("il ne reste que %.0f px par question : "
                         "raccourcissez le titre ou agrandissez l'image" % pas)

    for i, (q, lignes) in enumerate(zip(QUESTIONS, plies)):
        cy = haut + pas * i + PASTILLE / 2 + 4
        #  La pastille pleine : à la taille d'une vignette, c'est elle qui
        #  reste lisible et qui fait lire « une liste ».
        d.ellipse([MARGE, cy - PASTILLE / 2, MARGE + PASTILLE,
                   cy + PASTILLE / 2], fill=C.VIOLET)
        n = str(i + 1)
        d.text((MARGE + PASTILLE / 2 - d.textlength(n, font=f_num) / 2,
                cy - 15), n, font=f_num, fill=(255, 255, 255))

        x = MARGE + PASTILLE + COLONNE
        depart = cy - (len(lignes) * 34) / 2 - 2
        for j, ligne in enumerate(lignes):
            d.text((x, depart + j * 34), ligne, font=f_q, fill=C.ENCRE)

    out.save(SORTIE, "WEBP", quality=C.QUALITE, method=6)
    print()
    print("  %d × %d  (%.0f px par question)" % (L, H, pas))
    print("  %s  (%.0f Ko)"
          % (os.path.basename(SORTIE), os.path.getsize(SORTIE) / 1024))


if __name__ == "__main__":
    principal()
