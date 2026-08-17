"""
Étape 1 — capture des deux sites.

    python src/capture.py projets/tenakoe.json

Produit `out/<slug>/avant.png`, `out/<slug>/apres.png` et `out/<slug>/
capture.json` qui journalise la hauteur en pixels de chaque capture : cette
valeur est indispensable à l'étape suivante pour calculer le défilement.

Deux détails qui font la différence entre une capture utilisable et une
capture pleine de trous :

  1. **L'aller-retour de défilement.** On descend jusqu'en bas, on attend deux
     secondes, on remonte, et seulement ensuite on capture. C'est ce qui
     déclenche le chargement différé des images. Sans lui, la capture pleine
     page contient des blocs vides — c'est l'erreur la plus fréquente.

  2. **Les bandeaux de cookies.** Masqués par feuille de style injectée avant
     la capture, jamais par un clic sur « accepter » : le clic dépend de la
     langue du bouton et casse dès que le site change de prestataire.
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grammar as G
import config as C

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#  Les prestataires de consentement les plus répandus en France, plus les
#  formes génériques. Liste volontairement large : une capture avec un
#  bandeau est inutilisable, une capture qui a perdu un élément décoratif ne
#  l'est pas.
SELECTEURS_COOKIES = [
    "#onetrust-banner-sdk", "#onetrust-consent-sdk", ".onetrust-pc-dark-filter",
    "#tarteaucitronRoot", "#tarteaucitronAlertBig",
    "#axeptio_overlay", "#axeptio_main_button",
    "#didomi-host", ".didomi-popup-container", ".didomi-consent-popup",
    "#CybotCookiebotDialog", "#CybotCookiebotDialogBodyUnderlay",
    "#usercentrics-root", "#uc-banner-content",
    ".osano-cm-window", ".osano-cm-dialog",
    "#cookiescript_injected", "#cookie-law-info-bar",
    "#hs-eu-cookie-confirmation", ".fc-consent-root",
    ".cc-window", ".cookie-consent", ".cookie-banner", ".cookies-banner",
    "#cookie-banner", "#cookieConsent", "#gdpr-cookie-message",
    '[id*="cookie-banner" i]', '[class*="cookie-banner" i]',
    '[aria-label*="cookie" i]', '[class*="consent-banner" i]',
]

#  Ce que l'on ne veut jamais voir dans un Reel : une infobulle de chat, une
#  fenêtre de newsletter, un bandeau d'alerte flottant.
SELECTEURS_PARASITES = [
    "#crisp-chatbox", ".intercom-lightweight-app", "#tidio-chat",
    "#launcher", ".drift-frame-controller", "#hubspot-messages-iframe-container",
    '[class*="newsletter-popup" i]', '[class*="exit-intent" i]',
]

CSS_MASQUE = """
%s { display: none !important; visibility: hidden !important; }
html { scroll-behavior: auto !important; }
*, *::before, *::after {
    animation-duration: 0s !important;
    animation-delay: 0s !important;
    transition-duration: 0s !important;
    transition-delay: 0s !important;
}
"""
#  Les animations sont neutralisées : une capture pleine page attrape une
#  animation à mi-course et fige un élément à moitié transparent.

CSS_FLOU = """
%s { filter: blur(9px) !important; }
"""


#  Un élément en `position: fixed` est peint UNE SEULE FOIS dans une capture
#  pleine page, à une hauteur arbitraire — on retrouve le bandeau de cookies
#  ou la barre d'appel plantés au milieu du site. On les repose donc dans le
#  flux avant de capturer : fixed devient absolute (l'en-tête remonte en haut,
#  la barre d'appel descend en bas), sticky devient relative (l'élément reste
#  à sa place naturelle).
JS_DEFIXER = """
() => {
  let n = 0;
  document.querySelectorAll('*').forEach(el => {
    const p = getComputedStyle(el).position;
    if (p === 'fixed') {
      el.style.setProperty('position', 'absolute', 'important'); n++;
    } else if (p === 'sticky') {
      el.style.setProperty('position', 'relative', 'important'); n++;
    }
  });
  return n;
}
"""


def _feuille(selecteurs):
    return ", ".join(selecteurs)


def capturer_une(page, url, sortie, flouter, masquer, hauteur_max_css,
                 attente_ms):
    page.goto(url, wait_until="load", timeout=60000)
    try:
        page.wait_for_load_state("networkidle", timeout=20000)
    except Exception:
        pass                                    # certains sites ne s'y posent jamais

    #  `masquer` complète la liste intégrée : aucune liste de sélecteurs ne
    #  peut couvrir tous les prestataires de consentement du monde, et une
    #  capture avec un bandeau est une capture perdue.
    page.add_style_tag(content=CSS_MASQUE % _feuille(
        SELECTEURS_COOKIES + SELECTEURS_PARASITES + list(masquer)))
    if flouter:
        #  Option de floutage par sélecteur : aucune donnée personnelle,
        #  aucun identifiant ne doit se retrouver dans une publication.
        page.add_style_tag(content=CSS_FLOU % _feuille(flouter))

    #  L'ALLER-RETOUR — c'est lui qui déclenche le chargement différé
    hauteur = page.evaluate("document.body.scrollHeight")
    pas = G.CAPTURE_VIEWPORT[1]
    y = 0
    while y < hauteur:
        page.evaluate("window.scrollTo(0, %d)" % y)
        page.wait_for_timeout(120)
        y += pas
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(attente_ms)
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(600)

    n_fixes = page.evaluate(JS_DEFIXER)
    page.wait_for_timeout(300)

    hauteur = int(page.evaluate(
        "Math.max(document.body.scrollHeight, "
        "document.documentElement.scrollHeight)"))
    largeur = G.CAPTURE_VIEWPORT[0]

    if hauteur > hauteur_max_css:
        #  Au-delà, c'est du poids de texture pour rien : le défilement du
        #  Reel ne descend jamais aussi bas.
        page.screenshot(path=sortie, clip={"x": 0, "y": 0,
                                           "width": largeur,
                                           "height": hauteur_max_css})
        hauteur = hauteur_max_css
        tronquee = True
    else:
        page.screenshot(path=sortie, full_page=True)
        tronquee = False
    return hauteur, tronquee, n_fixes


def reduire(chemin, largeur_cible):
    """
    On capture à ×3 pour que le texte du site soit net, puis on redescend à
    deux fois la largeur d'affichage réelle. Au-delà c'est de la mémoire de
    texture pure perte : l'écran ne fait que 560 px de large dans l'image
    finale.
    """
    from PIL import Image
    im = Image.open(chemin)
    if im.width <= largeur_cible:
        return im.size
    h = int(round(im.height * largeur_cible / float(im.width)))
    im = im.convert("RGB").resize((largeur_cible, h), Image.LANCZOS)
    im.save(chemin)
    return im.size


def chemin_chromium():
    """
    Certains environnements fournissent un Chromium déjà installé dont le
    numéro de build ne correspond pas à celui qu'attend la version de
    Playwright installée. Plutôt que de retélécharger un navigateur entier,
    on lui indique explicitement le binaire présent.

    On peut aussi forcer le chemin par la variable CHROMIUM_BIN.
    """
    force = os.environ.get("CHROMIUM_BIN")
    if force and os.path.exists(force):
        return force
    racine = os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")
    if not os.path.isdir(racine):
        return None
    import glob
    for motif in ("chromium-*/chrome-linux/chrome",
                  "chromium_headless_shell-*/chrome-linux/"
                  "chrome-headless-shell"):
        trouves = sorted(glob.glob(os.path.join(racine, motif)))
        if trouves:
            return trouves[-1]
    return None


def principal():
    ap = argparse.ArgumentParser(description="Captures avant / après")
    ap.add_argument("projet")
    ap.add_argument("--video", action="store_true",
                    help="mode de repli : enregistre une vidéo de défilement "
                         "au lieu d'une capture pleine page, pour les sites "
                         "dont les animations au défilement ne survivent pas "
                         "à la capture. N'est PAS le mode par défaut.")
    ap.add_argument("--hauteur-max", type=int, default=9000,
                    help="hauteur maximale capturée, en pixels CSS")
    ap.add_argument("--attente", type=int, default=2000,
                    help="attente en bas de page, en millisecondes")
    ap.add_argument("--largeur-texture", type=int, default=1120)
    args = ap.parse_args()

    cfg = C.charger(args.projet)
    dossier = os.path.join(RACINE, "out", cfg["slug"])
    os.makedirs(dossier, exist_ok=True)

    from playwright.sync_api import sync_playwright

    journal = {"slug": cfg["slug"], "viewport": list(G.CAPTURE_VIEWPORT),
               "navigateur": chemin_chromium() or "(celui de Playwright)",
               "echelle": G.CAPTURE_ECHELLE, "pages": {}}

    with sync_playwright() as p:
        binaire = chemin_chromium()
        nav = p.chromium.launch(executable_path=binaire,
                                args=["--hide-scrollbars",
                                      "--force-color-profile=srgb"])
        ctx = nav.new_context(
            viewport={"width": G.CAPTURE_VIEWPORT[0],
                      "height": G.CAPTURE_VIEWPORT[1]},
            device_scale_factor=G.CAPTURE_ECHELLE,
            locale="fr-FR",
            record_video_dir=(os.path.join(dossier, "video")
                              if args.video else None),
        )
        page = ctx.new_page()
        for cle, url in (("avant", cfg["url_avant"]),
                         ("apres", cfg["url_apres"])):
            sortie = os.path.join(dossier, "%s.png" % cle)
            h_css, tronquee, n_fixes = capturer_une(
                page, url, sortie, cfg.get("flouter", []),
                cfg.get("masquer", []), args.hauteur_max, args.attente)
            lp, hp = reduire(sortie, args.largeur_texture)
            #  ATTENTION — le nombre de hauteurs d'écran se déduit du RAPPORT
            #  DE LA TEXTURE, jamais de la hauteur CSS.
            #
            #  Un site sans balise viewport (le cas de tous les vieux sites,
            #  donc de tous les « avant ») est mis en page par le navigateur
            #  mobile sur une largeur de 980 px puis dézoomé pour tenir dans
            #  les 390 px de l'écran. Sa hauteur CSS est comptée dans le
            #  repère à 980 px de large : la lire telle quelle donnait ici
            #  2,48 hauteurs d'écran au lieu de 1,01, soit un défilement deux
            #  fois et demie trop long. C'est exactement le genre d'erreur qui
            #  fait mentir la comparaison de vitesse entre l'avant et l'après.
            rapport_ecran = (G.CAPTURE_VIEWPORT[1] /
                             float(G.CAPTURE_VIEWPORT[0]))
            hauteurs = (hp / float(lp)) / rapport_ecran
            journal["pages"][cle] = {
                "url": url, "fichier": os.path.basename(sortie),
                "hauteur_css": h_css, "tronquee": tronquee,
                "largeur_px": lp, "hauteur_px": hp,
                "hauteurs_ecran": round(hauteurs, 3),
                "elements_defixes": n_fixes,
            }
            print("  %-6s  texture %4d × %5d  =  %.2f hauteurs d'écran"
                  "   (%d px CSS)%s"
                  % (cle, lp, hp, hauteurs, h_css,
                     "   TRONQUÉE" if tronquee else ""))
        ctx.close()
        nav.close()

    with open(os.path.join(dossier, "capture.json"), "w",
              encoding="utf-8") as f:
        json.dump(journal, f, ensure_ascii=False, indent=2)
    print("  journal : out/%s/capture.json" % cfg["slug"])


if __name__ == "__main__":
    principal()
