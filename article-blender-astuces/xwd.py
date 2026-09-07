"""
Un décodeur XWD, parce qu'il n'y a pas d'ImageMagick.

    python3 xwd.py ecran.xwd ecran.png

----------------------------------------------------------------------------
POURQUOI PASSER PAR XWD
----------------------------------------------------------------------------
La capture interne de Blender, `bpy.ops.screen.screenshot()`, rend une image
noire sur cette machine : elle relit le tampon avant de la carte, et le GL
logiciel de l'écran virtuel ne le remplit pas comme le ferait une vraie carte
graphique. Vérifié — 1920 × 1080 entièrement à zéro.

`xwd` contourne le problème par le bas : il demande à X le contenu de la
fenêtre racine, indépendamment de qui l'a dessiné. Ce qui est à l'écran est
donc ce qui est capturé.

Reste que xwd écrit dans son propre format, et que ni PIL ni aucun outil de
conversion n'est présent ici. Le format est simple : un en-tête de nombres
32 bits gros-boutistes, le nom de la fenêtre, une palette, puis les pixels.
Trente lignes suffisent.
"""

import struct
import sys

import numpy as np
from PIL import Image

#  Les champs de l'en-tête XWD, dans l'ordre, tels que X les écrit.
CHAMPS = ("header_size", "file_version", "pixmap_format", "pixmap_depth",
          "pixmap_width", "pixmap_height", "xoffset", "byte_order",
          "bitmap_unit", "bitmap_bit_order", "bitmap_pad", "bits_per_pixel",
          "bytes_per_line", "visual_class", "red_mask", "green_mask",
          "blue_mask", "bits_per_rgb", "colormap_entries", "ncolors",
          "window_width", "window_height", "window_x", "window_y",
          "window_bdrwidth")


def decalage(masque):
    """La position du premier bit d'un masque de canal."""
    d = 0
    while masque and not masque & 1:
        masque >>= 1
        d += 1
    return d


def lire(chemin):
    with open(chemin, "rb") as f:
        brut = f.read()

    #  L'en-tête est toujours gros-boutiste, quel que soit `byte_order`, qui
    #  ne concerne que les pixels.
    tete = dict(zip(CHAMPS, struct.unpack(">25I", brut[:100])))
    if tete["file_version"] != 7:
        raise SystemExit("version XWD %d non gérée" % tete["file_version"])
    if tete["pixmap_format"] != 2:
        raise SystemExit("format XWD %d : seul ZPixmap est géré"
                         % tete["pixmap_format"])
    if tete["bits_per_pixel"] != 32:
        raise SystemExit("%d bits par pixel : seul le 32 bits est géré"
                         % tete["bits_per_pixel"])

    debut = tete["header_size"] + tete["ncolors"] * 12
    l, h = tete["pixmap_width"], tete["pixmap_height"]
    bpl = tete["bytes_per_line"]

    a = np.frombuffer(brut[debut:debut + bpl * h], dtype=np.uint8)
    a = a.reshape(h, bpl)[:, :l * 4]
    ordre = ">u4" if tete["byte_order"] else "<u4"
    mots = a.copy().view(ordre).reshape(h, l)

    canaux = []
    for cle in ("red_mask", "green_mask", "blue_mask"):
        m = tete[cle]
        canaux.append(((mots & m) >> decalage(m)).astype(np.uint8))
    return Image.fromarray(np.dstack(canaux))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage : python3 xwd.py entree.xwd sortie.png")
    im = lire(sys.argv[1])
    im.save(sys.argv[2])
    print("  %d × %d  -> %s" % (*im.size, sys.argv[2]))
