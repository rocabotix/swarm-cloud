# init.py - Vérification du projet avant lancement
import os
from dotenv import load_dotenv

load_dotenv()

def check_system():
    print("=" * 60)
    print("🔧 INITIALISATION DU POLYMARKET INSIDER SWARM")
    print("=" * 60)

    # 1. Vérification des clés API
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key and groq_key.startswith("gsk_"):
        print("✅ GROQ_API_KEY → OK")
    else:
        print("❌ GROQ_API_KEY manquante ou invalide dans .env")

    # 2. Vérification Telegram
    tg_token = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")
    tg_chat = os.getenv("TELEGRAM_CHAT_ID")
    if tg_token and tg_chat:
        print("✅ CONFIGURATION TELEGRAM → OK")
    else:
        print("⚠️  CONFIGURATION TELEGRAM incomplète (Token ou Chat ID)")

    # 3. Vérification des fichiers
    fichiers_requis = [
        "models.py", "config.py", "api_client.py", 
        "swarm_graph.py", "reporter.py", "app.py", "test_swarm.py"
    ]
    manquants = [f for f in fichiers_requis if not os.path.exists(f)]

    if manquants:
        print(f"⚠️  Fichiers manquants : {manquants}")
    else:
        print("✅ Tous les fichiers du projet sont présents")

    print("\n🎉 Initialisation terminée !")
    print("   Tape maintenant : python test_swarm.py pour un test manuel.")
    print("=" * 60)

if __name__ == "__main__":
    check_system()