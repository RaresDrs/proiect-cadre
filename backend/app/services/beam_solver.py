import numpy as np
from anastruct import SystemElements
from app.schemas.beam import BeamInput, BeamResult, DiagramPoint
from typing import Dict, List


def solve_beam(data: BeamInput) -> BeamResult:
    """
    Rezolva o grinda 2D folosind FEM (anastruct).
    Fara dependinta de Streamlit sau session_state.
    Toate inputurile vin din data: BeamInput.
    """
    L = data.length
    th = np.radians(data.angle_deg)
    c_ang, s_ang = np.cos(th), np.sin(th)

    q_end = data.q_end if data.q_end is not None else L

    # Construieste lista de noduri FEM
    raw_nodes = set([0.0, L])
    for s in data.supports:
        raw_nodes.add(round(s.x, 6))
    for f in data.point_loads:
        raw_nodes.add(round(f.x, 6))
    if data.distributed_load != 0:
        raw_nodes.add(round(data.q_start, 6))
        raw_nodes.add(round(q_end, 6))
    nodes_s = sorted(raw_nodes)
    nn = len(nodes_s)
    ne = nn - 1

    def nidx(xv):
        return nodes_s.index(round(xv, 6))

    # Initializeaza sistemul FEM
    ss_fem = SystemElements(EI=data.EI, EA=data.EA)
    for i in range(ne):
        x1, x2 = nodes_s[i], nodes_s[i + 1]
        ss_fem.add_element(
            location=[[x1 * c_ang, x1 * s_ang], [x2 * c_ang, x2 * s_ang]]
        )

    # Adauga reazeme
    for s in data.supports:
        nid = nidx(s.x) + 1
        if s.type == 1:
            ss_fem.add_support_hinged(node_id=nid)
        elif s.type == 2:
            ss_fem.add_support_roll(node_id=nid)
        elif s.type == 3:
            ss_fem.add_support_fixed(node_id=nid)

    # Sarcina distribuita
    if abs(data.distributed_load) > 1e-9 and q_end > data.q_start:
        q_sign = -data.distributed_load  # anastruct: negativ = in jos
        for eid in range(1, ne + 1):
            mid = (nodes_s[eid - 1] + nodes_s[eid]) / 2
            if data.q_start - 1e-6 <= mid <= q_end + 1e-6:
                ss_fem.q_load(element_id=eid, q=q_sign, direction='y')

    # Forte concentrate si momente
    for f in data.point_loads:
        nid = nidx(f.x) + 1
        if abs(f.fx) > 1e-9:
            ss_fem.point_load(node_id=nid, Fx=f.fx)
        if abs(f.fy) > 1e-9:
            ss_fem.point_load(node_id=nid, Fy=f.fy)

    # Rezolva sistemul
    ss_fem.solve()

    # Extrage reactiunile — float() pentru a converti numpy.float64
    reactions: Dict[str, float] = {}
    for s in data.supports:
        ni = nidx(s.x)
        nid = ni + 1
        r = ss_fem.get_node_results_system(node_id=nid)
        prefix = f"x={s.x:.2f}"
        reactions[f"{prefix}_Fx"] = float(r["Fx"])
        reactions[f"{prefix}_Fy"] = float(r["Fy"])
        reactions[f"{prefix}_Mz"] = float(r["Tz"])

    # Extrage deplasarile
    deflection = []
    for i in range(nn):
        nid = i + 1
        r = ss_fem.get_node_results_system(node_id=nid)
        deflection.append({
            "x": float(nodes_s[i]),
            "ux": float(r["ux"]),
            "uy": float(r["uy"])
        })

    # Construieste diagramele N, V, M
    diagrams: List[DiagramPoint] = []
    for i in range(ne):
        el = ss_fem.element_map[i + 1]
        npts = len(el.bending_moment)
        xs = np.linspace(nodes_s[i], nodes_s[i + 1], npts)
        N_arr = np.linspace(el.N_1, el.N_2, npts)
        for j in range(npts):
            diagrams.append(DiagramPoint(
                x=float(xs[j]),
                N=float(N_arr[j]),
                V=float(el.shear_force[j]),
                M=float(el.bending_moment[j])
            ))

    M_vals = [d.M for d in diagrams]
    V_vals = [d.V for d in diagrams]
    N_vals = [d.N for d in diagrams]

    return BeamResult(
        reactions=reactions,
        diagrams=diagrams,
        max_M=float(max(abs(m) for m in M_vals)),
        max_V=float(max(abs(v) for v in V_vals)),
        max_N=float(max(abs(n) for n in N_vals)) if N_vals else 0.0,
        deflection=deflection
    )
