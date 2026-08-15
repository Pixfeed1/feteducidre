# -*- coding: utf-8 -*-
u"""
Vectorise la course de la planche 62 de Muybridge (1887, domaine public) :
12 phases de profil d'une VRAIE course a pleine vitesse.

La chaine par phase :
  1. seuillage du corps (clair) sur le mur (sombre), fenetre au-dessus
     de la piste ; plus grande composante, mouchetures tuees par taille
  2. fermeture morphologique, suivi de bord, Douglas-Peucker (1.2),
     points en coordonnees locales : origine = le SOL sous le centre de
     gravite, hauteur normalisee a 100
  3. la sortie est un module Python : courses.py, PHASES = [[(x,y),...]]

L'enfant se fabrique ENSUITE par-dessus ces silhouettes (tete agrandie,
habillage charte) - la foulee est photographique, l'habit est a nous.
"""
import numpy as np
from PIL import Image
from collections import deque

im = Image.open('../muybridge_nulib/assets/images/thumbnails/'
                'plate-number-62-running-at-full-speed.gif')

def composantes_garde(m, mini):
    H, W = m.shape
    lab = np.zeros(m.shape, int); cur = 0; garde = np.zeros(m.shape, bool)
    meilleurs = []
    for y0, x0 in zip(*np.where(m)):
        if lab[y0, x0]: continue
        cur += 1; q = deque([(y0, x0)]); lab[y0, x0] = cur; pts = [(y0, x0)]
        while q:
            y, x = q.popleft()
            for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
                yy, xx = y+dy, x+dx
                if 0 <= yy < H and 0 <= xx < W and m[yy, xx] and not lab[yy, xx]:
                    lab[yy, xx] = cur; q.append((yy, xx)); pts.append((yy, xx))
        meilleurs.append(pts)
    meilleurs = [p for p in meilleurs if len(p) >= mini]
    if not meilleurs: return garde
    meilleurs.sort(key=len)
    for p in meilleurs[-1]:
        garde[p] = True
    return garde

def dilate(m, it=1):
    for _ in range(it):
        m = m | np.roll(m,1,0) | np.roll(m,-1,0) | np.roll(m,1,1) | np.roll(m,-1,1)
    return m
def erode(m, it=1):
    for _ in range(it):
        m = m & np.roll(m,1,0) & np.roll(m,-1,0) & np.roll(m,1,1) & np.roll(m,-1,1)
    return m

def bord(m):
    bd = m & ~erode(m)
    pts = set(zip(*np.where(bd)))
    y0 = min(p[0] for p in pts); x0 = min(p[1] for p in pts if p[0] == y0)
    ordre = [(y0, x0)]; pts.discard((y0, x0))
    while pts:
        y, x = ordre[-1]
        best, bd2 = None, 99
        for ray in (1, 2, 3):
            for dy in range(-ray, ray+1):
                for dx in range(-ray, ray+1):
                    c = (y+dy, x+dx)
                    if c in pts:
                        d2 = dy*dy+dx*dx
                        if d2 < bd2: best, bd2 = c, d2
            if best: break
        if best is None: break
        ordre.append(best); pts.discard(best)
    return [(x, y) for (y, x) in ordre]

def dp(pts, eps):
    if len(pts) < 3: return pts
    a, b = np.array(pts[0], float), np.array(pts[-1], float)
    ab = b - a; L = np.hypot(*ab)
    dmax, imax = -1.0, 0
    for i in range(1, len(pts) - 1):
        p = np.array(pts[i], float)
        d = np.hypot(*(p - a)) if L < 1e-9 else \
            abs(ab[0]*(a[1]-p[1]) - (a[0]-p[0])*ab[1]) / L
        if d > dmax: dmax, imax = d, i
    if dmax <= eps: return [pts[0], pts[-1]]
    return dp(pts[:imax+1], eps)[:-1] + dp(pts[imax:], eps)

def simplifier(pts, eps):
    n = len(pts)
    return dp(pts[:n//2+1], eps)[:-1] + dp(pts[n//2:] + [pts[0]], eps)[:-1]

brut = []
for i in range(12):                      # les 12 vues de PROFIL
    im.seek(i)
    a = np.array(im.convert('L')).astype(int)
    H, W = a.shape
    ys = np.arange(H)[:, None] + 0 * a
    fenetre = (ys < int(H * 0.82)) & (ys > int(H * 0.04))
    # SEUIL ADAPTATIF : le corps est le haut de l'histogramme de la
    # fenetre - un seuil fixe ratait les vues plus sombres
    vals = a[fenetre]
    seuil = np.percentile(vals, 88)
    m = (a > seuil) & fenetre
    m = composantes_garde(m, 300)
    m = erode(dilate(m, 2), 2)
    m = composantes_garde(m, 300)
    ysx, xsx = np.where(m)
    brut.append((m, ysx, xsx))
    print('phase %2d : seuil %d, %d px de corps' % (i, seuil, m.sum()))

# L'ECHELLE COMMUNE : normaliser chaque phase a sa propre hauteur tuait
# le REBOND naturel de la course. La reference est la phase la plus
# haute ; le sol de chaque phase reste son propre pied d'appui.
h_ref = max(float(ys_.max() - ys_.min()) for _, ys_, _ in brut)
phases = []
for i, (m, ysx, xsx) in enumerate(brut):
    sol = ysx.max()
    cx = xsx.mean()
    pts = simplifier(bord(m), 1.2)
    loc = [(float(round((x - cx) * 100.0 / h_ref, 1)),
            float(round((y - sol) * 100.0 / h_ref, 1))) for (x, y) in pts]
    phases.append(loc)
    print('phase %2d : %3d points' % (i, len(loc)))

with open('courses.py', 'w') as f:
    f.write('# -*- coding: utf-8 -*-\n')
    f.write('u"""La course de la planche 62 de Muybridge (1887, domaine\n')
    f.write('public), vectorisee : 12 phases de profil, origine au sol\n')
    f.write('sous le centre de gravite, hauteur normalisee a 100."""\n\n')
    f.write('PHASES = [\n')
    for ph in phases:
        f.write('    %r,\n' % (ph,))
    f.write(']\n')
print('courses.py ecrit')
