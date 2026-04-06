import asyncio
import logging
from datetime import datetime, timezone
from config import THEMATIQUES, TAG_FILTERS
from api_client import get_trending_markets, get_top_holders, get_wallet_creation_time
from swarm_graph import run_debate, WalletSignal
from reporter import generate_daily_report

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

async def test_swarm():
    print("=" * 70)
    print("TEST COMPLET DU SWARM - Polymarket Insider")
    print("=" * 70)
    now = datetime.now(timezone.utc)
    print(f"Date : {now.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    all_results = []
    test_count = 0
    for thema in THEMATIQUES:
        print(f"Analyse : {thema}")
        try:
            tag_filter = TAG_FILTERS.get(thema, thema.lower())
            trending = get_trending_markets(limit=20, tag_filter=tag_filter)
            print(f"   -> {len(trending)} marches trouves")
            if not trending:
                print("   Aucun marche")
                continue
            seen_slugs = [r.summary.split(" sur ")[-1] for r in all_results if hasattr(r, "summary")]
            market = next((m for m in trending if (m.get("slug") or m.get("id", "")) not in seen_slugs), trending[0])
            market_question = market.get("question", "N/A")
            market_slug = market.get("slug") or market.get("id", "unknown")
            print(f"   -> {market_question[:60]}")
            holders = get_top_holders(market_slug, limit=8, min_balance=500)
            print(f"   -> {len(holders)} holders recuperes")
            if not holders:
                print("   Signal synthetique")
                signal = WalletSignal(
                    wallet="0xSYNTHETIC",
                    market_slug=market_slug,
                    thematique=thema,
                    position_size=1000.0,
                    age_days=45,
                    risk_level="Medium"
                )
                result = run_debate(signal)
                if result and result.get("final_result"):
                    all_results.append(result["final_result"])
                    test_count += 1
                    verdict = result["final_result"].final_verdict
                    score = result["final_result"].confidence
                    print(f"   Verdict : {verdict} ({score}%)")
                continue
            for holder in holders[:3]:
                wallet = holder.get("proxyWallet") or holder.get("userId", "unknown")
                position_size = float(holder.get("size", 0))
                creation_time = get_wallet_creation_time(wallet)
                age_days = (datetime.now(timezone.utc) - creation_time.replace(tzinfo=timezone.utc)).days if creation_time else None
                signal = WalletSignal(
                    wallet=wallet,
                    market_slug=market_slug,
                    thematique=thema,
                    position_size=position_size,
                    age_days=age_days,
                    risk_level="Medium"
                )
                result = run_debate(signal)
                if result and result.get("final_result"):
                    all_results.append(result["final_result"])
                    test_count += 1
                    verdict = result["final_result"].final_verdict
                    score = result["final_result"].confidence
                    print(f"   Verdict : {verdict} ({score}%)")
        except Exception as e:
            logger.error(f"Erreur sur {thema}: {e}")
    print("Generation du rapport...")
    report = generate_daily_report(all_results)
    print("=" * 70)
    print("RESULTAT DU TEST")
    print("=" * 70)
    print(report)
    print("=" * 70)
    print(f"Test termine : {test_count} signaux analyses.")
    return all_results

if __name__ == "__main__":
    asyncio.run(test_swarm())