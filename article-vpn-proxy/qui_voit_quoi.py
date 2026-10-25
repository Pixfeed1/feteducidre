"""
Qui voit quoi : proxy ou VPN, mesuré en labo.

    python3 article-vpn-proxy/qui_voit_quoi.py

Produit `vpn-ou-proxy-qui-voit-quoi.webp`, son PNG et le SVG éditable.

----------------------------------------------------------------------------
ICI, LE ROUGE ET LE VERT SONT DANS LEUR RÔLE
----------------------------------------------------------------------------
La charte les réserve aux figures qui opposent un état sain à un état
dégradé. Celle-ci ne fait que ça : « visible » veut dire que l'observateur
l'apprend, « caché » qu'il ne voit que l'intermédiaire, ou rien. C'est
tout le contenu de la grille, et l'article s'écrit autour.

La version d'origine mettait l'orange sur « visible » et le bleu sur
« caché ». Mêmes rôles, teintes de la charte : alerte et vert, avec le
blanc dessus à 6,43:1 et 5,18:1.

----------------------------------------------------------------------------
PAS DE PAVÉS DE COULEUR DERRIÈRE CHAQUE CASE
----------------------------------------------------------------------------
Quarante cases sur fond teinté font un tableur. La pastille porte déjà
la couleur, et il en faut peu : le mot et sa précision se lisent sur le
papier. Les sections sont séparées par un filet, pas par des bordures.

----------------------------------------------------------------------------
LE « SANS OBJET » N'EST PAS UN TROU
----------------------------------------------------------------------------
Quatre cases ne disent ni visible ni caché : sans proxy ni VPN, il n'y a
pas d'intermédiaire pour voir quoi que ce soit, ni d'en-tête ajouté. Un
contrôle vérifie que ces quatre-là sont toutes dans la colonne « sans
protection », et nulle part ailleurs : un sans objet qui apparaîtrait
dans une colonne protégée serait une mesure manquante déguisée.
"""

import os

import charte as C
import dessin as D

L = 1600
MARGE = 56

INDIGO = C.VIOLET_TEXTE
VISIBLE = C.ALERTE
CACHE = C.VERT

MODES = ("Sans protection", "Proxy HTTP", "Proxy HTTPS", "Proxy SOCKS5",
         "VPN WireGuard")

#  ---------------------------------------------------------------------------
#  LA GRILLE
#
#  Chaque case vaut (état, mot, précision). L'état est "v" pour visible,
#  "c" pour caché, "n" pour sans objet. `note` renvoie à l'écart Firefox
#  du même numéro.
#  ---------------------------------------------------------------------------
V, Ca, N = "v", "c", "n"

SECTIONS = (
    {"nom": "TON FAI (ta ligne et son résolveur DNS)", "lignes": (
        {"quoi": "Le nom des sites visités", "cases": (
            (V, "Voit", "DNS et SNI"),
            (V, "Voit", "CONNECT et SNI"),
            (Ca, "Le proxy seul", "nom et IP du proxy", 1),
            (V, "Voit", "requête SOCKS et SNI"),
            (Ca, "Le VPN seul", "IP du serveur VPN"))},
        {"quoi": "Le contenu des pages HTTP", "cases": (
            (V, "Lit", "la page en clair"),
            (V, "Lit", "la page en clair"),
            (Ca, "Ne lit pas", "lien chiffré"),
            (V, "Lit", "la page en clair"),
            (Ca, "Ne lit pas", "tunnel chiffré"))},
    )},
    {"nom": "LE SITE VISITÉ", "lignes": (
        {"quoi": "Ta vraie IP, par la connexion", "cases": (
            (V, "Voit", ""),
            (Ca, "IP du proxy", ""),
            (Ca, "IP du proxy", ""),
            (Ca, "IP du proxy", ""),
            (Ca, "IP du VPN", ""))},
        {"quoi": "Ta vraie IP, par WebRTC", "cases": (
            (V, "Voit", ""),
            (V, "Voit", "STUN hors du proxy"),
            (V, "Voit", "STUN hors du proxy"),
            (V, "Voit", "STUN hors du proxy", 2),
            (Ca, "IP du VPN", ""))},
        {"quoi": "Ta vraie IP, dans un en-tête (page HTTP)", "cases": (
            (N, "", ""),
            (V, "Voit", "X-Forwarded-For"),
            (V, "Voit", "X-Forwarded-For"),
            (Ca, "Non", ""),
            (Ca, "Non", ""))},
    )},
    {"nom": "L’INTERMÉDIAIRE (proxy ou serveur VPN)", "lignes": (
        {"quoi": "Ta vraie IP", "cases": (
            (N, "", ""),
            (V, "Voit", ""),
            (V, "Voit", ""),
            (V, "Voit", ""),
            (V, "Voit", ""))},
        {"quoi": "Le nom des sites visités", "cases": (
            (N, "", ""),
            (V, "Voit", "CONNECT et SNI"),
            (V, "Voit", "CONNECT et SNI"),
            (V, "Voit", "requête SOCKS et SNI"),
            (V, "Voit", "DNS et SNI"))},
        {"quoi": "Le contenu des pages HTTP", "cases": (
            (N, "", ""),
            (V, "Lit", "la page en clair"),
            (V, "Lit", "la page en clair"),
            (V, "Lit", "la page en clair"),
            (V, "Lit", "la page en clair"))},
    )},
)

HTTPS = ("Le contenu des pages HTTPS : ni le FAI ni l’intermédiaire ne l’ont "
         "lu, quel que soit le mode ou le navigateur (aucune trace dans nos "
         "75 captures).")
ECARTS = (
    (1, "Proxy HTTPS réglé par fichier PAC : le résolveur de ton FAI a quand "
        "même reçu une question DNS sur le site."),
    (2, "Proxy SOCKS5 : aucune requête STUN, donc pas de fuite WebRTC."),
)
ECARTS_CHAPEAU = "Firefox 158 : mêmes cases, sauf deux."

POLICES = {
    "titre": (C.POLICE_G, 19, "bold"),
    "sous": (C.POLICE_R, 17, "normal"),
    "legende": (C.POLICE_R, 15, "normal"),
    "mode": (C.POLICE_G, 16, "bold"),
    "section": (C.POLICE_G, 13, "bold"),
    "quoi": (C.POLICE_R, 16, "normal"),
    "mot": (C.POLICE_G, 15, "bold"),
    "precision": (C.POLICE_R, 12, "normal"),
    "renvoi": (C.POLICE_G, 11, "bold"),
    "ecart": (C.POLICE_R, 15, "normal"),
    "note": (C.POLICE_R, 13, "normal"),
}
FAMILLE_SVG = "Liberation Sans, Arial, Helvetica, sans-serif"

TITRE = "QUI VOIT QUOI : PROXY OU VPN, MESURÉ EN LABO"
SOUS = ("ce que ton FAI, le site et l’intermédiaire ont appris avec Chromium "
        "153 ; Chromium 141, plus vieux d’un an, donne la même grille")
NOTE = ("Source : labo jurojin.net du 25 octobre 2026. Chromium 153 et 141, "
        "Firefox 158.0.1, Squid 6.14 et Dante 1.4.3 en réglages d’usine, "
        "WireGuard. Captures tcpdump lues avec tshark 4.2.")
SIGNATURE = "jurojin.net"

Y_LEGENDE = 112
Y_MODES = 164
X_QUOI = MARGE
X_COL = 466
PAS_COL = 216
H_LIGNE = 50
H_SECTION = 34
R_PAST = 10
R_RENVOI = 9


def rect(couche, b, r, teinte=None, contour=None, epaisseur=2):
    return {"quoi": "rect", "couche": couche, "b": b, "r": r, "t": teinte,
            "contour": contour, "e": epaisseur}


def trait(couche, b, teinte, epaisseur):
    return {"quoi": "trait", "couche": couche, "b": b, "t": teinte,
            "e": epaisseur}


def polyligne(couche, points, teinte, epaisseur):
    return {"quoi": "polyligne", "couche": couche, "pts": points,
            "t": teinte, "e": epaisseur}


def disque(couche, cx, cy, r, teinte=None, contour=None, epaisseur=2):
    return {"quoi": "disque", "couche": couche, "cx": cx, "cy": cy, "r": r,
            "t": teinte, "contour": contour, "e": epaisseur}


def texte(couche, xy, contenu, police, teinte, tracking=0.0, centre=False,
          droite=False):
    for c, nom in (("—", "cadratin"), ("–", "demi-cadratin")):
        if c in contenu:
            raise SystemExit("%s dans « %s »" % (nom, contenu[:60]))
    return {"quoi": "texte", "couche": couche, "xy": xy, "c": contenu,
            "p": police, "t": teinte, "tr": tracking, "centre": centre,
            "droite": droite}


def pastille(couche, cx, cy, etat):
    """Point d'exclamation blanc quand c'est visible, coche quand c'est caché."""
    if etat == V:
        return [disque(couche, cx, cy, R_PAST, teinte=VISIBLE),
                rect(couche, [cx - 1.6, cy - 6, cx + 1.6, cy + 1.5], 1.2,
                     teinte=D.BLANC),
                disque(couche, cx, cy + 4.6, 1.8, teinte=D.BLANC)]
    return [disque(couche, cx, cy, R_PAST, teinte=CACHE),
            polyligne(couche, [(cx - 4.8, cy + 0.2), (cx - 1.4, cy + 3.6),
                               (cx + 5.0, cy - 3.4)], D.BLANC, 2.6)]


def composer():
    mesure = D.Toile(L, 10)
    fontes = {k: mesure.police(f, t) for k, (f, t, _) in POLICES.items()}

    lignes = [li for s in SECTIONS for li in s["lignes"]]

    #  ------------------------------------------------------------------
    #  CONTRÔLES
    #  ------------------------------------------------------------------
    for li in lignes:
        if len(li["cases"]) != len(MODES):
            raise SystemExit("« %s » donne %d cases pour %d modes"
                             % (li["quoi"], len(li["cases"]), len(MODES)))
        for c in li["cases"]:
            if c[0] not in (V, Ca, N):
                raise SystemExit("état inconnu « %s » sur « %s »"
                                 % (c[0], li["quoi"]))
            if c[0] == N and (c[1] or c[2]):
                raise SystemExit("une case sans objet de « %s » porte quand "
                                 "même un libellé" % li["quoi"])
            if c[0] != N and not c[1]:
                raise SystemExit("une case de « %s » n'a pas de mot"
                                 % li["quoi"])

    #  Un « sans objet » ne peut exister que faute d'intermédiaire, donc
    #  seulement dans la première colonne. Ailleurs, ce serait une mesure
    #  manquante déguisée en case vide.
    hors = [(li["quoi"], MODES[j]) for li in lignes
            for j, c in enumerate(li["cases"]) if c[0] == N and j != 0]
    if hors:
        raise SystemExit("des cases sans objet hors de la colonne « %s » : %s"
                         % (MODES[0], hors))

    #  Les renvois du bas doivent pointer sur des cases qui existent.
    poses = sorted(c[3] for li in lignes for c in li["cases"] if len(c) > 3)
    if poses != [n for n, _ in ECARTS]:
        raise SystemExit("les renvois posés dans la grille sont %s et les "
                         "écarts décrits sont %s"
                         % (poses, [n for n, _ in ECARTS]))

    compte = {V: 0, Ca: 0, N: 0}
    for li in lignes:
        for c in li["cases"]:
            compte[c[0]] += 1
    if sum(compte.values()) != len(lignes) * len(MODES):
        raise SystemExit("la grille n'est pas complète")

    o = []
    o.append(texte("titre", (MARGE, 46), D.typo(TITRE), "titre", D.ENCRE,
                   2.2))
    sous = D.typo(SOUS)
    if mesure.mesure(sous, fontes["sous"]) > L - 2 * MARGE:
        raise SystemExit("le sous-titre déborde")
    o.append(texte("titre", (MARGE, 74), sous, "sous", D.FAIBLE))

    #  -----------------------------------------------------------  légende
    leg, legt = [], []
    x = MARGE
    for etat, gras, suite in (
            (V, "Visible", " : l’observateur l’apprend"),
            (Ca, "Caché", " : il ne voit que l’intermédiaire, ou rien")):
        leg.extend(pastille("legende", x + R_PAST, Y_LEGENDE + 8, etat))
        legt.append(texte("legt", (x + 2 * R_PAST + 12, Y_LEGENDE), gras,
                          "mode", D.ENCRE))
        gx = x + 2 * R_PAST + 12 + mesure.mesure(gras, fontes["mode"])
        legt.append(texte("legt", (gx, Y_LEGENDE + 1), D.typo(suite),
                          "legende", D.GRIS))
        x = gx + mesure.mesure(D.typo(suite), fontes["legende"]) + 48
    legt.append(texte("legt", (x, Y_LEGENDE), "sans objet", "mode", D.FAIBLE))
    gx = x + mesure.mesure("sans objet", fontes["mode"])
    legt.append(texte("legt", (gx, Y_LEGENDE + 1),
                      D.typo(" : pas d’intermédiaire"), "legende", D.FAIBLE))
    if gx + mesure.mesure(D.typo(" : pas d’intermédiaire"),
                          fontes["legende"]) > L - MARGE:
        raise SystemExit("la légende déborde")
    o.extend(leg)
    o.extend(legt)

    #  -------------------------------------------------------  les colonnes
    largeur_col = PAS_COL - 16
    for j, m in enumerate(MODES):
        if mesure.mesure(m, fontes["mode"]) > largeur_col:
            raise SystemExit("« %s » déborde de sa colonne" % m)
        o.append(texte("modes", (X_COL + j * PAS_COL + largeur_col / 2.0,
                                 Y_MODES), m, "mode", D.ENCRE, centre=True))
    if X_COL + (len(MODES) - 1) * PAS_COL + largeur_col > L - MARGE:
        raise SystemExit("la dernière colonne sort du cadre")

    filets, quoi, pasts, mots, renvois = [], [], [], [], []
    y = Y_MODES + 26
    filets.append(trait("filets", [MARGE, y, L - MARGE, y], D.FILET, 2))

    for s in SECTIONS:
        y += 16
        filets.append(texte("filets", (MARGE, y), D.typo(s["nom"]),
                            "section", INDIGO, 1.2))
        y += H_SECTION

        for li in s["lignes"]:
            t = D.typo(li["quoi"])
            if mesure.mesure(t, fontes["quoi"]) > X_COL - X_QUOI - 24:
                raise SystemExit("« %s » mord sur la première colonne" % t)
            quoi.append(texte("quoi", (X_QUOI + 18, y + 10), t, "quoi",
                              D.GRIS))

            for j, c in enumerate(li["cases"]):
                cx = X_COL + j * PAS_COL
                if c[0] == N:
                    mots.append(texte("mots", (cx + 2, y + 8), "sans objet",
                                      "precision", D.FAIBLE))
                    continue
                pasts.extend(pastille("pastilles", cx + R_PAST, y + 16,
                                      c[0]))
                tx = cx + 2 * R_PAST + 12
                deux = bool(c[2])
                mots.append(texte("mots", (tx, y + (6 if deux else 16)),
                                  D.typo(c[1]), "mot", D.ENCRE))
                if deux:
                    p = D.typo(c[2])
                    mots.append(texte("mots", (tx, y + 26), p, "precision",
                                      D.GRIS))
                    if tx + mesure.mesure(p, fontes["precision"]) \
                            > cx + largeur_col + 6:
                        raise SystemExit("« %s » déborde de sa colonne" % p)
                if len(c) > 3:
                    rx = (tx + mesure.mesure(D.typo(c[1]), fontes["mot"])
                          + 12 + R_RENVOI)
                    if rx + R_RENVOI > cx + largeur_col:
                        raise SystemExit("le renvoi %d déborde de sa case"
                                         % c[3])
                    ry = y + (6 if deux else 16)
                    renvois.append(disque("renvois", rx, ry + 8, R_RENVOI,
                                          teinte=D.PAPIER, contour=INDIGO,
                                          epaisseur=1.5))
                    renvois.append(texte("renvois", (rx, ry + 1), str(c[3]),
                                         "renvoi", INDIGO, centre=True))
            y += H_LIGNE

        y += 4
        filets.append(trait("filets", [MARGE, y, L - MARGE, y], D.FILET, 1))

    o.extend(filets)
    o.extend(quoi)
    o.extend(pasts)
    o.extend(mots)
    o.extend(renvois)

    #  -------------------------------------------------------  les trois pieds
    bas = []
    y += 22
    bas.extend(pastille("pied", MARGE + R_PAST, y + 8, Ca))
    h = D.typo("Le contenu des pages HTTPS")
    bas.append(texte("pied", (MARGE + 2 * R_PAST + 12, y), h, "mode",
                     D.ENCRE))
    gx = MARGE + 2 * R_PAST + 12 + mesure.mesure(h, fontes["mode"])
    suite = D.typo(HTTPS[len(h):])
    bas.append(texte("pied", (gx, y + 1), suite, "ecart", D.GRIS))
    if gx + mesure.mesure(suite, fontes["ecart"]) > L - MARGE:
        raise SystemExit("la ligne sur le HTTPS déborde")

    y += 40
    bas.append(texte("pied", (MARGE, y), D.typo(ECARTS_CHAPEAU), "mode",
                     D.ENCRE))
    y += 26
    for numero, propos in ECARTS:
        bas.append(disque("pied", MARGE + R_RENVOI, y + 8, R_RENVOI,
                          teinte=D.PAPIER, contour=INDIGO, epaisseur=1.5))
        bas.append(texte("pied", (MARGE + R_RENVOI, y + 1), str(numero),
                         "renvoi", INDIGO, centre=True))
        p = D.typo(propos)
        bas.append(texte("pied", (MARGE + 2 * R_RENVOI + 14, y), p, "ecart",
                         D.GRIS))
        if MARGE + 2 * R_RENVOI + 14 + mesure.mesure(p, fontes["ecart"]) \
                > L - MARGE:
            raise SystemExit("« %s » déborde" % p)
        y += 28
    o.extend(bas)

    y += 24
    note = D.typo(NOTE)
    if mesure.mesure(note, fontes["note"]) > L - 2 * MARGE - 130:
        raise SystemExit("la source déborde")
    o.append(texte("source", (MARGE, y), note, "note", D.FAIBLE))
    o.append(texte("source", (L - MARGE, y), SIGNATURE, "note", D.FAIBLE,
                   droite=True))

    H = int(y + 54)
    o.insert(0, rect("fond", [0, 0, L, H], 0, teinte=D.PAPIER))
    return H, o, compte


def rendre_matriciel(H, ordres, base):
    t = D.Toile(L, H)
    fontes = {k: t.police(f, taille) for k, (f, taille, _) in POLICES.items()}
    for a in ordres:
        if a["quoi"] == "rect":
            t.rrect(a["b"], a["r"], teinte=a["t"], contour=a["contour"],
                    epaisseur=a["e"])
        elif a["quoi"] == "trait":
            t.ligne(a["b"], a["t"], a["e"])
        elif a["quoi"] == "polyligne":
            t.polyligne(a["pts"], a["t"], a["e"])
        elif a["quoi"] == "disque":
            t.disque(a["cx"], a["cy"], a["r"], teinte=a["t"],
                     contour=a["contour"], epaisseur=a["e"])
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
                           'stroke="%s" stroke-width="%g"/>'
                           % (x0, y0, x1, y1, teinte(a["t"]), a["e"]))
            elif a["quoi"] == "polyligne":
                pts = " ".join("%g,%g" % p for p in a["pts"])
                out.append('    <polyline points="%s" fill="none" '
                           'stroke="%s" stroke-width="%g" '
                           'stroke-linecap="round" stroke-linejoin="round"/>'
                           % (pts, teinte(a["t"]), a["e"]))
            elif a["quoi"] == "disque":
                bord = ('" stroke="%s" stroke-width="%g'
                        % (teinte(a["contour"]), a["e"])) if a["contour"] \
                    else ""
                out.append('    <circle cx="%g" cy="%g" r="%g" fill="%s%s"/>'
                           % (a["cx"], a["cy"], a["r"],
                              teinte(a["t"]) if a["t"] else "none", bord))
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
                        "vpn-ou-proxy-qui-voit-quoi")
    D.verifier(("encre", D.ENCRE, 4.5), ("gris", D.GRIS, 4.5),
               ("faible", D.FAIBLE, 3.0), ("indigo", INDIGO, 4.5),
               ("visible", VISIBLE, 4.5), ("caché", CACHE, 4.5))
    for nom, fond in (("visible", VISIBLE), ("caché", CACHE)):
        r = C.contraste(D.BLANC, fond)
        print("  blanc sur %-8s %-16s %.2f:1  %s"
              % (nom, str(fond), r, "ok" if r >= 4.5 else "INSUFFISANT"))
        if r < 4.5:
            raise SystemExit("blanc sur %s : %.2f:1" % (nom, r))

    H, ordres, compte = composer()
    rendre_matriciel(H, ordres, base)
    couches, textes = rendre_svg(H, ordres, base)

    print()
    print("  %-38s %.0f Ko"
          % (os.path.basename(base + ".svg"),
             os.path.getsize(base + ".svg") / 1024.0))
    print("  %d x %d, %d calques, %d textes" % (L, H, couches, textes))
    print()
    for s in SECTIONS:
        print("  %s" % s["nom"])
        for li in s["lignes"]:
            print("    %-42s %s"
                  % (li["quoi"],
                     "  ".join("%-4s" % {V: "vu", Ca: "caché",
                                         N: "."}[c[0]]
                               for c in li["cases"])))
    print()
    print("  visible %d, caché %d, sans objet %d, total %d"
          % (compte[V], compte[Ca], compte[N], sum(compte.values())))


if __name__ == "__main__":
    principal()
