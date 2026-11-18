"""Verificador del Lab C2: los datos, el modelo y las metricas del informe cuadran entre si."""
import csv, io, json
from .base import falla, ok

ID = "c2-ndr"
TITULO = "Clasificador NDR"

def _csv(texto):
    if not texto:
        return None
    return list(csv.DictReader(io.StringIO(texto)))

def revisar(ctx):
    r = []

    entrena = _csv(ctx.leer("datos/entrenamiento.csv"))
    prueba = _csv(ctx.leer("datos/prueba.csv"))
    if not entrena or not prueba:
        return [falla("datos", "faltan datos/entrenamiento.csv o datos/prueba.csv",
                      "Ejecuta el generador del paso A.2 con semilla 2027.")]

    if len(entrena) >= 1000 and len(prueba) >= 500:
        r.append(ok("datos", "conjuntos presentes: %d de entrenamiento y %d de prueba" % (len(entrena), len(prueba))))
    else:
        r.append(falla("datos", "los conjuntos son muy pequenos: %d y %d" % (len(entrena), len(prueba)),
                       "Vuelve a generar con --filas 4000 como en A.2."))

    etiquetas = {f.get("etiqueta") for f in prueba}
    if len(etiquetas) >= 2:
        r.append(ok("clases", "el conjunto de prueba tiene las dos clases: " + ", ".join(sorted(etiquetas))))
    else:
        r.append(falla("clases", "el conjunto de prueba tiene una sola clase",
                       "Revisa el reparto del paso A.2: si una clase casi no aparece, el modelo no aprende."))

    pred = _csv(ctx.leer("predicciones.csv"))
    if not pred:
        r.append(falla("predicciones", "no existe predicciones.csv", "Ejecuta el paso B.1: predecir.py."))
        return r
    if len(pred) != len(prueba):
        r.append(falla("predicciones", "predicciones.csv tiene %d filas y la prueba %d" % (len(pred), len(prueba)),
                       "Vuelve a predecir sobre todo el conjunto: no filtres filas."))
        return r
    r.append(ok("predicciones", "hay una prediccion por cada fila de la prueba"))

    col_pred = "prediccion" if "prediccion" in pred[0] else list(pred[0].keys())[-1]
    clases_pred = {f.get(col_pred) for f in pred}
    if len(clases_pred) >= 2:
        r.append(ok("modelo", "el modelo predice las dos clases, no solo una"))
    else:
        r.append(falla("modelo", "el modelo predice una sola clase: " + ", ".join(str(x) for x in clases_pred),
                       "Mira la matriz de confusion: un modelo que dice siempre lo mismo suele venir de clases desbalanceadas."))

    metricas = ctx.leer("metricas.json")
    try:
        m = json.loads(metricas) if metricas else None
    except json.JSONDecodeError:
        m = None
    if not m or "matriz" not in m:
        r.append(falla("metricas", "metricas.json no tiene matriz de confusion", "Ejecuta el paso B.1: evaluar.py."))
        return r
    r.append(ok("metricas", "el informe incluye matriz de confusion"))

    reales = [f.get("etiqueta") for f in prueba]
    predichas = [f.get(col_pred) for f in pred]
    aciertos = sum(1 for a, b in zip(reales, predichas) if a == b)
    exactitud = aciertos / len(reales)
    declarada = m.get("exactitud")
    if declarada is None:
        r.append(falla("coherencia", "metricas.json no declara exactitud",
                       "Vuelve a ejecutar evaluar.py sin editar el archivo a mano."))
    elif abs(float(declarada) - exactitud) <= 0.01:
        r.append(ok("coherencia", "la exactitud del informe coincide con la recalculada (%.3f)" % exactitud))
    else:
        r.append(falla("coherencia", "la exactitud declarada (%.3f) no cuadra con la recalculada (%.3f)"
                       % (float(declarada), exactitud),
                       "No edites las metricas: recalcula con evaluar.py sobre datos/prueba.csv."))
    return r
