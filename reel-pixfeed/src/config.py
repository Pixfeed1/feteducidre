"""
Lecture et validation d'un fichier projet.

Règle du cahier des charges : on échoue avec un message clair, jamais de
troncature silencieuse. Un texte trop long qui déborde de la zone sûre est un
Reel raté ; un script qui s'arrête en le disant est un Reel à corriger.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grammar as G


class ConfigInvalide(Exception):
    pass


CHAMPS_OBLIGATOIRES = [
    "slug", "client", "secteur", "annee", "url_avant", "url_apres",
    "hook", "avant", "apres", "chiffre", "sortie", "cta",
]


def _exiger(cond, message, erreurs):
    if not cond:
        erreurs.append(message)


def charger(chemin):
    """Lit le JSON, valide, renvoie un dictionnaire normalisé."""
    if not os.path.exists(chemin):
        raise ConfigInvalide("fichier projet introuvable : %s" % chemin)
    with open(chemin, encoding="utf-8") as f:
        try:
            cfg = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigInvalide("JSON illisible dans %s : %s" % (chemin, e))

    erreurs = []

    for champ in CHAMPS_OBLIGATOIRES:
        _exiger(champ in cfg, "champ obligatoire manquant : « %s »" % champ,
                erreurs)
    if erreurs:
        raise ConfigInvalide(_rapport(chemin, erreurs))

    # --- les deux listes de trois points -----------------------------------
    for cle in ("avant", "apres"):
        v = cfg[cle]
        _exiger(isinstance(v, list),
                "« %s » doit être une liste" % cle, erreurs)
        if isinstance(v, list):
            _exiger(len(v) == G.POINTS_ATTENDUS,
                    "« %s » doit contenir exactement %d entrées, il y en a %d"
                    % (cle, G.POINTS_ATTENDUS, len(v)), erreurs)
            for i, ligne in enumerate(v):
                _exiger(isinstance(ligne, str),
                        "« %s »[%d] doit être une chaîne" % (cle, i), erreurs)
                if isinstance(ligne, str):
                    _exiger(
                        len(ligne) <= G.LONGUEUR_POINT,
                        "« %s »[%d] fait %d caractères, maximum %d — "
                        "au-delà le texte sort de la zone sûre.\n"
                        "        texte : %s"
                        % (cle, i, len(ligne), G.LONGUEUR_POINT, ligne),
                        erreurs)

    # --- l'accroche ---------------------------------------------------------
    if isinstance(cfg.get("hook"), str):
        _exiger(len(cfg["hook"]) <= G.LONGUEUR_HOOK,
                "« hook » fait %d caractères, maximum %d.\n        texte : %s"
                % (len(cfg["hook"]), G.LONGUEUR_HOOK, cfg["hook"]), erreurs)
    else:
        _exiger(False, "« hook » doit être une chaîne", erreurs)

    # --- le chiffre ---------------------------------------------------------
    ch = cfg.get("chiffre")
    _exiger(isinstance(ch, dict) and "valeur" in ch and "legende" in ch,
            "« chiffre » doit être un objet { valeur, legende }", erreurs)

    # --- divers -------------------------------------------------------------
    _exiger(isinstance(cfg.get("annee"), int),
            "« annee » doit être un entier", erreurs)
    _exiger(isinstance(cfg.get("slug"), str) and cfg.get("slug", "").strip(),
            "« slug » doit être une chaîne non vide", erreurs)
    for cle in ("url_avant", "url_apres"):
        v = cfg.get(cle, "")
        _exiger(isinstance(v, str) and v.startswith(("http://", "https://",
                                                     "file://")),
                "« %s » doit être une URL http(s) ou file://" % cle, erreurs)

    if erreurs:
        raise ConfigInvalide(_rapport(chemin, erreurs))

    # --- normalisation ------------------------------------------------------
    cfg.setdefault("anonyme", False)
    cfg.setdefault("flouter", [])           # sélecteurs CSS à flouter
    cfg.setdefault("masquer", [])           # sélecteurs CSS à cacher
    if cfg["anonyme"]:
        # le nom disparaît, le secteur porte l'identification
        cfg["client_affiche"] = cfg["secteur"]
        cfg["secteur_affiche"] = "Client sous accord de confidentialité"
    else:
        cfg["client_affiche"] = cfg["client"]
        cfg["secteur_affiche"] = cfg["secteur"]
    return cfg


def _rapport(chemin, erreurs):
    lignes = ["", "  %s : %d erreur(s)" % (chemin, len(erreurs)), ""]
    lignes += ["    - " + e for e in erreurs]
    lignes.append("")
    return "\n".join(lignes)


def couper(texte, largeur):
    """
    Retour à la ligne décidé par le script : Blender ne sait pas le faire.
    On coupe aux espaces, sans jamais couper un mot.
    """
    mots, lignes, courante = texte.split(), [], ""
    for mot in mots:
        essai = (courante + " " + mot).strip()
        if len(essai) <= largeur or not courante:
            courante = essai
        else:
            lignes.append(courante)
            courante = mot
    if courante:
        lignes.append(courante)
    return "\n".join(lignes)


if __name__ == "__main__":
    for chemin in sys.argv[1:]:
        try:
            cfg = charger(chemin)
        except ConfigInvalide as e:
            print("ÉCHEC%s" % e)
            sys.exit(1)
        print("OK  %s  (%s, %s)" % (chemin, cfg["client_affiche"],
                                    cfg["secteur_affiche"]))
