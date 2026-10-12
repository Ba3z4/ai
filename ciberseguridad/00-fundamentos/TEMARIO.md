# Fase 0 · Fundamentos: temario detallado (6 semanas)

**Ritmo sugerido:** 5 sesiones/semana de ~1–1,5 h (≈ 30–45 h en total). Si vas más lento, estira a 8 semanas; lo importante es la constancia.
**Cada sesión:** `git pull` → estudiar → nota en `diario/` (`../nuevo-dia.sh`) → `git push`.
**Regla de oro:** después de cada tema, explícalo con tus palabras en un archivo `notas-*.md` de esta carpeta. Si no puedes explicarlo, no lo has aprendido.

---

## Semana 1 · Cómo funciona una computadora
**Objetivo:** entender qué hay dentro de un equipo y qué ocurre cuando ejecutas un programa.

| Sesión | Tema | Qué hacer |
|---|---|---|
| 1 | CPU, RAM, disco, placa base; qué hace cada uno | Dibuja un diagrama a mano y fotografíalo; describe qué pasa al abrir un navegador |
| 2 | Sistema operativo, kernel, procesos, hilos | Ver procesos activos en tu equipo (Administrador de tareas / `ps`, `top`) e identificar 5 y su función |
| 3 | Sistema de archivos y almacenamiento (particiones, tipos de FS) | Explora las carpetas de tu SO; anota para qué sirve cada carpeta del sistema |
| 4 | Memoria: stack, heap, memoria virtual (concepto) | Resumen de una página: por qué importa en seguridad (desbordamientos, a nivel conceptual) |
| 5 | Repaso + mini-quiz propio de 10 preguntas | Responde sin mirar; revisa errores |

**Recursos:** CS50 (Harvard, gratis) semanas 0 y 1 · "Crash Course Computer Science" (YouTube) episodios 1–10.
**Entregable:** `notas-computadora.md`.

## Semana 2 · Números, datos y codificaciones
**Objetivo:** leer y convertir datos como lo hace un analista (base de forense y criptografía).

| Sesión | Tema | Qué hacer |
|---|---|---|
| 1 | Binario y hexadecimal: conversiones a mano | 20 conversiones decimal↔binario↔hex |
| 2 | ASCII y UTF-8; bytes vs. caracteres | Escribe tu nombre en hex y binario |
| 3 | Base64 y URL-encoding: para qué sirven (no es cifrado) | Codifica/decodifica con CyberChef |
| 4 | Operaciones bit a bit: AND, OR, XOR (XOR es clave en cripto) | Cifra y descifra un mensaje con XOR en papel |
| 5 | Práctica con CyberChef | Resuelve 5 retos "Base64/hex/XOR" en picoCTF (General Skills) |

**Recursos:** CyberChef · picoCTF "General Skills".
**Entregable:** `notas-codificaciones.md` con tabla de conversiones y ejemplos.

## Semana 3 · Conceptos de seguridad y panorama de amenazas
**Objetivo:** hablar el idioma de la ciberseguridad con precisión.

| Sesión | Tema | Qué hacer |
|---|---|---|
| 1 | Tríada CIA; autenticidad y no repudio | Para 5 incidentes reales, indica qué pilar se vio afectado |
| 2 | Activo, amenaza, vulnerabilidad, riesgo, control | Haz el análisis de riesgo de tu propia vida digital (cuentas, teléfono, correo) |
| 3 | Tipos de malware (virus, gusano, troyano, ransomware, spyware) | Tabla comparativa con ejemplo histórico de cada uno |
| 4 | Ingeniería social y phishing | Analiza 3 correos de phishing (ejemplos públicos) y marca las señales de alerta |
| 5 | CVE, CVSS, NVD, exploits y parches | Busca un CVE conocido y resume qué afectaba, su puntuación y la solución |

**Recursos:** TryHackMe "Pre Security" (intro a seguridad) · NIST glosario · cve.org / nvd.nist.gov.
**Entregable:** `glosario.md` (mínimo 40 términos con tus palabras).

## Semana 4 · Hábitos de seguridad y defensa personal
**Objetivo:** aplicar lo aprendido a ti mismo (la primera línea de defensa).

| Sesión | Tema | Qué hacer |
|---|---|---|
| 1 | Contraseñas, gestores de contraseñas, entropía | Instala un gestor (Bitwarden/KeePassXC); migra tus cuentas |
| 2 | MFA / 2FA: tipos y robustez (SMS < TOTP < llave física) | Activa MFA en correo, GitHub y redes principales |
| 3 | Actualizaciones, copias de seguridad (regla 3-2-1), cifrado de disco | Configura backup y cifrado de disco |
| 4 | Privacidad: navegador, extensiones, permisos de apps, VPN (qué sí y qué no hace) | Audita permisos en tu teléfono |
| 5 | Revisión de brechas | Revisa tus correos en haveibeenpwned.com y corrige lo que encuentres |

**Entregable:** `checklist-seguridad-personal.md` (tu lista verificada).

## Semana 5 · Terminal, Bash y Git
**Objetivo:** moverte con soltura en la línea de comandos y versionar tu trabajo.

| Sesión | Tema | Qué hacer |
|---|---|---|
| 1 | Navegación: `pwd ls cd mkdir rm cp mv cat less` | OverTheWire **Bandit** niveles 0–5 |
| 2 | Búsqueda y filtros: `grep find head tail sort uniq wc`, pipes `\|` y redirecciones | Bandit niveles 6–10 |
| 3 | Permisos y usuarios: `chmod chown`, rwx, `sudo` (concepto) | Explica `-rwxr-x---` con tus palabras |
| 4 | Scripts Bash: variables, `if`, `for` | Escribe un script que cuente líneas de todos los `.md` del repo |
| 5 | Git: `clone commit branch merge`, resolver un conflicto | Provoca y resuelve un conflicto a propósito en una rama de prueba |

**Recursos:** OverTheWire Bandit · "The Linux Command Line" (William Shotts, gratis) caps. 1–10 · Pro Git (libro gratis) caps. 1–3.
**Entregable:** `cheatsheet-bash.md` y `cheatsheet-git.md`.

## Semana 6 · Python para seguridad (básico) + evaluación
**Objetivo:** automatizar tareas simples y cerrar la fase.

| Sesión | Tema | Qué hacer |
|---|---|---|
| 1 | Variables, tipos, condicionales, bucles | 10 ejercicios en Python.org tutorial o CS50P |
| 2 | Funciones, listas, diccionarios, archivos | Programa que lee un archivo y cuenta palabras |
| 3 | Módulos y entorno virtual: `venv`, `pip`, `hashlib`, `base64` | Calcula el SHA-256 de un archivo y verifica su integridad |
| 4 | HTTP básico con `requests` (solo contra sitios propios/de práctica) | Pide una página de `httpbin.org` e imprime cabeceras |
| 5 | **Evaluación final de la fase** | Ver abajo |

**Mini-proyecto:** `herramientas/hash_checker.py` (calcula y compara hashes de archivos) + `herramientas/password_strength.py` (estima la fortaleza de una contraseña por longitud/variedad; nunca guardes contraseñas reales).

---

## Evaluación final (criterios para pasar a la Fase 1)
- [ ] Conviertes entre binario/decimal/hex a mano sin ayuda.
- [ ] Explicas CIA, riesgo, amenaza y vulnerabilidad con ejemplos propios.
- [ ] Distingues cifrado, codificación y hash.
- [ ] Completaste OverTheWire Bandit hasta el nivel 10 y 5 retos de picoCTF.
- [ ] Tu checklist de seguridad personal está aplicada (gestor + MFA + backup).
- [ ] Haces commits y resuelves conflictos en git.
- [ ] Escribiste los dos scripts de Python del mini-proyecto.
- [ ] `glosario.md` con ≥ 40 términos.

Al terminar: marca la Fase 0 en [`../ROADMAP.md`](../ROADMAP.md), actualiza [`../PROGRESO.md`](../PROGRESO.md) y pasa a `01-redes/`.
