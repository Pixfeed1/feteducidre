# Bibliothèque de matériaux procéduraux Blender (Cycles) — projet rendu boulangerie.
# Chaque builder construit son graphe dans le node tree fourni et renvoie un dict :
#   color  : socket couleur de base
#   rough  : socket rugosité (niveaux de gris)
#   height : socket hauteur (pour Bump / bake normale)
#   bump   : force de bump conseillée
#   metal  : valeur métallique constante
#   span   : taille physique (mètres) couverte par UV 0..1 lors du bake
import math


def _uv_meters(nt, span):
    coord = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (span, span, span)
    nt.links.new(coord.outputs["UV"], mp.inputs["Vector"])
    return mp.outputs["Vector"]


def _ramp(nt, stops):
    r = nt.nodes.new("ShaderNodeValToRGB")
    cr = r.color_ramp
    cr.elements[0].position = stops[0][0]
    cr.elements[0].color = stops[0][1]
    cr.elements[-1].position = stops[-1][0]
    cr.elements[-1].color = stops[-1][1]
    for pos, col in stops[1:-1]:
        e = cr.elements.new(pos)
        e.color = col
    return r


def carrelage_sol_beige(nt):
    """Carrelage 20 cm beige clair, joints gris creuses, variation par carreau."""
    span = 3.2
    v = _uv_meters(nt, span)
    brick = nt.nodes.new("ShaderNodeTexBrick")
    brick.offset = 0.0
    brick.inputs["Scale"].default_value = 1.0
    brick.inputs["Brick Width"].default_value = 0.20
    brick.inputs["Row Height"].default_value = 0.20
    brick.inputs["Mortar Size"].default_value = 0.0035
    brick.inputs["Mortar Smooth"].default_value = 0.6
    brick.inputs["Color1"].default_value = (1, 1, 1, 1)
    brick.inputs["Color2"].default_value = (1, 1, 1, 1)
    brick.inputs["Mortar"].default_value = (0.42, 0.39, 0.34, 1)
    nt.links.new(v, brick.inputs["Vector"])

    # variation de teinte par carreau
    snap = nt.nodes.new("ShaderNodeVectorMath"); snap.operation = 'SNAP'
    snap.inputs[1].default_value = (0.20, 0.20, 0.20)
    nt.links.new(v, snap.inputs[0])
    wn = nt.nodes.new("ShaderNodeTexWhiteNoise")
    nt.links.new(snap.outputs["Vector"], wn.inputs["Vector"])
    tint = _ramp(nt, [(0.0, (0.80, 0.77, 0.70, 1)), (0.5, (0.84, 0.81, 0.74, 1)), (1.0, (0.87, 0.84, 0.78, 1))])
    nt.links.new(wn.outputs["Value"], tint.inputs["Fac"])

    # micro-moucheture du grès
    spec = nt.nodes.new("ShaderNodeTexNoise")
    spec.inputs["Scale"].default_value = 900; spec.inputs["Detail"].default_value = 2
    nt.links.new(v, spec.inputs["Vector"])
    spot = _ramp(nt, [(0.44, (1, 1, 1, 1)), (0.52, (0.90, 0.88, 0.84, 1)), (0.6, (1, 1, 1, 1))])
    nt.links.new(spec.outputs["Fac"], spot.inputs["Fac"])
    mulc = nt.nodes.new("ShaderNodeMixRGB"); mulc.blend_type = 'MULTIPLY'
    mulc.inputs["Fac"].default_value = 0.5
    nt.links.new(tint.outputs["Color"], mulc.inputs["Color1"])
    nt.links.new(spot.outputs["Color"], mulc.inputs["Color2"])

    # carreau vs joint
    mixj = nt.nodes.new("ShaderNodeMixRGB")
    nt.links.new(brick.outputs["Fac"], mixj.inputs["Fac"])
    nt.links.new(mulc.outputs["Color"], mixj.inputs["Color1"])
    mixj.inputs["Color2"].default_value = (0.42, 0.39, 0.34, 1)

    # rugosite : joint mat, carreau semi-brillant variable
    rtile = nt.nodes.new("ShaderNodeMapRange")
    rtile.inputs["To Min"].default_value = 0.10; rtile.inputs["To Max"].default_value = 0.30
    nt.links.new(wn.outputs["Value"], rtile.inputs["Value"])
    rmix = nt.nodes.new("ShaderNodeMixRGB")
    nt.links.new(brick.outputs["Fac"], rmix.inputs["Fac"])
    nt.links.new(rtile.outputs["Result"], rmix.inputs["Color1"])
    rmix.inputs["Color2"].default_value = (0.85, 0.85, 0.85, 1)

    # hauteur : joints creuses + micro relief
    inv = nt.nodes.new("ShaderNodeMath"); inv.operation = 'SUBTRACT'
    inv.inputs[0].default_value = 1.0
    nt.links.new(brick.outputs["Fac"], inv.inputs[1])
    micro = nt.nodes.new("ShaderNodeTexNoise")
    micro.inputs["Scale"].default_value = 300; micro.inputs["Detail"].default_value = 3
    nt.links.new(v, micro.inputs["Vector"])
    hsum = nt.nodes.new("ShaderNodeMath"); hsum.operation = 'MULTIPLY_ADD'
    nt.links.new(micro.outputs["Fac"], hsum.inputs[0])
    hsum.inputs[1].default_value = 0.06
    nt.links.new(inv.outputs["Value"], hsum.inputs[2])

    return dict(color=mixj.outputs["Color"], rough=rmix.outputs["Color"],
                height=hsum.outputs["Value"], bump=0.25, metal=0.0, span=span)


def bois_chene_clair(nt):
    """Plan de travail chene clair huile, lattes collees, veinage marque."""
    span = 2.0
    v = _uv_meters(nt, span)

    # lattes de 4.5 cm : teinte differente par latte
    snap = nt.nodes.new("ShaderNodeVectorMath"); snap.operation = 'SNAP'
    snap.inputs[1].default_value = (100.0, 0.045, 100.0)
    nt.links.new(v, snap.inputs[0])
    wn = nt.nodes.new("ShaderNodeTexWhiteNoise")
    nt.links.new(snap.outputs["Vector"], wn.inputs["Vector"])

    # veinage : ondes le long de X deformees par bruit
    warp = nt.nodes.new("ShaderNodeTexNoise")
    warp.inputs["Scale"].default_value = 2.5; warp.inputs["Detail"].default_value = 4
    nt.links.new(v, warp.inputs["Vector"])
    add = nt.nodes.new("ShaderNodeVectorMath"); add.operation = 'MULTIPLY_ADD'
    nt.links.new(warp.outputs["Color"], add.inputs[0])
    add.inputs[1].default_value = (0.06, 0.35, 0.0)
    nt.links.new(v, add.inputs[2])
    wave = nt.nodes.new("ShaderNodeTexWave")
    wave.wave_type = 'BANDS'; wave.bands_direction = 'Y'
    wave.inputs["Scale"].default_value = 26
    wave.inputs["Distortion"].default_value = 3.0
    wave.inputs["Detail"].default_value = 2.0
    nt.links.new(add.outputs["Vector"], wave.inputs["Vector"])

    # fibres fines
    fib = nt.nodes.new("ShaderNodeTexNoise")
    fib.inputs["Scale"].default_value = 60; fib.inputs["Detail"].default_value = 6
    nt.links.new(add.outputs["Vector"], fib.inputs["Vector"])

    grain = nt.nodes.new("ShaderNodeMath"); grain.operation = 'MULTIPLY_ADD'
    nt.links.new(wave.outputs["Fac"], grain.inputs[0])
    grain.inputs[1].default_value = 0.75
    m2 = nt.nodes.new("ShaderNodeMath"); m2.operation = 'MULTIPLY'
    nt.links.new(fib.outputs["Fac"], m2.inputs[0]); m2.inputs[1].default_value = 0.25
    nt.links.new(m2.outputs["Value"], grain.inputs[2])

    oak = _ramp(nt, [(0.0, (0.63, 0.45, 0.26, 1)), (0.45, (0.72, 0.55, 0.34, 1)),
                     (0.75, (0.55, 0.38, 0.20, 1)), (1.0, (0.38, 0.24, 0.12, 1))])
    nt.links.new(grain.outputs["Value"], oak.inputs["Fac"])

    lat = _ramp(nt, [(0.0, (0.92, 0.88, 0.85, 1)), (1.0, (1.06, 1.02, 0.96, 1))])
    nt.links.new(wn.outputs["Value"], lat.inputs["Fac"])
    mul = nt.nodes.new("ShaderNodeMixRGB"); mul.blend_type = 'MULTIPLY'; mul.inputs["Fac"].default_value = 1.0
    nt.links.new(oak.outputs["Color"], mul.inputs["Color1"])
    nt.links.new(lat.outputs["Color"], mul.inputs["Color2"])

    rough = nt.nodes.new("ShaderNodeMapRange")
    rough.inputs["To Min"].default_value = 0.42; rough.inputs["To Max"].default_value = 0.28
    nt.links.new(grain.outputs["Value"], rough.inputs["Value"])

    return dict(color=mul.outputs["Color"], rough=rough.outputs["Result"],
                height=grain.outputs["Value"], bump=0.10, metal=0.0, span=span)


def granit_pilier(nt):
    """Granit gris mouchete, finition adoucie."""
    span = 1.0
    v = _uv_meters(nt, span)
    n1 = nt.nodes.new("ShaderNodeTexNoise")
    n1.inputs["Scale"].default_value = 700; n1.inputs["Detail"].default_value = 4
    nt.links.new(v, n1.inputs["Vector"])
    vor = nt.nodes.new("ShaderNodeTexVoronoi"); vor.feature = 'SMOOTH_F1'
    vor.inputs["Scale"].default_value = 90
    vor.inputs["Smoothness"].default_value = 0.4
    nt.links.new(v, vor.inputs["Vector"])
    blend = nt.nodes.new("ShaderNodeMath"); blend.operation = 'MULTIPLY_ADD'
    nt.links.new(n1.outputs["Fac"], blend.inputs[0]); blend.inputs[1].default_value = 0.65
    m = nt.nodes.new("ShaderNodeMath"); m.operation = 'MULTIPLY'
    nt.links.new(vor.outputs["Distance"], m.inputs[0]); m.inputs[1].default_value = 0.5
    nt.links.new(m.outputs["Value"], blend.inputs[2])
    ramp = _ramp(nt, [(0.0, (0.30, 0.28, 0.27, 1)), (0.35, (0.48, 0.45, 0.43, 1)),
                      (0.65, (0.60, 0.57, 0.54, 1)), (1.0, (0.74, 0.71, 0.68, 1))])
    nt.links.new(blend.outputs["Value"], ramp.inputs["Fac"])
    rough = nt.nodes.new("ShaderNodeMapRange")
    rough.inputs["To Min"].default_value = 0.30; rough.inputs["To Max"].default_value = 0.50
    nt.links.new(n1.outputs["Fac"], rough.inputs["Value"])
    return dict(color=ramp.outputs["Color"], rough=rough.outputs["Result"],
                height=blend.outputs["Value"], bump=0.05, metal=0.0, span=span)


def _peinture(nt, rgba):
    span = 1.0
    v = _uv_meters(nt, span)
    col = nt.nodes.new("ShaderNodeRGB"); col.outputs[0].default_value = rgba
    peel = nt.nodes.new("ShaderNodeTexNoise")
    peel.inputs["Scale"].default_value = 140; peel.inputs["Detail"].default_value = 3
    nt.links.new(v, peel.inputs["Vector"])
    rough = nt.nodes.new("ShaderNodeMapRange")
    rough.inputs["To Min"].default_value = 0.50; rough.inputs["To Max"].default_value = 0.62
    nt.links.new(peel.outputs["Fac"], rough.inputs["Value"])
    return dict(color=col.outputs[0], rough=rough.outputs["Result"],
                height=peel.outputs["Fac"], bump=0.04, metal=0.0, span=span)


def peinture_blanc_casse(nt):
    """Peinture murale blanc casse, grain peau d'orange."""
    return _peinture(nt, (0.85, 0.84, 0.80, 1))


def peinture_bordeaux(nt):
    """Peinture murale bordeaux (mur existant cote salle)."""
    return _peinture(nt, (0.245, 0.055, 0.085, 1))


def inox_brosse(nt):
    """Inox brosse, stries horizontales, pour tables et credences."""
    span = 1.0
    v = _uv_meters(nt, span)
    st = nt.nodes.new("ShaderNodeMapping")
    st.inputs["Scale"].default_value = (1.0, 220.0, 1.0)
    nt.links.new(v, st.inputs["Vector"])
    streak = nt.nodes.new("ShaderNodeTexNoise")
    streak.inputs["Scale"].default_value = 3.0; streak.inputs["Detail"].default_value = 5
    nt.links.new(st.outputs["Vector"], streak.inputs["Vector"])
    col = _ramp(nt, [(0.0, (0.66, 0.66, 0.68, 1)), (1.0, (0.78, 0.78, 0.80, 1))])
    nt.links.new(streak.outputs["Fac"], col.inputs["Fac"])
    rough = nt.nodes.new("ShaderNodeMapRange")
    rough.inputs["To Min"].default_value = 0.14; rough.inputs["To Max"].default_value = 0.38
    nt.links.new(streak.outputs["Fac"], rough.inputs["Value"])
    return dict(color=col.outputs["Color"], rough=rough.outputs["Result"],
                height=streak.outputs["Fac"], bump=0.015, metal=1.0, span=span)


def faience_murale_taupe(nt):
    """Faience murale 10x10 taupe/greige brillante (zone porte actuelle)."""
    span = 1.6
    v = _uv_meters(nt, span)
    brick = nt.nodes.new("ShaderNodeTexBrick")
    brick.offset = 0.0
    brick.inputs["Scale"].default_value = 1.0
    brick.inputs["Brick Width"].default_value = 0.10
    brick.inputs["Row Height"].default_value = 0.10
    brick.inputs["Mortar Size"].default_value = 0.003
    brick.inputs["Mortar Smooth"].default_value = 0.5
    brick.inputs["Color1"].default_value = (1, 1, 1, 1)
    brick.inputs["Color2"].default_value = (1, 1, 1, 1)
    brick.inputs["Mortar"].default_value = (0.55, 0.52, 0.48, 1)
    nt.links.new(v, brick.inputs["Vector"])
    snap = nt.nodes.new("ShaderNodeVectorMath"); snap.operation = 'SNAP'
    snap.inputs[1].default_value = (0.10, 0.10, 0.10)
    nt.links.new(v, snap.inputs[0])
    wn = nt.nodes.new("ShaderNodeTexWhiteNoise")
    nt.links.new(snap.outputs["Vector"], wn.inputs["Vector"])
    tint = _ramp(nt, [(0.0, (0.55, 0.51, 0.46, 1)), (0.5, (0.63, 0.59, 0.53, 1)), (1.0, (0.70, 0.66, 0.60, 1))])
    nt.links.new(wn.outputs["Value"], tint.inputs["Fac"])
    mixj = nt.nodes.new("ShaderNodeMixRGB")
    nt.links.new(brick.outputs["Fac"], mixj.inputs["Fac"])
    nt.links.new(tint.outputs["Color"], mixj.inputs["Color1"])
    mixj.inputs["Color2"].default_value = (0.55, 0.52, 0.48, 1)
    rmix = nt.nodes.new("ShaderNodeMixRGB")
    nt.links.new(brick.outputs["Fac"], rmix.inputs["Fac"])
    rmix.inputs["Color1"].default_value = (0.08, 0.08, 0.08, 1)
    rmix.inputs["Color2"].default_value = (0.8, 0.8, 0.8, 1)
    inv = nt.nodes.new("ShaderNodeMath"); inv.operation = 'SUBTRACT'
    inv.inputs[0].default_value = 1.0
    nt.links.new(brick.outputs["Fac"], inv.inputs[1])
    return dict(color=mixj.outputs["Color"], rough=rmix.outputs["Color"],
                height=inv.outputs["Value"], bump=0.2, metal=0.0, span=span)


def osier_panier(nt):
    """Osier tresse pour panieres a pain."""
    span = 0.5
    v = _uv_meters(nt, span)
    wx = nt.nodes.new("ShaderNodeTexWave")
    wx.wave_type = 'BANDS'; wx.bands_direction = 'X'
    wx.inputs["Scale"].default_value = 40; wx.inputs["Distortion"].default_value = 1.2
    nt.links.new(v, wx.inputs["Vector"])
    wy = nt.nodes.new("ShaderNodeTexWave")
    wy.wave_type = 'BANDS'; wy.bands_direction = 'Y'
    wy.inputs["Scale"].default_value = 40; wy.inputs["Distortion"].default_value = 1.2
    nt.links.new(v, wy.inputs["Vector"])
    chk = nt.nodes.new("ShaderNodeTexChecker")
    chk.inputs["Scale"].default_value = 40
    chk.inputs["Color1"].default_value = (1, 1, 1, 1)
    chk.inputs["Color2"].default_value = (0, 0, 0, 1)
    nt.links.new(v, chk.inputs["Vector"])
    weave = nt.nodes.new("ShaderNodeMixRGB")
    nt.links.new(chk.outputs["Color"], weave.inputs["Fac"])
    nt.links.new(wx.outputs["Fac"], weave.inputs["Color1"])
    nt.links.new(wy.outputs["Fac"], weave.inputs["Color2"])
    fib = nt.nodes.new("ShaderNodeTexNoise")
    fib.inputs["Scale"].default_value = 200; fib.inputs["Detail"].default_value = 3
    nt.links.new(v, fib.inputs["Vector"])
    h = nt.nodes.new("ShaderNodeMath"); h.operation = 'MULTIPLY_ADD'
    nt.links.new(fib.outputs["Fac"], h.inputs[0]); h.inputs[1].default_value = 0.15
    nt.links.new(weave.outputs["Color"], h.inputs[2])
    col = _ramp(nt, [(0.0, (0.28, 0.16, 0.07, 1)), (0.5, (0.45, 0.28, 0.13, 1)), (1.0, (0.60, 0.41, 0.21, 1))])
    nt.links.new(h.outputs["Value"], col.inputs["Fac"])
    return dict(color=col.outputs["Color"], rough=None, rough_value=0.65,
                height=h.outputs["Value"], bump=0.35, metal=0.0, span=span)


MATERIALS = {
    "carrelage_sol_beige": carrelage_sol_beige,
    "bois_chene_clair": bois_chene_clair,
    "granit_pilier": granit_pilier,
    "peinture_blanc_casse": peinture_blanc_casse,
    "peinture_bordeaux": peinture_bordeaux,
    "inox_brosse": inox_brosse,
    "faience_murale_taupe": faience_murale_taupe,
    "osier_panier": osier_panier,
}
