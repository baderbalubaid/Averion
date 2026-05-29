import shutil
shutil.copy("dashboard.html","dashboard_backup2.html")
h=open("dashboard.html","r",encoding="utf-8").read()
print("Read:",len(h))
css="""
/* BOTS FLAT LIST v4.5 */
.bots-topbar{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;gap:10px;flex-wrap:wrap}
.bots-title-wrap{display:flex;flex-direction:column}
.bots-main-title{font-size:20px;font-weight:800;letter-spacing:-0.3px}
.bots-subtitle{font-size:11px;color:var(--text3);margin-top:2px}
.bots-topbar-right{display:flex;align-items:center;gap:8px}
.bots-search{padding:8px 14px;background:var(--bg2);border:1px solid var(--border);border-radius:9px;color:var(--text);font-size:12px;font-family:Inter,sans-serif;outline:none;width:200px}
.bots-filter-bar{display:flex;gap:8px;margin-bottom:14px;flex-wrap:wrap;align-items:center}
.bots-filter-sel{padding:7px 12px;background:var(--bg2);border:1px solid var(--border);border-radius:8px;color:var(--text2);font-size:12px;font-family:Inter,sans-serif;outline:none;cursor:pointer}
.bots-flat-table{background:var(--bg2);border:1px solid var(--border);border-radius:16px;overflow:hidden;margin-bottom:14px}
.bots-flat-hdr{display:grid;grid-template-columns:2fr 70px 80px 110px 80px 150px 44px;padding:10px 16px;background:var(--bg3);border-bottom:1px solid var(--border)}
.bots-col-hdr{font-size:9px;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:0.8px}
.bots-flat-row{display:grid;grid-template-columns:2fr 70px 80px 110px 80px 150px 44px;padding:12px 16px;border-bottom:1px solid var(--border);align-items:center;transition:background 0.15s;cursor:pointer}
.bots-flat-row:last-child{border-bottom:none}
.bots-flat-row:hover{background:#6366F106}
.bot-flat-name-wrap{display:flex;align-items:center;gap:10px}
.bot-flat-indicator{width:7px;height:7px;border-radius:50%;flex-shrink:0}
.bot-flat-indicator.live{background:var(--green);box-shadow:0 0 6px #10D98A60}
.bot-flat-indicator.off{background:var(--text3)}
.bot-flat-name{font-size:12px;font-weight:700;margin-bottom:2px}
.bot-flat-sub{font-size:10px;color:var(--text3)}
.exc-badge{padding:2px 6px;border-radius:5px;font-size:9px;font-weight:800;display:inline-block}
.exc-badge.mexc{background:#38BDF820;color:#38BDF8}
.exc-badge.binance{background:#F59E0B20;color:#F59E0B}
.exc-badge.kucoin{background:#10D98A20;color:#10D98A}
.exc-badge.okx{background:#E2E8F020;color:#E2E8F0}
.exc-badge.gateio{background:#38BDF815;color:#38BDF8}
.exc-badge.bybit{background:#FB923C20;color:#FB923C}
.exc-badge.bitget{background:#A78BFA20;color:#A78BFA}
.bot-mode-badge{padding:3px 8px;border-radius:20px;font-size:9px;font-weight:700;display:inline-block}
.bot-mode-live{background:#10D98A15;color:var(--green);border:1px solid #10D98A25}
.bot-mode-paper{background:#38BDF815;color:#38BDF8;border:1px solid #38BDF825}
.toggle-pair{display:flex;gap:8px;align-items:center}
.toggle-mini-wrap{display:flex;flex-direction:column;align-items:center;gap:2px}
.toggle-mini-lbl{font-size:8px;color:var(--text3);font-weight:600;text-transform:uppercase}
.toggle-mini{width:36px;height:20px;border-radius:10px;border:none;cursor:pointer;position:relative;transition:background 0.2s;flex-shrink:0}
.toggle-mini-thumb{width:14px;height:14px;background:#fff;border-radius:50%;position:absolute;top:3px;transition:left 0.2s}
.bot-kebab{width:30px;height:30px;background:var(--bg3);border:1px solid var(--border);border-radius:7px;display:flex;align-items:center;justify-content:center;cursor:pointer;font-size:14px;color:var(--text2);transition:all 0.15s}
.bot-kebab:hover{border-color:var(--accent);color:var(--accent)}
.bots-footer{padding:12px 16px;border-top:1px solid var(--border);font-size:11px;color:var(--text3);text-align:center}
@media(max-width:767px){.bots-flat-hdr{display:none}.bots-flat-row{grid-template-columns:1fr auto;row-gap:6px;padding:12px 14px}.bots-exch-cell,.bots-trades-cell{display:none}.bots-search{width:130px}}
"""
h=h.replace("</style>",css+"</style>",1)
print("CSS done")
# Replace bots tab HTML
i1=h.find("BOTS TAB")
i2=h.find("HISTORY TAB")
print("markers:",i1,i2)
html_new="""    <!-- BOTS TAB -->
    <div class="tab-content" id="tab-bots">
      <div id="bots-l1">
        <div class="bots-topbar">
          <div class="bots-title-wrap">
            <div class="bots-main-title">Bots</div>
            <div class="bots-subtitle" id="botsSubtitle">0 bots</div>
          </div>
          <div class="bots-topbar-right">
            <input class="bots-search" id="botsSearch" placeholder="Search bots..." oninput="renderBotsFlat()">
            <button class="btn btn-accent btn-sm" onclick="alert(chr(39)Bot wizard - Phase 5chr(39))">+ Create Bot</button>
          </div>
        </div>
        <div class="bots-filter-bar">
          <select class="bots-filter-sel" id="botsFilterStatus" onchange="renderBotsFlat()">
            <option value="">All Status</option>
            <option value="running">Running</option>
            <option value="stopped">Stopped</option>
            <option value="live">Live</option>
            <option value="paper">Paper</option>
          </select>
          <select class="bots-filter-sel" id="botsFilterExch" onchange="renderBotsFlat()">
            <option value="">All Exchanges</option>
            <option value="mexc">MEXC</option>
            <option value="binance">Binance</option>
            <option value="kucoin">KuCoin</option>
            <option value="okx">OKX</option>
            <option value="gateio">Gate.io</option>
            <option value="bybit">Bybit</option>
            <option value="bitget">Bitget</option>
          </select>
          <select class="bots-filter-sel" id="botsFilterSort" onchange="renderBotsFlat()">
            <option value="pnl">Sort: PnL</option>
            <option value="trades">Sort: Trades</option>
            <option value="name">Sort: Name</option>
          </select>
        </div>
        <div class="bots-flat-table">
          <div class="bots-flat-hdr">
            <div class="bots-col-hdr">BOT</div>
            <div class="bots-col-hdr">EXCH</div>
            <div class="bots-col-hdr">TRADES</div>
            <div class="bots-col-hdr">PnL</div>
            <div class="bots-col-hdr">MODE</div>
            <div class="bots-col-hdr">CONTROLS</div>
            <div class="bots-col-hdr">...</div>
          </div>
          <div id="botsFlatList"><div class="loading">Loading...</div></div>
          <div class="bots-footer" id="botsFooter">0 bots</div>
        </div>
      </div>
      <div id="bots-l2" style="display:none;margin:-24px">
        <div class="bot-detail-hdr">
          <div class="bot-detail-back" onclick="backToBots()">Back</div>
          <div class="bot-detail-title" id="bdTitle">Bot</div>
          <div class="bot-detail-badge" id="bdBadge">Live</div>
        </div>
        <div class="stats4">
          <div class="stat4"><div class="stat4-lbl">Open</div><div class="stat4-val" id="bd-open" style="color:var(--blue)">0</div></div>
          <div class="stat4"><div class="stat4-lbl">Invested</div><div class="stat4-val" id="bd-inv" style="color:var(--purple)">0</div></div>
          <div class="stat4"><div class="stat4-lbl">PnL</div><div class="stat4-val" id="bd-pnl">0</div></div>
          <div class="stat4"><div class="stat4-lbl">PnL%</div><div class="stat4-val" id="bd-pnlpct">0%</div></div>
        </div>
        <div style="display:flex;gap:8px;padding:0 14px 12px">
          <button class="btn btn-red btn-sm" id="bdToggleBtn" onclick="toggleBot()">Stop Bot</button>
          <button class="btn btn-ghost btn-sm" onclick="applyBotFilter()">Refresh</button>
        </div>
        <div class="search-wrap"><input class="search-input" id="bdSearch" onkeyup="applyBotFilter()" placeholder="Search coin..."></div>
        <div class="filter-bar">
          <button class="f-btn active" onclick="setBotFilter(chr(39)allchr(39),this)">All</button>
          <button class="f-btn" onclick="setBotFilter(chr(39)profitchr(39),this)">Profit</button>
          <button class="f-btn" onclick="setBotFilter(chr(39)losschr(39),this)">Loss</button>
          <button class="f-btn" onclick="setBotFilter(chr(39)dcachr(39),this)">DCAd</button>
          <button class="f-btn" onclick="setBotFilter(chr(39)stuckchr(39),this)">Stuck</button>
          <button class="f-btn" onclick="setBotFilter(chr(39)tpchr(39),this)">TP Armed</button>
        </div>
        <div class="tbl-container">
          <div class="tbl-hdr"><span class="tbl-title">Positions</span><span class="tbl-count" id="bd-count">0 open</span></div>
          <table><thead><tr>
            <th onclick="sortBd(chr(39)coinchr(39))">Coin</th><th>Avg</th><th>Price</th>
            <th onclick="sortBd(chr(39)dca_countchr(39))">DCA</th>
            <th onclick="sortBd(chr(39)days_openchr(39))">Days</th>
            <th onclick="sortBd(chr(39)pnl_pctchr(39))">PnL%</th>
            <th onclick="sortBd(chr(39)pnlchr(39))">PnL</th>
            <th>Status</th><th>X</th>
          </tr></thead>
          <tbody id="bdTable"></tbody></table>
        </div>
      </div>
    </div>
"""
html_new=html_new.replace("chr(39)",chr(39))
idx1=h.find("    <!-- BOTS TAB")
idx2=h.find("    <!-- HISTORY TAB")
print("idx1=",idx1,"idx2=",idx2)
if idx1>0 and idx2>0:
    h=h[:idx1]+html_new+"    <!-- HISTORY TAB"+h[idx2+len("    <!-- HISTORY TAB"):]
    print("HTML replaced")
else:
    print("ERROR markers not found")