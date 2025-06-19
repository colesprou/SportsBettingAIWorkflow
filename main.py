from flask import Flask, request, jsonify
import os
import pandas as pd
import openai
from mlb_tools import get_mlb_ev_props

app = Flask(__name__)

# Load API key for OpenAI and betting API
API_KEY = os.getenv("ODDSJAM_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

@app.route("/ask", methods=["POST"])
def ask_for_ev_plays():
    user_input = request.json.get("query", "")

    # Use OpenAI LLM to confirm user wants MLB props
    prompt = f"""
    Does this query ask for MLB betting props or odds? Respond with 'yes' or 'no'.
    Query: {user_input}
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that returns 'yes' or 'no'."},
                {"role": "user", "content": prompt}
            ]
        )
        answer = response.choices[0].message["content"].strip().lower()
        if answer != "yes":
            return jsonify({"message": "This app only supports MLB right now. Try asking about MLB props."})
    except Exception as e:
        return jsonify({"error": "LLM processing failed", "details": str(e)}), 500

    # Retrieve +EV MLB props
    ev_df = get_mlb_ev_props(api_key=API_KEY, true_book='Pinnacle', user_book='Caesars')
    ev_df_sorted = ev_df.sort_values(by="EV", ascending=False).head(5)
    result = ev_df_sorted.to_dict(orient="records")
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
