/**
 * Contrato de datos compartido con el backend.
 * Cada tipo es el espejo exacto de un modelo Pydantic de `api/index.py`.
 */

export type Meta = 'aprobar' | 'nota_alta' | 'memorizar' | 'repaso_express';
export type Nivel = 'principiante' | 'intermedio' | 'avanzado';
export type Recurso = 'apuntes' | 'libro' | 'videos' | 'ejercicios' | 'flashcards';

/** Espejo de `PlanRequest`. */
export interface PlanRequest {
  meta: Meta;
  dias_disponibles: number;
  recursos: Recurso[];
  nivel: Nivel;
}

/** Espejo de `Sesion`. */
export interface Sesion {
  dia: number;
  titulo: string;
  duracion_minutos: number;
  tecnica: string;
  recurso_principal: string;
  carga_cognitiva: string;
  consejo: string;
}

/** Espejo de `PlanResponse`. */
export interface PlanResponse {
  diagnostico: string;
  sesiones: Sesion[];
  repaso_espaciado: string;
  alternativa_rapida: string;
  horas_totales_estimadas: number;
}
