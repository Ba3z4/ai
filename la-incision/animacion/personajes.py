"""Personajes: Alex, su familia y las tres figuras enmascaradas.

Cada función dibuja en coordenadas locales (se coloca con x, y, s) y recibe su pose como
parámetros, para animarla cuadro a cuadro desde los planos.
"""

import math

import numpy as np

from dibujo import elipse, hexa, mezcla, oscuro

# --- paleta de personajes ----------------------------------------------------------------------

PIEL_ALEX = hexa("#9a6a4c")
PELO = hexa("#141015")
SUDADERA = hexa("#3d4440")
MASCARA = hexa("#dcd8cc")
MASCARA_SOMBRA = hexa("#8a8e96")
CUERPO_SOMBRA = hexa("#07080c")


# --- las figuras -------------------------------------------------------------------------------

def _harapos(x0, x1, y, n, largo, semilla, t, ondula=1.0):
    """Borde deshilachado (dobladillo o manga) de izquierda a derecha."""
    rng = np.random.default_rng(semilla)
    pts = []
    for i in range(n + 1):
        u = i / n
        x = x0 + (x1 - x0) * u
        onda = math.sin(t * 1.3 + i * 0.9 + semilla) * 10 * ondula
        if i % 2:
            pts.append((x + onda, y + largo * (0.5 + rng.random())))
        else:
            pts.append((x + onda * 0.5, y - largo * 0.25 * rng.random()))
    return pts


def figura(lz, x, y, s, t=0.0, inclina=0.0, semilla=0, alfa=1.0, contraluz=1.0, brazo=0.0,
           mascara_brillo=1.0, flota=1.0):
    """Figura alta, flaca y oscura con máscara blanca lisa. Origen: los pies. Mide ~1000 unidades.

    inclina: ladeo de la cabeza (radianes). brazo: 0 colgando, 1 extendido hacia la cámara.
    contraluz: filo de luz de luna del lado derecho.
    """
    lz.guardar()
    flotar = math.sin(t * 1.1 + semilla * 2.3) * 8 * flota
    lz.mover(x, y + flotar, s)
    if alfa < 1:
        lz.grupo()
    cuerpo = hexa("#05060a")
    filo = mezcla(cuerpo, hexa("#6d8aa8"), 0.6 * contraluz)
    luz = dict(brillo=filo, contraluz=(9, 0), sombra=None)

    # Túnica larga que se deshace en la oscuridad del piso.
    tunica = [(-40, -805), (-96, -770), (-112, -660), (-118, -470), (-128, -260), (-142, -90)]
    tunica += _harapos(-142, 142, -70, 10, 36, semilla, t, ondula=0.6)
    tunica += [(142, -90), (128, -260), (118, -470), (112, -660), (96, -770), (40, -805)]
    lz.forma(np.array(tunica, float), cuerpo, **luz, grosor=4.5)
    lz.degradado(0, -260, 0, 10, [(0, cuerpo, 0), (1, cuerpo, 0.95)], rect=(-170, -260, 340, 300))

    # Brazos flacos y larguísimos (el derecho se puede alzar hacia la cámara).
    for lado in (-1, 1):
        alza = brazo if lado == 1 else 0.0
        hombro = np.array([lado * 98, -752.0])
        codo = hombro + np.array([lado * 22, 250]) * (1 - alza) + np.array([-lado * 10, 90]) * alza
        mano = codo + np.array([lado * 6, 250]) * (1 - alza) + np.array([-lado * 70, 150]) * alza
        manga = [hombro + (-lado * 20, -4), hombro + (lado * 22, 8), codo + (lado * 20, 0), mano + (lado * 14, -26),
                 mano + (-lado * 12, -26), codo + (-lado * 18, 4)]
        lz.forma(np.array(manga, float), cuerpo, **luz, grosor=4.5)
        for k, (dx, largo) in enumerate(((-12, 120), (-4, 150), (5, 142), (13, 108))):
            base = mano + (dx * lado, -20)
            curva = 0.3 * math.sin(t * 0.9 + k * 1.7 + semilla)
            punta = base + (dx * lado * 0.6 + curva * 26, largo)
            medio = (base + punta) / 2 + (curva * 12 + lado * 4, 0)
            lz.pincel([base, medio, punta], 8, cuerpo)
            if contraluz > 0 and lado == 1:
                lz.pincel([base + (4, 0), medio + (4, 0), punta + (2, -4)], 2.2, filo, alfa=0.8)

    lz.guardar()
    lz.mover(0, -805, 1, rot=inclina)
    _cabeza(lz, t, semilla, luz, cuerpo, filo, mascara_brillo)
    lz.restaurar()

    if alfa < 1:
        lz.soltar(alfa)
    lz.restaurar()


def _cabeza(lz, t, semilla, luz, cuerpo, filo, mascara_brillo, boca=0.0, pupilas=0.0, grietas=False):
    """Melena lacia, máscara y huecos de los ojos. Origen: la base del cuello.

    boca 0..1 abre una grieta con dientes en la máscara (el narrador habla); pupilas 0..1 enciende
    dos puntitos de luz en el fondo de los ojos.
    """
    pelo = [(-70, -150), (-30, -205), (30, -205), (70, -150), (84, -40), (92, 80), (100, 190)]
    pelo += _harapos(100, -100, 190, 7, 70, semilla + 5, t, ondula=0.5)
    pelo += [(-100, 190), (-92, 80), (-84, -40)]
    lz.forma(np.array(pelo, float), cuerpo, **luz, grosor=4.5)
    for k in range(7):
        fx = -80 + k * 27
        lz.pincel([(fx * 0.5, -160), (fx * 0.9, -20), (fx * 1.1 + math.sin(t + k) * 6, 170)], 3,
                  mezcla(cuerpo, filo, 0.3 if fx > 0 else 0.1))
    mascara = np.array([(0, -176), (36, -166), (54, -128), (57, -74), (50, -20), (32, 26), (0, 44), (-32, 26), (-50, -20),
                        (-57, -74), (-54, -128), (-36, -166)], float) + (0, -6)
    lz.resplandor(0, -70, 190, hexa("#a9bdd2"), 0.09 * mascara_brillo)
    lz.forma(mascara, mezcla(MASCARA_SOMBRA, MASCARA, mascara_brillo), sombra=MASCARA_SOMBRA, luz=(8, -5), grosor=4.5)
    # Ojos: huecos negros, caídos hacia afuera. Ni nariz ni boca.
    for lado in (-1, 1):
        ojo = [(lado * 9, -97), (lado * 22, -106), (lado * 39, -101), (lado * 46, -88), (lado * 31, -83), (lado * 15, -86)]
        lz.forma(np.array(ojo, float), hexa("#000000"), grosor=2.5)
    lz.pincel([(-2, -80), (0, -56)], 2.5, oscuro(MASCARA_SOMBRA, 0.9), alfa=0.35)
    if pupilas > 0:
        for lado in (-1, 1):
            lz.resplandor(lado * 27 + math.sin(t * 0.7) * 2, -94, 9, (1, 1, 1), 0.9 * pupilas)
            lz.forma(elipse(lado * 27 + math.sin(t * 0.7) * 2, -94, 2.2, 2.2, 8), (1, 1, 1), tinta=False,
                     alfa=pupilas, hervor=0)
    if grietas:
        for g in ([(-40, -150), (-28, -128), (-34, -112), (-22, -96)], [(30, -40), (18, -20), (26, 0), (14, 20)],
                  [(46, -120), (36, -104), (40, -88)]):
            lz.pincel(g, 2.2, oscuro(MASCARA_SOMBRA, 0.55), alfa=0.8)
    if boca > 0.02:
        ancho, alto = 30 + 8 * boca, 4 + 30 * boca
        cy = -8
        borde = []
        for i in range(9):
            x = -ancho + 2 * ancho * i / 8
            borde.append((x, cy - alto * 0.35 * (1 - (x / ancho) ** 2) + (3 if i % 2 else -3)))
        for i in range(9):
            x = ancho - 2 * ancho * i / 8
            borde.append((x, cy + alto * (1 - (x / ancho) ** 2) + (4 if i % 2 else -2)))
        lz.forma(np.array(borde, float), hexa("#050305"), grosor=2.5)
        if boca > 0.25:
            for i in range(6):
                x = -ancho * 0.7 + i * ancho * 0.28
                arriba = cy - alto * 0.3 * (1 - (x / ancho) ** 2)
                lz.forma(np.array([(x - 4, arriba), (x + 4, arriba), (x, arriba + 9 * boca)], float),
                         hexa("#d9d3c2"), tinta=False, suave=False, hervor=0)


def mascara_cerca(lz, x, y, s, t=0.0, inclina=0.0, semilla=0, contraluz=1.0, mascara_brillo=1.0, hombros=True,
                  boca=0.0, pupilas=0.0, grietas=False):
    """Cabeza de una figura muy de cerca (encima de la cara de Alex). Origen: centro de la máscara."""
    cuerpo = hexa("#05060a")
    filo = mezcla(cuerpo, hexa("#6d8aa8"), 0.6 * contraluz)
    luz = dict(brillo=filo, contraluz=(7, 0), sombra=None)
    lz.guardar()
    lz.mover(x, y, s, rot=inclina)
    if hombros:
        lz.forma(np.array([(-260, 520), (-200, 250), (-80, 170), (80, 170), (200, 250), (260, 520), (300, 900),
                           (-300, 900)], float), cuerpo, **luz, grosor=4.5)
    lz.mover(0, 80, 1)
    _cabeza(lz, t, semilla, luz, cuerpo, filo, mascara_brillo, boca, pupilas, grietas)
    lz.restaurar()


# --- Alex --------------------------------------------------------------------------------------

def _ojo(lz, cx, cy, lado, parpado, mira, piel, ojera, abierto=1.0, grande=1.0):
    """Ojo de frente: blanco, iris, párpado pesado y ojera. parpado 0 abierto … 1 cerrado."""
    ancho, alto = 25 * grande, 11 * grande * abierto
    blanco = [(cx - ancho, cy + 1), (cx - ancho * 0.4, cy - alto), (cx + ancho * 0.5, cy - alto * 0.95),
              (cx + ancho, cy - 1), (cx + ancho * 0.4, cy + alto * 0.8), (cx - ancho * 0.5, cy + alto * 0.75)]
    blanco = np.array(blanco, float)
    if lado < 0:
        blanco[:, 0] = 2 * cx - blanco[:, 0]
    lz.forma(np.array([(cx - ancho * 1.1, cy + 16), (cx, cy + 26), (cx + ancho * 1.1, cy + 14), (cx, cy + 12)], float),
             ojera, tinta=False, alfa=0.55)
    if parpado >= 0.98:
        lz.pincel([(cx - ancho, cy + 2), (cx, cy + 6), (cx + ancho, cy + 2)], 5)
        return
    esclera = mezcla(hexa("#e9e2d2"), piel, 0.45) if lz.sin_tinta else hexa("#e9e2d2")
    lz.forma(blanco, esclera, grosor=3.5)
    lz.recorte(blanco)
    ix, iy = cx + mira[0] * ancho * 0.55, cy + mira[1] * alto * 0.5
    lz.forma(elipse(ix, iy, 9.5 * grande, 10.5 * grande, 12), hexa("#3b2416"), grosor=2)
    lz.forma(elipse(ix, iy, 4.5 * grande, 4.5 * grande, 10), hexa("#050404"), tinta=False)
    lz.forma(elipse(ix - 3, iy - 4, 2.2, 2.2, 8), hexa("#f4f0e6"), tinta=False, hervor=0)
    if parpado > 0:
        caida = -alto - 4 + (alto * 2 + 8) * parpado
        lz.forma(np.array([(cx - ancho * 1.3, cy - 40), (cx + ancho * 1.3, cy - 40), (cx + ancho * 1.3, cy + caida),
                           (cx, cy + caida + 3), (cx - ancho * 1.3, cy + caida)], float), piel, tinta=False)
        lz.pincel([(cx - ancho, cy + caida + 1), (cx, cy + caida + 4), (cx + ancho, cy + caida + 1)], 4.5)
    lz.restaurar()
    lz.pincel([(cx - ancho * 1.05 * lado, cy + 1), (cx - ancho * 0.3 * lado, cy - alto - 2), (cx + ancho * 0.6 * lado, cy - alto - 1),
               (cx + ancho * 1.08 * lado, cy - 2)], 6.5, punta=0.3)


def alex_frente(lz, x, y, s, t=0.0, mira=(0, 0), parpado=0.25, boca="neutra", habla=0.0, cejas=0.0,
                inclina=0.0, luz=(-10, -6), piel=None, sudor=0.0, palidez=0.0, ropa=True, cuello=True,
                agitado=0.0, contraluz=None):
    """Cabeza y hombros de Alex de frente. Origen: centro de la cara. Cabeza ~400 de alto.

    boca: neutra, media_sonrisa, abierta (grito), jadeo, apretada. habla 0..1 abre la boca.
    cejas: -1 enojado/tenso … 1 levantadas (miedo). mira: hacia dónde ven los ojos (-1..1).
    """
    piel = piel or mezcla(PIEL_ALEX, hexa("#a39a8e"), palidez * 0.55)
    piel_sombra = mezcla(oscuro(piel, 0.66), hexa("#3a2c3c"), 0.25)
    ojera = mezcla(piel_sombra, hexa("#4a3050"), 0.4 + palidez * 0.3)
    brillo = contraluz[0] if contraluz else None
    filo = contraluz[1] if contraluz else (0, 0)
    lz.guardar()
    lz.mover(x, y, s)

    if ropa:
        sud = SUDADERA
        cuerpo = [(-60, 190), (-150, 240), (-235, 320), (-270, 520), (-285, 800), (285, 800), (270, 520), (235, 320),
                  (150, 240), (60, 190)]
        lz.forma(np.array(cuerpo, float), sud, sombra=oscuro(sud, 0.62), luz=(-24, -10), brillo=brillo, contraluz=filo)
        capucha = [(-150, 205), (-100, 160), (0, 150), (100, 160), (150, 205), (110, 250), (0, 262), (-110, 250)]
        lz.forma(np.array(capucha, float), oscuro(sud, 0.8), sombra=oscuro(sud, 0.5), luz=(0, -10))
        for lado in (-1, 1):
            lz.pincel([(lado * 42, 250), (lado * 48, 330), (lado * 44, 410)], 5, hexa("#c9c3b5"))
        lz.pincel([(-205, 420), (-185, 600)], 5, oscuro(sud, 0.45))
        lz.pincel([(200, 430), (180, 610)], 5, oscuro(sud, 0.45))
    if cuello:
        lz.forma(np.array([(-46, 110), (46, 110), (50, 236), (0, 256), (-50, 236)], float), piel,
                 sombra=piel_sombra, luz=(0, 40))

    lz.guardar()
    lz.mover(0, 0, 1, rot=inclina)
    mx, my = mira[0] * 10, mira[1] * 12  # la cara «gira» un poco hacia donde mira
    for lado in (-1, 1):
        oreja = elipse(lado * 126, 8, 21, 38, 12)
        lz.forma(oreja, piel, sombra=piel_sombra, luz=(lado * -8, 0))
        lz.pincel([(lado * 124, -10), (lado * 132, 8), (lado * 124, 26)], 3, piel_sombra)
    cara = [(0, -205), (72, -190), (114, -132), (122, -62), (123, 8), (110, 80), (88, 132), (46, 178), (0, 192),
            (-46, 178), (-88, 132), (-110, 80), (-123, 8), (-122, -62), (-114, -132), (-72, -190)]
    lz.forma(np.array(cara, float), piel, sombra=piel_sombra, luz=luz, brillo=brillo, contraluz=filo)
    # Barba de días.
    barba = [(-104, 70), (-80, 128), (-40, 170), (0, 182), (40, 170), (80, 128), (104, 70), (70, 110), (40, 140),
             (0, 150), (-40, 140), (-70, 110)]
    lz.mancha(np.array(barba, float), hexa("#2a1e22"), 0.28)
    lz.mancha(np.array([(-34 + mx, 76 + my), (0 + mx, 70 + my), (34 + mx, 76 + my), (0 + mx, 84 + my)], float),
              hexa("#2a1e22"), 0.3)

    # Ojos y cejas.
    for lado in (-1, 1):
        _ojo(lz, lado * 52 + mx, -28 + my, lado, parpado, mira, piel, ojera, abierto=1 + cejas * 0.35)
        levanta = cejas * 14
        lz.pincel([(lado * 86 + mx, -64 + my - levanta * 0.4), (lado * 56 + mx, -74 + my - levanta),
                   (lado * 20 + mx, -66 + my - levanta * 1.1 + max(-cejas, 0) * 12)], 12, punta=0.35)
    # Nariz.
    lz.pincel([(8 + mx * 1.3, -30 + my), (14 + mx * 1.3, 18 + my), (6 + mx * 1.3, 40 + my)], 4)
    lz.mancha(np.array([(10 + mx * 1.3, -10 + my), (26 + mx * 1.3, 30 + my), (8 + mx * 1.3, 44 + my)], float), piel_sombra, 0.7)
    lz.pincel([(-18 + mx * 1.3, 42 + my), (-6 + mx * 1.3, 49 + my), (8 + mx * 1.3, 47 + my), (20 + mx * 1.3, 40 + my)], 4)

    # Boca.
    bx, by = mx * 1.1, 104 + my
    abre = habla
    if boca in ("abierta", "jadeo") or abre > 0.05:
        if boca == "abierta":
            rx, ry = 34 + agitado * 4, 46
        elif boca == "jadeo":
            rx, ry = 20, 14 + 10 * abs(math.sin(t * 9))
        else:
            rx, ry = 22, 5 + 16 * abre
        dy = ry * 0.4
        lz.forma(elipse(bx, by + dy, rx, ry, 16), hexa("#2a0e10"), grosor=4)
        if ry > 12:
            lz.recorte(elipse(bx, by + dy, rx, ry, 16))
            lz.forma(np.array([(bx - rx, by + dy - ry), (bx + rx, by + dy - ry), (bx + rx, by + dy - ry + 8),
                               (bx - rx, by + dy - ry + 8)], float), hexa("#e2dccb"), tinta=False, suave=False)
            lz.forma(elipse(bx, by + dy + ry * 0.8, rx * 0.6, ry * 0.4, 12), hexa("#8a3a3a"), tinta=False)
            lz.restaurar()
    elif boca == "media_sonrisa":
        lz.pincel([(bx - 34, by - 2), (bx - 8, by + 4), (bx + 18, by), (bx + 36, by - 12)], 5.5)
        lz.pincel([(bx + 34, by - 20), (bx + 40, by - 8)], 3)
    elif boca == "apretada":
        lz.pincel([(bx - 30, by + 2), (bx, by), (bx + 30, by + 2)], 6)
    else:
        lz.pincel([(bx - 30, by + 3), (bx - 6, by), (bx + 16, by + 1), (bx + 30, by + 5)], 5.5)
    lz.pincel([(bx - 16, by + 24), (bx, by + 28), (bx + 16, by + 24)], 3, piel_sombra)

    # Pelo negro, despeinado, con fleco en picos.
    pelo = [(-126, 30), (-138, -60), (-146, -140), (-122, -206), (-70, -246), (-8, -262), (60, -254), (116, -222),
            (146, -150), (140, -62), (126, 30), (116, -40), (112, -110), (86, -92), (70, -128), (40, -104), (18, -140),
            (-10, -108), (-38, -142), (-62, -104), (-90, -134), (-112, -100), (-116, -40)]
    lz.forma(np.array(pelo, float), PELO, sombra=hexa("#07060a"), luz=(-10, -12),
             brillo=brillo if brillo else hexa("#2c2733"), contraluz=filo if contraluz else (-6, -8), tension=0.7)
    for k in range(5):
        px = -90 + k * 45
        lz.pincel([(px, -230 + abs(px) * 0.2), (px + 16, -180), (px + 10, -150)], 3.5, hexa("#3a3440"))
    # Sudor frío.
    if sudor > 0:
        for k, (sx, sy) in enumerate(((-96, -70), (82, -96), (-60, -140), (104, 40), (-30, 120))):
            if k / 5 < sudor:
                baja = (t * 30 + k * 40) % 90 * sudor
                gota = [(sx, sy + baja - 10), (sx + 6, sy + baja + 6), (sx, sy + baja + 12), (sx - 6, sy + baja + 6)]
                lz.forma(np.array(gota, float), hexa("#d9e6ef"), grosor=2.2, alfa=0.9)
    lz.restaurar()
    lz.restaurar()


def alex_perfil(lz, x, y, s, t=0.0, parpado=0.3, boca=0.0, mira_abajo=0.6, luz=(-12, -4),
                luz_cara=None, sudor=0.0, piel=None, ropa=True, jadeo=0.0, palidez=0.0, contraluz=None, inclina=0.0):
    """Alex de perfil mirando a la izquierda. Origen: centro de la cabeza. Cabeza ~420 de alto.

    luz_cara: (color, alfa) de una luz que le pega desde abajo (el celular).
    inclina: cuánto agacha la cabeza (radianes).
    """
    piel = piel or mezcla(PIEL_ALEX, hexa("#a39a8e"), palidez * 0.55)
    piel_sombra = mezcla(oscuro(piel, 0.62), hexa("#3a2c3c"), 0.25)
    brillo = contraluz[0] if contraluz else None
    filo = contraluz[1] if contraluz else (0, 0)
    lz.guardar()
    lz.mover(x, y, s)
    if ropa:
        sud = SUDADERA
        cuerpo = [(10, 160), (150, 190), (240, 260), (300, 420), (330, 700), (-260, 700), (-240, 460), (-160, 300),
                  (-60, 230)]
        lz.forma(np.array(cuerpo, float), sud, sombra=oscuro(sud, 0.6), luz=(-20, -16), brillo=brillo, contraluz=filo)
        capucha = [(60, 120), (170, 110), (240, 180), (250, 260), (170, 250), (90, 210)]
        lz.forma(np.array(capucha, float), oscuro(sud, 0.8), sombra=oscuro(sud, 0.5), luz=(-10, -8))
        lz.pincel([(-40, 240), (-50, 330), (-44, 420)], 5, hexa("#c9c3b5"))
    if inclina:
        lz.ctx.translate(30, 170)
        lz.ctx.rotate(-inclina)
        lz.ctx.translate(-30, -170)
    # Cuello.
    lz.forma(np.array([(-40, 100), (70, 80), (110, 210), (-30, 250)], float), piel, sombra=piel_sombra, luz=(-8, 30))
    perfil = [(60, -205), (-10, -196), (-58, -162), (-78, -118), (-84, -90), (-78, -70), (-92, -44), (-112, -14),
              (-130, 10), (-124, 20), (-106, 24), (-98, 30), (-104, 44), (-94, 54), (-100, 64), (-90, 80), (-96, 108),
              (-86, 136), (-40, 158), (20, 160), (80, 130), (120, 70), (148, -30), (140, -120), (110, -180)]
    perfil = np.array(perfil, float)
    lz.forma(perfil, piel, sombra=piel_sombra, luz=luz, brillo=brillo, contraluz=filo, tension=0.75)
    if luz_cara:
        lz.recorte(np.array(perfil, float))
        lz.resplandor(-120, 60, 190, luz_cara[0], luz_cara[1])
        lz.restaurar()
    # Barba de días.
    lz.recorte(perfil)
    lz.mancha(np.array([(-110, 40), (-100, 100), (-90, 150), (40, 170), (110, 110), (60, 90), (-10, 110), (-60, 80),
                        (-76, 36)], float), hexa("#2a1e22"), 0.3)
    lz.restaurar()
    # Oreja.
    lz.forma(elipse(58, -4, 24, 40, 12), piel, sombra=piel_sombra, luz=(-8, 0))
    lz.pincel([(52, -24), (66, -4), (54, 20)], 3, piel_sombra)
    # Ojo de perfil (mirando abajo), ojera y ceja.
    ox, oy = -58, -54
    lz.forma(np.array([(ox - 12, oy + 22), (ox + 16, oy + 34), (ox + 34, oy + 20), (ox + 8, oy + 14)], float),
             mezcla(piel_sombra, hexa("#4a3050"), 0.4), tinta=False, alfa=0.6)
    if parpado < 0.95:
        ojo = [(ox - 14, oy + 2 + mira_abajo * 4), (ox + 4, oy - 8), (ox + 18, oy - 4), (ox + 16, oy + 8), (ox + 2, oy + 10)]
        lz.forma(np.array(ojo, float), hexa("#e6dece"), grosor=3)
        lz.forma(elipse(ox - 4, oy + 1 + mira_abajo * 4, 5.5, 6.5, 10), hexa("#1d120c"), tinta=False)
        caida = -8 + 18 * parpado
        lz.pincel([(ox - 16, oy + caida + mira_abajo * 3), (ox + 2, oy + caida - 4), (ox + 20, oy + caida - 2)], 6.5)
    else:
        lz.pincel([(ox - 14, oy + 6), (ox + 18, oy + 6)], 5)
    lz.pincel([(ox - 30, oy - 30), (ox - 4, oy - 42), (ox + 36, oy - 38)], 11, punta=0.35)
    # Boca de perfil.
    if boca > 0.05 or jadeo > 0:
        abre = max(boca, jadeo * (0.5 + 0.5 * abs(math.sin(t * 8))))
        lz.forma(np.array([(-102, 50), (-80, 48 - abre * 4), (-74, 60 + abre * 16), (-98, 64 + abre * 20)], float),
                 hexa("#140708"), grosor=3.5)
    else:
        lz.pincel([(-98, 54), (-86, 57), (-72, 61)], 4)
    lz.pincel([(-118, 12), (-110, 4), (-100, 10)], 3, piel_sombra)
    # Pelo.
    pelo = [(-40, -170), (-70, -200), (-40, -236), (10, -250), (60, -252), (110, -236), (152, -196), (170, -130),
            (168, -50), (150, 10), (120, 40), (100, -10), (80, -60), (40, -80), (0, -120), (-30, -130), (-54, -150),
            (-86, -150), (-70, -176)]
    lz.forma(np.array(pelo, float), PELO, sombra=hexa("#07060a"), luz=(-8, -12),
             brillo=brillo if brillo else hexa("#2c2733"), contraluz=filo if contraluz else (-6, -8), tension=0.7)
    for k in range(4):
        lz.pincel([(-20 + k * 40, -225), (10 + k * 40, -180), (30 + k * 40, -140)], 3.5, hexa("#3a3440"))
    if sudor > 0:
        for k, (sx, sy) in enumerate(((-40, -140), (10, -60), (-60, 110), (40, 40))):
            if k / 4 < sudor:
                baja = (t * 30 + k * 40) % 80 * sudor
                gota = [(sx, sy + baja - 10), (sx + 6, sy + baja + 6), (sx, sy + baja + 12), (sx - 6, sy + baja + 6)]
                lz.forma(np.array(gota, float), hexa("#d9e6ef"), grosor=2.2, alfa=0.9)
    lz.restaurar()
