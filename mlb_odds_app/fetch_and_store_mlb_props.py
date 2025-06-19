import requests
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime
from betting_functions import get_todays_game_ids, fetch_game_data,fetch_sports_markets
from datetime import datetime

OPTIC_ODDS_BASE = 'https://api.opticodds.com/api/v3'

def fetch_game_data(game_ids, api_key, market_type='game', sport='baseball', league='MLB', sportsbooks=None, include_player_name=True, is_live='false'):
    # Validate inputs
    if sportsbooks is None:
        sportsbooks = ['Pinnacle', 'FanDuel', 'DraftKings']

    # Fetch game names
    game_data_dict = get_todays_game_ids(api_key, league, is_live=is_live)
    if not game_data_dict:
        print("No game data found.")
        return pd.DataFrame()

    # Fetch markets for the given sport and league
    markets_df = fetch_sports_markets(api_key, sport, league, sportsbooks)
    if market_type == 'player':
        markets = markets_df[markets_df['name'].str.contains('Player', case=False)]['name'].tolist()
    elif market_type == 'game':
        markets = markets_df[~markets_df['name'].str.contains('Player', case=False)]['name'].tolist()
    else:
        print(f"Unknown market type: {market_type}")
        return pd.DataFrame()
    
    if league == 'MLB':
        markets = [
    # Main game lines
    "Moneyline", "Run Line", "Total Runs", "Team Total",

    # 1st half main lines
    "1st Half Moneyline", "1st Half Run Line", "1st Half Total Runs", "1st Half Team Total",

    # Player props
    "Player Bases", "Player Earned Runs", "Player Hits Allowed",
    "Player Home Runs", "Player Home Runs Yes/No", "Player Outs",
    "Player Strikeouts", "Player Batting Strikeouts", "Player Batting Walks",
    "Player Doubles", "Player Hits", "Player Hits + Runs + RBIs",
    "Player RBIs", "Player Runs", "Player Singles", "Player Stolen Bases",
    "Player Triples", "Player Walks", "Player To Record Win"
        ]
    else:
        markets = markets

    url = "https://api.opticodds.com/api/v3/fixtures/odds"
    all_data = []  # Collect all data across sportsbooks and chunks

    for chunk in [game_ids[i:i + 5] for i in range(0, len(game_ids), 5)]:
        for sportsbook in sportsbooks:
            params = {
                'key': api_key,
                'sportsbook': sportsbook,
                'fixture_id': chunk,
                'market_name': markets
            }
            if is_live != 'false':
                params['status'] = 'live'

            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json().get('data', [])
                for game_data in data:
                    # Add sportsbook info to each record
                    for item in game_data.get('odds', []):
                        all_data.append({
                            'Game ID': game_data.get('id', 'Unknown'),
                            'Game Name': game_data_dict.get(game_data.get('id', 'Unknown'), 'Unknown Game'),
                            'Bet Name': item.get('name', None),
                            'Market Name': item.get('market', ''),
                            'Grouping Key':item.get('grouping_key',''),
                            'Sportsbook': sportsbook,
                            'line': item.get('points', None),
                            'Odds': item.get('price', None)
                        })
            else:
                print(f"Error fetching data for sportsbook {sportsbook}: {response.status_code} - {response.text}")

    return pd.DataFrame(all_data)

"""

"""
def insert_data(df, engine):
    try:
        df.to_sql(
            name="mlb_odds",
            con=engine,  # ✅ use engine, not connection
            if_exists="append",
            index=False,
            method="multi"
        )
        print(f"✅ Inserted {len(df)} rows into mlb_odds.", flush=True)
    except Exception as e:
        print(f"❌ Failed to insert data: {e}", flush=True)

