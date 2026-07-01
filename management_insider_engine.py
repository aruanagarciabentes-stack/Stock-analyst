import yfinance as yf
import pandas as pd
import lxml as lm # pylint: disable=unused-import
# This engine extracts insider transaction files (Form 4s), institutional holdings (13Fs), 
# and chronological earnings surprise metrics to evaluate executive alignment and smart money flows.

# ==========================================
# 1. CONFIGURATION & DICTIONARIES
# ==========================================
ticker_symbol = "AAPL"  # Apple is highly active with Form 4 filing pipelines
ticker = yf.Ticker(ticker_symbol)

print("=" * 60)
print("Connection Successful!")
print(f"Company Name: {ticker.info.get('longName', 'N.A')}")
print(f"Ticker      : {ticker.info.get('symbol', 'N/A')}")
print("=" * 60)

# ==========================================
# 2. EXECUTIVE INSIDER TRANSACTIONS (Form 4)
# ==========================================
print("\n" + "="*40)
print("  INSIDER TRANSACTION TRACKER")
print("="*40)

try:
    insiders = ticker.get_insider_transactions()

    if insiders is not None and not insiders.empty:

        print(insiders.head(5))

        if "Aquisitions or Disposition" in insiders.columns:
            buys = insiders["Aquisitions or Dispositions"] == "A"
            sells = insiders["Aquisitions or Dipsositiona"] == "D"
            
            print(f"\nRecent activity in database{len(buys)} purchaces | {len(sells)} sales ")
    else:
        
        print("⚠️ No Form 4 executive insider transactions returned on public servers for this equity.")
except Exception as i:# pylint: disable=broad-exception-caught
    print( f"⚠️ Insider Extraction Error: {i}")

# ==========================================
# 3. INSTITUTIONAL OWNERSHIP (13F Holdings)
# ==========================================

print("\n" + "="*40)
print("  TOP INSTITUTIONAL HOLDERS")
print("="*40)

try:
    # Pull institutional holdings table
    institutions = ticker.get_institutional_holders()
    
    # Defensive Check: Verify DataFrame is valid
    if institutions is not None and not institutions.empty:
        # Standardize columns if needed and show the top 5 largest holders
        # Columns typically include: 'Holder', 'Shares', 'Value', 'Date Reported', 'out'
        print(institutions.head(5))
    else:
        print("⚠️ Institutional holdings tables returned empty.")
except Exception as i:# pylint: disable=broad-exception-caught
    print(f"⚠️ Institutional Extraction Error: {i}")

# ==========================================
# 4. MANAGEMENT TRACK RECORD (Earnings Surprise)
# ==========================================
print("\n" + "="*40)
print("  EARNINGS ESTIMATE SURPRISE HISTORY")
print("="*40)

try:
    # Pull surprise history
    earnings_dates = ticker.get_earnings_dates(limit=8)
    
    if earnings_dates is not None and not earnings_dates.empty:
        # We only want to look at reported earnings (not future expectations)
        reported_quarters = earnings_dates.dropna(subset=["Reported EPS"])
        
        if not reported_quarters.empty:
            # 1. Format general numbers globally as clean 2-decimal floats
            pd.set_option('display.float_format', lambda x: f'{x:.2f}')
            
            # 2. Extract the last 4 completed quarters into a temporary display DataFrame
            display_df = reported_quarters.head(4)[['EPS Estimate', 'Reported EPS', 'Surprise(%)']].copy()
            
            # 3. Format ONLY the 'Surprise(%)' column to have the '%' symbol attached
            display_df['Surprise(%)'] = display_df['Surprise(%)'].map(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
            
            # Show the final beautiful custom-formatted table!
            print(display_df)
        else:
            print("No completed earnings report surprises on file.")
    else:
        print("⚠️ Earnings metrics not exposed on public files for this stock.")
except Exception as e:# pylint: disable=broad-exception-caught
    print(f"⚠️ Earnings Extraction Error: {e}")

print("="*60)