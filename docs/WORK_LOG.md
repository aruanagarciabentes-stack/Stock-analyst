# Stock Analyst refinement log

## Goal
Make the six-part Streamlit dashboard run for the ticker the user enters, handle missing public data, and leave a reproducible demo for the October 2026 event.

## Baseline, 17 October 2026
- Local branch `main` was clean and tracked `origin/main`.
- Virtual environment: Python 3.14.4, Streamlit 1.58.0, yfinance 1.5.1, pandas 3.0.3.
- Importing `Dashboard_App.py` immediately fetched Apple data in five engines. The financial-health engine was hard-coded to `APLE` (Apple Hospitality REIT), while most others used `AAPL`; the dashboard default was `IONQ`.
- `importlib.reload()` in the dashboard resets an injected ticker to the module's hard-coded ticker, so selecting another ticker cannot reliably change those five reports.
- A live baseline import reached Yahoo Finance outside the network sandbox, then failed on Windows console encoding in the news engine. The output also showed global pandas float formatting leaking between reports (money displayed as percentages).
- Yahoo Finance access is required for live reports; the app should open and explain failures even if that feed is unavailable.

## Planned repairs and verification
- Move data fetching into ticker-parameterized functions and remove import-time network calls.
- Make each section show its own missing-data or provider error without blocking the other sections.
- Audit calculations and labels, especially ROE, ROIC, correlation versus hedging, and price currency.
- Add focused automated checks using fixed sample data, then smoke-test the Streamlit app and live tickers.

## Repairs completed
- Replaced import-time execution in five engines with `analyze(symbol)` functions. The dashboard now keeps reports by selected ticker and does not fetch data until a Run button is pressed.
- Removed module reloads, console capture, and global pandas display formatting. Financial ratios now use aligned dates and show unavailable inputs as N/A instead of substituting zero.
- Updated the business-quality and financial-health formulas, made valuation price currency explicit, and reframed correlations as observed relationships rather than guaranteed hedges.
- Fixed insider classification spelling/counting, the missing comma and tokenization in the sentiment lexicon, and the news fallback to Yahoo's search endpoint. Live Yahoo ticker news returned no articles, while search returned five for both tested tickers.
- Added `README.md`, pinned the tested direct dependencies, and added offline, live and UI smoke checks.

## Verification, 17 October 2026
- `python -m unittest discover -s tests -p test_*.py -v`: seven deterministic checks passed (financial formulas, cash fallback, zero denominator, momentum, ownership, news fallback, pairwise correlation).
- `python tests/live_smoke.py AAPL IONQ`: all twelve engine/ticker combinations returned without an exception after the correlation output fix. Financial data may contain N/A values when the provider omits inputs.
- Yahoo search news endpoint returned five headlines for each of AAPL and IONQ after the fallback change.
- `python tests/ui_smoke.py`: all six AAPL report views rendered without a Streamlit exception or error. Switching to IONQ cleared the AAPL report and loaded IONQ revenue, addressing the original wrong-ticker failure.
- Real Streamlit server started on `127.0.0.1:8501`; its health endpoint returned HTTP 200. The browser tab was opened in the right panel.

## Remaining limits
- Yahoo Finance is an unofficial public-data dependency and may change fields, rate-limit, or return empty sections. A passing smoke test does not guarantee future availability.
- Sector/niche comparison lists in the correlation engine are curated static examples; some names may later delist or stop returning history. The engine skips peers with fewer than 60 paired days.
- ROIC is an estimate based on provider line items and the effective tax rate; unusual capital structures can make it hard to compare across firms.
