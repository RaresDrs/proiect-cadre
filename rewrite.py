import re

with open("app_staged.py", "w", encoding="utf-8") as f:
    pass # we will read app.py and write directly later, wait, let's process it in memory.

with open("app.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
in_css = False
in_beam_module = False
beam_done = False

css_found = False

for i, line in enumerate(lines):
    # CSS Replacement
    if "<style>" in line and not css_found:
        in_css = True
        css_found = True
        new_lines.append(line)
        new_lines.append("""@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
/* Base Font */
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

/* Hide Streamlit Header/Footer */
header {visibility: hidden;}
footer {visibility: hidden;}

/* Main App Background */
.stApp { background-color: #f5f7fa; }

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 1px solid #e1e4e8;
}
[data-testid="stSidebar"] * { color: #1a202c !important; }

/* Titles */
h1 {
    color: #1a202c; 
    border-bottom: none; 
    font-weight: 700;
    font-size: 1.8rem;
    padding-bottom: 0px;
}
h2, h3 { color: #2d3748; font-weight: 600; }
h4 { color: #4a5568; font-weight: 600; font-size: 1.1rem; margin-top: 10px; }

/* Control Panel Inputs styling */
.stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div {
    background-color: #ffffff !important;
    border: 1px solid #cbd5e0 !important;
    border-radius: 6px !important;
    color: #1a202c !important;
    box-shadow: none !important;
}
.stTextInput>div>div>input:focus, .stNumberInput>div>div>input:focus {
    border-color: #3182ce !important;
    box-shadow: 0 0 0 1px #3182ce !important;
}

/* Primary Buttons */
button[kind="primary"] {
    background-color: #3182ce !important;
    color: white !important;
    border-radius: 6px !important;
    border: none !important;
    font-weight: 600 !important;
    padding: 0.6rem 1rem !important;
    transition: background-color 0.2s ease;
}
button[kind="primary"]:hover {
    background-color: #2b6cb0 !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] {
    background-color: transparent !important;
    border-radius: 6px !important;
    padding: 8px 16px !important;
    font-weight: 500 !important;
    border: 1px solid transparent !important;
}
.stTabs [aria-selected="true"] {
    background-color: #ffffff !important;
    color: #3182ce !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: 0 -2px 0 0 #3182ce inset !important;
}

/* Metric box */
div[data-testid="stMetric"] {
    background: #ffffff;
    border-radius: 8px;
    padding: 16px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
""")
        continue
    
    if in_css:
        if "</style>" in line:
            in_css = False
            new_lines.append(line)
        continue

    new_lines.append(line)

with open("app_new.py", "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("CSS updated in app_new.py")
