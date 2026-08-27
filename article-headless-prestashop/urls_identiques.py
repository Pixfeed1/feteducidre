"""
IMAGE 4 de l'article « PrestaShop headless » — les URLs ne bougent pas.

    python3 article-headless-prestashop/urls_identiques.py

Produit `article-headless-prestashop/urls-identiques-migration-headless-sans-301.webp`.

----------------------------------------------------------------------------
L'IDÉE TIENT DANS UN TRAIT QUI NE S'INTERROMPT PAS
----------------------------------------------------------------------------
Le sujet est une absence : il ne se passe rien, l'URL ne change pas. Une
absence ne se dessine pas avec des boîtes et des flèches — il faut lui donner
une forme.

Ici c'est une barre. L'URL est une longue barre qui traverse toute la figure,
et le trait vertical de la migration passe DERRIÈRE elle. Sous la barre, le
moteur change de couleur : gris de fer avant, violet après. Le lecteur voit
donc en une seconde que ce qui change est en dessous, et que l'adresse, elle,
continue.

C'est aussi pour ça que la barre du haut — la chaîne habituelle avec sa
redirection — est barrée d'un trait rouge plutôt que simplement absente. Une
figure qui ne montre que la bonne solution n'apprend rien : c'est la
comparaison avec ce qu'on fait d'habitude qui donne sa valeur à l'absence.

----------------------------------------------------------------------------
CE QUE LA FIGURE NE DIT PAS, ET POURQUOI
----------------------------------------------------------------------------
Elle ne dit pas qu'une redirection 301 fait perdre du référencement. C'est une
croyance tenace et Google a confirmé depuis longtemps qu'une 301 transmet la
totalité du signal. L'écrire ferait exactement le tort qu'on veut éviter :
donner au lecteur un argument qu'on lui démontera ailleurs.

Ce qui est vrai tient en trois mots, écrits sous la chaîne barrée : une table
de correspondances à maintenir indéfiniment, un aller-retour de plus à chaque
visite, et des 404 partout où elle se trompe. Garder les mêmes URLs supprime
les trois d'un coup.
"""

import os

from PIL import Image, ImageDraw

import charte as C

RACINE = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(
    RACINE, "urls-identiques-migration-headless-sans-301.webp")

#  La hauteur suit le contenu : l'étiquette « migration » finit à 620, plus
#  une marge. Fixée à 742, il restait une bande vide sous la figure.
L, H = 1600, 660
MARGE = 60

URL = "/vinyles/mon-disque.html"
URL_NEUVE = "/products/12-mon-disque"

BARRE_H = 74


def boite_url(d, x, y, w, texte, f, teinte, encre, fond=None):
    d.rounded_rectangle([x, y, x + w, y + BARRE_H], radius=12,
                        fill=fond if fond else C.CARTE, outline=teinte,
                        width=2)
    d.text((x + 26, y + BARRE_H / 2 - 14), texte, font=f, fill=encre)


def pointilles_v(d, x, y0, y1, couleur, pas=15, plein=8, largeur=3):
    y = y0
    while y < y1:
        d.line([x, y, x, min(y + plein, y1)], fill=couleur, width=largeur)
        y += pas


def fleche(d, x0, x1, y, couleur):
    d.line([x0, y, x1 - 12, y], fill=couleur, width=3)
    d.polygon([(x1, y), (x1 - 13, y - 7), (x1 - 13, y + 7)], fill=couleur)


def principal():
    C.verifier()

    out = Image.new("RGB", (L, H), C.FOND)
    d = ImageDraw.Draw(out, "RGBA")

    f_titre = C.police(C.POLICE_G, 30)
    f_url = C.police(C.POLICE_M, 24)
    f_url_g = C.police(C.POLICE_M, 27)
    f_etiq = C.police(C.POLICE_G, 19)
    f_moteur = C.police(C.POLICE_G, 22)
    f_note = C.police(C.POLICE_R, 20)
    f_badge = C.police(C.POLICE_G, 26)

    d.rectangle([MARGE, 44, MARGE + 10, 78], fill=C.VITRINE)
    d.text((MARGE + 24, 40), "L'ADRESSE NE BOUGE PAS", font=f_titre,
           fill=C.ENCRE)

    # ------------------------------------------------  ce qu'on fait d'habitude
    y = 124
    d.text((MARGE, y), "D'HABITUDE", font=f_etiq, fill=C.FAIBLE)
    y += 32

    gris = (176, 182, 194)
    b1 = 430
    boite_url(d, MARGE, y, b1, URL, f_url, gris, gris)
    x = MARGE + b1
    fleche(d, x + 22, x + 78, y + BARRE_H / 2, gris)
    #  La pastille est plus haute et son texte plus gros qu'ailleurs : le
    #  trait rouge lui passe dessus, et à 19 points « 301 » n'était plus qu'une
    #  tache. Ce qu'on barre doit rester lisible, sinon on barre du vide.
    f_301 = C.police(C.POLICE_G, 24)
    d.rounded_rectangle([x + 92, y + 6, x + 184, y + BARRE_H - 6],
                        radius=31, fill=gris)
    t = "301"
    d.text((x + 138 - d.textlength(t, font=f_301) / 2, y + BARRE_H / 2 - 15),
           t, font=f_301, fill=C.CARTE)
    fleche(d, x + 198, x + 246, y + BARRE_H / 2, gris)
    boite_url(d, x + 260, y, b1, URL_NEUVE, f_url, gris, gris)

    #  LE TRAIT ROUGE. Il barre toute la chaîne, pas seulement la pastille :
    #  ce n'est pas la redirection qu'on refuse, c'est le fait de changer
    #  d'adresse — la redirection n'en est que la conséquence.
    d.line([MARGE - 10, y + BARRE_H / 2, x + 260 + b1 + 10, y + BARRE_H / 2],
           fill=C.ALERTE, width=4)

    y += BARRE_H + 18
    d.text((MARGE, y),
           "une table de correspondances à maintenir, un aller-retour de plus, "
           "et des 404 partout où elle se trompe",
           font=f_note, fill=C.FAIBLE)

    # ---------------------------------------------------------------  ici
    y += 62
    d.line([MARGE, y, L - MARGE, y], fill=C.TRAIT, width=1)
    y += 30
    d.text((MARGE, y), "ICI", font=f_etiq, fill=C.VITRINE)
    y += 34

    #  Le trait de la migration, tracé D'ABORD : la barre de l'URL passera
    #  par-dessus, et c'est ce recouvrement qui dit la continuité.
    x_mig = MARGE + (L - 2 * MARGE) // 2
    pointilles_v(d, x_mig, y - 10, y + 236, (196, 202, 214))

    largeur = L - 2 * MARGE
    boite_url(d, MARGE, y, largeur, URL, f_url_g, C.VITRINE, C.ENCRE)

    #  Sous la barre : le moteur, qui lui change.
    ym = y + BARRE_H + 44
    demi = largeur // 2
    d.rounded_rectangle([MARGE, ym, MARGE + demi, ym + 76], radius=12,
                        fill=C.ADMIN)
    d.rounded_rectangle([MARGE + demi, ym, MARGE + largeur, ym + 76],
                        radius=12, fill=C.VITRINE)
    for x0, w, nom, sous in ((MARGE, demi, "PrestaShop", "avant"),
                             (MARGE + demi, largeur - demi, "Next.js",
                              "après")):
        cx = x0 + w / 2
        d.text((cx - d.textlength(nom, font=f_moteur) / 2, ym + 16), nom,
               font=f_moteur, fill=C.CARTE)
        d.text((cx - d.textlength(sous, font=f_note) / 2, ym + 44), sous,
               font=f_note, fill=(224, 226, 236))

    #  L'étiquette de la migration, posée sur le pointillé.
    t = "migration"
    w = d.textlength(t, font=f_etiq) + 26
    d.rounded_rectangle([x_mig - w / 2, ym + 92, x_mig + w / 2, ym + 128],
                        radius=18, fill=C.FOND, outline=(196, 202, 214),
                        width=2)
    d.text((x_mig - d.textlength(t, font=f_etiq) / 2, ym + 101), t,
           font=f_etiq, fill=C.GRIS)

    #  LE BADGE. Le chiffre est le sujet de l'image, il a le droit d'être gros.
    t = "0 redirection"
    w = d.textlength(t, font=f_badge) + 48
    d.rounded_rectangle([L - MARGE - w, y - 96, L - MARGE, y - 36], radius=30,
                        fill=C.VITRINE)
    d.text((L - MARGE - w / 2 - d.textlength(t, font=f_badge) / 2, y - 79), t,
           font=f_badge, fill=C.CARTE)

    out.save(SORTIE, "WEBP", quality=C.QUALITE, method=6)
    print()
    print("  %d × %d" % out.size)
    print("  %s  (%.0f Ko)"
          % (os.path.basename(SORTIE), os.path.getsize(SORTIE) / 1024))


if __name__ == "__main__":
    principal()
