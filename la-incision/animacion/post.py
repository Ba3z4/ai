"""Acabado de cada cuadro: color por escena y la textura de una cinta VHS de los 90.

Recibe el cuadro como arreglo float32 RGB (alto, ancho, 3) en 0..1 y devuelve otro igual.
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy.ndimage import uniform_filter1d

from dibujo import hexa

# Guion de color: cada escena empuja el dibujo hacia su ánimo (y todas a lo enfermizo).
GRADOS = {
    "cena": dict(lift=(0.03, 0.02, 0.0), gain=(1.04, 0.92, 0.70), gamma=1.08, sat=0.92, sombra=(0.02, 0.035, 0.0)),
    "celular": dict(lift=(0.0, 0.02, 0.03), gain=(1.0, 0.95, 0.88), gamma=1.05, sat=0.9, sombra=(0.0, 0.02, 0.03)),
    "noche": dict(lift=(0.0, 0.015, 0.035), gain=(0.86, 0.97, 1.1), gamma=1.05, sat=0.75, sombra=(0.0, 0.015, 0.03)),
    "recuerdo": dict(lift=(0.03, 0.025, 0.0), gain=(1.04, 1.0, 0.9), gamma=1.0, sat=1.15, sombra=(0, 0, 0), brillo=0.3),
    "manana": dict(lift=(0.035, 0.04, 0.04), gain=(0.96, 0.98, 0.92), gamma=1.0, sat=0.62, sombra=(0.0, 0.02, 0.01)),
    "neutro": dict(lift=(0, 0, 0), gain=(1, 1, 1), gamma=1.0, sat=1.0, sombra=(0, 0, 0)),
}

_cache = {}


def _fijos(h, w):
    """Viñeta, líneas de barrido y bancos de ruido (se calculan una vez por tamaño)."""
    clave = (h, w)
    if clave not in _cache:
        y, x = np.mgrid[0:h, 0:w].astype(np.float32)
        dx = (x - w / 2) / (w / 2)
        dy = (y - h / 2) / (h / 2)
        r = np.sqrt(dx * dx * 1.0 + dy * dy * 0.55)
        viñeta = np.clip(1.0 - 0.55 * np.clip(r - 0.45, 0, None) ** 1.6, 0.25, 1.0)
        paso = max(2, round(h / 480))  # unas 480 líneas, como la NTSC
        lineas = np.where((np.arange(h) % paso) < max(1, paso // 2), 1.0, 0.9).astype(np.float32)
        rng = np.random.default_rng(99)
        ruidos = []
        for _ in range(6):
            r = rng.standard_normal((h // 2 + 4, w // 2 + 4)).astype(np.float32)
            ruidos.append(np.repeat(np.repeat(r, 2, axis=0), 2, axis=1))
        _cache[clave] = (viñeta.astype(np.float32), lineas[:, None], ruidos)
    return _cache[clave]


_luts = {}


def _lut(grado, extra):
    """Curva por canal (lift, gain, gamma) precalculada para valores de 8 bits."""
    clave = (grado, tuple(sorted((extra or {}).items())))
    if clave not in _luts:
        g = dict(GRADOS[grado])
        if extra:
            g.update(extra)
        v = np.arange(256, dtype=np.float32)[:, None] / 255
        curva = v * np.array(g["gain"], np.float32) + np.array(g["lift"], np.float32) * (1 - v)
        curva = np.clip(curva, 0, 1) ** g["gamma"]
        _luts[clave] = (curva.T.copy(), g)
    return _luts[clave]


def graduar(img, grado, extra=None):
    """Aplica el color de la escena. Acepta el cuadro en uint8 (rápido) o float 0..1."""
    lut, g = _lut(grado, extra)
    if img.dtype != np.uint8:
        img = np.clip(img * 255 + 0.5, 0, 255).astype(np.uint8)
    out = np.empty(img.shape, np.float32)
    for c in range(3):
        out[..., c] = lut[c][img[..., c]]
    luma = out @ np.array([0.299, 0.587, 0.114], np.float32)
    if g["sat"] != 1.0:
        out -= luma[..., None]
        out *= g["sat"]
        out += luma[..., None]
    sombra = np.array(g["sombra"], np.float32)
    if sombra.any():
        out += sombra * ((1 - luma) ** 3)[..., None]
    if g.get("brillo"):
        out = resplandor(out, g["brillo"])
    return np.clip(out, 0, 1, out=out)


def resplandor(img, fuerza):
    """Brillo difuso en las altas luces (el recuerdo)."""
    h, w = img.shape[:2]
    altas = np.clip((img - 0.6) / 0.4, 0, 1)
    peq = Image.fromarray((altas * 255).astype(np.uint8)).resize((w // 8, h // 8), Image.BILINEAR)
    peq = peq.filter(ImageFilter.GaussianBlur(6))
    halo = np.asarray(peq.resize((w, h), Image.BILINEAR), np.float32) / 255
    halo = halo * np.array([1.0, 0.85, 0.7], np.float32)
    return img + halo * fuerza


def vhs(img, cuadro, fuerza=1.0, falla=0.0, semilla=0):
    """Sangrado de color, líneas, ruido de cinta y fallas de tracking. `falla` 0..1 añade tirones."""
    h, w = img.shape[:2]
    viñeta, lineas, ruidos = _fijos(h, w)
    rng = np.random.default_rng((semilla, cuadro))
    esc = w / 1080

    y = img @ np.array([0.299, 0.587, 0.114], np.float32)
    u = img[..., 2] - y
    v = img[..., 0] - y
    k = max(3, int(13 * esc) | 1)
    u = uniform_filter1d(u, k, axis=1)
    v = uniform_filter1d(v, k, axis=1)
    corr = max(1, int(5 * esc))
    u = np.roll(u, corr, axis=1)
    v = np.roll(v, -corr // 2 - 1, axis=1)
    y = uniform_filter1d(y, max(1, int(2 * esc) | 1), axis=1) * 0.7 + y * 0.3

    # Ruido de la cinta (granito grueso, como el de una copia de VHS).
    banco = ruidos[cuadro % len(ruidos)]
    oy, ox = int(rng.integers(0, 7)), int(rng.integers(0, 7))
    y += banco[oy:oy + h, ox:ox + w] * (0.028 * fuerza)

    img = np.stack([y + v, y - 0.509 * v - 0.194 * u, y + u], axis=-1)

    # Fallas de tracking: bandas que se corren y se llenan de nieve.
    if falla > 0 or rng.random() < 0.012 * fuerza:
        intensidad = max(falla, 0.35)
        bandas = 1 + int(intensidad * 4)
        for _ in range(bandas):
            alto = int(rng.integers(6, 60) * esc * (0.5 + intensidad))
            y0 = int(rng.integers(0, max(1, h - alto)))
            corrimiento = int(rng.normal(0, 40 * esc * intensidad))
            img[y0:y0 + alto] = np.roll(img[y0:y0 + alto], corrimiento, axis=1)
            nieve = rng.random((alto, w)) < 0.08 * intensidad
            img[y0:y0 + alto][nieve[: img[y0:y0 + alto].shape[0]]] = 0.85
    # La franja de cambio de cabeza al fondo del cuadro.
    base = int(10 * esc)
    img[h - base:] = np.roll(img[h - base:], int(12 * esc), axis=1) * 0.8 + 0.1

    img = img * (lineas * viñeta)[..., None]
    return np.clip(img, 0, 1)


def nieve(img, cuadro, cantidad):
    """Nieve de televisión (cinta sin señal)."""
    if cantidad <= 0:
        return img
    h, w = img.shape[:2]
    rng = np.random.default_rng((77, cuadro))
    g = rng.random((h // 3 + 1, w // 3 + 1)).astype(np.float32)
    g = np.repeat(np.repeat(g, 3, axis=0), 3, axis=1)[:h, :w]
    bandas = 0.75 + 0.25 * np.sin(np.arange(h, dtype=np.float32) / h * 40 + cuadro)[:, None]
    return img * (1 - cantidad) + (g * bandas)[..., None] * cantidad


# --- rótulos -----------------------------------------------------------------------------

_fuentes = {}


def fuente(ruta, tam):
    clave = (str(ruta), tam)
    if clave not in _fuentes:
        _fuentes[clave] = ImageFont.truetype(str(ruta), tam)
    return _fuentes[clave]


def poner_texto(img, lineas_texto, ruta_fuente, tam, y_centro, color="#FFE65A", borde=6,
                ancho_max=0.78, alfa=1.0, x_centro=0.5, interlineado=1.15):
    """Texto centrado con borde negro (subtítulos amarillos de VHS). Tamaños en px virtuales."""
    if alfa <= 0:
        return img
    h, w = img.shape[:2]
    esc = w / 1080
    f = fuente(ruta_fuente, max(8, int(tam * esc)))
    capa = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    renglones = []
    for linea in lineas_texto:
        palabras, actual = linea.split(), ""
        for p in palabras:
            prueba = (actual + " " + p).strip()
            if d.textlength(prueba, font=f) > w * ancho_max and actual:
                renglones.append(actual)
                actual = p
            else:
                actual = prueba
        renglones.append(actual)
    alto_linea = int(tam * esc * interlineado)
    y = int(y_centro * esc - alto_linea * len(renglones) / 2)
    color = tuple(int(c * 255) for c in hexa(color)) if isinstance(color, str) else color
    for r in renglones:
        ancho = d.textlength(r, font=f)
        x = int(w * x_centro - ancho / 2)
        d.text((x, y), r, font=f, fill=color + (255,), stroke_width=max(1, int(borde * esc)), stroke_fill=(8, 6, 10, 255))
        y += alto_linea
    arr = np.asarray(capa, np.float32) / 255
    a = arr[..., 3:4] * alfa
    return img * (1 - a) + arr[..., :3] * a


def poner_osd(img, texto, ruta_fuente, alfa=1.0, triangulo=True):
    """Letrero de videocasetera (▶ PLAY) en la esquina superior izquierda."""
    if alfa <= 0:
        return img
    h, w = img.shape[:2]
    esc = w / 1080
    capa = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    f = fuente(ruta_fuente, int(78 * esc))
    x, y = int(90 * esc), int(170 * esc)
    if triangulo:
        t = int(46 * esc)
        d.polygon([(x, y + int(14 * esc)), (x, y + int(14 * esc) + t), (x + int(t * 0.9), y + int(14 * esc) + t // 2)],
                  fill=(235, 235, 235, 255))
        x += int(70 * esc)
    d.text((x + int(3 * esc), y + int(3 * esc)), texto, font=f, fill=(0, 0, 0, 160))
    d.text((x, y), texto, font=f, fill=(235, 235, 235, 255))
    arr = np.asarray(capa, np.float32) / 255
    a = arr[..., 3:4] * alfa
    return img * (1 - a) + arr[..., :3] * a


def a_bytes(img):
    return (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)
