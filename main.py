# main.py - Lancement principal du Polymarket Insider Swarm
import asyncio
import logging
from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Imports locaux
from config import THEMATIQUES, REPORT_HOUR_UTC
from reporter import generate_daily_report, send_telegram_report
from test_swarm import test_swarm

# Configuration du logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)

async def daily_job():
    """Exécute l'analyse complète et envoie le rapport"""
    now_str = datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M')
    print(f"\n🚀 === DÉMARRAGE DU SWARM - {now_str} UTC ===")
    
    try:
        # 1. Analyse via l'essaim d'agents
        all_results = await test_swarm()
        
        # 2. Génération du rapport formaté
        report = generate_daily_report(all_results)
        
        # 3. Envoi sur Telegram
        send_telegram_report(report)
        
        print("✅ Rapport quotidien terminé et envoyé sur Telegram !")
    except Exception as e:
        logger.error(f"💥 Erreur critique pendant le job quotidien: {e}")

async def main():
    print("=" * 60)
    print("🌟 POLYMARKET INSIDER SWARM - ACTIVÉ")
    print(f"📍 Thématiques : {THEMATIQUES}")
    print(f"🕒 Planification : {REPORT_HOUR_UTC}:00 UTC tous les jours")
    print("=" * 60)

    # Lancement immédiat au démarrage pour vérifier que tout fonctionne
    await daily_job()

    # Configuration du scheduler pour les fois suivantes
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        daily_job, 
        'cron', 
        hour=REPORT_HOUR_UTC, 
        minute=0,
        timezone='UTC'
    )
    
    scheduler.start()
    print(f"✅ Scheduler démarré. En attente du prochain créneau...")

    # Maintient le script en vie
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        print("\n🛑 Arrêt du Swarm.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.fatal(f"Le programme s'est arrêté brutalement : {e}")