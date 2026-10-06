# G08 · Amazon S3 como Data Lake básico

**Curso:** Curso de Especialización FP Aprendizaje Automático — Instalación, Despliegue y Explotación de Sistemas  
**Módulo:** Explotación de servicios de procesamiento y analítica de datos  
**Entorno:** Windows 11 → AWS Academy Learner Lab → Ubuntu en EC2  
**Duración orientativa:** 50–60 minutos  
**Requisitos:** G01; región confirmada y permiso para crear buckets y subir objetos.  
**Recursos:** Un bucket privado y un CSV sintético de menos de 2 KB.  
**Resultado:** Dataset raw almacenado y estructura de prefijos preparada para analítica.

## Antes de empezar

1. Inicia el Learner Lab con **Start Lab** y espera a que esté activo.
2. Abre la consola AWS desde el enlace del Lab. Usa **París (`eu-west-3`) solo si está autorizada**, según G01 y las instrucciones actuales. Si se utiliza otra región, mantenla en toda la práctica.
3. Comprueba presupuesto y tiempo restante. Las cifras dependen de tu laboratorio; no se presupone gratuidad. La aparición de un servicio no garantiza permiso para utilizarlo.
4. Sigue el lugar de ejecución indicado: **PowerShell de Windows**, **terminal del Learner Lab** o **terminal Ubuntu de EC2**. No intercambies sus comandos.
5. En bloques con varias órdenes, ejecuta una línea cada vez, excepto los bloques de creación de archivos que se indique pegar completos. No copies los marcadores de Markdown.

> **Importante · Seguridad**  
> No compartas Account ID, UserId, ARN completo, Access Key, Secret Key, Session Token ni archivos privados `.pem`. No subas claves a EC2, S3, repositorios o herramientas de IA. Entrega resultados resumidos y capturas recortadas. Los permisos se conceden mediante los roles previstos por el laboratorio; no los amplíes para eludir una restricción.

## 1. Objetivo y estructura

```text
Windows: metricas_raw.csv → S3 privado
                              ├── raw/metricas/
                              ├── curated/metricas/
                              ├── resultados/
                              └── athena-results/
```

`raw` conserva el original; `curated` contendrá datos limpios; `resultados` guarda informes; `athena-results` contendrá salidas de consultas. Los prefijos no son discos ni carpetas físicas: forman parte de las claves de objetos. S3 cobra por almacenamiento y operaciones según condiciones; la práctica usa un archivo muy pequeño.

## 2. Prepara el dataset en Windows

En el paquete de esta colección tienes **metricas_raw.csv**. Es un dataset sintético, sin personas reales, con 15 registros: 12 válidos, un duplicado y dos problemas de calidad. No sustituye un dataset real del proyecto final.

Si no tienes el archivo, copia este contenido en Bloc de notas, guarda como `metricas_raw.csv`, tipo **Todos los archivos**, UTF-8. Activa extensiones para evitar `.csv.txt`:

```csv
id,fecha,centro,servicio,peticiones,latencia_ms
1,2026-01-10,madrid,inferencia,100,120
2,2026-01-10,madrid,analitica,200,80
3,2026-01-10,sevilla,inferencia,150,150
4,2026-01-10,sevilla,analitica,180,90
5,2026-01-10,valencia,inferencia,120,110
6,2026-01-10,valencia,analitica,160,70
7,2026-01-11,madrid,inferencia,130,100
8,2026-01-11,sevilla,inferencia,140,140
9,2026-01-11,valencia,inferencia,110,130
10,2026-01-11,madrid,analitica,190,85
11,2026-01-11,sevilla,analitica,170,95
12,2026-01-11,valencia,analitica,150,75
12,2026-01-11,valencia,analitica,150,75
13,2026-01-11,madrid,inferencia,50,
14,2026-01-11,sevilla,analitica,-10,100
```

La coma separa columnas y el punto se usaría como separador decimal. Los nombres de ciudad identifican centros ficticios de procesamiento, no regiones AWS.

## 3. Crea un bucket de propósito general

1. En la consola abre **S3 → Buckets → Create bucket**.
2. Selecciona **General purpose / Propósito general**, no Directory bucket ni S3 Tables.
3. Elige la región autorizada de toda la colección.
4. Usa un nombre sin datos personales, por ejemplo `fp-analytics-aula-` seguido de 12 caracteres aleatorios de tu elección, en minúsculas y números. En el espacio de nombres global compartido debe ser único.
5. No incluyas Account ID, nombre completo ni credenciales en el nombre.
6. Conserva **Object Ownership: Bucket owner enforced**, ACL deshabilitadas.
7. Mantén activadas las cuatro opciones de **Block all public access**.
8. Para esta práctica deja versionado deshabilitado y Object Lock sin activar, si el laboratorio lo permite. No alteres un bucket ya existente para ajustarlo.
9. Mantén el cifrado predeterminado **SSE-S3**. No solicites una clave KMS nueva para el ejercicio.
10. Revisa y crea el bucket. Guarda el nombre exacto en tu inventario local.

[AWS: creación de buckets](https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html), [reglas de nombres](https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html) y [bloqueo de acceso público](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html).

> **Si algo falla**  
> Si el nombre está ocupado, cambia únicamente su sufijo. Si CreateBucket está denegado, el docente debe decidir si proporcionará un bucket o prefijo de trabajo existente. No cambies de región sin confirmación ni hagas público un bucket para corregir errores IAM.

## 4. Sube y verifica el original

1. Abre tu bucket y crea una carpeta/prefijo `raw`.
2. Entra en `raw`, crea `metricas` y entra.
3. Pulsa **Upload / Cargar → Add files** y selecciona `metricas_raw.csv`.
4. Confirma la carga sin modificar acceso público.
5. Abre sus propiedades y comprueba la clave `raw/metricas/metricas_raw.csv`.
6. Descárgalo desde la consola y ábrelo en Bloc de notas: encabezado y 15 registros deben coincidir.
7. Crea los prefijos `curated/metricas`, `resultados` y `athena-results` desde el nivel raíz si quieres ver la organización; se podrán crear automáticamente al escribir objetos.

> **Qué está ocurriendo**  
> La descarga en consola usa tu sesión autenticada. Un enlace de objeto abierto de forma anónima puede devolver AccessDenied, aunque tú puedas descargarlo desde la consola. Ese bloqueo es el comportamiento deseado; no necesitas una web pública para analizar S3.

## 5. Entrega, continuidad y limpieza

Registra nombre del bucket localmente, región, clave exacta del objeto y «bloqueo público activado». Entrega un esquema con las capas y explica por qué conservar el original.

Conserva el bucket para G09–G16; S3 sigue existiendo cuando EC2 está detenida. No vacíes un bucket compartido. Cuando el docente dé por terminada la colección, elimina solo los objetos propios; en un bucket exclusivamente tuyo sin versionado, la consola permite vaciarlo y después borrarlo. Verifica el alcance antes de confirmar. Cierra con End Lab.

**Resumen:** has preparado la capa de almacenamiento del análisis. **Siguiente:** G09, acceso a S3 desde EC2 mediante un rol. **Reto:** explica por qué separar resultados de Athena del prefijo raw evita mezclar formatos al consultar.

