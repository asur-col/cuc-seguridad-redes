#!/usr/bin/env python3
"""Genera los 4 videos (MP4 1920x1080) de una semana a partir de su HTML.

Por cada diapositiva: captura de pantalla + narración del <aside class="notes"> con voz
sintética (edge-tts, es-CO-GonzaloNeural, la misma de los videos anteriores) + FFmpeg.
Cada diapositiva con data-parte="N" abre un video nuevo: <archivo>-parteN.mp4 en videos/.

Uso:
  python3 herramientas/videos.py 2026-2-S01-seguridad-redes-panorama-amenazas-zero-trust.html
  python3 herramientas/videos.py <html> --partes 2 3        # solo algunas partes
  python3 herramientas/videos.py <html> --sin-voz           # prueba sin red: audio en silencio
Opciones: --voz es-CO-GonzaloNeural  --velocidad +0%

Requisitos (una vez):  pip install playwright edge-tts beautifulsoup4
                       playwright install chromium
                       FFmpeg en el PATH (Windows: winget install Gyan.FFmpeg)
"""
import argparse, asyncio, hashlib, shutil, subprocess, sys
from pathlib import Path
from bs4 import BeautifulSoup

RAIZ = Path(__file__).resolve().parent.parent
CACHE = RAIZ / ".cache-videos"
PAUSA = 0.8      # segundos de silencio al final de cada diapositiva
PPM = 150        # solo para --sin-voz


def guiones(html):
    soup = BeautifulSoup(Path(html).read_text(encoding="utf-8"), "html.parser")
    out = []
    for s in soup.select("#stage > section.slide"):
        n = s.find("aside", class_="notes")
        out.append((s.get("data-parte"), n.get_text(" ", strip=True) if n else ""))
    return out


def capturar(html, carpeta, n):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1280, "height": 720}, device_scale_factor=1.5)
        pg.goto(Path(html).resolve().as_uri() + "?captura=1"); pg.wait_for_timeout(1200)
        for i in range(n):
            pg.evaluate(f"irA({i})"); pg.wait_for_timeout(120)
            pg.screenshot(path=str(carpeta / f"d{i+1:03d}.png"))
        b.close()


async def tts(texto, destino, voz, velocidad):
    import edge_tts
    await edge_tts.Communicate(texto, voz, rate=velocidad).save(str(destino))


def duracion(f):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


def audio(texto, voz, velocidad, sin_voz):
    CACHE.mkdir(exist_ok=True)
    clave = hashlib.sha1(f"{voz}|{velocidad}|{sin_voz}|{texto}".encode()).hexdigest()[:16]
    f = CACHE / f"{clave}.mp3"
    if f.exists() and f.stat().st_size > 0:
        return f
    if sin_voz or not texto.strip():
        seg = max(3.0, len(texto.split()) / PPM * 60)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
                        "-t", f"{seg:.2f}", "-q:a", "9", str(f)], check=True)
    else:
        for intento in range(4):
            try:
                asyncio.run(tts(texto, f, voz, velocidad)); break
            except Exception as e:
                if intento == 3: raise
                print("   reintento TTS:", e)
    return f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html"); ap.add_argument("--partes", nargs="*", type=int)
    ap.add_argument("--voz", default="es-CO-GonzaloNeural"); ap.add_argument("--velocidad", default="+0%")
    ap.add_argument("--sin-voz", action="store_true")
    a = ap.parse_args()
    if not shutil.which("ffmpeg"):
        sys.exit("Falta FFmpeg en el PATH")
    html = Path(a.html).resolve()
    g = guiones(html)
    tmp = CACHE / html.stem; tmp.mkdir(parents=True, exist_ok=True)
    print(f"Capturando {len(g)} diapositivas…"); capturar(html, tmp, len(g))
    # agrupar por parte
    partes, actual = {}, None
    for i, (marca, texto) in enumerate(g):
        if marca: actual = int(marca)
        partes.setdefault(actual, []).append((i + 1, texto))
    (RAIZ / "videos").mkdir(exist_ok=True)
    for n, items in partes.items():
        if a.partes and n not in a.partes: continue
        print(f"Parte {n}: {len(items)} diapositivas")
        lista = tmp / f"parte{n}.txt"; segs = []
        for k, texto in items:
            au = audio(texto, a.voz, a.velocidad, a.sin_voz)
            d = duracion(au) + PAUSA
            seg = tmp / f"seg{k:03d}.mp4"
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-loop", "1", "-i", str(tmp / f"d{k:03d}.png"),
                            "-i", str(au), "-af", f"apad=pad_dur={PAUSA}", "-t", f"{d:.2f}",
                            "-vf", "scale=1920:1080:flags=lanczos,format=yuv420p", "-r", "30",
                            "-c:v", "libx264", "-tune", "stillimage", "-preset", "medium", "-crf", "22",
                            "-c:a", "aac", "-b:a", "128k", "-ar", "24000", "-ac", "1", str(seg)], check=True)
            segs.append(seg)
        lista.write_text("".join(f"file '{s.as_posix()}'\n" for s in segs))
        out = RAIZ / "videos" / f"{html.stem}-parte{n}.mp4"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lista),
                        "-c", "copy", "-movflags", "+faststart", str(out)], check=True)
        print(f"   → {out.relative_to(RAIZ)} ({duracion(out)/60:.1f} min)")


if __name__ == "__main__":
    main()
