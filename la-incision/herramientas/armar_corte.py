#!/usr/bin/env python3
"""Arma el corte bruto de La Incisión con las tomas elegidas de Kling.

Busca en tomas/ un archivo por plano (1A.mp4, 1B.mp4…), recorta cada uno a la duración
que marca plan.json, inserta el negro y el título, y escribe corte-bruto.mp4 (1920×1080, 24 fps).
Los planos que falten salen como una tarjeta gris con su ID, así que sirve también para revisar
el ritmo antes de tener todas las tomas. Conserva el audio de los clips que lo traigan.

Uso:
    python3 herramientas/armar_corte.py
    python3 herramientas/armar_corte.py --tomas otra/carpeta --salida prueba.mp4

Si la parte buena de una toma no empieza en el segundo 0, anota la entrada en tomas/entradas.json:
    {"3A": 1.5, "5B": 2}

Necesita ffmpeg en el PATH (Windows: winget install Gyan.FFmpeg) o el paquete imageio-ffmpeg.
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generar import RAIZ, cargar, secuencia  # noqa: E402

ANCHO, ALTO, FPS = 1920, 1080, 24
EXTENSIONES = (".mp4", ".mov", ".webm", ".mkv")
FUENTES = (
    "C:/Windows/Fonts/georgiab.ttf",
    "C:/Windows/Fonts/georgia.ttf",
    "C:/Windows/Fonts/arial.ttf",
    "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
    "/System/Library/Fonts/Supplemental/Georgia.ttf",
    "/Library/Fonts/Georgia.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
)


def buscar_ffmpeg():
    ruta = shutil.which("ffmpeg")
    if ruta:
        return ruta
    try:
        import imageio_ffmpeg
    except ImportError:
        sys.exit("No encontré ffmpeg. Instálalo (Windows: winget install Gyan.FFmpeg) o corre: pip install imageio-ffmpeg")
    return imageio_ffmpeg.get_ffmpeg_exe()


def consultar(ffmpeg, *args):
    resultado = subprocess.run([ffmpeg, "-hide_banner", *args], capture_output=True, text=True,
                               encoding="utf-8", errors="replace")
    return resultado.stdout + resultado.stderr


def buscar_fuente(elegida):
    if elegida:
        return elegida
    return next((Path(f) for f in FUENTES if Path(f).is_file()), None)


def valor(texto):
    """Protege un valor para drawtext: comillas para el grafo y \\: para las opciones del filtro."""
    texto = str(texto).replace("\\", "/").replace("'", "’").replace(":", r"\:")
    return f"'{texto}'"


def rotulo(fuente, texto, tamano, y, color="white"):
    return (f"drawtext=fontfile={valor(fuente.as_posix())}:text={valor(texto)}:expansion=none:"
            f"fontcolor={color}:fontsize={tamano}:x=(w-text_w)/2:y={y}")


def buscar_toma(carpeta, ident):
    return next((carpeta / f"{ident}{ext}" for ext in EXTENSIONES if (carpeta / f"{ident}{ext}").is_file()), None)


def armar(ffmpeg, plan, carpeta, salida, fuente):
    filas, total = secuencia(plan)
    archivo_entradas = carpeta / "entradas.json"
    entradas = json.loads(archivo_entradas.read_text(encoding="utf-8")) if archivo_entradas.is_file() else {}
    args, filtros, pares, informe = [ffmpeg, "-hide_banner", "-y"], [], [], []
    n = 0

    def entrada(*opciones):
        nonlocal n
        args.extend(opciones)
        n += 1
        return n - 1

    for i, f in enumerate(filas):
        dur = f["uso"]
        toma = None if f["extra"] else buscar_toma(carpeta, f["id"])
        if toma:
            inicio = float(entradas.get(f["id"], 0))
            v = entrada("-ss", str(inicio), "-t", str(dur + 1), "-i", str(toma))
            con_audio = "Audio:" in consultar(ffmpeg, "-i", str(toma))
            a = v if con_audio else entrada("-f", "lavfi", "-t", str(dur), "-i", "anullsrc=r=48000:cl=stereo")
            video = (f"[{v}:v]scale={ANCHO}:{ALTO}:force_original_aspect_ratio=decrease,"
                     f"pad={ANCHO}:{ALTO}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={FPS}")
            informe.append((f["id"], f"{toma.name} desde {inicio:g} s" + ("" if con_audio else ", sin audio"), dur))
        else:
            color = "black" if f["extra"] else "0x2A2F36"
            v = entrada("-f", "lavfi", "-t", str(dur), "-i", f"color=c={color}:s={ANCHO}x{ALTO}:r={FPS}")
            a = entrada("-f", "lavfi", "-t", str(dur), "-i", "anullsrc=r=48000:cl=stereo")
            video = f"[{v}:v]setsar=1"
            if fuente and f["id"] == "Título":
                video += "," + rotulo(fuente, plan["titulo"].upper(), 110, "(h-text_h)/2")
            elif fuente and not f["extra"]:
                video += ("," + rotulo(fuente, f["id"], 130, "(h/2)-190") + "," + rotulo(fuente, f["titulo"], 46, "(h/2)+10")
                          + "," + rotulo(fuente, "Falta la toma", 30, "(h/2)+90", "0x9AA4AE"))
            informe.append((f["id"], f["titulo"] if f["extra"] else "falta: tarjeta gris", dur))
        filtros.append(f"{video},format=yuv420p,tpad=stop_mode=clone:stop_duration={dur},"
                       f"trim=duration={dur},setpts=PTS-STARTPTS[v{i}]")
        filtros.append(f"[{a}:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,"
                       f"apad,atrim=duration={dur},asetpts=PTS-STARTPTS[a{i}]")
        pares.append(f"[v{i}][a{i}]")
    filtros.append(f"{''.join(pares)}concat=n={len(filas)}:v=1:a=1[v][a]")
    args += ["-filter_complex", ";".join(filtros), "-map", "[v]", "-map", "[a]",
             "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
             "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(salida)]
    for ident, detalle, dur in informe:
        print(f"{ident:>7}  {dur:>2} s  {detalle}")
    print(f"Total: {total // 60}:{total % 60:02d}. Renderizando {salida.name}…")
    resultado = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if resultado.returncode != 0:
        sys.exit("ffmpeg falló:\n" + resultado.stderr[-3000:])
    print(f"Listo: {salida}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--tomas", type=Path, default=RAIZ / "tomas", help="carpeta con las tomas elegidas (por defecto tomas/)")
    parser.add_argument("--salida", type=Path, default=RAIZ / "corte-bruto.mp4", help="archivo de salida")
    parser.add_argument("--fuente", type=Path, help="fuente .ttf para el título y las tarjetas")
    args = parser.parse_args()
    ffmpeg = buscar_ffmpeg()
    fuente = buscar_fuente(args.fuente)
    if fuente and " drawtext " not in consultar(ffmpeg, "-filters"):
        print("Este ffmpeg no trae drawtext: el título y las tarjetas saldrán sin texto.")
        fuente = None
    elif not fuente:
        print("No encontré una fuente: el título y las tarjetas saldrán sin texto (usa --fuente).")
    if not args.tomas.is_dir():
        print(f"No existe {args.tomas}: todos los planos saldrán como tarjetas grises.")
    armar(ffmpeg, cargar(), args.tomas, args.salida, fuente)


if __name__ == "__main__":
    main()
