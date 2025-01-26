sql_create_accounts_tbl = """
CREATE TABLE IF NOT EXISTS accounts (
    id SERIAL PRIMARY KEY,
    account_number VARCHAR(20),
    account_type VARCHAR(50),
    account_status VARCHAR(20)
);
"""

sql_create_positions_tbl = """
CREATE TABLE IF NOT EXISTS positions (
    id SERIAL PRIMARY KEY,
    account_number VARCHAR(20),
    average_entry_price NUMERIC(10, 2), -- Price with up to 2 decimal places
    closed_pnl NUMERIC(10, 2),         -- Profit/Loss with up to 2 decimal places
    closed_quantity INTEGER,           -- Number of closed quantities
    current_market_value NUMERIC(10, 2), -- Current market value with up to 2 decimal places
    current_price NUMERIC(10, 2),      -- Current price with up to 2 decimal places
    is_real_time BOOLEAN,              -- Boolean to indicate real-time status
    is_under_reorg BOOLEAN,            -- Boolean to indicate reorganization status
    open_pnl NUMERIC(10, 2),           -- Open profit/loss
    open_quantity INTEGER,             -- Number of open quantities
    symbol VARCHAR(50),                -- Stock symbol
    symbol_id BIGINT,                  -- Unique identifier for the symbol
    total_cost NUMERIC(10, 2),          -- Total cost with up to 2 decimal places
    day DATE                          -- load day
);
"""