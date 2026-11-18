#!/usr/bin/env python3
"""Verificadores de los laboratorios. Se llama desde asur-lab check <id>."""
import argparse, importlib, json, os, sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent))

from verificadores.base import Contexto  # noqa: E402

MODULOS = {
    "a1-linux": "verificadores.a1_linux",
    "a3-hardening": "verificadores.a3_hardening",
    "b1-tls": "verificadores.b1_tls",
    "b2-identidad": "verificadores.b2_identidad",
    "b3-rutas": "verificadores.b3_rutas",
    "c2-ndr": "verificadores.c2_ndr",
    "c3-lab8": "verificadores.c3_lab8",
    "lab09": "verificadores.lab09_prompt",
    "rubrica-c3": "verificadores.rubrica_c3",
}

def main(argv=None):
    ap = argparse.ArgumentParser(prog="asur-lab check")
    ap.add_argument("id", nargs="?")
    ap.add_argument("--fixture", help="estado falso en JSON, para probar sin VM")
    ap.add_argument("--json", action="store_true", help="salida en JSON")
    ap.add_argument("--dir", help="carpeta del laboratorio (defecto: la actual)")
    ap.add_argument("--lista", action="store_true", help="laboratorios con verificador")
    a = ap.parse_args(argv)

    if a.lista or not a.id:
        for k in sorted(MODULOS):
            print(k)
        return 0
    if a.id not in MODULOS:
        print("no existe el laboratorio %s. Disponibles: %s" % (a.id, ", ".join(sorted(MODULOS))), file=sys.stderr)
        return 2

    if a.dir:
        try:
            os.chdir(a.dir)
        except OSError as e:
            print("no puedo entrar en %s: %s" % (a.dir, e), file=sys.stderr)
            return 2

    mod = importlib.import_module(MODULOS[a.id])
    ctx = Contexto.desde_fixture(a.fixture) if a.fixture else Contexto(real=True)
    resultados = mod.revisar(ctx)
    fallos = [x for x in resultados if not x["ok"]]
    if a.json:
        print(json.dumps({"id": a.id, "resultados": resultados, "ok": not fallos}, ensure_ascii=False, indent=2))
    else:
        print("Laboratorio %s - %s" % (a.id, getattr(mod, "TITULO", "")))
        for x in resultados:
            print(("  OK    " if x["ok"] else "  FALLA ") + x["id"] + ": " + x["mensaje"])
            if not x["ok"] and x["pista"]:
                print("        pista: " + x["pista"])
        print("RESULTADO: " + ("objetivos cumplidos (%d de %d)" % (len(resultados), len(resultados))
                               if not fallos else "%d de %d pendientes" % (len(fallos), len(resultados))))
    return 0 if not fallos else 1

if __name__ == "__main__":
    raise SystemExit(main())
