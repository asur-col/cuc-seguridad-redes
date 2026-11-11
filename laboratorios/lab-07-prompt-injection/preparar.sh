#!/usr/bin/env bash
# preparar.sh — deja lista la VM del curso para el Lab 9 (prompt injection)
# Universidad de la Costa · Seguridad en Redes · 2026-2
#
# Uso (en la terminal de la VM):
#   curl -fsSL https://asur-col.github.io/cuc-seguridad-redes/laboratorios/lab-07-prompt-injection/preparar.sh | bash
# Opcional, para volver a permitir SSH con contraseña (pide la clave de sudo):
#   curl -fsSL .../preparar.sh | bash -s -- --ssh

set -u
SITIO="https://asur-col.github.io/cuc-seguridad-redes"
LOCAL="http://127.0.0.1:8088"
ok()   { printf '\033[32m[OK]\033[0m    %s\n' "$*"; }
info() { printf '\033[36m[INFO]\033[0m  %s\n' "$*"; }
mal()  { printf '\033[31m[ERROR]\033[0m %s\n' "$*" >&2; }

# 1. Variables fijas en la terminal y en las próximas
export PATH="$HOME/.local/bin:$HOME/.opencode/bin:$PATH"
export ASUR_LAB_URL="$LOCAL"
grep -q 'ASUR_LAB_URL=' "$HOME/.bashrc" 2>/dev/null || \
  echo 'export PATH=$HOME/.local/bin:$HOME/.opencode/bin:$PATH; export ASUR_LAB_URL=http://127.0.0.1:8088' >> "$HOME/.bashrc"
ok "PATH y ASUR_LAB_URL configurados (también en ~/.bashrc)"

# 2. SSH con contraseña (solo si se pide)
if [ "${1:-}" = "--ssh" ]; then
  info "habilitando SSH con contraseña (pide la clave de sudo)"
  sudo rm -f /etc/ssh/sshd_config.d/10-a3.conf /etc/sudoers.d/90-operador </dev/null
  sudo sshd -t </dev/null && sudo systemctl restart ssh </dev/null
  if sudo sshd -T </dev/null | grep -q '^passwordauthentication yes'; then
    ok "SSH: passwordauthentication yes (ya puedes entrar con usuario y clave)"
  else
    mal "SSH sigue sin contraseña: revisa /etc/ssh/sshd_config.d/"
  fi
fi

# 3. OpenCode
command -v opencode >/dev/null 2>&1 || { info "instalando OpenCode..."; I=$(mktemp); curl -fsSL https://opencode.ai/install -o "$I" && bash "$I" </dev/null >/dev/null 2>&1; rm -f "$I"; export PATH="$HOME/.opencode/bin:$PATH"; }
command -v opencode >/dev/null 2>&1 && ok "OpenCode $(opencode --version 2>/dev/null)" || mal "no pude instalar OpenCode (revisa internet)"

# 4. Catálogo local y cliente asur-lab
if curl -fsS --max-time 5 "$LOCAL/laboratorios/catalogo.json" 2>/dev/null | grep -q '"lab09"'; then
  asur-lab actualizar </dev/null >/dev/null 2>&1 && ok "asur-lab actualizado" || info "asur-lab ya estaba al día"
  asur-lab iniciar lab09 </dev/null && ok "lab09 instalado desde el catálogo de la VM"
else
  info "el catálogo de la VM no trae lab09: lo descargo del sitio del curso"
  T=$(mktemp -d)
  curl -fsSL "$SITIO/laboratorios/lab-07-prompt-injection/paquete/paquete.tar.gz" -o "$T/p.tgz" \
   && curl -fsSL "$SITIO/laboratorios/lab-07-prompt-injection/paquete/paquete.tar.gz.sha256" -o "$T/p.sha" \
   && [ "$(sha256sum "$T/p.tgz" | cut -d' ' -f1)" = "$(cut -d' ' -f1 "$T/p.sha")" ] \
   || { mal "no pude descargar o verificar el paquete"; exit 1; }
  rm -rf "$HOME/labs/lab09" && mkdir -p "$HOME/labs/lab09" && tar xzf "$T/p.tgz" -C "$HOME/labs/lab09" && rm -rf "$T"
  ok "lab09 instalado en ~/labs/lab09 (sin «asur-lab check»: avisa al docente)"
fi

echo
ok "Listo. Ahora:"
echo "   cd ~/labs/lab09"
echo "   export NVIDIA_API_KEY=tu_clave_personal      # gratis en https://build.nvidia.com"
echo "   ./asistente \"¿Cuál es el horario de la sede Centro?\""
