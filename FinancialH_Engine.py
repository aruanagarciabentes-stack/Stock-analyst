import yfinance as yf
import pandas as pd 

#This engine uses balance sheet and cash flow metrics to evaluate a company's short-term liquidity, 
# long-term solvency, and capital allocation efficiency.

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

ticker_symbol = "APLE"
ticker = yf.Ticker(ticker_symbol)

print("="*60)
print("connection successful!")
print(f"Company Name: {ticker.info.get('longName', 'N.A')}")
print(f"Ticker : {ticker.info.get('symbol', 'N/A')}")
print("="*60)

# Pull financial statements
balance_sheet = ticker.quarterly_balance_sheet
cashflow_stm = ticker.quarterly_cashflow
income_stm = ticker.quarterly_income_stmt

# ==========================================
# 2. RAW DATA EXTRACTION & COGNITIVE FALLBACKS
# ==========================================

# --- ADVANCED CASH FALLBACK LOOP ---
# Looks for pre-aggregated parent rows first. If missing, sums up granular cash sub-components
cash_labels = ["Cash Cash Equivalents And Short Term Investments" , "Cash And Cash Equivalents" ]
total_cash = None

for labels in cash_labels:
    if labels in balance_sheet.index:
        series = balance_sheet.loc[labels]
        if not series.dropna().empty:
            total_cash = series
            break 

if total_cash is None:
    cash_fin = balance_sheet.loc["Cash Financial"] if "Cash Financial" in balance_sheet.index else 0
    cash_eq = balance_sheet.loc["Cash Equivalents"] if "Cash Equivalents" in balance_sheet.index else 0
    total_cash = cash_fin.fillna(0) + cash_eq.fillna(0)

# --- ADVANCED EBIT BOTTOM-UP FALLBACK LOOP---
# Calculates clean bottom-up EBIT (Net Income + Taxes + Interest Expense).
# Falls back to standard Operating Income if the database has empty values.
ebit_components = ["Net Income","Tax Provision","Interest Expense"]
can_use_bottom_up = True
ebit_series = None

for components in ebit_components:
    if components not in income_stm.index:
        can_use_bottom_up = False
        break
if can_use_bottom_up:
    net_inc = income_stm.loc["Net Income"]
    tax_exp = income_stm.loc["Tax Provision"]
    int_exp =  income_stm.loc["Interest Expense"]
    ebit_series = net_inc.fillna(0)+tax_exp.fillna(0)+int_exp.fillna(0)

if ebit_series is None or ebit_series.fillna(0).empty:
    can_use_bottom_up = False

if not can_use_bottom_up:
    print("Missing bottom up metrics, Operating income used in its stead")
    ebit_series = income_stm.loc["Operating Income"]
else:
    print("True EBIT calculated")


# --- CORE EXTRACTIONS ---
total_debt = balance_sheet.loc["Total Debt"]
cashflow = cashflow_stm.loc["Free Cash Flow"]
current_assets = balance_sheet.loc["Current Assets"]
current_liabilities = balance_sheet.loc["Current Liabilities"]
stockHEQ = balance_sheet.loc["Stockholders Equity"]


total_cashc =  total_cash.dropna().iloc[::-1]
total_debtC = total_debt.dropna().iloc[::-1]
currentA_clean = current_assets.dropna().iloc[::-1]
currentL_clean = current_liabilities.dropna().iloc[::-1]
stockHEQ_clean = stockHEQ.dropna().iloc[::-1]
ebit_cleaned = ebit_series.dropna().iloc[::-1]

# ==========================================
# 4. MATH CALCULATIONS
# ==========================================

#=== Layer A Short term liquidity: Current Ratio ===
current_ratio = currentA_clean/currentL_clean

#=== Layer B Long-Term Solvency: Debt-To-Equity ===
DtE = total_debtC/stockHEQ_clean

#=== Layer C: Capital Allocation Efficiency ===
corp_tax = 0.21 # lets get everything done, then change this assumption since its terrible for certain companies

#NOPAT = ebit * (1 - corporate tax)
NOPAT = ebit_cleaned * (1 - corp_tax)

#Invested Capital = Debt + equity - Cash 
invested_cap = total_debtC + stockHEQ_clean - total_cashc

# ROIC % = (NOPAT/Invested Capital)*100
ROIC = (NOPAT/invested_cap)*100

# ==========================================
# 5. PRINTING FORMATTED RESULTS
# ==========================================

# --- Part A: Solvency & Liquidity (Formatted as Multiples) ---
pd.set_option('display.float_format', lambda x: f'{x:.2f}x')

print("\n" + "="*40)
print("  SOLVENCY & LIQUIDITY MULTIPLES")
print("="*40)
print("\n--- CURRENT RATIO (Target: > 1.0x to 1.5x) ---")
print(current_ratio)

print("\n--- DEBT-TO-EQUITY (Target: < 1.0x to 1.5x) ---")
print(DtE)

# --- Part B: Capital Allocation (Formatted as Percentages) ---
pd.set_option('display.float_format', lambda x: f'{x:.2f}%')

print("\n" + "="*40)
print("  CAPITAL ALLOCATION EFFICIENCY")
print("="*40)
print("\n--- RETURN ON INVESTED CAPITAL (Target: > 10%) ---")
print(ROIC)
print("="*60)