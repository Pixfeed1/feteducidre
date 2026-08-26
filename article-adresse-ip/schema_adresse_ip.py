"""
IMAGE 1 de l'article « Comment obtenir son adresse IP » — l'image à la une.

    python3 article-adresse-ip/schema_adresse_ip.py

Produit `article-adresse-ip/adresse-ip-locale-publique-box.webp`.

----------------------------------------------------------------------------
CE QUE LE SCHÉMA DOIT FAIRE COMPRENDRE EN UN COUP D'ŒIL
----------------------------------------------------------------------------
La légende annonce « deux adresses, deux rôles ». Un schéma qui se contente
d'aligner un appareil, une box et un site ne montre pas deux rôles : il montre
un tuyau. Ce qui sépare les deux adresses, ce n'est pas leur position sur la
ligne, c'est une FRONTIÈRE — celle de votre réseau.

D'où les trois décisions de mise en scène :

  - une limite verticale en pointillés traverse l'image, et la box est posée
    DESSUS. C'est le seul objet du schéma qui appartient aux deux mondes, et
    c'est exactement son rôle : elle a une adresse de chaque côté ;
  - trois appareils, pas un. Avec un seul, rien n'explique pourquoi l'adresse
    publique est « la vôtre » plutôt que « celle de votre ordinateur ». À
    trois, on voit que les trois adresses locales diffèrent et que le site,
    lui, n'en voit qu'une, la même pour tous ;
  - la couleur porte le sens et rien d'autre. Vert d'eau pour ce qui reste à
    la maison, violet pour ce qui circule. Les deux teintes ne se croisent
    jamais : aucune adresse locale n'apparaît à droite de la frontière, et
    c'est ça, la démonstration.

----------------------------------------------------------------------------
LES CHIFFRES SONT DES EXEMPLES, MAIS PAS N'IMPORTE LESQUELS
----------------------------------------------------------------------------
Les adresses locales sont prises dans 192.168.0.0/16, l'une des trois plages
réservées aux réseaux privés — c'est ce qui garantit qu'elles ne circulent
jamais sur Internet. L'adresse publique de l'exemple est prise dans une plage
réellement routable, pour ne pas apprendre au lecteur une adresse qui n'existe
nulle part.

----------------------------------------------------------------------------
UNE IMAGE À LA UNE SE FAIT ROGNER
----------------------------------------------------------------------------
WordPress la recadre selon les thèmes et les emplacements : 16/9, carré,
bandeau. Tout ce qui porte le sens tient donc dans la bande centrale, et les
marges ne contiennent que du décor. La ligne de bas de page est la seule chose
qu'on accepte de perdre.
"""

import os

from PIL import Image, ImageDraw, ImageFont

RACINE = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(RACINE, "adresse-ip-locale-publique-box.webp")

L, H = 1600, 900
QUALITE = 92

#  La palette, les polices et le contrôle de contraste vivent dans `charte.py`
#  et sont partagés par toutes les figures de l'article. Deux figures qui se
#  suivent avec deux verts différents se lisent comme deux articles.
from charte import (FOND, PANNEAU, BORD, ENCRE, GRIS, FAIBLE, TRAIT, ECRAN,
                    LOCAL, PUBLIC, POLICE_G, POLICE_R, POLICE_M, QUALITE,
                    police, verifier)

FRONTIERE = 800                 # l'abscisse de la limite, au milieu de la box

APPAREILS = (
    ("ordinateur", "Ordinateur", "192.168.1.42"),
    ("telephone", "Téléphone", "192.168.1.51"),
    ("televiseur", "Téléviseur", "192.168.1.23"),
)
IP_BOX_LOCALE = "192.168.1.1"
IP_PUBLIQUE = "88.120.34.7"



def pointilles(d, x, y0, y1, couleur, pas=14, plein=7, largeur=2):
    """PIL ne sait pas tracer en pointillés : on pose les tirets un par un."""
    y = y0
    while y < y1:
        d.line([x, y, x, min(y + plein, y1)], fill=couleur, width=largeur)
        y += pas


def fleche(d, x0, y0, x1, y1, couleur, largeur=3, pointe=13):
    import math
    d.line([x0, y0, x1, y1], fill=couleur, width=largeur)
    a = math.atan2(y1 - y0, x1 - x0)
    for signe in (+1, -1):
        b = a + signe * math.radians(148)
        d.line([x1, y1, x1 + pointe * math.cos(b), y1 + pointe * math.sin(b)],
               fill=couleur, width=largeur)


# ---------------------------------------------------------------------------
#  LES OBJETS. Dessinés à la main : une icône qu'on dessine se redimensionne
#  et se recolore, une icône qu'on télécharge fait dépendre la figure d'un
#  fichier qu'on n'a pas.
# ---------------------------------------------------------------------------
def ordinateur(d, cx, cy, w, couleur):
    h = int(w * 0.64)
    x0, y0 = cx - w // 2, cy - h // 2 - 8
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=10,
                        fill=ECRAN, outline=couleur, width=3)
    d.rounded_rectangle([x0 - 14, y0 + h + 4, x0 + w + 14, y0 + h + 16],
                        radius=6, fill=couleur)


def telephone(d, cx, cy, w, couleur):
    ww = int(w * 0.46)
    hh = int(w * 0.82)
    x0, y0 = cx - ww // 2, cy - hh // 2
    d.rounded_rectangle([x0, y0, x0 + ww, y0 + hh], radius=12,
                        fill=ECRAN, outline=couleur, width=3)
    d.line([cx - 12, y0 + 12, cx + 12, y0 + 12], fill=couleur, width=3)


def televiseur(d, cx, cy, w, couleur):
    h = int(w * 0.58)
    x0, y0 = cx - w // 2, cy - h // 2 - 10
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=8,
                        fill=ECRAN, outline=couleur, width=3)
    d.line([cx, y0 + h, cx, y0 + h + 14], fill=couleur, width=3)
    d.line([cx - 22, y0 + h + 14, cx + 22, y0 + h + 14], fill=couleur,
           width=4)


DESSIN = {"ordinateur": ordinateur, "telephone": telephone,
          "televiseur": televiseur}


def la_box(d, cx, cy, w):
    """La box, à cheval sur la frontière : le seul objet des deux mondes."""
    h = int(w * 0.52)
    x0, y0 = cx - w // 2, cy - h // 2
    #  Deux antennes, l'une de chaque côté — le détail qui la fait reconnaître.
    for dx in (-w // 3, w // 3):
        d.line([cx + dx, y0, cx + dx, y0 - 34], fill=(168, 174, 186), width=5)
        d.ellipse([cx + dx - 6, y0 - 44, cx + dx + 6, y0 - 32],
                  fill=(168, 174, 186))
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=14,
                        fill=PANNEAU, outline=(120, 128, 142), width=3)
    #  Les diodes : vert d'eau côté maison, violet côté Internet.
    for i, coul in enumerate((LOCAL, LOCAL, PUBLIC)):
        px = x0 + 26 + i * 22
        d.ellipse([px, y0 + h - 24, px + 10, y0 + h - 14], fill=coul)


def navigateur(d, x0, y0, w, h, f_petit, f_ip, f_txt):
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=14,
                        fill=PANNEAU, outline=BORD, width=2)
    d.rounded_rectangle([x0, y0, x0 + w, y0 + 46], radius=14, fill=ECRAN)
    d.rectangle([x0, y0 + 32, x0 + w, y0 + 46], fill=ECRAN)
    for i in range(3):
        d.ellipse([x0 + 20 + i * 20, y0 + 17, x0 + 30 + i * 20, y0 + 27],
                  fill=(196, 202, 212))
    d.text((x0 + 96, y0 + 13), "un-site-quelconque.fr", font=f_petit,
           fill=FAIBLE)

    d.text((x0 + 34, y0 + 86), "Ce que ce site voit de vous", font=f_txt,
           fill=GRIS)
    d.text((x0 + 34, y0 + 128), IP_PUBLIQUE, font=f_ip, fill=PUBLIC)
    d.text((x0 + 34, y0 + 196),
           "— et rien de plus, quel que soit", font=f_txt, fill=FAIBLE)
    d.text((x0 + 34, y0 + 226),
           "  l'appareil que vous utilisez.", font=f_txt, fill=FAIBLE)




def principal():
    verifier()
    out = Image.new("RGB", (L, H), FOND)
    d = ImageDraw.Draw(out, "RGBA")

    f_zone = police(POLICE_G, 22)
    f_nom = police(POLICE_R, 25)
    f_ip = police(POLICE_M, 27)
    f_ip_gros = police(POLICE_M, 38)
    f_txt = police(POLICE_R, 22)
    f_note = police(POLICE_R, 23)
    f_petit = police(POLICE_R, 19)

    #  LA FRONTIÈRE. Elle est tracée avant tout le reste : c'est le fond sur
    #  lequel les deux mondes se distinguent.
    pointilles(d, FRONTIERE, 96, H - 210, (176, 182, 194))
    d.rectangle([0, 96, FRONTIERE, H - 210], fill=(6, 119, 97, 14))
    d.rectangle([FRONTIERE, 96, L, H - 210], fill=(98, 44, 200, 12))

    d.text((70, 58), "CHEZ VOUS", font=f_zone, fill=LOCAL)
    d.text((70, 88), "votre réseau local", font=f_petit, fill=FAIBLE)
    t = "INTERNET"
    d.text((L - 70 - d.textlength(t, font=f_zone), 58), t, font=f_zone,
           fill=PUBLIC)
    t2 = "tout ce qui est en dehors"
    d.text((L - 70 - d.textlength(t2, font=f_petit), 88), t2, font=f_petit,
           fill=FAIBLE)

    #  LES TROIS APPAREILS.
    ys = (250, 400, 550)
    for (cle, nom, ip), y in zip(APPAREILS, ys):
        DESSIN[cle](d, 150, y, 96, LOCAL)
        d.text((232, y - 26), nom, font=f_nom, fill=ENCRE)
        d.text((232, y + 6), ip, font=f_ip, fill=LOCAL)
        fleche(d, 470, y, 660, 400, (6, 119, 97, 120), 2, 10)

    #  LA BOX, posée sur la frontière.
    la_box(d, FRONTIERE, 400, 190)
    d.text((FRONTIERE - 30, 486), "LA BOX", font=f_zone, fill=ENCRE)
    d.text((FRONTIERE - 236, 528), IP_BOX_LOCALE, font=f_ip, fill=LOCAL)
    d.text((FRONTIERE + 40, 528), IP_PUBLIQUE, font=f_ip, fill=PUBLIC)
    d.text((FRONTIERE - 236, 560), "son adresse côté maison", font=f_petit,
           fill=FAIBLE)
    d.text((FRONTIERE + 40, 560), "son adresse côté Internet", font=f_petit,
           fill=FAIBLE)

    #  LE SITE.
    #
    #  La carte du navigateur commençait à x = 1010 et recouvrait la fin de
    #  l'adresse publique écrite sous la box : « 88.120.34.7 » se terminait
    #  derrière elle. On mesure donc où finit ce texte, et on refuse de
    #  produire la figure si la carte mord dessus — une adresse tronquée dans
    #  un schéma qui explique les adresses, c'est la seule faute qu'on ne
    #  puisse pas rattraper par une légende.
    fin_ip = FRONTIERE + 40 + d.textlength(IP_PUBLIQUE, font=f_ip)
    carte_x = 1076
    if carte_x < fin_ip + 24:
        raise SystemExit("la carte du site recouvre l'adresse publique de la "
                         "box (%d px de trop)" % (fin_ip + 24 - carte_x))
    fleche(d, 900, 400, carte_x - 16, 400, PUBLIC, 3, 14)
    navigateur(d, carte_x, 250, L - 70 - carte_x, 300,
               f_petit, f_ip_gros, f_txt)

    #  LES DEUX RÔLES, écrits en toutes lettres sous le schéma.
    yb = H - 178
    d.line([70, yb - 20, L - 70, yb - 20], fill=TRAIT, width=1)
    for x, coul, titre, lignes in (
            (70, LOCAL, "L'ADRESSE LOCALE reste chez vous",
             ["Attribuée par la box à chaque appareil. Elle sert à",
              "les distinguer entre eux — et elle ne franchit jamais",
              "la ligne : aucun site ne la voit."]),
            (830, PUBLIC, "L'ADRESSE PUBLIQUE circule",
             ["Attribuée par votre opérateur, à la box. C'est la seule",
              "que les sites voient, et elle est la même pour tous vos",
              "appareils : ils passent tous par la même porte."])):
        d.rectangle([x, yb + 2, x + 8, yb + 26], fill=coul)
        d.text((x + 22, yb - 2), titre, font=police(POLICE_G, 24), fill=ENCRE)
        for i, ligne in enumerate(lignes):
            d.text((x + 22, yb + 38 + i * 29), ligne, font=f_note, fill=GRIS)

    #  LA RÉSERVE QUI REND LE SCHÉMA HONNÊTE.
    #
    #  « Une seule adresse publique pour tous vos appareils » est vrai en
    #  IPv4, parce que la box traduit les adresses (NAT). En IPv6 il n'y a pas
    #  de traduction : chaque appareil porte en plus sa propre adresse
    #  publique, et le raisonnement du schéma ne tient plus tel quel. Or les
    #  principaux opérateurs français activent IPv6 par défaut.
    #
    #  Le schéma reste celui d'IPv4 — c'est ce que voit le lecteur quand il
    #  cherche « mon adresse IP », et c'est ce que la légende décrit. Mais on
    #  l'écrit, plutôt que de laisser croire à une règle sans exception.
    d.text((70, H - 44),
           "Schéma en IPv4, le cas le plus courant. En IPv6, il n'y a pas de "
           "traduction : chaque appareil porte en plus sa propre adresse "
           "publique.",
           font=f_petit, fill=FAIBLE)

    out.save(SORTIE, "WEBP", quality=QUALITE, method=6)
    print()
    print("  %d × %d" % out.size)
    print("  %s  (%.0f Ko)"
          % (os.path.basename(SORTIE), os.path.getsize(SORTIE) / 1024))


if __name__ == "__main__":
    principal()
