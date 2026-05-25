import threading
import ccxt
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database import get_db, init_db
from config import COIN, DCA_PERCENT, TAKE_PROFIT_PERCENT, TRAILING_PERCENT, BASE_ORDER_USDT, CHECK_INTERVAL

app = FastAPI(title="Averion Bot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

bot_thread = None
bot_running = False
stop_event = threading.Event()


def run_bot_thread():
    import main
    main.run_bot(stop_event)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/status")
def get_status():
    try:
        exchange = ccxt.mexc()
        ticker = exchange.fetch_ticker(COIN)
        price = ticker["last"]
    except Exception:
        price = 0
    return {
        "running": bot_running,
        "coin": COIN,
        "price": price,
    }


@app.get("/positions")
def get_positions():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM positions WHERE status='open'")
    rows = c.fetchall()
    conn.close()
    return [
        {
            "id": row["id"],
            "coin": row["coin"],
            "avg_cost": row["avg_cost"],
            "quantity": row["quantity"],
            "total_invested": row["total_invested"],
            "dca_count": row["dca_count"],
            "opened_at": row["opened_at"],
        }
        for row in rows
    ]


@app.get("/trades")
def get_trades():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM trades ORDER BY timestamp DESC LIMIT 50")
    rows = c.fetchall()
    conn.close()
    return [
        {
            "id": row["id"],
            "position_id": row["position_id"],
            "side": row["side"],
            "price": row["price"],
            "quantity": row["quantity"],
            "usdt_amount": row["usdt_amount"],
            "reason": row["reason"],
            "timestamp": row["timestamp"],
        }
        for row in rows
    ]


@app.post("/start")
def start_bot():
    global bot_thread, bot_running, stop_event
    if bot_running:
        return {"message": "Bot already running"}
    stop_event = threading.Event()
    bot_running = True
    bot_thread = threading.Thread(target=run_bot_thread, daemon=True)
    bot_thread.start()
    return {"message": "Bot started"}


@app.post("/stop")
def stop_bot():
    global bot_running
    stop_event.set()
    bot_running = False
    return {"message": "Bot stopped"}


@app.post("/positions/{position_id}/close")
def close_position(position_id: int):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "UPDATE positions SET status='closed', closed_at=CURRENT_TIMESTAMP WHERE id=?",
        (position_id,),
    )
    if c.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Position not found")
    conn.commit()
    conn.close()
    return {"message": f"Position {position_id} closed"}


@app.post("/positions/{position_id}/add")
def add_funds(position_id: int, amount: float = 1.0):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM positions WHERE id=?", (position_id,))
    pos = c.fetchone()
    if not pos:
        conn.close()
        raise HTTPException(status_code=404, detail="Position not found")
    exchange = ccxt.mexc()
    ticker = exchange.fetch_ticker(COIN)
    price = ticker["last"]
    qty = amount / price
    new_total = pos["total_invested"] + amount
    new_qty = pos["quantity"] + qty
    new_avg = new_total / new_qty
    c.execute(
        "UPDATE positions SET avg_cost=?, quantity=?, total_invested=? WHERE id=?",
        (new_avg, new_qty, new_total, position_id),
    )
    c.execute(
        "INSERT INTO trades (position_id, side, price, quantity, usdt_amount, reason, paper) VALUES (?,?,?,?,?,?,1)",
        (position_id, "buy", price, qty, amount, "manual"),
    )
    conn.commit()
    conn.close()
    return {"message": f"Added ${amount}", "new_avg": new_avg}


@app.get("/config")
def get_config():
    return {
        "coin": COIN,
        "dca_percent": DCA_PERCENT,
        "take_profit_percent": TAKE_PROFIT_PERCENT,
        "trailing_percent": TRAILING_PERCENT,
        "base_order_usdt": BASE_ORDER_USDT,
        "check_interval": CHECK_INTERVAL,
    }


@app.get("/dashboard")
def dashboard():
    return FileResponse("dashboard.html")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
