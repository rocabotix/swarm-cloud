# reporter.py - Génère le rapport quotidien Telegram
from models import DebateResult
from datetime import datetime
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
import requests

def generate_daily_report(results: list):
    """Crée un beau rapport à partir des résultats du swarm"""
    if not results:
        return "Aucun signal intéressant aujourd'hui."

    rapport = f"🚨 Polymarket Insider Swarm Report 🚨\n"
    rapport += f"📅 {datetime.utcnow().strftime('%d %B %Y à %H:%M UTC')}\n\n"
    rapport += f"🔍 {len(results)} signaux analysés\n\n"

    for i, result in enumerate(results, 1):
        rapport += f"{i}. {result.thematique}\n"
        rapport += f"Verdict : {result.final_verdict} ({result.confidence}%)\n"
        rapport += f"Résumé : {result.summary}\n"
        rapport += f"Recommandation : {result.recommendation}\n"
        rapport += "────────────────────\n\n"

    return rapport

def send_telegram_report(rapport: str):
    """Envoie le rapport sur Telegram"""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram non configuré (optionnel)")
        print(rapport)
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": rapport,
        "parse_mode": "Markdown"
    }
    
    try:
        requests.post(url, data=data, timeout=10)
        print("✅ Rapport envoyé sur Telegram")
    except:
        print("❌ Impossible d'envoyer sur Telegram (vérifie le token)")

# Test rapide du fichier
if __name__ == "__main__":
    print("🧪 Test reporter.py")
    fake_result = DebateResult(
        final_verdict="INSIDER",
        confidence=82,
        summary="Wallet suspect sur marché Trump 2028",
        key_arguments=["Position énorme", "Wallet très ancien"],
        risk_assessment="High",
        recommendation="À surveiller de près",
        thematique="Politics"
    )
    report = generate_daily_report([fake_result])
    print(report)
    send_telegram_report(report)