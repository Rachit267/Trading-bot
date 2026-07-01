"""
validators.py

Input validation for CLI-supplied order parameters.
Raises ValueError with a clear message on invalid input.
"""

import re

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}

# Basic pattern for Binance USDT-M futures symbols, e.g. BTCUSDT, ETHUSDT, 1000SHIBUSDT
SYMBOL_PATTERN = re.compile(r"^[A-Z0-9]{2,17}USDT$")


def validate_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if not SYMBOL_PATTERN.match(symbol):
        raise ValueError(
            f"Invalid symbol '{symbol}'. Expected a USDT-M futures pair, e.g. BTCUSDT."
        )
    return symbol


def validate_side(side: str) -> str:
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValueError(f"Invalid side '{side}'. Must be one of {sorted(VALID_SIDES)}.")
    return side


def validate_order_type(order_type: str) -> str:
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValueError(
            f"Invalid order type '{order_type}'. Must be one of {sorted(VALID_ORDER_TYPES)}."
        )
    return order_type


def validate_quantity(quantity: float) -> float:
    try:
        quantity = float(quantity)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid quantity '{quantity}'. Must be a positive number.")
    if quantity <= 0:
        raise ValueError(f"Invalid quantity '{quantity}'. Must be greater than 0.")
    return quantity


def validate_price(price, order_type: str):
    """
    Price is required for LIMIT orders and must be a positive number.
    Not applicable (and ignored) for MARKET orders.
    """
    if order_type == "MARKET":
        return None

    if price is None:
        raise ValueError("Price is required for LIMIT orders.")

    try:
        price = float(price)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid price '{price}'. Must be a positive number.")

    if price <= 0:
        raise ValueError(f"Invalid price '{price}'. Must be greater than 0.")

    return price


def validate_order_params(symbol: str, side: str, order_type: str, quantity: float, price=None):
    """
    Validate a full set of order parameters at once.
    Returns a dict of cleaned/normalized values.
    """
    clean_symbol = validate_symbol(symbol)
    clean_side = validate_side(side)
    clean_order_type = validate_order_type(order_type)
    clean_quantity = validate_quantity(quantity)
    clean_price = validate_price(price, clean_order_type)

    return {
        "symbol": clean_symbol,
        "side": clean_side,
        "order_type": clean_order_type,
        "quantity": clean_quantity,
        "price": clean_price,
    }
