"""Verificador del Lab B3: los tres saltos, el NAT, la regla que corta y el visor en marcha."""
import json, re
from .base import falla, ok

ID = "b3-rutas"
TITULO = "Rutas y trafico"

def _contadores(salida, palabra):
    """Suma el primer campo (paquetes) de las lineas con la palabra dada."""
    total = 0
    for l in salida.splitlines():
        if palabra in l:
            p = l.split()
            if p and p[0].isdigit():
                total += int(p[0])
    return total

def revisar(ctx):
    r = []

    c, ps = ctx.ejecutar("docker ps --format {{.Names}}")
    faltan = [n for n in ("lab-b3-cliente", "lab-b3-router", "lab-b3-interno") if n not in ps]
    if not faltan:
        r.append(ok("arriba", "los contenedores del laboratorio estan en marcha"))
    else:
        r.append(falla("arriba", "faltan contenedores: " + ", ".join(faltan),
                       "Levanta el laboratorio con docker compose up -d como en A.2."))

    c, nat = ctx.ejecutar("docker exec lab-b3-router iptables -t nat -L POSTROUTING -v -n")
    if _contadores(nat, "MASQUERADE") > 0:
        r.append(ok("nat", "la regla de traduccion ha movido paquetes"))
    elif "MASQUERADE" in nat:
        r.append(falla("nat", "la regla de traduccion existe pero no ha movido paquetes",
                       "Genera el trafico del paso B.2 y vuelve a mirar el contador."))
    else:
        r.append(falla("nat", "no hay regla de traduccion", "Revisa el script de reglas del paso A.3."))

    c, fw = ctx.ejecutar("docker exec lab-b3-router iptables -L FORWARD -v -n")
    if _contadores(fw, "DROP") > 0:
        r.append(ok("bloqueo", "la regla de bloqueo ha cortado paquetes"))
    else:
        r.append(falla("bloqueo", "la regla de bloqueo no ha cortado nada",
                       "Haz el intento al puerto cerrado del paso B.4 y vuelve a mirar la regla."))

    c, salud = ctx.ejecutar("curl -s http://127.0.0.1:8099/salud")
    try:
        j = json.loads(salud) if salud.strip() else None
    except json.JSONDecodeError:
        j = None
    if j and j.get("ok") and int(j.get("flujos", 0)) > 0:
        r.append(ok("visor", "el visor esta en marcha y ha visto %s flujos" % j.get("flujos")))
    else:
        r.append(falla("visor", "el visor no responde o no ha visto flujos",
                       "Arranca colector.py como en B.1 y genera trafico antes de comprobar."))

    informe = ctx.leer("informe-b3.md")
    if informe and len(informe.split()) >= 80 and re.search(r"nat|traducc", informe, re.I):
        r.append(ok("informe", "el informe describe el flujo y la traduccion"))
    else:
        r.append(falla("informe", "el informe falta o no describe la traduccion",
                       "El entregable pide una frase por captura, incluida la marca NAT."))
    return r
