const API = window.location.origin;
const ADMIN_BASE = '/admin';

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
  { name: 'Health & Control', path: '/admin/page/health' },
  { name: 'Users', path: '/admin/page/users' },
  { name: 'Research Lab', path: '/admin/page/research' },
  { name: 'Trading Intelligence', path: '/admin/page/champions' },
  { name: 'System Control', path: '/admin/page/system' },
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
  if (!confirm('Stop ALL trading immediately?')) return;
  alert('Emergency stop - wiring pending');
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
