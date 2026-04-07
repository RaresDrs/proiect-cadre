import sys

with open('app.py', 'r', encoding='utf-8') as f:
    original_text = f.read()

# CSS replacement
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
h4 { color: #4a5568; font-weight: 600; font-size: 1.1rem; margin-top: 10px; padding-bottom: 5px; border-bottom: 1px solid #edf2f7; }
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

if css_old in original_text:
    text = original_text.replace(css_old, css_new)
else:
    print("WARNING: CSS target missing. Could be already replaced.")
    text = original_text

lines = text.splitlines()

new_lines = []
i = 0
in_target = False

while i < len(lines):
    line = lines[i]
    if line.strip() == 'if modul == "Calcul Grinzi simplu":':
        new_lines.append(line)
        new_lines.append('    col_panel, col_canvas = st.columns([1.5, 4], gap="large")')
        new_lines.append('    with col_panel:')
        new_lines.append('        st.markdown("<h3 style=\'margin-top:-10px;\'>🎛️ Panou Control</h3>", unsafe_allow_html=True)')
        new_lines.append('        tab_geom, tab_sup, tab_load = st.tabs(["Material", "Reazeme", "Încărcări"])')
        new_lines.append('        with tab_geom:')
        
        # Skip st.title and st.markdown("---")
        i += 3
        continue
    
    if 'st.session_state.gv_forces=f_edited' in line:
        # End of inputs definition
        spaces = len(line) - len(line.lstrip())
        new_lines.append(" " * (spaces + 4) + line.lstrip())
        new_lines.append('        st.markdown("<br>", unsafe_allow_html=True)')
        new_lines.append('        btn_calc = st.button("▶ Efectuează Calculul", type="primary", use_container_width=True, key="gv_calc")')
        new_lines.append('')
        new_lines.append('    canvas_container = col_canvas.container()')
        new_lines.append('    with canvas_container:')
        new_lines.append('        st.title("BeamFlow | Proiectare")')
        i += 1
        
        # Now process all subsequent lines until the next `elif modul == `
        while i < len(lines):
            rest_line = lines[i]

            if rest_line.strip().startswith('elif modul == '):
                # End of this module!
                new_lines.append(rest_line)
                i += 1
                break

            if 'if st.button("▶ Efectuează Calculul",type="primary",width="stretch",key="gv_calc")' in rest_line:
                new_lines.append('        if btn_calc:')
                i += 1
                continue
            
            # For the rest of the lines, just push them to 1 level deeper (4 spaces) 
            # EXCEPT if they are root level (4 spaces) => make them 8 spaces.
            # Basically, just add 4 spaces to everything.
            if rest_line.strip() == "":
                new_lines.append("")
            else:
                new_lines.append("    " + rest_line)
            i += 1
            
        continue

    # Inner logic for parsing tab additions
    if 'st.subheader("Reazeme")' in line:
        new_lines.append('        with tab_sup:')
        new_lines.append('            st.markdown("#### Setări Reazeme")')
        i += 1
        continue
    if 'st.subheader("Încărcări distribuite q")' in line:
        new_lines.append('        with tab_load:')
        new_lines.append('            st.markdown("#### Distribuite (q)")')
        i += 1
        continue
    if 'st.subheader("Forțe concentrate și momente")' in line:
        new_lines.append('            st.markdown("#### Concentrate")')
        i += 1
        continue

    # Clean up st.sidebar usage
    # We only apply these if we are actually past the layout creation and haven't hit btn_calc
    # BUT wait, this simple script runs over the WHOLE file. We should only do this between `if modul` and `btn_calc`.
    # Let's fix that.
    
    # Just append normally for now, we will add the space shift dynamically.
    if 'if modul == "Calcul Grinzi simplu":' in "\n".join(new_lines) and 'canvas_container =' not in "\n".join(new_lines):
        line = line.replace('st.sidebar.', 'st.')
        line = line.replace('st.header("1. ', 'st.markdown("#### 1. ')
        line = line.replace('st.header("2. ', 'st.markdown("#### 2. ')
        line = line.replace('st.header("3. ', 'st.markdown("#### 3. ')

        if line.strip() != "":
            # Whatever indentation it had natively, add 4 spaces to put it inside the with col_panel -> with tab_*
            # Original: 4 spaces inside `if modul` -> 8 spaces inside `with split` -> 12 inside `with tab_*`
            # Since original was 4 spaces, we add 8 spaces!
            spaces = len(line) - len(line.lstrip())
            new_lines.append(" " * (spaces + 4) + line.lstrip())
        else:
            new_lines.append("")
        i += 1
        continue

    new_lines.append(line)
    i += 1

with open('app.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(new_lines) + '\n')
print("SUCCESS")
