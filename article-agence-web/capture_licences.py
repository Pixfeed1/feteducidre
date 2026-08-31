"""
La capture de l'écran des extensions, sur un WordPress réellement installé.

    python3 article-agence-web/capture_licences.py

Produit `article-agence-web/licences-capture-wordpress-7.1.png`.

----------------------------------------------------------------------------
CE QUI TOURNE DERRIÈRE
----------------------------------------------------------------------------
Un WordPress 7.1 complet, dans un conteneur, avec MariaDB à côté. Les trois
extensions payantes de `wordpress-licences/` sont installées et activées ;
chacune déclare une nouvelle version disponible sans fournir de paquet, ce qui
est exactement la réponse d'un serveur de licences quand l'abonnement est
terminé.

La phrase « Automatic update is unavailable for this plugin » qui apparaît sur
la capture n'est écrite nulle part dans ce dépôt : c'est WordPress qui la
produit, dans `wp-admin/includes/update.php`, parce qu'il constate qu'il n'y a
rien à télécharger. C'est tout l'intérêt de faire tourner le vrai logiciel
plutôt que d'en dessiner une imitation.

----------------------------------------------------------------------------
LE NAVIGATEUR
----------------------------------------------------------------------------
Le Chromium préinstallé de l'environnement, lancé sans passer par le proxy —
le site est sur la boucle locale et le proxy refuserait la sortie. Le facteur
d'échelle est à 2 : une capture d'écran d'admin repassée à 1600 px de large
devient illisible si elle a été prise à 1600 px.
"""

import os

from playwright.sync_api import sync_playwright

RACINE = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(RACINE, "licences-capture-wordpress-7.1.png")

BASE = "http://127.0.0.1:8080"
UTILISATEUR, MOTDEPASSE = "michael", "pixfeed2026"

CHROMIUM = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"


def principal():
    with sync_playwright() as p:
        nav = p.chromium.launch(
            executable_path=CHROMIUM,
            args=["--no-sandbox", "--no-proxy-server",
                  "--disable-dev-shm-usage"])
        ctx = nav.new_context(viewport={"width": 1500, "height": 1100},
                              device_scale_factor=2, locale="fr-FR")
        pg = ctx.new_page()

        pg.goto(BASE + "/wp-login.php", wait_until="networkidle")
        pg.fill("#user_login", UTILISATEUR)
        pg.fill("#user_pass", MOTDEPASSE)
        pg.click("#wp-submit")
        pg.wait_for_load_state("networkidle")

        pg.goto(BASE + "/wp-admin/plugins.php", wait_until="networkidle")

        #  On vérifie AVANT de capturer que l'écran dit bien ce qu'on veut
        #  montrer. Une capture d'un écran vide se remarque trop tard.
        texte = pg.inner_text("body")
        for attendu in ("Licence expirée", "3.6.0", "5.3.1", "3.0.2"):
            if attendu not in texte:
                raise SystemExit(
                    "l'écran ne contient pas « %s » : les extensions ne "
                    "déclarent pas leur mise à jour" % attendu)

        rangs = pg.locator("tr.plugin-update-tr:not(.hidden)")
        lignes = rangs.count()
        if lignes < 3:
            raise SystemExit("seulement %d ligne(s) de mise à jour sur 3"
                             % lignes)

        #  La coupe est MESURÉE sur la page, pas devinée : on s'arrête sous la
        #  dernière ligne de mise à jour, au pixel. Une constante en dur se
        #  décale dès qu'un libellé passe à la ligne.
        bas = rangs.nth(lignes - 1).bounding_box()
        hauteur = int(bas["y"] + bas["height"])
        pg.screenshot(path=SORTIE,
                      clip={"x": 0, "y": 0, "width": 1500, "height": hauteur})
        print("  %d lignes de mise à jour, coupe à %d px" % (lignes, hauteur))
        print("  -> %s" % os.path.basename(SORTIE))
        nav.close()


if __name__ == "__main__":
    principal()
