# Guía para Claude en tu PC

Instrucciones para una sesión de Claude que corre en la PC de la persona (Claude Desktop con Computer use) y tiene que producir el corto en Kling de principio a fin. Todo el plan está en esta carpeta; esta guía dice en qué orden ejecutarlo y qué pedir antes de gastar créditos.

## Antes de empezar (lo hace la persona)

- Claude Desktop abierto, con Computer use activado y acceso concedido a Kling (app o navegador) y al explorador de archivos.
- Sesión iniciada en Kling.
- Esta carpeta en la PC. Si no está, clona el repo (`git clone -b claude/la-incision-video-script-vazp6w https://github.com/Ba3z4/ai`) o descárgalo como ZIP desde GitHub.
- Un presupuesto de créditos. Pregúntalo si no lo dijo: una pasada completa son 11 imágenes y unos 160 s de video, y cada plano suele necesitar 2 o 3 intentos.

## Reglas

- Confirma con la persona el presupuesto y el modelo (Kling 3.0 u otro) antes de la primera generación. Lleva la cuenta de créditos en `tomas/registro.md` y detente al llegar al límite.
- Copia los prompts tal cual de `plan.json` (o de `shotlist-kling.md` y `keyframes.md`). Si cambias uno, anota el cambio y el motivo en `tomas/registro.md`.
- No generes texto en pantalla con Kling: el chat y el título se ponen en la edición.
- Borradores en modo rápido; la toma final en calidad Pro solo cuando el borrador funcione.
- Todo en vertical 9:16 (es para TikTok).

## 1. Elements

1. Genera **K0** (hoja de personaje) con `elements/alex-toma1A.jpg` como referencia (prompt en `keyframes.md`).
2. Crea el Element **«Alex»** con `elements/alex-toma1A.jpg` + K0.
3. Crea el Element **«Figura»** con `elements/figura-enmascarada.jpg`.

## 2. Keyframes

Genera K1–K9 en este orden: K2, K4, K3, K5, K6, K7, K8, K9 (K1 solo si se elige la ruta pro de 1B). K10 ya no hace falta: 1C empieza en el último cuadro de la toma 1A (`referencias/vertical/07-toma1A-final.jpg`). K7 va antes que K8 y K9 porque les sirve de referencia de luz.

- Guarda cada una como `keyframes/K2.png`, `keyframes/K4.png`…
- Revisa la lista de continuidad de `shotlist-kling.md`: K2 con el mismo encuadre que `referencias/01-habitacion-noche.jpg`, y brazo **izquierdo** en K5 y K9 (si sale el derecho, voltea la imagen).
- **Punto de control:** enséñale a la persona K0, K2, K4 y K9 antes de animar.

## 3. Planos

Sigue el orden de la línea de tiempo de `shotlist-kling.md` (1A → 6C). La toma 1A ya existe: es el video de Gemini que tiene la persona, recortado desde el segundo 1.4; guárdalo como `tomas/1A.mp4`. Los primeros cuadros van en su versión vertical (`referencias/vertical/`). Para cada plano:

1. Imagen a video con el fotograma inicial indicado (y el final en 2B). «Último cuadro de 4A» se exporta del clip 4A ya elegido.
2. Duración = «Genera». Añade los Elements indicados si la versión lo permite con fotograma inicial.
3. Pega prompt y negative prompt. Audio nativo solo en 1A–1C, si la persona lo quiere.
4. Guarda cada intento como `tomas/<ID>_v1.mp4`, `tomas/<ID>_v2.mp4`…
5. Elige la mejor toma y cópiala como `tomas/<ID>.mp4`. Si la parte buena no empieza en el segundo 0, anota el segundo de entrada en `tomas/entradas.json` (ejemplo: `{"3A": 1.5}`).

**Puntos de control:** al terminar la escena 1 y la escena 2, enséñale las tomas elegidas a la persona antes de seguir.

## 4. Corte

Con las tomas en `tomas/`, arma el corte bruto (sin sonido diseñado, con el audio que traigan los clips):

```sh
python3 herramientas/armar_corte.py
```

Genera `corte-bruto.mp4` con cada plano recortado a su duración, el negro y el título. Los planos que falten salen como una tarjeta gris con su ID, así que puedes armarlo desde el principio para revisar ritmo. Necesita Python 3 y ffmpeg (en Windows: `winget install Gyan.FFmpeg`, o `pip install imageio-ffmpeg`).

Después, el sonido, las voces, el color y los efectos se hacen en CapCut o DaVinci Resolve siguiendo `postproduccion.md`.
