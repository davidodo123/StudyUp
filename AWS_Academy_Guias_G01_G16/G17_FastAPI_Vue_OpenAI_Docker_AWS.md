# G17 · Práctica: asistente de IA con FastAPI, Vue y Docker en AWS

**Curso:** Especialización FP Aprendizaje Automático — Instalación, Despliegue y Explotación de Sistemas.  
**Módulo:** Explotación de servicios de procesamiento y analítica de datos.  
**Entorno:** Windows 11 → SSH / VS Code → EC2 Ubuntu → Docker Compose.  
**Duración orientativa:** 4 sesiones de 90 minutos, más la ampliación de publicación HTTPS.  
**Entrega:** aplicación, comprobaciones y memoria sin secretos.

## 1. Dónde encaja y qué vas a aprender

Esta práctica ocupa el puesto G17 por combinar desarrollo, despliegue y explotación. Necesitas G01–G07, conocer Python, HTTP/JSON y conceptos básicos de TypeScript. G09–G10 son necesarios únicamente para la alternativa con Secrets Manager. No necesitas haber completado Athena, Glue o Spark.

Al terminar podrás:

1. Explicar qué ejecuta el navegador y qué ejecuta el servidor.
2. Modificar una API FastAPI y una interfaz Vue 3 con TypeScript y Composition API.
3. Probar la aplicación sin gastar dinero mediante respuestas simuladas.
4. Crear dos imágenes y desplegarlas en EC2 Ubuntu con Docker Compose.
5. Activar OpenAI manteniendo la clave fuera del navegador, del repositorio y de las imágenes.
6. Comprobar funcionamiento, errores y cierre; identificar qué falta para añadir Clerk.

> **Importante**  
> Se proporciona un proyecto completo en `G17_app.zip`. Descomprímelo conservando su estructura. La guía no presupone que ya tengas una aplicación hecha. **Clerk todavía no está implementado**: esta versión usa el acceso SSH al laboratorio para restringir el uso real de OpenAI.

## 2. Arquitectura y decisiones de la práctica

```text
Windows 11, navegador
       │ http://127.0.0.1:8080
       │ túnel SSH cifrado hasta Ubuntu
       ▼
EC2 Ubuntu, puerto 8080 vinculado solo a 127.0.0.1
       │
       ▼
frontend: Nginx + Vue compilado
       │ /api/*, red interna de Compose
       ▼
backend: FastAPI ── HTTPS ── OpenAI Responses API
       │
       └── /run/secrets/openai_api_key, solo lectura
```

Vue recoge una pregunta y muestra una respuesta. FastAPI valida la petición, aplica límites y llama a OpenAI. Nginx sirve los archivos estáticos y reenvía `/api/` al backend. El navegador usa un único origen; no necesita conocer la dirección interna de FastAPI.

| Modalidad | Acceso | Clave real | Uso |
|---|---|---|---|
| Simulada inicial | Túnel SSH | No | Desarrollo y pruebas |
| OpenAI | Túnel SSH | Solo backend | Prueba supervisada con consumo |
| Demostración pública opcional | HTTPS con dominio | No | Mostrar interfaz y respuesta simulada |
| Futura con Clerk | HTTPS y usuario autenticado | Solo backend | Requiere implementar y probar autenticación |

> **Qué está ocurriendo**  
> `AUTH_MODE=lab` no es un inicio de sesión web. La barrera de acceso es SSH y el puerto vinculado a loopback. Validar el encabezado `Origin` ayuda frente a peticiones de otras páginas, pero **no autentica usuarios**. El servidor rechaza la combinación declarada de acceso público y OpenAI real. No cambies ese control ni publiques el puerto privado para saltártelo.

## 3. Comprobaciones previas del docente

Antes de la clase, confirma en el Learner Lab la región y el lanzamiento de EC2 Ubuntu. Usa `eu-west-3` si está permitida. Que aparezca en `describe-regions` no prueba que se autorice crear recursos allí. Si una política lo impide, el docente adapta toda la práctica a una región autorizada.

Comprueba espacio y memoria en Ubuntu; las construcciones consumen más recursos que servir la aplicación:

```bash
free -h
df -h /
uname -m
```

`free` muestra memoria; `df`, espacio del disco raíz; `uname -m`, arquitectura. Trabajaremos con Ubuntu de 64 bits y una instancia permitida que soporte ambas construcciones. No hay un tamaño confirmado para tu Academy. Si hay poca RAM, cierra Jupyter/Spark y otros procesos; el docente debe decidir un tipo autorizado o construir en otro entorno compatible. No amplíes recursos sin revisar presupuesto.

La conexión de salida necesita resolver DNS y alcanzar los repositorios de paquetes y OpenAI por HTTPS. No hace falta abrir puertos de entrada hacia OpenAI. No se utilizan ECS, ECR, un balanceador ni roles IAM nuevos como requisito.

> **Importante**  
> OpenAI requiere un proyecto y una clave con acceso al modelo elegido. Su consumo se factura fuera del presupuesto de AWS Academy; una suscripción de ChatGPT no sustituye la configuración de la API. El docente decidirá quién administra las claves y el gasto. Puedes completar toda la práctica en modo simulado.

## 4. Llevar el proyecto de Windows a Ubuntu

### 4.1. En Windows 11 — PowerShell

Descarga `G17_app.zip` a Descargas. Comprueba primero el alias de G06:

```powershell
ssh fp-analytics
```

Debes llegar a un terminal de Ubuntu. Escribe `exit` para volver a PowerShell. Después copia el paquete:

```powershell
scp "$env:USERPROFILE\Downloads\G17_app.zip" fp-analytics:/home/ubuntu/
```

`scp` transfiere el ZIP por SSH; el alias aporta usuario, IP y archivo `.pem`. Si el navegador cambió el nombre del ZIP, sustituye la ruta. No copies la clave SSH dentro del proyecto. Si la IP de EC2 cambió, actualiza el alias antes de copiar.

### 4.2. En Ubuntu — terminal remoto de VS Code

Abre `fp-analytics` con Remote - SSH como en G06 y ejecuta:

```bash
sudo apt update
sudo apt install -y unzip python3-venv curl ca-certificates
mkdir -p ~/practicas-aws
unzip ~/G17_app.zip -d ~/practicas-aws
cd ~/practicas-aws/G17_app
pwd
ls
```

`apt update` actualiza el catálogo; `apt install` añade herramientas; `mkdir -p` crea la carpeta si falta; `unzip` extrae; `cd` cambia de carpeta; `pwd` confirma dónde estás. Debes ver `backend`, `frontend`, `deploy` y archivos `compose*.yaml`. Si ya existe una práctica modificada, guarda una copia antes de extraer; no aceptes sobrescribirla a ciegas.

Usa **Archivo → Abrir carpeta** en VS Code para abrir `/home/ubuntu/practicas-aws/G17_app` en la ventana remota. En esta guía, salvo indicación expresa, los comandos siguientes se ejecutan en **Ubuntu**, no en PowerShell.

## 5. Instalar y comprobar Docker en Ubuntu

Primero comprueba si ya está instalado:

```bash
docker --version
sudo docker compose version
sudo docker info
```

Si los tres funcionan, continúa en el apartado 6. Si Docker ya existe pero falla, consulta al docente antes de reemplazar paquetes. Para una Ubuntu limpia, utiliza el repositorio oficial:

```bash
sudo apt update
sudo apt install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
sudo tee /etc/apt/sources.list.d/docker.sources > /dev/null <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
sudo docker compose version
sudo docker run --rm hello-world
```

La clave permite verificar los paquetes; `docker.sources` identifica repositorio, versión Ubuntu y arquitectura; `systemctl` inicia el servicio. `hello-world` descarga una imagen de prueba, muestra un mensaje y elimina su contenedor al finalizar. [Instalación oficial de Docker para Ubuntu](https://docs.docker.com/engine/install/ubuntu/).

> **Importante**  
> Usaremos `sudo docker`. Administrar Docker concede un poder equivalente a administrar el servidor; no añadas usuarios ajenos al grupo `docker`. No necesitas Docker Desktop ni WSL en Windows para esta ruta: Docker se ejecuta en EC2 Ubuntu.

> **Si algo falla**  
> `Cannot connect to the Docker daemon`: comprueba `sudo systemctl status docker`. Error de repositorio o distribución: confirma `/etc/os-release` y una Ubuntu soportada; no cambies a Amazon Linux. Denegación de red: revisa con el docente rutas, salida y políticas del laboratorio.

## 6. Explorar la aplicación antes de construirla

| Archivo | Función | Modificación propuesta |
|---|---|---|
| `backend/app/main.py` | Rutas, validación, límites y ciclo de vida | Leer `/api/health` y `/api/chat` |
| `backend/app/llm.py` | Respuesta simulada y adaptador OpenAI | Cambiar las instrucciones del asistente |
| `backend/app/settings.py` | Configuración y comprobaciones de seguridad | Identificar combinaciones rechazadas |
| `backend/app/auth.py` | Dependencia que entrega el usuario al endpoint | Preparación para Clerk |
| `frontend/src/App.vue` | Componente con `<script setup lang="ts">` | Personalizar título y etiquetas |
| `frontend/src/composables/useChat.ts` | Estado reactivo y envío | Explicar `ref` y `computed` |
| `frontend/src/services/api.ts` | Peticiones HTTP tipadas | Leer el manejo de errores |
| `frontend/src/services/auth.ts` | Obtención futura del token | No inventar una identidad del usuario |
| `frontend/nginx.conf` | Archivos estáticos y proxy `/api/` | Identificar destino `backend:8000` |
| `compose.yaml` | Servicios y acceso privado | Leer el puerto publicado |

El composable usa `ref` para valores que cambian y `computed` para habilitar el envío. El frontend muestra texto mediante interpolación Vue: no interpreta una respuesta de IA como HTML. El backend acepta solo `message`, rechaza campos adicionales y limita longitud. La pregunta es de un solo turno; no guardamos un historial en una base de datos.

La Composition API con TypeScript se documenta en [Vue](https://vuejs.org/guide/typescript/composition-api). Las dependencias concretas están fijadas en `package-lock.json` y `requirements.txt`; conserva esos archivos para reproducir la práctica.

## 7. Sesión de desarrollo: FastAPI y Vue por separado

### 7.1. Terminal A de Ubuntu — backend simulado

```bash
cd ~/practicas-aws/G17_app/backend
python3 -m venv .venv-backend
source .venv-backend/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

`venv` aísla las librerías; `source` activa ese entorno; `pip` instala versiones fijadas; Uvicorn sirve FastAPI. `--reload` reinicia al editar y es solo para desarrollo. No exportes variables de OpenAI en esta fase. El valor predeterminado es `mock`.

Deja ese terminal abierto. En otro terminal Ubuntu:

```bash
curl -sS http://127.0.0.1:8000/api/health
```

Resultado esperado: `{"status":"ok","mode":"mock"}`. Este endpoint comprueba el servicio; no consume OpenAI.

### 7.2. Terminal B de Ubuntu — frontend

Utilizamos Node dentro de un contenedor para no instalarlo en el servidor:

```bash
cd ~/practicas-aws/G17_app/frontend
sudo docker run --rm --user "$(id -u):$(id -g)" -e HOME=/tmp -v "$PWD:/app" -w /app node:22-alpine npm ci
sudo docker run --rm --network host --user "$(id -u):$(id -g)" -e HOME=/tmp -v "$PWD:/app" -w /app node:22-alpine npm run dev
```

`npm ci` instala según el lock; el volumen permite editar con VS Code; `--user` conserva la propiedad de los archivos; `--network host` permite al proxy Vite llegar al backend en el loopback de **Ubuntu**. El servidor de desarrollo escucha `127.0.0.1:5173`. Esta modalidad de red se usa aquí en Linux, no en Docker de Windows.

Si prefieres Node ya instalado en Ubuntu, comprueba `node --version`: este proyecto exige al menos 22.12 dentro de la rama 22 o una versión compatible posterior. Ejecuta entonces `npm ci` y `npm run dev` directamente. [Requisitos de Vite](https://vite.dev/guide/).

### 7.3. Windows — abrir el túnel

En una ventana nueva de PowerShell:

```powershell
ssh -N -L 127.0.0.1:5173:127.0.0.1:5173 fp-analytics
```

`-N` mantiene la conexión sin ejecutar una consola remota; `-L` conecta el puerto local de Windows con el puerto de Ubuntu. Deja la ventana abierta y visita **http://127.0.0.1:5173** en Windows. Pregunta «¿Qué es un dataset?». Debes ver una respuesta marcada como simulada.

> **Qué está ocurriendo**  
> El navegador envía `/api/chat` a Vite; su proxy lo dirige a FastAPI. La respuesta simulada comprueba el recorrido sin claves ni consumo. `localhost` siempre significa la máquina o contenedor donde se interpreta: el navegador está en Windows; Vite y FastAPI están en Ubuntu.

### 7.4. Actividad y comprobación

Modifica el título en `App.vue` y explica qué cambia al escribir en la caja de texto. Prueba una pregunta vacía y otra con 1.500 caracteres. Comprueba que no puedes enviar mientras se procesa la anterior. En Ubuntu ejecuta las pruebas en un tercer terminal:

```bash
cd ~/practicas-aws/G17_app/backend
source .venv-backend/bin/activate
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Las 15 pruebas cubren simulación, validación, origen, límite de peticiones, configuración insegura y errores del adaptador con clientes falsos. No usan una clave real. Cuando termines, detén A y B con `Ctrl+C`; cierra el túnel con `Ctrl+C` en PowerShell. No hace falta borrar los archivos.

## 8. Dockerizar y desplegar en EC2

### 8.1. Entender las imágenes

El Dockerfile del backend instala Python y ejecuta Uvicorn con un usuario sin privilegios, UID 10001. El frontend utiliza una etapa Node para compilar y una etapa Nginx para servir el resultado. Node y el código fuente de Vue no son necesarios en el contenedor final.

La configuración Compose añade sistema de archivos de solo lectura, directorios temporales y eliminación de capacidades Linux. Estos controles no convierten una máquina compartida en un almacén inaccesible para su administrador. [Contenedores FastAPI](https://fastapi.tiangolo.com/deployment/docker/).

### 8.2. Ubuntu — construcción y arranque

```bash
cd ~/practicas-aws/G17_app
cp .env.example .env
sudo docker compose config --quiet
sudo docker compose build
sudo docker compose up -d
sudo docker compose ps
curl -sS http://127.0.0.1:8080/api/health
```

`.env` contiene **configuración no secreta**: puerto, modelo, ruta del archivo de clave y límites. `config --quiet` valida Compose; `build` crea imágenes; `up -d` arranca en segundo plano; `ps` comprueba estado. El backend debe estar `healthy`, el frontend iniciado y la salud indicar `mock`. Si tarda, espera unos segundos y repite `ps`.

Las imágenes base tienen etiquetas de versión, pero no están fijadas por digest. El docente debe revisar actualizaciones y ensayar cada edición; los locks no garantizan una compilación idéntica cuando cambia una imagen base.

### 8.3. Windows — acceder a la versión desplegada

```powershell
ssh -N -L 127.0.0.1:8080:127.0.0.1:8080 fp-analytics
```

Visita **http://127.0.0.1:8080**. Confirma modo simulado y envía una pregunta. La aplicación ya se ejecuta en AWS, aunque su acceso se mantiene privado por SSH.

En el Security Group conserva SSH 22 desde tu IP de clase según G05. **No añadas 8000, 5173 ni 8080 como entrada pública.** El backend no publica ningún puerto del host. Además, Docker puede gestionar tráfico publicado de una manera que no coincida con las expectativas de UFW; por eso comprobamos tanto vínculo loopback como Security Group. [Red y cortafuegos de Docker](https://docs.docker.com/engine/network/packet-filtering-firewalls/).

> **Si algo falla**  
> Examina `sudo docker compose logs --tail=50 backend frontend`. Los mensajes del proveedor se sustituyen por errores genéricos y no se registran preguntas ni claves. Antes de compartir un diagnóstico, revisa que tampoco has añadido secretos a tu propio código o salida. Un `502` de Nginx puede indicar backend no disponible; `unhealthy` exige revisar primero el backend.

## 9. Activar OpenAI sin enviar la clave al frontend

### 9.1. Preparación

El docente facilita acceso a un proyecto OpenAI y decide un modelo disponible para ese proyecto. **No existe un modelo predeterminado en el ejemplo.** Revisa acceso y costes antes de escribir su identificador. El adaptador usa el SDK oficial y `Responses API`: envía instrucciones, pregunta, modelo y límite de tokens; obtiene `output_text`. [Guía oficial de texto de OpenAI](https://developers.openai.com/api/docs/guides/text).

No escribas la clave en el chat de clase, en una orden del terminal, en capturas ni en `.env`. Tampoco uses un prefijo `VITE_` para secretos: esas variables se incorporan al frontend. [Variables de Vite](https://vite.dev/guide/env-and-mode.html).

### 9.2. Ubuntu — crear el archivo privado

En el terminal interactivo de Ubuntu, fuera del proyecto:

```bash
mkdir -p ~/.config/fp-ai
chmod 700 ~/.config/fp-ai
python3 - <<'PY'
import os
from getpass import getpass
from pathlib import Path

path = Path.home() / '.config/fp-ai/openai_api_key'
key = getpass('Clave OpenAI (no se mostrará): ').strip()
if not key:
    raise SystemExit('No se ha introducido una clave.')
fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
with os.fdopen(fd, 'w', encoding='utf-8') as stream:
    stream.write(key)
print('Archivo creado; contenido oculto.')
PY
sudo chown 10001:10001 ~/.config/fp-ai/openai_api_key
sudo chmod 400 ~/.config/fp-ai/openai_api_key
```

Pega la clave únicamente cuando la solicite `getpass`; no quedará en el historial de órdenes. `O_EXCL` rechaza sobrescribir un archivo existente. `700` restringe el directorio al usuario Ubuntu; `400` permite leer el archivo solo a su propietario, que coincide con el UID del backend. Docker se ejecuta con `sudo` y monta ese archivo para el contenedor.

Si ya existe, no lo borres a ciegas: confirma si estás rotando una clave y quién la administra. No ejecutes `cat` para comprobarla. Comprueba solo metadatos:

```bash
sudo stat -c 'propietario=%u grupo=%g permisos=%a' ~/.config/fp-ai/openai_api_key
```

Resultado: propietario y grupo `10001`, permisos `400`. Si `getpass` avisa que no puede ocultar la entrada, cancela con `Ctrl+C` y utiliza un terminal SSH interactivo; no continúes con entrada visible.

### 9.3. Ubuntu — configuración no secreta y arranque

En VS Code abre `.env`, situado en la raíz del proyecto. Sustituye el valor vacío de `OPENAI_MODEL` por el identificador acordado. La ruta de referencia es:

```dotenv
OPENAI_MODEL=IDENTIFICADOR_AUTORIZADO_DEL_MODELO
OPENAI_KEY_FILE=/home/ubuntu/.config/fp-ai/openai_api_key
MAX_OUTPUT_TOKENS=400
REQUESTS_PER_MINUTE=5
```

El marcador del modelo debe sustituirse; no es un modelo real. Si el usuario de Ubuntu es distinto, cambia la ruta. Después:

```bash
cd ~/practicas-aws/G17_app
sudo docker compose -f compose.yaml -f compose.openai.yaml config --quiet
sudo docker compose -f compose.yaml -f compose.openai.yaml up -d --build
sudo docker compose -f compose.yaml -f compose.openai.yaml ps
curl -sS http://127.0.0.1:8080/api/health
```

El segundo archivo modifica el backend para modo `openai` y monta el secreto. Resultado esperado: salud `openai`; aún no se ha efectuado una llamada al proveedor. Para comprobar lectura sin mostrarlo:

```bash
sudo docker compose -f compose.yaml -f compose.openai.yaml exec backend python -c "import os; print('Legible:', os.access('/run/secrets/openai_api_key', os.R_OK))"
```

Debe indicar `True`. En Windows conserva el túnel del apartado 8, recarga la página y envía una pregunta corta. **Esta prueba sí consume OpenAI**. Revisa el uso en el proyecto del proveedor. Una respuesta demuestra el recorrido completo; una salud correcta solo demuestra que arrancó el servicio.

> **Qué está ocurriendo**  
> Compose monta un archivo del host en `/run/secrets`; no lo copia a una capa de la imagen ni lo envía al navegador. En Compose local este mecanismo no cifra el archivo en disco. El administrador del host y quien controla Docker pueden leerlo. Nunca compartas el servidor con usuarios no autorizados. [Secrets de Docker Compose](https://docs.docker.com/compose/how-tos/use-secrets/).

### 9.4. Límites y privacidad

La aplicación limita preguntas a 1.500 caracteres, salida a 400 tokens por defecto, dos operaciones simultáneas y cinco solicitudes por minuto compartidas entre usuarios. Utiliza un único worker, tiempos de espera y ninguna repetición automática. Una petición rechazada o fallida puede contar para el límite.

El contador vive en memoria y se reinicia al reiniciar el servicio; no es una cuota persistente ni un límite de gasto mensual. Los límites del proyecto y alertas del proveedor deben configurarse y supervisarse aparte. Un modelo de razonamiento puede consumir parte de los tokens en razonamiento y no devolver texto con un límite bajo: revisa modelo y salida con el docente antes de elevar el límite.

Se solicita `store=False`; eso evita almacenar la respuesta para su recuperación mediante esa opción, pero no garantiza retención cero para todos los datos operativos. No introduzcas información personal ni confidencial. [Controles de datos de OpenAI](https://developers.openai.com/api/docs/guides/your-data).

### 9.5. Volver al modo simulado

```bash
sudo docker compose -f compose.yaml -f compose.openai.yaml down
sudo docker compose up -d
curl -sS http://127.0.0.1:8080/api/health
```

La salud debe volver a `mock`. Conserva el archivo privado según la política docente; si la clave se filtró, revócala en OpenAI y genera otra. Borrar un archivo local no revoca una clave.

## 10. Alternativa docente: AWS Secrets Manager

La ruta con archivo privado funciona sin permisos IAM adicionales. Secrets Manager es una ampliación opcional: comprueba disponibilidad regional, permisos de `GetSecretValue` para un secreto concreto, acceso KMS si corresponde y coste. No crees roles nuevos ni intentes eludir una denegación del Learner Lab.

El secreto puede contener un JSON con el campo `openai_api_key`. `deploy/fetch_openai_secret.py` lo recupera en **el host Ubuntu**, usando la cadena normal de credenciales de Boto3 y el perfil EC2 validado en G09. No se inyectan credenciales AWS estáticas en el contenedor ni se abre IMDS para el backend.

Con el backend detenido y el entorno Boto3 de G10 disponible:

```bash
cd ~/practicas-aws/G17_app
source ~/practicas-aws/.venv/bin/activate
python deploy/fetch_openai_secret.py --region eu-west-3 --secret-id IDENTIFICADOR_PRIVADO_DEL_SECRETO
sudo chown 10001:10001 ~/.config/fp-ai/openai_api_key
sudo chmod 400 ~/.config/fp-ai/openai_api_key
```

Sustituye región si el docente tuvo que adaptarla y el identificador por el secreto autorizado. El programa no muestra su contenido; escribe el archivo fuera del proyecto. Arranca con el overlay OpenAI de nuevo. La rotación requiere recuperar la nueva versión y reiniciar el backend, porque la clave se lee al arrancar. [Recuperación con Boto3](https://docs.aws.amazon.com/secretsmanager/latest/userguide/retrieving-secrets-python-sdk.html).

## 11. Demostración pública opcional con HTTPS — solo simulación

Este apartado necesita aprobación del docente para los recursos de la práctica y un dominio/subdominio que administre el centro. Si no existe, termina con el túnel SSH; no necesitas contratar un dominio.

1. Detén la modalidad anterior con los mismos archivos Compose usados para arrancar.
2. Configura un registro DNS `A` del subdominio hacia la IPv4 pública actual de EC2. Si existe `AAAA`, debe apuntar a un servicio IPv6 realmente accesible; elimina una configuración incorrecta con el administrador DNS.
3. En `.env`, escribe `PUBLIC_DOMAIN=SUBDOMINIO_REAL_DEL_CENTRO`, sin `https://` ni ruta.
4. Añade en el Security Group entradas TCP 80 y 443 para el público previsto. El 80 permite validación/redirección HTTPS; conserva SSH limitado a tu IP. No abras 8080 ni 8000.
5. En Ubuntu ejecuta exclusivamente:

```bash
cd ~/practicas-aws/G17_app
sudo docker compose -f compose.yaml -f compose.public-mock.yaml config --quiet
sudo docker compose -f compose.yaml -f compose.public-mock.yaml up -d --build
sudo docker compose -f compose.yaml -f compose.public-mock.yaml ps
```

Visita `https://SUBDOMINIO_REAL_DEL_CENTRO`. Debe aparecer modo simulado y un certificado válido. Caddy termina TLS y reenvía al frontend; conserva certificados en volúmenes. No combines aquí `compose.openai.yaml`, no montes una clave real y no desactives la validación TLS del navegador. [HTTPS automático de Caddy](https://caddyserver.com/docs/automatic-https).

> **Si algo falla**  
> Revisa DNS, IP tras reiniciar EC2, puertos 80/443, salida a Internet y `sudo docker compose -f compose.yaml -f compose.public-mock.yaml logs --tail=50 caddy`. Sin DNS correcto y conectividad, no hay certificado válido. No uses una IP con un dominio inventado ni una excepción de seguridad como solución.

## 12. Ampliación futura G18: Clerk

La aplicación deja dos puntos preparados: `get_current_user` en FastAPI y un proveedor de tokens en Vue. Eso permite añadir autenticación después, pero **no significa que ya sea segura para publicar OpenAI**. `AUTH_MODE=clerk` falla expresamente hasta que se implemente.

La próxima práctica deberá:

1. Integrar `@clerk/vue`, componentes de acceso y una clave **publicable** `VITE_CLERK_PUBLISHABLE_KEY`. Una clave secreta de Clerk nunca va en Vue. [Inicio con Clerk y Vue](https://clerk.com/docs/vue/getting-started/quickstart).
2. Obtener el token de sesión con el SDK y enviarlo como `Authorization: Bearer …` desde el proveedor de `services/auth.ts`.
3. Validar en FastAPI la firma, algoritmo permitido, emisor, caducidad, vigencia y destinatarios/orígenes aplicables al tipo de token configurado, con JWKS o SDK de backend y caché adecuada. Extraer `sub` solo después de validar; no aceptar un identificador enviado por Vue. [Verificación de tokens de Clerk](https://clerk.com/docs/guides/sessions/manual-jwt-verification).
4. Aplicar autorización y cuotas por usuario verificado, con almacenamiento compartido para varios procesos/instancias. Proteger `/api/chat` en el servidor; ocultar el botón en Vue no basta.
5. Adaptar HTTPS, URLs y política CSP a los recursos reales de Clerk; no permitir cualquier origen para resolver un bloqueo.
6. Probar peticiones sin token, token mal firmado, caducado, de otro emisor/proyecto y de usuario sin permiso; todas deben rechazarse sin llamar a OpenAI. Probar además una sesión autorizada y revocación/caducidad.

Solo tras esas pruebas se podrá habilitar la modalidad pública con OpenAI. La hoja de ruta ampliada está en `docs/Clerk_futuro.md`.

## 13. Diagnóstico guiado

| Síntoma | Qué comprobar | Acción |
|---|---|---|
| SSH no conecta | Lab activo, instancia iniciada, IP, regla 22 | Repetir G05; no abrir a cualquier IP |
| `Address already in use` en Windows | Otro túnel ocupa el puerto | Cerrar ese túnel o usar otro puerto local y adaptar orígenes explícitos |
| npm falla por versión | Node utilizado | Usar el contenedor Node 22 del apartado 7 |
| Construcción termina por falta de memoria/disco | `free -h`, `df -h /` | Detener cargas innecesarias; el docente adapta recursos |
| Backend no arranca al activar OpenAI | Modelo, ruta, UID, permisos | Comprobar `.env` y `stat`; no mostrar clave |
| OpenAI devuelve 503 | Clave, cuotas, facturación o límite del proveedor | Revisar en el proyecto OpenAI; no repetir en bucle |
| 502 o respuesta sin texto | Modelo/servicio o tokens insuficientes | Revisar compatibilidad del modelo y límites con el docente |
| 504 | Tiempo de espera/red/proveedor | Esperar y comprobar conectividad; no aumentar gasto a ciegas |
| 429 | Cinco solicitudes/minuto | Esperar una ventana; no reiniciar para eludir el límite |
| 403 desde otra web | Origen no autorizado | Usar URL indicada; no configurar comodín |
| No aparece el cambio de Vue en Compose | Imagen conserva compilación previa | Volver a `build` y `up -d` |
| Denegación de AWS | Región/servicio/acción restringida | Registrar mensaje saneado y pedir adaptación docente |

## 14. Entrega y criterios de evaluación

Entrega código sin secretos y una memoria breve con:

- Diagrama del recorrido de una pregunta y diferencia entre modo simulado y real.
- Captura de interfaz en simulación y resultado de salud, sin datos personales.
- Resultado de las pruebas y construcción; indicación explícita de lo que no se pudo ejecutar.
- Explicación de las dos imágenes, proxy, puerto loopback y túnel.
- Comprobación de permisos de la clave mostrando solo números; si no utilizaste OpenAI real, indícalo y no inventes resultados.
- Un error reproducido sin secretos y su solución.
- Lista de requisitos pendientes para publicar la modalidad real con Clerk.

No incluyas Account ID, UserId, ARN completo, Access Key, Secret Key, Session Token, claves OpenAI/Clerk ni `.pem`. Revisa capturas, terminales y ZIP antes de entregar. El `.gitignore` ayuda, pero no sustituye revisar contenido ni elimina secretos que ya entraron en el historial Git.

## 15. Cierre del laboratorio

En Ubuntu, usa la pareja de archivos correspondiente a la modalidad activa:

```bash
# Modalidad simulada privada:
sudo docker compose down

# O modalidad OpenAI privada:
sudo docker compose -f compose.yaml -f compose.openai.yaml down

# O demostración pública simulada:
sudo docker compose -f compose.yaml -f compose.public-mock.yaml down
```

Ejecuta **una** de esas alternativas desde la raíz del proyecto. `down` detiene y elimina contenedores y red, conservando imágenes y los volúmenes de certificados. No añadas `-v` durante el cierre diario. Detén también servidores de desarrollo y túneles, guarda archivos, revisa gasto AWS y OpenAI, detén EC2 y pulsa **End Lab** siguiendo G01. No presupongas que End Lab borra todos los recursos o invalida una clave externa.

Al finalizar definitivamente la actividad, el docente indicará qué recursos eliminar, revocará las claves que ya no se usen y revisará reglas públicas/DNS. Guardar el proyecto no requiere guardar sus secretos dentro del ZIP.

## 16. Resumen y estado de validación

Has separado interfaz, API y proveedor, desplegado una aplicación contenedorizada en Ubuntu y protegido el uso real mediante acceso SSH y una clave montada exclusivamente en el backend. La publicación con autenticación queda como ampliación G18.

El material se ha comprobado con **15 pruebas de backend superadas** y **compilación/typecheck de Vue superados**, sin utilizar claves reales ni efectuar llamadas facturables. En el entorno de preparación no había un daemon Docker operativo y no se accedió a tu cuenta AWS: la construcción y ejecución de contenedores, permisos Academy, DNS y llamada real deben verificarse siguiendo esta guía antes de impartirla. Detalles en `docs/Validacion.md`.
