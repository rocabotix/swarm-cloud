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
    
    # 1. RÉCUPÉRATION DES DONNÉES (API GAMMA)
    try:
        # On récupère 100 événements pour avoir plus de choix
        url = "https://gamma-api.polymarket.com/events?active=true&closed=false&limit=100"
        response = requests.get(url, timeout=15)
        if response.status_code != 200: return []
        data = response.json()

        for event in data:
            title = event.get('title', 'Titre inconnu')
            markets_list = event.get('markets', [])
            
            if markets_list:
                m = markets_list[0]
                try:
                    # Volume 24h (si dispo) ou volume total
                    v24 = float(m.get('volume24hr', 0))
                    v_total = float(m.get('volume', 0))
                    liq = float(m.get('liquidity', 0))
                    
                    # FILTRE : On ne veut que du "sérieux" (Liq > 2000$)
                    if liq < 2000:
                        continue
                    
                    # CALCUL DE L'ACCÉLÉRATION (Velocity)
                    # Si le volume 24h représente une grosse part de la liquidité = SUSPECT
                    velocity = v24 / liq if liq > 0 else 0
                    
                    raw_markets.append({
                        "title": title,
                        "v24": v24,
                        "v_total": v_total,
                        "liq": liq,
                        "velocity": velocity
                    })
                except:
                    continue
    except Exception as e:
        print(f"Erreur Fetch: {e}")
        return []

    # 2. TRI PAR VÉLOCITÉ (Les plus agressifs en premier)
    # On exclut les bruits habituels
    excluded = ["GTA", "BITCOIN", "BTC", "ETH", "SOLANA", "DOGE", "PRICE"]
    filtered = [m for m in raw_markets if not any(x in m['title'].upper() for x in excluded)]
    
    # On trie par le score de vélocité
    filtered = sorted(filtered, key=lambda x: x['velocity'], reverse=True)

    if not filtered:
        return []

    results = []

    # 3. ANALYSE IA SUR LES 3 MEILLEURS SIGNAUX D'URGENCE
    for market in filtered[:3]:
        title = market['title']
        v24, liq, vel = market['v24'], market['liq'], market['velocity']

        try:
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Tu es un expert en flux financiers clandestins et détection d'insiders. Ton but est d'analyser si une accélération de volume est liée à une fuite d'information."},
                    {"role": "user", "content": f"""Analyse d'urgence pour : '{title}'
                    - Volume 24h : ${v24:,.0f}
                    - Liquidité : ${liq:,.0f}
                    - Score d'accélération : {vel:.2f}
                    
                    Si le score d'accélération est > 1.0, cela signifie que le volume des dernières 24h dépasse la liquidité totale disponible. C'est un signe majeur d'entrée massive d'initiés."""}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.1, # Très froid pour plus de précision
            )
            
            analysis = response.choices[0].message.content
            # Confiance basée sur la vélocité
            conf = min(98, int(75 + (vel * 10)))

            results.append(SwarmResult(
                thematique=title,
                final_verdict="URGENCE INITIÉ" if vel > 1.5 else "ACCUMULATION FORTE",
                confidence=conf,
                summary=analysis,
                recommendation=f"Vélocité de {vel:.2f}. Entrée de capitaux agressive détectée.",
                key_arguments=[f"Le volume 24h représente {vel*100:.1f}% de la liquidité."],
                risk_assessment="TRÈS ÉLEVÉ" if vel > 2 else "MODÉRÉ",
                kelly_criterion=f"Mise {min(4.0, vel+1):.1f}%"
            ))
        except:
            continue

    return results

if __name__ == "__main__":
    res = asyncio.run(test_swarm())
    for r in res: print(f"\n🚀 {r.thematique} - Verdict: {r.final_verdict} (Score: {r.confidence})")