"""
IMAGE 7 de l'article — la mesure du coût de la résolution et des surfels.

    python3 article/mesurer_bake.py            # la campagne complète
    python3 article/mesurer_bake.py --sonder   # deux points, pour l'échelle

Écrit `article/mesures-bake.json`, que `montage_bake.py` transforme en figure.

----------------------------------------------------------------------------
CE QU'ON MESURE, ET POURQUOI DEUX CHOSES À LA FOIS
----------------------------------------------------------------------------
La légende de l'image affirme que doubler la résolution multiplie le temps de
calcul « sans que le rendu suive vraiment ». C'est une affirmation à deux
membres, et on ne peut pas en tenir un sans l'autre :

  - LE COÛT. Le temps de cuisson, chronométré autour de l'opérateur.
  - LE GAIN. De combien l'image finale change réellement. Sans cette
    deuxième mesure, « le rendu ne suit pas » n'est qu'une impression.

Le gain se mesure contre le réglage le plus cher de la campagne, pris comme
référence. Pour chaque réglage on rend la même image et on la compare à cette
référence : écart moyen sur 255, et part des pixels qui s'en écartent d'au
moins DEUX niveaux — le seuil en deçà duquel personne ne voit rien sur un
écran ordinaire.

----------------------------------------------------------------------------
LE PLANCHER DE BRUIT, SANS LEQUEL AUCUN ÉCART N'A DE SENS
----------------------------------------------------------------------------
Une cuisson n'est pas déterministe : elle échantillonne au hasard. Deux
cuissons du MÊME réglage ne donnent donc pas exactement la même image.

Si on ne mesure pas cet écart-là, on ne sait pas lire les autres. Un réglage
qui s'écarte de la référence de 0,4/255 est-il « moins bon » ? Pas si deux
cuissons identiques s'écartent déjà de 0,4 entre elles : il est alors
indiscernable de la référence, et tout ce qu'on a payé en plus, on l'a payé
pour rien.

La campagne cuit donc DEUX FOIS le réglage de l'article, et le plancher ainsi
obtenu est écrit sur la figure à côté des écarts.
"""

import json
import os
import sys
import time

sys.argv = [sys.argv[0]]          # neutraliser les drapeaux avant l'import :
                                  # le module de scène lit sys.argv au chargement
import bpy                                                    # noqa: E402
import light_probes_eevee_next as scene                       # noqa: E402

RACINE = os.path.dirname(os.path.abspath(__file__))
JOURNAL = os.path.join(RACINE, "mesures-bake.json")
RENDUS = os.path.join(RACINE, "mesures-bake")

SONDER = "--sonder" in os.environ.get("MESURE_ARGS", "")

#  Le rendu de comparaison : plus petit que celui de l'article, mais identique
#  d'un réglage à l'autre. Ce qu'on compare, c'est des images entre elles.
COMPARAISON = (960, 540)
ECHANTILLONS = 48

#  Doubler la résolution, c'est doubler CHAQUE ARÊTE : le nombre
#  d'échantillons est donc multiplié par huit à chaque palier, pas par deux.
#  C'est déjà la moitié de ce que dit la légende, et ça se voit sur la courbe.
SERIE_RESOLUTION = [(3, 3, 2), (6, 6, 3), (11, 12, 6), (22, 24, 12)]
SURFEL_FIXE = 28

#  60 est DANS la liste alors qu'il échoue, et c'est volontaire : le mur se
#  mesure, il ne se contourne pas. Voir `cuire()`.
SERIE_SURFEL = [5, 10, 20, 40, 50, 60]
RES_FIXE = (11, 12, 6)

REFERENCE = ((22, 24, 12), 50)
BAKE_SAMPLES = 1024               # fixe partout : une variable à la fois


def cuire(p, resolution, surfels):
    """
    Cuisson chronométrée.

    On VIDE le cache d'abord — sans ça, Blender garderait la cuisson
    précédente et on mesurerait un temps de zéro.

    UN ÉCHEC EST UNE MESURE, PAS UN ACCIDENT. Au-delà d'une certaine densité
    de surfels la cuisson est refusée faute de mémoire vidéo. Le script ne
    s'arrête pas là-dessus : il note ce qui a été demandé et continue. Une
    campagne qui ne garderait que les réglages ayant réussi laisserait croire
    que le coût monte doucement jusqu'à l'infini.
    """
    p.data.resolution_x, p.data.resolution_y, p.data.resolution_z = resolution
    p.data.surfel_density = surfels
    p.data.bake_samples = BAKE_SAMPLES
    bpy.context.view_layer.objects.active = p
    bpy.ops.object.lightprobe_cache_free(subset='ALL')
    t0 = time.perf_counter()
    try:
        bpy.ops.object.lightprobe_cache_bake(subset='ALL')
        return time.perf_counter() - t0, None
    except RuntimeError as e:
        return time.perf_counter() - t0, str(e).strip()


def rendre(chemin):
    sc = bpy.context.scene
    sc.render.filepath = chemin
    t0 = time.perf_counter()
    bpy.ops.render.render(write_still=True)
    return time.perf_counter() - t0


def ecart(a, b):
    """Écart entre deux rendus : moyenne sur 255, et part des pixels qui
    s'écartent d'au moins deux niveaux."""
    import numpy as np
    from PIL import Image
    x = np.asarray(Image.open(a).convert("RGB"), dtype=float)
    y = np.asarray(Image.open(b).convert("RGB"), dtype=float)
    d = np.abs(x - y)
    return float(d.mean()), float(100.0 * (d.mean(2) >= 2.0).mean())


def mes_par_nom(resultats, nom):
    return next((x for x in resultats if x["nom"] == nom), None)


def campagne():
    os.makedirs(RENDUS, exist_ok=True)
    p = scene.monter_la_scene()

    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = COMPARAISON
    sc.render.resolution_percentage = 100
    sc.eevee.taa_render_samples = ECHANTILLONS

    #  LE MUR QU'ON RENCONTRE AVANT CELUI DU TEMPS.
    #
    #  Premier essai de campagne, sur le réglage le plus fin :
    #
    #      Error: Not enough available video memory to bake
    #      "OBVOLUME_PROBE" (67 / 30 MBytes)
    #
    #  J'ai d'abord accusé la réserve d'irradiance de la scène, laissée à
    #  32 Mo. C'était faux, et le vérifier a pris trois lignes : en la portant
    #  à 512 Mo, le message reste identique au mégaoctet près. Les 30 Mo sont
    #  la mémoire vidéo réellement disponible sur cette machine, pas un
    #  réglage de Blender.
    #
    #  La vraie variable, isolée en faisant varier une chose à la fois :
    #
    #      11 × 12 ×  6, surfels 80  ->  67 Mo demandés  ->  ÉCHEC
    #      22 × 24 × 12, surfels 28  ->  passe
    #
    #  Le même besoin de 67 Mo pour la plus petite grille que pour la plus
    #  grande : ce n'est donc pas la résolution du volume qui remplit la
    #  mémoire, C'EST LA DENSITÉ DE SURFELS.
    #
    #  J'ai cru un moment que le message égarait, parce qu'il nomme l'objet
    #  sonde. Relu en entier, il ne s'agit pas de ça — il désigne le bon
    #  coupable, en toutes lettres :
    #
    #      Not enough available video memory to bake "OBVOLUME_PROBE"
    #      (38 / 30 MBytes). Try reducing surfel resolution or capture
    #      distance to lower the size of the allocation
    #
    #  C'est moi qui l'avais tronqué en le filtrant. Une leçon qui vaut le
    #  détour : lire le message en entier avant d'accuser le message.
    #
    #  On laisse quand même la réserve au large : elle ne coûte rien et elle
    #  écarte une variable de la mesure.
    sc.eevee.gi_irradiance_pool_size = '512'

    plan = []
    if SONDER:
        plan = [("sonde-basse", (3, 3, 2), SURFEL_FIXE),
                ("sonde-haute", REFERENCE[0], REFERENCE[1])]
    else:
        plan.append(("reference", REFERENCE[0], REFERENCE[1]))
        for r in SERIE_RESOLUTION:
            plan.append(("resolution-%dx%dx%d" % r, r, SURFEL_FIXE))
        for s in SERIE_SURFEL:
            plan.append(("surfel-%d" % s, RES_FIXE, s))
        #  La même cuisson, une seconde fois : c'est le plancher de bruit.
        plan.append(("plancher", RES_FIXE, SURFEL_FIXE))

    resultats = []
    for i, (nom, r, s) in enumerate(plan, 1):
        chemin = os.path.join(RENDUS, nom + ".png")
        tb, echec = cuire(p, r, s)
        e = {"nom": nom, "resolution": list(r), "surfels": s,
             "echantillons": r[0] * r[1] * r[2],
             "cuisson_s": round(tb, 3), "echec": echec}
        if echec is None:
            e["rendu_s"] = round(rendre(chemin), 3)
            e["image"] = os.path.relpath(chemin, RACINE)
        resultats.append(e)
        print("  [%d/%d] %-22s %2dx%2dx%2d  surfels %2d  %s"
              % (i, len(plan), nom, r[0], r[1], r[2], s,
                 ("cuisson %7.2f s" % tb) if echec is None
                 else ("ECHEC : " + echec.split("bake")[-1].strip())))
        sys.stdout.flush()

    #  Les écarts, une fois tous les rendus faits.
    ref = next((x for x in resultats
                if x["nom"] == "reference" and x.get("image")), None)
    if ref is None:
        raise SystemExit("la reference n'a pas cuit : tout le reste est sans "
                         "point de comparaison")
    for e in resultats:
        if not e.get("image"):
            continue
        m, pc = ecart(os.path.join(RACINE, e["image"]),
                      os.path.join(RACINE, ref["image"]))
        e["ecart_moyen"] = round(m, 3)
        e["pixels_visibles_pc"] = round(pc, 2)

    #  LE PLANCHER SE MESURE ENTRE LES DEUX CUISSONS, PAS PAR SOUSTRACTION.
    #  Chaque réglage porte son écart À LA RÉFÉRENCE. J'avais d'abord pris la
    #  différence de ces deux écarts — |A−R| moins |B−R| — ce qui ne vaut
    #  rien : deux images peuvent être à la même distance de la référence et
    #  très loin l'une de l'autre. On compare donc A et B directement.
    plancher_direct = None
    a = mes_par_nom(resultats, "resolution-%dx%dx%d" % RES_FIXE)
    b = mes_par_nom(resultats, "plancher")
    if a and b and a.get("image") and b.get("image"):
        m, pc = ecart(os.path.join(RACINE, a["image"]),
                      os.path.join(RACINE, b["image"]))
        plancher_direct = {"ecart_moyen": round(m, 3),
                           "pixels_visibles_pc": round(pc, 2)}
        print("  plancher de bruit (deux cuissons identiques) : "
              "%.3f/255,  %.2f %% de pixels" % (m, pc))

    #  CHAQUE SÉRIE SE COMPARE À SON PROPRE SOMMET, pas à la référence
    #  globale. Sinon les deux réglages se contaminent : dans la série des
    #  surfels, tous les rendus sont en 11 × 12 × 6 alors que la référence est
    #  en 22 × 24 × 12, et l'écart mesuré contient donc surtout un écart de
    #  RÉSOLUTION. On lirait « les surfels ne descendent jamais sous 14 » là
    #  où ce 14, ce sont les surfels qui n'y sont pour rien.
    for prefixe, sommet in (("resolution-", "resolution-%dx%dx%d"
                             % SERIE_RESOLUTION[-1]),
                            ("surfel-", "surfel-%d" % SERIE_SURFEL[-2])):
        haut = mes_par_nom(resultats, sommet)
        if not (haut and haut.get("image")):
            continue
        for e in resultats:
            if not e["nom"].startswith(prefixe) or not e.get("image"):
                continue
            m, pc = ecart(os.path.join(RACINE, e["image"]),
                          os.path.join(RACINE, haut["image"]))
            e["ecart_serie"] = round(m, 3)
            e["pixels_serie_pc"] = round(pc, 2)
            e["sommet_de_serie"] = sommet

    donnees = {"comparaison": list(COMPARAISON),
               "plancher_direct": plancher_direct,
               "echantillons_rendu": ECHANTILLONS,
               "bake_samples": BAKE_SAMPLES,
               "reference": {"resolution": list(REFERENCE[0]),
                             "surfels": REFERENCE[1]},
               "mesures": resultats}
    with open(JOURNAL, "w") as f:
        json.dump(donnees, f, indent=2)
    print()
    print("  -> %s" % JOURNAL)


if __name__ == "__main__":
    campagne()
