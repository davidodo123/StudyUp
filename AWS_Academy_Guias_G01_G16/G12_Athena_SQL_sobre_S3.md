# G12 · Consultas SQL sobre S3 con Amazon Athena

**Curso:** Curso de Especialización FP Aprendizaje Automático — Instalación, Despliegue y Explotación de Sistemas  
**Módulo:** Explotación de servicios de procesamiento y analítica de datos  
**Entorno:** Windows 11 → AWS Academy Learner Lab → Ubuntu en EC2  
**Duración orientativa:** 75–90 minutos  
**Requisitos:** G08; Athena y escritura en Glue Data Catalog autorizados; bucket de resultados accesible.  
**Recursos:** Athena, catálogo Glue y bucket existente; EC2 puede estar detenida.  
**Resultado:** Tabla externa raw, vista limpia y consulta SQL con resultados contrastados.

## Antes de empezar

1. Inicia el Learner Lab con **Start Lab** y espera a que esté activo.
2. Abre la consola AWS desde el enlace del Lab. Usa **París (`eu-west-3`) solo si está autorizada**, según G01 y las instrucciones actuales. Si se utiliza otra región, mantenla en toda la práctica.
3. Comprueba presupuesto y tiempo restante. Las cifras dependen de tu laboratorio; no se presupone gratuidad. La aparición de un servicio no garantiza permiso para utilizarlo.
4. Sigue el lugar de ejecución indicado: **PowerShell de Windows**, **terminal del Learner Lab** o **terminal Ubuntu de EC2**. No intercambies sus comandos.
5. En bloques con varias órdenes, ejecuta una línea cada vez, excepto los bloques de creación de archivos que se indique pegar completos. No copies los marcadores de Markdown.

> **Importante · Seguridad**  
> No compartas Account ID, UserId, ARN completo, Access Key, Secret Key, Session Token ni archivos privados `.pem`. No subas claves a EC2, S3, repositorios o herramientas de IA. Entrega resultados resumidos y capturas recortadas. Los permisos se conceden mediante los roles previstos por el laboratorio; no los amplíes para eludir una restricción.

## 1. Puerta de entrada y alternativa

El docente debe haber comprobado **ejecución de consultas**, acceso a los datos/resultados en S3 y creación de bases, tablas y vistas en el catálogo. Una tabla creada desde Athena también utiliza el catálogo Glue: no evita restricciones de Glue o Lake Formation.

Si esas operaciones están denegadas, registra cuál y utiliza G11 para obtener las mismas métricas. No declares que has ejecutado Athena si solo has analizado con pandas.

```text
Athena SQL → metadatos Glue + CSV privado S3 → resultados en otro prefijo S3
```

## 2. Configura el editor y la salida

1. En consola abre **Athena** en la región autorizada.
2. Abre **Query editor / Editor de consultas** y selecciona el workgroup aprobado por el docente. No crees uno para eludir restricciones.
3. Utiliza el catálogo **AwsDataCatalog**.
4. En ajustes de consultas, establece salida en `s3://NOMBRE_REAL_DEL_BUCKET/athena-results/`, salvo que el workgroup imponga otra ubicación autorizada.
5. Mantén el cifrado compatible con el bucket; no solicites nuevas claves KMS.
6. Guarda y registra la ubicación efectiva.

La salida puede estar impuesta por el workgroup y requiere permisos S3. [AWS: ubicación de resultados de Athena](https://docs.aws.amazon.com/athena/latest/ug/query-results-specify-location.html).

## 3. Crea una base de metadatos

En el **editor SQL de Athena**, no en PowerShell ni Ubuntu, ejecuta cada sentencia por separado:

```sql
CREATE DATABASE IF NOT EXISTS fp_analytics;
```

`IF NOT EXISTS` evita error si tu base ya existe. Selecciónala en el panel de datos. En una cuenta compartida utiliza una base propia con el sufijo acordado y cambia todas las referencias de esta guía. [AWS: bases de datos en Athena](https://docs.aws.amazon.com/athena/latest/ug/creating-databases.html).

## 4. Define la tabla raw

Sustituye `NOMBRE_REAL_DEL_BUCKET` antes de ejecutar:

```sql
CREATE EXTERNAL TABLE IF NOT EXISTS fp_analytics.metricas_raw (
    id string,
    fecha string,
    centro string,
    servicio string,
    peticiones string,
    latencia_ms string
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES ('separatorChar' = ',', 'quoteChar' = '"')
STORED AS TEXTFILE
LOCATION 's3://NOMBRE_REAL_DEL_BUCKET/raw/metricas/'
TBLPROPERTIES ('skip.header.line.count' = '1');
```

`EXTERNAL` describe archivos existentes; no los importa a una base física. Definimos columnas como texto para inspeccionar valores defectuosos sin fallar al leer. El SerDe interpreta CSV y `skip.header.line.count` omite la cabecera. La ubicación es el prefijo, no una mezcla con resultados. [AWS: OpenCSVSerDe](https://docs.aws.amazon.com/athena/latest/ug/csv-serde.html).

> **Importante**  
> `IF NOT EXISTS` no corrige una tabla creada antes con otro esquema o ubicación. Si ya existe, revisa su definición y corrige solo una tabla propia con el docente. No subas otro formato al mismo prefijo.

Comprueba:

```sql
SELECT COUNT(*) AS filas_raw FROM fp_analytics.metricas_raw;
```

**Esperado:** 15. Si ves 16, revisa cabecera; si ves 30, busca copias del CSV en el prefijo. No «arregles» el conteo cambiando el resultado esperado.

## 5. Crea una vista para los datos válidos

```sql
CREATE OR REPLACE VIEW fp_analytics.metricas_validas AS
WITH tipadas AS (
    SELECT DISTINCT
        TRY_CAST(id AS BIGINT) AS id,
        TRY_CAST(fecha AS DATE) AS fecha,
        centro,
        servicio,
        TRY_CAST(peticiones AS BIGINT) AS peticiones,
        TRY_CAST(latencia_ms AS DOUBLE) AS latencia_ms
    FROM fp_analytics.metricas_raw
)
SELECT * FROM tipadas
WHERE id > 0
  AND fecha IS NOT NULL
  AND centro IN ('madrid', 'sevilla', 'valencia')
  AND servicio IN ('inferencia', 'analitica')
  AND peticiones >= 0
  AND latencia_ms >= 0;
```

`TRY_CAST` convierte tipos y devuelve NULL cuando no puede; `DISTINCT` quita registros iguales tras convertir; las condiciones retienen los válidos. Para **este dataset**, produce lo mismo que G11. En datos generales, deduplicar después de convertir puede fusionar representaciones que no eran idénticas en raw; documenta esa diferencia si amplías la práctica.

La vista no escribe un nuevo CSV: conserva la transformación como una consulta reutilizable.

## 6. Consulta y compara

```sql
SELECT COUNT(*) AS filas_limpias, SUM(peticiones) AS peticiones_totales
FROM fp_analytics.metricas_validas;
```

**Esperado:** 12 y 1800.

```sql
SELECT centro,
       SUM(peticiones) AS peticiones_totales,
       ROUND(AVG(latencia_ms), 2) AS latencia_media_ms,
       COUNT(*) AS registros
FROM fp_analytics.metricas_validas
GROUP BY centro
ORDER BY centro;
```

Compara con G11: madrid 620/96,25/4; sevilla 640/118,75/4; valencia 540/96,25/4. Descarga el resultado desde el editor y guarda la SQL localmente, sin ARN ni datos de sesión.

> **Qué está ocurriendo**  
> Athena lee S3 a través de una definición del catálogo. La vista conserva reglas SQL y las aplica sobre raw, mientras que el CSV curated de Python ya contiene los registros transformados. Ambos deben coincidir porque utilizan la misma entrada de referencia.

## 7. Coste y diagnóstico

Registra bytes escaneados y duración que muestre Athena. El coste de consulta depende del modelo del workgroup y del procesamiento; los mínimos de facturación pueden ser superiores al tamaño del CSV. `LIMIT` limita resultados, no garantiza limitar bytes escaneados. No repitas consultas en bucle. [AWS: precios de Athena](https://aws.amazon.com/athena/pricing/).

> **Si algo falla**  
> Un error de permisos puede corresponder a Athena, S3, Glue, Lake Formation o KMS. Registra el código sin compartir el mensaje íntegro. Si falta salida S3, revisa el workgroup. Si los números no coinciden, revisa archivos del prefijo, cabecera y conversiones antes de concluir que el motor calcula mal.

## 8. Entrega, cierre y resumen

Entrega SQL, resultado y comparación con pandas; anota servicio denegado si corresponde. Conserva tabla y vista para G14. No hay EC2 necesaria para las consultas: mantenla detenida si no se usa. Guarda evidencias y pulsa End Lab.

Al terminar la colección, elimina vista y tabla **propias**, después la base si queda vacía. Los metadatos externos no borran automáticamente los CSV de S3: su limpieza se realiza aparte.

**Resumen:** has separado almacenamiento, metadatos y cómputo SQL. **Reto:** consulta las peticiones por servicio y comprueba 750 y 1050.
