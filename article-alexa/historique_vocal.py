"""
L'historique vocal d'Alexa, redessiné, et ce qu'on peut y faire.

    python3 article-alexa/historique_vocal.py

Produit `alexa-historique-vocal.webp`, son PNG et le SVG éditable.

----------------------------------------------------------------------------
REDESSINÉ, JAMAIS CAPTURÉ
----------------------------------------------------------------------------
L'application Alexa n'existe que sur mobile, et la page d'historique vocal
d'un compte contient par définition les demandes d'une personne réelle. Il
n'y a donc pas de capture possible qui ne soit pas une fuite de données.

L'écran est reconstruit, comme l'écran d'état de la batterie du dossier
obsolescence : même méthode, mêmes réserves. Ce qu'il montre est la
structure réelle de l'écran, pas une image de l'écran.

----------------------------------------------------------------------------
LES DEMANDES SONT DES BANDES, ET AUCUNE N'EST INVENTÉE
----------------------------------------------------------------------------
Le brief demande des contenus floutés. Une bande de masquage dit la même
chose qu'un flou, et elle a un avantage décisif : elle n'oblige pas à
écrire de fausses demandes vocales.

Inventer « Alexa, quel temps fait-il ? » semblerait anodin, mais ce serait
fabriquer le contenu d'un compte qui n'existe pas, dans une figure dont
tout le propos est que ce contenu est personnel. Un contrôle refuse de
dessiner si une entrée porte le moindre texte de demande.

----------------------------------------------------------------------------
LES LIBELLÉS SONT À VÉRIFIER DANS L'APPLICATION
----------------------------------------------------------------------------
Le chemin est établi : Plus, puis Paramètres, puis Confidentialité Alexa,
puis Vérifier l'historique vocal. Les filtres par date, par appareil et
par profil sont documentés, ainsi que la suppression unitaire et la
suppression de toute une période.

Les chaînes exactes de la version française, elles, n'ont pas pu être
vérifiées depuis ici. Elles sont écrites dans l'usage courant d'Amazon et
doivent être relues sur un téléphone avant publication : dans un tutoriel,
un libellé approximatif envoie le lecteur chercher un bouton qui ne porte
pas ce nom.
"""

import os

import charte as C
import dessin as D

L = 1600
MARGE = 56

INDIGO = C.VIOLET_TEXTE
INDIGO_CLAIR = (238, 232, 252)
MASQUE = (214, 216, 224)

#  ---------------------------------------------------------------------------
#  LE TÉLÉPHONE
#  ---------------------------------------------------------------------------
TEL_X, TEL_Y, TEL_L = 96, 150, 540
PAD = 26
ECRAN_X0 = TEL_X + PAD
ECRAN_X1 = TEL_X + TEL_L - PAD

#  ---------------------------------------------------------------------------
#  LES ENTRÉES DE L'HISTORIQUE
#
#  `demande` est VOLONTAIREMENT vide : voir l'en-tête. `large` est la part
#  de la largeur disponible que prend la bande de masquage, pour que les
#  demandes n'aient pas toutes la même longueur.
#  `deplie` marque celle qui montre ses commandes.
#  ---------------------------------------------------------------------------
ENTREES = (
    {"heure": "08:12", "appareil": "Echo Dot du salon",
     "demande": "", "large": 0.82, "deplie": False},
    {"heure": "08:41", "appareil": "Echo Show de la cuisine",
     "demande": "", "large": 0.58, "deplie": True},
    {"heure": "12:05", "appareil": "Echo Dot du salon",
     "demande": "", "large": 0.74, "deplie": False},
    {"heure": "19:33", "appareil": "Echo Dot de la chambre",
     "demande": "", "large": 0.46, "deplie": False},
    {"heure": "21:58", "appareil": "Echo Show de la cuisine",
     "demande": "", "large": 0.68, "deplie": False},
)

FILTRE = "Affichage : 7 derniers jours"
EN_TETE = "Historique vocal"
CHEMIN = "Plus  >  Paramètres  >  Confidentialité Alexa"
BOUTON = "Supprimer toutes mes activités de cette période"
DEPLIE = ("Réécouter l’enregistrement", "Supprimer l’enregistrement")

#  ---------------------------------------------------------------------------
#  LES REPÈRES
#
#  `cible` est le nom du point d'accroche, `y` la hauteur de l'annotation.
#  L'ordre des deux doit coïncider, sinon les filets se croisent.
#  ---------------------------------------------------------------------------
REPERES = (
    {"cible": "filtre", "y": 196,
     "titre": "Le filtre par date",
     "detail": "Aujourd’hui, les 7 ou 30 derniers jours, tout l’historique, "
               "ou une période au choix. On peut aussi filtrer par appareil "
               "et par profil."},
    {"cible": "bande", "y": 356,
     "titre": "Le contenu de la demande",
     "detail": "Amazon garde la transcription et l’enregistrement audio tant "
               "que vous ne les supprimez pas, ou jusqu’à l’échéance de "
               "suppression automatique que vous avez réglée."},
    {"cible": "deplie", "y": 516,
     "titre": "Réécouter, puis supprimer",
     "detail": "Chaque demande s’ouvre sur ses deux commandes. La suppression "
               "porte sur cette demande seule."},
    {"cible": "bouton", "y": 676,
     "titre": "Tout effacer d’un coup",
     "detail": "Le bouton du bas ne vide pas l’historique entier : il efface "
               "la période actuellement affichée."},
)

POLICES = {
    "titre": (C.POLICE_G, 19, "bold"),
    "sous": (C.POLICE_R, 17, "normal"),
    "chemin": (C.POLICE_R, 13, "normal"),
    "entete": (C.POLICE_G, 21, "bold"),
    "filtre": (C.POLICE_G, 15, "bold"),
    "heure": (C.POLICE_G, 14, "bold"),
    "appareil": (C.POLICE_R, 13, "normal"),
    "action": (C.POLICE_R, 14, "normal"),
    "bouton": (C.POLICE_G, 14, "bold"),
    "anno": (C.POLICE_G, 18, "bold"),
    "detail": (C.POLICE_R, 15, "normal"),
}
FAMILLE_SVG = "Liberation Sans, Arial, Helvetica, sans-serif"

TITRE = "CE QUE L’HISTORIQUE VOCAL PERMET D’EFFACER"
SOUS = ("l’écran « Vérifier l’historique vocal » de l’application Alexa, "
        "redessiné, contenus des demandes masqués")

X_ANNO = 760
COUDES = (690, 706, 722, 738)


def rect(couche, b, r, teinte):
    return {"quoi": "rect", "couche": couche, "b": b, "r": r, "t": teinte}


def cadre(couche, b, r, teinte, epaisseur=2):
    return {"quoi": "cadre", "couche": couche, "b": b, "r": r, "t": teinte,
            "e": epaisseur}


def trait(couche, b, teinte, epaisseur):
    return {"quoi": "trait", "couche": couche, "b": b, "t": teinte,
            "e": epaisseur}


def disque(couche, cx, cy, r, teinte):
    return {"quoi": "disque", "couche": couche, "cx": cx, "cy": cy, "r": r,
            "t": teinte}


def polygone(couche, points, teinte):
    return {"quoi": "polygone", "couche": couche, "p": points, "t": teinte}


def texte(couche, xy, contenu, police, teinte, tracking=0.0, centre=False):
    for c, nom in (("—", "cadratin"), ("–", "demi-cadratin")):
        if c in contenu:
            raise SystemExit("%s dans « %s »" % (nom, contenu[:60]))
    return {"quoi": "texte", "couche": couche, "xy": xy, "c": contenu,
            "p": police, "t": teinte, "tr": tracking, "centre": centre}


def composer():
    mesure = D.Toile(L, 10)
    fontes = {k: mesure.police(f, t) for k, (f, t, _) in POLICES.items()}

    #  ------------------------------------------------------------------
    #  CONTRÔLES
    #  ------------------------------------------------------------------
    #  LE CONTRÔLE QUI COMPTE : aucune demande vocale ne doit être écrite.
    #  La figure dit que ce contenu est personnel ; en inventer serait se
    #  contredire soi-même.
    for e in ENTREES:
        if e["demande"].strip():
            raise SystemExit(
                "l'entrée de %s porte un texte de demande : la figure masque "
                "les contenus, elle n'en invente pas" % e["heure"])
        if not 0.3 <= e["large"] <= 0.95:
            raise SystemExit("la bande de %s déborde ou disparaît"
                             % e["heure"])

    if len({e["large"] for e in ENTREES}) < len(ENTREES):
        raise SystemExit("deux bandes ont la même longueur : des demandes "
                         "toutes identiques ne ressembleraient à rien")

    deplies = [e for e in ENTREES if e["deplie"]]
    if len(deplies) != 1:
        raise SystemExit("une seule entrée montre ses commandes, la table en "
                         "compte %d" % len(deplies))

    for a, b in zip(REPERES, REPERES[1:]):
        if b["y"] <= a["y"]:
            raise SystemExit("les annotations ne sont pas dans l'ordre")

    o = []
    o.append(texte("titre", (MARGE, 46), TITRE, "titre", D.ENCRE, 2.2))
    sous = D.typo(SOUS)
    if mesure.mesure(sous, fontes["sous"]) > L - 2 * MARGE:
        raise SystemExit("le sous-titre déborde")
    o.append(texte("titre", (MARGE, 74), sous, "sous", D.FAIBLE))

    #  --------------------------------------------------------------  écran
    ecran, masques, textes_e = [], [], []
    largeur_u = ECRAN_X1 - ECRAN_X0
    y = TEL_Y + PAD + 6

    textes_e.append(texte("écran", (ECRAN_X0, y), D.typo(CHEMIN), "chemin",
                          D.FAIBLE))
    y += 26
    textes_e.append(texte("écran", (ECRAN_X0, y), D.typo(EN_TETE), "entete",
                          D.ENCRE))
    y += 40

    #  Le filtre, dans sa pastille.
    filtre_h = 40
    ancres = {"filtre": (ECRAN_X1 + 8, y + filtre_h / 2.0)}
    ecran.append(rect("écran", [ECRAN_X0, y, ECRAN_X1, y + filtre_h], 10,
                      INDIGO_CLAIR))
    textes_e.append(texte("écran", (ECRAN_X0 + 14, y + 11), D.typo(FILTRE),
                          "filtre", INDIGO))
    #  Le chevron du menu déroulant.
    cx, cy = ECRAN_X1 - 20, y + filtre_h / 2.0
    ecran.append(polygone("écran", [(cx - 6, cy - 3), (cx + 6, cy - 3),
                                    (cx, cy + 4)], INDIGO))
    y += filtre_h + 22

    for i, e in enumerate(ENTREES):
        haut = y
        textes_e.append(texte("écran", (ECRAN_X0, y), e["heure"], "heure",
                              D.ENCRE))
        textes_e.append(texte("écran", (ECRAN_X0 + 54, y + 1),
                              D.typo(e["appareil"]), "appareil", D.FAIBLE))
        y += 24

        #  La bande de masquage, à la place de la demande.
        bl = largeur_u * e["large"]
        masques.append(rect("masques", [ECRAN_X0, y, ECRAN_X0 + bl, y + 15],
                            7, MASQUE))
        if i == 1:
            ancres["bande"] = (ECRAN_X0 + bl + 8, y + 8)
        y += 15 + 14

        if e["deplie"]:
            for j, action in enumerate(DEPLIE):
                teinte_a = INDIGO if j == 0 else C.ALERTE
                if j == 0:
                    #  Un triangle de lecture, dessiné et non écrit : un
                    #  caractère « ▶ » n'existe pas dans la police.
                    ecran.append(polygone(
                        "écran", [(ECRAN_X0 + 4, y + 2), (ECRAN_X0 + 4,
                                                          y + 14),
                                  (ECRAN_X0 + 14, y + 8)], teinte_a))
                else:
                    #  Une corbeille sommaire : couvercle et cuve.
                    bx = ECRAN_X0 + 3
                    ecran.append(rect("écran", [bx, y + 1, bx + 12, y + 3],
                                      1, teinte_a))
                    ecran.append(cadre("écran", [bx + 1, y + 4, bx + 11,
                                                 y + 15], 2, teinte_a, 2))
                textes_e.append(texte("écran", (ECRAN_X0 + 24, y),
                                      D.typo(action), "action", teinte_a))
                if j == 1:
                    ancres["deplie"] = (ECRAN_X1 + 8, y + 8)
                y += 26
            y += 4

        if i < len(ENTREES) - 1:
            ecran.append(trait("écran", [ECRAN_X0, y, ECRAN_X1, y],
                               D.FILET, 1))
            y += 18
        del haut

    y += 10
    bouton_h = 44
    ecran.append(cadre("écran", [ECRAN_X0, y, ECRAN_X1, y + bouton_h], 10,
                       C.ALERTE, 2))
    lb = D.typo(BOUTON)
    lignes_b = mesure.couper(lb, fontes["bouton"], largeur_u - 28)
    if len(lignes_b) > 1:
        raise SystemExit("le libellé du bouton tient en %d lignes"
                         % len(lignes_b))
    textes_e.append(texte("écran", ((ECRAN_X0 + ECRAN_X1) / 2.0, y + 14),
                          lignes_b[0], "bouton", C.ALERTE, centre=True))
    ancres["bouton"] = (ECRAN_X1 + 8, y + bouton_h / 2.0)
    y += bouton_h

    tel_h = y + PAD - TEL_Y
    chassis = [rect("châssis", [TEL_X, TEL_Y, TEL_X + TEL_L, TEL_Y + tel_h],
                    26, D.BLANC),
               cadre("châssis", [TEL_X, TEL_Y, TEL_X + TEL_L, TEL_Y + tel_h],
                     26, (198, 202, 212), 2)]

    o.extend(chassis)
    o.extend(ecran)
    o.extend(masques)
    o.extend(textes_e)

    #  -----------------------------------------------------------  repères
    manquantes = [r["cible"] for r in REPERES if r["cible"] not in ancres]
    if manquantes:
        raise SystemExit("ces repères ne pointent sur rien : %s" % manquantes)

    filets, points = [], []
    for r, coude in zip(REPERES, COUDES):
        ax, ay = ancres[r["cible"]]
        points.append(disque("points", ax, ay, 4, INDIGO))
        filets.append(trait("filets", [ax, ay, coude, ay], INDIGO, 2))
        filets.append(trait("filets", [coude, ay, coude, r["y"] + 9],
                            INDIGO, 2))
        filets.append(trait("filets", [coude, r["y"] + 9, X_ANNO - 12,
                                       r["y"] + 9], INDIGO, 2))
    o.extend(filets)
    o.extend(points)

    annos, boites = [], []
    largeur_a = L - MARGE - X_ANNO
    for r in REPERES:
        t = D.typo(r["titre"])
        if mesure.mesure(t, fontes["anno"]) > largeur_a:
            raise SystemExit("le titre « %s » déborde" % t)
        annos.append(texte("annotations", (X_ANNO, r["y"]), t, "anno",
                           D.ENCRE))
        yy = r["y"] + 28
        lignes = mesure.couper(D.typo(r["detail"]), fontes["detail"],
                               largeur_a)
        if len(lignes) > 3:
            raise SystemExit("le détail de « %s » tient en %d lignes"
                             % (t, len(lignes)))
        for ligne in lignes:
            annos.append(texte("annotations", (X_ANNO, yy), ligne, "detail",
                               D.GRIS))
            yy += 22
        boites.append((r["y"], yy, t))

    for (h0, b0, n0), (h1, b1, n1) in zip(boites, boites[1:]):
        if b0 > h1 - 12:
            raise SystemExit("« %s » descend jusqu'à %d et « %s » commence à "
                             "%d" % (n0, b0, n1, h1))
    o.extend(annos)

    H = int(max(TEL_Y + tel_h, boites[-1][1]) + 48)
    o.insert(0, rect("fond", [0, 0, L, H], 0, D.PAPIER))
    return H, o


def rendre_matriciel(H, ordres, base):
    t = D.Toile(L, H)
    fontes = {k: t.police(f, taille) for k, (f, taille, _) in POLICES.items()}
    for a in ordres:
        if a["quoi"] == "rect":
            t.rrect(a["b"], a["r"], teinte=a["t"])
        elif a["quoi"] == "cadre":
            t.rrect(a["b"], a["r"], contour=a["t"], epaisseur=a["e"])
        elif a["quoi"] == "trait":
            t.ligne(a["b"], a["t"], a["e"])
        elif a["quoi"] == "disque":
            t.disque(a["cx"], a["cy"], a["r"], teinte=a["t"])
        elif a["quoi"] == "polygone":
            t.polygone(a["p"], a["t"])
        else:
            f = fontes[a["p"]]
            x, y = a["xy"]
            if a["centre"]:
                x -= t.mesure(a["c"], f) / 2.0
            if a["tr"]:
                t.espace((x, y), a["c"], f, a["t"], a["tr"])
            else:
                t.texte((x, y), a["c"], f, a["t"])
    D.enregistrer(t.final(L, H), base, L, H)


def rendre_svg(H, ordres, base):
    montees = {c: C.police(f, t).getmetrics()[0]
               for c, (f, t, _) in POLICES.items()}

    def teinte(t):
        return "#%02x%02x%02x" % tuple(t)

    def propre(s):
        return (s.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;"))

    couches = []
    for a in ordres:
        if not couches or couches[-1][0] != a["couche"]:
            couches.append((a["couche"], []))
        couches[-1][1].append(a)

    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<svg xmlns="http://www.w3.org/2000/svg" '
           'xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
           'width="%dpx" height="%dpx" viewBox="0 0 %d %d" '
           'version="1.1">' % (L, H, L, H),
           '  <title>%s</title>' % propre(TITRE),
           '  <desc>%s</desc>' % propre(SOUS)]

    for i, (nom, groupe) in enumerate(couches):
        out.append('  <g inkscape:groupmode="layer" inkscape:label="%s" '
                   'id="couche%d">' % (nom, i + 1))
        for a in groupe:
            if a["quoi"] in ("rect", "cadre"):
                x0, y0, x1, y1 = a["b"]
                if a["quoi"] == "rect":
                    peinture = 'fill="%s"' % teinte(a["t"])
                else:
                    peinture = ('fill="none" stroke="%s" stroke-width="%g"'
                                % (teinte(a["t"]), a["e"]))
                out.append('    <rect x="%g" y="%g" width="%g" height="%g" '
                           'rx="%g" %s/>'
                           % (x0, y0, x1 - x0, y1 - y0, a["r"], peinture))
            elif a["quoi"] == "trait":
                x0, y0, x1, y1 = a["b"]
                out.append('    <line x1="%g" y1="%g" x2="%g" y2="%g" '
                           'stroke="%s" stroke-width="%g" '
                           'stroke-linecap="round"/>'
                           % (x0, y0, x1, y1, teinte(a["t"]), a["e"]))
            elif a["quoi"] == "disque":
                out.append('    <circle cx="%g" cy="%g" r="%g" fill="%s"/>'
                           % (a["cx"], a["cy"], a["r"], teinte(a["t"])))
            elif a["quoi"] == "polygone":
                pts = " ".join("%g,%g" % p for p in a["p"])
                out.append('    <polygon points="%s" fill="%s"/>'
                           % (pts, teinte(a["t"])))
            else:
                _, taille, graisse = POLICES[a["p"]]
                espacement = (' letter-spacing="%g"' % a["tr"]
                              if a["tr"] else "")
                ancre = ' text-anchor="middle"' if a["centre"] else ""
                out.append('    <text x="%g" y="%g" font-family="%s" '
                           'font-size="%g" font-weight="%s" fill="%s"%s%s'
                           ' xml:space="preserve">%s</text>'
                           % (a["xy"][0], a["xy"][1] + montees[a["p"]],
                              FAMILLE_SVG, taille, graisse, teinte(a["t"]),
                              espacement, ancre, propre(a["c"])))
        out.append('  </g>')
    out.append('</svg>')

    with open(base + ".svg", "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    return len(couches), sum(1 for a in ordres if a["quoi"] == "texte")


def principal():
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "alexa-historique-vocal")
    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5),
               ("indigo", INDIGO, 4.5), ("alerte", C.ALERTE, 4.5))

    H, ordres = composer()
    rendre_matriciel(H, ordres, base)
    couches, textes = rendre_svg(H, ordres, base)

    print("  %-36s %.0f Ko"
          % (os.path.basename(base + ".svg"),
             os.path.getsize(base + ".svg") / 1024.0))
    print("  %d x %d, %d calques, %d textes" % (L, H, couches, textes))
    print()
    print("  %d entrées, aucune ne porte de demande écrite" % len(ENTREES))
    for r in REPERES:
        print("  repère %-10s vers « %s »" % (r["cible"], r["titre"]))


if __name__ == "__main__":
    principal()
