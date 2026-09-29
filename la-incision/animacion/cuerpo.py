"""Piezas de cerca: el celular con el chat, las manos, el antebrazo con la incisión, la extremidad
oscura, Alex acostado e incorporándose, el plato de chilaquiles y la familia del recuerdo.
"""

import math

import cairo
import numpy as np

from dibujo import catmull, elipse, hexa, mezcla, oscuro
from familia import FAMILIA, bebe, brazo, familiar, nino
from personajes import PIEL_ALEX, SUDADERA, alex_frente, alex_perfil


def rect_redondo(x0, y0, x1, y1, r, n=5):
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -math.pi / 2), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, math.pi / 2),
                       (x0 + r, y0 + r, math.pi)):
        for k in range(n + 1):
            a = a0 + k / n * math.pi / 2
            pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    return np.array(pts, float)


def capsula(a, b, w0, w1, n=4):
    """Contorno de un hueso o dedo: de `a` (ancho w0) a `b` (ancho w1) con puntas redondeadas."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    d = b - a
    u = d / (np.linalg.norm(d) + 1e-9)
    nrm = np.array([-u[1], u[0]])
    pts = []
    for k in range(n + 1):
        ang = -math.pi / 2 + k / n * math.pi
        pts.append(b + (u * math.cos(ang) + nrm * math.sin(ang)) * w1 / 2)
    for k in range(n + 1):
        ang = math.pi / 2 + k / n * math.pi
        pts.append(a + (u * math.cos(ang) + nrm * math.sin(ang)) * w0 / 2)
    return np.array(pts, float)


def dedo(pts, w0, w1, pasos=6):
    """Contorno de un dedo (o cualquier miembro curvo) que sigue `pts` y se adelgaza de w0 a w1."""
    curva = catmull(np.asarray(pts, float), cerrada=False, pasos=pasos)
    d = np.gradient(curva, axis=0)
    d /= np.linalg.norm(d, axis=1, keepdims=True) + 1e-9
    n = np.stack([-d[:, 1], d[:, 0]], axis=1)
    w = np.linspace(w0, w1, len(curva))[:, None] / 2
    izq, der = curva + n * w, curva - n * w
    punta = [curva[-1] + (d[-1] * math.cos(a) + n[-1] * math.sin(a)) * w1 / 2 for a in np.linspace(math.pi / 2, -math.pi / 2, 7)[1:-1]]
    base = [curva[0] + (-d[0] * math.cos(a) - n[0] * math.sin(a)) * w0 / 2 for a in np.linspace(math.pi / 2, -math.pi / 2, 7)[1:-1]]
    return np.array(list(izq) + punta + list(der[::-1]) + base, float)


# --- el celular -------------------------------------------------------------------------------

MENSAJES = [
    ("ella", "Todo está bien", "21:02"),
    ("el", "¿Segura?", "21:03"),
    ("ella", "Sí. Bueno, no.", "21:15"),
    ("ella", "¿Por qué no contestaste en toda la tarde?", "21:16"),
    ("el", "Estaba en la chamba, ya te dije", "21:31"),
    ("ella", "Siempre es lo mismo contigo, Alex", "21:32"),
    ("el", "No empieces, estoy cenando", "21:40"),
    ("ella", "Ok. Cena. Ya no te voy a molestar.", "21:41"),
]
ULTIMO = ("ella", "Olvídalo.", "21:47")

_PANT = (-212, -446, 212, 446)   # pantalla en coordenadas del celular
_CHAT = (-350, 364)              # zona del chat (entre la barra de arriba y la de abajo)


def _renglones(ctx, texto, ancho):
    palabras, lineas, actual = texto.split(), [], ""
    for p in palabras:
        prueba = (actual + " " + p).strip()
        if ctx.text_extents(prueba).x_advance > ancho and actual:
            lineas.append(actual)
            actual = p
        else:
            actual = prueba
    lineas.append(actual)
    return lineas


def _burbujas(ctx, mensajes):
    """Acomoda las burbujas: devuelve [(lado, lineas, hora, y, alto, ancho)] y la altura total."""
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(25)
    y, salida, anterior = 0.0, [], None
    for lado, texto, hora in mensajes:
        lineas = _renglones(ctx, texto, 270)
        ancho = max(ctx.text_extents(l).x_advance for l in lineas) + 40
        ancho = max(ancho, 150)
        alto = 26 + len(lineas) * 32 + 20
        y += 10 if lado == anterior else 22
        salida.append((lado, lineas, hora, y, alto, ancho))
        y += alto
        anterior = lado
    return salida, y


def _camino_redondo(ctx, x0, y0, x1, y1, r):
    ctx.new_sub_path()
    ctx.arc(x1 - r, y0 + r, r, -math.pi / 2, 0)
    ctx.arc(x1 - r, y1 - r, r, 0, math.pi / 2)
    ctx.arc(x0 + r, y1 - r, r, math.pi / 2, math.pi)
    ctx.arc(x0 + r, y0 + r, r, math.pi, 3 * math.pi / 2)
    ctx.close_path()


def celular(lz, x, y, s, rot=0.0, desliza=0.0, nuevo=0.0, brillo=1.0, encendido=True):
    """Celular con el chat con Mariana (WhatsApp en modo oscuro).

    desliza 0..1 recorre la conversación hacia abajo; nuevo 0..1 hace aparecer «Olvídalo.».
    """
    c = lz.ctx
    lz.guardar()
    lz.mover(x, y, s, rot=rot)
    if encendido:
        lz.resplandor(0, 0, 760, hexa("#4f8fc8"), 0.22 * brillo)
    lz.forma(rect_redondo(-236, -472, 236, 472, 62), hexa("#16181c"), sombra=hexa("#0b0c0e"), luz=(-10, -10),
             grosor=5, suave=False)
    x0, y0, x1, y1 = _PANT
    c.save()
    c.new_path()
    _camino_redondo(c, x0, y0, x1, y1, 44)
    c.clip()
    if not encendido:
        c.set_source_rgb(*hexa("#050607"))
        c.paint()
        c.new_path()
        c.move_to(x0, y0 + 200)
        c.line_to(x0 + 160, y0)
        c.line_to(x0 + 260, y0)
        c.line_to(x0, y0 + 330)
        c.close_path()
        c.set_source_rgba(1, 1, 1, 0.05)
        c.fill()
        c.restore()
        lz.restaurar()
        return
    c.set_source_rgb(*hexa("#0b141a"))
    c.paint()
    # Fondo de garabatos del chat.
    rng = np.random.default_rng(2)
    c.set_source_rgba(1, 1, 1, 0.035)
    c.set_line_width(2)
    for _ in range(60):
        gx, gy = rng.uniform(x0, x1), rng.uniform(y0, y1)
        c.new_path()
        c.arc(gx, gy, rng.uniform(6, 14), 0, 2 * math.pi)
        c.stroke()

    burbujas, alto_total = _burbujas(c, MENSAJES)
    ultimo, alto_ultimo = _burbujas(c, [MENSAJES[-1], ULTIMO])
    visible = _CHAT[1] - _CHAT[0] - 20
    maximo = max(0.0, alto_total - visible)
    extra = (ultimo[1][3] + ultimo[1][4] - (ultimo[0][3] + ultimo[0][4])) * min(nuevo * 1.6, 1)
    desplaza = maximo * desliza + extra
    c.save()
    c.rectangle(x0, _CHAT[0], x1 - x0, _CHAT[1] - _CHAT[0])
    c.clip()
    todas = list(burbujas)
    if nuevo > 0:
        lado, lineas, hora, _, alto, ancho = ultimo[1]
        yy = burbujas[-1][3] + burbujas[-1][4] + (ultimo[1][3] - ultimo[0][3] - ultimo[0][4])
        todas.append((lado, lineas, hora, yy, alto, ancho, min(nuevo * 1.8, 1)))
    for b in todas:
        lado, lineas, hora, by, alto, ancho = b[:6]
        escala = b[6] if len(b) > 6 else 1.0
        top = _CHAT[0] + 10 + by - desplaza
        if top > _CHAT[1] or top + alto < _CHAT[0]:
            continue
        if lado == "el":
            bx1 = x1 - 18
            bx0 = bx1 - ancho
            color = hexa("#005c4b")
        else:
            bx0 = x0 + 18
            bx1 = bx0 + ancho
            color = hexa("#202c33")
        c.save()
        if escala < 1:
            cx = bx0 if lado == "ella" else bx1
            c.translate(cx, top + alto)
            c.scale(escala, escala)
            c.translate(-cx, -(top + alto))
        c.new_path()
        _camino_redondo(c, bx0, top, bx1, top + alto, 16)
        c.set_source_rgb(*color)
        c.fill()
        c.set_source_rgb(*hexa("#e9edef"))
        c.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        c.set_font_size(25)
        for i, linea in enumerate(lineas):
            c.move_to(bx0 + 18, top + 38 + i * 32)
            c.show_text(linea)
        c.set_font_size(17)
        c.set_source_rgb(*hexa("#8fa3ad"))
        ext = c.text_extents(hora)
        hx = bx1 - ext.x_advance - (48 if lado == "el" else 16)
        c.move_to(hx, top + alto - 12)
        c.show_text(hora)
        if lado == "el":
            c.set_source_rgb(*hexa("#53bdeb"))
            c.set_line_width(2.6)
            for dx in (0, 9):
                c.new_path()
                c.move_to(bx1 - 40 + dx, top + alto - 20)
                c.line_to(bx1 - 34 + dx, top + alto - 14)
                c.line_to(bx1 - 22 + dx, top + alto - 27)
                c.stroke()
        c.restore()
    c.restore()

    # Barra de arriba: Mariana, en línea.
    c.set_source_rgb(*hexa("#1f2c34"))
    c.rectangle(x0, y0, x1 - x0, _CHAT[0] - y0)
    c.fill()
    c.set_source_rgb(*hexa("#d6dde0"))
    c.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    c.set_font_size(16)
    c.move_to(x0 + 34, y0 + 30)
    c.show_text("21:47")
    c.rectangle(x1 - 70, y0 + 16, 34, 16)
    c.set_line_width(2)
    c.stroke()
    c.rectangle(x1 - 67, y0 + 19, 14, 10)
    c.fill()
    c.set_line_width(4)
    c.new_path()
    c.move_to(x0 + 40, y0 + 72)
    c.line_to(x0 + 26, y0 + 60)
    c.line_to(x0 + 40, y0 + 48)
    c.stroke()
    c.new_path()
    c.arc(x0 + 86, y0 + 60, 26, 0, 2 * math.pi)
    c.set_source_rgb(*hexa("#6b7c85"))
    c.fill()
    c.set_source_rgb(*hexa("#e9edef"))
    c.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    c.set_font_size(26)
    c.move_to(x0 + 77, y0 + 70)
    c.show_text("M")
    c.move_to(x0 + 126, y0 + 56)
    c.show_text("Mariana")
    c.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    c.set_font_size(18)
    c.set_source_rgb(*hexa("#8fa3ad"))
    c.move_to(x0 + 126, y0 + 82)
    c.show_text("en línea")
    # Barra de abajo.
    c.set_source_rgb(*hexa("#0b141a"))
    c.rectangle(x0, _CHAT[1], x1 - x0, y1 - _CHAT[1])
    c.fill()
    c.new_path()
    _camino_redondo(c, x0 + 14, _CHAT[1] + 14, x1 - 80, y1 - 14, 30)
    c.set_source_rgb(*hexa("#1f2c34"))
    c.fill()
    c.set_source_rgb(*hexa("#8fa3ad"))
    c.set_font_size(22)
    c.move_to(x0 + 40, _CHAT[1] + 50)
    c.show_text("Mensaje")
    c.new_path()
    c.arc(x1 - 42, (_CHAT[1] + y1) / 2, 30, 0, 2 * math.pi)
    c.set_source_rgb(*hexa("#00a884"))
    c.fill()
    # Reflejo del vidrio.
    c.new_path()
    c.move_to(x0, y0 + 260)
    c.line_to(x0 + 250, y0)
    c.line_to(x0 + 330, y0)
    c.line_to(x0, y0 + 380)
    c.close_path()
    c.set_source_rgba(1, 1, 1, 0.045)
    c.fill()
    c.restore()
    lz.restaurar()


def manos_celular(lz, x, y, s, rot=0.0, pulgar=0.0, piel=None, luz_pantalla=1.0):
    """Las dos manos de Alex sosteniendo el celular (primera persona). pulgar 0..1 desliza hacia arriba."""
    piel = piel or PIEL_ALEX
    ps = oscuro(piel, 0.6)
    filo = mezcla(piel, hexa("#9fd0f5"), 0.45 * luz_pantalla)
    lz.guardar()
    lz.mover(x, y, s, rot=rot)
    for lado in (-1, 1):
        manga = [(lado * 250, 520), (lado * 330, 470), (lado * 470, 620), (lado * 520, 1000), (lado * 240, 1000),
                 (lado * 220, 700)]
        lz.forma(np.array(manga, float), SUDADERA, sombra=oscuro(SUDADERA, 0.6), luz=(lado * 20, -10))
        palma = [(lado * 236, 180), (lado * 262, 150), (lado * 312, 190), (lado * 360, 330), (lado * 380, 520),
                 (lado * 300, 600), (lado * 236, 560), (lado * 210, 420)]
        lz.forma(np.array(palma, float), piel, sombra=ps, luz=(lado * 18, 0), brillo=filo, contraluz=(-lado * 8, -6))
        # Dedos que abrazan la orilla del celular.
        for k, yy in enumerate((200, 262, 322)):
            lz.forma(capsula((lado * 250, yy), (lado * 222, yy + 6), 44, 36), piel, sombra=ps, luz=(lado * 6, -4),
                     grosor=4)
        # Pulgar sobre la pantalla (el derecho desliza).
        if lado == 1:
            punta = np.array([96 - 6 * pulgar, 330 - 120 * pulgar])
        else:
            punta = np.array([-120, 350])
        base = np.array([lado * 236, 470])
        medio = (base + punta) / 2 + (lado * 18, 26)
        lz.forma(dedo([base, medio, punta], 92, 66), piel, sombra=ps, luz=(lado * 8, 8), brillo=filo,
                 contraluz=(0, -9), suave=False)
        d = punta - medio
        d = d / (np.linalg.norm(d) + 1e-9)
        uña = dedo([punta - d * 34, punta - d * 6], 40, 36)
        lz.forma(uña, mezcla(piel, (1, 0.86, 0.8), 0.35), grosor=2.5, suave=False)
    lz.restaurar()


# --- el antebrazo y la incisión ---------------------------------------------------------------

def _herida(lz, visible, t, semilla=3):
    """Incisión con suturas a lo largo del antebrazo (coordenadas del antebrazo)."""
    if visible <= 0:
        return
    u = np.linspace(0, 1, 24)
    linea = np.stack([110 + 330 * u, 4 + 6 * np.sin(u * math.pi * 1.3)], axis=1)
    alfa = min(visible, 1.0)
    moreton = np.concatenate([linea + (0, -46), linea[::-1] + (0, 46)])
    lz.mancha(moreton, hexa("#6a4a6a"), 0.28 * alfa)
    lz.mancha(np.concatenate([linea + (0, -30), linea[::-1] + (0, 30)]), hexa("#8a5a4a"), 0.3 * alfa)
    hinchado = np.concatenate([linea + (0, -13), linea[::-1] + (0, 13)])
    lz.forma(hinchado, hexa("#c24a55"), grosor=2.5, alfa=0.9 * alfa)
    lz.pincel(linea, 9, hexa("#4a080d"), punta=0.08, alfa=alfa)
    lz.pincel(linea + (0, -1), 3, hexa("#a3212c"), punta=0.1, alfa=alfa)
    brillo = 0.5 + 0.5 * math.sin(t * 2.2)
    lz.pincel(linea[4:18] + (0, -9), 2, hexa("#ffd8d0"), alfa=0.35 * alfa * brillo)
    rng = np.random.default_rng(semilla)
    for k in range(11):
        i = int(1 + k * 2.1)
        px, py = linea[min(i, len(linea) - 1)]
        inclina = rng.uniform(-6, 6)
        lz.pincel([(px - 7 + inclina, py - 30), (px + 7 - inclina, py + 30)], 4.5, hexa("#141014"), punta=0.05, alfa=alfa)
        lz.forma(elipse(px - 8 + inclina, py - 31, 5, 4, 8), hexa("#141014"), grosor=1.5, alfa=alfa)
        lz.pincel([(px - 8 + inclina, py - 32), (px - 20 + inclina, py - 44)], 2.2, hexa("#141014"), alfa=alfa)
        lz.pincel([(px - 8 + inclina, py - 32), (px + 2 + inclina, py - 48)], 2.2, hexa("#141014"), alfa=alfa)
        if k % 3 == 1:
            lz.forma(elipse(px + 10, py + 16, 4, 3, 8), hexa("#5a0d12"), tinta=False, alfa=0.8 * alfa)


def antebrazo(lz, x, y, s, ang=0.0, t=0.0, herida=0.0, vista=1.0, dedos=0.35, puno=0.0, piel=None,
              luz=(0, -10), contraluz=None, manga=SUDADERA, tiembla=0.0):
    """Antebrazo izquierdo de Alex con la palma hacia arriba. Origen: el codo; la muñeca queda en x=520.

    vista 0..1 aplasta el brazo (0: de canto, 1: se ve la cara interna). puno 0..1 cierra la mano.
    """
    piel = piel or mezcla(PIEL_ALEX, (1, 0.9, 0.8), 0.12)
    ps = mezcla(oscuro(piel, 0.64), hexa("#3a2c3c"), 0.2)
    brillo = contraluz[0] if contraluz else None
    filo = contraluz[1] if contraluz else (0, 0)
    lz.guardar()
    lz.mover(x, y, 1, rot=ang)
    lz.ctx.scale(s, s * max(vista, 0.15))
    if manga is not None:
        pliegues = [(-320, -110), (-120, -98), (20, -86), (60, -40), (48, 20), (70, 70), (10, 104), (-150, 112),
                    (-320, 120)]
        lz.forma(np.array(pliegues, float), manga, sombra=oscuro(manga, 0.58), luz=(10, -14), brillo=brillo,
                 contraluz=filo)
        for k in range(3):
            lz.pincel([(-40 - k * 60, -90), (-20 - k * 60, 0), (-50 - k * 60, 96)], 5, oscuro(manga, 0.45))
    brazo_pts = [(20, -70), (140, -74), (300, -60), (440, -48), (525, -44), (540, 0), (525, 46), (440, 52), (300, 60),
                 (140, 72), (20, 70)]
    lz.forma(np.array(brazo_pts, float), piel, sombra=ps, luz=luz, brillo=brillo, contraluz=filo)
    lz.pincel([(160, -30), (320, -18), (470, -8)], 3, ps, alfa=0.5)
    lz.pincel([(200, 30), (360, 26)], 3, ps, alfa=0.4)
    # Mano con la palma hacia arriba.
    temblor = math.sin(t * 31) * tiembla * 3
    cierra = min(max(puno, 0), 1)
    palma = [(516, -50), (600, -62), (664, -58), (694, -30), (704, 10), (694, 46), (640, 62), (560, 58), (516, 46)]
    lz.forma(np.array(palma, float), piel, sombra=ps, luz=luz, brillo=brillo, contraluz=filo)
    if cierra > 0.55:
        # Puño cerrado: los dedos doblados forman una sola masa con nudillos.
        puño = [(640, -64), (720, -66), (770, -40), (782, 0), (770, 44), (720, 66), (640, 62)]
        lz.forma(np.array(puño, float), piel, sombra=ps, luz=luz, brillo=brillo, contraluz=filo)
        for dy in (-34, -10, 14, 38):
            lz.pincel([(700, dy - 12), (740, dy - 4), (752, dy + 10)], 3.5, ps)
    else:
        for k, (dy, largo) in enumerate(((-36, 112), (-12, 130), (12, 124), (36, 100))):
            curva = min(dedos + cierra * 0.9, 1)
            base = np.array([690, dy * 1.05])
            direccion = np.array([math.cos(dy / 200), math.sin(dy / 200)])
            medio = base + direccion * largo * 0.5 * (1 - curva * 0.55) + (0, temblor)
            punta = medio + direccion * largo * 0.5 * (1 - curva * 0.9) + (-curva * 30, temblor)
            lz.forma(dedo([base, medio, punta], 34, 26), piel, sombra=ps, luz=luz, brillo=brillo, contraluz=filo,
                     grosor=4, suave=False)
    pulgar_base = np.array([570, -56])
    pulgar_punta = pulgar_base + (70 - cierra * 40, -60 + cierra * 40)
    lz.forma(dedo([pulgar_base, (pulgar_base + pulgar_punta) / 2 + (10, 4), pulgar_punta], 44, 32), piel, sombra=ps,
             luz=luz, brillo=brillo, contraluz=filo, grosor=4, suave=False)
    lz.pincel([(560, -20), (620, -10), (660, 20)], 3.5, ps)
    lz.pincel([(560, 30), (630, 26)], 3, ps)
    _herida(lz, herida, t)
    lz.restaurar()


# --- la extremidad oscura -------------------------------------------------------------------

def extremidad(lz, hombro, punta, t=0.0, curva=1.0, abre=0.5, grosor=1.0, contraluz=1.0):
    """Brazo larguísimo, flaco y con nudillos de una figura, del hombro a la punta del dedo."""
    cuerpo = hexa("#05060a")
    filo = mezcla(cuerpo, hexa("#6d8aa8"), 0.65 * contraluz)
    h = np.asarray(hombro, float)
    p = np.asarray(punta, float)
    d = p - h
    largo = np.linalg.norm(d) + 1e-9
    u = d / largo
    n = np.array([-u[1], u[0]])
    ondula = math.sin(t * 1.3) * 0.02
    j1 = h + d * 0.36 + n * largo * (0.07 + ondula) * curva
    j2 = h + d * 0.66 - n * largo * (0.05 - ondula) * curva
    mano = h + d * 0.82
    g = grosor * 1.7
    luz = dict(brillo=filo, contraluz=(n * 8).tolist(), sombra=None)
    lz.forma(dedo([h, j1, j2, mano], 64 * g, 34 * g, pasos=10), cuerpo, **luz, grosor=4, suave=False)
    for j, r in ((j1, 30), (j2, 24), (mano, 26)):
        lz.forma(elipse(j[0], j[1], r * g, r * g * 0.85, 12), cuerpo, **luz, grosor=4)
    lz.pincel([h + n * 26 * g, j1 + n * 20 * g, j2 + n * 14 * g, mano + n * 12 * g], 3, filo, alfa=0.7)
    resto = p - mano
    lr = np.linalg.norm(resto) + 1e-9
    ur = resto / lr
    for k, giro in enumerate((-0.5, -0.2, 0.0, 0.24)):
        a = giro * abre + math.sin(t * 2.1 + k) * 0.03
        rot = np.array([ur[0] * math.cos(a) - ur[1] * math.sin(a), ur[0] * math.sin(a) + ur[1] * math.cos(a)])
        perp = np.array([-rot[1], rot[0]])
        largo_dedo = lr * (1.0 if k == 2 else 0.82 - abs(giro) * 0.3)
        nudillo = mano + rot * largo_dedo * 0.45 + perp * 16 * g
        garra = mano + rot * largo_dedo * 0.8 + perp * 10 * g
        fin = mano + rot * largo_dedo
        lz.forma(dedo([mano, nudillo, garra, fin], 20 * g, 3, pasos=8), cuerpo, **luz, grosor=3.5, suave=False)
        lz.forma(elipse(nudillo[0], nudillo[1], 8 * g, 7 * g, 8), cuerpo, **luz, grosor=3)


# --- Alex en la cama ---------------------------------------------------------------------------

def alex_acostado(lz, x, y, s, t=0.0, luna=1.0, **cara):
    """La cara de Alex sobre la almohada, vista desde arriba, con la cobija hasta el cuello."""
    almohada = hexa("#39465a")
    lz.guardar()
    lz.mover(x, y, s)
    lz.forma(rect_redondo(-420, -380, 420, 300, 120), almohada, sombra=oscuro(almohada, 0.62), luz=(-20, -26),
             grosor=5, suave=True)
    for pl in ([(-380, -200), (-250, -150), (-200, -60)], [(360, -260), (260, -200)], [(300, 200), (200, 150)]):
        lz.pincel(pl, 6, oscuro(almohada, 0.5))
    piel = mezcla(PIEL_ALEX, hexa("#6d7f99"), 0.35 * luna)
    alex_frente(lz, 0, 0, 1, t=t, ropa=False, cuello=True, piel=piel,
                contraluz=(mezcla(piel, hexa("#b9d2ea"), 0.5), (8, -6)), **cara)
    cobija = hexa("#27324a")
    tela = [(-700, 260), (-400, 226), (-160, 244), (0, 232), (170, 246), (420, 222), (700, 250), (700, 1100),
            (-700, 1100)]
    lz.forma(np.array(tela, float), cobija, sombra=oscuro(cobija, 0.6), luz=(0, 30), brillo=hexa("#3f5070"),
             contraluz=(0, -10))
    for pl in ([(-380, 300), (-300, 480), (-320, 700)], [(200, 290), (260, 520)], [(-60, 300), (0, 420)]):
        lz.pincel(pl, 7, oscuro(cobija, 0.5))
    lz.restaurar()


def alex_incorporado(lz, x, y, s, t=0.0, jadeo=1.0, sudor=1.0, luna=1.0):
    """Alex sentado de golpe en la cama, de perfil hacia la ventana, jadeando. Origen: centro de la cabeza."""
    piel = mezcla(PIEL_ALEX, hexa("#6d7f99"), 0.35 * luna)
    filo = mezcla(piel, hexa("#c3d8ee"), 0.55)
    playera = hexa("#2b3140")
    respira = -abs(math.sin(t * 7.5)) * 12 * jadeo
    lz.guardar()
    lz.mover(x, y, s)
    brazo(lz, (150, 300 + respira), (60, 920), 330, 330, oscuro(playera, 0.8), oscuro(piel, 0.8), grosor=80,
          doblez=-1, corta=True)
    torso = [(-40, 150 + respira), (-140, 240 + respira), (-175, 420), (-160, 660), (-140, 1000), (230, 1000),
             (240, 660), (225, 380), (190, 240 + respira), (90, 160 + respira)]
    lz.forma(np.array(torso, float), playera, sombra=oscuro(playera, 0.55), luz=(16, 0), brillo=mezcla(playera, filo, 0.5),
             contraluz=(-10, 0))
    alex_perfil(lz, 0, respira, 1, t=t, parpado=0.0, mira_abajo=0.0, jadeo=jadeo, sudor=sudor, piel=piel,
                ropa=False, contraluz=(filo, (-9, -3)))
    lz.restaurar()


# --- el desayuno ----------------------------------------------------------------------------

def chilaquiles(lz, x, y, s):
    """Plato de talavera con chilaquiles verdes, crema, queso y cebolla morada."""
    lz.guardar()
    lz.mover(x, y, s)
    lz.forma(elipse(0, 14, 310, 116, 28), (0, 0, 0), tinta=False, alfa=0.25)
    lz.forma(elipse(0, 0, 300, 110, 28), hexa("#f1ece0"), grosor=5)
    lz.forma(elipse(0, 0, 284, 100, 28), hexa("#2f5d98"), tinta=False)
    lz.forma(elipse(0, 0, 262, 90, 28), hexa("#f1ece0"), tinta=False)
    for k in range(18):
        a = k / 18 * 2 * math.pi
        lz.forma(elipse(math.cos(a) * 273, math.sin(a) * 95, 7, 4, 8), hexa("#e7b93c"), tinta=False, hervor=0)
    rng = np.random.default_rng(6)
    for _ in range(26):
        r, a = math.sqrt(rng.random()), rng.uniform(0, 2 * math.pi)
        cx, cy = math.cos(a) * r * 190, math.sin(a) * r * 58 - 18
        giro = rng.uniform(0, 2 * math.pi)
        tam = rng.uniform(46, 70)
        tri = [(cx + math.cos(giro + k * 2.094) * tam, cy + math.sin(giro + k * 2.094) * tam * 0.45) for k in range(3)]
        salsa = hexa("#5b8f32") if rng.random() < 0.75 else hexa("#d8a44a")
        lz.forma(np.array(tri, float), salsa, sombra=oscuro(salsa, 0.7), luz=(-4, -6), grosor=3, tension=0.4)
    lz.pincel([(-170, -30), (-110, -60), (-40, -20), (30, -64), (100, -24), (170, -52)], 12, hexa("#f6f1e6"))
    for _ in range(36):
        r, a = math.sqrt(rng.random()), rng.uniform(0, 2 * math.pi)
        lz.forma(elipse(math.cos(a) * r * 170, math.sin(a) * r * 52 - 22, 6, 4, 6), hexa("#fbf8f0"), tinta=False, hervor=0)
    for k in range(5):
        a = rng.uniform(0, 2 * math.pi)
        lz.linea(elipse(math.cos(a) * 110, math.sin(a) * 34 - 20, 26, 10, 12), 4, hexa("#b6528a"), cerrada=True)
    for _ in range(14):
        r, a = math.sqrt(rng.random()), rng.uniform(0, 2 * math.pi)
        lz.forma(elipse(math.cos(a) * r * 160, math.sin(a) * r * 48 - 24, 5, 3, 6), hexa("#2f7a2a"), tinta=False, hervor=0)
    lz.restaurar()


def tenedor(lz, x, y, s, ang=0.0):
    lz.guardar()
    lz.mover(x, y, s, rot=ang)
    lz.forma(np.array([(0, -8), (190, -10), (200, 0), (190, 10), (0, 8)], float), hexa("#b9bcc2"), grosor=3)
    lz.forma(np.array([(-80, -18), (0, -12), (0, 12), (-80, 18)], float), hexa("#b9bcc2"), grosor=3, suave=False)
    for k in (-12, -4, 4, 12):
        lz.linea([(-80, k), (-150, k * 1.2)], 5, hexa("#9a9ea6"))
    lz.restaurar()


# --- la familia del recuerdo -------------------------------------------------------------------

def papa_recuerdo(lz, x, y, s, t=0.0):
    """Papá joven de pie cargando a Alex niño por encima de su cabeza (cámara lenta). Origen: su cara."""
    e = FAMILIA["papa"]
    lz.guardar()
    lz.mover(x, y, s)
    for lado in (-1, 1):
        pierna = [(lado * 20, 780), (lado * 210, 780), (lado * 200, 1250), (lado * 176, 1640), (lado * 60, 1640),
                  (lado * 40, 1250)]
        lz.forma(np.array(pierna, float), hexa("#3d5a8a"), sombra=hexa("#2a3d60"), luz=(-lado * 10, 0))
        lz.forma(elipse(lado * 130, 1660, 96, 38, 14), hexa("#5a3a22"), grosor=5)
    familiar(lz, 0, 0, 1, "papa", t=t, risa=0.85 + 0.15 * math.sin(t * 2), mira=(0, -0.9), inclina=-0.06)
    vuelo = math.sin(t * 1.4) * 30
    kx, ky, ks = 0, -700 + vuelo, 0.85
    nino(lz, kx, ky, ks, t=t, risa=1, brazos=1, inclina=math.sin(t * 1.1) * 0.08)
    for lado in (-1, 1):
        brazo(lz, (lado * 205, 300), (kx + lado * 105 * ks, ky + 290 * ks), 380, 380, e["ropa"], e["piel"], grosor=76,
              doblez=lado)
    lz.restaurar()


def mama_recuerdo(lz, x, y, s, t=0.0):
    """Mamá joven sentada en el mantel con la hermana de bebé en brazos. Origen: su cara."""
    e = FAMILIA["mama"]
    lz.guardar()
    lz.mover(x, y, s)
    falda = [(-230, 760), (230, 760), (300, 960), (200, 1080), (-300, 1100), (-560, 1060), (-600, 960), (-400, 880)]
    lz.forma(np.array(falda, float), hexa("#e2b64a"), sombra=hexa("#b8902e"), luz=(-10, -16))
    familiar(lz, 0, 0, 1, "mama", t=t, risa=0.9, mira=(0.2, 0.4), inclina=0.1 + math.sin(t * 1.3) * 0.04)
    bebe(lz, 30, 560, 1.0, t=t)
    for lado in (-1, 1):
        brazo(lz, (lado * 170, 300), (30 + lado * 110, 700), 240, 240, e["ropa"], e["piel"], grosor=64, doblez=-lado)
    lz.restaurar()
