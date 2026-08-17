# Générateur de Reels « projet client » PixFeed

Une commande par projet client, une vidéo verticale de vingt secondes prête à
publier. Le contenant ne change jamais : même cadrage, même typographie, même
durée, même rythme, quel que soit le client. Seuls changent les captures, les
textes et les chiffres. C'est cette constance qui rend le fil reconnaissable.

```
make reel PROJECT=tenakoe     →  out/tenakoe/reel.mp4
make demo                     →  la chaîne complète sur un projet de démonstration
make test                     →  les neuf critères d'acceptation
```

Sortie : 1080 × 1920, H.264, yuv420p, 30 images/s, **20,000 s exactement**,
600 images, **sans piste audio**, **bouclée sans couture** — l'image 599 est
identique à l'image 0, au hash près.

---

## La chaîne

| étape | fichier | ce qu'elle fait |
|---|---|---|
| 1 | `src/capture.py` | Playwright : captures pleine page de l'avant et de l'après |
| 2 | `template.blend` | la scène modèle, versionnée, jamais régénérée par la production |
| 3 | `src/build_reel.py` | remplit le modèle, pose les clés, vérifie, rend la séquence |
| 4 | `src/encode.py` | ffmpeg : séquence PNG → MP4, puis relecture de contrôle |

`src/grammar.py` est **la charte** : couleurs, durées, positions, tailles.
Aucune de ces valeurs n'existe ailleurs — et un test le vérifie.

---

## Écarts assumés avec le cahier des charges

Quatre. Tous documentés dans le code, à l'endroit concerné.

**1. Le modèle est produit par un script, une fois.**
Le cahier demande un `template.blend` construit à la main dans l'interface.
La session qui a écrit ce dépôt n'avait pas d'interface graphique. Le modèle
est donc fabriqué par `src/faire_template.py`, **une seule fois**, puis
versionné comme un binaire. L'intention est respectée : `build_reel.py` ne
régénère jamais la scène, il la remplit. Le modèle redevient modifiable à la
souris dès qu'on l'ouvre sur un poste de travail — et c'est alors le `.blend`
qui fait foi.

**2. La zone sûre n'est pas symétrique.**
Le cahier demandait 250 px en haut et 250 px en bas, centré. Vérification
faite sur les guides Instagram 2026 : l'interface mange **280 à 320 px en
bas** (pseudo, légende, crédit audio), 108 à 250 px en haut, et surtout
**90 à 120 px sur la colonne de droite** — les boutons j'aime / commenter /
partager, que le cahier ne mentionnait pas. On garde la hauteur utile demandée
(1420 px) mais correctement répartie, et on protège la colonne de droite.
Réglé dans `grammar.py`, quatre constantes.

**3. Le moteur de rendu s'adapte à la version de Blender.**
Le cahier vise Blender 4.2 LTS et `BLENDER_EEVEE_NEXT`. Sur 4.0 et 4.1 ce nom
n'existe pas. Le script prend celui que la version présente sait ouvrir.

**4. Les polices livrées sont des remplaçantes.**
`assets/fonts/charte-Bold.ttf` et `charte-Regular.ttf` sont pour l'instant
Liberation Sans, métriquement compatible Helvetica. **Déposez les vraies
polices de la charte à ces deux noms** : rien d'autre à changer, aucun code à
toucher. Elles sont chargées explicitement depuis le dépôt, jamais résolues
depuis les polices système — le rendu doit être identique sur toute machine.

---

## Ce que la recherche a changé

**Montrer le résultat dans la première seconde.** Les mesures publiées sur le
format donnent 58 % de visionnage complet quand le résultat final apparaît
dans les deux premières secondes, contre ~35 % pour une ouverture classique :
**+65 % de rétention**. Or le découpage du cahier montre l'**ancien** site
pendant 2,5 s avant tout résultat. C'est exactement l'inverse.

Les deux montages sont donc fournis, et on passe de l'un à l'autre en changeant
**une constante** :

```python
MONTAGE = "cahier"            # le découpage du cahier des charges
MONTAGE = "resultat_dabord"   # 0,8 s de l'APRÈS en ouverture, puis le reste
```

Le montage `resultat_dabord` place 24 images de l'après en tête et rééquilibre
le reste ; les 600 images et la boucle sont préservées à l'identique.

**Le défilement garde un palier linéaire.** La littérature recommande un
lissage complet ; à l'usage c'est faux pour un défilement long — ça donne une
impression de flottement. Le cahier avait raison : corps linéaire, 0,3 s
d'amorce à chaque bout. Conservé tel quel.

---

## Ce que les vérifications ont attrapé

Chaque défaut ci-dessous a été trouvé par une mesure, pas par une relecture.

**La hauteur CSS d'un vieux site ne dit pas sa hauteur à l'écran.**
Un site sans balise `viewport` — c'est-à-dire tous les « avant » — est mis en
page par le navigateur mobile sur 980 px puis dézoomé pour tenir dans les
390 px de l'écran. Sa hauteur CSS est comptée dans le repère à 980 px. La lire
telle quelle donnait **2,48 hauteurs d'écran au lieu de 1,01** : un défilement
deux fois et demie trop long, et la comparaison de vitesse ruinée. On déduit
la hauteur du **rapport de la texture**, jamais de la hauteur CSS.

**La couleur d'objet de Blender est linéaire, pas sRGB.**
Y écrire directement les valeurs de la charte délavait tout : le violet
`#9442FA` sortait en lavande, et le bandeau censé assombrir le fond
l'**éclaircissait** — mesuré 24 au lieu de 6 sur 255. Après conversion, le
violet rendu est (146, 66, 247) pour une cible de (148, 66, 250), l'écart
restant étant l'anticrénelage des lettres.

**La règle de remplissage pair-impair du SVG faisait des trous dans le logo.**
La marque est définie par cinq rectangles ; deux d'entre eux se chevauchaient.
Sans conséquence pour le film du logo, fatal en SVG : chaque recouvrement
devenait un trou et la marque sortait déchiquetée. Les deux blocs ont été
raccourcis de la part déjà couverte par leur voisin — union vérifiée
rigoureusement identique sur 360 000 points d'échantillonnage.

**Un élément en `position: fixed` se pose au hasard dans une capture pleine
page.** On retrouvait le bandeau de cookies planté au milieu du site. Avant de
capturer, on repose tout dans le flux : `fixed` devient `absolute`, `sticky`
devient `relative`.

**Le carton d'ouverture démarrait 22 px trop bas.** Sans clé de position à
l'image 0, Blender maintient la valeur de la première clé posée — celle de la
remontée finale. Trouvé par le contrôle de fermeture de boucle.

**La vitesse moyenne n'est pas la vitesse de défilement.** Le premier contrôle
comparait la moyenne de la phase, amorces comprises, et refusait un défilement
pourtant parfaitement réglé (0,603 au lieu de 0,620). Ce qui doit être
identique d'un plan à l'autre, c'est le **palier**, relevé sur les clés
réellement posées.

**Une page qui tient dans un écran n'a rien à faire défiler.** C'est le cas
normal d'un vieux site dézoomé — et c'est précisément la preuve visuelle qu'on
cherche à montrer. On maintient la position, et le contrôle de vitesse le dit
au lieu d'échouer.

---

## Le fichier de configuration

```json
{
  "slug": "tenakoe",
  "client": "Tenakoe",
  "secteur": "Bureau d'études RGE",
  "annee": 2026,
  "anonyme": false,
  "url_avant": "https://web.archive.org/web/2024id_/https://tenakoe.fr/",
  "url_apres": "https://tenakoe.fr/",
  "hook": "Ce site n'avait pas bougé depuis six ans.",
  "avant": ["…", "…", "…"],
  "apres": ["…", "…", "…"],
  "chiffre": { "valeur": "1,1 s", "legende": "au chargement" },
  "sortie": "Refonte complète, site livré et maintenu.",
  "cta": "Votre site a plus de trois ans ? Envoyez-le moi.",
  "flouter": [".mon-adresse", "#compte-client"],
  "masquer": ["#bandeau-maison"]
}
```

Contraintes **vérifiées, jamais tronquées en silence** : exactement 3 entrées
de chaque côté, 42 caractères maximum par entrée, 60 pour l'accroche. Un
dépassement arrête le script en nommant la ligne fautive.

`anonyme: true` remplace le nom du client par son secteur et retire son logo.
`flouter` reçoit des sélecteurs CSS floutés avant capture — aucune donnée
personnelle, aucun identifiant ne doit se retrouver dans une publication.
`masquer` complète la liste intégrée de bandeaux de consentement.

---

## Les neuf critères d'acceptation

```
make test
```

| clé | critère |
|---|---|
| `mp4` | un MP4 valide est produit sans aucune intervention |
| `duree` | 20,00 s, 600 images, sans piste audio |
| `boucle` | l'image 0 et l'image 599 sont identiques (sha256) |
| `zone` | aucun texte hors de la zone sûre (boîtes englobantes) |
| `vitesse` | deux projets aux hauteurs différentes défilent au même palier |
| `couleurs` | l'aplat dominant d'une capture ressort inchangé du rendu |
| `charte` | aucune valeur de charte écrite en dur hors `grammar.py` |
| `rendu` | le rendu complet tient sous dix minutes |
| `config` | la validation refuse ce qu'elle doit refuser |

Un critère qui ne peut pas être évalué faute d'artefact n'est **pas** compté
comme réussi : il est annoncé « non évaluable » et fait échouer la série.

### Résultat mesuré sur le projet de démonstration

**8 critères sur 9.** Le seul qui échoue est `rendu`, et il est borné par la
machine, pas par le code : **769 s pour 600 images**, soit 1,28 s l'image.

Le coût de l'anticrénelage a été profilé : il est linéaire, **60 ms par
échantillon et par image**. Passer de 16 à 8 échantillons ramènerait le rendu
à 6,5 min et ferait passer le critère — mais dégrade 6,5 % des pixels jusqu'à
84/255, et **93 % de cette perte tombe à l'intérieur de l'écran du site**,
c'est-à-dire sur ce que la vidéo est précisément censée montrer. On garde 16
et on rend un chiffre au-dessus du seuil plutôt qu'une image dégradée.

Cette mesure a été prise sur une machine **sans carte graphique**, où EEVEE
tourne en rastérisation logicielle. Sur un poste de travail équipé d'un GPU,
le même rendu est d'un tout autre ordre de grandeur — mais ça n'a pas pu être
vérifié ici, donc ce n'est pas présenté comme acquis.

Le critère `couleurs` passe avec un **écart de 0/255** : l'aplat `#FBFAF6`
de la page source ressort du rendu à l'identique. C'est la preuve que la
transformation de vue et l'espace colorimétrique des textures sont justes.

---

## La démonstration

`projets/exemple.json` est un projet **fictif** — « Atelier Peyrat » n'existe
pas. Ses deux URL pointent sur `demo/avant.html` et `demo/apres.html`, servies
en local par `make demo`. C'est ce qui permet de valider toute la chaîne, avec
un vrai Chromium et un vrai défilement, sans dépendre d'un site tiers ni du
réseau.

Les deux pages sont représentatives à dessein : l'« avant » n'a pas de balise
`viewport` (le défaut de sa génération), une mise en page fixe à 960 px, un
compteur de visiteurs et un bandeau `#tarteaucitronAlertBig` ; l'« après » est
responsive, avec appel à l'action dès le premier écran et chargement différé
des images. Les deux servent aussi de banc d'essai : sans le chargement
différé, on ne saurait pas si l'aller-retour de défilement fonctionne.

`projets/exemple2.json` reprend les mêmes pages **inversées** : c'est le second
couple de hauteurs dont le critère « même vitesse apparente » a besoin. Il n'est
pas destiné à être publié.

---

## Prérequis

```
blender          4.0 ou plus
python3          avec playwright et pillow
ffmpeg / ffprobe
```

`requirements.txt` liste les dépendances Python. Si l'environnement fournit
déjà un Chromium dont le numéro de build ne correspond pas à celui qu'attend
Playwright, `capture.py` le détecte et l'utilise tel quel plutôt que d'en
retélécharger un ; on peut aussi forcer le chemin par `CHROMIUM_BIN`.

---

## Ce qu'il ne faut pas faire

- Ne pas utiliser les couleurs du client. Le cadre reste aux couleurs PixFeed,
  le site du client vit à l'intérieur de l'écran.
- Ne pas laisser apparaître de curseur ni de fenêtre de navigateur.
- Ne pas ajouter de musique dans le fichier exporté.
- Ne pas introduire de variation esthétique entre deux projets. Toute demande
  de changement visuel passe par `grammar.py` et s'applique à toute la série.
- Ne pas régénérer la scène dans la chaîne de production. `make template` est
  une opération rare, à faire exprès.
