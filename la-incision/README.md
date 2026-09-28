# La Incisión

Corto de terror vertical (9:16) de 1:49 para TikTok, producido con Gemini Omni o Kling AI a partir de un guion de 6 escenas y 5 imágenes de referencia.

> Alex, de 22 años, cena con su familia pero tiene la cabeza en una pelea con su novia. Esa noche, paralizado en su cama, tres figuras con máscaras blancas lo rodean. A la mañana siguiente descubre en su brazo una incisión con suturas perfectas: no fue un sueño.

## Qué hay en esta carpeta

| Archivo | Para qué sirve |
|---|---|
| [guion.md](guion.md) | El guion original |
| [biblia-visual.md](biblia-visual.md) | Tono, formato, guion de color, personajes, locaciones y reglas para escribir prompts |
| [keyframes.md](keyframes.md) | Las 11 imágenes que faltan (K0–K10), con su prompt. Se generan primero |
| [shotlist-kling.md](shotlist-kling.md) | Ajustes de Kling, continuidad, línea de tiempo y los 20 planos con prompt, negative prompt, duración y fotogramas |
| [gemini-omni.md](gemini-omni.md) | Los mismos 20 planos adaptados a Gemini Omni (app de Gemini o Google Flow), con prompt maestro y arreglos rápidos |
| [postproduccion.md](postproduccion.md) | Transiciones, sonido, voces, música, color, título y exportación |
| [storyboard.html](storyboard.html) | Todo lo anterior en una página visual con botones para copiar. Ábrela en el navegador |
| [referencias/](referencias/) | Tus 5 imágenes de referencia, numeradas. En `vertical/` están recortadas a 9:16 para usarlas como primer cuadro, más dos cuadros de tu toma 1A |
| [elements/](elements/) | Recortes de referencia de Alex (sacado de tu toma 1A) y de la figura enmascarada |
| [plan.json](plan.json) | Los datos de planos y keyframes de los que salen el shotlist, los keyframes y el storyboard |
| [guia-para-claude-en-tu-pc.md](guia-para-claude-en-tu-pc.md) | Instrucciones para que Claude Desktop (con Computer use) produzca todo en Kling desde tu PC |
| [herramientas/armar_corte.py](herramientas/armar_corte.py) | Arma el corte bruto con las tomas de `tomas/` (necesita Python 3 y ffmpeg) |

## Flujo de trabajo

1. Sube las referencias a Kling y crea los Elements «Alex» y «Figura» con los recortes de `elements/`.
2. Genera los keyframes K0–K10 ([keyframes.md](keyframes.md)) y revisa la lista de continuidad del shotlist.
3. Genera los 20 planos escena por escena ([shotlist-kling.md](shotlist-kling.md)): borrador rápido y luego toma final.
4. Guarda la mejor toma de cada plano con su ID (`1A.mp4`, `1B.mp4`…).
5. Graba o genera las dos líneas de diálogo y junta los efectos de sonido.
6. Monta con [postproduccion.md](postproduccion.md).

## Referencias

| Ref. | Archivo | Se usa en |
|---|---|---|
| 01 | [01-habitacion-noche.jpg](referencias/01-habitacion-noche.jpg) | 2A, 2B, 5F y como base de K2, K4 y K6 |
| 02 | [02-recuerdo-parque.jpg](referencias/02-recuerdo-parque.jpg) | 4A |
| 03 | [03-pov-chat.jpg](referencias/03-pov-chat.jpg) | 1B y como base de K1 |
| 04 | [04-comedor-cena.jpg](referencias/04-comedor-cena.jpg) | 1A y como base de K0, K7 y K10 |
| 05 | [05-figuras-enmascaradas.jpg](referencias/05-figuras-enmascaradas.jpg) | 5B, el Element «Figura» y como base de K2, K4 y K5 |

## Cambiar un prompt

`shotlist-kling.md`, `keyframes.md` y `storyboard.html` se generan desde `plan.json`. Para cambiar un prompt, una duración o una nota, edita `plan.json` y vuelve a generar:

```sh
python3 la-incision/herramientas/generar.py
```
