VA_z = 1.0
d_camp = 2.0
h_zab = 3.0
N_talpa_inf = 4.0
N_talpa_sup = 5.0
T_sect = 6.0
sin_d = 7.0
N_diag = 8.0

print(rf"N_{{talpa\,inf}} = \frac{{M_{{sectiune}}}}{{h}} = \frac{{V_A \cdot d}}{{h}} = \frac{{{VA_z:.2f} \times {d_camp:.2f}}}{{{h_zab:.2f}}} = {N_talpa_inf:.3f} \text{{ kN}} \text{{ (întindere)}}")
print(rf"N_{{talpa\,sup}} = -\frac{{M_{{sectiune}}}}{{h}} = {N_talpa_sup:.3f} \text{{ kN}} \text{{ (compresiune)}}")
print(rf"N_{{diagonala}} = \frac{{T}}{{\sin\varphi}} = \frac{{{T_sect:.2f}}}{{{sin_d:.4f}}} = {N_diag:.3f} \text{{ kN}}")
