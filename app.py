import streamlit as st
import asyncio
import os
import requests
from datetime import datetime, timezone
from test_swarm import test_swarm

# --- CONFIGURATION TELEGRAM ---
def send_telegram_alert(results):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return

    message = "🚨 **NOUVELLE ANALYSE DU SWARM** 🚨\n\n"
    for i, res in enumerate(results):
        # On limite aux top opportunités pour ne pas saturer Telegram
        if res.confidence >= 70:
            message += f"🎯 {res.thematique}\n"
            message += f"Verdict: {res.final_verdict} ({res.confidence}%)\n"
            message += f"💡 Reco: {res.recommendation}\n"
            message += "-------------------\n"
    
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"})
    except Exception as e:
        print(f"Erreur Telegram: {e}")

# --- CONFIGURATION PAGE ---
st.set_page_config(
    page_title="Polymarket Insider Swarm",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 Essaim d'initiés de Polymarket")
st.caption("Analyse automatique des marchés Polymarket via IA (Analyste + Contradicteur)")

# --- DASHBOARD STATS ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Sessions par jour", "2")
with col2:
    st.metric("Heure matin", "8h00 UTC")
with col3:
    st.metric("Heure soir", "21h00 UTC")

st.divider()

# --- GESTION DE L'ÉTAT ---
if "results" not in st.session_state:
    st.session_state.results = []
if "last_run" not in st.session_state:
    st.session_state.last_run = None

col_btn, col_info = st.columns([1, 3])
with col_btn:
    run_button = st.button("Lancer une analyse", type="primary", use_container_width=True)
with col_info:
    if st.session_state.last_run:
        st.info(f"Dernière analyse : {st.session_state.last_run}")

# --- LOGIQUE DE LANCEMENT ---
if run_button:
    with st.spinner("L'Essaim est en train de réfléchir..."):
        # Lancement du swarm (qui inclut déjà ton test_swarm)
        results = asyncio.run(test_swarm())
        st.session_state.results = results
        st.session_state.last_run = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        
        # Envoi de l'alerte Telegram si des résultats existent
        if results:
            send_telegram_alert(results)
            st.success("Analyse terminée et alerte envoyée sur Telegram !")

st.divider()

# --- AFFICHAGE DES RÉSULTATS ---
if st.session_state.results:
    st.subheader(f"🔥 {len(st.session_state.results)} opportunités détectées")
    
    for i, result in enumerate(st.session_state.results):
        # Couleur dynamique selon la confiance
        label = f"{i+1}. {result.thematique} — {result.final_verdict} ({result.confidence}%)"
        
        with st.expander(label):
            col_a, col_b = st.columns(2)
            with col_a:
                st.write("**🛡️ Verdict Final**", result.final_verdict)
                st.write("**📊 Confiance**", f"{result.confidence}%")
                st.write("**🏷️ Thématique**", result.thematique)
            with col_b:
                st.write("**📝 Résumé**", result.summary)
                st.write("**💡 Recommandation**", result.recommendation)
            
            if hasattr(result, 'key_arguments') and result.key_arguments:
                st.divider()
                st.write("**🔍 Analyse détaillée des agents**")
                # On affiche ici les arguments (Analyste vs Contradicteur)
                for arg in result.key_arguments:
                    st.write(f"• {arg}")
else:
    st.info("Clique sur 'Lancer une analyse' pour démarrer le swarm.")