with open(r'C:\Users\hp\Desktop\NCMB\static\index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if line.strip() == '</div>' and i > 50 and i < 65 and 'view-entry' in lines[i-1]:
        continue
    new_lines.append(line)

with open(r'C:\Users\hp\Desktop\NCMB\static\index.html', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Cleaned up dangling div successfully!")
