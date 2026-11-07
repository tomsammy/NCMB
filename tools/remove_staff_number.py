with open(r'C:\Users\hp\Desktop\NCMB\static\index.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace(
    'Enter your Candidate / Staff Number and 5-Digit Examination PIN to commence the assessment',
    'Enter your Candidate ID and 5-Digit Examination PIN to commence the assessment'
)

html = html.replace(
    '<li>Authentication: <strong>Staff Number / Candidate ID + 5-Digit Examination PIN</strong></li>',
    '<li>Authentication: <strong>Candidate ID + 5-Digit Examination PIN</strong></li>'
)

html = html.replace(
    '<label for="token-exam-psn">Staff Number / Candidate ID <span class="req">*</span></label>',
    '<label for="token-exam-psn">Candidate ID <span class="req">*</span></label>'
)

html = html.replace(
    'placeholder="e.g. NCDMB-2026-001 or Staff ID"',
    'placeholder="e.g. NCDMB-2026-001"'
)

with open(r'C:\Users\hp\Desktop\NCMB\static\index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html updated successfully!")

with open(r'C:\Users\hp\Desktop\NCMB\static\js\cbt.js', 'r', encoding='utf-8') as f:
    js = f.read()

js = js.replace('Staff ID / Candidate ID:', 'Candidate ID:')
js = js.replace('Staff Number / Candidate ID', 'Candidate ID')

with open(r'C:\Users\hp\Desktop\NCMB\static\js\cbt.js', 'w', encoding='utf-8') as f:
    f.write(js)

print("cbt.js updated successfully!")
