"""Herramientas de dibujo de la versión animada: tinta que tiembla, colores planos y sombras duras.

Todo se dibuja en un lienzo virtual de 1080×1920 (9:16); la resolución real la fija el ancho
con el que se crea el Lienzo. Las figuras se describen con listas de puntos: `forma` las rellena
con color plano, les pone una sombra dura (el truco del cel: la misma forma desplazada hacia
la luz) y las contornea con tinta que «hierve» un poco en cada dibujo, como en la animación a mano.
"""

import math

import cairo
import numpy as np

W, H = 1080, 1920
TINTA = (0.05, 0.035, 0.06)


def hexa(c):
    """'#aabbcc' → (r, g, b) en 0..1."""
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) / 255 for i in (0, 2, 4))


def mezcla(a, b, t):
    return tuple(x + (y - x) * t for x, y in zip(a, b))


def oscuro(c, f):
    return tuple(x * f for x in c)


def suave(t):
    """Curva de aceleración y frenado para 0..1."""
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def tramo(t, a, b):
    """0 antes de a, 1 después de b, rampa suave en medio."""
    if b <= a:
        return 1.0 if t >= b else 0.0
    return suave((t - a) / (b - a))


def ruido1(t, semilla=0, vel=1.0):
    """Ruido suave de una dimensión en -1..1 (para temblores y vaivenes)."""
    x = t * vel + semilla * 17.31
    return (math.sin(x * 1.7) * 0.5 + math.sin(x * 3.1 + 1.3) * 0.3 + math.sin(x * 5.3 + 2.1) * 0.2)


def elipse(cx, cy, rx, ry, n=16, rot=0.0):
    a = np.linspace(0, 2 * math.pi, n, endpoint=False) + rot
    return np.stack([cx + rx * np.cos(a), cy + ry * np.sin(a)], axis=1)


def catmull(pts, cerrada=True, tension=1.0, pasos=8):
    """Muestrea la curva que pasa por los puntos (para trazos de pincel)."""
    pts = np.asarray(pts, float)
    n = len(pts)
    if n < 3:
        return pts
    salida = []
    rango = range(n) if cerrada else range(n - 1)
    for i in rango:
        p0 = pts[(i - 1) % n] if cerrada or i > 0 else pts[0]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if cerrada or i + 2 < n else pts[-1]
        c1 = p1 + (p2 - p0) / 6 * tension
        c2 = p2 - (p3 - p1) / 6 * tension
        for s in np.linspace(0, 1, pasos, endpoint=False):
            u = 1 - s
            salida.append(u ** 3 * p1 + 3 * u * u * s * c1 + 3 * u * s * s * c2 + s ** 3 * p2)
    if not cerrada:
        salida.append(pts[-1])
    return np.array(salida)


class Lienzo:
    """Envuelve un contexto de cairo con las reglas de dibujo del corto."""

    def __init__(self, ancho=1080, semilla=0, margen=0):
        self.esc = ancho / W
        self.margen = margen
        self.w = int(round((W + 2 * margen) * self.esc / 2)) * 2
        self.h = int(round((H + 2 * margen) * self.esc / 2)) * 2
        self.sup = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.w, self.h)
        self.ctx = cairo.Context(self.sup)
        self.ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        self.ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        self.semilla = semilla
        self.dibujo = 0
        self.k = 0
        self.hervor = 1.3      # temblor de la tinta, en px del lienzo virtual
        self.grosor_min = 2.2  # la tinta nunca es más delgada que esto (px virtuales)
        self.tinta = TINTA
        self.sin_tinta = False  # modo pintura: sin contornos negros
        self.base = cairo.Matrix(self.esc, 0, 0, self.esc, margen * self.esc, margen * self.esc)

    # --- cuadro y cámara -------------------------------------------------------------------

    def nuevo(self, dibujo, fondo=(0, 0, 0)):
        """Empieza un cuadro. `dibujo` cambia cada dos cuadros (animación a dos).
        Con fondo=None el cuadro empieza transparente (capas que se pintan después)."""
        self.dibujo = dibujo
        self.k = 0
        c = self.ctx
        c.set_matrix(cairo.Matrix())
        if fondo is None:
            c.set_operator(cairo.OPERATOR_CLEAR)
            c.paint()
        else:
            c.set_operator(cairo.OPERATOR_SOURCE)
            c.set_source_rgb(*fondo)
            c.paint()
        c.set_operator(cairo.OPERATOR_OVER)
        c.set_matrix(self.base)

    def camara(self, zoom=1.0, cx=W / 2, cy=H / 2, rot=0.0, par=1.0):
        """Fija la cámara: el punto (cx, cy) del lienzo queda al centro con ese zoom.
        `par` < 1 mueve la capa menos que la cámara (efecto multiplano)."""
        z = 1 + (zoom - 1) * par
        cx = W / 2 + (cx - W / 2) * par
        cy = H / 2 + (cy - H / 2) * par
        c = self.ctx
        c.set_matrix(self.base)
        c.translate(W / 2, H / 2)
        c.rotate(rot * par)
        c.scale(z, z)
        c.translate(-cx, -cy)
        self.cam = (zoom, cx, cy, rot)

    def pantalla(self):
        """Coordenadas del cuadro sin cámara (para párpados, viñetas y rótulos)."""
        self.ctx.set_matrix(self.base)

    def desenfocar(self, fuerza=1.0, factor=7):
        """Desenfoca lo que ya está dibujado (lo que queda fuera de foco). fuerza 0..1."""
        if fuerza <= 0.01:
            return
        w, h = max(2, self.w // factor), max(2, self.h // factor)
        peq = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        c = cairo.Context(peq)
        c.scale(w / self.w, h / self.h)
        c.set_source_surface(self.sup, 0, 0)
        c.get_source().set_filter(cairo.FILTER_GOOD)
        c.paint()
        ctx = self.ctx
        ctx.save()
        ctx.set_matrix(cairo.Matrix())
        ctx.scale(self.w / w, self.h / h)
        ctx.set_source_surface(peq, 0, 0)
        patron = ctx.get_source()
        patron.set_filter(cairo.FILTER_BILINEAR)
        patron.set_extend(cairo.EXTEND_PAD)
        ctx.paint_with_alpha(min(fuerza, 1.0))
        ctx.restore()

    def viñeta(self, alfa=0.6, cx=W / 2, cy=H / 2, r0=500, r1=1300, color=(0, 0, 0)):
        """Oscurece las orillas del cuadro con un degradado radial."""
        c = self.ctx
        c.save()
        c.set_matrix(self.base)
        g = cairo.RadialGradient(cx, cy, r0, cx, cy, r1)
        g.add_color_stop_rgba(0, *color, 0)
        g.add_color_stop_rgba(1, *color, alfa)
        c.set_source(g)
        c.paint()
        c.restore()

    def grupo(self):
        """Empieza un grupo para pintarlo después con transparencia (ver `soltar`)."""
        self.ctx.push_group()

    def soltar(self, alfa=1.0):
        self.ctx.pop_group_to_source()
        self.ctx.paint_with_alpha(alfa)

    def guardar(self):
        self.ctx.save()

    def restaurar(self):
        self.ctx.restore()

    def mover(self, x=0, y=0, s=1.0, rot=0.0, sx=None):
        c = self.ctx
        c.translate(x, y)
        if rot:
            c.rotate(rot)
        c.scale(s if sx is None else sx, s)

    def _escala(self):
        m = self.ctx.get_matrix()
        return math.sqrt(abs(m.xx * m.yy - m.xy * m.yx)) / self.esc

    def _rng(self):
        self.k += 1
        return np.random.default_rng((self.semilla, self.dibujo, self.k))

    def _hervir(self, pts, hervor=None):
        """Temblor de la tinta: un pequeño giro/desplazamiento de toda la figura más ruido suave por punto."""
        pts = np.asarray(pts, float)
        amp = (self.hervor if hervor is None else hervor) / max(self._escala(), 1e-6)
        rng = self._rng()
        if amp <= 0 or len(pts) == 0:
            return pts
        centro = pts.mean(axis=0)
        rel = pts - centro
        radio = max(float(np.abs(rel).max()), 20.0)
        ang = rng.normal(0, amp * 0.7 / radio)
        esc = 1 + rng.normal(0, amp * 0.5 / radio, 2)
        ca, sa = math.cos(ang), math.sin(ang)
        rel = np.stack([rel[:, 0] * ca - rel[:, 1] * sa, rel[:, 0] * sa + rel[:, 1] * ca], axis=1) * esc
        ruido = rng.normal(0, amp * 0.75, pts.shape)
        n = len(pts)
        if n > 12:
            k = max(2, n // 10)
            ext = np.concatenate([ruido[-k:], ruido, ruido[:k]])
            nucleo = np.ones(2 * k + 1) / (2 * k + 1)
            ruido = np.stack([np.convolve(ext[:, i], nucleo, mode="valid") for i in range(2)], axis=1) * math.sqrt(k)
        return centro + rel + rng.normal(0, amp * 0.5, 2) + ruido

    def _camino(self, pts, cerrada=True, suave=True, tension=1.0):
        c = self.ctx
        c.new_path()
        n = len(pts)
        if not suave or n < 3:
            c.move_to(*pts[0])
            for p in pts[1:]:
                c.line_to(*p)
        else:
            c.move_to(*pts[0])
            rango = range(n) if cerrada else range(n - 1)
            for i in rango:
                p0 = pts[(i - 1) % n] if cerrada or i > 0 else pts[0]
                p1 = pts[i]
                p2 = pts[(i + 1) % n]
                p3 = pts[(i + 2) % n] if cerrada or i + 2 < n else pts[-1]
                c1 = p1 + (p2 - p0) / 6 * tension
                c2 = p2 - (p3 - p1) / 6 * tension
                c.curve_to(c1[0], c1[1], c2[0], c2[1], p2[0], p2[1])
        if cerrada:
            c.close_path()
        return c.copy_path()

    def _trazar(self, camino, grosor, color=None, alfa=1.0):
        c = self.ctx
        ancho = max(grosor * self._escala(), self.grosor_min) * self.esc
        c.save()
        c.new_path()
        c.append_path(camino)
        c.set_matrix(cairo.Matrix())
        c.set_line_width(ancho)
        c.set_source_rgba(*(color or self.tinta), alfa)
        c.stroke()
        c.restore()

    # --- figuras -------------------------------------------------------------------------

    def forma(self, pts, color, sombra=None, luz=(0, 0), brillo=None, contraluz=(0, 0),
              grosor=5.0, tinta=True, suave=True, tension=1.0, alfa=1.0, hervor=None,
              relleno=None):
        """Figura cerrada con color plano.

        sombra/luz: color de la sombra y hacia dónde se desplaza la parte iluminada
        (en unidades locales). brillo/contraluz: un filo de luz del lado contrario.
        relleno: función opcional que dibuja un estampado dentro de la figura (ya recortada).
        """
        p = self._hervir(pts, hervor)
        c = self.ctx
        if self.sin_tinta:
            tinta = False
        camino = self._camino(p, True, suave, tension)
        c.save()
        c.new_path()
        c.append_path(camino)
        c.clip()
        if alfa < 1:
            c.push_group()
        if brillo is not None:
            c.set_source_rgb(*brillo)
            c.paint()
            self._camino(p - np.array(contraluz), True, suave, tension)
            c.clip()
        if sombra is not None:
            c.set_source_rgb(*sombra)
            c.paint()
            c.new_path()
            self._camino(p + np.array(luz), True, suave, tension)
            c.set_source_rgb(*color)
            c.fill()
        else:
            c.set_source_rgb(*color)
            c.paint()
        if relleno:
            relleno()
        if alfa < 1:
            c.pop_group_to_source()
            c.paint_with_alpha(alfa)
        c.restore()
        if tinta:
            self._trazar(camino, grosor, alfa=alfa)
        return camino

    def linea(self, pts, grosor=5.0, color=None, cerrada=False, suave=True, alfa=1.0, hervor=None):
        """Línea de tinta de grosor constante."""
        p = self._hervir(pts, hervor)
        camino = self._camino(p, cerrada, suave)
        self._trazar(camino, grosor, color, alfa)

    def pincel(self, pts, ancho=6.0, color=None, punta=0.25, alfa=1.0, hervor=None, cerrada=False):
        """Trazo de pincel que se afila en las puntas (cejas, pliegues, arrugas)."""
        p = self._hervir(pts, hervor)
        curva = catmull(p, cerrada=cerrada, pasos=10)
        if len(curva) < 2:
            return
        d = np.gradient(curva, axis=0)
        largo = np.linalg.norm(d, axis=1, keepdims=True) + 1e-9
        normal = np.stack([-d[:, 1], d[:, 0]], axis=1) / largo
        seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(curva, axis=0), axis=1))]
        u = seg / max(seg[-1], 1e-9)
        if cerrada:
            perfil = np.ones_like(u)
        else:
            perfil = np.clip(np.minimum(u, 1 - u) / max(punta, 1e-3), 0.12, 1) ** 0.8
        minimo = self.grosor_min * 0.6 / max(self._escala(), 1e-6)
        w = np.maximum(ancho * perfil, minimo)[:, None] / 2
        izq = curva + normal * w
        der = curva - normal * w
        c = self.ctx
        c.new_path()
        c.move_to(*izq[0])
        for q in izq[1:]:
            c.line_to(*q)
        for q in der[::-1]:
            c.line_to(*q)
        c.close_path()
        c.set_source_rgba(*(color or self.tinta), alfa)
        c.fill()

    def mancha(self, pts, color, alfa=1.0, suave=True, hervor=None, operador=None):
        """Figura sin tinta (sombras proyectadas, reflejos, brillos)."""
        p = self._hervir(pts, hervor)
        c = self.ctx
        self._camino(p, True, suave)
        c.set_source_rgba(*color, alfa)
        if operador is not None:
            c.save()
            c.set_operator(operador)
            c.fill()
            c.restore()
        else:
            c.fill()

    def recorte(self, pts, suave=True):
        """Recorta lo que sigue a la figura (hasta `restaurar`)."""
        c = self.ctx
        c.save()
        self._camino(np.asarray(pts, float), True, suave)
        c.clip()

    # --- luz -----------------------------------------------------------------------------

    def resplandor(self, x, y, r, color, alfa=1.0, operador=cairo.OPERATOR_ADD, ry=None):
        c = self.ctx
        c.save()
        c.translate(x, y)
        if ry:
            c.scale(1, ry / r)
        g = cairo.RadialGradient(0, 0, 0, 0, 0, r)
        g.add_color_stop_rgba(0, *color, alfa)
        g.add_color_stop_rgba(0.35, *color, alfa * 0.45)
        g.add_color_stop_rgba(1, *color, 0)
        c.set_source(g)
        c.set_operator(operador)
        c.arc(0, 0, r, 0, 2 * math.pi)
        c.fill()
        c.restore()

    def degradado(self, x0, y0, x1, y1, paradas, rect=None):
        """Rellena (todo o un rectángulo) con un degradado lineal: paradas = [(pos, color, alfa)]."""
        c = self.ctx
        g = cairo.LinearGradient(x0, y0, x1, y1)
        for pos, col, a in paradas:
            g.add_color_stop_rgba(pos, *col, a)
        c.save()
        c.set_source(g)
        if rect:
            c.rectangle(*rect)
            c.fill()
        else:
            c.paint()
        c.restore()

    def velo(self, color, alfa):
        c = self.ctx
        c.save()
        c.set_matrix(cairo.Matrix())
        c.set_source_rgba(*color, alfa)
        c.paint()
        c.restore()

    # --- superficies -----------------------------------------------------------------------

    def pintar_superficie(self, sup, x=0, y=0, escala=1.0, alfa=1.0, filtro=cairo.FILTER_BILINEAR):
        """Pinta una superficie ya dibujada (fondos cacheados) en coordenadas virtuales."""
        c = self.ctx
        c.save()
        c.translate(x, y)
        c.scale(escala / self.esc, escala / self.esc)
        c.set_source_surface(sup, 0, 0)
        c.get_source().set_filter(filtro)
        c.paint_with_alpha(alfa)
        c.restore()

    def capturar(self):
        """Copia del cuadro actual como superficie de cairo."""
        copia = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.w, self.h)
        c = cairo.Context(copia)
        c.set_source_surface(self.sup, 0, 0)
        c.paint()
        return copia

    def rgb8(self):
        """El cuadro como arreglo uint8 RGB (alto, ancho, 3)."""
        self.sup.flush()
        datos = np.ndarray((self.h, self.w, 4), np.uint8, self.sup.get_data(), strides=(self.sup.get_stride(), 4, 1))
        return datos[..., 2::-1]

    def matriz(self):
        """El cuadro como arreglo float32 RGB (alto, ancho, 3) en 0..1."""
        self.sup.flush()
        datos = np.ndarray((self.h, self.w, 4), np.uint8, self.sup.get_data(), strides=(self.sup.get_stride(), 4, 1))
        return datos[..., 2::-1].astype(np.float32) / 255.0


def superficie_de(arr):
    """Arreglo RGB float (0..1) → superficie de cairo."""
    h, w = arr.shape[:2]
    sup = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    datos = np.ndarray((h, w, 4), np.uint8, sup.get_data(), strides=(sup.get_stride(), 4, 1))
    rgb = (np.clip(arr, 0, 1) * 255 + 0.5).astype(np.uint8)
    datos[..., 0] = rgb[..., 2]
    datos[..., 1] = rgb[..., 1]
    datos[..., 2] = rgb[..., 0]
    datos[..., 3] = 255
    sup.mark_dirty()
    return sup


def textura(h, w, semilla, escalas=((6, 0.5), (24, 0.3), (90, 0.2))):
    """Ruido de varias escalas en -1..1 para dar a los fondos un aire de pintura a mano."""
    from scipy.ndimage import zoom
    rng = np.random.default_rng(semilla)
    total = np.zeros((h, w), np.float32)
    for tam, peso in escalas:
        ch, cw = max(2, h // tam), max(2, w // tam)
        base = rng.standard_normal((ch, cw)).astype(np.float32)
        capa = zoom(base, (h / ch, w / cw), order=3)[:h, :w]
        if capa.shape != (h, w):
            capa = np.pad(capa, ((0, h - capa.shape[0]), (0, w - capa.shape[1])), mode="edge")
        total += capa * peso
    total /= np.abs(total).max() + 1e-6
    return total
