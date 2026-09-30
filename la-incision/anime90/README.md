# La Incisión · versión anime japonés de los 90

El corto completo, con el guion original plano por plano, hecho **desde cero con código**: nada de herramientas de IA externas ni de imágenes de referencia. Es el estilo del anime de terror japonés de los 90 (TV/OVA): acetatos pintados sobre fondos de gouache, filmados en película, con animación limitada y una banda sonora de sintetizadores, coro y violines. Vertical 9:16, 1080×1920, 24 fps, 1:49, con sonido.

Las reglas de estilo salen de una investigación en blogs y artículos y están en la skill [`.claude/skills/anime-90s`](../../.claude/skills/anime-90s/SKILL.md) (con sus fuentes en `references.md`).

## Cómo renderizar

Necesita Python 3 con `pip install numpy scipy pycairo pillow` y ffmpeg. Las voces usan espeak-ng con MBROLA (`apt install espeak-ng mbrola mbrola-mx1 mbrola-mx2`); sin ellas salen con voces sintéticas de respaldo. Desde la carpeta `la-incision`:

```sh
python3 -m anime90.render                  # → la-incision-anime90.mp4 y su versión ligera (< 30 MB)
python3 -m anime90.render --fotos          # hoja de contactos con dos cuadros de cada plano
python3 -m anime90.render --planos 1A 6C   # vuelve a dibujar solo esos planos y rearma el video
python3 -m anime90.render --solo-audio     # solo rehace el sonido y vuelve a armar
```

## Archivos

| Archivo | Qué hace |
|---|---|
| [cel.py](cel.py) | El acetato: formas planas, media luna de sombra de borde duro, tinta que se afila y curvas suaves |
| [estilo.py](estilo.py) | La textura de gouache de los fondos y el acabado de película: paleta, halación, aberración, grano, temblor de cámara, polvo, viñeta |
| [fondos.py](fondos.py) | Fondos pintados: comedor (noche y día), cuarto, techo, sábana y parque |
| [personajes.py](personajes.py) | Alex, su familia, las figuras enmascaradas, la extremidad, el antebrazo con la incisión, el celular y los chilaquiles |
| [planos.py](planos.py) | Los 22 planos, con la cámara sobre el fondo y la animación limitada del acetato |
| [sonido.py](sonido.py) | La banda sonora: pads, coro sin vibrato, violines que chillan, tambores, caja musical y ambientes |
| [render.py](render.py) | Línea de tiempo, render en paralelo, subtítulos, título, montaje y versión ligera |

## Cómo se ve, cómo se mueve, cómo suena

- **Dibujo.** Personajes delgados y sobrios con ojos rasgados, línea firme, sombra de un solo escalón y reflejo azulado en el pelo. Fondos con pinceladas de gouache, muy cargados en la cena y casi vacíos en el horror.
- **Película.** Halación rojiza en las luces, grano que cambia en cada cuadro, aberración en los bordes, temblor de la ventanilla y motas de polvo.
- **Animación.** El fondo se mueve con la cámara a 24 cuadros; el acetato se redibuja a 8 o 12 dibujos por segundo y se sostiene. Los sustos son cortes y cuadros fijos, con líneas de velocidad.
- **Sonido.** Silencio y ambiente presente; sintetizadores graves, coro en quintas abiertas para las figuras, violines que chillan en los sustos, tambores espaciados, caja musical en el recuerdo. El grito de 3B no suena: solo un pitido.
- **Subtítulos** de fansub (letras blancas con contorno negro) para las dos líneas del guion.
