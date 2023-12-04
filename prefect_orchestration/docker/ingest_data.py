import os 
import argparse 
from time import time
from datetime import timedelta
import pandas as pd 
from sqlalchemy import create_engine
from prefect import flow, task

@task(log_prints=True)
def extract_data(url):
    # keep the original formatting
    if url.endswith('.csv.gz'):
        csv_name = 'output.csv.gz'
    else:
        csv_name = 'output.csv'
    os.system(f"wget {url} -O {csv_name}")
    df_iter = pd.read_csv(csv_name, iterator=True, chunksize=100000)
    df = next(df_iter)
    return df

@task(log_prints=True)
def transform(df):
    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
    return df

@task(log_prints = True)
def ingest_data(df, table_name, user, password, host, port, db):
    target_engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')
    # create schema once 
    df.head(n=0).to_sql(name=table_name, con=target_engine, if_exists='replace')
    # append data from first iteration 
    df.to_sql(name=table_name, con=target_engine, if_exists='append')

@flow(name="Ingest Flow")
def main(params):
    user = params.user 
    password = params.password 
    host = params.host
    port = params.port 
    db = params.db
    table_name = params.table_name
    url = params.url 

    raw_data = extract_data(url)
    transformed_data = transform(raw_data)
    ingest_data(transformed_data, table_name, user, password, host, port, db)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ingest CSV data to Postgres')
    parser.add_argument('--user', required=True, help='user name for postgres')
    parser.add_argument('--password', required=True, help='password for postgres')
    parser.add_argument('--host', required=True, help='host for postgres')
    parser.add_argument('--port', required=True, help='port for postgres')
    parser.add_argument('--db', required=True, help='database name for postgres')
    parser.add_argument('--table_name', required=True, help='name of the table where we will write the results to')
    parser.add_argument('--url', required=True, help='url of the csv file')

    args = parser.parse_args()

    main(args)
