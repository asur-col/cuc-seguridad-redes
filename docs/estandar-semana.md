# Estándar de producción de una semana (instrucciones para quien produce)

Curso **Seguridad en Redes** · Universidad de la Costa (CUC) · 2026-2 · Ing. Rodolfo Cañas Cervantes.
Lee también `docs/analisis-tematico.md` (tabla 2.4: contenido por parte de cada semana) y `docs/fuentes-recursos.md` (qué recursos y licencias se permiten).

## 1. Qué produces

Solo archivos dentro de `fuentes/SNN/` (tu semana):

| Archivo | Contenido |
|---|---|
| `semana.json` | Ya existe. **No cambies** `titulo`, `archivo`, `semana`, `etiqueta`, `fechas`, `publicada`. Sí puedes ajustar `titulo_corto`/`descripcion`, los `titulo`/`temas` de cada parte, y **debes llenar** `portada_guion` y cada `partes[i].guion` (40–70 palabras: presenta la parte y lo que se verá). |
| `parte1.html` … `parte4.html` | **14 diapositivas de contenido cada una** (mín. 13, máx. 15). Solo elementos `<section class="slide">`; nada de `<html>`, `<head>`, CSS ni JS. |

No edites nada fuera de `fuentes/SNN/` (ni `assets/`, ni `index.html`, ni las herramientas). El constructor genera el HTML final en la raíz.

Comandos (desde la raíz del repo):
```bash
python3 herramientas/construir.py SNN
python3 herramientas/auditar.py <archivo>.html --capturas /tmp/capturas-SNN
```
Revisa las capturas PNG tú mismo (herramienta Read) antes de entregar.

## 2. Formato de una diapositiva

```html
<section class="slide" data-fuente="NIST SP 800-41 Rev.1 (2009), §4.1">
  <div class="kicker">Concepto</div>              <!-- 1–3 palabras -->
  <h2>Título afirmativo de máximo ~60 caracteres</h2>
  <p class="sub">Una línea que dice la idea principal.</p>   <!-- opcional, máx. ~110 caracteres -->
  <div class="s-body"> … SVG y/o componentes … </div>
  <aside class="notes">Guion de narración …</aside>
</section>
```

- `data-fuente`: fuente corta para el pie (norma, RFC, informe con año; o "Diagrama propio · concepto: …"). Máx. ~110 caracteres.
- El constructor agrega cabecera con logo, pie con "Semana N · Parte X de 4", numeración, portada y divisorias. No las escribas tú.
- Área útil de `.s-body`: **1184 px de ancho × ~520 px de alto** (menos si hay `.sub` largo). Nada debe pasar del pie.

## 3. Gráficos (lo más importante)

- **≥ 13 de 14 diapositivas por parte con gráfico; ≥ 9 de 14 con diagrama real**: topología de red, secuencia de protocolo, flujo/pipeline, árbol de decisión, línea de tiempo, arquitectura por capas. Una rejilla de tarjetas con íconos **no** cuenta como diagrama.
- Copia y adapta los 6 patrones de `fuentes/_EJEMPLO/parte1.html` (render en `plantillas/ejemplo-semana.html`): topología por zonas, secuencia, pipeline, comparación lado a lado, consola + diagrama, línea de tiempo/caso.
- SVG en línea: `<svg class="dgm" viewBox="0 0 1184 H">` con H ≤ 520 (o un ancho menor si va en columna). Llena el espacio: evita dejar más de un tercio de la diapositiva vacía.
- Íconos: **solo** la biblioteca propia, con `<use href="#i-NOMBRE" x y width height style="color:#A6192E"/>`. Disponibles:
  `router switch switch-l3 firewall ngfw ids ips sensor tap ap balanceador proxy vpn tunel internet nube wan cable servidor servidor-web bd pc portatil movil impresora iot camara plc contenedor vm dns correo api sede datacenter usuario grupo admin atacante bot ia candado candado-abierto llave certificado escudo escudo-alerta alerta bloqueo ok huella token malware ransomware phishing bug parche siem log grafica lupa escaner paquete terminal engranaje automatizacion reloj lista documento ley respaldo`.
  **Prohibido**: íconos de AWS/Azure/Cisco/Google, imágenes externas, PNG/JPG en base64, emojis como ícono.
- Paleta: vino `#A6192E`, vino oscuro `#7E1223`, dorado `#D4AF37`, dorado oscuro (texto) `#8A6D1D`, texto `#2A2A2A`, gris `#5F5F5F`, fondos `#F9EEF0` (vino claro), `#FBF6E7` (dorado claro), `#F4F4F2`; verde solo para "permitido/ok" `#2E7D4F` / `#E8F3EC`.
- Texto dentro de SVG: mínimo `font-size="12"`; títulos de nodo 13–15 negrita. Nada de texto encimado: revisa en la captura.
- IDs de `<marker>` y otros `id` **únicos en toda la semana**: prefijo `sNNpXdY-` (p. ej. `s09p2d5-flecha`).
- Componentes HTML disponibles (CSS ya cargado): `.cols/.col/.col-2`, `.card` (+ `.dark`, `.gold`, `.white`), `.note`, `.warn`, `.caso`, `.lab-box`, `.kpi > .k > .n/.l`, `.lista`, `table.t`, `pre.con` (consola oscura; resaltado con `<span class="c|k|v|p">`), `code`, `.pill`, `.refs`.
- Tamaño de texto del cuerpo: 14–16 px. Máximo ~70 palabras visibles por diapositiva fuera del SVG: el detalle va al guion.

## 4. Contenido

- Sigue la fila de tu semana en `docs/analisis-tematico.md` §2.4 y el título oficial de `semana.json` (que **no** se cambia). Ajusta los títulos de parte si mejora el hilo, sin salirte del tema oficial.
- Enfoque: **concepto genérico de industria → ejemplos con 2–3 tecnologías o fabricantes distintos** (p. ej., OPNsense/pfSense, Fortinet, Palo Alto, Check Point, Cisco, nftables, Suricata/Snort/Zeek, Wazuh/Elastic/Splunk; nubes solo como un ejemplo más, varias a la vez). Ningún producto es requisito.
- Práctica: la plataforma del curso es **VirtualBox + OPNsense + Alpine Linux** (topología del Lab 1: zonas LAN, DMZ, INTERNA, ADMIN), **Cisco Packet Tracer** y salas **gratuitas** de **TryHackMe**. La Parte 4 cierra con una práctica guiada (pasos, comandos y verificación) sobre esa plataforma. **No** menciones notas, porcentajes, rúbricas ni actividades evaluables.
- **Caso aplicado colombiano** en la Parte 4 (y, si encaja, alguno antes): incidentes reales documentados (IFX Networks 2023, Keralty 2022, EPM 2022, Rama Judicial, etc.), normativa (Ley 1273 de 2009, Ley 1581 de 2012, CONPES 3995, ColCERT/CSIRT) o un escenario realista de una empresa de la región Caribe (Barranquilla, Cartagena, Santa Marta) claramente marcado como ficticio.
- Cada parte: 1ª diapositiva = "de dónde venimos / qué veremos"; última = síntesis de la parte ("Lo que queda de la Parte X"). La última de la Parte 4 = "Qué sigue" (puente a la semana siguiente según el calendario oficial). La penúltima de la Parte 4 = referencias (APA, `.refs`).
- **Precisión técnica**: comandos que funcionen tal como se escriben, números de puerto/RFC/NIST correctos, sintaxis real. **No inventes cifras**: cada número de un informe lleva fuente y año en `data-fuente`; si no estás seguro, no pongas el número.
- Ortografía española completa (tildes, ¿?, ¡!). Tono: claro, profesional, en segunda persona plural ("ustedes") o impersonal.

## 5. Guion de narración (`<aside class="notes">`)

- **150–175 palabras por diapositiva de contenido** (≈ 1 min con voz sintética). Objetivo por parte: **2 000–2 400 palabras** → video de ~14–16 min.
- Narra lo que muestra el diagrama, en orden visual ("arriba…", "a la izquierda…"), y agrega la explicación que no cabe en pantalla. No leas la diapositiva textualmente.
- Escrito para voz sintética (es-CO-GonzaloNeural): oraciones de ≤ 25 palabras; sin viñetas, símbolos, flechas, emojis ni paréntesis largos; escribe "barra veinticuatro" para /24, "puerto cuatrocientos cuarenta y tres" o "el puerto 443" (ambos funcionan), siglas en mayúscula (TLS, VLAN, SIEM). Nada de HTML dentro del guion.
- Sin muletillas de video ("como ven en pantalla" una vez por parte como máximo). La primera diapositiva de cada parte retoma la anterior; la última cierra con una idea fuerza.

## 6. Criterios de aceptación (los audita el coordinador)

1. `construir.py` sin errores; 4 partes de 13–15 diapositivas de contenido.
2. `auditar.py`: 0 desbordes; gráfico ≥ 90 %; diagrama ≥ 60 %; guion 1 900–2 500 palabras por parte; 0 diapositivas sin guion.
3. Revisión visual de capturas: sin texto encimado, sin cortes, sin zonas vacías grandes, legible a 1280×720.
4. Precisión técnica y fuentes verificables; sin íconos de marca; sin cifras inventadas.
5. Título oficial intacto; nada de actividades evaluables.
