# G06 · VS Code y Remote - SSH con Ubuntu EC2

**Curso:** Curso de Especialización FP Aprendizaje Automático — Instalación, Despliegue y Explotación de Sistemas  
**Módulo:** Explotación de servicios de procesamiento y analítica de datos  
**Entorno:** Windows 11 → AWS Academy Learner Lab → Ubuntu en EC2  
**Duración orientativa:** 45–60 minutos  
**Requisitos:** G05 completa y SSH funcional; VS Code instalado en Windows.  
**Recursos:** VS Code, extensión de Microsoft y la EC2 existente.  
**Resultado:** Carpeta remota abierta, archivo editado y terminal Ubuntu en VS Code.

## Antes de empezar

1. Inicia el Learner Lab con **Start Lab** y espera a que esté activo.
2. Abre la consola AWS desde el enlace del Lab. Usa **París (`eu-west-3`) solo si está autorizada**, según G01 y las instrucciones actuales. Si se utiliza otra región, mantenla en toda la práctica.
3. Comprueba presupuesto y tiempo restante. Las cifras dependen de tu laboratorio; no se presupone gratuidad. La aparición de un servicio no garantiza permiso para utilizarlo.
4. Sigue el lugar de ejecución indicado: **PowerShell de Windows**, **terminal del Learner Lab** o **terminal Ubuntu de EC2**. No intercambies sus comandos.
5. En bloques con varias órdenes, ejecuta una línea cada vez, excepto los bloques de creación de archivos que se indique pegar completos. No copies los marcadores de Markdown.

> **Importante · Seguridad**  
> No compartas Account ID, UserId, ARN completo, Access Key, Secret Key, Session Token ni archivos privados `.pem`. No subas claves a EC2, S3, repositorios o herramientas de IA. Entrega resultados resumidos y capturas recortadas. Los permisos se conceden mediante los roles previstos por el laboratorio; no los amplíes para eludir una restricción.

## 1. Objetivo

```text
VS Code en Windows → OpenSSH + .pem local → VS Code Server en Ubuntu → archivos remotos
```

Primero debe funcionar SSH en PowerShell. Remote - SSH instalará sus componentes en Ubuntu y necesita conectividad para descargarlos. La clave privada permanece en Windows. [Microsoft: Remote - SSH](https://code.visualstudio.com/docs/remote/ssh).

## 2. Instala la extensión correcta

1. Abre VS Code en Windows; utiliza el instalador oficial si falta: [VS Code para Windows](https://code.visualstudio.com/docs/setup/windows).
2. Pulsa **Ctrl+Shift+X** para abrir Extensiones.
3. Busca **Remote - SSH** y comprueba que el editor es **Microsoft**; identificador `ms-vscode-remote.remote-ssh`.
4. Instálala en Windows. No instales extensiones de nombre similar de terceros para resolver la conexión.
5. Mantén la instancia en ejecución y comprueba la IP pública actual.

## 3. Crea una entrada SSH

En **PowerShell de Windows**, abre el archivo de configuración:

```powershell
notepad.exe "$env:USERPROFILE\.ssh\config"
```

Si no existe, acepta crearlo. Añade al final este bloque, conservando las entradas anteriores. Sustituye la IP y la ruta por valores reales:

```sshconfig
Host fp-analytics
    HostName IP_PUBLICA_REAL
    User ubuntu
    IdentityFile "C:/Users/TU_USUARIO/.ssh/fp-analytics-key.pem"
    IdentitiesOnly yes
    ServerAliveInterval 30
```

`Host` es un alias local; `HostName`, el servidor; `User`, el usuario remoto; `IdentityFile`, la clave **de Windows**; `IdentitiesOnly` limita las identidades ofrecidas; `ServerAliveInterval` envía comprobaciones periódicas. No impide que el Lab caduque.

Guarda como **config**, sin `.txt`. Si tu ruta contiene espacios, conserva sus comillas. Consulta tu ruta real con `Write-Output $env:USERPROFILE` en PowerShell; no escribas literalmente `TU_USUARIO`.

Comprueba la entrada en PowerShell:

```powershell
ssh fp-analytics
```

Debe abrir la misma Ubuntu. Si funciona, ejecuta `exit`. Si falla, resuelve la configuración antes de abrir VS Code remoto. [Microsoft: cliente SSH y configuración](https://code.visualstudio.com/docs/remote/troubleshooting).

## 4. Abre la sesión remota

1. Pulsa **Ctrl+Shift+P** en VS Code.
2. Ejecuta **Remote-SSH: Connect to Host…**.
3. Selecciona `fp-analytics` y, si se pregunta, plataforma **Linux**.
4. Si aparece confirmación de huella, contrástala como en G05.
5. Espera la instalación de VS Code Server.
6. Comprueba en la esquina inferior izquierda una indicación similar a **SSH: fp-analytics**.
7. Abre **File → Open Folder** y selecciona `/home/ubuntu/practicas-aws`.
8. Confirma confianza solo para tu carpeta de práctica.

**Resultado esperado:** el explorador de archivos muestra la carpeta remota, no una carpeta de Windows.

## 5. Comprueba edición y terminal

1. Crea `comprobacion.txt` en el explorador remoto.
2. Escribe `Editado desde VS Code en Ubuntu EC2` y guarda con Ctrl+S.
3. Abre **Terminal → New Terminal** en esa ventana remota.
4. Ejecuta:

```bash
whoami
pwd
cat /home/ubuntu/practicas-aws/comprobacion.txt
```

`whoami` debe dar `ubuntu`; `pwd` identifica la carpeta; `cat` confirma el archivo guardado en EC2.

> **Qué está ocurriendo**  
> La interfaz está en Windows, pero la terminal y la carpeta pertenecen a Ubuntu. Si abres otra ventana local de VS Code, su terminal podría ser PowerShell: comprueba el indicador de conexión.

## 6. Si algo falla

| Situación | Acción |
|---|---|
| PowerShell SSH falla | Vuelve a G05; la extensión no corrige problemas de red o clave |
| Descarga de VS Code Server falla | Revisa salida de Remote - SSH, espacio y conectividad; no desactives SSL |
| Se queda sin memoria o va muy lento | Comprueba `free -h`; cierra otros procesos y pide al docente capacidad permitida |
| Sistema no compatible | Comprueba Ubuntu LTS y arquitectura; no sustituyas por Amazon Linux |
| Host no aparece | Revisa el archivo config elegido por VS Code y la extensión `.txt` |
| Tras reiniciar EC2 no conecta | Actualiza HostName con la nueva IP y revisa Mi IP en el grupo |

Las distribuciones Ubuntu recientes y las bibliotecas del sistema deben cumplir los requisitos de Remote Development. La Ubuntu antigua mencionada por la terminal del Lab no es una imagen adecuada de referencia para esta instancia. [Microsoft: requisitos Linux](https://code.visualstudio.com/docs/remote/linux).

## 7. Entrega, cierre y resumen

Guarda todos los archivos. Entrega evidencia recortada del indicador SSH y del archivo, sin claves ni identificadores. Para salir ejecuta **Remote-SSH: Close Remote Connection** o cierra la ventana remota. Detén EC2 si termina la clase y pulsa End Lab.

**Resumen:** editas y ejecutas en Ubuntu desde Windows. **Siguiente:** G07, un servicio web. **Reto:** comprueba mediante SSH convencional que el archivo editado sigue en la misma ruta.

