import json
import sys

import bpy

arbre = bpy.data.node_groups.new("T", "ShaderNodeTree")
n = arbre.nodes.new("ShaderNodeBsdfPrincipled")

def defaut(s):
    v = getattr(s, "default_value", None)
    if v is None:
        return None
    try:
        return [round(float(x), 4) for x in v]
    except TypeError:
        pass
    if isinstance(v, float):
        return round(v, 4)
    return v if isinstance(v, (int, str, bool)) else str(v)

def couleur(s):
    for nom in ("draw_color_simple", "draw_color"):
        f = getattr(s, nom, None)
        if f is None:
            continue
        try:
            return [round(float(x), 4) for x in f()]
        except Exception:
            try:
                return [round(float(x), 4) for x in f(bpy.context, n)]
            except Exception:
                pass
    return None

entrees = [{"nom": s.name, "type": s.type, "bl": s.bl_idname,
            "defaut": defaut(s), "couleur": couleur(s),
            "cache": bool(s.hide_value)} for s in n.inputs]
sortie = {"version": bpy.app.version_string, "nombre": len(entrees),
          "entrees": entrees}
json.dump(sortie, open(sys.argv[-1], "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("VERSION %s  ENTREES %d" % (bpy.app.version_string, len(entrees)))
