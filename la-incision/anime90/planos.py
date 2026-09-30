"""Los 22 planos de La Incisión, con las convenciones del anime de los 90.

Cada plano tiene un fondo pintado (que se mueve con la cámara: panorámica, acercamiento, giro) y uno o
dos acetatos encima que se redibujan a pocos dibujos por segundo (animación limitada: 12, 8 o menos).
La cámara sí corre a 24 cuadros. Los sustos son cortes y cuadros sostenidos, no movimiento fluido.
"""

import math

import numpy as np
from PIL import Image, ImageFilter
from scipy.spatial import cKDTree

from . import fondos
from . import personajes as P
from .cel import Hoja, componer, elipse, hexa, mezcla, suave, tramo, curva

AN, AL = 720, 1280
W, H = 1080, 1920


def _pil(arr):
    return Image.fromarray((np.clip(arr, 0, 1) * 255 + 0.5).astype(np.uint8))


def _arr(im):
    return np.asarray(im, np.float32) / 255


def vista(im, cx, cy, ancho, rot=0.0):
    """Ventana vertical de la imagen grande, centrada en (cx, cy), de `ancho` de fondo y girada `rot` radianes."""
    s = ancho / AN
    a, b = s * math.cos(rot), -s * math.sin(rot)
    d, e = s * math.sin(rot), s * math.cos(rot)
    c = cx - a * AN / 2 - b * AL / 2
    f = cy - d * AN / 2 - e * AL / 2
    return _arr(im.transform((AN, AL), Image.AFFINE, (a, b, c, d, e, f), resample=Image.BICUBIC))


def lerp(a, b, t):
    return a + (b - a) * t


def pantalla():
    """Acetato del tamaño del cuadro para cosas que no se mueven con el fondo (párpados, líneas)."""
    return Hoja(W, H, AN / W)


def poner(img, h):
    return componer(img, h.rgba())


def sacudida(t, fuerza, semilla=0, cada=1 / 24):
    rng = np.random.default_rng((semilla, int(t / cada)))
    return rng.normal(0, fuerza), rng.normal(0, fuerza)


def cierre_de_parpados(t, parpadeos, base=0.0, dur=0.22, maximo=1.0):
    """0 = ojos abiertos, 1 = cerrados. `parpadeos` son los segundos en que empieza cada parpadeo."""
    c = base
    for t0 in parpadeos:
        if t0 <= t <= t0 + dur:
            c = max(c, math.sin(math.pi * (t - t0) / dur) * maximo)
    return c


def parpados(h, c):
    """Los párpados de Alex cerrándose sobre la vista: dos cortinas negras con borde curvo."""
    if c <= 0.005:
        return
    ye = c * H * 0.52
    ab = 0.16 * H * min(c * 1.5, 1)
    top = [(-40, -40), (W + 40, -40), (W + 40, ye), (W * 0.8, ye + ab * 0.55), (W * 0.5, ye + ab), (W * 0.2, ye + ab * 0.55), (-40, ye)]
    bot = [(-40, H + 40), (W + 40, H + 40), (W + 40, H - ye), (W * 0.8, H - ye - ab * 0.55), (W * 0.5, H - ye - ab),
           (W * 0.2, H - ye - ab * 0.55), (-40, H - ye)]
    for k, alfa in ((14, 0.28), (7, 0.4), (0, 1.0)):
        for pts in (top, bot):
            mov = [(x, y + (k if pts is top else -k)) for x, y in pts]
            h.forma(mov, (0.0, 0.0, 0.0), alfa=alfa)


def lineas_de_velocidad(h, centro, n, semilla, r0=170, largo=900, color=(0.02, 0.02, 0.03), ancho=13):
    rng = np.random.default_rng(semilla)
    for _ in range(n):
        a = rng.uniform(0, 2 * math.pi)
        r_in = r0 * rng.uniform(1.0, 2.2)
        r_out = r_in + largo * rng.uniform(0.3, 1.0)
        h.tinta([(centro[0] + math.cos(a) * r_in, centro[1] + math.sin(a) * r_in),
                 (centro[0] + math.cos(a) * r_out, centro[1] + math.sin(a) * r_out)],
                ancho * rng.uniform(0.5, 1.3), color, afila=(0.0, 0.0), alfa=0.9)


class Plano:
    paleta = "noche"
    dib = 12          # dibujos por segundo del acetato
    grano = 0.045
    halo = 0.55

    def __init__(self, dur):
        self.dur = dur
        self._tq = None
        self._im = None
        self.preparar()

    def preparar(self):
        pass

    def tq(self, t):
        return math.floor(t * self.dib + 1e-6) / self.dib

    def compuesto(self, tq, fondo, atras, delante=None, mesa_y=None):
        """Fondo + acetato, guardado mientras el dibujo no cambie (así se sostienen los cuadros)."""
        if tq != self._tq:
            base = fondo
            if atras is not None:
                h = Hoja(k=1.0)
                atras(h, tq)
                base = componer(fondo, h.rgba())
            if mesa_y is not None:
                base = base.copy()
                base[mesa_y:] = fondo[mesa_y:]
            if delante is not None:
                h = Hoja(k=1.0)
                delante(h, tq)
                base = componer(base, h.rgba())
            self._im = _pil(base)
            self._tq = tq
        return self._im

    def cuadro(self, t):
        raise NotImplementedError


def _desenfocar(arr, radio):
    return _arr(_pil(arr).filter(ImageFilter.GaussianBlur(radio)))


# =========================================================================================================
# ESCENA 1 · el comedor

class P1A(Plano):
    """La cena: la familia platica; la cámara se acerca despacio a Alex, que mira su celular bajo la mesa."""
    paleta = "cena"

    def preparar(self):
        self.fondo = fondos.comedor()

    def atras(self, h, tq):
        rng = np.random.default_rng(int(tq * 12) + 7)
        for i, (x, quien, flip) in enumerate(((150, "padre", False), (430, "madre", True), (700, "hermana", False))):
            habla = ((int(tq * 12) // 3 + i) % 3) != 0
            bob = 3 * math.sin(tq * 2.1 + i * 2)
            P.busto(h, x, 860 + bob, 0.62, quien, "cena", flip=flip, largo=760)
            P.cabeza(h, x, 860 + bob, 0.62, quien=quien, tono="cena", flip=flip, ap=0.9,
                     boca="abierta" if habla else "neutra", abre=rng.uniform(0.2, 0.9), ceja=rng.uniform(-0.2, 0.5),
                     ojera=0.2, arrugas=0.7 if quien != "hermana" else 0.0)

    def delante(self, h, tq):
        parp = cierre_de_parpados(tq, (1.5, 4.6, 6.9), dur=0.17)
        res = 0.5 * (math.sin(tq * 1.7) * 0.5 + 0.5)
        P.busto(h, 900, 1240 + 3 * math.sin(tq * 1.9), 0.92, "alex", "cena", flip=False, largo=900)
        P.cabeza(h, 900, 1240 + 3 * math.sin(tq * 1.9), 0.92, quien="alex", tono="cena", rot=0.16, ap=0.5 * (1 - parp),
                 mirada=(0.25, 1.0), ceja=-0.1, boca="cansada", ojera=1.0)
        # el brillo azul del celular sobre su cara
        h.resplandor(820, 1360, 220, (0.55, 0.78, 1.0), 0.32 + 0.1 * res, ry=130)

    def cuadro(self, t):
        e = suave(t / self.dur)
        im = self.compuesto(self.tq(t), self.fondo, self.atras, self.delante, mesa_y=1240)
        return vista(im, lerp(540, 830, e), lerp(960, 1180, e), lerp(1080, 640, e)), {}


def _dedo(h, x0, y0, x1, y1, ancho, piel, sombra):
    ruta = [(x0, y0), ((x0 + x1) / 2 + 6, (y0 + y1) / 2 + 4), (x1, y1)]
    h.tinta(ruta, ancho, hexa("#2a160f"), afila=(0.0, 0.0))
    h.tinta(ruta, ancho - 8, piel, afila=(0.0, 0.0))
    h.tinta([(x + 2, y + ancho * 0.2) for x, y in ruta], ancho * 0.28, sombra, afila=(0.1, 0.2), alfa=0.85)
    h.forma(elipse(x1, y1, ancho * 0.36, ancho * 0.42), piel)


CHAT = [
    ("ella", "Todo está bien"),
    ("el", "ok"),
    ("ella", "no es ok, Alex"),
    ("ella", "siempre es lo mismo"),
    ("el", "no empieces otra vez"),
    ("ella", "¿otra vez? llevas semanas ausente"),
    ("el", "estoy cenando con mi familia"),
    ("ella", "ni siquiera estás ahí"),
    ("ella", "ya no sé qué estamos haciendo"),
    ("ella", "escríbeme cuando decidas quedarte"),
]


class P1B(Plano):
    """POV del celular: el chat empieza en «Todo está bien» y baja hasta la discusión. Las letras se desenfocan."""
    paleta = "cena"
    dib = 8

    def preparar(self):
        self.fondo = _desenfocar(fondos.comedor(), 22) * 0.75

    def atras(self, h, tq):
        cx, cy, s = 540, 1130, 2.05
        P.celular(h, cx, cy, s, tono="cena")
        # el chat: se dibuja encima con recorte a la pantalla y un desplazamiento
        scroll = suave(tq / self.dur * 1.05) * 1180
        h.guarda()
        h.cr.rectangle(cx - 132 * s, cy - 200 * s, 264 * s, 446 * s)
        h.cr.clip()
        h.rect(cx - 132 * s, cy - 252 * s, cx + 132 * s, cy + 246 * s, hexa("#e6dfd2"))
        y = cy - 200 * s + 40 - scroll
        cr = h.cr
        cr.select_font_face("DejaVu Sans")
        cr.set_font_size(34)
        max_w = 420
        for lado, txt in CHAT:
            lineas, actual = [], ""
            for palabra in txt.split():
                prueba = (actual + " " + palabra).strip()
                if cr.text_extents(prueba).x_advance > max_w and actual:
                    lineas.append(actual)
                    actual = palabra
                else:
                    actual = prueba
            lineas.append(actual)
            ancho = max(cr.text_extents(ln).x_advance for ln in lineas) + 44
            alto = 30 + 46 * len(lineas)
            col = hexa("#ffffff") if lado == "ella" else hexa("#bfeaa8")
            bx = cx - 122 * s if lado == "ella" else cx + 122 * s - ancho
            h.forma([(bx, y), (bx + ancho, y), (bx + ancho, y + alto), (bx, y + alto)], col, suave_=False)
            for k, ln in enumerate(lineas):
                h.texto(bx + 22, y + 48 + 46 * k, ln, 34, hexa("#1c2420"))
            y += alto + 40
        h.restaura()
        h.rect(cx - 132 * s, cy - 252 * s, cx + 132 * s, cy - 196 * s, hexa("#2f7a63"))
        h.texto(cx - 90 * s, cy - 212 * s, "Mariana ♥", 36, (1, 1, 1), negrita=True)
        # las manos que sostienen el celular: salen de abajo, con la palma detrás y los dedos sobre el borde
        piel, sombra = P.teñir(hexa("#b48560"), "cena"), P.teñir(hexa("#8a5f42"), "cena")
        linea = P.teñir(P.TINTA, "cena")
        borde = 150 * s
        for lado in (-1, 1):
            ex = cx + lado * borde
            palma = [(ex + lado * 230, 1230), (ex + lado * 40, 1210), (ex - lado * 6, 1500), (ex + lado * 40, 1780),
                     (ex + lado * 200, 1920), (ex + lado * 420, 1920), (ex + lado * 330, 1500)]
            h.cel(palma, piel, sombra, luz=(-lado, -0.5), prof=34, linea=linea, grosor=5)
            for k in range(4):
                y0 = 1290 + k * 88
                ruta = [(ex + lado * 80, y0), (ex - lado * 40, y0 + 4), (ex - lado * 112, y0 + 16)]
                h.tinta(ruta, 60, linea, afila=(0.0, 0.0))
                h.tinta(ruta, 50, piel, afila=(0.0, 0.0))
                h.forma(elipse(ruta[-1][0], ruta[-1][1], 25, 30), piel)
                h.tinta([(x, y + 12) for x, y in ruta[:2]], 10, sombra, afila=(0.1, 0.2), alfa=0.85)
            # pulgar al frente, sobre la pantalla
            ruta = [(ex + lado * 130, 1690), (ex - lado * 60, 1600), (ex - lado * 190, 1520)]
            h.tinta(ruta, 78, linea, afila=(0.0, 0.1))
            h.tinta(ruta, 66, piel, afila=(0.0, 0.1))
            h.forma(elipse(ruta[-1][0], ruta[-1][1], 33, 38), piel)

    def cuadro(self, t):
        e = suave(t / self.dur)
        im = self.compuesto(self.tq(t), self.fondo, self.atras)
        img = vista(im, 540, lerp(1040, 1000, e), lerp(1080, 980, e))
        # las letras se desenfocan por el estrés
        r = 2.4 * tramo(t, 3.0, 7.0)
        if r > 0.05:
            img = _desenfocar(img, r)
        return img, {}


class P1C(Plano):
    """Alex bloquea el celular y levanta la vista con una sonrisa forzada: «Sí, ma. Todo bien.»"""
    paleta = "cena"
    SILABAS = ((2.2, 2.42), (2.5, 2.72), (2.95, 3.1), (3.14, 3.28), (3.32, 3.6))

    def preparar(self):
        self.fondo = _desenfocar(fondos.comedor(), 14)

    def _habla(self, t):
        for a, b in self.SILABAS:
            if a <= t <= b:
                return math.sin(math.pi * (t - a) / (b - a))
        return 0.0

    def atras(self, h, tq):
        sube = suave(tramo(tq, 0.9, 1.25))
        parp = cierre_de_parpados(tq, (2.0, 4.9), dur=0.17)
        habla = self._habla(tq)
        if tq < 1.6:
            boca, abre = "cansada", 0
        elif habla > 0.05:
            boca, abre = "abierta", 0.15 + 0.35 * habla
        else:
            boca, abre = "sonrisa", 0
        if tq > 5.3:
            boca = "cansada"
        sudor = 0.5 * tramo(tq, 3.6, 5.5)
        y = 1000 + 2 * math.sin(tq * 2)
        P.busto(h, 560, y, 2.0, "alex", "cena", largo=700)
        P.cabeza(h, 560, y, 2.0, quien="alex", tono="cena", rot=lerp(0.2, 0.0, sube), ap=lerp(0.5, 0.78, sube) * (1 - parp),
                 mirada=(lerp(0.25, -0.55, sube), lerp(1.0, 0.05, sube)), ceja=0.0 if tq < 1.6 else 0.25, boca=boca,
                 abre=abre, ojera=1.0, sudor=sudor)
        if tq < 1.0:
            h.resplandor(430, 1250, 300, (0.55, 0.78, 1.0), 0.35, ry=180)

    def cuadro(self, t):
        e = suave(t / self.dur)
        im = self.compuesto(self.tq(t), self.fondo, self.atras)
        img = vista(im, lerp(600, 560, e), lerp(960, 930, e), lerp(760, 640, e))
        ef = {}
        if 0.9 <= t < 1.02:
            ef["blanco"] = 0.35
        return img, ef


class Negro(Plano):
    """Corte directo a la oscuridad."""

    def cuadro(self, t):
        return np.zeros((AL, AN, 3), np.float32), {"sin_acabado": True}


# =========================================================================================================
# ESCENA 2 · el cuarto

def _sombras_que_se_estiran(h, tq, fuerza):
    """Manchas oscuras que salen de las esquinas y se estiran de forma poco natural."""
    rng = np.random.default_rng(5)
    for esq, (bx, by, dx, dy) in enumerate(((0, 0, 1, 1), (W, 0, -1, 1), (0, 1250, 1, -0.6), (W, 1250, -1, -0.6))):
        for k in range(3):
            fase = tq * (0.7 + 0.2 * k) + esq * 1.7 + k
            largo = (300 + 200 * math.sin(fase) + 140 * k) * fuerza
            ancho = (46 + 16 * math.sin(fase * 1.3 + k)) * fuerza
            pts = [(bx, by), (bx + dx * largo * 0.5 + rng.normal(0, 10), by + dy * ancho * 3),
                   (bx + dx * largo, by + dy * largo * 0.9)]
            h.tinta(pts, ancho, hexa("#020409"), afila=(0.02, 0.9), alfa=0.9)


class P2A(Plano):
    """POV desde la cama: el cuarto a oscuras, las sombras de los rincones que se estiran, los párpados pesados."""
    paleta = "noche"
    dib = 8

    def preparar(self):
        self.fondo = fondos.cuarto()

    def atras(self, h, tq):
        _sombras_que_se_estiran(h, tq, 0.6 + 0.6 * tq / self.dur)

    def cuadro(self, t):
        e = suave(t / self.dur)
        im = self.compuesto(self.tq(t), self.fondo, self.atras)
        img = vista(im, lerp(540, 620, e), lerp(1000, 900, e), lerp(1080, 860, e))
        h = pantalla()
        parpados(h, cierre_de_parpados(t, (1.4, 3.3, 5.0, 6.6), base=0.1, dur=0.9, maximo=0.55))
        return poner(img, h), {}


class P2B(Plano):
    """Tres sombras altas con máscara blanca aparecen de pie en la habitación y lo miran en silencio."""
    paleta = "noche"
    dib = 8
    APARECEN = (2.2, 3.6, 4.9)

    def preparar(self):
        self.fondo = fondos.cuarto()

    def atras(self, h, tq):
        _sombras_que_se_estiran(h, tq, 0.7)
        for i, (x, y) in enumerate(((560, 560), (270, 590), (880, 580))):
            if tq >= self.APARECEN[i]:
                P.figura(h, x, y, 0.42, "noche", ladea=0.1 * math.sin(tq * 0.8 + i), ancho=1.0)

    def cuadro(self, t):
        e = suave(t / self.dur)
        im = self.compuesto(self.tq(t), self.fondo, self.atras)
        img = vista(im, lerp(540, 560, e), lerp(980, 900, e), lerp(1080, 880, e))
        h = pantalla()
        parpados(h, cierre_de_parpados(t, (1.0, 3.0, 5.4), base=0.18 + 0.2 * e, dur=0.7, maximo=0.5))
        ef = {}
        if any(a <= t < a + 1 / 12 for a in self.APARECEN):
            ef["negativo"] = True
        return poner(img, h), ef


class P2C(Plano):
    """Primer plano de Alex: el cuerpo no responde; solo los ojos se mueven."""
    paleta = "noche"
    dib = 8

    def preparar(self):
        self.fondo = _desenfocar(fondos.cuarto(), 16) * 0.7

    def atras(self, h, tq):
        h.forma([(60, 1180), (1020, 1120), (1060, 1700), (20, 1720)], hexa("#4a5b7a"))
        h.forma([(60, 1180), (1020, 1120), (1030, 1210), (40, 1260)], hexa("#6a7ea0"))
        rng = np.random.default_rng(int(tq * 8))
        mx = -0.8 if tq < 1.0 else (0.7 if tq < 1.9 else -0.2)
        P.busto(h, 540, 900, 2.6, "alex", "noche", largo=700, capucha=False)
        P.cabeza(h, 540 + rng.normal(0, 1.5), 900, 2.6, quien="alex", tono="noche", rot=-0.22, ap=1.2, pupila=0.42,
                 mirada=(mx, 0.0), ceja=0.9, ceja_in=0.6, boca="neutra", ojera=1.0, sudor=0.6)

    def cuadro(self, t):
        jx, jy = sacudida(t, 3.0, 2)
        im = self.compuesto(self.tq(t), self.fondo, self.atras)
        return vista(im, 480 + jx, 850 + jy, lerp(760, 620, suave(t / self.dur))), {}


class P2D(Plano):
    """Las figuras se deslizan hacia él en cortes cada vez más cerca. Sus ojos se cierran."""
    paleta = "noche"
    dib = 8
    ETAPAS = ((0.0, 0.44, 250), (1.5, 0.58, 300), (2.9, 0.8, 340), (4.2, 1.1, 380), (5.4, 1.5, 430))

    def preparar(self):
        self.fondo = fondos.cuarto()

    def etapa(self, tq):
        for i in range(len(self.ETAPAS) - 1, -1, -1):
            if tq >= self.ETAPAS[i][0]:
                return self.ETAPAS[i]
        return self.ETAPAS[0]

    def atras(self, h, tq):
        _, s, spread = self.etapa(tq)
        cy = min(540 + (s - 0.44) * 400, 800)
        rng = np.random.default_rng(int(tq * 8))
        for i, dx in enumerate((-1, 0, 1)):
            x = 540 + dx * spread + rng.normal(0, 4 + 6 * s)
            y = cy + (40 if dx == 0 else 0)
            P.figura(h, x, y, s, "noche", ladea=rng.uniform(-0.25, 0.25), ancho=1.0)

    def cuadro(self, t):
        tq = self.tq(t)
        e = suave(t / self.dur)
        im = self.compuesto(tq, self.fondo, self.atras)
        jx, jy = sacudida(t, 1.5 + 8 * e, 4)
        img = vista(im, 540 + jx, 950 + jy, lerp(1080, 900, e))
        h = pantalla()
        if t > 5.3:
            lineas_de_velocidad(h, (540, 640), 26, int(tq * 8), r0=220, ancho=15)
        parpados(h, cierre_de_parpados(t, (1.2, 3.3), dur=0.6, maximo=0.5, base=0.15 + 0.85 * suave(tramo(t, 5.8, 7.7))))
        return poner(img, h), {"negro": tramo(t, 7.6, 8.0)}


# =========================================================================================================
# ESCENA 3 · la parálisis

class P3A(Plano):
    """POV al techo: las tres máscaras flotan a centímetros de su rostro."""
    paleta = "noche"
    dib = 8

    def preparar(self):
        self.fondo = fondos.techo()

    def atras(self, h, tq):
        for i, (x, y, ang) in enumerate(((540, 640, 0.0), (210, 980, 0.3), (860, 940, -0.3))):
            bob = 14 * math.sin(tq * 0.9 + i * 2.1)
            P.mascara_cerca(h, x, y + bob, 0.46, "noche", ladea=ang + 0.14 * math.sin(tq * 0.7 + i))

    def cuadro(self, t):
        e = suave(t / self.dur)
        im = self.compuesto(self.tq(t), self.fondo, self.atras)
        jx, jy = sacudida(t, 1.2, 6)
        return vista(im, 540 + jx, lerp(800, 780, e) + jy, lerp(1080, 880, e)), {"blanco": 0.85 * (1 - tramo(t, 0.0, 0.25))}


class P3B(Plano):
    """El grito sin voz."""
    paleta = "noche"
    dib = 12

    def preparar(self):
        self.fondo = _desenfocar(fondos.techo(), 10) * 0.8

    def atras(self, h, tq):
        rng = np.random.default_rng(int(tq * 12) + 3)
        x = 540 + rng.normal(0, 3)
        P.busto(h, x, 900, 2.5, "alex", "noche", largo=700, capucha=False)
        P.cabeza(h, x, 900, 2.5, quien="alex", tono="noche", rot=-0.12 + rng.normal(0, 0.01), ap=1.3, pupila=0.4,
                 ceja=1.0, ceja_in=0.8, boca="grito", abre=0.6 + 0.35 * math.sin(tq * 6) ** 2, ojera=1.0, sudor=1.0,
                 palidez=0.1)
        # tendones del cuello tensos
        for dx in (-30, 30):
            h.tinta([(x + dx * 2.5, 1160), (x + dx * 3.1, 1320)], 12, hexa("#1a2440"), afila=(0.1, 0.3), alfa=0.8)

    def cuadro(self, t):
        tq = self.tq(t)
        jx, jy = sacudida(t, 4.5, 8)
        im = self.compuesto(tq, self.fondo, self.atras)
        img = vista(im, 540 + jx, 900 + jy, lerp(900, 700, suave(t / self.dur)))
        h = pantalla()
        if t > 0.6:
            lineas_de_velocidad(h, (540, 640), 20, int(tq * 12), r0=330, largo=800, color=(0.01, 0.01, 0.02), ancho=10)
        return poner(img, h), {}


class P3C(Plano):
    """Una extremidad larga y oscura se acerca a su antebrazo izquierdo. Corte a blanco."""
    paleta = "noche"
    dib = 12

    def preparar(self):
        self.fondo = fondos.sabana()

    def atras(self, h, tq):
        temblor = 4 * math.sin(tq * 9)
        P.antebrazo(h, 600 + temblor * 0.3, 1150, 1.05, rot=0.2, tono="noche", palidez=0.12)
        llega = suave(tramo(tq, 0.3, 4.3))
        punta = (lerp(1180, 640, llega), lerp(150, 1010, llega))
        P.extremidad(h, (1500, -260), punta, t=tq, abre=0.75 - 0.4 * llega)

    def cuadro(self, t):
        tq = self.tq(t)
        e = suave(t / self.dur)
        im = self.compuesto(tq, self.fondo, self.atras)
        return vista(im, lerp(600, 560, e), lerp(900, 1020, e), lerp(1080, 800, e)), {"blanco": tramo(t, 4.3, 4.42)}


# =========================================================================================================
# ESCENA 4 · el recuerdo

class P4A(Plano):
    """La familia sonriendo en un parque soleado."""
    paleta = "recuerdo"
    dib = 8
    halo = 0.95
    grano = 0.03

    def preparar(self):
        self.fondo = fondos.parque()

    def atras(self, h, tq):
        b = lambda i: 2.5 * math.sin(tq * 1.6 + i * 1.9)
        # el niño sobre los hombros del padre
        P.busto(h, 770, 800 + b(3), 0.42, "nino", "recuerdo", largo=1000)
        P.cabeza(h, 770, 800 + b(3), 0.42, quien="nino", tono="recuerdo", ap=0.55, boca="feliz", ceja=0.3, ojera=0.0)
        for i, (x, y, quien, flip) in enumerate(((210, 1080, "hermana", False), (490, 1030, "madre", False),
                                                 (770, 1090, "padre", True))):
            yy = y + b(i)
            inc = (-0.05, 0.03, 0.06)[i]
            P.busto(h, x, yy, 0.66, quien, "recuerdo", flip=flip, largo=900, rot=inc)
            if quien == "padre":
                for lado in (-1, 1):
                    ruta = [(x + lado * 40, yy - 90), (x + lado * 150, yy + 10), (x + lado * 160, yy + 190)]
                    h.tinta(ruta, 62, hexa("#2a1a12"), afila=(0.0, 0.0))
                    h.tinta(ruta, 52, hexa("#44618a"), afila=(0.0, 0.0))
                    h.forma(elipse(x + lado * 160, yy + 200, 38, 26), hexa("#f0ece2"))
            P.cabeza(h, x, yy, 0.66, quien=quien, tono="recuerdo", flip=flip, ap=0.5, boca="feliz", ceja=0.4, ojera=0.0,
                     rot=inc)
        # motas de polen y luz que flotan
        rng = np.random.default_rng(3)
        for k in range(40):
            x = (rng.uniform(0, W) + tq * rng.uniform(4, 22)) % W
            y = (rng.uniform(0, 1200) - tq * rng.uniform(4, 16)) % 1200
            h.resplandor(x, y, rng.uniform(8, 20), (1, 0.96, 0.7), 0.7)

    def imagen(self, t):
        e = suave(t / self.dur)
        im = self.compuesto(self.tq(t), self.fondo, self.atras)
        return vista(im, lerp(540, 520, e), lerp(980, 1060, e), lerp(1080, 800, e))

    def cuadro(self, t):
        return self.imagen(t), {"blanco": 1 - tramo(t, 0.0, 1.4)}


# =========================================================================================================
# ESCENA 5 · el despertar

class P5A(Plano):
    """El recuerdo se congela, se agrieta y se rompe como un cristal hacia la oscuridad."""
    paleta = "recuerdo"
    dib = 24
    halo = 0.7

    def preparar(self):
        self.mem = P4A(8.0)
        self.foto = _pil(self.mem.imagen(7.95))
        rng = np.random.default_rng(11)
        n = 44
        gx, gy = np.meshgrid(np.linspace(0, AN, 7), np.linspace(0, AL, 9))
        semillas = np.stack([gx.ravel() + rng.normal(0, 40, gx.size), gy.ravel() + rng.normal(0, 60, gy.size)], axis=1)[:n]
        yy, xx = np.mgrid[0:AL, 0:AN]
        _, self.etiquetas = cKDTree(semillas).query(np.stack([xx.ravel(), yy.ravel()], axis=1))
        self.etiquetas = self.etiquetas.reshape(AL, AN)
        self.semillas = semillas
        self.vel = rng.normal(0, 1, (len(semillas), 2)) * np.array([260, 300]) + (semillas - [AN / 2, AL / 2]) * 0.5
        self.gira = rng.normal(0, 1.4, len(semillas))
        self.cajas = []
        for i in range(len(semillas)):
            ys, xs = np.where(self.etiquetas == i)
            self.cajas.append((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1) if len(xs) else (0, 0, 1, 1))

    def cuadro(self, t):
        rota = tramo(t, 0.9, 3.0)
        if t < 0.9:
            img = _arr(self.foto)
            jx, jy = sacudida(t, 3.5 * tramo(t, 0.3, 0.9), 1)
            img = np.roll(img, (int(jy), int(jx)), axis=(0, 1))
            h = pantalla()
            centro = (540, 900)
            rng = np.random.default_rng(5)
            for _ in range(int(60 * tramo(t, 0.1, 0.9))):
                a = rng.uniform(0, 2 * math.pi)
                L = rng.uniform(150, 900) * tramo(t, 0.1, 0.9) * 1.4
                pts = [centro, (centro[0] + math.cos(a) * L * 0.5 + rng.normal(0, 30),
                                centro[1] + math.sin(a) * L * 0.5 + rng.normal(0, 30)),
                       (centro[0] + math.cos(a + 0.05) * L, centro[1] + math.sin(a + 0.05) * L)]
                h.tinta(pts, 5, (1, 1, 1), afila=(0.0, 1.0), alfa=0.9)
            return poner(img, h), {}
        # a partir de aquí caen los pedazos, uno por uno
        salida = np.zeros((AL, AN, 3), np.float32)
        rgba = self.foto.convert("RGBA")
        d = t - 0.9
        for i, (x0, y0, x1, y1) in enumerate(self.cajas):
            retraso = (i % 9) * 0.045
            u = max(d - retraso, 0.0)
            m = (self.etiquetas[y0:y1, x0:x1] == i).astype(np.uint8) * 255
            trozo = rgba.crop((x0, y0, x1, y1))
            trozo.putalpha(Image.fromarray(m))
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            ang = math.degrees(self.gira[i] * u * 2.2)
            esc = max(1.0 - 0.28 * u, 0.2)
            nx, ny = cx + self.vel[i][0] * u * 0.9, cy + self.vel[i][1] * u * 0.9 + 320 * u * u
            t2 = trozo.resize((max(1, int((x1 - x0) * esc)), max(1, int((y1 - y0) * esc)))).rotate(ang, expand=True)
            base = Image.fromarray((salida * 255).astype(np.uint8)).convert("RGBA")
            base.alpha_composite(t2, (int(nx - t2.width / 2), int(ny - t2.height / 2))) if (
                -t2.width < nx < AN + t2.width and -t2.height < ny < AL + t2.height) else None
            salida = _arr(base.convert("RGB"))
        return salida * (1 - 0.6 * rota), {}


class _Flash(Plano):
    """Cada flash del montaje: un cuadro fuerte, sostenido, con un destello."""
    paleta = "noche"
    dib = 12
    grano = 0.07


class P5B(_Flash):
    """Flash: una máscara blanca ladea la cabeza."""

    def preparar(self):
        self.fondo = np.full((H, W, 3), 0.02, np.float32)

    def atras(self, h, tq):
        k = int(tq * 12)
        ang = (0.0, 0.32, 0.62, 0.5)[min(k // 3, 3)]
        P.mascara_cerca(h, 540 + 30 * math.sin(k), 900, 0.72, "noche", ladea=ang)

    def cuadro(self, t):
        tq = self.tq(t)
        im = self.compuesto(tq, self.fondo, self.atras)
        jx, jy = sacudida(t, 5, 12)
        h = pantalla()
        lineas_de_velocidad(h, (540, 700), 16, int(tq * 12), r0=380, color=(0.9, 0.95, 1.0), ancho=6)
        return poner(vista(im, 540 + jx, 900 + jy, 900), h), {"negativo": int(tq * 12) in (1, 5), "blanco": 0.5 * (t < 0.06)}


class P5C(_Flash):
    """Flash: el techo gira violentamente."""

    def preparar(self):
        self.fondo = _pil(fondos.techo())

    def cuadro(self, t):
        ang = t * 6.5 + t * t * 6
        img = vista(self.fondo, 540, 840, 760, rot=ang)
        for k in (1, 2):
            img = img * 0.55 + vista(self.fondo, 540, 840, 760, rot=ang - 0.16 * k) * 0.45
        return np.clip(img * 1.5, 0, 1), {"blanco": 0.4 * (t < 0.05)}


class P5D(_Flash):
    """Flash: Alex recupera el control de su brazo y la extremidad se retira."""

    def preparar(self):
        self.fondo = fondos.sabana()

    def atras(self, h, tq):
        golpe = tramo(tq, 0.3, 0.5)
        P.antebrazo(h, 600 - 90 * golpe, 1150 + 160 * golpe, 1.05 + 0.15 * golpe, rot=0.2 - 0.5 * golpe, tono="noche",
                    palidez=0.12)
        se_va = suave(tramo(tq, 0.05, 0.85))
        P.extremidad(h, (1500, -260), (lerp(560, 1350, se_va), lerp(1040, -300, se_va)), t=tq, abre=0.85)

    def cuadro(self, t):
        tq = self.tq(t)
        jx, jy = sacudida(t, 6 * (1 - tramo(t, 0.5, 0.9)), 14)
        im = self.compuesto(tq, self.fondo, self.atras)
        return vista(im, 560 + jx, 1000 + jy, lerp(1000, 820, suave(t))), {"blanco": 0.5 * (t < 0.06)}


class P5E(Plano):
    """Se sienta de golpe en la cama, empapado en sudor frío, jadeando."""
    paleta = "noche"
    dib = 12

    def preparar(self):
        self.fondo = fondos.cuarto()

    def atras(self, h, tq):
        sube = suave(tramo(tq, 0.1, 0.5))
        rebote = math.sin(tramo(tq, 0.5, 0.9) * math.pi) * 26
        jadeo = abs(math.sin(tq * 5.2)) * (1 - 0.4 * tramo(tq, 2.5, 4.0))
        y = 1080 + 900 * (1 - sube) + rebote + 6 * jadeo
        P.busto(h, 560, y, 1.5, "alex", "noche", largo=900)
        P.cabeza(h, 560, y, 1.5, quien="alex", tono="noche", rot=0.06 * math.sin(tq * 5), ap=1.1, pupila=0.55,
                 mirada=(0.2 * math.sin(tq * 1.3), 0.15), ceja=0.7, ceja_in=0.5, boca="abierta", abre=0.3 + 0.5 * jadeo,
                 ojera=1.0, sudor=1.0, palidez=0.14)
        # la cobija arrugada sobre las piernas
        h.forma([(-20, 1690), (300, 1650), (640, 1662), (1100, 1620), (1100, 1930), (-20, 1930)], hexa("#1f2c44"),
                suave_=False)
        h.tinta([(-20, 1690), (300, 1650), (640, 1662), (1100, 1620)], 12, hexa("#5a76a4"), afila=(0.0, 0.0), alfa=0.8)
        for x0 in (140, 420, 760):
            h.tinta([(x0, 1700), (x0 + 60, 1800), (x0 + 30, 1920)], 14, hexa("#0e1524"), afila=(0.2, 0.4), alfa=0.8)

    def cuadro(self, t):
        tq = self.tq(t)
        jx, jy = sacudida(t, 10 * math.exp(-max(t - 0.45, 0) * 2.4) * (t > 0.4), 23)
        im = self.compuesto(tq, self.fondo, self.atras)
        return vista(im, 560 + jx, lerp(1050, 1010, suave(t / self.dur)) + jy, lerp(1000, 880, suave(t / self.dur))), {}


class P5F(Plano):
    """La habitación vacía: solo la luz de la luna entra por la ventana. Todo en silencio."""
    paleta = "noche"
    dib = 8
    halo = 0.7

    def preparar(self):
        self.fondo = fondos.cuarto()

    def atras(self, h, tq):
        rng = np.random.default_rng(9)
        for k in range(28):
            x = (rng.uniform(560, 1050) - tq * rng.uniform(6, 26)) % 1050 + 40
            y = (rng.uniform(420, 1000) + tq * rng.uniform(4, 16)) % 600 + 420
            h.resplandor(x, y, rng.uniform(5, 12), (0.75, 0.9, 1.0), 0.55)

    def cuadro(self, t):
        e = suave(t / self.dur)
        im = self.compuesto(self.tq(t), self.fondo, self.atras)
        return vista(im, lerp(560, 760, e), lerp(1000, 820, e), lerp(1080, 760, e)), {}


# =========================================================================================================
# ESCENA 6 · la mañana

class P6A(Plano):
    """La mañana: el mismo comedor, Alex solo con sus chilaquiles. Un plano largo y casi inmóvil."""
    paleta = "manana"
    dib = 8
    grano = 0.05

    def preparar(self):
        self.fondo = fondos.comedor(dia=True)

    def atras(self, h, tq):
        parp = cierre_de_parpados(tq, (3.0, 6.1), dur=0.2)
        y = 1110 + 3 * math.sin(tq * 1.1)
        P.busto(h, 800, y, 1.0, "alex", "manana", largo=900)
        P.cabeza(h, 800, y, 1.0, quien="alex", tono="manana", rot=0.02, ap=0.45 * (1 - parp), mirada=(-0.1, 0.25),
                 ceja=-0.15, boca="cansada", ojera=1.0, palidez=0.25)

    def delante(self, h, tq):
        P.chilaquiles(h, 600, 1480, 0.9, "manana")
        for i in range(3):
            x0 = 560 + i * 60
            fase = tq * 0.6 + i * 0.4
            pts = [(x0, 1400), (x0 + 24 * math.sin(fase * 3), 1330), (x0 - 20 * math.sin(fase * 2), 1250),
                   (x0 + 14, 1180)]
            h.tinta(pts, 22, (0.95, 0.95, 0.95), afila=(0.2, 0.7), alfa=0.22)

    def cuadro(self, t):
        e = suave(t / self.dur)
        im = self.compuesto(self.tq(t), self.fondo, self.atras, self.delante)
        return vista(im, lerp(600, 720, e), lerp(1050, 1180, e), lerp(1080, 900, e)), {}


class P6B(Plano):
    """Un ardor sordo: baja la mirada hacia su brazo izquierdo."""
    paleta = "manana"
    dib = 12

    def preparar(self):
        self.fondo = _desenfocar(fondos.comedor(dia=True), 14)

    def atras(self, h, tq):
        punzada = math.sin(math.pi * tramo(tq, 0.8, 1.3))
        baja = suave(tramo(tq, 1.5, 2.6))
        x = 560 + 3 * punzada * math.sin(tq * 40)
        P.busto(h, x, 950, 2.0, "alex", "manana", largo=700)
        P.cabeza(h, x, 950, 2.0, quien="alex", tono="manana", rot=0.24 * baja, ap=lerp(0.55, 0.42, baja),
                 mirada=(lerp(0.0, -0.3, baja), lerp(0.15, 1.0, baja)), ceja=-0.2 - 0.6 * punzada, ceja_in=0.5 * punzada,
                 boca="cansada", ojera=1.0, palidez=0.25, sudor=0.3 * punzada)

    def cuadro(self, t):
        e = suave(t / self.dur)
        im = self.compuesto(self.tq(t), self.fondo, self.atras)
        return vista(im, lerp(580, 520, e), lerp(950, 1050, e), lerp(760, 640, e)), {}


class P6C(Plano):
    """Levanta el antebrazo: una incisión profunda, con suturas quirúrgicas perfectas. Corte a negro."""
    paleta = "manana"
    dib = 12

    def preparar(self):
        self.fondo = _desenfocar(fondos.comedor(dia=True), 26) * 0.9

    def atras(self, h, tq):
        sube = suave(tramo(tq, 0.1, 1.4))
        y = 1050 + 1200 * (1 - sube)
        P.antebrazo(h, 540, y, 1.55, rot=-0.13 + 0.08 * (1 - sube), tono="manana", incision=1.0, palidez=0.22)

    def cuadro(self, t):
        e = suave(tramo(t, 1.6, self.dur))
        jx, jy = sacudida(t, 2.0 * tramo(t, 1.4, 2.0), 31)
        im = self.compuesto(self.tq(t), self.fondo, self.atras)
        return vista(im, 540 + jx, lerp(1020, 1000, e) + jy, lerp(1080, 620, e)), {"negro": tramo(t, self.dur - 0.12, self.dur - 0.04)}


class Titulo(Plano):
    """Negro, y el título."""
    paleta = "neutro"
    dib = 12

    def cuadro(self, t):
        h = pantalla()
        cose = tramo(t, 0.9, 2.1) * (1 - tramo(t, 3.3, 3.8))
        if cose > 0:
            x0, x1, y = 300, 780, 1450
            xf = x0 + (x1 - x0) * cose
            h.tinta([(x0, y), ((x0 + xf) / 2, y + 3), (xf, y)], 6, hexa("#7a1a22"), afila=(0.02, 0.02))
            for i in range(int(11 * cose)):
                px = x0 + 22 + i * 44
                h.tinta([(px - 7, y - 16), (px + 7, y + 16)], 4, hexa("#d8d2c4"), afila=(0.1, 0.1))
        return poner(np.zeros((AL, AN, 3), np.float32), h), {"titulo": tramo(t, 0.5, 1.2) * (1 - tramo(t, 3.3, 3.8))}


PLANOS = {"1A": P1A, "1B": P1B, "1C": P1C, "Negro": Negro, "2A": P2A, "2B": P2B, "2C": P2C, "2D": P2D,
          "3A": P3A, "3B": P3B, "3C": P3C, "4A": P4A, "5A": P5A, "5B": P5B, "5C": P5C, "5D": P5D, "5E": P5E,
          "5F": P5F, "6A": P6A, "6B": P6B, "6C": P6C, "Título": Titulo}
