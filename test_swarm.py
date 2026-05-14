import asyncio
import os
import requests
from dataclasses import dataclass
from typing import List
from groq import Groq

# --- CONFIGURATION ---
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
    raw_markets = []
    
    # 1. RÉCUPÉRATION DES DONNÉES
    try:
        url = "https://gamma-api.polymarket.com/events?active=true&closed=false&limit=50"
        response = requests.get(url, timeout=15)
        if response.status_code != 200: return []
        data = response.json()

        for event in data:
            title = event.get('title', 'Titre inconnu')
            markets_list = event.get('markets', [])
            
            if markets_list:
                m = markets_list[0]
                try:
                    v = float(m.get('volume', 0))
                    l = float(m.get('liquidity', 0))
                    
                    # --- FILTRE DE LIQUIDITÉ MINIMUM (1000$) ---
                    # On ignore les marchés "fantômes" ou trop petits
                    if l < 1000:
                        continue
                        
                    ratio = v / l
                    raw_markets.append({"title": title, "volume": v, "liquidity": l, "ratio": ratio})
                except:
                    continue
    except Exception as e:
        print(f"Erreur Fetch: {e}")
        return []

    # 2. FILTRAGE ANTI-BRUIT & TRI
    excluded = ["GTA", "BITCOIN", "BTC", "ETH", "ETHEREUM", "SOLANA", "DOGE"]
    
    # On ne garde que les marchés propres et on trie par ratio (anomalie)
    filtered = [m for m in raw_markets if not any(x in m['title'].upper() for x in excluded)]
    filtered = sorted(filtered, key=lambda x: x['ratio'], reverse=True)

    if not filtered:
        return []

    results = []

    # 3. ANALYSE IA (Top 3 des plus grosses anomalies réelles)
    for market in filtered[:3]:
        title, v, l, r = market['title'], market['volume'], market['liquidity'], market['ratio']

        try:
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Tu es un analyste en Insider Trading. Analyse l'asymétrie volume/liquidité."},
                    {"role": "user", "content": f"Marché: '{title}'. Vol: ${v:,.0f} | Liq: ${l:,.0f} | Ratio: {r:.2f}."}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.2,
            )
            
            analysis = response.choices[0].message.content
            conf = min(95, int(70 + (r * 2)))

            results.append(SwarmResult(
                thematique=title,
                final_verdict="INSIDER SUSPECTÉ" if r > 1.8 else "FLUX ACTIF",
                confidence=conf,
                summary=analysis,
                recommendation=f"Ratio de {r:.2f}. Surveillance requise.",
                key_arguments=[f"Liquidité saine (${l:,.0f}) mais volume disproportionné"],
                risk_assessment="ÉLEVÉ" if r > 3 else "MODÉRÉ",
                kelly_criterion=f"Mise {min(3.0, r):.1f}%"
            ))
        except:
            continue

    return results

if __name__ == "__main__":
    res = asyncio.run(test_swarm())
    for r in res: print(f"\n✅ {r.thematique} (Ratio: {r.key_arguments[0]})")