"""
api.py
------
Fetches live cryptocurrency prices from CoinGecko's free public API.
No API key required for basic price queries.
"""

import urllib.request
import urllib.error
import json

# Mapping of ticker symbol → CoinGecko coin ID
COINGECKO_IDS: dict[str, str] = {
    "BTC":   "bitcoin",
    "ETH":   "ethereum",
    "SOL":   "solana",
    "BNB":   "binancecoin",
    "XRP":   "ripple",
    "ADA":   "cardano",
    "DOGE":  "dogecoin",
    "DOT":   "polkadot",
    "MATIC": "matic-network",
    "LTC":   "litecoin",
    "AVAX":  "avalanche-2",
    "LINK":  "chainlink",
    "UNI":   "uniswap",
    "ATOM":  "cosmos",
    "TRX":   "tron",
    "SHIB":  "shiba-inu",
    "TON":   "the-open-network",
    "BCH":   "bitcoin-cash",
    "NEAR":  "near",
    "APT":   "aptos",
}

# Reverse map: coingecko_id → symbol (built once at import time)
_ID_TO_SYMBOL: dict[str, str] = {v: k for k, v in COINGECKO_IDS.items()}

BASE_URL = "https://api.coingecko.com/api/v3/simple/price"


def fetch_prices(symbols: list[str]) -> dict[str, float]:
    """
    Fetch current USD prices for the given list of ticker symbols.

    Returns a dict like {"BTC": 67000.0, "ETH": 3500.0, ...}.
    Returns an empty dict on any network or parsing error.
    """
    if not symbols:
        return {}

    # Only request IDs we know about
    ids = [COINGECKO_IDS[s.upper()] for s in symbols if s.upper() in COINGECKO_IDS]
    if not ids:
        return {}

    ids_str = ",".join(ids)
    url = f"{BASE_URL}?ids={ids_str}&vs_currencies=usd"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "CryptoTracker/1.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            raw = response.read()
            data: dict = json.loads(raw)

        # Map back: coingecko_id → symbol → price
        result: dict[str, float] = {}
        for cg_id, price_data in data.items():
            symbol = _ID_TO_SYMBOL.get(cg_id)
            if symbol and "usd" in price_data:
                result[symbol] = float(price_data["usd"])
        return result

    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, TimeoutError):
        return {}


def get_supported_symbols() -> list[str]:
    """Return all ticker symbols that can be fetched via the API."""
    return sorted(COINGECKO_IDS.keys())
