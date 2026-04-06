from groq import Groq
from models import WalletSignal, DebateResult
from config import GROQ_API_KEY
import json

client = Groq(api_key=GROQ_API_KEY)

def call_llm(prompt, system=None):
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.7,
        max_tokens=1000
    )
    return response.choices[0].message.content

def parse_json(content):
    try:
        content = content.strip()
        if "```" in content:
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        return json.loads(content.strip())
    except:
        return {}

def scout_node(market_title, market_slug, volume, implied_yes):
    system = "Tu es le Market Scout du Swarm Polymarket. Tu analyses les marches et identifies les opportunites. Reponds uniquement en JSON valide."
    prompt = f"""Analyse ce marche Polymarket :
Titre : {market_title}
Slug : {market_slug}
Volume : {volume} USDC
Probabilite implicite YES : {implied_yes}%

Reponds en JSON :
{{"priority": "HIGH|MEDIUM|LOW", "catalyst": "evenement cle identifie", "scout_signal": "raison en 1 phrase", "days_to_resolution_estimate": nombre}}"""
    content = call_llm(prompt, system)
    return parse_json(content)

def news_node(market_title):
    system = "Tu es le News & Sentiment Agent du Swarm Polymarket. Tu analyses le sentiment et les actualites. Reponds uniquement en JSON valide."
    prompt = f"""Analyse le sentiment et les actualites pour ce marche Polymarket :
Titre : {market_title}

Reponds en JSON :
{{"sentiment_score": nombre entre -100 et 100, "sentiment_label": "Positif|Negatif|Neutre", "key_facts": ["fait1", "fait2"], "imminent_catalyst": "evenement imminent ou null", "narrative_vs_market": "DECALAGE HAUSSIER|DECALAGE BAISSIER|ALIGNEMENT"}}"""
    content = call_llm(prompt, system)
    return parse_json(content)
def analyst_node(state: WalletSignal):
    prompt = f"""Tu es un ANALYSTE ON-CHAIN specialise Polymarket.
Wallet: {state.wallet}
Marche: {state.market_slug}
Position: {state.position_size} USDC
Age wallet: {state.age_days} jours

Reponds en JSON :
{{"score": nombre 0-100, "reasoning": "explication courte", "risk_factors": ["facteur1", "facteur2"]}}"""
    try:
        data = parse_json(call_llm(prompt))
        state.breakdown["analyst"] = data
        state.initial_score = data.get("score", 50)
    except Exception as e:
        state.breakdown["analyst"] = {"score": 50, "reasoning": "Erreur"}
    return state

def whale_node(state: WalletSignal):
    prompt = f"""Tu es un EXPERT WHALE HUNTER specialise Polymarket.
Wallet: {state.wallet}
Marche: {state.market_slug}
Position: {state.position_size} USDC
Age wallet: {state.age_days} jours

Reponds en JSON :
{{"whale_score": nombre 0-100, "is_insider": true ou false, "explanation": "explication courte"}}"""
    try:
        data = parse_json(call_llm(prompt))
        state.breakdown["whale"] = data
    except:
        state.breakdown["whale"] = {"whale_score": 50, "is_insider": False, "explanation": "Erreur"}
    return state

def validator_node(market_title, scout_data, news_data, analyst_score, whale_score):
    system = "Tu es le Strategist Validator du Swarm Polymarket. Tu synthetises les analyses et donnes une recommandation finale. Reponds uniquement en JSON valide."
    prompt = f"""Synthetise ces analyses pour le marche : {market_title}

Scout : {json.dumps(scout_data)}
News & Sentiment : {json.dumps(news_data)}
Score Analyste : {analyst_score}
Score Whale : {whale_score}

Calcule un score global 0-100 et une recommandation.
Reponds en JSON :
{{"global_score": nombre 0-100, "recommendation": "STRONG EDGE|MODERATE EDGE|MONITOR|AVOID", "thesis": "these en 2 phrases", "risk": "risque principal en 1 phrase"}}"""
    content = call_llm(prompt, system)
    return parse_json(content)

def final_decision(state: WalletSignal, validator_data=None):
    analyst_score = state.breakdown.get("analyst", {}).get("score", 50)
    whale_score = state.breakdown.get("whale", {}).get("whale_score", 50)
    global_score = validator_data.get("global_score", (analyst_score + whale_score) / 2) if validator_data else (analyst_score + whale_score) / 2
    recommendation = validator_data.get("recommendation", "NORMAL") if validator_data else "NORMAL"
    thesis = validator_data.get("thesis", "") if validator_data else ""
    result = DebateResult(
        final_verdict="INSIDER" if global_score > 65 else recommendation,
        confidence=int(global_score),
        summary=f"Wallet {state.wallet[:8]}... sur {state.market_slug}",
        key_arguments=[thesis] if thesis else [state.breakdown.get("analyst", {}).get("reasoning", "")],
        risk_assessment="Medium",
        recommendation=validator_data.get("risk", "Rien a signaler") if validator_data else "Rien a signaler",
        thematique=state.thematique
    )
    return {"final_result": result}

def run_debate(signal: WalletSignal):
    try:
        market_title = signal.market_slug.replace("-", " ").title()
        scout_data = scout_node(market_title, signal.market_slug, signal.position_size, 50)
        news_data = news_node(market_title)
        state = analyst_node(signal)
        state = whale_node(state)
        analyst_score = state.breakdown.get("analyst", {}).get("score", 50)
        whale_score = state.breakdown.get("whale", {}).get("whale_score", 50)
        validator_data = validator_node(market_title, scout_data, news_data, analyst_score, whale_score)
        result = final_decision(state, validator_data)
        return result
    except Exception as e:
        print(f"Erreur run_debate: {e}")
        return None