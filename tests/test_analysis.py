"""Offline checks for calculations and provider edge cases."""

import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd
import yfinance as yf


with patch.object(yf, "Ticker", side_effect=AssertionError("network call during import")):
    from stock_analyst import business_quality as business
    from stock_analyst import correlation
    from stock_analyst import financial_health as financial
    from stock_analyst import news_sentiment as news
    from stock_analyst import ownership_earnings as ownership
    from stock_analyst import valuation_momentum as valuation


class FakeTicker:
    def __init__(self):
        dates = pd.date_range("2025-03-31", periods=5, freq="QE")
        self.quarterly_income_stmt = pd.DataFrame({
            date: {"Total Revenue": revenue, "Gross Profit": revenue / 2,
                   "Operating Income": 20, "Net Income": 10,
                   "Tax Provision": 5, "Pretax Income": 25}
            for date, revenue in zip(dates, [100, 110, 120, 130, 150])
        })
        self.quarterly_balance_sheet = pd.DataFrame({
            date: {"Current Assets": 200, "Current Liabilities": 100,
                   "Stockholders Equity": 100, "Total Debt": 50,
                   "Cash And Cash Equivalents": 10}
            for date in dates
        })
        self.info = {"currency": "USD", "longName": "Fixture Corp", "currentPrice": 100,
                     "trailingPE": 10, "enterpriseValue": 1000, "ebitda": 100}
        self.news = []

    def history(self, **_kwargs):
        return pd.DataFrame({"Close": np.arange(1, 202, dtype=float)},
                            index=pd.date_range("2025-01-01", periods=201, freq="B"))

    def get_insider_transactions(self):
        return pd.DataFrame({"Acquisitions or Dispositions": ["A", "D", "A"]})

    def get_institutional_holders(self):
        return pd.DataFrame()

    def get_earnings_dates(self, **_kwargs):
        return pd.DataFrame()


class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.ticker = FakeTicker()

    def test_business_uses_ttm_roe_and_same_quarter_growth(self):
        result = business.analyze("TEST", self.ticker)
        self.assertAlmostEqual(result.iloc[0]["Revenue growth YoY %"], 50)
        self.assertAlmostEqual(result.iloc[0]["ROE TTM %"], 40)
        self.assertEqual(result.attrs["currency"], "USD")

    def test_financial_ratios_and_missing_denominator(self):
        result = financial.analyze("TEST", self.ticker)
        self.assertAlmostEqual(result.iloc[0]["Current ratio x"], 2)
        self.assertAlmostEqual(result.iloc[0]["ROIC estimate TTM %"], 64 / 140 * 100)
        self.ticker.quarterly_balance_sheet.loc["Current Liabilities"] = 0
        result = financial.analyze("TEST", self.ticker)
        self.assertTrue(pd.isna(result.iloc[0]["Current ratio x"]))

    def test_cash_component_fallback_preserves_roic(self):
        self.ticker.quarterly_balance_sheet = self.ticker.quarterly_balance_sheet.drop(
            index="Cash And Cash Equivalents")
        self.ticker.quarterly_balance_sheet.loc["Cash Financial"] = 6
        self.ticker.quarterly_balance_sheet.loc["Cash Equivalents"] = 4
        result = financial.analyze("TEST", self.ticker)
        self.assertAlmostEqual(result.iloc[0]["ROIC estimate TTM %"], 64 / 140 * 100)

    def test_momentum_and_currency(self):
        result = valuation.analyze("TEST", self.ticker)
        self.assertEqual(result["currency"], "USD")
        self.assertAlmostEqual(result["ev_to_ebitda"], 10)
        self.assertAlmostEqual(result["return_6m_pct"], (201 / 75 - 1) * 100)

    def test_insider_counts_and_empty_news(self):
        result = ownership.analyze("TEST", self.ticker)
        self.assertEqual((result["buys"], result["sells"]), (2, 1))
        with patch.object(yf, "Search", return_value=type("EmptySearch", (), {"news": []})()):
            self.assertIsNone(news.analyze("TEST", self.ticker)["average_score"])
        self.assertEqual(news.analyze_headline_sentiment("adoption grows"), 1)

    def test_news_search_fallback_shape(self):
        article = {"title": "Adoption grows", "publisher": "Fixture Wire",
                   "link": "https://example.com/a", "providerPublishTime": 1_700_000_000}
        with patch.object(yf, "Search", return_value=type("Search", (), {"news": [article]})()):
            result = news.analyze("TEST", self.ticker)
        self.assertEqual(len(result["headlines"]), 1)
        self.assertEqual(result["headlines"].iloc[0]["Link"], "https://example.com/a")
        self.assertEqual(result["average_score"], 1)

    def test_correlation_uses_available_pairs(self):
        dates = pd.date_range("2025-01-01", periods=80, freq="B")
        base = np.exp(np.cumsum(np.linspace(0.001, 0.02, 80)))
        prices = pd.DataFrame({"TEST": base, "AAA": base * 2,
                               "BBB": 100 / base, "CCC": [np.nan] * 50 + list(base[50:])},
                              index=dates)
        prices.columns = pd.MultiIndex.from_product([["Close"], prices.columns])
        result = correlation.analyze(
            "TEST", downloader=lambda *_args, **_kwargs: prices,
            discoverer=lambda _symbol: (["AAA", "BBB", "CCC"], "Fixture", "Test", "Fixture Corp"))
        self.assertEqual(set(result["correlations"]["Ticker"]), {"AAA", "BBB"})
        self.assertAlmostEqual(result["correlations"].iloc[0]["Correlation"], 1)
        self.assertAlmostEqual(result["correlations"].iloc[1]["Correlation"], -1)


if __name__ == "__main__":
    unittest.main()
