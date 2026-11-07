import re

path = r'C:\Users\hp\Desktop\NCMB\static\index.html'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

html = re.sub(r'style\.css\?v=[^"\'\s>]+', 'style.css?v=20261107_v4', html)
html = re.sub(r'cbt\.js\?v=[^"\'\s>]+', 'cbt.js?v=20261107_v4', html)

with open(path, 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated asset version strings in index.html to v20261107_v4 successfully!")
