"""
Compléter la traduction française de l'écran des extensions.

    python3 article-agence-web/traduire_fr.py

Écrit `wp-content/languages/fr_FR.mo` dans le WordPress du conteneur.

----------------------------------------------------------------------------
LE PROBLÈME
----------------------------------------------------------------------------
`translate.wordpress.org` et `downloads.wordpress.org` sont refusés par la
politique de sortie de cet environnement : impossible d'installer le pack de
langue par la voie normale. Le seul jeu de fichiers atteignable est le miroir
GitHub `ThemeBoy/wp-languages`, qui date de 2014.

Résultat : les menus, les colonnes et les boutons sortent en français — ces
chaînes n'ont pas bougé depuis dix ans — mais la phrase qui compte ici, celle
qui annonce la mise à jour impossible, reste en anglais. Son identifiant a
changé entre-temps : WordPress écrivait

    <a href="%2$s" class="thickbox" title="%3$s">

et écrit aujourd'hui

    <a href="%2$s" %3$s>

Un seul caractère de différence suffit à ce que gettext ne reconnaisse plus la
chaîne et retombe sur l'anglais.

----------------------------------------------------------------------------
CE QUE FAIT CE SCRIPT, ET CE QU'IL NE FAIT PAS
----------------------------------------------------------------------------
Il RECALE les traductions officielles sur les identifiants actuels. La phrase
française vient telle quelle du pack officiel fr_FR — je n'ai touché qu'aux
marqueurs de position. Les quelques libellés apparus après 2014 (« Ajouter une
extension », « Mises à jour automatiques ») sont traduits ici selon l'usage
constant de la traduction française de WordPress.

Ce n'est donc pas un habillage : le fichier produit est un vrai catalogue
gettext, chargé par WordPress comme n'importe quel pack de langue. Ce qui
s'affiche à l'écran est bien du WordPress traduit, pas une image retouchée.
"""

import os
import struct
import sys

MIROIR = "/home/user/themeboy/wp-languages"
CIBLE = "/tmp/wp-html/wp-content/languages/fr_FR.mo"

NUL = b"\x00"
CTX = b"\x04"          # séparateur msgctxt, dans le format gettext

#  Les deux phrases du coeur de WordPress, reprises du pack officiel de 2014 et
#  recalées sur les identifiants de la 7.1. Seuls les marqueurs changent.
_MAJ = ("Il y a une nouvelle version de %1$s disponible. "
        "<a href=\"%2$s\" %3$s>Afficher les détails de la version %4$s</a>")

TRADUCTIONS = {
    "There is a new version of %1$s available. <a href=\"%2$s\" %3$s>View "
    "version %4$s details</a>. <em>Automatic update is unavailable for this "
    "plugin.</em>":
        _MAJ + ". <em>La mise à jour automatique n&rsquo;est pas possible "
               "pour cette extension</em>.",

    "There is a new version of %1$s available. <a href=\"%2$s\" %3$s>View "
    "version %4$s details</a>.":
        _MAJ + ".",

    "View %1$s version %2$s details":
        "Afficher les détails de la version %2$s de %1$s",

    #  Libellés d'écran apparus après le pack de 2014.
    "Add Plugin": "Ajouter une extension",
    "Bulk actions": "Actions groupées",
    "Select bulk action": "Sélectionner l’action groupée",
    "Search installed plugins": "Rechercher parmi les extensions installées",
    "Automatic Updates": "Mises à jour automatiques",
    "Enable auto-updates": "Activer les mises à jour automatiques",
    "View details": "Voir les détails",
    "Howdy, %s": "Bonjour, %s",
    "Collapse Menu": "Réduire le menu",

    #  Chaînes à contexte : « plugin » ici, parce que « Activate » ne se traduit
    #  pas pareil pour une extension et pour un thème.
    "plugin\x04Activate": "Activer",
    "plugin\x04Activate %s": "Activer %s",
}

#  Les pluriels s'écrivent avec un NUL entre les deux formes, des deux côtés.
PLURIELS = {
    ("%s item", "%s items"): ("%s élément", "%s éléments"),
    ("Auto-updates Disabled <span class=\"count\">(%s)</span>",
     "Auto-updates Disabled <span class=\"count\">(%s)</span>"):
        ("Mises à jour automatiques désactivées "
         "<span class=\"count\">(%s)</span>",
         "Mises à jour automatiques désactivées "
         "<span class=\"count\">(%s)</span>"),
}


def lire_mo(chemin):
    """Le catalogue tel quel, en octets — aucune interprétation."""
    with open(chemin, "rb") as f:
        brut = f.read()
    magie = struct.unpack("<I", brut[:4])[0]
    boutisme = "<" if magie == 0x950412de else ">"
    if magie not in (0x950412de, 0xde120495):
        raise SystemExit("%s n'est pas un fichier .mo" % chemin)
    n, o_orig, o_trad = struct.unpack(boutisme + "3I", brut[8:20])
    entrees = {}
    for i in range(n):
        lo, po = struct.unpack(boutisme + "2I", brut[o_orig + i * 8:
                                                     o_orig + i * 8 + 8])
        lt, pt = struct.unpack(boutisme + "2I", brut[o_trad + i * 8:
                                                     o_trad + i * 8 + 8])
        entrees[brut[po:po + lo]] = brut[pt:pt + lt]
    return entrees


def ecrire_mo(chemin, entrees):
    """
    Le format .mo est simple : deux tables de (longueur, position), puis les
    chaînes. Les identifiants doivent être triés — c'est ce tri qui permet la
    recherche dichotomique côté lecteur.
    """
    cles = sorted(entrees)
    n = len(cles)
    debut = 28 + n * 16
    corps, tables_o, tables_t = b"", [], []
    for c in cles:
        tables_o.append((len(c), debut + len(corps)))
        corps += c + NUL
    for c in cles:
        t = entrees[c]
        tables_t.append((len(t), debut + len(corps)))
        corps += t + NUL
    tete = struct.pack("<7I", 0x950412de, 0, n, 28, 28 + n * 8, 0, 0)
    plat = b"".join(struct.pack("<2I", l, p) for l, p in tables_o)
    plat += b"".join(struct.pack("<2I", l, p) for l, p in tables_t)
    with open(chemin, "wb") as f:
        f.write(tete + plat + corps)


def principal():
    base = os.path.join(MIROIR, "fr_FR.mo")
    if not os.path.exists(base):
        raise SystemExit("miroir des traductions absent : %s" % base)
    entrees = lire_mo(base)
    #  Le pack « admin » officiel par-dessus : il porte l'essentiel des
    #  libellés de l'écran des extensions.
    admin = lire_mo(os.path.join(MIROIR, "admin-fr_FR.mo"))
    admin.pop(b"", None)
    entrees.update(admin)

    avant = len(entrees)
    for msgid, msgstr in TRADUCTIONS.items():
        entrees[msgid.encode()] = msgstr.encode()
    for (u, d), (tu, td) in PLURIELS.items():
        entrees[u.encode() + NUL + d.encode()] = tu.encode() + NUL + td.encode()

    os.makedirs(os.path.dirname(CIBLE), exist_ok=True)
    ecrire_mo(CIBLE, entrees)

    #  On relit ce qu'on vient d'écrire : un catalogue mal formé ne se voit pas
    #  autrement qu'en constatant l'anglais sur la capture, trop tard.
    relu = lire_mo(CIBLE)
    manquants = [m for m in TRADUCTIONS if m.encode() not in relu]
    if manquants:
        raise SystemExit("chaînes absentes du fichier écrit : %s"
                         % manquants[:3])
    print("  %d entrées (%d du miroir officiel, %d recalées ici)"
          % (len(relu), avant, len(TRADUCTIONS) + len(PLURIELS)))
    print("  -> %s" % CIBLE)


if __name__ == "__main__":
    sys.exit(principal())
