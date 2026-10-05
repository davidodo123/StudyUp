# StudyUp AI — Instrucciones y contexto

Este fichero tiene doble propósito:

1. **Traspaso de contexto** (§1–§3) para un asistente que abra este repositorio sin memoria de las sesiones anteriores: qué es el proyecto, en qué estado está y qué decisiones no deben deshacerse.
2. **Manual de operación** (§4–§14) para montar, ejecutar, verificar y desplegar el proyecto en cualquier ordenador.

> La memoria técnica de la práctica (especificación, UML, requisitos, código comentado) está en [`pract01-studyup.md`](pract01-studyup.md). Ese es el entregable académico; este fichero es el manual.

---

# PARTE A — Contexto

## 1. Qué es esto y de dónde viene

**StudyUp AI** es una SPA que genera planes de estudio personalizados con IA. El usuario introduce 4 parámetros (meta, días hasta el examen, recursos disponibles, nivel de partida) y recibe un plan con sesiones agrupadas por día, técnica de estudio, carga cognitiva, calendario de repaso espaciado y plan de contingencia.

- **Frontend:** Vue 3 + TypeScript + Vite + Tailwind CSS
- **Backend:** FastAPI (Python) como función *serverless*
- **IA:** API de OpenAI (compatible con Groq vía `OPENAI_BASE_URL`)
- **Hosting:** Vercel, monorepositorio bajo el mismo origen
- **Repositorio:** https://github.com/davidodo123/StudyUp — rama `main`

### Es una práctica de clase, no un proyecto libre

El fichero [`pract01-vercel.md`](pract01-vercel.md) que está en el repositorio **es la plantilla del enunciado**: una práctica resuelta de otra aplicación (*FitAdapt AI*, generador de rutinas de gimnasio). StudyUp replica deliberadamente su **mismo stack y la misma estructura de memoria**, cambiando solo el dominio a planes de estudio.

El mapeo de parámetros entre ambas es uno a uno:

| FitAdapt (plantilla) | StudyUp |
| :--- | :--- |
| `objetivo` (hipertrofia, fuerza…) | `meta` (aprobar, nota_alta, memorizar, repaso_express) |
| `tiempo_minutos` (20–75) | `dias_disponibles` (1–30) |
| `equipamiento` (mancuernas…) | `recursos` (apuntes, libro, videos, ejercicios, flashcards) |
| `nivel` (principiante…) | `nivel` (principiante, intermedio, avanzado) |

**Implicación práctica:** si hay que decidir cómo estructurar algo nuevo, la respuesta por defecto es "como lo hace `pract01-vercel.md`". Las desviaciones están justificadas en §3 y son deliberadas.

### El usuario trabaja en dos ordenadores

Uno personal y uno de clase. El `.env` con la clave de API **no viaja por git** (ver §6 y §13). Al cambiar de máquina hay que recrearlo a mano.

---

## 2. Estado actual

### Fases del enunciado

| Fase | Contenido | Estado |
| :--- | :--- | :--- |
| 1 | Inicialización del proyecto y entornos | ✅ Completa |
| 2 | Backend serverless con FastAPI | ✅ Completa |
| 3 | Pruebas de backend con Pytest | ✅ Completa, 11/11 |
| 4 | Frontend Vue 3 + Composition API | ✅ Completa |
| 5 | Pruebas de frontend con Vitest | ✅ Completa, 7/7 |
| 6.2 | Repositorio Git + push a GitHub | ✅ Hecho |
| 6.3 | **Desplegar en Vercel con variables de entorno** | ❌ **PENDIENTE** |
| 6.4 | **Verificar en producción (URL pública, sin fugas)** | ❌ **PENDIENTE** |

**Lo único que falta del enunciado es el despliegue (§11).** Sin URL pública no se puede demostrar el objetivo de arquitectura serverless ni la verificación de que la clave no se filtra al cliente.

### Verificación ejecutada

Todo esto se corrió de verdad, no es una estimación:

| Comprobación | Comando | Resultado |
| :--- | :--- | :--- |
| Tipado estricto | `npm run typecheck` | 0 errores |
| Tests de frontend | `npm test` | 7 de 7 pasando |
| Tests de backend | `pytest -v` | 11 de 11 pasando, 0 tokens consumidos |
| Compilación | `npm run build` | OK — 84 kB JS / 13,8 kB CSS |
| Arranque real del servidor | `uvicorn api.index:app --port 8000` | `GET /api/health` → `{"status":"ok", ...}` |
| Diagramas UML | `node tools/check-mermaid.mjs pract01-studyup.md` | 5 de 5 válidos |
| Fuga de secretos en el bundle | `grep -ric "openai\|sk-\|api_key" dist/` | 0 coincidencias |

### Ficheros no versionados todavía

Al cerrar la última sesión quedaban sin commitear: `instrucciones.md`, `CLAUDE.md` y el directorio `tools/`. Conviene comprobarlo con `git status` antes de dar nada por subido.

---

## 3. Decisiones de diseño — no deshacer sin motivo

Esta es la sección más importante para una sesión nueva. Varias de estas decisiones **se desvían a propósito de la plantilla `pract01-vercel.md`**, que tiene fallos reales. Deshacerlas rompe el proyecto o reintroduce un bug.

| # | Decisión | Por qué |
| :-- | :--- | :--- |
| 1 | **Cero campos de texto libre.** Los 4 parámetros son enums cerrados y un entero acotado | Es el modelo de seguridad del proyecto (RNF-02). Sin texto libre, la inyección de prompts no tiene superficie de ataque. Añadir un `<input type="text">` para "asignatura" destruiría el requisito |
| 2 | **La llamada a la IA solo ocurre en el servidor** | Si el `fetch` a OpenAI estuviera en `App.vue`, la clave viajaría en el bundle JS y sería legible con F12 (RNF-01) |
| 3 | **No hay middleware de CORS** | La plantilla lo incluía con `allow_origins=["*"]` + `allow_credentials=True`, combinación **prohibida por la especificación CORS** que los navegadores rechazan. Y es innecesario: frontend y backend comparten origen (RNF-04) |
| 4 | **No existe `api/__init__.py`** | Vercel convierte **cada** `.py` dentro de `api/` en una función independiente. `pytest.ini` declara `pythonpath = .` y Python ≥3.3 trata `api/` como *namespace package*, así que `from api.index import app` funciona sin él |
| 5 | **Los tests de Python están en `tests/`, no en `api/`** | Mismo motivo: un `api/test_api.py` se desplegaría a producción como función inútil |
| 6 | **`requirements.txt` ≠ `requirements-dev.txt`** | Vercel instala solo el primero. `pytest`, `httpx` y `uvicorn` no deben acabar en el bundle de la función serverless |
| 7 | **`vue-tsc@^3.1`, no `^1.8`** | La versión 1.8 de la plantilla es **incompatible con TypeScript ≥5.5** y falla con `Search string not found: "/supportedTSExtensions = .*(?=;)/"`. Con TS 5.9 no arranca |
| 8 | **Cuatro bloques `except` separados, ningún `except Exception` genérico** | La plantilla envolvía todo en un `except Exception` que convertía errores de esquema en HTTP 500 y filtraba trazas de Pydantic al cliente. Aquí cada fallo tiene su 502 con mensaje propio |
| 9 | **Se valida la respuesta de la IA, no solo la petición del usuario** | Un LLM alucina. Hay 4 barreras: respuesta vacía, JSON no parseable, esquema incorrecto, y `dia > dias_disponibles`. Esta última es semántica y es la que la plantilla no tenía |
| 10 | **`<fieldset :disabled="loading">` envolviendo los 4 controles** | La plantilla solo deshabilitaba el botón de submit, incumpliendo su propio RF-02. Un `fieldset` lo resuelve de una vez |
| 11 | **`response_format={"type": "json_object"}`** | Fuerza JSON en origen en lugar de confiar en que el prompt baste. La limpieza de vallas markdown (`limpiar_delimitadores`) se mantiene como red de seguridad |
| 12 | **`load_dotenv()` al importar el módulo** | Sin esto, el arranque local da HTTP 500 aunque exista el `.env`. En Vercel es un *no-op* porque las variables ya están inyectadas |
| 13 | **`pract01-studyup.md` se genera con un script, no se edita a mano** | Ver §10. El documento inyecta el código real desde disco, así que no puede desincronizarse |
| 14 | **`max_tokens=2000`** | La plantilla usaba 900, insuficiente para el caso peor (30 días) → JSON truncado → 502 intermitentes |
| 15 | **Tope de sesiones `MAX_SESIONES = 14`, calculado en el servidor e inyectado en el *user prompt*** | Ni 2000 tokens bastaban: con 2 sesiones/día, a partir de ~14 días el modelo llegaba al límite (`finish_reason: length`) y el JSON salía cortado → 502 casi siempre. Como regla genérica en el *system prompt* el modelo la ignoraba; con un número concreto la cumple. Medido con `gpt-4o-mini`: 30 días → 13-14 sesiones, ~1400 tokens, 15-22 s. Es un entero derivado de `dias_disponibles` ya validado, así que no abre superficie de inyección. No subir `max_tokens` en su lugar: los planes largos tardarían 40-50 s |

### Trampas del entorno de este usuario (Windows)

| Trampa | Qué hacer |
| :--- | :--- |
| **Windows PowerShell 5.1 no acepta `&&`** | Un comando por línea. Ni `&&` ni `\|\|` ni `?:` ni `??` |
| **`python.exe` en `WindowsApps` es el alias falso de la Microsoft Store** | El Python real está en `%LOCALAPPDATA%\Programs\Python\Python312`. Si `python --version` da el mensaje de la Store, es que el PATH de la terminal está desactualizado o el alias sigue activo |
| **Tras instalar algo con `winget`, la terminal abierta no ve el PATH nuevo** | Reabrir la terminal, o refrescar el PATH (§4) |
| **Los heredocs de bash con contenido Python fallan en este entorno** | Para escribir ficheros con código, usar la herramienta `Write`, no `cat <<'EOF'` |
| **`uvicorn` y `npm run dev` "cuelgan" la terminal** | Es lo normal en un servidor de desarrollo. Hacen falta dos terminales simultáneas |

### Sobre la plantilla `pract01-vercel.md`

Se revisó y tiene bugs reales: `nombre: str` (tipo Python) dentro de un `interface` de TypeScript, ausencia de `load_dotenv()`, el CORS inválido ya mencionado, `except Exception` genérico, tests dentro de `api/`, y `vue-tsc@1.8`. StudyUp los corrige todos.

**Dos avisos que se dieron sobre esa plantilla eran falsos** y no hay que repetirlos: los labels de Mermaid `|<<include>>|` y `-- No (HTTP 422) -->` **sí son válidos**; se comprobó con el parser real y los 5 diagramas de la plantilla pasan.

---

# PARTE B — Manual de operación

## 4. Requisitos previos

| Herramienta | Versión | Comprobar con |
| :--- | :--- | :--- |
| Node.js | 20 LTS o superior | `node --version` |
| Python | 3.10 – 3.12 | `python --version` |
| Git | cualquiera reciente | `git --version` |
| Clave de API | OpenAI (`sk-...`) o Groq (`gsk-...`) | — |

### Si falta Node o Python

Con `winget` (no necesita permisos de administrador: instala en la carpeta del usuario):

```powershell
winget install --id Python.Python.3.12 --exact --source winget
```

```powershell
winget install --id OpenJS.NodeJS.LTS --exact --source winget
```

**Después de instalar, cierra y vuelve a abrir PowerShell.** El `PATH` nuevo no llega a las terminales ya abiertas. Si no quieres cerrarla, refréscalo a mano:

```powershell
$env:Path = [Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [Environment]::GetEnvironmentVariable('Path','User')
```

Si `python --version` sigue respondiendo *"Python was not found; run without arguments to install from the Microsoft Store"*, ese `python.exe` es el alias falso de la Store. Desactívalo en **Configuración → Aplicaciones → Configuración avanzada de aplicaciones → Alias de ejecución de aplicaciones** y apaga `python.exe` y `python3.exe`.

---

## 5. Instalación desde cero

> **Sintaxis:** Windows PowerShell 5.1 **no acepta `&&`**. Ejecuta cada bloque por separado.

```powershell
git clone https://github.com/davidodo123/StudyUp.git
```

```powershell
cd StudyUp
```

### 5.1. Dependencias del frontend

```powershell
npm ci
```

`npm ci` y no `npm install`: respeta el `package-lock.json` del repositorio e instala exactamente las versiones ya verificadas.

### 5.2. Entorno virtual y dependencias del backend

```powershell
python -m venv .venv
```

```powershell
.venv\Scripts\Activate.ps1
```

El *prompt* debe quedar con `(.venv)` delante. Si sale *"no se puede cargar el archivo ... Activate.ps1 ... está deshabilitada la ejecución de scripts"*, ejecuta esto una sola vez y repite la activación:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

```powershell
pip install -r requirements-dev.txt
```

---

## 6. Poner la clave de API

**Paso obligatorio que no se puede clonar de git.** El `.env` está en `.gitignore` a propósito: contiene un secreto. Git solo trae la plantilla `.env.example`.

```powershell
Copy-Item .env.example .env
```

```powershell
notepad .env
```

Sustituye el placeholder por la clave real:

```env
OPENAI_API_KEY=sk-aqui-va-tu-clave-de-verdad
```

Para usar **Groq** en lugar de OpenAI, descomenta también:

```env
OPENAI_BASE_URL=https://api.groq.com/openai/v1
AI_MODEL=llama-3.3-70b-versatile
```

Si arrancas sin crear el `.env`, el backend responde HTTP 500 con `La variable de entorno OPENAI_API_KEY no está configurada en el servidor.` No es un bug: es el aislamiento de secretos funcionando.

---

## 7. Arrancar en local

Hacen falta **dos terminales abiertas a la vez**: son dos procesos distintos. Las dos se quedarán imprimiendo logs, eso es lo normal en un servidor de desarrollo. Se paran con `Ctrl+C`.

### Terminal 1 — Backend (puerto 8000)

```powershell
cd C:\ruta\a\StudyUp
```

```powershell
.venv\Scripts\Activate.ps1
```

```powershell
uvicorn api.index:app --reload --port 8000
```

Comprobación: http://127.0.0.1:8000/api/health debe devolver

```json
{"status":"ok","service":"StudyUp API (Python/FastAPI)"}
```

Extra útil: http://127.0.0.1:8000/docs abre la documentación interactiva de FastAPI, donde se puede probar `POST /api/generate-plan` sin tocar la interfaz.

### Terminal 2 — Frontend (puerto 5173)

```powershell
cd C:\ruta\a\StudyUp
```

```powershell
npm run dev
```

Abre **http://localhost:5173**.

Vite redirige todo `/api/*` al puerto 8000 (`server.proxy` en `vite.config.ts`), así que el cliente usa la misma ruta relativa en local y en producción. No hay que cambiar nada al desplegar.

> Si arrancas solo el frontend, la interfaz carga igual pero al pulsar "Generar plan con IA" aparece la tarjeta de error roja. Es el comportamiento correcto ante un fallo de red (RF-05).

---

## 8. Verificar que todo funciona

| Qué comprueba | Comando | Resultado esperado |
| :--- | :--- | :--- |
| Tests del backend | `pytest -v` | 11 passed |
| Tests del frontend | `npm test` | 7 passed |
| Tipado estricto | `npm run typecheck` | sin salida (0 errores) |
| Compilación de producción | `npm run build` | `✓ built in ...` |

Los tests del backend necesitan el `(.venv)` activado. **Ninguna prueba llama a la API real**: el proveedor de IA se sustituye por un `MagicMock`, así que la suite no gasta tokens y funciona sin clave válida.

Comprobación extra de que no se filtra el secreto al cliente (debe dar 0 coincidencias):

```powershell
npm run build
```

```powershell
Select-String -Path dist\assets\*.js,dist\assets\*.css,dist\index.html -Pattern "openai","sk-","api_key" | Measure-Object | Select-Object Count
```

---

## 9. Dónde está la API en el código

Toda la integración con la IA vive en **un solo fichero**: [`api/index.py`](api/index.py). El navegador nunca habla con OpenAI.

| # | Qué pasa | Línea |
| :-- | :--- | :--- |
| 1 | Se carga el `.env` con la clave | `12`, `19` |
| 2 | Entra la clave y se crea el cliente | `104-112` |
| 3 | Se construyen los prompts | `126-178` |
| 4 | **La llamada a la API** | `196-204` |
| 5 | Se lee la respuesta del modelo | `212` |
| 6 | Se valida esa respuesta (4 barreras → HTTP 502) | `213-240` |

La llamada en sí:

```python
completion = client.chat.completions.create(
    model=os.getenv("AI_MODEL", "gpt-4o-mini"),
    messages=[
        {"role": "system", "content": construir_system_prompt()},
        {"role": "user",   "content": construir_user_prompt(payload)},
    ],
    response_format={"type": "json_object"},
    temperature=0.3,
    max_tokens=2000,
)
```

El frontend solo llama al backend propio — `src/App.vue`, línea 97:

```typescript
const response = await fetch('/api/generate-plan', { ... });
```

### Las tres ideas que hay que saber defender

1. **La llamada está en el servidor, no en el navegador.** Si el `fetch` a OpenAI estuviera en `App.vue`, la clave viajaría dentro del bundle JavaScript y cualquiera la leería con F12 para gastar la cuota.

2. **No hay ni un campo de texto libre.** Sin texto libre, un ataque de *prompt injection* ("ignora tus instrucciones y…") no tiene por dónde entrar. La traducción a prosa la hacen diccionarios del servidor (`ETIQUETAS_META`, `ETIQUETAS_NIVEL`), nunca concatenación de texto del usuario.

3. **La respuesta de la IA también es entrada no confiable.** Un modelo puede devolver prosa en vez de JSON, omitir campos o inventarse un "día 40" en un plan de 7 días. Hay cuatro comprobaciones encadenadas antes de que el plan llegue a la pantalla, cada una con su HTTP 502.

---

## 10. Regenerar la memoria de la práctica

`pract01-studyup.md` **no se edita a mano.** Se genera inyectando los ficheros de código reales, así que nunca puede contradecir al código.

Si cambias cualquier fichero fuente, regenérala:

```powershell
node tools/build-doc.mjs
```

Si quieres cambiar la **prosa** (especificación, UML, requisitos, guía de despliegue), edita las fuentes y vuelve a generar:

| Fichero | Contiene |
| :--- | :--- |
| `tools/doc/part1.md` | PARTE 1 completa: descripción, objetivos, stack, estructura, RF/RNF, los 5 diagramas UML y el plan de fases |
| `tools/doc/part3.md` | La guía final de ejecución y despliegue, más la tabla de diagnóstico |
| `tools/build-doc.mjs` | Qué ficheros de código se inyectan, en qué orden y con qué introducción |

Validar los diagramas de Mermaid (necesita instalar dos paquetes de forma puntual; no son dependencias del proyecto):

```powershell
npm i --no-save mermaid jsdom
```

```powershell
node tools/check-mermaid.mjs pract01-studyup.md
```

Debe decir `5/5 diagramas válidos`.

---

## 11. Desplegar en Vercel — PENDIENTE

Esto es lo único que falta del enunciado.

### 11.1. Subir los cambios

```powershell
git add .
```

```powershell
git commit -m "docs: instrucciones y generador de la memoria"
```

```powershell
git push
```

### 11.2. Importar el proyecto

1. Entrar en https://vercel.com y pulsar **Add New → Project**.
2. Seleccionar el repositorio `StudyUp`.
3. Vercel detecta **Vite** automáticamente y lee `requirements.txt` para construir la función Python. **No hay que cambiar ningún comando de build.**

### 11.3. Configurar las variables de entorno

En **Environment Variables**, *antes* de desplegar:

| Nombre | Valor | ¿Obligatoria? |
| :--- | :--- | :--- |
| `OPENAI_API_KEY` | la clave (`sk-...` o `gsk-...`) | **Sí** |
| `OPENAI_BASE_URL` | `https://api.groq.com/openai/v1` | solo con Groq |
| `AI_MODEL` | `llama-3.3-70b-versatile` | solo con Groq |

Marcarlas para los tres entornos: *Production*, *Preview* y *Development*.

### 11.4. Verificar en producción (fase 6.4 del enunciado)

1. Abrir `https://<tu-proyecto>.vercel.app/api/health`. Debe responder `{"status":"ok", ...}`. Si falla aquí, el problema está en la función Python, no en la interfaz.
2. Abrir la raíz del sitio y generar un plan.
3. Abrir F12 → pestaña **Network** → petición a `/api/generate-plan`. Debe ir al mismo origen (sin *preflight* de CORS) y **ninguna cabecera ni cuerpo debe contener la clave de API**. Esta es la demostración visual del RNF-01.

> Las variables de entorno nuevas no se aplican a despliegues ya construidos. Si añades una después, hay que volver a desplegar.

---

## 12. Llevarlo a otro ordenador

Lo que viaja por git y lo que no:

| Se clona de git | Se regenera en el destino |
| :--- | :--- |
| Código, configs, tests, documentación, `tools/` | `node_modules/` → `npm ci` |
| `package-lock.json` | `.venv/` → `python -m venv .venv` |
| `.env.example` (plantilla) | `dist/` → `npm run build` |
| | `.env` → **a mano, con la clave** |

Resumen en el equipo nuevo: clonar → `npm ci` → crear venv → `pip install -r requirements-dev.txt` → `Copy-Item .env.example .env` → pegar la clave → dos terminales.

### Si solo hay que enseñar la aplicación

No montes nada. Despliega en Vercel (§11) y abre la URL pública en el navegador del otro equipo. Cero instalaciones y, sobre todo, **la clave no pisa ese ordenador**.

### Flujo entre dos ordenadores

En el equipo donde trabajas:

```powershell
git add .
git commit -m "fix: lo que hayas cambiado"
git push
```

En el otro, antes de empezar:

```powershell
git pull
```

El `.env` de cada máquina se queda donde está: git lo ignora, así que no se pisan entre sí.

---

## 13. Seguridad: la clave de API

La clave de OpenAI es una credencial de pago. Tres reglas:

1. **Nunca subirla a git.** `.gitignore` ya excluye `.env`, pero si alguna vez se pega directamente en un `.py` o un `.ts` y se hace *commit*, queda en el historial de GitHub para siempre — y los bots que rastrean claves filtradas la encuentran en minutos. Si pasa, revocarla de inmediato; borrar el fichero en un commit posterior **no** la elimina del historial.

2. **Cuidado en ordenadores compartidos.** Un `.env` es texto plano en disco. En un equipo de clase con perfiles comunes, otra persona puede leerlo. Si hay que hacerlo: crear una clave aparte solo para la presentación con límite de gasto bajo, borrar el `.env` y la carpeta al terminar, y **revocar esa clave** desde el panel de OpenAI. Borrar el fichero no invalida la clave; solo la revocación lo hace.

3. **En producción, la clave va en las variables de entorno de Vercel.** Nunca en el repositorio ni en el código del cliente.

---

## 14. Diagnóstico de errores

| Síntoma | Causa | Solución |
| :--- | :--- | :--- |
| `El token '&&' no es un separador de instrucciones válido` | Sintaxis bash pegada en PowerShell 5.1 | Un comando por línea |
| `Python was not found; run without arguments...` | Es el alias de la Microsoft Store, no Python | Instalar Python y reabrir la terminal; desactivar el alias (§4) |
| `'uvicorn' no se reconoce...` | Falta el venv o no está activado | `.venv\Scripts\Activate.ps1`, luego `pip install -r requirements-dev.txt` |
| `Activate.ps1 ... deshabilitada la ejecución de scripts` | Política de ejecución de PowerShell | `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` |
| La terminal "se queda colgada" tras `uvicorn` o `npm run dev` | Comportamiento normal de un servidor | Dejarla abierta y usar otra terminal; `Ctrl+C` para parar |
| HTTP 500 nombrando `OPENAI_API_KEY` | Falta el `.env` en local o la variable en Vercel | Crear `.env` desde `.env.example`, o añadir la variable y volver a desplegar |
| HTTP 502 *"no cumplió con el formato JSON"* | El modelo devolvió prosa en vez de JSON | Comprobar que el proveedor soporta `response_format: json_object`; bajar `temperature` |
| HTTP 502 *"no respeta el esquema"* | El modelo omitió campos obligatorios | Reforzar el esquema del *System Prompt* o subir `max_tokens` |
| HTTP 502 *"sesiones fuera de los días"* | Alucinación del modelo en el campo `dia` | Es el comportamiento correcto: la barrera semántica está funcionando |
| HTTP 422 al enviar el formulario | El payload no respeta enumerados o rangos | Comparar `src/types/plan.ts` con los modelos de `api/index.py` |
| 404 en `/api/*` en local | El backend no está arrancado | `uvicorn api.index:app --reload --port 8000` |
| `Search string not found: supportedTSExtensions` | `vue-tsc@1.8` con TypeScript ≥5.5 | Ya corregido: el proyecto usa `vue-tsc@^3.1`. No bajar la versión |
| Pytest no encuentra el módulo `api` | Se ejecuta desde otra carpeta | Lanzar `pytest` desde la raíz del repositorio |
| `pract01-studyup.md` contradice al código | Se editó a mano | `node tools/build-doc.mjs` (§10) |

---

## Versiones verificadas

Node 24.13.0 · Python 3.12.10 · Vue 3.5.43 · TypeScript 5.9.3 · Vite 5.4.21 · Vitest 1.6.1 · vue-tsc 3.1 · FastAPI 0.142.2 · Pydantic 2.13.5 · OpenAI SDK 3.24.0 · Pytest 9.1.1

> `requirements.txt` declara `openai>=1.12.0`, que hoy resuelve a la rama **3.x**. Se comprobó por introspección que `OpenAI(api_key, base_url)`, `client.chat.completions.create(...)` y los parámetros `model`, `messages`, `response_format`, `temperature` y `max_tokens` siguen existiendo en 3.24.0, y que `OpenAIError` continúa derivando de `Exception`. El código es compatible con ambas ramas sin cambios. Ojo: los tests usan *mock*, así que **no** detectarían una ruptura futura del SDK real.
