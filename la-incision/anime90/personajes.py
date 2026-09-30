"""Personajes al estilo de los 90: Alex, su familia, las figuras enmascaradas y la extremidad oscura.

Diseño sobrio y algo alargado (no chibi): rostro angular, ojos rasgados con el párpado superior grueso y
brillos duros, pelo en bandas con un reflejo azulado, sombra de un solo escalón y tinta de grosor firme.
Cada función dibuja sobre un `Hoja` en coordenadas virtuales, en (cx, cy) con escala `s`.
"""

import math
from contextlib import contextmanager

from .cel import Hoja, elipse, hexa, mezcla, oscuro, curva

TINTA = hexa("#22120f")

# Tonos de iluminación: multiplican el color y lo tiñen (los cels de noche se repintaban en azul).
TONOS = {
    "cena": ((1.0, 0.93, 0.82), 0.0, 1.0),
    "noche": ((0.55, 0.64, 0.98), 0.0, 0.9),
    "recuerdo": ((1.08, 1.02, 0.86), 0.0, 1.1),
    "manana": ((0.95, 0.96, 0.98), 0.35, 1.0),
}


def teñir(c, tono):
    mult, palidez, brillo = TONOS[tono]
    gris = sum(c) / 3
    c = mezcla(c, (gris, gris, gris), palidez)
    return tuple(min(max(v * m * brillo, 0), 1) for v, m in zip(c, mult))


@contextmanager
def _pos(h, cx, cy, s=1.0, flip=False, rot=0.0):
    h.guarda()
    h.cr.translate(cx, cy)
    if rot:
        h.cr.rotate(rot)
    h.cr.scale(-s if flip else s, s)
    try:
        yield
    finally:
        h.restaura()


class Paleta:
    """Los colores de un personaje bajo una luz."""

    def __init__(self, tono, piel, pelo, ropa, ojos="#2a1a14"):
        t = lambda c: teñir(hexa(c), tono)
        self.piel = t(piel)
        self.piel_s = t(oscuro_hex(piel, 0.74))
        self.piel_l = t(claro_hex(piel, 0.22))
        self.pelo = t(pelo)
        self.pelo_l = t(claro_hex(pelo, 0.55, azul=True))
        self.ropa = t(ropa)
        self.ropa_s = t(oscuro_hex(ropa, 0.68))
        self.ropa_l = t(claro_hex(ropa, 0.25))
        self.ojo = t(ojos)
        self.blanco = t("#ece3da")
        self.blanco_s = t("#c9bdb6")
        self.labio = t("#8a4a40")
        self.linea = teñir(TINTA, tono)


def oscuro_hex(c, f):
    r = hexa(c)
    return "#%02x%02x%02x" % tuple(int(min(255, v * f * 255)) for v in (r[0] * 0.98, r[1] * 0.92, r[2] * 0.95))


def claro_hex(c, t, azul=False):
    r = hexa(c)
    m = (0.7, 0.8, 1.0) if azul else (1, 0.96, 0.9)
    return "#%02x%02x%02x" % tuple(int(min(255, (v + (mm - v) * t) * 255)) for v, mm in zip(r, m))


GENTE = {
    "alex": dict(piel="#b48560", pelo="#1c1418", ropa="#4b5a72", pelo_estilo="alex"),
    "padre": dict(piel="#a9775a", pelo="#241b1a", ropa="#6f8fa6", pelo_estilo="padre"),
    "madre": dict(piel="#b98763", pelo="#2b1a17", ropa="#a8483f", pelo_estilo="madre"),
    "hermana": dict(piel="#c0916b", pelo="#20161a", ropa="#d0a23c", pelo_estilo="hermana"),
    "nino": dict(piel="#bd8c66", pelo="#1e1416", ropa="#6f9a5c", pelo_estilo="alex"),
}


# --- ojos, cejas y boca -----------------------------------------------------------------------------

def _ojo(h, p, x, y, w, ap, mirada, pupila, cerca=True, ojera=0.0):
    """Ojo rasgado de anime: esclerótica, iris con dos brillos, párpado superior grueso y pestañas."""
    ap = max(ap, 0.02)
    alto = w * 0.42 * ap
    arriba = [(x - w / 2, y + 2), (x - w * 0.25, y - alto * 0.85), (x + w * 0.1, y - alto), (x + w / 2, y - alto * 0.3)]
    abajo = [(x + w / 2, y - alto * 0.3), (x + w * 0.2, y + alto * 0.55), (x - w * 0.15, y + alto * 0.5), (x - w / 2, y + 2)]
    contorno = arriba + abajo[1:-1]
    h.cel(contorno, p.blanco, p.blanco_s, luz=(-0.3, -1), prof=alto * 0.35, suave_=True)
    # iris recortado por el ojo
    h.guarda()
    h._camino(contorno, True, True, 1.0)
    h.cr.clip()
    ir = w * 0.235
    ix = x + mirada[0] * w * 0.18
    iy = y + mirada[1] * alto * 0.5 - alto * 0.05
    h.forma(elipse(ix, iy, ir, ir * 1.28), p.ojo)
    h.forma(elipse(ix, iy - ir * 0.15, ir * 0.66, ir * 0.85), oscuro(p.ojo, 0.6))
    h.forma(elipse(ix, iy, ir * 0.36 * pupila, ir * 0.36 * pupila * 1.1), (0.02, 0.01, 0.02))
    h.forma(elipse(ix - ir * 0.38, iy - ir * 0.5, ir * 0.3, ir * 0.36), (1, 0.98, 0.95))
    h.forma(elipse(ix + ir * 0.36, iy + ir * 0.4, ir * 0.14, ir * 0.14), (1, 0.98, 0.95), alfa=0.85)
    # sombra del párpado sobre el ojo
    h.forma([(x - w * 0.6, y - alto * 1.5), (x + w * 0.6, y - alto * 1.5), (x + w * 0.5, y - alto * 0.55),
             (x, y - alto * 0.3), (x - w * 0.5, y - alto * 0.5)], p.piel_s, alfa=0.35)
    h.restaura()
    # línea del párpado superior: gruesa, con pestaña en el extremo
    lid = [(x - w * 0.54, y + 3), (x - w * 0.3, y - alto * 0.8), (x + w * 0.1, y - alto * 1.02),
           (x + w * 0.5, y - alto * 0.35), (x + w * 0.62, y - alto * 0.12 + 3)]
    h.tinta(lid, w * 0.11, p.linea, afila=(0.15, 0.1))
    h.tinta([(x + w * 0.5, y - alto * 0.4), (x + w * 0.66, y - alto * 0.55), (x + w * 0.74, y - alto * 0.8)],
            w * 0.055, p.linea, afila=(0.0, 0.7))
    # párpado inferior fino y ojera
    h.tinta([(x - w * 0.36, y + alto * 0.42), (x, y + alto * 0.62), (x + w * 0.4, y + alto * 0.32)], w * 0.03,
            oscuro(p.linea, 1.6), afila=(0.3, 0.3), alfa=0.8)
    if ojera > 0:
        h.tinta([(x - w * 0.42, y + alto * 1.1), (x, y + alto * 1.45), (x + w * 0.42, y + alto * 1.0)], w * 0.07,
                mezcla(p.piel_s, (0.25, 0.18, 0.3), 0.35), afila=(0.3, 0.3), alfa=0.55 * ojera)


def _ceja(h, p, x, y, w, alto, inclina):
    """Ceja fina que se afila: `alto` la sube y `inclina` inclina el lado interior."""
    y = y - alto * 16
    h.tinta([(x - w / 2, y + inclina * 9 + 6), (x, y - 5), (x + w / 2, y - inclina * 7 + 3)], w * 0.14, p.linea,
            afila=(0.15, 0.55))


def _boca(h, p, x, y, w, forma, abre):
    if forma in ("neutra", "cansada"):
        h.tinta([(x - w / 2, y + 2), (x, y + 6), (x + w / 2, y - 3)], 5.5, p.linea, afila=(0.2, 0.2))
    elif forma == "sonrisa":
        # sonrisa forzada, a medias: solo sube un lado
        h.tinta([(x - w / 2, y + 4), (x - w * 0.1, y + 10), (x + w / 2, y - 12)], 6, p.linea, afila=(0.15, 0.15))
        h.tinta([(x + w * 0.5, y - 12), (x + w * 0.58, y - 22)], 4, p.linea, afila=(0.0, 0.8))
    elif forma == "feliz":
        pts = [(x - w * 0.5, y - 6), (x - w * 0.1, y + 4), (x + w * 0.45, y - 12), (x + w * 0.3, y + 30),
               (x - w * 0.05, y + 38), (x - w * 0.36, y + 22)]
        h.forma(pts, (0.2, 0.05, 0.07))
        h.forma([(x - w * 0.44, y - 4), (x + w * 0.4, y - 10), (x + w * 0.32, y + 8), (x - w * 0.34, y + 8)], p.blanco)
        h.forma(elipse(x + w * 0.02, y + 30, w * 0.2, 7), (0.6, 0.25, 0.28))
        h.contorno(pts, 4, p.linea)
    elif forma == "abierta":
        a = 6 + abre * 26
        pts = [(x - w * 0.42, y), (x - w * 0.2, y - 6), (x + w * 0.25, y - 4), (x + w * 0.46, y + 1),
               (x + w * 0.3, y + a), (x - w * 0.1, y + a * 1.15), (x - w * 0.36, y + a * 0.55)]
        h.forma(pts, (0.13, 0.03, 0.05))
        h.forma([(x - w * 0.3, y - 2), (x + w * 0.35, y - 2), (x + w * 0.3, y + a * 0.3), (x - w * 0.25, y + a * 0.28)],
                p.blanco, alfa=0.95)
        h.forma(elipse(x + w * 0.02, y + a * 0.82, w * 0.22, a * 0.22), (0.5, 0.18, 0.2))
        h.contorno(pts, 4, p.linea)
    elif forma == "grito":
        a = 30 + abre * 60
        pts = [(x - w * 0.5, y - 2), (x - w * 0.3, y - 14), (x + w * 0.3, y - 12), (x + w * 0.55, y),
               (x + w * 0.42, y + a * 0.9), (x, y + a * 1.25), (x - w * 0.4, y + a * 0.85)]
        h.forma(pts, (0.1, 0.02, 0.04))
        h.forma([(x - w * 0.4, y - 8), (x + w * 0.42, y - 8), (x + w * 0.36, y + a * 0.22), (x - w * 0.34, y + a * 0.2)],
                p.blanco)
        h.forma(elipse(x, y + a * 0.95, w * 0.28, a * 0.25), (0.45, 0.1, 0.15))
        h.contorno(pts, 5, p.linea)


# --- Alex ---------------------------------------------------------------------------------------------

def _pelo_atras(h, p, estilo):
    if estilo == "madre":
        h.cel([(-130, -100), (-100, -210), (-20, -252), (66, -246), (130, -190), (160, -80), (170, 60), (176, 210),
               (110, 250), (60, 130), (-70, 120), (-140, 200), (-150, 60)], p.pelo, p.pelo, luz=(-1, -1))
    elif estilo == "hermana":
        h.cel([(-114, -108), (-94, -200), (-30, -246), (50, -250), (120, -206), (148, -112), (138, -8), (108, 52),
               (76, 60)], p.pelo, p.pelo, luz=(-1, -1))
        # cola de caballo que cuelga por detrás
        h.cel([(120, -150), (176, -130), (210, -40), (206, 90), (182, 190), (150, 100), (152, -20)], p.pelo, p.pelo,
              luz=(-1, -1), linea=p.linea, grosor=3.5)
        h.forma(elipse(128, -150, 16, 22, rot=0.4), (0.85, 0.3, 0.3))
    else:
        h.cel([(-112, -110), (-92, -196), (-30, -244), (50, -248), (118, -204), (146, -112), (140, -8), (108, 52),
               (76, 60)], p.pelo, p.pelo, luz=(-1, -1))


def _pelo_frente(h, p, estilo):
    if estilo == "padre":
        # corto, con entradas y canas sobre las orejas
        corto = [(-104, -120), (-80, -184), (-20, -226), (50, -228), (108, -190), (100, -124), (60, -150), (10, -156),
                 (-40, -140), (-70, -118), (-92, -84)]
        h.cel(corto, p.pelo, p.pelo, luz=(-1, -1), linea=p.linea, grosor=4, suave_=False)
        h.forma([(-70, -196), (-10, -218), (48, -216), (0, -200), (-50, -184)], p.pelo_l)
        h.forma([(80, -92), (94, -20), (78, -6), (72, -60)], mezcla(p.pelo, (0.7, 0.7, 0.72), 0.55))
        # bigote
        h.forma([(-118, 98), (-90, 92), (-46, 98), (-30, 112), (-70, 106), (-104, 116)], p.pelo, suave_=True)
    elif estilo == "madre":
        # raya al lado y cortinas de pelo que enmarcan la cara
        h.cel([(-116, -150), (-104, -190), (-40, -236), (40, -238), (108, -196), (104, -110), (60, -150), (-10, -168),
               (-70, -146), (-100, -60), (-108, 20), (-96, 112), (-118, 40), (-124, -40)], p.pelo, p.pelo,
              luz=(-1, -1), linea=p.linea, grosor=4, tension=0.9)
        h.forma([(-90, -196), (-40, -226), (20, -230), (-10, -212), (-60, -190)], p.pelo_l)
        h.forma([(84, -110), (110, -60), (120, 60), (96, 120), (86, 20)], p.pelo)
        # arete
        h.forma(elipse(104, 52, 9, 9), (0.9, 0.78, 0.35))
    elif estilo == "hermana":
        fl = [(-116, -140), (-120, -80), (-96, -118), (-84, -60), (-62, -116), (-30, -70), (-14, -122), (26, -84),
              (40, -130), (84, -100), (104, -140), (100, -204), (40, -246), (-40, -244), (-98, -204)]
        h.cel(fl, p.pelo, p.pelo, luz=(-1, -1), linea=p.linea, grosor=4, suave_=False)
        h.forma([(-96, -186), (-50, -226), (14, -236), (66, -222), (18, -208), (-40, -196), (-84, -160)], p.pelo_l)
    else:
        flequillo = [(-114, -150), (-124, -92), (-98, -128), (-88, -78), (-68, -124), (-40, -90), (-26, -134),
                     (10, -88), (24, -140), (62, -108), (104, -142), (100, -204), (40, -246), (-40, -244),
                     (-98, -204)]
        h.cel(flequillo, p.pelo, p.pelo, luz=(-1, -1), linea=p.linea, grosor=4, suave_=False)
        h.forma([(-96, -186), (-50, -226), (14, -236), (66, -222), (18, -208), (-40, -196), (-84, -160)], p.pelo_l,
                suave_=True)
        h.forma([(54, -196), (92, -180), (100, -156), (68, -170)], p.pelo_l, alfa=0.7)
        h.tinta([(-30, -140), (-34, -104), (-44, -96)], 3, p.linea, afila=(0.1, 0.4), alfa=0.9)
        h.tinta([(24, -148), (30, -112), (22, -100)], 3, p.linea, afila=(0.1, 0.4), alfa=0.9)
        h.forma([(80, -90), (94, -20), (78, -6), (74, -60)], p.pelo)


def alpha_(v):
    return v


def cabeza(h, cx, cy, s=1.0, quien="alex", tono="cena", flip=False, rot=0.0, ap=0.8, mirada=(0.0, 0.0), pupila=1.0,
           ceja=0.0, ceja_in=0.0, boca="neutra", abre=0.0, ojera=0.6, sudor=0.0, palidez=0.0, cuello=True, arrugas=0.0):
    """Cabeza en tres cuartos mirando a la izquierda (`flip` para la derecha)."""
    cfg = GENTE[quien]
    p = Paleta(tono, cfg["piel"], cfg["pelo"], cfg["ropa"])
    estilo = cfg["pelo_estilo"]
    if palidez:
        for nombre in ("piel", "piel_s", "piel_l"):
            c = getattr(p, nombre)
            setattr(p, nombre, mezcla(c, (0.78, 0.72, 0.7), palidez))
    with _pos(h, cx, cy, s, flip, rot):
        _pelo_atras(h, p, estilo)
        if cuello:
            h.cel([(-10, 100), (56, 92), (66, 230), (-26, 240), (-36, 175)], p.piel, p.piel_s, luz=(-1, -0.4), prof=24,
                  linea=p.linea, grosor=4)
            h.forma([(-10, 100), (56, 92), (58, 130), (10, 160), (-24, 150)], p.piel_s, alfa=0.9)
        # cara en tres cuartos: la nariz y los labios asoman en el perfil de la izquierda
        cara = [(-70, -150), (-98, -105), (-104, -62), (-102, -28), (-112, 10), (-142, 54), (-120, 68), (-108, 86),
                (-118, 106), (-108, 124), (-100, 142), (-84, 170), (-46, 188), (2, 174), (46, 134), (76, 80),
                (92, 10), (88, -90), (70, -140)]
        if estilo in ("madre", "hermana"):
            cara[11:14] = [(-90, 166), (-52, 184), (-4, 170)]
        h.cel(cara, p.piel, p.piel_s, luz=(-1, -0.6), prof=38, brillo=p.piel_l, prof_brillo=9, linea=p.linea,
              grosor=4.5, tension=0.8)
        h.cel([(88, -26), (112, -34), (122, 4), (106, 34), (88, 26)], p.piel, p.piel_s, luz=(-1, -1), prof=8,
              linea=p.linea, grosor=3.5)
        h.tinta([(96, -12), (108, -8), (104, 14)], 3, p.piel_s, afila=(0.2, 0.5))
        h.tinta([(-92, -26), (-102, 8), (-134, 50)], 5, p.linea, afila=(0.0, 0.3))
        h.forma([(-136, 56), (-118, 70), (-94, 64), (-84, 78), (-112, 84)], p.piel_s, alfa=0.85)
        h.tinta([(-110, 68), (-94, 64)], 4.5, p.linea, afila=(0.0, 0.6))
        _ojo(h, p, -58, -22, 84, ap, mirada, pupila, ojera=ojera)
        _ojo(h, p, 44, -26, 60, ap, mirada, pupila, ojera=ojera * 0.6)
        _ceja(h, p, -58, -74, 88, ceja, ceja_in)
        _ceja(h, p, 44, -78, 64, ceja, ceja_in * 0.8)
        _boca(h, p, -62, 122, 60, boca, abre)
        if boca in ("neutra", "cansada", "sonrisa"):
            h.tinta([(-92, 144), (-70, 152), (-48, 148)], 3.5, p.piel_s, afila=(0.3, 0.3), alfa=0.8)
        h.tinta([(-72, 40), (-54, 62)], 3.2, p.piel_s, afila=(0.1, 0.5), alfa=0.9)
        if arrugas:
            for dy in (-118, -104):
                h.tinta([(-70, dy), (-20, dy - 4), (30, dy)], 3, p.piel_s, afila=(0.3, 0.3), alfa=0.6 * arrugas)
            h.tinta([(-92, 66), (-84, 104), (-92, 128)], 3, p.piel_s, afila=(0.2, 0.3), alfa=0.6 * arrugas)
        _pelo_frente(h, p, estilo)
        if sudor > 0:
            for i, (dx, dy) in enumerate(((-100, -110), (84, -70), (-86, 20), (66, 60))):
                h.forma([(dx, dy - 12 * sudor), (dx + 6, dy + 2), (dx, dy + 12 * sudor + 4), (dx - 6, dy + 2)],
                        (0.85, 0.92, 1.0), alfa=0.85)
                h.forma(elipse(dx - 2, dy + 2, 2.4, 3.4), (1, 1, 1))


def alex_cabeza(h, cx, cy, s=1.0, **kw):
    cabeza(h, cx, cy, s, quien="alex", **kw)


def busto(h, cx, cy, s, quien, tono="cena", flip=False, ancho=1.0, rot=0.0, capucha=True, largo=620):
    """Hombros y pecho bajo la cabeza (el origen es el centro de la cabeza; los hombros quedan ~260 abajo)."""
    cfg = GENTE[quien]
    p = Paleta(tono, cfg["piel"], cfg["pelo"], cfg["ropa"])
    with _pos(h, cx, cy, s, flip, rot):
        a = 250 * ancho
        h.cel([(-a, largo), (-a, largo - 60), (-a, 372), (-a * 0.92, 296), (-a * 0.62, 252), (-a * 0.28, 232), (-64, 224),
               (64, 224), (a * 0.28, 232), (a * 0.62, 252), (a * 0.92, 296), (a, 372), (a, largo - 60), (a, largo)],
              p.ropa, p.ropa_s, luz=(-1, -0.7), prof=48, brillo=p.ropa_l, prof_brillo=10, linea=p.linea, grosor=4.5,
              tension=0.55)
        # cuello de la prenda
        h.tinta([(-92, 228), (0, 262), (92, 228)], 5, p.linea, afila=(0.1, 0.1), alfa=0.9)
        if quien == "alex" and capucha:
            h.cel([(-100, 214), (-30, 232), (60, 226), (110, 214), (90, 262), (10, 284), (-70, 270)], p.ropa_s,
                  p.ropa_s, linea=p.linea, grosor=4)
            h.tinta([(-30, 256), (-34, 330)], 3.5, p.linea, afila=(0.1, 0.3))
            h.tinta([(30, 258), (36, 322)], 3.5, p.linea, afila=(0.1, 0.3))
        elif quien == "madre":
            for dx in (-150, -60, 60, 150):
                h.forma(elipse(dx, 340 + (dx % 3) * 8, 14, 11), (0.95, 0.85, 0.5), alfa=0.9)
        elif quien == "padre":
            h.forma([(-40, 220), (0, 262), (44, 220)], p.piel_s)
            h.tinta([(-40, 220), (0, 264), (44, 220)], 4, p.linea, afila=(0.1, 0.1))
            h.tinta([(0, 264), (0, 400)], 3, p.linea, afila=(0.1, 0.2))


def _blanco_mascara(tono):
    """Blanco de la máscara: bajo la luna es un blanco frío, no azul."""
    return (0.9, 0.94, 1.0) if tono == "noche" else teñir(hexa("#eeece6"), tono)


# --- las figuras enmascaradas -------------------------------------------------------------------------

def figura(h, cx, cy, s=1.0, tono="noche", ladea=0.0, ancho=1.0, dobladillo=1.0, mascara=True, solo_cara=False):
    """Una figura alta y oscura con máscara blanca lisa. (cx, cy) es el centro de la máscara."""
    negro = teñir(hexa("#0a0c13"), tono)
    borde = teñir(hexa("#3a4e75"), tono)
    tela = teñir(hexa("#141a2a"), tono)
    blanco = _blanco_mascara(tono)
    sombra_m = teñir(hexa("#9fadc4"), tono) if tono != "noche" else (0.55, 0.64, 0.82)
    with _pos(h, cx, cy, s, False, ladea * 0.35):
        if not solo_cara:
            a = 210 * ancho
            capa = [(-96, 150), (-a, 260), (-a * 1.25, 700), (-a * 1.6, 1500 * dobladillo)]
            capa += [(-a * 1.3 + 44 * i, 1500 * dobladillo + (34 if i % 2 else -10)) for i in range(0, 14)]
            capa += [(a * 1.6, 1500 * dobladillo), (a * 1.25, 700), (a, 260), (96, 150)]
            h.cel(capa, negro, negro, luz=(1, -0.3), prof=28, brillo=borde, prof_brillo=7, suave_=True, tension=0.6)
            # pliegues verticales apenas más claros
            for k in range(-3, 4):
                x = k * 62 * ancho
                h.tinta([(x * 0.55, 300), (x * 0.9, 800 * dobladillo), (x * 1.35, 1400 * dobladillo)], 9, tela,
                        afila=(0.2, 0.5), alfa=0.8)
            # brazos largos colgando hasta las rodillas
            for lado in (-1, 1):
                h.tinta([(lado * 150 * ancho, 290), (lado * 205 * ancho, 700), (lado * 190 * ancho + ladea * 20, 1120)],
                        50, tela, afila=(0.05, 0.3))
                h.tinta([(lado * 190 * ancho, 1100), (lado * 178 * ancho, 1230), (lado * 172 * ancho, 1290)], 16, negro,
                        afila=(0.0, 0.8))
        # capucha
        capucha = [(-138, -20), (-120, -150), (-50, -222), (50, -222), (120, -150), (138, -20), (120, 120), (0, 178),
                   (-120, 120)]
        h.cel(capucha, negro, negro, luz=(1, -0.4), prof=22, brillo=borde, prof_brillo=6, tension=0.8)
        if mascara:
            m = [(-72, -96), (-46, -132), (0, -142), (46, -132), (72, -96), (76, -10), (62, 70), (34, 128), (0, 146),
                 (-34, 128), (-62, 70), (-76, -10)]
            h.cel(m, blanco, sombra_m, luz=(-1, -0.6), prof=30, brillo=(1, 1, 1), prof_brillo=8, tension=0.8)
            h.tinta([(-40, -70), (-30, 10), (-24, 60)], 4, sombra_m, afila=(0.3, 0.5), alfa=0.5)


def mascara_cerca(h, cx, cy, s=1.0, tono="noche", ladea=0.0, brillo=1.0):
    """Primer plano: la máscara con la capucha, enorme. Sirve para los planos cerrados de las figuras."""
    with _pos(h, cx, cy, s, False, ladea):
        blanco = _blanco_mascara(tono)
        sombra_m = teñir(hexa("#98a7c0"), tono) if tono != "noche" else (0.5, 0.6, 0.8)
        negro = teñir(hexa("#07090f"), tono)
        borde = teñir(hexa("#4a6090"), tono)
        h.cel([(-330, -60), (-290, -360), (-100, -520), (100, -520), (290, -360), (330, -60), (300, 400), (0, 620),
               (-300, 400)], negro, negro, luz=(1, -0.5), prof=40, brillo=borde, prof_brillo=10, tension=0.8)
        m = [(-190, -260), (-110, -350), (0, -372), (110, -350), (190, -260), (200, -20), (168, 190), (88, 340),
             (0, 380), (-88, 340), (-168, 190), (-200, -20)]
        h.cel(m, blanco, sombra_m, luz=(-1, -0.7), prof=84, brillo=(1, 1, 1), prof_brillo=20, tension=0.8)
        h.tinta([(-100, -160), (-70, 20), (-56, 150)], 8, sombra_m, afila=(0.3, 0.5), alfa=0.45)


def extremidad(h, base, punta, t=0.0, abre=0.6, tono="noche", grosor=1.0):
    """Una extremidad larga y oscura, con codos de más y cuatro dedos larguísimos."""
    negro = teñir(hexa("#090b12"), tono)
    borde = teñir(hexa("#40567f"), tono)
    bx, by = base
    px, py = punta
    dx, dy = px - bx, py - by
    n = math.hypot(dx, dy) or 1.0
    ux, uy = dx / n, dy / n
    nx, ny = -uy, ux
    ondula = math.sin(t * 2.4) * 22
    pts = [(bx, by)]
    for k in (0.28, 0.52, 0.76):
        pts.append((bx + dx * k + nx * (ondula * (1 if k < 0.6 else -0.7) + 40 * (k - 0.5)),
                    by + dy * k + ny * (ondula * (1 if k < 0.6 else -0.7) + 40 * (k - 0.5))))
    mano = (px - ux * 90, py - uy * 90)
    pts.append(mano)
    h.tinta([(x + 4, y - 4) for x, y in pts], 66 * grosor, borde, afila=(0.05, 0.25), alfa=0.9)
    h.tinta(pts, 60 * grosor, negro, afila=(0.05, 0.25))
    for x, y in pts[1:-1]:
        h.forma(elipse(x, y, 36 * grosor, 36 * grosor), negro)
    h.forma(elipse(mano[0], mano[1], 44 * grosor, 48 * grosor, rot=math.atan2(uy, ux)), negro)
    for i in range(4):
        ang = (i - 1.5) * (0.28 + 0.3 * abre) + math.atan2(uy, ux)
        L = (120 + 22 * (i % 2)) * grosor
        codo = (mano[0] + math.cos(ang) * L * 0.55, mano[1] + math.sin(ang) * L * 0.55 + 10 * math.sin(t * 3 + i))
        fin = (mano[0] + math.cos(ang + 0.18) * L, mano[1] + math.sin(ang + 0.18) * L)
        h.tinta([mano, codo, fin], 24 * grosor, borde, afila=(0.0, 0.85), alfa=0.9)
        h.tinta([mano, codo, fin], 19 * grosor, negro, afila=(0.0, 0.85))


# --- brazo, celular, comida --------------------------------------------------------------------------

def antebrazo(h, cx, cy, s=1.0, rot=0.0, tono="cena", incision=0.0, puntadas=11, palidez=0.0, mano=True):
    """El antebrazo izquierdo de Alex, horizontal (codo a la derecha). Con `incision` > 0 sale la herida suturada."""
    cfg = GENTE["alex"]
    p = Paleta(tono, cfg["piel"], cfg["pelo"], cfg["ropa"])
    piel, piel_s, piel_l = p.piel, p.piel_s, p.piel_l
    if palidez:
        piel, piel_s, piel_l = (mezcla(c, (0.78, 0.72, 0.7), palidez) for c in (piel, piel_s, piel_l))
    with _pos(h, cx, cy, s, False, rot):
        cuerpo = [(-360, -50), (-250, -76), (-100, -92), (60, -100), (230, -128), (420, -160), (470, 0), (420, 140),
                  (230, 122), (60, 92), (-100, 76), (-250, 50), (-360, 40)]
        h.cel(cuerpo, piel, piel_s, luz=(-0.2, -1), prof=52, brillo=piel_l, prof_brillo=12, linea=p.linea, grosor=5,
              tension=0.8)
        # vello, venas y tendones
        h.tinta([(-330, -8), (-160, -14), (20, -6)], 3.5, piel_s, afila=(0.3, 0.3), alfa=0.6)
        h.tinta([(-280, 22), (-120, 30), (40, 40)], 3, piel_s, afila=(0.3, 0.3), alfa=0.5)
        if mano:
            palma = [(-340, -66), (-400, -98), (-462, -78), (-478, 6), (-458, 76), (-396, 98), (-340, 58)]
            h.cel(palma, piel, piel_s, luz=(-0.2, -1), prof=26, linea=p.linea, grosor=4.5)
            for i, (y0, largo_) in enumerate(((-52, 118), (-14, 132), (26, 126), (62, 104))):
                curva_ = [(-450, y0), (-450 - largo_ * 0.6, y0 + 6 + i * 2), (-450 - largo_, y0 + 22 + i * 3)]
                h.tinta(curva_, 40, p.linea, afila=(0.0, 0.45))
                h.tinta(curva_, 32, piel, afila=(0.0, 0.45))
                h.tinta([(x, y + 9) for x, y in curva_], 10, piel_s, afila=(0.0, 0.5), alfa=0.9)
            pulgar = [(-392, -92), (-450, -132), (-504, -128)]
            h.tinta(pulgar, 40, p.linea, afila=(0.0, 0.4))
            h.tinta(pulgar, 32, piel, afila=(0.0, 0.4))
        if incision > 0:
            x0, x1 = -230, 250
            xf = x0 + (x1 - x0) * min(incision, 1)
            eje = [(x0, -10), (x0 + (x1 - x0) * 0.3, -18), (x0 + (x1 - x0) * 0.65, -12), (x1, -22)]
            # piel inflamada alrededor
            h.tinta(eje, 64, mezcla(piel, (0.75, 0.2, 0.25), 0.55), afila=(0.15, 0.15), alfa=0.6)
            h.tinta(eje, 34, mezcla(piel, (0.7, 0.12, 0.16), 0.75), afila=(0.15, 0.15), alfa=0.85)
            # la hendidura, profunda y oscura
            h.tinta(eje, 15, (0.24, 0.02, 0.05), afila=(0.12, 0.12))
            h.tinta(eje, 5, (0.05, 0.0, 0.02), afila=(0.2, 0.2))
            pts = curva(eje, pasos=20)
            for k in range(puntadas):
                u = (k + 0.5) / puntadas
                if u > incision:
                    break
                cx0, cy0 = pts[int(u * (len(pts) - 1))]
                h.tinta([(cx0 - 5, cy0 - 42), (cx0 + 3, cy0), (cx0 - 4, cy0 + 42)], 6, (0.03, 0.03, 0.05),
                        afila=(0.1, 0.1))
                h.forma(elipse(cx0 - 5, cy0 - 42, 5, 5), (0.03, 0.03, 0.05))
                h.forma(elipse(cx0 - 4, cy0 + 42, 5, 5), (0.03, 0.03, 0.05))
                h.tinta([(cx0 - 3, cy0 - 20), (cx0 + 2, cy0 - 4)], 2.5, (0.5, 0.5, 0.55), afila=(0.0, 0.6), alfa=0.7)


def celular(h, cx, cy, s=1.0, rot=0.0, tono="cena", encendido=True):
    with _pos(h, cx, cy, s, False, rot):
        h.cel([(-150, -280), (150, -280), (150, 280), (-150, 280)], (0.05, 0.05, 0.07), (0.02, 0.02, 0.03), suave_=False,
              luz=(-1, -1), prof=8, linea=(0.02, 0.02, 0.03), grosor=4)
        pant = (0.72, 0.85, 1.0) if encendido else (0.05, 0.06, 0.08)
        h.rect(-132, -252, 132, 246, pant)
        if encendido:
            h.rect(-132, -252, 132, -200, (0.2, 0.55, 0.42))
            for i, (x, y, w, c) in enumerate(((-118, -170, 150, "#ffffff"), (-10, -90, 128, "#a6e3a0"),
                                             (-118, -10, 170, "#ffffff"), (-30, 70, 148, "#a6e3a0"),
                                             (-118, 150, 130, "#ffffff"))):
                h.forma([(x, y), (x + w, y), (x + w, y + 60), (x, y + 60)], hexa(c), suave_=False)
                h.rect(x + 12, y + 14, x + w - 14, y + 22, (0.55, 0.6, 0.6))
                h.rect(x + 12, y + 34, x + w - 40, y + 42, (0.6, 0.65, 0.65))


def chilaquiles(h, cx, cy, s=1.0, tono="manana"):
    """Un plato de chilaquiles rojos con crema, queso y cebolla."""
    t = lambda c: teñir(hexa(c), tono)
    with _pos(h, cx, cy, s):
        h.cel(elipse(0, 0, 330, 120), t("#ece9e0"), t("#b9b6ae"), luz=(-1, -1), prof=24, linea=t("#3a2a24"), grosor=4)
        h.forma(elipse(0, -6, 250, 84), t("#d6d2c6"))
        rng = __import__("random").Random(3)
        for _ in range(26):
            x, y = rng.uniform(-210, 210), rng.uniform(-58, 50)
            r = rng.uniform(34, 56)
            a = rng.uniform(0, 6.28)
            tri = [(x + r * math.cos(a + k * 2.094), y + r * 0.6 * math.sin(a + k * 2.094)) for k in range(3)]
            h.cel(tri, t("#c0432c"), t("#8a2a1c"), luz=(-1, -1), prof=8, suave_=False, linea=t("#5a1a10"), grosor=2.5)
        for i in range(3):
            h.tinta([(-180 + i * 30, -30 + i * 28), (-40 + i * 40, -50 + i * 20), (140 + i * 20, -22 + i * 24)], 14,
                    t("#f6efe0"), afila=(0.2, 0.2))
        for _ in range(18):
            h.forma(elipse(rng.uniform(-190, 190), rng.uniform(-50, 46), 6, 4), t("#f0f0e6"))
        for _ in range(10):
            h.forma(elipse(rng.uniform(-190, 190), rng.uniform(-50, 46), 4, 3), t("#4f8a3c"))
