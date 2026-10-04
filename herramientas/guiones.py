#!/usr/bin/env python3
"""Exporta el guion de narración de una semana a guiones/<archivo>.md, con los cortes de video marcados.
Uso: python3 herramientas/guiones.py 2026-2-S01-....html [más archivos]   |   python3 herramientas/guiones.py todas
"""
import sys
from pathlib import Path
from bs4 import BeautifulSoup

RAIZ = Path(__file__).resolve().parent.parent

def exportar(h):
    soup = BeautifulSoup(Path(h).read_text(encoding="utf-8"), "html.parser")
    out = [f"# Guion — {soup.title.get_text()}\n"]
    for i, s in enumerate(soup.select("#stage > section.slide"), 1):
        n = s.find("aside", class_="notes"); t = n.get_text(" ", strip=True) if n else ""
        if s.get("data-parte"):
            out.append(f"\n---\n## ✂ CORTE DE VIDEO · Parte {s['data-parte']} de 4\n")
        h2 = s.find(["h2", "h1"])
        out.append(f"**Diapositiva {i}** — {h2.get_text(' ', strip=True) if h2 else ''}\n\n{t}\n")
    d = RAIZ / "guiones"; d.mkdir(exist_ok=True)
    f = d / (Path(h).stem + ".md"); f.write_text("\n".join(out), encoding="utf-8"); print("→", f.relative_to(RAIZ))

args = sys.argv[1:]
if args == ["todas"]:
    args = [str(p) for p in sorted(RAIZ.glob("2026-2-S*.html"))]
for a in args: exportar(a)
