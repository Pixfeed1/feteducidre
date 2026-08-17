"""
Les critères d'acceptation, un par un, exécutables.

    python tests/lancer.py            tout
    python tests/lancer.py boucle     un seul critère

Un critère qui ne peut pas être évalué faute d'artefact n'est PAS compté
comme réussi : il est annoncé « non évaluable » et fait échouer la série.
Un test qui se tait quand il manque quelque chose ne sert à rien.
"""

import hashlib
import json
import os
import re
import subprocess
import sys
import time

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "src"))
import grammar as G                                            # noqa: E402
import config as C                                             # noqa: E402

BLENDER = os.environ.get("BLENDER", "blender")
PYTHON = sys.executable
SLUG = "exemple"


class Echec(Exception):
    pass


def _dossier(slug=SLUG):
    return os.path.join(RACINE, "out", slug)


def _exiger_fichier(chemin, comment):
    if not os.path.exists(chemin):
        raise Echec("%s absent — %s" % (os.path.relpath(chemin, RACINE),
                                        comment))
    return chemin


def _sonder(chemin):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration:stream=width,height,nb_frames,pix_fmt,codec_type",
         "-of", "json", chemin], capture_output=True, text=True)
    return json.loads(r.stdout)


# ===========================================================================

def t_mp4_valide():
    """Un MP4 lisible est produit sans aucune intervention."""
    f = _exiger_fichier(os.path.join(_dossier(), "reel.mp4"),
                        "lancez `make demo`")
    d = _sonder(f)
    if not d.get("streams"):
        raise Echec("aucun flux lisible dans le fichier")
    return "%s, %.1f Mo" % (os.path.relpath(f, RACINE),
                            os.path.getsize(f) / 1e6)


def t_duree_et_images():
    """20,00 s exactement, 600 images, sans piste audio."""
    f = _exiger_fichier(os.path.join(_dossier(), "reel.mp4"),
                        "lancez `make demo`")
    d = _sonder(f)
    v = [s for s in d["streams"] if s["codec_type"] == "video"][0]
    duree = float(d["format"]["duration"])
    cible = G.DUREE_IMAGES / float(G.IMAGES_PAR_SECONDE)
    if abs(duree - cible) > 0.005:
        raise Echec("durée %.4f s au lieu de %.2f" % (duree, cible))
    if int(v["nb_frames"]) != G.DUREE_IMAGES:
        raise Echec("%s images au lieu de %d" % (v["nb_frames"],
                                                 G.DUREE_IMAGES))
    if (int(v["width"]), int(v["height"])) != (G.LARGEUR_PX, G.HAUTEUR_PX):
        raise Echec("%sx%s" % (v["width"], v["height"]))
    if v["pix_fmt"] != G.FORMAT_PIXEL:
        raise Echec("format de pixel %s" % v["pix_fmt"])
    if len(d["streams"]) != 1:
        raise Echec("%d flux : il y a une piste audio" % len(d["streams"]))
    return "%.3f s, %s images, %sx%s, %s, aucune piste audio" % (
        duree, v["nb_frames"], v["width"], v["height"], v["pix_fmt"])


def t_boucle():
    """L'image 0 et l'image 599 sont identiques, au pixel près."""
    d = os.path.join(_dossier(), "frames")
    a = _exiger_fichier(os.path.join(d, "%04d.png" % G.IMAGE_PREMIERE),
                        "lancez `make demo`")
    b = _exiger_fichier(os.path.join(d, "%04d.png" % G.IMAGE_DERNIERE),
                        "lancez `make demo`")
    ha = hashlib.sha256(open(a, "rb").read()).hexdigest()
    hb = hashlib.sha256(open(b, "rb").read()).hexdigest()
    if ha != hb:
        from PIL import Image
        import numpy as np
        x = np.asarray(Image.open(a).convert("RGB"), dtype=int)
        y = np.asarray(Image.open(b).convert("RGB"), dtype=int)
        raise Echec("écart maximal %d/255 sur %d pixels"
                    % (abs(x - y).max(), (abs(x - y).sum(2) > 0).sum()))
    return "sha256 identique : %s…" % ha[:16]


def t_zone_sure():
    """Aucun texte ne sort de la zone sûre — contrôle sur les boîtes
    englobantes, fait par build_reel.py au moment de la construction."""
    r = subprocess.run(
        [BLENDER, "-b", os.path.join(RACINE, "template.blend"),
         "-P", os.path.join(RACINE, "src", "build_reel.py"), "--",
         "projets/%s.json" % SLUG, "--pas-de-rendu"],
        capture_output=True, text=True, cwd=RACINE)
    m = re.search(r"zone sûre : (\d+) objets vérifiés, aucun débordement",
                  r.stdout)
    if not m:
        sortie = (r.stdout + r.stderr)[-1200:]
        raise Echec("le contrôle n'a pas confirmé :\n%s" % sortie)
    return "%s objets dans 1080 × %d px (haut %d, bas %d, droite %d)" % (
        m.group(1), G.HAUTEUR_PX - G.SUR_MARGE_HAUT - G.SUR_MARGE_BAS,
        G.SUR_MARGE_HAUT, G.SUR_MARGE_BAS, G.SUR_MARGE_DROITE)


def t_meme_vitesse():
    """Deux projets aux hauteurs de page différentes doivent défiler à la
    même vitesse APPARENTE — on compare les paliers relevés sur les clés."""
    releves = {}
    hauteurs = {}
    for slug in ("exemple", "exemple2"):
        j = os.path.join(_dossier(slug), "capture.json")
        _exiger_fichier(j, "lancez `make demo` puis capturez exemple2")
        journal = json.load(open(j, encoding="utf-8"))
        hauteurs[slug] = tuple(round(journal["pages"][k]["hauteurs_ecran"], 2)
                               for k in ("avant", "apres"))
        r = subprocess.run(
            [BLENDER, "-b", os.path.join(RACINE, "template.blend"),
             "-P", os.path.join(RACINE, "src", "build_reel.py"), "--",
             "projets/%s.json" % slug, "--pas-de-rendu"],
            capture_output=True, text=True, cwd=RACINE)
        v = [float(x) for x in re.findall(r"croisière (\d\.\d+) h/s",
                                          r.stdout)]
        if not v:
            raise Echec("aucune vitesse relevée pour %s :\n%s"
                        % (slug, (r.stdout + r.stderr)[-900:]))
        releves[slug] = v
    toutes = [x for v in releves.values() for x in v]
    if hauteurs["exemple"] == hauteurs["exemple2"]:
        raise Echec("les deux projets ont les mêmes hauteurs de page, "
                    "le critère ne teste rien")
    if max(toutes) - min(toutes) > 1e-6:
        raise Echec("vitesses différentes : %s" % releves)
    return ("hauteurs %s et %s hauteurs d'écran — palier identique "
            "à %.3f h/s" % (hauteurs["exemple"], hauteurs["exemple2"],
                            toutes[0]))


def t_couleurs():
    """
    La couleur d'une capture doit ressortir du rendu TELLE QUELLE.

    On compare l'aplat dominant de la capture source à l'aplat dominant de
    la zone d'écran dans l'image rendue. C'est ce contrôle qui attrape la
    transformation de vue AgX laissée par défaut, et l'espace colorimétrique
    de texture mal réglé.
    """
    from PIL import Image
    import numpy as np

    src = _exiger_fichier(os.path.join(_dossier(), "apres.png"), "capturez")
    frame = os.path.join(_dossier(), "frames", "0400.png")
    _exiger_fichier(frame, "lancez `make demo`")

    def dominante(a):
        q = (a // 4).reshape(-1, 3)
        cles, comptes = np.unique(q, axis=0, return_counts=True)
        return cles[comptes.argmax()] * 4 + 2, comptes.max() / float(len(q))

    a_src = np.asarray(Image.open(src).convert("RGB"), dtype=int)
    c_src, part_src = dominante(a_src)

    #  La fenêtre d'écran, en pixels de l'image finale
    x0 = int(G.LARGEUR_PX / 2 - G.ECRAN_LARGEUR / 2 * G.PX_PAR_UNITE) + 20
    x1 = int(G.LARGEUR_PX / 2 + G.ECRAN_LARGEUR / 2 * G.PX_PAR_UNITE) - 20
    yc = int((G.DEMI_HAUTEUR - G.APPAREIL_CENTRE_Y) * G.PX_PAR_UNITE)
    dh = int(G.ECRAN_HAUTEUR / 2 * G.PX_PAR_UNITE) - 20
    a_ren = np.asarray(Image.open(frame).convert("RGB"),
                       dtype=int)[yc - dh:yc + dh, x0:x1]
    c_ren, part_ren = dominante(a_ren)

    ecart = int(np.abs(c_src - c_ren).max())
    if ecart > 4:
        raise Echec("aplat source %s, aplat rendu %s — écart %d/255"
                    % (c_src.tolist(), c_ren.tolist(), ecart))
    return ("aplat source %s (%.0f %% de la capture) = aplat rendu %s, "
            "écart %d/255" % (c_src.tolist(), part_src * 100,
                              c_ren.tolist(), ecart))


#  Ce qu'on ne cherche PAS : 0, 1, 2, 3… écrire `1.0` dans un calcul n'est
#  pas écrire une valeur de charte en dur.
BANALES = {0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 0.5, 100.0, 255.0, 10.0, 8.0, 6.0,
           12.0, 16.0, 20.0, 30.0, 40.0, 60.0, 90.0, 180.0, 360.0}


def t_charte_unique():
    """Aucune valeur de charte ne doit être écrite en dur hors grammar.py."""
    valeurs = {}
    for nom in dir(G):
        if nom.startswith("_"):
            continue
        v = getattr(G, nom)
        if isinstance(v, float) and abs(v) > 1e-9 and v not in BANALES:
            valeurs.setdefault(round(v, 6), []).append(nom)
        elif isinstance(v, tuple) and v and isinstance(v[0], float):
            for x in v:
                if abs(x) > 1e-9 and x not in BANALES:
                    valeurs.setdefault(round(x, 6), []).append(nom)
    fautes = []
    for chemin in sorted(os.listdir(os.path.join(RACINE, "src"))):
        if not chemin.endswith(".py") or chemin == "grammar.py":
            continue
        texte = open(os.path.join(RACINE, "src", chemin),
                     encoding="utf-8").read()
        #  on ignore les commentaires et les chaînes de documentation
        texte = re.sub(r"#[^\n]*", "", texte)
        texte = re.sub(r'"""[\s\S]*?"""', "", texte)
        for litteral in set(re.findall(r"(?<![\w.])\d+\.\d+", texte)):
            v = round(float(litteral), 6)
            if v in valeurs and v not in BANALES:
                fautes.append("%s : %s (= G.%s)"
                              % (chemin, litteral, valeurs[v][0]))
    if fautes:
        raise Echec("valeur(s) de charte écrite(s) en dur :\n      "
                    + "\n      ".join(fautes))
    return "%d valeurs de charte, aucune recopiée dans les %d autres " \
           "fichiers" % (len(valeurs),
                         len([f for f in os.listdir(
                             os.path.join(RACINE, "src"))
                             if f.endswith(".py")]) - 1)


def t_duree_rendu():
    """Le rendu complet doit tenir sous dix minutes."""
    marque = os.path.join(_dossier(), "duree_rendu.txt")
    if not os.path.exists(marque):
        raise Echec("durée non mesurée — lancez `make demo`, qui la "
                    "consigne dans out/%s/duree_rendu.txt" % SLUG)
    secondes = float(open(marque).read().strip())
    if secondes > 600:
        raise Echec("%.0f s, soit %.1f min" % (secondes, secondes / 60.0))
    return "%.0f s pour %d images (%.2f s par image)" % (
        secondes, G.DUREE_IMAGES, secondes / G.DUREE_IMAGES)


def t_validation_config():
    """La configuration refuse ce qu'elle doit refuser, sans troncature."""
    import tempfile
    base = json.load(open(os.path.join(RACINE, "projets/exemple.json"),
                          encoding="utf-8"))
    cas = [
        ("quatre points au lieu de trois",
         lambda c: c.__setitem__("avant", c["avant"] + ["un de trop"])),
        ("un point trop long",
         lambda c: c.__setitem__("apres", ["x" * (G.LONGUEUR_POINT + 1)]
                                 + c["apres"][1:])),
        ("une accroche trop longue",
         lambda c: c.__setitem__("hook", "y" * (G.LONGUEUR_HOOK + 1))),
        ("un chiffre mal formé",
         lambda c: c.__setitem__("chiffre", "48 h")),
        ("une année en texte",
         lambda c: c.__setitem__("annee", "2026")),
        ("une URL sans schéma",
         lambda c: c.__setitem__("url_apres", "exemple.fr")),
    ]
    for nom, muter in cas:
        c = json.loads(json.dumps(base))
        muter(c)
        f = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False,
                                        encoding="utf-8")
        json.dump(c, f, ensure_ascii=False)
        f.close()
        try:
            C.charger(f.name)
            raise Echec("« %s » a été accepté" % nom)
        except C.ConfigInvalide:
            pass
        finally:
            os.unlink(f.name)
    return "%d configurations fautives, %d refusées" % (len(cas), len(cas))


CRITERES = [
    ("mp4", "un MP4 valide est produit sans intervention", t_mp4_valide),
    ("duree", "20,00 s, 600 images, sans audio", t_duree_et_images),
    ("boucle", "l'image 0 et l'image 599 sont identiques", t_boucle),
    ("zone", "aucun texte hors de la zone sûre", t_zone_sure),
    ("vitesse", "même vitesse apparente à hauteurs différentes",
     t_meme_vitesse),
    ("couleurs", "les couleurs d'une capture sont préservées", t_couleurs),
    ("charte", "aucune valeur de charte en dur hors grammar.py",
     t_charte_unique),
    ("rendu", "le rendu complet tient sous dix minutes", t_duree_rendu),
    ("config", "la validation refuse ce qu'elle doit refuser",
     t_validation_config),
]


def main():
    choisis = sys.argv[1:]
    liste = [c for c in CRITERES if not choisis or c[0] in choisis]
    print()
    ok = 0
    for cle, titre, fn in liste:
        t0 = time.time()
        try:
            detail = fn()
            ok += 1
            print("  \033[32mOK\033[0m    %-9s %s" % (cle, titre))
            print("            %s   [%.1f s]" % (detail, time.time() - t0))
        except Echec as e:
            print("  \033[31mÉCHEC\033[0m %-9s %s" % (cle, titre))
            for ligne in str(e).splitlines():
                print("            %s" % ligne)
        except Exception as e:
            print("  \033[31mERREUR\033[0m %-8s %s : %r" % (cle, titre, e))
    print("\n  %d / %d critères satisfaits\n" % (ok, len(liste)))
    sys.exit(0 if ok == len(liste) else 1)


if __name__ == "__main__":
    main()
