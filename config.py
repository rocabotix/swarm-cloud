# config.py - Configuration du Polymarket Insider Swarm
from dotenv import load_dotenv
import os
from datetime import timedelta

load_dotenv()

# ====================== THÉMATIQUES À SUIVRE ======================
THEMATIQUES = ["Sports", "Politics", "Crypto"]

# Filtres de tags pour Polymarket
TAG_FILTERS = {
    "Sports": "sports",
    "Politics": "politics",
    "Crypto": "crypto"
}

# ====================== PARAMÈTRES DU SWARM ======================
MAX_HOLDERS_PER_MARKET = 8
MIN_POSITION_SIZE = 500          # en USDC
MIN_WALLET_AGE_DAYS = 30

# ====================== SCHEDULER ======================
REPORT_HOUR_UTC = 8   # Heure à laquelle le rapport quotidien est envoyé (UTC)

# ====================== CLÉS API (chargées depuis .env) ======================
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Vérification rapide au démarrage
if not ANTHROPIC_API_KEY:
    print("⚠️  ATTENTION : ANTHROPIC_API_KEY n'est pas définie dans le .env")
else:
    print("✅ Config chargée avec succès")
    print(f"   Thématiques actives : {THEMATIQUES}")
    print(f"   Rapport quotidien à {REPORT_HOUR_UTC}h UTC")