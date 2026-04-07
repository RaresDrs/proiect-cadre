import re
import sys

# Read powershell redirected file
with open("app_clean.py", "r", encoding="utf-16") as f:
    text = f.read()

# 1. Update CSS
css_old = """<style>
[data-testid="stSidebar"]{background:#0d1b2a;}
[data-testid="stSidebar"] *{color:#e8e8e8!important;}
[data-testid="stSidebar"] input{color:#111111!important;background:#ffffff!important;}
[data-testid="stSidebar"] input[type="number"]{color:#111111!important;background:#ffffff!important;}
[data-testid="stSidebar"] .stNumberInput input{color:#111111!important;background:#ffffff!important;}
[data-testid="stSidebar"] label{color:#e8e8e8!important;}
h1{color:#0d1b2a;border-bottom:3px solid #E8641A;padding-bottom:8px;}
h2{color:#1a3a5c;}h3{color:#0d1b2a;}
.result-box{background:linear-gradient(135deg,#f0f4ff,#e8f0fe);border-left:5px solid #E8641A;
  padding:14px 18px;border-radius:8px;margin:10px 0;}
div[data-testid="stMetric"]{background:#f8f9fa;border-radius:10px;padding:12px;border:1px solid #dee2e6;}
.stTabs [data-baseweb="tab"]{background:#f0f4ff;border-radius:8px 8px 0 0;padding:8px 18px;font-weight:600;}
.stTabs [aria-selected="true"]{background:#E8641A!important;color:white!important;}
</style>"""

css_new = """<style>
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
</style>"""

if css_old in text:
    text = text.replace(css_old, css_new)

# 2. Update Layout
start_str = """if modul == "Calcul Grinzi simplu":
    st.title("Calcul Grinzi simplu")
    st.markdown("---")"""
end_forces_str = """        st.session_state.gv_forces=f_edited"""

if start_str not in text or end_forces_str not in text:
    print("ERROR parts not found")
    sys.exit()

pre_start = text.split(start_str)[0]
rest = text.split(start_str)[1]
forces_block = rest.split(end_forces_str)[0] + end_forces_str
rest_after_forces = rest.split(end_forces_str)[1]

new_panel_code = """if modul == "Calcul Grinzi simplu":
    # 2-column layout
    col_panel, col_canvas = st.columns([1.5, 4], gap="large")
    
    with col_panel:
        st.markdown("<h3 style='margin-top:-10px;'>Panou Control</h3>", unsafe_allow_html=True)
        tab_geom, tab_sup, tab_load = st.tabs(["Material", "Reazeme", "Încărcări"])
        
        with tab_geom:
"""
old_lines = forces_block.splitlines()

for line in old_lines:
    if line.strip() == "": continue
    if "st.subheader(\"Reazeme\")" in line:
        new_panel_code += "        with tab_sup:\n"
        new_panel_code += "            st.markdown(\"#### Setări Reazeme\")\n"
        continue
    
    if "st.subheader(\"Încărcări distribuite q\")" in line:
        new_panel_code += "        with tab_load:\n"
        new_panel_code += "            st.markdown(\"#### Distribuite (q)\")\n"
        continue

    line = line.replace("st.sidebar.", "st.")
    line = line.replace("st.header(\"1. ", "st.markdown(\"#### 1. ")
    line = line.replace("st.header(\"2. ", "st.markdown(\"#### 2. ")
    line = line.replace("st.header(\"3. ", "st.markdown(\"#### 3. ")
    if "st.subheader(\"Forțe concentrate și momente\")" in line:
        line = "            st.markdown(\"#### Concentrate\")"

    # Fix indentation based on original spaces
    original_spaces = len(line) - len(line.lstrip())
    # The minimum indentation in this block was 4. We want minimum to be 12.
    # So we add exactly 8 spaces.
    new_panel_code += " " * 8 + line + "\n"

new_panel_code += """        st.markdown("<br>", unsafe_allow_html=True)
        btn_calc = st.button("▶ Efectuează Calculul", type="primary", use_container_width=True, key="gv_calc")

    canvas_container = col_canvas.container()
    with canvas_container:
        st.title("BeamFlow | Proiectare")
"""

new_rest_lines = []
for line in rest_after_forces.splitlines():
    if line.strip() == 'if st.button("▶ Efectuează Calculul",type="primary",width="stretch",key="gv_calc"):':
        new_rest_lines.append("        if btn_calc:")
    else:
        if line == "":
            new_rest_lines.append("")
        else:
            new_rest_lines.append("    " + line)

new_text = pre_start + new_panel_code + "\n".join(new_rest_lines)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(new_text)

print("SUCCESS")
