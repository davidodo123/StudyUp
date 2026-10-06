# G02 · Red y configuración básica del laboratorio

**Curso:** Curso de Especialización FP Aprendizaje Automático — Instalación, Despliegue y Explotación de Sistemas  
**Módulo:** Explotación de servicios de procesamiento y analítica de datos  
**Entorno:** Windows 11 → AWS Academy Learner Lab → Ubuntu en EC2  
**Duración orientativa:** 45–60 minutos  
**Requisitos:** G01 terminada; región autorizada por el docente.  
**Recursos:** VPC y subred existentes; un Security Group propio.  
**Resultado:** Red de referencia identificada y acceso SSH preparado sin crear aún EC2.

## Antes de empezar

1. Inicia el Learner Lab con **Start Lab** y espera a que esté activo.
2. Abre la consola AWS desde el enlace del Lab. Usa **París (`eu-west-3`) solo si está autorizada**, según G01 y las instrucciones actuales. Si se utiliza otra región, mantenla en toda la práctica.
3. Comprueba presupuesto y tiempo restante. Las cifras dependen de tu laboratorio; no se presupone gratuidad. La aparición de un servicio no garantiza permiso para utilizarlo.
4. Sigue el lugar de ejecución indicado: **PowerShell de Windows**, **terminal del Learner Lab** o **terminal Ubuntu de EC2**. No intercambies sus comandos.
5. En bloques con varias órdenes, ejecuta una línea cada vez, excepto los bloques de creación de archivos que se indique pegar completos. No copies los marcadores de Markdown.

> **Importante · Seguridad**  
> No compartas Account ID, UserId, ARN completo, Access Key, Secret Key, Session Token ni archivos privados `.pem`. No subas claves a EC2, S3, repositorios o herramientas de IA. Entrega resultados resumidos y capturas recortadas. Los permisos se conceden mediante los roles previstos por el laboratorio; no los amplíes para eludir una restricción.

## 1. Objetivos y esquema de trabajo

Identificarás VPC, subred, tabla de rutas e Internet Gateway. Prepararás un grupo de seguridad que permitirá SSH únicamente desde tu IP pública.

```text
Windows 11 → Internet → Internet Gateway → subred pública → futura EC2 Ubuntu
                                                         ↑ Security Group
```

Una **VPC** es una red virtual; una **subred** es una parte de esa red; una **ruta** indica por dónde sale el tráfico. Una subred pública tiene una ruta al Internet Gateway. La futura instancia necesitará además IP pública y permisos de tráfico. [AWS: acceso a Internet en una VPC](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Internet_Gateway.html).

## 2. Localiza una red existente

1. En la consola busca **VPC** y abre el servicio.
2. Comprueba la región del selector.
3. Abre **Your VPCs / Tus VPC**.
4. Selecciona la VPC que indique el docente. Si hay una predeterminada y el docente la ha previsto, utiliza esa.
5. Anota su ID únicamente en tu inventario local.
6. En **Subnets / Subredes**, filtra por esa VPC.
7. Selecciona una subred candidata y anota su ID y zona de disponibilidad.
8. En sus detalles, abre la tabla de rutas asociada. Comprueba que existe una ruta `0.0.0.0/0` cuyo destino es un Internet Gateway `igw-…` y está activa.
9. En **Internet gateways**, comprueba que ese gateway está conectado a la misma VPC.

**Resultado esperado:** una VPC y una subred pública identificadas. No hace falta crear una nueva red para cada alumno.

> **Qué está ocurriendo**  
> `0.0.0.0/0` significa cualquier destino IPv4 en una tabla de rutas. No es una regla de entrada que permita a todo Internet conectarse a EC2. Ruta, IP pública y Security Group cumplen funciones diferentes.

> **Si algo falla**  
> Si no hay VPC, no hay ruta al gateway o no puedes leer la configuración, registra el caso y avisa al docente. No crees NAT Gateway ni cambies rutas de redes compartidas. La G04 queda pendiente hasta disponer de la red prevista.

## 3. Prepara un Security Group para SSH

1. Abre **EC2 → Network & Security → Security Groups**.
2. Pulsa **Create security group / Crear grupo de seguridad**.
3. Nombre: `fp-analytics-sg`. Si la cuenta es compartida, añade el código de alumno acordado, sin nombre completo ni datos personales.
4. Descripción: `SSH de las practicas FP desde la IP del alumno`.
5. Selecciona **la VPC identificada en el paso 2**.
6. Añade una única regla de entrada: tipo **SSH**, protocolo **TCP**, puerto **22**, origen **My IP / Mi IP**.
7. Comprueba que el origen es una IPv4 concreta seguida de `/32`. No selecciones Anywhere ni `0.0.0.0/0` para SSH.
8. En salida conserva la configuración prevista por el docente. Para esta ruta de prácticas, la salida habitual permite descargas de Ubuntu, Python y VS Code por Internet. No modifiques grupos compartidos.
9. Crea el grupo y anota su ID localmente.

**Resultado esperado:** un grupo propio con una regla SSH desde tu IP. Todavía no está asociado a una instancia.

> **Qué está ocurriendo**  
> El Security Group filtra el tráfico de las interfaces de red asociadas. `/32` representa una única IPv4. En una red de centro con NAT, varios alumnos pueden compartir esa IP pública; la autenticación SSH por clave sigue siendo necesaria. [AWS: grupos de seguridad](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html).

> **Si algo falla**  
> Si cambias de red, VPN o conexión doméstica, tu IP pública puede cambiar: actualiza **solo el origen** de la regla SSH de tu grupo. Si no tienes una IPv4 pública utilizable o el centro bloquea el puerto 22, pide la solución de conectividad prevista por el docente; no abras todos los puertos.

## 4. Comprobación sin crear recursos

En la **terminal del Learner Lab**, sustituye los dos textos entre comillas por los IDs de tu inventario y usa tu región autorizada:

```bash
aws ec2 describe-subnets --subnet-ids 'SUBNET_ID_REAL' --region eu-west-3 --query 'Subnets[].{VPC:VpcId,Estado:State,Zona:AvailabilityZone}' --output table --no-cli-pager
aws ec2 describe-security-groups --group-ids 'SG_ID_REAL' --region eu-west-3 --query 'SecurityGroups[].IpPermissions' --output json --no-cli-pager
```

`describe-subnets` comprueba los datos de la subred; `describe-security-groups` consulta las reglas de entrada; `--query` limita la salida; `--region` fija dónde se consulta. No son pruebas de permiso para lanzar EC2. Si falla la lectura CLI pero puedes verificar los datos en consola, registra esa diferencia.

## 5. Entrega, cierre y resumen

- Entrega un esquema con VPC, subred pública y regla TCP/22 desde Mi IP, sin IDs completos.
- Conserva el grupo para G04; no elimines redes del laboratorio.
- Pulsa **End Lab** y confirma el cierre. El grupo creado permanece según las condiciones del Lab.

**Has aprendido:** la conectividad necesita una ruta válida, una dirección alcanzable y reglas adecuadas. **Siguiente:** G03, claves privadas en Windows 11. **Reto:** explica por qué una instancia con IP pública podría seguir siendo inaccesible.
