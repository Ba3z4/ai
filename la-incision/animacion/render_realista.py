#!/usr/bin/env python3
"""Renderiza La Incisión con personajes realistas y el arte pintado de la referencia
(guion original, vertical 9:16, 24 fps, con sonido).

Los personajes y lugares salen de las imágenes del proyecto: la toma 1A de Gemini (Alex y su familia),
el chat de Mariana (referencia 3), las figuras enmascaradas (5), la habitación (1) y el parque (2).
Cada plano es una de esas imágenes pintada (pinceladas planas, póster, claroscuro), con cámara lenta y
deformaciones suaves para actuar: Alex levanta la mirada, sonríe forzado, mueve los labios, mueve los
ojos, grita sin voz y baja la vista. Lo que no tiene foto (la sábana, la garra, la herida, el sudor) se pinta
encima; su antebrazo es el de la toma 1A, recortado con su silueta.

Uso (desde la carpeta la-incision):
    python3 animacion/render_realista.py              # → la-incision-realista.mp4 y su versión ligera
    python3 animacion/render_realista.py --fotos      # hoja de contactos
    python3 animacion/render_realista.py --planos 1C  # vuelve a pintar solo esos planos y rearma el video

La toma 1A (tomas/1A.mp4) es opcional: si no está, el plano 1A usa su cuadro fijo con cámara lenta.
"""

import argparse
import math
import os
import subprocess
import sys
import time
from multiprocessing import Pool
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(RAIZ / "herramientas"))

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402
from scipy.ndimage import gaussian_filter, map_coordinates  # noqa: E402

import dibujo  # noqa: E402
import pintura  # noqa: E402
import planos  # noqa: E402
from cuerpo import chilaquiles, extremidad  # noqa: E402
from dibujo import Lienzo, superficie_de, suave, tramo  # noqa: E402
from render import buscar_ffmpeg  # noqa: E402
from render_pintado import TituloPintado, linea_de_tiempo, palabras_de_dialogo  # noqa: E402

dibujo.Lienzo.sin_tinta = True
planos.SUBLIMINALES = False

FPS = 24
AN, AL = 720, 1280
BUILD = AQUI / "build" / "realista"
FUENTE = AQUI / "fuentes" / "Cinzel.ttf"
REF = RAIZ / "referencias"
FUENTES = {
    "alex": REF / "vertical" / "07-toma1A-final.jpg",
    "comedor": REF / "vertical" / "06-toma1A-comedor.jpg",
    "cuarto": REF / "01-habitacion-noche.jpg",
    "parque": REF / "02-recuerdo-parque.jpg",
    "chat": REF / "03-pov-chat.jpg",
    "cena": REF / "04-comedor-cena.jpg",
    "figuras": REF / "05-figuras-enmascaradas.jpg",
}
TOMA = RAIZ / "tomas" / "1A.mp4"

# Rasgos de Alex en su primer plano (07-toma1A-final.jpg, 720×1280).
IRIS, PARPADO, CEJA = (315, 585), (318, 566), (270, 515)
COMISURA, MEJILLA, LABIO, MENTON, QUIJADA = (345, 882), (385, 835), (290, 905), (340, 1025), (450, 980)
# Cajas de recorte: máscaras de la referencia 5 y el antebrazo de la toma 1A.
MASCARAS = {"centro": (1060, 40, 1240, 335), "izq": (835, 215, 950, 405), "der": (1388, 170, 1505, 375)}
ANTEBRAZO = (250, 1005, 720, 1250)
SILUETA_BRAZO = [(255, 1022), (350, 1054), (450, 1080), (550, 1100), (650, 1110), (705, 1110), (712, 1180),
                 (700, 1232), (550, 1232), (400, 1222), (320, 1190), (255, 1150)]
EJE_BRAZO = ((280, 1088), (690, 1168))

_arr, _pil = {}, {}


def fuente(nombre):
    if nombre not in _arr:
        _pil[nombre] = Image.open(FUENTES[nombre]).convert("RGB")
        _arr[nombre] = np.asarray(_pil[nombre], np.float32) / 255
    return _arr[nombre]


def a_pil(arr):
    return Image.fromarray((np.clip(arr, 0, 1) * 255 + 0.5).astype(np.uint8))


def encuadre(src, cx, cy, ancho, rot=0.0):
    """Rectángulo 9:16 de la imagen centrado en (cx, cy), de `ancho` px de la fuente y girado `rot` grados."""
    im = src if isinstance(src, Image.Image) else a_pil(src)
    s = ancho / AN
    th = math.radians(rot)
    a, b = s * math.cos(th), -s * math.sin(th)
    d, e = s * math.sin(th), s * math.cos(th)
    c = cx - a * AN / 2 - b * AL / 2
    f = cy - d * AN / 2 - e * AL / 2
    out = im.transform((AN, AL), Image.AFFINE, (a, b, c, d, e, f), resample=Image.BICUBIC, fillcolor=(0, 0, 0))
    return np.asarray(out, np.float32) / 255


def encuadre_de(nombre, cx, cy, ancho, rot=0.0):
    fuente(nombre)
    return encuadre(_pil[nombre], cx, cy, ancho, rot)


def deformar(arr, bultos):
    """Deformación suave: cada bulto (x, y, dx, dy, radio) empuja la imagen alrededor de (x, y)."""
    bultos = [b for b in bultos if abs(b[2]) + abs(b[3]) > 0.05]
    if not bultos:
        return arr
    out = arr.copy()
    h, w = arr.shape[:2]
    x0 = max(0, int(min(b[0] - 3 * b[4] for b in bultos)))
    x1 = min(w, int(max(b[0] + 3 * b[4] for b in bultos)) + 1)
    y0 = max(0, int(min(b[1] - 3 * b[4] for b in bultos)))
    y1 = min(h, int(max(b[1] + 3 * b[4] for b in bultos)) + 1)
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    dx = np.zeros_like(xx)
    dy = np.zeros_like(yy)
    for bx, by, ddx, ddy, r in bultos:
        g = np.exp(-((xx - bx) ** 2 + (yy - by) ** 2) / (2 * r * r))
        dx += ddx * g
        dy += ddy * g
    for c in range(3):
        out[y0:y1, x0:x1, c] = map_coordinates(arr[..., c], [yy - dy, xx - dx], order=1, mode="nearest")
    return out


def noche(img, fuerza=1.0):
    """La foto pasa a luz de luna: azul, oscura, con las luces frías."""
    luma = img @ np.array([0.299, 0.587, 0.114], np.float32)
    frio = luma[..., None] * np.array([0.42, 0.58, 0.95], np.float32) * 0.75
    return img * (1 - fuerza) + frio * fuerza


def manana(img):
    """Luz de mañana lavada: casi sin color y la piel pálida."""
    luma = img @ np.array([0.299, 0.587, 0.114], np.float32)
    return np.clip(luma[..., None] * np.array([0.98, 1.0, 1.02], np.float32) * 0.55 + img * 0.4 + 0.06, 0, 1)


def pegar(base, src, caja, centro, alto, rot=0.0, borde=0.4, transformar=None, silueta=None):
    """Pega un recorte de `src` escalado a `alto` y girado `rot` grados, con orilla difuminada en elipse
    (o siguiendo `silueta`, un polígono en coordenadas de la fuente)."""
    x0, y0, x1, y1 = caja
    trozo = src[y0:y1, x0:x1]
    if transformar:
        trozo = transformar(trozo)
    h, w = trozo.shape[:2]
    if silueta:
        m = Image.new("L", (w, h), 0)
        ImageDraw.Draw(m).polygon([(x - x0, y - y0) for x, y in silueta], fill=255)
        alfa = np.asarray(m.filter(ImageFilter.GaussianBlur(7)), np.float32) / 255
    else:
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
        alfa = np.clip((1 - r) / borde, 0, 1)
    rgba = np.concatenate([trozo, alfa[..., None]], axis=2)
    im = Image.fromarray((np.clip(rgba, 0, 1) * 255).astype(np.uint8), "RGBA")
    esc = alto / h
    im = im.resize((max(1, int(w * esc)), max(1, int(h * esc))), Image.BICUBIC)
    if rot:
        im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    arr = np.asarray(im, np.float32) / 255
    ph, pw = arr.shape[:2]
    px, py = int(centro[0] - pw / 2), int(centro[1] - ph / 2)
    ax0, ay0 = max(0, px), max(0, py)
    ax1, ay1 = min(AN, px + pw), min(AL, py + ph)
    if ax1 <= ax0 or ay1 <= ay0:
        return base
    parte = arr[ay0 - py:ay1 - py, ax0 - px:ax1 - px]
    a = parte[..., 3:4]
    base[ay0:ay1, ax0:ax1] = base[ay0:ay1, ax0:ax1] * (1 - a) + parte[..., :3] * a
    return base


def capa():
    """Lienzo transparente del tamaño del cuadro para pintar encima (garra, sudor, párpados)."""
    lz = Lienzo(AN, semilla=5)
    lz.hervor = 0.0
    lz.nuevo(0, fondo=None)
    lz.camara()
    return lz


def encima(base, lz):
    lz.sup.flush()
    datos = np.ndarray((lz.h, lz.w, 4), np.uint8, lz.sup.get_data(), strides=(lz.sup.get_stride(), 4, 1))
    rgb = datos[..., 2::-1].astype(np.float32) / 255
    a = datos[..., 3:4].astype(np.float32) / 255
    return base * (1 - a) + rgb


def sudor(lz, t, gotas=((200, 380), (560, 300), (430, 760))):
    for k, (x, y) in enumerate(gotas):
        baja = (t * 70 + k * 90) % 260
        lz.resplandor(x, y + baja, 16, (0.85, 0.92, 1.0), 0.8)
        lz.forma(dibujo.elipse(x, y + baja, 6, 9, 10), (0.88, 0.94, 1.0), tinta=False, alfa=0.85)


def habla_en(t, silabas):
    for a, b in silabas:
        if a <= t <= b:
            return math.sin(math.pi * (t - a) / (b - a))
    return 0.0


def temblor(t, fuerza, semilla=0):
    rng = np.random.default_rng((semilla, int(t * 12)))
    return rng.normal(0, fuerza), rng.normal(0, fuerza)


# --- los planos ---------------------------------------------------------------------------------

class Plano:
    paleta = "noche"
    radio = None

    def __init__(self, ident, dur):
        self.id, self.dur = ident, dur
        self.preparar()

    def preparar(self):
        pass

    def cuadro(self, t):
        """Devuelve (imagen float AL×AN×3, efectos)."""
        raise NotImplementedError


class P1A(Plano):
    """La cena: la toma de Gemini en movimiento (o su cuadro fijo si no está)."""
    paleta = "cena"

    def preparar(self):
        self.proc, self.siguiente = None, 0

    def _leer(self, i):
        if self.proc is None or i != self.siguiente:
            if self.proc:
                self.proc.kill()
            self.proc = subprocess.Popen([buscar_ffmpeg(), "-hide_banner", "-loglevel", "error", "-ss", f"{i / FPS:.3f}",
                                          "-i", str(TOMA), "-vf", f"fps={FPS},scale={AN}:{AL}", "-f", "rawvideo",
                                          "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE,
                                         stderr=subprocess.DEVNULL)
            self.siguiente = i
        datos = self.proc.stdout.read(AN * AL * 3)
        self.siguiente += 1
        if len(datos) < AN * AL * 3:
            return None
        return np.frombuffer(datos, np.uint8).reshape(AL, AN, 3).astype(np.float32) / 255

    def cuadro(self, t):
        img = self._leer(int(round(t * FPS))) if TOMA.is_file() else None
        if img is None:
            k = suave(t / self.dur)
            img = encuadre_de("comedor", 360 + 120 * k, 640 + 60 * k, 720 - 260 * k)
        return img, {}


class P1B(Plano):
    """El chat con Mariana, en las manos de Alex."""
    paleta = "cena"
    radio = 2

    def cuadro(self, t):
        u = suave(t / self.dur)
        img = encuadre_de("chat", 1025 + math.sin(t * 0.7) * 8, 600 + math.sin(t * 1.1) * 8, 660 - 150 * u)
        estres = tramo(t, 3.0, 3.5) * (1 - tramo(t, 4.3, 4.9))
        if estres > 0.02:
            img = np.asarray(a_pil(img).filter(ImageFilter.GaussianBlur(estres * 5)), np.float32) / 255
        return img, {}


SILABAS_ALEX = ((2.2, 2.42), (2.5, 2.72), (2.95, 3.1), (3.14, 3.28), (3.32, 3.6))


class P1C(Plano):
    """«Sí, ma. Todo bien.»: bloquea el celular, levanta la mirada, sonrisa forzada que se borra."""
    paleta = "cena"

    def cuadro(self, t):
        sube = suave(tramo(t, 1.0, 1.6))
        baja = suave(tramo(t, 4.3, 5.3))
        arriba = sube * (1 - baja)
        sonrisa = tramo(t, 1.8, 2.2) * (1 - tramo(t, 4.4, 5.2))
        habla = habla_en(t, SILABAS_ALEX)
        cara = deformar(fuente("alex"), [
            (*IRIS, 0, -8 * arriba, 13), (*PARPADO, 0, -5 * arriba, 24),
            (*COMISURA, 5 * sonrisa, -9 * sonrisa, 24), (*MEJILLA, 2 * sonrisa, -5 * sonrisa, 50),
            (*LABIO, 0, 8 * habla, 22), (*MENTON, 0, 6 * habla, 70),
        ])
        img = encuadre(cara, 390, 650 - 25 * arriba, 700 - 20 * t / self.dur, rot=4 * arriba)
        celular = 1 - tramo(t, 0.9, 1.0)
        if celular > 0:
            yy, xx = np.mgrid[0:AL, 0:AN].astype(np.float32)
            luz = np.exp(-((xx - 60) ** 2 + (yy - 1350) ** 2) / (2 * 420 ** 2))
            img = img + luz[..., None] * np.array([0.1, 0.35, 0.6], np.float32) * celular
        return img, {}


class P2A(Plano):
    """La habitación en penumbra: las sombras de los rincones crecen, Alex parpadea."""
    paleta = "noche"

    def cuadro(self, t):
        u = t / self.dur
        img = encuadre_de("cuarto", 1400 - 60 * u, 560, 613 - 40 * u)
        crece = suave(tramo(t, 0.8, self.dur))
        xs = np.linspace(-1, 1, AN, dtype=np.float32)
        orillas = np.clip((np.abs(xs) - (0.75 - 0.45 * crece)) / 0.3, 0, 1)
        img = img * (1 - 0.85 * orillas)[None, :, None]
        lz = capa()
        cierre = max(math.sin(math.pi * tramo(t, 2.0, 2.7)) * 0.75, math.sin(math.pi * tramo(t, 5.0, 6.1)) * 0.95)
        planos.parpados(lz, cierre)
        return encima(img, lz), {}


class P2B(Plano):
    """Aparecen las tres sombras: primero las máscaras, luego los cuerpos."""
    paleta = "noche"

    def cuadro(self, t):
        k = suave(tramo(t, 0.5, self.dur))
        img = encuadre_de("figuras", 1150, 520 - 60 * k, 613 - 120 * k)
        luma = img @ np.array([0.299, 0.587, 0.114], np.float32)
        mascaras = np.clip((luma - 0.42) / 0.2, 0, 1)
        cuerpos = 0.12 + 0.88 * tramo(t, 1.3, 3.8)
        visible = np.maximum(cuerpos, mascaras * tramo(t, 0.8, 2.2))
        return img * visible[..., None], {}


class P2C(Plano):
    """El cuerpo no responde: solo los ojos se mueven."""
    paleta = "noche"
    MIRADAS = ((0.0, -1.0), (0.45, 1.0), (0.9, -0.5), (1.3, 0.9), (1.75, -1.0), (2.25, 0.2), (2.7, 0.8))

    def cuadro(self, t):
        mira = [m for a, m in self.MIRADAS if t >= a][-1]
        cara = deformar(noche(fuente("alex"), 0.75) * 1.35, [(*IRIS, 9 * mira, 0, 12), (*PARPADO, 0, -4, 24)])
        jx, jy = temblor(t, 3, 7)
        img = encuadre(cara, 350 + jx, 640 + jy, 500)
        lz = capa()
        sudor(lz, t, ((180, 300), (620, 250)))
        return encima(img, lz), {}


class P2D(Plano):
    """Se deslizan hacia la cama; la imagen tiembla y se le cierran los ojos."""
    paleta = "noche"

    def cuadro(self, t):
        av = suave(tramo(t, 0.4, 6.6))
        jx, jy = temblor(t, 2 + 12 * av, 9)
        img = encuadre_de("figuras", 1150 + jx, 520 - 200 * av + jy, 613 - 280 * av)
        img = img * (1 - 0.35 * av)
        lz = capa()
        planos.parpados(lz, tramo(t, 5.2, 6.1) * 0.7 - tramo(t, 6.2, 6.6) * 0.35 + tramo(t, 6.7, 7.7) * 0.66)
        return encima(img, lz), {}


class P3A(Plano):
    """Los ojos se abren de golpe: las tres máscaras flotan encima de su cara."""
    paleta = "noche"

    def cuadro(self, t):
        jx, jy = temblor(t, 2.5, 11)
        img = noche(encuadre_de("cuarto", 960 + jx, 330 + jy, 520), 0.7) * 0.55
        figuras = fuente("figuras")
        pegar(img, figuras, MASCARAS["izq"], (70, 900), 700, rot=38)
        pegar(img, figuras, MASCARAS["der"], (660, 860), 700, rot=-34)
        ladeo = suave(tramo(t, 2.0, 5.2))
        pegar(img, figuras, MASCARAS["centro"], (360 + jx, 620 + jy), 980, rot=-2 - 24 * ladeo)
        lz = capa()
        planos.parpados(lz, 1 - tramo(t, 0.0, 0.22) + 0.9 * math.sin(math.pi * tramo(t, 3.3, 3.55)))
        return encima(img, lz), {}


class P3B(Plano):
    """El grito sin voz: abre la boca y no sale nada."""
    paleta = "noche"

    def cuadro(self, t):
        abre = suave(tramo(t, 0.15, 0.6)) * (0.9 + 0.1 * math.sin(t * 23))
        cara = deformar(noche(fuente("alex"), 0.75) * 1.3, [
            (*LABIO, -4 * abre, 34 * abre, 32), (*MENTON, 0, 30 * abre, 90), (*QUIJADA, 0, 16 * abre, 110),
            (*PARPADO, 0, -7, 24), (*CEJA, 0, -8 * abre, 40),
        ])
        if abre > 0.05:
            boca = Image.new("L", (AN, AL), 0)
            ImageDraw.Draw(boca).ellipse([240, 880 + 4 * abre, 318, 890 + 30 * abre], fill=255)
            m = np.asarray(boca.filter(ImageFilter.GaussianBlur(4)), np.float32)[..., None] / 255
            cara = cara * (1 - m) + np.array([0.05, 0.01, 0.02], np.float32) * m
        jx, jy = temblor(t, 6, 13)
        img = encuadre(cara, 360 + jx, 820 + jy, 600)
        ys = np.linspace(0, 1, AL, dtype=np.float32)
        img = img * (0.25 + 0.75 * np.clip(ys / 0.3, 0, 1))[:, None, None]
        return img, {}


_sabana = {}


def sabana_de_noche(semilla=33):
    """Sábana arrugada bajo la luz de la luna: un relieve de pliegues suaves iluminado desde la ventana."""
    if semilla not in _sabana:
        rng = np.random.default_rng(semilla)
        h, w = AL // 2, AN // 2

        def ruido(s):
            n = gaussian_filter(rng.standard_normal((h, w)).astype(np.float32), s)
            return n / n.std()

        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        wx = ruido(50) * 10
        relieve = ruido(70) * 0.35 + ruido(4) * 0.03
        # Pliegues largos: crestas curvas que se afinan en las puntas, casi todas en diagonal.
        for _ in range(11):
            ang = 0.65 + rng.normal(0, 0.4)
            px, py = rng.uniform(0, w), rng.uniform(0, h)
            c, s = math.cos(ang), math.sin(ang)
            largo = (xx - px) * c + (yy - py) * s
            ancho = -(xx - px) * s + (yy - py) * c + rng.normal(0, 0.0015) * largo ** 2 + wx
            relieve += rng.uniform(0.5, 1.1) * np.exp(-(ancho / rng.uniform(10, 26)) ** 2) * \
                np.exp(-(largo / rng.uniform(90, 220)) ** 2)
        gy, gx = np.gradient(gaussian_filter(relieve, 1.5))
        normal = np.stack([-gx * 18, -gy * 18, np.ones_like(gx)], axis=-1)
        normal /= np.linalg.norm(normal, axis=-1, keepdims=True)
        luz = np.array([0.55, -0.6, 0.58], np.float32)
        luz /= np.linalg.norm(luz)
        lambert = np.clip(normal @ luz, 0, 1)
        hueco = (relieve - relieve.min()) / (np.ptp(relieve) + 1e-6)
        ventana = np.clip(0.55 + 0.6 * (xx / w - yy / h), 0.25, 1.1)
        brillo = (0.3 + 0.7 * lambert) * (0.75 + 0.25 * hueco) * ventana * 0.8
        img = brillo[..., None] * np.array([0.5, 0.6, 0.8], np.float32) + ruido(0.7)[..., None] * 0.012
        img = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).resize((AN, AL), Image.BICUBIC)
        _sabana[semilla] = np.asarray(img, np.float32) / 255
    return _sabana[semilla].copy()


def brazo_de_noche(base, centro, alto, rot):
    """Su antebrazo sobre la sábana, con luz de luna y su sombra."""
    sombra = base.copy()
    pegar(sombra, fuente("comedor"), ANTEBRAZO, (centro[0] + 22, centro[1] + 30), alto, rot=rot,
          silueta=SILUETA_BRAZO, transformar=lambda x: x * 0)
    sombra = np.asarray(a_pil(sombra).filter(ImageFilter.GaussianBlur(14)), np.float32) / 255
    base[:] = base * 0.35 + sombra * 0.65
    return pegar(base, fuente("comedor"), ANTEBRAZO, centro, alto, rot=rot, silueta=SILUETA_BRAZO,
                 transformar=lambda x: noche(x, 0.75) * 1.45)


class P3C(Plano):
    """Una extremidad larga y oscura se acerca a su antebrazo izquierdo. Corte a blanco."""
    paleta = "noche"
    radio = 4

    def cuadro(self, t):
        base = brazo_de_noche(sabana_de_noche(), (380, 600), 470, 28)
        lz = capa()
        llega = suave(tramo(t, 0.3, 4.3))
        punta = np.array([1180, 120]) + (np.array([620, 860]) - np.array([1180, 120])) * llega
        extremidad(lz, (1500, -420), punta + (math.sin(t * 3) * 6, 0), t=t, abre=0.7 - 0.3 * llega)
        return encima(base, lz), {"blanco": tramo(t, 4.3, 4.42)}


class P4A(Plano):
    """El recuerdo: la familia en el parque soleado."""
    paleta = "oro"

    def cuadro(self, t):
        u = suave(t / 8)
        img = encuadre_de("parque", 1265 + 10 * u, 560, 700 - 90 * u)
        return img, {"blanco": 1 - tramo(t, 0.0, 1.3)}


class P5A(Plano):
    """El recuerdo se congela y se rompe como vidrio."""
    paleta = "oro"

    def preparar(self):
        self.vidrio = planos.P5A(3, AN)
        congelado, _ = P4A("4A", 8).cuadro(7.95)
        self.vidrio.congelado = superficie_de(congelado)

    def cuadro(self, t):
        lz = Lienzo(AN, semilla=3)
        lz.hervor = 0.0
        lz.nuevo(int(t * 12))
        lz.camara()
        ef = self.vidrio.dibujar(lz, t, t)
        img = np.asarray(lz.rgb8(), np.float32) / 255
        return img, {"paleta": "noche" if ef.get("grado") == "noche" else "oro"}


class P5B(Plano):
    """Flash: una máscara ladea la cabeza de forma antinatural."""
    paleta = "noche"

    def cuadro(self, t):
        ang = planos.P5B.PASOS[min(int(t * 12), len(planos.P5B.PASOS) - 1)]
        jx, jy = temblor(t, 10, 17)
        img = np.zeros((AL, AN, 3), np.float32)
        pegar(img, fuente("figuras"), MASCARAS["centro"], (360 + jx, 560 + jy), 1300, rot=-math.degrees(ang) * 0.8)
        return img, {"negativo": int(t * FPS) in (3, 4, 15)}


class P5C(Plano):
    """Flash: el techo gira violentamente."""
    paleta = "noche"

    def cuadro(self, t):
        ang = math.degrees(t * 6.5 + t * t * 5)
        img = encuadre_de("cuarto", 1000, 545, 520, rot=ang)
        for k in (1, 2):
            img = img * 0.6 + encuadre_de("cuarto", 1000, 545, 520, rot=ang - 7 * k) * 0.4
        return img * 1.25, {}


class P5D(Plano):
    """Flash: la mano oscura se retira; Alex recupera el brazo de un tirón."""
    paleta = "noche"
    radio = 4

    def cuadro(self, t):
        golpe = tramo(t, 0.3, 0.5)
        jx, jy = temblor(t, 4 + 10 * golpe * (1 - tramo(t, 0.5, 0.9)), 19)
        img = brazo_de_noche(sabana_de_noche(), (380 + jx - 110 * golpe, 600 + jy + 160 * golpe), 470 + 40 * golpe,
                             28 - 16 * golpe)
        lz = capa()
        se_va = suave(tramo(t, 0.05, 0.85))
        punta = np.array([620, 860]) + (np.array([1400, -500]) - np.array([620, 860])) * se_va
        extremidad(lz, (1600, -700), punta, t=t, abre=0.8, grosor=1.3)
        return encima(img, lz), {}


class P5E(Plano):
    """Se incorpora de golpe, empapado en sudor, jadeando."""
    paleta = "noche"

    def cuadro(self, t):
        sube = suave(tramo(t, 0.15, 0.5))
        rebote = math.sin(tramo(t, 0.5, 0.9) * math.pi) * 30
        sacude = 16 * math.exp(-max(t - 0.45, 0) * 2.2) * (t > 0.4)
        jx, jy = temblor(t, sacude, 23)
        jadeo = abs(math.sin(t * 7.5)) * (1 - 0.4 * tramo(t, 2.5, 4.0))
        cara = deformar(noche(fuente("alex"), 0.8), [(*LABIO, 0, 10 * jadeo, 22), (*PARPADO, 0, -7, 24)])
        img = encuadre(cara, 360 + jx, 640 - 950 * (1 - sube) + rebote + jy, 690 - 8 * jadeo)
        lz = capa()
        sudor(lz, t)
        return encima(img, lz), {}


class P5F(Plano):
    """La habitación vacía: solo la luz de la luna."""
    paleta = "noche"

    def cuadro(self, t):
        k = suave(t / self.dur)
        return encuadre_de("cuarto", 1450 - 40 * k, 470, 613 - 140 * k), {}


class P6A(Plano):
    """La mañana: los chilaquiles y Alex solo, pálido, con la mirada perdida."""
    paleta = "manana"

    def cuadro(self, t):
        if t < 2.6:
            img = manana(encuadre_de("cena", 1150, 760, 380 - 20 * t))
            lz = capa()
            chilaquiles(lz, 540, 1100 - 10 * t, 1.5)
            return encima(img, lz), {}
        k = suave((t - 2.6) / (self.dur - 2.6))
        parpado = 14 * math.sin(math.pi * tramo(t, 5.2, 5.45))
        cara = deformar(manana(fuente("alex")), [(*PARPADO, 0, parpado, 22)])
        return encuadre(cara, 360, 640, 720 - 60 * k), {}


class P6B(Plano):
    """Un ardor sordo: baja la mirada hacia su brazo izquierdo."""
    paleta = "manana"

    def cuadro(self, t):
        punzada = math.sin(math.pi * tramo(t, 0.8, 1.3))
        baja = suave(tramo(t, 1.5, 2.6))
        jx, jy = temblor(t, 3 * punzada, 29)
        cara = deformar(manana(fuente("alex")), [
            (*CEJA, 0, 7 * punzada, 40), (*PARPADO, 0, 7 * punzada + 5 * baja, 22), (*IRIS, -3 * baja, 8 * baja, 13),
        ])
        return encuadre(cara, 380 + jx, 660 + 25 * baja + jy, 560, rot=-5 * baja), {}


def pintar_herida(img):
    """La incisión suturada a lo largo del antebrazo (en coordenadas de la toma 1A): la piel inflamada,
    el corte cerrado que se afina en las puntas, costras y once puntadas de hilo oscuro, cada una distinta."""
    rng = np.random.default_rng(4)
    a, b = np.array(EJE_BRAZO[0], float), np.array(EJE_BRAZO[1], float)
    a, b = a + (b - a) * 0.14, a + (b - a) * 0.86
    eje = (b - a) / np.linalg.norm(b - a)
    normal = np.array([-eje[1], eje[0]])

    def punto(u):
        return a + (b - a) * u + normal * (2.2 * math.sin(u * 6.5 + 1) + 1.2 * math.sin(u * 19))

    us = np.linspace(0, 1, 60)
    linea = [tuple(punto(u)) for u in us]
    im = a_pil(img).convert("RGBA")
    capa_halo = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(capa_halo).line(linea, fill=(165, 55, 75, 110), width=24)
    im = Image.alpha_composite(im, capa_halo.filter(ImageFilter.GaussianBlur(7)))
    corte = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(corte)
    ancho = 0.6 + 2.8 * np.sin(np.pi * us) ** 0.6
    borde = [tuple(punto(u) + normal * g) for u, g in zip(us, ancho)] + \
            [tuple(punto(u) - normal * g) for u, g in zip(us[::-1], ancho[::-1])]
    d.polygon(borde, fill=(88, 14, 20, 235))
    d.line(linea[4:-4], fill=(45, 4, 8, 255), width=1)
    for _ in range(9):
        c = punto(rng.uniform(0.1, 0.9)) + normal * rng.normal(0, 2)
        r = rng.uniform(1.2, 2.6)
        d.ellipse([c[0] - r * 1.6, c[1] - r, c[0] + r * 1.6, c[1] + r], fill=(70, 12, 16, 200))
    for k in range(11):
        u = (k + 0.5) / 11 + rng.normal(0, 0.012)
        c = punto(u)
        g = rng.uniform(-0.3, 0.3)
        cruz = normal * math.cos(g) + eje * math.sin(g)
        p0, p1 = c - cruz * rng.uniform(11, 15), c + cruz * rng.uniform(11, 15)
        for p in (p0, p1):
            d.ellipse([p[0] - 2.5, p[1] - 2.5, p[0] + 2.5, p[1] + 2.5], fill=(125, 35, 45, 170))
        d.line([tuple(p0), tuple(c + normal * 0.8), tuple(p1)], fill=(20, 14, 20, 255), width=3)
        d.line([tuple(p0 + cruz * 2 - eje * 0.8), tuple(p1 - cruz * 2 - eje * 0.8)], fill=(110, 105, 115, 110), width=1)
        nudo = p1 if k % 3 else p0
        for s in (-1, 1):
            cola = nudo + eje * s * rng.uniform(5, 8) + cruz * rng.uniform(2, 5)
            d.line([tuple(nudo), tuple(cola)], fill=(20, 14, 20, 240), width=2)
    im = Image.alpha_composite(im, corte.filter(ImageFilter.GaussianBlur(0.7)))
    return np.asarray(im.convert("RGB"), np.float32) / 255


class P6C(Plano):
    """Levanta el antebrazo: una incisión con suturas quirúrgicas perfectas. Corte a negro."""
    paleta = "manana"
    radio = 3

    def preparar(self):
        self.brazo = pintar_herida(manana(fuente("comedor")) * 1.08)
        mesa = manana(encuadre_de("comedor", 360, 700, 720))
        mesa = np.asarray(a_pil(mesa).filter(ImageFilter.GaussianBlur(30)), np.float32) / 255
        luma = mesa @ np.array([0.299, 0.587, 0.114], np.float32)
        yy, xx = np.mgrid[0:AL, 0:AN].astype(np.float32)
        ventana = np.clip(1.1 - 0.55 * np.hypot(xx / AN, yy / AL * 0.8), 0.45, 1)
        self.mesa = ((luma.mean() + (luma - luma.mean()) * 0.05) * ventana)[..., None] * np.array([0.94, 0.97, 1.0], np.float32) * 0.6

    def cuadro(self, t):
        sube = suave(tramo(t, 0.1, 1.3))
        acerca = suave(tramo(t, 1.6, self.dur))
        jx, jy = temblor(t, 2.5 * tramo(t, 1.4, 2.0), 31)
        img = pegar(self.mesa.copy(), self.brazo, ANTEBRAZO, (370 + jx, 620 + 760 * (1 - sube) + jy),
                    420 + 150 * acerca, rot=30 - 6 * sube, silueta=SILUETA_BRAZO)
        return img, {"negro": tramo(t, self.dur - 0.12, self.dur - 0.04)}


class Negro(Plano):
    def cuadro(self, t):
        return np.zeros((AL, AN, 3), np.float32), {}


class Titulo(Plano):
    paleta = "cosmos"

    def preparar(self):
        self.p = TituloPintado(self.dur, AN)

    def cuadro(self, t):
        lz = Lienzo(AN, semilla=1)
        lz.hervor = 0.0
        lz.nuevo(0)
        lz.camara()
        ef = self.p.dibujar(lz, t, t)
        return np.asarray(lz.rgb8(), np.float32) / 255, ef


PLANOS = {"1A": P1A, "1B": P1B, "1C": P1C, "Negro": Negro, "2A": P2A, "2B": P2B, "2C": P2C, "2D": P2D,
          "3A": P3A, "3B": P3B, "3C": P3C, "4A": P4A, "5A": P5A, "5B": P5B, "5C": P5C, "5D": P5D, "5E": P5E,
          "5F": P5F, "6A": P6A, "6B": P6B, "6C": P6C, "Título": Titulo}


# --- acabado y montaje --------------------------------------------------------------------------

def acabado(img, plano, ef, t_global, palabras):
    img = pintura.pintar(img, ef.get("paleta", plano.paleta), radio=plano.radio)
    img = pintura.resplandor(img, 0.3)
    if ef.get("negativo"):
        img = 1 - img
    if ef.get("blanco", 0) > 0:
        img = img * (1 - ef["blanco"]) + ef["blanco"]
    if ef.get("negro", 0) > 0:
        img = img * (1 - ef["negro"])
    img = pintura.banda(img)
    if ef.get("titulo", 0) > 0:
        img = pintura.palabra(img, "LA INCISIÓN", FUENTE, alfa=ef["titulo"], tam=86)
    for texto, ini, fin in palabras:
        if ini <= t_global < fin:
            gris = max(0.0, ((t_global - ini) / (fin - ini) - 0.7) / 0.3)
            img = pintura.palabra(img, texto, FUENTE, gris=gris)
            break
    return img


def render_plano(args):
    ident, inicio, dur, salida, ffmpeg, palabras = args
    t0 = time.time()
    plano = PLANOS[ident](ident, dur)
    n = int(round(dur * FPS))
    proc = subprocess.Popen([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                             "-s", f"{AN}x{AL}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                             "-crf", "16", "-pix_fmt", "yuv420p", "-threads", "2", str(salida)], stdin=subprocess.PIPE)
    for f in range(n):
        t = f / FPS
        img, ef = plano.cuadro(t)
        img = acabado(np.clip(img, 0, 1), plano, ef, inicio + t, palabras)
        proc.stdin.write((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError(f"ffmpeg falló en el plano {ident}")
    return ident, time.time() - t0


def hoja(linea, palabras, salida, momentos=(0.55,)):
    fotos = []
    for ident, ini, dur in linea:
        plano = PLANOS[ident](ident, dur)
        for m in momentos:
            t = min(dur * m, dur - 1 / FPS)
            img, ef = plano.cuadro(t)
            img = acabado(np.clip(img, 0, 1), plano, ef, ini + t, palabras)
            im = a_pil(img).resize((AN // 2, AL // 2))
            ImageDraw.Draw(im).text((6, 6), f"{ident} {t:.1f}s", fill=(255, 255, 0))
            fotos.append(im)
        print(f"  {ident}", flush=True)
    w, h = fotos[0].size
    cols = 6
    lienzo = Image.new("RGB", (w * cols, h * math.ceil(len(fotos) / cols)))
    for i, im in enumerate(fotos):
        lienzo.paste(im, ((i % cols) * w, (i // cols) * h))
    lienzo.save(salida)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--fotos", action="store_true")
    parser.add_argument("--momentos", type=float, nargs="*", default=[0.55])
    parser.add_argument("--planos", nargs="*", help="vuelve a pintar solo estos planos")
    parser.add_argument("--procesos", type=int, default=os.cpu_count() or 2)
    parser.add_argument("--salida", type=Path, default=RAIZ / "la-incision-realista.mp4")
    args = parser.parse_args()
    BUILD.mkdir(parents=True, exist_ok=True)
    linea = linea_de_tiempo()
    palabras = palabras_de_dialogo(linea)
    total = sum(d for _, _, d in linea)
    elegidos = [x for x in linea if not args.planos or x[0] in args.planos]
    if args.fotos:
        hoja(elegidos, palabras, BUILD / "contactos.png", args.momentos)
        print(f"Hoja de contactos → {BUILD / 'contactos.png'}")
        return
    ffmpeg = buscar_ffmpeg()
    carpeta = BUILD / "planos"
    carpeta.mkdir(exist_ok=True)
    archivos = {ident: carpeta / f"{i:02d}-{ident.replace('í', 'i')}.mp4" for i, (ident, _, _) in enumerate(linea)}
    trabajos = [(ident, ini, dur, archivos[ident], ffmpeg, palabras) for ident, ini, dur in elegidos]
    trabajos.sort(key=lambda x: -x[2])
    t0 = time.time()
    print(f"Pintando {len(trabajos)} planos con {args.procesos} procesos…", flush=True)
    with Pool(args.procesos) as pool:
        for ident, seg in pool.imap_unordered(render_plano, trabajos):
            print(f"  {ident:>6} listo en {seg:.0f} s", flush=True)
    print(f"Planos en {time.time() - t0:.0f} s", flush=True)

    import sonido
    audio = BUILD / "sonido.wav"
    print("Mezclando el sonido…", flush=True)
    sonido.generar(linea, audio, cinta=False)
    lista = BUILD / "lista.txt"
    lista.write_text("".join(f"file '{archivos[i].as_posix()}'\n" for i, _, _ in linea), encoding="utf-8")
    video_in = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lista)]
    formato = ["-vf", "scale=1080:1920:flags=lanczos", "-pix_fmt", "yuv420p", "-r", str(FPS)]
    subprocess.run(video_in + ["-i", str(audio)] + formato + ["-c:v", "libx264", "-preset", "slow", "-crf", "19",
                   "-maxrate", "7M", "-bufsize", "14M", "-c:a", "aac", "-b:a", "192k", "-shortest",
                   "-movflags", "+faststart", str(args.salida)], check=True)
    print(f"Listo: {args.salida}")
    ligera = args.salida.with_name(args.salida.stem + "-ligera.mp4")
    kbps = int(28 * 8192 / total) - 128
    video = ["-c:v", "libx264", "-preset", "slower", "-b:v", f"{kbps}k", "-x264-params", "aq-mode=3:aq-strength=0.9",
             "-passlogfile", str(BUILD / "ligera")]
    subprocess.run(video_in + formato + video + ["-pass", "1", "-an", "-f", "mp4", os.devnull], check=True)
    subprocess.run(video_in + ["-i", str(audio)] + formato + video + ["-pass", "2", "-c:a", "aac", "-b:a", "128k",
                   "-shortest", "-movflags", "+faststart", str(ligera)], check=True)
    print(f"Versión ligera: {ligera}")


if __name__ == "__main__":
    main()
