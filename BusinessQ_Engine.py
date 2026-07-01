import yfinance as yf
import pandas as pd

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

# ==========================================
# 2. DATA EXTRACTION
# ==========================================
# Target stock ticker
ticker_symbol = "AAPL"
ticker = yf.Ticker(ticker_symbol)

print("="*60)
print("connection successful!")
print(f"Company Name: {ticker.info.get('longName', 'N.A')}")
print(f"Ticker : {ticker.info.get('symbol', 'N/A')}")
print("="*60)

#Pull fincancial statements
income_stm = ticker.quarterly_income_stmt
balance_sheet = ticker.quarterly_balance_sheet

#Extract the rows from income statement
Trevenue =income_stm.loc["Total Revenue"]
Gross_profit = income_stm.loc["Gross Profit"]
Operating_income = income_stm.loc["Operating Income"]
Net_income = income_stm.loc["Net Income"]

#Extract the rows from balance sheet
equity = balance_sheet.loc["Stockholders Equity"]

# ==========================================
# 3. DATA CLEANING & REVERSING
# ==========================================
# Drop missing values and reverse chronologically (oldest -> newest)
Trevenue_clean = Trevenue.dropna().iloc[::-1]
Gross_profit_clean = Gross_profit.dropna().iloc[::-1]
Operating_income_clean = Operating_income.dropna().iloc[::-1]
net_income_clean = Net_income.dropna().iloc[::-1]
equity_clean = equity.dropna().iloc[::-1]

#set up a dynamic currency symbol based on the stock's currency using yfinance metadata.
currency_code = ticker.info.get('currency', 'UNKNOWN')
currency_symbol = CURRENCY_SYMBOLS.get(currency_code, f"{currency_code} ")

# ==========================================
# 4. MATH CALCULATIONS
# ==========================================
# A. Profitability Margins (%)
gross_profit_margin = (Gross_profit_clean / Trevenue_clean) * 100
gross_operating_margin = (Operating_income_clean / Trevenue_clean) * 100
net_income_margin = (net_income_clean / Trevenue_clean) * 100

#B. Year-over-Year Revenue Growth (%) 
yoy_revgrowth = ((Trevenue_clean.shift(0) - Trevenue_clean.shift(4))/Trevenue_clean.shift(4)) * 100

#C. Return on Equity (ROE) (%)
# Note: Net Income is quarterly, so we multiply by 4 to annualize it
Net_income_annualized = net_income_clean * 4 
ROE = (Net_income_annualized / equity_clean)*100 

# ==========================================
# 5. PRINTING FORMATTED RESULTS
# ==========================================

#Part A: raw financials (formatted in Ticker )
pd.set_option('display.float_format', lambda x: f'{currency_symbol}{x:,.2f}')


print("---CLEAN REVENUE---")
print(Trevenue_clean)

print("\n---CLEAN GROSS PROFIT---")
print(Gross_profit_clean)

print("\n---CLEAN OPERATING INCOME---")
print(Operating_income_clean)
print("Reporting currency:", ticker.info.get("currency", "N/A"))
print("-" * 40)

#Part B: Performance metrics (formatted in %)
pd.set_option('display.float_format', lambda x: f'{x:.2f}%')
print("\n---GROSS PROFIT MARGIN---")
print(gross_profit_margin) 

print("\n---GROSS OPERATING MARGIN---")
print(gross_operating_margin) 

print("\n---YEAR-OVER-YEAR REVENUE GROWTH---")
print(yoy_revgrowth)

print("\n---NET INCOME MARGIN---")
print(net_income_margin)

print("\n---RETURN ON EQUITY (ROE)---")
print(ROE)
print("=" * 60)