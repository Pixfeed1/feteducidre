"""
LA VRAIE CAPTURE DU MENU Add ▸ Light Probe.

    blender --python capturer_menu.py

Compatible Blender 4.2 LTS à 4.5 LTS. Blender s'ouvre, met la vue 3D en
plein écran, déroule le menu, se photographie, détoure le menu et se referme.

OÙ ATTERRIT LA CAPTURE
----------------------
Par défaut, dans le MÊME DOSSIER que ce script. Le chemin absolu est
imprimé en clair à la fin — c'est la dernière ligne de la console.

Pour choisir soi-même :

    blender --python capturer_menu.py -- --sortie ~/Images

Deux fichiers en sortent :

    menu-capture.png         le menu détouré, sur fond transparent
    menu-capture-brute.png   la fenêtre entière, au cas où

AVANT DE LANCER
---------------
Rien à préparer. Le script remet le thème et l'échelle d'interface comme il
les a trouvés. Si vous voulez garder Blender ouvert pour regarder :

    blender --python capturer_menu.py -- --rester

----------------------------------------------------------------------------
COMMENT LE MENU EST DÉTOURÉ
----------------------------------------------------------------------------
Un menu déroulé est FUGACE : il se ferme au premier clic, et sa position
dépend de celle de la souris. Le découper à la main donnerait un cadrage
différent à chaque fois.

D'où l'incrustation par couleur-clé, comme en vidéo : on repeint le fond de
la vue 3D en magenta pur le temps de la photo. Le menu devient la seule zone
non magenta, et son rectangle se déduit sans ambiguïté.

Avec DEUX précautions qui font toute la fiabilité :

  1. la vue 3D est passée en PLEIN ÉCRAN. Sinon la barre d'outils, l'outliner
     et les propriétés — qui ne sont pas magenta — seraient pris pour le
     menu ;

  2. la recherche est bornée AU RECTANGLE DE LA VUE 3D, relevé sur l'aire
     elle-même. Il reste toujours la barre du haut et la barre d'état, qui
     ne deviendront jamais magenta ; sans cette borne, le découpage les
     attrapait et le « menu » faisait la largeur de l'écran.

Aucune dépendance : uniquement le numpy fourni avec Blender.
"""

import os
import sys

import bpy
import numpy as np

#  `blender --python x.py -- --sortie /chemin` : Blender passe tout ce qui
#  suit `--` au script, sans y toucher.
ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def dossier_de_sortie():
    if "--sortie" in ARGS:
        d = os.path.abspath(os.path.expanduser(
            ARGS[ARGS.index("--sortie") + 1]))
        os.makedirs(d, exist_ok=True)
        return d
    #  Sinon : à côté du script. Sous `--python`, __file__ est bien défini
    #  et pointe le fichier réellement exécuté.
    return os.path.dirname(os.path.abspath(__file__))


DOSSIER = dossier_de_sortie()
SORTIE = os.path.join(DOSSIER, "menu-capture.png")
BRUTE = os.path.join(DOSSIER, "menu-capture-brute.png")

MENU = "VIEW3D_MT_lightprobe_add"
CLE = (1.0, 0.0, 1.0)              # le magenta d'incrustation
MARGE = 6                          # pixels conservés autour du menu
ATTENTE = 0.55                     # laisse le menu se dessiner

#  L'ÉCHELLE D'INTERFACE, ET POURQUOI ON LA POUSSE.
#
#  Un menu de Blender à l'échelle 1 fait environ 200 px de large. Dans une
#  image d'article de 1600 px c'est un timbre-poste, et l'agrandir après coup
#  donne une bouillie. On double donc l'échelle AVANT la photo : Blender
#  redessine le menu à sa taille double, nativement net, plus rien à
#  interpoler. Restaurée juste après, comme le thème.
ECHELLE = 2.0

_etat = {}


def vue3d():
    """La fenêtre, l'aire et la région d'une vue 3D — un menu ne se déroule
    que dans un contexte qui en possède une."""
    for w in bpy.context.window_manager.windows:
        for a in w.screen.areas:
            if a.type != "VIEW_3D":
                continue
            for r in a.regions:
                if r.type == "WINDOW":
                    return w, a, r
    return None, None, None


def preparer():
    """Plein écran, fond magenta, interface doublée."""
    w, a, r = vue3d()
    th = bpy.context.preferences.themes[0].view_3d.space
    vu = bpy.context.preferences.view
    _etat["fond"] = th.gradients.background_type
    _etat["couleur"] = tuple(th.gradients.high_gradient)
    _etat["echelle"] = vu.ui_scale

    with bpy.context.temp_override(window=w, area=a, region=r):
        #  Plein écran : tout ce qui n'est pas la vue 3D disparaît, donc
        #  tout ce qui n'est pas magenta après coup est bien le menu.
        bpy.ops.screen.screen_full_area()
    _etat["plein_ecran"] = True

    th.gradients.background_type = "SINGLE_COLOR"
    th.gradients.high_gradient = CLE
    vu.ui_scale = ECHELLE


def restaurer():
    th = bpy.context.preferences.themes[0].view_3d.space
    vu = bpy.context.preferences.view
    if "fond" in _etat:
        th.gradients.background_type = _etat["fond"]
        th.gradients.high_gradient = _etat["couleur"]
        vu.ui_scale = _etat["echelle"]
    if _etat.get("plein_ecran"):
        w, a, r = vue3d()
        if a is not None:
            with bpy.context.temp_override(window=w, area=a, region=r):
                bpy.ops.screen.back_to_previous()


def lire(chemin):
    img = bpy.data.images.load(chemin)
    l, h = img.size
    a = np.empty(l * h * 4, dtype=np.float32)
    img.pixels.foreach_get(a)
    bpy.data.images.remove(img)
    #  Blender range ses images de bas en haut : on remet à l'endroit.
    return a.reshape(h, l, 4)[::-1]


def ecrire(a, chemin):
    h, l, _ = a.shape
    img = bpy.data.images.new("DECOUPE", width=l, height=h, alpha=True)
    img.pixels.foreach_set(a[::-1].ravel())
    img.filepath_raw = chemin
    img.file_format = "PNG"
    img.save()
    bpy.data.images.remove(img)


def est_magenta(a):
    """Tolérant : l'anticrénelage des bords du menu produit des pixels à
    mi-chemin entre le magenta et le gris, et une égalité stricte rognerait
    le contour d'un pixel ou deux."""
    return (a[..., 0] > 0.80) & (a[..., 1] < 0.20) & (a[..., 2] > 0.80)


def detourer(rect):
    a = lire(BRUTE)
    H, L = a.shape[:2]
    x0v, y0v, lv, hv = rect

    #  Le rectangle de la vue 3D, converti dans le repère de l'image.
    #  Blender compte ses aires depuis le bas de la fenêtre, une image se lit
    #  depuis le haut : d'où l'inversion.
    ix0 = max(0, min(L, x0v))
    ix1 = max(0, min(L, x0v + lv))
    iy0 = max(0, min(H, H - (y0v + hv)))
    iy1 = max(0, min(H, H - y0v))

    zone = a[iy0:iy1, ix0:ix1]
    if zone.size == 0:
        print("  ÉCHEC : la vue 3D est hors de la capture.")
        return False

    utile = ~est_magenta(zone)
    lignes = np.where(utile.any(axis=1))[0]
    colonnes = np.where(utile.any(axis=0))[0]
    if not len(lignes) or not len(colonnes):
        print("  ÉCHEC : aucune zone non magenta dans la vue 3D — le menu "
              "ne s'est pas déroulé.")
        print("  Essayez en laissant la souris AU MILIEU de la fenêtre "
              "de Blender au lancement.")
        return False

    y0 = max(0, lignes[0] - MARGE) + iy0
    y1 = min(zone.shape[0], lignes[-1] + 1 + MARGE) + iy0
    x0 = max(0, colonnes[0] - MARGE) + ix0
    x1 = min(zone.shape[1], colonnes[-1] + 1 + MARGE) + ix0

    coupe = a[y0:y1, x0:x1].copy()
    #  Le magenta résiduel des angles arrondis passe en transparent : le menu
    #  se posera proprement sur n'importe quel fond.
    coupe[est_magenta(coupe)] = (0.0, 0.0, 0.0, 0.0)
    ecrire(coupe, SORTIE)

    print()
    print("  menu détouré : %d × %d px" % (x1 - x0, y1 - y0))
    if (x1 - x0) > lv * 0.9:
        print("  ATTENTION : le découpage fait presque toute la largeur de "
              "la vue.")
        print("  Le menu ne s'est probablement pas déroulé — vérifiez %s."
              % os.path.basename(BRUTE))
    print()
    print("  CAPTURE   %s" % SORTIE)
    print("  fenêtre   %s" % BRUTE)
    return True


# ---------------------------------------------------------------------------
#  L'ENCHAÎNEMENT, EN TROIS RÉVEILS
# ---------------------------------------------------------------------------
#  Un menu ne se déroule pas dans le même souffle que sa photographie : il
#  faut rendre la main à Blender entre les deux pour qu'il ait le temps de le
#  dessiner. D'où trois temps, et non trois lignes à la suite.

def _derouler():
    w, a, r = vue3d()
    if a is None:
        print("  ÉCHEC : aucune vue 3D.")
        print("  Ce script demande un Blender AVEC interface : lancez-le "
              "sans l'option -b.")
        bpy.ops.wm.quit_blender()
        return None
    preparer()
    w, a, r = vue3d()                  # l'aire a changé avec le plein écran
    _etat["rect"] = (a.x, a.y, a.width, a.height)
    with bpy.context.temp_override(window=w, area=a, region=r):
        bpy.ops.wm.call_menu(name=MENU)
    bpy.app.timers.register(_photographier, first_interval=ATTENTE)
    return None


def _photographier():
    w, a, r = vue3d()
    with bpy.context.temp_override(window=w, area=a, region=r):
        bpy.ops.screen.screenshot(filepath=BRUTE)
    bpy.app.timers.register(_ranger, first_interval=0.3)
    return None


def _ranger():
    ok = detourer(_etat["rect"])
    restaurer()
    if "--rester" not in ARGS:
        bpy.ops.wm.quit_blender()
    return None


if __name__ == "__main__":
    print()
    print("  capture de %s" % MENU)
    print("  sortie prévue : %s" % SORTIE)
    bpy.app.timers.register(_derouler, first_interval=1.0)
