#!/usr/bin/env python3
"""Renderiza La Incisión como cinta de terror analógico con dibujos de caricatura de los 90
(vertical 9:16, 24 fps, con sonido).

Uso (desde la carpeta la-incision):
    python3 animacion/render.py                  # corto completo → la-incision-animada.mp4 (1080×1920)
    python3 animacion/render.py --ancho 360      # borrador rápido
    python3 animacion/render.py --planos 3A 3B   # solo esos planos (quedan en animacion/build/)
    python3 animacion/render.py --fotos          # hoja de contactos con un cuadro de cada plano
    python3 animacion/render.py --solo-audio     # vuelve a mezclar el sonido sobre los planos ya hechos
    python3 animacion/render.py --portada        # portada para TikTok → portada-tiktok.png
    python3 animacion/render.py --ligero         # versión de menos de 30 MB con los planos ya hechos

Necesita Python 3 con numpy, scipy, pycairo y Pillow (pip install numpy scipy pycairo pillow) y ffmpeg.
Las duraciones salen de plan.json. Además de los planos del guion, la cinta lleva un gancho de 1.5 s para
TikTok, barras de color al empezar y un aviso de emergencia antes del título.
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

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

import post  # noqa: E402
from dibujo import Lienzo  # noqa: E402
from planos import AVISO_DUR, BARRAS, FPS, GANCHO, PLANOS  # noqa: E402

BUILD = AQUI / "build"
FUENTE_VHS = AQUI / "fuentes" / "VT323-Regular.ttf"
FUENTES_CC = (
    "C:/Windows/Fonts/consolab.ttf",
    "C:/Windows/Fonts/courbd.ttf",
    "/System/Library/Fonts/Menlo.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf",
)


def fuente_cc():
    """Letra monoespaciada para los closed captions (si no hay, la de la videocasetera)."""
    return next((Path(f) for f in FUENTES_CC if Path(f).is_file()), FUENTE_VHS)


FUENTES = {"vhs": FUENTE_VHS}


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
    """[(id, inicio, duración)]: gancho, barras de color, los planos y extras de plan.json, el aviso y el título."""
    from generar import cargar, secuencia
    filas, _ = secuencia(cargar())
    linea, t = [("Gancho", 0.0, GANCHO), ("Barras", GANCHO, BARRAS)], GANCHO + BARRAS
    for f in filas:
        if f["id"] == "Título":
            linea.append(("Aviso", t, AVISO_DUR))
            t += AVISO_DUR
        linea.append((f["id"], t, float(f["uso"])))
        t += f["uso"]
    return linea


# La hora de la cinta en cada escena: la madrugada se salta casi tres horas (tiempo perdido).
RELOJ = {"1": ("28 SEP", "21:47:03"), "2": ("29 SEP", "03:17:22"), "3": ("29 SEP", "03:18:40"),
         "5E": ("29 SEP", "05:58:14"), "6": ("29 SEP", "07:40:51")}
_inicios = {}


def reloj(ident, t_global):
    """Texto y color del contador de la cinta, o None si en ese plano no se ve."""
    if not ident[:1].isdigit() or ident.startswith("4"):
        return None
    cuadro = int(t_global * FPS)
    rng = np.random.default_rng((5, cuadro // 3))
    if ident in ("5A", "5B", "5C", "5D"):
        basura = "".join(rng.choice(list("0123456789?#")) for _ in range(6))
        return f"?? ??? {basura[:2]}:{basura[2:4]}:{basura[4:]}", (235, 60, 60)
    clave = "5E" if ident in ("5E", "5F") else ident[0]
    if not _inicios:
        for i, ini, _ in linea_de_tiempo():
            k = "5E" if i in ("5E", "5F") else i[:1]
            _inicios[k] = min(_inicios.get(k, ini), ini)
    fecha, hora = RELOJ[clave]
    hh, mm, ss = map(int, hora.split(":"))
    seg = hh * 3600 + mm * 60 + ss + int(t_global - _inicios[clave])
    texto = f"{fecha} {seg // 3600 % 24:02d}:{seg // 60 % 60:02d}:{seg % 60:02d}"
    if clave == "3" and rng.random() < 0.18:
        pos = int(rng.integers(7, len(texto)))
        texto = texto[:pos] + str(rng.choice(list("?#8"))) + texto[pos + 1:]
    rojo = clave == "5E" and t_global - _inicios[clave] < 1.8
    return texto, (235, 60, 60) if rojo else (235, 235, 235)


def acabado(img, plano, ef, cuadro):
    """Color, rótulos grabados en la cinta, efectos de cinta y letreros de la videocasetera."""
    img = post.graduar(img, ef.get("grado", plano.grado))
    if ef.get("negativo"):
        img = 1 - img
    if ef.get("blanco", 0) > 0:
        b = ef["blanco"]
        img = img * (1 - b) + b
    for tj in ef.get("tarjetas", []):
        img = post.poner_texto(img, tj["lineas"], FUENTES[tj["fuente"]], tj["tam"], tj["y"], color=tj["color"],
                               borde=0 if tj["caja"] else 3, alfa=tj["alfa"], ancho_max=tj["ancho_max"],
                               caja=tj["caja"])
    img = post.nieve(img, cuadro, ef.get("nieve", 0))
    img = post.vhs(img, cuadro, fuerza=plano.vhs, falla=ef.get("falla", 0))
    if ef.get("negro", 0) > 0:
        img = img * (1 - ef["negro"])
    for lineas, alfa in ef.get("subtitulos", []):
        img = post.poner_texto(img, [x.upper() for x in lineas], fuente_cc(), 44, 1400, color="#FFFFFF", alfa=alfa,
                               ancho_max=0.82, caja=True, interlineado=1.3)
    if ef.get("osd"):
        texto, alfa = ef["osd"]
        img = post.poner_osd(img, texto, FUENTE_VHS, alfa=alfa, simbolo="stop" if texto == "STOP" else "play")
    hora = reloj(getattr(plano, "id", ""), cuadro / FPS)
    if hora:
        img = post.poner_osd(img, hora[0], FUENTE_VHS, simbolo=None, y=250, color=hora[1], tam=62)
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
    plano.id = ident
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
        plano.id = ident
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


def portada(ancho, salida):
    """Portada para TikTok: las máscaras encima de su cara con el título."""
    plano = PLANOS["3A"](6, ancho)
    lz = Lienzo(ancho, semilla=7)
    img = cuadro_de(plano, lz, 4.6, 55, 1300)
    img = post.poner_texto(img, ["LA INCISIÓN"], FUENTE_VHS, 200, 1480, color="#E6E0D2", borde=6, ancho_max=0.95)
    Image.fromarray(post.a_bytes(img)).save(salida)
    return salida


def ligero(ffmpeg, lista, audio, salida, duracion, megas=28):
    """Versión de menos de 30 MB en 1080×1920 (dos pasadas, cuidando las escenas oscuras) para mandarla por chat."""
    kbps = int(megas * 8192 / duracion) - 128
    base = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lista)]
    video = ["-vf", "scale=1080:1920:flags=lanczos", "-c:v", "libx264", "-preset", "slower", "-b:v", f"{kbps}k",
             "-x264-params", "aq-mode=3:aq-strength=0.9", "-pix_fmt", "yuv420p", "-r", str(FPS),
             "-passlogfile", str(BUILD / "ligero")]
    subprocess.run(base + video + ["-pass", "1", "-an", "-f", "mp4", os.devnull], check=True)
    subprocess.run(base + ["-i", str(audio)] + video + ["-pass", "2", "-c:a", "aac", "-b:a", "128k", "-shortest",
                                                         "-movflags", "+faststart", str(salida)], check=True)
    return salida


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--ancho", type=int, default=720,
                        help="ancho al que se dibuja (720 por defecto: se ve más a cinta; el video final sale a 1080)")
    parser.add_argument("--planos", nargs="*", help="solo estos planos")
    parser.add_argument("--fotos", action="store_true", help="hoja de contactos en vez de video")
    parser.add_argument("--momentos", type=float, nargs="*", default=[0.5], help="momentos (0..1) para --fotos")
    parser.add_argument("--solo-audio", action="store_true", help="solo rehace el sonido y el montaje")
    parser.add_argument("--portada", action="store_true", help="solo la portada para TikTok (PNG)")
    parser.add_argument("--ligero", action="store_true",
                        help="solo la versión de menos de 30 MB a partir de los planos y el sonido ya hechos")
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
    if args.portada:
        print(f"Portada → {portada(args.ancho, RAIZ / 'portada-tiktok.png')}")
        return
    if args.fotos:
        salida = BUILD / "contactos.png"
        print(f"Hoja de contactos → {salida}")
        hoja_de_contactos(elegidos, args.ancho, salida, args.momentos)
        return

    ffmpeg = buscar_ffmpeg()
    carpeta = BUILD / f"planos-{args.ancho}"
    carpeta.mkdir(exist_ok=True)
    archivo = {ident: carpeta / f"{i:02d}-{ident.replace('í', 'i')}.mp4" for i, (ident, _, _) in enumerate(linea)}
    if not args.solo_audio and not args.ligero:
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
    lista = BUILD / "lista.txt"
    lista.write_text("".join(f"file '{archivo[ident].as_posix()}'\n" for ident, _, _ in linea), encoding="utf-8")
    duracion = sum(d for _, _, d in linea)
    salida_ligera = args.salida.with_name(args.salida.stem + "-ligera.mp4")
    if args.ligero:
        if not audio.is_file():
            sonido.generar(linea, audio)
        print(f"Listo: {ligero(ffmpeg, lista, audio, salida_ligera, duracion)}")
        return
    print("Sintetizando el sonido…", flush=True)
    sonido.generar(linea, audio)
    comando = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lista),
               "-i", str(audio)]
    if args.ancho != 1080:
        comando += ["-vf", "scale=1080:1920:flags=bicubic"]
    # El ruido de cinta pesa mucho: se limita el bitrate para que el archivo se pueda subir a TikTok (~100 MB).
    comando += ["-c:v", "libx264", "-preset", "slow", "-crf", "20", "-maxrate", "7M", "-bufsize", "14M",
                "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-shortest",
                "-movflags", "+faststart", str(args.salida)]
    subprocess.run(comando, check=True)
    print(f"Listo: {args.salida}")
    print(f"Versión ligera: {ligero(ffmpeg, lista, audio, salida_ligera, duracion)}")


if __name__ == "__main__":
    main()
