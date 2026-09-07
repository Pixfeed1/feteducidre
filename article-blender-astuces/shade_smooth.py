"""
Les trois états de la sphère, avec leur maillage visible.

    python3 article-blender-astuces/shade_smooth.py

Produit `ss-1-flat.png`, `ss-2-smooth.png`, `ss-3-subdiv.png` et
`ss-comptes.json`.

----------------------------------------------------------------------------
POURQUOI PAS UN ENREGISTREMENT D'ÉCRAN, QUI ÉTAIT AU BRIEF
----------------------------------------------------------------------------
Il n'y a pas d'interface graphique dans cet environnement : Blender y tourne
en module Python, sans fenêtre. Aucun ScreenToGif, aucun OBS.

Mais l'enregistrement d'écran n'était pas le bon outil de toute façon. Le
propos de la section est que « Shade Smooth n'ajoute aucune géométrie ». Une
vidéo d'un clic droit dans un menu ne le montre pas : on y voit une sphère
qui devient lisse, ce qui donne plutôt l'impression du contraire.

Ce qui le montre, c'est LE MAILLAGE. Les trois états sont donc rendus avec
leur fil de fer par-dessus, et le nombre de faces écrit à côté. On voit alors
la seule chose qui compte : entre le premier et le deuxième état, le fil de fer
est identique au trait près. Entre le deuxième et le troisième, il se remplit.

----------------------------------------------------------------------------
LE FIL DE FER EST DE LA VRAIE GÉOMÉTRIE
----------------------------------------------------------------------------
Pas un post-traitement : une copie de l'objet portant un modificateur
Wireframe, qui transforme chaque arête en tube. Elle subit les mêmes
modificateurs que l'original — donc au troisième état, le fil de fer est celui
de la surface subdivisée, pas celui de la cage.

La copie est mise à l'échelle de 1,002 pour que les tubes affleurent la
surface au lieu de se battre avec elle en profondeur.

----------------------------------------------------------------------------
LES COMPTES SONT LUS, PAS ÉCRITS
----------------------------------------------------------------------------
Le nombre de faces de chaque état est relevé sur le maillage évalué, après
modificateurs, et écrit dans `ss-comptes.json`. L'animation les affiche tels
quels. Écrire « 8 192 » à la main dans une légende serait une occasion de se
tromper pour rien.
"""

import json
import math
import os

import bpy

import symptomes as S

RACINE = os.path.dirname(os.path.abspath(__file__))
COMPTES = os.path.join(RACINE, "ss-comptes.json")

#  La sphère par défaut de Blender : 32 segments, 16 anneaux.
SEGMENTS, ANNEAUX = 32, 16
NIVEAU = 2                      # ce que fait Ctrl+2


def faces_evaluees(ob):
    """Le nombre de faces APRÈS modificateurs, lu sur le maillage évalué."""
    dep = bpy.context.evaluated_depsgraph_get()
    return len(ob.evaluated_get(dep).to_mesh().polygons)


def scene(lisse, subdiv):
    S.nettoyer()
    S.monde((0.035, 0.037, 0.042))
    S.sol()

    bpy.ops.mesh.primitive_uv_sphere_add(segments=SEGMENTS,
                                         ring_count=ANNEAUX,
                                         radius=1.2, location=(0, 0, 0.2))
    sph = bpy.context.object
    sph.name = "Sphere"
    for p in sph.data.polygons:
        p.use_smooth = lisse
    if subdiv:
        m = sph.modifiers.new("Subdivision", 'SUBSURF')
        m.levels = m.render_levels = NIVEAU
    sph.data.materials.append(
        S.matiere(base=(0.46, 0.47, 0.50), rugosite=0.38))

    #  LA COPIE EN FIL DE FER. Mêmes modificateurs, donc même géométrie que ce
    #  qu'on voit : c'est toute la démonstration.
    fil = sph.copy()
    fil.data = sph.data.copy()
    fil.name = "Fil"
    fil.modifiers.clear()
    if subdiv:
        m = fil.modifiers.new("Subdivision", 'SUBSURF')
        m.levels = m.render_levels = NIVEAU
    w = fil.modifiers.new("Wireframe", 'WIREFRAME')
    w.thickness = 0.0075
    w.use_replace = True
    fil.scale = (1.002, 1.002, 1.002)
    fil.data.materials.clear()
    encre = S.matiere("FIL", base=(0.015, 0.016, 0.020), rugosite=0.65)
    fil.data.materials.append(encre)
    bpy.context.collection.objects.link(fil)

    S.studio(force=0.55)
    S.camera((0.0, -6.4, 1.5), (0.0, 0.0, 0.2), focale=55.0)
    S.reglages()
    return sph


def rendre(nom):
    chemin = os.path.join(RACINE, "%s.png" % nom)
    bpy.context.scene.render.filepath = chemin
    bpy.ops.render.render(write_still=True)
    return chemin


def main():
    etats = (("ss-1-flat", False, False),
             ("ss-2-smooth", True, False),
             ("ss-3-subdiv", True, True))
    comptes, coins = {}, 0
    for nom, lisse, subdiv in etats:
        sph = scene(lisse, subdiv)
        comptes[nom] = faces_evaluees(sph)
        if not subdiv:
            #  Le nombre de coins du maillage de départ : c'est lui qui donne
            #  le compte après le premier niveau de subdivision.
            coins = sum(len(p.vertices) for p in sph.data.polygons)
        rendre(nom)
        print("  %-14s %6d faces  -> %s.png" % (nom, comptes[nom], nom))

    #  Le contrôle qui donne son sens à toute la figure : les deux premiers
    #  états DOIVENT avoir le même nombre de faces, le troisième non.
    if comptes["ss-1-flat"] != comptes["ss-2-smooth"]:
        raise SystemExit("Shade Smooth aurait changé la géométrie : %d puis %d"
                         % (comptes["ss-1-flat"], comptes["ss-2-smooth"]))
    #  L'ATTENDU N'EST PAS × 4 PAR NIVEAU, et le contrôle me l'a appris en
    #  refusant un rendu pourtant juste. Catmull-Clark découpe une face de n
    #  côtés en n quads, pas en quatre : une UV sphere a des TRIANGLES aux deux
    #  pôles, donc 448 quads et 64 triangles. Le premier niveau donne
    #  448 × 4 + 64 × 3 = 1 984 faces, et non 2 048. Les niveaux suivants, eux,
    #  quadruplent bien, puisque tout est devenu quadrangulaire.
    attendu = coins * (4 ** (NIVEAU - 1))
    if comptes["ss-3-subdiv"] != attendu:
        raise SystemExit("la subdivision de niveau %d devrait donner %d faces, "
                         "elle en donne %d"
                         % (NIVEAU, attendu, comptes["ss-3-subdiv"]))
    print("  contrôle : %d = %d faces après Shade Smooth, puis %d après "
          "Subdivision niveau %d"
          % (comptes["ss-1-flat"], comptes["ss-2-smooth"],
             comptes["ss-3-subdiv"], NIVEAU))

    with open(COMPTES, "w", encoding="utf-8") as f:
        json.dump(comptes, f, indent=2)


if __name__ == "__main__":
    main()
