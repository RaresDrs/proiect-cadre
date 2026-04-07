import re

with open("app_clean.py", "r", encoding="utf-16") as f:
    lines = f.readlines()

new_lines = []
in_css = False
in_forces = False

# We will just traverse line by line
i = 0
found_module = False
found_forces_end = False

while i < len(lines):
    line = lines[i]
    
    # Replace CSS
    if "<style>" in line and not found_module:
        new_lines.append("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
header {visibility: hidden;} footer {visibility: hidden;}
.stApp { background-color: #f5f7fa; }
[data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e1e4e8; }
[data-testid="stSidebar"] * { color: #1a202c !important; }
h1 { color: #1a202c; border-bottom: none; font-weight: 700; font-size: 1.8rem; padding-bottom: 0px; }
h2, h3 { color: #2d3748; font-weight: 600; }
h4 { color: #4a5568; font-weight: 600; font-size: 1.1rem; margin-top: 10px; }
.stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div { background-color: #ffffff !important; border: 1px solid #cbd5e0 !important; border-radius: 6px !important; color: #1a202c !important; box-shadow: none !important; }
.stTextInput>div>div>input:focus, .stNumberInput>div>div>input:focus { border-color: #3182ce !important; box-shadow: 0 0 0 1px #3182ce !important; }
button[kind="primary"] { background-color: #3182ce !important; color: white !important; border-radius: 6px !important; border: none !important; font-weight: 600 !important; padding: 0.6rem 1rem !important; transition: background-color 0.2s ease; }
button[kind="primary"]:hover { background-color: #2b6cb0 !important; }
.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] { background-color: transparent !important; border-radius: 6px !important; padding: 8px 16px !important; font-weight: 500 !important; border: 1px solid transparent !important; }
.stTabs [aria-selected="true"] { background-color: #ffffff !important; color: #3182ce !important; border: 1px solid #e2e8f0 !important; box-shadow: 0 -2px 0 0 #3182ce inset !important; }
div[data-testid="stMetric"] { background: #ffffff; border-radius: 8px; padding: 16px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
div[data-testid="stForm"] { border-radius: 8px; border: 1px solid #e2e8f0; background-color: #ffffff; }
""")
        # skip old CSS
        while "</style>" not in lines[i]:
            i += 1
        new_lines.append("</style>\n")
        i += 1
        continue

    if 'if modul == "Calcul Grinzi simplu":' in line:
        found_module = True
        new_lines.append(line)
        new_lines.append("    col_panel, col_canvas = st.columns([1.5, 4], gap=\"large\")\n")
        new_lines.append("    with col_panel:\n")
        new_lines.append("        st.markdown(\"<h3 style='margin-top:-10px;'>Panou Control</h3>\", unsafe_allow_html=True)\n")
        new_lines.append("        tab_geom, tab_sup, tab_load = st.tabs([\"Material\", \"Reazeme\", \"Încărcări\"])\n")
        new_lines.append("        with tab_geom:\n")
        
        # Skip the next 2 lines (st.title and st.markdown("---"))
        i += 3
        
        in_panel = True
        while in_panel and i < len(lines):
            l = lines[i]
            
            # Reached end of panel inputs
            if "st.session_state.gv_forces=f_edited" in l:
                new_lines.append(" " * 8 + l.lstrip())
                new_lines.append("        st.markdown(\"<br>\", unsafe_allow_html=True)\n")
                new_lines.append("        btn_calc = st.button(\"▶ Efectuează Calculul\", type=\"primary\", use_container_width=True, key=\"gv_calc\")\n\n")
                new_lines.append("    canvas_container = col_canvas.container()\n")
                new_lines.append("    with canvas_container:\n")
                new_lines.append("        st.title(\"BeamFlow | Proiectare\")\n")
                in_panel = False
                i += 1
                break

            if "st.subheader(\"Reazeme\")" in l:
                new_lines.append("        with tab_sup:\n")
                new_lines.append("            st.markdown(\"#### Setări Reazeme\")\n")
                i += 1
                continue
            
            if "st.subheader(\"Încărcări distribuite q\")" in l:
                new_lines.append("        with tab_load:\n")
                new_lines.append("            st.markdown(\"#### Distribuite (q)\")\n")
                i += 1
                continue

            l = l.replace("st.sidebar.", "st.")
            l = l.replace("st.header(\"1. ", "st.markdown(\"#### 1. ")
            l = l.replace("st.header(\"2. ", "st.markdown(\"#### 2. ")
            l = l.replace("st.header(\"3. ", "st.markdown(\"#### 3. ")
            if "st.subheader(\"Forțe concentrate și momente\")" in l:
                l = "            st.markdown(\"#### Concentrate\")\n"

            if l.strip() != "":
                # figure out indent
                spaces = len(l) - len(l.lstrip())
                new_lines.append(" " * (spaces + 8) + l.lstrip())
            else:
                new_lines.append("\n")
            
            i += 1
        
        continue # continue the outer while loop

    if found_module and not in_panel:
        # We are after the panel, inside the canvas logic!
        # Need to fix the btn_calc logic
        if 'if st.button("▶ Efectuează Calculul"' in line:
            new_lines.append("        if btn_calc:\n")
            i += 1
            continue
        
        if line.strip() != "":
            if line.startswith("    ") and not line.startswith("        "):
                new_lines.append("    " + line)
            elif line.startswith("        "): # 8 spaces + 4
                new_lines.append("    " + line)
            elif line.startswith("\t"):
                new_lines.append("    " + line)
            else:
                new_lines.append("    " + line) # Add 4 spaces to everything to push it into 'with canvas_container'
        else:
            new_lines.append("\n")

        i += 1
        continue

    # outside everything
    new_lines.append(line)
    i += 1

with open("app.py", "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("SUCCESS")
