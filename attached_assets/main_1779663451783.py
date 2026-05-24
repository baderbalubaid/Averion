import ccxt

print("DCA Bot - Phase 1 Starting...")
print("Connecting to MEXC...")

exchange = ccxt.mexc()

ticker = exchange.fetch_ticker('BTC/USDT')
price = ticker['last']

print(f"BTC/USDT Current Price: ${price}")
print("Connection successful!")

buy_amount_usdt = 1.0
quantity = buy_amount_usdt / price
new_avg = price

print(f"\n--- Simulated Buy ---")
print(f"Spent: ${buy_amount_usdt}")
print(f"Quantity: {quantity:.6f} BTC")
print(f"Average Cost: ${new_avg}")
print(f"Status: PAPER TRADE - No real order placed")