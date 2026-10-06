# G15 · Spark y fundamentos del procesamiento distribuido

**Curso:** Curso de Especialización FP Aprendizaje Automático — Instalación, Despliegue y Explotación de Sistemas  
**Módulo:** Explotación de servicios de procesamiento y analítica de datos  
**Entorno:** Windows 11 → AWS Academy Learner Lab → Ubuntu en EC2  
**Duración orientativa:** 90–120 minutos; ampliación gestionada opcional  
**Requisitos:** G11; Ubuntu con capacidad aprobada, propuesta mínima 4 GiB de RAM y espacio para Spark.  
**Recursos:** EC2 Ubuntu y Spark local; EMR Serverless solo si está comprobado y autorizado.  
**Resultado:** Agregación PySpark contrastada con pandas; distinción entre ejecución local y distribuida.

## Antes de empezar

1. Inicia el Learner Lab con **Start Lab** y espera a que esté activo.
2. Abre la consola AWS desde el enlace del Lab. Usa **París (`eu-west-3`) solo si está autorizada**, según G01 y las instrucciones actuales. Si se utiliza otra región, mantenla en toda la práctica.
3. Comprueba presupuesto y tiempo restante. Las cifras dependen de tu laboratorio; no se presupone gratuidad. La aparición de un servicio no garantiza permiso para utilizarlo.
4. Sigue el lugar de ejecución indicado: **PowerShell de Windows**, **terminal del Learner Lab** o **terminal Ubuntu de EC2**. No intercambies sus comandos.
5. En bloques con varias órdenes, ejecuta una línea cada vez, excepto los bloques de creación de archivos que se indique pegar completos. No copies los marcadores de Markdown.

> **Importante · Seguridad**  
> No compartas Account ID, UserId, ARN completo, Access Key, Secret Key, Session Token ni archivos privados `.pem`. No subas claves a EC2, S3, repositorios o herramientas de IA. Entrega resultados resumidos y capturas recortadas. Los permisos se conceden mediante los roles previstos por el laboratorio; no los amplíes para eludir una restricción.

## 1. Alcance y elección de ruta

```text
Ruta base: CSV limpio local → Spark local[2] en Ubuntu → resultados locales
Opcional:  CSV limpio S3 → ejecución Spark gestionada → resultados S3
```

La ruta base utiliza una única EC2 Ubuntu. Dos hilos locales **no equivalen a dos máquinas ni prueban escalado distribuido**. Sirve para comprender DataFrames, particiones, transformaciones y acciones. Si el laboratorio admite ejecución gestionada, se podrá comparar con EMR Serverless. No se propondrán clústeres EMR sobre EC2 que sustituyan la base Ubuntu por Amazon Linux.

Si tu instancia no tiene capacidad aprobada, realiza la lectura y comparación conceptual o usa la máquina Ubuntu de demostración del docente. No ejecutes Spark en una micro suponiendo que memoria virtual o una ampliación no autorizada resolverán el problema.

## 2. Instala en un entorno separado

En **Ubuntu EC2**:

```bash
free -h
df -h /
python3 --version
sudo apt-get update
sudo apt-get install -y openjdk-17-jre-headless
java -version
cd ~/practicas-aws
python3 -m venv .venv-spark
source .venv-spark/bin/activate
python -m pip install 'pyspark==4.0.1'
export JAVA_HOME="$(dirname "$(dirname "$(readlink -f "$(command -v java)")")")"
export PYSPARK_PYTHON="$(command -v python)"
```

Las primeras órdenes comprueban capacidad; OpenJDK aporta la máquina Java; `.venv-spark` separa Spark de pandas/Jupyter; la versión queda fijada como referencia didáctica. `JAVA_HOME` apunta al Java seleccionado y `PYSPARK_PYTHON` al Python activo. Vuelve a establecer ambas al abrir otra terminal si es necesario.

PySpark 4.0.1 necesita Python 3.9 o superior y Java 17 o posterior. El docente debe ensayar este conjunto en su AMI Ubuntu antes de clase. [Apache Spark: instalación 4.0.1](https://spark.apache.org/docs/4.0.1/api/python/getting_started/install.html).

## 3. Crea el programa de agregación

En VS Code remoto crea `scripts/resumen_spark.py`:

```python
import argparse
from pyspark.sql import SparkSession, functions as F, types as T

parser = argparse.ArgumentParser()
parser.add_argument("entrada")
parser.add_argument("salida")
args = parser.parse_args()
builder = SparkSession.builder.appName("FP-metricas")
if not args.entrada.startswith("s3://"):
    builder = builder.master("local[2]").config("spark.sql.shuffle.partitions", "2")
spark = builder.getOrCreate()
try:
    schema = T.StructType([
        T.StructField("id", T.LongType()),
        T.StructField("fecha", T.StringType()),
        T.StructField("centro", T.StringType()),
        T.StructField("servicio", T.StringType()),
        T.StructField("peticiones", T.LongType()),
        T.StructField("latencia_ms", T.DoubleType()),
    ])
    datos = spark.read.option("header", True).schema(schema).csv(args.entrada)
    print("Filas limpias:", datos.count())
    datos.agg(F.sum("peticiones").alias("peticiones_totales")).show()
    resumen = datos.groupBy("centro").agg(
        F.sum("peticiones").alias("peticiones_totales"),
        F.avg("latencia_ms").alias("latencia_media_ms"),
        F.count("id").alias("registros"),
    )
    resumen.orderBy("centro").show()
    resumen.write.mode("errorifexists").option("header", True).csv(args.salida)
finally:
    spark.stop()
```

El esquema evita una inferencia innecesaria. `groupBy` y `agg` describen transformaciones; `count`, `show` y escritura desencadenan trabajo. La entrada debe ser el CSV **limpio de G11**, no raw. No volvemos a limpiar en este script. [Apache Spark: lectura y escritura CSV](https://spark.apache.org/docs/4.0.1/sql-data-sources-csv.html).

## 4. Ejecuta la ruta local

En Ubuntu, con `.venv-spark` activo:

```bash
cd ~/practicas-aws
spark-submit --driver-memory 1g scripts/resumen_spark.py datos/curated/metricas_limpias.csv resultados/spark-g15-01
```

`spark-submit` inicia el programa; los dos últimos argumentos son entrada y directorio de salida. `--driver-memory` establece memoria Java del driver, no un límite de RAM de toda la instancia. Usa una salida nueva, por ejemplo `spark-g15-02`, para repetir sin sobrescribir.

**Esperado:** 12 filas, 1800 peticiones y los mismos valores por centro que en pandas. Spark genera un **directorio** con archivos `part-…csv` y un marcador `_SUCCESS`, no un único archivo con el nombre del directorio. Examina sus archivos desde VS Code.

> **Si algo falla**  
> `JAVA_GATEWAY_EXITED` requiere revisar Java, JAVA_HOME y memoria; un proceso `Killed` puede indicar recursos insuficientes. Un error de salida existente es deliberado: utiliza una ruta nueva propia. No cambies a S3 desde Spark local esperando que el paquete instalado incluya automáticamente todos los conectores y credenciales; la ruta local usa el archivo descargado.

> **Qué está ocurriendo**  
> Spark puede repartir tareas en particiones incluso cuando trabaja en un solo servidor. La ruta local permite estudiar ese modelo; una ejecución gestionada cambia dónde se ejecutan driver y tareas, y exige permisos y recursos adicionales.

## 5. Ampliación: ejecución gestionada, solo tras ensayo docente

Esta ampliación utiliza un servicio gestionado; no instala otro sistema operativo en la EC2 del alumno. Si está restringido o no encaja con el entorno aprobado, mantén la ruta base y registra «sin ejecución distribuida gestionada».

El docente debe confirmar creación de aplicaciones y trabajos, versión de runtime, rol de ejecución compatible, `PassRole`, permisos de S3/logs y presupuesto. El rol de ejecución del trabajo es distinto de tu perfil EC2 y debe ser asumible por EMR Serverless. [AWS: roles de ejecución](https://docs.aws.amazon.com/emr/latest/EMR-Serverless-UserGuide/security-iam-runtime-role.html).

1. En Ubuntu, carga `source ~/practicas-aws/lab.env` y sube el script propio:

```bash
aws s3 cp ~/practicas-aws/scripts/resumen_spark.py "s3://$BUCKET/scripts/resumen_spark.py" --region "$AWS_REGION"
```

2. Abre **EMR → EMR Serverless** y el Studio existente autorizado. Si requiere crear un Studio no permitido, detente.
3. Crea una aplicación **Spark**, solo batch, con la versión de runtime probada por el docente. El código usa APIs básicas; el runtime gestionado aporta su propia versión de Spark.
4. Desactiva capacidad preinicializada y habilita parada automática. Configura un máximo de capacidad ensayado; como referencia de aula, 2 vCPU, 16 GiB de memoria y 40 GiB de disco, sujeto a límites reales. Si no se admite, no aumentes el máximo a ciegas.
5. En **Submit job**, usa el rol aprobado y ubicación `s3://TU_BUCKET/scripts/resumen_spark.py`.
6. Argumentos: entrada `s3://TU_BUCKET/curated/metricas/metricas_limpias.csv` y salida **nueva y propia** `s3://TU_BUCKET/resultados/spark-g15-01/`. Sustituye TU_BUCKET; no escribas las palabras de marcador.

[AWS: aplicación, envío de trabajo y logs desde consola](https://docs.aws.amazon.com/emr/latest/EMR-Serverless-UserGuide/gs-console.html).

7. En propiedades Spark, aplica el conjunto ensayado por el docente para driver y un executor, sin escalado dinámico. Referencia para validar:

```text
--conf spark.dynamicAllocation.enabled=false --conf spark.executor.instances=1 --conf spark.executor.cores=1 --conf spark.executor.memory=2g --conf spark.driver.cores=1 --conf spark.driver.memory=2g --conf spark.executor.memoryOverhead=1g --conf spark.driver.memoryOverhead=1g --conf spark.sql.shuffle.partitions=2
```

8. Configura logs en un prefijo propio `s3://TU_BUCKET/logs/emr/` si esa opción está habilitada. Envía un solo trabajo.
9. Espera éxito, revisa logs y archivos de salida; comprueba 12/1800 y tres centros.
10. Si falla, registra el código, cancela cualquier ejecución aún activa y revisa permisos/capacidad con el docente antes de reintentar.

La capacidad máxima y preinicializada son ajustes diferentes; hay que validar ambos para controlar consumo. [AWS: capacidad de aplicaciones](https://docs.aws.amazon.com/emr/latest/EMR-Serverless-UserGuide/application-capacity.html).

## 6. Entrega y cierre

Entrega script, comparación y una explicación de dónde se ejecutaron driver y tareas en tu ruta. Con 12 filas no tiene sentido concluir que Spark será más rápido que pandas: el coste de arranque domina.

El programa local llama a `spark.stop()`. En la ruta gestionada cancela trabajos pendientes, detén la aplicación, espera **STOPPED** y bórrala si era exclusivamente de esta práctica. No borres Studios o roles compartidos. Después detén tu EC2 y pulsa End Lab. No confíes solo en la parada automática. [AWS: comportamiento y parada de aplicaciones](https://docs.aws.amazon.com/emr/latest/EMR-Serverless-UserGuide/app-behavior.html).

**Resumen:** has ejecutado un programa Spark y distingues paralelismo local de procesamiento gestionado distribuido. **Reto:** explica el papel de una partición y por qué este dataset no permite medir escalabilidad.
