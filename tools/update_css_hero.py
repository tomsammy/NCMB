with open(r'C:\Users\hp\Desktop\NCMB\static\css\style.css', 'r', encoding='utf-8') as f:
    css = f.read()

target = """.card-entry-header .hero-logo {
  height: 68px;
  margin-bottom: 12px;
}"""

replacement = """.card-entry-header .hero-logo {
  height: 72px;
  max-width: 90%;
  object-fit: contain;
  margin-bottom: 8px;
  filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.35));
}"""

if target in css:
    css = css.replace(target, replacement)
elif target.replace('\n', '\r\n') in css:
    css = css.replace(target.replace('\n', '\r\n'), replacement.replace('\n', '\r\n'))

with open(r'C:\Users\hp\Desktop\NCMB\static\css\style.css', 'w', encoding='utf-8') as f:
    f.write(css)

print("Updated style.css successfully!")
