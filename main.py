import asyncio
import logging
import os
import json
import urllib.request
from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from config import THEMATIQUES, REPORT_HOUR_UTC
from reporter import generate_daily_report
from test_swarm import test_swarm

load_dotenv()
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)
def build_html_report(results, session, now):
    rows = ""
    for i, r in enumerate(results):
        color = "#2ecc71" if r.confidence > 65 else "#f39c12" if r.confidence > 40 else "#e74c3c"
        rows += f"""
        <tr>
            <td style="padding:10px;border-bottom:1px solid #333;">{i+1}. {r.thematique}</td>
            <td style="padding:10px;border-bottom:1px solid #333;color:{color};font-weight:bold;">{r.final_verdict}</td>
            <td style="padding:10px;border-bottom:1px solid #333;">{r.confidence}%</td>
            <td style="padding:10px;border-bottom:1px solid #333;">{r.recommendation[:80]}</td>
        </tr>"""
    if not results:
        rows = '<tr><td colspan="4" style="padding:20px;text-align:center;color:#888;">Aucun signal</td></tr>'
    return f"""<html><body style="background:#1a1a2e;color:#eee;font-family:Arial,sans-serif;padding:20px;">
    <div style="max-width:700px;margin:auto;background:#16213e;border-radius:12px;padding:30px;">
    <h1 style="color:#00d4ff;text-align:center;">Polymarket Insider Swarm</h1>
    <p style="text-align:center;color:#888;">Session {session} - {now.strftime('%d/%m/%Y %H:%M')} UTC</p>
    <hr style="border-color:#333;margin:20px 0;">
    <h2 style="color:#00d4ff;">Signaux : {len(results)}</h2>
    <table style="width:100%;border-collapse:collapse;">
    <tr style="background:#0f3460;color:#00d4ff;">
        <th style="padding:10px;text-align:left;">Thematique</th>
        <th style="padding:10px;text-align:left;">Verdict</th>
        <th style="padding:10px;text-align:left;">Score</th>
        <th style="padding:10px;text-align:left;">Recommandation</th>
    </tr>{rows}
    </table>
    <hr style="border-color:#333;margin:20px 0;">
    <p style="color:#888;font-size:12px;text-align:center;">Rapport genere par Polymarket Insider Swarm. Pas un conseil financier.</p>
    </
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