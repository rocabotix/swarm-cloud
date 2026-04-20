import streamlit as st
import asyncio
import os
import requests
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from test_swarm import test_swarm

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Polymarket Insider Swarm", page_icon="🎯", layout="wide")

# Style CSS pour un look Terminal
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #ff4b4b; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- FONCTION DE NOTIFICATION TELEGRAM PRO ---
def send_telegram_alert(results):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return

    for res in results:
        priority = "🚨 HAUTE PRIORITÉ" if res.confidence > 85 else "📡 SIGNAL"
        
        message = f"{priority}\n"
        message += f"━━━━━━━━━━━━━━━━━━\n"
        message += f"🎯 **MARCHÉ :** {res.thematique.upper()}\n\n"
        message += f"💰 **ACTION :** {res.final_verdict}\n"
        message += f"📊 **CONFIANCE :** {res.confidence}%\n"
        message += f"⚖️ **STRATÉGIE :** {res.kelly_criterion}\n\n"
        message += f"🔎 **POURQUOI :**\n{res.summary[:250]}...\n\n"
        message += f"⚠️ **RISQUE :** {res.risk_assessment}\n"
        message += f"━━━━━━━━━━━━━━━━━━\n"
        message += f"🔗 [Ouvrir Polymarket](https://polymarket.com/)"

        try:
            requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                          json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown", "disable_web_page_preview": True},
                          timeout=10)
        except Exception as e:
            print(f"Erreur envoi : {e}")

# --- LOGIQUE DU PLANIFICATEUR ---
def autonomous_scan_job():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        results = loop.run_until_complete(test_swarm())
        if results:
            send_telegram_alert(results)
    finally:
        loop.close()

if 'scheduler_started' not in st.session_state:
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(autonomous_scan_job, 'cron', hour=7, minute=0) # 09:00 FR
    scheduler.add_job(autonomous_scan_job, 'cron', hour=19, minute=0) # 21:00 FR
    scheduler.start()
    st.session_state.scheduler_started = True

# --- INTERFACE ---
st.title("🎯 Swarm Insider Trading")
col1, col2, col3 = st.columns(3)
col1.metric("Status", "Opérationnel")
col2.metric("Scan", "2 / jour")
col3.metric("Filtre", "Anti-Bruit Actif")

if st.button("🚀 LANCER UNE ANALYSE MANUELLE MAINTENANT"):
    with st.spinner("Analyse des anomalies en cours..."):
        results = asyncio.run(test_swarm())
        st.session_state.last_results = results
        send_telegram_alert(results)
        st.success("Analyses envoyées sur Telegram !")

if 'last_results' in st.session_state:
    for res in st.session_state.last_results:
        with st.expander(f"{res.thematique} - {res.confidence}%", expanded=True):
            st.write(f"**Action :** {res.final_verdict}")
            st.write(f"**Analyse :** {res.summary}")
            st.info(f"**Stratégie :** {res.kelly_criterion}")