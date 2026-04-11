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

def send_email(subject, html_body, text_body):
    try:
        data = json.dumps({
            "personalizations": [{"to": [{"email": EMAIL_RECEIVER}]}],
            "from": {"email": EMAIL_SENDER},
            "subject": subject,
            "content": [
                {"type": "text/plain", "value": text_body},
                {"type": "text/html", "value": html_body}
            ]
        }).encode("utf-8")
        req = urllib.request.Request(
            "https://api.sendgrid.com/v3/mail/send",
            data=data,
            headers={
                "Authorization": f"Bearer {SENDGRID_API_KEY}",
                "Content-Type": "application/json"
            },
            method="POST"
        )
        urllib.request.urlopen(req)
        print("Email envoye avec succes via SendGrid")
    except Exception as e:
        print(f"Erreur email SendGrid: {e}")
def build_html_report(results, session, now):
    rows = ""
    for i, r in enumerate(results):
        color = "#2ecc71" if r.confidence > 65 else "#f39c12" if r.confidence > 40 else "#e74c3c"
        rows += "<tr>"
        rows += f"<td style='padding:10px'>{i+1}. {r.thematique}</td>"
        rows += f"<td style='padding:10px;color:{color}'>{r.final_verdict}</td>"
        rows += f"<td style='padding:10px'>{r.confidence}%</td>"
        rows += f"<td style='padding:10px'>{r.recommendation[:80]}</td>"
        rows += "</tr>"
    html = "<html><body style='background:#1a1a2e;color:#eee;padding:20px'>"
    html += "<h1 style='color:#00d4ff'>Polymarket Insider Swarm</h1>"
    html += f"<p>Session {session} - {now.strftime('%d/%m/%Y %H:%M')} UTC</p>"
    html += f"<p>Signaux : {len(results)}</p>"
    html += "<table style='width:100%;border-collapse:collapse'>"
    html += "<tr style='background:#0f3460;color:#00d4ff'>"
    html += "<th>Thematique</th><th>Verdict</th><th>Score</th><th>Recommandation</th>"
    html += "</tr>"
    html += rows
    html += "</table>"
    html += "<p style='color:#888;font-size:12px'>Pas un conseil financier.</p>"
    html += "</body></html>"
    return html

async def daily_job():
    now = datetime.now(timezone.utc)
    session = "matin" if now.hour < 12 else "soir"
    print(f"=== DEMARRAGE DU SWARM - {now.strftime('%d/%m/%Y %H:%M')} UTC ===")
    try:
        all_results = await test_swarm()
        report = generate_daily_report(all_results)
        html_report = build_html_report(all_results, session, now)
        subject = "Polymarket Swarm - " + session + " - " + now.strftime('%d/%m/%Y')
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