# Textures PBR procédurales 4K — projet rendu boulangerie

Générées par bake Cycles des matériaux procéduraux définis dans `../materials.py`
(script : `../bake_textures.py`). 100 % procédural, aucune ressource externe — libres de droits.

Chaque dossier contient : `*_color_4k.jpg` (sRGB), `*_rough_4k.jpg` (linéaire),
`*_normal_4k.png` (tangent space, OpenGL), `preview.jpg`, `META.txt`
(taille physique couverte `span_m`, valeur metallic, force de bump conseillée).

| Set | Usage | Couvre |
|---|---|---|
| carrelage_sol_beige | Sol 20 cm, joints creusés (poser en diagonale via mapping 45°) | 3,2 m |
| bois_chene_clair | Plan de travail lattes chêne huilé | 2,0 m |
| granit_pilier | Pilier granit moucheté | 1,0 m |
| peinture_blanc_casse | Murs / plafond | 1,0 m |
| peinture_bordeaux | Mur d'accent salle | 1,0 m |
| inox_brosse | Tables inox, crédences (metallic = 1) | 1,0 m |
| faience_murale_taupe | Faïence murale 10×10 | 1,6 m |
| osier_panier | Panières à pain | 0,5 m |

Note : motifs structurés (carreaux, lattes) périodiques ; les composantes de bruit
ne sont pas parfaitement seamless — prévoir les raccords hors zones très visibles,
ou utiliser directement les matériaux procéduraux de `materials.py` (résolution infinie).
