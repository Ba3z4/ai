"""Acabado de película y textura de gouache para el anime de los 90.

Cada cuadro de aquel anime era una foto de película de un acetato sobre un fondo pintado; por eso el look
lleva halación, grano, un poco de aberración, temblor de la cámara y polvo. Todo trabaja con arreglos
float32 RGB en 0..1.
"""

import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import gaussian_filter, map_coordinates

LUMA = np.array([0.299, 0.587, 0.114], np.float32)

# Paletas de película: (sombras, luces, saturación, desvaído). Tintes suaves, colores apagados.
PALETAS = {
    "cena": ((0.10, 0.04, 0.02), (1.00, 0.86, 0.66), 0.92, 0.05),
    "noche": ((0.02, 0.05, 0.14), (0.62, 0.78, 1.0), 0.95, 0.03),
    "recuerdo": ((0.10, 0.06, 0.02), (1.0, 0.94, 0.72), 0.95, 0.08),
    "manana": ((0.06, 0.07, 0.08), (0.94, 0.95, 0.92), 0.55, 0.12),
    "neutro": ((0.03, 0.03, 0.04), (1.0, 1.0, 1.0), 1.0, 0.02),
}


def _ruido_suave(h, w, sigma, rng):
    n = gaussian_filter(rng.standard_normal((h, w)).astype(np.float32), sigma)
    return n / (n.std() + 1e-6)


# --- textura de gouache para los fondos ------------------------------------------------------------

def gouache(img, semilla=0, mancha=0.06, cerdas=0.035, papel=0.022, temblor=2.4, vertical=True):
    """Hace que un fondo dibujado con formas planas parezca pintado con gouache sobre papel.

    Manchas de pigmento a gran escala, cerdas del pincel en franjas, grano del papel y bordes que no
    son del todo rectos.
    """
    rng = np.random.default_rng(semilla)
    h, w = img.shape[:2]
    if temblor:
        dx = _ruido_suave(h, w, 28, rng) * temblor
        dy = _ruido_suave(h, w, 28, rng) * temblor
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        img = np.stack([map_coordinates(img[..., c], [yy + dy, xx + dx], order=1, mode="nearest")
                        for c in range(3)], axis=-1)
    luma = img @ LUMA
    grande = _ruido_suave(h, w, 60, rng)
    medio = _ruido_suave(h, w, 14, rng)
    ejes = (34, 1.4) if vertical else (1.4, 34)
    franjas = gaussian_filter(rng.standard_normal((h, w)).astype(np.float32), ejes)
    franjas = franjas / (franjas.std() + 1e-6)
    fino = rng.standard_normal((h, w)).astype(np.float32)
    pigmento = grande * mancha + medio * mancha * 0.5 + franjas * cerdas + fino * papel
    # el pigmento se nota más en las zonas claras y medias que en el negro
    return np.clip(img * (1 + pigmento[..., None] * (0.35 + 0.9 * np.clip(luma, 0, 1))[..., None] * 1.0), 0, 1)


# --- acabado de película ----------------------------------------------------------------------------

def graduar(img, paleta):
    """Color de película: luces con el tinte de la escena, sombras teñidas y un desvaído que lava los negros."""
    sombras, luces, sat, desvaido = PALETAS[paleta]
    luma = (img @ LUMA)[..., None]
    img = luma + (img - luma) * sat
    img = img * np.array(luces, np.float32) + np.array(sombras, np.float32) * (1 - luma) ** 2 * 0.6
    return np.clip(desvaido + img * (1 - desvaido), 0, 1)


def halacion(img, fuerza=0.55, umbral=0.72, radio=9, color=(1.0, 0.42, 0.22)):
    """Resplandor rojizo que se derrama de las luces fuertes, como en película."""
    luma = img @ LUMA
    altas = np.clip((luma - umbral) / (1 - umbral), 0, 1) ** 1.3
    h, w = altas.shape
    peq = Image.fromarray((altas * 255).astype(np.uint8)).resize((max(w // 4, 8), max(h // 4, 8)), Image.BILINEAR)
    peq = peq.filter(ImageFilter.GaussianBlur(radio / 4))
    halo = np.asarray(peq.resize((w, h), Image.BICUBIC), np.float32) / 255
    peq2 = Image.fromarray((altas * 255).astype(np.uint8)).resize((max(w // 12, 8), max(h // 12, 8)), Image.BILINEAR)
    peq2 = peq2.filter(ImageFilter.GaussianBlur(radio / 4))
    halo2 = np.asarray(peq2.resize((w, h), Image.BICUBIC), np.float32) / 255
    color = np.array(color, np.float32)
    return np.clip(img + (halo * 0.7 + halo2 * 0.6)[..., None] * color * fuerza, 0, 1)


def grano(img, cuadro, fuerza=0.045):
    """Grano de película que cambia en cada cuadro y se nota más en las sombras."""
    rng = np.random.default_rng(1000 + cuadro)
    h, w = img.shape[:2]
    n = rng.standard_normal((h, w)).astype(np.float32)
    n = gaussian_filter(n, 0.7) * 1.6
    luma = img @ LUMA
    peso = 0.55 + 0.9 * (1 - luma)
    return np.clip(img + n[..., None] * fuerza * peso[..., None], 0, 1)


def aberracion(img, px=1.6):
    """Franjas de color en los bordes del cuadro: el rojo y el azul se corren en sentidos contrarios."""
    h, w = img.shape[:2]
    salida = img.copy()
    for canal, signo in ((0, 1), (2, -1)):
        pil = Image.fromarray((np.clip(img[..., canal], 0, 1) * 255).astype(np.uint8))
        f = 1 + signo * px / w * 2
        nw, nh = int(w * f), int(h * f)
        g = pil.resize((nw, nh), Image.BILINEAR)
        x0, y0 = (nw - w) // 2, (nh - h) // 2
        g = g.crop((x0, y0, x0 + w, y0 + h)) if f >= 1 else None
        if g is None:
            lienzo = Image.new("L", (w, h), 0)
            lienzo.paste(pil.resize((nw, nh), Image.BILINEAR), (-x0, -y0))
            g = lienzo
        salida[..., canal] = np.asarray(g, np.float32) / 255
    return salida


def temblor_de_camara(img, cuadro, px=1.4):
    """Temblor mínimo de todo el encuadre (la película en la ventanilla de la cámara)."""
    rng = np.random.default_rng(50 + cuadro)
    dx, dy = rng.normal(0, px * 0.6), rng.normal(0, px)
    h, w = img.shape[:2]
    pil = Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8))
    out = pil.transform((w, h), Image.AFFINE, (1, 0, -dx, 0, 1, -dy), resample=Image.BILINEAR)
    return np.asarray(out, np.float32) / 255


def polvo(img, cuadro):
    """Motas y pelos de acetato que aparecen uno o dos cuadros."""
    rng = np.random.default_rng(9000 + cuadro)
    h, w = img.shape[:2]
    pil = Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8))
    d = ImageDraw.Draw(pil, "RGBA")
    for _ in range(rng.poisson(2.2)):
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        r = rng.uniform(0.6, 2.2)
        oscuro = rng.random() < 0.6
        d.ellipse([x - r, y - r, x + r, y + r], fill=(10, 8, 8, 170) if oscuro else (240, 235, 225, 150))
    if rng.random() < 0.14:
        x, y = rng.uniform(0.1 * w, 0.9 * w), rng.uniform(0.1 * h, 0.9 * h)
        pts = [(x, y)]
        a = rng.uniform(0, 6.28)
        for _ in range(6):
            a += rng.normal(0, 0.7)
            x += math.cos(a) * rng.uniform(4, 10)
            y += math.sin(a) * rng.uniform(4, 10)
            pts.append((x, y))
        d.line(pts, fill=(12, 10, 10, 150), width=1)
    if rng.random() < 0.08:
        x = rng.uniform(0, w)
        d.line([(x, 0), (x + rng.normal(0, 2), h)], fill=(240, 240, 240, 34), width=1)
    return np.asarray(pil, np.float32) / 255


def viñeta(img, fuerza=0.45):
    h, w = img.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h * 0.48) / (h / 2)) ** 2)
    v = 1 - fuerza * np.clip(r - 0.55, 0, None) ** 1.6
    return img * np.clip(v, 0.3, 1)[..., None]


def acabado(img, paleta, cuadro, fuerza_grano=0.045, halo=0.55):
    """La cadena completa, en el orden de la skill: paleta, halación, grano, aberración, temblor, polvo, viñeta."""
    img = graduar(img, paleta)
    img = halacion(img, fuerza=halo)
    img = aberracion(img)
    img = grano(img, cuadro, fuerza_grano)
    img = temblor_de_camara(img, cuadro)
    img = polvo(img, cuadro)
    img = viñeta(img)
    flicker = 1 + 0.018 * math.sin(cuadro * 2.3) + 0.012 * math.sin(cuadro * 7.1)
    return np.clip(img * flicker, 0, 1)
