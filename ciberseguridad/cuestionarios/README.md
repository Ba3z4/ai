# Cuestionarios con retroalimentación

Pensado para hacerse en la **PC de escritorio** después de escuchar las lecciones en el celular.

**En la PC:** `git pull`, entra a `ciberseguridad/cuestionarios/` y abre **`index.html`** con doble clic (Chrome, Firefox, Edge…). No necesita Internet ni servidor. También funciona en el móvil si lo prefieres.

- Cada pregunta muestra al instante si acertaste, cuál era la correcta y **por qué**.
- Las opciones salen en orden aleatorio, así que no puedes memorizar posiciones.
- Al final te dice qué **lecciones repasar**.
- El botón **«Repasar fallos»** repite solo lo que fallaste (se guarda en el navegador de ese dispositivo, así que usa siempre la misma PC y el mismo navegador).
- Aprobado: **85 % o más**. Si no, escucha de nuevo las lecciones marcadas y repite.

## Añadir o editar preguntas
Edita `semana-XX.json` (campos: `leccion`, `pregunta`, `opciones`, `correcta` = índice desde 0, `explicacion`) y regenera:
```bash
python3 build.py
```
`build.py` valida los datos y genera `index.html`. Haz commit de ambos.

