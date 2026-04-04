import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from io import BytesIO
from matplotlib.backends.backend_pdf import PdfPages

# --- SETĂRI PAGINĂ ---
st.set_page_config(page_title="Calcul Structural 2D", layout="wide")
st.markdown("<div style='text-align: right; color: gray; font-size: 18px; font-weight: bold;'>Stud. Pop Rareș Darius</div>", unsafe_allow_html=True)
st.title("Calcul Structural 2D")
st.markdown("---")

def to_sci(val):
    if val == 0: return "0"
    exp = int(np.floor(np.log10(abs(val))))
    coef = val / (10**exp)
    return rf"{coef:.2f} \cdot 10^{{{exp}}}"

# ==========================================
# NAVIGARE PRINCIPALĂ
# ==========================================
modul = st.sidebar.radio("Selectează Modulul", [
    "1. Calcul FEM Bară 2D",
    "2. Grinzi Static Determinate",
    "3. Grinzi Gerber",
    "4. Cadre Static Determinate",
    "5. Arce Static Determinate",
    "6. Rezistența Materialelor",
    "7. Metoda Forțelor (SSN)",
    "8. Asistent Teoretic",
])

# ==========================================
# MODUL 1: CALCUL FEM BARĂ 2D (original)
# ==========================================
if modul == "1. Calcul FEM Bară 2D":
    if 'L_val' not in st.session_state: st.session_state.L_val = 0.0
    if 'Ang_val' not in st.session_state: st.session_state.Ang_val = 0.0

    def update_L_from_slider(): st.session_state.L_val = st.session_state.L_slider
    def update_L_from_num(): st.session_state.L_val = st.session_state.L_num
    def update_A_from_slider(): st.session_state.Ang_val = float(st.session_state.A_slider)
    def update_A_from_num(): st.session_state.Ang_val = float(st.session_state.A_num)

    st.sidebar.header("1. Geometrie Bară")
    st.sidebar.slider("Trage lungimea L (m)", 0.0, 20.0, st.session_state.L_val, key='L_slider', on_change=update_L_from_slider)
    L = st.sidebar.number_input("Sau scrie exact L (m):", 0.0, 20.0, st.session_state.L_val, key='L_num', on_change=update_L_from_num)

    st.sidebar.slider("Înclinare Bară (°)", 0.0, 90.0, st.session_state.Ang_val, key='A_slider', on_change=update_A_from_slider)
    theta_deg = st.sidebar.number_input("Sau scrie unghiul (°):", 0.0, 90.0, st.session_state.Ang_val, key='A_num', on_change=update_A_from_num)

    b_cm = st.sidebar.number_input("Lățime b (cm)", min_value=0.0, value=0.0)
    h_cm = st.sidebar.number_input("Înălțime h (cm)", min_value=0.0, value=0.0)

    b, h = b_cm/100, h_cm/100
    A = b * h
    I = (b * h**3) / 12 if b>0 and h>0 else 0

    st.sidebar.markdown("### Caracteristici Secțiune")
    st.sidebar.latex(r"A = b \cdot h")
    st.sidebar.markdown(f"**Arie (A):** {A:.4f} m²" if A>0 else "**Arie (A):** 0.0000 m²")

    st.sidebar.latex(r"I = \frac{b \cdot h^3}{12}")
    if I > 0:
        st.sidebar.latex(rf"\text{{Inerție }} (I) = {to_sci(I)} \text{{ m}}^4")
    else:
        st.sidebar.markdown("**Inerție (I):** 0 m⁴")

    st.sidebar.header("2. Material")
    mat = st.sidebar.selectbox("Clasă Material", [
        "Beton C12/15", "Beton C16/20", "Beton C20/25", "Beton C25/30",
        "Beton C30/37", "Beton C35/45", "Beton C40/50", "Beton C45/55", "Beton C50/60",
        "Oțel S235", "Oțel S275", "Oțel S355"
    ])
    E_dict = {
        "Beton C12/15": 27e6, "Beton C16/20": 29e6, "Beton C20/25": 30e6, "Beton C25/30": 31e6,
        "Beton C30/37": 33e6, "Beton C35/45": 34e6, "Beton C40/50": 35e6, "Beton C45/55": 36e6, "Beton C50/60": 37e6,
        "Oțel S235": 210e6, "Oțel S275": 210e6, "Oțel S355": 210e6
    }
    E = E_dict[mat]
    st.sidebar.markdown(f"**Modul Young (E):** {E/1e6:.1f} GPa ({E:,.0f} kN/m²)".replace(',', '.'))

    st.sidebar.header("3. Reazeme")
    reaz_options = {
        0: "Liber (0 GDL)",
        1: "Articulație (Blochează ΔX, ΔY)",
        2: "Reazem Simplu (Blochează ΔY)",
        3: "Încastrare (Blochează ΔX, ΔY, Rotire)"
    }
    r1 = st.sidebar.selectbox("Nod START (x=0)", [0, 1, 2, 3], index=0, format_func=lambda x: reaz_options[x])
    r2 = st.sidebar.selectbox("Nod END (x=L)", [0, 1, 2, 3], index=0, format_func=lambda x: reaz_options[x])

    st.sidebar.markdown("---")
    st.sidebar.subheader("Determinare Statică")
    gdl_blocate = 0
    if r1 == 1: gdl_blocate += 2
    elif r1 == 2: gdl_blocate += 1
    elif r1 == 3: gdl_blocate += 3
    if r2 == 1: gdl_blocate += 2
    elif r2 == 2: gdl_blocate += 1
    elif r2 == 3: gdl_blocate += 3

    G_form = gdl_blocate - 3
    if G_form == 0:
        st.sidebar.success(f"G = {gdl_blocate} - 3 = {G_form}\n\nStructură Static Determinată (SSD)")
    elif G_form > 0:
        st.sidebar.warning(f"G = {gdl_blocate} - 3 = {G_form}\n\nStructură Static Nedeterminată (SSN)")
    else:
        st.sidebar.error(f"G = {gdl_blocate} - 3 = {G_form}\n\nMecanism! Structura este instabilă.")

    if L == 0 or A == 0:
        st.info("Introduceți Lungimea (L), Lățimea (b) și Înălțimea (h) în meniul din stânga pentru a începe.")
    else:
        st.header("Configurare Încărcări")

        st.markdown("**Forță uniform distribuită (q)** [acționează vertical în jos]")
        col_q1, col_q2, col_q3 = st.columns(3)
        with col_q1:
            q_val = st.number_input("Valoare q (kN/m) [pozitiv = în jos]", min_value=0.0, value=0.0, step=1.0)
        with col_q2:
            q_start = st.number_input("De la x (m)", min_value=0.0, max_value=float(L), value=0.0)
        with col_q3:
            q_end = st.number_input("Până la x (m)", min_value=float(q_start), max_value=float(L), value=float(L))

        st.markdown("---")
        if 'forces' not in st.session_state:
            st.session_state.forces = []

        c_btn1, c_btn2 = st.columns([1, 4])
        with c_btn1:
            if st.button("Adaugă Forță / Moment"):
                st.session_state.forces.append({'tip': 'Forță Verticală (Fy)', 'val': 0.0, 'dist': float(L)/2})
            if st.button("Șterge Ultima"):
                if len(st.session_state.forces) > 0: st.session_state.forces.pop()

        edited_forces = []
        if len(st.session_state.forces) > 0:
            cols = st.columns(min(len(st.session_state.forces), 4))
            for i, f in enumerate(st.session_state.forces):
                col_idx = i % 4
                with cols[col_idx]:
                    st.markdown(f"**Acțiunea {i+1}**")
                    tip = st.selectbox("Tip", ["Forță Verticală (Fy)", "Forță Orizontală (Fx)", "Moment (M)"],
                                       index=["Forță Verticală (Fy)", "Forță Orizontală (Fx)", "Moment (M)"].index(f['tip']), key=f"tip{i}")
                    help_txt = ""
                    if "Fy" in tip: help_txt = "[+ = Sus, - = Jos]"
                    elif "Fx" in tip: help_txt = "[+ = Dreapta, - = Stânga]"
                    else: help_txt = "[+ = Orar, - = Anti-orar]"
                    val = st.number_input(f"Valoare {help_txt} ##{i}", value=f['val'], key=f"val{i}")
                    d = st.number_input(f"Distanța (m) ##{i}", 0.0, float(L), float(f['dist']), key=f"d{i}")
                    edited_forces.append({'tip': tip, 'val': val, 'dist': d})
            st.session_state.forces = edited_forces

        st.markdown("---")
        st.subheader("Schiță Model Structural")
        th = np.radians(theta_deg)
        c_ang, s_ang = np.cos(th), np.sin(th)

        fig_height = max(3.5, 7.0 * np.sin(th))
        fig1, ax1 = plt.subplots(figsize=(10, fig_height), dpi=150)

        end_x, end_y = L*c_ang, L*s_ang

        lw_beam = 3 + (min(h_cm, 150.0)/30)
        ax1.plot([0, end_x], [0, end_y], 'k', lw=lw_beam, zorder=1)

        ax1.plot([0, end_x], [0-0.6, end_y-0.6], color='gray', linestyle='--', lw=1)
        ax1.text(end_x/2, end_y/2 - 0.8, f"L = {L:.2f} m", color='black', weight='bold', ha='center', fontsize=11)

        def draw_reaz(tip, x, y):
            if tip == 1: ax1.plot(x, y, '^', ms=14, color='orange', markeredgecolor='black', zorder=5)
            elif tip == 2: ax1.plot(x, y, 'o', ms=10, color='green', markeredgecolor='black', zorder=5)
            elif tip == 3:
                per_dx, per_dy = 0.4*s_ang, -0.4*c_ang
                ax1.plot([x-per_dx, x+per_dx], [y-per_dy, y+per_dy], 'blue', lw=5)

        draw_reaz(r1, 0, 0)
        draw_reaz(r2, end_x, end_y)

        if q_val > 0 and (q_end > q_start):
            v_offset = max(0.8, L * 0.1)
            qs_x, qs_y = q_start*c_ang, q_start*s_ang
            qe_x, qe_y = q_end*c_ang, q_end*s_ang
            ax1.plot([qs_x, qe_x], [qs_y + v_offset, qe_y + v_offset], 'blue', lw=2, zorder=2)
            for d in np.linspace(q_start, q_end, max(4, int((q_end-q_start)*2))):
                xi, yi = d*c_ang, d*s_ang
                ax1.arrow(xi, yi + v_offset, 0, -v_offset + 0.1, head_width=0.08, fc='blue', ec='blue', length_includes_head=True, zorder=2)
            ax1.text((qs_x+qe_x)/2, (qs_y+qe_y)/2 + v_offset + 0.15, f"q = {q_val} kN/m", color='blue', weight='bold', ha='center', fontsize=11)

        arrow_len_scale = max(0.8, L * 0.1)
        for f in st.session_state.forces:
            if abs(f['val']) > 0:
                f_x, f_y = f['dist']*c_ang, f['dist']*s_ang
                val_abs = abs(f['val'])
                stop_gap = 0.1
                if "Fx" in f['tip']:
                    dx = arrow_len_scale if f['val'] > 0 else -arrow_len_scale
                    ax1.arrow(f_x-dx, f_y, dx-np.sign(f['val'])*stop_gap, 0, head_width=0.1, fc='red', ec='red', length_includes_head=True, lw=2, zorder=10)
                    ax1.text(f_x-dx, f_y+0.2, f"{val_abs}kN", color='red', weight='bold', fontsize=10)
                elif "Fy" in f['tip']:
                    dy = arrow_len_scale if f['val'] > 0 else -arrow_len_scale
                    ax1.arrow(f_x, f_y-dy, 0, dy-np.sign(f['val'])*stop_gap, head_width=0.1, fc='red', ec='red', length_includes_head=True, lw=2, zorder=10)
                    ax1.text(f_x+0.2, f_y-dy, f"{val_abs}kN", color='red', weight='bold', fontsize=10)
                elif "Moment" in f['tip']:
                    ax1.plot(f_x, f_y, 'ro', ms=8)
                    semn = "↻" if f['val'] > 0 else "↺"
                    ax1.text(f_x+0.2, f_y+0.2, f"{val_abs}kNm {semn}", color='purple', weight='bold', fontsize=11)

        ax1.set_aspect('equal')
        margin = L * 0.15 + 0.5
        ax1.set_xlim(min(0, end_x) - margin, max(0, end_x) + margin)
        ax1.set_ylim(min(0, end_y) - margin, max(0, end_y) + margin)
        ax1.axis('off')
        st.pyplot(fig1)

        def solve_fem():
            raw_nodes = [0.0, L] + [f['dist'] for f in st.session_state.forces if abs(f['val']) > 0]
            if q_val > 0:
                raw_nodes.extend([q_start, q_end])
            nodes_s = np.unique(np.round(raw_nodes, 4)).tolist()
            num_nodes = len(nodes_s)
            num_elems = num_nodes - 1

            K_glob = np.zeros((3*num_nodes, 3*num_nodes))
            F_glob = np.zeros(3*num_nodes)

            T_blk = np.array([[c_ang, s_ang, 0], [-s_ang, c_ang, 0], [0, 0, 1]])
            T = np.zeros((6,6))
            T[0:3, 0:3] = T_blk
            T[3:6, 3:6] = T_blk

            for i in range(num_elems):
                L_e = nodes_s[i+1] - nodes_s[i]
                if L_e <= 0: continue
                k_loc = np.array([
                    [E*A/L_e, 0, 0, -E*A/L_e, 0, 0],
                    [0, 12*E*I/L_e**3, 6*E*I/L_e**2, 0, -12*E*I/L_e**3, 6*E*I/L_e**2],
                    [0, 6*E*I/L_e**2, 4*E*I/L_e, 0, -6*E*I/L_e**2, 2*E*I/L_e],
                    [-E*A/L_e, 0, 0, E*A/L_e, 0, 0],
                    [0, -12*E*I/L_e**3, -6*E*I/L_e**2, 0, 12*E*I/L_e**3, -6*E*I/L_e**2],
                    [0, 6*E*I/L_e**2, 2*E*I/L_e, 0, -6*E*I/L_e**2, 4*E*I/L_e]
                ])
                k_g = T.T @ k_loc @ T
                idx = slice(3*i, 3*i + 6)
                K_glob[idx, idx] += k_g

                midpoint_e = (nodes_s[i] + nodes_s[i+1]) / 2
                if q_val > 0 and (q_start - 1e-4 <= midpoint_e <= q_end + 1e-4):
                    q_vert = -q_val
                    q_y_loc = q_vert * c_ang
                    q_x_loc = q_vert * s_ang
                    f_eq_loc = np.array([
                        q_x_loc * L_e / 2, q_y_loc * L_e / 2, q_y_loc * (L_e**2) / 12,
                        q_x_loc * L_e / 2, q_y_loc * L_e / 2, -q_y_loc * (L_e**2) / 12
                    ])
                    f_eq_glob = T.T @ f_eq_loc
                    F_glob[idx] += f_eq_glob

            for f in st.session_state.forces:
                if abs(f['val']) > 0:
                    node_idx = nodes_s.index(np.round(f['dist'], 4))
                    if "Fx" in f['tip']: F_glob[3*node_idx] += f['val']
                    elif "Fy" in f['tip']: F_glob[3*node_idx + 1] += f['val']
                    elif "Moment" in f['tip']: F_glob[3*node_idx + 2] += f['val']

            blocked = []
            if r1 == 1: blocked += [0, 1]
            elif r1 == 2: blocked += [1]
            elif r1 == 3: blocked += [0, 1, 2]
            last = 3 * (num_nodes - 1)
            if r2 == 1: blocked += [last, last+1]
            elif r2 == 2: blocked += [last+1]
            elif r2 == 3: blocked += [last, last+1, last+2]

            free = [i for i in range(3*num_nodes) if i not in blocked]
            if len(free) == 0: raise ValueError("Sistem blocat")

            U_glob = np.zeros(3*num_nodes)
            U_glob[free] = np.linalg.solve(K_glob[np.ix_(free, free)], F_glob[free])
            Reac_glob = (K_glob @ U_glob) - F_glob

            x_plot, N_plot, V_plot, M_plot = [], [], [], []
            parabola_info = []
            key_labels = {'N': [], 'V': [], 'M': []}

            U_loc_full = np.zeros(3*num_nodes)
            for i in range(num_nodes):
                u_g = U_glob[3*i : 3*i+3]
                U_loc_full[3*i : 3*i+3] = T_blk @ u_g

            for i in range(num_elems):
                L_e = nodes_s[i+1] - nodes_s[i]
                if L_e == 0: continue
                k_loc = np.array([
                    [E*A/L_e, 0, 0, -E*A/L_e, 0, 0],
                    [0, 12*E*I/L_e**3, 6*E*I/L_e**2, 0, -12*E*I/L_e**3, 6*E*I/L_e**2],
                    [0, 6*E*I/L_e**2, 4*E*I/L_e, 0, -6*E*I/L_e**2, 2*E*I/L_e],
                    [-E*A/L_e, 0, 0, E*A/L_e, 0, 0],
                    [0, -12*E*I/L_e**3, -6*E*I/L_e**2, 0, 12*E*I/L_e**3, -6*E*I/L_e**2],
                    [0, 6*E*I/L_e**2, 2*E*I/L_e, 0, -6*E*I/L_e**2, 4*E*I/L_e]
                ])
                u_loc_e = np.concatenate((U_loc_full[3*i : 3*i+3], U_loc_full[3*(i+1) : 3*(i+1)+3]))
                f_eq_loc = np.zeros(6)
                midpoint_e = (nodes_s[i] + nodes_s[i+1]) / 2
                element_has_q = False
                q_y_loc = 0; q_x_loc = 0
                if q_val > 0 and (q_start - 1e-4 <= midpoint_e <= q_end + 1e-4):
                    element_has_q = True
                    q_vert = -q_val; q_y_loc = q_vert * c_ang; q_x_loc = q_vert * s_ang
                    f_eq_loc = np.array([
                        q_x_loc * L_e / 2, q_y_loc * L_e / 2, q_y_loc * (L_e**2) / 12,
                        q_x_loc * L_e / 2, q_y_loc * L_e / 2, -q_y_loc * (L_e**2) / 12
                    ])
                f_ends = k_loc @ u_loc_e - f_eq_loc
                N_start = -f_ends[0]; V_start = f_ends[1]; M_start = -f_ends[2]
                N_end = f_ends[3]; V_end = -f_ends[4]; M_end = f_ends[5]
                key_labels['N'].extend([(nodes_s[i], N_start), (nodes_s[i+1], N_end)])
                key_labels['V'].extend([(nodes_s[i], V_start), (nodes_s[i+1], V_end)])
                key_labels['M'].extend([(nodes_s[i], M_start), (nodes_s[i+1], M_end)])
                x_pts = np.linspace(0, L_e, 50)
                if element_has_q:
                    N_x = N_start + (-q_x_loc) * x_pts
                    V_x = V_start + q_y_loc * x_pts
                    M_x = M_start + V_start * x_pts + q_y_loc * (x_pts**2) / 2
                    if (V_start > 0 and V_end < 0):
                        x_zero = V_start / (-q_y_loc)
                        x_global = nodes_s[i] + x_zero
                        m_max_local = M_start + V_start * x_zero + q_y_loc * (x_zero**2)/2
                        parabola_info.append({'x': x_global, 'V_start': V_start, 'q_loc': -q_y_loc, 'M_max': m_max_local, 'M_start': M_start})
                        key_labels['M'].append((x_global, m_max_local))
                else:
                    N_x = N_start * np.ones_like(x_pts)
                    V_x = V_start * np.ones_like(x_pts)
                    M_x = M_start + V_start * x_pts
                x_plot.extend(nodes_s[i] + x_pts)
                N_plot.extend(N_x); V_plot.extend(V_x); M_plot.extend(M_x)

            return nodes_s, U_loc_full, U_glob, Reac_glob, {'x': x_plot, 'N': N_plot, 'V': V_plot, 'M': M_plot}, parabola_info, key_labels

        st.markdown("---")
        if st.button("Efectuează Calculul Structural", type="primary", use_container_width=True):
            if A == 0:
                st.error("Aria secțiunii este 0. Introduceți lățimea (b) și înălțimea (h).")
            else:
                try:
                    nx, U_local, U_glob_res, Reac_glob, forces_res, parabola_info, key_labels = solve_fem()
                    st.success("Calcul finalizat!")

                    Rx_A, Ry_A, M_A = Reac_glob[0], Reac_glob[1], Reac_glob[2]
                    Rx_B, Ry_B, M_B = Reac_glob[-3], Reac_glob[-2], Reac_glob[-1]

                    c_reac1, c_reac2 = st.columns(2)
                    with c_reac1:
                        st.markdown("**Nod START (x=0)**")
                        if r1 in [1, 3]: st.write(f"Hx = {Rx_A:.2f} kN")
                        if r1 in [1, 2, 3]: st.write(f"Vy = {Ry_A:.2f} kN")
                        if r1 == 3: st.write(f"M = {M_A:.2f} kNm")
                    with c_reac2:
                        st.markdown("**Nod END (x=L)**")
                        if r2 in [1, 3]: st.write(f"Hx = {Rx_B:.2f} kN")
                        if r2 in [1, 2, 3]: st.write(f"Vy = {Ry_B:.2f} kN")
                        if r2 == 3: st.write(f"M = {M_B:.2f} kNm")

                    max_def_loc = np.max(np.abs(U_local[1::3])) * 1000
                    idx_max_x = np.argmax(np.abs(U_glob_res[0::3])) * 3
                    idx_max_y = np.argmax(np.abs(U_glob_res[1::3])) * 3 + 1
                    max_dx = U_glob_res[idx_max_x] * 1000
                    max_dy = U_glob_res[idx_max_y] * 1000

                    st.markdown("---")
                    col_m1, col_m2, col_m3 = st.columns(3)
                    col_m1.metric("Săgeată (Perpendicular pe bară)", f"{max_def_loc:.2f} mm")
                    col_m2.metric("Deplasare U1 (Global X)", f"{max_dx:.2f} mm")
                    col_m3.metric("Deplasare U2 (Global Y)", f"{max_dy:.2f} mm")

                    fig_res, (ax_N, ax_V, ax_M) = plt.subplots(3, 1, figsize=(12, 10), sharex=True, dpi=300)

                    def plot_labels(ax, label_list, color):
                        seen = set()
                        for x, y in label_list:
                            coord = (round(x, 3), round(y, 2))
                            if coord not in seen and abs(y) > 0.01:
                                ax.text(x, y, f"{y:.2f}", color=color, fontsize=9, weight='bold',
                                        ha='center', va='center',
                                        bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=1))
                                seen.add(coord)

                    color_N = '#E63946'; color_V = '#2A9D8F'; color_M = '#1D3557'; color_axis = '#2B2D42'

                    max_n = max(abs(np.array(forces_res['N']))) if len(forces_res['N']) > 0 else 0
                    ax_N.fill_between(forces_res['x'], forces_res['N'], color=color_N, alpha=0.15)
                    ax_N.plot(forces_res['x'], forces_res['N'], color=color_N, lw=2.5)
                    ax_N.axhline(0, color=color_axis, lw=1.5)
                    ax_N.set_title(f"Forță Axială (N) [kN] | Max: {max_n:.2f}", weight='bold', color=color_N)
                    ax_N.grid(False); ax_N.axis('off')
                    ax_N.plot([0, L], [0, 0], color=color_axis, lw=1.5)
                    plot_labels(ax_N, key_labels['N'], '#92000A')

                    max_v = max(abs(np.array(forces_res['V']))) if len(forces_res['V']) > 0 else 0
                    ax_V.fill_between(forces_res['x'], forces_res['V'], color=color_V, alpha=0.15)
                    ax_V.plot(forces_res['x'], forces_res['V'], color=color_V, lw=2.5)
                    ax_V.axhline(0, color=color_axis, lw=1.5)
                    ax_V.set_title(f"Forță Tăietoare (V) [kN] | Max: {max_v:.2f}", weight='bold', color=color_V)
                    ax_V.grid(False); ax_V.axis('off')
                    ax_V.plot([0, L], [0, 0], color=color_axis, lw=1.5)
                    plot_labels(ax_V, key_labels['V'], '#004C42')

                    max_m = max(abs(np.array(forces_res['M']))) if len(forces_res['M']) > 0 else 0
                    ax_M.fill_between(forces_res['x'], forces_res['M'], color=color_M, alpha=0.15)
                    ax_M.plot(forces_res['x'], forces_res['M'], color=color_M, lw=2.5)
                    ax_M.axhline(0, color=color_axis, lw=1.5)
                    ax_M.invert_yaxis()
                    ax_M.set_title(f"Moment Încovoietor (M) [kNm] | Max: {max_m:.2f}", weight='bold', color=color_M)
                    ax_M.grid(False); ax_M.axis('off')
                    ax_M.plot([0, L], [0, 0], color=color_axis, lw=1.5)
                    plot_labels(ax_M, key_labels['M'], '#00142A')

                    plt.tight_layout()
                    st.pyplot(fig_res)

                    buf = BytesIO()
                    with PdfPages(buf) as pdf_out:
                        pdf_out.savefig(fig1, bbox_inches='tight')
                        pdf_out.savefig(fig_res, bbox_inches='tight')
                    st.download_button(
                        label="Descarcă Raport Complet (PDF cu Diagrame)",
                        data=buf.getvalue(),
                        file_name="Raport_FEM_Diagrame.pdf",
                        mime="application/pdf",
                        type="primary"
                    )

                    if len(parabola_info) > 0:
                        st.info("Calcul Didactic Moment Maxim pe Parabolă")
                        for p in parabola_info:
                            st.latex(rf"x_{{0}} = \frac{{V_{{st}}}}{{q}} = \frac{{{p['V_start']:.2f}}}{{{p['q_loc']:.2f}}} = {p['V_start']/p['q_loc']:.3f} \text{{ m}} \rightarrow x_{{global}} = {p['x']:.3f} \text{{ m}}")
                            st.latex(rf"M_{{max}} = {p['M_max']:.2f} \text{{ kNm}}")

                except np.linalg.LinAlgError:
                    st.error("MECANISM! Structura este instabilă.")

# ==========================================
# MODUL 2: GRINZI STATIC DETERMINATE
# ==========================================
elif modul == "2. Grinzi Static Determinate":
    st.header("Grinzi Drepte Static Determinate")
    st.markdown("Calcul reacțiuni, diagrame N, T, M conform metodelor din textbook (975-4.pdf)")

    tip_grinda = st.selectbox("Tip grindă", [
        "Grindă simplu rezemată (articulație + reazem simplu)",
        "Consolă (încastrare la stânga)",
        "Grindă cu consolă laterală",
    ])

    col1, col2 = st.columns(2)
    with col1:
        L_gr = st.number_input("Lungime deschidere L (m)", min_value=0.1, value=6.0, step=0.5)
        q_gr = st.number_input("Încărcare distribuită q (kN/m)", min_value=0.0, value=10.0, step=1.0)
        q_gr_start = st.number_input("q de la x1 (m)", min_value=0.0, max_value=float(L_gr), value=0.0)
        q_gr_end = st.number_input("q până la x2 (m)", min_value=float(q_gr_start), max_value=float(L_gr), value=float(L_gr))
    with col2:
        P_gr = st.number_input("Forță concentrată P (kN)", min_value=0.0, value=0.0, step=5.0)
        a_gr = st.number_input("Poziție P față de A (m)", min_value=0.0, max_value=float(L_gr), value=float(L_gr)/2)
        M0_gr = st.number_input("Moment concentrat M0 (kNm, + orar)", value=0.0, step=5.0)
        m0_pos = st.number_input("Poziție M0 față de A (m)", min_value=0.0, max_value=float(L_gr), value=float(L_gr)/2)

    if st.button("Calculează Grindă", type="primary"):
        # Calcul reacțiuni
        if "simplu rezemată" in tip_grinda:
            # Suma momente față de A = 0 => VB
            # q pe [x1, x2]: rezultantă Q = q*(x2-x1), la centrul intervalului
            Q_total = q_gr * (q_gr_end - q_gr_start)
            xQ = (q_gr_start + q_gr_end) / 2.0
            VB = (Q_total * xQ + P_gr * a_gr + M0_gr) / L_gr
            VA = Q_total + P_gr - VB
            HA = 0.0

            st.success(f"**Reacțiuni:** VA = {VA:.3f} kN | VB = {VB:.3f} kN | HA = {HA:.3f} kN")
            st.latex(rf"\sum M_A = 0 \Rightarrow V_B = \frac{{Q \cdot x_Q + P \cdot a + M_0}}{{L}} = \frac{{{Q_total:.2f} \cdot {xQ:.2f} + {P_gr:.2f} \cdot {a_gr:.2f} + {M0_gr:.2f}}}{{{L_gr:.2f}}} = {VB:.3f} \text{{ kN}}")
            st.latex(rf"\sum F_y = 0 \Rightarrow V_A = {VA:.3f} \text{{ kN}}")

            # Construire diagrame
            x_arr = np.linspace(0, L_gr, 500)
            T_arr = np.zeros_like(x_arr)
            M_arr = np.zeros_like(x_arr)
            N_arr = np.zeros_like(x_arr)

            for idx_x, x in enumerate(x_arr):
                # T(x) = VA - q*(x-x1) pentru x in [x1, x2]  - P*heaviside(x-a) - ...
                t = VA
                if x > q_gr_start:
                    xq_eff = min(x, q_gr_end) - q_gr_start
                    if xq_eff > 0:
                        t -= q_gr * xq_eff
                if x > a_gr and P_gr > 0:
                    t -= P_gr
                T_arr[idx_x] = t

                # M(x) = VA*x - q/2*(x-x1)^2 - P*(x-a) - M0*heaviside(x-m0_pos)
                m = VA * x
                if x > q_gr_start:
                    xq_eff = min(x, q_gr_end) - q_gr_start
                    if xq_eff > 0:
                        m -= q_gr / 2 * xq_eff**2
                    if x > q_gr_end:
                        # restul
                        pass
                if x > a_gr and P_gr > 0:
                    m -= P_gr * (x - a_gr)
                if x > m0_pos:
                    m -= M0_gr
                M_arr[idx_x] = m

        elif "Consolă" in tip_grinda:
            Q_total = q_gr * (q_gr_end - q_gr_start)
            xQ = (q_gr_start + q_gr_end) / 2.0
            VA = Q_total + P_gr
            HA = 0.0
            MA_fix = Q_total * xQ + P_gr * a_gr + M0_gr

            st.success(f"**Reacțiuni încastrare:** VA = {VA:.3f} kN | HA = {HA:.3f} kN | MA = {MA_fix:.3f} kNm")

            x_arr = np.linspace(0, L_gr, 500)
            T_arr = np.zeros_like(x_arr)
            M_arr = np.zeros_like(x_arr)
            N_arr = np.zeros_like(x_arr)

            for idx_x, x in enumerate(x_arr):
                # From right end (free end B)
                t = 0.0
                m = 0.0
                if x < a_gr and P_gr > 0:
                    t += P_gr
                    m += P_gr * (a_gr - x)
                if P_gr > 0 and x >= a_gr:
                    pass  # already passed
                # q contribution from right
                if q_gr_end > x:
                    xq_start_eff = max(x, q_gr_start)
                    xq_end_eff = q_gr_end
                    if xq_end_eff > xq_start_eff:
                        Q_right = q_gr * (xq_end_eff - xq_start_eff)
                        xQ_right = (xq_start_eff + xq_end_eff) / 2.0
                        t += Q_right
                        m += Q_right * (xQ_right - x)
                if x < m0_pos:
                    m += M0_gr
                T_arr[idx_x] = t
                M_arr[idx_x] = m
        else:
            # Grindă cu consolă: simplificare, tratată ca simplu rezemată extinsă
            Q_total = q_gr * (q_gr_end - q_gr_start)
            xQ = (q_gr_start + q_gr_end) / 2.0
            VB = (Q_total * xQ + P_gr * a_gr + M0_gr) / L_gr
            VA = Q_total + P_gr - VB
            HA = 0.0
            st.success(f"**Reacțiuni:** VA = {VA:.3f} kN | VB = {VB:.3f} kN | HA = {HA:.3f} kN")

            x_arr = np.linspace(0, L_gr, 500)
            T_arr = np.zeros_like(x_arr)
            M_arr = np.zeros_like(x_arr)
            N_arr = np.zeros_like(x_arr)
            for idx_x, x in enumerate(x_arr):
                t = VA
                if x > q_gr_start:
                    xq_eff = min(x, q_gr_end) - q_gr_start
                    if xq_eff > 0: t -= q_gr * xq_eff
                if x > a_gr and P_gr > 0: t -= P_gr
                T_arr[idx_x] = t

                m = VA * x
                if x > q_gr_start:
                    xq_eff = min(x, q_gr_end) - q_gr_start
                    if xq_eff > 0: m -= q_gr / 2 * xq_eff**2
                if x > a_gr and P_gr > 0: m -= P_gr * (x - a_gr)
                if x > m0_pos: m -= M0_gr
                M_arr[idx_x] = m

        # Valori caracteristice
        max_T = np.max(np.abs(T_arr))
        max_M = np.max(np.abs(M_arr))

        # Punct T=0 (M maxim)
        sign_changes = np.where(np.diff(np.sign(T_arr)))[0]

        col_r1, col_r2 = st.columns(2)
        col_r1.metric("T max", f"{max_T:.3f} kN")
        col_r2.metric("M max", f"{max_M:.3f} kNm")

        if len(sign_changes) > 0:
            for sc in sign_changes:
                x0 = x_arr[sc]
                m0_val = M_arr[sc]
                st.info(f"T=0 la x ≈ {x0:.3f} m → M = {m0_val:.3f} kNm")

        # Plot diagrame
        fig, axes = plt.subplots(3, 1, figsize=(12, 9), dpi=150, sharex=True)

        colors = ['#E63946', '#2A9D8F', '#1D3557']
        labels = ['N (kN)', 'T (kN)', 'M (kNm)']
        data = [N_arr, T_arr, M_arr]

        for ax, dat, col, lab in zip(axes, data, colors, labels):
            ax.fill_between(x_arr, dat, alpha=0.18, color=col)
            ax.plot(x_arr, dat, color=col, lw=2.5)
            ax.axhline(0, color='black', lw=1.5)
            ax.set_ylabel(lab, color=col, fontsize=11, weight='bold')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.grid(True, alpha=0.3)

        # M invers (fibra întinsă jos)
        axes[2].invert_yaxis()
        axes[2].set_xlabel("x (m)", fontsize=11)
        fig.suptitle("Diagrame Eforturi N, T, M", fontsize=14, weight='bold')
        plt.tight_layout()
        st.pyplot(fig)

        # Formule explicative
        with st.expander("Formule și explicații"):
            st.latex(r"V_B = \frac{\sum M_A}{L} \quad ; \quad V_A = \sum F_y - V_B")
            st.latex(r"T(x) = V_A - q \cdot (x - x_1) - P \cdot H(x-a)")
            st.latex(r"M(x) = V_A \cdot x - \frac{q}{2}(x-x_1)^2 - P(x-a) \cdot H(x-a)")
            st.latex(r"M_{max} = \frac{q \cdot L^2}{8} \text{ (grindă simplu rezemată, q pe toată lungimea)}")
            st.markdown("**Reguli diagrame (din 975-4.pdf, Cap. 1):**")
            st.markdown("- Diagrama M se trasează pe fibra întinsă")
            st.markdown("- La forțe concentrate → salturi în T, schimbare de pantă în M")
            st.markdown("- La q uniform → T variatie lineară, M parabolă grad II")
            st.markdown("- M maxim unde T = 0")

# ==========================================
# MODUL 3: GRINZI GERBER
# ==========================================
elif modul == "3. Grinzi Gerber":
    st.header("Grinzi cu Articulații Intermediare (Grinzi Gerber)")
    st.markdown("Calcul conform metodei din textbook: desprinderea grinzilor secundare, calcul reacțiuni, trasare diagrame.")

    with st.expander("Teorie: Principii Grinzi Gerber (975-4.pdf, Cap. 2)", expanded=False):
        st.markdown("""
**Grinda Gerber** este o grindă cu articulații intermediare care o face static determinată.

**Algoritm rezolvare (din textbook):**
1. Se identifică **Grinda Secundară (G.S.)** = cea care are cel mult o legătură cu terenul; se desprinde din structură
2. Se calculează **reacțiunile G.S.** din încărcările direct aplicate pe ea
3. Pe **Grinda Principală (G.P.)** se aplică: încărcările proprii + reacțiunile din articulație (= acțiunile G.S. luate cu semn opus)
4. Se calculează reacțiunile finale ale G.P.
5. Se trasează diagramele N, T, M pe fiecare segment

**Proprietăți articulație intermediară:**
- M = 0 în articulație (nu transmite moment încovoietor)
- T ≠ 0 (transmite forță tăietoare)
- N ≠ 0 (transmite efort axial)
        """)
        st.latex(r"G = r - 3 - a = 0 \quad \text{(condiție SSD)}")
        st.markdown("unde: r = nr. reacțiuni, a = nr. articulații intermediare")

    st.subheader("Calculator Grindă Gerber cu o articulație intermediară")

    col1, col2, col3 = st.columns(3)
    with col1:
        L_GP = st.number_input("Lungime Grindă Principală (m)", min_value=1.0, value=8.0, step=0.5)
        q_GP = st.number_input("q pe G.P. (kN/m)", min_value=0.0, value=15.0, step=1.0)
    with col2:
        L_GS = st.number_input("Lungime Grindă Secundară (m)", min_value=0.5, value=4.0, step=0.5)
        q_GS = st.number_input("q pe G.S. (kN/m)", min_value=0.0, value=10.0, step=1.0)
    with col3:
        P_GS = st.number_input("Forță concentrată P pe G.S. (kN)", min_value=0.0, value=0.0, step=5.0)
        a_PS = st.number_input("Poziție P față de articulație (m)", min_value=0.0, max_value=float(L_GS), value=float(L_GS)/2)

    if st.button("Calculează Grindă Gerber", type="primary"):
        # G.S. = grindă simplu rezemată (articulație stânga, reazem simplu dreapta)
        Q_GS = q_GS * L_GS
        VD_GS = (Q_GS * L_GS/2 + P_GS * a_PS) / L_GS
        VB_GS_art = Q_GS + P_GS - VD_GS  # reacțiune în articulație (B)

        st.subheader("Pas 1 & 2: Grinda Secundară")
        st.success(f"Reacție în articulație B (↑ pe G.S.): VB = {VB_GS_art:.3f} kN | Reacție reazem D: VD = {VD_GS:.3f} kN")
        st.latex(rf"\sum M_B = 0 \Rightarrow V_D = \frac{{q \cdot L_{{GS}}^2/2 + P \cdot a}}{{L_{{GS}}}} = {VD_GS:.3f} \text{{ kN}}")

        st.subheader("Pas 3 & 4: Grinda Principală")
        # G.P. = articulație A, reazem simplu C, cu forța VB_GS aplicată în articulație B (la distanța L_GP-L_GS de A)
        xB_GP = L_GP - L_GS  # poziția articulației B pe G.P.
        Q_GP = q_GP * L_GP
        # Suma momente față de A:
        VC_GP = (Q_GP * L_GP/2 + VB_GS_art * xB_GP) / L_GP
        VA_GP = Q_GP + VB_GS_art - VC_GP

        st.success(f"Reacție A (G.P.): VA = {VA_GP:.3f} kN | Reacție C: VC = {VC_GP:.3f} kN")
        st.latex(rf"\sum M_A = 0 \Rightarrow V_C = \frac{{q_{{GP}} \cdot L_{{GP}}^2/2 + V_B^{{GS}} \cdot x_B}}{{L_{{GP}}}} = {VC_GP:.3f} \text{{ kN}}")

        # Diagrame
        # Segment G.P. (de la 0 la L_GP-L_GS) + Segment G.S. (de la L_GP-L_GS la L_GP)
        x_GP = np.linspace(0, xB_GP, 300)
        x_GS = np.linspace(xB_GP, L_GP, 300)
        x_tot = np.concatenate([x_GP, x_GS])

        T_GP = np.zeros_like(x_GP)
        M_GP = np.zeros_like(x_GP)
        for i, x in enumerate(x_GP):
            T_GP[i] = VA_GP - q_GP * x
            M_GP[i] = VA_GP * x - q_GP * x**2 / 2

        T_GS = np.zeros_like(x_GS)
        M_GS = np.zeros_like(x_GS)
        for i, x in enumerate(x_GS):
            xi = x - xB_GP  # coordonată locală pe G.S.
            T_GS[i] = VB_GS_art - q_GS * xi
            if xi > a_PS and P_GS > 0:
                T_GS[i] -= P_GS
            M_GS[i] = VB_GS_art * xi - q_GS * xi**2 / 2
            if xi > a_PS and P_GS > 0:
                M_GS[i] -= P_GS * (xi - a_PS)

        T_tot = np.concatenate([T_GP, T_GS])
        M_tot = np.concatenate([M_GP, M_GS])

        fig, axes = plt.subplots(2, 1, figsize=(12, 7), sharex=True, dpi=150)
        axes[0].fill_between(x_tot, T_tot, alpha=0.18, color='#2A9D8F')
        axes[0].plot(x_tot, T_tot, color='#2A9D8F', lw=2.5)
        axes[0].axhline(0, color='k', lw=1.5)
        axes[0].axvline(xB_GP, color='red', lw=1.5, linestyle='--', label=f'Articulație x={xB_GP}m')
        axes[0].set_ylabel("T (kN)", weight='bold', color='#2A9D8F')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)

        axes[1].fill_between(x_tot, M_tot, alpha=0.18, color='#1D3557')
        axes[1].plot(x_tot, M_tot, color='#1D3557', lw=2.5)
        axes[1].axhline(0, color='k', lw=1.5)
        axes[1].axvline(xB_GP, color='red', lw=1.5, linestyle='--', label=f'Articulație x={xB_GP}m (M=0)')
        axes[1].set_ylabel("M (kNm)", weight='bold', color='#1D3557')
        axes[1].set_xlabel("x (m)")
        axes[1].invert_yaxis()
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)

        # Verificare M=0 în articulație
        M_in_art = M_GP[-1]
        fig.suptitle(f"Diagrame Grindă Gerber | M în articulație = {M_in_art:.4f} kNm (≈0 ✓)", weight='bold')
        plt.tight_layout()
        st.pyplot(fig)

        st.info(f"Verificare: M în articulație = {M_in_art:.4f} kNm (trebuie să fie ≈ 0)")
        col_r1, col_r2 = st.columns(2)
        col_r1.metric("T max (G.P.)", f"{np.max(np.abs(T_GP)):.2f} kN")
        col_r2.metric("M max (total)", f"{np.max(np.abs(M_tot)):.2f} kNm")

# ==========================================
# MODUL 4: CADRE STATIC DETERMINATE
# ==========================================
elif modul == "4. Cadre Static Determinate":
    st.header("Cadre Static Determinate")
    st.markdown("Calcul reacțiuni și diagrame N, T, M conform 975-4.pdf Cap. 3")

    with st.expander("Teorie: Principii Cadre Static Determinate", expanded=False):
        st.markdown("""
**Cadre static determinate** - structuri din bare rigide conectate în noduri rigide sau articulate.

**Condiție SSD:** `3 * nr_bare + nr_reacții_externe = 3 * nr_noduri + nr_articulații_interne`

**Metoda de calcul:**
1. Se scriu 3 ecuații de echilibru global (ΣFx=0, ΣFy=0, ΣM=0)
2. Dacă există articulație internă: ecuație suplimentară (M=0 în articulație)
3. Se trasează diagramele pe fiecare bară, tratând-o ca grindă dreaptă

**Convenții semne:**
- N > 0 = întindere (tracțiune)
- T: semn convențional (pozitiv dacă rotește tronsonul în sens orar)
- M se trasează pe fibra întinsă
        """)
        st.latex(r"\text{Cadru simplu rezemat: } \sum M_A=0, \sum M_B=0, \sum F_x=0")
        st.latex(r"\text{Cadru cu 3 articulații: } \sum M_{A}^{st}=0, \sum M_{A}^{dr}=0")

    st.subheader("Cadru Portal (2 stâlpi + 1 grindă)")

    col1, col2 = st.columns(2)
    with col1:
        H_stlp = st.number_input("Înălțime stâlpi h (m)", min_value=1.0, value=4.0, step=0.5)
        L_gr_c = st.number_input("Deschidere grindă L (m)", min_value=1.0, value=6.0, step=0.5)
        q_gr_c = st.number_input("q pe grindă (kN/m)", min_value=0.0, value=20.0, step=1.0)
    with col2:
        H_vant = st.number_input("Forță orizontală (vânt) pe stâlpul stg. (kN)", min_value=0.0, value=0.0, step=1.0)
        tip_cadru = st.selectbox("Tip rezemare", ["Articulație A + Articulație B", "Încastrare A + Articulație B"])
        P_concentrat = st.number_input("Forță P pe grindă (kN)", min_value=0.0, value=0.0, step=5.0)
        a_P_c = st.number_input("Poziție P de la A (m)", min_value=0.0, max_value=float(L_gr_c), value=float(L_gr_c)/2)

    if st.button("Calculează Cadru", type="primary"):
        Q_gr = q_gr_c * L_gr_c
        # Echilibru cadru portal simplu:
        # ΣFx=0: HA + HB = H_vant
        # ΣMB=0: VA*L - Q_gr*L/2 - P*（L-a) - H_vant*H_stlp = 0  (pt. articulatii)
        # ΣMA=0: VB*L - Q_gr*L/2 - P*a + H_vant*H_stlp ... (depinde de tip)

        if "Articulație A + Articulație B" in tip_cadru:
            # 4 necunoscute: VA, VB, HA, HB -> 3 ec. + ΣMA=0
            # ΣFx: HA + HB = H_vant (fara alte forte orizontale)
            # ΣMA=0: VB*L - Q*L/2 - P*(L-a_P_c) + H_vant*0 = 0 (momentul vantului -> H_vant*H_stlp pe verticalul A)
            # Simplificat: pentru cadru cu 2 articulatii la baza si grinda orizontala:
            # ΣMA_global=0 => VB*L = Q_gr*L/2 + P*a_P_c - H_vant*H_stlp (moment vant fata de A)
            VB_c = (Q_gr * L_gr_c/2 + P_concentrat * a_P_c - H_vant * H_stlp) / L_gr_c
            VA_c = Q_gr + P_concentrat - VB_c
            # ΣFx=0: HA + HB = H_vant  (HB=0 pt. articulatie simpla fara moment)
            # Pt. cadru cu 2 articulatii la baza, ΣMC (nod de coama) = 0 pe jumatate stanga:
            # VA*L/2 - Q_gr*L^2/8 + HA*H - H_vant*H^2/2 = ... depinde de geometrie
            # Simplificat pentru cadru dreptunghic:
            HB_c = 0.0  # reazem simplu vert in B
            HA_c = H_vant  # echilibru
            st.success(f"VA={VA_c:.3f} kN | VB={VB_c:.3f} kN | HA={HA_c:.3f} kN | HB={HB_c:.3f} kN")
        else:
            # Încastrare A: MA, HA, VA + articulatie B: VB, HB
            VB_c = (Q_gr * L_gr_c/2 + P_concentrat * a_P_c) / L_gr_c
            VA_c = Q_gr + P_concentrat - VB_c
            HA_c = H_vant
            HB_c = 0.0
            MA_c = HA_c * H_stlp - H_vant * H_stlp  # simplificat
            st.success(f"VA={VA_c:.3f} kN | VB={VB_c:.3f} kN | HA={HA_c:.3f} kN | HB={HB_c:.3f} kN")

        # Construire diagrame vizuale
        x_gr_arr = np.linspace(0, L_gr_c, 200)
        T_gr_arr = np.zeros_like(x_gr_arr)
        M_gr_arr = np.zeros_like(x_gr_arr)
        N_gr_arr = np.zeros_like(x_gr_arr)

        for i, x in enumerate(x_gr_arr):
            T_gr_arr[i] = VA_c - q_gr_c * x - (P_concentrat if x > a_P_c else 0)
            M_gr_arr[i] = VA_c * x - q_gr_c * x**2/2 - (P_concentrat*(x-a_P_c) if x > a_P_c else 0)

        # Stâlpi: N = reactiune verticala, T = reactiune orizontala
        y_st = np.linspace(0, H_stlp, 100)
        N_stlp_stg = -VA_c  # compresiune
        T_stlp_stg_arr = HA_c * np.ones_like(y_st)
        M_stlp_stg_arr = HA_c * y_st  # moment creste de jos in sus

        fig_c, axes_c = plt.subplots(1, 3, figsize=(15, 7), dpi=150)

        # Plot cadru schematic
        ax = axes_c[0]
        ax.set_aspect('equal')
        # Stâlpi
        ax.plot([0, 0], [0, H_stlp], 'k-', lw=3)
        ax.plot([L_gr_c, L_gr_c], [0, H_stlp], 'k-', lw=3)
        # Grindă
        ax.plot([0, L_gr_c], [H_stlp, H_stlp], 'k-', lw=3)
        # Reazeme
        ax.plot(0, 0, '^', ms=14, color='orange', markeredgecolor='k')
        ax.plot(L_gr_c, 0, '^', ms=14, color='orange', markeredgecolor='k')
        # Incarcari
        for xx in np.linspace(0, L_gr_c, 8):
            ax.arrow(xx, H_stlp + 0.5, 0, -0.4, head_width=0.1, fc='blue', ec='blue', length_includes_head=True)
        ax.text(L_gr_c/2, H_stlp + 0.7, f"q={q_gr_c} kN/m", ha='center', color='blue', weight='bold')
        if H_vant > 0:
            ax.arrow(-0.8, H_stlp/2, 0.7, 0, head_width=0.15, fc='red', ec='red', length_includes_head=True)
            ax.text(-1.2, H_stlp/2, f"H={H_vant}kN", color='red', fontsize=9)
        ax.text(-0.3, -0.3, f"VA={VA_c:.1f}kN", ha='right', fontsize=9)
        ax.text(L_gr_c+0.1, -0.3, f"VB={VB_c:.1f}kN", ha='left', fontsize=9)
        ax.set_xlim(-1.5, L_gr_c + 1.5)
        ax.set_ylim(-0.8, H_stlp + 1.2)
        ax.axis('off')
        ax.set_title("Schema Cadrului", weight='bold')

        # Plot M pe grindă
        ax2 = axes_c[1]
        ax2.fill_between(x_gr_arr, M_gr_arr, alpha=0.2, color='#1D3557')
        ax2.plot(x_gr_arr, M_gr_arr, color='#1D3557', lw=2)
        ax2.axhline(0, color='k', lw=1)
        ax2.invert_yaxis()
        ax2.set_title(f"M pe Grindă (kNm)\nMmax={np.max(np.abs(M_gr_arr)):.2f}", weight='bold')
        ax2.set_xlabel("x (m)")
        ax2.grid(True, alpha=0.3)

        # Plot M pe stâlp stâng
        ax3 = axes_c[2]
        ax3.fill_betweenx(y_st, M_stlp_stg_arr, alpha=0.2, color='#E63946')
        ax3.plot(M_stlp_stg_arr, y_st, color='#E63946', lw=2)
        ax3.axvline(0, color='k', lw=1)
        ax3.set_title(f"M Stâlp Stg. (kNm)\nMmax={HA_c*H_stlp:.2f}", weight='bold')
        ax3.set_ylabel("y (m)")
        ax3.grid(True, alpha=0.3)

        plt.tight_layout()
        st.pyplot(fig_c)

        col_r1, col_r2, col_r3 = st.columns(3)
        col_r1.metric("M max grindă", f"{np.max(np.abs(M_gr_arr)):.2f} kNm")
        col_r2.metric("N stâlp stg.", f"{abs(N_stlp_stg):.2f} kN")
        col_r3.metric("M baza stâlp stg.", f"{HA_c*H_stlp:.2f} kNm")

# ==========================================
# MODUL 5: ARCE STATIC DETERMINATE
# ==========================================
elif modul == "5. Arce Static Determinate":
    st.header("Arce Static Determinate")
    st.markdown("Arc parabolice cu 3 articulații (A, B, C=coamă) - conform 975-4.pdf Cap. 4")

    with st.expander("Teorie: Arce cu 3 Articulații", expanded=False):
        st.markdown("""
**Arcul cu 3 articulații** este static determinat:
- Articulații la reazeme (A, B) + articulație la coamă (C)

**Formele arcului:** parabolică, circulară, polinomială

**Ecuația parabolei:** `y(x) = 4f/L² · x · (L-x)`

**Calcul reacțiuni:**
- Din ΣM_A=0 → VB
- Din ΣM_B=0 → VA
- Din ΣM_C(stg)=0 → H (reacțiunea orizontală = împingerea arcului)
- ΣFx=0 → verificare

**Efortul axial** în arc (compresiune):
- `N = -√(V² + H²)` în general

**Formula Mmax pentru arc cu q uniform:**
- Arcul parabolice cu q pe proiecție orizontală → M=0 în toate secțiunile!
        """)
        st.latex(r"H = \frac{q \cdot L^2}{8 \cdot f}")
        st.latex(r"M(x) = M_0(x) - H \cdot y(x)")
        st.markdown("unde M₀ este momentul grinzii echivalente simplu rezemate")

    col1, col2 = st.columns(2)
    with col1:
        L_arc = st.number_input("Deschidere arc L (m)", min_value=1.0, value=12.0, step=1.0)
        f_arc = st.number_input("Săgeata arcului f (m)", min_value=0.1, value=3.0, step=0.5)
        q_arc = st.number_input("Încărcare q (kN/m) pe proiecție orizontală", min_value=0.0, value=20.0, step=1.0)
    with col2:
        P_arc = st.number_input("Forță concentrată P (kN)", min_value=0.0, value=0.0, step=5.0)
        a_arc = st.number_input("Poziție P față de A (m)", min_value=0.0, max_value=float(L_arc), value=float(L_arc)/3)

    if st.button("Calculează Arc", type="primary"):
        # Geometrie arc parabolice
        x_arr = np.linspace(0, L_arc, 500)
        y_arc = 4 * f_arc / L_arc**2 * x_arr * (L_arc - x_arr)

        # Reacțiuni
        Q = q_arc * L_arc
        # ΣMB=0: VA*L - q*L²/2 - P*(L-a) = 0
        VB = (Q * L_arc/2 + P_arc * a_arc) / L_arc
        VA = Q + P_arc - VB
        HA_arc = HB_arc = 0.0  # initial

        # Ecuație articulatie coamă: ΣM_C_stg = 0
        # VA * L/2 - q*(L/2)^2/2 - H*f = 0
        y_C = f_arc  # coama la x=L/2
        M0_C = VA * L_arc/2 - q_arc * (L_arc/2)**2 / 2
        if P_arc > 0 and a_arc < L_arc/2:
            M0_C -= P_arc * (L_arc/2 - a_arc)
        H_arc = M0_C / f_arc

        st.success(f"VA = {VA:.3f} kN | VB = {VB:.3f} kN | H = {H_arc:.3f} kN (împingere)")
        st.latex(rf"H = \frac{{M_0^C}}{{f}} = \frac{{{M0_C:.2f}}}{{{f_arc:.2f}}} = {H_arc:.3f} \text{{ kN}}")

        # Diagrame eforturi
        M0_arr = VA * x_arr - q_arc * x_arr**2 / 2
        if P_arc > 0:
            for i, x in enumerate(x_arr):
                if x > a_arc:
                    M0_arr[i] -= P_arc * (x - a_arc)

        M_arc_arr = M0_arr - H_arc * y_arc

        # Forța axială: N = -H/cos(θ) ≈ -√(T² + H²) simplificat
        dy_dx = 4 * f_arc / L_arc**2 * (L_arc - 2*x_arr)
        T0_arr = VA * np.ones_like(x_arr) - q_arc * x_arr
        if P_arc > 0:
            for i, x in enumerate(x_arr):
                if x > a_arc:
                    T0_arr[i] -= P_arc
        T_arc_arr = T0_arr - H_arc * dy_dx  # proiectat perpendicular pe arc
        N_arc_arr = -(H_arc * np.cos(np.arctan(dy_dx)) + T0_arr * np.sin(np.arctan(dy_dx)))

        fig_a, axes_a = plt.subplots(2, 2, figsize=(14, 9), dpi=150)

        # Arc geometrie
        axes_a[0,0].plot(x_arr, y_arc, 'k-', lw=3, label='Arc')
        axes_a[0,0].plot([0, L_arc], [0, 0], 'k--', lw=1)
        axes_a[0,0].plot(0, 0, '^', ms=14, color='orange', markeredgecolor='k')
        axes_a[0,0].plot(L_arc, 0, '^', ms=14, color='orange', markeredgecolor='k')
        axes_a[0,0].plot(L_arc/2, f_arc, 'ro', ms=10, label=f'Coamă C (f={f_arc}m)')
        axes_a[0,0].set_aspect('equal')
        axes_a[0,0].set_title("Geometrie Arc Parabolice", weight='bold')
        axes_a[0,0].legend()
        axes_a[0,0].grid(True, alpha=0.3)

        # M diagram
        axes_a[0,1].fill_between(x_arr, M_arc_arr, alpha=0.2, color='#1D3557')
        axes_a[0,1].plot(x_arr, M_arc_arr, color='#1D3557', lw=2)
        axes_a[0,1].axhline(0, color='k', lw=1)
        axes_a[0,1].set_title(f"M (kNm) | Mmax={np.max(np.abs(M_arc_arr)):.3f}", weight='bold')
        axes_a[0,1].invert_yaxis()
        axes_a[0,1].grid(True, alpha=0.3)

        # T diagram
        axes_a[1,0].fill_between(x_arr, T_arc_arr, alpha=0.2, color='#2A9D8F')
        axes_a[1,0].plot(x_arr, T_arc_arr, color='#2A9D8F', lw=2)
        axes_a[1,0].axhline(0, color='k', lw=1)
        axes_a[1,0].set_title("T (kN)", weight='bold')
        axes_a[1,0].grid(True, alpha=0.3)

        # N diagram
        axes_a[1,1].fill_between(x_arr, N_arc_arr, alpha=0.2, color='#E63946')
        axes_a[1,1].plot(x_arr, N_arc_arr, color='#E63946', lw=2)
        axes_a[1,1].axhline(0, color='k', lw=1)
        axes_a[1,1].set_title(f"N (kN) | Nmax={np.min(N_arc_arr):.2f}", weight='bold')
        axes_a[1,1].grid(True, alpha=0.3)

        for ax in axes_a.flat:
            ax.set_xlabel("x (m)")

        plt.tight_layout()
        st.pyplot(fig_a)

        col_r1, col_r2, col_r3 = st.columns(3)
        col_r1.metric("H (împingere)", f"{H_arc:.3f} kN")
        col_r2.metric("M max", f"{np.max(np.abs(M_arc_arr)):.4f} kNm")
        col_r3.metric("N min (compresiune)", f"{np.min(N_arc_arr):.2f} kN")

        if q_arc > 0 and P_arc == 0:
            if np.max(np.abs(M_arc_arr)) < 0.01 * q_arc * L_arc**2 / 8:
                st.success("Arc parabolice cu q pe proj. orizontala → M ≈ 0 în toate secțiunile! (arc funicular)")
            st.latex(rf"H = \frac{{q \cdot L^2}}{{8f}} = \frac{{{q_arc} \cdot {L_arc}^2}}{{8 \cdot {f_arc}}} = {q_arc*L_arc**2/(8*f_arc):.3f} \text{{ kN}}")

# ==========================================
# MODUL 6: REZISTENȚA MATERIALELOR
# ==========================================
elif modul == "6. Rezistența Materialelor":
    st.header("Rezistența Materialelor (481-0.pdf)")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Caracteristici Geometrice",
        "Întindere/Compresiune",
        "Încovoiere",
        "Forfecare / Torsiune",
        "Flambaj"
    ])

    # TAB 1: CARACTERISTICI GEOMETRICE
    with tab1:
        st.subheader("Caracteristici Geometrice Secțiuni (Lucrarea 5)")
        st.markdown("Calcul arie, centru de greutate, momente de inerție, module de rezistență")

        tip_sect = st.selectbox("Tip secțiune", [
            "Dreptunghi simplu",
            "Secțiune T (platbandă + inimă)",
            "Secțiune I simetrică",
            "Cerc plin",
            "Inel circular (țeavă)",
        ])

        if tip_sect == "Dreptunghi simplu":
            c1, c2 = st.columns(2)
            b_s = c1.number_input("Lățime b (cm)", min_value=0.1, value=20.0)
            h_s = c2.number_input("Înălțime h (cm)", min_value=0.1, value=40.0)

            A_s = b_s * h_s
            Iy = b_s * h_s**3 / 12
            Iz = h_s * b_s**3 / 12
            Wy = Iy / (h_s/2)
            Wz = Iz / (b_s/2)
            iy = np.sqrt(Iy / A_s)
            iz = np.sqrt(Iz / A_s)

            st.success(f"A = {A_s:.2f} cm² | Iy = {Iy:.2f} cm⁴ | Iz = {Iz:.2f} cm⁴ | Wy = {Wy:.2f} cm³")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("A (cm²)", f"{A_s:.2f}")
            col2.metric("Iy (cm⁴)", f"{Iy:.2f}")
            col3.metric("Wy (cm³)", f"{Wy:.2f}")
            col4.metric("iy (cm)", f"{iy:.2f}")

            st.latex(rf"I_y = \frac{{b \cdot h^3}}{{12}} = \frac{{{b_s:.1f} \cdot {h_s:.1f}^3}}{{12}} = {Iy:.2f} \text{{ cm}}^4")
            st.latex(rf"W_y = \frac{{I_y}}{{h/2}} = \frac{{{Iy:.2f}}}{{{h_s/2:.1f}}} = {Wy:.2f} \text{{ cm}}^3")

        elif tip_sect == "Secțiune T (platbandă + inimă)":
            c1, c2 = st.columns(2)
            b_t = c1.number_input("Lățime talpă bt (cm)", min_value=1.0, value=24.0)
            tt = c1.number_input("Grosime talpă tt (cm)", min_value=0.1, value=1.6)
            h_i = c2.number_input("Înălțime inimă hi (cm)", min_value=1.0, value=33.5)
            ti = c2.number_input("Grosime inimă ti (cm)", min_value=0.1, value=0.8)

            # Arii
            A1 = b_t * tt  # talpă
            A2 = h_i * ti  # inimă
            A_tot = A1 + A2

            # CG față de baza inferioară
            z1 = h_i + tt/2  # centrul talpă față de baza
            z2 = h_i/2       # centrul inimii față de baza

            zG = (A1*z1 + A2*z2) / A_tot

            # Momente de inerție (Steiner)
            Iy1 = b_t * tt**3/12 + A1*(z1-zG)**2
            Iy2 = ti * h_i**3/12 + A2*(z2-zG)**2
            Iy_T = Iy1 + Iy2

            # Module
            z_max = max(zG, h_i+tt - zG)
            Wy_T = Iy_T / z_max

            col1, col2, col3 = st.columns(3)
            col1.metric("A (cm²)", f"{A_tot:.2f}")
            col2.metric("zG de la baza (cm)", f"{zG:.2f}")
            col3.metric("Iy (cm⁴)", f"{Iy_T:.2f}")
            col1.metric("Wy (cm³)", f"{Wy_T:.2f}")

            st.latex(rf"z_G = \frac{{A_1 \cdot z_1 + A_2 \cdot z_2}}{{A_1+A_2}} = \frac{{{A1:.2f} \cdot {z1:.2f} + {A2:.2f} \cdot {z2:.2f}}}{{{A_tot:.2f}}} = {zG:.2f} \text{{ cm}}")
            st.latex(rf"I_y = \sum\left(I_{{y_i}} + A_i \cdot d_i^2\right) = {Iy_T:.2f} \text{{ cm}}^4 \quad \text{{(Teorema lui Steiner)}}")

            # Desenare secțiune
            fig_s, ax_s = plt.subplots(figsize=(5, 6), dpi=120)
            from matplotlib.patches import Rectangle
            ax_s.add_patch(Rectangle((-b_t/2, h_i), b_t, tt, fill=True, facecolor='steelblue', edgecolor='k', lw=2))
            ax_s.add_patch(Rectangle((-ti/2, 0), ti, h_i, fill=True, facecolor='steelblue', edgecolor='k', lw=2))
            ax_s.axhline(zG, color='red', lw=2, linestyle='--', label=f'CG (zG={zG:.2f}cm)')
            ax_s.set_xlim(-b_t/2-1, b_t/2+1)
            ax_s.set_ylim(-1, h_i+tt+1)
            ax_s.set_aspect('equal')
            ax_s.legend()
            ax_s.set_title("Secțiune T", weight='bold')
            ax_s.set_xlabel("y (cm)"); ax_s.set_ylabel("z (cm)")
            st.pyplot(fig_s)

        elif tip_sect == "Cerc plin":
            d_s = st.number_input("Diametru d (cm)", min_value=0.1, value=20.0)
            r_s = d_s/2
            A_c = np.pi * r_s**2
            I_c = np.pi * d_s**4 / 64
            W_c = np.pi * d_s**3 / 32
            i_c = r_s/2

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("A (cm²)", f"{A_c:.2f}")
            col2.metric("I (cm⁴)", f"{I_c:.2f}")
            col3.metric("W (cm³)", f"{W_c:.2f}")
            col4.metric("i (cm)", f"{i_c:.2f}")
            st.latex(rf"I = \frac{{\pi d^4}}{{64}} = \frac{{\pi \cdot {d_s:.1f}^4}}{{64}} = {I_c:.2f} \text{{ cm}}^4")
            st.latex(rf"W = \frac{{\pi d^3}}{{32}} = {W_c:.2f} \text{{ cm}}^3")

        elif tip_sect == "Inel circular (țeavă)":
            D_s = st.number_input("Diametru exterior D (cm)", min_value=1.0, value=20.0)
            d_s2 = st.number_input("Diametru interior d (cm)", min_value=0.1, max_value=float(D_s)-0.1, value=16.0)
            A_in = np.pi/4 * (D_s**2 - d_s2**2)
            I_in = np.pi/64 * (D_s**4 - d_s2**4)
            W_in = I_in / (D_s/2)
            st.latex(rf"I = \frac{{\pi(D^4-d^4)}}{{64}} = {I_in:.2f} \text{{ cm}}^4")
            col1, col2, col3 = st.columns(3)
            col1.metric("A (cm²)", f"{A_in:.2f}")
            col2.metric("I (cm⁴)", f"{I_in:.2f}")
            col3.metric("W (cm³)", f"{W_in:.2f}")

        elif tip_sect == "Secțiune I simetrică":
            c1, c2 = st.columns(2)
            B_I = c1.number_input("Lățime tălpi B (cm)", min_value=1.0, value=20.0)
            t_f = c1.number_input("Grosime talpă tf (cm)", min_value=0.1, value=1.5)
            H_I = c2.number_input("Înălțime totală H (cm)", min_value=1.0, value=40.0)
            t_w = c2.number_input("Grosime inimă tw (cm)", min_value=0.1, value=1.0)

            h_w = H_I - 2*t_f  # înălțime inimă
            A_I = 2*B_I*t_f + h_w*t_w
            I_I = B_I*H_I**3/12 - (B_I-t_w)*h_w**3/12
            W_I = I_I / (H_I/2)
            i_I = np.sqrt(I_I/A_I)

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("A (cm²)", f"{A_I:.2f}")
            col2.metric("Iy (cm⁴)", f"{I_I:.2f}")
            col3.metric("Wy (cm³)", f"{W_I:.2f}")
            col4.metric("iy (cm)", f"{i_I:.2f}")
            st.latex(rf"I_y = \frac{{B \cdot H^3}}{{12}} - \frac{{(B-t_w) \cdot h_w^3}}{{12}} = {I_I:.2f} \text{{ cm}}^4")

    # TAB 2: ÎNTINDERE/COMPRESIUNE
    with tab2:
        st.subheader("Solicitări Axiale (Lucrarea 6 & 7 din 481-0.pdf)")

        sub_tab = st.radio("Tip calcul", ["Verificare rezistență", "Dimensionare", "Efort capabil", "Alungire bară"])

        if sub_tab == "Verificare rezistență":
            c1, c2 = st.columns(2)
            N_ax = c1.number_input("Efort axial N (kN)", value=200.0)
            A_ax = c1.number_input("Arie secțiune A (cm²)", min_value=0.1, value=10.0)
            R_ax = c2.number_input("Rezistență de calcul R (N/mm²)", value=235.0)
            alpha = c2.number_input("Coef. reducere α (0.85 pt. slăbiri)", min_value=0.1, max_value=1.0, value=0.85)

            N_kNmm2 = N_ax * 10  # kN -> N, cm² -> mm²: kN/cm² -> N/mm² (*10)
            sigma = N_kNmm2 / (A_ax * 100)  # N/mm²
            sigma2 = N_ax * 1000 / (A_ax * 100)  # N/mm²

            st.latex(rf"\sigma = \frac{{N}}{{A}} = \frac{{{N_ax:.2f} \cdot 10^3 \text{{ N}}}}{{{A_ax:.2f} \cdot 10^2 \text{{ mm}}^2}} = {sigma2:.2f} \text{{ N/mm}}^2")

            if sigma2 <= alpha * R_ax:
                st.success(f"✓ VERIFICĂ: σ = {sigma2:.2f} N/mm² ≤ α·R = {alpha*R_ax:.2f} N/mm²")
            else:
                st.error(f"✗ NU VERIFICĂ: σ = {sigma2:.2f} N/mm² > α·R = {alpha*R_ax:.2f} N/mm²")

        elif sub_tab == "Dimensionare":
            c1, c2 = st.columns(2)
            N_dim = c1.number_input("Efort axial N (kN)", value=300.0)
            R_dim = c1.number_input("Rezistență R (N/mm²)", value=235.0)
            alpha_dim = c2.number_input("Coef. α", min_value=0.1, max_value=1.0, value=0.85)

            A_nec = N_dim * 1000 / (alpha_dim * R_dim)
            A_nec_cm2 = A_nec / 100

            st.latex(rf"A_{{nec}} \geq \frac{{N}}{{\alpha \cdot R}} = \frac{{{N_dim:.2f} \cdot 10^3}}{{{alpha_dim:.2f} \cdot {R_dim:.0f}}} = {A_nec:.2f} \text{{ mm}}^2 = {A_nec_cm2:.2f} \text{{ cm}}^2")
            st.info(f"Secțiunea necesară: A_nec ≥ {A_nec_cm2:.2f} cm²")

        elif sub_tab == "Efort capabil":
            c1, c2 = st.columns(2)
            A_cap = c1.number_input("Arie netă A_ef (cm²)", min_value=0.1, value=15.0)
            R_cap = c1.number_input("Rezistență R (N/mm²)", value=235.0)
            N_cap = A_cap * 100 * R_cap / 1000  # kN
            st.latex(rf"N_{{cap}} = A_{{ef}} \cdot R = {A_cap:.2f} \cdot 10^2 \cdot {R_cap:.0f} = {N_cap:.2f} \text{{ kN}}")
            st.success(f"Efort capabil: N_cap = {N_cap:.2f} kN")

        elif sub_tab == "Alungire bară":
            c1, c2 = st.columns(2)
            N_al = c1.number_input("N (kN)", value=100.0)
            L_al = c1.number_input("Lungime L (m)", min_value=0.01, value=3.0)
            A_al = c2.number_input("Arie A (cm²)", min_value=0.1, value=10.0)
            E_al = c2.number_input("Modul E (N/mm²)", value=210000.0)

            delta_l = N_al * 1000 * L_al * 1000 / (E_al * A_al * 100)
            st.latex(rf"\Delta l = \frac{{N \cdot L}}{{E \cdot A}} = \frac{{{N_al:.2f} \cdot 10^3 \cdot {L_al*1000:.0f}}}{{{E_al:.0f} \cdot {A_al*100:.0f}}} = {delta_l:.3f} \text{{ mm}}")
            st.success(f"Alungire: Δl = {delta_l:.3f} mm")

    # TAB 3: ÎNCOVOIERE
    with tab3:
        st.subheader("Calculul de Rezistență al Grinzilor Încovoiate (Lucrarea 10-11)")

        c1, c2 = st.columns(2)
        M_inc = c1.number_input("Moment maxim |Mmax| (kNm)", min_value=0.0, value=50.0)
        T_inc = c1.number_input("Forță tăietoare max |Tmax| (kN)", min_value=0.0, value=30.0)
        R_inc = c2.number_input("Rezistență normală R (N/mm²)", value=235.0)
        Rf_inc = c2.number_input("Rezistență la forfecare Rf (N/mm²)", value=140.0)

        tip_calc_inc = st.radio("Calcul", ["Verificare", "Dimensionare (profil IPE/HEA)"])

        if tip_calc_inc == "Verificare":
            Wy_v = st.number_input("Modul rezistență Wy (cm³)", min_value=0.1, value=500.0)
            Iz_v = st.number_input("Moment inerție Iy (cm⁴)", min_value=0.1, value=5000.0)
            Sy_v = st.number_input("Moment static Sy (cm³) - la nivelul axei neutre", min_value=0.1, value=300.0)
            tw_v = st.number_input("Grosime inimă tw (cm)", min_value=0.1, value=1.0)

            sigma_max = M_inc * 1e6 / (Wy_v * 1e3)  # N/mm²
            tau_max = T_inc * 1e3 * Sy_v * 1e3 / (Iz_v * 1e4 * tw_v * 10)  # N/mm²

            st.latex(rf"\sigma_{{max}} = \frac{{|M_{{max}}|}}{{W_y}} = \frac{{{M_inc:.2f} \cdot 10^6}}{{{Wy_v:.2f} \cdot 10^3}} = {sigma_max:.2f} \text{{ N/mm}}^2")
            st.latex(rf"\tau_{{max}} = \frac{{|T_{{max}}| \cdot S_y}}{{I_y \cdot t_w}} = {tau_max:.2f} \text{{ N/mm}}^2")

            col_r1, col_r2 = st.columns(2)
            if sigma_max <= R_inc:
                col_r1.success(f"σmax = {sigma_max:.2f} ≤ R = {R_inc:.0f} N/mm² ✓")
            else:
                col_r1.error(f"σmax = {sigma_max:.2f} > R = {R_inc:.0f} N/mm² ✗")

            if tau_max <= Rf_inc:
                col_r2.success(f"τmax = {tau_max:.2f} ≤ Rf = {Rf_inc:.0f} N/mm² ✓")
            else:
                col_r2.error(f"τmax = {tau_max:.2f} > Rf = {Rf_inc:.0f} N/mm² ✗")

        else:
            st.markdown("**Dimensionare profil IPE din oțel:**")
            Wy_nec = M_inc * 1e6 / R_inc / 1e3  # cm³
            st.latex(rf"W_{{y,nec}} \geq \frac{{|M_{{max}}|}}{{R}} = \frac{{{M_inc:.2f} \cdot 10^6}}{{{R_inc:.0f}}} = {Wy_nec:.2f} \text{{ cm}}^3")

            # Profile IPE standard
            ipe_profiles = {
                "IPE 160": {"Wy": 123, "Iy": 869, "A": 20.1, "h": 16, "tw": 0.5},
                "IPE 200": {"Wy": 194, "Iy": 1943, "A": 28.5, "h": 20, "tw": 0.56},
                "IPE 240": {"Wy": 307, "Iy": 3892, "A": 39.1, "h": 24, "tw": 0.62},
                "IPE 270": {"Wy": 395, "Iy": 5790, "A": 45.9, "h": 27, "tw": 0.66},
                "IPE 300": {"Wy": 557, "Iy": 8356, "A": 53.8, "h": 30, "tw": 0.71},
                "IPE 330": {"Wy": 713, "Iy": 11770, "A": 62.6, "h": 33, "tw": 0.75},
                "IPE 360": {"Wy": 904, "Iy": 16270, "A": 72.7, "h": 36, "tw": 0.8},
                "IPE 400": {"Wy": 1156, "Iy": 23130, "A": 84.5, "h": 40, "tw": 0.86},
                "IPE 450": {"Wy": 1500, "Iy": 33740, "A": 98.8, "h": 45, "tw": 0.94},
                "IPE 500": {"Wy": 1928, "Iy": 48200, "A": 116, "h": 50, "tw": 1.02},
                "IPE 550": {"Wy": 2441, "Iy": 67120, "A": 134, "h": 55, "tw": 1.11},
                "IPE 600": {"Wy": 3069, "Iy": 92080, "A": 156, "h": 60, "tw": 1.2},
            }
            ales = None
            for name, props in ipe_profiles.items():
                if props["Wy"] >= Wy_nec:
                    ales = (name, props)
                    break

            if ales:
                st.success(f"Se alege: **{ales[0]}** cu Wy = {ales[1]['Wy']} cm³ ≥ {Wy_nec:.2f} cm³")
                col1, col2, col3 = st.columns(3)
                col1.metric(f"{ales[0]} - Wy (cm³)", ales[1]['Wy'])
                col2.metric("Iy (cm⁴)", ales[1]['Iy'])
                col3.metric("A (cm²)", ales[1]['A'])
            else:
                st.warning(f"Wy necesar = {Wy_nec:.2f} cm³ - Alegeți profil personalizat!")

    # TAB 4: FORFECARE / TORSIUNE
    with tab4:
        st.subheader("Forfecare și Torsiune")

        sub_t = st.radio("Tip solicitare", ["Forfecare pură", "Torsiune bară circulară"])

        if sub_t == "Forfecare pură":
            c1, c2 = st.columns(2)
            T_ff = c1.number_input("Forță tăietoare T (kN)", value=100.0)
            b_ff = c1.number_input("Lățime în secțiunea de verificare (cm)", min_value=0.1, value=1.0)
            S_ff = c2.number_input("Moment static S (cm³)", min_value=0.1, value=200.0)
            I_ff = c2.number_input("Moment inerție I (cm⁴)", min_value=0.1, value=5000.0)
            Rf_ff = c2.number_input("Rezistență la forfecare Rf (N/mm²)", value=140.0)

            tau = T_ff * 1e3 * S_ff * 1e3 / (I_ff * 1e4 * b_ff * 10)
            st.latex(rf"\tau = \frac{{T \cdot S}}{{I \cdot b}} = \frac{{{T_ff:.2f} \cdot 10^3 \cdot {S_ff:.2f} \cdot 10^3}}{{{I_ff:.2f} \cdot 10^4 \cdot {b_ff:.2f} \cdot 10}} = {tau:.2f} \text{{ N/mm}}^2")

            if tau <= Rf_ff:
                st.success(f"τ = {tau:.2f} N/mm² ≤ Rf = {Rf_ff:.0f} N/mm² ✓")
            else:
                st.error(f"τ = {tau:.2f} N/mm² > Rf = {Rf_ff:.0f} N/mm² ✗")

            # Formulă parabolica distribuție τ pe secțiune dreptunghiulară
            st.latex(r"\tau_{max} = \frac{3T}{2A} \quad \text{(secțiune dreptunghiulară)}")

        else:
            st.markdown("**Torsiune bară circulară plină:**")
            c1, c2 = st.columns(2)
            Mt = c1.number_input("Moment de torsiune Mt (kNm)", min_value=0.0, value=5.0)
            d_t = c1.number_input("Diametru d (mm)", min_value=1.0, value=80.0)
            Rtor = c2.number_input("Rezistență la torsiune Rtor (N/mm²)", value=140.0)
            G_mod = c2.number_input("Modul de forfecare G (N/mm²)", value=81000.0)
            L_t = c2.number_input("Lungime bară L (m)", min_value=0.1, value=2.0)

            Ip = np.pi * d_t**4 / 32  # mm⁴
            Wt = np.pi * d_t**3 / 16  # mm³
            tau_t = Mt * 1e6 / Wt
            phi_rad = Mt * 1e6 * L_t * 1e3 / (G_mod * Ip)
            phi_deg = np.degrees(phi_rad)

            st.latex(rf"I_p = \frac{{\pi d^4}}{{32}} = \frac{{\pi \cdot {d_t:.0f}^4}}{{32}} = {Ip:.0f} \text{{ mm}}^4")
            st.latex(rf"W_t = \frac{{\pi d^3}}{{16}} = {Wt:.0f} \text{{ mm}}^3")
            st.latex(rf"\tau_{{max}} = \frac{{M_t}}{{W_t}} = \frac{{{Mt*1e6:.0f}}}{{{Wt:.0f}}} = {tau_t:.2f} \text{{ N/mm}}^2")
            st.latex(rf"\phi = \frac{{M_t \cdot L}}{{G \cdot I_p}} = \frac{{{Mt*1e6:.0f} \cdot {L_t*1e3:.0f}}}{{{G_mod:.0f} \cdot {Ip:.0f}}} = {phi_rad:.4f} \text{{ rad}} = {phi_deg:.3f}°")

            col1, col2 = st.columns(2)
            if tau_t <= Rtor:
                col1.success(f"τmax = {tau_t:.2f} ≤ Rtor = {Rtor:.0f} N/mm² ✓")
            else:
                col1.error(f"τmax = {tau_t:.2f} > Rtor = {Rtor:.0f} N/mm² ✗")
            col2.metric("Unghi torsiune φ (°)", f"{phi_deg:.3f}")

    # TAB 5: FLAMBAJ
    with tab5:
        st.subheader("Flambaj (Instabilitate la Compresiune)")
        st.markdown("Calcul conform Euler - bare comprimate zvelte")

        with st.expander("Teorie Flambaj", expanded=False):
            st.latex(r"N_{cr} = \frac{\pi^2 \cdot E \cdot I}{\left(\mu \cdot L\right)^2}")
            st.markdown("""
**Lungimea de flambaj** `μL`:
- Ambele capete articulate: μ = 1.0
- Un capăt încastrat, celălalt liber: μ = 2.0
- Ambele capete încastrate: μ = 0.5
- Un capăt încastrat, celălalt articulat: μ = 0.7

**Zveltețea:** λ = μL / i_min  (i = raza de girație minimă)
**Forță critică Euler** (valabilă pentru λ > λ_limit)
            """)

        c1, c2 = st.columns(2)
        N_fl = c1.number_input("Forță de compresiune N (kN)", min_value=0.0, value=500.0)
        L_fl = c1.number_input("Lungime bară L (m)", min_value=0.1, value=4.0)
        mu_fl = c1.selectbox("Condiții rezemare (μ)", [1.0, 0.7, 0.5, 2.0],
                              format_func=lambda x: {1.0: "μ=1.0 (art-art)", 0.7: "μ=0.7 (înc-art)", 0.5: "μ=0.5 (înc-înc)", 2.0: "μ=2.0 (înc-liber)"}[x])
        E_fl = c2.number_input("E (N/mm²)", value=210000.0)
        I_fl = c2.number_input("Moment inerție minim Imin (cm⁴)", min_value=0.1, value=1000.0)
        A_fl = c2.number_input("Arie A (cm²)", min_value=0.1, value=50.0)

        L_fl_mm = L_fl * 1000
        I_fl_mm4 = I_fl * 1e4
        A_fl_mm2 = A_fl * 1e2

        N_cr = np.pi**2 * E_fl * I_fl_mm4 / (mu_fl * L_fl_mm)**2 / 1000  # kN
        i_min = np.sqrt(I_fl_mm4 / A_fl_mm2)  # mm
        lam = mu_fl * L_fl_mm / i_min
        rezerva = N_cr / N_fl if N_fl > 0 else float('inf')

        st.latex(rf"N_{{cr}} = \frac{{\pi^2 E I}}{{(\mu L)^2}} = \frac{{\pi^2 \cdot {E_fl:.0f} \cdot {I_fl_mm4:.0f}}}{{({mu_fl:.1f} \cdot {L_fl_mm:.0f})^2}} = {N_cr:.2f} \text{{ kN}}")
        st.latex(rf"\lambda = \frac{{\mu L}}{{i}} = \frac{{{mu_fl:.1f} \cdot {L_fl_mm:.0f}}}{{{i_min:.2f}}} = {lam:.2f}")

        col1, col2, col3 = st.columns(3)
        col1.metric("N_cr (kN)", f"{N_cr:.2f}")
        col2.metric("Zveltețe λ", f"{lam:.1f}")
        col3.metric("Rezervă N_cr/N", f"{rezerva:.2f}")

        if N_fl < N_cr:
            st.success(f"N = {N_fl:.2f} kN < N_cr = {N_cr:.2f} kN → Bara NU flambează ✓")
        else:
            st.error(f"N = {N_fl:.2f} kN ≥ N_cr = {N_cr:.2f} kN → RISC DE FLAMBAJ ✗")

        # Curba Euler
        fig_fl, ax_fl = plt.subplots(figsize=(8, 5), dpi=120)
        lam_arr = np.linspace(20, 300, 500)
        sigma_cr = np.pi**2 * E_fl / lam_arr**2
        ax_fl.plot(lam_arr, sigma_cr, 'b-', lw=2.5, label='Curba Euler: σcr = π²E/λ²')
        ax_fl.axvline(lam, color='red', lw=2, linestyle='--', label=f'λ = {lam:.1f}')
        sigma_N = N_fl * 1000 / A_fl_mm2
        ax_fl.axhline(sigma_N, color='orange', lw=1.5, linestyle=':', label=f'σ = {sigma_N:.1f} N/mm²')
        ax_fl.set_xlabel("Zveltețe λ"); ax_fl.set_ylabel("σcr (N/mm²)")
        ax_fl.set_title("Curba Euler de Flambaj", weight='bold')
        ax_fl.legend(); ax_fl.grid(True, alpha=0.3)
        ax_fl.set_ylim(0, min(600, 2*sigma_N + 100) if sigma_N > 0 else 600)
        st.pyplot(fig_fl)

# ==========================================
# MODUL 7: METODA FORȚELOR (SSN)
# ==========================================
elif modul == "7. Metoda Forțelor (SSN)":
    st.header("Metoda Generală a Forțelor – Structuri Static Nedeterminate")
    st.markdown("Conform 138-3.pdf: Metoda Forțelor și Metoda Deplasărilor")

    with st.expander("Teorie: Metoda Forțelor (138-3.pdf, Cap. 1)", expanded=False):
        st.markdown("""
**Metoda Generală a Forțelor** rezolvă structurile static nedeterminate (SSN) impunând condiția de continuitate a deformatei.

**Etape:**
1. Se determină gradul de nedeterminare statică: `n = r - 3 - a`
2. Se suprimă `n` legături → **Sistemul de Bază (S.B.)** (static determinat)
3. Se introduc necunoscutele-forțe `X₁, X₂, ..., Xₙ` pe direcțiile legăturilor suprimate
4. Se trasează diagramele de eforturi:
   - `Mf` – din încărcările exterioare pe S.B.
   - `m₁, m₂,...` – din Xᵢ = 1 pe S.B.
5. Se calculează coeficienții (integrarea Veresceaghin):
   - `δᵢⱼ = ∫(mᵢ·mⱼ/EI)dx`
   - `Δᵢf = ∫(Mf·mᵢ/EI)dx`
6. Se rezolvă sistemul de ecuații: `[δ]·{X} = -{Δf}`
7. Diagramele finale: `M = Mf + Σ(Xᵢ·mᵢ)`
        """)
        st.latex(r"\delta_{ij} X_j + \Delta_{if} = 0 \quad (i = 1, 2, ..., n)")
        st.latex(r"M_{final} = M_f + \sum_{i=1}^{n} X_i \cdot m_i")
        st.markdown("**Regula Veresceaghin** pentru integrare diagrame:")
        st.latex(r"\int \frac{m_i \cdot m_j}{EI} dx = \frac{1}{EI} \cdot \Omega_i \cdot \bar{m}_j")
        st.markdown("unde Ωᵢ = aria diagramei mᵢ, m̄ⱼ = ordonata diagramei mⱼ sub centrul de greutate al Ωᵢ")

    st.subheader("Aplicație: Grindă o dată static nedeterminată (1 grad)")
    st.markdown("**Exemplu:** Grindă cu încastrare la A și reazem simplu la B (o dată SSN)")

    col1, col2 = st.columns(2)
    with col1:
        L_ssn = col1.number_input("Lungime L (m)", min_value=1.0, value=6.0, step=0.5)
        q_ssn = col1.number_input("Încărcare distribuită q (kN/m)", min_value=0.0, value=20.0)
    with col2:
        P_ssn = col2.number_input("Forță concentrată P (kN)", min_value=0.0, value=0.0, step=5.0)
        a_ssn = col2.number_input("Poziție P față de A (m)", min_value=0.0, max_value=float(L_ssn), value=float(L_ssn)/2)
        EI_ssn = col2.number_input("EI (kNm²) - rigiditate", min_value=1.0, value=10000.0)

    if st.button("Rezolvă prin Metoda Forțelor", type="primary"):
        # Sistem de baza: grindă simplu rezemată (A articulat, B articulat)
        # Necunoscuta X1 = momentul de încastrare în A
        # Sistemul de baza = grindă simplu rezemată AB

        # Diagrama Mf (pe S.B. = grindă simplu rezemată):
        # VB_sb = (q*L^2/2 + P*a) / L
        Q = q_ssn * L_ssn
        VB_sb = (Q * L_ssn/2 + P_ssn * a_ssn) / L_ssn
        VA_sb = Q + P_ssn - VB_sb

        # Diagrama m1 (X1=1 = moment unitar aplicat la A pe S.B.):
        # Grindă simplu rez. cu moment unitar la A → reacțiuni: VB1=1/L (sus), VA1=-1/L
        # m1 = 1 la A, 0 la B → variatie liniara: m1(x) = 1 - x/L

        # Coeficienți (Veresceaghin) - neglijând N, T:
        # δ11 = ∫ m1² /EI dx = (1/EI) * (1/3)*1*L = L/(3*EI)  (triunghi m1=1 la A)
        delta11 = L_ssn / (3 * EI_ssn)  # fara EI (se lucreaza cu EI=1 și se imparte la EI)

        # Δ1f = ∫ Mf * m1 / EI dx
        # Mf pe S.B.: parabolă sub q + triunghi sub P
        # ∫ Mf*m1 dx = ∫₀ᴸ [VA_sb*x - q*x²/2 - P*(x-a)*H(x-a)] * (1-x/L) dx

        # Calculăm numeric
        x_int = np.linspace(0, L_ssn, 1000)
        dx = x_int[1] - x_int[0]

        Mf_arr = VA_sb * x_int - q_ssn * x_int**2 / 2
        if P_ssn > 0:
            for ii, xx in enumerate(x_int):
                if xx > a_ssn:
                    Mf_arr[ii] -= P_ssn * (xx - a_ssn)

        m1_arr = 1.0 - x_int / L_ssn  # m1 liniar de la 1 la 0

        delta11_num = np.trapz(m1_arr**2, x_int) / EI_ssn
        Delta1f_num = np.trapz(Mf_arr * m1_arr, x_int) / EI_ssn

        X1 = -Delta1f_num / delta11_num  # moment de încastrare la A [kNm]

        # Diagrame finale
        M_final = Mf_arr + X1 * m1_arr

        # Reacțiuni finale
        # X1 = moment la A (încastrare)
        VB_fin = (Q * L_ssn/2 + P_ssn * a_ssn - X1) / L_ssn
        VA_fin = Q + P_ssn - VB_fin

        st.success(f"**Necunoscuta X₁ (moment în A) = {X1:.3f} kNm**")
        st.latex(rf"X_1 = -\frac{{\Delta_{{1f}}}}{{\delta_{{11}}}} = -\frac{{{Delta1f_num*EI_ssn:.3f}/EI}}{{{delta11_num*EI_ssn:.3f}/EI}} = {X1:.3f} \text{{ kNm}}")

        col_r1, col_r2, col_r3 = st.columns(3)
        col_r1.metric("X₁ = MA (kNm)", f"{X1:.3f}")
        col_r2.metric("VA (kN)", f"{VA_fin:.3f}")
        col_r3.metric("VB (kN)", f"{VB_fin:.3f}")

        # Forță tăietoare finală
        T_final = np.zeros_like(x_int)
        for ii, xx in enumerate(x_int):
            t = VA_fin - q_ssn * xx
            if xx > a_ssn and P_ssn > 0:
                t -= P_ssn
            T_final[ii] = t

        # Plot
        fig_ssn, axes_ssn = plt.subplots(3, 1, figsize=(12, 10), dpi=150, sharex=True)

        # Diagrama m1
        axes_ssn[0].fill_between(x_int, m1_arr, alpha=0.2, color='green')
        axes_ssn[0].plot(x_int, m1_arr, 'g-', lw=2.5)
        axes_ssn[0].axhline(0, color='k', lw=1)
        axes_ssn[0].set_title("Diagrama m₁ (S.B. cu X₁=1)", weight='bold', color='green')
        axes_ssn[0].set_ylabel("m₁ (m/kNm)")
        axes_ssn[0].grid(True, alpha=0.3)

        # Diagrama Mf
        axes_ssn[1].fill_between(x_int, Mf_arr, alpha=0.2, color='orange')
        axes_ssn[1].plot(x_int, Mf_arr, color='orange', lw=2.5)
        axes_ssn[1].axhline(0, color='k', lw=1)
        axes_ssn[1].set_title(f"Diagrama Mf (S.B. cu încărcări exterioare)", weight='bold', color='orange')
        axes_ssn[1].set_ylabel("Mf (kNm)")
        axes_ssn[1].grid(True, alpha=0.3)

        # Diagrama M final
        axes_ssn[2].fill_between(x_int, M_final, alpha=0.2, color='#1D3557')
        axes_ssn[2].plot(x_int, M_final, color='#1D3557', lw=2.5)
        axes_ssn[2].axhline(0, color='k', lw=1)
        axes_ssn[2].invert_yaxis()
        axes_ssn[2].set_title(f"Diagrama M final = Mf + X₁·m₁ | Mmax={np.max(np.abs(M_final)):.3f} kNm", weight='bold', color='#1D3557')
        axes_ssn[2].set_ylabel("M (kNm)")
        axes_ssn[2].set_xlabel("x (m)")
        axes_ssn[2].grid(True, alpha=0.3)

        plt.tight_layout()
        st.pyplot(fig_ssn)

        # Verificare: M în A trebuie = X1
        st.info(f"Verificare: M(x=0) = {M_final[0]:.3f} kNm ≈ X₁ = {X1:.3f} kNm | M(x=L) = {M_final[-1]:.4f} kNm ≈ 0")

        # Pasul 7: prezentare formule
        with st.expander("Formule analitice (grindă încastrată-rezemată, q uniform)"):
            st.markdown("**Soluție analitică pentru grindă încastrată la A, reazem simplu la B, cu q uniform pe toată lungimea:**")
            X1_analitic = q_ssn * L_ssn**2 / 8
            st.latex(rf"M_A = X_1 = \frac{{q \cdot L^2}}{{8}} = \frac{{{q_ssn} \cdot {L_ssn}^2}}{{8}} = {X1_analitic:.3f} \text{{ kNm}}")
            VB_an = 3*q_ssn*L_ssn/8
            VA_an = q_ssn*L_ssn - VB_an
            st.latex(rf"V_B = \frac{{3qL}}{{8}} = {VB_an:.3f} \text{{ kN}} \quad ; \quad V_A = \frac{{5qL}}{{8}} = {VA_an:.3f} \text{{ kN}}")
            st.latex(rf"M_{{max}} = \frac{{9 q L^2}}{{128}} = {9*q_ssn*L_ssn**2/128:.3f} \text{{ kNm}}")

    st.markdown("---")
    st.subheader("Metoda Deplasărilor – Noțiuni de bază (138-3.pdf, Partea II)")

    with st.expander("Teorie: Metoda Deplasărilor", expanded=False):
        st.markdown("""
**Metoda Deplasărilor (Metoda Rigidității)** tratează structura ca un sistem în care necunoscutele sunt deplasările (rotirile, translațiile) nodurilor.

**Etape:**
1. Se identifică **nodurile active** și gradele de libertate (GDL)
2. Se formează **matricea de rigiditate** `[K]`
3. Se aplică condițiile de încărcare și rezemare → vectorul forțelor `{F}`
4. Se rezolvă: `[K]·{U} = {F}` → deplasările `{U}`
5. Se calculează eforturile din deplasări

**Rigiditatea unui element de bară (modulii de rigiditate):**
- `k = EI/L` (rigiditate la rotire)
- Momentele capătului apropiat: `4EI/L · φ + 2EI/L · φ_far + ...`
- Momentele capătului depărtat: `2EI/L · φ + 4EI/L · φ_far + ...`

**Momentele de încastrare (MI)** din încărcări pe S.B. (bare încastrate la capete):
        """)
        st.latex(r"MI_A = \frac{q L^2}{12} \quad ; \quad MI_B = -\frac{q L^2}{12} \quad \text{(q uniform)}")
        st.latex(r"MI_A = \frac{P a b^2}{L^2} \quad ; \quad MI_B = -\frac{P a^2 b}{L^2} \quad \text{(forță concentrată P)}")
        st.markdown("**Condiție de echilibru nod:** Suma momentelor din bare concurente în nod = 0")

    st.subheader("Calculator Metoda Deplasărilor – Grindă continuă 2 deschideri")
    st.markdown("Grindă AB+BC: A încastrat, B nod intermediar (rotire liberă), C reazem simplu")

    col1, col2 = st.columns(2)
    with col1:
        L1_md = st.number_input("Deschidere AB: L₁ (m)", min_value=1.0, value=5.0, step=0.5)
        q1_md = st.number_input("q pe AB (kN/m)", min_value=0.0, value=20.0)
        EI1_md = st.number_input("EI pentru AB (kNm²)", min_value=1.0, value=10000.0)
    with col2:
        L2_md = st.number_input("Deschidere BC: L₂ (m)", min_value=1.0, value=6.0, step=0.5)
        q2_md = st.number_input("q pe BC (kN/m)", min_value=0.0, value=15.0)
        EI2_md = st.number_input("EI pentru BC (kNm²)", min_value=1.0, value=10000.0)

    if st.button("Rezolvă Metoda Deplasărilor", type="primary"):
        # Nodul B este singurul cu GDL de rotire (A încastrat → rB=0 fizic la A, C articulat)
        # Necunoscuta: φB (rotirea nodului B)
        # k1 = EI1/L1, k2 = EI2/L2

        k1 = EI1_md / L1_md
        k2 = EI2_md / L2_md

        # Momentele de încastrare pe fiecare bară (cu capetele blocate):
        MI_BA_inf = -q1_md * L1_md**2 / 12   # capatul B din bara AB (momentul de incastrare)
        MI_BA_sup =  q1_md * L1_md**2 / 12   # (opus - capatul A)
        MI_BC_inf = -q2_md * L2_md**2 / 12   # capatul B din bara BC
        MI_BC_sup =  q2_md * L2_md**2 / 12   # capatul C

        # Suma momentelor în B = 0 (condiție echilibru):
        # M_BA + M_BC = 0
        # M_BA = 4k1*φB + MI_BA_inf  (bara AB, capatul B)
        # M_BC = 4k2*φB + MI_BC_inf  (bara BC, capatul B, cu C articulat → 3EI/L pentru grinda cu cap liber)
        # Dacă C este articulat (reazem simplu): M_BC = 3k2*φB + MI_BC_articulat
        # MI_BC_articulat = -q2*L2^2/8 (pentru grinda cu un cap articulat)

        # Corect pentru C articulat:
        MI_BC_B_art = -q2_md * L2_md**2 / 8  # momentul încastrare la B pentru grindă BC (C articulat)
        K_BC_art = 3 * k2  # rigiditate efectivă (capăt articulat)

        # Condiție nod B:
        # (4k1 + K_BC_art) * φB + MI_BA_inf + MI_BC_B_art = 0
        K_nod = 4 * k1 + K_BC_art
        incarcari_nod = -(MI_BA_inf + MI_BC_B_art)

        phi_B = incarcari_nod / K_nod

        # Momente finale la capetele barelor:
        M_BA = 4*k1*phi_B + MI_BA_inf  # moment la B pe bara AB
        M_AB = 2*k1*phi_B + MI_BA_sup  # moment la A (încastrare)
        M_BC = K_BC_art * phi_B + MI_BC_B_art  # moment la B pe bara BC
        M_CB = 0.0  # C articulat → M=0

        st.success(f"φB = {phi_B:.6f} rad | M_AB = {M_AB:.3f} kNm | M_BA = {M_BA:.3f} kNm | M_BC = {M_BC:.3f} kNm")

        st.latex(rf"\varphi_B = \frac{{-(MI_{{BA}} + MI_{{BC}})}}{{4k_1 + 3k_2}} = \frac{{{incarcari_nod:.3f}}}{{{K_nod:.3f}}} = {phi_B:.5f} \text{{ rad}}")
        st.latex(rf"M_{{AB}} = 2k_1 \varphi_B + MI_{{AB}} = 2 \cdot {k1:.2f} \cdot {phi_B:.5f} + {MI_BA_sup:.3f} = {M_AB:.3f} \text{{ kNm}}")
        st.latex(rf"M_{{BA}} = 4k_1 \varphi_B + MI_{{BA}} = {M_BA:.3f} \text{{ kNm}}")

        # Verificare: suma momente la B
        verif = M_BA + M_BC
        st.info(f"Verificare echilibru nod B: M_BA + M_BC = {M_BA:.4f} + {M_BC:.4f} = {verif:.6f} ≈ 0 ✓")

        # Diagrame pe bare
        x1 = np.linspace(0, L1_md, 300)
        x2 = np.linspace(0, L2_md, 300)

        # Reacțiuni bara AB
        VA_ab = (q1_md * L1_md / 2 + (M_AB + M_BA) / L1_md)
        VB_ab = q1_md * L1_md - VA_ab

        # Reacțiuni bara BC
        VB_bc = (q2_md * L2_md / 2 + M_BC / L2_md)
        VC_bc = q2_md * L2_md - VB_bc

        M1 = M_AB + VA_ab * x1 - q1_md * x1**2 / 2
        # Corectie: M la A este M_AB si la B este M_BA
        # Verificam capetele
        M2 = M_BC + VB_bc * x2 - q2_md * x2**2 / 2

        x_tot = np.concatenate([x1, x2 + L1_md])
        M_tot = np.concatenate([M1, M2])

        fig_md, ax_md = plt.subplots(figsize=(12, 5), dpi=150)
        ax_md.fill_between(x_tot, M_tot, alpha=0.2, color='#1D3557')
        ax_md.plot(x_tot, M_tot, color='#1D3557', lw=2.5)
        ax_md.axhline(0, color='k', lw=1.5)
        ax_md.axvline(L1_md, color='red', lw=1.5, linestyle='--', label=f'Nod B (x={L1_md}m)')
        ax_md.plot(0, M_AB, 'ko', ms=8, label=f'M_A={M_AB:.2f}kNm')
        ax_md.plot(L1_md, M_BA, 'rs', ms=8, label=f'M_B={M_BA:.2f}kNm')
        ax_md.invert_yaxis()
        ax_md.set_title("Diagramă M finală (Metoda Deplasărilor - Grindă Continuă 2 Deschideri)", weight='bold')
        ax_md.set_xlabel("x (m)"); ax_md.set_ylabel("M (kNm)")
        ax_md.legend(); ax_md.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig_md)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("M_A (kNm)", f"{M_AB:.3f}")
        col2.metric("M_B (kNm)", f"{M_BA:.3f}")
        col3.metric("M max span 1", f"{np.max(M1):.3f}")
        col4.metric("M max span 2", f"{np.max(M2):.3f}")

# ==========================================
# MODUL 8: ASISTENT TEORETIC
# ==========================================
elif modul == "8. Asistent Teoretic":
    st.header("Asistent Teoretic: Algoritmi și Formule")

    with st.expander("1. Clasificare Noduri și Grinzi", expanded=True):
        st.markdown("""
**Nod Rigid:** 3 grade de libertate (2 translații, 1 rotire). Transmite moment încovoietor.

**Nod Articulat:** 2 grade de libertate (2 translații). NU transmite moment încovoietor.

**Grindă Principală (G.P.):** Static determinată și fixată față de teren.

**Grindă Secundară (G.S.):** Are cel mult o legătură cu terenul; descarcă pe G.P.
        """)

    with st.expander("2. Formule Standard Grinzi (975-4.pdf)"):
        st.markdown("### Grindă simplu rezemată - cazuri standard")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**q uniform pe toată lungimea:**")
            st.latex(r"V_A = V_B = \frac{qL}{2}")
            st.latex(r"M_{max} = \frac{qL^2}{8} \quad \text{la } x = L/2")
            st.latex(r"T(x) = \frac{qL}{2} - qx")

            st.markdown("**Forță concentrată P la mijloc:**")
            st.latex(r"V_A = V_B = \frac{P}{2}")
            st.latex(r"M_{max} = \frac{PL}{4} \quad \text{la } x = L/2")
        with col2:
            st.markdown("**Forță concentrată P la distanța a:**")
            st.latex(r"V_A = \frac{P(L-a)}{L} \quad ; \quad V_B = \frac{Pa}{L}")
            st.latex(r"M_{max} = \frac{Pa(L-a)}{L} \quad \text{la } x = a")

            st.markdown("**Consolă (încastrare la A, liberă la B), q uniform:**")
            st.latex(r"V_A = qL \quad ; \quad M_A = \frac{qL^2}{2}")
            st.latex(r"M(x) = \frac{q(L-x)^2}{2} \quad \text{(de la capătul liber)}")

    with st.expander("3. Formule Arc Parabolice (975-4.pdf, Cap. 4)"):
        st.latex(r"y(x) = \frac{4f}{L^2} x(L-x)")
        st.latex(r"H = \frac{qL^2}{8f} \quad \text{(arc funicular, q pe proj. orizontală → M=0)}")
        st.latex(r"M(x) = M_0(x) - H \cdot y(x)")
        st.latex(r"N \approx -\frac{H}{\cos\theta} \quad ; \quad \tan\theta = y'(x) = \frac{4f}{L^2}(L-2x)")

    with st.expander("4. Rezistența Materialelor - Formule Esențiale (481-0.pdf)"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Secțiune dreptunghiulară:**")
            st.latex(r"I_y = \frac{bh^3}{12} \quad ; \quad W_y = \frac{bh^2}{6}")
            st.latex(r"i_y = \frac{h}{\sqrt{12}} = \frac{h}{2\sqrt{3}}")
            st.markdown("**Secțiune circulară:**")
            st.latex(r"I = \frac{\pi d^4}{64} \quad ; \quad W = \frac{\pi d^3}{32}")
            st.markdown("**Formula lui Navier (tensiune normală la încovoiere):**")
            st.latex(r"\sigma = \frac{M}{I} \cdot z \quad ; \quad \sigma_{max} = \frac{M}{W}")
            st.markdown("**Tensiune tangențială la forfecare (Jouravski):**")
            st.latex(r"\tau = \frac{T \cdot S}{I \cdot b}")
        with col2:
            st.markdown("**Solicitare axială:**")
            st.latex(r"\sigma = \frac{N}{A} \leq R \quad ; \quad \Delta l = \frac{NL}{EA}")
            st.markdown("**Flambaj Euler:**")
            st.latex(r"N_{cr} = \frac{\pi^2 EI}{(\mu L)^2} \quad ; \quad \lambda = \frac{\mu L}{i}")
            st.markdown("**Torsiune bară circulară:**")
            st.latex(r"I_p = \frac{\pi d^4}{32} \quad ; \quad \tau_{max} = \frac{M_t}{W_t} = \frac{2M_t}{\pi r^3}")
            st.markdown("**Teorema lui Steiner:**")
            st.latex(r"I = I_0 + A \cdot d^2")

    with st.expander("5. Metoda Forțelor - Regula Veresceaghin (138-3.pdf)"):
        st.markdown("**Integrare diagrame (Veresceaghin):**")
        st.latex(r"\delta_{ij} = \int_0^L \frac{m_i \cdot m_j}{EI} dx = \frac{1}{EI} \cdot \Omega_i \cdot \bar{m}_j")

        st.markdown("**Produse standard diagrame:**")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("- Triunghi × Triunghi (același sens):")
            st.latex(r"\frac{1}{EI} \cdot \frac{1}{3} \cdot h_1 \cdot L \cdot h_2")
            st.markdown("- Triunghi × Triunghi (sens opus):")
            st.latex(r"\frac{1}{EI} \cdot \frac{1}{6} \cdot h_1 \cdot L \cdot h_2")
        with col2:
            st.markdown("- Parabolă × Dreptunghi:")
            st.latex(r"\frac{1}{EI} \cdot \frac{2}{3} \cdot h \cdot L \cdot c")
            st.markdown("- Parabolă × Triunghi:")
            st.latex(r"\frac{1}{EI} \cdot \frac{1}{3} \cdot h \cdot L \cdot c \quad \text{(sub centru parabolă)}")

    with st.expander("6. Metoda Deplasărilor - Rigidități și MI (138-3.pdf)"):
        st.markdown("**Ecuații moment la capetele barei (bare prismatice):**")
        st.latex(r"M_{ij} = \frac{4EI}{L}\varphi_i + \frac{2EI}{L}\varphi_j + MI_{ij}")
        st.latex(r"M_{ji} = \frac{2EI}{L}\varphi_i + \frac{4EI}{L}\varphi_j + MI_{ji}")
        st.markdown("**Dacă celălalt capăt este articulat:**")
        st.latex(r"M_{ij} = \frac{3EI}{L}\varphi_i + MI_{ij}^{art}")

        st.markdown("**Momente de încastrare MI (bare cu capete încastrate):**")
        data_mi = {
            "Tip încărcare": ["q uniform", "Forță P la a de la i", "Moment M₀ la mijloc"],
            "MI_ij (la i)": ["qL²/12", "Pab²/L²", "M₀/2"],
            "MI_ji (la j)": ["-qL²/12", "-Pa²b/L²", "-M₀/2"]
        }
        import pandas as pd
        st.table(pd.DataFrame(data_mi))

    with st.expander("7. Algoritm Grinzi Gerber"):
        st.markdown("""
**PAS 1:** Identificare grinzi secundare (G.S.) și principale (G.P.)
- G.S. = grindă cu cel mult 1 legătură cu terenul; se desprinde din structură
- G.P. = fixată față de teren, primește reacțiunile de la G.S.

**PAS 2:** Calcul reacțiuni pe G.S. (grindă simplu rezemată)
- Suma momente față de articulație → reacțiunea în celălalt reazem
- Suma forțe verticale → reacțiunea în articulație

**PAS 3:** Izolarea G.P.
- Reacțiunea G.S. devine forță pe G.P. (cu sens opus - Principiul acțiunii/reacțiunii)
- Se adaugă la încărcările proprii ale G.P.

**PAS 4:** Calcul reacțiuni G.P. (grindă simplu rezemată cu încărcări compuse)

**PAS 5:** Trasare diagrame eforturi
- Articulația intermediară: **M = 0** (verificare)
- T și N se transmit prin articulație
        """)
