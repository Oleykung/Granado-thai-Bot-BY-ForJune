
from flask import Flask
import threading
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ GEM Boss Bot is running 24h - Granado Espada M"

@app.route("/health")
def health():
    return {"status": "ok", "bot": "GEM Boss Timer", "uptime": "24h"}

def run():
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = threading.Thread(target=run, daemon=True)
    t.start()
