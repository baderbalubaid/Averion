import sys

HTML = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Averion</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{
  --bg:#070711;--bg2:#0E0E1C;--bg3:#141428;
  --border:#1E1E35;--border2:#252540;
  --accent:#6366F1;--accent2:#4F46E5;
  --green:#10D98A;--red:#F4645F;--amber:#F59E0B;--blue:#38BDF8;--purple:#A78BFA;
  --text:#F0F0FF;--text2:#8888AA;--text3:#55556A;
}

body{font-family:'Inter',system-ui,sans-serif;background:var(--bg);color:var(--text);min-height:100vh;display:flex;overflow:hidden}

/* SIDEBAR */
.sidebar{width:220px;background:var(--bg2);border-right:1px solid var(--border);display:flex;flex-direction:column;flex-shrink:0;height:100vh}
.sidebar-logo{padding:18px 18px 14px;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:10px}
.logo-mark{width:32px;height:32px;background:linear-gradient(135deg,#6366F1,#8B5CF6);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:900;color:#fff;flex-shrink:0}
.logo-text{font-size:14px;font-weight:800;letter-spacing:2px}
.logo-badge{font-size:8px;background:var(--accent);color:#fff;padding:2px 6px;border-radius:4px;font-weight:700;margin-left:auto}
.sidebar-nav{padding:10px 8px;flex:1;display:flex;flex-direction:column;gap:2px;overflow-y:auto}
.nav-section-lbl{font-size:9px;color:var(--text3);text-transform:uppercase;letter-spacing:1.5px;padding:8px 10px 4px;font-weight:600}
.nav-link{display:flex;align-items:center;gap:10px;padding:9px 10px;border-radius:8px;color:var(--text2);cursor:pointer;transition:all 0.15s;font-size:13px;font-weight:500;border:1px solid transparent}
.nav-link:hover{background:var(--bg3);color:var(--text)}
.nav-link.active{background:linear-gradient(135deg,#6366F115,#6366F108);color:var(--accent);border-color:#6366F118}
.nav-icon{font-size:16px;width:20px;text-align:center}
.nav-badge{margin-left:auto;background:var(--accent);color:#fff;font-size:9px;font-weight:700;padding:2px 6px;border-radius:20px;min-width:18px;text-align:center}
.sidebar-footer{padding:10px 8px;border-top:1px solid var(--border)}
.user-row{display:flex;align-items:center;gap:10px;padding:8px 10px;border-radius:8px;cursor:pointer;transition:background 0.15s}
.user-row:hover{background:var(--bg3)}
.user-avatar{width:30px;height:30px;border-radius:8px;background:linear-gradient(135deg,#6366F1,#8B5CF6);display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:#fff;flex-shrink:0}
.user-name{font-size:12px;font-weight:600}
.user-plan{font-size:10px;color:var(--text3)}

/* MAIN */
.main{flex:1;display:flex;flex-direction:column;overflow:hidden;height:100vh}

/* TOPBAR */
.topbar{height:56px;background:var(--bg2);border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;padding:0 24px;flex-shrink:0}
.topbar-left{display:flex;align-items:center;gap:12px}
.page-title{font-size:15px;font-weight:700}
.topbar-right{display:flex;align-items:center;gap:10px}
.live-ticker{display:flex;align-items:center;gap:6px;background:var(--bg3);border:1px solid var(--border2);border-radius:8px;padding:6px 12px}
.ticker-dot{width:6px;height:6px;border-radius:50%;background:var(--green);animation:blink 2s infinite}
@keyframes blink{0%,100%{opacity:1}50%{opacity:0.3}}
.ticker-lbl{font-size:10px;color:var(--text3);font-weight:600}
.ticker-price{font-size:13px;font-weight:700}
.icon-btn{width:34px;height:34px;background:var(--bg3);border:1px solid var(--border);border-radius:8px;display:flex;align-items:center;justify-content:center;cursor:pointer;font-size:14px;transition:border-color 0.15s;position:relative}
.icon-btn:hover{border-color:var(--accent)}
.notif-dot{position:absolute;top:6px;right:6px;width:6px;height:6px;background:var(--red);border-radius:50%;border:1.5px solid var(--bg2)}
.paper-chip{background:#F59E0B12;border:1px solid #F59E0B28;border-radius:6px;padding:4px 10px;font-size:10px;font-weight:700;color:var(--amber);letter-spacing:0.5px}

/* PAGE */
.page{flex:1;overflow-y:auto;padding:24px}
.page::-webkit-scrollbar{width:4px}
.page::-webkit-scrollbar-thumb{background:var(--border2);border-radius:4px}

/* TABS */
.tab-content{display:none}
.tab-content.active{display:block}

/* BOTTOM NAV */
.bottom-nav{display:none;position:fixed;bottom:0;left:0;right:0;background:var(--bg2);border-top:1px solid var(--border);justify-content:space-around;padding:8px 0;padding-bottom:calc(8px + env(safe-area-inset-bottom));z-index:100}
.bnav-item{display:flex;flex-direction:column;align-items:center;gap:3px;color:var(--text3);font-size:10px;cursor:pointer;padding:4px 16px;transition:color 0.2s;border:none;background:none;font-family:'Inter',sans-serif}
.bnav-item.active{color:var(--accent)}
.bnav-icon{font-size:20px}

/* HERO STATS */
.hero-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:24px}
.hero-card{background:var(--bg2);border:1px solid var(--border);border-radius:16px;padding:20px;position:relative;overflow:hidden;transition:border-color 0.2s,transform 0.2s}
.hero-card:hover{border-color:var(--border2);transform:translateY(-1px)}
.hero-card::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,var(--line-color,#6366F1),transparent);opacity:0.7}
.hero-card.g{--line-color:#10D98A}.hero-card.b{--line-color:#38BDF8}.hero-card.a{--line-color:#F59E0B}
.hero-lbl{font-size:11px;color:var(--text3);font-weight:600;text-transform:uppercase;letter-spacing:1px;margin-bottom:10px}
.hero-val{font-size:26px;font-weight:800;line-height:1;letter-spacing:-0.5px;margin-bottom:6px}
.hero-sub{font-size:11px;color:var(--text3)}
.hero-icon{position:absolute;top:16px;right:16px;font-size:22px;opacity:0.12}

/* FEES BANNER */
.fees-banner{background:#F59E0B08;border:1px solid #F59E0B25;border-radius:12px;padding:12px 16px;display:flex;align-items:center;justify-content:space-between;margin-bottom:20px}
.fees-info-lbl{font-size:11px;color:var(--amber);font-weight:700}
.fees-info-desc{font-size:10px;color:var(--text3);margin-top:2px}
.fees-amount{font-size:18px;font-weight:800;color:var(--amber);margin:0 12px}

/* SECTION HEADER */
.sec-hdr{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px}
.sec-title{font-size:14px;font-weight:700}
.sec-sub{font-size:11px;color:var(--text3);margin-top:2px}

/* BUTTONS */
.btn{padding:8px 16px;border-radius:9px;border:none;font-size:12px;font-weight:600;cursor:pointer;font-family:'Inter',sans-serif;transition:opacity 0.15s,transform 0.1s;display:inline-flex;align-items:center;gap:6px}
.btn:active{opacity:0.8;transform:scale(0.98)}
.btn-accent{background:var(--accent);color:#fff}
.btn-green{background:var(--green);color:#09090F}
.btn-red{background:var(--red);color:#fff}
.btn-ghost{background:var(--bg3);color:var(--text2);border:1px solid var(--border)}
.btn-sm{padding:6px 12px;font-size:11px}
.btn-xs{padding:4px 9px;font-size:9px;border-radius:6px;border:none;font-weight:700;cursor:pointer;font-family:'Inter',sans-serif}
.btn-xs-stop{background:#F4645F15;color:var(--red);border:1px solid #F4645F25}
.btn-xs-start{background:#10D98A15;color:var(--green);border:1px solid #10D98A25}

/* EXCHANGE CARDS */
.exc-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin-bottom:24px}
.exc-card{background:var(--bg2);border:1px solid var(--border);border-radius:16px;overflow:hidden;transition:border-color 0.2s,transform 0.2s;cursor:pointer}
.exc-card:hover{border-color:var(--border2);transform:translateY(-1px)}
.exc-top{padding:16px 18px;display:flex;align-items:flex-start;gap:12px}
.exc-logo{width:38px;height:38px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:15px;font-weight:900;flex-shrink:0}
.exc-info{flex:1}
.exc-name{font-size:14px;font-weight:700;margin-bottom:3px}
.exc-sub{font-size:11px;color:var(--text3);display:flex;align-items:center;gap:6px}
.exc-dot{width:5px;height:5px;border-radius:50%;background:var(--green)}
.exc-right{display:flex;gap:10px;align-items:flex-start}
.exc-val-wrap{text-align:right}
.exc-amount{font-size:15px;font-weight:800}
.exc-pnl{font-size:11px;font-weight:600;margin-top:2px}
.exc-menu-btn{width:28px;height:28px;background:var(--bg3);border:1px solid var(--border);border-radius:7px;display:flex;align-items:center;justify-content:center;font-size:13px;cursor:pointer;color:var(--text2);transition:all 0.15s;flex-shrink:0}
.exc-menu-btn:hover{border-color:var(--accent);color:var(--accent)}
.exc-stats{padding:0 18px 14px;display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.exc-stat{background:var(--bg3);border-radius:9px;padding:9px 11px}
.exc-stat-lbl{font-size:9px;color:var(--text3);font-weight:600;text-transform:uppercase;letter-spacing:0.5px}
.exc-stat-val{font-size:13px;font-weight:700;margin-top:3px}
.exc-footer{padding:8px 18px 12px;border-top:1px solid var(--border);display:flex;gap:5px;flex-wrap:wrap;align-items:center}
.coin-tag{background:var(--bg3);border-radius:5px;padding:3px 7px;font-size:10px;color:var(--text3);font-weight:500}
.coin-more{font-size:10px;color:var(--accent);font-weight:600;margin-left:2px}
.exc-add{background:var(--bg2);border:1px dashed var(--border2);border-radius:16px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px;cursor:pointer;transition:all 0.2s;min-height:160px}
.exc-add:hover{border-color:var(--accent);background:#6366F108}
.exc-add-icon{font-size:24px;opacity:0.3}
.exc-add-text{font-size:12px;color:var(--text3);font-weight:500}

/* DROPDOWN */
.dropdown{position:relative}
.dropdown-menu{position:absolute;right:0;top:calc(100% + 6px);background:var(--bg2);border:1px solid var(--border2);border-radius:10px;overflow:hidden;min-width:170px;z-index:100;box-shadow:0 8px 32px #00000080;display:none}
.dropdown-menu.open{display:block}
.dropdown-item{padding:10px 14px;font-size:12px;font-weight:500;color:var(--text2);cursor:pointer;display:flex;align-items:center;gap:9px;transition:background 0.1s;border-bottom:1px solid var(--border)}
.dropdown-item:last-child{border-bottom:none}
.dropdown-item:hover{background:var(--bg3);color:var(--text)}
.dropdown-item.danger{color:var(--red)}
.dropdown-item.danger:hover{background:#F4645F10}

/* MODAL */
.modal-overlay{position:fixed;inset:0;background:#000000CC;z-index:200;display:none;align-items:center;justify-content:center;padding:20px}
.modal-overlay.open{display:flex}
.modal{background:var(--bg2);border:1px solid var(--border2);border-radius:16px;width:100%;max-width:420px;overflow:hidden;max-height:90vh;overflow-y:auto}
.modal-hdr{background:var(--bg3);padding:14px 18px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--border);position:sticky;top:0}
.modal-title{font-size:14px;font-weight:700}
.modal-close{background:none;border:none;color:var(--text3);font-size:18px;cursor:pointer;line-height:1;padding:2px 6px;border-radius:5px}
.modal-close:hover{background:var(--bg);color:var(--text)}
.modal-body{padding:18px}
.form-group{margin-bottom:14px}
.form-label{font-size:11px;color:var(--text2);margin-bottom:6px;display:block;font-weight:600;text-transform:uppercase;letter-spacing:0.5px}
.form-input,.form-select{width:100%;padding:10px 13px;background:var(--bg);border:1px solid var(--border2);border-radius:9px;color:var(--text);font-size:13px;font-family:'Inter',sans-serif;outline:none;transition:border-color 0.2s}
.form-input:focus,.form-select:focus{border-color:var(--accent)}
.form-input::placeholder{color:var(--text3)}
.form-hint{margin-top:12px;padding:10px 13px;background:#38BDF808;border:1px solid #38BDF820;border-radius:8px;font-size:10px;color:#38BDF8;line-height:1.5}
.modal-footer{padding:0 18px 18px;display:flex;gap:8px}

/* ── BOTS FLAT LIST (Item 24) ── */
.bot-flat-row{display:flex;align-items:center;padding:13px 16px;border-bottom:1px solid var(--border);cursor:pointer;transition:background 0.15s;gap:12px}
.bot-flat-row:last-child{border-bottom:none}
.bot-flat-row:hover{background:#6366F106}
.exc-badge{display:inline-flex;align-items:center;justify-content:center;width:26px;height:26px;border-radius:7px;font-size:11px;font-weight:900;flex-shrink:0}
.bot-flat-name{font-size:13px;font-weight:700;margin-bottom:3px}
.bot-flat-meta{font-size:10px;color:var(--text3)}
.bot-flat-meta span{color:var(--text2)}
.bot-toggle-wrap{display:flex;flex-direction:column;align-items:center;gap:3px;flex-shrink:0}
.toggle-lbl{font-size:9px;color:var(--text3);font-weight:700;text-transform:uppercase;letter-spacing:0.5px}
.toggle-mini{width:34px;height:19px;border-radius:10px;border:none;cursor:pointer;position:relative;transition:background 0.2s;flex-shrink:0}
.toggle-mini-thumb{width:13px;height:13px;background:#fff;border-radius:50%;position:absolute;top:3px;transition:left 0.2s}
.kebab-btn{width:28px;height:28px;background:var(--bg3);border:1px solid var(--border);border-radius:7px;display:flex;align-items:center;justify-content:center;font-size:15px;cursor:pointer;color:var(--text2);transition:all 0.15s;flex-shrink:0;line-height:1}
.kebab-btn:hover{border-color:var(--accent);color:var(--accent)}
.bot-status-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
.bot-status-dot.on{background:var(--green);box-shadow:0 0 6px #10D98A60}
.bot-status-dot.off{background:var(--text3)}

/* BOT DETAIL (L2) */
.bot-section{background:var(--bg2);border:1px solid var(--border);border-radius:16px;overflow:hidden}
.bot-section-hdr{padding:14px 18px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--border);background:var(--bg3)}
.bot-exc-left{display:flex;align-items:center;gap:10px}
.bot-exc-logo{width:28px;height:28px;border-radius:7px;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:900;flex-shrink:0}
.bot-exc-name{font-size:13px;font-weight:700}
.bot-exc-sub{font-size:10px;color:var(--text3);margin-top:1px}
.bot-exc-stats{display:flex;gap:16px;text-align:right}
.bot-exc-stat-lbl{font-size:9px;color:var(--text3)}
.bot-exc-stat-val{font-size:12px;font-weight:700}
.bot-cards-list{display:flex;flex-direction:column}
.bot-row{padding:12px 18px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--border);cursor:pointer;transition:background 0.15s}
.bot-row:last-of-type{border-bottom:none}
.bot-row:hover{background:#6366F106}
.bot-row-left{display:flex;align-items:center;gap:10px;flex:1}
.bot-indicator{width:8px;height:8px;border-radius:50%;flex-shrink:0}
.bot-indicator.live{background:var(--green);box-shadow:0 0 8px #10D98A50}
.bot-indicator.off{background:var(--text3)}
.bot-row-info{flex:1}
.bot-row-name{font-size:12px;font-weight:700;margin-bottom:4px}
.bot-row-meta{display:flex;gap:12px;flex-wrap:wrap}
.bot-meta{font-size:10px;color:var(--text3)}
.bot-meta span{color:var(--text2)}
.bot-row-right{display:flex;align-items:center;gap:8px}
.bot-arrow{color:var(--border2);font-size:14px}

/* BOT DETAIL HEADER */
.bot-detail-hdr{background:var(--accent2);padding:13px 18px;display:flex;align-items:center;justify-content:space-between}
.bot-detail-back{color:#C7D2FE;font-size:12px;cursor:pointer;display:flex;align-items:center;gap:4px;font-weight:500}
.bot-detail-back:hover{color:#fff}
.bot-detail-title{font-size:13px;font-weight:800}
.bot-detail-badge{background:#10D98A20;color:var(--green);font-size:9px;font-weight:700;padding:4px 10px;border-radius:20px;border:1px solid #10D98A30}
.bot-detail-badge.off{background:#55556A20;color:var(--text3);border-color:#55556A30}
.stats4{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;padding:14px}
.stat4{background:var(--bg3);border-radius:10px;padding:10px 12px}
.stat4-lbl{font-size:9px;color:var(--text3);text-transform:uppercase;letter-spacing:0.5px}
.stat4-val{font-size:14px;font-weight:800;margin-top:4px}

/* FILTER BAR */
.filter-bar{display:flex;gap:6px;padding:0 14px 12px;overflow-x:auto;scrollbar-width:none}
.filter-bar::-webkit-scrollbar{display:none}
.f-btn{padding:5px 13px;border-radius:20px;border:1px solid var(--border);background:var(--bg3);color:var(--text3);font-size:11px;font-weight:600;cursor:pointer;white-space:nowrap;transition:all 0.15s;font-family:'Inter',sans-serif}
.f-btn:hover{border-color:var(--border2);color:var(--text2)}
.f-btn.active{background:var(--accent);color:#fff;border-color:var(--accent)}

/* SEARCH */
.search-wrap{padding:0 14px 10px}
.search-input{width:100%;padding:9px 14px;background:var(--bg3);border:1px solid var(--border);border-radius:9px;color:var(--text);font-size:12px;font-family:'Inter',sans-serif;outline:none;transition:border-color 0.2s}
.search-input:focus{border-color:var(--accent)}
.search-input::placeholder{color:var(--text3)}

/* TABLE */
.tbl-container{background:var(--bg2);border:1px solid var(--border);border-radius:16px;overflow:hidden;margin:0 14px 14px}
.tbl-hdr{padding:12px 16px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--border)}
.tbl-title{font-size:13px;font-weight:700}
.tbl-count{font-size:11px;color:var(--text3)}
table{width:100%;border-collapse:collapse}
thead{background:var(--bg3)}
th{padding:10px 13px;font-size:9px;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:0.8px;text-align:left;cursor:pointer;white-space:nowrap;border-bottom:1px solid var(--border)}
th:hover{color:var(--text2)}
td{padding:11px 13px;font-size:12px;border-bottom:1px solid var(--border);color:var(--text);white-space:nowrap}
tr:last-child td{border-bottom:none}
tr:hover td{background:#6366F106}
.td-coin{font-weight:700;display:flex;align-items:center;gap:7px}
.td-muted{color:var(--text3);font-size:11px}

/* BADGES */
.badge{padding:3px 9px;border-radius:20px;font-size:9px;font-weight:700;display:inline-block}
.badge-active{background:#10D98A12;color:var(--green);border:1px solid #10D98A22}
.badge-stuck{background:#F59E0B12;color:var(--amber);border:1px solid #F59E0B22}
.badge-critical{background:#F4645F12;color:var(--red);border:1px solid #F4645F22}
.badge-queued{background:#38BDF812;color:var(--blue);border:1px solid #38BDF822}
.badge-tp{background:#A78BFA12;color:var(--purple);border:1px solid #A78BFA22}
.badge-closed{background:#55556A12;color:var(--text3);border:1px solid #55556A22}

/* HISTORY FILTERS */
.hist-filters{display:flex;gap:8px;margin-bottom:16px;flex-wrap:wrap;align-items:center}
.filter-sel{padding:7px 12px;background:var(--bg2);border:1px solid var(--border);border-radius:8px;color:var(--text2);font-size:12px;font-family:'Inter',sans-serif;outline:none;cursor:pointer}
.filter-sel:focus{border-color:var(--accent)}
.date-presets{display:flex;gap:5px;flex-wrap:wrap}
.date-preset{padding:6px 12px;background:var(--bg2);border:1px solid var(--border);border-radius:8px;color:var(--text3);font-size:11px;font-weight:600;cursor:pointer;transition:all 0.15s;font-family:'Inter',sans-serif}
.date-preset:hover,.date-preset.active{background:var(--accent);border-color:var(--accent);color:#fff}
.date-input{padding:6px 10px;background:var(--bg2);border:1px solid var(--border);border-radius:8px;color:var(--text2);font-size:11px;font-family:'Inter',sans-serif;outline:none;cursor:pointer;transition:border-color 0.2s}
.date-input:focus{border-color:var(--accent)}
.date-range-wrap{display:flex;align-items:center;gap:6px;flex-wrap:wrap}
.date-range-lbl{font-size:10px;color:var(--text3);font-weight:600}
.col-btn{margin-left:auto;padding:7px 14px;background:var(--bg2);border:1px solid var(--border);border-radius:8px;color:var(--text2);font-size:12px;font-weight:600;cursor:pointer;display:flex;align-items:center;gap:6px;font-family:'Inter',sans-serif;transition:all 0.15s}
.col-btn:hover{border-color:var(--accent);color:var(--accent)}

/* SETTINGS */
.settings-group{background:var(--bg2);border:1px solid var(--border);border-radius:14px;overflow:hidden;margin-bottom:14px}
.settings-group-title{background:var(--bg3);padding:10px 16px;font-size:10px;color:var(--text3);text-transform:uppercase;letter-spacing:1.5px;font-weight:600;border-bottom:1px solid var(--border)}
.settings-row{display:flex;justify-content:space-between;align-items:center;padding:13px 16px;border-bottom:1px solid var(--border);cursor:pointer;transition:background 0.15s}
.settings-row:last-child{border-bottom:none}
.settings-row:hover{background:var(--bg3)}
.settings-lbl{font-size:13px;font-weight:500}
.settings-desc{font-size:10px;color:var(--text3);margin-top:2px}
.settings-val{font-size:12px;color:var(--text3);display:flex;align-items:center;gap:6px}
.settings-arrow{color:var(--border2);font-size:14px}
.settings-input{width:100%;padding:10px 13px;background:var(--bg);border:1px solid var(--border2);border-radius:9px;color:var(--text);font-size:13px;font-family:'Inter',sans-serif;outline:none;transition:border-color 0.2s;margin-top:6px}
.settings-input:focus{border-color:var(--accent)}
.toggle{width:42px;height:23px;border-radius:12px;border:none;cursor:pointer;position:relative;transition:background 0.2s;flex-shrink:0}
.toggle-thumb{width:17px;height:17px;background:#fff;border-radius:50%;position:absolute;top:3px;transition:left 0.2s}

/* MISC */
.close-btn{padding:4px 9px;background:transparent;color:var(--red);border:1px solid #F4645F40;border-radius:6px;font-size:9px;cursor:pointer;font-weight:700;transition:background 0.15s}
.close-btn:hover{background:#F4645F15}
.empty{text-align:center;padding:40px 20px}
.empty-icon{font-size:36px;margin-bottom:10px;opacity:0.4}
.empty-text{font-size:12px;color:var(--text3);line-height:1.6}
.loading{color:var(--text3);font-size:12px;padding:24px;text-align:center}
.notif-badge{display:inline-block;background:var(--green);color:#09090F;font-size:8px;font-weight:700;padding:1px 5px;border-radius:10px;margin-left:6px}
.notif-badge.off{background:var(--text3);color:var(--text)}

/* RESPONSIVE TABLET */
@media(max-width:1023px) and (min-width:768px){
  .sidebar{width:60px}
  .logo-text,.logo-badge,.nav-section-lbl,.nav-badge,.user-name,.user-plan{display:none}
  .sidebar-logo{padding:14px;justify-content:center}
  .sidebar-logo .logo-mark{margin:0}
  .nav-link{padding:10px;justify-content:center}
  .nav-link span:last-child{display:none}
  .nav-icon{width:auto;font-size:18px}
  .sidebar-footer{padding:8px 4px}
  .user-row{justify-content:center;padding:8px}
  .user-avatar{margin:0}
  .hero-stats{grid-template-columns:repeat(2,1fr)}
  .exc-grid{grid-template-columns:1fr}
}

/* RESPONSIVE MOBILE */
@media(max-width:767px){
  body{flex-direction:column}
  .sidebar{display:none}
  .main{height:100vh}
  .bottom-nav{display:flex}
  .page{padding:16px;padding-bottom:80px}
  .hero-stats{grid-template-columns:repeat(2,1fr);gap:10px;margin-bottom:16px}
  .hero-card{padding:14px}
  .hero-val{font-size:20px}
  .exc-grid{grid-template-columns:1fr;gap:10px}
  .topbar{padding:0 16px;height:50px}
  .paper-chip{display:none}
  .ticker-lbl{display:none}
  .tbl-container{margin:0 0 14px}
  .stats4{grid-template-columns:repeat(2,1fr)}
  .hist-filters{gap:6px}
  .col-btn{margin-left:0}
  table{font-size:11px}
  th,td{padding:8px 10px}
  .bot-flat-row{gap:8px;padding:12px 14px}
  .bot-toggle-wrap{gap:2px}
}

@media(max-width:480px){
  .hero-stats{grid-template-columns:1fr 1fr}
  .hero-val{font-size:18px}
  .live-ticker{padding:5px 8px}
  .ticker-price{font-size:12px}
}
</style>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
</head>
<body>

<!-- SIDEBAR -->
<div class="sidebar">
  <div class="sidebar-logo">
    <div class="logo-mark">A</div>
    <span class="logo-text">AVERION</span>
    <span class="logo-badge">BETA</span>
  </div>
  <div class="sidebar-nav">
    <div class="nav-section-lbl">Overview</div>
    <div class="nav-link active" onclick="switchTab('home',this)">
      <span class="nav-icon">&#127968;</span><span>Home</span>
    </div>
    <div class="nav-link" onclick="switchTab('bots',this)">
      <span class="nav-icon">&#129302;</span><span>Bots</span>
      <span class="nav-badge" id="navBotsBadge">0</span>
    </div>
    <div class="nav-section-lbl" style="margin-top:8px">Analytics</div>
    <div class="nav-link" onclick="switchTab('history',this)">
      <span class="nav-icon">&#128202;</span><span>History</span>
    </div>
    <div class="nav-section-lbl" style="margin-top:8px">System</div>
    <div class="nav-link" onclick="switchTab('settings',this)">
      <span class="nav-icon">&#9881;&#65039;</span><span>Settings</span>
    </div>
  </div>
  <div class="sidebar-footer">
    <div class="user-row">
      <div class="user-avatar">B</div>
      <div>
        <div class="user-name">Bader</div>
        <div class="user-plan" id="userPlan">Personal &middot; Paper</div>
      </div>
    </div>
  </div>
</div>

<!-- MAIN -->
<div class="main">

  <!-- TOPBAR -->
  <div class="topbar">
    <div class="topbar-left">
      <span class="page-title" id="pageTitle">Home</span>
    </div>
    <div class="topbar-right">
      <div class="paper-chip">&#9889; PAPER</div>
      <div class="live-ticker">
        <div class="ticker-dot"></div>
        <span class="ticker-lbl">BTC</span>
        <span class="ticker-price" id="btcPrice">Loading...</span>
      </div>
      <div class="icon-btn">&#128276;<div class="notif-dot"></div></div>
      <div class="icon-btn">&#128100;</div>
    </div>
  </div>

  <!-- PAGE CONTENT -->
  <div class="page">

    <!-- ══ HOME TAB ══ -->
    <div class="tab-content active" id="tab-home">
      <div class="hero-stats">
        <div class="hero-card">
          <div class="hero-icon">&#128176;</div>
          <div class="hero-lbl">Total Capital</div>
          <div class="hero-val" id="h-capital">$0.00</div>
          <div class="hero-sub" id="h-capital-sub">across all exchanges</div>
        </div>
        <div class="hero-card g">
          <div class="hero-icon">&#128200;</div>
          <div class="hero-lbl">Last 24h P&amp;L</div>
          <div class="hero-val" id="h-24h">$0.00</div>
          <div class="hero-sub" id="h-24h-pct">+0.00%</div>
        </div>
        <div class="hero-card b">
          <div class="hero-icon">&#127942;</div>
          <div class="hero-lbl">Total Profit</div>
          <div class="hero-val" id="h-profit">$0.00</div>
          <div class="hero-sub">all time &middot; all exchanges</div>
        </div>
        <div class="hero-card a">
          <div class="hero-icon">&#9888;&#65039;</div>
          <div class="hero-lbl">Fees Due</div>
          <div class="hero-val" id="h-fees" style="color:var(--amber)">$0.00</div>
          <div class="hero-sub" id="h-fees-sub">20% of realized profit</div>
        </div>
      </div>
      <div class="fees-banner" id="feesBanner" style="display:none">
        <div>
          <div class="fees-info-lbl">&#9888;&#65039; Performance Fee Due</div>
          <div class="fees-info-desc" id="feesDesc">20% of realized profit this month</div>
        </div>
        <span class="fees-amount" id="feesAmount">$0.00</span>
        <button class="btn btn-accent btn-sm" onclick="alert('Stripe payment - Phase 7')">Pay Now</button>
      </div>
      <div class="sec-hdr">
        <div>
          <div class="sec-title">Exchanges</div>
          <div class="sec-sub">Connected API accounts</div>
        </div>
        <button class="btn btn-accent btn-sm" onclick="openModal()">+ Add Exchange</button>
      </div>
      <div class="exc-grid" id="exchangesGrid">
        <div class="loading">Loading...</div>
      </div>
    </div>

    <!-- ══ EXCHANGE DETAIL ══ -->
    <div class="tab-content" id="tab-excdetail">
      <div style="margin:-24px">
        <div class="bot-detail-hdr">
          <div class="bot-detail-back" onclick="closeExcDetail()">&#8249; Home</div>
          <div class="bot-detail-title" id="excDetailName">Exchange</div>
          <div class="dropdown">
            <div class="exc-menu-btn" onclick="toggleDropdown(event,'dd-detail')">&#8943;</div>
            <div class="dropdown-menu" id="dd-detail">
              <div class="dropdown-item">&#10003; &nbsp;Test Connection</div>
              <div class="dropdown-item">&#9999; &nbsp;Edit API Keys</div>
              <div class="dropdown-item">&#127991; &nbsp;Rename</div>
              <div class="dropdown-item danger">&#10005; &nbsp;Delete Exchange</div>
            </div>
          </div>
        </div>
        <div class="stats4">
          <div class="stat4"><div class="stat4-lbl">Total Capital</div><div class="stat4-val" id="exc-capital">$0.00</div></div>
          <div class="stat4"><div class="stat4-lbl">Total Profit</div><div class="stat4-val" id="exc-profit" style="color:var(--green)">$0.00</div></div>
          <div class="stat4"><div class="stat4-lbl">Open Trades</div><div class="stat4-val" id="exc-open" style="color:var(--blue)">0</div></div>
          <div class="stat4"><div class="stat4-lbl">24h P&amp;L</div><div class="stat4-val" id="exc-pnl">$0.00</div></div>
        </div>
        <div style="padding:0 14px 14px">
          <div style="background:var(--bg2);border:1px solid var(--border);border-radius:14px;padding:16px">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">
              <div style="font-size:12px;font-weight:700">Capital History</div>
              <div style="display:flex;gap:6px">
                <button class="f-btn active" onclick="setChartRange('7d',this)">7D</button>
                <button class="f-btn" onclick="setChartRange('30d',this)">30D</button>
                <button class="f-btn" onclick="setChartRange('all',this)">All</button>
              </div>
            </div>
            <div style="position:relative;height:200px">
              <canvas id="capitalChart"></canvas>
            </div>
            <div style="font-size:9px;color:var(--text3);text-align:center;margin-top:8px">Hover over chart to see date and value</div>
          </div>
        </div>
        <div style="padding:0 14px">
          <div class="sec-hdr"><div class="sec-title">Bots on this Exchange</div></div>
          <div id="excDetailBots"></div>
        </div>
      </div>
    </div>

    <!-- ══ BOTS TAB (Item 24 — Flat List) ══ -->
    <div class="tab-content" id="tab-bots">

      <!-- L1: Flat list -->
      <div id="bots-l1">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px">
          <div>
            <div style="font-size:15px;font-weight:800">Bots</div>
            <div style="font-size:11px;color:var(--text3);margin-top:2px" id="botsSubtitle">Loading...</div>
          </div>
          <button class="btn btn-accent btn-sm" onclick="alert('Bot creation wizard - Phase 5')">+ New Bot</button>
        </div>
        <!-- Filter pills -->
        <div style="display:flex;gap:6px;margin-bottom:14px;overflow-x:auto;scrollbar-width:none;padding-bottom:2px">
          <button class="f-btn active" onclick="setBotListFilter('all',this)">All</button>
          <button class="f-btn" onclick="setBotListFilter('running',this)">&#128994; Running</button>
          <button class="f-btn" onclick="setBotListFilter('stopped',this)">&#11035; Stopped</button>
          <button class="f-btn" onclick="setBotListFilter('paper',this)">&#128196; Paper</button>
        </div>
        <!-- Flat list card -->
        <div style="background:var(--bg2);border:1px solid var(--border);border-radius:16px;overflow:hidden" id="flatBotsList">
          <div class="loading">Loading...</div>
        </div>
      </div>

      <!-- L2: Bot detail (positions) -->
      <div id="bots-l2" style="display:none;margin:-24px">
        <div class="bot-detail-hdr">
          <div class="bot-detail-back" onclick="backToBots()">&#8249; Bots</div>
          <div class="bot-detail-title" id="bdTitle">Bot</div>
          <div class="bot-detail-badge" id="bdBadge">&#9679; Live</div>
        </div>
        <div class="stats4">
          <div class="stat4"><div class="stat4-lbl">Open</div><div class="stat4-val" id="bd-open" style="color:var(--blue)">0</div></div>
          <div class="stat4"><div class="stat4-lbl">Invested</div><div class="stat4-val" id="bd-inv" style="color:var(--purple)">$0</div></div>
          <div class="stat4"><div class="stat4-lbl">P&amp;L$</div><div class="stat4-val" id="bd-pnl">$0</div></div>
          <div class="stat4"><div class="stat4-lbl">P&amp;L%</div><div class="stat4-val" id="bd-pnlpct">0%</div></div>
        </div>
        <div style="display:flex;gap:8px;padding:0 14px 12px">
          <button class="btn btn-red btn-sm" id="bdToggleBtn" onclick="toggleBot()">&#11035; Stop Bot</button>
          <button class="btn btn-ghost btn-sm" onclick="applyBotFilter()">&#8635; Refresh</button>
        </div>
        <div class="search-wrap">
          <input class="search-input" id="bdSearch" onkeyup="applyBotFilter()" placeholder="&#128269; Search coin...">
        </div>
        <div class="filter-bar">
          <button class="f-btn active" onclick="setBotFilter('all',this)">All</button>
          <button class="f-btn" onclick="setBotFilter('profit',this)">&#128200; Profit</button>
          <button class="f-btn" onclick="setBotFilter('loss',this)">&#128201; Loss</button>
          <button class="f-btn" onclick="setBotFilter('dca',this)">&#128260; DCA'd</button>
          <button class="f-btn" onclick="setBotFilter('stuck',this)">&#8987; Stuck</button>
          <button class="f-btn" onclick="setBotFilter('tp',this)">&#128640; TP Armed</button>
        </div>
        <div class="tbl-container">
          <div class="tbl-hdr">
            <span class="tbl-title">Positions</span>
            <span class="tbl-count" id="bd-count">0 open</span>
          </div>
          <table>
            <thead><tr>
              <th onclick="sortBd('coin')">Coin &#8597;</th>
              <th>Avg Cost</th><th>Current</th>
              <th onclick="sortBd('dca_count')">DCA# &#8597;</th>
              <th onclick="sortBd('days_open')">Days &#8597;</th>
              <th onclick="sortBd('pnl_pct')">P&amp;L% &#8597;</th>
              <th onclick="sortBd('pnl')">P&amp;L$ &#8597;</th>
              <th>Status</th><th>Action</th>
            </tr></thead>
            <tbody id="bdTable"><tr><td colspan="9" class="loading">Loading...</td></tr></tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ══ HISTORY TAB ══ -->
    <div class="tab-content" id="tab-history">
      <div class="hero-stats" style="margin-bottom:16px;grid-template-columns:repeat(3,1fr)">
        <div class="hero-card">
          <div class="hero-lbl">Closed Trades</div>
          <div class="hero-val" id="hs-count" style="color:var(--blue)">0</div>
        </div>
        <div class="hero-card g">
          <div class="hero-lbl">Total Profit</div>
          <div class="hero-val" id="hs-profit">$0.00</div>
        </div>
        <div class="hero-card">
          <div class="hero-lbl">Win Rate</div>
          <div class="hero-val" id="hs-winrate" style="color:var(--green)">0%</div>
        </div>
        <div class="hero-card">
          <div class="hero-lbl">Avg Hold</div>
          <div class="hero-val" id="hs-avghold" style="color:var(--text2)">&#8212;</div>
        </div>
        <div class="hero-card a">
          <div class="hero-lbl">Fees (20%)</div>
          <div class="hero-val" id="hs-fees" style="color:var(--amber)">$0.00</div>
          <div class="hero-sub">performance fee due</div>
        </div>
        <div class="hero-card b">
          <div class="hero-lbl">Net Profit</div>
          <div class="hero-val" id="hs-net">$0.00</div>
          <div class="hero-sub">after fees</div>
        </div>
      </div>
      <div class="hist-filters">
        <select class="filter-sel" id="hf-exchange" onchange="applyHistoryFilter()">
          <option value="">All Exchanges</option>
          <option value="MEXC">MEXC</option>
          <option value="Binance">Binance</option>
        </select>
        <select class="filter-sel" id="hf-coin" onchange="applyHistoryFilter()">
          <option value="">All Coins</option>
        </select>
        <div class="date-presets">
          <button class="date-preset" onclick="setDateFilter('today',this)">Today</button>
          <button class="date-preset" onclick="setDateFilter('7d',this)">7d</button>
          <button class="date-preset" onclick="setDateFilter('30d',this)">30d</button>
          <button class="date-preset active" onclick="setDateFilter('all',this)">All</button>
        </div>
        <div class="date-range-wrap">
          <span class="date-range-lbl">From</span>
          <input class="date-input" type="date" id="hf-from" onchange="applyHistoryFilter()">
          <span class="date-range-lbl">To</span>
          <input class="date-input" type="date" id="hf-to" onchange="applyHistoryFilter()">
          <button class="date-preset" onclick="clearDateRange()">&#10005; Clear</button>
        </div>
        <button class="col-btn" onclick="toggleColumnPicker()">&#8862; Columns</button>
      </div>
      <div id="columnPicker" style="display:none;background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:14px;margin-bottom:14px">
        <div style="font-size:11px;color:var(--text3);margin-bottom:10px;font-weight:600;text-transform:uppercase;letter-spacing:1px">Show / Hide Columns</div>
        <div style="display:flex;flex-wrap:wrap;gap:8px" id="columnToggles"></div>
      </div>
      <div class="tbl-container" style="margin:0 0 14px">
        <div class="tbl-hdr">
          <span class="tbl-title">Closed Positions</span>
          <span class="tbl-count" id="hs-tbl-count">0 trades</span>
        </div>
        <table>
          <thead><tr id="historyThead"></tr></thead>
          <tbody id="historyTable"><tr><td class="loading">Loading...</td></tr></tbody>
        </table>
      </div>
    </div>

    <!-- ══ SETTINGS TAB ══ -->
    <div class="tab-content" id="tab-settings">
      <div style="max-width:560px">
        <div class="settings-group">
          <div class="settings-group-title">Profile</div>
          <div class="settings-row" onclick="editField('email')">
            <div>
              <div class="settings-lbl">Email Address</div>
              <div class="settings-desc" id="set-email">bader@example.com</div>
            </div>
            <div class="settings-val"><span>Edit</span><span class="settings-arrow">&#8250;</span></div>
          </div>
          <div class="settings-row" onclick="editField('phone')">
            <div>
              <div class="settings-lbl">Phone Number</div>
              <div class="settings-desc" id="set-phone">+966 &mdash; not set</div>
            </div>
            <div class="settings-val"><span>Edit</span><span class="settings-arrow">&#8250;</span></div>
          </div>
        </div>
        <div class="settings-group">
          <div class="settings-group-title">Security</div>
          <div class="settings-row" onclick="toggle2FA()">
            <div>
              <div class="settings-lbl">Two-Factor Authentication</div>
              <div class="settings-desc">Telegram code on new device login</div>
            </div>
            <button class="toggle" id="toggle2fa" style="background:var(--text3)">
              <div class="toggle-thumb" id="thumb2fa" style="left:3px"></div>
            </button>
          </div>
          <div class="settings-row" onclick="editField('password')">
            <div>
              <div class="settings-lbl">Change Password</div>
              <div class="settings-desc">Last changed &mdash; never</div>
            </div>
            <div class="settings-val"><span>Change</span><span class="settings-arrow">&#8250;</span></div>
          </div>
        </div>
        <div class="settings-group">
          <div class="settings-group-title">Exchanges</div>
          <div class="settings-row" onclick="switchTab('home', document.querySelector('.nav-link'))">
            <div>
              <div class="settings-lbl">Manage Exchanges</div>
              <div class="settings-desc" id="set-exc-count">0 connected</div>
            </div>
            <div class="settings-val"><span>Manage</span><span class="settings-arrow">&#8250;</span></div>
          </div>
        </div>
        <div class="settings-group">
          <div class="settings-group-title">Notifications</div>
          <div class="settings-row">
            <div>
              <div class="settings-lbl">Telegram Alerts</div>
              <div class="settings-desc">DCA fired, TP hit, stuck position, errors</div>
            </div>
            <button class="toggle" id="toggleTelegram" onclick="toggleNotif('telegram')" style="background:var(--text3)">
              <div class="toggle-thumb" id="thumbTelegram" style="left:3px"></div>
            </button>
          </div>
          <div class="settings-row" id="telegramSetup" style="display:none">
            <div style="flex:1">
              <div class="settings-lbl" style="margin-bottom:4px">Telegram Chat ID</div>
              <input class="settings-input" id="telegramId" placeholder="Enter your Telegram Chat ID">
            </div>
          </div>
          <div class="settings-row">
            <div>
              <div class="settings-lbl">DCA Fired Alerts</div>
              <div class="settings-desc">Notify when a DCA buy executes</div>
            </div>
            <button class="toggle" id="toggleDCA" onclick="toggleNotif('dca')" style="background:var(--accent)">
              <div class="toggle-thumb" id="thumbDCA" style="left:22px"></div>
            </button>
          </div>
          <div class="settings-row">
            <div>
              <div class="settings-lbl">TP Hit Alerts</div>
              <div class="settings-desc">Notify when take profit triggers</div>
            </div>
            <button class="toggle" id="toggleTP" onclick="toggleNotif('tp')" style="background:var(--accent)">
              <div class="toggle-thumb" id="thumbTP" style="left:22px"></div>
            </button>
          </div>
          <div class="settings-row">
            <div>
              <div class="settings-lbl">Stuck Position Alerts</div>
              <div class="settings-desc">Notify when position stuck &gt; 30 days</div>
            </div>
            <button class="toggle" id="toggleStuck" onclick="toggleNotif('stuck')" style="background:var(--accent)">
              <div class="toggle-thumb" id="thumbStuck" style="left:22px"></div>
            </button>
          </div>
        </div>
        <div class="settings-group">
          <div class="settings-group-title">Help &amp; Support</div>
          <div class="settings-row" onclick="alert('Documentation - coming soon')">
            <div>
              <div class="settings-lbl">Documentation</div>
              <div class="settings-desc">How to use Averion</div>
            </div>
            <div class="settings-val"><span class="settings-arrow">&#8250;</span></div>
          </div>
          <div class="settings-row" onclick="openFeatureRequest()">
            <div>
              <div class="settings-lbl">Feature Request</div>
              <div class="settings-desc">Suggest something new</div>
            </div>
            <div class="settings-val"><span class="settings-arrow">&#8250;</span></div>
          </div>
          <div class="settings-row" onclick="alert('Support - coming soon')">
            <div>
              <div class="settings-lbl">Contact Support</div>
              <div class="settings-desc">Report a bug or get help</div>
            </div>
            <div class="settings-val"><span class="settings-arrow">&#8250;</span></div>
          </div>
        </div>
        <div style="padding:12px 16px;text-align:center;color:var(--text3);font-size:11px">
          Averion v0.3 &middot; Paper Mode &middot; Phase 3<br>
          <span style="font-size:10px;color:var(--text3)">github.com/baderbalubaid/Averion</span>
        </div>
      </div>
    </div>

  </div><!-- /page -->
</div><!-- /main -->

<!-- BOTTOM NAV -->
<nav class="bottom-nav" id="bottomNav">
  <button class="bnav-item active" onclick="switchTabMobile('home',this)">
    <span class="bnav-icon">&#127968;</span><span>Home</span>
  </button>
  <button class="bnav-item" onclick="switchTabMobile('bots',this)">
    <span class="bnav-icon">&#129302;</span><span>Bots</span>
  </button>
  <button class="bnav-item" onclick="switchTabMobile('history',this)">
    <span class="bnav-icon">&#128202;</span><span>History</span>
  </button>
  <button class="bnav-item" onclick="switchTabMobile('settings',this)">
    <span class="bnav-icon">&#9881;&#65039;</span><span>Settings</span>
  </button>
</nav>

<!-- ADD EXCHANGE MODAL -->
<div class="modal-overlay" id="addModal">
  <div class="modal">
    <div class="modal-hdr">
      <span class="modal-title">Add Exchange</span>
      <button class="modal-close" onclick="closeModal()">&#10005;</button>
    </div>
    <div class="modal-body">
      <div class="form-group">
        <label class="form-label">Exchange</label>
        <select class="form-select" id="m-exchange" onchange="onExchangeChange()">
          <option value="mexc">MEXC</option>
          <option value="binance">Binance</option>
          <option value="kucoin">KuCoin</option>
          <option value="gateio">Gate.io</option>
          <option value="okx">OKX</option>
          <option value="htx">HTX</option>
        </select>
      </div>
      <div class="form-group">
        <label class="form-label">Custom Name</label>
        <input class="form-input" id="m-name" placeholder="e.g. My MEXC Main Account">
      </div>
      <div class="form-group">
        <label class="form-label">API Key</label>
        <input class="form-input" id="m-apikey" placeholder="Paste your API key">
      </div>
      <div class="form-group">
        <label class="form-label">API Secret</label>
        <input class="form-input" id="m-secret" type="password" placeholder="Paste your API secret">
      </div>
      <div class="form-group" id="m-pass-group" style="display:none">
        <label class="form-label">Passphrase</label>
        <input class="form-input" id="m-passphrase" type="password" placeholder="Required for this exchange">
      </div>
      <div class="form-hint">&#8505;&#65039; Enable <strong>Read + Trade</strong> only. Never enable withdrawals.</div>
    </div>
    <div class="modal-footer">
      <button class="btn btn-ghost" style="flex:1" onclick="closeModal()">Cancel</button>
      <button class="btn btn-accent" style="flex:2;justify-content:center" onclick="saveExchange()">&#10003; Test &amp; Save</button>
    </div>
  </div>
</div>

<!-- FEATURE REQUEST MODAL -->
<div class="modal-overlay" id="featureModal">
  <div class="modal">
    <div class="modal-hdr">
      <span class="modal-title">Feature Request</span>
      <button class="modal-close" onclick="document.getElementById('featureModal').classList.remove('open')">&#10005;</button>
    </div>
    <div class="modal-body">
      <div class="form-group">
        <label class="form-label">What would you like to see?</label>
        <textarea class="form-input" id="featureText" rows="4" placeholder="Describe the feature..." style="resize:vertical"></textarea>
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn btn-ghost" style="flex:1" onclick="document.getElementById('featureModal').classList.remove('open')">Cancel</button>
      <button class="btn btn-accent" style="flex:2;justify-content:center" onclick="submitFeature()">Send Request</button>
    </div>
  </div>
</div>

<script>
const API = 'https://bbd72f98-d728-46fe-81c6-af97d0011150-00-1c2g4v036wde1.sisko.replit.dev';

const EXC = {
  mexc:    {name:'MEXC',    bg:'#1E3A5F',text:'#38BDF8',logo:'M',pass:false},
  binance: {name:'Binance', bg:'#3D2B00',text:'#F59E0B',logo:'B',pass:false},
  kucoin:  {name:'KuCoin',  bg:'#003D1E',text:'#4ADE80',logo:'K',pass:true},
  gateio:  {name:'Gate.io', bg:'#1A2E3D',text:'#38BDF8',logo:'G',pass:false},
  okx:     {name:'OKX',     bg:'#1A1A1A',text:'#E2E8F0',logo:'O',pass:true},
  htx:     {name:'HTX',     bg:'#3D0000',text:'#F87171',logo:'H',pass:false},
  bybit:   {name:'Bybit',   bg:'#2D1A00',text:'#FB923C',logo:'By',pass:false},
  bitget:  {name:'Bitget',  bg:'#1A0D2E',text:'#A78BFA',logo:'Bg',pass:true},
};

const HISTORY_COLS = [
  {key:'coin',        label:'Coin',        show:true},
  {key:'exchange',    label:'Exchange',    show:true},
  {key:'entry_date',  label:'Entry Date',  show:true},
  {key:'exit_date',   label:'Exit Date',   show:true},
  {key:'entry_price', label:'Entry Price', show:true},
  {key:'avg_cost',    label:'Avg Cost',    show:false},
  {key:'exit_price',  label:'Exit Price',  show:true},
  {key:'dca_count',   label:'DCA#',        show:true},
  {key:'pnl_pct',     label:'P&L%',        show:true},
  {key:'pnl_usd',     label:'P&L$',        show:true},
  {key:'hold',        label:'Hold Time',   show:false},
  {key:'exit_reason', label:'Exit',        show:true},
  {key:'fee',         label:'Fee (20%)',   show:true},
  {key:'net_profit',  label:'Net Profit',  show:true},
];

let allPositions      = [];
let allHistory        = [];
let botFilter         = 'all';
let botSort           = 'pnl_pct';
let botSortAsc        = true;
let currentBotRunning = true;
let histDateFilter    = 'all';
let botListFilter     = 'all';

// ── TAB NAVIGATION ──
const TAB_TITLES = {home:'Home',bots:'Bots',history:'History',settings:'Settings'};

function switchTab(name, el) {
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.nav-link').forEach(n => n.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
  if(el) el.classList.add('active');
  document.getElementById('pageTitle').textContent = TAB_TITLES[name];
  if(name==='history'){ fetchHistory(); buildColumnToggles(); }
  if(name==='bots')   renderBotsList();
  if(name==='settings') renderSettings();
}

function switchTabMobile(name, el) {
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.bnav-item').forEach(n => n.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
  el.classList.add('active');
  document.getElementById('pageTitle').textContent = TAB_TITLES[name];
  if(name==='history'){ fetchHistory(); buildColumnToggles(); }
  if(name==='bots')   renderBotsList();
  if(name==='settings') renderSettings();
}

// ── STATUS ──
async function fetchStatus() {
  try {
    const res = await fetch(`${API}/status`);
    const d   = await res.json();
    document.getElementById('btcPrice').textContent =
      '$' + (d.btc_price||0).toLocaleString('en-US',{maximumFractionDigits:2});
    document.getElementById('navBotsBadge').textContent = allPositions.length;
  } catch(e) {
    document.getElementById('btcPrice').textContent = 'Offline';
  }
}

// ── POSITIONS ──
async function fetchPositions() {
  try {
    const res = await fetch(`${API}/positions`);
    allPositions = await res.json();
    renderHome();
    if(document.getElementById('bots-l2').style.display !== 'none') applyBotFilter();
  } catch(e) {}
}

function statusInfo(pos) {
  const d = pos.days_open || 0;
  if(pos.tp_armed) return {label:'&#128640; TP Armed', cls:'badge-tp'};
  if(d > 60)       return {label:'&#128308; Critical', cls:'badge-critical'};
  if(d > 30)       return {label:'&#128993; Stuck',    cls:'badge-stuck'};
  if(pos.queued)   return {label:'&#8987; Queued',     cls:'badge-queued'};
  return {label:'&#128994; Active', cls:'badge-active'};
}

// ── HOME ──
function renderHome() {
  const total = allPositions.reduce((s,p) => s + p.total_invested, 0);
  const pnl   = allPositions.reduce((s,p) => s + p.pnl, 0);
  const pct   = total > 0 ? (pnl/total*100).toFixed(2) : '0.00';
  const fees  = Math.max(0, pnl * 0.20);

  document.getElementById('h-capital').textContent = '$' + total.toFixed(2);
  document.getElementById('h-capital-sub').textContent =
    `across ${getExchanges().length} exchange${getExchanges().length!==1?'s':''}`;

  const el24 = document.getElementById('h-24h');
  el24.textContent = (pnl>=0?'+':'') + '$' + Math.abs(pnl).toFixed(2);
  el24.style.color = pnl>=0?'var(--green)':'var(--red)';
  const elPct = document.getElementById('h-24h-pct');
  elPct.textContent = (pnl>=0?'+':'') + pct + '%';
  elPct.style.color = pnl>=0?'var(--green)':'var(--red)';

  const profEl = document.getElementById('h-profit');
  profEl.textContent = (pnl>=0?'+':'') + '$' + Math.abs(pnl).toFixed(2);
  profEl.style.color = pnl>=0?'var(--blue)':'var(--red)';

  document.getElementById('h-fees').textContent = '$' + fees.toFixed(2);
  document.getElementById('h-fees-sub').textContent =
    fees > 0 ? `20% of $${pnl.toFixed(2)} profit` : 'No fees due';

  const banner = document.getElementById('feesBanner');
  if(fees > 0){
    banner.style.display = 'flex';
    document.getElementById('feesAmount').textContent = '$' + fees.toFixed(2);
    document.getElementById('feesDesc').textContent = `20% of $${pnl.toFixed(2)} realized profit`;
  } else {
    banner.style.display = 'none';
  }
  renderExchanges();
}

// ── EXCHANGES ──
function getExchanges() {
  try { return JSON.parse(localStorage.getItem('av_exchanges') || '[]'); }
  catch(e) { return []; }
}
function setExchanges(list) {
  try { localStorage.setItem('av_exchanges', JSON.stringify(list)); } catch(e) {}
}

function renderExchanges() {
  const list  = getExchanges();
  const grid  = document.getElementById('exchangesGrid');
  const count = list.length;
  const setExc = document.getElementById('set-exc-count');
  if(setExc) setExc.textContent = `${count} connected`;

  if(count === 0){
    grid.innerHTML = `<div class="exc-add" onclick="openModal()">
      <div class="exc-add-icon">&#128268;</div>
      <div class="exc-add-text">Connect your first exchange</div>
    </div>`;
    return;
  }

  const posCount = allPositions.length;
  const pnl      = allPositions.reduce((s,p)=>s+p.pnl,0);
  const inv      = allPositions.reduce((s,p)=>s+p.total_invested,0);
  const pnlSign  = pnl>=0?'+':'';
  const pnlColor = pnl>=0?'var(--green)':'var(--red)';
  const coins    = allPositions.slice(0,5).map(p=>p.coin.replace('/USDT','')).filter(Boolean);
  const more     = Math.max(0, posCount - 5);

  grid.innerHTML = list.map(exc => {
    const cfg = EXC[exc.id] || {name:exc.id,bg:'#1E1E35',text:'#E2E8F0',logo:'?'};
    const displayName = exc.name || cfg.name;
    return `
    <div class="exc-card" onclick="openExcDetail('${exc.id}')">
      <div class="exc-top">
        <div class="exc-logo" style="background:${cfg.bg};color:${cfg.text}">${cfg.logo}</div>
        <div class="exc-info">
          <div class="exc-name">${displayName}</div>
          <div class="exc-sub"><div class="exc-dot"></div>Connected &middot; ${posCount} positions</div>
        </div>
        <div class="exc-right">
          <div class="exc-val-wrap">
            <div class="exc-amount">$${inv.toFixed(2)}</div>
            <div class="exc-pnl" style="color:${pnlColor}">${pnlSign}$${Math.abs(pnl).toFixed(2)} today</div>
          </div>
          <div class="dropdown">
            <div class="exc-menu-btn" onclick="toggleDropdown(event,'dd-${exc.id}')">&#8943;</div>
            <div class="dropdown-menu" id="dd-${exc.id}">
              <div class="dropdown-item" onclick="testExc(event,'${exc.id}')">&#10003; &nbsp;Test Connection</div>
              <div class="dropdown-item" onclick="editExc(event,'${exc.id}')">&#9999;&#65039; &nbsp;Edit API Keys</div>
              <div class="dropdown-item" onclick="renameExc(event,'${exc.id}')">&#127991;&#65039; &nbsp;Rename</div>
              <div class="dropdown-item danger" onclick="deleteExc(event,'${exc.id}')">&#10005; &nbsp;Delete Exchange</div>
            </div>
          </div>
        </div>
      </div>
      <div class="exc-stats">
        <div class="exc-stat"><div class="exc-stat-lbl">Positions</div><div class="exc-stat-val" style="color:var(--blue)">${posCount}</div></div>
        <div class="exc-stat"><div class="exc-stat-lbl">Bots Live</div><div class="exc-stat-val"><span style="color:var(--green)">1</span>/1</div></div>
        <div class="exc-stat"><div class="exc-stat-lbl">24h P&amp;L</div><div class="exc-stat-val" style="color:${pnlColor}">${pnlSign}$${Math.abs(pnl).toFixed(2)}</div></div>
      </div>
      ${coins.length>0?`<div class="exc-footer">
        ${coins.map(c=>`<span class="coin-tag">${c}</span>`).join('')}
        ${more>0?`<span class="coin-more">+${more} more</span>`:''}
      </div>`:''}
    </div>`;
  }).join('') + `
  <div class="exc-add" onclick="openModal()">
    <div class="exc-add-icon">&#128268;</div>
    <div class="exc-add-text">Connect another exchange</div>
  </div>`;
}

function toggleDropdown(e, id) {
  e.stopPropagation();
  const menu   = document.getElementById(id);
  const isOpen = menu.classList.contains('open');
  document.querySelectorAll('.dropdown-menu').forEach(m => m.classList.remove('open'));
  if(!isOpen) menu.classList.add('open');
}
document.addEventListener('click', () => {
  document.querySelectorAll('.dropdown-menu').forEach(m => m.classList.remove('open'));
});

function testExc(e, id) {
  e.stopPropagation();
  document.querySelectorAll('.dropdown-menu').forEach(m => m.classList.remove('open'));
  alert(`&#10003; ${EXC[id]?.name || id} API connection successful!`);
}
function editExc(e, id) {
  e.stopPropagation();
  document.querySelectorAll('.dropdown-menu').forEach(m => m.classList.remove('open'));
  document.getElementById('m-exchange').value = id;
  onExchangeChange();
  openModal();
}
function renameExc(e, id) {
  e.stopPropagation();
  document.querySelectorAll('.dropdown-menu').forEach(m => m.classList.remove('open'));
  const list = getExchanges();
  const exc  = list.find(x => x.id === id);
  if(!exc) return;
  const name = prompt('New name:', exc.name || EXC[id]?.name || id);
  if(name && name.trim()){ exc.name = name.trim(); setExchanges(list); renderExchanges(); }
}
function deleteExc(e, id) {
  e.stopPropagation();
  document.querySelectorAll('.dropdown-menu').forEach(m => m.classList.remove('open'));
  if(!confirm(`Remove ${EXC[id]?.name || id}?`)) return;
  setExchanges(getExchanges().filter(x => x.id !== id));
  renderExchanges();
}

function openModal()  { document.getElementById('addModal').classList.add('open'); }
function closeModal() { document.getElementById('addModal').classList.remove('open'); }
function onExchangeChange() {
  const id = document.getElementById('m-exchange').value;
  document.getElementById('m-pass-group').style.display = EXC[id]?.pass ? 'block' : 'none';
  document.getElementById('m-name').placeholder = `e.g. My ${EXC[id]?.name||''} Account`;
}
function saveExchange() {
  const id   = document.getElementById('m-exchange').value;
  const name = document.getElementById('m-name').value.trim() || EXC[id]?.name || id;
  const key  = document.getElementById('m-apikey').value.trim();
  if(!key){ alert('Please enter your API key'); return; }
  const list     = getExchanges();
  const existing = list.find(x => x.id === id);
  if(!existing) list.push({id, name, connected:true});
  else { existing.name = name; existing.connected = true; }
  setExchanges(list);
  closeModal();
  renderExchanges();
  alert(`&#10003; ${name} connected!`);
}

// ── BOTS FLAT LIST (Item 24) ──
function setBotListFilter(type, el) {
  botListFilter = type;
  document.querySelectorAll('#bots-l1 .f-btn').forEach(b => b.classList.remove('active'));
  el.classList.add('active');
  renderBotsList();
}

function renderBotsList() {
  const container = document.getElementById('flatBotsList');
  const subtitle  = document.getElementById('botsSubtitle');
  const exchanges = getExchanges();

  if(exchanges.length === 0){
    container.innerHTML = `<div class="empty"><div class="empty-icon">&#128268;</div><div class="empty-text">No exchanges connected.<br>Add one from the Home tab.</div></div>`;
    if(subtitle) subtitle.textContent = '0 bots';
    return;
  }

  const pnl    = allPositions.reduce((s,p) => s + p.pnl, 0);
  const trades = allPositions.length;

  const bots = exchanges.map(exc => {
    const cfg     = EXC[exc.id] || {};
    const name    = exc.name || cfg.name || exc.id;
    const running = exc.trading !== false;
    const dcaOn   = exc.dca    !== false;
    return {id:exc.id, name, cfg, running, dcaOn, pnl, trades, mode:'Paper'};
  });

  const filtered = bots.filter(b => {
    if(botListFilter === 'running') return b.running;
    if(botListFilter === 'stopped') return !b.running;
    if(botListFilter === 'paper')   return b.mode === 'Paper';
    return true;
  });

  const runCount = bots.filter(b => b.running).length;
  if(subtitle) subtitle.textContent = `${bots.length} bot${bots.length!==1?'s':''} \u00b7 ${runCount} running`;

  if(!filtered.length){
    container.innerHTML = `<div class="empty"><div class="empty-icon">&#129302;</div><div class="empty-text">No bots match this filter.</div></div>`;
    return;
  }

  container.innerHTML = filtered.map(bot => {
    const pnlSign  = bot.pnl >= 0 ? '+' : '';
    const pnlColor = bot.pnl >= 0 ? 'var(--green)' : 'var(--red)';
    const badgeBg  = bot.cfg.bg    || '#1E1E35';
    const badgeClr = bot.cfg.text  || '#E2E8F0';
    const badgeLbl = bot.cfg.logo  || '?';
    return `
    <div class="bot-flat-row" onclick="openBotDetail('${bot.name}',${bot.running})">
      <div class="bot-status-dot ${bot.running?'on':'off'}"></div>
      <div class="exc-badge" style="background:${badgeBg};color:${badgeClr}">${badgeLbl}</div>
      <div style="flex:1;min-width:0">
        <div class="bot-flat-name">${bot.name}</div>
        <div class="bot-flat-meta">
          Trades: <span>${bot.trades}</span> &nbsp;&middot;&nbsp;
          P&amp;L: <span style="color:${pnlColor}">${pnlSign}$${Math.abs(bot.pnl).toFixed(2)}</span> &nbsp;&middot;&nbsp;
          <span>${bot.mode}</span>
        </div>
      </div>
      <div class="bot-toggle-wrap" onclick="event.stopPropagation()">
        <span class="toggle-lbl">T</span>
        <button class="toggle-mini"
          style="background:${bot.running?'var(--green)':'var(--text3)'}"
          onclick="toggleBotSwitch('${bot.id}','trading',this)">
          <div class="toggle-mini-thumb" style="left:${bot.running?'18px':'3px'}"></div>
        </button>
      </div>
      <div class="bot-toggle-wrap" onclick="event.stopPropagation()">
        <span class="toggle-lbl">DCA</span>
        <button class="toggle-mini"
          style="background:${bot.dcaOn?'var(--accent)':'var(--text3)'}"
          onclick="toggleBotSwitch('${bot.id}','dca',this)">
          <div class="toggle-mini-thumb" style="left:${bot.dcaOn?'18px':'3px'}"></div>
        </button>
      </div>
      <div class="dropdown" onclick="event.stopPropagation()">
        <div class="kebab-btn" onclick="toggleDropdown(event,'keb-${bot.id}')">&#8943;</div>
        <div class="dropdown-menu" id="keb-${bot.id}">
          <div class="dropdown-item" onclick="alert('Bot wizard - Phase 5')">&#9999;&#65039; &nbsp;Edit Settings</div>
          <div class="dropdown-item" onclick="alert('Duplicate - Phase 5')">&#10064; &nbsp;Duplicate Bot</div>
          <div class="dropdown-item danger" onclick="alert('Delete - Phase 5')">&#10005; &nbsp;Delete Bot</div>
        </div>
      </div>
    </div>`;
  }).join('');
}

function toggleBotSwitch(excId, type, btn) {
  const list = getExchanges();
  const exc  = list.find(e => e.id === excId);
  if(!exc) return;
  if(type === 'trading'){
    exc.trading = exc.trading === false ? true : false;
    const on = exc.trading !== false;
    btn.style.background = on ? 'var(--green)' : 'var(--text3)';
    btn.querySelector('.toggle-mini-thumb').style.left = on ? '18px' : '3px';
    if(on) fetch(`${API}/start`,{method:'POST'});
    else   fetch(`${API}/stop`, {method:'POST'});
  } else {
    exc.dca = exc.dca === false ? true : false;
    const on = exc.dca !== false;
    btn.style.background = on ? 'var(--accent)' : 'var(--text3)';
    btn.querySelector('.toggle-mini-thumb').style.left = on ? '18px' : '3px';
  }
  setExchanges(list);
  const exchanges = getExchanges();
  const subtitle  = document.getElementById('botsSubtitle');
  if(subtitle) subtitle.textContent =
    `${exchanges.length} bot${exchanges.length!==1?'s':''} \u00b7 ${exchanges.filter(e=>e.trading!==false).length} running`;
}

// ── BOT DETAIL (L2) ──
function openBotDetail(name, running) {
  currentBotRunning = running;
  document.getElementById('bots-l1').style.display = 'none';
  document.getElementById('bots-l2').style.display = 'block';
  document.getElementById('bdTitle').textContent = name;
  updateBdHeader();
  applyBotFilter();
}
function backToBots() {
  document.getElementById('bots-l1').style.display = 'block';
  document.getElementById('bots-l2').style.display = 'none';
  renderBotsList();
}
function updateBdHeader() {
  const badge = document.getElementById('bdBadge');
  const btn   = document.getElementById('bdToggleBtn');
  if(currentBotRunning){
    badge.textContent='&#9679; Live'; badge.className='bot-detail-badge';
    btn.textContent='&#11035; Stop Bot'; btn.className='btn btn-red btn-sm';
  } else {
    badge.textContent='&#9675; Stopped'; badge.className='bot-detail-badge off';
    btn.textContent='&#9654; Start Bot'; btn.className='btn btn-green btn-sm';
  }
}
async function toggleBot() {
  if(currentBotRunning) await fetch(`${API}/stop`,{method:'POST'});
  else                  await fetch(`${API}/start`,{method:'POST'});
  currentBotRunning = !currentBotRunning;
  updateBdHeader();
}

function applyBotFilter() {
  const search = (document.getElementById('bdSearch')?.value||'').toLowerCase();
  let data = allPositions.filter(p => {
    if(!p.coin.toLowerCase().includes(search)) return false;
    const d = p.days_open||0;
    if(botFilter==='profit') return p.pnl>=0;
    if(botFilter==='loss')   return p.pnl<0;
    if(botFilter==='dca')    return p.dca_count>0;
    if(botFilter==='stuck')  return d>30;
    if(botFilter==='tp')     return p.tp_armed;
    return true;
  });
  data.sort((a,b)=>{
    let av=a[botSort]??0, bv=b[botSort]??0;
    if(typeof av==='string') return botSortAsc?av.localeCompare(bv):bv.localeCompare(av);
    return botSortAsc?av-bv:bv-av;
  });
  const invested = data.reduce((s,p)=>s+p.total_invested,0);
  const pnl      = data.reduce((s,p)=>s+p.pnl,0);
  const pct      = invested>0?(pnl/invested*100).toFixed(2):'0.00';
  document.getElementById('bd-open').textContent = data.length;
  document.getElementById('bd-inv').textContent  = '$'+invested.toFixed(2);
  const pe = document.getElementById('bd-pnl');
  pe.textContent = (pnl>=0?'+':'')+'$'+Math.abs(pnl).toFixed(2);
  pe.style.color = pnl>=0?'var(--green)':'var(--red)';
  const pp = document.getElementById('bd-pnlpct');
  pp.textContent = (pnl>=0?'+':'')+pct+'%';
  pp.style.color = pnl>=0?'var(--green)':'var(--red)';
  document.getElementById('bd-count').textContent = data.length+' open';
  const tbody = document.getElementById('bdTable');
  if(!data.length){
    tbody.innerHTML=`<tr><td colspan="9"><div class="empty"><div class="empty-icon">&#129302;</div><div class="empty-text">No positions match filter</div></div></td></tr>`;
    return;
  }
  tbody.innerHTML = data.map(pos => {
    const pc   = pos.pnl>=0?'var(--green)':'var(--red)';
    const sign = pos.pnl>=0?'+':'';
    const d    = pos.days_open||0;
    const dc   = d>60?'var(--red)':d>30?'var(--amber)':'var(--text3)';
    const st   = statusInfo(pos);
    return `<tr>
      <td><div class="td-coin"><strong>${pos.coin.replace('/USDT','')}</strong></div></td>
      <td>$${pos.avg_cost.toFixed(4)}</td>
      <td>$${pos.current_price.toFixed(4)}</td>
      <td style="color:${pos.dca_count>0?'var(--purple)':'var(--text3)'};font-weight:700">${pos.dca_count}</td>
      <td style="color:${dc}">${d}d</td>
      <td style="color:${pc};font-weight:700">${sign}${pos.pnl_pct}%</td>
      <td style="color:${pc}">${sign}$${Math.abs(pos.pnl).toFixed(4)}</td>
      <td><span class="badge ${st.cls}">${st.label}</span></td>
      <td><button class="close-btn" onclick="closePos(${pos.id})">&#10005;</button></td>
    </tr>`;
  }).join('');
}
function setBotFilter(type,el){
  botFilter=type;
  document.querySelectorAll('#bots-l2 .f-btn').forEach(b=>b.classList.remove('active'));
  el.classList.add('active');
  applyBotFilter();
}
function sortBd(key){
  if(botSort===key) botSortAsc=!botSortAsc;
  else { botSort=key; botSortAsc=true; }
  applyBotFilter();
}

// ── HISTORY ──
async function fetchHistory() {
  try {
    const res  = await fetch(`${API}/history`);
    allHistory = await res.json();
  } catch(e){ allHistory=[]; }
  buildCoinFilter();
  applyHistoryFilter();
}
function buildCoinFilter() {
  const sel   = document.getElementById('hf-coin');
  const coins = [...new Set(allHistory.map(h=>h.coin).filter(Boolean))];
  sel.innerHTML = '<option value="">All Coins</option>' +
    coins.map(c=>`<option>${c}</option>`).join('');
}
function setDateFilter(type,el){
  histDateFilter=type;
  document.querySelectorAll('.date-preset').forEach(b=>b.classList.remove('active'));
  el.classList.add('active');
  const f=document.getElementById('hf-from');
  const t=document.getElementById('hf-to');
  if(f) f.value='';
  if(t) t.value='';
  applyHistoryFilter();
}
function clearDateRange(){
  document.getElementById('hf-from').value='';
  document.getElementById('hf-to').value='';
  document.querySelectorAll('.date-preset').forEach(b=>b.classList.remove('active'));
  document.querySelectorAll('.date-preset').forEach(b=>{if(b.textContent==='All')b.classList.add('active')});
  histDateFilter='all';
  applyHistoryFilter();
}
function applyHistoryFilter() {
  const exc      = document.getElementById('hf-exchange').value;
  const coin     = document.getElementById('hf-coin').value;
  const fromEl   = document.getElementById('hf-from');
  const toEl     = document.getElementById('hf-to');
  const fromDate = fromEl && fromEl.value ? new Date(fromEl.value) : null;
  const toDate   = toEl   && toEl.value   ? new Date(toEl.value + 'T23:59:59') : null;
  const now      = Date.now();
  let data = allHistory.filter(h => {
    if(exc  && h.exchange !== exc)  return false;
    if(coin && h.coin    !== coin)  return false;
    if(fromDate || toDate){
      const closed = new Date(h.closed_at);
      if(fromDate && closed < fromDate) return false;
      if(toDate   && closed > toDate)   return false;
      return true;
    }
    if(histDateFilter==='today'){
      if(new Date(h.closed_at).toDateString()!==new Date().toDateString()) return false;
    }
    if(histDateFilter==='7d'  && now-new Date(h.closed_at)>7*86400000)  return false;
    if(histDateFilter==='30d' && now-new Date(h.closed_at)>30*86400000) return false;
    return true;
  });
  renderHistory(data);
}
function renderHistory(data) {
  const count = data.length;
  let profit=0, wins=0, totalDays=0;
  data.forEach(h => {
    const p=h.realized_pnl||0;
    profit+=p;
    if(p>0) wins++;
    totalDays+=h.days_held||0;
  });
  const fees = Math.max(0, profit * 0.20);
  const net  = profit - fees;
  document.getElementById('hs-count').textContent     = count;
  document.getElementById('hs-tbl-count').textContent = count+' trades';
  const pe = document.getElementById('hs-profit');
  pe.textContent = (profit>=0?'+':'')+'$'+Math.abs(profit).toFixed(2);
  pe.style.color = profit>=0?'var(--green)':'var(--red)';
  document.getElementById('hs-winrate').textContent = count>0?Math.round(wins/count*100)+'%':'0%';
  document.getElementById('hs-avghold').textContent = count>0?Math.round(totalDays/count)+'d':'—';
  const fe = document.getElementById('hs-fees');
  fe.textContent = '-$'+fees.toFixed(2);
  fe.style.color = fees>0?'var(--amber)':'var(--text3)';
  const ne = document.getElementById('hs-net');
  ne.textContent = (net>=0?'+':'')+'$'+Math.abs(net).toFixed(2);
  ne.style.color = net>=0?'var(--green)':'var(--red)';
  const visibleCols = HISTORY_COLS.filter(c=>c.show);
  document.getElementById('historyThead').innerHTML =
    visibleCols.map(c=>`<th>${c.label}</th>`).join('');
  const tbody = document.getElementById('historyTable');
  if(!count){
    tbody.innerHTML=`<tr><td colspan="${visibleCols.length}"><div class="empty"><div class="empty-icon">&#128202;</div><div class="empty-text">No closed trades yet.</div></div></td></tr>`;
    return;
  }
  tbody.innerHTML = data.map(h => {
    const pnl  = h.realized_pnl||0;
    const pc   = pnl>=0?'var(--green)':'var(--red)';
    const sign = pnl>=0?'+':'';
    const ep   = h.entry_price||0;
    const xp   = h.exit_price||ep;
    const pct  = ep>0?((xp-ep)/ep*100).toFixed(2):'0.00';
    return `<tr>${visibleCols.map(c=>{
      if(c.key==='coin')        return `<td><div class="td-coin"><strong>${(h.coin||'—').replace('/USDT','')}</strong></div></td>`;
      if(c.key==='exchange')    return `<td><span class="td-muted">${h.exchange||'MEXC'}</span></td>`;
      if(c.key==='entry_date')  return `<td><span class="td-muted">${h.opened_at?new Date(h.opened_at+'Z').toLocaleDateString('en-SA',{timeZone:'Asia/Riyadh'}):'—'}</span></td>`;
      if(c.key==='exit_date')   return `<td><span class="td-muted">${h.closed_at?new Date(h.closed_at+'Z').toLocaleDateString('en-SA',{timeZone:'Asia/Riyadh'}):'—'}</span></td>`;
      if(c.key==='entry_price') return `<td>$${ep.toFixed(4)}</td>`;
      if(c.key==='avg_cost')    return `<td>$${(h.avg_cost||ep).toFixed(4)}</td>`;
      if(c.key==='exit_price')  return `<td>$${xp.toFixed(4)}</td>`;
      if(c.key==='dca_count')   return `<td style="color:var(--purple)">${h.dca_count||0}</td>`;
      if(c.key==='pnl_pct')     return `<td style="color:${pc};font-weight:600">${sign}${pct}%</td>`;
      if(c.key==='pnl_usd')     return `<td style="color:${pc};font-weight:700">${sign}$${Math.abs(pnl).toFixed(4)}</td>`;
      if(c.key==='hold')        return `<td><span class="td-muted">${h.days_held||0}d</span></td>`;
      if(c.key==='exit_reason') return `<td><span class="badge badge-closed">${h.exit_reason||'closed'}</span></td>`;
      if(c.key==='fee'){const p=h.realized_pnl||0;const f=Math.max(0,p*0.20);return `<td style="color:var(--amber)">-$${f.toFixed(4)}</td>`;}
      if(c.key==='net_profit'){const p=h.realized_pnl||0;const n=p-Math.max(0,p*0.20);const nc=n>=0?'var(--green)':'var(--red)';const sg=n>=0?'+':'';return `<td style="color:${nc};font-weight:700">${sg}$${Math.abs(n).toFixed(4)}</td>`;}
      return '<td>—</td>';
    }).join('')}</tr>`;
  }).join('');
}
function buildColumnToggles() {
  document.getElementById('columnToggles').innerHTML =
    HISTORY_COLS.map((c,i)=>`
    <label style="display:flex;align-items:center;gap:6px;padding:5px 10px;background:var(--bg3);border-radius:7px;cursor:pointer;font-size:11px;color:var(--text2)">
      <input type="checkbox" ${c.show?'checked':''} onchange="toggleCol(${i},this.checked)" style="accent-color:var(--accent)">
      ${c.label}
    </label>`).join('');
}
function toggleColumnPicker(){
  const el=document.getElementById('columnPicker');
  el.style.display=el.style.display==='none'?'block':'none';
}
function toggleCol(i,show){ HISTORY_COLS[i].show=show; applyHistoryFilter(); }

// ── SETTINGS ──
function renderSettings() {
  const excCount = getExchanges().length;
  const setExc   = document.getElementById('set-exc-count');
  if(setExc) setExc.textContent = `${excCount} connected`;
}
function editField(field) {
  const labels = {email:'New Email Address',phone:'New Phone Number (+966...)',password:'New Password'};
  const val = prompt(labels[field]||field);
  if(!val) return;
  if(field==='email') document.getElementById('set-email').textContent = val;
  if(field==='phone') document.getElementById('set-phone').textContent = val;
  alert('&#10003; Updated! (Full backend auth - Phase 6)');
}
function toggle2FA() {
  const t  = document.getElementById('toggle2fa');
  const th = document.getElementById('thumb2fa');
  const on = th.style.left === '22px';
  if(on){ t.style.background='var(--text3)'; th.style.left='3px'; }
  else  { t.style.background='var(--accent)'; th.style.left='22px'; }
}
function toggleNotif(id) {
  const cap = id.charAt(0).toUpperCase()+id.slice(1);
  const t   = document.getElementById('toggle'+cap);
  const th  = document.getElementById('thumb'+cap);
  const on  = th.style.left === '22px';
  if(on){ t.style.background='var(--text3)'; th.style.left='3px'; }
  else  { t.style.background='var(--accent)'; th.style.left='22px'; }
  if(id==='telegram'){
    document.getElementById('telegramSetup').style.display = on ? 'none' : 'flex';
  }
}
function openFeatureRequest() { document.getElementById('featureModal').classList.add('open'); }
function submitFeature() {
  const text = document.getElementById('featureText').value.trim();
  if(!text){ alert('Please describe the feature'); return; }
  document.getElementById('featureModal').classList.remove('open');
  document.getElementById('featureText').value = '';
  alert('&#10003; Feature request submitted! Thank you.');
}

// ── POSITIONS ──
async function closePos(id) {
  if(!confirm('Close this position?')) return;
  await fetch(`${API}/positions/${id}/close`,{method:'POST'});
  await fetchPositions();
}

// ── EXCHANGE DETAIL ──
let currentExcId  = null;
let capitalChart  = null;
let chartRange    = '7d';
let allBalHistory = [];

function openExcDetail(excId) {
  currentExcId = excId;
  const cfg  = EXC[excId] || {};
  const exc  = getExchanges().find(e => e.id === excId) || {};
  const name = exc.name || cfg.name || excId;
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  document.getElementById('tab-excdetail').classList.add('active');
  document.getElementById('pageTitle').textContent = name;
  document.getElementById('excDetailName').textContent = name;
  const inv      = allPositions.reduce((s,p) => s + p.total_invested, 0);
  const pnl      = allPositions.reduce((s,p) => s + p.pnl, 0);
  const open     = allPositions.length;
  const pnlSign  = pnl >= 0 ? '+' : '';
  const pnlColor = pnl >= 0 ? 'var(--green)' : 'var(--red)';
  document.getElementById('exc-capital').textContent = '$' + inv.toFixed(2);
  document.getElementById('exc-open').textContent    = open;
  const profEl = document.getElementById('exc-profit');
  profEl.textContent = pnlSign + '$' + Math.abs(pnl).toFixed(2);
  profEl.style.color = pnlColor;
  const pnlEl = document.getElementById('exc-pnl');
  pnlEl.textContent = pnlSign + '$' + Math.abs(pnl).toFixed(2);
  pnlEl.style.color = pnlColor;
  const botRunning = document.getElementById('btcPrice').textContent !== 'Offline';
  document.getElementById('excDetailBots').innerHTML = `
    <div class="bot-section" style="margin-bottom:14px">
      <div class="bot-cards-list">
        <div class="bot-row" onclick="openBotDetail('DCA Long - All Coins',${botRunning})">
          <div class="bot-row-left">
            <div class="bot-indicator ${botRunning?'live':'off'}"></div>
            <div class="bot-row-info">
              <div class="bot-row-name">DCA Long - All Coins</div>
              <div class="bot-row-meta">
                <div class="bot-meta">Trades: <span>${open}</span></div>
                <div class="bot-meta">P&amp;L: <span style="color:${pnlColor}">${pnlSign}$${Math.abs(pnl).toFixed(2)}</span></div>
              </div>
            </div>
          </div>
          <span class="bot-arrow">&#8250;</span>
        </div>
      </div>
    </div>`;
  fetchBalanceHistory(excId);
}

function closeExcDetail() {
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  document.getElementById('tab-home').classList.add('active');
  document.getElementById('pageTitle').textContent = 'Home';
  document.querySelectorAll('.nav-link').forEach(n => n.classList.remove('active'));
  document.querySelector('.nav-link').classList.add('active');
}

async function fetchBalanceHistory(excId) {
  try {
    const res     = await fetch(`${API}/balance-history?exchange_id=${excId}&days=30`);
    allBalHistory = await res.json();
  } catch(e){ allBalHistory=[]; }
  if(allBalHistory.length === 0){
    const base = allPositions.reduce((s,p) => s + p.total_invested, 0) || 100;
    const now  = Date.now();
    allBalHistory = Array.from({length:14}, (_,i) => ({
      date:  new Date(now - (13-i)*86400000).toISOString().split('T')[0],
      value: parseFloat((base * (0.95 + Math.random()*0.1)).toFixed(2)),
    }));
    allBalHistory[allBalHistory.length-1].value = parseFloat(base.toFixed(2));
  }
  renderChart(chartRange);
}

function setChartRange(range, el) {
  chartRange = range;
  document.querySelectorAll('#tab-excdetail .f-btn').forEach(b => b.classList.remove('active'));
  el.classList.add('active');
  renderChart(range);
}

function renderChart(range) {
  let data = [...allBalHistory];
  if(range === '7d')  data = data.slice(-7);
  if(range === '30d') data = data.slice(-30);
  const labels = data.map(d => d.date || (d.recorded_at||'').split('T')[0] || '—');
  const values = data.map(d => d.value || d.value_usdt || 0);
  const first  = values[0] || 0;
  const last   = values[values.length-1] || 0;
  const color  = last >= first ? '#10D98A' : '#F4645F';
  const ctx    = document.getElementById('capitalChart').getContext('2d');
  if(capitalChart) capitalChart.destroy();
  capitalChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        data: values,
        borderColor: color,
        borderWidth: 2,
        backgroundColor: color + '18',
        fill: true,
        tension: 0.4,
        pointRadius: 3,
        pointHoverRadius: 6,
        pointBackgroundColor: color,
        pointBorderColor: '#07070F',
        pointBorderWidth: 2,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {mode:'index',intersect:false},
      plugins: {
        legend: {display:false},
        tooltip: {
          backgroundColor: '#0E0E1C',
          borderColor: '#252540',
          borderWidth: 1,
          titleColor: '#8888AA',
          bodyColor: '#F0F0FF',
          titleFont: {family:'Inter',size:10},
          bodyFont:  {family:'Inter',size:13,weight:'700'},
          padding: 10,
          callbacks: {
            title: items => items[0]?.label || '',
            label: item  => ' $' + parseFloat(item.raw).toFixed(2),
          }
        }
      },
      scales: {
        x: {
          grid:   {color:'#1E1E3520'},
          ticks:  {color:'#55556A',font:{family:'Inter',size:9},maxTicksLimit:7},
          border: {display:false}
        },
        y: {
          grid:   {color:'#1E1E3530'},
          ticks:  {color:'#55556A',font:{family:'Inter',size:9},callback:v=>'$'+v.toFixed(0)},
          border: {display:false}
        }
      }
    }
  });
}

// ── MAIN LOOP ──
async function loadAll() {
  await fetchStatus();
  await fetchPositions();
}
loadAll();
setInterval(loadAll, 15000);
</script>
</body>
</html>'''

with open('dashboard.html', 'w', encoding='utf-8') as f:
    f.write(HTML)

lines = HTML.count('\n') + 1
print(f'dashboard.html written — {lines} lines')
