# La Incisión · Postproducción

Cómo armar el corto con las tomas de Kling. El orden y la duración exacta de cada plano están en la [línea de tiempo del shotlist](shotlist-kling.md#linea-de-tiempo).

## Programa y proyecto

- CapCut (gratis y sencillo) o DaVinci Resolve (gratis, con más control de color y audio).
- Proyecto de 1920×1080 a 24 fps. Si vas a entregar en 4K, crea el proyecto en 3840×2160 desde el inicio.

## Preparar el material

- Renombra cada toma elegida con su ID: `1A.mp4`, `1B.mp4`… Así el montaje sigue el shotlist sin buscar.
- Si Kling te entrega a 30 fps, deja que el editor convierta a 24 y revisa que no haya tirones en los movimientos lentos.
- Si un plano quedó corto, alárgalo con la opción de extender de Kling o ralentízalo al 80 % con interpolación de cuadros (en DaVinci: *Optical Flow*).
- Cuando un clip empiece o termine con deformaciones, recorta esos cuadros: por eso cada plano se genera más largo de lo que se usa.

## Transiciones y efectos

| Momento | Efecto | Cómo hacerlo |
|---|---|---|
| 1C → 2A | Corte seco a negro | Clip negro de 1 s en silencio total |
| 2A | Parpadeos pesados de Alex | Dos rectángulos negros con borde difuminado que bajan y suben como párpados (6 a 8 cuadros), o el efecto de parpadeo de CapCut |
| 2D | Los ojos se cierran | Termina el fundido a negro en la edición si Kling no llegó |
| Negro → 3A | Los ojos se abren de golpe | Párpados que se abren en 3 o 4 cuadros, con un desenfoque que se aclara |
| 3C → 4A | Flash blanco | 4 a 6 cuadros de blanco; el recuerdo entra sobreexpuesto y se asienta |
| 4A → 5A | El recuerdo se rompe | El clip 5A, o un efecto de vidrio roto sobre los últimos cuadros de 4A |
| 5B, 5C, 5D | Montaje de flashes | Unos 12 cuadros por flash, con 2 cuadros de blanco o negro entre ellos y una sacudida de cámara |
| 6C → final | Corte a negro | Corte seco y 1 s de silencio absoluto antes del título |

## Sonido por escena

| Escena | Ambiente | Momentos clave |
|---|---|---|
| 1 · La cena | Plática familiar, cubiertos, radio lejana | Al acercarse a Alex, filtro paso bajo (todo suena como bajo el agua) y un zumbido grave. La voz de mamá entra amortiguada y se aclara de golpe en «¿Alex?» |
| 2 · Las tres sombras | Silencio total 1 s; luego tono de cuarto: respiración, ventilador, un perro lejano, crujidos | Cuando aparecen las figuras: drone grave que crece y un pitido agudo tipo acúfeno; la respiración se acelera |
| 3 · La parálisis | Latidos y acúfeno en aumento | Inhalación brusca al abrir los ojos. El grito es mudo, solo aire ahogado. La extremidad: crujido lento de articulaciones |
| 4 · El recuerdo | Pájaros, risas con eco | Golpe en reversa con el flash. Un arrullo tarareado (por ejemplo «A la rorro niño», que es tradicional). El acúfeno desaparece |
| 5 · El despertar | Acúfeno de regreso | Cristal rompiéndose, golpes y glitches en cada flash, bocanada de aire al incorporarse y luego silencio |
| 6 · La incisión | Mañana normal: pájaros, un vendedor o el camión del gas a lo lejos, tenedor contra el plato | Un tono grave entra cuando mira su brazo. Corte a negro en silencio y un golpe grave con el título |

Efectos gratuitos: Freesound y Pixabay (revisa la licencia de cada archivo). Los sonidos de casa (cubiertos, puerta, respiración) quedan mejor grabados por ti con el celular.

## Voces

| Plano | Personaje | Línea |
|---|---|---|
| 1B (fuera de cuadro) | Mamá | «...y entonces le dije a tu tía que no íbamos a poder ir el domingo. ¿Alex? ¿Me estás escuchando, mijo?» |
| 1C | Alex | «Sí, ma. Todo bien.» |

Tres maneras de hacerlas, de la más natural a la más rápida:

1. **Grabarlas con personas reales.** El celular basta. Graba dentro de un clóset con ropa: la ropa absorbe el eco del cuarto.
2. **Audio nativo de Kling 3.0 en español.** Pega el bloque «Audio nativo» de 1B y 1C al final de su prompt y activa el audio.
3. **Voz sintética en español mexicano** y después el Lip Sync de Kling sobre 1C para que los labios coincidan.

La línea de mamá lleva el filtro de «bajo el agua» en la primera mitad; quítalo de golpe en «¿Alex?».

## Música

Casi nada. Un drone grave que crece de 2B a 3C y desaparece en el recuerdo; en la escena 4, el arrullo o un piano suave. El silencio de 5F y el del final valen más que cualquier música. Bancos libres de derechos: Pixabay Music y la Biblioteca de audio de YouTube.

## Color

- Aplica el guion de color de la [biblia visual](biblia-visual.md#guion-de-color).
- Unifica todo el corto con el mismo grano de película y el mismo viñeteado sutil: así los clips de Kling se sienten de la misma cámara.
- El recuerdo (4A): sube las altas luces, añade brillo difuso (*glow*) y una halación rojiza en los bordes de las zonas claras.
- La mañana (escena 6): baja la saturación entre 15 y 20 % y enfría un poco la piel de Alex.
- Opcional: franjas negras 2.39:1 para un look de cine.

## Título

«LA INCISIÓN» en blanco sobre negro, con una tipografía serif delgada y bastante espacio entre letras. Idea: una línea roja fina cruza el título de izquierda a derecha, como un bisturí, y deja pequeñas marcas de sutura. Dura 4 s y entra con un golpe grave. Si lo publicas en redes, puedes repetir el título al principio, justo después de 1C.

## Exportación

- Master: 1920×1080 (o 3840×2160), 24 fps, H.264 o H.265, entre 20 y 40 Mbps.
- Vertical 9:16 para Reels o TikTok: reencuadra plano por plano centrando la acción. Los POV y los insertos (máscaras, brazo) funcionan bien en vertical; el comedor es lo que más sufre. Si el vertical es el formato principal, genera los keyframes también en 9:16.
- Subtítulos: solo hay dos líneas de diálogo. Agrégalos en español (y en inglés si lo vas a mover fuera de México).
