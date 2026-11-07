path = r'C:\Users\hp\Desktop\NCMB\static\index.html'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

target = '            <!-- Login Form -->'

instructions = '''            <!-- Examination Hall Directives & Instructions -->
            <div class="info-banner" style="margin-top: 0; margin-bottom: 22px;">
              <div style="font-size: 1.6rem;">⏱️</div>
              <div>
                <strong>Official Examination Hall Instructions:</strong>
                <ul style="margin-top: 4px; margin-left: 18px; font-size: 0.85rem; line-height: 1.5;">
                  <li>Structure: <strong>3-Part Assessment (Part 1, Part 2, and Part 3)</strong></li>
                  <li>Duration: <strong>Strictly 60 Minutes per Part</strong> (Live automatic countdown timer)</li>
                  <li>Questions: <strong>60 Multiple Choice Questions per Part</strong> (1.0 mark each = 60 marks per Part | Total: 180 Marks)</li>
                  <li>Curriculum: <strong>Part 1</strong> (Digital Productivity & Statistics) • <strong>Part 2</strong> (SQL & RDBMS) • <strong>Part 3</strong> (Data Governance & Oil & Gas Analytics)</li>
                  <li>Authentication: <strong>Candidate ID + 5-Digit Examination PIN</strong></li>
                  <li>PIN Binding: Login PIN binds permanently to your record upon first login. Single attempt only.</li>
                </ul>
              </div>
            </div>

            <!-- Login Form -->'''

if target in html:
    html = html.replace(target, instructions, 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("SUCCESS: Instructions restored into index.html!")
else:
    print("Target not found!")
