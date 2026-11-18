# DISEÑO — Rúbrica Corte 3 (Seguridad en Redes, CUC 2026-2)

**Estado:** diseño interno del docente (no publicar).  
**Corte 3:** una sola actividad, la rúbrica del 20 %, práctica y autoevaluable en la VM.  
**Plazo máximo:** sábado 28-nov-2026, 23:59.

---

## 1. Resumen de la rúbrica

- **5 criterios × 1,0 punto.** Nota = suma de los cinco criterios.
- **Aprobado:** 3,0 sobre 5,0.
- **Bonos opcionales**, tope final 5,0 (la nota nunca supera 5,0).
- **Autoevaluable:** el estudiante ejecuta `asur-lab check rubrica-c3` y obtiene su nota firmada.
- **Entrega:** `evidencia.tar.gz` + `resultado-rubrica.txt` por Teams.

---

## 2. Variantes (por último dígito del documento)

El estudiante escribe su variante en `~/labs/rubrica-c3/variante` (`A` o `B`) y su documento en `~/labs/rubrica-c3/estudiante` (solo el número; se usa para el hash de la evidencia, nunca se publica).

| Elemento | Variante A (par) | Variante B (impar) |
|---|---|---|
| Vector principal | SYN flood contra 10.30.0.10:80 | HTTP flood contra 10.30.0.10:80 |
| SSH del servidor | puerto 22 | puerto 2222 |
| Puertos del escaneo | 22, 443, 3306, 5432, 8080 | 2222, 3306, 5432, 6379, 8080, 8443, 9000, 9200, 11211, 27017 |
| Set dinámico | `bloqueados`, timeout 10 min | `escaneo`, timeout 15 min |
| Umbral HTTP | 10 nuevas conexiones/s por origen | 8 nuevas conexiones/s por origen |
| Umbral conexiones simultáneas | ct count over 30 | ct count over 20 |
| Bono | +0,2 bloqueo de escaneo por set dinámico con timeout | +0,3 alerta HTTP distinguida del SYN (dos firmas distintas, ambas disparan) |

---

## 3. Criterios de evaluación

### Criterio 1 — Detección (1,0)

Regla Suricata activa con `threshold … track by_src` acorde al vector de la variante. Al lanzar el ataque de su variante mediante el check, aparece una alerta del atacante con `sid` del estudiante en `eve.json`.

| Puntaje | Nivel |
|---|---|
| 1,0 | Regla con `track by_src` presente en `reglas/lab.rules` y alerta del atacante con sid del estudiante tras el ataque. |
| 0,5 | Regla presente pero sin umbral por origen, o alerta genérica sin sid identificable. |
| 0 | Sin regla, o sin alerta al lanzar el ataque. |

### Criterio 2 — Línea base y confirmación (1,0)

`evidencia/linea-base.txt` medido sin mitigación (con `./lab base 30` antes de aplicar reglas). `evidencia/confirmacion.txt` con salida real de `tcpdump` en fw (líneas con la IP del atacante) y `ss` en web.

| Puntaje | Nivel |
|---|---|
| 1,0 | Ambos archivos existen con salida real de tcpdump y ss; la línea base se midió SIN reglas de mitigación. |
| 0,5 | Uno de los dos archivos falta o tiene contenido incompleto/plantilla sin rellenar. |
| 0 | Sin evidencia de línea base ni confirmación. |

### Criterio 3 — Mitigación con continuidad (1,0)

Ruleset nftables con `limit rate over` por origen y `ct count over`. Durante el ataque lanzado por el check, el cliente legítimo obtiene ≥ 90 % HTTP 200 (30 peticiones); el atacante queda en un set dinámico o el contador de drop sube.

| Puntaje | Nivel |
|---|---|
| 1,0 | ≥ 90 % HTTP 200 del cliente legítimo durante el ataque; atacante contenido (set dinámico o contador de drop > 0). |
| 0,5 | < 90 % pero > 0 % HTTP 200 (mitigación parcial que afecta al legítimo). |
| 0 | 0 % HTTP 200 (p. ej. regla `drop` total sin `over` que corta todo). |

### Criterio 4 — Acceso no autorizado (1,0)

El check escanea desde `cliente` los puertos de la variante: alerta del SSH de su variante y del escaneo; los puertos no publicados no responden; contador de drop > 0; HTTP sigue en 200.

| Puntaje | Nivel |
|---|---|
| 1,0 | Alerta de escaneo y de SSH (puerto de la variante); puertos no publicados filtrados; contador de drop > 0; HTTP 200 mantenido. |
| 0,5 | Alerta parcial (solo escaneo o solo SSH) o puertos no publicados responden. |
| 0 | Sin alerta de escaneo/SSH, o HTTP cae durante el escaneo. |

### Criterio 5 — Evidencia íntegra (1,0)

`./lab evidencia` genera el paquete con los archivos anteriores, alertas guardadas y `nft list ruleset`. El check firma el resultado (sha256 de evidencia + variante + hash del documento) en `evidencia/resultado-rubrica.txt`.

| Puntaje | Nivel |
|---|---|
| 1,0 | `evidencia.tar.gz` generado, `resultado-rubrica.txt` con firma sha256 válida, todos los archivos anteriores presentes. |
| 0,5 | Paquete generado pero falta algún archivo o la firma no cuadra. |
| 0 | Sin paquete de evidencia o sin firma. |

---

## 4. Bonos (tope 5,0)

| Bono | Valor | Condición |
|---|---|---|
| A (variante A) | +0,2 | Bloqueo de escaneo por set dinámico con timeout (origen en `@bloqueados` con `flags dynamic,timeout`). |
| B (variante B) | +0,3 | Alerta HTTP distinguida del SYN: dos firmas Suricata distintas y ambas disparan al lanzar el ataque de su variante. |

- Máximo posible por bonos: la nota final **no pasa de 5,0**.
- Los bonos se verifican con `./lab check` en verde y con su evidencia en la carpeta.

---

## 5. Flujo del estudiante

1. `asur-lab iniciar rubrica-c3` (instala el paquete, carga imágenes de lab06, levanta el lab).
2. Escribe `~/labs/rubrica-c3/variante` (A|B) y `~/labs/rubrica-c3/estudiante` (número de documento).
3. Edita `reglas/nftables.fw` (mitigación nftables) y `reglas/lab.rules` (reglas Suricata con sid propio).
4. `./lab base 30` → `evidencia/linea-base.txt` (sin mitigación).
5. `./lab recargar` (aplica nftables y reinicia Suricata guardando alertas previas).
6. `./lab check` → ejecuta el verificador: lanza el ataque de su variante, mide continuidad, escanea, califica los 5 criterios + bonos.
7. `./lab evidencia` → genera `evidencia.tar.gz`.
8. Entrega `evidencia.tar.gz` + `evidencia/resultado-rubrica.txt` por Teams.

---

## 6. Flujo del verificador (`verificadores/rubrica_c3.py`)

El check (`asur-lab check rubrica-c3`):

1. Lee la variante desde `~/labs/rubrica-c3/variante` y el documento desde `~/labs/rubrica-c3/estudiante`.
2. Comprueba que el lab esté arriba (si no, informa y falla).
3. Criterio 1: inspecciona `reglas/lab.rules` buscando `threshold … track by_src` y el sid del estudiante; lanza el ataque de la variante y comprueba que aparece una alerta del atacante en `eve.json`.
4. Criterio 2: verifica `evidencia/linea-base.txt` y `evidencia/confirmacion.txt` (tcpdump en fw con IP del atacante, `ss` en web).
5. Criterio 3: inspecciona el ruleset nftables en fw buscando `limit rate over` y `ct count over`; lanza el ataque de la variante; mide que el cliente legítimo obtiene ≥ 90 % HTTP 200 (30 peticiones); verifica que el atacante quede en un set dinámico o que el contador de drop suba.
6. Criterio 4: escanea desde `cliente` los puertos de la variante; verifica alerta de SSH y de escaneo; verifica que puertos no publicados no respondan; verifica contador de drop > 0 y HTTP en 200.
7. Criterio 5: verifica `evidencia.tar.gz` y firma `evidencia/resultado-rubrica.txt` (sha256 de evidencia + variante + hash del documento).
8. Bonos: verifica condiciones de A o B según la variante.
9. Imprime resultado por criterio y nota total; devuelve código de salida 0 si aprueba (≥ 3,0), 1 si no.
10. Dura < 3 minutos y deja el lab como estaba.

---

## 7. Relación con el Lab 6

La rúbrica reusa la infraestructura del Lab 6 (contenedores `lab06-web`, `lab06-fw`, `lab06-ids`, `lab06-cliente`, `lab06-generador`; redes `10.20.10.0/24` y `10.30.0.0/24`). El paquete `rubrica-c3` depende de `lab06` instalado (imágenes ya cargadas) y no duplica los ~700 MB de imágenes.

El `lab` de `rubrica-c3` es una copia del `lab` del Lab 6 con los dos parches que hoy existen solo en la VM:
1. `cmd_up` libera redes de otros labs en `10.30.0.0/24` o `10.20.10.0/24` sin contenedores en uso (si están en uso, aborta con mensaje claro).
2. `reiniciar_suricata` guarda las alertas de `eve.json` en `evidencia/alertas-HHMMSS.json` antes de reiniciar.

---

## 8. Formato del paquete (catálogo 2027)

- `id`: `rubrica-c3`
- `versión`: `1.0.0`
- `estado`: `activo`
- `depende_de`: `lab06` (reusa sus imágenes; no trae `imagenes.tar.gz`)
- `url_paquete`: `/laboratorios/lab-rubrica-c3/paquete/paquete.tar.gz`
- Contenido del paquete: `lab` (con parches), `plantillas/` (nftables-base.fw, lab.rules), `reglas/` (vacías), `evidencia/`, `docker/`, `docker-compose.yml` (name: `rubrica-c3`, imágenes `lab06/*:latest` sin build).
