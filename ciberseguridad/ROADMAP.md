# Roadmap: de cero a ciberseguridad

Marca con `[x]` lo completado. Orden recomendado; no te saltes fundamentos.

## Fase 0 · Fundamentos (4–6 semanas) → `00-fundamentos/`
- [ ] (Detalle semana a semana en `00-fundamentos/TEMARIO.md`) Cómo funciona una computadora: CPU, memoria, almacenamiento, procesos
- [ ] Sistemas numéricos (binario, hexadecimal) y codificaciones (ASCII, UTF-8, Base64)
- [ ] Tríada CIA (confidencialidad, integridad, disponibilidad), riesgo, amenaza, vulnerabilidad
- [ ] Terminología: malware, phishing, ransomware, exploit, CVE, CVSS
- [ ] Git y Markdown (para este mismo repo)
- [ ] Python básico: variables, funciones, archivos, módulos, `requests`
- [ ] Bash básico

## Fase 1 · Redes (4–6 semanas) → `01-redes/`
- [ ] Modelo OSI y TCP/IP
- [ ] IP, subredes, NAT, MAC, ARP
- [ ] DNS, DHCP, HTTP/HTTPS, TLS, SSH, FTP, SMB
- [ ] TCP vs UDP, handshake de 3 vías, puertos
- [ ] Wireshark: capturar y leer tráfico
- [ ] Firewalls, VPN, proxies, IDS/IPS

## Fase 2 · Sistemas operativos (4 semanas) → `02-sistemas-linux/`
- [ ] Linux: sistema de archivos, permisos, usuarios, procesos, servicios
- [ ] Administración desde la terminal, logs (`/var/log`), cron
- [ ] Windows: registro, Active Directory (conceptos), PowerShell básico
- [ ] Hardening básico

## Fase 3 · Criptografía (3 semanas) → `03-criptografia/`
- [ ] Simétrica vs asimétrica, hashes, firmas digitales
- [ ] AES, RSA, curvas elípticas (concepto)
- [ ] Certificados, PKI, TLS en detalle
- [ ] Gestión de contraseñas, salting, bcrypt/argon2
- [ ] Retos de criptografía básica (CryptoHack)

## Fase 4 · Seguridad web (4–6 semanas) → `04-seguridad-web/`
- [ ] Cómo funciona una aplicación web (cliente, servidor, cookies, sesiones)
- [ ] OWASP Top 10
- [ ] Inyección SQL, XSS, CSRF, IDOR, SSRF, subida de archivos
- [ ] Autenticación y control de acceso
- [ ] Burp Suite (Community)
- [ ] PortSwigger Web Security Academy

## Fase 5 · Ofensiva ética (6+ semanas) → `05-ofensiva-etica/`
- [ ] Metodología: reconocimiento, escaneo, explotación, post-explotación, reporte
- [ ] Nmap, Gobuster/ffuf, Metasploit (conceptos y uso en lab)
- [ ] Escalada de privilegios Linux/Windows
- [ ] Ataques a contraseñas (hashcat/john en lab)
- [ ] Redacción de informes de pentest

## Fase 6 · Defensa / Blue Team (6+ semanas) → `06-defensa-blue-team/`
- [ ] Logs, SIEM, detección (Wazuh / Elastic / Splunk free)
- [ ] Análisis de malware básico (estático)
- [ ] Respuesta a incidentes, forense básico
- [ ] MITRE ATT&CK, threat intelligence
- [ ] Hardening y gestión de vulnerabilidades

## Fase 7 · Práctica continua → `07-ctf-y-practica/`
- [ ] TryHackMe: ruta "Pre Security" → "Jr Penetration Tester"
- [ ] picoCTF, OverTheWire (Bandit)
- [ ] Hack The Box (máquinas fáciles retiradas)
- [ ] Participar en un CTF en equipo
- [ ] Escribir write-ups de cada reto resuelto

## Certificaciones (opcional, en este orden)
CompTIA Security+ → eJPT / PNPT (ofensiva) o BTL1 / CySA+ (defensa) → OSCP (avanzado)
