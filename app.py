import streamlit as st
import asyncio
import os
import requests
from datetime import datetime, timezone
from test_swarm import test_swarm

# --- CONFIGURATION TELEGRAM ---
def send_telegram_alert(results):
    # Support des deux noms de variables pour éviter les erreurs Render
    token = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        st.warning("⚠️ Configuration Telegram manquante sur Render (TOKEN ou CHAT_ID)")
        return

    message = "🚨 **NOUVELLE ANALYSE DU SWARM** 🚨\n\n"
    for i, res in enumerate(results):
        # On baisse le seuil à 0 pour être sûr de recevoir les tests
        if res.confidence >= 0:
            message += f"🎯 *{res.thematique.upper()}*\n"
            message += f"Verdict: {res.final_verdict} ({res.confidence}%)\n"
            message += f"💡 Reco: {res.recommendation}\n"
            message += "-------------------\n"
    
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        r = requests.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"})
        if r.status_code != 200:
            print(f"Erreur API Telegram: {r.text}")
    except Exception as e:
        print(f"Erreur connexion Telegram: {e}")

# --- UI STREAMLIT ---
st.set_page_config(page_title="Polymarket Insider Swarm", page_icon="🎯", layout="wide")

st.title("🎯 Polymarket Insider Swarm")
st.caption("Analyse des flux On-chain avec Analyste & Contradicteur")

if "results" not in st.session_state:
    st.session_state.results = []
if "last_run" not in st.session_state:
    st.session_state.last_run = None

if st.button("Lancer une analyse", type="primary"):
    with st.spinner("L'essaim analyse les marchés..."):
        # On utilise try/except pour voir l'erreur exacte dans Streamlit si ça crash
        try:
            results = asyncio.run(test_swarm())
            st.session_state.results = results
            st.session_state.last_run = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            
            if results:
                send_telegram_alert(results)
                st.success(f"Analyse terminée : {len(results)} signaux trouvés.")
            else:
                st.info("Aucun mouvement suspect détecté sur Polymarket.")
        except Exception as e:
            st.error(f"Erreur lors de l'analyse : {e}")

st.divider()

if st.session_state.results:
    for i, result in enumerate(st.session_state.results):
        with st.expander(f"{i+1}. {result.thematique} — {result.final_verdict} ({result.confidence}%)"):
            col1, col2 = st.columns(2)
            with col1:
                st.write("**🛡️ Verdict:**", result.final_verdict)
                st.write("**📊 Confiance:**", f"{result.confidence}%")
            with col2:
                st.write("**📝 Résumé:**", result.summary)
                st.write("**💡 Reco:**", result.recommendation)
            
            if hasattr(result, 'key_arguments') and result.key_arguments:
                st.divider()
                st.write("**🔍 DÉBAT ANALYSTE vs CONTRADICTEUR**")
                for arg in result.key_arguments:
                    st.info(arg) if "✅" in arg else st.warning(arg)