import re

path = r'C:\Users\hp\Desktop\NCMB\static\index.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

pattern = r'\s*<!-- Examination Hall Directives & Instructions -->\s*<div class="info-banner".*?</div>\s*</div>'
match = re.search(pattern, content, flags=re.DOTALL)
if match:
    content = re.sub(pattern, '', content, count=1, flags=re.DOTALL)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("SUCCESS: info-banner removed from index.html!")
else:
    print("Pattern not matched!")
