#!/usr/bin/env python3
"""Regenera las tarjetas de semanas de index.html (entre los marcadores SEMANAS:INICIO/FIN).

Fuente: fuentes/SNN/semana.json. Campo "publicada": true → tarjeta con enlaces;
false → tarjeta gris "Próximamente" SIN enlace. Los enlaces de video solo aparecen
si los MP4 existen en videos/ (primero -parteN.mp4; si no, el video único anterior).
Uso: python3 herramientas/indice.py
"""
import json, re, html
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def tarjeta(m):
    num = m["etiqueta"].split(" ", 1)[1]
    t = f'{m["etiqueta"]} · {html.escape(m["titulo_corto"])}'
    d = html.escape(m.get("descripcion", ""))
    if not m.get("publicada"):
        return (f'      <div class="week-card pending">\n        <div class="num">{num}</div>\n'
                f'        <div>\n          <div class="title">{t}</div>\n          <div class="desc">{d}</div>\n        </div>\n'
                f'        <div class="go">Próximamente</div>\n      </div>')
    a = m["archivo"]
    links = [f'<a class="go" href="{a}.html" target="_blank">Ver HTML →</a>']
    if (RAIZ / f"{a}.pdf").exists():
        links.append(f'<a class="go" href="{a}.pdf" target="_blank">Ver PDF →</a>')
    partes = [n for n in range(1, 5) if (RAIZ / "videos" / f"{a}-parte{n}.mp4").exists()]
    if partes:
        links += [f'<a class="go" href="videos/{a}-parte{n}.mp4" target="_blank">Video Parte {n} →</a>' for n in partes]
    elif (RAIZ / "videos" / f"{a}.mp4").exists():
        links.append(f'<a class="go" href="videos/{a}.mp4" target="_blank">Ver video →</a>')
    g = "\n          ".join(links)
    return (f'      <div class="week-card multi">\n        <div class="num">{num}</div>\n'
            f'        <div>\n          <div class="title">{t}</div>\n          <div class="desc">{d}</div>\n        </div>\n'
            f'        <div class="go-group">\n          {g}\n        </div>\n      </div>')


def main():
    metas = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((RAIZ / "fuentes").glob("S*/semana.json"))]
    metas.sort(key=lambda m: m["semana"])
    pub = sum(1 for m in metas if m.get("publicada"))
    bloque = "\n".join(tarjeta(m) for m in metas)
    idx = RAIZ / "index.html"
    s = idx.read_text(encoding="utf-8")
    s = re.sub(r"<!-- SEMANAS:INICIO -->.*?<!-- SEMANAS:FIN -->",
               lambda x: "<!-- SEMANAS:INICIO -->\n" + bloque + "\n      <!-- SEMANAS:FIN -->", s, flags=re.S)
    s = re.sub(r'<span class="count">\d+ de \d+ publicadas</span>', f'<span class="count">{pub} de {len(metas)} publicadas</span>', s)
    idx.write_text(s, encoding="utf-8")
    print(f"index.html: {pub} de {len(metas)} semanas publicadas")


if __name__ == "__main__":
    main()
