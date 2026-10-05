---

### 6. Guía de Ejecución Local y Despliegue

#### 6.1. Instalación inicial (una sola vez)

1. **Dependencias del frontend:**
   ```bash
   npm install
   ```
2. **Entorno virtual y dependencias del backend:**
   ```bash
   # Windows (PowerShell)
   python -m venv .venv
   .venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv .venv
   source .venv/bin/activate

   pip install -r requirements-dev.txt
   ```
3. **Secretos:** copiar la plantilla y rellenar la clave real.
   ```bash
   # Windows (PowerShell)
   Copy-Item .env.example .env

   # Linux / macOS
   cp .env.example .env
   ```
   Editar `.env` y poner la clave de OpenRouter en `OPENAI_API_KEY`. La plantilla ya trae `OPENAI_BASE_URL` y `AI_MODEL` apuntando a OpenRouter. `python-dotenv` lo cargará todo al arrancar el backend.

#### 6.2. Ejecución en Local (Desarrollo)

Se requieren **dos terminales simultáneas**, porque Vite y FastAPI son dos procesos distintos:

1. **Terminal 1 (Backend FastAPI en el puerto 8000):**
   ```bash
   # Windows (PowerShell)
   .venv\Scripts\Activate.ps1
   # Linux / macOS
   source .venv/bin/activate

   uvicorn api.index:app --reload --port 8000
   ```
   Comprobación rápida: `http://127.0.0.1:8000/api/health` debe devolver `{"status":"ok", ...}`. La documentación interactiva de FastAPI queda en `http://127.0.0.1:8000/docs`.

2. **Terminal 2 (Frontend Vite + Vue en el puerto 5173):**
   ```bash
   npm run dev
   ```
   Navegar a `http://localhost:5173`. Vite enrutará automáticamente cualquier petición a `/api/*` hacia el puerto 8000 gracias al `server.proxy` de `vite.config.ts`, de modo que el código del cliente usa exactamente la misma ruta relativa que usará en producción.

#### 6.3. Ejecución de Pruebas Automatizadas

* **Backend (11 pruebas, sin consumir tokens):**
  ```bash
  pytest -v
  ```
* **Frontend (7 pruebas sobre jsdom):**
  ```bash
  npm test
  ```
* **Chequeo de tipos estricto (RNF-05):**
  ```bash
  npm run typecheck
  ```
* **Compilación de producción (ejecuta el chequeo de tipos y luego empaqueta):**
  ```bash
  npm run build
  ```

#### 6.4. Despliegue en Vercel

1. **Inicializar el repositorio y subirlo:**
   ```bash
   git init
   git add .
   git commit -m "feat: StudyUp AI, monorepo Vue 3 + TypeScript + FastAPI serverless"
   git branch -M main
   git remote add origin https://github.com/davidodo123/StudyUp.git
   git push -u origin main
   ```
2. **Importar el proyecto:** acceder a [Vercel Dashboard](https://vercel.com) y pulsar **Add New → Project**. Seleccionar el repositorio. Vercel detectará el framework **Vite** automáticamente y leerá `requirements.txt` para construir la función Python; no hay que tocar los comandos de *build*.
3. **Configurar las variables de entorno:** en la sección **Environment Variables**, antes de desplegar, añadir:

   | Nombre | Valor |
   | :--- | :--- |
   | `OPENAI_API_KEY` | La clave de OpenRouter (`sk-or-v1-...`) |
   | `OPENAI_BASE_URL` | `https://openrouter.ai/api/v1` |
   | `AI_MODEL` | `openai/gpt-4o-mini` |

   Las tres son obligatorias: sin las dos últimas, el SDK enviaría la clave de OpenRouter a la API de OpenAI y fallaría. Guardarlas como tipo **Secret** y asignarlas al entorno *Production*. Se puede pegar el contenido del `.env` directamente en el campo *Key* y Vercel lo separa en las tres variables.
4. **Desplegar:** pulsar **Deploy** y esperar a que terminen los dos *builds* (el estático de Vite y la función Python).
5. **Verificación en producción** (URL pública del proyecto: <https://study-up-beryl.vercel.app>):
   * Abrir `https://study-up-beryl.vercel.app/api/health`. Debe responder `{"status":"ok","service":"StudyUp API (Python/FastAPI)"}`. Si falla aquí, el problema está en la función Python, no en la UI.
   * Abrir la raíz del sitio, generar un plan y confirmar que se renderiza.
   * Abrir las herramientas de desarrollo del navegador, pestaña **Network**, y revisar la petición a `/api/generate-plan`: debe salir hacia el mismo origen (sin preflight CORS) y **ninguna cabecera ni cuerpo debe contener la clave de API**. Esta es la comprobación visual de RNF-01.
   * Si aparece un HTTP 500 cuyo mensaje nombra `OPENAI_API_KEY`, la variable no se guardó en el entorno correcto o se añadió después del despliegue: revisarla en **Environment Variables** y hacer **Deployments → ⋯ → Redeploy** (las variables nuevas no se aplican a despliegues ya construidos).

   Resultado verificado en producción: `/api/health` responde 200; un plan de 5 días se genera en ~6 s y uno de 30 días (14 sesiones) en ~32 s; el *bundle* servido no contiene ninguna aparición de `sk-or`, `openai`, `openrouter` ni `api_key`.

#### 6.5. Guía rápida de diagnóstico

| Síntoma | Causa probable | Solución |
| :--- | :--- | :--- |
| HTTP 500 nombrando `OPENAI_API_KEY` | Falta el `.env` en local o la variable en Vercel | Crear `.env` desde `.env.example`, o añadir la variable y volver a desplegar |
| HTTP 502 "no cumplió con el formato JSON" | El modelo devolvió prosa en lugar de JSON | Revisar que el proveedor soporta `response_format: json_object`; bajar `temperature` |
| HTTP 502 "no cumplió con el formato JSON" en planes largos | La respuesta llegó a `max_tokens` y el JSON salió cortado (`finish_reason: length`) | Bajar `MAX_SESIONES` en `api/index.py` en lugar de subir `max_tokens`, que alargaría la espera |
| HTTP 502 "no respeta el esquema" | El modelo omitió campos obligatorios | Reforzar el esquema literal del *System Prompt* |
| HTTP 502 "sesiones fuera de los días" | Alucinación del modelo en el campo `dia` | Es el comportamiento correcto: la barrera semántica está funcionando |
| HTTP 422 al enviar el formulario | El payload no respeta los enumerados o rangos | Comparar `src/types/plan.ts` con los modelos de `api/index.py` |
| 404 en `/api/*` en local | El backend no está arrancado o no escucha en el 8000 | Arrancar `uvicorn api.index:app --reload --port 8000` |
| `Search string not found: supportedTSExtensions` | `vue-tsc@1.8` con TypeScript ≥ 5.5 | Actualizar a `vue-tsc@^3.1` y reinstalar |
| Pytest no encuentra el módulo `api` | Falta `pythonpath = .` o se ejecuta desde otra carpeta | Lanzar `pytest` desde la raíz del repositorio |
