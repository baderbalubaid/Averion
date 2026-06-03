-- Migration 002: Post Session 5 AI Review fixes
-- Run: python3 run_migration.py 002
-- Bugs fixed: 8-16 · Gaps: 1-7

-- Bug 9: PENDING_BUYBACK
ALTER TABLE positions ADD COLUMN IF NOT EXISTS pending_buyback_usdt_locked DECIMAL(20,8) DEFAULT 0;
ALTER TABLE positions ADD COLUMN IF NOT EXISTS pending_buyback_expires_at TIMESTAMP;

-- Bug 12: Research account bypass
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_research_account BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS trade_limit_bypass BOOLEAN DEFAULT FALSE;

-- Bug 14: Champion challenger tracking
ALTER TABLE smart_dca_champions ADD COLUMN IF NOT EXISTS challenger_method VARCHAR(20);
ALTER TABLE smart_dca_champions ADD COLUMN IF NOT EXISTS challenger_rars DECIMAL(10,4);
ALTER TABLE smart_dca_champions ADD COLUMN IF NOT EXISTS challenger_weeks INTEGER DEFAULT 0;
ALTER TABLE smart_dca_champions ADD COLUMN IF NOT EXISTS challenge_start_date DATE;
ALTER TABLE smart_dca_champions ADD COLUMN IF NOT EXISTS challenger_trades INTEGER DEFAULT 0;

-- Bug 15: Client order ID
ALTER TABLE trades ADD COLUMN IF NOT EXISTS client_order_id VARCHAR(100);
ALTER TABLE trades ADD COLUMN IF NOT EXISTS reconciled_at TIMESTAMP;
ALTER TABLE trades ADD COLUMN IF NOT EXISTS reconciliation_status VARCHAR(20) DEFAULT 'pending';

-- Gap 1: Security audit log
CREATE TABLE IF NOT EXISTS security_audit_log (
   id BIGSERIAL PRIMARY KEY,
   user_id INTEGER REFERENCES users(id),
   action VARCHAR(100) NOT NULL,
   entity_type VARCHAR(50),
   entity_id INTEGER,
   ip_address VARCHAR(45),
   user_agent TEXT,
   details JSONB DEFAULT '{}',
   created_at TIMESTAMP DEFAULT NOW()
);

-- Gap 4: Rate limits
CREATE TABLE IF NOT EXISTS rate_limits (
   id BIGSERIAL PRIMARY KEY,
   ip_address VARCHAR(45) NOT NULL,
   endpoint VARCHAR(100) NOT NULL,
   attempt_count INTEGER DEFAULT 1,
   window_start TIMESTAMP DEFAULT NOW(),
   created_at TIMESTAMP DEFAULT NOW()
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_rate_ip_endpoint ON rate_limits(ip_address, endpoint);

-- Gap 5: Migration tracking
CREATE TABLE IF NOT EXISTS schema_migrations (
   id SERIAL PRIMARY KEY,
   version VARCHAR(20) NOT NULL UNIQUE,
   description TEXT,
   applied_at TIMESTAMP DEFAULT NOW(),
   applied_by VARCHAR(100) DEFAULT 'system'
);

INSERT INTO schema_migrations (version, description)
VALUES
 ('001', 'Initial schema setup'),
 ('002', 'Post Session 5 AI Review fixes')
ON CONFLICT (version) DO NOTHING;

SELECT 'Migration 002 complete' AS status;
