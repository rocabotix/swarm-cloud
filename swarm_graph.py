import os
from groq import Groq
from ddgs import DDGS
from models import WalletSignal, DebateResult

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_web_context(topic):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(f"{topic} news polymarket", max_results=3))
            return "\n".join([f"- {r['title']}: {r['body'][:200]}" for r in results]) if results else "Pas de news."
    except:
        return "Contexte indisponible."

def call_llm(prompt, system_prompt):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7 # Un peu de créativité pour l'agressivité
    )
    return response.choices[0].message.content

def run_debate(signal: WalletSignal):
    slug = signal.market_slug 
    print(f"🤖 Analyse Swarm (Mode Agressif) sur : {slug}...")
    context = get_web_context(slug)
    
    # --- PROMPT ANALYSTE AGRESSIF ---
    analyst_prompt = f"""
    ANALYSE DE MARCHÉ : {slug}
    CONTEXTE WEB : {context}
    TAILLE DE POSITION : {signal.position_size}
    
    Ta mission : Agis comme un analyste 'Degen' qui cherche à détecter l'insider trading ou les erreurs de prix massives.
    Ne sois pas modéré. Si le marché est illogique ou manipulé, dis-le brutalement. 
    Cherche la faille. Est-ce une opportunité en or ou un piège à cons ? Tranche !
    """
    
    opinion = call_llm(analyst_prompt, "Tu es un analyste financier pro-actif, cynique et ultra-rapide.")
    
    # --- PROMPT CONTRADICTEUR IMPITOYABLE ---
    critic_prompt = f"""
    L'analyste vient de dire : "{opinion}"
    
    Ta mission : Démolis cette analyse. Agis comme un auditeur de risques qui déteste prendre des positions.
    Trouve les biais cognitifs, les risques de liquidité, ou les fausses news que l'analyste a ignoré. 
    Pourquoi va-t-on perdre de l'argent en suivant son avis ? Sois impitoyable.
    """
    
    critique = call_llm(critic_prompt, "Tu es l'avocat du diable, expert en gestion de risques et en détection de scams.")
    
    # Synthèse finale
    return {
        "final_result": DebateResult(
            final_verdict="ACTION RECOMMANDÉE" if "fort" in opinion.lower() else "PRUDENCE MAXIMALE",
            confidence=75,
            summary=f"DÉBAT CHOC : {opinion[:250]}... VS {critique[:250]}...",
            key_arguments=[f"L'Analyste dit: {opinion[:400]}", f"Le Critique répond: {critique[:400]}"],
            risk_assessment="Élevé (Analyse agressive)",
            recommendation="Vérifier les flux de wallets avant d'entrer.",
            thematique=signal.thematique
        )
    }