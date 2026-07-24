# Test sol photorealiste : carrelage beige 30 cm, chanfreins, joints creuses,
# rugosite variable (traces de passage), variation par carreau.
# Usage : blender -b -P sol_photoreal.py -- <sortie.png> [samples]
import bpy, math, sys

argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]
SAMPLES = int(argv[1]) if len(argv) > 1 else 96

TILE = 0.30      # carreau 30 cm
GROUT = 0.006    # demi-largeur du joint
BEVEL = 0.010    # largeur du chanfrein adouci

bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete()
SC = bpy.context.scene
SC.render.engine = 'CYCLES'; SC.cycles.device = 'CPU'
SC.cycles.samples = SAMPLES; SC.cycles.use_denoising = False
SC.render.resolution_x = 1152; SC.render.resolution_y = 720
SC.view_settings.view_transform = 'Filmic'
SC.view_settings.look = 'Medium Contrast'
SC.view_settings.exposure = -0.65

# ---------------- shader du sol ----------------
mat = bpy.data.materials.new("sol_photoreal"); mat.use_nodes = True
nt = mat.node_tree
bsdf = nt.nodes["Principled BSDF"]

coord = nt.nodes.new("ShaderNodeTexCoord")

# p = coord / TILE ; f = fract(p) ; d = distance au bord du carreau
scale = nt.nodes.new("ShaderNodeVectorMath"); scale.operation = 'SCALE'
scale.inputs[3].default_value = 1.0 / TILE
nt.links.new(coord.outputs["Object"], scale.inputs[0])
frac = nt.nodes.new("ShaderNodeVectorMath"); frac.operation = 'FRACTION'
nt.links.new(scale.outputs["Vector"], frac.inputs[0])
sep = nt.nodes.new("ShaderNodeSeparateXYZ")
nt.links.new(frac.outputs["Vector"], sep.inputs[0])

def edge_dist(axis_out):
    inv = nt.nodes.new("ShaderNodeMath"); inv.operation = 'SUBTRACT'
    inv.inputs[0].default_value = 1.0
    nt.links.new(axis_out, inv.inputs[1])
    mn = nt.nodes.new("ShaderNodeMath"); mn.operation = 'MINIMUM'
    nt.links.new(axis_out, mn.inputs[0])
    nt.links.new(inv.outputs["Value"], mn.inputs[1])
    return mn.outputs["Value"]

dmin = nt.nodes.new("ShaderNodeMath"); dmin.operation = 'MINIMUM'
nt.links.new(edge_dist(sep.outputs["X"]), dmin.inputs[0])
nt.links.new(edge_dist(sep.outputs["Y"]), dmin.inputs[1])

# masque carreau (0 = joint, 1 = plein carreau) avec chanfrein doux
tilemask = nt.nodes.new("ShaderNodeMapRange")
tilemask.interpolation_type = 'SMOOTHSTEP'
tilemask.inputs["From Min"].default_value = GROUT / TILE
tilemask.inputs["From Max"].default_value = (GROUT + BEVEL) / TILE
nt.links.new(dmin.outputs["Value"], tilemask.inputs["Value"])

# variation de teinte par carreau
snap = nt.nodes.new("ShaderNodeVectorMath"); snap.operation = 'SNAP'
snap.inputs[1].default_value = (TILE, TILE, TILE)
nt.links.new(coord.outputs["Object"], snap.inputs[0])
wn = nt.nodes.new("ShaderNodeTexWhiteNoise")
nt.links.new(snap.outputs["Vector"], wn.inputs["Vector"])
tone = nt.nodes.new("ShaderNodeValToRGB")
tone.color_ramp.elements[0].color = (0.415, 0.375, 0.305, 1)
tone.color_ramp.elements[1].color = (0.545, 0.505, 0.43, 1)
nt.links.new(wn.outputs["Value"], tone.inputs["Fac"])

# nuage doux dans le carreau (emaux) + moucheture fine
cloud = nt.nodes.new("ShaderNodeTexNoise")
cloud.inputs["Scale"].default_value = 5.0; cloud.inputs["Detail"].default_value = 3
nt.links.new(coord.outputs["Object"], cloud.inputs["Vector"])
cloudramp = nt.nodes.new("ShaderNodeValToRGB")
cloudramp.color_ramp.elements[0].color = (0.93, 0.93, 0.92, 1)
cloudramp.color_ramp.elements[1].color = (1.05, 1.04, 1.02, 1)
nt.links.new(cloud.outputs["Fac"], cloudramp.inputs["Fac"])
mul1 = nt.nodes.new("ShaderNodeMixRGB"); mul1.blend_type = 'MULTIPLY'; mul1.inputs["Fac"].default_value = 1.0
nt.links.new(tone.outputs["Color"], mul1.inputs["Color1"])
nt.links.new(cloudramp.outputs["Color"], mul1.inputs["Color2"])
spec = nt.nodes.new("ShaderNodeTexNoise")
spec.inputs["Scale"].default_value = 1400; spec.inputs["Detail"].default_value = 2
nt.links.new(coord.outputs["Object"], spec.inputs["Vector"])
specramp = nt.nodes.new("ShaderNodeValToRGB")
specramp.color_ramp.elements[0].position = 0.42
specramp.color_ramp.elements[0].color = (0.85, 0.83, 0.80, 1)
specramp.color_ramp.elements[1].position = 0.5
specramp.color_ramp.elements[1].color = (1, 1, 1, 1)
nt.links.new(spec.outputs["Fac"], specramp.inputs["Fac"])
mul2 = nt.nodes.new("ShaderNodeMixRGB"); mul2.blend_type = 'MULTIPLY'; mul2.inputs["Fac"].default_value = 0.6
nt.links.new(mul1.outputs["Color"], mul2.inputs["Color1"])
nt.links.new(specramp.outputs["Color"], mul2.inputs["Color2"])

# legere salissure des joints pres des bords (AO fake)
dirt = nt.nodes.new("ShaderNodeMapRange")
dirt.interpolation_type = 'SMOOTHSTEP'
dirt.inputs["From Min"].default_value = GROUT / TILE
dirt.inputs["From Max"].default_value = 0.10
dirt.inputs["To Min"].default_value = 0.86
dirt.inputs["To Max"].default_value = 1.0
nt.links.new(dmin.outputs["Value"], dirt.inputs["Value"])
mul3 = nt.nodes.new("ShaderNodeMixRGB"); mul3.blend_type = 'MULTIPLY'; mul3.inputs["Fac"].default_value = 1.0
nt.links.new(mul2.outputs["Color"], mul3.inputs["Color1"])
nt.links.new(dirt.outputs["Result"], mul3.inputs["Color2"])

# couleur joint sable
groutcol = nt.nodes.new("ShaderNodeRGB")
groutcol.outputs[0].default_value = (0.30, 0.27, 0.225, 1)
colmix = nt.nodes.new("ShaderNodeMixRGB")
nt.links.new(tilemask.outputs["Result"], colmix.inputs["Fac"])
nt.links.new(groutcol.outputs[0], colmix.inputs["Color1"])
nt.links.new(mul3.outputs["Color"], colmix.inputs["Color2"])
nt.links.new(colmix.outputs["Color"], bsdf.inputs["Base Color"])

# rugosite : plaques de traces de passage (grand bruit) + micro variation
wear = nt.nodes.new("ShaderNodeTexNoise")
wear.inputs["Scale"].default_value = 0.55; wear.inputs["Detail"].default_value = 4
nt.links.new(coord.outputs["Object"], wear.inputs["Vector"])
wearrange = nt.nodes.new("ShaderNodeMapRange")
wearrange.inputs["To Min"].default_value = 0.15
wearrange.inputs["To Max"].default_value = 0.42
nt.links.new(wear.outputs["Fac"], wearrange.inputs["Value"])
micro = nt.nodes.new("ShaderNodeTexNoise")
micro.inputs["Scale"].default_value = 60; micro.inputs["Detail"].default_value = 4
nt.links.new(coord.outputs["Object"], micro.inputs["Vector"])
microrange = nt.nodes.new("ShaderNodeMapRange")
microrange.inputs["To Min"].default_value = -0.05
microrange.inputs["To Max"].default_value = 0.05
nt.links.new(micro.outputs["Fac"], microrange.inputs["Value"])
raddm = nt.nodes.new("ShaderNodeMath"); raddm.operation = 'ADD'
nt.links.new(wearrange.outputs["Result"], raddm.inputs[0])
nt.links.new(microrange.outputs["Result"], raddm.inputs[1])
roughmix = nt.nodes.new("ShaderNodeMixRGB")
nt.links.new(tilemask.outputs["Result"], roughmix.inputs["Fac"])
roughmix.inputs["Color1"].default_value = (0.85, 0.85, 0.85, 1)   # joint mat
nt.links.new(raddm.outputs["Value"], roughmix.inputs["Color2"])
nt.links.new(roughmix.outputs["Color"], bsdf.inputs["Roughness"])

# relief : joint creuse + chanfrein (tilemask) + micro grain
hmix = nt.nodes.new("ShaderNodeMath"); hmix.operation = 'MULTIPLY_ADD'
nt.links.new(micro.outputs["Fac"], hmix.inputs[0])
hmix.inputs[1].default_value = 0.04
nt.links.new(tilemask.outputs["Result"], hmix.inputs[2])
bump = nt.nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value = 0.35
bump.inputs["Distance"].default_value = 0.002
nt.links.new(hmix.outputs["Value"], bump.inputs["Height"])
nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

# ---------------- scene de test ----------------
bpy.ops.mesh.primitive_plane_add(size=14, location=(0, 0, 0))
floor = bpy.context.object; floor.data.materials.append(mat)

# mur anthracite au fond pour les reflets + plinthe
wallm = bpy.data.materials.new("wall"); wallm.use_nodes = True
wallm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.055, 0.06, 0.065, 1)
wallm.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.55
bpy.ops.mesh.primitive_cube_add(location=(0, 3.2, 1.35))
wall = bpy.context.object; wall.scale = (7, 0.05, 1.35); wall.data.materials.append(wallm)

whitem = bpy.data.materials.new("white"); whitem.use_nodes = True
whitem.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.85, 0.84, 0.80, 1)
bpy.ops.mesh.primitive_cube_add(location=(-4.5, 3.15, 1.35))
w2 = bpy.context.object; w2.scale = (2.5, 0.04, 1.35); w2.data.materials.append(whitem)

# plafond discret
bpy.ops.mesh.primitive_plane_add(size=14, location=(0, 0, 2.7))
ceil = bpy.context.object; ceil.rotation_euler = (math.pi, 0, 0)
ceil.data.materials.append(whitem)

# spots chauds en ligne (reflets rasants sur le sol)
for x in (-2.4, -0.8, 0.8, 2.4):
    bpy.ops.object.light_add(type='AREA', location=(x, 1.8, 2.62))
    L = bpy.context.object
    L.data.energy = 70; L.data.size = 0.22
    L.data.color = (1.0, 0.88, 0.72)

# nappe douce derriere la camera (lumiere du magasin)
bpy.ops.object.light_add(type='AREA', location=(0, -4.5, 2.2))
L = bpy.context.object; L.data.energy = 130; L.data.size = 5
L.data.color = (0.95, 0.94, 0.90)
L.rotation_euler = (math.radians(-60), 0, 0)

world = bpy.data.worlds.new("w"); world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.5, 0.48, 0.44, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.15
SC.world = world

# camera basse en angle rasant, legere profondeur de champ
bpy.ops.object.camera_add(location=(-1.8, -3.6, 1.05))
cam = bpy.context.object
cam.data.lens = 28; cam.data.sensor_width = 36
cam.data.dof.use_dof = True
cam.data.dof.focus_distance = 2.6
cam.data.dof.aperture_fstop = 9.0
from mathutils import Vector
d = Vector((0.8, 2.5, 0.0)) - cam.location
cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
SC.camera = cam

SC.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print("RENDER OK ->", OUT)
