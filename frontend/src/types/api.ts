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

// ── Phase 3: Modul Cadre 2D ─────────────────────────────────────────────────

export type ConstraintType = 'free' | 'pin' | 'roller' | 'fixed'

export interface FrameNode {
  id: string           // UUID string, e.g. crypto.randomUUID()
  x: number            // metres, engineering coordinate
  y: number            // metres, engineering coordinate (Y up)
  constraint: ConstraintType
}

export interface FrameBar {
  id: string           // UUID string
  node_i: string       // FrameNode.id of start node
  node_j: string       // FrameNode.id of end node
  EI: number           // kN·m², default 21000
  EA: number           // kN, default 2100000
}

export interface NodeLoad {
  node_id: string      // FrameNode.id
  Fx: number           // kN, positive = rightward
  Fy: number           // kN, positive = upward
  Mz: number           // kN·m, positive = CCW
}

export interface BarLoad {
  bar_id: string       // FrameBar.id
  q: number            // kN/m, positive = downward (global Y-)
  q_start: number      // fraction 0..1 of bar length, start of load
  q_end: number        // fraction 0..1 of bar length, end of load
}

export interface FrameInput {
  nodes: FrameNode[]
  bars: FrameBar[]
  node_loads: NodeLoad[]
  bar_loads: BarLoad[]
}

// Per-bar diagram data returned by backend
export interface FrameBarDiagram {
  bar_id: string
  M: number[]          // bending moment values at equally-spaced points along bar
  V: number[]          // shear force values
  N: number[]          // axial force values
}

// Per-node displacement result
export interface FrameNodeResult {
  node_id: string
  ux: number           // horizontal displacement (m)
  uy: number           // vertical displacement (m)
  phi_z: number        // rotation (rad)
}

export interface FrameResult {
  bar_diagrams: FrameBarDiagram[]
  node_results: FrameNodeResult[]
  reactions: Record<string, number>  // key: "node_{id}_Fx|Fy|Mz", value: kN or kN·m
  max_M: number
  max_V: number
  max_N: number
}
