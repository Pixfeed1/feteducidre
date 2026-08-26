"""
IMAGE 6 de l'article — le placement du Volume probe autour de la pièce.

DEUX FAÇONS DE LANCER CE FICHIER, ET IL SAIT LAQUELLE
-----------------------------------------------------------------------------
1. DANS BLENDER, pour obtenir la VRAIE capture d'écran :

       blender --python article/placer_volume.py

   ou, sans terminal : Blender ▸ onglet **Scripting** ▸ **Open** ▸ ce fichier
   ▸ **Run Script**.

   Le script monte la pièce, pose la sonde, règle la vue 3D, ouvre l'onglet
   **Object Data** à droite et déclenche la photo tout seul. Aucune souris à
   placer, rien à survoler : il n'y a pas de menu dans cette image, donc rien
   qui exige d'être « invoqué ». L'image part sur le Bureau.

2. EN LIGNE DE COMMANDE, pour un aperçu sans interface :

       python3 article/placer_volume.py

   Rend `article/placer-irradiance-volume-apercu.png` : un tracé filaire de
   la même scène, qui sert à vérifier le cadrage et le débordement avant
   d'ouvrir Blender. Ce n'est PAS la capture — c'est un schéma.

-----------------------------------------------------------------------------
POURQUOI LE VOLUME DOIT DÉBORDER, ET DE COMBIEN
-----------------------------------------------------------------------------
C'est le sujet de l'image, et ce n'est pas une préférence de goût.

La sonde n'éclaire que ce qu'elle contient. Un mur laissé À L'EXTÉRIEUR du
volume ne reçoit aucune irradiance : il rend noir. Sur cette pièce, un volume
rentré de 45 cm sous les parois donnait une image de moyenne 86,5 ; le même
volume débordant derrière les murs, 129,9. Ce n'était pas une nuance, c'était
la moitié de la pièce.

Ici le volume déborde de 18 cm au-delà de la face INTÉRIEURE des murs. Comme
les cloisons font 12 cm d'épaisseur, il ressort donc de 6 cm derrière leur
face extérieure : chaque paroi est entièrement prise dedans, avec un peu de
marge. C'est ce léger dépassement qu'on voit sur l'image, et c'est lui qui
supprime les fuites de lumière au calcul.

Le sens du réglage est contre-intuitif : on croit protéger le calcul en
rentrant le volume à l'intérieur de la pièce, alors qu'on prive les murs de
la seule chose qui les éclaire.
"""

import math
import os
import sys

import bpy

# ---------------------------------------------------------------------------
#  LA PIÈCE — les mêmes cotes que le rendu d'ouverture de l'article
# ---------------------------------------------------------------------------
X0, X1 = -3.00, 3.00
Y0, Y1 = -3.50, 3.50
Z0, Z1 = 0.00, 3.00
EP = 0.12                      # épaisseur des cloisons

F_Y0, F_Y1 = -0.80, 1.60       # la fenêtre, dans le mur de gauche
F_Z0, F_Z1 = 0.65, 2.50

#  LE DÉBORDEMENT. Positif = la sonde ressort au-delà de la face intérieure.
DEBORD = 0.18
RESOLUTION_SONDE = (11, 12, 6)

#  LES PAROIS QU'ON RETIRE DE LA VUE — la coupe.
#
#  Première capture : toutes les cloisons en place et les rayons X à 0,42.
#  Résultat, une masse sombre translucide où l'on ne distingue ni les murs,
#  ni la fenêtre, ni les meubles — donc rien de ce que le volume est censé
#  déborder. Une pièce fermée photographiée de l'extérieur ne montre qu'une
#  boîte, et la question posée est justement le rapport entre cette boîte et
#  ses murs.
#
#  On enlève donc les trois parois placées entre la caméra et l'intérieur.
#  Les autres restent, et ce sont elles qui servent de repère : le volume les
#  dépasse visiblement en haut et dans les angles.
MASQUES = ("Plafond", "Mur_avant", "Mur_droite")

#  Le teal des sondes dans Blender, pour le tracé filaire de l'aperçu.
TEAL = (0.28, 0.88, 0.72)
GRIS = (0.62, 0.64, 0.70)


def dossier_bureau():
    """`__file__` n'existe pas quand on lance depuis l'onglet Scripting.
    Le Bureau est le seul endroit qu'on ne peut pas rater."""
    maison = os.path.expanduser("~")
    for nom in ("Desktop", "Bureau"):
        d = os.path.join(maison, nom)
        if os.path.isdir(d):
            return d
    return maison


def matiere(nom, couleur, emission=False):
    m = bpy.data.materials.new(nom)
    m.use_nodes = True
    if emission:
        nt = m.node_tree
        nt.nodes.clear()
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs["Color"].default_value = (*couleur, 1.0)
        em.inputs["Strength"].default_value = 1.0
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    else:
        p = m.node_tree.nodes["Principled BSDF"]
        p.inputs["Base Color"].default_value = (*couleur, 1.0)
        p.inputs["Roughness"].default_value = 0.75
    m.diffuse_color = (*couleur, 1.0)      # la couleur du mode Solid
    return m


#  Les six faces d'un pavé, orientées vers l'EXTÉRIEUR. L'ordre compte :
#  (0,1,2,3) pour la face du bas donnerait une normale vers le haut, donc
#  rentrante, et le mode Solid afficherait la pièce à l'envers.
_FACES = ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
          (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7))


def pave(nom, x0, x1, y0, y1, z0, z1, mat=None):
    """
    Un pavé, construit par l'API DE DONNÉES et non par un opérateur.

    AUCUN `bpy.ops` ICI, ET C'EST LE POINT.
    La version précédente faisait `bpy.ops.mesh.primitive_cube_add()` puis
    relisait l'objet créé dans `bpy.context.object`. Lancée depuis l'onglet
    Scripting, elle s'arrêtait sur

        AttributeError: 'Context' object has no attribute 'object'

    parce que le contexte y est celui de l'ÉDITEUR DE TEXTE : il n'a ni objet
    actif ni vue 3D. Un opérateur qui marche dans la vue 3D n'a aucune raison
    de marcher ailleurs, et `bpy.context` change de contenu selon la zone d'où
    part le script. Construire le maillage à la main ne dépend, lui, de rien.
    """
    hx, hy, hz = (x1 - x0) / 2, (y1 - y0) / 2, (z1 - z0) / 2
    coins = [(-hx, -hy, -hz), (hx, -hy, -hz), (hx, hy, -hz), (-hx, hy, -hz),
             (-hx, -hy, hz), (hx, -hy, hz), (hx, hy, hz), (-hx, hy, hz)]
    me = bpy.data.meshes.new(nom)
    me.from_pydata(coins, [], list(_FACES))
    me.validate()
    me.update()
    ob = bpy.data.objects.new(nom, me)
    ob.location = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    if mat is not None:
        me.materials.append(mat)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def dalle(nom, x0, x1, y0, y1, z0, z1, mat):
    return pave(nom, x0, x1, y0, y1, z0, z1, mat)


def nettoyer():
    """
    Vider la scène SANS toucher à l'interface.

    `wm.read_factory_settings()` faisait le ménage, mais il recharge le
    fichier : lancé depuis l'onglet Scripting, il efface le bloc de texte en
    cours d'exécution. Le script survit — Python tient déjà son code compilé —
    mais l'utilisateur, lui, n'a plus son script à l'écran pour le relancer.
    On retire donc les données une par une.
    """
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for banque in (bpy.data.meshes, bpy.data.lightprobes, bpy.data.materials):
        for x in list(banque):
            if x.users == 0:
                banque.remove(x)


def piece():
    """La coquille. Le mur de gauche est découpé en quatre dalles autour de
    la fenêtre — un trou dans une boîte demanderait un booléen, et un booléen
    dans une image d'interface est une complication qui ne se voit pas."""
    nettoyer()
    mur = matiere("Mur", (0.78, 0.77, 0.75))
    sol = matiere("Sol", (0.42, 0.34, 0.27))

    dalle("Sol", X0 - EP, X1 + EP, Y0 - EP, Y1 + EP, Z0 - EP, Z0, sol)
    dalle("Plafond", X0 - EP, X1 + EP, Y0 - EP, Y1 + EP, Z1, Z1 + EP, mur)
    dalle("Mur_fond", X0 - EP, X1 + EP, Y1, Y1 + EP, Z0, Z1, mur)
    dalle("Mur_avant", X0 - EP, X1 + EP, Y0 - EP, Y0, Z0, Z1, mur)
    dalle("Mur_droite", X1, X1 + EP, Y0, Y1, Z0, Z1, mur)
    #  Le mur de gauche, en quatre morceaux autour de l'ouverture
    dalle("Mur_g_bas", X0 - EP, X0, F_Y0, F_Y1, Z0, F_Z0, mur)
    dalle("Mur_g_haut", X0 - EP, X0, F_Y0, F_Y1, F_Z1, Z1, mur)
    dalle("Mur_g_avant", X0 - EP, X0, Y0, F_Y0, Z0, Z1, mur)
    dalle("Mur_g_arriere", X0 - EP, X0, F_Y1, Y1, Z0, Z1, mur)

    #  Deux meubles : sans eux la pièce est une boîte vide et le lecteur ne
    #  situe plus l'échelle.
    bois = matiere("Bois", (0.35, 0.22, 0.13))
    dalle("Meuble", X1 - 0.55, X1 - 0.05, Y1 - 1.90, Y1 - 0.10, Z0, 1.80, bois)
    dalle("Table", -1.10, 0.90, -1.00, 0.60, 0.34, 0.42, bois)


def sonde():
    """
    Le Volume probe, dimensionné pour ENGLOBER les murs — c'est tout le sujet
    de l'image. Voir l'en-tête pour la mesure qui a tranché.
    """
    d0 = bpy.data.lightprobes.new("VOLUME_PROBE", type='VOLUME')
    ob = bpy.data.objects.new("VOLUME_PROBE", d0)
    ob.location = ((X0 + X1) / 2, (Y0 + Y1) / 2, (Z0 + Z1) / 2)
    bpy.context.scene.collection.objects.link(ob)
    ob.scale = ((X1 - X0) / 2 + DEBORD,
                (Y1 - Y0) / 2 + DEBORD,
                (Z1 - Z0) / 2 + DEBORD)
    d = ob.data
    d.resolution_x, d.resolution_y, d.resolution_z = RESOLUTION_SONDE
    d.bake_samples = 1024
    d.surfel_density = 28
    d.capture_world = True
    d.capture_indirect = True
    d.capture_emission = True
    return ob


def cotes():
    """Ce que l'image affirme, en chiffres, pour la légende et le journal."""
    demi_x = (X1 - X0) / 2 + DEBORD
    return {
        "piece": (X1 - X0, Y1 - Y0, Z1 - Z0),
        "sonde": (2 * demi_x, (Y1 - Y0) + 2 * DEBORD, (Z1 - Z0) + 2 * DEBORD),
        "debord_interieur": DEBORD,
        "debord_exterieur": DEBORD - EP,
        "resolution": RESOLUTION_SONDE,
        "echantillons": RESOLUTION_SONDE[0] * RESOLUTION_SONDE[1]
                        * RESOLUTION_SONDE[2],
    }


def journal():
    c = cotes()
    print()
    print("  piece      %.2f x %.2f x %.2f m  (cloisons %.0f cm)"
          % (*c["piece"], EP * 100))
    print("  sonde      %.2f x %.2f x %.2f m" % c["sonde"])
    print("  debord     %.0f cm au-dela de la face interieure,"
          "  %.0f cm derriere la face exterieure"
          % (c["debord_interieur"] * 100, c["debord_exterieur"] * 100))
    print("  resolution %d x %d x %d  =  %d echantillons"
          % (*c["resolution"], c["echantillons"]))
    if c["debord_exterieur"] <= 0:
        raise SystemExit(
            "le volume ne ressort pas derriere les murs : avec un debord de "
            "%.0f cm et des cloisons de %.0f cm, les parois restent hors du "
            "volume et rendront noir" % (DEBORD * 100, EP * 100))


# ---------------------------------------------------------------------------
#  MODE 1 : DANS BLENDER — régler l'interface, puis photographier
# ---------------------------------------------------------------------------
def aller_sur_layout():
    """
    Se placer sur l'espace de travail « Layout » avant de photographier.

    Si on lance le script depuis l'onglet Scripting — ce qui est le cas le
    plus probable — on est sur un espace où la vue 3D est réduite au quart de
    l'écran et où il n'y a AUCUN éditeur Properties. La capture serait donc
    conforme à la demande sur le papier et inutilisable en fait : pas de
    panneau Object Data à droite, pas de résolution visible.

    Blender traduit les noms d'espaces de travail, mais pas celui-ci : dans
    toutes les langues il s'appelle « Layout ». On prend quand même la
    précaution de retomber sur le premier espace contenant à la fois une vue
    3D et un éditeur Properties.
    """
    fen = bpy.context.window

    def convient(ws):
        types = {z.type for e in ws.screens for z in e.areas}
        return 'VIEW_3D' in types and 'PROPERTIES' in types

    choix = bpy.data.workspaces.get("Layout")
    if choix is None or not convient(choix):
        choix = next((w for w in bpy.data.workspaces if convient(w)), None)
    if choix is None:
        print("  aucun espace de travail avec vue 3D + Properties")
        return None
    if fen.workspace != choix:
        fen.workspace = choix
        #  Le changement d'espace n'est effectif qu'au redessin suivant.
        redessiner(1)
    print("  espace de travail : %s" % choix.name)
    #  On renvoie l'espace choisi, et la suite règle SES écrans plutôt que
    #  `bpy.context.window.screen` : au moment où on le lit, celui-ci peut
    #  encore être l'ancien. Viser l'objet plutôt que le contexte, une fois
    #  de plus.
    return choix


def redessiner(fois=2):
    """Forcer Blender à redessiner. Beaucoup de choses ne deviennent vraies
    qu'au redessin : le changement d'espace de travail, et surtout la liste
    des onglets que l'éditeur Properties accepte."""
    try:
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=fois)
    except Exception as e:
        print("  redessin force indisponible (%s)" % e)


def regler_vue_3d(espace):
    """
    La vue 3D : Solid + rayons X, vue depuis l'extérieur en trois quarts.

    Les rayons X ne sont pas un effet : sans eux le volume est CACHÉ par les
    murs qu'il englobe, et l'image ne montre plus rien du débordement — le
    gizmo d'une sonde est dessiné avec test de profondeur comme le reste.
    """
    from mathutils import Vector, Matrix

    oeil = Vector((9.6, -11.4, 7.6))
    cible = Vector((0.0, 0.0, 1.35))
    rot = (cible - oeil).to_track_quat('-Z', 'Y').to_matrix().to_4x4()
    pose = Matrix.Translation(oeil) @ rot

    n = 0
    zones = [z for e in espace.screens for z in e.areas]
    for zone in zones:
        if zone.type != 'VIEW_3D':
            continue
        sp = zone.spaces.active
        sp.shading.type = 'SOLID'
        #  Plus de rayons X : la coupe fait le travail, et mieux. Les rayons X
        #  délavent tout — murs, sol, meubles et gizmo prennent la même teinte
        #  fantôme, et on perd la seule chose qu'on voulait montrer.
        sp.shading.show_xray = False
        sp.overlay.show_overlays = True
        #  Le fil de fer par-dessus le solide : il dessine l'arête des murs,
        #  donc la limite exacte que le volume dépasse. Sans lui, deux surfaces
        #  grises voisines se lisent comme une seule.
        sp.overlay.show_wireframes = True
        sp.overlay.wireframe_opacity = 0.55
        sp.lens = 42.0
        for region in zone.regions:
            if region.type == 'WINDOW' and region.data is not None:
                rv = region.data
                rv.view_perspective = 'PERSP'
                rv.view_matrix = pose.inverted()
                #  `update()` n'est pas une propriété mais une FONCTION RNA :
                #  la chercher avec `hasattr` sur le type répond False et
                #  laisse croire qu'elle n'existe pas. Elle existe, et sans
                #  elle la matrice posée est écrasée au redessin suivant par
                #  la position et la distance de vue mémorisées.
                rv.update()
                n += 1
        zone.tag_redraw()
    return n


def couper_les_parois(pour_le_rendu=False):
    """Retirer de la vue les parois qui bouchent le regard. Voir MASQUES."""
    n = 0
    for nom in MASQUES:
        ob = bpy.data.objects.get(nom)
        if ob is None:
            continue
        #  `hide_viewport` est une propriété simple : elle ne dépend d'aucun
        #  contexte, contrairement à `hide_set()` qui veut une couche de vue.
        ob.hide_viewport = True
        ob.hide_render = pour_le_rendu
        n += 1
    return n


def activer_la_sonde(sonde_ob):
    """
    Rendre la sonde ACTIVE, et le faire AVANT de toucher à l'interface.

    Un objet seulement sélectionné ne suffit pas : l'onglet Object Data
    affiche les données de l'objet actif.
    """
    #  `object.select_all` est un opérateur de vue 3D : depuis l'onglet
    #  Scripting il n'a pas de contexte. On désélectionne à la main, en
    #  nommant explicitement la couche de vue plutôt qu'en laissant
    #  `select_set` aller la chercher dans un contexte qui n'en a peut-être
    #  pas — c'est la même erreur, un cran plus bas.
    vl = bpy.context.view_layer
    for ob in bpy.context.scene.objects:
        ob.select_set(ob is sonde_ob, view_layer=vl)
    vl.objects.active = sonde_ob


def regler_panneau_data(espace):
    """
    Basculer l'éditeur Properties sur l'onglet Object Data.

    LA LISTE DES ONGLETS EST DYNAMIQUE, ET C'EST TOUT LE PIÈGE.
    `SpaceProperties.context` n'accepte pas les dix-huit onglets du type : il
    n'accepte que ceux qui ont un sens à l'instant où on écrit dedans. Sans
    objet actif, la liste se réduit à

        ('TOOL', 'RENDER', 'OUTPUT', 'VIEW_LAYER', 'SCENE', 'WORLD')

    et poser 'DATA' lève un TypeError. C'est exactement ce qui arrivait : la
    sonde était bien rendue active une ligne plus haut, mais l'éditeur
    Properties n'avait pas encore été redessiné, donc il ne la voyait pas
    encore. L'erreur ne dit pas « pas encore prêt », elle dit « valeur
    inconnue » — d'où l'envie d'aller chercher une faute d'orthographe dans
    'DATA' plutôt qu'un problème de moment.

    On redessine donc, puis on réessaie, et on le dit si ça ne prend pas.
    """
    n, manques = 0, 0
    for ecran in espace.screens:
        for zone in ecran.areas:
            if zone.type != 'PROPERTIES':
                continue
            ok, pourquoi = _poser_onglet(zone, 'DATA', ecran)
            if not ok:
                redessiner(1)          # laisser l'éditeur voir l'objet actif
                ok, pourquoi = _poser_onglet(zone, 'DATA', ecran)
            if ok:
                n += 1
            else:
                manques += 1
                if pourquoi:
                    print("  onglet refuse -> %s" % pourquoi)
            zone.tag_redraw()
    if manques:
        actif = bpy.context.view_layer.objects.active
        print("  %d editeur(s) Properties n'ont pas accepte l'onglet Object "
              "Data (objet actif : %s)"
              % (manques, actif.name if actif else "AUCUN"))
        print("  la capture partira quand meme : mieux vaut une image "
              "incomplete qu'un script qui s'arrete")
    return n


def _poser_onglet(zone, onglet, ecran=None):
    """
    Poser un onglet, d'abord en désignant la zone visée.

    Deux raisons peuvent faire refuser 'DATA', et on ne sait pas laquelle
    depuis Python, alors on couvre les deux :

      - l'éditeur Properties n'a pas encore été rafraîchi et ne voit pas
        l'objet actif tout juste posé — c'est le redessin qui règle ça ;
      - le contexte d'où part le script (l'éditeur de texte) n'expose pas
        l'objet actif, et c'est LUI que Blender interroge pour construire la
        liste. `temp_override` reconstruit alors un contexte centré sur la
        fenêtre et la zone visées, où l'objet actif se résout.

    Le repli sans `temp_override` reste utile : sur une version plus ancienne
    ou dans un contexte incomplet, l'affectation directe peut passer alors
    que l'override échoue.
    """
    cible = zone.spaces.active
    fen = bpy.context.window
    dernier = ""
    if fen is not None:
        try:
            reglages = {"window": fen, "area": zone}
            if ecran is not None:
                reglages["screen"] = ecran
            with bpy.context.temp_override(**reglages):
                cible.context = onglet
            return True, ""
        except (TypeError, RuntimeError, AttributeError) as e:
            dernier = str(e)
    try:
        cible.context = onglet
        return True, ""
    except TypeError as e:
        #  Le message d'erreur de Blender ÉNUMÈRE les onglets acceptés. C'est
        #  le seul moyen simple de connaître cette liste dynamique depuis
        #  Python, alors on la garde pour la dire à l'utilisateur au lieu de
        #  le laisser deviner.
        return False, str(e) or dernier


def photographier():
    """
    La photo.

    `wm.redraw_timer` est indispensable : lancé par `--python`, le script
    s'exécute AVANT le premier dessin de la fenêtre. Sans redessin forcé, la
    capture fige une interface qui n'a pas encore vu nos réglages — vue par
    défaut, onglet par défaut. On photographie alors le cube de démarrage.
    """
    sortie = os.path.join(dossier_bureau(), "placer-volume-capture.png")
    for zone in bpy.context.window.screen.areas:
        zone.tag_redraw()
    try:
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=3)
    except Exception as e:
        print("  redessin force indisponible (%s), on tente quand meme" % e)
    bpy.ops.screen.screenshot(filepath=sortie)

    ok = os.path.exists(sortie)
    lignes = ([sortie, "%.0f Ko" % (os.path.getsize(sortie) / 1024.0)]
              if ok else ["Aucun fichier ecrit dans :", dossier_bureau()])

    def dessiner(self, _ctx):
        for l in lignes:
            self.layout.label(text=l)
    try:
        bpy.context.window_manager.popup_menu(
            dessiner, title="Capture enregistree" if ok else "Echec",
            icon='CHECKMARK' if ok else 'ERROR')
    except Exception:
        pass
    for l in lignes:
        print("  " + l)


# ---------------------------------------------------------------------------
#  MODE 2 : SANS INTERFACE — un tracé filaire pour vérifier le cadrage
# ---------------------------------------------------------------------------
def filaire(ob, couleur, epaisseur):
    """Le mode Solid n'existe pas au rendu. Pour qu'une arête apparaisse dans
    une image calculée, il faut lui donner de la matière : modificateur
    Wireframe, émission pure."""
    w = ob.modifiers.new("FIL", 'WIREFRAME')
    w.thickness = epaisseur
    w.use_replace = True
    ob.data.materials.clear()
    ob.data.materials.append(matiere("FIL_" + ob.name, couleur, emission=True))


def apercu():
    sortie = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "placer-irradiance-volume-apercu.png")
    couper_les_parois(pour_le_rendu=True)
    for ob in list(bpy.data.objects):
        if ob.type == 'MESH' and not ob.hide_render:
            filaire(ob, GRIS, 0.014)

    s = bpy.data.objects["VOLUME_PROBE"]
    cx, cy, cz = s.location
    ex, ey, ez = s.scale                # la « taille » d'une sonde EST son
                                        # échelle : demi-dimensions, en mètres
    boite = pave("SONDE_FILAIRE", cx - ex, cx + ex, cy - ey, cy + ey,
                 cz - ez, cz + ez)
    filaire(boite, TEAL, 0.028)

    cd = bpy.data.cameras.new("C")
    cd.lens = 42.0
    cam = bpy.data.objects.new("C", cd)
    cam.location = (9.6, -11.4, 7.6)
    from mathutils import Vector
    cam.rotation_euler = (Vector((0.0, 0.0, 1.35)) - cam.location) \
        .to_track_quat('-Z', 'Y').to_euler()
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam

    w = bpy.data.worlds.new("W")
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = \
        (0.020, 0.021, 0.026, 1.0)
    sc = bpy.context.scene
    sc.world = w
    sc.render.engine = 'BLENDER_EEVEE_NEXT'
    sc.render.resolution_x, sc.render.resolution_y = 1500, 1050
    sc.eevee.taa_render_samples = 32
    sc.eevee.use_raytracing = False
    sc.view_settings.view_transform = 'Standard'
    sc.render.filepath = sortie
    bpy.ops.render.render(write_still=True)
    print("  -> %s" % sortie)


def main():
    piece()
    s = sonde()
    journal()

    if bpy.app.background:
        print("  (pas d'interface : on rend l'apercu filaire)")
        apercu()
        return

    #  L'ORDRE COMPTE. La sonde doit être l'objet actif AVANT qu'on demande
    #  à l'éditeur Properties son onglet Object Data : cet onglet n'existe
    #  dans la liste des valeurs acceptées que s'il y a un objet actif.
    activer_la_sonde(s)
    print("  parois retirees de la vue : %d" % couper_les_parois())
    espace = aller_sur_layout()
    if espace is None:
        espace = bpy.context.window.workspace
    redessiner(1)

    v = regler_vue_3d(espace)
    p = regler_panneau_data(espace)
    print("  vues 3D reglees : %d      panneaux Properties sur Data : %d"
          % (v, p))
    if v == 0:
        print("  ATTENTION : aucune vue 3D reglee.")
    photographier()


if __name__ == "__main__":
    main()
