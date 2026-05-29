# Averion — Item 24: Bots tab flat list redesign
# Run in Replit terminal: python patch_dashboard.py

import shutil

# Backup
shutil.copy('dashboard.html', 'dashboard_backup.html')
print("Backup created: dashboard_backup.html")

with open('dashboard.html', 'r', encoding='utf-8') as f:
    h = f.read()

# ── 1. ADD CSS before </style> ──────────────────────────
CSS = """
/* ── BOTS FLAT LIST v4.5 ── */
.bots-topbar{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;gap:10px;flex-wrap:wrap}
.bots-title-wrap{display:flex;flex-direction:column}
.bots-main-title{font-size:20px;font-weight:800;letter-spacing:-0.3px}
.bots-subtitle{font-size:11px;color:var(--text3);margin-top:2px}
.bots-topbar-right{display:flex;align-items:center;gap:8px}
.bots-search{padding:8px 14px;background:var(--bg2);border:1px solid var(--border);border-radius:9px;color:var(--text);font-size:12px;font-family:'Inter',sans-serif;outline:none;transition:border-color 0.2s;width:200px}
.bots-search:focus{border-color:var(--accent)}
.bots-search::placeholder{color:var(--text3)}
.bots-filter-bar{display:flex;gap:8px;margin-bottom:14px;flex-wrap:wrap;align-items:center}
.bots-filter-sel{padding:7px 12px;background:var(--bg2);border:1px solid var(--border);border-radius:8px;color:var(--text2);font-size:12px;font-family:'Inter',sans-serif;outline:none;cursor:pointer;transition:border-color 0.2s}
.bots-filter-sel:focus{border-color:var(--accent)}
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
.toggle-mini-lbl{font-size:8px;color:var(--text3);font-weight:600;text-transform:uppercase;letter-spacing:0.3px}
.toggle-mini{width:36px;height:20px;border-radius:10px;border:none;cursor:pointer;position:relative;transition:background 0.2s;flex-shrink:0}
.toggle-mini-thumb{width:14px;height:14px;background:#fff;border-radius:50%;position:absolute;top:3px;transition:left 0.2s}
.bot-kebab{width:30px;height:30px;background:var(--bg3);border:1px solid var(--border);border-radius:7px;display:flex;align-items:center;justify-content:center;cursor:pointer;font-size:14px;color:var(--text2);transition:all 0.15s}
.bot-kebab:hover{border-color:var(--accent);color:var(--accent)}
.bots-footer{padding:12px 16px;border-top:1px solid var(--border);font-size:11px;color:var(--text3);text-align:center}
@media(max-width:767px){
  .bots-flat-hdr{display:none}
  .bots-flat-row{grid-template-columns:1fr auto;row-gap:6px;padding:12px 14px}
  .bots-exch-cell,.bots-trades-cell{display:none}
  .bots-search{width:130px}
  .bots-main-title{font-size:17px}
}
"""
if '/* ── BOTS FLAT LIST v4.5 ── */' in h:
    print("CSS already added, skipping")
else:
    h = h.replace('</style>', CSS + '</style>', 1)
    print("CSS added")

# ── 2. REPLACE BOTS TAB HTML ────────────────────────────
NEW_HTML = """    <!-- \u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550 BOTS TAB \u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550 -->
    <div class="tab-content" id="tab-bots">
      <div id="bots-l1">
        <div class="bots-topbar">
          <div class="bots-title-wrap">
            <div class="bots-main-title">Bots</div>
            <div class="bots-subtitle" id="botsSubtitle">0 bots</div>
          </div>
          <div class="bots-topbar-right">
            <input class="bots-search" id="botsSearch" placeholder="Search bots..." oninput="renderBotsFlat()">
            <button class="btn btn-accent btn-sm" onclick="alert('Bot creation wizard - Phase 5')">+ Create Bot</button>
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
            <option value="pnl">Sort: P&amp;L%</option>
            <option value="trades">Sort: Trades</option>
            <option value="name">Sort: Name</option>
          </select>
        </div>
        <div class="bots-flat-table">
          <div class="bots-flat-hdr">
            <div class="bots-col-hdr">BOT</div>
            <div class="bots-col-hdr">EXCH</div>
            <div class="bots-col-hdr">TRADES</div>
            <div class="bots-col-hdr">P&amp;L</div>
            <div class="bots-col-hdr">MODE</div>
            <div class="bots-col-hdr">CONTROLS</div>
            <div class="bots-col-hdr">&#8943;</div>
          </div>
          <div id="botsFlatList"><div class="loading">Loading...</div></div>
          <div class="bots-footer" id="botsFooter">Showing 0 bots</div>
        </div>
      </div>
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
          <button class="btn btn-red btn-sm" id="bdToggleBtn" onclick="toggleBot()">&#9635; Stop Bot</button>
          <button class="btn btn-ghost btn-sm" onclick="applyBotFilter()">&#8635; Refresh</button>
        </div>
        <div class="search-wrap">
          <input class="search-input" id="bdSearch" onkeyup="applyBotFilter()" placeholder="Search coin...">
        </div>
        <div class="filter-bar">
          <button class="f-btn active" onclick="setBotFilter('all',this)">All</button>
          <button class="f-btn" onclick="setBotFilter('profit',this)">Profit</button>
          <button class="f-btn" onclick="setBotFilter('loss',this)">Loss</button>
          <button class="f-btn" onclick="setBotFilter('dca',this)">DCA'd</button>
          <button class="f-btn" onclick="setBotFilter('stuck',this)">Stuck</button>
          <button class="f-btn" onclick="setBotFilter('tp',this)">TP Armed</button>
        </div>
        <div class="tbl-container">
          <div class="tbl-hdr">
            <span class="tbl-title">Positions</span>
            <span class="tbl-count" id="bd-count">0 open</span>
          </div>
          <table>
            <thead><tr>
              <th onclick="sortBd('coin')">Coin</th>
              <th>Avg Cost</th><th>Current</th>
              <th onclick="sortBd('dca_count')">DCA#</th>
              <th onclick="sortBd('days_open')">Days</th>
              <th onclick="sortBd('pnl_pct')">P&amp;L%</th>
              <th onclick="sortBd('pnl')">P&amp;L$</th>
              <th>Status</th><th>Action</th>
            </tr></thead>
            <tbody id="bdTable"><tr><td colspan="9" class="loading">Loading...</td></tr></tbody>
          </table>
        </div>
      </div>
    </div>
"""

OLD_START = '    <!-- \u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550 BOTS TAB \u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550 -->'
OLD_END   = '    <!-- \u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550 HISTORY TAB \u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550 -->'

i1 = h.find(OLD_START)
i2 = h.find(OLD_END)
if i1 == -1 or i2 == -1:
    print("ERROR: Could not find BOTS TAB markers in HTML!")
    print("i1=%d i2=%d" % (i1, i2))
else:
    h = h[:i1] + NEW_HTML + '\n    ' + h[i2:]
    print("Bots tab HTML replaced")

# ── 3. REPLACE BOTS JS ──────────────────────────────────
NEW_JS = """
// ── BOTS FLAT LIST v4.5 ──────────────────────────────────
const EXC_BADGE = {
  mexc:    {label:'M',  cls:'mexc',    name:'MEXC'},
  binance: {label:'B',  cls:'binance', name:'Binance'},
  kucoin:  {label:'K',  cls:'kucoin',  name:'KuCoin'},
  okx:     {label:'O',  cls:'okx',     name:'OKX'},
  gateio:  {label:'G',  cls:'gateio',  name:'Gate.io'},
  bybit:   {label:'By', cls:'bybit',   name:'Bybit'},
  bitget:  {label:'Bg', cls:'bitget',  name:'Bitget'},
};
let botStates = {};
function getBotState(id){if(!botStates[id])botStates[id]={trading:true,dca:true};return botStates[id];}
function renderBotsList(){renderBotsFlat();}
function renderBotsFlat(){
  const exchanges=getExchanges();
  const search=(document.getElementById('botsSearch')?.value||'').toLowerCase();
  const fExch=document.getElementById('botsFilterExch')?.value||'';
  const fStat=document.getElementById('botsFilterStatus')?.value||'';
  const sortBy=document.getElementById('botsFilterSort')?.value||'pnl';
  const sub=document.getElementById('botsSubtitle');
  const foot=document.getElementById('botsFooter');
  const list=document.getElementById('botsFlatList');
  if(!exchanges.length){
    list.innerHTML='<div class="empty" style="padding:40px"><div class="empty-icon">&#128268;</div><div class="empty-text">No exchanges connected.<br>Add one from Home tab.</div></div>';
    if(sub)sub.textContent='0 bots';
    if(foot)foot.textContent='No bots yet';
    return;
  }
  const pnl=allPositions.reduce((s,p)=>s+p.pnl,0);
  const inv=allPositions.reduce((s,p)=>s+p.total_invested,0);
  const isRunning=document.getElementById('btcPrice')?.textContent!=='Offline';
  let bots=exchanges.map(exc=>({
    id:exc.id+'_bot1',excId:exc.id,
    excName:exc.name||EXC_BADGE[exc.id]?.name||exc.id,
    name:'DCA Long - All Coins',
    trades:allPositions.length,pnl:pnl,
    pnlPct:inv>0?(pnl/inv*100):0,
    mode:'paper',running:isRunning,
  }));
  bots=bots.filter(b=>{
    if(search&&!b.name.toLowerCase().includes(search)&&!b.excName.toLowerCase().includes(search))return false;
    if(fExch&&b.excId!==fExch)return false;
    if(fStat==='running'&&!b.running)return false;
    if(fStat==='stopped'&&b.running)return false;
    if(fStat==='live'&&b.mode!=='live')return false;
    if(fStat==='paper'&&b.mode!=='paper')return false;
    return true;
  });
  if(sortBy==='pnl')   bots.sort((a,b)=>b.pnlPct-a.pnlPct);
  if(sortBy==='trades')bots.sort((a,b)=>b.trades-a.trades);
  if(sortBy==='name')  bots.sort((a,b)=>a.name.localeCompare(b.name));
  const running=bots.filter(b=>b.running).length;
  if(sub)sub.textContent=bots.length+' bot'+(bots.length!==1?'s':'')+' \u00b7 '+running+' running';
  if(foot)foot.textContent='Showing '+bots.length+' of '+exchanges.length+' bot'+(exchanges.length!==1?'s':'');
  if(!bots.length){
    list.innerHTML='<div class="empty" style="padding:32px"><div class="empty-icon">&#128269;</div><div class="empty-text">No bots match your filters</div></div>';
    return;
  }
  list.innerHTML=bots.map(function(bot){
    var badge=EXC_BADGE[bot.excId]||{label:'?',cls:'',name:bot.excId};
    var state=getBotState(bot.id);
    var pc=bot.pnl>=0?'var(--green)':'var(--red)';
    var sign=bot.pnl>=0?'+':'';
    var pctStr=(bot.pnlPct>=0?'+':'')+Math.abs(bot.pnlPct).toFixed(2)+'%';
    var tBg=state.trading?'var(--green)':'var(--text3)';
    var tLeft=state.trading?'19px':'3px';
    var dBg=state.dca?'var(--green)':'var(--text3)';
    var dLeft=state.dca?'19px':'3px';
    return '<div class="bots-flat-row" onclick="openBotDetail(\''+bot.name+'\','+bot.running+')">'
      +'<div class="bot-flat-name-wrap">'
        +'<div class="bot-flat-indicator '+(bot.running?'live':'off')+'"></div>'
        +'<div><div class="bot-flat-name">'+bot.name+'</div><div class="bot-flat-sub">'+bot.excName+'</div></div>'
      +'</div>'
      +'<div class="bots-exch-cell"><span class="exc-badge '+badge.cls+'">['+badge.label+']</span></div>'
      +'<div class="bots-trades-cell" style="font-size:13px;font-weight:700;color:var(--blue)">'+bot.trades+'</div>'
      +'<div class="bots-pnl-cell">'
        +'<div style="font-size:12px;font-weight:700;color:'+pc+'">'+sign+'$'+Math.abs(bot.pnl).toFixed(2)+'</div>'
        +'<div style="font-size:10px;color:'+pc+'">'+pctStr+'</div>'
      +'</div>'
      +'<div class="bots-mode-cell"><span class="bot-mode-badge '+(bot.mode==='live'?'bot-mode-live':'bot-mode-paper')+'">'+(bot.mode==='live'?'LIVE':'PAPER')+'</span></div>'
      +'<div onclick="event.stopPropagation()">'
        +'<div class="toggle-pair">'
          +'<div class="toggle-mini-wrap">'
            +'<span class="toggle-mini-lbl">T</span>'
            +'<button class="toggle-mini" id="tT_'+bot.id+'" style="background:'+tBg+'" onclick="toggleBotTrading(\''+bot.id+'\')">'
              +'<div class="toggle-mini-thumb" id="thT_'+bot.id+'" style="left:'+tLeft+'"></div>'
            +'</button>'
          +'</div>'
          +'<div class="toggle-mini-wrap">'
            +'<span class="toggle-mini-lbl">DCA</span>'
            +'<button class="toggle-mini" id="tD_'+bot.id+'" style="background:'+dBg+'" onclick="toggleBotDCA(\''+bot.id+'\')">'
              +'<div class="toggle-mini-thumb" id="thD_'+bot.id+'" style="left:'+dLeft+'"></div>'
            +'</button>'
          +'</div>'
        +'</div>'
      +'</div>'
      +'<div style="display:flex;justify-content:flex-end" onclick="event.stopPropagation()">'
        +'<div class="dropdown">'
          +'<div class="bot-kebab" onclick="toggleDropdown(event,\'dd-bot-'+bot.id+'\')">&#8943;</div>'
          +'<div class="dropdown-menu" id="dd-bot-'+bot.id+'" style="right:0;min-width:160px">'
            +'<div class="dropdown-item" onclick="editBot(event,\''+bot.id+'\')">&#9999;&nbsp; Edit bot</div>'
            +'<div class="dropdown-item" onclick="duplicateBot(event,\''+bot.id+'\',\''+bot.name+'\')">&#10697;&nbsp; Duplicate</div>'
            +'<div class="dropdown-item danger" onclick="deleteBot(event,\''+bot.id+'\')">&#10005;&nbsp; Delete</div>'
          +'</div>'
        +'</div>'
      +'</div>'
    +'</div>';
  }).join('');
}
function toggleBotTrading(id){
  var s=getBotState(id);s.trading=!s.trading;
  var b=document.getElementById('tT_'+id),t=document.getElementById('thT_'+id);
  if(b&&t){b.style.background=s.trading?'var(--green)':'var(--text3)';t.style.left=s.trading?'19px':'3px';}
}
function toggleBotDCA(id){
  var s=getBotState(id);s.dca=!s.dca;
  var b=document.getElementById('tD_'+id),t=document.getElementById('thD_'+id);
  if(b&&t){b.style.background=s.dca?'var(--green)':'var(--text3)';t.style.left=s.dca?'19px':'3px';}
}
function editBot(e,id){e.stopPropagation();document.querySelectorAll('.dropdown-menu').forEach(function(m){m.classList.remove('open');});alert('Edit bot - Phase 5');}
function duplicateBot(e,id,name){e.stopPropagation();document.querySelectorAll('.dropdown-menu').forEach(function(m){m.classList.remove('open');});alert('Duplicate: '+name+' - Phase 5');}
function deleteBot(e,id){e.stopPropagation();document.querySelectorAll('.dropdown-menu').forEach(function(m){m.classList.remove('open');});if(!confirm('Delete this bot?'))return;alert('Bot deleted - Phase 5');}
async function startBotInList(e){e.stopPropagation();await fetch(API+'/start',{method:'POST'});setTimeout(function(){fetchPositions();renderBotsFlat();},1000);}
async function stopBotInList(e){e.stopPropagation();await fetch(API+'/stop',{method:'POST'});setTimeout(function(){renderBotsFlat();},1000);}
function openBotDetail(name,running){currentBotRunning=running;document.getElementById('bots-l1').style.display='none';document.getElementById('bots-l2').style.display='block';document.getElementById('bdTitle').textContent=name;updateBdHeader();applyBotFilter();}
function backToBots(){document.getElementById('bots-l1').style.display='block';document.getElementById('bots-l2').style.display='none';renderBotsFlat();}
function updateBdHeader(){var badge=document.getElementById('bdBadge'),btn=document.getElementById('bdToggleBtn');if(currentBotRunning){badge.textContent='Live';badge.className='bot-detail-badge';btn.textContent='Stop Bot';btn.className='btn btn-red btn-sm';}else{badge.textContent='Stopped';badge.className='bot-detail-badge off';btn.textContent='Start Bot';btn.className='btn btn-green btn-sm';}}
async function toggleBot(){if(currentBotRunning)await fetch(API+'/stop',{method:'POST'});else await fetch(API+'/start',{method:'POST'});currentBotRunning=!currentBotRunning;updateBdHeader();}
function applyBotFilter(){var search=(document.getElementById('bdSearch')?.value||'').toLowerCase();var data=allPositions.filter(function(p){if(!p.coin.toLowerCase().includes(search))return false;var d=p.days_open||0;if(botFilter==='profit')return p.pnl>=0;if(botFilter==='loss')return p.pnl<0;if(botFilter==='dca')return p.dca_count>0;if(botFilter==='stuck')return d>30;if(botFilter==='tp')return p.tp_armed;return true;});data.sort(function(a,b){var av=a[botSort]??0,bv=b[botSort]??0;if(typeof av==='string')return botSortAsc?av.localeCompare(bv):bv.localeCompare(av);return botSortAsc?av-bv:bv-av;});var invested=data.reduce(function(s,p){return s+p.total_invested;},0),pnl=data.reduce(function(s,p){return s+p.pnl;},0),pct=invested>0?(pnl/invested*100).toFixed(2):'0.00';document.getElementById('bd-open').textContent=data.length;document.getElementById('bd-inv').textContent='$'+invested.toFixed(2);var pe=document.getElementById('bd-pnl');pe.textContent=(pnl>=0?'+':'')+'$'+Math.abs(pnl).toFixed(2);pe.style.color=pnl>=0?'var(--green)':'var(--red)';var pp=document.getElementById('bd-pnlpct');pp.textContent=(pnl>=0?'+':'')+pct+'%';pp.style.color=pnl>=0?'var(--green)':'var(--red)';document.getElementById('bd-count').textContent=data.length+' open';var tbody=document.getElementById('bdTable');if(!data.length){tbody.innerHTML='<tr><td colspan="9"><div class="empty"><div class="empty-icon">&#129302;</div><div class="empty-text">No positions match filter</div></div></td></tr>';return;}tbody.innerHTML=data.map(function(pos){var pc=pos.pnl>=0?'var(--green)':'var(--red)',sign=pos.pnl>=0?'+':'',d=pos.days_open||0,dc=d>60?'var(--red)':d>30?'var(--amber)':'var(--text3)',st=statusInfo(pos);return '<tr><td><div class="td-coin"><strong>'+pos.coin.replace('/USDT','')+'</strong></div></td><td>$'+pos.avg_cost.toFixed(4)+'</td><td>$'+pos.current_price.toFixed(4)+'</td><td style="color:'+(pos.dca_count>0?'var(--purple)':'var(--text3)')+';font-weight:700">'+pos.dca_count+'</td><td style="color:'+dc+'">'+d+'d</td><td style="color:'+pc+';font-weight:700">'+sign+pos.pnl_pct+'%</td><td style="color:'+pc+'">'+sign+'$'+Math.abs(pos.pnl).toFixed(4)+'</td><td><span class="badge '+st.cls+'">'+st.label+'</span></td><td><button class="close-btn" onclick="closePos('+pos.id+')">X</button></td></tr>';}).join('');}
function setBotFilter(type,el){botFilter=type;document.querySelectorAll('#bots-l2 .f-btn').forEach(function(b){b.classList.remove('active');});el.classList.add('active');applyBotFilter();}
function sortBd(key){if(botSort===key)botSortAsc=!botSortAsc;else{botSort=key;botSortAsc=true;}applyBotFilter();}
"""

OLD_JS_START = '// \u2500\u2500 BOTS \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500'
OLD_JS_END   = '// \u2500\u2500 HISTORY \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500'

j1 = h.find(OLD_JS_START)
j2 = h.find(OLD_JS_END)
if j1 == -1 or j2 == -1:
    print("ERROR: Could not find JS BOTS markers!")
    print("j1=%d j2=%d" % (j1, j2))
else:
    h = h[:j1] + NEW_JS + '\n' + h[j2:]
    print("Bots JS replaced")

# ── 4. WRITE ─────────────────────────────────────────────
with open('dashboard.html', 'w', encoding='utf-8') as f:
    f.write(h)
print("")
print("dashboard.html saved successfully!")
print("")
print("Now run:")
print('git add dashboard.html && git commit -m "Item 24: Bots tab flat list redesign" && git push https://baderbalubaid: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@github.com/baderbalubaid/Averion.git main')
