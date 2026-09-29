#!/usr/bin/env python3
"""Renderiza La Incisión con el guion original y el arte de ilustración oscura pintada
(vertical 9:16, 24 fps, con sonido).

Es la misma historia, plano por plano, de plan.json: la cena, el chat, las tres sombras, la parálisis,
el recuerdo, el despertar y la incisión. Solo cambia el arte: sin contornos, con volumen pintado,
pinceladas planas (Kuwahara), colores de póster y claroscuro, y la franja negra donde aparecen las
palabras de los diálogos en letra romana.

Uso (desde la carpeta la-incision):
    python3 animacion/render_pintado.py              # → la-incision-pintada.mp4 y su versión ligera
    python3 animacion/render_pintado.py --fotos      # hoja de contactos con un cuadro de cada plano
    python3 animacion/render_pintado.py --planos 1B  # vuelve a pintar solo esos planos y rearma el video
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
from PIL import Image, ImageDraw  # noqa: E402

import dibujo  # noqa: E402
import pintura  # noqa: E402
import planos  # noqa: E402
from dibujo import Lienzo, hexa  # noqa: E402
from planos import FPS, PLANOS  # noqa: E402
from render import buscar_ffmpeg  # noqa: E402

# Arte pintado en todo: sin contornos, con volumen, sin cuadros subliminales.
dibujo.Lienzo.sin_tinta = True
planos.SUBLIMINALES = False

BUILD = AQUI / "build" / "pintado"
FUENTE = AQUI / "fuentes" / "Cinzel.ttf"
PALETAS = {"cena": "cena", "celular": "cena", "noche": "noche", "recuerdo": "oro", "manana": "manana",
           "neutro": "cosmos"}
# Pinceladas más finas donde hay que leer (el chat) o ver detalle (la herida).
RADIO = {"1B": 2, "6C": 3}

# Los diálogos del guion: (plano, segundo en que empieza, segundo en que termina, texto).
DIALOGOS = [
    ("1B", 0.8, 4.4, "…Y entonces le dije a tu tía que no íbamos a poder ir el domingo."),
    ("1B", 5.25, 5.9, "¿Alex?"),
    ("1B", 6.05, 7.8, "¿Me estás escuchando, mijo?"),
    ("1C", 2.2, 3.75, "Sí, ma. Todo bien."),
]


def linea_de_tiempo():
    """[(id, inicio, duración)] tal cual el guion: los planos de plan.json con su negro y su título."""
    from generar import cargar, secuencia
    filas, _ = secuencia(cargar())
    linea, t = [], 0.0
    for f in filas:
        linea.append((f["id"], t, float(f["uso"])))
        t += f["uso"]
    return linea


def palabras_de_dialogo(linea):
    """Cada diálogo repartido en pedazos de una o dos palabras, como en la franja de la referencia."""
    inicio = {ident: ini for ident, ini, _ in linea}
    salida = []
    for ident, a, b, texto in DIALOGOS:
        palabras = texto.upper().split()
        pedazos, actual = [], []
        for p in palabras:
            actual.append(p)
            if len(" ".join(actual)) >= 7 or p[-1] in ",.?":
                pedazos.append(" ".join(actual))
                actual = []
        if actual:
            pedazos.append(" ".join(actual))
        pesos = np.array([len(x) + 3 for x in pedazos], float)
        cortes = np.r_[0, np.cumsum(pesos)] / pesos.sum() * (b - a)
        for x, c0, c1 in zip(pedazos, cortes[:-1], cortes[1:]):
            salida.append((x, inicio[ident] + a + c0, inicio[ident] + a + c1 + 0.1))
    return salida


class TituloPintado(planos.Plano):
    """Cierre: negro, el título en la franja y una línea de suturas que se cose debajo."""
    grado = "neutro"

    def dibujar(self, lz, t, tq):
        lz.camara()
        lz.velo((0, 0, 0), 1.0)
        cose = planos.tramo(t, 0.7, 1.9) * (1 - planos.tramo(t, 3.3, 3.8))
        if cose > 0:
            x0, x1, y = 300, 780, 1440
            xf = x0 + (x1 - x0) * cose
            lz.pincel([(x0, y), ((x0 + xf) / 2, y + 3), (xf, y)], 6, hexa("#8e1a22"))
            for i in range(int(11 * cose)):
                px = x0 + 22 + i * 44
                lz.pincel([(px - 7, y - 16), (px + 7, y + 16)], 4, hexa("#d8d2c4"))
        return {"titulo": planos.tramo(t, 0.35, 0.9) * (1 - planos.tramo(t, 3.3, 3.8))}


def plano_pintado(ident, dur, ancho):
    p = TituloPintado(dur, ancho) if ident == "Título" else PLANOS[ident](dur, ancho)
    p.id = ident
    return p


def acabado(img, plano, ef, t_global, cuadro, palabras):
    grado = ef.get("grado", plano.grado)
    img = pintura.pintar(img, PALETAS[grado], radio=RADIO.get(plano.id))
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


def cuadro_de(plano, lz, t, cuadro, t_global, palabras):
    tq = math.floor(t * 12 + 1e-6) / 12
    lz.nuevo(cuadro // 2)
    lz.camara()
    ef = plano.dibujar(lz, t, tq) or {}
    return acabado(lz.rgb8(), plano, ef, t_global, cuadro, palabras)


def render_plano(args):
    ident, inicio, dur, ancho, salida, ffmpeg, palabras = args
    t0 = time.time()
    plano = plano_pintado(ident, dur, ancho)
    lz = Lienzo(ancho, semilla=sum(map(ord, ident)))
    lz.hervor = 0.0
    n = int(round(dur * FPS))
    primero = int(round(inicio * FPS))
    proc = subprocess.Popen([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                             "-s", f"{lz.w}x{lz.h}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                             "-crf", "16", "-pix_fmt", "yuv420p", "-threads", "2", str(salida)], stdin=subprocess.PIPE)
    for f in range(n):
        t = f / FPS
        img = cuadro_de(plano, lz, t, primero + f, inicio + t, palabras)
        proc.stdin.write((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError(f"ffmpeg falló en el plano {ident}")
    return ident, time.time() - t0


def hoja(linea, palabras, ancho, salida):
    fotos = []
    for ident, ini, dur in linea:
        plano = plano_pintado(ident, dur, ancho)
        lz = Lienzo(ancho, semilla=sum(map(ord, ident)))
        lz.hervor = 0.0
        t = min(dur * 0.55, dur - 1 / FPS)
        img = cuadro_de(plano, lz, t, int((ini + t) * FPS), ini + t, palabras)
        im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
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
    parser.add_argument("--ancho", type=int, default=720)
    parser.add_argument("--fotos", action="store_true")
    parser.add_argument("--planos", nargs="*", help="vuelve a pintar solo estos planos")
    parser.add_argument("--procesos", type=int, default=os.cpu_count() or 2)
    parser.add_argument("--salida", type=Path, default=RAIZ / "la-incision-pintada.mp4")
    args = parser.parse_args()
    BUILD.mkdir(parents=True, exist_ok=True)
    linea = linea_de_tiempo()
    palabras = palabras_de_dialogo(linea)
    total = sum(d for _, _, d in linea)
    if args.fotos:
        hoja(linea, palabras, 360, BUILD / "contactos.png")
        print(f"Hoja de contactos → {BUILD / 'contactos.png'}")
        return
    ffmpeg = buscar_ffmpeg()
    carpeta = BUILD / f"planos-{args.ancho}"
    carpeta.mkdir(exist_ok=True)
    archivos = {ident: carpeta / f"{i:02d}-{ident.replace('í', 'i')}.mp4" for i, (ident, _, _) in enumerate(linea)}
    trabajos = [(ident, ini, dur, args.ancho, archivos[ident], ffmpeg, palabras) for ident, ini, dur in linea
                if not args.planos or ident in args.planos]
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
