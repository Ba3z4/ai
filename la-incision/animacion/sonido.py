"""Sonido del corto animado, sintetizado desde cero (sin grabaciones): ambientes, voces amortiguadas
de caricatura, reloj, latidos, drones, golpes, vidrio y una caja musical.

Todo va a 48 kHz en estéreo. `generar(linea, ruta)` escribe el WAV siguiendo la línea de tiempo
[(id, inicio, duración)] que arma render.py.
"""

import math
import shutil
import subprocess
import tempfile
import wave
from pathlib import Path

import numpy as np
from scipy import signal

SR = 48000


# --- utilidades --------------------------------------------------------------------------------

def muestras(dur):
    return max(1, int(round(dur * SR)))


def tiempo(n):
    return np.arange(n, dtype=np.float32) / SR


def ruido(n, rng, color="blanco"):
    x = rng.standard_normal(n).astype(np.float32)
    if color == "blanco":
        return x
    espectro = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    f[0] = f[1] if len(f) > 1 else 1
    espectro /= np.sqrt(f) if color == "rosa" else f
    y = np.fft.irfft(espectro, n).astype(np.float32)
    return y / (np.abs(y).max() + 1e-9)


def _sos(tipo, fc, orden=2):
    if isinstance(fc, (list, tuple)):
        fc = [min(max(f, 10), SR / 2 - 100) for f in fc]
    else:
        fc = min(max(fc, 10), SR / 2 - 100)
    return signal.butter(orden, fc, btype=tipo, fs=SR, output="sos")


def pb(x, fc, orden=2):
    return signal.sosfilt(_sos("lowpass", fc, orden), x, axis=0).astype(np.float32)


def pa(x, fc, orden=2):
    return signal.sosfilt(_sos("highpass", fc, orden), x, axis=0).astype(np.float32)


def banda(x, f1, f2, orden=2):
    return signal.sosfilt(_sos("bandpass", [f1, f2], orden), x, axis=0).astype(np.float32)


def resonador(x, f, ancho):
    """Filtro de dos polos (formante)."""
    r = math.exp(-math.pi * ancho / SR)
    th = 2 * math.pi * f / SR
    return signal.lfilter([1 - r], [1, -2 * r * math.cos(th), r * r], x).astype(np.float32)


def env_exp(n, tau):
    return np.exp(-tiempo(n) / max(tau, 1e-4)).astype(np.float32)


def env_ar(n, ataque, caida):
    t = tiempo(n)
    dur = n / SR
    a = np.clip(t / max(ataque, 1e-4), 0, 1)
    r = np.clip((dur - t) / max(caida, 1e-4), 0, 1)
    return (a * r).astype(np.float32)


def fase(f, n):
    f = np.broadcast_to(np.asarray(f, np.float32), (n,))
    return np.cumsum(f) / SR


def seno(f, n, fase0=0.0):
    return np.sin(2 * math.pi * fase(f, n) + fase0).astype(np.float32)


def sierra(f, n):
    ph = fase(f, n)
    return (2 * (ph % 1.0) - 1).astype(np.float32)


def reverb(x, dur=1.8, mezcla=0.3, rng=None, brillo=4000):
    """Reverberación por convolución con una cola de ruido que decae (estéreo)."""
    rng = rng or np.random.default_rng(7)
    n = muestras(dur)
    cola = np.stack([ruido(n, rng), ruido(n, rng)], axis=1) * env_exp(n, dur / 5)[:, None]
    cola = pb(cola, brillo)
    cola /= np.sqrt((cola ** 2).sum(axis=0)) + 1e-9
    mono = x if x.ndim == 1 else x.mean(axis=1)
    mojado = np.stack([signal.fftconvolve(mono, cola[:, i])[: len(mono)] for i in range(2)], axis=1).astype(np.float32)
    seco = x if x.ndim == 2 else np.stack([x, x], axis=1)
    return seco * (1 - mezcla) + mojado * mezcla * 2.2


def estereo(x, pan=0.0):
    if x.ndim == 2:
        return x
    izq = math.cos((pan + 1) * math.pi / 4)
    der = math.sin((pan + 1) * math.pi / 4)
    return np.stack([x * izq * 1.414, x * der * 1.414], axis=1).astype(np.float32)


class Pista:
    def __init__(self, dur):
        self.x = np.zeros((muestras(dur) + SR, 2), np.float32)

    def poner(self, s, t, gan=1.0, pan=0.0):
        s = estereo(np.asarray(s, np.float32), pan) * gan
        i = int(round(t * SR))
        if i < 0:
            s = s[-i:]
            i = 0
        fin = min(len(self.x), i + len(s))
        if fin > i:
            self.x[i:fin] += s[: fin - i]


# --- voces de caricatura (síntesis por formantes) -----------------------------------------------

VOCALES = {"a": (800, 1250, 2650), "e": (450, 1900, 2600), "i": (300, 2250, 3000), "o": (480, 880, 2500),
           "u": (330, 800, 2400)}
SIN_ACENTO = str.maketrans("áéíóúü", "aeiouu")


def _silaba(s, f0, dur, rng, brillo=1.0, acento=False):
    s = s.lower().translate(SIN_ACENTO)
    vocal = next((ch for ch in s if ch in "aeiou"), "e")
    consonante = s[: s.index(vocal)] if vocal in s else ""
    n = muestras(dur)
    nc = muestras(0.05) if consonante else 0
    nv = n - nc
    t = tiempo(nv)
    vib = 1 + 0.012 * np.sin(2 * math.pi * 5.2 * t) + 0.004 * rng.standard_normal()
    fuente = sierra(f0 * vib, nv)
    fuente = pb(fuente, 3500 * brillo) + 0.06 * ruido(nv, rng)
    f1, f2, f3 = VOCALES[vocal]
    voz = resonador(fuente, f1, 90) * 1.0 + resonador(fuente, f2, 120) * 0.55 + resonador(fuente, f3, 180) * 0.25
    voz *= env_ar(nv, 0.02, 0.05) * (1.15 if acento else 1.0)
    if nc:
        c = consonante[-1]
        if c in "szcxf" or consonante in ("ch",):
            pre = pa(ruido(nc, rng), 3800) * env_ar(nc, 0.01, 0.02) * 0.25
        elif c in "tpkq" or consonante == "c":
            pre = np.zeros(nc, np.float32)
            k = muestras(0.012)
            pre[-k:] = pa(ruido(k, rng), 1500) * 0.5
        elif c in "mnñ":
            pre = pb(sierra(f0, nc), 350) * 0.5 * env_ar(nc, 0.01, 0.01)
        elif c == "j":
            pre = banda(ruido(nc, rng), 900, 3500) * 0.3 * env_ar(nc, 0.01, 0.02)
        else:
            pre = resonador(sierra(f0, nc), 350, 100) * 0.6 * env_ar(nc, 0.01, 0.01)
        voz = np.concatenate([pre, voz])
    return voz.astype(np.float32)


def voz(silabas, f0, inicio_rng=0, ritmo=0.17, pregunta=False, brillo=1.0, acentos=()):
    """Frase de caricatura: sílabas con entonación. Las sílabas con '|' al final llevan una pausa."""
    rng = np.random.default_rng(inicio_rng)
    partes = []
    total = len(silabas)
    for i, s in enumerate(silabas):
        pausa = s.endswith("|")
        s = s.rstrip("|")
        acento = i in acentos or any(ch in s for ch in "áéíóú")
        declina = 1 - 0.14 * i / max(total - 1, 1)
        sube = 1 + (0.35 * (i - total + 3) / 2 if pregunta and i >= total - 2 else 0)
        f = f0 * declina * sube * (1.12 if acento else 1.0) * (1 + rng.normal(0, 0.03))
        dur = ritmo * (1.35 if acento else 1.0) * (1 + rng.normal(0, 0.08))
        partes.append(_silaba(s, f, dur, rng, brillo, acento))
        if pausa:
            partes.append(np.zeros(muestras(0.22), np.float32))
    x = np.concatenate(partes)
    return x / (np.abs(x).max() + 1e-9)


def murmullo(dur, f0, semilla, densidad=0.8):
    """Plática de fondo con sílabas al azar."""
    rng = np.random.default_rng(semilla)
    silabas = ["la", "que", "no", "si", "de", "pa", "ma", "te", "lo", "ya", "es", "bue", "mo", "dí", "ca", "ra", "to"]
    salida = np.zeros(muestras(dur), np.float32)
    t = rng.uniform(0, 0.4)
    while t < dur - 0.3:
        frase = [silabas[int(rng.integers(0, len(silabas)))] for _ in range(int(rng.integers(3, 9)))]
        x = voz(frase, f0 * rng.uniform(0.92, 1.1), int(rng.integers(0, 1 << 30)), ritmo=rng.uniform(0.13, 0.18))
        i = muestras(t)
        fin = min(len(salida), i + len(x))
        salida[i:fin] += x[: fin - i] * rng.uniform(0.5, 1.0)
        t += len(x) / SR + rng.uniform(0.2, 1.2) / densidad
    return salida


def risa(f0, veces=4, semilla=0):
    return voz(["ja"] * veces, f0, semilla, ritmo=0.13, brillo=1.2)


# --- efectos -----------------------------------------------------------------------------------

def tintineo(rng, f=None):
    f = f or rng.uniform(1800, 3200)
    n = muestras(0.5)
    x = sum(seno(f * k, n) * env_exp(n, tau) * a for k, tau, a in ((1, 0.22, 1), (2.76, 0.11, 0.5), (5.4, 0.06, 0.3),
                                                                     (8.9, 0.035, 0.2)))
    ataque = pa(ruido(muestras(0.004), rng), 3000)
    x[: len(ataque)] += ataque * 0.6
    return x * 0.5


def clic(rng, f=2500, dur=0.03, q=300):
    n = muestras(dur)
    x = np.zeros(n, np.float32)
    x[:muestras(0.002)] = rng.standard_normal(muestras(0.002))
    return resonador(x, f, q) * 20


def zumbido(dur, f=60):
    n = muestras(dur)
    return pb(seno(f, n) + 0.5 * seno(2 * f, n) + 0.25 * seno(3 * f, n) + 0.1 * sierra(f, n), 400)


def tono_cuarto(dur, rng, fc=220):
    return pb(ruido(muestras(dur), rng, "cafe"), fc)


def ventilador_sonido(dur, rng, vel=1.6):
    n = muestras(dur)
    x = banda(ruido(n, rng, "rosa"), 150, 900)
    return x * (1 + 0.35 * np.sin(2 * math.pi * vel * tiempo(n)))


def reloj(dur, rng, inicio=0.0):
    x = np.zeros(muestras(dur), np.float32)
    k = 0
    t = inicio
    while t < dur - 0.05:
        c = clic(rng, 3200 if k % 2 == 0 else 2300, 0.04, 250)
        i = muestras(t)
        fin = min(len(x), i + len(c))
        x[i:fin] += c[: fin - i]
        t += 0.5
        k += 1
    return x


def respiracion(dur, rng, ritmo=0.3, fuerza=1.0, nariz=True):
    """Respiración: ritmo en respiraciones por segundo (puede ser una función del tiempo)."""
    n = muestras(dur)
    x = np.zeros(n, np.float32)
    t = 0.0
    while t < dur:
        r = ritmo(t) if callable(ritmo) else ritmo
        periodo = 1 / max(r, 0.05)
        for es_inhala, parte, lo, hi in ((True, 0.42, 700, 2600), (False, 0.5, 300, 1500)):
            d = periodo * parte
            m = muestras(d)
            s = banda(ruido(m, rng, "rosa"), lo if not nariz else lo * 0.8, hi) * env_ar(m, d * 0.4, d * 0.5)
            i = muestras(t + (0 if es_inhala else periodo * 0.45))
            fin = min(n, i + m)
            if fin > i:
                x[i:fin] += s[: fin - i] * (0.8 if es_inhala else 0.6)
        t += periodo
    return x * fuerza


def latidos(dur, bpm, rng, fuerza=1.0):
    n = muestras(dur)
    x = np.zeros(n, np.float32)
    t = 0.0
    while t < dur:
        b = bpm(t) if callable(bpm) else bpm
        for retraso, g, f in ((0, 1.0, 58), (0.2, 0.65, 70)):
            m = muestras(0.25)
            tt = tiempo(m)
            golpe = np.sin(2 * math.pi * np.cumsum(f * (1 + 0.8 * np.exp(-tt * 40))) / SR) * env_exp(m, 0.07)
            golpe += pb(ruido(m, rng), 180) * env_exp(m, 0.02) * 0.6
            i = muestras(t + retraso)
            fin = min(n, i + m)
            if fin > i:
                x[i:fin] += golpe[: fin - i].astype(np.float32) * g
        t += 60 / b
    return pb(x, 220) * fuerza


def acufeno(dur, f=7600):
    n = muestras(dur)
    return (seno(f, n) * (0.8 + 0.2 * np.sin(2 * math.pi * 0.3 * tiempo(n)))).astype(np.float32)


def drone(dur, rng, f0=55.0, abre=600):
    n = muestras(dur)
    t = tiempo(n)
    x = sum(sierra(f0 * m, n) * a for m, a in ((1, 1), (1.004, 0.8), (1.498, 0.5), (2.01, 0.35), (1.06, 0.25)))
    x = pb(x, abre) + 0.2 * pb(ruido(n, rng, "rosa"), 300)
    return (x * (0.85 + 0.15 * np.sin(2 * math.pi * 0.13 * t))).astype(np.float32)


def cluster(dur, rng, base=440.0):
    """Cuerdas disonantes (acorde de segundas) que chirrían."""
    n = muestras(dur)
    t = tiempo(n)
    x = np.zeros(n, np.float32)
    for k, m in enumerate((1, 1.059, 1.122, 1.189, 1.5, 1.587)):
        vib = 1 + 0.006 * np.sin(2 * math.pi * (5 + k * 0.4) * t + k)
        x += sierra(base * m * vib, n)
    return banda(x, 700, 5000) * 0.25


def swell_reverso(dur, rng):
    n = muestras(dur)
    t = tiempo(n)
    return pa(ruido(n, rng), 1500) * ((t / dur) ** 3).astype(np.float32)


def golpe(rng, grave=1.0, dur=1.6):
    n = muestras(dur)
    t = tiempo(n)
    f = 38 + 70 * np.exp(-t * 9)
    x = np.sin(2 * math.pi * np.cumsum(f) / SR).astype(np.float32) * env_exp(n, 0.45) * grave
    x += pb(ruido(n, rng), 1800) * env_exp(n, 0.05) * 0.8
    return np.tanh(x * 1.8).astype(np.float32)


def susurros(dur, rng):
    n = muestras(dur)
    x = np.zeros(n, np.float32)
    t = 0.0
    while t < dur - 0.2:
        d = rng.uniform(0.12, 0.3)
        m = muestras(d)
        vocal = list(VOCALES.values())[int(rng.integers(0, 5))]
        s = sum(resonador(ruido(m, rng), f, 150) * a for f, a in zip(vocal, (1, 0.6, 0.3))) * env_ar(m, 0.03, 0.08)
        i = muestras(t)
        fin = min(n, i + m)
        x[i:fin] += s[: fin - i]
        t += d + rng.uniform(0.0, 0.25)
    return pa(x, 500)


def crujidos(dur, rng, densidad=6.0):
    n = muestras(dur)
    x = np.zeros(n, np.float32)
    for _ in range(int(dur * densidad)):
        c = clic(rng, rng.uniform(700, 2200), 0.05, 150) * rng.uniform(0.3, 1.0)
        i = int(rng.uniform(0, max(1, n - len(c))))
        x[i:i + len(c)] += c
    # Chirrido de hueso: sierra irregular muy grave filtrada.
    f = 40 + 25 * np.abs(np.sin(tiempo(n) * 3.1)) + rng.normal(0, 4, n).astype(np.float32)
    x += banda(sierra(f, n), 400, 1600) * 0.12
    return x


def aire_ahogado(dur, rng):
    n = muestras(dur)
    t = tiempo(n)
    jitter = np.repeat(rng.uniform(0.3, 1.0, int(dur * 30) + 1), muestras(1 / 30))[:n]
    x = banda(ruido(n, rng), 700, 3200) * jitter * env_ar(n, 0.15, 0.3)
    x += pb(sierra(70 + 10 * np.sin(t * 7), n), 300) * 0.25 * env_ar(n, 0.2, 0.3)
    return x


def vidrio_grieta(dur, rng):
    n = muestras(dur)
    x = np.zeros(n, np.float32)
    t = 0.0
    while t < dur:
        c = clic(rng, rng.uniform(3000, 7000), 0.03, 400) * rng.uniform(0.4, 1)
        i = muestras(t)
        fin = min(n, i + len(c))
        x[i:fin] += c[: fin - i]
        t += rng.uniform(0.005, 0.06) * (1 - t / dur * 0.7)
    return x + seno(6200, n) * env_exp(n, 0.3) * 0.1


def vidrio_rompe(rng):
    n = muestras(2.2)
    x = pa(ruido(n, rng), 2000) * env_exp(n, 0.25)
    for _ in range(45):
        m = muestras(rng.uniform(0.05, 0.2))
        tin = seno(rng.uniform(3000, 9000), m) * env_exp(m, 0.04)
        i = int(rng.uniform(0, n * 0.8) * (rng.random() ** 1.5))
        x[i:i + m] += tin[: max(0, min(m, n - i))] * rng.uniform(0.1, 0.5)
    return x


def falla(dur, rng):
    n = muestras(dur)
    x = ruido(n, rng)
    paso = int(rng.integers(8, 40))
    x = np.repeat(x[::paso], paso)[:n]
    zumb = np.sign(seno(rng.choice([60, 120, 240]), n)) * 0.3
    corte = np.repeat(rng.random(int(dur * 40) + 1) > 0.3, muestras(1 / 40))[:n]
    return ((x * 0.5 + zumb) * corte).astype(np.float32)


def estatica(dur, rng):
    n = muestras(dur)
    return banda(ruido(n, rng), 300, 9000) + (rng.random(n) > 0.9985).astype(np.float32) * rng.standard_normal(n) * 2


def jadeo(rng, dur=3.5, inicio=True):
    n = muestras(dur)
    x = np.zeros(n, np.float32)
    if inicio:
        m = muestras(0.45)
        tt = tiempo(m)
        fc = 600 + 1800 * tt / 0.45
        g = ruido(m, rng)
        g = np.concatenate([banda(g[i:i + 1200], max(fc[i] * 0.5, 100), fc[i] * 1.6) for i in range(0, m, 1200)])[:m]
        x[:m] += g * env_ar(m, 0.35, 0.05) * 1.8
    x[muestras(0.5):] += respiracion(dur - 0.5, rng, ritmo=lambda t: 2.4 - 0.35 * t, fuerza=1.0, nariz=False)[
        : n - muestras(0.5)] * np.linspace(1, 0.45, n - muestras(0.5), dtype=np.float32)
    return x


def sabanas(dur, rng):
    n = muestras(dur)
    grano = np.repeat(rng.random(int(dur * 60) + 1), muestras(1 / 60))[:n] ** 3
    return banda(ruido(n, rng), 900, 6000) * grano


def pajaros(dur, rng, densidad=1.5):
    n = muestras(dur)
    x = np.zeros(n, np.float32)
    for _ in range(int(dur * densidad)):
        notas = int(rng.integers(2, 6))
        t0 = rng.uniform(0, dur - 0.6)
        f0 = rng.uniform(2600, 5200)
        for k in range(notas):
            m = muestras(rng.uniform(0.05, 0.1))
            tt = tiempo(m)
            f = f0 * (1 + 0.25 * np.sin(math.pi * tt / (m / SR))) * rng.uniform(0.9, 1.1)
            s = seno(f, m) * env_ar(m, 0.01, 0.03)
            i = muestras(t0 + k * 0.11)
            fin = min(n, i + m)
            x[i:fin] += s[: fin - i] * 0.4
    return x


def viento(dur, rng):
    n = muestras(dur)
    return pb(ruido(n, rng, "rosa"), 700) * (0.7 + 0.3 * np.sin(2 * math.pi * 0.2 * tiempo(n)))


def campanada(rng, f=220):
    n = muestras(4.0)
    parciales = ((0.5, 1.0, 2.5), (1, 0.8, 1.8), (1.19, 0.5, 1.2), (1.5, 0.4, 1.0), (2.0, 0.35, 0.8), (2.74, 0.2, 0.5))
    return sum(seno(f * m, n) * env_exp(n, tau) * a for m, a, tau in parciales) * 0.3


def ladrido(rng):
    x = []
    for _ in range(2):
        m = muestras(0.16)
        tt = tiempo(m)
        f = 520 - 250 * tt / 0.16
        s = resonador(sierra(f, m), 900, 300) + resonador(sierra(f, m), 1600, 400) * 0.5
        x.append(s * env_ar(m, 0.01, 0.08) * 3)
        x.append(np.zeros(muestras(0.2), np.float32))
    return pb(np.concatenate(x), 2000)


def zumbido_giro(dur, rng):
    n = muestras(dur)
    t = tiempo(n)
    x = ruido(n, rng)
    lfo = 600 + 500 * np.sin(2 * math.pi * 5 * t)
    trozos = [banda(x[i:i + 960], max(lfo[i] * 0.6, 60), lfo[i] * 1.6) for i in range(0, n, 960)]
    return np.concatenate(trozos)[:n] * env_ar(n, 0.1, 0.2)


def caja_musical(notas, tempo=0.36, rng=None, desafina=0.0):
    """Caja musical: cada nota es una campanita con parciales inarmónicos."""
    rng = rng or np.random.default_rng(3)
    dur = len(notas) * tempo + 2.0
    x = np.zeros(muestras(dur), np.float32)
    t = 0.0
    for nota, largo in notas:
        if nota is not None:
            f = 440 * 2 ** ((nota - 69) / 12) * (1 + rng.normal(0, 0.004) + desafina)
            m = muestras(1.8)
            s = (seno(f, m) * env_exp(m, 0.9) + seno(f * 2.0, m) * env_exp(m, 0.35) * 0.35
                 + seno(f * 3.01, m) * env_exp(m, 0.18) * 0.2 + seno(f * 5.43, m) * env_exp(m, 0.05) * 0.15)
            s[:muestras(0.003)] += rng.standard_normal(muestras(0.003)) * 0.2
            i = muestras(t)
            fin = min(len(x), i + m)
            x[i:fin] += s[: fin - i]
        t += tempo * largo
    return x


# Canción de cuna original (3/4) para el recuerdo.
CANCION = [(67, 1), (72, 1), (76, 1), (74, 2), (72, 1), (69, 1), (72, 1), (77, 1), (76, 3), (67, 1), (72, 1), (76, 1),
           (79, 2), (77, 1), (76, 1), (74, 1), (71, 1), (72, 3)]


def cinta_frena(x, dur_frenado):
    """Frenado de cinta: la señal se hace más lenta y grave hasta detenerse."""
    n = len(x)
    m = muestras(dur_frenado)
    velocidad = np.clip(1 - tiempo(m) / dur_frenado, 0, 1) ** 1.5
    pos = np.cumsum(velocidad)
    pos = pos[pos < n - 1]
    return np.interp(pos, np.arange(n), x).astype(np.float32)


def clunk(rng):
    n = muestras(0.35)
    x = pb(ruido(n, rng), 900) * env_exp(n, 0.03) * 1.5
    x += seno(90, n) * env_exp(n, 0.08)
    x[muestras(0.12):] += clic(rng, 2600, 0.23, 300)[: n - muestras(0.12)] * 0.5
    return x


def rebobinado(dur, rng):
    n = muestras(dur)
    t = tiempo(n)
    f = 1800 + 900 * np.sin(2 * math.pi * 7 * t) + 3000 * t / dur
    return (seno(f, n) * 0.3 + banda(ruido(n, rng), 2000, 8000) * 0.4) * env_ar(n, 0.05, 0.05)


# --- voces sintéticas (espeak-ng) -----------------------------------------------------------------
#
# En el terror analógico las voces de computadora son parte del estilo. Si espeak-ng no está
# instalado, se usan las voces de caricatura de arriba.

VOZ_MAMA = "es-419+f4"
VOZ_ALEX = "mb-mx2"
VOZ_AVISO = "mb-mx1"


def tts(texto, voz, velocidad=160, tono=50, maximo=None):
    """Lee `texto` con espeak-ng y devuelve la señal a 48 kHz, o None si no hay espeak-ng.
    Si pasa de `maximo` segundos, la vuelve a leer más rápido."""
    exe = shutil.which("espeak-ng") or shutil.which("espeak")
    if not exe:
        return None
    for _ in range(4):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "voz.wav"
            r = subprocess.run([exe, "-v", voz, "-s", str(int(velocidad)), "-p", str(tono), "-w", str(ruta), texto],
                               capture_output=True)
            if r.returncode != 0 or not ruta.is_file() or ruta.stat().st_size < 1000:
                if voz.startswith("mb-"):
                    voz = "es-419"
                    continue
                return None
            with wave.open(str(ruta)) as w:
                sr = w.getframerate()
                x = np.frombuffer(w.readframes(w.getnframes()), "<i2").astype(np.float32) / 32768
        activo = np.flatnonzero(np.abs(x) > 0.01)
        if len(activo):
            x = x[max(0, activo[0] - 200):activo[-1] + 400]
        g = math.gcd(SR, sr)
        x = signal.resample_poly(x, SR // g, sr // g).astype(np.float32)
        if maximo is None or len(x) / SR <= maximo:
            break
        velocidad *= min(1.6, len(x) / SR / maximo * 1.05)
    return x / (np.abs(x).max() + 1e-9)


def al_aire(x, rng, bajos=300, altos=3400, sucio=1.6):
    """Voz de transmisión: banda de teléfono y un poco de saturación."""
    y = banda(x, bajos, altos)
    return np.tanh(y * sucio) / math.tanh(sucio)


def alerta(dur):
    """Tono de atención de las alertas de emergencia (dos senos disonantes)."""
    n = muestras(dur)
    return ((seno(853, n) + seno(960, n)) * 0.5 * env_ar(n, 0.01, 0.02)).astype(np.float32)


def temblor_de_cinta(x, profundidad=1.0):
    """Wow y flutter: la velocidad de la cinta varía un poco y la afinación ondula."""
    n = len(x)
    t = np.arange(n, dtype=np.float64) / SR
    desvio = (0.0022 * SR / (2 * math.pi * 0.45) * np.sin(2 * math.pi * 0.45 * t)
              + 0.0005 * SR / (2 * math.pi * 6.3) * np.sin(2 * math.pi * 6.3 * t)) * profundidad
    pos = np.clip(np.arange(n) + desvio, 0, n - 1)
    base = np.arange(n)
    return np.stack([np.interp(pos, base, x[:, c]) for c in range(x.shape[1])], axis=1).astype(np.float32)


# --- la mezcla por escena -----------------------------------------------------------------------

def generar(linea, ruta, cinta=True):
    """linea: [(id, inicio, duración)]. Escribe un WAV estéreo de 16 bits.

    cinta=False quita todo lo de la videocasetera (siseo, zumbido, clunks, estática, temblor de cinta)
    para la versión pintada.
    """
    total = max(i + d for _, i, d in linea)
    P = Pista(total)
    rng = np.random.default_rng(2026)
    T = {ident: (ini, dur) for ident, ini, dur in linea}

    def en(ident, t=0.0):
        return T[ident][0] + t

    if cinta:
        hiss = pb(pa(ruido(muestras(total), rng), 3000), 12000) * 0.004
        P.poner(hiss, 0)

    # Gancho.
    if "Gancho" in T:
        d = T["Gancho"][1]
        P.poner(cluster(d, rng, 520) * env_ar(muestras(d), 0.05, 0.1), en("Gancho"), 0.35)
        P.poner(latidos(d, 120, rng), en("Gancho"), 0.9)
        P.poner(falla(0.25, rng), en("Gancho", 0.0), 0.25)
        P.poner(falla(0.3, rng), en("Gancho", 0.9), 0.3)
        P.poner(estatica(0.35, rng) * np.linspace(0, 1, muestras(0.35), dtype=np.float32), en("Gancho", 1.15), 0.35)
        P.poner(rebobinado(0.4, rng), en("Gancho", 1.1), 0.25)

    # Barras de color: la videocasetera arranca y suena el tono de prueba.
    if "Barras" in T:
        ib, db = T["Barras"]
        P.poner(clunk(rng), ib, 0.5)
        n = muestras(db - 0.1)
        P.poner(seno(1000, n) * env_ar(n, 0.01, 0.01), ib + 0.05, 0.1)

    # Escena 1: la cena.
    ini, dur = T["1A"]
    if cinta:
        P.poner(clunk(rng), ini, 0.6)
    fin_cena = T["1C"][0] + T["1C"][1]
    largo = fin_cena - ini
    ambiente = zumbido(largo) * 0.05 + tono_cuarto(largo, rng) * 0.25
    P.poner(ambiente, ini)
    # Plática de la familia: clara al principio, bajo el agua cuando la cámara llega a Alex.
    d1a, d1b = T["1A"][1], T["1B"][1]
    platica = murmullo(d1a + 5.1, 205, 1) * 0.55 + murmullo(d1a + 5.1, 118, 2, 0.6) * 0.5 + murmullo(d1a + 5.1, 240, 3, 0.5) * 0.35
    for t_risa, f, veces, g in ((1.2, 120, 5, 0.8), (2.0, 260, 4, 0.5)):
        r = risa(f, veces, int(t_risa * 10))
        platica[muestras(t_risa):muestras(t_risa) + len(r)] += r * g
    t_pl = tiempo(len(platica))
    ahoga = np.clip((t_pl - 2.2) / 4.0, 0, 1)
    platica = platica * (1 - ahoga) + pb(platica, 380, 4) * ahoga * 1.4
    platica *= (1 - 0.35 * ahoga)
    platica[muestras(d1a + 4.9):] *= np.linspace(1, 0, len(platica) - muestras(d1a + 4.9), dtype=np.float32) ** 3
    P.poner(reverb(platica, 0.8, 0.15, rng), ini, 0.28)
    for k in range(26):
        t = rng.uniform(0, d1a + 4.5)
        s = tintineo(rng) if rng.random() < 0.7 else clic(rng, 1200, 0.1, 200)
        ahogo_t = min(max((t - 2.2) / 4.0, 0), 1)
        s = s * (1 - ahogo_t) + pb(s, 500) * ahogo_t
        P.poner(s, ini + t, rng.uniform(0.04, 0.1), rng.uniform(-0.6, 0.6))
    P.poner(drone(d1a - 2.5 + d1b, rng, 41.2, 220) * env_ar(muestras(d1a - 2.5 + d1b), 3.0, 0.4), ini + 2.5, 0.12)
    # 1B: la voz de mamá amortiguada, el mensaje y el «¿Alex?» que corta.
    i1b = T["1B"][0]
    linea1 = tts("y entonces le dije a tu tía que no íbamos a poder ir el domingo", VOZ_MAMA, 185, 55, maximo=3.9)
    if linea1 is None:
        linea1 = voz("y en ton ces le di je a tu tí a que no í ba mos a po der ir el do min go".split(), 215, 11,
                     ritmo=0.165)
    P.poner(reverb(pb(linea1, 450, 4), 0.6, 0.2, rng), i1b + 0.8, 0.2)
    P.poner(acufeno(1.8, 6900) * env_ar(muestras(1.8), 0.5, 0.6), i1b + 3.0, 0.01)
    burbuja = seno(np.linspace(880, 1320, muestras(0.09)), muestras(0.09)) * env_ar(muestras(0.09), 0.005, 0.05)
    P.poner(burbuja, i1b + 5.55, 0.12)
    alex = tts("¿Alex?", VOZ_MAMA, 150, 60, maximo=0.8)
    if alex is None:
        alex = voz(["¿A", "lex?"], 225, 12, ritmo=0.2, pregunta=True, brillo=1.3)
    alex = al_aire(alex, rng, 200, 4200, 1.2)
    P.poner(reverb(alex, 0.7, 0.18, rng), i1b + 5.25, 0.2)
    linea2 = tts("¿Me estás escuchando, mijo?", VOZ_MAMA, 165, 60, maximo=1.8)
    if linea2 is None:
        linea2 = voz("me es tás es cu chan do mi jo".split(), 230, 13, ritmo=0.165, pregunta=True, brillo=1.3)
    linea2 = al_aire(linea2, rng, 200, 4200, 1.2)
    P.poner(reverb(linea2, 0.7, 0.18, rng), i1b + 6.05, 0.22)
    # 1C: bloquea el celular y contesta.
    i1c = T["1C"][0]
    P.poner(clic(rng, 1800, 0.05, 200), i1c + 0.9, 0.25)
    respuesta = tts("Sí, ma. Todo bien.", VOZ_ALEX, 140, 42, maximo=1.6)
    if respuesta is None:
        respuesta = voz(["sí,|", "ma.|", "to", "do", "bien"], 112, 14, ritmo=0.2, brillo=0.9)
    respuesta = al_aire(respuesta, rng, 150, 4000, 1.2)
    P.poner(reverb(respuesta, 0.7, 0.15, rng), i1c + 2.2, 0.24)
    platica2 = murmullo(2.0, 210, 21) * 0.5 + murmullo(2.0, 120, 22) * 0.4
    P.poner(reverb(pb(platica2, 700) * env_ar(muestras(2.0), 0.6, 0.3), 0.8, 0.2, rng), i1c + 4.1, 0.14)
    for k in range(4):
        P.poner(tintineo(rng), i1c + 4.2 + k * 0.4, 0.05, rng.uniform(-0.5, 0.5))
    P.poner(drone(2.0, rng, 36.7, 180) * env_ar(muestras(2.0), 1.5, 0.05), i1c + 4.0, 0.16)

    # Escena 2: las tres sombras.
    i2, fin2 = T["2A"][0] + 1.0, T["2D"][0] + T["2D"][1]
    cuarto = tono_cuarto(fin2 - i2, rng, 160) * 0.18 + ventilador_sonido(fin2 - i2, rng) * 0.05
    cuarto *= env_ar(muestras(fin2 - i2), 1.0, 0.05)
    P.poner(cuarto, i2)
    P.poner(reloj(fin2 - i2, rng) * 0.05, i2)
    d2a, d2b = T["2A"][1], T["2B"][1]
    P.poner(respiracion(d2a + d2b, rng, lambda t: 0.28 if t < d2a + 3 else 0.28 + 0.1 * (t - d2a - 3)), T["2A"][0] + 0.8, 0.09)
    P.poner(reverb(ladrido(rng), 2.5, 0.5, rng) * 0.2, en("2A", 4.2), 0.3, -0.7)
    P.poner(crujidos(0.6, rng, 8), en("2A", 6.0), 0.1, 0.4)
    P.poner(drone(2.6, rng, 49, 260) * env_ar(muestras(2.6), 2.0, 0.6), en("2B", 0.2), 0.16)
    P.poner(swell_reverso(1.6, rng), en("2B", 0.0), 0.22)
    P.poner(golpe(rng, 0.6), en("2B", 1.6), 0.35)
    fin_acufeno = T["3C"][0] + 4.35
    P.poner(acufeno(fin_acufeno - en("2B", 2.0)) * np.linspace(0, 1, muestras(fin_acufeno - en("2B", 2.0)), dtype=np.float32) ** 1.5,
            en("2B", 2.0), 0.02)
    tension = T["3C"][0] + 4.35 - en("2B", 3.0)
    P.poner(cluster(tension, rng, 330) * np.linspace(0.2, 1, muestras(tension), dtype=np.float32), en("2B", 3.0), 0.12)
    P.poner(drone(tension, rng, 41.2, 400) * np.linspace(0.3, 1, muestras(tension), dtype=np.float32), en("2B", 3.0), 0.2)
    d2c = T["2C"][1]
    P.poner(latidos(d2c + T["2D"][1], lambda t: 88 + 4 * t, rng), en("2C"), 0.9)
    P.poner(respiracion(d2c + 5, rng, 0.9, nariz=True), en("2C"), 0.1)
    P.poner(sabanas(d2c, rng), en("2C"), 0.03)
    P.poner(zumbido_giro(6.0, rng), en("2D", 0.5), 0.1)
    P.poner(swell_reverso(1.2, rng), en("2D", 5.0), 0.15)

    # Escena 3: la parálisis.
    i3 = T["3A"][0]
    P.poner(golpe(rng, 1.0), i3, 0.6)
    P.poner(cluster(0.9, rng, 660) * env_exp(muestras(0.9), 0.4), i3, 0.3)
    P.poner(jadeo(rng, 0.5, True)[: muestras(0.5)], i3 - 0.05, 0.35)
    d3 = T["3A"][1] + T["3B"][1] + 4.35
    P.poner(latidos(d3, lambda t: 112 + 3 * t, rng), i3, 1.1)
    P.poner(crujidos(3.2, rng, 5), en("3A", 2.0), 0.16, 0.2)
    P.poner(susurros(d3, rng), i3, 0.03, -0.3)
    P.poner(aire_ahogado(T["3B"][1], rng), en("3B"), 0.12)
    P.poner(crujidos(4.2, rng, 9), en("3C", 0.2), 0.2, 0.5)
    P.poner(swell_reverso(1.1, rng), en("3C", 3.25), 0.4)

    # Escena 4: el recuerdo.
    i4, d4 = T["4A"]
    P.poner(pa(swell_reverso(0.6, rng)[::-1].copy(), 800), i4, 0.2)
    campo = pajaros(d4, rng, 1.8) * 0.25 + viento(d4, rng) * 0.2
    P.poner(reverb(campo * env_ar(muestras(d4), 1.0, 0.1), 1.5, 0.3, rng), i4, 0.8)
    musica = caja_musical(CANCION, 0.4, rng, desafina=-0.004)
    corte = muestras(d4 - 0.3)  # la música empieza en 0.3 s y se frena justo cuando el recuerdo se congela
    frenado = cinta_frena(musica[corte:], 0.9)
    musica = np.concatenate([musica[:corte], frenado])
    P.poner(reverb(musica * env_ar(len(musica), 0.8, 0.05), 2.2, 0.35, rng), i4 + 0.3, 0.14)
    for t_risa, f in ((2.4, 330), (5.3, 300)):
        P.poner(reverb(risa(f, 4, int(t_risa * 10)), 2.0, 0.5, rng), i4 + t_risa, 0.08, 0.3)

    # Escena 5: el despertar.
    i5 = T["5A"][0]
    P.poner(vidrio_grieta(0.8, rng), i5 + 0.05, 0.25)
    P.poner(vidrio_rompe(rng), i5 + 0.9, 0.35)
    P.poner(golpe(rng, 1.0), i5 + 0.9, 0.55)
    P.poner(acufeno(T["5F"][0] + 3.0 - (i5 + 1.2)) * env_ar(muestras(T["5F"][0] + 3.0 - (i5 + 1.2)), 0.6, 2.5), i5 + 1.2, 0.02)
    for ident, extra in (("5B", "hueso"), ("5C", "giro"), ("5D", "puño")):
        t0, d = T[ident]
        P.poner(falla(d * 0.6, rng), t0, 0.22)
        P.poner(golpe(rng, 0.8, 0.9), t0, 0.35)
        if extra == "hueso":
            P.poner(crujidos(d, rng, 30), t0, 0.35)
        elif extra == "giro":
            P.poner(zumbido_giro(d, rng), t0, 0.4)
        else:
            P.poner(crujidos(0.4, rng, 25), t0 + 0.15, 0.3)
            P.poner(golpe(rng, 1.0, 0.9), t0 + 0.45, 0.4)
    i5e, d5e = T["5E"]
    P.poner(jadeo(rng, d5e, True), i5e + 0.12, 0.35)
    P.poner(sabanas(0.7, rng), i5e + 0.15, 0.08)
    P.poner(latidos(d5e, lambda t: 120 - 10 * t, rng), i5e, 0.7 * 1.0)
    i5f, d5f = T["5F"]
    P.poner(tono_cuarto(d5f, rng, 140) * env_ar(muestras(d5f), 1.5, 0.05), i5f, 0.1)
    P.poner(reloj(d5f, rng, 0.8) * 0.03, i5f)

    # Escena 6: la incisión.
    i6 = T["6A"][0]
    fin6 = T["6C"][0] + T["6C"][1] - 0.12
    manana = pajaros(fin6 - i6, rng, 1.2) * 0.2 + tono_cuarto(fin6 - i6, rng, 300) * 0.25 + zumbido(fin6 - i6, 120) * 0.01
    agacha = np.ones(muestras(fin6 - i6), np.float32)
    t_rel = tiempo(len(agacha))
    agacha *= np.clip(1 - (t_rel - (T["6B"][0] + 0.8 - i6)) / 2.0, 0.25, 1)
    P.poner(reverb(manana * agacha, 1.0, 0.2, rng), i6)
    P.poner(reverb(campanada(rng, 196), 3.0, 0.5, rng), i6 + 1.5, 0.05, -0.6)
    P.poner(clic(rng, 3000, 0.08, 150), i6 + 6.5, 0.05)
    tono = fin6 - (T["6B"][0] + 0.8)
    n_tono = muestras(tono)
    subida = seno(np.linspace(38, 52, n_tono), n_tono) * np.linspace(0, 1, n_tono, dtype=np.float32) ** 1.5
    P.poner(subida + acufeno(tono, 3100) * 0.02, T["6B"][0] + 0.8, 0.3)
    P.poner(latidos(fin6 - T["6B"][0] - 1.5, lambda t: 70 + 6 * t, rng), T["6B"][0] + 1.5, 0.6)
    i6c = T["6C"][0]
    P.poner(golpe(rng, 1.0, 2.0), i6c + 1.3, 0.6)
    P.poner(cluster(fin6 - i6c - 1.3, rng, 590) * np.linspace(1, 0.6, muestras(fin6 - i6c - 1.3), dtype=np.float32), i6c + 1.3, 0.2)
    P.poner(drone(fin6 - i6c, rng, 36.7, 500) * np.linspace(0.4, 1, muestras(fin6 - i6c), dtype=np.float32), i6c, 0.28)

    # Aviso a la población: tono de alerta, voz de la transmisión y zumbido.
    if "Aviso" in T:
        from planos import AVISO
        ia, da = T["Aviso"]
        P.poner(alerta(1.4), ia + 0.05, 0.16)
        cama = zumbido(da, 60) * 0.35 + drone(da, rng, 43.65, 300) * 0.5
        P.poner(cama * env_ar(muestras(da), 0.3, 0.4), ia, 0.12)
        siguientes = [a[0] for a in AVISO[1:]] + [da - 0.3]
        for (inicio, _, dicho), fin in zip(AVISO, siguientes):
            x = tts(dicho, VOZ_AVISO, 150, 28, maximo=fin - inicio - 0.15)
            if x is None:
                x = voz(dicho.lower().replace(",", "").replace(".", "").split(), 105, int(inicio * 10), ritmo=0.17)
            P.poner(reverb(al_aire(x, rng), 0.5, 0.12, rng), ia + inicio, 0.3)

    # Título.
    it, dt = T["Título"]
    P.poner(golpe(rng, 1.2, 3.0), it + 0.35, 0.7)
    if cinta:
        P.poner(falla(0.25, rng), it + 0.33, 0.2)
    for k in range(12):
        P.poner(clic(rng, 2400, 0.03, 200), it + 0.75 + k * 0.095, 0.08)
    P.poner(drone(dt - 0.5, rng, 32.7, 260) * env_ar(muestras(dt - 0.5), 0.3, 1.2), it + 0.35, 0.18)
    if cinta:
        P.poner(falla(0.15, rng), it + 2.95, 0.15)
        P.poner(clunk(rng), it + 3.3, 0.5)
        P.poner(estatica(0.45, rng), it + 3.55, 0.3)

    # Silencios: el negro después de 1C y el corte seco al final de 6C.
    x = P.x
    corte_final = T["Aviso"][0] if "Aviso" in T else it + 0.33
    for inicio, fin in ((T["Negro"][0] + 0.02, T["Negro"][0] + T["Negro"][1]), (fin6, corte_final)):
        a, b = muestras(inicio), muestras(fin)
        x[a:b] *= 0.05
    if cinta:
        # En el negro solo queda el pitido de la hora (03:17 A.M.).
        pitido = seno(1000, muestras(0.12)) * env_ar(muestras(0.12), 0.005, 0.01)
        P.poner(pitido, T["Negro"][0] + 0.06, 0.12)
        # Zumbido de la tele y siseo constantes: la cinta nunca está en silencio del todo.
        P.poner(zumbido(total, 60) * 0.004 + pb(pa(ruido(muestras(total), rng), 2500), 9000) * 0.003, 0)

    # Maestro: (temblor de cinta y ancho de banda de VHS), compresión suave y pico a -1 dB.
    if cinta:
        x = temblor_de_cinta(P.x)
        x = pb(pa(x, 28), 11000, 4)
    else:
        x = pa(P.x, 28)
    rms = np.sqrt(np.mean(x ** 2)) + 1e-9
    x = x * (0.11 / rms)
    x = np.tanh(x * 1.3) / 1.3
    x = x / (np.abs(x).max() + 1e-9) * 0.89
    x = x[: muestras(total)]
    with wave.open(str(ruta), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype("<i2").tobytes())
    return ruta
