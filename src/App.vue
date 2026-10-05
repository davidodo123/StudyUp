<script setup lang="ts">
import { computed, ref } from 'vue';
import {
  AlertCircle,
  Brain,
  CalendarDays,
  CheckCircle2,
  GraduationCap,
  Layers,
  Loader2,
  Repeat,
  Sparkles,
  Target,
  Zap,
} from 'lucide-vue-next';
import type { Meta, Nivel, PlanRequest, PlanResponse, Recurso, Sesion } from './types/plan';

interface Opcion<T> {
  id: T;
  label: string;
}

const OPCIONES_META: Opcion<Meta>[] = [
  { id: 'aprobar', label: 'Aprobar con seguridad' },
  { id: 'nota_alta', label: 'Sacar nota alta' },
  { id: 'memorizar', label: 'Memorizar a largo plazo' },
  { id: 'repaso_express', label: 'Repaso exprés' },
];

const OPCIONES_NIVEL: Opcion<Nivel>[] = [
  { id: 'principiante', label: 'Principiante (lo veo por primera vez)' },
  { id: 'intermedio', label: 'Intermedio (lo tengo a medias)' },
  { id: 'avanzado', label: 'Avanzado (solo necesito repasar)' },
];

const OPCIONES_RECURSOS: Opcion<Recurso>[] = [
  { id: 'apuntes', label: 'Apuntes de clase' },
  { id: 'libro', label: 'Libro / manual' },
  { id: 'videos', label: 'Vídeos y clases online' },
  { id: 'ejercicios', label: 'Ejercicios y problemas' },
  { id: 'flashcards', label: 'Flashcards / Anki' },
];

// --- Estado reactivo -------------------------------------------------------
const meta = ref<Meta>('aprobar');
const diasDisponibles = ref<number>(7);
const recursos = ref<Recurso[]>(['apuntes', 'ejercicios']);
const nivel = ref<Nivel>('intermedio');

const loading = ref<boolean>(false);
const error = ref<string | null>(null);
const plan = ref<PlanResponse | null>(null);

const etiquetaMeta = computed(
  () => OPCIONES_META.find((opcion) => opcion.id === meta.value)?.label ?? meta.value,
);

/** Agrupa las sesiones por día para renderizar el plan como un calendario. */
const sesionesPorDia = computed<{ dia: number; sesiones: Sesion[] }[]>(() => {
  if (!plan.value) return [];
  const agrupadas = new Map<number, Sesion[]>();
  for (const sesion of plan.value.sesiones) {
    const existentes = agrupadas.get(sesion.dia) ?? [];
    existentes.push(sesion);
    agrupadas.set(sesion.dia, existentes);
  }
  return [...agrupadas.entries()]
    .sort(([diaA], [diaB]) => diaA - diaB)
    .map(([dia, sesiones]) => ({ dia, sesiones }));
});

/** Alterna un recurso garantizando que siempre quede al menos uno activo (RF-01.3). */
const toggleRecurso = (id: Recurso): void => {
  if (recursos.value.includes(id)) {
    if (recursos.value.length > 1) {
      recursos.value = recursos.value.filter((item) => item !== id);
    }
    return;
  }
  recursos.value = [...recursos.value, id];
};

const handleSubmit = async (): Promise<void> => {
  loading.value = true;
  error.value = null;
  plan.value = null;

  const payload: PlanRequest = {
    meta: meta.value,
    dias_disponibles: Number(diasDisponibles.value),
    recursos: recursos.value,
    nivel: nivel.value,
  };

  try {
    const response = await fetch('/api/generate-plan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const cuerpo = await response.json().catch(() => ({}));
      throw new Error(
        typeof cuerpo.detail === 'string'
          ? cuerpo.detail
          : `No se pudo generar el plan (HTTP ${response.status}).`,
      );
    }

    plan.value = (await response.json()) as PlanResponse;
  } catch (err: unknown) {
    error.value = err instanceof Error ? err.message : 'Ocurrió un error inesperado.';
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <main class="min-h-screen bg-slate-950 px-4 py-10 text-slate-100 sm:px-6 lg:px-8">
    <div class="mx-auto max-w-4xl space-y-8">
      <!-- Cabecera -->
      <header class="space-y-2 text-center">
        <div
          class="mb-2 inline-flex items-center justify-center rounded-2xl border border-indigo-500/20 bg-indigo-500/10 p-3 text-indigo-400"
        >
          <GraduationCap class="h-8 w-8" />
        </div>
        <h1 class="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
          Study<span class="text-indigo-400">Up</span> AI
        </h1>
        <p class="mx-auto max-w-lg text-sm text-slate-400 sm:text-base">
          Generador de planes de estudio personalizados con Inteligencia Artificial según los días
          y los recursos que tengas de verdad.
        </p>
      </header>

      <!-- Formulario de entrada (4 parámetros) -->
      <section class="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-xl sm:p-8">
        <form class="space-y-6" @submit.prevent="handleSubmit">
          <fieldset :disabled="loading" class="space-y-6 disabled:opacity-60">
            <div class="grid grid-cols-1 gap-6 md:grid-cols-2">
              <!-- 1. Meta -->
              <div>
                <label
                  for="campo-meta"
                  class="mb-2 flex items-center text-sm font-semibold text-slate-300"
                >
                  <Target class="mr-2 h-4 w-4 text-indigo-400" />
                  1. Meta del estudio
                </label>
                <select
                  id="campo-meta"
                  v-model="meta"
                  aria-label="Meta del estudio"
                  class="w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:cursor-not-allowed"
                >
                  <option v-for="opcion in OPCIONES_META" :key="opcion.id" :value="opcion.id">
                    {{ opcion.label }}
                  </option>
                </select>
              </div>

              <!-- 2. Días disponibles -->
              <div>
                <div class="mb-2 flex items-center justify-between">
                  <label
                    for="campo-dias"
                    class="flex items-center text-sm font-semibold text-slate-300"
                  >
                    <CalendarDays class="mr-2 h-4 w-4 text-indigo-400" />
                    2. Días hasta el examen
                  </label>
                  <span
                    class="rounded-md bg-indigo-500/20 px-2.5 py-1 text-xs font-bold text-indigo-300"
                  >
                    {{ diasDisponibles }} {{ diasDisponibles === 1 ? 'día' : 'días' }}
                  </span>
                </div>
                <input
                  id="campo-dias"
                  v-model.number="diasDisponibles"
                  type="range"
                  aria-label="Días hasta el examen"
                  min="1"
                  max="30"
                  step="1"
                  class="h-2 w-full cursor-pointer appearance-none rounded-lg bg-slate-700 disabled:cursor-not-allowed"
                />
                <div class="mt-1 flex justify-between text-xs text-slate-500">
                  <span>1 día</span>
                  <span>15 días</span>
                  <span>30 días</span>
                </div>
              </div>

              <!-- 3. Nivel de partida -->
              <div>
                <label
                  for="campo-nivel"
                  class="mb-2 flex items-center text-sm font-semibold text-slate-300"
                >
                  <Brain class="mr-2 h-4 w-4 text-indigo-400" />
                  3. Nivel de partida
                </label>
                <select
                  id="campo-nivel"
                  v-model="nivel"
                  aria-label="Nivel de partida"
                  class="w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:cursor-not-allowed"
                >
                  <option v-for="opcion in OPCIONES_NIVEL" :key="opcion.id" :value="opcion.id">
                    {{ opcion.label }}
                  </option>
                </select>
              </div>

              <!-- 4. Recursos disponibles -->
              <div>
                <span class="mb-2 flex items-center text-sm font-semibold text-slate-300">
                  <Layers class="mr-2 h-4 w-4 text-indigo-400" />
                  4. Recursos disponibles
                </span>
                <div class="flex flex-wrap gap-2">
                  <button
                    v-for="opcion in OPCIONES_RECURSOS"
                    :key="opcion.id"
                    type="button"
                    :aria-pressed="recursos.includes(opcion.id)"
                    :class="[
                      'rounded-lg border px-3 py-2 text-xs font-medium transition disabled:cursor-not-allowed',
                      recursos.includes(opcion.id)
                        ? 'border-indigo-400 bg-indigo-500 font-semibold text-slate-950'
                        : 'border-slate-700 bg-slate-800 text-slate-400 hover:border-slate-600',
                    ]"
                    @click="toggleRecurso(opcion.id)"
                  >
                    {{ opcion.label }}
                  </button>
                </div>
                <p class="mt-2 text-xs text-slate-500">
                  Debe quedar al menos un recurso seleccionado.
                </p>
              </div>
            </div>
          </fieldset>

          <!-- Botón de envío -->
          <button
            type="submit"
            :disabled="loading"
            class="flex w-full items-center justify-center gap-2 rounded-xl bg-indigo-500 px-6 py-3.5 font-bold text-white shadow-lg shadow-indigo-500/20 transition duration-150 hover:bg-indigo-400 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <template v-if="loading">
              <Loader2 class="h-5 w-5 animate-spin" />
              <span>Diseñando tu plan de estudio...</span>
            </template>
            <template v-else>
              <Sparkles class="h-5 w-5" />
              <span>Generar plan con IA</span>
            </template>
          </button>
        </form>
      </section>

      <!-- Alerta de error (RF-05) -->
      <section
        v-if="error"
        role="alert"
        class="flex items-start gap-3 rounded-xl border border-rose-800 bg-rose-950/40 p-4 text-rose-300"
      >
        <AlertCircle class="mt-0.5 h-5 w-5 flex-shrink-0 text-rose-400" />
        <div>
          <h2 class="text-sm font-semibold text-rose-200">Error en la petición</h2>
          <p class="text-sm">{{ error }}</p>
        </div>
      </section>

      <!-- Plan generado -->
      <article
        v-if="plan"
        class="space-y-6 rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl sm:p-8"
      >
        <div
          class="flex flex-col justify-between gap-2 border-b border-slate-800 pb-4 sm:flex-row sm:items-center"
        >
          <div>
            <h2 class="flex items-center gap-2 text-xl font-bold text-white sm:text-2xl">
              <CheckCircle2 class="h-6 w-6 text-indigo-400" />
              Tu plan de estudio
            </h2>
            <p class="text-sm text-slate-400">
              {{ etiquetaMeta }} • {{ diasDisponibles }}
              {{ diasDisponibles === 1 ? 'día' : 'días' }} • nivel {{ nivel }}
            </p>
          </div>
          <div
            class="w-fit rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs font-semibold text-indigo-300"
          >
            {{ plan.horas_totales_estimadas }} h estimadas
          </div>
        </div>

        <!-- Diagnóstico -->
        <div class="rounded-xl border border-slate-800/80 bg-slate-950 p-4">
          <h3 class="mb-1 text-xs font-semibold uppercase tracking-wider text-indigo-400">
            Fase 1: Diagnóstico y estrategia
          </h3>
          <p class="text-sm text-slate-300">{{ plan.diagnostico }}</p>
        </div>

        <!-- Calendario de sesiones -->
        <div class="space-y-3">
          <h3 class="text-xs font-semibold uppercase tracking-wider text-indigo-400">
            Fase 2: Calendario de sesiones
          </h3>
          <div
            v-for="grupo in sesionesPorDia"
            :key="grupo.dia"
            class="rounded-xl border border-slate-800 bg-slate-950 p-4"
          >
            <div class="mb-3 flex items-center gap-2">
              <span
                class="rounded border border-indigo-800 bg-indigo-950/70 px-2 py-0.5 text-xs font-bold text-indigo-300"
              >
                Día {{ grupo.dia }}
              </span>
              <span class="text-xs text-slate-500">
                {{ grupo.sesiones.length }}
                {{ grupo.sesiones.length === 1 ? 'sesión' : 'sesiones' }}
              </span>
            </div>

            <div class="space-y-3">
              <div
                v-for="(sesion, indice) in grupo.sesiones"
                :key="`${grupo.dia}-${indice}`"
                class="flex flex-col justify-between gap-4 rounded-lg border border-slate-800 bg-slate-900 p-4 sm:flex-row sm:items-center"
              >
                <div class="space-y-1">
                  <h4 class="text-base font-bold text-white">{{ sesion.titulo }}</h4>
                  <p class="text-xs font-medium text-indigo-300">{{ sesion.tecnica }}</p>
                  <p class="text-xs text-slate-400">{{ sesion.consejo }}</p>
                </div>

                <div
                  class="flex items-center gap-4 rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-xs font-medium text-slate-300"
                >
                  <div>
                    <span class="block text-slate-500">Duración</span>
                    <span class="font-bold text-white">{{ sesion.duracion_minutos }} min</span>
                  </div>
                  <div class="h-6 w-px bg-slate-800" />
                  <div>
                    <span class="block text-slate-500">Recurso</span>
                    <span class="font-bold text-white">{{ sesion.recurso_principal }}</span>
                  </div>
                  <div class="h-6 w-px bg-slate-800" />
                  <div>
                    <span class="block text-slate-500">Carga</span>
                    <span class="font-bold text-indigo-400">{{ sesion.carga_cognitiva }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Repaso espaciado -->
        <div class="rounded-xl border border-slate-800/80 bg-slate-950 p-4">
          <h3
            class="mb-1 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-indigo-400"
          >
            <Repeat class="h-3.5 w-3.5" />
            Fase 3: Repaso espaciado
          </h3>
          <p class="text-sm text-slate-300">{{ plan.repaso_espaciado }}</p>
        </div>

        <!-- Plan de contingencia -->
        <div class="rounded-xl border border-indigo-800/40 bg-indigo-950/20 p-4">
          <h3
            class="mb-1 flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-indigo-300"
          >
            <Zap class="h-3.5 w-3.5" />
            ¿Solo tienes 20 minutos hoy?
          </h3>
          <p class="text-xs text-slate-300">{{ plan.alternativa_rapida }}</p>
        </div>
      </article>
    </div>
  </main>
</template>
