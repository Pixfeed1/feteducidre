# -*- coding: utf-8 -*-
u"""
Un enfant assis dans le sable.

CE QUI N'ALLAIT PAS DANS MA PREMIERE VERSION
  1. DES TUYAUX. Tous les membres etaient des traits d'epaisseur constante.
     Dans la reference ils sont FUSELES - epais a l'attache, fins a
     l'extremite - et ils se courbent. Cette variation est ce qui fait la
     souplesse ; sans elle on dessine un bonhomme en tubes. Corrige par
     trace.fusele(), qui calcule le contour d'une courbe a largeur variable.
  2. AUCUN GRAIN SUR LE VETEMENT. Dans la reference le maillot et la
     serviette sont graines comme le reste. Le short etait un aplat nu, et un
     aplat nu au milieu d'une image entierement grainee se voit.
  3. DES JOUETS GROSSIERS. Le seau etait un trapeze, la pelle deux
     rectangles. Un seau a un profil GALBE et un fond arrondi ; une pelle a
     un manche, une poignee et une lame en cuillere.

CE QUE JE GARDE DE LA REFERENCE
  Aucun visage - les personnages y sont lisibles par leur seule posture.
  Deux tons de peau, jamais de degrade. Un seul accent sature : le short.
  Un accessoire qui raconte le geste.

LA CONSTRUCTION
  Tout est decrit dans un repere local - origine au point ou l'enfant touche
  le sable, y negatif vers le haut - puis les coordonnees sont CALCULEES a
  leur place finale. Pas de transform : un groupe transforme fait calculer le
  grain dans l'espace transforme, et Inkscape le rend alors par bandes.
"""

import booleen as B
import trace as T

PEAU = "#F2A07B"
PEAU_OMBRE = "#DB8760"
CHEVEUX = "#5A3A28"
CHEVEUX_CLAIR = "#7A5238"
SHORT = "#E8433F"
SHORT_OMBRE = "#C7332F"
SEAU = "#2E6FE0"
SEAU_OMBRE = "#2455B0"
PELLE = "#F5C542"
PELLE_OMBRE = "#D9A82E"
OMBRE_SOL = "#EDEBE0"


def dessiner(ox, oy, k=1.0, indent=4, filtre_tissu="grainTissu"):
    """ox, oy : le point ou l'enfant touche le sable. k : l'echelle."""
    e = " " * indent

    def P(x, y):
        return (ox + x * k, oy + y * k)

    def pose(d, couleur):
        """Un chemin decrit en local, amene a sa place, sans transform."""
        return u'<path d="%s" fill="%s"/>' % (B.placer(d, ox, oy, k), couleur)

    def membre(controle, profil, couleur, avec=None):
        """
        Un membre fusele, LISSE.

        trace.fusele() echantillonne la courbe et relie les points par des
        segments : le contour sortait en polygone a 52 cotes. On le fait donc
        passer par Simplifier avant de le poser - Inkscape y rajuste des
        cubiques, et le contour redevient continu en courbure.

        avec : une forme a REUNIR avant de lisser (un pied, une main). La
        reunion d'abord, le lissage ensuite : ainsi le raccord lui-meme est
        lisse, au lieu de rester un angle entre deux pieces jointes.
        """
        d = T.fusele(controle, profil)
        if avec:
            d = B.union(d, avec)
        return pose(B.lisser(d), couleur)

    def rond(c, r, couleur):
        p = P(*c)
        return (u'<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>'
                % (p[0], p[1], r * k, couleur))

    def chemin(d, couleur, extra=""):
        return u'<path d="%s" fill="%s"%s/>' % (d, couleur, extra)

    def C(*pts):
        """Une suite de points locaux -> une commande de chemin absolue."""
        out = "M%.1f %.1f" % P(*pts[0])
        for q in pts[1:]:
            out += " L%.1f %.1f" % P(*q)
        return out + " Z"

    peau, tissu, objets = [], [], []

    # ---- l'ombre au sol -------------------------------------------------
    p = P(26, 8)
    fond = [u'<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" '
            u'opacity="0.6"/>' % (p[0], p[1], 116 * k, 16 * k, OMBRE_SOL)]

    # ---- la jambe ARRIERE, ton sombre -----------------------------------
    # Elle part de la hanche, passe le genou, s'affine jusqu'a la cheville.
    peau.append(membre([(-8, -44), (36, -50), (86, -34), (124, -26)],
                       [(0.0, 46), (0.55, 38), (1.0, 25)], PEAU_OMBRE))
    # LE PIED. Les deux jambes se terminaient en pointe, comme des nouilles :
    # une jambe sans pied ne se lit pas comme une jambe. Le pied est une forme
    # a part, REUNIE au mollet - donc aucune jointure a rater.
    peau.append(membre([(124, -26), (140, -24), (152, -20), (160, -14)],
                       [(0.0, 25), (1.0, 20)], PEAU_OMBRE,
                       avec="M150 -26 C172 -30 192 -23 193 -14 "
                            "C194 -6 182 -2 167 -3 C156 -4 148 -13 150 -26 Z"))

    # ---- le torse -------------------------------------------------------
    # Lui aussi fusele : large aux hanches, plus etroit aux epaules, et
    # legerement penche en avant. Un tronc vertical donne un garde-a-vous.
    peau.append(membre([(-6, -58), (2, -100), (10, -132), (20, -156)],
                       [(0.0, 76), (0.5, 70), (1.0, 60)], PEAU))

    # ---- la jambe AVANT, ton clair --------------------------------------
    peau.append(membre([(-10, -36), (34, -42), (88, -26), (132, -18)],
                       [(0.0, 48), (0.55, 40), (1.0, 27)], PEAU))
    peau.append(membre([(132, -18), (148, -16), (162, -12), (172, -4)],
                       [(0.0, 27), (1.0, 21)], PEAU,
                       avec="M162 -18 C186 -22 208 -14 209 -4 "
                            "C210 5 197 8 181 7 C169 6 160 -4 162 -18 Z"))

    # ---- le bras, tendu vers le sable -----------------------------------
    # Il sort NETTEMENT de la silhouette du torse : dessine dans l'axe du
    # corps il s'y noyait, et le geste ne se lisait plus.
    peau.append(membre([(26, -142), (62, -124), (86, -96), (104, -60)],
                       [(0.0, 30), (0.6, 24), (1.0, 18)], PEAU,
                       avec=B.ellipse(106, -54, 12, 11)))

    # ---- le short, avec son grain ---------------------------------------
    # Une forme galbee, pas un rectangle : la ceinture est plus etroite que
    # le bas, et l'ourlet suit la cuisse.
    #
    # L'OURLET EST UNE INTERSECTION, plus un second chemin redessine. Avant,
    # j'approchais a la main la courbe du bas du short avec une deuxieme
    # courbe : elle ne tombait jamais exactement dessus. Ici on croise le
    # short avec une simple bande horizontale - le bord de l'ourlet suit donc
    # le bord du short au point pres, par construction.
    SHORT_D = ("M-40 -78 C-16 -86 12 -84 30 -76 L38 -22 "
               "C6 -14 -28 -16 -42 -30 Z")
    tissu.append(pose(SHORT_D, SHORT))
    tissu.append(pose(B.intersection(
        SHORT_D, "M-60 -42 C-20 -30 20 -28 60 -40 L60 24 L-60 24 Z"),
        SHORT_OMBRE))

    # ---- la tete --------------------------------------------------------
    peau.append(rond((16, -196), 45, PEAU))
    # LA COIFFURE. Elle etait symetrique et barrait le front d'un trait
    # horizontal - une casquette, pas des cheveux. Elle est maintenant
    # ASYMETRIQUE : basse sur la nuque, a gauche, et remontee sur le front,
    # a droite, du cote ou l'enfant regarde. C'est cette dissymetrie qui
    # donne un sens a la tete.
    CHEVEUX_D = ("M-28 -176 C-46 -232 2 -260 40 -251 "
                 "C61 -246 67 -224 58 -206 "
                 "C50 -228 8 -234 -8 -206 "
                 "C-14 -194 -20 -184 -28 -176 Z")
    objets.append(pose(CHEVEUX_D, CHEVEUX))
    # UNE MECHE CLAIRE sur le dessus : sans elle la chevelure est une masse.
    # Elle aussi est une intersection - la chevelure croisee avec une simple
    # ellipse posee au-dessus. Son bord exterieur est donc exactement celui
    # des cheveux, et son bord interieur une courbe franche. Dessinee a la
    # main, elle debordait ou rentrait d'un ou deux pixels selon l'endroit,
    # ce qui se lit tout de suite comme une bavure.
    objets.append(pose(B.intersection(CHEVEUX_D, B.ellipse(14, -286, 64, 48)),
                       CHEVEUX_CLAIR))

    # ================= LE SEAU, construit et non approche =================
    # LE PRINCIPE, et c'est lui qui change tout : le seau n'est dessine QU'UNE
    # FOIS. Sa panse, sa levre et son anse sont ensuite obtenues par des
    # operations sur cette forme unique, calculees par Inkscape (voir
    # booleen.py). Aucune courbe n'est redessinee pour en longer une autre :
    # une ombre qui doit epouser un bord ne peut pas etre approchee, elle doit
    # en DESCENDRE.

    # La panse : evasee vers le haut, ventrue au tiers, resserree au fond.
    PANSE = ("M192 -104 C194 -66 200 -30 208 -12 "
             "C213 -2 257 -2 262 -12 "
             "C270 -30 276 -66 278 -104 Z")
    # La levre, vue de trois quarts : une ellipse. Reunie a la panse, elle
    # donne au seau un bord superieur COURBE - et le raccord est exact, alors
    # qu'un bord droit surmonte d'une ellipse laissait deux petites cornes
    # aux angles.
    LEVRE = B.ellipse(235, -104, 43, 11)
    CORPS = B.union(PANSE, LEVRE)

    objets.append(pose(CORPS, SEAU))
    # LE COTE A L'OMBRE. Un masque grossier - une bande verticale un peu
    # cintree - croise avec le corps. Le bord droit de l'ombre est donc le
    # bord droit du seau, exactement, sur toute sa hauteur.
    objets.append(pose(
        B.intersection(CORPS,
                       "M252 -126 C240 -84 236 -40 244 16 L330 16 L330 -126 Z"),
        SEAU_OMBRE))
    # L'interieur, vu par la levre.
    objets.append(pose(LEVRE, SEAU_OMBRE))

    # L'ANSE : un vrai anneau, pas un trait. On prend deux ellipses
    # concentriques, on retire la petite de la grande - il reste un anneau -
    # puis on coupe tout ce qui passe sous la levre. Restent deux pieds qui
    # tombent PILE sur les bords du seau, parce qu'ils ont le meme rayon.
    ANNEAU = B.difference(B.ellipse(235, -104, 44, 44),
                          B.ellipse(235, -104, 36, 36))
    objets.append(pose(B.difference(ANNEAU, B.boite(180, -104, 292, 40)),
                       SEAU_OMBRE))

    # ================= LA PELLE, en une seule piece ========================
    # Manche, poignee et lame etaient trois objets poses cote a cote, et les
    # raccords se voyaient. Ils sont maintenant REUNIS en une seule forme :
    # plus de jointure, donc plus de raccord a rater.
    MANCHE = T.fusele([(316, -14), (322, -50), (328, -84), (334, -114)],
                      [(0.0, 14), (1.0, 11)])
    POIGNEE = T.fusele([(316, -116), (326, -126), (344, -126), (354, -116)],
                       [(0.0, 13), (1.0, 13)])
    # Une lame de pelle, pas une pomme : large a l'attache, elle se retrecit
    # jusqu'a une pointe arrondie. C'est le RETRECISSEMENT qui la designe.
    LAME = ("M293 -40 C287 -14 295 8 311 24 "
            "C327 8 335 -14 329 -40 Z")
    PELLE_D = B.lisser(B.union(LAME, MANCHE, POIGNEE))

    objets.append(pose(PELLE_D, PELLE))
    # Meme lumiere que sur le seau - elle vient de la gauche - donc meme
    # masque, sur la droite. C'est cette CONSTANCE qui fait qu'un ensemble
    # d'objets appartient a la meme image.
    objets.append(pose(
        B.intersection(PELLE_D,
                       "M318 -150 C312 -80 310 -30 316 40 L400 40 L400 -150 Z"),
        PELLE_OMBRE))

    lignes = [u'%s<g inkscape:label="Enfant">' % e]
    lignes += [u'%s  %s' % (e, x) for x in fond]
    lignes += [u'%s  %s' % (e, x) for x in peau]
    # LE VETEMENT PORTE SON PROPRE GRAIN : dans la reference le maillot est
    # graine comme le decor. Un aplat nu au milieu d'une image entierement
    # grainee se remarque immediatement.
    lignes.append(u'%s  <g filter="url(#%s)">' % (e, filtre_tissu))
    lignes += [u'%s    %s' % (e, x) for x in tissu]
    lignes.append(u'%s  </g>' % e)
    lignes += [u'%s  %s' % (e, x) for x in objets]
    lignes.append(u'%s</g>' % e)
    return "\n".join(lignes)


if __name__ == "__main__":
    s = dessiner(900, 1180, 1.0)
    print(u"%d elements, %d caracteres" % (s.count("<path") + s.count("<circle")
                                           + s.count("<ellipse"), len(s)))
