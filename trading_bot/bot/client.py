"""
client.py

Thin wrapper around python-binance's Client, configured to talk to the
Binance USDT-M Futures Demo Trading / Testnet API
(https://demo-fapi.binance.com).

Note: Binance retired the old standalone testnet.binancefuture.com sign-up
flow in a 2025 platform revamp. Futures Testnet ("Demo Trading") API keys
are now generated from your real Binance account's API Management page
while in Demo Trading mode, and REST calls go to demo-fapi.binance.com
instead of the old testnet.binancefuture.com host.

Keeping this in its own module isolates all "how do I talk to Binance"
concerns from order-building/validation/CLI logic.
"""

import os

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException, BinanceRequestException

from .logging_config import setup_logger

logger = setup_logger(__name__)

FUTURES_TESTNET_BASE_URL = "https://demo-fapi.binance.com"


class BotClientError(Exception):
    """Raised when the Binance client cannot be created or a call fails unexpectedly."""


def get_futures_testnet_client(api_key: str = None, api_secret: str = None) -> Client:
    """
    Build a python-binance Client pointed at the Futures Testnet.

    Credentials are read from arguments first, falling back to the
    BINANCE_TESTNET_API_KEY / BINANCE_TESTNET_API_SECRET environment
    variables so secrets never need to be hardcoded or passed on the CLI.
    """
    api_key = api_key or os.environ.get("BINANCE_TESTNET_API_KEY")
    api_secret = api_secret or os.environ.get("BINANCE_TESTNET_API_SECRET")

    if not api_key or not api_secret:
        raise BotClientError(
            "Missing API credentials. Set BINANCE_TESTNET_API_KEY and "
            "BINANCE_TESTNET_API_SECRET environment variables, or pass them explicitly."
        )

    try:
        client = Client(api_key, api_secret, testnet=True)
        # python-binance's `testnet` flag correctly maps the SPOT testnet;
        # for Futures we explicitly point FUTURES_URL at the futures testnet
        # host so all fapi/* calls resolve correctly.
        client.FUTURES_URL = FUTURES_TESTNET_BASE_URL + "/fapi"
    except Exception as exc:  # noqa: BLE001 - surfacing any client construction failure
        logger.exception("Failed to initialize Binance Futures Testnet client")
        raise BotClientError(f"Could not initialize Binance client: {exc}") from exc

    logger.info("Initialized Binance Futures Testnet client (base_url=%s)", client.FUTURES_URL)
    return client


# Re-export exceptions here so callers only need to import from `bot.client`
__all__ = [
    "get_futures_testnet_client",
    "BotClientError",
    "BinanceAPIException",
    "BinanceOrderException",
    "BinanceRequestException",
]
