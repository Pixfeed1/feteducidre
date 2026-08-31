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
PAYSAGE, PARCE QU'UNE IMAGE À LA UNE EST RECADRÉE
----------------------------------------------------------------------------
La première version suivait le brief à la lettre : 1080 × 1620, vertical. Elle
était juste sur le papier et inutilisable en pratique.

WordPress ne montre presque jamais une image à la une telle quelle. Les
vignettes de cartes et de pages d'archives sont en PAYSAGE, et le partage sur
les réseaux passe par la balise Open Graph, dont le format de référence est
1200 × 630. Sur une image verticale, ces recadrages prennent une bande
centrale : sur onze questions, il en resterait trois ou quatre.

D'où 1600 × 900. Ce format se recadre en 1200 × 630 en ne perdant que trente
pixels en haut et en bas — rien qui porte du sens ici — et remplit les
vignettes de thème sans bande vide.

----------------------------------------------------------------------------
DEUX COLONNES, ET LE REFUS DE DÉBORDER
----------------------------------------------------------------------------
Onze lignes ne tiennent pas en pleine largeur sur 900 px de haut sans devenir
minuscules. Elles sont donc réparties en deux colonnes, six et cinq.

Le texte est replié à la largeur de sa colonne, et le script REFUSE de
produire l'image si une question déborde sur trois lignes ou si la place par
ligne descend sous le diamètre d'une pastille. Mieux vaut un script qui
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

L, H = 1600, 900                # 16/9 : se recadre proprement en 1200 × 630
MARGE = 56
GOUTTIERE = 48
GAUCHE = 6                      # questions dans la colonne de gauche

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

PASTILLE = 46                    # diamètre de la pastille du numéro
COLONNE = 24                     # espace entre la pastille et le texte


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

    f_marque = C.police(C.POLICE_G, 21)
    f_titre = C.police(C.POLICE_G, 44)
    f_num = C.police(C.POLICE_G, 22)
    f_q = C.police(C.POLICE_R, 23)

    #  La marque, discrète : une image à la une n'est pas une affiche.
    d.rectangle([MARGE, MARGE, MARGE + 8, MARGE + 22], fill=C.VIOLET)
    d.text((MARGE + 22, MARGE - 3), "PIXFEED", font=f_marque,
           fill=C.VIOLET_TEXTE)

    #  Le titre tient sur deux lignes en paysage, contre trois en vertical.
    y = MARGE + 62
    d.text((MARGE, y), TITRE[0], font=f_titre, fill=C.VIOLET_TEXTE)
    d.text((MARGE + d.textlength(TITRE[0] + " ", font=f_titre), y),
           TITRE[1], font=f_titre, fill=C.ENCRE)
    d.text((MARGE, y + 54), TITRE[2], font=f_titre, fill=C.ENCRE)
    y += 54 + 60
    d.line([MARGE, y, L - MARGE, y], fill=C.TRAIT, width=2)

    #  DEUX COLONNES. On mesure d'abord, on dessine ensuite : c'est la seule
    #  façon de savoir si tout tient avant d'avoir produit une image fausse.
    col_l = (L - MARGE * 2 - GOUTTIERE) // 2
    largeur_texte = col_l - PASTILLE - COLONNE
    plies = [couper(d, q, f_q, largeur_texte) for q in QUESTIONS]
    trop = [q for q, p in zip(QUESTIONS, plies) if len(p) > 2]
    if trop:
        raise SystemExit(
            "ces questions tiennent sur plus de deux lignes, elles seront "
            "illisibles en vignette :\n        - " + "\n        - ".join(trop))

    haut = y + 32
    par_col = max(GAUCHE, len(QUESTIONS) - GAUCHE)
    pas = (H - haut - MARGE) / float(par_col)
    if pas < PASTILLE + 10:
        raise SystemExit("il ne reste que %.0f px par question : "
                         "raccourcissez le titre ou agrandissez l'image" % pas)

    for i, (q, lignes) in enumerate(zip(QUESTIONS, plies)):
        colonne = 0 if i < GAUCHE else 1
        rang = i if colonne == 0 else i - GAUCHE
        x0 = MARGE + colonne * (col_l + GOUTTIERE)
        cy = haut + pas * rang + PASTILLE / 2 + 2

        d.ellipse([x0, cy - PASTILLE / 2, x0 + PASTILLE, cy + PASTILLE / 2],
                  fill=C.VIOLET)
        n = str(i + 1)
        d.text((x0 + PASTILLE / 2 - d.textlength(n, font=f_num) / 2, cy - 13),
               n, font=f_num, fill=(255, 255, 255))

        x = x0 + PASTILLE + COLONNE
        depart = cy - (len(lignes) * 30) / 2 - 1
        for j, ligne in enumerate(lignes):
            d.text((x, depart + j * 30), ligne, font=f_q, fill=C.ENCRE)

    out.save(SORTIE, "WEBP", quality=C.QUALITE, method=6)
    print()
    print("  %d × %d  (%.0f px par question, %d + %d)"
          % (L, H, pas, GAUCHE, len(QUESTIONS) - GAUCHE))
    print("  %s  (%.0f Ko)"
          % (os.path.basename(SORTIE), os.path.getsize(SORTIE) / 1024))


if __name__ == "__main__":
    principal()
