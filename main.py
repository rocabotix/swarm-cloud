import asyncio
import logging
from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import THEMATIQUES, REPORT_HOUR_UTC
from reporter import generate_daily_report
from test_swarm import test_swarm
from run_daily import send_email, build_html_report

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

async def daily_job():
    now = datetime.now(timezone.utc)
    session = "matin" if now.hour < 12 else "soir"
    print(f"=== DEMARRAGE DU SWARM - {now.strftime('%d/%m/%Y %H:%M')} UTC ===")
    try:
        all_results = await test_swarm()
        report = generate_daily_report(all_results)
        html_report = build_html_report(all_results, session, now)
        subject = f"Polymarket Swarm - Rapport {session} {now.strftime('%d/%m/%Y')}"
        send_email(subject, html_report, report)
        print("Rapport envoye par email avec succes")
    except Exception as e:
        logger.error(f"Erreur critique: {e}")
async def main():
    print("=" * 60)
    print("POLYMARKET INSIDER SWARM - ACTIVE")
    print(f"Thematiques : {THEMATIQUES}")
    print(f"Planification : {REPORT_HOUR_UTC}:00 UTC tous les jours")
    print("=" * 60)

    await daily_job()

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        daily_job,
        'cron',
        hour=REPORT_HOUR_UTC,
        minute=0,
        timezone='UTC'
    )
    scheduler.start()
    print("Scheduler demarre. En attente du prochain creneau...")

    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        print("Arret du Swarm.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.fatal(f"Le programme s'est arrete : {e}")