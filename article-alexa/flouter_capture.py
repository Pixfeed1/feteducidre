"""
Floute les prompts visibles AUTOUR du dialogue « Supprimer l'activité ».

    python3 flouter2.py entree.png sortie.png

Le dialogue couvre une partie de la liste. Les zones à masquer sont donc
découpées pour s'arrêter à son bord : flouter en travers effacerait le
dialogue, qui est le sujet de l'image.

Même traitement qu'avant, flou gaussien puis pixellisation : un simple
calque translucide ou un flou léger se remontent, la pixellisation non.
"""

import sys

from PIL import Image, ImageFilter

#  Le dialogue, mesuré sur la capture. Rien ne doit mordre dedans.
DIALOGUE = (383, 246, 766, 558)


def masquer(img, boite, rayon=12, grain=10):
    x0, y0, x1, y1 = [int(v) for v in boite]
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(img.width, x1), min(img.height, y1)
    if x1 <= x0 or y1 <= y0:
        raise SystemExit("zone vide : %s" % (boite,))

    #  Garde-fou : une zone ne doit jamais chevaucher le dialogue.
    dx0, dy0, dx1, dy1 = DIALOGUE
    if x0 < dx1 and dx0 < x1 and y0 < dy1 and dy0 < y1:
        raise SystemExit(
            "la zone %s mord sur le dialogue %s : elle l'effacerait"
            % (boite, DIALOGUE))

    zone = img.crop((x0, y0, x1, y1)).filter(ImageFilter.GaussianBlur(rayon))
    pw = max(1, (x1 - x0) // grain)
    ph = max(1, (y1 - y0) // grain)
    zone = zone.resize((pw, ph), Image.BILINEAR)
    zone = zone.resize((x1 - x0, y1 - y0), Image.NEAREST)
    img.paste(zone, (x0, y0))
    return img


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: flouter2.py entree.png sortie.png")

    im = Image.open(sys.argv[1]).convert("RGB")

    zones = (
        (269, 193, 662, 219),     # 1er prompt, au-dessus du dialogue
        (269, 316, 381, 342),     # 2e prompt, bande gauche visible
        (269, 471, 381, 497),     # 3e prompt, bande gauche visible
        (269, 624, 652, 650),     # 4e prompt, sous le dialogue
        (269, 776, 797, 827),     # 5e prompt, deux lignes
        (800, 775, 883, 838),     # la vignette de l'image générée
    )
    for z in zones:
        masquer(im, z)

    im.save(sys.argv[2])
    print("écrit %s  %dx%d, %d zones masquées"
          % (sys.argv[2], im.width, im.height, len(zones)))


if __name__ == "__main__":
    main()
