# La Incisión · Biblia visual

Las reglas de estilo que comparten todos los planos. Los prompts ya las aplican; este documento sirve para corregir una toma que se salió del tono o para escribir planos nuevos.

## Tono

Terror psicológico contenido: pocos sustos y mucha tensión. En la habitación la cámara casi no se mueve, y lo que asusta es lo que se queda quieto. El contraste emocional está en la luz: la calidez de la familia contra el frío de la noche.

Referencias de ambiente:

- *The Nightmare* (2015), documental sobre la parálisis del sueño y sus «figuras de sombra».
- *Fire in the Sky* (1993), por el tono de abducción y la marca física que queda al despertar.
- *It Follows* (2014), por los planos fijos donde algo avanza despacio hacia cámara.

## Formato

- Vertical 9:16 para TikTok, 1080×1920, 24 fps. Los primeros cuadros verticales están en `referencias/vertical/`.
- Montaje de 1:49 (tiempos exactos en [shotlist-kling.md](shotlist-kling.md#linea-de-tiempo)).
- Look base: fotorrealista y cinematográfico, lente de 35 mm, poca profundidad de campo, grano de película.

### Si por «3D» buscas un look animado

Tus referencias son fotorrealistas, y Kling respeta el estilo del fotograma inicial. Para un look de animación 3D (tipo Pixar o cinemática de Unreal):

1. Re-estiliza primero las 5 referencias y los keyframes con un mismo prompt de estilo.
2. En todos los prompts cambia el cierre «Photorealistic, 35mm film look…» por `Stylized 3D animated film, Unreal Engine 5 cinematic render, soft subsurface skin, volumetric light, detailed textures`.
3. Quita `cartoon` y `plastic CGI look` del negative prompt.

No mezcles planos fotorrealistas con planos 3D: elige un solo look para todo el corto.

## Guion de color

| Escena | Luz | Paleta | Qué debe sentirse |
|---|---|---|---|
| 1 · La cena | Tungsteno de la lámpara colgante; la pantalla ilumina a Alex en frío | Ámbar, terracota, madera; azul del celular | Una calidez de la que Alex está ausente |
| 2, 3 y 5 · La habitación | Luna y farola por la ventana | Azul noche y negro profundo; el rojo del reloj como único acento | Asfixia, amenaza quieta |
| 4 · El recuerdo | Hora dorada a contraluz, sobreexpuesta | Dorado y verde follaje | Refugio y amor |
| 6 · La mañana | Luz de día suave por la ventana | Neutra, un poco desaturada | Normalidad rota |

Los códigos de color de cada escena están en el shotlist y en el storyboard.

## Personajes

### Alex

- 22 años, mexicano, piel morena, cabello negro corto con los lados degradados, bigote delgado y barba de pocos días, ojeras, complexión delgada.
- Vestuario: en la escena 1, polo con rayas grises y blancas (tu toma 1A). De la escena 2 a la 6, playera gris lisa de manga corta.
- Brazo izquierdo sin marcas hasta la escena 6.
- Referencia de Alex: [elements/alex-toma1A.jpg](elements/alex-toma1A.jpg), sacada del último cuadro de tu toma 1A, + la hoja de personaje K0.
- Descripción fija para los prompts: *a tired 22-year-old Mexican man with brown skin, short black hair and a thin mustache*.

### La familia (tu toma 1A, ref. 06)

Gemini cambió a la familia de tu imagen 4, y como la toma quedó bien, esta es la familia del corto:

- Mamá (unos 45): cabello largo oscuro, blusa de flores. Es la que habla.
- Papá (unos 50): cabello corto, camisa azul claro.
- Hermana (unos 17): cabello largo oscuro.

### El recuerdo (ref. 02)

Es la infancia de Alex: la abuela, con blusa de flores, carga a la hermana (vestido amarillo y trenzas); mamá joven con blusa bordada; papá joven con polo a rayas y Alex de niño en sus hombros, con playera verde. El papá viste casi igual que Alex en la cena, y ese eco visual ayuda a leer el recuerdo como suyo.

### Las tres figuras

- Muy altas (unos 2.20 m) y delgadas; cuerpos de tela negra desgarrada que se funde con la sombra; cabello negro, largo y lacio; dedos larguísimos.
- Máscara blanca de porcelana mate. En la ref. 05 tienen cuencas negras y rasgos suaves; el guion pide «lisa, sin facciones». Decide una versión y úsala en todo el corto (ver continuidad en el shotlist).
- Movimiento: nunca caminan, se deslizan. Nunca hacen ruido. Casi no se mueven, y cuando algo cambia (un ladeo de cabeza) debe sentirse antinatural.
- Element «Figura»: [elements/figura-enmascarada.jpg](elements/figura-enmascarada.jpg).
- Descripción fija para los prompts: *tall, thin figures with long bodies of tattered black cloth, long black hair and smooth white porcelain masks with hollow black eyes*.

## Locaciones

- **Comedor** (tu toma 1A, ref. 06): pared terracota llena de fotos familiares enmarcadas, mesa de madera con mantel de flores, canasta de tortillas y lámpara de mesa. En la escena 6 es el mismo lugar con luz de mañana y las sillas vacías.
- **Habitación de Alex** (ref. 01): cama de madera tipo trineo con cobijas grises, ventilador de techo oscuro con pantallas blancas, ropero a la izquierda, puerta entreabierta con ropa colgada, cómoda con espejo, repisas con libros, silla con ropa, ventana a la derecha con farola, buró con lámpara y reloj digital rojo.
- **Parque** (ref. 02): encinos, pasto, mantas de picnic y sol a contraluz.

## Objetos clave

- **Celular:** el mismo en todas las tomas (negro, sin funda brillante). Chat con «Mariana 💔»: «Todo está bien» arriba y la pelea abajo.
- **Reloj digital rojo:** 03:14.
- **Chilaquiles:** rojos, con crema, queso fresco y cebolla, en plato de barro, con un café al lado.
- **La incisión:** recta, de unos 8 cm, en la cara interna del antebrazo izquierdo; de 6 a 8 puntos negros perfectamente espaciados; piel enrojecida alrededor y sin sangre.

## Reglas para escribir prompts

- Un plano, una acción principal. Si le pides tres cosas a la vez, Kling hará dos mal.
- Describe el movimiento de principio a fin y di también lo que **no** se mueve («The camera does not move»).
- Repite las descripciones de Alex y de las figuras con las mismas palabras en todos los planos.
- Mantén el mismo cierre de estilo en todos los planos de una escena.
- Nada de texto en pantalla generado por Kling: los chats y el título se ponen en la edición.

## Idea opcional: el tiempo perdido

En los relatos de abducción, la víctima «pierde» horas. Para sembrarlo sin decirlo: en la escena 2 el reloj marca 03:14, como en la ref. 01, y al despertar en 5F marca 05:52. Se hace en la edición poniendo los números encima del reloj.
