"""
LA CHARTE — source de vérité unique du générateur de Reels PixFeed.

Aucune couleur, aucune durée, aucune position, aucune taille de texte ne doit
apparaître ailleurs que dans ce fichier. Changer l'allure de toute la série se
fait ici, en une ligne, et s'applique rétroactivement à tous les projets.

Le test `tests/test_charte.py` échoue si une valeur de charte est écrite en dur
dans un autre fichier de `src/`.

----------------------------------------------------------------------------
CONVENTION D'UNITÉS
----------------------------------------------------------------------------
La scène Blender est en projection orthographique et l'échelle est choisie pour
que **1 unité Blender = 100 pixels de l'image finale**. Toute la mise en page
s'écrit donc en centièmes de pixel sans conversion mentale :

    x ∈ [-5.40, +5.40]      (1080 px de large)
    y ∈ [-9.60, +9.60]      (1920 px de haut)

C'est le seul réglage qui rende la géométrie relisible six mois plus tard.
"""

# ---------------------------------------------------------------------------
#  FORMAT
# ---------------------------------------------------------------------------

LARGEUR_PX = 1080
HAUTEUR_PX = 1920
IMAGES_PAR_SECONDE = 30
DUREE_IMAGES = 600                      # 20,00 s exactement
IMAGE_PREMIERE = 0
IMAGE_DERNIERE = DUREE_IMAGES - 1       # 599 — identique à l'image 0

PX_PAR_UNITE = 100.0
DEMI_LARGEUR = LARGEUR_PX / 2.0 / PX_PAR_UNITE      # 5.40
DEMI_HAUTEUR = HAUTEUR_PX / 2.0 / PX_PAR_UNITE      # 9.60


# ---------------------------------------------------------------------------
#  ZONE SÛRE
# ---------------------------------------------------------------------------
#  Le cahier des charges demandait 250 px en haut et 250 px en bas, centré.
#  Vérification faite sur les guides Instagram 2026 : la zone occupée par
#  l'interface n'est PAS symétrique.
#
#    - en bas, le pseudo, la légende et le crédit audio mangent 280 à 320 px ;
#    - à droite, la colonne j'aime / commenter / partager / remixer prend
#      90 à 120 px — le cahier des charges ne la mentionnait pas du tout ;
#    - en haut, 108 à 250 px selon l'appareil.
#
#  On garde la hauteur utile demandée (1420 px) mais on la répartit
#  correctement, et on protège la colonne de droite.
#
#  Pour revenir au cadrage symétrique du cahier : mettre 250 / 250 / 0 / 0.

SUR_MARGE_HAUT = 160
SUR_MARGE_BAS = 340
SUR_MARGE_GAUCHE = 60
SUR_MARGE_DROITE = 120

SUR_Y_HAUT = DEMI_HAUTEUR - SUR_MARGE_HAUT / PX_PAR_UNITE        # +8.00
SUR_Y_BAS = -DEMI_HAUTEUR + SUR_MARGE_BAS / PX_PAR_UNITE         # -6.20
SUR_X_GAUCHE = -DEMI_LARGEUR + SUR_MARGE_GAUCHE / PX_PAR_UNITE   # -4.80
SUR_X_DROITE = DEMI_LARGEUR - SUR_MARGE_DROITE / PX_PAR_UNITE    # +4.20
SUR_Y_CENTRE = (SUR_Y_HAUT + SUR_Y_BAS) / 2.0                    # +0.90


# ---------------------------------------------------------------------------
#  COULEURS
# ---------------------------------------------------------------------------
#  Reprises du film du logo (voir logo/METHODE.md) pour que les deux formats
#  se ressemblent dans le fil. Le fond n'est jamais du noir pur : un noir pur
#  se confond avec le fond de l'application et l'image perd ses bords.

ENCRE = (0.038, 0.038, 0.050)          # #0A0A0D — le fond
BLANC = (0.925, 0.925, 0.945)          # #ECECF1 — le texte principal
VIOLET = (0.580, 0.260, 0.980)         # #9442FA — la marque, et l'« après »
GRIS = (0.430, 0.430, 0.478)           # #6E6E7A — le secondaire, et l'« avant »
VOILE = (0.020, 0.020, 0.030)          # le bandeau sous les incrustations
VOILE_OPACITE = 0.82

#  Règle absolue : on n'emprunte JAMAIS les couleurs du client. Le cadre est
#  aux couleurs PixFeed, le site du client vit à l'intérieur de l'écran.


# ---------------------------------------------------------------------------
#  TYPOGRAPHIE
# ---------------------------------------------------------------------------
#  Les fichiers sont versionnés dans assets/fonts/ et chargés explicitement.
#  Jamais de police système : le rendu doit être identique sur toute machine.

POLICE_TITRE = "assets/fonts/charte-Bold.ttf"
POLICE_TEXTE = "assets/fonts/charte-Regular.ttf"

#  Tailles NOMINALES, en unités (1 unité = 100 px ; la hauteur de capitale
#  vaut environ 0,72 × la taille). Elles sont ensuite RÉDUITES
#  automatiquement si le texte dépasse la largeur utile — voir `ajuster()`
#  dans build_reel.py. Deviner la largeur d'une chaîne au nombre de
#  caractères ne marche pas : « MMM » et « iii » ne font pas la même largeur.
T_CLIENT = 1.30
T_SECTEUR = 0.52
T_ANNEE = 0.44
T_HOOK = 0.98
T_POINT = 0.80
T_NUM = 3.20                            # le chiffre, seul et énorme
T_NUM_LEG = 0.52
T_SORTIE = 0.72
T_CTA = 0.66

INTERLIGNE = 1.26                       # multiple de la taille

#  Largeur utile d'une ligne de texte. Volontairement plus large que
#  l'appareil : une incrustation pleine largeur se lit mieux qu'une
#  incrustation coincée dans l'écran du téléphone.
#
#  Elle est DÉDUITE de la zone sûre, jamais choisie. Les textes sont centrés
#  sur x = 0 alors que la zone sûre est asymétrique (la colonne de boutons
#  d'Instagram mange plus à droite qu'à gauche) : la demi-largeur utilisable
#  est donc celle du côté LE PLUS ÉTROIT. Écrite en dur à 9,00, elle faisait
#  dépasser de 31 px à droite le premier nom de client un peu long.
TEXTE_LARGEUR = 2.0 * min(abs(SUR_X_GAUCHE), SUR_X_DROITE)

#  Blender ne sait ni couper les lignes ni gérer une mise en forme riche :
#  le retour à la ligne est décidé par le script, à ce nombre de caractères.
COUPE_HOOK = 18
COUPE_POINT = 20
COUPE_SORTIE = 24
COUPE_CTA = 24


# ---------------------------------------------------------------------------
#  L'APPAREIL ET SON ÉCRAN
# ---------------------------------------------------------------------------
#  Rapport 390 × 844 : le viewport de capture. L'écran affiché en garde le
#  rapport exact, sinon les captures seraient déformées.

CAPTURE_VIEWPORT = (390, 844)
CAPTURE_ECHELLE = 3                     # device_scale_factor

ECRAN_LARGEUR = 5.60
ECRAN_HAUTEUR = ECRAN_LARGEUR * CAPTURE_VIEWPORT[1] / CAPTURE_VIEWPORT[0]
APPAREIL_BORD = 0.12
#  Centré sur la ZONE SÛRE (y = +0,90), pas sur l'image : sinon l'appareil
#  laisse un grand vide sous lui, là où l'interface d'Instagram vient de
#  toute façon poser la légende.
APPAREIL_CENTRE_Y = 0.90
APPAREIL_RAYON = 0.40                   # arrondi des coins
APPAREIL_COULEUR = (0.170, 0.170, 0.215)   # le cadre, un cran au-dessus du fond

#  L'écran s'étend donc de :
ECRAN_Y_HAUT = APPAREIL_CENTRE_Y + ECRAN_HAUTEUR / 2.0
ECRAN_Y_BAS = APPAREIL_CENTRE_Y - ECRAN_HAUTEUR / 2.0


# ---------------------------------------------------------------------------
#  LE DÉFILEMENT
# ---------------------------------------------------------------------------
#  LA règle d'honnêteté du format : l'avant et l'après défilent à la MÊME
#  vitesse apparente, exprimée en hauteurs d'écran par seconde. Comparer deux
#  sites à deux vitesses différentes est un mensonge, et ça se voit.
#
#  Si une page est trop courte pour occuper tout le temps imparti, on défile
#  jusqu'à sa fin puis on maintient. On n'accélère jamais pour « remplir ».

VITESSE_DEFILEMENT = 0.62               # hauteurs d'écran par seconde

#  En dessous de cette course, il n'y a rien à faire défiler : la page tient
#  dans un écran. C'est le cas normal d'un vieux site non responsive, que le
#  navigateur mobile dézoome en entier — et c'est précisément la preuve
#  visuelle qu'on cherche à montrer. On maintient alors la position, comme le
#  demande le cahier des charges, et la vitesse n'a pas de sens à vérifier.
COURSE_NEGLIGEABLE = 0.05               # en hauteurs d'écran

#  Amorce et sortie : le corps du défilement est LINÉAIRE, avec seulement
#  0,3 s d'accélération à chaque bout. Un défilement entièrement lissé donne
#  une impression de flottement — mesuré, c'est le défaut le plus visible.
DEFILEMENT_AMORCE_S = 0.30


# ---------------------------------------------------------------------------
#  LE DÉCOUPAGE TEMPOREL (600 images, 30 im/s)
# ---------------------------------------------------------------------------
#  Deux montages sont fournis. Le premier est celui du cahier des charges.
#  Le second applique une trouvaille mesurée : montrer le RÉSULTAT dans la
#  première seconde fait passer le taux de visionnage complet de ~35 % à
#  58 % (+65 % de rétention). Le cahier des charges montre l'ancien site
#  pendant 2,5 s avant tout résultat — c'est exactement l'inverse.
#
#  On change de montage en changeant cette seule constante.

MONTAGE = "cahier"                      # "cahier" | "resultat_dabord"

_MONTAGE_CAHIER = {
    "ouverture": (0, 15),               # 0,5 s  carton client / secteur / année
    "teaser": None,                     #        (pas de teaser)
    "hook": (15, 90),                   # 2,5 s  accroche, ancien site immobile
    "avant": (90, 210),                 # 4,0 s  défilement de l'avant
    "bascule": (210, 270),              # 2,0 s  bascule 3D
    "apres": (270, 510),                # 8,0 s  défilement de l'après
    "sortie": (510, 585),               # 2,5 s  chiffre, sortie, logo, CTA
    "boucle": (585, 600),               # 0,5 s  retour au carton d'ouverture
}

_MONTAGE_RESULTAT = {
    "teaser": (0, 24),                  # 0,8 s  L'APRÈS, plein cadre, d'emblée
    "ouverture": (24, 39),              # 0,5 s  carton client / secteur / année
    "hook": (39, 99),                   # 2,0 s  accroche, ancien site immobile
    "avant": (99, 207),                 # 3,6 s  défilement de l'avant
    "bascule": (207, 261),              # 1,8 s  bascule 3D
    "apres": (261, 501),                # 8,0 s  défilement de l'après
    "sortie": (501, 585),               # 2,8 s  chiffre, sortie, logo, CTA
    "boucle": (585, 600),               # 0,5 s  retour au carton d'ouverture
}

TEMPS = _MONTAGE_CAHIER if MONTAGE == "cahier" else _MONTAGE_RESULTAT


# ---------------------------------------------------------------------------
#  LES INCRUSTATIONS
# ---------------------------------------------------------------------------
#  Une seule visible à la fois. Apparition par translation verticale courte
#  plus fondu, sur 6 images. Jamais de rotation, jamais de rebond : le
#  contenu du client bouge déjà, deux mouvements concurrents se mangent.

INCRUST_ENTREE = 6                      # images
INCRUST_MONTEE = 0.22                   # unités de translation à l'apparition
INCRUST_Y = -3.20                       # posée dans le bas de l'image
INCRUST_BANDE_HAUT = 1.30               # hauteur du voile, pleine largeur

#  Rien n'est jamais totalement immobile : les plans dits fixes gardent un
#  zoom lent de 2 % sur toute leur durée. Sans lui, l'œil décroche.
RESPIRATION = 0.02


# ---------------------------------------------------------------------------
#  LA BASCULE
# ---------------------------------------------------------------------------
#  L'appareil et son masque restent immobiles ; c'est le CONTENU qui pivote
#  à l'intérieur. Sous projection orthographique, une rotation autour de
#  l'axe vertical ne change pas la hauteur apparente : un masque fixe suffit
#  donc à contenir le débord du défilement pendant toute la bascule.

BASCULE_ECHELLE = 1.07                  # gonflement à mi-parcours
#  Pas de « recul en Z » : sous projection ORTHOGRAPHIQUE, éloigner un objet
#  de la caméra ne change strictement rien à sa taille à l'image. Le seul
#  moyen de suggérer la profondeur pendant la bascule est donc l'échelle.
#
#  Fractions de la respiration déjà parcourues à l'entrée et à la sortie de
#  la bascule : le gonflement s'INSÈRE dans le mouvement lent au lieu de le
#  couper net.
BASCULE_RESPIRATION = (0.40, 0.60)


# ---------------------------------------------------------------------------
#  LE CARTON DE SORTIE
# ---------------------------------------------------------------------------

LOGO_LARGEUR = 1.90
LOGO_Y = -4.95
NUM_Y = 3.05
NUM_LEG_Y = 1.25
SORTIE_Y = -0.60
CTA_Y = -2.80


# ---------------------------------------------------------------------------
#  LE CARTON D'OUVERTURE
# ---------------------------------------------------------------------------

OUV_CLIENT_Y = 1.55
OUV_SECTEUR_Y = 0.20
OUV_ANNEE_Y = -0.80
HOOK_Y = INCRUST_Y                      # même bandeau que les incrustations

#  Qui porte quelle couleur. « Avant » en blanc neutre, « après » en violet :
#  l'œil apprend l'association en deux secondes et n'a plus besoin de lire
#  une étiquette « AVANT » / « APRÈS ».
COUL_CLIENT = BLANC
COUL_SECTEUR = GRIS
COUL_ANNEE = GRIS
COUL_HOOK = BLANC
COUL_AVANT = BLANC
COUL_APRES = VIOLET
COUL_NUM = VIOLET
COUL_NUM_LEG = GRIS
COUL_SORTIE = GRIS
COUL_CTA = BLANC
COUL_LOGO = BLANC


# ---------------------------------------------------------------------------
#  RENDU
# ---------------------------------------------------------------------------

ECHANTILLONS = 16
TRANSFORMATION_VUE = "Standard"
#  Blender applique AgX par défaut : il délave les captures d'écran et fausse
#  les couleurs d'interface. Une capture doit ressortir exactement comme à
#  l'écran, donc « Standard », et matériaux en émission pure de force 1 pour
#  que l'écran ne dépende d'aucun éclairage de la scène.
EMISSION_FORCE = 1.0

CRF = 18
ENCODEUR = "libx264"
FORMAT_PIXEL = "yuv420p"


# ---------------------------------------------------------------------------
#  VALIDATION DE LA CONFIGURATION
# ---------------------------------------------------------------------------

POINTS_ATTENDUS = 3
LONGUEUR_POINT = 42
LONGUEUR_HOOK = 60


def secondes(images):
    return images / float(IMAGES_PAR_SECONDE)


def images(secondes_):
    return int(round(secondes_ * IMAGES_PAR_SECONDE))


# ---------------------------------------------------------------------------
#  L'EMPILEMENT DES PLANS
# ---------------------------------------------------------------------------
#  La caméra est orthographique et regarde vers les Z décroissants : la
#  profondeur ne sert donc QU'À l'ordre d'empilement, jamais à la taille.
#
#  Les écrans doivent rester très en retrait du masque : pendant la bascule,
#  un plan de 5,6 unités de large qui pivote autour de son axe vertical
#  balaie ± 2,8 unités en profondeur. Sans cet écart il traverserait le
#  masque et le débord du défilement réapparaîtrait en plein milieu.

Z_FOND = -8.0
Z_ECRAN = 0.0
Z_MASQUE = 5.0
Z_APPAREIL = 5.3
Z_VOILE = 5.8
Z_TEXTE = 6.0
Z_CAMERA = 14.0
