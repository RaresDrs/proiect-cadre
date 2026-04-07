with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Lines are 0-indexed. Canvas body starts at line index 344 (line 345) and ends
# just before the first 'elif modul ==' which is at line index 933 (line 934).
# We need to indent lines 344..932 (0-indexed) by 4 additional spaces,
# BUT line 344 is already `    with col_canvas:` — leave that as-is.
# So indent lines 345..932 (0-indexed).

canvas_body_start = 344  # 0-indexed, first line INSIDE with col_canvas
canvas_body_end   = 932  # 0-indexed, last line of canvas body (inclusive)

new_lines = []
for i, line in enumerate(lines):
    if canvas_body_start <= i <= canvas_body_end:
        # Only indent non-blank lines
        if line.strip():
            # Fix the old calculate button trigger to use btn_calc
            fixed = line.replace(
                'if st.button("▶ Efectuează Calculul",type="primary",width="stretch",key="gv_calc"):',
                'if btn_calc:'
            )
            new_lines.append('    ' + fixed)
        else:
            new_lines.append(line)
    else:
        new_lines.append(line)

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Done — canvas block indented.")
