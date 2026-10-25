"""
Le labo : un petit Internet dans une seule machine Linux.

    python3 article-vpn-proxy/labo.py

Produit `vpn-ou-proxy-labo.webp`, son PNG et le SVG éditable.

----------------------------------------------------------------------------
CE QUE CETTE FIGURE REMPLACE
----------------------------------------------------------------------------
Une première version circulait hors charte : fond crème, titres bleu
marine, bandeaux sombres au-dessus de chaque boîte, pastilles oranges,
tunnel bleu vif et filtre de grain. Le contenu est repris mot pour mot,
adresses comprises.

----------------------------------------------------------------------------
LES PASTILLES NE SONT PAS EN ALERTE
----------------------------------------------------------------------------
Les quatre points d'écoute étaient en orange, la teinte des avertissements.
Un point de mesure n'avertit de rien : il dit où l'on regarde. Ils passent
donc au violet des aplats, celui que la charte réserve justement aux
pastilles de numéro, avec le blanc dessus à 4,75:1.

L'alerte et le vert ne servent nulle part ici. Un schéma qui décrit un
montage n'oppose pas un état sain à un état dégradé.

----------------------------------------------------------------------------
DEUX CHEMINS, DEUX TRAITEMENTS
----------------------------------------------------------------------------
Le câblage ordinaire est en gris : c'est de la plomberie, elle ne doit
pas crier. Le tunnel WireGuard, lui, est un second chemin posé par-dessus
le premier, et prend l'ambre, la seconde teinte neutre de la charte. Il
est en pointillé parce qu'il ne remplace pas le câble : il passe dedans.

----------------------------------------------------------------------------
CE QUE LE SOUS-TITRE COMPTE
----------------------------------------------------------------------------
« Six espaces réseau isolés, deux vrais navigateurs et quatre points
d'écoute. » Les trois nombres sont recomptés à chaque dessin sur les
machines, les navigateurs et les pastilles réellement posés.
"""

import os

import charte as C
import dessin as D

L = 1600
MARGE = 56

INDIGO = C.VIOLET_TEXTE
PASTILLE = C.VIOLET          # l'aplat des pastilles de numéro
TUNNEL = (180, 83, 9)        # l'ambre, pour le second chemin
CABLE = (150, 152, 162)

NAVIGATEURS = ("Chromium 153", "Firefox 158")

#  ---------------------------------------------------------------------------
#  LES SIX MACHINES
#
#  Chacune tourne dans son propre espace de noms réseau. `boite` donne le
#  rectangle, `adresse` se range à droite du nom, `ecoute` porte le numéro
#  du point d'écoute quand la machine en abrite un.
#  ---------------------------------------------------------------------------
MACHINES = (
    {"nom": "Ton PC", "boite": (56, 336, 316, 486),
     "lignes": ("Chromium 153, Firefox 158", "192.168.1.10",
                "proxy ou VPN réglé ici")},
    {"nom": "Box et FAI", "boite": (376, 326, 716, 496),
     "lignes": ("Ton IP publique : 203.0.113.10",
                "Résolveur DNS du FAI,",
                "qui note chaque nom demandé")},
    {"nom": "Serveur proxy", "boite": (926, 146, 1544, 300),
     "adresse": "198.51.100.20", "ecoute": 2,
     "lignes": ("Squid : proxy HTTP (port 3128) et HTTPS (3129)",
                "Dante : proxy SOCKS5 (port 1080)",
                "réglages d’usine")},
    {"nom": "Serveur VPN", "boite": (926, 330, 1544, 456),
     "adresse": "198.51.100.30", "ecoute": 3,
     "lignes": ("WireGuard, UDP 51820",
                "résolveur DNS du VPN (10.8.0.1)")},
    {"nom": "Le site visité", "boite": (926, 486, 1544, 586),
     "adresse": "192.0.2.80", "ecoute": 4,
     "lignes": ("site.test en HTTPS et en HTTP, page WebRTC",)},
    {"nom": "Serveur STUN tiers", "boite": (926, 616, 1544, 716),
     "adresse": "stun.visio.test",
     "lignes": ("celui qu’appelle la page WebRTC",)},
)

INTERNET = (826, 406, 54)    # le nuage, qui n'est pas une machine du labo

#  Le point 1 ne tient dans aucune boîte : il est sur la ligne elle-même.
ECOUTE_LIGNE = {"numero": 1, "xy": (346, 406)}

POINTS = (
    (1, "ta ligne chez le FAI : capture et journal du résolveur DNS"),
    (2, "le serveur proxy : capture, journaux de Squid et de Dante"),
    (3, "le serveur VPN : capture à l’intérieur du tunnel"),
    (4, "le site : journal des requêtes, capture et serveur STUN"),
)

#  Ce que le sous-titre annonce, et que la figure doit retrouver seule.
ANNONCES = {"espaces réseau": 6, "navigateurs": 2, "points d’écoute": 4}

POLICES = {
    "titre": (C.POLICE_G, 19, "bold"),
    "sous": (C.POLICE_R, 17, "normal"),
    "machine": (C.POLICE_G, 20, "bold"),
    "adresse": (C.POLICE_G, 15, "bold"),
    "ligne": (C.POLICE_R, 15, "normal"),
    "nuage": (C.POLICE_G, 16, "bold"),
    "tunnel": (C.POLICE_G, 15, "bold"),
    "numero": (C.POLICE_G, 17, "bold"),
    "bande": (C.POLICE_G, 13, "bold"),
    "point": (C.POLICE_R, 15, "normal"),
    "note": (C.POLICE_R, 14, "normal"),
}
FAMILLE_SVG = "Liberation Sans, Arial, Helvetica, sans-serif"

TITRE = "LE LABO : UN PETIT INTERNET DANS UNE SEULE MACHINE LINUX"
SOUS = ("six espaces réseau isolés, deux vrais navigateurs et quatre points "
        "d’écoute ; tests du 25 octobre 2026")
TUNNEL_MOT = "Mode VPN : tunnel WireGuard chiffré, du PC jusqu’au serveur VPN"
BANDE = "LES QUATRE POINTS D’ÉCOUTE"
NOTE = ("Adresses de documentation (RFC 5737). Chaque machine tourne dans "
        "son propre espace de noms réseau Linux, reliée aux autres par des "
        "câbles virtuels.")
SIGNATURE = "jurojin.net"

R_PASTILLE = 17
Y_BANDE = 556


def rect(couche, b, r, teinte=None, contour=None, epaisseur=2):
    return {"quoi": "rect", "couche": couche, "b": b, "r": r, "t": teinte,
            "contour": contour, "e": epaisseur}


def trait(couche, b, teinte, epaisseur, tirets=None):
    return {"quoi": "trait", "couche": couche, "b": b, "t": teinte,
            "e": epaisseur, "tirets": tirets}


def courbe(couche, points, teinte, epaisseur, tirets=None):
    return {"quoi": "courbe", "couche": couche, "pts": points, "t": teinte,
            "e": epaisseur, "tirets": tirets}


def disque(couche, cx, cy, r, teinte=None, contour=None, epaisseur=2):
    return {"quoi": "disque", "couche": couche, "cx": cx, "cy": cy, "r": r,
            "t": teinte, "contour": contour, "e": epaisseur}


def fleche(couche, x0, y0, x1, y1, teinte, epaisseur):
    return {"quoi": "fleche", "couche": couche, "b": [x0, y0, x1, y1],
            "t": teinte, "e": epaisseur}


def texte(couche, xy, contenu, police, teinte, tracking=0.0, centre=False,
          droite=False):
    for c, nom in (("—", "cadratin"), ("–", "demi-cadratin")):
        if c in contenu:
            raise SystemExit("%s dans « %s »" % (nom, contenu[:60]))
    return {"quoi": "texte", "couche": couche, "xy": xy, "c": contenu,
            "p": police, "t": teinte, "tr": tracking, "centre": centre,
            "droite": droite}


def composer():
    mesure = D.Toile(L, 10)
    fontes = {k: mesure.police(f, t) for k, (f, t, _) in POLICES.items()}

    #  ------------------------------------------------------------------
    #  CONTRÔLES
    #  ------------------------------------------------------------------
    ecoutes = sorted([m["ecoute"] for m in MACHINES if "ecoute" in m]
                     + [ECOUTE_LIGNE["numero"]])
    trouve = {"espaces réseau": len(MACHINES),
              "navigateurs": len(NAVIGATEURS),
              "points d’écoute": len(ecoutes)}
    for quoi, attendu in ANNONCES.items():
        if trouve[quoi] != attendu:
            raise SystemExit("le sous-titre annonce %d %s, la figure en "
                             "compte %d" % (attendu, quoi, trouve[quoi]))
    if ecoutes != list(range(1, len(ecoutes) + 1)):
        raise SystemExit("les points d'écoute ne sont pas numérotés de 1 à "
                         "%d : %s" % (len(ecoutes), ecoutes))
    if [n for n, _ in POINTS] != ecoutes:
        raise SystemExit("la légende du bas ne décrit pas les mêmes points "
                         "que le schéma")

    #  Les navigateurs annoncés doivent être ceux qui sont écrits sur le PC.
    pc = MACHINES[0]
    for nav in NAVIGATEURS:
        if not any(nav in li for li in pc["lignes"]):
            raise SystemExit("« %s » est compté dans le sous-titre mais "
                             "n'apparaît pas sur le PC" % nav)

    #  Aucune boîte ne doit en recouvrir une autre.
    for i, a in enumerate(MACHINES):
        ax0, ay0, ax1, ay1 = a["boite"]
        if ax0 < MARGE or ax1 > L - MARGE:
            raise SystemExit("la boîte de « %s » sort du cadre" % a["nom"])
        for b in MACHINES[i + 1:]:
            bx0, by0, bx1, by1 = b["boite"]
            if ax0 < bx1 and bx0 < ax1 and ay0 < by1 and by0 < ay1:
                raise SystemExit("les boîtes de « %s » et « %s » se "
                                 "chevauchent" % (a["nom"], b["nom"]))

    o = []
    o.append(texte("titre", (MARGE, 46), D.typo(TITRE), "titre", D.ENCRE,
                   2.2))
    sous = D.typo(SOUS)
    if mesure.mesure(sous, fontes["sous"]) > L - 2 * MARGE:
        raise SystemExit("le sous-titre déborde")
    o.append(texte("titre", (MARGE, 74), sous, "sous", D.FAIBLE))

    #  ---------------------------------------------------------  le câblage
    cables = []
    cx, cy, cr = INTERNET
    pc_b, fai_b = MACHINES[0]["boite"], MACHINES[1]["boite"]
    cables.append(trait("cables", [pc_b[2], 406, fai_b[0], 406], CABLE, 3))
    cables.append(trait("cables", [fai_b[2], 406, cx - cr, 406], CABLE, 3))
    for m in MACHINES[2:]:
        x0, y0, x1, y1 = m["boite"]
        cables.append(trait("cables", [cx + cr, cy, x0, (y0 + y1) / 2.0],
                            CABLE, 3))
    o.extend(cables)

    #  ----------------------------------------------------------  le tunnel
    #  Il part du haut du PC, passe au-dessus de la box et du nuage, et
    #  redescend sur le serveur VPN. Son apex se cale juste au-dessus de la
    #  plus haute des deux boîtes qu'il survole.
    vpn = MACHINES[3]["boite"]
    apex = min(pc_b[1], fai_b[1], cy - cr) - 42
    if apex < 150:
        raise SystemExit("le tunnel passerait à %d px, dans le sous-titre"
                         % apex)
    depart = ((pc_b[0] + pc_b[2]) / 2.0, pc_b[1])
    arrivee = (vpn[0] - 6, (vpn[1] + vpn[3]) / 2.0)
    pts = [depart, (depart[0], apex + 28), (depart[0] + 90, apex),
           (arrivee[0] - 150, apex), (arrivee[0] - 40, apex + 20),
           (arrivee[0], arrivee[1] - 40)]
    o.append(courbe("tunnel", pts, TUNNEL, 3, tirets=(10, 8)))
    o.append(fleche("tunnel", arrivee[0], arrivee[1] - 34,
                    arrivee[0], arrivee[1] - 4, TUNNEL, 3))
    mot = D.typo(TUNNEL_MOT)
    o.append(texte("tunnel", (depart[0] + 108, apex - 26), mot, "tunnel",
                   TUNNEL))
    if depart[0] + 108 + mesure.mesure(mot, fontes["tunnel"]) > L - MARGE:
        raise SystemExit("le libellé du tunnel déborde")

    #  -----------------------------------------------------------  le nuage
    o.append(disque("nuage", cx, cy, cr, teinte=INDIGO))
    o.append(texte("nuage", (cx, cy - 9), "Internet", "nuage", D.BLANC,
                   centre=True))

    #  ---------------------------------------------------------  les boîtes
    cadres, contenus, pastilles, numeros = [], [], [], []

    for m in MACHINES:
        x0, y0, x1, y1 = m["boite"]
        cadres.append(rect("boites", [x0, y0, x1, y1], 10, teinte=D.BLANC,
                           contour=D.FILET, epaisseur=2))

        y = y0 + 22
        gx = x0 + 22
        if "ecoute" in m:
            pastilles.append(disque("pastilles", gx + R_PASTILLE,
                                    y + 10, R_PASTILLE, teinte=PASTILLE))
            numeros.append(texte("numeros", (gx + R_PASTILLE, y + 1),
                                 str(m["ecoute"]), "numero", D.BLANC,
                                 centre=True))
            gx += 2 * R_PASTILLE + 14

        contenus.append(texte("contenus", (gx, y), m["nom"], "machine",
                              D.ENCRE))
        if "adresse" in m:
            contenus.append(texte("contenus", (x1 - 22, y + 5),
                                  m["adresse"], "adresse", INDIGO,
                                  droite=True))
            bout = gx + mesure.mesure(m["nom"], fontes["machine"]) + 24
            debut = x1 - 22 - mesure.mesure(m["adresse"], fontes["adresse"])
            if bout > debut:
                raise SystemExit("sur « %s », le nom et l'adresse se "
                                 "touchent" % m["nom"])
        y += 32
        for li in m["lignes"]:
            t = D.typo(li)
            if mesure.mesure(t, fontes["ligne"]) > x1 - x0 - 44:
                raise SystemExit("« %s » déborde de la boîte de « %s »"
                                 % (t, m["nom"]))
            contenus.append(texte("contenus", (x0 + 22, y), t, "ligne",
                                  D.GRIS))
            y += 24
        if y - 6 > y1:
            raise SystemExit("le contenu de « %s » descend à %d px pour une "
                             "boîte qui finit à %d" % (m["nom"], y - 6, y1))

    #  Le point 1, posé sur la ligne, avec un halo de papier pour que le
    #  câble ne le traverse pas.
    px, py = ECOUTE_LIGNE["xy"]
    pastilles.append(disque("pastilles", px, py, R_PASTILLE + 4,
                            teinte=D.PAPIER))
    pastilles.append(disque("pastilles", px, py, R_PASTILLE,
                            teinte=PASTILLE))
    numeros.append(texte("numeros", (px, py - 9),
                         str(ECOUTE_LIGNE["numero"]), "numero", D.BLANC,
                         centre=True))

    o.extend(cadres)
    o.extend(contenus)
    o.extend(pastilles)
    o.extend(numeros)

    #  ------------------------------------------------------  la légende
    legende, lnum = [], []
    legende.append(trait("legende", [MARGE, Y_BANDE, 856, Y_BANDE],
                         D.FILET, 1))
    legende.append(texte("legende", (MARGE, Y_BANDE + 12), D.typo(BANDE),
                         "bande", INDIGO, 1.4))
    y = Y_BANDE + 48
    for numero, propos in POINTS:
        legende.append(disque("legende", MARGE + R_PASTILLE, y + 9,
                              R_PASTILLE, teinte=PASTILLE))
        lnum.append(texte("legnum", (MARGE + R_PASTILLE, y), str(numero),
                          "numero", D.BLANC, centre=True))
        t = D.typo(propos)
        lnum.append(texte("legnum", (MARGE + 2 * R_PASTILLE + 16, y + 1), t,
                          "point", D.GRIS))
        if MARGE + 2 * R_PASTILLE + 16 + mesure.mesure(t, fontes["point"]) \
                > 880:
            raise SystemExit("« %s » mord sur la colonne de droite" % t)
        y += 38
    o.extend(legende)
    o.extend(lnum)

    bas = max(y + 10, MACHINES[-1]["boite"][3] + 40)
    note = D.typo(NOTE)
    if mesure.mesure(note, fontes["note"]) > L - 2 * MARGE - 140:
        raise SystemExit("la note déborde")
    o.append(texte("pied", (MARGE, bas), note, "note", D.FAIBLE))
    o.append(texte("pied", (L - MARGE, bas), SIGNATURE, "note", D.FAIBLE,
                   droite=True))

    H = int(bas + 54)
    o.insert(0, rect("fond", [0, 0, L, H], 0, teinte=D.PAPIER))
    return H, o, trouve


def rendre_matriciel(H, ordres, base):
    t = D.Toile(L, H)
    fontes = {k: t.police(f, taille) for k, (f, taille, _) in POLICES.items()}
    for a in ordres:
        if a["quoi"] == "rect":
            t.rrect(a["b"], a["r"], teinte=a["t"], contour=a["contour"],
                    epaisseur=a["e"])
        elif a["quoi"] == "trait":
            if a.get("tirets"):
                plein, vide = a["tirets"]
                x0, y0, x1, y1 = a["b"]
                t.pointilles([(x0, y0), (x1, y1)], a["t"], a["e"], plein,
                             vide)
            else:
                t.ligne(a["b"], a["t"], a["e"])
        elif a["quoi"] == "courbe":
            if a.get("tirets"):
                plein, vide = a["tirets"]
                t.pointilles(a["pts"], a["t"], a["e"], plein, vide)
            else:
                t.polyligne(a["pts"], a["t"], a["e"])
        elif a["quoi"] == "disque":
            t.disque(a["cx"], a["cy"], a["r"], teinte=a["t"],
                     contour=a["contour"], epaisseur=a["e"])
        elif a["quoi"] == "fleche":
            x0, y0, x1, y1 = a["b"]
            t.fleche(x0, y0, x1, y1, a["t"], a["e"])
        else:
            f = fontes[a["p"]]
            x, y = a["xy"]
            if a["centre"]:
                x -= t.mesure(a["c"], f) / 2.0
            elif a.get("droite"):
                x -= t.mesure(a["c"], f)
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
            tirets = ('" stroke-dasharray="%g %g'
                      % a["tirets"]) if a.get("tirets") else ""
            if a["quoi"] == "rect":
                x0, y0, x1, y1 = a["b"]
                bord = ('" stroke="%s" stroke-width="%g'
                        % (teinte(a["contour"]), a["e"])) if a["contour"] \
                    else ""
                out.append('    <rect x="%g" y="%g" width="%g" height="%g" '
                           'rx="%g" fill="%s%s"/>'
                           % (x0, y0, x1 - x0, y1 - y0, a["r"],
                              teinte(a["t"]) if a["t"] else "none", bord))
            elif a["quoi"] == "trait":
                x0, y0, x1, y1 = a["b"]
                out.append('    <line x1="%g" y1="%g" x2="%g" y2="%g" '
                           'stroke="%s" stroke-width="%g%s" '
                           'stroke-linecap="round"/>'
                           % (x0, y0, x1, y1, teinte(a["t"]), a["e"], tirets))
            elif a["quoi"] == "courbe":
                pts = " ".join("%g,%g" % p for p in a["pts"])
                out.append('    <polyline points="%s" fill="none" '
                           'stroke="%s" stroke-width="%g%s" '
                           'stroke-linecap="round" stroke-linejoin="round"/>'
                           % (pts, teinte(a["t"]), a["e"], tirets))
            elif a["quoi"] == "disque":
                bord = ('" stroke="%s" stroke-width="%g'
                        % (teinte(a["contour"]), a["e"])) if a["contour"] \
                    else ""
                out.append('    <circle cx="%g" cy="%g" r="%g" fill="%s%s"/>'
                           % (a["cx"], a["cy"], a["r"],
                              teinte(a["t"]) if a["t"] else "none", bord))
            elif a["quoi"] == "fleche":
                x0, y0, x1, y1 = a["b"]
                out.append('    <line x1="%g" y1="%g" x2="%g" y2="%g" '
                           'stroke="%s" stroke-width="%g"/>'
                           % (x0, y0, x1, y1 - 8, teinte(a["t"]), a["e"]))
                out.append('    <polygon points="%g,%g %g,%g %g,%g" '
                           'fill="%s"/>'
                           % (x1, y1, x1 - 6, y1 - 12, x1 + 6, y1 - 12,
                              teinte(a["t"])))
            else:
                _, taille, graisse = POLICES[a["p"]]
                espacement = (' letter-spacing="%g"' % a["tr"]
                              if a["tr"] else "")
                ancre = ""
                if a["centre"]:
                    ancre = ' text-anchor="middle"'
                elif a.get("droite"):
                    ancre = ' text-anchor="end"'
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
                        "vpn-ou-proxy-labo")
    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5),
               ("faible", D.FAIBLE, 3.0), ("indigo", INDIGO, 4.5),
               ("tunnel", TUNNEL, 4.5))
    for nom, fond in (("pastille", PASTILLE), ("nuage", INDIGO)):
        r = C.contraste(D.BLANC, fond)
        print("  blanc sur %-9s %-16s %.2f:1  %s"
              % (nom, str(fond), r, "ok" if r >= 4.5 else "INSUFFISANT"))
        if r < 4.5:
            raise SystemExit("blanc sur %s : %.2f:1" % (nom, r))

    H, ordres, trouve = composer()
    rendre_matriciel(H, ordres, base)
    couches, textes = rendre_svg(H, ordres, base)

    print()
    print("  %-38s %.0f Ko"
          % (os.path.basename(base + ".svg"),
             os.path.getsize(base + ".svg") / 1024.0))
    print("  %d x %d, %d calques, %d textes" % (L, H, couches, textes))
    print()
    for m in MACHINES:
        print("  %-20s %-16s%s"
              % (m["nom"], m.get("adresse", ""),
                 "   point d'écoute %d" % m["ecoute"] if "ecoute" in m
                 else ""))
    print()
    for quoi, n in trouve.items():
        print("  %-18s %d" % (quoi, n))


if __name__ == "__main__":
    principal()
