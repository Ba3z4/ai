"""Primitivas de dibujo para un cel de anime de los 90: color plano, sombra de borde duro y línea entintada.

Se dibuja en coordenadas virtuales (por defecto 1080×1920, el cuadro vertical) y se rasteriza a la escala `k`.
Nada aquí usa degradados en personajes: solo formas planas, una media luna de sombra y tinta que se afila
en las puntas, como el acetato pintado detrás de su línea.
"""

import math

import cairo
import numpy as np

W, H = 1080, 1920


def hexa(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) / 255 for i in (0, 2, 4))


def mezcla(a, b, t):
    return tuple(x + (y - x) * t for x, y in zip(a, b))


def oscuro(c, f):
    return tuple(x * f for x in c)


def suave(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def tramo(t, a, b):
    return min(max((t - a) / (b - a), 0.0), 1.0) if b > a else float(t >= b)


def elipse(cx, cy, rx, ry, n=20, rot=0.0):
    c, s = math.cos(rot), math.sin(rot)
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        x, y = rx * math.cos(a), ry * math.sin(a)
        pts.append((cx + x * c - y * s, cy + x * s + y * c))
    return pts


def _bezier(pts, cerrada, tension):
    """Convierte puntos en curva Catmull-Rom (segmentos de Bézier cúbicos)."""
    n = len(pts)
    seg = []
    rango = range(n) if cerrada else range(n - 1)
    for i in rango:
        p0 = pts[(i - 1) % n] if (cerrada or i > 0) else pts[0]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (cerrada or i + 2 < n) else pts[-1]
        c1 = (p1[0] + (p2[0] - p0[0]) * tension / 6, p1[1] + (p2[1] - p0[1]) * tension / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) * tension / 6, p2[1] - (p3[1] - p1[1]) * tension / 6)
        seg.append((c1, c2, p2))
    return seg


def curva(pts, cerrada=False, tension=1.0, pasos=10):
    """Puntos densos a lo largo de la curva suave que pasa por `pts`."""
    if len(pts) < 3:
        return [tuple(p) for p in pts]
    out = [tuple(pts[0])]
    p1 = pts[0]
    for c1, c2, p2 in _bezier(pts, cerrada, tension):
        for k in range(1, pasos + 1):
            t = k / pasos
            u = 1 - t
            out.append((u ** 3 * p1[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t ** 3 * p2[0],
                        u ** 3 * p1[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t ** 3 * p2[1]))
        p1 = p2
    return out


class Hoja:
    """Un acetato: se dibuja encima de él y se lee como arreglo RGBA."""

    def __init__(self, vw=W, vh=H, k=2 / 3, transparente=True, fondo=(0, 0, 0)):
        self.vw, self.vh, self.k = vw, vh, k
        self.w, self.h = int(round(vw * k)), int(round(vh * k))
        self.sup = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.w, self.h)
        self.cr = cairo.Context(self.sup)
        self.cr.scale(k, k)
        self.cr.set_antialias(cairo.ANTIALIAS_BEST)
        self.cr.set_line_join(cairo.LINE_JOIN_ROUND)
        self.cr.set_line_cap(cairo.LINE_CAP_ROUND)
        if not transparente:
            self.cr.set_source_rgb(*fondo)
            self.cr.paint()

    # --- caminos ---
    def _camino(self, pts, cerrada=True, suave_=True, tension=1.0):
        cr = self.cr
        cr.new_path()
        cr.move_to(*pts[0])
        if suave_ and len(pts) >= 3:
            for c1, c2, p2 in _bezier(pts, cerrada, tension):
                cr.curve_to(*c1, *c2, *p2)
        else:
            for p in pts[1:]:
                cr.line_to(*p)
        if cerrada:
            cr.close_path()

    def _color(self, color, alfa=1.0):
        if len(color) == 4:
            self.cr.set_source_rgba(*color)
        else:
            self.cr.set_source_rgba(*color, alfa)

    # --- formas planas ---
    def forma(self, pts, color, alfa=1.0, suave_=True, tension=1.0):
        self._camino(pts, True, suave_, tension)
        self._color(color, alfa)
        self.cr.fill()

    def rect(self, x0, y0, x1, y1, color, alfa=1.0):
        self.cr.rectangle(x0, y0, x1 - x0, y1 - y0)
        self._color(color, alfa)
        self.cr.fill()

    def contorno(self, pts, grosor, color, cerrada=True, suave_=True, alfa=1.0):
        self._camino(pts, cerrada, suave_)
        self._color(color, alfa)
        self.cr.set_line_width(grosor)
        self.cr.stroke()

    def tinta(self, pts, grosor, color=(0.05, 0.03, 0.04), afila=(0.25, 0.25), alfa=1.0, cerrada=False):
        """Trazo entintado: se engrosa en el centro y se afila en las puntas."""
        dens = curva(pts, cerrada, pasos=8)
        n = len(dens)
        if n < 2:
            return
        izq, der = [], []
        for i, (x, y) in enumerate(dens):
            a = dens[max(i - 1, 0)]
            b = dens[min(i + 1, n - 1)]
            dx, dy = b[0] - a[0], b[1] - a[1]
            d = math.hypot(dx, dy) or 1.0
            nx, ny = -dy / d, dx / d
            t = i / (n - 1)
            perfil = min(1.0, (t / afila[0]) if afila[0] > 0 else 1.0, ((1 - t) / afila[1]) if afila[1] > 0 else 1.0)
            r = grosor * (0.18 + 0.82 * math.sqrt(max(perfil, 0.0))) / 2
            izq.append((x + nx * r, y + ny * r))
            der.append((x - nx * r, y - ny * r))
        self.cr.new_path()
        self.cr.move_to(*izq[0])
        for p in izq[1:]:
            self.cr.line_to(*p)
        for p in der[::-1]:
            self.cr.line_to(*p)
        self.cr.close_path()
        self._color(color, alfa)
        self.cr.fill()

    def _creciente(self, pts, dx, dy, suave_, tension):
        """Máscara de la parte de la forma que NO cubre su copia corrida (dx, dy): una media luna."""
        cr = self.cr
        cr.push_group()
        self._camino(pts, True, suave_, tension)
        cr.set_source_rgba(0, 0, 0, 1)
        cr.fill()
        cr.set_operator(cairo.OPERATOR_DEST_OUT)
        cr.save()
        cr.translate(dx, dy)
        self._camino(pts, True, suave_, tension)
        cr.fill()
        cr.restore()
        cr.set_operator(cairo.OPERATOR_OVER)
        return cr.pop_group()

    def cel(self, pts, base, sombra=None, luz=(-1.0, -1.0), prof=16.0, linea=None, grosor=4.0, suave_=True,
            tension=1.0, brillo=None, prof_brillo=None):
        """Forma pintada como un acetato: base plana, media luna de sombra y otra de brillo, ambas de borde duro.

        `luz` es la dirección de donde viene la luz. La sombra queda en el lado contrario y mide `prof`;
        el brillo (si se da) queda del lado de la fuente y mide `prof_brillo`.
        """
        cr = self.cr
        n = math.hypot(*luz) or 1.0
        ux, uy = luz[0] / n, luz[1] / n
        self.forma(pts, base, suave_=suave_, tension=tension)
        if sombra is not None:
            m = self._creciente(pts, ux * prof, uy * prof, suave_, tension)
            self._color(sombra)
            cr.mask(m)
        if brillo is not None:
            p = prof_brillo if prof_brillo is not None else prof * 0.4
            m = self._creciente(pts, -ux * p, -uy * p, suave_, tension)
            self._color(brillo)
            cr.mask(m)
        if linea is not None:
            self.contorno(pts, grosor, linea, True, suave_)

    def resplandor(self, x, y, r, color, alfa=1.0, ry=None):
        cr = self.cr
        cr.save()
        cr.translate(x, y)
        cr.scale(1.0, (ry or r) / r)
        g = cairo.RadialGradient(0, 0, 0, 0, 0, r)
        g.add_color_stop_rgba(0, *color, alfa)
        g.add_color_stop_rgba(0.35, *color, alfa * 0.45)
        g.add_color_stop_rgba(1, *color, 0)
        cr.set_source(g)
        cr.arc(0, 0, r, 0, 2 * math.pi)
        cr.fill()
        cr.restore()

    def degradado(self, x0, y0, x1, y1, paradas, rect=None):
        g = cairo.LinearGradient(x0, y0, x1, y1)
        for p, c in paradas:
            g.add_color_stop_rgba(p, *(c if len(c) == 4 else (*c, 1.0)))
        self.cr.set_source(g)
        if rect:
            self.cr.rectangle(rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1])
            self.cr.fill()
        else:
            self.cr.paint()

    def texto(self, x, y, s, tam, color=(1, 1, 1), familia="DejaVu Sans", negrita=False, alfa=1.0):
        cr = self.cr
        cr.select_font_face(familia, cairo.FONT_SLANT_NORMAL,
                            cairo.FONT_WEIGHT_BOLD if negrita else cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(tam)
        self._color(color, alfa)
        cr.move_to(x, y)
        cr.show_text(s)

    def capa(self):
        self.cr.push_group()

    def suelta(self, alfa=1.0):
        self.cr.pop_group_to_source()
        self.cr.paint_with_alpha(alfa)

    def guarda(self):
        self.cr.save()

    def restaura(self):
        self.cr.restore()

    def mueve(self, x=0.0, y=0.0, escala=1.0, rot=0.0):
        self.cr.translate(x, y)
        if rot:
            self.cr.rotate(rot)
        if escala != 1.0:
            self.cr.scale(escala, escala)

    # --- salida ---
    def rgba(self):
        """Arreglo (alto, ancho, 4) float32 con color recto (sin premultiplicar) y alfa."""
        self.sup.flush()
        buf = np.ndarray((self.h, self.w, 4), np.uint8, self.sup.get_data(), strides=(self.sup.get_stride(), 4, 1))
        a = buf[..., 3:4].astype(np.float32) / 255
        rgb = buf[..., 2::-1].astype(np.float32) / 255
        rgb = np.where(a > 0, rgb / np.maximum(a, 1e-4), 0)
        return np.concatenate([np.clip(rgb, 0, 1), a], axis=2)

    def rgb(self):
        return self.rgba()[..., :3]


def componer(base, capa_rgba):
    """Pone un acetato RGBA encima de una imagen RGB."""
    a = capa_rgba[..., 3:4]
    return base * (1 - a) + capa_rgba[..., :3] * a
