import yfinance as yf
import pandas as pd
import numpy as np

# ==========================================
# 1. DYNAMIC CONFIGURATION & SECTOR DICTIONARY
# ==========================================
SECTOR_ETF_MAP = {
    "Technology": {
        "ETF": "XLK",
        "Peers": ["MSFT", "AAPL", "NVDA", "AVGO", "ORCL", "CSCO", "ADBE", "CRM", "AMD", "QCOM"]
    },
    "Financial Services": {
        "ETF": "XLF",
        "Peers": ["JPM", "BAC", "WFC", "MS", "GS", "C", "AXP", "BLK", "SCHW", "V"]
    },
    "Healthcare": {
        "ETF": "XLV",
        "Peers": ["LLY", "UNH", "JNJ", "ABBV", "MRK", "AMGN", "PFE", "TMO", "ABT", "ISRG"]
    },
    "Consumer Cyclical": {
        "ETF": "XLY",
        "Peers": ["AMZN", "TSLA", "HD", "MCD", "NKE", "LOW", "SBUX", "TJX", "BKNG", "ORLY"]
    },
    "Consumer Defensive": {
        "ETF": "XLP",
        "Peers": ["PG", "COST", "WMT", "KO", "PEP", "PM", "EL", "MO", "TGT", "CL"]
    },
    "Energy": {
        "ETF": "XLE",
        "Peers": ["XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO", "HAL", "BKR"]
    },
    "Utilities": {
        "ETF": "XLU",
        "Peers": ["NEE", "SO", "DUK", "AEP", "SRE", "D", "PCG", "EXC", "XEL", "ED"]
    },
    "Industrials": {
        "ETF": "XLI",
        "Peers": ["GE", "CAT", "UNP", "HON", "RTX", "LMT", "UPS", "DE", "BA", "ADP"]
    },
    "Basic Materials": {
        "ETF": "XLB",
        "Peers": ["LIN", "APD", "SHW", "FCX", "ECL", "NEM", "NUE", "DOW", "DD", "ALB"]
    },
    "Real Estate": {
        "ETF": "XLRE",
        "Peers": ["PLD", "AMT", "EQIX", "CCI", "WY", "PSA", "O", "SBAC", "WELL", "DLR"]
    },
    "Communication Services": {
        "ETF": "XLC",
        "Peers": ["META", "GOOGL", "NFLX", "DIS", "TMUS", "CMCSA", "VZ", "T", "CHTR", "EA"]
    }
}

NICHE_OVERRIED_MAPS = [
    {
        "Keywords": ["quantum", "qubit"],
        "Group_Name": "Quantum Computing Pure-Plays",
        "Peers": ["IONQ", "RGTI", "QBTS", "GOOGL", "MSFT", "HON", "IBM"] 
    },
    {
        "Keywords": ["space", "satellite", "aerospace"],
        "Group_Name": "Space & Satellite Technology",
        "Peers": ["RKLB", "SPCE", "BKSY", "PL", "LLAP", "LMT", "RTX"]
    },
    {
        "Keywords": ["uranium", "nuclear fusion", "nuclear fission"],
        "Group_Name": "Nuclear & Uranium Energy",
        "Peers": ["CCJ", "UUUU", "UEC", "NXE", "SMR", "LEU"]
    }
]

# FIX: Swapped out dead VIXM for live ^VIX index
MACRO_ANCHORS = [
    "SPY",   
    "GLD",   
    "TLT",   
    "UUP",   
    "^VIX"   
]

# ==========================================
# 2. DYNAMIC DISCOVERY ENGINE
# ==========================================
def discover_market_universe(target_ticker: str) -> tuple:
    """
    Looks up the target ticker's sector, industry, and description dynamically.
    Matches against standard sectors and specialty niche keywords.
    """
    print(f"🔍 Initializing metadata lookup for: {target_ticker}...")
    try:
        ticker_obj = yf.Ticker(target_ticker)
        info = ticker_obj.info
        
        sector = info.get("sector", None)
        industry = info.get("industry", "N/A")
        company_name = info.get("longName", "Unknown Company")
        business_summary = info.get("longBusinessSummary", "").lower()
        
        for niche in NICHE_OVERRIED_MAPS:
            for kw in niche["Keywords"]:
                if kw in business_summary or kw in industry.lower() or kw in company_name.lower():
                    print(f"🎯 SPECIALTY DETECTED: Clustered under '{niche['Group_Name']}'")
                    niche_peers = niche["Peers"]
                    
                    full_universe = list(set(niche_peers + MACRO_ANCHORS))
                    if target_ticker in full_universe:
                        full_universe.remove(target_ticker)
                        
                    return full_universe, niche["Group_Name"], industry, company_name

        if not sector:
            print("⚠️ Sector key missing in metadata. Defaulting to broad market comparison.")
            return MACRO_ANCHORS, "Broad Market", "N/A", company_name

        print(f"✅ Found Sector: {sector} | Industry: {industry}")
        
        sector_data = SECTOR_ETF_MAP.get(sector, None)
        if sector_data:
            sector_etf = sector_data["ETF"]
            sector_peers = sector_data["Peers"]
            print(f"📂 Activating {sector_etf} Sector ETF peer group...")
        else:
            sector_peers = []
            sector_etf = "Broad Market"

        full_universe = list(set(sector_peers + MACRO_ANCHORS))
        
        if target_ticker in full_universe:
            full_universe.remove(target_ticker)
            
        return full_universe, sector_etf, industry, company_name

    except Exception as ex: # pylint: disable=broad-exception-caught
        print(f"⚠️ Metadata harvesting failed: {ex}. Using broad market fallback.")
        return MACRO_ANCHORS, "Broad Market", "N/A", target_ticker

# ==========================================
# 3. MATHEMATICAL COMPUTATION ENGINE
# ==========================================
def run_correlation_pipeline(target_ticker: str):
    """
    Executes the calculation matrix to track and hedge an equity asset.
    """
    # 1. Harvest our dynamic candidate list based on the target stock's sector/niche
    comparison_universe, sector_group, industry, company_name = discover_market_universe(target_ticker)
    
    download_list = [target_ticker] + comparison_universe
    
    print(f"\n2. Downloading 1 year of daily historical data for {len(download_list)} assets...")
    try:
        raw_data = yf.download(download_list, period="1y", interval="1d", progress=False)
        
        if raw_data.empty:
            raise ValueError("No records returned from public trading servers.")
            
        # FIX: Added dynamic safety fallback for column extraction
        if "Adj Close" in raw_data.columns:
            adj_close = raw_data["Adj Close"]
        elif "Close" in raw_data.columns:
            adj_close = raw_data["Close"]
            print("ℹ️ 'Adj Close' missing. Utilizing fallback 'Close' metrics.")
        else:
            raise KeyError("Neither 'Adj Close' nor 'Close' price frames exist in dataset.")
            
    except Exception as e: # pylint: disable=broad-exception-caught
        print(f"❌ Ingestion Failed: {e}")
        return

    # Calculate Daily Log Returns: ln(P_t / P_t-1)
    daily_returns = np.log(adj_close / adj_close.shift(1)).dropna()
    
    # Calculate Pearson Correlation Matrix
    correlation_matrix = daily_returns.corr()
    
    # Isolate correlation series relative to the target stock
    target_correlations = correlation_matrix[target_ticker].drop(target_ticker).dropna()
    
    # Sort rankings (highest positive correlation to highest negative)
    sorted_rankings = target_correlations.sort_values(ascending=False)
    
    tracking_ticker = sorted_rankings.idxmax()
    tracking_corr = sorted_rankings.max()
    
    hedging_ticker = sorted_rankings.idxmin()
    hedging_corr = sorted_rankings.min()
    
    # ==========================================
    # 4. PRINTING FORMATTED DOSSIER
    # ==========================================
    pd.set_option('display.float_format', lambda x: f'{x:+.2f}')
    
    print("\n" + "=" * 60)
    print(f"  QUANTITATIVE RELATIONSHIP DOSSIER: {target_ticker}")
    print("=" * 60)
    print(f"Company Profile   : {company_name}")
    print(f"Sector / Niche    : {sector_group}")
    print(f"Specific Industry : {industry}")
    print(f"Analyzed Assets   : {len(comparison_universe)} (Niche/Sector Peers & Macro Anchors)")
    print("=" * 60)
    
    print("\n📈 DYNAMIC CORRELATION LEADERBOARD:")
    print("-" * 40)
    for asset, score in sorted_rankings.items():
        tag = "⚪"
        if score > 0.60:
            tag = "🟢 (High Tracking)"
        elif score < -0.20:
            tag = "🔴 (Active Hedge)"
        print(f"   {asset:<6} : {score:+.2f} {tag}")
    print("-" * 40)
    
    print("\n🛡️ PORTFOLIO ALLOCATION DECISION INSIGHTS:")
    print("-" * 50)
    print(f"🎯 TARGET SECURITY      : {target_ticker}")
    print(f"🟢 TRACKING BENCHMARK   : {tracking_ticker} ({tracking_corr:+.2f})")
    print(f"   ↳ Portfolio Utility  : Excellent peer-tracking alternative. Moves closely with {target_ticker}.")
    print("                          (Allows industry exposure while diluting single-stock gap risk.)")
    print("-" * 50)
    print(f"🛡️ STRUCTURAL HEDGE     : {hedging_ticker} ({hedging_corr:+.2f})")
    
    if hedging_corr < -0.40:
        print("    ↳ Portfolio Utility  : ⚠️ POWERFUL CONTRA-HEDGE POSITION DETECTED.")
        print(f"                           Allocating capital to {hedging_ticker} actively suppresses your")
        print("                           portfolio's overall beta and insulates it during sector corrections.")
    elif hedging_corr < 0.00:
        print("    ↳ Portfolio Utility  : ✅ CAPITAL PRESERVATION SAFE HAVEN.")
        print("                           Uncorrelated or weak inverse buffer. Cushions downside drawdown.")
    else:
        print("    ↳ Portfolio Utility  : ❌ NO NATURAL CONTRA-HEDGES DETECTED.")
        print(f"                           Even the most negative asset is positive ({hedging_corr:+.2f}).")
        print("                           Systemic beta risk is dominant. Consider physical Cash reserves.")
    print("=" * 60)

# ==========================================
# 5. EXECUTION ENTRY POINT
# ==========================================
if __name__ == "__main__":
    target = "IONQ" 
    run_correlation_pipeline(target)

# this is a fix for the exception codde:

# try:
#    raw_data = yf.download(download_list, period="1y")
#     #... code ...
# except KeyError as k_err:
#    print(f"❌ Data column structure shifted: {k_err}")
#    return
# except Exception:  # No 'as e' needed if you just want a silent fallback blanket
#    print("❌ An unexpected network or system error occurred.")
#    return