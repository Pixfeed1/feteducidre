"""
Étape 4 — encodage.

    python src/encode.py projets/exemple.json

On passe par une SÉQUENCE PNG, pas par la sortie vidéo intégrée de Blender.
Trois raisons, toutes vérifiées à l'usage :

  - un rendu interrompu se reprend là où il s'est arrêté ;
  - on peut ouvrir l'image 348 et regarder ce qui cloche ;
  - l'encodage se refait sans relancer trois heures de calcul.

`-an` est volontaire : aucune piste audio. La musique est ajoutée dans
l'application Instagram au moment de publier — sur un compte professionnel,
c'est même la seule façon d'avoir une piste utilisable, la bibliothèque
commerciale n'étant pas accessible depuis un fichier importé.
"""

import argparse
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grammar as G
import config as C

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def images_presentes(dossier):
    return sorted(f for f in os.listdir(dossier)
                  if f.endswith(".png") and f[:-4].isdigit())


def encoder(slug, ouvrir=None):
    dossier = os.path.join(RACINE, "out", slug)
    frames = os.path.join(dossier, "frames")
    if not os.path.isdir(frames):
        raise SystemExit("aucune image rendue dans %s" % frames)

    presentes = images_presentes(frames)
    attendu = G.DUREE_IMAGES
    if len(presentes) != attendu:
        raise SystemExit(
            "%d images rendues au lieu de %d — le rendu est incomplet.\n"
            "        première : %s   dernière : %s"
            % (len(presentes), attendu,
               presentes[0] if presentes else "(aucune)",
               presentes[-1] if presentes else "(aucune)"))

    depart = int(presentes[0][:-4])
    sortie = ouvrir or os.path.join(dossier, "reel.mp4")
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(G.IMAGES_PAR_SECONDE),
        "-start_number", str(depart),
        "-i", os.path.join(frames, "%04d.png"),
        "-c:v", G.ENCODEUR,
        "-crf", str(G.CRF),
        "-pix_fmt", G.FORMAT_PIXEL,
        "-movflags", "+faststart",
        "-an",
        sortie,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("ffmpeg a échoué :\n" + r.stderr[-2500:])
    return sortie


def controler(chemin):
    """On ne fait jamais confiance à un encodage sans le relire."""
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration:stream=width,height,nb_frames,r_frame_rate,"
         "pix_fmt,codec_name,codec_type",
         "-of", "json", chemin],
        capture_output=True, text=True)
    d = json.loads(r.stdout)
    flux = d.get("streams", [])
    v = [s for s in flux if s.get("codec_type") == "video"][0]
    duree = float(d["format"]["duration"])
    fautes = []
    if (int(v["width"]), int(v["height"])) != (G.LARGEUR_PX, G.HAUTEUR_PX):
        fautes.append("résolution %sx%s" % (v["width"], v["height"]))
    if int(v.get("nb_frames", 0)) != G.DUREE_IMAGES:
        fautes.append("%s images" % v.get("nb_frames"))
    if abs(duree - G.DUREE_IMAGES / float(G.IMAGES_PAR_SECONDE)) > 0.005:
        fautes.append("durée %.3f s" % duree)
    if v["pix_fmt"] != G.FORMAT_PIXEL:
        fautes.append("format de pixel %s" % v["pix_fmt"])
    if len(flux) != 1:
        fautes.append("%d flux au lieu d'un seul (piste audio ?)" % len(flux))
    print("  %s" % os.path.relpath(chemin, RACINE))
    print("  %s × %s, %s images, %.3f s, %s, %s, %d flux — %s"
          % (v["width"], v["height"], v.get("nb_frames"), duree,
             v["codec_name"], v["pix_fmt"], len(flux),
             "conforme" if not fautes else "NON CONFORME : " +
             ", ".join(fautes)))
    if fautes:
        raise SystemExit(1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("projet")
    ap.add_argument("--sortie")
    a = ap.parse_args()
    cfg = C.charger(a.projet)
    controler(encoder(cfg["slug"], a.sortie))
