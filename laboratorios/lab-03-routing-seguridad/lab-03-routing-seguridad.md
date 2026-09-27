# Laboratorio 3: Routing Multi-Sitio con Seguridad de Red Aplicada

> **Seguridad en Redes (CUC) · Ponderación y semana: por definir con Rodolfo — construido a partir del "Taller de Routing" original.**
> Adaptado del taller de enrutamiento estático/VLANs de Packet Tracer (base: Ing. Rodolfo Cañas), agregando la capa de seguridad que el taller original no tenía: gestión remota cifrada (SSH/AAA), control de acceso entre zonas (ACLs) y monitoreo centralizado (Syslog) — para que el mismo escenario de red sirva también como ejercicio de Seguridad en Redes, no solo de Routing.

## Antes de empezar — 3 correcciones al taller original

Al revisar el taller base se encontraron 3 errores técnicos que se corrigen aquí (no están en la versión que circulaba antes):

1. **Máscara incorrecta en R4 (interfaz de LAN3):** la configuración original tenía `ip address 172.30.3.1 255.255.248.0` (`/21`), pero el diseño (tabla de LANs 2-5) definía `172.30.3.0/24`. Se corrige a `255.255.255.0`.
2. **IP de ping mal escrita en la prueba de conectividad a LAN2/LAN3:** el taller original probaba `170.20.2.3` (con "170", typo) en vez de `172.20.2.2` — eso explica el "Destination host unreachable" que aparecía ahí, no era un problema real de la red. Se corrige el destino del ping.
3. **Ruta rechazada en R6 sin explicar por qué:** el taller original mostraba el error real de IOS `%Invalid next hop address (it's this router)` al intentar `ip route 10.0.5.0 255.255.255.252 10.0.4.1` (esa IP es la del propio R6, no puede ser el "next hop"). Se corrige a `10.0.4.2` (la IP de R5 al otro lado del enlace) y se deja la nota explicando el error, como ejemplo real de troubleshooting — vale la pena mostrarlo a los estudiantes, pero explicado, no como si fuera parte normal del procedimiento.

## Topología (igual que el taller original, sin cambios)

6 routers (R1-R6) interconectados por 6 enlaces WAN punto a punto en anillo/malla parcial, LAN #1 con 2 VLANs (GrupoA/GrupoB) tras un switch central + 2 switches de acceso, LAN #2 a LAN #5 sin VLANs (una red plana cada una), un servidor Web (LAN5) y un servidor DNS (LAN4).

**Planificación de LAN #1 (VLSM sobre 192.168.10.0/24):**

| VLAN | Nombre | Hosts | Red | Rango asignable | Gateway |
|---|---|---|---|---|---|
| 10 | GrupoA | 70 | 192.168.10.0/25 | .1 - .126 | 192.168.10.1 |
| 20 | GrupoB | 50 | 192.168.10.128/26 | .129 - .190 | 192.168.10.129 |

**LAN #2 a LAN #5** (sin VLAN, /24 cada una): LAN2 `172.20.2.0/24`, LAN3 `172.30.3.0/24` (**corregida**, ver error 1), LAN4-DNS `172.40.4.0/24`, LAN5-Web `172.50.5.0/24`.

**WANs (6 enlaces /30 punto a punto):** WAN1 R1-R2, WAN2 R2-R4, WAN3 R4-R6, WAN4 R6-R5, WAN5 R5-R3, WAN6 R3-R1 (`10.0.1.0/30` a `10.0.6.0/30` en ese orden) — ver el taller original para el detalle interfaz por interfaz, no se repite aquí porque no cambia.

**Ruteo:** estático en los 6 routers (cada uno con las rutas hacia las redes que no están directamente conectadas). Ver taller original para las 7-8 rutas por router — tampoco cambian, solo se corrige la de R6 (error 3).

## Parte NUEVA — Capa de seguridad (esto es lo que agrega este laboratorio)

### S.1 — Gestión remota cifrada: SSH en vez de Telnet (todos los routers y switches)

**Por qué:** Telnet manda usuario y clave en texto plano; cualquiera que capture el tráfico de gestión los ve. SSH los cifra. Es la primera regla de hardening de cualquier dispositivo de red real.

En **cada router y switch** (ejemplo con R1, repetir con R2-R6, Central, SW-1, SW-2):

```
enable
configure terminal
hostname R1
ip domain-name cuc-lab.local
username admin privilege 15 secret Cisco123!
crypto key generate rsa
   ! elegir 1024 bits cuando lo pida
line vty 0 4
 transport input ssh
 login local
 exec-timeout 5 0
line console 0
 exec-timeout 5 0
 logging synchronous
enable secret Cisco123!
service password-encryption
end
wr
```

**Verificación:** desde otro router, `ssh -l admin <ip-destino>` debe pedir la clave y entrar; `telnet <ip-destino>` debe ser rechazado (no hay `transport input telnet`).

### S.2 — Control de acceso entre zonas: ACLs extendidas (en R1, punto de entrada de LAN #1)

**Objetivo:** aplicar el principio de mínimo privilegio del taller de Identidad y Acceso (semana 7) a esta topología: GrupoB (usuarios) no necesita administrar nada — solo debe poder navegar a la Web (LAN5) y resolver DNS (LAN4). GrupoA (TI/administración) sí puede llegar a todo.

En R1:

```
enable
configure terminal
ip access-list extended ACL-GRUPOB
 permit udp 192.168.10.128 0.0.0.63 host 172.40.4.2 eq 53
 permit tcp 192.168.10.128 0.0.0.63 host 172.50.5.2 eq 80
 permit tcp 192.168.10.128 0.0.0.63 host 172.50.5.2 eq 443
 permit icmp 192.168.10.128 0.0.0.63 host 172.50.5.2
 deny ip 192.168.10.128 0.0.0.63 172.20.2.0 0.0.0.255
 deny ip 192.168.10.128 0.0.0.63 172.30.3.0 0.0.0.255
 permit ip any any
exit
interface g0/0/1.2
 ip access-group ACL-GRUPOB in
end
wr
```

**Qué demuestra:** `permit ip any any` al final es intencional — el punto no es bloquear todo, es bloquear específicamente lo que GrupoB no necesita (acceso a LAN2/LAN3, redes de administración/servidores internos) sin romper su navegación normal.

**Verificación:** desde una PC de GrupoB, `ping 172.50.5.2` (Web) debe responder; `ping 172.20.2.2` (LAN2) debe fallar por la ACL, no por falta de ruta (se puede comparar con el resultado de una PC de GrupoA, que sí llega).

### S.3 — Port Security en los switches de acceso (SW-1, SW-2)

**Objetivo:** que un puerto de acceso solo acepte la MAC del equipo que ya está conectado — si alguien desconecta la PC y conecta otro equipo (o un switch no autorizado), el puerto se bloquea.

En SW-1 y SW-2, en los puertos de acceso (`f0/2` a `f0/20`):

```
enable
configure terminal
interface range f0/2-20
 switchport port-security
 switchport port-security maximum 1
 switchport port-security mac-address sticky
 switchport port-security violation shutdown
end
wr
```

**Verificación:** `show port-security interface f0/2` debe mostrar la MAC aprendida y el estado `secure-up`. Si se cambia el cable de esa PC a otro puerto y se intenta usarlo con una MAC distinta en el puerto original (simulado agregando otra PC), el puerto debe pasar a `err-disabled`.

### S.4 — Monitoreo centralizado: Syslog (nuevo dispositivo en LAN4)

**Objetivo:** conectar el tema de la semana ("Monitoreo y logging de red") con la topología existente — todos los routers mandan sus logs a un solo punto, en vez de tener que revisar cada uno por separado.

1. Agregar un servidor genérico ("Server-PT") en LAN4, junto al DNS existente, con IP `172.40.4.3/24`. Activar el servicio **Syslog** en su pestaña "Services".
2. En cada router:

```
enable
configure terminal
logging host 172.40.4.3
logging trap informational
logging on
end
wr
```

**Verificación:** provocar un evento (por ejemplo, un intento de SSH fallido, o el port-security del paso S.3 disparándose) y revisar en el servidor Syslog que el mensaje llegó con severidad correcta.

## Entregable

**Un solo archivo: el `.pkt` completo**, con las correcciones (sección "Antes de empezar") y las 4 partes de seguridad (S.1-S.4) implementadas en los 6 routers y los 3 switches. No se piden capturas ni documento aparte — la evaluación se hace abriendo el `.pkt` directamente y revisando la configuración real de cada dispositivo (`show running-config`, `show ip route`, `show port-security`, `show logging`, etc.), no capturas de pantalla que el estudiante eligió mostrar.

## Criterios de evaluación (ponderación por definir)

Se verifica revisando la configuración de cada dispositivo dentro del propio `.pkt` entregado (no capturas):

| Criterio | Cómo se verifica en el .pkt | Peso sugerido |
|---|---|---|
| Topología base (routing+VLANs) funcionando sin las 3 fallas originales | `show ip route` en los 6 routers, `show vlan` en los switches | 25% |
| S.1 SSH/AAA en los 9 dispositivos | `show running-config` — `transport input ssh`, sin `telnet`; conexión SSH real entre dos dispositivos | 20% |
| S.2 ACL de mínimo privilegio, verificada en ambos sentidos | `show access-lists`, `show ip interface g0/0/1.2` (ACL aplicada); ping real GrupoB→Web (pasa) y GrupoB→LAN2 (bloqueado) | 25% |
| S.3 Port security verificado | `show port-security interface` en SW-1/SW-2 — estado `secure-up`, MAC aprendida | 15% |
| S.4 Syslog centralizado con evento real capturado | `show logging` en los routers + mensajes reales recibidos en el servidor Syslog de LAN4 | 15% |

## Referencias

- Taller de Routing original — Ing. Rodolfo Cañas Cervantes (base de la topología, VLSM y routing estático).
- Cisco: [IOS Security Command Reference](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/security/command/sec-cr-book.html) — ACLs, AAA, port security.
- Cisco: [Configuring Syslog](https://www.cisco.com/c/en/us/support/docs/ip/simple-network-management-protocol-snmp/13608-21.html).
