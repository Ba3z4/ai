#!/usr/bin/env python3
"""Renderiza «Cómo abrir a un humano», la versión pintada de La Incisión (vertical 9:16, con sonido).

El narrador enmascarado dicta ocho pasos palabra por palabra; su voz marca el ritmo: cada pedazo del
guion dura lo que tarda en decirlo, y cada ilustración dura lo que duran sus palabras.

Uso (desde la carpeta la-incision):
    python3 animacion/render_pasos.py              # → la-incision-como-abrir-un-humano.mp4 y su versión ligera
    python3 animacion/render_pasos.py --fotos      # hoja de contactos con un cuadro de cada ilustración
    python3 animacion/render_pasos.py --solo-audio # rehace voz y música sin volver a dibujar
    python3 animacion/render_pasos.py --solo glitch  # vuelve a pintar solo esa ilustración y rearma el video

Necesita lo mismo que render.py, y espeak-ng con la voz mexicana de MBROLA para el narrador.
"""

import argparse
import json
import math
import os
import subprocess
import sys
import time
import wave
from multiprocessing import Pool
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(RAIZ / "herramientas"))

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

import pintura  # noqa: E402
import sonido as S  # noqa: E402
from dibujo import Lienzo  # noqa: E402
from pasos import GUION, lamina  # noqa: E402
from render import buscar_ffmpeg  # noqa: E402

FPS = 24
BUILD = AQUI / "build" / "pasos"
FUENTE = AQUI / "fuentes" / "Cinzel.ttf"
VOZ = "mb-mx1"


# --- la voz del narrador ------------------------------------------------------------------------

def voz_narrador(texto, rng):
    """Voz grave y doble (una capa una octava más oscura), con saturación y sala."""
    alta = S.tts(texto.lower(), VOZ, 92, 22)
    baja = S.tts(texto.lower(), VOZ, 92, 0)
    if alta is None:
        alta = S.voz(texto.lower().split(), 92, 3, ritmo=0.26)
        baja = alta
    n = max(len(alta), len(baja))
    alta = np.pad(alta, (0, n - len(alta)))
    baja = np.pad(baja, (0, n - len(baja)))
    x = alta * 0.7 + S.pb(baja, 2500) * 0.55
    x = S.banda(x, 70, 7000)
    x = np.tanh(x * 1.8) / math.tanh(1.8)
    return x / (np.abs(x).max() + 1e-9)


def linea_de_tiempo(rng):
    """Voz por pedazos y la línea de tiempo: segmentos [(ilustración, variante, inicio, dur)] y palabras."""
    t = 0.35
    segmentos, palabras, clips = [], [], []
    variante = 0
    for n, (ilustracion, pedazos) in enumerate(GUION):
        inicio = t
        for k, texto in enumerate(pedazos):
            x = voz_narrador(texto, rng)
            if ilustracion == "glitch":
                x = S.cinta_frena(np.concatenate([x, x[: len(x) // 3]]), len(x) / S.SR * 1.2)
            d = len(x) / S.SR
            clips.append((t, x, ilustracion))
            palabras.append((texto, t, t + d + 0.12, ilustracion == "glitch"))
            pausa = 0.5
            if texto == "PASO":
                pausa = 0.15
            elif k == len(pedazos) - 1:
                pausa = 0.8 if pedazos[0] == "PASO" else 0.65
            if texto == "HUMANO":
                pausa = 1.1
            t += d + pausa
        if t - inicio < 1.6:
            t = inicio + 1.6
        segmentos.append((ilustracion, variante if ilustracion == "narrador" else 0, inicio if n else 0.0, 0.0))
        if ilustracion == "narrador":
            variante += 1
    # La duración de cada segmento llega hasta el inicio del siguiente; el último dura su voz más un respiro.
    final = t + 1.6
    ajustados = []
    for i, (ilu, var, ini, _) in enumerate(segmentos):
        fin = segmentos[i + 1][2] if i + 1 < len(segmentos) else final
        ajustados.append((ilu, var, ini, fin - ini))
    return ajustados, palabras, clips, final


def pista_de_voz(clips, total):
    voz = np.zeros(S.muestras(total) + S.SR, np.float32)
    for t, x, _ in clips:
        i = S.muestras(t)
        voz[i:i + len(x)] += x[: len(voz) - i]
    return voz


def envolvente(voz, total):
    """Qué tan abierta va la boca del narrador en cada cuadro."""
    n = int(total * FPS) + 1
    salto = S.SR // FPS
    env = np.array([np.sqrt(np.mean(voz[i * salto:(i + 1) * salto] ** 2)) for i in range(n)], np.float32)
    env = np.convolve(env, np.ones(2) / 2, mode="same")
    return np.clip(env / (np.percentile(env[env > 0.01], 90) + 1e-6) if (env > 0.01).any() else env, 0, 1)


# --- los cuadros ----------------------------------------------------------------------------------

def acabado(img, lam, t_global, cuadro, palabras):
    img = pintura.pintar(img, lam.paleta)
    img = pintura.resplandor(img, 0.32)
    glitch = getattr(lam, "variante", None) == "glitch"
    if glitch:
        rng = np.random.default_rng(cuadro)
        h = img.shape[0]
        for _ in range(6):
            a = int(rng.integers(0, h))
            b = a + int(rng.integers(4, 60))
            img[a:b] = np.roll(img[a:b], int(rng.normal(0, 60)), axis=1)
        img[..., 0] = np.roll(img[..., 0], int(rng.integers(4, 14)), axis=1)
        if rng.random() < 0.18:
            img = 1 - img
    img = pintura.banda(img)
    for texto, ini, fin, roto in palabras:
        if ini <= t_global < fin:
            u = (t_global - ini) / (fin - ini)
            gris = max(0.0, (u - 0.7) / 0.3)
            if roto:
                img = pintura.palabra_rota(img, texto, FUENTE, cuadro)
            else:
                img = pintura.palabra(img, texto, FUENTE, gris=gris)
            break
    return img


def render_segmento(args):
    i, ilu, var, ini, dur, ancho, salida, ffmpeg, palabras, env = args
    t0 = time.time()
    lam = lamina(ilu, dur, ancho, var)
    lz = Lienzo(ancho, semilla=11 + i)
    lz.sin_tinta = True
    lz.hervor = 0.0
    n = max(1, int(round(dur * FPS)))
    primero = int(round(ini * FPS))
    proc = subprocess.Popen([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                             "-s", f"{lz.w}x{lz.h}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                             "-crf", "16", "-pix_fmt", "yuv420p", "-threads", "2", str(salida)], stdin=subprocess.PIPE)
    for f in range(n):
        t = f / FPS
        tq = math.floor(t * 12 + 1e-6) / 12
        cuadro = primero + f
        lz.nuevo(cuadro // 2)
        lz.camara()
        boca = float(env[min(cuadro, len(env) - 1)]) if ilu in ("narrador", "final", "glitch") else 0.0
        lam.dibujar(lz, t, tq, boca=boca)
        img = acabado(lz.rgb8(), lam, ini + t, cuadro, palabras)
        proc.stdin.write((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError(f"ffmpeg falló en el segmento {i} ({ilu})")
    return i, ilu, time.time() - t0


# --- música y efectos ------------------------------------------------------------------------------

def nota(f):
    return 440 * 2 ** ((f - 69) / 12)


def colchon(dur, rng):
    """Colchón oscuro: acordes de re menor (pad y coro sin palabras) con un bajo que late a 56 por minuto."""
    acordes = [(38, 50, 53, 57), (34, 50, 53, 58), (31, 50, 55, 58), (33, 49, 52, 57)]
    largo = 4.3
    n = S.muestras(dur)
    x = np.zeros(n, np.float32)
    t = 0.0
    k = 0
    while t < dur:
        raiz, *notas = acordes[k % 4]
        m = S.muestras(min(largo + 1.5, dur - t + 0.01))
        env = S.env_ar(m, 1.2, 1.4)
        pad = sum(S.sierra(nota(nt) * d, m) for nt in notas for d in (0.997, 1.003)) * 0.12
        pad = S.pb(pad, 900)
        coro = sum(S.resonador(S.sierra(nota(nt + 12) * (1 + 0.004 * np.sin(np.arange(m) / S.SR * 5.5)), m), f, bw)
                   for nt in notas[1:] for f, bw in ((800, 90), (1200, 120))) * 0.02
        bajo = S.seno(nota(raiz), m) * 0.5
        i = S.muestras(t)
        fin = min(n, i + m)
        x[i:fin] += ((pad + coro + bajo) * env)[: fin - i]
        t += largo
        k += 1
    latido = S.latidos(dur, 56, rng) * 0.35
    return x + latido[:n]


def mezcla_sonido(segmentos, palabras, clips, total, ruta, rng):
    P = S.Pista(total + 1)
    voz = pista_de_voz(clips, total)
    P.poner(S.reverb(voz, 2.2, 0.3, rng), 0, 0.5)
    fin_musica = next(ini for ilu, _, ini, _ in segmentos if ilu == "glitch")
    ini_musica = next(fin for texto, _, fin, _ in palabras if texto == "HUMANO")
    m = colchon(fin_musica - ini_musica, rng)
    m *= np.clip(np.linspace(0, 1, len(m)) * 6, 0, 1).astype(np.float32)
    P.poner(S.reverb(m, 2.5, 0.35, rng), ini_musica, 0.28)
    # Golpe en cada «PASO» y un aliento al revés que lo anuncia.
    for texto, ini, _, _ in palabras:
        if texto == "PASO":
            P.poner(S.golpe(rng, 1.0, 2.2), ini - 0.02, 0.45)
            P.poner(S.swell_reverso(0.9, rng), ini - 0.9, 0.12)
            P.poner(S.campanada(rng, 73.4), ini, 0.25)
    for ilu, _, ini, dur in segmentos:
        if ilu == "cena":
            ch = S.pb(S.murmullo(dur, 200, 1) + S.murmullo(dur, 120, 2), 500)
            P.poner(ch, ini, 0.06)
            for k in range(3):
                P.poner(S.tintineo(rng), ini + 0.4 + k * dur / 3, 0.03)
        elif ilu == "noche":
            P.poner(S.reloj(dur, rng) * 0.06, ini)
        elif ilu == "rincon":
            P.poner(S.drone(dur, rng, 41.2, 400) * np.linspace(0.2, 1, S.muestras(dur), dtype=np.float32), ini, 0.2)
        elif ilu == "mascaras":
            P.poner(S.latidos(dur, 112, rng), ini, 0.7)
        elif ilu == "grito":
            P.poner(S.aire_ahogado(dur, rng), ini, 0.1)
        elif ilu == "recuerdo":
            P.poner(S.reverb(S.caja_musical(S.CANCION[:8], 0.36, rng), 2.2, 0.4, rng), ini, 0.1)
            P.poner(S.pajaros(dur, rng, 1.5), ini, 0.04)
        elif ilu == "rompe":
            golpe = ini + dur * (0.9 - 0.35) / (2.2 - 0.35)
            P.poner(S.vidrio_grieta(0.5, rng), ini, 0.18)
            P.poner(S.vidrio_rompe(rng), golpe, 0.3)
            P.poner(S.golpe(rng, 0.9, 1.5), golpe, 0.35)
        elif ilu == "abre":
            corte = S.pa(S.ruido(S.muestras(0.5), rng), 2500) * S.env_ar(S.muestras(0.5), 0.02, 0.3)
            P.poner(corte, ini + dur * 0.45, 0.25)
        elif ilu == "toma":
            n = S.muestras(dur)
            brillo = sum(S.seno(f, n) for f in (1760, 2217, 2637)) * (0.5 + 0.5 * np.sin(np.arange(n) / S.SR * 30))
            P.poner(brillo * np.linspace(0, 1, n, dtype=np.float32) * 0.1, ini, 0.3)
        elif ilu == "cose":
            for k in range(10):
                P.poner(S.clic(rng, 3200, 0.04, 250), ini + dur * (k + 1) / 11, 0.1)
        elif ilu == "mesa":
            P.poner(S.pajaros(dur, rng, 1.0), ini, 0.04)
        elif ilu == "herida":
            P.poner(S.latidos(dur, 80, rng), ini, 0.6)
            P.poner(S.cluster(dur, rng, 590), ini + 0.6, 0.08)
        elif ilu == "final":
            P.poner(S.golpe(rng, 1.3, 3.0), ini, 0.6)
        elif ilu == "glitch":
            P.poner(S.estatica(dur, rng), ini, 0.12)
            for k in range(4):
                P.poner(S.falla(0.2, rng), ini + k * dur / 4, 0.25)
    x = P.x
    x = S.pb(S.pa(x, 30), 12000)
    rms = np.sqrt(np.mean(x ** 2)) + 1e-9
    x = np.tanh(x * (0.12 / rms) * 1.3) / 1.3
    x = x / (np.abs(x).max() + 1e-9) * 0.89
    x = x[: S.muestras(total)]
    with wave.open(str(ruta), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(S.SR)
        w.writeframes((x * 32767).astype("<i2").tobytes())


# --- montaje ---------------------------------------------------------------------------------------

def hoja(segmentos, palabras, env, ancho, salida):
    fotos = []
    for i, (ilu, var, ini, dur) in enumerate(segmentos):
        lam = lamina(ilu, dur, ancho, var)
        lz = Lienzo(ancho, semilla=11 + i)
        lz.sin_tinta = True
        lz.hervor = 0.0
        t = dur * 0.6
        cuadro = int((ini + t) * FPS)
        lz.nuevo(cuadro // 2)
        lz.camara()
        lam.dibujar(lz, t, t, boca=float(env[min(cuadro, len(env) - 1)]))
        img = acabado(lz.rgb8(), lam, ini + t, cuadro, palabras)
        im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
        ImageDraw.Draw(im).text((6, 6), f"{i} {ilu} {ini:.1f}s", fill=(255, 255, 0))
        fotos.append(im)
        print(f"  {i:2d} {ilu}", flush=True)
    w, h = fotos[0].size
    cols = 6
    filas = math.ceil(len(fotos) / cols)
    hoja = Image.new("RGB", (w * cols, h * filas))
    for i, im in enumerate(fotos):
        hoja.paste(im, ((i % cols) * w, (i // cols) * h))
    hoja.save(salida)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--ancho", type=int, default=720)
    parser.add_argument("--fotos", action="store_true")
    parser.add_argument("--solo-audio", action="store_true")
    parser.add_argument("--solo", nargs="*", help="vuelve a pintar solo estas ilustraciones (p. ej. glitch cena)")
    parser.add_argument("--procesos", type=int, default=os.cpu_count() or 2)
    parser.add_argument("--salida", type=Path, default=RAIZ / "la-incision-como-abrir-un-humano.mp4")
    args = parser.parse_args()
    BUILD.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(2026)
    print("Grabando al narrador…", flush=True)
    segmentos, palabras, clips, total = linea_de_tiempo(rng)
    env = envolvente(pista_de_voz(clips, total), total)
    (BUILD / "linea.json").write_text(json.dumps({"segmentos": segmentos, "palabras": palabras, "total": total},
                                                 ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Duración: {total:.1f} s en {len(segmentos)} ilustraciones", flush=True)
    if args.fotos:
        hoja(segmentos, palabras, env, 360, BUILD / "contactos.png")
        print(f"Hoja de contactos → {BUILD / 'contactos.png'}")
        return
    ffmpeg = buscar_ffmpeg()
    carpeta = BUILD / f"segmentos-{args.ancho}"
    carpeta.mkdir(exist_ok=True)
    archivos = [carpeta / f"{i:02d}-{ilu}.mp4" for i, (ilu, _, _, _) in enumerate(segmentos)]
    if not args.solo_audio:
        trabajos = [(i, ilu, var, ini, dur, args.ancho, archivos[i], ffmpeg, palabras, env)
                    for i, (ilu, var, ini, dur) in enumerate(segmentos) if not args.solo or ilu in args.solo]
        trabajos.sort(key=lambda x: -x[4])
        t0 = time.time()
        print(f"Pintando {len(trabajos)} ilustraciones con {args.procesos} procesos…", flush=True)
        with Pool(args.procesos) as pool:
            for i, ilu, seg in pool.imap_unordered(render_segmento, trabajos):
                print(f"  {i:2d} {ilu:>9} lista en {seg:.0f} s", flush=True)
        print(f"Ilustraciones en {time.time() - t0:.0f} s", flush=True)
    audio = BUILD / "sonido.wav"
    print("Mezclando voz y música…", flush=True)
    mezcla_sonido(segmentos, palabras, clips, total, audio, rng)
    lista = BUILD / "lista.txt"
    lista.write_text("".join(f"file '{a.as_posix()}'\n" for a in archivos), encoding="utf-8")
    video_in = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lista)]
    formato = ["-vf", "scale=1080:1920:flags=lanczos", "-pix_fmt", "yuv420p", "-r", str(FPS)]
    base = video_in + ["-i", str(audio)] + formato
    subprocess.run(base + ["-c:v", "libx264", "-preset", "slow", "-crf", "19", "-maxrate", "7M", "-bufsize", "14M",
                           "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(args.salida)],
                   check=True)
    print(f"Listo: {args.salida}")
    ligera = args.salida.with_name(args.salida.stem + "-ligera.mp4")
    kbps = int(28 * 8192 / total) - 128
    video = ["-c:v", "libx264", "-preset", "slower", "-b:v", f"{kbps}k", "-x264-params", "aq-mode=3:aq-strength=0.9",
             "-passlogfile", str(BUILD / "ligera")]
    subprocess.run(video_in + formato + video + ["-pass", "1", "-an", "-f", "mp4", os.devnull], check=True)
    subprocess.run(base + video + ["-pass", "2", "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart",
                                   str(ligera)], check=True)
    print(f"Versión ligera: {ligera}")


if __name__ == "__main__":
    main()
