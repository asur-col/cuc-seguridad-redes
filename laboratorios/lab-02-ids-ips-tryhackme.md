# Laboratorio 2 — Detección de Intrusos con Snort (IDS/IPS)
**Seguridad en Redes · Unidad 1 · Actividad 2 del 10% · Trabajo asíncrono en TryHackMe**
Ing. Rodolfo Cañas Cervantes — Universidad de la Costa (CUC) · Periodo 2026-2 · Semana 4

**Datos rápidos:** 1 h 45 min – 2 h · 10% Unidad 1 · Actividad 2 · 100% asíncrono · sala gratuita · Snort 2.9.7.0
*(Versión Markdown del instructivo; los diagramas FIG A y FIG 1 están en la versión HTML.)*

## OBJETIVO
Practicar los tres modos de Snort (sniffer, logger, NIDS) sobre la sala gratuita "Snort" de TryHackMe y escribir tus propias reglas de detección.

## CONCEPTO — IDS vs IPS
- **IDS**: detección pasiva — analiza una copia del tráfico y alerta.
- **IPS**: prevención en línea — bloquea en el camino.
En este laboratorio Snort actúa como **NIDS pasivo**.

## ANATOMÍA DE UNA REGLA SNORT
Acción + tráfico (protocolo, origen, dirección, destino) + opciones entre paréntesis. Ver FIG 2 en la versión HTML.

## PREVIO
- Cuenta gratuita en tryhackme.com · navegador actualizado · ~1.5 h continuas (puedes pausar).
- La VM usa **Snort 2.9.7.0**: sintaxis Snort 2. Suricata NO acepta `<>`. El número de build exacto lo confirmas tú con `snort -V` (es una pregunta de la sala).
- La VM gratuita expira ~1 hora por arranque: planifica en bloques; el progreso de respuestas se conserva.

## FASE 0 · Arranque (5 min) — Tasks 1–2
1. Entra a https://tryhackme.com/room/snort · Start Machine → Show Split View.
2. ```
   cd ~/Desktop/Task-Exercises
   ./.easy.sh
   ```
   Es un archivo **oculto** (empieza con punto) — `./easy.sh` sin el punto no lo encuentra. Salida esperada: **Too Easy!**

## FASE 1 · Conceptos (10 min) — Task 3
Quiz: NIDS/HIDS (detección, red/host) · NIPS/HIPS/NBA/WIPS (prevención, red/host/comportamiento/inalámbrica) y baselining (periodo de entrenamiento de NBA).

## FASE 2 · Instalación y validación (10 min) — Task 4
```
snort -V
sudo snort -c /etc/snort/snort.conf -T
sudo snort -c /etc/snort/snortv2.conf -T
```
`-V` te da la versión y el build (anótalo, es respuesta de la sala). `-c archivo -T` valida y reporta cuántas reglas cargó — compara snort.conf (completo) contra snortv2.conf (mínimo, muchas menos reglas).

## FASE 3 · Modo sniffer (15 min) — Task 5
```
sudo snort -v
sudo snort -v -i eth0
sudo snort -vde -i eth0
sudo snort -X -i eth0
```

## FASE 4 · Modo logger (20 min) — Task 6
```
sudo snort -dev -K ASCII -l .
ls
sudo snort -r snort.log.* -n 10
sudo snort -r snort.log.* -X
sudo snort -r snort.log.* 'tcp port 80'
```
Los logs ASCII no se releen con Snort; solo el binario. Se crea una carpeta con nombre de IP (ej. 145.254.160.237 — la que pregunta la sala) y dentro, archivos por protocolo/puerto (ej. UDP:36648-53).

## FASE 5 · Modo NIDS (20 min) — Task 7
```
sudo snort -c /etc/snort/snort.conf -A full -l .
```
Genera tráfico (traffic-generator.sh → TASK 7) y detén con Ctrl+C: **el resumen estadístico solo aparece al detener**. Variantes: -A console / fast / cmg.

## FASE 6 · Reglas propias + pcaps (25 min) — Tasks 8–9
```
sudo snort -c /etc/snort/snort.conf -A full -l . -r mx-1.pcap
sudo snort -c /etc/snort/snortv2.conf -A console -l . -r mx-1.pcap
sudo snort -c /etc/snort/snortv2.conf -A console --pcap-list="mx-2.pcap mx-3.pcap" --pcap-show
sudo gedit local.rules      # o nano
```
Elementos: opción no-payload `id:35369` (filtra el campo IP ID — no es `content`, ese keyword busca dentro del payload) · flags:S · flags:PA · `sameip` (alerta cuando origen y destino son la misma IP) · `sid` ≥ 1.000.000 (Snort reserva <100 para el motor y 100-999.999 para reglas del build; el rango de usuario empieza en 1.000.000) · rev incremental.

## FASE 7 · Lectura final (5 min) — Tasks 10–11
Lógica interna y buenas prácticas → sala al 100%.

## ENTREGABLE (PDF único)
1. Progreso de la sala con tu usuario **y fecha visibles**.
2. Tu regla completa.
3. Evidencia de la alerta disparada.
4. Explicación técnica de 3–5 líneas.

## RÚBRICA (Actividad 2 · 10% U1)
| Criterio | Peso |
|---|---|
| Progreso completo con usuario visible | 25% |
| Regla propia con sintaxis correcta | 30% |
| Evidencia de la alerta | 25% |
| Explicación técnica | 20% |

## TROUBLESHOOTING
| Síntoma | Qué hacer |
|---|---|
| Resumen estadístico no aparece | Detén Snort con Ctrl+C |
| Permission denied en snort.log.* | sudo snort -r … o sudo chown $USER snort.log.* |
| Generador no corre | sudo ./traffic-generator.sh y elige la TASK exacta |
| ASCII no se relee | Solo binario: snort -r |
| Mi regla no alerta | Comenta reglas viejas (#), borra logs, prueba -A console |
| sameip no cuadra | `sameip` = origen y destino son la MISMA IP (no filtra broadcast/multicast); revisa que apuntes al protocolo correcto y que borraste el archivo de alertas anterior |
| No sé editar local.rules | sudo gedit local.rules o nano |
| VM expira ~1 hora | Dos arranques; respuestas conservadas |

*Existen walkthroughs públicos: usarlos se nota en la revisión. Cada captura debe mostrar tu usuario y la fecha.*
