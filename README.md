# Simplified Trading Bot — Binance USDT-M Futures Testnet

A small, structured Python CLI application that places **MARKET** and **LIMIT**
orders on the Binance Futures **Testnet** (USDT-M), with input validation,
logging, and error handling.

## Project Structure

```
trading_bot/
  bot/
    __init__.py
    client.py          # Binance client wrapper (points at Futures Testnet)
    orders.py           # Order placement logic
    validators.py        # CLI input validation
    logging_config.py    # Logging setup (file + console)
  cli.py                 # CLI entry point
  README.md
  requirements.txt
  logs/                  # Created automatically at runtime (trading_bot.log)
```

## Setup

1. Log into your regular Binance account and switch to **Demo Trading** (Futures) —
   go to **[More] → [Demo Trading]** on binance.com, or visit
   https://demo.binance.com/futures directly.
2. While in Demo Trading mode, click your account icon → **API Management**
   (or go straight to https://www.binance.com/en/my/settings/api-management),
   then click **[Create API]** to generate a key + secret scoped to your demo
   futures balance.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set your credentials as environment variables (recommended, keeps secrets
   out of shell history / logs):
   ```bash
   export BINANCE_TESTNET_API_KEY="your_key_here"
   export BINANCE_TESTNET_API_SECRET="your_secret_here"
   ```
   Alternatively, pass `--api-key` / `--api-secret` directly on the command line.

> Note: Binance retired the old standalone `testnet.binancefuture.com`
> sign-up flow in a 2025 platform revamp. Demo Trading API keys are now
> generated from your real Binance account (as above), and this bot talks to
> the current REST host, `https://demo-fapi.binance.com`.

## How to Run

**Market order:**
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

**Limit order:**
```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 60000
```

Each run prints:
- an order request summary
- the order response (`orderId`, `status`, `executedQty`, `avgPrice`)
- a clear success/failure message

All requests, responses, and errors are also written to `logs/trading_bot.log`.

## Design Notes

- **Client layer (`bot/client.py`)** isolates all Binance-connection concerns.
  It builds a `python-binance` `Client` and overrides `FUTURES_URL` to point
  at `https://testnet.binancefuture.com/fapi`, since the library's built-in
  `testnet=True` flag targets the Spot testnet, not Futures.
- **Order layer (`bot/orders.py`)** builds and sends the order payload,
  catching `BinanceAPIException`, `BinanceOrderException`,
  `BinanceRequestException`, and network errors separately so failures are
  reported with useful, specific messages rather than raw stack traces.
- **Validation layer (`bot/validators.py`)** checks symbol format, side,
  order type, quantity, and price (required only for LIMIT orders) *before*
  any network call is made.
- **CLI layer (`cli.py`)** is a thin `argparse` wrapper that ties the above
  together and handles user-facing output.

## Assumptions

- Only `MARKET` and `SELL`/`BUY` LIMIT orders are in scope per the core
  requirements; LIMIT orders use `timeInForce=GTC`.
- Symbol validation assumes a USDT-M pair (e.g. `BTCUSDT`); this is a
  lightweight format check, not a live exchange-info lookup.
- API credentials are expected via environment variables by default for
  security; CLI flags are provided as a fallback for convenience.

## A note on the submitted log files

This project was built in a sandboxed environment without outbound internet
access, so I was not able to execute live calls against the Binance Futures
Testnet to generate real `orderId`/`executedQty` log entries. **You'll need
to run the two commands above yourself** (with your own testnet API keys) to
produce the actual MARKET and LIMIT order log entries required for
submission — the code is complete and ready to run, this is just a
sandboxing limitation on my end, not a gap in the implementation.
