#!/usr/bin/env python3
"""Ensambla una semana a partir de sus fuentes.

Entrada:  fuentes/SNN/semana.json + fuentes/SNN/parte1.html ... parte4.html
Salida:   <archivo>.html en la raíz del repo (presentación final, lienzo 1280x720)

Uso:  python3 herramientas/construir.py S01        (una semana)
      python3 herramientas/construir.py todas      (todas las que tengan fuentes)

Cada parteN.html contiene solo diapositivas de contenido con este formato:

  <section class="slide" data-fuente="NIST SP 800-41r1 (2009)">
    <div class="kicker">Concepto</div>
    <h2>Título de la diapositiva</h2>
    <p class="sub">Subtítulo opcional de una línea.</p>
    <div class="s-body"> ... diagrama SVG / componentes ... </div>
    <aside class="notes">Guion de narración ...</aside>
  </section>

El constructor agrega portada (= divisoria de la Parte 1), divisorias "Parte X de 4",
cabecera con logo, pie con fuente y numeración, la hoja de estilos, la navegación y
la biblioteca de íconos (assets/iconos.svg) en línea.
"""
import json, re, sys, html
from pathlib import Path
from bs4 import BeautifulSoup

RAIZ = Path(__file__).resolve().parent.parent
FUENTES = RAIZ / "fuentes"
CURSO = "Seguridad en Redes"
DOCENTE = "Ing. Rodolfo Cañas Cervantes"
INST = "Universidad de la Costa (CUC) · Ingeniería de Sistemas"
PERIODO = "Periodo 2026-2 · Barranquilla, Colombia"


def esc(t):
    return html.escape(t or "", quote=True)


def portada(meta, parte):
    temas = "".join(f"<span>{esc(t)}</span>" for t in parte.get("temas", []))
    return f'''<section class="slide cover divider-1" data-parte="1">
  <div class="topline-g"></div><div class="topline-v"></div>
  <img class="logo-main" src="assets/logo-cuc.png" alt="Universidad de la Costa">
  <div class="cover-kicker">{esc(meta["etiqueta"])} · {esc(meta["unidad"])} · {CURSO}</div>
  <h1>{esc(meta["titulo"])}</h1>
  <div class="bar"></div>
  <div class="author"><b>{DOCENTE}</b><br>{INST}<br>{esc(meta["etiqueta"])} · {PERIODO}</div>
  <div class="cover-parte">Parte 1 de 4 · {esc(parte["titulo"])}</div>
  <div class="temas">{temas}</div>
  <aside class="notes">{esc(meta.get("portada_guion") or parte.get("guion", ""))}</aside>
</section>'''


def divisoria(meta, n, parte):
    temas = "".join(f"<span>{esc(t)}</span>" for t in parte.get("temas", []))
    return f'''<section class="slide divider" data-parte="{n}">
  <div class="topline-g"></div><div class="topline-v"></div>
  <div class="parte-n">Parte {n} de 4</div>
  <div class="parte-big">{n}</div>
  <h1>{esc(parte["titulo"])}</h1>
  <div class="semana">{esc(meta["etiqueta"])} · {esc(meta["titulo"])}</div>
  <div class="temas">{temas}</div>
  <img class="logo-div" src="assets/logo-cuc.png" alt="CUC">
  <aside class="notes">{esc(parte.get("guion", ""))}</aside>
</section>'''


def envolver(sec, meta, n_parte):
    """Convierte una diapositiva de fuente en la estructura final."""
    kicker = sec.find(class_="kicker")
    h2 = sec.find("h2")
    sub = sec.find(class_="sub")
    body = sec.find(class_="s-body")
    notes = sec.find("aside", class_="notes")
    if h2 is None or body is None or notes is None:
        raise SystemExit(f"Diapositiva sin h2/s-body/notes en parte {n_parte}: {str(sec)[:160]}")
    fuente = sec.get("data-fuente", "")
    extra = " ".join(c for c in sec.get("class", []) if c != "slide")
    head = '<div class="s-head">'
    head += str(kicker) if kicker else ""
    head += str(h2) + '<div class="rule"></div>'
    if sub:
        sub.name = "div"
        head += str(sub)
    head += '<img class="logo-corner" src="assets/logo-cuc.png" alt="CUC"></div>'
    pie = (f'<div class="s-foot"><span>{CURSO} · {esc(meta["etiqueta"])} · Parte {n_parte} de 4</span>'
           f'<span class="src">{esc(fuente)}</span><span class="pg">@@PG@@</span></div>')
    clases = f"slide {extra}".strip()
    return f'<section class="{clases}" data-parte-de="{n_parte}">{head}{body}{pie}{notes}</section>'


def construir(cod):
    d = FUENTES / cod
    meta = json.loads((d / "semana.json").read_text(encoding="utf-8"))
    partes = meta["partes"]
    assert len(partes) == 4, "se esperan 4 partes"
    piezas = []
    for i, p in enumerate(partes, 1):
        piezas.append(portada(meta, p) if i == 1 else divisoria(meta, i, p))
        src = (d / f"parte{i}.html").read_text(encoding="utf-8")
        soup = BeautifulSoup(src, "html.parser")
        secs = soup.find_all("section")
        if not secs:
            raise SystemExit(f"{cod} parte{i}.html no tiene diapositivas")
        for s in secs:
            piezas.append(envolver(s, meta, i))
    total = len(piezas)
    salida = []
    for k, p in enumerate(piezas, 1):
        salida.append(p.replace("@@PG@@", f"{k} / {total}"))
    sprite = (RAIZ / "assets" / "iconos.svg").read_text(encoding="utf-8")
    sprite = re.sub(r"<!--.*?-->", "", sprite, flags=re.S)
    doc = f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{CURSO} — {esc(meta["etiqueta"])} · {esc(meta["titulo"])}</title>
<meta name="description" content="{esc(meta.get("descripcion", ""))}">
<link rel="stylesheet" href="assets/cuc-deck.css">
</head>
<body>
{sprite}
<div id="progress"></div>
<div id="stage">
{chr(10).join(salida)}
</div>
<div id="nav"><button id="prev" aria-label="Anterior">‹</button><span id="counter"></span><button id="next" aria-label="Siguiente">›</button></div>
<script src="assets/cuc-deck.js"></script>
</body>
</html>
'''
    pre = "../" * meta["archivo"].count("/")
    if pre:
        doc = doc.replace('src="assets/', f'src="{pre}assets/').replace('href="assets/', f'href="{pre}assets/')
    out = RAIZ / f'{meta["archivo"]}.html'
    out.write_text(doc, encoding="utf-8")
    print(f"{cod}: {out.name} · {total} diapositivas")
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cods = sorted(p.name for p in FUENTES.iterdir() if (p / "semana.json").exists()) if sys.argv[1] == "todas" else sys.argv[1:]
    for c in cods:
        construir(c.upper())
