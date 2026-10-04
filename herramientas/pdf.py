#!/usr/bin/env python3
"""Genera el PDF (una página 1280x720 por diapositiva) desde el HTML de una semana.
Uso: python3 herramientas/pdf.py 2026-2-S01-....html [más archivos...]
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch()
    for h in sys.argv[1:]:
        h = Path(h).resolve()
        pg = b.new_page(viewport={"width": 1280, "height": 720})
        pg.goto(h.as_uri() + "?captura=1"); pg.wait_for_timeout(1000)
        pg.emulate_media(media="print")
        out = h.with_suffix(".pdf")
        pg.pdf(path=str(out), width="1280px", height="720px", print_background=True,
               margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
        print("PDF:", out.name); pg.close()
    b.close()
