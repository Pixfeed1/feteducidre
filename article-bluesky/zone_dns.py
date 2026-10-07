"""
L'enregistrement TXT _atproto dans une zone DNS, redessiné.

    python3 article-bluesky/zone_dns.py

Produit `bluesky-zone-dns.webp`, son PNG et le SVG éditable.

----------------------------------------------------------------------------
UN TABLEAU, ET CETTE FOIS C'EST JUSTIFIÉ
----------------------------------------------------------------------------
Les figures précédentes de la série évitent la grille de cases, parce
qu'elles décrivent des chaînes ou des durées. Ici, non : une zone DNS EST
un tableau, chez tous les hébergeurs sans exception, avec les mêmes
colonnes. Lui donner une autre forme éloignerait le lecteur de ce qu'il a
sous les yeux.

----------------------------------------------------------------------------
LE FORMAT EST VÉRIFIÉ, PAS SUPPOSÉ
----------------------------------------------------------------------------
Trois domaines qui utilisent réellement un pseudo Bluesky ont été
interrogés en DNS avant d'écrire cette figure :

    _atproto.pfrazee.com    did=did:plc:ragtjsm2j2vknwkz3zp4oxrd
    _atproto.jay.bsky.team  did=did:plc:oky5czdrnfjpqslsw2a5iclo
    _atproto.bsky.app       did=did:plc:z72i7hdynmk6r22z27h6tvur

D'où les trois constantes ci-dessous : le préfixe « did= » fait partie de
la valeur, et le suffixe compte 24 caractères dans les trois cas.

----------------------------------------------------------------------------
LE DID N'EST PAS FLOUTÉ, ET C'EST VOULU
----------------------------------------------------------------------------
Le brief demandait de le masquer. Il est publié dans le DNS public par
construction : n'importe qui le lit en trois secondes, c'est le mécanisme
même de la résolution des pseudos. Le présenter comme un secret
apprendrait au lecteur quelque chose de faux.

Le suffixe est donc remplacé par une bande, non pour le cacher mais pour
ne pas imprimer un identifiant que des lecteurs recopieraient. Une
annotation dit explicitement qu'il est public.

----------------------------------------------------------------------------
LES EXEMPLES NE POINTENT NULLE PART
----------------------------------------------------------------------------
L'adresse IP de la ligne A est prise dans 203.0.113.0/24, la plage que le
RFC 5737 réserve à la documentation. Elle ne peut appartenir à personne.
Même principe pour le domaine, « votredomaine.fr », et pour l'hébergeur.
"""

import os

import charte as C
import dessin as D

L = 1600
MARGE = 56

INDIGO = C.VIOLET_TEXTE
INDIGO_CLAIR = (238, 232, 252)
MASQUE = (206, 209, 219)

#  Vérifié par interrogation DNS de trois domaines réels : voir l'en-tête.
PREFIXE_DID = "did=did:plc:"
LONGUEUR_DID = 24

DOMAINE = "votredomaine.fr"

#  ---------------------------------------------------------------------------
#  LES LIGNES DE LA ZONE
#
#  `vedette` marque celle que l'article fait ajouter. Les autres sont là
#  pour que le lecteur reconnaisse son écran, pas pour être lues.
#  ---------------------------------------------------------------------------
LIGNES = (
    {"type": "A", "nom": "@", "ttl": "3600",
     "valeur": "203.0.113.10", "vedette": False},
    {"type": "CNAME", "nom": "www", "ttl": "3600",
     "valeur": "votredomaine.fr.", "vedette": False},
    {"type": "MX", "nom": "@", "ttl": "3600",
     "valeur": "10 mx1.hebergeur.fr.", "vedette": False},
    {"type": "TXT", "nom": "@", "ttl": "3600",
     "valeur": "v=spf1 include:_spf.hebergeur.fr ~all", "vedette": False},
    {"type": "TXT", "nom": "_atproto", "ttl": "3600",
     "valeur": PREFIXE_DID, "vedette": True},
)

COLONNES = (("Type", 0), ("Nom", 150), ("TTL", 330), ("Valeur", 430))

#  Les annotations sont SOUS le panneau, pas à sa droite.
#
#  Premier jet : trois blocs à droite, trois filets horizontaux partant des
#  champs. Les trois champs étant sur la MÊME ligne, les trois filets la
#  traversaient de bout en bout et la barraient littéralement. Les repères
#  descendent donc maintenant hors du panneau avant de rejoindre leur bloc,
#  chacun à une hauteur différente pour ne pas se croiser.
REPERES = (
    {"colonne": "Type", "bloc": 0, "creux": 26,
     "titre": "Le type : TXT",
     "detail": "Ni A, ni CNAME. Un simple enregistrement de texte, que le "
               "réseau vient lire pour vérifier que le domaine est bien à "
               "vous."},
    {"colonne": "Nom", "bloc": 1, "creux": 50,
     "titre": "Le nom : _atproto",
     "detail": "Rien d’autre, surtout pas le domaine : l’hébergeur l’ajoute "
               "tout seul. Selon les interfaces, le champ s’appelle Nom, "
               "Hôte ou Sous-domaine."},
    {"colonne": "Valeur", "bloc": 2, "creux": 74,
     "titre": "La valeur : did=did:plc:",
     "detail": "Le « did= » fait partie de la valeur. Les 24 caractères qui "
               "suivent désignent votre compte, et ils sont publics : "
               "n’importe qui peut les lire dans le DNS."},
)

POLICES = {
    "titre": (C.POLICE_G, 19, "bold"),
    "sous": (C.POLICE_R, 17, "normal"),
    "panneau": (C.POLICE_G, 17, "bold"),
    "entete": (C.POLICE_G, 13, "bold"),
    "cellule": (C.POLICE_R, 15, "normal"),
    "vedette": (C.POLICE_G, 15, "bold"),
    "anno": (C.POLICE_G, 18, "bold"),
    "detail": (C.POLICE_R, 15, "normal"),
}
FAMILLE_SVG = "Liberation Sans, Arial, Helvetica, sans-serif"

TITRE = "UNE SEULE LIGNE À AJOUTER DANS LA ZONE DNS"
SOUS = ("l’enregistrement TXT qui fait d’un nom de domaine un pseudo "
        "Bluesky, redessiné d’après trois domaines réels interrogés en DNS")

PAN_X, PAN_Y = 96, 150
PAN_L = L - 2 * PAN_X
PAD = 26
LIGNE_H = 42

#  Trois colonnes d'annotation sous le panneau.
BLOCS = (PAN_X, PAN_X + 486, PAN_X + 972)
LARGEUR_BLOC = 444


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
    vedettes = [l for l in LIGNES if l["vedette"]]
    if len(vedettes) != 1:
        raise SystemExit("une seule ligne est celle à ajouter, la table en "
                         "compte %d" % len(vedettes))
    v = vedettes[0]
    if v["type"] != "TXT" or v["nom"] != "_atproto":
        raise SystemExit("la ligne en vedette doit être un TXT sur _atproto, "
                         "elle est « %s %s »" % (v["type"], v["nom"]))
    if v["valeur"] != PREFIXE_DID:
        raise SystemExit("la valeur en vedette doit être le préfixe vérifié "
                         "« %s »" % PREFIXE_DID)

    #  Aucun exemple ne doit pointer vers une adresse qui existe : la plage
    #  203.0.113.0/24 est réservée à la documentation par le RFC 5737.
    for l in LIGNES:
        if l["type"] == "A" and not l["valeur"].startswith("203.0.113."):
            raise SystemExit(
                "l'adresse d'exemple %s sort de la plage de documentation : "
                "elle appartient à quelqu'un" % l["valeur"])

    noms = {c for c, _ in COLONNES}
    inconnues = [r["colonne"] for r in REPERES if r["colonne"] not in noms]
    if inconnues:
        raise SystemExit("ces repères visent une colonne inexistante : %s"
                         % inconnues)
    if len(REPERES) != len(BLOCS):
        raise SystemExit("il faut un bloc par repère")
    if sorted(r["bloc"] for r in REPERES) != list(range(len(BLOCS))):
        raise SystemExit("deux repères visent le même bloc")
    #  Les repères descendent à des hauteurs distinctes, sinon leurs
    #  segments horizontaux se superposent.
    if len({r["creux"] for r in REPERES}) != len(REPERES):
        raise SystemExit("deux repères descendent à la même hauteur : leurs "
                         "filets se confondraient")
    #  L'ordre des blocs doit suivre celui des colonnes, sinon les filets
    #  se croisent en chemin.
    rang = {nom: i for i, (nom, _) in enumerate(COLONNES)}
    if [r["bloc"] for r in REPERES] != sorted(
            range(len(REPERES)), key=lambda i: rang[REPERES[i]["colonne"]]):
        raise SystemExit("l'ordre des blocs ne suit pas celui des colonnes : "
                         "les filets se croiseraient")

    o = []
    o.append(texte("titre", (MARGE, 46), TITRE, "titre", D.ENCRE, 2.2))
    sous = D.typo(SOUS)
    if mesure.mesure(sous, fontes["sous"]) > L - 2 * MARGE:
        raise SystemExit("le sous-titre déborde")
    o.append(texte("titre", (MARGE, 74), sous, "sous", D.FAIBLE))

    #  -------------------------------------------------------------  panneau
    x0 = PAN_X + PAD
    x1 = PAN_X + PAN_L - PAD
    colonnes = {nom: x0 + dec for nom, dec in COLONNES}

    corps, textes_p, masques = [], [], []
    y = PAN_Y + PAD

    textes_p.append(texte("panneau", (x0, y), "Zone DNS  ·  " + DOMAINE,
                          "panneau", D.ENCRE))
    y += 36

    for nom, _ in COLONNES:
        textes_p.append(texte("panneau", (colonnes[nom], y), nom.upper(),
                              "entete", D.FAIBLE, 1.0))
    y += 22
    corps.append(trait("panneau", [x0, y, x1, y], D.FILET, 2))
    y += 6

    ancres = {}
    for l in LIGNES:
        if l["vedette"]:
            corps.append(rect("panneau", [x0 - 10, y - 3, x1 + 10,
                                          y + LIGNE_H - 9], 8, INDIGO_CLAIR))
        police = "vedette" if l["vedette"] else "cellule"
        teinte_l = INDIGO if l["vedette"] else D.GRIS
        teinte_f = INDIGO if l["vedette"] else D.ENCRE

        for nom, cle in (("Type", "type"), ("Nom", "nom"), ("TTL", "ttl")):
            t = l[cle]
            textes_p.append(texte("panneau", (colonnes[nom], y + 6), t,
                                  police,
                                  teinte_f if cle != "ttl" else teinte_l))
            if l["vedette"] and nom in ancres_voulus():
                #  Sous le champ, au bas de la ligne : le filet descend
                #  hors du panneau au lieu de traverser la ligne.
                ancres[nom] = (colonnes[nom]
                               + mesure.mesure(t, fontes[police]) / 2.0,
                               y + LIGNE_H - 9)

        xv = colonnes["Valeur"]
        valeur = D.typo(l["valeur"])
        if mesure.mesure(valeur, fontes[police]) > x1 - xv:
            raise SystemExit("la valeur « %s » déborde de sa colonne"
                             % valeur[:40])
        textes_p.append(texte("panneau", (xv, y + 6), valeur, police,
                              teinte_f))

        if l["vedette"]:
            #  Le suffixe du DID : une bande, pour ne pas imprimer un
            #  identifiant que des lecteurs recopieraient.
            bx = xv + mesure.mesure(valeur, fontes[police]) + 2
            bl = min(LONGUEUR_DID * 7.0, x1 - bx)
            masques.append(rect("masques", [bx, y + 9, bx + bl, y + 23], 6,
                                MASQUE))
            ancres["Valeur"] = ((xv + bx + bl) / 2.0, y + LIGNE_H - 9)

        y += LIGNE_H

    pan_h = y + PAD - 6 - PAN_Y
    panneau = [rect("châssis", [PAN_X, PAN_Y, PAN_X + PAN_L, PAN_Y + pan_h],
                    14, D.BLANC),
               cadre("châssis", [PAN_X, PAN_Y, PAN_X + PAN_L, PAN_Y + pan_h],
                     14, (204, 208, 218), 2)]

    o.extend(panneau)
    o.extend(corps)
    o.extend(masques)
    o.extend(textes_p)

    #  -----------------------------------------------------------  repères
    absentes = [r["colonne"] for r in REPERES if r["colonne"] not in ancres]
    if absentes:
        raise SystemExit("ces repères ne pointent sur rien : %s" % absentes)

    y_blocs = PAN_Y + pan_h + max(r["creux"] for r in REPERES) + 36

    filets, points = [], []
    for r in REPERES:
        ax, ay = ancres[r["colonne"]]
        bx = BLOCS[r["bloc"]] + 2
        palier = PAN_Y + pan_h + r["creux"]
        points.append(disque("points", ax, ay, 4, INDIGO))
        filets.append(trait("filets", [ax, ay, ax, palier], INDIGO, 2))
        filets.append(trait("filets", [ax, palier, bx, palier], INDIGO, 2))
        filets.append(trait("filets", [bx, palier, bx, y_blocs - 6],
                            INDIGO, 2))
    o.extend(filets)
    o.extend(points)

    annos, bas = [], 0
    for r in REPERES:
        bx = BLOCS[r["bloc"]]
        t = D.typo(r["titre"])
        if mesure.mesure(t, fontes["anno"]) > LARGEUR_BLOC:
            raise SystemExit("le titre « %s » déborde de son bloc" % t)
        annos.append(texte("annotations", (bx, y_blocs), t, "anno", D.ENCRE))
        yy = y_blocs + 28
        lignes = mesure.couper(D.typo(r["detail"]), fontes["detail"],
                               LARGEUR_BLOC)
        if len(lignes) > 4:
            raise SystemExit("le détail de « %s » tient en %d lignes"
                             % (t, len(lignes)))
        for ligne in lignes:
            annos.append(texte("annotations", (bx, yy), ligne, "detail",
                               D.GRIS))
            yy += 22
        bas = max(bas, yy)
    o.extend(annos)
    boites = [(y_blocs, bas, "blocs")]

    H = int(max(PAN_Y + pan_h, boites[-1][1]) + 46)
    o.insert(0, rect("fond", [0, 0, L, H], 0, D.PAPIER))
    return H, o


def ancres_voulus():
    return {r["colonne"] for r in REPERES}


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
                        "bluesky-zone-dns")
    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5),
               ("indigo", INDIGO, 4.5))

    H, ordres = composer()
    rendre_matriciel(H, ordres, base)
    couches, textes = rendre_svg(H, ordres, base)

    print("  %-32s %.0f Ko"
          % (os.path.basename(base + ".svg"),
             os.path.getsize(base + ".svg") / 1024.0))
    print("  %d x %d, %d calques, %d textes" % (L, H, couches, textes))
    print()
    print("  préfixe vérifié    %s" % PREFIXE_DID)
    print("  suffixe            %d caractères" % LONGUEUR_DID)
    for r in REPERES:
        print("  repère %-8s vers « %s »" % (r["colonne"], r["titre"]))


if __name__ == "__main__":
    principal()
