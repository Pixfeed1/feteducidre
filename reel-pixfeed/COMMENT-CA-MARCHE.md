# Comment cette vidéo est fabriquée

Ce document explique, de bout en bout, comment une commande produit un Reel de
vingt secondes. Il est écrit pour être lu six mois plus tard, quand on aura
oublié pourquoi telle constante vaut telle valeur.

Le `README.md` dit **quoi**. Celui-ci dit **comment** et surtout **pourquoi**.

---

## 1. L'idée en une phrase

On ne monte pas une vidéo. On remplit un moule.

Le moule — cadrage, typographie, durée, rythme, positions — ne bouge jamais
d'un client à l'autre. Ce qui change, ce sont deux captures d'écran, dix
lignes de texte et un chiffre. Tout ça tient dans un fichier JSON de trente
lignes.

C'est cette constance qui rend le fil Instagram reconnaissable : quelqu'un qui
a vu deux Reels PixFeed reconnaît le troisième avant d'avoir lu un mot.

---

## 2. La commande

```bash
make reel PROJECT=tenakoe
```

Elle enchaîne quatre programmes Python, dans cet ordre :

```
projets/tenakoe.json
        │
        ▼
  ① capture.py        Playwright pilote un vrai Chromium, capture les deux
        │             sites en pleine page → avant.png, apres.png
        ▼
  ② template.blend    la scène modèle, versionnée, jamais régénérée
        │
        ▼
  ③ build_reel.py     Blender ouvre le modèle, y met les deux images, écrit
        │             les textes, pose 400 clés d'animation, VÉRIFIE, et
        │             rend 600 images PNG
        ▼
  ④ encode.py         ffmpeg assemble les PNG en MP4, puis relit le fichier
        │             pour contrôler qu'il est conforme
        ▼
  out/tenakoe/reel.mp4
```

Environ 2 500 lignes de Python au total, dont un tiers de commentaires.

---

## 3. Le fichier de charte : `src/grammar.py`

**Aucune couleur, aucune durée, aucune position, aucune taille ne doit exister
ailleurs que dans ce fichier.** Un test le vérifie automatiquement : il
récupère toutes les constantes numériques de `grammar.py` et cherche leur
valeur écrite en dur dans les six autres fichiers. S'il en trouve une, la série
échoue.

Pourquoi cette discipline ? Parce que le jour où il faudra changer le violet de
la marque, ou raccourcir le carton d'ouverture, on veut modifier **une ligne**
et que ça s'applique à toute la série passée et future. Une valeur recopiée à
trois endroits, c'est trois occasions de rater le troisième.

### La convention d'unités

Un seul réglage rend toute la géométrie relisible :

> **1 unité Blender = 100 pixels de l'image finale.**

La caméra est orthographique et son `ortho_scale` vaut 19,20. Du coup :

```
x va de -5,40 à +5,40      (1080 px de large)
y va de -9,60 à +9,60      (1920 px de haut)
```

Toute la mise en page s'écrit donc en centièmes de pixel, sans conversion
mentale. Une position à `y = 1.55` est à 155 px au-dessus du centre. C'est
bête, et c'est ce qui fait qu'on relit le code six mois après sans calculette.

---

## 4. Étape ① — la capture (`src/capture.py`)

Playwright ouvre un Chromium en 390 × 844 avec un facteur d'échelle de 3 —
c'est-à-dire un téléphone moderne. Puis, **dans cet ordre précis** :

### a) On masque ce qui pollue

Une feuille de style est injectée pour cacher les bandeaux de consentement
(une trentaine de sélecteurs : OneTrust, tarteaucitron, Axeptio, Didomi,
Cookiebot…) et les parasites (chat, fenêtres de newsletter).

On masque **par CSS, jamais par un clic sur « accepter »** : le clic dépend de
la langue du bouton et casse dès que le site change de prestataire. Un
sélecteur, lui, tient.

La même feuille met toutes les animations à zéro seconde. Sans ça, une capture
pleine page attrape une animation à mi-course et fige un élément à moitié
transparent.

### b) On fait l'aller-retour

```python
# on descend écran par écran…
while y < hauteur:
    page.evaluate("window.scrollTo(0, %d)" % y)
    page.wait_for_timeout(120)
    y += pas
# …on attend en bas…
page.wait_for_timeout(2000)
# …et on remonte
page.evaluate("window.scrollTo(0, 0)")
```

**C'est le détail le plus important de tout le fichier.** Les sites modernes
chargent leurs images en différé, quand elles entrent dans le champ. Sans cet
aller-retour, la capture pleine page contient des blocs gris à la place des
photos. C'est l'erreur numéro un de ce genre d'outil.

### c) On repose les éléments flottants dans le flux

```javascript
if (getComputedStyle(el).position === 'fixed')  el.style.position = 'absolute';
if (getComputedStyle(el).position === 'sticky') el.style.position = 'relative';
```

Un élément en `position: fixed` n'est peint **qu'une seule fois** dans une
capture pleine page, à une hauteur arbitraire. On se retrouvait avec le
bandeau de cookies planté au milieu du site. En le reposant dans le flux,
l'en-tête remonte en haut, la barre d'appel descend en bas, chacun à sa place.

### d) On journalise la hauteur — et c'est un piège

`capture.json` note, pour chaque page, sa hauteur en **hauteurs d'écran**. Le
calcul du défilement en dépend entièrement.

Et voici le piège qui m'a eu :

> **La hauteur CSS d'un vieux site ne dit pas sa hauteur à l'écran.**

Un site sans balise `<meta viewport>` — c'est-à-dire tous les « avant » — est
mis en page par le navigateur mobile sur une largeur virtuelle de 980 px, puis
dézoomé pour tenir dans les 390 px réels. Sa hauteur CSS est comptée dans le
repère à 980 px de large. La lire telle quelle donnait **2,48 hauteurs d'écran
au lieu de 1,01** : un défilement deux fois et demie trop long, et toute la
comparaison de vitesse ruinée.

La hauteur se déduit donc du **rapport de la texture**, jamais de la hauteur
CSS :

```python
rapport_ecran = 844 / 390
hauteurs = (hauteur_texture / largeur_texture) / rapport_ecran
```

### e) On réduit

On capture à ×3 pour que le texte du site soit net, puis on redescend à
1120 px de large. L'écran ne fait que 560 px dans l'image finale : au-delà de
deux fois, c'est de la mémoire de texture pour rien.

---

## 5. Étape ② — la scène modèle (`template.blend`)

Vingt-trois objets, cinq matériaux. Le script de production ne les crée pas,
il les **remplit**.

| objet | rôle |
|---|---|
| `CAM` | caméra orthographique, strictement de face, ne bouge jamais |
| `BG` | le fond couleur d'encre |
| `DEVICE` | le cadre du téléphone |
| `PIVOT` | l'empty qui porte la bascule 3D |
| `SCREEN_BEFORE` / `SCREEN_AFTER` | les deux plans qui portent les captures |
| `SCREEN_MASK` | ce qui cache le débord du défilement |
| `VOILE_INCRUST` | le bandeau sombre sous les incrustations |
| `TXT_*` (14 objets) | tous les textes |
| `LOGO` | la marque PixFeed |

### L'empilement des plans

La caméra étant orthographique, **la profondeur ne sert qu'à l'ordre
d'empilement, jamais à la taille**. Un objet qu'on éloigne ne rétrécit pas.

```
z = +14,0   CAM
z =  +6,0   les textes et le logo
z =  +5,8   le voile
z =  +5,3   le cadre du téléphone
z =  +5,0   le masque
z =   0,0   les deux écrans
z =  -8,0   le fond
```

L'écart de 5 unités entre les écrans et le masque n'est pas décoratif :
pendant la bascule, un plan de 5,6 unités de large qui pivote autour de son
axe vertical **balaie ± 2,8 unités en profondeur**. Sans cet écart il
traverserait le masque et le débord du défilement réapparaîtrait en plein
milieu de l'image.

### Le masque, et pourquoi il peut rester immobile

C'est le petit théorème sur lequel repose toute la scène :

> Sous projection **orthographique**, une rotation autour de l'axe vertical
> laisse la hauteur apparente **inchangée** ; seule la largeur se comprime en
> cosinus.

Or le débord à masquer est purement **vertical** (c'est la page qui dépasse en
haut et en bas de l'écran). Donc un masque fixe suffit pendant toute la
bascule. On économise un objet, une hiérarchie de parentage, et une classe
entière de bugs.

Le masque est construit en quatre barres plus quatre éventails de coin, plutôt
qu'en un grand rectangle percé : relier un contour à quatre points à un
contour arrondi à quarante points demanderait un pontage, alors que quatre
barres et quatre éventails se posent directement et ne peuvent pas se vriller.

### Trois réglages qu'on oublie et qui coûtent cher

**1. La transformation de vue sur `Standard`.**
Blender applique AgX par défaut. AgX est un excellent rendu photographique —
et une catastrophe sur une capture d'écran : ça délave les blancs et fausse
les couleurs d'interface. Une capture doit ressortir **exactement** comme à
l'écran. Le test « couleurs » mesure ça : aplat source `#FBFAF6`, aplat rendu
`#FBFAF6`, **écart 0/255**.

**2. Les écrans en émission pure de force 1.**
Aucune lumière dans la scène. Un écran qui dépendrait de l'éclairage
ressortirait plus sombre ou plus chaud que le site réel — et la comparaison
avant/après deviendrait un mensonge sur les couleurs.

**3. L'espace colorimétrique de la texture sur `sRGB`.**
Une capture d'écran **est** une image sRGB. En « Non-Color », Blender la
traiterait comme des données linéaires et tout ressortirait beaucoup trop
clair.

---

## 6. Étape ③ — la construction (`src/build_reel.py`)

C'est le gros morceau : 680 lignes. Il fait six choses.

### a) Il pose les deux images

Il remplace l'image du nœud nommé `TEX` dans chaque matériau d'écran — **il ne
reconstruit pas le matériau**. Puis il remet chaque plan au rapport exact de sa
capture :

```python
hauteur = ECRAN_LARGEUR * hauteur_texture / largeur_texture
```

Un plan laissé au rapport du modèle écraserait ou étirerait la capture. Le site
du client apparaîtrait déformé — le seul défaut vraiment impardonnable dans un
avant/après.

Notez qu'on modifie les **sommets du maillage**, pas l'échelle de l'objet.
L'échelle sert à l'animation ; mélanger les deux rend les clés illisibles.

### b) Il écrit les textes, et les ajuste à la mesure

Blender ne sait ni couper les lignes automatiquement ni gérer une mise en forme
riche. Le retour à la ligne est donc décidé par le script, à un nombre de
caractères défini dans la charte.

Puis vient le point important :

```python
cu.body = texte
bpy.context.view_layer.update()
largeur = ob.dimensions.x          # la largeur RÉELLEMENT obtenue
if largeur > largeur_max:
    cu.size *= largeur_max / largeur
```

On **mesure** la largeur obtenue au lieu de la deviner au nombre de
caractères. « MMMMM » et « iiiii » ont le même compte et pas du tout la même
largeur. C'est ce qui garantit qu'aucun texte ne sort de la zone sûre, quel que
soit le nom du client.

### c) Il pose les clés d'animation

Environ quatre cents, réparties sur vingt objets. Trois mécanismes seulement.

#### Le défilement

C'est la règle d'honnêteté du format :

> **La vitesse est fixée en hauteurs d'écran par seconde, et ne dépend jamais
> de la longueur de la page.**

Une page courte est parcourue puis maintenue. Une page longue n'est pas
parcourue en entier. **On n'accélère jamais pour « remplir » le temps
disponible** : deux sites comparés à deux vitesses différentes, ça se voit, et
ça ment.

Le corps du mouvement est **linéaire**, avec seulement 0,3 s d'adoucissement à
chaque extrémité. Un défilement entièrement lissé donne une impression de
flottement — c'est le défaut le plus visible de ce genre de vidéo.

Et la longueur des amorces se **calcule**. Blender adoucit en sinus : sur une
amorce de durée `a` atteignant la vitesse `v`, la courbe `1 − cos(πx/2)` a une
pente finale de `π/2`, donc la distance parcourue vaut

```
marge = 2·v·a/π          et non v·a/2
```

Se tromper là-dessus décale le palier de 27 % et les deux plans ne défilent
plus à la même vitesse. Le script **relève** ensuite la vitesse de croisière
sur les clés réellement posées, et la compare à la consigne :

```
apres  : 4,82 hauteurs d'écran en 8,00 s   croisière 0,620 h/s
avant  : 0,72 hauteur d'écran en 1,38 s    croisière 0,620 h/s
```

#### La bascule

`PIVOT` tourne de 0° à 180° autour de l'axe vertical. Les deux écrans sont ses
enfants, et `SCREEN_AFTER` est posé à 180° dans le repère local — de sorte
qu'à l'arrivée sa rotation totale vaut 360° : il se présente à l'endroit, pas
en miroir.

Le basculement de l'un à l'autre ne demande **aucune clé de visibilité** :

```python
mat.use_backface_culling = True
```

À 0°, l'avant fait face à la caméra et l'après lui tourne le dos : l'après est
éliminé. À 180°, l'inverse. L'élimination des faces arrière fait tout le
travail toute seule.

L'appareil et le masque, eux, restent immobiles : c'est le **contenu** qui
pivote à l'intérieur du téléphone. C'est plus moderne à l'œil, et ça évite de
faire tourner le masque.

#### Les incrustations

Translation verticale courte plus fondu, sur six images. **Jamais de rotation,
jamais de rebond** : la capture derrière bouge déjà, deux mouvements
concurrents se mangent l'un l'autre.

Une seule incrustation visible à la fois, et un bandeau sombre dessous — sans
lui, un texte blanc sur une capture claire est illisible.

Le bandeau change de teinte selon la phase : sombre pour l'« avant », teinté
marque pour l'« après ». L'œil apprend l'association en deux secondes et n'a
plus besoin qu'on lui écrive « AVANT » et « APRÈS ».

### d) La couleur d'objet : un matériau pour vingt textes

Tous les textes partagent **un seul** matériau. La couleur et l'opacité sont
portées par la couleur de l'objet (`ob.color`), lue par un nœud *Object Info* :

```
Object Info ─── Color ──→ Emission ─┐
            └── Alpha ──→ Fac ──→ Mix Shader ──→ Output
                     Transparent ───┘
```

On anime donc l'apparition d'un texte sans jamais toucher au matériau, et les
vingt objets partagent un unique nuanceur.

**Attention** : la couleur d'objet est transmise **telle quelle** au nuanceur,
qui travaille en **linéaire**. Y écrire directement les valeurs sRGB de la
charte délavait tout — le violet `#9442FA` sortait en lavande, et le bandeau
censé assombrir le fond l'**éclaircissait**. Il faut convertir.

### e) Il ferme la boucle

L'image 599 doit être identique à l'image 0. Plutôt que d'espérer que chaque
piste ait bien été ramenée à la main à sa valeur de départ, on **contraint** :

```python
for fc in ob.animation_data.action.fcurves:
    depart = fc.evaluate(0)
    fc.keyframe_points.insert(599, depart)
```

Pour chaque courbe animée, on pose une clé sur la dernière image dont la
valeur est celle évaluée à l'image 0. Une piste oubliée est corrigée d'office
— **et signalée**, parce qu'une correction silencieuse cacherait un défaut
d'animation.

Résultat : `sha256` identique sur les pixels décodés des deux images.

### f) Il vérifie avant de rendre

Trois contrôles, tous **avant** de lancer les treize minutes de calcul :

1. **La zone sûre** — la boîte englobante de chaque texte, en coordonnées du
   monde, en tenant compte du décalage d'apparition (c'est pendant l'entrée
   que le texte est le plus bas).
2. **Les vitesses** — les deux paliers doivent être identiques au millième.
3. **La fermeture de boucle** — et la liste de ce qui a dû être corrigé.

Si un contrôle échoue, le script s'arrête en nommant l'objet et le
dépassement en pixels. Pas de troncature silencieuse.

---

## 7. Étape ④ — l'encodage (`src/encode.py`)

```bash
ffmpeg -framerate 30 -i frames/%04d.png -c:v libx264 -crf 18 \
       -pix_fmt yuv420p -movflags +faststart -an reel.mp4
```

On passe par une **séquence PNG**, pas par la sortie vidéo intégrée de
Blender. Trois raisons, toutes vérifiées à l'usage :

- un rendu interrompu se reprend là où il s'est arrêté ;
- on peut ouvrir l'image 348 et regarder ce qui cloche ;
- l'encodage se refait sans relancer treize minutes de calcul.

`-an` est volontaire : **aucune piste audio**. La musique s'ajoute dans
l'application Instagram au moment de publier — sur un compte professionnel,
c'est même la seule façon d'avoir une piste utilisable, la bibliothèque
commerciale n'étant pas accessible depuis un fichier importé.

Le script **relit ensuite le fichier** avec `ffprobe` et refuse de rendre la
main si la durée, le nombre d'images, la résolution, le format de pixel ou le
nombre de flux ne sont pas conformes. On ne fait jamais confiance à un
encodage sans le vérifier.

---

## 8. Les défauts que les mesures ont attrapés

Dix, tous trouvés par une mesure, aucun par relecture. Les trois plus graves
auraient produit une vidéo publiable **en apparence** mais fausse.

| ce qui n'allait pas | comment ça a été trouvé |
|---|---|
| **La carte se dé-basculait pendant les 8 s de l'« après »** — 105° au lieu de 180° à l'image 400, le site écrasé au tiers de sa largeur | le test « couleurs » ne retrouvait plus l'aplat de la page |
| **La hauteur CSS lue telle quelle** — 2,48 hauteurs d'écran au lieu de 1,01 | le contrôle de vitesse |
| **Le bandeau ne portait pas son texte** — le site passait de 128 à 58 seulement | mesure de pixels sur le rendu |
| La couleur d'objet est linéaire, pas sRGB | mesure : 24 au lieu de 6 sur 255 |
| Le logo sortait déchiqueté (règle pair-impair du SVG sur deux rectangles qui se chevauchaient) | inspection du rendu, puis vérification de l'union sur 360 000 points |
| Le bandeau de cookies planté au milieu de la capture | inspection de la capture |
| Le carton d'ouverture démarrait 22 px trop bas | le contrôle de fermeture de boucle |
| `TEXTE_LARGEUR` écrite en dur à 9,00 dépassait de 31 px à droite | le contrôle de zone sûre, sur un second projet |
| Le contrôle comparait la vitesse **moyenne** au lieu du **palier** | il refusait un défilement pourtant juste |
| Le test de boucle hachait les octets du fichier au lieu des pixels | il échouait avec « écart 0/255 » |

Deux enseignements :

1. **Les deux derniers sont des défauts du test, pas du code.** Un test qui
   échoue n'a pas forcément raison. Il faut aller regarder.
2. **Les trois premiers n'auraient jamais été vus à l'œil** sur une planche de
   vignettes. C'est pour ça qu'on mesure.

---

## 9. Faire un nouveau Reel

Copier `projets/exemple.json`, changer huit champs, lancer la commande.

```json
{
  "slug": "monclient",
  "client": "Nom du client",
  "secteur": "Son métier",
  "annee": 2026,
  "anonyme": false,
  "url_avant": "https://web.archive.org/web/2024id_/https://site.fr/",
  "url_apres": "https://site.fr/",
  "hook": "La phrase qui retient au défilement.",
  "avant": ["…", "…", "…"],
  "apres": ["…", "…", "…"],
  "chiffre": { "valeur": "1,1 s", "legende": "au chargement" },
  "sortie": "Refonte complète, site livré et maintenu.",
  "cta": "Votre site a plus de trois ans ? Écrivez-moi."
}
```

Contraintes **vérifiées** : exactement 3 entrées de chaque côté, 42 caractères
maximum par entrée, 60 pour l'accroche. Un dépassement arrête le script en
nommant la ligne fautive — jamais de troncature en silence.

Deux options utiles :

- `"anonyme": true` remplace le nom du client par son secteur ;
- `"flouter": [".mon-adresse"]` floute des éléments avant capture — aucune
  donnée personnelle, aucun identifiant ne doit se retrouver dans une
  publication ;
- `"masquer": ["#bandeau-maison"]` complète la liste intégrée des bandeaux de
  consentement, pour les cas qu'elle rate.

---

## 10. Changer l'allure de toute la série

Tout est dans `src/grammar.py`, et s'applique rétroactivement à tous les
projets.

| ce qu'on veut changer | la constante |
|---|---|
| le violet de la marque | `VIOLET` |
| la vitesse de défilement | `VITESSE_DEFILEMENT` (en hauteurs d'écran/s) |
| la taille du chiffre final | `T_NUM` |
| la place du téléphone | `APPAREIL_CENTRE_Y` |
| la répartition des vingt secondes | `_MONTAGE_CAHIER` |
| la police | déposer les `.ttf` dans `assets/fonts/` |

### Le montage : deux versions, une constante

```python
MONTAGE = "cahier"            # l'ancien site d'abord, comme spécifié
MONTAGE = "resultat_dabord"   # 0,8 s de l'APRÈS en ouverture
```

Les mesures publiées sur le format donnent **58 %** de visionnage complet
quand le résultat final apparaît dans les deux premières secondes, contre
~35 % pour une ouverture classique — soit **+65 % de rétention**. Or le
découpage d'origine montre l'**ancien** site pendant 2,5 s avant tout
résultat.

Les deux montages sont fournis. Les 600 images et la fermeture de boucle sont
préservées à l'identique dans les deux cas.

---

## 11. Vérifier que tout va bien

```bash
make test
```

Neuf critères, exécutables, qui rendent chacun un chiffre :

```
OK    mp4       un MP4 valide est produit sans intervention
OK    duree     20,000 s, 600 images, 1080x1920, aucune piste audio
OK    boucle    sha256 identique sur les pixels décodés
OK    zone      15 objets dans 1080 × 1420 px
OK    vitesse   palier identique à 0,620 h/s à hauteurs différentes
OK    couleurs  aplat source = aplat rendu, écart 0/255
OK    charte    57 valeurs, aucune recopiée ailleurs
ÉCHEC rendu     769 s, soit 12,8 min
OK    config    6 configurations fautives, 6 refusées
```

Un critère qui ne peut pas être évalué faute d'artefact n'est **pas** compté
comme réussi. Un test qui se tait quand il manque quelque chose ne sert à rien.

### Sur le seul échec

769 s pour 600 images, soit 1,28 s l'image, sur une machine **sans carte
graphique** où EEVEE rastérise en logiciel.

Le coût de l'anticrénelage a été profilé : il est linéaire, **60 ms par
échantillon et par image**. Passer de 16 à 8 échantillons ramènerait le rendu
à 6,5 min et ferait passer le critère — mais dégrade 6,5 % des pixels jusqu'à
84/255, et **93 % de cette perte tombe à l'intérieur de l'écran du site**,
c'est-à-dire sur ce que la vidéo est précisément censée montrer.

On garde 16 échantillons. On rend un chiffre au-dessus du seuil plutôt qu'une
image dégradée pour verdir un test.

---

## 12. Ce qui reste à faire sur ton poste

1. **Déposer les vraies polices** de la charte sous
   `assets/fonts/charte-Bold.ttf` et `charte-Regular.ttf`. Rien d'autre à
   toucher : elles sont chargées explicitement depuis le dépôt, jamais
   résolues depuis les polices système.
2. **Lancer `make reel PROJECT=tenakoe`** — la capture des vrais sites demande
   un accès réseau sortant que l'environnement où ce dépôt a été écrit ne
   fournit pas.
3. **Ouvrir `template.blend` dans Blender** si tu veux retoucher la scène à la
   souris. À partir de là, c'est le `.blend` qui fait foi ; le script de
   fabrication n'est plus à relancer.
