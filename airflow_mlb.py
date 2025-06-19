from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os
sys.path.append("/Users/colesprouse/Desktop/Projects/SportsBettingAgent")

from fetch_and_store_mlb_props import fetch_game_data, insert_data, get_todays_game_ids
from betting_functions import fetch_sports_markets
from sqlalchemy import create_engine
import pandas as pd

default_args = {
    'owner': 'you',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def fetch_and_store():
    engine = create_engine("postgresql+psycopg2://sb_user:Barleysmu22!@localhost:5432/sb_data")
    api_key = '540d8b29-e704-403d-9926-363d3d7fcaff'
    game_data_dict = get_todays_game_ids(api_key, league='MLB')
    game_ids = list(game_data_dict.keys())

    print(f"🔍 Found {len(game_ids)} games", flush=True)

    df = fetch_game_data(game_ids=game_ids, api_key=api_key, sport='baseball', league='MLB')
    print(f"📊 Retrieved {len(df)} rows from API", flush=True)

    if not df.empty:
        df['fetched_at'] = datetime.now()
        df = df.rename(columns={
            'Game ID': 'game_id',
            'Game Name': 'game_name',
            'Player Name': 'player_name',
            'Bet Name': 'bet_name',
            'Market Name': 'market_name',
            'Grouping Key': 'grouping_key',
            'Sportsbook': 'sportsbook',
            'Odds': 'odds'
        })

        print("💾 Inserting into database...", flush=True)
        insert_data(df, engine)
        print("✅ Insert complete", flush=True)

with DAG(
    dag_id='mlb_odds_ingestion',
    default_args=default_args,
    start_date=datetime(2025, 6, 12),
    schedule_interval='*/30 * * * *',  # every 30 mins
    catchup=False
) as dag:
    ingest_task = PythonOperator(
        task_id='fetch_and_store_mlb_odds',
        python_callable=fetch_and_store
    )