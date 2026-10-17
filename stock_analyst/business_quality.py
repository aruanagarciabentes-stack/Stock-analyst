"""Quarterly profitability and trailing-twelve-month return on equity."""

import pandas as pd
import yfinance as yf

from stock_analyst.data_utils import display_frame, safe_ratio, statement_row


def analyze(symbol: str, ticker=None) -> pd.DataFrame:
    ticker = ticker or yf.Ticker(symbol)
    income = ticker.quarterly_income_stmt
    balance = ticker.quarterly_balance_sheet

    revenue = statement_row(income, "Total Revenue")
    if revenue.empty:
        raise ValueError("Quarterly revenue is unavailable for this ticker.")

    gross = statement_row(income, "Gross Profit")
    operating = statement_row(income, "Operating Income")
    net = statement_row(income, "Net Income")
    equity = statement_row(balance, "Stockholders Equity", "Common Stock Equity")

    yoy = safe_ratio(revenue - revenue.shift(4), revenue.shift(4), 100)
    ttm_net = net.rolling(4, min_periods=4).sum()
    average_equity = (equity + equity.shift(4)) / 2

    result = display_frame({
        "Revenue": revenue,
        "Gross profit": gross,
        "Operating income": operating,
        "Net income": net,
        "Stockholders equity": equity,
        "Gross margin %": safe_ratio(gross, revenue, 100),
        "Operating margin %": safe_ratio(operating, revenue, 100),
        "Net margin %": safe_ratio(net, revenue, 100),
        "Revenue growth YoY %": yoy,
        "ROE TTM %": safe_ratio(ttm_net, average_equity, 100),
    })
    try:
        info = ticker.info or {}
        result.attrs["currency"] = info.get("financialCurrency") or info.get("currency") or "Unknown"
    except Exception:
        result.attrs["currency"] = "Unknown"
    return result
