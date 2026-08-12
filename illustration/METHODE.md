# Illustration vectorielle en aplats + grain — la méthode

Ce dossier contient la chaîne complète qui engendre une illustration plate
grainée, dans le style de la référence client, entièrement par script et
ouvrable dans Inkscape.

Ce fichier existe pour une raison précise : **ne pas recommencer**. Chaque
règle ci-dessous a coûté au moins un aller-retour raté.

---

## La règle de travail

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

**Relever le modèle avant de dessiner.** Quatre planches de variantes de
parasol ont été produites sans que l'image de référence soit consultable :
aucune ne ressemblait au modèle. La bonne forme a été trouvée en dix minutes
une fois l'image sous les yeux.

---

## Ce que la référence nous a appris

| | |
|---|---|
| **Parasol** | un **éventail** : demi-lune en secteurs égaux en angle, tous issus du milieu du bord droit. Pas une coupole à fuseaux. |
| **Bord bas** | une **droite** franche. Pas de feston, pas de vaguelette. |
| **Contours** | **aucun**. Pas de liseré, pas de couture tracée, pas d'embout. Les secteurs ne sont que des changements de couleur. |
| **Secteurs** | nombre **impair**, ce qui met la couleur pleine aux deux extrémités. |
| **Mât** | droit, perpendiculaire au diamètre, ~0,95 × le rayon, très fin (~1/22 du rayon). |
| **Inclinaison** | ~34°, le mât partant vers le bas à droite. |
| **Grain** | la référence **charge les aplats saturés bien plus que ses fonds**. Le parasol est franchement moucheté là où le ciel reste lisse. |
| **Nuages** | rapport **5,8 : 1** — six fois plus larges que hauts. Mesuré sur les trois : 170×30, 145×25, 140×24. Bas rigoureusement droit. |

Réglage retenu : `grainToileVerte` **0.38**, `grainToileBlanche` **1.00**,
soit **11,9 niveaux** d'écart-type mesurés sur le vert (contre 3,9 quand on
l'avait calé sur le ciel).

Le rapport vert/blanc de 3,1 n'est pas arbitraire : un point clair sur du
blanc ne se voit pas, donc le blanc a besoin de plus de points pour rendre
la même matière.

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
| `verdure.py` | le buisson : deux rangs de lobes semés sur une graine fixe |
| `grillage.py` | la clôture (retirée de la version validée) |
| `nuages.py` | les nuages, au rapport du modèle |
| `parasols.py` | `un_eventail()` — la forme du modèle. `un_parasol()` — l'ancienne coupole à fuseaux, conservée. |
| `enfant.py` | l'enfant et ses jouets |
| `trace.py` | l'épaisseur variable, l'équivalent calculé du *Power Stroke* |
| `booleen.py` | union / différence / intersection / simplification, calculées par Inkscape |
| `importer_figure.py` | greffer un personnage téléchargé et l'accorder à la palette |
| `essai_parasol.py` | le banc d'essai — à copier pour régler un autre élément |
| `essai_nuage.py` | le banc des nuages : les anciens en haut, les nouveaux en bas |

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
