// Tipuri pentru StructCalc API — sincronizate cu backend/app/schemas/

export interface HealthResponse {
  status: string;
  service: string;
}

export interface Support {
  x: number;       // pozitie pe bara (m)
  type: number;    // 1=articulatie, 2=reazem mobil, 3=incastrare
}

export interface PointLoad {
  x: number;
  fx: number;
  fy: number;
}

export interface BeamInput {
  length: number;          // L in metri
  angle_deg: number;       // inclinare bara
  supports: Support[];
  point_loads: PointLoad[];
  distributed_load: number; // q in kN/m
  q_start: number;
  q_end: number;
  EI: number;
  EA: number;
}

export interface DiagramPoint {
  x: number;
  N: number;
  V: number;
  M: number;
}

export interface BeamResult {
  reactions: Record<string, number>;
  diagrams: DiagramPoint[];
  max_M: number;
  max_V: number;
  deflection: Array<{ x: number; ux: number; uy: number }>;
}

export interface SectionInput {
  shape: 'rectangle' | 'circle' | 'hollow_circle' | 'T' | 'I';
  b?: number;   // latime (cm)
  h?: number;   // inaltime (cm)
  d?: number;   // diametru (cm)
  d_inner?: number; // diametru interior (cm)
}

export interface SectionResult {
  A: number;    // arie (cm2)
  Ix: number;   // moment de inertie (cm4)
  Iy: number;
  Wx: number;   // modul de rezistenta (cm3)
  ix: number;   // raza de giratie (cm)
}
