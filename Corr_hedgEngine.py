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
    try:
        ticker_obj = yf.Ticker(target_ticker)
        info = ticker_obj.info
        
        sector = info.get("sector", None)
        industry = info.get("industry", "N/A")
        company_name = info.get("longName", "Unknown Company")
        business_summary = (info.get("longBusinessSummary") or "").lower()
        
        for niche in NICHE_OVERRIED_MAPS:
            for kw in niche["Keywords"]:
                if kw in business_summary or kw in industry.lower() or kw in company_name.lower():
                    niche_peers = niche["Peers"]
                    
                    full_universe = list(set(niche_peers + MACRO_ANCHORS))
                    if target_ticker in full_universe:
                        full_universe.remove(target_ticker)
                        
                    return full_universe, niche["Group_Name"], industry, company_name

        if not sector:
            return MACRO_ANCHORS, "Broad Market", "N/A", company_name

        sector_data = SECTOR_ETF_MAP.get(sector, None)
        if sector_data:
            sector_etf = sector_data["ETF"]
            sector_peers = sector_data["Peers"]
        else:
            sector_peers = []
            sector_etf = "Broad Market"

        full_universe = list(set(sector_peers + MACRO_ANCHORS))
        
        if target_ticker in full_universe:
            full_universe.remove(target_ticker)
            
        return full_universe, sector_etf, industry, company_name

    except Exception as ex: # pylint: disable=broad-exception-caught
        return MACRO_ANCHORS, "Broad Market", "N/A", target_ticker

# ==========================================
# 3. MATHEMATICAL COMPUTATION ENGINE
# ==========================================
def analyze(symbol: str, downloader=None, discoverer=None) -> dict:
    """Calculate pairwise daily-return correlations for available assets."""
    discoverer = discoverer or discover_market_universe
    downloader = downloader or yf.download
    peers, sector, industry, company = discoverer(symbol)
    universe = [symbol] + sorted(set(peers) - {symbol})
    raw = downloader(universe, period="1y", interval="1d",
                     auto_adjust=True, progress=False, threads=False)
    if raw is None or raw.empty:
        raise ValueError("No historical prices were returned by Yahoo Finance.")

    if isinstance(raw.columns, pd.MultiIndex):
        level = "Close" if "Close" in raw.columns.get_level_values(0) else "Adj Close"
        prices = raw[level]
    elif "Close" in raw:
        prices = raw[["Close"]].rename(columns={"Close": symbol})
    else:
        raise ValueError("Historical prices have no Close column.")

    if isinstance(prices, pd.Series):
        prices = prices.to_frame(name=symbol)
    if symbol not in prices:
        raise ValueError(f"No historical prices were returned for {symbol}.")

    prices = prices.apply(pd.to_numeric, errors="coerce").where(lambda frame: frame > 0)
    returns = np.log(prices / prices.shift(1))
    target = returns[symbol]
    rows = []
    for peer in universe[1:]:
        if peer not in returns:
            continue
        paired = pd.concat([target, returns[peer]], axis=1).dropna()
        if len(paired) < 60:
            continue
        score = paired.iloc[:, 0].corr(paired.iloc[:, 1])
        if pd.notna(score):
            rows.append({"Ticker": peer, "Correlation": float(score),
                         "Paired days": len(paired),
                         "Type": "Market indicator" if peer.startswith("^") else "Security/ETF"})
    rankings = pd.DataFrame(rows, columns=["Ticker", "Correlation", "Paired days", "Type"])
    if rankings.empty:
        raise ValueError("Fewer than 60 overlapping trading days were available for comparisons.")
    rankings = rankings.sort_values("Correlation", ascending=False).reset_index(drop=True)
    return {"company": company, "sector": sector, "industry": industry,
            "correlations": rankings,
            "closest": rankings.iloc[0]["Ticker"],
            "least_correlated": rankings.iloc[-1]["Ticker"]}


def run_correlation_pipeline(target_ticker: str):
    """Compatibility entry point for command-line users."""
    report = analyze(target_ticker)
    print(f'{report["company"]} | {report["sector"]} | {report["industry"]}')
    print(report["correlations"].to_string(index=False))
    return report


if __name__ == "__main__":
    run_correlation_pipeline("IONQ")
