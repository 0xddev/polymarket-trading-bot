#!/usr/bin/env python3
"""
Market Maker - Real-time order book monitoring for Polymarket BTC 5-min markets
Uses PolymarketBot to find markets and PolymarketCLOBWebSocket for live bid/ask data
"""

import os
import time
from datetime import datetime

# Try to load from .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from polymarket_bot import PolymarketBot
from websocket_client import PolymarketCLOBWebSocket


def main():
    """Initialize bot, find current market, and stream real-time order book data"""

    # ── 1. Load configuration from environment ──────────────────────────
    private_key = os.getenv("PRIVATE_KEY")
    if not private_key:
        print("ERROR: PRIVATE_KEY not set. Export it or add to .env")
        return

    host = os.getenv("HOST", "https://clob.polymarket.com")
    funder = os.getenv("FUNDER")
    chain_id = os.getenv("CHAIN_ID")
    signature_type = os.getenv("SIGNATURE_TYPE")

    # ── 2. Initialize PolymarketBot ─────────────────────────────────────
    bot = PolymarketBot(
        private_key=private_key,
        host=host,
        funder=funder,
        chain_id=chain_id,
        signature_type=signature_type,
    )

    if not bot.client:
        print("CLOB client failed to initialize. Check credentials.")
        return

    # ── 3. Find the current BTC 5-min up/down market ───────────────────
    print("\nSearching for active BTC 5-min market...")
    market = bot.find_current_market()

    if not market:
        print("Could not find any active BTC up/down 5-minute market")
        return

    # ── 4. Extract Up / Down token IDs ─────────────────────────────────
    token_ids = bot.get_token_ids(market)
    if not token_ids:
        print("Could not extract token IDs from market data")
        return

    up_token = token_ids["up_token_id"]
    down_token = token_ids["down_token_id"]
    print(f"  UP  token: {up_token}")
    print(f"  DOWN token: {down_token}")

    # ── 5. Set up WebSocket client for real-time order book ─────────────
    ws_client = PolymarketCLOBWebSocket()

    # TODO: Implement your own real-time data handling
    # - Define on_price_change / on_book_update callbacks
    # - Track bid/ask spreads, mid prices, and market signals
    # - Implement your own trading strategy based on real-time data
    # - Register callbacks: ws_client.on_price_change = your_handler
    # - Subscribe to tokens: ws_client.subscribe([up_token, down_token])

    def on_connect():
        """Subscribe to both UP and DOWN tokens once connected"""
        print("WebSocket connected — subscribing to tokens...")
        time.sleep(1)
        ws_client.subscribe([up_token, down_token])

    def on_disconnect(code, msg):
        print(f"WebSocket disconnected (code={code})")

    def on_error(err):
        print(f"WebSocket error: {err}")

    # Register callbacks
    ws_client.on_connect = on_connect
    ws_client.on_disconnect = on_disconnect
    ws_client.on_error = on_error

    # TODO: Register your own on_price_change and on_book_update callbacks
    # ws_client.on_price_change = your_price_change_handler
    # ws_client.on_book_update = your_book_update_handler
    raise NotImplementedError(
        "Market maker strategy removed. "
        "Implement your own real-time callbacks and trading logic."
    )

    # ── 6. Connect and stream ──────────────────────────────────────────
    print("\nConnecting to Polymarket CLOB WebSocket...")
    if ws_client.connect(debug=False):
        print("Streaming real-time order book — press Ctrl+C to stop\n")
        try:
            while ws_client.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nStopping...")
            ws_client.disconnect()
    else:
        print("Failed to connect to WebSocket")


if __name__ == "__main__":
    main()
