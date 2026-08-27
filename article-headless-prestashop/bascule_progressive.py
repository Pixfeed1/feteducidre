"""
IMAGE 5 de l'article « PrestaShop headless » — le sélecteur de bascule.

    python3 article-headless-prestashop/bascule_progressive.py

Produit `article-headless-prestashop/bascule-progressive-back-office-prestashop.webp`.

----------------------------------------------------------------------------
POURQUOI UNE RECONSTITUTION, ET NON UNE CAPTURE
----------------------------------------------------------------------------
Le brief laisse le choix entre capture anonymisée et reconstitution. C'est la
reconstitution, pour deux raisons dont la seconde suffirait seule.

D'abord l'environnement : pas de démon Docker, pas de serveur MySQL, et les
dépôts de paquets répondent 403. PrestaShop ne peut donc pas tourner ici.

Ensuite, et c'est décisif : CE RÉGLAGE N'EXISTE PAS DANS PRESTASHOP. Un
sélecteur à trois positions Désactivé / Par IP / Complet est un module écrit
pour cette migration-là. Même sur une boutique qui tourne, l'écran n'existe
qu'une fois le module installé — une « vraie capture » serait donc la capture
d'une interface qu'on aurait dessinée soi-même, avec des étapes en plus.

La figure est donc une maquette, et elle le dit : elle reprend la mise en page
d'un panneau de configuration sans imiter la charte de PrestaShop, sans logo,
sans nom de boutique et sans domaine.

----------------------------------------------------------------------------
LES ADRESSES DE L'EXEMPLE
----------------------------------------------------------------------------
Prises dans 203.0.113.0/24, la plage que la RFC 5737 réserve à la
documentation. Aucune machine réelle ne porte ces adresses : le brief demande
d'anonymiser, et une adresse inventée au hasard désigne toujours quelqu'un.

----------------------------------------------------------------------------
CE QUE LA FIGURE DOIT PROUVER
----------------------------------------------------------------------------
Que c'est le commerçant qui pilote. D'où le choix de montrer le réglage EN
COURS D'USAGE — position du milieu retenue, champ d'adresses ouvert en
dessous, bouton d'enregistrement actif — plutôt qu'un menu au repos. Un
réglage qu'on voit à moitié rempli est un réglage dont on comprend qu'il se
manipule.
"""

import os

from PIL import Image, ImageDraw

import charte as C

RACINE = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(
    RACINE, "bascule-progressive-back-office-prestashop.webp")

L, H = 1600, 726
MARGE = 60

OPTIONS = (
    ("Désactivé", "tout est servi par PrestaShop", False),
    ("Par IP", "seules les adresses listées voient le nouveau front", True),
    ("Complet", "tout le monde voit le nouveau front", False),
)
#  RFC 5737 : plage réservée à la documentation.
ADRESSES = "203.0.113.24, 203.0.113.57"


def principal():
    C.verifier()

    out = Image.new("RGB", (L, H), C.FOND)
    d = ImageDraw.Draw(out, "RGBA")

    f_titre = C.police(C.POLICE_G, 30)
    f_entete = C.police(C.POLICE_G, 24)
    f_label = C.police(C.POLICE_G, 20)
    f_opt = C.police(C.POLICE_G, 24)
    f_desc = C.police(C.POLICE_R, 18)
    f_champ = C.police(C.POLICE_M, 21)
    f_aide = C.police(C.POLICE_R, 17)
    f_bouton = C.police(C.POLICE_G, 19)
    f_note = C.police(C.POLICE_R, 21)

    d.rectangle([MARGE, 44, MARGE + 10, 78], fill=C.VITRINE)
    d.text((MARGE + 24, 40), "LE COMMERÇANT GARDE LA MAIN", font=f_titre,
           fill=C.ENCRE)

    # ------------------------------------------------------------  le panneau
    cx0, cy0 = MARGE, 116
    cw = L - 2 * MARGE
    ch = 480
    d.rounded_rectangle([cx0, cy0, cx0 + cw, cy0 + ch], radius=16,
                        fill=C.CARTE, outline=C.BORD, width=2)
    #  L'en-tête du panneau, dans l'arrondi.
    d.rounded_rectangle([cx0, cy0, cx0 + cw, cy0 + 62], radius=16,
                        fill=(243, 245, 249))
    d.rectangle([cx0, cy0 + 46, cx0 + cw, cy0 + 62], fill=(243, 245, 249))
    d.rounded_rectangle([cx0 + 26, cy0 + 20, cx0 + 62, cy0 + 42], radius=11,
                        fill=C.VITRINE)
    d.ellipse([cx0 + 44, cy0 + 22, cx0 + 60, cy0 + 40], fill=C.CARTE)
    d.text((cx0 + 78, cy0 + 18), "Bascule progressive", font=f_entete,
           fill=C.ENCRE)

    d.text((cx0 + 40, cy0 + 92), "MODE DE DIFFUSION", font=f_label,
           fill=C.FAIBLE)

    # ------------------------------------------------------------  les options
    ox = cx0 + 40
    oy = cy0 + 128
    ow = (cw - 80 - 2 * 26) // 3
    oh = 128
    x_choisi = None
    for i, (nom, desc, actif) in enumerate(OPTIONS):
        x = ox + i * (ow + 26)
        teinte = C.VITRINE if actif else C.BORD
        d.rounded_rectangle([x, oy, x + ow, oy + oh], radius=12,
                            fill=(250, 248, 255) if actif else C.CARTE,
                            outline=teinte, width=3 if actif else 2)
        #  Le bouton radio : anneau vide, ou anneau plein avec sa pastille.
        d.ellipse([x + 22, oy + 26, x + 46, oy + 50], fill=C.CARTE,
                  outline=C.VITRINE if actif else (188, 195, 208), width=3)
        if actif:
            d.ellipse([x + 28, oy + 32, x + 40, oy + 44], fill=C.VITRINE)
            x_choisi = x + ow / 2
        d.text((x + 60, oy + 24), nom, font=f_opt,
               fill=C.ENCRE if actif else C.GRIS)
        #  La description passe à la ligne toute seule si elle est longue.
        mots, ligne, lignes = desc.split(), "", []
        for m in mots:
            essai = (ligne + " " + m).strip()
            if d.textlength(essai, font=f_desc) > ow - 44:
                lignes.append(ligne)
                ligne = m
            else:
                ligne = essai
        lignes.append(ligne)
        for j, t in enumerate(lignes[:2]):
            d.text((x + 22, oy + 70 + j * 24), t, font=f_desc, fill=C.GRIS)

    # ------------------------------------  le champ, rattaché à l'option retenue
    fy = oy + oh + 34
    #  Un bec qui pointe vers l'option choisie : c'est lui qui dit que le
    #  champ appartient à « Par IP » et pas au panneau en général.
    d.polygon([(x_choisi, fy - 14), (x_choisi - 14, fy + 2),
               (x_choisi + 14, fy + 2)], fill=(250, 248, 255))
    d.rounded_rectangle([cx0 + 40, fy, cx0 + cw - 40, fy + 108], radius=12,
                        fill=(250, 248, 255), outline=(216, 206, 246), width=2)
    d.text((cx0 + 64, fy + 20), "ADRESSES AUTORISÉES", font=C.police(
        C.POLICE_G, 16), fill=C.VITRINE)
    d.rounded_rectangle([cx0 + 64, fy + 46, cx0 + cw - 64, fy + 88],
                        radius=8, fill=C.CARTE, outline=C.BORD, width=2)
    d.text((cx0 + 82, fy + 57), ADRESSES, font=f_champ, fill=C.ENCRE)
    aide = "vos bureaux, votre téléphone — personne d'autre ne voit le "\
           "nouveau front"
    d.text((cx0 + cw - 64 - d.textlength(aide, font=f_aide), fy + 22), aide,
           font=f_aide, fill=C.FAIBLE)

    # ------------------------------------------------------------  le bouton
    by = cy0 + ch - 64
    bw = 200
    d.rounded_rectangle([cx0 + cw - 40 - bw, by, cx0 + cw - 40, by + 46],
                        radius=10, fill=C.VITRINE)
    t = "Enregistrer"
    d.text((cx0 + cw - 40 - bw / 2 - d.textlength(t, font=f_bouton) / 2,
            by + 12), t, font=f_bouton, fill=C.CARTE)

    # ------------------------------------------------------------  la note
    yf = cy0 + ch + 44
    d.line([MARGE, yf, L - MARGE, yf], fill=C.TRAIT, width=1)
    d.text((MARGE, yf + 22),
           "Trois positions, un bouton : le commerçant bascule, vérifie, et "
           "revient en arrière sans appeler personne.",
           font=f_note, fill=C.GRIS)

    out.save(SORTIE, "WEBP", quality=C.QUALITE, method=6)
    print()
    print("  %d × %d" % out.size)
    print("  %s  (%.0f Ko)"
          % (os.path.basename(SORTIE), os.path.getsize(SORTIE) / 1024))


if __name__ == "__main__":
    principal()
