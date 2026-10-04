# Cómo generar los videos (en tu computador)

Los videos **no se generan en el repositorio**: se producen localmente con la misma voz de los videos anteriores
(`es-CO-GonzaloNeural`, voz neuronal de Edge). Cada semana produce 4 MP4 de ~15 min, cortados en cada diapositiva "Parte X de 4".

## Una sola vez
```bash
git pull
pip install playwright edge-tts beautifulsoup4
playwright install chromium
# FFmpeg en el PATH:  Windows: winget install Gyan.FFmpeg · macOS: brew install ffmpeg · Linux: apt install ffmpeg
```
Requiere Internet (edge-tts usa el servicio de voz de Microsoft).

## Por semana (un comando)
```bash
python3 herramientas/videos.py 2026-2-S01-seguridad-redes-panorama-amenazas-zero-trust.html
```
Resultado: `videos/<archivo>-parte1.mp4` … `-parte4.mp4` (1920×1080, H.264 + AAC).
- Solo algunas partes: `--partes 2 3`
- Otra velocidad de voz: `--velocidad -5%` · otra voz: `--voz es-CO-SalomeNeural`
- Prueba sin voz (audio en silencio, para revisar tiempos): `--sin-voz`
- La voz de cada diapositiva se guarda en `.cache-videos/`; si editas un guion solo se vuelve a sintetizar lo que cambió.

## Después
```bash
python3 herramientas/pdf.py <archivo>.html      # PDF (una página por diapositiva)
python3 herramientas/indice.py                  # actualiza index.html con los enlaces a los videos que existan
git add videos index.html && git commit -m "Videos Semana N" && git push
```

## Guiones
`python3 herramientas/guiones.py todas` escribe `guiones/<semana>.md` con el texto de cada diapositiva y los cortes de video marcados (✂), para revisarlos o leerlos en voz alta.
Para corregir un guion edita `fuentes/SNN/parteN.html` (bloque `<aside class="notes">`) y reconstruye con `python3 herramientas/construir.py SNN`.

## Si algo falla
- *No se puede conectar a speech.platform.bing.com*: revisa Internet/proxy; el script reintenta 4 veces.
- *FFmpeg no encontrado*: instálalo y abre una terminal nueva.
- Los videos antiguos de S01–S08 (voz sin cortes por parte) siguen enlazados hasta que generes los nuevos.
