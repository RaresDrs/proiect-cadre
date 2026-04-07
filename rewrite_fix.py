with open("app.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i in range(310, 420):
    line = lines[i]
    if line.strip() == "": continue
    if "st.markdown(\"<br>\", unsafe_allow_html=True)" in line:
        break # reached end of panel
    # If the line starts with 8 spaces but NOT 12
    if line.startswith("        ") and not line.startswith("            "):
        lines[i] = "    " + line

with open("app.py", "w", encoding="utf-8") as f:
    f.writelines(lines)

print("FIXED")
