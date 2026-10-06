# G01 · Primeros pasos y configuración básica de AWS Academy Learner Lab

**Curso:** Curso de Especialización FP Aprendizaje Automático — Instalación, Despliegue y Explotación de Sistemas  
**Módulo:** Explotación de servicios de procesamiento y analítica de datos  
**Equipo del alumnado:** Windows 11  
**Nivel inicial:** conocimientos básicos de AWS  
**Duración orientativa:** 45–60 minutos  
**Región de referencia:** Europa (París), `eu-west-3`, condicionada a las restricciones del laboratorio.

## 1. Qué vas a aprender

Al finalizar podrás iniciar y cerrar una sesión del Learner Lab, entrar en la consola web de AWS, comprobar tu identidad temporal, consultar regiones y preparar la región de trabajo. También sabrás registrar una limitación sin confundirla con un error de tus comandos.

Esta preparación será la base para las prácticas de procesamiento y analítica de datos. En esta guía **no crearás instancias EC2, claves SSH, redes ni otros recursos**. Las guías posteriores abordarán Ubuntu en EC2, claves `.pem`, SSH y VS Code Remote - SSH. No se utilizará Amazon Linux como sistema de las instancias de las prácticas.

### Punto de partida comprobado por el docente

| Comprobación previa | Resultado observado | Qué queda por comprobar |
|---|---|---|
| Identidad mediante STS | Sesión con `assumed-role/voclabs` | Que tu sesión esté activa |
| Región en el archivo de configuración | `us-east-1` | Que tu entorno presente el mismo valor |
| Lista de regiones | Incluye `eu-west-3` | Permisos efectivos para operaciones en París |
| Herramienta AWS CLI | Versión `2.1.11` | Versión disponible en tu sesión |

Estos datos proceden del laboratorio del docente. No son una garantía de que todas las cuentas del alumnado tengan la misma configuración.

> **Importante**  
> París es la referencia elegida por su proximidad a España. No afirmamos que sea la región más cercana disponible ni que esté autorizada en tu Learner Lab. El código de París es `eu-west-3`, según la [lista oficial de regiones de AWS](https://docs.aws.amazon.com/global-infrastructure/latest/regions/aws-regions.html).

## 2. Prepara Windows 11 y tu registro de trabajo

1. Abre un navegador actualizado, como Microsoft Edge o Google Chrome.
2. Ten disponibles tus datos de acceso a AWS Academy y el curso indicado por el docente.
3. En el Explorador de archivos de Windows crea una carpeta para las prácticas, por ejemplo, dentro de **Documentos**, llamada `Practicas_AWS`.
4. Abre el Bloc de notas y guarda un archivo llamado `G01_comprobaciones.txt` dentro de esa carpeta.
5. Copia en él la ficha de comprobaciones del apartado 12. La completarás durante la práctica.

> **Qué está ocurriendo**  
> Windows 11 es tu equipo de trabajo, pero en esta G01 ejecutarás los comandos en la **terminal integrada en la página del Learner Lab**. Esa terminal utiliza un entorno Linux remoto. No es una instancia EC2 tuya ni la terminal PowerShell de Windows.

No necesitas instalar AWS CLI, WSL, Ubuntu ni VS Code para esta guía. Tampoco necesitas introducir una tarjeta bancaria ni crear una cuenta personal de AWS.

### Norma de seguridad para toda la práctica

No compartas **Account ID, UserId, ARN completo, Access Key, Secret Key, Session Token ni claves privadas `.pem`** en entregas, chats, repositorios, herramientas de IA o capturas. Si una captura los muestra, recórtala u ocúltalos antes de enviarla. Los identificadores no son contraseñas, pero en este curso también los protegeremos.

Guarda únicamente resultados resumidos: «identidad temporal comprobada», región, versión y nombre del error sin información identificativa. No abras ni copies archivos de credenciales para completar esta guía. Si expones una credencial o una clave privada, informa al docente de inmediato para que gestione su invalidación o sustitución; borrar el mensaje no basta.

## 3. Entra en el Learner Lab y revisa sus instrucciones

1. Accede a AWS Academy mediante el enlace facilitado por el centro.
2. Inicia sesión con tu usuario de alumno.
3. Abre el curso correspondiente al **AWS Academy Learner Lab**.
4. Busca en sus módulos o contenidos el enlace al laboratorio y ábrelo.
5. Localiza el panel con los controles de sesión, normalmente **Start Lab**, **End Lab** y el enlace **AWS**.
6. Lee las instrucciones del laboratorio. Busca apartados equivalentes a **Region restriction**, **Service usage and other restrictions** y **Environment Overview**. Los nombres y la distribución pueden variar.
7. Anota las regiones autorizadas que indiquen esas instrucciones, el presupuesto disponible y la duración de sesión mostrada, si aparecen.

> **Importante**  
> Las instrucciones de tu laboratorio son la referencia para sus restricciones. No supongas un presupuesto, una duración ni una lista de servicios universal. Si París figura como no autorizada, registra esa limitación y utiliza únicamente la región que indique el docente. No intentes activar regiones ni modificar políticas para eludirla.

> **Si algo falla**  
> Si no aparece el curso, comprueba que has entrado con el usuario correcto. Si el enlace no se abre, permite ventanas emergentes para el sitio de AWS Academy y vuelve a intentarlo. Si sigue faltando el acceso, comunica al docente «no puedo acceder al Learner Lab», sin enviar tus credenciales.

## 4. Inicia la sesión del laboratorio

1. Pulsa **Start Lab** una sola vez.
2. Espera a que el panel indique que la sesión está preparada. En muchas interfaces el indicador junto a AWS cambia a verde.
3. Comprueba el tiempo disponible y el estado de la sesión.
4. Mantén abierta esta pestaña: volverás a ella para usar la terminal y finalizar.

**Resultado esperado:** sesión activa y acceso AWS disponible.

> **Qué está ocurriendo**  
> El entorno prepara el acceso temporal al laboratorio. La sesión del navegador de AWS Academy y la sesión de la consola de AWS son accesos relacionados, pero diferentes.

> **Si algo falla**  
> Si el estado sigue en preparación, espera unos minutos y revisa el mensaje del panel. No pulses repetidamente Start Lab ni uses Reset. Si aparece presupuesto agotado, laboratorio caducado o cuenta deshabilitada, anota el mensaje resumido y avisa al docente. No lo soluciones creando una cuenta personal de AWS.

## 5. Abre la consola web de AWS

1. Con el laboratorio activo, pulsa el enlace **AWS** o **AWS Management Console**.
2. Si se abre una pestaña nueva, mantenla junto a la del Learner Lab.
3. Comprueba que ves la consola de AWS con su buscador de servicios.
4. Localiza el selector de región, normalmente en la parte superior derecha.
5. Anota la región inicial sin copiar datos de la cuenta. Puede ser **N. Virginia (`us-east-1`)**.

**Resultado esperado:** acceso a AWS desde el navegador sin introducir claves de API.

> **Si algo falla**  
> Si aparece una pantalla para iniciar sesión en una cuenta personal, cierra esa pestaña y vuelve a abrir AWS desde el laboratorio activo. Si tienes varias cuentas AWS abiertas, usa una ventana privada para entrar en AWS Academy y repetir este acceso. Si recibes «sesión caducada», vuelve al panel del Lab y comprueba su estado antes de reabrir la consola.

## 6. Localiza la terminal del Learner Lab

1. Regresa a la pestaña del laboratorio.
2. Busca su terminal integrada. Si está contraída, despliega el panel correspondiente. Consulta el apartado de instrucciones sobre la terminal si no la encuentras.
3. Haz clic dentro de la terminal. Debe aparecer un cursor junto a un indicador similar a `usuario@servidor:~$`.
4. Copia cada comando de esta guía **sin los marcadores del bloque** y pulsa **Intro**.
5. Ejecuta un comando cada vez y espera a que reaparezca el indicador de la terminal.

> **Importante**  
> Todos los comandos siguientes se ejecutan en esta terminal Linux del navegador. No los pegues en PowerShell, en el buscador de la consola AWS ni en AWS CloudShell. No copies el `$` del indicador ni las salidas de ejemplo. Los comandos están en una sola línea para facilitar su uso.

> **Si algo falla**  
> Para cancelar una entrada incompleta, pulsa **Ctrl+C**. Si estás viendo una salida paginada con `(END)`, pulsa **q** para volver a la terminal. Si no existe terminal integrada en tu edición del laboratorio, registra la incidencia y solicita al docente la vía prevista; no exportes credenciales por tu cuenta.

## 7. Comprueba la herramienta y la identidad

### 7.1. Versión de AWS CLI

```bash
aws --version
```

**Qué significa:** `aws` ejecuta AWS CLI, la herramienta para comunicarse con AWS mediante comandos; `--version` muestra su versión y datos de su entorno, sin crear recursos.

**Resultado de referencia observado por el docente:**

```text
aws-cli/2.1.11 Python/3.7.3 Linux/4.4.0-210-generic exe/x86_64.ubuntu.16 prompt/off
```

Tu salida puede ser distinta. Anota solo la versión de AWS CLI. La referencia a Linux o Ubuntu describe esta terminal, no tu Windows 11 ni una instancia EC2 creada por ti. No actualices el software del entorno administrado durante esta práctica.

> **Si algo falla**  
> Si aparece `aws: command not found`, comprueba que estás en la terminal del Learner Lab. Si lo estás, registra el error y avisa al docente.

### 7.2. Identidad temporal

```bash
aws sts get-caller-identity --no-cli-pager
```

**Qué significa:** `sts` es el servicio de tokens de seguridad; `get-caller-identity` consulta la identidad de las credenciales utilizadas; `--no-cli-pager` evita abrir un visor paginado.

**Ejemplo anonimizado, no una salida para copiar:**

```json
{
  "UserId": "[OCULTO]",
  "Account": "[OCULTO]",
  "Arn": "arn:aws:sts::[CUENTA_OCULTA]:assumed-role/voclabs/[SESION_OCULTA]"
}
```

Comprueba visualmente los tres campos. `Account` identifica la cuenta, `UserId` identifica al llamante y `Arn` identifica la identidad utilizada. En el laboratorio comprobado se observa `assumed-role/voclabs`: estás usando una sesión de rol, no acceso de administrador ilimitado. Otro nombre de rol debe contrastarse con el docente.

> **Qué está ocurriendo**  
> Esta consulta comprueba tu identidad, pero no demuestra que puedas crear recursos ni utilizar París. [Referencia de AWS: get-caller-identity](https://docs.aws.amazon.com/cli/latest/reference/sts/get-caller-identity.html).

> **Si algo falla**  
> Ante `ExpiredToken`, `InvalidClientTokenId` o `Unable to locate credentials`, revisa que el Lab esté activo y vuelve a abrir su terminal según sus instrucciones. Las credenciales temporales pueden caducar. No ejecutes el asistente `aws configure` ni introduzcas claves personales. Si el error continúa, avisa al docente.

## 8. Consulta la región inicial y las regiones visibles

### 8.1. Lee la región guardada

```bash
aws configure get region
```

**Qué significa:** `configure get region` lee el valor de región del archivo de configuración de AWS CLI. En el entorno observado devolvió:

```text
us-east-1
```

Si no imprime nada, puede no existir un valor guardado. Este comando no muestra necesariamente la región efectiva de todas las peticiones: no resuelve las variables de entorno ni las opciones de cada comando. [Referencia de AWS: configure get](https://docs.aws.amazon.com/cli/latest/reference/configure/get.html).

### 8.2. Lista las regiones que devuelve EC2

```bash
aws ec2 describe-regions --region us-east-1 --query "Regions[].RegionName" --output table --no-cli-pager
```

| Parte | Significado |
|---|---|
| `ec2 describe-regions` | Consulta regiones habilitadas para la cuenta, sin crear instancias |
| `--region us-east-1` | Dirige esta petición a la región inicial de referencia |
| `--query "Regions[].RegionName"` | Selecciona solo los nombres de región de la respuesta |
| `--output table` | Presenta el resultado como tabla |
| `--no-cli-pager` | Muestra la salida directamente |

Busca `eu-west-3`. El orden y la cantidad de filas pueden cambiar. [Referencia de AWS: describe-regions](https://docs.aws.amazon.com/cli/latest/reference/ec2/describe-regions.html).

> **Importante**  
> Hay tres comprobaciones distintas: una región puede ser **visible** en el selector o en una lista; estar **habilitada en la cuenta**; y permitir **una operación concreta** con tu rol. La lista no demuestra autorización para desplegar servicios allí. Tampoco una consulta correcta garantiza permisos de creación. Si las instrucciones prohíben París, no hagas la prueba del apartado siguiente.

> **Si algo falla**  
> Si la consulta devuelve `AccessDenied` o `UnauthorizedOperation`, anota «consulta de regiones denegada». No significa que todas las regiones estén deshabilitadas. Si `us-east-1` no está autorizada en tu edición, usa en esta consulta la región indicada por el docente.

## 9. Comprueba una operación de lectura en París

**Haz este apartado solo si las instrucciones no excluyen París.** Si hay dudas sobre sus restricciones, detente aquí y consúltalas con el docente.

```bash
aws ec2 describe-vpcs --region eu-west-3 --query "Vpcs[].{Predeterminada:IsDefault,Estado:State}" --output json --no-cli-pager
```

**Qué significa:** `describe-vpcs` consulta redes virtuales existentes; `--region eu-west-3` dirige esta operación a París; la consulta selecciona si cada red es predeterminada y su estado; `--output json` permite distinguir claramente una lista vacía. No crea ni modifica redes. [Referencia de AWS: describe-vpcs](https://docs.aws.amazon.com/cli/latest/reference/ec2/describe-vpcs.html).

**Ejemplo si existe una VPC predeterminada accesible:**

```json
[
  {
    "Predeterminada": true,
    "Estado": "available"
  }
]
```

También puede devolver varias redes o `[]`. **Una lista vacía sin error es una consulta correcta**: no se han devuelto VPC en esa región. No crees una para rellenar el resultado.

### Decide qué registrar

| Resultado | Interpretación | Siguiente paso |
|---|---|---|
| Respuesta correcta, incluso `[]` | Esta operación de lectura funciona en París | Anota «lectura de VPC en París correcta»; pasa al apartado 10 si las instrucciones la autorizan |
| `AccessDenied` o `UnauthorizedOperation` | La operación está denegada; puede ser por región, acción o políticas | Anota el error; no configures París como región de trabajo sin aclararlo |
| `ExpiredToken` | Problema de vigencia de la sesión | Revisa el Lab y repite cuando el acceso esté renovado |
| Error de conexión o endpoint | No demuestra una restricción de permisos | Revisa conexión y escritura de `eu-west-3`; consulta al docente si persiste |

Si la consulta falla por permisos y **las instrucciones autorizan `us-east-1`**, puedes repetir exactamente la misma consulta sustituyendo únicamente `--region eu-west-3` por `--region us-east-1`. Registra ambos resultados.

> **Qué está ocurriendo**  
> Si la lectura funciona en N. Virginia y se deniega en París, hay un indicio de restricción regional, pero no un diagnóstico definitivo. El docente debe contrastarlo con las instrucciones. Si se deniega en ambas, también puede estar restringida la acción. No modifiques IAM ni intentes sortear las políticas.

## 10. Alinea la región de la consola y de la terminal

### 10.1. Elige la región de trabajo

Utiliza **París (`eu-west-3`)** si las instrucciones la autorizan y la comprobación anterior funciona. Si está restringida o el resultado sigue sin aclararse, registra la incidencia y utiliza la región autorizada que indique el docente. Si aún no hay una región confirmada, deja pendiente este apartado: puedes completar el registro y cerrar correctamente el laboratorio.

### 10.2. Configura la consola web

1. Vuelve a la pestaña de la consola AWS.
2. Abre el selector de región.
3. Selecciona **Europa (París)** si es la región confirmada.
4. Comprueba que el selector muestra París o `eu-west-3`.
5. No pulses botones para crear recursos.

Si el selector no ofrece París o muestra una restricción, registra el resultado y vuelve al docente. Algunos servicios son globales y no presentan el selector de la misma forma.

### 10.3. Configura la terminal

Vuelve a la terminal del Learner Lab. Para París ejecuta:

```bash
aws configure set region eu-west-3
```

**Qué significa:** guarda París como región predeterminada en el archivo de configuración de AWS CLI. Habitualmente no imprime ningún mensaje cuando termina correctamente. No modifica credenciales ni concede permisos. [Referencia de AWS: configure set](https://docs.aws.amazon.com/cli/latest/reference/configure/set.html).

Comprueba el valor guardado:

```bash
aws configure get region
```

**Resultado esperado:** `eu-west-3`.

Para alinear también las variables de región de esta terminal Linux, ejecuta cada línea por separado:

```bash
export AWS_REGION=eu-west-3
export AWS_DEFAULT_REGION=eu-west-3
```

**Qué significa:** `export` establece variables de entorno para esta terminal y sus procesos. Ambas indican París; no son credenciales. No suele haber salida. Su duración se limita a este entorno de terminal. Compruébalas:

```bash
printf 'AWS_REGION=%s\nAWS_DEFAULT_REGION=%s\n' "$AWS_REGION" "$AWS_DEFAULT_REGION"
```

**Resultado esperado:**

```text
AWS_REGION=eu-west-3
AWS_DEFAULT_REGION=eu-west-3
```

`printf` imprime exclusivamente esas dos variables de región. No utilices comandos para mostrar todas las variables del entorno: podrían contener credenciales. [Referencia de AWS: variables de entorno](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-envvars.html).

Si el docente confirma otra región, sustituye `eu-west-3` por ese mismo código en los tres comandos de configuración y selecciónala también en la consola. No mezcles códigos.

> **Importante**  
> Cambiar la región en la consola no cambia la terminal, ni a la inversa. En las peticiones de AWS CLI, `--region` prevalece sobre las variables de entorno y el archivo de configuración. Por eso las comprobaciones anteriores especifican la región expresamente. Al volver otro día, comprueba estos ajustes otra vez: el entorno puede regenerarse.

## 11. Limitaciones y errores habituales

El Learner Lab es un entorno educativo administrado. Comprueba las condiciones de tu edición antes de cada práctica. La [guía de AWS Academy para docentes](https://d1.awsstatic.com/AWS%20Academy%20Learner%20Lab%20Educator%20Guide.pdf) aporta contexto general, pero no sustituye las instrucciones actuales de tu laboratorio.

| Situación posible | Cómo actuar |
|---|---|
| Región o servicio restringido | Registra la operación y la región; utiliza solo lo autorizado |
| IAM limitado o rol sin permisos administrativos | No crees usuarios, claves permanentes ni políticas para resolverlo |
| Límites de tipos, capacidad o número de recursos | Se comprobarán antes de desplegar en las siguientes guías |
| Presupuesto agotado o indicadores con retraso | Revisa el panel del Lab y comunica la incidencia; no interpretes un saldo antiguo como garantía |
| Sesión temporal caducada | Comprueba el estado del Lab y renueva el acceso mediante su interfaz |
| Panel de facturación denegado | Utiliza el presupuesto del Lab; no necesitas permisos de facturación para G01 |
| Recursos que no aparecen | Comprueba primero región y filtros antes de concluir que se han borrado |
| Error SSL o conexión desde la red del centro | Comunícalo al docente; no desactives la verificación SSL |

> **Si algo falla**  
> Para pedir ayuda, envía: paso de la guía, comando sin datos sensibles, región utilizada, nombre del error y estado del laboratorio. Por ejemplo: «G01, paso 9; describe-vpcs en eu-west-3; UnauthorizedOperation; Lab activo». No envíes la salida íntegra si contiene ARN, cuenta o datos de sesión.

## 12. Ficha de comprobaciones y entrega

Completa esta ficha en tu archivo local. Una limitación documentada es un resultado válido; no inventes una comprobación correcta.

```text
G01 — Registro de comprobaciones
Fecha:
Laboratorio y curso (sin identificadores de cuenta):
Instrucciones de restricciones revisadas: sí / pendiente
Regiones autorizadas según las instrucciones:
Estado inicial del Lab: activo / incidencia
Consola web abierta desde el Lab: sí / incidencia
Versión AWS CLI:
Identidad temporal comprobada: sí / incidencia (sin copiar identificadores)
Región inicial del archivo de configuración:
eu-west-3 aparece en la lista: sí / no / consulta denegada
Lectura de VPC en París: correcta / denegada / otro error / no realizada por restricción
Consulta de comparación, si procede:
Región de trabajo confirmada:
Región en la consola:
Región guardada y variables de terminal alineadas: sí / pendiente
Incidencias y pasos pendientes (sin datos sensibles):
Recursos creados durante G01: ninguno
End Lab ejecutado y cierre confirmado: sí / incidencia
```

Antes de entregar, revisa que no haya credenciales ni identificadores completos. Adjunta solo capturas recortadas si el docente las solicita. No se exige una captura de la respuesta íntegra de STS.

## 13. Finaliza correctamente el laboratorio

1. Guarda la ficha en tu equipo Windows 11. No dependas de archivos guardados únicamente en la terminal remota.
2. Comprueba que no has creado recursos durante esta G01. Si pulsaste por error una acción de creación, informa al docente para revisar qué ocurrió.
3. Vuelve a la pestaña del Learner Lab.
4. Pulsa **End Lab**.
5. Confirma el cierre si la interfaz lo solicita.
6. Espera hasta que el panel indique que la sesión ha finalizado o está inactiva.
7. Completa la última línea de la ficha y guarda el archivo.
8. Cierra la pestaña de la consola AWS y después la del laboratorio. En un equipo compartido, cierra también la sesión de AWS Academy.

> **Importante**  
> Cerrar el navegador no equivale a pulsar End Lab. Tampoco presupongas que End Lab borra todos los recursos o elimina cualquier consumo: la persistencia y el cierre de recursos dependen del laboratorio y del servicio. En las guías de despliegue habrá pasos específicos de parada o limpieza. **Reset no es un botón de cierre** y puede eliminar trabajo.

> **Si algo falla**  
> Si no puedes confirmar el cierre, revisa el estado del panel y comunica la incidencia al docente. No marques la sesión como finalizada solo porque has cerrado la pestaña.

## 14. Resumen y comprobación final

- [ ] He abierto el entorno desde AWS Academy y he leído sus restricciones.
- [ ] Distingo Windows 11, la consola web y la terminal Linux del Lab.
- [ ] He comprobado versión e identidad sin compartir datos sensibles.
- [ ] Entiendo que ver París no garantiza permisos para trabajar allí.
- [ ] He probado solo una operación de lectura cuando estaba permitido, o he registrado la restricción.
- [ ] He alineado la región confirmada en consola y terminal, o he documentado por qué queda pendiente.
- [ ] No he creado EC2, claves SSH ni otros recursos.
- [ ] He guardado mi registro y he confirmado End Lab.

**Preguntas de autoevaluación:**

1. ¿Por qué `describe-regions` no demuestra que puedas crear una instancia en París?
2. ¿Cambiar la región en la consola cambia también AWS CLI?
3. ¿Qué debes hacer si aparece `ExpiredToken`?
4. ¿Por qué no basta con cerrar la pestaña para terminar?

**Respuestas orientativas:** la lista no prueba los permisos de una acción de creación; consola y CLI se configuran por separado; hay que revisar la sesión temporal y renovar el acceso desde el Lab; el cierre se realiza con End Lab y se confirma en el panel.

**Siguiente etapa:** utilizar la región autorizada y comprobar la configuración necesaria para preparar una instancia Ubuntu en EC2. La creación de instancias, las claves `.pem`, SSH y VS Code se desarrollarán en guías posteriores.
