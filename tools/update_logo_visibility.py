with open(r'C:\Users\hp\Desktop\NCMB\static\index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update header-bar logo to logo_white.png
html = html.replace(
    '<img src="/static/images/logo.png" alt="Organization Logo" class="brand-logo" onerror="this.style.display=\'none\'">',
    '<img src="/static/images/logo_white.png" alt="Organization Logo" class="brand-logo" onerror="this.src=\'/static/images/logo.png\'">'
)

# 2. Update card-entry-header with logo_white.png and explicit visible title
old_card_header = '''        <div class="card-entry-header">
          <img src="/static/images/logo.png" alt="Organization Logo" class="hero-logo" onerror="this.style.display='none'">
          <h2 id="entry-card-title">CBT Examination Login</h2>
          <p id="entry-card-subtitle">Enter your Candidate / Staff Number and 5-Digit Examination PIN to commence the assessment</p>
        </div>'''

new_card_header = '''        <div class="card-entry-header">
          <img src="/static/images/logo_white.png" alt="Nigerian Content Development and Monitoring Board (NCDMB)" class="hero-logo" onerror="this.src=\'/static/images/logo.png\'">
          <div class="card-entry-org-name" style="font-size: 1.15rem; font-weight: 800; color: #ffffff; letter-spacing: 0.5px; text-transform: uppercase; margin: 6px 0 6px 0; text-shadow: 0 2px 4px rgba(0,0,0,0.35);">
            Nigerian Content Development and Monitoring Board (NCDMB)
          </div>
          <h2 id="entry-card-title" style="color: #fde68a; font-size: 1.25rem; font-weight: 700; margin: 0 0 6px 0;">CBT Examination Login</h2>
          <p id="entry-card-subtitle" style="color: #e2e8f0; font-size: 0.88rem; margin: 0;">Enter your Candidate / Staff Number and 5-Digit Examination PIN to commence the assessment</p>
        </div>'''

if old_card_header in html:
    html = html.replace(old_card_header, new_card_header)
    print("card-entry-header replaced directly")
else:
    # try CRLF
    html = html.replace(old_card_header.replace('\n', '\r\n'), new_card_header.replace('\n', '\r\n'))
    print("card-entry-header replaced (CRLF)")

with open(r'C:\Users\hp\Desktop\NCMB\static\index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated index.html successfully!")
