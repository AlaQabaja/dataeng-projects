import argparse
from sqlalchemy import create_engine, text
import requests
import logging
from typing import TypedDict
from utils import *
from questrade import Questrade
from datetime import datetime, timedelta

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)
logging.basicConfig(level=logging.ERROR,  format='%(asctime)s - %(levelname)s - %(message)s')

def get_questrade_token_and_server(token_file):
    # read existing information
    access_token_yaml = get_access_token_yaml(token_file)
    # do authorization
    authorize_access_token(access_token_yaml['access_token'], access_token_yaml['refresh_token'], access_token_yaml['api_server'])
    # read new authorization from file 
    access_token_yaml_new = get_access_token_yaml(token_file)
    return access_token_yaml_new['access_token'], access_token_yaml_new['api_server'], access_token_yaml_new['refresh_token']

def date_time_to_date (date_time_str):
    input_dt = datetime.fromisoformat(date_time_str)
    return input_dt.strftime('%Y-%m-%d')

def create_date_chunks_from_range(start_date, end_date, chunk_size=30):
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    chunks = []
    current_start = start_date

    while current_start <= end_date:
        # Ensure the last chunk ends exactly on end_date
        current_end = min(current_start + timedelta(days=chunk_size - 1), end_date)
        
        chunks.append({
            "start_date": current_start.strftime("%Y-%m-%d"),
            "end_date": current_end.strftime("%Y-%m-%d")
        })
        
        # Move to the next chunk, starting one day after current_end
        current_start = current_end + timedelta(days=1)
    
    return chunks

def load_accounts(engine, account_info):
    with engine.connect() as conn:
        with conn.begin():
            conn.execute(
                text("DELETE FROM accounts")
            )
        for account in account_info:
            logging.info(f'Writing account {account}')
            conn.execute(
                text("""INSERT INTO accounts (account_number
                                             ,account_type
                                             ,account_status) 
                        VALUES (:number
                               , :type
                     , :status)"""),
                {"number": account["number"]
                , "type": account["type"]
                , "status": account["status"]}
            )
    logging.info('Done writing account info')

def load_positions(engine, account_ids, questrade_obj, today_date):
    with engine.connect() as conn:
        with conn.begin():
            conn.execute(
                text('DELETE FROM positions WHERE day = :day'),
                {"day": today_date}
            )
            for account_id in account_ids:
                positions = questrade_obj.get_account_positions(account_id)
                for position in positions:
                    logging.info(f'Writing positions')
                    conn.execute(
                        text("""INSERT INTO positions 
                            (account_number
                            , average_entry_price
                            , closed_pnl
                            , closed_quantity
                            , current_market_value
                            , current_price
                            , open_pnl
                            , open_quantity
                            , symbol, symbol_id
                            , total_cost
                            , day ) 
                    VALUES (:account_number
                            , :average_entry_price
                            , :closed_pnl
                            , :closed_quantity
                            , :current_market_value
                            , :current_price
                            , :open_pnl
                            , :open_quantity
                            , :symbol
                            , :symbol_id
                            , :total_cost
                            , :day)"""),
                        {"account_number": account_id
                        , "average_entry_price": position['averageEntryPrice']
                        , "closed_pnl": position['closedPnl']
                        , "closed_quantity": position['closedQuantity']
                        , "current_market_value": position['currentMarketValue']
                        , "current_price": position['currentPrice']
                        , "open_pnl": position['openPnl']
                        , "open_quantity": position['openQuantity']
                        , "symbol": position['symbol']
                        , "symbol_id": position['symbolId']
                        , "total_cost": position['totalCost']
                        , "day": today_date}
                    )
        logging.info("Done writing positions info")

def load_account_balance(engine, account_ids, questrade_obj, today_date):
     with engine.connect() as conn:
        with conn.begin():
            conn.execute(
                text('DELETE FROM account_balances WHERE day = :day'),
                {"day": today_date}
            )
            for account_id in account_ids:
                account_balances = questrade_obj.get_account_balances(account_id)
                logging.info(f"account balances object {account_balances}")
                for account_balance in account_balances['perCurrencyBalances']:
                    logging.info(f'Writing account per currency balances')
                    conn.execute(
                        text("""INSERT INTO account_balances 
                        (account_number
                         , currency
                         , cash
                         , market_value
                         , total_equity
                         , buying_power
                         , maintenance_excess
                         , balance_type
                         , day)
                     VALUES (:account_number
                             , :currency
                             , :cash
                             , :market_value
                             , :total_equity
                             , :buying_power
                             , :maintenance_excess
                             , :balance_type
                             , :day)"""),
                        {"account_number": account_id
                         , "currency": account_balance['currency']
                         , "cash": account_balance['cash']
                         , "market_value": account_balance['marketValue']
                         , "total_equity": account_balance['totalEquity']
                         , "buying_power": account_balance['buyingPower']
                         , "maintenance_excess": account_balance['maintenanceExcess']
                         , "balance_type": "per_currency"
                         , "day": today_date}
                    )
                for account_balance in account_balances['combinedBalances']:
                    logging.info(f'Writing account combined balances')
                    conn.execute(
                        text("""INSERT INTO account_balances (
                             account_number
                             , currency
                             , cash
                             , market_value
                             , total_equity
                             , buying_power
                             , maintenance_excess
                             , balance_type
                             , day) VALUES (
                             :account_number
                             , :currency
                             , :cash
                             , :market_value
                             , :total_equity
                             , :buying_power
                             , :maintenance_excess
                             , :balance_type
                             , :day)"""),
                        {"account_number": account_id
                         , "currency": account_balance['currency']
                         , "cash": account_balance['cash']
                         , "market_value": account_balance['marketValue']
                         , "total_equity": account_balance['totalEquity']
                         , "buying_power": account_balance['buyingPower']
                         , "maintenance_excess": account_balance['maintenanceExcess']
                         , "balance_type": "combined"
                         , "day": today_date
                        }
                    )
     logging.info("Done writing account balances")

def load_account_activities(engine, account_ids, questrade_obj, start_date, end_date, today_date):
    with engine.connect() as conn:
        with conn.begin():
            conn.execute(
                text('DELETE FROM account_activities WHERE transaction_date between :start_date and :end_date'),
                {"start_date": start_date, "end_date": end_date}
            )
            for account_id in account_ids:
                activities = questrade_obj.get_account_activities(account_id= account_id, start_date= start_date, end_date= end_date)
                for activity in activities:
                    logging.info(f'Writing account activities {activity}')
                    conn.execute(
                        text("""INSERT INTO account_activities (
                                  account_number
                                , trade_time
                                , trade_date
                                , transaction_time
                                , transaction_date
                                , settlement_time
                                , settlement_date
                                , action
                                , symbol
                                , symbol_id
                                , description
                                , currency
                                , quantity
                                , price
                                , gross_amount
                                , commission
                                , net_amount
                                , type
                                , today_date
                             ) VALUES (
                              :account_number
                            , :trade_time
                            , :trade_date
                            , :transaction_time
                            , :transaction_date
                            , :settlement_time
                            , :settlement_date
                            , :action
                            , :symbol
                            , :symbol_id
                            , :description
                            , :currency
                            , :quantity
                            , :price
                            , :gross_amount
                            , :commission
                            , :net_amount
                            , :type
                            , :today_date
                             )"""
                        ),
                        {
                            "account_number" : account_id,
                            "trade_time" : activity.get('tradeDate', ''),
                            "trade_date" : date_time_to_date(activity.get('tradeDate', '')),
                            "transaction_time" : activity.get('transactionDate', ''),
                            "transaction_date" : date_time_to_date(activity.get('transactionDate', '')),
                            "settlement_time" : activity.get('settlementDate', ''),
                            "settlement_date" : date_time_to_date(activity.get('settlementDate', '')),
                            "action" : activity.get('action', ''),
                            "symbol" : activity.get('symbol', ''),
                            "symbol_id" : activity.get('symbolId', ''),
                            "description" : activity.get('description', ''),
                            "currency" : activity.get('currency', ''),
                            "quantity" : activity.get('quantity', ''),
                            "price" : activity.get('price', ''),
                            "gross_amount" : activity.get('grossAmount', ''),
                            "commission" : activity.get('commission', ''),
                            "net_amount" : activity.get('netAmount', ''),
                            "type" : activity.get('type', ''),
                            "today_date" : today_date
                        }
                    )
    logging.info("Done writing account activities")

start_date = "2023-01-01"
end_date = "2025-02-08"
date_chunks = create_date_chunks_from_range(start_date, end_date)

access_token, api_server, next_refresh_token = get_questrade_token_and_server('access_token.yaml')
logging.info(f'using access_token: {access_token} api server: {api_server}, refresh token: {next_refresh_token}')
questrade_obj = Questrade(access_token, api_server)
account_ids = questrade_obj.get_account_ids()
account_info = questrade_obj.get_accounts_info()
today_date = datetime.today().strftime('%Y-%m-%d')
today_date_obj = datetime.strptime(today_date, '%Y-%m-%d')


def main(params):
    user = params.user 
    password = params.password 
    host = params.host
    port = params.port 
    db = params.db
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')
    load_accounts(engine, account_info)
    load_positions(engine, account_ids, questrade_obj, today_date)
    load_account_balance(engine, account_ids, questrade_obj, today_date)
    for date_chunk in date_chunks:
        logging.info(f"Processing date chunk: {date_chunk}")
        start_date = date_chunk['start_date']
        end_date = date_chunk['end_date']
        load_account_activities(engine, account_ids, questrade_obj, start_date, end_date, today_date)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ingest Questrade Data Into Database')
    parser.add_argument('--user', required=True, help='user name for postgres')
    parser.add_argument('--password', required=True, help='password for postgres')
    parser.add_argument('--host', required=True, help='host for postgres')
    parser.add_argument('--port', required=True, help='port for postgres')
    parser.add_argument('--db', required=True, help='database name for postgres')
    args = parser.parse_args()
    main(args)

