"""La familia de Alex (mamá, papá, hermana) y sus versiones del recuerdo, más brazos y manos.

Misma convención que personajes.py: origen en el centro de la cara, cabeza de ~400 de alto.
"""

import math

import numpy as np

from dibujo import elipse, hexa, mezcla, oscuro

FAMILIA = {
    "mama": dict(piel=hexa("#b07a58"), pelo=hexa("#2a1712"), ropa=hexa("#e6d3bd"), estampado=hexa("#c4566a"),
                 ancho=108, hombros=175, labios=hexa("#8a3440")),
    "papa": dict(piel=hexa("#8d5c3f"), pelo=hexa("#141116"), ropa=hexa("#9cb8cc"), estampado=None,
                 ancho=126, hombros=225, labios=None),
    "hermana": dict(piel=hexa("#a8704f"), pelo=hexa("#110d10"), ropa=hexa("#8d8e98"), estampado=hexa("#e4e2dc"),
                    ancho=104, hombros=165, labios=hexa("#8c4a4a")),
}


def ik(hombro, mano, l1, l2, doblez=1):
    """Codo de un brazo de dos huesos que alcanza `mano` desde `hombro`."""
    h = np.asarray(hombro, float)
    m = np.asarray(mano, float)
    d = m - h
    dist = min(np.linalg.norm(d), l1 + l2 - 1e-3)
    dist = max(dist, abs(l1 - l2) + 1e-3)
    a = (l1 * l1 - l2 * l2 + dist * dist) / (2 * dist)
    alto = math.sqrt(max(l1 * l1 - a * a, 0))
    u = d / (np.linalg.norm(d) + 1e-9)
    n = np.array([-u[1], u[0]]) * doblez
    return h + u * a + n * alto


def mano_simple(lz, pos, ang, piel, sombra, s=1.0, cerrada=0.0, cosa=None):
    """Mano en forma de manopla con pulgar, orientada con el ángulo del antebrazo."""
    lz.guardar()
    lz.mover(pos[0], pos[1], s, rot=ang)
    largo = 62 - cerrada * 22
    palma = [(-4, -24), (28, -26), (largo, -18), (largo + 8, 0), (largo, 18), (26, 24), (-4, 22)]
    lz.forma(np.array(palma, float), piel, sombra=sombra, luz=(-4, -6), grosor=4)
    pulgar = [(14, -20), (30, -40), (44, -44), (46, -34), (30, -20)]
    lz.forma(np.array(pulgar, float), piel, sombra=sombra, luz=(-3, -4), grosor=3.5)
    for k in (-8, 4):
        lz.pincel([(largo - 16, k), (largo + 2, k + 2)], 2.5, sombra)
    if cosa == "tenedor":
        lz.forma(np.array([(40, -4), (140, -8), (140, 2), (40, 6)], float), hexa("#b9bcc2"), grosor=3, suave=False)
    lz.restaurar()


def brazo(lz, hombro, mano, l1, l2, manga, piel, grosor=46, doblez=1, sombra_manga=None, sombra_piel=None,
          corta=False, cerrada=0.0, cosa=None, ancho_mano=1.0):
    codo = ik(hombro, mano, l1, l2, doblez)
    sm = sombra_manga or oscuro(manga, 0.65)
    sp = sombra_piel or oscuro(piel, 0.68)

    def segmento(a, b, g0, g1, color, sombra):
        a, b = np.asarray(a, float), np.asarray(b, float)
        d = b - a
        n = np.array([-d[1], d[0]]) / (np.linalg.norm(d) + 1e-9)
        pts = [a + n * g0, a + d * 0.5 + n * (g0 + g1) / 2 * 1.04, b + n * g1, b - n * g1, a + d * 0.5 - n * (g0 + g1) / 2 * 1.04,
               a - n * g0]
        lz.forma(np.array(pts, float), color, sombra=sombra, luz=(-n * 6) * doblez, grosor=4)

    segmento(hombro, codo, grosor * 0.55, grosor * 0.48, manga, sm)
    if corta:
        segmento(codo, mano, grosor * 0.4, grosor * 0.32, piel, sp)
    else:
        punto = np.asarray(codo) + (np.asarray(mano) - np.asarray(codo)) * 0.72
        segmento(codo, punto, grosor * 0.48, grosor * 0.42, manga, sm)
        segmento(punto - (np.asarray(mano) - np.asarray(codo)) * 0.05, mano, grosor * 0.3, grosor * 0.28, piel, sp)
    d = np.asarray(mano, float) - codo
    mano_simple(lz, mano, math.atan2(d[1], d[0]), piel, sp, s=grosor / 50 * ancho_mano, cerrada=cerrada, cosa=cosa)
    return codo


def _ojos_familia(lz, quien, ancho, piel, mira, parpado, risa, mujer):
    for lado in (-1, 1):
        cx, cy = lado * ancho * 0.44 + mira[0] * 8, -24 + mira[1] * 8
        if risa > 0.5:
            lz.pincel([(cx - 20, cy + 4), (cx, cy - 10), (cx + 20, cy + 4)], 7)
            continue
        alto = 12 * (1 - parpado)
        ojo = [(cx - 22, cy), (cx - 8, cy - alto), (cx + 10, cy - alto), (cx + 22, cy), (cx + 8, cy + alto * 0.7),
               (cx - 8, cy + alto * 0.7)]
        if alto > 2:
            lz.forma(np.array(ojo, float), hexa("#ece6d8"), grosor=3)
            lz.recorte(np.array(ojo, float))
            ix = cx + mira[0] * 9
            lz.forma(elipse(ix, cy + mira[1] * 3, 9, 10, 10), hexa("#2c190f"), tinta=False)
            lz.forma(elipse(ix - 3, cy - 3, 2.2, 2.2, 8), hexa("#f4f0e6"), tinta=False, hervor=0)
            lz.restaurar()
        lz.pincel([(cx - 24, cy + 1), (cx - 8, cy - alto - 3), (cx + 12, cy - alto - 2), (cx + 25, cy - 2)],
                  8 if mujer else 6, punta=0.25)
        if mujer:
            lz.pincel([(cx + lado * 22, cy - 2), (cx + lado * 32, cy - 10)], 4)


def familiar(lz, x, y, s, quien, t=0.0, habla=0.0, risa=0.0, mira=(0, 0), parpado=0.0, luz=(-10, -8),
             inclina=0.0, contraluz=None, ropa=True):
    """Mamá, papá o hermana de frente (busto). habla/risa 0..1."""
    e = FAMILIA[quien]
    piel, pelo = e["piel"], e["pelo"]
    ps = mezcla(oscuro(piel, 0.66), hexa("#3a2c3c"), 0.2)
    ancho = e["ancho"]
    mujer = quien != "papa"
    brillo = contraluz[0] if contraluz else None
    filo = contraluz[1] if contraluz else (0, 0)
    lz.guardar()
    lz.mover(x, y, s)

    # Pelo de atrás.
    if quien == "mama":
        atras = [(0, -236), (90, -212), (150, -130), (168, -10), (182, 120), (205, 250), (190, 330), (150, 300),
                 (120, 340), (80, 260), (-80, 260), (-120, 340), (-150, 300), (-190, 330), (-205, 250), (-182, 120),
                 (-168, -10), (-150, -130), (-90, -212)]
        lz.forma(np.array(atras, float), pelo, sombra=oscuro(pelo, 0.5), luz=(-8, -8), brillo=brillo, contraluz=filo)
    elif quien == "hermana":
        onda = math.sin(t * 2.2) * 8
        cola = [(90, -170), (170, -150), (215, -60), (225 + onda, 60), (200 + onda, 150), (185 + onda, 60), (160, -60),
                (110, -110)]
        lz.forma(np.array(cola, float), pelo, sombra=oscuro(pelo, 0.5), luz=(-6, -6), brillo=brillo, contraluz=filo)
        lz.forma(elipse(122, -150, 26, 20, 10), hexa("#b8344a"), grosor=3)

    if ropa:
        hombros = e["hombros"]
        torso = [(-50, 196), (-hombros * 0.7, 250), (-hombros, 330), (-hombros * 1.08, 560), (-hombros * 1.1, 820),
                 (hombros * 1.1, 820), (hombros * 1.08, 560), (hombros, 330), (hombros * 0.7, 250), (50, 196)]

        def estampado():
            if e["estampado"] is None:
                return
            rng = np.random.default_rng(7 if quien == "mama" else 8)
            for _ in range(46):
                fx, fy = rng.uniform(-hombros * 1.1, hombros * 1.1), rng.uniform(220, 820)
                if quien == "mama":
                    for k in range(5):
                        a = k * 2 * math.pi / 5
                        lz.forma(elipse(fx + math.cos(a) * 9, fy + math.sin(a) * 9, 7, 7, 8), e["estampado"], tinta=False,
                                 hervor=0)
                    lz.forma(elipse(fx, fy, 5, 5, 8), hexa("#e7c25a"), tinta=False, hervor=0)
                else:
                    lz.pincel([(fx - 18, fy), (fx + 18, fy - 4)], 5, e["estampado"], hervor=0)

        lz.forma(np.array(torso, float), e["ropa"], sombra=oscuro(e["ropa"], 0.66), luz=(-20, -12), brillo=brillo,
                 contraluz=filo, relleno=estampado)
        if quien == "papa":
            for lado in (-1, 1):
                cuello = [(lado * 10, 214), (lado * 70, 196), (lado * 96, 250), (lado * 40, 300)]
                lz.forma(np.array(cuello, float), mezcla(e["ropa"], (1, 1, 1), 0.25), grosor=4)
            for k in range(3):
                lz.forma(elipse(0, 330 + k * 110, 6, 6, 8), hexa("#f0f0f0"), grosor=2)
            lz.linea([(0, 290), (0, 820)], 3)
    # Cuello (con escote en V para la mamá).
    cuello = [(-44, 110), (44, 110), (46, 216), (0, 236 if not mujer else 290), (-46, 216)]
    lz.forma(np.array(cuello, float), piel, sombra=ps, luz=(0, 40))

    lz.guardar()
    lz.mover(0, 0, 1, rot=inclina)
    if not mujer:
        for lado in (-1, 1):
            lz.forma(elipse(lado * (ancho + 6), 8, 20, 36, 12), piel, sombra=ps, luz=(lado * -8, 0))
    menton = 186 if mujer else 196
    cara = [(0, -205), (ancho * 0.62, -190), (ancho * 0.95, -130), (ancho, -60), (ancho, 10), (ancho * 0.9, 80),
            (ancho * 0.68, 136), (ancho * 0.36, 176), (0, menton), (-ancho * 0.36, 176), (-ancho * 0.68, 136),
            (-ancho * 0.9, 80), (-ancho, 10), (-ancho, -60), (-ancho * 0.95, -130), (-ancho * 0.62, -190)]
    if not mujer:
        cara = [(px * (1.06 if py > 60 else 1.0), py) for px, py in cara]
    lz.forma(np.array(cara, float), piel, sombra=ps, luz=luz, brillo=brillo, contraluz=filo)
    # Mejillas.
    if mujer:
        for lado in (-1, 1):
            lz.mancha(elipse(lado * ancho * 0.55, 40, 22, 12, 10), hexa("#c7564f"), 0.25)

    _ojos_familia(lz, quien, ancho, piel, mira, parpado, risa, mujer)
    for lado in (-1, 1):
        cx = lado * ancho * 0.44 + mira[0] * 8
        sube = risa * 8
        lz.pincel([(cx - lado * 30, -62 - sube), (cx, -72 - sube), (cx + lado * 28, -64 - sube)], 10 if not mujer else 6)
    # Nariz.
    nx = mira[0] * 12
    lz.pincel([(6 + nx, -20), (12 + nx, 24), (4 + nx, 40)], 3.5)
    lz.pincel([(-14 + nx, 42), (0 + nx, 48), (14 + nx, 42)], 3.5)
    # Bigote de papá.
    if quien == "papa":
        lz.forma(np.array([(-50 + nx, 74), (-20 + nx, 58), (0 + nx, 64), (20 + nx, 58), (50 + nx, 74), (40 + nx, 84),
                           (0 + nx, 78), (-40 + nx, 84)], float), pelo, grosor=3)
    # Boca.
    bx, by = nx, 104
    abre = max(habla, risa)
    if abre > 0.08:
        ry = 6 + 26 * abre
        rx = 26 + 10 * risa
        boca = [(bx - rx, by - 4), (bx, by - 8), (bx + rx, by - 4), (bx + rx * 0.7, by + ry * 0.7), (bx, by + ry),
                (bx - rx * 0.7, by + ry * 0.7)]
        lz.forma(np.array(boca, float), hexa("#3a1214"), grosor=4)
        if risa > 0.3:
            lz.recorte(np.array(boca, float))
            lz.forma(np.array([(bx - rx, by - 10), (bx + rx, by - 10), (bx + rx, by + 4), (bx - rx, by + 4)], float),
                     hexa("#efe8da"), tinta=False, suave=False)
            lz.restaurar()
        if e["labios"] is not None:
            lz.pincel([(bx - rx - 2, by - 4), (bx, by - 10), (bx + rx + 2, by - 4)], 5, e["labios"])
    else:
        col = e["labios"]
        lz.pincel([(bx - 28, by - 2), (bx, by + 5), (bx + 28, by - 2)], 5)
        if col is not None:
            lz.pincel([(bx - 20, by + 6), (bx, by + 12), (bx + 20, by + 6)], 6, col, alfa=0.9)
    # Aretes.
    if mujer:
        for lado in (-1, 1):
            lz.forma(elipse(lado * (ancho + 2), 64, 7, 7, 8), hexa("#d9b24a"), grosor=2)

    # Pelo de enfrente.
    if quien == "mama":
        for lado in (-1, 1):
            mech = [(0, -214), (lado * 70, -206), (lado * 118, -150), (lado * 128, -60), (lado * 124, 40),
                    (lado * 136, 120), (lado * 110, 60), (lado * 104, -40), (lado * 86, -120), (lado * 40, -170)]
            lz.forma(np.array(mech, float), pelo, sombra=oscuro(pelo, 0.5), luz=(-8, -8), brillo=brillo, contraluz=filo)
    elif quien == "hermana":
        fleco = [(-112, -40), (-120, -140), (-80, -210), (0, -232), (80, -210), (120, -140), (112, -40), (100, -96),
                 (60, -110), (20, -100), (-20, -112), (-60, -98), (-100, -110)]
        lz.forma(np.array(fleco, float), pelo, sombra=oscuro(pelo, 0.5), luz=(-8, -8), brillo=brillo, contraluz=filo,
                 tension=0.8)
    else:
        corto = [(-128, -30), (-136, -120), (-100, -200), (-30, -232), (50, -228), (112, -196), (138, -120), (130, -30),
                 (116, -100), (84, -148), (20, -150), (-40, -140), (-100, -120), (-114, -60)]
        lz.forma(np.array(corto, float), pelo, sombra=oscuro(pelo, 0.5), luz=(-8, -8), brillo=brillo, contraluz=filo,
                 tension=0.8)
        for lado in (-1, 1):
            lz.pincel([(lado * 124, -60), (lado * 128, -10)], 6, hexa("#6d6a6e"))
    lz.restaurar()
    lz.restaurar()


# --- los niños del recuerdo ----------------------------------------------------------------------

def nino(lz, x, y, s, t=0.0, risa=1.0, brazos=1.0, inclina=0.0):
    """Alex de niño (unos 7 años) con playera de rayas, brazos arriba. Origen: centro de la cara."""
    piel = hexa("#a87050")
    ps = oscuro(piel, 0.7)
    lz.guardar()
    lz.mover(x, y, s, rot=inclina)
    # Piernas colgando.
    for lado in (-1, 1):
        balanceo = math.sin(t * 2.4 + lado) * 12
        pierna = [(lado * 30, 360), (lado * 80, 360), (lado * 84 + balanceo, 560), (lado * 40 + balanceo, 560)]
        lz.forma(np.array(pierna, float), hexa("#3d5a8a"), sombra=hexa("#2a3d60"), luz=(-6, 0), suave=False)
        lz.forma(np.array([(lado * 38 + balanceo, 560), (lado * 84 + balanceo, 560), (lado * 86 + balanceo, 650),
                           (lado * 40 + balanceo, 650)], float), piel, sombra=ps, luz=(-4, 0), suave=False)
        lz.forma(elipse(lado * 66 + balanceo, 668, 40, 20, 12), hexa("#e8e2d6"), grosor=4)
    # Playera de rayas.
    torso = [(-40, 150), (-110, 190), (-120, 380), (120, 380), (110, 190), (40, 150)]

    def rayas():
        for k in range(8):
            yy = 170 + k * 28
            col = hexa("#d8423a") if k % 2 == 0 else hexa("#f0e9dc")
            lz.forma(np.array([(-150, yy), (150, yy), (150, yy + 28), (-150, yy + 28)], float), col, tinta=False,
                     suave=False, hervor=0)

    lz.forma(np.array(torso, float), hexa("#f0e9dc"), relleno=rayas)
    for lado in (-1, 1):
        mano = (lado * (150 + 30 * brazos), -60 - 160 * brazos + math.sin(t * 3 + lado) * 10)
        brazo(lz, (lado * 100, 205), mano, 110, 110, hexa("#d8423a"), piel, grosor=40, doblez=-lado, corta=True)
    lz.forma(np.array([(-36, 100), (36, 100), (38, 170), (-38, 170)], float), piel, sombra=ps, luz=(0, 20))
    cara = elipse(0, 0, 120, 128, 20)
    lz.forma(cara, piel, sombra=ps, luz=(-10, -10))
    for lado in (-1, 1):
        lz.pincel([(lado * 46 - 18, -10), (lado * 46, -24), (lado * 46 + 18, -10)], 7)
        lz.mancha(elipse(lado * 70, 36, 20, 11, 10), hexa("#d9605a"), 0.35)
    lz.forma(np.array([(-40, 50), (40, 50), (30, 86), (0, 100), (-30, 86)], float), hexa("#3a1214"), grosor=4)
    lz.recorte(np.array([(-40, 50), (40, 50), (30, 86), (0, 100), (-30, 86)], float))
    lz.forma(np.array([(-40, 44), (40, 44), (40, 58), (-40, 58)], float), hexa("#efe8da"), tinta=False, suave=False)
    lz.restaurar()
    pelo = [(-120, -10), (-130, -80), (-90, -140), (-20, -160), (60, -150), (120, -100), (126, -10), (100, -60),
            (70, -40), (40, -80), (0, -50), (-40, -84), (-80, -50), (-104, -70)]
    lz.forma(np.array(pelo, float), hexa("#1a1316"), sombra=hexa("#0a080a"), luz=(-6, -8), tension=0.8)
    lz.restaurar()


def bebe(lz, x, y, s, t=0.0):
    """La hermana de bebé, con dos coletas."""
    piel = hexa("#b37a58")
    ps = oscuro(piel, 0.7)
    lz.guardar()
    lz.mover(x, y, s)
    lz.forma(np.array([(-90, 100), (90, 100), (110, 300), (-110, 300)], float), hexa("#f2b8c6"),
             sombra=hexa("#c98a9c"), luz=(-10, -6))
    for lado in (-1, 1):
        lz.forma(elipse(lado * 112, -60, 34, 22, 10, rot=lado * 0.5), hexa("#1a1316"), grosor=4)
    lz.forma(elipse(0, 0, 100, 104, 18), piel, sombra=ps, luz=(-8, -8))
    for lado in (-1, 1):
        lz.pincel([(lado * 38 - 14, -4), (lado * 38, -16), (lado * 38 + 14, -4)], 6)
        lz.mancha(elipse(lado * 60, 30, 16, 9, 10), hexa("#d9605a"), 0.35)
    lz.forma(elipse(0, 50, 20, 16 + 6 * abs(math.sin(t * 3)), 12), hexa("#3a1214"), grosor=3)
    lz.forma(np.array([(-60, -70), (-20, -110), (30, -104), (60, -70), (20, -84), (-20, -80)], float), hexa("#1a1316"),
             grosor=3)
    lz.restaurar()
