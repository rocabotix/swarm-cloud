import asyncio
import logging
from datetime import datetime, timezone
from config import THEMATIQUES, TAG_FILTERS
from api_client import get_trending_markets, get_top_holders, get_wallet_creation_time
from swarm_graph import run_debate, WalletSignal
from reporter import generate_daily_report
from models import DebateResult

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

            # On prend le premier marché trouvé
            market = trending[0]
            market_slug = market.get("slug") or market.get("id", "unknown")
            
            # Récupération des parieurs (Holders)
            holders = get_top_holders(market_slug, limit=3, min_balance=500)
            
            if holders:
                for holder in holders[:2]:
                    wallet = holder.get("proxyWallet") or holder.get("userId", "unknown")
                    signal = WalletSignal(
                        wallet=wallet,
                        market_slug=market_slug,
                        thematique=thema,
                        position_size=float(holder.get("size", 0)),
                        age_days=30, # Valeur par défaut pour le test
                        risk_level="Medium"
                    )
                    # LANCEMENT DU DÉBAT IA
                    debate = run_debate(signal)
                    if debate and debate.get("final_result"):
                        all_results.append(debate["final_result"])
        
        except Exception as e:
            logger.error(f"Erreur sur {thema}: {e}")

    # --- SÉCURITÉ : MODE TEST SI VIDE ---
    if not all_results:
        print("⚠️ Aucun signal réel trouvé. Envoi d'un signal de TEST.")
        test_signal = DebateResult(
            final_verdict="TEST SYSTÈME",
            confidence=99,
            summary="Test de connexion technique (Aucun holder trouvé sur Polymarket)",
            key_arguments=[
                "✅ ANALYSTE : Le système de scan fonctionne.",
                "⚠️ CONTRADICTEUR : En attente de vrais mouvements on-chain."
            ],
            risk_assessment="NUL",
            recommendation="Vérifier les logs Render pour plus de détails.",
            thematique="TEST"
        )
        all_results.append(test_signal)

    return all_results

if __name__ == "__main__":
    asyncio.run(test_swarm())