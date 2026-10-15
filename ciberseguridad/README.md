# Ciberseguridad desde cero

Proyecto personal para aprender ciberseguridad paso a paso, pensado para trabajarlo desde **varios dispositivos** (PC, laptop, móvil, sesiones en la nube) con git como fuente única de verdad.

## Cómo está organizado

| Carpeta | Para qué |
|---|---|
| [`ROADMAP.md`](ROADMAP.md) | Ruta de aprendizaje completa, con checklist |
| [`PROGRESO.md`](PROGRESO.md) | Dónde voy, qué sigue, qué me cuesta |
| `00-fundamentos` … `07-ctf-y-practica` | Notas y ejercicios por módulo |
| [`laboratorio/`](laboratorio/README.md) | Cómo montar un lab seguro y aislado |
| `recursos/` | Libros, cursos, plataformas, cheatsheets |
| `diario/` | Una nota por día de estudio (`AAAA-MM-DD.md`) |

## Flujo multi-dispositivo

1. **Al empezar a estudiar:** `git pull`
2. Estudia y escribe notas en el módulo que toque (Markdown, funciona en cualquier dispositivo).
3. Crea o actualiza la nota del día: `./nuevo-dia.sh` (crea `diario/AAAA-MM-DD.md`).
4. Marca lo avanzado en `ROADMAP.md` y `PROGRESO.md`.
5. **Al terminar:** `git add -A && git commit -m "..." && git push`

Reglas para no tener conflictos entre dispositivos:
- Un commit por sesión de estudio, siempre `pull` antes y `push` después.
- Una nota de diario por día; si estudias en dos dispositivos el mismo día, usa sufijo (`-movil`, `-laptop`).
- Nada de binarios pesados, capturas grandes ni imágenes de VM en git (ya están en `.gitignore`).
- **Nunca** subas contraseñas, tokens, claves privadas, ni datos reales de terceros.

## Ética y legalidad (léelo primero)

Todo lo que se practique aquí es **solo en entornos propios o autorizados**: tu laboratorio, máquinas de plataformas de práctica (TryHackMe, Hack The Box, picoCTF…) o CTFs. Atacar sistemas sin permiso escrito es ilegal. Ver [`ETICA.md`](ETICA.md).
