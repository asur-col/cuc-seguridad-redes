"""Verificador del Lab A1: la VM existe, el usuario no es root y el ejercicio esta hecho."""
from .base import falla, ok

ID = "a1-linux"
TITULO = "Linux desde cero"

def revisar(ctx):
    r = []

    c, out = ctx.ejecutar("lsb_release -ds")
    if c == 0 and out.strip():
        r.append(ok("sistema", "sistema identificado: " + out.strip().splitlines()[0][:60]))
    else:
        r.append(falla("sistema", "no se pudo leer la version del sistema",
                       "Repite el paso 1 de A.1: lsb_release -ds debe imprimir la version de Ubuntu."))

    c, out = ctx.ejecutar("id -un")
    usuario = out.strip().splitlines()[0] if out.strip() else ""
    if usuario and usuario != "root":
        r.append(ok("usuario", "trabajas con un usuario normal: " + usuario))
    elif usuario == "root":
        r.append(falla("usuario", "estas trabajando como root",
                       "Sal de root: el laboratorio pide un usuario normal con sudo. Revisa A.1."))
    else:
        r.append(falla("usuario", "no se pudo leer el usuario", "Comprueba que la sesion esta abierta en la VM."))

    c, out = ctx.ejecutar("ip -4 addr show")
    if c == 0 and ("10." in out or "192.168." in out):
        r.append(ok("red", "la VM tiene direccion IPv4 de la red del aula"))
    else:
        r.append(falla("red", "la VM no muestra una direccion IPv4 esperada",
                       "Revisa el adaptador en modo puente y vuelve a A.2: ip -4 addr show."))

    c, out = ctx.ejecutar("ls -l ~/a1/prueba.txt")
    if c == 0 and "-rw-r-----" in out:
        r.append(ok("permisos", "el archivo del ejercicio existe con permisos 640"))
    elif c != 0:
        r.append(falla("permisos", "no existe ~/a1/prueba.txt",
                       "Crea el archivo como dice el entregable: mkdir -p ~/a1 && echo hola > ~/a1/prueba.txt"))
    else:
        r.append(falla("permisos", "el archivo existe pero los permisos no son 640",
                       "Aplica chmod 640 ~/a1/prueba.txt y comprueba con ls -l."))

    c, out = ctx.ejecutar("sudo tail -5 /var/log/syslog")
    if c == 0 and len(out.strip().splitlines()) >= 3:
        r.append(ok("registro", "el registro del sistema es legible"))
    else:
        r.append(falla("registro", "no se pudo leer el registro del sistema",
                       "Comprueba que tu usuario esta en sudo y que /var/log/syslog existe."))
    return r
