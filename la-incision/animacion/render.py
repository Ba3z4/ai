#!/usr/bin/env python3
"""Renderiza La Incisión como caricatura tétrica de los 90 (vertical 9:16, 24 fps, con sonido).

Uso (desde la carpeta la-incision):
    python3 animacion/render.py                  # corto completo 1080×1920 → la-incision-animada.mp4
    python3 animacion/render.py --ancho 540      # borrador rápido a media resolución
    python3 animacion/render.py --planos 3A 3B   # solo esos planos (quedan en animacion/build/)
    python3 animacion/render.py --fotos          # hoja de contactos con un cuadro de cada plano
    python3 animacion/render.py --solo-audio     # vuelve a mezclar el sonido sobre los planos ya hechos

Necesita Python 3 con numpy, scipy, pycairo y Pillow (pip install numpy scipy pycairo pillow) y ffmpeg.
Las duraciones salen de plan.json; antes del plano 1A va un gancho de 1.5 s para TikTok.
"""

import argparse
import math
import os
import shutil
import subprocess
import sys
import time
from multiprocessing import Pool
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(RAIZ / "herramientas"))

from PIL import Image, ImageDraw  # noqa: E402

import post  # noqa: E402
from dibujo import Lienzo  # noqa: E402
from planos import FPS, GANCHO, PLANOS  # noqa: E402

BUILD = AQUI / "build"
FUENTE_TITULO = AQUI / "fuentes" / "Creepster-Regular.ttf"
FUENTE_VHS = AQUI / "fuentes" / "VT323-Regular.ttf"
FUENTES_SUBS = (
    "C:/Windows/Fonts/arialbd.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
)


def fuente_subtitulos():
    return next((Path(f) for f in FUENTES_SUBS if Path(f).is_file()), FUENTE_VHS)


def buscar_ffmpeg():
    ruta = shutil.which("ffmpeg")
    if ruta:
        return ruta
    try:
        import imageio_ffmpeg
    except ImportError:
        sys.exit("No encontré ffmpeg. Instálalo (Windows: winget install Gyan.FFmpeg) o corre: pip install imageio-ffmpeg")
    return imageio_ffmpeg.get_ffmpeg_exe()


def linea_de_tiempo():
    """[(id, inicio, duración)] con el gancho y los extras (negro y título) de plan.json."""
    from generar import cargar, secuencia
    filas, _ = secuencia(cargar())
    linea, t = [("Gancho", 0.0, GANCHO)], GANCHO
    for f in filas:
        linea.append((f["id"], t, float(f["uso"])))
        t += f["uso"]
    return linea


def acabado(img, plano, ef, cuadro):
    """Color, efectos de cinta y rótulos de un cuadro."""
    img = post.graduar(img, ef.get("grado", plano.grado))
    if ef.get("negativo"):
        img = 1 - img
    if ef.get("blanco", 0) > 0:
        b = ef["blanco"]
        img = img * (1 - b) + b
    if ef.get("titulo", 0) > 0:
        img = post.poner_texto(img, ["LA INCISIÓN"], FUENTE_TITULO, 150, 930, color="#E6E0D2", borde=3,
                               alfa=ef["titulo"], ancho_max=0.95)
    img = post.nieve(img, cuadro, ef.get("nieve", 0))
    img = post.vhs(img, cuadro, fuerza=plano.vhs, falla=ef.get("falla", 0))
    if ef.get("negro", 0) > 0:
        img = img * (1 - ef["negro"])
    for lineas, alfa in ef.get("subtitulos", []):
        img = post.poner_texto(img, lineas, fuente_subtitulos(), 50, 1400, alfa=alfa, ancho_max=0.8)
    if ef.get("osd"):
        texto, alfa = ef["osd"]
        img = post.poner_osd(img, texto, FUENTE_VHS, alfa=alfa)
    if ef.get("fecha"):
        texto, alfa = ef["fecha"]
        img = post.poner_texto(img, [texto], FUENTE_VHS, 70, 300, color="#F2A33A", borde=3, alfa=alfa, x_centro=0.3)
    return img


def cuadro_de(plano, lz, t, dibujo, cuadro):
    tq = math.floor(t * 12 + 1e-6) / 12
    lz.nuevo(dibujo)
    lz.camara()
    ef = plano.dibujar(lz, t, tq) or {}
    return acabado(lz.rgb8(), plano, ef, cuadro)


def render_plano(args):
    ident, inicio, dur, ancho, salida, ffmpeg = args
    t0 = time.time()
    plano = PLANOS[ident](dur, ancho)
    lz = Lienzo(ancho, semilla=sum(map(ord, ident)))
    n = int(round(dur * FPS))
    primero = int(round(inicio * FPS))
    proc = subprocess.Popen([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                             "-s", f"{lz.w}x{lz.h}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                             "-crf", "17", "-pix_fmt", "yuv420p", "-threads", "2", str(salida)], stdin=subprocess.PIPE)
    for f in range(n):
        t = f / FPS
        img = cuadro_de(plano, lz, t, (primero + f) // 2, primero + f)
        proc.stdin.write(post.a_bytes(img).tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError(f"ffmpeg falló en el plano {ident}")
    return ident, time.time() - t0


def hoja_de_contactos(linea, ancho, salida, momentos=(0.5,)):
    miniaturas = []
    for ident, inicio, dur in linea:
        plano = PLANOS[ident](dur, ancho)
        lz = Lienzo(ancho, semilla=sum(map(ord, ident)))
        for m in momentos:
            t = min(dur * m, dur - 1 / FPS)
            cuadro = int(round((inicio + t) * FPS))
            img = cuadro_de(plano, lz, t, cuadro // 2, cuadro)
            im = Image.fromarray(post.a_bytes(img))
            ImageDraw.Draw(im).text((10, 8), f"{ident} {t:.1f}s", fill=(255, 255, 0))
            miniaturas.append(im)
        print(f"  {ident}", flush=True)
    w, h = miniaturas[0].size
    cols = 6
    filas = math.ceil(len(miniaturas) / cols)
    hoja = Image.new("RGB", (w * cols, h * filas))
    for i, im in enumerate(miniaturas):
        hoja.paste(im, ((i % cols) * w, (i // cols) * h))
    hoja.save(salida)
    return salida


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--ancho", type=int, default=1080, help="ancho del video (1080 para el final)")
    parser.add_argument("--planos", nargs="*", help="solo estos planos")
    parser.add_argument("--fotos", action="store_true", help="hoja de contactos en vez de video")
    parser.add_argument("--momentos", type=float, nargs="*", default=[0.5], help="momentos (0..1) para --fotos")
    parser.add_argument("--solo-audio", action="store_true", help="solo rehace el sonido y el montaje")
    parser.add_argument("--procesos", type=int, default=os.cpu_count() or 2)
    parser.add_argument("--salida", type=Path, default=RAIZ / "la-incision-animada.mp4")
    args = parser.parse_args()

    linea = linea_de_tiempo()
    if args.planos:
        faltan = [p for p in args.planos if p not in PLANOS]
        if faltan:
            sys.exit(f"No conozco estos planos: {', '.join(faltan)}")
    elegidos = [x for x in linea if not args.planos or x[0] in args.planos]
    BUILD.mkdir(exist_ok=True)
    if args.fotos:
        salida = BUILD / "contactos.png"
        print(f"Hoja de contactos → {salida}")
        hoja_de_contactos(elegidos, args.ancho, salida, args.momentos)
        return

    ffmpeg = buscar_ffmpeg()
    carpeta = BUILD / f"planos-{args.ancho}"
    carpeta.mkdir(exist_ok=True)
    archivo = {ident: carpeta / f"{i:02d}-{ident.replace('í', 'i')}.mp4" for i, (ident, _, _) in enumerate(linea)}
    if not args.solo_audio:
        trabajos = [(ident, ini, dur, args.ancho, archivo[ident], ffmpeg) for ident, ini, dur in elegidos]
        trabajos.sort(key=lambda x: -x[2])
        t0 = time.time()
        print(f"Renderizando {len(trabajos)} planos a {args.ancho} px con {args.procesos} procesos…", flush=True)
        with Pool(args.procesos) as pool:
            for ident, seg in pool.imap_unordered(render_plano, trabajos):
                print(f"  {ident:>6} listo en {seg:.0f} s", flush=True)
        print(f"Planos en {time.time() - t0:.0f} s")
        if args.planos:
            return

    faltan = [ident for ident, _, _ in linea if not archivo[ident].is_file()]
    if faltan:
        sys.exit(f"Faltan planos por renderizar: {', '.join(faltan)}")
    import sonido
    audio = BUILD / "sonido.wav"
    print("Sintetizando el sonido…", flush=True)
    sonido.generar(linea, audio)
    lista = BUILD / "lista.txt"
    lista.write_text("".join(f"file '{archivo[ident].as_posix()}'\n" for ident, _, _ in linea), encoding="utf-8")
    comando = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lista),
               "-i", str(audio)]
    if args.ancho != 1080:
        comando += ["-vf", "scale=1080:1920:flags=lanczos", "-c:v", "libx264", "-crf", "18", "-preset", "medium",
                    "-pix_fmt", "yuv420p"]
    else:
        comando += ["-c:v", "copy"]
    comando += ["-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(args.salida)]
    subprocess.run(comando, check=True)
    print(f"Listo: {args.salida}")


if __name__ == "__main__":
    main()
