"""Valuation multiples and price momentum for the selected security."""

import math

import pandas as pd
import yfinance as yf


def _number(value):
    try:
        value = float(value)
        return value if math.isfinite(value) else None
    except (TypeError, ValueError):
        return None


def analyze(symbol: str, ticker=None) -> dict:
    ticker = ticker or yf.Ticker(symbol)
    info = ticker.info or {}
    history = ticker.history(period="1y", auto_adjust=True)
    close = (pd.to_numeric(history["Close"], errors="coerce").dropna()
             if history is not None and "Close" in history else pd.Series(dtype="float64"))

    latest = _number(close.iloc[-1]) if not close.empty else _number(info.get("currentPrice"))
    previous = _number(close.iloc[-127]) if len(close) >= 127 else None
    sma = _number(close.iloc[-200:].mean()) if len(close) >= 200 else None
    ev = _number(info.get("enterpriseValue"))
    ebitda = _number(info.get("ebitda"))

    return {
        "company": info.get("longName") or info.get("shortName") or symbol,
        "currency": info.get("currency") or "Unknown",
        "price": latest,
        "trailing_pe": _number(info.get("trailingPE")),
        "forward_pe": _number(info.get("forwardPE")),
        "price_to_sales": _number(info.get("priceToSalesTrailing12Months")),
        "ev_to_ebitda": ev / ebitda if ev is not None and ebitda is not None and ebitda > 0 else None,
        "return_6m_pct": (latest / previous - 1) * 100 if latest is not None and previous and previous > 0 else None,
        "distance_sma_200_pct": (latest / sma - 1) * 100 if latest is not None and sma and sma > 0 else None,
        "price_date": str(close.index[-1].date()) if not close.empty else None,
    }
