#!/usr/bin/env bash
# instalar-asur-lab.sh — Instala el cliente asur-lab en la VM (una sola vez, sin sudo).
# Universidad de la Costa · Seguridad en Redes · 2026-2
#
# Uso: bash instalar-asur-lab.sh        (desde GitHub Pages del curso)
#      ASUR_LAB_URL=http://127.0.0.1:8000 bash instalar-asur-lab.sh  (local)

set -u

: "${ASUR_LAB_URL:=https://asur-col.github.io/cuc-seguridad-redes}"
DESTINO="$HOME/.local/bin/asur-lab"

ok()   { printf '\033[32m[OK]\033[0m   %s\n' "$*"; }
mal()  { printf '\033[31m[ERROR]\033[0m %s\n' "$*" >&2; }
info() { printf '\033[36m[INFO]\033[0m %s\n' "$*"; }
aviso(){ printf '\033[33m[AVISO]\033[0m %s\n' "$*"; }

mkdir -p "$(dirname "$DESTINO")"

if command -v curl >/dev/null 2>&1; then
  curl -fsSL --retry 3 --connect-timeout 10 -o "$DESTINO" \
    "${ASUR_LAB_URL}/laboratorios/asur-lab" \
  || { mal "no se pudo descargar asur-lab"; exit 1; }
elif command -v wget >/dev/null 2>&1; then
  wget -q -t 3 --connect-timeout=10 -O "$DESTINO" \
    "${ASUR_LAB_URL}/laboratorios/asur-lab" \
  || { mal "no se pudo descargar asur-lab"; exit 1; }
else
  mal "se necesita curl o wget"; exit 1
fi

chmod +x "$DESTINO"
ok "asur-lab instalado en $DESTINO"

# Asegurar que ~/.local/bin está en el PATH
case ":$PATH:" in
  *:"$HOME/.local/bin":*) ;;
  *) aviso "Agregue '$HOME/.local/bin' a su PATH (ej.: export PATH=\"\$HOME/.local/bin:\$PATH\")" ;;
esac

echo
info "Pruebe: asur-lab lista"
echo "      asur-lab iniciar lab06"
