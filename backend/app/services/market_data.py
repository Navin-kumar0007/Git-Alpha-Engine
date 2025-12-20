import httpx
import asyncio
import time

COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"

# ------------------------------
# SAFE REQUEST function (retry)
# ------------------------------
async def safe_get(client, url, params=None, max_retries=3):
    for attempt in range(max_retries):
        try:
            resp = await client.get(url, params=params, timeout=20)
            if resp.status_code == 429:
                await asyncio.sleep(2)   # delay on rate limit
                continue
            resp.raise_for_status()
            return resp.json()
        except Exception:
            await asyncio.sleep(1)
    return None


# ------------------------------
# Fetch CoinGecko Prices
# ------------------------------
async def _fetch_coingecko_markets(client, ids):
    params = {
        "vs_currency": "usd",
        "ids": ",".join(ids),
        "sparkline": True,
        "price_change_percentage": "24h"
    }

    data = await safe_get(client, COINGECKO_URL, params=params)

    if not data or not isinstance(data, list):
        # 🔥 Fallback if API fails or rate limited or returns error dict
        return [
            {
                "id": asset,
                "current_price": 0,
                "sparkline_in_7d": {"price": [1, 1, 1, 1, 1, 1, 1]},
                "price_change_percentage_24h_in_currency": 0,
            }
            for asset in ids
        ]

    return data


# ------------------------------
# Safe conversion helper
# ------------------------------
def safe_float(value, default=0.0):
    try:
        return float(value) if value is not None else default
    except:
        return default


# ------------------------------
# GitHub Repo Safe Fetch
# ------------------------------
async def fetch_repo_safe(client, repo):
    url = f"https://api.github.com/repos/{repo}"

    try:
        resp = await client.get(url, timeout=15)
        if resp.status_code == 403:
            return {"stars": 0, "commits": 0}  # rate limited fallback
        resp.raise_for_status()
        j = resp.json()

        return {
            "stars": j.get("stargazers_count", 0),
            "commits": j.get("open_issues_count", 0),  # placeholder
        }

    except:
        return {"stars": 0, "commits": 0}


# ------------------------------
# Build final asset entry
# ------------------------------
async def _build_asset_entry(asset, cg_data, github_metrics, repos):
    spark = cg_data.get("sparkline_in_7d", {}).get("price", [])
    if len(spark) == 0:
        spark = [1, 1, 1, 1, 1, 1, 1]  # fallback

    history_points = [
        {
            "day": f"D{i}",
            "price": safe_float(p),
            "commits": github_metrics.get("commits", 0)
        }
        for i, p in enumerate(spark[:7])
    ]
    
    # Map asset IDs to display names and symbols
    asset_info = {
        "bitcoin": {"name": "Bitcoin", "symbol": "BTC"},
        "ethereum": {"name": "Ethereum", "symbol": "ETH"},
        "solana": {"name": "Solana", "symbol": "SOL"},
        "matic-network": {"name": "Polygon", "symbol": "MATIC"},
        "chainlink": {"name": "Chainlink", "symbol": "LINK"},
        "binancecoin": {"name": "BNB", "symbol": "BNB"},
        "cardano": {"name": "Cardano", "symbol": "ADA"},
        "ripple": {"name": "XRP", "symbol": "XRP"},
        "polkadot": {"name": "Polkadot", "symbol": "DOT"},
        "near": {"name": "Near Protocol", "symbol": "NEAR"},
    }
    
    info = asset_info.get(asset, {"name": asset.title(), "symbol": asset.upper()[:4]})
    
    # Calculate simple alpha score based on price change and stars
    change = safe_float(cg_data.get("price_change_percentage_24h_in_currency"))
    stars = github_metrics.get("stars", 0)
    alpha_score = min(100, max(0, int(50 + change * 5 + stars / 1000)))

    return {
        "id": asset,
        "name": info["name"],
        "symbol": info["symbol"],
        "price": safe_float(cg_data.get("current_price")),
        "change24h": change,
        "alphaScore": alpha_score,
        "repo": repos.get(asset, "unknown/unknown"),
        "velocity": github_metrics.get("commits", 0),
        "sentiment": "Bullish" if change > 1 else "Bearish" if change < -1 else "Neutral",
        "keywords": ["crypto", "blockchain"],
        "description": f"{info['name']} cryptocurrency",
        "stars": github_metrics.get("stars", 0),
        "history": history_points,
    }


# ------------------------------
# MAIN FUNCTION: get_assets_with_metrics()
# ------------------------------
async def get_assets_with_metrics():
    assets = [
        "bitcoin",
        "ethereum",
        "solana",
        "matic-network",
        "chainlink",
        "binancecoin",
        "cardano",
        "ripple",
        "polkadot",
        "near"
    ]

    repos = {
        "bitcoin": "bitcoin/bitcoin",
        "ethereum": "ethereum/go-ethereum",
        "solana": "solana-labs/solana",
        "matic-network": "maticnetwork/bor",
        "chainlink": "smartcontractkit/chainlink",
        "binancecoin": "bnb-chain/bsc",
        "cardano": "input-output-hk/cardano-node",
        "ripple": "ripple/rippled",
        "polkadot": "paritytech/polkadot",
        "near": "near/nearcore"
    }

    try:
        async with httpx.AsyncClient() as client:

            # --- Fetch CoinGecko
            cg_data = await _fetch_coingecko_markets(client, assets)
            cg_map = {item["id"]: item for item in cg_data}

            # --- Fetch GitHub
            github_results = {}
            for asset in assets:
                github_results[asset] = await fetch_repo_safe(client, repos[asset])

            # --- Build response list
            final_assets = []
            for asset in assets:
                final_assets.append(
                    await _build_asset_entry(asset, cg_map.get(asset, {}), github_results[asset], repos)
                )

            return final_assets
    except Exception as e:
        print(f"Error in get_assets_with_metrics: {e}")
        # Fallback to empty/mock data to prevent 500
        return []
