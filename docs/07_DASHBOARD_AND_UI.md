# Dashboard and UI

> Complete dashboard design · all tabs · responsive layout.

---

## Architecture

- Single file: dashboard.html (on Replit)
- Split into separate tab files on Hetzner Day 1
- Served by FastAPI on port 8080
- Chart.js for capital chart
- Inter font from Google Fonts
- No external CSS frameworks

---

## Responsive Layout

| Screen | Layout |
|--------|--------|
| Desktop >= 1024px | Full sidebar 220px + content area |
| Tablet 768-1023px | Icon-only sidebar 60px + content |
| Mobile < 768px | No sidebar · bottom nav 4 tabs |

100% automatic CSS media queries — no JavaScript toggle.

---

## Sidebar (Desktop/Tablet)

### Desktop (220px)
- Logo mark + AVERION text + BETA badge
- Nav links with icons + labels
- Section labels (Overview · Analytics · System)
- User avatar + name + plan at bottom

### Tablet (60px icon only)
- Logo mark only
- Icons only — no labels
- User avatar only

### Nav Links
- Home (active state: indigo background + border)
- Bots (with count badge)
- History
- Settings

---

## Topbar

- Height: 56px desktop · 50px mobile
- Left: page title
- Right: PAPER chip · BTC price ticker · notification bell · user icon
- LIVE mode: full red banner replaces topbar
- PAPER chip hidden on mobile

---

## Bottom Nav (Mobile Only)

- 4 tabs: Home · Bots · History · Settings
- Active tab: indigo color
- Icons + labels
- Safe area padding for iPhone notch

---

## Home Tab

### 5 Hero Stat Cards
| Card | Value | Subtitle |
|------|-------|---------|
| Total Capital | Sum all exchanges USDT | across X exchanges |
| Last 24h P&L | Unrealized change | +/- % colored |
| Total Profit | All-time realized | all time · all exchanges |
| Fees Due | 20% of month profits | Pay Now button if >$0 |
| Active Trades | Open count | Paper: X/30 · Live: Y |

### Fees Banner
- Shows only when fees > $0
- Amber background · Pay Now button (Phase 7 Stripe)

### Exchange Cards Grid
- 2 columns desktop · 1 column mobile
- Each card: logo · name · value · 24h P&L · 3 mini stats · coin tags
- Tap card → Exchange Detail screen
- 3-dot menu: Test Connection · Edit API Keys · Rename · Delete
- Add Exchange card (dashed border) always last

---

## Exchange Detail Screen

- Back button → Home
- Exchange name in header
- 3-dot menu (Test · Edit · Rename · Delete)
- 4 stat cards: Capital · Profit · Open Trades · 24h P&L
- Interactive capital chart (Chart.js)
  - Green line if growing · Red if declining
  - Hover shows date + exact value
  - 7D / 30D / All range buttons
- Bots section below chart

---

## Bots Tab (NEW v4.6 Flat List — LOCKED)

### Layout
- NOT grouped by exchange
- Flat list — one row per bot
- Exchange shown as colored badge per row

### Top Bar
- Title: Bots + subtitle (X bots · Y running)
- Search input
- Create Bot button

### Filter Bar
- Status filter (All · Running · Stopped · Live · Paper)
- Exchange filter (All · MEXC · Binance etc)
- Sort filter (P&L · Trades · Name)

### Table Columns
- BOT: indicator dot + name + exchange name
- EXCH: colored badge [M][B][K][O][G][By][Bg]
- TRADES: count in blue
- P&L: dollar + percentage colored
- MODE: LIVE or PAPER badge
- CONTROLS: T toggle + DCA toggle inline
- Actions: 3-dot menu

### Exchange Badge Colors
| Badge | Exchange | Color |
|-------|---------|-------|
| [M] | MEXC | Blue #38BDF8 |
| [B] | Binance | Amber #F59E0B |
| [K] | KuCoin | Green #10D98A |
| [O] | OKX | White #E2E8F0 |
| [G] | Gate.io | Blue lighter |
| [By] | Bybit | Orange #FB923C |
| [Bg] | Bitget | Purple #A78BFA |

### Two Toggles (inline per row)
- T = Trading (opens new positions)
- DCA = DCA averaging (existing positions)
- Green ON · Gray OFF · independent

### Kebab Menu
- Edit bot settings
- Duplicate bot (wizard pre-filled)
- Delete bot

### Bot Detail (Level 2)
- Back to Bots button
- 4 stats: Open · Invested · P&L$ · P&L%
- Stop/Start bot button
- Search + filter bar
- Positions table with all columns

---

## History Tab

### 6 Hero Cards
- Closed Trades · Total Profit · Win Rate
- Avg Hold · Fees 20% · Net Profit

### Filters
- Exchange dropdown
- Coin dropdown
- Date presets: Today · 7d · 30d · All
- Custom date range (from/to)
- Column picker (show/hide any column)

### Table Columns
Coin · Exchange · Entry Date · Exit Date · Entry Price ·
Avg Cost · Exit Price · DCA# · P&L% · P&L$ ·
Hold Time · Exit Reason · Fee 20% · Net Profit

---

## Settings Tab

Account info ONLY — bot config lives in wizard.

### Sections
- Profile: email · phone
- Security: 2FA toggle · change password · active sessions
- Exchanges: link to Home tab management
- Notifications: 3 Telegram IDs · alert type toggles
- Reserve Wallet: balance · top-up · deduction history · referral income
- Help: documentation · feature request · contact support

---

## Dashboard Comment Markers (Item 26)

To be added after Item 24:
- Every section marked clearly
- Makes terminal editing safe
- Preparation for Hetzner file split

Example:

## Customer Dashboard — Home Tab (LOCKED)

### Design Philosophy
- Fits one phone screen · no scrolling for critical info
- Most important info visible immediately on open
- Clean · minimal · actionable

### Layout

#### TOP — 4 Quick Stat Cards
| Open Positions | Profit Today | Fees Today | Reserve Wallet |
|----------------|--------------|------------|----------------|
| 23             | +$47.20      | $9.44      | $50.00         |

- Profit today = realized profits only
- Fees today = performance fees deducted today
- Reserve wallet = current balance · tap to top up

#### SECTION 2 — Active Alerts
- Same attention log as Bots tab
- Only shows when something needs attention
- Empty = shows "✅ All systems normal"
- Tap alert → goes to relevant screen

#### SECTION 3 — Exchange Capital (compact)
One line per exchange:
- MEXC    $234.50  [3 bots · 12 positions]
- KuCoin  $567.20  [5 bots · 11 positions]
- Total   $801.70

- Tap exchange row → goes to Bots tab filtered by exchange
- Shows only exchanges user has added
- Shows capital deployed + active bots + open positions

#### SECTION 4 — Recent Activity
Last 5 closed positions:
- Coin · profit/loss · time ago · result icon
- RVN  +$4.20  2h ago  ✅
- BTC  +$12.50  5h ago  ✅
- ETH  -$2.10  8h ago  ❌
- Tap any row → goes to position detail screen

### Mobile First
- Designed for phone screen primarily
- 4 cards fit in 2×2 grid on small screen
- All sections stack vertically
- Large tap targets · no tiny buttons
