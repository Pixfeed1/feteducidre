#  Générateur de Reels « projet client » PixFeed
#
#      make reel PROJECT=tenakoe      la chaîne complète
#      make demo                      la démonstration, de bout en bout
#      make test                      les critères d'acceptation
#
#  Une commande par projet, aucune intervention manuelle dans Blender.

BLENDER ?= blender
PYTHON  ?= python3
PROJECT ?= exemple

JSON    := projets/$(PROJECT).json
OUT     := out/$(PROJECT)
FRAMES  := $(OUT)/frames
REEL    := $(OUT)/reel.mp4

.PHONY: reel capture build encode demo demo-serveur test template propre aide

aide:
	@echo "  make reel PROJECT=<slug>   capture + rendu + encodage"
	@echo "  make demo                  la démonstration complète"
	@echo "  make test                  les critères d'acceptation"
	@echo "  make template              REFABRIQUE template.blend (rare)"
	@echo "  make propre PROJECT=<slug> efface les images d'un projet"

reel: capture build encode

capture:
	@echo "== capture =================================================="
	@$(PYTHON) src/capture.py $(JSON)

build:
	@echo "== construction et rendu ===================================="
	@rm -rf $(FRAMES) && mkdir -p $(FRAMES)
	@d=$$(date +%s); \
	 $(BLENDER) -b template.blend -P src/build_reel.py -- $(JSON) \
	    --sortie $(FRAMES)/ 2>&1 | grep -vE "^(Fra:|Blender|Read blend|EGL|Managed|found bundled|Read prefs)" || true; \
	 echo $$(( $$(date +%s) - d )) > $(OUT)/duree_rendu.txt
	@echo "   $$(ls $(FRAMES) | wc -l) images rendues en $$(cat $(OUT)/duree_rendu.txt) s"

encode:
	@echo "== encodage ================================================="
	@$(PYTHON) src/encode.py $(JSON)

#  Le modèle est VERSIONNÉ. On ne le refabrique que si la scène change —
#  jamais dans la chaîne de production d'un Reel.
template:
	@$(PYTHON) src/faire_logo_svg.py
	@$(BLENDER) -b --factory-startup --python src/faire_template.py 2>&1 | tail -2

#  Les deux pages de démonstration sont servies en local : la chaîne de
#  capture se valide alors sans dépendre d'un site tiers ni du réseau.
demo-serveur:
	@$(PYTHON) -m http.server 8777 --bind 127.0.0.1 --directory demo

#  `exemple2` reprend les mêmes pages INVERSÉES : c'est le second couple de
#  hauteurs dont le critère « même vitesse apparente » a besoin.
demo:
	@($(PYTHON) -m http.server 8777 --bind 127.0.0.1 --directory demo \
	    >/dev/null 2>&1 & echo $$! > /tmp/reel-demo.pid); sleep 1
	@( $(MAKE) reel PROJECT=exemple && \
	   $(PYTHON) src/capture.py projets/exemple2.json ); r=$$?; \
	    kill $$(cat /tmp/reel-demo.pid) 2>/dev/null; exit $$r

test:
	@$(PYTHON) tests/lancer.py

propre:
	@rm -rf $(FRAMES) $(OUT)/img_*.png $(OUT)/_*.png
	@echo "  $(OUT) nettoyé (captures et reel.mp4 conservés)"
