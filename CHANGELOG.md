# Change record

## 17 October 2026 — Explain the reports and organize the repository

- **Stayed the same:** All six research subjects, their calculations, Yahoo Finance requests, ticker selection, 15-minute cache, independent report errors, and the Streamlit run command. This update does not change the numeric output of an engine.
- **Changed:** The README now explains every displayed metric, its formula or provider source, how to read N/A, the project flow, and limits in beginner-friendly language. The original work log moved to `docs/WORK_LOG.md`.
- **File layout:** The dashboard stays at the root as `Dashboard_App.py`; the six engines and shared helpers moved into `stock_analyst/` with descriptive module names. Dashboard and test imports were updated to match. GitHub sorts each directory automatically, so folders and the README project map provide the navigable structure.
- **Compatibility note:** Code importing the former root-level engine module names must now import the corresponding `stock_analyst` module; the Streamlit launch command is unchanged.

| Former root file | Current file |
| --- | --- |
| `BusinessQ_Engine.py` | `stock_analyst/business_quality.py` |
| `FinancialH_Engine.py` | `stock_analyst/financial_health.py` |
| `Valuation_MomentumMetric.py` | `stock_analyst/valuation_momentum.py` |
| `Corr_hedgEngine.py` | `stock_analyst/correlation.py` |
| `management_insider_engine.py` | `stock_analyst/ownership_earnings.py` |
| `QuantativeNewsFeed.py` | `stock_analyst/news_sentiment.py` |
| `data_utils.py` | `stock_analyst/data_utils.py` |

## 17 October 2026 — Restore and test the six-report dashboard

This update turns the original collection of Yahoo Finance analysis scripts into a ticker-driven Streamlit app. It retains the six research subjects and the original sector and niche peer lists. The calculations and presentation below were changed deliberately; this is more than a formatting or error-handling patch.

### Dashboard

- **Before:** Opening the dashboard imported five scripts that fetched hard-coded data immediately. Entering another ticker and reloading those modules reset them to their hard-coded values. The default dashboard ticker was `IONQ`, while the engines used `AAPL` and, for financial health, `APLE` (Apple Hospitality REIT).
- **Now:** Each engine exposes `analyze(symbol)`. The dashboard fetches only when the user presses **Run selected report** or **Run all reports**. It clears prior results when the ticker changes, caches successful calls for 15 minutes, and shows each report's own provider error without hiding the other reports.
- **Presentation:** The six tabs and console-style printed dossiers became a report selector with tables, values and explanatory captions. The old ISA-specific and investment-decision language was removed. This changes the look and some wording, not the six subjects.

### Business quality (`BusinessQ_Engine.py`)

- Kept quarterly revenue, gross profit, operating income, and gross, operating and net margins. Raw net income and stockholders' equity are now visible alongside the original raw figures.
- Revenue growth still compares a quarter with the same quarter one year earlier. The input rows are aligned by statement date and unavailable values remain blank rather than shifting another period into place.
- **Changed ROE methodology:** The original multiplied one quarter's net income by four and divided by that quarter's equity. The new ROE uses four quarters of net income divided by the average of current and year-earlier equity. The label says `ROE TTM %`; early quarters without enough history are N/A.
- Removed global pandas formatting that could cause a later engine's money values to appear as percentages. The report displays the provider's reported currency code.

### Financial health (`FinancialH_Engine.py`)

- Kept current ratio, debt/equity, cash and invested-capital analysis. The fallback that sums `Cash Financial` and `Cash Equivalents` when an aggregate cash row is absent is retained and tested.
- **Changed ROIC methodology:** The original estimated EBIT as net income + tax provision + interest expense, fell back to operating income, multiplied by `(1 - 0.21)`, and divided the quarter's NOPAT by that quarter's invested capital. The new estimate uses trailing-four-quarter operating income as an EBIT proxy, the reported TTM tax provision divided by positive TTM pretax income, and average invested capital across a year. This can produce a materially different number. It is labelled as an estimate; invalid or missing inputs give N/A.
- Removed the unused free-cash-flow extraction and universal ratio target labels, which were not used in a calculation and are not suitable for all industries.

### Valuation and momentum (`Valuation_MomentumMetric.py`)

- Kept trailing/forward P/E, price/sales, EV/EBITDA, a roughly six-month price return and distance from a 200-session moving average.
- The return now uses the latest adjusted close versus the close **126 sessions earlier** (127 price observations). EV/EBITDA is shown only when EBITDA is positive. Missing and non-finite values show N/A, and the price uses the ticker's actual currency code instead of a fixed dollar sign.
- The provider's last price date is shown so a closed market or stale price is more obvious.

### Correlation (`Corr_hedgEngine.py`)

- Kept metadata-based sector/niche detection, the original peer lists, macro comparisons, daily log returns and Pearson correlations.
- Calculations now use adjusted close prices and pair each peer with the target separately. A peer must have at least 60 matching daily returns, so one sparse ticker does not discard the whole matrix.
- **Changed interpretation:** The former report called the least-correlated ticker a structural hedge or safe haven and recommended portfolio actions. The new report gives the closest and least-correlated comparisons as observations. Historical correlation alone does not establish future downside protection. `^VIX` is marked as a market indicator.

### Ownership and earnings (`management_insider_engine.py`)

- Kept the three original provider datasets: insider transactions, institutional holders and earnings surprises.
- Fixed the misspelled acquisitions/dispositions column lookup and counted `A` and `D` codes in the displayed recent rows. Each provider call can now fail independently. Earnings output excludes future rows without reported EPS.
- Removed misleading global percentage formatting that affected monetary values in the holder and insider tables.

### News sentiment (`QuantativeNewsFeed.py`)

- Retained the original bullish and bearish word lists and the score `(bullish matches - bearish matches) / total matches`.
- Fixed a missing comma that merged two words in the bullish set, removed leading whitespace in one entry, and made punctuation/hyphen tokenization consistent.
- Yahoo's ticker news call returned no articles during testing. The engine now tries Yahoo Search as a fallback and handles both observed article shapes. Five headlines were returned for each of AAPL and IONQ during the live check.
- The previous positive/negative/neutral “regime” verdict was removed. The score is presented as simple text classification, not a price prediction.

### Reproducibility and checks

- Pinned the four direct Python dependencies tested locally in `requirements.txt`; added run instructions and metric definitions in `README.md`.
- Added seven offline tests in `tests/test_analysis.py`, plus opt-in live engine and Streamlit UI smoke scripts.
- Live checks on 17 October 2026: 12 of 12 engine/ticker calls succeeded for AAPL and IONQ; all six AAPL views rendered in Streamlit; changing AAPL to IONQ cleared the old report and loaded IONQ revenue; the local server health endpoint returned HTTP 200.

### Limits

- Yahoo Finance is a changing public-data source. A live check is a snapshot, and some ratios remain N/A when statement rows are missing.
- Static peer lists need occasional review as listings and business classifications change.
- ROE and ROIC can be difficult to compare for firms with unusual or negative capital balances. The app exposes inputs and labels the ROIC as an estimate rather than an investment decision.
