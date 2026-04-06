# main.py - Lancement principal du Polymarket Insider Swarm
import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging
from config import THEMATIQUES, REPORT_HOUR_UTC
from reporter import generate_daily_report, send_telegram_report
from test_swarm import test_swarm

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

async def daily_job():
    """Job qui tourne tous les jours à l'heure choisie"""
    print(f"\n🚀 === RAPPORT QUOTIDIEN - {datetime.utcnow().strftime('%d/%m/%Y %H:%M')} UTC ===\n")
    try:
        all_results = await test_swarm()
        report = generate_daily_report(all_results)
        send_telegram_report(report)
        print("✅ Rapport quotidien terminé et envoyé !")
    except Exception as e:
        logger.error(f"Erreur pendant le job quotidien: {e}")

async def main():
    print("=" * 60)
    print("🌟 POLYMARKET INSIDER SWARM - Démarrage")
    print(f"📍 Thématiques suivies : {THEMATIQUES}")
    print(f"🕒 Rapport automatique tous les jours à {REPORT_HOUR_UTC}h UTC")
    print("=" * 60)

    # Premier rapport immédiat
    await daily_job()

    # Scheduler pour les jours suivants
    scheduler = AsyncIOScheduler()
    scheduler.add_job(daily_job, 'cron', hour=REPORT_HOUR_UTC, minute=0)
    scheduler.start()

    print(f"\n✅ Swarm lancé avec succès !")
    print(f" • Premier rapport fait maintenant")
    print(f" • Prochains rapports tous les jours à {REPORT_HOUR_UTC}h UTC")
    print(" Appuie sur Ctrl + C pour arrêter le programme")

    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        print("\n\n👋 Swarm arrêté par l'utilisateur.")

if __name__ == "__main__":
    asyncio.run(main())