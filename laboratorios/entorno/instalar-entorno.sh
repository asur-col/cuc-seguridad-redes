#!/usr/bin/env bash
# instalar-entorno.sh — Entorno gráfico liviano por navegador (noVNC) para ASUR
# Universidad de la Costa · Seguridad en Redes · 2026-2
#
# Uso:
#   curl -fsSL https://asur-col.github.io/cuc-seguridad-redes/laboratorios/entorno/instalar-entorno.sh | bash
#
# Idempotente: puede ejecutarse múltiples veces de forma segura.
# Requiere sudo (el estudiante ingresa su contraseña si no tiene sudo sin clave).

set -euo pipefail

# Colores de salida
VERDE='\033[32m'
ROJO='\033[31m'
AMAR='\033[33m'
CYAN='\033[36m'
APAGA='\033[0m'

ok()   { printf "${VERDE}[OK]${APAGA}   %s\n" "$*"; }
mal()  { printf "${ROJO}[ERROR]${APAGA} %s\n" "$*" >&2; }
info() { printf "${CYAN}[INFO]${APAGA}  %s\n" "$*"; }
aviso(){ printf "${AMAR}[AVISO]${APAGA} %s\n" "$*"; }

info "Iniciando instalación del entorno gráfico ASUR por navegador..."

# 0. Detección de usuario y permisos
REAL_USER="${SUDO_USER:-$USER}"
USER_HOME=$(eval echo "~$REAL_USER")

# Función para ejecutar con sudo si no somos root
SUDO=""
if [ "$(id -u)" -ne 0 ]; then
  if command -v sudo >/dev/null 2>&1; then
    SUDO="sudo"
    info "Se solicitarán permisos de sudo para configurar paquetes del sistema."
  else
    mal "Este instalador requiere permisos de administrador (sudo no encontrado)."
    exit 1
  fi
fi

# 1. Actualización e instalación de paquetes base y escritorio liviano (XFCE4)
info "1/7 Instalando XFCE4, TigerVNC, websockify y herramientas de red..."
$SUDO apt-get update -y
DEBIAN_FRONTEND=noninteractive $SUDO apt-get install -y --no-install-recommends \
  xfce4 xfce4-goodies dbus-x11 \
  tigervnc-standalone-server tigervnc-tools \
  websockify novnc netcat-openbsd \
  tcpdump tshark nmap wireshark-common mousepad \
  curl wget ca-certificates gnupg software-properties-common

# 2. Firefox nativo desde repositorio Mozilla (evita problemas de rendimiento snap en 3.8GB)
info "2/7 Configurando Firefox nativo (.deb)..."
if ! dpkg -s firefox 2>/dev/null | grep -q "mozillateam"; then
  $SUDO install -d -m 0755 /etc/apt/keyrings
  $SUDO add-apt-repository -y ppa:mozillateam/ppa || true
  cat << 'APTPREF' | $SUDO tee /etc/apt/preferences.d/mozilla-firefox >/dev/null
Package: *
Pin: release o=LP-PPA-mozillateam
Pin-Priority: 1001
APTPREF
  $SUDO apt-get update -y
  DEBIAN_FRONTEND=noninteractive $SUDO apt-get install -y --allow-downgrades firefox || true
fi

# 3. Docker: verificar o agregar usuario al grupo docker
info "3/7 Verificando Docker..."
if ! command -v docker >/dev/null 2>&1; then
  DEBIAN_FRONTEND=noninteractive $SUDO apt-get install -y docker.io docker-compose-v2
fi
$SUDO usermod -aG docker "$REAL_USER" || true

# Wireshark sin root
$SUDO usermod -aG wireshark "$REAL_USER" 2>/dev/null || true

# 4. Generar clave aleatoria por VM y configurar VNC
info "4/7 Configurando autenticación VNC (clave única aleatoria)..."
VNC_DIR="$USER_HOME/.vnc"
mkdir -p "$VNC_DIR"
chown "$REAL_USER:$REAL_USER" "$VNC_DIR"
chmod 700 "$VNC_DIR"

if [ ! -s "$VNC_DIR/clave.txt" ]; then
  # Generar clave aleatoria de 8 caracteres alfanuméricos
  VNC_PASS=$(openssl rand -hex 4)
  echo "$VNC_PASS" > "$VNC_DIR/clave.txt"
  chown "$REAL_USER:$REAL_USER" "$VNC_DIR/clave.txt"
  chmod 600 "$VNC_DIR/clave.txt"
else
  VNC_PASS=$(cat "$VNC_DIR/clave.txt" | tr -d '[:space:]')
fi

# Establecer la contraseña en formato TigerVNC
su - "$REAL_USER" -c "echo '$VNC_PASS' | vncpasswd -f > '$VNC_DIR/passwd'"
chmod 600 "$VNC_DIR/passwd"

# Script xstartup para sesión XFCE
cat << 'XEOF' > "$VNC_DIR/xstartup"
#!/bin/sh
unset SESSION_MANAGER
unset DBUS_SESSION_BUS_ADDRESS
[ -x /etc/vnc/xstartup ] && exec /etc/vnc/xstartup
[ -r $HOME/.Xresources ] && xrdb $HOME/.Xresources
exec dbus-launch --exit-with-session startxfce4
XEOF
chown "$REAL_USER:$REAL_USER" "$VNC_DIR/xstartup"
chmod 755 "$VNC_DIR/xstartup"

# 5. Servicio Web VNC (TigerVNC + websockify/noVNC en puerto 6080)
info "5/7 Configurando servicio web noVNC (puerto 6080)..."
cat << 'DESKSH' | $SUDO tee /usr/local/bin/asur-desktop.sh >/dev/null
#!/bin/bash
export USER=cuc
export HOME=/home/cuc
# Limpiar sesión previa si existe
vncserver -kill :1 >/dev/null 2>&1 || true
rm -rf /tmp/.X1-lock /tmp/.X11-unix/X1
# Iniciar Xvnc en display :1
vncserver :1 -geometry 1280x720 -depth 24 -localhost no -rfbauth /home/cuc/.vnc/passwd
# Esperar a que el puerto RFB esté escuchando
for i in $(seq 1 15); do
    nc -z 127.0.0.1 5901 && break
    sleep 0.5
done
# Iniciar websocket bridge
exec /usr/bin/websockify --web /usr/share/novnc 6080 127.0.0.1:5901
DESKSH
$SUDO chmod 755 /usr/local/bin/asur-desktop.sh

cat << 'SERV' | $SUDO tee /etc/systemd/system/asur-desktop.service >/dev/null
[Unit]
Description=ASUR Entorno de Escritorio Web (TigerVNC + noVNC)
After=network.target

[Service]
Type=simple
User=cuc
Group=cuc
WorkingDirectory=/home/cuc
ExecStart=/usr/local/bin/asur-desktop.sh
ExecStop=/usr/bin/vncserver -kill :1
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
SERV

$SUDO systemctl daemon-reload
$SUDO systemctl enable asur-desktop.service
$SUDO systemctl restart asur-desktop.service

# 6. Actualizador de /etc/issue (muestra IP y clave en consola virtual)
cat << 'ISSUESH' | $SUDO tee /usr/local/bin/asur-actualizar-issue.sh >/dev/null
#!/bin/bash
IP_ACTUAL=$(ip -4 -o addr show scope global | awk '{print $4}' | cut -d/ -f1 | grep -v '^172\.17\.' | grep -v '^172\.18\.' | head -n1 || echo "127.0.0.1")
CLAVE=$(cat /home/cuc/.vnc/clave.txt 2>/dev/null || echo "ver ~/.vnc/clave.txt")

cat << ISSUE_TXT > /etc/issue
\S{PRETTY_NAME} \n \l

========================================================================
  ASUR — ENTORNO DE LABORATORIO POR NAVEGADOR
========================================================================
  Acceso Web:  http://${IP_ACTUAL}:6080/vnc.html
  Clave VNC:   ${CLAVE}

  Respaldo SSH: ssh cuc@${IP_ACTUAL}
  (En modo NAT VirtualBox: http://127.0.0.1:6080 si hay reenvío de puertos)
========================================================================

ISSUE_TXT
ISSUESH
$SUDO chmod 755 /usr/local/bin/asur-actualizar-issue.sh
$SUDO /usr/local/bin/asur-actualizar-issue.sh

# Servicio para refrescar /etc/issue en cada arranque
cat << 'ISSUE_SERV' | $SUDO tee /etc/systemd/system/asur-issue.service >/dev/null
[Unit]
Description=Actualizar /etc/issue con IP y Clave ASUR
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/asur-actualizar-issue.sh
RemainAfterExit=true

[Install]
WantedBy=multi-user.target
ISSUE_SERV
$SUDO systemctl enable asur-issue.service || true

# 7. Cliente asur-lab, acceso directo en escritorio y temporizador autoactualización
info "6/7 Instalando cliente asur-lab y temporizador de autoactualización..."
ASUR_LAB_URL="${ASUR_LAB_URL:-https://asur-col.github.io/cuc-seguridad-redes}"
su - "$REAL_USER" -c "curl -fsSL ${ASUR_LAB_URL}/laboratorios/instalar-asur-lab.sh | bash" || true
$SUDO ln -sf "/home/$REAL_USER/.local/bin/asur-lab" /usr/local/bin/asur-lab

# Script de autoactualización asur-lab-sync.sh
cat << 'SYNCSH' | $SUDO tee /usr/local/bin/asur-lab-sync.sh >/dev/null
#!/bin/bash
# asur-lab-sync.sh — Sincronización y autoactualización periódica de asur-lab
export HOME="/home/cuc"
export PATH="$HOME/.local/bin:$PATH"
export DISPLAY=":1"

ASUR_LAB_URL="${ASUR_LAB_URL:-https://asur-col.github.io/cuc-seguridad-redes}"
CATALOGO_URL="${ASUR_LAB_URL}/laboratorios/catalogo.json"
CACHE_DIR="$HOME/.cache/asur-lab"
mkdir -p "$CACHE_DIR" "$HOME/.local/bin"

CAT_TMP=$(mktemp)
if ! curl -fsSL --connect-timeout 5 --max-time 10 "$CATALOGO_URL" -o "$CAT_TMP" 2>/dev/null; then
  rm -f "$CAT_TMP"
  exit 0
fi

if ! python3 -m json.tool "$CAT_TMP" >/dev/null 2>&1; then
  rm -f "$CAT_TMP"
  exit 0
fi

for act in "$HOME"/labs/*/.asur-lab-activo; do
  if [ -f "$act" ]; then
    rm -f "$CAT_TMP"
    exit 0
  fi
done

if [ -f "$CACHE_DIR/catalogo.json" ]; then
  python3 - "$CACHE_DIR/catalogo.json" "$CAT_TMP" << 'PY' 2>/dev/null
import json, sys, subprocess
try:
    old = {x['id']: x.get('titulo', x['id']) for x in json.load(open(sys.argv[1])) if x.get('estado') == 'activo'}
    new = {x['id']: x.get('titulo', x['id']) for x in json.load(open(sys.argv[2])) if x.get('estado') == 'activo'}
    agregados = set(new.keys()) - set(old.keys())
    for aid in agregados:
        titulo = new[aid]
        subprocess.run(["notify-send", "-u", "normal", "ASUR Lab — Nuevo Laboratorio",
                        f"Disponible: {titulo}\nEjecuta: asur-lab iniciar {aid}"],
                       env={"DISPLAY": ":1", "HOME": "/home/cuc"}, check=False)
except Exception:
    pass
PY
fi
cp "$CAT_TMP" "$CACHE_DIR/catalogo.json"

CLI_DEST="$HOME/.local/bin/asur-lab"
python3 - "$CAT_TMP" "$CLI_DEST" "$ASUR_LAB_URL" << 'PY'
import json, sys, subprocess, hashlib, os, shutil

cat_path, cli_path, base_url = sys.argv[1], sys.argv[2], sys.argv[3]
try:
    data = json.load(open(cat_path))
except Exception:
    sys.exit(0)

cli_entry = next((x for x in data if x.get("id") == "asur-lab"), None)
if not cli_entry:
    sys.exit(0)

version_remota = cli_entry.get("version", "")
sha_esperado = cli_entry.get("sha256", "").strip().lower()
rel_url = cli_entry.get("url", "/laboratorios/asur-lab")
url_descarga = base_url.rstrip("/") + ("" if rel_url.startswith("/") else "/") + rel_url

if not (url_descarga.startswith("https://") or url_descarga.startswith("http://127.0.0.1") or url_descarga.startswith("http://localhost") or url_descarga.startswith("http://172.") or url_descarga.startswith("http://10.") or url_descarga.startswith("http://200.30.")):
    sys.exit(0)

tmp_cli = cli_path + ".new"
try:
    res = subprocess.run(["curl", "-fsSL", "--connect-timeout", "5", "--max-time", "15", url_descarga, "-o", tmp_cli], check=True)
except Exception:
    sys.exit(0)

h = hashlib.sha256()
with open(tmp_cli, "rb") as f:
    h.update(f.read())
sha_real = h.hexdigest().lower()

if sha_esperado and sha_real != sha_esperado:
    if os.path.exists(tmp_cli): os.remove(tmp_cli)
    sys.exit(1)

if os.path.isfile(cli_path):
    h_inst = hashlib.sha256()
    with open(cli_path, "rb") as f:
        h_inst.update(f.read())
    if h_inst.hexdigest().lower() == sha_real:
        if os.path.exists(tmp_cli): os.remove(tmp_cli)
        sys.exit(0)

if os.path.isfile(cli_path):
    shutil.copy2(cli_path, cli_path + ".prev")

os.chmod(tmp_cli, 0o755)
os.replace(tmp_cli, cli_path)

subprocess.run(["notify-send", "-u", "normal", "ASUR Lab — Actualización",
                f"Cliente asur-lab actualizado a v{version_remota}"],
               env={"DISPLAY": ":1", "HOME": "/home/cuc"}, check=False)
PY
RC=$?
rm -f "$CAT_TMP"
exit $RC
SYNCSH
$SUDO chmod 755 /usr/local/bin/asur-lab-sync.sh

cat << 'SYNCSERV' | $SUDO tee /etc/systemd/system/asur-lab-sync.service >/dev/null
[Unit]
Description=Sincronizacion periodica de laboratorios ASUR
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User=cuc
Group=cuc
Environment=HOME=/home/cuc
Environment=PATH=/home/cuc/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ExecStart=/usr/local/bin/asur-lab-sync.sh
SYNCSERV

cat << 'SYNCTIMER' | $SUDO tee /etc/systemd/system/asur-lab-sync.timer >/dev/null
[Unit]
Description=Temporizador de autoactualizacion de asur-lab (al arrancar y cada 30 min)

[Timer]
OnBootSec=1min
OnUnitActiveSec=30min
RandomizedDelaySec=60
Persistent=true

[Install]
WantedBy=timers.target
SYNCTIMER

$SUDO systemctl daemon-reload
$SUDO systemctl enable --now asur-lab-sync.timer

# Acceso directo en escritorio
info "7/7 Creando acceso directo en el escritorio..."
DESK_DIR="$USER_HOME/Desktop"
mkdir -p "$DESK_DIR"
cat << 'DSK' > "$DESK_DIR/Laboratorios.desktop"
[Desktop Entry]
Version=1.0
Type=Application
Name=Laboratorios ASUR
Comment=Gestor de Laboratorios Seguridad en Redes
Exec=xfce4-terminal --title="Laboratorios ASUR" --working-directory=/home/cuc -e "bash -c 'asur-lab lista; echo; echo \"Comandos: asur-lab iniciar <id> | ./lab check | ./lab estado\"; exec bash'"
Icon=utilities-terminal
Path=/home/cuc
Terminal=false
StartupNotify=true
Categories=Education;Development;
DSK
chmod 755 "$DESK_DIR/Laboratorios.desktop"
chown "$REAL_USER:$REAL_USER" "$DESK_DIR/Laboratorios.desktop"

ok "Instalación completada con éxito."
echo
IP_SHOW=$(ip -4 -o addr show scope global | awk '{print $4}' | cut -d/ -f1 | grep -v '^172\.17\.' | grep -v '^172\.18\.' | head -n1 || echo "127.0.0.1")
info "Acceda desde el navegador en su equipo anfitrión a:"
echo "   http://${IP_SHOW}:6080/vnc.html"
echo "   Contraseña: (ver $VNC_DIR/clave.txt o en la pantalla de inicio de sesión de la VM)"
