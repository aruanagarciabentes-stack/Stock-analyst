"""Liquidity, solvency, and an explicitly defined ROIC estimate."""

import pandas as pd
import yfinance as yf

from data_utils import display_frame, safe_ratio, statement_row


def analyze(symbol: str, ticker=None) -> pd.DataFrame:
    ticker = ticker or yf.Ticker(symbol)
    balance = ticker.quarterly_balance_sheet
    income = ticker.quarterly_income_stmt
    if balance is None or balance.empty:
        raise ValueError("Quarterly balance-sheet data is unavailable for this ticker.")

    assets = statement_row(balance, "Current Assets")
    liabilities = statement_row(balance, "Current Liabilities")
    equity = statement_row(balance, "Stockholders Equity", "Common Stock Equity")
    debt = statement_row(balance, "Total Debt")
    cash = statement_row(balance, "Cash Cash Equivalents And Short Term Investments",
                         "Cash And Cash Equivalents")
    if cash.empty:
        cash_financial = statement_row(balance, "Cash Financial")
        cash_equivalents = statement_row(balance, "Cash Equivalents")
        if not cash_financial.empty or not cash_equivalents.empty:
            cash = cash_financial.add(cash_equivalents, fill_value=0)
    operating = statement_row(income, "Operating Income")
    tax = statement_row(income, "Tax Provision")
    pretax = statement_row(income, "Pretax Income")

    invested = debt + equity - cash
    average_invested = (invested + invested.shift(4)) / 2
    ttm_operating = operating.rolling(4, min_periods=4).sum()
    ttm_tax = tax.rolling(4, min_periods=4).sum()
    ttm_pretax = pretax.rolling(4, min_periods=4).sum()
    effective_tax = safe_ratio(ttm_tax, ttm_pretax).where(ttm_pretax > 0)
    effective_tax = effective_tax.where(effective_tax.between(0, 1))
    nopat = ttm_operating * (1 - effective_tax)

    return display_frame({
        "Current ratio x": safe_ratio(assets, liabilities),
        "Debt / equity x": safe_ratio(debt, equity),
        "ROIC estimate TTM %": safe_ratio(nopat, average_invested.where(average_invested > 0), 100),
    })
