import asyncio
import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import THEMATIQUES, REPORT_HOUR_UTC, EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER
from reporter import generate_daily_report, send_telegram_report
from test_swarm import test_swarm

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

def send_email(subject, html_body, text_body):
    if not all([EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER]):
        logger.warning("Configuration Email incomplète dans le .env")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        logger.info("✅ Email envoyé avec succès via Gmail.")
    except Exception as e:
        logger.error(f"❌ Erreur SMTP : {e}")

def build_html_report(results, session, now):
    rows = ""
    for i, r in enumerate(results):
        color = "#2ecc71" if r.confidence > 70 else "#f39c12" if r.confidence > 50 else "#e74c3c"
        rows += f"<tr><td style='padding:10px; border-bottom:1px solid #444;'>{r.thematique}</td>"
        rows += f"<td style='padding:10px; border-bottom:1px solid #444; color:{color};'>{r.final_verdict} ({r.confidence}%)</td>"
        rows += f"<td style='padding:10px; border-bottom:1px solid #444;'>{r.recommendation}</td></tr>"
    
    return f"<html><body style='background:#1a1a1a; color:#eee; padding:20px;'><h2>Rapport Swarm {session} - {now.strftime('%d/%m/%Y')}</h2><table style='width:100%; border-collapse: collapse;'>{rows}</table></body></html>"

async def daily_job():
    now = datetime.now(timezone.utc)
    session = "Matin" if now.hour < 12 else "Soir"
    logger.info(f"--- DÉBUT DE LA SESSION {session.upper()} ---")
    try:
        all_results = await test_swarm()
        if all_results:
            report_text = generate_daily_report(all_results)
            send_telegram_report(report_text) # Envoi Telegram
            
            html_report = build_html_report(all_results, session, now)
            send_email(f"Polymarket Swarm Report - {session}", html_report, report_text)
        else:
            logger.info("Aucun résultat généré lors de cette session.")
    except Exception as e:
        logger.error(f"Erreur durant le job quotidien : {e}")

async def main():
    logger.info("POLYMARKET SWARM BOT INITIALISÉ")
    await daily_job() # Test immédiat au lancement
    
    scheduler = AsyncIOScheduler()
    scheduler.add_job(daily_job, 'cron', hour=REPORT_HOUR_UTC, minute=0, timezone='UTC')
    scheduler.start()
    
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())