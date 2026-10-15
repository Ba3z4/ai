#!/usr/bin/env bash
# Convierte las lecciones .md en MP3 para escucharlas con el móvil mientras haces ejercicio.
# Requiere: pip install edge-tts   (voz neuronal gratuita, necesita Internet)
# Uso: ./generar-audio.sh                 (todas)   |   ./generar-audio.sh semana-01-sesion-1.md
set -euo pipefail
cd "$(dirname "$0")"
VOZ="${VOZ:-es-MX-DaliaNeural}"   # otras: es-ES-ElviraNeural, es-MX-JorgeNeural, es-AR-TomasNeural
mkdir -p mp3
for f in ${@:-semana-*.md}; do
  out="mp3/${f%.md}.mp3"
  # quita la línea de título "# ..." y marcas markdown
  sed -e '1d' -e 's/[*_`#]//g' "$f" > "/tmp/$$.txt"
  edge-tts --voice "$VOZ" --rate="+0%" --file "/tmp/$$.txt" --write-media "$out"
  echo "OK  $out"
done
rm -f "/tmp/$$.txt"
