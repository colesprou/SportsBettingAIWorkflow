import os
import requests
import pandas as pd
from datetime import datetime, timezone, timedelta

# --- Helpers ---

def load_api_key(path):
    with open(path, 'r') as file:
        return file.readline().strip()

def american_to_decimal(odds):
    return (odds / 100) + 1 if odds > 0 else (100 / abs(odds)) + 1

def implied_probability(decimal_odds):
    return 1 / decimal_odds

def calculate_ev(true_prob, odds, stake=100):
    dec_odds = american_to_decimal(odds)
    payout = (dec_odds - 1) * stake
    return (true_prob * payout) - ((1 - true_prob) * stake)

# --- API Endpoints ---

OPTIC_ODDS_BASE = "https://api.opticodds.com/api/v3"

# --- Main Functions ---

def get_today_game_ids(api_key, league='MLB'):
    now = datetime.now(timezone.utc)
    future = now + timedelta(hours=48)
    params = {
        'key': api_key,
        'league': league,
        'start_date_after': now.isoformat(),
        'start_date_before': future.isoformat()
    }
    r = requests.get(f"{OPTIC_ODDS_BASE}/fixtures", params=params)
    if r.status_code != 200:
        return {}
    return {
        g['id']: f"{g['home_team_display']} vs {g['away_team_display']}"
        for g in r.json().get('data', [])
    }

def fetch_mlb_props(api_key, sportsbooks=['Pinnacle', 'Caesars']):
    game_ids = list(get_today_game_ids(api_key).keys())
    if not game_ids:
        return pd.DataFrame()

    all_data = []

    for chunk in [game_ids[i:i + 5] for i in range(0, len(game_ids), 5)]:
        for book in sportsbooks:
            params = {
                'key': api_key,
                'sportsbook': book,
                'fixture_id': chunk,
                'market_name': ['Player Hits', 'Player Home Runs', 'Player Strikeouts']
            }
            r = requests.get(f"{OPTIC_ODDS_BASE}/fixtures/odds", params=params)
            if r.status_code != 200:
                continue
            for g in r.json().get('data', []):
                for o in g.get('odds', []):
                    all_data.append({
                        'Game ID': g['id'],
                        'Game': f"{g['home_team_display']} vs {g['away_team_display']}",
                        'Player': o.get('selection'),
                        'Market': o.get('market'),
                        'Line': o.get('points'),
                        'Odds': o.get('price'),
                        'Sportsbook': book
                    })

    return pd.DataFrame(all_data)

def calculate_ev_for_props(df, sharp_book='Pinnacle', user_book='Caesars', stake=100):
    df = df[df['Sportsbook'].isin([sharp_book, user_book])].dropna(subset=['Odds'])

    pivot_df = df.pivot_table(
        index=['Player', 'Market', 'Line', 'Game'],
        columns='Sportsbook',
        values='Odds'
    ).reset_index()

    if sharp_book not in pivot_df.columns or user_book not in pivot_df.columns:
        return pd.DataFrame(columns=['Player', 'Market', 'Line', 'Game', 'EV'])

    pivot_df = pivot_df.dropna(subset=[sharp_book, user_book])

    pivot_df['Decimal True Odds'] = pivot_df[sharp_book].apply(american_to_decimal)
    pivot_df['True Prob'] = pivot_df['Decimal True Odds'].apply(implied_probability) * 0.98

    pivot_df['EV'] = pivot_df.apply(
        lambda x: calculate_ev(x['True Prob'], x[user_book], stake),
        axis=1
    )

    pivot_df['True Odds'] = pivot_df[sharp_book]
    pivot_df['User Odds'] = pivot_df[user_book]

    return pivot_df[['Player', 'Market', 'Line', 'Game', 'True Odds', 'User Odds', 'True Prob', 'EV']]\
             .sort_values(by='EV', ascending=False)

def get_mlb_ev_props(api_key, true_book='Pinnacle', user_book='Caesars'):
    df = fetch_mlb_props(api_key, sportsbooks=[true_book, user_book])
    return calculate_ev_for_props(df, sharp_book=true_book, user_book=user_book)
