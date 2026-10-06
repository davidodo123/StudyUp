# G13 · Catálogo de datos con AWS Glue y un crawler

**Curso:** Curso de Especialización FP Aprendizaje Automático — Instalación, Despliegue y Explotación de Sistemas  
**Módulo:** Explotación de servicios de procesamiento y analítica de datos  
**Entorno:** Windows 11 → AWS Academy Learner Lab → Ubuntu en EC2  
**Duración orientativa:** 60–90 minutos  
**Requisitos:** G11 con CSV limpio en S3; permisos de catálogo y crawler; rol compatible confirmado.  
**Recursos:** Glue Data Catalog y un crawler bajo demanda; sin Glue Jobs.  
**Resultado:** Tabla catalogada y esquema contrastado con los datos reales.

## Antes de empezar

1. Inicia el Learner Lab con **Start Lab** y espera a que esté activo.
2. Abre la consola AWS desde el enlace del Lab. Usa **París (`eu-west-3`) solo si está autorizada**, según G01 y las instrucciones actuales. Si se utiliza otra región, mantenla en toda la práctica.
3. Comprueba presupuesto y tiempo restante. Las cifras dependen de tu laboratorio; no se presupone gratuidad. La aparición de un servicio no garantiza permiso para utilizarlo.
4. Sigue el lugar de ejecución indicado: **PowerShell de Windows**, **terminal del Learner Lab** o **terminal Ubuntu de EC2**. No intercambies sus comandos.
5. En bloques con varias órdenes, ejecuta una línea cada vez, excepto los bloques de creación de archivos que se indique pegar completos. No copies los marcadores de Markdown.

> **Importante · Seguridad**  
> No compartas Account ID, UserId, ARN completo, Access Key, Secret Key, Session Token ni archivos privados `.pem`. No subas claves a EC2, S3, repositorios o herramientas de IA. Entrega resultados resumidos y capturas recortadas. Los permisos se conceden mediante los roles previstos por el laboratorio; no los amplíes para eludir una restricción.

## 1. Objetivo y condición de uso

```text
CSV limpio S3 → crawler Glue → metadatos Data Catalog → Athena
```

Un crawler descubre metadatos; no limpia el dataset ni sustituye el procesador de G11. Data Catalog y ejecución de crawlers son operaciones diferentes. Puede estar permitida la primera y denegada la segunda. [AWS: funcionamiento de crawlers](https://docs.aws.amazon.com/glue/latest/dg/add-crawler.html).

Antes de empezar, el docente debe confirmar un rol existente que Glue pueda asumir, permiso del alumno para pasarlo al servicio y acceso del rol a S3, catálogo y logs. Que exista `LabRole` no garantiza que su política de confianza permita Glue. [AWS: requisitos de crawler](https://docs.aws.amazon.com/glue/latest/dg/crawler-prereqs.html).

## 2. Comprueba el prefijo de origen

En S3 abre exclusivamente `curated/metricas/`. Debe contener `metricas_limpias.csv`, con seis columnas y 12 registros, y ningún resumen o JSON de otro esquema. Si G11 no subió la salida, completa ese paso antes de crear el crawler.

> **Importante**  
> No apuntes el crawler al bucket completo. Evita mezclar raw, curated y resultados; el origen de esta tabla es un único prefijo homogéneo.

## 3. Crea la base de catálogo

1. Abre **AWS Glue** en la misma región.
2. Busca **Data Catalog → Databases** y pulsa **Add database**.
3. Nombre: `fp_catalogo`, o la base individual acordada en una cuenta compartida.
4. Crea la base. No crees conexiones JDBC, jobs ni un entorno de desarrollo.

Si ya existe y es tuya, reutilízala. Una base del catálogo agrupa definiciones de tablas, no contiene copias de los CSV.

## 4. Configura el crawler

En **Crawlers → Create crawler**, realiza los pasos del asistente:

1. Nombre propio: `fp-metricas-crawler`.
2. Origen **S3**, en esta cuenta, ruta `s3://NOMBRE_REAL_DEL_BUCKET/curated/metricas/`.
3. Utiliza el rol IAM existente aprobado; no elijas crear un nuevo rol automáticamente.
4. Salida: base `fp_catalogo`.
5. Prefijo de tablas: `g13_`.
6. Frecuencia: **On demand / Bajo demanda**, sin programación periódica.
7. Revisa origen, rol y destino; crea el crawler.

Si un paso no aparece con el mismo nombre, busca la configuración equivalente en las instrucciones de tu edición. [AWS: configuración de un crawler](https://docs.aws.amazon.com/glue/latest/dg/define-crawler.html).

## 5. Ejecuta una vez y revisa

1. Selecciona el crawler propio y pulsa **Run**.
2. Espera a que termine; revisa el resultado de la última ejecución, no solo el estado Ready.
3. En la base abre las tablas creadas.
4. Anota el **nombre real**: puede parecerse a `g13_metricas`, pero la inferencia no garantiza ese nombre.
5. Comprueba ubicación S3, seis columnas, nombres y tipos.
6. Verifica cómo se interpreta la cabecera; revisa la propiedad `skip.header.line.count = 1` si es necesaria para esa definición CSV.

Con un CSV pequeño, la inferencia puede producir nombres `col0`, interpretar mal la cabecera o elegir tipos que no te convienen. No continúes suponiendo que siempre acertará. El docente puede ensayar un clasificador CSV con cabecera explícita o validar una corrección manual de **la tabla propia**, manteniendo orden y SerDe coherentes. [AWS: CSV y cabeceras en Glue/Athena](https://docs.aws.amazon.com/athena/latest/ug/schema-csv.html).

## 6. Valida el catálogo desde Athena

Si Athena también está autorizado, selecciona `AwsDataCatalog` y tu base. En el siguiente SQL sustituye `TABLA_REAL` por el nombre anotado:

```sql
SELECT COUNT(*) AS filas FROM fp_catalogo.TABLA_REAL;
```

**Esperado:** 12. Si necesitas comprobar conversión numérica:

```sql
SELECT SUM(TRY_CAST(peticiones AS BIGINT)) AS total
FROM fp_catalogo.TABLA_REAL;
```

**Esperado:** 1800. Si los campos fueron inferidos con otros nombres, revisa la definición antes de adaptar consultas.

> **Qué está ocurriendo**  
> La tabla apunta al mismo objeto de S3 que produjo Python. Consultarla no crea una copia del dataset en Glue. [AWS: consulta del catálogo Glue](https://docs.aws.amazon.com/athena/latest/ug/querying-glue-catalog.html).

## 7. Si el crawler está restringido

Registra «crawler no ejecutable» y el paso concreto. Si Athena y la escritura del catálogo sí funcionan, conserva la ruta manual de G12; para datos limpios puedes crear una segunda tabla manual copiando el DDL, cambiando nombre a `metricas_curated` y ubicación a `curated/metricas/`. No uses una tabla raw para afirmar que se ha catalogado curated. Si tampoco se permite el catálogo, continúa con pandas y registra la alternativa.

> **Si algo falla**  
> Revisa la última ejecución del crawler y su error, origen exacto, confianza del rol y permisos de S3/catálogo. No conviertas el bucket en público. Si hay una denegación del laboratorio, utiliza la alternativa autorizada del apartado 7 y registra que no se ejecutó el crawler.

## 8. Entrega, cierre y resumen

Entrega esquema, resultado de última ejecución y revisión de columnas. Los crawlers consumen presupuesto por su ejecución y pueden tener mínimos de facturación; no programes repeticiones automáticas.

Conserva la tabla para G14. No dejes un crawler en ejecución al acabar: espera su finalización o usa Stop si procede. Elimina su programación si se activó por error, y pulsa End Lab. Al finalizar la colección elimina crawler y metadatos propios; no borres roles compartidos.

**Resumen:** descubrimiento automático y validación de esquema son pasos distintos. **Reto:** explica por qué un crawler sobre datos raw no elimina el duplicado ni la fila negativa.
