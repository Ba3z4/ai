# Cuestionarios con retroalimentación

Abre **`index.html`** en cualquier navegador (PC o móvil). No necesita Internet ni servidor.

- Cada pregunta muestra al instante si acertaste, cuál era la correcta y **por qué**.
- Las opciones salen en orden aleatorio, así que no puedes memorizar posiciones.
- Al final te dice qué **lecciones repasar**.
- El botón **«Repasar fallos»** repite solo lo que fallaste (se guarda en el navegador de ese dispositivo).
- Aprobado: **85 % o más**. Si no, escucha de nuevo las lecciones marcadas y repite.

## Añadir o editar preguntas
Edita `semana-XX.json` (campos: `leccion`, `pregunta`, `opciones`, `correcta` = índice desde 0, `explicacion`) y regenera:
```bash
python3 build.py
```
`build.py` valida los datos y genera `index.html`. Haz commit de ambos.

## Verlo en el móvil
- Descarga `index.html` desde GitHub y ábrelo, o
- Activa GitHub Pages para el repo y usa la URL publicada (Settings → Pages).
