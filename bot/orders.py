"""
orders.py

Order placement logic for Binance USDT-M Futures Testnet.
Handles both MARKET and LIMIT orders, with logging of requests/responses
and translation of Binance exceptions into a consistent result shape.
"""

from binance.exceptions import BinanceAPIException, BinanceOrderException, BinanceRequestException

from .logging_config import setup_logger

logger = setup_logger(__name__)


class OrderResult:
    """Simple container describing the outcome of a placed order."""

    def __init__(self, success: bool, raw_response: dict = None, error: str = None):
        self.success = success
        self.raw_response = raw_response or {}
        self.error = error

    def summary(self) -> dict:
        if self.success:
            return {
                "success": True,
                "orderId": self.raw_response.get("orderId"),
                "status": self.raw_response.get("status"),
                "executedQty": self.raw_response.get("executedQty"),
                "avgPrice": self.raw_response.get("avgPrice"),
                "symbol": self.raw_response.get("symbol"),
                "side": self.raw_response.get("side"),
                "type": self.raw_response.get("type"),
            }
        return {"success": False, "error": self.error}


def place_order(client, symbol: str, side: str, order_type: str, quantity: float, price=None) -> OrderResult:
    """
    Place a MARKET or LIMIT order on Binance USDT-M Futures Testnet.

    Parameters are assumed to already be validated (see bot.validators).
    Returns an OrderResult; never raises for expected API/network failures
    so the CLI layer can print a clean success/failure message.
    """
    order_kwargs = {
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "quantity": quantity,
    }

    if order_type == "LIMIT":
        order_kwargs.update({
            "price": price,
            "timeInForce": "GTC",  # Good-Til-Canceled, required for LIMIT orders
        })

    logger.info("Order request: %s", order_kwargs)

    try:
        response = client.futures_create_order(**order_kwargs)
        logger.info("Order response: %s", response)
        return OrderResult(success=True, raw_response=response)

    except (BinanceAPIException, BinanceOrderException) as exc:
        logger.error("Binance API rejected the order: %s", exc)
        return OrderResult(success=False, error=f"Binance API error: {exc}")

    except BinanceRequestException as exc:
        logger.error("Malformed request sent to Binance: %s", exc)
        return OrderResult(success=False, error=f"Request error: {exc}")

    except (ConnectionError, TimeoutError) as exc:
        logger.error("Network failure while placing order: %s", exc)
        return OrderResult(success=False, error=f"Network error: {exc}")

    except Exception as exc:  # noqa: BLE001 - last-resort catch so the CLI never crashes raw
        logger.exception("Unexpected error while placing order")
        return OrderResult(success=False, error=f"Unexpected error: {exc}")
