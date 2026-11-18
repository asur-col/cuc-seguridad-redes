"""Verificador de la rúbrica Corte 3 (Seguridad en Redes · CUC 2026-2).

Estilo de base.py: usa Contexto (nunca subprocess/open directo), devuelve
lista de {id, ok, mensaje, pista} y soporta --json vía run.py.

El check lanza él mismo el ataque de la variante, mide continuidad y escanea;
dura < 3 min y deja el lab como estaba.
"""
import hashlib, json, os, re, time
from .base import falla, ok

ID = "rubrica-c3"
TITULO = "Rúbrica Corte 3 — Detección y mitigación de DoS (20 %)"

LAB_DIR = os.path.expanduser("~/labs/rubrica-c3")
VARIANTE_FILE = os.path.join(LAB_DIR, "variante")
ESTUDIANTE_FILE = os.path.join(LAB_DIR, "estudiante")
REGLAS_RULES = os.path.join(LAB_DIR, "reglas", "lab.rules")
REGLAS_NFT = os.path.join(LAB_DIR, "reglas", "nftables.fw")
EVIDENCIA_DIR = os.path.join(LAB_DIR, "evidencia")
LINEA_BASE = os.path.join(EVIDENCIA_DIR, "linea-base.txt")
CONFIRMACION = os.path.join(EVIDENCIA_DIR, "confirmacion.txt")
EVIDENCIA_TGZ = os.path.join(EVIDENCIA_DIR, "..", "evidencia.tar.gz")
RESULTADO = os.path.join(EVIDENCIA_DIR, "resultado-rubrica.txt")

# Sal fija para control de integridad del archivo resultado-rubrica.txt
SAL_CONTROL = "asur-cuc-segredes-2026-corte3-integ"

# Contenedores del compose rubrica-c3 (nombre exacto de Docker).
CONT = {
    "web": "rubrica-c3-web",
    "fw": "rubrica-c3-fw",
    "ids": "rubrica-c3-ids",
    "cliente": "rubrica-c3-cliente",
    "generador": "rubrica-c3-generador",
}

# Puertos y vector de ataque por variante.
VARIANTES = {
    "A": {
        "ssh": 22,
        "ataque": "syn",
        "atacante_ip": "10.20.10.71",
        "escaneo": [22, 443, 3306, 5432, 8080],
        "set": "bloqueados",
    },
    "B": {
        "ssh": 2222,
        "ataque": "http",
        "atacante_ip": "10.20.10.91",
        "escaneo": [2222, 3306, 5432, 6379, 8080, 8443, 9000, 9200, 11211, 27017],
        "set": "escaneo",
    },
}

WEB_IP = "10.30.0.10"
FW_IP = "10.20.10.2"


def calcular_control(nota_str, variante, h_doc, sha_evidencia, fecha):
    """Calcula sha256(nota|variante|documento_hash|sha256_evidencia|fecha|sal)."""
    cadena = "%s|%s|%s|%s|%s|%s" % (nota_str, variante, h_doc, sha_evidencia, fecha, SAL_CONTROL)
    return hashlib.sha256(cadena.encode("utf-8")).hexdigest()


def verificar_resultado_archivo(ruta):
    """Comprueba la integridad de un archivo resultado-rubrica.txt entregado."""
    if not os.path.isfile(ruta):
        print("ERROR: el archivo '%s' no existe" % ruta)
        return False
    campos = {}
    with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
        for linea in f:
            linea = linea.strip()
            if "=" in linea:
                k, v = linea.split("=", 1)
                campos[k.strip()] = v.strip()

    control_guardado = campos.get("control", "")
    nota = campos.get("nota", "")
    variante = campos.get("variante", "")
    doc_hash = campos.get("documento_hash", "")
    sha_evid = campos.get("sha256_evidencia", "")
    fecha = campos.get("fecha", "")

    if not (control_guardado and nota and variante and doc_hash and sha_evid and fecha):
        print("RECHAZADO: faltan campos obligatorios en '%s'" % ruta)
        return False

    esperado = calcular_control(nota, variante, doc_hash, sha_evid, fecha)
    if control_guardado.lower() == esperado.lower():
        print("OK: control de integridad verificado (nota: %s, variante: %s, doc_hash: %s)" % (nota, variante, doc_hash))
        return True
    else:
        print("RECHAZADO: control de integridad no coincide (el archivo fue modificado)")
        return False


def _leer_archivo(ctx, ruta):
    try:
        v = ctx.leer(ruta)
        return v.strip() if v else ""
    except Exception:
        return ""


def _ejecutar(ctx, comando, timeout=25):
    c, salida = ctx.ejecutar(comando, timeout=timeout)
    return c, (salida or "")


def _lab_arriba(ctx):
    """Devuelve True si los 5 contenedores de rubrica-c3 están running."""
    for nombre in CONT.values():
        c, out = _ejecutar(ctx,
            "docker ps -q --filter 'name=^/%s$'" % nombre, timeout=10)
        if c != 0 or not out.strip():
            return False
    return True


def _nombres_servicio(ctx):
    """Devuelve el container_id real de cada servicio (por si el compose usa
    prefijo distinto). Fallback a los nombres fijos de CONT."""
    resultado = {}
    for clave, nombre in CONT.items():
        c, out = _ejecutar(ctx,
            "docker compose -p rubrica-c3 ps -q %s" % clave, timeout=10)
        cid = out.strip().splitlines()[0] if out.strip() else ""
        resultado[clave] = cid or nombre
    return resultado


def _sid_de_reglas(reglas_texto):
    """Extrae el primer sid de las reglas Suricata."""
    m = re.search(r'sid\s*:\s*(\d+)', reglas_texto)
    return m.group(1) if m else None


def _obtener_todas_alertas(ctx):
    """Devuelve una lista de dicts con todas las alertas en eve.json
    y en evidencia/alertas-*.json (guardadas al recargar Suricata)."""
    alertas = []
    ids = CONT["ids"]
    c, out = _ejecutar(ctx,
        "docker exec %s cat /var/log/suricata/eve.json 2>/dev/null || true" % ids,
        timeout=25)
    for linea in out.splitlines():
        linea = linea.strip()
        if not linea:
            continue
        try:
            d = json.loads(linea)
            if d.get("event_type") == "alert":
                alertas.append(d)
        except Exception:
            pass

    # Alertas preservadas en evidencia/alertas-*.json
    if os.path.isdir(EVIDENCIA_DIR):
        try:
            for nom in sorted(os.listdir(EVIDENCIA_DIR)):
                if nom.startswith("alertas-") and nom.endswith(".json"):
                    ruta = os.path.join(EVIDENCIA_DIR, nom)
                    try:
                        with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
                            for linea in f:
                                linea = linea.strip()
                                if not linea:
                                    continue
                                try:
                                    d = json.loads(linea)
                                    if d.get("event_type") == "alert":
                                        alertas.append(d)
                                except Exception:
                                    pass
                    except OSError:
                        pass
        except OSError:
            pass
    return alertas


def _contar_lineas_cliente(ctx):
    cli = CONT["cliente"]
    c, out = _ejecutar(ctx,
        "docker exec %s sh -c 'wc -l < /var/log/cliente/respuestas.log 2>/dev/null || echo 0'" % cli,
        timeout=15)
    try:
        return int(out.strip().splitlines()[-1]) if out.strip() else 0
    except ValueError:
        return 0


def _segmento_200(ctx, antes, despues):
    """Devuelve (pos, total) de respuestas 200 del cliente entre antes y despues."""
    cli = CONT["cliente"]
    total = despues - antes
    if total <= 0:
        return 0, 0
    c, out = _ejecutar(ctx,
        "docker exec %s sh -c \"tail -n +$((%d+1)) /var/log/cliente/respuestas.log | head -n %d | awk '\\$2==\\\"200\\\"' | wc -l\""
        % (cli, antes, total), timeout=20)
    try:
        pos = int(out.strip().splitlines()[-1]) if out.strip() else 0
    except ValueError:
        pos = 0
    return pos, total


def _scaneo_desde_cliente(ctx, puertos):
    """Escanear desde cliente hacia web (10.30.0.10) cada puerto usando bash.
    Realiza 2 pasadas para asegurar que las reglas Suricata con umbral capturen paquetes."""
    cli = CONT["cliente"]
    resultados = {}
    p_str = " ".join(str(p) for p in puertos)
    cmd = (
        "docker exec %s bash -c '"
        "for iter in 1 2; do "
        "  for p in %s; do "
        "    if timeout 0.2 bash -c \"echo > /dev/tcp/%s/\\$p\" 2>/dev/null; then "
        "      [ \\$iter -eq 1 ] && echo \"\\$p:abierto\"; "
        "    else "
        "      [ \\$iter -eq 1 ] && echo \"\\$p:cerrado\"; "
        "    fi; "
        "  done; "
        "done'"
        % (cli, p_str, WEB_IP)
    )
    c, out = _ejecutar(ctx, cmd, timeout=15)
    for linea in out.splitlines():
        linea = linea.strip()
        if ":" in linea:
            p_val, est = linea.split(":", 1)
            try:
                resultados[int(p_val)] = est.strip()
            except ValueError:
                pass
    for p in puertos:
        if p not in resultados:
            resultados[p] = "cerrado"
    return resultados


def _contador_drop_fw(ctx):
    """Lee el contador de drop del ruleset nftables en fw."""
    fw = CONT["fw"]
    c, out = _ejecutar(ctx,
        "docker exec %s nft list ruleset 2>/dev/null" % fw, timeout=15)
    total = 0
    for m in re.finditer(r'counter\s+packets\s+(\d+)', out):
        total += int(m.group(1))
    return total, out


def _firmar_resultado(ctx, nota, variante, estudiante):
    """Calcula sha256 de la evidencia y escribe resultado-rubrica.txt con línea control."""
    sha_evidencia = ""
    if os.path.exists(EVIDENCIA_TGZ):
        try:
            with open(EVIDENCIA_TGZ, "rb") as f:
                sha_evidencia = hashlib.sha256(f.read()).hexdigest()
        except OSError:
            sha_evidencia = "error-leyendo-evidencia"
    elif os.path.isdir(EVIDENCIA_DIR):
        h = hashlib.sha256()
        for root, _dirs, files in os.walk(EVIDENCIA_DIR):
            for nombre in sorted(files):
                if nombre == "resultado-rubrica.txt":
                    continue
                ruta = os.path.join(root, nombre)
                try:
                    with open(ruta, "rb") as f:
                        h.update(f.read())
                except OSError:
                    pass
        sha_evidencia = h.hexdigest()
    else:
        sha_evidencia = "sin-evidencia"

    h_doc = hashlib.sha256((estudiante or "desconocido").encode()).hexdigest()[:16]
    fecha_str = time.strftime("%Y-%m-%d %H:%M:%S")
    nota_str = "%.2f" % nota
    control_hash = calcular_control(nota_str, variante, h_doc, sha_evidencia, fecha_str)

    lineas = [
        "resultado-rubrica — rúbrica Corte 3",
        "variante=%s" % variante,
        "documento_hash=%s" % h_doc,
        "nota=%s" % nota_str,
        "sha256_evidencia=%s" % sha_evidencia,
        "fecha=%s" % fecha_str,
        "control=%s" % control_hash,
    ]
    try:
        with open(RESULTADO, "w", encoding="utf-8") as f:
            f.write("\n".join(lineas) + "\n")
    except OSError:
        pass
    return sha_evidencia, h_doc


def revisar(ctx):
    r = []

    # ------------------------------------------------------------------ variantes
    variante = _leer_archivo(ctx, VARIANTE_FILE)
    estudiante = _leer_archivo(ctx, ESTUDIANTE_FILE)

    if not estudiante:
        r.append(falla("estudiante",
            "falta ~/labs/rubrica-c3/estudiante (escribe solo el número de documento)",
            "echo 12345678 > ~/labs/rubrica-c3/estudiante"))
        return r

    digitos = [c for c in estudiante if c.isdigit()]
    if not digitos:
        r.append(falla("estudiante",
            "el archivo estudiante no contiene dígitos válidos",
            "echo 12345678 > ~/labs/rubrica-c3/estudiante"))
        return r

    ult_dig = int(digitos[-1])
    variante_esperada = "A" if (ult_dig % 2 == 0) else "B"

    variante_invalida = False
    if variante not in ("A", "B"):
        variante_invalida = True
        r.append(falla("variante",
            "falta ~/labs/rubrica-c3/variante o valor inválido (escribe A o B)",
            "echo %s > ~/labs/rubrica-c3/variante" % variante_esperada))
    elif variante != variante_esperada:
        variante_invalida = True
        r.append(falla("variante",
            "rechazo de variante: declaraste variante %s pero tu documento %s (último dígito %d) exige variante %s"
            % (variante, estudiante, ult_dig, variante_esperada),
            "Corrige tu archivo: echo %s > ~/labs/rubrica-c3/variante" % variante_esperada))

    vd = VARIANTES.get(variante, VARIANTES[variante_esperada])
    ataque_modo = vd["ataque"]
    ip_atacante = vd["atacante_ip"]
    puertos_escaneo = vd["escaneo"]
    ssh_puerto = vd["ssh"]
    set_nombre = vd["set"]

    # ------------------------------------------------------------------ lab arriba
    if not _lab_arriba(ctx):
        r.append(falla("lab",
            "el lab rubrica-c3 no está arriba (ejecuta ./lab up)",
            "Entra a ~/labs/rubrica-c3 y corre ./lab up"))
        return r

    nombres = _nombres_servicio(ctx)

    # =========================================================================
    # CRITERIO 1 — Detección (1,0)
    # =========================================================================
    reglas_texto = _leer_archivo(ctx, REGLAS_RULES) or ""
    tiene_umbral = "track by_src" in reglas_texto
    sid_estudiante = _sid_de_reglas(reglas_texto)

    if variante_invalida:
        r.append(falla("c1-deteccion",
            "rechazo de variante: declaraste variante %s pero el documento %s termina en %d (nota 0)"
            % (variante, estudiante, ult_dig),
            "Escribe la variante correcta en ~/labs/rubrica-c3/variante"))
    elif not tiene_umbral:
        r.append(falla("c1-deteccion",
            "la regla Suricata no tiene umbral por origen (falta «track by_src»)",
            "Agrega threshold: type threshold, track by_src, count N, seconds M en reglas/lab.rules"))
    elif not sid_estudiante:
        r.append(falla("c1-deteccion",
            "no se encontró un sid en tus reglas Suricata",
            "Pon sid:TU_NUMERO (entre 1000000 y 1999999) en cada regla alert"))
    else:
        # Lanzar ataque de la variante y verificar alerta del atacante
        _ejecutar(ctx,
            "docker exec -d %s /usr/local/bin/reproducir.sh %s" % (nombres["generador"], ataque_modo),
            timeout=10)
        time.sleep(22)
        alertas = _obtener_todas_alertas(ctx)
        alertas_atacante = [a for a in alertas if a.get("src_ip") == ip_atacante or a.get("dest_port") == 80]
        alerta_con_sid = any(a.get("alert", {}).get("signature_id") == int(sid_estudiante) for a in alertas_atacante)

        if alertas_atacante and alerta_con_sid:
            r.append(ok("c1-deteccion",
                "regla con umbral por origen activa y alerta con sid %s del atacante (%d alerta(s))"
                % (sid_estudiante, len(alertas_atacante))))
        elif alertas_atacante:
            r.append(falla("c1-deteccion",
                "hubo %d alerta(s) pero ninguna con el sid %s de tus reglas" % (len(alertas_atacante), sid_estudiante),
                "Revisa que el sid de tus reglas coincida con el que aparece en las alertas de eve.json"))
        else:
            r.append(falla("c1-deteccion",
                "no hubo alertas de Suricata al lanzar el ataque %s" % ataque_modo,
                "Aplica tus reglas con ./lab recargar y verifica que Suricata esté corriendo"))

    # =========================================================================
    # CRITERIO 2 — Línea base y confirmación (1,0)
    # =========================================================================
    lb = _leer_archivo(ctx, LINEA_BASE)
    conf = _leer_archivo(ctx, CONFIRMACION)
    lb_valida = bool(lb) and "pps=" in lb and "SYN-RECV=" in lb

    # C2 exige: confirmacion.txt con >= 5 lineas tipo tcpdump (IP 10.20.10.x.PUERTO > 10.30.0.10.80)
    # que incluyan la IP del atacante de la variante (A 10.20.10.71, B 10.20.10.91).
    lineas_tcpdump = re.findall(r'IP\s+10\.20\.10\.\d+[\.\d]*\s*>\s*10\.30\.0\.10\.(?:80|http)', conf)
    conf_tiene_ip = ip_atacante in conf
    conf_valida = bool(conf) and len(lineas_tcpdump) >= 5 and conf_tiene_ip

    if lb_valida and conf_valida:
        r.append(ok("c2-linea-base",
            "línea base y confirmación presentes con salida real de tcpdump/ss"))
    elif lb_valida or bool(conf):
        faltas_c2 = []
        if not lb_valida:
            faltas_c2.append("linea-base.txt incompleta (falta pps= o SYN-RECV=)")
        if not conf_valida:
            if len(lineas_tcpdump) < 5:
                faltas_c2.append("confirmacion.txt no tiene al menos 5 líneas tcpdump del ataque")
            if not conf_tiene_ip:
                faltas_c2.append("confirmacion.txt no incluye la IP del atacante %s" % ip_atacante)
        r.append(falla("c2-linea-base",
            "evidencia de línea base o confirmación inválida: %s" % "; ".join(faltas_c2),
            "Corre ./lab base 30 y genera confirmacion.txt con tcpdump en fw durante ./lab ataque %s" % ataque_modo))
    else:
        r.append(falla("c2-linea-base",
            "no existen evidencia/linea-base.txt ni evidencia/confirmacion.txt",
            "Ejecuta ./lab base 30 antes de aplicar reglas, y registra la confirmación"))

    # =========================================================================
    # CRITERIO 3 — Mitigación con continuidad (1,0)
    # =========================================================================
    n_drop_antes, ruleset = _contador_drop_fw(ctx)
    tiene_limit_rate = "limit rate over" in ruleset
    tiene_ct_count = "ct count over" in ruleset
    tiene_set_dinamico = ("flags dynamic,timeout" in ruleset or "update @" in ruleset)

    if not (tiene_limit_rate and tiene_ct_count):
        r.append(falla("c3-mitigacion",
            "el ruleset nftables no tiene limit rate over ni ct count over",
            "Agrega límite de tasa por origen y límite de conexiones simultáneas en reglas/nftables.fw, luego ./lab recargar"))
    else:
        # Medir continuidad durante el ataque: cliente legítimo >= 90% HTTP 200
        antes = _contar_lineas_cliente(ctx)
        _ejecutar(ctx,
            "docker exec -d %s /usr/local/bin/reproducir.sh %s" % (nombres["generador"], ataque_modo),
            timeout=10)
        time.sleep(22)
        despues = _contar_lineas_cliente(ctx)
        pos, total = _segmento_200(ctx, antes, despues)

        pct = (pos * 100 // total) if total > 0 else 0

        n_drop_despues, ruleset_despues = _contador_drop_fw(ctx)
        drop_subio = n_drop_despues > n_drop_antes

        # Verificar que el atacante quedó contenido en cualquier set con su IP o contador subió
        atacante_en_set = ip_atacante in ruleset_despues
        atacante_contenido = atacante_en_set or drop_subio

        if total >= 10 and pct >= 90 and atacante_contenido:
            r.append(ok("c3-mitigacion",
                "cliente legítimo %d%% HTTP 200 durante el ataque (%d/%d); atacante contenido (set con su IP o contador de drop subió)"
                % (pct, pos, total)))
        elif total >= 10 and pct < 90:
            if pct > 0:
                r.append(falla("c3-mitigacion",
                    "continuidad no cumplida: cliente legítimo cayó al %d%% HTTP 200 (< 90%% requerido) durante el ataque" % pct,
                    "Tus reglas son demasiado estrictas: el tráfico legítimo se ve afectado"))
            else:
                r.append(falla("c3-mitigacion",
                    "continuidad no cumplida: cliente legítimo sin HTTP 200 durante el ataque (0%%)",
                    "Regla drop total sin over: corta todo el tráfico. Usa limit rate over / ct count over."))
        elif not atacante_contenido:
            r.append(falla("c3-mitigacion",
                "el atacante no quedó contenido: no hay set con su IP ni los contadores de drop aumentaron",
                "Verifica que nftables contenga al atacante con set dinámico o regla de drop"))
        else:
            r.append(falla("c3-mitigacion",
                "cliente legítimo con muestras insuficientes (%d peticiones)" % total,
                "Asegúrate de que el cliente legítimo esté enviando peticiones activas"))

    # =========================================================================
    # CRITERIO 4 — Acceso no autorizado (1,0)
    # =========================================================================
    if variante_invalida:
        r.append(falla("c4-acceso-no-autorizado",
            "rechazo de variante: discrepancia de variante (nota 0)",
            "Corrige la variante para que coincida con tu documento"))
    else:
        # Escanear desde cliente hacia web los puertos de la variante
        scan = _scaneo_desde_cliente(ctx, puertos_escaneo)
        time.sleep(2)
        puertos_cerrados = [p for p, est in scan.items() if est == "cerrado"]
        puertos_abiertos = [p for p, est in scan.items() if est == "abierto"]

        todas_alertas = _obtener_todas_alertas(ctx)
        alertas_ssh = [a for a in todas_alertas if a.get("dest_port") == ssh_puerto]
        hay_alerta_ssh = len(alertas_ssh) > 0

        puertos_escaneo_distintos = [p for p in puertos_escaneo if p != ssh_puerto]
        puertos_con_alerta = set(a.get("dest_port") for a in todas_alertas if a.get("dest_port") in puertos_escaneo_distintos)
        hay_alerta_escaneo = len(puertos_con_alerta) >= 2

        # HTTP sigue en 200 (verificar que web responde)
        c_http, out_http = _ejecutar(ctx,
            "docker exec %s sh -c 'ss -ltn | grep -q :80 && echo web-escuchando || echo web-silencioso'" % CONT["web"],
            timeout=10)
        web_activa = "web-escuchando" in out_http

        n_drop_despues4, _ = _contador_drop_fw(ctx)

        if (not puertos_abiertos) and hay_alerta_escaneo and hay_alerta_ssh and web_activa and n_drop_despues4 > 0:
            r.append(ok("c4-acceso-no-autorizado",
                "escaneo detectado, puertos no publicados filtrados, alerta SSH (%d) y HTTP activo" % ssh_puerto))
        else:
            faltantes = []
            if puertos_abiertos:
                faltantes.append("puertos abiertos: %s" % puertos_abiertos)
            if not hay_alerta_escaneo:
                faltantes.append("sin alerta de escaneo (se requieren >= 2 puertos distintos alertados)")
            if not hay_alerta_ssh:
                faltantes.append("sin alerta SSH puerto %d" % ssh_puerto)
            if not web_activa:
                faltantes.append("web no responde")
            if n_drop_despues4 == 0:
                faltantes.append("contador de drop en 0")
            r.append(falla("c4-acceso-no-autorizado",
                "acceso no autorizado no verificado: %s" % "; ".join(faltantes),
                "Aplica reglas de filtro en nftables y reglas Suricata de escaneo/SSH, luego ./lab recargar"))

    # =========================================================================
    # CRITERIO 5 — Evidencia íntegra (1,0)
    # =========================================================================
    tgz_existe = os.path.exists(EVIDENCIA_TGZ)
    archivos_evidencia = []
    if os.path.isdir(EVIDENCIA_DIR):
        archivos_evidencia = [f for f in os.listdir(EVIDENCIA_DIR) if f != "resultado-rubrica.txt"]

    hay_linea_base = "linea-base.txt" in archivos_evidencia
    hay_confirmacion = "confirmacion.txt" in archivos_evidencia

    if tgz_existe and hay_linea_base and hay_confirmacion and len(archivos_evidencia) >= 2:
        sha_evidencia, h_doc = _firmar_resultado(ctx, 0, variante, estudiante)  # nota provisional
        r.append(ok("c5-evidencia",
            "evidencia.tar.gz generado y resultado-rubrica.txt firmado (sha256 de evidencia + variante + documento)"))
    else:
        faltantes5 = []
        if not tgz_existe:
            faltantes5.append("evidencia.tar.gz no existe")
        if not hay_linea_base:
            faltantes5.append("linea-base.txt")
        if not hay_confirmacion:
            faltantes5.append("confirmacion.txt")
        r.append(falla("c5-evidencia",
            "evidencia íntegra incompleta: %s" % "; ".join(faltantes5),
            "Ejecuta ./lab evidencia para empaquetar la carpeta evidencia/"))

    # =========================================================================
    # CÁLCULO DE NOTA Y BONOS
    # =========================================================================
    ok_ids = {x["id"] for x in r if x["ok"]}
    criterios = ["c1-deteccion", "c2-linea-base", "c3-mitigacion", "c4-acceso-no-autorizado", "c5-evidencia"]
    nota = sum(1.0 for c in criterios if c in ok_ids)

    # Bonos (solo si la variante es válida)
    bono_ok = False
    if variante == "A" and not variante_invalida:
        # Bono A: set dinámico con timeout
        if tiene_set_dinamico and "timeout" in ruleset:
            nota = min(nota + 0.2, 5.0)
            bono_ok = True
            r.append(ok("bono-A", "bloqueo de escaneo por set dinámico con timeout (+0,2)"))
        else:
            r.append(falla("bono-A", "set dinámico con timeout no presente en nftables", "Agrega un set con flags dynamic,timeout y update @set en reglas/nftables.fw"))
    elif variante == "B" and not variante_invalida:
        # Bono B: dos firmas HTTP distintas que ambas disparan
        alertas_todas = _obtener_todas_alertas(ctx)
        alertas_http = [a for a in alertas_todas if a.get("dest_port") == 80]
        sids_http = set()
        for a in alertas_http:
            sid = a.get("alert", {}).get("signature_id")
            if sid and sid >= 1000000:
                sids_http.add(sid)
        if len(sids_http) >= 2:
            nota = min(nota + 0.3, 5.0)
            bono_ok = True
            r.append(ok("bono-B", "dos firmas HTTP distintas dispararon alertas en el ataque HTTP (sids: %s) (+0,3)" % sorted(sids_http)))
        else:
            r.append(falla("bono-B", "se requieren dos firmas HTTP distintas que ambas disparen", "Agrega dos reglas alert con content distintas y sid diferentes en reglas/lab.rules"))

    # Re-firmar con la nota final calculada
    _firmar_resultado(ctx, nota, variante, estudiante)

    aprobado = (nota >= 3.0) and (not variante_invalida)
    if variante_invalida:
        msg = "NOTA FINAL: %.2f / 5,0  NO APROBADO (rechazo de variante)" % nota
    elif aprobado:
        msg = "NOTA FINAL: %.2f / 5,0  APROBADO" % nota
    else:
        msg = "NOTA FINAL: %.2f / 5,0  NO APROBADO (mínimo 3,0)" % nota

    r.append({
        "id": "resultado-final",
        "ok": aprobado,
        "mensaje": msg,
        "pista": "Intentos ilimitados hasta el plazo (28-nov-2026 23:59). Cuenta el último resultado firmado.",
    })
    return r


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3 and sys.argv[1] == "--verificar":
        ok_verif = verificar_resultado_archivo(sys.argv[2])
        sys.exit(0 if ok_verif else 1)
