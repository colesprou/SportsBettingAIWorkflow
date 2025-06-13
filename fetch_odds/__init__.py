import logging
import os
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine
from fetch_and_store_mlb_props import fetch_game_data, insert_data, get_todays_game_ids
from betting_functions import fetch_sports_markets
import azure.functions as func

def main(mytimer: func.TimerRequest) -> None:
    logging.info("⏰ Azure Function triggered")

    try:
        # Load config
        engine = create_engine(os.getenv("PG_CONN"))
        api_key = os.getenv("ODDSJAM_API_KEY")

        # Fetch game IDs
        game_data_dict = get_todays_game_ids(api_key, league="MLB")
        game_ids = list(game_data_dict.keys())
        logging.info(f"🔍 Found {len(game_ids)} games")

        # Fetch data
        df = fetch_game_data(game_ids=game_ids, api_key=api_key, sport="baseball", league="MLB")
        logging.info(f"📊 Retrieved {len(df)} rows from API")

        if not df.empty:
            df['fetched_at'] = datetime.utcnow()
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

            logging.info("💾 Inserting into PostgreSQL...")
            insert_data(df, engine)
            logging.info("✅ Insert complete")

        else:
            logging.info("⚠️ No data to insert.")

    except Exception as e:
        logging.error(f"❌ Error: {e}")
