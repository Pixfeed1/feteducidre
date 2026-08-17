"""
Fabrique `template.blend` — la scène modèle.

    blender -b --factory-startup --python src/faire_template.py

À NE LANCER QU'UNE FOIS. Le `.blend` produit est versionné et devient la
référence visuelle du projet ; `build_reel.py` ne fait ensuite que le REMPLIR
et l'animer, il ne le reconstruit jamais.

  ┌──────────────────────────────────────────────────────────────────────┐
  │ ÉCART ASSUMÉ AVEC LE CAHIER DES CHARGES                              │
  │                                                                      │
  │ Le cahier demande que template.blend soit construit « une seule fois │
  │ à la main » dans l'interface de Blender. Cette session n'a pas       │
  │ d'interface graphique : le modèle est donc produit par ce script,    │
  │ une fois, puis versionné comme un binaire. L'intention du cahier est │
  │ respectée — le .blend reste la référence, build_reel.py ne le        │
  │ régénère pas — et le modèle redevient modifiable à la souris dès     │
  │ qu'on l'ouvre sur un poste de travail.                               │
  └──────────────────────────────────────────────────────────────────────┘
"""

import os
import sys
import math

import bpy
import bmesh

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "src"))
import grammar as G                                            # noqa: E402


def srgb(c):
    """Les couleurs de la charte sont données telles qu'on les lit dans un
    sélecteur (sRGB) ; Blender travaille en linéaire."""
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4
                 for x in c)


# ---------------------------------------------------------------------------
#  OUTILS DE GÉOMÉTRIE
# ---------------------------------------------------------------------------

def contour_arrondi(largeur, hauteur, rayon, par_coin=10):
    """
    Points d'un rectangle à coins arrondis, dans le sens trigonométrique.

    Les centres des quarts de cercle ne dépendent PAS du rayon choisi mais
    seulement des dimensions : deux contours emboîtés (extérieur et
    intérieur d'un cadre) échantillonnés aux mêmes angles se correspondent
    donc point à point, ce qui permet de les relier par des quadrilatères
    sans aucun calcul supplémentaire.
    """
    dx, dy = largeur / 2.0 - rayon, hauteur / 2.0 - rayon
    centres = [(dx, dy, 0.0), (-dx, dy, math.pi / 2),
               (-dx, -dy, math.pi), (dx, -dy, 3 * math.pi / 2)]
    pts = []
    for cx, cy, a0 in centres:
        for i in range(par_coin + 1):
            a = a0 + (math.pi / 2) * i / float(par_coin)
            pts.append((cx + rayon * math.cos(a), cy + rayon * math.sin(a)))
    return pts


def maillage_depuis_faces(nom, faces_xy, z):
    """Construit un maillage plat à partir d'une liste de polygones 2D."""
    me = bpy.data.meshes.new(nom)
    bm = bmesh.new()
    for poly in faces_xy:
        vs = [bm.verts.new((x, y, z)) for x, y in poly]
        bm.faces.new(vs)
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    return me


def plan_uv(nom, largeur, hauteur, z=0.0):
    """Un quadrilatère avec ses coordonnées de texture posées explicitement.
    On ne compte jamais sur les UV par défaut d'une primitive."""
    me = bpy.data.meshes.new(nom)
    hw, hh = largeur / 2.0, hauteur / 2.0
    me.from_pydata([(-hw, -hh, z), (hw, -hh, z), (hw, hh, z), (-hw, hh, z)],
                   [], [(0, 1, 2, 3)])
    me.update()
    uv = me.uv_layers.new(name="UV")
    for i, co in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]):
        uv.data[i].uv = co
    return me


def objet(nom, donnee, materiau=None, parent=None):
    ob = bpy.data.objects.new(nom, donnee)
    bpy.context.collection.objects.link(ob)
    if materiau is not None and hasattr(donnee, "materials"):
        donnee.materials.append(materiau)
    if parent is not None:
        ob.parent = parent
    return ob


# ---------------------------------------------------------------------------
#  MATÉRIAUX
# ---------------------------------------------------------------------------

def mat_emission(nom, couleur, melange="OPAQUE"):
    mat = bpy.data.materials.new(nom)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*srgb(couleur), 1.0)
    em.inputs["Strength"].default_value = G.EMISSION_FORCE
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    mat.blend_method = melange
    mat.shadow_method = "NONE"
    return mat


def mat_ecran(nom):
    """
    Le matériau d'un écran : une image, en ÉMISSION PURE de force 1.

    Un écran ne doit dépendre d'aucun éclairage de la scène — sinon la
    capture ressort plus sombre ou plus chaude que le site réel, et la
    comparaison avant/après devient un mensonge sur les couleurs.

    Le nœud d'image s'appelle « TEX » : build_reel.py remplace SON IMAGE, il
    ne reconstruit jamais ce matériau.
    """
    mat = bpy.data.materials.new(nom)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.name = tex.label = "TEX"
    tex.location = (-320, 0)
    tex.extension = "EXTEND"
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = G.EMISSION_FORCE
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (240, 0)
    nt.links.new(tex.outputs["Color"], em.inputs["Color"])
    nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    mat.blend_method = "OPAQUE"
    mat.shadow_method = "NONE"
    #  L'élimination des faces arrière fait tout le travail de la bascule :
    #  à 0° on voit l'avant, à 180° on voit l'après, sans une seule clé de
    #  visibilité à poser.
    mat.use_backface_culling = True
    return mat


def mat_couleur_objet(nom):
    """
    UN SEUL matériau pour tous les textes. La couleur ET l'opacité sont
    portées par la couleur d'objet (`ob.color`), lue par un nœud « Object
    Info ». On anime donc l'apparition d'un texte sans toucher au matériau,
    et les vingt objets texte de la scène partagent un unique nuanceur.
    """
    mat = bpy.data.materials.new(nom)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    info = nt.nodes.new("ShaderNodeObjectInfo")
    info.location = (-460, 0)
    em = nt.nodes.new("ShaderNodeEmission")
    em.location = (-200, -60)
    em.inputs["Strength"].default_value = G.EMISSION_FORCE
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    tr.location = (-200, 120)
    mix = nt.nodes.new("ShaderNodeMixShader")
    mix.location = (40, 0)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (280, 0)
    nt.links.new(info.outputs["Color"], em.inputs["Color"])
    nt.links.new(info.outputs["Alpha"], mix.inputs["Fac"])
    nt.links.new(tr.outputs["BSDF"], mix.inputs[1])
    nt.links.new(em.outputs["Emission"], mix.inputs[2])
    nt.links.new(mix.outputs["Shader"], out.inputs["Surface"])
    mat.blend_method = "BLEND"
    mat.shadow_method = "NONE"
    return mat


# ---------------------------------------------------------------------------
#  LA SCÈNE
# ---------------------------------------------------------------------------

def reglages():
    sc = bpy.context.scene
    sc.render.engine = ("BLENDER_EEVEE_NEXT"
                        if "BLENDER_EEVEE_NEXT" in
                        sc.render.bl_rna.properties["engine"].enum_items
                        else "BLENDER_EEVEE")
    #  Blender 4.2 LTS a renommé le moteur ; 4.0 et 4.1 ne connaissent que
    #  l'ancien nom. On prend celui que la version présente sait ouvrir.
    try:
        sc.eevee.taa_render_samples = G.ECHANTILLONS
    except AttributeError:
        pass
    sc.render.resolution_x = G.LARGEUR_PX
    sc.render.resolution_y = G.HAUTEUR_PX
    sc.render.resolution_percentage = 100
    sc.render.fps = G.IMAGES_PAR_SECONDE
    sc.frame_start = G.IMAGE_PREMIERE
    sc.frame_end = G.IMAGE_DERNIERE
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGB"
    sc.render.film_transparent = False

    #  LE RÉGLAGE QUI FAIT LE PLUS DE DÉGÂTS QUAND ON L'OUBLIE.
    #  Blender applique AgX par défaut : les captures d'écran ressortent
    #  délavées et les couleurs d'interface sont fausses. « Standard » rend
    #  la valeur exacte du pixel source.
    sc.view_settings.view_transform = G.TRANSFORMATION_VUE
    sc.view_settings.look = "None"
    sc.view_settings.exposure = 0.0
    sc.view_settings.gamma = 1.0


def camera():
    cd = bpy.data.cameras.new("CAM")
    cd.type = "ORTHO"
    cd.sensor_fit = "VERTICAL"
    cd.ortho_scale = 2 * G.DEMI_HAUTEUR          # 19,20 -> 1 unité = 100 px
    cd.clip_start = 0.1
    cd.clip_end = 200.0
    cam = objet("CAM", cd)
    cam.location = (0.0, 0.0, G.Z_CAMERA)
    cam.rotation_euler = (0.0, 0.0, 0.0)         # strictement de face
    bpy.context.scene.camera = cam
    return cam


def fond(mat):
    me = plan_uv("M_BG", 2 * G.DEMI_LARGEUR + 1.0, 2 * G.DEMI_HAUTEUR + 1.0)
    ob = objet("BG", me, mat)
    ob.location = (0.0, 0.0, G.Z_FOND)
    return ob


def appareil(mat):
    """Le cadre du téléphone : un anneau à coins arrondis, opaque."""
    ext = contour_arrondi(G.ECRAN_LARGEUR + 2 * G.APPAREIL_BORD,
                          G.ECRAN_HAUTEUR + 2 * G.APPAREIL_BORD,
                          G.APPAREIL_RAYON)
    inte = contour_arrondi(G.ECRAN_LARGEUR, G.ECRAN_HAUTEUR,
                           G.APPAREIL_RAYON - G.APPAREIL_BORD)
    faces = []
    n = len(ext)
    for i in range(n):
        j = (i + 1) % n
        faces.append([ext[i], ext[j], inte[j], inte[i]])
    me = maillage_depuis_faces("M_DEVICE", faces, 0.0)
    ob = objet("DEVICE", me, mat)
    ob.location = (0.0, G.APPAREIL_CENTRE_Y, G.Z_APPAREIL)
    return ob


def masque(mat):
    """
    SCREEN_MASK — ce qui cache le débord du défilement.

    Quatre barres plus quatre éventails de coin, plutôt qu'un grand
    rectangle percé : relier un contour à quatre points à un contour arrondi
    à quarante points demanderait un pontage, alors que quatre barres et
    quatre éventails se posent directement et ne peuvent pas se vriller.

    Le masque est FIXE, il ne suit pas la bascule. Sous projection
    orthographique, une rotation autour de l'axe vertical laisse la hauteur
    apparente inchangée : le débord à masquer est purement vertical, donc un
    masque immobile suffit pendant toute la bascule.
    """
    L = 40.0                                    # largement plus grand que le cadre
    hw, hh = G.ECRAN_LARGEUR / 2.0, G.ECRAN_HAUTEUR / 2.0
    r = G.APPAREIL_RAYON - G.APPAREIL_BORD
    faces = [
        [(-L, hh), (L, hh), (L, L), (-L, L)],           # au-dessus
        [(-L, -L), (L, -L), (L, -hh), (-L, -hh)],       # au-dessous
        [(-L, -hh), (-hw, -hh), (-hw, hh), (-L, hh)],   # à gauche
        [(hw, -hh), (L, -hh), (L, hh), (hw, hh)],       # à droite
    ]
    #  Les éventails de coin : ils comblent l'espace entre le coin carré de
    #  l'écran et l'arc du cadre, sinon l'angle de la capture dépasse.
    for sx, sy, a0 in ((1, 1, 0.0), (-1, 1, math.pi / 2),
                       (-1, -1, math.pi), (1, -1, 3 * math.pi / 2)):
        cx, cy = sx * (hw - r), sy * (hh - r)
        carre = (sx * hw, sy * hh)
        pas = 8
        for i in range(pas):
            a = a0 + (math.pi / 2) * i / float(pas)
            b = a0 + (math.pi / 2) * (i + 1) / float(pas)
            faces.append([carre,
                          (cx + r * math.cos(a), cy + r * math.sin(a)),
                          (cx + r * math.cos(b), cy + r * math.sin(b))])
    me = maillage_depuis_faces("M_MASK", faces, 0.0)
    ob = objet("SCREEN_MASK", me, mat)
    ob.location = (0.0, G.APPAREIL_CENTRE_Y, G.Z_MASQUE)
    return ob


def ecrans(mat_avant, mat_apres):
    """
    PIVOT porte la bascule ; les deux écrans sont ses enfants.

    SCREEN_AFTER est posé à 180° dans le repère local : quand PIVOT atteint
    180°, sa rotation totale vaut 360°, il se présente donc à l'endroit et
    non en miroir. C'est le seul agencement qui donne une bascule correcte
    sans retourner la texture.
    """
    pivot = bpy.data.objects.new("PIVOT", None)
    bpy.context.collection.objects.link(pivot)
    pivot.empty_display_type = "PLAIN_AXES"
    pivot.empty_display_size = 1.0
    pivot.location = (0.0, G.APPAREIL_CENTRE_Y, G.Z_ECRAN)

    #  Hauteur provisoire : build_reel.py la remet au rapport réel de la
    #  capture. Le modèle ne peut pas la connaître, elle dépend du site.
    haut = G.ECRAN_HAUTEUR * 3.0
    obs = []
    for nom, mat, rot in (("SCREEN_BEFORE", mat_avant, 0.0),
                          ("SCREEN_AFTER", mat_apres, math.pi)):
        me = plan_uv("M_" + nom, G.ECRAN_LARGEUR, haut)
        ob = objet(nom, me, mat, parent=pivot)
        ob.location = (0.0, 0.0, 0.0)
        ob.rotation_euler = (0.0, rot, 0.0)
        obs.append(ob)
    return pivot, obs


def voile(mat):
    """Le bandeau sombre posé sous les incrustations : sans lui, un texte
    blanc sur une capture claire devient illisible."""
    me = plan_uv("M_VOILE", 2 * G.DEMI_LARGEUR + 1.0, G.INCRUST_BANDE_HAUT)
    ob = objet("VOILE_INCRUST", me, mat)
    ob.location = (0.0, G.INCRUST_Y, G.Z_VOILE)
    #  Couleur d'objet = valeur LINÉAIRE (voir la note dans build_reel.py)
    ob.color = (*srgb(G.VOILE), 0.0)
    return ob


TEXTES = [
    ("TXT_CLIENT",  "titre",   G.T_CLIENT),
    ("TXT_SECTEUR", "texte",   G.T_SECTEUR),
    ("TXT_ANNEE",   "texte",   G.T_ANNEE),
    ("TXT_HOOK",    "titre",   G.T_HOOK),
    ("TXT_A1",      "titre",   G.T_POINT),
    ("TXT_A2",      "titre",   G.T_POINT),
    ("TXT_A3",      "titre",   G.T_POINT),
    ("TXT_B1",      "titre",   G.T_POINT),
    ("TXT_B2",      "titre",   G.T_POINT),
    ("TXT_B3",      "titre",   G.T_POINT),
    ("TXT_NUM",     "titre",   G.T_NUM),
    ("TXT_NUM_LEG", "texte",   G.T_NUM_LEG),
    ("TXT_SORTIE",  "titre",   G.T_SORTIE),
    ("TXT_CTA",     "texte",   G.T_CTA),
]


def textes(mat):
    polices = {
        "titre": bpy.data.fonts.load(os.path.join(RACINE, G.POLICE_TITRE)),
        "texte": bpy.data.fonts.load(os.path.join(RACINE, G.POLICE_TEXTE)),
    }
    obs = []
    for nom, style, taille in TEXTES:
        cu = bpy.data.curves.new(nom, type="FONT")
        cu.font = polices[style]
        cu.body = nom                       # remplacé par build_reel.py
        cu.size = taille
        cu.align_x = "CENTER"
        cu.align_y = "CENTER"
        cu.space_line = G.INTERLIGNE
        ob = objet(nom, cu, mat)
        ob.location = (0.0, 0.0, G.Z_TEXTE)
        ob.color = (*srgb(G.BLANC), 0.0)    # invisible au départ
        obs.append(ob)
    return obs


def logo(mat):
    """
    LOGO — importé depuis assets/svg/logo.svg, en courbes.

    Si l'extension d'import SVG n'est pas disponible (elle ne l'est pas
    toujours dans une compilation minimale), on retombe sur le même tracé
    construit en maillage. La forme est identique : les deux chemins partent
    des mêmes cinq rectangles.
    """
    svg = os.path.join(RACINE, "assets", "svg", "logo.svg")
    avant = set(bpy.data.objects.keys())
    importe = False
    try:
        bpy.ops.preferences.addon_enable(module="io_curve_svg")
    except Exception:
        pass
    try:
        bpy.ops.import_curve.svg(filepath=svg)
        importe = True
    except Exception as e:
        print("  (import SVG indisponible : %s — repli en maillage)" % e)

    nouveaux = [bpy.data.objects[k] for k in bpy.data.objects.keys()
                if k not in avant]
    if importe and nouveaux:
        bpy.ops.object.select_all(action="DESELECT")
        for ob in nouveaux:
            ob.select_set(True)
        bpy.context.view_layer.objects.active = nouveaux[0]
        if len(nouveaux) > 1:
            bpy.ops.object.join()
        ob = bpy.context.view_layer.objects.active
        ob.data.materials.clear()
        ob.data.materials.append(mat)
    else:
        sys.path.insert(0, os.path.join(RACINE, "src"))
        from faire_logo_svg import P, BLOCS, COTE
        faces = []
        for a, b, c, d in BLOCS:
            #  en SVG l'axe vertical descend, en 3D il monte
            faces.append([(P[a], COTE - P[b]), (P[c], COTE - P[b]),
                          (P[c], COTE - P[d]), (P[a], COTE - P[d])])
        ob = objet("LOGO_TMP", maillage_depuis_faces("M_LOGO", faces, 0.0),
                   mat)

    ob.name = "LOGO"
    ob.data.name = "M_LOGO"
    #  On recentre et on met à la largeur de charte, quelle que soit la
    #  façon dont la forme est arrivée dans la scène.
    bpy.context.view_layer.update()
    dim = ob.dimensions
    k = G.LOGO_LARGEUR / max(dim.x, 1e-6)
    ob.scale = (k, k, k)
    bpy.context.view_layer.update()
    centre = sum((ob.matrix_world @ v.co for v in _sommets(ob)),
                 __import__("mathutils").Vector((0, 0, 0))) / max(
        1, len(_sommets(ob)))
    ob.location = (-centre.x, G.LOGO_Y - centre.y, G.Z_TEXTE)
    ob.color = (*srgb(G.BLANC), 0.0)
    return ob


def _sommets(ob):
    if ob.type == "MESH":
        return ob.data.vertices
    pts = []
    for sp in ob.data.splines:
        pts += list(sp.bezier_points) + list(sp.points)
    return pts


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    reglages()

    m_fond = mat_emission("MAT_BG", G.ENCRE)
    m_encre = mat_emission("MAT_ENCRE", G.ENCRE)
    m_texte = mat_couleur_objet("MAT_TEXTE")
    m_av = mat_ecran("MAT_SCREEN_BEFORE")
    m_ap = mat_ecran("MAT_SCREEN_AFTER")

    camera()
    fond(m_fond)
    ecrans(m_av, m_ap)
    masque(m_encre)
    appareil(m_encre)
    voile(m_texte)
    textes(m_texte)
    logo(m_texte)

    chemin = os.path.join(RACINE, "template.blend")
    bpy.ops.wm.save_as_mainfile(filepath=chemin)
    attendus = ["CAM", "BG", "DEVICE", "SCREEN_BEFORE", "SCREEN_AFTER",
                "SCREEN_MASK", "PIVOT", "LOGO", "VOILE_INCRUST"] + \
               [n for n, _, _ in TEXTES]
    manquants = [n for n in attendus if n not in bpy.data.objects]
    print("template.blend écrit — %d objets, %d matériaux%s"
          % (len(bpy.data.objects), len(bpy.data.materials),
             "" if not manquants else "  MANQUE : %s" % manquants))
    if manquants:
        sys.exit(1)


main()
