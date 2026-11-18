"""Verificador del Lab B2: el servicio de identidad decide y el portal exige segundo factor."""
from .base import falla, ok

ID = "b2-identidad"
TITULO = "Identidad y segundo factor"

RADTEST = "docker exec lab-b2-cliente radtest %s %s 10.40.0.10 0 secreto-del-laboratorio"

def revisar(ctx):
    r = []

    c, out = ctx.ejecutar(RADTEST % ("ana", "ClaveAna2027"))
    if "Access-Accept" in out:
        r.append(ok("acepta", "la credencial valida recibe Access-Accept"))
    else:
        r.append(falla("acepta", "la credencial valida no es aceptada",
                       "Revisa clients.conf (secreto e IP del cliente) y el usuario en el paso A.2."))

    c, out = ctx.ejecutar(RADTEST % ("ana", "clave-equivocada"))
    if "Access-Reject" in out:
        r.append(ok("rechaza", "la credencial equivocada recibe Access-Reject"))
    else:
        r.append(falla("rechaza", "la credencial equivocada no es rechazada",
                       "Comprueba que la clave del usuario es la del laboratorio y que el servicio arranco."))

    c, out = ctx.ejecutar(RADTEST % ("desconocido", "Cualquiera1"))
    if "Access-Reject" in out:
        r.append(ok("inexistente", "una cuenta que no existe tambien es rechazada"))
    else:
        r.append(falla("inexistente", "una cuenta inexistente no es rechazada",
                       "Ese caso debe dar Access-Reject igual que una clave mala: revisa el paso A.3."))

    c, out = ctx.ejecutar("docker logs lab-b2-radius 2>&1")
    if "ClaveAna2027" in out or "ClaveLuis2027" in out:
        r.append(falla("registro", "el registro del servicio contiene una clave",
                       "El registro no debe guardar claves: revisa la configuracion de log del paso A.4."))
    else:
        r.append(ok("registro", "el registro no contiene claves"))

    c, out = ctx.ejecutar("python3 portal.py --correo ana --clave ClaveAna2027")
    if "RECHAZO" in out.upper() and ("segundo" in out.lower() or "codigo" in out.lower()):
        r.append(ok("portal-sin-codigo", "el portal no concede acceso solo con la clave"))
    else:
        r.append(falla("portal-sin-codigo", "el portal concede acceso sin segundo factor",
                       "Revisa B.2: el portal debe exigir clave y codigo."))

    usados = ctx.leer("usados.json")
    if usados and usados.strip() not in ("", "{}", "[]"):
        r.append(ok("reuso", "el portal recuerda los codigos ya usados"))
    else:
        r.append(falla("reuso", "el portal no guarda los codigos usados",
                       "Sin memoria del ultimo codigo, un codigo robado sirve dos veces: revisa B.2."))
    return r
