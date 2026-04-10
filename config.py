# config.py
from dotenv import load_dotenv
import os

load_dotenv()

THEMATIQUES = ["Sports", "Politics", "Crypto"]

TAG_FILTERS = {
    "Sports": "sports",
    "Politics": "politics",
    "Crypto": "crypto"
}

MAX_HOLDERS_PER_MARKET = 8
MIN_POSITION_SIZE = 100 
REPORT_HOUR_UTC = 8 

# Utilisation d'os.getenv avec une valeur par défaut pour éviter les crashs
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# On harmonise les noms pour correspondre à app.py et reporter.py
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not GROQ_API_KEY:
    print("❌ ERREUR : GROQ_API_KEY manquante.")