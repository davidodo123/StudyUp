# G14 · Pipeline S3 → Python → Glue → Athena

**Curso:** Curso de Especialización FP Aprendizaje Automático — Instalación, Despliegue y Explotación de Sistemas  
**Módulo:** Explotación de servicios de procesamiento y analítica de datos  
**Entorno:** Windows 11 → AWS Academy Learner Lab → Ubuntu en EC2  
**Duración orientativa:** 75–90 minutos  
**Requisitos:** G08–G13 o alternativas documentadas; reglas de calidad y tabla curated verificadas.  
**Recursos:** EC2 existente para transformación, S3, catálogo y Athena si están autorizados.  
**Resultado:** Flujo reproducible con evidencias de calidad y comparación de resultados.

## Antes de empezar

1. Inicia el Learner Lab con **Start Lab** y espera a que esté activo.
2. Abre la consola AWS desde el enlace del Lab. Usa **París (`eu-west-3`) solo si está autorizada**, según G01 y las instrucciones actuales. Si se utiliza otra región, mantenla en toda la práctica.
3. Comprueba presupuesto y tiempo restante. Las cifras dependen de tu laboratorio; no se presupone gratuidad. La aparición de un servicio no garantiza permiso para utilizarlo.
4. Sigue el lugar de ejecución indicado: **PowerShell de Windows**, **terminal del Learner Lab** o **terminal Ubuntu de EC2**. No intercambies sus comandos.
5. En bloques con varias órdenes, ejecuta una línea cada vez, excepto los bloques de creación de archivos que se indique pegar completos. No copies los marcadores de Markdown.

> **Importante · Seguridad**  
> No compartas Account ID, UserId, ARN completo, Access Key, Secret Key, Session Token ni archivos privados `.pem`. No subas claves a EC2, S3, repositorios o herramientas de IA. Entrega resultados resumidos y capturas recortadas. Los permisos se conceden mediante los roles previstos por el laboratorio; no los amplíes para eludir una restricción.

## 1. Objetivo y rutas posibles

```text
raw S3 → Python en Ubuntu → curated S3 → catálogo Glue → consulta Athena → informe
```

El título incorpora Python porque aquí la transformación ocurre en EC2. No ejecutaremos un Glue Job: un crawler solo descubre metadatos. Mantendrás la misma definición de métricas y registrarás qué parte del flujo se ha ejecutado realmente.

| Permisos disponibles | Ruta de la práctica |
|---|---|
| Crawler, catálogo y Athena | Ruta completa con descubrimiento automático |
| Catálogo y Athena, sin crawler | Tabla manual curated y consulta SQL |
| Solo EC2/S3 | Transformación y resumen de G11; catálogo/SQL pendientes |

## 2. Revisa el contrato de datos

Antes de ejecutar, anota seis columnas, formato CSV, coma, cabecera, fecha ISO, reglas de calidad y rutas raw/curated. Conserva `raw/metricas/metricas_raw.csv` sin modificar. No mezcles resúmenes con registros originales.

**Contrato esperado:** cada fila limpia describe un centro y servicio en una fecha; la suma de peticiones y la media por registro se calculan con la misma definición de G11.

## 3. Repite la transformación de forma controlada

En **Ubuntu EC2**, una vez iniciada:

```bash
cd ~/practicas-aws
source .venv/bin/activate
source lab.env
python scripts/descargar_s3.py
python scripts/procesar.py
```

La primera ejecución recupera el original de S3 y la segunda reconstruye salidas locales. Detente si el informe no indica **15 → 12**, un duplicado y dos inválidas.

Después publica:

```bash
aws s3 cp datos/curated/metricas_limpias.csv "s3://$BUCKET/curated/metricas/metricas_limpias.csv" --region "$AWS_REGION"
aws s3 cp resultados/calidad.json "s3://$BUCKET/resultados/calidad.json" --region "$AWS_REGION"
aws s3 cp resultados/resumen_centros.csv "s3://$BUCKET/resultados/resumen_centros.csv" --region "$AWS_REGION"
```

Estos comandos reemplazan exclusivamente las tres claves propias previstas. Repetirlos con la misma entrada debe dar el mismo resultado; no elimina otros objetos que se hubieran añadido por error al prefijo. Comprueba que curated contiene solo el dataset previsto.

## 4. Actualiza o verifica metadatos

Si hay crawler autorizado, ejecútalo una vez y valida su última ejecución como en G13. Si el esquema no ha cambiado, los metadatos existentes ya pueden permitir leer el objeto reemplazado; no programes el crawler en cada consulta.

Si usas tabla manual, confirma que su ubicación es **curated**, no raw. El catálogo describe el esquema; no conserva una instantánea de los datos por sí solo. Guarda fecha de la ejecución y versión del programa para documentar qué resultado has generado.

## 5. Consulta datos limpios

En **Athena**, cambia `TABLA_CURATED_REAL` por la tabla de G13 o la tabla manual alternativa. Cambia la base si acordaste otro nombre:

```sql
SELECT COUNT(*) AS filas,
       SUM(TRY_CAST(peticiones AS BIGINT)) AS peticiones_totales
FROM fp_catalogo.TABLA_CURATED_REAL;
```

**Esperado:** 12 y 1800. Para una tabla manual que esté en `fp_analytics`, cambia también el nombre de base.

```sql
SELECT centro,
       SUM(TRY_CAST(peticiones AS BIGINT)) AS peticiones_totales,
       ROUND(AVG(TRY_CAST(latencia_ms AS DOUBLE)), 2) AS latencia_media_ms,
       COUNT(*) AS registros
FROM fp_catalogo.TABLA_CURATED_REAL
GROUP BY centro
ORDER BY centro;
```

**Esperado:** los mismos tres centros y valores de G11. Estas consultas leen curated; no vuelven a limpiar raw. Si ves otra cuenta de filas, revisa ubicación, cabeceras y objetos del prefijo.

> **Importante**  
> Para comprobar una modificación reciente de S3, desactiva la reutilización de resultados de consultas en el editor si está habilitada. Revisa la ubicación efectiva de salida del workgroup. No atribuyas una respuesta reutilizada a una nueva lectura de los objetos. [AWS: reutilización de resultados](https://docs.aws.amazon.com/athena/latest/ug/reusing-query-results.html).

## 6. Contrasta y registra trazabilidad

Completa una tabla local:

| Etapa | Entrada | Salida | Evidencia |
|---|---|---|---|
| Descarga | raw S3 | CSV local | 15 registros |
| Calidad | CSV local | curated y calidad.json | 1 duplicado, 2 inválidas, 12 limpias |
| Carga | curated local | curated S3 | objeto exacto |
| Catálogo | prefijo curated | tabla | esquema y ubicación |
| Consulta | tabla curated | resumen SQL | 12 filas, 1800 peticiones |

Si una etapa fue sustituida o no autorizada, escríbelo en su fila. No uses capturas de un entorno ajeno como evidencia de ejecución.

> **Qué está ocurriendo**  
> Cada etapa tiene una entrada y una evidencia propia. Cuando comparas pandas y SQL no comparas solo dos programas: verificas también que ambos han leído la versión y el esquema correctos.

## 7. Incidencias y repetición

Si pandas y Athena discrepan, compara primero entradas y reglas; revisa archivos extra, duplicados, cabeceras y tipos. Las medias deben ser por registro en ambos. Si no hay permisos de catálogo o consulta, conserva el informe de Python y el registro de la denegación.

> **Si algo falla**  
> Localiza la primera etapa cuya evidencia difiere de la esperada. Corrige esa etapa y vuelve a comprobar las siguientes, en vez de recrear toda la infraestructura. Una denegación debe quedar en la trazabilidad junto a la ruta alternativa.

**Reto:** repite el pipeline sin cambiar la entrada y verifica que los conteos y métricas no varían. No necesitas lanzar otra instancia ni crear otro bucket.

## 8. Entrega y cierre

Entrega scripts, SQL, tabla de trazabilidad y un breve informe de comparación. Conserva el entorno para el proyecto final. Para terminar, cierra procesos de práctica, espera el crawler si sigue activo, detén EC2 y pulsa End Lab. Los objetos de S3 y metadatos persisten conforme al Lab y deben limpiarse al finalizar el curso.

**Resumen:** has integrado almacenamiento, transformación, catálogo y explotación; sabes demostrar cada etapa y explicar las alternativas.
