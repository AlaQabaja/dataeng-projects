import argparse
from sqlalchemy import create_engine, text
import requests
import logging
from typing import TypedDict
from utils import *
from questrade import Questrade
from datetime import datetime

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO,  format='%(asctime)s - %(levelname)s - %(message)s')

def get_questrade_token_and_server(token_file):
    # read existing information
    access_token_yaml = get_access_token_yaml(token_file)
    # do authorization
    authorize_access_token(access_token_yaml['access_token'], access_token_yaml['refresh_token'], access_token_yaml['api_server'])
    # read new authorization from file 
    access_token_yaml_new = get_access_token_yaml(token_file)
    return access_token_yaml_new['access_token'], access_token_yaml_new['api_server'], access_token_yaml_new['refresh_token']

access_token, api_server, next_refresh_token = get_questrade_token_and_server('access_token.yaml')
logging.info(f'using access_token: {access_token} api server: {api_server}, refresh token: {next_refresh_token}')
questrade_obj = Questrade(access_token, api_server)
account_ids = questrade_obj.get_account_ids()
account_info = questrade_obj.get_accounts_info()
today_date = datetime.today().strftime('%Y-%m-%d')

def main(params):
    user = params.user 
    password = params.password 
    host = params.host
    port = params.port 
    db = params.db
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')
    with engine.connect() as conn:
        with conn.begin():
            for account in account_info:
                logging.info(f'Writing account {account}')
                conn.execute(
                text("INSERT INTO accounts (account_number, account_type, account_status) VALUES (:number, :type, :status)"),
                {"number": account["number"], "type": account["type"], "status": account["status"]}
            )
                # Load Data into PostgreSQL
            logging.info('Done writing account info')
            logging.info('Delete position data')
            conn.execute(
                 text('DELETE FROM positions WHERE day = :day'),
                 {"day" : today_date}
            )
            for account_id in account_ids:
                positions = questrade_obj.get_account_positions(account_id)
                for position in positions:
                    logging.info(f'Writing positions')
                    conn.execute(
                    text("INSERT INTO positions (account_number, average_entry_price, closed_pnl, closed_quantity, current_market_value, current_price, open_pnl, open_quantity, symbol, symbol_id, total_cost, day ) VALUES (:account_number, :average_entry_price, :closed_pnl, :closed_quantity, :current_market_value, :current_price, :open_pnl, :open_quantity, :symbol, :symbol_id, :total_cost, :day)"),
                    {"account_number": account_id, "average_entry_price": position['averageEntryPrice'], "closed_pnl": position['closedPnl'], "closed_quantity": position['closedQuantity'], "current_market_value": position['currentMarketValue'], "current_price": position['currentPrice'], "open_pnl": position['openPnl'], "open_quantity": position['openQuantity'], "symbol": position['symbol'], "symbol_id": position['symbolId'], "total_cost": position['totalCost'], "day": today_date}
                    )
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ingest Questrade Data Into Database')
    parser.add_argument('--user', required=True, help='user name for postgres')
    parser.add_argument('--password', required=True, help='password for postgres')
    parser.add_argument('--host', required=True, help='host for postgres')
    parser.add_argument('--port', required=True, help='port for postgres')
    parser.add_argument('--db', required=True, help='database name for postgres')
    args = parser.parse_args()
    main(args)

