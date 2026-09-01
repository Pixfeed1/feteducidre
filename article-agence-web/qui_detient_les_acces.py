"""
Figure de la question 3 — « Qui détient les accès ? »

    python3 article-agence-web/qui_detient_les_acces.py

Produit `article-agence-web/qui-detient-les-acces-site-web.webp` et son
équivalent PNG.

----------------------------------------------------------------------------
LA FORME VIENT DE LA PHRASE QUI COMPTE
----------------------------------------------------------------------------
Le paragraphe dit quatre choses, mais il en dit surtout une : le domaine est le
seul qui ne se récupère pas. Une figure qui alignerait les quatre accès côte à
côte, du même format, dirait exactement le contraire — qu'ils se valent.

D'où deux zones séparées par un trait, et non quatre cases. Au-dessus, seul,
sur toute la largeur : le nom de domaine. En dessous, plus petits et à égalité
entre eux : les trois autres. Le lecteur n'a pas besoin de lire pour saisir la
hiérarchie, elle est dans la mise en page.

----------------------------------------------------------------------------
LA NUANCE DES COMPTES GOOGLE
----------------------------------------------------------------------------
Elle est conservée telle quelle : l'accès se reprend, l'historique non. Ranger
Search Console avec l'hébergement sans le préciser aurait fait dire au schéma
quelque chose de faux, et c'est justement la ligne qui décide un commerçant à
vérifier son compte le soir même.

----------------------------------------------------------------------------
LA HAUTEUR EST CALCULÉE, PAS FIXÉE
----------------------------------------------------------------------------
Les libellés se replient sur la largeur de leur carte ; le nombre de lignes
dépend donc du texte. Fixer la hauteur d'avance revient à choisir entre une
bande vide en bas et un texte coupé. Elle se déduit du contenu, et le script
refuse de produire l'image si un bloc dépasse la place qui lui revient.
"""

import os

from PIL import Image, ImageDraw

import charte as C

RACINE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(RACINE, "qui-detient-les-acces-site-web")

L = 1600
MARGE = 56
GOUTTIERE = 32

DOMAINE = {
    "titre": "Le nom de domaine",
    "exigence": "À votre nom, dans votre compte, chez votre bureau "
                "d'enregistrement.",
    "precision": "Pas « géré par » l'agence : la nuance ne se voit que le jour "
                 "où vous partez.",
    "verdict": "NE SE RÉCUPÈRE PAS",
    "detail": "ou au prix d'une procédure de plusieurs mois",
}

AUTRES = (
    {
        "titre": "L'hébergement",
        "texte": "Vous devez pouvoir y accéder et le résilier sans passer par "
                 "un tiers.",
        "note": None,
    },
    {
        "titre": "L'administration du site",
        "texte": "Un compte administrateur à votre nom, pas un identifiant "
                 "partagé transmis par message.",
        "note": None,
    },
    {
        "titre": "Les comptes Google",
        "texte": "Search Console, Analytics, fiche d'établissement : vous "
                 "propriétaire, l'agence simplement ajoutée comme "
                 "utilisateur.",
        "note": "l'accès se reprend, l'historique non",
    },
)


def couper(d, texte, f, largeur):
    """Le texte replié sur la largeur disponible, mot à mot."""
    ligne, lignes = "", []
    for m in texte.split():
        essai = (ligne + " " + m).strip()
        if d.textlength(essai, font=f) > largeur and ligne:
            lignes.append(ligne)
            ligne = m
        else:
            ligne = essai
    lignes.append(ligne)
    return lignes


def barre(d, x, y0, y1, epaisseur, rayon, teinte, fond):
    """
    Une barre pleine le long du bord gauche, aux angles de la carte.

    Dessinée en deux temps : un rectangle arrondi large, puis un rectangle de
    la couleur de la carte qui en recouvre la partie droite. C'est le seul
    moyen d'obtenir une barre dont les DEUX coins gauches suivent l'arrondi et
    dont le bord droit reste droit — un simple rectangle dépasse des angles.
    """
    d.rounded_rectangle([x, y0, x + rayon * 3, y1], radius=rayon, fill=teinte)
    d.rectangle([x + epaisseur, y0, x + rayon * 3, y1], fill=fond)


def pastille(d, x, y, diam, numero, f, fond):
    d.ellipse([x, y, x + diam, y + diam], fill=fond)
    n = str(numero)
    d.text((x + diam / 2 - d.textlength(n, font=f) / 2,
            y + diam / 2 - f.size * 0.68), n, font=f, fill=(255, 255, 255))


def etiquette(d, x, y, texte, f, teinte, plein=False):
    """Une pastille de texte : pleine pour le verdict, cerclée pour le reste."""
    w = d.textlength(texte, font=f) + 34
    h = f.size + 20
    d.rounded_rectangle([x, y, x + w, y + h], radius=(h // 2),
                        fill=teinte if plein else None,
                        outline=None if plein else teinte,
                        width=1 if plein else 2)
    d.text((x + 17, y + 9), texte, font=f,
           fill=(255, 255, 255) if plein else teinte)
    return w, h


def principal():
    C.verifier()

    #  On dessine une première fois sur une image jetable pour MESURER les
    #  replis de texte, puis on crée l'image à la bonne hauteur. Sans ça, la
    #  hauteur serait une estimation, et une estimation finit toujours par
    #  couper une ligne.
    mesure = ImageDraw.Draw(Image.new("RGB", (10, 10)))

    f_titre = C.police(C.POLICE_G, 30)
    f_zone = C.police(C.POLICE_G, 18)
    f_dom = C.police(C.POLICE_G, 38)
    f_dom_txt = C.police(C.POLICE_R, 24)
    f_dom_pre = C.police(C.POLICE_R, 21)
    f_verdict = C.police(C.POLICE_G, 21)
    f_detail = C.police(C.POLICE_R, 18)
    f_carte = C.police(C.POLICE_G, 25)
    f_corps = C.police(C.POLICE_R, 21)
    f_note = C.police(C.POLICE_R, 18)
    f_num = C.police(C.POLICE_G, 24)
    f_num_p = C.police(C.POLICE_G, 20)

    largeur_utile = L - 2 * MARGE
    col = (largeur_utile - 2 * GOUTTIERE) // 3
    texte_col = col - 56

    #  La carte du domaine réserve sa moitié droite au verdict.
    verdict_w = mesure.textlength(DOMAINE["verdict"], font=f_verdict) + 34
    detail_w = mesure.textlength(DOMAINE["detail"], font=f_detail)
    reserve = int(max(verdict_w, detail_w)) + 60
    dom_texte = largeur_utile - 108 - reserve

    dom_exig = couper(mesure, DOMAINE["exigence"], f_dom_txt, dom_texte)
    dom_prec = couper(mesure, DOMAINE["precision"], f_dom_pre, dom_texte)
    h_dom = 34 + 46 + len(dom_exig) * 33 + 6 + len(dom_prec) * 28 + 34

    plies = [couper(mesure, c["texte"], f_corps, texte_col) for c in AUTRES]
    #  La mention commence après la puce, elle a donc moins de place que le
    #  corps. La replier sur la largeur du corps la faisait sortir de la carte.
    texte_note = texte_col - 20
    notes = [couper(mesure, c["note"], f_note, texte_note) if c["note"] else []
             for c in AUTRES]
    lignes_max = max(len(p) for p in plies)
    notes_max = max(len(n) for n in notes)
    h_bande = (22 + notes_max * 24 + 20) if notes_max else 0
    h_carte = 26 + 44 + lignes_max * 29 + 20 + h_bande + 6

    y_zone_a = MARGE + 74
    y_dom = y_zone_a + 28
    y_zone_b = y_dom + h_dom + 44
    y_cartes = y_zone_b + 28
    H = y_cartes + h_carte + MARGE

    out = Image.new("RGB", (L, H), C.FOND)
    d = ImageDraw.Draw(out)

    d.rectangle([MARGE, 44, MARGE + 10, 78], fill=C.VIOLET)
    d.text((MARGE + 24, 40), "QUI DÉTIENT LES ACCÈS ?", font=f_titre,
           fill=C.ENCRE)

    # ------------------------------------------------  ce qui ne revient pas
    d.text((MARGE, y_zone_a), "CE QUI NE SE RÉCUPÈRE PAS", font=f_zone,
           fill=C.ALERTE)

    x1 = L - MARGE
    rose = (255, 246, 245)
    d.rounded_rectangle([MARGE, y_dom, x1, y_dom + h_dom], radius=14,
                        fill=rose)
    #  La barre pleine à gauche : c'est elle qu'on voit en vignette, avant même
    #  d'avoir lu le mot « domaine ».
    barre(d, MARGE, y_dom, y_dom + h_dom, 22, 14, C.ALERTE, rose)
    d.rounded_rectangle([MARGE, y_dom, x1, y_dom + h_dom], radius=14,
                        outline=C.ALERTE, width=2)

    xt = MARGE + 108
    pastille(d, MARGE + 46, y_dom + 30, 44, 1, f_num, C.ALERTE)
    d.text((xt, y_dom + 26), DOMAINE["titre"], font=f_dom, fill=C.ENCRE)
    y = y_dom + 34 + 46
    for t in dom_exig:
        d.text((xt, y), t, font=f_dom_txt, fill=C.ENCRE)
        y += 33
    y += 6
    for t in dom_prec:
        d.text((xt, y), t, font=f_dom_pre, fill=C.GRIS)
        y += 28

    xv = x1 - reserve + 20
    w, h = etiquette(d, xv, y_dom + 36, DOMAINE["verdict"], f_verdict,
                     C.ALERTE, plein=True)
    d.text((xv, y_dom + 36 + h + 14), DOMAINE["detail"], font=f_detail,
           fill=C.ALERTE)
    if xv < xt + dom_texte:
        raise SystemExit("le verdict recouvre le texte du domaine")

    # -------------------------------------------  ce dont on reprend la main
    d.text((MARGE, y_zone_b), "CE DONT ON REPREND LA MAIN", font=f_zone,
           fill=C.GRIS)

    bas_carte = y_cartes + h_carte
    for i, (carte, lignes, note) in enumerate(zip(AUTRES, plies, notes)):
        x0 = MARGE + i * (col + GOUTTIERE)
        d.rounded_rectangle([x0, y_cartes, x0 + col, bas_carte], radius=14,
                            fill=C.CARTE)
        barre(d, x0, y_cartes, bas_carte, 16, 14, C.VIOLET, C.CARTE)

        if note:
            #  La nuance des comptes Google occupe une bande teintée en pied de
            #  carte. Posée dans le vide comme une ligne de plus, elle se lisait
            #  comme du remplissage ; encadrée, elle se lit comme une réserve.
            y_bande = bas_carte - h_bande
            d.rounded_rectangle([x0 + 16, y_bande, x0 + col, bas_carte],
                                radius=14, fill=(253, 244, 243))
            d.rectangle([x0 + 16, y_bande, x0 + col, y_bande + 14],
                        fill=(253, 244, 243))

        d.rounded_rectangle([x0, y_cartes, x0 + col, bas_carte], radius=14,
                            outline=C.BORD, width=2)

        pastille(d, x0 + 36, y_cartes + 28, 36, i + 2, f_num_p, C.VIOLET)
        d.text((x0 + 84, y_cartes + 28), carte["titre"], font=f_carte,
               fill=C.ENCRE)
        y = y_cartes + 26 + 44
        for t in lignes:
            d.text((x0 + 36, y), t, font=f_corps, fill=C.GRIS)
            y += 29
        if y > bas_carte - h_bande - 8:
            raise SystemExit("le texte de « %s » entre dans la bande du bas"
                             % carte["titre"])

        if note:
            y = bas_carte - h_bande + 20
            #  Le point rouge signale que cette carte n'est pas tout à fait
            #  comme les deux autres.
            d.ellipse([x0 + 36, y + 7, x0 + 46, y + 17], fill=C.ALERTE)
            for t in note:
                d.text((x0 + 56, y), t, font=f_note, fill=C.GRIS)
                if x0 + 56 + d.textlength(t, font=f_note) > x0 + col - 16:
                    raise SystemExit("la mention de « %s » sort de la carte"
                                     % carte["titre"])
                y += 24

    out.save(BASE + ".webp", "WEBP", quality=C.QUALITE, method=6)
    out.save(BASE + ".png", "PNG", optimize=True)
    print()
    print("  %d × %d" % out.size)
    for e in (".webp", ".png"):
        print("  %-44s %.0f Ko" % (os.path.basename(BASE + e),
                                   os.path.getsize(BASE + e) / 1024))


if __name__ == "__main__":
    principal()
