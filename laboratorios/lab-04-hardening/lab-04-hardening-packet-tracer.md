# Laboratorio 4: Hardening de dispositivos de red

**Curso:** Seguridad en Redes — Ingeniería de Sistemas
**Docente:** Ing. Rodolfo Cañas Cervantes — Universidad de la Costa (CUC) · 2026-2
**Actividad individual · 10 %** · corte y semana por definir
**Modalidad:** Cisco Packet Tracer 8.x, en aula · guiado, paso a paso con comandos · individual · máximo 2 horas

## Introducción

Recibes una red que funciona: los equipos se ven, las VLAN responden y los usuarios llegan a sus servicios. Nadie la ha asegurado. Tu trabajo es aplicar los controles de hardening sobre R1, SW1 y SW2, verificar cada uno con comandos `show` y dejar evidencia propia de que quedó aplicado.

Cada parte indica qué buscas y por qué, los comandos IOS para cada equipo, cómo verificar el resultado y qué debes ver. Sigue las partes en orden: las primeras preparan el acceso que usan las siguientes.

> **Actividad individual · máximo 2 horas · aula.** Todo se resuelve dentro de Cisco Packet Tracer 8.x, sin Internet ni herramientas externas.

> **Solo laboratorio:** todas las credenciales de este laboratorio son ficticias y de práctica. No reutilices ninguna clave real.

## Escenario y direccionamiento

Una oficina ficticia tiene un router (R1), dos switches (SW1 y SW2), tres VLAN de uso (ADMIN 10, USUARIOS 20, SERVIDORES 30) y la VLAN 1 usada hoy como nativa y de gestión. Los equipos ya tienen configuración, pero no está endurecida.

**Punto de partida:** el archivo `lab04-inicial.pkt` que entrega el docente. Trabajas sobre ese archivo; no lo reconstruyas desde cero.

| Dispositivo | Interfaz | VLAN | IP / máscara | Gateway |
|---|---|---|---|---|
| R1 | g0/0.1 | 1 (nativa) | 192.168.1.1 / 24 | — |
| R1 | g0/0.10 | 10 | 192.168.10.1 / 24 | — |
| R1 | g0/0.20 | 20 | 192.168.20.1 / 24 | — |
| R1 | g0/0.30 | 30 | 192.168.30.1 / 24 | — |
| SW1 | VLAN 1 (SVI) | 1 | 192.168.1.2 / 24 | 192.168.1.1 |
| SW2 | VLAN 1 (SVI) | 1 | 192.168.1.3 / 24 | 192.168.1.1 |
| PC-ADM | Ethernet | 10 | 192.168.10.10 / 24 | 192.168.10.1 |
| PC-U1 | Ethernet | 20 | 192.168.20.11 / 24 | 192.168.20.1 |
| PC-U2 | Ethernet | 20 | 192.168.20.12 / 24 | 192.168.20.1 |
| SRV-01 | Ethernet | 30 | 192.168.30.10 / 24 | 192.168.30.1 |

**Puertos en uso:** SW1 `f0/1` hacia R1, `f0/2` hacia SW2, `f0/3` PC-ADM, `f0/4` SRV-01. SW2 `f0/1` hacia SW1, `f0/2` PC-U1, `f0/3` PC-U2. Los demás puertos de SW1 (`f0/5` a `f0/24`) y de SW2 (`f0/4` a `f0/24`) no tienen equipo.

**Dónde ejecutar cada bloque:** los bloques de comandos son para el CLI de cada equipo. Para los PC usa **Desktop > Command Prompt** (pruebas con `ping`, `ssh` y `telnet`).

## Partes del laboratorio

> **Aviso:** Los comandos fueron preparados para Packet Tracer 8.x. Si tu versión rechaza alguno, anota el error exacto en `manifest.md` y continúa con el siguiente paso.

Convenciones:

- Cada bloque de código tiene el botón **Copiar**. Pégalo en el CLI del equipo indicado, en modo privilegiado (`enable`).
- `wr` guarda la configuración en la memoria de arranque. Ejecútalo al final de cada parte.
- Las partes no están en el orden de la numeración de objetivos O1 a O8: el orden sigue la dependencia técnica (primero el acceso remoto, luego la VLAN de gestión, luego el control de puertos).
- Cada cambio, con su comando, va a `manifest.md`.

| Parte | Objetivo | Qué demuestra la evidencia |
|---|---|---|
| 0 | Punto de partida | Estado inicial antes de tocar nada |
| 1 | O1 | SSH activo y Telnet rechazado |
| 2 | O2 | Ninguna contraseña en claro; contraseña de privilegio protegida |
| 3 | O3 | Bloqueo tras tres intentos fallidos |
| 4 | O4 | VLAN 99 nativa y de gestión; VLAN 1 retirada |
| 5 | O4 | Puertos sin uso apagados y aislados en VLAN 999 |
| 6 | O5 | Port security con cambio de equipo bloqueado |
| 7 | O6 | PortFast y BPDU guard en puertos de acceso |
| 8 | O8 | CDP desactivado |
| 9 | O7 | Gestión solo desde VLAN 10 |

## Parte 0 · Punto de partida y evidencia «antes»

**Qué buscas y por qué:** confirmar que el `.pkt` tiene la configuración inicial y guardar la evidencia «antes» de cualquier cambio. Sin esa foto no puedes demostrar después qué cambió. Un auditor reportaría que, hoy, el tráfico de administración viaja en claro y que cualquiera puede conectarse.

### Comandos

**R1**

```
enable
show running-config
```

**SW1**

```
enable
show running-config
show vlan brief
show interfaces status
show cdp
```

**SW2**

```
enable
show running-config
show vlan brief
show interfaces status
show cdp
```

**PC-ADM** (Desktop > Command Prompt)

```
ping 192.168.1.2
```

### Verificación

- En R1, `show running-config` muestra `transport input telnet` y `cdp run`.
- En SW1 y SW2, `show cdp` indica que CDP está habilitado (no dice `CDP is not enabled`).
- En `show vlan brief`, las VLAN 10, 20 y 30 existen; la VLAN 99 y la VLAN 999 todavía no.
- El `ping` desde PC-ADM a 192.168.1.2 responde.

### Resultado esperado

- La configuración inicial está visible en los tres equipos y coincide con lo descrito arriba.
- Tienes una captura «antes» por equipo, con la hora del sistema y el nombre del dispositivo visibles.

> **Si ves que `show running-config` de R1 no tiene `transport input telnet`:** el `.pkt` no es la configuración inicial. Avísale al docente antes de seguir.

## Parte 1 · O1: gestión remota cifrada (SSH)

**Qué buscas y por qué:** Telnet envía usuario y clave en texto plano; cualquiera que capture el tráfico de administración los lee. SSH los cifra. Objetivo: los tres equipos aceptan administración solo por SSH.

Haz esta parte desde la consola o por Telnet desde PC-ADM. Al poner `transport input ssh` se elimina Telnet, así que guarda con `wr` antes de cerrar la sesión.

### Comandos

**R1**

```
enable
configure terminal
ip domain-name lab04.local
crypto key generate rsa modulus 1024
ip ssh version 2
line vty 0 4
 transport input ssh
end
wr
```

**SW1**

```
enable
configure terminal
ip domain-name lab04.local
crypto key generate rsa modulus 1024
ip ssh version 2
line vty 0 15
 transport input ssh
end
wr
```

**SW2**

```
enable
configure terminal
ip domain-name lab04.local
crypto key generate rsa modulus 1024
ip ssh version 2
line vty 0 15
 transport input ssh
end
wr
```

> **Nota:** si Packet Tracer pide el tamaño de la clave RSA, escribe `1024`.

### Verificación

- En R1, SW1 y SW2: `show ip ssh` (debe indicar SSH v2 habilitado).
- En R1, SW1 y SW2: `show running-config | section line vty` (debe aparecer `transport input ssh`, sin `telnet`).
- Desde PC-ADM: `ssh -l admin 192.168.1.1` pide clave y entra con el usuario `admin` y la clave de la configuración inicial. Repite con `192.168.1.2` y `192.168.1.3`.
- Desde PC-ADM: `telnet 192.168.1.1` debe ser rechazado.

### Resultado esperado

- SSH entra en los tres equipos; Telnet no conecta.

> **Si `telnet` todavía conecta:** revisa que la línea `transport input ssh` esté en el bloque `line vty` de ese equipo.
>
> **Si `ssh` responde que no hay clave RSA:** revisa que `ip domain-name lab04.local` se aplicó antes de `crypto key generate rsa`.

## Parte 2 · O2: credenciales protegidas

**Qué buscas y por qué:** en la configuración en ejecución, las contraseñas aparecen legibles (`enable password` y `username ... password`). Un atacante con acceso a la configuración las lee directamente. Objetivo: ninguna contraseña en claro y una contraseña de privilegio protegida (`enable secret`).

Ejecuta esta parte por consola, o con una sesión SSH abierta antes de borrar el usuario `admin`. Si te quedas fuera, entra por consola con la nueva clave.

### Comandos

**R1**

```
enable
configure terminal
no enable password
enable secret Lab4-Priv!2026
no username admin
no username operador
username admin privilege 15 secret Lab4-Admin!2026
username operador privilege 1 secret Lab4-Oper!2026
service password-encryption
end
wr
```

**SW1**

```
enable
configure terminal
no enable password
enable secret Lab4-Priv!2026
no username admin
username admin privilege 15 secret Lab4-Admin!2026
service password-encryption
end
wr
```

**SW2**

```
enable
configure terminal
no enable password
enable secret Lab4-Priv!2026
no username admin
username admin privilege 15 secret Lab4-Admin!2026
service password-encryption
end
wr
```

### Verificación

- En R1, SW1 y SW2: `show running-config`. No debe aparecer ninguna clave legible en `enable password` ni en `username ... password`. Debe aparecer `enable secret` y `username ... secret`, con un valor cifrado (no la clave escrita).
- Desde PC-ADM: `ssh -l admin 192.168.1.1` con la clave **nueva** entra; con la clave **inicial** debe ser rechazado.

### Resultado esperado

- `show running-config` no muestra claves en texto claro en los tres equipos.
- Las credenciales de práctica (`Lab4-...`) son solo de este laboratorio.

> **Si ves `password` seguido de una clave legible:** esa línea sigue en la configuración; repite el bloque del equipo correspondiente.
>
> **Si `enable` no acepta la clave nueva:** escribe `Lab4-Priv!2026` completa, con el signo de admiración, tal como aparece en el bloque.

## Parte 3 · O3: protección contra fuerza bruta

**Qué buscas y por qué:** un atacante puede probar claves sin límite contra SSH. Objetivo: tres intentos fallidos bloquean el acceso durante un tiempo que tú defines y documentas.

El comando de ejemplo bloquea durante 120 segundos tras tres intentos fallidos dentro de 60 segundos. Puedes elegir otros valores; anótalos en `manifest.md`.

### Comandos

**R1**

```
enable
configure terminal
login block-for 120 attempts 3 within 60
end
wr
```

**SW1**

```
enable
configure terminal
login block-for 120 attempts 3 within 60
end
wr
```

**SW2**

```
enable
configure terminal
login block-for 120 attempts 3 within 60
end
wr
```

### Verificación

- En R1: `show login` debe mostrar el bloqueo configurado con 3 intentos.
- Desde PC-ADM: `ssh -l admin 192.168.1.1` con clave incorrecta, tres veces seguidas. Luego intenta con la clave correcta: debe ser rechazado mientras dure el bloqueo.
- Captura los tres intentos fallidos y el rechazo posterior, con hora y nombre visibles.

### Resultado esperado

- Tras tres fallos, el acceso queda bloqueado durante el tiempo configurado.

> **Si el bloqueo no aparece en `show login`:** revisa que el comando quedó en modo de configuración global y que se ejecutó `wr`.

## Parte 4 · O4: VLAN nativa y de gestión fuera de VLAN 1

**Qué buscas y por qué:** la VLAN 1 es la nativa del trunk y la de gestión. Tráfico sin etiqueta viaja por VLAN 1, y un atacante que conoce la nativa puede inyectar tráfico en otras VLAN (VLAN hopping). Objetivo: la VLAN nativa y la de gestión dejan de ser la VLAN 1.

Esta parte tiene cuatro pasos y el orden importa: el paso 4.3 se hace por **consola** de SW1 y SW2, porque cambia la nativa y corta la gestión por 192.168.1.x. El paso 4.4 se hace por SSH desde PC-ADM a 192.168.10.1, que no depende de la VLAN 1.

### Paso 4.1 · R1 (por SSH desde PC-ADM a 192.168.10.1, o por consola)

Crea la subinterfaz de gestión en VLAN 99, todavía sin nativa.

```
enable
configure terminal
interface GigabitEthernet0/0.99
 encapsulation dot1Q 99
 ip address 192.168.99.1 255.255.255.0
end
wr
```

### Paso 4.2 · SW1 y SW2 (por SSH desde PC-ADM a 192.168.1.2 y 192.168.1.3)

Crea la VLAN 99 y la SVI de gestión; sin cambiar la nativa todavía.

**SW1**

```
enable
configure terminal
vlan 99
 name GESTION
interface vlan 99
 ip address 192.168.99.2 255.255.255.0
 no shutdown
exit
ip default-gateway 192.168.99.1
end
wr
```

**SW2**

```
enable
configure terminal
vlan 99
 name GESTION
interface vlan 99
 ip address 192.168.99.3 255.255.255.0
 no shutdown
exit
ip default-gateway 192.168.99.1
end
wr
```

### Paso 4.3 · SW1 y SW2 (por consola)

Cambia la nativa de los trunks a 99 y apaga la SVI de VLAN 1.

**SW1**

```
enable
configure terminal
interface f0/1
 switchport trunk native vlan 99
interface f0/2
 switchport trunk native vlan 99
exit
interface vlan 1
 no ip address
 shutdown
end
wr
```

**SW2**

```
enable
configure terminal
interface f0/1
 switchport trunk native vlan 99
exit
interface vlan 1
 no ip address
 shutdown
end
wr
```

> **Mensajes `native VLAN mismatch` entre este paso y el 4.4:** son esperados. Desaparecen cuando R1 queda con la nativa 99 en el paso 4.4.

### Paso 4.4 · R1 (por SSH desde PC-ADM a 192.168.10.1)

Retira la subinterfaz de VLAN 1 y deja la VLAN 99 como nativa.

```
enable
configure terminal
no interface GigabitEthernet0/0.1
no interface GigabitEthernet0/0.99
interface GigabitEthernet0/0.99
 encapsulation dot1Q 99 native
 ip address 192.168.99.1 255.255.255.0
end
wr
```

### Verificación

- En SW1 y SW2: `show vlan brief`. Debe existir la VLAN 99 (GESTION) y la VLAN 1 no debe tener puertos de usuario.
- En SW1: `show interfaces trunk`. Los puertos `f0/1` y `f0/2` deben mostrar native 99.
- En SW2: `show interfaces trunk`. El puerto `f0/1` debe mostrar native 99.
- Desde PC-ADM: `ssh -l admin 192.168.99.1`, `ssh -l admin 192.168.99.2` y `ssh -l admin 192.168.99.3` deben entrar.

### Resultado esperado

- Ambos extremos de cada trunk usan native 99.
- La gestión responde en 192.168.99.1, 192.168.99.2 y 192.168.99.3.
- La VLAN 1 ya no es nativa ni de gestión.

> **Si ves `native VLAN mismatch` después del paso 4.4:** revisa que la nativa sea 99 en R1 (`GigabitEthernet0/0.99`), en SW1 `f0/1` y `f0/2`, y en SW2 `f0/1`.
>
> **Si no llegas a 192.168.99.2 o 192.168.99.3 después del paso 4.2:** desde PC-ADM haz `ping 192.168.99.2` (o `.3`) y revisa que el paso 4.1 y el paso 4.2 quedaron aplicados.
>
> **Si no llegas a 192.168.99.1 desde PC-ADM:** conéctate por consola a R1 y revisa `show running-config` de la subinterfaz `GigabitEthernet0/0.99`.

## Parte 5 · O4: puertos sin uso apagados y aislados

**Qué buscas y por qué:** un equipo conectado a un puerto sin usar de un switch llega a la red donde están los administradores. Objetivo: los puertos sin uso quedan apagados y asignados a una VLAN de descarte (VLAN 999).

### Comandos

**R1**

No aplica: esta parte es solo de los switches.

**SW1** (puertos `f0/5` a `f0/24`)

```
enable
configure terminal
vlan 999
 name BLACKHOLE
interface range f0/5-24
 switchport mode access
 switchport access vlan 999
 shutdown
end
wr
```

**SW2** (puertos `f0/4` a `f0/24`)

```
enable
configure terminal
vlan 999
 name BLACKHOLE
interface range f0/4-24
 switchport mode access
 switchport access vlan 999
 shutdown
end
wr
```

### Verificación

- En SW1 y SW2: `show interfaces status`. Los puertos sin uso deben estar `disabled`.
- En SW1 y SW2: `show vlan brief`. La VLAN 999 (BLACKHOLE) existe y lista los puertos sin uso.

### Resultado esperado

- Ningún puerto sin uso está activo; todos aparecen `disabled`.

> **Si ves puertos sin uso en `notconnect` en vez de `disabled`:** el `shutdown` no se aplicó. Revisa que el rango sea `f0/5-24` en SW1 y `f0/4-24` en SW2.

## Parte 6 · O5: control de puertos de acceso (port security)

**Qué buscas y por qué:** cualquier equipo conectado a un puerto de usuario puede introducir otro equipo o un switch sin que el puerto reaccione. Objetivo: cada puerto de acceso en uso aprende una sola MAC y se bloquea ante otra.

### Comandos

**R1**

No aplica: esta parte es solo de los switches.

**SW1** (puertos de acceso en uso `f0/3` y `f0/4`)

```
enable
configure terminal
interface range f0/3-4
 switchport mode access
 switchport port-security
 switchport port-security maximum 1
 switchport port-security mac-address sticky
 switchport port-security violation shutdown
end
wr
```

**SW2** (puertos de acceso en uso `f0/2` y `f0/3`)

```
enable
configure terminal
interface range f0/2-3
 switchport mode access
 switchport port-security
 switchport port-security maximum 1
 switchport port-security mac-address sticky
 switchport port-security violation shutdown
end
wr
```

### Verificación

- Antes de la prueba, desde PC-U1 haz `ping 192.168.20.1` para que el puerto aprenda su MAC.
- En SW1: `show port-security interface f0/3`. Debe mostrar `Secure-up` y máximo 1.
- En SW2: `show port-security interface f0/2`. Debe mostrar `Secure-up` y máximo 1.
- **Prueba de cambio de equipo (captura «antes» y «después»):** retira PC-U1 del puerto `f0/2` de SW2 y conecta ahí PC-U2 (que estaba en `f0/3`). Luego ejecuta `show port-security interface f0/2`. El puerto debe pasar a `err-disabled`.

### Recuperación del puerto (paso de la prueba)

Retira PC-U2, vuelve a conectar PC-U1 en `f0/2` y reinicia el puerto:

**SW2**

```
enable
configure terminal
interface f0/2
 shutdown
 no shutdown
end
wr
```

### Resultado esperado

- Con el equipo correcto, el puerto está `Secure-up`.
- Con otro equipo, el puerto queda `err-disabled` y la captura lo muestra.

> **Si el puerto no se bloquea con PC-U2:** revisa que el `ping` de PC-U1 se hizo antes de cambiar el cable; sin tráfico, el puerto no aprende la MAC.
>
> **Si el puerto queda `err-disabled` con PC-U1 conectado:** repite la recuperación de este paso (`shutdown` y `no shutdown` en `f0/2`).

## Parte 7 · O6: árbol de expansión protegido

**Qué buscas y por qué:** un equipo conectado a un puerto de acceso puede enviar BPDU y alterar el árbol de expansión, con lo que puede desviar tráfico. Objetivo: los puertos de acceso pasan a reenvío de inmediato (PortFast) y se apagan si reciben BPDU (BPDU guard).

PortFast y BPDU guard solo van en puertos de acceso, nunca en los trunks (`f0/1` y `f0/2` de SW1, `f0/1` de SW2).

### Comandos

**R1**

No aplica: esta parte es solo de los switches.

**SW1** (puertos de acceso en uso `f0/3` y `f0/4`)

```
enable
configure terminal
interface range f0/3-4
 spanning-tree portfast
 spanning-tree bpduguard enable
end
wr
```

**SW2** (puertos de acceso en uso `f0/2` y `f0/3`)

```
enable
configure terminal
interface range f0/2-3
 spanning-tree portfast
 spanning-tree bpduguard enable
end
wr
```

### Verificación

- En SW1: `show spanning-tree interface f0/3 detail` y `show spanning-tree interface f0/4 detail`. PortFast y BPDU guard deben aparecer habilitados.
- En SW2: `show spanning-tree interface f0/2 detail` y `show spanning-tree interface f0/3 detail`. Lo mismo.

### Resultado esperado

- Los cuatro puertos de acceso muestran PortFast y BPDU guard habilitados.

> **Si `show spanning-tree` no muestra PortFast en un puerto:** revisa que el bloque se aplicó en el rango de acceso y no en el trunk.

## Parte 8 · O8: protocolo de vecinos (CDP) desactivado

**Qué buscas y por qué:** CDP anuncia a cualquier vecino en el mismo segmento el modelo y la versión de cada equipo, que sirve a un atacante para elegir sus ataques. Objetivo: CDP queda desactivado en los tres equipos.

### Comandos

**R1**

```
enable
configure terminal
no cdp run
end
wr
```

**SW1**

```
enable
configure terminal
no cdp run
end
wr
```

**SW2**

```
enable
configure terminal
no cdp run
end
wr
```

### Verificación

- En R1, SW1 y SW2: `show cdp`. Debe indicar `CDP is not enabled`.

PC-U1 no tiene CLI de switch, así que la prueba de «sin vecinos» se hace con `show cdp` en cada equipo de red.

### Resultado esperado

- Los tres equipos muestran `CDP is not enabled`.

> **Si `show cdp` sigue mostrando CDP activo:** el bloque no se ejecutó en ese equipo; repítelo y ejecuta `wr`.

## Parte 9 · O7: gestión limitada a VLAN 10

**Qué buscas y por qué:** hoy cualquier PC de la red, incluida la de VLAN 20, puede abrir sesión de administración en los equipos. Objetivo: solo PC-ADM (VLAN 10, red 192.168.10.0/24) puede administrar R1, SW1 y SW2. PC-U1 y PC-U2 son rechazados.

Esta parte va al final porque usa las IP de gestión de la Parte 4.

### Comandos

**R1**

```
enable
configure terminal
ip access-list standard ACL-GESTION
 permit 192.168.10.0 0.0.0.255
 deny any
exit
line vty 0 4
 access-class ACL-GESTION in
end
wr
```

**SW1**

```
enable
configure terminal
ip access-list standard ACL-GESTION
 permit 192.168.10.0 0.0.0.255
 deny any
exit
line vty 0 15
 access-class ACL-GESTION in
end
wr
```

**SW2**

```
enable
configure terminal
ip access-list standard ACL-GESTION
 permit 192.168.10.0 0.0.0.255
 deny any
exit
line vty 0 15
 access-class ACL-GESTION in
end
wr
```

> **Diferencia clave:** la ACL de línea VTY se aplica con `access-class`, no con `access-group` sobre la interfaz.

### Verificación

- En R1, SW1 y SW2: `show running-config | section line vty`. Debe aparecer `access-class ACL-GESTION in`.
- Desde PC-ADM: `ssh -l admin 192.168.99.1` entra (y lo mismo con `192.168.99.2` y `192.168.99.3`).
- Desde PC-U1: `ssh -l admin 192.168.99.1` debe ser rechazado. Repite con `192.168.99.2` y `192.168.99.3`.
- Captura: la sesión aceptada desde PC-ADM y el rechazo desde PC-U1, con hora y nombre visibles.

### Resultado esperado

- PC-ADM administra los tres equipos; PC-U1 no puede conectarse a ninguno.

> **Si PC-ADM también queda rechazado:** revisa que la ACL permite `192.168.10.0 0.0.0.255` y que la PC tiene la IP 192.168.10.10.
>
> **Si PC-U1 todavía entra:** la ACL no está aplicada al bloque `line vty`; revisa que el comando sea `access-class`, no `access-group`.

## Entrega y evidencia

### Entregables (una entrega por estudiante, por Teams)

Cada estudiante entrega una carpeta `apellido-nombre/` con:

1. **Archivo `.pkt` final**, con el nombre `apellido-nombre-lab04.pkt`.
2. **Carpeta de capturas** (PNG o JPG), con la evidencia de las partes.
3. **`manifest.md`** con la tabla objetivo-captura-comando, las salidas `show` solicitadas, los comandos que Packet Tracer rechazó (con el error exacto) y la justificación (máximo 300 palabras).

Cada estudiante responde en aula una pregunta al azar sobre su propio trabajo (criterio 5 de la rúbrica).

### Evidencia exigida

- Al menos **una captura por objetivo** (O1 a O8). En O1, O2, O5 y O7, incluye una captura **antes** y otra **después** del cambio.
- Cada captura debe mostrar **la hora del sistema** y **el nombre del dispositivo** en el prompt o en la ventana activa.
- En `manifest.md`, pega la salida de cada comando `show` que uses como prueba. No basta con decir que algo «quedó bien».
- La justificación (máximo 300 palabras) explica, con tus palabras, el riesgo que mitiga cada control que aplicaste al menos en O1, O4 y O5, y qué te mostró su verificación. No copies comandos ni configuración.

## Reglas y rúbrica

### Reglas

- Actividad **individual**. Máximo **2 horas** en aula.
- Trabajo **100 % dentro de Packet Tracer 8.x**. Sin Internet y sin herramientas externas.
- Puedes consultar la ayuda incluida en Packet Tracer.
- Cualquier cambio en un equipo debe quedar anotado en `manifest.md`, con el comando que lo aplicó.
- No cambies el direccionamiento de los PC ni del servidor. Si lo haces, debes anotarlo y justificarlo.

### Rúbrica

Cinco criterios, cada uno hasta 1,0 (total 5,0), evaluados de forma individual con cuatro niveles. Corte y semana por definir.

Esta es una práctica guiada. La rúbrica evalúa que los controles quedaron **aplicados y verificados**, la **evidencia propia** y la **defensa individual**; no evalúa haber descubierto las fallas.

| Criterio | 1,0 | 0,75 | 0,5 | 0 |
|---|---|---|---|---|
| C1. Gestión remota segura (O1, O3, O7) | SSH funciona, Telnet inhabilitado, límite de intentos y acceso restringido a la VLAN de gestión, todo verificado | Tres de las cuatro partes verificadas | Dos de las cuatro partes verificadas | Una o ninguna verificada |
| C2. Credenciales y autenticación (O2) | Ninguna contraseña en claro y contraseña de privilegio protegida, verificadas en la configuración | Una contraseña en claro restante | Contraseña de privilegio protegida pero otras en claro | Sin cambios |
| C3. Capa 2: VLAN y puertos (O4, O5) | VLAN nativa y de gestión fuera de VLAN 1, puertos sin uso apagados, y bloqueo por MAC demostrado | Una de las tres partes incompleta | Dos de las tres partes incompletas | Sin cambios |
| C4. Árbol de expansión y superficie (O6, O8) | PortFast y protección ante BPDU en puertos de acceso, y CDP desactivado, verificados | Una de las tres partes incompleta | Dos de las tres partes incompletas | Sin cambios |
| C5. Evidencia y defensa individual | El `.pkt` reproduce los controles; una captura por objetivo con hora y nombre visibles; manifest completo; justificación clara; respuesta técnica correcta y justificada a la pregunta al azar | Una captura o salida faltante, o respuesta correcta sin justificación | Evidencia parcial o sin hora, o respuesta parcial | Sin evidencia, o no responde o responde incorrectamente |

## Checklist de avance

- [ ] Parte 0: evidencia «antes» de los tres equipos, con hora y nombre visibles.
- [ ] Partes 1 a 3 (O1, O2 y O3): SSH activo, Telnet inhabilitado, sin claves en claro y bloqueo por intentos verificados.
- [ ] Partes 4 y 5 (O4): VLAN 99 nativa y de gestión; VLAN 1 fuera; puertos sin uso apagados.
- [ ] Parte 6 (O5): port security probado con cambio de equipo.
- [ ] Partes 7 y 8 (O6 y O8): PortFast, BPDU guard y CDP desactivado verificados.
- [ ] Parte 9 (O7): gestión solo desde VLAN 10; rechazo desde PC-U1 probado.
- [ ] Capturas con hora y nombre visibles; `manifest.md` con salidas `show` y justificación de 300 palabras o menos.
- [ ] Carpeta `apellido-nombre/` completa: `.pkt`, capturas y `manifest.md`.

## Referencias

- Cisco: [IOS Security Command Reference](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/security/command/sec-cr-book.html): ACLs, AAA, control de acceso.
- Cisco Packet Tracer 8.x: ayuda incluida en la aplicación (menú Help).
