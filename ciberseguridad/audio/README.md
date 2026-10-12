# Lecciones para escuchar en el celular

Textos escritos para **oírse**: frases cortas, sin tablas ni código, con un resumen «para recordar» al final. Cada uno dura 3–5 minutos de audio.

## Escuchar desde el celular

Los MP3 viven en [`mp3/`](mp3/) dentro del repo. En el celular:

1. Abre la carpeta `ciberseguridad/audio/mp3/` en la app o web de GitHub.
2. Toca el MP3: GitHub lo reproduce, o usa **Descargar** para guardarlo en el teléfono y oírlo con tu reproductor (así sigue sonando con la pantalla apagada y sin datos mientras haces ejercicio).
3. Tip: descarga toda la semana antes de salir.

### Semana 1
| Sesión | Audio | Texto |
|---|---|---|
| 1 · Las piezas de una computadora | [mp3](mp3/semana-01-sesion-1.mp3) | [md](semana-01-sesion-1.md) |
| 2 · Sistema operativo, kernel y procesos | [mp3](mp3/semana-01-sesion-2.mp3) | [md](semana-01-sesion-2.md) |
| 3 · Archivos y almacenamiento | [mp3](mp3/semana-01-sesion-3.mp3) | [md](semana-01-sesion-3.md) |
| 4 · La memoria de un programa | [mp3](mp3/semana-01-sesion-4.mp3) | [md](semana-01-sesion-4.md) |
| 5 · Repaso en voz alta | [mp3](mp3/semana-01-sesion-5.mp3) | [md](semana-01-sesion-5.md) |

## De dónde salen los MP3 (elige una)

**A · Automático con GitHub.** Cada vez que se sube un `semana-*.md`, el workflow `.github/workflows/audio.yml` genera los MP3 y los guarda en `mp3/`. También puedes lanzarlo a mano: pestaña **Actions → Generar audio de las lecciones → Run workflow**. Tarda ~1 min; luego haz `git pull` en tus equipos.

**B · Desde tu PC.**
```bash
pip install edge-tts
./generar-audio.sh                                   # crea mp3/*.mp3
git add -A && git commit -m "Audio" && git push      # para que lleguen al celular
```
La voz se cambia con `VOZ=es-ES-ElviraNeural ./generar-audio.sh` (otras: es-MX-JorgeNeural, es-AR-TomasNeural).

**Sin MP3 todavía:** abre el `.md` desde el celular y usa el lector del sistema (Android: *Seleccionar para escuchar*; iPhone: *Hablar pantalla*).

## Flujo recomendado
Celular: escuchas las sesiones (ejercicio, trayecto, tareas) → PC: haces el [cuestionario](../cuestionarios/README.md) de la semana y los ejercicios del [temario](../00-fundamentos/TEMARIO.md).
