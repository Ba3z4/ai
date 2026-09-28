<!-- Archivo generado por herramientas/generar.py a partir de plan.json. Edita plan.json y vuelve a generar. -->

# La Incisión · Keyframes

Son las imágenes que faltan para animar los planos. Genéralas **antes** que los videos, en 16:9 y a la mayor resolución que permita tu plan.

- En Kling usa **Imágenes** con referencia (o edición con varias referencias, según tu versión). Cualquier generador con referencias sirve.
- «The reference image» o «the first/second reference image» son las imágenes que subes, en ese orden. Si tu herramienta usa etiquetas (por ejemplo @imagen1), cámbialas en el prompt.
- Genera 3 o 4 variantes y quédate con la que mejor respete la continuidad (ver [shotlist-kling.md](shotlist-kling.md)).

| Keyframe | Se usa en |
|---|---|
| [K0 · Hoja de personaje de Alex](#k0) | Element «Alex» |
| [K1 · Celular con pantalla verde (ruta pro)](#k1) (opcional) | 1B (inicio, ruta pro) |
| [K2 · La habitación con las tres figuras](#k2) | 2B (fin) · 2D (inicio) |
| [K3 · Alex paralizado (primer plano)](#k3) | 2C · 3B |
| [K4 · POV al techo: las máscaras encima](#k4) | 3A · 5C |
| [K5 · El antebrazo y la mano oscura](#k5) | 3C · 5D |
| [K6 · Alex acostado (plano medio)](#k6) | 5E |
| [K7 · El comedor en la mañana](#k7) | 6A · referencia de luz para K8 y K9 |
| [K8 · Alex en el desayuno (primer plano)](#k8) | 6B |
| [K9 · La incisión](#k9) | 6C |
| [K10 · Alex en la cena (plano medio corto)](#k10) | 1C |

<a id="k0"></a>

## K0 · Hoja de personaje de Alex

<img src="elements/alex-rostro.jpg" width="220" alt="Recorte «Alex»">

**Referencias:** Recorte «Alex»  
**Se usa en:** Element «Alex»  
**Cómo:** Imagen con referencia de rostro o personaje: sube elements/alex-rostro.jpg.

```text
Character reference sheet of the young man in the reference image: a 22-year-old Mexican man with brown skin, short black hair with faded sides, a thin mustache and light stubble, tired eyes with dark circles, slim build. Three views side by side in one image: front, three-quarter and profile, neutral expression, wearing a plain heather-gray crew-neck t-shirt, neutral gray studio background, soft even lighting. Photorealistic, detailed skin texture, the same face in all three views.
```

> Crea el Element «Alex» con el recorte + esta hoja. Si la cara de frente no se parece, genera varias y quédate con la más fiel al perfil.

<a id="k1"></a>

## K1 · Celular con pantalla verde (ruta pro) (opcional)

<img src="referencias/03-pov-chat.jpg" width="220" alt="Ref. 03">

**Referencias:** Ref. 03  
**Se usa en:** 1B (inicio, ruta pro)  
**Cómo:** Edición de imagen sobre la ref. 03.

```text
Edit the reference image: replace everything on the phone screen with a flat, evenly lit, solid bright green screen (#00FF00) with no interface, no text and no reflections, and remove the ring from the finger. Keep the hands, the phone, the dinner table, the blurred family in the background and the warm lighting exactly the same.
```

> Solo si vas a meter el chat real en la edición (croma + seguimiento). Así el texto se lee perfecto y puedes empezar en «Todo está bien» antes de la pelea.

<a id="k2"></a>

## K2 · La habitación con las tres figuras

<img src="referencias/01-habitacion-noche.jpg" width="220" alt="Ref. 01"> <img src="referencias/05-figuras-enmascaradas.jpg" width="220" alt="Ref. 05">

**Referencias:** Ref. 01, Ref. 05  
**Se usa en:** 2B (fin) · 2D (inicio)  
**Cómo:** Edición con dos referencias: la ref. 01 como imagen base y la ref. 05 para las figuras.

```text
Keep the dark bedroom from the first reference image exactly as it is: same camera angle from the bed, same wardrobe, half-open door, dresser with mirror, wall shelves, window with the streetlight and the red digital clock. Add the three tall, thin figures from the second reference image, standing in the far corner between the half-open door and the dresser and silently facing the bed: long bodies of tattered black cloth, long black hair and smooth white porcelain masks with hollow black eyes. They are partly swallowed by the shadows. Cold blue moonlight, deep black shadows, photorealistic horror film still, heavy film grain, 16:9.
```

> Este cuadro y la ref. 01 deben tener el mismo encuadre: son el inicio y el fin de 2B.

<a id="k3"></a>

## K3 · Alex paralizado (primer plano)

<img src="elements/alex-rostro.jpg" width="220" alt="Recorte «Alex»">

**Referencias:** Recorte «Alex», K0 · Hoja de personaje de Alex  
**Se usa en:** 2C · 3B  
**Cómo:** Imagen con el Element o la referencia de personaje de Alex.

```text
Close-up of the young man from the reference, a 22-year-old Mexican man with brown skin, short black hair and a thin mustache, lying on his back in bed with his head on a dark gray pillow, wearing a plain gray t-shirt. His eyes are wide open in terror, his body is frozen and there is a thin layer of sweat on his forehead. Lit only by cold blue moonlight from a window, deep black shadows. Photorealistic horror film still, 35mm, shallow depth of field, film grain, 16:9.
```

<a id="k4"></a>

## K4 · POV al techo: las máscaras encima

<img src="referencias/01-habitacion-noche.jpg" width="220" alt="Ref. 01"> <img src="referencias/05-figuras-enmascaradas.jpg" width="220" alt="Ref. 05">

**Referencias:** Ref. 01, Ref. 05  
**Se usa en:** 3A · 5C  
**Cómo:** Imagen con dos referencias: la ref. 01 (ventilador y ambiente) y la ref. 05 (figuras).

```text
First-person point of view lying on the back in bed, looking straight up at a dark bedroom ceiling with a dark wooden ceiling fan with white glass shades, like the fan in the first reference. Three smooth white porcelain masks with hollow black eyes, like the figures in the second reference, lean over the viewer from above, very close to the camera, filling most of the frame. Their long black hair hangs down toward the lens and their dark bodies merge with the darkness. Cold blue moonlight, deep black shadows, photorealistic horror film still, wide-angle lens, heavy film grain, 16:9.
```

<a id="k5"></a>

## K5 · El antebrazo y la mano oscura

<img src="elements/alex-rostro.jpg" width="220" alt="Recorte «Alex»"> <img src="referencias/05-figuras-enmascaradas.jpg" width="220" alt="Ref. 05">

**Referencias:** Recorte «Alex», Ref. 05  
**Se usa en:** 3C · 5D  
**Cómo:** Imagen con referencia de piel (Alex) y de las figuras (ref. 05).

```text
Close-up of a young Mexican man's left forearm with brown skin, resting palm up on a dark gray bed sheet at night, the sleeve of a gray t-shirt visible at the edge of the frame. From the darkness at the top of the frame, a long, thin, black shadowy hand with unnaturally long fingers reaches toward the inside of the forearm, almost touching it. Cold blue moonlight, deep black shadows, photorealistic horror film still, macro lens, heavy film grain, 16:9.
```

> Revisa que sea el brazo IZQUIERDO. Si sale el derecho, voltea la imagen horizontalmente.

<a id="k6"></a>

## K6 · Alex acostado (plano medio)

<img src="elements/alex-rostro.jpg" width="220" alt="Recorte «Alex»"> <img src="referencias/01-habitacion-noche.jpg" width="220" alt="Ref. 01">

**Referencias:** Recorte «Alex», Ref. 01  
**Se usa en:** 5E  
**Cómo:** Imagen con el Element de Alex y la ref. 01 como referencia de la habitación.

```text
Medium side shot of the young man from the reference, a 22-year-old Mexican man with brown skin, short black hair and a thin mustache, wearing a plain gray t-shirt, lying on his back in a dark wooden sleigh bed with dark gray bedding, in the same dark bedroom as the second reference. His eyes are closed, he looks restless and there is sweat on his face. Cold blue moonlight from the window, ceiling fan above, dark wooden furniture. Photorealistic horror film still, 35mm, film grain, 16:9.
```

<a id="k7"></a>

## K7 · El comedor en la mañana

<img src="referencias/04-comedor-cena.jpg" width="220" alt="Ref. 04"> <img src="elements/alex-rostro.jpg" width="220" alt="Recorte «Alex»">

**Referencias:** Ref. 04, Recorte «Alex»  
**Se usa en:** 6A · referencia de luz para K8 y K9  
**Cómo:** Edición de la ref. 04 (mismo comedor) con el Element de Alex.

```text
The same Mexican dining room as the reference image, with the same textured walls, framed family photos, green arch and plants, but now in the morning with soft natural daylight coming through a window. The table is clean and all the other chairs are empty. The young man from the reference, now wearing a plain gray t-shirt, sits alone at the center of the table, pale and exhausted, in front of a clay plate of red chilaquiles with cream, crumbled fresh cheese and sliced onion, next to a cup of coffee. Neutral, slightly desaturated colors, quiet atmosphere, photorealistic 35mm film still, 16:9.
```

<a id="k8"></a>

## K8 · Alex en el desayuno (primer plano)

<img src="elements/alex-rostro.jpg" width="220" alt="Recorte «Alex»">

**Referencias:** K7 · El comedor en la mañana, Recorte «Alex»  
**Se usa en:** 6B  
**Cómo:** Imagen con el Element de Alex; usa K7 como referencia de luz y fondo.

```text
Close-up of the young man from the reference, a pale, exhausted 22-year-old Mexican man with brown skin, short black hair and a thin mustache, wearing a plain gray t-shirt, sitting at a wooden dining table in soft morning daylight. He stares blankly into nothing, with dark circles under his eyes. A textured wall with framed family photos is blurred in the background. Photorealistic, 35mm, shallow depth of field, film grain, 16:9.
```

<a id="k9"></a>

## K9 · La incisión

<img src="elements/alex-rostro.jpg" width="220" alt="Recorte «Alex»">

**Referencias:** Recorte «Alex», K7 · El comedor en la mañana  
**Se usa en:** 6C  
**Cómo:** Imagen con referencia de piel (Alex) y K7 para la luz de la mañana.

```text
Close-up of a young Mexican man's left forearm with brown skin, held up in soft morning daylight with the inside of the forearm facing the camera. A long, straight, fresh surgical incision runs along the forearm, slightly reddened and swollen, closed with neat, perfectly spaced black surgical stitches. Clinical and precise, no blood. A plate of chilaquiles on a wooden table is blurred in the background. Photorealistic, 50mm macro, shallow depth of field, realistic skin texture, 16:9.
```

> Deja «clinical» y «no blood» para no activar el filtro de contenido. Brazo IZQUIERDO.

<a id="k10"></a>

## K10 · Alex en la cena (plano medio corto)

<img src="referencias/04-comedor-cena.jpg" width="220" alt="Ref. 04">

**Referencias:** Ref. 04  
**Se usa en:** 1C  
**Cómo:** Edición o reencuadre de la ref. 04.

```text
Medium close-up of the young man in the white and gray striped polo shirt from the reference image, sitting at the family dinner table at night, head down, looking at the phone in his hands, his tired face lit by the cold glow of the screen and turned slightly toward the camera. Behind him the family dinner is blurred into warm bokeh. Warm tungsten light from a hanging lamp, photorealistic 35mm film still, shallow depth of field, film grain, 16:9.
```
