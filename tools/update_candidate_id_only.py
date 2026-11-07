with open(r'C:\Users\hp\Desktop\NCMB\static\index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update candidate badge in exam view
html = html.replace(
    '<h3 id="exam-candidate-name">Officer Name</h3>\n            <p id="exam-candidate-psn">PSN: - | GL --</p>',
    '<h3 id="exam-candidate-name">Candidate ID</h3>\n            <p id="exam-candidate-psn">Status: Active Session</p>'
)
html = html.replace(
    '<h3 id="exam-candidate-name">Officer Name</h3>\r\n            <p id="exam-candidate-psn">PSN: - | GL --</p>',
    '<h3 id="exam-candidate-name">Candidate ID</h3>\r\n            <p id="exam-candidate-psn">Status: Active Session</p>'
)

# 2. Update initial countdown display to 60:00
html = html.replace(
    '<span id="timer-text" class="timer-countdown">20:00</span>',
    '<span id="timer-text" class="timer-countdown">60:00</span>'
)

# 3. Update Result slip: Replace 'Officer Name' with 'Candidate ID'
html = html.replace(
    '<div class="lbl">Officer Name</div>\n                <div class="val" id="res-name">-</div>',
    '<div class="lbl">Candidate ID</div>\n                <div class="val" id="res-name">-</div>'
)
html = html.replace(
    '<div class="lbl">Officer Name</div>\r\n                <div class="val" id="res-name">-</div>',
    '<div class="lbl">Candidate ID</div>\r\n                <div class="val" id="res-name">-</div>'
)

# Replace 'PSN' with 'Assessment Paper'
html = html.replace(
    '<div class="lbl">PSN</div>\n                <div class="val" id="res-psn">-</div>',
    '<div class="lbl">Portal Assessment</div>\n                <div class="val" id="res-psn">-</div>'
)
html = html.replace(
    '<div class="lbl">PSN</div>\r\n                <div class="val" id="res-psn">-</div>',
    '<div class="lbl">Portal Assessment</div>\r\n                <div class="val" id="res-psn">-</div>'
)

with open(r'C:\Users\hp\Desktop\NCMB\static\index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html updated successfully!")

with open(r'C:\Users\hp\Desktop\NCMB\static\js\cbt.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Update exam header candidate text in cbt.js
js = js.replace(
    "document.getElementById('exam-candidate-name').textContent = state.candidate.name;\n        document.getElementById('exam-candidate-psn').textContent = `PSN: ${state.candidate.psn} | Paper: ${state.candidate.paper_code || 'Cadre Evaluation'}`;",
    "document.getElementById('exam-candidate-name').textContent = `Candidate ID: ${state.candidate.psn}`;\n        document.getElementById('exam-candidate-psn').textContent = `Paper: ${state.candidate.paper_code || 'Module 1 Assessment'}`;",
)
js = js.replace(
    "document.getElementById('exam-candidate-name').textContent = state.candidate.name;\r\n        document.getElementById('exam-candidate-psn').textContent = `PSN: ${state.candidate.psn} | Paper: ${state.candidate.paper_code || 'Cadre Evaluation'}`;",
    "document.getElementById('exam-candidate-name').textContent = `Candidate ID: ${state.candidate.psn}`;\r\n        document.getElementById('exam-candidate-psn').textContent = `Paper: ${state.candidate.paper_code || 'Module 1 Assessment'}`;",
)

js = js.replace(
    "document.getElementById('exam-candidate-name').textContent = state.candidate.name;\n      document.getElementById('exam-candidate-psn').textContent = `PSN: ${state.candidate.psn} | Paper: ${state.candidate.paper_code || data.paper_code || 'Cadre Evaluation'}`;",
    "document.getElementById('exam-candidate-name').textContent = `Candidate ID: ${state.candidate.psn}`;\n      document.getElementById('exam-candidate-psn').textContent = `Paper: ${state.candidate.paper_code || data.paper_code || 'Module 1 Assessment'}`;",
)
js = js.replace(
    "document.getElementById('exam-candidate-name').textContent = state.candidate.name;\r\n      document.getElementById('exam-candidate-psn').textContent = `PSN: ${state.candidate.psn} | Paper: ${state.candidate.paper_code || data.paper_code || 'Cadre Evaluation'}`;",
    "document.getElementById('exam-candidate-name').textContent = `Candidate ID: ${state.candidate.psn}`;\r\n      document.getElementById('exam-candidate-psn').textContent = `Paper: ${state.candidate.paper_code || data.paper_code || 'Module 1 Assessment'}`;",
)

# In results slip: set res-name to Candidate ID
js = js.replace(
    "if (nameEl) nameEl.textContent = state.candidate.name || 'Candidate';",
    "if (nameEl) nameEl.textContent = state.candidate.psn || 'Candidate';"
)
js = js.replace(
    "if (psnEl) psnEl.textContent = state.candidate.psn || '-';",
    "if (psnEl) psnEl.textContent = state.candidate.paper_code || 'Module 1 Digital Foundations';"
)

with open(r'C:\Users\hp\Desktop\NCMB\static\js\cbt.js', 'w', encoding='utf-8') as f:
    f.write(js)

print("cbt.js updated successfully!")
