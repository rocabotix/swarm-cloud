import asyncio
import logging
from config import THEMATIQUES, TAG_FILTERS
from api_client import get_trending_markets, get_top_holders
from swarm_graph import run_debate
from models import WalletSignal, DebateResult # Import correct depuis models

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

async def test_swarm():
    print("🚀 Démarrage du Swarm...")
    all_results = []
    
    for thema in THEMATIQUES:
        try:
            tag_filter = TAG_FILTERS.get(thema, thema.lower())
            trending = get_trending_markets(limit=10, tag_filter=tag_filter)
            
            if not trending:
                continue

            market = trending[0]
            market_slug = market.get("slug")
            
            holders = get_top_holders(market_slug, limit=3, min_balance=100)
            
            if holders:
                for holder in holders[:2]:
                    # Sécurisation des données API
                    wallet = holder.get("proxyWallet") or holder.get("userId", "unknown")
                    try:
                        size = float(holder.get("size", 0))
                    except:
                        size = 0.0

                    signal = WalletSignal(
                        wallet=wallet,
                        market_slug=market_slug,
                        thematique=thema,
                        position_size=size,
                        age_days=30,
                        risk_level="Medium"
                    )
                    
                    debate = run_debate(signal)
                    if debate and "final_result" in debate:
                        all_results.append(debate["final_result"])
        
        except Exception as e:
            logger.error(f"Erreur sur {thema}: {e}")

    if not all_results:
        all_results.append(DebateResult(
            final_verdict="TEST SYSTÈME",
            confidence=99,
            summary="Scanner actif, aucun mouvement majeur détecté.",
            key_arguments=["✅ API OK", "⚠️ Calme plat"],
            risk_assessment="NUL",
            recommendation="RAS",
            thematique="TEST"
        ))
    return all_results