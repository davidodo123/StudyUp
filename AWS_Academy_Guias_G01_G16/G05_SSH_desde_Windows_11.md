# G05 · Acceso a Ubuntu EC2 por SSH desde Windows 11

**Curso:** Curso de Especialización FP Aprendizaje Automático — Instalación, Despliegue y Explotación de Sistemas  
**Módulo:** Explotación de servicios de procesamiento y analítica de datos  
**Entorno:** Windows 11 → AWS Academy Learner Lab → Ubuntu en EC2  
**Duración orientativa:** 45–60 minutos  
**Requisitos:** G03–G04; EC2 en ejecución; IPv4 actual; regla TCP/22 desde tu IP.  
**Recursos:** Cliente OpenSSH de Windows y EC2 de G04.  
**Resultado:** Sesión SSH autenticada y primeras comprobaciones de Ubuntu.

## Antes de empezar

1. Inicia el Learner Lab con **Start Lab** y espera a que esté activo.
2. Abre la consola AWS desde el enlace del Lab. Usa **París (`eu-west-3`) solo si está autorizada**, según G01 y las instrucciones actuales. Si se utiliza otra región, mantenla en toda la práctica.
3. Comprueba presupuesto y tiempo restante. Las cifras dependen de tu laboratorio; no se presupone gratuidad. La aparición de un servicio no garantiza permiso para utilizarlo.
4. Sigue el lugar de ejecución indicado: **PowerShell de Windows**, **terminal del Learner Lab** o **terminal Ubuntu de EC2**. No intercambies sus comandos.
5. En bloques con varias órdenes, ejecuta una línea cada vez, excepto los bloques de creación de archivos que se indique pegar completos. No copies los marcadores de Markdown.

> **Importante · Seguridad**  
> No compartas Account ID, UserId, ARN completo, Access Key, Secret Key, Session Token ni archivos privados `.pem`. No subas claves a EC2, S3, repositorios o herramientas de IA. Entrega resultados resumidos y capturas recortadas. Los permisos se conceden mediante los roles previstos por el laboratorio; no los amplíes para eludir una restricción.

## 1. Comprueba el cliente local

En **PowerShell de Windows**, ejecuta:

```powershell
ssh -V
```

`-V` muestra la versión de OpenSSH. Si no se reconoce, abre **Configuración → busca Características opcionales → Ver características**, busca **OpenSSH Client / Cliente OpenSSH** y pide su instalación al responsable del equipo si no tienes permisos. Reabre PowerShell tras instalarlo. No necesitas OpenSSH Server en Windows para esta práctica. [Microsoft: instalación de OpenSSH](https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse).

## 2. Comprueba red y clave antes de conectar

1. En la consola copia la **IPv4 pública actual** de tu instancia, no la privada.
2. Comprueba que el grupo de seguridad permite TCP/22 desde tu IP pública actual.
3. En PowerShell sustituye el texto entre comillas por la IP, conservando las comillas:

```powershell
$ec2Host = 'IP_PUBLICA_REAL'
$keyPath = Join-Path $env:USERPROFILE '.ssh\fp-analytics-key.pem'
Test-Path -LiteralPath $keyPath
Test-NetConnection -ComputerName $ec2Host -Port 22
```

La primera prueba debe dar `True`. La segunda comprueba TCP al puerto 22: busca **TcpTestSucceeded : True**. Un ping fallido no demuestra un fallo de SSH; ICMP puede estar bloqueado.

> **Si algo falla**  
> Si TCP falla, revisa instancia Running, IP pública, regla Mi IP, ruta de G02 y red del centro. No abras SSH a todo Internet ni todos los puertos. Si la red del centro bloquea SSH, solicita la alternativa prevista por el docente.

## 3. Verifica la identidad del servidor

Antes del primer acceso, el docente debe proporcionar una vía fiable para contrastar la huella SSH. Si puedes leerlo en la consola:

1. Selecciona tu instancia en EC2.
2. Abre **Actions → Monitor and troubleshoot → Get system log**.
3. Busca el bloque de huellas SSH generado en el primer arranque de Ubuntu, por ejemplo `SSH HOST KEY FINGERPRINTS`.
4. Localiza la huella SHA256 y el tipo de clave que mostrará el cliente.

Si el log no contiene la huella o no está accesible, el docente debe verificarla por un canal independiente autorizado. Obtenerla con `ssh-keyscan` por la misma conexión no autentica por sí solo al servidor. No aceptes una huella desconocida solo para continuar. [AWS: conexión SSH y huella del servidor](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/connect-linux-inst-ssh.html).

## 4. Conecta

En la misma ventana PowerShell:

```powershell
ssh -i "$keyPath" "ubuntu@$ec2Host"
```

`ssh` inicia la conexión cifrada; `-i` selecciona tu clave privada; `ubuntu` es el usuario de la AMI oficial Ubuntu; después de `@` va el servidor.

En el primer acceso compara la huella presentada con la verificada en el paso 3. Solo si coincide, escribe `yes`. Se guardará la identidad del servidor en `known_hosts` de tu PC. [AWS: conexión con cliente SSH](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/connect-linux-inst-ssh.html).

**Resultado esperado:** un indicador parecido a `ubuntu@ip-…:~$`. Desde este momento, los comandos de esa ventana se ejecutan en **Ubuntu EC2**.

## 5. Comprueba dónde estás

En **Ubuntu**, ejecuta cada orden:

```bash
whoami
pwd
cat /etc/os-release
uname -m
df -h /
free -h
mkdir -p ~/practicas-aws
cd ~/practicas-aws
pwd
```

| Orden | Qué significa / resultado esperado |
|---|---|
| `whoami` | Usuario actual: `ubuntu` |
| `pwd` | Directorio actual, inicialmente normalmente `/home/ubuntu` |
| `cat /etc/os-release` | Identificación del sistema: Ubuntu y versión LTS validada |
| `uname -m` | Arquitectura: `x86_64` para esta colección |
| `df -h /` | Capacidad y espacio disponible en el disco raíz |
| `free -h` | Memoria disponible; ayuda a diagnosticar falta de recursos |
| `mkdir -p` | Crea la carpeta de prácticas si no existe |
| `cd` y último `pwd` | Entra y confirma `/home/ubuntu/practicas-aws` |

No pegues las salidas completas si incluyen información identificativa.

> **Qué está ocurriendo**  
> La conexión SSH transporta tus órdenes, pero las ejecuta Ubuntu. Por eso `pwd` muestra una ruta Linux aunque hayas iniciado SSH desde Windows. La prueba TCP previa comprueba red; la clave y la huella comprueban autenticación e identidad.

## 6. Errores frecuentes

| Error | Revisión |
|---|---|
| `Permission denied (publickey)` | Usuario `ubuntu`, par elegido al lanzar, ruta `.pem` y permisos de G03 |
| `UNPROTECTED PRIVATE KEY FILE` | Revisa ACL de ese archivo en Windows; no lo hagas público |
| `Connection timed out` | Revisa conectividad del paso 2, ruta e IP actual |
| `Connection refused` | El destino responde, pero SSH podría no estar listo; revisa estado y diagnóstico |
| `Could not resolve hostname` | Has dejado un marcador o copiado un nombre/IP incorrecto |
| `REMOTE HOST IDENTIFICATION HAS CHANGED` | No ignores el aviso: comprueba instancia, nueva IP y huella con el docente |

Solo tras verificar una sustitución legítima del servidor, elimina **la entrada concreta antigua**, en PowerShell:

```powershell
ssh-keygen -R "$ec2Host"
```

`-R` retira la entrada para ese host. No borres todo `known_hosts`; vuelve a contrastar la nueva huella al conectar. [AWS: diagnóstico de conexión](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/TroubleshootingInstancesConnecting.html).

## 7. Salida, entrega y cierre

En Ubuntu ejecuta `exit`: cierra SSH y regresa a PowerShell. No detiene EC2.

Entrega «SSH correcto, usuario ubuntu, versión de Ubuntu, arquitectura y carpeta creada», sin IP/ARN completos. Si no continúas, detén tu instancia desde EC2, espera Stopped y finaliza con End Lab.

**Resumen:** ya distingues el equipo local del remoto. **Siguiente:** G06, edición remota. **Reto:** vuelve a conectar, entra en la carpeta y explica por qué tus archivos siguen ahí tras cerrar SSH.
