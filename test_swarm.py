import asyncio
import os
from dataclasses import dataclass
from typing import List
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@dataclass
class SwarmResult:
    thematique: str
    final_verdict: str
    confidence: int
    summary: str
    recommendation: str
    key_arguments: List[str]
    risk_assessment: str
    kelly_criterion: str

async def test_swarm():
    # 1. DONNÉES SIMULÉES (À remplacer par API Polymarket plus tard)
    raw_markets = [
        {"title": "GTA VI Release", "volume": 1000000, "liquidity": 500000},
        {"title": "US TikTok Ban by August", "volume": 450000, "liquidity": 40000}, # Anomalie !
        {"title": "Bitcoin Price $100k", "volume": 5000000, "liquidity": 2000000},
        {"title": "New Tech CEO Announcement", "volume": 150000, "liquidity": 15000} # Anomalie !
    ]

    # 2. FILTRAGE ANTI-BRUIT
    excluded = ["GTA", "BITCOIN", "BTC", "ETH", "SOLANA", "DOGE"]
    filtered = [m for m in raw_markets if not any(x in m['title'].upper() for x in excluded)]

    results = []
    for market in filtered[:3]:
        vol_liq_ratio = market['volume'] / market['liquidity']
        
        # Débat IA
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Tu es un analyste financier expert en détection d'insiders. Sois froid et critique."},
                {"role": "user", "content": f"Analyse le marché : {market['title']}. Ratio Vol/Liq : {vol_liq_ratio}. Est-ce une accumulation suspecte ?"}
            ],
            model="llama3-70b-8192",
            temperature=0.2
        )
        
        analysis = response.choices[0].message.content
        conf = 90 if vol_liq_ratio > 3 else 70

        results.append(SwarmResult(
            thematique=market['title'],
            final_verdict="ACHAT / ACCUMULATION" if vol_liq_ratio > 3 else "OBSERVATION",
            confidence=conf,
            summary=analysis,
            recommendation=f"Ratio Vol/Liq exceptionnel de {vol_liq_ratio:.2f}",
            key_arguments=["Anomalie quantitative", "Mouvement Smart Money"],
            risk_assessment="ÉLEVÉ (Marché de niche)",
            kelly_criterion="Miser 2% du capital" if conf > 85 else "Ne pas miser"
        ))
    return results