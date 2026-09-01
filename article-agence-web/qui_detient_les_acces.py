"""
Schéma de la question 3 — « Qui détient les accès ? »

    python3 article-agence-web/qui_detient_les_acces.py

Produit `article-agence-web/qui-detient-les-acces-site-web.webp` et son
équivalent PNG.

----------------------------------------------------------------------------
CE QU'IL A FALLU JETER POUR ARRIVER ICI
----------------------------------------------------------------------------
Trois essais, trois erreurs différentes, et chacune apprend quelque chose.

  - des cartes à coins arrondis avec des pastilles et un bandeau rouge : le
    gabarit qu'on voit partout, et un rouge d'alarme sur un paragraphe qui
    n'élève pas la voix ;
  - de la belle typographie : mieux composé, mais quatre lignes de texte mises
    en page restent du texte. On se demande pourquoi c'est une image ;
  - une photographie de clés rendue en 3D : une image, oui, mais plus un
    schéma. Le sujet n'est pas « des clés », c'est quatre accès nommés.

Ce qu'il fallait était entre les deux derniers : un SCHÉMA, avec des choses
DESSINÉES. Chaque accès a son pictogramme — une barre d'adresse, un serveur,
un écran d'administration, un graphique — et c'est le dessin qui porte le sens.
Le texte ne fait que nommer.

----------------------------------------------------------------------------
LA HIÉRARCHIE SANS COULEUR D'ALARME
----------------------------------------------------------------------------
Le domaine occupe le tiers gauche, seul, avec un pictogramme deux fois plus
grand et le seul trait violet de l'image. Un filet vertical le sépare des trois
autres, rangés côte à côte à droite, en gris.

Rien ne crie. On voit qu'un élément est traité autrement, et on comprend
pourquoi en lisant les quatre mots qui l'accompagnent.

----------------------------------------------------------------------------
POURQUOI TOUT EST DESSINÉ TROIS FOIS TROP GRAND
----------------------------------------------------------------------------
PIL ne lisse pas les formes : un cercle tracé directement à la taille finale
sort en escalier, et un schéma aux contours crénelés a l'air bâclé quoi qu'on
mette dedans. Tout est donc dessiné à trois fois la taille puis réduit en
Lanczos. C'est le seul moyen d'obtenir des arrondis propres, et ça ne coûte
qu'une seconde de calcul.
"""

import os

from PIL import Image, ImageDraw

import charte as C

RACINE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(RACINE, "qui-detient-les-acces-site-web")

L = 1600
MARGE = 88
ECHELLE = 3                      # dessin en 4800 px de large, puis réduction

PAPIER = (250, 249, 246)
ENCRE = (26, 27, 32)
GRIS = (100, 102, 112)
FAIBLE = (140, 141, 150)
FILET = (213, 211, 204)
VIOLET = (98, 44, 200)
VIOLET_PALE = (234, 227, 252)

SERIF_G = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"

SURTITRE = "QUESTION 3"
TITRE = "Qui détient les accès ?"

DOMAINE_NOM = "Le nom de domaine"
DOMAINE_TXT = ("À votre nom, dans votre compte, chez votre bureau "
               "d'enregistrement. Pas « géré par » l'agence.")
DOMAINE_VERDICT = "NE SE RÉCUPÈRE PAS"
ADRESSE = "votre-site.fr"

AUTRES = (
    ("serveur", "L'hébergement",
     "Y accéder et le résilier sans passer par un tiers."),
    ("admin", "L'administration du site",
     "Un compte administrateur à votre nom, pas un identifiant partagé."),
    ("mesure", "Les comptes Google",
     "Vous propriétaire, l'agence ajoutée comme utilisateur."),
)
VERDICT_AUTRES = "SE REPREND"


def typo(t):
    """L'apostrophe courbe : celle des livres, pas celle des claviers."""
    return t.replace("'", "’")


class Toile:
    """
    Un calque de dessin qui travaille en coordonnées finales.

    Tout ce qu'on lui demande est multiplié par l'échelle avant d'atteindre
    PIL. On raisonne donc sur l'image telle qu'elle sera lue, et le
    suréchantillonnage ne se voit nulle part dans le code de mise en page.
    """

    def __init__(self, l, h, echelle, fond):
        self.e = echelle
        self.im = Image.new("RGB", (l * echelle, h * echelle), fond)
        self.d = ImageDraw.Draw(self.im)

    def _b(self, b):
        return [v * self.e for v in b]

    def police(self, chemin, taille):
        return C.police(chemin, int(round(taille * self.e)))

    def mesure(self, texte, f):
        return self.d.textlength(texte, font=f) / self.e

    def texte(self, xy, t, f, teinte):
        self.d.text((xy[0] * self.e, xy[1] * self.e), t, font=f, fill=teinte)

    def ligne(self, b, teinte, epaisseur):
        self.d.line(self._b(b), fill=teinte, width=int(epaisseur * self.e))

    def rrect(self, b, rayon, teinte=None, contour=None, epaisseur=2):
        self.d.rounded_rectangle(self._b(b), radius=rayon * self.e,
                                 fill=teinte, outline=contour,
                                 width=int(epaisseur * self.e))

    def disque(self, cx, cy, r, teinte=None, contour=None, epaisseur=2):
        self.d.ellipse(self._b([cx - r, cy - r, cx + r, cy + r]),
                       fill=teinte, outline=contour,
                       width=int(epaisseur * self.e))

    def arc(self, cx, cy, r, a0, a1, teinte, epaisseur):
        self.d.arc(self._b([cx - r, cy - r, cx + r, cy + r]), a0, a1,
                   fill=teinte, width=int(epaisseur * self.e))

    def espace(self, xy, texte, f, teinte, tracking):
        """Des capitales lettre à lettre, avec de l'air entre elles."""
        x, y = xy
        for c in texte:
            self.texte((x, y), c, f, teinte)
            x += self.mesure(c, f) + tracking
        return x - tracking

    def largeur_espacee(self, texte, f, tracking):
        return sum(self.mesure(c, f) for c in texte) \
            + tracking * max(len(texte) - 1, 0)

    def final(self, l, h):
        return self.im.resize((l, h), Image.LANCZOS)


def couper(t, texte, f, largeur):
    ligne, lignes = "", []
    for m in texte.split():
        essai = (ligne + " " + m).strip()
        if t.mesure(essai, f) > largeur and ligne:
            lignes.append(ligne)
            ligne = m
        else:
            ligne = essai
    lignes.append(ligne)
    return lignes


# ---------------------------------------------------------------  pictogrammes

def cadenas(t, cx, cy, larg, teinte, plein):
    """Un cadenas : le corps, et l'anse au-dessus."""
    h = larg * 0.76
    t.rrect([cx - larg / 2, cy - h * 0.12, cx + larg / 2, cy + h * 0.88],
            larg * 0.16, teinte=teinte if plein else None,
            contour=None if plein else teinte, epaisseur=1.6)
    t.arc(cx, cy - h * 0.12, larg * 0.31, 180, 360, teinte, 1.8)
    if plein:
        t.disque(cx, cy + h * 0.34, larg * 0.10, teinte=PAPIER)


def picto_adresse(t, x0, y0, larg, haut):
    """
    La barre d'adresse d'un navigateur.

    C'est le seul pictogramme qui montre un NOM plutôt qu'un objet, et c'est
    voulu : un nom de domaine n'est pas une machine, c'est une inscription à un
    registre. Le cadenas plein rappelle à qui elle appartient.
    """
    r = haut / 2
    t.rrect([x0, y0, x0 + larg, y0 + haut], r, teinte=(255, 255, 255),
            contour=VIOLET, epaisseur=2.4)
    cy = y0 + haut / 2
    cadenas(t, x0 + haut * 0.56, cy, haut * 0.34, VIOLET, True)
    return x0 + haut * 0.56 + haut * 0.34, cy


def picto_serveur(t, x0, y0, larg, haut):
    """Trois baies empilées : l'image qu'on se fait d'un hébergement."""
    n, ecart = 3, 10
    hb = (haut - ecart * (n - 1)) / n
    for i in range(n):
        y = y0 + i * (hb + ecart)
        t.rrect([x0, y, x0 + larg, y + hb], 5, contour=GRIS, epaisseur=1.8)
        for j in range(2):
            t.disque(x0 + 16 + j * 14, y + hb / 2, 3.2, teinte=GRIS)
        t.ligne([x0 + larg - 62, y + hb / 2, x0 + larg - 18, y + hb / 2],
                FILET, 2.4)


def picto_admin(t, x0, y0, larg, haut):
    """Une fenêtre d'administration : barre de titre, colonne, contenu."""
    t.rrect([x0, y0, x0 + larg, y0 + haut], 7, contour=GRIS, epaisseur=1.8)
    t.ligne([x0, y0 + 26, x0 + larg, y0 + 26], GRIS, 1.6)
    for j in range(3):
        t.disque(x0 + 15 + j * 13, y0 + 13, 3.0, teinte=FAIBLE)
    #  La colonne de gauche : c'est elle qui fait reconnaître un back-office
    #  plutôt qu'une page web quelconque.
    t.ligne([x0 + 58, y0 + 26, x0 + 58, y0 + haut], GRIS, 1.6)
    for j in range(4):
        t.ligne([x0 + 14, y0 + 46 + j * 17, x0 + 44, y0 + 46 + j * 17],
                FILET, 2.6)
    for j, w in enumerate((0.72, 0.52, 0.62)):
        t.ligne([x0 + 74, y0 + 50 + j * 22,
                 x0 + 74 + (larg - 92) * w, y0 + 50 + j * 22], FILET, 3.0)


def picto_mesure(t, x0, y0, larg, haut):
    """Des barres et une loupe : l'audience, et de quoi la regarder."""
    base = y0 + haut
    for i, hb in enumerate((0.34, 0.58, 0.82)):
        x = x0 + 12 + i * 34
        t.rrect([x, base - haut * hb, x + 22, base], 3, teinte=(228, 229, 234))
        t.rrect([x, base - haut * hb, x + 22, base], 3, contour=GRIS,
                epaisseur=1.8)
    cx, cy, r = x0 + larg - 46, y0 + 40, 27
    t.disque(cx, cy, r, teinte=PAPIER, contour=GRIS, epaisseur=2.4)
    t.ligne([cx + r * 0.72, cy + r * 0.72, cx + r * 1.5, cy + r * 1.5],
            GRIS, 3.2)


PICTOS = {"serveur": picto_serveur, "admin": picto_admin,
          "mesure": picto_mesure}


# --------------------------------------------------------------------  montage

def principal():
    for nom, teinte, seuil in (("encre", ENCRE, 4.5), ("gris", GRIS, 4.5),
                               ("faible", FAIBLE, 3.0),
                               ("violet", VIOLET, 4.5)):
        r = C.contraste(teinte, PAPIER)
        print("  %-8s %-16s %.2f:1  %s"
              % (nom, str(teinte), r, "ok" if r >= seuil else "INSUFFISANT"))
        if r < seuil:
            raise SystemExit("%s : %.2f:1, sous le seuil" % (nom, r))

    mesure = Toile(10, 10, ECHELLE, PAPIER)

    f_sur = mesure.police(C.POLICE_G, 15)
    f_titre = mesure.police(SERIF, 52)
    f_nom_d = mesure.police(SERIF_G, 34)
    f_txt_d = mesure.police(C.POLICE_R, 20)
    f_adr = mesure.police(C.POLICE_R, 25)
    f_verd_d = mesure.police(C.POLICE_G, 15)
    f_nom = mesure.police(SERIF_G, 22)
    f_txt = mesure.police(C.POLICE_R, 17)
    f_verd = mesure.police(C.POLICE_G, 13)

    # ------------------------------------------------------------  la trame
    x_sep = 618
    x_col = 674
    col = (L - MARGE - x_col - 2 * 46) // 3
    gauche = x_sep - 52 - MARGE

    dom_lignes = couper(mesure, typo(DOMAINE_TXT), f_txt_d, gauche)
    plies = [couper(mesure, typo(t), f_txt, col) for _, _, t in AUTRES]
    noms = [couper(mesure, typo(n), f_nom, col) for _, n, _ in AUTRES]
    trop = [n for n, p in zip(noms, noms) if len(p) > 2]
    if trop:
        raise SystemExit("un intitulé tient sur plus de deux lignes : %s"
                         % trop)

    y_picto = 262
    h_picto = 128
    y_nom = y_picto + h_picto + 44
    y_txt_d = y_nom + 50
    y_verd_d = y_txt_d + len(dom_lignes) * 27 + 26

    y_nom_c = y_picto + h_picto + 40
    y_txt_c = y_nom_c + max(len(n) for n in noms) * 28 + 12
    y_verd_c = y_txt_c + max(len(p) for p in plies) * 24 + 22

    bas = max(y_verd_d + 24, y_verd_c + 22)
    H = bas + MARGE

    t = Toile(L, H, ECHELLE, PAPIER)

    # ------------------------------------------------------------  l'en-tête
    t.espace((MARGE, 72), SURTITRE, f_sur, VIOLET, 2.6)
    t.texte((MARGE - 3, 100), typo(TITRE), f_titre, ENCRE)
    t.ligne([MARGE, 206, L - MARGE, 206], FILET, 1)

    # ---------------------------------------------------------  le domaine
    xa, _ = picto_adresse(t, MARGE, y_picto + 22, gauche - 30, 84)
    t.texte((xa + 26, y_picto + 22 + 26), ADRESSE, f_adr, ENCRE)

    t.texte((MARGE, y_nom), typo(DOMAINE_NOM), f_nom_d, ENCRE)
    y = y_txt_d
    for ligne in dom_lignes:
        t.texte((MARGE, y), ligne, f_txt_d, GRIS)
        y += 27
    t.ligne([MARGE, y_verd_d - 14, MARGE + 44, y_verd_d - 14], VIOLET, 2)
    t.espace((MARGE, y_verd_d), DOMAINE_VERDICT, f_verd_d, VIOLET, 2.4)

    #  Le filet vertical : la seule séparation de l'image, et elle suffit.
    t.ligne([x_sep, y_picto - 18, x_sep, bas - 6], FILET, 1)

    # -----------------------------------------------------------  les trois
    for i, ((cle, nom, _), lignes, nom_lignes) in enumerate(
            zip(AUTRES, plies, noms)):
        x0 = x_col + i * (col + 46)
        PICTOS[cle](t, x0, y_picto, col - 26, h_picto)

        y = y_nom_c
        for ligne in nom_lignes:
            t.texte((x0, y), ligne, f_nom, ENCRE)
            y += 28
        y = y_txt_c
        for ligne in lignes:
            t.texte((x0, y), ligne, f_txt, GRIS)
            y += 24
        t.ligne([x0, y_verd_c - 12, x0 + 30, y_verd_c - 12], FILET, 2)
        t.espace((x0, y_verd_c), VERDICT_AUTRES, f_verd, FAIBLE, 2.2)

    out = t.final(L, H)
    out.save(BASE + ".webp", "WEBP", quality=C.QUALITE, method=6)
    out.save(BASE + ".png", "PNG", optimize=True)
    print()
    print("  %d × %d  (dessiné à %d × %d)" % (L, H, L * ECHELLE, H * ECHELLE))
    for e in (".webp", ".png"):
        print("  %-44s %.0f Ko" % (os.path.basename(BASE + e),
                                   os.path.getsize(BASE + e) / 1024))


if __name__ == "__main__":
    principal()
