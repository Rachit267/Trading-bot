#!/usr/bin/env python3
"""
cli.py

CLI entry point for the simplified Binance USDT-M Futures Testnet trading bot.

Example usage:
    python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
    python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 60000
"""

import argparse
import sys

from bot.client import BotClientError, get_futures_testnet_client
from bot.logging_config import setup_logger
from bot.orders import place_order
from bot.validators import validate_order_params

logger = setup_logger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Place MARKET or LIMIT orders on Binance USDT-M Futures Testnet.",
    )
    parser.add_argument("--symbol", required=True, help="Trading pair, e.g. BTCUSDT")
    parser.add_argument("--side", required=True, choices=["BUY", "SELL"], help="Order side")
    parser.add_argument(
        "--type", dest="order_type", required=True, choices=["MARKET", "LIMIT"], help="Order type"
    )
    parser.add_argument("--quantity", required=True, type=float, help="Order quantity")
    parser.add_argument(
        "--price", type=float, default=None, help="Limit price (required for LIMIT orders)"
    )
    parser.add_argument(
        "--api-key", dest="api_key", default=None,
        help="Binance testnet API key (falls back to BINANCE_TESTNET_API_KEY env var)",
    )
    parser.add_argument(
        "--api-secret", dest="api_secret", default=None,
        help="Binance testnet API secret (falls back to BINANCE_TESTNET_API_SECRET env var)",
    )
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # --- 1. Validate input ---
    try:
        clean = validate_order_params(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
        )
    except ValueError as exc:
        print(f"❌ Invalid input: {exc}")
        logger.error("Validation failed: %s", exc)
        return 1

    # --- 2. Print order request summary ---
    print("Order request summary:")
    print(f"  Symbol   : {clean['symbol']}")
    print(f"  Side     : {clean['side']}")
    print(f"  Type     : {clean['order_type']}")
    print(f"  Quantity : {clean['quantity']}")
    if clean["price"] is not None:
        print(f"  Price    : {clean['price']}")
    print()

    # --- 3. Build client ---
    try:
        client = get_futures_testnet_client(api_key=args.api_key, api_secret=args.api_secret)
    except BotClientError as exc:
        print(f"❌ Failed to connect to Binance Futures Testnet: {exc}")
        return 1

    # --- 4. Place order ---
    result = place_order(
        client=client,
        symbol=clean["symbol"],
        side=clean["side"],
        order_type=clean["order_type"],
        quantity=clean["quantity"],
        price=clean["price"],
    )

    summary = result.summary()
    print("Order response:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    print()

    if result.success:
        print("✅ Order placed successfully.")
        return 0
    else:
        print(f"❌ Order failed: {result.error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
