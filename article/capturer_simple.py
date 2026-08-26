"""
CAPTURE DU MENU — version simple.

    blender --python capturer_simple.py

Ou, sans terminal : ouvrir Blender, onglet **Scripting**, **Open**, choisir ce
fichier, puis **Run Script**.

CE QUI SE PASSE
---------------
Une fenêtre s'affiche : « la photo part dans 10 secondes ». Vous ouvrez le
menu vous-même, la photo part toute seule, et le chemin du fichier s'affiche.

    1. lancer le script
    2. souris au milieu de la vue 3D
    3. Shift + A, puis survoler « Light Probe »
    4. ne pas cliquer, attendre le déclenchement
    5. l'image est sur le Bureau : menu-capture.png

----------------------------------------------------------------------------
POURQUOI CETTE VERSION EXISTE
----------------------------------------------------------------------------
La version précédente ouvrait le menu elle-même, par `wm.call_menu`, appelé
depuis une minuterie. C'est là qu'elle échouait, et pour une raison de fond :

    bpy.ops.wm.call_menu(name=...)          # ne montre RIEN
    bpy.ops.wm.call_menu('INVOKE_DEFAULT', name=...)   # montre le menu

Appelé depuis Python, un opérateur s'exécute par défaut en mode EXEC. Or un
menu n'a pas d'exécution : il n'existe qu'INVOQUÉ, à une position de souris.
En mode EXEC il rend la main sans rien dessiner. La suite s'enchaînait donc
sur une vue vide, et le découpage ne trouvait rien.

Elle empilait en plus trois autres fragilités : un passage en plein écran qui
remplace l'écran courant et invalide les repères, des opérateurs appelés
depuis une minuterie — ce que la documentation de Blender déconseille
justement parce que le contexte n'y est pas celui d'une interface — et une
incrustation par couleur-clé qui ne pouvait pas fonctionner puisqu'il n'y
avait aucun menu à détourer.

Cette version-ci ne fait qu'UNE chose : attendre, puis photographier. Le
menu, c'est vous qui l'ouvrez — et une main humaine n'a besoin d'aucun
contexte d'opérateur pour tenir un menu ouvert.

Le découpage n'est plus fait ici non plus : mieux vaut une photo brute
utilisable qu'un détourage automatique qui échoue en silence.
"""

import os
import sys

import bpy

DELAI = 10.0                       # secondes avant le déclenchement

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if "--delai" in ARGS:
    DELAI = float(ARGS[ARGS.index("--delai") + 1])


def dossier():
    """Le Bureau. C'est le seul endroit qu'on ne peut pas rater — et
    `__file__` n'existe pas quand on lance depuis l'onglet Scripting."""
    maison = os.path.expanduser("~")
    for nom in ("Desktop", "Bureau"):
        d = os.path.join(maison, nom)
        if os.path.isdir(d):
            return d
    return maison


SORTIE = os.path.join(dossier(), "menu-capture.png")


def fenetre(titre, lignes, icone="INFO"):
    def dessiner(self, _ctx):
        for l in lignes:
            self.layout.label(text=l)
    try:
        bpy.context.window_manager.popup_menu(dessiner, title=titre,
                                              icon=icone)
    except Exception:
        pass
    for l in lignes:
        print("  " + l)


def photographier():
    """
    La prise de vue. `screen.screenshot` reçoit un chemin, donc il s'exécute
    et enregistre — contrairement à un menu, une capture d'écran a bien un
    mode EXEC.
    """
    try:
        bpy.ops.screen.screenshot(filepath=SORTIE)
        ok = os.path.exists(SORTIE)
    except Exception as e:
        fenetre("Echec", ["La capture a echoue :", str(e)], "ERROR")
        return None

    if ok:
        taille = os.path.getsize(SORTIE) / 1024.0
        fenetre("Capture enregistree",
                [SORTIE, "%.0f Ko" % taille], "CHECKMARK")
    else:
        fenetre("Echec", ["Aucun fichier ecrit dans :", dossier()], "ERROR")
    return None


if __name__ == "__main__":
    fenetre("Capture dans %d secondes" % DELAI,
            ["Shift + A, puis survolez Light Probe.",
             "Ne cliquez pas. La photo part toute seule.",
             "",
             "Fichier : " + SORTIE])
    print()
    print("  photo dans %d s  ->  %s" % (DELAI, SORTIE))
    bpy.app.timers.register(photographier, first_interval=DELAI)
