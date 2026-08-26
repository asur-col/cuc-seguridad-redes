# Laboratorio 2: Detección de Intrusos con Snort (IDS/IPS)

> **Unidad 1 · Actividad 2 · 10% de la nota final · Seguridad en Redes (CUC)**
> Versión ilustrada (con diagramas) disponible en [`lab-02-ids-ips-tryhackme.html`](lab-02-ids-ips-tryhackme.html) de esta misma carpeta. Este documento es la versión Markdown para lectura, copia de comandos y control de versiones.

Trabajo asíncrono en TryHackMe — complementa la clase de Firewalls de host e IDS/IPS.

## Objetivo — Qué vas a aprender

En clase viste la diferencia conceptual entre un **IDS** (detección pasiva, alerta después de que el tráfico ya pasó) y un **IPS** (prevención en línea, bloquea el tráfico antes de que llegue). Este laboratorio te pone a operar un IDS/IPS real — **Snort**, uno de los motores de detección más usados en la industria — sin necesidad de instalar nada en tu computador.

Vas a trabajar con los tres modos de Snort (sniffer, logger, NIDS), y vas a **escribir tus propias reglas de detección** — el corazón de cualquier IDS: una regla le dice al motor qué patrón de tráfico debe considerarse sospechoso.

## Concepto — IDS vs. IPS: el mismo motor, dos formas de actuar

Antes de entrar a la plataforma, ten clara esta diferencia — el laboratorio la va a poner en práctica:

- **IDS (detección pasiva, fuera de línea):** analiza una copia del tráfico (mirror/span) y genera una alerta — el paquete ya alcanzó su destino, la respuesta es posterior.
- **IPS (prevención activa, en línea):** se coloca directamente en el camino del flujo y bloquea el paquete malicioso antes de que llegue a su destino.
- Ambos trabajan con **firmas** (patrones conocidos) y **anomalías** (comportamiento inusual).

*(Diagrama comparativo disponible en la versión HTML — FIG 1.)*

> 💡 TIP — Snort puede operar en modo IDS (solo alerta, lo que vas a usar en este lab) o en modo IPS (`inline`, bloqueando activamente) — la plataforma del lab usa el modo IDS para que puedas ver las alertas sin arriesgar cortar tráfico legítimo por error mientras aprendes.

## Concepto — Anatomía de una regla Snort

Toda regla de Snort/Suricata sigue la misma estructura: una **acción**, el **tráfico** que debe igualar (protocolo, origen, dirección, destino) y unas **opciones** entre paréntesis que afinan la detección.

Regla de ejemplo (detecta un posible escaneo HTTP):

```
alert tcp any any -> $HOME_NET 80 (msg:"Posible escaneo HTTP"; flags:S; threshold:type threshold, track by_src, count 20, seconds 60; sid:1000001; rev:1;)
```

| Sección | Qué decide |
|---|---|
| `alert` (**acción**) | Qué hacer si coincide: `alert` / `drop` / `reject` / `pass` |
| `tcp` (**protocolo**) | `tcp` / `udp` / `icmp` / `ip` / `http` (capa de aplicación) |
| `any any` (**origen/puerto**) | IP y puerto de origen del tráfico a inspeccionar |
| `->` (**dirección**) | `->` unidireccional / `<>` bidireccional |
| `$HOME_NET 80` (**destino/puerto**) | Red/host y puerto de destino |
| `(msg:...; flags:...; threshold:...; sid:...; rev:...;)` (**opciones**) | `msg`: texto de la alerta · `flags`: banderas TCP a igualar (S=SYN) · `threshold`: umbral para no saturar de alertas · `sid`/`rev`: identificador único y versión de la regla |

**Lectura de la regla de ejemplo:** si llega tráfico TCP con bandera SYN hacia el puerto 80 de la red protegida, y esto ocurre 20+ veces en 60 segundos desde el mismo origen, generar una alerta (posible escaneo).

*(Diagrama de la anatomía completa disponible en la versión HTML — FIG 2.)*

No necesitas memorizar la sintaxis exacta — la sala te guía paso a paso para construir la tuya. Lo que sí debes entender es **qué decide cada sección**, porque eso es lo que vas a explicar en tu entregable.

## Previo — Requisitos antes de empezar

- Una cuenta gratuita en [tryhackme.com](https://tryhackme.com) (correo + contraseña, no pide tarjeta para las salas gratuitas).
- Navegador actualizado — la sala corre una máquina virtual dentro del navegador, no instalas nada en tu equipo.
- ~1.5 horas continuas (puedes pausar y retomar, TryHackMe guarda tu progreso en la cuenta).

> ⚠ ATENCIÓN — Esta actividad es **asíncrona**: no se hace en la sesión de clase de esta semana, tienes hasta la fecha límite que se anuncie en clase para completarla y subir el entregable.

## Parte A — Acceso a la sala (~10 min)

1. Entra a [`tryhackme.com/room/snort`](https://tryhackme.com/room/snort) — es la sala oficial "Snort", **gratuita** (no requiere suscripción).
2. Si no tienes cuenta, créala con tu correo institucional o personal (proceso de 1 minuto, sin tarjeta de crédito para el plan gratuito).
3. Haz clic en **"Start Room"** / **"Join Room"**. TryHackMe desplegará una máquina virtual Linux accesible desde el navegador (puede tardar 1-2 minutos en iniciar).
4. Confirma que tu usuario de TryHackMe queda visible en tu perfil — es lo primero que debe aparecer en tu captura de evidencia.

## Parte B — Recorrido de la sala (~70 min)

La sala está organizada en tareas progresivas. El orden exacto y el texto de cada pregunta son propios de la plataforma (no los reproducimos aquí — TryHackMe actualiza sus salas periódicamente), pero vas a pasar por estos bloques temáticos:

| Bloque | Qué vas a hacer | Por qué importa |
|---|---|---|
| Introducción a Snort | Contexto de qué es Snort y dónde se usa en la industria | Ubica la herramienta frente a lo visto en clase (NGFW/IDS/IPS conceptual) |
| Modo sniffer | Capturar tráfico crudo en tiempo real con Snort | Es la base de cualquier IDS: sin ver el tráfico no hay nada que analizar |
| Modo logger | Guardar el tráfico capturado en disco para análisis posterior | Equivalente a la evidencia forense que revisa un analista SOC |
| Modo NIDS (detección) | Activar el motor de reglas y ver alertas generadas en tiempo real | Este es el modo IDS real — el mismo del concepto anterior |
| Escritura de reglas | Construir tus propias reglas siguiendo la estructura de la sección anterior | Es la habilidad central: traducir "qué quiero detectar" en sintaxis de regla |
| Generador de tráfico | Ejecutar tráfico de prueba (incluido en la sala) contra tu propia regla | Verificas con tus propios ojos que la regla que escribiste sí dispara la alerta |

> 💡 TIP — Ve completando las preguntas de la sala a medida que avanzas — TryHackMe marca cada tarea con un check verde cuando la respuesta es correcta. Ese progreso es parte de tu evidencia.

> ☠ CRÍTICO — No copies ni compartas las respuestas exactas con tus compañeros. Cada quien debe generar su propia captura de progreso — se revisa que el **usuario de TryHackMe visible en la captura coincida contigo**.

## Parte C — Entregable (~10 min)

Un solo documento (PDF) con estas 4 evidencias, en este orden:

1. **Progreso de la sala:** captura de pantalla de la barra/lista de tareas de la sala "Snort" mostrando el avance completado, con tu usuario de TryHackMe visible en la esquina de la página.
2. **Tu regla:** captura del texto exacto de la regla Snort que construiste durante la sala (la sintaxis completa, tal como la escribiste).
3. **Verificación:** captura de la alerta generada por Snort cuando tu regla detectó el tráfico de prueba (salida de consola o de la interfaz de la sala mostrando la alerta).
4. **Explicación de 3-5 líneas:** en tus palabras, ¿qué patrón de tráfico detecta tu regla y por qué elegiste esas condiciones (protocolo, puerto, opciones)?

## Relación con la rúbrica (Actividad 2 · 10% Unidad 1)

| Criterio | Peso |
|---|---|
| Progreso de la sala completo con usuario visible | 25% |
| Regla propia con sintaxis correcta (acción/protocolo/direccionalidad/opciones) | 30% |
| Evidencia de la alerta disparada por la regla propia | 25% |
| Explicación técnica de la regla (3-5 líneas) | 20% |

## Solución de problemas

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| La VM del navegador no carga o queda en blanco | La sala tarda en desplegar el contenedor | Espera 2 minutos, recarga la página sin cerrar la sesión |
| No aparece el botón "Start Room" | No iniciaste sesión antes de abrir la sala | Inicia sesión en tryhackme.com primero, luego vuelve a abrir el enlace |
| Mi regla no genera ninguna alerta | El puerto/protocolo de la regla no coincide con el tráfico de prueba | Revisa cada sección de la anatomía de la regla contra el tráfico real que genera la sala |
| Se me acabó el tiempo de sesión de la VM | TryHackMe limita la sesión activa de la VM gratuita | Vuelve a iniciar la sala — tu progreso de preguntas respondidas queda guardado |

## Checklist antes de entregar

- [ ] Completé el progreso de la sala "Snort" y tomé la captura con mi usuario visible.
- [ ] Escribí mi propia regla siguiendo la estructura enseñada (no copié la de un compañero).
- [ ] Verifiqué que mi regla dispara una alerta real contra el tráfico de prueba de la sala.
- [ ] Redacté la explicación de 3-5 líneas relacionando mi regla con el concepto de anatomía de reglas.
- [ ] Armé el PDF único con las 4 evidencias en el orden pedido.

---
Seguridad en Redes · Universidad de la Costa (CUC) · Periodo 2026-2 · Ing. Rodolfo Cañas Cervantes
