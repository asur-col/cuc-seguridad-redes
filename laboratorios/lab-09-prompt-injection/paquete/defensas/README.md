# Defensas del Lab 9

Tres controles que se activan **una por una**, en este orden, para poder medir el aporte de cada uno:

| # | Control | Dónde se implementa | Cómo se activa |
|---|---------|---------------------|----------------|
| D1 | Refuerzo del prompt de sistema (delimitadores + reglas anti-inyección) | `.opencode/agent/saludvital.md` | pegar el texto de `d1-refuerzo-prompt.md` en el cuerpo del agente |
| D2 | Filtro de entrada | `defensas/d2-filtro-entrada.sh` | `cp d2-filtro-entrada.sh.ejemplo d2-filtro-entrada.sh` |
| D3 | Filtro de salida (bloquea el secreto) | `defensas/d3-filtro-salida.sh` | `cp d3-filtro-salida.sh.ejemplo d3-filtro-salida.sh` |

El asistente solo aplica un filtro si el archivo existe **y** es ejecutable. Para desactivar una
defensa y volver a medir sin ella:

```
chmod -x defensas/d2-filtro-entrada.sh     # D2 desactivada (se conserva el archivo)
```

Después de cada cambio corre la batería:

```
python3 bateria.py
```

Cada corrida añade un bloque con la fecha, la configuración detectada y la tasa de fuga por
ataque a `tabla-antes-despues.md`.

La plantilla del prompt reforzado se entrega en `d1-refuerzo-prompt.md`: ábrelo, copia su
contenido en el cuerpo del agente y ajusta lo que creas necesario. La medición te dice si te
quedó corto. El script `./asistente` ya envuelve cada pregunta entre `<<<DATOS>>>` y `<<<FIN>>>`,
así que D1 es únicamente texto: el modelo debe respetar esa frontera.
