# Laboratorio 4: Hardening de dispositivos de red

**Curso:** Seguridad en Redes — Ingeniería de Sistemas
**Docente:** Ing. Rodolfo Cañas Cervantes — Universidad de la Costa (CUC) · 2026-2
**Unidad · Actividad · Ponderación:** por definir · semana por definir
**Modalidad:** Cisco Packet Tracer 8.x, en aula · equipos de máximo 2 personas · máximo 2 horas

## Introducción

Recibes una red que funciona: los equipos se ven, las VLAN responden y los usuarios llegan a sus servicios. Nadie la ha asegurado. Tu equipo debe auditarla, endurecerla y demostrar, con evidencia, que cada falla quedó corregida.

Este laboratorio no construye una red desde cero: parte de una red ya armada y configurada de forma insegura. El trabajo es encontrar las fallas a partir de sus síntomas, corregirlas en los dispositivos y dejar pruebas de cada corrección.

> **Solo laboratorio:** todas las credenciales que aparecen en la configuración inicial son ficticias. No reutilices ninguna clave real.

## Parte A — Escenario y topología

Una oficina ficticia tiene un router (R1), dos switches (SW1 y SW2), tres VLAN de uso (ADMIN, USUARIOS y SERVIDORES) y una VLAN de gestión. Los switches y el router ya tienen configuración, pero no está endurecida.

**Punto de partida:** el archivo `lab04-inicial.pkt` que entrega el docente. Contiene la topología y la configuración inicial. El `.pkt` lo arma el docente; ustedes trabajan sobre ese archivo.

Figura 1 (en la versión HTML): topología con R1, SW1, SW2, PC-ADM, PC-U1, PC-U2 y SRV-01.

### Direccionamiento del estado inicial

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

## Parte B — Síntomas y objetivos

### Síntomas del estado inicial

Un auditor de la oficina reporta lo siguiente. Cada síntoma corresponde a una falla de seguridad que deben encontrar y corregir.

1. Al capturar el tráfico de administración de un switch se leen usuario y clave del administrador en texto claro.
2. Al revisar la configuración en ejecución de R1, las contraseñas aparecen legibles.
3. Un atacante puede intentar adivinar la clave de acceso remoto sin ningún límite de intentos.
4. Un equipo conectado a un puerto sin usar de SW2 llega a la misma red de gestión que los administradores.
5. Cualquier equipo conectado a un puerto de usuario puede introducir otro equipo o switch sin que el puerto reaccione.
6. Un equipo conectado a un puerto de acceso puede enviar BPDU y alterar el árbol de expansión sin que el switch lo bloquee.
7. Un vecino en el mismo segmento ve en la tabla de vecinos el modelo y la versión de cada equipo.
8. Cualquier PC de la red, incluida la de VLAN 20, puede abrir sesión de administración en los equipos.

### Dónde mirar

- La **configuración en ejecución** de cada dispositivo (R1, SW1 y SW2): revisa cada línea de acceso, cada contraseña y cada interfaz.
- La **tabla de VLAN** y el **estado de las interfaces** de cada switch: qué VLAN usa cada puerto y cuáles están activos sin uso.
- El **modo Simulation** de Packet Tracer: observa qué paquetes viajan, en qué VLAN y en qué orden.
- Las **pruebas desde los PC**: desde PC-U1 y desde PC-ADM, intenta administrar R1, SW1 y SW2.

### Objetivos medibles

Al terminar, el equipo debe cumplir los ocho objetivos siguientes. Cada uno se demuestra con la evidencia indicada.

| # | Objetivo | Cómo se demuestra |
|---|---|---|
| O1 | Gestión remota cifrada: los tres equipos aceptan administración solo por SSH y Telnet queda inhabilitado. | Sesión SSH exitosa desde PC-ADM; intento de Telnet rechazado; configuración de las líneas de acceso. |
| O2 | Credenciales protegidas: ninguna contraseña legible en la configuración en ejecución, y existe una contraseña de privilegio protegida. | `show running-config` sin contraseñas en texto claro. |
| O3 | Protección contra fuerza bruta: tres intentos fallidos bloquean el acceso durante un tiempo que el equipo define y documenta. | Captura de los tres intentos fallidos y del bloqueo. |
| O4 | Capa 2 endurecida: la VLAN nativa y la de gestión dejan de ser la VLAN 1, y los puertos sin uso quedan apagados y aislados. | `show vlan brief`, estado de interfaces y prueba de gestión desde PC-ADM. |
| O5 | Control de puertos de acceso: cada puerto de usuario acepta solo la MAC aprendida y se bloquea ante otra MAC. | Prueba de cambio de equipo en un puerto y captura del puerto bloqueado. |
| O6 | Árbol de expansión protegido: los puertos de acceso pasan a reenvío de inmediato y se apagan si reciben BPDU. | Estado de los puertos de acceso en la salida de árbol de expansión. |
| O7 | Gestión limitada: solo PC-ADM (VLAN 10) puede administrar los equipos; PC-U1 y PC-U2 son rechazados. | Intento desde PC-U1 rechazado y sesión desde PC-ADM aceptada. |
| O8 | Superficie reducida: el protocolo de descubrimiento de vecinos queda desactivado en los equipos. | Salida que muestra el protocolo desactivado y ausencia de vecinos en PC-U1. |

## Parte C — Entregables y evidencia

### Entregables (una entrega por equipo, por Teams)

1. **Archivo `.pkt` final** del equipo, con el nombre `EQUIPO-lab04.pkt`.
2. **Carpeta de capturas** (PNG o JPG), con la evidencia de la Parte D.
3. **`manifest.md`** con la tabla objetivo-captura-comando, las salidas `show` solicitadas y la justificación (máximo 300 palabras).

Cada integrante responde en aula una pregunta al azar sobre el trabajo del equipo (criterio individual de la rúbrica).

### Evidencia exigida

- Al menos **una captura por objetivo** (O1 a O8). En O1, O2, O5 y O7, incluye una captura **antes** y otra **después** del cambio.
- Cada captura debe mostrar **la hora del sistema** y **el nombre del dispositivo** en el prompt o en la ventana activa.
- En `manifest.md`, pega la salida de cada comando `show` que uses como prueba. No basta con decir que algo "quedó bien".
- La justificación (máximo 300 palabras) explica qué falla encontraron primero, por qué es un riesgo y cómo la corrigieron. No copies la configuración.

## Parte D — Reglas y rúbrica

### Reglas

- Equipos de **máximo 2 personas**. Máximo **2 horas** en aula.
- Trabajo **100 % dentro de Packet Tracer 8.x**. Sin Internet y sin herramientas externas.
- Puedes consultar la ayuda incluida en Packet Tracer.
- Cualquier cambio en un equipo debe quedar anotado en `manifest.md`.
- No cambies el direccionamiento de los PC ni del servidor sin anotarlo; si lo haces, debes justificarlo.

### Rúbrica

Ponderación y semana por definir. Cada criterio grupal vale hasta 1,0 y se evalúa con cuatro niveles.

| Criterio | 1,0 | 0,75 | 0,5 | 0 |
|---|---|---|---|---|
| C1. Gestión remota segura (O1, O3, O7) | SSH funciona, Telnet inhabilitado, límite de intentos y acceso restringido a la VLAN de gestión, todo verificado | Tres de las cuatro partes verificadas | Dos de las cuatro partes verificadas | Una o ninguna verificada |
| C2. Credenciales y autenticación (O2) | Ninguna contraseña en claro y contraseña de privilegio protegida, verificadas en la configuración | Una contraseña en claro restante | Contraseña de privilegio protegida pero otras en claro | Sin cambios |
| C3. Capa 2: VLAN y puertos (O4, O5) | VLAN nativa y de gestión fuera de VLAN 1, puertos sin uso apagados, y bloqueo por MAC demostrado | Una de las tres partes incompleta | Dos de las tres partes incompletas | Sin cambios |
| C4. Árbol de expansión y superficie (O6, O8) | PortFast y protección ante BPDU en puertos de acceso, y protocolo de vecinos desactivado, verificados | Una de las tres partes incompleta | Dos de las tres partes incompletas | Sin cambios |
| C5. Evidencia y documentación | Una captura por objetivo con hora y nombre visibles, manifest completo y justificación clara | Una captura o salida faltante | Evidencia parcial o sin hora | Sin evidencia |
| Individual: pregunta al azar por integrante | Respuesta técnica correcta y justificada sobre el trabajo del equipo | Respuesta correcta sin justificación | Respuesta parcial | No responde o incorrecta |

## Checklist de avance

- [ ] Encontré las fallas a partir de los síntomas (Parte B).
- [ ] O1: gestión por SSH funcionando y Telnet inhabilitado.
- [ ] O2: sin contraseñas en claro.
- [ ] O3: bloqueo de fuerza bruta configurado y probado.
- [ ] O4: VLAN nativa y de gestión fuera de VLAN 1; puertos sin uso apagados.
- [ ] O5: control de puertos de acceso probado.
- [ ] O6 y O8: árbol de expansión protegido y vecinos desactivados.
- [ ] O7: gestión restringida a VLAN 10 y probada desde PC-U1.
- [ ] Capturas con hora y nombre visibles; `manifest.md` con justificación de 300 palabras o menos.

## Referencias

- Cisco: [IOS Security Command Reference](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/security/command/sec-cr-book.html) — ACLs, AAA, control de acceso.
- Cisco Packet Tracer 8.x: ayuda incluida en la aplicación (menú Help).
