# Colección de guías tutorizadas AWS Academy Learner Lab

**Curso:** Curso de Especialización FP Aprendizaje Automático — Instalación, Despliegue y Explotación de Sistemas.  
**Módulo:** Explotación de servicios de procesamiento y analítica de datos.  
**Base común:** Windows 11, Ubuntu en EC2, región autorizada; París (`eu-west-3`) como referencia condicionada.

## Cómo utilizar la colección

Sigue el orden G01–G16. Cada guía especifica dónde ejecutar comandos, explica su función, incluye comprobaciones y termina con entrega y cierre. Los tiempos son orientativos y no incluyen esperas por incidencias del laboratorio.

La numeración conserva el índice original: G02 prepara la red, G03 las claves y G04 la instancia. Así cada elemento se comprueba antes del lanzamiento. G01 se mantiene tal como se entregó.

**Antes de distribuir al alumnado**, el docente debe completar [las comprobaciones de su Learner Lab](DOCENTE_Comprobaciones_y_adaptacion.md). Esta colección no declara que EC2, perfiles IAM, Athena, Glue o EMR hayan sido ensayados en la cuenta de tu centro. Las restricciones específicas siguen pendientes de comprobación práctica.

## Bloque A · Acceso y entorno de trabajo

| Guía | Tiempo | Resultado |
|---|---|---|
| [G01 · Primeros pasos](G01_Primeros_pasos_AWS_Academy_Learner_Lab.md) | 45–60 min | Acceso, identidad temporal y región comprobados |
| [G02 · Red y configuración básica](G02_Red_y_configuracion_basica.md) | 45–60 min | VPC/subred pública identificadas y grupo SSH propio |
| [G03 · Claves SSH en Windows](G03_Claves_SSH_en_Windows_11.md) | 40–50 min | `.pem` creado, almacenado y protegido |
| [G04 · EC2 Ubuntu](G04_EC2_Ubuntu.md) | 60–75 min | Una instancia Ubuntu reutilizable |
| [G05 · Acceso SSH](G05_SSH_desde_Windows_11.md) | 45–60 min | Conexión autenticada desde PowerShell |
| [G06 · VS Code Remote - SSH](G06_VS_Code_Remote_SSH.md) | 45–60 min | Edición y terminal remotas |
| [G07 · Servicio web](G07_Servicio_web_en_Ubuntu.md) | 45–60 min | Página accesible por un puerto temporal restringido |

## Bloque B · Procesamiento y explotación

| Guía | Tiempo | Resultado |
|---|---|---|
| [G08 · S3 como Data Lake](G08_S3_Data_Lake_basico.md) | 50–60 min | Dataset raw privado y estructura de capas |
| [G09 · AWS CLI desde EC2](G09_AWS_CLI_desde_EC2.md) | 60–75 min | Acceso a S3 mediante perfil IAM |
| [G10 · Python, Boto3 y S3](G10_Python_Boto3_S3.md) | 60–75 min | Descarga programática autenticada |
| [G11 · pandas y Jupyter](G11_Procesamiento_Pandas_Jupyter.md) | 90–120 min | Calidad, dataset limpio y métricas |
| [G12 · Athena SQL](G12_Athena_SQL_sobre_S3.md) | 75–90 min | Tabla externa, vista válida y consultas |
| [G13 · Glue Data Catalog y crawler](G13_Glue_Data_Catalog_y_Crawler.md) | 60–90 min | Esquema descubierto y verificado |
| [G14 · Pipeline](G14_Pipeline_S3_Glue_Athena.md) | 75–90 min | Flujo reproducible y comparación pandas/SQL |
| [G15 · Spark](G15_Spark_y_procesamiento_distribuido.md) | 90–120 min | Spark local en Ubuntu; ampliación gestionada condicionada |
| [G16 · Mini plataforma analítica](G16_Mini_plataforma_analitica.md) | 2–3 × 90 min | Proyecto sobre Iris de UCI, con procedencia y cierre |

## Material de apoyo

- [CSV sintético de métricas](metricas_raw.csv): utilizado de G08 a G15; incluye errores de calidad deliberados.
- [Comprobaciones y adaptación docente](DOCENTE_Comprobaciones_y_adaptacion.md): permisos, versiones, capacidades y rutas alternativas.
- Carpeta `apoyo_scripts` del paquete ZIP: copias de los programas completos de las guías. Deben colocarse en las rutas indicadas de Ubuntu; no se ejecutan automáticamente al abrirlos.
- Los enlaces oficiales junto a las instrucciones permiten contrastar los detalles de servicios y herramientas.

## Convenciones que se mantienen

| Elemento | Referencia |
|---|---|
| Instancia | `fp-analytics-01` |
| Grupo propio | `fp-analytics-sg` |
| Par y clave local | `fp-analytics-key` / `fp-analytics-key.pem` |
| Alias SSH local | `fp-analytics` |
| Carpeta Ubuntu | `/home/ubuntu/practicas-aws` |
| Configuración no secreta | `lab.env`, creada en G09 |
| Entorno Python | `.venv`; Spark separado en `.venv-spark` |
| Bucket | Nombre individual, privado, sin datos personales |
| Capas S3 | `raw`, `curated`, `resultados`, `athena-results` |

Si varios alumnos comparten cuenta, el docente asignará nombres/prefijos individuales y hará sustituirlos de forma coherente en todos los comandos. Los marcadores `IP_PUBLICA_REAL`, `NOMBRE_REAL_DEL_BUCKET`, `TABLA_REAL` y similares deben sustituirse antes de ejecutar.

## Decisiones sobre los servicios aún no verificados

- París se usa solo si la región y las acciones necesarias están autorizadas; una lista visible no lo prueba.
- AMI Ubuntu, tipo y disco son propuestas que el docente debe ensayar, no parámetros ya confirmados de Academy.
- AWS CLI y Boto3 desde EC2 requieren un perfil IAM utilizable. No se proporcionan claves manuales como alternativa a una denegación.
- Athena requiere catálogo y acceso S3; Glue crawler requiere además rol y permisos propios. G12–G14 incluyen alternativas documentadas.
- G15 distingue Spark local de procesamiento distribuido. EMR Serverless es una ampliación opcional sujeta a ensayo y presupuesto; no se lanzan clústeres EC2 con Amazon Linux.
- RDS, Redshift y Lambda se mencionaban en la auditoría inicial, pero no eran guías independientes del índice G01–G16; no se añaden despliegues de esos servicios a esta colección.

## Rutina al terminar cada clase

Guarda la entrega, detén procesos temporales y EC2 cuando corresponda, revisa trabajos gestionados y utiliza **End Lab** con confirmación. Conserva los recursos necesarios para las guías siguientes. La eliminación final, tras copiar los resultados, se detalla en G16.
