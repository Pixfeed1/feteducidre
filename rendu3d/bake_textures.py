# Bake des materiaux proceduraux en maps PBR 4K (couleur / rugosite / normale).
# Usage : blender -b -P bake_textures.py -- <nom_materiau> <dossier_sortie> [taille]
import bpy, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from materials import MATERIALS

argv = sys.argv[sys.argv.index("--") + 1:]
mat_name, outdir = argv[0], argv[1]
size = int(argv[2]) if len(argv) > 2 else 4096
os.makedirs(outdir, exist_ok=True)

bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete()
SC = bpy.context.scene
SC.render.engine = 'CYCLES'
SC.cycles.device = 'CPU'
SC.cycles.samples = 4
SC.cycles.use_denoising = False  # build apt sans OIDN : denoise actif = bake noir
SC.render.bake.margin = 4

bpy.ops.mesh.primitive_plane_add(size=1)
plane = bpy.context.object

mat = bpy.data.materials.new(mat_name); mat.use_nodes = True
nt = mat.node_tree
for n in list(nt.nodes):
    nt.nodes.remove(n)
out = nt.nodes.new("ShaderNodeOutputMaterial")
plane.data.materials.append(mat)

sockets = MATERIALS[mat_name](nt)

emit = nt.nodes.new("ShaderNodeEmission")
bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
bump = nt.nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value = sockets["bump"]
if sockets.get("height") is not None:
    nt.links.new(sockets["height"], bump.inputs["Height"])
nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

img_node = nt.nodes.new("ShaderNodeTexImage")
nt.nodes.active = img_node


def bake(kind, filename, colorspace):
    img = bpy.data.images.new(f"bake_{kind}", size, size, alpha=False,
                              float_buffer=(kind == "normal"))
    img.colorspace_settings.name = colorspace
    img_node.image = img
    # cablage de sortie selon la map
    for l in list(out.inputs["Surface"].links):
        nt.links.remove(l)
    if kind == "normal":
        nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
        bpy.ops.object.bake(type='NORMAL', normal_space='TANGENT')
    else:
        src = sockets["rough"] if kind == "rough" else sockets["color"]
        if kind == "rough" and src is None:
            emit.inputs["Color"].default_value = (sockets["rough_value"],) * 3 + (1,)
        else:
            nt.links.new(src, emit.inputs["Color"])
        nt.links.new(emit.outputs["Emission"], out.inputs["Surface"])
        bpy.ops.object.bake(type='EMIT')
    img.filepath_raw = os.path.join(outdir, filename)
    img.file_format = 'PNG'
    img.save()
    bpy.data.images.remove(img)
    print("BAKED", kind, "->", filename)


bake("color", f"{mat_name}_color_{size//1024}k.png", "sRGB")
bake("rough", f"{mat_name}_rough_{size//1024}k.png", "Non-Color")
bake("normal", f"{mat_name}_normal_{size//1024}k.png", "Non-Color")
with open(os.path.join(outdir, "META.txt"), "w") as f:
    f.write(f"span_m={sockets['span']}\nmetallic={sockets['metal']}\nbump={sockets['bump']}\n")
print("DONE", mat_name)
