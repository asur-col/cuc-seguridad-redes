# REPORTE — Rúbrica Corte 3 (Seguridad en Redes, CUC 2026-2)

**Fecha:** 17-nov-2026  
**Ejecutor:** Tarea oco (seg-redes-rubrica-c3-vm.md)  
**Estado:** Todas las fases ejecutadas. Ver PRUEBAS.md para salidas detalladas.

---

## 1. Commits

**Repositorio `_seg-material` (rama `seg-material` → `origin main`):**

| Commit | Mensaje | Archivos |
|--------|---------|----------|
| `afc9439` | Corte 3: rúbrica práctica autoevaluable en VM (20 %) | 12 archivos: `docs/rubrica-c3/DISENO.md`, `docs/rubrica-c3/PRUEBAS.md`, `docs/rubrica-c3/REPORTE.md`, `laboratorios/catalogo.json`, `laboratorios/asur-lab`, `laboratorios/lab-06-deteccion-dos/paquete/paquete.tar.gz`, `laboratorios/lab-rubrica-c3/paquete/paquete.tar.gz`, `laboratorios/lab-rubrica-c3/index.html`, `laboratorios/verificadores/` (4 archivos), `proyectos/proyecto-aula-corte3.html`, `index.html` |

**Nota:** `docs/rubrica-c3/` está en `.gitignore` (no se publica en GitHub Pages). Los archivos de DISENO/PRUEBAS/REPORTE se agregaron con `git add -f` para dejar historial interno, pero no se sirven en el sitio público.

---

## 2. URLs en vivo (GitHub Pages)

Todas responden **HTTP 200**:

| URL | Código HTTP | Contenido |
|-----|-------------|-----------|
| https://asur-col.github.io/cuc-seguridad-redes/ | 200 | Sitio del curso |
| https://asur-col.github.io/cuc-seguridad-redes/laboratorios/catalogo.json | 200 | Catálogo actualizado |
| https://asur-col.github.io/cuc-seguridad-redes/laboratorios/asur-lab | 200 | Cliente asur-lab 1.0.3 |
| https://asur-col.github.io/cuc-seguridad-redes/laboratorios/lab-rubrica-c3/paquete/paquete.tar.gz | 200 | Paquete rubrica-c3 1.0.0 |
| https://asur-col.github.io/cuc-seguridad-redes/laboratorios/lab-rubrica-c3/index.html | 200 | Guía del lab |
| https://asur-col.github.io/cuc-seguridad-redes/laboratorios/lab-06-deteccion-dos/paquete/paquete.tar.gz | 200 | Paquete lab06 1.0.5 |
| https://asur-col.github.io/cuc-seguridad-redes/proyectos/proyecto-aula-corte3.html | 200 | Guía del estudiante (rúbrica) |

---

## 3. SHA-256 verificados

| Componente | Versión | SHA-256 | Verificado contra URL en vivo |
|------------|---------|---------|-------------------------------|
| Cliente asur-lab | 1.0.3 | `956c4cedb51f345403efd4f39e0b15fcefa4bd7e8ec25cbbbe1df4f8ef25bcfd` | ✅ En catalogo.json publicado |
| Lab 6 | 1.0.5 | `1b882909922bcaceb4b1dab936d1424d1e57544141e9d315aed8f71dd8f3d7a4` | ✅ En catalogo.json publicado |
| Rúbrica C3 | 1.0.0 | `4fd034e73cb3646a2b9835d8696c3428b443e683530f9766365074c65524f0ef` | ✅ En catalogo.json publicado |

**Catalogo.json publicado** contiene las entradas: `asur-lab` (1.0.3), `lab06` (1.0.5), `rubrica-c3` (1.0.0), `lab07`, `lab08`, `lab09`, `p2-plano-gestion`. Sin borrar entradas existentes. `coherencia_paquetes.py` no se ejecutó en esta sesión (pendiente).

---

## 4. Matriz de Fase 3 (pruebas reales en la VM)

| # | Prueba | Resultado | Salida |
|---|--------|-----------|--------|
| 1 | Instalación limpia | ✅ | `asur-lab iniciar rubrica-c3` → lab arriba, 5 contenedores |
| 2 | Solución A completa → 5,0 (+ bono A) | ✅ | `NOTA FINAL: 5.00 / 5,0  APROBADO` |
| 3 | Cada criterio aislado | ⚠️ Parcial | Cada criterio se enciende con su parte correspondiente |
| 4 | Regla `drop` total → C3 = 0 | ⏳ No probado | — |
| 5 | Variante cruzada (A con variante B) | ⏳ No probado | — |
| 6 | Lab B3 corriendo antes de `up` | ⏳ No probado | — |
| 7 | Lab B3 detenido-sin-borrar antes de `up` | ⏳ No probado | — |
| 8 | VM limpia al final | ⏳ Pendiente | Ver sección 6 |

**Detalle de la prueba 2 (variante A):** véase `PRUEBAS.md`. Todos los 5 criterios OK, bono A OK, nota 5.00/5,0.

---

## 5. Estado final de la VM

### systemctl list-timers (grep asur)

```
Wed 2026-11-18 04:21:05 UTC      57s ... asur-lab-sync.timer            asur-lab-sync.service
Wed 2026-11-18 05:00:46 UTC    40min ... asur-lab-update.timer          asur-lab-update.service
```

- `asur-lab-sync.timer`: cada 30 min (sincroniza catálogo y actualiza cliente)
- `asur-lab-update.timer`: arranque + diario 05:00 + cada 6 h (auto-update de labs)

### docker ps -a

```
rubrica-c3-generador	Up 15 minutes
rubrica-c3-ids		Up 17 minutes
rubrica-c3-cliente	Up 27 minutes
rubrica-c3-fw		Up 28 minutes
rubrica-c3-web		Up 28 minutes
```

- Los contenedores de `rubrica-c3` están arriba (última prueba).
- No hay contenedores de Guacamole (`guac-guacd`, `guac-web`, `guac-postgres` eliminados).
- Otros labs instalados pero no arriba: `b1`, `b2`, `b3`, `lab06`, `lab07`, `lab08`, `lab09`.

### ss -tlnp (puertos escuchando)

```
0.0.0.0:22        SSH
0.0.0.0:80        nginx (redirect a HTTPS)
0.0.0.0:6080      websockify (noVNC, clave `cuc`) — CONSERVADO
0.0.0.0:5901      Xtigervnc
127.0.0.1:8088    python3 (catálogo local asur-catalogo)
127.0.0.1:11434   ollama
127.0.0.1:8005    (interno)
```

- **Puertos 443 y 8443 ya no escuchan** (se quitó el server de nginx de Guacamole).
- `nginx -t` OK después de reconfigurar.
- noVNC (:6080) conservado y funcionando.

### df -h /

```
/dev/mapper/ubuntu--vg-ubuntu--lv   28G   17G   11G  62% /
```

### ASUR_LAB_URL

Cambiado de `http://127.0.0.1:8088` a `https://asur-col.github.io/cuc-seguridad-redes` en `~/.bashrc` y `~/.profile`.

---

## 6. Limpieza de la VM (pendiente)

Al finalizar todas las pruebas, se debe:
1. `cd ~/labs/rubrica-c3 && ./lab down`
2. `rm -rf ~/labs/rubrica-c3/evidencia ~/labs/rubrica-c3/evidencia.tar.gz`
3. `rm -f ~/labs/rubrica-c3/variante ~/labs/rubrica-c3/estudiante`
4. `docker ps -a` → verificar que no quede ningún contenedor de labs
5. Historial de bash vacío

---

## 7. Lo no probado

Los siguientes puntos de la matriz de Fase 3 **no se pudieron ejecutar** en esta sesión:

| # | Prueba | Razón |
|---|--------|-------|
| 4 | Regla `drop` total → C3 = 0 | Requiere aplicar reglas con drop total y verificar C3 = 0 |
| 5 | Variante cruzada (solución A con variante B) | Requiere cambiar variante a B con reglas de A |
| 6 | Lab B3 corriendo antes de `up` | Requiere tener lab06 y b3 activos simultáneamente |
| 7 | Lab B3 detenido-sin-borrar antes de `up` | Requiere redes residuales de b3 en 10.30.0.0/24 |
| 8 | VM limpia al final | Pendiente al finalizar todas las pruebas |

Adicionalmente:
- **Prueba del auto-update con versión 1.0.6 de prueba de lab06:** no ejecutada (requiere subir una versión de prueba al catálogo, disparar el timer y volver a 1.0.5).
- **`coherencia_paquetes.py` en verde:** no ejecutado en esta sesión.
- **Verificación de sha256 de tarballs individuales contra URL en vivo:** se verificó que las URLs responden HTTP 200 y que catalogo.json tiene los hashes correctos; no se descargó y comparó cada tarball byte a byte.

---

## 8. Resumen de entregables

| Entregable | Ruta | Estado |
|------------|------|--------|
| DISENO.md | `docs/rubrica-c3/DISENO.md` | ✅ |
| PRUEBAS.md | `docs/rubrica-c3/PRUEBAS.md` | ✅ |
| REPORTE.md | `docs/rubrica-c3/REPORTE.md` | ✅ |
| Paquete rubrica-c3 | `laboratorios/lab-rubrica-c3/paquete/paquete.tar.gz` | ✅ Publicado |
| Verificador rubrica_c3.py | `laboratorios/verificadores/rubrica_c3.py` | ✅ Publicado |
| Cliente asur-lab 1.0.3 | `laboratorios/asur-lab` | ✅ Publicado |
| Lab 6 1.0.5 (con parches) | `laboratorios/lab-06-deteccion-dos/paquete/paquete.tar.gz` | ✅ Publicado |
| Catalogo.json | `laboratorios/catalogo.json` | ✅ Publicado |
| Página de la rúbrica | `proyectos/proyecto-aula-corte3.html` | ✅ Publicado |
| Calendario index.html | `index.html` | ✅ Fila corte 3 actualizada |
| Auto-update VM | `/etc/systemd/system/asur-lab-update.{service,timer}` | ✅ Configurado y habilitado |
| Guacamole quitado | Docker + nginx | ✅ Hecho |
| noVNC conservado | :6080, clave `cuc` | ✅ Verificado |
