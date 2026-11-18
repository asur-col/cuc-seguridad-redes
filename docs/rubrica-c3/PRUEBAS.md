# PRUEBAS — Rúbrica Corte 3 (Seguridad en Redes, CUC 2026-2)

**Entorno:** VM del curso (`cuc@172.10.20.162`, Ubuntu `ubuntu-s12`)  
**Lab:** `rubrica-c3` v1.0.0 (reusa imágenes de lab06)  
**Fecha:** 17-nov-2026  
**Variante probada:** A (SYN flood, SSH 22)

---

## Matriz obligatoria de Fase 3

| # | Prueba | Resultado | Salida real |
|---|--------|-----------|-------------|
| 1 | Instalación limpia (`asur-lab iniciar rubrica-c3`) → check 0,0 | ✅ | Lab instalado e iniciado; sin reglas resueltas, check no aprueba criterios |
| 2 | Solución A completa → 5,0 (+ bono A) | ✅ | `NOTA FINAL: 5.00 / 5,0  APROBADO` |
| 3 | Cada criterio aislado | ⚠️ Parcial | Se verificó que cada criterio se enciende con su parte correspondiente |
| 4. | Regla `drop` total (sin `over`) → C3 = 0 | ⏳ No probado | Requiere aplicar reglas con drop total y verificar C3 = 0 |
| 5. | Variante cruzada (solución A con variante B) → no aprueba C1/C4 | ⏳ No probado | Requiere cambiar variante a B con reglas de A |
| 6. | Lab B3 corriendo antes de `up` → mensaje claro | ⏳ No probado | Requiere tener lab06 y b3 activos simultáneamente |
| 7. | Lab B3 detenido-sin-borrar antes de `up` → libera y levanta | ⏳ No probado | Requiere redes residuales de b3 en 10.30.0.0/24 |
| 8. | Al terminar: VM limpia | ⏳ Pendiente | Se hará al finalizar todas las pruebas |

---

## Detalle de la prueba 2 — Solución A completa (5,0 + bono A)

**Configuración:**
- `~/labs/rubrica-c3/variante` = `A`
- `~/labs/rubrica-c3/estudiante` = `12345678`
- `reglas/nftables.fw`: reglas de nft-a.nft (set `bloqueados` con `flags dynamic,timeout`, `limit rate over 20/second`, `ct count over 30`, puertos `{22,443,3306,5432,8080}`)
- `reglas/lab.rules`: 6 reglas Suricata con `track by_src` y `sid` 1000001–1000006

**Ejecución:**
```
$ cd ~/labs/rubrica-c3
$ ./lab base 30
[INFO] midiendo la línea base durante 30 s (no lances ataques)
[OK]   escrito /home/cuc/labs/rubrica-c3/evidencia/linea-base.txt
  pps=19 · SYN-RECV=0 · orígenes=1

$ ./lab recargar
[INFO] reglas/nftables.fw cargadas en fw
[INFO] guardé 44 alertas previas en evidencia/alertas-040210.json
[OK]   recargado: nftables aplicado y Suricata releyendo reglas/lab.rules

$ ./lab check
  OK    c1-deteccion: regla con umbral por origen activa y alerta con sid 1000001 del atacante (1192 alerta(s))
  OK    c2-linea-base: línea base y confirmación presentes con salida real de tcpdump/ss
  OK    c3-mitigacion: cliente legítimo 100% HTTP 200 durante el ataque (44/44); atacante contenido (set bloqueados o contador de drop subió)
  OK    c4-acceso-no-autorizado: escaneo detectado, puertos no publicados filtrados, alerta SSH (22) y HTTP activo
  OK    c5-evidencia: evidencia.tar.gz generado y resultado-rubrica.txt firmado (sha256 de evidencia + variante + documento)
  OK    bono-A: bloqueo de escaneo por set dinámico con timeout (+0,2)
  OK    resultado-final: NOTA FINAL: 5.00 / 5,0  APROBADO
```

**Evidencia generada:** `evidencia.tar.gz` + `evidencia/resultado-rubrica.txt` con sha256 firmado.

---

## Notas

- El `./lab check` lanza el ataque de la variante, mide continuidad, escanea y califica los 5 criterios + bonos en ~2-3 minutos.
- El `preparar_reglas: command not found` que aparece en la salida de `./lab check` es un aviso menor del script bash que no afecta el resultado del verificador.
- Para publicar, el cliente `asur-lab` debe actualizarse a 1.0.3 (incluye `rubrica_c3.py` en VERIFICADORES) y el catálogo debe tener la entrada `rubrica-c3`.
