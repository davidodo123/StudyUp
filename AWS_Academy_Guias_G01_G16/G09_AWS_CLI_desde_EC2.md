# G09 · AWS CLI desde Ubuntu EC2 mediante un rol

**Curso:** Curso de Especialización FP Aprendizaje Automático — Instalación, Despliegue y Explotación de Sistemas  
**Módulo:** Explotación de servicios de procesamiento y analítica de datos  
**Entorno:** Windows 11 → AWS Academy Learner Lab → Ubuntu en EC2  
**Duración orientativa:** 60–75 minutos  
**Requisitos:** G04–G05 y G08; perfil IAM asignable a EC2 confirmado por el docente.  
**Recursos:** EC2 existente, AWS CLI v2 y acceso al bucket de G08.  
**Resultado:** Descarga desde S3 usando credenciales temporales del perfil, sin claves manuales.

## Antes de empezar

1. Inicia el Learner Lab con **Start Lab** y espera a que esté activo.
2. Abre la consola AWS desde el enlace del Lab. Usa **París (`eu-west-3`) solo si está autorizada**, según G01 y las instrucciones actuales. Si se utiliza otra región, mantenla en toda la práctica.
3. Comprueba presupuesto y tiempo restante. Las cifras dependen de tu laboratorio; no se presupone gratuidad. La aparición de un servicio no garantiza permiso para utilizarlo.
4. Sigue el lugar de ejecución indicado: **PowerShell de Windows**, **terminal del Learner Lab** o **terminal Ubuntu de EC2**. No intercambies sus comandos.
5. En bloques con varias órdenes, ejecuta una línea cada vez, excepto los bloques de creación de archivos que se indique pegar completos. No copies los marcadores de Markdown.

> **Importante · Seguridad**  
> No compartas Account ID, UserId, ARN completo, Access Key, Secret Key, Session Token ni archivos privados `.pem`. No subas claves a EC2, S3, repositorios o herramientas de IA. Entrega resultados resumidos y capturas recortadas. Los permisos se conceden mediante los roles previstos por el laboratorio; no los amplíes para eludir una restricción.

## 1. Qué cambia respecto a G01

```text
Windows → SSH con .pem → Ubuntu EC2 → perfil IAM → S3
```

La CLI de G01 estaba en la terminal del Learner Lab. Ahora la ejecutarás dentro de tu EC2. Las credenciales de esos entornos no se comparten automáticamente.

## 2. Comprueba el perfil de instancia

1. En la consola EC2 selecciona tu instancia y revisa su rol/perfil IAM.
2. Si no está asociado y el docente ha confirmado uno existente, utiliza **Actions → Security → Modify IAM role** y selecciona ese perfil.
3. No crees un rol nuevo. El nombre puede ser `LabInstanceProfile`, pero no es un dato verificado para todas las ediciones.
4. Si no puedes asociarlo o aparece error de `iam:PassRole`, registra la limitación. No copies credenciales del Lab a Ubuntu para sortearla.

El perfil proporciona a la instancia credenciales temporales para su rol. No necesitas almacenarlas en archivos ni consultarlas manualmente en los metadatos. [AWS: roles IAM para EC2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/iam-roles-for-amazon-ec2.html).

## 3. Instala AWS CLI v2 si falta

Conecta por SSH. Todos los comandos siguientes se ejecutan en **Ubuntu EC2**.

```bash
uname -m
command -v aws
```

`uname -m` debe mostrar `x86_64` para este instalador. `command -v` busca la herramienta. Si existe, ejecuta `aws --version` y registra su versión. Si ya tienes CLI v2 funcional, pasa al paso 4.

Si no existe, ejecuta:

```bash
sudo apt-get update
sudo apt-get install -y curl unzip
mkdir -p ~/practicas-aws/instaladores
cd ~/practicas-aws/instaladores
curl --fail --location https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip -o awscliv2.zip
unzip awscliv2.zip
sudo ./aws/install
aws --version
```

`curl` descarga del sitio oficial y falla ante un error HTTP; `unzip` extrae el instalador; `sudo ./aws/install` instala la herramienta. Si `aws/` ya existía de otro intento, no aceptes sobrescrituras sin revisar con el docente. Si hay una instalación previa v1 o una ruta distinta, el docente debe resolverla en vez de instalar varias copias.

Estas órdenes siguen la ruta de instalación de [AWS CLI v2 en Linux](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html). Para preparar la imagen del aula, el docente debe comprobar también la firma del instalador mediante el procedimiento PGP de esa página y registrar la versión elegida.

## 4. Guarda solo la configuración no secreta

En Ubuntu pega **completo** el bloque siguiente, cambiando región y nombre del bucket por los reales antes de ejecutarlo:

```bash
cat > ~/practicas-aws/lab.env <<'ENV'
export AWS_REGION='eu-west-3'
export AWS_DEFAULT_REGION='eu-west-3'
export AWS_PAGER=''
export BUCKET='NOMBRE_REAL_DEL_BUCKET'
ENV
```

Contiene región, ajuste de paginador y bucket, **nunca credenciales**. No añadas Access Key, Secret Key ni Session Token. `export` hace disponibles esos valores a los programas de esta terminal.

Actívalo:

```bash
source ~/practicas-aws/lab.env
printf 'Region=%s\nBucket=%s\n' "$AWS_REGION" "$BUCKET"
```

`source` aplica el archivo a la terminal actual; la impresión muestra solo región y bucket. Repite `source` cada vez que abras una nueva terminal. No uses `env` para imprimir todas las variables ni ejecutes el asistente `aws configure` para introducir credenciales.

## 5. Comprueba identidad sin imprimir identificadores

```bash
aws sts get-caller-identity --region "$AWS_REGION" --query "contains(Arn, ':assumed-role/')" --output text --no-cli-pager
```

El servicio STS comprueba quién llama; la consulta muestra solo si el ARN corresponde a una sesión de rol. **Resultado esperado: `True`**. No presupongas que el rol dentro de EC2 será `voclabs`, que era la identidad de la terminal del Lab. [AWS: get-caller-identity](https://docs.aws.amazon.com/cli/latest/reference/sts/get-caller-identity.html).

> **Si algo falla**  
> `Unable to locate credentials` requiere revisar perfil y metadatos con el docente. Si hay credenciales antiguas configuradas manualmente, pueden prevalecer sobre el perfil: no muestres su contenido; pide retirarlas de forma controlada. No consultes endpoints de metadatos que devuelvan tokens o claves para compartirlos.

> **Qué está ocurriendo**  
> El acceso SSH te identifica frente a Ubuntu y el perfil IAM identifica a los programas frente a AWS. La región y el bucket de `lab.env` son configuración; no sustituyen ninguno de esos mecanismos.

## 6. Consulta y descarga un objeto propio

```bash
aws s3 ls "s3://$BUCKET/raw/metricas/" --region "$AWS_REGION"
mkdir -p ~/practicas-aws/datos/raw
aws s3 cp "s3://$BUCKET/raw/metricas/metricas_raw.csv" ~/practicas-aws/datos/raw/metricas_raw.csv --region "$AWS_REGION"
head -n 3 ~/practicas-aws/datos/raw/metricas_raw.csv
```

`s3 ls` lista el prefijo concreto; `cp` descarga el objeto; `head` muestra encabezado y dos registros. Debes ver el CSV de G08. No hace falta listar todos los buckets de la cuenta: esa acción puede estar denegada aunque tengas acceso al tuyo.

> **Si algo falla**  
> `AccessDenied` en lista puede indicar falta de ListBucket; en descarga, falta de GetObject o una política adicional. STS correcto no prueba permisos S3. `NoSuchKey` significa que la clave no coincide: revisa mayúsculas, prefijo y archivo en consola. Comprueba que EC2 puede salir a Internet antes de atribuir un timeout a IAM.

## 7. Entrega, cierre y resumen

Registra versión, «sesión de rol comprobada», listado del prefijo y descarga correcta, sin ARN. Conserva `lab.env` y el CSV para Python. La asignación del perfil no es un secreto, pero no publiques identificadores completos. Detén EC2 si terminas y pulsa End Lab.

**Resumen:** Ubuntu puede acceder a servicios AWS sin claves persistentes. **Siguiente:** G10, el mismo acceso desde Python. **Reto:** explica por qué STS puede funcionar mientras un `s3 cp` devuelve AccessDenied.
