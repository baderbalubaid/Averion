from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from database import get_db, init_db
from datetime import datetime, timezone
import threading
import uvicorn
import ccxt

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="Averion Bot API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

bot_running = True
stop_event  = threading.Event()
exchange    = ccxt.mexc({'enableRateLimit': True})

# ── HELPERS ───────────────────────────────────────────────
def days_open(opened_at_str):
    """Calculate days since position opened."""
    if not opened_at_str:
        return 0
    try:
        opened = datetime.fromisoformat(str(opened_at_str))
        if opened.tzinfo is None:
            opened = opened.replace(tzinfo=timezone.utc)
        delta = datetime.now(timezone.utc) - opened
        return delta.days
    except:
        return 0

# ── DASHBOARD ─────────────────────────────────────────────
@app.get("/dashboard")
def dashboard():
    return FileResponse("dashboard.html")

# ── STATUS ────────────────────────────────────────────────
@app.get("/status")
def get_status():
    try:
        ticker = exchange.fetch_ticker('BTC/USDT')
        price  = ticker['last']
    except:
        price = 0
    return {
        "running":   bot_running,
        "btc_price": price,
        "mode":      "paper",
    }

# ── POSITIONS ─────────────────────────────────────────────
@app.get("/positions")
def get_positions():
    conn = get_db()
    c    = conn.cursor()
    c.execute("SELECT * FROM positions WHERE status='open'")
    rows = c.fetchall()
    conn.close()

    positions = []
    for row in rows:
        try:
            ticker        = exchange.fetch_ticker(row["coin"])
            current_price = ticker['last']
        except:
            current_price = row["avg_cost"]

        pnl     = (current_price - row["avg_cost"]) * row["quantity"]
        pnl_pct = ((current_price - row["avg_cost"]) / row["avg_cost"]) * 100 if row["avg_cost"] else 0

        positions.append({
            "id":            row["id"],
            "coin":          row["coin"],
            "avg_cost":      row["avg_cost"],
            "quantity":      row["quantity"],
            "total_invested":row["total_invested"],
            "dca_count":     row["dca_count"],
            "opened_at":     row["opened_at"],
            "current_price": current_price,
            "pnl":           round(pnl, 4),
            "pnl_pct":       round(pnl_pct, 2),
            "days_open":     days_open(row["opened_at"]),
            "tp_armed":      bool(row["tp_armed"]) if "tp_armed" in row.keys() else False,
            "queued":        bool(row["queued"])    if "queued"   in row.keys() else False,
        })
    return positions

# ── TRADES ────────────────────────────────────────────────
@app.get("/trades")
def get_trades():
    conn = get_db()
    c    = conn.cursor()
    c.execute("SELECT * FROM trades ORDER BY timestamp DESC LIMIT 50")
    rows = c.fetchall()
    conn.close()
    trades = []
    for row in rows:
        trades.append({
            "id":          row["id"],
            "position_id": row["position_id"],
            "coin":        row["coin"] if "coin" in row.keys() else "",
            "side":        row["side"],
            "price":       row["price"],
            "quantity":    row["quantity"],
            "usdt_amount": row["usdt_amount"],
            "reason":      row["reason"],
            "timestamp":   row["timestamp"],
        })
    return trades

# ── HISTORY (Item 1) ──────────────────────────────────────
@app.get("/history")
def get_history():
    conn = get_db()
    c    = conn.cursor()
    c.execute("""
        SELECT p.*, t.price as exit_price, t.timestamp as closed_at_trade
        FROM positions p
        LEFT JOIN trades t ON t.position_id = p.id AND t.reason IN ('tp','manual')
        WHERE p.status = 'closed'
        ORDER BY p.closed_at DESC
        LIMIT 200
    """)
    rows = c.fetchall()
    conn.close()
    history = []
    for row in rows:
        entry_price = row["avg_cost"] or 0
        exit_price  = row["exit_price"] or row["avg_cost"] or 0
        realized_pnl = (exit_price - entry_price) * (row["quantity"] or 0)
        history.append({
            "id":           row["id"],
            "coin":         row["coin"],
            "exchange":     "MEXC",
            "dca_count":    row["dca_count"],
            "total_invested":row["total_invested"],
            "entry_price":  entry_price,
            "avg_cost":     entry_price,
            "exit_price":   exit_price,
            "exit_reason":  "closed",
            "realized_pnl": round(realized_pnl, 4),
            "opened_at":    row["opened_at"],
            "closed_at":    row["closed_at"],
            "days_held":    days_open(row["opened_at"]),
        })
    return history

# ── BALANCE HISTORY (for chart) ───────────────────────────
@app.get("/balance-history")
def get_balance_history(exchange_id: str = "mexc", days: int = 30):
    conn = get_db()
    c    = conn.cursor()
    c.execute("""
        SELECT value_usdt, recorded_at
        FROM balance_history
        WHERE exchange = ?
        ORDER BY recorded_at ASC
        LIMIT ?
    """, (exchange_id, days))
    rows = c.fetchall()
    conn.close()
    return [{"value": row["value_usdt"], "date": row["recorded_at"]} for row in rows]

# ── CONFIG GET (Item 2) ───────────────────────────────────
@app.get("/config")
def get_config():
    try:
        from config import (DCA_PERCENT, TAKE_PROFIT_PERCENT, TRAILING_PERCENT,
                            BASE_ORDER_USDT, CHECK_INTERVAL, SPACING_MULTIPLIER,
                            SIZE_MULTIPLIER, PAPER_MODE, MAX_DCA_ORDERS)
        return {
            "paper_mode":          PAPER_MODE,
            "dca_percent":         DCA_PERCENT,
            "spacing_multiplier":  SPACING_MULTIPLIER,
            "size_multiplier":     SIZE_MULTIPLIER,
            "take_profit_percent": TAKE_PROFIT_PERCENT,
            "trailing_percent":    TRAILING_PERCENT,
            "base_order_usdt":     BASE_ORDER_USDT,
            "check_interval":      CHECK_INTERVAL,
            "max_dca_orders":      MAX_DCA_ORDERS,
        }
    except Exception as e:
        return {"error": str(e)}

# ── CONFIG POST (Item 2) ──────────────────────────────────
class ConfigUpdate(BaseModel):
    paper_mode:          bool  = True
    dca_percent:         float = 7.0
    spacing_multiplier:  float = 1.4
    size_multiplier:     float = 1.5
    take_profit_percent: float = 5.0
    trailing_percent:    float = 2.0
    base_order_usdt:     float = 1.0
    check_interval:      int   = 60
    max_dca_orders:      int   = 10

@app.post("/config")
def update_config(cfg: ConfigUpdate):
    try:
        lines = [
            f"PAPER_MODE          = {cfg.paper_mode}",
            f"QUOTE               = 'USDT'",
            f"BASE_ORDER_USDT     = {cfg.base_order_usdt}",
            f"DCA_PERCENT         = {cfg.dca_percent}",
            f"SPACING_MULTIPLIER  = {cfg.spacing_multiplier}",
            f"SIZE_MULTIPLIER     = {cfg.size_multiplier}",
            f"TAKE_PROFIT_PERCENT = {cfg.take_profit_percent}",
            f"TRAILING_PERCENT    = {cfg.trailing_percent}",
            f"MAX_DCA_ORDERS      = {cfg.max_dca_orders}",
            f"CHECK_INTERVAL      = {cfg.check_interval}",
            f"AUTO_COINS          = True",
            f"MAX_COINS           = 100",
        ]
        with open("config.py", "w") as f:
            f.write("\n".join(lines) + "\n")
        return {"message": "Config saved — restart bot to apply"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── BOT CONTROLS ──────────────────────────────────────────
@app.post("/start")
def start_bot():
    global bot_running, stop_event
    if bot_running:
        return {"message": "Bot already running"}
    stop_event  = threading.Event()
    bot_running = True
    import main
    t = threading.Thread(target=main.run_bot, daemon=True)
    t.start()
    return {"message": "Bot started"}

@app.post("/stop")
def stop_bot():
    global bot_running
    bot_running = False
    stop_event.set()
    return {"message": "Bot stopped"}

# ── CLOSE POSITION ────────────────────────────────────────
@app.post("/positions/{position_id}/close")
def close_position(position_id: int):
    conn = get_db()
    c    = conn.cursor()
    c.execute("SELECT * FROM positions WHERE id=?", (position_id,))
    pos  = c.fetchone()
    if not pos:
        raise HTTPException(status_code=404, detail="Position not found")
    try:
        ticker = exchange.fetch_ticker(pos["coin"])
        price  = ticker['last']
    except:
        price  = pos["avg_cost"]
    qty    = pos["quantity"]
    pnl    = (price - pos["avg_cost"]) * qty
    c.execute("""UPDATE positions SET status='closed', closed_at=CURRENT_TIMESTAMP
                 WHERE id=?""", (position_id,))
    c.execute("""INSERT INTO trades (position_id, coin, side, price, quantity,
                 usdt_amount, reason, paper) VALUES (?,?,?,?,?,?,?,1)""",
              (position_id, pos["coin"], "sell", price, qty,
               round(price * qty, 4), "manual"))
    conn.commit()
    conn.close()
    return {"message": f"Position {position_id} closed", "pnl": round(pnl, 4)}

# ── ADD FUNDS ─────────────────────────────────────────────
@app.post("/positions/{position_id}/add")
def add_funds(position_id: int, amount: float = 1.0):
    conn = get_db()
    c    = conn.cursor()
    c.execute("SELECT * FROM positions WHERE id=?", (position_id,))
    pos  = c.fetchone()
    if not pos:
        raise HTTPException(status_code=404, detail="Position not found")
    try:
        ticker = exchange.fetch_ticker(pos["coin"])
        price  = ticker['last']
    except:
        price  = pos["avg_cost"]
    qty      = amount / price
    new_total = pos["total_invested"] + amount
    new_qty   = pos["quantity"] + qty
    new_avg   = new_total / new_qty
    c.execute("""UPDATE positions SET avg_cost=?, quantity=?, total_invested=?
                 WHERE id=?""", (new_avg, new_qty, new_total, position_id))
    c.execute("""INSERT INTO trades (position_id, coin, side, price, quantity,
                 usdt_amount, reason, paper) VALUES (?,?,?,?,?,?,?,1)""",
              (position_id, pos["coin"], "buy", price, qty, amount, "manual"))
    conn.commit()
    conn.close()
    return {"message": f"Added ${amount}", "new_avg": round(new_avg, 6)}

# ── RECORD BALANCE (called daily by bot) ──────────────────
@app.post("/record-balance")
def record_balance(value: float, exchange_id: str = "mexc"):
    conn = get_db()
    c    = conn.cursor()
    c.execute("INSERT INTO balance_history (exchange, value_usdt) VALUES (?,?)",
              (exchange_id, value))
    conn.commit()
    conn.close()
    return {"message": "Balance recorded"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
