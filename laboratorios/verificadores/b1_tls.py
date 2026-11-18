"""Verificador del Lab B1: certificado propio, canal verificado, TLS viejo fuera y servicio interno solo por el tunel."""
from .base import falla, ok

ID = "b1-tls"
TITULO = "TLS y tunel entre sedes"

def revisar(ctx):
    r = []

    c, out = ctx.ejecutar("openssl verify -CAfile ca.crt servidor.crt")
    if c == 0 and "OK" in out:
        r.append(ok("cadena", "el certificado del servidor valida contra tu CA"))
    else:
        r.append(falla("cadena", "el certificado no valida contra la CA",
                       "Revisa la parte A: la CA debe haber firmado el certificado y openssl verify debe decir OK."))

    c, out = ctx.ejecutar("openssl x509 -in servidor.crt -noout -ext subjectAltName")
    if "DNS:web.lab" in out and ("IP:10.20.0.10" in out or "IP Address:10.20.0.10" in out):
        r.append(ok("san", "el certificado lleva los nombres que se usan"))
    else:
        r.append(falla("san", "al certificado le faltan los nombres (SAN)",
                       "Vuelve a generarlo con -addext subjectAltName=DNS:web.lab,IP:10.20.0.10."))

    c, nginx = ctx.ejecutar("docker exec lab-b1-web nginx -T")
    if "tlsv1.2" in nginx.lower() and "tlsv1.3" in nginx.lower() and "tlsv1.1" not in nginx.lower():
        r.append(ok("protocolos", "el servidor solo habla TLS 1.2 y 1.3"))
    else:
        r.append(falla("protocolos", "el servidor sigue admitiendo versiones viejas de TLS",
                       "Revisa ssl_protocols en la configuracion del paso A.3 y recarga nginx."))

    c, out = ctx.ejecutar("curl --cacert ca.crt --resolve web.lab:443:10.20.0.10 -s -o /dev/null -w %{http_code} https://web.lab/")
    if c == 0 and out.strip().endswith("200"):
        r.append(ok("https", "el sitio responde 200 con la CA del laboratorio"))
    else:
        r.append(falla("https", "el sitio no responde 200 con tu CA: " + out.strip()[:40],
                       "Comprueba que el certificado y la clave son los que usa nginx y que la CA es la tuya."))

    c, out = ctx.ejecutar("openssl s_client -connect 10.20.0.10:443 -tls1_1 </dev/null")
    if ("alert protocol version" in out.lower()) or ("no protocols available" in out.lower()) or ("handshake failure" in out.lower()):
        r.append(ok("tls11", "TLS 1.1 se rechaza, como debe"))
    else:
        r.append(falla("tls11", "TLS 1.1 no se rechaza",
                       "Confirma ssl_protocols TLSv1.2 TLSv1.3 en A.3 y repite la prueba."))

    c, out = ctx.ejecutar("docker port lab-b1-interno")
    if c != 0 or not out.strip():
        r.append(ok("interno", "el servicio interno no publica puertos"))
    else:
        r.append(falla("interno", "el servicio interno esta publicado en el anfitrion: " + out.strip()[:40],
                       "Quita la seccion ports del servicio interno: solo debe verse por el tunel."))

    c, out = ctx.ejecutar("docker exec lab-b1-sede2 wg show")
    if "latest handshake" in out.lower():
        r.append(ok("tunel", "el tunel tiene handshake reciente"))
    else:
        r.append(falla("tunel", "el tunel no muestra handshake", "Revisa llaves y AllowedIPs en las dos sedes."))
    return r
