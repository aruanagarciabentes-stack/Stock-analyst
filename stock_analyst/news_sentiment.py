import yfinance as yf
from datetime import datetime, timezone
import re
import pandas as pd
# This engine extracts live corporate news feeds and runs a lightweight, offline-safe 
# Natural Language Processing (NLP) scoring model to evaluate qualitative sentiment.

# ==========================================
# 1. CONFIGURATION & INITIAL SETUP
# ==========================================

# ==========================================
# 2. MASSIVE FINANCIAL-GRADE LEXICON (EXPANDED)
# ==========================================
# pylint: disable=line-too-long, bad-whitespace

BULLISH_WORDS = {
    # Core Growth & Expansion Verbs/Tenses
    "adds", "rewards", "redemption", "integration", "integrate", "adoption",
    "grow", "grows", "growing", "grown", "growth", "growths",
    "expand", "expands", "expanding", "expanded", "expansion", "expansions", "expansionary",
    "outperform", "outperforms", "outperforming", "outperformed", "outperformance",
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
    """Lexicon score from -1 to 1; zero means no directional words."""
    words = re.findall(r"[a-z]+(?:-[a-z]+)*", headline.lower())
    bull_count = sum(word in BULLISH_WORDS for word in words)
    bear_count = sum(word in BEARISH_WORDS for word in words)
    count = bull_count + bear_count
    return (bull_count - bear_count) / count if count else 0.0


def analyze(symbol: str, ticker=None) -> dict:
    """Return recent headlines; word count is descriptive, not a price forecast."""
    ticker = ticker or yf.Ticker(symbol)
    try:
        news_feed = ticker.news or []
    except Exception:
        news_feed = []
    if not news_feed:
        try:
            news_feed = yf.Search(symbol, news_count=5).news or []
        except Exception:
            news_feed = []
    rows = []
    for article in news_feed[:5]:
        content = article.get("content") or article
        title = content.get("title") or "Untitled"
        provider = content.get("provider") or {}
        publisher = provider.get("displayName") if isinstance(provider, dict) else None
        url_data = content.get("canonicalUrl") or content.get("clickThroughUrl") or content.get("link") or {}
        url = url_data.get("url", "") if isinstance(url_data, dict) else str(url_data)
        raw_time = content.get("pubDate") or content.get("providerPublishTime")
        try:
            if isinstance(raw_time, (int, float)):
                timestamp = datetime.fromtimestamp(raw_time, timezone.utc)
            else:
                timestamp = datetime.fromisoformat(raw_time.replace("Z", "+00:00"))
            published = timestamp.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        except (AttributeError, TypeError, ValueError, OSError):
            published = "N/A"
        rows.append({
            "Published": published,
            "Source": publisher or content.get("publisher") or "Unknown",
            "Headline": title,
            "Score": analyze_headline_sentiment(title),
            "Link": url,
        })
    frame = pd.DataFrame(rows, columns=["Published", "Source", "Headline", "Score", "Link"])
    return {"headlines": frame, "average_score": float(frame["Score"].mean()) if not frame.empty else None}
