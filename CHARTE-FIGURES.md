# Charte des figures — jurojin.net et pixfeed

Instructions complètes pour fabriquer un visuel d'article. À donner telle
quelle à qui fabrique la figure.

---

## 1. Palette

Aucune autre couleur. Les contrastes sont mesurés sur le papier.

### Fond et texte

| rôle | hex | contraste |
|---|---|---|
| papier, le fond | `#FAF9F6` | jamais de crème, jamais de blanc pur |
| encre, titres et texte fort | `#1A1B20` | 16,33:1 |
| gris, texte secondaire | `#646670` | 5,43:1 |
| faible, mentions discrètes et notes | `#8C8D96` | 3,13:1 |
| filet, traits de séparation | `#D5D3CC` | trait seulement, jamais du texte |
| blanc | `#FFFFFF` | uniquement SUR un aplat de couleur |

### Accent, l'indigo de la maison

| rôle | hex | contraste |
|---|---|---|
| indigo texte, pour écrire en indigo sur le papier | `#622CC8` | 7,35:1 |
| indigo aplat, pastilles de numéro et aplats | `#9442FA` | blanc dessus 4,75:1 |
| indigo barre, aplats de barres et de rubans | `#7C60D0` | blanc dessus 4,73:1 |

### Signalisation, usage strictement réservé

| rôle | hex | contraste | blanc dessus |
|---|---|---|---|
| alerte | `#B02E26` | 6,11:1 | 6,43:1 |
| vert | `#0C7C5C` | 4,92:1 | 5,18:1 |

### Séries neutres, s'il faut plus d'une teinte sans signification

| rôle | hex | contraste |
|---|---|---|
| ambre | `#B45309` | 4,77:1 |
| bleu | `#1668B8` | 4,77:1 |

---

## 2. Quand le rouge et le vert ont le droit d'apparaître

**Seulement dans une figure qui oppose un état sain à un état dégradé.**
Dès qu'ils apparaissent, ils veulent dire quelque chose. Jamais en décor,
jamais pour distinguer deux séries neutres.

**Oui :** trouvé contre pas trouvé, une étape qui passe contre une qui
casse, visible contre caché, avant contre après.

**Non :** deux modes de rendu, deux façons de payer, deux prises de vue
qui se recouvrent, trois bibliothèques qui pèsent trois poids, quatre
résolutions, un point de mesure. Dans tous ces cas : indigo, et ambre
pour la seconde série.

Deux pièges déjà rencontrés :

- Peindre en alerte la colonne d'un produit qui échoue **une seule fois
  sur vingt-quatre**. Le compte reste neutre, l'alerte ne touche que la
  case qui échoue.
- Peindre en alerte un élément dans **tous** les panneaux, y compris
  celui où il ne se passe rien. Signaler un danger là où rien n'arrive
  use le signal pour rien.

---

## 3. Typographie

- **Liberation Sans**, repli Arial puis Helvetica. Jamais Inter.
- Titre : 19 px gras, en capitales, interlettrage 2,2.
- Sous-titre : 17 px normal, en faible.
- Libellés : 15 à 20 px selon le rôle. Notes : 13 à 14 px.
- Pas de titre à 40 px : le titre de la figure n'est pas celui de
  l'article.

---

## 4. Règles non négociables

1. **Jamais de tiret cadratin — ni demi-cadratin –** dans aucun texte.
2. **Tout texte atteint 4,5:1** sur le fond qu'il occupe réellement
   (3,0:1 pour les mentions faibles). À vérifier **par calcul avant de
   dessiner**, pas à l'œil.
3. Pas de bandes zébrées, pas de bordures de cellules, pas de grille
   façon tableur, pas de pavé de couleur derrière chaque case.
4. Pas de filtre de grain, d'ombre portée, de dégradé ni de texture.
5. **Une seule ligne de texte sous la figure**, au maximum. La source et
   la méthode longue vont dans la légende de l'article, pas gravées dans
   l'image. Sauf demande explicite.
6. Pas de nom d'auteur d'asset gravé dans l'image.
7. Largeur **1600 px**. Export **WebP + SVG**, calques SVG nommés.
8. Signature du site seulement si elle est demandée.

---

## 5. Règles de données

Celles-ci comptent plus que les couleurs.

1. **Ne jamais inventer une mesure.** Si l'article ne donne pas une
   valeur, la demander. Une figure signée « banc d'essai » ou « tests
   maison » ne contient que des nombres relevés.
2. **Tout chiffre écrit dans la figure est recalculé** à partir des
   données, et comparé à ce que l'article affirme. Le dessin s'arrête à
   la première divergence.
3. **Composer les phrases à partir des données**, ne pas les recopier.
   Une phrase recopiée peut diverger ; une phrase composée, non.
4. **Afficher l'arrondi de l'article, pas celui de l'interpréteur.**
   `round(3.25, 1)` rend 3,2 en Python, quand l'arrondi commercial écrit
   3,3. Comparer à un demi-pas près.
5. **Ne pas mélanger deux unités sur un axe.** Poser 33 € sur un axe en
   dollars demande un taux de change que l'article ne donne pas.
6. **Garder l'échelle linéaire quand la disproportion est le propos.**
   Une barre à 2,3 % d'une autre n'est pas un défaut de dessin.
7. **Dire quand un axe n'est pas proportionnel** (« échelle doublée à
   chaque cran »), sinon la figure laisse croire à une croissance
   linéaire.
8. **Un « sans objet » doit être possible.** Ailleurs, c'est une mesure
   manquante déguisée en case vide, et un contrôle doit le refuser.
9. **Compter ce que le titre annonce.** « Sept logiciels », « dix-huit
   versions », « six espaces réseau » : recompter sur ce qui est
   réellement dessiné.

---

## 6. Règles de composition

1. **Contrôles de collision obligatoires**, parce que ces défauts ne se
   voient qu'une fois l'image tirée :
   - une étiquette qui mord sur la colonne voisine ;
   - une tige qui traverse le bloc d'un autre jalon ;
   - une valeur qui déborde de sa barre ;
   - deux blocs du même côté et de la même profondeur qui se croisent ;
   - un renvoi collé au bord de sa colonne, donc lisible comme
     appartenant à la suivante.
2. **Conduites pointillées** dès que l'œil doit traverser plus de trois
   cents pixels de papier entre une étiquette et sa marque.
3. **Un bloc qui sortirait du cadre bascule à gauche de sa tige**, texte
   rangé sur le bord droit. La tige touche alors le coin du bloc au lieu
   de le barrer.
4. **Sur un axe proportionnel**, chaque jalon porte son côté (au-dessus
   ou au-dessous) et sa profondeur, et un contrôle refuse deux blocs qui
   partagent les deux et se croisent.
5. **Plafond d'un panneau : 1,15 fois son maximum.** Sans cette marge,
   une série plate bute contre le haut du cadre et se lit comme une
   jauge pleine.
6. **Une valeur ne tient pas dans une barre courte** : la poser après la
   barre plutôt que dedans, et contrôler qu'elle y tient.
7. **Le SVG groupe les calques sur les suites consécutives de la clé de
   couche.** Émettre les ordres groupés par calque, sinon on obtient
   vingt-cinq calques au lieu de huit.
8. **Un disque blanc posé sur une fente de papier disparaît.** Faire se
   toucher les segments d'un ruban plutôt que les séparer d'un filet.

---

## 7. Captures d'écran

1. **Faire tourner le vrai logiciel** chaque fois que c'est possible.
2. **Redessiner** seulement si le logiciel est injoignable **et** qu'il
   ne s'agit pas de refaire l'interface d'un tiers.
3. **Ne jamais fabriquer** l'écran d'une application tierce ni la fiche
   d'une organisation réelle. Un lecteur a le logiciel ouvert en
   lisant : un dialogue inventé se repère en trente secondes.
4. **Visuels de presse d'un tiers** : renvoyer vers l'ayant droit, sauf
   licence explicite.
5. **Floutage irréversible** : flou gaussien **puis** pixelisation. Un
   calque translucide ou un flou léger se récupère.

---

## 8. Ce qu'un script de figure doit produire

- Un `composer()` unique qui rend la liste des ordres de dessin, lue à
  la fois par le rendu matriciel et par le rendu SVG : les deux ne
  peuvent pas diverger.
- Un contrôle de contraste exécuté **avant** le premier trait.
- Les contrôles de données et de collision, chacun avec un message qui
  dit quoi corriger.
- Le dessin à trois fois la taille, puis réduction Lanczos.
- Les trois fichiers : WebP, PNG, SVG à calques nommés.
