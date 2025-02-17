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

sql_create_account_balances_tbl = """
 CREATE TABLE IF NOT EXISTS account_balances 
 (
	 id SERIAL PRIMARY KEY,
	 account_number VARCHAR(20),
	 currency VARCHAR(5),
	 cash NUMERIC(10,4),
	 market_value NUMERIC(10,4),
	 total_equity NUMERIC(10,4),
	 buying_power NUMERIC(10,4),
	 maintenance_excess NUMERIC(10,4),
	 balance_type VARCHAR(20),
	 day DATE
	 
 );
"""

sql_create_account_activities_tbl = """
CREATE TABLE IF NOT EXISTS account_activities 
(
	id SERIAL PRIMARY KEY, 
	account_number VARCHAR(20),
	trade_time TIMESTAMPTZ,
	trade_date DATE,
	transaction_time TIMESTAMPTZ,
	transaction_date DATE,
	settlement_time TIMESTAMPTZ,
	settlement_date DATE,
	action VARCHAR(20),
	symbol VARCHAR(20),
	symbol_id BIGINT,
	description TEXT,
	currency VARCHAR(10),
	quantity BIGINT,
	price NUMERIC(10,4),
	gross_amount NUMERIC(10,4),
	commission NUMERIC(10,4),
	net_amount NUMERIC(10,4),
	type VARCHAR(30),
    day DATE
);
"""