"""Fondos pintados: el comedor, el cuarto de Alex, el techo, el parque y las telas.

Cada fondo se dibuja con formas planas y muchas pinceladas y luego pasa por `estilo.gouache`, que le pone
la mancha de pigmento, las cerdas del pincel y el grano del papel. Miden 1080×1920 (el cuadro vertical
completo) para poder hacer panorámicas y acercamientos con la cámara sobre ellos.
"""

import math

import numpy as np

from . import estilo
from .cel import Hoja, W, H, elipse, hexa, mezcla, oscuro

_cache = {}


def _pinceladas(h, rect, color, n, semilla, largo=(60, 200), ancho=(6, 16), vert=True, alfa=0.35, variacion=0.10):
    """Pinceladas semitransparentes que rompen el color plano de una zona."""
    rng = np.random.default_rng(semilla)
    x0, y0, x1, y1 = rect
    h.cr.save()
    h.cr.rectangle(x0, y0, x1 - x0, y1 - y0)
    h.cr.clip()
    for _ in range(n):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        L = rng.uniform(*largo)
        a = rng.uniform(*ancho)
        f = 1 + rng.uniform(-variacion, variacion)
        c = tuple(min(max(v * f, 0), 1) for v in color)
        if vert:
            pts = [(x, y), (x + rng.normal(0, 3), y + L / 2), (x + rng.normal(0, 4), y + L)]
        else:
            pts = [(x, y), (x + L / 2, y + rng.normal(0, 3)), (x + L, y + rng.normal(0, 4))]
        h.tinta(pts, a, c, afila=(0.3, 0.3), alfa=alfa)
    h.cr.restore()


def _zona(h, rect, color, semilla, n=420, variacion=0.09, vert=True, alfa=0.4):
    x0, y0, x1, y1 = rect
    h.rect(x0, y0, x1, y1, color)
    area = (x1 - x0) * (y1 - y0)
    _pinceladas(h, rect, color, max(int(n * area / 1e6 * 4), 20), semilla, variacion=variacion, vert=vert, alfa=alfa)


def _foto(h, x, y, w, ancho_marco, marco, foto, semilla, personas=2):
    """Retrato enmarcado: marco de madera, paspartú y siluetas de gente sonriendo."""
    h.rect(x - ancho_marco, y - ancho_marco, x + w + ancho_marco, y + w * 1.25 + ancho_marco, marco)
    h.rect(x, y, x + w, y + w * 1.25, mezcla(foto, (1, 1, 1), 0.35))
    rng = np.random.default_rng(semilla)
    for i in range(personas):
        cx = x + w * (0.3 + 0.4 * i / max(personas - 1, 1)) if personas > 1 else x + w / 2
        cy = y + w * 0.55
        h.forma(elipse(cx, cy, w * 0.16, w * 0.19), mezcla(hexa("#d0966a"), foto, 0.25))
        h.forma(elipse(cx, cy - w * 0.1, w * 0.17, w * 0.13), oscuro(hexa("#3a2a22"), 0.9 + rng.uniform(0, 0.2)))
        h.forma([(cx - w * 0.28, y + w * 1.25), (cx - w * 0.2, cy + w * 0.3), (cx + w * 0.2, cy + w * 0.3),
                 (cx + w * 0.28, y + w * 1.25)], mezcla(hexa("#8aa0b0"), foto, 0.3), suave_=False)


def _mantel(h, y0, y1, base, semilla):
    """Mantel de flores con la caída al frente."""
    rng = np.random.default_rng(semilla)
    h.rect(0, y0, W, y1, base)
    _pinceladas(h, (0, y0, W, y1), base, 260, semilla + 1, largo=(80, 260), ancho=(10, 26), alfa=0.28, vert=False)
    rojo, verde, amarillo = hexa("#b8443a"), hexa("#5f8a4a"), hexa("#d9a93c")
    for _ in range(90):
        x, y = rng.uniform(0, W), rng.uniform(y0, y1)
        esc = 0.45 + 0.9 * (y - y0) / (y1 - y0)
        r = rng.uniform(16, 30) * esc
        c = (rojo, amarillo)[rng.integers(0, 2)]
        for a in range(5):
            ang = 2 * math.pi * a / 5 + rng.uniform(0, 1)
            h.forma(elipse(x + math.cos(ang) * r * 0.75, y + math.sin(ang) * r * 0.6, r * 0.55, r * 0.42), c, alfa=0.85)
        h.forma(elipse(x, y, r * 0.3, r * 0.26), hexa("#f2e2b0"))
        for a in range(2):
            h.forma(elipse(x + rng.uniform(-1, 1) * r * 1.5, y + rng.uniform(0.6, 1.3) * r, r * 0.6, r * 0.22,
                           rot=rng.uniform(-0.6, 0.6)), verde, alfa=0.8)


def comedor(dia=False):
    """El comedor de la casa: paredes con textura, fotos familiares, un trastero con platos y la mesa."""
    clave = ("comedor", dia)
    if clave in _cache:
        return _cache[clave]
    h = Hoja(k=1.0)
    if dia:
        pared, dado, madera, mantel, luz = hexa("#c9b89a"), hexa("#8d7a63"), hexa("#6d5644"), hexa("#e6e0d0"), hexa("#f4f0e2")
    else:
        pared, dado, madera, mantel, luz = hexa("#a2643c"), hexa("#6b3a25"), hexa("#4f2c1d"), hexa("#e6d9b6"), hexa("#ffd27f")
    # muro con textura, dado de madera y zoclo
    _zona(h, (0, 0, W, 960), pared, 1, n=700, vert=True)
    _zona(h, (0, 960, W, 1240), dado, 2, n=500, vert=True)
    h.rect(0, 950, W, 972, oscuro(dado, 0.7))
    h.rect(0, 972, W, 985, mezcla(dado, (1, 1, 1), 0.12))
    # trastero de madera (derecha) con platos de talavera y adornos
    h.rect(690, 250, 1010, 1010, oscuro(madera, 0.75))
    h.rect(702, 262, 998, 998, oscuro(madera, 0.5))
    for i in range(3):
        y = 330 + i * 230
        h.rect(702, y + 150, 998, y + 172, madera)
        for j in range(4):
            px = 745 + j * 70
            h.forma(elipse(px, y + 90, 32, 58), hexa("#e6e2d6"))
            h.forma(elipse(px, y + 90, 22, 42), hexa("#3f66a8"), alfa=0.85)
            h.forma(elipse(px, y + 90, 9, 20), hexa("#e6e2d6"))
    h.rect(690, 240, 1010, 262, madera)
    # fotos familiares en la pared izquierda y sobre el trastero
    _foto(h, 70, 310, 130, 14, madera, hexa("#c7b18a"), 11, personas=3)
    _foto(h, 250, 250, 120, 12, oscuro(madera, 1.1), hexa("#b9c4c8"), 12, personas=2)
    _foto(h, 100, 620, 170, 16, madera, hexa("#d8c39c"), 13, personas=3)
    _foto(h, 330, 560, 105, 11, oscuro(madera, 0.9), hexa("#c2b08d"), 14, personas=1)
    # calendario y crucifijo
    h.rect(455, 300, 560, 470, hexa("#e0d2b0"))
    h.rect(455, 300, 560, 345, hexa("#b34a3a"))
    h.rect(500, 130, 515, 210, oscuro(madera, 0.9))
    h.rect(478, 152, 537, 168, oscuro(madera, 0.9))
    # lámpara colgante y su resplandor
    h.rect(538, 0, 542, 220, oscuro(madera, 0.6))
    h.forma([(430, 330), (470, 225), (610, 225), (650, 330)], hexa("#c98c3e") if not dia else hexa("#d8d0b8"),
            suave_=False)
    h.forma(elipse(540, 335, 112, 18), luz)
    h.resplandor(540, 335, 700, luz, 0.55 if not dia else 0.25, ry=640)
    h.resplandor(540, 335, 260, (1, 0.95, 0.8), 0.6)
    if dia:
        # ventana de la mañana con cortina clara, a la izquierda
        h.rect(40, 90, 380, 640, hexa("#e9eef2"))
        for x in (40, 208, 378):
            h.rect(x, 90, x + 8, 640, oscuro(madera, 1.2))
        h.rect(40, 360, 380, 368, oscuro(madera, 1.2))
        h.rect(40, 90, 380, 98, oscuro(madera, 1.2))
        h.rect(40, 632, 380, 640, oscuro(madera, 1.2))
        h.forma([(0, 60), (140, 60), (110, 700), (0, 720)], hexa("#ded6c2"), suave_=True)
        h.resplandor(210, 360, 520, (1, 1, 0.95), 0.4, ry=700)
    # sillas: respaldos de madera tras la mesa
    for cx in (150, 540, 930):
        h.rect(cx - 95, 780, cx + 95, 1240, oscuro(madera, 0.85))
        h.rect(cx - 80, 800, cx - 60, 1240, madera)
        h.rect(cx + 60, 800, cx + 80, 1240, madera)
        h.rect(cx - 95, 780, cx + 95, 810, madera)
    # mesa: superficie con perspectiva y caída del mantel
    h.forma([(0, 1240), (W, 1240), (W + 160, 1560), (-160, 1560)], oscuro(madera, 0.9), suave_=False)
    _mantel(h, 1240, 1560, mantel, 21)
    h.rect(0, 1560, W, 1920, oscuro(mantel, 0.78))
    _mantel(h, 1560, 1920, oscuro(mantel, 0.82), 22)
    # borde de la mesa y sombra
    h.rect(0, 1552, W, 1568, oscuro(mantel, 0.55))
    # platos, vasos y una jarra sobre la mesa
    for cx in (170, 540, 910):
        h.forma(elipse(cx, 1370, 150, 44), hexa("#f0ece2"))
        h.forma(elipse(cx, 1370, 108, 28), hexa("#ddd6c6"))
        h.forma(elipse(cx, 1365, 70, 17), hexa("#c47a3a") if not dia else hexa("#d9d2c0"))
    h.forma(elipse(360, 1310, 52, 15), hexa("#d94a2a"))
    h.forma([(330, 1300), (390, 1300), (382, 1250), (338, 1250)], hexa("#d0d8d8"), alfa=0.7, suave_=False)
    h.forma([(700, 1300), (780, 1300), (770, 1210), (710, 1210)], hexa("#4a78a8"), suave_=False)
    h.resplandor(540, 1330, 520, luz, 0.25 if not dia else 0.1, ry=160)
    img = estilo.gouache(h.rgb(), semilla=3, cerdas=0.03 if not dia else 0.018)
    _cache[clave] = img
    return img


def cuarto():
    """El cuarto de Alex de noche, visto desde la cama: casi negro, con la luz azul de la ventana."""
    if "cuarto" in _cache:
        return _cache["cuarto"]
    h = Hoja(k=1.0)
    pared, madera = hexa("#1c2a3e"), hexa("#1a1418")
    _zona(h, (0, 0, W, 1250), pared, 31, n=600, vert=True, variacion=0.12)
    h.rect(0, 1250, W, 1920, hexa("#12161f"))
    # piso de madera
    _zona(h, (0, 1150, W, 1440), hexa("#211a1c"), 32, n=400, vert=False)
    # ventana a la derecha: la luz de la luna
    h.rect(700, 380, 1060, 1010, hexa("#0c1420"))
    h.rect(716, 396, 1044, 994, hexa("#b7d4ea"))
    h.rect(716, 396, 1044, 994, hexa("#8fb4d6"), alfa=0.5)
    for x in (716, 875, 1036):
        h.rect(x, 396, x + 10, 994, hexa("#0c1420"))
    for y in (396, 690, 986):
        h.rect(716, y, 1044, y + 10, hexa("#0c1420"))
    # farola lejana en el vidrio
    h.resplandor(930, 830, 90, (1, 0.8, 0.45), 0.9)
    h.resplandor(880, 520, 130, (0.9, 0.98, 1), 0.5)
    # cortina oscura
    h.forma([(640, 330), (720, 330), (760, 1040), (630, 1060), (560, 700)], hexa("#0d1219"))
    h.forma([(1060, 330), (1080, 330), (1080, 1050), (1030, 1040)], hexa("#0d1219"))
    # luz de la luna sobre el suelo y la cama
    h.forma([(700, 1010), (1060, 1010), (1080, 1400), (330, 1400)], hexa("#6a93b8"), alfa=0.28, suave_=False)
    h.resplandor(880, 700, 560, (0.6, 0.78, 0.95), 0.32, ry=760)
    # armario a la izquierda, casi silueta
    h.rect(-20, 240, 300, 1180, hexa("#0e1118"))
    h.rect(-20, 240, 300, 262, hexa("#20242e"))
    h.rect(140, 262, 150, 1180, hexa("#06080c"))
    # puerta entreabierta con ropa colgada
    h.rect(385, 420, 560, 1130, hexa("#33445a"))
    h.rect(400, 435, 545, 1115, hexa("#26374d"))
    h.rect(545, 425, 610, 1125, hexa("#05070b"))
    for i in range(3):
        x = 430 + i * 45
        h.forma([(x, 500), (x + 34, 500), (x + 42, 900), (x - 6, 900)], hexa("#141a24"), suave_=False)
    # tocador con espejo al centro
    h.rect(560, 640, 700, 1000, hexa("#101620"))
    h.rect(575, 655, 685, 985, hexa("#17233a"))
    h.rect(555, 1000, 720, 1150, hexa("#251c1c"))
    for j in range(3):
        h.rect(565, 1015 + j * 44, 710, 1050 + j * 44, hexa("#2d2222"))
        h.rect(626, 1028 + j * 44, 650, 1036 + j * 44, hexa("#4b3a34"))
    # despertador rojo (03:17), sobre la mesa de noche a la derecha
    h.rect(920, 1090, 1060, 1180, hexa("#0b0d12"))
    h.rect(936, 1104, 1044, 1160, hexa("#2a0808"))
    h.resplandor(990, 1130, 110, (1, 0.12, 0.08), 0.65, ry=70)
    for i, seg in enumerate(("0", "3", ":", "1", "7")):
        h.texto(944 + i * 20, 1150, seg, 42, (1, 0.28, 0.2), familia="DejaVu Sans Mono", negrita=True)
    # sombras en las esquinas
    h.forma([(0, 0), (330, 0), (150, 500), (0, 700)], hexa("#03050a"), alfa=0.6)
    h.forma([(W, 0), (W - 240, 0), (W - 100, 300), (W, 350)], hexa("#03050a"), alfa=0.5)
    # cama: los pies con tablero de madera y la cobija arrugada
    h.forma([(-40, 1290), (W + 40, 1290), (W + 40, 1920), (-40, 1920)], hexa("#141c2a"))
    h.rect(-40, 1240, W + 40, 1320, hexa("#0d090b"))
    h.rect(-40, 1240, W + 40, 1256, hexa("#241a1c"))
    rng = np.random.default_rng(33)
    for _ in range(46):
        x, y = rng.uniform(-40, W), rng.uniform(1330, 1900)
        L = rng.uniform(160, 460)
        pts = [(x, y), (x + L * 0.5, y + rng.normal(0, 26)), (x + L, y + rng.normal(0, 40))]
        h.tinta(pts, rng.uniform(16, 42), hexa("#2a3a52") if rng.random() < 0.5 else hexa("#0a0f18"),
                afila=(0.4, 0.4), alfa=0.6)
    h.resplandor(740, 1500, 620, (0.55, 0.72, 0.92), 0.18, ry=280)
    img = estilo.gouache(h.rgb(), semilla=5, mancha=0.06)
    _cache["cuarto"] = img
    return img


def techo():
    """El techo visto desde la cama: el ventilador apagado, la esquina y un charco de luz de la ventana."""
    if "techo" in _cache:
        return _cache["techo"]
    h = Hoja(k=1.0)
    _zona(h, (0, 0, W, H), hexa("#1d2a44"), 41, n=500, vert=False, variacion=0.10)
    h.degradado(0, 0, W, H, [(0, (0.03, 0.05, 0.1, 0.0)), (1, (0.02, 0.03, 0.06, 0.55))])
    # luz de la luna: un óvalo largo que entra en diagonal desde la derecha
    h.forma(elipse(830, 500, 480, 250, rot=0.55), hexa("#5f8ab0"), alfa=0.20)
    h.resplandor(900, 420, 700, (0.5, 0.7, 0.95), 0.28, ry=520)
    # esquinas del techo: dos líneas que convergen y una moldura
    h.tinta([(0, 220), (300, 460)], 18, hexa("#0a0e18"), afila=(0.0, 0.2))
    h.tinta([(W, 180), (760, 420)], 18, hexa("#0a0e18"), afila=(0.0, 0.2))
    # ventilador de techo: domo, motor y cuatro aspas
    cx, cy = 540, 860
    h.tinta([(cx, 0), (cx, cy - 120)], 22, hexa("#0b0f18"))
    for ang in (0.25, 1.82, 3.4, 4.97):
        pts = [(cx, cy), (cx + math.cos(ang) * 260, cy + math.sin(ang) * 120),
               (cx + math.cos(ang) * 470, cy + math.sin(ang) * 210)]
        h.tinta(pts, 120, hexa("#1b2740"), afila=(0.1, 0.35))
        h.tinta([(x + 6, y - 8) for x, y in pts], 30, hexa("#7f9cc8"), afila=(0.1, 0.35), alfa=0.9)
    h.forma(elipse(cx, cy, 108, 62), hexa("#0e1422"))
    h.forma(elipse(cx - 20, cy - 14, 54, 26), hexa("#3d5a82"), alfa=0.8)
    h.forma(elipse(cx, cy + 46, 92, 40), hexa("#b8cce0"), alfa=0.35)
    h.resplandor(cx, cy + 40, 250, (0.5, 0.65, 0.9), 0.22)
    img = estilo.gouache(h.rgb(), semilla=6, mancha=0.05, vertical=False)
    _cache["techo"] = img
    return img


def sabana():
    """La sábana en penumbra, arrugada, con la luz de la luna al sesgo."""
    if "sabana" in _cache:
        return _cache["sabana"]
    h = Hoja(k=1.0)
    _zona(h, (0, 0, W, H), hexa("#243450"), 51, n=700, vert=False, variacion=0.10)
    rng = np.random.default_rng(52)
    for i in range(70):
        x, y = rng.uniform(-200, W), rng.uniform(-100, H)
        L = rng.uniform(300, 900)
        ang = rng.normal(0.5, 0.35)
        pts = [(x, y), (x + math.cos(ang) * L * 0.5, y + math.sin(ang) * L * 0.5 + rng.normal(0, 40)),
               (x + math.cos(ang) * L, y + math.sin(ang) * L)]
        oscura = rng.random() < 0.5
        h.tinta(pts, rng.uniform(40, 110), hexa("#0d1422") if oscura else hexa("#4d6a94"), afila=(0.35, 0.45),
                alfa=0.55 if oscura else 0.4)
    for i in range(24):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        L = rng.uniform(200, 500)
        ang = 0.5 + rng.normal(0, 0.2)
        h.tinta([(x, y), (x + math.cos(ang) * L, y + math.sin(ang) * L)], rng.uniform(8, 20), hexa("#8fb0d4"),
                afila=(0.3, 0.5), alfa=0.35)
    h.resplandor(900, 400, 800, (0.55, 0.75, 1.0), 0.3, ry=700)
    img = estilo.gouache(h.rgb(), semilla=7, vertical=False)
    _cache["sabana"] = img
    return img


def parque():
    """Un parque soleado: árboles que enmarcan, cielo con nubes pintadas, pasto brillante y lejanía azulada."""
    if "parque" in _cache:
        return _cache["parque"]
    h = Hoja(k=1.0)
    h.degradado(0, 0, 0, 1100, [(0, hexa("#7fb6df")), (0.6, hexa("#cfe6ef")), (1, hexa("#f6ecc8"))])
    rng = np.random.default_rng(61)
    for _ in range(9):
        x, y = rng.uniform(0, W), rng.uniform(80, 560)
        for _ in range(5):
            h.forma(elipse(x + rng.uniform(-120, 120), y + rng.uniform(-24, 24), rng.uniform(80, 160), rng.uniform(26, 48)),
                    (1, 0.98, 0.94), alfa=0.8)
    # lejanía: bosque en tres capas que se aclaran hacia el fondo
    for k, (col, base, alto) in enumerate((("#9fb9a8", 980, 200), ("#7da48b", 1060, 220), ("#5f9068", 1140, 240))):
        pts = [(-20, base + 100)]
        for i in range(0, 12):
            pts.append((i * 100, base - alto * (0.4 + 0.6 * rng.random())))
        pts += [(W + 20, base - alto * 0.6), (W + 20, base + 400), (-20, base + 400)]
        h.forma(pts, hexa(col), suave_=True)
    # pasto brillante en dos planos y un camino
    _zona(h, (0, 1180, W, H), hexa("#8bb24c"), 62, n=900, vert=True, variacion=0.14)
    h.forma([(380, 1180), (700, 1180), (1100, H), (-160, H)], hexa("#d8c68c"), alfa=0.85)
    for _ in range(90):
        x, y = rng.uniform(0, W), rng.uniform(1200, H)
        h.tinta([(x, y), (x + rng.normal(0, 6), y - rng.uniform(20, 60))], 5, hexa("#c6dc70"), afila=(0.1, 0.9), alfa=0.8)
    # copas de los árboles que enmarcan: racimos de hojas en las esquinas de arriba y un tronco que sale del cuadro
    for lado, ox in ((-1, 0), (1, W)):
        h.tinta([(ox - lado * 40, 300), (ox - lado * 90, 900), (ox - lado * 60, 1300)], 110, hexa("#3d2c22"),
                afila=(0.0, 0.0))
        h.tinta([(ox - lado * 70, 500), (ox - lado * 210, 330), (ox - lado * 330, 250)], 46, hexa("#3d2c22"),
                afila=(0.0, 0.6))
        for capa_, (col, alfa) in enumerate((("#2f5a35", 1.0), ("#4c8a44", 0.95), ("#a9d268", 0.85))):
            for _ in range(46 - 12 * capa_):
                r = abs(rng.normal(0, 260 - 40 * capa_))
                x = ox - lado * min(r, 720) * rng.uniform(0.2, 1.0)
                y = rng.uniform(-40, 500) * (1 - min(abs(x - ox), 700) / 900)
                h.forma(elipse(x, y, rng.uniform(46, 100), rng.uniform(30, 64)), hexa(col), alfa=alfa)
    # el sol, rayos y polen
    h.resplandor(220, 140, 720, (1, 0.96, 0.75), 0.75, ry=560)
    for a in (0.6, 0.85, 1.1, 1.35):
        h.forma([(160, 80), (160 + math.cos(a) * 1500, 80 + math.sin(a) * 1500),
                 (160 + math.cos(a + 0.12) * 1500, 80 + math.sin(a + 0.12) * 1500)], (1, 0.97, 0.78), alfa=0.16)
    # banca a la izquierda
    h.rect(30, 1230, 250, 1252, hexa("#6a4630"))
    h.rect(40, 1252, 60, 1340, hexa("#4a2f20"))
    h.rect(220, 1252, 240, 1340, hexa("#4a2f20"))
    h.rect(36, 1140, 244, 1152, hexa("#6a4630"))
    h.rect(46, 1140, 56, 1236, hexa("#4a2f20"))
    h.rect(224, 1140, 234, 1236, hexa("#4a2f20"))
    img = estilo.gouache(h.rgb(), semilla=8, mancha=0.05, cerdas=0.008)
    _cache["parque"] = img
    return img
