# Stock Analyst

A Streamlit dashboard for exploring six types of public equity data: business quality, financial health, valuation and momentum, return correlation, ownership and earnings, and headline sentiment. Enter a ticker such as `AAPL`, `IONQ`, or `0700.HK`, then run one report or all six. Each section loads independently so a missing Yahoo Finance dataset does not block the others.

## Run locally

From the project folder in PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run Dashboard_App.py --server.address 127.0.0.1
```

The current working environment has Python 3.14.4 and the package versions pinned in `requirements.txt`. A network connection is needed to load Yahoo Finance data. The application starts without fetching a ticker; data is requested when you press a Run button. Streamlit caches successful report results for 15 minutes.

## What the figures mean

| Report | Calculation or interpretation |
| --- | --- |
| Business quality | Quarterly gross, operating and net margins; revenue growth against the same quarter a year earlier; TTM net income divided by average equity at the current and year-earlier quarter ends. |
| Financial health | Current assets / current liabilities; debt / equity; estimated TTM ROIC = TTM operating income after a reported effective tax rate divided by average invested capital (debt + equity - cash). Missing or unusable inputs produce N/A. |
| Valuation & momentum | Provider P/E and price/sales multiples; EV / EBITDA only with positive EBITDA; adjusted close return over 126 trading sessions; distance from the 200-session average. Prices are labelled with the provider's currency. |
| Correlation | Pairwise correlation of daily log returns over one year, requiring at least 60 shared observations per comparison. The peer universe is selected from company metadata and fixed comparison lists. Lowest correlation is only a historical observation, not a proven hedge. `^VIX` is a market indicator. |
| Ownership & earnings | Recent provider insider transactions, institutional holders and completed earnings dates. Acquisitions/dispositions are counted only when Yahoo supplies that classification. |
| News sentiment | Up to five recent Yahoo headlines; simple bullish/bearish word-count score from -1 to +1. This is exploratory text scoring, not a prediction. |

The average-equity ROE and average-capital ROIC conventions follow [CFA Institute's ROE discussion](https://rpc.cfainstitute.org/sites/default/files/-/media/documents/article/position-paper/cfa-leasing-paper.pdf) and [return-on-capital research](https://rpc.cfainstitute.org/sites/default/files/-/media/documents/book/rf-publication/1996/rf-v1996-n2-4456-pdf.pdf). Yahoo Finance's available fields determine whether this dashboard can calculate each estimate.

Data availability differs by ticker, security type and region. Yahoo Finance can delay or revise figures. Neither the classifications nor the ratios are investment recommendations. For a demo, `AAPL` and `IONQ` were checked live on 17 October 2026; always verify current values before showing them publicly.

## Verify

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_*.py -v
.\.venv\Scripts\python.exe tests\live_smoke.py AAPL IONQ
.\.venv\Scripts\python.exe tests\ui_smoke.py
```

The first command is offline. The latter two contact Yahoo Finance. `CHANGELOG.md` explains the before/after changes in each engine; `WORK_LOG.md` records the run and latest test results.
