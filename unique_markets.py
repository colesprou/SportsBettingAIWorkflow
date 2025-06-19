import pandas as pd

df = pd.read_csv('MLB_Odds.csv')

print(df['Market Name'].unique())

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
