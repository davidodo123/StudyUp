# G16 · Mini plataforma de analítica de datos en AWS

**Curso:** Curso de Especialización FP Aprendizaje Automático — Instalación, Despliegue y Explotación de Sistemas  
**Módulo:** Explotación de servicios de procesamiento y analítica de datos  
**Entorno:** Windows 11 → AWS Academy Learner Lab → Ubuntu en EC2  
**Duración orientativa:** 2–3 sesiones de 90 minutos  
**Requisitos:** G01–G11; catálogo/Athena y Spark según permisos confirmados; Python funcional.  
**Recursos:** Misma EC2 Ubuntu y bucket; catálogo/Athena opcionales; sin nuevos servicios obligatorios.  
**Resultado:** Proyecto reproducible sobre un dataset real, con trazabilidad, informe y limpieza final.

## Antes de empezar

1. Inicia el Learner Lab con **Start Lab** y espera a que esté activo.
2. Abre la consola AWS desde el enlace del Lab. Usa **París (`eu-west-3`) solo si está autorizada**, según G01 y las instrucciones actuales. Si se utiliza otra región, mantenla en toda la práctica.
3. Comprueba presupuesto y tiempo restante. Las cifras dependen de tu laboratorio; no se presupone gratuidad. La aparición de un servicio no garantiza permiso para utilizarlo.
4. Sigue el lugar de ejecución indicado: **PowerShell de Windows**, **terminal del Learner Lab** o **terminal Ubuntu de EC2**. No intercambies sus comandos.
5. En bloques con varias órdenes, ejecuta una línea cada vez, excepto los bloques de creación de archivos que se indique pegar completos. No copies los marcadores de Markdown.

> **Importante · Seguridad**  
> No compartas Account ID, UserId, ARN completo, Access Key, Secret Key, Session Token ni archivos privados `.pem`. No subas claves a EC2, S3, repositorios o herramientas de IA. Entrega resultados resumidos y capturas recortadas. Los permisos se conceden mediante los roles previstos por el laboratorio; no los amplíes para eludir una restricción.

## 1. Encargo y alcance

Construirás una plataforma pequeña que conserva un dataset real, lo valida, genera una capa analítica y permite consultarla. El objetivo es explotar datos y demostrar que el flujo se puede repetir; no entrenar un modelo ni añadir muchos servicios.

```text
UCI Iris → raw S3 → validación Python Ubuntu → curated S3
                                             ├── informe pandas
                                             └── catálogo → Athena, si autorizado
```

Usaremos **Iris de UCI**: 150 observaciones, cuatro medidas en centímetros y tres clases de 50. Su licencia es CC BY 4.0. Referencia: Fisher, R. (1936), Iris [Dataset], UCI Machine Learning Repository, DOI 10.24432/C56C76. La fuente documenta diferencias entre versiones históricas: conserva el archivo exacto y su hash en vez de corregir muestras silenciosamente. [UCI: Iris](https://archive.ics.uci.edu/dataset/53/iris).

## 2. Sesión 1: prepara y conserva la fuente

1. Comprueba región, permisos y presupuesto; reutiliza tu EC2 y bucket.
2. Conecta a Ubuntu. En su terminal ejecuta:

```bash
cd ~/practicas-aws
source .venv/bin/activate
source lab.env
mkdir -p datos/raw/iris datos/curated/iris resultados/iris
curl --fail --location https://archive.ics.uci.edu/static/public/53/iris.zip -o datos/raw/iris/iris.zip
sha256sum datos/raw/iris/iris.zip
```

`curl` obtiene el archivo de la fuente oficial; `sha256sum` identifica esos bytes. Si la descarga está bloqueada, utiliza una copia de la misma fuente facilitada por el docente y registra cómo la recibiste. No uses la copia de sklearn como si fuera necesariamente el mismo archivo histórico.

## 3. Crea un programa de validación y transformación

En VS Code remoto crea `scripts/proyecto_iris.py`:

```python
import hashlib
import io
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd

base = Path.home() / "practicas-aws"
archivo_zip = base / "datos/raw/iris/iris.zip"
with zipfile.ZipFile(archivo_zip) as paquete:
    candidatos = [n for n in paquete.namelist() if Path(n).name == "iris.data"]
    if len(candidatos) != 1:
        raise SystemExit("Revisa el contenido de la descarga con el docente.")
    original = paquete.read(candidatos[0])
(base / "datos/raw/iris/iris_original.data").write_bytes(original)
medidas = ["sepal_length_cm", "sepal_width_cm", "petal_length_cm", "petal_width_cm"]
datos = pd.read_csv(io.BytesIO(original), header=None, names=medidas + ["species"])
for nombre in medidas:
    datos[nombre] = pd.to_numeric(datos[nombre], errors="coerce")
datos["species"] = datos["species"].astype("string").str.strip()
especies = {"Iris-setosa", "Iris-versicolor", "Iris-virginica"}
validas = datos[medidas].notna().all(axis=1) & datos[medidas].gt(0).all(axis=1)
validas &= datos["species"].isin(especies)
if len(datos) != 150 or not validas.all():
    raise SystemExit("La fuente no cumple 150 filas válidas. Documenta y revisa antes de publicar.")
conteos = datos.groupby("species").size()
if set(conteos.index) != especies or not conteos.eq(50).all():
    raise SystemExit("Revisa la distribución de clases de la fuente.")
datos.insert(0, "id", range(1, len(datos) + 1))
resumen = datos.groupby("species", as_index=False).agg(
    registros=("id", "count"),
    petal_length_media_cm=("petal_length_cm", "mean"),
    petal_width_media_cm=("petal_width_cm", "mean"),
)
curated = base / "datos/curated/iris"
salidas = base / "resultados/iris"
curated.mkdir(parents=True, exist_ok=True)
salidas.mkdir(parents=True, exist_ok=True)
datos.to_csv(curated / "iris_curated.csv", index=False)
resumen.to_csv(salidas / "resumen.csv", index=False)
procedencia = {
    "fuente": "https://archive.ics.uci.edu/dataset/53/iris",
    "doi": "10.24432/C56C76",
    "licencia": "CC BY 4.0",
    "archivo_interno": candidatos[0],
    "sha256_zip": hashlib.sha256(archivo_zip.read_bytes()).hexdigest(),
    "sha256_original": hashlib.sha256(original).hexdigest(),
    "procesado_utc": datetime.now(timezone.utc).isoformat(),
    "filas_validas": len(datos),
    "duplicados_de_medidas": int(datos.drop(columns="id").duplicated().sum()),
}
(salidas / "procedencia.json").write_text(
    json.dumps(procedencia, indent=2), encoding="utf-8"
)
print("Filas válidas:", len(datos))
print(resumen.to_string(index=False))
```

No se extraen rutas del ZIP al sistema de archivos: se lee únicamente el archivo esperado. La validación comprueba tipos, valores positivos, número de filas y clases. Las medidas idénticas no se eliminan automáticamente: dos observaciones reales pueden tener las mismas medidas. El ID añadido es técnico y depende del orden del archivo; no es un identificador biológico.

Ejecuta:

```bash
python scripts/proyecto_iris.py
```

**Esperado:** 150 válidas y tres clases con 50 registros. Guarda los promedios realmente obtenidos y el hash; se compararán con SQL sobre **esa misma entrada**.

> **Qué está ocurriendo**  
> La procedencia identifica qué archivo real se procesó; el contrato comprueba su estructura y las métricas permiten contrastar motores. Preservar observaciones con medidas repetidas es una decisión del dominio, diferente de eliminar un duplicado deliberado del CSV sintético.

> **Si algo falla**  
> Si la descarga, el número de filas o las clases no cumplen el contrato, guarda la evidencia y consulta la fuente con el docente antes de publicar curated. Si S3 o el catálogo deniegan una operación, utiliza la ruta habilitada y documenta la parte pendiente.

## 4. Publica raw, curated e informes

En Ubuntu:

```bash
aws s3 cp datos/raw/iris/iris.zip "s3://$BUCKET/raw/iris/iris.zip" --region "$AWS_REGION"
aws s3 cp datos/raw/iris/iris_original.data "s3://$BUCKET/raw/iris/iris_original.data" --region "$AWS_REGION"
aws s3 cp datos/curated/iris/iris_curated.csv "s3://$BUCKET/curated/iris/iris_curated.csv" --region "$AWS_REGION"
aws s3 cp resultados/iris/resumen.csv "s3://$BUCKET/resultados/iris/resumen.csv" --region "$AWS_REGION"
aws s3 cp resultados/iris/procedencia.json "s3://$BUCKET/resultados/iris/procedencia.json" --region "$AWS_REGION"
```

Cada orden publica una clave propia. Conserva la atribución junto al informe. El prefijo raw/iris contiene archivo comprimido y original: **no lo uses como ubicación de una única tabla CSV**. La tabla siguiente lee solo curated/iris.

## 5. Sesión 2: catálogo y explotación

Si hay crawler autorizado, replica G13 con un **crawler propio para Iris**, origen `curated/iris/` y prefijo `g16_`. No cambies el origen del crawler de métricas sin registrar el cambio. Revisa nombres, tipos, cabecera y 150 filas.

Alternativa manual si catálogo y Athena están permitidos: ejecuta en el editor Athena este DDL, cambiando el bucket y tu base si procede:

```sql
CREATE EXTERNAL TABLE IF NOT EXISTS fp_analytics.iris_curated (
    id string,
    sepal_length_cm string,
    sepal_width_cm string,
    petal_length_cm string,
    petal_width_cm string,
    species string
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES ('separatorChar' = ',', 'quoteChar' = '"')
STORED AS TEXTFILE
LOCATION 's3://NOMBRE_REAL_DEL_BUCKET/curated/iris/'
TBLPROPERTIES ('skip.header.line.count' = '1');
```

Se aplica el mismo patrón de CSV de G12 a un esquema diferente. Si usas el crawler, cambia las referencias de las consultas a la tabla real que generó.

```sql
SELECT COUNT(*) AS observaciones FROM fp_analytics.iris_curated;
```

```sql
SELECT species,
       COUNT(*) AS registros,
       AVG(TRY_CAST(petal_length_cm AS DOUBLE)) AS petal_length_media_cm,
       AVG(TRY_CAST(petal_width_cm AS DOUBLE)) AS petal_width_media_cm
FROM fp_analytics.iris_curated
GROUP BY species
ORDER BY species;
```

Contrasta 150 filas, 50 por clase y medias de pandas, admitiendo solo diferencias mínimas de representación numérica. Registra duración y bytes escaneados. Si Athena no está autorizado, realiza la explotación con pandas y documenta esa sustitución.

## 6. Sesión 3: reproducibilidad y presentación

1. Vuelve a ejecutar el procesador con el mismo ZIP.
2. Comprueba que el hash original, las filas y las métricas coinciden. La fecha de procesamiento puede cambiar.
3. Guarda scripts, SQL, requisitos utilizados, informe y procedencia en Windows, mediante descarga desde VS Code remoto o la consola S3.
4. Redacta un informe con origen/licencia, arquitectura, reglas, resultados, restricciones y consumo observado. No confundas presupuesto restante con coste exacto de tu proyecto si hay otros recursos.
5. Explica qué cambiarías para un dataset mayor: procesamiento por bloques, formato columnar, particiones y cómputo distribuido. No lo despliegues automáticamente.

**Reto opcional:** adapta el programa Spark de G15 al esquema Iris y compara conteos y medias. No reutilices el esquema de métricas sin cambiarlo.

## 7. Entregables y criterios de evaluación

| Criterio | Peso orientativo |
|---|---:|
| Acceso seguro y configuración coherente | 20 % |
| Procedencia, contrato y calidad de datos | 25 % |
| Pipeline reproducible | 25 % |
| Explotación y comparación justificadas | 20 % |
| Inventario y cierre/limpieza | 10 % |

Entrega README del proyecto, programa, SQL si se utilizó, procedencia, resumen y evidencias recortadas. Una restricción bien documentada no debe penalizarse como si fuera un error del alumno; el docente adapta la rúbrica a la ruta habilitada.

## 8. Limpieza final, tras guardar y revisar la entrega

Realiza la limpieza de fin de colección solo cuando el docente confirme que ya no necesitarás estos recursos.

1. Guarda y descarga todas tus salidas; verifica que puedes abrirlas en Windows.
2. Detén servidor web/Jupyter, cierra túneles y confirma que no hay trabajos gestionados activos.
3. Detén y elimina únicamente tus aplicaciones EMR Serverless de práctica, si las creaste. Conserva Studios/roles compartidos.
4. En Glue elimina crawlers propios y tablas propias; elimina bases solo si están vacías y son tuyas. En Athena elimina primero vistas y después tablas externas propias. No elimines bases compartidas.
5. En S3 revisa los objetos propios antes de borrarlos. Si el bucket es exclusivamente tuyo y está autorizado eliminarlo, vacíalo y bórralo. Si tiene versionado, vaciar requiere gestionar también versiones y marcadores; utiliza el procedimiento del docente. En un bucket compartido, borra solo tus prefijos autorizados.
6. En EC2 selecciona la instancia correcta y **Terminate** solo ahora, con la copia verificada. Comprueba después sus volúmenes y elimina únicamente discos propios no necesarios que hayan quedado sin asociar.
7. Elimina tu Security Group cuando ya no haya interfaces que lo usen. No borres VPC, rutas ni subredes del Lab.
8. Elimina el registro del Key Pair propio si ya no se usa. Retira de Windows la entrada SSH y, cuando no sea necesaria para ninguna instancia, la clave privada propia según la política del centro.
9. Revisa el inventario y presupuesto, pulsa **End Lab** y confirma cierre.

> **Importante**  
> Terminar EC2, borrar objetos o eliminar una clave es irreversible para los datos afectados. La copia y la revisión del alcance van antes de confirmar. End Lab no sustituye esta limpieza de recursos.

**Resumen:** has completado una plataforma pequeña de almacenamiento, procesamiento y explotación sobre datos reales, con seguridad, evidencias y un cierre verificable.
