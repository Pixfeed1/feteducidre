# -*- coding: utf-8 -*-
"""
PIXFEED - LE CHAMP ELECTRIQUE. 8 secondes, 240 images a 30 i/s, 1080x1920.
Blender 4.0 (EEVEE).

POURQUOI LES VERSIONS PRECEDENTES ETAIENT MOLLES
  Elles etaient justes et plates. La recherche sur le metier donne la
  raison en une phrase : "le meme mouvement en 6 images est vif, en 30 il
  est languissant". Les miens duraient 16 a 30 images, tous lisses aux deux
  bouts (EASE_IN_OUT) : c'est la definition du mou. Trois autres manques,
  tous documentes comme fondamentaux :

    - l'EASE OUT BACK : le mouvement depasse sa cible et revient. Sans ce
      depassement, rien n'a de poids ;
    - le DECALAGE court : une image d'ecart entre voisines, du centre vers
      les bords. Le mien etait de vingt ;
    - l'ANTICIPATION : un petit mouvement CONTRAIRE avant le coup. C'est ce
      qui fait qu'on sent venir, donc qu'on regarde ;
    - l'ACCENT a l'impact : une image de flash. L'oeil enregistre le
      changement avant de comprendre l'image.

LA PARTITION - un evenement toutes les demi-secondes, jamais de plateau
    0,1 s  LE CHAMP SE CONSTRUIT   chaque lettre nait d'une echelle nulle,
                                   en depassement, du centre vers les bords
    1,4 s  LA MOSAIQUE             le fond claque en arriere en 7 images,
                                   quinze petites marques restent devant
    2,5 s  LA RESPIRATION          tout revient au plan - c'est
                                   l'anticipation du coup suivant
    2,8 s  LA MARQUE               le fond s'effondre, la grande marque
                                   bondit vers l'oeil, FLASH a l'impact
    3,3 s  LE COURANT              il traverse la marque en 0,8 s, chaque
                                   lettre gonfle et vire au violet
    5,3 s  LES PULSATIONS          deux battements de la marque entiere
    5,9 s  L'EFFONDREMENT          tout retombe et se replie a l'echelle
                                   nulle : l'image finale est la premiere

TOUT LE CHAMP PARTICIPE. Les 3 200 lettres bougent, aucune ne reste
plantee : c'etait le reproche juste fait a la version d'avant.
"""

import bpy
import math
import random
from collections import deque

FPS = 30
DUREE = 240
RESOLUTION = (1080, 1920)
MOT = "PIXFEED"

# LA CAMERA : frontale, courte focale, pres du champ.
CAM_DISTANCE = 12.4
CAPTEUR = 24.0
VUE_H = 11.0
VUE_L = VUE_H * RESOLUTION[0] / RESOLUTION[1]

TAILLE_GLYPHE = 0.135
PAS_X = 0.175
PAS_Z = 0.235
MARGE = 1.6

LOGO_TAILLE = 5.10
LOGO_JEU = 0.444
PETIT_TAILLE = 1.72
PETIT_PAS = (2.30, 2.55)
PETIT_COLONNES = 3
PETIT_RANGEES = 5

RECUL = 5.60                     # le fond s'efface
RECUL_PETIT = 2.60
AVANCEE = -0.40                  # la figure bondit vers l'oeil

# LE TEMPS (images). Chaque coup dure 7 images, pas 30.
COUP = 7
ANTICIPE = 4                     # le petit mouvement contraire, avant
T_NAISSANCE = 3
T_MOSAIQUE = 42
T_RESPIRE = 76
T_MARQUE = 84
T_FLASH = 92
T_COURANT = 100
TRAVERSEE = 24.0                 # 0,8 s pour tout traverser
T_PULSE = 160
T_EFFONDRE = 178
T_BOUCLE = 232

POP = 1.55
POP_DUREE = 4

LETTRE = (0.925, 0.925, 0.945)
FOND = (0.043, 0.043, 0.055)
VIOLET = (0.58, 0.26, 0.98)
FORCE_ALLUM = 3.0


def srgb_vers_lineaire(c):
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4
                 for x in c)


def vif(ob, chemin, indice=-1):
    """
    EASE OUT BACK sur toutes les cles d'un canal : le mouvement depasse sa
    cible puis revient. C'est ce depassement qui donne du poids - un lissage
    symetrique (EASE_IN_OUT) donne du coton.
    """
    if ob.animation_data is None or ob.animation_data.action is None:
        return
    for fc in ob.animation_data.action.fcurves:
        if fc.data_path != chemin or (indice >= 0 and fc.array_index != indice):
            continue
        for kp in fc.keyframe_points:
            kp.interpolation = "BACK"
            kp.easing = "EASE_OUT"
            kp.back = 1.5


def vider_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def monde():
    """
    Le fond, et LE FLASH : deux images de blanc a l'impact. L'oeil
    enregistre un changement de luminance avant de comprendre une forme -
    c'est l'accent qui manquait a toutes les versions precedentes.
    """
    m = bpy.data.worlds.new("MONDE")
    m.use_nodes = True
    n = m.node_tree.nodes["Background"]
    c = n.inputs["Color"]
    # 0.72 sur trois images LAVAIT l'image au moment meme de la
    # revelation : le fond passait plus clair que les lettres, qui
    # disparaissaient. Un accent doit se sentir, pas cacher ce qu'il
    # annonce - 0.30 sur deux images.
    for img, val in ((T_FLASH - 2, FOND), (T_FLASH, (0.30, 0.28, 0.38)),
                     (T_FLASH + 2, FOND)):
        c.default_value = (*srgb_vers_lineaire(val), 1.0)
        c.keyframe_insert("default_value", frame=img)
    for fc in m.node_tree.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = "EXPO"
            kp.easing = "EASE_OUT"
    bpy.context.scene.world = m


def materiau_lettre():
    """Un seul materiau : profondeur par le Y du monde, couleur par l'objet."""
    mat = bpy.data.materials.new("LETTRE")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Position"], sep.inputs["Vector"])
    prof = nt.nodes.new("ShaderNodeMapRange")
    prof.inputs["From Min"].default_value = 0.0
    prof.inputs["From Max"].default_value = RECUL
    prof.inputs["To Min"].default_value = 1.0
    prof.inputs["To Max"].default_value = 0.04
    prof.clamp = True
    nt.links.new(sep.outputs["Y"], prof.inputs["Value"])
    info = nt.nodes.new("ShaderNodeObjectInfo")
    sepc = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(info.outputs["Color"], sepc.inputs["Color"])
    allum = nt.nodes.new("ShaderNodeMapRange")
    allum.inputs["From Min"].default_value = LETTRE[1]
    allum.inputs["From Max"].default_value = VIOLET[1]
    allum.inputs["To Min"].default_value = 0.0
    allum.inputs["To Max"].default_value = 1.0
    allum.clamp = True
    nt.links.new(sepc.outputs["Green"], allum.inputs["Value"])
    boost = nt.nodes.new("ShaderNodeMapRange")
    boost.inputs["To Min"].default_value = 1.0
    boost.inputs["To Max"].default_value = FORCE_ALLUM
    boost.clamp = True
    nt.links.new(allum.outputs["Result"], boost.inputs["Value"])
    mult = nt.nodes.new("ShaderNodeMath")
    mult.operation = "MULTIPLY"
    nt.links.new(prof.outputs["Result"], mult.inputs[0])
    nt.links.new(boost.outputs["Result"], mult.inputs[1])
    emi = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(info.outputs["Color"], emi.inputs["Color"])
    nt.links.new(mult.outputs["Value"], emi.inputs["Strength"])
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (260, 0)
    nt.links.new(emi.outputs["Emission"], out.inputs["Surface"])
    return mat


def glyphe(lettre, mat):
    courbe = bpy.data.curves.new("C_" + lettre, type="FONT")
    courbe.body = lettre
    courbe.size = TAILLE_GLYPHE
    courbe.align_x = "CENTER"
    courbe.align_y = "CENTER"
    ob = bpy.data.objects.new("T_" + lettre, courbe)
    bpy.context.collection.objects.link(ob)
    dep = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dep))
    me.name = "M_" + lettre
    bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.curves.remove(courbe)
    me.materials.append(mat)
    return me


def rectangles_logo(hauteur, cx=0.0, cz=0.0):
    P = [0.0, 1.0, 1.0 + LOGO_JEU, 2.0 + LOGO_JEU,
         2.0 + 2 * LOGO_JEU, 3.0 + 2 * LOGO_JEU]
    E = [(0, 0, 5, 1), (4, 0, 5, 3), (0, 2, 3, 3),
         (2, 2, 3, 5), (0, 4, 1, 5)]
    k = hauteur / P[5]
    m = P[5] / 2.0
    out = []
    for a, b, c, d in E:
        x0, x1 = (P[a] - m) * k + cx, (P[c] - m) * k + cx
        z1, z0 = (m - P[b]) * k + cz, (m - P[d]) * k + cz
        out.append(((x0 + x1) / 2.0, (z0 + z1) / 2.0,
                    (x1 - x0) / 2.0, (z1 - z0) / 2.0))
    return out


def caler(blocs):
    """Les bords poses ENTRE deux lettres : le contour fait un escalier
    franc au lieu de baver sur des lettres a moitie dedans."""
    def milieu(v, pas):
        return (math.floor(v / pas - 0.5) + 0.5) * pas
    out = []
    for cx, cz, hl, hh in blocs:
        x0, x1 = milieu(cx - hl, PAS_X), milieu(cx + hl, PAS_X)
        z0, z1 = milieu(cz - hh, PAS_Z), milieu(cz + hh, PAS_Z)
        out.append(((x0 + x1) / 2.0, (z0 + z1) / 2.0,
                    (x1 - x0) / 2.0, (z1 - z0) / 2.0))
    return out


def dedans(blocs, x, z):
    for cx, cz, hl, hh in blocs:
        if abs(x - cx) <= hl and abs(z - cz) <= hh:
            return True
    return False


def construire():
    mat = materiau_lettre()
    maillages = {c: glyphe(c, mat) for c in set(MOT)}
    grand = caler(rectangles_logo(LOGO_TAILLE))
    tuiles = []
    for i in range(PETIT_COLONNES):
        for j in range(PETIT_RANGEES):
            cx = (i - (PETIT_COLONNES - 1) / 2.0) * PETIT_PAS[0]
            cz = (j - (PETIT_RANGEES - 1) / 2.0) * PETIT_PAS[1]
            tuiles.append(caler(rectangles_logo(PETIT_TAILLE, cx, cz)))
    nx = int((VUE_L / 2.0 + MARGE) / PAS_X)
    nz = int((VUE_H / 2.0 + MARGE) / PAS_Z)
    lettres, k = [], 0
    for iz in range(-nz, nz + 1):
        for ix in range(-nx, nx + 1):
            x, z = ix * PAS_X, iz * PAS_Z
            c = MOT[k % len(MOT)]
            k += 1
            ob = bpy.data.objects.new("G_%05d" % len(lettres), maillages[c])
            ob.location = (x, 0.0, z)
            ob.rotation_euler = (math.pi / 2.0, 0.0, 0.0)
            ob.color = (*LETTRE, 1.0)
            ob.scale = (0.0, 0.0, 0.0)
            bpy.context.collection.objects.link(ob)
            petit = any(dedans(t, x, z) for t in tuiles)
            lettres.append({"ob": ob, "ix": ix, "iz": iz, "x": x, "z": z,
                            "grand": dedans(grand, x, z), "petit": petit,
                            "r": math.hypot(x / 1.4, z)})
    return lettres


def animer(lettres):
    """
    Tous les coups durent COUP images, avec depassement, et se propagent du
    centre vers les bords a une image d'ecart. Avant chaque coup, une
    ANTICIPATION : un petit mouvement contraire.
    """
    rmax = max(l["r"] for l in lettres)
    alea = random.Random(11)
    for l in lettres:
        ob, r = l["ob"], l["r"] / rmax
        d = r * 16.0                              # le decalage, court
        ech, prof = [], []

        # 1. LA NAISSANCE : d'une echelle nulle, en depassement
        ech += [(T_NAISSANCE + d, 0.0), (T_NAISSANCE + d + COUP + 2, 1.0)]
        prof += [(T_NAISSANCE + d, 0.0)]

        # 2. LA MOSAIQUE : le fond claque en arriere, le motif reste devant
        if not l["petit"]:
            prof += [(T_MOSAIQUE + d * 0.4 - ANTICIPE, -0.12),
                     (T_MOSAIQUE + d * 0.4, 0.0),
                     (T_MOSAIQUE + d * 0.4 + COUP, RECUL_PETIT)]
        else:
            prof += [(T_MOSAIQUE + d * 0.4, 0.0),
                     (T_MOSAIQUE + d * 0.4 + COUP, AVANCEE * 0.5)]

        # 3. LA RESPIRATION : tout revient au plan - anticipation du coup
        prof += [(T_RESPIRE, prof[-1][1]), (T_RESPIRE + COUP - 1, 0.0)]

        # 4. LA MARQUE : le fond s'effondre, la figure bondit vers l'oeil
        if l["grand"]:
            prof += [(T_MARQUE - ANTICIPE, 0.20),
                     (T_MARQUE, 0.0), (T_MARQUE + COUP, AVANCEE)]
        else:
            prof += [(T_MARQUE - ANTICIPE, -0.15),
                     (T_MARQUE + d * 0.25, 0.0),
                     (T_MARQUE + d * 0.25 + COUP + 2, RECUL)]

        # 5. L'EFFONDREMENT : tout retombe, puis se replie a l'echelle nulle
        prof += [(T_EFFONDRE + d * 0.5, prof[-1][1]),
                 (T_EFFONDRE + d * 0.5 + COUP + 3, 0.0)]
        ech += [(T_BOUCLE - 26 + d * 0.6, 1.0),
                (T_BOUCLE - 26 + d * 0.6 + COUP + 3, 0.0)]

        for img, v in prof:
            ob.location.y = v
            ob.keyframe_insert("location", index=1, frame=int(round(img)))
        for img, s in ech:
            ob.scale = (s, s, s)
            ob.keyframe_insert("scale", frame=int(round(img)))
        vif(ob, "location", 1)
        vif(ob, "scale")


def contaminer(lettres):
    """
    LE COURANT : parcours en largeur dans les cases de la marque, huit
    voisins (en quatre, le pied du logo n'est pas connexe et le courant y
    reste enferme), avec un ARC vers les morceaux separes. La cadence se
    calcule : on fixe la traversee totale et on en deduit le delai.

    Chaque lettre atteinte GONFLE en quatre images (le pop) et vire au
    violet. Puis la marque entiere PULSE deux fois - c'est le battement qui
    fait exister l'objet pendant qu'il tient.
    """
    cases = {(l["ix"], l["iz"]): l["ob"] for l in lettres if l["grand"]}
    if not cases:
        return
    V = [(a, b) for a in (-1, 0, 1) for b in (-1, 0, 1) if (a, b) != (0, 0)]

    def propager(depart, etape, depuis):
        etape[depart] = depuis
        f = deque([depart])
        while f:
            c = f.popleft()
            for a, b in V:
                v = (c[0] + a, c[1] + b)
                if v in cases and v not in etape:
                    etape[v] = etape[c] + 1
                    f.append(v)

    foyer = min(cases, key=lambda c: (c[1], c[0]))
    etape = {}
    propager(foyer, etape, 0)
    while len(etape) < len(cases):
        best = None
        for r in [c for c in cases if c not in etape]:
            for a in etape:
                d2 = (r[0] - a[0]) ** 2 + (r[1] - a[1]) ** 2
                if best is None or d2 < best[0]:
                    best = (d2, r, a)
        d2, r, a = best
        propager(r, etape, etape[a] + max(2, int(math.sqrt(d2) * 2)))

    profond = max(etape.values())
    pas = TRAVERSEE / float(max(1, profond))
    for case, n in etape.items():
        ob = cases[case]
        t0 = T_COURANT + n * pas
        for img, coul in ((t0, LETTRE), (t0 + 3, VIOLET),
                          (T_EFFONDRE, VIOLET), (T_EFFONDRE + 12, LETTRE)):
            ob.color = (*coul, 1.0)
            ob.keyframe_insert("color", frame=int(round(img)))
        gonfle = [(t0, 1.0), (t0 + POP_DUREE, POP), (t0 + POP_DUREE * 3, 1.0)]
        # LES DEUX PULSATIONS de la marque entiere
        for p in (T_PULSE, T_PULSE + 14):
            gonfle += [(p, 1.0), (p + 3, 1.22), (p + 8, 1.0)]
        for img, s in gonfle:
            ob.scale = (s, s, s)
            ob.keyframe_insert("scale", frame=int(round(img)))
    print("Courant : %d lettres, %d etapes, traversee %.1f s"
          % (len(cases), profond, TRAVERSEE / FPS))


def placer_camera():
    cd = bpy.data.cameras.new("CAM")
    cd.sensor_fit = "VERTICAL"
    cd.sensor_height = CAPTEUR
    cd.lens = CAPTEUR * CAM_DISTANCE / VUE_H
    cam = bpy.data.objects.new("CAM", cd)
    bpy.context.collection.objects.link(cam)
    cam.rotation_euler = (math.pi / 2.0, 0.0, 0.0)
    cd.dof.use_dof = True
    cd.dof.focus_distance = CAM_DISTANCE
    cd.dof.aperture_fstop = 0.05
    # LE COUP DE ZOOM a l'impact : la camera recule d'un rien en trois
    # images puis revient. C'est le "kick" - sans lui l'impact n'a pas de
    # corps.
    for img, d in ((1, CAM_DISTANCE + 0.9), (T_MARQUE, CAM_DISTANCE + 0.5),
                   (T_MARQUE + 3, CAM_DISTANCE + 1.15),
                   (T_MARQUE + 12, CAM_DISTANCE),
                   (T_EFFONDRE, CAM_DISTANCE - 0.35),
                   (T_BOUCLE, CAM_DISTANCE + 0.9)):
        cam.location = (0.0, -d, 0.0)
        cam.keyframe_insert("location", frame=img)
        cd.dof.focus_distance = d
        cd.dof.keyframe_insert("focus_distance", frame=img)
    for act in (cam.animation_data.action, cd.animation_data.action):
        for fc in act.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = "EXPO"
                kp.easing = "EASE_OUT"
    bpy.context.scene.camera = cam


def reglages():
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.eevee.taa_render_samples = 16
    sc.eevee.use_bloom = True
    sc.eevee.bloom_threshold = 1.05
    sc.eevee.bloom_intensity = 0.08
    sc.eevee.bloom_radius = 5.0
    # LE FLOU DE MOUVEMENT : a ces vitesses, il n'est plus un luxe. Sans
    # lui, un deplacement de sept images se lit comme une saccade.
    sc.eevee.use_motion_blur = True
    sc.eevee.motion_blur_shutter = 0.42
    sc.render.resolution_x, sc.render.resolution_y = RESOLUTION
    sc.render.fps = FPS
    sc.frame_start, sc.frame_end = 1, DUREE
    sc.render.image_settings.file_format = "PNG"


def main():
    vider_scene()
    monde()
    lettres = construire()
    animer(lettres)
    contaminer(lettres)
    placer_camera()
    reglages()
    print("PIXFEED : %d lettres, %d dans la marque, coups de %d images"
          % (len(lettres), sum(1 for l in lettres if l["grand"]), COUP))


main()
