-- ====================================================================
-- FinWise Mutual Fund AI Chatbot (Groww G.1 Architecture) Migration
-- PostgreSQL Schema with pgvector, HNSW Indexes & Hybrid Vector Search
-- ====================================================================

-- 1. Enable Required Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- 2. User Conversation Sessions
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    risk_profile TEXT CHECK (risk_profile IN ('Conservative', 'Moderate', 'Aggressive')) DEFAULT 'Moderate',
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 3. Chat History (Stores native Gemini Content parts & role structures)
CREATE TABLE IF NOT EXISTS chat_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES user_sessions(id) ON DELETE CASCADE NOT NULL,
    role TEXT CHECK (role IN ('user', 'model', 'function')) NOT NULL,
    content JSONB NOT NULL,
    tokens_used INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 4. Mutual Fund Master & Performance Metadata
CREATE TABLE IF NOT EXISTS fund_master (
    amfi_code TEXT PRIMARY KEY,
    isin_growth TEXT,
    isin_div_reinvest TEXT,
    scheme_name TEXT NOT NULL,
    fund_house TEXT NOT NULL,
    category TEXT NOT NULL,
    sub_category TEXT NOT NULL,
    ter NUMERIC(4,2),
    aum_crores NUMERIC(12,2),
    latest_nav NUMERIC(10,4),
    nav_date DATE,
    benchmark_name TEXT,
    equity_split NUMERIC(5,2) DEFAULT 0.0,
    debt_split NUMERIC(5,2) DEFAULT 0.0,
    cash_split NUMERIC(5,2) DEFAULT 0.0,
    top_10_holdings JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 5. RAG Document Chunks (SIDs, KIMs, Factsheets, Regulations)
CREATE TABLE IF NOT EXISTS document_embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    amfi_code TEXT REFERENCES fund_master(amfi_code) ON DELETE CASCADE,
    fund_house TEXT NOT NULL,
    document_type TEXT CHECK (document_type IN ('SID', 'KIM', 'FACTSHEET', 'REGULATION')) NOT NULL,
    section_name TEXT NOT NULL,
    chunk_content TEXT NOT NULL,
    document_date DATE NOT NULL,
    embedding VECTOR(768),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 6. High-Performance HNSW & Relational Indexes
CREATE INDEX IF NOT EXISTS idx_doc_embeddings_hnsw ON document_embeddings 
USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);

CREATE INDEX IF NOT EXISTS idx_doc_amfi_code ON document_embeddings(amfi_code);
CREATE INDEX IF NOT EXISTS idx_doc_fund_house ON document_embeddings(fund_house);
CREATE INDEX IF NOT EXISTS idx_doc_type ON document_embeddings(document_type);
CREATE INDEX IF NOT EXISTS idx_chat_session ON chat_history(session_id, created_at ASC);
CREATE INDEX IF NOT EXISTS idx_fund_category ON fund_master(category);
CREATE INDEX IF NOT EXISTS idx_fund_house ON fund_master(fund_house);

-- 7. Macro & Regulatory Daily Context Cache
CREATE TABLE IF NOT EXISTS market_macro_context (
    id SERIAL PRIMARY KEY,
    summary_date DATE UNIQUE NOT NULL,
    macro_brief TEXT NOT NULL,
    nifty_pe NUMERIC(5,2),
    gsec_10y_yield NUMERIC(4,2),
    recent_sebi_circulars JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 8. Hybrid Vector Search Stored Procedure
CREATE OR REPLACE FUNCTION match_fund_documents (
    query_embedding VECTOR(768),
    filter_amfi_code TEXT DEFAULT NULL,
    filter_doc_type TEXT DEFAULT NULL,
    match_count INT DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    amfi_code TEXT,
    fund_house TEXT,
    document_type TEXT,
    section_name TEXT,
    chunk_content TEXT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.id,
        d.amfi_code,
        d.fund_house,
        d.document_type,
        d.section_name,
        d.chunk_content,
        (1 - (d.embedding <=> query_embedding))::FLOAT AS similarity
    FROM document_embeddings d
    WHERE
        (filter_amfi_code IS NULL OR d.amfi_code = filter_amfi_code) AND
        (filter_doc_type IS NULL OR d.document_type = filter_doc_type)
    ORDER BY d.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- 9. Seed Data for Indian Mutual Funds (Groww G.1 Top Active Holdings)
INSERT INTO fund_master (
    amfi_code, isin_growth, scheme_name, fund_house, category, sub_category,
    ter, aum_crores, latest_nav, nav_date, benchmark_name,
    equity_split, debt_split, cash_split, top_10_holdings
) VALUES
(
    '122639', 'INF209K01166',
    'Parag Parikh Flexi Cap Fund - Direct Plan - Growth',
    'PPFAS Mutual Fund', 'Equity', 'Flexi Cap',
    0.63, 68420.50, 78.4520, '2026-08-14', 'NIFTY 500 TRI',
    84.20, 0.00, 15.80,
    '[{"stock": "HDFC Bank Ltd", "weight": 8.15}, {"stock": "Bajaj Holdings & Inv Ltd", "weight": 7.42}, {"stock": "ITC Ltd", "weight": 6.85}, {"stock": "Power Grid Corp of India", "weight": 5.92}, {"stock": "Coal India Ltd", "weight": 5.12}, {"stock": "Alphabet Inc (Google)", "weight": 4.88}, {"stock": "Microsoft Corp", "weight": 4.15}, {"stock": "ICICI Bank Ltd", "weight": 3.95}, {"stock": "Maruti Suzuki India", "weight": 3.65}, {"stock": "HCL Technologies", "weight": 3.40}]'::jsonb
),
(
    '127042', 'INF109K012R0',
    'Bandhan Small Cap Fund - Direct Plan - Growth',
    'Bandhan Mutual Fund', 'Equity', 'Small Cap',
    0.48, 6380.25, 42.1850, '2026-08-14', 'NIFTY Smallcap 250 TRI',
    94.50, 0.00, 5.50,
    '[{"stock": "Apar Industries Ltd", "weight": 4.12}, {"stock": "Arvind Ltd", "weight": 3.85}, {"stock": "Cholamandalam Financial", "weight": 3.60}, {"stock": "REC Ltd", "weight": 3.25}, {"stock": "Power Finance Corp", "weight": 3.10}, {"stock": "Birlasoft Ltd", "weight": 2.95}, {"stock": "Radico Khaitan Ltd", "weight": 2.80}, {"stock": "TVS Holdings Ltd", "weight": 2.65}, {"stock": "KEC International Ltd", "weight": 2.50}, {"stock": "V-Guard Industries", "weight": 2.40}]'::jsonb
),
(
    '120828', 'INF200K01UT4',
    'SBI Ultra Short Duration Fund - Direct Plan - Growth',
    'SBI Mutual Fund', 'Debt', 'Ultra Short Duration',
    0.34, 15890.00, 5214.8250, '2026-08-14', 'CRISIL Ultra Short Duration Debt B-I Index',
    0.00, 92.40, 7.60,
    '[{"stock": "NABARD CP (7.45%)", "weight": 9.20}, {"stock": "HDFC Bank CD (7.38%)", "weight": 8.50}, {"stock": "Small Industries Dev Bank CD", "weight": 7.80}, {"stock": "Axis Bank CD (7.40%)", "weight": 6.95}, {"stock": "REC Ltd Commercial Paper", "weight": 6.10}, {"stock": "91 Day Treasury Bill", "weight": 5.80}, {"stock": "182 Day Treasury Bill", "weight": 5.40}, {"stock": "Power Finance Corp CP", "weight": 4.90}, {"stock": "ICICI Bank CD", "weight": 4.75}, {"stock": "Canara Bank CD", "weight": 4.20}]'::jsonb
),
(
    '149022', 'INF204KB18R3',
    'Nippon India Growth Mid Cap Fund - Direct Plan - Growth',
    'Nippon India Mutual Fund', 'Equity', 'Mid Cap',
    0.88, 31450.80, 4125.6500, '2026-08-14', 'NIFTY Midcap 150 TRI',
    96.10, 0.00, 3.90,
    '[{"stock": "Cholamandalam Investment", "weight": 4.60}, {"stock": "Federal Bank Ltd", "weight": 3.95}, {"stock": "Persistent Systems Ltd", "weight": 3.75}, {"stock": "Max Financial Services", "weight": 3.45}, {"stock": "Voltas Ltd", "weight": 3.20}, {"stock": "Supreme Industries Ltd", "weight": 3.10}, {"stock": "Bharat Forge Ltd", "weight": 2.95}, {"stock": "APL Apollo Tubes Ltd", "weight": 2.80}, {"stock": "Coforge Ltd", "weight": 2.65}, {"stock": "AU Small Finance Bank", "weight": 2.50}]'::jsonb
),
(
    '120503', 'INF966L01683',
    'Quant Multi Asset Allocation Fund - Direct Plan - Growth',
    'Quant Mutual Fund', 'Hybrid', 'Multi Asset Allocation',
    0.72, 11240.60, 134.8200, '2026-08-14', 'Multi Asset Blended Index',
    52.40, 24.10, 23.50,
    '[{"stock": "Reliance Industries Ltd", "weight": 9.40}, {"stock": "Jio Financial Services", "weight": 7.15}, {"stock": "HDFC Bank Ltd", "weight": 5.80}, {"stock": "Adani Power Ltd", "weight": 4.95}, {"stock": "Physical Gold ETF", "weight": 14.50}, {"stock": "Physical Silver ETF", "weight": 8.60}, {"stock": "7.18% GS 2033 (Sovereign)", "weight": 12.40}, {"stock": "7.30% GS 2053 (Sovereign)", "weight": 8.20}, {"stock": "Steel Authority of India", "weight": 3.40}, {"stock": "IRCTC Ltd", "weight": 2.85}]'::jsonb
)
ON CONFLICT (amfi_code) DO UPDATE SET
    latest_nav = EXCLUDED.latest_nav,
    nav_date = EXCLUDED.nav_date,
    aum_crores = EXCLUDED.aum_crores,
    top_10_holdings = EXCLUDED.top_10_holdings;

-- 10. Seed Market Macro Context
INSERT INTO market_macro_context (summary_date, macro_brief, nifty_pe, gsec_10y_yield, recent_sebi_circulars)
VALUES (
    '2026-08-15',
    'Indian equity markets trade with resilient domestic SIP inflows exceeding ₹24,000 Cr/month. RBI maintains repo rate at 6.50% ensuring stable short-term money market yields. Small-cap valuations require disciplined portfolio rebalancing.',
    22.45,
    6.98,
    '[{"title": "SEBI Mandate on Direct Plan Transparency", "date": "2026-06-01", "summary": "AMCs must explicitly disclose exact distributor commission rupee differentials in periodic account statements."}, {"title": "SEBI True-to-Label Categorization Norms", "date": "2026-04-15", "summary": "Strict enforcement of 80% minimum allocation for thematic and mid-cap equity fund mandates."}]'::jsonb
)
ON CONFLICT (summary_date) DO NOTHING;
