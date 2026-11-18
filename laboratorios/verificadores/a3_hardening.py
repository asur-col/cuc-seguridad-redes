"""Verificador del Lab A3: el servidor quedo endurecido y se puede demostrar."""
from .base import falla, ok

ID = "a3-hardening"
TITULO = "Endurecer el servidor"

def _valor(texto, clave):
    for l in texto.splitlines():
        p = l.split()
        if len(p) >= 2 and p[0].lower() == clave:
            return p[1].lower()
    return ""

def revisar(ctx):
    r = []
    c, sshd = ctx.ejecutar("sudo sshd -T")
    if c != 0 or not sshd.strip():
        return [falla("sshd", "no se pudo leer la configuracion de SSH",
                      "Ejecuta sudo sshd -T en la VM; si falla, revisa /etc/ssh/sshd_config.d/10-a3.conf.")]

    if _valor(sshd, "passwordauthentication") == "no":
        r.append(ok("password", "la autenticacion por contrasena esta desactivada"))
    else:
        r.append(falla("password", "SSH sigue aceptando contrasenas",
                       "Revisa el paso B.1 y comprueba con sudo sshd -T | grep passwordauthentication."))

    if _valor(sshd, "permitrootlogin") in ("no", "prohibit-password"):
        r.append(ok("root", "root no entra por SSH con contrasena"))
    else:
        r.append(falla("root", "root puede entrar por SSH", "Pon PermitRootLogin no en el archivo del paso B.1."))

    intentos = _valor(sshd, "maxauthtries")
    try:
        n = int(intentos)
    except ValueError:
        n = 99
    if n <= 3:
        r.append(ok("intentos", "los intentos por conexion estan acotados: %d" % n))
    else:
        r.append(falla("intentos", "MaxAuthTries es %s" % (intentos or "desconocido"),
                       "Pon MaxAuthTries 3 en el archivo del paso B.1."))

    c, ufw = ctx.ejecutar("sudo ufw status verbose")
    if c == 0 and "Status: active" in ufw and "deny (incoming)" in ufw:
        r.append(ok("cortafuegos", "el cortafuegos esta activo y niega la entrada por defecto"))
    elif c != 0:
        r.append(falla("cortafuegos", "no se pudo leer el estado de ufw", "Revisa el paso B.3."))
    else:
        r.append(falla("cortafuegos", "el cortafuegos no esta activo o no niega por defecto",
                       "sudo ufw default deny incoming && sudo ufw enable, como en B.3."))

    if "22/tcp" in ufw and "LIMIT" in ufw.upper():
        r.append(ok("limite", "el puerto de administracion tiene regla de limite"))
    else:
        r.append(falla("limite", "no hay regla de limite en el puerto de administracion",
                       "Aplica sudo ufw limit 22/tcp y vuelve a comprobar con ufw status."))

    c, sudo_l = ctx.ejecutar("sudo -l -U operador")
    if c != 0 or "operador" not in sudo_l or "may run" not in sudo_l:
        r.append(falla("sudo", "no se pudo comprobar el usuario operador",
                       "Crea el usuario del paso B.4 y revisa visudo -c."))
    elif "(ALL" in sudo_l:
        r.append(falla("sudo", "operador tiene sudo completo",
                       "No lo metas en el grupo sudo: deja solo el archivo de /etc/sudoers.d del paso B.4."))
    elif "/usr/bin/apt" in sudo_l:
        r.append(ok("sudo", "operador existe y su sudo esta acotado a lo declarado"))
    else:
        r.append(falla("sudo", "operador existe pero no tiene el sudo acotado del paso B.4",
                       "Escribe la regla en /etc/sudoers.d/90-operador y valida con visudo -c."))

    contenido = ctx.leer("/var/lib/a3-huellas.txt")
    if contenido and len([l for l in contenido.splitlines() if l.strip()]) >= 20:
        r.append(ok("huellas", "hay huellas registradas de los archivos de configuracion"))
    else:
        r.append(falla("huellas", "no hay huellas o son muy pocas",
                       "Ejecuta el primer comando de B.5 y guarda en /var/lib/a3-huellas.txt."))
    return r
