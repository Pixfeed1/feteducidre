# Le film du logo PIXFEED — méthode

Animation 3D du logo Pixfeed, faite sous Blender en Python, sans interface :
tout est écrit, tout est mesuré, tout est reproductible par une commande.

    ./rendre_30s.sh      le film de trente secondes (900 images, 1080×1920)
    ./rendre_plat.sh     la version courte de huit secondes

Aucun fichier `.blend` n'est versionné : le script EST la scène. On relance,
on obtient exactement la même image.

---

## Le principe

Un champ de lettres — le mot PIXFEED répété des centaines de fois — occupe
tout le cadre. Le logo n'est pas *dessiné* : il **apparaît** parce qu'une
partie de ces lettres recule dans la profondeur, puis s'allume en violet.
Le spectateur voit une forme émerger d'une matière, pas un objet qu'on
pose devant lui.

2 279 lettres à l'écran, 470 d'entre elles composent la marque.

## Les seize temps

| image | temps  | ce qui se passe |
|-------|--------|-----------------|
| 3     | 0 s    | **naissance** — les lettres éclosent en spirale, du centre vers les bords |
| 50    | 1,7 s  | **houle** — une vague de profondeur traverse le champ en diagonale |
| 100   | 3,3 s  | **tourbillon** — tout le champ pivote d'un quart de tour, sur des arcs |
| 160   | 5,3 s  | **mosaïque** — quinze petits logos apparaissent, le fond claque en arrière |
| 210   | 7,0 s  | **plongeon** — le petit logo du centre **devient** le grand (raccord de forme) |
| 218   | 7,3 s  | **flash** d'impact |
| 270   | 9,0 s  | **courant** — une lettre s'allume et contamine ses voisines de proche en proche |
| 330   | 11,0 s | **pulsations** |
| 390   | 13,0 s | **disparition** — le champ s'envole sur des arcs et s'éteint |
| 465   | 15,5 s | **culbutes** — chaque lettre de la marque fait un tour sur elle-même, en vague |
| 540   | 18,0 s | **retour** — le champ revient en spirale, de plus loin |
| 615   | 20,5 s | **onde de choc** — un anneau part de la marque et pousse tout |
| 675   | 22,5 s | **grille** — trois battements de la marque entière |
| 750   | 25,0 s | **traversée** — la marque fonce vers l'œil et passe au-delà |
| 790   | 26,3 s | **reformation** — tout revient du fond, sur des arcs |
| 818   | 27,3 s | **signature** — la marque s'allume d'un coup, puis on la **tient** |
| 876   | 29,2 s | **effondrement** — du bord vers le centre ; la boucle se ferme sur le noir |

---

## Ce que j'ai appris, dans l'ordre où je me suis trompé

### 1. Le texte de Blender naît couché

Un objet texte est créé dans le plan du sol. Sans `rotation_euler =
(π/2, 0, 0)` les lettres sont des **tuiles vues en raccourci** : c'est ce
qui donnait ce champ « en arc de cercle » qu'on m'avait reproché. Le
problème n'était pas la caméra, c'était l'orientation des glyphes.

### 2. On ne vise pas une caméra à la main

Calculer les angles d'Euler pour pointer un objet introduit toujours un
**roulis**. On utilise une contrainte `TRACK_TO`, ou — comme ici, la caméra
étant strictement frontale — on impose `(π/2, 0, 0)` et on ne bouge que la
position. Une caméra de face doit être *vraiment* de face.

### 3. `me.materials.clear()` après `bm.to_mesh()` remet tous les indices à zéro

Trois tentatives ratées avant de trouver ça. Les faces latérales de
l'extrusion se rendaient claires alors que je leur assignais un matériau
sombre. Ni `f.tag` (recopié par l'extrusion) ni `id()` sur un élément bmesh
(les enveloppes Python sont recréées à chaque accès) ne permettent de
suivre une face. La cause réelle : **les emplacements de matériaux doivent
être posés AVANT `to_mesh`**. Vérifié à la mesure : 30,8 % de pixels clairs
→ 6,5 %.

### 4. La profondeur de champ se calcule, elle ne se devine pas

À 28 mm et f/1.4, la zone nette va de 8 à 59 unités : *tout* était net, le
flou n'existait pas. Il a fallu descendre à **f/0.05**. Quand un réglage
optique ne produit rien, on fait le calcul avant de tourner le bouton.

### 5. La contamination doit se propager en huit voisins

En quatre voisins, le parcours en largeur s'arrêtait à 12 étapes : le pied
du logo n'est pas connexe en quatre. Huit voisins, plus un saut en arc vers
les morceaux séparés, et la cadence **calculée sur la durée totale de
traversée** plutôt que fixée à l'aveugle : 51 étapes, tout le logo s'allume.

### 6. Mesurer le cadre avant de rendre

La marge du champ était à 1,6 : 3 233 lettres calculées pour 2 100
visibles. **35 % du temps de rendu jeté par la fenêtre.** Marge ramenée à
0,70, échantillons de 12 à 10 → de 13,7 s à 9,2 s par image. On profile
avant de lancer deux heures de calcul, pas après.

### 7. Un film de logo se termine sur son logo

Première version du montage : entre l'image 782 et l'image 900 il ne restait
**rien** à l'écran. Quatre secondes de noir à la fin d'un film de trente.
D'où les trois temps ajoutés — reformation, signature, tenu — et la marque
qui est la **dernière** chose à s'éteindre.

### 8. L'étage de composition n'est pas une option

C'est ce qui manquait à toutes les versions que Michael a trouvées plates.
Quatre couches, toutes discrètes — c'est leur cumul qui fait l'image
professionnelle, jamais l'une d'elles poussée fort :

- **Fog glow** — le halo doux autour des lettres allumées ;
- **Streaks** — quatre branches de lumière anamorphiques, la signature
  « cinéma » du glare ;
- **Distorsion d'objectif** — une aberration chromatique légère, les bords
  se décomposent en couleurs comme dans un vrai objectif ;
- **Vignettage** — les coins s'assombrissent, l'œil revient au centre.

### 9. Les principes du mouvement, appliqués et pas récités

- **Anticipation** : quatre images de mouvement contraire avant chaque
  temps fort. Sans elle, un déplacement démarre « mort ».
- **Dépassement** (*ease out back*) : les positions et les échelles
  dépassent leur cible de 1,4 puis reviennent. Les rotations et les
  couleurs, elles, sont en **expo** — elles doivent claquer, pas rebondir.
- **Décalage court** : une image d'écart entre voisines. Plus, et la vague
  devient une traînée molle.
- **Arcs** : aucun déplacement en ligne droite. `arc()` décale le point de
  passage **perpendiculairement** au trajet, l'interpolation dessine une
  courbe.
- **Raccord de forme** : le petit logo du centre ne disparaît pas pour
  laisser la place au grand — il *devient* le grand, ses lettres s'écartant
  vers leur position finale pendant que la caméra plonge.
- **Durée** : le même mouvement en 6 images est nerveux, en 30 il est
  languide. Rien ici n'est laissé au hasard de la valeur par défaut.

### 10. Une seule matière pour 2 279 lettres

La couleur de chaque lettre est portée par sa **couleur d'objet**
(`ShaderNodeObjectInfo`), l'allumage étant déduit du canal vert. Un seul
matériau partagé, donc une seule compilation de nuanceur. La profondeur est
lue sur la position Y du monde — pas sur la distance radiale à la caméra,
qui assombrissait les coins de l'image.

---

## Les réglages qui comptent

    résolution      1080 × 1920 (9:16, Instagram)
    cadence         30 images/s, 900 images
    moteur          EEVEE, 10 échantillons, flou de bougé à 0,40
    objectif        24 mm de capteur vertical, f/0.05
    violet          (0.58, 0.26, 0.98), gain d'émission ×3
    fond            (0.038, 0.038, 0.050) — jamais du noir pur
