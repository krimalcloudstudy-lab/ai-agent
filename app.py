from flask import Flask, request, jsonify, render_template
import requests
import os
from openai import OpenAI
from dotenv import load_dotenv

# =========================
# LOAD ENV
# =========================
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)

# =========================
# CONTEXT (Weather API)
# =========================
def get_weather(city):
    try:
        url = f"https://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}"
        res = requests.get(url, timeout=10).json()
        temp = res["current"]["temp_c"]
        condition = res["current"]["condition"]["text"]
        return f"{city} weather: {temp}°C, {condition}"
    except Exception as e:
        return f"Weather unavailable for {city}: {str(e)}"

# =========================
# MODEL (OpenAI)
# =========================
def ai_model(context, question):
    if not OPENAI_API_KEY:
        return "OpenAI key missing. Add valid key to .env"

    prompt = f"""
You are a smart assistant.
Context: {context}
Question: {question}
Answer: Safe or Not Safe + reason (short).
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI unavailable (quota exceeded?): {str(e)[:100]}. Context: {context}"

# =========================
# ROUTES
# =========================
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    city = request.form.get("city", "").strip()
    question = request.form.get("question", "").strip()
    
    if not city or not question:
        return jsonify({"answer": "Please enter both city and question."}), 400

    weather = get_weather(city)
    answer = ai_model(weather, question)
    
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True, port=8080)
