import streamlit as st
import asyncio
import os
import requests
from datetime import datetime, timezone
from apscheduler.schedulers.background import BackgroundScheduler
from test_swarm import test_swarm

# --- CONFIGURATION TELEGRAM ---
def send_telegram_alert(results):
    token = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id: return
    message = "🚨 *RAPPORT AUTOMATIQUE DU SWARM* 🚨\n\n"
    for res in results:
        message += f"📌 *{res.thematique.upper()}*\nVerdict: {res.final_verdict} ({res.confidence}%)\n---\n"
    try:
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                      json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"})
    except: pass

# --- FONCTION POUR LE SCHEDULER ---
def autonomous_scan():
    """Cette fonction sera appelée par le scheduler en arrière-plan"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    results = loop.run_until_complete(test_swarm())
    if results:
        send_telegram_alert(results)

# --- LANCEMENT DU SCHEDULER (Une seule fois) ---
if 'scheduler_started' not in st.session_state:
    scheduler = BackgroundScheduler()
    # On planifie à 8h et 21h (Heure de Paris environ / 7h et 19h UTC)
    scheduler.add_job(autonomous_scan, 'cron', hour=7, minute=0)
    scheduler.add_job(autonomous_scan, 'cron', hour=19, minute=0)
    scheduler.start()
    st.session_state.scheduler_started = True

# --- INTERFACE STREAMLIT ---
st.set_page_config(page_title="Polymarket Insider Swarm", page_icon="🎯")
st.title("🎯 Polymarket Insider Swarm")

if st.button("🚀 Lancer l'Analyse Manuelle"):
    with st.spinner("Analyse en cours..."):
        results = asyncio.run(test_swarm())
        if results:
            st.success("Analyse terminée !")
            for res in results:
                st.write(f"**{res.thematique}** : {res.final_verdict} ({res.confidence}%)")
            send_telegram_alert(results)