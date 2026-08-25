"""
LA VRAIE CAPTURE DU MENU — à lancer sur un poste avec interface graphique.

    blender --python article/capturer_menu.py

Blender s'ouvre, déroule Add ▸ Light Probe, se photographie lui-même, découpe
le menu et se referme. Vous récupérez `article/menu-capture.png` : une vraie
capture d'écran de votre Blender, détourée, sur fond transparent.

Puis :

    python3 article/menu_light_probe.py --capture article/menu-capture.png

qui la monte dans la mise en page annotée de l'article.

----------------------------------------------------------------------------
POURQUOI CE SCRIPT EXISTE
----------------------------------------------------------------------------
Le module `bpy` distribué sur PyPI n'embarque aucun exécutable : c'est
Blender sans interface, par construction. Aucun écran à photographier. Une
capture d'écran demande donc un Blender complet, et une session graphique.

----------------------------------------------------------------------------
COMMENT LE MENU EST DÉTOURÉ
----------------------------------------------------------------------------
Un menu déroulé est un élément FUGACE : il se ferme au premier clic, et ses
coordonnées à l'écran dépendent de la position de la souris. Le découper à la
main à chaque fois serait interminable, et le résultat jamais deux fois
cadré pareil.

D'où l'incrustation par couleur-clé, comme en vidéo : on repeint le fond de
la vue 3D en magenta pur le temps de la photo. Le menu devient alors la seule
zone de l'image qui ne soit PAS magenta, et son rectangle se déduit sans la
moindre ambiguïté. Le thème est restauré juste après.

Aucune dépendance : uniquement le numpy fourni avec Blender.
"""

import os
import sys

import bpy
import numpy as np

RACINE = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(RACINE, "menu-capture.png")
BRUTE = os.path.join(RACINE, "menu-capture-brute.png")

MENU = "VIEW3D_MT_lightprobe_add"
CLE = (1.0, 0.0, 1.0)              # le magenta d'incrustation
MARGE = 6                          # pixels conservés autour du menu
ATTENTE = 0.45                     # laisse le menu se dessiner

#  L'ÉCHELLE D'INTERFACE, ET POURQUOI ON LA POUSSE.
#
#  Un menu de Blender à l'échelle 1 fait environ 200 px de large. Dans une
#  image d'article de 1600 px, c'est un timbre-poste — et l'agrandir après
#  coup donne une bouillie. On double donc l'échelle de l'interface AVANT la
#  photo : Blender redessine le menu à sa taille double, nativement net, et
#  il n'y a plus rien à interpoler. Restauré juste après, comme le thème.
ECHELLE = 2.0


def vue3d():
    """La fenêtre, la zone et la région d'une vue 3D — un menu ne peut être
    déroulé que dans un contexte qui en possède une."""
    for w in bpy.context.window_manager.windows:
        for a in w.screen.areas:
            if a.type != "VIEW_3D":
                continue
            for r in a.regions:
                if r.type == "WINDOW":
                    return w, a, r
    return None, None, None


def peindre_le_fond(actif):
    """Repeint le fond de la vue 3D en magenta et grossit l'interface, ou
    rétablit les deux."""
    th = bpy.context.preferences.themes[0].view_3d.space
    vu = bpy.context.preferences.view
    if actif:
        peindre_le_fond.memoire = (th.gradients.background_type,
                                   tuple(th.gradients.high_gradient),
                                   vu.ui_scale)
        th.gradients.background_type = "SINGLE_COLOR"
        th.gradients.high_gradient = CLE
        vu.ui_scale = ECHELLE
    elif hasattr(peindre_le_fond, "memoire"):
        t, c, e = peindre_le_fond.memoire
        th.gradients.background_type = t
        th.gradients.high_gradient = c
        vu.ui_scale = e


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


def detourer():
    """
    Le rectangle du menu = tout ce qui n'est pas magenta.

    On tolère un écart : l'anticrénelage des bords du menu produit des pixels
    à mi-chemin entre le magenta et le gris, et un test d'égalité stricte
    rognerait le contour d'un pixel ou deux.
    """
    a = lire(BRUTE)
    r, v, b = a[..., 0], a[..., 1], a[..., 2]
    fond = (r > 0.80) & (v < 0.20) & (b > 0.80)
    utile = ~fond

    lignes = np.where(utile.any(axis=1))[0]
    colonnes = np.where(utile.any(axis=0))[0]
    if not len(lignes) or not len(colonnes):
        print("  ÉCHEC : aucune zone non magenta — le menu ne s'est pas "
              "déroulé, ou le thème n'a pas été repeint.")
        return False

    y0 = max(0, lignes[0] - MARGE)
    y1 = min(a.shape[0], lignes[-1] + 1 + MARGE)
    x0 = max(0, colonnes[0] - MARGE)
    x1 = min(a.shape[1], colonnes[-1] + 1 + MARGE)

    coupe = a[y0:y1, x0:x1].copy()
    #  Le magenta résiduel des angles arrondis passe en transparent : le
    #  menu se posera proprement sur n'importe quel fond.
    m = ((coupe[..., 0] > 0.80) & (coupe[..., 1] < 0.20) &
         (coupe[..., 2] > 0.80))
    coupe[m] = (0.0, 0.0, 0.0, 0.0)

    ecrire(coupe, SORTIE)
    print("  menu détouré : %d × %d px  ->  %s"
          % (x1 - x0, y1 - y0, os.path.basename(SORTIE)))
    print("  (capture entière conservée : %s)" % os.path.basename(BRUTE))
    return True


# ---------------------------------------------------------------------------
#  L'ENCHAÎNEMENT, EN TROIS RÉVEILS
# ---------------------------------------------------------------------------
#  Un menu ne se déroule pas dans le même souffle que sa photographie : il
#  faut rendre la main à Blender entre les deux pour qu'il ait le temps de
#  le dessiner. D'où trois temps, et non trois lignes à la suite.

def _derouler():
    w, a, r = vue3d()
    if a is None:
        print("  ÉCHEC : aucune vue 3D. Lancez ce script sur un Blender "
              "avec interface, pas en mode -b.")
        bpy.ops.wm.quit_blender()
        return None
    peindre_le_fond(True)
    with bpy.context.temp_override(window=w, area=a, region=r):
        bpy.ops.wm.call_menu(name=MENU)
    bpy.app.timers.register(_photographier, first_interval=ATTENTE)
    return None


def _photographier():
    w, a, r = vue3d()
    with bpy.context.temp_override(window=w, area=a, region=r):
        bpy.ops.screen.screenshot(filepath=BRUTE)
    bpy.app.timers.register(_ranger, first_interval=0.25)
    return None


def _ranger():
    peindre_le_fond(False)
    ok = detourer()
    print("  terminé." if ok else "  terminé avec une erreur.")
    if "--rester" not in sys.argv:
        bpy.ops.wm.quit_blender()
    return None


if __name__ == "__main__":
    print()
    print("  capture de %s …" % MENU)
    bpy.app.timers.register(_derouler, first_interval=0.8)
