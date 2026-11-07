html_path = r'C:\Users\hp\Desktop\NCMB\static\index.html'
js_path = r'C:\Users\hp\Desktop\NCMB\static\js\cbt.js'

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update the green instruction box
old_box = """                <strong>Official Examination Hall Instructions:</strong>
                <ul style="margin-top: 4px; margin-left: 18px; font-size: 0.85rem;">
                  <li>Duration: <strong>Strictly 20 Minutes</strong> (Live automatic countdown timer)</li>
                  <li>Questions: <strong>40 Cadre-Specific Multiple Choice Questions</strong> (2.5 marks each = 100 marks)</li>
                  <li>Authentication: <strong>PSN + 5-Digit Login PIN</strong> issued physically in the examination hall</li>
                  <li>PIN Binding: Login PIN binds permanently to your PSN upon first login. Single attempt only.</li>
                </ul>"""

new_box = """                <strong>Official Examination Hall Instructions:</strong>
                <ul style="margin-top: 4px; margin-left: 18px; font-size: 0.85rem; line-height: 1.5;">
                  <li>Structure: <strong>3-Part Assessment (Part 1, Part 2, and Part 3)</strong></li>
                  <li>Duration: <strong>Strictly 60 Minutes per Part</strong> (Live automatic countdown timer)</li>
                  <li>Questions: <strong>60 Multiple Choice Questions per Part</strong> (1.0 mark each = 60 marks per Part | Total: 180 Marks)</li>
                  <li>Curriculum: <strong>Part 1</strong> (Digital Productivity & Statistics) • <strong>Part 2</strong> (SQL & RDBMS) • <strong>Part 3</strong> (Data Governance & Oil & Gas Analytics)</li>
                  <li>Authentication: <strong>Staff Number / Candidate ID + 5-Digit Examination PIN</strong></li>
                  <li>PIN Binding: Login PIN binds permanently to your record upon first login. Single attempt only.</li>
                </ul>"""

html = html.replace(old_box, new_box)

# 2. Update the PSN label and input
html = html.replace(
    '<label for="token-exam-psn">PSN</label>',
    '<label for="token-exam-psn">Staff Number / Candidate ID <span class="req">*</span></label>'
)

html = html.replace(
    '<input type="text" id="token-exam-psn" class="form-control" placeholder="e.g. 128439"',
    '<input type="text" id="token-exam-psn" class="form-control" placeholder="e.g. NCDMB-2026-001 or Staff ID"'
)

# 3. Update button text
html = html.replace(
    'LOGIN & COMMENCE CBT EXAMINATION (20 MINS)',
    'LOGIN & COMMENCE CBT ASSESSMENT (60 MINS)'
)

# 4. Update "All 40 questions" text
html = html.replace(
    'All 40 questions must be answered before manual submission can be completed.',
    'All questions in this Part must be answered before manual submission can be completed.'
)

html = html.replace('(Determines 40 questions)', '(Determines examination questions)')
html = html.replace('40 Questions Loaded', 'Questions Loaded')
html = html.replace('Save All 40 Questions', 'Save All Questions')
html = html.replace('Search within these 40 questions', 'Search within questions')
html = html.replace('Loading all 40 questions', 'Loading questions')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("Updated index.html successfully!")

# Now update cbt.js
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

js = js.replace(
    "startBtnText.textContent = '🚀 LOGIN & COMMENCE CBT EXAMINATION (20 MINS)';",
    "startBtnText.textContent = '🚀 LOGIN & COMMENCE CBT ASSESSMENT (60 MINS)';"
)

js = js.replace(
    "<li><strong>Exam Duration:</strong> Strictly <strong>20 Minutes</strong> (40 cadre-specific multiple choice questions). The test automatically submits when the countdown timer expires.</li>",
    "<li><strong>Exam Structure & Duration:</strong> The assessment is structured into <strong>Part 1, Part 2, and Part 3</strong>. Each part has a duration of <strong>Strictly 60 Minutes</strong> (60 multiple choice questions per part, 1 mark each). The test automatically submits when the countdown timer expires.</li>"
)

js = js.replace(
    "state.durationSeconds = (data.duration_minutes || 20) * 60; // Strictly 20 minutes (1200s)",
    "state.durationSeconds = (data.duration_minutes || 60) * 60; // Strictly 60 minutes (3600s)"
)

js = js.replace("view/edit 40 questions", "view/edit examination questions")
js = js.replace("Fetching all 40 questions", "Fetching all questions")
js = js.replace("Saving 40 Questions...", "Saving Questions...")
js = js.replace("Save All 40 Questions", "Save All Questions")

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Updated cbt.js successfully!")
