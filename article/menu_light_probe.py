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

from PIL import Image, ImageDraw, ImageFilter, ImageFont

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

#  LA POLICE DE BLENDER, LA VRAIE.
#
#  Le paquet `bpy` embarque les fichiers de données de Blender, dont sa
#  police d'interface : Inter. On la convertit une fois du woff2 vers le ttf
#  (voir extraire_inter.py) et on dessine le menu avec — plus aucune raison
#  d'approximer avec une Helvetica de substitution.
POLICE_BLENDER = os.path.join(RACINE, "polices", "Inter-Blender.ttf")

#  L'ÉCHELLE DU MENU RECONSTRUIT.
#
#  Blender pose toute son interface sur UI_UNIT_Y = 20 px à l'échelle 1 :
#  une ligne de menu fait 20 px de haut, une icône 16, le texte 11 points.
#  À l'échelle 1 le menu ferait 200 px de large dans une image de 1600 —
#  illisible. On le dessine donc à l'échelle 3, exactement comme Blender le
#  dessinerait sur un écran à forte densité.
ECHELLE_UI = 3.0
UI_UNIT = 20.0

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

#  --capture <png> : monte une VRAIE capture d'écran à la place du menu
#  redessiné. Le fichier se produit avec `capturer_menu.py`, sur un poste
#  doté d'une interface graphique. Tout le reste de la mise en page — les
#  anciens noms barrés, la note de version, le renommage de l'API — est
#  strictement identique dans les deux cas.
CAPTURE = (sys.argv[sys.argv.index("--capture") + 1]
           if "--capture" in sys.argv else None)


def police(chemin, taille):
    try:
        return ImageFont.truetype(chemin, taille)
    except OSError:
        return ImageFont.load_default()


def theme_de_blender():
    """
    Les couleurs du menu, LUES DANS LE THÈME de Blender.

    Elles étaient jusqu'ici recopiées à l'œil, et fausses : le fond d'un menu
    vaut 24, 24, 24 et non 43, 43, 43 comme je l'avais estimé. Un aplat trop
    clair de vingt niveaux, c'est ce qui fait qu'une reconstruction « sent »
    la reconstruction sans qu'on sache dire pourquoi.
    """
    import bpy
    t = bpy.context.preferences.themes[0].user_interface
    o = bpy.context.preferences.ui_styles[0].widget

    def px(v):
        return tuple(int(round(x * 255)) for x in tuple(v)[:3])

    return {
        "fond": px(t.wcol_menu_back.inner),
        "bord": px(t.wcol_menu_back.outline),
        "titre": px(t.wcol_menu_back.text),
        "texte": px(t.wcol_menu_item.text),
        "texte_sel": px(t.wcol_menu_item.text_sel),
        "selection": px(t.wcol_menu_item.inner_sel),
        "arrondi": t.wcol_menu_back.roundness,
        "arrondi_item": t.wcol_menu_item.roundness,
        "ombre": t.menu_shadow_fac,
        "ombre_largeur": t.menu_shadow_width,
        "points": o.points,
    }


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

def menu_blender(im, entrees, th, x, y, e=ECHELLE_UI):
    """
    Le menu, redessiné aux conventions de Blender.

    Toute la géométrie de l'interface de Blender se déduit d'une seule unité,
    UI_UNIT_Y = 20 px à l'échelle 1 : une ligne de menu fait une unité de
    haut, une icône en fait 16/20, le texte 11 points. On applique donc
    exactement ce barème, multiplié par l'échelle voulue, plutôt que de
    choisir des hauteurs à l'œil.

    Retourne le rectangle occupé, ombre comprise.
    """
    u = UI_UNIT * e
    #  Blender rend son interface à 72 ppp : un point vaut donc exactement
    #  un pixel à l'échelle 1. La taille du texte est « points × échelle »,
    #  sans autre facteur — j'en avais glissé un de 1,34 en croyant à du
    #  96 ppp, et le texte débordait de sa ligne.
    police_menu = police(POLICE_BLENDER, int(round(th["points"] * e)))

    marge_x = 0.30 * u                 # retrait du texte et des icônes
    icone_t = 16.0 / 20.0 * u
    ecart = 0.42 * u                   # entre l'icône et le libellé

    largeur = max(police_menu.getlength(n) for _c, n in entrees)
    L_menu = marge_x + icone_t + ecart + largeur + 1.4 * u
    L_menu = max(L_menu, 7.0 * u)
    H_menu = u * (len(entrees) + 1) + 0.5 * u        # + la ligne de titre

    r = th["arrondi"] * 0.5 * u
    ri = th["arrondi_item"] * 0.5 * u

    #  L'OMBRE PORTÉE. Blender en dessine une sous chaque menu ; sans elle
    #  le panneau a l'air collé au fond au lieu de flotter au-dessus.
    ombre = Image.new("RGBA", (int(L_menu) + 80, int(H_menu) + 80), (0, 0, 0, 0))
    do = ImageDraw.Draw(ombre)
    do.rounded_rectangle([40, 44, 40 + L_menu, 44 + H_menu], r,
                         fill=(0, 0, 0, int(255 * th["ombre"])))
    ombre = ombre.filter(ImageFilter.GaussianBlur(th["ombre_largeur"] * e))
    im.paste(ombre, (int(x) - 40, int(y) - 40), ombre)

    d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle([x, y, x + L_menu, y + H_menu], r,
                        fill=th["fond"], outline=th["bord"],
                        width=max(1, int(e * 0.6)))

    #  La ligne de titre : c'est ce qu'affiche `wm.call_menu`, donc ce que
    #  produira aussi la vraie capture. Les deux chemins doivent montrer la
    #  même chose.
    bb = police_menu.getbbox("Light Probe")
    d.text((x + marge_x + icone_t + ecart,
            y + (u - (bb[3] - bb[1])) / 2.0 - bb[1] + 0.10 * u),
           "Light Probe", font=police_menu, fill=th["titre"])

    y0 = y + u
    for i, (cle, nom) in enumerate(entrees):
        yl = y0 + i * u
        if i == 0:                      # la ligne sous le curseur
            d.rounded_rectangle([x + 0.12 * u, yl, x + L_menu - 0.12 * u,
                                 yl + u], ri, fill=th["selection"])
        teinte = th["texte_sel"] if i == 0 else th["texte"]
        icone(d, cle, x + marge_x, yl + (u - icone_t) / 2.0, icone_t, teinte)
        #  Le libellé est centré sur la hauteur de ligne, pas posé dessus :
        #  Blender centre verticalement le texte de ses menus.
        h_txt = police_menu.getbbox(nom)[3] - police_menu.getbbox(nom)[1]
        d.text((x + marge_x + icone_t + ecart,
                yl + (u - h_txt) / 2.0 - police_menu.getbbox(nom)[1]),
               nom, font=police_menu, fill=teinte)
    return L_menu, H_menu


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

    # -- l'encart des anciens noms, et le menu ----------------------------
    PY, PH = 226, 312
    AX, AL = 92, 560                     # l'encart : c'est MON annotation
    NX = 892                             # le menu : c'est BLENDER

    panneau(d, AX, PY, AL, PH, "", actif=False)
    d.text((AX + 22, PY + 13), "JUSQU'À BLENDER 4.0   ·   EEVEE LEGACY",
           font=f_tete, fill=GRIS_SOMBRE)

    #  Le fil d'Ariane est posé AU-DESSUS du menu, pas dedans : ce qui est
    #  de Blender doit rester de Blender, ce qui est de moi doit se voir
    #  comme tel. Le chevron est dessiné, pas écrit — les polices employées
    #  ici n'ont pas U+25B8 et le rendaient en carré vide.
    d.text((NX, PY + 13), "ADD", font=f_tete, fill=GRIS)
    cx = NX + d.textlength("ADD", font=f_tete) + 14
    d.polygon([(cx, PY + 18), (cx + 9, PY + 24), (cx, PY + 30)], fill=GRIS)
    d.text((cx + 22, PY + 13), "LIGHT PROBE", font=f_tete, fill=GRIS)
    lt = cx + 22 + d.textlength("LIGHT PROBE", font=f_tete)
    d.text((lt + 26, PY + 13), "BLENDER %s +" % VERSION_RENOMMAGE,
           font=f_tete, fill=TEAL)

    # -- les trois anciens noms, barrés ------------------------------------
    for i, (cle, _nom) in enumerate(entrees):
        yl = PY + 84 + i * 76
        ancien = ANCIENS.get(cle, "?")
        d.text((AX + 30, yl), ancien, font=f_menu, fill=GRIS_SOMBRE)
        la = d.textlength(ancien, font=f_menu)
        #  À hauteur d'x, pas sur la ligne de base : une rature posée trop
        #  bas se lit comme un soulignement et coupe les jambages.
        d.line([AX + 26, yl + 13, AX + 34 + la, yl + 13], fill=ROUGE,
               width=3)

    # -- le menu ------------------------------------------------------------
    MY = PY + 54
    if CAPTURE is None:
        lm, hm = menu_blender(im, entrees, theme_de_blender(), NX, MY)
    else:
        if not os.path.exists(CAPTURE):
            raise SystemExit(
                "capture introuvable : %s\n"
                "        produisez-la avec :\n"
                "        blender --python article/capturer_menu.py" % CAPTURE)
        cap = Image.open(CAPTURE).convert("RGBA")
        #  On ne dépasse JAMAIS l'échelle 1 : agrandir une capture d'écran
        #  la rend floue, et une image d'article floue décrédibilise le
        #  reste. Trop petite ? Refaites-la avec une échelle d'interface
        #  plus grande — voir ECHELLE dans capturer_menu.py.
        k = min((L - 92 - NX) / cap.width, (PH - 54) / cap.height, 1.0)
        if k < 1.0:
            cap = cap.resize((int(cap.width * k), int(cap.height * k)),
                             Image.LANCZOS)
        im.paste(cap, (NX, MY), cap)
        lm, hm = cap.width, cap.height

    #  Une flèche par ligne quand le menu est reconstruit — on connaît alors
    #  la position exacte de chaque entrée. Une seule flèche quand c'est une
    #  vraie capture : on ne sait pas où tombent ses lignes, et en inventer
    #  trois qui arriveraient à peu près en face serait pire que rien.
    u = UI_UNIT * ECHELLE_UI
    if CAPTURE is None:
        cibles = [MY + u + i * u + u / 2 for i in range(len(entrees))]
        depart = [PY + 84 + i * 76 + 20 for i in range(len(entrees))]
    else:
        cibles = [MY + hm / 2]
        depart = [PY + 84 + 76 + 20]
    for ya, yb in zip(depart, cibles):
        fx0, fx1 = AX + AL + 40, NX - 40
        d.line([fx0, ya, fx1 - 14, yb], fill=(78, 78, 90), width=2)
        d.polygon([(fx1, yb), (fx1 - 15, yb - 8), (fx1 - 15, yb + 8)],
                  fill=(120, 120, 134))

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
    prov = ("Menu redessiné avec la police (Inter), le thème et les mesures "
            "d'interface de Blender %s ; libellés lus dans "
            "LightProbe.bl_rna.properties['type']" % version)
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
