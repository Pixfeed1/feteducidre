# -*- coding: utf-8 -*-
u"""
LES OPERATIONS BOOLEENNES, calculees par Inkscape lui-meme.

LE PROBLEME QU'ELLES RESOLVENT
  Jusqu'ici, chaque ombre etait un SECOND CHEMIN que j'essayais de faire
  coincider a la main avec le galbe du premier. Le seau en est l'exemple : son
  cote sombre etait une courbe redessinee point par point, censee epouser le
  bord du seau. Elle ne l'epousait pas - a un pixel pres, jamais au meme
  endroit, et c'est exactement ce que tu voyais quand tu disais "trop
  d'approximation".

  Une ombre ne doit pas RESSEMBLER a la forme qu'elle habille : elle doit en
  DESCENDRE. On dessine donc la forme une seule fois, on la croise avec un
  masque grossier, et l'intersection tombe forcement sur le bord exact. Ce
  n'est plus une ressemblance, c'est une consequence.

POURQUOI PASSER PAR INKSCAPE ET NON PAR UNE BIBLIOTHEQUE
  Shapely sait faire des booleens, mais sur des POLYGONES : il faut aplatir
  les courbes en segments, et on recupere des milliers de petits traits au
  lieu de quelques Beziers. Ici la forme reste courbe d'un bout a l'autre.

  Inkscape, lui, opere sur les Beziers eux-memes, et il le fait en ligne de
  commande. Verifie sur la version installee (1.2.2) :

      path-union          OK
      path-difference     OK
      path-intersection   OK
      path-cut            OK        path-division     OK
      path-exclusion      OK        path-simplify     OK

      outset, offset, stroke-to-path    N'EXISTENT PAS sous ce nom.
      Les decalages de contour restent donc a notre charge - c'est ce que
      fait trace.fusele().

LE COUT, ET LE CACHE
  Chaque appel lance Inkscape : environ une seconde. C'est negligeable pour
  une dizaine d'operations, mais on reconstruit l'image des dizaines de fois.
  Les resultats sont donc gardes dans booleens.json, indexes par le contenu
  des formes : tant que le dessin ne bouge pas, Inkscape n'est plus appele du
  tout. Efface le fichier pour tout recalculer.
"""

import hashlib
import json
import os
import re
import subprocess
import tempfile

CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "booleens.json")
_memoire = None
_appels = [0]


def _charger():
    global _memoire
    if _memoire is None:
        try:
            _memoire = json.load(open(CACHE))
        except Exception:
            _memoire = {}
    return _memoire


def _ecrire():
    if _memoire is not None:
        json.dump(_memoire, open(CACHE, "w"), indent=0, sort_keys=True)


def operer(operation, formes, _brut=False):
    u"""
    Applique une operation booleenne a une suite de chemins.

    operation : "union", "difference", "intersection", "exclusion"
    formes    : les attributs d= , du DESSOUS vers le DESSUS.

                L'ordre compte pour la difference : Inkscape retire le dessus
                du dessous. difference([socle, outil]) enleve l'outil.

    Retourne le d= resultant. Les coordonnees sont celles qu'on lui a donnees
    - on travaille donc dans le repere local du personnage, avant mise a
    l'echelle, et le cache reste valable ou qu'on le pose ensuite.
    """
    formes = [f for f in formes if f and f.strip()]
    if not formes:
        return ""
    if len(formes) == 1 and not _brut:
        return formes[0]

    memoire = _charger()
    cle = hashlib.sha1(
        ("%s|%s" % (operation, "|".join(formes))).encode("utf-8")).hexdigest()
    if cle in memoire:
        return memoire[cle]

    corps = "\n".join('<path d="%s" fill="#000000"/>' % f for f in formes)
    # Une toile large et decalee : nos coordonnees locales sont negatives vers
    # le haut, et rien ne doit sortir du document - Inkscape ne rogne pas,
    # mais autant garder le fichier lisible si on veut l'ouvrir pour voir.
    doc = ('<svg xmlns="http://www.w3.org/2000/svg" width="2000" '
           'height="2000" viewBox="-800 -1200 2000 2000">\n%s\n</svg>' % corps)

    dossier = tempfile.mkdtemp(prefix="booleen_")
    entree = os.path.join(dossier, "e.svg")
    sortie = os.path.join(dossier, "s.svg")
    open(entree, "w").write(doc)

    _appels[0] += 1
    subprocess.run(
        ["inkscape",
         "--actions=select-all;object-to-path;%s;"
         "export-filename:%s;export-plain-svg;export-do"
         % (operation if _brut else "path-" + operation, sortie),
         entree],
        capture_output=True)

    if not os.path.exists(sortie):
        raise RuntimeError(
            u"Inkscape n'a pas ecrit de fichier pour %s. Est-il dans le PATH ?"
            % operation)
    chemins = re.findall(r'\sd="([^"]+)"', open(sortie).read())
    if not chemins:
        # Distinction importante : Inkscape a bien tourne, mais le resultat
        # est VIDE. Deux formes qui ne se touchent pas, une intersection sans
        # recouvrement. Ce n'est pas une panne, c'est un dessin a corriger -
        # et le dire ainsi evite de partir chercher un probleme d'installation.
        raise ValueError(
            u"%s : resultat vide, les formes ne se recouvrent pas." % operation)
    # Une operation peut laisser plusieurs chemins (une difference qui coupe
    # en deux, par exemple) : on les concatene, un chemin SVG accepte
    # plusieurs sous-chemins.
    # Ramene en absolu tout de suite : voir absolu().
    resultat = " ".join(absolu(c) for c in chemins)

    memoire[cle] = resultat
    _ecrire()
    return resultat


# Combien de nombres attend chaque commande, et lesquels sont des abscisses.
_SIGNATURE = {
    "M": 2, "L": 2, "T": 2, "H": 1, "V": 1,
    "C": 6, "S": 4, "Q": 4, "A": 7, "Z": 0,
}


def absolu(d):
    u"""
    Reecrit un chemin entierement en coordonnees ABSOLUES.

    POURQUOI C'EST INDISPENSABLE ICI
      Inkscape rend ses chemins en relatif : "m 31.3,-50.9 c 2.7,-19.5 ...".
      Et la grammaire SVG a une regle particuliere - un "m" MINUSCULE en tete
      de chemin est malgre tout absolu, puisqu'il n'y a pas encore de point
      courant. J'avais traite ses deux nombres comme du relatif : le membre
      partait alors de (x.k, y.k) au lieu de (ox + x.k, oy + y.k), c'est-a-dire
      a l'autre bout de l'image. C'est exactement ce qu'on a vu.

      Plutot que d'ajouter ce cas particulier a placer(), on supprime le
      probleme : tout est ramene en absolu des la sortie d'Inkscape, et le
      reste du code n'a plus qu'une seule forme a connaitre.

    Les lettres sont conservees (S et T gardent leur sens : elles se refletent
    sur le point de controle precedent, que la conversion ne change pas).
    """
    sortie = []
    cx = cy = 0.0          # le point courant
    sx = sy = 0.0          # le debut du sous-chemin, ou ramene Z
    premier = True

    for cmd, nombres in _decouper(d):
        haut = cmd.upper()
        rel = cmd.islower()
        n = _SIGNATURE.get(haut, 0)

        if haut == "Z":
            sortie.append("Z")
            cx, cy = sx, sy
            continue
        if n == 0 or not nombres:
            continue

        for i in range(0, len(nombres), n):
            bloc = list(nombres[i:i + n])
            if len(bloc) < n:
                break
            # Un "m" en tete de chemin est absolu ; ensuite seulement il
            # devient relatif comme les autres.
            local = rel and not (haut == "M" and premier and i == 0)

            if haut == "H":
                if local:
                    bloc[0] += cx
                cx = bloc[0]
            elif haut == "V":
                if local:
                    bloc[0] += cy
                cy = bloc[0]
            elif haut == "A":
                if local:
                    bloc[5] += cx
                    bloc[6] += cy
                cx, cy = bloc[5], bloc[6]
            else:
                if local:
                    for j in range(0, n, 2):
                        bloc[j] += cx
                        bloc[j + 1] += cy
                cx, cy = bloc[-2], bloc[-1]

            if haut == "M":
                if i == 0:
                    sx, sy = cx, cy
                # Les paires qui suivent un M sont des L implicites.
                lettre = "M" if i == 0 else "L"
            else:
                lettre = haut

            if haut == "A":
                sortie.append("A %.4f %.4f %.4f %d %d %.4f %.4f"
                              % (bloc[0], bloc[1], bloc[2],
                                 int(bloc[3]), int(bloc[4]), bloc[5], bloc[6]))
            else:
                sortie.append(lettre + " "
                              + " ".join("%.4f" % b for b in bloc))
            premier = False

    return " ".join(sortie)


def placer(d, ox, oy, k=1.0):
    u"""
    Amene un chemin de son repere local a sa place finale.

    POURQUOI PAS UN transform=""
      Parce qu'un filtre pose sur un groupe transforme se calcule dans
      l'espace transforme : le grain change de finesse avec l'echelle, et
      Inkscape le rend meme par bandes quand il y a une rotation. Toute la
      scene est donc ecrite en coordonnees absolues, celle-ci comprise.

    Le calcul reste simple parce que la transformation est une homothetie
    suivie d'une translation : les rayons d'arc se multiplient par k, l'angle
    de l'arc et ses deux drapeaux ne bougent pas.
    """
    sortie = []
    for cmd, nombres in _decouper(d):
        haut = cmd.upper()
        relatif = cmd.islower()
        n = _SIGNATURE.get(haut, 0)
        jetons = []
        for i in range(0, len(nombres), n or 1):
            bloc = nombres[i:i + n]
            if haut == "A" and len(bloc) == 7:
                # rx ry rotation grand-arc sens x y. Les deux DRAPEAUX doivent
                # rester des entiers : ecrits "0.00" ils sortent de la
                # grammaire SVG et le chemin est rejete.
                jetons += ["%.2f" % (bloc[0] * k), "%.2f" % (bloc[1] * k),
                           "%.2f" % bloc[2],
                           "%d" % bloc[3], "%d" % bloc[4],
                           "%.2f" % (bloc[5] * k + (0 if relatif else ox)),
                           "%.2f" % (bloc[6] * k + (0 if relatif else oy))]
            elif haut == "H":
                jetons += ["%.2f" % (b * k + (0 if relatif else ox))
                           for b in bloc]
            elif haut == "V":
                jetons += ["%.2f" % (b * k + (0 if relatif else oy))
                           for b in bloc]
            else:
                jetons += ["%.2f" % (b * k + (0 if relatif else
                                              (ox if j % 2 == 0 else oy)))
                           for j, b in enumerate(bloc)]
        sortie.append((cmd + " " + " ".join(jetons)) if jetons else cmd)
    return " ".join(sortie)


def _decouper(d):
    u"""Le chemin, commande par commande, avec ses nombres."""
    for m in re.finditer(r'([MmLlHhVvCcSsQqTtAaZz])([^MmLlHhVvCcSsQqTtAaZz]*)',
                         d):
        nombres = [float(x) for x in
                   re.findall(r'-?\d*\.?\d+(?:[eE][-+]?\d+)?', m.group(2))]
        yield m.group(1), nombres


def ellipse(cx, cy, rx, ry):
    u"""Une ellipse en chemin, pour la donner a manger aux booleens."""
    return ("M%.2f %.2f A%.2f %.2f 0 1 0 %.2f %.2f A%.2f %.2f 0 1 0 %.2f %.2f Z"
            % (cx - rx, cy, rx, ry, cx + rx, cy, rx, ry, cx - rx, cy))


def boite(x0, y0, x1, y1):
    u"""Un rectangle en chemin : le masque le plus courant."""
    return "M%.2f %.2f L%.2f %.2f L%.2f %.2f L%.2f %.2f Z" % (
        x0, y0, x1, y0, x1, y1, x0, y1)


def lisser(d, passes=1):
    u"""
    Remplace une suite de segments droits par de VRAIES courbes.

    LE DEFAUT QUE CELA CORRIGE, mesure et non suppose
      trace.fusele() echantillonne la ligne moyenne puis relie les points par
      des segments : le contour d'un torse sortait en POLYGONE A 52 COTES.
      A l'ecran on ne compte pas les facettes, mais on les voit - c'est
      precisement ce qui fait qu'un dessin a l'air fait a la souris dans
      Paint plutot qu'a la plume. Un contour de personnage doit etre continu
      en courbure, pas seulement en position.

    L'OUTIL
      Inkscape > Chemin > Simplifier (Ctrl+L). Il ne "lisse" pas au sens ou
      il arrondirait les angles : il AJUSTE des cubiques a travers les
      points, a une tolerance donnee. Les 52 segments deviennent une dizaine
      de courbes qui passent aux memes endroits - fichier plus leger, et
      surtout contour continu.

      Deux passes arrondissent davantage et s'ecartent un peu plus du trace
      d'origine. Une seule suffit dans presque tous les cas.
    """
    actions = ";".join(["path-simplify"] * max(1, passes))
    return operer(actions, [d], _brut=True)


def union(*formes):
    return operer("union", list(formes))


def difference(socle, outil):
    return operer("difference", [socle, outil])


def intersection(*formes):
    return operer("intersection", list(formes))


def appels():
    u"""Combien de fois Inkscape a reellement ete lance (le reste : cache)."""
    return _appels[0]


if __name__ == "__main__":
    carre = "M20 20 H110 V110 H20 Z"
    rond = ("M175 120 A55 55 0 0 1 65 120 A55 55 0 0 1 175 120 Z")
    for op in ("union", "intersection", "difference"):
        d = operer(op, [carre, rond])
        print(u"%-13s %3d caracteres  %s..." % (op, len(d), d[:52]))
    print(u"%d appels a Inkscape ; le reste vient de %s"
          % (appels(), os.path.basename(CACHE)))
