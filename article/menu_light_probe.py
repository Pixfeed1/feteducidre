"""
IMAGE 2 de l'article — les trois sondes, anciens et nouveaux noms.

    python3 article/menu_light_probe.py

Produit `article/light-probes-anciens-nouveaux-noms.webp`.

----------------------------------------------------------------------------
CE QUE CETTE IMAGE EST, ET CE QU'ELLE N'EST PAS
----------------------------------------------------------------------------
Ce n'est pas une capture d'écran : c'est une RECONSTRUCTION du menu.

La session qui a produit ce fichier n'a pas d'interface graphique — le module
`bpy` est sans fenêtre par construction, il n'y a donc aucun écran à capturer.
En revanche les libellés ne sont pas recopiés de mémoire : ils sont LUS dans
le Blender installé, à la même source que celle où le menu les prend.

    >>> layout.operator_enum("object.lightprobe_add", "type")

Le menu Add ▸ Light Probe ne contient rien d'autre que l'énumération `type`
de `LightProbe`. Les trois libellés affichés ici viennent donc directement de
`bpy.types.LightProbe.bl_rna.properties['type'].enum_items`, relevés au
moment de la fabrication de l'image. Si Blender les renomme, l'image se
corrige d'elle-même au prochain lancement.

----------------------------------------------------------------------------
LA VERSION, QUI N'EST PAS CELLE QU'ON CROIT
----------------------------------------------------------------------------
Le renommage est arrivé en **Blender 4.1**, pas en 4.2.

C'est contre-intuitif parce qu'on associe naturellement les nouveaux noms à
EEVEE Next, qui n'est arrivé qu'en **4.2**. Il y a donc eu une version
entière — la 4.1 — où le menu affichait déjà « Sphere / Plane / Volume »
alors que le moteur était encore EEVEE Legacy.

Vérifié dans les notes de version 4.1 d'EEVEE :
« probe types have been renamed: Reflection Cubemap to Sphere, Reflection
Plane to Plane, and Irradiance Grid to Volume ».

Les anciens libellés du menu, eux, étaient « Reflection Cubemap »,
« Reflection Plane » et « Irradiance Volume » — c'est sous ce dernier nom que
le manuel a documenté la sonde de volume pendant six versions.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

RACINE = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(RACINE, "light-probes-anciens-nouveaux-noms.webp")

L, H = 1600, 900
QUALITE = 92

FOND = (13, 13, 17)
PANNEAU = (43, 43, 43)              # le gris des menus de Blender
PANNEAU_BORD = (24, 24, 24)
PANNEAU_TETE = (33, 33, 33)
BLANC = (232, 232, 236)
GRIS = (138, 138, 150)
GRIS_SOMBRE = (96, 96, 106)
TEAL = (72, 224, 184)
ROUGE = (214, 118, 96)
BLEU_SEL = (71, 114, 179)           # le bleu de sélection de Blender

POLICE_G = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
POLICE_R = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
POLICE_M = "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf"

#  Les anciens libellés, dans le même ordre que l'énumération actuelle.
#  Ils ne peuvent pas être relevés dans le Blender installé — ils n'y sont
#  plus. Ils viennent des notes de version 4.1 et du manuel des versions 2.8
#  à 4.0, et c'est la seule partie de cette image qui repose sur une source
#  extérieure plutôt que sur l'exécutable lui-même.
ANCIENS = {
    "SPHERE": "Reflection Cubemap",
    "PLANE": "Reflection Plane",
    "VOLUME": "Irradiance Volume",
}
#  Le renommage n'a pas touché que les libellés : les identifiants de l'API
#  Python ont changé aussi. C'est LA raison pour laquelle un ancien script
#  ou un ancien fichier perd ses repères — un libellé qui change se relit,
#  un identifiant qui change lève une exception.
ANCIENS_API = {
    "SPHERE": "CUBEMAP",
    "PLANE": "PLANAR",
    "VOLUME": "GRID",
}
VERSION_RENOMMAGE = "4.1"
VERSION_EEVEE_NEXT = "4.2"


def police(chemin, taille):
    try:
        return ImageFont.truetype(chemin, taille)
    except OSError:
        return ImageFont.load_default()


def libelles_actuels():
    """
    Les trois entrées, lues dans Blender — pas recopiées.

    Le menu Add ▸ Light Probe est un `operator_enum` sur la propriété `type`
    de LightProbe : ce que renvoie cette fonction EST, au caractère près, ce
    que Blender affiche.
    """
    try:
        import bpy
        items = bpy.types.LightProbe.bl_rna.properties["type"].enum_items
        return ([(e.identifier, e.name) for e in items],
                bpy.app.version_string)
    except ImportError:
        raise SystemExit(
            "bpy introuvable — les libellés seraient recopiés de mémoire,\n"
            "        ce qui est exactement ce que cette image doit éviter.\n"
            "        `pip install bpy==4.5.12`")


# ---------------------------------------------------------------------------
#  LES TROIS PICTOGRAMMES
# ---------------------------------------------------------------------------
#  Dessinés, pas extraits. Les icônes de Blender sont dans un atlas interne
#  qu'on ne peut pas lire depuis `bpy`. On redessine donc trois glyphes qui
#  disent la même chose : un point, une surface, un volume.

def icone(d, cle, x, y, t, teinte):
    r = t / 2.0
    cx, cy = x + r, y + r
    if cle == "SPHERE":
        d.ellipse([cx - r * 0.78, cy - r * 0.78, cx + r * 0.78,
                   cy + r * 0.78], outline=teinte, width=2)
        d.ellipse([cx - r * 0.30, cy - r * 0.52, cx - r * 0.02,
                   cy - r * 0.24], fill=teinte)
    elif cle == "PLANE":
        #  une surface vue de biais, plus son axe de réflexion
        d.polygon([(cx - r * 0.85, cy + r * 0.28),
                   (cx - r * 0.25, cy - r * 0.42),
                   (cx + r * 0.85, cy - r * 0.42),
                   (cx + r * 0.25, cy + r * 0.28)],
                  outline=teinte)
        d.line([cx, cy + r * 0.34, cx, cy + r * 0.82], fill=teinte, width=2)
    else:
        #  un volume, et les points d'échantillonnage qu'il contient
        d.rectangle([cx - r * 0.82, cy - r * 0.82, cx + r * 0.82,
                     cy + r * 0.82], outline=teinte, width=2)
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                px, py = cx + i * r * 0.44, cy + j * r * 0.44
                d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=teinte)


# ---------------------------------------------------------------------------

def panneau(d, x, y, l, h, tete, actif):
    """Un panneau de menu à la manière de Blender : coins légèrement
    arrondis, en-tête plus sombre, bord franc."""
    fond = PANNEAU if actif else (30, 30, 33)
    bord = PANNEAU_BORD if actif else (44, 44, 50)
    d.rounded_rectangle([x, y, x + l, y + h], 8, fill=fond, outline=bord,
                        width=2)
    d.rounded_rectangle([x, y, x + l, y + 46], 8,
                        fill=PANNEAU_TETE if actif else (26, 26, 29))
    d.rectangle([x, y + 34, x + l, y + 46],
                fill=PANNEAU_TETE if actif else (26, 26, 29))
    d.line([x + 1, y + 46, x + l - 1, y + 46], fill=bord, width=1)
    return tete


def principal():
    entrees, version = libelles_actuels()
    im = Image.new("RGB", (L, H), FOND)
    d = ImageDraw.Draw(im, "RGBA")

    f_titre = police(POLICE_G, 40)
    f_chemin = police(POLICE_G, 27)
    f_menu = police(POLICE_R, 30)
    f_tete = police(POLICE_G, 22)
    f_note = police(POLICE_R, 24)
    f_puce = police(POLICE_G, 21)

    # -- le titre ----------------------------------------------------------
    d.text((70, 56), "Trois objets, trois nouveaux noms", font=f_titre,
           fill=BLANC)

    # -- les deux panneaux --------------------------------------------------
    PY, PH = 232, 300
    AX, AL = 92, 560                     # l'encart des anciens noms
    NX, NL = 872, 636                    # le menu actuel

    panneau(d, AX, PY, AL, PH, "", actif=False)
    panneau(d, NX, PY, NL, PH, "", actif=True)

    d.text((AX + 22, PY + 13), "JUSQU'À BLENDER 4.0   ·   EEVEE LEGACY",
           font=f_tete, fill=GRIS_SOMBRE)
    #  Le chevron est DESSINÉ, pas écrit : Liberation Sans n'a pas U+25B8 et
    #  le rendait en carré vide.
    d.text((NX + 22, PY + 13), "ADD", font=f_tete, fill=GRIS)
    cx = NX + 22 + d.textlength("ADD", font=f_tete) + 14
    cy = PY + 24
    d.polygon([(cx, cy - 6), (cx + 9, cy), (cx, cy + 6)], fill=GRIS)
    d.text((cx + 22, PY + 13), "LIGHT PROBE", font=f_tete, fill=GRIS)
    lt = cx + 22 + d.textlength("LIGHT PROBE", font=f_tete)
    d.text((lt + 26, PY + 13), "BLENDER %s +" % VERSION_RENOMMAGE,
           font=f_tete, fill=TEAL)

    # -- les trois lignes, alignées deux à deux ----------------------------
    y = PY + 78
    PAS = 76
    for i, (cle, nom) in enumerate(entrees):
        yl = y + i * PAS

        #  l'ancien nom, barré
        ancien = ANCIENS.get(cle, "?")
        d.text((AX + 30, yl), ancien, font=f_menu, fill=GRIS_SOMBRE)
        la = d.textlength(ancien, font=f_menu)
        #  À hauteur d'x, pas sur la ligne de base : une rature posée trop
        #  bas se lit comme un soulignement et coupe les jambages.
        yr = yl + 13
        d.line([AX + 26, yr, AX + 34 + la, yr], fill=ROUGE, width=3)

        #  la flèche
        fx0, fx1 = AX + AL + 44, NX - 44
        fy = yl + 20
        d.line([fx0, fy, fx1 - 12, fy], fill=(78, 78, 90), width=2)
        d.polygon([(fx1, fy), (fx1 - 15, fy - 8), (fx1 - 15, fy + 8)],
                  fill=(120, 120, 134))

        #  la ligne de menu : la première est surlignée, comme un menu
        #  réellement ouvert sous le curseur
        if i == 0:
            d.rounded_rectangle([NX + 8, yl - 12, NX + NL - 8, yl + 52], 4,
                                fill=BLEU_SEL)
        icone(d, cle, NX + 26, yl - 4, 42,
              BLANC if i == 0 else (196, 196, 200))
        d.text((NX + 88, yl), nom, font=f_menu, fill=BLANC)

    # -- la moitié basse : deux blocs, pas un bloc et du vide --------------
    yn = PY + PH + 56
    d.line([70, yn, L - 70, yn], fill=(40, 40, 48), width=1)
    MX = 812                               # la césure entre les deux blocs

    #  À GAUCHE : la version, qui n'est pas celle qu'on croit
    d.rectangle([70, yn + 32, 78, yn + 58], fill=TEAL)
    d.text((94, yn + 28),
           "Le renommage date de Blender %s, pas de %s."
           % (VERSION_RENOMMAGE, VERSION_EEVEE_NEXT),
           font=f_puce, fill=BLANC)
    for i, ligne in enumerate((
            "Une version entière a affiché « Sphere / Plane / Volume »",
            "alors que le moteur était encore EEVEE Legacy :",
            "EEVEE Next n'est arrivé qu'en %s." % VERSION_EEVEE_NEXT)):
        d.text((94, yn + 66 + i * 31), ligne, font=f_note, fill=GRIS)

    #  À DROITE : l'API, la vraie cause des fichiers qui perdent leurs
    #  repères. Un libellé qui change se relit ; un identifiant qui change
    #  lève une exception.
    d.rectangle([MX, yn + 32, MX + 8, yn + 58], fill=ROUGE)
    d.text((MX + 24, yn + 28), "Les identifiants Python ont changé aussi.",
           font=f_puce, fill=BLANC)
    f_mono = police(POLICE_M, 23)
    for i, (cle, _nom) in enumerate(entrees):
        ya = yn + 70 + i * 30
        av = "type='%s'" % ANCIENS_API.get(cle, "?")
        ap = "type='%s'" % cle
        d.text((MX + 24, ya), av, font=f_mono, fill=GRIS_SOMBRE)
        lv = d.textlength(av, font=f_mono)
        d.line([MX + 22, ya + 13, MX + 26 + lv, ya + 13], fill=ROUGE,
               width=2)
        fx = MX + 44 + lv
        d.polygon([(fx + 16, ya + 13), (fx + 4, ya + 6), (fx + 4, ya + 20)],
                  fill=(120, 120, 134))
        d.text((fx + 34, ya), ap, font=f_mono, fill=TEAL)

    #  La mention de provenance : elle doit être SUR l'image, pas seulement
    #  dans la légende. Une image technique qui ne dit pas d'où viennent ses
    #  libellés demande une confiance qu'elle n'a pas méritée.
    f_prov = police(POLICE_R, 19)
    prov = ("Libellés et identifiants actuels relevés dans Blender %s, à la "
            "source même du menu : LightProbe.bl_rna.properties['type']"
            % version)
    d.text((L - 70 - d.textlength(prov, font=f_prov), H - 46), prov,
           font=f_prov, fill=(74, 74, 84))

    im.save(SORTIE, "WEBP", quality=QUALITE, method=6)
    print()
    print("  %d × %d" % im.size)
    for cle, nom in entrees:
        print("  %-22s  ->  %s" % (ANCIENS.get(cle, "?"), nom))
    print("  libellés lus dans Blender %s" % version)
    print("  %s  (%.0f Ko)"
          % (os.path.basename(SORTIE), os.path.getsize(SORTIE) / 1024))


if __name__ == "__main__":
    principal()
