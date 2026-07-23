# Rendu Cycles de la maquette v5_5 exportee en glTF depuis three.js.
# Usage : blender -b -P render_scene.py -- <glb> <vue> <sortie.png> [largeur] [samples]
# Vues : dessus | salle | boulangerie | plan_travail | ensemble
# Reperes : three.js (x,y,z) Y-haut  ->  Blender (x,-z,y) Z-haut.
import bpy, math, sys, os
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from materials import MATERIALS

argv = sys.argv[sys.argv.index("--") + 1:]
GLB, VIEW, OUT = argv[0], argv[1], argv[2]
WIDTH = int(argv[3]) if len(argv) > 3 else 1920
SAMPLES = int(argv[4]) if len(argv) > 4 else 64
HEIGHT = WIDTH * 10 // 16  # viewport maquette 16:10
if len(sys.argv) and ("corner" in sys.argv or "corner2" in sys.argv):
    HEIGHT = WIDTH * 5 // 4    # cadrage portrait comme la photo de reference

def t2b(v):
    return Vector((v[0], -v[2], v[1]))

# positions/cibles copiees des boutons de la maquette (goTo)
CAMS = {
    "dessus":       ([1.0, 14.8, -3.2], [1.0, 0, -3.4]),
    "salle":        ([-1.1, 1.66, -1.3], [4.29, 1.28, -5.15]),
    "boulangerie":  ([8.6, 1.68, -1.5], [5.15, 1.3, -4.0]),
    "plan_travail": ([2.8, 1.55, -1.5], [4.14, 1.0, -4.10]),
    "ensemble":     ([9.2, 6.6, 3.0], [0.9, 1.1, -3.2]),
    "corner":       ([3.0, 1.5, -1.9], [4.45, 1.0, -4.9]),
    "corner2":      ([1.55, 1.55, -1.05], [4.25, 1.0, -5.05]),
}
SPOTS = [[1.4, -2.0], [3.6, -4.7], [-8.6, -4.0], [-4.6, -1.4], [7.2, -4.4], [10.4, -2.4], [8.2, -6.9]]
H = 2.70

bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete()

SC = bpy.context.scene
SC.render.engine = 'CYCLES'; SC.cycles.device = 'CPU'
SC.cycles.samples = SAMPLES
SC.cycles.use_denoising = False
SC.render.resolution_x = WIDTH; SC.render.resolution_y = HEIGHT
SC.view_settings.view_transform = 'Filmic'
SC.view_settings.look = 'Medium Contrast'

bpy.ops.import_scene.gltf(filepath=GLB)
print("IMPORTED objects:", len(bpy.data.objects))

# ---- nettoyage : reperes au sol, cotes, doublon de reflet, lampes three.js ----
def delete_tree(o):
    for c in list(o.children):
        delete_tree(c)
    bpy.data.objects.remove(o, do_unlink=True)

roots = [o for o in bpy.data.objects if o.parent is None]
empties = [o for o in roots if o.type == 'EMPTY']

def subtree_meshes(o, acc):
    for c in o.children:
        if c.type == 'MESH':
            acc.append(c)
        subtree_meshes(c, acc)
    return acc

def bbox_dims(o):
    bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
    xs = [p.x for p in bb]; ys = [p.y for p in bb]; zs = [p.z for p in bb]
    return max(xs)-min(xs), max(ys)-min(ys), max(zs)-min(zs), min(zs)

# ordre d'export stable : ambiance, gShell, gMob, gObjets, gAvant, gApres,
# gRepA, gRepV, gCotes... -> on garde gShell/gMob/gObjets/gApres (indices 1,2,3,5)
def node_num(o):
    try: return int(o.name.split("_")[1].split(".")[0])
    except Exception: return 10**9
emps = sorted(empties, key=node_num)
for i, e in enumerate(emps):
    if i not in (1, 2, 3, 5):
        print("DELETE GROUP idx", i, e.name)
        delete_tree(e)

# dalles du plan au-dessus de 2,4 m (toits des locaux voisins) : supprimees,
# notre propre plafond les remplace
for o in list(bpy.data.objects):
    if o.type == 'MESH':
        dx, dy, dz, z0 = bbox_dims(o)
        if z0 > 2.4 and dz < 0.25:
            print("DELETE SLAB", o.name, round(dx,1), round(dy,1))
            bpy.data.objects.remove(o, do_unlink=True)
for o in list(bpy.data.objects):
    if o.type == 'LIGHT':
        bpy.data.objects.remove(o, do_unlink=True)
    elif o.type == 'MESH' and o.parent is None and len(o.data.materials) == 0:
        print("DELETE", o.name)
        bpy.data.objects.remove(o, do_unlink=True)

# plafond simple (la maquette n'en exporte pas) + disques de spots
ceil_mat = bpy.data.materials.new("plafond"); ceil_mat.use_nodes = True
ceil_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.92, 0.92, 0.90, 1)
ceil_mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.9
bpy.ops.mesh.primitive_plane_add(size=1, location=(0.9, 5.03, 2.70))
ceil = bpy.context.object; ceil.scale = (23.2 / 2 + 1, 9.3 / 2 + 1, 1)
ceil.data.materials.append(ceil_mat)
# normale vers le bas (vue depuis l'interieur) + face arriere invisible d'en haut
ceil.rotation_euler = (math.pi, 0, 0)

# three.js n'affiche que la face avant des murs (effet maison de poupee) :
# on reproduit en rendant les faces arriere transparentes
for mat in bpy.data.materials:
    if not mat.name.startswith("Material_") or not mat.use_nodes:
        continue
    nt = mat.node_tree
    outn = next((n for n in nt.nodes if n.bl_idname == "ShaderNodeOutputMaterial" and n.is_active_output), None)
    if outn is None or not outn.inputs["Surface"].links:
        continue
    src = outn.inputs["Surface"].links[0].from_socket
    nt.links.remove(outn.inputs["Surface"].links[0])
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    trans = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(geo.outputs["Backfacing"], mix.inputs["Fac"])
    nt.links.new(src, mix.inputs[1])
    nt.links.new(trans.outputs["BSDF"], mix.inputs[2])
    nt.links.new(mix.outputs["Shader"], outn.inputs["Surface"])
mat_ceil_backface = None

# ---- surcouche de materiaux proceduraux sur les surfaces cles ----
def make_pbr(name, builder, mapping_rot=0.0):
    mat = bpy.data.materials.new("pbr_" + name); mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    sockets = builder(nt)
    # les builders utilisent la sortie UV : bascule sur coordonnees Objet (echelle metres)
    for n in nt.nodes:
        if n.bl_idname == "ShaderNodeTexCoord":
            for l in list(n.outputs["UV"].links):
                to = l.to_socket; nt.links.remove(l)
                nt.links.new(n.outputs["Object"], to)
    if mapping_rot:
        for n in nt.nodes:
            if n.bl_idname == "ShaderNodeMapping":
                n.inputs["Rotation"].default_value[2] = mapping_rot
    # remise a l'echelle 1:1 (les builders divisent par span pour le bake)
    for n in nt.nodes:
        if n.bl_idname == "ShaderNodeMapping" and n.inputs["Scale"].default_value[0] == sockets["span"]:
            n.inputs["Scale"].default_value = (1, 1, 1)
    nt.links.new(sockets["color"], bsdf.inputs["Base Color"])
    if sockets.get("rough") is not None:
        nt.links.new(sockets["rough"], bsdf.inputs["Roughness"])
    else:
        bsdf.inputs["Roughness"].default_value = sockets.get("rough_value", 0.6)
    bsdf.inputs["Metallic"].default_value = sockets["metal"]
    if sockets.get("height") is not None:
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = sockets["bump"]
        nt.links.new(sockets["height"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat

m_sol = make_pbr("sol", MATERIALS["carrelage_sol_beige"], mapping_rot=math.radians(45))

m_panneau = bpy.data.materials.new("pbr_panneau_anthracite"); m_panneau.use_nodes = True
_nt = m_panneau.node_tree; _b = _nt.nodes["Principled BSDF"]
_co = _nt.nodes.new("ShaderNodeTexCoord")
_mp = _nt.nodes.new("ShaderNodeMapping")
_nt.links.new(_co.outputs["Object"], _mp.inputs["Vector"])
_br = _nt.nodes.new("ShaderNodeTexBrick")
_br.offset = 0.0
_br.inputs["Scale"].default_value = 1.0
_br.inputs["Brick Width"].default_value = 0.85
_br.inputs["Row Height"].default_value = 0.90
_br.inputs["Mortar Size"].default_value = 0.004
_br.inputs["Color1"].default_value = (0.055, 0.06, 0.065, 1)
_br.inputs["Color2"].default_value = (0.05, 0.055, 0.06, 1)
_br.inputs["Mortar"].default_value = (0.02, 0.02, 0.022, 1)
_nt.links.new(_mp.outputs["Vector"], _br.inputs["Vector"])
_nt.links.new(_br.outputs["Color"], _b.inputs["Base Color"])
_b.inputs["Roughness"].default_value = 0.55
_bmp = _nt.nodes.new("ShaderNodeBump"); _bmp.inputs["Strength"].default_value = 0.15; _bmp.invert = True
_nt.links.new(_br.outputs["Fac"], _bmp.inputs["Height"])
_nt.links.new(_bmp.outputs["Normal"], _b.inputs["Normal"])
# tout mesh dans l'emprise de la gaine (G=4.29/-5.15, 1.50 m) -> anthracite
for _o in bpy.data.objects:
    if _o.type != 'MESH':
        continue
    _bb = [_o.matrix_world @ Vector(_c) for _c in _o.bound_box]
    _cx = sum(_p.x for _p in _bb) / 8; _cy = sum(_p.y for _p in _bb) / 8
    _dz = max(_p.z for _p in _bb) - min(_p.z for _p in _bb)
    if 3.4 <= _cx <= 5.2 and 4.3 <= _cy <= 6.0 and _dz > 1.5:
        if len(_o.data.materials) == 0:
            _o.data.materials.append(m_panneau)
        else:
            for _i in range(len(_o.data.materials)):
                _o.data.materials[_i] = m_panneau
        print("PANNEAU ->", _o.name)

# murs rouges -> bordeaux profond (reduction valeur/saturation des textures rougeatres)
import numpy as _np
for _m in bpy.data.materials:
    if not _m.name.startswith("Material_") or not _m.use_nodes:
        continue
    for _n in _m.node_tree.nodes:
        if _n.bl_idname == "ShaderNodeTexImage" and _n.image and _n.image.size[0] > 0:
            _img = _n.image
            _px = _np.array(_img.pixels[:]).reshape(-1, 4)
            _mean = _px[:, :3].mean(axis=0)
            if _mean[0] > 0.25 and _mean[0] > 1.8 * _mean[1]:
                _hs = _m.node_tree.nodes.new("ShaderNodeHueSaturation")
                _hs.inputs["Value"].default_value = 0.55
                _hs.inputs["Saturation"].default_value = 0.9
                for _l in list(_n.outputs["Color"].links):
                    _to = _l.to_socket
                    _m.node_tree.links.remove(_l)
                    _m.node_tree.links.new(_hs.outputs["Color"], _to)
                _m.node_tree.links.new(_n.outputs["Color"], _hs.inputs["Color"])
                print("BORDEAUX ->", _m.name)
m_granit = make_pbr("granit", MATERIALS["granit_pilier"])

ceiling_objs = []
for o in bpy.data.objects:
    if o.type != 'MESH':
        continue
    bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
    xs = [p.x for p in bb]; ys = [p.y for p in bb]; zs = [p.z for p in bb]
    dx, dy, dz = max(xs)-min(xs), max(ys)-min(ys), max(zs)-min(zs)
    # sol : tres grand plan horizontal au niveau 0
    if dz < 0.05 and dx > 15 and dy > 5 and abs(min(zs)) < 0.1:
        print("FLOOR OVERRIDE ->", o.name)
        o.data.materials.clear(); o.data.materials.append(m_sol)
    # plafond : grandes surfaces au-dessus de 2,5 m
    if min(zs) > 2.5 and dx > 3 and dy > 3:
        ceiling_objs.append(o)
    # la dalle ajoutee est aussi dans la liste via son niveau 2.70
    # pilier granit : cylindre haut et etroit
    if dz > 1.8 and 0.4 < dx < 0.9 and 0.4 < dy < 0.9 and len(o.data.vertices) > 60:
        print("GRANIT OVERRIDE ->", o.name)
        o.data.materials.clear(); o.data.materials.append(m_granit)

# vues aeriennes : plafond masque (reference directe, la bbox de l'objet
# fraichement cree n'est pas encore a jour dans la boucle ci-dessus)
if VIEW in ("dessus", "ensemble"):
    ceil.hide_render = True
    for o in ceiling_objs:
        o.hide_render = True

# ---- eclairage ----
for x, z in SPOTS:
    bpy.ops.object.light_add(type='AREA', location=(x, -z, H - 0.05))
    L = bpy.context.object
    L.data.energy = 70; L.data.size = 0.35
    L.data.color = (1.0, 0.85, 0.66)

# nappe douce generale (plafond lumineux)
bpy.ops.object.light_add(type='AREA', location=(1.0, 4.0, H - 0.02))
L = bpy.context.object
L.data.energy = 300; L.data.size = 16
L.data.color = (1.0, 0.96, 0.90)

# lumiere du jour depuis la facade (z three = -0.65 -> y blender = 0.65)
bpy.ops.object.light_add(type='AREA', location=(2.0, 0.75, 1.8))
L = bpy.context.object
L.data.energy = 130; L.data.size = 6
L.data.color = (0.88, 0.92, 1.0)
L.rotation_euler = (math.radians(-75), 0, 0)

world = bpy.data.worlds.new("w"); world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.85, 0.80, 0.72, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.25
SC.world = world

# ---- camera ----
pos, tgt = CAMS[VIEW]
bpy.ops.object.camera_add(location=t2b(pos))
cam = bpy.context.object
cam.data.sensor_fit = 'VERTICAL'
cam.data.angle_y = math.radians(42)
cam.data.clip_start = 0.06
d = t2b(tgt) - cam.location
cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
SC.camera = cam

SC.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print("RENDER OK", VIEW, "->", OUT)
