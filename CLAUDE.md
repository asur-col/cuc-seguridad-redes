# CLAUDE.md — Seguridad en Redes (CUC 2026-2)

Material de la asignatura **Seguridad en Redes** · Universidad de la Costa · Ing. Rodolfo Cañas Cervantes.
Rama de trabajo: `claude/kind-gauss-b90suh`. Idioma de todo el material: español (Colombia).

## Reglas que no se rompen
1. **Los títulos del calendario de `index.html` son oficiales: no se cambian.** Las mejoras van dentro de cada semana.
2. **Solo material académico**: presentaciones, guiones, PDF, videos. No se tocan actividades evaluables, porcentajes, rúbricas ni la columna "Actividad / Evaluación" del calendario; las presentaciones no los mencionan.
3. **Concepto genérico de industria**, ejemplos con 2–3 tecnologías. **No depender de AWS/Azure/Cisco**: la práctica corre en VirtualBox + OPNsense + Alpine (Lab 1), Cisco Packet Tracer (Lab 3) y salas gratuitas de TryHackMe (Lab 2). Nada de íconos de marca.
4. **Los videos los genera el docente en su computador** (no se generan en el repositorio). Ver `herramientas/LEEME-videos.md`.
5. Semanas futuras: se producen pero **sin enlace** en `index.html` ("Próximamente") hasta que el docente las publique (`"publicada": true` en su `semana.json`).

## Estándar por semana
- 1 hora = **4 partes de ~15 min** sobre un solo HTML. Diapositiva divisoria "Parte X de 4" (`data-parte`) = corte de video.
- **13–15 diapositivas de contenido por parte** (~56 + 4 divisorias); ≥ 90 % con gráfico y ≥ 60 % con diagrama real (topología, secuencia, flujo…), no rejillas de tarjetas.
- Estilo CUC: vino `#A6192E`, dorado `#D4AF37`, lienzo 1280×720, Roboto.
- Caso aplicado colombiano y cierre con práctica guiada en la Parte 4.
- Guion por diapositiva en `<aside class="notes">`, 150–175 palabras (~1 min), 1 900–2 500 palabras por parte, escrito para voz sintética.
- Detalle completo, formato y criterios de aceptación: **`docs/estandar-semana.md`**. Contenido por semana: `docs/analisis-tematico.md` §2.4. Recursos y licencias: `docs/fuentes-recursos.md`. Plan: `docs/plan-oleadas.md`.

## Estructura del repo
```
fuentes/SNN/semana.json     datos oficiales de la semana (título, archivo, publicada, partes, guiones de divisoria)
fuentes/SNN/parte1..4.html  diapositivas de contenido (FUENTE EDITABLE)
fuentes/_EJEMPLO/           6 patrones de diagrama de referencia
2026-2-SNN-….html           presentación generada (NO editar a mano)  → regenerar con construir.py
2026-2-SNN-….pdf            PDF generado
videos/                     MP4 (los nuevos los genera el docente)
guiones/                    guiones exportados (herramientas/guiones.py)
assets/                     cuc-deck.css/js, logo-cuc.png, fuentes locales, iconos.svg (70 íconos de red propios)
plantillas/                 ejemplo-semana.html (render de los patrones)
laboratorios/ proyectos/    guías de labs y proyecto de aula (no tocar sin pedirlo)
herramientas/               scripts (abajo)
docs/                       análisis, fuentes, plan, estándar
```

## Cómo regenerar (desde la raíz)
```bash
pip install playwright beautifulsoup4 && playwright install chromium
python3 herramientas/construir.py S05            # fuentes/S05 → HTML final (o "todas")
python3 herramientas/auditar.py <archivo>.html --capturas /tmp/cap   # métricas + desbordes + PNG por diapositiva
python3 herramientas/pdf.py <archivo>.html       # PDF
python3 herramientas/guiones.py <archivo>.html   # guiones/…md con cortes de video
python3 herramientas/indice.py                   # tarjetas de index.html desde fuentes/*/semana.json
python3 herramientas/videos.py <archivo>.html    # EN LOCAL: 4 MP4 con voz es-CO-GonzaloNeural (ver LEEME-videos.md)
```
Auditoría esperada: 0 desbordes · gráfico ≥ 90 % · diagrama ≥ 60 % · guion 1 900–2 500 palabras/parte · 0 diapositivas sin guion. Revisar siempre las capturas a ojo (texto encimado, cortes, vacíos).

## Convenciones técnicas
- Íconos solo con `<use href="#i-NOMBRE" …/>` (lista en `assets/iconos.svg`). IDs de `<marker>` únicos por semana (`sNNpXdY-…`).
- Colores en SVG: usar los tokens del estándar; verde solo para "permitido/ok".
- Cifras: siempre con fuente y año en `data-fuente`; no inventar. Ortografía completa.
- Commits por oleada, mensaje en español, en la rama de trabajo. No crear PR sin que el docente lo pida.

## Estado por semana (4-oct-2026)
| Semana | Fechas | `publicada` | Fuentes (`fuentes/SNN`) | Pendiente |
|---|---|---|---|---|
| 1–6 | 5 ago–13 sep | sí (viejo S01–S05 aún en la raíz, intactos) | **SUSPENDIDA** — Oleada 1 detenida a petición del docente; no hay partes escritas (solo `semana.json`) | Producir S01–S06 con el encargo de `docs/estandar-semana.md`; auditar, `construir.py`, PDF, commit; quitar HTML/PDF viejos al reemplazar |
| 7, 8 | 14–27 sep | sí (versión vieja de 56 diap.) | solo `semana.json` | Reescribir a íconos propios y diagramas reales; S07 sin dependencia de AWS KMS; añadir post-cuántica/SSH/WireGuard (S07) y Wi-Fi WPA3/EAP (S08); T2/V6 |
| **9** | 28 sep–4 oct | sí (en curso, **sin material aún**) | solo `semana.json` | **Prioridad 1**: Monitoreo/SIEM; Suricata + syslog en OPNsense |
| 10 | 12–18 oct | no | solo `semana.json` | Se dicta el 12-oct |
| 11 | 19–25 oct | no | solo `semana.json` | Repaso U2 |
| 12–15 | 26 oct–22 nov | no | solo `semana.json` | Amenazas modernas · Respuesta a incidentes · IA ofensiva/defensiva · Ethical hacking con IA |
| 16–17 | 23 nov–6 dic | no | solo `semana.json` | Cierre U3 + repaso general |

(Actualizar esta tabla al cerrar cada oleada.)

## Plan para continuar (en local, con Claude Code)
1. `git pull` en la rama. **La producción está suspendida**: Oleada 0 (infraestructura) terminada; Oleada 1 (S01–S06) sin empezar a producir contenido. Reanudar por la Oleada 1 (o por S09 si urge), un subagente Sonnet por semana.
2. **Oleada 2 — S07–S11** (S09 primero): un subagente por semana (modelo Sonnet) con el mismo encargo que en `docs/estandar-semana.md`; el coordinador audita cada entrega (conteos, capturas, precisión técnica, duración) antes de aceptar.
3. **Oleada 3 — S12–S16/17**, igual. Se crean pero `publicada:false`.
4. Cuando el docente decida publicar una semana: `"publicada": true` en su `semana.json` → `python3 herramientas/indice.py`.
5. Videos y PDF finales: ejecutar `pdf.py` y `videos.py` en el computador del docente (`herramientas/LEEME-videos.md`), luego `indice.py` y commit.
6. Al terminar todo: borrar HTML/PDF/MP4 antiguos que ya no se enlazan y eliminar `fuentes/_EJEMPLO` si ya no se necesita.

## Pendientes y decisiones abiertas
- **Videos antiguos** de S01–S08 siguen enlazados hasta que se generen los nuevos (decidir si se quitan).
- **Presentaciones viejas (.pptx)**: el docente puede compartirlas; se extraen ideas y se **redibujan como SVG propio** (sección 3 de `docs/analisis-tematico.md`).
- Verificar atribuciones de los casos colombianos antes de publicar (Keralty 2022, EPM 2022).
- Cada contenido del curso debe revisarse con el docente antes de marcarlo `publicada`.
