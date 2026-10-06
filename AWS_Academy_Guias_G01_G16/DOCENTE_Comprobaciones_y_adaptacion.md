# Preparación docente de la colección G01–G16

## 1. Qué está comprobado y qué falta

La información aportada por el docente confirma una identidad de sesión `assumed-role/voclabs`, región guardada `us-east-1`, presencia de `eu-west-3` en la consulta de regiones y AWS CLI `2.1.11` en la terminal observada. No confirma que se puedan crear recursos en París, lanzar una AMI concreta o utilizar los servicios de analítica.

Las guías se han redactado contrastando documentación oficial de AWS, Microsoft, Python, Apache Spark, Jupyter y UCI. **Una revisión documental o una validación local de código no sustituye el ensayo en el Learner Lab del alumnado.** Antes de clase, completa esta ficha con una cuenta de alumno y la misma edición del Lab.

## 2. Ficha maestra del aula

```text
Fecha del ensayo:
Edición/nombre del Learner Lab:
Cuenta por alumno o compartida (sin Account ID):
Región autorizada elegida:
Regiones expresamente prohibidas:
Presupuesto y duración de sesión mostrados:
VPC/subred prevista (IDs solo en inventario privado):
Conectividad TCP/22 desde la red real del centro:
AMI Ubuntu LTS probada / arquitectura / AMI ID privado:
Tipo de instancia permitido para SSH:
Tipo/capacidad probada para VS Code y pandas:
Tipo/capacidad probada para Spark, si se utilizará:
Disco EBS permitido y política de borrado:
Creación/descarga RSA PEM:
Perfil IAM de EC2 asignable:
Acceso S3 desde EC2: ListBucket / GetObject / PutObject:
Athena: workgroup, salida efectiva, consultas y creación de vista:
Glue: base/tabla permitidas:
Glue crawler: rol asumible, PassRole y ejecución permitida:
EMR Serverless: no utilizado / ensayado con ficha específica:
Versiones: Ubuntu / OpenSSH / VS Code / Python / AWS CLI / bibliotecas:
Ruta alternativa elegida si un servicio está restringido:
Limpieza verificada:
```

No distribuyas esta ficha con identificadores completos de cuenta, ARN ni secretos. Para alumnado prepara una ficha simplificada con nombres y parámetros de trabajo.

## 3. Ensayo por etapas, con criterios de aprobación

| Etapa | Prueba real | Aprobación antes de impartir |
|---|---|---|
| G01 | Acceso web, STS y lectura en la región elegida | Región e identidad operativas; restricciones registradas |
| G02–G03 | Lectura de red, grupo propio, par RSA y descarga | Ruta al gateway, origen correcto y `.pem` protegido |
| G04–G05 | Lanzar una sola Ubuntu y conectar desde Windows del centro | AMI/tipo/red válidos; huella verificada; SSH funcional |
| G06–G07 | Abrir carpeta remota y página temporal | VS Code instala su servidor; HTTP funciona desde Mi IP y se cierra |
| G08–G10 | Bucket privado, rol en EC2, descarga CLI/Boto3 | Sin credenciales copiadas; operaciones exactas permitidas |
| G11 | Ejecutar procesador de métricas y subir salidas | 15 raw, 1 duplicado, 2 inválidas, 12 limpias, 1800 peticiones |
| G12 | Base, tabla, vista y consultas sobre dataset pequeño | Resultado válido y salida efectiva controlada |
| G13–G14 | Crawler sobre curated y contraste en Athena | Rol/trust/PassRole correctos y esquema revisado |
| G15 | Spark local y, si procede, trabajo gestionado mínimo | Memoria y espacio suficientes; 12/1800; cierre probado |
| G16 | Descargar Iris, transformar y repetir | 150 válidas, 50 por clase y hash registrado |

Las comprobaciones de lectura no prueban permisos de creación. El ensayo de creación es deliberado y puede consumir presupuesto: planifica uno por etapa, verifica qué se creó tras un fallo y limpia los recursos de prueba. No pruebes todos los servicios a la vez.

## 4. Ajustes que debes fijar antes de repartir las guías

1. **Región:** confirma París o cambia la referencia por una región autorizada en todos los comandos y recursos. No selecciones una región solo porque aparece en `describe-regions`.
2. **Ubuntu:** utiliza una AMI LTS oficial, de arquitectura compatible, que hayas lanzado con éxito. G04 propone 24.04 LTS y contempla 22.04 LTS validada. No se utilizará Amazon Linux.
3. **Capacidad:** una micro puede bastar para SSH, pero no se presume adecuada para VS Code, pandas/Jupyter o Spark. Para Spark local se propone al menos 4 GiB de RAM, sujeto al tipo permitido y presupuesto. No obligues a ampliar si el Lab no lo permite.
4. **Perfil EC2:** confirma el perfil existente asignable, su política y la operación `PassRole`. No presupongas nombres ni permisos a partir de que aparezca `LabRole`.
5. **Versiones Python:** ensaya en un entorno virtual y registra `pip freeze`. Puedes entregar un requirements fijado después del ensayo. Spark mantiene entorno separado y versión de referencia 4.0.1, con Java 17.
6. **Nombres:** en cuenta compartida asigna sufijos y prefijos individuales para EC2, grupo, par, bucket, bases, tablas y crawlers. Adapta las referencias SQL y comandos conjuntamente.
7. **Huella SSH:** comprueba que los logs de arranque permiten obtenerla o prepara otra vía independiente fiable. No enseñes a aceptar cualquier huella ni a ignorar cambios de identidad.
8. **Red del centro:** prueba TCP/22, descargas de paquetes y componentes de VS Code desde la red que se usará en clase. Una prueba desde tu domicilio no confirma esa conectividad.

## 5. Condiciones especiales de analítica

Athena crea y utiliza metadatos del catálogo Glue; el DDL manual no elude restricciones del catálogo o Lake Formation. Un rol que funciona en EC2 no implica que Glue pueda asumirlo. Verifica por separado la confianza del rol, los permisos del servicio y los del usuario que lo pasa.

Ensaya el crawler sobre el pequeño CSV antes de clase: confirma nombres de columnas, tipos y cabecera. Si la inferencia no es estable, prepara un clasificador CSV con cabecera explícita o usa la ruta manual de las guías. No distribuyas un nombre de tabla inferido sin haberlo comprobado.

Para EMR Serverless, registra runtime/release, Studio autorizado, rol de ejecución, capacidad máxima, preinicialización desactivada, propiedades Spark, logs y resultado de un trabajo mínimo. Si no está permitido o exige crear recursos IAM no disponibles, omite la ampliación. Spark local enseña la API; no acredita ejecución en varias máquinas.

Referencias: [roles EC2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/iam-roles-for-amazon-ec2.html), [requisitos de crawler](https://docs.aws.amazon.com/glue/latest/dg/crawler-prereqs.html), [roles de EMR Serverless](https://docs.aws.amazon.com/emr/latest/EMR-Serverless-UserGuide/security-iam-runtime-role.html).

## 6. Cierre y preservación de entregas

Comprueba qué persiste en tu edición tras End Lab y qué servicios se detienen. No enseñes que End Lab elimina todos los recursos o garantiza cero consumo posterior. Detener EC2 conserva EBS; los archivos de S3 y metadatos requieren gestión propia.

Conserva recursos entre guías solo cuando son necesarios. Al finalizar, verifica descargas antes de terminar EC2 o vaciar buckets. Nunca elimines roles, VPC, subredes, Studios o bases compartidos al limpiar prácticas individuales. Si una denegación impide limpiar un recurso propio, registra la incidencia para gestionarla desde el entorno autorizado del docente.

## 7. Evaluación y accesibilidad

Evalúa las operaciones realmente habilitadas. Acepta una incidencia bien registrada cuando una restricción impide el ejercicio, y aplica la alternativa prevista. Solicita evidencias recortadas, sin secretos ni identificadores completos. No pidas al alumnado subir sus `.pem` para demostrar el acceso.

Antes de la primera sesión, proporciona el índice, las guías autorizadas, el CSV de referencia y las versiones/valores específicos del aula. Los programas copiados en `apoyo_scripts` reproducen los bloques de las guías, pero siguen requiriendo su configuración y rutas indicadas.

## 8. Validación realizada al preparar el material

El 5 de octubre de 2026 se comprobaron los 16 archivos de guía, su codificación, los bloques de código y los enlaces internos. Todos los bloques Python pasan análisis de sintaxis y los 11 bloques PowerShell pasan el analizador de PowerShell sin errores; esto no equivale a ejecutar sus acciones contra AWS o Windows.

Se ejecutaron los dos programas de transformación en un entorno local con pandas 3.0.1 y NumPy 2.2.6:

- **Métricas:** 15 originales, 1 duplicado, 2 inválidas, 12 limpias y 1.800 peticiones; sumas por centro 620/640/540 y medias 96,25/118,75/96,25.
- **Iris:** descarga del ZIP oficial de UCI, selección del archivo `iris.data`, 150 filas válidas y 50 por clase; procedencia y hashes generados correctamente.

La ejecución local se realizó en Windows y valida la transformación de datos. Quedan pendientes el ensayo de instalación en Ubuntu, las operaciones AWS, la autenticación SSH real, VS Code remoto, consultas Athena, crawler Glue y ejecución Spark/EMR en el laboratorio del aula. No se ha accedido a vuestra cuenta AWS ni se han creado recursos en ella.
