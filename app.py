import streamlit as st
import asyncio
from datetime import datetime, timezone
from test_swarm import test_swarm

st.set_page_config(
    page_title="Polymarket Insider Swarm",
    page_icon="🎯",
    layout="wide"
)

st.title("Polymarket Insider Swarm")
st.caption("Analyse automatique des marches Polymarket via IA")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Sessions par jour", "2")
with col2:
    st.metric("Heure matin", "8h00 UTC")
with col3:
    st.metric("Heure soir", "21h00 UTC")

st.divider()
if "results" not in st.session_state:
    st.session_state.results = []
if "last_run" not in st.session_state:
    st.session_state.last_run = None

col_btn, col_info = st.columns([1, 3])
with col_btn:
    run_button = st.button("Lancer une analyse", type="primary", use_container_width=True)
with col_info:
    if st.session_state.last_run:
        st.info(f"Derniere analyse : {st.session_state.last_run}")

if run_button:
    with st.spinner("Analyse en cours..."):
        results = asyncio.run(test_swarm())
        st.session_state.results = results
        st.session_state.last_run = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

st.divider()
if st.session_state.results:
    st.subheader(f"{len(st.session_state.results)} signaux analyses")
    for i, result in enumerate(st.session_state.results):
        with st.expander(f"{i+1}. {result.thematique} — {result.final_verdict} ({result.confidence}%)"):
            col_a, col_b = st.columns(2)
            with col_a:
                st.write("**Verdict**", result.final_verdict)
                st.write("**Confiance**", f"{result.confidence}%")
                st.write("**Thematique**", result.thematique)
            with col_b:
                st.write("**Resume**", result.summary)
                st.write("**Recommandation**", result.recommendation)
            if result.key_arguments:
                st.write("**Analyse**")
                for arg in result.key_arguments:
                    st.write(f"- {arg}")
else:
    st.info("Clique sur 'Lancer une analyse' pour demarrer le swarm.")