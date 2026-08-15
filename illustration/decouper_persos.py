# -*- coding: utf-8 -*-
u"""
Decoupe les personnages de la 5e reference et les accorde a nos tons.

    python3 decouper_persos.py          (attend reference5.png a cote)
    -> perso_homme.png, perso_femme.png  (RVBA, fond transparent)

LA CHAINE
  1. classes de couleur : peau (r>150, r-g>45), encre vraie (b<45 - les
     rayures a l'ombre ont un bleu de 60-95, c'est le canal bleu qui
     separe), debardeur (teal a bleu ELEVE >108, le mat et l'ombre non),
     pieds gris (fenetre serree) ;
  2. les mouchetures du grain meurent PAR TAILLE de composante (<25 px),
     jamais par erosion - l'erosion mange les doigts de 3 px ;
  3. fermeture morphologique (dilate x2 puis erode x2) pour boucher les
     trous interieurs ;
  4. balance des blancs : leur sable rose (248,235,212) -> notre
     #FAFAF6 - c'est ce qui les met "dans nos tons" ;
  5. bord adouci d'un demi-pixel (moyenne 3x3 de l'alpha).

LES ANCRES (imprimees a la fin) : le decalage entre le coin de la boite
et le point d'assise de chaque figure - personnages.vrais_persos() les
reprend en dur.
"""
import numpy as np
from PIL import Image
from collections import deque

im = np.array(Image.open('reference5.png').convert('RGB')).astype(float)
H, W = im.shape[:2]
r, g, b = im[..., 0], im[..., 1], im[..., 2]
ys = np.arange(H)[:, None]; xs = np.arange(W)[None, :]
fac = np.array([250.0, 250.0, 246.0]) / im[850:880, 560:660].reshape(-1, 3).mean(0)

peau = (r > 150) & (r - g > 45) & (g < 170)
encre = (r < 80) & (g < 85) & (b < 45)
teal = (np.abs(r - 0x65) < 45) & (np.abs(g - 0x93) < 42) & (b > 108) & (g > r)
gris_pied = (r > 150) & (r < 215) & (r - g > 15) & (r - g < 45) & (g > b)


def dilate(m, it=1):
    for _ in range(it):
        m = m | np.roll(m,1,0) | np.roll(m,-1,0) | np.roll(m,1,1) | np.roll(m,-1,1)
    return m


def erode(m, it=1):
    for _ in range(it):
        m = m & np.roll(m,1,0) & np.roll(m,-1,0) & np.roll(m,1,1) & np.roll(m,-1,1)
    return m


def par_taille(m, mini):
    lab = np.zeros(m.shape, int); cur = 0; garde = np.zeros(m.shape, bool)
    for y0, x0 in zip(*np.where(m)):
        if lab[y0, x0]:
            continue
        cur += 1; q = deque([(y0, x0)]); lab[y0, x0] = cur; pts = [(y0, x0)]
        while q:
            y, x = q.popleft()
            for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
                yy, xx = y+dy, x+dx
                if 0 <= yy < H and 0 <= xx < W and m[yy, xx] and not lab[yy, xx]:
                    lab[yy, xx] = cur; q.append((yy, xx)); pts.append((yy, xx))
        if len(pts) >= mini:
            for p in pts:
                garde[p] = True
    return garde


# le bras de la femme passe devant la cheville de l'homme : cette droite
# et ce coin bas-droit sont A ELLE (le meme partage que les decalques)
a_elle = ((xs > (960 + 0.6 * (ys - 770))) & (xs >= 966)) | \
         ((ys > 784) & (xs > 948))
lui = (peau | encre) & (ys >= 707) & (ys < 812) & (xs >= 856) & (xs < 996) \
      & ~a_elle & ~((xs < 873) & (ys < 786))
elle = (peau | encre
        | (teal & (xs > 975) & (xs < 1035) & (ys > 738) & (ys < 795))
        | (gris_pied & (xs > 1050) & (xs < 1100) & (ys > 772) & (ys < 806))) \
       & (ys >= 713) & (ys < 812) & (xs >= 950) & (xs < 1100) & a_elle


def decouper(nom, m, seat):
    m = par_taille(m, 25)
    m = erode(dilate(m, 2), 2)
    m = par_taille(m, 60)
    ysx, xsx = np.where(m)
    x0, x1, y0, y1 = xsx.min(), xsx.max()+1, ysx.min(), ysx.max()+1
    rgb = np.clip(im[y0:y1, x0:x1] * fac, 0, 255).astype(np.uint8)
    alpha = m[y0:y1, x0:x1].astype(float) * 255
    alpha = (alpha + np.roll(alpha,1,0) + np.roll(alpha,-1,0)
             + np.roll(alpha,1,1) + np.roll(alpha,-1,1)) / 5.0
    Image.fromarray(np.dstack([rgb, alpha.astype(np.uint8)]), 'RGBA').save(nom)
    print('%s : decalage assise (%d, %d), %dx%d'
          % (nom, x0-seat[0], y0-seat[1], x1-x0, y1-y0))


decouper('perso_homme.png', lui, (905, 800))
decouper('perso_femme.png', elle, (1010, 800))
