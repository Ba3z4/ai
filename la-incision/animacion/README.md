# La Incisión, versión animada

El corto completo como **cinta de terror analógico**: dibujos de caricatura de los 90 grabados en una cinta VHS gastada que alguien encontró. Es vertical 9:16 para TikTok, 1080×1920, 24 fps, dura unos 2 minutos y tiene sonido. Todo se dibuja y se sintetiza con código, sin generadores de video ni grabaciones, así que se puede volver a renderizar igual cuantas veces haga falta.

## El formato

| Tramo | Qué se ve |
|---|---|
| Gancho (1.5 s) | Las máscaras encima de su cara, la cinta se traba y se va a nieve |
| Barras (1.5 s) | Barras de color con tono de prueba, «▶ PLAY» y la etiqueta «CINTA 07 · CASO A.R.» |
| Escenas 1 a 6 | Los 20 planos del guion, con la hora de la cinta en pantalla |
| 03:17 A.M. | El negro entre la cena y la noche es una tarjeta con la hora |
| Aviso (10.5 s) | Interrupción de emergencia: tono de alerta y una voz de transmisión que lee el aviso |
| Título (4 s) | «LA INCISIÓN» con una línea de suturas, «■ STOP» y nieve |

La hora de la cinta cuenta la historia por su cuenta. La cena es a las 21:47. La parálisis empieza a las 03:17. En el despertar el contador se vuelve loco y, cuando Alex se incorpora, marca **05:58 en rojo**: pasaron casi tres horas que no recuerda.

## El estilo

- **Dibujo de los 90.** Tinta que tiembla, colores planos con sombra dura, fondos pintados y personajes animados a 12 dibujos por segundo.
- **Cinta gastada en una tele de tubo.** La imagen se dibuja a 720 px y se agranda, para que tenga la suavidad del VHS. Lleva negros lavados, color corrido, líneas que tiemblan, la barra de zumbido que baja por la pantalla, rayitas de cinta, fallas de tracking en los sustos y esquinas redondeadas de CRT.
- **Cuadros subliminales.** Una máscara de dos cuadros cuando se le borra la sonrisa, las figuras de vuelta en el rincón durante dos cuadros en el cuarto vacío y un cuadro de «NO FUE UN SUEÑO» en el desayuno.
- **Closed captions de los 90.** Letras blancas mayúsculas sobre cajas negras, porque en TikTok mucha gente ve sin sonido.
- **Sonido.** Voces sintéticas (mamá, Alex y el locutor del aviso), plática que se queda bajo el agua, reloj, latidos, drones, vidrio que se rompe, caja musical en el recuerdo, tono de prueba, tono de alerta, zumbido de tele y temblor de cinta en toda la mezcla.

## Cómo renderizar

Necesita Python 3 con `pip install numpy scipy pycairo pillow` y ffmpeg (en Windows: `winget install Gyan.FFmpeg`). Las voces usan [espeak-ng](https://github.com/espeak-ng/espeak-ng) con las voces MBROLA mexicanas (en Ubuntu: `apt install espeak-ng mbrola mbrola-mx1 mbrola-mx2`); si no están, el corto sale con voces de caricatura. Desde la carpeta `la-incision`:

```sh
python3 animacion/render.py                 # el corto completo → la-incision-animada.mp4
python3 animacion/render.py --ancho 360     # borrador rápido
python3 animacion/render.py --fotos         # hoja de contactos con un cuadro de cada plano
python3 animacion/render.py --planos 3A 3B  # solo esos planos (para probar cambios)
python3 animacion/render.py --solo-audio    # rehace el sonido sin volver a dibujar
python3 animacion/render.py --portada       # portada para TikTok → portada-tiktok.png
python3 animacion/render.py --ligero        # versión de menos de 30 MB (1080×1920) con lo ya renderizado
```

Los planos se dibujan en paralelo (uno por núcleo) y se guardan en `animacion/build/`. Con 4 núcleos el corto completo tarda unos 10 minutos. El video final se limita a unos 7 Mbps (unos 100 MB) para que se pueda subir a TikTok desde el celular, y junto a él sale `la-incision-animada-ligera.mp4`, también en 1080×1920 pero de menos de 30 MB, para mandarlo por chat. Las duraciones de los planos salen de `plan.json`, así que si cambias el `uso` de un plano, la animación se ajusta.

## Archivos

| Archivo | Qué hace |
|---|---|
| [render.py](render.py) | Arma la línea de tiempo, dibuja los planos en paralelo, pone la hora de la cinta y los letreros, y junta video y sonido |
| [planos.py](planos.py) | Los planos: animación, cámara, tarjetas, subtítulos, subliminales y efectos de cada uno |
| [personajes.py](personajes.py) | Alex (de frente y de perfil) y las figuras enmascaradas |
| [familia.py](familia.py) | Mamá, papá, la hermana, Alex niño y la bebé, más brazos y manos |
| [cuerpo.py](cuerpo.py) | El celular con el chat, el antebrazo con la incisión, la extremidad oscura, Alex en la cama, los chilaquiles |
| [escenarios.py](escenarios.py) | Fondos pintados: el comedor, el cuarto, el techo, el parque y los fondos de los planos cerrados |
| [dibujo.py](dibujo.py) | El lienzo: figuras con sombra de cel, tinta que tiembla, pinceles, luces y cámara |
| [post.py](post.py) | Color por escena, la cinta VHS en la tele de tubo y los rótulos |
| [sonido.py](sonido.py) | Toda la pista de sonido, sintetizada |
| [pasos.py](pasos.py) | «Cómo abrir a un humano»: el guion en pasos, el narrador y las ilustraciones |
| [render_pasos.py](render_pasos.py) | Voz del narrador, línea de tiempo, música y render de esa versión |
| [pintura.py](pintura.py) | El acabado de pintura (Kuwahara, póster, lienzo) y la franja con la palabra |
| [fuentes/](fuentes/) | VT323 (letreros de videocasetera) y Cinzel (la palabra del narrador), las dos con licencia OFL |

## Otra versión: «Cómo abrir a un humano»

La misma historia contada al estilo de los videos de «cómo encerrar a un ángel». Una de las figuras enmascaradas, frente al cosmos, dicta ocho pasos con voz grave, palabra por palabra, y entre paso y paso aparecen ilustraciones de lo que le hicieron a Alex:

1. Elige a uno que ya no escuche (la cena).
2. Espera a que su casa duerma (03:17).
3. Entra por el rincón más oscuro.
4. Quítale la voz, que grite hacia adentro.
5. Dale un recuerdo feliz para que no mire.
6. Ábrelo. Toma lo que viniste a buscar.
7. Cóselo con cuidado.
8. Devuélvelo a su mesa. Déjalo creer que fue un sueño.

Cierra con «Volveremos» y un glitch. El arte es de ilustración oscura pintada: sin contornos, con pinceladas planas (filtro Kuwahara), colores tipo póster, claroscuro y luces de color. La palabra que dice el narrador aparece en una franja negra con letra romana (Cinzel), y la máscara abre una boca cuando habla. La voz marca el ritmo: cada ilustración dura lo que tardan sus palabras. Debajo van un colchón de acordes en re menor con coro, un golpe en cada «PASO» y pocos efectos.

```sh
python3 animacion/render_pasos.py           # → la-incision-como-abrir-un-humano.mp4 y su versión ligera
python3 animacion/render_pasos.py --fotos   # hoja de contactos con una ilustración de cada tramo
```

El guion está en `GUION` dentro de [pasos.py](pasos.py): si cambias una palabra, la voz, los tiempos y las ilustraciones se ajustan solos.

## Las voces

Mamá, Alex y el aviso usan voces de computadora a propósito: en el terror analógico son parte del estilo. Si prefieres voces reales para la cena, grábalas con el celular (las líneas están en [postproduccion.md](../postproduccion.md#voces)) y ponlas encima en CapCut. Mamá habla entre los segundos 11.8 y 18.8 del corto y Alex entre 21.2 y 22.7.
