import re

with open(r'C:\Users\hp\Desktop\NCMB\static\index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Remove homepage-exam-alert block
html = re.sub(
    r'\s*<!-- Prominent Examination Day Notice Banner -->\s*<div class="homepage-exam-alert".*?</div>\s*</div>',
    '',
    html,
    flags=re.DOTALL
)

# Remove login-footer-verification block
html = re.sub(
    r'\s*<!-- Bottom Sub-Link for Candidate Verification & Photocard Printing -->\s*<div class="login-footer-verification".*?</div>\s*</div>',
    '\n          </div>',
    html,
    flags=re.DOTALL
)

with open(r'C:\Users\hp\Desktop\NCMB\static\index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated index.html successfully!")
