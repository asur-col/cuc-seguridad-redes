
# Laboratorio 1: Segmentación de Redes y Zero Trust

> **Unidad 1 · Actividad 1 · 10% de la nota final · Seguridad en Redes (CUC)**
> Versión ilustrada (con diagramas de referencia) disponible en [`index.html`](index.html) de esta misma carpeta. Este documento es la versión Markdown para lectura, copia de comandos y control de versiones.

VirtualBox + OPNsense + Alpine Linux: tres zonas de servicio aisladas, una zona de administración con escritorio gráfico, NAT de salida, una aplicación web real con su base de datos protegida, y publicación controlada del servicio por NAT/PAT

En las semanas anteriores trabajaste segmentación de forma simulada en un sandbox online. Esta vez vas a construir una infraestructura **real**: un firewall OPNsense como único punto de control entre cuatro zonas, salida a Internet por NAT, una aplicación web en la DMZ conectada a una base de datos blindada en la red interna, y la publicación del servicio hacia la red WAN mediante NAT/PAT (port forwarding) — todo bajo el principio Zero Trust: **todo bloqueado por defecto, solo se permite lo estrictamente necesario.**

Trabajarás desde una **máquina de administración con escritorio gráfico** (zona de administración), desde donde gestionarás el firewall por HTTPS y los servidores por SSH — con copiar y pegar funcionando, como en un puesto de trabajo real. El resultado final es la misma arquitectura que encontrarás en una empresa: los usuarios solo ven la aplicación web, la aplicación solo puede hablar con la base de datos por el puerto MySQL, la base de datos es invisible para todos los demás, y desde la red externa (WAN) solo entra tráfico web al puerto publicado — nada más. Todos los procedimientos están alineados con la documentación oficial de [OPNsense](https://docs.opnsense.org/), el [manual de VirtualBox](https://www.virtualbox.org/manual/) y el [handbook de Alpine Linux](https://docs.alpinelinux.org/) (enlaces en la sección de Referencias), e incluyen imágenes de referencia tomadas de esa documentación oficial.

## Subredes del Laboratorio (cómo se calculan)

Esta sección es de referencia: **no es un ejercicio que debas resolver ni entregar**. Aquí se explica cómo se obtienen las 4 subredes que usarás en todo el laboratorio, para que entiendas de dónde salen los números que vas a configurar.

El bloque base es `10.20.0.0/22`. La lógica es la siguiente:

1. Un prefijo `/22` equivale a la máscara `255.255.252.0`. Los primeros 22 bits son fijos; quedan 10 bits libres para hosts: 2^10 = 1024 direcciones, desde `10.20.0.0` hasta `10.20.3.255`.
2. Para crear 4 zonas del mismo tamaño se subdivide en `/24` (máscara `255.255.255.0`): cada una tiene 2^8 = 256 direcciones. Como 4 × 256 = 1024, el bloque se usa completo sin desperdicio ni solapamiento.
3. En cada `/24`: la primera dirección (`.0`) es la **dirección de red**, la última (`.255`) es el **broadcast**, y las 254 intermedias (`.1 – .254`) son hosts utilizables. Al firewall le asignamos la primera utilizable (`.1`) como gateway de cada zona.

Estas son las 4 subredes resultantes — **usa exactamente estas direcciones en todas las partes del laboratorio**:

| Zona Funcional | Subred CIDR | Rango de Hosts Útiles | Broadcast | Gateway (OPNsense) |
|---|---|---|---|---|
| Red de Usuarios | 10.20.0.0/24 | 10.20.0.1 – 10.20.0.254 | 10.20.0.255 | 10.20.0.1 |
| Red Interna (Base de datos) | 10.20.1.0/24 | 10.20.1.1 – 10.20.1.254 | 10.20.1.255 | 10.20.1.1 |
| DMZ (Servidor web) | 10.20.2.0/24 | 10.20.2.1 – 10.20.2.254 | 10.20.2.255 | 10.20.2.1 |
| Red de Administración | 10.20.3.0/24 | 10.20.3.1 – 10.20.3.254 | 10.20.3.255 | 10.20.3.1 |

## Instalación y Montaje (paso a paso)

### B.0 — Verificación de requisitos del equipo

1. **Virtualización habilitada en BIOS/UEFI:** apaga el equipo, enciéndelo y presiona repetidamente la tecla del setup (`F2`, `F10`, `Del` o `Esc` según el fabricante). Busca en las pestañas *Advanced*, *CPU Configuration* o *Security* la opción **Intel VT-x** / **Intel Virtualization Technology** (equipos Intel) o **AMD-V** / **SVM Mode** (equipos AMD) y déjala en **Enabled**. Guarda con `F10` y reinicia.
2. **RAM:** mínimo **8 GB totales** en tu equipo. Presupuesto del laboratorio: OPNsense (1 GB) + estación de administración con GUI (1.5 GB) + 3 VMs Alpine (512 MB c/u = 1.5 GB) ≈ **4 GB de VMs** + tu sistema operativo. Si tienes exactamente 8 GB, cierra navegadores e IDEs pesados mientras trabajas.
3. **Disco:** al menos 35 GB libres (OPNsense ~8 GB, cada Alpine ~2 GB, la imagen de la estación de administración ~8 GB, ISOs ~1.5 GB).
4. **Windows + Hyper-V:** si tienes Hyper-V, WSL2 o "Seguridad basada en virtualización" activos, chocan con VirtualBox (las VMs no arrancan o van extremadamente lentas). Verifica en PowerShell **como administrador** (clic derecho en el menú Inicio → *Terminal (Administrador)*):
            `Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V-All`
            Si el `State` aparece como `Enabled` y tus VMs fallan:
            `Disable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V-All`
            y reinicia. (Si usas WSL2 en otras materias, reactívalo después del lab con el comando inverso `Enable-WindowsOptionalFeature`.)

### B.1 — Instalación de VirtualBox

Referencia oficial: [VirtualBox Manual, Cap. 1 — First Steps](https://www.virtualbox.org/manual/ch01.html)

1. Abre tu navegador y ve a `virtualbox.org/wiki/Downloads`. Descarga el paquete de plataforma según tu sistema:
            **Windows:** "Windows hosts" → obtienes un `.exe`. Ejecútalo con clic derecho → *Ejecutar como administrador*. Durante la instalación, Windows preguntará varias veces si deseas instalar "software de dispositivo" de Oracle (son los adaptadores de red virtual): acepta todos. Si Windows advierte que la red se desconectará un momento, es normal.
**macOS (Intel):** "macOS / Intel hosts" → abre el `.dmg` descargado y haz doble clic en `VirtualBox.pkg`. Si macOS bloquea la instalación, ve a *Ajustes del Sistema → Privacidad y Seguridad* y pulsa "Permitir" junto al mensaje sobre software de Oracle; luego reinicia el Mac.
**macOS (Apple Silicon M1/M2/M3):** descarga la versión "ARM64" de VirtualBox 7.x. OPNsense y Alpine tienen imágenes ARM64. Si algo no funciona en ARM, avisa al docente el primer día.
**Linux (Debian/Ubuntu):** `sudo apt update && sudo apt install virtualbox`. En Fedora: `sudo dnf install VirtualBox`. En openSUSE: `sudo zypper install virtualbox`.
2. Abre VirtualBox. Debes ver la ventana del **VirtualBox Manager** vacía, sin mensajes de error en la parte inferior. Según el manual oficial, esta ventana tiene dos paneles: la lista de máquinas a la izquierda y el panel de detalles a la derecha, con los botones **Nueva**, **Configuración** e **Iniciar** en la barra superior — los usarás en toda esta parte.

*(Ver diagrama en la versión HTML: Referencia oficial: VirtualBox Manager, la ventana principal desde donde crearás y configurarás todas las VMs. Fuente: [Manual de VirtualBox, Cap. 1](https://www.virtualbox.org/manual/ch01.html))*

### B.2 — Creación e instalación de la VM OPNsense

Referencias oficiales: [OPNsense — Initial Installation & Configuration](https://docs.opnsense.org/manual/install.html) · [OPNsense — Virtual & Cloud-Based Installation](https://docs.opnsense.org/manual/virtuals.html)

1. Ve a `opnsense.org/download`. Selecciona: arquitectura **amd64**, tipo de imagen **dvd** (según la tabla oficial de tipos de imagen: *imagen ISO que arranca en un entorno en vivo en modo VGA con soporte UEFI*), y el mirror más cercano a Colombia. El archivo descargado termina en `.bz2`: debes descomprimirlo para obtener el `.iso`.
            **Windows:** usa 7-Zip (gratis, `7-zip.org`) → clic derecho sobre el archivo → *7-Zip → Extraer aquí*.
**macOS:** doble clic sobre el `.bz2` (el sistema lo descomprime solo) o `bunzip2 archivo.bz2` en Terminal.
**Linux:** `bunzip2 opnsense-*.bz2`.
2. **(Buena práctica, opcional) Verifica la integridad de la imagen** como indica la documentación oficial: descarga también el archivo `.sha256` del mismo mirror y compara el hash:
            `openssl sha256 OPNsense-*-dvd-amd64.iso`
            La salida debe coincidir con el valor publicado para esa imagen. Si no coincide, vuelve a descargarla.
3. En VirtualBox pulsa **Nueva**. En el asistente *Create Virtual Machine*: Nombre `OPNsense` → Carpeta: la que propone por defecto → en **ISO Image** selecciona la ISO de OPNsense (el asistente la montará automáticamente en la unidad DVD de la VM) → Tipo **BSD** → Versión **FreeBSD (64-bit)**. Si el asistente ofrece "unattended installation", marca **Skip Unattended Installation** — la instalación de OPNsense se hace manualmente desde su consola. Pulsa **Siguiente**.
4. Memoria base: **1024 MB (1 GB)** — suficiente para este laboratorio porque el firewall solo enrutará y filtrará unas pocas VMs (sin IDS/IPS ni proxies pesados). Procesadores: **1–2**. Pulsa **Siguiente**.
            
Nota: la documentación oficial recomienda 3 GB como mínimo general para VMs; si el instalador llegara a fallar con el error conocido *"File copy failed during installation"* (problema documentado por falta de memoria), apaga la VM, súbela a 2048 MB y reintenta.
5. Disco duro: "Crear un disco duro virtual ahora" → tamaño **16 GB** (el mínimo recomendado oficialmente es 8 GB), sin marcar "Pre-Allocate Full Size" (asignación dinámica). Pulsa **Siguiente** y **Finalizar**.
6. Con la VM seleccionada, pulsa **Configuración** → sección **Red**. Configura los **5 adaptadores** (cada uno en su pestaña):
            **Adaptador 1 (WAN):** marca "Habilitar adaptador de red" → en "Conectado a:" elige **Adaptador puente** → en "Nombre:" selecciona tu tarjeta de red física activa (la que tiene Internet: tu Wi-Fi o tu Ethernet). Este adaptador recibirá una IP por DHCP de tu red real.
**Adaptador 2 (LAN):** habilítalo → "Conectado a:" **Red interna** → en "Nombre:" escribe exactamente `red-usuarios`.
**Adaptador 3 (OPT1):** habilítalo → "Red interna" → nombre exacto `red-interna`.
**Adaptador 4 (OPT2):** habilítalo → "Red interna" → nombre exacto `red-dmz`.
**Adaptador 5 (OPT3):** habilítalo → "Red interna" → nombre exacto `red-admin`. Esta es la **zona de administración**: por aquí gestionarás el firewall, sin exponer la WAN.
            Los nombres de las redes internas son sensibles a mayúsculas: escríbelos tal cual, porque las VMs cliente deben usar los mismos nombres para quedar conectadas al mismo "switch virtual".
7. Arranca la VM (botón **Iniciar**). El sistema arranca en el **entorno en vivo** (live environment): verás texto desplazándose durante 1–2 minutos. Cuando aparezca el prompt `login:` inicia sesión con usuario `installer` y contraseña `opnsense` — según la documentación oficial, este es el usuario que invoca el instalador (si entraras como `root`, con la misma contraseña `opnsense`, solo abrirías el sistema en vivo sin instalar nada).
8. El instalador te guía por estas pantallas (secuencia oficial):
            **Keymap selection:** acepta el mapa por defecto con Enter (o busca "Latin American" si prefieres).
**Install (UFS|ZFS):** elige **UFS**. (La documentación señala que ZFS es la opción más robusta, pero exige más capacidad y memoria; para este laboratorio UFS es suficiente y más liviano.)
**Disk Selection:** selecciona el disco virtual (`ada0` o `vtbd0`, será el único de ~16 GB).
**Last Chance!:** confirma con **Yes** — se formateará el disco virtual (está vacío, no pierdes nada).
**Continue with recommended swap (UFS):** acepta con **Yes**.
**Root Password:** define y confirma una contraseña de root que recuerdes — será también la de la interfaz web.
**Complete Install:** al seleccionarlo, el instalador termina y reinicia la máquina.
9. **Importante:** mientras la VM se apaga para reiniciar, ve al menú de la ventana de VirtualBox: *Dispositivos → Unidades ópticas → Eliminar disco de la unidad virtual*. Si no lo haces, la VM volverá a arrancar el instalador.

*(Ver diagrama en la versión HTML: Referencia oficial: gestor de arranque (bootloader) de OPNsense al iniciar desde la imagen de instalación. Fuente: [documentación de OPNsense](https://docs.opnsense.org/manual/how-tos/serial_access.html))*

*(Ver diagrama en la versión HTML: Referencia oficial: ventana de configuración de almacenamiento de una VM — aquí es donde se monta la ISO en la unidad óptica virtual. Fuente: [Manual de VirtualBox](https://www.virtualbox.org/manual/))*

### B.3 — Asignación de interfaces y direcciones IP en OPNsense

Referencia oficial: [OPNsense — Initial Configuration (menú de consola)](https://docs.opnsense.org/manual/install.html)

Tras el reinicio, la consola mostrará el mensaje de bienvenida y el menú de 14 opciones. Esto es **exactamente** lo que verás al final de esta sección (texto basado en la documentación oficial):

```
*** Welcome to OPNsense 25.x (amd64) on OPNsense ***

 WAN  (em0) -> v4/DHCP4: 192.168.1.50/24
 LAN  (em1) -> v4: 10.20.0.1/24
 OPT1 (em2) -> v4: 10.20.1.1/24
 OPT2 (em3) -> v4: 10.20.2.1/24
 OPT3 (em4) -> v4: 10.20.3.1/24

 0) Logout                         7) Ping host
 1) Assign interfaces              8) Shell
 2) Set interface(s) IP address    9) pfTop
 3) Reset the root password       10) Filter logs
 4) Reset to factory defaults     11) Restart web interface
 5) Reboot system                 12) Upgrade from console
 6) Halt system                   13) Restore a configuration
```

*Ejemplo ilustrativo basado en el menú de consola documentado oficialmente — tu IP de WAN y la versión variarán.*

1. Inicia sesión en la consola con usuario `root` y la contraseña que definiste en la instalación. Selecciona **1) Assign interfaces** escribiendo `1` y Enter.
2. Cuando pregunte *"Do you want to configure VLANs now?"* escribe `n` y Enter (la documentación oficial confirma que las VLANs son opcionales y se pueden configurar después; aquí usamos adaptadores virtuales separados).
3. Te pedirá el nombre de cada interfaz. Los nombres disponibles serán algo como `em0 em1 em2 em3 em4` (o `vtnet0..vtnet4`). Asigna en este orden:
            **WAN:** `em0` — corresponde al Adaptador 1 (puente).
**LAN:** `em1` — Adaptador 2 (red-usuarios).
**Optional 1 (OPT1):** `em2` — Adaptador 3 (red-interna).
**Optional 2 (OPT2):** `em3` — Adaptador 4 (red-dmz).
**Optional 3 (OPT3):** `em4` — Adaptador 5 (red-admin).
            Cuando pregunte *"Do you want to proceed?"* responde `y`. La consola recargará y mostrará las 5 interfaces. La WAN debería mostrar una IP de tu red real (por ejemplo `192.168.1.50`) — si la WAN no tiene IP, revisa que el Adaptador 1 esté en modo puente sobre la tarjeta correcta.
4. Selecciona **2) Set interface(s) IP address** → escribe el número de **LAN** y responde así:
            
```
Enter the new LAN IPv4 address: 10.20.0.1
Enter the new LAN IPv4 subnet bit count: 24
Enter the new LAN IPv4 upstream gateway address: (presiona Enter — none)
Do you want to configure IPv6: n
Do you want to enable the DHCP server on LAN: n
Do you want to revert to HTTP as the webConfigurator protocol: n
```
5. Repite la opción 2 para las demás interfaces internas, siempre sin gateway, sin IPv6 y sin DHCP:
            **OPT1:** `10.20.1.1` / 24
**OPT2:** `10.20.2.1` / 24
**OPT3:** `10.20.3.1` / 24
6. Verificación: selecciona **8) Shell**, ejecuta `ifconfig | grep "inet "` y confirma que ves las 4 IPs internas (`10.20.0.1`, `10.20.1.1`, `10.20.2.1`, `10.20.3.1`) en interfaces distintas. Escribe `exit` para volver al menú.

### B.4 — Estación de administración con escritorio gráfico (imagen OSBoxes)

En lugar de exponer la administración del firewall hacia la WAN, vas a trabajar como en una empresa real: desde una **estación de administración** dentro de una zona dedicada (`red-admin`). Esta VM tiene escritorio gráfico y navegador, y además resuelve un problema práctico importante: **la consola cruda de VirtualBox no permite copiar y pegar** — desde esta VM podrás pegar comandos por SSH a los servidores Alpine y copiar archivos con `scp`.

Para no instalar un sistema desde cero, usarás una **imagen VDI pre-construida de OSBoxes** (imágenes oficiales listas para VirtualBox):

1. Ve a `osboxes.org` → sección **Lubuntu** (escritorio LXQt, muy liviano; como alternativa equivalente sirve **Xubuntu** o **MX Linux**) → descarga la imagen para **VirtualBox (VDI, 64-bit)** de la versión más reciente. El archivo viene comprimido (`.7z` o `.zip`): extráelo hasta obtener el `.vdi` (~4–8 GB).
2. En VirtualBox pulsa **Nueva**: Nombre `admin-gui` → Tipo **Linux** → Versión **Ubuntu (64-bit)** → **Siguiente**.
3. Memoria: **1536 MB (1.5 GB)**. Procesadores: **2**. **Siguiente**.
4. En la pantalla de disco duro elige **"Usar un archivo de disco duro virtual existente"** → pulsa el ícono de carpeta → **Añadir** → selecciona el `.vdi` que extrajiste → **Elegir** → **Finalizar**. (No instales nada: el sistema ya viene instalado en la imagen.)
5. Con la VM seleccionada, entra a **Configuración**:
            **General → Avanzado:** pon **Portapapeles compartido** en **Bidireccional** y **Arrastrar y soltar** en **Bidireccional** — así podrás copiar comandos desde esta guía en tu equipo y pegarlos dentro de la VM.
**Pantalla:** sube la memoria de vídeo a **64 MB**.
**Red → Adaptador 1:** habilítalo → "Conectado a:" **Red interna** → Nombre exacto `red-admin`.
6. Arranca la VM. Inicia sesión con las credenciales por defecto de OSBoxes: usuario `osboxes`, contraseña `osboxes.org`. (Para tareas de administrador usa `sudo` en la terminal; la contraseña es la misma.)
7. Configura la IP estática desde la interfaz gráfica: clic en el ícono de red de la barra inferior (o superior, según el escritorio) → *Edit Connections* (o "Configuración de red") → selecciona la conexión cableada → pestaña **IPv4** → Método **Manual** → **Add** y escribe: Address `10.20.3.10`, Netmask `24`, Gateway `10.20.3.1` → en DNS escribe `10.20.3.1` → **Save**. Desconecta y reconecta la red (clic en el ícono → desactivar/activar la conexión) para aplicar.
8. Verifica desde una terminal dentro de la VM (menú de aplicaciones → *Terminal*):
            
```
ip addr show | grep 10.20.3.10
ping -c 3 10.20.3.1
```

            Debes ver tu IP y recibir respuestas del firewall (el ping al gateway funciona incluso sin reglas nuevas porque la interfaz OPT3 responde a su propia red).
9. **Prueba el portapapeles compartido:** copia un texto cualquiera en tu equipo anfitrión y pégalo en la terminal de la VM. Si no funciona, las Guest Additions no están activas: no te detengas — podrás instalarlas al final de la Parte C con `sudo apt update && sudo apt install virtualbox-guest-utils virtualbox-guest-x11` y reiniciando la VM (mientras tanto, el trabajo por SSH desde esta VM no depende del portapapeles).

*(Ver diagrama en la versión HTML: Referencia oficial: una VM con sistema operativo de escritorio corriendo dentro de VirtualBox — así se verá tu estación de administración. Fuente: [Manual de VirtualBox](https://www.virtualbox.org/manual/))*

### B.5 — Acceso a la interfaz web de OPNsense (sin exponer la WAN)

La interfaz web de OPNsense escucha en todas las interfaces, pero el firewall solo permite entrar por LAN por defecto — y tu estación de administración está en OPT3. El orden correcto y seguro es: **primero crear la regla de administración, y solo después reactivar el firewall**, verificando que nunca te bloqueas a ti mismo. Este es el flujo completo:

1. En la consola de OPNsense selecciona **8) Shell** y pausa temporalmente el firewall:
            `pfctl -d`
            (Como advierte la documentación oficial de NAT, desactivar `pf` también desactiva el NAT — es solo por un momento, mientras creas la regla.)
2. En la VM `admin-gui`, abre el navegador (Firefox o el que incluya el escritorio) y ve a `https://10.20.3.1`. Acepta la advertencia de certificado autofirmado (*Avanzado → Aceptar el riesgo y continuar*). Entra con `root` y tu contraseña.
3. Completa el asistente inicial (*System → Wizard*): hostname `fw-lab`, dominio `lab.local`, DNS primario `1.1.1.1` y secundario `9.9.9.9`, zona horaria **America/Bogota**. En la pantalla de la WAN **desmarca "Block private networks and loopback addresses"**: no la necesitas para administrar (la gestión entra por OPT3), pero en la Parte E publicarás un servicio hacia tu red física — que es privada RFC1918 — y con esa casilla marcada el port forward no respondería. Finaliza el wizard.
4. **Crea la regla de administración ahora, antes de reactivar el firewall:** **Firewall → Rules → OPT3** → **Add**:
            **Action:** Pass · **Interface:** OPT3 · **TCP/IP Version:** IPv4 · **Protocol:** TCP
**Source:** OPT3 net
**Destination:** This firewall
**Destination port range:** HTTPS (443)
**Description:** `Admin web UI desde red-admin`
**Save** → **Apply changes**.
5. Aprovecha para renombrar las interfaces y que todo sea legible: **Interfaces → [OPT1]** → Description `INTERNA` → Save; **Interfaces → [OPT2]** → `DMZ` → Save; **Interfaces → [OPT3]** → `ADMIN` → Save. Desde ahora los menús mostrarán esos nombres.
6. Vuelve a la consola de OPNsense (opción 8) y **reactiva el firewall**:
            `pfctl -e`
7. **Verificación obligatoria:** recarga `https://10.20.3.1` en el navegador de admin-gui. Debe seguir cargando con el firewall activo. Si no carga, no entres en pánico: vuelve a la consola, `pfctl -d`, revisa la regla (¿Source = OPT3 net? ¿Destination = This firewall? ¿puerto 443? ¿Apply changes?), corrige y repite desde el paso 6.
8. **Ajuste recomendado para VMs (documentación oficial):** ve a **Interfaces → Settings** y marca las casillas para deshabilitar *hardware checksum offloading*, *hardware TCP segmentation offloading* y *hardware large receive offload*. La documentación de instalación virtual de OPNsense recomienda desactivar estos off-loadings en hipervisores. Guarda y aplica.
9. **Actualiza el sistema (buena práctica documentada):** la documentación oficial indica que las imágenes se publican con los releases de enero y julio, y recomienda actualizar después de instalar. Ve a **System → Firmware → Updates**, pulsa **Check for updates** y aplica lo que aparezca. Como tu WAN tiene salida a Internet por DHCP, la actualización funcionará directamente.

*(Ver diagrama en la versión HTML: Referencia oficial: pantalla *System → Firmware → Updates* de OPNsense, donde aplicarás las actualizaciones posteriores a la instalación. Fuente: [documentación de OPNsense](https://docs.opnsense.org/manual/install.html))*

### B.6 — Creación e instalación de las 3 VMs Alpine Linux

Referencias oficiales: [VirtualBox Manual, Cap. 1 — Create Virtual Machine wizard](https://www.virtualbox.org/manual/ch01.html) · [Alpine Linux Handbook — setup-alpine](https://docs.alpinelinux.org/user-handbook/0.1a/Installing/setup_alpine.html)

Vas a crear tres máquinas virtuales ligeras, una por cada zona de servicio:

| VM | Red interna (VirtualBox) | IP estática | Gateway | DNS | Rol final |
|---|---|---|---|---|---|
| cliente-usuarios | red-usuarios | 10.20.0.10/24 | 10.20.0.1 | 10.20.0.1 | Cliente que navega la app web |
| srv-db | red-interna | 10.20.1.10/24 | 10.20.1.1 | 10.20.1.1 | Servidor MariaDB (base de datos) |
| srv-web | red-dmz | 10.20.2.10/24 | 10.20.2.1 | 10.20.2.1 | Servidor nginx + PHP (aplicación) |

1. Ve a `alpinelinux.org/downloads` y descarga la imagen **Standard** para arquitectura **x86_64** (~200 MB; es un `.iso`, no necesita descompresión).
2. En VirtualBox pulsa **Nueva**: Nombre `cliente-usuarios` → en **ISO Image** selecciona la ISO de Alpine → Tipo **Linux** → Versión **Other Linux (64-bit)** → marca **Skip Unattended Installation** si aparece → **Siguiente**.
3. Memoria: **512 MB**. Procesadores: **1**. Disco: **2 GB** sin pre-asignación completa. Pulsa **Siguiente** y **Finalizar**.
4. Entra a **Configuración → Red → Adaptador 1**: habilítalo, "Conectado a:" **Red interna**, Nombre exacto `red-usuarios`. Arranca la VM.
5. Cuando aparezca `localhost login:` escribe `root` (Alpine en vivo no pide contraseña). Luego ejecuta:
            `setup-alpine`
6. Responde el asistente exactamente así (el handbook oficial de Alpine describe este mismo flujo):
            **Select keyboard layout:** escribe `es` → **Select variant:** escribe `es`.
**Enter system hostname:** `cliente-usuarios`.
**Which one do you want to initialize? (eth0):** presiona Enter (acepta eth0).
**Ip address for eth0? (dhcp):** escribe `10.20.0.10` (¡escribe la IP, no aceptes dhcp!).
**Netmask:** `255.255.255.0`.
**Gateway:** `10.20.0.1`.
**Do you want to do any manual network configuration?:** `n`.
**DNS domain name:** presiona Enter (vacío). **DNS nameserver(s):** `10.20.0.1`.
**New password for root:** escribe una contraseña de laboratorio dos veces (no se ve mientras escribes, es normal).
**Which timezone?:** `America/Bogota`.
**HTTP/FTP proxy URL:** Enter (ninguno).
**Enter mirror number or URL:** como aún no has configurado NAT (Parte C), la detección de mirror puede fallar — no pasa nada: elige `none` si lo ofrece, o deja que falle y continúa. Lo arreglarás en la Parte C ejecutando `setup-apkrepos`.
**Which SSH server?:** `openssh` ← **importante**: esto te permitirá administrar cada VM por SSH desde la estación admin-gui (copiar y pegar incluido), en lugar de teclear todo en la consola cruda de VirtualBox.
**Which disk(s) would you like to use?:** `sda`.
**How would you like to use it?:** `sys`.
**Erase the above disk and continue? (y/n):** `y`. Espera a que copie el sistema (~1 minuto).
7. Cuando vuelva el prompt, ejecuta `poweroff`. Desmonta la ISO de Alpine (*Dispositivos → Unidades ópticas → Eliminar disco*) y enciende la VM de nuevo. Entra como `root` con tu contraseña.
8. **Habilita el acceso SSH de root** (necesario porque por defecto OpenSSH lo bloquea). Este es el **único comando largo que teclearás a mano** en la consola de cada VM:
            
```
sed -i 's/^#PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config
rc-service sshd restart
```

**Nota de seguridad:** `PermitRootLogin yes` es aceptable solo en este laboratorio aislado. En producción jamás se habilita: se crea un usuario normal con `sudo` y llaves SSH.
9. Verifica la red:
            
```
ip addr show eth0
ip route
cat /etc/resolv.conf
```

            Debes ver tu IP `10.20.0.10/24`, una línea `default via 10.20.0.1` y `nameserver 10.20.0.1`.
10. Repite los pasos 2 a 9 para las otras dos VMs, cambiando nombre, red interna e IPs según la tabla: `srv-db` (red `red-interna`, IP `10.20.1.10`, GW/DNS `10.20.1.1`) y `srv-web` (red `red-dmz`, IP `10.20.2.10`, GW/DNS `10.20.2.1`).

*(Ver diagrama en la versión HTML: Alpine Linux — "Small. Simple. Secure." La guía sigue el flujo del asistente `setup-alpine` descrito en el [handbook oficial](https://docs.alpinelinux.org/user-handbook/0.1a/Installing/setup_alpine.html) y en la [wiki oficial de instalación](https://wiki.alpinelinux.org/wiki/Installation).)*

### B.7 — Flujo de trabajo con SSH y portapapeles (léelo antes de seguir)

Desde este punto, **ya no trabajarás en las consolas crudas de VirtualBox**. El flujo de trabajo del laboratorio es:

1. En tu equipo anfitrión lees esta guía y copias los comandos con `Ctrl+C`.
2. En la ventana de `admin-gui`, pegas en la terminal con `Ctrl+V` (el portapapeles compartido de VirtualBox lo transfiere; si no está activo todavía, igual puedes escribir los comandos — son pocos).
3. Para ejecutar algo en un servidor Alpine, primero entras por SSH desde la terminal de admin-gui:
            
```
ssh root@10.20.2.10     # srv-web
ssh root@10.20.1.10     # srv-db
ssh root@10.20.0.10     # cliente-usuarios
```

            La primera vez acepta la huella escribiendo `yes` y escribe la contraseña de root de esa VM. Una vez dentro, todo lo que pegues se ejecuta en el servidor remoto. Para salir: `exit`.
4. Para copiar **archivos** (por ejemplo el código PHP de la Parte D) desde admin-gui hacia un servidor, usa `scp`:
            `scp /home/osboxes/app/index.php root@10.20.2.10:/var/www/app/`

**Requisito de firewall:** para que este flujo funcione, en la Parte C crearás una regla en la zona ADMIN que permite SSH (puerto 22) hacia las tres zonas de servicio — la estación de administración es la única que puede hacerlo, igual que un bastion host en una empresa real.

### B.8 — Instantáneas (snapshots): tu red de seguridad

Antes de empezar a tocar el firewall, toma una instantánea de cada VM recién instalada. Si algo se daña en las partes C–E, podrás volver a este punto en segundos en lugar de reinstalar:

1. Con las VMs apagadas, en el VirtualBox Manager selecciona la VM → menú **Máquina → Herramientas → Instantáneas** (o el botón *Snapshots* en la barra derecha).
2. Pulsa **Tomar** (ícono de cámara) y nómbrala `01-instalacion-limpia`. Repite para las 5 VMs (OPNsense, admin-gui y las 3 Alpine).
3. Para restaurar más adelante: selecciona la instantánea y pulsa **Restaurar**.

*(Ver diagrama en la versión HTML: Referencia oficial: gestor de instantáneas de VirtualBox — tu punto de restauración antes de experimentar con las reglas. Fuente: [Manual de VirtualBox](https://www.virtualbox.org/manual/))*

## Políticas de Firewall entre Zonas y NAT de Salida

### C.1 — Verificar el bloqueo por defecto (evidencia Zero Trust)

OPNsense es un firewall **stateful** cuya política de entrada por defecto es **bloquear todo lo que no tenga una regla explícita** (default deny), como documenta su manual de reglas de firewall. Sin ninguna regla creada por ti, desde la consola de `cliente-usuarios` ejecuta:

```
ping -c 4 10.20.2.10
```

*Salida esperada (ejemplo ilustrativo):* `4 packets transmitted, 0 packets received, 100% packet loss`. Captura esta pantalla: es tu primera evidencia de que el firewall bloquea por defecto.

### C.2 — NAT de salida (masquerade) hacia Internet

Referencia oficial: [OPNsense — Network Address Translation (Outbound)](https://docs.opnsense.org/manual/nat.html)

Las zonas internas usan direcciones privadas (`10.20.x.x`) que no son enrutables en Internet: cuando un servidor interno hace una petición hacia afuera, el firewall debe reescribir la IP de origen con la IP de su WAN, porque el servidor externo no sabría devolver la respuesta a una IP privada. Esto es **Outbound NAT** (también llamado Source NAT o masquerade). Para que tus servidores puedan descargar paquetes con `apk` (y la estación admin-gui con `apt`):

1. En la interfaz web de OPNsense (trabajando desde el navegador de `admin-gui`) ve a **Firewall → NAT → Outbound**.
2. Selecciona el modo **"Hybrid outbound NAT rule generation"** y pulsa **Save**. Según la documentación oficial, los cuatro modos son: *Automatic* (reglas automáticas, el valor por defecto), *Hybrid* (automáticas + las manuales que agregues), *Manual* (solo manuales) y *Disabled*. El modo automático solo cubre la LAN; con hybrid conservamos las reglas automáticas y agregamos manualmente las zonas OPT.
3. En la sección de reglas manuales, pulsa **Add** (esquina superior derecha) y crea la primera regla:
            **Interface:** WAN (la documentación indica que casi siempre será WAN)
**TCP/IP Version:** IPv4
**Protocol:** any
**Source address:** selecciona "Network" y escribe `10.20.0.0/24`
**Source port:** any (la documentación aclara que el puerto de origen es aleatorio y casi nunca debe restringirse)
**Translation / target:** Interface address (es decir, la IP de la WAN)
**Description:** `NAT usuarios a Internet`
            Pulsa **Save**.
4. Repite con tres reglas idénticas cambiando solo el origen y la descripción: `10.20.1.0/24` ("NAT interna a Internet"), `10.20.2.0/24` ("NAT DMZ a Internet") y `10.20.3.0/24` ("NAT admin a Internet"). Al final pulsa el botón naranja **Apply changes**.

### C.3 — Política de la DMZ (srv-web)

Referencia oficial: [OPNsense — Firewall Rules](https://docs.opnsense.org/manual/firewall.html)

Ve a **Firewall → Rules → DMZ** y crea estas reglas **en este orden exacto**. El manual oficial explica por qué el orden manda: las reglas se procesan por interfaz, en dirección entrante (*inbound*, es decir, en la interfaz que recibe el tráfico), y por defecto cada regla es de tipo `quick` — **la primera regla que coincide con el paquete gana** y las siguientes ya no se evalúan. Para cada regla: botón **Add**, llenar los campos indicados, **Save**:

| # | Acción | Proto | Origen | Destino | Puerto destino | Propósito |
|---|---|---|---|---|---|---|
| 1 | Pass | TCP | DMZ net | Single host: 10.20.1.10 | 3306 (MySQL) | La app web habla con la BD — y solo con la BD |
| 2 | Block | any | DMZ net | Network 10.20.0.0/24 | any | La DMZ nunca inicia conexiones hacia usuarios |
| 3 | Block | any | DMZ net | Network 10.20.1.0/24 | any | La DMZ no ve el resto de la red interna |
| 4 | Pass | TCP/UDP | DMZ net | DMZ address | 53 (DNS) | Consultas DNS al resolvedor Unbound de OPNsense |
| 5 | Pass | TCP | DMZ net | any | 80, 443 (HTTP, HTTPS) | Descargas apk / actualizaciones vía NAT |

La regla 1 va **antes** que la 3: primero se permite MySQL hacia la BD específica, y después se bloquea todo lo demás hacia la red interna. Si las pones al revés, la aplicación nunca conectará. Cuando termines las cinco, pulsa **Apply changes**.

*Detalle del manual:* la acción `Block` descarta el paquete en silencio (recomendada para redes no confiables), mientras `Reject` además responde al cliente con un TCP RST o ICMP unreachable (práctica en redes internas porque el cliente no espera el timeout). En este lab usamos `Block` para observar el comportamiento más estricto.

### C.4 — Política de la red de usuarios (LAN)

En **Firewall → Rules → LAN** encontrarás la regla por defecto *"Default allow LAN to any"*, que es incompatible con Zero Trust. Primero crea las reglas nuevas y al final **desactiva** la regla permisiva (ícono de ✓ verde a su izquierda para deshabilitarla — no la borres todavía, por si necesitas revertir):

| # | Acción | Proto | Origen | Destino | Puerto destino | Propósito |
|---|---|---|---|---|---|---|
| 1 | Pass | TCP/UDP | LAN net | LAN address | 53 (DNS) | DNS hacia OPNsense |
| 2 | Pass | TCP | LAN net | Network 10.20.2.0/24 | 80, 443 | Usuarios → aplicación web en la DMZ |
| 3 | Block | any | LAN net | Network 10.20.1.0/24 | any | Usuarios nunca tocan la red interna |
| 4 | Pass | TCP | LAN net | any | 80, 443 | (Temporal) Internet para apk del cliente — bórrala al final del lab |

### C.5 — Política de la red interna (INTERNA)

En **Firewall → Rules → INTERNA** crea solo estas dos reglas; todo lo demás queda bloqueado por defecto:

| # | Acción | Proto | Origen | Destino | Puerto destino | Propósito |
|---|---|---|---|---|---|---|
| 1 | Pass | TCP/UDP | INTERNA net | INTERNA address | 53 (DNS) | DNS hacia OPNsense |
| 2 | Pass | TCP | INTERNA net | any | 80, 443 | Actualizaciones apk vía NAT (tráfico saliente) |

Nadie inicia conexiones **hacia** la red interna excepto la regla 3306 que ya creaste en la DMZ. Las reglas de esta tabla solo permiten que el servidor de BD salga a actualizarse.

### C.6 — Política de la zona de administración (ADMIN)

La estación `admin-gui` es tu puesto de trabajo privilegiado — el equivalente a un *bastion host* o jump box empresarial. En **Firewall → Rules → ADMIN** ya existe la regla de gestión web que creaste en B.5; agrega las siguientes debajo de ella:

| # | Acción | Proto | Origen | Destino | Puerto destino | Propósito |
|---|---|---|---|---|---|---|
| 0 | Pass | TCP | ADMIN net | This firewall | 443 (HTTPS) | (Ya existe desde B.5) Gestión de la interfaz web |
| 1 | Pass | TCP | ADMIN net | any | 22 (SSH) | Administrar las 3 VMs Alpine por SSH |
| 2 | Pass | TCP/UDP | ADMIN net | ADMIN address | 53 (DNS) | DNS hacia OPNsense |
| 3 | Pass | TCP | ADMIN net | any | 80, 443 | Actualizaciones apt / navegación de consulta |

Todo lo demás queda bloqueado por defecto. Nota el contraste deliberado: la zona de administración **sí** puede hablar con las demás zonas (solo por SSH), porque administrar es su función — pero nadie desde las demás zonas puede iniciar conexiones hacia ella.

### C.7 — Resumen: política resultante por zona

Esta es la matriz completa de políticas que debe quedar configurada. Úsala para autoevaluarte antes de las pruebas:

| Zona / Interfaz | Tráfico entrante permitido | Tráfico saliente permitido | Denegado (implícito o explícito) |
|---|---|---|---|
| **WAN** | En la Parte E: TCP 8080 para el port-forward | Traducciones NAT de las 4 zonas | Todo lo demás entrante (default deny) — la administración NO se expone aquí |
| **LAN (usuarios)** | SSH 22 solo desde la zona ADMIN | DNS al firewall · HTTP/HTTPS a la DMZ · (temporal) HTTP/HTTPS a Internet | Red interna completa · cualquier otro destino/puerto |
| **DMZ (srv-web)** | HTTP/HTTPS desde usuarios · (Parte E) HTTP redirigido por PAT desde WAN · SSH 22 solo desde ADMIN | MySQL 3306 solo a 10.20.1.10 · DNS al firewall · HTTP/HTTPS a Internet | Iniciar hacia usuarios · resto de la red interna · cualquier otro puerto |
| **INTERNA (srv-db)** | MySQL 3306 únicamente desde 10.20.2.10 · SSH 22 solo desde ADMIN | DNS al firewall · HTTP/HTTPS a Internet (actualizaciones) | Cualquier otro origen y cualquier otro puerto |
| **ADMIN (admin-gui)** | — | HTTPS 443 al firewall · SSH 22 a todas las zonas · DNS al firewall · HTTP/HTTPS a Internet | Cualquier otro destino/puerto |

### C.8 — Verificación de NAT, segmentación y acceso de administración

1. **NAT + DNS funcionando** — desde `srv-web` y desde `srv-db` (entra por SSH desde admin-gui: `ssh root@10.20.2.10`):
            
```
ping -c 3 8.8.8.8
ping -c 3 google.com
setup-apkrepos -1
apk update
```

            El primer ping prueba NAT puro (IP directa, sin DNS), el segundo prueba la resolución DNS a través de OPNsense, `setup-apkrepos -1` elige el primer mirror de la lista, y `apk update` confirma que puedes descargar índices de paquetes por el NAT. Captura una de estas salidas como evidencia de la salida NAT. (Ejecuta también `setup-apkrepos -1` en `cliente-usuarios` si necesitas instalarle paquetes.)
2. **El acceso SSH de administración funciona** — desde la terminal de `admin-gui`:
            `ssh root@10.20.2.10 "hostname"`
            Debe responder `srv-web`. Esto confirma que la regla SSH de la zona ADMIN está operativa (y es tu primera evidencia del plano de administración funcionando).
3. **Bloqueo usuarios → interna** — desde `cliente-usuarios`:
            
```
ping -c 3 10.20.1.10
nc -zv 10.20.1.10 3306
```

            Ambos deben fallar (timeout).
4. **Bloqueo DMZ → usuarios** — desde `srv-web`:
            `ping -c 3 10.20.0.10`
            Debe fallar.
5. Abre **Firewall → Log Files → Live View** en OPNsense mientras repites las pruebas: verás en tiempo real cada paquete marcado como *pass* (verde) o *block* (rojo) con la regla que lo procesó. El manual recomienda poner descripciones legibles a las reglas y activar su opción *Log* precisamente para poder leerlas en esta vista. Captura esta vista como evidencia complementaria.

## Aplicación Web en la DMZ + Base de Datos en la Red Interna

Desplegarás una aplicación web sencilla en PHP (código incluido abajo) que se conecta por red a MariaDB. Cada visita a la página inserta un registro en la base de datos de la red interna — así tu evidencia demuestra el flujo completo: *cliente → firewall → DMZ → firewall → BD interna*. Gracias a la estación `admin-gui`, escribirás el código en un editor gráfico y lo transferirás por `scp` — sin teclearlo en consolas seriales.

### D.0 — Anatomía de un paquete en tu laboratorio

Antes de escribir comandos, entiende el recorrido exacto de una petición (son los números ①②③ de la Figura 1):

1. `cliente-usuarios` (10.20.0.10) pide `http://10.20.2.10`. El paquete sale por eth0 hacia su gateway `10.20.0.1` y **entra al firewall por la interfaz LAN**. Ahí se evalúan las reglas de LAN de arriba hacia abajo: coincide con la regla 2 (TCP hacia 10.20.2.0/24 puerto 80) → **pass**. OPNsense crea una **entrada de estado** para esta conexión.
2. El firewall reenvía el paquete por su interfaz DMZ (`10.20.2.1`) hasta `srv-web`. nginx recibe la petición y PHP se ejecuta: la aplicación abre una **segunda conexión**, esta vez TCP al puerto 3306 de `10.20.1.10`. Ese paquete entra al firewall por la interfaz DMZ: coincide con la regla 1 de la DMZ (3306 solo a la BD) → **pass**.
3. El firewall entrega el paquete por su interfaz INTERNA a `srv-db`, y MariaDB responde. Aquí está la magia del firewall **stateful** que describe la documentación oficial: **las respuestas de una conexión ya establecida regresan automáticamente sin necesitar reglas inversas** — por eso nunca creaste una regla "INTERNA → DMZ" ni "DMZ → usuarios" para el tráfico de respuesta, y sin embargo todo funciona.

Si entiendes estos tres saltos, entiendes el laboratorio completo: cada zona solo puede iniciar lo que su política permite explícitamente, y el estado de la conexión se encarga del retorno.

### D.1 — Servidor MariaDB en srv-db (10.20.1.10)

Trabaja desde la terminal de `admin-gui`: entra por SSH con `ssh root@10.20.1.10` y ejecuta allí todos los comandos de esta sección (así puedes copiarlos y pegarlos desde esta guía).

1. Instala MariaDB:
            
```
apk update
apk add mariadb mariadb-client
```
2. Inicializa el directorio de datos y arranca el servicio:
            
```
/etc/init.d/mariadb setup
rc-service mariadb start
rc-update add mariadb
```
3. Asegura la instalación:
            `mysql_secure_installation`
            Responde: cuando pida la contraseña actual de root pulsa Enter (está vacía) → `y` para definir una nueva contraseña de root de MariaDB (escríbela dos veces) → `y` a remover usuarios anónimos → `y` a deshabilitar el login remoto de root → `y` a eliminar la base de prueba → `y` a recargar privilegios.
4. Por defecto MariaDB solo escucha en `localhost`; hay que decirle que escuche en la IP de la red interna. Edita el archivo `/etc/my.cnf.d/mariadb-server.cnf` (con `vi` o instala `nano` con `apk add nano`) y en la sección `[mysqld]` deja estas líneas así (si alguna existe comentada con `#`, descoméntala y cámbiala):
            
```
[mysqld]
bind-address = 10.20.1.10
skip-networking = 0
```

            Reinicia el servicio para aplicar:
            `rc-service mariadb restart`
            Verifica que escucha en la red:
            `netstat -tlnp | grep 3306`
*Salida esperada (ejemplo ilustrativo):* una línea con `10.20.1.10:3306` en estado `LISTEN`.
5. Crea la base de datos, la tabla y el usuario exclusivo de la aplicación:
            `mysql -u root -p`
            (escribe la contraseña de root de MariaDB que definiste). Dentro del prompt `MariaDB [(none)]>` ejecuta una por una:
            
```
CREATE DATABASE appdb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'appuser'@'10.20.2.10' IDENTIFIED BY 'Cl4ve-Segura-Lab';
GRANT SELECT, INSERT ON appdb.* TO 'appuser'@'10.20.2.10';
USE appdb;
CREATE TABLE visitas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  ip_cliente VARCHAR(45) NOT NULL,
  fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
FLUSH PRIVILEGES;
EXIT;
```

            Fíjate en la doble capa de seguridad: el usuario `appuser` solo puede conectarse desde la IP exacta del servidor web (`10.20.2.10`) y solo tiene privilegios de `SELECT` e `INSERT` sobre `appdb` — ni siquiera puede borrar datos. El firewall limita la red; la base de datos limita al origen y al privilegio mínimo.

### D.2 — Servidor web nginx + PHP en srv-web (10.20.2.10)

1. Entra por SSH: `ssh root@10.20.2.10`. Instala nginx, PHP-FPM y la extensión de MySQL:
            
```
apk update
apk add nginx php83-fpm php83-mysqli php83-session
```

**Nota:** si tu versión de Alpine trae PHP 8.4 en lugar de 8.3, cambia el prefijo `php83` por `php84` en los paquetes (verifica con `apk search php8 | head`).
2. Configura PHP-FPM para correr con el mismo usuario que nginx. Edita `/etc/php83/php-fpm.d/www.conf` y ajusta estas líneas (búscalas con `/user` en vi):
            
```
user = nginx
group = nginx
listen = 127.0.0.1:9000
listen.owner = nginx
listen.group = nginx
```
3. Crea el directorio del sitio:
            
```
mkdir -p /var/www/app
chown -R nginx:nginx /var/www/app
```
4. Ahora el código de la aplicación. **En admin-gui** abre un editor de texto gráfico (menú de aplicaciones → *Text Editor* / *FeatherPad* / *Mousepad* según la imagen OSBoxes), pega este contenido completo (cópialo con el botón "Copiar" del bloque) y guárdalo como `/home/osboxes/app/index.php` (crea la carpeta `app`):
            
```
<?php
// ============================================================
// App de laboratorio - Seguridad en Redes (CUC)
// Se conecta a MariaDB en la RED INTERNA y registra visitas.
// ============================================================
$host = '10.20.1.10';   // srv-db en la red interna
$user = 'appuser';
$pass = 'Cl4ve-Segura-Lab';
$db   = 'appdb';

$estado = '';
$ok     = false;
$filas  = [];

try {
    $conn = new mysqli($host, $user, $pass, $db);
    $conn->set_charset('utf8mb4');

    $ip = $_SERVER['REMOTE_ADDR'] ?? 'desconocida';
    $stmt = $conn->prepare('INSERT INTO visitas (ip_cliente) VALUES (?)');
    $stmt->bind_param('s', $ip);
    $stmt->execute();

    $res = $conn->query('SELECT id, ip_cliente, fecha FROM visitas ORDER BY id DESC LIMIT 10');
    while ($r = $res->fetch_assoc()) { $filas[] = $r; }

    $estado = 'CONECTADO a MariaDB en ' . $host . ':3306';
    $ok = true;
} catch (Throwable $e) {
    http_response_code(500);
    $estado = 'ERROR de conexion a la base de datos: ' . $e->getMessage();
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>App Lab - DMZ</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 640px; margin: 40px auto; padding: 0 16px; color: #222; }
    .card { border: 1px solid #ddd; border-radius: 12px; padding: 20px 24px; box-shadow: 0 4px 14px rgba(0,0,0,.06); }
    .ok  { color: #0a7a3d; font-weight: 700; }
    .err { color: #b00020; font-weight: 700; }
    table { border-collapse: collapse; width: 100%; margin-top: 12px; font-size: 14px; }
    th, td { border: 1px solid #ddd; padding: 6px 10px; text-align: left; }
    th { background: #f4f4f4; }
    .meta { color: #666; font-size: 13px; }
  </style>
</head>
<body>
  <div class="card">
    <h1>Aplicacion del Laboratorio</h1>
    <p class="meta">Servidor web: <?php echo gethostname(); ?> (zona DMZ, 10.20.2.10)</p>
    <p class="<?php echo $ok ? 'ok' : 'err'; ?>"><?php echo $estado; ?></p>
    <?php if ($ok): ?>
      <h2>Ultimas 10 visitas registradas en la BD interna</h2>
      <table>
        <tr><th>#</th><th>IP cliente</th><th>Fecha</th></tr>
        <?php foreach ($filas as $f): ?>
          <tr>
            <td><?php echo $f['id']; ?></td>
            <td><?php echo htmlspecialchars($f['ip_cliente']); ?></td>
            <td><?php echo $f['fecha']; ?></td>
          </tr>
        <?php endforeach; ?>
      </table>
    <?php endif; ?>
  </div>
</body>
</html>
```
5. Transfiere el archivo al servidor web por SSH (desde la terminal de admin-gui):
            `scp /home/osboxes/app/index.php root@10.20.2.10:/var/www/app/`
            Luego, en la sesión SSH de `srv-web`, ajusta el propietario:
            `chown nginx:nginx /var/www/app/index.php`
6. Crea la configuración de nginx. Reemplaza **todo** el contenido del archivo `/etc/nginx/http.d/default.conf` por:
            
```
server {
    listen 80 default_server;
    server_name _;
    root /var/www/app;
    index index.php index.html;

    location / {
        try_files $uri $uri/ /index.php?$args;
    }

    location ~ \.php$ {
        fastcgi_pass 127.0.0.1:9000;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
    }
}
```
7. Arranca ambos servicios y déjalos habilitados al arranque:
            
```
rc-service php-fpm83 start
rc-service nginx start
rc-update add php-fpm83
rc-update add nginx
```

            (Si instalaste PHP 8.4, el servicio se llama `php-fpm84`.)
8. Verifica localmente que nginx y PHP responden:
            `wget -qO- http://127.0.0.1 | head -8`
            Deberías ver el HTML de la aplicación. Si aparece el mensaje de error de conexión a la BD, es lo esperado hasta que pruebes la ruta completa en el siguiente paso.

### D.3 — Verificación de extremo a extremo

1. **La ruta de datos hacia la BD existe** — desde `srv-web`:
            `nc -zv 10.20.1.10 3306`
*Salida esperada (ejemplo ilustrativo):* `10.20.1.10 (10.20.1.10:3306) open`. Si dice `open`, tu regla 1 de la DMZ y MariaDB están bien. Si falla, revisa el orden de las reglas en C.3 y el `bind-address` en D.1.
2. **El usuario navega la aplicación** — desde `cliente-usuarios`:
            `wget -qO- http://10.20.2.10 | grep -E "CONECTADO|ERROR|visitas"`
            Debes ver la línea `CONECTADO a MariaDB en 10.20.1.10:3306` y el encabezado de la tabla de visitas. Cada vez que ejecutes el comando se inserta una visita nueva con la IP del cliente (`10.20.0.10`) — ejecútalo 2 o 3 veces y verás crecer la tabla.
3. **El usuario NO puede tocar la base de datos** — desde `cliente-usuarios`:
            `nc -zv 10.20.1.10 3306`
            Debe fallar (timeout). Captura esta salida junto con la anterior: son la evidencia central del laboratorio.
4. **Vista gráfica desde la zona de administración:** en el navegador de `admin-gui` abre `http://10.20.2.10` — debería funcionar gracias a la regla SSH/web... ¡espera! Si no carga, es porque la zona ADMIN no tiene una regla HTTP hacia la DMZ. Añádela como ejercicio: *Firewall → Rules → ADMIN → Add → Pass · TCP · ADMIN net → 10.20.2.10 · puerto 80 · descripción "Admin prueba la app"*. Ahora sí: recarga y verás la app completa con su tabla de visitas. Esta captura (navegador gráfico con la app y la URL visibles) es una de las evidencias más claras de tu entregable.
5. **Evidencia en el firewall:** con las pruebas anteriores corriendo, abre **Firewall → Log Files → Live View** y captura los registros mostrando el `pass` de `10.20.2.10 → 10.20.1.10:3306` y los `block` de los intentos prohibidos desde usuarios.

## NAT/PAT Entrante: Publicar la Aplicación hacia la WAN

### E.1 — Concepto: NAT de salida vs. PAT entrante (port forwarding)

Referencia oficial: [OPNsense — Destination NAT (Port Forward)](https://docs.opnsense.org/manual/nat.html)

En la Parte C configuraste **NAT de salida**: muchos hosts internos comparten la IP de la WAN para salir (masquerade). Ahora harás lo inverso: **PAT entrante**, que la documentación de OPNsense llama *Destination NAT (Port Forward)*. El problema que resuelve: cuando varios clientes internos comparten una sola IP externa, una conexión entrante dirigida a la IP externa no tiene a dónde ir — el firewall no sabe a qué host interno entregarla. La solución es una regla que traduzca *destino = IP-WAN, puerto 8080* hacia *10.20.2.10, puerto 80*. Es exactamente lo que hace una empresa cuando publica su sitio web sin exponer nada más de su red.

| Mecanismo | Dirección | Qué traduce | Ejemplo en tu lab |
|---|---|---|---|
| **NAT saliente (masquerade)** | Interna → Internet | IP origen interna → IP de la WAN | `10.20.2.10` sale a Internet como `<IP-WAN>` |
| **PAT entrante (port forward)** | Internet → Interna | Puerto de la WAN → IP:puerto interno | `<IP-WAN>:8080` → `10.20.2.10:80` |

### E.2 — Crear la regla de Port Forward

1. En la interfaz web de OPNsense ve a **Firewall → NAT → Port Forward** y pulsa **Add** (esquina superior derecha).
2. Llena el formulario exactamente así (los nombres de campo corresponden a la documentación oficial):
            **Interface:** WAN — la interfaz en la que *se origina* el tráfico entrante.
**TCP/IP Version:** IPv4
**Protocol:** TCP
**Source / Invert:** sin marcar · **Source Address:** any (cualquier equipo de la red física podrá probar la app) · **Source Port:** any
**Destination Address:** WAN address — el destino original del paquete es la IP externa del firewall.
**Destination Port:** de `8080` a `8080` (usamos 8080 y no 80 para no chocar con servicios de tu red física ni con la interfaz web del firewall)
**Redirect Target IP:** `10.20.2.10` — la IP interna a la que se reenvía el tráfico.
**Redirect Target Port:** `80` (HTTP) — el puerto del servidor interno.
**Description:** `Publicar app web de la DMZ`
**Filter rule association:** aquí la documentación oficial ofrece tres opciones y vale la pena entenderlas:
                *None:* no crea ninguna regla — tendrías que crearla a mano en *Firewall → Rules → WAN* (recomendada solo para escenarios complejos).
*Pass:* deja pasar el tráfico de la regla NAT sin crear una regla visible en la lista (recomendada por simplicidad en la mayoría de casos, pero no se puede auditar en la lista de reglas).
*Add associated filter rule:* crea una regla vinculada **visible** en *Firewall → Rules → WAN*, que se actualiza automáticamente si editas la regla NAT. **Elige esta**: en el laboratorio te conviene ver y documentar la regla. Ten en cuenta el detalle clave de la documentación: el destino de la regla de firewall generada será la IP interna del NAT (`10.20.2.10`), no la IP de la WAN.
3. Pulsa **Save** y luego **Apply changes**.
4. Verifica la regla asociada: ve a **Firewall → Rules → WAN** — debes ver una regla nueva que permite TCP hacia `10.20.2.10` puerto 80, vinculada a tu port forward. No la edites manualmente (se gestiona desde la regla NAT; si la editas a mano, se desvincula).

### E.3 — Verificación desde la red WAN

1. Desde el navegador de **tu equipo anfitrión** (que está en la red WAN del laboratorio), abre:
            `http://<IP-WAN>:8080`
            Debe cargar la aplicación del laboratorio con el mensaje `CONECTADO a MariaDB en 10.20.1.10:3306` y la tabla de visitas. Captura esta pantalla completa (con la URL visible): es la evidencia de que el PAT entrante funciona.
2. Recarga la página 2 o 3 veces y observa cómo la tabla registra las visitas nuevas. La IP que verás registrada será la de tu equipo en la red física — anótala y coméntala en tu análisis (demuestra que el firewall preserva el origen real al reenviar).
3. Confirma lo que **no** quedó expuesto: desde tu equipo anfitrión intenta `ping 10.20.1.10` o conectarte al puerto 3306 de la WAN — todo debe fallar. Solo el puerto 8080 publicado responde.
4. En **Firewall → Log Files → Live View**, filtra por la interfaz WAN y captura el registro `pass` del tráfico entrante hacia `10.20.2.10:80`.

### E.4 — Pregunta de análisis

Piensa en este escenario para tu entregable: un atacante en la red WAN encuentra el puerto 8080 abierto y explota una vulnerabilidad en la aplicación PHP, logrando ejecutar comandos como el usuario `nginx` en `srv-web`. Con las políticas que configuraste: ¿a qué puede llegar desde ahí? (Pista: puede leer las credenciales del `index.php` y hablar con la BD por el 3306 con privilegios de solo SELECT/INSERT sobre `appdb`… pero ¿puede alcanzar la red de usuarios? ¿otros hosts de la red interna? ¿la interfaz de administración del firewall? ¿puede la BD iniciar conexiones de vuelta hacia él? ¿puede tocar la zona de administración?)

## Entregable del Laboratorio

Un solo documento **PDF** individual que contenga, en este orden:

1. **Diagrama de la topología** implementada (puedes basarte en la Figura 1 de esta guía, dibujarlo en draw.io o fotografiar tu esquema a mano) indicando las 4 zonas internas, las IPs, los flujos permitidos y el port forward.
2. **Matriz de pruebas ejecutadas**: replica esta tabla en tu informe y márcala con tus resultados reales (✓/✗) más la captura asociada a cada prueba:
            #DesdeHaciaComando / acciónResultado esperado¿Lo lograste?
P1cliente-usuarios10.20.2.10 (ICMP)ping -c 4 10.20.2.10Falla — bloqueo por defecto (antes de crear reglas)
P2srv-web / srv-db8.8.8.8ping -c 3 8.8.8.8Funciona — NAT saliente operativo
P3srv-webgoogle.comping -c 3 google.comFunciona — DNS vía OPNsense
P4cliente-usuarios10.20.1.10:3306nc -zv 10.20.1.10 3306Falla — usuarios nunca tocan la BD
P5srv-web10.20.0.10 (ICMP)ping -c 3 10.20.0.10Falla — la DMZ no inicia hacia usuarios
P6srv-web10.20.1.10:3306nc -zv 10.20.1.10 3306Funciona (open) — única vía permitida a la interna
P7cliente-usuarios10.20.2.10:80wget -qO- http://10.20.2.10HTML de la app + "CONECTADO a MariaDB"
P8admin-guisrv-web (SSH)ssh root@10.20.2.10 "hostname"Responde "srv-web" — plano de administración operativo
P9tu equipo (WAN)<IP-WAN>:8080Navegador → http://<IP-WAN>:8080La app carga — PAT entrante operativo
P10tu equipo (WAN)10.20.1.10ping 10.20.1.10Falla — la BD no existe para la WAN
3. **Capturas de evidencia técnica** (con la terminal y la fecha/hora visibles) de cada prueba de la matriz, más el **Live View** de OPNsense mostrando los pass/block relevantes (C.8 y E.3).
4. **Tabla de políticas por zona**: tu versión de la tabla C.7 con lo que efectivamente configuraste (puedes fotografiar tus pantallas de *Firewall → Rules* por interfaz como soporte).
5. **Análisis de seguridad (5–8 líneas):** responde la pregunta de E.4 — qué puede y qué no puede hacer un atacante que comprometió la aplicación publicada por PAT, y cómo la combinación de segmentación + privilegio mínimo en la base de datos + plano de administración separado limita el daño.

## Solución de Problemas Frecuentes

Si algo no funciona, ubica el síntoma en esta tabla antes de preguntar — el 90% de los bloqueos del laboratorio están aquí:

| Síntoma | Causa más probable | Solución |
|---|---|---|
| El instalador de OPNsense falla con *"File copy failed during installation"* | Memoria insuficiente asignada a la VM (problema documentado oficialmente) | Apaga la VM, súbela a **2048 MB** de RAM y reintenta la instalación |
| La WAN de OPNsense no obtiene IP | El Adaptador 1 no está en modo puente o apunta a la tarjeta física equivocada (ej. Ethernet sin cable) | Configuración → Red → Adaptador 1 → Adaptador puente → elige la tarjeta que sí tiene Internet (normalmente tu Wi-Fi). Luego en consola: opción 8 → `dhclient em0` |
| No carga `https://10.20.3.1` desde admin-gui | Reactivaste el firewall (`pfctl -e`) antes de crear la regla de administración, o la regla tiene mal el origen/destino | Consola de OPNsense → opción 8 → `pfctl -d` → entra por el navegador → revisa la regla en *Firewall → Rules → ADMIN* (Source: ADMIN net · Destination: This firewall · puerto 443) → `pfctl -e` |
| No puedes copiar/pegar texto dentro de las VMs Alpine | La consola de VirtualBox es una terminal serial cruda — no tiene portapapeles | No es un error: trabaja por SSH desde la terminal de admin-gui (`ssh root@10.20.x.x`). El portapapeles bidireccional solo aplica entre tu equipo y admin-gui |
| `apk update` falla en una VM Alpine | Sin NAT de salida, sin regla 80/443 en esa zona, o sin DNS | Verifica en orden: `ping 10.20.2.1` (gateway) → `ping 8.8.8.8` (NAT) → `ping google.com` (DNS). El primero que falle te dice qué capa revisar (red local / NAT / regla DNS) |
| `nc -zv 10.20.1.10 3306` falla desde srv-web | Regla 3306 debajo del bloqueo a la red interna, o MariaDB escuchando solo en localhost | En *Firewall → Rules → DMZ* sube la regla 3306 por encima del bloqueo (flecha de mover). En srv-db verifica `netstat -tlnp \| grep 3306` → debe mostrar `10.20.1.10:3306`, no `127.0.0.1:3306` |
| La app muestra *"ERROR de conexión a la base de datos"* | Usuario/clave incorrectos en `index.php`, o el usuario MariaDB no permite el origen | Verifica que el usuario sea `'appuser'@'10.20.2.10'` (con esa IP exacta) y que la clave coincida. Prueba desde srv-web: `apk add mariadb-client` → `mysql -h 10.20.1.10 -u appuser -p` |
| nginx responde *502 Bad Gateway* | PHP-FPM no está corriendo o escucha en otro socket/puerto | `rc-service php-fpm83 status` → si está parado, `rc-service php-fpm83 start`. Verifica que `listen = 127.0.0.1:9000` en www.conf coincida con el `fastcgi_pass` de nginx |
| El port forward no responde desde tu navegador (`http://<IP-WAN>:8080`) | Falta la regla de firewall asociada en WAN, o la app no está escuchando | Verifica que en *Firewall → Rules → WAN* exista la regla vinculada al port forward hacia `10.20.2.10:80`. Luego desde srv-web: `wget -qO- http://127.0.0.1 \| head -3` debe responder |
| Después de cambiar reglas, una conexión vieja sigue comportándose igual | La tabla de estados conserva la conexión anterior (comportamiento stateful documentado) | *Firewall → Diagnostics → States → Reset States* para forzar que las conexiones se reevalúen con las reglas nuevas |

## Rúbrica de Evaluación (10% de la nota final)

| Criterio | Qué se evalúa | Peso |
|---|---|---|
| **Topología montada y funcional** | VirtualBox + OPNsense + 3 VMs Alpine + estación admin-gui en sus zonas correctas, con IPs coherentes con la Parte A. | 25% |
| **Políticas de firewall entre zonas** | Política Zero Trust por interfaz, en el orden correcto, verificada con evidencia real (permitido vs. bloqueado). | 30% |
| **Aplicación web + base de datos** | App en la DMZ respondiendo y conectada a MariaDB de la red interna únicamente por el puerto 3306. | 20% |
| **NAT saliente y PAT entrante** | Salida a Internet por masquerade y publicación del servicio por port forward, ambos verificados. | 15% |
| **Razonamiento de seguridad** | Análisis del escenario de compromiso y de cómo la segmentación limita el movimiento lateral. | 10% |

## Referencias Oficiales y Glosario

Esta guía está alineada con la documentación oficial de las herramientas. Consúltala si un paso difiere de lo que ves en tu versión del software:

- [OPNsense — Initial Installation & Configuration](https://docs.opnsense.org/manual/install.html) (instalador, entorno en vivo, menú de consola, configuración inicial)
- [OPNsense — Virtual & Cloud-Based Installation](https://docs.opnsense.org/manual/virtuals.html) (requisitos de RAM/disco en VMs, off-loading, problemas conocidos)
- [OPNsense — Firewall Rules](https://docs.opnsense.org/manual/firewall.html) (stateful, orden de procesamiento, quick, block vs. reject, default deny)
- [OPNsense — Network Address Translation](https://docs.opnsense.org/manual/nat.html) (Outbound NAT, Destination NAT / Port Forward, filter rule association)
- [Oracle VM VirtualBox User Manual — Chapter 1: First Steps](https://www.virtualbox.org/manual/ch01.html) (VirtualBox Manager, asistente de creación de VMs, memoria y disco)
- [Alpine Linux Handbook — setup-alpine](https://docs.alpinelinux.org/user-handbook/0.1a/Installing/setup_alpine.html) y [Wiki oficial — Installation](https://wiki.alpinelinux.org/wiki/Installation)
- [OSBoxes](https://www.osboxes.org/) (imágenes VDI pre-construidas para VirtualBox — fuente de la estación admin-gui)

### Glosario mínimo

| Término | Definición práctica (como se usa en este lab) |
|---|---|
| **Zero Trust** | Nada se confía por defecto: todo tráfico se deniega salvo que una regla explícita lo permita. |
| **Default deny** | La política implícita del firewall: si ningún paquete coincide con una regla, se descarta en silencio. |
| **DMZ** | Zona desmilitarizada: red intermedia donde viven los servicios expuestos, aislada de la red interna. |
| **Stateful** | El firewall recuerda las conexiones activas: las respuestas de una conexión permitida regresan sin regla inversa. |
| **NAT saliente (masquerade)** | Muchos hosts internos comparten la IP de la WAN para salir a Internet; el firewall reescribe el origen. |
| **PAT entrante (port forward)** | Publicar un servicio interno: un puerto de la IP de la WAN se traduce a la IP:puerto del servidor interno. |
| **Red interna (VirtualBox)** | Switch virtual aislado dentro del hipervisor: solo se comunican las VMs conectadas a ese mismo nombre de red. |
| **Plano de administración** | Zona separada (red-admin) desde donde se gestiona el firewall y los servidores; nunca se expone por la WAN. |

## Checklist de Verificación Previa

- Virtualización habilitada en BIOS/UEFI antes de instalar cualquier software.
- Mínimo 8 GB de RAM en el equipo y 35 GB de disco libres.
- En Windows: verificado que Hyper-V/WSL2 no generan conflicto con VirtualBox.
- Estación admin-gui arrancando con escritorio gráfico y portapapeles bidireccional probado.
- Instantáneas tomadas de las 5 VMs recién instaladas (B.8) antes de tocar reglas.
- Regla de administración creada ANTES de reactivar el firewall (pfctl -e) — no me bloqueé a mí mismo.
- Orden de reglas de la DMZ revisado: primero el permitir 3306 a la BD, después los bloqueos.
- Respaldo config-*.xml descargado y port forward desactivado al terminar las evidencias.
