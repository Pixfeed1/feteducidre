# Sol photorealiste v2 — carrelage ceramique beige 30 cm.
# Corrections v2 :
#   1. lippage : micro-inclinaison aleatoire PAR carreau (les reflets "sautent")
#   2. motif d'email discontinu a chaque joint (offset de bruit par carreau)
#   3. couche de vernis ceramique (Coat du Principled)
#   4. vrai deplacement geometrique des joints (Displacement + subdivision adaptative)
#   5. teintes calees sur la photo de reference du client
#   6. usure directionnelle + couloir de passage poli, joints a largeur irreguliere
# Usage : blender -b -P sol_photoreal_v2.py -- <sortie.png> [samples]
import bpy, math, sys
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]
SAMPLES = int(argv[1]) if len(argv) > 1 else 112

TILE = 0.30        # carreau 30 cm
GROUT = 0.006      # demi-largeur moyenne du joint (m)
GROUT_JIT = 0.0018 # variation de largeur du joint (m)
BEVEL = 0.011      # largeur du chanfrein (m)
GROUT_DEPTH = 0.0028   # profondeur reelle du joint (m)
LIPPAGE = 0.0007       # desaffleur max entre carreaux (m)

bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete()
SC = bpy.context.scene
SC.render.engine = 'CYCLES'; SC.cycles.device = 'CPU'
SC.cycles.feature_set = 'EXPERIMENTAL'      # subdivision adaptative pour le displacement
SC.cycles.dicing_rate = 4.0
SC.cycles.samples = SAMPLES; SC.cycles.use_denoising = False
SC.render.resolution_x = 1152; SC.render.resolution_y = 720
SC.view_settings.view_transform = 'Filmic'
SC.view_settings.look = 'Medium Contrast'
SC.view_settings.exposure = -0.65

# ============================ SHADER SOL ============================
mat = bpy.data.materials.new("sol_v2"); mat.use_nodes = True
try:
    mat.displacement_method = 'BOTH'
except AttributeError:
    mat.cycles.displacement_method = 'BOTH'
nt = mat.node_tree
bsdf = nt.nodes["Principled BSDF"]
out = nt.nodes["Material Output"]

coord = nt.nodes.new("ShaderNodeTexCoord")
P = coord.outputs["Object"]

def math_node(op, a=None, b=None, va=None, vb=None):
    n = nt.nodes.new("ShaderNodeMath"); n.operation = op
    if a is not None: nt.links.new(a, n.inputs[0])
    if va is not None: n.inputs[0].default_value = va
    if b is not None: nt.links.new(b, n.inputs[1])
    if vb is not None: n.inputs[1].default_value = vb
    return n.outputs["Value"]

def maprange(v, fmin, fmax, tmin, tmax, smooth=False):
    n = nt.nodes.new("ShaderNodeMapRange")
    if smooth: n.interpolation_type = 'SMOOTHSTEP'
    n.inputs["From Min"].default_value = fmin
    n.inputs["From Max"].default_value = fmax
    n.inputs["To Min"].default_value = tmin
    n.inputs["To Max"].default_value = tmax
    nt.links.new(v, n.inputs["Value"])
    return n.outputs["Result"]

# ---- grille : fraction locale + distance au bord ----
scl = nt.nodes.new("ShaderNodeVectorMath"); scl.operation = 'SCALE'
scl.inputs[3].default_value = 1.0 / TILE
nt.links.new(P, scl.inputs[0])
frac = nt.nodes.new("ShaderNodeVectorMath"); frac.operation = 'FRACTION'
nt.links.new(scl.outputs["Vector"], frac.inputs[0])
sepf = nt.nodes.new("ShaderNodeSeparateXYZ")
nt.links.new(frac.outputs["Vector"], sepf.inputs[0])
fx, fy = sepf.outputs["X"], sepf.outputs["Y"]

def edge_dist(f):
    return math_node('MINIMUM', f, math_node('SUBTRACT', b=f, va=1.0))

dmin = math_node('MINIMUM', edge_dist(fx), edge_dist(fy))

# ---- aleatoire par carreau ----
snap = nt.nodes.new("ShaderNodeVectorMath"); snap.operation = 'SNAP'
snap.inputs[1].default_value = (TILE, TILE, TILE)
nt.links.new(P, snap.inputs[0])
wn = nt.nodes.new("ShaderNodeTexWhiteNoise")
nt.links.new(snap.outputs["Vector"], wn.inputs["Vector"])
sepc = nt.nodes.new("ShaderNodeSeparateColor")
nt.links.new(wn.outputs["Color"], sepc.inputs["Color"])
rnd_tone = wn.outputs["Value"]
rnd_a, rnd_b = sepc.outputs["Red"], sepc.outputs["Green"]

# ---- joints a largeur irreguliere (6) ----
jn = nt.nodes.new("ShaderNodeTexNoise")
jn.inputs["Scale"].default_value = 9.0; jn.inputs["Detail"].default_value = 2
nt.links.new(P, jn.inputs["Vector"])
jitter = maprange(jn.outputs["Fac"], 0, 1, -GROUT_JIT / TILE, GROUT_JIT / TILE)
dj = math_node('ADD', dmin, jitter)

# masque carreau (0 = fond de joint, 1 = plein carreau), chanfrein doux
tilemask = maprange(dj, GROUT / TILE, (GROUT + BEVEL) / TILE, 0, 1, smooth=True)

# ---- motif d'email discontinu par carreau (2) ----
offs = nt.nodes.new("ShaderNodeVectorMath"); offs.operation = 'SCALE'
offs.inputs[3].default_value = 37.0
nt.links.new(wn.outputs["Color"], offs.inputs[0])
pcell = nt.nodes.new("ShaderNodeVectorMath"); pcell.operation = 'ADD'
nt.links.new(P, pcell.inputs[0])
nt.links.new(offs.outputs["Vector"], pcell.inputs[1])
PC = pcell.outputs["Vector"]

# teintes calees sur la photo client (5) : beige clair chaud, joint taupe
tone = nt.nodes.new("ShaderNodeValToRGB")
tone.color_ramp.elements[0].color = (0.430, 0.385, 0.310, 1)
tone.color_ramp.elements[1].color = (0.550, 0.505, 0.425, 1)
nt.links.new(rnd_tone, tone.inputs["Fac"])

cloud = nt.nodes.new("ShaderNodeTexNoise")
cloud.inputs["Scale"].default_value = 5.5; cloud.inputs["Detail"].default_value = 4
nt.links.new(PC, cloud.inputs["Vector"])
cloudramp = nt.nodes.new("ShaderNodeValToRGB")
cloudramp.color_ramp.elements[0].color = (0.92, 0.92, 0.91, 1)
cloudramp.color_ramp.elements[1].color = (1.06, 1.05, 1.03, 1)
nt.links.new(cloud.outputs["Fac"], cloudramp.inputs["Fac"])
mul1 = nt.nodes.new("ShaderNodeMixRGB"); mul1.blend_type = 'MULTIPLY'; mul1.inputs["Fac"].default_value = 1.0
nt.links.new(tone.outputs["Color"], mul1.inputs["Color1"])
nt.links.new(cloudramp.outputs["Color"], mul1.inputs["Color2"])

spk = nt.nodes.new("ShaderNodeTexNoise")
spk.inputs["Scale"].default_value = 1500; spk.inputs["Detail"].default_value = 2
nt.links.new(PC, spk.inputs["Vector"])
spkramp = nt.nodes.new("ShaderNodeValToRGB")
spkramp.color_ramp.elements[0].position = 0.44
spkramp.color_ramp.elements[0].color = (0.86, 0.84, 0.81, 1)
spkramp.color_ramp.elements[1].position = 0.52
spkramp.color_ramp.elements[1].color = (1, 1, 1, 1)
nt.links.new(spk.outputs["Fac"], spkramp.inputs["Fac"])
mul2 = nt.nodes.new("ShaderNodeMixRGB"); mul2.blend_type = 'MULTIPLY'; mul2.inputs["Fac"].default_value = 0.55
nt.links.new(mul1.outputs["Color"], mul2.inputs["Color1"])
nt.links.new(spkramp.outputs["Color"], mul2.inputs["Color2"])

# encrassement leger vers les joints
dirt = maprange(dj, GROUT / TILE, 0.10, 0.87, 1.0, smooth=True)
mul3 = nt.nodes.new("ShaderNodeMixRGB"); mul3.blend_type = 'MULTIPLY'; mul3.inputs["Fac"].default_value = 1.0
nt.links.new(mul2.outputs["Color"], mul3.inputs["Color1"])
nt.links.new(dirt, mul3.inputs["Color2"])

# joint : ciment taupe avec granulosite
gn = nt.nodes.new("ShaderNodeTexNoise")
gn.inputs["Scale"].default_value = 800; gn.inputs["Detail"].default_value = 2
nt.links.new(P, gn.inputs["Vector"])
groutramp = nt.nodes.new("ShaderNodeValToRGB")
groutramp.color_ramp.elements[0].color = (0.255, 0.228, 0.190, 1)
groutramp.color_ramp.elements[1].color = (0.335, 0.302, 0.252, 1)
nt.links.new(gn.outputs["Fac"], groutramp.inputs["Fac"])

colmix = nt.nodes.new("ShaderNodeMixRGB")
nt.links.new(tilemask, colmix.inputs["Fac"])
nt.links.new(groutramp.outputs["Color"], colmix.inputs["Color1"])
nt.links.new(mul3.outputs["Color"], colmix.inputs["Color2"])
nt.links.new(colmix.outputs["Color"], bsdf.inputs["Base Color"])

# ---- rugosite : usure directionnelle + couloir de passage (6) ----
wmap = nt.nodes.new("ShaderNodeMapping")
wmap.inputs["Scale"].default_value = (1.0, 0.28, 1.0)   # etire le bruit le long de l'axe de marche (Y)
nt.links.new(P, wmap.inputs["Vector"])
wear = nt.nodes.new("ShaderNodeTexNoise")
wear.inputs["Scale"].default_value = 0.9; wear.inputs["Detail"].default_value = 4
nt.links.new(wmap.outputs["Vector"], wear.inputs["Vector"])
wearr = maprange(wear.outputs["Fac"], 0, 1, 0.24, 0.50)

sepp = nt.nodes.new("ShaderNodeSeparateXYZ")
nt.links.new(P, sepp.inputs[0])
lane_d = math_node('ABSOLUTE', math_node('SUBTRACT', sepp.outputs["X"], vb=-0.6))
lane = maprange(lane_d, 0.0, 1.5, 0.07, 0.0, smooth=True)   # couloir poli autour de x=-0.6
rough_tile = math_node('SUBTRACT', wearr, lane)

micro = nt.nodes.new("ShaderNodeTexNoise")
micro.inputs["Scale"].default_value = 34; micro.inputs["Detail"].default_value = 4
nt.links.new(PC, micro.inputs["Vector"])
mvar = maprange(micro.outputs["Fac"], 0, 1, -0.018, 0.018)
rough_tile2 = math_node('ADD', rough_tile, mvar)

roughmix = nt.nodes.new("ShaderNodeMixRGB")
nt.links.new(tilemask, roughmix.inputs["Fac"])
roughmix.inputs["Color1"].default_value = (0.88, 0.88, 0.88, 1)
nt.links.new(rough_tile2, roughmix.inputs["Color2"])
nt.links.new(roughmix.outputs["Color"], bsdf.inputs["Roughness"])

# ---- vernis ceramique (3) : Coat uniquement sur le carreau ----
coatw = math_node('MULTIPLY', tilemask, vb=0.12)
nt.links.new(coatw, bsdf.inputs["Coat Weight"])
bsdf.inputs["Coat Roughness"].default_value = 0.18

# ---- hauteur reelle (4) : joint creuse + chanfrein + lippage + grain ----
h_tile = math_node('MULTIPLY', tilemask, vb=GROUT_DEPTH)
tiltx = maprange(rnd_a, 0, 1, -LIPPAGE, LIPPAGE)
tilty = maprange(rnd_b, 0, 1, -LIPPAGE, LIPPAGE)
h_lip = math_node('ADD', math_node('MULTIPLY', tiltx, fx), math_node('MULTIPLY', tilty, fy))
h_lip_masked = math_node('MULTIPLY', h_lip, tilemask)   # le joint, lui, reste au fond
h_grain = math_node('MULTIPLY', maprange(micro.outputs["Fac"], 0, 1, -1, 1), vb=0.000015)
height = math_node('ADD', math_node('ADD', h_tile, h_lip_masked), h_grain)

disp = nt.nodes.new("ShaderNodeDisplacement")
disp.inputs["Midlevel"].default_value = GROUT_DEPTH
disp.inputs["Scale"].default_value = 1.0
nt.links.new(height, disp.inputs["Height"])
nt.links.new(disp.outputs["Displacement"], out.inputs["Displacement"])

# ============================ SCENE DE TEST v3 ============================
bpy.ops.mesh.primitive_plane_add(size=16, location=(0, 0, 0))
floor = bpy.context.object; floor.data.materials.append(mat)
sub = floor.modifiers.new("adaptive", 'SUBSURF')
sub.subdivision_type = 'SIMPLE'
floor.cycles.use_adaptive_subdivision = True

def simple_mat(name, rgba, rough, metal=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rgba
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m

wallm = simple_mat("anthracite", (0.055, 0.06, 0.065, 1), 0.55)
bpy.ops.mesh.primitive_cube_add(location=(0.5, 3.2, 1.35))
wall = bpy.context.object; wall.scale = (5.5, 0.05, 1.35); wall.data.materials.append(wallm)

plm = simple_mat("plinthe", (0.12, 0.09, 0.07, 1), 0.4)
bpy.ops.mesh.primitive_cube_add(location=(0.5, 3.14, 0.045))
pl = bpy.context.object; pl.scale = (5.5, 0.012, 0.045); pl.data.materials.append(plm)

# mur bordeaux a gauche (comme la salle du client)
bordm = simple_mat("bordeaux", (0.245, 0.055, 0.085, 1), 0.75)
bpy.ops.mesh.primitive_cube_add(location=(-5.0, 1.0, 1.35))
bw = bpy.context.object; bw.scale = (0.05, 6.0, 1.35); bw.data.materials.append(bordm)

# comptoir bois pin au fond droit (reflets chauds sur le sol)
woodm = bpy.data.materials.new("pin"); woodm.use_nodes = True
wb = woodm.node_tree.nodes["Principled BSDF"]
wnz = woodm.node_tree.nodes.new("ShaderNodeTexNoise")
wnz.inputs["Scale"].default_value = 3.0; wnz.inputs["Detail"].default_value = 5
wmapn = woodm.node_tree.nodes.new("ShaderNodeMapping")
wmapn.inputs["Scale"].default_value = (1.0, 14.0, 1.0)
wco = woodm.node_tree.nodes.new("ShaderNodeTexCoord")
woodm.node_tree.links.new(wco.outputs["Object"], wmapn.inputs["Vector"])
woodm.node_tree.links.new(wmapn.outputs["Vector"], wnz.inputs["Vector"])
wramp = woodm.node_tree.nodes.new("ShaderNodeValToRGB")
wramp.color_ramp.elements[0].color = (0.36, 0.19, 0.08, 1)
wramp.color_ramp.elements[1].color = (0.60, 0.38, 0.18, 1)
woodm.node_tree.links.new(wnz.outputs["Fac"], wramp.inputs["Fac"])
woodm.node_tree.links.new(wramp.outputs["Color"], wb.inputs["Base Color"])
wb.inputs["Roughness"].default_value = 0.30
wbump = woodm.node_tree.nodes.new("ShaderNodeBump")
wbump.inputs["Strength"].default_value = 0.12
woodm.node_tree.links.new(wnz.outputs["Fac"], wbump.inputs["Height"])
woodm.node_tree.links.new(wbump.outputs["Normal"], wb.inputs["Normal"])
bpy.ops.mesh.primitive_cube_add(location=(2.6, 2.35, 0.46))
ct = bpy.context.object; ct.scale = (1.3, 0.75, 0.46); ct.data.materials.append(woodm)
bpy.ops.mesh.primitive_cube_add(location=(2.6, 2.35, 0.935))
cttop = bpy.context.object; cttop.scale = (1.36, 0.80, 0.022); cttop.data.materials.append(woodm)

whitem = simple_mat("white", (0.85, 0.84, 0.80, 1), 0.8)
bpy.ops.mesh.primitive_cube_add(location=(-4.2, 3.15, 1.35))
w2 = bpy.context.object; w2.scale = (1.5, 0.04, 1.35); w2.data.materials.append(whitem)

bpy.ops.mesh.primitive_plane_add(size=16, location=(-2.5, 0, 2.7))
ceil = bpy.context.object; ceil.rotation_euler = (math.pi, 0, 0)
ceil.scale = (0.5, 1, 1)   # le plafond s'arrete a x=5.5, avant la fenetre
ceil.data.materials.append(whitem)

# ---- lumieres ----
for x in (-2.4, -0.8, 0.8, 2.4):
    bpy.ops.object.light_add(type='AREA', location=(x, 1.8, 2.62))
    L = bpy.context.object
    L.data.energy = 55; L.data.size = 0.22
    L.data.color = (1.0, 0.88, 0.72)

bpy.ops.object.light_add(type='AREA', location=(0, -4.5, 2.2))
L = bpy.context.object; L.data.energy = 90; L.data.size = 5
L.data.color = (0.95, 0.94, 0.90)
L.rotation_euler = (math.radians(-60), 0, 0)

# soleil chaud rasant a travers une croisee de fenetre (gobo)
bpy.ops.object.light_add(type='SUN', location=(0, 0, 5))
sun = bpy.context.object
sun.data.energy = 4.5; sun.data.angle = math.radians(0.6)
sun.data.color = (1.0, 0.83, 0.62)
sdir = Vector((-0.88, 0.16, -0.34)).normalized()
sun.rotation_euler = sdir.to_track_quat('-Z', 'Y').to_euler()

# cadre de fenetre hors champ (x=6) qui decoupe le rayon en carreaux de vitrine
fm = simple_mat("frame", (0.05, 0.05, 0.05, 1), 0.5)
fz0, fz1, fy0, fy1 = 0.7, 2.5, -1.6, 1.6
for (cy, cz, sy, sz) in [
    ((fy0+fy1)/2, fz0-0.6, (fy1-fy0)/2+1.2, 0.6),   # allege sous la fenetre
    ((fy0+fy1)/2, fz1+0.1, (fy1-fy0)/2+1.2, 0.12),  # linteau
    (fy0-0.6, (fz0+fz1)/2, 0.6, (fz1-fz0)/2+0.7),   # tableau gauche
    (fy1+0.6, (fz0+fz1)/2, 0.6, (fz1-fz0)/2+0.7),   # tableau droit
    ((fy0+fy1)/2, (fz0+fz1)/2, 0.035, (fz1-fz0)/2), # meneau vertical
    ((fy0+fy1)/2, (fz0+fz1)/2, (fy1-fy0)/2, 0.035), # traverse horizontale
]:
    bpy.ops.mesh.primitive_cube_add(location=(6.0, cy, cz))
    f = bpy.context.object; f.scale = (0.03, sy, sz); f.data.materials.append(fm)

world = bpy.data.worlds.new("w"); world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.55, 0.52, 0.48, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.12
SC.world = world

bpy.ops.object.camera_add(location=(-1.8, -3.6, 1.05))
cam = bpy.context.object
cam.data.lens = 28; cam.data.sensor_width = 36
cam.data.dof.use_dof = True
cam.data.dof.focus_distance = 2.6
cam.data.dof.aperture_fstop = 9.0
d = Vector((0.8, 2.5, 0.0)) - cam.location
cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
SC.camera = cam

SC.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print("RENDER OK ->", OUT)
