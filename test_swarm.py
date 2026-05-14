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
    
    # 1. RÉCUPÉRATION DES DONNÉES (On élargit pour trouver plus de politique)
    try:
        url = "https://gamma-api.polymarket.com/events?active=true&closed=false&limit=200"
        response = requests.get(url, timeout=15)
        if response.status_code != 200: return []
        data = response.json()

        # MOTS-CLÉS POLITIQUES OBLIGATOIRES
        political_keywords = [
            "PRESIDENT", "ELECTION", "DEMOCRAT", "REPUBLICAN", "SENATE", 
            "HOUSE", "GOVERNOR", "TRUMP", "BIDEN", "WHITE HOUSE", 
            "SUPREME COURT", "VOTE", "NOMINEE", "POLITICAL", "CONGRESS"
        ]

        for event in data:
            title = event.get('title', 'Titre inconnu').upper()
            
            # FILTRE : On ne garde QUE la politique
            if not any(word in title for word in political_keywords):
                continue
                
            markets_list = event.get('markets', [])
            if markets_list:
                m = markets_list[0]
                try:
                    v24 = float(m.get('volume24hr', 0))
                    liq = float(m.get('liquidity', 0))
                    
                    # Liquidité minimum pour éviter les marchés morts (1000$)
                    if liq < 1000: continue
                    
                    velocity = v24 / liq if liq > 0 else 0
                    raw_markets.append({
                        "title": title.title(),
                        "v24": v24,
                        "liq": liq,
                        "velocity": velocity
                    })
                except:
                    continue
    except Exception as e:
        print(f"Erreur Fetch: {e}")
        return []

    # 2. TRI PAR VÉLOCITÉ (Les mouvements les plus suspects)
    filtered = sorted(raw_markets, key=lambda x: x['velocity'], reverse=True)

    if not filtered:
        return []

    results = []

    # 3. ANALYSE IA SPÉCIALISÉE "INSIDER POLITIQUE"
    for market in filtered[:3]:
        title, v24, liq, vel = market['title'], market['v24'], market['liq'], market['velocity']

        try:
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Tu es un analyste expert en renseignements politiques et financement de campagne. Ton but est de détecter si une injection de capital sur Polymarket précède une annonce politique majeure (sondage secret, retrait de candidat, décision judiciaire)."},
                    {"role": "user", "content": f"ALERTE POLITIQUE : '{title}'. Vol 24h: ${v24:,.0f} | Liq: ${liq:,.0f} | Ratio: {vel:.2f}."}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.1,
            )
            
            analysis = response.choices[0].message.content
            conf = min(98, int(80 + (vel * 12)))

            results.append(SwarmResult(
                thematique=title,
                final_verdict="INSIDER POLITIQUE" if vel > 0.8 else "FLUX ÉLECTORAL",
                confidence=conf,
                summary=analysis,
                recommendation=f"Vélocité Politique: {vel:.2f}.",
                key_arguments=[f"Mouvement suspect détecté sur le segment {title}"],
                risk_assessment="ÉLEVÉ" if vel > 1.5 else "MODÉRÉ",
                kelly_criterion=f"Mise {min(5.0, vel+1.5):.1f}%"
            ))
        except:
            continue

    return results

if __name__ == "__main__":
    res = asyncio.run(test_swarm())
    for r in res: print(f"\n🏛️ {r.thematique} - Verdict: {r.final_verdict}")