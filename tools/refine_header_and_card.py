with open(r'C:\Users\hp\Desktop\NCMB\static\index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update brand-logo in header to emblem_logo.png
html = html.replace(
    '<img src="/static/images/logo_white.png?v=3" alt="Organization Logo" class="brand-logo" onerror="this.src=\'/static/images/logo.png\'">',
    '<img src="/static/images/emblem_logo.png?v=1" alt="NCDMB Emblem" class="brand-logo" onerror="this.src=\'/static/images/logo.png\'">'
)

# 2. Remove redundant card-entry-org-name since logo_white.png contains the text
redundant_div = '''          <div class="card-entry-org-name" style="font-size: 1.15rem; font-weight: 800; color: #ffffff; letter-spacing: 0.5px; text-transform: uppercase; margin: 6px 0 6px 0; text-shadow: 0 2px 4px rgba(0,0,0,0.35);">
            Nigerian Content Development and Monitoring Board (NCDMB)
          </div>'''

if redundant_div in html:
    html = html.replace(redundant_div + '\n', '')
    print("Removed redundant card-entry-org-name")
else:
    print("Redundant div not found directly, checking regex")
    import re
    html = re.sub(r'\s*<div class="card-entry-org-name".*?</div>', '', html)
    print("Regex replaced card-entry-org-name")

with open(r'C:\Users\hp\Desktop\NCMB\static\index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated index.html branding successfully!")
