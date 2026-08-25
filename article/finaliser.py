"""
Finalise l'IMAGE 1 : contrôle chiffré, puis conversion en WebP.

    python3 article/finaliser.py

Le contrôle n'est pas décoratif. Une image d'article qui prétend démontrer
quelque chose doit pouvoir le prouver autrement qu'à l'œil — d'autant qu'une
image d'éclairage indirect est exactement le genre de chose qu'on croit
lisible sur son écran calibré et qui se referme sur un téléphone.

Trois mesures :

  1. LA FLAQUE          le soleil doit produire une vraie tache, pas un
                        dégradé. On veut un rapport franc entre la zone
                        éclairée en direct et le reste du sol.
  2. LE COIN SOMBRE     le fond des rayonnages est le point le plus mal
                        éclairé de la pièce. S'il est bouché, la sonde n'a
                        pas travaillé et l'image ne démontre rien.
  3. LA COULEUR TENUE   un livre dans l'ombre doit rester coloré. Une
                        irradiance mal cuite désature avant d'assombrir.
"""

import os
import sys

from PIL import Image
import numpy as np

RACINE = os.path.dirname(os.path.abspath(__file__))
NOM = "light-probes-blender-eevee-next"
PNG = os.path.join(RACINE, NOM + ".png")
GIZMO = os.path.join(RACINE, NOM + "-gizmo.png")
TEMOIN = os.path.join(RACINE, NOM + "-sans-sonde.png")
WEBP = os.path.join(RACINE, NOM + ".webp")

QUALITE = 88
GIZMO_OPACITE = 0.82


def mesurer(a):
    h, w, _ = a.shape
    lum = a.mean(2)

    #  1. la flaque : le centile haut du sol contre son centile bas
    sol = lum[int(h * 0.62):, :]
    flaque = np.percentile(sol, 99.0)
    ombre = np.percentile(sol, 10.0)

    #  2. le coin sombre : la bibliothèque, dans le tiers droit et le tiers
    #     médian en hauteur
    coin = a[int(h * 0.18):int(h * 0.68), int(w * 0.80):int(w * 0.97)]
    coin_lum = coin.mean(2)

    #  3. la couleur tenue : saturation moyenne des pixels du coin qui ne
    #     sont ni noirs ni gris neutres
    mx = coin.max(2).astype(float)
    mn = coin.min(2).astype(float)
    sat = np.where(mx > 8, (mx - mn) / np.maximum(mx, 1), 0.0)

    return {
        "flaque": flaque,
        "ombre": ombre,
        "contraste": flaque / max(ombre, 1.0),
        "coin_median": float(np.median(coin_lum)),
        "coin_min": float(np.percentile(coin_lum, 2)),
        "coin_sature": float(np.percentile(sat, 97) * 100),
    }


def superposer(fond, gizmo):
    """
    Le gizmo par-dessus le décor, comme une surcouche de fenêtre 3D : sans
    test de profondeur, et légèrement transparent. C'est exactement ce que
    fait Blender à l'écran — et la seule façon de montrer une sonde qui,
    correctement dimensionnée, déborde derrière les murs.
    """
    g = np.asarray(gizmo.convert("RGBA"), dtype=float) / 255.0
    f = np.asarray(fond.convert("RGB"), dtype=float) / 255.0
    a = (g[..., 3:4] * GIZMO_OPACITE)
    #  Superposition PAR RECOUVREMENT, pas en additif.
    #
    #  En additif, le trait ne fait qu'éclaircir ce qu'il traverse : sur un
    #  mur déjà clair il ne se voit plus du tout — mesuré, il passait de 190
    #  à 227 sur 255, invisible. Un gizmo de Blender est un trait PLEIN,
    #  légèrement transparent : il remplace la matière, il ne s'y ajoute pas.
    out = f * (1.0 - a) + g[..., :3] * a
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))


def temoin():
    """Le rapport avec / sans sonde, s'il a été rendu."""
    if not os.path.exists(TEMOIN):
        return None
    A = np.asarray(Image.open(PNG).convert("RGB"), dtype=float)
    B = np.asarray(Image.open(TEMOIN).convert("RGB"), dtype=float)
    if A.shape != B.shape:
        return None
    h, w, _ = A.shape

    def zone(x, box):
        x0, x1, y0, y1 = box
        return x[int(h * y0):int(h * y1), int(w * x0):int(w * x1)].mean()
    r = {}
    for nom, box in (("bibliothèque", (0.82, 0.96, 0.20, 0.70)),
                     ("mur au dos de la fenêtre", (0.26, 0.34, 0.10, 0.55)),
                     ("image entière", (0.0, 1.0, 0.0, 1.0))):
        a, b = zone(A, box), zone(B, box)
        r[nom] = (a, b, a / max(b, 0.01))
    return r


def principal():
    if not os.path.exists(PNG):
        raise SystemExit("rendu absent — lancez d'abord "
                         "`python3 article/light_probes_eevee_next.py`")
    im = Image.open(PNG).convert("RGB")
    a = np.asarray(im, dtype=float)
    m = mesurer(a)

    print()
    print("  %d × %d" % im.size)
    print("  flaque de soleil     %5.0f / 255" % m["flaque"])
    print("  sol à l'ombre        %5.0f / 255" % m["ombre"])
    print("  contraste de flaque  %5.2f  (en dessous de 2,5 c'est un "
          "dégradé, pas une flaque)" % m["contraste"])
    print("  coin le plus sombre  %5.0f / 255   médiane %3.0f"
          % (m["coin_min"], m["coin_median"]))
    print("  couleur tenue        %5.1f %% de saturation dans l'ombre"
          % m["coin_sature"])

    t = temoin()
    if t:
        print()
        print("  TÉMOIN — la même image rendue SANS Volume probe :")
        for nom, (av, sa, gain) in t.items():
            print("    %-26s avec %6.1f   sans %6.1f   ×%.2f"
                  % (nom, av, sa, gain))

    fautes = []
    if t and t["bibliothèque"][2] < 1.4:
        fautes.append("le Volume probe n'apporte presque rien (×%.2f dans "
                      "le coin le plus sombre) — l'image ne démontre pas "
                      "ce qu'elle annonce" % t["bibliothèque"][2])
    if m["contraste"] < 2.5:
        fautes.append("la flaque ne se détache pas du reste du sol")
    #  On ne juge PAS le coin sombre sur son 2e centile : une bibliothèque
    #  ouverte contient de vraies fentes noires, et elles doivent le rester.
    #  Ce qui compte, c'est la médiane — et surtout le témoin ci-dessus.
    if m["coin_median"] < 12:
        fautes.append("le coin sombre est bouché : médiane à %.0f/255"
                      % m["coin_median"])
    if m["coin_sature"] < 12:
        fautes.append("les couleurs sont désaturées dans l'ombre")
    if fautes:
        print()
        for f in fautes:
            print("  DÉFAUT : %s" % f)
        sys.exit(1)

    if os.path.exists(GIZMO):
        im = superposer(im, Image.open(GIZMO))
        print()
        print("  gizmo superposé depuis %s" % os.path.basename(GIZMO))
    else:
        print()
        print("  (pas de passe gizmo — lancez `--gizmo-seul`)")
    im.save(WEBP, "WEBP", quality=QUALITE, method=6)
    print()
    print("  %s  (%.0f Ko, qualité %d)"
          % (os.path.basename(WEBP), os.path.getsize(WEBP) / 1024, QUALITE))

    #  Le témoin sort AUSSI en WebP : c'est une image d'article à part
    #  entière, et le couple avec/sans est plus démonstratif que n'importe
    #  quelle explication écrite.
    if os.path.exists(TEMOIN):
        w2 = WEBP.replace(".webp", "-sans-sonde.webp")
        Image.open(TEMOIN).convert("RGB").save(w2, "WEBP",
                                               quality=QUALITE, method=6)
        print("  %s  (%.0f Ko)  — le témoin, utilisable tel quel"
              % (os.path.basename(w2), os.path.getsize(w2) / 1024))


if __name__ == "__main__":
    principal()
