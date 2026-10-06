# G03 · Claves SSH y almacenamiento seguro en Windows 11

**Curso:** Curso de Especialización FP Aprendizaje Automático — Instalación, Despliegue y Explotación de Sistemas  
**Módulo:** Explotación de servicios de procesamiento y analítica de datos  
**Entorno:** Windows 11 → AWS Academy Learner Lab → Ubuntu en EC2  
**Duración orientativa:** 40–50 minutos  
**Requisitos:** G01–G02; permiso para crear un par de claves en la región confirmada.  
**Recursos:** Un Key Pair RSA; archivo privado local .pem.  
**Resultado:** Par de claves creado y archivo protegido en el perfil de Windows.

## Antes de empezar

1. Inicia el Learner Lab con **Start Lab** y espera a que esté activo.
2. Abre la consola AWS desde el enlace del Lab. Usa **París (`eu-west-3`) solo si está autorizada**, según G01 y las instrucciones actuales. Si se utiliza otra región, mantenla en toda la práctica.
3. Comprueba presupuesto y tiempo restante. Las cifras dependen de tu laboratorio; no se presupone gratuidad. La aparición de un servicio no garantiza permiso para utilizarlo.
4. Sigue el lugar de ejecución indicado: **PowerShell de Windows**, **terminal del Learner Lab** o **terminal Ubuntu de EC2**. No intercambies sus comandos.
5. En bloques con varias órdenes, ejecuta una línea cada vez, excepto los bloques de creación de archivos que se indique pegar completos. No copies los marcadores de Markdown.

> **Importante · Seguridad**  
> No compartas Account ID, UserId, ARN completo, Access Key, Secret Key, Session Token ni archivos privados `.pem`. No subas claves a EC2, S3, repositorios o herramientas de IA. Entrega resultados resumidos y capturas recortadas. Los permisos se conceden mediante los roles previstos por el laboratorio; no los amplíes para eludir una restricción.

## 1. Qué vas a preparar

```text
Windows: clave privada .pem → autenticación SSH → Ubuntu: clave pública
```

La clave privada permanece en tu PC. AWS conserva la pública y la incorpora a la instancia cuando se lanza. Una clave SSH no es una credencial de AWS CLI. [AWS: pares de claves de EC2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html).

## 2. Crea y descarga el par de claves

1. En la consola de EC2 comprueba la región.
2. Abre **Network & Security → Key Pairs / Pares de claves**.
3. Pulsa **Create key pair**.
4. Nombre: `fp-analytics-key` o el nombre individual acordado en cuentas compartidas.
5. Selecciona **RSA** y formato **.pem**.
6. Crea el par. Comprueba que el navegador descarga `fp-analytics-key.pem`.
7. No abras el archivo para copiar su contenido ni lo envíes al docente.

**Resultado esperado:** par visible en la región y un archivo privado descargado. La descarga de la clave privada creada por EC2 se ofrece una sola vez. [AWS: creación de pares de claves](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/create-key-pairs.html).

> **Si algo falla**  
> Si CreateKeyPair está denegado, el docente debe comprobar la posibilidad de crear claves o el mecanismo previsto por el Lab. No asumas que existe una clave llamada `vockey`. Si la descarga falla antes de lanzar EC2, consulta al docente para sustituir únicamente tu par inutilizable por uno nuevo; crear otro con el mismo nombre no recupera la clave anterior.

## 3. Guarda el archivo fuera de Descargas

1. En Windows pulsa Inicio, escribe **PowerShell** y ábrelo como tu usuario habitual.
2. Ejecuta:

```powershell
New-Item -ItemType Directory -Path "$env:USERPROFILE\.ssh" -Force
```

`$env:USERPROFILE` es tu carpeta de usuario; `.ssh` será la carpeta local de conexión. `-Force` permite que ya exista.

3. En el Explorador activa la visualización de extensiones de archivo.
4. Mueve el `.pem` descargado a esa carpeta. Puedes pegar `%USERPROFILE%\.ssh` en la barra de direcciones del Explorador.
5. Comprueba que su nombre es exactamente `fp-analytics-key.pem`, no `.pem.txt` ni una copia con `(1)`.
6. En PowerShell comprueba la existencia sin mostrar su contenido:

```powershell
$keyPath = Join-Path $env:USERPROFILE '.ssh\fp-analytics-key.pem'
Test-Path -LiteralPath $keyPath
```

**Resultado esperado:** `True`. La variable `$keyPath` contiene una ruta, no la clave.

## 4. Restringe los permisos del archivo

Realiza esto **solo sobre el `.pem` propio**, no sobre carpetas ni otros archivos. No necesitas elevar PowerShell para un archivo de tu propiedad.

```powershell
$keyPath = Join-Path $env:USERPROFILE '.ssh\fp-analytics-key.pem'
$mySid = [System.Security.Principal.WindowsIdentity]::GetCurrent().User.Value
icacls.exe "$keyPath" /inheritance:r
icacls.exe "$keyPath" /grant:r "*${mySid}:(R)"
icacls.exe "$keyPath"
```

| Orden | Qué significa |
|---|---|
| Obtención de `$mySid` | Identificador de seguridad de tu usuario, independiente del idioma de Windows |
| `/inheritance:r` | Quita permisos heredados del archivo |
| `/grant:r` y `(R)` | Establece lectura para tu usuario |
| Último `icacls` | Muestra los permisos para revisarlos |

Cada modificación debe indicar que se ha procesado un archivo sin errores. Revisa la última salida: puede haber permisos explícitos que no se hayan eliminado. Si otros usuarios o grupos amplios mantienen lectura, abre **Propiedades → Seguridad → Opciones avanzadas** del archivo y retira esas entradas, con ayuda del docente. Comprueba que eres el propietario y conservas lectura. No concedas acceso a Everyone/Todos o Users/Usuarios. [Microsoft: icacls](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/icacls).

> **Importante**  
> No utilices `chmod 400` en PowerShell para resolver permisos de Windows. La ACL de Windows controla el acceso. Evita carpetas compartidas y sincronización de la clave en repositorios o almacenamiento de clase. [AWS: requisitos de conexión y permisos de clave en Windows](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/connection-prereqs-general.html).

> **Qué está ocurriendo**  
> Tener un `.pem` descargado no demuestra todavía que puedas entrar en Ubuntu. Debe corresponder al par seleccionado al lanzar la instancia y ser legible solo por las identidades autorizadas en Windows.

## 5. Pérdida, exposición y comprobación final

Si pierdes la clave, AWS no devuelve otra copia. En esta fase inicial, antes de crear EC2, se puede preparar un nuevo par propio. Una vez lanzada la instancia, cambiar el nombre del par en la consola o crear otro par no cambia automáticamente las claves autorizadas dentro de Ubuntu. El docente decidirá recuperación o recreación tras guardar los datos.

Si se expone el `.pem`, trata la clave como comprometida y avisa. Eliminar el registro del Key Pair en EC2 tampoco retira una clave pública ya presente en `authorized_keys` de una instancia.

## 6. Entrega, cierre y resumen

- Registra nombre del par, región y «archivo local existente; permisos revisados».
- No entregues el `.pem`, su contenido ni una captura del contenido.
- Conserva la clave para G04–G06. Pulsa **End Lab** y comprueba el cierre.

**Has aprendido:** pública y privada tienen funciones distintas; custodiar la privada es parte del acceso seguro. **Siguiente:** G04, lanzar Ubuntu con este par. **Reto:** explica por qué la clave de SSH no sirve para listar buckets S3.
