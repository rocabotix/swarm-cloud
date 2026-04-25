# reporter.py - Mise à jour pour la stabilité Telegram
from models import DebateResult
from datetime import datetime, timezone
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
import requests

def generate_daily_report(results: list):
    if not results:
        return "📭 <b>Polymarket Swarm</b> : Aucun signal pertinent détecté."

    now_str = datetime.now(timezone.utc).strftime('%d/%m/%Y à %H:%M UTC')
    rapport = f"🎯 <b>POLYMARKET INSIDER SWARM REPORT</b>\n"
    rapport += f"📅 {now_str}\n"
    rapport += f"🔍 {len(results)} opportunités analysées\n"
    rapport += f"────────────────────────\n\n"

    for i, result in enumerate(results, 1):
        emoji_score = "🔥" if result.confidence >= 75 else "⚖️"
        
        rapport += f"{i}. {emoji_score} <b>{result.thematique.upper()}</b> : {result.final_verdict}\n"
        rapport += f"📊 <b>Confiance :</b> {result.confidence}%\n"
        rapport += f"📝 <b>Résumé :</b> {result.summary[:300]}...\n"
        rapport += f"💡 <b>Recommandation :</b> {result.recommendation}\n"
        rapport += f"🛡️ <b>Risque :</b> {result.risk_assessment}\n"
        rapport += "────────────────────────\n\n"

    rapport += "<i>IA générative : Pas un conseil financier.</i>"
    return rapport

def send_telegram_report(rapport: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Config Telegram manquante.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    # Découpage si trop long
    parts = [rapport[i:i+4000] for i in range(0, len(rapport), 4000)] if len(rapport) > 4000 else [rapport]

    for part in parts:
        try:
            # On passe en parse_mode="HTML" pour plus de sécurité
            response = requests.post(url, data={
                "chat_id": TELEGRAM_CHAT_ID, 
                "text": part, 
                "parse_mode": "HTML"
            }, timeout=15)
            response.raise_for_status()
            print("✅ Rapport Swarm envoyé sur Telegram.")
        except Exception as e:
            print(f"❌ Erreur Telegram : {e}")