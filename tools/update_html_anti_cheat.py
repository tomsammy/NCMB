with open(r'C:\Users\hp\Desktop\NCMB\static\index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update admin-control-bar with anti-cheat toggle
old_ctrl_bar = '''        <!-- Admin CBT Exam Control Bar -->
        <div class="admin-control-bar">
          <div class="admin-status-box" id="admin-status-box">
            <span class="status-pulse-dot" id="status-pulse-dot"></span>
            <div>
              <div style="font-size:0.72rem; font-weight:800; color:#64748b; text-transform:uppercase; letter-spacing:0.05em;">CBT NCDMB CBT Portal (www.ncdmb.gov.ng) Status</div>
              <strong id="admin-status-text" class="status-text-open">🟢 ACTIVE & OPEN FOR CANDIDATES</strong>
            </div>
          </div>
          <button type="button" class="btn-toggle-exam btn-status-close" id="btn-toggle-status" onclick="toggleExamStatus()">
            <span id="btn-toggle-status-text">🔒 Close CBT Examination</span>
          </button>
        </div>'''

new_ctrl_bar = '''        <!-- Admin CBT Exam Control Bar (Exam Access & Anti-Cheat Controls) -->
        <div class="admin-control-bar" style="display: flex; gap: 14px; flex-wrap: wrap; margin-bottom: 24px;">
          <div style="flex: 1; min-width: 300px; display: flex; align-items: center; justify-content: space-between; background: #fff; padding: 12px 18px; border-radius: 10px; border: 1.5px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
            <div class="admin-status-box" id="admin-status-box" style="margin: 0; padding: 0; border: none; background: transparent;">
              <span class="status-pulse-dot" id="status-pulse-dot"></span>
              <div>
                <div style="font-size:0.72rem; font-weight:800; color:#64748b; text-transform:uppercase; letter-spacing:0.05em;">CBT Portal Access Status</div>
                <strong id="admin-status-text" class="status-text-open">🟢 ACTIVE & OPEN FOR CANDIDATES</strong>
              </div>
            </div>
            <button type="button" class="btn-toggle-exam btn-status-close" id="btn-toggle-status" onclick="toggleExamStatus()">
              <span id="btn-toggle-status-text">🔒 Close CBT Examination</span>
            </button>
          </div>

          <!-- Anti-Cheat Proctor Shield Control Box -->
          <div style="flex: 1; min-width: 300px; display: flex; align-items: center; justify-content: space-between; background: #fff; padding: 12px 18px; border-radius: 10px; border: 1.5px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05);" id="admin-anti-cheat-box">
            <div style="display: flex; align-items: center; gap: 10px;">
              <span id="anti-cheat-status-icon" style="font-size: 1.6rem;">🛡️</span>
              <div>
                <div style="font-size:0.72rem; font-weight:800; color:#64748b; text-transform:uppercase; letter-spacing:0.05em;">Anti-Cheat Proctor Shield</div>
                <strong id="anti-cheat-status-text" style="color: #16a34a; font-size: 0.92rem; font-weight: 800;">ACTIVE (3 Strikes Auto-Submit)</strong>
              </div>
            </div>
            <button type="button" class="btn-toggle-exam" id="btn-toggle-anti-cheat" style="background: #dc2626; color: #fff; border: none; border-radius: 6px; padding: 8px 14px; font-weight: 700; cursor: pointer; transition: all 0.2s;" onclick="toggleAntiCheatStatus()">
              <span id="btn-toggle-anti-cheat-text">🔒 Turn OFF Anti-Cheat</span>
            </button>
          </div>
        </div>'''

if old_ctrl_bar in html:
    html = html.replace(old_ctrl_bar, new_ctrl_bar)
else:
    html = html.replace(old_ctrl_bar.replace('\n', '\r\n'), new_ctrl_bar.replace('\n', '\r\n'))

# 2. Update security-violation-modal
html = html.replace(
    '<div class="modal-overlay" id="security-violation-modal" style="display:none !important; z-index: 100000;">',
    '<div class="modal-overlay" id="security-violation-modal" style="display:none; z-index: 100000;">'
)

with open(r'C:\Users\hp\Desktop\NCMB\static\index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated index.html with Anti-Cheat admin control and modal styles!")
