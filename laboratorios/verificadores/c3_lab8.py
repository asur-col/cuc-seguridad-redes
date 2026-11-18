"""Verificador del Lab C3: reconocimiento hecho, hallazgos cerrados y servicio en pie."""
from .base import falla, ok

ID = "c3-lab8"
TITULO = "Reconocimiento en entorno aislado"

RUTAS = ("admin", "backup", "respaldo", ".git", ".env", "config.php", "uploads")

def _codigo(ctx, ruta):
    c, out = ctx.ejecutar("curl -s -o /dev/null -w %%{http_code} http://10.50.0.10/%s" % ruta)
    return out.strip()[-3:] if out.strip() else "000"

def revisar(ctx):
    r = []

    c, ps = ctx.ejecutar("docker ps --format {{.Names}}")
    if "lab-c3-objetivo" in ps:
        r.append(ok("objetivo", "el objetivo aislado esta en marcha"))
    else:
        r.append(falla("objetivo", "el objetivo no esta en marcha",
                       "Levanta el paquete con docker compose up -d como en A.1."))

    c, out = ctx.ejecutar("curl -s -o /dev/null -w %{http_code} http://10.50.0.10/")
    if out.strip().endswith("200"):
        r.append(ok("servicio", "el sitio sigue respondiendo 200: no lo apagaste"))
    else:
        r.append(falla("servicio", "el sitio no responde 200",
                       "Corregir no es apagar: deja el sitio arriba y cierra solo lo que sobraba."))

    antes = ctx.leer("reconocimiento.txt")
    despues = ctx.leer("reconocimiento-despues.txt")
    if antes and "/tcp" in antes:
        r.append(ok("reconocimiento", "existe el reconocimiento de la parte A"))
    else:
        r.append(falla("reconocimiento", "falta reconocimiento.txt con puertos",
                       "Guarda la salida de nmap del paso A.2 con -oN reconocimiento.txt."))
    if despues and "/tcp" in despues:
        r.append(ok("comparacion", "existe el reconocimiento de despues para comparar"))
    else:
        r.append(falla("comparacion", "falta reconocimiento-despues.txt",
                       "Repite el reconocimiento despues de corregir y guardalo como en B.2."))

    abiertas = [x for x in RUTAS if _codigo(ctx, x) not in ("404", "403")]
    if abiertas:
        r.append(falla("exposicion", "queda al menos una ruta de despliegue que responde con contenido",
                       "Vuelve a A.3 y repite la tabla de codigos: lo que respondia distinto de 404 debe dar 404 o 403."))
    else:
        r.append(ok("exposicion", "ninguna de las rutas de despliegue sigue expuesta"))

    informe = ctx.leer("informe-c3.md")
    if informe and "alcance" in informe.lower() and len(informe.split()) >= 100:
        r.append(ok("informe", "el informe declara el alcance y desarrolla los hallazgos"))
    else:
        r.append(falla("informe", "el informe falta, no declara el alcance o es demasiado corto",
                       "El entregable pide alcance, tablas de antes y despues y los cuatro campos por hallazgo."))
    return r
