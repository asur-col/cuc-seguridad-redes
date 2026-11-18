"""Verificador de la rúbrica Corte 3 (Seguridad en Redes · CUC 2026-2).

Estilo de base.py: usa Contexto (nunca subprocess/open directo), devuelve
lista de {id, ok, mensaje, pista} y soporta --json vía run.py.

El check lanza él mismo el ataque de la variante, mide continuidad y escanea;
dura < 3 min y deja el lab como estaba.
"""
import hashlib, os, re, time
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
        "escaneo": [22, 443, 3306, 5432, 8080],
        "set": "bloqueados",
    },
    "B": {
        "ssh": 2222,
        "ataque": "http",
        "escaneo": [2222, 3306, 5432, 6379, 8080, 8443, 9000, 9200, 11211, 27017],
        "set": "escaneo",
    },
}

WEB_IP = "10.30.0.10"
FW_IP = "10.20.10.2"


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


def _tiene_alertas_eve(ctx, segundos_espera=25):
    """Cuenta alertas en eve.json del contenedor ids tras un ataque."""
    ids = CONT["ids"]
    c, out = _ejecutar(ctx,
        "docker exec %s sh -c 'grep -c \"event_type.*alert\" /var/log/suricata/eve.json 2>/dev/null || echo 0'" % ids,
        timeout=segundos_espera)
    try:
        return int(out.strip().splitlines()[-1]) if out.strip() else 0
    except ValueError:
        return 0


def _contenido_eve(ctx):
    ids = CONT["ids"]
    c, out = _ejecutar(ctx,
        "docker exec %s sh -c 'grep \"event_type.*alert\" /var/log/suricata/eve.json 2>/dev/null || true'" % ids,
        timeout=25)
    return out


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
    """Escanear desde cliente hacia web (10.30.0.10) cada puerto; devuelve dict puerto->estado."""
    cli = CONT["cliente"]
    resultados = {}
    for p in puertos:
        c, out = _ejecutar(ctx,
            "docker exec %s sh -c '(echo > /dev/tcp/%s/%d) 2>/dev/null && echo abierto || echo cerrado'" % (cli, WEB_IP, p),
            timeout=5)
        estado = "abierto" if "abierto" in out.lower() else "cerrado"
        resultados[p] = estado
    return resultados


def _contador_drop_fw(ctx):
    """Lee el contador de drop del ruleset nftables en fw."""
    fw = CONT["fw"]
    c, out = _ejecutar(ctx,
        "docker exec %s nft list ruleset 2>/dev/null" % fw, timeout=15)
    # Busca los contadores de drop (packets N bytes M drop)
    total = 0
    for m in re.finditer(r'counter\s+packets\s+(\d+)', out):
        total += int(m.group(1))
    return total, out


def _firmar_resultado(ctx, nota, variante, estudiante):
    """Calcula sha256 de la evidencia y escribe resultado-rubrica.txt."""
    sha_evidencia = ""
    if os.path.exists(EVIDENCIA_TGZ):
        try:
            with open(EVIDENCIA_TGZ, "rb") as f:
                sha_evidencia = hashlib.sha256(f.read()).hexdigest()
        except OSError:
            sha_evidencia = "error-leyendo-evidencia"
    elif os.path.isdir(EVIDENCIA_DIR):
        # Hash recursivo del contenido de evidencia/ (sin el resultado propio)
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

    lineas = [
        "resultado-rubrica — rúbrica Corte 3",
        "variante=%s" % variante,
        "documento_hash=%s" % h_doc,
        "nota=%.2f" % nota,
        "sha256_evidencia=%s" % sha_evidencia,
        "fecha=%s" % time.strftime("%Y-%m-%d %H:%M:%S"),
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

    if variante not in ("A", "B"):
        r.append(falla("variante",
            "falta ~/labs/rubrica-c3/variante (escribe A o B)",
            "echo A > ~/labs/rubrica-c3/variante   (o B si tu documento termina en dígito impar)"))
        return r
    if not estudiante:
        r.append(falla("estudiante",
            "falta ~/labs/rubrica-c3/estudiante (escribe solo el número de documento)",
            "echo 12345678 > ~/labs/rubrica-c3/estudiante"))
        return r

    vd = VARIANTES[variante]
    ataque_modo = vd["ataque"]
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

    if not tiene_umbral:
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
        eve = _contenido_eve(ctx)
        n_alertas = eve.count('"event_type":"alert"')

        alerta_con_sid = False
        if sid_estudiante:
            alerta_con_sid = ('"signature_id":%d' % int(sid_estudiante)) in eve

        if n_alertas > 0 and alerta_con_sid:
            r.append(ok("c1-deteccion",
                "regla con umbral por origen activa y alerta con sid %s del atacante (%d alerta(s))" % (sid_estudiante, n_alertas)))
        elif n_alertas > 0:
            r.append(falla("c1-deteccion",
                "hubo %d alerta(s) pero ninguna con el sid %s de tus reglas" % (n_alertas, sid_estudiante),
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
    conf_valida = bool(conf) and ("tcpdump" in conf.lower() or "10.30.0" in conf or "ss" in conf.lower())

    if lb_valida and conf_valida:
        r.append(ok("c2-linea-base",
            "línea base y confirmación presentes con salida real de tcpdump/ss"))
    elif lb_valida or conf_valida:
        r.append(falla("c2-linea-base",
            "falta uno de los dos archivos (línea base o confirmación) o están incompletos",
            "Corre ./lab base 30 SIN mitigación y genera evidencia/confirmacion.txt con tcpdump en fw y ss en web"))
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
        # Medir continuidad durante el ataque: cliente legítimo ≥ 90% HTTP 200 (30 peticiones)
        antes = _contar_lineas_cliente(ctx)
        _ejecutar(ctx,
            "docker exec -d %s /usr/local/bin/reproducir.sh %s" % (nombres["generador"], ataque_modo),
            timeout=10)
        time.sleep(22)
        despues = _contar_lineas_cliente(ctx)
        pos, total = _segmento_200(ctx, antes, despues)

        pct = (pos * 100 // total) if total > 0 else 0

        n_drop_despues, _ = _contador_drop_fw(ctx)
        drop_subio = n_drop_despues > n_drop_antes

        # Verificar que el atacante quedó en un set dinámico
        fw = CONT["fw"]
        c_set, out_set = _ejecutar(ctx,
            "docker exec %s nft list set inet rubrica3 %s 2>/dev/null || docker exec %s nft list ruleset 2>/dev/null | grep -A2 '%s'" % (fw, set_nombre, fw, set_nombre),
            timeout=15)
        atacante_en_set = bool(out_set.strip()) and ("10.20.10" in out_set or "71" in out_set or "91" in out_set)

        if total >= 10 and pct >= 90:
            msg = "cliente legítimo %d%% HTTP 200 durante el ataque (%d/%d)" % (pct, pos, total)
            if atacante_en_set or drop_subio:
                msg += "; atacante contenido (set %s o contador de drop subió)" % set_nombre
            r.append(ok("c3-mitigacion", msg))
        elif total >= 10 and pct > 0:
            r.append(falla("c3-mitigacion",
                "cliente legítimo cayó al %d%% HTTP 200 (< 90%%) durante el ataque" % pct,
                "Tus reglas son demasiado estrictas: el tráfico legítimo se ve afectado"))
        else:
            r.append(falla("c3-mitigacion",
                "cliente legítimo sin HTTP 200 durante el ataque (0%%)",
                "Regla drop total sin over: corta todo el tráfico. Usa limit rate over / ct count over."))

    # =========================================================================
    # CRITERIO 4 — Acceso no autorizado (1,0)
    # =========================================================================
    # Escanear desde cliente hacia web los puertos de la variante
    scan = _scaneo_desde_cliente(ctx, puertos_escaneo)
    puertos_cerrados = [p for p, est in scan.items() if est == "cerrado"]
    puertos_abiertos = [p for p, est in scan.items() if est == "abierto"]

    # Verificar alerta de escaneo y SSH en eve.json
    eve = _contenido_eve(ctx)
    hay_alerta_escaneo = "escaneo" in eve.lower() or "port" in eve.lower() or "scan" in eve.lower()
    # Buscar alerta que mencione el puerto SSH
    hay_alerta_ssh = ("dport:%d" % ssh_puerto) in eve or ("%d" % ssh_puerto) in eve

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
            faltantes.append("sin alerta de escaneo")
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
    # Contar criterios aprobados
    ok_ids = {x["id"] for x in r if x["ok"]}
    criterios = ["c1-deteccion", "c2-linea-base", "c3-mitigacion", "c4-acceso-no-autorizado", "c5-evidencia"]
    nota = sum(1.0 for c in criterios if c in ok_ids)

    # Bonos
    bono_ok = False
    if variante == "A":
        # Bono A: set dinámico con timeout
        if tiene_set_dinamico and "timeout" in ruleset:
            nota = min(nota + 0.2, 5.0)
            bono_ok = True
            r.append(ok("bono-A", "bloqueo de escaneo por set dinámico con timeout (+0,2)"))
        else:
            r.append(falla("bono-A", "set dinámico con timeout no presente en nftables", "Agrega un set con flags dynamic,timeout y update @set en reglas/nftables.fw"))
    elif variante == "B":
        # Bono B: dos firmas HTTP distintas que ambas disparan
        n_http_firmas = len(re.findall(r'content:"GET ', reglas_texto)) + len(re.findall(r'content:"Host:', reglas_texto))
        if n_http_firmas >= 2:
            nota = min(nota + 0.3, 5.0)
            bono_ok = True
            r.append(ok("bono-B", "dos firmas HTTP distintas (GET y Host) con sid diferentes (+0,3)"))
        else:
            r.append(falla("bono-B", "se requieren dos firmas HTTP distintas que ambas disparen", "Agrega dos reglas alert con content distintas (p. ej. \"GET \" y \"Host:\") y sid diferentes en reglas/lab.rules"))

    # Re-firmar con la nota final
    _firmar_resultado(ctx, nota, variante, estudiante)

    aprobado = nota >= 3.0
    r.append({
        "id": "resultado-final",
        "ok": aprobado,
        "mensaje": "NOTA FINAL: %.2f / 5,0  %s" % (nota, "APROBADO" if aprobado else "NO APROBADO (mínimo 3,0)"),
        "pista": "Intentos ilimitados hasta el plazo (28-nov-2026 23:59). Cuenta el último resultado firmado.",
    })
    return r
