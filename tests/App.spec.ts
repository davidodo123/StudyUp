import { flushPromises, mount } from '@vue/test-utils';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import App from '../src/App.vue';
import type { PlanResponse } from '../src/types/plan';

const PLAN_MOCK: PlanResponse = {
  diagnostico: 'Tienes el temario a medias, así que atacamos primero las lagunas.',
  sesiones: [
    {
      dia: 1,
      titulo: 'Mapa general del temario',
      duracion_minutos: 50,
      tecnica: 'Pomodoro 25/5 + esquema Feynman',
      recurso_principal: 'apuntes',
      carga_cognitiva: 'Carga 5/10',
      consejo: 'Cierra los apuntes y reescribe el esquema de memoria.',
    },
    {
      dia: 2,
      titulo: 'Problemas tipo examen',
      duracion_minutos: 60,
      tecnica: 'Práctica de recuperación intercalada',
      recurso_principal: 'ejercicios',
      carga_cognitiva: 'Carga 7/10',
      consejo: 'Resuelve sin mirar la solución y corrige al final del bloque.',
    },
  ],
  repaso_espaciado: 'Repasa el día 1 otra vez en los días 3 y 7.',
  alternativa_rapida: 'Con 20 minutos, repasa solo las flashcards que fallaste ayer.',
  horas_totales_estimadas: 9.5,
};

const mockFetchOk = (plan: PlanResponse = PLAN_MOCK) => {
  const fetchMock = vi.fn().mockResolvedValue({
    ok: true,
    status: 200,
    json: async () => plan,
  });
  vi.stubGlobal('fetch', fetchMock);
  return fetchMock;
};

describe('StudyUp - componente App.vue', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('renderiza el formulario con sus 4 parámetros y el botón de acción', () => {
    const wrapper = mount(App);

    expect(wrapper.text()).toContain('1. Meta del estudio');
    expect(wrapper.text()).toContain('2. Días hasta el examen');
    expect(wrapper.text()).toContain('3. Nivel de partida');
    expect(wrapper.text()).toContain('4. Recursos disponibles');
    expect(wrapper.find('button[type="submit"]').text()).toContain('Generar plan con IA');
  });

  it('envía el payload con los 4 parámetros al endpoint correcto', async () => {
    const fetchMock = mockFetchOk();
    const wrapper = mount(App);

    await wrapper.find('form').trigger('submit.prevent');
    await flushPromises();

    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [url, opciones] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toBe('/api/generate-plan');
    expect(opciones.method).toBe('POST');
    expect(JSON.parse(opciones.body as string)).toEqual({
      meta: 'aprobar',
      dias_disponibles: 7,
      recursos: ['apuntes', 'ejercicios'],
      nivel: 'intermedio',
    });
  });

  it('renderiza el plan devuelto agrupando las sesiones por día', async () => {
    mockFetchOk();
    const wrapper = mount(App);

    await wrapper.find('form').trigger('submit.prevent');
    await flushPromises();

    const texto = wrapper.text();
    expect(texto).toContain('Tu plan de estudio');
    expect(texto).toContain('Día 1');
    expect(texto).toContain('Día 2');
    expect(texto).toContain('Mapa general del temario');
    expect(texto).toContain('Problemas tipo examen');
    expect(texto).toContain('Repasa el día 1 otra vez en los días 3 y 7.');
    expect(texto).toContain('Con 20 minutos, repasa solo las flashcards que fallaste ayer.');
    expect(texto).toContain('9.5 h estimadas');
  });

  it('muestra el mensaje de error del backend y no renderiza plan alguno (RF-05)', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 502,
        json: async () => ({ detail: 'La respuesta del modelo de IA no es un JSON válido.' }),
      }),
    );
    const wrapper = mount(App);

    await wrapper.find('form').trigger('submit.prevent');
    await flushPromises();

    expect(wrapper.find('[role="alert"]').exists()).toBe(true);
    expect(wrapper.text()).toContain('La respuesta del modelo de IA no es un JSON válido.');
    expect(wrapper.text()).not.toContain('Tu plan de estudio');
  });

  it('muestra un error legible cuando falla la red', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('Failed to fetch')));
    const wrapper = mount(App);

    await wrapper.find('form').trigger('submit.prevent');
    await flushPromises();

    expect(wrapper.text()).toContain('Failed to fetch');
  });

  it('impide desmarcar el último recurso seleccionado (RF-01.3)', async () => {
    mockFetchOk();
    const wrapper = mount(App);
    const pulsar = async (etiqueta: string) => {
      const boton = wrapper
        .findAll('button[type="button"]')
        .find((candidato) => candidato.text() === etiqueta);
      expect(boton, `No se encontró el botón "${etiqueta}"`).toBeTruthy();
      await boton!.trigger('click');
    };

    // Estado inicial: apuntes + ejercicios. Quitamos uno y el otro debe resistir.
    await pulsar('Ejercicios y problemas');
    await pulsar('Apuntes de clase');

    await wrapper.find('form').trigger('submit.prevent');
    await flushPromises();

    const fetchMock = globalThis.fetch as unknown as ReturnType<typeof vi.fn>;
    const [, opciones] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(JSON.parse(opciones.body as string).recursos).toEqual(['apuntes']);
  });

  it('bloquea el formulario mientras la petición está en vuelo (RF-02)', async () => {
    let resolver: (valor: unknown) => void = () => {};
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation(() => new Promise((resolve) => (resolver = resolve))),
    );
    const wrapper = mount(App);

    await wrapper.find('form').trigger('submit.prevent');

    expect(wrapper.find('fieldset').attributes('disabled')).toBeDefined();
    expect(wrapper.find('button[type="submit"]').attributes('disabled')).toBeDefined();
    expect(wrapper.text()).toContain('Diseñando tu plan de estudio...');

    resolver({ ok: true, status: 200, json: async () => PLAN_MOCK });
    await flushPromises();

    expect(wrapper.find('fieldset').attributes('disabled')).toBeUndefined();
    expect(wrapper.text()).toContain('Tu plan de estudio');
  });
});
