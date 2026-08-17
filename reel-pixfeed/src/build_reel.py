"""
Étape 3 — la construction.

    blender -b template.blend -P src/build_reel.py -- projets/tenakoe.json

Le script ne CRÉE pas la scène : il ouvre le modèle et le remplit. Il
remplace les deux images, redimensionne les deux écrans au rapport réel des
captures, écrit les textes, pose les clés, vérifie la zone sûre, puis rend la
séquence d'images.

Options après le nom du projet :
    --image N        ne rend qu'une seule image (contrôle de cadrage)
    --images A,B,C   rend seulement ces images-là
    --pas-de-rendu   construit et vérifie seulement
    --sortie CHEMIN  dossier de sortie des images
"""

import os
import sys
import math
import json

import bpy

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "src"))
import grammar as G                                            # noqa: E402
import config as C                                             # noqa: E402


def srgb(c):
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4
                 for x in c)


def s(secondes):
    """secondes -> images"""
    return secondes * G.IMAGES_PAR_SECONDE


O = bpy.data.objects


# ===========================================================================
#  REMPLISSAGE
# ===========================================================================

def poser_images(journal, slug):
    """
    Remplace l'image du nœud « TEX » de chaque matériau d'écran, et remet
    chaque plan au rapport EXACT de sa capture.

    Un plan laissé au rapport du modèle écraserait ou étirerait la capture :
    le site du client apparaîtrait déformé, ce qui est le seul défaut
    réellement impardonnable dans un avant/après.
    """
    dossier = os.path.join(RACINE, "out", slug)
    tailles = {}
    for cle, mat_nom, ob_nom in (("avant", "MAT_SCREEN_BEFORE",
                                  "SCREEN_BEFORE"),
                                 ("apres", "MAT_SCREEN_AFTER",
                                  "SCREEN_AFTER")):
        chemin = os.path.join(dossier, journal["pages"][cle]["fichier"])
        img = bpy.data.images.load(chemin, check_existing=True)
        img.colorspace_settings.name = "sRGB"
        #  sRGB et non « Non-Color » : une capture d'écran EST une image
        #  sRGB. En Non-Color, Blender la traiterait comme des données
        #  linéaires et tout ressortirait beaucoup trop clair.
        mat = bpy.data.materials[mat_nom]
        tex = mat.node_tree.nodes["TEX"]
        tex.image = img

        lp, hp = img.size
        hauteur = G.ECRAN_LARGEUR * hp / float(lp)
        ob = O[ob_nom]
        #  On remet le maillage au bon rapport plutôt que de mettre l'objet
        #  à l'échelle : l'échelle d'objet sert à l'animation, la mélanger à
        #  la mise en page rend les clés illisibles.
        hw, hh = G.ECRAN_LARGEUR / 2.0, hauteur / 2.0
        for v, co in zip(ob.data.vertices,
                         [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]):
            v.co.x, v.co.y = co
        ob.data.update()
        tailles[cle] = hauteur
        print("  %-6s texture %d × %d  ->  plan %.2f × %.2f unités"
              % (cle, lp, hp, G.ECRAN_LARGEUR, hauteur))
    return tailles


def ajuster(ob, texte, largeur_max, couleur):
    """
    Écrit le texte puis RÉDUIT la taille si la ligne la plus large dépasse.

    On mesure la largeur réellement obtenue au lieu de la deviner au nombre
    de caractères : « MMMMM » et « iiiii » ont le même compte et pas du tout
    la même largeur. C'est ce qui garantit qu'aucun texte ne sort de la zone
    sûre, quel que soit le client.
    """
    cu = ob.data
    cu.body = texte
    bpy.context.view_layer.update()
    largeur = ob.dimensions.x
    if largeur > largeur_max > 0:
        cu.size *= largeur_max / largeur
        bpy.context.view_layer.update()
    #  La couleur d'objet est transmise TELLE QUELLE au nuanceur, qui
    #  travaille en linéaire. Y écrire directement la valeur sRGB de la
    #  charte délavait tout : le violet #9442FA sortait en lavande et le
    #  bandeau, censé assombrir, ÉCLAIRCISSAIT le fond. Mesuré : 24 au lieu
    #  de 6 sur 255. D'où la conversion, ici et nulle part ailleurs.
    ob.color = (*srgb(couleur), 0.0)
    return ob.dimensions.y


def remplir_textes(cfg):
    """Chaque objet texte reçoit son contenu, sa coupe et sa couleur."""
    t = {}
    t["TXT_CLIENT"] = ajuster(O["TXT_CLIENT"], cfg["client_affiche"],
                              G.TEXTE_LARGEUR, G.COUL_CLIENT)
    t["TXT_SECTEUR"] = ajuster(O["TXT_SECTEUR"], cfg["secteur_affiche"],
                               G.TEXTE_LARGEUR, G.COUL_SECTEUR)
    t["TXT_ANNEE"] = ajuster(O["TXT_ANNEE"], str(cfg["annee"]),
                             G.TEXTE_LARGEUR, G.COUL_ANNEE)
    t["TXT_HOOK"] = ajuster(O["TXT_HOOK"],
                            C.couper(cfg["hook"], G.COUPE_HOOK),
                            G.TEXTE_LARGEUR, G.COUL_HOOK)
    for i in range(3):
        t["TXT_A%d" % (i + 1)] = ajuster(
            O["TXT_A%d" % (i + 1)],
            C.couper(cfg["avant"][i], G.COUPE_POINT),
            G.TEXTE_LARGEUR, G.COUL_AVANT)
        t["TXT_B%d" % (i + 1)] = ajuster(
            O["TXT_B%d" % (i + 1)],
            C.couper(cfg["apres"][i], G.COUPE_POINT),
            G.TEXTE_LARGEUR, G.COUL_APRES)
    t["TXT_NUM"] = ajuster(O["TXT_NUM"], cfg["chiffre"]["valeur"],
                           G.TEXTE_LARGEUR, G.COUL_NUM)
    t["TXT_NUM_LEG"] = ajuster(O["TXT_NUM_LEG"], cfg["chiffre"]["legende"],
                               G.TEXTE_LARGEUR, G.COUL_NUM_LEG)
    t["TXT_SORTIE"] = ajuster(O["TXT_SORTIE"],
                              C.couper(cfg["sortie"], G.COUPE_SORTIE),
                              G.TEXTE_LARGEUR, G.COUL_SORTIE)
    t["TXT_CTA"] = ajuster(O["TXT_CTA"], C.couper(cfg["cta"], G.COUPE_CTA),
                           G.TEXTE_LARGEUR, G.COUL_CTA)

    #  Mise en place verticale
    for nom, y in (("TXT_CLIENT", G.OUV_CLIENT_Y),
                   ("TXT_SECTEUR", G.OUV_SECTEUR_Y),
                   ("TXT_ANNEE", G.OUV_ANNEE_Y),
                   ("TXT_HOOK", G.HOOK_Y),
                   ("TXT_NUM", G.NUM_Y),
                   ("TXT_NUM_LEG", G.NUM_LEG_Y),
                   ("TXT_SORTIE", G.SORTIE_Y),
                   ("TXT_CTA", G.CTA_Y)):
        O[nom].location = (0.0, y, G.Z_TEXTE)
    for i in range(3):
        O["TXT_A%d" % (i + 1)].location = (0.0, G.INCRUST_Y, G.Z_TEXTE)
        O["TXT_B%d" % (i + 1)].location = (0.0, G.INCRUST_Y, G.Z_TEXTE)
    O["LOGO"].color = (*srgb(G.COUL_LOGO), 0.0)
    O["DEVICE"].data.materials[0] = bpy.data.materials["MAT_APPAREIL"]
    return t


# ===========================================================================
#  LES CLÉS
# ===========================================================================

def cle(ob, prop, image, valeur, interp="BEZIER", easing="AUTO", index=-1):
    if prop == "color":
        ob.color = valeur
    elif prop == "location":
        ob.location = valeur
    elif prop == "scale":
        ob.scale = valeur
    elif prop == "rotation_euler":
        ob.rotation_euler = valeur
    ob.keyframe_insert(prop, frame=int(round(image)), index=index)
    act = ob.animation_data.action
    for fc in act.fcurves:
        if fc.data_path != prop:
            continue
        if index >= 0 and fc.array_index != index:
            continue
        for kp in fc.keyframe_points:
            if abs(kp.co.x - round(image)) < 0.5:
                kp.interpolation = interp
                kp.easing = easing


def alpha(ob, image, valeur, interp="SINE", easing="EASE_OUT"):
    """N'anime QUE la composante alpha de la couleur d'objet : la teinte
    reste celle posée au remplissage."""
    c = list(ob.color)
    c[3] = valeur
    ob.color = c
    ob.keyframe_insert("color", frame=int(round(image)), index=3)
    for fc in ob.animation_data.action.fcurves:
        if fc.data_path == "color" and fc.array_index == 3:
            for kp in fc.keyframe_points:
                if abs(kp.co.x - round(image)) < 0.5:
                    kp.interpolation = interp
                    kp.easing = easing


def apparaitre(ob, debut, fin, y_repos, duree=None):
    """
    L'incrustation : translation verticale courte PLUS fondu, sur six
    images. Jamais de rotation, jamais de rebond — la capture derrière bouge
    déjà, deux mouvements concurrents se mangent l'un l'autre.
    """
    d = duree or G.INCRUST_ENTREE
    cle(ob, "location", debut, (0.0, y_repos - G.INCRUST_MONTEE, G.Z_TEXTE),
        "SINE", "EASE_OUT")
    cle(ob, "location", debut + d, (0.0, y_repos, G.Z_TEXTE),
        "SINE", "EASE_OUT")
    alpha(ob, debut, 0.0)
    alpha(ob, debut + d, 1.0)
    alpha(ob, fin - d, 1.0)
    alpha(ob, fin, 0.0, "SINE", "EASE_IN")


def defilement(ob, hauteur_plan, debut, fin):
    """
    LE DÉFILEMENT — la règle d'honnêteté du format.

    La vitesse est fixée en HAUTEURS D'ÉCRAN PAR SECONDE et ne dépend donc
    jamais de la longueur de la page. Une page courte est parcourue puis
    maintenue ; une page longue n'est pas parcourue en entier. On
    n'accélère JAMAIS pour « remplir » le temps disponible : deux sites
    comparés à deux vitesses différentes, ça se voit et ça ment.

    Le corps du mouvement est LINÉAIRE. Seules les 0,3 s de chaque
    extrémité sont adoucies : un défilement entièrement lissé donne une
    impression de flottement.

    La longueur des amorces est calculée, pas devinée. Blender adoucit en
    sinus : sur une amorce de durée a atteignant la vitesse v, la courbe
    1-cos(πx/2) a une pente finale de π/2, la distance parcourue vaut donc
    2·v·a/π et non v·a/2.
    """
    A = G.ECRAN_HAUTEUR
    D = max(0.0, hauteur_plan - A)             # course totale possible
    y0 = (A - hauteur_plan) / 2.0              # haut de page en haut d'écran
    v = G.VITESSE_DEFILEMENT * A               # LA vitesse de croisière, u/s
    a = G.DEFILEMENT_AMORCE_S
    t = (fin - debut) / float(G.IMAGES_PAR_SECONDE)
    marge = 2.0 * v * a / math.pi              # distance d'UNE amorce

    if D <= 1e-6:
        cle(ob, "location", debut, (0.0, y0, 0.0), "LINEAR")
        cle(ob, "location", fin, (0.0, y0, 0.0), "LINEAR")
        return {"course": 0.0, "duree": t, "croisiere": None,
                "palier": False}

    d_max = v * (t - 2 * a) + 2 * marge        # course faisable dans le temps
    if D <= d_max:
        course, t_lin = D, (D - 2 * marge) / v
    else:
        course, t_lin = d_max, t - 2 * a

    if t_lin <= 0.0:
        #  Page si courte que les deux amorces suffisent : elles se
        #  rejoignent, il n'y a pas de palier. On dimensionne la durée pour
        #  que la vitesse de POINTE reste v — sinon ce plan-là filerait plus
        #  vite que l'autre, et la comparaison serait faussée.
        demi = math.pi * course / (4.0 * v)
        cle(ob, "location", debut, (0.0, y0, 0.0), "SINE", "EASE_IN")
        cle(ob, "location", debut + s(demi), (0.0, y0 + course / 2.0, 0.0),
            "SINE", "EASE_OUT")
        cle(ob, "location", debut + s(2 * demi), (0.0, y0 + course, 0.0),
            "LINEAR")
        cle(ob, "location", fin, (0.0, y0 + course, 0.0), "LINEAR")
        return {"course": course / A, "duree": 2 * demi, "croisiere": v / A,
                "palier": False}

    ya, yb = y0 + marge, y0 + course - marge
    fa, fb = debut + s(a), debut + s(a + t_lin)
    cle(ob, "location", debut, (0.0, y0, 0.0), "SINE", "EASE_IN")
    cle(ob, "location", fa, (0.0, ya, 0.0), "LINEAR")
    cle(ob, "location", fb, (0.0, yb, 0.0), "SINE", "EASE_OUT")
    cle(ob, "location", fb + s(a), (0.0, y0 + course, 0.0), "LINEAR")
    if fb + s(a) < fin:                        # puis on MAINTIENT
        cle(ob, "location", fin, (0.0, y0 + course, 0.0), "LINEAR")

    #  La vitesse de croisière est RELEVÉE sur les clés réellement posées,
    #  pas recopiée depuis la consigne : c'est la seule mesure qui prouve
    #  que les deux défilements avancent au même rythme.
    croisiere = (yb - ya) / ((fb - fa) / float(G.IMAGES_PAR_SECONDE)) / A
    return {"course": course / A, "duree": 2 * a + t_lin,
            "croisiere": croisiere, "palier": True}


def voile_pour(hauteur_texte):
    """Le bandeau s'ajuste à la hauteur du texte qu'il porte."""
    return max(1.0, (hauteur_texte + 0.55) / G.INCRUST_BANDE_HAUT)


def animer(cfg, tailles, hauteurs_txt):
    T = G.TEMPS
    pivot, dev = O["PIVOT"], O["DEVICE"]
    voile = O["VOILE_INCRUST"]
    f0, f9 = G.IMAGE_PREMIERE, G.IMAGE_DERNIERE
    rapport = {}

    # -- l'appareil : absent aux deux cartons, présent au milieu -----------
    ouv0, ouv1 = T["ouverture"]
    sor0, sor1 = T["sortie"]
    bou0, _ = T["boucle"]
    for ob in (pivot, dev):
        cle(ob, "scale", f0, (0.0, 0.0, 0.0), "SINE", "EASE_IN_OUT")
        cle(ob, "scale", ouv1 - 3, (0.0, 0.0, 0.0), "SINE", "EASE_OUT")
        cle(ob, "scale", ouv1 + 9, (1.0, 1.0, 1.0), "SINE", "EASE_OUT")
        #  RESPIRATION : rien n'est jamais totalement immobile. 2 % sur
        #  toute la traversée, invisible consciemment, mais l'œil décroche
        #  sans elle.
        cle(ob, "scale", sor0 - 2,
            (1 + G.RESPIRATION,) * 3, "SINE", "EASE_IN_OUT")
        cle(ob, "scale", sor0 + 12, (0.0, 0.0, 0.0), "SINE", "EASE_IN")
        cle(ob, "scale", f9, (0.0, 0.0, 0.0), "LINEAR")

    # -- la bascule --------------------------------------------------------
    bas0, bas1 = T["bascule"]
    #  EASE_IN_OUT et non EASE_IN : une bascule qui démarre lentement mais
    #  s'arrête net a l'air de heurter un mur.
    cle(pivot, "rotation_euler", bas0, (0.0, 0.0, 0.0), "SINE",
        "EASE_IN_OUT")
    cle(pivot, "rotation_euler", bas1, (0.0, math.pi, 0.0), "SINE",
        "EASE_IN_OUT")
    #  Un gonflement à mi-parcours. Sous projection orthographique un recul
    #  en profondeur ne se voit pas : l'échelle est le seul levier.
    mi = (bas0 + bas1) / 2.0
    for ob in (pivot, dev):
        cle(ob, "scale", bas0,
            (1 + G.RESPIRATION * G.BASCULE_RESPIRATION[0],) * 3,
            "SINE", "EASE_IN_OUT")
        cle(ob, "scale", mi, (G.BASCULE_ECHELLE,) * 3, "SINE", "EASE_IN_OUT")
        cle(ob, "scale", bas1,
            (1 + G.RESPIRATION * G.BASCULE_RESPIRATION[1],) * 3,
            "SINE", "EASE_IN_OUT")

    # -- les deux défilements ---------------------------------------------
    av0, av1 = T["avant"]
    ap0, ap1 = T["apres"]
    #  L'avant est immobile pendant l'accroche, puis défile.
    cle(O["SCREEN_BEFORE"], "location", f0,
        (0.0, (G.ECRAN_HAUTEUR - tailles["avant"]) / 2.0, 0.0), "LINEAR")
    rapport["avant"] = defilement(O["SCREEN_BEFORE"], tailles["avant"],
                                  av0, bas0)
    #  L'après est déjà en haut de page pendant la bascule, puis défile.
    cle(O["SCREEN_AFTER"], "location", f0,
        (0.0, (G.ECRAN_HAUTEUR - tailles["apres"]) / 2.0, 0.0), "LINEAR")
    rapport["apres"] = defilement(O["SCREEN_AFTER"], tailles["apres"],
                                  ap0, sor0)

    # -- le carton d'ouverture, et son retour en fin de boucle -------------
    #  ATTENTION : il faut une clé de position DÈS L'IMAGE 0.
    #  Sans elle, Blender maintient la valeur de la première clé posée —
    #  celle de la remontée finale, 22 px plus bas — et le carton
    #  d'ouverture démarrait décalé vers le bas au premier tour de boucle.
    for nom in ("TXT_CLIENT", "TXT_SECTEUR", "TXT_ANNEE"):
        ob = O[nom]
        y = ob.location.y
        cle(ob, "location", f0, (0.0, y, G.Z_TEXTE), "LINEAR")
        cle(ob, "location", ouv1 + 2, (0.0, y, G.Z_TEXTE), "LINEAR")
        alpha(ob, f0, 1.0)
        alpha(ob, ouv1 - 4, 1.0)
        alpha(ob, ouv1 + 2, 0.0, "SINE", "EASE_IN")
        alpha(ob, bou0, 0.0)
        cle(ob, "location", bou0, (0.0, y - G.INCRUST_MONTEE, G.Z_TEXTE),
            "SINE", "EASE_OUT")
        cle(ob, "location", bou0 + 8, (0.0, y, G.Z_TEXTE),
            "SINE", "EASE_OUT")
        alpha(ob, bou0 + 8, 1.0)
        alpha(ob, f9, 1.0)

    # -- l'accroche --------------------------------------------------------
    hk0, hk1 = T["hook"]
    #  Elle s'efface AVANT la première incrustation : le cahier des charges
    #  impose une seule incrustation visible à la fois, et deux bandeaux
    #  superposés se disputaient leurs clés d'opacité.
    hook_d, hook_f = hk0 + 4, av0 - 2
    apparaitre(O["TXT_HOOK"], hook_d, hook_f, G.HOOK_Y)

    # -- les six incrustations, une seule visible à la fois ----------------
    bandes = []
    for cle_phase, prefixe, (p0, p1) in (("avant", "TXT_A", (av0, bas0)),
                                         ("apres", "TXT_B", (ap0, sor0))):
        pas = (p1 - p0) / 3.0
        for i in range(3):
            ob = O["%s%d" % (prefixe, i + 1)]
            d = p0 + i * pas + 2
            f = p0 + (i + 1) * pas - 2
            apparaitre(ob, d, f, G.INCRUST_Y)
            bandes.append((d, f, hauteurs_txt["%s%d" % (prefixe, i + 1)]))
    bandes.append((hook_d, hook_f, hauteurs_txt["TXT_HOOK"]))
    bandes.sort()

    # -- le voile : présent dès qu'une incrustation l'est ------------------
    alpha(voile, f0, 0.0)
    cle(voile, "scale", f0, (1.0, 1.0, 1.0), "LINEAR")
    for d, f, h in bandes:
        k = voile_pour(h)
        cle(voile, "scale", d, (1.0, k, 1.0), "SINE", "EASE_OUT")
        cle(voile, "scale", f, (1.0, k, 1.0), "SINE", "EASE_OUT")
        alpha(voile, d, 0.0)
        alpha(voile, d + G.INCRUST_ENTREE, G.VOILE_OPACITE)
        alpha(voile, f - G.INCRUST_ENTREE, G.VOILE_OPACITE)
        alpha(voile, f, 0.0, "SINE", "EASE_IN")
    alpha(voile, f9, 0.0)

    # -- le carton de sortie ----------------------------------------------
    for nom, retard in (("TXT_NUM", 0), ("TXT_NUM_LEG", 4),
                        ("TXT_SORTIE", 10), ("TXT_CTA", 16), ("LOGO", 22)):
        ob = O[nom]
        #  On relit x sur l'objet : le LOGO porte dans sa position le
        #  recentrage de sa forme, forcer x à 0 le décalerait.
        x, y = ob.location.x, ob.location.y
        d = sor0 + 6 + retard
        cle(ob, "location", d, (x, y - G.INCRUST_MONTEE, G.Z_TEXTE),
            "SINE", "EASE_OUT")
        cle(ob, "location", d + G.INCRUST_ENTREE, (x, y, G.Z_TEXTE),
            "SINE", "EASE_OUT")
        alpha(ob, f0, 0.0)
        alpha(ob, d, 0.0)
        alpha(ob, d + G.INCRUST_ENTREE, 1.0)
        alpha(ob, bou0, 1.0)
        alpha(ob, bou0 + 7, 0.0, "SINE", "EASE_IN")
        alpha(ob, f9, 0.0)

    # -- LA REMISE EN PLACE ------------------------------------------------
    #  Tout ce qui s'est déplacé revient explicitement à sa valeur de
    #  départ, à une image où l'objet est DÉJÀ invisible. Sans ces clés, la
    #  fermeture de boucle ramènerait bien les mêmes pistes, mais en les
    #  faisant dériver lentement sur les quatre-vingts dernières images —
    #  correct au compteur, sale dans la fabrique.
    r_tot = bou0 - 2                    # appareil et incrustations : éteints
    r_fin = f9 - 2                      # carton de sortie : éteint depuis 592
    cle(O["SCREEN_BEFORE"], "location", r_tot,
        (0.0, (G.ECRAN_HAUTEUR - tailles["avant"]) / 2.0, 0.0), "LINEAR")
    cle(O["SCREEN_AFTER"], "location", r_tot,
        (0.0, (G.ECRAN_HAUTEUR - tailles["apres"]) / 2.0, 0.0), "LINEAR")
    cle(pivot, "rotation_euler", r_tot, (0.0, 0.0, 0.0), "LINEAR")
    cle(voile, "scale", r_tot, (1.0, 1.0, 1.0), "LINEAR")
    for nom in (["TXT_HOOK"] + ["TXT_A%d" % i for i in (1, 2, 3)]
                + ["TXT_B%d" % i for i in (1, 2, 3)]):
        cle(O[nom], "location", r_tot,
            (0.0, G.INCRUST_Y - G.INCRUST_MONTEE, G.Z_TEXTE), "LINEAR")
    for nom in ("TXT_NUM", "TXT_NUM_LEG", "TXT_SORTIE", "TXT_CTA", "LOGO"):
        ob = O[nom]
        cle(ob, "location", r_fin,
            (ob.location.x, ob.location.y - G.INCRUST_MONTEE, G.Z_TEXTE),
            "LINEAR")
    return rapport


def fermer_la_boucle():
    """
    L'IMAGE 599 DOIT ÊTRE IDENTIQUE À L'IMAGE 0.

    Plutôt que d'espérer que chaque piste ait été ramenée à la main à sa
    valeur de départ, on la contraint : pour chaque courbe animée, on pose
    une clé sur la dernière image dont la valeur est celle évaluée à
    l'image 0. Une piste oubliée est alors corrigée d'office — et signalée,
    parce qu'une correction silencieuse cacherait un défaut d'animation.
    """
    corrigees = []
    for ob in bpy.data.objects:
        if not ob.animation_data or not ob.animation_data.action:
            continue
        for fc in ob.animation_data.action.fcurves:
            depart = fc.evaluate(G.IMAGE_PREMIERE)
            arrivee = fc.evaluate(G.IMAGE_DERNIERE)
            if abs(depart - arrivee) > 1e-6:
                corrigees.append("%s.%s[%d]  %.4f -> %.4f"
                                 % (ob.name, fc.data_path, fc.array_index,
                                    arrivee, depart))
            kp = fc.keyframe_points.insert(G.IMAGE_DERNIERE, depart)
            kp.interpolation = "LINEAR"
    if corrigees:
        print("  boucle : %d piste(s) ramenées d'office à leur valeur "
              "de départ" % len(corrigees))
        for c in corrigees[:8]:
            print("      %s" % c)
    else:
        print("  boucle : toutes les pistes revenaient déjà à leur "
              "valeur de départ")


# ===========================================================================
#  VÉRIFICATIONS
# ===========================================================================

def verifier_zone_sure():
    """
    Aucun texte ne doit sortir de la zone sûre. On teste la boîte
    englobante EN COORDONNÉES DU MONDE, et on tient compte du décalage
    d'apparition : c'est pendant l'entrée que le texte est le plus bas.
    """
    fautes = []
    noms = [n for n in bpy.data.objects.keys()
            if n.startswith("TXT_")] + ["LOGO"]
    for nom in noms:
        ob = O[nom]
        xs, ys = [], []
        for co in ob.bound_box:
            v = ob.matrix_world @ __import__("mathutils").Vector(co)
            xs.append(v.x)
            ys.append(v.y)
        bas = min(ys) - G.INCRUST_MONTEE          # position basse d'entrée
        haut, gauche, droite = max(ys), min(xs), max(xs)
        d = []
        if haut > G.SUR_Y_HAUT:
            d.append("dépasse en haut de %.0f px"
                     % ((haut - G.SUR_Y_HAUT) * G.PX_PAR_UNITE))
        if bas < G.SUR_Y_BAS:
            d.append("dépasse en bas de %.0f px"
                     % ((G.SUR_Y_BAS - bas) * G.PX_PAR_UNITE))
        if gauche < G.SUR_X_GAUCHE:
            d.append("dépasse à gauche de %.0f px"
                     % ((G.SUR_X_GAUCHE - gauche) * G.PX_PAR_UNITE))
        if droite > G.SUR_X_DROITE:
            d.append("dépasse à droite de %.0f px"
                     % ((droite - G.SUR_X_DROITE) * G.PX_PAR_UNITE))
        if d:
            fautes.append("%-13s %s" % (nom, " ; ".join(d)))
    if fautes:
        print("\n  ZONE SÛRE — %d objet(s) hors cadre :" % len(fautes))
        for f in fautes:
            print("      " + f)
        raise SystemExit(2)
    print("  zone sûre : %d objets vérifiés, aucun débordement" % len(noms))


def verifier_vitesses(rapport):
    """
    On compare les vitesses de CROISIÈRE, pas les vitesses moyennes.

    La moyenne d'une phase inclut ses deux amorces et vaut donc toujours
    moins que la consigne : la lire comme la vitesse du défilement ferait
    échouer le contrôle sur un défilement pourtant parfaitement réglé.
    Ce qui doit être identique d'un plan à l'autre, c'est le palier.
    """
    v = G.VITESSE_DEFILEMENT
    paliers = []
    for nom, r in sorted(rapport.items()):
        if r["course"] < G.COURSE_NEGLIGEABLE:
            print("  %-6s : page d'%.2f hauteur d'écran — rien à faire "
                  "défiler, position maintenue" % (nom, 1.0 + r["course"]))
            continue
        moyenne = r["course"] / r["duree"]
        print("  %-6s : %.2f hauteurs d'écran en %.2f s   croisière %.3f h/s"
              "   (moyenne %.3f, amorces comprises)"
              % (nom, r["course"], r["duree"], r["croisiere"], moyenne))
        if abs(r["croisiere"] - v) > 0.002:
            raise SystemExit("vitesse de croisière %.4f au lieu de %.4f "
                             "pour « %s »" % (r["croisiere"], v, nom))
        paliers.append(r["croisiere"])
    if len(paliers) >= 2 and max(paliers) - min(paliers) > 1e-6:
        raise SystemExit("les deux défilements n'ont pas la même vitesse "
                         "de croisière : %s" % paliers)
    print("  vitesses : croisière identique à %.3f hauteur d'écran "
          "par seconde" % v)


# ===========================================================================

def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if not argv:
        raise SystemExit("usage : ... -- projets/<slug>.json [options]")
    projet = argv[0]
    image_seule = None
    rendre = "--pas-de-rendu" not in argv
    sortie = None
    if "--image" in argv:
        image_seule = [int(argv[argv.index("--image") + 1])]
    if "--images" in argv:
        image_seule = [int(x) for x
                       in argv[argv.index("--images") + 1].split(",")]
    if "--sortie" in argv:
        sortie = argv[argv.index("--sortie") + 1]

    cfg = C.charger(os.path.join(RACINE, projet)
                    if not os.path.isabs(projet) else projet)
    jchemin = os.path.join(RACINE, "out", cfg["slug"], "capture.json")
    if not os.path.exists(jchemin):
        raise SystemExit("capture manquante : lancez d'abord "
                         "`python src/capture.py %s`" % projet)
    journal = json.load(open(jchemin, encoding="utf-8"))

    print("\n  %s — %s (%d)" % (cfg["slug"], cfg["client_affiche"],
                                cfg["annee"]))
    #  Le cadre du téléphone a sa propre teinte : sur le fond d'encre, un
    #  cadre couleur d'encre serait invisible.
    if "MAT_APPAREIL" not in bpy.data.materials:
        src = bpy.data.materials["MAT_ENCRE"]
        m = src.copy()
        m.name = "MAT_APPAREIL"
        em = [n for n in m.node_tree.nodes if n.type == "EMISSION"][0]
        em.inputs["Color"].default_value = (*srgb(G.APPAREIL_COULEUR), 1.0)

    tailles = poser_images(journal, cfg["slug"])
    hauteurs = remplir_textes(cfg)
    verifier_zone_sure()
    rapport = animer(cfg, tailles, hauteurs)
    verifier_vitesses(rapport)
    fermer_la_boucle()

    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = G.IMAGE_PREMIERE, G.IMAGE_DERNIERE
    sc.render.filepath = sortie or os.path.join(RACINE, "out", cfg["slug"],
                                                "frames", "")
    if not rendre:
        print("  (construction seule, pas de rendu)")
        return
    if image_seule is not None:
        for f in image_seule:
            sc.frame_set(f)
            sc.render.filepath = os.path.join(
                sortie or os.path.join(RACINE, "out", cfg["slug"]),
                "img_%04d.png" % f)
            bpy.ops.render.render(write_still=True)
    else:
        bpy.ops.render.render(animation=True)


main()
