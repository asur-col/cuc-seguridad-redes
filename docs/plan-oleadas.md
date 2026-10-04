# Plan de producción por oleadas — Seguridad en Redes 2026-2

Depende de: `docs/analisis-tematico.md` (qué va en cada semana) y `docs/fuentes-recursos.md` (qué se puede usar).
Estado: **propuesta — espera aprobación del docente.**

## Estándar por semana (Fase 2)

- 1 hora = **4 partes de ~15 min** en **un solo HTML** por semana. Cada parte abre con una diapositiva divisoria **"Parte X de 4"** (`data-parte="X"`) = punto de corte del video.
- **~14 diapositivas de contenido por parte** (≈56 + 4 divisorias). Meta: ≥ 90 % con gráfico y **≥ 60 % con diagrama real** (topología, flujo, secuencia, arquitectura), no rejillas de tarjetas.
- Estilo institucional CUC: vino `#A6192E`, dorado `#D4AF37`, lienzo 1280×720, plantilla común en `assets/`.
- Enfoque: concepto genérico de industria → ejemplo con 2–3 tecnologías/proveedores distintos → práctica en la **plataforma propia**: VirtualBox + OPNsense + Alpine (topología del Lab 1, que crece cada semana), Cisco Packet Tracer y salas gratuitas de TryHackMe. **Ningún lab exige cuenta en la nube.**
- Parte 4: caso aplicado colombiano + cierre con el lab.
- Cada diapositiva lleva su guion en `<aside class="notes">` (~130–160 palabras ≈ 1 min con voz sintética); 14 diapositivas ≈ 15 min por parte.
- Fuente en el pie de cada diapositiva con cifra/norma; lista APA al cierre de cada parte.
- Entregables por semana: `2026-2-SNN-....html`, `....pdf`, `videos/....-parte1..4.mp4`.

## Oleada 0 — Infraestructura común (modelo principal, 1 sesión)

1. `assets/`: `cuc.css` (tokens, componentes, impresión, `aside.notes` oculto), `deck.js` (navegación, `?slide=N`, modo captura sin UI), `logo-cuc.png` local, fuentes Roboto/IBM Plex embebidas.
2. `assets/iconos/`: biblioteca SVG propia de símbolos de red (lista en `fuentes-recursos.md` §1) + `LICENSES.md`.
3. `plantillas/semana-plantilla.html`: portada, divisoria, 6 patrones de diagrama de ejemplo (topología por zonas, secuencia cliente-servidor, pipeline, ciclo, comparación lado a lado, línea de tiempo de ataque) y diapositiva de cierre de lab.
4. `herramientas/`:
   - `auditar_presentacion.js` (ya creado en Fase 1): capturas por diapositiva + detección de desbordes.
   - `contar.py`: diapositivas/partes/gráficos/diagramas reales/palabras de guion por parte → duración estimada.
   - `pdf.js`: PDF 16:9 desde el HTML (Playwright).
   - `videos.py` + `README.md`: un comando → 4 MP4 por semana (captura de cada diapositiva + TTS del guion + FFmpeg, corte en cada `data-parte`). TTS por defecto `edge-tts` (voz `es-CO`), alternativa offline Piper/Kokoro.
5. `index.html`: tarjetas de semanas futuras **sin enlace** (clase `pending`, "Próximamente"), contador corregido, prefijo "Semana N ·" uniforme. Títulos del calendario intactos.

> Red de este contenedor: `speech.platform.bing.com` y `huggingface.co` están bloqueados → **los MP4 con voz neuronal no se pueden generar aquí**; se dejará el script listo para tu computador. PDF sí se genera aquí.

## Oleada 1 — Urgente (receso 5–11 oct)

| Semana | Por qué | Lab de cierre (plataforma propia) |
|---|---|---|
| **S09** Monitoreo y logging: SIEM, IDS/IPS avanzado | Atrasada (semana actual), Actividad 2 de U2 (10 %) | Suricata en OPNsense (IDS → IPS) + syslog remoto a colector Alpine (rsyslog) + consultas y alerta; Wazuh opcional |
| **S10** Hardening y gestión de vulnerabilidades | Se dicta el 12 oct | Formativo: nmap (descubrimiento, estados) + Greenbone/OpenVAS contra las Alpine/DMZ del Lab 1; priorizar con CVSS v4 + EPSS + KEV |
| **S11** Repaso U2 | Parcial 2 (19–25 oct) | Ejercicios tipo examen práctico sobre la topología del Lab 1 |

Subagentes en paralelo: 3 (uno por semana).

## Oleada 2 — Unidad 3 (antes del 26 oct)

S12 (ransomware/APT/movimiento lateral — lab formativo de análisis de PCAP/logs), S13 (respuesta a incidentes y remediación automatizada — fail2ban/nftables, bloqueo vía API de OPNsense), S14 (IA ofensiva vs defensiva), S15 (ethical hacking asistido por IA — entorno controlado, Ley 1273/2009), S16–17 (cierre + repaso). 5 subagentes en paralelo.

## Oleada 3 — Elevar U1 al estándar (S01–S05) + repaso S06

Reescritura completa a 4 partes según la tabla 2.4 del análisis (incluye ataques de capa 2 en S03, netfilter/nftables en S04, AAA/ACL avanzadas en S05) y corrección de T1, T4, T5, T3. Se conservan los diagramas buenos de S03 redibujados como SVG. 6 subagentes.

## Oleada 4 — Pulir U2 publicada (S07, S08)

Volumen ya cumple; se trabaja calidad: reemplazar íconos AWS por la biblioteca propia, convertir rejillas de tarjetas en diagramas reales (meta ≥ 60 %), corregir T2 y V6, sacar la dependencia de AWS KMS de la Parte 4 de S07 (lab propio: CA con OpenSSL + HTTPS en DMZ + túnel WireGuard/IPsec), agregar post-cuántica/SSH/WireGuard (S07) y Wi-Fi WPA3/EAP (S08), escribir guiones. 2 subagentes.

## Flujo por semana (cada oleada)

1. Subagente (Sonnet) recibe: estándar, plantilla, fila de la tabla 2.4, fuentes permitidas, lab de cierre. Entrega HTML con guiones.
2. **Auditoría del modelo principal** (`herramientas/contar.py` + `auditar_presentacion.js`):
   - 4 divisorias, 52–60 diapositivas de contenido, ≥ 90 % con gráfico, ≥ 60 % diagramas reales;
   - 0 desbordes; revisión visual de la hoja de contacto;
   - precisión técnica (comandos, RFC/NIST, cifras con fuente y fecha);
   - guion 1 900–2 400 palabras por parte (≈ 13–16 min).
   - Si falla → devolución con lista concreta al subagente.
3. PDF generado; tarjeta en `index.html` creada **desactivada** hasta que el docente publique.
4. Commit por oleada en `claude/kind-gauss-b90suh`.
5. Al final: `CLAUDE.md` con estándar, convenciones, comandos, estado por semana y pendientes.

## Preguntas abiertas para el docente

1. **Columna "Actividad / Evaluación" del calendario**: hoy menciona "Lab 4.1/5.1/6.1/7.1 AWS Academy". Como no usas AWS, ¿la reemplazo por los labs propios (p. ej. "Actividad 2 (U2): lab propio de monitoreo con Suricata + syslog") o la dejo intacta por ser parte del calendario oficial? (Los **títulos de tema** no se tocan en ningún caso.)
2. **Orden**: ¿apruebas que la Oleada 1 (S09–S11) vaya antes de reescribir S01–S05, dado que S09 está atrasada?
3. **Repasos** (S06, S11, S16–17): ¿presentación completa de 4 partes o un formato corto (1–2 partes) de ejercicios?
4. **Voz**: ¿edge-tts con voz colombiana (`es-CO-GonzaloNeural` / `es-CO-SalomeNeural`) en tu equipo, u opción 100 % offline (Piper/Kokoro)?
5. **Presentaciones viejas (.pptx)**: compártelas cuando quieras; se mapean a esta tabla antes de la oleada que corresponda.
