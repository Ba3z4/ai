"""Fondos pintados: el comedor (noche y mañana), el cuarto de Alex, su techo y el parque del recuerdo.

Como en la animación de los 90, los fondos son pinturas quietas sin tinta; se dibujan una vez
por plano (con textura de pintura) y la cámara se mueve sobre ellos. Lo que se mueve dentro
del fondo (el ventilador, las sombras que se estiran) se dibuja aparte en cada cuadro.
"""

import math

import numpy as np
from PIL import Image, ImageFilter

from dibujo import H, W, Lienzo, elipse, hexa, mezcla, oscuro, textura


class Fondo:
    """Pinta `dibujar(lz)` una vez, le pone textura de pintura y lo guarda como superficie.

    transparente: la capa conserva su canal alfa (para ponerla delante de los personajes).
    desenfoque: radio en px virtuales, para fondos fuera de foco.
    """

    def __init__(self, dibujar, ancho, margen=160, calidad=1.0, grano=0.07, semilla=1, transparente=False,
                 desenfoque=0):
        self.margen = margen
        self.calidad = calidad
        lz = Lienzo(ancho * calidad, semilla=semilla, margen=margen)
        lz.hervor = 0
        lz.nuevo(0, fondo=None if transparente else (0, 0, 0))
        dibujar(lz)
        lz.sup.flush()
        datos = np.ndarray((lz.h, lz.w, 4), np.uint8, lz.sup.get_data(), strides=(lz.sup.get_stride(), 4, 1))
        arr = datos.astype(np.float32)
        if grano:
            tex = textura(lz.h, lz.w, semilla)[..., None]
            alfa = arr[..., 3:4]
            arr[..., :3] = np.clip(arr[..., :3] * (1 + tex * grano) + tex * grano * 12 * (alfa / 255), 0, alfa)
        if desenfoque:
            img = Image.fromarray(arr.astype(np.uint8), "RGBA")  # datos premultiplicados: el desenfoque es lineal
            arr = np.asarray(img.filter(ImageFilter.GaussianBlur(desenfoque * lz.esc)), np.float32)
        datos[:] = np.clip(arr + 0.5, 0, 255).astype(np.uint8)
        lz.sup.mark_dirty()
        self.sup = lz.sup

    def pintar(self, lz, alfa=1.0):
        lz.pintar_superficie(self.sup, -self.margen, -self.margen, 1 / self.calidad, alfa)


# --- el cuarto de Alex, de noche ------------------------------------------------------------

# Punto de fuga y pared del fondo (vista desde la cama, un poco incorporado).
PF = (540, 760)
PARED = (120, 330, 960, 1170)  # x0, y0, x1, y1

C_NOCHE = {
    "pared": hexa("#1c2331"),
    "pared_luna": hexa("#2b394c"),
    "techo": hexa("#121822"),
    "piso": hexa("#18130f"),
    "puerta": hexa("#2a3240"),
    "marco": hexa("#343d4c"),
    "hueco": hexa("#030305"),
    "ropa": hexa("#0d1016"),
    "vidrio": hexa("#6f93b3"),
    "cortina": hexa("#1a2130"),
    "mueble": hexa("#21160f"),
    "espejo": hexa("#1b2531"),
    "cobija": hexa("#1d2534"),
    "cobija_sombra": hexa("#10151e"),
    "cobija_luz": hexa("#34445c"),
    "tapete": hexa("#15181f"),
}


def _poli(lz, pts, color, **kw):
    lz.forma(np.array(pts, float), color, tinta=False, suave=False, **kw)


def cuarto_noche(lz, luna=1.0, puerta_abierta=0.28):
    c = C_NOCHE
    x0, y0, x1, y1 = PARED
    M = 200
    # Techo, paredes laterales y piso en perspectiva.
    _poli(lz, [(-M, -M), (W + M, -M), (x1, y0), (x0, y0)], c["techo"])
    _poli(lz, [(-M, -M), (x0, y0), (x0, y1), (-M, y1 + 190)], oscuro(c["pared"], 0.72))
    _poli(lz, [(W + M, -M), (x1, y0), (x1, y1), (W + M, y1 + 190)], oscuro(c["pared"], 0.8))
    _poli(lz, [(x0, y1), (x1, y1), (W + M, y1 + 190), (W + M, H + M), (-M, H + M), (-M, y1 + 190)], c["piso"])
    _poli(lz, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], c["pared"])
    # Tablas del piso.
    for i in range(-6, 9):
        xa = PF[0] + (x0 - PF[0]) + i * 110
        lz.pincel([(PF[0] + (xa - PF[0]) * 1.0, y1), (PF[0] + (xa - PF[0]) * 2.4, y1 + 520)], 3, oscuro(c["piso"], 0.55))
    # Degradados de las esquinas: la oscuridad se junta ahí.
    lz.degradado(x0, 0, x0 + 260, 0, [(0, (0, 0, 0), 0.75), (1, (0, 0, 0), 0)], rect=(x0, y0, 260, y1 - y0))
    lz.degradado(x1, 0, x1 - 220, 0, [(0, (0, 0, 0), 0.7), (1, (0, 0, 0), 0)], rect=(x1 - 220, y0, 220, y1 - y0))
    lz.degradado(0, y0, 0, y0 + 180, [(0, (0, 0, 0), 0.55), (1, (0, 0, 0), 0)], rect=(x0, y0, x1 - x0, 180))

    # Ventana con luz de luna.
    vx0, vy0, vx1, vy1 = 470, 470, 690, 840
    lz.resplandor((vx0 + vx1) / 2, (vy0 + vy1) / 2, 330, c["pared_luna"], 0.55 * luna)
    _poli(lz, [(vx0 - 16, vy0 - 16), (vx1 + 16, vy0 - 16), (vx1 + 16, vy1 + 22), (vx0 - 16, vy1 + 22)], c["marco"])
    lz.degradado(0, vy0, 0, vy1, [(0, oscuro(c["vidrio"], 0.9), 1), (1, oscuro(c["vidrio"], 0.55), 1)],
                 rect=(vx0, vy0, vx1 - vx0, vy1 - vy0))
    lz.resplandor(640, 540, 60, (0.85, 0.92, 1.0), 0.8 * luna)  # la luna
    lz.forma(elipse(640, 540, 26, 26, 20), hexa("#e8eef2"), tinta=False)
    # Ramas afuera.
    for rama in ([(700, 690), (620, 640), (560, 650), (500, 600)], [(620, 640), (600, 580), (560, 540)],
                 [(700, 790), (640, 760), (590, 780)]):
        lz.pincel(rama, 9, hexa("#141b25"))
    _poli(lz, [(vx0, (vy0 + vy1) / 2 - 7), (vx1, (vy0 + vy1) / 2 - 7), (vx1, (vy0 + vy1) / 2 + 7), (vx0, (vy0 + vy1) / 2 + 7)], c["marco"])
    _poli(lz, [((vx0 + vx1) / 2 - 7, vy0), ((vx0 + vx1) / 2 + 7, vy0), ((vx0 + vx1) / 2 + 7, vy1), ((vx0 + vx1) / 2 - 7, vy1)], c["marco"])
    # Cortinas.
    for lado in (-1, 1):
        bx = vx0 - 10 if lado < 0 else vx1 + 10
        pts = [(bx, vy0 - 40), (bx + lado * 70, vy0 - 40), (bx + lado * 80, vy1 + 90), (bx + lado * 60, vy1 + 120),
               (bx + lado * 20, vy1 + 100), (bx - lado * 12, vy1 + 60), (bx - lado * 6, vy0 + 200)]
        lz.forma(np.array(pts, float), c["cortina"], sombra=oscuro(c["cortina"], 0.6), luz=(-lado * 18, 0), tinta=False)
        for k in range(3):
            fx = bx + lado * (18 + k * 20)
            lz.pincel([(fx, vy0 - 20), (fx + lado * 6, vy1 + 40)], 4, oscuro(c["cortina"], 0.5))
    _poli(lz, [(vx0 - 110, vy0 - 52), (vx1 + 110, vy0 - 52), (vx1 + 110, vy0 - 36), (vx0 - 110, vy0 - 36)], hexa("#0e1219"))

    # Puerta entreabierta a la izquierda, con ropa colgada.
    px0, py0, px1 = 150, 600, 360
    _poli(lz, [(px0 - 16, py0 - 16), (px1 + 16, py0 - 16), (px1 + 16, y1), (px0 - 16, y1)], c["marco"])
    _poli(lz, [(px0, py0), (px1, py0), (px1, y1), (px0, y1)], c["hueco"])
    abre = puerta_abierta
    borde = px0 + (px1 - px0) * (1 - abre)
    _poli(lz, [(px0, py0 - 4), (borde, py0 + 26), (borde, y1 + 12), (px0, y1)], c["puerta"],
          sombra=oscuro(c["puerta"], 0.7), luz=(-40, 0))
    for (a, b) in ((0.12, 0.42), (0.55, 0.9)):
        yy0, yy1 = py0 + 40 + (y1 - py0) * a, py0 + 40 + (y1 - py0) * b * 0.9
        _poli(lz, [(px0 + 24, yy0), (borde - 22, yy0 + 12), (borde - 22, yy1 - 6), (px0 + 24, yy1)], oscuro(c["puerta"], 0.82))
    lz.forma(elipse(borde - 20, (py0 + y1) / 2 + 20, 7, 7, 10), hexa("#6d6a5e"), tinta=False)
    # Sudadera y chamarra colgadas (de noche parecen alguien).
    for gx, largo in ((px0 + 40, 330), (px0 + 95, 280)):
        pts = [(gx, py0 + 40), (gx + 30, py0 + 50), (gx + 48, py0 + 120), (gx + 44, py0 + largo),
               (gx + 10, py0 + largo + 20), (gx - 26, py0 + largo - 10), (gx - 30, py0 + 110), (gx - 16, py0 + 50)]
        lz.forma(np.array(pts, float), c["ropa"], tinta=False)

    # Cómoda con espejo a la derecha.
    mx0, my0, mx1, my1 = 720, 610, 930, 900
    _poli(lz, [(mx0 - 14, my0 - 14), (mx1 + 14, my0 - 14), (mx1 + 14, my1 + 10), (mx0 - 14, my1 + 10)], oscuro(c["mueble"], 0.9))
    lz.degradado(mx0, my0, mx1, my1, [(0, oscuro(c["espejo"], 1.2), 1), (0.5, c["espejo"], 1), (1, oscuro(c["espejo"], 0.6), 1)],
                 rect=(mx0, my0, mx1 - mx0, my1 - my0))
    lz.mancha(np.array([(mx0 + 30, my1), (mx0 + 90, my0), (mx0 + 130, my0), (mx0 + 70, my1)]), (0.6, 0.7, 0.8), 0.07, suave=False)
    dx0, dy0 = 690, 920
    _poli(lz, [(dx0, dy0), (x1 + 4, dy0), (x1 + 4, y1), (dx0, y1)], c["mueble"])
    _poli(lz, [(dx0 - 12, dy0 - 16), (x1 + 8, dy0 - 16), (x1 + 8, dy0 + 4), (dx0 - 12, dy0 + 4)], oscuro(c["mueble"], 1.3))
    for k in range(3):
        yy = dy0 + 28 + k * 76
        _poli(lz, [(dx0 + 14, yy), (x1 - 12, yy), (x1 - 12, yy + 64), (dx0 + 14, yy + 64)], oscuro(c["mueble"], 0.78))
        for kx in (dx0 + 70, x1 - 70):
            lz.forma(elipse(kx, yy + 32, 6, 6, 10), hexa("#3b2d20"), tinta=False)
    # Cosas sobre la cómoda.
    _poli(lz, [(720, dy0 - 16), (720, dy0 - 70), (738, dy0 - 70), (738, dy0 - 16)], hexa("#2c3440"))
    _poli(lz, [(760, dy0 - 16), (760, dy0 - 44), (820, dy0 - 44), (820, dy0 - 16)], hexa("#252018"))
    _poli(lz, [(860, dy0 - 16), (860, dy0 - 80), (920, dy0 - 80), (920, dy0 - 16)], hexa("#1a1f28"))

    # Tapete.
    _poli(lz, [(60, 1260), (1020, 1260), (1180, 1500), (-100, 1500)], c["tapete"])

    # Rayo de luna sobre el piso y la cama.
    lz.mancha(np.array([(vx0, vy1), (vx1, vy1), (900, 1700), (330, 1700)]), (0.55, 0.7, 0.9), 0.05 * luna, suave=False)
    return lz


def cobija(lz, respira=0.0, luna=1.0):
    """Primer plano: el pie de la cama con la cobija (se dibuja encima de todo)."""
    c = C_NOCHE
    sube = respira * 6
    pts = [(-200, 1420 - sube), (120, 1400 - sube), (300, 1380 - sube), (440, 1330 - sube * 1.5),
           (560, 1345 - sube * 1.5), (700, 1390 - sube), (900, 1370 - sube), (1300, 1400), (1300, 2200), (-200, 2200)]
    lz.forma(np.array(pts, float), c["cobija"], sombra=c["cobija_sombra"], luz=(30, 40),
             brillo=c["cobija_luz"], contraluz=(0, -10 * luna), grosor=5)
    for pl in ([(120, 1500), (300, 1560), (420, 1700)], [(620, 1450), (720, 1600), (700, 1800)],
               [(860, 1480), (980, 1620)], [(260, 1780), (420, 1850), (520, 1960)], [(470, 1380), (520, 1470)]):
        lz.pincel(pl, 9, oscuro(c["cobija_sombra"], 0.6))


def ventilador(lz, angulo, luz=1.0):
    """Ventilador de techo visto desde abajo y un poco de frente."""
    cx, cy = 540, 170
    col = hexa("#1a1d24")
    lz.forma(np.array([(532, -60), (548, -60), (548, cy - 30), (532, cy - 30)]), col, suave=False, grosor=4)
    for k in range(5):
        a = angulo + k * 2 * math.pi / 5
        dx, dy = math.cos(a), math.sin(a) * 0.28
        punta = (cx + dx * 420, cy + dy * 420)
        base = (cx + dx * 60, cy + dy * 60)
        nx, ny = -dy * 0.9, dx * 0.9
        ancho = 36 + 14 * abs(math.sin(a))
        pts = [(base[0] + nx * 22, base[1] + ny * 12), (punta[0] + nx * ancho, punta[1] + ny * ancho * 0.4),
               (punta[0] + dx * 18, punta[1] + dy * 18), (punta[0] - nx * ancho, punta[1] - ny * ancho * 0.4),
               (base[0] - nx * 22, base[1] - ny * 12)]
        lz.forma(np.array(pts, float), hexa("#191c22"), sombra=hexa("#0e1014"), luz=(0, -8), grosor=4)
    lz.forma(elipse(cx, cy, 70, 42, 18), hexa("#23272f"), sombra=hexa("#101216"), luz=(0, -12), grosor=4)
    lz.forma(elipse(cx, cy + 34, 44, 30, 16), hexa("#3b4150"), sombra=hexa("#1b1e25"), luz=(-6, -8), grosor=4)
    for dx in (-14, 12):
        lz.linea([(cx + dx, cy + 50), (cx + dx, cy + 140)], 2)
        lz.forma(elipse(cx + dx, cy + 146, 5, 8, 8), hexa("#111111"), tinta=False)


# --- el comedor -------------------------------------------------------------------------------

def _cuadros(lz, dia):
    """Fotos familiares enmarcadas en la pared."""
    marcos = [(80, 250, 180, 220), (300, 200, 250, 200), (600, 240, 160, 210), (810, 250, 190, 230),
              (130, 530, 210, 160), (390, 470, 150, 200), (610, 520, 220, 170), (880, 540, 140, 170)]
    rng = np.random.default_rng(4)
    for i, (x, y, w, h) in enumerate(marcos):
        madera = hexa("#3a2416") if i % 3 else hexa("#2a2a2a")
        lz.forma(np.array([(x + 8, y + 10), (x + w + 10, y + 12), (x + w + 10, y + h + 14), (x + 8, y + h + 12)], float),
                 (0, 0, 0), tinta=False, suave=False, alfa=0.35)
        lz.forma(np.array([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], float), madera, suave=False, tinta=False)
        foto = hexa("#b9a58a") if i % 2 else hexa("#9d9a92")
        if dia:
            foto = mezcla(foto, (1, 1, 1), 0.1)
        m = 14
        lz.forma(np.array([(x + m, y + m), (x + w - m, y + m), (x + w - m, y + h - m), (x + m, y + h - m)], float),
                 foto, suave=False, tinta=False)
        # Siluetas de la familia en cada foto.
        n = 1 + int(rng.integers(0, 4))
        for k in range(n):
            cx = x + m + (w - 2 * m) * (k + 0.5) / n
            r = min(w, h) * 0.1
            base = y + h - m
            sombra = oscuro(foto, 0.55)
            lz.forma(elipse(cx, base - r * 3.2, r, r * 1.15, 10), sombra, tinta=False)
            lz.forma(np.array([(cx - r * 1.6, base), (cx - r * 1.3, base - r * 2), (cx + r * 1.3, base - r * 2),
                               (cx + r * 1.6, base)], float), sombra, tinta=False)
        lz.forma(np.array([(x + m, y + m), (x + w - m, y + m), (x + m + 30, y + h - m)], float), (1, 1, 1), tinta=False,
                 suave=False, alfa=0.06)


def pared_comedor(lz, dia=False):
    """La pared de terracota con fotos y el trastero con ollas de barro (vista de frente)."""
    M = 200
    muro = hexa("#a55a3a") if dia else hexa("#8a4630")
    lz.forma(np.array([(-M, -M), (W + M, -M), (W + M, H + M), (-M, H + M)], float), muro, tinta=False, suave=False)
    if dia:
        lz.degradado(-M, 0, W + M, 0, [(0, (1, 0.97, 0.9), 0.28), (0.6, (1, 1, 1), 0.0)])
    else:
        lz.resplandor(540, 380, 900, hexa("#ffb060"), 0.35)
        lz.degradado(0, -M, 0, 1100, [(0, (0, 0, 0), 0.55), (0.35, (0, 0, 0), 0.0)])
        lz.degradado(-M, 0, W + M, 0, [(0, (0, 0, 0), 0.6), (0.25, (0, 0, 0), 0), (0.75, (0, 0, 0), 0), (1, (0, 0, 0), 0.6)])
    # Grietas y manchas de humedad.
    for g in ([(40, 900), (80, 820), (70, 760), (110, 700)], [(980, 120), (940, 180), (960, 240)]):
        lz.pincel(g, 3, oscuro(muro, 0.6))
    _cuadros(lz, dia)
    # Trastero con ollas.
    tx0, ty0, tx1, ty1 = 230, 830, 850, 1100
    madera = hexa("#4a2c1a")
    lz.forma(np.array([(tx0, ty0), (tx1, ty0), (tx1, ty1), (tx0, ty1)], float), madera, sombra=oscuro(madera, 0.7),
             luz=(0, -20), tinta=False, suave=False)
    lz.forma(np.array([(tx0 - 14, ty0 - 16), (tx1 + 14, ty0 - 16), (tx1 + 14, ty0 + 6), (tx0 - 14, ty0 + 6)], float),
             oscuro(madera, 1.3), tinta=False, suave=False)
    barro = hexa("#9c5530")
    for i, (ox, alto, ancho) in enumerate(((300, 110, 70), (410, 80, 90), (530, 140, 64), (640, 90, 80), (760, 120, 60))):
        olla = [(ox - ancho * 0.45, ty0 - 14), (ox - ancho * 0.6, ty0 - alto * 0.45), (ox - ancho * 0.35, ty0 - alto * 0.85),
                (ox - ancho * 0.25, ty0 - alto), (ox + ancho * 0.25, ty0 - alto), (ox + ancho * 0.35, ty0 - alto * 0.85),
                (ox + ancho * 0.6, ty0 - alto * 0.45), (ox + ancho * 0.45, ty0 - 14)]
        color = barro if i % 2 == 0 else hexa("#4f6e4a")
        lz.forma(np.array(olla, float), color, sombra=oscuro(color, 0.6), luz=(-10, -6), tinta=False)
        lz.pincel([(ox - ancho * 0.4, ty0 - alto * 0.5), (ox + ancho * 0.4, ty0 - alto * 0.5)], 4, hexa("#e0c49a"), alfa=0.6)


def lampara(lz, encendida=True, vaiven=0.0):
    """Lámpara colgante sobre la mesa."""
    lz.guardar()
    lz.mover(540, -200, 1, rot=vaiven)
    lz.linea([(0, 0), (0, 480)], 4)
    pantalla = [(-90, 480), (90, 480), (150, 590), (-150, 590)]
    lz.forma(np.array(pantalla, float), hexa("#3d4a36"), sombra=hexa("#232b1f"), luz=(-12, 0), suave=False)
    if encendida:
        lz.forma(elipse(0, 596, 150, 24, 20), hexa("#ffe2a0"), grosor=4)
        lz.resplandor(0, 620, 260, hexa("#ffc070"), 0.55)
    else:
        lz.forma(elipse(0, 596, 150, 24, 20), hexa("#6f6a5a"), grosor=4)
    lz.restaurar()


def mesa_comedor(lz, dia=False, platos=True):
    """La mesa con mantel floreado en perspectiva (plano abierto de la cena)."""
    mantel = hexa("#e4d4b4") if dia else hexa("#d9c19a")
    borde = [(300, 1000), (780, 1000), (1400, 2200), (-320, 2200)]
    lz.forma(np.array(borde, float), mantel, sombra=oscuro(mantel, 0.78), luz=(0, -30), suave=False, grosor=5)

    def flores():
        rng = np.random.default_rng(11)
        for _ in range(140):
            v = rng.random()
            yy = 1000 + v ** 1.6 * 1200
            u = rng.random()
            x0 = 300 + (-320 - 300) * (yy - 1000) / 1200
            x1 = 780 + (1400 - 780) * (yy - 1000) / 1200
            xx = x0 + (x1 - x0) * u
            r = 4 + 18 * (yy - 1000) / 1200
            col = hexa("#c4566a") if rng.random() < 0.6 else hexa("#6f9a5a")
            lz.forma(elipse(xx, yy, r * 1.4, r * 0.8, 8), col, tinta=False, hervor=0, alfa=0.7)

    lz.recorte(np.array(borde, float), suave=False)
    flores()
    if not dia:
        lz.resplandor(540, 1150, 600, hexa("#ffb060"), 0.28, ry=260)
    lz.restaurar()
    if not platos:
        return
    # Cazuela, canasta de tortillas, jarra de agua de jamaica, platos y vasos.
    barro = hexa("#94502c")
    lz.forma(elipse(560, 1190, 150, 58, 20), oscuro(barro, 0.8), grosor=4)
    lz.forma(elipse(560, 1172, 130, 44, 20), hexa("#7a3a1c"), grosor=3)
    lz.forma(elipse(560, 1176, 110, 34, 18), hexa("#a4552a"), tinta=False)
    for k in range(6):
        lz.forma(elipse(510 + k * 20, 1170 + (k % 2) * 8, 14, 7, 8), hexa("#e3b064"), tinta=False)
    lz.forma(elipse(390, 1080, 90, 40, 18), hexa("#b98a4a"), grosor=4)
    lz.forma(np.array([(330, 1060), (390, 1020), (450, 1062), (400, 1070)], float), hexa("#f2ece0"), grosor=3)
    jarra = [(680, 1080), (672, 1000), (690, 980), (740, 980), (756, 1000), (748, 1080)]
    lz.forma(np.array(jarra, float), hexa("#8e1f3c"), sombra=hexa("#5a1026"), luz=(-8, 0), grosor=4, alfa=0.92)
    lz.forma(elipse(714, 984, 34, 10, 12), hexa("#c9d6de"), grosor=3, alfa=0.6)
    for (px, py, r) in ((540, 1030, 60), (330, 1130, 80), (760, 1120, 80), (560, 1440, 140)):
        lz.forma(elipse(px, py, r, r * 0.38, 20), hexa("#f1ece0"), grosor=4)
        lz.forma(elipse(px, py, r * 0.8, r * 0.3, 20), hexa("#3f6aa0"), tinta=False)
        lz.forma(elipse(px, py, r * 0.7, r * 0.26, 20), hexa("#f1ece0"), tinta=False)
        lz.forma(elipse(px + r * 0.1, py - r * 0.02, r * 0.4, r * 0.14, 12), hexa("#b8733a"), tinta=False)
    for (vx, vy, h) in ((440, 1000, 60), (250, 1110, 80), (860, 1090, 80)):
        lz.forma(np.array([(vx - h * 0.3, vy - h), (vx + h * 0.3, vy - h), (vx + h * 0.25, vy), (vx - h * 0.25, vy)], float),
                 hexa("#cfe0e6"), grosor=3, suave=False, alfa=0.5)


def silla(lz, x, y, s):
    lz.guardar()
    lz.mover(x, y, s)
    madera = hexa("#3b2213")
    for lado in (-1, 1):
        lz.forma(np.array([(lado * 110 - 14, -260), (lado * 110 + 14, -260), (lado * 110 + 14, 200), (lado * 110 - 14, 200)],
                          float), madera, suave=False, grosor=4)
    lz.forma(np.array([(-130, -300), (130, -300), (124, -230), (-124, -230)], float), madera, sombra=oscuro(madera, 0.6),
             luz=(0, -8), grosor=4)
    lz.restaurar()


# --- el techo (visto desde la cama) -----------------------------------------------------------

def techo(lz):
    M = 400
    base = hexa("#1e2530")
    lz.forma(np.array([(-M, -M), (W + M, -M), (W + M, H + M), (-M, H + M)], float), base, tinta=False, suave=False)
    lz.resplandor(700, 1100, 900, hexa("#3c5068"), 0.5)
    rng = np.random.default_rng(3)
    for _ in range(420):
        x, y = rng.uniform(-M, W + M), rng.uniform(-M, H + M)
        lz.forma(elipse(x, y, rng.uniform(2, 6), rng.uniform(2, 6), 6), oscuro(base, rng.uniform(0.6, 1.3)),
                 tinta=False, hervor=0)
    lz.pincel([(120, 300), (220, 360), (260, 470), (380, 520), (420, 640)], 4, hexa("#0c1016"))
    lz.pincel([(260, 470), (200, 560)], 3, hexa("#0c1016"))
    # Molduras de las paredes en las orillas.
    lz.degradado(-M, 0, 160, 0, [(0, (0, 0, 0), 0.9), (1, (0, 0, 0), 0)], rect=(-M, -M, 160 + M, H + 2 * M))
    lz.degradado(W + M, 0, W - 160, 0, [(0, (0, 0, 0), 0.9), (1, (0, 0, 0), 0)], rect=(W - 160, -M, 160 + M, H + 2 * M))


def ventilador_techo(lz, cx, cy, angulo, s=1.0):
    """El ventilador visto justo desde abajo."""
    lz.guardar()
    lz.mover(cx, cy, s)
    for k in range(5):
        a = angulo + k * 2 * math.pi / 5
        lz.guardar()
        lz.mover(0, 0, 1, rot=a)
        aspa = [(60, -30), (380, -60), (420, 0), (380, 60), (60, 30)]
        lz.forma(np.array(aspa, float), hexa("#232830"), sombra=hexa("#14171c"), luz=(0, -12), grosor=5)
        lz.restaurar()
    lz.forma(elipse(0, 0, 90, 90, 20), hexa("#2c313b"), sombra=hexa("#15181e"), luz=(-10, -10), grosor=5)
    lz.forma(elipse(0, 0, 40, 40, 16), hexa("#4b5260"), grosor=4)
    lz.restaurar()


# --- el parque del recuerdo -------------------------------------------------------------------

def parque(lz):
    M = 200
    lz.degradado(0, -M, 0, 1100, [(0, hexa("#3f97d8"), 1), (0.7, hexa("#8fcdf2"), 1), (1, hexa("#e2efd8"), 1)],
                 rect=(-M, -M, W + 2 * M, 1300 + M))
    # Sol.
    lz.resplandor(820, 260, 360, hexa("#fff2b0"), 0.5)
    lz.forma(elipse(820, 260, 80, 80, 24), hexa("#fff6c8"), tinta=False)
    # Nubes.
    for (cx, cy, s) in ((200, 250, 1.0), (560, 420, 0.8), (980, 560, 0.7)):
        pts = []
        for k in range(10):
            a = k / 10 * 2 * math.pi
            r = (1 + 0.25 * math.sin(k * 2.7)) * 1
            pts.append((cx + math.cos(a) * 140 * s * r, cy + math.sin(a) * 60 * s * r))
        lz.forma(np.array(pts, float), hexa("#ffffff"), sombra=hexa("#d4e6f2"), luz=(0, -14), grosor=4)
    # Lomas.
    lz.forma(np.array([(-M, 1060), (200, 980), (500, 1020), (800, 960), (W + M, 1000), (W + M, 1300), (-M, 1300)],
                      float), hexa("#7cc46a"), sombra=hexa("#5da651"), luz=(0, -20), grosor=4)
    lz.forma(np.array([(-M, 1120), (W + M, 1080), (W + M, H + M), (-M, H + M)], float), hexa("#6cbf4a"),
             sombra=hexa("#58a63c"), luz=(0, -30), grosor=4)
    rng = np.random.default_rng(5)
    for _ in range(160):
        x, y = rng.uniform(-M, W + M), rng.uniform(1150, H + M)
        s = 0.5 + (y - 1150) / 800
        lz.pincel([(x - 8 * s, y), (x, y - 26 * s), (x + 8 * s, y)], 4 * s, hexa("#4d9a36"), hervor=0)
    for _ in range(50):
        x, y = rng.uniform(-M, W + M), rng.uniform(1150, H + M)
        col = (hexa("#ffffff"), hexa("#f7d64a"), hexa("#f08aa8"))[int(rng.integers(0, 3))]
        lz.forma(elipse(x, y, 7, 6, 8), col, tinta=False, hervor=0)
    # Árbol grande a la izquierda.
    lz.forma(np.array([(60, 1150), (90, 700), (130, 560), (180, 560), (200, 700), (230, 1150)], float), hexa("#7a4b2c"),
             sombra=hexa("#553320"), luz=(-10, 0), grosor=5)
    for (cx, cy, r) in ((140, 420, 230), (-20, 540, 170), (300, 520, 170), (140, 620, 160)):
        lz.forma(elipse(cx, cy, r, r * 0.85, 18), hexa("#3f9a45"), sombra=hexa("#2c7534"), luz=(12, -18), grosor=5)
    # Mantel de día de campo.
    manta = [(420, 1500), (1100, 1470), (1250, 1900), (340, 1960)]

    def cuadros():
        for i in range(-2, 14):
            for j in range(-2, 10):
                if (i + j) % 2:
                    continue
                x0 = 340 + i * 80
                y0 = 1470 + j * 70
                lz.forma(np.array([(x0, y0), (x0 + 80, y0 - 4), (x0 + 84, y0 + 66), (x0 + 4, y0 + 70)], float),
                         hexa("#d8423a"), tinta=False, suave=False, hervor=0)

    lz.forma(np.array(manta, float), hexa("#f4efe4"), suave=False, grosor=5, relleno=cuadros)
    lz.forma(np.array([(470, 1560), (620, 1550), (640, 1640), (460, 1650)], float), hexa("#c08a4a"),
             sombra=hexa("#8a5e2c"), luz=(-8, -6), grosor=5)


# --- fondos de apoyo para los planos cerrados ---------------------------------------------------

def mesa_pov(lz):
    """La mesa vista desde los ojos de Alex (fondo del celular, se desenfoca)."""
    mantel = hexa("#cdb48c")
    lz.forma(np.array([(-300, -300), (1400, -300), (1400, 2300), (-300, 2300)], float), hexa("#5a3020"), tinta=False,
             suave=False)
    lz.forma(np.array([(-300, 560), (1400, 520), (1400, 2300), (-300, 2300)], float), mantel, tinta=False, suave=False)
    rng = np.random.default_rng(12)
    for _ in range(60):
        x, y = rng.uniform(-200, 1300), rng.uniform(600, 2200)
        lz.forma(elipse(x, y, 16, 10, 8), hexa("#b8566a") if rng.random() < 0.6 else hexa("#6f9a5a"), tinta=False, alfa=0.7)
    lz.forma(elipse(160, 1650, 300, 150, 24), hexa("#f1ece0"), tinta=False)
    lz.forma(elipse(160, 1650, 250, 120, 24), hexa("#3f6aa0"), tinta=False)
    lz.forma(elipse(160, 1650, 225, 106, 24), hexa("#f1ece0"), tinta=False)
    lz.forma(elipse(190, 1640, 130, 60, 16), hexa("#b8733a"), tinta=False)
    lz.forma(elipse(900, 900, 150, 60, 20), hexa("#94502c"), tinta=False)
    # La familia, lejos y sin foco.
    for (x, y, col, ropa) in ((120, 260, hexa("#b07a58"), hexa("#e6d3bd")), (560, 190, hexa("#8d5c3f"), hexa("#9cb8cc")),
                              (980, 250, hexa("#a8704f"), hexa("#8d8e98"))):
        lz.forma(elipse(x, y + 330, 190, 190, 16), oscuro(ropa, 0.7), tinta=False)
        lz.forma(elipse(x, y, 90, 110, 16), col, tinta=False)
        lz.forma(elipse(x, y - 60, 100, 70, 16), hexa("#1a1214"), tinta=False)
    lz.resplandor(560, -100, 700, hexa("#ffb060"), 0.5)


def sabana(lz, luna=1.0):
    """Sábana arrugada de noche, vista de cerca (3C, 5D)."""
    base = hexa("#26314a")
    lz.forma(np.array([(-400, -400), (1500, -400), (1500, 2400), (-400, 2400)], float), base, tinta=False, suave=False)
    rng = np.random.default_rng(31)
    for _ in range(18):
        x, y = rng.uniform(-200, 1300), rng.uniform(-200, 2200)
        largo, ang = rng.uniform(250, 600), rng.uniform(-0.6, 0.6)
        pts = [(x, y), (x + math.cos(ang) * largo * 0.5, y + math.sin(ang) * largo * 0.5 + 30),
               (x + math.cos(ang) * largo, y + math.sin(ang) * largo)]
        lz.pincel(pts, rng.uniform(18, 40), oscuro(base, 0.62), punta=0.5)
        lz.pincel(np.array(pts) + (0, -22), rng.uniform(6, 14), mezcla(base, hexa("#7f9dc4"), 0.35), punta=0.5, alfa=0.6)
    lz.mancha(np.array([(-400, 200), (900, -400), (1500, -400), (-400, 900)], float), hexa("#9dbbe0"), 0.07 * luna,
              suave=False)


def cuarto_lado(lz):
    """Pared del cuarto de lado, con la ventana y su luz de luna (5E)."""
    muro = hexa("#18202e")
    lz.forma(np.array([(-300, -300), (1400, -300), (1400, 2300), (-300, 2300)], float), muro, tinta=False, suave=False)
    lz.resplandor(210, 520, 520, hexa("#3c5474"), 0.6)
    lz.forma(np.array([(40, 200), (380, 200), (380, 840), (40, 840)], float), hexa("#2d3748"), tinta=False, suave=False)
    lz.degradado(0, 230, 0, 810, [(0, hexa("#9fc0de"), 1), (1, hexa("#4f6f90"), 1)], rect=(70, 230, 280, 580))
    lz.forma(np.array([(200, 230), (216, 230), (216, 810), (200, 810)], float), hexa("#2d3748"), tinta=False, suave=False)
    lz.forma(np.array([(70, 512), (350, 512), (350, 528), (70, 528)], float), hexa("#2d3748"), tinta=False, suave=False)
    # La ventana proyectada en la pared.
    lz.mancha(np.array([(560, 620), (960, 700), (1000, 1500), (600, 1360)], float), hexa("#8fb0d4"), 0.16, suave=False)
    lz.mancha(np.array([(770, 660), (786, 663), (812, 1432), (796, 1428)], float), muro, 0.8, suave=False)
    lz.mancha(np.array([(570, 990), (980, 1100), (982, 1116), (572, 1006)], float), muro, 0.8, suave=False)
    # Cabecera y almohada.
    lz.forma(np.array([(-300, 1480), (1400, 1480), (1400, 2300), (-300, 2300)], float), hexa("#1d130d"), tinta=False,
             suave=False)
    lz.forma(rect_suave(360, 1520, 1180, 1880), hexa("#3a475c"), sombra=hexa("#242d3c"), luz=(-20, -20), grosor=5)


def rect_suave(x0, y0, x1, y1):
    return np.array([(x0 + 40, y0), (x1 - 40, y0 + 10), (x1, y0 + 60), (x1 - 10, y1 - 40), (x1 - 60, y1),
                     (x0 + 50, y1 - 10), (x0, y1 - 60), (x0 + 6, y0 + 40)], float)


def mesa_frente(lz):
    """Borde de la mesa de frente con el desayuno (6A). Capa transparente."""
    mantel = hexa("#e8dcc0")
    tela = [(-300, 1330), (1400, 1330), (1400, 2300), (-300, 2300)]

    def flores():
        rng = np.random.default_rng(15)
        for _ in range(70):
            x, y = rng.uniform(-250, 1350), rng.uniform(1340, 2250)
            col = hexa("#c4566a") if rng.random() < 0.6 else hexa("#6f9a5a")
            lz.forma(elipse(x, y, 16, 9, 8), col, tinta=False, hervor=0, alfa=0.6)

    lz.forma(np.array(tela, float), mantel, sombra=oscuro(mantel, 0.82), luz=(0, 40), suave=False, grosor=5,
             relleno=flores)
    from cuerpo import chilaquiles
    chilaquiles(lz, 540, 1560, 1.0)
    lz.forma(np.array([(830, 1330), (900, 1330), (894, 1480), (836, 1480)], float), hexa("#f0a53a"), grosor=4,
             suave=False, alfa=0.9)
    lz.forma(elipse(865, 1332, 36, 10, 12), hexa("#f7c86a"), grosor=3)


def mesa_cerca(lz):
    """La mesa del desayuno muy de cerca, fuera de foco (fondo del brazo en 6C)."""
    lz.forma(np.array([(-300, -300), (1400, -300), (1400, 2300), (-300, 2300)], float), hexa("#e2d6bc"), tinta=False,
             suave=False)
    rng = np.random.default_rng(16)
    for _ in range(40):
        x, y = rng.uniform(-250, 1350), rng.uniform(-250, 2250)
        lz.forma(elipse(x, y, 30, 18, 10), hexa("#c4566a") if rng.random() < 0.6 else hexa("#6f9a5a"), tinta=False,
                 alfa=0.6)
    lz.forma(elipse(820, 1650, 420, 170, 24), hexa("#f1ece0"), tinta=False)
    lz.forma(elipse(820, 1650, 380, 150, 24), hexa("#2f5d98"), tinta=False)
    lz.forma(elipse(820, 1650, 350, 136, 24), hexa("#f1ece0"), tinta=False)
    lz.forma(elipse(830, 1640, 250, 90, 20), hexa("#5b8f32"), tinta=False)
    lz.degradado(0, -300, 0, 900, [(0, hexa("#a55a3a"), 1), (1, hexa("#a55a3a"), 0)])
