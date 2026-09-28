<!-- Archivo generado por herramientas/generar.py a partir de plan.json. Edita plan.json y vuelve a generar. -->

# La Incisión · Prompts para Gemini Omni

Los mismos 20 planos del [shotlist](shotlist-kling.md), adaptados a Gemini Omni (app de Gemini o Google Flow): clips de 3, 5 o 10 s, sonido generado junto con la imagen y la imagen adjunta como primer cuadro. Las imágenes que faltan (K0–K10) se generan con los prompts de [keyframes.md](keyframes.md).

**Planos:** 20 · **Montaje:** 1:50 · **Generación:** 154 s por pasada completa

## Flujo

1. Abre la app de Gemini o Google Flow y elige Gemini Omni, en formato 16:9.
2. En la app de Gemini abre un chat nuevo, elige formato 16:9, adjunta los recortes de elements/ y pega el prompt maestro. En Flow no hace falta.
3. Genera los keyframes K0–K10 con Gemini (imágenes), adjuntando las referencias en el orden de cada prompt, y descárgalos.
4. Genera los planos en orden: adjunta las imágenes de «Adjunta», en ese orden, y pega el prompt de Omni.
5. Si una toma sale casi bien, pide un arreglo rápido en lugar de regenerarla.
6. Descarga cada toma con su ID (1A.mp4, 1B.mp4…) y arma el corte con herramientas/armar_corte.py o en CapCut.

## Ajustes

| Ajuste | Valor |
|---|---|
| Dónde | App de Gemini (crear video con Gemini Omni) o Google Flow con el modelo Gemini Omni Flash. Necesitas Google AI Plus, Pro o Ultra. |
| Formato | 16:9. Elígelo en la configuración de la app o de Flow antes de generar: si solo lo pides en el prompt, puede salir vertical (9:16). |
| Duración | 3, 5 o 10 s por clip, según «Clip». Omni puede extender hasta 40 s, pero aquí cada plano cabe en un clip. |
| Primer cuadro | Adjunta la imagen que indica «Adjunta»: el prompt le dice a Omni que es el cuadro inicial exacto. Si la app de Gemini no la respeta (cambia la familia o el cuarto), usa Flow: «Frames to Video» → «+ Add start frame». |
| Último cuadro | Solo en 2B (ref. 01 → K2). En Flow: «+ Add end frame». |
| Personajes | Los recortes de Alex y de la figura van solo con el prompt maestro. No los adjuntes en cada plano: Omni los convierte en un plano extra al inicio. Adjunta solo los cuadros que indica «Adjunta». |
| Audio | Omni genera el sonido junto con la imagen. Cada prompt ya trae su audio y los diálogos en español, sin música: la música va en la edición. |
| Arreglos | Si una toma sale casi bien, no la regeneres: pide un solo cambio por mensaje. |
| Límites | Tu plan tiene un límite diario de videos. Con 20 planos y reintentos puede tomarte más de un día. |

## Prompt maestro

Pégalo en un chat nuevo de la app de Gemini con `elements/alex-rostro.jpg` y `elements/figura-enmascarada.jpg` adjuntos, en ese orden. En Flow no hace falta.

```text
Vamos a producir, plano por plano, un cortometraje de terror de 1:50 llamado «La Incisión». Formato 16:9, look cinematográfico fotorrealista: lente de 35 mm, poca profundidad de campo y grano de película.

Historia: Alex, de 22 años, cena con su familia pero tiene la cabeza en una pelea con su novia. Esa noche, paralizado en su cama, tres figuras con máscaras blancas lo rodean. A la mañana siguiente descubre en su antebrazo izquierdo una incisión con suturas perfectas: no fue un sueño.

Personajes:
- Alex: 22 años, mexicano, piel morena, cabello negro corto con los lados degradados, bigote delgado y ojeras. En la cena usa una polo blanca con rayas grises; de noche y en el desayuno, una playera gris lisa. La primera imagen adjunta es su rostro.
- Su familia: mamá (unos 50 años, blusa estampada), papá (unos 55, bigote, camisa a cuadros) y hermana (unos 19, playera rosa).
- Las tres figuras: altísimas y delgadas, de tela negra desgarrada, cabello negro largo y máscaras blancas de porcelana con cuencas negras. Nunca caminan: se deslizan. Nunca hacen ruido. La segunda imagen adjunta es una de ellas.

Reglas para cada video:
1. Te mandaré cada plano con su ID (1A, 1B…), su duración y su prompt en inglés. Genera solo ese plano y espera el siguiente.
2. La imagen que adjunte en cada plano es su cuadro inicial exacto: empieza ahí, en un solo plano continuo, sin cortes y con las mismas personas y el mismo lugar.
3. Sigue el prompt al pie de la letra: una sola acción por plano y cámara fija cuando lo pida.
4. Sin subtítulos ni texto en pantalla. Diálogos en español con acento mexicano y labios sincronizados. Sin música.
5. Mantén a Alex, la familia y las figuras idénticos en todos los planos.
6. Si te pido un cambio, cambia solo eso y deja todo lo demás igual.

Si entendiste, responde solo «Listo».
```

## Escena 1 · La cena

`INT. COMEDOR CASA MEXICANA - NOCHE`

<a id="1a"></a>

### 1A · La cena

**Clip:** 10 s · **Usa en el montaje:** 9 s  
**Adjunta:** 1) Ref. 04 (primer cuadro)  
**Qué pasa:** La familia platica y se pasa los platos; Alex, inmóvil, mira el celular. La cámara se acerca despacio y el foco pasa de la familia a su cara.

```text
Shot 1A, 10 seconds, 16:9. The attached image is the exact first frame. One continuous shot with no cuts. Slow cinematic dolly-in on a lively Mexican family dinner at night. The mother talks animatedly and gestures with her hands, the father smiles while cutting his chicken, and the sister laughs and reaches for the tortilla basket. Only the young man in the striped polo shirt in the foreground stays completely still, head down, staring at the phone in his hand, his face lit by the cold glow of the screen. As the camera drifts toward him, the focus slowly shifts from the family to his face, and the family softens into warm, blurry bokeh. Warm tungsten light from a hanging lamp, terracotta walls, framed family photos. Photorealistic, 35mm film look, shallow depth of field, natural film grain. Audio: lively family chatter in Mexican Spanish and clinking cutlery; as the camera reaches the young man, the voices become muffled, as if heard underwater, under a low hum. No music. No subtitles or on-screen text.
```

> En la ref. 04 el celular está sobre la mesa y el guion dice «debajo». No cambia la historia; si te importa, corrígelo en el keyframe.

<a id="1b"></a>

### 1B · POV: el chat

**Clip:** 10 s · **Usa en el montaje:** 8 s  
**Adjunta:** 1) Ref. 03 (primer cuadro)  
**Qué pasa:** Vemos el chat por los ojos de Alex. El pulgar desliza, las manos tiemblan y las letras se desenfocan un instante. La voz de la madre entra amortiguada.

```text
Shot 1B, 10 seconds, 16:9. The attached image is the exact first frame. One continuous shot with no cuts. First-person POV of a young man holding a smartphone with both hands at a family dinner table at night. His thumb slowly scrolls the chat on the screen. His hands tremble slightly with tension and the phone rises and falls gently with his breathing. For a moment the focus drifts and the text on the screen softens, as if his eyes lose focus from stress, then it sharpens again. In the background the family keeps eating and talking, completely out of focus in warm bokeh. Warm tungsten light from a hanging lamp. Photorealistic, 35mm film look, shallow depth of field, natural film grain. Audio: the family chatter is muffled, as if heard underwater, under a low hum. Then a warm middle-aged Mexican woman's voice off-screen, growing clearer, says in Spanish: "...y entonces le dije a tu tía que no íbamos a poder ir el domingo. ¿Alex? ¿Me estás escuchando, mijo?" No music. No subtitles or on-screen text.
```

> Ruta rápida: usa la ref. 03 tal cual (el texto puede deformarse un poco). Ruta pro: genera desde K1 (pantalla verde) y en la edición pon una grabación real del chat que empiece en «Todo está bien» y baje hasta la pelea.

<a id="1c"></a>

### 1C · «Sí, ma. Todo bien.»

**Clip:** 10 s · **Usa en el montaje:** 6 s  
**Adjunta:** 1) [K10 · Alex en la cena (plano medio corto)](keyframes.md#k10) (primer cuadro)  
**Qué pasa:** Alex bloquea el celular, levanta la vista y finge media sonrisa: «Sí, ma. Todo bien.» La sonrisa se le borra en cuanto dejan de mirarlo.

```text
Shot 1C, 10 seconds, 16:9. The attached image is the exact first frame. One continuous shot with no cuts. Medium close-up of Alex, a tired 22-year-old Mexican man with brown skin, short black hair and a thin mustache, wearing a white and gray striped polo shirt, sitting at a family dinner table at night. He quickly locks his phone and the screen goes dark. He looks up toward his mother off-screen, forces a small, unconvincing half-smile and says quietly: "Sí, ma. Todo bien." A moment later the smile fades and his eyes drop again, empty and exhausted. Warm tungsten light, the family dinner blurred in the background. Photorealistic, 35mm film look, shallow depth of field, natural film grain. Audio: his voice is tired and flat, in Mexican Spanish, and he says the line only once. Muffled family chatter continues in the background. No music. No subtitles or on-screen text.
```

> Omni sincroniza los labios con la voz. Si no suena mexicana o repite la línea, usa los arreglos rápidos.

## Escena 2 · Las tres sombras

`INT. HABITACIÓN DE ALEX - NOCHE`

<a id="2a"></a>

### 2A · La habitación en penumbra

**Clip:** 10 s · **Usa en el montaje:** 8 s  
**Adjunta:** 1) Ref. 01 (primer cuadro)  
**Qué pasa:** Penumbra y silencio. Las sombras de los rincones se estiran de forma antinatural. Alex parpadea, pesado.

```text
Shot 2A, 10 seconds, 16:9. The attached image is the exact first frame. One continuous shot with no cuts. Static first-person POV from a bed in a dark bedroom at night, as if lying on the pillow and looking into the room. The camera does not move. Everything is silent and still. The ceiling fan turns very slowly and the curtain moves slightly. The shadows in the corners of the room slowly stretch and creep up the walls in an unnatural way, as if they were alive. The streetlight outside the window flickers faintly. No people in the room. Cold blue moonlight through the window, deep black shadows, the red digital clock as the only warm light. Photorealistic horror film look, low-key lighting, heavy film grain. Audio: heavy silence, slow calm breathing close to the camera, the soft hum of the ceiling fan, a distant dog barking once and the house creaking. No music. No subtitles or on-screen text.
```

> El parpadeo pesado de Alex se hace en la edición (párpados negros que bajan y suben), no en el generador.

<a id="2b"></a>

### 2B · Aparecen las tres sombras

**Clip:** 10 s · **Usa en el montaje:** 7 s  
**Adjunta:** 1) Ref. 01 (primer cuadro) · 2) [K2 · La habitación con las tres figuras](keyframes.md#k2) (último cuadro)  
**Qué pasa:** La oscuridad de la esquina se espesa y de ella salen tres figuras altas con máscara blanca. Se quedan quietas, observándolo.

```text
Shot 2B, 10 seconds, 16:9. The first attached image is the exact first frame and the second attached image is the exact last frame. One continuous shot with no cuts. Static first-person POV from a bed in a dark bedroom at night. The camera does not move. In the far corner, between the half-open door and the dresser, the darkness slowly thickens and takes shape: three tall, thin figures emerge from the shadows one by one and stand perfectly still, silently facing the bed. They have long bodies of tattered black cloth, long black hair and smooth white porcelain masks. Once they appear, they do not move at all. Cold blue moonlight, deep black shadows, photorealistic horror film look, low-key lighting, heavy film grain. Audio: near silence and slow breathing; as the figures appear, a deep low drone slowly rises and a faint high-pitched ringing begins. The figures make no sound. No music. No subtitles or on-screen text.
```

> En la app de Gemini adjunta primero la ref. 01 y luego K2. En Flow usa «Frames to Video» con los dos cuadros.

<a id="2c"></a>

### 2C · El cuerpo no responde (opcional)

**Clip:** 5 s · **Usa en el montaje:** 3 s  
**Adjunta:** 1) [K3 · Alex paralizado (primer plano)](keyframes.md#k3) (primer cuadro)  
**Qué pasa:** Inserto del rostro de Alex: el cuerpo no responde, solo los ojos se mueven. Parálisis del sueño.

```text
Shot 2C, 5 seconds, 16:9. The attached image is the exact first frame. One continuous shot with no cuts. Close-up of Alex, a 22-year-old Mexican man with brown skin, lying on his back in bed in the dark, lit only by cold blue moonlight. His body is completely frozen; only his eyes move, darting from side to side in terror. His breathing becomes fast and shallow, a drop of sweat runs down his temple, and his fingers twitch, but his body cannot move. Photorealistic horror film look, low-key lighting, heavy film grain, shallow depth of field. Audio: fast, shallow, panicked breathing through the nose, a racing heartbeat and a high-pitched ringing. No music. No subtitles or on-screen text.
```

> Opcional. Rompe el POV del guion, pero le pone cara al terror. Va entre 2B y 2D.

<a id="2d"></a>

### 2D · Se deslizan hacia él

**Clip:** 10 s · **Usa en el montaje:** 8 s  
**Adjunta:** 1) [K2 · La habitación con las tres figuras](keyframes.md#k2) (primer cuadro)  
**Qué pasa:** Las figuras se deslizan hacia la cama sin caminar. La imagen tiembla (él lucha) y se oscurece mientras se le cierran los ojos.

```text
Shot 2D, 10 seconds, 16:9. The attached image is the exact first frame. One continuous shot with no cuts. Static first-person POV from a bed, lying down and unable to move. Three tall shadowy figures with smooth white porcelain masks stand in the dark bedroom, watching. Very slowly they begin to glide toward the bed without moving their legs, as if floating, their masks fixed on the camera. The camera trembles slightly, as if the viewer is desperately trying to move but cannot. The edges of the image slowly darken and blur as the eyelids grow heavy, until the image fades almost completely to black. Cold blue moonlight, deep black shadows, photorealistic horror film look, heavy film grain. Audio: the deep drone keeps rising, the breathing becomes strained and desperate and the ringing grows louder, then everything fades into silence as the image goes dark. No music. No subtitles or on-screen text.
```

> Si la imagen no llega a negro, termina el fundido en la edición.

## Escena 3 · La parálisis

`INT. HABITACIÓN DE ALEX - MADRUGADA`

<a id="3a"></a>

### 3A · Las máscaras encima

**Clip:** 10 s · **Usa en el montaje:** 6 s  
**Adjunta:** 1) [K4 · POV al techo: las máscaras encima](keyframes.md#k4) (primer cuadro)  
**Qué pasa:** Los ojos se abren de golpe: las tres máscaras flotan a centímetros de su cara. La del centro ladea la cabeza.

```text
Shot 3A, 10 seconds, 16:9. The attached image is the exact first frame. One continuous shot with no cuts. First-person POV lying on the back in bed, looking straight up at the dark ceiling. Three smooth white porcelain masks with hollow black eyes lean over the viewer only a few centimeters from the camera, their long black hair hanging down toward the lens. They are perfectly still and staring; only their hair sways slightly. Very slowly, the middle mask tilts its head to one side. The camera trembles subtly, as if the viewer is struggling but cannot move. Cold blue moonlight, deep black shadows, photorealistic horror film look, heavy film grain. Audio: a sharp gasp at the first frame, then a loud heartbeat and an intense high-pitched ringing. The masks make no sound. No music. No subtitles or on-screen text.
```

> Entra desde negro, con los ojos abriéndose de golpe (3 o 4 cuadros) y una inhalación brusca.

<a id="3b"></a>

### 3B · El grito sin voz

**Clip:** 5 s · **Usa en el montaje:** 4 s  
**Adjunta:** 1) [K3 · Alex paralizado (primer plano)](keyframes.md#k3) (primer cuadro)  
**Qué pasa:** Intenta gritar: abre la boca y no sale nada. Solo tiembla.

```text
Shot 3B, 5 seconds, 16:9. The attached image is the exact first frame. One continuous shot with no cuts. Extreme close-up of Alex's face as he lies on his back in bed in cold blue moonlight, completely paralyzed. He tries to scream: his mouth opens wide but no sound comes out, the tendons in his neck tighten, his wide eyes fill with tears and his face trembles with effort, but his head does not move. Photorealistic horror film look, low-key lighting, heavy film grain. Audio: no scream at all, only a choked, airless rasp, a pounding heartbeat and the high-pitched ringing. No music. No subtitles or on-screen text.
```

> Omni siempre genera sonido. El prompt pide un grito mudo; si se oye un grito, pide que lo quite.

<a id="3c"></a>

### 3C · La extremidad oscura

**Clip:** 10 s · **Usa en el montaje:** 5 s  
**Adjunta:** 1) [K5 · El antebrazo y la mano oscura](keyframes.md#k5) (primer cuadro)  
**Qué pasa:** Una extremidad larga y oscura se acerca a su antebrazo izquierdo y, justo antes de tocarlo, corte a blanco.

```text
Shot 3C, 10 seconds, 16:9. The attached image is the exact first frame. One continuous shot with no cuts. Close-up of a young man's left forearm lying still on a dark bed sheet, palm up, in cold blue moonlight. From the darkness at the top of the frame, a long, thin, unnaturally jointed black hand with very long fingers slowly reaches toward the inside of the forearm. The forearm trembles slightly but cannot pull away. The fingertips stop a few millimeters above the skin. Slow, tense movement, deep black shadows, photorealistic horror film look, heavy film grain. Audio: a slow, dry creaking of joints, like knuckles cracking, over the heartbeat and the ringing. No music. No subtitles or on-screen text.
```

> Corta justo antes del contacto y entra directo el flash blanco de 4A.

## Escena 4 · El recuerdo

`INT. MENTE DE ALEX - SUEÑO/FLASHBACK`

<a id="4a"></a>

### 4A · El parque

**Clip:** 10 s · **Usa en el montaje:** 8 s  
**Adjunta:** 1) Ref. 02 (primer cuadro)  
**Qué pasa:** Tras un destello de luz, la familia de su infancia ríe en un parque soleado, en cámara lenta. Paz absoluta.

```text
Shot 4A, 10 seconds, 16:9. The attached image is the exact first frame. One continuous shot with no cuts. Dreamlike slow-motion memory of a happy Mexican family in a sunny park at golden hour. The grandmother laughs and gently rocks the little girl in the yellow dress in her arms, the mother hugs them and smiles, and the father laughs as he bounces the little boy on his shoulders while the boy throws his head back laughing. Warm sunlight flares through the oak trees and the leaves sway softly in the breeze. The camera slowly pushes in. Soft glow, bloom and halation, bright overexposed highlights, warm golden colors, peaceful and loving atmosphere, photorealistic, 35mm film look. Audio: the ringing disappears; warm, echoing laughter of children and adults, birds singing, a gentle breeze and a woman softly humming a lullaby. No subtitles or on-screen text.
```

> Entra con un flash blanco de 4 a 6 cuadros. Si el movimiento sale exagerado, añade «subtle movement» al prompt.

## Escena 5 · El despertar

`INT. HABITACIÓN DE ALEX - MADRUGADA`

<a id="5a"></a>

### 5A · El recuerdo se rompe

**Clip:** 5 s · **Usa en el montaje:** 3 s  
**Adjunta:** 1) Último cuadro de 4A (primer cuadro)  
**Qué pasa:** El recuerdo se congela y se rompe como cristal hacia la oscuridad.

```text
Shot 5A, 5 seconds, 16:9. The attached image is the exact first frame. One continuous shot with no cuts. The image of the happy family in the sunny park freezes like a photograph. Thin cracks spread across the entire picture like breaking glass, then it shatters into hundreds of sharp shards that fall away in slow motion into complete darkness. Glinting glass edges, cinematic, photorealistic. Audio: glass cracking and shattering with a long reverberant tail, and the high-pitched ringing returns. No music. No subtitles or on-screen text.
```

> Inicio: exporta el último cuadro de 4A. Alternativa: el efecto de vidrio roto de CapCut sobre el final de 4A.

<a id="5b"></a>

### 5B · Flash: la máscara ladea la cabeza

**Clip:** 3 s · **Usa en el montaje:** 1 s  
**Adjunta:** 1) Ref. 05 (primer cuadro)  
**Qué pasa:** Flash: una máscara blanca ladea la cabeza de forma antinatural.

```text
Shot 5B, 3 seconds, 16:9. The attached image is the exact first frame. One continuous shot with no cuts. Fast push-in toward the central figure's smooth white porcelain mask in a dark bedroom until the mask fills the frame. The mask slowly and unnaturally tilts its head sideways, almost ninety degrees, still staring at the camera. Cold blue moonlight, deep black shadows, photorealistic horror film look, heavy film grain. Audio: a sharp distorted hit and a glitchy crackle. No music. No subtitles or on-screen text.
```

> Solo usarás 1 s. Genera 5 s y quédate con el instante más raro del ladeo.

<a id="5c"></a>

### 5C · Flash: el techo girando

**Clip:** 3 s · **Usa en el montaje:** 1 s  
**Adjunta:** 1) [K4 · POV al techo: las máscaras encima](keyframes.md#k4) (primer cuadro)  
**Qué pasa:** Flash: el techo gira violentamente.

```text
Shot 5C, 3 seconds, 16:9. The attached image is the exact first frame. One continuous shot with no cuts. First-person POV looking up at a dark bedroom ceiling with a ceiling fan. The camera suddenly spins fast and violently around its axis; the ceiling and the fan whirl in circles with heavy motion blur, and the white masks at the edges smear into streaks of pale light. Disorienting and chaotic. Cold blue moonlight, photorealistic horror film look, heavy film grain. Audio: a violent whoosh and a distorted rumble. No music. No subtitles or on-screen text.
```

> Solo usarás 1 s.

<a id="5d"></a>

### 5D · Flash: recupera el brazo

**Clip:** 3 s · **Usa en el montaje:** 1 s  
**Adjunta:** 1) [K5 · El antebrazo y la mano oscura](keyframes.md#k5) (primer cuadro)  
**Qué pasa:** Flash: la mano oscura se retira; Alex cierra el puño y recupera el brazo.

```text
Shot 5D, 3 seconds, 16:9. The attached image is the exact first frame. One continuous shot with no cuts. Close-up of a young man's left forearm lying on a dark bed sheet in cold blue moonlight. The long black shadowy hand quickly pulls back into the darkness and disappears. The fingers twitch, then the hand clenches into a tight fist and the whole arm jerks upward, out of the frame. Sudden, fast movement, photorealistic horror film look, heavy film grain. Audio: a sharp impact as the arm jerks free and a short gasp. No music. No subtitles or on-screen text.
```

> Solo usarás 1 s: el instante del puño.

<a id="5e"></a>

### 5E · Despierta de golpe

**Clip:** 5 s · **Usa en el montaje:** 4 s  
**Adjunta:** 1) [K6 · Alex acostado (plano medio)](keyframes.md#k6) (primer cuadro)  
**Qué pasa:** Alex se incorpora de golpe, empapado en sudor frío, jadeando.

```text
Shot 5E, 5 seconds, 16:9. The attached image is the exact first frame. One continuous shot with no cuts. Medium shot of Alex, a 22-year-old Mexican man with brown skin and short black hair, wearing a gray t-shirt, lying on his back in bed in a dark bedroom. Suddenly he sits bolt upright, gasping desperately for air, his face and t-shirt drenched in cold sweat and his chest heaving. He looks around the room in panic. Cold blue moonlight from the window, deep shadows, photorealistic horror film look, heavy film grain. Audio: a huge, desperate gasp for air, then heavy, ragged breathing and the creak of the bed. No music. No subtitles or on-screen text.
```

> Si tarda en incorporarse, acelera el clip en la edición.

<a id="5f"></a>

### 5F · El cuarto vacío

**Clip:** 10 s · **Usa en el montaje:** 6 s  
**Adjunta:** 1) Ref. 01 (primer cuadro)  
**Qué pasa:** Mira alrededor: la esquina donde estaban las figuras está vacía. Solo la luz de la luna. Silencio.

```text
Shot 5F, 10 seconds, 16:9. The attached image is the exact first frame. One continuous shot with no cuts. First-person POV from a bed in a dark bedroom, breathing heavily. The camera rises slightly as if sitting up, slowly pushes in toward the dark corner between the half-open door and the dresser, which is completely empty, then pans nervously to the right toward the window. The room is empty and silent; only cold moonlight comes in through the window. Subtle handheld movement, low-key lighting, photorealistic horror film look, heavy film grain. Audio: only his heavy breathing slowly calming down, and deep silence in the room. No music. No subtitles or on-screen text.
```

> Sin música aquí: solo respiración y silencio.

## Escena 6 · La incisión

`INT. COMEDOR CASA MEXICANA - DÍA (MAÑANA)`

<a id="6a"></a>

### 6A · Desayuno en silencio

**Clip:** 10 s · **Usa en el montaje:** 8 s  
**Adjunta:** 1) [K7 · El comedor en la mañana](keyframes.md#k7) (primer cuadro)  
**Qué pasa:** Luz de mañana. Alex desayuna chilaquiles solo, pálido, con la mirada perdida.

```text
Shot 6A, 10 seconds, 16:9. The attached image is the exact first frame. One continuous shot with no cuts. Wide shot of a Mexican family dining room in the morning, soft natural daylight coming through a window. The house is calm and quiet. Alex, a pale 22-year-old Mexican man in a gray t-shirt, sits alone at the wooden table in front of a plate of red chilaquiles and a cup of coffee. He mechanically pushes the food around with his fork without eating, then stops and stares at the empty space in front of him, lost. The camera slowly pushes in toward him. Neutral, slightly desaturated colors, still and quiet atmosphere, photorealistic, 35mm film look, natural film grain. Audio: a calm morning: birds outside, a distant street vendor calling out, the soft scrape of a fork on a clay plate and a quiet refrigerator hum. No music. No subtitles or on-screen text.
```

> Si cambia la comida, añade «the plate of chilaquiles stays the same».

<a id="6b"></a>

### 6B · El ardor

**Clip:** 5 s · **Usa en el montaje:** 4 s  
**Adjunta:** 1) [K8 · Alex en el desayuno (primer plano)](keyframes.md#k8) (primer cuadro)  
**Qué pasa:** Siente un ardor sordo y baja la mirada hacia su brazo izquierdo.

```text
Shot 6B, 5 seconds, 16:9. The attached image is the exact first frame. One continuous shot with no cuts. Close-up of Alex, a pale and exhausted 22-year-old Mexican man with brown skin, short black hair and a thin mustache, wearing a gray t-shirt, sitting at a dining table in soft morning daylight. He stares blankly into nothing. Suddenly he frowns slightly, as if feeling a dull, burning pain, and slowly lowers his gaze toward his left arm. Neutral, slightly desaturated colors, photorealistic, 35mm film look, shallow depth of field, natural film grain. Audio: the same quiet morning ambience; a low, ominous tone slowly rises as he looks down. No music. No subtitles or on-screen text.
```

<a id="6c"></a>

### 6C · No fue un sueño

**Clip:** 10 s · **Usa en el montaje:** 5 s  
**Adjunta:** 1) [K9 · La incisión](keyframes.md#k9) (primer cuadro)  
**Qué pasa:** Levanta el antebrazo: una incisión con suturas quirúrgicas perfectas. Corte a negro.

```text
Shot 6C, 10 seconds, 16:9. The attached image is the exact first frame. One continuous shot with no cuts. Close-up of a young man's left forearm with brown skin in soft morning daylight, the inside of the forearm facing the camera. A long, straight, fresh surgical incision runs along it, slightly reddened, closed with neat, perfectly spaced black surgical stitches. The forearm rises slightly into the light and turns a little toward the camera while the fingers tremble. The camera slowly pushes in toward the stitches. Clinical and precise, realistic skin texture, no blood, photorealistic, 35mm film look, shallow depth of field. Audio: the low ominous tone swells while the morning ambience fades away, ending in total silence. No music. No subtitles or on-screen text.
```

> Deja «clinical» y «no blood» para no activar el filtro de contenido. Revisa que sea el brazo izquierdo.

## Arreglos rápidos

Si una toma sale casi bien, pide un solo cambio en el mismo chat en vez de regenerarla.

| Si pasa esto | Escribe |
|---|---|
| Salió vertical | No se arregla con un mensaje: cambia el formato a 16:9 en la configuración y genera de nuevo. |
| Hizo cortes o empezó con otro plano | Deja todo igual, pero que sea un solo plano continuo, sin cortes, que empiece exactamente en la imagen adjunta. |
| Cambió la familia o el cuarto | Usa exactamente las personas y el cuarto de la imagen adjunta, sin cambiar a nadie. |
| Se movió la cámara | Deja todo igual, pero la cámara no debe moverse en absoluto. |
| El movimiento es muy rápido | Deja todo igual y haz el movimiento el doble de lento. |
| Salió texto o subtítulos | Deja todo igual y quita todo el texto y los subtítulos. |
| Cambió la cara de Alex | Deja todo igual, pero la cara de Alex debe ser idéntica a la imagen de referencia. |
| Quedó muy iluminado | Deja todo igual, pero más oscuro: solo luz de luna azul y fría por la ventana. |
| Las figuras caminan | Deja todo igual, pero las figuras no mueven las piernas: se deslizan flotando. |
| Salió el brazo derecho | Deja todo igual, pero tiene que ser el antebrazo izquierdo. |
| Metió música | Deja todo igual y quita la música; deja solo el sonido ambiente. |
| La voz no suena mexicana | Deja todo igual y que la voz tenga un acento mexicano natural. |
| Repitió el diálogo | Deja todo igual y que diga la línea una sola vez. |
