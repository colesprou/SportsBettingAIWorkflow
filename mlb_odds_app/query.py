import psycopg2

# Connect to Azure PostgreSQL
conn = psycopg2.connect(
    host="sports.postgres.database.azure.com",
    dbname="sb_data",
    user="colesprou",
    password="Test12345!",
    sslmode="require"
)

cur = conn.cursor()

# Query from mlb_odds table
cur.execute("SELECT * FROM mlb_odds ORDER BY fetched_at DESC LIMIT 5;")

rows = cur.fetchall()

# Print results
for row in rows:
    print(row)

cur.close()
conn.close()
