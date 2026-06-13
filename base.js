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

    nav.innerHTML = NAV_ITEMS.map(item => `
        <a href="${item.url}" class="nav-link ${currentPath === item.url ? 'active' : ''}" style="text-decoration:none!important;color:inherit">
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

    const mobileItems = [
        { icon: '🏠', label: 'Home', url: '/dashboard' },
        { icon: '🤖', label: 'Bots', url: '/bots' },
        { icon: '📊', label: 'Trades', url: '/trades' },
        { icon: '📜', label: 'History', url: '/history' },
        { icon: '⚙️', label: 'More', url: '/settings' },
    ];

    bnav.innerHTML = mobileItems.map(item => `
        <a href="${item.url}" class="bnav-item ${currentPath === item.url ? 'active' : ''}" style="text-decoration:none!important">
            <span class="bnav-icon">${item.icon}</span>
            <span class="bnav-label">${item.label}</span>
        </a>
    `).join('');
}

// ── UTILITIES ──
function fmtPrice(p) {
    if (!p || p == 0) return '$0';
    const n = parseFloat(p);
    if (n >= 1000) return '$' + n.toLocaleString('en', {maximumFractionDigits: 2});
    if (n >= 1) return '$' + n.toFixed(4);
    if (n >= 0.001) return '$' + n.toFixed(6);
    return '$' + n.toFixed(8);
}

function fmtLocal(utcStr) {
    if (!utcStr) return '—';
    return new Date(utcStr).toLocaleString();
}

function fmtAgo(utcStr) {
    if (!utcStr) return '—';
    const diff = Date.now() - new Date(utcStr).getTime();
    const h = Math.floor(diff / 3600000);
    const m = Math.floor((diff % 3600000) / 60000);
    if (h > 24) return `${Math.floor(h/24)}d ago`;
    if (h > 0) return `${h}h ${m}m ago`;
    return `${m}m ago`;
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
