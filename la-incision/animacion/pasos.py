"""«Cómo abrir a un humano»: La Incisión contada como los videos de «cómo encerrar a un ángel».

Una de las figuras enmascaradas, frente al cosmos, dicta ocho pasos palabra por palabra; entre
paso y paso se ven ilustraciones pintadas de lo que le hicieron a Alex. Aquí están el guion, el
narrador y las ilustraciones; render_pasos.py pone la voz, arma la línea de tiempo y renderiza.
"""

import math

import cairo
import numpy as np

import planos
from cuerpo import antebrazo, dedo, extremidad, rect_redondo
from dibujo import H, W, Lienzo, elipse, hexa, mezcla, suave, tramo
from escenarios import Fondo, cobija, cuarto_noche, lampara, mesa_comedor, pared_comedor, sabana, ventilador
from familia import familiar
from personajes import PIEL_ALEX, alex_perfil, figura, mascara_cerca

# (ilustración, [lo que dice el narrador, un pedazo a la vez; así aparece en la franja])
GUION = [
    ("narrador", ["CÓMO", "ABRIR", "A UN", "HUMANO"]),
    ("narrador", ["PASO", "UNO"]),
    ("cena", ["ELIGE", "A UNO", "QUE YA", "NO ESCUCHE"]),
    ("narrador", ["PASO", "DOS"]),
    ("noche", ["ESPERA", "A QUE", "SU CASA", "DUERMA"]),
    ("narrador", ["PASO", "TRES"]),
    ("rincon", ["ENTRA", "POR EL", "RINCÓN", "MÁS OSCURO"]),
    ("narrador", ["PASO", "CUATRO"]),
    ("mascaras", ["QUÍTALE", "LA VOZ"]),
    ("grito", ["QUE GRITE", "HACIA ADENTRO"]),
    ("narrador", ["PASO", "CINCO"]),
    ("recuerdo", ["DALE", "UN RECUERDO", "FELIZ"]),
    ("rompe", ["PARA QUE", "NO MIRE"]),
    ("narrador", ["PASO", "SEIS"]),
    ("abre", ["ÁBRELO"]),
    ("toma", ["TOMA", "LO QUE", "VINISTE", "A BUSCAR"]),
    ("narrador", ["PASO", "SIETE"]),
    ("cose", ["CÓSELO", "CON", "CUIDADO"]),
    ("narrador", ["PASO", "OCHO"]),
    ("mesa", ["DEVUÉLVELO", "A SU MESA"]),
    ("herida", ["DÉJALO", "CREER", "QUE FUE", "UN SUEÑO"]),
    ("final", ["VOLVEREMOS"]),
    ("glitch", ["POR LO QUE", "DEJAMOS"]),
]

CIAN = hexa("#6fc8ff")
MAGENTA = hexa("#ff3d9a")


def claroscuro(lz, cx, cy, r0, r1, alfa=0.85, color=(0, 0, 0)):
    """Todo se hunde en sombra salvo un charco de luz alrededor de (cx, cy)."""
    c = lz.ctx
    c.save()
    g = cairo.RadialGradient(cx, cy, r0, cx, cy, r1)
    g.add_color_stop_rgba(0, *color, 0)
    g.add_color_stop_rgba(1, *color, alfa)
    c.set_source(g)
    c.paint()
    c.restore()


class Lamina:
    """Una ilustración: se dibuja en coordenadas del lienzo y se anima con t (0..dur)."""
    paleta = "noche"

    def __init__(self, dur, ancho, variante=0):
        self.dur = dur
        self.ancho = ancho
        self.variante = variante
        self.preparar()

    def preparar(self):
        pass

    def dibujar(self, lz, t, tq, boca=0.0):
        return {}


# --- el narrador ------------------------------------------------------------------------------

_estrellas = np.random.default_rng(5).uniform(0, 1, (460, 4))


def cosmos(lz, t):
    """Fondo de espacio profundo: nebulosas, estrellas que titilan y una columna de luz detrás."""
    lz.degradado(0, -200, 0, H + 200, [(0, hexa("#04030c"), 1), (0.45, hexa("#130a2c"), 1), (1, hexa("#030207"), 1)],
                 rect=(-400, -400, W + 800, H + 800))
    for x, y, r, col, a in ((200, 520, 560, "#b3206f", 0.38), (880, 330, 620, "#2b46c8", 0.45),
                            (620, 980, 720, "#5a1a9a", 0.32), (120, 1250, 520, "#1a2a80", 0.3),
                            (960, 1400, 480, "#8a1450", 0.25)):
        lz.resplandor(x, y, r, hexa(col), a)
    c = lz.ctx
    for k, (u, v, tam, fase) in enumerate(_estrellas):
        x, y = -200 + u * (W + 400), -200 + v * (H + 400)
        r = 0.7 + tam ** 3 * 3.2
        brillo = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(t * (0.6 + fase * 2.4) + k))
        c.new_path()
        c.arc(x, y, r, 0, 2 * math.pi)
        c.set_source_rgba(0.9, 0.93, 1.0, brillo)
        c.fill()
        if tam > 0.93:
            lz.resplandor(x, y, 22 + r * 6, (0.8, 0.88, 1.0), 0.5 * brillo)
    pulso = 0.85 + 0.15 * math.sin(t * 1.3)
    lz.degradado(0, -200, 0, 560, [(0, (0.8, 0.9, 1.0), 0.9 * pulso), (1, (0.5, 0.7, 1.0), 0.0)], rect=(533, -200, 14, 760))
    lz.resplandor(540, 300, 280, (0.55, 0.72, 1.0), 0.6 * pulso, ry=520)
    lz.resplandor(540, 470, 140, (0.9, 0.95, 1.0), 0.7 * pulso)


def manos_juntas(lz, cx, cy, s, t):
    """Las manos de dedos larguísimos entrelazadas bajo la franja, con filo de luz azul y magenta."""
    negro = hexa("#1b1628")
    filo = hexa("#5f8ae8")
    lz.guardar()
    lz.mover(cx, cy, s)
    lz.forma(elipse(0, 90, 260, 150, 20), negro, brillo=mezcla(negro, MAGENTA, 0.5), contraluz=(-10, -6))
    for lado in (-1, 1):
        lz.forma(elipse(lado * 150, 40, 150, 120, 18, rot=lado * 0.3), negro, brillo=filo, contraluz=(lado * 9, -7))
    for k in range(4):
        mueve = math.sin(t * 1.1 + k) * 6
        for lado in (-1, 1):
            base = np.array([lado * 170, -40 + k * 34.0])
            nudillo = base + (-lado * 150, -60 + k * 10 + mueve)
            punta = nudillo + (-lado * 120, 40 + k * 14)
            lz.forma(dedo([base, nudillo, punta], 62, 18), negro, sombra=hexa("#0a0810"), luz=(0, -10),
                     brillo=filo if lado > 0 else mezcla(negro, MAGENTA, 0.6), contraluz=(0, -9), suave=False)
            lz.forma(elipse(nudillo[0], nudillo[1], 16, 14, 8), negro, brillo=filo, contraluz=(0, -6))
    lz.restaurar()


class Narrador(Lamina):
    """La figura que dicta los pasos. variante cambia el encuadre; «final» y «glitch» son el cierre."""
    paleta = "cosmos"

    def dibujar(self, lz, t, tq, boca=0.0):
        v = self.variante
        u = t / max(self.dur, 1e-6)
        if v == "final":
            zoom, cy, rot = 1.55 + 0.1 * u, 780, 0.0
        elif v == "glitch":
            zoom, cy, rot = 1.75, 760, math.sin(t * 13) * 0.02
        else:
            k = int(v)
            zoom = 1.0 + 0.04 * (k % 3) + 0.05 * u
            rot = (-0.018, 0.0, 0.018)[k % 3]
            cy = 960 - 20 * (k % 2)
        lz.camara(zoom, 540, cy, rot=rot)
        cosmos(lz, t)
        lz.resplandor(210, 760, 420, MAGENTA, 0.28)
        lz.resplandor(880, 700, 420, CIAN, 0.24)
        inclina = math.sin(t * 0.6 + (0 if v in ("final", "glitch") else int(v))) * 0.04
        mascara_cerca(lz, 540, 700, 2.7, t=tq, inclina=inclina, semilla=0, boca=boca, pupilas=1.0, grietas=True,
                      contraluz=1.0, mascara_brillo=0.8)
        # La luz cae desde arriba: la parte baja de la máscara y el cuerpo se hunden en sombra.
        claroscuro(lz, 540, 520, 90, 760, 0.62)
        lz.resplandor(395, 640, 150, MAGENTA, 0.35, ry=300)
        lz.resplandor(690, 640, 150, CIAN, 0.3, ry=300)
        manos_juntas(lz, 540, 1640, 1.25, t)
        return {}


# --- las ilustraciones ------------------------------------------------------------------------

class Cena(Lamina):
    """Paso uno: el que ya no escucha, con el celular bajo la mesa."""
    paleta = "cena"

    def preparar(self):
        self.pared = Fondo(pared_comedor, self.ancho, semilla=11, grano=0)
        self.mesa = Fondo(mesa_comedor, self.ancho, semilla=12, transparente=True, grano=0)

    def dibujar(self, lz, t, tq, boca=0.0):
        u = t / self.dur
        lz.camara(1.32 + 0.1 * u, 700, 1130)
        self.pared.pintar(lz)
        lampara(lz, vaiven=math.sin(t * 0.7) * 0.02)
        familiar(lz, 540, 790, 0.33, "papa", t=tq, risa=0.4, mira=(-0.3, 0.2))
        familiar(lz, 208, 895, 0.47, "mama", t=tq, habla=0.5 + 0.5 * math.sin(tq * 9), mira=(0.7, 0.1), luz=(12, -8))
        familiar(lz, 862, 870, 0.4, "hermana", t=tq, mira=(-0.7, 0.2), luz=(-12, -8))
        self.mesa.pintar(lz)
        lz.desenfocar(0.7)
        claroscuro(lz, 760, 1330, 160, 780, 0.8)
        planos._celular_mano(lz, 640, 1740, 0.9, t)
        alex_perfil(lz, 832, 1330, 0.95, t=tq, parpado=0.62, mira_abajo=1.0, luz=(-10, -6),
                    luz_cara=((0.25, 0.55, 0.95), 0.75), inclina=0.2)
        lz.resplandor(640, 1740, 520, CIAN, 0.45)
        return {}


def reloj_digital(lz, x, y, texto="03:17"):
    c = lz.ctx
    lz.forma(rect_redondo(x - 70, y - 34, x + 70, y + 34, 10), hexa("#0b0b0e"), suave=False)
    lz.resplandor(x, y, 120, hexa("#ff2a2a"), 0.45)
    c.save()
    c.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    c.set_font_size(46)
    ext = c.text_extents(texto)
    c.move_to(x - ext.x_advance / 2, y + ext.height / 2)
    c.set_source_rgb(1.0, 0.2, 0.18)
    c.show_text(texto)
    c.restore()


class Noche(Lamina):
    """Paso dos: la casa duerme. 03:17 en el reloj."""
    paleta = "noche"

    def preparar(self):
        self.fondo = Fondo(cuarto_noche, self.ancho, semilla=21, grano=0)

    def dibujar(self, lz, t, tq, boca=0.0):
        u = t / self.dur
        lz.camara(1.12 + 0.1 * u, 680, 860)
        self.fondo.pintar(lz)
        ventilador(lz, t * 0.4)
        reloj_digital(lz, 850, 872)
        cobija(lz, respira=math.sin(t * 1.1))
        claroscuro(lz, 640, 760, 120, 820, 0.8)
        lz.resplandor(640, 540, 300, hexa("#a9c8ff"), 0.35)
        return {}


class Rincon(Lamina):
    """Paso tres: salen del rincón más oscuro."""
    paleta = "noche"

    def preparar(self):
        self.fondo = Fondo(cuarto_noche, self.ancho, semilla=21, grano=0)

    def dibujar(self, lz, t, tq, boca=0.0):
        u = t / self.dur
        lz.camara(1.3 + 0.08 * u, 430, 930)
        self.fondo.pintar(lz)
        lz.resplandor(420, 950, 520, (0, 0, 0), 0.9, operador=cairo.OPERATOR_OVER, ry=620)
        aparece = tramo(u, 0.0, 0.45)
        for i, ((x, y, s), _) in enumerate(planos.FIGURAS):
            figura(lz, x, y, s, t=tq, semilla=i, alfa=max(aparece, 0.01), mascara_brillo=1.0,
                   inclina=0.16 * tramo(u, 0.5, 0.9) if i == 1 else 0.0)
        claroscuro(lz, 420, 620, 160, 700, 0.55)
        cobija(lz, respira=math.sin(t * 1.6) * 1.4)
        return {}


class Reusada(Lamina):
    """Ilustración que reutiliza un plano de la versión animada en un tramo de su tiempo."""

    def __init__(self, dur, ancho, variante=0, plano=None, dur_plano=6, t0=0.0, t1=1.0, paleta="noche"):
        self.plano = planos.PLANOS[plano](dur_plano, ancho)
        self.t0, self.t1 = t0, t1
        self.paleta = paleta
        super().__init__(dur, ancho, variante)

    def dibujar(self, lz, t, tq, boca=0.0):
        u = t / max(self.dur, 1e-6)
        tp = self.t0 + (self.t1 - self.t0) * u
        self.plano.dibujar(lz, tp, math.floor(tp * 12) / 12)
        return {}


class Rompe(Reusada):
    """Paso cinco (fin): el recuerdo se rompe. El cuadro congelado también va sin contornos."""

    def __init__(self, dur, ancho, variante=0):
        super().__init__(dur, ancho, variante, plano="5A", dur_plano=3, t0=0.35, t1=2.2, paleta="oro")
        recuerdo = planos.P4A(8, ancho)
        lz = Lienzo(ancho, semilla=0)
        lz.sin_tinta = True
        lz.hervor = 0
        lz.nuevo(96)
        recuerdo.dibujar(lz, 7.95, 7.95)
        self.plano.congelado = lz.capturar()


class Abre(Lamina):
    """Paso seis: la garra toca el antebrazo y el corte se abre."""
    paleta = "sangre"

    def preparar(self):
        self.fondo = Fondo(sabana, self.ancho, semilla=33, grano=0)

    def dibujar(self, lz, t, tq, boca=0.0):
        u = t / self.dur
        lz.camara(1.05 + 0.1 * u, 470, 1000)
        self.fondo.pintar(lz)
        piel = mezcla(PIEL_ALEX, hexa("#6d7f99"), 0.3)
        antebrazo(lz, -60, 1330, 1.3, ang=-0.36, t=tq, dedos=0.3, piel=piel, manga=None, corte=tramo(u, 0.45, 1.0),
                  contraluz=(mezcla(piel, hexa("#c3d8ee"), 0.5), (0, -9)))
        # La garra baja hasta el inicio del corte y luego lo recorre a lo largo del antebrazo.
        arriba, inicio, fin = np.array([1150.0, 150.0]), np.array([76.0, 1272.0]), np.array([477.0, 1121.0])
        if u <= 0.45:
            punta = arriba + (inicio - arriba) * suave(u / 0.45)
        else:
            punta = inicio + (fin - inicio) * tramo(u, 0.45, 1.0)
        extremidad(lz, (1500, -420), punta, t=tq, abre=0.5)
        claroscuro(lz, 450, 1150, 180, 900, 0.75)
        return {}


class Toma(Lamina):
    """Paso seis (fin): la garra se lleva algo que brilla."""
    paleta = "sangre"

    def preparar(self):
        self.fondo = Fondo(sabana, self.ancho, semilla=33, grano=0)

    def dibujar(self, lz, t, tq, boca=0.0):
        u = t / self.dur
        lz.camara(1.0 + 0.06 * u, 540, 960)
        self.fondo.pintar(lz)
        piel = mezcla(PIEL_ALEX, hexa("#6d7f99"), 0.3)
        antebrazo(lz, -60, 1500, 1.3, ang=-0.36, t=tq, dedos=0.3, piel=piel, manga=None, corte=1.0,
                  contraluz=(mezcla(piel, hexa("#c3d8ee"), 0.5), (0, -9)))
        sube = suave(tramo(u, 0.1, 1.0))
        punta = np.array([560, 1180]) + (np.array([720, 520]) - np.array([560, 1180])) * sube
        extremidad(lz, (1500, -420), punta, t=tq, abre=0.15)
        brillo = 0.8 + 0.2 * math.sin(t * 5)
        lz.resplandor(punta[0], punta[1] + 20, 260, hexa("#bfe8ff"), 0.9 * brillo)
        lz.forma(elipse(punta[0], punta[1] + 20, 22, 22, 16), hexa("#f4fbff"), tinta=False)
        claroscuro(lz, punta[0], punta[1], 200, 1000, 0.8)
        return {}


class Cose(Lamina):
    """Paso siete: las puntadas aparecen una a una; la garra tira del hilo."""
    paleta = "sangre"

    def preparar(self):
        self.fondo = Fondo(sabana, self.ancho, semilla=34, grano=0)

    def dibujar(self, lz, t, tq, boca=0.0):
        u = t / self.dur
        lz.camara(1.0 + 0.05 * u, 540, 960)
        self.fondo.pintar(lz)
        a, s = -0.3, 2.2
        ox, oy = 560 - s * 275 * math.cos(a), 900 - s * 275 * math.sin(a)
        piel = mezcla(PIEL_ALEX, hexa("#6d7f99"), 0.3)
        puntadas = 1 + int(10 * u)
        antebrazo(lz, ox, oy, s, ang=a, t=tq, herida=1.0, puntadas=puntadas, piel=piel, manga=None,
                  contraluz=(mezcla(piel, hexa("#c3d8ee"), 0.5), (0, -9)))
        # Dónde quedó la última puntada, para tirar del hilo desde ahí.
        i = int(1 + (puntadas - 1) * 2.1)
        lx = 110 + 330 * min(i, 23) / 23
        px = ox + s * (lx * math.cos(a) - (-30) * math.sin(a))
        py = oy + s * (lx * math.sin(a) + (-30) * math.cos(a))
        tira = math.sin(t * 3) * 30
        garra = np.array([px + 160, py - 420 + tira])
        lz.linea([(px, py), ((px + garra[0]) / 2 + 30, (py + garra[1]) / 2), tuple(garra)], 3, hexa("#0d0b10"))
        lz.linea([tuple(garra), tuple(garra + (30, -70))], 3.5, hexa("#c9ccd2"))
        extremidad(lz, (1500, -500), garra + (20, -40), t=tq, abre=0.1, grosor=0.9)
        claroscuro(lz, 560, 900, 200, 900, 0.7)
        return {}


LAMINAS = {
    "narrador": Narrador, "final": Narrador, "glitch": Narrador, "cena": Cena, "noche": Noche, "rincon": Rincon,
    "abre": Abre, "toma": Toma, "cose": Cose, "rompe": Rompe,
}
REUSADAS = {
    "mascaras": dict(plano="3A", dur_plano=6, t0=1.6, t1=5.2, paleta="noche"),
    "grito": dict(plano="3B", dur_plano=4, t0=0.3, t1=3.6, paleta="noche"),
    "recuerdo": dict(plano="4A", dur_plano=8, t0=1.6, t1=7.2, paleta="oro"),
    "mesa": dict(plano="6A", dur_plano=8, t0=0.8, t1=5.6, paleta="manana"),
    "herida": dict(plano="6C", dur_plano=5, t0=0.3, t1=4.7, paleta="manana"),
}


def lamina(ilustracion, dur, ancho, variante=0):
    if ilustracion in REUSADAS:
        return Reusada(dur, ancho, variante, **REUSADAS[ilustracion])
    if ilustracion in ("final", "glitch"):
        variante = ilustracion
    return LAMINAS[ilustracion](dur, ancho, variante)
