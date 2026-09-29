"""Los planos del corto animado: qué se dibuja en cada cuadro, cómo se mueve la cámara y qué
efectos pide cada momento (subtítulos, fallas de la cinta, destellos).

Cada plano recibe el tiempo real `t` (para la cámara, a 24 cuadros) y `tq`, el tiempo cuantizado
a 12 dibujos por segundo con el que se animan los personajes, como en la animación a dos.
"""

import math

import cairo
import numpy as np

from cuerpo import (alex_acostado, alex_incorporado, antebrazo, celular, dedo, extremidad, manos_celular,
                    mama_recuerdo, papa_recuerdo, rect_redondo, tenedor)
from dibujo import H, W, Lienzo, hexa, mezcla, oscuro, suave, tramo
from escenarios import (Fondo, cobija, cuarto_lado, cuarto_noche, lampara, mesa_cerca, mesa_comedor, mesa_frente,
                        mesa_pov, pared_comedor, parque, sabana, silla, techo, ventilador, ventilador_techo)
from familia import brazo, familiar
from personajes import PIEL_ALEX, SUDADERA, alex_frente, alex_perfil, figura, mascara_cerca

FPS = 24
LUNA = hexa("#9fc0e6")


def latido(t, bpm):
    """Pulso de 0..1 con forma de latido (dos golpes)."""
    fase = (t * bpm / 60) % 1
    return math.exp(-fase * 14) + 0.6 * math.exp(-max(fase - 0.18, 0) * 14) * (fase > 0.18)


def temblor(tq, fuerza, semilla=0):
    rng = np.random.default_rng((semilla, int(tq * 12)))
    return rng.normal(0, fuerza), rng.normal(0, fuerza)


def parpados(lz, cierre):
    """Párpados que cierran la vista subjetiva desde arriba y desde abajo."""
    if cierre <= 0.001:
        return
    lz.pantalla()
    cierre = min(cierre, 1.0)
    for arriba in (True, False):
        alto = (H / 2 + 40) * cierre * (1.0 if arriba else 0.85)
        comba = 170 * (1 - cierre * 0.7)
        pts = []
        for i in range(13):
            x = -60 + (W + 120) * i / 12
            v = (x - W / 2) / (W / 2)
            y = alto + comba * (1 - v * v) - comba * 0.4
            pts.append((x, y if arriba else H - y))
        pts += [(W + 60, -60), (-60, -60)] if arriba else [(W + 60, H + 60), (-60, H + 60)]
        borde = np.array(pts, float)
        lz.mancha(borde + (0, 34 if arriba else -34), (0, 0, 0), 0.45, hervor=0)
        lz.mancha(borde, (0, 0, 0), 1.0, hervor=0)


class Plano:
    grado = "neutro"
    vhs = 1.0

    def __init__(self, dur, ancho):
        self.dur = dur
        self.ancho = ancho
        self.preparar()

    def preparar(self):
        pass

    def dibujar(self, lz, t, tq):
        return {}


# --- gancho para TikTok --------------------------------------------------------------------------

class Gancho(Plano):
    """1.5 s de las máscaras encima de su cara antes de que empiece la cinta."""
    grado = "noche"

    def preparar(self):
        self.p = P3A(6, self.ancho)

    def dibujar(self, lz, t, tq):
        ef = self.p.dibujar(lz, 4.4 + t * 0.6, 4.4 + tq * 0.6)
        ef["falla"] = 0.3 + 0.7 * tramo(t, 0.8, 1.4)
        ef["nieve"] = tramo(t, 1.2, 1.5)
        return ef


# --- escena 1: la cena -------------------------------------------------------------------------

def _habla(tq, inicio, fin, vel=13.0, semilla=0):
    if not inicio <= tq <= fin:
        return 0.0
    silaba = 0.5 + 0.5 * math.sin(tq * vel + semilla)
    pausa = 0.5 + 0.5 * math.sin(tq * 1.7 + semilla * 3)
    return silaba * (0.35 + 0.65 * (pausa > 0.25))


def _celular_mano(lz, x, y, s, t):
    """El celular a escondidas bajo la mesa (se ve de lejos en 1A)."""
    lz.guardar()
    lz.mover(x, y, s, rot=-0.5)
    lz.resplandor(0, 0, 260, hexa("#5ea4e6"), 0.55)
    lz.forma(rect_redondo(-60, -110, 60, 110, 16), hexa("#15171b"), grosor=4, suave=False)
    lz.forma(rect_redondo(-50, -98, 50, 98, 10), hexa("#6fb0e8"), tinta=False, suave=False)
    for k in range(5):
        lado = -1 if k % 2 else 1
        yy = -70 + k * 34
        lz.forma(np.array([(lado * 40 - 26, yy), (lado * 40 + 26, yy), (lado * 40 + 26, yy + 20), (lado * 40 - 26, yy + 20)],
                          float), hexa("#1d4e46") if lado > 0 else hexa("#2b3a44"), tinta=False, suave=False)
    piel = PIEL_ALEX
    lz.forma(np.array([(-90, 40), (-40, 30), (10, 90), (40, 170), (-70, 190), (-110, 120)], float), piel,
             sombra=oscuro(piel, 0.62), luz=(6, -6))
    lz.forma(np.array([(60, 60), (100, 40), (140, 120), (110, 200), (40, 180)], float), piel, sombra=oscuro(piel, 0.62),
             luz=(-6, -6))
    lz.restaurar()


class P1A(Plano):
    grado = "cena"

    def preparar(self):
        self.pared = Fondo(pared_comedor, self.ancho, semilla=11)
        self.mesa = Fondo(mesa_comedor, self.ancho, semilla=12, transparente=True)

    def dibujar(self, lz, t, tq):
        k = suave(tramo(t, 0.4, self.dur - 0.3))
        lz.camara(1 + 0.85 * k, 540 + (812 - 540) * k, 990 + (1290 - 990) * k)
        self.pared.pintar(lz)
        lampara(lz, vaiven=math.sin(t * 0.9) * 0.02)
        risa_papa = max(0.0, math.sin((tq - 1.2) * 2.4)) * (1.2 < tq < 3.1)
        familiar(lz, 540, 790, 0.33, "papa", t=tq, risa=risa_papa, habla=_habla(tq, 4.5, 6.2, 11, 2) * 0.6,
                 mira=(-0.3, 0.2))
        silla(lz, 860, 1110, 0.5)
        familiar(lz, 208, 895, 0.47, "mama", t=tq, habla=_habla(tq, 0.2, 7.8, 13, 0), mira=(0.7, 0.1),
                 inclina=math.sin(tq * 1.3) * 0.04, luz=(12, -8))
        risa_h = 0.7 * (2.0 < tq < 2.9)
        familiar(lz, 862, 870, 0.4, "hermana", t=tq, risa=risa_h, mira=(-0.7, 0.3 if tq > 3.2 else 0.0), luz=(-12, -8))
        self.mesa.pintar(lz)
        foco = tramo(t, 2.2, 6.2)
        lz.desenfocar(foco * 0.95)
        lz.viñeta(0.5 + 0.35 * foco, cx=W / 2, cy=H / 2 + 200, r0=380, r1=1250)
        parpado = 1.0 if 3.25 < tq < 3.45 else 0.5
        _celular_mano(lz, 640, 1740, 0.9, t)
        alex_perfil(lz, 832, 1330, 0.95, t=tq, parpado=parpado, mira_abajo=1.0, luz=(-10, -6),
                    luz_cara=((0.25, 0.5, 0.85), 0.6))
        lz.viñeta(0.35, r0=500, r1=1300)
        return {"osd": ("PLAY", 1.0 if t < 2.6 and (t < 2.0 or int(t * 4) % 2 == 0) else 0.0),
                "falla": 0.6 * (1 - tramo(t, 0.0, 0.35))}


class P1B(Plano):
    grado = "celular"

    def preparar(self):
        self.fondo = Fondo(mesa_pov, self.ancho, semilla=13, desenfoque=16)

    def dibujar(self, lz, t, tq):
        lz.camara(1.03, 540 + math.sin(t * 0.7) * 6, 960 + math.sin(t * 1.1) * 8)
        self.fondo.pintar(lz)
        lz.viñeta(0.55, r0=300, r1=1200)
        respira = math.sin(t * 1.6) * 9
        jx, jy = temblor(tq, 2.2, 5)
        rot = -0.05 + math.sin(t * 0.8) * 0.012
        gestos = ((0.6, 1.4, 0.0, 0.34), (2.2, 3.0, 0.34, 0.67), (3.9, 4.7, 0.67, 1.0))
        desliza, pulgar = 0.0, 0.0
        for a, b, d0, d1 in gestos:
            if t >= a:
                desliza = d0 + (d1 - d0) * suave(tramo(t, a, b))
            if a - 0.25 <= t <= b + 0.1:
                pulgar = math.sin(math.pi * tramo(t, a - 0.25, b + 0.1))
        nuevo = tramo(t, 5.55, 5.85)
        celular(lz, 540 + jx, 1000 + respira + jy, 1.0, rot=rot, desliza=desliza, nuevo=nuevo)
        manos_celular(lz, 540 + jx, 1000 + respira + jy, 1.0, rot=rot, pulgar=pulgar)
        estres = tramo(t, 3.0, 3.5) * (1 - tramo(t, 4.3, 4.9))
        lz.desenfocar(estres * 0.85)
        subs = []
        a1 = tramo(t, 0.8, 1.0) * (1 - tramo(t, 4.8, 5.0))
        if a1 > 0:
            subs.append((["…y entonces le dije a tu tía que no íbamos a poder ir el domingo."], a1))
        a2 = tramo(t, 5.2, 5.35) * (1 - tramo(t, 7.8, 8.0))
        if a2 > 0:
            subs.append((["¿Alex? ¿Me estás escuchando, mijo?"], a2))
        return {"subtitulos": subs}


class P1C(Plano):
    grado = "cena"

    def preparar(self):
        def fondo(lz):
            lz.camara(1.7, 540, 560)
            pared_comedor(lz)
            lz.resplandor(300, 250, 500, hexa("#ffb060"), 0.35)
        self.fondo = Fondo(fondo, self.ancho, semilla=14, desenfoque=12)

    def dibujar(self, lz, t, tq):
        lz.camara(1.0 + 0.05 * t / self.dur, 540, 980)
        self.fondo.pintar(lz)
        lz.viñeta(0.45, r0=300, r1=1200)
        bloquea = tramo(tq, 0.9, 1.0)
        sube = suave(tramo(tq, 1.0, 1.6))
        baja = suave(tramo(tq, 4.3, 5.3))
        mira = (-0.75 * sube * (1 - baja), 1.0 - 1.2 * sube + 1.1 * baja)
        parpado = 0.55 - 0.35 * sube + 0.3 * baja
        if 3.9 < tq < 4.05:
            parpado = 1.0
        habla = 0.0
        for a, b in ((2.2, 2.42), (2.5, 2.72), (2.95, 3.1), (3.14, 3.28), (3.32, 3.6)):
            if a <= tq <= b:
                habla = math.sin(math.pi * (tq - a) / (b - a)) * 0.8
        boca = "media_sonrisa" if 1.8 <= tq < 4.5 else "neutra"
        luz_cel = 1 - bloquea
        alex_frente(lz, 540, 1070 + (1 - sube) * 30 - baja * 10, 1.45, t=tq, mira=mira, parpado=parpado, boca=boca,
                    habla=habla, cejas=0.15 * sube * (1 - baja) - 0.25 * baja, inclina=0.03 * (1 - sube), luz=(-14, -10),
                    contraluz=(mezcla(PIEL_ALEX, hexa("#9ccff5"), 0.5), (0, 12)) if luz_cel > 0.5 else None)
        if luz_cel > 0:
            lz.resplandor(560, 1980, 760, hexa("#4f9be0"), 0.45 * luz_cel)
        lz.viñeta(0.3, r0=500, r1=1250)
        subs = []
        a = tramo(t, 2.05, 2.2) * (1 - tramo(t, 4.1, 4.3))
        if a > 0:
            subs.append((["Sí, ma. Todo bien."], a))
        return {"subtitulos": subs}


class Negro(Plano):
    grado = "neutro"

    def dibujar(self, lz, t, tq):
        return {}


# --- escena 2: las tres sombras ------------------------------------------------------------------

def _sombras_rincon(lz, t, crece):
    """Sombras de los rincones que se estiran por la pared como dedos."""
    for lado, x0 in ((-1, 122), (1, 958)):
        for k in range(5):
            y0 = 380 + k * 165
            largo = (60 + 300 * crece * (0.6 + 0.4 * math.sin(k * 2.3 + 1))) * (1 + 0.05 * math.sin(t * 1.3 + k))
            pts = []
            for i in range(6):
                u = i / 5
                pts.append((x0 - lado * largo * u, y0 + math.sin(u * 3 + t * 0.8 + k) * 26 * u + u * 60 * crece))
            lz.mancha(dedo(pts, 70 + 40 * crece, 4), (0, 0, 0), 0.72, hervor=0.8)
    for lado in (-1, 1):
        base = (540 + lado * 420, 330)
        largo = 80 + 260 * crece
        pts = [(base[0] - lado * largo * u, base[1] - 40 * u - math.sin(u * 3 + t) * 20 * u) for u in np.linspace(0, 1, 6)]
        lz.mancha(dedo(pts, 90, 4), (0, 0, 0), 0.6, hervor=0.8)


class P2A(Plano):
    grado = "noche"

    def preparar(self):
        self.fondo = Fondo(cuarto_noche, self.ancho, semilla=21)

    def parpadeo(self, t):
        return max(math.sin(math.pi * tramo(t, 2.0, 2.7)) * 0.75, math.sin(math.pi * tramo(t, 5.0, 6.1)) * 0.95)

    def dibujar(self, lz, t, tq):
        lz.camara(1.03 + 0.02 * t / self.dur, 540 + math.sin(t * 0.3) * 6, 960 + math.sin(t * 0.5) * 5)
        self.fondo.pintar(lz)
        ventilador(lz, t * 0.5)
        _sombras_rincon(lz, tq, suave(tramo(t, 0.8, self.dur)))
        cobija(lz, respira=math.sin(t * 1.1))
        lz.viñeta(0.72, r0=320, r1=1150)
        parpados(lz, self.parpadeo(t))
        return {}


FIGURAS = [((250, 1215, 0.6), (150, 1680, 1.4)), ((420, 1238, 0.66), (560, 1760, 1.62)), ((592, 1210, 0.6), (930, 1670, 1.4))]


class P2B(Plano):
    grado = "noche"

    def preparar(self):
        self.fondo = Fondo(cuarto_noche, self.ancho, semilla=21)

    def dibujar(self, lz, t, tq):
        k = suave(tramo(t, 0.5, self.dur))
        lz.camara(1.03 + 0.12 * k, 540 - 110 * k, 960 - 40 * k)
        self.fondo.pintar(lz)
        ventilador(lz, t * 0.5)
        _sombras_rincon(lz, tq, 1.0)
        espesa = tramo(t, 0.2, 2.4)
        lz.resplandor(420, 950, 520, (0, 0, 0), 0.92 * espesa, operador=cairo.OPERATOR_OVER, ry=620)
        aparece = tramo(t, 1.3, 3.8)
        mascaras = tramo(t, 1.0, 2.4)
        for i, ((x, y, s), _) in enumerate(FIGURAS):
            if aparece <= 0 and mascaras <= 0:
                break
            inclina = 0.18 * tramo(t, 5.0, 6.2) if i == 1 else 0.0
            figura(lz, x, y, s, t=tq, semilla=i, alfa=max(aparece, 0.001), mascara_brillo=mascaras * (0.85 + 0.15 * math.sin(t * 3 + i)),
                   inclina=inclina)
            if mascaras > aparece:
                # Las máscaras se ven antes que los cuerpos.
                lz.guardar()
                lz.mover(x, y, s)
                lz.resplandor(0, -890, 120, hexa("#c9d6e6"), 0.25 * (mascaras - aparece))
                lz.restaurar()
        cobija(lz, respira=math.sin(t * 1.6) * 1.4)
        lz.viñeta(0.7, r0=320, r1=1150)
        return {}


class P2C(Plano):
    grado = "noche"

    def dibujar(self, lz, t, tq):
        jx, jy = temblor(tq, 2.5, 7)
        lz.camara(1.0 + 0.03 * t / self.dur, 540 + jx, 960 + jy)
        lz.velo(hexa("#0a0e16"), 1.0)
        miradas = ((0.0, -0.9), (0.45, 0.95), (0.9, -0.5), (1.3, 0.9), (1.75, -0.95), (2.25, 0.2), (2.7, 0.7))
        mira_x = [m for a, m in miradas if tq >= a][-1]
        alex_acostado(lz, 540, 930, 1.55, t=tq, mira=(mira_x, -0.1), parpado=0.0, cejas=0.9, boca="apretada",
                      sudor=0.6)
        lz.mancha(np.array([(-300, 200), (1400, -300), (1400, 500), (-300, 1100)], float), LUNA, 0.06, suave=False)
        lz.viñeta(0.78, r0=300, r1=1100)
        return {}


class P2D(Plano):
    grado = "noche"

    def preparar(self):
        self.fondo = Fondo(cuarto_noche, self.ancho, semilla=21)

    def dibujar(self, lz, t, tq):
        av = suave(tramo(t, 0.4, 6.6))
        lucha = 2 + 12 * av
        jx, jy = temblor(tq, lucha, 9)
        lz.camara(1.15 - 0.05 * av, 430 + jx, 920 + jy)
        self.fondo.pintar(lz)
        ventilador(lz, t * 0.5)
        _sombras_rincon(lz, tq, 1.0)
        lz.resplandor(420, 950, 520, (0, 0, 0), 0.92, operador=cairo.OPERATOR_OVER, ry=620)
        orden = sorted(range(3), key=lambda i: FIGURAS[i][1][2])
        for i in orden:
            (x0, y0, s0), (x1, y1, s1) = FIGURAS[i]
            ai = suave(tramo(t, 0.4 + i * 0.25, 6.6 + i * 0.2))
            figura(lz, x0 + (x1 - x0) * ai, y0 + (y1 - y0) * ai, s0 + (s1 - s0) * ai, t=tq, semilla=i, flota=2.0,
                   brazo=0.6 * ai if i == 1 else 0.0, inclina=0.18 if i == 1 else 0.0)
        cobija(lz, respira=math.sin(t * 3.2) * 1.8)
        lz.viñeta(0.7 + 0.25 * av, r0=280, r1=1100)
        cierre = tramo(t, 5.2, 6.1) * 0.7 - tramo(t, 6.2, 6.6) * 0.35 + tramo(t, 6.7, 7.7) * 0.66
        parpados(lz, cierre)
        return {"falla": 0.25 * av * (tq % 1 < 0.15)}


# --- escena 3: la parálisis ----------------------------------------------------------------------

class P3A(Plano):
    grado = "noche"

    def preparar(self):
        self.fondo = Fondo(techo, self.ancho, semilla=31, margen=420)

    def dibujar(self, lz, t, tq):
        pulso = latido(t, 112)
        jx, jy = temblor(tq, 2.0, 11)
        lz.camara(1.02 + 0.015 * pulso + 0.04 * t / self.dur, 540 + jx, 960 + jy, rot=0.02 * math.sin(t * 0.5))
        self.fondo.pintar(lz)
        ventilador_techo(lz, 540, 640, t * 0.25, s=0.85)
        lz.viñeta(0.55, r0=250, r1=1100)
        mascara_cerca(lz, 150, 1230, 1.9, t=tq, inclina=0.62 + math.sin(tq * 0.9) * 0.04, semilla=1)
        mascara_cerca(lz, 950, 1170, 1.9, t=tq, inclina=-0.55 + math.sin(tq * 0.8 + 1) * 0.04, semilla=2)
        ladeo = 0.5 * suave(tramo(tq, 2.0, 5.2))
        mascara_cerca(lz, 545, 920, 2.45, t=tq, inclina=-0.04 + ladeo, semilla=0)
        lz.viñeta(0.35, r0=500, r1=1250)
        parpados(lz, 1 - tramo(t, 0.0, 0.22) + 0.9 * math.sin(math.pi * tramo(t, 3.3, 3.55)))
        return {"falla": 0.4 * (1 - tramo(t, 0.0, 0.3))}


class P3B(Plano):
    grado = "noche"

    def dibujar(self, lz, t, tq):
        jx, jy = temblor(tq, 6, 13)
        lz.camara(1.0 + 0.06 * t / self.dur, 540, 960)
        lz.velo(hexa("#0a0e16"), 1.0)
        alex_acostado(lz, 540 + jx, 1010 + jy, 1.6, t=tq, boca="abierta", cejas=1.0, parpado=0.0, sudor=1.0,
                      mira=(0.0, -0.4), agitado=1.0)
        mascara_cerca(lz, 560, 110, 2.6, t=tq, inclina=math.pi - 0.2 + math.sin(tq) * 0.05, semilla=0, hombros=True)
        lz.mancha(np.array([(-300, -300), (380, -300), (120, 700), (-300, 900)], float), (0, 0, 0), 0.85)
        lz.mancha(np.array([(1400, -300), (760, -300), (980, 600), (1400, 800)], float), (0, 0, 0), 0.85)
        lz.viñeta(0.8, r0=280, r1=1100)
        return {"falla": 0.15 * (int(tq * 12) % 7 == 0)}


class P3C(Plano):
    grado = "noche"

    def preparar(self):
        self.fondo = Fondo(sabana, self.ancho, semilla=33)

    def dibujar(self, lz, t, tq):
        lz.camara(1.0 + 0.08 * suave(t / self.dur), 470, 1050)
        self.fondo.pintar(lz)
        piel = mezcla(PIEL_ALEX, hexa("#6d7f99"), 0.35)
        antebrazo(lz, -60, 1330, 1.3, ang=-0.36, t=tq, dedos=0.3, piel=piel, manga=None,
                  contraluz=(mezcla(piel, hexa("#c3d8ee"), 0.5), (0, -9)), tiembla=0.6)
        llega = suave(tramo(t, 0.3, 4.3))
        punta = np.array([1180, 120]) + (np.array([430, 1120]) - np.array([1180, 120])) * llega
        punta = punta + (math.sin(tq * 3) * 6, 0)
        extremidad(lz, (1500, -420), punta, t=tq, abre=0.7 - 0.3 * llega)
        lz.viñeta(0.7, r0=300, r1=1100)
        return {"blanco": tramo(t, 4.3, 4.42)}


# --- escena 4: el recuerdo -----------------------------------------------------------------------

class P4A(Plano):
    grado = "recuerdo"

    def preparar(self):
        self.fondo = Fondo(parque, self.ancho, semilla=41)
        rng = np.random.default_rng(42)
        self.semillas = rng.uniform(0, 1, (26, 4))

    def dibujar(self, lz, t, tq):
        lento = tq * 0.42
        lz.camara(1.0 + 0.07 * t / self.dur, 560, 1000)
        self.fondo.pintar(lz)
        # Rayos de sol que giran despacio.
        for k in range(9):
            a = k / 9 * 2 * math.pi + t * 0.05
            pts = np.array([(820, 260), (820 + math.cos(a - 0.05) * 1600, 260 + math.sin(a - 0.05) * 1600),
                            (820 + math.cos(a + 0.05) * 1600, 260 + math.sin(a + 0.05) * 1600)])
            lz.mancha(pts, hexa("#fff4c0"), 0.07, suave=False, hervor=0)
        papa_recuerdo(lz, 400, 1030, 0.5, t=lento)
        mama_recuerdo(lz, 830, 1470, 0.44, t=lento)
        for i, (sx, sy, fase, vel) in enumerate(self.semillas):
            x = (sx * 1300 - 100 + t * (18 + vel * 30)) % 1300 - 100
            y = sy * 1500 + 150 + math.sin(t * 0.8 + fase * 6) * 30
            lz.resplandor(x, y, 16, (1, 1, 1), 0.7, operador=cairo.OPERATOR_OVER)
            for k in range(6):
                a = k / 6 * 2 * math.pi
                lz.linea([(x, y), (x + math.cos(a) * 12, y + math.sin(a) * 12)], 1.2, (1, 1, 1), hervor=0)
        for k in range(2):
            bx = 300 + k * 90 + t * 30
            by = 330 + k * 40 + math.sin(t * 2 + k) * 8
            lz.pincel([(bx - 18, by - 8), (bx, by), (bx + 18, by - 8)], 4, hexa("#2a2a3a"))
        blanco = 1 - tramo(t, 0.0, 1.3)
        return {"blanco": blanco, "fecha": ("JUN. 14 2011", tramo(t, 0.9, 1.4) * (1 - tramo(t, 7.6, 7.9)))}


# --- escena 5: el despertar ----------------------------------------------------------------------

class P5A(Plano):
    """El recuerdo se congela y se rompe como un vidrio hacia la oscuridad."""
    grado = "recuerdo"

    def preparar(self):
        recuerdo = P4A(8, self.ancho)
        lz = Lienzo(self.ancho, semilla=0)
        lz.nuevo(int(8 * 12))
        recuerdo.dibujar(lz, 7.95, 7.95)
        self.congelado = lz.capturar()
        self.impacto = np.array([560.0, 820.0])
        rng = np.random.default_rng(51)
        angulos = np.sort(rng.uniform(0, 2 * math.pi, 15))
        radios = [0, 110, 260, 460, 740, 1150, 2600]
        vert = {}
        for i, a in enumerate(angulos):
            for j, r in enumerate(radios):
                jit = 0 if j == 0 else rng.normal(0, 18 + r * 0.04)
                aa = a + (rng.normal(0, 0.05) if j else 0)
                vert[(i, j)] = self.impacto + np.array([math.cos(aa), math.sin(aa)]) * (r + jit)
        self.trozos = []
        n = len(angulos)
        for i in range(n):
            for j in range(len(radios) - 1):
                poli = np.array([vert[(i, j)], vert[((i + 1) % n, j)], vert[((i + 1) % n, j + 1)], vert[(i, j + 1)]])
                centro = poli.mean(axis=0)
                dirc = centro - self.impacto
                dirc = dirc / (np.linalg.norm(dirc) + 1e-9)
                vel = dirc * rng.uniform(250, 650) + (0, rng.uniform(-300, 50))
                self.trozos.append((poli, centro, vel, rng.uniform(-2.5, 2.5), rng.uniform(0.0, 0.25)))
        self.grietas = [(vert[(i, 0)], [vert[(i, j)] for j in range(1, len(radios))]) for i in range(n)]

    def dibujar(self, lz, t, tq):
        c = lz.ctx
        rompe = 0.9
        lz.pantalla()
        if t < rompe:
            lz.pintar_superficie(self.congelado, 0, 0, 1.0)
            crece = tramo(t, 0.05, 0.75)
            for _, puntos in self.grietas:
                camino = [self.impacto] + puntos
                total = max(1, int(round(crece * len(camino))))
                if total >= 2:
                    lz.linea(camino[:total], 3, (1, 1, 1), suave=False, alfa=0.85)
                    lz.linea(camino[:total], 7, (0, 0, 0), suave=False, alfa=0.35)
            lz.resplandor(*self.impacto, 140, (1, 1, 1), 0.6 * (1 - tramo(t, 0.0, 0.3)))
            return {"falla": 0.2}
        dt = t - rompe
        for poli, centro, vel, giro, retraso in self.trozos:
            d = max(dt - retraso * 0.3, 0)
            mueve = vel * d + np.array([0, 1500]) * d * d
            alfa = 1 - tramo(dt, 0.9, 1.9)
            if alfa <= 0:
                continue
            c.save()
            lz.pantalla()
            c.translate(centro[0] + mueve[0], centro[1] + mueve[1])
            c.rotate(giro * d)
            c.translate(-centro[0], -centro[1])
            c.new_path()
            c.move_to(*poli[0])
            for p in poli[1:]:
                c.line_to(*p)
            c.close_path()
            camino = c.copy_path()
            c.save()
            c.clip()
            c.scale(1 / lz.esc, 1 / lz.esc)
            c.set_source_surface(self.congelado, 0, 0)
            c.paint_with_alpha(alfa)
            c.restore()
            c.append_path(camino)
            c.set_line_width(2.5)
            c.set_source_rgba(1, 1, 1, 0.6 * alfa)
            c.stroke()
            c.restore()
        return {"falla": 0.8 * (1 - tramo(dt, 0.0, 0.5)), "grado": "noche" if dt > 1.2 else "recuerdo"}


class P5B(Plano):
    grado = "noche"
    PASOS = (0.0, 0.0, 0.28, 0.28, 0.28, 0.75, 0.75, 1.15, 1.15, 1.15, 1.6, 1.6)

    def dibujar(self, lz, t, tq):
        lz.camara()
        lz.velo((0.0, 0.0, 0.0), 1.0)
        ang = self.PASOS[min(int(t * 12), len(self.PASOS) - 1)]
        jx, jy = temblor(tq, 10, 17)
        mascara_cerca(lz, 540 + jx, 860 + jy, 3.2, t=tq, inclina=ang, semilla=0)
        lz.viñeta(0.8, r0=280, r1=1000)
        cuadro = int(t * FPS)
        return {"negativo": cuadro in (3, 4, 15), "falla": 0.55}


class P5C(Plano):
    grado = "noche"

    def preparar(self):
        self.fondo = Fondo(techo, self.ancho, semilla=31, margen=520)

    def dibujar(self, lz, t, tq):
        ang = t * 6.5 + t * t * 5
        for k, alfa in enumerate((1.0, 0.5, 0.3)):
            lz.grupo()
            lz.camara(1.25, 540, 960, rot=ang - k * 0.09)
            self.fondo.pintar(lz)
            ventilador_techo(lz, 540, 900, ang * 2.2, s=1.0)
            mascara_cerca(lz, 540, 300, 2.2, t=tq, inclina=math.pi, semilla=0, mascara_brillo=0.7)
            lz.soltar(alfa)
        lz.viñeta(0.8, r0=250, r1=1000)
        return {"falla": 0.5}


class P5D(Plano):
    grado = "noche"

    def preparar(self):
        self.fondo = Fondo(sabana, self.ancho, semilla=34)

    def dibujar(self, lz, t, tq):
        golpe = tramo(t, 0.3, 0.5)
        jx, jy = temblor(tq, 4 + 10 * golpe * (1 - tramo(t, 0.5, 0.9)), 19)
        lz.camara(1.0, 540 + jx, 960 + jy)
        self.fondo.pintar(lz)
        piel = mezcla(PIEL_ALEX, hexa("#6d7f99"), 0.35)
        a = -0.25
        s = 2.1
        ox, oy = 600 - s * 620 * math.cos(a), 1030 - s * 620 * math.sin(a)
        antebrazo(lz, ox, oy, s, ang=a, t=tq, puno=golpe, dedos=0.2, piel=piel, manga=None,
                  contraluz=(mezcla(piel, hexa("#c3d8ee"), 0.5), (0, -9)))
        se_va = suave(tramo(t, 0.05, 0.85))
        punta = np.array([760, 820]) + (np.array([1400, -500]) - np.array([760, 820])) * se_va
        extremidad(lz, (1600, -700), punta, t=tq, abre=0.8, grosor=1.3)
        lz.viñeta(0.7, r0=300, r1=1100)
        return {"falla": 0.4 * golpe * (1 - tramo(t, 0.5, 0.8))}


class P5E(Plano):
    grado = "noche"

    def preparar(self):
        self.fondo = Fondo(cuarto_lado, self.ancho, semilla=35)

    def dibujar(self, lz, t, tq):
        sube = suave(tramo(t, 0.15, 0.5))
        rebote = math.sin(tramo(t, 0.5, 0.9) * math.pi) * 40
        sacude = 16 * math.exp(-max(t - 0.45, 0) * 2.2) * (t > 0.4)
        jx, jy = temblor(tq, sacude, 23)
        lz.camara(1.0, 540 + jx, 960 + jy)
        self.fondo.pintar(lz)
        y = 2000 - 1180 * sube + rebote
        alex_incorporado(lz, 560, y, 1.2, t=tq, jadeo=1.0 - 0.4 * tramo(t, 2.5, 4.0), sudor=1.0)
        lz.viñeta(0.65, r0=300, r1=1100)
        return {"falla": 0.5 * tramo(t, 0.3, 0.4) * (1 - tramo(t, 0.45, 0.7))}


class P5F(Plano):
    grado = "noche"

    def preparar(self):
        self.fondo = Fondo(cuarto_noche, self.ancho, semilla=21)
        self.polvo = np.random.default_rng(56).uniform(0, 1, (30, 3))

    def dibujar(self, lz, t, tq):
        k = suave(t / self.dur)
        lz.camara(1.03 + 0.2 * k, 540 - 190 * k, 960 - 60 * k)
        self.fondo.pintar(lz)
        ventilador(lz, t * 0.4)
        for px, py, fase in self.polvo:
            x = 420 + px * 420 + math.sin(t * 0.3 + fase * 6) * 30
            y = 860 + py * 800 - t * 12 * (0.5 + fase)
            lz.resplandor(x, y, 6, LUNA, 0.5 * (0.5 + 0.5 * math.sin(t * 2 + fase * 9)))
        cobija(lz, respira=math.sin(t * 1.4) * 1.2)
        lz.viñeta(0.72, r0=320, r1=1150)
        return {}


# --- escena 6: la incisión -----------------------------------------------------------------------

def _pared_dia(zoom, cy):
    def dibujar(lz):
        lz.camara(zoom, 540, cy)
        pared_comedor(lz, dia=True)
    return dibujar


class P6A(Plano):
    grado = "manana"

    def preparar(self):
        self.fondo = Fondo(_pared_dia(1.45, 600), self.ancho, semilla=61, desenfoque=3)
        self.mesa = Fondo(mesa_frente, self.ancho, semilla=62, transparente=True)

    def dibujar(self, lz, t, tq):
        k = suave(t / self.dur)
        lz.camara(1.0 + 0.1 * k, 540, 1000 + 40 * k)
        self.fondo.pintar(lz)
        lz.mancha(np.array([(-300, -200), (500, -200), (1200, 1400), (300, 1400)], float), (1, 0.98, 0.9), 0.1,
                  suave=False, hervor=0)
        silla(lz, 150, 1240, 0.95)
        silla(lz, 930, 1240, 0.95)
        parpado = 1.0 if 5.2 < tq < 5.4 else 0.42
        alex_frente(lz, 540, 890, 1.02, t=tq, mira=(0.05, 0.2), parpado=parpado, boca="neutra", palidez=0.85,
                    luz=(-16, -4))
        self.mesa.pintar(lz)
        piel = mezcla(PIEL_ALEX, hexa("#a39a8e"), 0.45)
        brazo(lz, (315, 1210), (380, 1500), 230, 230, SUDADERA, piel, grosor=92, doblez=1)
        brazo(lz, (765, 1210), (700, 1490), 230, 230, SUDADERA, piel, grosor=92, doblez=-1)
        tenedor(lz, 880, 1700, 0.85, ang=0.05)
        lz.viñeta(0.4, r0=450, r1=1250)
        return {}


class P6B(Plano):
    grado = "manana"

    def preparar(self):
        self.fondo = Fondo(_pared_dia(2.2, 520), self.ancho, semilla=63, desenfoque=12)

    def dibujar(self, lz, t, tq):
        lz.camara(1.0 + 0.06 * t / self.dur, 540, 960)
        self.fondo.pintar(lz)
        punzada = math.sin(math.pi * tramo(tq, 0.8, 1.3))
        baja = suave(tramo(tq, 1.5, 2.6))
        mira = (0.75 * baja, 0.25 + 0.85 * baja)
        parpado = 0.42 + 0.35 * punzada + 0.08 * baja
        alex_frente(lz, 540, 1010 + 20 * baja, 1.85, t=tq, mira=mira, parpado=parpado,
                    boca="apretada" if punzada > 0.2 else "neutra", cejas=-0.7 * punzada + 0.25 * baja, palidez=0.9,
                    inclina=0.05 * baja, luz=(-16, -6))
        lz.viñeta(0.45, r0=400, r1=1200)
        return {}


class P6C(Plano):
    grado = "manana"

    def preparar(self):
        self.fondo = Fondo(mesa_cerca, self.ancho, semilla=64, desenfoque=14)

    def dibujar(self, lz, t, tq):
        acerca = suave(tramo(t, 1.6, self.dur))
        pulso = latido(t, 96) * tramo(t, 1.5, 2.0)
        lz.camara(1.0 + 0.25 * acerca + 0.01 * pulso, 540 - 20 * acerca, 950 - 20 * acerca)
        self.fondo.pintar(lz)
        sube = suave(tramo(t, 0.1, 1.3))
        a = -0.5
        s = 1.35
        ox = 520 - s * 275 * math.cos(a)
        oy = 920 - s * 275 * math.sin(a) + 760 * (1 - sube)
        piel = mezcla(PIEL_ALEX, hexa("#a39a8e"), 0.45)
        antebrazo(lz, ox, oy, s, ang=a + 0.25 * (1 - sube), t=tq, herida=1.0, vista=0.35 + 0.65 * sube, dedos=0.5,
                  piel=piel, tiembla=tramo(t, 1.4, 2.0), luz=(0, -12))
        lz.viñeta(0.5, r0=380, r1=1200)
        return {"negro": tramo(t, self.dur - 0.12, self.dur - 0.04)}


class Titulo(Plano):
    grado = "neutro"

    def dibujar(self, lz, t, tq):
        lz.camara()
        lz.velo((0, 0, 0), 1.0)
        aparece = tramo(t, 0.35, 0.8)
        cose = tramo(t, 0.7, 1.9)
        if cose > 0:
            x0, x1, y = 250, 830, 1045
            xf = x0 + (x1 - x0) * cose
            lz.pincel([(x0, y), ((x0 + xf) / 2, y + 4), (xf, y)], 7, hexa("#8e1a22"))
            n = int(12 * cose)
            for i in range(n):
                px = x0 + 25 + i * 48
                lz.pincel([(px - 8, y - 20), (px + 8, y + 20)], 4.5, hexa("#d8d2c4"))
        return {"titulo": aparece * (1 - tramo(t, 3.45, 3.95)), "falla": 0.5 * (tramo(t, 0.3, 0.4) * (1 - tramo(t, 0.5, 0.7)))
                + 0.4 * (3.1 < t < 3.25), "negro": tramo(t, 3.5, 3.95)}


PLANOS = {
    "Gancho": Gancho, "1A": P1A, "1B": P1B, "1C": P1C, "Negro": Negro, "2A": P2A, "2B": P2B, "2C": P2C, "2D": P2D,
    "3A": P3A, "3B": P3B, "3C": P3C, "4A": P4A, "5A": P5A, "5B": P5B, "5C": P5C, "5D": P5D, "5E": P5E, "5F": P5F,
    "6A": P6A, "6B": P6B, "6C": P6C, "Título": Titulo,
}
GANCHO = 1.5
