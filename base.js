/**
 * base.js — Shared foundation for all Averion pages
 * Auth · Navigation · Utilities · API connection
 */

// ── API CONNECTION ──
const API = window.location.hostname === 'localhost' 
    ? 'http://localhost:8080' 
    : 'https://averionbot.com';

// ── AUTH ──
function getToken() {
    return localStorage.getItem('averion_token');
}

function authHeaders() {
    return {
        'Authorization': `Bearer ${getToken()}`,
        'Content-Type': 'application/json'
    };
}

function requireAuth() {
    const token = getToken();
    if (!token) {
        window.location.href = '/login';
        return false;
    }
    return true;
}

function logout() {
    localStorage.removeItem('averion_token');
    localStorage.removeItem('averion_user');
    window.location.href = '/login';
}

function getUser() {
    try {
        return JSON.parse(localStorage.getItem('averion_user') || '{}');
    } catch {
        return {};
    }
}

// ── NAVIGATION ──
const NAV_ITEMS = [
    { icon: '🏠', label: 'Dashboard', url: '/dashboard' },
    { icon: '🤖', label: 'Bots', url: '/bots' },
    { icon: '📊', label: 'Trades', url: '/trades' },
    { icon: '📜', label: 'History', url: '/history' },
    { icon: '🔗', label: 'Exchanges', url: '/exchanges' },
    { icon: '📈', label: 'Reports', url: '/reports' },
    { icon: '⚙️', label: 'Settings', url: '/settings' },
    { icon: '+', label: 'Create Bot', url: '/create-bot' },
];

function buildNav() {
    const currentPath = window.location.pathname;
    const nav = document.getElementById('sidebar-nav');
    if (!nav) return;

    nav.innerHTML = NAV_ITEMS.filter(item => item.url !== currentPath).map(item => `
        <a href="${item.url}" class="nav-link" style="text-decoration:none!important;color:inherit">
            <span class="nav-icon">${item.icon}</span>
            <span>${item.label}</span>
        </a>
    `).join('');

    // Create Bot button
    nav.innerHTML += `
        <div style="padding:8px 0;margin-top:auto">
            <a href="/create-bot" class="nav-link" style="background:linear-gradient(135deg,#6366F1,#4F46E5);color:#fff;border-color:transparent;justify-content:center;font-weight:600;margin-top:8px">
                <span>+</span>
                <span>Create Bot</span>
            </a>
        </div>
    `;
}

function buildUserRow() {
    const user = getUser();
    const el = document.getElementById('user-row');
    if (!el) return;
    const initial = (user.email || 'U')[0].toUpperCase();
    el.innerHTML = `
        <div class="user-avatar">${initial}</div>
        <div>
            <div class="user-name">${user.email || 'User'}</div>
            <div class="user-plan">${user.plan || 'Free'}</div>
        </div>
    `;
}

function buildMobileNav() {
    const currentPath = window.location.pathname;
    const bnav = document.getElementById('bottom-nav');
    if (!bnav) return;

    const allItems = [
        { icon: '🏠', label: 'Home', url: '/dashboard' },
        { icon: '🤖', label: 'Bots', url: '/bots' },
        { icon: '📊', label: 'Trades', url: '/trades' },
        { icon: '📜', label: 'History', url: '/history' },
        { icon: '📈', label: 'Reports', url: '/reports' },
        { icon: '⚙️', label: 'Settings', url: '/settings' },
    ];
    const mobileItems = allItems.filter(i => i.url !== currentPath);

    bnav.innerHTML = mobileItems.map(item => `
        <a href="${item.url}" class="bnav-item" style="text-decoration:none!important">
            <span class="bnav-icon">${item.icon}</span>
            <span class="bnav-label">${item.label}</span>
        </a>
    `).join('');
}

// ── UTILITIES ──
// ── Get user timezone (auto from browser, overridable from settings) ──
function getUserTimezone() {
    return localStorage.getItem('averion_timezone') || 
           Intl.DateTimeFormat().resolvedOptions().timeZone;
}

function fmtPrice(p) {
    if (p === null || p === undefined || p === '') return '$0';
    const n = parseFloat(p);
    if (isNaN(n)) return '$0';
    const sign = n < 0 ? '-' : '';
    const abs = Math.abs(n);
    if (abs >= 1000) return sign + '$' + abs.toLocaleString('en-US', {maximumFractionDigits: 2});
    if (abs >= 1) return sign + '$' + abs.toFixed(4);
    if (abs >= 0.001) return sign + '$' + abs.toFixed(6);
    return sign + '$' + abs.toFixed(8);
}

function fmtPnl(n) {
    if (n === null || n === undefined) return '$0.00';
    const val = parseFloat(n);
    if (isNaN(val)) return '$0.00';
    const sign = val >= 0 ? '+' : '-';
    return sign + '$' + Math.abs(val).toFixed(2);
}

function fmtPct(n) {
    if (n === null || n === undefined) return '0.00%';
    const val = parseFloat(n);
    if (isNaN(val)) return '0.00%';
    const sign = val >= 0 ? '+' : '-';
    return sign + Math.abs(val).toFixed(2) + '%';
}

function parseUTC(utcStr) {
    if (!utcStr || utcStr === 'None' || utcStr === 'null') return null;
    // Ensure UTC parsing - add Z if missing
    const s = utcStr.toString().trim();
    if (s.endsWith('Z') || s.includes('+') || s.match(/[+-]\d{2}:\d{2}$/)) {
        return new Date(s);
    }
    return new Date(s + 'Z'); // treat as UTC
}

function is12h() {
    return localStorage.getItem('averion_time_format') === '12h';
}

function fmtLocal(utcStr) {
    if (!utcStr || utcStr === 'None' || utcStr === 'null') return '—';
    try {
        return parseUTC(utcStr).toLocaleString('en-US', {
            timeZone: getUserTimezone(),
            year: 'numeric', month: 'short', day: 'numeric',
            hour: '2-digit', minute: '2-digit', second: '2-digit',
            hour12: is12h()
        });
    } catch(e) { return utcStr; }
}

function fmtDate(utcStr) {
    if (!utcStr || utcStr === 'None' || utcStr === 'null') return '—';
    try {
        return parseUTC(utcStr).toLocaleString('en-US', {
            timeZone: getUserTimezone(),
            year: 'numeric', month: 'short', day: 'numeric',
            hour: '2-digit', minute: '2-digit',
            hour12: is12h()
        });
    } catch(e) { return utcStr; }
}

function fmtTime(utcStr) {
    if (!utcStr || utcStr === 'None' || utcStr === 'null') return '—';
    try {
        return parseUTC(utcStr).toLocaleString('en-US', {
            timeZone: getUserTimezone(),
            hour: '2-digit', minute: '2-digit', second: '2-digit',
            hour12: is12h()
        });
    } catch(e) { return utcStr; }
}

function fmtAgo(utcStr) {
    if (!utcStr || utcStr === 'None' || utcStr === 'null') return '—';
    const diff = Date.now() - parseUTC(utcStr).getTime();
    const h = Math.floor(diff / 3600000);
    const m = Math.floor((diff % 3600000) / 60000);
    const s = Math.floor((diff % 60000) / 1000);
    if (h > 24) return `${Math.floor(h/24)}d ago`;
    if (h > 0) return `${h}h ${m}m ago`;
    if (m > 0) return `${m}m ${s}s ago`;
    return `${s}s ago`;
}

// ── SIDEBAR HTML TEMPLATE ──
function getSidebarHTML(pageTitle = '') {
    return `
    <div class="sidebar">
        <div class="sidebar-logo">
            <div class="logo-mark">A</div>
            <div class="logo-text">AVERION</div>
            <div class="logo-badge">BETA</div>
        </div>
        <nav class="sidebar-nav" id="sidebar-nav"></nav>
        <div class="sidebar-footer">
            <div class="user-row" id="user-row" onclick="logout()"></div>
        </div>
    </div>`;
}

function getTopbarHTML(pageTitle = '') {
    return `
    <div class="topbar">
        <div class="topbar-left">
            <div class="page-title">${pageTitle}</div>
        </div>
        <div class="topbar-right">
            <div class="ws-dot" id="ws-dot" style="width:8px;height:8px;border-radius:50%;background:var(--green);display:inline-block"></div>
        </div>
    </div>`;
}

function getMobileNavHTML() {
    return `<div class="bottom-nav" id="bottom-nav"></div>`;
}

// ── INIT (call on every page) ──
function initPage(pageTitle = '') {
    if (!requireAuth()) return;
    buildNav();
    buildUserRow();
    buildMobileNav();
}
