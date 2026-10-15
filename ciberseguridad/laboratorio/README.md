# Laboratorio seguro

Todo se practica aquí o en plataformas legales. **Aislado de tu red doméstica.**

## Opción A · Sin instalar nada (recomendado para empezar)
- [TryHackMe](https://tryhackme.com): máquinas en el navegador (AttackBox).
- [picoCTF](https://picoctf.org), [OverTheWire](https://overthewire.org/wargames/), [PortSwigger Academy](https://portswigger.net/web-security).
- Funciona desde cualquier dispositivo, incluido el móvil/tablet.

## Opción B · Laboratorio local
1. Instalar **VirtualBox** o **VMware Workstation Player**.
2. VM atacante: **Kali Linux** (o Parrot).
3. VMs objetivo (intencionalmente vulnerables): Metasploitable 2, DVWA, OWASP Juice Shop, VulnHub.
4. Red de laboratorio: **Host-Only** o **Red NAT interna**, nunca "puente" con objetivos vulnerables.
5. Hacer **snapshots** antes de cada práctica.

## Opción C · Docker (ligero)
```bash
docker run --rm -p 3000:3000 bkimminich/juice-shop     # OWASP Juice Shop
docker run --rm -p 8080:80 vulnerables/web-dvwa        # DVWA
```
Solo exponer en `localhost`.

## Herramientas a ir conociendo
Nmap · Wireshark · Burp Suite Community · Gobuster/ffuf · John/Hashcat · Metasploit · CyberChef · Ghidra (más adelante)

> Las imágenes de VM, capturas `.pcap` grandes y wordlists pesadas **no** se suben a git.
