"""
Une saison, plusieurs abonnements, et une répartition qui bouge.

    python3 article-anime-streaming/repartition_saison.py

Produit `streaming-anime-repartition-saison.webp` et son PNG.

----------------------------------------------------------------------------
CE QUE LE BRIEF DEMANDAIT, ET POURQUOI CE N'EST PAS CE QUI EST DESSINÉ
----------------------------------------------------------------------------
Le brief demandait une grille de sortie de saison, titre par titre, avec les
logos des plateformes posés dessus. Deux choses l'interdisent.

La liste des quelque cent titres de l'été 2026 et le service qui porte
chacun d'eux n'existent nulle part dans les sources de l'article : elles
donnent des COMPTES, pas une grille. Dessiner cette grille reviendrait à
inventer des titres et à leur attribuer des plateformes au jugé, c'est-à-dire
à fabriquer la donnée que la figure prétendrait montrer.

Les logos, eux, sont des marques déposées, et je n'en ai pas les fichiers :
les redessiner de mémoire donnerait cinq approximations qui ressemblent à des
logos sans en être. Les services sont donc nommés en toutes lettres.

Reste le propos de la légende — « une saison, plusieurs abonnements, la
répartition change à chaque trimestre » —, et celui-là est mesurable avec les
chiffres que l'article source déjà. C'est lui qui est dessiné.

----------------------------------------------------------------------------
LES TOTAUX DÉPASSENT LA SAISON, ET IL FAUT LE DIRE
----------------------------------------------------------------------------
85 + 15 + 8 + 5 + 1 font 114 pour « quelque 100 titres ». Ce n'est pas une
erreur de l'article : une même série peut être portée par plusieurs services
— l'arc Elbaph de One Piece est chez Crunchyroll, chez ADN et chez Netflix,
et l'article le montre lui-même deux sections plus loin.

Mais un lecteur qui additionne tombe sur 114 pour 100 et en conclut que les
chiffres sont faux. La figure écrit donc le chevauchement en pied — et c'est
aussi pourquoi elle ne peut pas être un camembert : des parts qui se
recouvrent ne se découpent pas en quartiers.

----------------------------------------------------------------------------
DEUX PANNEAUX, DEUX DÉNOMINATEURS, DEUX FOIS DITS
----------------------------------------------------------------------------
À gauche, le simulcast d'une saison : la domination de Crunchyroll, qui est
le fait central. À droite, le doublage français d'un trimestre à l'autre :
le mouvement, qui est le propos de la légende. Les deux panneaux n'ont pas la
même échelle parce qu'ils ne comptent pas la même chose, et chacun porte son
dénominateur sous son titre.
"""

import os

import charte as C
import dessin as D

RACINE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(RACINE, "streaming-anime-repartition-saison")

L = 1600
MARGE = 56
GOUTTIERE = 40

#  Les deux violets sont un dégradé d'une seule teinte, et non deux couleurs
#  d'identité : printemps et automne sont ORDONNÉS, et une paire clair/foncé
#  dit cet ordre là où deux teintes le cacheraient.
#  Validés : séparation 16,9 en vision protanope, 20,5 en tritanope, et tous
#  deux au-dessus de 3:1 sur le fond.
VIOLET = (98, 44, 200)
VIOLET_DOUX = (162, 120, 228)

#  Simulcast de l'été 2026. Source : Dexerto, 10 juin 2026.
SAISON = 100
SIMULCAST = (("Crunchyroll", 85), ("ADN", 15), ("Netflix", 8),
             ("Prime Video", 5), ("Disney+", 1))

#  Séries doublées en VF. Source : AnimOtaku, 11 avril et 17 septembre 2026.
#  Le même ordre de plateformes qu'à gauche, pour que l'oeil les retrouve.
VF_SAISON = 20
VF = (("Crunchyroll", 15, 10), ("ADN", 1, 2), ("Netflix", 3, 5),
      ("Prime Video", 2, 1))

TITRE = "UNE SAISON, PLUSIEURS ABONNEMENTS"
SOUS = ("nombre de séries portées par chaque service, France, 2026 ; "
        "les services sont nommés, sans logo")

PIED = (
    "Simulcast : Dexerto, 10 juin 2026. Doublages : AnimOtaku, 11 avril et "
    "17 septembre 2026. Disney+ n’apparaît pas à droite : la source qui "
    "compte les VF ne le relève pas.",
    "Les barres de gauche totalisent 114 pour une saison d’environ "
    "100 titres, et ce n’est pas une erreur : une série peut être portée par "
    "plusieurs services à la fois.",
    "L’arc Elbaph de One Piece est ainsi chez Crunchyroll, chez ADN et chez "
    "Netflix. Des parts qui se recouvrent ne se découpent pas en quartiers, "
    "d’où des barres et non un camembert.",
)


def principal():
    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5),
               ("violet", VIOLET, 4.5))
    #  Les deux aplats doivent se détacher du papier, sinon une barre pâle
    #  disparaît chez qui imprime la page.
    for nom, teinte in (("violet", VIOLET), ("violet doux", VIOLET_DOUX)):
        if C.contraste(teinte, C.FOND) < 3.0:
            raise SystemExit("l'aplat %s ne se détache pas du fond (%.2f:1)"
                             % (nom, C.contraste(teinte, C.FOND)))

    if sum(n for _, n in SIMULCAST) <= SAISON:
        raise SystemExit("le pied annonce un chevauchement que les chiffres "
                         "ne montrent pas")
    #  L'ordre des plateformes doit être le même à gauche et à droite.
    gauche = [n for n, _ in SIMULCAST if n != "Disney+"]
    if gauche != [n for n, _, _ in VF]:
        raise SystemExit("les deux panneaux ne rangent pas les plateformes "
                         "dans le même ordre : %s contre %s"
                         % (gauche, [n for n, _, _ in VF]))

    large = (L - 2 * MARGE - GOUTTIERE) // 2
    colonne = 128
    piste = large - colonne - 56

    lignes = 46
    ecart = 16
    haut_a = len(SIMULCAST) * lignes + (len(SIMULCAST) - 1) * ecart
    barre = 21
    groupe = 2 * barre + 2
    haut_b = len(VF) * groupe + (len(VF) - 1) * 28
    #  Le panneau de droite descend d'un cran pour loger sa légende, qui
    #  n'appartient qu'à lui : collée sous le titre, elle passait par-dessus
    #  la ligne du dénominateur.
    decale = 34
    haut = max(haut_a, haut_b + decale)

    y_panneau = 148
    y_barres = y_panneau + 66
    y_fait = y_barres + haut + 46
    y_pied = y_fait + 70
    H = y_pied + 18 + len(PIED) * 24 + 40

    t = D.Toile(L, H)
    f_titre = t.police(C.POLICE_G, 17)
    f_sous = t.police(C.POLICE_R, 18)
    f_pan = t.police(C.POLICE_G, 16)
    f_den = t.police(C.POLICE_R, 15)
    f_nom = t.police(C.POLICE_R, 17)
    f_val = t.police(C.POLICE_G, 17)
    f_note = t.police(C.POLICE_R, 15)
    f_fait = t.police(C.POLICE_G, 21)
    f_pied = t.police(C.POLICE_R, 16)

    t.espace((MARGE, 52), TITRE, f_titre, D.ENCRE, 2.2)
    t.texte((MARGE, 78), D.typo(SOUS), f_sous, D.FAIBLE)

    def entete(x, titre, denominateur):
        t.espace((x, y_panneau), titre, f_pan, D.ENCRE, 1.6)
        t.texte((x, y_panneau + 26), D.typo(denominateur), f_den, D.GRIS)

    def trace(x, y, valeur, total, teinte):
        """Une barre, et sa valeur écrite à côté plutôt que dedans."""
        w = piste * valeur / float(total)
        #  Une barre de 1 sur 100 fait cinq pixels : on lui laisse de quoi
        #  exister, sinon Disney+ disparaît et la figure ment par omission.
        t.rrect([x, y, x + max(w, 4.0), y + barre], 4, teinte=teinte)
        return x + max(w, 4.0)

    # ------------------------------------------  à gauche, le simulcast
    x = MARGE
    entete(x, "EN SIMULCAST, ÉTÉ 2026",
           "sur environ %d titres dans la saison" % SAISON)
    for i, (nom, valeur) in enumerate(SIMULCAST):
        y = y_barres + i * (lignes + ecart)
        t.texte((x, y + 1), D.typo(nom), f_nom, D.ENCRE)
        bout = trace(x + colonne, y, valeur, SAISON, VIOLET)
        t.texte((bout + 12, y), str(valeur), f_val, D.ENCRE)

    # ------------------------------------------  à droite, les doublages
    x = MARGE + large + GOUTTIERE
    entete(x, "DOUBLÉS EN VF, D’UN TRIMESTRE À L’AUTRE",
           "sur environ %d titres doublés par saison" % VF_SAISON)

    #  La légende : deux aplats et deux mots, parce que la couleur seule ne
    #  doit jamais porter l'information.
    xl = x
    for teinte, mot in ((VIOLET_DOUX, "printemps 2026"),
                        (VIOLET, "automne 2026")):
        t.rrect([xl, y_barres + 4, xl + 22, y_barres + 16], 4, teinte=teinte)
        t.texte((xl + 30, y_barres), D.typo(mot), f_note, D.GRIS)
        xl += 30 + t.mesure(D.typo(mot), f_note) + 30
    if xl > MARGE + 2 * large + GOUTTIERE:
        raise SystemExit("la légende déborde de son panneau")

    for i, (nom, avant, apres) in enumerate(VF):
        y = y_barres + decale + i * (groupe + 28)
        t.texte((x, y + 10), D.typo(nom), f_nom, D.ENCRE)
        for j, (valeur, teinte) in enumerate(((avant, VIOLET_DOUX),
                                              (apres, VIOLET))):
            yb = y + j * (barre + 2)
            bout = trace(x + colonne, yb, valeur, VF_SAISON, teinte)
            t.texte((bout + 12, yb - 1), str(valeur), f_val, D.ENCRE)

    # ------------------------------------------------  le fait à retenir
    part_avant = 100.0 * VF[0][1] / 19.0
    part_apres = 100.0 * VF[0][2] / VF_SAISON
    fait = ("Crunchyroll portait %d %% des séries doublées au printemps, "
            "%d %% à l’automne." % (round(part_avant), round(part_apres)))
    t.ligne([MARGE, y_fait - 22, L - MARGE, y_fait - 22], D.FILET, 2)
    if t.mesure(D.typo(fait), f_fait) > L - 2 * MARGE:
        raise SystemExit("le fait à retenir déborde")
    t.texte((MARGE, y_fait), D.typo(fait), f_fait, D.VIOLET)

    # ---------------------------------------------------------  le pied
    t.ligne([MARGE, y_pied, L - MARGE, y_pied], D.FILET, 2)
    for i, ligne in enumerate(PIED):
        ligne = D.typo(ligne)
        if t.mesure(ligne, f_pied) > L - 2 * MARGE:
            raise SystemExit("la ligne %d du pied déborde" % (i + 1))
        t.texte((MARGE, y_pied + 18 + i * 24), ligne, f_pied, D.FAIBLE)

    D.enregistrer(t.final(L, H), BASE, L, H)
    print("  simulcast : %d titres comptés pour une saison de %d"
          % (sum(n for _, n in SIMULCAST), SAISON))
    print("  VF : printemps %d, automne %d"
          % (sum(a for _, a, _ in VF), sum(b for _, _, b in VF)))
    print("  Crunchyroll : %d %% au printemps, %d %% à l’automne"
          % (round(part_avant), round(part_apres)))


if __name__ == "__main__":
    principal()
