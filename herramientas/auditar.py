#!/usr/bin/env python3
"""Auditoría de una semana: estructura, gráficos, guion, duración estimada y desbordes.

Uso:  python3 herramientas/auditar.py 2026-2-S01-....html [--capturas DIR]
Requiere: pip install playwright beautifulsoup4 && playwright install chromium
"""
import sys, re, argparse
from pathlib import Path
from bs4 import BeautifulSoup

PPM = 150  # palabras por minuto de es-CO-GonzaloNeural a velocidad normal (aprox.)


def metricas(html):
    soup = BeautifulSoup(Path(html).read_text(encoding="utf-8"), "html.parser")
    slides = soup.select("#stage > section.slide")
    partes = {}
    for s in slides:
        p = s.get("data-parte") or s.get("data-parte-de")
        d = partes.setdefault(p, dict(contenido=0, grafico=0, diagrama=0, palabras=0, sin_guion=0))
        notas = s.find("aside", class_="notes")
        txt = notas.get_text(" ", strip=True) if notas else ""
        d["palabras"] += len(txt.split())
        if s.get("data-parte"):
            continue
        d["contenido"] += 1
        if not txt:
            d["sin_guion"] += 1
        svgs = s.select(".s-body svg")
        if svgs or s.select(".s-body img"):
            d["grafico"] += 1
        con = sum(len(x.find_all(["line", "polyline", "path"])) for x in svgs)
        usos = sum(len(x.find_all("use")) for x in svgs)
        if con >= 3 and usos + sum(len(x.find_all("rect")) for x in svgs) >= 3:
            d["diagrama"] += 1
    return len(slides), partes


def desbordes(html, capturas=None):
    from playwright.sync_api import sync_playwright
    url = Path(html).resolve().as_uri() + "?captura=1"
    out = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1280, "height": 720})
        pg.goto(url); pg.wait_for_timeout(800)
        n = pg.evaluate("totalDiapositivas")
        for i in range(n):
            r = pg.evaluate("""(i)=>{irA(i); const s=document.querySelectorAll('.slide')[i];
              const sb=s.getBoundingClientRect(); const f=s.querySelector('.s-foot');
              const ft=f?f.getBoundingClientRect().top:sb.bottom; const bad=new Set();
              s.querySelectorAll('.s-head *, .s-body, .s-body > *, .s-body .card, .s-body .note, .s-body pre, .s-body table, .s-body svg').forEach(e=>{
                const b=e.getBoundingClientRect(); if(!b.width) return;
                if(b.right>sb.right+1) bad.add('sale-derecha:'+e.tagName);
                if(f && b.bottom>ft+1 && !e.classList.contains('s-body')) bad.add('pisa-pie:'+e.tagName+'.'+(e.getAttribute('class')||''));
              });
              s.querySelectorAll('.s-body svg text').forEach(t=>{const b=t.getBoundingClientRect(); if(b.right>sb.right-20||b.left<sb.left+20) bad.add('texto-svg-al-borde');});
              return [...bad];}""", i)
            if capturas:
                Path(capturas).mkdir(parents=True, exist_ok=True)
                pg.screenshot(path=f"{capturas}/s{i+1:02d}.png")
            if r:
                out.append(f"  diap. {i+1}: {', '.join(r[:4])}")
        b.close()
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("html"); ap.add_argument("--capturas"); ap.add_argument("--sin-render", action="store_true")
    a = ap.parse_args()
    n, partes = metricas(a.html)
    print(f"{Path(a.html).name}: {n} diapositivas")
    for k, d in sorted(partes.items(), key=lambda x: str(x[0])):
        c = max(d["contenido"], 1)
        print(f"  Parte {k}: {d['contenido']} contenido · gráfico {d['grafico']} ({100*d['grafico']//c}%) · "
              f"diagrama {d['diagrama']} ({100*d['diagrama']//c}%) · guion {d['palabras']} palabras ≈ {d['palabras']/PPM:.1f} min"
              + (f" · {d['sin_guion']} SIN GUION" if d['sin_guion'] else ""))
    if not a.sin_render:
        r = desbordes(a.html, a.capturas)
        print("  Desbordes:" if r else "  Sin desbordes"); print("\n".join(r)) if r else None
