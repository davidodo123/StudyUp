# StudyUp AI

**Lee [`instrucciones.md`](instrucciones.md) antes de tocar nada.** Sus secciones §1–§3 son el traspaso de contexto: qué es el proyecto, en qué estado está y qué decisiones de diseño no deben deshacerse. El resto es el manual de operación.

## Lo mínimo para orientarse

Práctica de clase. SPA que genera planes de estudio con IA. Vue 3 + TypeScript + Vite + Tailwind en el cliente; FastAPI (Python) como función serverless en Vercel; OpenRouter (`openai/gpt-4o-mini`, vía el SDK de OpenAI) como proveedor de IA.

[`pract01-vercel.md`](pract01-vercel.md) **es la plantilla del enunciado** (otra app: *FitAdapt*, rutinas de gimnasio). StudyUp replica su stack y su estructura de memoria cambiando el dominio. Ante una duda de estructura, la respuesta por defecto es "como lo hace la plantilla"; las desviaciones están justificadas en §3 de `instrucciones.md` y son deliberadas.

- Repositorio: https://github.com/davidodo123/StudyUp — rama `main`
- Entregable académico: `pract01-studyup.md`
- Producción: https://study-up-beryl.vercel.app — cada `git push` a `main` despliega solo.
- **Todas las fases del enunciado están hechas y verificadas**, incluido el despliegue.

## Reglas que no se negocian

1. **La llamada a la IA solo ocurre en `api/index.py`.** Nunca en el cliente: la clave viajaría en el bundle.
2. **Cero campos de texto libre.** Los 4 parámetros son enums cerrados y un entero acotado. Es el modelo de seguridad del proyecto (RNF-02).
3. **Se valida la respuesta del LLM, no solo la petición del usuario.** Cuatro barreras → HTTP 502. No sustituir por un `except Exception` genérico.
4. **`pract01-studyup.md` no se edita a mano.** Se regenera con `node tools/build-doc.mjs`, que inyecta el código real. Para cambiar la prosa, editar `tools/doc/part1.md` o `tools/doc/part3.md`.
5. **No bajar `vue-tsc` por debajo de `^3.1`.** La versión 1.8 es incompatible con TypeScript ≥5.5.
6. **No añadir middleware de CORS.** Frontend y backend comparten origen.
7. **No cambiar el modelo a uno `:free` de OpenRouter.** Lo eligió el profesor y la clave trae saldo.
8. **No subir `max_tokens` para arreglar JSON truncado.** Se limita el número de sesiones con `MAX_SESIONES` (§3, decisión 15).

## Entorno (Windows)

- **Windows PowerShell 5.1: no existe `&&`.** Un comando por línea.
- El `python.exe` de `WindowsApps` es el alias falso de la Microsoft Store. El real está en `%LOCALAPPDATA%\Programs\Python\Python312`.
- Los heredocs de bash con contenido Python fallan en este entorno: usar la herramienta `Write`.
- `uvicorn` y `npm run dev` ocupan la terminal. Hacen falta dos.

## Comandos

```powershell
npm run dev                              # frontend, puerto 5173
uvicorn api.index:app --reload --port 8000   # backend (con el venv activado)
npm test                                 # 7 tests de frontend
pytest -v                                # 11 tests de backend, sin gastar tokens
npm run typecheck                        # debe dar 0 errores
node tools/build-doc.mjs                 # regenerar la memoria de la práctica
```

El `.env` con la clave **no está en git**. En una máquina nueva: `Copy-Item .env.example .env` y pegar la clave de OpenRouter (la plantilla ya trae `OPENAI_BASE_URL` y `AI_MODEL`). Ver §6 y §13 de `instrucciones.md`.
