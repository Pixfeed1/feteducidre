"""
IMAGE 8 de l'article — la fuite de lumière à travers un mur.

    python3 article/fuite_lumiere.py

Rend les trois passes dans `article/fuite/` et écrit `article/fuite.json` :

    grossiere.png    la grille trop lâche — la fuite
    fine.png         la même scène, grille assez fine pour résoudre le mur
    sans-sonde.png   aucune sonde : le plancher, ce que la pièce DOIT valoir

----------------------------------------------------------------------------
CE QUI FAIT VRAIMENT FUIR LA LUMIÈRE
----------------------------------------------------------------------------
Le brief parle d'un « volume trop petit ». Une sonde trop petite produit un
autre symptôme, mesuré plus tôt dans cet article : les parois laissées HORS du
volume ne reçoivent plus rien et rendent noires. C'est un manque, pas une
fuite.

La fuite, elle, vient de la TAILLE DE MAILLE. L'irradiance est stockée aux
sommets d'une grille et interpolée entre eux. Si une maille est plus large que
le mur n'est épais, ses huit sommets ne peuvent pas tous être du bon côté :
certains sont dans la pièce éclairée. Un point de la pièce sombre, situé dans
cette maille, reçoit alors une moyenne qui contient de la lumière d'à côté —
et le mur cesse d'exister pour l'éclairage.

D'où la règle, qui est une comparaison de longueurs et rien d'autre :

    taille de maille  <  épaisseur du mur

Ici la pièce fait 8,00 m de large. À 4 mailles en X, chaque maille fait 2,00 m
pour un mur de 0,30 m : la lumière traverse. À 40 mailles, 0,20 m par maille,
sous l'épaisseur du mur : elle ne traverse plus.

C'est pour ça que la figure porte la taille de maille en clair à côté de
l'épaisseur du mur. « Augmentez la résolution » n'est pas un conseil ; « une
maille doit être plus petite que le mur » en est un.

----------------------------------------------------------------------------
POURQUOI UNE PASSE SANS SONDE
----------------------------------------------------------------------------
Sans elle, on comparerait une fuite à une fuite plus discrète, sans savoir où
est le zéro. La passe sans sonde donne ce que la pièce sombre vaut quand
aucune lumière ne peut y entrer : c'est la seule valeur qui permette de dire
combien il RESTE de fuite dans la version corrigée.
"""

import json
import math
import os
import sys

import bpy

RACINE = os.path.dirname(os.path.abspath(__file__))
DOSSIER = os.path.join(RACINE, "fuite")
JOURNAL = os.path.join(RACINE, "fuite.json")

RAPIDE = "--rapide" in sys.argv
RESOLUTION = (900, 600) if RAPIDE else (1500, 1000)
ECHANTILLONS = 24 if RAPIDE else 128

# ---------------------------------------------------------------------------
#  LES DEUX PIÈCES
# ---------------------------------------------------------------------------
X0, X1 = -4.00, 4.00
Y0, Y1 = -2.50, 2.50
Z0, Z1 = 0.00, 3.00
EP = 0.20                      # murs extérieurs

CLOISON = 0.30                 # LA cote de l'image : l'épaisseur du refend
CX = 0.00                      # il coupe la boîte en deux à x = 0

#  La fenêtre, dans le mur ouest — donc entièrement du côté éclairé.
F_Y0, F_Y1 = -1.60, 1.60
F_Z0, F_Z1 = 0.70, 2.40

#  Les deux réglages comparés. Seule la résolution change.
GROSSIERE = (4, 3, 2)
FINE = (40, 24, 14)
SURFELS = 28
BAKE_SAMPLES = 1024

#  LA COUPE. Ces deux parois sont rendues INVISIBLES À LA CAMÉRA, et non
#  masquées : `hide_render` les retirerait du calcul, la pièce ne serait plus
#  étanche et la lumière sortirait pour de bon — on démontrerait une fuite
#  qu'on aurait fabriquée soi-même. `visible_camera = False` laisse l'objet
#  arrêter la lumière et projeter son ombre ; il n'est simplement pas dessiné.
MASQUES_CAMERA = ("Plafond", "Mur_sud")

#  La zone de contrôle : le fond de la pièce SOMBRE, en fractions d'image.
#  Aucune lumière ne peut physiquement l'atteindre.
CONTROLE = (0.56, 0.86, 0.34, 0.62)


def matiere(nom, base, rugosite, emission=None, force=0.0):
    m = bpy.data.materials.new(nom)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*base, 1.0)
    p.inputs["Roughness"].default_value = rugosite
    if emission is not None:
        p.inputs["Emission Color"].default_value = (*emission, 1.0)
        p.inputs["Emission Strength"].default_value = force
    return m


_FACES = ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
          (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7))


def pave(nom, x0, x1, y0, y1, z0, z1, mat):
    hx, hy, hz = (x1 - x0) / 2, (y1 - y0) / 2, (z1 - z0) / 2
    coins = [(-hx, -hy, -hz), (hx, -hy, -hz), (hx, hy, -hz), (-hx, hy, -hz),
             (-hx, -hy, hz), (hx, -hy, hz), (hx, hy, hz), (-hx, hy, hz)]
    me = bpy.data.meshes.new(nom)
    me.from_pydata(coins, [], list(_FACES))
    me.validate()
    me.update()
    me.materials.append(mat)
    ob = bpy.data.objects.new(nom, me)
    ob.location = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def batir():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    mur = matiere("MUR", (0.855, 0.840, 0.815), 0.90)
    sol = matiere("SOL", (0.560, 0.450, 0.330), 0.55)
    refend = matiere("REFEND", (0.870, 0.855, 0.830), 0.90)

    pave("Sol", X0 - EP, X1 + EP, Y0 - EP, Y1 + EP, Z0 - EP, Z0, sol)
    pave("Plafond", X0 - EP, X1 + EP, Y0 - EP, Y1 + EP, Z1, Z1 + EP, mur)
    pave("Mur_nord", X0 - EP, X1 + EP, Y1, Y1 + EP, Z0, Z1, mur)
    pave("Mur_sud", X0 - EP, X1 + EP, Y0 - EP, Y0, Z0, Z1, mur)
    pave("Mur_est", X1, X1 + EP, Y0, Y1, Z0, Z1, mur)

    #  Le mur ouest, percé pour la fenêtre : quatre dalles autour du trou.
    pave("Ouest_bas", X0 - EP, X0, F_Y0, F_Y1, Z0, F_Z0, mur)
    pave("Ouest_haut", X0 - EP, X0, F_Y0, F_Y1, F_Z1, Z1, mur)
    pave("Ouest_sud", X0 - EP, X0, Y0, F_Y0, Z0, Z1, mur)
    pave("Ouest_nord", X0 - EP, X0, F_Y1, Y1, Z0, Z1, mur)

    #  LE REFEND. Plein, du sol au plafond, d'un mur à l'autre : aucune
    #  ouverture, aucun jour. Tout ce qui passera ne peut passer que par la
    #  sonde.
    pave("Refend", CX - CLOISON / 2, CX + CLOISON / 2,
         Y0, Y1, Z0, Z1, refend)


def eclairage():
    """Une nappe de ciel devant la fenêtre, côté éclairé uniquement."""
    d = bpy.data.lights.new("CIEL", type='AREA')
    d.shape = 'RECTANGLE'
    d.size, d.size_y = (F_Z1 - F_Z0) * 1.4, (F_Y1 - F_Y0) * 1.2
    d.energy = 900.0
    d.color = (0.86, 0.91, 1.00)
    ob = bpy.data.objects.new("CIEL", d)
    ob.location = (X0 - 0.45, (F_Y0 + F_Y1) / 2, (F_Z0 + F_Z1) / 2)
    #  UNE LAMPE SURFACIQUE ÉMET SUIVANT SON −Z LOCAL.
    #  Avec +90° autour de Y, −Z part vers −X : la nappe éclairait le dehors
    #  et tournait le dos à la fenêtre. Toute la scène sortait noire, pièce
    #  éclairée comprise, et j'ai commencé par soupçonner la sonde.
    ob.rotation_euler = (0.0, math.radians(-90.0), 0.0)
    bpy.context.collection.objects.link(ob)

    w = bpy.data.worlds.new("MONDE")
    w.use_nodes = True
    #  Un monde presque nul : sinon il éclairerait la pièce sombre par
    #  l'ambiante et on ne saurait plus ce qui vient de la fuite.
    w.node_tree.nodes["Background"].inputs[0].default_value = \
        (0.010, 0.011, 0.014, 1.0)
    bpy.context.scene.world = w


def camera():
    """
    Une COUPE, vue de trois quarts au-dessus, les deux pièces dans le même
    cadre.

    Premier essai : caméra DANS la pièce sombre, face au refend. C'est le
    cadrage qui décrit le mieux le sujet et le pire pour le montrer — une
    pièce noire photographiée à l'exposition d'une pièce éclairée est une
    image noire, fuite comprise. Moyenne relevée : 8,3/255 sur toute l'image.

    Il faut les deux côtés dans le champ : le clair donne l'échelle, et c'est
    par comparaison avec lui qu'on voit que le sombre ne devrait rien recevoir.
    """
    cd = bpy.data.cameras.new("CAM")
    cd.lens = 38.0
    ob = bpy.data.objects.new("CAM", cd)
    ob.location = (7.90, -8.70, 5.75)
    cible = (-0.10, 0.10, 1.15)
    from mathutils import Vector
    ob.rotation_euler = (Vector(cible) - ob.location) \
        .to_track_quat('-Z', 'Y').to_euler()
    bpy.context.collection.objects.link(ob)
    bpy.context.scene.camera = ob
    return ob


def sonde():
    d = bpy.data.lightprobes.new("SONDE", type='VOLUME')
    d.bake_samples = BAKE_SAMPLES
    d.surfel_density = SURFELS
    d.capture_world = True
    d.capture_indirect = True
    d.capture_emission = True
    ob = bpy.data.objects.new("SONDE", d)
    ob.location = ((X0 + X1) / 2, (Y0 + Y1) / 2, (Z0 + Z1) / 2)
    #  Le volume englobe les deux pièces et déborde derrière les murs.
    ob.scale = ((X1 - X0) / 2 + 0.25, (Y1 - Y0) / 2 + 0.25,
                (Z1 - Z0) / 2 + 0.25)
    bpy.context.collection.objects.link(ob)
    return ob


def reglages():
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_EEVEE_NEXT'
    sc.render.resolution_x, sc.render.resolution_y = RESOLUTION
    sc.render.image_settings.file_format = 'PNG'
    e = sc.eevee
    e.taa_render_samples = ECHANTILLONS
    #  Coupés tous les deux : ce sont les autres sources d'indirect. Il ne
    #  doit rester QUE la sonde, sinon on ne sait pas d'où vient la fuite.
    e.use_raytracing = False
    e.use_fast_gi = False
    e.use_shadows = True
    e.shadow_ray_count = 4
    e.gi_irradiance_pool_size = '512'
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - Base Contrast'


def maille(resolution):
    """La taille de maille, en mètres, sur chaque axe. C'est la grandeur qui
    décide de la fuite — pas le nombre de mailles."""
    s = bpy.data.objects["SONDE"].scale
    return tuple(2.0 * s[i] / resolution[i] for i in range(3))


def mesurer(chemin):
    import numpy as np
    from PIL import Image
    im = Image.open(chemin).convert("RGB")
    x0, x1, y0, y1 = CONTROLE
    w, h = im.size
    z = np.asarray(im.crop((int(w * x0), int(h * y0),
                            int(w * x1), int(h * y1))), dtype=float)
    return float(z.mean())


def passe(p, nom, resolution):
    sc = bpy.context.scene
    if resolution is None:
        p.hide_render = True
        bpy.ops.object.lightprobe_cache_free(subset='ALL')
    else:
        p.hide_render = False
        p.data.resolution_x, p.data.resolution_y, p.data.resolution_z = \
            resolution
        bpy.context.view_layer.objects.active = p
        bpy.ops.object.lightprobe_cache_free(subset='ALL')
        bpy.ops.object.lightprobe_cache_bake(subset='ALL')
    chemin = os.path.join(DOSSIER, nom + ".png")
    sc.render.filepath = chemin
    bpy.ops.render.render(write_still=True)
    v = mesurer(chemin)
    m = maille(resolution) if resolution else None
    print("  %-12s %-14s maille %-22s  mur sombre : %6.2f/255"
          % (nom, str(resolution) if resolution else "aucune",
             ("%.2f × %.2f × %.2f m" % m) if m else "—", v))
    return {"nom": nom, "resolution": list(resolution) if resolution else None,
            "maille_m": [round(t, 3) for t in m] if m else None,
            "luminance": round(v, 3),
            "image": os.path.relpath(chemin, RACINE)}


def main():
    os.makedirs(DOSSIER, exist_ok=True)
    batir()
    eclairage()
    camera()
    reglages()
    p = sonde()

    for nom in MASQUES_CAMERA:
        bpy.data.objects[nom].visible_camera = False

    r = [passe(p, "grossiere", GROSSIERE),
         passe(p, "fine", FINE),
         passe(p, "sans-sonde", None)]

    par = {x["nom"]: x for x in r}
    plancher = par["sans-sonde"]["luminance"]
    fuite = par["grossiere"]["luminance"] - plancher
    reste = par["fine"]["luminance"] - plancher
    print()
    print("  fuite de la grille grossiere : %+.2f/255 au-dessus du plancher"
          % fuite)
    print("  reste avec la grille fine    : %+.2f/255  (%.0f %% de moins)"
          % (reste, 100.0 * (1.0 - reste / max(fuite, 1e-6))))

    donnees = {"cloison_m": CLOISON, "surfels": SURFELS,
               "bake_samples": BAKE_SAMPLES, "resolution": list(RESOLUTION),
               "echantillons": ECHANTILLONS, "controle": list(CONTROLE),
               "plancher": plancher, "fuite": round(fuite, 3),
               "reste": round(reste, 3), "passes": r}
    with open(JOURNAL, "w") as f:
        json.dump(donnees, f, indent=2)
    print("  -> %s" % JOURNAL)


if __name__ == "__main__":
    main()
