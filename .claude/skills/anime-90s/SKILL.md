---
name: anime-90s
description: Reglas de estilo para hacer animación (con código) que se vea y suene como anime de terror de los 90 — cel pintado sobre fondos de gouache, filmado en película, animación limitada, banda sonora sintetizada y coral. Úsala antes de dibujar personajes, fondos, animar planos o componer sonido de cualquier versión "anime 90s" de La Incisión.
---

# Anime de los 90 (terror), hecho con código

Todo se genera con código: nada de herramientas externas de IA ni de fotos de referencia. Esta skill dice **cómo debe verse, moverse y sonar**, y cómo revisarlo. Los datos vienen de las fuentes de [references.md](references.md); lo marcado como *oficio* es práctica común del medio, no una cita.

**Es anime japonés** (TV/OVA de los 90), no caricatura occidental: diseño de personajes, fondos, cámara, montaje y sonido siguen sus convenciones. La historia y el diálogo se quedan tal cual el guion (mexicana, en español); lo japonés es la manera de dibujarla, animarla, editarla y musicalizarla.

## 1. Cómo se hacía (y por qué se ve así)

- Los fondos se pintaban a mano con **gouache / poster color** sobre papel, uno por escena. Los personajes iban en **acetatos (cels)**: línea entintada y color plano pintado detrás.
- Cada cuadro se **fotografiaba en película**. Por eso el look incluye grano, halación, polvo y un poco de desvaído. No es un filtro "retro": es el aparato de captura.
- Cel shading con **pocos valores** (lo normal son 3: base, sombra, a veces luz), con formas de sombra de borde duro. Nada de degradados en personajes.
- El movimiento es **animación limitada**: se dibuja a 12 fps o menos y en TV se filma "en treses" (cada dibujo dura 3 cuadros, 8 dibujos por segundo). Se sostienen dibujos, se mueve solo una parte (boca, ojos, pelo) sobre un cel fijo, y se mueve la cámara sobre el fondo.

## 2. Arte

**Personajes** (diseño de los 90: más sobrio y refinado que el de los 2000)
- Figuras delgadas, algo alargadas; piel pálida en los pálidos, morena con sombras más cálidas en Alex. Rostros sobrios, ojos expresivos pero **no** gigantes ni chibi; brillos de pelo en bandas duras.
- Línea de grosor visible y firme, entintada; en sombras la línea puede ir en un tono oscuro del color, no negro puro *(oficio)*.
- Sombra en dos escalones; el segundo solo en los momentos de tensión.
- Alex: 22 años, moreno, cansado (ojeras, pelo revuelto, sudadera). Familia: papá, mamá, hermana con siluetas y peinados claramente distintos. Las figuras enmascaradas: **siluetas altísimas, negro sólido, máscara blanca lisa** sin rasgos.

**Fondos**
- Pintados: pinceladas de gouache visibles, colores un poco tizosos, **perspectiva atmosférica** (lo lejano más claro y azulado).
- Muy cargados de detalle cotidiano (fotos en marcos, manteles, trastes) cuando la escena es normal, y **desnudos y oscuros** cuando es horror.
- Halos alrededor de las luces (farolas, lámparas), como los de las lentes empañadas de Ghost in the Shell.

**Color y luz** (terror de los 90)
- Paleta **apagada, filmica**. Nada de saturación de hoy, ni bloom excesivo, ni piel de plástico.
- Realismo sobrio: el ambiente de la cena debe ser *aburrido y cotidiano* (Perfect Blue) para que el horror pese.
- Contraste tipo Lain: día casi blanco, noche negra con **negros profundos** y solo unas luces de color (la ventana, el celular, el reloj rojo).
- Azules saturados con luz artificial para la noche; cálidos ocre-naranja para la cena; blanco lechoso para el recuerdo y la mañana pálida.

**Acabado de película** (siempre, en este orden): paleta filmica → **halación** en zonas muy claras → **grano** de película (más en sombras) → leve **aberración cromática** en bordes → **gate weave** (temblor mínimo del encuadre entero) → **polvo/pelos de cel** ocasionales → viñeta suave. Vertical 9:16 es concesión de TikTok; los planos deben componerse para ese formato.

## 3. Animación

- Base 24 fps de salida, dibujos a **12 dibujos/seg. en movimiento normal, 8 en treses, 4-6 en lo casi quieto**; mantener el mismo dibujo varios cuadros es correcto, no un fallo.
- Recursos obligatorios de la época: **cuadro sostenido** con solo boca/ojos/pelo moviéndose; **panorámica** lenta sobre fondo pintado; **acercamiento** lento (cámara sobre el cel); **líneas de velocidad** con fondo abstracto en los sustos; **plano fijo largo** (Evangelion aguanta más de un minuto un solo dibujo) para tensión; **corte a negro seco**.
- Actuación mínima, con peso: un parpadeo, una pupila que se encoge, un temblor de pelo. Los sustos se hacen con **cortes y sostenidos**, no con movimiento fluido.
- Los flashes del montaje (máscara ladeada, techo girando, brazo liberado) van en 3-6 cuadros cada uno, con destellos blancos y líneas.

## 4. Sonido

- Mezcla de época: **sintetizadores + cuerdas/coro**, mucho silencio, ambiente muy presente y **efectos de foley exagerados**.
- Referencias: Kenji Kawai (coro cantando en armonías abiertas y sin vibrato, percusión antigua con sintetizador), Shiro Sagisu (cantos ominosos, chillidos de violín tipo *Psycho*).
- Receta para esta pieza: pad de sintetizador grave sostenido; golpes de tambor grave espaciados; **coro sin vibrato en quintas** para las figuras; **violines que chillan en glissando** en los sustos; caja de música en el recuerdo; silencio total tras el corte a negro. Voces de la familia amortiguadas en la cena; solo las dos líneas del guion con claridad.
- Música que entra solo cuando la escena lo pide; nada de canción pop ni jazz-fusion tipo Bebop (no es el tono).
- Ancho de banda de la época: recorte suave sobre 12-14 kHz y un poco de siseo de película; sin efectos de VHS.

## 5. Flujo con código

1. Nuevo paquete `la-incision/anime90/` (no reutiliza el arte de versiones previas): `estilo.py` (paleta y acabado de película), `fondos.py` (gouache), `personajes.py`, `planos.py`, `sonido.py`, `render.py`.
2. Contact sheet con **un cuadro por plano** y una tira de 3 cuadros de los planos animados antes de renderizar.
3. Render por plano en paralelo → concatenar → mezcla → versión ligera < 30 MB.

## 6. Lista de revisión (marca todo antes de entregar)

- [ ] Ningún personaje tiene degradado ni contorno de grosor uniforme de vector.
- [ ] Sombras de borde duro, 2 escalones como máximo.
- [ ] Los fondos parecen pintados (textura de pincel), no planos ni degradados de computadora.
- [ ] Hay grano, halación y leve aberración, sin exceso de bloom.
- [ ] La animación se sostiene: no hay movimiento fluido en todo; hay cuadros repetidos.
- [ ] Las máscaras son blancas y lisas; las figuras no tienen cara.
- [ ] El guion original no se alteró (los 23 cuadros, las dos líneas de diálogo).
- [ ] El sonido tiene silencio, síntesis, coro y violín; sin efectos de VHS.
- [ ] 1080×1920, 24 fps, ~109 s, versión ligera < 30 MiB.

## Límites honestos

No se pudo abrir ninguna de las páginas fuente completas (el acceso a esos dominios está bloqueado); esta skill se basa en los resúmenes de las búsquedas. Las técnicas de código son una **aproximación** a la película real, no una réplica.
