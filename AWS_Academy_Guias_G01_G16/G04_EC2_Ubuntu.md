# G04 · Creación y configuración de una instancia EC2 Ubuntu

**Curso:** Curso de Especialización FP Aprendizaje Automático — Instalación, Despliegue y Explotación de Sistemas  
**Módulo:** Explotación de servicios de procesamiento y analítica de datos  
**Entorno:** Windows 11 → AWS Academy Learner Lab → Ubuntu en EC2  
**Duración orientativa:** 60–75 minutos  
**Requisitos:** G01–G03; VPC y subred válidas; clave privada protegida; AMI y tipo comprobados por el docente.  
**Recursos:** Una EC2 Ubuntu x86_64, un volumen EBS y una IPv4 pública durante el uso.  
**Resultado:** Instancia fp-analytics-01 preparada para SSH y futuras prácticas.

## Antes de empezar

1. Inicia el Learner Lab con **Start Lab** y espera a que esté activo.
2. Abre la consola AWS desde el enlace del Lab. Usa **París (`eu-west-3`) solo si está autorizada**, según G01 y las instrucciones actuales. Si se utiliza otra región, mantenla en toda la práctica.
3. Comprueba presupuesto y tiempo restante. Las cifras dependen de tu laboratorio; no se presupone gratuidad. La aparición de un servicio no garantiza permiso para utilizarlo.
4. Sigue el lugar de ejecución indicado: **PowerShell de Windows**, **terminal del Learner Lab** o **terminal Ubuntu de EC2**. No intercambies sus comandos.
5. En bloques con varias órdenes, ejecuta una línea cada vez, excepto los bloques de creación de archivos que se indique pegar completos. No copies los marcadores de Markdown.

> **Importante · Seguridad**  
> No compartas Account ID, UserId, ARN completo, Access Key, Secret Key, Session Token ni archivos privados `.pem`. No subas claves a EC2, S3, repositorios o herramientas de IA. Entrega resultados resumidos y capturas recortadas. Los permisos se conceden mediante los roles previstos por el laboratorio; no los amplíes para eludir una restricción.

## 1. Objetivos y coste

Aprenderás a seleccionar imagen, capacidad, disco, red, clave y perfil IAM sin aceptar todos los valores del asistente automáticamente.

```text
Windows → TCP/22 desde Mi IP → fp-analytics-01 (Ubuntu)
                                      ├── disco EBS
                                      └── perfil IAM, si está autorizado
```

EC2 en ejecución, EBS e IPv4 pública pueden consumir presupuesto. Las etiquetas «Free tier» del asistente no garantizan gratuidad en Academy. Trabajaremos con una sola instancia reutilizable.

## 2. Ficha que debe validar el docente

| Parámetro | Referencia para la colección |
|---|---|
| AMI | Ubuntu Server 24.04 LTS oficial de Canonical, x86_64; 22.04 LTS si es la validada |
| Tipo | El menor tipo permitido que soporte la práctica; `t3.micro`/`t2.micro` son candidatos para SSH, no garantías |
| Disco | 16 GiB gp3 como propuesta de aula, ajustada a permiso y presupuesto |
| Red | VPC y subred pública de G02 |
| Entrada | Grupo propio con SSH desde Mi IP |
| Clave | Par de G03 en la misma región |
| Perfil IAM | El perfil existente autorizado para EC2, si está disponible |

Para VS Code, pandas y especialmente Spark puede hacer falta más memoria que en una micro. No cambies de tipo para aumentar capacidad sin comprobar consumo y autorización. No se proporciona un AMI ID universal: depende de la región y debe verificarse.

## 3. Configura el lanzamiento sin pulsar aún Launch

1. En **EC2 → Instances**, pulsa **Launch instances / Lanzar instancias**.
2. Nombre: `fp-analytics-01`; añade código de alumno si se comparte cuenta.
3. En **Application and OS Images**, selecciona **Ubuntu**.
4. Elige la versión LTS y arquitectura validadas en la ficha. Comprueba editor Canonical y que no sea una imagen de Marketplace con cargos adicionales.
5. Selecciona el tipo permitido de arquitectura x86_64. No combines AMI ARM64 con un tipo x86_64.
6. En **Key pair**, selecciona el par creado en G03. No continúes sin un método de acceso previsto.
7. En **Network settings**, pulsa **Edit**.
8. Elige la VPC y subred anotadas en G02.
9. Activa **Auto-assign public IP / Asignar IP pública automáticamente**.
10. Selecciona un grupo de seguridad **existente** y marca solo `fp-analytics-sg`.
11. Comprueba que no se está creando otro grupo con SSH desde cualquier origen.
12. En almacenamiento, configura el volumen raíz aprobado. Mantén eliminación al terminar para este volumen de práctica, una vez comprobada la política del docente.

Estos parámetros conectan con el flujo de [lanzamiento y conexión de una instancia de prueba de AWS](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/tutorial-launch-a-test-ec2-instance.html). Los valores concretos de esta ficha son una propuesta docente pendiente de ensayo en Academy.

## 4. Perfil IAM y opciones avanzadas

1. Despliega **Advanced details / Detalles avanzados**.
2. En **IAM instance profile**, selecciona el perfil **existente confirmado** por el docente. Algunos Labs lo denominan `LabInstanceProfile`, pero no lo des por existente.
3. No crees un rol ni una Access Key. Si no hay perfil autorizado, deja registrado «sin perfil»: SSH puede funcionar, pero G09–G10 necesitarán resolver esa condición.
4. Mantén los metadatos de instancia habilitados y configura **IMDSv2 requerido**, si está permitido. Las herramientas actuales pueden obtener credenciales del perfil sin almacenarlas manualmente.
5. Deja **User data** vacío en esta primera creación, para poder realizar y comprender la configuración después.
6. No solicites Spot, Elastic IP ni servicios adicionales.

> **Qué está ocurriendo**  
> Un perfil de instancia permite asociar un rol IAM a EC2. Ese rol controla llamadas de Ubuntu a servicios AWS; el `.pem` controla tu entrada SSH. Son mecanismos diferentes. [AWS: roles IAM para EC2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/iam-roles-for-amazon-ec2.html).

## 5. Revisión y lanzamiento

Antes de lanzar comprueba en voz alta o con un compañero: región, Ubuntu LTS oficial, arquitectura compatible, tipo, disco, VPC/subred, IP pública, grupo propio, clave y una sola instancia.

1. Configura **Number of instances = 1**.
2. Pulsa **Launch instance** una vez.
3. Abre **View all instances**.
4. Selecciona la instancia por su nombre y revisa su ID localmente.
5. Espera a **Running** y a que las comprobaciones de estado disponibles se indiquen correctas. No te guíes por un número fijo: la interfaz puede mostrar varias comprobaciones.
6. En detalles comprueba IPv4 pública, AMI, tipo y par de claves.
7. En seguridad verifica que el grupo asociado es el propio de G02.

**Resultado esperado:** instancia en ejecución con IP pública y comprobaciones correctas. Que esté en ejecución no demuestra todavía acceso SSH.

> **Si algo falla**  
> Ante `UnauthorizedOperation`, `AccessDenied`, error de `PassRole`, AMI restringida, límite de vCPU o tipo no permitido, registra el parámetro y el error. No repitas el lanzamiento con variantes al azar: revisa primero si se creó una instancia. Pide al docente la combinación validada. Una AMI que aparece en el buscador puede estar restringida.

Si no hay IP pública, comprueba la subred y la asignación solicitada. No añadas una Elastic IP como solución automática. Si las comprobaciones fallan, consulta estado y diagnóstico con el docente antes de reemplazar la instancia. [AWS: diagnóstico de instancias inaccesibles](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/troubleshoot-unreachable-instance.html).

## 6. Guarda el inventario

En un archivo local privado registra: nombre, región, AMI/versión, arquitectura, tipo, ID de instancia, VPC/subred, grupo, par y perfil IAM. No guardes credenciales. La IP pública se consulta de nuevo cada día.

## 7. Detener, reanudar y cerrar

1. Si continúas inmediatamente con G05, mantén la instancia en ejecución durante esa guía.
2. Si termina la clase, selecciona tu instancia: **Instance state → Stop instance**. Espera a **Stopped**.
3. No selecciones **Terminate**: destruye la instancia y puede borrar su disco raíz. Detener conserva el volumen EBS, que puede seguir consumiendo presupuesto.
4. Pulsa **End Lab** y confirma el cierre.
5. Para la próxima clase, inicia el Lab y después inicia tu instancia si está detenida. Espera sus comprobaciones y copia la nueva IP pública.

La IPv4 asignada automáticamente puede cambiar tras detener y arrancar. Actualiza SSH y VS Code en ese caso. [AWS: parada y arranque](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/Stop_Start.html).

**Entrega:** ficha sin IDs completos, evidencia de Ubuntu seleccionado y estado correcto. **Resumen:** has construido el servidor que reutilizarás. **Siguiente:** G05, SSH desde Windows. **Reto:** diferencia detener y terminar, incluyendo lo que sucede con el almacenamiento.

