import yfinance as yf
import pandas as pd


# This engine evaluates the valuation multiples and technical momentum signals of a target equity 
# to ensure we don't buy quality assets at highly over-inflated bubble prices.

# ==========================================
# 1. CONFIGURATION & DICTIONARIES
# ==========================================
CURRENCY_SYMBOLS = {
    "USD": "$",
    "GBP": "£",
    "EUR": "€",
    "JPY": "¥",
    "CAD": "C$",
    "AUD": "A$"
}

ticker_symbol = "AAPL"  
ticker = yf.Ticker(ticker_symbol)

print("="*60)
print("Connection Successful!")
print(f"Company Name: {ticker.info.get('longName', 'N.A')}")
print(f"Ticker      : {ticker.info.get('symbol', 'N/A')}")
print("="*60)


# ==========================================
# 2. DATA EXTRACTION
# ==========================================
# A. Extract Valuation Multiples from yfinance Metadata (.info)
# Layer A: Valuation Multiples (The Price Layer): Measures what the market is demanding today for the company's historical earnings,
# future estimated earnings, sales, and core operational cash flows.

# Multiple 1: Trailing vs. Forward P/E
# - P/E Trailing = Current stock price / actual earnings per share in the past 12 months 
# - P/E Forward = Current stock price / estimated earnings per share in the next 12 months
# In layer A, we are measuring the difference between both. If Forward P/E < Trailing P/E, 
# then analysts expect the company's earnings to increase over the next year.
info = ticker.info

trailing_pe = info.get("trailingPE", None)
forward_pe = info.get("forwardPE", None)

# Multiple 2: Price-to-Sales (P/S)
# - What it is: The market capitalization of the company divided by its total revenue over the last 12 months.
# - Why it matters: For high-growth technology companies that are reinvesting heavily in R&D, net income can look artificially depressed. 
#   Price-to-Sales provides a baseline multiple that cannot be easily manipulated by accounting choices.
p_s = info.get("priceToSalesTrailing12Months", None)

# Multiple 3: EV / EBITDA
# - Compares a company's total business cost (Enterprise Value) to its core operating cash flow.
# Bug Fix 1: Fixed spelling of "enterpriseValue" (was "enterpiseValue" in your draft)
ev = info.get("enterpriseValue", None)
ebitda = info.get("ebitda", None)

# Bug Fix 2: Added defensive division protection to prevent ZeroDivisionError or TypeError crashes
if ev and ebitda and ebitda != 0:
    ev_ebitdam = ev / ebitda
else:
    ev_ebitdam = None


# Layer B: Technical Momentum
# Indicator 1: 6-Month Price Run-up (The Momentum Check)
# There are roughly 126 active trading days in a 6-month market calendar. We want to measure the percentage return over this period to see if the stock is overextended.
price_history = ticker.history(period="1y")

# Bug Fix 3: "Close" must be extracted from the price_history DataFrame, not the 'info' metadata dict!
if not price_history.empty:
    close_price = price_history["Close"]
    closep = close_price.iloc[-1]
    
    # Bug Fix 4: Extract the close price value from close_price series (was pulling the whole row from price_history)
    p126c = close_price.iloc[-126] if len(close_price) >= 126 else None
    
    if p126c is not None:
        R6m = ((closep - p126c) / p126c) * 100
    else:
        R6m = None

    # Indicator 2: Distance from the 200-Day Moving Average
    # The 200-Day Simple Moving Average (SMA_200) is the benchmark trendline monitored by institutional fund managers.
    # The Concept: A stock trading slightly above or at its 200-day average is considered in a healthy, supported uptrend. 
    # A stock trading way above its 200-day average is mathematically "overextended" (historically stretched) and highly vulnerable to a sharp mean-reversion crash.
    price_history["SMA_200"] = close_price.rolling(window=200).mean()
    current_sma200 = price_history["SMA_200"].iloc[-1]

    # Bug Fix 5: Fixed pd.na syntax to pd.notna, reversed logic error, and removed bad variable overwrites
    if pd.notna(current_sma200) and current_sma200 > 0:
        distsma = ((closep - current_sma200) / current_sma200) * 100
    else:
        distsma = None
else:
    closep = info.get("currentPrice", 0.0)
    R6m = None
    distsma = None


# ==========================================
# 3. PRINTING FORMATTED RESULTS
# ==========================================
# Set formatting for multiples (e.g. 15.50x)
pd.set_option('display.float_format', lambda x: f'{x:.2f}x')

print("\n" + "="*40)
print("  VALUATION MULTIPLES LAYER")
print("="*40)

if trailing_pe:
    print(f"Trailing P/E Ratio            : {trailing_pe:.2f}x")
else:
    print("Trailing P/E Ratio            : N/A (Company may be temporarily unprofitable)")

if forward_pe:
    print(f"Forward P/E Ratio             : {forward_pe:.2f}x")
else:
    print("Forward P/E Ratio             : N/A")

if p_s:
    print(f"Price-to-Sales (P/S) Ratio    : {p_s:.2f}x")
else:
    print("Price-to-Sales (P/S) Ratio    : N/A")

if ev_ebitdam:
    print(f"Enterprise Value/EBITDA       : {ev_ebitdam:.2f}x")
else:
    print("Enterprise Value/EBITDA       : N/A")


# Set formatting for percentages (e.g. 12.50%)
print("\n" + "="*40)
print("  TECHNICAL MOMENTUM LAYER")
print("="*40)
print(f"Current Stock Price           : ${closep:.2f}")

if R6m is not None:
    print(f"6-Month Price Run-up (Return) : {R6m:.2f}%")
else:
    print("6-Month Price Run-up (Return) : N/A")

if distsma is not None:
    print(f"Distance from 200-Day SMA     : {distsma:.2f}%")
else:
    print("Distance from 200-Day SMA     : N/A (Insufficient historical days)")
print("="*60)