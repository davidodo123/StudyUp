# G11 · Procesamiento de datos en EC2 con pandas y Jupyter

**Curso:** Curso de Especialización FP Aprendizaje Automático — Instalación, Despliegue y Explotación de Sistemas  
**Módulo:** Explotación de servicios de procesamiento y analítica de datos  
**Entorno:** Windows 11 → AWS Academy Learner Lab → Ubuntu en EC2  
**Duración orientativa:** 90–120 minutos  
**Requisitos:** G10; CSV de referencia; espacio y memoria suficientes; perfil S3 operativo.  
**Recursos:** EC2 y entorno Python existente; Jupyter opcional por túnel SSH.  
**Resultado:** Dataset limpio, informe de calidad y resumen reproducible por centro.

## Antes de empezar

1. Inicia el Learner Lab con **Start Lab** y espera a que esté activo.
2. Abre la consola AWS desde el enlace del Lab. Usa **París (`eu-west-3`) solo si está autorizada**, según G01 y las instrucciones actuales. Si se utiliza otra región, mantenla en toda la práctica.
3. Comprueba presupuesto y tiempo restante. Las cifras dependen de tu laboratorio; no se presupone gratuidad. La aparición de un servicio no garantiza permiso para utilizarlo.
4. Sigue el lugar de ejecución indicado: **PowerShell de Windows**, **terminal del Learner Lab** o **terminal Ubuntu de EC2**. No intercambies sus comandos.
5. En bloques con varias órdenes, ejecuta una línea cada vez, excepto los bloques de creación de archivos que se indique pegar completos. No copies los marcadores de Markdown.

> **Importante · Seguridad**  
> No compartas Account ID, UserId, ARN completo, Access Key, Secret Key, Session Token ni archivos privados `.pem`. No subas claves a EC2, S3, repositorios o herramientas de IA. Entrega resultados resumidos y capturas recortadas. Los permisos se conceden mediante los roles previstos por el laboratorio; no los amplíes para eludir una restricción.

## 1. Objetivo y reglas de calidad

```text
raw (15 filas) → quitar duplicados exactos → validar → curated (12 filas) → resumen
```

Aplicaremos reglas explícitas: ID numérico entero positivo; fecha válida; centro y servicio conocidos; peticiones enteras no negativas; latencia no negativa y presente. Eliminaremos duplicados exactos, no todas las filas con el mismo centro o servicio. Guardaremos el original y contaremos las exclusiones.

## 2. Prepara dependencias

En **Ubuntu EC2**:

```bash
cd ~/practicas-aws
source .venv/bin/activate
source lab.env
python -m pip install pandas numpy
mkdir -p datos/curated resultados
```

`pip` instala las bibliotecas dentro del entorno. `pandas` proporciona tablas y agrupaciones; NumPy soporta cálculo numérico. `mkdir` prepara salidas. Antes de instalar Jupyter comprueba `free -h` y `df -h /`.

## 3. Crea el procesador

En VS Code remoto crea `scripts/procesar.py` dentro de `/home/ubuntu/practicas-aws`. Pega:

```python
import json
from pathlib import Path
import pandas as pd

base = Path.home() / "practicas-aws"
raw = pd.read_csv(base / "datos/raw/metricas_raw.csv", encoding="utf-8-sig")
columnas = ["id", "fecha", "centro", "servicio", "peticiones", "latencia_ms"]
if list(raw.columns) != columnas:
    raise SystemExit("Revisa el esquema del CSV antes de procesar.")

sin_duplicados = raw.drop_duplicates().copy()
for nombre in ["id", "peticiones", "latencia_ms"]:
    sin_duplicados[nombre] = pd.to_numeric(sin_duplicados[nombre], errors="coerce")
fechas = pd.to_datetime(sin_duplicados["fecha"], format="%Y-%m-%d", errors="coerce")
valida = (
    sin_duplicados["id"].gt(0)
    & sin_duplicados["id"].mod(1).eq(0)
    & fechas.notna()
    & sin_duplicados["centro"].isin(["madrid", "sevilla", "valencia"])
    & sin_duplicados["servicio"].isin(["inferencia", "analitica"])
    & sin_duplicados["peticiones"].ge(0)
    & sin_duplicados["peticiones"].mod(1).eq(0)
    & sin_duplicados["latencia_ms"].ge(0)
)
limpio = sin_duplicados.loc[valida, columnas].copy()
limpio["id"] = limpio["id"].astype("int64")
limpio["peticiones"] = limpio["peticiones"].astype("int64")
limpio["fecha"] = fechas.loc[valida].dt.strftime("%Y-%m-%d")
resumen = limpio.groupby("centro", as_index=False).agg(
    peticiones_totales=("peticiones", "sum"),
    latencia_media_ms=("latencia_ms", "mean"),
    registros=("id", "count"),
).sort_values("centro")
calidad = {
    "filas_raw": len(raw),
    "duplicados_exactos": len(raw) - len(sin_duplicados),
    "invalidas_tras_deduplicar": int((~valida).sum()),
    "filas_limpias": len(limpio),
    "peticiones_totales": int(limpio["peticiones"].sum()),
}
(base / "datos/curated").mkdir(parents=True, exist_ok=True)
(base / "resultados").mkdir(parents=True, exist_ok=True)
limpio.to_csv(base / "datos/curated/metricas_limpias.csv", index=False)
resumen.to_csv(base / "resultados/resumen_centros.csv", index=False)
(base / "resultados/calidad.json").write_text(
    json.dumps(calidad, indent=2), encoding="utf-8"
)
print(json.dumps(calidad, indent=2))
print(resumen.to_string(index=False))
```

`errors="coerce"` transforma valores no interpretables en ausentes; las reglas los excluyen. `groupby` agrupa por centro; `agg` calcula suma, media y conteo. `index=False` evita una columna de índice adicional en los CSV. [pandas: estadísticas y agrupación](https://pandas.pydata.org/docs/getting_started/intro_tutorials/06_calculate_statistics.html).

## 4. Ejecuta y valida el resultado

```bash
python scripts/procesar.py
```

**Resultado esperado:** 15 filas raw, 1 duplicado, 2 inválidas después de quitar duplicados, **12 filas limpias** y **1.800 peticiones**.

| Centro | Peticiones totales | Latencia media ms | Registros |
|---|---:|---:|---:|
| madrid | 620 | 96,25 | 4 |
| sevilla | 640 | 118,75 | 4 |
| valencia | 540 | 96,25 | 4 |

La media es aritmética por registro; no una media ponderada por peticiones. No cambies esta definición al comparar motores.

> **Si algo falla**  
> Ante archivo no encontrado, repite G10 y revisa la ruta. Si hay distinta cantidad de filas, contrasta el dataset. Un proceso terminado con `Killed` puede indicar falta de memoria: comprueba recursos y consulta al docente; no aumentes tamaño sin autorización.

> **Qué está ocurriendo**  
> Has separado transporte, calidad y cálculo. El original permanece intacto; el informe explica qué filas se excluyeron. Así puedes repetir el proceso y justificar por qué las métricas usan 12 registros.

## 5. Publica únicamente las salidas previstas en S3

```bash
aws s3 cp datos/curated/metricas_limpias.csv "s3://$BUCKET/curated/metricas/metricas_limpias.csv" --region "$AWS_REGION"
aws s3 cp resultados/resumen_centros.csv "s3://$BUCKET/resultados/resumen_centros.csv" --region "$AWS_REGION"
aws s3 cp resultados/calidad.json "s3://$BUCKET/resultados/calidad.json" --region "$AWS_REGION"
```

Las órdenes suben los tres archivos a sus capas. Pueden reemplazar versiones previas de esos mismos objetos: revisa que el bucket y el prefijo sean propios. **No subas el resumen al prefijo `curated/metricas/`**, porque tiene otro esquema. Comprueba los objetos en consola.

## 6. Jupyter opcional mediante un túnel

Solo si la capacidad de la instancia lo permite. En Ubuntu, con `.venv` activo:

```bash
python -m pip install jupyterlab
jupyter lab --no-browser --ip=127.0.0.1 --port=8888 --ServerApp.port_retries=0
```

Escucha solo en la propia EC2. Conserva habilitada la autenticación por token y no compartas el token ni captures su URL completa. `port_retries=0` evita cambiar de puerto silenciosamente.

En una **segunda ventana PowerShell de Windows**, usando el alias de G06:

```powershell
ssh -N -L 127.0.0.1:8888:127.0.0.1:8888 fp-analytics
```

`-N` no abre una shell; `-L` reenvía el puerto local por SSH al puerto remoto. En Edge abre `http://127.0.0.1:8888` e introduce el token mostrado **en tu terminal Ubuntu**. No abras TCP/8888 en el Security Group. [Jupyter: seguridad del servidor](https://jupyter-server.readthedocs.io/en/stable/operators/public-server.html).

Crea un notebook y ejecuta una celda:

```python
from pathlib import Path
import pandas as pd
base = Path.home() / "practicas-aws"
pd.read_csv(base / "resultados/resumen_centros.csv")
```

Comprueba que se muestran los tres centros. Guarda el notebook. Si el puerto local está ocupado, usa `127.0.0.1:8889:127.0.0.1:8888` en el túnel y abre localhost:8889. No desactives la autenticación.

## 7. Entrega, cierre y resumen

Entrega programa, `calidad.json`, resumen y explicación de las reglas. Registra versiones con `python -m pip freeze > resultados/requirements-usadas.txt`; no contiene credenciales y permitirá al docente fijar el entorno ensayado.

Si abriste Jupyter, pulsa Ctrl+C y confirma su parada en Ubuntu; cierra el túnel con Ctrl+C en Windows. Guarda archivos, detén EC2 cuando termine la clase y pulsa End Lab. Conserva S3 para G12–G14.

**Resumen:** tienes una transformación reproducible, con conteos de calidad. **Reto:** calcula el total por servicio: inferencia debe sumar 750 y analítica 1.050.
