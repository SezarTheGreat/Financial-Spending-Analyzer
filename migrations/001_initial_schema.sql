-- 001_initial_schema.sql
-- Supabase PostgreSQL DDL for FinWise Tri-Hybrid RAG Platform

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table: fund_master
CREATE TABLE IF NOT EXISTS fund_master (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    amfi_code VARCHAR(20) UNIQUE NOT NULL,
    scheme_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    plan_type VARCHAR(50),
    nav_latest DECIMAL(10, 4),
    nav_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_fund_master_amfi ON fund_master(amfi_code);

-- Table: exit_load_schedules
CREATE TABLE IF NOT EXISTS exit_load_schedules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    amfi_code VARCHAR(20) REFERENCES fund_master(amfi_code) ON DELETE CASCADE,
    condition_text TEXT NOT NULL,
    load_percentage DECIMAL(5, 2) NOT NULL,
    days_limit INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_exit_load_amfi ON exit_load_schedules(amfi_code);

-- Table: scheme_mandates
CREATE TABLE IF NOT EXISTS scheme_mandates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    amfi_code VARCHAR(20) REFERENCES fund_master(amfi_code) ON DELETE CASCADE,
    min_equity_pct DECIMAL(5, 2),
    max_equity_pct DECIMAL(5, 2),
    min_debt_pct DECIMAL(5, 2),
    max_debt_pct DECIMAL(5, 2),
    benchmark_index VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_scheme_mandates_amfi ON scheme_mandates(amfi_code);

-- Table: chat_sessions
CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID, -- For future auth
    risk_profile VARCHAR(50) DEFAULT 'Moderate',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table: chat_messages
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_chat_messages_session ON chat_messages(session_id);

-- Row Level Security (RLS)
ALTER TABLE fund_master ENABLE ROW LEVEL SECURITY;
ALTER TABLE exit_load_schedules ENABLE ROW LEVEL SECURITY;
ALTER TABLE scheme_mandates ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;

-- Allow anonymous read on public tables
CREATE POLICY "Allow anonymous read on fund_master" ON fund_master FOR SELECT USING (true);
CREATE POLICY "Allow anonymous read on exit_load_schedules" ON exit_load_schedules FOR SELECT USING (true);
CREATE POLICY "Allow anonymous read on scheme_mandates" ON scheme_mandates FOR SELECT USING (true);

-- Allow anonymous insert/select on chat (for stateless demo)
CREATE POLICY "Allow anonymous all on chat_sessions" ON chat_sessions FOR ALL USING (true);
CREATE POLICY "Allow anonymous all on chat_messages" ON chat_messages FOR ALL USING (true);
