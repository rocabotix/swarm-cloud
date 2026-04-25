import streamlit as st
import asyncio
import os
import requests
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from test_swarm import test_swarm

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Polymarket Insider Swarm", 
    page_icon="🎯", 
    layout="wide"
)

# Style CSS pour un look "Terminal"
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3.5em; background-color: #ff4b4b; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- FONCTION D'ENVOI TELEGRAM ---
def send_telegram_alert(results):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("⚠️ [ERREUR] Variables Telegram manquantes.")
        return

    for res in results:
        priority = "🚨 HAUTE PRIORITÉ" if res.confidence > 85 else "📡 SIGNAL"
        message = (
            f"{priority}\n━━━━━━━━━━━━━━━━━━\n"
            f"🎯 **MARCHÉ :** {res.thematique.upper()}\n\n"
            f"💰 **ACTION :** {res.final_verdict}\n"
            f"📊 **CONFIANCE :** {res.confidence}%\n"
            f"⚖️ **STRATÉGIE :** {res.kelly_criterion}\n\n"
            f"🔎 **ANALYSE :**\n{res.summary[:400]}...\n\n"
            f"⚠️ **RISQUE :** {res.risk_assessment}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🔗 [Ouvrir Polymarket](https://polymarket.com/)"
        )

        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown", "disable_web_page_preview": True}, timeout=10)
        except Exception as e:
            print(f"❌ [ERREUR TELEGRAM] {e}")

# --- LOGIQUE DU PLANIFICATEUR (SCHEDULER) ---

def autonomous_scan_job():
    """Fonction exécutée automatiquement par le scheduler"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"⏰ [SYSTEM] Lancement du scan automatique à {now} (UTC)")
    
    # Création d'une nouvelle boucle d'événement pour le thread Background
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        results = loop.run_until_complete(test_swarm())
        if results and len(results) > 0:
            print(f"✅ [SYSTEM] {len(results)} signaux trouvés ! Envoi Telegram...")
            send_telegram_alert(results)
        else:
            print("🔍 [SYSTEM] Scan terminé : 0 anomalie détectée.")
    except Exception as e:
        print(f"❌ [SYSTEM ERROR] Échec du scan auto : {e}")
    finally:
        loop.close()

@st.cache_resource
def start_scheduler():
    """Initialise le scheduler une seule fois et le garde en mémoire"""
    sched = BackgroundScheduler(daemon=True)
    # 07:00 UTC = 09:00 Paris | 19:00 UTC = 21:00 Paris
    sched.add_job(autonomous_scan_job, 'cron', hour=7, minute=0)
    sched.add_job(autonomous_scan_job, 'cron', hour=19, minute=0)
    sched.start()
    print("🚀 [SCHEDULER] Le planificateur est démarré (09h/21h Paris).")
    return sched

# Démarrage automatique
scheduler_instance = start_scheduler()

# --- INTERFACE STREAMLIT ---
st.title("🎯 Swarm Insider Trading")

col1, col2, col3 = st.columns(3)
with col1: st.metric("Statut", "Opérationnel", "UptimeRobot OK")
with col2: st.metric("Prochain Scan", "09:00 / 21:00")
with col3: st.metric("Modèle", "Llama 3.3-70B")

st.divider()

if st.button("🚀 LANCER UNE ANALYSE MANUELLE MAINTENANT"):
    with st.spinner("Analyse en cours..."):
        try:
            results = asyncio.run(test_swarm())
            st.session_state.last_results = results
            if results:
                send_telegram_alert(results)
                st.success(f"Analyse terminée. {len(results)} signaux trouvés.")
            else:
                st.warning("Analyse terminée. 0 signaux trouvés.")
        except Exception as e:
            st.error(f"Erreur : {e}")

if 'last_results' in st.session_state and st.session_state.last_results:
    st.subheader("📊 Derniers Signaux")
    for res in st.session_state.last_results:
        with st.expander(f"MARCHÉ : {res.thematique.upper()}", expanded=True):
            st.write(f"**Verdict :** {res.final_verdict} ({res.confidence}%)")
            st.write(f"**Analyse :** {res.summary}")
            st.info(f"**Stratégie :** {res.kelly_criterion}")
else:
    st.info("En attente de signaux...")

st.divider()
st.caption(f"Heure serveur actuelle : {datetime.now().strftime('%H:%M:%S')} UTC")