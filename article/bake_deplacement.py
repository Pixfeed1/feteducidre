"""
IMAGE — le bouton « Bake Indirect Lighting » a déménagé.

    python3 article/bake_deplacement.py

Produit `article/bake-indirect-lighting-nouvel-emplacement.webp`.

----------------------------------------------------------------------------
POURQUOI LES DEUX PANNEAUX SONT RECONSTRUITS
----------------------------------------------------------------------------
Le panneau de gauche N'EXISTE PLUS. « Indirect Lighting » appartenait à EEVEE
Legacy, retiré en 4.2 : personne ne peut plus le photographier sans
réinstaller une version antérieure. Le reconstruire n'est donc pas un pis-
aller, c'est la seule façon de le montrer.

Celui de droite existe, lui — mais deux panneaux côte à côte dont l'un serait
photographié et l'autre dessiné ne se compareraient pas : deux rendus de
texte différents, deux échelles, deux compressions. On les dessine tous les
deux, à la même échelle, avec les mêmes données.

Et ces données viennent de Blender :

  - les couleurs, lues dans le thème (`wcol_tool`, `panelcolors`) ;
  - la police, Inter, extraite du paquet bpy ;
  - les libellés actuels, lus dans les classes d'interface elles-mêmes.

----------------------------------------------------------------------------
CE QUI A ÉTÉ VÉRIFIÉ, ET COMMENT
----------------------------------------------------------------------------
Relevé dans les sources d'interface de Blender 4.5 :

    properties_scene.py, classe SCENE_PT_eevee_next_light_probes
        bl_label = "Light Probes"
        bl_options = {'DEFAULT_CLOSED'}
        row.operator("object.lightprobe_cache_bake",
                     text="Bake All Light Probe Volumes").subset = 'ALL'

    properties_data_lightprobe.py, classe DATA_PT_lightprobe_bake
        bl_label = "Bake"
        row.operator("object.lightprobe_cache_bake").subset = 'ACTIVE'

Le `DEFAULT_CLOSED` explique à lui seul la moitié des « le bouton a
disparu » : le panneau est REPLIÉ au premier lancement.

L'ancien opérateur, lui, a bel et bien été retiré :

    >>> bpy.ops.scene.light_cache_bake.get_rna_type()
    KeyError: 'get_rna_type("SCENE_OT_light_cache_bake") not found'

Attention au piège de vérification : `hasattr(bpy.ops.scene, "x")` répond
TOUJOURS vrai — `bpy.ops` fabrique un objet pour n'importe quel nom sans
vérifier qu'il existe. Je m'y suis laissé prendre une première fois et j'ai
failli écrire le contraire. Seul `get_rna_type()` dit la vérité.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

RACINE = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(RACINE, "bake-indirect-lighting-nouvel-emplacement.webp")
POLICE_BLENDER = os.path.join(RACINE, "polices", "Inter-Blender.ttf")
POLICE_G = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
POLICE_R = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
POLICE_M = "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf"

L, H = 1600, 900
QUALITE = 92

FOND = (13, 13, 17)
BLANC = (232, 232, 236)
GRIS = (138, 138, 150)
GRIS_SOMBRE = (96, 96, 106)
TEAL = (72, 224, 184)
ROUGE = (214, 118, 96)

#  Blender pose toute son interface sur UI_UNIT_Y = 20 px à l'échelle 1.
UI_UNIT = 20.0
#  2,0 et non 2,6 : à 2,6 le panneau de gauche, avec ses six rangées,
#  descendait dans le bloc de notes. On ne règle pas une échelle
#  d'interface sans regarder ce qu'il y a en dessous.
ECHELLE_UI = 2.0

VERSION_RETRAIT = "4.2"        # la version qui a retiré EEVEE Legacy


def police(chemin, taille):
    try:
        return ImageFont.truetype(chemin, taille)
    except OSError:
        return ImageFont.load_default()


def theme():
    """Couleurs de l'éditeur de propriétés et des widgets, lues dans le
    thème plutôt qu'estimées à l'œil."""
    import bpy
    t = bpy.context.preferences.themes[0]
    pr, ui = t.properties.space, t.user_interface
    o = bpy.context.preferences.ui_styles[0].widget

    def px(v):
        return tuple(int(round(x * 255)) for x in tuple(v)[:3])

    return {
        "editeur": px(pr.back),
        "panneau": px(pr.panelcolors.back),
        "entete": px(pr.panelcolors.header),
        "texte": px(pr.text),
        "bouton": px(ui.wcol_tool.inner),
        "bouton_bord": px(ui.wcol_tool.outline),
        "bouton_texte": px(ui.wcol_tool.text),
        "champ": px(ui.wcol_numslider.inner),
        "arrondi": ui.wcol_tool.roundness,
        "points": o.points,
    }


def libelles():
    """
    Les libellés actuels, LUS DANS LES CLASSES D'INTERFACE de Blender.

    On ne recopie pas : on ouvre le module qui dessine le panneau et on y
    relève le texte du bouton. Si Blender le renomme, l'image suit.
    """
    import bpy
    base = os.path.join(bpy.utils.resource_path("LOCAL"), "scripts",
                        "startup", "bl_ui")
    import re
    out = {}
    src = open(os.path.join(base, "properties_scene.py"),
               encoding="utf-8").read()
    m = re.search(r'operator\("object\.lightprobe_cache_bake",\s*'
                  r'text="([^"]+)"\)', src)
    out["scene_bouton"] = m.group(1) if m else "Bake All Light Probe Volumes"
    m = re.search(r'class SCENE_PT_eevee_next_light_probes[\s\S]*?'
                  r'bl_label = "([^"]+)"', src)
    out["scene_panneau"] = m.group(1) if m else "Light Probes"
    out["scene_replie"] = "DEFAULT_CLOSED" in src[src.index(
        "class SCENE_PT_eevee_next_light_probes"):][:400]

    src = open(os.path.join(base, "properties_data_lightprobe.py"),
               encoding="utf-8").read()
    m = re.search(r'class DATA_PT_lightprobe_bake\b[\s\S]*?'
                  r'bl_label = "([^"]+)"', src)
    out["objet_panneau"] = m.group(1) if m else "Bake"
    #  Le bouton par sonde n'a pas de `text=` : il affiche le nom de
    #  l'opérateur lui-même.
    out["objet_bouton"] = bpy.ops.object.lightprobe_cache_bake \
        .get_rna_type().name
    out["version"] = bpy.app.version_string

    #  L'ancien opérateur existe-t-il encore ? `hasattr` mentirait.
    try:
        bpy.ops.scene.light_cache_bake.get_rna_type()
        out["ancien_present"] = True
    except KeyError:
        out["ancien_present"] = False
    return out


# ---------------------------------------------------------------------------
#  LES MORCEAUX D'INTERFACE
# ---------------------------------------------------------------------------

def triangle(d, x, y, t, couleur, ouvert=True):
    if ouvert:
        d.polygon([(x, y - t * 0.32), (x + t * 0.62, y - t * 0.32),
                   (x + t * 0.31, y + t * 0.30)], fill=couleur)
    else:
        d.polygon([(x + t * 0.10, y - t * 0.40),
                   (x + t * 0.10, y + t * 0.40),
                   (x + t * 0.62, y)], fill=couleur)


def panneau(im, d, th, x, y, l, titre, lignes, e=ECHELLE_UI, replie=False):
    """
    Un panneau de l'éditeur de propriétés : un en-tête avec son triangle,
    puis des lignes. `lignes` est une liste de tuples décrivant chaque rangée.
    """
    u = UI_UNIT * e
    f = police(POLICE_BLENDER, int(round(th["points"] * e)))
    fg = police(POLICE_BLENDER, int(round(th["points"] * e)))
    r = th["arrondi"] * 0.5 * u

    h_entete = u * 1.2
    h = h_entete + (0 if replie else u * 0.4 + len(lignes) * u * 1.35
                    + u * 0.3)

    d.rounded_rectangle([x, y, x + l, y + h], r * 0.8, fill=th["panneau"])
    d.rounded_rectangle([x, y, x + l, y + h_entete], r * 0.8,
                        fill=th["entete"])
    d.rectangle([x, y + h_entete - r, x + l, y + h_entete], fill=th["entete"])
    triangle(d, x + u * 0.35, y + h_entete / 2, u * 0.55, th["texte"],
             not replie)
    bb = fg.getbbox(titre)
    d.text((x + u * 1.15, y + (h_entete - (bb[3] - bb[1])) / 2 - bb[1]),
           titre, font=fg, fill=th["texte"])

    if replie:
        return h

    yl = y + h_entete + u * 0.4
    boutons = {}
    for ligne in lignes:
        genre = ligne[0]
        hl = u * 1.35
        if genre == "bouton":
            _, texte = ligne
            bx0, bx1 = x + u * 0.5, x + l - u * 0.5
            d.rounded_rectangle([bx0, yl, bx1, yl + u * 1.1], r,
                                fill=th["bouton"], outline=th["bouton_bord"])
            bb = f.getbbox(texte)
            d.text((bx0 + (bx1 - bx0 - f.getlength(texte)) / 2,
                    yl + (u * 1.1 - (bb[3] - bb[1])) / 2 - bb[1]),
                   texte, font=f, fill=th["bouton_texte"])
            boutons[texte] = (bx0, yl, bx1, yl + u * 1.1)
        elif genre == "bouton_corbeille":
            _, texte = ligne
            bx0, bx1 = x + u * 0.5, x + l - u * 2.1
            d.rounded_rectangle([bx0, yl, bx1, yl + u * 1.1], r,
                                fill=th["bouton"], outline=th["bouton_bord"])
            bb = f.getbbox(texte)
            d.text((bx0 + (bx1 - bx0 - f.getlength(texte)) / 2,
                    yl + (u * 1.1 - (bb[3] - bb[1])) / 2 - bb[1]),
                   texte, font=f, fill=th["bouton_texte"])
            boutons[texte] = (bx0, yl, bx1, yl + u * 1.1)
            cx0 = x + l - u * 1.9
            d.rounded_rectangle([cx0, yl, x + l - u * 0.5, yl + u * 1.1], r,
                                fill=th["bouton"], outline=th["bouton_bord"])
            corbeille(d, cx0 + u * 0.42, yl + u * 0.28, u * 0.55,
                      th["bouton_texte"])
        elif genre == "champ":
            _, etiquette, valeur = ligne
            mx = x + l * 0.46
            bb = f.getbbox(etiquette)
            d.text((mx - u * 0.35 - f.getlength(etiquette),
                    yl + (u * 1.1 - (bb[3] - bb[1])) / 2 - bb[1]),
                   etiquette, font=f, fill=th["texte"])
            d.rounded_rectangle([mx, yl, x + l - u * 0.5, yl + u * 1.1], r,
                                fill=th["champ"])
            bb = f.getbbox(valeur)
            d.text((mx + (x + l - u * 0.5 - mx - f.getlength(valeur)) / 2,
                    yl + (u * 1.1 - (bb[3] - bb[1])) / 2 - bb[1]),
                   valeur, font=f, fill=th["texte"])
        elif genre == "case":
            _, etiquette, coche = ligne
            mx = x + l * 0.46
            d.rounded_rectangle([mx, yl + u * 0.16, mx + u * 0.78,
                                 yl + u * 0.94], r * 0.5,
                                fill=(71, 114, 179) if coche
                                else th["champ"])
            bb = f.getbbox(etiquette)
            d.text((mx + u * 1.1,
                    yl + (u * 1.1 - (bb[3] - bb[1])) / 2 - bb[1]),
                   etiquette, font=f, fill=th["texte"])
        yl += hl
    return h, boutons


def corbeille(d, x, y, t, c):
    d.rectangle([x + t * 0.16, y + t * 0.22, x + t * 0.84, y + t * 1.0],
                outline=c, width=2)
    d.line([x, y + t * 0.18, x + t, y + t * 0.18], fill=c, width=2)
    d.line([x + t * 0.36, y + t * 0.06, x + t * 0.64, y + t * 0.06],
           fill=c, width=2)


def cerne(d, boite, couleur, marge=10, epaisseur=4):
    """L'entourage du bouton. Un ovale, pas un rectangle : un rectangle se
    confond avec les bords des widgets de Blender, un ovale se lit tout de
    suite comme une annotation posée par-dessus."""
    x0, y0, x1, y1 = boite
    d.ellipse([x0 - marge, y0 - marge, x1 + marge, y1 + marge],
              outline=couleur, width=epaisseur)


# ---------------------------------------------------------------------------

def principal():
    th, lb = theme(), libelles()
    im = Image.new("RGB", (L, H), FOND)
    d = ImageDraw.Draw(im, "RGBA")

    f_titre = police(POLICE_G, 40)
    f_tete = police(POLICE_G, 22)
    f_note = police(POLICE_R, 24)
    f_puce = police(POLICE_G, 21)

    d.text((70, 50), "Le bouton n'a pas disparu, il a déménagé",
           font=f_titre, fill=BLANC)

    PY = 176
    AX, AL = 70, 600            # l'ancien panneau
    NX, NL = 930, 600           # le nouveau

    d.rectangle([AX, PY - 50, AX + 8, PY - 24], fill=ROUGE)
    d.text((AX + 24, PY - 54), "JUSQU'À BLENDER 4.1   ·   RENDER PROPERTIES",
           font=f_tete, fill=GRIS_SOMBRE)
    d.rectangle([NX, PY - 50, NX + 8, PY - 24], fill=TEAL)
    d.text((NX + 24, PY - 54), "DEPUIS %s   ·   SCENE PROPERTIES"
           % VERSION_RETRAIT, font=f_tete, fill=BLANC)

    #  L'ANCIEN — retiré de Blender, donc impossible à photographier.
    _, anciens = panneau(im, d, th, AX, PY, AL, "Indirect Lighting", [
        ("bouton", "Bake Indirect Lighting"),
        ("bouton", "Bake Cubemap Only"),
        ("bouton", "Delete Lighting Cache"),
        ("case", "Auto Bake", False),
    ])
    #  Quatre rangées, pas six : « Diffuse Bounces » et « Cubemap Size »
    #  allongeaient le panneau sans rien apporter à la démonstration, qui
    #  porte sur l'emplacement d'un bouton.

    #  LE NOUVEAU — relevé dans les sources d'interface de la 4.5.
    _, nouveaux = panneau(im, d, th, NX, PY, NL, lb["scene_panneau"], [
        ("champ", "Spheres Resolution", "512 px"),
        ("bouton_corbeille", lb["scene_bouton"]),
    ])

    b_ancien = anciens["Bake Indirect Lighting"]
    b_nouveau = nouveaux[lb["scene_bouton"]]
    cerne(d, b_ancien, ROUGE)
    cerne(d, b_nouveau, TEAL)

    #  La flèche, d'un cerne à l'autre
    y0 = (b_ancien[1] + b_ancien[3]) / 2
    y1 = (b_nouveau[1] + b_nouveau[3]) / 2
    fx0, fx1 = AX + AL + 62, NX - 62
    d.line([fx0, y0, fx1 - 16, y1], fill=(96, 96, 110), width=3)
    d.polygon([(fx1, y1), (fx1 - 19, y1 - 11), (fx1 - 19, y1 + 11)],
              fill=(140, 140, 154))

    # -- les trois choses à savoir ----------------------------------------
    yn = 560
    d.line([70, yn, L - 70, yn], fill=(40, 40, 48), width=1)

    d.rectangle([70, yn + 32, 78, yn + 58], fill=TEAL)
    d.text((94, yn + 28), "Le panneau est REPLIÉ par défaut.", font=f_puce,
           fill=BLANC)
    for i, l in enumerate((
            "C'est la moitié des « le bouton a disparu » :",
            "il faut déplier « %s »" % lb["scene_panneau"],
            "pour le voir.")):
        d.text((94, yn + 66 + i * 30), l, font=f_note, fill=GRIS)

    MX = 610
    d.rectangle([MX, yn + 32, MX + 8, yn + 58], fill=TEAL)
    d.text((MX + 24, yn + 28), "Il y a un SECOND endroit.", font=f_puce,
           fill=BLANC)
    for i, l in enumerate((
            "Sonde sélectionnée → Object Data Properties",
            "→ panneau « %s » → « %s »" % (lb["objet_panneau"],
                                           lb["objet_bouton"]),
            "pour ne cuire que celle-là.")):
        d.text((MX + 24, yn + 66 + i * 30), l, font=f_note, fill=GRIS)

    MX2 = 1140
    d.rectangle([MX2, yn + 32, MX2 + 8, yn + 58], fill=ROUGE)
    d.text((MX2 + 24, yn + 28), "L'opérateur Python a changé.", font=f_puce,
           fill=BLANC)
    f_mono = police(POLICE_M, 21)
    av = "scene.light_cache_bake"
    d.text((MX2 + 24, yn + 70), av, font=f_mono, fill=GRIS_SOMBRE)
    lv = d.textlength(av, font=f_mono)
    d.line([MX2 + 22, yn + 82, MX2 + 28 + lv, yn + 82], fill=ROUGE, width=2)
    d.text((MX2 + 24, yn + 100), "object.lightprobe_cache_bake",
           font=f_mono, fill=TEAL)
    d.text((MX2 + 24, yn + 126), "subset='ALL'", font=f_mono, fill=TEAL)

    f_prov = police(POLICE_R, 19)
    #  Deux lignes, pas une : la mention tenait sur 1 540 px et se faisait
    #  couper par le bord droit.
    for i, ligne in enumerate((
            "Panneaux redessinés avec le thème et la police de Blender %s ; "
            "libellés actuels lus dans ses classes d'interface." % lb["version"],
            "Le panneau de gauche a été retiré de Blender en %s : il n'est "
            "plus photographiable." % VERSION_RETRAIT)):
        d.text((70, H - 66 + i * 26), ligne, font=f_prov,
               fill=(74, 74, 84))

    im.save(SORTIE, "WEBP", quality=QUALITE, method=6)
    print()
    print("  %d x %d" % im.size)
    print("  ancien  : Render Properties > Indirect Lighting > "
          "Bake Indirect Lighting")
    print("  nouveau : Scene Properties > %s > %s%s"
          % (lb["scene_panneau"], lb["scene_bouton"],
             "  (replié par défaut)" if lb["scene_replie"] else ""))
    print("  par sonde : Object Data > %s > %s"
          % (lb["objet_panneau"], lb["objet_bouton"]))
    print("  scene.light_cache_bake encore present : %s"
          % lb["ancien_present"])
    print("  %s  (%.0f Ko)"
          % (os.path.basename(SORTIE), os.path.getsize(SORTIE) / 1024))


if __name__ == "__main__":
    principal()
