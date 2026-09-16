"""
La texture image du banc d'essai : un vrai fichier, lu sur le disque.

    python3 article-blender-shader/texture_source.py

Écrit `texture-2048.png` dans le répertoire de travail du banc.

Le sujet de la section est le COÛT d'une image comparé à celui d'un arbre
procédural. Il faut donc que la première sphère lise réellement un fichier :
un aplat ou une couleur constante ne mesurerait rien. Deux mille quarante-huit
pixels de côté, c'est la taille d'une texture de production courante.
"""

import os

import numpy as np
from PIL import Image

TAILLE = 2048
OCTAVES = 6
TRAVAIL = os.environ.get("TRAVAIL", "/tmp/bl-couches")


def bruit(n, graine):
    """Un bruit multi-octave, interpolé, déterministe."""
    alea = np.random.default_rng(graine)
    total = np.zeros((n, n), dtype=np.float64)
    amplitude, poids = 1.0, 0.0
    for octave in range(OCTAVES):
        cote = 2 ** (octave + 2)
        grille = alea.random((cote + 1, cote + 1))
        im = Image.fromarray((grille * 255).astype(np.uint8))
        couche = np.asarray(im.resize((n, n), Image.BICUBIC),
                            dtype=np.float64) / 255.0
        total += amplitude * couche
        poids += amplitude
        amplitude *= 0.55
    return total / poids


def principal():
    os.makedirs(TRAVAIL, exist_ok=True)
    a = bruit(TAILLE, 11)
    b = bruit(TAILLE, 29)
    #  Une pierre chaude : le bruit fin module la teinte, le bruit large la
    #  clarté. Rien de savant, il s'agit d'avoir un fichier à lire.
    v = 0.35 + 0.5 * a
    rvb = np.dstack([v * (0.82 + 0.18 * b),
                     v * (0.70 + 0.12 * b),
                     v * (0.58 + 0.10 * b)])
    im = Image.fromarray(np.clip(rvb * 255, 0, 255).astype(np.uint8))
    chemin = os.path.join(TRAVAIL, "texture-2048.png")
    im.save(chemin)
    print("  %s  %d × %d  %.1f Mo"
          % (os.path.basename(chemin), TAILLE, TAILLE,
             os.path.getsize(chemin) / 1048576))


if __name__ == "__main__":
    principal()
