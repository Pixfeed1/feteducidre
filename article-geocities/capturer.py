"""
Rend la page reconstituée dans un vrai navigateur et la capture.

    python3 article-geocities/capturer.py

Produit `geocities-page-perso.png`.

----------------------------------------------------------------------------
800 x 600, PARCE QUE C'EST LA RÉSOLUTION DU SUJET
----------------------------------------------------------------------------
La page elle-même annonce « optimisé pour 800x600 ». La rendre dans une
fenêtre moderne de 1600 pixels de large étalerait les tableaux et
détruirait exactement ce que la figure doit montrer : une mise en page
pensée pour un petit écran.

La fenêtre fait donc 800 points de large, et le facteur d'échelle est
porté à 2. Le navigateur dessine réellement deux fois plus gros, ce qui
donne une image de 1600 pixels nette sur écran moderne, sans agrandir
après coup une capture floue.

----------------------------------------------------------------------------
UN VRAI MOTEUR DE RENDU, PAS UN DESSIN
----------------------------------------------------------------------------
Le balisage de 1997 est passé tel quel à Chromium : TABLE de mise en
page, attributs BACKGROUND et TEXT sur BODY, MARQUEE, FONT SIZE. Ce qui
sort est ce qu'un navigateur fait de ce code, pas ce que j'imagine qu'il
en ferait.
"""

import os
import sys

from playwright.sync_api import sync_playwright

ICI = os.path.dirname(os.path.abspath(__file__))
PAGE = os.path.join(ICI, "page.html")
SORTIE = os.path.join(ICI, "geocities-page-perso.png")

LARGEUR = 800          # la résolution que la page revendique
ECHELLE = 2            # rendu réel à 1600 px, pas un agrandissement

#  Le Chromium du conteneur est désigné explicitement : le paquet pip
#  installé ici attend un autre numéro de build et voudrait retélécharger
#  un navigateur, ce que l'environnement interdit.
CHROMIUM = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"


def principal():
    if not os.path.exists(PAGE):
        raise SystemExit("page.html introuvable")

    with sync_playwright() as p:
        if not os.path.exists(CHROMIUM):
            raise SystemExit("Chromium introuvable : %s" % CHROMIUM)
        navigateur = p.chromium.launch(executable_path=CHROMIUM)
        page = navigateur.new_page(
            viewport={"width": LARGEUR, "height": 600},
            device_scale_factor=ECHELLE)
        page.goto("file://" + PAGE)
        page.wait_for_load_state("networkidle")

        #  Le marquee défile : on le fige au même endroit à chaque
        #  exécution, sinon la capture n'est pas reproductible.
        page.evaluate("""() => {
            document.querySelectorAll('marquee').forEach(m => m.stop());
        }""")
        page.wait_for_timeout(400)

        hauteur = page.evaluate(
            "() => document.documentElement.scrollHeight")
        page.set_viewport_size({"width": LARGEUR, "height": int(hauteur)})
        page.wait_for_timeout(300)
        page.screenshot(path=SORTIE, full_page=True)
        navigateur.close()

    from PIL import Image
    im = Image.open(SORTIE)
    attendu = LARGEUR * ECHELLE
    if im.width != attendu:
        raise SystemExit("la capture fait %d px de large, %d attendus : le "
                         "facteur d'échelle n'a pas été appliqué"
                         % (im.width, attendu))
    #  Une page noire et vide passerait inaperçue : on vérifie qu'il y a
    #  vraiment quelque chose de dessiné.
    couleurs = im.convert("RGB").getcolors(400000)
    if couleurs is None or len(couleurs) < 200:
        raise SystemExit("la capture ne contient presque aucune couleur : la "
                         "page ne s'est pas chargée")

    print("  %s" % os.path.basename(SORTIE))
    print("  %d x %d, %.0f Ko, %d couleurs distinctes"
          % (im.width, im.height, os.path.getsize(SORTIE) / 1024.0,
             len(couleurs)))


if __name__ == "__main__":
    sys.exit(principal())
