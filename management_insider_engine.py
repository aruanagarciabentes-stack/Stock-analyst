"""Provider-supplied insider, institutional holder, and earnings tables."""

import pandas as pd
import yfinance as yf


def _fetch(method, count=5):
    try:
        frame = method()
        return frame.head(count) if isinstance(frame, pd.DataFrame) else pd.DataFrame()
    except Exception as exc:
        return pd.DataFrame(), str(exc)


def analyze(symbol: str, ticker=None) -> dict:
    ticker = ticker or yf.Ticker(symbol)
    result = {}
    for name, method, count in (
        ("insiders", ticker.get_insider_transactions, 5),
        ("institutions", ticker.get_institutional_holders, 5),
        ("earnings", lambda: ticker.get_earnings_dates(limit=8), 8),
    ):
        fetched = _fetch(method, count)
        if isinstance(fetched, tuple):
            result[name] = fetched[0]
            result[name + "_error"] = fetched[1]
        else:
            result[name] = fetched

    insiders = result["insiders"]
    activity_col = next((name for name in ("Acquisitions or Dispositions", "Acquisition or Disposition")
                         if name in insiders.columns), None)
    if activity_col:
        values = insiders[activity_col].astype(str).str.upper().str.strip()
        result["buys"] = int(values.eq("A").sum())
        result["sells"] = int(values.eq("D").sum())
    else:
        result["buys"] = result["sells"] = None

    earnings = result["earnings"]
    if not earnings.empty and "Reported EPS" in earnings.columns:
        earnings = earnings.dropna(subset=["Reported EPS"])
        columns = [name for name in ("EPS Estimate", "Reported EPS", "Surprise(%)") if name in earnings]
        result["earnings"] = earnings[columns].head(4)
    return result
