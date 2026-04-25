import os
from dotenv import load_dotenv

load_dotenv()

# Paramètres des marchés
THEMATIQUES = ["Sports", "Politics", "Crypto"]
TAG_FILTERS = {
    "Sports": "sports",
    "Politics": "politics",
    "Crypto": "crypto"
}

REPORT_HOUR_UTC = 8

# Identifiants API
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Configuration Email (SMTP Gmail)
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

# Headers pour api_client
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}