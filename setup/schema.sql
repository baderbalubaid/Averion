-- Averion PostgreSQL Schema
-- Run this on Hetzner Day 1
-- Command: psql -U averion -d averion < schema.sql

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ═══════════════════════════════
-- USERS
-- ═══════════════════════════════
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    password_hash VARCHAR(255) NOT NULL,
    referral_code VARCHAR(20) UNIQUE,
    referred_by INTEGER REFERENCES users(id),
    fee_override DECIMAL(5,2) DEFAULT 20.00,
    is_admin BOOLEAN DEFAULT FALSE,
    is_zero_fee BOOLEAN DEFAULT FALSE,
    is_suspended BOOLEAN DEFAULT FALSE,
    free_trial_credit DECIMAL(10,2) DEFAULT 5.00,
    created_at TIMESTAMP DEFAULT NOW(),
    last_active_at TIMESTAMP
);

-- ═══════════════════════════════
-- EXCHANGES
-- ═══════════════════════════════
CREATE TABLE exchanges (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    exchange VARCHAR(50) NOT NULL,
    custom_name VARCHAR(100),
    api_key_enc TEXT NOT NULL,
    secret_enc TEXT NOT NULL,
    uid_fingerprint VARCHAR(255),
    active BOOLEAN DEFAULT TRUE,
    paused_at TIMESTAMP,
    pause_reason VARCHAR(50),
    pause_type VARCHAR(20),
    reconnect_attempts INTEGER DEFAULT 0,
    last_connected_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ═══════════════════════════════
-- VIRTUAL WALLETS
-- ═══════════════════════════════
CREATE TABLE virtual_wallets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    exchange_id INTEGER REFERENCES exchanges(id),
    name VARCHAR(100) NOT NULL,
    currency VARCHAR(20) DEFAULT 'USDT',
    allocation_type VARCHAR(10) DEFAULT 'fixed',
    allocation_amount DECIMAL(20,8),
    current_balance DECIMAL(20,8) DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ═══════════════════════════════
-- BOTS
-- ═══════════════════════════════
CREATE TABLE bots (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    exchange_id INTEGER REFERENCES exchanges(id),
    wallet_id INTEGER REFERENCES virtual_wallets(id),
    name VARCHAR(100) NOT NULL,
    method VARCHAR(50) DEFAULT 'smart',
    direction VARCHAR(10) DEFAULT 'long',
    trading_on BOOLEAN DEFAULT TRUE,
    dca_on BOOLEAN DEFAULT TRUE,
    base_order DECIMAL(20,8) DEFAULT 1.00,
    dca_percent DECIMAL(5,2) DEFAULT 7.00,
    spacing_multiplier DECIMAL(5,2) DEFAULT 1.4,
    size_multiplier DECIMAL(5,2) DEFAULT 1.5,
    take_profit_percent DECIMAL(5,2) DEFAULT 5.00,
    trailing_percent DECIMAL(5,2) DEFAULT 2.00,
    profit_coin VARCHAR(20) DEFAULT 'USDT',
    reserve_floor DECIMAL(20,8) DEFAULT 50.00,
    resume_threshold DECIMAL(20,8) DEFAULT 75.00,
    auto_resume BOOLEAN DEFAULT TRUE,
    max_trades INTEGER DEFAULT 0,
    dca_checkpoint INTEGER DEFAULT 0,
    is_paper BOOLEAN DEFAULT TRUE,
    status VARCHAR(20) DEFAULT 'active',
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ═══════════════════════════════
-- POSITIONS
-- ═══════════════════════════════
CREATE TABLE positions (
    id SERIAL PRIMARY KEY,
    bot_id INTEGER REFERENCES bots(id),
    user_id INTEGER REFERENCES users(id),
    exchange_id INTEGER REFERENCES exchanges(id),
    wallet_id INTEGER REFERENCES virtual_wallets(id),
    coin VARCHAR(20) NOT NULL,
    direction VARCHAR(10) DEFAULT 'long',
    status VARCHAR(20) DEFAULT 'open',
    avg_cost DECIMAL(20,8),
    avg_sell_price DECIMAL(20,8),
    quantity DECIMAL(20,8) DEFAULT 0,
    total_invested DECIMAL(20,8) DEFAULT 0,
    total_sold_usdt DECIMAL(20,8) DEFAULT 0,
    dca_count INTEGER DEFAULT 0,
    last_buy_price DECIMAL(20,8),
    last_sell_price DECIMAL(20,8),
    tp_armed BOOLEAN DEFAULT FALSE,
    peak_price DECIMAL(20,8),
    queued BOOLEAN DEFAULT FALSE,
    standby_amount DECIMAL(20,8) DEFAULT 0,
    standby_price DECIMAL(20,8),
    standby_timeout_at TIMESTAMP,
    dust_amount DECIMAL(20,8) DEFAULT 0,
    dust_currency VARCHAR(20),
    is_manual BOOLEAN DEFAULT FALSE,
    is_paper BOOLEAN DEFAULT TRUE,
    category VARCHAR(20),
    entry_method VARCHAR(20),
    opened_at TIMESTAMP DEFAULT NOW(),
    closed_at TIMESTAMP,
    close_reason VARCHAR(50)
);

-- ═══════════════════════════════
-- TRADES
-- ═══════════════════════════════
CREATE TABLE trades (
    id SERIAL PRIMARY KEY,
    position_id INTEGER REFERENCES positions(id),
    bot_id INTEGER REFERENCES bots(id),
    user_id INTEGER REFERENCES users(id),
    exchange_id INTEGER REFERENCES exchanges(id),
    coin VARCHAR(20) NOT NULL,
    side VARCHAR(10) NOT NULL,
    price DECIMAL(20,8) NOT NULL,
    quantity DECIMAL(20,8) NOT NULL,
    usdt_amount DECIMAL(20,8) NOT NULL,
    exchange_fee DECIMAL(20,8) DEFAULT 0,
    fee_currency VARCHAR(20),
    reason VARCHAR(50),
    order_type VARCHAR(20) DEFAULT 'market',
    exchange_order_id VARCHAR(100),
    is_paper BOOLEAN DEFAULT TRUE,
    dca_level INTEGER DEFAULT 0,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- ═══════════════════════════════
-- STANDBY ORDERS
-- ═══════════════════════════════
CREATE TABLE standby_orders (
    id SERIAL PRIMARY KEY,
    position_id INTEGER REFERENCES positions(id),
    bot_id INTEGER REFERENCES bots(id),
    wallet_id INTEGER REFERENCES virtual_wallets(id),
    standby_amount DECIMAL(20,8) NOT NULL,
    target_price DECIMAL(20,8) NOT NULL,
    dca_level INTEGER NOT NULL,
    timeout_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    triggered_at TIMESTAMP,
    expired_at TIMESTAMP
);

-- ═══════════════════════════════
-- RESERVE WALLETS
-- ═══════════════════════════════
CREATE TABLE reserve_wallets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) UNIQUE,
    balance_usdt DECIMAL(20,8) DEFAULT 0,
    total_deposited DECIMAL(20,8) DEFAULT 0,
    total_deducted DECIMAL(20,8) DEFAULT 0,
    last_updated TIMESTAMP DEFAULT NOW()
);

-- ═══════════════════════════════
-- RESERVE DEPOSITS
-- ═══════════════════════════════
CREATE TABLE reserve_deposits (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    nowpayments_id VARCHAR(100) UNIQUE,
    amount_sent DECIMAL(20,8),
    amount_received DECIMAL(20,8),
    network VARCHAR(20),
    tx_hash VARCHAR(255),
    status VARCHAR(20) DEFAULT 'pending',
    credited_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ═══════════════════════════════
-- FEE DEBT
-- ═══════════════════════════════
CREATE TABLE fee_debt (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    position_id INTEGER REFERENCES positions(id),
    amount_usdt DECIMAL(20,8) NOT NULL,
    trade_profit DECIMAL(20,8),
    paid_at TIMESTAMP,
    paid_from_deposit_id INTEGER REFERENCES reserve_deposits(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- ═══════════════════════════════
-- BALANCE HISTORY
-- ═══════════════════════════════
CREATE TABLE balance_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    exchange_id INTEGER REFERENCES exchanges(id),
    value_usdt DECIMAL(20,8),
    recorded_at TIMESTAMP DEFAULT NOW()
);

-- ═══════════════════════════════
-- COIN HISTORY (Classification)
-- ═══════════════════════════════
CREATE TABLE coin_history (
    id SERIAL PRIMARY KEY,
    coin VARCHAR(20) NOT NULL,
    exchange VARCHAR(50),
    real_cap DECIMAL(30,2),
    recorded_cap DECIMAL(30,2),
    category VARCHAR(20),
    volume_24h DECIMAL(30,2),
    confidence_days INTEGER DEFAULT 0,
    recorded_at TIMESTAMP DEFAULT NOW()
);

-- ═══════════════════════════════
-- OHLCV HOURLY
-- ═══════════════════════════════
CREATE TABLE ohlcv_hourly (
    id SERIAL PRIMARY KEY,
    coin VARCHAR(20) NOT NULL,
    exchange VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    open DECIMAL(20,8),
    high DECIMAL(20,8),
    low DECIMAL(20,8),
    close DECIMAL(20,8),
    volume DECIMAL(30,8),
    atr_14 DECIMAL(20,8),
    UNIQUE(coin, exchange, timestamp)
);

-- ═══════════════════════════════
-- OWNER BALANCE
-- ═══════════════════════════════
CREATE TABLE owner_balance (
    id SERIAL PRIMARY KEY,
    accumulated_fees_usdt DECIMAL(20,8) DEFAULT 0,
    last_transfer_date TIMESTAMP,
    last_transfer_amount DECIMAL(20,8),
    total_transferred DECIMAL(20,8) DEFAULT 0
);

-- ═══════════════════════════════
-- REFERRALS
-- ═══════════════════════════════
CREATE TABLE referrals (
    id SERIAL PRIMARY KEY,
    referrer_user_id INTEGER REFERENCES users(id),
    referred_user_id INTEGER REFERENCES users(id) UNIQUE,
    total_earned DECIMAL(20,8) DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ═══════════════════════════════
-- WALLET BOT ASSIGNMENTS
-- ═══════════════════════════════
CREATE TABLE wallet_bot_assignments (
    id SERIAL PRIMARY KEY,
    wallet_id INTEGER REFERENCES virtual_wallets(id),
    bot_id INTEGER REFERENCES bots(id),
    assigned_at TIMESTAMP DEFAULT NOW(),
    unassigned_at TIMESTAMP
);

-- ═══════════════════════════════
-- WALLET TRANSACTIONS
-- ═══════════════════════════════
CREATE TABLE wallet_transactions (
    id SERIAL PRIMARY KEY,
    wallet_id INTEGER REFERENCES virtual_wallets(id),
    position_id INTEGER REFERENCES positions(id),
    type VARCHAR(30) NOT NULL,
    amount DECIMAL(20,8) NOT NULL,
    balance_after DECIMAL(20,8),
    created_at TIMESTAMP DEFAULT NOW()
);

-- ═══════════════════════════════
-- INDEXES (Performance)
-- ═══════════════════════════════
CREATE INDEX idx_positions_exchange_status ON positions(exchange_id, status);
CREATE INDEX idx_positions_user_status ON positions(user_id, status);
CREATE INDEX idx_positions_coin_last_buy ON positions(coin, last_buy_price);
CREATE INDEX idx_positions_bot ON positions(bot_id);
CREATE INDEX idx_trades_position ON trades(position_id);
CREATE INDEX idx_trades_user_closed ON trades(user_id, timestamp);
CREATE INDEX idx_balance_history_exchange ON balance_history(exchange_id, recorded_at);
CREATE INDEX idx_ohlcv_coin_exchange_time ON ohlcv_hourly(coin, exchange, timestamp);
CREATE INDEX idx_coin_history_coin ON coin_history(coin, recorded_at);
CREATE INDEX idx_standby_status ON standby_orders(status, target_price);

-- ═══════════════════════════════
-- INITIAL DATA
-- ═══════════════════════════════
INSERT INTO owner_balance (accumulated_fees_usdt, total_transferred)
VALUES (0, 0);

SELECT 'Averion database schema created successfully!' AS result;
