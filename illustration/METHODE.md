# Illustration vectorielle en aplats + grain — la méthode

Ce dossier contient la chaîne complète qui engendre une illustration plate
grainée, dans le style de la référence client, entièrement par script et
ouvrable dans Inkscape.

Ce fichier existe pour une raison précise : **ne pas recommencer**. Chaque
règle ci-dessous a coûté au moins un aller-retour raté.

---

## La règle de travail

**Un découpage se donne en fractions, pas en pixels.** `PART_CIEL`,
`PART_SABLE`, `PART_MER` dans `construire.py` : l'horizon, le haut du sable et
la ligne moyenne de la vague en découlent tous. Changer une fraction suffit,
il n'y a aucun nombre à rattraper à la main ailleurs.

**Par paliers.** Un élément à la fois, rendu isolé, validé, puis intégré.
`essai_parasol.py` est le patron de ce genre de banc d'essai : il importe les
filtres de `construire.py` pour que ce qu'on juge soit exactement ce qui ira
dans l'image.

**Mesurer, pas supposer.** Le grain se juge à l'écart-type, pas à l'œil.
Et la fenêtre de mesure doit être *cherchée*, pas fixée : une fenêtre posée
au hasard tombe à cheval sur une couture et rend 69 niveaux au lieu de 4.

```python
def vert(p):
    r, g, b = p
    return g > r + 25 and g > b + 25       # tolérant au grain
# on balaie jusqu'à trouver un carré dont les 4 coins ET le centre sont verts
```

**Un banc d'essai doit montrer l'élément dans son cadre réel.** La vague a
été jugée dans des bandes de 420 px : l'épaisseur du bleu n'y voulait rien
dire, et elle paraissait juste alors qu'elle était deux fois trop plate. Une
proportion ne se juge qu'au format final.

**Ne jamais estimer une grandeur qu'on peut mesurer.** Pour la vague, la
longueur d'onde avait été mesurée et l'amplitude estimée à l'œil : une onde
de bonne période mais trop plate se lit comme un bord bombé, pas comme une
vague.

**Relever le modèle avant de dessiner.** Quatre planches de variantes de
parasol ont été produites sans que l'image de référence soit consultable :
aucune ne ressemblait au modèle. La bonne forme a été trouvée en dix minutes
une fois l'image sous les yeux.

---

## Ce que la référence nous a appris

| | |
|---|---|
| **Parasol** (4ᵉ référence, retenue) | une **toile tendue en pointe**, pas un dôme : pentes presque droites (flèche ≈ 0,1 × la hauteur), sommet pointu, ry/rx = 0,61. 4 fuseaux par azimut (crème étroit / vert sombre / vert clair / crème), jupe à festons de 0,17 ry en tons **assombris** — l'intérieur de la toile vu par en dessous. Mât penché d'un bloc, l'angle découle du relevé. |
| **Parasol** (1ʳᵉ référence, conservé en code) | un **éventail** : demi-lune en secteurs égaux issus du milieu du bord droit — `un_eventail()`. |
| **Bord bas** | une **droite** franche. Pas de feston, pas de vaguelette. |
| **Contours** | **aucun**. Pas de liseré, pas de couture tracée, pas d'embout. Les secteurs ne sont que des changements de couleur. |
| **Secteurs** | nombre **impair**, ce qui met la couleur pleine aux deux extrémités. |
| **Mât** | droit, perpendiculaire au diamètre, ~0,95 × le rayon, très fin (~1/22 du rayon). |
| **Inclinaison** | ~34°, le mât partant vers le bas à droite. |
| **Grain** | **un seul calque sur toute l'image**, même densité et même taille de point partout — y compris sur le sable. Points d'environ 3 px. |
| **Composition** | ciel **30 %**, sable **44 %**, mer **26 %**, mesuré sur 760 px de haut. Pas de bande de verdure. |
| **Parasol, nombre** | **un seul**, planté dans un coin. Deux de part et d'autre du sujet font une composition en balance que le modèle ne fait pas. |
| **Mer** | crête à y=562 sur 760, soit **26 % de la hauteur**. Ligne moyenne à **0,78 × H**. |
| **Vague** | **3 ondulations** dans le cadre, amplitude ± 58 sur 1800, soit une raideur de 0,19. |
| **Serviette** | un **rectangle** de 0,40 × 0,15 du cadre, incliné de 1,5° à peine, **pourtour blanc extérieur**. Aucune fuite : l'image est plate. |
| **Placement** | parasol ancré à (0,105 W ; 0,312 H) — **juste sous l'horizon, toile dans le ciel**. Serviette centrée à (0,263 W ; 0,414 H). |
| **Haie** (2ᵉ référence) | masse pleine, ciel **54 %**, haie **27 %**, sable **19 %**. Touffes de **12 à 22 px** sur 1800 — 3,3 fois plus petites que l'ancien buisson. |
| **Serviette rayée** (5ᵉ référence) | **relevée coin par coin** : près-gauche (722, 836), près-droit (938, 830), loin-droit (955, 782), loin-gauche (762, 786) sur 1232×928. Elle fuit **vers la droite** — extrémités obliques (39°), hauteur 94 px à gauche contre 74 à droite. Chaque rayure est un **quadrilatère interpolé** entre bord près et bord loin : convergence, resserrement et amincissement **découlent** des coins, ce ne sont pas des réglages. |
| **Verge + coins d'herbe** | construits sur un contresens (« le vert au sol » désignait la serviette), **éteints** (`AVEC_SOL_VERT = False`) mais conservés dans `herbe.sol_vert()`. |
| **Herbe pleine largeur** (3ᵉ référence) | retirée : elle fermait l'image comme un muret. `AVEC_HERBE`. |
| **Personnages** (5ᵉ référence) | des **silhouettes** : une couleur corail, aucun visage, un accent par figure (short, haut clair). Toute la lecture est dans la **posture**. Membres fuselés + lissés, ballon en croissants par booléens, serviette rayée en bandes pleines. |
| **Nuages** | rapport **5,8 : 1** — six fois plus larges que hauts. Mesuré sur les trois : 170×30, 145×25, 140×24. Bas rigoureusement droit. |

### Le grain : un seul calque, posé sur tout

`GRAIN_GLOBAL = True`, `GRAIN_FINESSE = 0.28`, `GRAIN_FORCE = 0.90`.

Mesuré au même réglage sur toute l'image : ciel **20,6**, haie sombre
**18,2**, sable **20,8** niveaux d'écart-type. C'est l'unité qu'aucun réglage
par matière n'atteignait.

**Le grain n'était pas trop faible, il était trop FIN.** `baseFrequency` est
en unités de dessin : 1,2 donne des points de 0,83 px, sous la résolution de
l'œil, et un bruit trop fin se moyenne et disparaît. La référence a des
points d'environ 3 px, soit une fréquence de 0,3.

Au-delà de `GRAIN_FORCE` ≈ 1,3 la mesure ne bouge plus : 20,2 à 1,30 comme à
1,80. La table `feFuncA` sature.

Les filtres par matière restent dans le fichier mais sont mis en veille
automatiquement quand `GRAIN_GLOBAL` est vrai.

---

## Les pièges vérifiés, pas supposés

**`soft-light` n'existe pas dans Inkscape 1.2.** Le grain y disparaît
complètement — écart-type mesuré à 0.00. Utiliser `overlay`.

**Au-delà de `baseFrequency` ≈ 1.6, le bruit s'annule.** Il passe sous la
résolution de rendu. Mesuré à 0.00 partout à 2.0.

**Un filtre dans un groupe tourné se calcule dans l'espace tourné**, et
Inkscape le rend alors par bandes. D'où l'absence totale de
`transform="rotate()"` : les rotations sont calculées sur les coordonnées.

**La commande `A` de SVG ne se pilote pas.** Elle prend des rayons et des
drapeaux, pas une paramétrisation : entre deux points, deux ellipses de
mêmes rayons passent. Pire, si les rayons sont trop petits pour joindre les
deux points, la norme impose de les **agrandir silencieusement**. Utiliser
`parasols.cubiques()`, qui rend un arc d'ellipse quelconque en cubiques
exactes à partir de `P(t) = centre + U·cos t + V·sin t`.

**Inkscape rend ses chemins en relatif**, et un `m` minuscule *en tête de
chemin* est malgré tout absolu. Tout ce qui sort d'Inkscape passe donc par
`booleen.absolu()` avant d'être replacé.

**`trace.fusele()` produit des segments droits.** Un torse sortait en
polygone à 52 côtés — c'est ce qui donne l'aspect « fait à la souris ».
Passer par `booleen.lisser()`, qui appelle *Chemin > Simplifier*.

**Une bosse faite d'un cercle ne peut pas s'aplatir.** Un cercle n'a qu'une
dimension : dès qu'il dépasse, il gonfle. Les nuages étaient une barre
surmontée de cercles, d'où un rapport de 2,6 : 1 impossible à corriger. Il
faut des **ellipses**, et il faut qu'elles se **chevauchent** — sinon on
obtient une file de bulles au lieu d'une crête.

**Le nombre de motifs vus ne doit pas dépendre d'où tombe le cadre.** La
phase de la vague est calculée pour poser un creux sur chaque bord : on voit
alors exactement `CRETES` ondulations entières. Avec une phase libre, un bout
de crête dépassait à droite et on en comptait quatre.

**Une vérification qui ne peut pas échouer ne vérifie rien.** `eroder()`
dilatait au lieu de réduire — normale intérieure prise à l'envers — et le test
mesurait une distance **non signée** : il affichait fièrement 19,00 px sur les
quatre côtés, du mauvais côté. Il compare maintenant les **aires**, qui
portent le signe.

**La perspective d'un parasol tient dans son rebord.** Le rebord est un
cercle ; vu d'un peu plus bas que la toile, il se projette en ellipse et son
avant **descend sous la ligne des pointes** — de 0,15 rx sur le modèle. Un
bord rectiligne = une toile vue exactement de profil, à plat. La jupe suit le
même arc : chaque point des festons est décalé de la même quantité sous
`y_bord(x)`.

**À encombrement égal, un dôme rond a l'air plus gros qu'un cône.** Les
coupoles en quarts d'ellipse paraissaient disproportionnées alors que rx et
ry étaient justes : le modèle est une toile **tendue** — pentes presque
droites, sommet en pointe. Chaque méridien est une quadratique dont le
contrôle est à peine au-dessus de la corde.

**Le modèle décide, pas la règle générale.** La serviette avait été construite
en trapèze fuyant au nom du « rectangle à angles droits = plaque dressée ».
C'est vrai dans une image en perspective ; celle-ci n'en a pas. Une forme
fuyante au milieu d'une image plate ne fait pas plus vrai, elle fait faux.

**Un liséré intérieur n'est pas une homothétie.** Réduire une forme vers son
centre rapproche d'autant plus les bords qu'ils sont loin du centre : la marge
serait plus large en haut qu'en bas, et sur une forme en perspective ça se
voit. `serviette.eroder()` décale chaque côté de la même distance le long de
sa normale puis recoupe les côtés voisins — marge constante, vérifiée à
22,00 px sur les quatre côtés.

**Deux aplats de même couleur qui se touchent ne font plus deux objets.** La
serviette posée sous le parasol se fondait avec lui. Ce n'est pas une
question de teinte mais de contact : sur le modèle c'est le sable entre les
deux qui les sépare.

**Un seul rang de touffes garde une ligne moyenne visible.** Même semé au
hasard, l'œil la reconstitue et la frange redevient une frise. Il en faut
**deux**, décalés en hauteur et tirés indépendamment.

**Un filtre de bruit ajoute du grain ; il n'ajoute pas de feuilles.** Le
corps de la haie restait deux aplats nus sous le grain — de loin, deux bandes
vertes. Il lui fallait des **mouchetures semées dans la masse** : ~1 850
petites taches, et c'est ce piquetage, pas le filtre, qui fait la matière.

**Une silhouette se lit par sa posture, pas par ses détails.** Le premier
enfant détaillé (deux tons de peau, coiffure, ourlets) avait échoué ; les
figures de la référence marchent parce qu'elles n'ont *qu'une* couleur et
*un* accent. Ce qui les rend reproductibles par le code : le coureur est
trois obliques parallèles (torse, jambe arrière, bras tendu), l'assis est un
angle (torse penché contre genoux relevés), et le bras d'appui doit être
plus fin et plus court que les jambes, sinon il en devient une troisième.

**Un ballon de plage est fait de croissants, pas d'une croix.** Deux bandes
en intersection donnent une croix de pharmacie ; le cercle **moins** le même
cercle décalé donne le croissant, dont le bord est le bord du ballon par
construction.

**L'herbe est faite de traits, la haie de masses.** Même vocabulaire — des
formes semées sur une graine fixe — mais la forme élémentaire change tout :
un brin est une quadratique courbée, pas un disque. Un brin raide est un
bâton.

**Un bord d'herbe est un duvet, pas un peigne.** Premier essai : brins de
0,3–0,6 fois la bande, espacés de 9 px — chaque dent lisible une à une. La
référence fait court (≈ 0,1–0,25 de la bande) et dense (≈ 4,6 px). C'est la
proximité des brins qui fait la matière, pas leur taille.

**La serviette, lue lentement.** Quatre faits, dans l'ordre : les rayures
suivent la **longueur**, parallèles aux grands bords, fines et serrées ;
l'obliquité est portée par les **extrémités** (coupées à ~39°) et le
décalage du bord loin, pas par l'axe, qui est presque horizontal ;
l'ondulation vit **dans les rayures**, qui serpentent avec le pli
puisqu'elles le traversent ; et la finition tient à deux détails — les
**lisières** unies le long des grands bords, et une **ombre fine sous le
bord près**, l'épaisseur du tissu, sans laquelle la serviette est peinte
sur le sable au lieu d'être posée dessus. Le passage par des bandes
transversales était une surinterprétation.

**Un effet décrit n'existe que s'il se mesure sur le rendu.** La bosse à
5 px sur un tapis de 70 et l'ombre à 30 % sous le grain : je décrivais un
relief que le PNG ne montrait pas — plusieurs tours durant. Deux seuils
payés : un accident de surface se voit à partir d'≈ 1/7 de la hauteur de
l'objet, et une ombre doit survivre au grain qui la recouvre. La
vérification se fait au pixel sur le rendu (bord relevé colonne par
colonne : bosse mesurée à 12 px), jamais en relisant le code.

**Un pli est une bosse, pas une onde.** Une sinusoïde met ses crêtes où ses
phases les posent — la nôtre tombait à côté du milieu — et elle descend
autant qu'elle monte, ce qu'un tissu posé ne fait pas : il se soulève, il ne
s'enfonce pas sous le sable. Le champ de plis est une somme de **bosses
gaussiennes vers le haut**, la principale placée où on la veut (au milieu),
plus haute sur le bord près que sur le bord loin. Et c'est **l'ombre du
flanc** qui transforme la montée des lignes en relief : sans elle les
rayures ondulent, avec elle le tissu bombe.

**« Au milieu du parasol » veut dire : le centre de l'objet sous le mât.**
Pas son bord, pas son coin d'ancrage, pas « à côté du pied » — son **centre
géométrique** à l'aplomb du bâton. L'ancre d'un objet relevé par ses coins
n'est pas son centre : il faut calculer le centre des quatre coins et le
caler sur le mât, puis le **mesurer sur le rendu** (mât à x = 1512, sommet
de la bosse à 1504, centre du tissu à ≈ 1500). Et comme la bosse principale
est à u = 0,5, centrer le tissu place le pli sous le mât par construction —
les deux exigences n'en font qu'une.

**Le mât ne se plante pas derrière la serviette : il se coupe dessus.**
Arrêter le trait au bord du tissu racontait une serviette posée *au pied*
du parasol. Sur la référence le mât continue **par-dessus** les premières
rayures et s'arrête **net** au premier tiers de la profondeur (relevé :
18 px sur 54) — pas de pied, pas d'embase, un trait coupé
(`stroke-linecap="butt"`). C'est un effet stylisé assumé de l'image.
Techniquement : un second segment sur la même droite, dessiné *après* la
serviette (`parasols.mat_sur_serviette`), qui repart 12 px en amont du pied
pour une couture invisible ; c'est la serviette qui donne le y du tiers,
pli compris (`personnages.serviette_coupe_mat`).

**Un tissu, c'est du désordre cohérent.** Les rayures droites faisaient un
carrelage ; le mouvement juste est UN SEUL champ de plis d(u), commun au
contour et aux neuf rayures — c'est le même pli qui les soulève toutes.
Éteint aux extrémités pour que les coins relevés restent en place. Et
l'amplitude juste est celle qu'on remarque à peine : à 4 px la serviette
flottait comme un drapeau, à 1,5 px elle repose. Même famille que la houle
de la haie et le vent de l'herbe : le mouvement est global, le détail local.

**Un relevé tronqué par un personnage décrit un autre objet.** Le premier
relevé de la serviette s'arrêtait à l'homme assis : il mesurait la partie
visible à sa gauche et prenait le bord de l'homme pour le bout du tissu —
résultat, une bande plate de 315 × 74, une serviette vue par la tranche.
En balayant les rayures de **toute** la zone (filtre : du crème à moins de
6 px, pour ne pas gober le short), la serviette continue sous le couple :
un **losange** de 407 × 84 dont le coin caché se reconstruit par
parallélogramme (N = W + E − S, vérifié : les deux grands bords portent le
même vecteur). On voit le *dessus* du tissu, pas sa tranche — c'était toute
la perspective qui manquait, et aucun réglage de plis ne pouvait la
remplacer.

**Une perspective se relève coin par coin, elle ne s'ajuste pas par
paramètres.** Trois essais de perspective sur la serviette (biais seul, puis
fuite + compression réglées à l'œil) avant de relever les quatre coins du
modèle et d'interpoler tout le reste entre eux. Donner la géométrie, pas ses
conséquences — comme le découpage en fractions.

**Une trame se relève, elle ne s'interprète pas.** La serviette a été faite
trois fois : bandes vertes pleines (tapis à moitié vert), puis tirets épars
sur fond crème (crème tamponné de vert), avant de regarder vraiment : des
rayures **continues, fines, serrées**, à trame égale vert/blanc. Compter les
rayures du modèle aurait évité les deux premiers essais.

**Le vent est global, le fouillis est local.** Les brins penchent tous du
même côté — un biais commun de 0,30 rad — avec leur désordre individuel
par-dessus, exactement comme la houle de la haie porte le frisottis.

**Une ombre portée appartient au sol qui la reçoit.** Les ombres des
parasols remontaient sur la verge : une ombre posée sur l'herbe du fond
raconte une fausse profondeur. `parasols.OMBRE_Y_MIN`, calé par
`construire.py` sous la verge.

**Des brins à hauteur fixe font des rangs de poireaux.** Deux appels à
hauteur fixe dessinaient deux rangées visibles. Le pied de chaque brin est
tiré au hasard dans la bande.

**Les taches vont par grappes, pas une à une.** Un semis uniforme se lit
comme du bruit ; le feuillage va par paquets. On tire des centres de grappe,
puis trois à huit taches autour de chacun, dans une ellipse couchée — le
feuillage s'étale en largeur, pas en hauteur. Même nombre total, tout autre
dessin.

**Une frange, même désordonnée, reste posée sur une règle.** Le frisottis est
un désordre local ; à grande échelle la crête de la référence respire —
quelques pixels de dérive sur des longueurs de plusieurs centaines. `houle()`
ajoute cette dérive, la **même** pour la crête et pour la limite intérieure :
une haie taillée garde une épaisseur constante, ses deux lignes respirent
ensemble.

**Des taches trop discrètes ne font rien du tout.** Premier essai avec des
tons à peine différents de leur fond : 700 taches invisibles. Sur la référence
elles **tranchent** ; ce sont leur petitesse et leur nombre qui les empêchent
de faire des confettis, pas leur discrétion.

**Une frange se règle par la taille des touffes, pas par leur désordre.**
L'ancien buisson avait des lobes de 38 à 74 px : de grosses boules, une frise
de nuages verts. À 12–22 px et trois fois plus nombreux, la même construction
donne du feuillage.

**Une forme posée sur une ligne doit y être tangente.** Les bosses des
nuages débordaient sous la ligne de pose et le dessous devenait bosselé :
demi-hauteur égale à la moitié de l'élévation, centre remonté d'autant.

**Le sable est à `#FAFAF6`, la toile blanche à `#FBFCFA`** : un point
d'écart. Un objet blanc posé sur le sable disparaît. Dans la référence les
parasols se détachent toujours sur le ciel.

---

## Ce qui existe en ligne de commande, et ce qui n'existe pas

Vérifié sur Inkscape 1.2.2 :

```
path-union   path-difference   path-intersection   path-cut
path-division   path-exclusion   path-simplify        →  OK
outset   offset   stroke-to-path                      →  N'EXISTENT PAS
```

Les décalages de contour restent donc à la charge de `trace.py`.

---

## Les fichiers

| fichier | rôle |
|---|---|
| `construire.py` | le chef d'orchestre. Format, découpage, palette, filtres de grain. |
| `perspective.py` | l'interrupteur `FRONTAL`. Vue de face ou point de fuite. |
| `haie.py` | la haie taillée, relevée sur la 2ᵉ référence (`AVEC_HAIE`) |
| `herbe.py` | la bande d'herbe du premier plan (`AVEC_HERBE`) |
| `verdure.py` | l'ancien buisson à gros lobes, retiré (`AVEC_VERDURE`) |
| `mer.py` | la mer et sa vague, retirée (`AVEC_MER`) |
| `serviette.py` | la serviette, retirée (`AVEC_SERVIETTE`) |
| `grillage.py` | la clôture (retirée de la version validée) |
| `nuages.py` | les nuages, au rapport du modèle |
| `parasols.py` | `un_eventail()` — la forme du modèle. `un_parasol()` — l'ancienne coupole à fuseaux, conservée. |
| `enfant.py` | l'ancien enfant détaillé, retiré (`AVEC_ENFANT`) |
| `personnages.py` | les silhouettes de la 5ᵉ référence : creuseur, coureur au ballon, couple sur serviette rayée (`AVEC_PERSONNAGES`) |
| `trace.py` | l'épaisseur variable, l'équivalent calculé du *Power Stroke* |
| `booleen.py` | union / différence / intersection / simplification, calculées par Inkscape |
| `importer_figure.py` | greffer un personnage téléchargé et l'accorder à la palette |
| `essai_parasol.py` | le banc d'essai — à copier pour régler un autre élément |
| `essai_nuage.py` | le banc des nuages : les anciens en haut, les nouveaux en bas |
| `essai_vague.py` | le banc de la vague, au format réel |

---

## Construire

```
python construire.py            ->  scene.svg              (avec le grillage)
python construire.py sans       ->  scene_sans_grillage.svg
inkscape --export-type=png --export-filename=sortie.png -w 1800 scene_sans_grillage.svg
```

**Le script ne réécrit jamais un fichier modifié à la main.** Il garde son
empreinte dans `.empreintes.json` ; si elle ne correspond plus, il s'arrête
et pose sa version à côté sous `*_nouveau.svg`.

**Un fichier `personnage.svg` posé à côté remplace l'enfant codé**, tel quel,
sans être relu. Le décor se calcule, le personnage se dépose.

Les booléens sont mis en cache dans `booleens.json`, indexés par le contenu
des formes. Efface-le pour tout recalculer.
