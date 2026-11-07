with open(r'C:\Users\hp\Desktop\NCMB\static\js\cbt.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Update state object
js = js.replace(
    "adminTokensSummary: null,\n  examStatus: 'open'",
    "adminTokensSummary: null,\n  examStatus: 'open',\n  antiCheatStatus: 'enabled',\n  antiCheatEnabled: true"
)
js = js.replace(
    "adminTokensSummary: null,\r\n  examStatus: 'open'",
    "adminTokensSummary: null,\r\n  examStatus: 'open',\r\n  antiCheatStatus: 'enabled',\r\n  antiCheatEnabled: true"
)

# 2. Update initPortalStatus to capture anti_cheat
old_init_portal = """      state.examStatus = data.exam_status || 'open';
      applyExamStatusToUI(state.examStatus);"""

new_init_portal = """      state.examStatus = data.exam_status || 'open';
      applyExamStatusToUI(state.examStatus);
      if (data.anti_cheat_status) state.antiCheatStatus = data.anti_cheat_status;
      if (data.anti_cheat_enabled !== undefined) state.antiCheatEnabled = data.anti_cheat_enabled;"""

js = js.replace(old_init_portal, new_init_portal)

# 3. Update startTokenExam to capture anti_cheat
old_start_token = """      state.questions = data.questions;
      state.currentIndex = 0;"""

new_start_token = """      state.questions = data.questions;
      state.currentIndex = 0;
      if (data.anti_cheat_status) state.antiCheatStatus = data.anti_cheat_status;
      if (data.anti_cheat_enabled !== undefined) state.antiCheatEnabled = data.anti_cheat_enabled;"""

js = js.replace(old_start_token, new_start_token)

# 4. Replace proctorEngine with full active 3-strikes auto-submit engine
old_proctor_engine_pattern = """// PROCTORING & ANTI-CHEATING SHIELD ENGINE
// ============================================================================
const proctorEngine = {
  active: false,
  violations: 0,
  maxViolations: 999,"""

new_proctor_engine = """// PROCTORING & ANTI-CHEATING SHIELD ENGINE (3 STRIKES AUTO-SUBMIT)
// ============================================================================
const proctorEngine = {
  enabled: true,
  active: false,
  violations: 0,
  maxViolations: 3,
  violationLogs: [],
  lastViolationTime: 0,
  cooldownMs: 2500, // 2.5s debounce to prevent double-counting when window blur & visibilitychange fire together
  _visHandler: null,
  _blurHandler: null,
  _contextHandler: null,
  _copyHandler: null,
  _keyHandler: null,

  init() {
    this.closeViolationModal();
    this.hideCurtain();
  },

  start(candidate) {
    // Check if anti-cheat is disabled from backend
    if (state.antiCheatEnabled === false || (candidate && candidate.anti_cheat_enabled === false)) {
      this.enabled = false;
      this.active = false;
      this.detachListeners();
      this.updateSecurityBadge();
      this.closeViolationModal();
      return;
    }

    this.enabled = true;
    this.violations = 0;
    this.maxViolations = 3;
    this.violationLogs = [];
    this.lastViolationTime = 0;
    this.active = true;

    this.updateSecurityBadge();
    this.closeViolationModal();
    this.attachListeners();
  },

  stop() {
    this.active = false;
    this.detachListeners();
    this.closeViolationModal();
    this.hideCurtain();
  },

  attachListeners() {
    this.detachListeners();

    this._visHandler = () => {
      if (!this.active || !this.enabled || state.isSubmitted) return;
      if (document.hidden || document.visibilityState === 'hidden') {
        this.recordViolation('Switched tab or minimized browser window');
      }
    };

    this._blurHandler = () => {
      if (!this.active || !this.enabled || state.isSubmitted) return;
      this.recordViolation('Navigated away from examination window (lost focus)');
    };

    this._contextHandler = (e) => {
      if (this.active && this.enabled) {
        e.preventDefault();
      }
    };

    this._copyHandler = (e) => {
      if (this.active && this.enabled) {
        e.preventDefault();
        this.recordViolation('Copy / cut attempt intercepted');
      }
    };

    this._keyHandler = (e) => {
      if (!this.active || !this.enabled) return;
      // Intercept dev tools and window switching keys
      if (e.key === 'F12' || (e.ctrlKey && e.shiftKey && (e.key === 'I' || e.key === 'J' || e.key === 'C')) || (e.ctrlKey && (e.key === 'u' || e.key === 'U'))) {
        e.preventDefault();
        this.recordViolation('Restricted developer shortcut intercepted');
      }
    };

    document.addEventListener('visibilitychange', this._visHandler);
    window.addEventListener('blur', this._blurHandler);
    window.addEventListener('contextmenu', this._contextHandler);
    window.addEventListener('copy', this._copyHandler);
    window.addEventListener('cut', this._copyHandler);
    window.addEventListener('keydown', this._keyHandler);
  },

  detachListeners() {
    if (this._visHandler) document.removeEventListener('visibilitychange', this._visHandler);
    if (this._blurHandler) window.removeEventListener('blur', this._blurHandler);
    if (this._contextHandler) window.removeEventListener('contextmenu', this._contextHandler);
    if (this._copyHandler) window.removeEventListener('copy', this._copyHandler);
    if (this._copyHandler) window.removeEventListener('cut', this._copyHandler);
    if (this._keyHandler) window.removeEventListener('keydown', this._keyHandler);
  },

  recordViolation(reason) {
    if (!this.active || !this.enabled || state.isSubmitted) return;

    const now = Date.now();
    if (now - this.lastViolationTime < this.cooldownMs) {
      return; // Ignore rapid duplicate trigger
    }
    this.lastViolationTime = now;

    this.violations++;
    const timestamp = new Date().toLocaleTimeString();
    this.violationLogs.push({ time: timestamp, reason: reason, strike: this.violations });

    this.updateSecurityBadge();

    if (this.violations < this.maxViolations) {
      this.showViolationModal(reason);
    } else {
      // 3rd strike reached: Terminate & Auto-Submit
      this.handleTermination(reason);
    }
  },

  updateSecurityBadge() {
    const badge = document.getElementById('exam-security-badge');
    const text = document.getElementById('security-status-text');
    if (!badge || !text) return;

    if (!this.enabled) {
      badge.className = 'security-status-badge';
      badge.style.background = '#f1f5f9';
      badge.style.borderColor = '#cbd5e1';
      text.style.color = '#64748b';
      text.textContent = '⚪ Shield: Inactive (Switched Off)';
      return;
    }

    if (this.violations === 0) {
      badge.className = 'security-status-badge secure';
      badge.style.background = '#f0fdf4';
      badge.style.borderColor = '#16a34a';
      text.style.color = '#166534';
      text.textContent = `🛡️ Shield: Active (0/${this.maxViolations} Strikes)`;
    } else if (this.violations === 1) {
      badge.className = 'security-status-badge warning';
      badge.style.background = '#fffbeb';
      badge.style.borderColor = '#f59e0b';
      text.style.color = '#b45309';
      text.textContent = `⚠️ Strike 1/${this.maxViolations} (Navigated Away)`;
    } else if (this.violations === 2) {
      badge.className = 'security-status-badge danger';
      badge.style.background = '#fef2f2';
      badge.style.borderColor = '#dc2626';
      text.style.color = '#b91c1c';
      text.textContent = `🚨 FINAL WARNING: Strike 2/${this.maxViolations}`;
    } else {
      badge.className = 'security-status-badge danger';
      badge.style.background = '#7f1d1d';
      badge.style.borderColor = '#dc2626';
      text.style.color = '#ffffff';
      text.textContent = `🚨 Strike 3/${this.maxViolations}: Auto-Submitting`;
    }
  },

  showViolationModal(reason) {
    const modal = document.getElementById('security-violation-modal');
    if (!modal) return;

    modal.style.display = 'flex';
    modal.classList.add('active');

    const remaining = this.maxViolations - this.violations;
    const strikePills = [];
    for (let s = 1; s <= this.maxViolations; s++) {
      if (s <= this.violations) {
        strikePills.push(`<span style="background: #dc2626; color: #fff; padding: 4px 10px; border-radius: 6px; font-weight: 800; font-size: 0.78rem;">⚠️ STRIKE ${s} INCURRED</span>`);
      } else {
        strikePills.push(`<span style="background: #e2e8f0; color: #64748b; padding: 4px 10px; border-radius: 6px; font-weight: 700; font-size: 0.78rem;">⚪ Strike ${s} Pending</span>`);
      }
    }

    modal.innerHTML = `
      <div class="modal-card" style="max-width: 520px; width: 92%; border-radius: 16px; border: 2.5px solid #dc2626; box-shadow: 0 25px 50px -12px rgba(220, 38, 38, 0.4); overflow: hidden; text-align: center; padding: 0;">
        <div style="background: linear-gradient(135deg, #b91c1c 0%, #dc2626 100%); color: #fff; padding: 18px 20px;">
          <div style="font-size: 2.4rem; margin-bottom: 6px;">⚠️</div>
          <h3 style="margin: 0; font-size: 1.25rem; font-weight: 800; letter-spacing: -0.01em;">
            ANTI-CHEAT SECURITY WARNING: STRIKE ${this.violations} OF ${this.maxViolations}
          </h3>
          <p style="margin: 4px 0 0 0; font-size: 0.85rem; color: #fee2e2; font-weight: 600;">
            Navigation away from examination window detected
          </p>
        </div>

        <div style="padding: 22px 20px; font-size: 0.9rem; line-height: 1.55; color: #334155;">
          <p style="margin: 0 0 14px 0;">
            You navigated away from the CBT examination browser window (<strong>${reason}</strong>).
            Under NCDMB examination regulations, switching browser tabs, minimizing the window, or accessing other applications is strictly prohibited.
          </p>

          <div style="display: flex; gap: 8px; justify-content: center; margin-bottom: 16px; flex-wrap: wrap;">
            ${strikePills.join('')}
          </div>

          <div style="background: #fef2f2; border-left: 4px solid #dc2626; padding: 12px 14px; border-radius: 6px; text-align: left; margin-bottom: 18px;">
            <div style="color: #991b1b; font-weight: 800; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 2px;">
              ⚠️ Critical Rule:
            </div>
            <div style="color: #7f1d1d; font-size: 0.84rem;">
              You have <strong>${remaining} warning(s)</strong> remaining. On the <strong>3rd strike</strong>, your examination session will be <strong>IMMEDIATELY TERMINATED</strong> and automatically submitted with your current answers.
            </div>
          </div>

          <button type="button" class="btn-primary-large" style="width: 100%; padding: 12px 16px; font-size: 0.98rem; font-weight: 800; background: #00563F; border: none; border-radius: 8px; color: #fff; cursor: pointer;" onclick="proctorEngine.resumeExam()">
            <span>✅ I Acknowledge & Return to Examination</span>
          </button>
        </div>
      </div>
    `;
  },

  handleTermination(reason) {
    this.active = false;
    this.detachListeners();

    if (state.timerInterval) clearInterval(state.timerInterval);

    const modal = document.getElementById('security-violation-modal');
    if (modal) {
      modal.style.display = 'flex';
      modal.classList.add('active');

      modal.innerHTML = `
        <div class="modal-card" style="max-width: 520px; width: 92%; border-radius: 16px; border: 3px solid #7f1d1d; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.6); overflow: hidden; text-align: center; padding: 0;">
          <div style="background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 100%); color: #fff; padding: 22px 20px;">
            <div style="font-size: 2.8rem; margin-bottom: 6px;">🚨</div>
            <h3 style="margin: 0; font-size: 1.3rem; font-weight: 900; letter-spacing: -0.01em;">
              EXAMINATION TERMINATED (3 STRIKES EXCEEDED)
            </h3>
            <p style="margin: 6px 0 0 0; font-size: 0.88rem; color: #fecaca; font-weight: 600;">
              Anti-Cheat Policy Violation — Browser Navigation Lockout
            </p>
          </div>

          <div style="padding: 24px 20px; font-size: 0.92rem; line-height: 1.55; color: #334155;">
            <p style="margin: 0 0 16px 0;">
              You have repeatedly navigated away from the CBT examination window (<strong>3 strikes reached</strong>).
              In accordance with NCDMB CBT integrity guidelines, your examination has been permanently terminated.
            </p>

            <div style="background: #fef2f2; border: 1.5px solid #f87171; padding: 12px 14px; border-radius: 8px; color: #991b1b; font-weight: 700; margin-bottom: 20px;">
              ⏳ Automatically submitting and locking your examination answers now...
            </div>
          </div>
        </div>
      `;
    }

    setTimeout(() => {
      this.closeViolationModal();
      submitExam(true, 'Anti-Cheat Policy Violation: 3 Strikes Navigated Away from Browser');
    }, 2200);
  },

  resumeExam() {
    this.closeViolationModal();
    this.hideCurtain();
  },

  closeViolationModal() {
    const modal = document.getElementById('security-violation-modal');
    if (modal) {
      modal.classList.remove('active');
      modal.style.display = 'none';
      modal.innerHTML = '';
    }
  },

  hideCurtain() {
    const curtain = document.getElementById('security-curtain');
    if (curtain) {
      curtain.style.display = 'none';
      curtain.classList.remove('active');
    }
  },

  getSecurityFlags() {
    if (!this.violationLogs || this.violationLogs.length === 0) return '';
    return this.violationLogs.map(v => `[${v.time}] Strike ${v.strike}: ${v.reason}`).join('; ');
  }
};"""

# Find start and end of proctorEngine
idx_start = js.find('// PROCTORING & ANTI-CHEATING SHIELD ENGINE')
idx_end = js.find('// 2. CBT Testing Engine & Live Countdown')

if idx_start != -1 and idx_end != -1:
    js = js[:idx_start] + new_proctor_engine + "\n\n// -------------------------------------------------------------\n" + js[idx_end:]
    print("Replaced proctorEngine successfully!")
else:
    print("Could not locate proctorEngine markers")

# 5. Add toggleAntiCheatStatus and updateAdminAntiCheatUI right after updateAdminStatusUI
old_admin_status_ui = """    if (btnText) btnText.textContent = '🔒 Close CBT Examination';
  }
}"""

new_admin_status_ui = """    if (btnText) btnText.textContent = '🔒 Close CBT Examination';
  }
}

// Admin Toggle Anti-Cheat Proctor Shield
async function toggleAntiCheatStatus() {
  if (!state.adminToken) {
    openAdminLoginModal();
    return;
  }

  const btn = document.getElementById('btn-toggle-anti-cheat');
  if (btn) btn.disabled = true;

  try {
    const res = await fetch('/api/admin/toggle-anti-cheat', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${state.adminToken}`
      }
    });

    if (res.status === 401) {
      state.adminToken = null;
      sessionStorage.removeItem('kws_admin_token');
      openAdminLoginModal();
      return;
    }

    const data = await res.json();
    state.antiCheatStatus = data.anti_cheat_status;
    state.antiCheatEnabled = data.anti_cheat_enabled;
    updateAdminAntiCheatUI(data.anti_cheat_status);

    showAlertModal(
      'Anti-Cheat Status Updated',
      data.message,
      data.anti_cheat_enabled ? 'success' : 'warning'
    );
  } catch (err) {
    showAlertModal('Error', 'Failed to update anti-cheat status: ' + err.message, 'error');
  } finally {
    if (btn) btn.disabled = false;
  }
}

function updateAdminAntiCheatUI(status) {
  const icon = document.getElementById('anti-cheat-status-icon');
  const text = document.getElementById('anti-cheat-status-text');
  const btn = document.getElementById('btn-toggle-anti-cheat');
  const btnText = document.getElementById('btn-toggle-anti-cheat-text');

  const isEnabled = (status === 'enabled');
  if (icon) icon.textContent = isEnabled ? '🛡️' : '⚪';
  if (text) {
    text.style.color = isEnabled ? '#16a34a' : '#64748b';
    text.textContent = isEnabled ? 'ACTIVE (3 Strikes Auto-Submit)' : 'DISABLED (Navigation Permitted)';
  }
  if (btn) {
    btn.style.background = isEnabled ? '#dc2626' : '#16a34a';
  }
  if (btnText) {
    btnText.textContent = isEnabled ? '🔒 Turn OFF Anti-Cheat' : '🛡️ Turn ON Anti-Cheat';
  }
}"""

js = js.replace(old_admin_status_ui, new_admin_status_ui)

# 6. Update loadAdminSubmissions to update Admin Anti-Cheat UI
old_load_admin = """    updateAdminStatusUI(state.examStatus);
    applyExamStatusToUI(state.examStatus);"""

new_load_admin = """    updateAdminStatusUI(state.examStatus);
    applyExamStatusToUI(state.examStatus);
    state.antiCheatStatus = data.anti_cheat_status || 'enabled';
    state.antiCheatEnabled = (data.anti_cheat_enabled !== false);
    updateAdminAntiCheatUI(state.antiCheatStatus);"""

js = js.replace(old_load_admin, new_load_admin)

# 7. Update submitExam to send proctor violations and security flags
old_submit_payload = """    violations_count: 0,
    security_flags: ''"""

new_submit_payload = """    violations_count: (typeof proctorEngine !== 'undefined' ? proctorEngine.violations : 0),
    security_flags: (typeof proctorEngine !== 'undefined' ? proctorEngine.getSecurityFlags() : '')"""

js = js.replace(old_submit_payload, new_submit_payload)

with open(r'C:\Users\hp\Desktop\NCMB\static\js\cbt.js', 'w', encoding='utf-8') as f:
    f.write(js)

print("cbt.js updated successfully with Anti-Cheat 3-strikes auto-submit and backend toggle!")
