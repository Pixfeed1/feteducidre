"""
CAPTURE AUTOMATIQUE DU MENU Add ▸ Light Probe.

    blender --python capturer_menu.py

Ou, sans terminal : ouvrir Blender, onglet **Scripting**, **Open**, choisir ce
fichier, **Run Script**.

Rien à faire d'autre. Pas de souris à placer, pas de menu à ouvrir, pas de
minuteur à surveiller. Le script s'occupe de tout et affiche le chemin du
fichier quand il a fini.

    Sortie : Bureau / menu-capture.png        le menu détouré, fond transparent
             Bureau / menu-capture-brute.png  l'écran entier
             Bureau / menu-capture.log        le compte-rendu

----------------------------------------------------------------------------
CE QUI NE MARCHAIT PAS DANS LA VERSION PRÉCÉDENTE
----------------------------------------------------------------------------
Une seule ligne, et elle expliquait tout :

    bpy.ops.wm.call_menu(name=MENU)              # ne dessine RIEN
    bpy.ops.wm.call_menu('INVOKE_DEFAULT', ...)  # ouvre le menu

Appelé depuis Python, un opérateur s'exécute par défaut en mode EXEC. Or un
menu n'a pas d'exécution : il n'existe qu'INVOQUÉ, à une position de souris.
En mode EXEC il rendait la main sans rien afficher — la suite photographiait
donc une vue vide, et le détourage ne trouvait rien à détourer.

D'où venait aussi « il faut mettre la souris au milieu » : un menu invoqué
s'ouvre là où est le pointeur. Blender sait le déplacer lui-même —
`window.cursor_warp()` — il n'y avait aucune raison de le demander à
l'utilisateur.

----------------------------------------------------------------------------
COMMENT LE MENU EST ISOLÉ
----------------------------------------------------------------------------
Incrustation par couleur-clé, comme en vidéo : le fond de la vue 3D est
repeint en magenta pur le temps de la photo, le menu devient la seule zone
qui ne soit pas magenta, et son rectangle se déduit sans ambiguïté.

Trois précautions, chacune indispensable :

  1. les surcouches, la barre d'outils et la barre latérale sont masquées —
     ce sont elles, à l'intérieur même de la vue, qui pollueraient le fond ;
  2. la recherche est bornée à la RÉGION de dessin, relevée sur Blender. La
     barre du haut et la barre d'état ne deviendront jamais magenta : sans
     cette borne, le « menu » retrouvé faisait la largeur de l'écran ;
  3. l'échelle d'interface est doublée avant la photo. Un menu à l'échelle 1
     fait 200 px de large : agrandi après coup, il est illisible.

Tout est remis en place ensuite — thème, panneaux, surcouches, échelle.

Aucune dépendance : uniquement le numpy fourni avec Blender.
"""

import os
import sys

import bpy
import numpy as np

MENU = "VIEW3D_MT_lightprobe_add"
CLE = (1.0, 0.0, 1.0)              # le magenta d'incrustation
MARGE = 6                          # pixels conservés autour du menu
ECHELLE = 2.0                      # échelle d'interface pendant la photo

#  Les temps d'attente. Chaque étape doit RENDRE LA MAIN à Blender pour
#  qu'il redessine : changer l'échelle d'interface relayoute toute la
#  fenêtre, et ouvrir un menu demande une image de plus.
T_REGLAGE = 0.8
T_MENU = 0.7
T_PHOTO = 0.4

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def dossier_de_sortie():
    """Le Bureau. `__file__` n'existe pas quand on lance depuis l'onglet
    Scripting, et personne ne va chercher une image dans ses
    téléchargements."""
    if "--sortie" in ARGS:
        d = os.path.abspath(os.path.expanduser(
            ARGS[ARGS.index("--sortie") + 1]))
        os.makedirs(d, exist_ok=True)
        return d
    maison = os.path.expanduser("~")
    for nom in ("Desktop", "Bureau"):
        d = os.path.join(maison, nom)
        if os.path.isdir(d):
            return d
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except NameError:
        return maison


DOSSIER = dossier_de_sortie()
SORTIE = os.path.join(DOSSIER, "menu-capture.png")
BRUTE = os.path.join(DOSSIER, "menu-capture-brute.png")
JOURNAL = os.path.join(DOSSIER, "menu-capture.log")

_etat = {}


def dire(*morceaux):
    """Console ET fichier : lancé autrement que depuis un terminal, Blender
    n'ouvre aucune console, et le script parlerait dans le vide."""
    ligne = " ".join(str(m) for m in morceaux)
    print(ligne)
    try:
        with open(JOURNAL, "a", encoding="utf-8") as f:
            f.write(ligne + "\n")
    except OSError:
        pass


def fenetre(titre, lignes, icone="INFO"):
    """Le résultat par-dessus l'interface : c'est le seul endroit où
    l'utilisateur le verra à coup sûr."""
    def dessiner(self, _ctx):
        for l in lignes:
            self.layout.label(text=l)
    try:
        bpy.context.window_manager.popup_menu(dessiner, title=titre,
                                              icon=icone)
    except Exception:
        pass


def vue3d():
    """La fenêtre, l'aire et la RÉGION DE DESSIN d'une vue 3D."""
    for w in bpy.context.window_manager.windows:
        for a in w.screen.areas:
            if a.type != "VIEW_3D":
                continue
            for r in a.regions:
                if r.type == "WINDOW":
                    return w, a, r
    return None, None, None


# ---------------------------------------------------------------------------

def _reglages():
    """Étape 1 : vider la vue, la peindre en magenta, doubler l'échelle."""
    w, a, r = vue3d()
    if a is None:
        dire("  ECHEC : aucune vue 3D.")
        dire("  Lancez ce script sur un Blender AVEC interface, pas en -b.")
        fenetre("Echec", ["Aucune vue 3D dans cette fenetre."], "ERROR")
        return None

    sp = a.spaces.active
    th = bpy.context.preferences.themes[0].view_3d.space
    vu = bpy.context.preferences.view

    _etat["memoire"] = {
        "fond": th.gradients.background_type,
        "couleur": tuple(th.gradients.high_gradient),
        "echelle": vu.ui_scale,
        "surcouches": sp.overlay.show_overlays,
        "outils": sp.show_region_toolbar,
        "lateral": sp.show_region_ui,
        "gizmo": sp.show_gizmo,
    }

    #  Tout ce qui se dessine DANS la vue et n'est pas magenta polluerait le
    #  détourage : grille, axes, gizmo de navigation, panneaux latéraux.
    sp.overlay.show_overlays = False
    sp.show_gizmo = False
    sp.show_region_toolbar = False
    sp.show_region_ui = False
    th.gradients.background_type = "SINGLE_COLOR"
    th.gradients.high_gradient = CLE
    vu.ui_scale = ECHELLE

    bpy.app.timers.register(_ouvrir, first_interval=T_MENU)
    return None


def _ouvrir():
    """Étape 2 : poser le pointeur au centre de la vue, ouvrir le menu."""
    w, a, r = vue3d()
    #  La géométrie est relue MAINTENANT : doubler l'échelle d'interface a
    #  relayouté toute la fenêtre, les rectangles d'avant ne valent plus rien.
    _etat["region"] = (r.x, r.y, r.width, r.height)

    #  Blender déplace lui-même le pointeur. Un menu s'ouvre où il se trouve :
    #  sans ce recentrage, il se collait au bord de l'écran — d'où le
    #  « mettez la souris au milieu » qu'on n'aurait jamais dû demander.
    w.cursor_warp(r.x + r.width // 2, r.y + r.height // 2)

    with bpy.context.temp_override(window=w, area=a, region=r):
        #  INVOKE_DEFAULT, et pas autrement : un menu n'a pas d'exécution.
        bpy.ops.wm.call_menu("INVOKE_DEFAULT", name=MENU)

    bpy.app.timers.register(_photographier, first_interval=T_PHOTO)
    return None


def _photographier():
    """Étape 3 : la photo. `screen.screenshot` reçoit un chemin, donc lui
    s'exécute bel et bien."""
    w, a, r = vue3d()
    with bpy.context.temp_override(window=w, area=a, region=r):
        bpy.ops.screen.screenshot(filepath=BRUTE)
    bpy.app.timers.register(_ranger, first_interval=T_PHOTO)
    return None


def _ranger():
    """Étape 4 : détourer, tout remettre en place, annoncer."""
    try:
        ok = detourer(_etat["region"])
    except Exception:
        import traceback
        dire("  ERREUR pendant le decoupage :")
        dire(traceback.format_exc())
        ok = False
    restaurer()

    if ok:
        fenetre("Capture enregistree", [SORTIE], "CHECKMARK")
    else:
        fenetre("Echec", ["Compte-rendu :", JOURNAL], "ERROR")

    #  On ne referme que si ça a marché ET si Blender a été lancé en ligne de
    #  commande : depuis l'onglet Scripting, fermer la fenêtre cacherait
    #  justement le message.
    if ok and "--python" in sys.argv and "--rester" not in ARGS:
        bpy.ops.wm.quit_blender()
    return None


def restaurer():
    m = _etat.get("memoire")
    if not m:
        return
    w, a, r = vue3d()
    th = bpy.context.preferences.themes[0].view_3d.space
    vu = bpy.context.preferences.view
    th.gradients.background_type = m["fond"]
    th.gradients.high_gradient = m["couleur"]
    vu.ui_scale = m["echelle"]
    if a is not None:
        sp = a.spaces.active
        sp.overlay.show_overlays = m["surcouches"]
        sp.show_gizmo = m["gizmo"]
        sp.show_region_toolbar = m["outils"]
        sp.show_region_ui = m["lateral"]


# ---------------------------------------------------------------------------

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
    """Tolérant : l'anticrénelage du bord du menu produit des pixels à
    mi-chemin, et une égalité stricte rognerait le contour."""
    return (a[..., 0] > 0.80) & (a[..., 1] < 0.20) & (a[..., 2] > 0.80)


def detourer(rect):
    if not os.path.exists(BRUTE):
        dire("  ECHEC : aucune capture ecrite. La prise de vue a echoue.")
        return False

    a = lire(BRUTE)
    H, L = a.shape[:2]
    rx, ry, rl, rh = rect

    #  Blender compte ses régions depuis le BAS de la fenêtre, une image se
    #  lit depuis le HAUT : d'où l'inversion.
    ix0, ix1 = max(0, rx), min(L, rx + rl)
    iy0, iy1 = max(0, H - (ry + rh)), min(H, H - ry)

    zone = a[iy0:iy1, ix0:ix1]
    if zone.size == 0:
        dire("  ECHEC : la region de dessin est hors de la capture.")
        return False

    utile = ~est_magenta(zone)
    part = 100.0 * utile.mean()
    dire("  zone analysee : %d x %d px, %.1f %% non magenta"
         % (zone.shape[1], zone.shape[0], part))

    lignes = np.where(utile.any(axis=1))[0]
    colonnes = np.where(utile.any(axis=0))[0]
    if not len(lignes) or not len(colonnes):
        dire("  ECHEC : la vue est entierement magenta.")
        dire("  Le menu ne s'est pas ouvert. Regardez %s."
             % os.path.basename(BRUTE))
        return False

    y0 = max(0, lignes[0] - MARGE) + iy0
    y1 = min(zone.shape[0], lignes[-1] + 1 + MARGE) + iy0
    x0 = max(0, colonnes[0] - MARGE) + ix0
    x1 = min(zone.shape[1], colonnes[-1] + 1 + MARGE) + ix0

    if (x1 - x0) > rl * 0.9 or (y1 - y0) > rh * 0.9:
        dire("  ECHEC : le decoupage fait presque toute la vue (%d x %d)."
             % (x1 - x0, y1 - y0))
        dire("  Quelque chose d'autre que le menu est reste a l'ecran.")
        return False

    coupe = a[y0:y1, x0:x1].copy()
    #  Le magenta des angles arrondis passe en transparent : le menu se
    #  posera proprement sur n'importe quel fond.
    coupe[est_magenta(coupe)] = (0.0, 0.0, 0.0, 0.0)
    ecrire(coupe, SORTIE)

    dire("  menu detoure : %d x %d px" % (x1 - x0, y1 - y0))
    dire("  CAPTURE  %s" % SORTIE)
    return True


if __name__ == "__main__":
    try:
        os.remove(JOURNAL)
    except OSError:
        pass
    dire("")
    dire("  capture de %s" % MENU)
    dire("  Blender %s" % bpy.app.version_string)
    dire("  sortie : %s" % DOSSIER)
    bpy.app.timers.register(_reglages, first_interval=T_REGLAGE)
