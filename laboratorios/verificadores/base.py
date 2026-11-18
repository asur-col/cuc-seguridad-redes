"""Contexto de verificacion: todo lo que un verificador puede mirar pasa por aqui."""
import json, os, subprocess

class Contexto:
    """Da acceso al sistema real o a un estado falso descrito en JSON.

    Los verificadores no llaman a subprocess ni a open: piden comandos y archivos a este objeto.
    Asi el mismo verificador se puede probar sin VM, con un estado escrito a mano.
    """
    def __init__(self, comandos=None, archivos=None, real=False):
        self.comandos = comandos or {}
        self.archivos = archivos or {}
        self.real = real

    @classmethod
    def desde_fixture(cls, ruta):
        with open(ruta, encoding="utf-8") as f:
            d = json.load(f)
        return cls(comandos=d.get("comandos", {}), archivos=d.get("archivos", {}))

    def ejecutar(self, comando, timeout=25):
        if not self.real:
            if comando in self.comandos:
                v = self.comandos[comando]
                return (v.get("codigo", 0), v.get("salida", ""))
            return (127, "no configurado en el estado falso")
        try:
            r = subprocess.run(comando, shell=True, capture_output=True, text=True, timeout=timeout)
            return (r.returncode, (r.stdout or "") + (r.stderr or ""))
        except Exception as e:
            return (1, str(e))

    def leer(self, ruta):
        if not self.real:
            return self.archivos.get(ruta)
        try:
            with open(os.path.expanduser(ruta), encoding="utf-8", errors="replace") as f:
                return f.read()
        except OSError:
            return None

    def existe(self, ruta):
        if not self.real:
            return ruta in self.archivos
        return os.path.exists(os.path.expanduser(ruta))

def ok(ident, mensaje, pista=""):
    return {"id": ident, "ok": True, "mensaje": mensaje, "pista": pista}

def falla(ident, mensaje, pista):
    return {"id": ident, "ok": False, "mensaje": mensaje, "pista": pista}
