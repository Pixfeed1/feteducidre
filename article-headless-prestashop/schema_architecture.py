"""
IMAGE 2 de l'article « PrestaShop headless avec Next.js » — le schéma clé.

    python3 article-headless-prestashop/schema_architecture.py

Produit `article-headless-prestashop/schema-architecture-headless-prestashop-nextjs.webp`.

----------------------------------------------------------------------------
TROIS BLOCS, ET UNE BOUCLE
----------------------------------------------------------------------------
Le brief donne la chaîne : PrestaShop → API → Next.js → Visiteur. Elle est
juste, mais elle s'arrête au milieu de l'histoire — elle ne dit que l'aller.
Un lecteur qui la suit jusqu'au bout arrive chez le visiteur et se demande où
part son panier, puisque le seul trait du schéma pointe dans l'autre sens.

D'où la voie de retour sous les trois blocs. Elle referme la boucle et répond
à la question avant qu'elle ne se pose : la commande repart jusqu'au moteur,
qui reste le seul endroit où elle existe.

----------------------------------------------------------------------------
CE QUE CHAQUE BLOC ANNONCE, ET CE QU'IL N'ANNONCE PAS
----------------------------------------------------------------------------
Le bloc de droite ne dit pas « pages pré-rendues ». C'est un mode possible
parmi d'autres — un front Next.js peut aussi bien interroger l'API à la
demande, ou dans le navigateur. Écrire une seule de ces trois façons sur un
schéma d'architecture, c'est apprendre au lecteur une règle qui n'en est pas
une. Le bloc dit donc ce qui est vrai dans tous les cas : il fabrique les
pages.

De même, aucun logo n'est redessiné. Les noms suffisent, et un logo
approximatif se remarque immédiatement dans un article technique.

----------------------------------------------------------------------------
LA PHRASE DU BAS EST LA DÉFINITION
----------------------------------------------------------------------------
Tout le schéma tient dans une seule phrase, et elle est écrite en toutes
lettres sous les blocs plutôt que laissée à la légende : PrestaShop ne
fabrique plus aucune page. Si le lecteur ne retient que ça, il a compris ce
que « headless » veut dire.
"""

import os

from PIL import Image, ImageDraw

import charte as C

RACINE = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(
    RACINE, "schema-architecture-headless-prestashop-nextjs.webp")

L, H = 1600, 652
MARGE = 60
BLOC_L = 380
BLOC_H = 286
Y0 = 132
#  380 × 3 + 170 × 2 = 1480, soit exactement la largeur utile. L'écart entre
#  blocs n'est pas un reste : c'est lui qui doit loger la pastille et son
#  sous-titre, et il était trop étroit à 140.
ECART = 170                      # entre deux blocs

VISITEUR = (64, 76, 98)


def police_qui_tient(texte, largeur, tailles=(17, 16, 15, 14, 13, 12)):
    """
    La plus grande taille à laquelle ce texte tient dans cette largeur.

    Les sous-titres des flèches vivent dans l'écart entre deux blocs. Fixer
    leur corps une fois pour toutes revient à parier que personne ne
    rallongera jamais un libellé — et le jour où ça arrive, le texte passe
    sous les blocs voisins sans que rien ne le signale.
    """
    from PIL import ImageDraw, Image as _I
    d = ImageDraw.Draw(_I.new("RGB", (1, 1)))
    for t in tailles:
        f = C.police(C.POLICE_R, t)
        if d.textlength(texte, font=f) <= largeur:
            return f
    return C.police(C.POLICE_R, tailles[-1])


def fleche_h(d, x0, x1, y, couleur, largeur=3, pointe=15):
    """Une flèche horizontale. `x1 > x0` va vers la droite, sinon la gauche."""
    sens = 1 if x1 > x0 else -1
    d.line([x0, y, x1, y], fill=couleur, width=largeur)
    d.polygon([(x1, y), (x1 - sens * pointe, y - 8),
               (x1 - sens * pointe, y + 8)], fill=couleur)


def moteur(d, cx, cy, teinte):
    """Un empilement de galettes : la figure convenue d'un entrepôt de
    données. Trois disques suffisent à la faire reconnaître."""
    for i in range(3):
        yy = cy - 22 + i * 20
        d.ellipse([cx - 30, yy, cx + 30, yy + 22], fill=C.CARTE,
                  outline=teinte, width=3)


def fenetre(d, cx, cy, teinte):
    """Une fenêtre de navigateur : la vitrine."""
    x0, y0 = cx - 36, cy - 28
    d.rounded_rectangle([x0, y0, x0 + 72, y0 + 56], radius=7,
                        fill=C.CARTE, outline=teinte, width=3)
    d.line([x0, y0 + 17, x0 + 72, y0 + 17], fill=teinte, width=3)
    for i in range(3):
        d.ellipse([x0 + 8 + i * 11, y0 + 5, x0 + 15 + i * 11, y0 + 12],
                  fill=teinte)


def personne(d, cx, cy, teinte):
    """Le visiteur. Une tête et des épaules — le reste n'apporte rien."""
    d.ellipse([cx - 14, cy - 30, cx + 14, cy - 2], fill=C.CARTE,
              outline=teinte, width=3)
    d.arc([cx - 28, cy + 4, cx + 28, cy + 58], start=180, end=360,
          fill=teinte, width=3)


DESSIN = {"moteur": moteur, "fenetre": fenetre, "personne": personne}

BLOCS = (
    ("moteur", "PrestaShop", "LE MOTEUR", C.ADMIN,
     ("le catalogue et les prix", "les stocks",
      "les commandes et les clients")),
    ("fenetre", "Next.js", "LA VITRINE", C.VITRINE,
     ("fabrique les pages", "porte le parcours d'achat",
      "porte le référencement")),
    ("personne", "Le visiteur", "", VISITEUR,
     ("navigateur", "mobile")),
)


def principal():
    C.verifier()

    out = Image.new("RGB", (L, H), C.FOND)
    d = ImageDraw.Draw(out, "RGBA")

    f_titre = C.police(C.POLICE_G, 30)
    f_nom = C.police(C.POLICE_G, 30)
    f_role = C.police(C.POLICE_G, 16)
    f_ligne = C.police(C.POLICE_R, 20)
    f_pastille = C.police(C.POLICE_G, 19)
    f_petit = C.police(C.POLICE_R, 17)
    f_bas = C.police(C.POLICE_R, 21)

    d.rectangle([MARGE, 44, MARGE + 10, 78], fill=C.VITRINE)
    d.text((MARGE + 24, 40), "OÙ VIVENT LES DONNÉES, OÙ NAISSENT LES PAGES",
           font=f_titre, fill=C.ENCRE)

    xs = [MARGE + i * (BLOC_L + ECART) for i in range(3)]
    milieu = Y0 + BLOC_H // 2

    for x, (cle, nom, role, teinte, lignes) in zip(xs, BLOCS):
        d.rounded_rectangle([x, Y0, x + BLOC_L, Y0 + BLOC_H], radius=18,
                            fill=C.CARTE, outline=C.BORD, width=2)
        #  Un filet de couleur en tête de bloc : c'est lui qui distingue les
        #  trois rôles sans qu'on ait à lire.
        d.rounded_rectangle([x, Y0, x + BLOC_L, Y0 + 8], radius=4, fill=teinte)

        DESSIN[cle](d, x + 70, Y0 + 74, teinte)
        d.text((x + 128, Y0 + 42), nom, font=f_nom, fill=C.ENCRE)
        if role:
            d.text((x + 128, Y0 + 80), role, font=f_role, fill=teinte)

        d.line([x + 30, Y0 + 128, x + BLOC_L - 30, Y0 + 128], fill=C.TRAIT,
               width=1)
        for i, ligne in enumerate(lignes):
            yy = Y0 + 150 + i * 36
            d.ellipse([x + 32, yy + 8, x + 40, yy + 16], fill=teinte)
            d.text((x + 54, yy), ligne, font=f_ligne, fill=C.GRIS)

    # ------------------------------------------------------------  les liens
    for i, (etiquette, sous, teinte) in enumerate(
            (("API", "produits · prix · stocks", C.VITRINE),
             ("la page", "livrée telle quelle", VISITEUR))):
        xa = xs[i] + BLOC_L
        xb = xs[i + 1]
        fleche_h(d, xa + 20, xb - 20, milieu, teinte)
        w = d.textlength(etiquette, font=f_pastille) + 34
        cx = (xa + xb) / 2
        d.rounded_rectangle([cx - w / 2, milieu - 46, cx + w / 2, milieu - 8],
                            radius=19, fill=teinte)
        d.text((cx - d.textlength(etiquette, font=f_pastille) / 2,
                milieu - 39), etiquette, font=f_pastille,
               fill=(255, 255, 255))
        f_sous = police_qui_tient(sous, ECART - 12)
        d.text((cx - d.textlength(sous, font=f_sous) / 2, milieu + 22), sous,
               font=f_sous, fill=C.FAIBLE)

    # -----------------------------------------------  la boucle de retour
    #  Elle passe SOUS les trois blocs et remonte dans le premier : c'est le
    #  seul endroit où une commande existe.
    yr = Y0 + BLOC_H + 74
    x_dep = xs[2] + BLOC_L // 2
    x_arr = xs[0] + BLOC_L // 2
    gris = (150, 160, 180)
    d.line([x_dep, Y0 + BLOC_H, x_dep, yr], fill=gris, width=3)
    d.line([x_dep, yr, x_arr, yr], fill=gris, width=3)
    d.line([x_arr, yr, x_arr, Y0 + BLOC_H + 14], fill=gris, width=3)
    d.polygon([(x_arr, Y0 + BLOC_H + 6), (x_arr - 8, Y0 + BLOC_H + 22),
               (x_arr + 8, Y0 + BLOC_H + 22)], fill=gris)

    t = "la commande repart jusqu'au moteur — c'est le seul endroit où elle existe"
    cx = (x_dep + x_arr) / 2
    lw = d.textlength(t, font=f_petit)
    d.rectangle([cx - lw / 2 - 14, yr - 12, cx + lw / 2 + 14, yr + 12],
                fill=C.FOND)
    d.text((cx - lw / 2, yr - 9), t, font=f_petit, fill=C.GRIS)

    # ------------------------------------------------------------  la phrase
    yb = H - 58
    d.line([MARGE, yb - 24, L - MARGE, yb - 24], fill=C.TRAIT, width=1)
    d.text((MARGE, yb),
           "PrestaShop ne fabrique plus aucune page : il fournit les données, "
           "Next.js fabrique les pages. C'est tout ce que veut dire « headless ».",
           font=f_bas, fill=C.GRIS)

    out.save(SORTIE, "WEBP", quality=C.QUALITE, method=6)
    print()
    print("  %d × %d" % out.size)
    print("  %s  (%.0f Ko)"
          % (os.path.basename(SORTIE), os.path.getsize(SORTIE) / 1024))


if __name__ == "__main__":
    principal()
