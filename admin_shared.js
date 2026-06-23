const API = window.location.origin;
const ADMIN_BASE = '/admins';

function getAdminToken() { return localStorage.getItem('admin_session_token'); }
function getLoginToken() { return localStorage.getItem('averion_token'); }
function authHeaders() { return { 'Authorization': `Bearer ${getLoginToken()}` }; }

// Every content page (not the gate page itself) calls this first.
// Redirects to the gate if there's no valid admin session.
function requireAdminSession() {
  if (!getAdminToken()) {
    window.location.href = ADMIN_BASE;
    return false;
  }
  return true;
}

const TABS = [
  { name: 'Health & Control', path: '/admins/health' },
  { name: 'Users', path: '/admins/users' },
  { name: 'Research Lab', path: '/admins/research' },
  { name: 'Trading Intelligence', path: '/admins/champions' },
  { name: 'System Control', path: '/admins/system' },
];

function renderHeaderAndTabs() {
  const headerHtml = `
    <div class="header">
      <div class="header-left">
        <div class="logo">AVERION</div>
        <div class="status-pill">
          <div class="status-dot" id="status-dot"></div>
          <span id="status-text">Loading...</span>
        </div>
      </div>
      <div class="menu-wrap">
        <button class="menu-btn" onclick="toggleMenu()">⋮</button>
        <div class="menu-dropdown" id="menu-dropdown">
          <div class="menu-item" onclick="restartBot()">🔄 Restart Bot</div>
          <div class="menu-item danger" onclick="emergencyStop()">🔴 Stop All Trading</div>
          <div class="menu-item" onclick="logout()">🚪 Sign Out</div>
        </div>
      </div>
    </div>
    <div class="tabnav">
      ${TABS.map(t => `<div class="tab ${window.location.pathname === t.path ? 'active' : ''}"
        onclick="window.location.href='${t.path}'">${t.name}</div>`).join('')}
    </div>
  `;
  document.getElementById('app-shell').insertAdjacentHTML('afterbegin', headerHtml);
  updateStatusPill();
  setInterval(updateStatusPill, 10000);
}

// MOVED June 22 2026: this previously only lived inside admin_health.html's
// own page-specific script, so the status pill in the shared header
// showed "Loading..." forever on every OTHER admin tab. Now part of
// the shared render function, so it works identically everywhere.
async function updateStatusPill() {
  try {
    const res = await fetch(`${API}/status`, { headers: authHeaders() });
    const sdata = await res.json();
    const statusText = document.getElementById('status-text');
    const statusDot = document.getElementById('status-dot');
    if (statusText) {
      statusText.textContent = sdata.running
        ? `BOT RUNNING · ${sdata.cycle_time || '—'}s`
        : 'BOT STOPPED';
    }
    if (statusDot) {
      statusDot.style.background = sdata.running ? 'var(--green)' : 'var(--red)';
    }
  } catch (e) {
    console.error('Status pill update failed', e);
  }
}

function toggleMenu() {
  document.getElementById('menu-dropdown').classList.toggle('open');
}
document.addEventListener('click', (e) => {
  const dropdown = document.getElementById('menu-dropdown');
  if (dropdown && !e.target.closest('.menu-wrap')) {
    dropdown.classList.remove('open');
  }
});

function logout() {
  localStorage.removeItem('admin_session_token');
  localStorage.removeItem('averion_token');
  window.location.href = '/login';
}

async function restartBot() {
  if (!confirm('Restart the trading engine?')) return;
  try {
    await fetch(`${API}/admin/bot/restart`, { method: 'POST', headers: authHeaders() });
    alert('Restart triggered');
  } catch (e) { alert('Failed: ' + e.message); }
}
async function emergencyStop() {
  // WIRED June 23 2026 - was a placeholder showing "wiring pending"
  // forever, found while reviewing what's still incomplete in Health
  // and Controls. Now calls the same emergency_halt setting Tab 5's
  // Trade Control section uses, so this quicker dropdown shortcut
  // genuinely works too, not just the full Tab 5 toggle.
  if (!confirm('Stop ALL new trading immediately? Existing open trades will keep running their own DCA/TP/trailing/buyback normally - this only blocks new entries platform-wide.')) return;
  try {
    await fetch(`${API}/admin/settings`, {
      method: 'POST',
      headers: { ...authHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ emergency_halt: 'true' })
    });
    alert('Emergency stop activated. New trades are now blocked platform-wide. Release it from System Control when ready.');
  } catch (e) {
    alert('Failed to activate emergency stop: ' + e.message);
  }
}

// Single source of truth for timezone display - respects the user's
// explicit preference set in Settings (localStorage 'averion_timezone'),
// falling back to browser auto-detection if none is set. Both timestamp
// formatting and schedule-time labels use this same function, so
// changing the setting in one place updates everything consistently.
function getEffectiveTimezone() {
  const saved = (localStorage.getItem('averion_timezone') || '').trim();
  return saved || undefined; // undefined = browser default in Intl APIs
}

function fmtLocal(utcStr) {
  if (!utcStr) return '—';
  const d = new Date(utcStr.replace(' ', 'T') + 'Z');
  const tz = getEffectiveTimezone();
  return tz ? d.toLocaleString('en-US', { timeZone: tz }) : d.toLocaleString();
}

function utcHourMinToLocal(utcTimeStr) {
  // utcTimeStr like '03:00' - returns the equivalent time in the
  // user's effective timezone (saved preference or browser default)
  const [h, m] = utcTimeStr.split(':').map(Number);
  const now = new Date();
  const utcDate = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate(), h, m));
  const tz = getEffectiveTimezone();
  if (tz) {
    return utcDate.toLocaleTimeString('en-US', { timeZone: tz, hour: '2-digit', minute: '2-digit', hour12: false });
  }
  return utcDate.getHours().toString().padStart(2,'0') + ':' +
         utcDate.getMinutes().toString().padStart(2,'0');
}

// Re-check session on mobile back/forward cache restores
window.addEventListener('pageshow', () => {
  if (!getAdminToken()) window.location.href = ADMIN_BASE;
});
