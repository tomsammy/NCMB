import re

html_path = r'C:\Users\hp\Desktop\NCMB\static\index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update title
html = re.sub(
    r'<title.*?>.*?</title>',
    '<title class="exam-title-tag">NCDMB CBT Portal - Assessment on Module 1: Digital Foundations</title>',
    html
)

# 2. Update Header Brand Section
old_header = """<div class="brand-titles">
        <h1 class="org-name-text">CBT EXAMINATION PLATFORM</h1>
        <p class="exam-title-text">Professional Competency & Evaluation Examination</p>
      </div>"""

new_header = """<div class="brand-titles">
        <h1 class="org-name-text" style="letter-spacing: 0.5px; font-weight: 800;">NIGERIAN CONTENT DEVELOPMENT AND MONITORING BOARD</h1>
        <p class="exam-title-text" style="color: #E5A823; font-weight: 600;">Assessment on Module 1: Digital Foundations</p>
      </div>"""

html = html.replace(old_header, new_header)

# 3. Update entry card title and labels
html = html.replace(
    'Enter your PSN and 5-Digit Login PIN to commence your evaluation',
    'Enter your Candidate / Staff Number and 5-Digit Examination PIN to commence the assessment'
)

html = html.replace(
    'Public Service Number (PSN):',
    'Candidate / Staff ID Number:'
)

html = html.replace(
    'placeholder="e.g. 123456"',
    'placeholder="e.g. NCDMB-2026-001 or Staff ID"'
)

# 4. Result slip headers
html = html.replace(
    '<h2 class="org-name-text">CBT EXAMINATION PLATFORM</h2>',
    '<h2 class="org-name-text" style="color: #00563F; font-weight: 800;">NIGERIAN CONTENT DEVELOPMENT AND MONITORING BOARD</h2>'
)

html = html.replace(
    'Examination Assessment Commission',
    'Nigerian Content Development and Monitoring Board (NCDMB)'
)

html = html.replace(
    'Examination Portal',
    'NCDMB CBT Portal (www.ncdmb.gov.ng)'
)

# 5. Instructions Modal
html = html.replace(
    'IMPORTANT NOTICE: MANDATORY EXAMINATION DAY DIRECTIVES',
    'NCDMB ASSESSMENT GUIDELINES: MODULE 1 DIGITAL FOUNDATIONS'
)

html = html.replace(
    'All candidates must arrive with their <strong>fully charged smartphone (Android or iOS)</strong>, <strong>active data subscription</strong>, <strong>updated web browser</strong> (Chrome, Opera Mini, Firefox, Safari, Edge, etc.), and <strong>printed photocard only</strong>. <strong>Strictly no loitering</strong> within the venue.',
    'Candidates must answer all 60 multiple choice questions within the 60-minute duration. Questions cover Digital Productivity, Cloud Ecosystems, Statistics, SQL RDBMS, Data Ethics, and Oil & Gas Analytics. Adhere strictly to examination integrity guidelines.'
)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated index.html with NCDMB brand identity!")
