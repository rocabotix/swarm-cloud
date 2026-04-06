# reporter.py - Génère le rapport détaillé pour Telegram et Email
from models import DebateResult
from datetime import datetime, timezone
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
import requests

def generate_daily_report(results: list):
    """
    Crée un rapport riche avec le détail du débat entre les agents.
    """
    if not results:
        return "📭 *Polymarket Swarm* : Aucun signal pertinent détecté lors de cette session."

    # En-tête du rapport
    now_str = datetime.now(timezone.utc).strftime('%d/%m/%Y à %H:%M UTC')
    rapport = f"🎯 *POLYMARKET INSIDER SWARM REPORT*\n"
    rapport += f"📅 {now_str}\n"
    rapport += f"🔍 {len(results)} opportunités analysées par le Swarm\n"
    rapport += f"────────────────────────\n\n"

    for i, result in enumerate(results, 1):
        # Détermination de l'émoji selon la confiance
        emoji_score = "🔥" if result.confidence >= 75 else "⚖️"
        
        # Structure du Signal
        rapport += f"{i}. {emoji_score} *{result.thematique.upper()}* : {result.final_verdict}\n"
        rapport += f"📊 *Confiance :* {result.confidence}%\n"
        rapport += f"📝 *Résumé :* {result.summary}\n"
        
        # --- SECTION DÉBAT DES AGENTS ---
        if hasattr(result, 'key_arguments') and result.key_arguments:
            rapport += f"\n📖 *DÉBAT INTERNE :*\n"
            for arg in result.key_arguments:
                # Formatage spécifique selon l'agent pour Telegram
                if "CONTRADICTEUR" in arg.upper() or "⚠️" in arg:
                    rapport += f"{arg}\n"
                else:
                    rapport += f"{arg}\n"
        
        # --- RECOMMANDATION & RISQUE ---
        rapport += f"\n💡 *Recommandation :* {result.recommendation}\n"
        rapport += f"🛡️ *Évaluation du Risque :* {result.risk_assessment}\n"
        rapport += "────────────────────────\n\n"

    rapport += "⚠️ _Ce rapport est généré par IA et ne constitue pas un conseil financier._"
    return rapport

def send_telegram_report(rapport: str):
    """
    Envoie le rapport final sur Telegram avec gestion de la limite de caractères.
    """
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Config Telegram manquante. Rapport affiché dans la console.")
        print(rapport)
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    # Telegram limite les messages à 4096 caractères
    if len(rapport) > 4000:
        parts = [rapport[i:i+4000] for i in range(0, len(rapport), 4000)]
    else:
        parts = [rapport]

    for part in parts:
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": part,
            "parse_mode": "Markdown" # Active le gras et l'italique
        }
        
        try:
            response = requests.post(url, data=data, timeout=15)
            response.raise_for_status()
            print("✅ Rapport Swarm envoyé avec succès sur Telegram.")
        except Exception as e:
            print(f"❌ Erreur lors de l'envoi Telegram : {e}")

# --- TEST UNITAIRE ---
if __name__ == "__main__":
    print("🧪 Test de formatage du rapport...")
    test_res = [
        DebateResult(
            final_verdict="INSIDER CONFIRMÉ",
            confidence=88,
            summary="Whale identifiée sur le marché NBA",
            key_arguments=[
                "✅ ANALYSTE : Le wallet a un historique de 100% de réussite sur ce tag.",
                "⚠️ CONTRADICTEUR : Le volume global du marché est faible, attention au dump."
            ],
            risk_assessment="MODÉRÉ",
            recommendation="Suivre la position avec un stop-loss mental.",
            thematique="Sports"
        )
    ]
    print(generate_daily_report(test_res))