import yfinance as yf
from datetime import datetime
import lxml as lm # pylint: disable=unused-import
# This engine extracts live corporate news feeds and runs a lightweight, offline-safe 
# Natural Language Processing (NLP) scoring model to evaluate qualitative sentiment.

# ==========================================
# 1. CONFIGURATION & INITIAL SETUP
# ==========================================
ticker_symbol = "AAPL"
ticker = yf.Ticker(ticker_symbol)

print("=" * 60)
print("Connection Successful!")
print(f"Company Name: {ticker.info.get('longName', 'N.A')}")
print(f"Ticker      : {ticker.info.get('symbol', 'N/A')}")
print("=" * 60)

# ==========================================
# 2. MASSIVE FINANCIAL-GRADE LEXICON (EXPANDED)
# ==========================================
# pylint: disable=line-too-long, bad-whitespace

BULLISH_WORDS = {
    # Core Growth & Expansion Verbs/Tenses
    "adds", "rewards", "redemption", "integration", "integrate", "adoption"
    "grow", "grows", "growing", "grown", "growth", "growths",
    "expand", "expands", "expanding", "expanded", "expansion", "expansions", "expansionary",
    "outperform", " outperforms", "outperforming", "outperformed", "outperformance",
    "beat", "beats", "beating", "beaten",
    "buy", "buys", "buying", "bought", "buyer", "buyers",
    "upgrade", "upgrades", "upgrading", "upgraded",
    "gain", "gains", "gaining", "gained",
    "surpass", "surpasses", "surpassing", "surpassed",
    "accelerate", "accelerates", "accelerating", "accelerated", "acceleration",
    "innovate", "innovates", "innovating", "innovated", "innovative", "innovation", "innovations",
    "rose", "rises", "rising", "rise", "risen",
    "climb", "climbs", "climbing", "climbed",
    "soar", "soars", "soaring", "soared",
    "surge", "surges", "surging", "surged",
    "jump", "jumps", "jumping", "jumped",
    "rally", "rallies", "rallying", "rallied",
    "advance", "advances", "advancing", "advanced", "advancement", "advancements",
    "exceed", "exceeds", "exceeding", "exceeded",
    "secure", "secures", "securing", "secured", "securitization",
    "boost", "boosts", "boosting", "boosted",
    "scale", "scales", "scaling", "scaled",
    "double", "doubles", "doubling", "doubled",
    "triple", "triples", "tripling", "tripled",
    "compound", "compounds", "compounding", "compounded",
    "capture", "captures", "capturing", "captured",
    "acquire", "acquires", "acquiring", "acquired", "acquisition", "acquisitions",
    "recover", "recovers", "recovering", "recovered", "recovery", "recoveries",
    "rebound", "rebounds", "rebounding", "rebounded",
    "optimize", "optimizes", "optimizing", "optimized", "optimization", "optimizations",
    "strengthen", "strengthens", "strengthening", "strengthened",
    "approve", "approves", "approving", "approved", "approval", "approvals",
    "unlock", "unlocks", "unlocking", "unlocked",
    
    # Financial Strength Nouns & Adjectives
    "profit", "profits", "profitable", "profitably", "profitability",
    "positive", "strong", "stronger", "strongest", "strength", "strengths",
    "partnership", "partnerships", "partner", "partners", "partnered",
    "success", "successful", "successfully",
    "dividend", "dividends", "record", "records", "historic", "historical",
    "breakthrough", "breakthroughs", "bull", "bullish", "bulls",
    "upside", "catalyst", "catalysts", "momentum", "moat", "moats",
    "tailwind", "tailwinds", "high", "highs", "peak", "peaks",
    "leader", "leaders", "leadership", "dominant", "dominance", "dominates",
    "value", "values", "valuable", "premium", "robust", "robustness",
    "resilient", "resilience", "efficiency", "efficient", "efficiently",
    "productive", "productivity", "demand", "healthy", "liquid", "liquidity",
    "solvency", "solvent", "unprecedented", "undervalued"
}

BEARISH_WORDS = {
    # Core Decline & Operational Distress Verbs/Tenses
    "decline", "declines", "declining", "declined",
    "fall", "falls", "falling", "fell", "fallen",
    "drop", "drops", "dropping", "dropped",
    "underperform", "underperforms", "underperforming", "underperformed", "underperformance",
    "miss", "misses", "missing", "missed",
    "sell", "sells", "selling", "sold", "seller", "sellers", "selloff", "selloffs",
    "downgrade", "downgrades", "downgrading", "downgraded",
    "contract", "contracts", "contracting", "contracted", "contraction", "contractions",
    "warn", "warns", "warning", "warnings", "warned",
    "investigate", "investigates", "investigating", "investigated", "investigation", "investigations",
    "layoff", "layoffs", "laying", "laid",
    "crash", "crashes", "crashing", "crashed",
    "plunge", "plunges", "plunging", "plunged",
    "tumble", "tumbles", "tumbling", "tumbled",
    "slump", "slumps", "slumping", "slumped",
    "sink", "sinks", "sinking", "sank", "sunk",
    "slide", "slides", "sliding", "slid",
    "fail", "fails", "failing", "failed", "failure", "failures",
    "struggle", "struggles", "struggling", "struggled",
    "default", "defaults", "defaulting", "defaulted",
    "bleed", "bleeds", "bleeding", "bled",
    "shrink", "shrinks", "shrinking", "shrunk", "shrinkage",
    "lose", "loses", "losing", "lost", "loser", "losers",
    "erode", "erodes", "eroding", "eroded", "erosion",
    "delay", "delays", "delaying", "delayed",
    "suffer", "suffers", "suffering", "suffered",
    "collapse", "collapses", "collapsing", "collapsed",
    "halt", "halts", "halting", "halted",
    "suspect", "suspects", "suing", "suspected",
    "accuse", "accuses", "accusing", "accused", "accusation", "accusations",
    "sue", "sues", "sued", "suit", "suits",  # Fix: Removed duplicate "suspect"
    "litigate", "litigates", "litigating", "litigated", "litigation", "litigations",
    "restrict", "restricts", "restricting", "restricted", "restriction", "restrictions",
    "block", "blocks", "blocking", "blocked",
    "slash", "slashes", "slashing", "slashed",
    "trim", "trims", "trimming", "trimmed",
    "dilute", "dilutes", "diluting", "diluted", "dilution",
    
    # Financial Headwind Nouns & Adjectives
    "loss", "losses", "negative", "weak", "weaker", "weakest", "weakness", "weaknesses",
    "lawsuit", "lawsuits", "debt", "debts", "debtor", "debtors",
    "risk", "risks", "risky", "shortfall", "shortfalls", "bear", "bearish", "bears",
    "downside", "hazard", "hazards", "penalty", "penalties", "fine", "fines",
    "headwind", "headwinds", "low", "lows", "bottom", "bottoms",
    "bubble", "correction", "panic", "fear", "distress", "distressed",
    "deficit", "deficits", "margin-squeeze", "compression", "inflation", "inflationary",
    "pressure", "pressures", "sanction", "sanctions", "dispute", "disputes",
    "controversy", "controversial", "bankrupt", "bankruptcy", "bankruptcies",
    "insolvent", "insolvency", "liquidating", "liquidation", "liquidations",
    "write-down", "write-downs", "write-off", "write-offs", "impairment", "impairments",
    "sluggish", "turbulent", "volatility", "volatile", "unprofitable", "overvalued"
}

# Re-enable standard pylint checks for rest of file
# pylint: enable=line-too-long, bad-whitespace

# ==========================================
# 3. SENTIMENT ENGINE DEFINITION
# ==========================================
def analyze_headline_sentiment(headline: str) -> float:
    """
    Scans a headline string, counts occurrences of bullish vs bearish keywords,
    and returns a standardized sentiment score between -1.0 and 1.0.
    """
    words = headline.lower().split()

    # Clean punctuation and count matching lexicon tokens
    bull_count = sum(1 for word in words if word.strip(",.?!()\"';:") in BULLISH_WORDS)
    bear_count = sum(1 for word in words if word.strip(",.?!()\"';:") in BEARISH_WORDS)

    total_sentiment_count = bull_count + bear_count

    if total_sentiment_count == 0:
        return 0.0  # Neutral score for an informational headline
        
    score = (bull_count - bear_count) / total_sentiment_count  # Polarization formula
    return score

# ==========================================
# 4. LIVE NEWS EXTRACTION & PROCESSING
# ==========================================
print("\n" + "="*40)
print("  LIVE CORPORATE INTELLIGENCE FEED")
print("="*40)

try:
    news_feed = ticker.news

    if news_feed:
        headline_scores = 0 
        cumulative_sentiment = 0.0

        for i, article in enumerate(news_feed[:5], 1):
            content = article.get("content", {})
            title = content.get("title", "Headline Not Available")
            
            provider = content.get("provider", {})
            publisher = provider.get("displayName", "Unknown Source")
            
            canonical_url_dict = content.get("canonicalUrl", {})
            link = canonical_url_dict.get("url", "#")

            raw_time_str = content.get("pubDate", None)
            if raw_time_str:
                try:
                    cleaned_time_str = raw_time_str.replace("Z", "+00:00")
                    dt = datetime.fromisoformat(cleaned_time_str)
                    formatted_time = dt.strftime('%Y-%m-%d %H:%M')
                except Exception:# pylint: disable=broad-exception-caught
                    formatted_time = str(raw_time_str)
            else:
                formatted_time = "N/A"

            sentiment_score = analyze_headline_sentiment(title)
            cumulative_sentiment += sentiment_score
            headline_scores += 1 

            # Map sentiment score to a visual tag
            if sentiment_score > 0:
                tag = f"🟢 BULLISH ({sentiment_score:.2f})"
            elif sentiment_score < 0:
                tag = f"🔴 BEARISH ({sentiment_score:.2f})"
            else:
                tag = "⚪ NEUTRAL (0.00)"
        
            # Print the structured news card
            print(f"\n{i}. [{formatted_time}] - {publisher}")
            print(f"   📰 Headline: {title}")
            print(f"   📊 NLP Sentiment: {tag}")
            print(f"   🔗 Direct Link: {link}")
            print("-" * 50)

        # --- Print Overall Sentiment Dossier ---
        if headline_scores > 0:
            avg_sentiment = cumulative_sentiment / headline_scores
            print("\n" + "="*40)
            print("  CONSOLIDATED SENTIMENT ASSESSMENT")
            print("="*40)
            print(f"Processed Headlines  : {headline_scores}")
            print(f"Consolidated Score   : {avg_sentiment:.2f}")

            if avg_sentiment > 0.15:
                print("Verdict              : 🟢 POSITIVE REGIME (Expansionary momentum & catalyst support)")
            elif avg_sentiment < -0.15:
                print("Verdict              : 🔴 NEGATIVE REGIME (Heightened operational risk / correction fear)")
            else:
                print("Verdict              : ⚪ NEUTRAL REGIME (Consolidating news pipeline)")
                
    else:
        print("⚠️ No public media or press releases found on the server index.")
        
except Exception as e:# pylint: disable=broad-exception-caught
    print(f"⚠️ Qualitative Scraper Error: {e}")

print("="*60)