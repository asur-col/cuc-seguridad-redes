# Análisis temático y de calidad — Seguridad en Redes 2026-2

**Universidad de la Costa (CUC) · Ing. Rodolfo Cañas Cervantes · Fase 1 (análisis)**
Fecha del corte: **domingo 4 de octubre de 2026** (último día de la Semana 9).

> Regla de oro: los títulos del calendario de `index.html` son oficiales y **no cambian**. Todas las mejoras propuestas van **dentro** de cada semana.
>
> **Alcance: solo material académico** (presentaciones, guiones, PDF, videos). Las actividades evaluables, sus ponderaciones y la columna "Actividad / Evaluación" del calendario quedan fuera del análisis y no se modifican. Cuando este documento dice "lab" de cierre, se refiere a la práctica demostrativa que muestra la presentación sobre la plataforma propia, no a una actividad calificada.

---

## 1. Estado del repositorio

### 1.1 Dónde estamos en el calendario

| Semana | Fechas | Estado del material | Comentario |
|---|---|---|---|
| 1–5 | 5 ago – 6 sep | Publicadas (formato corto) | Ya dictadas. |
| 6 | 7–13 sep | Repaso U1 / Parcial 1 | Sin presentación (no se necesita para el calendario, pero sí conviene un repaso). |
| 7–8 | 14–27 sep | Publicadas (formato 4×15 min) | Ya dictadas. |
| **9** | **28 sep – 4 oct (hoy)** | **NO publicada** | **Atrasada.** Monitoreo/SIEM. Es la prioridad n.º 1. |
| Receso | 5–11 oct | — | Ventana para ponerse al día. |
| 10 | 12–18 oct | Pendiente | Se necesita el lunes 12 oct. |
| 11 | 19–25 oct | Pendiente (repaso U2, Parcial 2) | — |
| 12–15 | 26 oct – 22 nov | Pendientes | — |
| 16–17 | 23 nov – 6 dic | Pendiente (cierre U3 + repaso) | Fin de clases: 30 nov. |

### 1.2 Inventario y métricas por semana publicada

Medido con `herramientas/auditar_presentacion.js` (renderizado real a 1280×720 con Chromium). Un "diagrama real" es un SVG con ≥3 conectores (líneas/flechas entre nodos); "tarjetas" son SVG de cajas de texto con íconos sin relaciones.

| Sem. | Diap. totales | Contenido | Con gráfico | Diagramas reales | Tarjetas | Raster | Sin gráfico | Video(s) | Duración |
|---|---|---|---|---|---|---|---|---|---|
| S01 | 8 | 7 | 2 (29 %) | 0 | 0 | 2 | 5 | 1 | 6:37 |
| S02 | 12 | 11 | 8 (73 %) | 0 | 0 | 8 | 3 | 1 | 8:13 |
| S03 | 14 | 13 | 8 (62 %) | 0 | 0 | 8 | 5 | 1 | 13:09 |
| S04 | 13 | 12 | 4 (33 %) | 0 | 0 | 4 | 8 | 1 | 11:37 |
| S05 | 11 | 10 | 3 (30 %) | 0 | 0 | 3 | 7 | 1 | 5:40 |
| S07 | 56 (4 portadas "Parte X de 4") | 52 | 52 (100 %) | 13 | 37 | 2 | 0 | 4 | 14:23–14:30 c/u |
| S08 | 56 (4 portadas "Parte X de 4") | 52 | 52 (100 %) | 14 | 38 | 0 | 0 | 4 | 14:13–14:45 c/u |

Estándar objetivo (Fase 2): **4 partes × ~14 diapositivas de contenido = ~56 + 4 divisorias**, casi todas con gráfico, 4 videos de ~15 min.

**Brecha de volumen:** S01–S05 suman 53 diapositivas de contenido y ~45 min de video **en total**; el estándar pide ~56 diapositivas y ~60 min **por semana**. S07 y S08 cumplen el volumen pero no la calidad gráfica (ver 1.3).

### 1.3 Calidad visual (revisión de capturas)

**Lo que está bien (conservar):**
- Lienzo fijo 1280×720, paleta institucional vino `#A6192E` / dorado `#D4AF37`, cabecera con *kicker* + título + regla degradada, pie con fuente y numeración. Es una buena base para la plantilla común.
- S07/S08 ya tienen la estructura de 4 partes con portada divisoria "Parte X de 4 · Unidad 2" y pie "Semana N · Parte X de 4" — es exactamente el patrón a generalizar.
- S07/S08 citan fuentes primarias en el pie (RFC 8446, 5280, 4301, 7296, 8555; NIST SP 800-63B, 800-207, 800-162, 800-53, 800-77r1).
- S03 tiene los mejores diagramas de red (topologías, 802.1Q, router-on-a-stick, DMZ) y atribuye imágenes de Wikimedia con su licencia.
- Sin desbordes en 5 de 7 semanas.

**Problemas detectados:**

| # | Severidad | Semana | Problema |
|---|---|---|---|
| V1 | Alta | S07, S08 | ~72 % de los "gráficos" son **rejillas de tarjetas**, no diagramas: no muestran topología, flujo ni relación. Deja la mitad inferior de la diapositiva en blanco (≈40 % del lienzo vacío). |
| V2 | Alta | S07, S08 | **Íconos de AWS usados como metáforas genéricas** (AWS Shield = "firewall", EC2 = "usuario/identidad", Amazon Connect, Budgets...). Contradice el enfoque "concepto genérico de industria" y las pautas de AWS (sus íconos deben representar servicios AWS). Reemplazar por un set propio de símbolos de red. |
| V3 | Alta | Todas | El logo se carga en caliente desde `es.wikipedia.org/wiki/Special:FilePath/Logo_cuc.png`. En este entorno devuelve 403 y desaparece (lo oculta el `onerror`). Para PDF/video reproducible hay que **vendorizar** el logo (ya existe `laboratorios/lab-03-routing-seguridad/logo-cuc.png`). |
| V4 | Media | S05 diap. 4–5 | Desborde: el checklist (diap. 5) se sale del lienzo y pisa el pie; el "antes/después" (diap. 4) queda pegado al pie. |
| V5 | Media | S03 diap. 6 | Texto del pie de imagen pisa el pie de página. |
| V6 | Media | S08 diap. 35 | Rótulos superpuestos ("todas pasan por la misma decisión de acceso" sobre la etiqueta del nodo). |
| V7 | Media | S01–S05 | Imágenes raster PNG embebidas (base64, 80–280 KB c/u) con texto pequeño; no escalan y no se pueden editar. Redibujar como SVG propio. |
| V8 | Baja | Todas (pantalla) | El navegador flotante (`#nav`, "1 / 56") se superpone al número de página del pie. No afecta PDF, sí capturas de video si se usa la UI. |
| V9 | Baja | Todas | Tipografía `Segoe UI` no existe en Linux → el render de PDF/video cae a Arial/DejaVu y cambia métricas. Embeber Roboto (Apache 2.0) o IBM Plex Sans (OFL), que ya usa `index.html`. |
| V10 | Baja | S01–S05 | No existe portada divisoria ni marca de corte; un solo video por semana. |

### 1.4 Calidad técnica y de consistencia

| # | Severidad | Dónde | Problema |
|---|---|---|---|
| T1 | Alta | S01 diap. 3–4 | **Calendario desactualizado** dentro de la presentación: muestra la numeración vieja (Cifrado en S6, Identidad en S7, Monitoreo en S8, Repaso U2 en S10...). Contradice `index.html`. |
| T2 | Alta | S07, S08 | Pies de fuente citan `TEMARIO-seguridad-redes-2026-2.md` (archivo interno que no está en el repo) **con la numeración vieja** ("S06: Lab 5.1", "S07: ejercicio...", "S08: monitoreo"). Reemplazar por la referencia al calendario oficial. |
| T3 | Media | S05 diap. 10 | "Lo que sigue": S7 = Identidad, S8 = Monitoreo (numeración vieja; hoy S7 = Cifrado, S8 = Identidad, S9 = Monitoreo). |
| T4 | Media | S01, S02 | Portadas dicen "Sesiones 1-2" (vestigio de cuando S01 y S02 eran una sola). |
| T5 | Media | S02 diap. 10 | "pfSense ... será la base del laboratorio de la semana 3": el Lab 1 usa **OPNsense**. |
| T6 | Media | S04 | El título oficial dice "Firewalls de host (ufw/iptables) práctico" pero no hay una sola diapositiva de netfilter/iptables (cadenas INPUT/FORWARD/OUTPUT, tablas, conntrack, orden de reglas). Brecha de contenido, no solo de forma. |
| T7 | Media | S01 | El título oficial promete "panorama de amenazas 2026 (IA ofensiva, identidad como nuevo perímetro)" y Zero Trust; la presentación no tiene diapositivas sobre IA ofensiva, identidad como perímetro ni principios Zero Trust. |
| T8 | Baja | `index.html` | Contador "5 de 13 publicadas" (hay 7). Las tarjetas de S3 y S4 no llevan el prefijo "Semana N ·" como las demás. |
| T9 | Baja | Todas | No hay guion de narración en el repo (los MP4 tienen audio, pero el texto fuente no está versionado) → los videos no se pueden regenerar. |
| T11 | Alta | S04, S07, (S08) | **Dependencia de AWS en material publicado**: S04 cierra con "Lanzar la instancia con su Security Group" (lab en AWS); la Parte 4 de S07 completa (diap. 44–52) gira en torno a AWS KMS y su laboratorio; S08 usa íconos AWS. El curso no usa AWS en la práctica → reorientar a concepto genérico + labs propios. |

---

## 2. Validación contra referentes externos

### 2.1 Referentes usados

| Referente | Por qué aplica | Cómo se usa |
|---|---|---|
| **Plataforma de labs propia del curso** (ver `laboratorios/`): Lab 1 VirtualBox + OPNsense + Alpine (4 zonas, NAT/PAT, app web + BD), Lab 2 TryHackMe gratuito (Snort), Lab 3 Cisco Packet Tracer (routing multi-sitio + SSH/ACL/port security/Syslog) | **Es la práctica real del curso**; no depende de ningún proveedor de nube | Cada semana cierra en su Parte 4 con un lab sobre esta plataforma, idealmente **extendiendo la topología del Lab 1** (misma red, nueva capa de seguridad cada semana). |
| **Cisco Networking Academy — Network Security** (22 módulos: amenazas, acceso seguro a dispositivos, AAA, ACL, tecnologías de firewall, ZPF, IPS, seguridad de endpoint, capa 2, criptografía, PKI, VPN/IPsec, ASA, pruebas de seguridad) | Referente de industria más cercano a "seguridad de **redes**" | Mapa de cobertura por semana (tabla 2.2). |
| **CompTIA Security+ SY0-701** (5 dominios: Conceptos generales 12 %, Amenazas/vulnerabilidades/mitigaciones 22 %, Arquitectura 18 %, Operaciones 28 %, Gestión del programa 20 %) | Certificación vendor-neutral de entrada; da el peso relativo de operaciones (monitoreo, vulnerabilidades, IR) | Verificar que U2–U3 tengan peso operativo. |
| **ACM/IEEE CS2023** — KA *Networking and Communication* (unidad NC-Security) y KA *Security* (SEC: fundamentos, criptografía, análisis e ingeniería de seguridad, forense, gobierno) | Marco curricular | Validar que haya mentalidad de seguridad, cripto aplicada, análisis de riesgos, ética/legal. |
| **NIST CSF 2.0** (Gobernar, Identificar, Proteger, Detectar, Responder, Recuperar) | Hilo conductor del curso | U1 ≈ Proteger, U2 ≈ Proteger+Detectar, U3 ≈ Detectar+Responder+Recuperar. |
| **NIST SP**: 800-41r1 (firewalls), 800-94 (IDPS), 800-92 / 800-92r1 borrador (logs), 800-77r1 (IPsec), 800-52r2 (TLS), 800-63B (autenticación), 800-207 (ZTA), 800-40r4 (parcheo), 800-115 (pruebas técnicas), **800-61r3 (abril 2025, respuesta a incidentes como perfil CSF 2.0)**, AI 100-2 (ML adversario) | Normas técnicas de cada semana | Fuente en el pie de cada diapositiva. |
| **ISO/IEC 27001:2022 / 27002:2022** (controles 8.20 seguridad de redes, 8.21 servicios de red, 8.22 segregación, 8.16 monitoreo, 8.8 vulnerabilidades, 5.24–5.28 incidentes) | Estándar de gestión que piden las empresas colombianas | Diapositiva de "cumplimiento" por semana (solo citar; ISO tiene derechos). |
| **CIS Controls v8.1** (12 Gestión de infraestructura de red, 13 Monitoreo y defensa de red, 7 Gestión de vulnerabilidades, 17 Respuesta a incidentes) y **CIS Benchmarks** | Práctica priorizada | S05, S09, S10, S13. |
| **MITRE ATT&CK** (Enterprise) y **MITRE ATLAS** (IA) | Lenguaje común de TTP | S09, S12, S14, S15. |
| **Colombia**: CONPES 3995 de 2020 (Política Nacional de Confianza y Seguridad Digital), ColCERT y CSIRT sectoriales, Ley 1273 de 2009 (delitos informáticos), Ley 1581 de 2012 (datos personales), Ley 1928 de 2018 (Convenio de Budapest) | Caso aplicado colombiano y marco legal | S01, S12, S13, S15. |

### 2.2 Mapa de cobertura (● cubierto · ◐ parcial · ○ falta · — no aplica)

| Tema de referencia | Cisco NetSec | Sec+ | Dónde está hoy | Estado | Dónde debe ir (sin cambiar títulos) |
|---|---|---|---|---|---|
| Amenazas, actores, superficie de ataque | M2 | D2 | S01 | ◐ | S01 P1–P2 |
| CIA, defensa en profundidad, Zero Trust (intro) | M1 | D1 | S01 (título), S04 | ◐ | S01 P3 |
| TCP/IP, ARP, DNS, puertos, handshake TCP | — | D3 | S02 | ◐ (falta handshake/puertos/DNS) | S02 P1–P2 |
| Routing estático/dinámico y su seguridad (BGP, RPKI, OSPF auth) | — | D3 | S02, S03 | ● | S02 P3 |
| VLAN, 802.1Q, subnetting, DMZ | M14 | D3 | S03 | ● | S03 |
| **Ataques de capa 2** (ARP spoofing, DHCP starvation/snooping, STP, CAM overflow, VLAN hopping, port security) | M14 | D2 | S02/S03 (menciones) | ◐ | S03 P2 |
| Firewalls: stateless/stateful/NGFW, orden de reglas | M9 | D3 | S02 | ● | S02 P4 |
| **netfilter/iptables/nftables/ufw práctico** | M9 | D4 | — | ○ | S04 P1–P2 |
| IDS/IPS, firmas/anomalías, Snort/Suricata | M11–12 | D4 | S04 | ● | S04 P3 |
| Firewall como servicio en nube (grupos de seguridad vs ACL de subred, cualquier proveedor) | — | D3 | S04 | ◐ | S04 P4 (como ejemplo, no como lab) |
| **Acceso seguro a dispositivos** (SSH, AAA/TACACS+/RADIUS, niveles de privilegio, plano de gestión, SNMPv3, NTP, banner, syslog) | M4–M7 | D4 | — | ○ | S05 P1–P2 |
| **ACL avanzadas** (estándar/extendida, wildcard, ubicación, object-groups, ACL IPv6) | M8 | D3 | S03 (1 ejemplo) | ◐ | S05 P3 |
| Hardening y benchmarks | — | D4 | S05 | ◐ | S05 P1 |
| Criptografía, hashes, integridad | M15–16 | D1 | S07 | ● | S07 P1 |
| PKI y certificados | M17 | D1 | S07 | ● | S07 P2 |
| VPN/IPsec, sitio a sitio, acceso remoto | M18–19 | D3 | S07 | ● | S07 P3 |
| **Criptografía post-cuántica en TLS (ML-KEM híbrido)** | — | D1 | — | ○ | S07 P1 (1 diap.) |
| **SSH y WireGuard** | M4 | D3 | — | ○ | S07 P3 |
| AAA, MFA, 802.1X/RADIUS, federación | M7 | D4 | S08 | ● | S08 |
| **Seguridad inalámbrica** (WPA2/WPA3, Enterprise/EAP, rogue AP, evil twin) | (CCNA) | D3/D4 | — | ○ **(falta en todo el curso)** | S08 P1 (con 802.1X) |
| Zero Trust a fondo, ZTNA, microsegmentación | — | D1/D3 | S03, S07, S08 | ● (repetido) | S08 P3 |
| **Logging, syslog, NetFlow/IPFIX, SIEM, correlación** | M6 | D4 | — | ○ | S09 |
| **Seguridad DNS** (DNSSEC, DoH/DoT, sinkhole, tunneling DNS) | — | D3/D4 | S02 menciones | ○ | S09 P2 (detección) / S12 |
| Gestión de vulnerabilidades (CVE, CVSS v4.0, EPSS, CISA KEV, escaneo) | M22 | D4 | — | ○ | S10 |
| Ransomware, APT, movimiento lateral, ATT&CK | M2 | D2 | S01 (menciones) | ○ | S12 |
| Respuesta a incidentes (NIST 800-61r3), forense básica, SOAR | — | D4 | — | ○ | S13 |
| IA ofensiva/defensiva, NDR con ML, SASE/SSE | — | D2/D3 | — | ○ | S14 |
| Pruebas de penetración, reglas de enfrentamiento, marco legal | M22 | D5 | — | ○ | S15 |
| Seguridad de nube de red (VPC, WAF, DDoS) | — | D3 | S04, S07 | ◐ | S04 P4, S07 P3, S14 |
| Gobierno y cumplimiento (ISO 27001, CONPES, Ley 1581) | — | D5 | S07 | ◐ | Diapositiva de cumplimiento en cada semana |

**Lectura:** la Unidad 1 está bien orientada pero corta en profundidad (S01, S04 y S05 no entregan lo que promete su título); la Unidad 2 cubre bien cripto e identidad; las brechas grandes son las semanas aún no producidas (S09–S15) y **tres temas transversales que faltan en todo el curso: seguridad inalámbrica, ataques de capa 2 como unidad, y acceso seguro a dispositivos de red (AAA/plano de gestión)**. Los tres caben dentro de títulos existentes.

### 2.3 Repeticiones a convertir en espiral (no eliminar, cambiar profundidad)

| Tema | Aparece en | Propuesta |
|---|---|---|
| Zero Trust | S01, S03 (diap. 10–11), S07 (diap. 39), S08 (Parte 3 completa) | S01 = motivación (por qué cae el perímetro); S03 = microsegmentación como *mecanismo de red*; S07 = ZT frente a la VPN; S08 = arquitectura NIST 800-207 (PDP/PEP) a fondo. Cada una enlaza con la anterior con una diapositiva "ya lo vimos en SXX". |
| RBAC/ABAC | S05 (diap. 6–9), S08 (Parte 2) | **Duplicación real.** S05 debe centrarse en el *control de acceso administrativo a dispositivos de red* (AAA, TACACS+, niveles de privilegio, cuentas compartidas → caso Corporación Industrial del Caribe). RBAC/ABAC como modelos quedan solo en S08. |
| IDS/IPS | S02 (concepto), S04 (a fondo), S09 ("avanzado") | S04 = sensor y reglas (Snort); S09 = IDS como *fuente de eventos* del SIEM: Suricata/Zeek, EVE JSON, afinamiento, correlación, NDR. No repetir anatomía de regla. |
| Hardening | S05 (perimetral), S10 (hardening + vulnerabilidades) | S05 = configuración segura de dispositivos de red; S10 = ciclo de vida (descubrir → priorizar → parchear → verificar) sobre hosts y servicios. |
| Security Groups | S04, S07 (nube híbrida) | Correcto como espiral. |

### 2.4 Propuesta de contenido por semana (4 partes; los títulos oficiales se mantienen)

Cada parte ≈ 14 diapositivas de contenido; la Parte 4 cierra con caso colombiano + laboratorio.

| Sem. | Parte 1 | Parte 2 | Parte 3 | Parte 4 (caso CO + lab) |
|---|---|---|---|---|
| **S01** Encuadre + red tradicional → Zero Trust | Encuadre del curso (calendario corregido, evaluación, labs), CIA + AAA, vocabulario (activo, amenaza, vulnerabilidad, riesgo) | Panorama 2026: actores, superficie de ataque, cadena de ataque (Kill Chain/ATT&CK resumido), incidentes por mala configuración 2024–2026 | IA ofensiva (phishing a escala, deepfakes, malware asistido) e identidad como nuevo perímetro; por qué cae el "castillo y foso" → principios Zero Trust | Caso CO: IFX Networks (sep 2023, >760 entidades) y CONPES 3995/ColCERT; reconocimiento con nmap en sandbox; puente al Lab 1 |
| **S02** Red básica + controles | Viaje del paquete: Ethernet/ARP, IP, TCP 3-way handshake, UDP, puertos, DNS | Direccionamiento IPv4/IPv6, NAT/PAT, ICMP — y la lectura de seguridad de cada uno (RA spoofing, NAT ≠ firewall) | Routing estático vs dinámico (OSPF, BGP), riesgos (hijack, route leak) y controles (autenticación OSPF, RPKI/ROV) | Firewall → stateful → NGFW → IDS conceptual; dónde vive cada control en TCP/IP; caso CO (Check Point en CUC como ejemplo de NGFW en campus); captura Wireshark guiada |
| **S03** Segmentación | Red plana y su riesgo; VLAN/802.1Q; trunks; inter-VLAN | **Ataques de capa 2** y defensas: VLAN hopping, ARP spoofing + DAI, DHCP snooping, STP/BPDU guard, port security, PVLAN | Subnetting por función, DMZ (1 y 2 firewalls), routing a fondo entre zonas | Microsegmentación como puente a ZT; caso CO de una IPS (Keralty 2022 → SaludVital); Lab 1 OPNsense |
| **S04** Firewalls de host + IDS/IPS | **netfilter**: tablas, cadenas, flujo del paquete, conntrack, iptables vs nftables | **ufw/iptables práctico**: política por defecto, orden de reglas, logging, rate-limit SSH, persistencia, verificación con nmap/ss | IDS/IPS: taxonomía, firmas vs anomalías, Snort/Suricata, ubicación (SPAN/TAP/inline), falsos positivos | Defensa en capas: perímetro (OPNsense) + host (nftables/ufw) + firewall como servicio en nube como ejemplo (stateful vs stateless); **lab: nftables/ufw en las Alpine del Lab 1 + verificación nmap**, Lab 2 Snort |
| **S05** Hardening perimetral + políticas de acceso | Hardening de dispositivos: planos de gestión/control/datos, CIS Benchmarks, servicios inseguros (Telnet, HTTP, SNMPv1) | **Acceso administrativo seguro**: SSH, AAA, TACACS+ vs RADIUS, niveles de privilegio, jump host/bastión, cuentas compartidas | **ACL avanzadas**: estándar/extendida, wildcard, ubicación, implícito deny, object-groups, ACL IPv6, defensa en profundidad | Checklist perimetral + política de cambios/logging; caso CO Corporación Industrial del Caribe; Lab 3 (Packet Tracer: SSH/AAA/ACL/port security/Syslog) |
| **S07** Cifrado en tránsito | (mantener) + 1 diap. post-cuántica (ML-KEM híbrido en TLS 1.3) | (mantener) | + SSH y WireGuard como alternativas de túnel | Reemplazar el foco KMS/AWS por cifrado en reposo genérico (LUKS, cifrado de BD, gestión de llaves/HSM/KMS de cualquier proveedor); caso CO: Ley 1581; **lab propio: CA interna con OpenSSL + HTTPS en la DMZ del Lab 1 y túnel WireGuard/IPsec en OPNsense** |
| **S08** Identidad y acceso | Autenticación, MFA, 802.1X/RADIUS + **Wi-Fi seguro (WPA3-Personal/Enterprise, EAP-TLS, rogue AP/evil twin)** | Autorización: RBAC/ABAC, mínimo privilegio, JIT | Zero Trust a fondo (NIST 800-207, PDP/PEP, ZTNA) | Ejercicio propio de control de acceso (se mantiene) |
| **S09** Monitoreo y logging: SIEM, IDS/IPS avanzado | Fuentes de evidencia: syslog (RFC 5424), logs de firewall/IDS/host, NetFlow/IPFIX, PCAP; sincronización NTP; qué registrar (NIST 800-92) | SIEM: ingesta, normalización, correlación, casos de uso, alertas, MITRE ATT&CK como mapa de detección; métricas (MTTD) | IDS/IPS avanzado: Suricata + Zeek, EVE JSON, afinamiento, NDR, detección de DNS tunneling/beaconing | Auditoría de plano de control en nube como ejemplo (registros de API de cualquier proveedor); caso CO (SOC/CSIRT, ColCERT); **lab propio: Suricata en OPNsense + syslog remoto a un colector Alpine (rsyslog) + consultas/alertas; opción Wazuh si el equipo da** |
| **S10** Hardening y gestión de vulnerabilidades | Ciclo de gestión de vulnerabilidades; CVE, CWE, NVD; CVSS v4.0; EPSS; CISA KEV | Escaneo: descubrimiento (nmap: tipos de escaneo, estados open/closed/filtered), escaneo autenticado vs no autenticado, Greenbone/OpenVAS | Priorización y parcheo (NIST 800-40r4), excepciones, mitigaciones compensatorias, hardening de hosts (CIS) | Caso CO + lab formativo Nmap/OpenVAS (sin nota): leer un reporte y priorizar |
| **S11** Repaso U2 | Mapa conceptual U2 (cifrado → identidad → monitoreo → vulnerabilidades) | Ejercicios tipo examen práctico | Errores frecuentes de los labs 5.1/6.1 | Rúbrica Parcial 2 y autoevaluación |
| **S12** Amenazas modernas | Ransomware moderno: RaaS, doble/triple extorsión, cadena típica, ATT&CK | APT: ciclo, persistencia, C2, exfiltración, living-off-the-land | Movimiento lateral: credenciales (pass-the-hash, Kerberoasting), SMB/RDP/WinRM, cómo lo frena la segmentación/ZT | Casos CO: IFX Networks 2023, Keralty nov 2022 (RansomHouse), EPM dic 2022 (BlackCat/ALPHV) — verificar atribuciones con fuente al producir; lab formativo de análisis (PCAP/logs) |
| **S13** Respuesta a incidentes y remediación automatizada | NIST SP 800-61r3 y CSF 2.0: preparación, detección, contención, erradicación, recuperación, lecciones | Playbooks, roles, comunicación, evidencia y cadena de custodia, reporte a ColCERT/CSIRT | Automatización: SOAR, eventos → reglas → acciones, idempotencia, riesgos de la automatización | Remediación automatizada genérica (evento → regla → acción): fail2ban/nftables en Alpine, bloqueo por alias vía API de OPNsense, respuesta activa de Wazuh; la nube (reglas de conformidad + funciones) como ejemplo; **lab propio de contención automatizada sobre la topología del Lab 1** |
| **S14** IA ofensiva vs IA defensiva | IA ofensiva: phishing generado, deepfakes de voz/video, malware asistido, reconocimiento automatizado | IA defensiva: NDR/UEBA con ML, detección de anomalías, falsos positivos, copilotos SOC | Atacar la IA: MITRE ATLAS, OWASP Top 10 para LLM, NIST AI 100-2; SASE/SSE "consciente de IA" | Caso CO (fraude por deepfake/vishing), ejercicio de detección |
| **S15** Ethical hacking asistido por IA | Metodologías (PTES, NIST 800-115, OSSTMM), fases, tipos de prueba | Marco legal/ético: Ley 1273 de 2009 (art. 269A y ss.), Convenio de Budapest (Ley 1928 de 2018), reglas de enfrentamiento, autorización escrita | Herramientas y asistentes IA: recon, escaneo, explotación controlada, reporte; límites y alucinaciones | Lab de ethical hacking asistido por IA en entorno controlado (10 %) |
| **S16–17** Cierre U3 + repaso general | Síntesis del curso con NIST CSF 2.0 | Ejercicios integradores | Rúbrica Parcial 3 | Proyecto/ruta de certificación (Security+, Cisco CyberOps, CCNA) |

### 2.5 Recomendaciones del análisis

1. **Urgente:** producir S09 durante el receso (5–11 oct) — es la semana actual. Luego S10 antes del 12 de octubre.
2. Unificar la plantilla (CSS/JS/logo/fuentes) en `assets/` para que las 13 semanas se vean y rendericen igual.
3. Reemplazar íconos AWS-como-metáfora por una biblioteca propia de símbolos de red en SVG (router, switch, firewall, servidor, nube, usuario, IDS, SIEM, VPN, candado, base de datos, AP inalámbrico) con la paleta CUC.
4. Diagramas: privilegiar topologías y diagramas de secuencia/flujo (paquete que recorre zonas, handshake, cadena de ataque, pipeline SIEM) sobre rejillas de tarjetas; meta ≥ 60 % de diagramas reales por semana.
5. Versionar el guion de narración dentro del HTML (fuente única) para regenerar PDF y video.
6. **Independencia de proveedor:** ningún lab depende de una cuenta en la nube; la práctica corre en VirtualBox + OPNsense + Alpine, Packet Tracer y salas gratuitas de TryHackMe. Los ejemplos de nube se muestran con íconos genéricos y se nombran 2–3 proveedores a la vez.
7. Corregir T1–T5 en la oleada que toque S01/S02/S05/S07/S08.

---

## 3. Presentaciones antiguas (.pptx)

No se recibieron archivos `.pptx` en esta fase (el repo no contiene ninguno). **Pendiente:** cuando los compartas, se extraerán sus diagramas e ideas (texto, notas y estructura de formas con `python-pptx`/`markitdown`), se mapearán a la tabla 2.4 y cada diagrama útil se **redibujará como SVG propio** (no se pegan imágenes con derechos). El resultado se agregará como sección 3.1 de este documento con la tabla *diapositiva origen → semana/parte destino → diagrama SVG nuevo*.

---

## 4. Fuentes consultadas para el análisis

- Guías de laboratorio del repo (`laboratorios/lab-01…03`).
- Cisco Networking Academy — *Network Security*, listado de 22 módulos ([classcentral](https://www.classcentral.com/course/cisco-networking-academy-network-security-534119), [netacad](https://www.netacad.com/catalogs/learn/cybersecurity)).
- CompTIA Security+ SY0-701 — dominios y pesos ([resumen](https://destcert.com/resources/security-plus-701-objectives/)).
- ACM/IEEE CS2023 — áreas NC y SEC ([csed.acm.org/knowledge-areas](https://csed.acm.org/knowledge-areas/)).
- NIST SP 800-61r3 (abril 2025) ([nist.gov](https://nist.gov/news-events/news/2025/04/nist-revises-sp-800-61-incident-response-recommendations-and-considerations), [PDF](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-61r3.pdf)).
- CONPES 3995 de 2020 ([DNP](https://colaboracion.dnp.gov.co/CDT/Conpes/Econ%C3%B3micos/3995.pdf)).
- ColCERT — informe de tendencias 2025 ([MinTIC](https://mintic.gov.co/portal/inicio/Sala-de-prensa/Noticias/433511:Colombia-fortalece-su-soberania-digital-durante-2025-logro-reducir-en-un-48-los-incidentes-ciberneticos)).
- Ataque a IFX Networks, sep 2023 ([INCIBE-CERT](https://www.incibe.es/en/incibe-cert/publications/cybersecurity-highlights/ransomware-cyber-attack-against-ifx-networks), [Infobae](https://www.infobae.com/colombia/2023/09/19/ransomhouse-podria-ser-responsable-de-ciberataque-a-ifx-networks-fiscalia/)).
