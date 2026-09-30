#!/usr/bin/env python3
"""Renderiza La Incisión como anime japonés de terror de los 90 (vertical 9:16, 24 fps, con sonido).

Todo se dibuja y se sintetiza con código, sin herramientas de IA externas ni imágenes de referencia: fondos
de gouache, acetatos con sombra de borde duro y tinta, animación limitada, acabado de película y una banda
sonora sintetizada. El guion es el original, plano por plano.

Uso (desde la carpeta la-incision):
    python3 -m anime90.render                  # → la-incision-anime90.mp4 y su versión ligera
    python3 -m anime90.render --fotos          # hoja de contactos con dos cuadros de cada plano
    python3 -m anime90.render --planos 1A 6C   # vuelve a pintar solo esos planos y rearma el video
    python3 -m anime90.render --solo-audio     # solo rehace el sonido y vuelve a armar
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

import numpy as np
from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "herramientas"))

from anime90 import estilo  # noqa: E402
from anime90.planos import AL, AN, PLANOS  # noqa: E402

FPS = 24
BUILD = RAIZ / "anime90" / "build"
FUENTE_TITULO = RAIZ / "animacion" / "fuentes" / "Cinzel.ttf"
FUENTE_SUB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# Los diálogos del guion: (plano, desde, hasta, texto en una o dos líneas).
SUBTITULOS = [
    ("1B", 0.8, 4.4, "…y entonces le dije a tu tía que no íbamos\na poder ir el domingo."),
    ("1B", 5.25, 5.9, "¿Alex?"),
    ("1B", 6.05, 7.8, "¿Me estás escuchando, mijo?"),
    ("1C", 2.2, 3.75, "Sí, ma. Todo bien."),
]


def buscar_ffmpeg():
    return shutil.which("ffmpeg") or "ffmpeg"


def linea_de_tiempo():
    """[(id, inicio, duración)] tal cual el guion: los planos de plan.json con su negro y su título."""
    from generar import cargar, secuencia
    filas, _ = secuencia(cargar())
    linea, t = [], 0.0
    for f in filas:
        linea.append((f["id"], t, float(f["uso"])))
        t += f["uso"]
    return linea


_fuentes = {}


def _fuente(ruta, tam, peso=None):
    clave = (str(ruta), tam, peso)
    if clave not in _fuentes:
        f = ImageFont.truetype(str(ruta), tam)
        if peso:
            try:
                f.set_variation_by_name(peso)
            except Exception:
                pass
        _fuentes[clave] = f
    return _fuentes[clave]


def subtitulo(img, texto):
    """Subtítulo de fansub de los 90: letras blancas gruesas con contorno negro, abajo."""
    pil = Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8))
    d = ImageDraw.Draw(pil)
    f = _fuente(FUENTE_SUB, 27)
    lineas = texto.split("\n")
    y = int(AL * 0.845) - 16 * (len(lineas) - 1)
    for ln in lineas:
        w = d.textlength(ln, font=f)
        d.text(((AN - w) / 2, y), ln, font=f, fill=(246, 246, 238), stroke_width=3, stroke_fill=(6, 6, 8))
        y += 36
    return np.asarray(pil, np.float32) / 255


def titulo(img, alfa):
    pil = Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)).convert("RGBA")
    capa = Image.new("RGBA", pil.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    f = _fuente(FUENTE_TITULO, 74, "Bold")
    txt = "LA INCISIÓN"
    w = d.textlength(txt, font=f)
    d.text(((AN - w) / 2, AL * 0.5 - 50), txt, font=f, fill=(240, 236, 226, int(255 * alfa)))
    from PIL import ImageFilter
    brillo = capa.filter(ImageFilter.GaussianBlur(9))
    pil = Image.alpha_composite(pil, brillo)
    pil = Image.alpha_composite(pil, capa)
    return np.asarray(pil.convert("RGB"), np.float32) / 255


def acabado(img, plano, ef, t_global, cuadro, id_plano, t_local):
    if not ef.get("sin_acabado"):
        img = estilo.acabado(img, plano.paleta, cuadro, plano.grano, plano.halo)
    if ef.get("negativo"):
        img = 1 - img
    if ef.get("blanco", 0) > 0:
        img = img * (1 - ef["blanco"]) + ef["blanco"]
    if ef.get("negro", 0) > 0:
        img = img * (1 - ef["negro"])
    if ef.get("titulo", 0) > 0:
        img = titulo(img, ef["titulo"])
    for ident, a, b, txt in SUBTITULOS:
        if ident == id_plano and a <= t_local < b:
            img = subtitulo(img, txt)
            break
    return img


def render_plano(args):
    ident, inicio, dur, salida, ffmpeg = args
    t0 = time.time()
    plano = PLANOS[ident](dur)
    n = int(round(dur * FPS))
    primero = int(round(inicio * FPS))
    proc = subprocess.Popen([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                             "-s", f"{AN}x{AL}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                             "-crf", "15", "-pix_fmt", "yuv420p", "-threads", "2", str(salida)], stdin=subprocess.PIPE)
    for f in range(n):
        t = f / FPS
        img, ef = plano.cuadro(t)
        img = acabado(img, plano, ef, inicio + t, primero + f, ident, t)
        proc.stdin.write((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError(f"ffmpeg falló en el plano {ident}")
    return ident, time.time() - t0


def hoja(linea, salida, momentos=(0.3, 0.8), ids=None):
    fotos = []
    for ident, ini, dur in linea:
        if ids and ident not in ids:
            continue
        plano = PLANOS[ident](dur)
        for m in momentos:
            t = min(dur * m, dur - 1 / FPS)
            img, ef = plano.cuadro(t)
            img = acabado(img, plano, ef, ini + t, int((ini + t) * FPS), ident, t)
            im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).resize((AN // 2, AL // 2))
            ImageDraw.Draw(im).text((6, 6), f"{ident} {t:.1f}s", fill=(255, 255, 0))
            fotos.append(im)
        print(f"  {ident}", flush=True)
    w, h = fotos[0].size
    cols = 8
    lienzo = Image.new("RGB", (w * cols, h * math.ceil(len(fotos) / cols)))
    for i, im in enumerate(fotos):
        lienzo.paste(im, ((i % cols) * w, (i // cols) * h))
    lienzo.save(salida)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--fotos", action="store_true")
    parser.add_argument("--momentos", type=float, nargs="*", default=[0.3, 0.8])
    parser.add_argument("--planos", nargs="*", help="vuelve a pintar solo estos planos")
    parser.add_argument("--solo-audio", action="store_true")
    parser.add_argument("--sin-sonido", action="store_true")
    parser.add_argument("--procesos", type=int, default=os.cpu_count() or 2)
    parser.add_argument("--salida", type=Path, default=RAIZ / "la-incision-anime90.mp4")
    args = parser.parse_args()
    BUILD.mkdir(parents=True, exist_ok=True)
    linea = linea_de_tiempo()
    total = sum(d for _, _, d in linea)
    if args.fotos:
        hoja(linea, BUILD / "contactos.png", tuple(args.momentos), args.planos)
        print(f"Hoja de contactos → {BUILD / 'contactos.png'}")
        return
    ffmpeg = buscar_ffmpeg()
    carpeta = BUILD / "planos"
    carpeta.mkdir(exist_ok=True)
    archivos = {ident: carpeta / f"{i:02d}-{ident.replace('í', 'i')}.mp4" for i, (ident, _, _) in enumerate(linea)}
    if not args.solo_audio:
        trabajos = [(ident, ini, dur, archivos[ident], ffmpeg) for ident, ini, dur in linea
                    if not args.planos or ident in args.planos]
        trabajos.sort(key=lambda x: -x[2])
        t0 = time.time()
        print(f"Dibujando {len(trabajos)} planos con {args.procesos} procesos…", flush=True)
        with Pool(args.procesos) as pool:
            for ident, seg in pool.imap_unordered(render_plano, trabajos):
                print(f"  {ident:>6} listo en {seg:.0f} s", flush=True)
        print(f"Planos en {time.time() - t0:.0f} s", flush=True)
    lista = BUILD / "lista.txt"
    lista.write_text("".join(f"file '{archivos[i].as_posix()}'\n" for i, _, _ in linea), encoding="utf-8")
    video_in = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lista)]
    formato = ["-vf", "scale=1080:1920:flags=lanczos", "-pix_fmt", "yuv420p", "-r", str(FPS)]
    if args.sin_sonido:
        subprocess.run(video_in + formato + ["-c:v", "libx264", "-preset", "medium", "-crf", "19", "-an",
                                             str(args.salida)], check=True)
        print(f"Listo (sin sonido): {args.salida}")
        return
    from anime90 import sonido
    audio = BUILD / "sonido.wav"
    print("Componiendo el sonido…", flush=True)
    sonido.generar(linea, audio)
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
