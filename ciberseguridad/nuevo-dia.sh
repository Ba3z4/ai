#!/usr/bin/env bash
# Crea la nota de diario de hoy. Uso: ./nuevo-dia.sh [sufijo]   (ej. ./nuevo-dia.sh movil)
set -euo pipefail
cd "$(dirname "$0")"
f="diario/$(date +%F)${1:+-$1}.md"
if [ -e "$f" ]; then echo "Ya existe: $f"; exit 0; fi
cat > "$f" <<NOTA
# $(date +%F)

**Dispositivo:** ${1:-}
**Tiempo:** 
**Módulo:** 

## Qué estudié
-

## Qué aprendí
-

## Qué no entendí
-

## Siguiente
-
NOTA
echo "Creado: $f"
