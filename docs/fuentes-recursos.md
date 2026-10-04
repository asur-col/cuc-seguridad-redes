# Fuentes de gráficos, íconos, imágenes, datos y notas — con licencia

**Seguridad en Redes · CUC · 2026-2**

Política del curso:

1. **Los diagramas se dibujan como SVG propio**, en la paleta CUC (vino `#A6192E`, dorado `#D4AF37`). Una idea, topología o flujo no tiene derechos; el dibujo de otro sí. Por eso se redibuja, no se pega.
2. Los íconos vienen de **una biblioteca propia** (`assets/iconos/`, a crear en la Oleada 0) dibujada desde cero o derivada de sets con licencia permisiva (MIT/ISC/Apache/CC0). No se usan íconos de marca (AWS, Cisco, Azure) como metáfora de un concepto genérico.
3. Toda cifra, cita o diagrama "basado en" lleva la fuente en el pie de la diapositiva (`.s-foot .src`).
4. Antes de publicar un recurso de terceros, revisar su página de licencia: las licencias cambian. Esta tabla resume el estado conocido a la fecha y marca con ⚠ lo que debe verificarse caso por caso.

---

## 1. Íconos

| Fuente | Licencia | ¿Se puede modificar/recolorear? | Atribución | Uso recomendado en el curso |
|---|---|---|---|---|
| **Tabler Icons** (tabler.io/icons) | MIT | Sí | No obligatoria en la diapositiva; conservar aviso MIT en `assets/iconos/LICENSES.md` | Base principal de pictogramas (router, servidor, candado, usuario, nube, alerta). |
| **Lucide** (lucide.dev) | ISC | Sí | Igual que MIT | Alternativa a Tabler. |
| **Bootstrap Icons** | MIT | Sí | Igual que MIT | Complemento. |
| **Material Symbols** (Google) | Apache 2.0 | Sí | Conservar aviso en `LICENSES.md` | Complemento. |
| **Phosphor Icons** | MIT | Sí | Igual que MIT | Complemento. |
| **Font Awesome Free** (íconos) | CC BY 4.0 | Sí | **Obligatoria** (basta en `LICENSES.md` + crédito global en la diapositiva final) | Evitar si hay alternativa MIT, por la atribución. |
| **draw.io / diagrams.net** (formas base) | Apache 2.0 | Sí | Aviso en `LICENSES.md` | Útil para bocetar; exportar a SVG y limpiar. Ojo: los *stencils* de Cisco/AWS/Azure incluidos en draw.io conservan la licencia de su fabricante. |
| **Cisco Network Topology Icons** (cisco.com/brand-center) | Términos de Cisco: uso libre, **no se pueden alterar** ⚠ | **No** (no recolorear a la paleta CUC) | Indicar "Íconos: Cisco Systems" | Solo cuando se hable de equipo Cisco específico o en guías de Packet Tracer. Para concepto genérico, ícono propio. |
| **AWS Architecture Icons** (aws.amazon.com/architecture/icons) | Términos de AWS: uso permitido para diagramas y presentaciones sobre **servicios AWS**; son marcas de Amazon ⚠ | No alterar | "Íconos de AWS © Amazon Web Services" | El curso no usa AWS en la práctica: solo si una diapositiva nombra explícitamente un servicio AWS junto a sus equivalentes de otros proveedores (preferir ícono genérico + nombre). **No** para "firewall genérico", "usuario" ni "identidad" (error V2 del análisis). |
| **Azure Architecture Icons** (Microsoft) | Términos de Microsoft: uso en diagramas de arquitectura; no modificar ⚠ | No | "Íconos © Microsoft" | Solo si se muestra un servicio Azure como ejemplo de proveedor. |
| **Google Cloud icons** | Términos de Google ⚠ | No | "Íconos © Google" | Ídem. |
| **Simple Icons** (logos de marcas) | CC0 para el SVG; las marcas siguen siendo de sus dueños | — | Nombrar la marca | Logos de productos (Snort, Suricata, Wireshark) solo como referencia nominativa, tamaño pequeño. |

**Biblioteca propia a crear** (`assets/iconos/*.svg`, trazo 2 px, 64×64, vino/dorado/gris): router, switch L2, switch L3, firewall, NGFW, IDS/IPS (sensor), servidor, base de datos, PC, portátil, móvil, AP inalámbrico, nube/Internet, usuario, grupo, atacante, candado, llave, certificado, túnel VPN, SIEM, log, alerta, escáner, nube pública genérica, contenedor, IoT/OT, edificio/sede.

## 2. Imágenes y fotografías

| Fuente | Licencia | Reutilización | Cómo citar |
|---|---|---|---|
| **Wikimedia Commons** | Varía por archivo (dominio público, CC0, CC BY, CC BY-SA) ⚠ | Revisar la página de cada archivo. CC BY-SA obliga a compartir la obra derivada con la misma licencia si se modifica la imagen. | "Título — Autor — Wikimedia Commons — Licencia" (S02/S03 ya lo hacen así: p. ej. "Michel Bakni · Wikimedia Commons · CC BY-SA 4.0"). |
| **Unsplash** | Unsplash License (uso libre, sin atribución obligatoria; no recopilar para servicio competidor) | Sí | Cortesía: "Foto: Autor / Unsplash". |
| **Pexels** | Pexels License (similar a Unsplash) | Sí | Cortesía: "Foto: Autor / Pexels". |
| **Openclipart** | CC0 | Sí | Opcional. |
| **unDraw** | Licencia propia de unDraw (uso libre, sin atribución) ⚠ | Sí, recolorable | Opcional. |
| Capturas de pantalla de herramientas (Wireshark, nmap, OPNsense, consola AWS) | Captura propia de software para fines didácticos y críticos (cita) | Sí, como cita ilustrativa | "Captura propia — Wireshark 4.x". Evitar datos personales/IPs reales. |
| Logo CUC | Marca institucional | Uso del docente en material del curso, sin alterar | Copia local en `assets/logo-cuc.png` (hoy se enlaza en caliente a Wikipedia y falla sin red). |

**No usar:** imágenes de prensa (El Tiempo, Semana, Infobae...), figuras de informes comerciales copiadas como imagen, ni resultados de búsqueda de Google Imágenes.

## 3. Datos, cifras y diagramas de referencia (para redibujar y citar)

| Fuente | Licencia / régimen | Qué se puede hacer | Ejemplo de cita en pie |
|---|---|---|---|
| **NIST** (SP 800-41, 800-92, 800-94, 800-207, 800-61r3, 800-63B, 800-115, CSF 2.0, AI 100-2) | Obra del gobierno de EE. UU. — no sujeta a copyright en EE. UU.; NIST pide citar | Reproducir/adaptar figuras con cita | "NIST SP 800-207 (2020), fig. 2" |
| **CISA** (KEV, avisos) | Mayormente dominio público (EE. UU.) | Usar datos con cita | "CISA KEV, consultado AAAA-MM-DD" |
| **IETF RFC** | IETF Trust Legal Provisions: se permite citar extractos con referencia | Citar secciones, redibujar diagramas | "IETF RFC 8446 §2" |
| **MITRE ATT&CK / ATLAS** | Licencia royalty-free de MITRE: uso y reproducción con el aviso de copyright | Usar nombres e IDs de técnicas (T1021, T1486...) y redibujar la matriz | "MITRE ATT&CK® v1x — © The MITRE Corporation" |
| **OWASP** (Top 10, Top 10 LLM) | CC BY-SA 4.0 | Adaptar con atribución y misma licencia | "OWASP Top 10 for LLM Applications 2025 — CC BY-SA 4.0" |
| **CIS Controls v8.1** | CC BY-NC-ND 4.0 ⚠ | Citar números/nombres de control; **no** publicar versiones modificadas del texto | "CIS Controls v8.1, Control 13" |
| **CIS Benchmarks** | Términos de CIS (uso no comercial, registro) ⚠ | Citar recomendaciones puntuales | "CIS Benchmark <producto> vX, rec. 1.1.1" |
| **ISO/IEC 27001/27002:2022** | Derechos de ISO | Solo citar número y nombre de control; no copiar texto | "ISO/IEC 27002:2022, 8.22" |
| **ENISA Threat Landscape** | Reutilización con atribución (CC BY 4.0 en la mayoría) ⚠ | Redibujar cifras | "ENISA Threat Landscape 2025" |
| **Verizon DBIR**, informes de fabricantes (IBM, Mandiant, CrowdStrike, Fortinet) | Copyright del autor | Usar **cifras** con cita; redibujar gráficos propios | "Verizon DBIR 2026, p. X" |
| **Cloudflare Radar** | CC BY-NC 4.0 ⚠ | Datos con atribución, uso no comercial (académico OK) | "Cloudflare Radar, CC BY-NC 4.0" |
| **Google IPv6 statistics / APNIC Labs** | Datos públicos | Cifras con fecha de consulta | "Google IPv6 Statistics, 28-mar-2026" |
| **Colombia**: CONPES 3995, MinTIC/ColCERT, Ley 1273/2009, Ley 1581/2012, Ley 1928/2018, Fiscalía | Documentos públicos | Citar y resumir | "CONPES 3995 (DNP, 2020)" |
| **Prensa** (Infobae, Semana, El Tiempo, Portafolio) e **INCIBE-CERT** | Copyright del medio | Solo hechos + enlace; nunca imágenes | "INCIBE-CERT, 2023" |

## 4. Tipografías

| Fuente | Licencia | Notas |
|---|---|---|
| **Roboto** | OFL 1.1 / Apache 2.0 | Cuerpo (coincide con la guía institucional del skill CUC). Embeber `.woff2` en `assets/fonts/` para render idéntico en PDF/video. |
| **IBM Plex Sans / Mono** | OFL 1.1 | Ya usada en `index.html`; Mono para comandos/consola. |
| **EB Garamond** | OFL 1.1 | Sustituto libre de *Adobe Garamond Pro* (licencia comercial; no embeber sin licencia). |
| Segoe UI | Licencia de Microsoft, no redistribuible | Hoy es la primera opción del CSS; en Linux no existe y el render cambia. Reemplazar. |

## 5. Voz sintética y herramientas de video

| Herramienta | Licencia | Red necesaria | Comentario |
|---|---|---|---|
| **edge-tts** (paquete Python) | Biblioteca MIT; usa el servicio en línea de voces neuronales de Microsoft Edge ⚠ (términos del servicio) | Sí (`speech.platform.bing.com`, **bloqueado en este contenedor**) | Mejor calidad gratuita en español (p. ej. `es-CO-GonzaloNeural`, `es-CO-SalomeNeural`). Opción por defecto para correr en el computador del docente. |
| **Piper TTS** | Motor MIT; cada voz tiene su propia licencia en su *model card* ⚠ | Solo para descargar la voz (Hugging Face — bloqueado aquí) | Offline. Voces `es_MX`/`es_ES`. |
| **Kokoro-82M** | Apache 2.0 | Descarga del modelo | Offline, incluye voces en español. |
| Coqui XTTS-v2 | Coqui Public Model License (no comercial) ⚠ | Descarga | Uso académico; clonación de voz solo con consentimiento. |
| Azure / Google Cloud TTS | Comercial, requiere cuenta | Sí | Alternativa de pago. |
| espeak-ng | GPL-3.0 | No | Calidad baja; solo para pruebas de sincronía. |
| **Playwright + Chromium** | Apache 2.0 / BSD | No | Captura de diapositivas y PDF. |
| **FFmpeg** | LGPL/GPL | No | Ensamble MP4 (H.264 + AAC). |

Si se usa voz sintética, la diapositiva final de cada parte indica: "Narración generada con voz sintética (<motor/voz>)".

## 6. Notas y guiones

- El guion de cada diapositiva es **texto propio** del curso (sin copiar párrafos de libros o informes). Cuando se apoye en una norma, se parafrasea y se cita en el pie.
- Formato acordado: `<aside class="notes">` dentro de cada `<section class="slide">` (oculto en pantalla y en PDF); la diapositiva divisoria lleva `data-parte="N"` y es la marca de corte del video.
- Bibliografía base recomendada para el docente (citar, no copiar): Stallings, *Network Security Essentials* (Pearson); Santos, *CCNA/CyberOps* (Cisco Press); Chapple & Seidl, *CompTIA Security+ Study Guide SY0-701* (Sybex); Sanders & Smith, *Applied Network Security Monitoring* (Syngress).

## 7. Cómo citar (resumen)

- **Pie de diapositiva** (corto): `Fuente: NIST SP 800-92 (2006) · ATT&CK T1021 (MITRE)`.
- **Diagrama propio basado en otro**: `Diagrama propio basado en NIST SP 800-207, fig. 2`.
- **Imagen CC BY / CC BY-SA**: `"Título" — Autor — Wikimedia Commons — CC BY-SA 4.0`.
- **Datos con fecha**: `Google IPv6 Statistics, consultado 2026-03-28`.
- **Diapositiva final de cada parte**: lista APA 7 de las fuentes de esa parte.
