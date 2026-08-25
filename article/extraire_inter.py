"""
Extrait la police d'interface de Blender.

    python3 article/extraire_inter.py

Le paquet `bpy` distribué sur PyPI embarque les fichiers de données de
Blender, dont sa police d'interface : **Inter**, au format woff2. Pillow ne
sait pas lire le woff2 ; on le convertit donc une fois en ttf, et le menu
reconstruit se dessine avec la police exacte de Blender au lieu d'une
Helvetica de substitution.

À relancer seulement si l'on change de version de `bpy`.

Dépendances : fonttools et brotli (`pip install fonttools brotli`).
"""

import os
import sys

RACINE = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(RACINE, "polices", "Inter-Blender.ttf")


def source():
    """Le woff2 d'Inter, dans les données de la version de bpy installée."""
    import bpy
    #  bpy expose sa racine de données : on ne devine pas le chemin, on le
    #  demande. Il change à chaque version mineure.
    base = bpy.utils.resource_path("LOCAL")
    chemin = os.path.join(base, "datafiles", "fonts", "Inter.woff2")
    if not os.path.exists(chemin):
        raise SystemExit("Inter.woff2 introuvable sous %s" % base)
    return chemin


def principal():
    try:
        from fontTools.ttLib import TTFont
    except ImportError:
        raise SystemExit("fonttools manquant : pip install fonttools brotli")

    src = source()
    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    f = TTFont(src)
    f.flavor = None                    # woff2 -> ttf
    f.save(SORTIE)
    print("  %s  ->  %s  (%.0f Ko)"
          % (os.path.relpath(src, "/"), os.path.relpath(SORTIE, RACINE),
             os.path.getsize(SORTIE) / 1024))


if __name__ == "__main__":
    principal()
