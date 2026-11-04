#!/usr/bin/env bash
# lab06.sh — Atajo real del Lab 6: instala asur-lab (si falta) e inicia el lab.
# Uso:  bash lab06.sh        (o desde ~/Descargas: bash ~/Descargas/lab06.sh)
# Universidad de la Costa · Seguridad en Redes · 2026-2 · Semana 13

set -u

ASUR_LAB_URL="${ASUR_LAB_URL:-https://asur-col.github.io/cuc-seguridad-redes}"
export ASUR_LAB_URL

aviso() { printf '\033[33m[AVISO]\033[0m %s\n' "$*"; }
info()  { printf '\033[36m[INFO]\033[0m  %s\n' "$*"; }

if ! command -v docker >/dev/null 2>&1; then
  echo "Se necesita Docker instalado (ejecute el Lab 5 / Ubuntu primero)." >&2
  exit 1
fi
if ! docker info >/dev/null 2>&1; then
  echo "Docker no responde. Ejecute: sudo systemctl start docker" >&2
  exit 1
fi

export PATH="$HOME/.local/bin:$PATH"
if ! command -v asur-lab >/dev/null 2>&1; then
  info "instalando asur-lab desde $ASUR_LAB_URL ..."
  curl -fsSL --retry 3 --connect-timeout 10 "${ASUR_LAB_URL}/laboratorios/instalar-asur-lab.sh" | bash || {
    aviso "sin red: buscando respaldo local de asur-lab"; :; }
  export PATH="$HOME/.local/bin:$PATH"
fi
command -v asur-lab >/dev/null 2>&1 || {
  echo "No se pudo instalar asur-lab. Revisa tu conexión o copia asur-lab a ~/.local/bin/" >&2
  exit 1
}
exec asur-lab iniciar lab06
