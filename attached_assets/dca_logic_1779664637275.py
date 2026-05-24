from decimal import Decimal

def calc_new_average(total_invested, quantity):
    if quantity == 0:
        return 0
    return total_invested / quantity

def should_dca(avg_cost, current_price, dca_percent):
    trigger = avg_cost * (1 - dca_percent / 100)
    return current_price <= trigger

def should_take_profit(avg_cost, current_price, tp_percent):
    target = avg_cost * (1 + tp_percent / 100)
    return current_price >= target

def calc_quantity(usdt_amount, price):
    return usdt_amount / price