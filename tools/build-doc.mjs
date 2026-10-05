/**
 * Genera `pract01-studyup.md` (la memoria de la práctica) a partir de:
 *   - tools/doc/part1.md  -> PARTE 1: especificación, UML y plan de fases
 *   - los ficheros de código REALES del repositorio
 *   - tools/doc/part3.md  -> guía de ejecución y despliegue
 *
 * Así el documento nunca puede desincronizarse del código: si cambias un
 * fichero fuente, vuelves a lanzar este script y la memoria queda al día.
 *
 * Uso (desde la raíz del repositorio):
 *   node tools/build-doc.mjs
 */

import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const AQUI = dirname(fileURLToPath(import.meta.url));
const RAIZ = resolve(AQUI, '..');
const FUENTES = join(AQUI, 'doc');
const SALIDA = join(RAIZ, 'pract01-studyup.md');

/** Elige una valla más larga que la secuencia de backticks más larga del contenido. */
function fenceFor(contenido) {
  const rachas = contenido.match(/`+/g) ?? [];
  const maxima = rachas.reduce((max, racha) => Math.max(max, racha.length), 0);
  return '`'.repeat(Math.max(3, maxima + 1));
}

function bloque(rutaRelativa, lenguaje) {
  const contenido = readFileSync(join(RAIZ, rutaRelativa), 'utf8').replace(/\s+$/, '');
  const valla = fenceFor(contenido);
  return `#### \`${rutaRelativa}\`\n${valla}${lenguaje}\n${contenido}\n${valla}\n`;
}

const SECCIONES = [
  {
    titulo: '### 1. Configuración del Proyecto y Tipado',
    intro:
      'Nótese la separación de `requirements.txt` y `requirements-dev.txt`: Vercel instala únicamente el primero, así que las dependencias de testing no acaban en el bundle de la función Serverless.',
    archivos: [
      ['package.json', 'json'],
      ['requirements.txt', 'text'],
      ['requirements-dev.txt', 'text'],
      ['pytest.ini', 'ini'],
      ['tsconfig.json', 'json'],
      ['tsconfig.node.json', 'json'],
      ['src/env.d.ts', 'typescript'],
      ['vite.config.ts', 'typescript'],
      ['tailwind.config.js', 'javascript'],
      ['postcss.config.js', 'javascript'],
      ['vercel.json', 'json'],
      ['.env.example', 'env'],
      ['.gitignore', 'text'],
      ['index.html', 'html'],
      ['public/favicon.svg', 'xml'],
    ],
  },
  {
    titulo: '### 2. Backend: FastAPI, Pydantic y la Doble Barrera de Validación',
    intro:
      'Un único fichero concentra los esquemas de entrada (HTTP 422), los esquemas de salida (HTTP 502), la factoría de secretos (HTTP 500), la ingeniería del prompt y los dos endpoints. Los bloques de `except` están deliberadamente separados por tipo de fallo: no hay ningún `except Exception` genérico que convierta un error de esquema en un 500 y filtre trazas internas al cliente.',
    archivos: [['api/index.py', 'python']],
  },
  {
    titulo: '### 3. Pruebas Automatizadas del Backend con Pytest',
    intro:
      'Once pruebas que cubren salud del servicio, las tres rutas de rechazo 422, los dos caminos felices (JSON limpio y JSON envuelto en vallas markdown), las cuatro rutas de fallo 502 y la ausencia de secreto (500). El proveedor de IA se sustituye siempre por un `MagicMock`, de modo que la suite no gasta tokens ni necesita una clave válida (RNF-06).',
    archivos: [['tests/test_api.py', 'python']],
  },
  {
    titulo: '### 4. Frontend: Vue 3 (Composition API + TypeScript)',
    intro:
      'El contrato de datos vive en `src/types/plan.ts` y es el espejo exacto de los modelos Pydantic. En `App.vue`, los cuatro controles van dentro de un único `<fieldset :disabled="loading">`, que resuelve el requisito RF-02 de bloqueo total con una sola línea en lugar de repetir `:disabled` en cada control.',
    archivos: [
      ['src/types/plan.ts', 'typescript'],
      ['src/style.css', 'css'],
      ['src/main.ts', 'typescript'],
      ['src/App.vue', 'vue'],
    ],
  },
  {
    titulo: '### 5. Pruebas Unitarias del Frontend con Vitest y Vue Test Utils',
    intro:
      'Siete pruebas sobre `jsdom`. Destacan la verificación del payload exacto enviado al backend, las dos rutas de error (respuesta 502 con `detail` y `fetch` rechazado) y el test del estado de bloqueo, que guarda el `resolve` de la promesa en una variable para poder inspeccionar la UI mientras la petición sigue en vuelo.',
    archivos: [['tests/App.spec.ts', 'typescript']],
  },
];

const partes = [readFileSync(join(FUENTES, 'part1.md'), 'utf8').replace(/\s+$/, '')];

for (const seccion of SECCIONES) {
  partes.push(`\n---\n\n${seccion.titulo}\n\n${seccion.intro}\n`);
  for (const [ruta, lenguaje] of seccion.archivos) {
    partes.push(bloque(ruta, lenguaje));
  }
}

partes.push(readFileSync(join(FUENTES, 'part3.md'), 'utf8').replace(/\s+$/, ''));

const salida = partes.join('\n') + '\n';
writeFileSync(SALIDA, salida, 'utf8');
console.log(`pract01-studyup.md regenerado: ${salida.split('\n').length} líneas`);
