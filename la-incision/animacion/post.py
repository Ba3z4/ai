"""Acabado de cada cuadro con el aspecto del terror analógico: una cinta VHS gastada vista en una
tele de tubo (negros lavados, color corrido, líneas que tiemblan, barra de zumbido, cortes de cinta,
esquinas de CRT) y los rótulos de la época (letrero de videocasetera, hora, closed captions).

Recibe el cuadro como arreglo RGB (alto, ancho, 3) y devuelve float32 en 0..1.
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy.ndimage import uniform_filter1d

from dibujo import hexa

# Guion de color: cada escena empuja el dibujo hacia su ánimo, siempre deslavado como cinta vieja.
GRADOS = {
    "cena": dict(lift=(0.04, 0.03, 0.01), gain=(1.02, 0.9, 0.7), gamma=1.1, sat=0.78, sombra=(0.02, 0.035, 0.0)),
    "celular": dict(lift=(0.01, 0.03, 0.04), gain=(0.98, 0.95, 0.9), gamma=1.05, sat=0.75, sombra=(0.0, 0.02, 0.03)),
    "noche": dict(lift=(0.01, 0.025, 0.045), gain=(0.86, 0.97, 1.08), gamma=1.05, sat=0.6, sombra=(0.0, 0.015, 0.03)),
    "recuerdo": dict(lift=(0.05, 0.04, 0.02), gain=(1.02, 0.98, 0.88), gamma=1.0, sat=0.95, sombra=(0, 0, 0), brillo=0.3),
    "manana": dict(lift=(0.045, 0.05, 0.05), gain=(0.95, 0.97, 0.92), gamma=1.0, sat=0.5, sombra=(0.0, 0.02, 0.01)),
    "neutro": dict(lift=(0, 0, 0), gain=(1, 1, 1), gamma=1.0, sat=1.0, sombra=(0, 0, 0)),
}

_cache = {}


def _fijos(h, w):
    """Viñeta con esquinas de CRT, líneas de barrido y bancos de ruido (una vez por tamaño)."""
    clave = (h, w)
    if clave not in _cache:
        esc = w / 1080
        y, x = np.mgrid[0:h, 0:w].astype(np.float32)
        dx = (x - w / 2) / (w / 2)
        dy = (y - h / 2) / (h / 2)
        r = np.sqrt(dx * dx + dy * dy * 0.55)
        viñeta = np.clip(1.0 - 0.6 * np.clip(r - 0.4, 0, None) ** 1.5, 0.2, 1.0)
        # Esquinas redondeadas de la pantalla de tubo.
        radio = 70 * esc
        cx = np.clip(np.maximum(radio - x, x - (w - 1 - radio)), 0, None)
        cy = np.clip(np.maximum(radio - y, y - (h - 1 - radio)), 0, None)
        fuera = np.sqrt(cx * cx + cy * cy) - radio
        esquinas = np.clip(1 - (fuera + 3 * esc) / (6 * esc), 0, 1)
        paso = max(2, round(h / 480))  # unas 480 líneas, como la NTSC
        lineas = np.where((np.arange(h) % paso) < max(1, paso // 2), 1.0, 0.86).astype(np.float32)
        rng = np.random.default_rng(99)
        ruidos, cromas = [], []
        for _ in range(6):
            r = rng.standard_normal((h // 2 + 4, w // 2 + 4)).astype(np.float32)
            ruidos.append(np.repeat(np.repeat(r, 2, axis=0), 2, axis=1))
            c = rng.standard_normal((2, h // 8 + 2, w // 8 + 2)).astype(np.float32)
            cromas.append(np.repeat(np.repeat(c, 8, axis=1), 8, axis=2))
        _cache[clave] = dict(viñeta=(viñeta * esquinas).astype(np.float32), lineas=lineas[:, None], ruidos=ruidos,
                             cromas=cromas, xs=np.arange(w)[None, :], filas=np.arange(h)[:, None],
                             ys=np.arange(h, dtype=np.float32))
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
    """La cinta: color corrido, ruido, líneas que tiemblan, barra de zumbido, cortes y fallas de tracking."""
    h, w = img.shape[:2]
    f = _fijos(h, w)
    rng = np.random.default_rng((semilla, cuadro))
    esc = w / 1080

    # Niveles de cinta gastada: negros lavados y blancos que no llegan a blanco.
    img = img * 0.9 + 0.04
    y = img @ np.array([0.299, 0.587, 0.114], np.float32)
    u = img[..., 2] - y
    v = img[..., 0] - y
    k = max(3, int(19 * esc) | 1)
    u = uniform_filter1d(u, k, axis=1)
    v = uniform_filter1d(v, k, axis=1)
    corr = max(1, int(8 * esc))
    u = np.roll(u, corr, axis=1)
    v = np.roll(v, -corr // 2 - 1, axis=1)
    croma = f["cromas"][(cuadro // 2) % len(f["cromas"])]
    u += croma[0, :h, :w] * 0.018 * fuerza
    v += croma[1, :h, :w] * 0.018 * fuerza
    y = uniform_filter1d(y, max(1, int(3 * esc) | 1), axis=1) * 0.75 + y * 0.25
    banco = f["ruidos"][cuadro % len(f["ruidos"])]
    oy, ox = int(rng.integers(0, 7)), int(rng.integers(0, 7))
    y += banco[oy:oy + h, ox:ox + w] * (0.032 * fuerza)
    img = np.stack([y + v, y - 0.509 * v - 0.194 * u, y + u], axis=-1)

    # Las líneas tiemblan de lado (la cinta estirada).
    ys = f["ys"]
    desvio = (np.sin(ys * 0.011 + cuadro * 0.9) * 0.9 + np.sin(ys * 0.067 + cuadro * 2.3) * 0.5
              + rng.normal(0, 0.35, h)) * 1.4 * esc * fuerza
    if falla > 0:
        desvio += np.sin(ys * 0.02 + cuadro) * 14 * esc * falla
    idx = (f["xs"] - np.round(desvio).astype(np.int64)[:, None]) % w
    img = img[f["filas"], idx]

    # Barra de zumbido que baja despacio por la pantalla.
    pos = ((cuadro * 0.55) % 100) / 100 * h * 1.5 - 0.25 * h
    barra = 1 + 0.07 * np.exp(-((ys - pos) / (0.07 * h)) ** 2)
    img *= barra[:, None, None]

    # Cortes de cinta: rayitas blancas horizontales.
    for _ in range(int(rng.integers(0, 4))):
        fy = int(rng.integers(0, h))
        fx = int(rng.integers(0, w))
        largo = int(rng.integers(20, 160) * esc)
        img[fy:fy + max(1, int(2 * esc)), fx:fx + largo] = 0.9

    # Fallas de tracking: bandas que se corren y se llenan de nieve.
    if falla > 0 or rng.random() < 0.015 * fuerza:
        intensidad = max(falla, 0.35)
        for _ in range(1 + int(intensidad * 4)):
            alto = int(rng.integers(6, 60) * esc * (0.5 + intensidad))
            y0 = int(rng.integers(0, max(1, h - alto)))
            corrimiento = int(rng.normal(0, 40 * esc * intensidad))
            img[y0:y0 + alto] = np.roll(img[y0:y0 + alto], corrimiento, axis=1)
            nieve_banda = rng.random((alto, w)) < 0.08 * intensidad
            img[y0:y0 + alto][nieve_banda[: img[y0:y0 + alto].shape[0]]] = 0.85
    # La franja de cambio de cabeza al fondo del cuadro.
    base = int(14 * esc)
    img[h - base:] = np.roll(img[h - base:], int(18 * esc), axis=1) * 0.7 + 0.12

    img = img * (f["lineas"] * f["viñeta"])[..., None]
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


# --- rótulos -----------------------------------------------------------------------------------
#
# Los textos se dibujan con Pillow en una capa del tamaño justo y se guardan en caché, porque el
# mismo letrero se repite muchos cuadros seguidos.

_fuentes = {}
_capas = {}


def fuente(ruta, tam):
    clave = (str(ruta), tam)
    if clave not in _fuentes:
        _fuentes[clave] = ImageFont.truetype(str(ruta), tam)
    return _fuentes[clave]


def _componer(img, capa, x0, y0, alfa):
    """Pone una capa RGBA (float, premultiplicada no) en (x0, y0) con transparencia."""
    if alfa <= 0 or capa is None:
        return img
    h, w = img.shape[:2]
    ch, cw = capa.shape[:2]
    xa, ya = max(0, x0), max(0, y0)
    xb, yb = min(w, x0 + cw), min(h, y0 + ch)
    if xb <= xa or yb <= ya:
        return img
    trozo = capa[ya - y0:yb - y0, xa - x0:xb - x0]
    a = trozo[..., 3:4] * alfa
    img[ya:yb, xa:xb] = img[ya:yb, xa:xb] * (1 - a) + trozo[..., :3] * a
    return img


def _renglones(d, f, lineas, ancho):
    salida = []
    for linea in lineas:
        palabras, actual = linea.split(), ""
        for p in palabras:
            prueba = (actual + " " + p).strip()
            if d.textlength(prueba, font=f) > ancho and actual:
                salida.append(actual)
                actual = p
            else:
                actual = prueba
        salida.append(actual)
    return salida


def _color(c):
    return tuple(int(x * 255) for x in hexa(c)) if isinstance(c, str) else tuple(c)


def _capa_texto(w, lineas, ruta, tam, color, borde, ancho_max, interlineado, caja):
    clave = ("t", w, tuple(lineas), str(ruta), tam, color, borde, ancho_max, interlineado, caja)
    if clave in _capas:
        return _capas[clave]
    esc = w / 1080
    f = fuente(ruta, max(8, int(tam * esc)))
    medir = ImageDraw.Draw(Image.new("L", (1, 1)))
    renglones = _renglones(medir, f, lineas, w * ancho_max)
    alto_linea = int(tam * esc * interlineado)
    anchos = [medir.textlength(r, font=f) for r in renglones]
    margen = int((borde + 18) * esc) if caja else int(borde * esc) + 2
    cw = int(max(anchos) + 2 * margen) + 2
    chh = alto_linea * len(renglones) + 2 * margen
    capa = Image.new("RGBA", (cw, chh), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    rgb = _color(color)
    for i, (r, an) in enumerate(zip(renglones, anchos)):
        x = (cw - an) / 2
        y = margen + i * alto_linea
        if caja:
            d.rectangle([x - 14 * esc, y - 4 * esc, x + an + 14 * esc, y + alto_linea], fill=(0, 0, 0, 235))
            d.text((x, y), r, font=f, fill=rgb + (255,))
        else:
            d.text((x, y), r, font=f, fill=rgb + (255,), stroke_width=max(1, int(borde * esc)) if borde else 0,
                   stroke_fill=(8, 6, 10, 255))
    arr = np.asarray(capa, np.float32) / 255
    _capas[clave] = arr
    if len(_capas) > 64:
        _capas.pop(next(iter(_capas)))
    return arr


def poner_texto(img, lineas_texto, ruta_fuente, tam, y_centro, color="#FFE65A", borde=6,
                ancho_max=0.78, alfa=1.0, x_centro=0.5, interlineado=1.15, caja=False):
    """Texto centrado en (x_centro, y_centro). caja=True: letras sobre cajas negras (closed caption)."""
    if alfa <= 0:
        return img
    h, w = img.shape[:2]
    capa = _capa_texto(w, lineas_texto, ruta_fuente, tam, color, borde, ancho_max, interlineado, caja)
    x0 = int(w * x_centro - capa.shape[1] / 2)
    y0 = int(y_centro * w / 1080 - capa.shape[0] / 2)
    return _componer(img, capa, x0, y0, alfa)


def poner_osd(img, texto, ruta_fuente, alfa=1.0, simbolo="play", y=170, color=(235, 235, 235), tam=78, x=90):
    """Letrero de videocasetera (▶ PLAY, ■ STOP, la hora) arriba a la izquierda."""
    if alfa <= 0:
        return img
    h, w = img.shape[:2]
    esc = w / 1080
    clave = ("osd", w, texto, str(ruta_fuente), simbolo, tuple(color), tam)
    if clave not in _capas:
        f = fuente(ruta_fuente, int(tam * esc))
        medir = ImageDraw.Draw(Image.new("L", (1, 1)))
        ancho = int(medir.textlength(texto, font=f) + 90 * esc)
        capa = Image.new("RGBA", (ancho, int(tam * esc * 1.3)), (0, 0, 0, 0))
        d = ImageDraw.Draw(capa)
        px = 0
        t = int(tam * 0.6 * esc)
        arriba = int(tam * 0.18 * esc)
        if simbolo == "play":
            d.polygon([(0, arriba), (0, arriba + t), (int(t * 0.9), arriba + t // 2)], fill=tuple(color) + (255,))
            px = int(tam * 0.9 * esc)
        elif simbolo == "stop":
            d.rectangle([0, arriba, int(t * 0.85), arriba + int(t * 0.85)], fill=tuple(color) + (255,))
            px = int(tam * 0.9 * esc)
        d.text((px + int(3 * esc), int(3 * esc)), texto, font=f, fill=(0, 0, 0, 170))
        d.text((px, 0), texto, font=f, fill=tuple(color) + (255,))
        _capas[clave] = np.asarray(capa, np.float32) / 255
    return _componer(img, _capas[clave], int(x * esc), int(y * esc), alfa)


def a_bytes(img):
    return (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)
