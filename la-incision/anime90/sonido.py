"""Banda sonora del terror anime de los 90, sintetizada desde cero.

Sintetizadores de la época (pads anchos con filtro que se abre), coro sin vibrato en quintas abiertas,
violines que chillan en glissando, tambores graves espaciados y una caja musical para el recuerdo. Mucho
silencio, ambiente muy presente y foley marcado, como en un OVA. Sin efectos de VHS.

Reutiliza las herramientas de bajo nivel de animacion/sonido.py (filtros, ruido, voces de espeak-ng, ambientes).
"""

import math
import sys
import wave
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "animacion"))

import sonido as b  # noqa: E402
from sonido import SR, Pista, env_ar, env_exp, muestras, pb, pa, banda, resonador, seno, sierra, tiempo  # noqa: E402


# --- instrumentos ------------------------------------------------------------------------------------

def pad(dur, notas, rng, abre=(500, 2600), ataque=1.5, caida=1.5, chorus=0.004):
    """Pad de sintetizador de los 90: sierras desafinadas, filtro que se abre y un chorus lento."""
    n = muestras(dur)
    t = tiempo(n)
    x = np.zeros(n, np.float32)
    for f in notas:
        for cent in (-chorus, 0.0, chorus):
            vib = 1 + 0.0012 * np.sin(2 * math.pi * 0.3 * t + rng.uniform(0, 6))
            x += sierra(f * (1 + cent) * vib, n) * 0.25
    corte = np.linspace(abre[0], abre[1], n)
    salida = np.zeros(n, np.float32)
    paso = 2048
    for i in range(0, n, paso):
        salida[i:i + paso] = pb(x[i:i + paso], float(corte[i]), 2)
    return salida * env_ar(n, ataque, caida)


def coro(dur, notas, rng, vocal="a", ataque=1.8, caida=2.0):
    """Coro sin vibrato: una fuente glotal cantada en armonías abiertas, con un soplo de aire."""
    n = muestras(dur)
    formantes = {"a": (800, 1250, 2650), "o": (480, 880, 2500), "u": (330, 800, 2400)}[vocal]
    total = np.zeros(n, np.float32)
    for f in notas:
        for cent in (-0.0025, 0.0, 0.0025):
            fuente = sierra(f * (1 + cent), n) + 0.05 * b.ruido(n, rng)
            voz = (resonador(fuente, formantes[0], 90) + resonador(fuente, formantes[1], 120) * 0.5
                   + resonador(fuente, formantes[2], 180) * 0.22)
            total += voz * 0.12
    return pb(total, 6000) * env_ar(n, ataque, caida)


def violin_chillido(dur, f0, f1, rng, fuerza=1.0):
    """Violines agudos que suben en glissando y tiemblan, al estilo de los sustos de Sagisu."""
    n = muestras(dur)
    t = tiempo(n)
    f = f0 + (f1 - f0) * (t / dur) ** 1.5
    vib = 1 + (0.004 + 0.012 * t / dur) * np.sin(2 * math.pi * 6.5 * t)
    x = np.zeros(n, np.float32)
    for cent in (-0.006, 0.0, 0.007, 0.012):
        x += sierra(f * vib * (1 + cent), n) * 0.3
    x = banda(x, 900, 7500) + 0.2 * banda(b.ruido(n, rng), 2500, 9000) * env_ar(n, 0.02, dur * 0.5)
    return np.tanh(x * 1.6) * env_ar(n, 0.08, dur * 0.35) * fuerza * 0.45


def taiko(rng, grave=1.0, dur=2.6):
    """Golpe de tambor grave con cola larga."""
    n = muestras(dur)
    t = tiempo(n)
    f = 46 + 90 * np.exp(-t * 14)
    x = np.sin(2 * math.pi * np.cumsum(f) / SR).astype(np.float32) * env_exp(n, 0.55) * grave
    x += pb(b.ruido(n, rng), 900) * env_exp(n, 0.03) * 0.9
    x += resonador(b.ruido(n, rng) * env_exp(n, 0.08), 140, 60) * 0.12
    return np.tanh(x * 1.5).astype(np.float32)


def campana_grave(rng, f=110.0, dur=7.0):
    """Campana o gong de cierre, con parciales inarmónicos."""
    n = muestras(dur)
    parciales = ((1.0, 1.0, 3.5), (2.0, 0.6, 2.6), (2.76, 0.5, 2.0), (4.16, 0.32, 1.4), (5.4, 0.2, 0.9), (6.9, 0.12, 0.6))
    x = sum(seno(f * m, n) * env_exp(n, tau) * a for m, a, tau in parciales)
    x += pb(b.ruido(n, rng), 2500) * env_exp(n, 0.06) * 0.4
    return (x * 0.35).astype(np.float32)


def golpe_de_cuerdas(rng, dur=1.6, base=880.0):
    """Sting corto de cuerdas en racimo (segunda menor) con ataque seco."""
    n = muestras(dur)
    x = np.zeros(n, np.float32)
    for m in (1.0, 1.0595, 1.335, 1.5, 2.0):
        x += sierra(base * m * (1 + rng.normal(0, 0.002)), n)
    return banda(x, 500, 6500) * env_exp(n, 0.5) * 0.28


def whoosh(dur, rng, sube=True):
    n = muestras(dur)
    t = tiempo(n)
    g = (t / dur) ** 2 if sube else (1 - t / dur) ** 2
    return banda(b.ruido(n, rng), 300, 5500) * g.astype(np.float32) * 0.6


def hz(nota):
    return 440 * 2 ** ((nota - 69) / 12)


# --- voz ---------------------------------------------------------------------------------------------

def voz_mama(texto, maximo=None):
    x = b.tts(texto, b.VOZ_MAMA, velocidad=165, tono=62, maximo=maximo)
    return x if x is not None else b.voz(texto.lower().replace(",", "").replace("¿", "").replace("?", "").split(), 230)


def voz_alex(texto, maximo=None):
    x = b.tts(texto, b.VOZ_ALEX, velocidad=150, tono=42, maximo=maximo)
    return x if x is not None else b.voz(["si", "ma|", "to", "do", "bien"], 130)


# --- la mezcla ---------------------------------------------------------------------------------------

def generar(linea, ruta):
    T = {i: (ini, dur) for i, ini, dur in linea}
    total = sum(d for _, _, d in linea)
    rng = np.random.default_rng(1997)
    P = Pista(total)

    def en(plano, seg=0.0):
        return T[plano][0] + seg

    # ---- ESCENA 1: la cena, cálida y ruidosa --------------------------------------------------------
    ini, dur = T["1A"]
    P.poner(b.tono_cuarto(dur + 16, rng, 260), ini, 0.12)
    P.poner(b.murmullo(dur, 190, 3) * 0.6, ini, 0.35, pan=-0.5)
    P.poner(b.murmullo(dur, 130, 8) * 0.6, ini, 0.3, pan=0.1)
    P.poner(b.murmullo(dur, 240, 12) * 0.6, ini, 0.3, pan=0.5)
    for k in range(9):
        P.poner(b.tintineo(rng, rng.uniform(1800, 3200)), ini + rng.uniform(0.3, dur - 0.5), rng.uniform(0.03, 0.08),
                pan=rng.uniform(-0.8, 0.8))
    # 1B: la plática se vuelve zumbido; la mamá habla al otro lado
    ini, dur = T["1B"]
    zumb = pb(b.murmullo(dur, 170, 21) + b.murmullo(dur, 210, 22), 700)
    P.poner(zumb, ini, 0.32 + 0.18 * np.linspace(0, 1, 1)[0])
    P.poner(b.zumbido(dur, 58), ini, 0.05)
    for k in range(6):
        P.poner(b.clic(rng, 3400, 0.03, 200), ini + 0.6 + k * 1.05 + rng.uniform(0, 0.3), 0.18, pan=0.2)
    m1 = voz_mama("Y entonces le dije a tu tía que no íbamos a poder ir el domingo.", maximo=3.6)
    P.poner(b.reverb(pb(m1, 900), 0.6, 0.22, rng), ini + 0.8, 0.55, pan=-0.35)
    P.poner(b.reverb(pb(voz_mama("¿Alex?"), 1100), 0.6, 0.25, rng), ini + 5.25, 0.6, pan=-0.35)
    m3 = voz_mama("¿Me estás escuchando, mijo?", maximo=1.75)
    P.poner(b.reverb(pb(m3, 1400), 0.6, 0.2, rng), ini + 6.05, 0.7, pan=-0.35)
    P.poner(pad(dur, [hz(38), hz(45)], rng, abre=(120, 400), ataque=4.0, caida=1.0), ini, 0.09 * 1.0)
    # 1C: el clic del celular y la respuesta
    ini, dur = T["1C"]
    P.poner(b.tono_cuarto(dur, rng, 240), ini, 0.1)
    P.poner(b.murmullo(dur, 190, 33) * 0.6, ini, 0.14, pan=-0.5)
    P.poner(b.clic(rng, 2800, 0.05, 260) * 1.6, ini + 0.9, 0.5)
    ax = voz_alex("Sí, ma. Todo bien.", maximo=1.5)
    P.poner(b.reverb(pb(ax, 4500), 0.5, 0.15, rng), ini + 2.2, 0.85, pan=0.05)
    P.poner(pad(dur - 2.0, [hz(38), hz(45), hz(50)], rng, abre=(150, 900), ataque=2.5, caida=1.5), ini + 2.0, 0.12)
    P.poner(b.latidos(dur - 3.5, 58, rng, 1.0), ini + 3.5, 0.18)
    # negro: casi silencio y el reloj
    ini, dur = T["Negro"]
    P.poner(b.reloj(dur + 1, rng), ini, 0.25)

    # ---- ESCENA 2: el cuarto, silencio pesado y el coro ---------------------------------------------
    ini, dur = T["2A"]
    P.poner(b.tono_cuarto(dur, rng, 180), ini, 0.12)
    P.poner(b.reloj(dur, rng), ini, 0.16, pan=0.7)
    P.poner(b.respiracion(dur, rng, ritmo=0.25, fuerza=1.0), ini, 0.16)
    P.poner(b.ventilador_sonido(dur, rng), ini, 0.04)
    P.poner(pad(dur, [hz(29), hz(36), hz(41)], rng, abre=(90, 380), ataque=3.0, caida=0.5), ini, 0.16)
    P.poner(b.sabanas(1.2, rng), ini + 4.5, 0.05)
    ini, dur = T["2B"]
    P.poner(b.tono_cuarto(dur, rng, 180), ini, 0.1)
    P.poner(b.reloj(dur, rng), ini, 0.14, pan=0.7)
    P.poner(b.respiracion(dur, rng, ritmo=lambda t: 0.25 + 0.05 * t, fuerza=1.0), ini, 0.16)
    P.poner(pad(dur, [hz(29), hz(36), hz(41)], rng, abre=(120, 700), ataque=1.0, caida=1.0), ini, 0.17)
    notas_coro = (hz(50), hz(57), hz(62))       # sol, re, fa♯ · quintas abiertas y una sensible que raspa
    for k, aparece in enumerate((2.2, 3.6, 4.9)):
        x = coro(dur - aparece + 0.6, [notas_coro[k]], rng, ataque=1.2, caida=1.5)
        P.poner(b.reverb(x, 2.4, 0.35, rng), ini + aparece, 0.34, pan=(-0.5, 0.0, 0.5)[k])
        P.poner(violin_chillido(0.9, 1800 + 200 * k, 2600 + 300 * k, rng, 0.45), ini + aparece, 0.4, pan=(-0.4, 0.0, 0.4)[k])
        P.poner(taiko(rng, 0.8), ini + aparece, 0.35)
    ini, dur = T["2C"]
    P.poner(b.tono_cuarto(dur, rng, 200), ini, 0.1)
    P.poner(b.latidos(dur, 84, rng, 1.0), ini, 0.4)
    P.poner(b.respiracion(dur, rng, ritmo=0.6, fuerza=1.0), ini, 0.16)
    P.poner(b.acufeno(dur, 7600), ini, 0.025 * 1.0)
    P.poner(coro(dur + 0.8, [hz(50), hz(57), hz(62)], rng, ataque=0.3, caida=0.8), ini, 0.22)
    ini, dur = T["2D"]
    P.poner(b.latidos(dur, lambda t: 84 + 10 * t, rng, 1.0), ini, 0.42)
    P.poner(b.tono_cuarto(dur, rng, 200), ini, 0.09)
    P.poner(b.reverb(coro(dur, [hz(38), hz(45), hz(50), hz(62)], rng, ataque=1.0, caida=2.0), 3.0, 0.4, rng), ini, 0.34)
    P.poner(pad(dur, [hz(29), hz(36), hz(41), hz(43)], rng, abre=(200, 1800), ataque=0.5, caida=2.0), ini, 0.16)
    for corte, gr in ((1.5, 0.6), (2.9, 0.75), (4.2, 0.9), (5.4, 1.0)):
        P.poner(taiko(rng, gr), ini + corte, 0.55 + 0.1 * gr)
        P.poner(violin_chillido(0.7, 2000, 2600, rng, 0.4), ini + corte, 0.28)
    P.poner(b.swell_reverso(2.4, rng), ini + 5.4, 0.18)
    P.poner(b.sabanas(1.5, rng), ini + 3.3, 0.08)

    # ---- ESCENA 3: la parálisis ---------------------------------------------------------------------
    ini, dur = T["3A"]
    P.poner(whoosh(0.3, rng, sube=False) * 2.0, ini, 0.5)
    P.poner(taiko(rng, 1.0), ini, 0.6)
    P.poner(b.reverb(coro(dur, [hz(38), hz(45), hz(50), hz(51)], rng, ataque=0.4, caida=1.5), 3.0, 0.4, rng), ini, 0.4)
    P.poner(pad(dur, [hz(29), hz(36), hz(41), hz(43)], rng, abre=(400, 2200), ataque=0.3, caida=1.5), ini, 0.16)
    P.poner(b.latidos(dur, 96, rng, 1.0), ini, 0.4)
    P.poner(b.susurros(dur, rng), ini, 0.15)
    ini, dur = T["3B"]
    P.poner(b.acufeno(dur, 6900), ini, 0.05)              # el grito no suena: solo un pitido y presión
    P.poner(b.latidos(dur, 110, rng, 1.0), ini, 0.5)
    P.poner(pb(b.ruido(muestras(dur), rng, "rosa"), 90) * 0.5, ini, 0.9)
    P.poner(b.reverb(coro(dur, [hz(45), hz(52), hz(57), hz(58)], rng, vocal="o", ataque=0.2, caida=1.0), 3.0, 0.4, rng),
            ini, 0.26)
    ini, dur = T["3C"]
    P.poner(b.acufeno(dur, 6900), ini, 0.03)
    P.poner(b.latidos(dur - 0.7, 96, rng, 1.0), ini, 0.4)
    P.poner(pad(dur, [hz(29), hz(36), hz(41), hz(43)], rng, abre=(200, 2600), ataque=1.0, caida=0.1), ini, 0.16)
    P.poner(violin_chillido(dur - 0.7, 900, 3400, rng, 0.85), ini + 0.3, 0.4)
    P.poner(b.sabanas(3.0, rng), ini + 1.0, 0.07)
    P.poner(b.swell_reverso(dur - 0.7, rng), ini, 0.25)

    # ---- ESCENA 4: el recuerdo, una caja musical y pájaros ------------------------------------------
    ini, dur = T["4A"]
    P.poner(b.pajaros(dur, rng, 1.6), ini, 0.28, pan=0.3)
    P.poner(b.viento(dur, rng), ini, 0.08)
    caja = b.caja_musical([(n_ + 0, l) for n_, l in b.CANCION], 0.42, rng)
    P.poner(b.reverb(caja, 2.5, 0.35, rng), ini + 0.6, 0.2)
    P.poner(pad(dur, [hz(60), hz(64), hz(67), hz(72)], rng, abre=(900, 4200), ataque=2.0, caida=2.0), ini, 0.07)
    P.poner(b.reverb(coro(dur, [hz(60), hz(67), hz(72)], rng, ataque=2.0, caida=2.0), 3.0, 0.4, rng), ini, 0.06)
    P.poner(b.risa(300, 4, 5), ini + 3.5, 0.10, pan=-0.4)
    P.poner(b.risa(420, 3, 6), ini + 5.0, 0.09, pan=0.4)

    # ---- ESCENA 5: el despertar ---------------------------------------------------------------------
    ini, dur = T["5A"]
    P.poner(b.vidrio_grieta(0.9, rng), ini, 0.6)
    P.poner(b.vidrio_rompe(rng), ini + 0.9, 0.9)
    P.poner(taiko(rng, 1.0), ini + 0.9, 0.8)
    P.poner(b.reverb(pb(caja, 1500), 2.5, 0.35, rng), ini, 0.14)
    P.poner(b.swell_reverso(dur, rng), ini, 0.2)
    for plano in ("5B", "5C", "5D"):
        i2, d2 = T[plano]
        P.poner(taiko(rng, 1.0, 1.4), i2, 0.6)
        P.poner(golpe_de_cuerdas(rng), i2, 0.45)
        P.poner(whoosh(0.5, rng, sube=False), i2, 0.35)
    ini, dur = T["5E"]
    P.poner(b.jadeo(rng, dur, True), ini + 0.1, 0.5)
    P.poner(b.latidos(dur, lambda t: 128 - 12 * t, rng, 1.0), ini, 0.5)
    P.poner(b.acufeno(dur, 7200), ini, 0.05 * 1.0)
    P.poner(b.sabanas(1.5, rng), ini + 0.2, 0.2)
    ini, dur = T["5F"]
    P.poner(b.tono_cuarto(dur, rng, 200), ini, 0.09)
    P.poner(b.viento(dur, rng), ini, 0.10, pan=0.5)
    P.poner(b.reloj(dur, rng), ini, 0.08, pan=0.7)
    P.poner(pad(dur, [hz(38), hz(45)], rng, abre=(120, 300), ataque=3.0, caida=3.0), ini, 0.09)

    # ---- ESCENA 6: la mañana --------------------------------------------------------------------------
    ini, dur = T["6A"]
    P.poner(b.pajaros(dur, rng, 1.2), ini, 0.22, pan=-0.3)
    P.poner(b.tono_cuarto(dur, rng, 300), ini, 0.06)
    P.poner(b.viento(dur, rng), ini, 0.05)
    for k in range(5):
        P.poner(b.tintineo(rng, rng.uniform(1600, 2400)), ini + 1.2 + k * 1.3 + rng.uniform(0, 0.4), 0.06, pan=0.3)
    P.poner(pad(dur, [hz(50), hz(55), hz(62)], rng, abre=(500, 1500), ataque=3.0, caida=2.5), ini, 0.10)
    ini, dur = T["6B"]
    P.poner(b.tono_cuarto(dur, rng, 300), ini, 0.06)
    P.poner(b.acufeno(dur, 7400) * np.linspace(0.2, 1.0, muestras(dur), dtype=np.float32), ini, 0.05)
    P.poner(pad(dur, [hz(38), hz(45), hz(51)], rng, abre=(200, 1500), ataque=1.0, caida=0.4), ini, 0.16)
    P.poner(b.latidos(dur, 70, rng, 1.0), ini + 1.4, 0.3)
    ini, dur = T["6C"]
    P.poner(b.latidos(dur - 0.3, lambda t: 70 + 12 * t, rng, 1.0), ini, 0.4)
    P.poner(b.reverb(coro(dur - 0.6, [hz(38), hz(45), hz(50), hz(51)], rng, ataque=1.0, caida=0.3), 3.0, 0.4, rng),
            ini + 0.8, 0.34)
    P.poner(violin_chillido(1.5, 1400, 3200, rng, 0.8), ini + 1.6, 0.4)
    P.poner(taiko(rng, 1.0), ini + 1.6, 0.6)
    P.poner(pad(dur - 0.2, [hz(29), hz(36), hz(41), hz(43)], rng, abre=(300, 2200), ataque=1.2, caida=0.1), ini, 0.16)
    ini, dur = T["Título"]
    P.poner(campana_grave(rng, 98.0, dur + 2), ini + 0.3, 0.55)
    P.poner(b.reverb(coro(dur, [hz(38), hz(45), hz(50)], rng, ataque=1.0, caida=2.2), 3.5, 0.45, rng), ini + 0.2, 0.28)

    # ---- masterización ---------------------------------------------------------------------------------
    x = P.x[: muestras(total)]
    x = pb(x, 15000)
    x = pa(x, 28)
    x = np.tanh(x * 1.15) / math.tanh(1.15)
    x *= 0.95 / (np.abs(x).max() + 1e-9)
    fade = np.ones(len(x), np.float32)
    fade[-muestras(0.2):] = np.linspace(1, 0, muestras(0.2), dtype=np.float32)
    x = x * fade[:, None]
    pcm = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(str(ruta), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    return ruta
