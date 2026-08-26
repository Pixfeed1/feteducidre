"""
IMAGE 2 de l'article « Comment obtenir son adresse IP » — IPv4 contre IPv6.

    python3 article-adresse-ip/formats_ipv4_ipv6.py

Produit `article-adresse-ip/format-adresse-ipv4-ipv6-comparaison.webp`.

----------------------------------------------------------------------------
CE QUE LA FIGURE DOIT FAIRE VOIR AVANT DE FAIRE LIRE
----------------------------------------------------------------------------
La légende dit « quatre nombres d'un côté, huit groupes de l'autre ». Ce
rapport de un à deux doit se voir AVANT qu'on ait lu un seul caractère : les
cases ont donc toutes la même largeur, et la ligne IPv6 est exactement deux
fois plus longue que la ligne IPv4. Si on ajustait la largeur des cases au
contenu, les deux lignes finiraient de longueur voisine et l'image dirait le
contraire du texte.

----------------------------------------------------------------------------
L'ÉCRITURE ABRÉGÉE EST DANS LA FIGURE, ET CE N'EST PAS UN BONUS
----------------------------------------------------------------------------
Personne ne rencontre jamais une adresse IPv6 sous sa forme longue. On voit
`2001:db8::1` et on ne la reconnaît pas comme la même chose. La figure montre
donc les deux écritures et les deux règles qui mènent de l'une à l'autre :

  - les zéros de tête de chaque groupe se retirent ;
  - UNE seule suite de groupes nuls se remplace par `::`.

« Une seule » est la règle qu'on oublie, et c'est celle qui rend l'adresse
ambiguë si on l'enfreint : avec deux `::`, on ne peut plus savoir combien de
groupes nuls chacun remplace.

----------------------------------------------------------------------------
LES CHIFFRES SONT CALCULÉS, PAS RECOPIÉS
----------------------------------------------------------------------------
2^32 et 2^128 sont écrits par le script, ainsi que le rapport entre les deux
et le nombre d'adresses par mètre carré de surface terrestre. Un article qui
cite « 340 sextillions » de mémoire se trompe une fois sur deux ; ici le
nombre affiché est celui que Python a calculé au moment du rendu.

L'adresse d'exemple est prise dans 2001:0db8::/32, le préfixe réservé par la
RFC 3849 à la documentation. C'est la seule plage qu'on puisse écrire dans un
article sans désigner la machine de quelqu'un.
"""

import os

from PIL import Image, ImageDraw

import charte as C

RACINE = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(RACINE, "format-adresse-ipv4-ipv6-comparaison.webp")

L, H = 1600, 1010
MARGE = 60

#  Une case de largeur FIXE des deux côtés : c'est ce qui fait que la ligne
#  IPv6 est deux fois plus longue à l'écran, comme elle l'est en nombre de
#  groupes.
CASE_L = 128
CASE_H = 78
ECART = 12

IPV4 = ("88", "120", "34", "7")
IPV6 = ("2001", "0db8", "3c4d", "0015", "0000", "0000", "1a2f", "1b3c")
IPV6_COURT = "2001:db8:3c4d:15::1a2f:1b3c"

#  Surface de la Terre, en mètres carrés (510,072 millions de km²).
TERRE_M2 = 510.072e12


def groupe(d, x, y, texte, teinte, f_case, sous, f_sous):
    d.rounded_rectangle([x, y, x + CASE_L, y + CASE_H], radius=10,
                        fill=C.PANNEAU, outline=teinte, width=2)
    w = d.textlength(texte, font=f_case)
    d.text((x + (CASE_L - w) / 2, y + 18), texte, font=f_case, fill=C.ENCRE)
    if sous:
        w2 = d.textlength(sous, font=f_sous)
        d.text((x + (CASE_L - w2) / 2, y + CASE_H + 10), sous, font=f_sous,
               fill=C.FAIBLE)


def ligne(d, x0, y, groupes, separateur, teinte, sous, f_case, f_sep, f_sous):
    x = x0
    for i, g in enumerate(groupes):
        groupe(d, x, y, g, teinte, f_case, sous, f_sous)
        x += CASE_L
        if i < len(groupes) - 1:
            w = d.textlength(separateur, font=f_sep)
            d.text((x + (ECART - w) / 2, y + 16), separateur, font=f_sep,
                   fill=teinte)
            x += ECART
    return x


def principal():
    C.verifier()

    #  Les nombres, calculés ici et nulle part ailleurs.
    v4 = 2 ** 32
    v6 = 2 ** 128
    rapport = v6 // v4                      # = 2**96
    par_m2 = v6 / TERRE_M2
    print()
    print("  IPv4 : %s adresses" % C.espacer(v4))
    print("  IPv6 : %s adresses" % C.espacer(v6))
    print("  rapport : %.2e   par metre carre de Terre : %.2e"
          % (rapport, par_m2))

    out = Image.new("RGB", (L, H), C.FOND)
    d = ImageDraw.Draw(out, "RGBA")

    f_titre = C.police(C.POLICE_G, 32)
    f_proto = C.police(C.POLICE_G, 38)
    f_case = C.police(C.POLICE_M, 30)
    f_sep = C.police(C.POLICE_M, 34)
    f_sous = C.police(C.POLICE_R, 17)
    f_txt = C.police(C.POLICE_R, 22)
    f_petit = C.police(C.POLICE_R, 19)
    f_mono = C.police(C.POLICE_M, 26)
    f_chiffre = C.police(C.POLICE_G, 34)
    f_long = C.police(C.POLICE_MR, 19)

    d.rectangle([MARGE, 46, MARGE + 10, 82], fill=C.PUBLIC)
    d.text((MARGE + 24, 42),
           "LE MÊME RÔLE, DEUX FORMATS, DEUX RÉSERVES",
           font=f_titre, fill=C.ENCRE)

    # -----------------------------------------------------------------  IPv4
    y = 148
    d.text((MARGE, y), "IPv4", font=f_proto, fill=C.LOCAL)
    d.text((MARGE + 118, y + 12), "32 bits", font=f_txt, fill=C.GRIS)
    y += 62
    fin4 = ligne(d, MARGE, y, IPV4, ".", C.LOCAL, "8 bits",
                 f_case, f_sep, f_sous)
    d.text((fin4 + 40, y + 8),
           "quatre nombres de 0 à 255,", font=f_txt, fill=C.GRIS)
    d.text((fin4 + 40, y + 38),
           "séparés par des points.", font=f_txt, fill=C.GRIS)

    y += CASE_H + 46
    d.line([MARGE, y, L - MARGE, y], fill=C.TRAIT, width=1)

    # -----------------------------------------------------------------  IPv6
    y += 40
    d.text((MARGE, y), "IPv6", font=f_proto, fill=C.PUBLIC)
    d.text((MARGE + 118, y + 12), "128 bits", font=f_txt, fill=C.GRIS)
    d.text((MARGE + 260, y + 12),
           "huit groupes de quatre chiffres hexadécimaux, "
           "séparés par des deux-points.", font=f_txt, fill=C.GRIS)
    y += 62
    ligne(d, MARGE, y, IPV6, ":", C.PUBLIC, "16 bits", f_case, f_sep, f_sous)

    #  L'écriture abrégée, sous la forme longue.
    y += CASE_H + 52
    d.text((MARGE, y), "la même adresse, telle qu'on la rencontre :",
           font=f_txt, fill=C.GRIS)
    d.text((MARGE + 470, y - 4), IPV6_COURT, font=f_mono, fill=C.PUBLIC)
    y += 34
    d.text((MARGE, y),
           "les zéros de tête de chaque groupe se retirent  ·  UNE seule "
           "suite de groupes nuls se remplace par « :: »",
           font=f_petit, fill=C.FAIBLE)
    y += 26
    d.text((MARGE, y),
           "une seule, car avec deux on ne saurait plus combien de groupes "
           "nuls chacune remplace.",
           font=f_petit, fill=C.FAIBLE)

    # ------------------------------------------------------------  la réserve
    y += 52
    d.line([MARGE, y, L - MARGE, y], fill=C.TRAIT, width=1)
    y += 26
    d.text((MARGE, y), "LA RÉSERVE D'ADRESSES", font=C.police(C.POLICE_G, 24),
           fill=C.ENCRE)
    y += 44

    d.rectangle([MARGE, y + 4, MARGE + 6, y + 30], fill=C.LOCAL)
    d.text((MARGE + 20, y), "IPv4", font=f_chiffre, fill=C.LOCAL)
    d.text((MARGE + 120, y + 8), C.espacer(v4), font=f_mono, fill=C.ENCRE)
    d.text((MARGE + 120, y + 44), "soit 4,3 milliards — moins d'une par "
           "habitant de la planète.", font=f_petit, fill=C.GRIS)

    y += 92
    d.rectangle([MARGE, y + 4, MARGE + 6, y + 30], fill=C.PUBLIC)
    d.text((MARGE + 20, y), "IPv6", font=f_chiffre, fill=C.PUBLIC)
    d.text((MARGE + 120, y + 10), C.espacer(v6), font=f_long, fill=C.ENCRE)
    d.text((MARGE + 120, y + 44),
           C.fr("soit environ %.1f × 10³⁸ — à peu près %.1f × 10²³ adresses "
                "par mètre carré de surface terrestre.",
                v6 / 1e38, par_m2 / 1e23),
           font=f_petit, fill=C.GRIS)

    y += 86
    #  %.0f arrondissait 7,92 à 8 et 6,67 à 7 : on perdait le chiffre qui
    #  rend le nombre vérifiable, sur une figure dont c'est tout l'argument.
    d.text((MARGE, y),
           C.fr("Le rapport entre les deux réserves est de 2⁹⁶, soit près de "
                "%.1f × 10²⁸ : IPv6 n'est pas « plus grand », il est sans "
                "commune mesure.", rapport / 1e28),
           font=f_txt, fill=C.GRIS)

    yf = H - 42
    d.line([MARGE, yf - 16, L - MARGE, yf - 16], fill=C.TRAIT, width=1)
    d.text((MARGE, yf),
           "Adresse d'exemple prise dans 2001:0db8::/32, le préfixe réservé "
           "à la documentation par la RFC 3849.",
           font=f_petit, fill=C.FAIBLE)

    out.save(SORTIE, "WEBP", quality=C.QUALITE, method=6)
    print()
    print("  %d × %d" % out.size)
    print("  %s  (%.0f Ko)"
          % (os.path.basename(SORTIE), os.path.getsize(SORTIE) / 1024))


if __name__ == "__main__":
    principal()
