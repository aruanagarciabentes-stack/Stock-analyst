# Stock Analyst

Stock Analyst is a local Streamlit dashboard for exploring a public company's financial statements, share-price history, ownership data and recent headlines. Enter a stock **ticker** (a market code such as `AAPL`, `IONQ` or `0700.HK`) and choose one of six reports. Data comes from Yahoo Finance through `yfinance`. The app does not trade or host a public website.

New to finance? Start with **Business quality** for sales and profit, then **Financial health** for debt and short-term resources. **Valuation & momentum** describes the share price, **Correlation** compares past price movements, **Ownership & earnings** shows available records, and **News sentiment** scores recent headlines. A larger number is not always better: a high valuation multiple can reflect high expectations rather than a bargain.

## Run locally

Install [Python](https://www.python.org/downloads/). From the project folder in PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run Dashboard_App.py --server.address 127.0.0.1
```

Open the local address Streamlit prints (usually `http://127.0.0.1:8501`). Enter a ticker in the sidebar, select a report, and press **Run selected report**. **Run all reports** fetches all six; use the selector to see each one. Changing the ticker clears the prior company's results. Internet access is required for data, but the app opens before fetching anything. Successful results are cached for 15 minutes.

## How to read the numbers

**Money** uses the company's reported currency, shown above the business-quality table; it is not converted to your home currency. The price report shows its own currency. **%** means “per 100”; **x** means “times” (a ratio or multiple). A **quarter** is a three-month reporting period. **TTM** means the latest four quarters together (“trailing twelve months”). **YoY** compares a quarter with the same quarter a year earlier. **N/A** means the provider did not supply enough usable data; it does not mean zero. Quarterly tables show the newest available period first.

### 1. Business quality: sales and profit

Money rows come from quarterly statements. Stockholders' equity is a balance at the quarter end; the other money rows cover that quarter.

| Value | What it means | This app's calculation |
| --- | --- | --- |
| Revenue | Money from selling goods or services, before expenses. | Reported quarterly total revenue. |
| Gross profit | Revenue after the direct cost of what was sold. | Reported quarterly gross profit. |
| Operating income | Profit from ordinary operations before interest and taxes. | Reported quarterly operating income. |
| Net income | Profit after all reported expenses and taxes; it can be negative. | Reported quarterly net income. |
| Stockholders equity | Accounting value belonging to shareholders: assets less liabilities. | Reported quarter-end equity; it can be negative. |
| Gross margin % | Share of revenue left as gross profit. | Gross profit ÷ revenue × 100. |
| Operating margin % | Share of revenue left as operating profit. | Operating income ÷ revenue × 100. |
| Net margin % | Share of revenue left as net profit. | Net income ÷ revenue × 100. |
| Revenue growth YoY % | Change in sales from the same quarter last year. | (Current revenue ÷ revenue four quarters earlier − 1) × 100. |
| ROE TTM % | *Return on equity*: annual profit relative to shareholders' accounting equity. | Latest four quarters' net income ÷ average equity at current and year-earlier quarter ends × 100. |

For example, revenue of 100 and gross profit of 40 gives a **40% gross margin**. ROE needs four profit quarters and two equity dates, so early rows can show N/A. Negative or tiny equity can make ROE difficult to interpret.

### 2. Financial health: obligations and capital

| Value | What it means | This app's calculation |
| --- | --- | --- |
| Current ratio x | Short-term resources relative to short-term bills. 2x means two units of current assets for each unit of current liabilities. | Current assets ÷ current liabilities. |
| Debt / equity x | Borrowing relative to shareholders' accounting equity. | Total debt ÷ stockholders' equity. |
| ROIC estimate TTM % | *Return on invested capital*: estimated after-tax operating profit relative to capital used by the business. | Latest four quarters' operating income × (1 − reported effective tax rate) ÷ average invested capital × 100. |

For ROIC, invested capital = total debt + equity − cash. The app averages that value at the current and year-earlier quarter ends. Its effective tax rate is TTM tax provision ÷ positive TTM pretax income. ROIC shows N/A without enough quarters, with missing inputs, with an effective tax rate outside 0–100%, or with nonpositive average invested capital. A 2x current ratio is an example, not a universal target for every industry.

### 3. Valuation & momentum: the market price

**Valuation** compares a share or whole-company price with business results. **Momentum** describes past adjusted share-price movement; it does not predict the next movement.

| Value | What it means | This app's calculation |
| --- | --- | --- |
| Last close | Latest available closing share price, with date and currency. | Latest adjusted close in one year of history; provider current price is a fallback. |
| Trailing P/E | Share price divided by past-year earnings per share. 20x means paying 20 currency units for each 1 unit of past annual earnings per share. | Yahoo's reported trailing P/E. |
| Forward P/E | Share price divided by *estimated future* earnings per share; estimates can change. | Yahoo's reported forward P/E. |
| Price / sales | Share value relative to sales over the past year. | Yahoo's reported trailing price-to-sales multiple. |
| EV / EBITDA | Whole-business value, including debt and accounting for cash, relative to earnings before interest, tax, depreciation and amortisation. | Provider enterprise value ÷ provider EBITDA, only when EBITDA is positive. |
| 126-session return | Approximately six months of adjusted share-price change; a session is a trading day. | (Latest adjusted close ÷ adjusted close 126 sessions earlier − 1) × 100. |
| Distance from 200-session average | How far the latest adjusted close is above or below its average over 200 trading sessions. | (Latest adjusted close ÷ average of last 200 adjusted closes − 1) × 100. |

“Adjusted close” uses Yahoo's price adjustments. The return measure does not separately add cash dividend income. P/E may be unavailable when earnings are negative or missing. A low multiple is not automatically cheap; compare a firm with similar businesses and its own history.

### 4. Correlation: did prices move together?

The report shows company name, sector and industry, then compares daily *log returns* (day-to-day price changes) over roughly one year. Sector and niche peers come from curated lists selected using the company's Yahoo metadata, alongside broad-market comparisons. They are examples, not a complete competitor list.

| Value | What it means |
| --- | --- |
| Ticker | Code for the comparison security, ETF or indicator. |
| Correlation | Number from −1 to +1. Near +1 means returns tended to move together; near 0 means little consistent linear relationship; near −1 means they tended to move oppositely. |
| Paired days | Trading days with usable returns for both series; at least 60 are required for each comparison. |
| Type | “Security/ETF” is a traded comparison; “Market indicator” marks an index such as `^VIX`. |
| Closest observed comparison / Lowest observed correlation | Highest and lowest scores among the available comparisons. These are historical observations, not hedge recommendations. |

For example, +0.8 is a stronger historical tendency to move together than +0.2. Low or negative correlation cannot guarantee protection in a market fall. `^VIX` is an indicator, not a share you can buy directly.

### 5. Ownership & earnings: available records

**Insider transactions** displays up to five recent provider rows involving company insiders. When Yahoo supplies its acquisitions/dispositions classification, the caption counts `A` (acquisitions) and `D` (dispositions) **within the displayed rows**. They are not a complete count of open-market buys and sells. **Institutional holders** displays up to five provider-supplied holder rows. A reported holding is a snapshot, not a live position. The app does not retrieve or verify original regulatory filings.

**Reported earnings** shows completed results with **EPS** (earnings per share, or profit per share). **EPS Estimate** is the prior expectation, **Reported EPS** is the published result, and **Surprise(%)** is Yahoo's percent difference between them, when provided. Future dates without reported EPS are excluded. One missing table need not block the others.

### 6. News sentiment: words in headlines

The table displays up to five headlines with **Published** time, **Source**, **Headline**, **Score** and **Link**. The fixed word lists count bullish and bearish matches: (bullish matches − bearish matches) ÷ total matches. Scores run from **−1** (only bearish matches) through **0** (balanced or no matched words) to **+1** (only bullish matches). **Average headline score** is the mean of displayed scores, or N/A when there are no headlines. The app tries Yahoo ticker news, then Yahoo Search if needed. This word count cannot reliably understand context, irony or whether news is already reflected in the share price.

## Project map

```text
Dashboard_App.py             Streamlit controls and report display
stock_analyst/
  business_quality.py        Quarterly profit, margins, growth and ROE
  financial_health.py        Balance-sheet ratios and estimated ROIC
  valuation_momentum.py      Valuation fields and adjusted-price measures
  correlation.py             Peer discovery and return correlations
  ownership_earnings.py      Insider, holder and completed earnings tables
  news_sentiment.py          Headline retrieval and dictionary scores
  data_utils.py              Shared statement alignment and safe division
tests/                       Offline tests and optional live/UI checks
docs/WORK_LOG.md             Original repair and verification log
CHANGELOG.md                 What changed and what stayed
requirements.txt             Tested direct Python dependencies
```

Each report's `analyze(symbol)` function fetches only the data it needs. The dashboard handles errors separately, so an empty Yahoo dataset in one report need not hide the others. `correlation.py` also has a `run_correlation_pipeline()` command-line entry point.

## Verify

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_*.py -v
.\.venv\Scripts\python.exe tests\live_smoke.py AAPL IONQ
.\.venv\Scripts\python.exe tests\ui_smoke.py
```

The first command uses fixed samples and needs no network. The next two contact Yahoo Finance and may fail when public data is unavailable. A live AAPL/IONQ check passed on 17 October 2026; that dated result is not a promise of future availability. See [CHANGELOG.md](CHANGELOG.md) for the earlier engine corrections and this layout update, and [docs/WORK_LOG.md](docs/WORK_LOG.md) for the original run log.

## Data and interpretation limits

Yahoo Finance fields vary by ticker, market and security type; figures can be missing, delayed or revised. The app does not audit filings, convert all currencies, or turn its reports into investment recommendations. Verify a figure against the company's filings or another reliable source before using it publicly. ROIC is explicitly this project's estimate, and static comparison lists can become outdated.

For background, see CFA Institute on [financial ratios](https://www.cfainstitute.org/sites/default/files/-/media/documents/support/programs/cfa/cfa_program_level_ii_financial_ratio_list.pdf), [valuation multiples](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/market-based-valuation-price-enterprise-value-multiples), [ROE](https://rpc.cfainstitute.org/sites/default/files/-/media/documents/article/position-paper/cfa-leasing-paper.pdf) and [return on invested capital](https://rpc.cfainstitute.org/sites/default/files/-/media/documents/book/rf-publication/1996/rf-v1996-n2-4456-pdf.pdf). The formulas above describe **this app's implementation**, which may differ from another provider's version of a similarly named ratio.
