import re
import sys

with open("app.py", "r", encoding="utf-8") as f:
    text = f.read()

# We need to find the start of the "Calcul Grinzi simplu" logic.
start_str = """if modul == "Calcul Grinzi simplu":
    st.title("Calcul Grinzi simplu")
    st.markdown("---")"""

# And the end of forces logic BEFORE # --- SCHIȚĂ ---
end_forces_str = """        st.session_state.gv_forces=f_edited"""

# We also need to modify btn_calc:
calc_str = """    st.markdown("---")
    if st.button("▶ Efectuează Calculul",type="primary",width="stretch",key="gv_calc"):"""

if start_str not in text:
    print("start_str not found!")
    sys.exit()

if end_forces_str not in text:
    print("end_forces_str not found!")
    sys.exit()

# Extract forces block
pre_start = text.split(start_str)[0]
rest = text.split(start_str)[1]

forces_block = rest.split(end_forces_str)[0] + end_forces_str
rest_after_forces = rest.split(end_forces_str)[1]

# Now, we rewrite the forces_block!
# We just need to replace `st.sidebar.` with `st.` inside it.
# And wrap it in our layout.

new_panel_code = """if modul == "Calcul Grinzi simplu":
    col_panel, col_canvas = st.columns([1.4, 3.6], gap="large")
    
    with col_panel:
        st.markdown("<h3 style='margin-top:-10px;'>🎛️ Panou Control</h3>", unsafe_allow_html=True)
        tab_geom, tab_sup, tab_load = st.tabs(["Geometrie", "Reazeme", "Încărcări"])
        
        with tab_geom:
"""
# Now we process the old lines
old_lines = forces_block.splitlines()

in_reazeme = False
in_load = False

for line in old_lines:
    if line.strip() == "": continue
    if "st.subheader(\"Reazeme\")" in line:
        in_reazeme = True
        new_panel_code += "        with tab_sup:\n"
        # We don't add st.subheader("Reazeme") here, we replace it
        new_panel_code += "            st.markdown(\"#### Setări Reazeme\")\n"
        continue
    
    if "st.subheader(\"Încărcări distribuite q\")" in line:
        in_load = True
        in_reazeme = False
        new_panel_code += "        with tab_load:\n"
        new_panel_code += "            st.markdown(\"#### Distribuite (q)\")\n"
        continue

    # Replacements:
    # remove st.sidebar.
    line = line.replace("st.sidebar.", "st.")
    # change headers
    line = line.replace("st.header(\"1. ", "st.markdown(\"#### 1. ")
    line = line.replace("st.header(\"2. ", "st.markdown(\"#### 2. ")
    line = line.replace("st.header(\"3. ", "st.markdown(\"#### 3. ")
    line = line.replace("\")\n", "\")\n") # dummy 
    
    if "st.subheader(\"Forțe concentrate și momente\")" in line:
        line = "            st.markdown(\"#### Concentrate\")"

    # Fix indentation for the tab (they were at 4 spaces, now 12)
    new_panel_code += "        " + line[4:] + "\n"

# Add button to panel
new_panel_code += """        st.markdown("<br>", unsafe_allow_html=True)
        btn_calc = st.button("▶ Efectuează Calculul", type="primary", use_container_width=True, key="gv_calc")

    canvas_container = col_canvas.container()
    with canvas_container:
        st.markdown("<h3 style='margin-top:-10px;'>✏️ Spațiu de Lucru</h3>", unsafe_allow_html=True)
"""

# Now handle the rest:
# It's basically everything after `end_forces_str` up to `calc_str`, the `st.pyplot(fig1)`, and then `calc_str`.
# We need to prepend 8 spaces to all of `rest_after_forces` to put it inside `with canvas_container:`.

# Wait! If we put everything inside `with canvas_container:`, we can just indent `rest_after_forces`.
new_rest_lines = []
for line in rest_after_forces.splitlines():
    # Fix the calc_str button replacement
    if line.strip() == "st.markdown(\"---\")" and "st.markdown(\"---\")\n    if st.button" in rest_after_forces:
        # this is the start of calc_str probably
        pass
    
    if line.strip() == 'if st.button("▶ Efectuează Calculul",type="primary",width="stretch",key="gv_calc"):':
        new_rest_lines.append("        if btn_calc:")
    else:
        if line == "":
            new_rest_lines.append("")
        else:
            # We want to indent the root level blocks. If it starts with 4 spaces, make it 8!
            if line.startswith("    ") and not line.startswith("        "):
                new_rest_lines.append("    " + line)
            elif line.startswith("        ") and not line.startswith("            "):
                new_rest_lines.append("    " + line) # basically +4 spaces everywhere!
            else:
                new_rest_lines.append("    " + line)

new_text = pre_start + new_panel_code + "\n".join(new_rest_lines)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(new_text)

print("SUCCESS")
