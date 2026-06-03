-- Migration 001: Initial schema
-- Applied automatically by hetzner_day1.sh
-- Run: psql $DB_URL < migrations/001_initial.sql
-- See setup/schema.sql for full initial schema
SELECT 'Migration 001 complete' AS status;
