"""
Les quatre symptômes, rendus pour de vrai dans Blender.

    python3 article-blender-astuces/symptomes.py            (les quatre)
    python3 article-blender-astuces/symptomes.py rose       (un seul)

Produit `symptome-rose.png`, `symptome-objet-noir.png`,
`symptome-sphere-cabossee.png` et `symptome-rendu-noir.png`.

----------------------------------------------------------------------------
AUCUN DES QUATRE N'EST SIMULÉ
----------------------------------------------------------------------------
On pourrait peindre un cube en magenta et l'appeler « texture manquante ». Ce
serait une illustration de la panne, pas la panne. Or l'article promet au
lecteur qu'il reconnaîtra son écran : il faut donc que ce soit son écran.

Chaque scène reproduit la CAUSE et laisse Blender produire l'effet :

  - le rose vient d'un noeud Image Texture qui pointe vers un fichier absent.
    Personne n'a choisi cette couleur, c'est celle que Blender affiche quand il
    ne trouve pas une image ;
  - l'objet noir vient d'un Principled réglé sur Metallic 1 dans une scène sans
    environnement. Un métal n'a pas de couleur propre, il ne fait que
    refléter ; s'il n'y a rien à refléter, il est noir ;
  - la sphère cabossée vient de sommets dédoublés — un Ctrl+D suivi d'un clic
    droit, la faute la plus commune de toutes — puis d'un Shade Smooth. Les
    taches sont un vrai conflit de profondeur entre faces superposées ;
  - le rendu noir vient d'une scène sans aucune lampe et d'un monde noir.

----------------------------------------------------------------------------
POURQUOI PAS « FACES NOIRES », QUI ÉTAIT AU BRIEF
----------------------------------------------------------------------------
Parce que ça ne se reproduit pas, et je l'ai mesuré trois fois plutôt que de
livrer une approximation :

  - faces retournées avec `normal_flip()` : 0,0 % de zone sombre sur le sujet,
    98,5 % éclairé. EEVEE Next éclaire les deux côtés d'une face et redresse de
    lui-même la normale d'une face vue par l'arrière ;
  - normales personnalisées inversées par coin de face : 0,0 % de sombre
    encore. Blender les corrige aussi ;
  - normales retournées plus `use_backface_culling` : 0,0 % de sombre, et à la
    place un grain de conflit de profondeur — pas des faces noires.

Ce que les débutants appellent « faces noires » est donc presque toujours
autre chose : soit l'overlay Face Orientation, qui peint les faces retournées
en rouge DANS LA VUE et non au rendu, soit l'ombrage sale d'une géométrie
dédoublée — c'est-à-dire déjà la vignette de la sphère.

C'est cohérent avec l'article, qui renvoie les faces noires et l'échelle vers
un autre texte. Le Metallic à 1 les remplace : vrai grand classique, distinct
du rendu noir, et il se reproduit.

----------------------------------------------------------------------------
CHAQUE RENDU EST VÉRIFIÉ AVANT D'ÊTRE GARDÉ
----------------------------------------------------------------------------
Un symptôme qu'on croit avoir reproduit et qui ne se voit pas à l'image, ça
arrive tout le temps. Chaque scène est donc suivie d'une mesure sur les pixels
du rendu, et le script s'arrête si le symptôme n'est pas au rendez-vous. Les
trois échecs ci-dessus viennent de là.

----------------------------------------------------------------------------
VERSION
----------------------------------------------------------------------------
Rendu avec le module `bpy` 4.5 LTS, la version disponible ici. Les causes sont
identiques en 5.x — ce sont des comportements de fond, pas des détails
d'interface — mais l'article annonce la 5.2 : le pied de figure doit dire la
version réellement utilisée.
"""

import math
import os
import sys

import bpy
from mathutils import Vector

RACINE = os.path.dirname(os.path.abspath(__file__))

RESOLUTION = (900, 700)
ECHANTILLONS = 24

#  Le creux des bosses, en fraction du rayon.
AMPLITUDE = 0.045


# ---------------------------------------------------------------  la scène type

def nettoyer():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def monde(couleur):
    m = bpy.data.worlds.new("MONDE")
    m.use_nodes = True
    m.node_tree.nodes["Background"].inputs[0].default_value = (*couleur, 1.0)
    bpy.context.scene.world = m


def lampe(nom, position, cible, energie, taille=2.4):
    d = bpy.data.lights.new(nom, type='AREA')
    d.shape = 'SQUARE'
    d.size = taille
    d.energy = energie
    ob = bpy.data.objects.new(nom, d)
    ob.location = position
    #  Les surfaces lumineuses émettent vers leur -Z local : on les oriente par
    #  un suivi de cible, jamais à la main.
    ob.rotation_euler = (Vector(cible) - Vector(position)) \
        .to_track_quat('-Z', 'Y').to_euler()
    bpy.context.collection.objects.link(ob)


def camera(position, cible, focale=50.0):
    d = bpy.data.cameras.new("CAM")
    d.lens = focale
    ob = bpy.data.objects.new("CAM", d)
    ob.location = position
    ob.rotation_euler = (Vector(cible) - Vector(position)) \
        .to_track_quat('-Z', 'Y').to_euler()
    bpy.context.collection.objects.link(ob)
    bpy.context.scene.camera = ob


def sol(teinte=(0.170, 0.172, 0.180)):
    bpy.ops.mesh.primitive_plane_add(size=40.0, location=(0, 0, -1.02))
    p = bpy.context.object
    p.name = "Sol"
    m = bpy.data.materials.new("SOL")
    m.use_nodes = True
    n = m.node_tree.nodes["Principled BSDF"]
    n.inputs["Base Color"].default_value = (*teinte, 1.0)
    n.inputs["Roughness"].default_value = 0.85
    p.data.materials.append(m)


def matiere(nom="GRIS", base=(0.64, 0.65, 0.68), rugosite=0.42, metal=0.0):
    m = bpy.data.materials.new(nom)
    m.use_nodes = True
    n = m.node_tree.nodes["Principled BSDF"]
    n.inputs["Base Color"].default_value = (*base, 1.0)
    n.inputs["Roughness"].default_value = rugosite
    n.inputs["Metallic"].default_value = metal
    return m


def studio(force=1.0):
    """
    L'éclairage commun aux scènes qui en ont un.

    `force` existe pour la sphère : à pleine puissance sur un gris clair, la
    surface était brûlée et les bosses ne se lisaient plus — la silhouette
    trahissait le défaut, l'ombrage non. Or c'est l'ombrage le sujet.
    """
    lampe("CLE", (-3.4, -3.6, 3.4), (0, 0, 0), 900.0 * force)
    lampe("APPOINT", (3.8, -1.4, 1.8), (0, 0, 0), 180.0 * force, taille=3.0)


def reglages():
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_EEVEE_NEXT'
    sc.render.resolution_x, sc.render.resolution_y = RESOLUTION
    sc.render.image_settings.file_format = 'PNG'
    e = sc.eevee
    e.taa_render_samples = ECHANTILLONS
    #  Pas de lancer de rayons : sur cette machine sans carte graphique il
    #  multiplie le temps de calcul, et aucun des quatre symptômes n'en dépend.
    e.use_raytracing = False
    e.use_shadows = True
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - Base Contrast'


def rendre(nom):
    chemin = os.path.join(RACINE, "symptome-%s.png" % nom)
    bpy.context.scene.render.filepath = chemin
    bpy.ops.render.render(write_still=True)
    return chemin


# -----------------------------------------------------------------  la mesure

def pixels(chemin):
    from PIL import Image
    import numpy as np
    return np.asarray(Image.open(chemin).convert("RGB"), dtype=float) / 255.0


def luminance(a):
    return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]


def zone_sujet(lum):
    """Le rectangle central : mesurer le fond aussi fausserait tout."""
    h, l = lum.shape
    return lum[int(h * 0.18):int(h * 0.82), int(l * 0.28):int(l * 0.72)]


# -------------------------------------------------------------  les symptômes

def rose():
    """
    Une texture qui pointe vers un fichier absent.

    C'est Blender qui choisit le magenta, pas moi : `source = 'FILE'` sur un
    chemin qui n'existe pas suffit, le noeud renvoie (1, 0, 1), et la console
    affiche « Blender Texture Not Loaded ».
    """
    nettoyer()
    monde((0.035, 0.037, 0.042))
    sol()

    bpy.ops.mesh.primitive_cube_add(size=1.7, location=(0, 0, -0.15))
    cube = bpy.context.object
    cube.name = "Cube"
    cube.rotation_euler = (0.0, 0.0, math.radians(28.0))
    b = cube.modifiers.new("B", 'BEVEL')
    b.width, b.segments = 0.02, 2

    m = bpy.data.materials.new("CARRELAGE")
    m.use_nodes = True
    arbre = m.node_tree
    tex = arbre.nodes.new("ShaderNodeTexImage")
    tex.location = (-320, 260)
    img = bpy.data.images.new("carrelage.png", 16, 16)
    img.filepath = "//textures/carrelage.png"
    img.source = 'FILE'
    try:
        img.reload()          # le fichier n'existe pas : l'image passe cassée
    except RuntimeError:
        pass
    tex.image = img
    arbre.links.new(tex.outputs["Color"],
                    arbre.nodes["Principled BSDF"].inputs["Base Color"])
    cube.data.materials.append(m)

    studio()
    camera((0.0, -5.6, 2.3), (0.0, 0.0, -0.15), focale=50.0)
    reglages()
    chemin = rendre("rose")

    a = pixels(chemin)
    #  Le magenta de Blender : rouge et bleu forts, vert nettement en retrait.
    magenta = ((a[..., 0] > 0.45) & (a[..., 2] > 0.45)
               & (a[..., 1] < a[..., 0] * 0.55)).mean()
    print("    magenta sur %.1f %% de l'image" % (magenta * 100))
    if magenta < 0.05:
        raise SystemExit("la texture manquante ne rend pas rose")
    return chemin


def objet_noir():
    """
    Un Principled réglé sur Metallic 1, dans une scène sans environnement.

    Un métal n'a pas de couleur diffuse : il ne fait que refléter ce qui
    l'entoure. Dans un monde presque noir, il ne reste que le reflet des deux
    lampes, et tout le reste tombe au noir. Le curseur a été poussé une fois
    par curiosité, et l'objet ne revient plus.
    """
    nettoyer()
    monde((0.012, 0.013, 0.016))
    sol()

    bpy.ops.mesh.primitive_monkey_add(size=2.4, location=(0, 0, 0.15))
    singe = bpy.context.object
    singe.name = "Suzanne"
    singe.rotation_euler = (math.radians(6.0), 0.0, math.radians(26.0))
    for p in singe.data.polygons:
        p.use_smooth = True
    singe.data.materials.append(
        matiere("METAL", base=(0.58, 0.59, 0.62), rugosite=0.12, metal=1.0))

    #  UNE seule lampe, et petite. Le studio à deux grandes surfaces des autres
    #  scènes couvrait le métal de reflets larges et l'objet n'était noir que
    #  sur 0,5 % de sa surface — mesuré. Une scène de débutant n'a de toute
    #  façon qu'une lampe : celle du fichier de démarrage.
    lampe("LAMPE", (-2.6, -2.4, 3.0), (0, 0, 0), 300.0, taille=0.5)
    camera((0.0, -7.2, 1.7), (0.0, 0.0, 0.15), focale=55.0)
    reglages()
    chemin = rendre("objet-noir")

    #  LA BONNE MESURE N'EST PAS UN SEUIL, C'EST UN ÉCART. Compter les pixels
    #  sous 0,05 dépend de la part du cadre qu'occupe l'objet, et refusait un
    #  rendu pourtant parfait. Ce qu'on veut établir, c'est que L'OBJET est noir
    #  ALORS QUE la scène est éclairée : on compare donc les deux.
    import numpy as np
    lum = luminance(pixels(chemin))
    h, l = lum.shape
    sujet = float(np.median(zone_sujet(lum)))
    plancher = float(np.median(lum[int(h * 0.86):int(h * 0.98),
                                   int(l * 0.04):int(l * 0.28)]))
    print("    luminance médiane : sujet %.3f, sol éclairé %.3f"
          % (sujet, plancher))
    if sujet > 0.08:
        raise SystemExit("l'objet métallique n'est pas noir")
    if plancher < 0.15:
        raise SystemExit("toute la scène est sombre : on ne verrait pas que "
                         "c'est l'objet qui est noir")
    return chemin


def _sphere(nom, bosselee):
    """Une sphère lissée, cabossée ou non, dans le même studio."""
    nettoyer()
    monde((0.035, 0.037, 0.042))
    sol()

    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32,
                                         radius=1.2, location=(0, 0, 0.2))
    sph = bpy.context.object
    sph.name = "Sphere"

    if bosselee:
        #  Un déplacement radial calculé par une somme de sinus — déterministe,
        #  donc la figure est reproductible. Premier essai à 0,9 % du rayon et
        #  en basse fréquence : relief mesuré × 1,0, c'est-à-dire rien. Ce n'est
        #  pas l'amplitude qui fait l'ombrage, c'est la PENTE : à fréquence
        #  basse, la normale bouge à peine. D'où des sinus quatre fois plus
        #  serrés, et une amplitude relevée.
        for v in sph.data.vertices:
            x, y, z = v.co
            bruit = (0.6 * math.sin(8.3 * x + 1.7) * math.sin(7.1 * y + 0.4)
                     + 0.4 * math.sin(11.7 * z + 2.2) * math.sin(9.4 * x - 0.9))
            v.co = v.co * (1.0 + AMPLITUDE * bruit)
        sph.data.update()

    for p in sph.data.polygons:
        p.use_smooth = True
    sph.data.materials.append(matiere(base=(0.42, 0.43, 0.46), rugosite=0.38))

    studio(force=0.45)
    camera((0.0, -6.4, 1.5), (0.0, 0.0, 0.2), focale=55.0)
    reglages()
    return rendre(nom)


def _ecart(un, deux):
    """
    L'écart moyen entre deux rendus, dans la zone du sujet.

    PREMIÈRE MESURE, MAUVAISE : l'énergie de laplacien de chaque image prise
    séparément. Elle donnait × 1,0 sur des rendus pourtant très différents,
    parce qu'elle était dominée par le grain du calcul, présent partout et
    identique dans les deux cas.

    Les deux scènes ne diffèrent que par le maillage. Il suffit donc de les
    soustraire : ce qui reste est exactement l'effet des bosses, et rien
    d'autre.
    """
    import numpy as np
    a, b = zone_sujet(luminance(pixels(un))), zone_sujet(luminance(pixels(deux)))
    return float(np.abs(a - b).mean())


def sphere_cabossee():
    """
    Un maillage irrégulier, que le Shade Smooth met en pleine lumière.

    DEUX PISTES ABANDONNÉES, ET CE QU'ELLES APPRENNENT. J'ai d'abord dédoublé
    la géométrie — le Ctrl+D suivi d'un clic droit, la faute classique — en
    espérant un conflit de profondeur. Décalée d'un cheveu puis exactement
    superposée : 0,1 % de sauts de luminance dans les deux cas. EEVEE tranche
    de façon déterministe sur une image fixe, le conflit ne se voit pas.

    Ce qui produit vraiment le « ballon dégonflé », c'est un maillage qui n'est
    plus tout à fait sphérique — sommets déplacés à la main, édition
    proportionnelle, coup de sculpt. À plat, ça passe presque inaperçu. Le
    Shade Smooth interpole les normales sur toute la surface et transforme des
    irrégularités d'un demi-pour-cent en taches franches.

    Le déplacement fait ici moins de 1 % du rayon. La silhouette reste ronde :
    c'est bien l'ombrage qui parle, et c'est tout l'intérêt de la vignette.
    """
    controle = _sphere("controle-sphere-lisse", bosselee=False)
    chemin = _sphere("sphere-cabossee", bosselee=True)

    ecart = _ecart(controle, chemin)
    print("    écart moyen avec la sphère saine : %.4f  (%.1f niveaux sur 255)"
          % (ecart, ecart * 255))
    if ecart < 0.02:
        raise SystemExit("la sphère cabossée ne se distingue pas assez de la "
                         "sphère saine")
    return chemin


def rendu_noir():
    """
    Aucune lampe, et un monde noir.

    C'est le premier F12 de tout le monde : la scène a été montée en vue
    solide, où l'éclairage est simulé par la fenêtre elle-même, et le rendu
    révèle qu'il n'y a jamais eu la moindre source de lumière.
    """
    nettoyer()
    monde((0.0, 0.0, 0.0))
    sol()

    bpy.ops.mesh.primitive_monkey_add(size=2.4, location=(0, 0, 0.15))
    singe = bpy.context.object
    singe.name = "Suzanne"
    singe.rotation_euler = (math.radians(6.0), 0.0, math.radians(26.0))
    for p in singe.data.polygons:
        p.use_smooth = True
    singe.data.materials.append(matiere())

    camera((0.0, -7.2, 1.7), (0.0, 0.0, 0.15), focale=55.0)
    reglages()
    chemin = rendre("rendu-noir")

    a = pixels(chemin)
    maxi = luminance(a).max()
    print("    luminance maximale du rendu : %.4f" % maxi)
    if maxi > 0.02:
        raise SystemExit("le rendu n'est pas noir")
    return chemin


SYMPTOMES = (("rose", rose), ("objet-noir", objet_noir),
             ("sphere-cabossee", sphere_cabossee), ("rendu-noir", rendu_noir))


def main():
    voulus = [a for a in sys.argv[1:] if not a.startswith("-")]
    for nom, fonction in SYMPTOMES:
        if voulus and nom not in voulus:
            continue
        print("  %s" % nom)
        print("    -> %s" % os.path.basename(fonction()))


if __name__ == "__main__":
    main()
