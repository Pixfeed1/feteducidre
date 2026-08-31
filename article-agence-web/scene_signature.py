"""
La photographie de fond de l'image à la une — rendue, pas cherchée.

    python3 article-agence-web/scene_signature.py

Produit `article-agence-web/fond-signature.png` (1600 × 900).

----------------------------------------------------------------------------
POURQUOI UN RENDU PLUTÔT QU'UNE BANQUE D'IMAGES
----------------------------------------------------------------------------
Pexels, Unsplash, Wikimedia : tous injoignables depuis cet environnement, la
politique de sortie les refuse. Mais une photo de banque n'était de toute
façon pas le meilleur choix — celles qui illustrent « signer un contrat » sont
vues partout, et une image à la une qu'on a déjà croisée dix fois ne retient
personne.

Le rendu règle les deux : le cadrage est fait pour cette image-là, et la
question de la licence ne se pose pas.

----------------------------------------------------------------------------
LE CADRAGE EST DICTÉ PAR LE TEXTE QUI VIENDRA DESSUS
----------------------------------------------------------------------------
Ce n'est pas une photo qu'on illustrera ensuite, c'est un FOND. Le sujet — le
contrat et le stylo — est donc calé dans le tiers gauche, et les deux tiers
droits sont laissés à une table qui s'éloigne dans le flou. C'est là que le
titre ira, et il se posera sur une zone sans détail, donc lisible.

La profondeur de champ n'est pas un effet : c'est elle qui crée cette zone
calme. À f/1.8 avec la mise au point sur les feuilles, le fond se dissout, et
un texte blanc posé dessus n'a plus rien à combattre.

----------------------------------------------------------------------------
LA LUMIÈRE
----------------------------------------------------------------------------
Une seule fenêtre à gauche, comme dans les autres rendus de ce dépôt. Elle
place naturellement les hautes lumières à gauche — sur le contrat — et laisse
la droite descendre dans l'ombre, ce qui va dans le même sens que le cadrage.
"""

import math
import os

import bpy

RACINE = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(RACINE, "fond-signature")

RESOLUTION = (1600, 900)
ECHANTILLONS = 160


def matiere(nom, base, rugosite, metal=0.0):
    m = bpy.data.materials.new(nom)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*base, 1.0)
    p.inputs["Roughness"].default_value = rugosite
    p.inputs["Metallic"].default_value = metal
    return m


def pave(nom, x0, x1, y0, y1, z0, z1, mat, biseau=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    ob = bpy.context.object
    ob.name = nom
    ob.location = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    ob.scale = (x1 - x0, y1 - y0, z1 - z0)
    bpy.ops.object.transform_apply(scale=True)
    ob.data.materials.append(mat)
    if biseau > 0:
        b = ob.modifiers.new("B", 'BEVEL')
        b.width = biseau
        b.segments = 3
    return ob


def scene():
    """
    Un bureau, à L'ÉCHELLE RÉELLE.

    Premier essai : des feuilles de 80 cm de large. Rien ne le signalait —
    Blender ne se plaint pas d'un contrat grand comme une table — mais au
    rendu il ne restait qu'une nappe blanche sans sujet. Une feuille A4 fait
    0,210 × 0,297 m, un stylo 14 cm, une tasse 8 cm de diamètre : tout part
    de là, et le cadrage suit.
    """
    bpy.ops.wm.read_factory_settings(use_empty=True)

    bois = matiere("BOIS", (0.132, 0.082, 0.048), 0.34)
    papier = matiere("PAPIER", (0.880, 0.870, 0.848), 0.66)
    encre = matiere("ENCRE", (0.048, 0.045, 0.052), 0.52)
    metal = matiere("METAL", (0.760, 0.740, 0.700), 0.24, metal=1.0)
    ceramique = matiere("CERAMIQUE", (0.700, 0.692, 0.680), 0.30)
    mur = matiere("MUR", (0.520, 0.512, 0.500), 0.92)

    pave("Table", -1.2, 1.2, -0.9, 1.4, -0.04, 0.0, bois)
    pave("Mur", -1.6, 1.6, 1.4, 1.45, -0.2, 1.2, mur)

    #  LE CONTRAT : cinq feuilles A4 très légèrement décalées.
    A, B = 0.210, 0.297
    cx, cy = -0.085, 0.020
    for i in range(5):
        d = i * 0.0012
        pave("Feuille%d" % i,
             cx - A / 2 + d * 1.6, cx + A / 2 + d * 1.6,
             cy - B / 2 + d, cy + B / 2 + d,
             i * 0.00011, 0.0001 + i * 0.00011, papier)
    haut = 5 * 0.00011 + 0.0001

    #  Le texte suggéré : des filets fins, pas des mots. À cette distance on
    #  ne lirait rien de toute façon, et de faux mots attireraient l'oeil.
    for i in range(7):
        y = cy + 0.10 - i * 0.016
        long = A * (0.74 if i % 3 else 0.52)
        pave("L%d" % i, cx - A / 2 + 0.018, cx - A / 2 + 0.018 + long,
             y, y + 0.0016, haut, haut + 0.00012, encre)
    #  Et le trait de signature, plus bas, plus court : c'est le sujet.
    pave("Signature", cx - A / 2 + 0.020, cx - A / 2 + 0.020 + A * 0.45,
         cy - 0.105, cy - 0.1034, haut, haut + 0.00014, encre)

    #  LE STYLO, 14 cm, posé en biais sur les feuilles.
    ang = math.radians(24.0)
    lg, r = 0.14, 0.0052
    px, py = cx + 0.030, cy - 0.058
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=lg,
                                        location=(px, py, haut + r))
    st = bpy.context.object
    st.name = "Stylo"
    st.rotation_euler = (0.0, math.radians(90.0), ang)
    st.data.materials.append(encre)
    #  La pointe, dans l'axe : calculée, pour qu'elle ne flotte pas à côté.
    tx = px + (lg / 2 + 0.010) * math.cos(ang)
    ty = py + (lg / 2 + 0.010) * math.sin(ang)
    bpy.ops.mesh.primitive_cone_add(radius1=r, radius2=0.0006, depth=0.020,
                                    location=(tx, ty, haut + r))
    po = bpy.context.object
    po.name = "Pointe"
    po.rotation_euler = (0.0, math.radians(90.0), ang)
    po.data.materials.append(metal)

    #  Une tasse et un carnet, plus loin à droite : de la matière à fondre
    #  dans le flou, là où le titre se posera.
    bpy.ops.mesh.primitive_cylinder_add(radius=0.040, depth=0.095,
                                        location=(0.235, 0.175, 0.047))
    bpy.context.object.name = "Tasse"
    bpy.context.object.data.materials.append(ceramique)
    pave("Carnet", 0.245, 0.395, -0.115, 0.095, 0.0, 0.011, encre,
         biseau=0.0015)

    #  LA FENÊTRE, à gauche. Une seule source, comme les autres rendus.
    d = bpy.data.lights.new("FENETRE", type='AREA')
    d.shape = 'RECTANGLE'
    d.size, d.size_y = 1.1, 0.8
    d.energy = 42.0
    d.color = (1.0, 0.965, 0.915)
    lo = bpy.data.objects.new("FENETRE", d)
    lo.location = (-0.62, 0.10, 0.52)
    lo.rotation_euler = (0.0, math.radians(-62.0), 0.0)
    bpy.context.collection.objects.link(lo)

    w = bpy.data.worlds.new("MONDE")
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = \
        (0.048, 0.050, 0.058, 1.0)
    bpy.context.scene.world = w


def camera():
    cd = bpy.data.cameras.new("CAM")
    cd.lens = 50.0
    #  LA PROFONDEUR DE CHAMP FAIT LA PLACE DU TEXTE. Mise au point sur les
    #  feuilles ; à f/2.8 et 60 cm, la tasse et le carnet se dissolvent, et le
    #  titre aura un fond sans détail.
    cd.dof.use_dof = True
    cd.dof.focus_distance = 0.60
    cd.dof.aperture_fstop = 2.8
    ob = bpy.data.objects.new("CAM", cd)
    ob.location = (-0.30, -0.46, 0.32)
    cible = (-0.02, 0.02, 0.012)
    from mathutils import Vector
    ob.rotation_euler = (Vector(cible) - ob.location) \
        .to_track_quat('-Z', 'Y').to_euler()
    bpy.context.collection.objects.link(ob)
    bpy.context.scene.camera = ob


def reglages():
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_EEVEE_NEXT'
    sc.render.resolution_x, sc.render.resolution_y = RESOLUTION
    sc.render.image_settings.file_format = 'PNG'
    e = sc.eevee
    e.taa_render_samples = ECHANTILLONS
    e.use_raytracing = True
    e.ray_tracing_method = 'SCREEN'
    e.use_shadows = True
    e.shadow_ray_count = 4
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - Medium High Contrast'
    sc.view_settings.exposure = 0.25


def main():
    scene()
    camera()
    reglages()
    bpy.context.scene.render.filepath = SORTIE + ".png"
    bpy.ops.render.render(write_still=True)
    print("  -> %s.png" % SORTIE)


if __name__ == "__main__":
    main()
