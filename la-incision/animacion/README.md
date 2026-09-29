# La Incisión, versión animada

El corto completo como caricatura tétrica de los 90: vertical 9:16 para TikTok, 1080×1920, 24 fps y con sonido. Todo se dibuja y se sintetiza con código, sin generadores de video ni grabaciones, así que se puede volver a renderizar igual cuantas veces haga falta.

## El estilo

- **Dibujo de los 90.** Tinta negra que tiembla un poco en cada dibujo, colores planos con sombra dura, fondos pintados sin línea y personajes animados a 12 dibujos por segundo (a dos, como la animación de TV de la época).
- **Tétrico.** Mucha oscuridad, una sola luz por escena (la lámpara, la luna, la mañana), viñeta pesada y color enfermizo.
- **Cinta VHS.** Sangrado de color, líneas, ruido de cinta, fallas de tracking en los sustos, el letrero «▶ PLAY» al empezar y la fecha de videocámara en el recuerdo.
- **Sonido sintetizado.** Plática que se va quedando bajo el agua, voces de caricatura amortiguadas, reloj, latidos, drones, cuerdas disonantes, vidrio que se rompe, pájaros y una caja musical con una canción de cuna original.
- **Subtítulos amarillos** con los dos diálogos, porque en TikTok mucha gente ve sin sonido.

## Cómo renderizar

Necesita Python 3 con `pip install numpy scipy pycairo pillow` y ffmpeg (en Windows: `winget install Gyan.FFmpeg`). Desde la carpeta `la-incision`:

```sh
python3 animacion/render.py                 # el corto completo → la-incision-animada.mp4
python3 animacion/render.py --ancho 540     # borrador rápido a media resolución
python3 animacion/render.py --fotos         # hoja de contactos con un cuadro de cada plano
python3 animacion/render.py --planos 3A 3B  # solo esos planos (para probar cambios)
python3 animacion/render.py --solo-audio    # rehace el sonido sin volver a dibujar
```

Los planos se dibujan en paralelo (uno por núcleo) y se guardan en `animacion/build/`. Las duraciones salen de `plan.json`, así que si cambias el `uso` de un plano, la animación se ajusta. Antes del plano 1A va un gancho de 1.5 s con las máscaras para enganchar en TikTok.

## Archivos

| Archivo | Qué hace |
|---|---|
| [render.py](render.py) | Arma la línea de tiempo, dibuja los planos en paralelo, aplica el acabado y junta video y sonido |
| [planos.py](planos.py) | Los 23 planos: animación, cámara, subtítulos y efectos de cada uno |
| [personajes.py](personajes.py) | Alex (de frente y de perfil) y las figuras enmascaradas |
| [familia.py](familia.py) | Mamá, papá, la hermana, Alex niño y la bebé, más brazos y manos |
| [cuerpo.py](cuerpo.py) | El celular con el chat, el antebrazo con la incisión, la extremidad oscura, Alex en la cama, los chilaquiles |
| [escenarios.py](escenarios.py) | Fondos pintados: el comedor, el cuarto, el techo, el parque y los fondos de los planos cerrados |
| [dibujo.py](dibujo.py) | El lienzo: figuras con sombra de cel, tinta que tiembla, pinceles, luces y cámara |
| [post.py](post.py) | Color por escena, textura de VHS y rótulos |
| [sonido.py](sonido.py) | Toda la pista de sonido, sintetizada |
| [fuentes/](fuentes/) | Creepster (título) y VT323 (letreros de videocasetera), las dos con licencia OFL |

## Las voces

Las líneas de mamá y de Alex suenan como voces de caricatura sin palabras claras y van subtituladas. Si quieres voces reales, grábalas con el celular (las líneas están en [postproduccion.md](../postproduccion.md#voces)) y ponlas encima en CapCut: mamá entre 10.3 y 17.1 s, Alex entre 19.7 y 21.1 s del corto.
