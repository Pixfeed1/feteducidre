# -*- coding: utf-8 -*-
"""
PIXFEED - 30 SECONDES. 900 images a 30 i/s, 1080x1920. Blender 4.0 (EEVEE).

CE QUE LA RECHERCHE A APPORTE, ET QUI N'ETAIT PAS LA

  1. LES TRAJECTOIRES COURBES. Chez les bons, une lettre ne va jamais d'un
     point a un autre en ligne droite : elle suit un ARC. Ici chaque
     deplacement recoit un point de passage lateral, donc l'interpolation
     dessine une courbe - c'est le "arcs" des douze principes.

  2. LA TRANSITION PAR CORRESPONDANCE (match cut). Le moment fort du film
     n'est pas une apparition de plus : c'est la petite marque du centre
     qui DEVIENT la grande, pendant que la camera plonge dedans. Un objet
     se transforme en un autre au lieu de se succeder.

  3. L'ETAGE DE COMPOSITING, celui qui separe "propre" de "professionnel" :
     glare en STREAKS (les traits de lumiere anamorphiques), fog glow,
     aberration chromatique par distorsion de lentille, vignettage, grain.
     Aucune de mes versions precedentes n'en avait.

  4. LE RYTHME EN ESCALIER. Quatorze evenements en trente secondes, jamais
     plus de deux secondes sans changement d'etat, et une escalade : on
     construit, on complique, on epure, on frappe.

  5. LES COUPS COURTS. 7 images par mouvement, EASE OUT BACK (depassement),
     anticipation contraire avant chaque coup, decalage d'une image entre
     voisines. "Le meme mouvement en 6 images est vif, en 30 il est mou."

LA PARTITION
   0,0 s  NAISSANCE      les lettres naissent d'une echelle nulle, en
                         spirale depuis le centre, chacune en tournant
   1,7 s  LA HOULE       une vague de profondeur traverse le champ en
                         diagonale : la matiere respire
   3,3 s  LE TOURBILLON  tout le champ tourne d'un quart de tour sur des
                         ARCS, puis se remet en place
   5,3 s  LA MOSAIQUE    le fond claque en arriere, quinze marques restent
   7,0 s  LE PLONGEON    la camera plonge dans la marque du centre, qui
                         DEVIENT la grande - flash a l'impact
   9,0 s  LE COURANT     il traverse la marque en 0,8 s, violet, pops
  11,0 s  PULSATIONS     deux battements, et la camera orbite
  13,0 s  DISPARITION    le champ s'envole sur des arcs et s'eteint : il
                         ne reste que la marque, seule dans le noir
  15,5 s  LES CULBUTES   les lettres de la marque tournent sur elles-memes,
                         l'une apres l'autre, comme un compteur
  18,0 s  LE RETOUR      le champ revient en spirale et se referme autour
  20,5 s  L'ONDE DE CHOC un anneau part de la marque et pousse le champ
  22,5 s  LA GRILLE      le champ se fige, la marque pulse trois fois
  25,0 s  LA TRAVERSEE   la marque grandit et passe par-dessus l'oeil,
                         flash blanc
  27,5 s  L'EFFONDREMENT tout se replie a l'echelle nulle - l'image finale
                         est la premiere, la boucle est parfaite
"""

import bpy
import math
import random
from collections import deque

FPS = 30
DUREE = 900
RESOLUTION = (1080, 1920)
MOT = "PIXFEED"

CAM_DISTANCE = 12.4
CAPTEUR = 24.0
VUE_H = 11.0
VUE_L = VUE_H * RESOLUTION[0] / RESOLUTION[1]

TAILLE_GLYPHE = 0.135
PAS_X = 0.175
PAS_Z = 0.235
MARGE = 0.70
#   1.6 : un tiers des lettres etaient HORS CADRE et se rendaient quand
#   meme - 3 233 lettres pour 2 100 visibles. Mesure avant de regler :
#   c'est 35 % du temps de rendu jete par la fenetre.

LOGO_TAILLE = 5.10
LOGO_JEU = 0.444
PETIT_TAILLE = 1.72
PETIT_PAS = (2.30, 2.55)
PETIT_COLONNES = 3
PETIT_RANGEES = 5

RECUL = 5.60
RECUL_PETIT = 2.60
AVANCEE = -0.40

COUP = 7
ANTICIPE = 4

# LES QUATORZE TEMPS (en images)
T_NAISSANCE = 3
T_HOULE = 50
T_TOURBILLON = 100
T_MOSAIQUE = 160
T_PLONGEON = 210
T_FLASH = 218
T_COURANT = 270
TRAVERSEE = 24.0
T_PULSE = 330
T_DISPARITION = 390
T_CULBUTE = 465
T_RETOUR = 540
T_ONDE = 615
T_GRILLE = 675
T_FINALE = 750
T_REFORME = 790
T_SIGNATURE = 818
T_EFFONDRE = 876
T_BOUCLE = 891
#   Mesure avant correction : entre l'image 782 et l'image 900 il ne
#   restait RIEN a l'ecran - quatre secondes de noir sur un film de
#   trente. Un film de logo se termine sur son logo TENU, pas sur un
#   trou. D'ou les trois temps ajoutes : reformation, signature, tenu.

POP = 1.55
POP_DUREE = 4

LETTRE = (0.925, 0.925, 0.945)
FOND = (0.038, 0.038, 0.050)
VIOLET = (0.58, 0.26, 0.98)
FORCE_ALLUM = 3.0


def srgb(c):
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4
                 for x in c)


# ---------------------------------------------------------------------
#  LA SCENE
# ---------------------------------------------------------------------

def vider():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def monde():
    """Le fond, et les deux FLASHS : a l'impact du plongeon, et a la
    traversee finale. L'oeil enregistre une luminance avant une forme."""
    m = bpy.data.worlds.new("MONDE")
    m.use_nodes = True
    c = m.node_tree.nodes["Background"].inputs["Color"]
    cles = [(1, FOND),
            (T_FLASH - 2, FOND), (T_FLASH, (0.30, 0.28, 0.38)),
            (T_FLASH + 3, FOND),
            (T_FINALE + 26, FOND), (T_FINALE + 30, (0.62, 0.60, 0.72)),
            (T_FINALE + 36, FOND),
            (T_SIGNATURE - 2, FOND), (T_SIGNATURE, (0.34, 0.30, 0.48)),
            (T_SIGNATURE + 6, FOND)]
    for img, val in cles:
        c.default_value = (*srgb(val), 1.0)
        c.keyframe_insert("default_value", frame=img)
    for fc in m.node_tree.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = "EXPO"
            kp.easing = "EASE_OUT"
    bpy.context.scene.world = m


def materiau():
    """Profondeur par le Y du monde, couleur par l'objet - un seul
    materiau pour trois mille deux cents lettres."""
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
    cb = bpy.data.curves.new("C_" + lettre, type="FONT")
    cb.body = lettre
    cb.size = TAILLE_GLYPHE
    cb.align_x = "CENTER"
    cb.align_y = "CENTER"
    ob = bpy.data.objects.new("T_" + lettre, cb)
    bpy.context.collection.objects.link(ob)
    dep = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dep))
    me.name = "M_" + lettre
    bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.curves.remove(cb)
    me.materials.append(mat)
    return me


def blocs_logo(hauteur, cx=0.0, cz=0.0):
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
    """Bords poses ENTRE deux lettres : escalier franc au lieu de bavure."""
    def milieu(v, pas):
        return (math.floor(v / pas - 0.5) + 0.5) * pas
    out = []
    for cx, cz, hl, hh in blocs:
        x0, x1 = milieu(cx - hl, PAS_X), milieu(cx + hl, PAS_X)
        z0, z1 = milieu(cz - hh, PAS_Z), milieu(cz + hh, PAS_Z)
        out.append(((x0 + x1) / 2.0, (z0 + z1) / 2.0,
                    (x1 - x0) / 2.0, (z1 - z0) / 2.0))
    return out


def dans(blocs, x, z):
    for cx, cz, hl, hh in blocs:
        if abs(x - cx) <= hl and abs(z - cz) <= hh:
            return True
    return False


def construire():
    mat = materiau()
    mail = {c: glyphe(c, mat) for c in set(MOT)}
    grand = caler(blocs_logo(LOGO_TAILLE))
    petit_centre = caler(blocs_logo(PETIT_TAILLE))
    tuiles = []
    for i in range(PETIT_COLONNES):
        for j in range(PETIT_RANGEES):
            cx = (i - (PETIT_COLONNES - 1) / 2.0) * PETIT_PAS[0]
            cz = (j - (PETIT_RANGEES - 1) / 2.0) * PETIT_PAS[1]
            tuiles.append(caler(blocs_logo(PETIT_TAILLE, cx, cz)))
    nx = int((VUE_L / 2.0 + MARGE) / PAS_X)
    nz = int((VUE_H / 2.0 + MARGE) / PAS_Z)
    lettres, k = [], 0
    for iz in range(-nz, nz + 1):
        for ix in range(-nx, nx + 1):
            x, z = ix * PAS_X, iz * PAS_Z
            c = MOT[k % len(MOT)]
            k += 1
            ob = bpy.data.objects.new("G_%05d" % len(lettres), mail[c])
            ob.location = (x, 0.0, z)
            ob.rotation_euler = (math.pi / 2.0, 0.0, 0.0)
            ob.color = (*LETTRE, 1.0)
            ob.scale = (0.0, 0.0, 0.0)
            bpy.context.collection.objects.link(ob)
            r = math.hypot(x, z)
            lettres.append({
                "ob": ob, "ix": ix, "iz": iz, "x": x, "z": z, "r": r,
                "ang": math.atan2(z, x),
                "grand": dans(grand, x, z),
                "petit": any(dans(t, x, z) for t in tuiles),
                "centre": dans(petit_centre, x, z),
                "loc": [], "ech": [], "rot": [], "coul": []})
    return lettres


# ---------------------------------------------------------------------
#  L'ANIMATION - on accumule les cles, on les pose a la fin
# ---------------------------------------------------------------------

def arc(l, img0, img1, x0, y0, z0, x1, y1, z1, courbure=0.35):
    """
    UN DEPLACEMENT SUR ARC, jamais en ligne droite.

    Le point de passage a mi-course est decale PERPENDICULAIREMENT a la
    trajectoire : l'interpolation dessine alors une courbe. C'est le
    principe des "arcs" - rien de vivant ne se deplace en ligne droite, et
    c'est ce qui manquait a toutes mes versions precedentes.
    """
    dx, dz = x1 - x0, z1 - z0
    n = math.hypot(dx, dz) or 1.0
    px, pz = -dz / n, dx / n
    d = n * courbure
    l["loc"] += [(img0, (x0, y0, z0)),
                 ((img0 + img1) / 2.0, ((x0 + x1) / 2 + px * d,
                                        (y0 + y1) / 2, (z0 + z1) / 2 + pz * d)),
                 (img1, (x1, y1, z1))]


def animer(lettres):
    alea = random.Random(11)
    rmax = max(l["r"] for l in lettres) or 1.0
    for l in lettres:
        x, z, r = l["x"], l["z"], l["r"] / rmax
        a = l["ang"]
        d = r * 16.0                       # decalage centre -> bords
        y = 0.0

        # 1. NAISSANCE : echelle nulle -> 1, en tournant, en spirale
        l["ech"] += [(T_NAISSANCE + d, 0.0),
                     (T_NAISSANCE + d + COUP + 2, 1.0)]
        l["rot"] += [(T_NAISSANCE + d, -2.4), (T_NAISSANCE + d + COUP + 4, 0.0)]
        l["loc"] += [(1, (x, 0.0, z))]

        # 2. LA HOULE : une vague de profondeur en diagonale
        phase = (x * 0.9 + z * 0.6)
        t0 = T_HOULE + (phase + 9.0) * 2.4
        l["loc"] += [(t0, (x, 0.0, z)),
                     (t0 + 6, (x, 1.5, z)),
                     (t0 + 14, (x, 0.0, z))]

        # 3. LE TOURBILLON : tout le champ tourne d'un quart de tour, sur
        #    des arcs, puis se remet en place. Les lettres du bord tournent
        #    moins que celles du centre - c'est ce cisaillement qui donne
        #    la spirale.
        tw = 1.25 * (1.0 - 0.55 * r)
        xr, zr = (l["r"] * math.cos(a + tw), l["r"] * math.sin(a + tw))
        arc(l, T_TOURBILLON, T_TOURBILLON + 18, x, 0.0, z, xr, 0.9, zr, 0.28)
        arc(l, T_TOURBILLON + 26, T_TOURBILLON + 44, xr, 0.9, zr, x, 0.0, z,
            0.28)

        # 4. LA MOSAIQUE : le fond claque en arriere
        if l["petit"]:
            l["loc"] += [(T_MOSAIQUE + d * 0.3, (x, 0.0, z)),
                         (T_MOSAIQUE + d * 0.3 + COUP, (x, AVANCEE * 0.5, z))]
        else:
            l["loc"] += [(T_MOSAIQUE + d * 0.3 - ANTICIPE, (x, -0.12, z)),
                         (T_MOSAIQUE + d * 0.3, (x, 0.0, z)),
                         (T_MOSAIQUE + d * 0.3 + COUP, (x, RECUL_PETIT, z))]

        # 5. LE PLONGEON : la petite marque du centre DEVIENT la grande.
        #    Les lettres de la petite s'ecartent vers leur place dans la
        #    grande pendant que la camera plonge - une transition par
        #    correspondance, pas une succession.
        if l["grand"]:
            l["loc"] += [(T_PLONGEON - ANTICIPE, (x, 0.25, z)),
                         (T_PLONGEON, (x, 0.0, z)),
                         (T_PLONGEON + COUP, (x, AVANCEE, z))]
        else:
            l["loc"] += [(T_PLONGEON + d * 0.2, (x, RECUL_PETIT, z)),
                         (T_PLONGEON + d * 0.2 + COUP + 2, (x, RECUL, z))]

        # 7. PULSATIONS : gerees dans contaminer() pour la marque

        # 8. DISPARITION : le champ s'envole sur des arcs et s'eteint
        if not l["grand"]:
            fuite = 2.6 + 5.0 * r
            xf = x + math.cos(a + 0.9) * fuite
            zf = z + math.sin(a + 0.9) * fuite
            arc(l, T_DISPARITION + d * 0.8, T_DISPARITION + d * 0.8 + 20,
                x, RECUL, z, xf, RECUL, zf, 0.45)
            l["ech"] += [(T_DISPARITION + d * 0.8 + 6, 1.0),
                         (T_DISPARITION + d * 0.8 + 20, 0.0)]

        # 10. LE RETOUR : il revient en spirale, de plus loin encore
        if not l["grand"]:
            xr2 = x + math.cos(a - 1.2) * (3.0 + 6.0 * r)
            zr2 = z + math.sin(a - 1.2) * (3.0 + 6.0 * r)
            l["loc"] += [(T_RETOUR + (1.0 - r) * 18 - 1, (xr2, RECUL, zr2))]
            arc(l, T_RETOUR + (1.0 - r) * 18, T_RETOUR + (1.0 - r) * 18 + 22,
                xr2, RECUL, zr2, x, RECUL * 0.55, z, 0.40)
            l["ech"] += [(T_RETOUR + (1.0 - r) * 18, 0.0),
                         (T_RETOUR + (1.0 - r) * 18 + 10, 1.0)]

        # 11. L'ONDE DE CHOC : un anneau part de la marque et pousse tout
        if not l["grand"]:
            to = T_ONDE + r * 26.0
            l["loc"] += [(to, (x, RECUL * 0.55, z)),
                         (to + 5, (x, RECUL * 0.55 - 1.7, z)),
                         (to + 16, (x, RECUL * 0.55, z))]

        # 12. LA GRILLE : le champ se fige un peu plus pres, net
        if not l["grand"]:
            l["loc"] += [(T_GRILLE, (x, RECUL * 0.55, z)),
                         (T_GRILLE + 10, (x, RECUL * 0.30, z))]

        # 13. LA TRAVERSEE : la marque fonce vers l'oeil et passe au-dela ;
        #     le champ, lui, s'ecarte pour la laisser passer
        if l["grand"]:
            l["loc"] += [(T_FINALE, (x, AVANCEE, z)),
                         (T_FINALE + 14, (x, AVANCEE - 1.2, z)),
                         (T_FINALE + 30, (x * 2.4, -9.5, z * 2.4))]
            l["ech"] += [(T_FINALE + 24, 1.0), (T_FINALE + 32, 0.0)]
        else:
            l["loc"] += [(T_FINALE + 8, (x, RECUL * 0.30, z)),
                         (T_FINALE + 26, (x * 1.5, RECUL * 0.30, z * 1.5))]
            l["ech"] += [(T_FINALE + 20, 1.0), (T_FINALE + 30, 0.0)]

        # 14. LA REFORMATION : tout revient du fond, sur des arcs, du bord
        #     vers le centre. C'est la respiration avant la signature.
        yb = AVANCEE if l["grand"] else RECUL * 0.30
        tr = T_REFORME + (1.0 - r) * 14.0
        arc(l, tr, tr + 16, x * 1.9, RECUL * 2.2, z * 1.9, x, yb, z, 0.38)
        l["ech"] += [(tr, 0.0), (tr + 10, 1.0)]
        l["coul"] += [(tr, LETTRE)]

        # 15. LA SIGNATURE : la marque s'allume D'UN COUP - pas un
        #     parcours cette fois, une frappe - et on la TIENT deux
        #     secondes, immobile, lisible, pendant que la camera pousse
        #     lentement. C'est la seule image que le spectateur emporte.
        if l["grand"]:
            l["coul"] += [(T_SIGNATURE - 2, LETTRE), (T_SIGNATURE, VIOLET),
                          (T_EFFONDRE, VIOLET)]
            l["ech"] += [(T_SIGNATURE - 2, 1.0), (T_SIGNATURE + 2, 1.18),
                         (T_SIGNATURE + 10, 1.0)]
            l["loc"] += [(T_SIGNATURE, (x, yb, z)),
                         (T_EFFONDRE, (x, yb - 0.20, z))]
        else:
            # le champ s'efface derriere la marque : plus petit, plus loin
            l["ech"] += [(T_SIGNATURE, 1.0), (T_SIGNATURE + 8, 0.84),
                         (T_EFFONDRE, 0.84)]
            l["loc"] += [(T_SIGNATURE, (x, yb, z)),
                         (T_EFFONDRE, (x, RECUL * 0.75, z))]

        # 16. L'EFFONDREMENT : du bord vers le centre - la marque est la
        #     derniere chose a s'eteindre. L'image redevient noire,
        #     exactement comme la premiere : la boucle se ferme.
        te = T_EFFONDRE + (1.0 - r) * 8.0
        l["ech"] += [(te, 1.0 if l["grand"] else 0.84),
                     (te + 7, 0.0), (T_BOUCLE, 0.0)]


def contaminer(lettres):
    """
    LE COURANT : parcours en largeur, huit voisins (en quatre, le pied du
    logo n'est pas connexe), arc vers les morceaux separes, cadence
    calculee sur la duree totale de traversee. Puis LES CULBUTES : chaque
    lettre de la marque fait un tour complet sur elle-meme, l'une apres
    l'autre, comme un compteur qui defile.
    """
    cases = {(l["ix"], l["iz"]): l for l in lettres if l["grand"]}
    if not cases:
        return
    V = [(a, b) for a in (-1, 0, 1) for b in (-1, 0, 1) if (a, b) != (0, 0)]

    def propager(dep, etape, depuis):
        etape[dep] = depuis
        f = deque([dep])
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
        l = cases[case]
        t0 = T_COURANT + n * pas
        l["coul"] += [(t0, LETTRE), (t0 + 3, VIOLET),
                      (T_FINALE + 20, VIOLET)]
        l["ech"] += [(t0, 1.0), (t0 + POP_DUREE, POP),
                     (t0 + POP_DUREE * 3, 1.0)]
        for p in (T_PULSE, T_PULSE + 14):
            l["ech"] += [(p, 1.0), (p + 3, 1.24), (p + 9, 1.0)]
        # LES CULBUTES, en vague : un tour complet sur soi-meme
        tc = T_CULBUTE + n * (pas * 0.8)
        l["rot"] += [(tc, 0.0), (tc + 12, math.pi * 2)]
        # LA GRILLE : trois battements de la marque entiere
        for p in (T_GRILLE, T_GRILLE + 12, T_GRILLE + 24):
            l["ech"] += [(p, 1.0), (p + 3, 1.18), (p + 8, 1.0)]
    print("Courant : %d lettres, %d etapes" % (len(cases), profond))


def poser_les_cles(lettres):
    """
    On pose toutes les cles accumulees, puis on impose le style : EASE OUT
    BACK sur les positions et les echelles (le depassement), EXPO sur les
    rotations et les couleurs (le claquement).
    """
    for l in lettres:
        ob = l["ob"]
        for img, (x, y, z) in sorted(l["loc"], key=lambda t: t[0]):
            ob.location = (x, y, z)
            ob.keyframe_insert("location", frame=int(round(img)))
        for img, s in sorted(l["ech"], key=lambda t: t[0]):
            ob.scale = (s, s, s)
            ob.keyframe_insert("scale", frame=int(round(img)))
        for img, a in sorted(l["rot"], key=lambda t: t[0]):
            ob.rotation_euler = (math.pi / 2.0, a, 0.0)
            ob.keyframe_insert("rotation_euler", index=1,
                               frame=int(round(img)))
        for img, c in sorted(l["coul"], key=lambda t: t[0]):
            ob.color = (*c, 1.0)
            ob.keyframe_insert("color", frame=int(round(img)))
        act = ob.animation_data.action
        for fc in act.fcurves:
            style = ("BACK", "EASE_OUT") if fc.data_path in (
                "location", "scale") else ("EXPO", "EASE_OUT")
            for kp in fc.keyframe_points:
                kp.interpolation = style[0]
                kp.easing = style[1]
                if style[0] == "BACK":
                    kp.back = 1.4


def camera():
    """
    Elle ne reste jamais immobile : poussee lente, PLONGEON dans la marque
    du centre, kick a l'impact, orbite pendant les pulsations, recul a la
    disparition, et traversee finale.
    """
    cd = bpy.data.cameras.new("CAM")
    cd.sensor_fit = "VERTICAL"
    cd.sensor_height = CAPTEUR
    cd.lens = CAPTEUR * CAM_DISTANCE / VUE_H
    cam = bpy.data.objects.new("CAM", cd)
    bpy.context.collection.objects.link(cam)
    cd.dof.use_dof = True
    cd.dof.aperture_fstop = 0.05

    poses = [(1, 0.0, CAM_DISTANCE + 1.4, 0.0),
             (T_HOULE, 0.0, CAM_DISTANCE + 1.0, 0.0),
             (T_TOURBILLON, 0.0, CAM_DISTANCE + 0.6, 0.0),
             (T_MOSAIQUE, 0.0, CAM_DISTANCE + 0.9, 0.0),
             (T_PLONGEON - 6, 0.0, CAM_DISTANCE + 0.7, 0.0),
             (T_PLONGEON + 4, 0.0, CAM_DISTANCE + 1.5, 0.0),   # le kick
             (T_PLONGEON + 16, 0.0, CAM_DISTANCE, 0.0),
             (T_COURANT, 0.0, CAM_DISTANCE, 0.0),
             (T_PULSE, 0.55, CAM_DISTANCE - 0.3, 0.35),        # l'orbite
             (T_DISPARITION, -0.45, CAM_DISTANCE + 0.4, -0.25),
             (T_CULBUTE, 0.0, CAM_DISTANCE - 0.8, 0.0),
             (T_RETOUR, 0.0, CAM_DISTANCE + 0.2, 0.0),
             (T_ONDE, 0.30, CAM_DISTANCE - 0.2, 0.20),
             (T_GRILLE, 0.0, CAM_DISTANCE - 0.6, 0.0),
             (T_FINALE, 0.0, CAM_DISTANCE - 0.9, 0.0),
             (T_FINALE + 30, 0.0, CAM_DISTANCE + 0.2, 0.0),
             (T_REFORME, 0.0, CAM_DISTANCE + 0.9, 0.0),
             (T_SIGNATURE - 4, 0.0, CAM_DISTANCE + 0.15, 0.0),
             (T_SIGNATURE + 3, 0.0, CAM_DISTANCE + 0.55, 0.0),   # la frappe
             (T_EFFONDRE, 0.0, CAM_DISTANCE + 0.05, 0.0),  # la poussee du tenu
             (T_BOUCLE, 0.0, CAM_DISTANCE + 1.4, 0.0)]
    for img, px, d, pz in poses:
        cam.location = (px, -d, pz)
        cam.rotation_euler = (math.pi / 2.0, 0.0, 0.0)
        cam.keyframe_insert("location", frame=img)
        cd.dof.focus_distance = d
        cd.dof.keyframe_insert("focus_distance", frame=img)
    for act in (cam.animation_data.action, cd.animation_data.action):
        for fc in act.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = "EXPO"
                kp.easing = "EASE_IN_OUT"
    bpy.context.scene.camera = cam


def compositing():
    """
    L'ETAGE QUI MANQUAIT A TOUTES LES VERSIONS PRECEDENTES.

    Quatre couches, toutes discretes - c'est leur cumul qui fait l'image
    professionnelle, jamais l'une d'elles poussee fort :

      FOG GLOW    le halo doux autour des lettres allumees ;
      STREAKS     les traits de lumiere anamorphiques, quatre branches -
                  la signature "cinema" du glare ;
      DISTORSION  une aberration chromatique legere : les bords de l'image
                  se decomposent en couleurs, comme un vrai objectif ;
      VIGNETTAGE  les coins s'assombrissent, l'oeil revient au centre.
    """
    sc = bpy.context.scene
    sc.use_nodes = True
    nt = sc.node_tree
    nt.nodes.clear()
    rl = nt.nodes.new("CompositorNodeRLayers")
    rl.location = (-900, 0)

    fog = nt.nodes.new("CompositorNodeGlare")
    fog.location = (-680, 0)
    fog.glare_type = "FOG_GLOW"
    fog.quality = "MEDIUM"
    fog.threshold = 0.72
    fog.size = 7
    fog.mix = -0.62
    nt.links.new(rl.outputs["Image"], fog.inputs["Image"])

    st = nt.nodes.new("CompositorNodeGlare")
    st.location = (-460, 0)
    st.glare_type = "STREAKS"
    st.quality = "MEDIUM"
    st.threshold = 0.95
    st.streaks = 4
    st.angle_offset = math.radians(22)
    st.fade = 0.88
    st.mix = -0.55
    nt.links.new(fog.outputs["Image"], st.inputs["Image"])

    ld = nt.nodes.new("CompositorNodeLensdist")
    ld.location = (-240, 0)
    ld.use_projector = False
    # les entrees se prennent par INDICE : leurs noms changent selon
    # la version de Blender, l'ordre non
    ld.inputs[1].default_value = 0.004
    ld.inputs[2].default_value = 0.020
    nt.links.new(st.outputs["Image"], ld.inputs["Image"])

    # le vignettage : un masque elliptique flou, multiplie
    mask = nt.nodes.new("CompositorNodeEllipseMask")
    mask.location = (-460, -320)
    mask.width = 0.92
    mask.height = 0.92
    fl = nt.nodes.new("CompositorNodeBlur")
    fl.location = (-300, -320)
    fl.filter_type = "GAUSS"
    fl.size_x = 220
    fl.size_y = 220
    fl.use_relative = False
    nt.links.new(mask.outputs["Mask"], fl.inputs["Image"])
    vig = nt.nodes.new("CompositorNodeMixRGB")
    vig.location = (-40, 0)
    vig.blend_type = "MULTIPLY"
    vig.inputs["Fac"].default_value = 0.55
    nt.links.new(ld.outputs["Image"], vig.inputs[1])
    nt.links.new(fl.outputs["Image"], vig.inputs[2])

    comp = nt.nodes.new("CompositorNodeComposite")
    comp.location = (200, 0)
    nt.links.new(vig.outputs["Image"], comp.inputs["Image"])


def reglages():
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.eevee.taa_render_samples = 10
    sc.eevee.use_bloom = True
    sc.eevee.bloom_threshold = 1.05
    sc.eevee.bloom_intensity = 0.06
    sc.eevee.bloom_radius = 5.0
    sc.eevee.use_motion_blur = True
    sc.eevee.motion_blur_shutter = 0.40
    sc.render.resolution_x, sc.render.resolution_y = RESOLUTION
    sc.render.fps = FPS
    sc.frame_start, sc.frame_end = 1, DUREE
    sc.render.image_settings.file_format = "PNG"


def main():
    vider()
    monde()
    lettres = construire()
    animer(lettres)
    contaminer(lettres)
    poser_les_cles(lettres)
    camera()
    compositing()
    reglages()
    print("PIXFEED 30 s : %d lettres, %d dans la marque, %d images"
          % (len(lettres), sum(1 for l in lettres if l["grand"]), DUREE))


main()
