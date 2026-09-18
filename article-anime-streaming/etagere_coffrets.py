"""
Une étagère de coffrets, et ce que le catalogue ne peut pas lui retirer.

    python3 article-anime-streaming/etagere_coffrets.py

Produit `streaming-anime-coffrets-etagere.webp` et son PNG.

----------------------------------------------------------------------------
POURQUOI UN DESSIN, ET PAS UNE PHOTOGRAPHIE NI UNE CAPTURE
----------------------------------------------------------------------------
Le brief laissait le choix entre une étagère de coffrets et la capture d'une
fiche de série retirée d'un catalogue. La capture est impossible ici sans
fabriquer une fausse page de plateforme, c'est-à-dire exactement le genre
d'image qu'on ne fait pas. Reste l'étagère.

Faute d'appareil photo, elle est dessinée. Et puisqu'elle est dessinée, une
règle s'impose : AUCUNE TRANCHE NE PORTE DE TITRE NI DE MARQUE. Poser des
noms de séries réelles sur des coffrets inventés reviendrait à fabriquer des
produits qui n'existent pas, sous des licences qui existent, elles. Les
tranches portent donc des barres, qui ne prétendent rien. La figure le dit en
sous-titre plutôt que de laisser le lecteur le supposer.

----------------------------------------------------------------------------
LE PIED PORTE LA DÉMONSTRATION
----------------------------------------------------------------------------
Une étagère dessinée ne prouve rien toute seule : c'est du décor. Ce qui
donne son sens à la légende, ce sont les trois pertes que l'article
documente déjà — six séries retirées sans annonce, les achats Wakanim perdus
à la fermeture, un film sans aucune offre légale en France. Elles sont en
pied, avec leur source et leur date.

----------------------------------------------------------------------------
LE HASARD EST TIRÉ D'UNE GRAINE FIXE
----------------------------------------------------------------------------
Les largeurs, les hauteurs et les teintes des tranches sont tirées au sort,
sinon la rangée est un peigne. Mais le tirage part d'une graine constante :
deux exécutions donnent la même image, et une retouche du script se compare
à la version précédente au lieu de rebattre les cartes.
"""

import os
import random

import charte as C
import dessin as D

RACINE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(RACINE, "streaming-anime-coffrets-etagere")

L = 1600
MARGE = 56
GRAINE = 7

#  Le meuble.
MONTANT = 18
PLANCHE = 13
RETRAIT = 16

#  Les teintes des tranches. Des neutres et des violets, plus un bleu poussé
#  et un sable : ni rouge ni vert, que la charte réserve à la signalisation.
#  Une couverture de coffret n'annonce rien, elle décore.
TEINTES = (
    (98, 44, 200), (148, 66, 250), (176, 150, 232),
    (40, 42, 52), (92, 98, 112), (150, 152, 158),
    (86, 104, 140), (198, 176, 140), (222, 216, 206),
)

TITRE = "UN COFFRET NE CHANGE PAS D’AVIS"
SOUS = "ce qu’un catalogue peut retirer, et ce qu’il ne peut pas"

PIED = (
    "Illustration, et non une photographie : les tranches ne portent ni "
    "titre ni marque, aucun coffret réel n’est représenté.",
    "Les licences de streaming sont à durée déterminée. Crunchyroll a "
    "retiré six séries en juillet 2026 sans l’annoncer (ComicBook, "
    "22 juillet 2026).",
    "À la fermeture de Wakanim, le 3 novembre 2023, les achats à l’unité "
    "ont été perdus, sans remboursement ni transfert ; seuls les fichiers "
    "déjà téléchargés restaient lisibles",
    "(Journal du Geek, 20 septembre 2023). One Piece 3D: Straw Hat Chase "
    "n’a, lui, aucune offre légale en France (jeuxvideo.com, "
    "26 janvier 2026).",
)


def foncer(t, k):
    return tuple(int(round(v * k)) for v in t)


def eclaircir(t, k):
    return tuple(int(round(v + (255 - v) * k)) for v in t)


def principal():
    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5),
               ("violet", D.VIOLET, 4.5))

    de = random.Random(GRAINE)

    #  Deux rayons, parce qu'un seul ne ressemble pas à une étagère.
    sols = (404, 648)
    hauteur_max = 232
    y_meuble = sols[0] - hauteur_max - 26
    y_bas = sols[1] + PLANCHE + 4

    y_pied = y_bas + 58
    H = y_pied + 18 + len(PIED) * 24 + 40

    t = D.Toile(L, H)
    f_titre = t.police(C.POLICE_G, 17)
    f_sous = t.police(C.POLICE_R, 18)
    f_pied = t.police(C.POLICE_R, 16)

    t.espace((MARGE, 52), TITRE, f_titre, D.ENCRE, 2.2)
    t.texte((MARGE, 78), D.typo(SOUS), f_sous, D.FAIBLE)

    # ------------------------------------------------------------  le meuble
    bois = (206, 198, 184)
    for x in (MARGE, L - MARGE - MONTANT):
        t.rrect([x, y_meuble, x + MONTANT, y_bas], 3, teinte=bois)
        t.rrect([x, y_meuble, x + MONTANT, y_bas], 3,
                contour=foncer(bois, 0.84), epaisseur=1)

    dedans = (MARGE + MONTANT, L - MARGE - MONTANT)
    utile = (dedans[0] + RETRAIT, dedans[1] - RETRAIT)

    def planche(sol):
        t.rrect([dedans[0], sol, dedans[1], sol + PLANCHE], 2, teinte=bois)
        t.rrect([dedans[0], sol + PLANCHE - 4, dedans[1], sol + PLANCHE], 0,
                teinte=foncer(bois, 0.84))

    # -----------------------------------------------------------  une tranche
    def barres(x, haut, w, bas, clair):
        """Les traits qui tiennent lieu de lettrage. Ils ne disent rien."""
        largeur = w * 0.56
        y = haut + (bas - haut) * 0.30
        for i, part in enumerate((1.0, 0.72, 0.86)):
            if y + 5 > bas - 26:
                break
            t.rrect([x + (w - largeur * part) / 2.0, y,
                     x + (w + largeur * part) / 2.0, y + 4], 2, teinte=clair)
            y += 13

    def tranche(x, sol, w, h, teinte):
        haut = sol - h
        clair = eclaircir(teinte, 0.62)
        t.rrect([x, haut, x + w, sol], 2, teinte=teinte)
        #  Deux bandeaux, comme sur une vraie tranche de coffret.
        t.rrect([x, haut, x + w, haut + 11], 2, teinte=foncer(teinte, 0.74))
        t.rrect([x, sol - 17, x + w, sol], 2, teinte=foncer(teinte, 0.84))
        barres(x, haut + 11, w, sol - 17, clair)
        #  Le liseré de lumière sur l'arête gauche.
        t.rrect([x + 2, haut + 13, x + 4, sol - 19], 0,
                teinte=eclaircir(teinte, 0.30))

    def penchee(x, sol, w, h, teinte):
        """Une tranche appuyée sur sa voisine de GAUCHE.

        Penchée vers la droite, elle s'appuyait sur le vide : on avançait
        ensuite de sa largeur plus son dévers, ce qui ouvrait un triangle
        derrière elle et donnait un éclat de verre plutôt qu'un livre.
        Penchée vers la gauche, elle recouvre les tranches déjà posées, ce
        qui est exactement ce que fait un livre qui s'affaisse.
        """
        d = h * 0.09
        haut = sol - h
        t.polygone([(x, sol), (x + w, sol), (x + w - d, haut + 4),
                    (x - d, haut + 4)], teinte)
        t.polygone([(x - d, haut + 4), (x + w - d, haut + 4),
                    (x + w - d + 2, haut + 15), (x - d + 2, haut + 15)],
                   foncer(teinte, 0.74))
        t.rrect([x + w * 0.22, sol - 17, x + w * 0.78, sol], 2,
                teinte=foncer(teinte, 0.84))
        return w

    def couche(x, sol, w, teinte):
        """Un coffret posé à plat sur la pile."""
        t.rrect([x, sol - 20, x + w, sol], 2, teinte=teinte)
        t.rrect([x, sol - 20, x + w, sol - 15], 2, teinte=foncer(teinte, 0.74))
        t.rrect([x + 12, sol - 10, x + w - 12, sol - 6], 2,
                teinte=eclaircir(teinte, 0.62))

    # ----------------------------------------------------------  le garnissage
    total = 0
    for rang, sol in enumerate(sols):
        planche(sol)
        x = utile[0]
        posees = []
        #  On penche une tranche par rangée, jamais la première ni la
        #  dernière : une tranche penchée a besoin d'une voisine pour
        #  s'appuyer.
        place_penchee = 4 if rang == 0 else 6
        i = 0
        while True:
            w = de.randint(23, 42)
            if de.random() < 0.18:
                w = de.randint(58, 92)
            h = de.randint(178, hauteur_max)
            teinte = TEINTES[de.randrange(len(TEINTES))]
            reste = utile[1] - x
            if reste < w + 6:
                break
            #  La dernière tranche s'élargit pour finir contre le montant :
            #  sinon la rangée s'arrête avant le bord et l'étagère a l'air
            #  d'avoir été vidée par la droite.
            if reste - (w + 3) < 46:
                w = reste - 3
            if i == place_penchee:
                x += penchee(x, sol, w, h, teinte) + 3
            else:
                tranche(x, sol, w, h, teinte)
                x += w + 3
            posees.append((x - w - 3, w, h, i == place_penchee))
            i += 1
            total += 1

        #  Les coffrets à plat sont posés EN DERNIER : dessinés au fil de la
        #  rangée, les tranches suivantes, plus hautes, les recouvraient.
        #
        #  Et ils ne se posent que sur un GROUPE DE MÊME HAUTEUR. Posés sur
        #  trois tranches quelconques, ils reposaient sur la plus haute et
        #  flottaient au-dessus des deux autres, parfois au-dessus d'un vide.
        #  Un coffret à plat a besoin d'une assise plane, en dessin comme sur
        #  une vraie étagère.
        pose = 0
        j = 0
        while j < len(posees) - 2 and pose < 2:
            groupe = posees[j:j + 3]
            hauteurs = [g[2] for g in groupe]
            #  Et il faut la place de le poser : sur le rayon du bas, une
            #  pile déjà haute laisserait le coffret traverser la planche
            #  du dessus.
            plat = (max(hauteurs) - min(hauteurs) <= 10
                    and max(hauteurs) <= hauteur_max - 26
                    and not any(g[3] for g in groupe))
            if not plat:
                j += 1
                continue
            gx = groupe[0][0]
            gl = groupe[-1][0] + groupe[-1][1] - gx
            couche(gx, sol - max(hauteurs), gl,
                   TEINTES[de.randrange(len(TEINTES))])
            pose += 1
            j += 5

        #  CONTRÔLE : rien ne doit dépasser du meuble ni flotter au-dessus.
        if x > utile[1] + 6:
            raise SystemExit("la rangée %d déborde du meuble" % (rang + 1))
        if sol - hauteur_max < y_meuble:
            raise SystemExit("une tranche dépasse du montant")

    if total < 40:
        raise SystemExit("seulement %d tranches : l'étagère fait vide"
                         % total)

    # ---------------------------------------------------------------  le pied
    t.ligne([MARGE, y_pied, L - MARGE, y_pied], D.FILET, 2)
    for i, ligne in enumerate(PIED):
        ligne = D.typo(ligne)
        if t.mesure(ligne, f_pied) > L - 2 * MARGE:
            raise SystemExit("la ligne %d du pied déborde" % (i + 1))
        t.texte((MARGE, y_pied + 18 + i * 24), ligne, f_pied, D.FAIBLE)

    D.enregistrer(t.final(L, H), BASE, L, H)
    print("  %d tranches sur deux rayons, graine %d" % (total, GRAINE))


if __name__ == "__main__":
    principal()
