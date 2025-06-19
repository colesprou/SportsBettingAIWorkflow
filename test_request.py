import requests

# Define the endpoint
url = "http://127.0.0.1:5000/ask"

# Define the input query
payload = {
    "query": "Show me any +EV MLB player prop bets for today"
}

# Send the POST request
response = requests.post(url, json=payload)

# Print the results
if response.status_code == 200:
    print("Top EV Bets:")
    for i, bet in enumerate(response.json(), 1):
        print(f"{i}. {bet}")
else:
    print("Error:", response.status_code, response.json())
