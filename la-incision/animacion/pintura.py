"""Acabado de pintura para la versión «Cómo abrir a un humano»: ilustración oscura con pinceladas
planas (filtro Kuwahara), colores tipo póster, textura de lienzo, y la franja negra con la palabra
que dice el narrador, como en los videos de «cómo encerrar a un ángel».

Todas las funciones reciben y devuelven arreglos float32 RGB (alto, ancho, 3) en 0..1.
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy.ndimage import uniform_filter

# Paletas por ilustración: (lift, gain, saturación, tinte de sombras, tinte de luces).
PALETAS = {
    "cosmos": ((0.0, 0.0, 0.02), (1.05, 0.98, 1.1), 1.25, (0.03, 0.0, 0.06), (0.0, 0.02, 0.05)),
    "cena": ((0.02, 0.0, 0.0), (1.12, 0.95, 0.78), 1.2, (0.05, 0.01, 0.0), (0.06, 0.03, 0.0)),
    "noche": ((0.0, 0.01, 0.04), (0.85, 0.98, 1.2), 1.15, (0.0, 0.02, 0.06), (0.0, 0.03, 0.06)),
    "sangre": ((0.02, 0.0, 0.01), (1.15, 0.85, 0.9), 1.25, (0.06, 0.0, 0.02), (0.05, 0.0, 0.01)),
    "oro": ((0.03, 0.02, 0.0), (1.12, 1.02, 0.78), 1.2, (0.04, 0.03, 0.0), (0.08, 0.05, 0.0)),
    "manana": ((0.03, 0.03, 0.03), (1.0, 0.98, 0.92), 0.85, (0.01, 0.02, 0.02), (0.04, 0.04, 0.02)),
}

_fijos = {}


def _base(h, w):
    if (h, w) not in _fijos:
        rng = np.random.default_rng(7)
        y, x = np.mgrid[0:h, 0:w].astype(np.float32)
        r = np.sqrt(((x - w / 2) / (w / 2)) ** 2 + ((y - h * 0.42) / (h / 2)) ** 2 * 0.7)
        viñeta = np.clip(1 - 0.75 * np.clip(r - 0.35, 0, None) ** 1.4, 0.15, 1).astype(np.float32)
        # Textura de lienzo: trama fina más manchas grandes.
        fino = rng.standard_normal((h, w)).astype(np.float32)
        fino = uniform_filter(fino, 2)
        grueso = uniform_filter(rng.standard_normal((h // 8 + 1, w // 8 + 1)).astype(np.float32), 3)
        grueso = np.repeat(np.repeat(grueso, 8, axis=0), 8, axis=1)[:h, :w]
        lienzo = (fino * 0.035 + grueso * 0.05).astype(np.float32)
        _fijos[(h, w)] = (viñeta, lienzo)
    return _fijos[(h, w)]


def kuwahara(img, radio):
    """Filtro de Kuwahara: cada píxel toma el color promedio del cuadrante más parejo (pincelada plana)."""
    if radio < 2:
        return img
    k = radio + 1
    luma = img @ np.array([0.299, 0.587, 0.114], np.float32)
    media = uniform_filter(img, size=(k, k, 1), mode="reflect")
    ml = uniform_filter(luma, size=k, mode="reflect")
    var = uniform_filter(luma * luma, size=k, mode="reflect") - ml * ml
    d = radio // 2
    salida = np.empty_like(img)
    mejor = np.full(luma.shape, np.inf, np.float32)
    for dy, dx in ((-d, -d), (-d, d), (d, -d), (d, d)):
        v = np.roll(var, (dy, dx), axis=(0, 1))
        m = np.roll(media, (dy, dx), axis=(0, 1))
        cual = v < mejor
        salida[cual] = m[cual]
        mejor = np.where(cual, v, mejor)
    return salida


def pintar(img, paleta="cosmos", radio=None, niveles=9, cuadro=0):
    """Convierte el dibujo en ilustración: pinceladas, color de la paleta, póster y lienzo."""
    h, w = img.shape[:2]
    if img.dtype == np.uint8:
        img = img.astype(np.float32) / 255
    radio = radio if radio is not None else max(3, round(w / 120))
    img = kuwahara(img, radio)
    lift, gain, sat, sombra, luz = PALETAS[paleta]
    img = img * np.array(gain, np.float32) + np.array(lift, np.float32) * (1 - img)
    luma = img @ np.array([0.299, 0.587, 0.114], np.float32)
    img = luma[..., None] + (img - luma[..., None]) * sat
    img += np.array(sombra, np.float32) * ((1 - luma) ** 2)[..., None] + np.array(luz, np.float32) * (luma ** 2)[..., None]
    # Contraste en S y colores de póster con un poco de difuminado entre bandas.
    img = np.clip(img, 0, 1)
    img = img * img * (3 - 2 * img) * 0.55 + img * 0.45
    img = np.round(img * (niveles - 1)) / (niveles - 1) * 0.7 + img * 0.3
    viñeta, lienzo = _base(h, w)
    img = img * viñeta[..., None] + lienzo[..., None] * (0.6 + 0.4 * luma[..., None])
    return np.clip(img, 0, 1)


def resplandor(img, fuerza=0.35, umbral=0.62):
    """Brillo que se derrama de las luces fuertes (estrellas, lámparas, la luz del recuerdo)."""
    h, w = img.shape[:2]
    altas = np.clip((img - umbral) / (1 - umbral), 0, 1)
    peq = Image.fromarray((altas * 255).astype(np.uint8)).resize((w // 6, h // 6), Image.BILINEAR)
    peq = peq.filter(ImageFilter.GaussianBlur(5))
    halo = np.asarray(peq.resize((w, h), Image.BILINEAR), np.float32) / 255
    return np.clip(img + halo * fuerza, 0, 1)


# --- la franja de la palabra ------------------------------------------------------------------

BANDA_Y = 0.70   # centro de la franja negra, en proporción del alto
BANDA_ALTO = 0.058

_fuentes = {}
_capas = {}


def _fuente(ruta, tam, peso="Bold"):
    clave = (str(ruta), tam, peso)
    if clave not in _fuentes:
        f = ImageFont.truetype(str(ruta), tam)
        try:
            f.set_variation_by_name(peso)
        except Exception:
            pass
        _fuentes[clave] = f
    return _fuentes[clave]


def banda(img):
    """Franja negra horizontal con bordes difuminados donde aparece la palabra."""
    h, w = img.shape[:2]
    clave = ("banda", h, w)
    if clave not in _capas:
        ys = np.arange(h, dtype=np.float32) / h
        centro, medio = BANDA_Y, BANDA_ALTO / 2
        dist = np.abs(ys - centro)
        alfa = np.clip(1 - (dist - medio) / 0.022, 0, 1)
        alfa = np.maximum(alfa, 0.55 * np.clip(1 - (dist - medio) / 0.07, 0, 1))
        _capas[clave] = alfa.astype(np.float32)[:, None, None]
    a = _capas[clave]
    return img * (1 - a) + 0.015 * a


def palabra(img, texto, ruta_fuente, alfa=1.0, tam=46, color=(242, 238, 230), gris=0.0):
    """La palabra (o dos) que dice el narrador, centrada en la franja. gris 0..1 la apaga como en el original."""
    if not texto or alfa <= 0:
        return img
    h, w = img.shape[:2]
    esc = w / 1080
    clave = ("palabra", w, texto, str(ruta_fuente), tam, color)
    if clave not in _capas:
        f = _fuente(ruta_fuente, max(10, int(tam * esc)))
        medir = ImageDraw.Draw(Image.new("L", (1, 1)))
        caja = medir.textbbox((0, 0), texto, font=f)
        cw, ch = caja[2] - caja[0] + int(40 * esc), caja[3] - caja[1] + int(40 * esc)
        capa = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        d = ImageDraw.Draw(capa)
        d.text((int(20 * esc) - caja[0], int(20 * esc) - caja[1]), texto, font=f, fill=tuple(color) + (255,))
        brillo = capa.filter(ImageFilter.GaussianBlur(6 * esc))
        arr = np.asarray(capa, np.float32) / 255
        glow = np.asarray(brillo, np.float32) / 255
        _capas[clave] = (arr, glow)
    arr, glow = _capas[clave]
    ch, cw = arr.shape[:2]
    x0 = (w - cw) // 2
    y0 = int(h * BANDA_Y - ch / 2)
    zona = img[y0:y0 + ch, x0:x0 + cw]
    tono = 1 - 0.55 * gris
    a = arr[..., 3:4] * alfa
    g = glow[..., 3:4] * 0.35 * alfa
    zona = zona * (1 - g) + g * 0.9
    zona = zona * (1 - a) + arr[..., :3] * tono * a
    img[y0:y0 + ch, x0:x0 + cw] = zona
    return img


def palabra_rota(img, texto, ruta_fuente, cuadro, alfa=1.0, tam=50):
    """Texto que se descompone (el narrador pierde la forma al final)."""
    rng = np.random.default_rng(cuadro)
    letras = list(texto)
    for i in range(len(letras)):
        if letras[i] != " " and rng.random() < 0.45:
            letras[i] = rng.choice(list("IEAQYHXVW"))
    img = palabra(img, "".join(letras), ruta_fuente, alfa=alfa, tam=tam, color=(210, 200, 200))
    h, w = img.shape[:2]
    y0 = int(h * (BANDA_Y - BANDA_ALTO))
    for _ in range(4):
        a = int(rng.integers(y0, y0 + int(h * BANDA_ALTO * 2)))
        b = a + int(rng.integers(3, 14))
        img[a:b] = np.roll(img[a:b], int(rng.normal(0, 30)), axis=1)
    return img
