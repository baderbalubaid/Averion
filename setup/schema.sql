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
    close_reason VARCHAR(50),
    short_buyback_order_id VARCHAR(100),
    short_buyback_reserved_usdt DECIMAL(20,8) DEFAULT 0,
    pending_buyback BOOLEAN DEFAULT FALSE
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

-- ═══════════════════════════════
-- TELEGRAM SETTINGS
-- ═══════════════════════════════
CREATE TABLE user_telegram (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) UNIQUE,
    chat_id VARCHAR(100),
    verified BOOLEAN DEFAULT FALSE,
    verification_code VARCHAR(20),
    trade_alerts BOOLEAN DEFAULT TRUE,
    report_alerts BOOLEAN DEFAULT TRUE,
    alert_alerts BOOLEAN DEFAULT TRUE,
    connected_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ═══════════════════════════════
-- ATTENTION LOG
-- ═══════════════════════════════
CREATE TABLE attention_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    bot_id INTEGER REFERENCES bots(id),
    position_id INTEGER REFERENCES positions(id),
    severity VARCHAR(10) NOT NULL,
    item_type VARCHAR(50) NOT NULL,
    message TEXT,
    action_taken VARCHAR(50),
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ═══════════════════════════════
-- NOTIFICATION QUEUE
-- ═══════════════════════════════
CREATE TABLE notification_queue (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    chat_id VARCHAR(100),
    message TEXT NOT NULL,
    message_type VARCHAR(30),
    sent BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMP,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ═══════════════════════════════
-- POSITIONS ARCHIVE
-- ═══════════════════════════════
CREATE TABLE positions_archive (
    LIKE positions INCLUDING ALL
);

-- ═══════════════════════════════
-- STRATEGY VERSIONS
-- ═══════════════════════════════
CREATE TABLE strategy_versions (
    id SERIAL PRIMARY KEY,
    method VARCHAR(20) NOT NULL,
    version INTEGER NOT NULL,
    parameters_json JSONB,
    date_created TIMESTAMP DEFAULT NOW(),
    parent_version INTEGER,
    cooldown_until TIMESTAMP,
    created_by INTEGER REFERENCES users(id)
);

-- ═══════════════════════════════
-- RESEARCH SCORES
-- ═══════════════════════════════
CREATE TABLE research_scores (
    id SERIAL PRIMARY KEY,
    bot_id INTEGER REFERENCES bots(id),
    method VARCHAR(20),
    bot_config_id VARCHAR(20),
    total_trades INTEGER DEFAULT 0,
    winning_trades INTEGER DEFAULT 0,
    losing_trades INTEGER DEFAULT 0,
    win_rate DECIMAL(5,2),
    avg_profit DECIMAL(20,8),
    avg_loss DECIMAL(20,8),
    total_profit DECIMAL(20,8),
    max_drawdown DECIMAL(20,8),
    avg_hold_hours DECIMAL(10,2),
    recovery_speed DECIMAL(10,2),
    promotion_score DECIMAL(10,6),
    rank INTEGER,
    status VARCHAR(20) DEFAULT 'active',
    last_calculated TIMESTAMP DEFAULT NOW()
);

-- ═══════════════════════════════
-- BOT SLOTS AND BUNDLES
-- ═══════════════════════════════
CREATE TABLE user_subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) UNIQUE,
    free_bot_slots INTEGER DEFAULT 5,
    paid_bot_slots INTEGER DEFAULT 0,
    free_trade_bundle INTEGER DEFAULT 100,
    paid_trade_bundle INTEGER DEFAULT 0,
    trades_used_this_month INTEGER DEFAULT 0,
    bundle_type VARCHAR(20) DEFAULT 'free',
    next_billing_date DATE,
    last_deduction_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ═══════════════════════════════
-- ADDITIONAL INDEXES
-- ═══════════════════════════════
CREATE INDEX idx_attention_log_user ON attention_log(user_id, resolved);
CREATE INDEX idx_notification_queue_sent ON notification_queue(sent, created_at);
CREATE INDEX idx_research_scores_method ON research_scores(method, promotion_score);
CREATE INDEX idx_strategy_versions_method ON strategy_versions(method, version);

SELECT 'Schema update complete — all tables created!' AS result;

-- ═══════════════════════════════
-- SCHEMA UPDATES — Additional Columns
-- ═══════════════════════════════

-- DCA Checkpoint fields for bots
ALTER TABLE bots ADD COLUMN IF NOT EXISTS dca_checkpoint_level INTEGER DEFAULT 0;
ALTER TABLE bots ADD COLUMN IF NOT EXISTS dca_checkpoint_on BOOLEAN DEFAULT FALSE;

-- DCA Checkpoint tracking for positions
ALTER TABLE positions ADD COLUMN IF NOT EXISTS checkpoint_reached BOOLEAN DEFAULT FALSE;
ALTER TABLE positions ADD COLUMN IF NOT EXISTS checkpoint_reached_at TIMESTAMP;
ALTER TABLE positions ADD COLUMN IF NOT EXISTS checkpoint_level_reached INTEGER DEFAULT 0;

-- Virtual wallet standby reserved amount
ALTER TABLE virtual_wallets ADD COLUMN IF NOT EXISTS standby_reserved DECIMAL(20,8) DEFAULT 0;

-- API key expiry tracking
ALTER TABLE exchanges ADD COLUMN IF NOT EXISTS key_expires_at TIMESTAMP;
ALTER TABLE exchanges ADD COLUMN IF NOT EXISTS last_alert_sent_at TIMESTAMP;
ALTER TABLE exchanges ADD COLUMN IF NOT EXISTS alert_count INTEGER DEFAULT 0;

-- Bot slot tracking per user
ALTER TABLE users ADD COLUMN IF NOT EXISTS telegram_chat_id VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS telegram_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS trade_alerts_on BOOLEAN DEFAULT TRUE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS report_alerts_on BOOLEAN DEFAULT TRUE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS alert_alerts_on BOOLEAN DEFAULT TRUE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS bot_slots_total INTEGER DEFAULT 5;
ALTER TABLE users ADD COLUMN IF NOT EXISTS trades_used_this_month INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS next_billing_date DATE;

SELECT 'Schema updates applied successfully!' AS result;

-- Base coin support
ALTER TABLE bots ADD COLUMN IF NOT EXISTS base_coin VARCHAR(10) DEFAULT 'USDT';

-- Position detail enhancements
ALTER TABLE trades ADD COLUMN IF NOT EXISTS dca_level_price DECIMAL(20,8);
ALTER TABLE trades ADD COLUMN IF NOT EXISTS running_avg_cost DECIMAL(20,8);
ALTER TABLE trades ADD COLUMN IF NOT EXISTS running_quantity DECIMAL(20,8);
ALTER TABLE trades ADD COLUMN IF NOT EXISTS running_total_invested DECIMAL(20,8);

SELECT 'Base coin and position detail columns added!' AS result;

-- ═══════════════════════════════
-- CRITICAL FIXES — v5 Review
-- ═══════════════════════════════

-- Exchange passphrase (KuCoin · OKX · Bitget)
ALTER TABLE exchanges ADD COLUMN IF NOT EXISTS passphrase_enc TEXT;
ALTER TABLE exchanges ADD COLUMN IF NOT EXISTS ip_whitelist_confirmed BOOLEAN DEFAULT FALSE;

-- Research bot market regime tracking
ALTER TABLE research_scores ADD COLUMN IF NOT EXISTS regimes_tested JSONB DEFAULT '[]';
ALTER TABLE research_scores ADD COLUMN IF NOT EXISTS bundle_period VARCHAR(7);

-- Subscription billing history
CREATE TABLE IF NOT EXISTS subscription_billing (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    billing_date DATE NOT NULL,
    bot_fee DECIMAL(20,8) DEFAULT 0,
    bundle_fee DECIMAL(20,8) DEFAULT 0,
    total_fee DECIMAL(20,8) DEFAULT 0,
    reserve_before DECIMAL(20,8),
    reserve_after DECIMAL(20,8),
    bots_affected JSONB,
    status VARCHAR(20) DEFAULT 'paid',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Exchange coin limits tracking
CREATE TABLE IF NOT EXISTS exchange_coin_limits (
    id SERIAL PRIMARY KEY,
    exchange_id INTEGER REFERENCES exchanges(id),
    coin VARCHAR(20) NOT NULL,
    min_order_size DECIMAL(20,8),
    min_notional DECIMAL(20,8),
    status VARCHAR(20) DEFAULT 'active',
    status_reason TEXT,
    last_checked TIMESTAMP DEFAULT NOW(),
    UNIQUE(exchange_id, coin)
);

-- Short buyback order history
CREATE TABLE IF NOT EXISTS short_buyback_orders (
    id SERIAL PRIMARY KEY,
    position_id INTEGER REFERENCES positions(id),
    exchange_order_id VARCHAR(100) UNIQUE,
    limit_price DECIMAL(20,8),
    quantity DECIMAL(20,8),
    usdt_reserved DECIMAL(20,8),
    status VARCHAR(20) DEFAULT 'pending',
    filled_at TIMESTAMP,
    cancelled_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Additional indexes
CREATE INDEX IF NOT EXISTS idx_subscription_billing_user ON subscription_billing(user_id, billing_date);
CREATE INDEX IF NOT EXISTS idx_exchange_coin_limits ON exchange_coin_limits(exchange_id, coin);
CREATE INDEX IF NOT EXISTS idx_short_buyback_position ON short_buyback_orders(position_id, status);
CREATE INDEX IF NOT EXISTS idx_reserve_deposits_nowpayments ON reserve_deposits(nowpayments_id, status);

SELECT 'v5 critical fixes applied!' AS result;

-- Auto-renew support for bots and bundles
ALTER TABLE bots ADD COLUMN IF NOT EXISTS auto_renew BOOLEAN DEFAULT FALSE;
ALTER TABLE bots ADD COLUMN IF NOT EXISTS renewal_type VARCHAR(20) DEFAULT 'one-time';

-- Trade bundle tracking per user
CREATE TABLE IF NOT EXISTS trade_bundles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    bundle_type VARCHAR(20) NOT NULL,
    trades_total INTEGER NOT NULL,
    trades_used INTEGER DEFAULT 0,
    price_usdt DECIMAL(10,2),
    auto_renew BOOLEAN DEFAULT FALSE,
    renewal_type VARCHAR(20) DEFAULT 'one-time',
    purchased_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active'
);

CREATE INDEX IF NOT EXISTS idx_trade_bundles_user ON trade_bundles(user_id, status);

SELECT 'Auto-renew and bundle tables added!' AS result;

-- ═══════════════════════════════
-- MULTI-TRADE GATE SYSTEM + LIMIT ORDERS
-- ═══════════════════════════════

-- Bot level settings
ALTER TABLE bots ADD COLUMN IF NOT EXISTS trades_per_bot INTEGER DEFAULT 1;
ALTER TABLE bots ADD COLUMN IF NOT EXISTS trades_per_coin INTEGER DEFAULT 1;
ALTER TABLE bots ADD COLUMN IF NOT EXISTS gate_dca_enabled BOOLEAN DEFAULT FALSE;
ALTER TABLE bots ADD COLUMN IF NOT EXISTS gate_timer_enabled BOOLEAN DEFAULT FALSE;
ALTER TABLE bots ADD COLUMN IF NOT EXISTS gate_timer_hours INTEGER DEFAULT 5;
ALTER TABLE bots ADD COLUMN IF NOT EXISTS order_entry_type VARCHAR(10) DEFAULT 'market';
ALTER TABLE bots ADD COLUMN IF NOT EXISTS order_dca_type VARCHAR(10) DEFAULT 'market';

-- Position level tracking
ALTER TABLE positions ADD COLUMN IF NOT EXISTS sequence_number INTEGER DEFAULT 1;
ALTER TABLE positions ADD COLUMN IF NOT EXISTS is_gate_reference BOOLEAN DEFAULT FALSE;
ALTER TABLE positions ADD COLUMN IF NOT EXISTS coin_trade_number INTEGER DEFAULT 1;

SELECT 'Multi-trade gate and limit order columns added!' AS result;

-- Gate reference tracking
ALTER TABLE positions ADD COLUMN IF NOT EXISTS base_coin VARCHAR(10) DEFAULT 'USDT';
ALTER TABLE positions ADD COLUMN IF NOT EXISTS gate_reference_since TIMESTAMP;

-- Pending limit orders
CREATE TABLE IF NOT EXISTS pending_limit_orders (
    id SERIAL PRIMARY KEY,
    position_id INTEGER REFERENCES positions(id),
    bot_id INTEGER REFERENCES bots(id),
    exchange_id INTEGER REFERENCES exchanges(id),
    order_type VARCHAR(20) NOT NULL,
    exchange_order_id VARCHAR(100) UNIQUE,
    original_quantity DECIMAL(20,8) NOT NULL,
    filled_quantity DECIMAL(20,8) DEFAULT 0,
    remaining_quantity DECIMAL(20,8),
    limit_price DECIMAL(20,8) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    placed_at TIMESTAMP DEFAULT NOW(),
    filled_at TIMESTAMP,
    cancelled_at TIMESTAMP,
    last_checked TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_pending_limit_orders_status ON pending_limit_orders(status, exchange_id);
CREATE INDEX IF NOT EXISTS idx_pending_limit_orders_position ON pending_limit_orders(position_id);

SELECT 'Final v6 fixes applied!' AS result;
